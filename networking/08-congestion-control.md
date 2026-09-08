# Congestion Control

**[Advanced]** — the most intellectually interesting thing in networking, and the least understood. It's a **distributed resource-allocation algorithm with no coordinator**: millions of independent senders, no communication between them, no central authority, sharing a resource none of them can measure — and it works well enough that the internet has not collapsed since 1986.

## The kid version first

A hundred cars all want to use one bridge. Nobody is directing traffic. There is no radio between drivers. If everyone drives on at once, the bridge jams and *nobody* crosses — worse than if they'd taken turns.

So each driver follows a private rule: **"speed up slowly while things are moving; slow down hard the moment I see trouble."** Nobody agreed to this rule. Nobody enforces it. But if enough drivers follow it, the bridge stays flowing and everyone gets roughly a fair share.

The remarkable part isn't the rule — it's that **"increase gently, decrease sharply" is the only shape of rule that converges to fairness.** That's a theorem, not a heuristic, and it's the reason TCP looks the way it does.

## The problem: congestion collapse

In October 1986, the link between LBL and UC Berkeley — 400 yards apart — dropped from 32 kbps to **40 bps**. A thousandfold collapse.

The mechanism is a feedback loop that eats itself: the network gets loaded → queues fill → packets are dropped → senders time out and retransmit → **more** traffic enters an already-overloaded network → more drops. The network is now saturated with retransmissions of packets that will also be dropped. Throughput approaches zero while utilisation approaches 100%.

Van Jacobson's response (1988) is the algorithm every TCP still descends from. The core insight, which was not obvious at the time: **packet loss is a signal.** The network can't tell you it's congested — there's no message for that — but a dropped packet *is* the message, because on a wired link, loss is overwhelmingly caused by a full queue rather than corruption.

## The congestion window

The sender keeps a second limit alongside the [[foundations/networking/07-tcp-reliability-and-flow-control|receive window]]:

```
bytes in flight ≤ min(receive window, congestion window)
                       └─ receiver's limit    └─ sender's guess about the network
```

`cwnd` is never told to the sender by anyone. It is a **continuously-updated guess**, revised by feedback. The whole field is about how to make that guess well.

### Slow start — find the ceiling fast

Start at ~10 segments (`IW10`) and **double `cwnd` every RTT**. Despite the name it's exponential and aggressive — "slow" only relative to the pre-1988 behaviour of blasting a full window immediately.

Doubling continues until loss occurs or `cwnd` crosses `ssthresh`, then it switches to congestion avoidance.

The practical consequence is one of the most useful facts in web performance: **a new connection cannot use the available bandwidth immediately.** Reaching 10 Mbps on a 100ms RTT path takes several round trips of doubling. Short HTTP responses *never leave slow start* — they finish before TCP has figured out how fast it could have gone. So for most web traffic, **the bottleneck isn't bandwidth, it's the number of round trips.** That's why connection reuse, HTTP/2 multiplexing, and QUIC's 0-RTT matter so much more than a faster link.

### Congestion avoidance — AIMD

Past `ssthresh`, switch to **AIMD**: **A**dditive **I**ncrease, **M**ultiplicative **D**ecrease.

- No loss for an RTT → `cwnd += 1 segment` (linear, cautious)
- Loss detected → `cwnd = cwnd / 2` (halve it, immediately)

Plotted, this gives TCP's characteristic **sawtooth**: slow climb, sharp drop, repeat. It looks wasteful — the sender is deliberately probing until it causes a drop — and it is. But Chiu & Jain proved (1989) that among linear control rules, **only** additive-increase/multiplicative-decrease converges to a fair *and* efficient allocation from arbitrary starting points. Additive decrease doesn't converge to fairness; multiplicative increase doesn't converge to stability. The shape is forced.

**Fast recovery** (Reno) softens the drop: on a fast-retransmit (3 dupACKs), halve `cwnd` and continue from there rather than collapsing to 1 and re-entering slow start. That's the difference between "the network dropped one packet" and "the network went away" — a timeout means the latter, and *does* reset to slow start.

## The modern algorithms

**CUBIC** (Linux default since 2.6.19, and Windows since 2019) fixes Reno's problem on high-bandwidth long-distance links, where additive increase takes absurdly long to refill a large window. It grows `cwnd` as a **cubic function of time since the last loss** — fast when far from the previous ceiling, cautious near it, then aggressive again if the ceiling seems to have moved. It's also *RTT-independent*, which fixes a real unfairness in Reno where short-RTT flows grow their windows faster and starve long-RTT ones.

**BBR** (Google, 2016) rejects the premise. Loss-based control has two flaws that got worse over time:

- **It only reacts after the queue is already full.** By design it *fills* buffers before backing off, adding queueing delay.
- On wireless and long-haul links, **loss isn't only congestion**, so loss-based algorithms back off for no reason.

BBR instead models the path directly: continuously estimate the **bottleneck bandwidth** and the **minimum RTT**, and send at exactly `BtlBw × RTprop` — the bandwidth-delay product, the amount in flight that keeps the pipe full *without* building a queue. It periodically probes higher to detect more bandwidth, and lower to re-measure the true minimum RTT.

This targets the right operating point in theory (Kleinrock's optimum). In practice BBRv1 could be unfair to CUBIC flows and had issues with shallow buffers; BBRv2/v3 incorporate loss and ECN signals to fix that. Worth knowing because **it's what YouTube and much of Google's traffic uses**, and it's a switchable sysctl on Linux (`net.ipv4.tcp_congestion_control=bbr`) that measurably helps on lossy or long-distance paths — one of the highest-leverage single-line server tunings available.

## Bufferbloat — the pathology everyone has felt

Memory got cheap, so router and modem vendors added enormous buffers, reasoning that a buffered packet beats a dropped one. This was a mistake.

Loss-based congestion control **needs** loss as its signal. Give it a huge buffer and it fills the entire thing before noticing anything is wrong. Now every packet queues behind seconds' worth of data. Throughput is fine; **latency is destroyed**.

This is exactly the "someone started a big upload and now video calls stutter and web pages take five seconds to start" experience. The buffer that was supposed to help is holding your latency-sensitive packets behind a bulk transfer.

The fixes are all about managing the queue rather than the sender: **AQM** (Active Queue Management) — **CoDel** drops packets based on how long they've been *queued* rather than how full the queue is, and **fq_codel** additionally gives each flow its own queue so a bulk transfer can't monopolise the buffer. Enabling `fq_codel` (or `cake` on a home router) is a genuinely transformative one-line change.

**ECN** (Explicit Congestion Notification) is the cleaner answer: routers *mark* packets instead of dropping them, and the receiver echoes the mark back. Congestion signalled without loss and without delay. Adoption has been slow for a very instructive reason — some middleboxes historically dropped packets with ECN bits set, so enabling it broke connectivity for a minority of users, and nobody would ship a feature that breaks 1% of traffic. That's [[foundations/networking/14-nat-firewalls-and-middleboxes|protocol ossification]] in one sentence.

## Incast — the data-centre failure mode

Worth knowing because it bites in [[architecture/README|distributed systems]] specifically. A client fans out a request to 40 servers ([[architecture/02-building-blocks/README|scatter-gather]]); all 40 reply at once. Their responses collide at the top-of-rack switch, its shallow buffer overflows, and packets are lost — often the *last* packets of a response, with nothing after them to trigger fast retransmit. So you wait for an **RTO: 200ms+ in a data centre where RTTs are microseconds.**

The result is a latency distribution that's mostly sub-millisecond with a p99 in the hundreds of milliseconds — the classic "tail latency" signature. Mitigations: smaller RTO minimums, ECN/DCTCP, staggering the fan-out, and application-level hedging. It's a good example of why p99 latency in distributed systems so often has a *transport-layer* explanation that never shows up in application profiling.

## Key insight

Congestion control is a **distributed algorithm running on machines that never communicate, allocating a resource none of them can observe, with no enforcement mechanism.** It works because the rule's *shape* — gentle increase, sharp decrease — provably converges to fairness, and because nearly everyone voluntarily runs it. The internet's stability rests on cooperation that is technically optional. That's also why writing a [[foundations/networking/05-udp-and-ports|UDP]] application without congestion control isn't just risky engineering — it's defection from the agreement that keeps the whole thing standing.

## Related
- [[foundations/networking/07-tcp-reliability-and-flow-control|TCP Reliability & Flow Control]] — the other window
- [[foundations/networking/15-network-performance|Network Performance]] — BDP, and why round trips dominate
- [[foundations/networking/13-quic-and-modern-transport|QUIC]] — congestion control moved to userspace, where it can be iterated on
- [[architecture/04-distributed-systems/README|Distributed Systems]] — incast, tail latency, and scatter-gather
- [[engineering/02-control-theory/README|Control Theory]] — AIMD is a feedback controller with a delayed, noisy plant. The maths that explains why it oscillates, and why the delay is the hard part
