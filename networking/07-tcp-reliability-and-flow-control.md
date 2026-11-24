---
id: ccda0a7d-d37b-4cca-8302-8b642b333694
---

# TCP Reliability & Flow Control

- **Flow control** — don't overwhelm the **receiver**. Solved by the receive window.
- **Congestion control** — don't overwhelm the **network**. Solved by the congestion window. → [[networking/08-congestion-control|next note]]

Both limit how much you can send. They have nothing else to do with each other, and confusing them makes TCP performance impossible to reason about.

## The kid version first
<!-- bite: 184975d1-d4db-433b-b5c7-5e47d22762ee -->

You're reading a long book aloud to a friend over those unreliable postcards. To make sure they get every word in the right order:

1. **Number every word.** Now they can tell if word 57 is missing, and can put words back in order if 58 arrives before 57.
2. **Have them say "I've got everything through word 56."** That's an acknowledgement.
3. **If nobody confirms word 57 after a while, say it again.** That's retransmission.
4. **Don't wait for confirmation after every word** — you'd take forever. Send a batch, wait for confirmations, send more. That's the sliding window.
5. **Let them say "slow down, my notebook is full."** That's flow control.

Every mechanism below is a refinement of one of those five.

## Sequence numbers and cumulative ACKs
<!-- bite: 6875838e-e450-4e98-867d-9f38186341b7 -->

TCP numbers **bytes**, not packets. The header carries a sequence number (the position of this segment's first byte in the stream) and an acknowledgement number.

The ACK is **cumulative**, and it means something precise that people misread: `ack=1000` means *"I have received every byte up to 999, and 1000 is the next one I want."* It is a statement about a contiguous prefix, not about the last packet received.

That definition has a sharp consequence. If you send bytes 1000–1999, 2000–2999, 3000–3999 and the middle one is lost, the receiver **cannot** say "I got the first and third." It can only keep saying `ack=2000`. The receiver holds 3000–3999 in its buffer but cannot deliver it to the application — bytes must be delivered in order.

That is **head-of-line blocking**, and it's not a bug; it's the direct price of the in-order byte-stream abstraction. If your connection is carrying twenty independent HTTP requests ([[networking/11-http-evolution/index|HTTP/2]]), one lost packet stalls all twenty. This single fact is why [[networking/13-quic-and-modern-transport|QUIC]] exists.

**SACK** (Selective Acknowledgement, RFC 2018) patches the diagnostic half of the problem: an option that says "additionally, I have 3000–3999." The sender then retransmits only the true gap instead of everything after it. Universally supported and a large real-world win — but note it fixes *sender efficiency*, not head-of-line blocking. The receiver still can't deliver out of order.

## Detecting loss: timeout vs. duplicate ACKs
<!-- bite: 9f266dd5-fbc2-4279-aeb3-033f8b7e4038 -->

Two mechanisms, and the difference in their cost is enormous.

**Retransmission timeout (RTO)** — the slow path. The sender estimates the round-trip time continuously (a smoothed average plus a variance term, Jacobson's algorithm) and sets `RTO ≈ SRTT + 4×RTTVAR`. If no ACK arrives in time, retransmit and **double the RTO** (exponential backoff). The initial RTO is 1 second, so a lost packet at connection start costs a *full second* — catastrophic for a page load, and one of the reasons early-connection loss hurts so much more than steady-state loss.

**Fast retransmit** — the fast path. Every out-of-order segment makes the receiver re-send its current cumulative ACK. Three **duplicate ACKs** tell the sender "a gap exists and traffic is still flowing" — enough evidence to retransmit immediately, without waiting for the timer. This turns a 1-second stall into roughly one RTT, and it's why TCP handles isolated loss gracefully but handles *tail* loss (the last packets of a response, with nothing after them to trigger duplicate ACKs) badly. **Tail Loss Probe** was added specifically for that case.

**RACK-TLP** (RFC 8985) is the modern replacement, now default on Linux: infer loss from *time* rather than counting duplicate ACKs — if a segment was sent more than an RTT before something that's already been ACKed, it's probably lost. Handles reordering far better than "three dupACKs," which misfires whenever the network mildly reorders packets.

**Karn's algorithm** is a subtle one worth knowing: never use a *retransmitted* segment's ACK to update the RTT estimate. You can't tell whether the ACK was for the original or the retransmission, so including it corrupts the estimate in exactly the situation where you need it most.

## Flow control: the receive window
<!-- bite: 1e8ffc4f-1d20-4c6c-9176-57f27984dffc -->

Every ACK carries a **window** field: "I have this many bytes of free buffer." The sender may never have more than that many unacknowledged bytes in flight. Simple, and it completely prevents a fast sender from drowning a slow receiver.

Three details that matter in practice:

- **Window scaling.** The field is 16 bits — max 64 KB. On a 100ms path that caps you at 640 KB/s no matter how fat the pipe, which is why the **window scale option** (RFC 7323, negotiated in the handshake, shifting the window up to 1 GB) is essential on any long-distance link. If a middlebox strips the option, you get a connection that works but is mysteriously slow — a classic "it's fast in the office, slow from the other continent" bug.
- **Zero window and the persist timer.** A receiver whose buffer is full advertises `window=0`. The sender stops. But the "I have room again" update is itself an ACK, and if *that* is lost, both sides wait forever. So the sender runs a **persist timer** and periodically pokes with a 1-byte probe. Deadlock avoidance built into the protocol.
- **Silly window syndrome.** A receiver draining one byte at a time would advertise a 1-byte window, and the sender would send 41-byte packets to carry 1 byte of data. Fixed on both sides: the receiver doesn't advertise tiny windows (waits until a decent chunk is free), and the sender doesn't send tiny segments (Nagle's algorithm, below).

**Autotuning:** modern kernels size receive buffers dynamically (`net.ipv4.tcp_rmem`). Manually pinning `SO_RCVBUF` disables autotuning and is usually a performance *regression*, not a win — a common cargo-cult mistake.

## Nagle's algorithm and delayed ACKs — the famous bad interaction
<!-- bite: 2824a690-48f0-4221-9766-69ad6b69ad79 -->

Two independent optimisations that combine into a notorious 40ms stall.

- **Nagle's algorithm** (sender side): don't send a small segment while an earlier small segment is still unacknowledged — buffer it and coalesce. Stops a telnet session sending a 41-byte packet per keystroke.
- **Delayed ACK** (receiver side): don't ACK immediately; wait up to ~40ms (200ms in some stacks) hoping to piggyback the ACK on outgoing data or combine two ACKs.

Now the pathology. Your application does a small write, then another small write, then waits for a response — a request that doesn't fit in one segment, which is extremely common with a header-then-body write pattern:

1. Sender sends chunk 1. Nagle holds chunk 2, because chunk 1 is unacknowledged.
2. Receiver has the incomplete request, so it can't respond. Delayed ACK holds the ACK, hoping for data to piggyback on.
3. **Both sides wait.** Nothing happens for 40ms until the delayed-ACK timer fires.

The symptom is latency quantised into suspicious 40ms multiples. The fixes: **`TCP_NODELAY`** to disable Nagle (what nearly every RPC library, database driver, and web server sets by default, and rightly so), or — better where you control it — **write your message in a single `write()`/`writev()` call** so the problem never arises. `TCP_QUICKACK` exists on Linux but isn't sticky, so it's fiddly.

This is worth carrying as a general lesson beyond TCP: **two locally-sensible optimisations, composed, can produce a pathology neither would cause alone.** Buffering-plus-batching interactions cause the same class of bug in message queues and event loops.

## Key insight
<!-- bite: 061dc37b-9fe9-4bb6-bf3f-bbdcae6a4325 -->

TCP's reliability is built from exactly two primitives — **number everything, and acknowledge a contiguous prefix** — and every other mechanism (SACK, fast retransmit, RACK, the persist timer, Nagle) is a patch on a specific way that minimal design underperforms. The one thing none of them can patch is **head-of-line blocking**, because that isn't an implementation flaw — it's the definition of the abstraction TCP promises. To escape it you can't fix TCP; you have to stop asking for a single ordered byte stream.

## Check your understanding
<!-- bite: 5903217c-8e1f-41e2-8608-fc52e94888e9 -->

Try each one before you open the answer.

1. <!-- q: gap id="6b9b606a" answers="receiver;network" -->
   Flow control stops the sender overwhelming the ___, using the receive window. Congestion control stops it overwhelming the ___, using the congestion window.

   <details><summary>Answer</summary>

   The receiver, then the network. Both cap how much can be in flight; otherwise they have nothing to do with each other.

   </details>

2. <!-- q: exact id="0708c1ad" answer="2000" -->
   A sender sends three segments: bytes 1000–1999, 2000–2999 and 3000–3999. The middle one is lost; the other two arrive. What cumulative ACK number does the receiver keep sending?

   <details><summary>Answer</summary>

   2000: "I have everything up to 1999, and I want 2000 next". It holds 3000–3999 but can't acknowledge it with a cumulative ACK, or hand it to the application, until the gap is filled. SACK can tell the sender about the held block.

   </details>

3. <!-- q: exact id="a50088fa" answer="3" -->
   How many duplicate ACKs trigger a classic fast retransmit, without waiting for the timer?

   <details><summary>Answer</summary>

   3. They show a gap exists while traffic is still flowing, which turns a stall of a second or more into about one round trip.

   </details>

4. <!-- q: exact id="feb32948" answer="327680" accept="327,680|320 KB|320KB" -->
   Without window scaling, the receive window is at most 64 KB (65,536 bytes). On a path with a 200 ms round trip, what is the most a connection can carry, in bytes per second?

   <details><summary>Answer</summary>

   327,680 bytes/s, about 320 KB/s. Throughput is at most window / RTT = 65,536 / 0.2. A link of any speed is capped there, which is why the window scale option matters on long paths.

   </details>

5. <!-- q: open id="90e4f2e0" -->
   An RPC client writes the request header and the body in two separate small `write()` calls, and every request takes an extra ~40 ms. Explain the cause and give two fixes.

   <details><summary>Answer</summary>

   Nagle's algorithm holds back the second small write because the first is still unacknowledged. The server can't answer an incomplete request, so its delayed-ACK timer holds the ACK, hoping to piggyback it. Both wait until the timer fires after about 40 ms. Fixes: set `TCP_NODELAY` to turn Nagle off, or send the whole message in one `write()` or `writev()`.

   </details>

6. <!-- q: mcq id="1dd3e759" -->
   Why can't SACK, fast retransmit or any other TCP improvement fix head-of-line blocking?

   - [ ] They are not supported by enough servers yet
   - [x] TCP promises one ordered byte stream, so later bytes can't be delivered before a missing earlier byte arrives
   - [ ] Head-of-line blocking is caused by routers, not TCP
   - [ ] They only work on IPv6

   <details><summary>Answer</summary>

   It's built into what TCP promises. SACK makes the sender retransmit smarter, but the receiver still has to deliver bytes in order. To escape it you have to stop asking for one ordered stream, which is what QUIC does with independent streams.

   </details>

## Related
<!-- bite: f795313b-c605-4ad0-8b31-7ad8bd31e301 -->
- [[build-your-own-shit/19-your-own-tcp-ip-stack|Your Own TCP/IP Stack]] — retransmission timers, the receive window and the congestion sawtooth, built and then tested under `tc netem` packet loss
- [[networking/08-congestion-control|Congestion Control]] — the other window, and the harder problem
- [[networking/13-quic-and-modern-transport|QUIC]] — what you get when you drop the single-stream abstraction
- [[networking/15-network-performance|Network Performance]] — bandwidth-delay product, why windows govern throughput
- [[networking/16-debugging-networks|Debugging Networks]] — spotting retransmissions and zero windows in `ss -i` / tcpdump

## About this lesson
<!-- bite: 84b2a3dc-1a92-4401-865c-13817512fdee -->

**Level:** Intermediate→Advanced. **Covers:** how a protocol builds a perfectly ordered, lossless byte stream on top of a medium that loses, duplicates, and reorders. Two separate problems live here, and keeping them apart is most of the battle:
