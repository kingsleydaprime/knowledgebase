# Modern Distributed Transactions

**[reference]** · **⏳ outline — deep note in progress** (part of the distributed-systems deep-curriculum build).

[[architecture/04-distributed-systems/10-distributed-transactions|Distributed transactions]] covers the classics (2PC/3PC, sagas, isolation). This note is how *modern* systems get **serializable, cross-shard transactions at scale** — the thing "NewSQL" made possible after a decade of "NoSQL means giving up transactions."

## Will cover
- **Google Spanner** — 2PC layered over **[[architecture/04-distributed-systems/07-consensus-and-paxos|Paxos]] groups** (each shard is a Paxos-replicated state machine), with **[[architecture/04-distributed-systems/03-time-and-ordering|TrueTime]]** providing globally-ordered commit timestamps and **commit-wait** delivering external consistency (linearizable global transactions). The system that proved global ACID at scale is achievable.
- **Percolator** (Google) — **snapshot-isolation** transactions layered on BigTable using a client-driven 2PC with a primary lock; how large-scale incremental processing got transactions without a central coordinator.
- **Calvin / deterministic databases** — flip the model: **agree on the order of transactions first** (via consensus), then execute deterministically on every replica so no cross-node commit protocol is needed. Trades flexibility for eliminating 2PC.
- **CockroachDB / YugabyteDB** — the open-source Spanner lineage: [[architecture/04-distributed-systems/03-time-and-ordering|HLC]] instead of TrueTime, serializable isolation over Raft ranges.
- **Sagas at scale** revisited — when you *can't* have distributed ACID (across service boundaries, [[architecture/03-architectural-patterns/04-microservices-patterns|microservices]]) and fall back to compensating transactions + [[architecture/04-distributed-systems/10-distributed-transactions|idempotency]].
- **The through-line** — the [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]] cost is still paid (commit-wait latency, coordination), just paid deliberately and bounded.

## Related
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] · [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering (TrueTime/HLC)]] · [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] · [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]]
