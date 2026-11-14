import unittest

from rates import FlakyApi, build


class StackTests(unittest.TestCase):
    def test_two_failures_then_cached(self):
        api, log = FlakyApi(failures=2), []
        rate = build(api, log)
        self.assertEqual(rate("GBP", "NGN"), 2000)
        self.assertEqual(rate("GBP", "NGN"), 2000)   # served by functools.cache
        self.assertEqual(api.calls, 3)
        self.assertEqual(log, ["GBP->NGN = 2000", "GBP->NGN = 2000"])

    def test_too_many_failures_still_fail(self):
        rate = build(FlakyApi(failures=5), [])
        with self.assertRaises(ConnectionError):
            rate("GBP", "NGN")


if __name__ == "__main__":
    unittest.main()
