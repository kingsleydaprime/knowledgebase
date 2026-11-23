---
id: 5482315c-f930-47ac-900a-3be8d053e8e4
---

# Databases at Scale

Databases at scale is about keeping data stored and quick to reach when an app has millions of users and far more data than one machine can hold. It starts with choosing the right kind of database and then spreading the data and the work across many machines. This lesson covers those choices and what each one costs.

## SQL vs NoSQL — the first choice
<!-- bite: 27411729-daf3-4347-8cc4-8134cacdc720 -->

- **SQL (relational)** — structured tables, a rigid schema, **ACID** transactions, and joins. Strong consistency, powerful queries. The right default for most applications and anything needing correctness (money, relationships between entities). Scales *up* easily; scaling *out* (writes) is harder.
- **NoSQL** — a family, each trading relational features for scale/flexibility:
  - **Key-value** (Redis, DynamoDB) — dead-simple, blazing fast, scales horizontally trivially. For caching, sessions, simple lookups.
  - **Document** (MongoDB) — JSON-like documents, flexible schema. For semi-structured, aggregate-oriented data.
  - **Wide-column** (Cassandra) — huge write throughput, tunable consistency, scales to petabytes. For time-series, event logs, write-heavy at massive scale.
  - **Graph** (Neo4j) — nodes and edges. For relationship-heavy queries (social graphs, recommendations).

The honest guidance: **default to SQL** — it's more capable, and "we might need to scale" is usually premature. Reach for NoSQL when you have a *specific* need it serves: extreme write scale, a flexible schema, or an access pattern (key lookups, graph traversal) SQL handles poorly. "NoSQL because it scales" without that specific need trades away transactions and joins you'll miss.

## Scaling reads: replication
<!-- bite: 02f7fca7-5bcf-4b7e-94c7-ef6a1f799d37 -->

Most load is reads, so the first database scaling move is **replication** — copies of the database that serve reads:

- **Leader-follower (primary-replica)** — writes go to one leader, which replicates to read-only followers. Route reads to followers to multiply read capacity. The standard pattern.
- The catch: **replication lag** — a follower may be slightly behind the leader, so a read right after a write can see stale data ([[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]]). "Read-your-own-writes" (route a user's reads to the leader briefly after they write) is the common fix.

Replication also buys availability (a follower can be promoted if the leader dies — [[architecture/01-system-design-fundamentals/03-availability-and-reliability|failover]]). The mechanics are in [[architecture/04-distributed-systems/05-replication|replication & consistency]].

## Scaling writes: sharding (partitioning)
<!-- bite: 445e1fe0-e6c3-414b-82ee-5bcaf717577d -->

Replication multiplies reads but every node still handles every write. To scale *writes* (and data beyond one machine), **shard**: split the data across multiple databases, each holding a subset.

- **Shard key** — the field you partition on (user_id, geography). *The* critical decision — a bad key creates **hot shards** (one shard gets most traffic) and makes cross-shard queries painful.
- **Strategies** — **range** partitioning (by key range — good for range scans, prone to hotspots) vs **hash** partitioning (hash the key — even distribution, but kills range queries). **Consistent hashing** ([[architecture/04-distributed-systems/13-partitioning|partitioning]]) minimizes reshuffling when nodes are added/removed.
- **The costs** — sharding is a big step: **cross-shard joins/transactions become hard or impossible**, rebalancing is operationally painful, and it adds real complexity. Exhaust replication + caching + a bigger box *first*; shard when you genuinely must.

## Other scaling tools
<!-- bite: 9f98c293-15ef-4b6a-b3dd-d7599871c078 -->

- **Indexing** — the highest-leverage single-DB optimization: an index turns an O(n) table scan into an O(log n) lookup. Under-indexing is the #1 cause of slow queries; over-indexing slows writes (every index must be maintained — the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|load-then-index]] insight). Know what your queries need.
- **Denormalization** — deliberately duplicating data to avoid expensive joins at read time, trading storage and write-complexity for read speed ([[machine-learning/index|the same tradeoff]] as everywhere). The [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|transaction-record denormalization]] is a real example.
- **Connection pooling, query optimization, materialized views** — squeeze more from one database before distributing.

## The order of operations
<!-- bite: 8339a4db-31b0-4fde-aa3c-2c57286eb5c5 -->

When the database is the bottleneck, escalate in roughly this order (cheap/simple → expensive/complex): **optimize queries + indexes → add caching → add read replicas → denormalize → shard.** Each step buys time; sharding is the last resort because it's the most complex and hardest to undo.

## Check your understanding
<!-- bite: d24ed2ba-8fdd-468d-89fb-ca862ca76b6b -->

Try each one before you open the answer.

1. <!-- q: mcq id="06bee7ad" -->
   A team says "let's use NoSQL because it scales", but has no specific need such as extreme write volume or graph queries. What's the usual advice?

   - [x] Default to SQL: it has transactions and joins, and the scaling worry is probably premature
   - [ ] Use NoSQL: it always scales better
   - [ ] Use a graph database to be safe
   - [ ] Shard a SQL database from day one

   <details><summary>Answer</summary>

   SQL is the right default for most applications. NoSQL earns its place when a specific need calls for it; without one, you give up transactions and joins you'll miss.

   </details>

2. <!-- q: mcq id="ec65e3f8" -->
   A user updates their profile, then reloads the page and sees the old profile. Reads go to followers that copy the leader. What's the cause, and the usual fix?

   - [ ] A missing index; add one
   - [x] Replication lag; send that user's reads to the leader for a short time after they write
   - [ ] A hot shard; change the shard key
   - [ ] The leader lost the write; turn on backups

   <details><summary>Answer</summary>

   A follower can be slightly behind the leader, so a read right after a write can be stale. "Read-your-own-writes" routes the writer's reads to the leader briefly.

   </details>

3. <!-- q: gap id="8663d3d7" answers="sharding|partitioning|shard;shard key" -->
   Fill in the gaps. Replication spreads reads, but every node still handles every write. To scale writes you use ___, splitting the data across databases by a field called the ___.

   <details><summary>Answer</summary>

   Sharding (partitioning) gives each database a subset of the data and so a subset of the writes. The shard key decides which database each row lives on, and a bad one creates hot shards.

   </details>

4. <!-- q: mcq id="8da50fd9" -->
   Which is true of hash partitioning compared with range partitioning?

   - [x] It spreads keys evenly, but makes range queries (such as "all orders from March") hit every shard
   - [ ] It's better for range scans but prone to hotspots
   - [ ] It needs no shard key
   - [ ] It makes cross-shard joins easy

   <details><summary>Answer</summary>

   Hashing the key scatters neighbouring keys across shards, which evens out load but breaks range scans. Range partitioning keeps neighbours together, which helps scans but can create hot shards.

   </details>

5. <!-- q: gap id="84354977" answers="caching|cache;read replicas|replicas;sharding|shard" -->
   Fill in the gaps. When the database is the bottleneck, escalate from cheap to expensive: optimise queries and indexes, then add ___, then add ___, then denormalise, and only then ___.

   <details><summary>Answer</summary>

   Queries and indexes, caching, read replicas, denormalisation, then sharding. Sharding comes last because it's the most complex and the hardest to undo.

   </details>

6. <!-- q: open id="8147d9d8" -->
   Why is sharding treated as a last resort?

   <details><summary>Answer</summary>

   Joins and transactions across shards become hard or impossible, rebalancing data when you add shards is painful, and the whole system gets more complex. Replication, caching and a bigger machine buy time with far less cost, so you shard only when you really must.

   </details>

## Check your understanding: worked problems
<!-- bite: 93979ddf-3cba-4c17-8498-c7e358d28d86 -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="05f6ef8c" answer="6" -->
   A database gets 30,000 reads a second, and all reads go to read-only followers. Each follower can serve 5,000 reads a second. How many followers are needed, at least?

   <details><summary>Answer</summary>

   6. 30,000 ÷ 5,000 = 6. Followers multiply read capacity, but every one of them still applies every write.

   </details>

2. <!-- q: exact id="c14728c3" answer="5" -->
   A system must take 18,000 writes a second. One database can handle 4,000 writes a second, and the writes spread evenly by a hashed shard key. How many shards does it need, at least?

   <details><summary>Answer</summary>

   5. 18,000 ÷ 4,000 = 4.5, rounded up to 5. Adding read replicas wouldn't help, because each replica still applies every write.

   </details>

3. <!-- q: exact id="3c624c2a" answer="12" -->
   A dataset is 12 TB. Each database machine has 2 TB of disk, and the team keeps each machine at most half full to leave room for growth. How many shards does it need?

   <details><summary>Answer</summary>

   12. Each machine holds at most 1 TB, so 12 TB ÷ 1 TB = 12 shards.

   </details>

4. <!-- q: gap id="ec775921" answers="50000000|50,000,000|50 million;26" -->
   Fill in the gaps. A table has 50 million rows. Finding one row with no index means checking up to ___ rows. With an index, which takes about log₂(n) steps, it takes about ___ steps (round up).

   <details><summary>Answer</summary>

   Up to 50,000,000 rows for a full scan, against ⌈log₂ 50,000,000⌉ = 26 steps with an index. That's why indexing is the highest-leverage single-database fix.

   </details>

## Related
<!-- bite: b39c0c03-55ef-4188-9fc0-01b017b5397e -->
- [[architecture/04-distributed-systems/05-replication|Replication & Consistency]] — how replication actually works
- [[architecture/02-building-blocks/02-caching/index|Caching]] — the layer that protects the database
- [[databases/database-design-reference|Databases reference]] — SQL/schema/indexing fundamentals

## About this lesson
<!-- bite: b2353fc4-c1cc-4144-a720-317a0822de0c -->

**Level:** reference. **Covers:** from the roadmap.sh system-design roadmap. The database is almost always the first thing to buckle under load, so scaling it is central to system design. This is the *scaling* view; the [[databases/database-design-reference|databases reference]] covers the fundamentals.
