# What a Database Is

**[Beginner → Intermediate]** — Why not just use files, what ACID actually buys you, and how the landscape is shaped.

**Source:** `[reference]` — see [[databases/README|the domain note]].

## Why not just files

**Every database exists because somebody tried files first.**

Store your records as JSON on disk. Then:

**Concurrency.** Two processes write the same file. One overwrites the other, or you get a half-written file. **You need locking**, and now you're building a lock manager.

**Crash safety.** The power fails mid-write. **Half a record is on disk.** You need write-ahead logging and recovery. → [[databases/10-durability-and-recovery|Durability and Recovery]]

**Finding things.** "All orders over £100 from last month" means reading every record. **You need indexes.** → [[databases/04-b-trees-and-indexes|B-Trees and Indexes]]

**Memory limits.** The data exceeds RAM. **You need a buffer pool and a page-based format.** → [[databases/03-storage-and-page-layout|Storage and Page Layout]]

**Atomicity across records.** Transfer money between two accounts — both writes must happen or neither. **You need transactions.** → [[databases/08-transactions-and-acid|Transactions and ACID]]

**Consistency rules.** "Every order must reference a real customer." **You need constraints.**

> **A database is what you get when you take those six problems seriously.** It's not a fancy file format — it's forty years of accumulated answers to problems that appear the moment more than one thing touches your data.
>
> **Which is the argument against writing your own.** Not that it's hard to start; it's that you will re-derive all six, badly, over years. → [[build-your-own-shit/06-your-own-database|build-your-own-database]] exists to make that concrete, and its own "where to stop" section is the honest version of this argument.

## ACID

**The transactional guarantees**, and they're more slippery than the acronym suggests.

**Atomicity** — all of a transaction happens, or none. **Implemented by the write-ahead log**: undo what a failed transaction did.

**Consistency** — the database moves from one valid state to another, where "valid" means your constraints hold.

> **The C is the odd one out.** Atomicity, isolation and durability are properties the *database* provides. **Consistency is a property of your application's rules** — the database just enforces the constraints you declared. Several database researchers have observed that C is in the acronym mostly because ACID is pronounceable.

**Isolation** — concurrent transactions don't interfere. **The one with degrees**, and the one people misunderstand. → [[databases/09-mvcc-and-concurrency-control|MVCC]]

**Durability** — once committed, it survives a crash. **Implemented by fsync on the log.**

**The honest caveats:**

**Isolation is almost never full.** Most databases default to Read Committed or Snapshot Isolation, **not** Serializable. **You are probably running with anomalies your code doesn't handle.** → [[databases/08-transactions-and-acid|Isolation levels]]

**Durability depends on fsync actually working.** Disks lie about flushing, filesystems buffer, and virtualised storage adds layers. **"Committed" is only as strong as your weakest layer.**

**ACID is per-node.** Across machines it becomes a much harder problem. → [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]]

## OLTP vs OLAP

**The split that explains most of the database landscape**, and getting it wrong is the commonest architectural mistake in this area.

| | **OLTP** | **OLAP** |
|---|---|---|
| Workload | many small reads/writes | few huge scans |
| Query | "get order 12345" | "revenue by region by month" |
| Rows touched | one to a few | millions |
| Columns touched | **all of them** | **three of forty** |
| Latency target | milliseconds | seconds to minutes |
| Storage | **row-oriented** | **column-oriented** |
| Examples | Postgres, MySQL | ClickHouse, BigQuery, Snowflake, DuckDB |

> **The storage layout follows directly from the access pattern.** OLTP reads whole rows, so store rows together. OLAP reads three columns of forty, so **store columns together** — you read only what you need, and identical values compress enormously. **A column store can be 10–100× faster on analytical queries and terrible at fetching one row.** → [[databases/03-storage-and-page-layout|Row vs Column Storage]]

**The practical failure:** running analytics on your production OLTP database. A single `GROUP BY` over a year of orders scans millions of rows, evicts the buffer pool, and **your transactional latency collapses while it runs.**

**The standard answer:** a read replica for reporting, or an ETL/CDC pipeline into a warehouse. **HTAP** systems claim to do both; treat the claim sceptically.

## The landscape

| Family | Model | Good at | Weak at |
|---|---|---|---|
| **Relational** | tables, SQL | **general purpose**, joins, integrity | horizontal scale, flexible schema |
| **Document** | JSON docs | aggregates fetched together, flexible schema | joins, cross-document consistency |
| **Key-value** | K→V | **speed**, caching, sessions | queries other than "by key" |
| **Wide-column** | partitioned rows | **write throughput**, time series | ad-hoc queries, joins |
| **Graph** | nodes and edges | **traversals**, relationships | scans, aggregates |
| **Search** | inverted index | **full-text**, faceting | as a source of truth |
| **Time-series** | timestamped points | **append-heavy**, retention, downsampling | updates |

**Full tours of each in [[databases/nosql-reference|nosql-reference]].**

> **The default should be a relational database**, and the reason isn't conservatism. **You usually don't know your access patterns yet.** A relational schema plus indexes supports queries you haven't thought of; a document or wide-column model bakes today's access pattern into the storage layout, and changing it later means a migration.
>
> **Postgres in particular has absorbed most of the specialised use cases** — JSONB for documents, full-text search, PostGIS for geospatial, `pg_trgm` for fuzzy matching, TimescaleDB for time series, and arrays. **"Just use Postgres" is a defensible default for most systems**, and running one database well beats running four badly.

**When you genuinely need something else:**

- **Redis** — you need sub-millisecond reads on hot data, or you need the data structures (sorted sets for leaderboards, streams for queues)
- **Cassandra/ScyllaDB** — write throughput beyond what one node can take, with a known partition key
- **Elasticsearch** — real full-text relevance ranking, not `LIKE '%foo%'`
- **A graph database** — traversals of unbounded depth are the *primary* query. Recursive CTEs handle shallow cases fine
- **A column store** — analytical scans over hundreds of millions of rows

**Polyglot persistence** — using several — is legitimate and it costs you: more operational surface, more failure modes, and **consistency between stores becomes your problem.** → [[architecture/04-distributed-systems/README|Distributed Systems]]

## The NoSQL story

Worth knowing because the vocabulary is still around.

**Late 2000s.** Web-scale companies hit limits scaling relational databases horizontally. Joins and ACID across shards are genuinely hard, so a wave of systems dropped them for scale and availability.

**What was learned:**

**The scaling problems were real.** So were the solutions — partitioning, eventual consistency, and replication ideas that fed back into everything.

**"NoSQL" was never one thing.** A document store and a graph database have nothing in common but the absence of SQL.

**"Schemaless" mostly means the schema lives in your application**, unversioned and unenforced. It hasn't gone away; it's moved somewhere nobody can check it.

**Most applications never needed it.** The scale that motivated Dynamo and Bigtable is rare, and **a well-indexed Postgres on modern hardware handles far more than people assume** — tens of thousands of transactions per second on one machine.

**The systems converged.** MongoDB added transactions and joins. Cassandra added SQL-ish CQL. Relational databases added JSON columns and horizontal scaling. **"NewSQL" (CockroachDB, Spanner, TiDB, Vitess) is explicitly relational-with-horizontal-scale**, which is where the argument landed.

## Reading this track

**These 12 notes are the *internals* layer — how a database works underneath.** The vault's four reference files cover the surface in depth and are not repeated here:

| For | Read |
|---|---|
| **SQL syntax**, joins, window functions, CTEs | [[databases/sql-reference|sql-reference]] (4,200 lines) |
| **Schema design**, normalisation, keys, patterns | [[databases/database-design-reference|database-design-reference]] |
| **MySQL specifics**, admin, replication setup | [[databases/mysql-reference|mysql-reference]] |
| **MongoDB, Redis, Cassandra, Neo4j, Elasticsearch** | [[databases/nosql-reference|nosql-reference]] |

**02–05 are storage** — the relational model, pages, B-trees, LSM trees.
**06–07 are query processing** — the pipeline, join algorithms, the optimiser.
**08–10 are transactions** — ACID, MVCC, and crash recovery.
**11–12 are scaling and operating.**

**Prerequisites:** you should be able to write SQL. [[foundations/dsa/04-data-structures/05-trees/01-trees|Trees]] and [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]] make notes 03–05 much more concrete.

---

## Related
- [[databases/02-the-relational-model|The Relational Model]] — the theory under SQL
- [[databases/03-storage-and-page-layout|Storage and Page Layout]] — where the bytes go
- [[databases/sql-reference|SQL Reference]] — the syntax layer
- [[databases/README|Databases map]]
