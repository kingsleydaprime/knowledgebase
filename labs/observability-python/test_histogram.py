import unittest

from histogram import cumulative_buckets, estimate_quantile, exposition, record

# The main lesson's 100 requests: 97 between 20 and 29 ms, then 1800, 2100 and 3000 ms.
LATENCIES = [20 + i % 10 for i in range(97)] + [1800, 2100, 3000]


class HistogramTests(unittest.TestCase):
    def test_bucket_estimates_versus_exact(self):
        buckets = cumulative_buckets(record(LATENCIES))
        # Buckets are "le": less than or equal. 60 requests are <= 25 ms, so p50 lands inside it.
        self.assertAlmostEqual(estimate_quantile(0.50, buckets), 20.83, places=2)  # exact: 24
        self.assertEqual(estimate_quantile(0.99, buckets), 2500.0)  # exact: 2100

    def test_the_scrape_format(self):
        text = exposition(record(LATENCIES))
        self.assertIn('request_duration_ms_bucket{le="25.0"} 60.0', text)
        self.assertIn('request_duration_ms_bucket{le="2500.0"} 99.0', text)
        self.assertIn("request_duration_ms_count 100.0", text)


if __name__ == "__main__":
    unittest.main()
