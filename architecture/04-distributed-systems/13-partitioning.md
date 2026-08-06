# Partitioning

**[reference]** — from the canon (DDIA ch. 6). How data is **split across many nodes** so you can store more and serve more than one machine can hold — and how to split it *well*, so load stays even and queries stay cheap. (Knowing *who's alive* to route around failures is the sibling topic: [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure detection & membership]].)

## The kid version first

You have **way too many toys for one toy box** — so you get several boxes and split the toys across them. Simple idea, but the *hard* question is **which toy goes in which box**, and you have two instincts:
- **By name (A–F in box 1, G–M in box 2…).** Nice when you want "all the toys starting with S" — they're together. But if a new craze means *everyone* wants the newest toys (all starting with "Z"), **one box gets mobbed** while others sit idle (a **hotspot**).
- **By a scramble rule (a "hash"): compute a number from the toy's name and use it to pick a box.** Spreads toys evenly so no box gets mobbed — but now "all the S toys" are scattered across every box.

And there's a nasty trap: if you pick the box with **"box = number mod (how many boxes)"** and then *add one more box*, the math changes for *almost every toy* → you have to **re-sort nearly everything**. The clever fix (**consistent hashing**) makes adding a box move only *a few* toys. That's this whole note.

## Partitioning (sharding) strategies

**Partitioning** (a.k.a. sharding) splits the dataset so each node holds a subset ([[architecture/02-building-blocks/03-databases-at-scale|databases at scale]]). Two base strategies, with opposite tradeoffs:

- **Range partitioning** — assign contiguous key ranges to nodes (`A–F` → node 1, `G–M` → node 2…). **Great for range scans** (a "last 24 hours" query hits few nodes) — but **hotspot-prone**: time-ordered keys send *all* recent writes to one node.
- **Hash partitioning** — hash the key, assign by hash. **Distributes evenly** (kills key-skew hotspots), but **destroys range queries** (adjacent keys scatter everywhere). Compound keys (hash the first part, range the second) recover *some* locality.

**The partition key is the single most important decision in a sharded system.** A poor choice bakes in hotspots or forces expensive cross-partition operations, and changing it later means a painful migration. Choose it to (a) spread load evenly and (b) keep your common queries on as few partitions as possible.

### The hot-key problem
Even perfect hashing can't save you from **one key that's individually enormous** — a celebrity's account, a viral post. All its traffic lands on one partition. Mitigations: **split the hot key** by appending a random suffix (spreading it across N partitions, at the cost of reads having to gather all N), or **cache it** separately in front of the store. There's no automatic fix; the application has to know which keys are hot.

## Consistent hashing — partitioning that survives change

Naive `node = hash(key) % N` has a fatal operational flaw: **change `N` (add or remove a node) and almost every key remaps**, triggering a cluster-wide reshuffle (and cache-miss storm). **Consistent hashing** fixes it:

- Map **both nodes and keys onto a ring** (a hash space wrapped into a circle). A key belongs to the **next node clockwise** from its position.
- Add or remove a node and **only the keys in that one arc move** — roughly **`1/N` of keys**, not all of them. The rest stay put.
- **Virtual nodes** — place each physical node at *many* points on the ring (not one). This smooths the distribution (no node accidentally owning a huge arc) and makes rebalancing spread evenly when a node joins/leaves. Without virtual nodes, consistent hashing distributes lumpily.

This is the backbone of Dynamo, Cassandra, Riak, and many caches/load balancers — and one of the best things to implement yourself to make distributed systems concrete (the ⭐ consistent-hash sharded cache in [[architecture/05-case-studies/README|case studies]]).

> **Aside — fixed-partition rebalancing.** Many systems (e.g. Kafka, Elasticsearch) instead create a *large fixed number* of partitions up front (say 1000) and just **assign partitions to nodes**, moving whole partitions when nodes change. Simpler than a ring, and "how many partitions" becomes the capacity ceiling. Both approaches solve the same "don't reshuffle everything" goal.

## Secondary indexes — the cross-partition headache

Partitioning by primary key is easy; **querying by something else** is where it bites. Two schemes:
- **Local (document-partitioned) index** — each partition indexes only its own data. Writes are cheap (one partition), but a query on the secondary field must **scatter-gather across *all* partitions** (each might have matches). Common default.
- **Global (term-partitioned) index** — the index itself is partitioned by the indexed term, so a read hits one partition — but a **write** must update a *different* partition than the data, making writes cross-partition (often async). You trade read cost for write cost.

There's no free lunch; which you pick depends on read-heavy vs write-heavy.

## Request routing — finding the right partition

When a client wants key `K`, *who knows which node holds it?* Three approaches: the client asks any node (which forwards), a **routing tier / load balancer** knows the mapping, or the client is **partition-aware** and computes it directly. The partition→node mapping is itself cluster state that must stay consistent as things rebalance — usually kept in a **[[architecture/04-distributed-systems/09-coordination-services|coordination service]]** (ZooKeeper/etcd) so everyone reads the same up-to-date map.

## Partitioning + replication together (the real architecture)

Real systems do **both**: **partition for scale, replicate each partition for fault tolerance.** A dataset is split into shards, and *each shard* has (say) 3 [[architecture/04-distributed-systems/05-replication|replicas]] across different nodes/racks/zones. Frequently **each shard's replicas form a small [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] group** (Raft) for strong consistency *within* the shard, and the system scales by running **many** such groups. This **"shard + replicate + consensus-per-shard"** pattern is the architecture of every modern distributed database — [[architecture/04-distributed-systems/11-modern-distributed-transactions|Spanner, CockroachDB, TiDB]] — and the synthesis of this whole course.

## Key insight

**Partitioning is "too much for one node, so split it across many," and the whole art is choosing *how* to split.** Range keys give cheap scans but risk hotspots; hash keys spread evenly but scatter ranges — and the **partition key is your most consequential, hardest-to-change decision.** Never use `hash % N` (adding a node reshuffles everything); use **consistent hashing with virtual nodes** (or a large fixed partition count) so growth moves only `~1/N` of the data. Secondary indexes force a read-cost-vs-write-cost choice (local vs global). And real systems **combine partitioning with [[architecture/04-distributed-systems/05-replication|replication]] and per-shard [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]** — shard for scale, replicate for safety, agree within each shard.

## Related
- [[architecture/04-distributed-systems/05-replication|Replication]] — the redundancy half; shard, then replicate each shard
- [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection & Membership]] — knowing which nodes are alive to route/rebalance
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — per-shard agreement
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — sharding from the system-design view
