# Databases — Projects

*You have 12 notes of internals and 11,000 lines of syntax reference. The gap is that **none of it has been felt** — a query plan you didn't read, a lock you didn't hold, a migration you didn't botch. Every project here produces a measurement.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **Make a query 100× faster** — take a slow query on a table with a million rows, read `EXPLAIN ANALYZE`, add the right index, and measure. **Done when:** you can point at the line in the plan that changed from Seq Scan to Index Scan, and explain why your index and not another. Exercises: [[databases/07-join-algorithms-and-the-optimiser|the optimiser]].

- 🟢 **Break it with a missing index** — the same exercise inverted: find an N+1 in a real app and fix it. **Done when:** query count per request drops and you have both numbers.

- 🟢 **Watch isolation levels differ** — two `psql` sessions, one table. Reproduce a dirty read, a non-repeatable read, and a phantom by changing only the isolation level. **Done when:** you've seen all three and can say which level your app actually uses. Exercises: [[databases/08-transactions-and-acid|isolation levels]].

- 🟡 **Cause a deadlock on purpose, then fix it** — two transactions, opposite lock order. **Done when:** you've read the deadlock in the logs and fixed it by ordering acquisitions consistently. Exercises: [[databases/09-mvcc-and-concurrency-control|MVCC]].

- 🟡 **A zero-downtime migration** — add a NOT NULL column to a large, live table without locking it: expand → backfill in batches → contract. **Done when:** you ran it against a table under concurrent write load and nothing blocked. **This is the single most valuable database skill nobody practises.**

- 🟡 **Set up replication and fail over** — a primary and a replica, then kill the primary and promote. **Done when:** you know your actual replication lag and what you lost. Exercises: [[databases/11-replication-and-scaling|replication]].

- 🟡 **Benchmark B-tree vs LSM** — the same write-heavy workload against Postgres and RocksDB/Cassandra. **Done when:** you can show write amplification differing and explain it from [[databases/05-lsm-trees|LSM]] and [[databases/04-b-trees-and-indexes|B-trees]].

- 🔴 **Build your own database** — the guide: [[build-your-own-shit/06-your-own-database|06-your-own-database]]. Pager → B-tree → SQL subset → **WAL**. **Done when:** `kill -9` mid-write and the data survives.

- 🔴 ⭐ **Model something hard, properly** — take a real domain (bookings with overlapping constraints, double-entry ledger, versioned documents) and design the schema with correct constraints so the *database* enforces the invariants, not the application. **Done when:** you cannot corrupt it from `psql` with a bad INSERT. Exercises: [[databases/database-design-reference|database design]].

## If you only do one

**The zero-downtime migration.** It's the difference between someone who knows SQL and someone you'd let near production, and it takes a weekend.

## Related
- [[databases/README|the databases course]] · [[databases/interview/README|interview bank]]
- [[databases/sql-reference|SQL reference]] · [[databases/database-design-reference|design reference]]
- [[project-ideas|Project Ideas]] — the vault-wide index
