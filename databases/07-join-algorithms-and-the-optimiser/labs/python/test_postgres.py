"""How PostgreSQL 18 chooses joins, and where its estimates go wrong. Run through ../shared/with-postgres.sh."""
import json
import unittest

import psycopg

SETUP = """
CREATE TABLE customers AS
SELECT i AS id, 'Customer ' || i AS name, i * 37 % 5000 AS credit_limit FROM generate_series(1, 50000) i;
ALTER TABLE customers ADD PRIMARY KEY (id);
CREATE TABLE orders AS
SELECT i AS id, 1 + i % 50000 AS customer_id, (i::bigint * 7919 % 10000)::int AS total FROM generate_series(1, 1000000) i;
ALTER TABLE orders ADD PRIMARY KEY (id);
CREATE INDEX orders_customer_id ON orders (customer_id);
CREATE TABLE addresses AS
SELECT i AS id,
       (ARRAY['London','Manchester','Leeds','Paris','Lyon','Lille','Berlin','Munich','Hamburg','Cologne'])[1 + i % 10] AS city,
       (ARRAY['UK','UK','UK','France','France','France','Germany','Germany','Germany','Germany'])[1 + i % 10] AS country
FROM generate_series(1, 30000) i;
VACUUM ANALYZE customers;
VACUUM ANALYZE orders;
ANALYZE addresses
"""


def nodes(plan: dict):
    yield plan
    for child in plan.get("Plans", []):
        yield from nodes(child)


class Postgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = psycopg.connect(autocommit=True)
        for statement in SETUP.split(";\n"):  # one at a time: VACUUM can't run inside a multi-statement call
            cls.db.execute(statement)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def explain(self, sql: str, analyze: bool = True) -> list[dict]:
        options = "ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON" if analyze else "FORMAT JSON"
        row = self.db.execute(f"EXPLAIN ({options}) {sql}").fetchone()
        plan = row[0] if isinstance(row[0], list) else json.loads(row[0])
        return list(nodes(plan[0]["Plan"]))

    def types(self, plan: list[dict]) -> list[str]:
        return [n["Node Type"] for n in plan]

    def test_large_to_large_on_equality_is_a_hash_join(self):
        plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")
        self.assertIn("Hash Join", self.types(plan))
        hash_node = next(n for n in plan if n["Node Type"] == "Hash")
        self.assertEqual(hash_node["Hash Batches"], 1)  # the 50,000 customers fit in work_mem (4 MB by default)

    def test_too_little_memory_and_the_hash_join_spills_to_disk(self):
        self.db.execute("SET work_mem = '64kB'")
        try:
            plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")
            hash_node = next(n for n in plan if n["Node Type"] == "Hash")
            self.assertEqual(hash_node["Hash Batches"], 16)  # split into 16 partitions, joined one at a time
            self.assertGreater(plan[0]["Temp Written Blocks"], 0)  # written to temporary files and read back
        finally:
            self.db.execute("RESET work_mem")

    def test_a_small_outer_side_is_a_nested_loop_through_an_index(self):
        plan = self.explain("SELECT c.name, o.total FROM orders o JOIN customers c ON c.id = o.customer_id WHERE o.customer_id = 42")
        self.assertEqual(plan[0]["Node Type"], "Nested Loop")
        self.assertEqual(plan[0]["Actual Rows"], 20)
        self.assertLess(plan[0]["Shared Hit Blocks"] + plan[0]["Shared Read Blocks"], 50)  # a few dozen pages, not thousands

    def test_an_inequality_join_can_only_be_a_nested_loop(self):
        plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON o.total < c.credit_limit WHERE c.id < 10 AND o.id < 1000", analyze=False)
        self.assertIn("Nested Loop", self.types(plan))
        self.assertFalse({"Hash Join", "Merge Join"} & set(self.types(plan)))  # neither works on '<' in PostgreSQL

    def test_a_merge_join_when_hashing_is_ruled_out_and_both_sides_come_sorted(self):
        self.db.execute("SET enable_hashjoin = off")  # a session setting for experiments, never for production
        try:
            plan = self.explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id", analyze=False)
            merge = next(n for n in plan if n["Node Type"] == "Merge Join")
            self.assertEqual({p["Node Type"] for p in merge["Plans"]}, {"Index Only Scan"})  # sorted by the indexes: no sort
        finally:
            self.db.execute("RESET enable_hashjoin")

    def test_correlated_columns_are_underestimated_until_the_planner_is_told(self):
        query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'"
        before = self.explain(query)[0]
        self.assertEqual((before["Plan Rows"], before["Actual Rows"]), (900, 3000))  # 10% × 30%: assumed independent
        self.db.execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses")
        self.db.execute("ANALYZE addresses")
        after = self.explain(query)[0]
        self.assertEqual((after["Plan Rows"], after["Actual Rows"]), (3000, 3000))  # city decides country: now exact

    def test_offset_reads_every_row_it_skips_keyset_pagination_does_not(self):
        offset = self.explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20")
        keyset = self.explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20")
        self.assertEqual((offset[1]["Actual Rows"], keyset[1]["Actual Rows"]), (100020, 20))  # the scans under each Limit
        self.assertGreater(offset[0]["Shared Hit Blocks"] + offset[0]["Shared Read Blocks"], 800)
        self.assertLess(keyset[0]["Shared Hit Blocks"] + keyset[0]["Shared Read Blocks"], 10)


if __name__ == "__main__":
    unittest.main()
