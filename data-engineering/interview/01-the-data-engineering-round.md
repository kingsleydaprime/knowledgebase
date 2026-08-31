# The Data Engineering Round

**[Intermediate → Advanced]** — what gets asked, what a strong answer covers, and the detail that separates memorised from understood. 🔥 marks the ones asked constantly.

## Fundamentals

**🔥 Q: Walk me through a data pipeline.**

**A strong answer covers:** sources → ingest (extract/load) → store (warehouse/lake) → transform → serve. Plus orchestration tying it together and quality checks throughout. Name the operational/analytical split as the reason it exists — get data out of the OLTP system into a columnar analytical one.

**The detail worth adding:** **ELT, not ETL** — load raw first, transform in the warehouse — and *why*: cloud warehouses separated storage from compute, so keeping raw data and transforming in place with SQL became cheaper than a separate transform server → [[data-engineering/01-what-data-engineering-is|01]].

**🔥 Q: Why not just run analytics on the production database?**

**A strong answer covers:** it competes with the operational workload (a `GROUP BY` over all orders locks resources the checkout needs), and row-oriented OLTP storage is the wrong shape for column-heavy aggregation.

**The detail worth adding:** **columnar storage** — analytical queries read a few columns over many rows, so storing columns together means reading far less data and compressing far better. This is the single reason analytical systems are fast → [[data-engineering/02-warehouses-lakes-and-lakehouses|columnar]].

**Q: Warehouse vs lake vs lakehouse?**

**A strong answer covers:** warehouse = structured, columnar, SQL, managed; lake = cheap raw files in object storage, any format, but "a bucket of files isn't a database"; lakehouse = lake files + a transaction layer that gives them warehouse behaviour.

**The detail worth adding:** the **open table format** (Iceberg/Delta) adds ACID, time travel, schema evolution and *upserts/deletes* over Parquet — and because it's open, the data isn't locked to one engine. **Iceberg winning matters because it decouples data from compute.**

## Movement

**🔥 Q: How do you extract only what changed from a source database?**

**A strong answer covers:** a watermark query (`WHERE updated_at > last_run`) is the obvious way, but it **requires a reliable `updated_at`, misses hard deletes, and has boundary issues.**

**The detail worth adding, and it's the answer they want:** **CDC** — read the database's own change log (WAL/binlog) instead of querying it. It captures deletes, runs near-real-time, and **puts almost no load on the source** because it's not running queries → [[data-engineering/04-ingestion-and-change-data-capture|CDC]]. Debezium is the standard.

**Q: Batch or streaming — how do you decide?**

**A strong answer covers:** freshness vs complexity. Batch is bounded, simple, cheap; streaming is unbounded, complex, always-on. **Default to batch** — most "real-time" needs are actually "within a few minutes." Reach for streaming when the value of the data decays in seconds (fraud, trading, alerting).

**The detail worth adding:** the real difficulty of streaming is **event time vs processing time and late data** — an event that happened at 2pm but arrives at 3pm must still land in the 2pm window, which is what watermarks manage → [[data-engineering/03-batch-and-streaming|batch and streaming]].

**🔥 Q: What is Kafka and why is it everywhere?**

**A strong answer covers:** a distributed, durable, **replayable log**. Unlike a queue, it keeps every event and each consumer tracks its own position — so you can add a consumer later and replay history. One abstraction serves messaging, streaming ingestion, CDC transport and service decoupling.

**The detail worth adding:** **ordering is guaranteed only within a partition**, so the partition key is a real design decision — key by user and one user's events stay ordered but a hot user creates skew; key randomly and you lose per-entity ordering → [[data-engineering/05-kafka-and-event-streaming|Kafka]].

## Processing

**🔥 Q: When would you use Spark, and when wouldn't you?**

**A strong answer covers:** Spark when the data genuinely doesn't fit on one machine (terabyte-plus) or you need distributed streaming/ML. **And crucially — often you wouldn't.** A cloud VM has terabytes of RAM; DuckDB, Polars and warehouses handle a shocking amount on one node.

**The detail worth adding, and this is what impresses:** **"most data fits on one machine, so measure before you distribute."** Reaching for a cluster by reflex buys a distributed system's complexity and the shuffle tax for a single-machine problem. Naming the ["big data is dead"](https://motherduck.com/blog/big-data-is-dead/) argument shows current awareness → [[data-engineering/06-distributed-processing|distributed processing]].

**Q: Why is my Spark job slow?**

**A strong answer covers:** almost always a **shuffle or skew.** A shuffle moves data across the network to regroup it (needed by `groupBy`/`join`); skew is when one key has most of the rows, so one machine does most of the work while the rest idle. Fixes: broadcast joins for small sides, better partition keys, salting skewed keys.

## Practice

**🔥 Q: What does idempotency mean here, and why does it matter?**

**A strong answer covers:** running a task twice gives the same result as once. It matters because **pipelines retry and backfill constantly** — a non-idempotent load double-counts on retry. The pattern: each run owns and fully replaces a partition (delete-then-insert, or upsert on a key) rather than appending.

**The detail worth adding:** **it's the load-bearing discipline of the whole domain** — the worst data incidents are non-idempotent pipelines that triple a month's revenue on a backfill. "Every task must be safe to run twice" → [[data-engineering/08-orchestration|orchestration]].

**Q: What does dbt actually do?**

**A strong answer covers:** it's SQL plus software engineering — you write `SELECT`s, dbt handles dependency ordering (via `ref()`), materialisation, testing, documentation and lineage. It doesn't process data itself; it compiles SQL and tells the *warehouse* to run it.

**The detail worth adding:** its contribution is **applying version control, testing and modularity to transformation**, turning scattered scripts into reviewed, trusted code — and the staging → intermediate → marts layering is where dimensional models get built → [[data-engineering/07-transformation-and-dbt|dbt]].

**🔥 Q: Design a dimensional model for [some business].**

**A strong answer covers:** facts (the measures you sum — one row per event, narrow) and dimensions (the context you group by — wide, descriptive). A star schema, joined fact-to-dimension. **State the grain explicitly** — what one fact row represents.

**The detail worth adding:** **Slowly Changing Dimensions Type 2** — when a customer's city changes, add a new dimension row with valid-from/to dates rather than overwriting, or last year's "revenue by city" silently rewrites itself. This is the "did you think about history" question → [[data-engineering/09-data-modelling-for-analytics|dimensional modelling]].

**Q: How do you know your data is correct?**

**A strong answer covers:** "the pipeline ran" isn't enough — data can be wrong while the job is green. Check freshness (did a source silently stop?), volume (did we get the expected rows?), schema, and value/distribution. dbt tests as the first line, data observability for anomalies.

**The detail worth adding:** **stale-but-green is the sneakiest failure** — everything succeeds, the numbers are just quietly out of date. That's why freshness monitoring is separate from pipeline monitoring → [[data-engineering/10-data-quality-governance-and-the-stack|data quality]].

## The judgement question

**Q: A team wants a Kafka + Spark + Airflow + lakehouse platform. What do you ask?**

**A strong answer covers:** how big is the data, actually? What freshness does the business need? How big is the team? **Most of the time the answer is a warehouse (or DuckDB) + dbt + one orchestrator + tests** — the ten-tool "modern data stack" is frequently over-engineered for data that fits on one machine.

**The detail worth adding:** this is testing **calibration** — whether you match the stack to the problem or to the blog posts. Naming the cost and operational burden of Kafka and Spark, and knowing the industry is *consolidating* back toward integrated and single-node tools, is the senior answer → [[data-engineering/10-data-quality-governance-and-the-stack|the stack, honestly]].

## What this round tests

1. **Do you understand *why* the pieces exist** — the operational/analytical split, ELT, columnar — or just their names?
2. **Idempotency and failure** — the operational maturity that separates someone who's run pipelines from someone who's read about them
3. **Calibration** — reaching for the simplest thing that works, not the most impressive stack

## Related
- [[data-engineering/README|the data engineering course]] · [[data-engineering/projects|projects]]
- [[databases/interview/README|databases interview]] — the adjacent round
- [[INTERVIEW|Interview Prep Index]]
