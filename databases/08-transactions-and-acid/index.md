# Transactions and ACID

**[Intermediate → Advanced]** — What a transaction guarantees, the anomalies that happen when transactions run at the same time, what each isolation level actually prevents, and why your default is weaker than you think. Every anomaly in this lesson is made to happen in the lab, on a real PostgreSQL 18, with two connections stepped one statement at a time.

## Before you start

You can already:

- Write `UPDATE` and `SELECT` statements, and run them in `psql` or from code.
- Explain what a row lock is in general terms: something that makes a second writer wait → [[os/06-concurrency-primitives|locks and races]] (helpful, not required).
- Run Python with `uv`, and have PostgreSQL 16 or later installed locally; the lab creates and deletes its own database, as in [[databases/04-b-trees-and-indexes/index|B-trees and indexes]].

After this lesson you will be able to:

1. Say what each letter of ACID guarantees, and which threat (a failure or a concurrent transaction) it guards against.
2. Recognise a dirty read, a non-repeatable read, a phantom, a lost update and write skew from a trace of two transactions.
3. Say what PostgreSQL's Read Committed, Repeatable Read and Serializable each prevent, and what they cost.
4. Fix a lost update four ways, and write the retry loop that Repeatable Read and Serializable require.

**Study route:** sections 1–4 build the vocabulary. Stop at the predictions in sections 5 and 7 and try them before reading on. Section 10 is the lab. Then read [[databases/09-mvcc-and-concurrency-control/index|MVCC]] for *how* PostgreSQL does all this.

## The kid version

Two brothers share a money jar with £10 in it. Each wants to buy an £8 game. Each looks in the jar, sees £10, thinks "plenty", and goes off to the shop. Now they owe £6 they don't have. Each check was right when it was made; the problem is that both checked before either took the money. A grown-up could fix it by letting only one person near the jar at a time, or by making each brother check again just before taking the money. Databases offer both, and a range in between.

**Where the analogy stops working.** A family can afford to make one brother wait. A database with thousands of users can't make everyone wait their turn, so by default it lets transactions run side by side and only stops some of the collisions. Which collisions it stops is the *isolation level*, and the default stops fewer than most people assume.

## 1. Why this exists

The shop has a gift-card balance. Checkout reads the balance, checks it covers the order, and writes the new balance. On a quiet day that's fine. During a sale, the same customer double-clicks "pay" and two requests run at once: both read £100, both see enough, and both write their own result. One deduction disappears, and nobody notices until the books don't balance. Nothing crashed and no error appeared, and a test with one user will never reproduce it. This lesson is about naming that kind of bug precisely, and choosing the database feature that prevents it.

## Terms used in this lesson

1. **Transaction**: This is a group of database operations that succeed or fail as one unit, started with `BEGIN` and ended with `COMMIT` (keep everything) or `ROLLBACK` (undo everything).
2. **ACID**: This stands for atomicity, consistency, isolation and durability, the four guarantees a transaction makes.
3. **Atomicity**: This means a transaction's changes all happen or none do, even if it fails halfway.
4. **Consistency**: This means a transaction moves the database from one valid state to another, where "valid" is defined by its constraints, such as `CHECK (balance >= 0)`.
5. **Isolation**: This means concurrent transactions don't see each other's half-finished work. How much they're shielded from each other is the isolation level.
6. **Durability**: This means a committed change survives a crash.
7. **Isolation level**: This is a setting that chooses which interference between concurrent transactions is allowed. The standard ones are Read Uncommitted, Read Committed, Repeatable Read and Serializable.
8. **Snapshot**: This is the consistent picture of the database a statement or transaction reads from: everything committed before a certain moment, and nothing after.
9. **Anomaly**: This is a result that couldn't happen if the transactions had run one after the other.
10. **Serialization failure**: This is PostgreSQL refusing to complete a transaction because it can't make the result look as if transactions ran one at a time. The error code is `40001`, and the right response is to run the whole transaction again.
11. **Optimistic concurrency**: This means letting transactions proceed without locks, and detecting at write time whether someone else changed the data in between, usually with a version number.

## 2. What a transaction is

**A group of operations that succeed or fail together.**

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**Either both updates happen or neither does.** No state exists where money left one account and didn't arrive at the other. In the lab, a transfer credits account 2 first, then the debit from account 1 fails its `CHECK (balance >= 0)`. After `ROLLBACK`, both balances are exactly what they were: not even the credit happened. After any error, PostgreSQL marks the transaction as aborted and accepts only `ROLLBACK`.

**The guarantee is against two different threats:**

- **Failures**: a crash, an error, a lost connection halfway through. Handled by **atomicity and durability**, through the write-ahead log → [[databases/10-durability-and-recovery|durability and recovery]].
- **Concurrency**: another transaction reading or writing the same data at the same time. Handled by **isolation**, and that's the rest of this lesson.

## 3. The anomalies

**They're defined by what can go wrong when transactions interleave**, and isolation levels are defined in terms of them, so the names are worth knowing precisely.

1. **Dirty read**: reading data another transaction wrote but hasn't committed. **If it rolls back, you read something that never existed.**
2. **Non-repeatable read**: reading the same row twice in one transaction and getting different values, because another transaction committed a change in between.
3. **Phantom read**: running the same *query* twice and getting different **rows**, because another transaction inserted or deleted matching rows.

> **A non-repeatable read is about a row's *value* changing. A phantom is about the *set of rows* changing.** They're prevented by different mechanisms: row locks stop the first; range locks or snapshots stop the second.

4. **Lost update**: two transactions read the same value, both change it, and the second write overwrites the first:

```
T1: read balance = 100
T2: read balance = 100
T1: write balance = 100 - 10 = 90
T2: write balance = 100 - 20 = 80    ← T1's deduction is gone
```

5. **Write skew**: the subtle one, and the one that survives Snapshot Isolation:

```
Rule: at least one doctor must be on call.
Currently: Alice and Bob are both on call.

T1: Alice checks: 2 on call, fine. She takes herself off call.
T2: Bob checks:   2 on call, fine. He takes himself off call.

Both commit. Zero doctors on call. Each transaction was valid on its own.
```

**Neither transaction changed a row the other one changed**: they read the same rows, but wrote *different* ones. **Snapshot Isolation allows this**, and it's why Serializable exists as a separate level.

## 4. The isolation levels

**The SQL standard defines four**, by which anomalies they allow:

| Level | Dirty read | Non-repeatable | Phantom | Write skew |
|---|---|---|---|---|
| **Read Uncommitted** | ✅ possible | ✅ | ✅ | ✅ |
| **Read Committed** | ❌ prevented | ✅ | ✅ | ✅ |
| **Repeatable Read** | ❌ | ❌ | ✅* | ✅ |
| **Serializable** | ❌ | ❌ | ❌ | ❌ |

**\*The asterisk matters.** The standard says Repeatable Read allows phantoms. **PostgreSQL's Repeatable Read is Snapshot Isolation, and prevents phantoms**: in the lab, a Read Committed transaction counts 2 accounts, another session inserts one, and the second count says 3; under Repeatable Read it still says 2. **InnoDB's Repeatable Read prevents them too**, by locking the gaps between index entries. **So both are stronger than the standard requires**, in different ways.

> **The standard is widely regarded as poorly specified.** It was written around a lock-based implementation and doesn't cleanly describe snapshot-based systems, which is why "Repeatable Read" means noticeably different things in PostgreSQL, MySQL and Oracle. **Berenson and others' 1995 paper *A Critique of ANSI SQL Isolation Levels* is the standard reference for why**, and it's where Snapshot Isolation was formally named.

**Read Uncommitted is essentially unused.** PostgreSQL runs it as Read Committed: in the lab, a session asking for Read Uncommitted still can't see another session's uncommitted change.

**What the defaults actually are:**

| Database | Default |
|---|---|
| **PostgreSQL** | Read Committed |
| **MySQL/InnoDB** | **Repeatable Read** |
| **Oracle** | Read Committed (snapshot-based) |
| **SQL Server** | Read Committed (lock-based by default) |
| **CockroachDB** | **Serializable** |

> **Two things worth taking in.**
>
> **You are almost certainly running at Read Committed**, which allows non-repeatable reads, phantoms, lost updates and write skew. **Most application code is written as though transactions are serializable.** That gap is where a real class of production bugs lives: the kind that appear only under load and can't be reproduced on a laptop.
>
> **PostgreSQL and MySQL differ at their defaults**, so behaviour genuinely changes when you port between them.

## 5. What each level costs, and the lost update

**Stronger isolation costs concurrency**, and the mechanism differs by engine:

- **Read Committed**: each *statement* sees a snapshot taken when that statement starts, **so two queries in the same transaction can see different data.** It's cheap, with high concurrency. In the lab, a Read Committed transaction reads 100, another session commits 70, and the same transaction's next read says 70.
- **Repeatable Read (Snapshot Isolation)**: the *transaction* takes one snapshot at its first statement and sees it throughout. The second read in the same scenario says 100. **A consistent view, with no read locks.**

**Predict before reading on.** Two Read Committed transactions each read a balance of 100. The first writes 90 (it read 100, minus 10) and commits. The second writes 80 (it read 100, minus 20) and commits. What's the final balance? What happens to the second transaction if both run at Repeatable Read instead?

<details>
<summary>After your prediction</summary>

At Read Committed the final balance is **80**, where 70 is right: a **lost update**, and no error anywhere. At Repeatable Read, the second transaction's `UPDATE` fails:

```
ERROR: could not serialize access due to concurrent update
```

Its snapshot says 100, but the row has changed since, so PostgreSQL refuses rather than overwrite a change the transaction never saw. The final balance stays 90, and **the application must run the second transaction again**, from the beginning, so it reads 90 and writes 70. The lab checks both.

</details>

> **Your application must be ready to retry.** This is the part people miss when they raise the isolation level: **the database is now telling you to try again, and code that doesn't handle it just fails.** Retry the whole transaction with backoff, and keep its body free of side effects (no emails sent from inside it) so running it twice is safe. The lab's `with_retry` does this.

**Serializable**: the result is equivalent to *some* order of running the transactions one at a time. There are two ways to implement it:

- **Two-phase locking**: take locks as you go, release them only at commit. **It's correct, and it serialises heavily**: readers block writers.
- **Serializable Snapshot Isolation (SSI)**, PostgreSQL 9.1+: **optimistic**. Run under snapshot isolation, track which transactions read what the others wrote, and abort one if a dangerous cycle forms. **No read locks, and much better concurrency**, at the cost of more aborts under contention. It still needs retry logic.

## 6. Four ways to fix the lost update

The lab runs each against the same two-transaction race:

1. **Let the database do the arithmetic.** `UPDATE accounts SET balance = balance - 20` re-reads the row as it updates it, so both deductions land: **70**. The simplest fix, whenever the new value can be expressed in SQL.
2. **Lock the row when you read it.** `SELECT balance FROM accounts WHERE id = 1 FOR UPDATE` takes a row lock, so a second `FOR UPDATE` waits until the first transaction commits, then reads the new value. In the lab, the second reader, given a 100 ms `lock_timeout`, gets `LockNotAvailable`: proof it would have waited. **This is the standard fix** when the application must read, decide, then write. `FOR SHARE` lets other readers in but blocks writers.
3. **Raise the isolation level** to Repeatable Read, and retry on the serialization failure.
4. **Optimistic concurrency with a version column**:

```sql
UPDATE accounts SET balance = 90, version = version + 1
WHERE id = 1 AND version = 3;
-- 0 rows updated → someone else changed it first → reload and retry
```

**No lock is held between reading and writing**, which matters when a user spends thirty seconds between loading a form and submitting it. **Holding a database lock across a user's thinking time is always wrong.** In the lab, the first update changes 1 row and the second, with the same old version, changes 0.

## 7. Write skew, and Serializable

**Predict before reading on.** Alice and Bob are both on call. Each runs: begin; count the doctors on call; if there are at least 2, take myself off call; commit. They run at the same time at Repeatable Read. How many are on call afterwards? And at Serializable?

<details>
<summary>After your prediction</summary>

At Repeatable Read, **0**: each counted 2 in its own snapshot, and they updated different rows, so nothing conflicts. That's write skew. At Serializable, the first to commit succeeds, and the second's `COMMIT` fails with a serialization failure: SSI noticed that each transaction read what the other was about to change, so no one-at-a-time order could produce the result. **1** doctor stays on call. When the failed transaction is retried, it counts 1 on call, so it doesn't take Bob off: the lab's last test checks that Bob is still on call afterwards.

</details>

Without Serializable, write skew needs a lock on what the check reads: `SELECT … FOR UPDATE` on the rows counted, or a constraint the database enforces itself.

## 8. Choosing a level

**Read Committed is the right default** for most applications, *provided* you handle the concurrency you actually have:

- Express updates as arithmetic in SQL wherever possible.
- **Use `SELECT … FOR UPDATE` for the specific read-then-write cases**, which is more surgical than raising the level everywhere.
- **Use optimistic concurrency** across user think time, or under low contention.
- **Raise to Serializable when correctness genuinely needs it**: financial invariants, stock, bookings, any rule that spans several rows. **And implement retry.**

## 9. Practical notes

- **Keep transactions short.** A long transaction holds locks, blocks vacuum, and lengthens the chain of row versions → [[databases/09-mvcc-and-concurrency-control/index|MVCC]].
- **Never hold a transaction open across a network call.** Calling an external API inside a transaction ties database locks to someone else's latency and timeouts.
- **Never hold one across user interaction.** Use optimistic concurrency instead.
- **Access rows in a consistent order** everywhere in your code. **Deadlocks happen when two transactions lock the same rows in opposite orders**; consistent ordering prevents them structurally.
- **Retry serialization failures and deadlocks.** Both are *expected* outcomes, not bugs: exponential backoff, a retry limit, and transaction bodies that are safe to run twice.
- **Set timeouts.** `statement_timeout` and `idle_in_transaction_session_timeout` stop one stuck session holding locks indefinitely. **The second is especially important**: an application that opens a transaction and stalls blocks vacuum across the whole database.
- **Know your framework's default.** ORMs and connection poolers may set an isolation level, wrap statements in transactions, or leave auto-commit on. **Check rather than assume** → [[databases/12-operating-a-database|operating a database]].
- **Test concurrency deliberately.** Anomalies don't appear in single-threaded tests. Open two `psql` sessions and step through a race by hand; it takes ten minutes and builds the intuition faster than anything else.

## 10. The lab: two sessions, stepped by hand

`test_isolation.py` opens two connections, `a` and `b`, with auto-commit on so every `BEGIN` and `COMMIT` is explicit, and steps them one statement at a time, so each interleaving is exact. Where `b` would wait for `a`'s lock, it's given a short `lock_timeout`, so "it would block" becomes an error the test can check. It uses the same [`with-postgres.sh`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/shared) throwaway cluster as week 5.

```python
"""The anomalies, made to happen on a real PostgreSQL 18, and what each isolation level and fix does about them.
Two connections, a and b, are stepped one statement at a time, so every interleaving is exact. Where one session
would wait for the other's lock, it gets a short lock_timeout instead, so "it would block" becomes a checkable error.
Run through ../shared/with-postgres.sh."""
import time
import unittest

import psycopg
from psycopg import errors


def connect() -> psycopg.Connection:
    # autocommit=True: psycopg starts no transactions of its own, so the tests' explicit BEGIN and COMMIT are the
    # only ones, exactly as they'd be typed into psql.
    return psycopg.connect(autocommit=True)


def value(conn: psycopg.Connection, sql: str, params=()) -> object:
    return conn.execute(sql, params).fetchone()[0]


def with_retry(work, attempts: int = 5):
    """Runs `work`, retrying when PostgreSQL reports a serialization failure or a deadlock: both are expected
    outcomes under concurrency, and the right response is to run the whole transaction again."""
    for attempt in range(attempts):
        try:
            return work()
        except (errors.SerializationFailure, errors.DeadlockDetected):
            if attempt == attempts - 1:
                raise
            time.sleep(0.01 * 2**attempt)  # back off a little longer each time


class Isolation(unittest.TestCase):
    def setUp(self):
        self.a, self.b = connect(), connect()
        self.a.execute("""
            DROP TABLE IF EXISTS accounts, doctors;
            CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0), version int NOT NULL DEFAULT 1);
            INSERT INTO accounts (id, balance) VALUES (1, 100), (2, 50);
            CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
            INSERT INTO doctors VALUES ('alice', true), ('bob', true);
        """)

    def tearDown(self):
        self.a.close()
        self.b.close()

    def balance(self, account: int = 1) -> int:
        return value(self.a, "SELECT balance FROM accounts WHERE id = %s", [account])

    def test_atomicity_a_failed_transfer_leaves_no_trace(self):
        self.a.execute("BEGIN")
        self.a.execute("UPDATE accounts SET balance = balance + 150 WHERE id = 2")  # the credit succeeds...
        with self.assertRaises(errors.CheckViolation):
            self.a.execute("UPDATE accounts SET balance = balance - 150 WHERE id = 1")  # ...the debit can't: 100 - 150 < 0
        self.a.execute("ROLLBACK")  # after an error the transaction is aborted: only ROLLBACK is accepted
        self.assertEqual((self.balance(1), self.balance(2)), (100, 50))  # not even the credit happened

    def test_no_dirty_reads_even_when_you_ask_for_read_uncommitted(self):
        self.b.execute("BEGIN")
        self.b.execute("UPDATE accounts SET balance = 0 WHERE id = 1")  # not committed
        self.a.execute("BEGIN ISOLATION LEVEL READ UNCOMMITTED")  # PostgreSQL runs this as Read Committed
        self.assertEqual(self.balance(), 100)  # the uncommitted 0 is invisible
        self.a.execute("COMMIT")
        self.b.execute("ROLLBACK")

    def test_read_committed_sees_other_commits_between_statements(self):
        for level, second_read in [("READ COMMITTED", 70), ("REPEATABLE READ", 100)]:
            self.a.execute("UPDATE accounts SET balance = 100 WHERE id = 1")
            self.a.execute(f"BEGIN ISOLATION LEVEL {level}")
            self.assertEqual(self.balance(), 100)
            self.b.execute("UPDATE accounts SET balance = 70 WHERE id = 1")  # b commits in between (autocommit)
            self.assertEqual(self.balance(), second_read, level)  # non-repeatable read, or a stable snapshot
            self.a.execute("COMMIT")

    def test_phantoms_in_read_committed_not_in_postgres_repeatable_read(self):
        for level, second_count in [("READ COMMITTED", 3), ("REPEATABLE READ", 2)]:
            self.a.execute("DELETE FROM accounts WHERE id = 3")
            self.a.execute(f"BEGIN ISOLATION LEVEL {level}")
            self.assertEqual(value(self.a, "SELECT count(*) FROM accounts"), 2)
            self.b.execute("INSERT INTO accounts (id, balance) VALUES (3, 10)")
            self.assertEqual(value(self.a, "SELECT count(*) FROM accounts"), second_count, level)
            self.a.execute("COMMIT")

    def test_a_lost_update_in_read_committed(self):
        # Both read 100, compute in the application, and write back. The second write erases the first.
        self.a.execute("BEGIN")
        self.b.execute("BEGIN")
        seen_a, seen_b = self.balance(), value(self.b, "SELECT balance FROM accounts WHERE id = 1")
        self.a.execute("UPDATE accounts SET balance = %s WHERE id = 1", [seen_a - 10])
        self.a.execute("COMMIT")
        self.b.execute("UPDATE accounts SET balance = %s WHERE id = 1", [seen_b - 20])
        self.b.execute("COMMIT")
        self.assertEqual(self.balance(), 80)  # should be 70: a's 10 is gone

    def test_fix_one_let_the_database_do_the_arithmetic(self):
        self.a.execute("BEGIN")
        self.b.execute("BEGIN")
        self.a.execute("UPDATE accounts SET balance = balance - 10 WHERE id = 1")
        self.a.execute("COMMIT")
        self.b.execute("UPDATE accounts SET balance = balance - 20 WHERE id = 1")  # re-reads the row it updates
        self.b.execute("COMMIT")
        self.assertEqual(self.balance(), 70)

    def test_fix_two_select_for_update_makes_the_second_reader_wait(self):
        self.a.execute("BEGIN")
        self.assertEqual(value(self.a, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"), 100)
        self.b.execute("BEGIN")
        self.b.execute("SET LOCAL lock_timeout = '100ms'")
        with self.assertRaises(errors.LockNotAvailable):  # b would wait until a commits
            self.b.execute("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
        self.b.execute("ROLLBACK")
        self.a.execute("UPDATE accounts SET balance = 90 WHERE id = 1")
        self.a.execute("COMMIT")
        self.b.execute("BEGIN")  # after a commits, b's read sees 90, and its write is correct
        self.assertEqual(value(self.b, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"), 90)
        self.b.execute("UPDATE accounts SET balance = 70 WHERE id = 1")
        self.b.execute("COMMIT")
        self.assertEqual(self.balance(), 70)

    def test_fix_three_repeatable_read_refuses_the_second_write(self):
        self.a.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        self.b.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        seen_b = value(self.b, "SELECT balance FROM accounts WHERE id = 1")
        self.a.execute("UPDATE accounts SET balance = balance - 10 WHERE id = 1")
        self.a.execute("COMMIT")
        with self.assertRaisesRegex(errors.SerializationFailure, "could not serialize access due to concurrent update"):
            self.b.execute("UPDATE accounts SET balance = %s WHERE id = 1", [seen_b - 20])
        self.b.execute("ROLLBACK")  # the application must now run b's whole transaction again
        self.assertEqual(self.balance(), 90)

    def test_fix_four_optimistic_concurrency_with_a_version_column(self):
        version = value(self.a, "SELECT version FROM accounts WHERE id = 1")
        first = self.a.execute("UPDATE accounts SET balance = 90, version = version + 1 WHERE id = 1 AND version = %s", [version])
        second = self.b.execute("UPDATE accounts SET balance = 80, version = version + 1 WHERE id = 1 AND version = %s", [version])
        self.assertEqual((first.rowcount, second.rowcount), (1, 0))  # 0 rows: someone changed it first; reload and retry
        self.assertEqual(self.balance(), 90)

    def test_write_skew_survives_repeatable_read_and_serializable_stops_it(self):
        def go_off_call(conn: psycopg.Connection, name: str, level: str) -> None:
            conn.execute(f"BEGIN ISOLATION LEVEL {level}")
            if value(conn, "SELECT count(*) FROM doctors WHERE on_call") >= 2:  # the rule: someone must stay on call
                conn.execute("UPDATE doctors SET on_call = false WHERE name = %s", [name])

        go_off_call(self.a, "alice", "REPEATABLE READ")
        go_off_call(self.b, "bob", "REPEATABLE READ")  # each saw 2 on call, in its own snapshot
        self.a.execute("COMMIT")
        self.b.execute("COMMIT")
        self.assertEqual(value(self.a, "SELECT count(*) FROM doctors WHERE on_call"), 0)  # both left: write skew

        self.a.execute("UPDATE doctors SET on_call = true")
        go_off_call(self.a, "alice", "SERIALIZABLE")
        go_off_call(self.b, "bob", "SERIALIZABLE")
        self.a.execute("COMMIT")
        with self.assertRaises(errors.SerializationFailure):  # SSI spots the read/write cycle and aborts one
            self.b.execute("COMMIT")
        self.assertEqual(value(self.a, "SELECT count(*) FROM doctors WHERE on_call"), 1)

    def test_the_retried_transaction_sees_the_new_state_and_keeps_the_rule(self):
        def bob_goes_off_call():
            try:
                self.b.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")
                if value(self.b, "SELECT count(*) FROM doctors WHERE on_call") >= 2:
                    self.b.execute("UPDATE doctors SET on_call = false WHERE name = 'bob'")
                self.b.execute("COMMIT")
            except Exception:
                self.b.execute("ROLLBACK")
                raise

        self.a.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")
        self.assertEqual(value(self.a, "SELECT count(*) FROM doctors WHERE on_call"), 2)
        self.a.execute("UPDATE doctors SET on_call = false WHERE name = 'alice'")
        self.b.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")  # bob's first attempt starts before alice commits
        value(self.b, "SELECT count(*) FROM doctors WHERE on_call")
        self.b.execute("UPDATE doctors SET on_call = false WHERE name = 'bob'")
        self.a.execute("COMMIT")
        with self.assertRaises(errors.SerializationFailure):
            self.b.execute("COMMIT")
        self.b.execute("ROLLBACK")
        with_retry(bob_goes_off_call)  # the retry sees 1 on call, so bob stays
        self.assertEqual(value(self.a, "SELECT name FROM doctors WHERE on_call"), "bob")


if __name__ == "__main__":
    unittest.main()
```

**Lab:** the code is in [`databases/08-transactions-and-acid/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/python). From the vault root, `python3 labs/run.py transactions-and-acid/python` runs it and checks this page still shows the same code. It needs PostgreSQL 16 or later installed. Expect 11 passing tests in about a second.

## Common pitfalls

1. **Read, compute in the application, write back, at Read Committed.** The lost update. Use SQL arithmetic, `FOR UPDATE`, or a version column.
2. **Raising the isolation level without retry.** Serialization failures then become user-facing errors.
3. **Retrying only the failed statement.** The whole transaction must run again, from its first read.
4. **Side effects inside a retried transaction.** An email sent from inside it is sent once per attempt.
5. **Assuming the database's default is Serializable.** In PostgreSQL it's Read Committed; in MySQL, Repeatable Read.
6. **Holding a transaction open across a network call or a user's think time.**
7. **Checking a multi-row rule at Repeatable Read.** Write skew gets through. Use Serializable or lock what you read.

## Check your understanding

1. Which ACID guarantees protect against a crash halfway through, and which against another transaction?
2. A transaction counts orders twice and gets 10, then 11. Another transaction had inserted an order in between. Which anomaly is it, and which PostgreSQL level stops it?
3. Why does `UPDATE … SET balance = balance - 20` avoid the lost update when reading the balance and writing `80` doesn't?
4. What must an application do when PostgreSQL reports `could not serialize access`?
5. Why doesn't Repeatable Read stop the doctors' write skew, and what does?
6. Why is optimistic concurrency better than `FOR UPDATE` for an edit form a user keeps open for a minute?

<details>
<summary>Answers — after your attempt</summary>

1. Atomicity and durability protect against failures: the write-ahead log lets PostgreSQL undo an unfinished transaction and keep a committed one. Isolation protects against other transactions. Consistency is kept by both, through constraints.
2. A phantom read: the set of rows changed. Repeatable Read stops it in PostgreSQL, because the whole transaction reads one snapshot. (The SQL standard only requires Serializable to.)
3. The `UPDATE` reads the row's current value at the moment it changes it, while holding the row's lock, so it subtracts from 90 if the other transaction already committed. Writing `80` uses a value read earlier, which may be stale.
4. Roll back and run the whole transaction again from the start, so its reads see the new state, with a short backoff and a limit on attempts. The transaction body must be safe to run more than once.
5. Each transaction reads its own snapshot, sees 2 on call, and updates a *different* row, so there's no write-write conflict for Repeatable Read to catch. Serializable (SSI) tracks read-write dependencies between transactions and aborts one when they form a cycle. Locking the rows the check reads with `FOR UPDATE` also works.
6. `FOR UPDATE` would hold a row lock, and an open transaction, for the whole minute, blocking other writers and vacuum. Optimistic concurrency holds nothing while the user thinks; it only checks the version when the form is submitted, and asks the user to reload if someone else changed it.

</details>

## Practice — independent task

**Book the last seat safely.**

1. In a scratch copy of the lab, create `seats (id int PRIMARY KEY, booked_by text)` with one free seat, and write `book(conn, name)`: find a free seat and give it to `name`.
2. Write a test that starts two bookings with two connections, interleaved so both find the same free seat, and show that the naive version gives the seat to both, the second overwriting the first.
3. Fix it twice, with `FOR UPDATE` and with Serializable plus retry. In each, exactly one booking succeeds and the other is told there are no seats.

**Done when:** your race test fails against the naive version and passes against both fixes, and you can say which fix you'd choose for a ticketing site with thousands of people trying to book the same concert at once, and why.

<details>
<summary>Hints — after your attempt</summary>

- The naive race: both sessions `SELECT id FROM seats WHERE booked_by IS NULL` before either `UPDATE`s.
- With `FOR UPDATE`, add `SKIP LOCKED` to let the second booking move straight on to the next free seat instead of waiting: the standard way to hand out rows from a queue.
- Under heavy contention for one row, Serializable aborts most attempts and retries pile up; locking (with `SKIP LOCKED` where possible) usually behaves better.

</details>

## Before moving on

You can say what each part of ACID guards against, name the five anomalies from a trace, say what each PostgreSQL level prevents and costs, fix a lost update four ways, and retry a serialization failure correctly.

**Recap.** A transaction is all-or-nothing against failures (atomicity, durability) and shielded from other transactions to the degree its isolation level says. PostgreSQL's default, Read Committed, takes a snapshot per statement: no dirty reads, but non-repeatable reads, phantoms, lost updates and write skew all happen. Repeatable Read takes one snapshot per transaction and refuses conflicting writes with a serialization failure; Serializable (SSI) also catches write skew. Fix lost updates with SQL arithmetic, `FOR UPDATE`, a stronger level, or a version column. And whenever the database can say "try again", retry the whole transaction.

**Next.** [[databases/09-mvcc-and-concurrency-control/index|MVCC and concurrency control]]: how PostgreSQL keeps all these snapshots without readers and writers blocking each other, and what that costs.

## Related

- [[databases/09-mvcc-and-concurrency-control/index|MVCC and concurrency control]]: how isolation is actually implemented
- [[databases/10-durability-and-recovery|Durability and recovery]]: the A and D of ACID
- [[architecture/04-distributed-systems/04-consistency-models|Consistency models]]: the same problem across machines
- [[databases/index|Databases map]]
