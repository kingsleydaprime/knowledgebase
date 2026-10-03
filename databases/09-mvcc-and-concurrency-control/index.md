# MVCC and Concurrency Control

**[Advanced]** — How isolation is actually implemented: row versions instead of read locks, why PostgreSQL needs `VACUUM` and what stops it, why every PostgreSQL update can touch every index, where deadlocks come from, and the migration lock that takes production down. Every PostgreSQL behaviour here is checked by the lab, which looks directly at the row versions on a page.

## Before you start

You can already:

- Explain isolation levels, snapshots and serialization failures, and fix a lost update with `FOR UPDATE` → [[databases/08-transactions-and-acid/index|transactions and ACID]].
- Read an index-only scan's `Heap Fetches`, and say what the visibility map is for → [[databases/04-b-trees-and-indexes/index|B-trees and indexes]].
- Run Python with `uv`, and have PostgreSQL 16 or later installed locally.

After this lesson you will be able to:

1. Explain how a row version's `xmin` and `xmax` and a transaction's snapshot decide what that transaction sees, and why readers and writers don't block each other.
2. Say what `VACUUM` does, what stops it working, and why a forgotten open transaction can bloat every table.
3. Explain a HOT update, and why a PostgreSQL update that changes one indexed column writes a new entry in every index.
4. Prevent deadlocks by lock ordering, and run a schema migration without queueing every query behind it.

**Study route:** sections 1–4 explain versions and snapshots. Stop at the predictions in sections 5, 6 and 8 and try them before reading on. Section 10 is the lab.

## The kid version

A class notice board has one sheet per pupil. Instead of rubbing out and rewriting a sheet, the teacher pins a new one on top, marked with the time, and leaves the old one underneath. Anyone who started reading at 9:00 keeps reading the sheets as they were at 9:00, even if new ones go up at 9:05, so nobody has to wait for the teacher to finish, and the teacher doesn't wait for the readers. At the end of the day a caretaker takes down the old sheets nobody is still reading.

**Where the analogy stops working.** On a notice board you'd notice the pile getting thick. In PostgreSQL, the old versions build up silently inside the table's pages, and if one reader never finishes, say a forgotten open transaction, the caretaker may take down *nothing*, anywhere in the database, until that reader leaves.

## 1. Why this exists

The shop's nightly report reads every order for twenty minutes. Meanwhile, customers keep placing and updating orders. With locks alone, the report's read locks would block every order update for twenty minutes, or the updates would block the report. Neither is acceptable. Almost every modern database solves this the same way: keep several versions of each row, so the report reads the versions as they were when it started while customers write new ones. That's MVCC, and it works so well that it's easy to forget it has costs: dead versions to clean up, a cleaner that can be blocked, and updates that rewrite more than you'd think.

## Terms used in this lesson

1. **MVCC (multiversion concurrency control)**: The letters stand for those words. It's keeping several versions of each row, so that each transaction can read the versions that match its snapshot without locking anything.
2. **Row version**: This is also called a **tuple**. It's one stored copy of a row as it was after one particular change.
3. **`xmin` and `xmax`**: These are the IDs of the transaction that created a row version and the one that deleted or replaced it. `xmax` is empty while the version is current.
4. **Dead tuple**: This is a row version that no current or future snapshot can see any more. It still takes up space until it's cleaned up.
5. **`VACUUM`**: This is PostgreSQL's clean-up: it removes dead tuples so their space can be reused, updates the visibility map, and freezes old transaction IDs.
6. **`ctid`**: This is a row version's physical address in PostgreSQL: (page number, position on the page).
7. **HOT update**: This stands for heap-only tuple. It's an update where no indexed column changed and the new version fits on the same page, so the indexes don't need new entries.
8. **Pruning**: This is PostgreSQL removing dead versions from a page during an ordinary read or write of that page, without waiting for `VACUUM`.
9. **Deadlock**: This is two or more transactions each waiting for a lock another one holds, so none can ever continue.
10. **Lock queue**: This is the line of sessions waiting for a lock on the same object. A session waiting for a strong lock makes later sessions wait behind it, even for weak locks.
11. **Transaction ID wraparound**: PostgreSQL's transaction IDs are 32-bit and count round after about 4 billion. Old rows must be "frozen" before then, or they would seem to come from the future.

## 2. Two approaches

**Pessimistic: two-phase locking.** Take locks before touching data, and hold them until commit. **The problem: readers block writers and writers block readers.** A long report blocks every update to the rows it reads, and concurrency collapses under mixed workloads.

**Optimistic: MVCC.** Keep multiple versions of each row. Readers see the version that was current when their snapshot began.

> **The MVCC rule, and it's the whole idea:**
>
> **Readers never block writers. Writers never block readers.**
>
> **Writers still block writers** on the same row; that part is unavoidable.

In the lab, session A opens a Repeatable Read transaction and reads a balance of 100. Session B, with a 100 ms lock timeout so any wait would fail, updates the balance to 50 and finishes at once. A reads again: still 100. A commits and reads: 50. But when A holds an uncommitted update on row 1, B's update of row 1 fails its lock timeout, while B's update of row 2 goes straight through.

**Essentially every modern database uses MVCC**: PostgreSQL, InnoDB, Oracle, SQL Server (optionally), CockroachDB, and MongoDB's WiredTiger.

## 3. How MVCC works

**Each row version carries visibility information:**

| Field | Meaning |
|---|---|
| `xmin` | the transaction that **created** this version |
| `xmax` | the transaction that **deleted or replaced** it (or empty) |

**A transaction has a snapshot**: the set of transactions that had committed at the moment it began. In words: a version is visible if the transaction that created it had committed by your snapshot, and the transaction that replaced it, if any, hadn't.

**An `UPDATE` doesn't change a row in place.** It writes a **new version** and sets `xmax` on the old one. **The old version stays** until nobody can see it any more:

```
 Row id=1, updated twice:

 version A: xmin=100, xmax=200   balance=100   ← old snapshots see this
 version B: xmin=200, xmax=300   balance=90
 version C: xmin=300, xmax=null  balance=80    ← current
```

**A transaction whose snapshot was taken when 200 was the latest committed transaction sees version B**, whatever has happened since. **That's a consistent snapshot with no locks taken.**

The lab looks at this directly. Every row exposes the hidden columns `xmin` and `ctid`, and the `pageinspect` extension shows every version stored on a page. After an update, the row has a new `xmin` and a new `ctid`: a new version, in a new place. While another session's snapshot still needs the old version, the page holds **one more version than before**. Once that snapshot ends and `VACUUM` runs, the count is back to where it started.

## 4. PostgreSQL and InnoDB

**Both use MVCC. They store the old versions in completely different places, and every operational difference follows from that.**

| | **PostgreSQL** | **InnoDB** |
|---|---|---|
| Old versions live | **in the table itself** | **in the undo log** (separate) |
| An update writes | **a whole new row version** | the new row in place + an undo record |
| Reading an old version | it's just another tuple | **rebuild it by applying undo** |
| Clean-up | **`VACUUM`** | the purge thread |
| Indexes on update | **every index gets a new entry** (unless HOT) | **only the affected indexes** |

**The consequences:**

- **PostgreSQL updates can be expensive.** A new row version has a new address, so **every index needs an entry pointing to it**, even indexes on columns that didn't change. **HOT updates avoid this** when no indexed column changed *and* the new version fits on the same page, which is why a lower fill factor (leaving free space in each page) helps update-heavy tables → [[databases/03-storage-and-page-layout|fill factor]].
- **PostgreSQL tables bloat.** Dead versions take up space until they're cleaned up.
- **InnoDB's long-running transactions bloat the undo log instead**, and reading very old versions gets slower as more undo records must be applied.

**Neither is strictly better.** They're different trades, and knowing which engine you're on tells you which operational problem to expect.

**Predict before reading on.** A table has a primary key on `id` and an index on `email`, and was created with `fillfactor = 90`. Row 1 is updated twice: first its `balance` (not indexed), then its `email`. How many entries for row 1 does the *primary key* index hold after each update?

<details>
<summary>After your prediction</summary>

After the `balance` update: still **1**. It was a HOT update: no indexed column changed and the new version fit on the page, so no index was touched, and PostgreSQL follows a chain from the old version to the new one. After the `email` update: **2**. Changing an indexed column means a non-HOT update, and then *every* index gets an entry for the new version, including the primary key, whose value didn't change. The lab counts the entries with `pageinspect`'s `bt_page_items`.

</details>

## 5. `VACUUM`, and what stops it

**PostgreSQL-specific, and the source of most PostgreSQL operational pain.** What it does:

1. **Reclaims dead tuples**, marking their space reusable. It doesn't return space to the operating system; that needs `VACUUM FULL`, which locks the table exclusively.
2. **Updates the visibility map**, which is what makes **index-only scans** possible → [[databases/04-b-trees-and-indexes/index|index-only scans]].
3. **Updates statistics**, with `ANALYZE`.
4. **Freezes old transaction IDs**, and this one is critical (section 6).

Dead versions can also disappear sooner: when a page is nearly full, an ordinary read or write of it may **prune** dead versions that no snapshot can see. It's opportunistic, and only `VACUUM` guarantees it.

**Predict before reading on.** Session A opens a Repeatable Read transaction and runs `SELECT 1`, touching no table at all. Session B updates all 1,000 rows of `accounts`, then runs `VACUUM accounts`. How many dead versions does `VACUUM` leave?

<details>
<summary>After your prediction</summary>

**All 1,000.** A's snapshot was taken at its first statement and covers the whole database, not just the tables it reads. PostgreSQL can't know A won't read `accounts` next, so every old version stays. `pgstattuple` reports a `dead_tuple_count` of 1,000 after the vacuum. Once A commits and B vacuums again, it's 0. **That's why one forgotten `BEGIN` in an idle session blocks clean-up across the entire database.**

</details>

**What blocks vacuum:**

- **A long-running transaction**, whatever it reads.
- **Idle-in-transaction sessions**, hence `idle_in_transaction_session_timeout`.
- **Abandoned replication slots**: a disconnected replica whose slot still exists holds back both the write-ahead log and vacuum.
- **Long queries on replicas** with `hot_standby_feedback = on`.

**Autovacuum** runs vacuum automatically, triggered by the fraction of rows changed. **The defaults are conservative for large tables**: 20% of a billion-row table is 200 million dead rows before it starts. **Tune `autovacuum_vacuum_scale_factor` down for big tables**, or set per-table thresholds. **Monitor** `pg_stat_user_tables` for `n_dead_tup` and `last_autovacuum`, and `pg_stat_activity` for long transactions.

## 6. Transaction ID wraparound

> **PostgreSQL's transaction IDs are 32-bit.** IDs are compared within a window of about 2 billion either side, so **rows must be "frozen" (marked as older than everything) before their ID falls out of that window, or they'd suddenly seem to come from the future and become invisible**: silent data loss.
>
> **PostgreSQL protects against this by refusing new writes** as wraparound approaches:
> ```
> ERROR: database is not accepting commands that assign new transaction IDs to avoid wraparound data loss
> ```
> **This has taken down production systems**, famously Sentry in 2015 and Mailchimp's Mandrill in 2019. **It happens when autovacuum can't keep up or has been disabled.** **Monitor `age(datfrozenxid)`.** Modern versions handle it far better and the risk is lower, but the failure mode is worth knowing.

## 7. Locking

**MVCC removes read locks. Write locks remain.**

**Row-level locks:**

| Lock | Taken by | Conflicts with |
|---|---|---|
| `FOR UPDATE` | explicit, or `UPDATE`/`DELETE` | other row locks |
| `FOR NO KEY UPDATE` | an `UPDATE` not touching a key | `FOR UPDATE` |
| `FOR SHARE` | explicit | `FOR UPDATE` |
| `FOR KEY SHARE` | **foreign-key checks** | `FOR UPDATE` |

**Table-level locks** range from `ACCESS SHARE`, taken by a plain `SELECT`, to `ACCESS EXCLUSIVE`, taken by `DROP`, `TRUNCATE` and most `ALTER TABLE`.

**InnoDB adds gap locks and next-key locks** at Repeatable Read, locking the *gaps between* index entries to prevent phantoms. **They cause deadlocks that surprise people**, because you can conflict on rows that don't exist.

## 8. The migration that queues everything

**Predict before reading on.** Session A has an open transaction that ran `SELECT count(*) FROM accounts`. Session B runs `ALTER TABLE accounts ADD COLUMN note text`. Session C then runs `SELECT count(*) FROM accounts`. A's lock and C's lock don't conflict with each other. Does C's query run?

<details>
<summary>After your prediction</summary>

**No.** B's `ALTER TABLE` needs an `ACCESS EXCLUSIVE` lock, so it waits for A. And **every new query on the table, even a plain `SELECT`, queues behind B**, because PostgreSQL grants locks in order and C's lock conflicts with the one B is waiting for. In the lab, C (with a 200 ms lock timeout) fails with `LockNotAvailable`. One slow transaction plus one migration has stopped all reads of the table. When A commits, B runs and the queue drains.

**The fix is one line:** give the migration a `lock_timeout`, so it gives up and can be retried instead of building a queue:

```sql
SET lock_timeout = '3s';
ALTER TABLE ...;
```

In the lab, B with a 200 ms `lock_timeout` fails fast, and C's reads carry on untouched. **This line prevents a large share of migration-caused outages.**

</details>

## 9. Deadlocks

**Two transactions each holding a lock the other wants:**

```
T1: locks row A ─────────► wants row B
T2: locks row B ─────────► wants row A
```

**After waiting `deadlock_timeout` (1 second by default), PostgreSQL looks for a cycle in the graph of who is waiting for whom, and cancels one transaction**, the *deadlock victim*, with a `deadlock detected` error. The other gets its lock and continues. In the lab, exactly one of the two sessions gets `DeadlockDetected`. **This is a normal outcome, not a bug**, and the application must retry the victim's transaction.

**Prevention:**

- **Lock rows in a consistent order.** If every transaction locks accounts in ascending ID order, **no cycle can form**: the second transaction simply waits its turn at the first row. In the lab, two sessions both running `SELECT … WHERE id IN (1, 2) ORDER BY id FOR UPDATE` never deadlock; the second just waits. This is the structural fix, worth enforcing as a convention.
- **Keep transactions short**, so less time is spent holding locks.
- **Take the strongest lock first**, rather than upgrading a shared lock to an exclusive one mid-transaction, a classic deadlock source.
- **Use `SELECT … FOR UPDATE` deliberately**, rather than relying on whatever order statements happen to lock rows in.

**Debug them:** PostgreSQL logs both queries of a deadlock by default, and `SHOW ENGINE INNODB STATUS` shows the last one in MySQL. **The log tells you exactly which two statements conflicted**, which usually makes the ordering fix obvious.

## 10. The lab: MVCC, looked at directly

`test_mvcc.py` uses two or three sessions. Where a session must block, it runs in a thread, and the test waits until `pg_stat_activity` reports it waiting for a lock before taking the next step, so the order of events is exact. It uses `pageinspect` to count row versions on a page and index entries, and `pgstattuple` to count dead tuples. It shares the [`with-postgres.sh`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/shared) throwaway cluster, which turns autovacuum off, so dead versions stay until the test vacuums.

```python
"""MVCC on a real PostgreSQL 18, looked at directly: row versions on the page, snapshots, what blocks vacuum,
HOT updates, deadlocks, and the DDL lock queue. Run through ../shared/with-postgres.sh.
Connections are stepped one statement at a time; where a session must block, it runs in a thread, and the test
waits until PostgreSQL reports it waiting before going on."""
import threading
import time
import unittest

import psycopg
from psycopg import errors


def connect() -> psycopg.Connection:
    return psycopg.connect(autocommit=True)  # every BEGIN and COMMIT below is explicit


def value(conn: psycopg.Connection, sql: str, params=()) -> object:
    return conn.execute(sql, params).fetchone()[0]


def wait_until_blocked(watcher: psycopg.Connection, pid: int) -> None:
    """Waits until the session with this backend pid is waiting for a lock: the moment to take the next step."""
    for _ in range(500):
        if value(watcher, "SELECT wait_event_type FROM pg_stat_activity WHERE pid = %s", [pid]) == "Lock":
            return
        time.sleep(0.01)
    raise AssertionError(f"session {pid} never waited for a lock")


class Mvcc(unittest.TestCase):
    def setUp(self):
        self.a, self.b = connect(), connect()
        self.a.execute("""
            CREATE EXTENSION IF NOT EXISTS pageinspect;
            CREATE EXTENSION IF NOT EXISTS pgstattuple;
            DROP TABLE IF EXISTS accounts;
            CREATE TABLE accounts (id int PRIMARY KEY, email text NOT NULL, balance int NOT NULL) WITH (fillfactor = 90);
            CREATE INDEX accounts_email ON accounts (email);
            INSERT INTO accounts SELECT i, 'user' || i || '@example.com', 100 FROM generate_series(1, 1000) i;
        """)
        self.a.execute("VACUUM accounts")  # on its own: VACUUM can't run in the transaction a multi-statement call makes

    def tearDown(self):
        self.a.close()
        self.b.close()

    def versions_on_page(self, page: int = 0) -> int:
        """Row versions physically present on a heap page, live or dead."""
        return value(self.a, "SELECT count(*) FROM heap_page_items(get_raw_page('accounts', %s)) WHERE t_data IS NOT NULL", [page])

    def test_an_update_writes_a_new_version_and_the_old_one_stays_while_a_snapshot_needs_it(self):
        before = self.versions_on_page()
        self.b.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        self.assertEqual(value(self.b, "SELECT balance FROM accounts WHERE id = 1"), 100)  # b's snapshot needs version 1
        xmin, ctid = self.a.execute("SELECT xmin::text, ctid::text FROM accounts WHERE id = 1").fetchone()
        self.a.execute("UPDATE accounts SET balance = 90 WHERE id = 1")
        new_xmin, new_ctid = self.a.execute("SELECT xmin::text, ctid::text FROM accounts WHERE id = 1").fetchone()
        self.assertNotEqual((new_xmin, new_ctid), (xmin, ctid))  # a new version, by a new transaction, in a new place
        self.assertEqual(self.versions_on_page(), before + 1)  # the old one is still on the page...
        self.assertEqual(value(self.b, "SELECT balance FROM accounts WHERE id = 1"), 100)  # ...because b still reads it
        self.b.execute("COMMIT")  # now nobody needs the old version
        self.a.execute("VACUUM accounts")  # (a later read may prune it from the page sooner; VACUUM always does)
        self.assertEqual(self.versions_on_page(), before)

    def test_readers_and_writers_dont_block_each_other(self):
        self.a.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        self.assertEqual(value(self.a, "SELECT balance FROM accounts WHERE id = 1"), 100)  # a's snapshot is taken here
        self.b.execute("SET lock_timeout = '100ms'")  # if b had to wait for a, this would raise
        self.b.execute("UPDATE accounts SET balance = 50 WHERE id = 1")  # finishes at once
        self.assertEqual(value(self.a, "SELECT balance FROM accounts WHERE id = 1"), 100)  # a still reads its version
        self.a.execute("COMMIT")
        self.assertEqual(value(self.a, "SELECT balance FROM accounts WHERE id = 1"), 50)

    def test_writers_still_block_writers(self):
        self.a.execute("BEGIN")
        self.a.execute("UPDATE accounts SET balance = 90 WHERE id = 1")
        self.b.execute("SET lock_timeout = '100ms'")
        with self.assertRaises(errors.LockNotAvailable):
            self.b.execute("UPDATE accounts SET balance = 80 WHERE id = 1")
        self.b.execute("UPDATE accounts SET balance = 80 WHERE id = 2")  # a different row: no conflict
        self.a.execute("COMMIT")

    def test_an_open_snapshot_stops_vacuum_removing_anything(self):
        self.a.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        value(self.a, "SELECT 1")  # a's snapshot exists from its first statement, whatever it reads
        self.b.execute("UPDATE accounts SET balance = balance + 1")  # 1,000 dead versions
        self.b.execute("VACUUM accounts")
        self.assertEqual(value(self.b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), 1000)  # all kept for a
        self.a.execute("COMMIT")
        self.b.execute("VACUUM accounts")
        self.assertEqual(value(self.b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), 0)

    def test_hot_updates_skip_the_indexes_other_updates_touch_them_all(self):
        def pkey_entries() -> int:  # entries in the primary key's index for row 1 (the index is small: one leaf)
            return value(self.a, "SELECT count(*) FROM bt_page_items('accounts_pkey', 1) WHERE data = '01 00 00 00 00 00 00 00'")

        self.assertEqual(pkey_entries(), 1)
        self.a.execute("UPDATE accounts SET balance = 1 WHERE id = 1")  # no indexed column changed: a HOT update
        self.assertEqual(pkey_entries(), 1)  # the index wasn't touched
        self.a.execute("UPDATE accounts SET email = 'new@example.com' WHERE id = 1")  # an indexed column changed
        self.assertEqual(pkey_entries(), 2)  # so every index gets a new entry, even the primary key, whose value didn't change

    def test_a_deadlock_is_detected_and_one_transaction_is_chosen_as_the_victim(self):
        for conn in (self.a, self.b):
            conn.execute("SET deadlock_timeout = '100ms'")  # how long to wait before checking for a cycle
        self.a.execute("BEGIN")
        self.b.execute("BEGIN")
        self.a.execute("UPDATE accounts SET balance = 1 WHERE id = 1")  # a holds row 1
        self.b.execute("UPDATE accounts SET balance = 2 WHERE id = 2")  # b holds row 2
        outcome: dict[str, BaseException | None] = {}

        def a_wants_row_2():
            try:
                self.a.execute("UPDATE accounts SET balance = 1 WHERE id = 2")
                outcome["a"] = None
            except psycopg.Error as e:
                outcome["a"] = e

        waiting = threading.Thread(target=a_wants_row_2)
        waiting.start()
        wait_until_blocked(self.b, self.a.info.backend_pid)
        try:
            self.b.execute("UPDATE accounts SET balance = 2 WHERE id = 1")  # b wants row 1: a cycle
            outcome["b"] = None
        except psycopg.Error as e:
            outcome["b"] = e
        waiting.join()
        victims = [who for who, error in outcome.items() if isinstance(error, errors.DeadlockDetected)]
        self.assertEqual(len(victims), 1)  # exactly one was rolled back; the other got its row
        for conn in (self.a, self.b):
            conn.execute("ROLLBACK")

    def test_locking_rows_in_the_same_order_cannot_deadlock(self):
        self.a.execute("BEGIN")
        self.a.execute("SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE")  # both rows, in id order
        self.b.execute("BEGIN")
        self.b.execute("SET LOCAL lock_timeout = '100ms'")
        with self.assertRaises(errors.LockNotAvailable):  # b simply waits its turn at row 1; no cycle is possible
            self.b.execute("SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE")
        self.b.execute("ROLLBACK")
        self.a.execute("COMMIT")

    def test_a_waiting_alter_table_blocks_every_query_queued_behind_it(self):
        c = connect()
        self.a.execute("BEGIN")
        self.a.execute("SELECT count(*) FROM accounts")  # a holds a weak lock until it commits
        alter_error: list[BaseException] = []

        def alter():
            try:
                self.b.execute("ALTER TABLE accounts ADD COLUMN note text")  # needs an exclusive lock: waits for a
            except psycopg.Error as e:
                alter_error.append(e)

        waiting = threading.Thread(target=alter)
        waiting.start()
        wait_until_blocked(c, self.b.info.backend_pid)
        c.execute("SET lock_timeout = '200ms'")
        with self.assertRaises(errors.LockNotAvailable):  # a plain SELECT now queues behind the waiting ALTER
            c.execute("SELECT count(*) FROM accounts")
        self.a.execute("COMMIT")  # a finishes; the ALTER runs; the queue drains
        waiting.join()
        self.assertEqual(alter_error, [])
        self.assertEqual(value(c, "SELECT count(*) FROM accounts"), 1000)

        # The fix: give the migration a lock_timeout, so it gives up instead of building a queue.
        self.a.execute("BEGIN")
        self.a.execute("SELECT count(*) FROM accounts")
        self.b.execute("SET lock_timeout = '200ms'")
        with self.assertRaises(errors.LockNotAvailable):
            self.b.execute("ALTER TABLE accounts ADD COLUMN another text")
        self.assertEqual(value(c, "SELECT count(*) FROM accounts"), 1000)  # nothing queued: reads carry on
        self.a.execute("COMMIT")
        c.close()


if __name__ == "__main__":
    unittest.main()
```

**Lab:** the code is in [`databases/09-mvcc-and-concurrency-control/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/python). From the vault root, `python3 labs/run.py mvcc-and-concurrency-control/python` runs it and checks this page still shows the same code. It needs PostgreSQL 16 or later installed. Expect 8 passing tests in a couple of seconds.

## Common pitfalls

1. **An open transaction left idle.** It blocks vacuum database-wide. Set `idle_in_transaction_session_timeout`.
2. **Schema migrations without `lock_timeout`.** One slow query plus one `ALTER TABLE` stops all access to the table.
3. **Indexing a frequently updated column without thinking.** Every update of it becomes non-HOT and writes to every index.
4. **Locking rows in whatever order the code happens to reach them.** Sort first.
5. **Treating deadlocks and serialization failures as bugs.** They're expected: retry.
6. **Leaving autovacuum at its defaults for a billion-row table.** Hundreds of millions of dead rows build up before it starts.
7. **Forgetting replication slots for replicas that no longer exist.** They hold back vacuum and fill the disk with log.

## Check your understanding

1. A Repeatable Read transaction reads a row, and another session updates it and commits. Why can the update finish without waiting, and what does the first transaction see if it reads again?
2. Why does a PostgreSQL update that changes only an indexed `email` column add an entry to the primary-key index?
3. A session ran `BEGIN; SELECT 1;` an hour ago and is idle. Why can't vacuum clean up tables it never touched?
4. Why does a waiting `ALTER TABLE` stop plain `SELECT`s that don't conflict with the transaction it's waiting for?
5. Two transactions transfer money between accounts 1 and 2, in opposite directions. How do they deadlock, and what one change to the code prevents it?
6. What's a HOT update, and what two conditions does it need?

<details>
<summary>Answers — after your attempt</summary>

1. The update writes a new row version rather than changing the one the reader is using, so it needs no lock that conflicts with reading. The reader keeps seeing the old version, the one its snapshot says is visible, until it commits.
2. A non-HOT update puts the new version at a new physical address (`ctid`), and PostgreSQL's indexes point at physical addresses. So every index needs an entry for the new address, whether or not its own column changed.
3. Its snapshot was taken at its first statement and applies to the whole database. PostgreSQL can't know which tables it will read next, so it must keep every version that snapshot might need, everywhere.
4. Locks on a table are granted in queue order. The `ALTER TABLE` is waiting for an `ACCESS EXCLUSIVE` lock, and a new `SELECT`'s `ACCESS SHARE` lock conflicts with that, so it queues behind it, even though it doesn't conflict with the transaction holding things up.
5. One locks account 1 and wants 2; the other locks 2 and wants 1: a cycle. Always lock both accounts in ascending ID order, for example with `SELECT … WHERE id IN (1, 2) ORDER BY id FOR UPDATE` at the start, so the second transfer simply waits for the first.
6. An update that creates the new version without new index entries, linked from the old version on the same page. It needs no indexed column to have changed, and room on the same page for the new version.

</details>

## Practice — independent task

**Find what's blocking, in a real database.**

1. In two `psql` sessions on your flagship's development database, reproduce a lock wait: session 1 updates a row inside an open transaction, session 2 updates the same row.
2. From a third session, write one query on `pg_stat_activity` and `pg_locks` (or `pg_blocking_pids(pid)`) that shows which session is blocked, which session blocks it, how long it's waited, and the blocker's last query.
3. Reproduce an idle open transaction, update rows in another session, and show with `pg_stat_user_tables` or `pgstattuple` that vacuum can't clean them, then that it can once the idle transaction ends.

**Done when:** you have your blocking query saved somewhere you'll find it during an incident, the two experiments written up with their numbers, and the `idle_in_transaction_session_timeout` you'd set for your project and why.

<details>
<summary>Hints — after your attempt</summary>

- `SELECT pid, pg_blocking_pids(pid), wait_event_type, now() - query_start, query FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;` is most of it. Join back to `pg_stat_activity` for the blocker's query.
- `VACUUM (VERBOSE) table` reports how many dead row versions "cannot be removed yet".

</details>

## Before moving on

You can explain how versions and snapshots let readers and writers work without blocking, say what vacuum does and what blocks it, explain HOT updates and why PostgreSQL updates touch every index, prevent deadlocks by ordering, and run a migration with `lock_timeout`.

**Recap.** MVCC keeps several versions of each row, marked with the transactions that created and replaced them, so each transaction reads its snapshot's versions without read locks: readers and writers don't block each other, though writers still block writers. PostgreSQL keeps old versions in the table, so updates write whole new versions (touching every index unless the update is HOT), dead versions accumulate, and `VACUUM` must clean them up. Any open snapshot, anywhere, stops that. Freeze old transaction IDs before wraparound. Deadlocks are detected and one transaction is cancelled; consistent lock order prevents them. And a waiting `ALTER TABLE` queues every query behind it unless it has a `lock_timeout`.

**Next.** Week 7, the web end to end: [[networking/10-dns-in-depth|DNS]], [[networking/11-http-evolution|HTTP]] and [[networking/12-tls-and-transport-security|TLS]].

## Related

- [[databases/08-transactions-and-acid/index|Transactions and ACID]]: the guarantees this implements
- [[databases/10-durability-and-recovery|Durability and recovery]]: the log underneath
- [[databases/12-operating-a-database|Operating a database]]: vacuum, bloat and monitoring in production
- [[os/06-concurrency-primitives|Concurrency primitives]]: locks one layer down
- [[databases/index|Databases map]]
