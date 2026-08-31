# Orchestration

**[Intermediate]** — the conductor that runs all the pieces in order, on schedule, and correctly when things fail.

## The kid version first

A data platform has dozens of steps: extract from Stripe, load to the warehouse, run dbt transformations, refresh the ML features, send the report. Some steps depend on others — you can't transform data you haven't loaded. Some run hourly, some nightly. Some fail and need retrying. Some need to be re-run for last week because a bug corrupted the numbers.

**Orchestration is the system that runs all of this in the right order, on the right schedule, retries what fails, and lets you re-run history when you need to.** It's the conductor; everything else is an instrument.

## The DAG

The central abstraction is the **Directed Acyclic Graph** — tasks as nodes, dependencies as edges, no cycles:

```
extract_stripe ──┐
extract_app  ────┼──► load_warehouse ──► dbt_run ──► refresh_features ──► send_report
extract_events ──┘                              └──► update_dashboard
```

**The orchestrator reads the DAG and runs tasks respecting dependencies** — `load_warehouse` waits for all three extracts; the two downstream branches run in parallel once `dbt_run` finishes. You declare the *shape*; the orchestrator handles ordering, parallelism, and what to do when a node fails.

**"Pipelines as code"** — the DAG is defined in a programming language (usually Python), version-controlled and reviewed, not clicked together in a UI → [[git/README|git]].

## The three things an orchestrator must do

**1. Schedule.** Run the DAG on a cadence (cron: "every hour", "daily at 2am") or trigger it on an event (a file arrived, an upstream finished). More sophisticated orchestrators are **data-aware** — run when the *data* a task depends on is fresh, not just when the clock says.

**2. Handle failure.** Tasks fail — a source API is down, the warehouse times out, data is malformed. The orchestrator must:
- **Retry** with backoff (transient failures often self-heal)
- **Alert** when retries are exhausted → [[data-engineering/10-data-quality-governance-and-the-stack|monitoring]]
- **Not run downstream tasks** whose inputs failed (don't build a report on data that didn't load)
- **Let you resume from the failure point**, not restart the whole DAG

**3. Backfill.** Re-run the pipeline for a past period — because you found a bug, added a column, or a source was late. **This is where idempotency becomes non-negotiable.**

## Idempotency — the load-bearing discipline

**A task is idempotent if running it twice produces the same result as running it once.** In data engineering this isn't a nicety — it's the property that makes the whole system operable, because tasks *will* be retried and backfilled.

```
NOT idempotent:   INSERT yesterday's orders     ← re-run → DUPLICATE rows
Idempotent:       DELETE yesterday's partition, then INSERT   ← re-run → same result
                  or: MERGE/upsert on a key                    ← re-run → same result
```

**The pattern:** each run should *own* a slice of the output (a date partition) and fully replace it, rather than appending. Then a retry or backfill overwrites cleanly instead of double-counting.

**Non-idempotent pipelines are the source of the worst data-engineering incidents** — a retried job that double-counts revenue, a backfill that triples a month's numbers. Design every task so that re-running it is *always safe*. This is the single most important habit in the domain, and it connects directly to [[data-engineering/04-ingestion-and-change-data-capture|idempotent loads]] and [[data-engineering/05-kafka-and-event-streaming|at-least-once + idempotent]].

## The tools

| | Note |
|---|---|
| **Apache Airflow** | The incumbent standard. Python DAGs, huge ecosystem, battle-tested. **Also creaky** — scheduling-centric, awkward for passing data between tasks, heavy to operate |
| **Dagster** | The modern challenger. **Asset-centric** — you model the *data assets* you're producing, not just tasks, so it knows what data exists and whether it's fresh. Better testing and local development |
| **Prefect** | Pythonic, lighter, dynamic workflows. Lower ceremony than Airflow |
| **Mage / Kestra** | Newer, config- or UI-forward options |
| **Temporal** | Durable execution for complex, long-running workflows — more general than data-specific |
| **dbt's own scheduler** | For dbt-only shops, sometimes enough on its own |

**Airflow vs Dagster is the live debate.** Airflow has the ecosystem and the jobs; Dagster has the better model (assets over tasks) and developer experience. **New projects increasingly pick Dagster**; existing infrastructure runs Airflow, and will for years.

## The anti-pattern this replaces

**Cron plus scripts.** A crontab of shell scripts *is* an orchestrator — a terrible one. It has no dependency awareness (script B runs whether or not A succeeded), no retries, no visibility (did last night's run work? who knows), no backfill, and no alerting. **Every data team starts here and outgrows it painfully**, usually after a silent failure corrupts a week of reports. Reaching for a real orchestrator early is one of the higher-leverage decisions in the field.

## Key insight

**Orchestration is the conductor that turns a pile of scripts into a reliable system — scheduling, failure handling, and backfills — and idempotency is the discipline that makes all three safe.** The DAG expresses dependencies as code so the orchestrator can order, parallelise and recover; but none of that helps if re-running a task double-counts your data, which is why "every task must be safe to run twice" is the habit the whole domain rests on. The tooling is shifting from task-centric Airflow toward asset-centric Dagster, but the principles are stable.

## Related
- [[data-engineering/04-ingestion-and-change-data-capture|ingestion]] — idempotent loads, the same idea at the source
- [[data-engineering/07-transformation-and-dbt|transformation and dbt]] — a major thing orchestrators run
- [[data-engineering/10-data-quality-governance-and-the-stack|data quality]] — where alerts go
- [[devops/06-ci-cd/README|CI/CD]] · [[architecture/03-architectural-patterns/README|architectural patterns]] — pipelines-as-code

*Source: [reference] — Aug 2026.*
