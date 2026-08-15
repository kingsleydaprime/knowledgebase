# Transactions and ACID

**[Intermediate → Advanced]** — The anomalies, what each isolation level actually prevents, and why your default is weaker than you think.

## What a transaction is

**A group of operations that succeed or fail together.**

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**Either both updates happen or neither does.** No state exists where money left one account and didn't arrive at the other.

**The guarantee is against two different threats**, and it's worth separating them:

**Failures** — a crash, an error, a lost connection halfway through. Handled by **atomicity and durability**, via the write-ahead log. → [[databases/10-durability-and-recovery|Durability and Recovery]]

**Concurrency** — another transaction reading or writing the same data at the same time. Handled by **isolation**, and that's this note.

## The anomalies

**Defined by what can go wrong when transactions interleave.** The names are worth knowing precisely, because isolation levels are defined in terms of them.

**Dirty read** — reading data another transaction wrote but hasn't committed. **If it rolls back, you read something that never existed.**

**Non-repeatable read** — reading the same row twice in one transaction and getting different values, because another transaction committed a change in between.

**Phantom read** — running the same *query* twice and getting different **rows**, because another transaction inserted or deleted matching rows.

> **Non-repeatable read is about a row's *value* changing. Phantom is about the *set of rows* changing.** The distinction matters because they're prevented by different mechanisms — row locks stop the first, range locks or snapshots stop the second.

**Lost update** — two transactions read the same value, both modify it, and the second overwrites the first's change:

```
T1: read balance = 100
T2: read balance = 100
T1: write balance = 100 - 10 = 90
T2: write balance = 100 - 20 = 80    ← T1's deduction is gone
```

**Write skew** — the subtle one, and the one that survives Snapshot Isolation:

```
Rule: at least one doctor must be on call.
Currently: Alice and Bob are both on call.

T1: Alice checks — 2 on call, fine — removes herself.
T2: Bob checks   — 2 on call, fine — removes himself.

Both commit. Zero doctors on call. Each transaction was individually valid.
```

**Neither transaction wrote to a row the other read a *changed* version of** — they read *different* rows and wrote *different* rows. **Snapshot Isolation permits this**, and it's the reason Serializable exists as a separate level.

## The isolation levels

**The SQL standard defines four**, by which anomalies they permit:

| Level | Dirty read | Non-repeatable | Phantom | Write skew |
|---|---|---|---|---|
| **Read Uncommitted** | ✅ possible | ✅ | ✅ | ✅ |
| **Read Committed** | ❌ prevented | ✅ | ✅ | ✅ |
| **Repeatable Read** | ❌ | ❌ | ✅* | ✅ |
| **Serializable** | ❌ | ❌ | ❌ | ❌ |

**\*The asterisk matters:** the standard says Repeatable Read permits phantoms. **Postgres's Repeatable Read is actually Snapshot Isolation and prevents phantoms.** **InnoDB's Repeatable Read prevents them too**, via next-key locking. **So both are stronger than the standard requires**, in different ways.

> **The standard is widely regarded as poorly specified.** It was written around a lock-based implementation, and it doesn't cleanly describe MVCC systems — which is why "Repeatable Read" means noticeably different things in Postgres, MySQL and Oracle. **Berenson et al.'s 1995 paper *A Critique of ANSI SQL Isolation Levels* is the standard reference for why**, and it's where Snapshot Isolation was formally named.

**What the defaults actually are:**

| Database | Default |
|---|---|
| **PostgreSQL** | Read Committed |
| **MySQL/InnoDB** | **Repeatable Read** |
| **Oracle** | Read Committed (snapshot-based) |
| **SQL Server** | Read Committed (lock-based by default) |
| **CockroachDB** | **Serializable** |

> **Two things worth internalising here.**
>
> **You are almost certainly running at Read Committed**, which permits non-repeatable reads, phantoms, lost updates and write skew. **Most application code is written as though transactions are serializable.** That gap is where a real class of production bugs lives — the kind that appear only under load and can't be reproduced.
>
> **And Postgres and MySQL differ at their defaults**, so behaviour genuinely changes when you port between them. This is not a portability detail you can ignore.

**Read Uncommitted is essentially unused** — Postgres treats it as Read Committed, and no one wants dirty reads.

## What each level costs

**Stronger isolation costs concurrency**, and the mechanism differs by engine.

**Read Committed** — each *statement* sees a snapshot taken at statement start. **So two queries in the same transaction can see different data.** Cheap, high concurrency.

**Repeatable Read / Snapshot Isolation** — the *transaction* takes one snapshot at its start and sees that throughout. **Consistent view, no read locks.**

**And it introduces serialization failures.** Under Postgres's Repeatable Read, if two transactions update the same row, the second gets:

```
ERROR: could not serialize access due to concurrent update
```

> **Your application must be prepared to retry.** This is the part people miss when raising the isolation level — **the database is now telling you to try again, and code that doesn't handle it just fails.** Retry with backoff, and make the transaction idempotent.

**Serializable** — the result is equivalent to *some* serial execution of the transactions.

**Two implementations:**

**Two-phase locking (2PL)** — acquire locks, release only at commit. **Correct, and it serialises heavily** — readers block writers.

**Serializable Snapshot Isolation (SSI)** — Postgres 9.1+. **Optimistic**: run under snapshot isolation, track read/write dependencies, and abort a transaction if a dangerous cycle forms. **No read locks, much better concurrency**, at the cost of more aborts under contention.

**SSI is a genuinely impressive piece of engineering** and makes Serializable practical for real workloads — but it still needs retry logic, and its abort rate rises sharply with contention.

## Choosing a level

**Read Committed is the right default** for most applications, *provided* you handle the concurrency you actually have.

**Use explicit locking for the specific dangerous cases:**

```sql
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
```

**`SELECT ... FOR UPDATE`** takes a row lock, so concurrent transactions block rather than reading stale data. **This is the standard fix for lost update**, and it's more surgical than raising the isolation level globally.

**`FOR SHARE`** allows concurrent readers, blocks writers.

**Optimistic concurrency** — the alternative, and usually better under low contention:

```sql
UPDATE items SET qty = 5, version = version + 1
WHERE id = 42 AND version = 3;
-- 0 rows updated → someone else changed it → retry
```

**No locks held between read and write**, which matters when a user is thinking for thirty seconds between loading a form and submitting it. **Holding a database lock across a user interaction is always wrong.**

**Raise to Serializable when** correctness genuinely requires it — financial invariants, inventory, booking systems — **and you've implemented retry.**

## Practical notes

**Keep transactions short.** A long transaction holds locks, blocks vacuum, and inflates the MVCC version chain. → [[databases/09-mvcc-and-concurrency-control|MVCC]]

**Never hold a transaction open across a network call.** Calling an external API inside a transaction ties database locks to someone else's latency and timeouts.

**Never hold one across user interaction.** Use optimistic concurrency instead.

**Access rows in a consistent order** across your codebase. **Deadlocks happen when two transactions lock the same rows in opposite orders** — consistent ordering prevents them structurally.

**Handle serialization failures and deadlocks with retry.** Both are *expected* outcomes, not bugs. Exponential backoff, a retry limit, and idempotent transaction bodies.

**Set a statement timeout.** `statement_timeout` and `idle_in_transaction_session_timeout` prevent one stuck session holding locks indefinitely. **The second is especially important** — an application that opens a transaction and then stalls will block vacuum across the whole database.

**Know your framework's default.** ORMs and connection poolers may set an isolation level, wrap statements in implicit transactions, or leave autocommit on. **Check rather than assume.** → [[databases/12-operating-a-database|ORMs]]

**Test concurrency deliberately.** Anomalies don't appear in single-threaded tests. Run two concurrent sessions by hand and see what happens — it takes ten minutes and it's the only way to build the intuition.

---

## Related
- [[databases/09-mvcc-and-concurrency-control|MVCC and Concurrency Control]] — how isolation is actually implemented
- [[databases/10-durability-and-recovery|Durability and Recovery]] — the A and D of ACID
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — the same problem across machines
- [[databases/README|Databases map]]
