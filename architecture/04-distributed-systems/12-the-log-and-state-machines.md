# The Log & State Machines

**[reference]** · **⏳ outline — deep note in progress** (part of the distributed-systems deep-curriculum build).

One idea unifies half of distributed systems: **the append-only, totally-ordered log.** Replication, consensus, streaming, databases, and event-driven architecture are all the same trick wearing different clothes — agree on an ordered sequence of events, and everything downstream that replays it deterministically ends up in the same state.

## Will cover
- **The Replicated State Machine (RSM) model** — if every replica starts in the same state and applies the *same commands in the same order*, they stay identical. This is the abstraction [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] actually provides: agreement on a **log**, not on a single value. Determinism is the hidden requirement.
- **The log as the core abstraction** (Jay Kreps' "The Log") — why an ordered log is the right primitive for integrating systems, and how it decouples producers from consumers.
- **Apache Kafka** — a distributed, partitioned, replicated log as infrastructure: partitions for scale, offsets for [[architecture/04-distributed-systems/03-time-and-ordering|ordering]] within a partition, consumer groups, and the log-compaction/retention model.
- **LSM-trees** — how storage engines (RocksDB, Cassandra, LevelDB) turn a write-ahead *log* + in-memory memtable + background compaction into fast writes; the log underneath your database.
- **Change Data Capture (CDC)** — treating a database's replication log as an event stream (Debezium); the bridge between "database" and "event stream."
- **Event sourcing** — storing the log of events *as the source of truth* and deriving state by replay; the app-architecture face of the same idea.
- **Exactly-once, honestly** — you can't get exactly-once *delivery* ([[architecture/04-distributed-systems/02-theoretical-limits|Two Generals]]), but idempotent consumers + ordered offsets give exactly-once *effect*.

## Related
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] · [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] · [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] · [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] · [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]]
