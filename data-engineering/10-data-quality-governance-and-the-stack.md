# Data Quality, Governance, and the Stack

**[Intermediate]** — keeping data trustworthy, and an honest look at the "modern data stack."

## The kid version first

A pipeline can run perfectly and still produce garbage: a source starts sending prices in cents instead of dollars, a currency column goes null, a duplicate load doubles the revenue. **The pipeline succeeds; the data lies.** And a dashboard nobody trusts is worse than no dashboard — people quietly go back to their own spreadsheets.

**Data quality is the work of catching bad data before it reaches the people who act on it**, and governance is knowing where data came from, who can see it, and what it means.

## Why "the pipeline ran" isn't enough

Software testing checks that *code* is correct. Data quality checks that *data* is correct — a different problem, because the data changes every day and the code doesn't:

- **Freshness** — is the data up to date, or did a source silently stop? **A pipeline that succeeds on stale data is the sneakiest failure** — everything is green, the numbers are just quietly wrong
- **Volume** — did we get roughly the expected number of rows? A load that's 10% of normal means a broken source, even though it "succeeded"
- **Schema** — did a column disappear, change type, or get renamed upstream? → [[data-engineering/05-kafka-and-event-streaming|schema registry]]
- **Values** — are prices positive, are emails valid, are enums in range, is the primary key unique?
- **Distribution** — did the *shape* of the data shift? Average order value tripling overnight is either a great day or a bug, and usually a bug

**The freshness and volume checks catch the failures that monitoring the pipeline itself misses**, which is why data observability is its own thing.

## Testing and observability

**In-pipeline tests** — assertions that fail the build:

- **dbt tests** — `unique`, `not_null`, `accepted_values`, relationships, plus custom SQL. **The first line of defence, and nearly free** → [[data-engineering/07-transformation-and-dbt|dbt]]
- **Great Expectations / Soda** — richer declarative data-quality suites with profiling and reporting

**Data observability** — monitoring data health continuously, like [[devops/10-observability/README|application observability]] but for data:

- **Anomaly detection** on freshness, volume and distribution — alert when today doesn't look like history
- **Monte Carlo, Anomalo** and similar are the commercial category
- **The point:** catch "the data looks wrong" automatically, before an executive catches it in a board meeting

**The principle: fail loudly and early.** A pipeline that stops and alerts on bad data is far better than one that cheerfully loads it and lets a wrong number reach a decision → [[data-engineering/08-orchestration|alerting]].

## Lineage — where did this number come from?

**Data lineage traces every value back through its transformations to its sources.** "This revenue figure comes from `mart_revenue`, built from `stg_orders` and `stg_refunds`, loaded from the Postgres `orders` table via CDC."

Why it's essential:
- **Debugging** — a wrong number in a dashboard: lineage shows every upstream table to check
- **Impact analysis** — before changing a source column, see everything downstream that breaks
- **Trust** — analysts can see how a metric was computed, so they believe it

dbt generates column-level lineage; **OpenLineage** is the emerging open standard; catalogs (below) visualise it across tools.

## Governance

The unglamorous, increasingly mandatory side:

- **Cataloguing** — a searchable inventory of what data exists, what it means, and who owns it (**DataHub**, **Amundsen**, Unity Catalog). Without one, a large org has hundreds of tables nobody can find or interpret
- **Access control** — who can see what. **PII** (personal data) needs restriction, masking, or tokenisation → [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|privacy]]
- **Compliance** — **GDPR/CCPA "delete this user everywhere"** is genuinely hard across a lake of immutable files, which is a real reason [[data-engineering/02-warehouses-lakes-and-lakehouses|lakehouse table formats]] (which support deletes) matter
- **Data contracts** — a newer idea: a *formal, enforced agreement* between the team producing data and the teams consuming it about schema and semantics, so an upstream app deploy can't silently break every downstream pipeline. **The most promising recent development** for the eternal "someone changed the source and broke everything" problem

## The "modern data stack" — honestly

Around 2020 a standard architecture crystallised: **Fivetran (ingest) → Snowflake/BigQuery (warehouse) → dbt (transform) → BI tool (serve)**, with an orchestrator and observability around it. Cloud-native, modular, each best-of-breed.

**What's genuinely good:** it's modular (swap any piece), managed (less ops), and SQL-centric (accessible to analysts, not just engineers). It democratised a capability that used to need a large specialist team.

**The honest criticisms, which the field is now voicing:**
- **Tool sprawl and cost.** "Modern data stack" often means 8+ SaaS subscriptions, and the bills — especially warehouse compute and Fivetran's per-row pricing — surprise people badly
- **Over-engineering.** Many teams assembled a ten-tool platform for data that fits in **DuckDB and a few Python scripts** → [[data-engineering/06-distributed-processing|the single-node case]]. **Match the stack to the actual data size and team, not to the blog posts**
- **Consolidation is happening.** The pendulum is swinging back toward integrated platforms (Databricks, Snowflake absorbing more of the stack) and simpler single-node tooling. The "assemble ten best-of-breed SaaS tools" era is being questioned

**The right first stack for most teams is small:** a warehouse (or DuckDB), dbt, one orchestrator, and dbt's own tests. Add pieces when a real need appears, not preemptively.

## Key insight

**A pipeline that runs successfully can still produce data that lies, so data quality — freshness, volume, schema, distribution — is a separate discipline from pipeline monitoring, and the sneakiest failures (stale data, a shrunk load) are the ones that stay green while being wrong.** Lineage makes numbers debuggable and trustworthy; governance makes them findable and compliant; and the sober lesson about the "modern data stack" is that it's frequently over-assembled — most teams need a warehouse, dbt, an orchestrator and some tests, and should add tools only when the data actually demands them.

## Related
- [[data-engineering/07-transformation-and-dbt|transformation and dbt]] — tests as the first line
- [[data-engineering/08-orchestration|orchestration]] — where quality alerts fire
- [[devops/10-observability/README|observability]] — the application-monitoring analogue
- [[data-engineering/01-what-data-engineering-is|what data engineering is]] — the whole picture

*Source: [reference] — Aug 2026. The stack landscape moves fast; treat specific tools as of-the-moment.*
