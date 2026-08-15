# Operating a Database

**[Intermediate → Advanced]** — Migrations that don't cause outages, ORMs and N+1, what to monitor, and how to choose.

## Migrations

**Schema changes on a live system**, and the commonest self-inflicted outage.

**The rule that governs everything here:**

> **`ALTER TABLE` takes an `ACCESS EXCLUSIVE` lock, and it must wait for existing queries to finish — while every new query queues behind it.** One slow `SELECT` turns a millisecond migration into a full table stall. → [[databases/09-mvcc-and-concurrency-control|Locking]]

**Always:**

```sql
SET lock_timeout = '3s';
ALTER TABLE ...;
```

**Fail fast and retry rather than accumulating a queue.**

**What's cheap and what isn't** (Postgres 11+):

| Operation | Cost |
|---|---|
| `ADD COLUMN` with no default | **instant** — metadata only |
| `ADD COLUMN` with a **constant** default | **instant** (11+) |
| `ADD COLUMN` with a **volatile** default | **rewrites the whole table** |
| `DROP COLUMN` | instant (space reclaimed by vacuum) |
| `ALTER TYPE` widening (`int`→`bigint`) | **full rewrite** |
| `ADD CONSTRAINT ... NOT VALID` then `VALIDATE` | **two cheap steps** |
| `CREATE INDEX` | **blocks writes** |
| `CREATE INDEX CONCURRENTLY` | **no write lock**, slower, can fail and leave an invalid index |

**The expand–contract pattern** for anything that would otherwise require downtime:

```
1. EXPAND    add the new column/table, nullable
2. BACKFILL  in batches, with pauses
3. DUAL WRITE application writes both old and new
4. MIGRATE   switch reads to the new
5. CONTRACT  drop the old — in a LATER deploy
```

**The point: every intermediate state is deployable and reversible.** And **step 5 must be a separate release**, because during a rolling deploy both old and new application versions are running simultaneously — **dropping a column the old version still reads breaks it mid-rollout.**

**Backfill in batches:**

```sql
UPDATE big_table SET new_col = old_col
WHERE id BETWEEN :lo AND :hi;   -- 10k rows, then sleep
```

**One giant `UPDATE` holds locks, generates enormous WAL, and bloats the table.** Batch it, pause between batches, and let vacuum keep up.

**Tools:** `pt-online-schema-change` and `gh-ost` (MySQL), `pg_repack` (Postgres). **`gh-ost` is notable for using the binlog rather than triggers**, so it doesn't add write overhead to the original table.

**Keep migrations in version control, forward-only, and tested against a production-sized copy.** A migration that takes 200ms on 10,000 rows may take 40 minutes on 100 million.

## ORMs and N+1

**The most common application-level database problem, by a wide margin.**

```python
for order in Order.objects.all():        # 1 query
    print(order.customer.name)           # N queries — one per order
```

**101 round trips instead of 1.** Each individually fast; the total is dominated by network latency.

**The fix is eager loading:**

| ORM | Fix |
|---|---|
| Django | `select_related()` (join) / `prefetch_related()` (second query) |
| SQLAlchemy | `joinedload()` / `selectinload()` |
| Rails | `includes()` |
| Hibernate | `JOIN FETCH`, `@BatchSize` |

> **Two joins is usually better than two queries; ten joins is usually worse than two queries.** A join multiplying rows across several one-to-many relationships produces a Cartesian explosion — the same customer row repeated hundreds of times. **`prefetch_related`/`selectinload` issue a second query with `WHERE id IN (...)` instead**, which is often faster despite being "more queries".

**Detect N+1 automatically** — `django-debug-toolbar`, `bullet` (Rails), or a query-count assertion in tests. **A test that fails when a page issues more than N queries catches the regression before production**, and it's cheap to add.

**Other ORM problems:**

**`SELECT *` by default** — pulling TOASTed columns you don't need. Use `.only()`/`.defer()`.

**Hidden transactions.** Many ORMs wrap requests in a transaction. **Long request = long transaction = blocked vacuum.** → [[databases/09-mvcc-and-concurrency-control|MVCC]]

**Generated SQL you've never read.** `EXPLAIN` what your ORM actually emits — it's frequently not what you pictured.

**Migrations that lock.** ORM-generated migrations rarely use `CONCURRENTLY` or `NOT VALID`. **Review them.**

> **The honest position on ORMs:** they're genuinely good for CRUD, mapping, and migrations, and genuinely bad at complex queries. **Use the ORM for the 90% and drop to raw SQL for the rest** — most ORMs support this well, and fighting the ORM to express a window function is wasted effort.

## Monitoring

**What to watch, roughly in order of usefulness:**

**Slow queries.** `pg_stat_statements` is the single most valuable extension — total time, mean time and call count per normalised query. **Sort by total time, not mean**: a 5ms query called a million times costs more than a 2-second query called twice, and it's the one people miss.

**Connections** — active, idle, and **idle in transaction**. That last one is the leading indicator of blocked vacuum and lock pileups.

**Cache hit ratio** — below ~99% on OLTP means your working set doesn't fit.

**Replication lag** — in bytes and seconds.

**Locks and waits** — `pg_locks`, and blocked-query detection.

**Bloat and dead tuples** — `pg_stat_user_tables`, and `last_autovacuum` timestamps.

**Transaction ID age** — `age(datfrozenxid)`. **The wraparound alarm.** → [[databases/09-mvcc-and-concurrency-control|VACUUM]]

**Disk space** — including WAL. **A full WAL disk stops the database**, and abandoned replication slots are the usual cause.

**Checkpoint frequency** — `log_checkpoints = on`. Frequent checkpoints mean `max_wal_size` is too small.

**Set `log_min_duration_statement`** to log anything slow, and `auto_explain` to capture plans for them. → [[devops/10-observability/README|Observability]]

## Security

**The basics, stated because they're skipped:**

**Parameterised queries, always.** String concatenation into SQL is SQL injection, and it remains the top web vulnerability after twenty-five years. **ORMs and prepared statements do this correctly by default; `f"SELECT ... {user_input}"` does not.** → [[cybersecurity/04-web-security/README|Web Security]]

**Least privilege.** The application user needs `SELECT`/`INSERT`/`UPDATE`/`DELETE`, not `SUPERUSER` and not DDL. **Separate the migration user from the runtime user.**

**Encryption in transit** — TLS, and verify the certificate.

**Encryption at rest** — disk-level, or column-level for specific sensitive fields.

**Don't log queries containing secrets.** Slow-query logs capture parameter values.

**Audit access to sensitive tables**, and separate production credentials from everything else.

**Restrict network access.** A database reachable from the internet will be found — Shodan scans for exposed Postgres, MongoDB and Redis continuously, and unauthenticated instances are compromised within hours.

## Choosing a database

**The decision framework**, compressed:

**Start with Postgres.** It is the correct default for the large majority of applications: mature, extremely capable, well-documented, permissively licensed, and it has absorbed most specialised use cases (JSONB, full-text, geospatial, time series). **Running one database well beats running four badly.**

**Choose otherwise for a specific, measured reason:**

| Reason | Consider |
|---|---|
| Sub-millisecond reads on hot data | **Redis** |
| Write throughput beyond one node, known partition key | **Cassandra / ScyllaDB** |
| Real full-text relevance ranking | **Elasticsearch** |
| Analytical scans over hundreds of millions of rows | **ClickHouse / DuckDB** |
| Unbounded-depth graph traversals as the primary query | **Neo4j** |
| Horizontal scale *with* SQL and transactions | **CockroachDB / TiDB / Vitess** |
| Document model genuinely fits, flexible schema | **MongoDB** |

**Full tours of each in [[databases/nosql-reference|nosql-reference]] §3–8, and a decision framework in §8.**

**Questions to ask before adopting anything:**

- **What are the access patterns?** If you don't know, that argues for relational
- **What's the actual data volume and growth rate?** Measured, not imagined
- **What consistency do you need?** Where can you tolerate staleness?
- **Who operates it at 3am?** A database nobody on the team knows is a liability
- **What's the migration path off it** if it's wrong?

> **The most expensive database decisions are the ones made for anticipated scale that never arrived.** Systems are far more often over-engineered for scale than under-engineered — and the cost is paid daily, in complexity, while the benefit stays hypothetical.

## Practical notes

**Read `pg_stat_statements` weekly.** It tells you where the time goes, and the answer is usually surprising.

**Set `statement_timeout` and `idle_in_transaction_session_timeout`.** Two settings that prevent a large class of incidents.

**`lock_timeout` before every migration.**

**Test restores, not just backups.** → [[databases/10-durability-and-recovery|Backups]]

**Keep a production-sized staging copy** (anonymised) for testing migrations and plans. **Plan behaviour at 10 million rows cannot be inferred from 10,000.**

**Version-control everything** — schema, migrations, configuration, and the extensions you rely on.

**Know your defaults.** Isolation level, `random_page_cost`, `work_mem`, connection limits. **Several are wrong for modern hardware.**

---

## Related
- [[databases/11-replication-and-scaling|Replication and Scaling]] — when one machine isn't enough
- [[databases/interview/01-sql-modelling-and-internals|Databases interview]] — what gets asked about all this
- [[devops/10-observability/README|Observability]] — the monitoring layer
- [[databases/README|Databases map]]
