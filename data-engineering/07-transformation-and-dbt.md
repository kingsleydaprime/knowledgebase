# Transformation and dbt

**[Intermediate]** — turning raw loaded data into trustworthy tables, and the tool that made it look like software engineering.

## The kid version first

Raw data in the warehouse is a mess: a `stripe_charges` table with cryptic columns, an `orders` table with test rows and duplicates, dates in three formats, and no notion of "revenue" anywhere. **Transformation is the work of turning that raw pile into clean, well-named, business-meaningful tables** an analyst can trust — `daily_revenue_by_region` with the test data removed and the currencies normalised.

**dbt** made this work look like real software: SQL files in version control, tested, documented, with dependencies figured out automatically.

## Why transformation is now a distinct layer

In the [[data-engineering/01-what-data-engineering-is|ELT model]], you load raw data first and transform it *inside* the warehouse afterward. That transformation step became large and important enough to be its own discipline — **"analytics engineering"** — sitting between data engineering (moving data) and data analysis (using it).

**The transformation layer is where business logic lives.** "What counts as an active user?" "How do we recognise revenue?" "Which orders are test data?" These definitions must live in *one* place, versioned and tested — otherwise every analyst reinvents them and every dashboard disagrees. That single-source-of-truth problem is what dbt solves.

## dbt — what it actually is

**dbt (data build tool) is SQL plus software-engineering discipline.** You write `SELECT` statements; dbt handles the rest:

```sql
-- models/marts/daily_revenue.sql
SELECT
    date_trunc('day', o.created_at) AS day,
    o.region,
    sum(o.amount) AS revenue
FROM {{ ref('stg_orders') }} o          -- ref() = a dependency on another model
WHERE o.is_test = false
GROUP BY 1, 2
```

- **`ref('stg_orders')`** is the key: it declares a dependency. dbt reads all your `ref`s, builds a **dependency graph (DAG)**, and runs models **in the right order automatically.** You never hand-order the pipeline
- **Each model is a `SELECT`** that dbt materialises as a table or view. You write transformation logic; dbt writes the `CREATE TABLE AS` boilerplate
- **Jinja templating** adds variables, loops and macros over SQL, so you can be DRY

**dbt doesn't move or process data itself** — it compiles your SQL and tells the *warehouse* to run it. It's a transformation *orchestrator and framework*, not an engine. All the compute is your warehouse's → [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouse]].

## What dbt brought that was genuinely new

Transformation used to be scattered SQL scripts, stored procedures, and undocumented cron jobs. dbt applied software practices to it, and *that's* the contribution:

- **Version control** — transformations are SQL files in git. Reviewed, diffed, rolled back → [[git/README|git]]
- **Testing** — assert data properties: `unique`, `not_null`, `accepted_values`, relationships, and custom SQL tests. **Data tests, in the pipeline, that fail the build** → [[data-engineering/10-data-quality-governance-and-the-stack|data quality]]
- **Documentation and lineage** — dbt generates docs and a visual DAG showing how every table derives from its sources. **"Where does this number come from?" becomes answerable**
- **Modularity** — reusable models and macros instead of copy-pasted SQL
- **Environments** — dev/staging/prod separation, so you test transformations before they hit production dashboards

**This is why dbt became ubiquitous:** it turned transformation from tribal knowledge into reviewed, tested, documented code.

## The standard layering

dbt projects converge on a layered structure, and it's worth adopting:

```
sources        raw loaded tables (stripe_charges, app_orders) — as-is
   ↓
staging (stg_) one model per source: rename, cast, clean. Light, 1:1 with source
   ↓
intermediate   business logic: joins, dedup, calculations
   ↓
marts          final, business-meaningful tables analysts and dashboards use
```

**Staging isolates you from source changes** (if Stripe renames a column, you fix one staging model, not fifty downstream); **marts are the clean public interface.** This layering is most of what "good dbt" means.

## Materialisation — the one real performance lever

Each model can be built as:

- **view** — a saved query, recomputed on every read. Cheap to build, slow to query. Good for staging
- **table** — fully computed and stored. Fast to query, rebuilt each run. Good for marts
- **incremental** — only process *new* rows since last run. **Essential for large tables** — rebuilding a billion-row table every hour is wasteful — and the source of most dbt complexity (you must define how to identify new rows and handle late-arriving updates)
- **ephemeral** — inlined into downstream models, never materialised

**Choosing materialisation is the main performance decision in dbt**, and incremental models are where the subtlety lives.

## The ecosystem

- **dbt Core** — open-source, free, the engine
- **dbt Cloud** — managed scheduling, IDE, docs hosting
- **SQLMesh** — a newer competitor with stronger handling of incremental logic and column-level lineage; worth watching
- **Warehouse-native** — some teams do this with plain scheduled SQL or the warehouse's own tooling, but dbt's testing and lineage are hard to give up

## Key insight

**dbt's contribution isn't SQL — it's applying software engineering to SQL:** version control, testing, documentation, modularity, and automatic dependency ordering via `ref()`. That turned transformation from scattered, untested, undocumented scripts into a reviewed and trustworthy codebase, and created the "analytics engineer" role in the process. The transformation layer matters because it's where business definitions live, and a definition of "revenue" or "active user" that isn't in one tested place is a definition every dashboard will get differently.

## Related
- [[data-engineering/09-data-modelling-for-analytics|dimensional modelling]] — how to structure the marts dbt produces
- [[data-engineering/10-data-quality-governance-and-the-stack|data quality]] — dbt tests as the first line
- [[data-engineering/08-orchestration|orchestration]] — what schedules dbt runs
- [[databases/sql-reference|SQL reference]] — the language it's all written in

*Source: [reference] — Aug 2026.*
