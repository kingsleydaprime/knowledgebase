# What Makes Distributed Systems Hard

**[reference]** — from the canon (Kleppmann's *Designing Data-Intensive Applications* ch. 8, MIT 6.824, Lamport). Why a system spread across machines is *categorically* harder than one machine — the foundation for everything else in this course. You feel this fully only when you build one (a [[architecture/05-case-studies/README|Raft KV store]]). This note establishes the **models** (failure, timing, clocks) that every later algorithm is defined against; the **impossibility results** those models produce (FLP, CAP) get their own treatment in [[architecture/04-distributed-systems/02-theoretical-limits|theoretical limits]].

## The kid version first

Doing your homework **alone**, you always know if it's finished — it's on your desk. Now imagine a **group project** where your teammates are in *different houses* and you can only text each other. Three annoying things happen that never happened when you worked alone:
1. A text you send might **not arrive** — and you can't tell if your friend got it and is working, or never saw it.
2. A friend might **fall asleep** in the middle of their part, and from the outside "thinking really hard" looks *exactly* the same as "asleep" — you just get silence either way.
3. Everyone's **clock is a little different**, so "I finished first!" arguments can't be settled by looking at watches.

That's it — that's the whole subject. A distributed system is a group project where you **can't see your teammates, can't tell slow from gone, and have no shared clock.** Every clever algorithm later is a trick for getting the project done anyway.

## The definition

A **distributed system** is a set of independent computers that appear to users as one coherent system, coordinating over a network to achieve a shared goal. We build them for **scale** (beyond one machine), **availability** (survive failures), and **latency** (be near users). Each benefit is bought with a fundamental increase in difficulty — and the difficulty isn't incidental (bad libraries, slow networks) but *essential*: it follows from three facts a single machine never faces.

## The root cause: partial failure

On one machine, computation is **deterministic and total** — an operation succeeds, or the whole machine is down, and you know which. A distributed system introduces **partial failure**: some components fail while others keep running, *and the working components often cannot tell what happened to the failed ones.*

The canonical case: you send a request and get no response. That could mean —
- the request never arrived (network dropped it on the way there),
- the request arrived, the node did the work, but the *reply* was lost (network dropped it on the way back — the work happened, you just don't know),
- the node received it and is still working (slow, not dead),
- the node crashed before, during, or after doing the work.

**From the outside, these are indistinguishable.** No amount of cleverness lets a node determine, with certainty, the state of another node it can't reach. This single fact — *you must act correctly without knowing what happened* — is the source of nearly all distributed-systems complexity. Every algorithm later in this course is, at bottom, a strategy for making progress despite this ambiguity.

## Model 1 — the failure model (how nodes fail)

To reason precisely, you fix *what kinds of failures* you'll tolerate. From weakest to strongest assumption about node behavior:

| Model | A failed node… | Handled by |
|---|---|---|
| **Fail-stop** | crashes and *announces it* (or is reliably detectable) | the easy, mostly-theoretical case |
| **Crash-stop (fail-silent)** | crashes and simply stops, silently, forever | classic consensus ([[architecture/04-distributed-systems/07-consensus-and-paxos\|Paxos]]/[[architecture/04-distributed-systems/08-raft-in-depth\|Raft]]) |
| **Crash-recovery** | crashes, then *comes back* — possibly with stale state, possibly having lost in-flight memory | real systems; needs stable storage + recovery logic |
| **Omission** | drops some messages (send/receive omission) but keeps running | flaky-network modeling |
| **Byzantine** | behaves *arbitrarily* — sends conflicting or malicious messages, lies | [[architecture/04-distributed-systems/09-coordination-services\|BFT]], blockchains, adversarial settings |

Most internal infrastructure assumes **crash-recovery with fair-loss networks**: nodes fail by crashing (not lying), may restart, and the network may drop messages but not forge them. Byzantine tolerance costs far more (you need `3f+1` nodes to tolerate `f` liars, vs `2f+1` for crashes) and is reserved for trustless environments. *Knowing which model you're in tells you which algorithm you're allowed to use.*

## Model 2 — the timing model (how fast is "the network")

The second axis is how much you can assume about *time bounds* on message delivery and computation:

- **Synchronous** — known upper bounds on message delay and processing speed. Wonderfully easy (a timeout *proves* a node is dead), and **unrealistic** — no real WAN gives you a hard bound.
- **Asynchronous** — *no* timing assumptions at all: messages take arbitrary, unbounded time, clocks are meaningless. The most honest model of a real network, and the harshest: it's the setting in which [[architecture/04-distributed-systems/02-theoretical-limits|FLP]] proves consensus can't be guaranteed to terminate.
- **Partially synchronous** — the pragmatic middle, and the model real systems target: the network is *asynchronous most of the time* but is *eventually* synchronous (bounds hold during "good" periods). This is exactly why Raft/Paxos use **timeouts**: they can't guarantee progress during a bad period, but they guarantee *safety always* and *progress once the network settles*.

The whole design art is: **be correct (safe) under full asynchrony; make progress (live) under eventual synchrony.**

## Model 3 — clocks, and why you can't trust them

There is no single "now" across machines, and the clocks you *do* have are treacherous. Two kinds, for two different jobs — confusing them is a classic bug:

- **Time-of-day (wall-clock)** — "what time is it," synced via NTP. It can **jump backwards** (NTP correction, leap seconds), drift, and disagree between nodes by milliseconds-to-seconds. **Never use it to measure durations or to order events** — a backward jump makes `end - start` negative.
- **Monotonic clock** — "how much time has elapsed," only ever moves forward, no absolute meaning. This is what you use for timeouts and elapsed-time measurement. But monotonic readings from *different* nodes are incomparable.

Even perfectly synced, NTP gets you to *maybe* ~milliseconds of accuracy — an eternity when a network round-trip is sub-millisecond. So **timestamps cannot order events across nodes** ("A's timestamp < B's timestamp" does *not* mean A happened first). Google's Spanner is the famous exception: it spends real money (GPS + atomic clocks) to bound clock uncertainty and *waits out* the error interval — see [[architecture/04-distributed-systems/03-time-and-ordering|time & ordering]] (TrueTime) and [[architecture/04-distributed-systems/11-modern-distributed-transactions|modern transactions]]. Everyone else uses **logical clocks** instead.

### The pause problem (why "slow" is unbounded even locally)
It's not just the network. A process can **pause for seconds with no warning** and no way to notice from inside: a stop-the-world **garbage-collection pause**, the OS de-scheduling the thread, a **VM being live-migrated or suspended**, disk I/O stalls, laptop-lid swap. To the rest of the cluster, a node in a 10-second GC pause is *identical to a dead node* — and when it resumes, it believes no time has passed and may act on now-stale assumptions (e.g. "I'm still the leader"). This is why leader-based systems need **fencing tokens** ([[architecture/04-distributed-systems/09-coordination-services|coordination]]): a monotonically increasing number that lets a resource *reject* a write from a paused-then-resumed old leader.

## Why perfect failure detection is impossible

Follows directly from Models 2 and 3: in an asynchronous (or partially-synchronous) network, **you cannot build a failure detector that is both accurate and complete.** A *timeout* is your only tool to guess "dead," and every timeout is a tradeoff:
- **too short** → you declare live-but-slow nodes dead (false positives → needless failovers, split-brain risk),
- **too long** → you're slow to react to real failures (availability hit).

There is no correct value; there is only a tradeoff you tune. Sophisticated systems use **adaptive/phi-accrual detectors** (output a *suspicion level*, not a boolean) — see [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure detection]]. The deep point: **failure is not a fact you observe, it's a decision you make** — and the whole cluster must agree on that decision, which is itself a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] problem.

## Safety and liveness (the vocabulary for "correct")

Every distributed algorithm is judged on two kinds of property, and the distinction is load-bearing:
- **Safety** — "nothing bad ever happens" (two nodes never both believe they're leader; a committed value is never lost). Safety violations are *irrecoverable* — the bad thing already happened. Good algorithms hold safety **unconditionally**, even under full asynchrony and arbitrary message loss.
- **Liveness** — "something good eventually happens" (a request eventually gets a response; the cluster eventually elects a leader). Liveness is usually only guaranteed **under conditions** (eventual synchrony, a majority alive). FLP is precisely a statement that a certain liveness property can't be guaranteed unconditionally.

The design mantra falls out of this: **never sacrifice safety; sacrifice liveness (temporarily) when you must.** A system that stops making progress during a bad partition is annoying; one that corrupts data is broken.

## The fallacies of distributed computing

The classic list of false assumptions engineers make and pay for — the informal version of everything above. Every one is **false**; robust systems assume the opposite of all eight:

1. The network is reliable.  2. Latency is zero.  3. Bandwidth is infinite.  4. The network is secure.  5. Topology doesn't change.  6. There is one administrator.  7. Transport cost is zero.  8. The network is homogeneous.

## Why this matters before the algorithms

Every technique in this course — [[architecture/04-distributed-systems/03-time-and-ordering|logical clocks]], [[architecture/04-distributed-systems/04-consistency-models|consistency models]], [[architecture/04-distributed-systems/05-replication|replication]], [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]], [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]] — exists to cope with these models: you can't tell dead from slow, there's no global order, the network and even your own process can stall unboundedly. Fix the *model* (which failures, which timing) and the right algorithm follows; ignore the model and the algorithms feel arbitrary. This is also why [[languages/01-java/02-jvm-and-concurrency/02-concurrency|single-machine concurrency]] is the *easy* cousin — there you still have shared memory and one clock; here you have neither.

## Key insight

**Distributed systems are hard because of partial failure — you must stay correct without knowing the state of the things you can't reach — and everything else is machinery for that.** Pin down the *failure model* (crash vs Byzantine) and the *timing model* (asynchronous vs partially synchronous), distrust every clock (wall vs monotonic; pauses are unbounded), accept that failure detection is a tuned guess not a fact, and hold **safety unconditionally while trading away liveness** when the network misbehaves.

## Related
- [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — FLP, CAP/PACELC: what these models make *impossible*
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — coping with no global clock via logical clocks
- [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection]] — turning the timeout tradeoff into phi-accrual suspicion
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals-level view
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — the single-machine (easier) version of coordination
