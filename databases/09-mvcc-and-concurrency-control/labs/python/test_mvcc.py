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
