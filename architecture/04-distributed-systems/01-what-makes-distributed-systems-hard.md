# What Makes Distributed Systems Hard

**[reference]** — from the canon (Kleppmann's *Designing Data-Intensive Applications*, MIT 6.824). Why a system spread across machines is *categorically* harder than one machine — the foundation for everything else in this section. You feel this fully only when you build one (a [[architecture/05-case-studies/README|Raft KV store]]).

## The definition

A **distributed system** is a set of independent computers that appear to users as one coherent system, coordinating over a network to achieve a shared goal. We build them for **scale** (beyond one machine), **availability** (survive failures), and **latency** (be near users) — but each of those benefits is bought with a fundamental increase in difficulty.

## The three fundamental hardships

Everything hard about distributed systems traces to three facts a single machine doesn't have to worry about:

### 1. Partial failure

On one machine, things work or the machine is down — binary. In a distributed system, *some* parts fail while others keep running, and — worse — **you often can't tell the difference between a node that's slow, a node that's dead, and a network that dropped your message.** A request with no response could mean: the node never got it, the node did the work but the reply was lost, or the node is just slow. You cannot distinguish these from the outside. This ambiguity is the root of most distributed-systems complexity — you must design for "I don't know what happened" as a normal case.

### 2. Unreliable networks

The network between nodes can drop, delay, duplicate, or reorder messages, and can partition (split the system so groups can't talk). Messages take *variable, unbounded* time. You cannot assume a message arrives, arrives once, arrives in order, or arrives promptly. Timeouts are your only tool to *guess* failure — and any timeout is a tradeoff (too short → false positives declaring live nodes dead; too long → slow failure detection).

### 3. No global clock

There is no single "now" across machines. Each has its own clock, and they drift; even synchronized (NTP), they disagree by milliseconds — an eternity at network speed. So you **cannot rely on timestamps to order events across nodes** ("this happened before that"). Determining ordering and causality without a shared clock is a deep problem with its own note ([[architecture/04-distributed-systems/02-time-and-ordering|time & ordering]]).

## The fallacies of distributed computing

The classic list of false assumptions engineers make (and pay for) — worth internalizing as things that are **NOT** true:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology doesn't change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

Every one of these is false, and assuming any of them is true is a bug waiting to happen. Robust distributed systems are built by assuming the opposite of all eight.

## FLP and the theoretical limits

Two results that bound what's *possible* (not just hard):

- **FLP impossibility** — in an asynchronous network where even one node can fail, it's impossible to guarantee [[architecture/04-distributed-systems/04-consensus|consensus]] will *always* terminate. Real systems get around this with timeouts/randomization (accepting "usually terminates, very fast" instead of "always") — which is why [[architecture/04-distributed-systems/04-consensus|Raft/Paxos]] work in practice despite FLP.
- **CAP** — during a partition, you choose consistency or availability ([[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP]]). A direct consequence of unreliable networks.

## Why this matters before the algorithms

Every technique in this section — [[architecture/04-distributed-systems/02-time-and-ordering|logical clocks]], [[architecture/04-distributed-systems/03-replication-and-consistency|replication/consistency]], [[architecture/04-distributed-systems/04-consensus|consensus]], [[architecture/04-distributed-systems/05-distributed-transactions|distributed transactions]], [[architecture/04-distributed-systems/06-partitioning-and-fault-tolerance|failure detection]] — exists to cope with these three hardships. Understanding *why* they're needed (you can't tell dead from slow; there's no global order; the network lies) makes the algorithms make sense instead of feeling arbitrary. This is also why the [[languages/01-java/02-jvm-and-concurrency/02-concurrency|single-machine concurrency]] problems (shared state, ordering, visibility) are the *easy* version — at least there you have shared memory and a single clock.

## Related
- [[architecture/04-distributed-systems/02-time-and-ordering|Time & Ordering]] — coping with no global clock
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the availability/consistency consequence
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — the single-machine (easier) version of coordination
