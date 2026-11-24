---
id: a8d81f2f-bce7-40c5-94b8-ee4b187764fa
---

# UDP & Ports — The Minimum Viable Transport

A port is a number that says which app on a device a message is for, and UDP is the simplest way of sending messages to that app. Your phone runs many apps at once, so it needs a way to hand each message to the right one. Online games and voice calls often use UDP because it is quick.

## The kid version first
<!-- bite: 30800e11-356d-4d7a-b396-2dccb28794a6 -->

IP gets a packet to a **house**. But a house has many people in it — the browser, the game, the music app, the SSH session. IP has no idea which one wants this packet.

A **port number** is the name on the door inside the house. IP delivers to the building; the transport layer delivers to the room.

That's it. That's the one thing the transport layer *must* do, and UDP does exactly that and nothing else.

## What UDP is
<!-- bite: 62329b1c-4c0c-4ff4-8fdf-cc0378383c41 -->

Eight bytes of header. That's the entire protocol:

```text
 0                   16                  32
+--------------------+--------------------+
|    Source Port     |  Destination Port  |
+--------------------+--------------------+
|      Length        |      Checksum      |
+--------------------+--------------------+
|                 Payload                 |
```

Ports for **multiplexing** (which program), length, and a checksum for **integrity** (did the bits get corrupted). Nothing else. No connection, no ordering, no retransmission, no flow control, no congestion control.

So UDP inherits IP's promises exactly: your datagram **may be lost, may arrive out of order, may arrive twice**, and you will not be told which. What UDP adds over raw IP is only: *the right program gets it, and it wasn't corrupted in transit.*

## The socket 4-tuple — how the OS demultiplexes
<!-- bite: 919facb3-d659-440c-83f9-a533932184c7 -->

A connection is identified by four values:

```text
(source IP, source port, destination IP, destination port)
```

Two browser tabs to the same server share three of those and differ only in **source port** — which the OS picks from the *ephemeral port range* (typically 32768–60999 on Linux, `net.ipv4.ip_local_port_range`). That's why one client can hold ~28,000 simultaneous connections to a single destination and then start failing with "cannot assign requested address": it has run out of source ports *for that destination*. The fix is more destination IPs/ports, not more client machines.

Port conventions: **0–1023** are well-known and require root to bind on Unix (a historical trust assumption that means very little today), **1024–49151** registered, above that ephemeral. Worth knowing cold: 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, 5432 Postgres, 3306 MySQL, 6379 Redis, 27017 MongoDB.

## Why anyone chooses UDP
<!-- bite: 1942c0d1-1148-4987-be3a-270423428b35 -->

Given that it guarantees nothing, why is it everywhere? Because for a large class of applications **TCP's guarantees are actively harmful**:

- **Retransmission is useless for real-time media.** In a voice call, a packet of audio that arrives 400ms late is worse than a packet that never arrives — you'd have to either play it out of order or stall the whole stream to wait for it. Better to conceal the gap and keep going. This is the single strongest argument for UDP.
- **Head-of-line blocking.** TCP delivers bytes strictly in order, so one lost packet stalls delivery of *everything behind it*, even data that already arrived intact and belongs to an unrelated message. For anything multiplexing independent streams, that's a self-inflicted wound. → this is exactly the flaw [[networking/13-quic-and-modern-transport|QUIC]] was built to fix.
- **One-shot request/response doesn't need a connection.** A DNS query is one small packet out, one small packet back. A TCP handshake would *triple* the cost. If it's lost, just ask again.
- **You want to build your own semantics.** Game networking, QUIC, and modern RPC systems all want reliability *for some things* and not others, custom congestion control, or connection migration. TCP is baked into the kernel and can't be reshaped; UDP is a blank slate.

Real users: **DNS** (queries), **QUIC/HTTP3**, **WebRTC** (voice/video), **DTLS**, most **game netcode**, **DHCP**, **NTP**, **syslog**, **VXLAN** and other tunnels, and high-frequency metrics (StatsD — losing a metric sample is fine, blocking your app to deliver one is not).

## The trap: UDP without congestion control
<!-- bite: 82d1caf4-4abb-4049-840c-f8c9ad3c145a -->

Here's the part that gets skipped, and it matters. TCP's [[networking/08-congestion-control|congestion control]] is not just for TCP's benefit — it's what stops the internet collapsing. Every TCP flow voluntarily slows down when the network is loaded.

A UDP application that just blasts packets at a fixed rate does **not** back off. Deployed at scale, it starves every TCP flow sharing the path (they back off, it doesn't) and can drive the network into **congestion collapse** — the 1986 NSFNET event where throughput dropped by a factor of a thousand because everyone was retransmitting into an already-saturated network.

So the real rule is: **choosing UDP means you have accepted responsibility for congestion control yourself.** QUIC and WebRTC both implement full congestion control in userspace precisely because they had to. If you write a UDP protocol and skip this, you have not built something simpler than TCP — you've built something antisocial.

The related operational reality: UDP is the workhorse of **amplification DDoS**. Spoof the victim's source address, send a small query to a server that returns a large answer (DNS, NTP, memcached), and the reply lands on the victim — a 50×+ amplification. UDP's lack of a handshake is what makes source-address spoofing productive, and it's why open resolvers are a liability. → [[cybersecurity/06-attacks-and-threats/index|attacks & threats]]

## Choosing between them
<!-- bite: 737fba98-92ee-451b-8fa2-297ab2e82714 -->

| Use TCP when | Use UDP when |
|---|---|
| Every byte must arrive, in order | Late data is worthless (real-time media) |
| The transfer is long-lived (a file, a stream of requests) | It's a single small request/response (DNS) |
| You don't want to think about loss | You need custom reliability/congestion semantics |
| You'd otherwise reimplement TCP badly | You're multiplexing independent streams (→ use QUIC) |

The honest default is TCP. If your reason for UDP is "TCP is slow," you're probably reaching for the wrong fix — measure first ([[networking/15-network-performance|performance]]), and consider QUIC, which gives you UDP's flexibility with reliability already correctly implemented.

## Key insight
<!-- bite: fec31fb4-4390-404b-b3a0-e10b00b11987 -->

UDP is not "TCP without the good parts" — it's **the transport layer with the end-to-end principle taken seriously**. It provides only what genuinely cannot be done at the application layer (demultiplexing to the right process), and leaves every other decision to the application that actually knows its own requirements. That's why the most sophisticated modern transport, QUIC, is built *on top of* the dumbest one.

## Check your understanding
<!-- bite: 27bc93f6-e8e7-4e6f-b9c5-fc933c0d62a4 -->

Try each one before you open the answer.

1. <!-- q: exact id="c7904f46" answer="8" -->
   How many bytes is a UDP header?

   <details><summary>Answer</summary>

   8: source port, destination port, length and checksum, 2 bytes each.

   </details>

2. <!-- q: mcq id="e3a0e1dc" -->
   What does UDP add on top of IP? Choose all that apply.

   - [x] Delivery to the right program, using ports
   - [x] A checksum to detect corrupted data
   - [ ] Retransmission of lost datagrams
   - [ ] Delivery in order

   <details><summary>Answer</summary>

   Ports and a checksum, and nothing else. A datagram can still be lost, reordered or duplicated, and nobody tells you.

   </details>

3. <!-- q: exact id="cb0e70e4" answer="28232" accept="28,232" -->
   A Linux client's ephemeral port range is 32768 to 60999, inclusive. Roughly how many simultaneous connections can it open to one server IP and port before it runs out of source ports?

   <details><summary>Answer</summary>

   28,232 (60999 − 32768 + 1). Every connection to the same destination needs a different source port, because the 4-tuple must be unique. After that you get "cannot assign requested address". More destination IPs or ports fix it.

   </details>

4. <!-- q: mcq id="a8c8b162" -->
   Why do voice calls usually run over UDP rather than TCP?

   - [ ] UDP has a larger maximum packet size
   - [x] A chunk of audio that arrives late is worse than one that never arrives, so retransmitting is useless
   - [ ] UDP is encrypted by default
   - [ ] TCP can't carry audio

   <details><summary>Answer</summary>

   Late audio can't be played, and TCP's retransmission and in-order delivery would stall the whole stream waiting for it. Better to hide the gap and keep going.

   </details>

5. <!-- q: open id="043b85f3" -->
   You build a UDP protocol that sends at a fixed high rate and never slows down. Why is this harmful to other people's traffic?

   <details><summary>Answer</summary>

   TCP flows back off when the network is congested, but yours doesn't. On a shared path, your flow takes the capacity they give up, starving them, and at scale this can drive the network into congestion collapse. Choosing UDP means you take on congestion control yourself, as QUIC and WebRTC do.

   </details>

6. <!-- q: open id="eb804e8c" -->
   How do attackers use open DNS or NTP servers to flood a victim with traffic far larger than what they send?

   <details><summary>Answer</summary>

   They send small UDP queries with the victim's address forged as the source. The servers send their much larger replies to the victim, often 50 times bigger or more. UDP has no handshake to prove where a request came from, which is why forged source addresses work and why open resolvers are a liability.

   </details>

## Related
<!-- bite: 41a0d517-77d4-47e2-a4b0-ef74cb3eb503 -->
- [[networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]] — what a connection costs
- [[networking/08-congestion-control|Congestion Control]] — the responsibility UDP hands you
- [[networking/13-quic-and-modern-transport|QUIC]] — what happens when you rebuild TCP properly on UDP
- [[networking/09-sockets-and-the-network-api|Sockets]] — the 4-tuple in code

## About this lesson
<!-- bite: cbdffb3e-1ccc-4f79-a473-e2f45a02812d -->

**Level:** Beginner→Intermediate. **Covers:** the transport layer's smallest possible implementation. Read this before TCP: UDP shows you what the transport layer *must* do, so that everything TCP adds is visible as a deliberate choice rather than an inevitability.
