# Debugging Networks

**[Intermediate]** — the practical payoff. Everything above becomes useful when something is broken at 2am and you need to find out *where*. This note is a method plus a toolkit, in the order you should actually use them.

## The method: bisect the layers

The single most valuable habit is **not guessing**. Work up the stack, and at each step ask a question with a binary answer. Each answer eliminates half the remaining possibilities.

```
1. Is the name resolving?          dig example.com
2. Is the host reachable?          ping / traceroute / mtr
3. Is the port open?               nc -vz host port   /  telnet
4. Does TLS complete?              openssl s_client -connect host:443
5. Does the app respond correctly?  curl -v
6. What's actually on the wire?    tcpdump / wireshark
```

Do not skip to step 6. Most incidents resolve at step 1 or 3, and a packet capture without a hypothesis is a waste of an hour.

## Step 1 — name resolution

```sh
dig example.com                    # the full answer, with TTL
dig +short example.com             # just the address
dig +trace example.com             # walk root → TLD → authoritative yourself
dig @8.8.8.8 example.com           # bypass your local resolver
dig -x 93.184.216.34               # reverse lookup
```

`+trace` is the one worth learning — it shows *which* level of the hierarchy is broken, rather than just "no answer." `@8.8.8.8` immediately distinguishes "the record is wrong" from "my resolver has a stale/broken cache."

Read the **TTL** in the answer: a TTL counting down tells you it's a cached answer and how long ago it was fetched. If you just changed a record and are still seeing the old one, the remaining TTL is exactly how long you'll keep seeing it. → [[foundations/networking/10-dns-in-depth|DNS in depth]]

`getent hosts example.com` is worth knowing too — it uses the OS resolver path (`/etc/hosts`, nsswitch, resolver config) which `dig` **bypasses**. If `dig` works and your app doesn't, the difference is here.

## Step 2 — reachability and path

```sh
ping -c 5 example.com              # up? and what's the RTT/loss?
traceroute example.com             # the path, hop by hop
mtr example.com                    # traceroute + ping, continuous — use this one
```

**Read these correctly**, because both are routinely misread:

- **ICMP being blocked is common.** Failed `ping` ≠ host down. Try the actual port instead.
- **`* * *` in traceroute means that router doesn't answer ICMP**, not that the packet stopped there. If later hops respond, the path is fine.
- **A latency spike at one hop that disappears at later hops is not a problem.** It means that router deprioritised generating an ICMP reply — a control-plane task. Only latency that *persists to the destination* is real.
- **Paths are asymmetric.** The return route may differ entirely, and you can't see it from here.

`mtr` is strictly better than `traceroute` for real diagnosis: it runs continuously, so you see **loss percentage per hop over time**, which separates a genuinely lossy link (loss persists at all subsequent hops) from ICMP rate-limiting (loss at one hop only, later hops clean). → [[foundations/networking/04-routing|routing]]

## Step 3 — is the port actually open?

```sh
nc -vz example.com 443             # simplest port check
nc -vz -w 3 host 5432              # with a timeout
curl -v telnet://host:port         # when nc isn't installed
nmap -Pn -p 443 host               # when you need more detail
```

**The single highest-value diagnostic in this note** — the difference between two failure modes:

| Symptom | Meaning | Usual cause |
|---|---|---|
| **"Connection refused" (instant)** | you reached the host; **nothing is listening** | service down, wrong port, bound to `127.0.0.1` instead of `0.0.0.0` |
| **Hang → timeout** | something is **silently dropping** | firewall/security group DROP, wrong route, MTU black hole |

That split immediately tells you whether to look at the application or at the network. → [[foundations/networking/14-nat-firewalls-and-middleboxes|firewalls: reject vs drop]]

The "bound to localhost" case is worth calling out — it's the most common self-inflicted version, and `ss -lntp` shows it instantly: `127.0.0.1:8080` will never accept remote connections, `0.0.0.0:8080` will.

## Step 4 — local socket state

```sh
ss -lntp                           # what's listening, and which process
ss -tan                            # all TCP sockets with states
ss -tan state time-wait | wc -l    # TIME_WAIT count
ss -tin                            # per-socket internals: RTT, cwnd, retransmits
lsof -i :8080                      # which process holds this port
lsof -p PID | wc -l                # fd count — for leak hunting
```

`ss` has replaced `netstat` (much faster on busy hosts). What to look for, mapping straight onto [[foundations/networking/06-tcp-connection-lifecycle|the TCP state machine]]:

- **Many `CLOSE_WAIT`** → *your* app isn't calling `close()`. A file-descriptor leak. Ends in "too many open files."
- **Many `FIN_WAIT_2`** → the *peer* isn't closing.
- **Many `TIME_WAIT`** → connection churn; you need connection pooling, not a sysctl.
- **`Recv-Q` non-zero on a LISTEN socket** → your app isn't calling `accept()` fast enough; the kernel is dropping connections silently.
- **`ss -tin`** shows `rtt`, `cwnd`, and `retrans` per connection — the fastest way to confirm "the network is lossy" versus "the server is slow." Rising `retrans` is direct evidence of loss. → [[foundations/networking/08-congestion-control|congestion control]]

## Step 5 — TLS and the application

```sh
openssl s_client -connect example.com:443 -servername example.com   # full handshake
echo | openssl s_client -connect host:443 2>/dev/null | openssl x509 -noout -dates
curl -v https://example.com                        # headers + TLS summary
curl -w '@curl-format.txt' -o /dev/null -s URL     # timing breakdown
```

`-servername` matters — without SNI you may get the wrong certificate entirely and chase a phantom problem.

The **curl timing breakdown** is the highest-value single tool for "why is this slow," because it attributes the time to a layer:

```
# curl-format.txt
dns:      %{time_namelookup}s
tcp:      %{time_connect}s
tls:      %{time_appconnect}s
ttfb:     %{time_starttransfer}s
total:    %{time_total}s
```

Read the *deltas*: big `dns` → resolver problem. Big `tcp - dns` → network distance or SYN retries. Big `tls - tcp` → handshake/cert-chain cost. Big `ttfb - tls` → **the server is slow, not the network.** That last one ends a lot of pointless network investigations.

## Step 6 — the wire

```sh
sudo tcpdump -i any -n host 10.0.0.5 and port 443       # filter tightly, always
sudo tcpdump -i any -n -w capture.pcap 'tcp port 80'    # write for Wireshark
sudo tcpdump -i any -n 'tcp[tcpflags] & (tcp-syn|tcp-rst) != 0'   # handshakes/resets only
```

Rules that make captures useful rather than overwhelming: **filter at capture time** (an unfiltered capture on a busy host is unreadable and can itself cause problems), use `-n` to skip DNS resolution of every address, and pull the file into Wireshark for anything non-trivial — *Statistics → Conversations* and *Expert Information* find in seconds what scrolling won't.

Signatures worth recognising:
- **SYN, SYN, SYN with no reply** → dropped by a firewall, or wrong route.
- **SYN → RST** → nothing listening.
- **Many retransmissions** → loss.
- **`TCP ZeroWindow`** → the *receiver* is the bottleneck (its app isn't reading fast enough) — a very different problem from network congestion.
- **Handshake fine, then silence on a large response** → classic [[foundations/networking/02-the-link-layer|MTU black hole]]. Confirm with `ping -M do -s 1472 host`, decreasing the size until it passes.

For [[foundations/networking/13-quic-and-modern-transport|QUIC/HTTP3]], packet capture shows you almost nothing — it's encrypted by design. Use **qlog** or `SSLKEYLOGFILE` with Wireshark instead.

## Common failure signatures, indexed by symptom

| Symptom | Likely cause | First check |
|---|---|---|
| Works locally, fails remotely | bound to `127.0.0.1`; firewall | `ss -lntp` |
| Instant "connection refused" | nothing listening | `ss -lntp`, is the service up? |
| Hangs then times out | silent DROP | firewall/security group rules |
| Small requests OK, large ones hang | **MTU / PMTU black hole** | `ping -M do -s 1472` |
| Fine locally, slow across continents | window scaling, or just RTT | `ss -tin`, count round trips |
| Fails after N minutes idle | NAT/LB idle timeout | add keepalives/heartbeats |
| Intermittent 5s delays (k8s) | `ndots:5` DNS resolution | `/etc/resolv.conf`, use FQDN |
| "Too many open files" | fd leak — `CLOSE_WAIT` | `ss -tan state close-wait` |
| "Cannot assign requested address" | ephemeral port exhaustion | `ss -tan state time-wait \| wc -l` |
| Certificate errors only on some clients | missing intermediate in chain | `openssl s_client` and read the chain |
| Fast, then slow after a big upload starts | **bufferbloat** | `mtr` during the transfer |

## Key insight

Network debugging is **binary search over the stack**, and the reason it feels hard is that people start at the layer they're most comfortable with rather than the layer that's cheapest to eliminate. Every tool here answers one narrow question; the skill is choosing the question whose answer removes the most possibilities. And the most valuable single distinction in the whole practice costs you three seconds: **refused (fast) means you got there and were told no; hung (slow) means something in between never told you anything.**

## Related
- [[foundations/networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]] — the states `ss` reports
- [[foundations/networking/15-network-performance|Network Performance]] — interpreting the timings
- [[devops/10-observability/README|Observability]] — turning this into monitoring rather than firefighting
- [[devops/01-linux/README|Linux]] — the shell fluency this assumes
