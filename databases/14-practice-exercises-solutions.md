# Practice Exercises — Solutions

> **[Intermediate]** · Worked answers to [[databases/13-practice-exercises|note 13]]. Measured on SQLite (Python 3.14, in-memory, 500k rows) and PostgreSQL 16, August 2026.

---

## Part A — Storage and indexes

### 1. Earn the index

Measured — 500,000 rows, 200 point lookups by `email`:

```
EXPLAIN before:  SCAN users
EXPLAIN after :  SEARCH users USING COVERING INDEX idx_email (email=?)

no index   6.002 s
index      0.0006 s
speedup    9,327×
```

**Nearly four orders of magnitude, from one `CREATE INDEX`.**

Without the index, each lookup reads all 500,000 rows: 200 × 500,000 = 100 million row inspections. With it, each is a B-tree descent of about $\log_{\text{fanout}}(500{,}000) \approx 3$ page reads.

**Note the plan says *covering*** — the index contains `email` and, implicitly, the rowid, so SQLite answered `SELECT id` from the index alone without touching the table. That's exercise 5, for free.

**The plan changing is more reliable evidence than the clock**, because a warm cache can make a bad plan look acceptable → [[databases/04-b-trees-and-indexes|note 04]].

### 2. Read the plan

| Query | Plan | Why |
|---|---|---|
| `WHERE id = 5` | seek | Primary key is the clustered B-tree |
| `WHERE city = 'lagos'` (no index) | **scan** | Nothing to descend |
| `WHERE id BETWEEN 10 AND 99` | **range seek** | B-trees keep keys ordered — seek once, walk the leaves |
| `WHERE email LIKE '%foo%'` | **scan** | See below |
| `WHERE email LIKE 'foo%'` | seek | Prefix is usable |

**A leading wildcard defeats a B-tree because the tree is ordered by the *start* of the string.** With `'foo%'` you can descend to the `foo` prefix and walk; with `'%foo'` the matching rows are scattered arbitrarily through the ordering, so there's nothing to descend to.

**That's why substring search needs a different structure** — a trigram index, or a full-text index → [[databases/06-the-query-pipeline|note 06]].

### 3. Kill your own index, four ways

- **`WHERE lower(email) = 'x'`** — the index stores `email`, not `lower(email)`. *(Fix: an expression index on `lower(email)`.)*
- **`WHERE user_id = '42'`** (text vs integer) — an implicit cast is applied to the *column*, same problem
- **`LIKE '%foo'`** — as above
- **Selecting >20–30% of the table** — the planner **deliberately** chooses a scan

**The general rule for the first three: an index on a column can only answer questions about that column *as stored*. Any transformation of the column defeats it.**

**The fourth is not a defeat — it's correct.** An index lookup gives a row *pointer*; fetching many scattered rows means many random reads. Above a threshold, reading the table sequentially is genuinely faster, because sequential I/O massively outperforms random I/O → [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|IOPS]]. **A planner that always used an index would be slower.**

### 4. Composite index column order

`INDEX(a, b)` is sorted by `a`, then by `b` **within each `a`**.

| Query | Uses index? |
|---|---|
| `WHERE a = 1` | **Yes** |
| `WHERE a = 1 AND b = 2` | **Yes, fully** |
| `WHERE b = 2` | **No** (usually a scan) |

**The leftmost-prefix rule.** Analogy: a phone book sorted by (surname, forename). Finding "Smith" is easy; finding everyone called "John" is not, because the Johns are scattered under every surname.

**Practical consequence: `INDEX(a,b)` makes `INDEX(a)` redundant, but not `INDEX(b)`.** Column order is a design decision, not a formality.

### 5. Covering index

When every column a query needs is *in the index*, the database skips the table entirely — Postgres calls it **Index Only Scan**, SQLite **COVERING INDEX**.

The saved I/O is the **heap fetch**: normally the index gives a row pointer and the engine then reads that row's page, which is a random read per row. Covering removes it.

**The trade:** wider indexes are larger, slower to write, and consume more cache. Adding columns to an index for one query can slow every insert → [[databases/12-operating-a-database|note 12]].

---

## Part B — Queries and joins

### 6. The optimiser changes its mind

Small table joined to large: expect a **hash join** (build a hash of the small side, stream the large) or a **nested loop with an index** if the join column is indexed and selective.

After deleting 90% and re-analysing, the plan often flips — commonly to a **merge join** or a different join order.

**The statistic driving it is the estimated row count**, from the table's histogram and distinct-value counts. Stale statistics are the single most common cause of a plan that was fine yesterday and terrible today — **the data changed and nobody told the planner** → [[databases/07-join-algorithms-and-the-optimiser|note 07]].

Hence autovacuum/auto-analyze, and hence `ANALYZE` after a bulk load.

### 7. N+1

```
loop version:   101 queries
join version:     1 query
```

Typical wall-clock difference is 10–100×, and it is **worse over a network** than locally, because you pay round-trip latency 101 times. **On a laptop with a local database it may look fine — which is exactly why this ships.**

**It's usually invisible in code**, because the ORM makes `order.customer.name` look like an attribute access rather than a query → [[backend/frameworks/python/02-django/README|Django]]. The fix is `select_related` / `JOIN FETCH` / `include`, and the defence is **watching the query count**, not the wall clock.

### 8. Make the planner wrong

Correlated columns are the reliable route: `WHERE city = 'Lagos' AND country = 'Nigeria'`. The planner assumes **independence**, so it multiplies selectivities — estimating far fewer rows than actually match, because every Lagos row is a Nigeria row.

`EXPLAIN ANALYZE` shows `rows=12` next to `actual rows=4000`.

**Consequences of a bad estimate:** a nested loop chosen where a hash join was needed (catastrophic on the real row count), or an under-sized hash table spilling to disk.

**Most slow queries are estimation failures, not algorithm failures.** Fixes: `CREATE STATISTICS` for correlated columns (Postgres 10+), or restructuring the query.

---

## Part C — Transactions and concurrency

### 9. Dirty read

**In PostgreSQL you cannot produce one.** Requesting `READ UNCOMMITTED` is accepted and silently gives you `READ COMMITTED`.

**That's the exercise's real answer.** Postgres's MVCC means a transaction reads a *snapshot*; uncommitted rows have an invisible transaction id and simply aren't in it. **There is no mechanism by which a dirty read could occur** — the level is unimplementable rather than unimplemented.

**The lesson: isolation levels are a standard, and each database implements a different subset with different mechanisms.** "REPEATABLE READ" does not mean the same thing in Postgres, MySQL/InnoDB and SQL Server. **Read your database's documentation, not the standard** → [[databases/08-transactions-and-acid|note 08]].

### 10. Non-repeatable read and phantom

**READ COMMITTED:** each *statement* gets a fresh snapshot, so re-reading a row after another transaction commits shows the new value — a **non-repeatable read**. A range query returning new rows is a **phantom**.

**REPEATABLE READ:** the snapshot is taken once per *transaction*, so both re-reads return the original values. In Postgres this also prevents phantoms (its REPEATABLE READ is snapshot isolation, stronger than the standard requires).

**The cost is serialisation failures.** At REPEATABLE READ and above, a conflicting concurrent write causes `could not serialize access` — **and your application must retry.** Choosing a higher level without retry logic converts a correctness problem into an availability problem.

### 11. Deadlock

```
ERROR: deadlock detected
DETAIL: Process 123 waits for ShareLock on transaction 456; blocked by process 789.
```

Postgres detects the cycle in the wait-for graph after `deadlock_timeout` (default 1s) and kills one transaction as the victim.

**The fix is ordering: always acquire locks in a consistent order** — e.g. always update the lower account id first. That makes a cycle impossible by construction, which is the same reasoning as lock-ordering in [[foundations/os/06-concurrency-primitives|OS concurrency]].

**Deadlocks are not prevented by retrying**, though retrying is a necessary backstop. They're prevented by ordering.

### 12. MVCC leaves rubbish

10,000 updates to **one row**: the table grows to hold ~10,000 row versions. Row count constant; `pg_relation_size` up substantially.

**An `UPDATE` in Postgres is an insert plus a mark-dead**, because MVCC requires old versions to remain visible to older snapshots. `VACUUM` reclaims the dead ones for reuse; `VACUUM FULL` rewrites the table to actually return space to the OS (and takes an exclusive lock).

**This is why hot-updated tables bloat**, why autovacuum is critical, and why long-running transactions are harmful — they hold back the horizon, so nothing since can be vacuumed. **A forgotten idle-in-transaction session can bloat a database until the disk fills** → [[databases/09-mvcc-and-concurrency-control|note 09]] · [[databases/12-operating-a-database|note 12]].

---

## Part D — Durability

### 13. Prove the WAL is doing something

10,000 inserts:

| | typical |
|---|---|
| One transaction each | **slow** — an `fsync` per commit |
| All in one transaction | **10–100× faster** — one `fsync` |
| `synchronous_commit = off` | faster still |

**Each commit must survive power loss, which means an `fsync` to durable storage** — and an fsync costs milliseconds even on an SSD, because it must reach media rather than the OS cache.

**Batching amortises it.** One transaction = one fsync for 10,000 rows.

**What (c) gives up, precisely:** with `synchronous_commit = off`, a commit returns *before* the WAL is flushed. You keep **atomicity and consistency** — recovery never leaves a torn transaction — but lose **durability** for a small window (~0.5s). A crash loses recently committed transactions that the client was told had succeeded.

**That's a legitimate trade for analytics and a catastrophic one for payments**, and it should be a deliberate decision recorded somewhere → [[foundations/systems-engineering/05-trade-studies|trade studies]].

### 14. Kill it mid-write

After `kill -9` and restart, the log shows recovery:

```
LOG: database system was interrupted; last known up at ...
LOG: database system was not properly shut down; automatic recovery in progress
LOG: redo starts at 0/1A2B3C0
LOG: redo done at ...
LOG: database system is ready to accept connections
```

**Uncommitted work is gone; committed work is present.** That's **atomicity** (no half-transaction) and **durability** (nothing acknowledged was lost) demonstrated rather than assumed.

**The mechanism is write-ahead logging: the log record reaches disk *before* the data page.** On restart, replay the log forward from the last checkpoint (redo), then undo anything uncommitted. **The same discipline as the atomic-write pattern in [[languages/06-python/15-files-and-io|files and I/O]]** — write elsewhere, flush, then make it visible — which is why that exercise and this one are the same idea at different scales.

## Related
- [[databases/13-practice-exercises|the exercises]]
- [[databases/README|the course]]

*Source: [reference] — SQLite figures measured August 2026; Postgres behaviour from its documentation and standard behaviour.*
