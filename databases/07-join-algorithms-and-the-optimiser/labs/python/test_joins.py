import unittest

from joins import hash_join, index_nested_loop, independent_estimate, merge_join, nested_loop, rows_read_for_page

# 10,000 orders across 1,000 customers: the order's customer is its key.
ORDERS = [(1 + i % 1_000, f"order {i}") for i in range(10_000)]
CUSTOMERS = [(c, f"customer {c}") for c in range(1, 1_001)]


class Joins(unittest.TestCase):
    def test_all_three_algorithms_give_the_same_answer(self):
        expected = sorted(nested_loop(ORDERS, CUSTOMERS)[0])
        self.assertEqual(len(expected), 10_000)
        self.assertEqual(sorted(index_nested_loop(ORDERS, CUSTOMERS)[0]), expected)
        self.assertEqual(sorted(hash_join(ORDERS, CUSTOMERS)[0]), expected)
        self.assertEqual(sorted(merge_join(sorted(ORDERS), CUSTOMERS)[0]), expected)

    def test_they_differ_enormously_in_work(self):
        self.assertEqual(nested_loop(ORDERS, CUSTOMERS)[1], 10_000_000)  # N × M
        self.assertEqual(index_nested_loop(ORDERS, CUSTOMERS)[1], 99_780)  # about N × log₂ M = 10,000 × 10
        self.assertEqual(hash_join(ORDERS, CUSTOMERS)[1], 11_000)  # build 1,000, probe 10,000
        self.assertEqual(merge_join(sorted(ORDERS), CUSTOMERS)[1], 10_999)  # about N + M, once both are sorted

    def test_a_small_outer_side_makes_the_indexed_nested_loop_cheapest(self):
        one_customer = [row for row in ORDERS if row[0] == 42]  # 10 orders
        self.assertEqual(index_nested_loop(one_customer, CUSTOMERS)[1], 100)  # 10 lookups of 10 steps
        self.assertEqual(hash_join(one_customer, CUSTOMERS)[1], 1_010)  # still builds the whole table

    def test_correlated_columns_fool_the_independence_assumption(self):
        # 30,000 addresses in 10 cities; London is 10% of them, the UK is 30%, and every London address is in the UK.
        self.assertEqual(round(independent_estimate(30_000, 0.1, 0.3)), 900)  # what the planner assumes
        self.assertEqual(round(independent_estimate(30_000, 0.1)), 3_000)  # the truth: London implies the UK

    def test_offset_pagination_reads_everything_it_skips(self):
        self.assertEqual(rows_read_for_page(100_000, 20, keyset=False), 100_020)
        self.assertEqual(rows_read_for_page(100_000, 20, keyset=True), 20)


if __name__ == "__main__":
    unittest.main()
