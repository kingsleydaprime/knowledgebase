# Ingestion and Change Data Capture

**[Intermediate]** — getting data *in*, and the technique that solved the hardest part of it.

## The kid version first

Before you can analyse data, you have to copy it out of wherever it lives — the app's database, a payment provider's API, a stream of clicks, a pile of files — into your warehouse. That copying is **ingestion**, and it sounds trivial until you ask: *how do I copy only what changed since last time, without hammering the source system or missing anything?*

The clever answer, for databases, is **Change Data Capture** — read the database's own internal change log instead of querying it.

## The sources

Data comes from four broad places, each with its own extraction method:

| Source | How you extract |
|---|---|
| **Operational databases** (Postgres, MySQL) | Full load, incremental query, or **CDC** |
| **Third-party SaaS** (Stripe, Salesforce, ad platforms) | Their REST APIs, usually via a managed connector |
| **Event streams** (clicks, IoT, app telemetry) | Consume from Kafka / Kinesis → [[data-engineering/05-kafka-and-event-streaming\|streaming]] |
| **Files** (CSV, logs, exports, Parquet drops) | Read from object storage on a schedule |

## Full vs incremental extraction

**Full load** — copy the entire source table every run. Simple, always correct, and **catastrophic at scale** — re-copying a billion-row table nightly wastes time, money and source-database resources.

**Incremental** — copy only what changed since last time. The obvious way is a **watermark column**: `WHERE updated_at > last_run_time`. It works, with real caveats:

- **Requires a reliable `updated_at`** that every write updates. Many tables don't have one, or code paths forget to set it
- **Misses hard deletes** — a deleted row has no `updated_at` to catch. Your warehouse keeps a row the source deleted, silently, forever
- **Clock and boundary issues** — a row written *during* your extraction, at exactly the watermark, is missed or duplicated

Those caveats — especially missing deletes — are exactly what CDC fixes.

## Change Data Capture — the elegant solution

**Every transactional database already keeps a log of every change it makes**, for its own crash recovery and replication — Postgres's WAL, MySQL's binlog → [[databases/10-durability-and-recovery|durability and recovery]]. **CDC reads that log** and turns each committed change into an event:

```
Postgres WAL:  INSERT id=5 ... → { op: insert, id: 5, after: {...} }
               UPDATE id=5 ... → { op: update, id: 5, before, after }
               DELETE id=5     → { op: delete, id: 5, before }     ← DELETES ARE CAPTURED
```

**Why CDC is the right answer:**

- **Captures deletes** — the thing watermark queries miss
- **Near-real-time** — changes stream out as they commit, not on a nightly poll
- **Near-zero load on the source** — reading the log doesn't run queries against the production database. **This is the killer property** — analytical extraction stops competing with the operational workload → [[data-engineering/01-what-data-engineering-is|the operational/analytical split]]
- **Complete and ordered** — every change, in commit order, nothing missed

**Debezium** is the standard open-source CDC engine; it reads WAL/binlog and publishes to Kafka. Managed connectors (Fivetran, Airbyte) offer CDC without running Debezium yourself.

**The catch:** CDC gives you a *stream of changes*, and reconstructing the *current state* of a table from an infinite change stream requires an **upsert** into a target that supports it — which is exactly what lakehouse table formats provide, and one reason they exist → [[data-engineering/02-warehouses-lakes-and-lakehouses|upserts]].

## The connector ecosystem

The unglamorous reality: **most ingestion is a solved, buy-not-build problem.** Extracting from Stripe or Salesforce means dealing with their pagination, rate limits, auth quirks and schema changes — tedious, and identical for every company. So managed connectors dominate:

| | |
|---|---|
| **Fivetran** | Managed, hundreds of connectors, "it just works," priced per row. The default for teams with budget |
| **Airbyte** | Open-source alternative, self-hostable, community connectors |
| **Meltano / Singer** | Open protocol (taps and targets) for pipelines-as-code |
| **Debezium** | The CDC specialist |

**Writing your own connector for a common source is usually a mistake** — you'll rebuild pagination and rate-limit handling that a connector already solved, and maintain it forever as the API changes. Build custom extraction only for genuinely bespoke or internal sources.

## The delivery guarantees, briefly

Ingestion inherits the distributed-systems delivery problem:

- **At-least-once** — every record arrives, possibly duplicated. **The common default** — pair it with idempotent loads (upsert on a key) so duplicates don't double-count
- **At-most-once** — no duplicates, but records can be lost. Rarely acceptable
- **Exactly-once** — every record once. Ideal, expensive, and often *approximated* as "at-least-once + idempotent target," which is good enough and much cheaper → [[data-engineering/05-kafka-and-event-streaming|Kafka delivery]]

**Design every load to be idempotent** — running it twice produces the same result. It's the single most important ingestion habit, because pipelines *will* retry and replay → [[data-engineering/08-orchestration|idempotency]].

## Key insight

**Ingestion's hard part is capturing *change* efficiently, and CDC solves it by reading the database's own change log instead of querying it** — which catches deletes, runs in near-real-time, and puts almost no load on the source. For everything that isn't a database, ingestion is mostly a buy-not-build connector problem, and the one discipline that ties it all together is idempotency: assume every load will run twice, and make sure that's harmless.

## Related
- [[data-engineering/05-kafka-and-event-streaming|Kafka and event streaming]] — where CDC events flow
- [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses and lakes]] — the destination, and why upserts matter
- [[databases/10-durability-and-recovery|durability and recovery]] — the WAL that CDC reads
- [[data-engineering/08-orchestration|orchestration]] — idempotency and retries

*Source: [reference] — Aug 2026.*
