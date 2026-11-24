---
id: 1f8c3d4c-2e12-4758-a560-66482e29f295
---

# Debugging Networks

Debugging a network means finding out where a connection is broken when something cannot reach something else. Think of the times a site will not load but your Wi-Fi seems fine. This lesson gives you a step-by-step method and the tools to use, so you check instead of guessing.

## The method: bisect the layers
<!-- bite: 5f6c27c4-2e9c-4177-8d08-d1ca84871855 -->

The single most valuable habit is **not guessing**. Work up the stack, and at each step ask a question with a binary answer. Each answer eliminates half the remaining possibilities.

```text
1. Is the name resolving?          dig example.com
2. Is the host reachable?          ping / traceroute / mtr
3. Is the port open?               nc -vz host port   /  telnet
4. Does TLS complete?              openssl s_client -connect host:443
5. Does the app respond correctly?  curl -v
6. What's actually on the wire?    tcpdump / wireshark
```

Do not skip to step 6. Most incidents resolve at step 1 or 3, and a packet capture without a hypothesis is a waste of an hour.

## Step 1 — name resolution
<!-- bite: 2989cfad-9153-4ed0-a836-5a60d1749975 -->

```sh
dig example.com                    # the full answer, with TTL
dig +short example.com             # just the address
dig +trace example.com             # walk root → TLD → authoritative yourself
dig @8.8.8.8 example.com           # bypass your local resolver
dig -x 93.184.216.34               # reverse lookup
```

`+trace` is the one worth learning — it shows *which* level of the hierarchy is broken, rather than just "no answer." `@8.8.8.8` immediately distinguishes "the record is wrong" from "my resolver has a stale/broken cache."

Read the **TTL** in the answer: a TTL counting down tells you it's a cached answer and how long ago it was fetched. If you just changed a record and are still seeing the old one, the remaining TTL is exactly how long you'll keep seeing it. → [[networking/10-dns-in-depth/index|DNS in depth]]

`getent hosts example.com` is worth knowing too — it uses the OS resolver path (`/etc/hosts`, nsswitch, resolver config) which `dig` **bypasses**. If `dig` works and your app doesn't, the difference is here.

## Step 2 — reachability and path
<!-- bite: d203a000-e081-4a19-b27c-cb35a58870c4 -->

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

`mtr` is strictly better than `traceroute` for real diagnosis: it runs continuously, so you see **loss percentage per hop over time**, which separates a genuinely lossy link (loss persists at all subsequent hops) from ICMP rate-limiting (loss at one hop only, later hops clean). → [[networking/04-routing|routing]]

## Step 3 — is the port actually open?
<!-- bite: ac400f06-457c-4fc3-8e70-2e07bbc5596e -->

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

That split immediately tells you whether to look at the application or at the network. → [[networking/14-nat-firewalls-and-middleboxes|firewalls: reject vs drop]]

The "bound to localhost" case is worth calling out — it's the most common self-inflicted version, and `ss -lntp` shows it instantly: `127.0.0.1:8080` will never accept remote connections, `0.0.0.0:8080` will.

## Step 4 — local socket state
<!-- bite: 147571a5-393c-4124-90b1-cdfe254ed0f5 -->

```sh
ss -lntp                           # what's listening, and which process
ss -tan                            # all TCP sockets with states
ss -tan state time-wait | wc -l    # TIME_WAIT count
ss -tin                            # per-socket internals: RTT, cwnd, retransmits
lsof -i :8080                      # which process holds this port
lsof -p PID | wc -l                # fd count — for leak hunting
```

`ss` has replaced `netstat` (much faster on busy hosts). What to look for, mapping straight onto [[networking/06-tcp-connection-lifecycle|the TCP state machine]]:

- **Many `CLOSE_WAIT`** → *your* app isn't calling `close()`. A file-descriptor leak. Ends in "too many open files."
- **Many `FIN_WAIT_2`** → the *peer* isn't closing.
- **Many `TIME_WAIT`** → connection churn; you need connection pooling, not a sysctl.
- **`Recv-Q` non-zero on a LISTEN socket** → your app isn't calling `accept()` fast enough; the kernel is dropping connections silently.
- **`ss -tin`** shows `rtt`, `cwnd`, and `retrans` per connection — the fastest way to confirm "the network is lossy" versus "the server is slow." Rising `retrans` is direct evidence of loss. → [[networking/08-congestion-control|congestion control]]

## Step 5 — TLS and the application
<!-- bite: d04c2de2-53fa-484f-b919-28a05630e90c -->

```sh
openssl s_client -connect example.com:443 -servername example.com   # full handshake
echo | openssl s_client -connect host:443 2>/dev/null | openssl x509 -noout -dates
curl -v https://example.com                        # headers + TLS summary
curl -w '@curl-format.txt' -o /dev/null -s URL     # timing breakdown
```

`-servername` matters — without SNI you may get the wrong certificate entirely and chase a phantom problem.

The **curl timing breakdown** is the highest-value single tool for "why is this slow," because it attributes the time to a layer:

```text
# curl-format.txt
dns:      %{time_namelookup}s
tcp:      %{time_connect}s
tls:      %{time_appconnect}s
ttfb:     %{time_starttransfer}s
total:    %{time_total}s
```

Read the *deltas*: big `dns` → resolver problem. Big `tcp - dns` → network distance or SYN retries. Big `tls - tcp` → handshake/cert-chain cost. Big `ttfb - tls` → **the server is slow, not the network.** That last one ends a lot of pointless network investigations.

## Step 6 — the wire
<!-- bite: 478f5583-f87d-48ab-9279-8aca1278258a -->

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
- **Handshake fine, then silence on a large response** → classic [[networking/02-the-link-layer|MTU black hole]]. Confirm with `ping -M do -s 1472 host`, decreasing the size until it passes.

For [[networking/13-quic-and-modern-transport|QUIC/HTTP3]], packet capture shows you almost nothing — it's encrypted by design. Use **qlog** or `SSLKEYLOGFILE` with Wireshark instead.

## Common failure signatures, indexed by symptom
<!-- bite: c85c6f77-9862-4b2c-ad42-df0d19f0eea2 -->

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
<!-- bite: 4b98596a-5618-46e0-9e63-275608d8446e -->

Network debugging is **binary search over the stack**, and the reason it feels hard is that people start at the layer they're most comfortable with rather than the layer that's cheapest to eliminate. Every tool here answers one narrow question; the skill is choosing the question whose answer removes the most possibilities. And the most valuable single distinction in the whole practice costs you three seconds: **refused (fast) means you got there and were told no; hung (slow) means something in between never told you anything.**

## Check your understanding
<!-- bite: 2e3002c2-4e82-4f20-837f-eb58eff662fc -->

Try each one before you open the answer.

1. <!-- q: mcq id="01ddd740" -->
   Your app runs fine on your laptop, but colleagues can't reach it. `ss -lntp` shows it listening on `127.0.0.1:3000`. What's wrong?

   - [ ] A firewall blocks port 3000
   - [x] It's bound to localhost only, so it never accepts connections from other machines
   - [ ] DNS is wrong
   - [ ] The port is in `TIME_WAIT`

   <details><summary>Answer</summary>

   Bound to loopback. Bind to `0.0.0.0:3000` (or the machine's real address) to accept remote connections.

   </details>

2. <!-- q: exact id="20d7bb22" answer="dig +trace" -->
   A domain doesn't resolve and you want to see which level of the hierarchy (root, TLD or authoritative) is broken. Which `dig` option walks the chain for you? Give `dig` and the option.

   <details><summary>Answer</summary>

   `dig +trace example.com`. It starts at the root and follows each delegation itself. `dig @8.8.8.8` tells you whether your own resolver's cache is the problem.

   </details>

3. <!-- q: mcq id="f5292eda" -->
   The curl timing output for a slow request reads: `dns 0.004s`, `tcp 0.030s`, `tls 0.065s`, `ttfb 2.410s`. Where is the time going?

   - [ ] DNS
   - [ ] The TCP connection
   - [ ] The TLS handshake
   - [x] The server, after the connection was set up

   <details><summary>Answer</summary>

   The server. Read the gaps: DNS 4 ms, TCP 26 ms, TLS 35 ms, then 2.345 s between TLS finishing and the first byte. The network is fine; the application is slow.

   </details>

4. <!-- q: exact id="44702b0f" answer="1472" -->
   You suspect an MTU black hole on a 1500-byte link. `ping -M do -s N` sets the don't-fragment bit with an N-byte payload. The IP header is 20 bytes and the ICMP header 8. What is the largest N that fits in 1500 bytes?

   <details><summary>Answer</summary>

   1472 (1500 − 20 − 8). If that fails and smaller sizes pass, something on the path has a smaller MTU and the "too big" messages aren't getting back to you.

   </details>

5. <!-- q: mcq id="8f1868a0" -->
   A packet capture shows the client sending SYN, then SYN again after a second, then again after three seconds, and nothing ever comes back. What does it point to?

   - [ ] Nothing is listening on the port
   - [x] Packets are being dropped by a firewall, or the route is wrong
   - [ ] The server's receive buffer is full
   - [ ] TLS failed

   <details><summary>Answer</summary>

   A silent drop or a wrong route. If nothing were listening, the host would answer with RST at once. A full receive buffer would show `TCP ZeroWindow` on an established connection instead.

   </details>

6. <!-- q: open id="7b3ad9ac" -->
   Why does the lesson say not to start with `tcpdump` when something can't connect?

   <details><summary>Answer</summary>

   A capture without a hypothesis is an hour of scrolling. Most problems are found at the cheap steps: does the name resolve, is the host reachable, is the port open? Work up the layers with questions that each have a yes or no answer, and capture only when you know what you're looking for, with a tight filter.

   </details>

## Related
<!-- bite: 761053a4-c990-45b6-8b2a-fa86261cfb65 -->
- [[networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]] — the states `ss` reports
- [[networking/15-network-performance|Network Performance]] — interpreting the timings
- [[devops/07-observability/index|Observability]] — turning this into monitoring rather than firefighting
- [[devops/01-linux/index|Linux]] — the shell fluency this assumes

## About this lesson
<!-- bite: 11377d70-bed4-4734-a7ad-00470830784c -->

**Level:** Intermediate. **Covers:** the practical payoff. Everything above becomes useful when something is broken at 2am and you need to find out *where*. This note is a method plus a toolkit, in the order you should actually use them.
