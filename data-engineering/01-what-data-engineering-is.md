# What Data Engineering Is

**[Beginner]** — the discipline, why it exists as a role, and the one distinction everything else rests on.

## The kid version first

A company's data starts scattered — in the app's database, in payment records, in logs, in spreadsheets, in third-party tools. **None of it is in a shape you can ask questions of.** *"How much did we make per region last quarter, split by new vs returning customers?"* touches five systems, and none of them can answer it alone.

**Data engineering is the plumbing that moves data from where it's created to where it can be analysed, and reshapes it on the way** so that question becomes one query. Analysts, dashboards and ML models are the taps; data engineering is the pipes.

## The one distinction: operational vs analytical

Everything in this domain rests on splitting two workloads that a single database can't serve well at once:

| | **Operational (OLTP)** | **Analytical (OLAP)** |
|---|---|---|
| Question | "What's in *this* user's cart?" | "What's the average cart value by region this year?" |
| Access | A few rows, by key | Millions of rows, a few columns, aggregated |
| Writes | Constant, small | Bulk loads |
| Latency | Milliseconds, user-facing | Seconds to minutes, fine |
| Storage | **Row-oriented** | **Column-oriented** |
| System | Postgres, MySQL → [[databases/README\|databases]] | Snowflake, BigQuery → [[data-engineering/02-warehouses-lakes-and-lakehouses\|warehouses]] |

**You must not run heavy analytics on the operational database.** A `GROUP BY` over the whole orders table locks resources the checkout flow needs, and the row-oriented storage is the wrong shape for it anyway → [[data-engineering/09-data-modelling-for-analytics|why columnar]].

**So step one of data engineering is always: get the data *out* of the operational systems and into an analytical one.** That movement is the job.

## The shape of a data pipeline

Almost every data system, however grand its tooling, is this:

```
   SOURCES              INGEST          STORE            TRANSFORM        SERVE
   app databases        ──extract──►   warehouse /      ──clean, join,  ──►  dashboards
   event streams                       lake             aggregate,           ML features
   third-party APIs                                     model──►             reports
   files, logs                                                                reverse-ETL
```

**Extract → Load → Transform**, plus orchestration tying it together and quality checks throughout. Every section in this folder is one box in that diagram:

- **Ingest** → [[data-engineering/04-ingestion-and-change-data-capture|ingestion & CDC]]
- **Store** → [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses & lakes]]
- **Transform** → [[data-engineering/07-transformation-and-dbt|transformation & dbt]]
- **Orchestrate** → [[data-engineering/08-orchestration|orchestration]]
- **Model** → [[data-engineering/09-data-modelling-for-analytics|dimensional modelling]]
- **Quality** → [[data-engineering/10-data-quality-governance-and-the-stack|quality & governance]]

## ETL vs ELT — the shift that defines the modern field

**Old way (ETL):** Extract, **Transform**, then Load. Reshape the data on a separate server *before* loading, because the warehouse was expensive and slow.

**Modern way (ELT):** Extract, **Load**, then Transform. Dump the raw data into the warehouse first, then transform it *inside* the warehouse with SQL.

**Cloud warehouses caused this flip.** When compute is cheap, elastic and separated from storage, it's easier to load everything raw and transform in place — you keep the raw data (so you can re-transform when requirements change), and you use SQL instead of a separate processing framework → [[data-engineering/07-transformation-and-dbt|dbt]] exists entirely because of ELT.

**"ELT over ETL" is the single biggest change in the field in the last decade**, and it's why the tooling looks the way it does.

## Where it sits between databases and ML

```
   databases/          →   DATA ENGINEERING   →   ai-ml/
   (one system,            (many systems,          (models over
    row-oriented,           moved and reshaped      the reshaped
    transactional)          for analysis)           data)
```

- **Below it:** [[databases/README|databases]] — the storage engines, indexes and transactions data engineering moves data between and builds warehouses on
- **Beside it:** [[architecture/04-distributed-systems/README|distributed systems]] — because at scale, every data tool is a distributed system, and its failures are distributed-systems failures
- **Above it:** [[ai-ml/README|ai-ml]] — **models are only as good as the data pipeline feeding them.** "Garbage in, garbage out" is a data-engineering problem, and [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]] is largely data engineering wearing an ML hat

## Why it's a distinct role

It emerged because building reliable data pipelines is neither database administration nor software engineering nor data science, but overlaps all three:

- **From software engineering:** version control, testing, CI/CD, idempotency, code review — pipelines are code → [[concepts/04-best-practices/README|best practices]]
- **From databases:** SQL, storage internals, query optimisation, modelling → [[databases/README|databases]]
- **From distributed systems:** partitioning, replication, consistency, and the fact that **things fail partway through** → [[architecture/04-distributed-systems/README|distributed systems]]
- **Its own:** the tools (warehouses, Kafka, Spark, orchestrators), the modelling patterns, and a deep respect for **idempotency and reprocessing**, because pipelines break and must be re-runnable

## Key insight

**Data engineering exists to separate the systems that *run* the business from the systems that *analyse* it, and to keep data flowing reliably between them.** The operational/analytical split is the root of everything — different storage, different systems, different access patterns — and the modern field is defined by ELT: load raw into a cheap elastic warehouse, then transform in place with SQL. Learn that split and that flip, and the tooling stops looking like an arbitrary zoo.

## Related
- [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses, lakes and lakehouses]] — where analytical data lives
- [[data-engineering/03-batch-and-streaming|batch and streaming]] — the two ways it moves
- [[databases/README|databases]] — the operational side
- [[ai-ml/README|ai-ml]] — the main consumer

*Source: [reference] — Aug 2026.*
