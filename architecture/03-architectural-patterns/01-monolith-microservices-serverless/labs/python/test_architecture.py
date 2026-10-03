import unittest

from architecture import (Module, Pricing, boundary_violations, break_even_requests, cold_share, coordination_links,
                          extract, find_cycle, release_breaks, serverless_monthly, simulate_cold_share)

PRICE = Pricing(per_million_requests=0.2, per_gb_second=0.0000166667)


class Architecture(unittest.TestCase):
    def test_coordination_grows_with_the_square(self):
        self.assertEqual([coordination_links(n) for n in [4, 8, 50]], [6, 28, 1_225])

    def test_a_shared_release_breaks_more_often(self):
        self.assertEqual(f"{release_breaks(40, 0.01) * 100:.1f}", "33.1")
        self.assertEqual(f"{release_breaks(5, 0.01) * 100:.1f}", "4.9")

    def test_chatty_versus_coarse(self):
        ms, availability = extract(40, 1, 0.9999)
        self.assertEqual((ms, f"{availability * 100:.2f}"), (40, "99.60"))
        ms, availability = extract(1, 1, 0.9999)
        self.assertEqual((ms, f"{availability * 100:.2f}"), (1, "99.99"))

    def test_serverless_until_traffic_is_steady(self):
        self.assertEqual(f"{serverless_monthly(1_000_000, 200, 0.5, PRICE):.2f}", "1.87")
        self.assertEqual(f"{serverless_monthly(50_000_000, 200, 0.5, PRICE):.2f}", "93.33")
        self.assertEqual(round(break_even_requests(30, 200, 0.5, PRICE) / 1e5) / 10, 16.1)

    def test_cold_starts_hit_quiet_functions(self):
        self.assertEqual([f"{cold_share(r, 5) * 100:.2f}" for r in [10, 1, 0.1]], ["0.00", "0.67", "60.65"])
        for rate in [1, 0.1]:
            self.assertLess(abs(simulate_cold_share(rate, 5, 100_000, 7) - cold_share(rate, 5)), 0.005)

    def test_boundaries_and_cycles(self):
        shop = [Module("orders", ["billing", "catalog/internal/prices"]), Module("billing", ["customers"]),
                Module("catalog", ["catalog/internal/prices"]), Module("customers")]
        self.assertEqual(boundary_violations(shop), ["orders → catalog/internal/prices"])
        self.assertIsNone(find_cycle(shop))
        shop[3].imports.append("orders")
        self.assertEqual(find_cycle(shop), ["orders", "billing", "customers", "orders"])


if __name__ == "__main__":
    unittest.main()
