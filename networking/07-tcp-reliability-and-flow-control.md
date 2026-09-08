# TCP Reliability & Flow Control

**[Intermediate→Advanced]** — how a protocol builds a perfectly ordered, lossless byte stream on top of a medium that loses, duplicates, and reorders. Two separate problems live here, and keeping them apart is most of the battle:

- **Flow control** — don't overwhelm the **receiver**. Solved by the receive window.
- **Congestion control** — don't overwhelm the **network**. Solved by the congestion window. → [[foundations/networking/08-congestion-control|next note]]

Both limit how much you can send. They have nothing else to do with each other, and confusing them makes TCP performance impossible to reason about.

## The kid version first

You're reading a long book aloud to a friend over those unreliable postcards. To make sure they get every word in the right order:

1. **Number every word.** Now they can tell if word 57 is missing, and can put words back in order if 58 arrives before 57.
2. **Have them say "I've got everything through word 56."** That's an acknowledgement.
3. **If nobody confirms word 57 after a while, say it again.** That's retransmission.
4. **Don't wait for confirmation after every word** — you'd take forever. Send a batch, wait for confirmations, send more. That's the sliding window.
5. **Let them say "slow down, my notebook is full."** That's flow control.

Every mechanism below is a refinement of one of those five.

## Sequence numbers and cumulative ACKs

TCP numbers **bytes**, not packets. The header carries a sequence number (the position of this segment's first byte in the stream) and an acknowledgement number.

The ACK is **cumulative**, and it means something precise that people misread: `ack=1000` means *"I have received every byte up to 999, and 1000 is the next one I want."* It is a statement about a contiguous prefix, not about the last packet received.

That definition has a sharp consequence. If you send bytes 1000–1999, 2000–2999, 3000–3999 and the middle one is lost, the receiver **cannot** say "I got the first and third." It can only keep saying `ack=2000`. The receiver holds 3000–3999 in its buffer but cannot deliver it to the application — bytes must be delivered in order.

That is **head-of-line blocking**, and it's not a bug; it's the direct price of the in-order byte-stream abstraction. If your connection is carrying twenty independent HTTP requests ([[foundations/networking/11-http-evolution|HTTP/2]]), one lost packet stalls all twenty. This single fact is why [[foundations/networking/13-quic-and-modern-transport|QUIC]] exists.

**SACK** (Selective Acknowledgement, RFC 2018) patches the diagnostic half of the problem: an option that says "additionally, I have 3000–3999." The sender then retransmits only the true gap instead of everything after it. Universally supported and a large real-world win — but note it fixes *sender efficiency*, not head-of-line blocking. The receiver still can't deliver out of order.

## Detecting loss: timeout vs. duplicate ACKs

Two mechanisms, and the difference in their cost is enormous.

**Retransmission timeout (RTO)** — the slow path. The sender estimates the round-trip time continuously (a smoothed average plus a variance term, Jacobson's algorithm) and sets `RTO ≈ SRTT + 4×RTTVAR`. If no ACK arrives in time, retransmit and **double the RTO** (exponential backoff). The initial RTO is 1 second, so a lost packet at connection start costs a *full second* — catastrophic for a page load, and one of the reasons early-connection loss hurts so much more than steady-state loss.

**Fast retransmit** — the fast path. Every out-of-order segment makes the receiver re-send its current cumulative ACK. Three **duplicate ACKs** tell the sender "a gap exists and traffic is still flowing" — enough evidence to retransmit immediately, without waiting for the timer. This turns a 1-second stall into roughly one RTT, and it's why TCP handles isolated loss gracefully but handles *tail* loss (the last packets of a response, with nothing after them to trigger duplicate ACKs) badly. **Tail Loss Probe** was added specifically for that case.

**RACK-TLP** (RFC 8985) is the modern replacement, now default on Linux: infer loss from *time* rather than counting duplicate ACKs — if a segment was sent more than an RTT before something that's already been ACKed, it's probably lost. Handles reordering far better than "three dupACKs," which misfires whenever the network mildly reorders packets.

**Karn's algorithm** is a subtle one worth knowing: never use a *retransmitted* segment's ACK to update the RTT estimate. You can't tell whether the ACK was for the original or the retransmission, so including it corrupts the estimate in exactly the situation where you need it most.

## Flow control: the receive window

Every ACK carries a **window** field: "I have this many bytes of free buffer." The sender may never have more than that many unacknowledged bytes in flight. Simple, and it completely prevents a fast sender from drowning a slow receiver.

Three details that matter in practice:

- **Window scaling.** The field is 16 bits — max 64 KB. On a 100ms path that caps you at 640 KB/s no matter how fat the pipe, which is why the **window scale option** (RFC 7323, negotiated in the handshake, shifting the window up to 1 GB) is essential on any long-distance link. If a middlebox strips the option, you get a connection that works but is mysteriously slow — a classic "it's fast in the office, slow from the other continent" bug.
- **Zero window and the persist timer.** A receiver whose buffer is full advertises `window=0`. The sender stops. But the "I have room again" update is itself an ACK, and if *that* is lost, both sides wait forever. So the sender runs a **persist timer** and periodically pokes with a 1-byte probe. Deadlock avoidance built into the protocol.
- **Silly window syndrome.** A receiver draining one byte at a time would advertise a 1-byte window, and the sender would send 41-byte packets to carry 1 byte of data. Fixed on both sides: the receiver doesn't advertise tiny windows (waits until a decent chunk is free), and the sender doesn't send tiny segments (Nagle's algorithm, below).

**Autotuning:** modern kernels size receive buffers dynamically (`net.ipv4.tcp_rmem`). Manually pinning `SO_RCVBUF` disables autotuning and is usually a performance *regression*, not a win — a common cargo-cult mistake.

## Nagle's algorithm and delayed ACKs — the famous bad interaction

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

TCP's reliability is built from exactly two primitives — **number everything, and acknowledge a contiguous prefix** — and every other mechanism (SACK, fast retransmit, RACK, the persist timer, Nagle) is a patch on a specific way that minimal design underperforms. The one thing none of them can patch is **head-of-line blocking**, because that isn't an implementation flaw — it's the definition of the abstraction TCP promises. To escape it you can't fix TCP; you have to stop asking for a single ordered byte stream.

## Related
- [[foundations/networking/08-congestion-control|Congestion Control]] — the other window, and the harder problem
- [[foundations/networking/13-quic-and-modern-transport|QUIC]] — what you get when you drop the single-stream abstraction
- [[foundations/networking/15-network-performance|Network Performance]] — bandwidth-delay product, why windows govern throughput
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — spotting retransmissions and zero windows in `ss -i` / tcpdump
