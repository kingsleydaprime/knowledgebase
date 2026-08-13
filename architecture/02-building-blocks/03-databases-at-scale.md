# Databases at Scale

**[reference]** — from the roadmap.sh system-design roadmap. The database is almost always the first thing to buckle under load, so scaling it is central to system design. This is the *scaling* view; the [[databases/database-design-reference|databases reference]] covers the fundamentals.

## SQL vs NoSQL — the first choice

- **SQL (relational)** — structured tables, a rigid schema, **ACID** transactions, and joins. Strong consistency, powerful queries. The right default for most applications and anything needing correctness (money, relationships between entities). Scales *up* easily; scaling *out* (writes) is harder.
- **NoSQL** — a family, each trading relational features for scale/flexibility:
  - **Key-value** (Redis, DynamoDB) — dead-simple, blazing fast, scales horizontally trivially. For caching, sessions, simple lookups.
  - **Document** (MongoDB) — JSON-like documents, flexible schema. For semi-structured, aggregate-oriented data.
  - **Wide-column** (Cassandra) — huge write throughput, tunable consistency, scales to petabytes. For time-series, event logs, write-heavy at massive scale.
  - **Graph** (Neo4j) — nodes and edges. For relationship-heavy queries (social graphs, recommendations).

The honest guidance: **default to SQL** — it's more capable, and "we might need to scale" is usually premature. Reach for NoSQL when you have a *specific* need it serves: extreme write scale, a flexible schema, or an access pattern (key lookups, graph traversal) SQL handles poorly. "NoSQL because it scales" without that specific need trades away transactions and joins you'll miss.

## Scaling reads: replication

Most load is reads, so the first database scaling move is **replication** — copies of the database that serve reads:

- **Leader-follower (primary-replica)** — writes go to one leader, which replicates to read-only followers. Route reads to followers to multiply read capacity. The standard pattern.
- The catch: **replication lag** — a follower may be slightly behind the leader, so a read right after a write can see stale data ([[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]]). "Read-your-own-writes" (route a user's reads to the leader briefly after they write) is the common fix.

Replication also buys availability (a follower can be promoted if the leader dies — [[architecture/01-system-design-fundamentals/03-availability-and-reliability|failover]]). The mechanics are in [[architecture/04-distributed-systems/05-replication|replication & consistency]].

## Scaling writes: sharding (partitioning)

Replication multiplies reads but every node still handles every write. To scale *writes* (and data beyond one machine), **shard**: split the data across multiple databases, each holding a subset.

- **Shard key** — the field you partition on (user_id, geography). *The* critical decision — a bad key creates **hot shards** (one shard gets most traffic) and makes cross-shard queries painful.
- **Strategies** — **range** partitioning (by key range — good for range scans, prone to hotspots) vs **hash** partitioning (hash the key — even distribution, but kills range queries). **Consistent hashing** ([[architecture/04-distributed-systems/13-partitioning|partitioning]]) minimizes reshuffling when nodes are added/removed.
- **The costs** — sharding is a big step: **cross-shard joins/transactions become hard or impossible**, rebalancing is operationally painful, and it adds real complexity. Exhaust replication + caching + a bigger box *first*; shard when you genuinely must.

## Other scaling tools

- **Indexing** — the highest-leverage single-DB optimization: an index turns an O(n) table scan into an O(log n) lookup. Under-indexing is the #1 cause of slow queries; over-indexing slows writes (every index must be maintained — the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|load-then-index]] insight). Know what your queries need.
- **Denormalization** — deliberately duplicating data to avoid expensive joins at read time, trading storage and write-complexity for read speed ([[ai-ml/02-ml-engineer/README|the same tradeoff]] as everywhere). The [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|transaction-record denormalization]] is a real example.
- **Connection pooling, query optimization, materialized views** — squeeze more from one database before distributing.

## The order of operations

When the database is the bottleneck, escalate in roughly this order (cheap/simple → expensive/complex): **optimize queries + indexes → add caching → add read replicas → denormalize → shard.** Each step buys time; sharding is the last resort because it's the most complex and hardest to undo.

## Related
- [[architecture/04-distributed-systems/05-replication|Replication & Consistency]] — how replication actually works
- [[architecture/02-building-blocks/02-caching|Caching]] — the layer that protects the database
- [[databases/database-design-reference|Databases reference]] — SQL/schema/indexing fundamentals
