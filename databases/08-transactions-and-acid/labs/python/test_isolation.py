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
