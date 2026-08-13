# Networking — From the Wire to the Web

The foundation layer under [[devops/README|DevOps]], [[cybersecurity/README|cybersecurity]], [[architecture/README|distributed systems]], and every backend service you will ever debug. This folder was empty for a long time while three domains that *depend* on it were built out — this is the floor going in underneath them.

**Source:** roadmap.sh has no standalone networking roadmap, so this is built from the canon — Kurose & Ross (*Computer Networking: A Top-Down Approach*), Stevens' *TCP/IP Illustrated*, RFCs where precision matters, and Grigorik's *High Performance Browser Networking* for the performance half. `[reference]` — theory to study *and* verify at a terminal.

**Every note opens with a plain-language "kid version first" intuition before going to full depth, and ends with a Key insight.** Same convention as [[architecture/04-distributed-systems/README|distributed systems]].

## How this differs from the networking notes elsewhere in the vault

Three folders touch networking, deliberately, at different altitudes:

| Folder | Altitude | Answers |
|---|---|---|
| **`foundations/networking/`** (here) | CS fundamentals | *Why* does TCP behave this way? What is actually happening on the wire? |
| [[devops/08-networking-and-web/README\|devops/08-networking-and-web]] | operations | Which DNS record do I set? How do I configure nginx? |
| [[cybersecurity/03-network-security/README\|cybersecurity/03-network-security]] | defence | How is this attacked, and how do I stop it? |

Read this folder once, and the other two stop being lists of facts to memorise.

## Part A — The model, and getting to the next machine

1. [[foundations/networking/01-what-a-network-is|What a Network Actually Is]] — **[Beginner]** — packet vs circuit switching, layering, encapsulation, the end-to-end argument, what happens when you load a webpage
2. [[foundations/networking/02-the-link-layer|The Link Layer]] — **[Beginner]** — frames, MTU and PMTU black holes, MAC addresses, ARP and its total lack of authentication, switches vs broadcast domains, why Wi-Fi breaks assumptions
3. [[foundations/networking/03-ip-addressing-and-subnetting|IP Addressing & Subnetting]] — **[Beginner→Intermediate]** — CIDR arithmetic you should do in your head, special ranges, NAT, IPv6
4. [[foundations/networking/04-routing|Routing]] — **[Intermediate]** — forwarding vs routing, longest prefix match, link-state vs distance-vector, BGP and why the internet's core is trust-based, traceroute's real semantics

## Part B — The transport layer (the heart of the course)

5. [[foundations/networking/05-udp-and-ports|UDP & Ports]] — **[Beginner→Intermediate]** — the minimum viable transport, the socket 4-tuple, when TCP's guarantees are actively harmful, and the congestion-control responsibility UDP hands you
6. [[foundations/networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]] — **[Intermediate]** — the handshake, SYN floods and SYN cookies, teardown, `TIME_WAIT`, the state machine, and what `CLOSE_WAIT` piling up means about your code
7. [[foundations/networking/07-tcp-reliability-and-flow-control|TCP Reliability & Flow Control]] — **[Intermediate→Advanced]** — sequence numbers, cumulative ACKs and head-of-line blocking, SACK, RTO vs fast retransmit, the receive window, the Nagle/delayed-ACK 40ms stall
8. [[foundations/networking/08-congestion-control|Congestion Control]] — **[Advanced]** — congestion collapse, slow start, why AIMD's shape is forced, CUBIC vs BBR, bufferbloat, incast and tail latency
9. [[foundations/networking/09-sockets-and-the-network-api|Sockets & the Network API]] — **[Intermediate]** — the BSD API, the options that matter, C10K and the `select`→`epoll`→`io_uring` progression, and the four ways the file metaphor lies to you

## Part C — Names, security, and the application layer

10. [[foundations/networking/10-dns-in-depth|DNS in Depth]] — **[Intermediate]** — the resolution walk, TTL discipline, DNSSEC vs DoH (orthogonal, routinely confused), and why DNS causes so many outages
11. [[foundations/networking/11-http-evolution|HTTP and Its Evolution]] — **[Intermediate]** — 1.1's flaws and the obsolete workarounds still in your codebase, HTTP/2 multiplexing, and the transport-layer flaw it couldn't fix
12. [[foundations/networking/12-tls-and-transport-security|TLS & Transport Security]] — **[Intermediate→Advanced]** — forward secrecy, the chain of trust, what TLS 1.3 deleted and why deletion *was* the security fix, mTLS, and what the padlock does not mean
13. [[foundations/networking/13-quic-and-modern-transport|QUIC & Modern Transport]] — **[Advanced]** — real stream multiplexing, connection migration, and escaping protocol ossification by hiding from the network

## Part D — Performance and operations

14. [[foundations/networking/14-nat-firewalls-and-middleboxes|NAT, Firewalls & Middleboxes]] — **[Intermediate→Advanced]** — NAT traversal (STUN/TURN/ICE/hole punching), reject vs drop, proxies and request smuggling, ossification as Hyrum's Law at internet scale
15. [[foundations/networking/15-network-performance|Network Performance]] — **[Intermediate→Advanced]** — latency vs bandwidth, the BDP, counting round trips, the `√p` loss penalty, tail latency
16. [[foundations/networking/16-debugging-networks|Debugging Networks]] — **[Intermediate]** — bisecting the layers, `dig`/`mtr`/`ss`/`curl -w`/`tcpdump`, and a symptom-indexed failure table

## Interview prep

[[foundations/networking/interview/README|interview/]] — question bank with model answers, drawn from these notes.

## How to actually learn this

Reading alone doesn't stick here, for the same reason it doesn't in distributed systems: everything is invisible until you watch it. The path that works:

1. **Read Part A**, then immediately run `ip route`, `ip neigh`, and `mtr` against a server you own. Reconcile the output with the notes.
2. **Read Part B**, then run `tcpdump` on a `curl` and *find the three-way handshake by eye*. This is the single highest-value exercise in the folder — the handshake stops being a diagram and becomes a thing you've seen.
3. **Build something**: a TCP echo server with raw sockets, then a length-prefixed protocol on top (you will hit the "TCP is a byte stream, not a message stream" bug, which is the point). Then an HTTP/1.1 server from scratch. → [[project-ideas|Project Ideas]]
4. **Read Part C–D** once you've felt the problems they solve.
5. **Break things deliberately**: `tc qdisc` can add latency and packet loss to your own interface. Watch throughput collapse as you add 1% loss — the `√p` from note 15 in front of your eyes.

```sh
# add 100ms latency and 1% loss to your loopback, then measure
sudo tc qdisc add dev lo root netem delay 100ms loss 1%
sudo tc qdisc del dev lo root          # undo
```

## Related
- [[foundations/os/fundamentals|OS Fundamentals]] — sockets are file descriptors; this sits directly on top
- [[architecture/04-distributed-systems/README|Distributed Systems]] — what happens when unreliable networks meet multiple machines
- [[devops/08-networking-and-web/README|Networking & Web (devops)]] — the operational layer above this
- [[cybersecurity/03-network-security/README|Network Security]] — attacking and defending everything here
- [[PRIMETECHIE|The Primetechie Path]] — where this folder sits in the wider progression
