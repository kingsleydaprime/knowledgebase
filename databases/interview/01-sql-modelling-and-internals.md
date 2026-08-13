# Database Interview — SQL, Modelling & Internals

From [[databases/sql-reference|sql-reference]], [[databases/database-design-reference|database-design-reference]], [[databases/nosql-reference|nosql-reference]].

---

### Q1. [Intermediate] 🔥 How does an index actually work, and when does it *not* help?

**Strong answer covers:** a B+tree — sorted, balanced, with all values in the leaves linked together (which is what makes range scans cheap). Lookup is O(log n) page reads instead of a full table scan. Typically 3–4 levels deep even for hundreds of millions of rows, and the upper levels stay in memory, so a lookup is often one or two actual disk reads.

**When it doesn't help — this is the real question:**
- **Low cardinality.** An index on a boolean is usually useless; if 50% of rows match, a table scan is cheaper than an index lookup plus a random-access fetch per row.
- **Leading-column rule.** An index on `(a, b)` serves queries on `a` and on `(a, b)`, but **not on `b` alone**. Think of it as a phone book sorted by (surname, first name) — useless for finding everyone named "Kingsley."
- **Functions on the column.** `WHERE UPPER(email) = ?` can't use an index on `email`. You need a functional/expression index.
- **Writes.** Every index must be maintained on insert/update/delete. Indexes are a **read/write tradeoff**, and an over-indexed table has slow writes.

**Detail that scores:** a **covering index** (one that contains every column the query needs) lets the database answer from the index alone — an "index-only scan," skipping the table entirely. Often a bigger win than adding another index.

---

### Q2. [Intermediate] 🔥 Explain ACID. Which property is the interesting one?

**Strong answer covers:** **Atomicity** (all or nothing), **Consistency** (constraints hold before and after — arguably the odd one out, since it's about your schema rather than the engine), **Isolation** (concurrent transactions don't corrupt each other), **Durability** (committed means survives a crash).

**Isolation is the interesting one**, because it's the only one that comes in *degrees* — and because the default in most databases is not the strictest. Everything in Q3 follows from that.

**Mechanisms worth naming:** durability comes from the **write-ahead log** — write the intent to a sequential log and `fsync` it *before* mutating pages, so a crash mid-write is recoverable. Sequential log writes are far cheaper than random page writes, which is why WAL is both a correctness and a performance mechanism.

---

### Q3. [Advanced] 🔥 Walk the isolation levels and the anomalies each one allows.

**Strong answer covers:**

| Level | Prevents | Still allows |
|---|---|---|
| **Read Uncommitted** | — | dirty reads |
| **Read Committed** | dirty reads | non-repeatable reads, phantoms |
| **Repeatable Read** | + non-repeatable reads | phantoms (classically) |
| **Serializable** | everything | — (but with contention/aborts) |

- **Dirty read** — you see another transaction's uncommitted data.
- **Non-repeatable read** — you read the same row twice and get different values.
- **Phantom** — you run the same *range query* twice and get different rows.

**What separates a strong answer:**
- **Know your defaults.** Postgres and Oracle default to **Read Committed**; MySQL/InnoDB defaults to **Repeatable Read**. The same application code behaves differently on each — a genuinely dangerous portability trap.
- **Postgres's "Repeatable Read" is actually snapshot isolation**, which prevents phantoms but permits **write skew** — two transactions each read an overlapping set, each makes a decision valid on its own snapshot, and together they violate an invariant. (Two doctors both go off-call because each sees the other still on-call.) Only `SERIALIZABLE` prevents it. Naming write skew is a strong senior signal.
- **MVCC** is the mechanism: readers see a snapshot rather than blocking on writers, which is why "readers don't block writers" in Postgres — at the cost of keeping old row versions around, and hence `VACUUM` and bloat.

---

### Q4. [Intermediate] 🔥 A query is slow. Walk me through it.

**Strong answer covers a method, not guesses:**
1. **`EXPLAIN ANALYZE`** — get the actual plan and actual timings, not the estimate.
2. **Look for a sequential scan on a large table** where you expected an index. Why wasn't it used? Wrong column order, a function on the column, a type mismatch, or the planner correctly deciding a scan is cheaper.
3. **Compare estimated vs actual rows.** A large divergence means **stale statistics** — the planner is choosing based on a wrong picture. `ANALYZE` the table.
4. **Look for the expensive node** — a nested loop over a large set (should be a hash join?), a sort that spilled to disk (`work_mem` too small), a filter applied late.
5. **Check whether it's the query at all** — lock contention, connection-pool exhaustion, and I/O saturation all look like "slow query" from the application.

**Join strategies to know:** nested loop (good when one side is tiny), hash join (good for large unsorted sets, needs memory), merge join (good when both are sorted). The planner picks; you influence it by giving it good statistics and useful indexes.

---

### Q5. [Intermediate] Normalise or denormalise?

**Strong answer covers:** normalise by default — 3NF means each fact lives in exactly one place, so updates can't produce contradictions. Denormalise **deliberately**, for a measured read problem, accepting that you now own the consistency of the duplicate.

**The framing that scores:** denormalisation is a **cache**, and it has every problem a cache has — invalidation, staleness, and drift. Treat it as such: know how it gets updated, and have a way to detect divergence.

**When it's clearly right:** a counter you'd otherwise compute with a `COUNT(*)` over millions of rows on every page load; a materialised view for an expensive aggregate; storing a display name alongside a foreign key on an append-only record where the historical value is *supposed* to be frozen.

---

### Q6. [Intermediate] 🔥 SQL vs NoSQL — how do you actually decide?

**Strong answer covers:** the honest default is **relational**, because you usually don't know your access patterns up front, and SQL lets you ask questions you didn't anticipate. NoSQL generally requires you to model *for* your queries, which is fine when you know them and painful when they change.

**Reach for NoSQL when there's a specific reason:**
- **Document** (Mongo) — genuinely variable schema, aggregate-oriented access, no cross-entity joins.
- **Key-value** (Redis, DynamoDB) — known access path, extreme throughput, simple lookups.
- **Wide-column** (Cassandra) — massive write throughput, time-series, tunable consistency, no single point of failure.
- **Graph** (Neo4j) — relationship traversal *is* the query (recommendations, fraud rings).
- **Vector** (pgvector, Pinecone) — similarity search for [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]].

**Two things that make this answer better than most:**
1. "NoSQL scales, SQL doesn't" is outdated. Postgres with partitioning and read replicas handles the vast majority of applications, and modern distributed SQL (CockroachDB, Spanner, Vitess) gives horizontal scale without giving up joins or transactions.
2. **Postgres often is the NoSQL database** — `JSONB` for documents, `pgvector` for embeddings, `LISTEN/NOTIFY` for pub/sub, arrays, full-text search. "One well-understood database" is a real operational advantage; the strongest version of this answer defends *not* adding a second datastore.

---

### Q7. [Intermediate] What are the tradeoffs of a UUID primary key?

**Strong answer covers:** UUIDs let clients generate IDs without coordination, don't leak row counts, and make merging data from multiple sources safe. But **UUIDv4 is random**, and as a clustered primary key that's genuinely bad: inserts land at random points in the B+tree, causing page splits, fragmentation, and a working set that doesn't fit in cache. They're also 16 bytes vs 4–8, and every secondary index carries a copy.

**The modern answer:** **UUIDv7 / ULID** — a time-ordered prefix plus randomness. You keep coordination-free generation *and* get insert locality. Use it. → [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|id generation]]

---

### Q8. [Intermediate] 🔥 How do connection pools work and how do you size one?

**Strong answer covers:** opening a database connection is expensive (TCP handshake, TLS, auth, backend process spawn in Postgres), so a pool keeps them open and hands them out. Key settings: max size, min idle, connection timeout, max lifetime, validation.

**Sizing — and the counterintuitive point is the answer:** **smaller is usually faster.** A common formula is `connections ≈ (2 × cores) + effective_spindles`. A pool of 300 against an 8-core database is slower than a pool of 20, because you've moved the queue from your application (where it's cheap) into the database (where every connection competes for CPU, memory, and locks). HikariCP's documentation makes this case well and it's a great thing to cite.

**Operational details:** set `maxLifetime` below any network/firewall idle timeout so the pool retires connections before a [[foundations/networking/06-tcp-connection-lifecycle|middlebox silently kills them]]. And in serverless/high-instance-count environments, use a proxy (PgBouncer, RDS Proxy) — otherwise 500 lambda instances × 10 connections exhausts the server.

---

### Q9. [Advanced] What happens when a replica lags, and how do you handle read-your-own-writes?

**Strong answer covers:** async replication means a replica may be seconds behind. A user posts a comment (write → primary), the page reloads (read → replica), and the comment isn't there. They post it again. This is the **read-your-own-writes** violation and it's one of the most common real bugs in a read-replica architecture.

**Fixes, with tradeoffs:** route reads to the primary for a short window after a user's write (simple, effective, gives up some read scaling); track the write position (LSN) and require the replica to have caught up to it (precise, more machinery); or use sticky routing per session.

**Related session guarantees to name:** monotonic reads (don't let a user see time go backwards by hitting a less-caught-up replica), consistent prefix. → [[architecture/04-distributed-systems/04-consistency-models|consistency models]]

---

### Q10. [Intermediate] 🔥 How would you safely add a NOT NULL column to a 500-million-row table in production?

**A brilliant question, because it separates people who've done migrations from people who've written them.**

**Strong answer covers:** the naive `ALTER TABLE ... ADD COLUMN NOT NULL DEFAULT x` historically rewrote the entire table while holding an exclusive lock — an outage. (Postgres 11+ and recent MySQL handle a constant default via metadata only, so **know your version** — that's part of the answer.)

**The safe general pattern — expand/contract:**
1. Add the column as **nullable**, no default. Instant.
2. **Backfill in batches**, with pauses, so you don't saturate I/O or hold long transactions that bloat the WAL.
3. Deploy code that writes the column for all new rows (dual-write).
4. Once fully backfilled, add the `NOT NULL` constraint — as `NOT VALID` first, then `VALIDATE` separately, which takes a weaker lock.
5. Contract: remove the old path.

**The principle to state:** **every schema migration must be backwards-compatible with the currently-running code**, because deploy and migration are never simultaneous, and you need to be able to roll back. That principle — expand, migrate, contract — is the real answer, and it generalises to renaming columns, changing types, and splitting tables.
