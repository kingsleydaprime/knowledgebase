# Partitioning & Fault Tolerance

**[reference]** — from the canon (DDIA chapters 6 & 8). How data is spread across nodes for scale, and how the system keeps working as nodes come, go, and die. The operational reality of running a distributed system.

## Partitioning (sharding) — spreading data

To store more data or handle more writes than one node can, you **partition** (shard): split the dataset so each node holds a subset ([[architecture/02-building-blocks/03-databases-at-scale|databases at scale]]). The whole game is choosing *how* to split so load is even and queries stay efficient.

### Partitioning strategies

- **Range partitioning** — assign contiguous key ranges to nodes (A–F on node 1, G–M on node 2…). Great for range scans (they hit few nodes), but prone to **hotspots** — if keys are time-ordered, all recent writes hit one node.
- **Hash partitioning** — hash the key and assign by hash. Distributes evenly (no hotspots from key skew), but destroys range queries (adjacent keys scatter across nodes).
- **The hot-key problem** — even with hashing, a single extremely popular key (a celebrity's account) overloads one partition. Mitigations: add a random suffix to split it, or cache it separately.

The **partition key** is the most important schema decision in a sharded system — a poor choice creates hotspots or forces expensive cross-partition operations that can't be undone without a painful migration.

### Consistent hashing — partitioning that survives change

Naive hashing (`node = hash(key) % N`) has a fatal flaw: **change N (add/remove a node) and *almost every* key remaps**, triggering a massive reshuffle. **Consistent hashing** solves this: map both nodes and keys onto a hash ring, and a key belongs to the next node clockwise. Adding/removing a node only remaps the keys in *one segment* of the ring — roughly `1/N` of keys move, not all of them. **Virtual nodes** (each physical node placed at many ring positions) smooth out the distribution and rebalancing. This is the backbone of Dynamo/Cassandra/many caches and load balancers, and a great thing to implement to understand.

## Fault detection — knowing who's alive

You can't [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|reliably tell dead from slow]], but you must *estimate* liveness to route around failures:

- **Heartbeats** — nodes periodically signal "I'm alive"; miss enough and you suspect failure. The timeout is a tradeoff (fast detection vs false positives).
- **Gossip protocols** — instead of a central monitor, nodes *gossip* health info to a few random peers, who spread it further, so knowledge of failures propagates epidemically across the cluster. Scalable and resilient (no central point), used by Cassandra, Consul, and others for membership and failure detection.
- **Phi accrual failure detectors** — output a *suspicion level* rather than a binary dead/alive, letting the app choose its own threshold.

## Rebalancing and recovery

When nodes are added (scale out), removed, or fail, data must **rebalance** so load stays even — moving partitions to new nodes ([[architecture/04-distributed-systems/05-replication|from replicas]]) without downtime and without moving *more* than necessary (why consistent hashing matters). Recovery from a failed node means promoting a [[architecture/04-distributed-systems/05-replication|replica]] and re-replicating to restore the redundancy level. Doing this automatically, safely, and without overwhelming the cluster (a rebalance storm) is core operational machinery.

## Replication + partitioning together

Real systems do **both**: partition for scale, and replicate each partition for fault tolerance. So a dataset is split into shards, and each shard has (say) 3 replicas across different nodes/racks/zones. A partition's replicas often form a small [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] group (Raft) for strong consistency within the shard, while the system scales by having *many* such groups. This "shard + replicate + consensus-per-shard" is the architecture of modern distributed databases (Spanner, CockroachDB, TiDB) — the synthesis of everything in this section.

## The synthesis

Fault tolerance isn't one feature; it's the *combination*: [[architecture/04-distributed-systems/05-replication|replication]] for redundancy, [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] for agreement, partitioning + consistent hashing for scale, failure detection + gossip for awareness, and rebalancing for recovery — all assuming [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|things constantly fail]]. Building even a slice of it (a consistent-hash sharded cache, a Raft KV-store) is where this stops being abstract.

## Related
- [[architecture/04-distributed-systems/05-replication|Replication & Consistency]] — the redundancy half of fault tolerance
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — per-shard agreement
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — sharding from the system-design view
