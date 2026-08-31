# Data Engineering — Projects

*The domain where **one end-to-end pipeline teaches more than reading the whole course** — because the failures that define the field (a source that stops, a re-run that double-counts, data that's stale but green) only show up when you've built and operated something. And most of it runs free on your laptop with DuckDB.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **The end-to-end mini-pipeline** — extract from a Postgres (or a public API), load into **DuckDB**, transform with **dbt**, and end at a chart. **Done when:** one command rebuilds the whole thing from raw to chart, and a dbt test fails the build if a key isn't unique. **Do this first** — a weekend, no cloud account, and it makes [[data-engineering/01-what-data-engineering-is|the whole diagram]] concrete.

- 🟢 **Prove idempotency to yourself** — take the pipeline above and run the load twice. Watch it double-count. Then rewrite it as delete-partition-then-insert (or an upsert) and run it twice again. **Done when:** running the load any number of times gives the same result → [[data-engineering/08-orchestration|idempotency]]. **The single most important habit in the domain, learned by breaking it.**

- 🟢 **Star-schema a messy dataset** — take a flat, denormalised dataset (a Kaggle sales export) and model it as facts and dimensions in dbt, with an explicit grain. **Done when:** "revenue by category by month" is a two-join query, and you can state what one fact row represents → [[data-engineering/09-data-modelling-for-analytics|dimensional modelling]].

- 🟡 ⭐ **CDC from a live database** — run Postgres with logical replication, point **Debezium** at it, and stream inserts/updates/**deletes** to a target. **Done when:** you delete a row in Postgres and watch the delete propagate — the thing a watermark query would miss → [[data-engineering/04-ingestion-and-change-data-capture|CDC]].

- 🟡 **Orchestrate it** — put the pipeline under **Dagster** (or Airflow): a DAG, a schedule, retries, and a **backfill** for a past date range. **Done when:** you can kill a task mid-run and resume from the failure point, and backfill last week without corrupting this week → [[data-engineering/08-orchestration|orchestration]].

- 🟡 **Handle Slowly Changing Dimensions** — model a customer whose city changes, Type 2. **Done when:** last year's "revenue by city" report stays correct after the customer moves — history doesn't silently rewrite itself.

- 🟡 **Add data quality that catches a real failure** — instrument freshness and volume checks, then simulate a source that sends 10% of normal rows or stops updating. **Done when:** the check fires *before* the bad data reaches the chart, even though the pipeline "succeeded" → [[data-engineering/10-data-quality-governance-and-the-stack|data quality]].

- 🟡 **A streaming word-count with windows** — consume a stream (Kafka or a generator), aggregate over a tumbling window using **event time**, and handle a deliberately late event. **Done when:** a late event lands in the correct time bucket, not the one it arrived in → [[data-engineering/03-batch-and-streaming|streaming]].

- 🔴 ⭐ **A lakehouse on object storage** — write Parquet to S3 (or MinIO locally), register it as **Iceberg**, and query the same tables from DuckDB *and* Spark. Do an upsert and a time-travel query. **Done when:** two engines read one Iceberg table, and you can query it "as of" before your upsert → [[data-engineering/02-warehouses-lakes-and-lakehouses|lakehouse]].

- 🔴 **Feed an ML model** — build a feature pipeline that produces training data for one of the [[ai-ml/projects|ai-ml projects]], with the transformation versioned in dbt. **Done when:** the model retrains from a reproducible, tested feature table → [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]].

## If you only do one

**The end-to-end mini-pipeline, then break its idempotency on purpose.** Together that's a weekend on your laptop, and it takes you from "I read about pipelines" to having felt the exact failure — a re-run that double-counts — that the whole discipline is organised to prevent.

## Related
- [[data-engineering/README|the data engineering course]] · [[data-engineering/interview/README|interview bank]]
- [[databases/projects|databases projects]] — the layer below · [[ai-ml/projects|ai-ml projects]] — the layer above
- [[project-ideas|Project Ideas]] — the vault-wide index
