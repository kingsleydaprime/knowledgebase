# Warehouses, Lakes and Lakehouses

**[Intermediate]** — where analytical data lives, why columnar storage changes everything, and the architecture that won.

## The kid version first

You need somewhere to put all the data you've extracted, in a form that answers analytical questions fast. Three answers evolved:

- **Warehouse** — a giant, structured, SQL database tuned for analytics. Tidy, fast, expensive, opinionated.
- **Lake** — a cheap bucket of raw files (S3). Holds *anything*, structured or not, but a bucket of files isn't a database.
- **Lakehouse** — files in the cheap bucket, plus a layer that makes them behave like a warehouse. **The current consensus.**

## Columnar storage — the idea underneath all of it

The single most important concept in analytical storage. **Row storage keeps each record together; column storage keeps each *field* together.**

```
Row-oriented (OLTP):     [id=1,name=Ada,age=36][id=2,name=Bo,age=29]...
Column-oriented (OLAP):  ids: [1,2,...]  names: [Ada,Bo,...]  ages: [36,29,...]
```

**Why this transforms analytics:**

- **Read only the columns you need.** `SELECT AVG(age)` touches one column, not the whole table. For a query over 3 of 200 columns, that's a ~60× reduction in data read
- **Compression is dramatic.** A column of ages is all similar small integers — it compresses far better than mixed rows. Analytical data is often 5–10× smaller columnar
- **Vectorised execution.** The CPU processes a column as a tight array, using SIMD → [[foundations/computer-architecture/README|the memory hierarchy]] loves this

**The trade:** fetching one *whole row* is slow (you gather from every column), which is exactly why OLTP uses row storage and OLAP uses columnar. Same data, opposite layout, for opposite questions → [[data-engineering/01-what-data-engineering-is|the operational/analytical split]].

**Parquet** is the ubiquitous columnar file format; **ORC** is the other. Both are what lakes actually store.

## The data warehouse

A managed, columnar, SQL-first analytical database. The big three:

| | Note |
|---|---|
| **Snowflake** | **Separated storage and compute** — the innovation everyone copied. Spin up isolated compute "warehouses" against shared storage, scale each independently. Not a cloud-native original but the one that popularised the model |
| **BigQuery** | Google's serverless warehouse — no clusters to manage, you pay per query scanned. Extremely low-ops |
| **Redshift** | Amazon's — older, node-based, now with serverless options. More knobs |
| **Databricks SQL** | The lakehouse vendor's warehouse-shaped surface |

**The separation of storage and compute is the key modern property.** Historically the warehouse coupled them (Redshift's original design), so scaling storage meant scaling compute and vice versa. Decoupling them means storage is cheap object storage, compute is elastic and per-workload, and **this is exactly what made ELT affordable** → [[data-engineering/01-what-data-engineering-is|ELT]].

## The data lake

**Raw files in cheap object storage** (S3, GCS, Azure Blob), in open formats (Parquet, JSON, CSV, images).

**The appeal:** dirt cheap, holds *any* data type (a warehouse wants tabular), no schema required up front (**schema-on-read** — impose structure when you query, not when you store), and no vendor lock-in — it's your files in open formats.

**The problem — "data swamp":** a bucket of files is not a database. No transactions, no schema enforcement, no easy updates or deletes, no indexes. Concurrent writers corrupt each other; a half-finished job leaves partial files that queries then read. **The early data-lake era drowned in ungoverned, undocumented, untrustworthy files.**

## The lakehouse — the architecture that won

**Files in the cheap lake, plus a metadata/transaction layer that gives them warehouse behaviour.** You get the lake's cost and openness *and* the warehouse's reliability. This is the current mainstream architecture.

The magic is the **open table format** — a layer over Parquet files that adds a transaction log:

| Format | Origin |
|---|---|
| **Apache Iceberg** | Netflix. **Winning the format war** — adopted by Snowflake, BigQuery, Databricks, AWS. The safe bet in 2026 |
| **Delta Lake** | Databricks. Mature, tightly integrated with Spark |
| **Apache Hudi** | Uber. Strong for streaming upserts |

What the transaction log buys you over raw Parquet:

- **ACID transactions** — concurrent writers don't corrupt each other; a failed job doesn't leave partial data visible → [[databases/08-transactions-and-acid|ACID]]
- **Time travel** — query the table as of last Tuesday; the log records every version
- **Schema evolution** — add or change columns safely
- **Upserts and deletes** — genuinely hard on raw files, routine with a table format (and needed for GDPR "delete this user")
- **Compaction** — merge the "small files problem" (thousands of tiny files kill query performance)

**The strategic point:** because Iceberg is an open format, **your data isn't locked into one vendor's warehouse.** Snowflake, Spark, DuckDB and Trino can all query the same Iceberg tables. This is why Iceberg winning matters — it decouples the data from the engine.

## The recent counter-current: single-node is back

Worth knowing, because it pushes against the "everything must be distributed" assumption:

**Most datasets are smaller than people think, and hardware got huge.** A modern server has terabytes of RAM. **DuckDB** — an in-process columnar engine ("SQLite for analytics") — queries Parquet and Iceberg on one machine, fast, with no cluster. The ["Big Data is Dead"](https://motherduck.com/blog/big-data-is-dead/) argument is that the median analytical workload fits comfortably on one node, and a distributed cluster is expensive complexity you probably don't need.

**Don't reach for Spark and a cluster by default.** DuckDB or a warehouse handles a shocking amount → [[data-engineering/06-distributed-processing|distributed processing]].

## Choosing

- **Just starting / small team** → a cloud warehouse (BigQuery or Snowflake). Lowest ops, and you may never outgrow it
- **Large scale, many data types, cost-sensitive** → lakehouse with Iceberg
- **Genuinely small data** → DuckDB + Parquet on object storage. Cheap and fast
- **Avoid** → a raw data lake with no table format. That's the swamp

## Key insight

**Columnar storage is why analytical systems are fast, and the separation of storage from compute is why the modern stack is affordable** — everything else is a consequence. The architecture converged on the lakehouse: cheap open files (Parquet) plus a transaction log (Iceberg) that makes them behave like a warehouse without the lock-in. And the useful contrarian note is that most data fits on one machine, so a distributed cluster should be a decision, not a default.

## Related
- [[data-engineering/06-distributed-processing|distributed processing]] — Spark, and when you actually need it
- [[data-engineering/09-data-modelling-for-analytics|dimensional modelling]] — how to structure what's in the warehouse
- [[databases/03-storage-and-page-layout|storage and page layout]] — row vs columnar at the engine level
- [[databases/05-lsm-trees|LSM-trees]] — the write-optimised cousin

*Source: [reference] — Aug 2026. Table-format landscape moves fast; verify Iceberg adoption before betting on it.*
