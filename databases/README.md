# Databases

How a database actually works underneath — pages, B-trees, query planning, MVCC, the write-ahead log — plus four deep reference files for the surface layer.

**Course: ~20,500 words across 14 notes** (built August 2026, including practice + solutions). **References: ~11,300 lines across 4 files** (older, and still the place to look up syntax). `[reference]` throughout.

> **Why the split.** The four reference files were already comprehensive on *what to type* — every join type, every window function, every normalisation form, every MongoDB operator. **What was missing was the layer underneath: why the planner chose that plan, why your update bloated the table, why the migration locked everything.** The numbered course is that layer, and it doesn't repeat the references.

## Two ways in

**Looking something up?** Go straight to a reference:

| For | File |
|---|---|
| **SQL syntax** — joins, window functions, CTEs, subqueries | [[databases/sql-reference\|sql-reference]] · 4,200 lines |
| **Schema design** — keys, normalisation, cardinality, patterns | [[databases/database-design-reference\|database-design-reference]] · 2,700 lines |
| **MySQL specifics** — admin, storage engines, replication setup | [[databases/mysql-reference\|mysql-reference]] · 2,100 lines |
| **MongoDB, Redis, Cassandra, Neo4j, Elasticsearch** | [[databases/nosql-reference\|nosql-reference]] · 2,000 lines |

**Want to understand what's happening?** Read the course, in order.

## The course

**02–05 are storage. 06–07 are query processing. 08–10 are transactions. 11–12 are scale and operations.**

1. [[databases/01-what-a-database-is|What a Database Is]] — **[Beginner → Intermediate]** — why not files, what ACID actually guarantees, OLTP vs OLAP, and an honest account of the NoSQL story
2. [[databases/02-the-relational-model|The Relational Model]] — **[Intermediate]** — Codd's data independence, relational algebra, and **why the optimiser's whole job is to never do what the algebra literally says**
3. [[databases/03-storage-and-page-layout|Storage and Page Layout]] — **[Intermediate → Advanced]** — pages, slotted layout, the buffer pool, row vs column storage, and **why a random UUID primary key hurts InnoDB specifically**
4. [[databases/04-b-trees-and-indexes|B-Trees and Indexes]] — **[Intermediate → Advanced]** — why B+ trees not binary trees, the leftmost prefix rule, index-only scans, and **when an index makes things worse**
5. [[databases/05-lsm-trees|LSM Trees]] — **[Advanced]** — the write-optimised alternative, compaction, bloom filters, and the RUM conjecture
6. [[databases/06-the-query-pipeline|The Query Pipeline]] — **[Intermediate → Advanced]** — parse → bind → rewrite → plan → execute. **A database is a compiler**
7. [[databases/07-join-algorithms-and-the-optimiser|Join Algorithms and the Optimiser]] — **[Advanced]** — the three joins, join ordering, cost estimation, and **the four ways estimates go wrong**
8. [[databases/08-transactions-and-acid|Transactions and ACID]] — **[Intermediate → Advanced]** — the anomalies precisely, isolation levels, and **why your default is weaker than your code assumes**
9. [[databases/09-mvcc-and-concurrency-control|MVCC and Concurrency Control]] — **[Advanced]** — how isolation is implemented, why Postgres needs `VACUUM`, transaction ID wraparound, and deadlocks
10. [[databases/10-durability-and-recovery|Durability and Recovery]] — **[Advanced]** — the WAL, ARIES, checkpoints, and **the ways `fsync` lies**
11. [[databases/11-replication-and-scaling|Replication and Scaling]] — **[Advanced]** — replicas, failover and split brain, partitioning vs sharding, connection pooling
12. [[databases/12-operating-a-database|Operating a Database]] — **[Intermediate → Advanced]** — migrations that don't cause outages, N+1, monitoring, and how to choose

## The things worth carrying

1. **A database is what you get when you take concurrency, crash safety, indexing, memory limits, atomicity and constraints seriously.** Not a fancy file format → [[databases/01-what-a-database-is|01]]
2. **Everything is pages**, and the page is the unit of I/O, caching and often locking → [[databases/03-storage-and-page-layout|03]]
3. **B+ trees win because they do hundreds of comparisons per block fetched.** Same argument as cache lines → [[databases/04-b-trees-and-indexes|04]]
4. **The leftmost prefix rule.** An index on `(a,b,c)` can't serve `WHERE b = 2`, and equality columns belong before range columns → [[databases/04-b-trees-and-indexes|04]]
5. **Estimated vs actual rows in `EXPLAIN ANALYZE` is the single most useful diagnostic.** Find the lowest node with a bad estimate → [[databases/07-join-algorithms-and-the-optimiser|07]]
6. **`random_page_cost = 4.0` assumes spinning disks.** Set it to 1.1 on SSDs — one line, large effect → [[databases/07-join-algorithms-and-the-optimiser|07]]
7. **You're probably running at Read Committed**, which permits lost updates and write skew. Most code assumes serializable → [[databases/08-transactions-and-acid|08]]
8. **Long transactions are the root of most MVCC problems** — bloat, blocked vacuum, lock pileups → [[databases/09-mvcc-and-concurrency-control|09]]
9. **`SET lock_timeout` before every migration.** One slow `SELECT` otherwise stalls the whole table → [[databases/12-operating-a-database|12]]
10. **Replication is not a backup.** A replica replicates `DROP TABLE` in milliseconds → [[databases/10-durability-and-recovery|10]]
11. **Scale up before you scale out.** Indexes, pooling, caching, a bigger machine — most systems never need more → [[databases/11-replication-and-scaling|11]]
12. **N+1 is the most common application-level database problem there is** → [[databases/12-operating-a-database|12]]

## Where this connects

| | |
|---|---|
| [[architecture/04-distributed-systems/README\|distributed systems]] | **Deliberate division of labour** — consensus, CAP, consistency models and distributed transactions live there. Note 11 is the operator's view |
| [[foundations/computer-architecture/08-the-memory-hierarchy\|memory hierarchy]] | Pages, buffer pools and B-tree fanout are the same argument one level up |
| [[foundations/compilers/README\|compilers]] | The query pipeline *is* a compiler pipeline |
| [[foundations/discrete-math/04-sets-relations-and-functions\|sets and relations]] | A table is a relation, literally — Codd's 1970 paper |
| [[backend/04-data-and-persistence/README\|backend/data]] | Using a database from an application |
| [[build-your-own-shit/06-your-own-database\|build-your-own-database]] | The build guide these notes explain |

## The honest note

**`[reference]`, with one qualification: the reference files predate this course and were written from wider use.** The numbered notes are the internals layer, assembled from the standard sources — Hellerstein & Stonebraker's *Architecture of a Database System*, *Designing Data-Intensive Applications*, Petrov's *Database Internals*, and the Postgres and InnoDB documentation. **Not from having operated a database at scale.**

**The tell to watch for:** the notes are confident about *mechanisms* and thinner on *judgement* — how bad a particular bloat number is in practice, when a plan regression is worth chasing, what a real incident feels like. **Those come from operating one.**

**What would close the gap, in rough order of value:**

1. **Run `EXPLAIN (ANALYZE, BUFFERS)` on your own slow queries** and find one where estimated and actual rows diverge. **Twenty minutes, and note 07 stops being abstract**
2. **Cause a deadlock deliberately.** Two `psql` sessions, opposite lock order. Read the log message
3. **Watch bloat happen** — update a table in a loop with vacuum off, watch `n_dead_tup` and the table size grow, then vacuum
4. **Do an expand–contract migration** on something real, including the separate contract release
5. **Restore from a backup, timed.** Your RTO is what a restore actually takes → [[databases/10-durability-and-recovery|10]]
6. **[[build-your-own-shit/06-your-own-database|Build a small database]]** — an append-only log, then a B-tree or LSM, then a WAL. `kill -9` mid-transaction and see the data survive. **The guide's verification hook is exactly the durability argument in note 10**
7. **The books:** *Database Internals* (Petrov) for storage and distribution; *Designing Data-Intensive Applications* (Kleppmann) for the systems view; *The Art of PostgreSQL* for the practitioner's; and the Postgres source, which is unusually readable

**What's missing:** ~~exercises~~ — **closed by notes 13–14 (Aug 2026)**; worked schema examples beyond what the design reference has, anything on data warehousing and dimensional modelling, stream processing, vector databases and embeddings (a real gap given this vault's AI/ML material), and time-series databases in depth.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[databases/13-practice-exercises|Practice Exercises]] — fourteen exercises against a real database — a 9,327× index speedup, N+1, deadlocks, MVCC bloat, and killing the server mid-write
- [[databases/14-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[data-engineering/README|data engineering]] — moving analytical data *between* databases: warehouses, Kafka, dbt, pipelines
- [[databases/projects|Projects]] — **the reps for this domain**, graded 🟢🟡🔴 with a *done when* for each
- [[databases/interview/README|Databases — Interview Prep]] — what gets asked about all this
- [[architecture/04-distributed-systems/README|Distributed Systems]] — the theory beyond one machine
- [[backend/README|Backend]] — where databases get used
- [[BUILD-PLAN|Build Plan]]
