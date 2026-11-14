# Data Engineering

## What data engineering is

**Data engineering is building the systems that collect a company's data from everywhere it's created, clean it up, and deliver it to the people and programs that analyse it.**

A business runs on many systems: the app's database, the payment provider, the website's visit logs, the support tool. Each is built to do its own job quickly, not to answer questions like "which customers from last year's campaign are still buying?". Asking that of the live app database would slow it down for real users, and the answer needs data from several systems anyway.

So data engineers build **pipelines**: automatic processes that copy data out of those systems, combine and tidy it, and load it into a **data warehouse**, a database built for analysis rather than for running the app. Analysts, dashboards and machine learning models then work from the warehouse.

## What you'll be able to do

By the end you will be able to:
- explain why the systems that run a business are kept separate from the ones that analyse it;
- choose where data should live: a warehouse, a "data lake" of raw files, or something in between;
- decide between processing data in scheduled batches or continuously as it arrives;
- copy changes out of a live database without slowing it down;
- move data with Kafka, and process large amounts with Spark (and judge when you don't need it);
- transform data with dbt, schedule pipelines safely, and design tables for analysis;
- check that the data is actually right, not just that the pipeline ran.

## Where to start

**Before you start:** you should know [[databases/00-your-first-sql|basic SQL]] and what a [[databases/index|database]] does. Some Python helps.

Read note 01 first; it's the map. Notes 02–06 are where data lives and how it moves; notes 07–10 are how you shape it and make sure it's right.

1. [[data-engineering/01-what-data-engineering-is|What Data Engineering Is]]: the split between running a business and analysing it, the shape of a pipeline, and the modern habit of loading raw data first and transforming it inside the warehouse.
2. [[data-engineering/02-warehouses-lakes-and-lakehouses|Warehouses, Lakes and Lakehouses]]: where analytical data lives, why storing it column by column makes analysis fast, and why a single machine is often enough again.
3. [[data-engineering/03-batch-and-streaming|Batch and Streaming]]: processing data in scheduled chunks versus continuously, and the trade between fresh data and complexity.
4. [[data-engineering/04-ingestion-and-change-data-capture|Ingestion and Change Data Capture]]: getting data in, and copying changes by reading the database's own change log, which also catches deletions.
5. [[data-engineering/05-kafka-and-event-streaming|Kafka and Event Streaming]]: Kafka, a shared, ordered log of events that many systems write to and read from.
6. [[data-engineering/06-distributed-processing|Distributed Processing]]: splitting huge jobs across many machines with Spark, and the honest question of whether you need to at all (usually not).
7. [[data-engineering/07-transformation-and-dbt|Transformation and dbt]]: transforming data with SQL, plus the good habits of software engineering: version control, tests and clear dependencies.
8. [[data-engineering/08-orchestration|Orchestration]]: scheduling pipeline steps, handling failures, re-running past days, and making every step safe to run twice.
9. [[data-engineering/09-data-modelling-for-analytics|Data Modelling for Analytics]]: designing warehouse tables for fast, simple analysis, which works almost the opposite way to app databases.
10. [[data-engineering/10-data-quality-governance-and-the-stack|Data Quality, Governance and the Stack]]: making sure the data is correct, knowing where every number came from, and an honest look at today's popular tools.

## Practice

- [[data-engineering/projects|Projects]]: hands-on tasks with a clear "done when". Start with the small end-to-end pipeline (a Postgres database, into DuckDB, transformed with dbt, shown as a chart). It takes a weekend and needs no cloud account.
- [[data-engineering/interview/index|Data engineering interview prep]].

## Key ideas to remember

1. **Keep analysis off the live app database.** Copy the data to a warehouse built for analysis. → [[data-engineering/01-what-data-engineering-is|01]]
2. **Every pipeline step must be safe to run twice,** because pipelines retry and re-run past days. → [[data-engineering/08-orchestration|08]]
3. **You probably don't need a cluster of machines.** Most data fits on one; measure before reaching for Spark. → [[data-engineering/06-distributed-processing|06]]
4. **"The pipeline ran" doesn't mean the data is right.** Test the data itself. → [[data-engineering/10-data-quality-governance-and-the-stack|10]]

## Related

- [[databases/index|Databases]]: the storage engines this builds on.
- [[data-analysis/index|Data Analysis]]: the people who use the warehouse to answer questions.
- [[ai-ml/index|AI & ML]] and [[ai-ml/02-ml-engineer/10-mlops/index|MLOps]]: the biggest users of these pipelines.
- [[architecture/04-distributed-systems/index|Distributed Systems]]: the theory behind every tool here at scale.

---

## About this course

- **Size:** 10 notes, written in August 2026 to fill the gap between the databases and AI courses.
- **A fast-moving field:** specific tools change often; the principles last.
