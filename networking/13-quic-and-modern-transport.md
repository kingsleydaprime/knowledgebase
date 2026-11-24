---
id: e1d23679-332a-47d8-a781-0c4ea2ef213c
---

# QUIC & Modern Transport

QUIC is a newer way of sending data across the internet, built to fix problems with TCP that could not be fixed inside TCP itself. YouTube, Google and many other big sites already use it. It brings together lessons from the earlier parts of this course.

## The kid version first
<!-- bite: 5e97e914-5765-4b27-aa16-28be45d9b0cb -->

TCP has four problems that can't be fixed *inside* TCP:

1. One lost postcard stalls **every** conversation sharing the connection.
2. Setting up takes several rounds of introductions (handshake, then encryption handshake) before you say anything real.
3. Move from Wi-Fi to mobile data and the connection **dies**, because its identity is its address.
4. Improving TCP means updating every operating system and every router on Earth. That takes a decade, if it happens at all.

QUIC's answer: **build a new transport on top of [[networking/05-udp-and-ports|UDP]], in userspace.** UDP is just "here are some bytes, for this port" — a blank slate that already passes through every network on Earth. Everything TCP does well gets reimplemented on top, properly, in a library that ships with the application and can be updated in a browser release rather than a kernel release.

## What QUIC actually fixes
<!-- bite: 97e64f6c-b45c-4baf-a9fa-d81b3b3e5fb0 -->

### 1. Real stream multiplexing — no head-of-line blocking

The headline. QUIC has **independent streams**, each with its own sequence numbering and delivery guarantee. A lost packet blocks **only the stream whose data it carried**; every other stream keeps delivering.

This is the thing [[networking/11-http-evolution/index|HTTP/2]] wanted and could not have, because it was multiplexing on top of a transport that insists on total ordering. QUIC moves the multiplexing *below* the reliability boundary, so ordering is per-stream rather than per-connection.

The consequence: **HTTP/3 on a lossy network (mobile, congested Wi-Fi) substantially outperforms HTTP/2**, which is precisely where HTTP/2 could lose to HTTP/1.1.

### 2. Handshake collapse — 1-RTT, and 0-RTT on resumption

TCP+TLS 1.3 is 2 RTT (one for TCP, one for TLS). QUIC **fuses the transport and cryptographic handshakes into one exchange**: 1 RTT for a new connection, **0 RTT** for a resumed one — application data rides in the very first packet.

The security caveat from [[networking/12-tls-and-transport-security/index|TLS]] carries over exactly: 0-RTT data is replayable, so restrict it to idempotent requests.

### 3. Connection migration

A TCP connection *is* its 4-tuple. Change your IP — walk out of Wi-Fi range onto mobile data — and the connection is dead by definition; the application must reconnect and redo every handshake.

QUIC identifies connections by a **connection ID** carried in the packet, independent of the addresses. Your IP changes, the connection ID doesn't, the connection survives. Your video call doesn't drop when you leave the house. This is impossible to retrofit into TCP because the 4-tuple identity is baked into every stack and every middlebox.

(Connection IDs are also *rotated* to prevent the ID becoming a tracking identifier across networks — a nice example of privacy designed in rather than bolted on.)

### 4. Escaping ossification

The deepest point. TCP is implemented in kernels and inspected by middleboxes worldwide. Adding a TCP feature means: get it standardised, get it into every OS, wait for deployment, *and* discover that middleboxes drop packets with options they don't recognise. **TCP Fast Open** was standardised in 2014 and is still not reliably usable, because middleboxes mangle it.

QUIC responds by **encrypting almost the entire packet, including most of the header** — not only for privacy, but so middleboxes *cannot* parse or "helpfully" modify it. If they can't see it, they can't ossify it. The protocol deliberately hides itself from the network to preserve its own ability to evolve.

Combined with userspace implementation (it ships in Chrome, in your app's library), QUIC can iterate on version timescales of *weeks*. That's the real long-term significance.

## What QUIC costs
<!-- bite: 85f41fd0-5f43-4374-a0c3-e3575c2fc2de -->

An honest accounting, because it isn't free:

- **CPU.** Userspace processing plus per-packet encryption is heavier than kernel TCP with decades of hardware offload (TSO/GRO/checksum offload). Early deployments saw 2–3× the CPU per byte; hardware offload and `io_uring`-style APIs are closing the gap, but it's still the main reason large-scale operators hesitate.
- **UDP's second-class status.** Some networks rate-limit or block UDP outright, on the assumption that it's only DNS and attack traffic. Every QUIC client therefore needs a **TCP fallback path**, which means you now maintain both.
- **Operational opacity.** You can't `tcpdump` a QUIC stream and read it — that's the point, but it also means your existing network monitoring, IDS, and debugging tooling sees an opaque blob. Debugging moved to endpoint logging (**qlog**) and `SSLKEYLOGFILE`.
- **Ampli­fication protection adds complexity.** Because UDP has no handshake, a QUIC server must not send more than 3× what it received from an unvalidated address, or it becomes a DDoS amplifier. Address validation tokens exist for this.

## HTTP/3 = HTTP over QUIC
<!-- bite: fd534b09-7831-452b-9091-4f426cd6f33e -->

HTTP/3 keeps HTTP's semantics unchanged (same methods, headers, status codes) and swaps the transport. Two adjustments were needed:

- **QPACK replaces HPACK.** HPACK's compression state assumed ordered delivery — the exact assumption QUIC removes. QPACK adds careful handling so a header block never blocks on a table update that hasn't arrived, reintroducing head-of-line blocking through the back door.
- **Discovery.** You can't just try HTTP/3 blindly. A server advertises `Alt-Svc: h3=":443"` over HTTP/2, or publishes an **HTTPS/SVCB DNS record**, and the client upgrades on a later connection. Note that this means **the first visit is usually still over TCP** — HTTP/3's benefit lands on repeat visits.

## Where this is going
<!-- bite: c054f20a-574c-4448-bb22-b4fa3a468828 -->

- **MASQUE** — proxying arbitrary UDP/IP over QUIC. The machinery behind iCloud Private Relay and modern VPN-over-HTTPS designs.
- **WebTransport** — the browser API for QUIC streams and datagrams, i.e. the long-overdue replacement for WebSockets that supports unreliable and multiplexed delivery.
- **Media over QUIC (MoQ)** — live streaming that gets low latency without the reliability tax, in a way neither RTMP nor HLS manages.
- **Post-quantum key exchange** — already shipping in TLS/QUIC hybrids (X25519+ML-KEM), specifically because of "harvest now, decrypt later."

## Key insight
<!-- bite: 262bd9c1-5086-4c85-a972-21c3243afea9 -->

QUIC's most important contribution isn't multiplexing or 0-RTT — it's **relocating the transport layer to somewhere it can still be changed.** Layering was supposed to allow independent evolution, but middleboxes broke that by inspecting layers that weren't theirs, freezing TCP in place. QUIC restores evolvability by two moves: **encrypt the layer so nobody downstack can read it, and implement it in userspace so it deploys at application speed.** The lesson generalises far past networking: *an interface that everyone can see and depend on will ossify, so hide what you intend to keep changing.*

## Check your understanding
<!-- bite: 7b7ea23e-bb33-4347-a376-fdd80e2b0963 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ad02fb33" -->
   A page loads 20 files over one HTTP/3 connection, and one packet carrying part of file 7 is lost. What waits for the retransmission?

   - [ ] All 20 files
   - [x] Only file 7's stream
   - [ ] Files 7 to 20
   - [ ] Nothing, because QUIC never retransmits

   <details><summary>Answer</summary>

   Only file 7. QUIC streams are ordered independently, so a loss blocks just the stream whose data it carried. Over HTTP/2 on TCP, all 20 would stall.

   </details>

2. <!-- q: exact id="88ad5845" answer="0" -->
   A browser reconnects to a QUIC server it visited yesterday and has resumption data. How many round trips pass before it can send its first request?

   <details><summary>Answer</summary>

   0. With 0-RTT resumption, the request rides in the very first packet. A brand-new connection needs 1 round trip, and TCP with TLS 1.3 needs 2. 0-RTT data can be replayed, so use it only for idempotent requests.

   </details>

3. <!-- q: open id="8461a692" -->
   You walk out of your house during a video call and your phone moves from Wi-Fi to mobile data. Why does a QUIC connection survive this when a TCP connection can't?

   <details><summary>Answer</summary>

   A TCP connection is its 4-tuple, so a new IP address means a different connection, and the old one is dead. QUIC identifies the connection by a connection ID inside the packet, independent of addresses, so the same connection carries on from the new address.

   </details>

4. <!-- q: mcq id="4dbd90f3" -->
   Why is QUIC built on UDP instead of being a brand-new IP protocol?

   - [ ] UDP is faster than any new protocol could be
   - [x] Middleboxes drop protocols they don't recognise, and UDP is one of the few that passes almost everywhere
   - [ ] UDP already provides reliability
   - [ ] New IP protocols are not allowed by the standards

   <details><summary>Answer</summary>

   Ossification. A new protocol number would be dropped by countless firewalls and NATs. UDP gets through, and QUIC builds everything else on top in user space.

   </details>

5. <!-- q: open id="e1232c42" -->
   QUIC encrypts almost the whole packet, including most of the header. Besides privacy, why?

   <details><summary>Answer</summary>

   So middleboxes can't read or change it, which means they can't come to depend on it. TCP froze because boxes in the network inspected its options and dropped anything unusual. By hiding its internals, QUIC keeps the freedom to change, and since it lives in user space it can ship new versions in weeks.

   </details>

6. <!-- q: mcq id="dad0d106" -->
   Why is a user's first visit to a site usually still over TCP, even when the server supports HTTP/3?

   - [ ] Browsers only try HTTP/3 on Fridays
   - [x] The client learns that HTTP/3 is available from an `Alt-Svc` header or an HTTPS DNS record, and upgrades on a later connection
   - [ ] QUIC needs a certificate the first visit doesn't have
   - [ ] HTTP/3 only works for images

   <details><summary>Answer</summary>

   The client can't know about HTTP/3 in advance unless DNS advertises it, so it often starts on TCP, sees `Alt-Svc: h3=":443"`, and switches next time. Clients also keep a TCP fallback, since some networks block UDP.

   </details>

## Related
<!-- bite: 37cc903b-d9b9-44fa-bda9-b599cbb858b4 -->
- [[networking/07-tcp-reliability-and-flow-control|TCP Reliability]] — the head-of-line blocking QUIC escapes
- [[networking/12-tls-and-transport-security/index|TLS]] — the handshake QUIC absorbed
- [[networking/11-http-evolution/index|HTTP Evolution]] — the story this concludes
- [[networking/14-nat-firewalls-and-middleboxes|Middleboxes]] — the ossification QUIC routes around

## About this lesson
<!-- bite: faea938a-2582-4eb4-8d84-002321668d50 -->

**Level:** Advanced. **Covers:** the payoff note. QUIC is what you get when you take every complaint in the previous seven notes seriously and rebuild the transport layer from scratch. It's also a case study in **how to deploy a new protocol on an internet that no longer permits new protocols.**
