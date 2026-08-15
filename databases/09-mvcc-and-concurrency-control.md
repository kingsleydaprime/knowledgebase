# MVCC and Concurrency Control

**[Advanced]** — How isolation is actually implemented, why Postgres needs vacuum, and where deadlocks come from.

## Two approaches

**Pessimistic — two-phase locking.** Acquire locks before touching data, hold until commit.

**The problem: readers block writers and writers block readers.** A long analytical query blocks every update to the rows it reads. **Concurrency collapses under mixed workloads.**

**Optimistic — multiversion concurrency control (MVCC).** Keep multiple versions of each row. Readers see the version that was current when their snapshot began.

> **The MVCC rule, and it's the whole idea:**
>
> **Readers never block writers. Writers never block readers.**
>
> **Writers still block writers** on the same row — that part is unavoidable.

**Essentially every modern database uses MVCC**: Postgres, InnoDB, Oracle, SQL Server (optionally), CockroachDB, MongoDB (WiredTiger).

## How MVCC works

**Each row version carries visibility metadata:**

| Field | Meaning |
|---|---|
| `xmin` | transaction that **created** this version |
| `xmax` | transaction that **deleted/superseded** it (or null) |

**A transaction has a snapshot** — the set of transaction IDs committed at the moment it began.

**A version is visible if** its `xmin` is committed and in your snapshot, **and** its `xmax` is null or not in your snapshot.

**An `UPDATE` does not modify in place.** It writes a **new version** and sets `xmax` on the old one. **The old version stays** until nobody can see it any more.

```
 Row id=1, updated twice:

 version A: xmin=100, xmax=200   balance=100   ← old snapshots see this
 version B: xmin=200, xmax=300   balance=90
 version C: xmin=300, xmax=null  balance=80    ← current
```

**A transaction that started when 200 was the latest committed sees version B**, regardless of what's happened since. **That's a consistent snapshot with no locks taken.**

## Postgres vs InnoDB

**Both use MVCC. They store the old versions in completely different places, and every operational difference follows from that.**

| | **Postgres** | **InnoDB** |
|---|---|---|
| Old versions live | **in the table itself** | **in the undo log** (separate) |
| Update writes | **a whole new row version** | new row in place + undo record |
| Reading an old version | it's just another tuple | **reconstruct by applying undo** |
| Cleanup | **`VACUUM`** | purge thread |
| Indexes on update | **all indexes updated** (unless HOT) | **only affected indexes** |

**The consequences:**

**Postgres updates are expensive.** A new row version means **every index must be updated**, even for columns that didn't change. **HOT (Heap-Only Tuple) updates avoid this** when no indexed column changed *and* the new version fits on the same page — which is why fill factor matters on update-heavy tables. → [[databases/03-storage-and-page-layout|Fill factor]]

**Postgres tables bloat.** Dead versions occupy space until vacuumed.

**InnoDB's long-running transactions bloat the undo log instead**, and reading very old versions gets progressively slower as more undo records must be applied.

**Neither is strictly better** — they're different trades, and knowing which you're on tells you which operational problem to expect.

## VACUUM

**Postgres-specific, and the source of most Postgres operational pain.**

**What it does:**

**Reclaims dead tuples**, marking space reusable (not returned to the OS — that needs `VACUUM FULL`, which locks the table exclusively).

**Updates the visibility map**, which is what enables **index-only scans**. → [[databases/04-b-trees-and-indexes|Index-only scans]]

**Updates statistics** (with `ANALYZE`).

**Freezes old transaction IDs** — and this one is critical.

> **Transaction ID wraparound.** Postgres XIDs are 32-bit and wrap after ~2 billion transactions. **Rows must be "frozen" before their XID becomes ancient, or they'd suddenly appear to be from the future and become invisible** — silent data loss.
>
> **Postgres protects against this by refusing new writes** as wraparound approaches:
> ```
> ERROR: database is not accepting commands to avoid wraparound data loss
> ```
> **This has taken down production systems** — famously Sentry in 2015, and Mailchimp. **It happens when autovacuum has been unable to keep up or has been disabled**, and the recovery requires single-user mode. **Monitor `age(datfrozenxid)`.** Postgres 9.6+ handles it far better and the risk is much lower now, but the failure mode is worth knowing.

**Autovacuum** runs it automatically, triggered by the fraction of changed rows. **The defaults are conservative for large tables** — 20% of a billion-row table is 200 million dead rows before it triggers. **Tune `autovacuum_vacuum_scale_factor` down for big tables**, or set per-table thresholds.

**What blocks vacuum:**

- **A long-running transaction** — vacuum cannot remove versions that any open snapshot might need. **One forgotten `BEGIN` in an idle session blocks cleanup across the entire database**
- **Idle-in-transaction sessions** — hence `idle_in_transaction_session_timeout`
- **Abandoned replication slots** — a disconnected replica whose slot still exists holds back WAL *and* vacuum
- **Long queries on replicas** with `hot_standby_feedback = on`

**Monitor:** `pg_stat_user_tables` for `n_dead_tup` and `last_autovacuum`, and `pg_stat_activity` for long transactions.

## Locking

**MVCC removes read locks. Write locks remain.**

**Row-level locks:**

| Lock | Taken by | Conflicts with |
|---|---|---|
| `FOR UPDATE` | explicit, or `UPDATE`/`DELETE` | other row locks |
| `FOR NO KEY UPDATE` | `UPDATE` not touching a key | `FOR UPDATE` |
| `FOR SHARE` | explicit | `FOR UPDATE` |
| `FOR KEY SHARE` | **foreign key checks** | `FOR UPDATE` |

**Table-level locks** range from `ACCESS SHARE` (a plain `SELECT`) to `ACCESS EXCLUSIVE` (`DROP`, `TRUNCATE`, most `ALTER TABLE`).

> **The DDL trap.** `ALTER TABLE` takes an `ACCESS EXCLUSIVE` lock — and **it must wait for existing queries to finish, while queueing behind it every new query.** So a migration behind one slow `SELECT` stalls the entire table.
>
> **Always set `lock_timeout` before a migration.** Fail fast and retry rather than accumulating a queue:
> ```sql
> SET lock_timeout = '3s';
> ALTER TABLE ...;
> ```
> **This one line prevents a large fraction of migration-caused outages.**

**InnoDB adds gap locks and next-key locks** at Repeatable Read — locking the *gaps between* index entries to prevent phantoms. **They cause deadlocks that surprise people**, because you can conflict on rows that don't exist.

## Deadlocks

**Two transactions each holding a lock the other wants.**

```
T1: locks row A ─────────► wants row B
T2: locks row B ─────────► wants row A
```

**The database detects the cycle in the wait-for graph and kills one** — the *deadlock victim*. **This is a normal outcome, not a bug**, and your application must retry.

**Prevention:**

**Access rows in a consistent order.** If every transaction touches accounts in ascending ID order, **no cycle can form.** This is the structural fix and it's worth enforcing as a convention.

**Keep transactions short** — less time holding locks.

**Take the strongest lock first**, rather than upgrading a shared lock to exclusive mid-transaction — lock upgrades are a classic deadlock source.

**Use `SELECT ... FOR UPDATE` deliberately** rather than relying on incidental locking order.

**Debug them:** Postgres logs deadlocks with both queries by default; `SHOW ENGINE INNODB STATUS` gives the last one in MySQL. **The log tells you exactly which two statements conflicted**, which usually makes the ordering fix obvious.

## Practical notes

**Long transactions are the root of most MVCC problems** — bloat, blocked vacuum, undo growth, lock waits. **Set `idle_in_transaction_session_timeout`.**

**Monitor bloat and dead tuples.** `pg_stat_user_tables`, and `pgstattuple` for detail.

**Tune autovacuum for large tables.** The defaults are wrong at scale.

**Watch for replication slots left by removed replicas** — a silent, slow-motion disk-filling failure.

**Understand which engine you're on.** Postgres bloat and InnoDB undo growth are different problems with different symptoms.

**Retry on deadlock and serialization failure.** Both are expected.

**Set `lock_timeout` before DDL.** Always.

---

## Related
- [[databases/08-transactions-and-acid|Transactions and ACID]] — the guarantees this implements
- [[databases/10-durability-and-recovery|Durability and Recovery]] — the log underneath
- [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — locks one layer down
- [[databases/README|Databases map]]
