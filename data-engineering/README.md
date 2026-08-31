# Data Engineering

**The plumbing between the systems that *run* a business and the systems that *analyse* it.** A 10-note course built Aug 2026, filling the gap between [[databases/README|databases]] (one system, transactional) and [[ai-ml/README|ai-ml]] (models over the reshaped data) — because a model is only as good as the pipeline feeding it, and nothing in the vault covered warehouses, Kafka, Spark, orchestration or dimensional modelling.

> **The one idea:** data engineering exists to separate **operational** systems (OLTP — row-oriented, transactional, user-facing) from **analytical** ones (OLAP — columnar, bulk, aggregated), and to move data reliably between them. Everything follows from that split and from one flip: **ELT** — load raw into a cheap elastic warehouse, then transform in place with SQL.

## Why this exists

The vault's gap audit named it: `databases/` is single-DB internals, `architecture/04-distributed-systems/` has the log and partitioning *theory*, `ai-ml/10-mlops/` touches serving — but **the discipline that assembles all of it into pipelines** had no home. It's a large, well-paid career track and the natural bridge between two domains the vault already covers well.

## Reading order

**01 is the map — read it first.** After that, 02–06 are the infrastructure (where data lives and how it moves) and 07–10 are the practice (how you shape and trust it).

1. [[data-engineering/01-what-data-engineering-is|what-data-engineering-is]] — **[Beginner]** — the operational/analytical split, the pipeline shape, and **ELT vs ETL, the change that defines the modern field**
2. [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses-lakes-and-lakehouses]] — **[Intermediate]** — **columnar storage (the idea underneath everything)**, storage/compute separation, and the lakehouse (Iceberg) that won — plus why single-node is quietly back
3. [[data-engineering/03-batch-and-streaming|batch-and-streaming]] — **[Intermediate]** — the **bounded/unbounded** distinction, the freshness-vs-complexity trade, event-time and watermarks, and why the industry is *unifying* the two
4. [[data-engineering/04-ingestion-and-change-data-capture|ingestion-and-change-data-capture]] — **[Intermediate]** — getting data in, and **CDC: read the database's own log instead of querying it** (which catches deletes and barely touches the source)
5. [[data-engineering/05-kafka-and-event-streaming|kafka-and-event-streaming]] — **[Advanced]** — **the log as one abstraction** that solves messaging, streaming, CDC transport and decoupling — and why the partition key is the design decision that matters
6. [[data-engineering/06-distributed-processing|distributed-processing]] — **[Advanced]** — MapReduce → Spark, the shuffle and skew, and **the honest question of whether you need a cluster at all** (usually not)
7. [[data-engineering/07-transformation-and-dbt|transformation-and-dbt]] — **[Intermediate]** — **dbt = SQL plus software engineering**: version control, tests, lineage, and automatic dependency ordering
8. [[data-engineering/08-orchestration|orchestration]] — **[Intermediate]** — DAGs, scheduling, failure handling, backfills, and **idempotency, the load-bearing discipline**
9. [[data-engineering/09-data-modelling-for-analytics|data-modelling-for-analytics]] — **[Intermediate]** — the star schema, **why analytics inverts normalisation**, grain, and Slowly Changing Dimensions
10. [[data-engineering/10-data-quality-governance-and-the-stack|data-quality-governance-and-the-stack]] — **[Intermediate]** — **why "the pipeline ran" isn't enough**, lineage, governance, and an honest read of the "modern data stack"

## If you only take three things

1. **Operational vs analytical, and ELT.** Get data out of the OLTP system into a columnar warehouse, then transform in place ([[data-engineering/01-what-data-engineering-is|01]]).
2. **Idempotency is non-negotiable** — every task must be safe to run twice, because pipelines retry and backfill ([[data-engineering/08-orchestration|08]]).
3. **You probably don't need a cluster.** Most data fits on one machine; measure before you reach for Spark ([[data-engineering/06-distributed-processing|06]]).

## Build it

[[data-engineering/projects|projects/]] — graded reps with a *done when* for each. **Start with the end-to-end mini-pipeline** (Postgres → DuckDB → dbt → a chart): it's a weekend, needs no cloud account, and makes the whole diagram concrete.

## Interview

[[data-engineering/interview/README|interview/]] — the data-engineering round: the operational/analytical split, ELT, CDC, idempotency, batch vs streaming, dimensional modelling, and the "would a database do?" judgement.

## Related
- [[databases/README|databases]] — the storage engines this builds on
- [[architecture/04-distributed-systems/README|distributed systems]] — every data tool at scale is one, with distributed failures
- [[ai-ml/README|ai-ml]] · [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]] — the main consumer; MLOps is largely data engineering
- [[devops/README|devops]] — the infrastructure these pipelines run on

*Source: [reference] — Aug 2026. A fast-moving field; treat specific tools as of-the-moment, the principles as durable.*
