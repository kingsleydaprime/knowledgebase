# The Log & State Machines

**[reference]** — from the canon (Jay Kreps' *The Log*, the Raft/VR papers, DDIA ch. 3 & 11). One idea quietly unifies half of distributed systems: the **append-only, totally-ordered log.** Replication, consensus, streaming, databases, and event-driven architecture turn out to be the *same trick* in different costumes — agree on an ordered sequence of events, and anything that replays it deterministically ends up in the same state.

## The kid version first

Imagine a **recipe written as a numbered list of steps** that you only ever *add to the end* of — never erase, never insert in the middle. Now give the exact same numbered recipe to five friends in five kitchens. If every friend **starts from the same empty bowl and follows the same steps in the same order**, they all bake the **identical cake** — even though they never talked to each other while baking. No need to compare cakes; sameness is *guaranteed* by "same start + same steps + same order."

That numbered, add-only list is **the log**, and "same start + same ordered steps → same result" is the **replicated state machine**. Almost everything else in distributed systems is either *how to agree on that list* ([[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]) or *what to do with it* (databases, streams, event apps). Once you see the log everywhere, the field gets a lot smaller.

## The Replicated State Machine (RSM) — the core model

A **state machine** is anything that takes commands and updates state (a key-value store, a bank ledger, a counter). The RSM insight:

> If every replica **starts in the same state** and **applies the same commands in the same order**, they end in the **same state** — forever.

So keeping N machines identical reduces to **one problem: agree on the ordered log of commands.** That's *exactly* what [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] provides — Raft/Paxos don't agree on a single value, they agree on a **log**, precisely so it can drive an RSM. There's one hidden requirement people miss: **the commands must be deterministic.** A command like "set `x = current_time()` " or "shuffle randomly" breaks the RSM — replicas diverge because "the same step" produces different results. Determinism is the price of the whole trick (and why [[architecture/04-distributed-systems/11-modern-distributed-transactions|Calvin]] insists on it).

## The log as *the* integration abstraction

Jay Kreps' argument ("The Log"): an ordered, replayable log is the right primitive for connecting *systems*, not just replicating one. Producers append; any number of consumers read at their own pace, each tracking its own position (**offset**). This **decouples** everyone — a new consumer can join later and replay from the beginning; a slow consumer doesn't block a fast one; the log is the single source of truth everyone derives their view from. "Turn your data pipeline into a log everyone subscribes to" reorganizes a messy web of point-to-point integrations into a clean hub.

## Where the log shows up (same idea, different costume)

- **Apache Kafka** — the log *as infrastructure*: a distributed, [[architecture/04-distributed-systems/13-partitioning|partitioned]], [[architecture/04-distributed-systems/05-replication|replicated]] commit log. **Ordering is guaranteed within a partition** (via offsets), consumers track offsets, and retention/compaction control how long history lives. It's the RSM log, productized for streaming.
- **LSM-trees** (Log-Structured Merge trees — RocksDB, Cassandra, LevelDB) — how storage engines make writes fast: append every write to a **write-ahead log** + an in-memory table, then merge to disk in the background. The database you query is *built on a log underneath*.
- **Change Data Capture (CDC)** — treat a database's own replication log as an event stream (Debezium tailing the WAL). This is the bridge that turns "a database" into "a stream of every change," so downstream systems (search indexes, caches, analytics) stay in sync by *consuming the log*.
- **Event sourcing** — the app-architecture face: store the **log of events as the source of truth** (not the current state), and derive current state by replaying. Gives a perfect audit trail and time-travel, at the cost of replay complexity. ([[architecture/03-architectural-patterns/03-data-and-integration-patterns|data & integration patterns]] covers this and CQRS.)

Every one of these is "an ordered, append-only log + something that replays it." Recognizing that is the payoff of the note.

## Exactly-once, honestly (again, via the log)

The log makes the [[architecture/04-distributed-systems/02-theoretical-limits|"exactly-once is impossible"]] reality manageable. You get **exactly-once *effect*** (not delivery) by combining:
- **ordered offsets** — a consumer knows exactly where it is,
- **idempotent consumers** — reprocessing the same offset is harmless,
- **atomic "process + advance offset"** — commit the work and the new offset together, so a crash-retry can't double-count.

Kafka's "exactly-once semantics" is this pattern, not magic — the same [[architecture/04-distributed-systems/10-distributed-transactions|at-least-once + idempotency]] truth wearing a log.

## Key insight

**The append-only, totally-ordered log is the hidden backbone of distributed systems: agree on an ordered list of commands, and every replica that replays it from the same start ends up identical (a replicated state machine — the one requirement being that commands are deterministic).** [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] exists to agree on that log; **Kafka** is the log as streaming infrastructure; **LSM-trees** are a log under your database; **CDC** turns a DB into its log; **event sourcing** stores the log *as* the truth. And "exactly-once" is just an ordered log + idempotent consumers + atomic offset commit. Once you see the log everywhere, the field unifies.

## Related
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — agrees on the log that drives the RSM
- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — a replicated log, concretely
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — the log *is* a total order of operations
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — event sourcing, CQRS, streaming
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — LSM storage engines
