# Replication & Consistency

**[reference]** — from the canon (DDIA chapters 5 & 9). How you keep multiple copies of data, and what guarantees you can offer about what readers see. This is the mechanism behind the [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP/consistency]] tradeoffs.

## Why replicate

Keeping copies of data on multiple nodes buys **availability** (survive a node loss), **read scalability** ([[architecture/02-building-blocks/03-databases-at-scale|serve reads from replicas]]), and **latency** (a replica near the user). The whole difficulty: **keeping the copies in sync** when writes happen and nodes/networks fail.

## The three replication architectures

### Single-leader (primary-replica)

All writes go to one **leader**, which propagates them to **followers**; reads can hit any replica. Simple and the most common (most SQL databases).

- **Sync vs async replication** — sync (leader waits for a follower to confirm before ack'ing the write) is durable but slow and blocks if the follower is down; async (ack immediately, replicate in background) is fast but can *lose* recently-acked writes if the leader dies before propagating. Most systems use async or semi-sync, accepting a small durability risk for speed.
- **Replication lag** — followers trail the leader, causing read anomalies: reading your own write and not seeing it, or seeing time "go backwards." Fixes are consistency guarantees like **read-your-writes** and **monotonic reads**.
- **Failover** — if the leader dies, promote a follower ([[architecture/01-system-design-fundamentals/03-availability-and-reliability|failover]]) — which needs [[architecture/04-distributed-systems/04-consensus|consensus]] to pick one and avoid **split-brain** (two leaders).

### Multi-leader

Multiple leaders accept writes (e.g. one per region), replicating to each other. Better write availability/latency (write locally), but now the same data can be written in two places concurrently → **write conflicts** that must be resolved.

### Leaderless (Dynamo-style)

Any replica accepts writes; clients write to *several* and read from *several*, using **quorums** to get consistency. The Dynamo/Cassandra model — highly available, no failover needed, but the client/coordinator handles conflict resolution.

## Quorums — consistency from counting

The leaderless trick: with **N** replicas, require **W** to acknowledge a write and **R** to respond to a read. If **W + R > N**, any read set overlaps any write set, so a read is guaranteed to see the latest write (a "quorum"). Tuning W and R trades consistency vs availability vs latency (e.g. W=N, R=1 for fast reads; W=1, R=N for fast writes). This is how leaderless systems offer *tunable* consistency.

## Conflict resolution

When concurrent writes conflict (multi-leader, or leaderless), you must resolve them:

- **Last-write-wins (LWW)** — pick by timestamp. Simple but **loses data** and is unreliable due to [[architecture/04-distributed-systems/02-time-and-ordering|clock skew]].
- **Vector clocks** — detect *which* writes are truly concurrent ([[architecture/04-distributed-systems/02-time-and-ordering|vector clocks]]) and keep both as siblings for the app to merge.
- **CRDTs** (Conflict-free Replicated Data Types) — data structures *designed* so concurrent updates always merge deterministically without conflict (counters, sets, sequences). The elegant answer: make conflicts mathematically impossible to lose. The basis of collaborative editing (Google Docs-style) and local-first apps.

## The consistency spectrum (what readers are promised)

From strongest/most-expensive to weakest/most-available — the precise version of the [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP spectrum]]:

- **Linearizable (strong)** — the system behaves as if there's a single copy; every read sees the latest completed write, and there's a single real-time order. The simplest to reason about, the most expensive (requires coordination — [[architecture/04-distributed-systems/04-consensus|consensus]] on every operation), limits availability.
- **Sequential** — all nodes see operations in the same order, but not necessarily real-time order.
- **Causal** — operations related by [[architecture/04-distributed-systems/02-time-and-ordering|happens-before]] are seen in order by everyone; concurrent ops may be seen in different orders. A strong, *achievable-with-availability* middle ground — often the best you can get in an AP system.
- **Eventual** — replicas converge if writes stop; until then, reads may be stale or see updates out of order. Cheapest, most available.

## The design instinct

Replication and its consistency level is the concrete "how" behind the [[architecture/01-system-design-fundamentals/04-cap-and-consistency|per-data consistency decision]]: single-leader + strong consistency for the money; leaderless/eventual + CRDTs for the collaborative feed. **Weaker consistency = more available + faster + more complex application logic** (you handle staleness/conflicts). Choose the weakest each dataset tolerates — and note that "strong consistency" ultimately requires [[architecture/04-distributed-systems/04-consensus|consensus]], the next note.

## Related
- [[architecture/04-distributed-systems/04-consensus|Consensus]] — what strong consistency and leader election require
- [[architecture/04-distributed-systems/02-time-and-ordering|Time & Ordering]] — vector clocks for conflict detection
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — replication as a scaling tool
