# Networking Interview — Debugging & Scenarios

From [[foundations/networking/14-nat-firewalls-and-middleboxes|14-nat-firewalls-and-middleboxes]], [[foundations/networking/15-network-performance|15-network-performance]], [[foundations/networking/16-debugging-networks|16-debugging-networks]].

**These are the questions that actually differentiate people.** Reciting the handshake is table stakes; driving an investigation is the signal. In every one of these, *say your method out loud* — the interviewer is grading how you narrow the search space, not whether you guess right immediately.

---

### Q1. [Intermediate] 🔥 "The service is down." Walk me through your investigation.

**Strong answer covers — bisect the layers, cheapest question first:**

1. **Is the name resolving?** `dig +short svc` / `dig @8.8.8.8 svc` to distinguish "record is wrong" from "my resolver is stale."
2. **Is the host reachable?** `mtr host` (not `ping` alone — ICMP is often blocked, and mtr shows per-hop loss over time).
3. **Is the port open?** `nc -vz host port`. **This is the highest-value step** — see Q2.
4. **Does TLS complete?** `openssl s_client -connect host:443 -servername host` — check dates and the full chain.
5. **Does the app respond?** `curl -v`, and `curl -w` for a timing breakdown.
6. **Only now**, packet capture with a tight filter.

**The framing that scores:** each step should have a **binary answer that eliminates half the remaining possibilities**. Starting at tcpdump without a hypothesis is a wasted hour, and saying so demonstrates judgement.

---

### Q2. [Intermediate] 🔥 What's the difference between "connection refused" and a connection that hangs?

**Strong answer covers:** **"Connection refused" is instant** — you reached the host and something actively said no (a TCP **RST** or ICMP unreachable). Nothing is listening on that port, or the firewall is set to REJECT. **A hang until timeout** means something is **silently dropping** — a firewall/security group set to DROP, a wrong route, or an MTU black hole.

**Why it's the most useful distinction in network debugging:** it instantly tells you whether to look at the *application* (it's not running / bound to the wrong interface) or at the *network* (something in between is discarding your packets, quietly). Cloud security groups DROP, so they hang; a stopped service refuses instantly.

**The follow-up to be ready for:** the most common self-inflicted version of "refused" is a service **bound to `127.0.0.1` instead of `0.0.0.0`**. `ss -lntp` shows it in one line.

---

### Q3. [Intermediate] 🔥 An app works over the office LAN but large responses hang over the VPN. What's your first hypothesis?

**Strong answer covers:** **MTU / PMTU black hole.** The VPN adds encapsulation headers, shrinking the usable MTU below 1500. Packets exceeding the path MTU are dropped, and the ICMP "Packet Too Big" messages that would tell the sender to shrink are being blocked by a firewall. Small packets (handshake, request) fit and work; the first large response vanishes.

**How to confirm:** `ping -M do -s 1472 <host>` (1472 + 28 bytes of headers = 1500), decreasing the size until it succeeds — that finds the real path MTU.

**The fix:** allow ICMP type 3 code 4, clamp MSS on the tunnel (`--clamp-mss-to-pmtu`), or lower the interface MTU. And note this is the same class of bug that bites Kubernetes overlay networks.

---

### Q4. [Intermediate] Your page loads in 200ms locally and 3 seconds for users in another continent. The link is 1 Gbps. What's happening?

**Strong answer covers:** **latency, not bandwidth.** Round trips dominate. DNS + TCP + TLS + request ≈ 4 RTTs before the first byte; at 250ms RTT that's a second before anything renders. Then **slow start** caps the first response near 14 KB and doubles per RTT, so a 100 KB page costs several more round trips *regardless of link speed*.

**Latency is bounded by physics** — light in fibre is ~200,000 km/s, so distance sets a floor you cannot buy your way under.

**The fixes, ranked — and the ranking is the answer:** *don't make the request* (caching, `immutable` on hashed assets) > *make it closer* (CDN/edge — the only thing that reduces RTT itself) > *make it in fewer trips* (TLS 1.3, QUIC 0-RTT, connection reuse, `preconnect`) > *make it faster*.

**Bonus:** check for HTTP/1.1-era workarounds still in place — domain sharding actively hurts here.

---

### Q5. [Advanced] Throughput between two data centres is 40 Mbps on a 1 Gbps link. Where do you look?

**Strong answer covers — two candidate causes, and how to tell them apart:**

1. **Window too small for the BDP.** `BDP = bandwidth × RTT`; a 1 Gbps link at 100ms needs **12.5 MB in flight**. If the receive window is smaller, you physically cannot saturate the link. Check whether **window scaling** is negotiated — a middlebox stripping the option produces exactly "fine locally, slow long-distance." Check kernel buffer autotuning (`net.ipv4.tcp_rmem`), and note that manually pinning `SO_RCVBUF` *disables* autotuning and usually makes things worse.
2. **Packet loss.** Mathis: `throughput ≈ MSS / (RTT × √p)`. At 1500 MSS and 100ms RTT, **0.1% loss caps you around 38 Mbps** — which matches the symptom suspiciously well. A "negligible" 1% loss costs ~90% of throughput.

**How to distinguish:** `ss -tin` shows `cwnd`, `rtt`, and `retrans` per socket. Rising retransmits → loss. Flat small cwnd with no retransmits → window limit. `mtr` finds where the loss is.

**If it's loss on a long or lossy path:** switching congestion control to **BBR** (`net.ipv4.tcp_congestion_control=bbr`) can be a dramatic single-line win, because it doesn't treat loss as the sole congestion signal.

---

### Q6. [Intermediate] 🔥 A long-lived connection (WebSocket / DB pool) dies after a few minutes idle. Why?

**Strong answer covers:** a **stateful middlebox timed out the flow** — a NAT translation entry or a load balancer's idle timeout. Both endpoints still believe the connection is `ESTABLISHED`; nothing was sent to tell them otherwise. You discover it on the next write, minutes later.

**Why TCP doesn't save you:** TCP keepalive defaults to **2 hours** idle before the first probe — useless here.

**The fix:** application-level heartbeats every 30–60 seconds (WebSocket ping frames, a pool validation query), comfortably under typical NAT/LB timeouts. Or tune `TCP_KEEPIDLE`. This is why ORM connection pools have "test on borrow" and "max idle time" settings — and why misconfiguring them produces "the first request after a quiet period always fails."

---

### Q7. [Advanced] Why is your p99 latency 500ms when your median is 5ms?

**Strong answer covers:** **tail latency**, and often a transport-layer cause that never shows up in application profiling:

- **RTO after tail loss.** If the last packets of a response are lost, there's nothing behind them to trigger the 3-duplicate-ACK fast retransmit, so you wait for a full retransmission timeout — 200ms+ in a data centre where RTTs are microseconds.
- **Incast.** A scatter-gather fan-out to 40 servers returns 40 simultaneous responses that collide at the top-of-rack switch and overflow its shallow buffer.
- **Bufferbloat**, GC pauses coinciding with a retransmit, DNS timeouts.

**The amplification point that matters most:** if one user request fans out to 100 backend calls, the user waits for the **slowest**. With a p99 of 1s, a 100-call fan-out hits it ~63% of the time — **your median user experiences your p99 backend.**

**Mitigations:** hedged requests (issue a second request after p95 elapses, take the first answer), tied requests, reducing fan-out width, ECN/DCTCP in the data centre, lower RTO minimums. The reference is Dean & Barroso, "The Tail at Scale."

---

### Q8. [Intermediate→Advanced] 🔥 Two users behind different home routers want a direct peer-to-peer connection. How?

**Strong answer covers:** both are behind [[foundations/networking/03-ip-addressing-and-subnetting|NAT]] with no publicly reachable address, and a NAT only forwards packets matching an existing outbound mapping. So:

- **STUN** — each peer asks a public server "what does my address look like from outside?" to discover its external IP:port.
- **Hole punching** — both peers send packets to each other's discovered external addresses *simultaneously*. Each outbound packet creates a mapping in its own NAT, so the peer's incoming packet now matches an existing entry and is let through. You're deliberately tricking both NATs into believing each side initiated.
- **TURN** — when that fails, relay through a public server. Always works; costs bandwidth and latency.
- **ICE** — gathers all candidates (local, STUN, TURN) and races them in parallel, using whichever connects first. This is what WebRTC runs.

**The detail that shows real understanding:** hole punching **fails against symmetric NAT**, which assigns a different external port per destination — so the address STUN told you about isn't the one your peer will hit. Roughly 10–20% of connections fall back to TURN, which is why you must budget for TURN infrastructure rather than assuming P2P is free.

---

### Q9. [Intermediate] Why did enabling ECN break connectivity for some users, and what's the general lesson?

**Strong answer covers:** ECN lets routers **mark** packets as congested instead of dropping them — congestion signalled without loss or delay, strictly better than the alternative. But some **middleboxes dropped packets with the ECN bits set**, because they'd never seen them. So enabling ECN broke a small percentage of users, and nobody ships a feature that breaks 1% of traffic. Deployment was delayed ~20 years.

**The general lesson — protocol ossification:** middleboxes inspect and enforce assumptions about layers that aren't theirs, so **the internet became resistant to change at exactly the layers designed to evolve.** Same story killed TCP Fast Open and constrained MPTCP.

**Connect it to QUIC:** this is *why* QUIC runs on UDP and encrypts nearly its entire header — so middleboxes physically cannot parse and therefore cannot ossify it. And the generalisation is **Hyrum's Law**: any interface others can observe will be depended upon, and anything depended upon becomes impossible to change. It's the same reason you version APIs and keep internals private.

---

### Q10. [Intermediate] You're behind a reverse proxy and your rate limiter isn't working. What's likely wrong?

**Strong answer covers:** the server sees the **proxy's** IP for every request, so either everyone shares one bucket, or you're trusting `X-Forwarded-For` — which is **client-controllable**. A client can send their own `X-Forwarded-For` header and spoof any IP they like, bypassing rate limits and IP allowlists.

**The correct handling:** only trust the hops you actually control. Count from the **rightmost** entry inward by the number of trusted proxies in front of you, rather than taking the leftmost value. Or use the `PROXY` protocol, which carries the real client address out of band where the client can't forge it.

**Related, if the conversation goes there:** L7 proxies re-parse and re-serialise HTTP, and when front-end and back-end disagree about `Content-Length` vs `Transfer-Encoding`, you get **request smuggling** — a direct consequence of a middlebox interpreting a layer it doesn't own.

---

### Q11. [Intermediate] Everything got slow right after someone started a large upload. Video calls stutter, pages take seconds. Bandwidth graphs look fine.

**Strong answer covers:** **bufferbloat.** Cheap memory led vendors to fit huge buffers, reasoning a queued packet beats a dropped one. But loss-based congestion control **needs loss as its signal** — so it fills the entire buffer before noticing anything is wrong. Now every latency-sensitive packet queues behind seconds of bulk data. Throughput is fine; **latency is destroyed** — which is exactly why the bandwidth graph looks healthy.

**How to confirm:** run `mtr` *during* the transfer and watch latency climb across the board.

**The fix:** **AQM** — `fq_codel` (or `cake` on a home router). CoDel drops based on how long a packet has been *queued* rather than queue depth; `fq` gives each flow its own queue so a bulk transfer can't monopolise the buffer. It's a one-line change with a transformative effect, and knowing it is a good signal of practical experience.
