"""The same ideas, checked on a real PostgreSQL 18 with a million rows. Run through ../shared/with-postgres.sh."""
import json
import unittest

import psycopg

SETUP = """
CREATE EXTENSION IF NOT EXISTS pageinspect;
CREATE TABLE orders AS
SELECT i AS id, i % 50000 AS customer_id,
       timestamptz '2026-01-01 00:00Z' + i * interval '30 seconds' AS created_at,
       (i::bigint * 7919 % 10000)::int AS total,       -- i * 7919 alone overflows a 32-bit integer
       CASE WHEN i % 100 = 0 THEN 'pending' ELSE 'complete' END AS status,
       'User' || i || '@Example.com' AS email
FROM generate_series(1, 1000000) AS i;
ALTER TABLE orders ADD PRIMARY KEY (id);
VACUUM ANALYZE orders;
"""


def nodes(plan: dict):
    """Every node of an EXPLAIN plan, top first."""
    yield plan
    for child in plan.get("Plans", []):
        yield from nodes(child)


class Postgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg.connect(autocommit=True)  # PGHOST etc. come from with-postgres.sh
        for statement in SETUP.split(";\n"):  # one at a time: several in one call run as one transaction,
            if statement.strip():  # and VACUUM refuses to run inside a transaction
                cls.db.execute(statement)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def explain(self, sql: str) -> list[dict]:
        row = self.db.execute(f"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}").fetchone()
        plan = row[0] if isinstance(row[0], list) else json.loads(row[0])
        return list(nodes(plan[0]["Plan"]))

    def pages(self, plan: list[dict]) -> int:
        top = plan[0]
        return top["Shared Hit Blocks"] + top["Shared Read Blocks"]  # the top node's counts include its children's

    def test_a_million_row_index_has_three_levels_and_a_lookup_reads_four_pages(self):
        level = self.db.execute("SELECT level FROM bt_metap('orders_pkey')").fetchone()[0]
        self.assertEqual(level, 2)  # the root is at level 2: levels 2, 1 and 0 (the leaves)
        plan = self.explain("SELECT * FROM orders WHERE id = 424242")
        self.assertEqual(plan[0]["Node Type"], "Index Scan")
        self.assertEqual(self.pages(plan), 4)  # three index pages, then the table page with the row

    def test_a_composite_index_serves_its_leading_column_not_the_second_alone(self):
        self.db.execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
        try:
            both = self.explain("SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'")
            self.assertIn("orders_customer_created", [n.get("Index Name") for n in both])
            second = self.explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
            self.assertEqual(second[0]["Node Type"], "Seq Scan")  # 50,000 customers to skip through: not worth it
        finally:
            self.db.execute("DROP INDEX orders_customer_created")

    def test_skip_scan_uses_an_index_without_its_leading_column_when_that_has_few_values(self):
        self.db.execute("CREATE INDEX orders_status_created ON orders (status, created_at)")
        try:
            plan = self.explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
            self.assertEqual((plan[0]["Node Type"], plan[0]["Index Name"]), ("Index Scan", "orders_status_created"))
            self.assertEqual(plan[0]["Actual Rows"], 120)
            self.assertLess(self.pages(plan), 50)  # a few searches, one per status value: 21 pages; a full scan reads 10,310
        finally:
            self.db.execute("DROP INDEX orders_status_created")

    def test_an_index_only_scan_needs_a_vacuumed_table(self):
        self.db.execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
        try:
            self.db.execute("VACUUM orders")
            clean = self.explain("SELECT total FROM orders WHERE customer_id = 42")
            self.assertEqual((clean[0]["Node Type"], clean[0]["Heap Fetches"]), ("Index Only Scan", 0))
            self.db.execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42")  # pages no longer all-visible
            dirty = self.explain("SELECT total FROM orders WHERE customer_id = 42")
            self.assertGreater(dirty[0]["Heap Fetches"], 0)  # it had to check the table after all
        finally:
            self.db.execute("DROP INDEX orders_customer_total")
            self.db.execute("VACUUM orders")

    def test_the_planner_refuses_an_index_that_matches_most_rows(self):
        self.db.execute("CREATE INDEX orders_status ON orders (status)")
        try:
            self.db.execute("ANALYZE orders")
            self.assertEqual(self.explain("SELECT * FROM orders WHERE status = 'complete'")[0]["Node Type"], "Seq Scan")  # 99%
            self.assertEqual(self.explain("SELECT * FROM orders WHERE status = 'pending'")[0]["Node Type"], "Index Scan")  # 1%
        finally:
            self.db.execute("DROP INDEX orders_status")

    def test_a_function_on_the_column_needs_an_expression_index(self):
        self.db.execute("CREATE INDEX orders_email ON orders (email)")
        try:
            query = "SELECT * FROM orders WHERE lower(email) = 'user42@example.com'"
            self.assertEqual(self.explain(query)[0]["Node Type"], "Seq Scan")  # the index on email doesn't help
            self.db.execute("CREATE INDEX orders_email_lower ON orders (lower(email))")
            self.db.execute("ANALYZE orders")
            self.assertEqual(self.explain(query)[0]["Node Type"], "Index Scan")
        finally:
            self.db.execute("DROP INDEX IF EXISTS orders_email; DROP INDEX IF EXISTS orders_email_lower")

    def test_a_partial_index_is_a_fraction_of_the_size(self):
        self.db.execute("CREATE INDEX orders_pending ON orders (created_at) WHERE status = 'pending'")
        self.db.execute("CREATE INDEX orders_created ON orders (created_at)")
        try:
            partial, full = self.db.execute("SELECT pg_relation_size('orders_pending'), pg_relation_size('orders_created')").fetchone()
            self.assertLess(partial / full, 0.02)  # 1% of the rows, about 1% of the size
        finally:
            self.db.execute("DROP INDEX orders_pending; DROP INDEX orders_created")

    def test_every_index_is_paid_for_on_every_write(self):
        self.db.execute("""
            CREATE TABLE plain (id int PRIMARY KEY, a int, b int, c int, d int);
            CREATE TABLE indexed (id int PRIMARY KEY, a int, b int, c int, d int);
            CREATE INDEX ON indexed (a); CREATE INDEX ON indexed (b); CREATE INDEX ON indexed (c); CREATE INDEX ON indexed (d);
        """)
        wal = []
        for table in ["plain", "indexed"]:
            before = self.db.execute("SELECT pg_current_wal_insert_lsn()").fetchone()[0]
            self.db.execute(f"INSERT INTO {table} SELECT i, i * 31 % 1000, i * 37 % 1000, i * 41 % 1000, i * 43 % 1000 FROM generate_series(1, 10000) i")
            wal.append(self.db.execute("SELECT pg_wal_lsn_diff(pg_current_wal_insert_lsn(), %s)", [before]).fetchone()[0])
        self.assertGreater(wal[1] / wal[0], 2.5)  # four more indexes: about three times the log written


if __name__ == "__main__":
    unittest.main()
