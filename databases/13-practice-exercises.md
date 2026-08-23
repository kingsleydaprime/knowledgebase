# Practice Exercises

> **[Intermediate]** · Fourteen exercises against a real database. **The internals in this course are all observable from the outside — if you know what to ask.**

**Setup:** `sqlite3` (in Python's standard library — nothing to install) does most of this. A few exercises need **PostgreSQL**, and are marked; Docker is the fastest route:
```bash
docker run --rm -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:16
```

**Build a table worth measuring** — 500,000 rows minimum. **On 1,000 rows every query is fast and every exercise here is invisible**, which is itself the first lesson.

Solutions with measured results in [[databases/14-practice-exercises-solutions|note 14]].

---

## Part A — Storage and indexes (notes 03–05)

**1. Earn the index.**
Load 500k users with an `email` column. Time 200 lookups by email with no index. Add `CREATE INDEX`. Time the same 200.
**Done when:** you have both timings and the ratio, and **`EXPLAIN QUERY PLAN` changed its wording** in a way you can quote → [[databases/04-b-trees-and-indexes|note 04]].

**2. Read the plan, not the clock.**
Run `EXPLAIN` (Postgres: `EXPLAIN ANALYZE`) on: a lookup by primary key, a lookup on an unindexed column, a range query, and a `LIKE '%foo%'`.
**Done when:** you can predict *before running* which produce a scan and which a seek — and can explain why leading-wildcard `LIKE` cannot use a B-tree.

**3. Kill your own index, four ways.**
Get the optimiser to ignore an index you created, by: wrapping the column in a function, comparing against a different type, using a leading wildcard, and selecting most of the table.
**Done when:** you have four plans showing a scan, and can state the general rule that covers all four. **The fourth is not a bug** → [[databases/07-join-algorithms-and-the-optimiser|note 07]].

**4. Composite index column order.**
Create `INDEX(a, b)`. Query on `a` alone, on `b` alone, and on both.
**Done when:** you can state which of the three uses the index and why — **the leftmost-prefix rule**, derived from your own plans rather than memorised.

**5. Covering index.**
Find a query where adding a column to the index removes a table lookup entirely. Compare plans.
**Done when:** the plan says *covering* / *index only*, and you can explain what I/O disappeared → [[databases/03-storage-and-page-layout|note 03]].

---

## Part B — Queries and joins (notes 06–07)

**6. Watch the optimiser change its mind.**
Take a join between a large and a small table. Run `EXPLAIN`. Now `ANALYZE` (update statistics) and run it again. Then delete 90% of one table, re-analyze, and look again.
**Done when:** the join *algorithm* changed, and you can name the statistic that drove it → [[databases/07-join-algorithms-and-the-optimiser|note 07]].

**7. Reproduce N+1.**
Write application code that fetches 100 orders then loops fetching each customer. Count queries. Rewrite as a single join.
**Done when:** you have 101 vs 1, and the timing difference. **This is the most common performance bug in application code** → [[backend/frameworks/python/02-django/README|Django]].

**8. Make the planner wrong.**
Construct a query where the estimated row count differs from actual by 100× or more (`EXPLAIN ANALYZE` shows both). Correlated columns are the easy route.
**Done when:** you can point at the estimate-vs-actual gap and say what assumption the planner made. **Bad estimates, not bad algorithms, cause most slow plans.**

---

## Part C — Transactions and concurrency (notes 08–09)

**9. Observe a dirty read — or fail to.**
Two connections. Set isolation to `READ UNCOMMITTED` and try to see uncommitted data.
**Done when:** you either observed it, or discovered your database **doesn't implement that level** and can say what it does instead. *(Postgres silently gives you READ COMMITTED — knowing that is the exercise.)*

**10. Cause a non-repeatable read and a phantom.** *(Postgres)*
In `READ COMMITTED`, read a row twice in one transaction with another transaction committing between. Then repeat at `REPEATABLE READ`.
**Done when:** you have produced the anomaly at one level and shown it prevented at the other → [[databases/08-transactions-and-acid|note 08]].

**11. Deadlock on purpose.** *(Postgres)*
Two transactions updating two rows in opposite order.
**Done when:** the database detects it and kills one, and you have the error message. Then fix it by **ordering the writes consistently** — the standard remedy.

**12. Watch MVCC leave rubbish.** *(Postgres)*
Update a row 10,000 times in a loop. Check table size before and after with `pg_relation_size`. Then `VACUUM` and check again.
**Done when:** the table grew despite the row count being constant, and you can explain why an `UPDATE` is really an insert → [[databases/09-mvcc-and-concurrency-control|note 09]].

---

## Part D — Durability (note 10)

**13. Prove the WAL is doing something.**
Insert 10,000 rows: (a) one transaction per row, (b) all in one transaction, (c) with `synchronous_commit = off` (Postgres) or `PRAGMA synchronous = OFF` (SQLite).
**Done when:** you have three timings that differ by orders of magnitude, and **can state exactly what durability you gave up in (c)** → [[databases/10-durability-and-recovery|note 10]].

**14. Kill it mid-write.**
Start a long transaction, then `kill -9` the database process. Restart it.
**Done when:** the database recovers to a consistent state with your uncommitted work gone, and you have found the recovery message in the log. **This is ACID's D and A, demonstrated rather than believed.**

## Related
- [[databases/14-practice-exercises-solutions|Solutions]] — with measured results
- [[databases/README|the course]] · [[databases/sql-reference|SQL reference]]

*Source: [reference] — results in note 14 measured Aug 2026.*
