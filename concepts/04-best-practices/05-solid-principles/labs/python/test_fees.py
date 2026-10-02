import unittest

from fees import OPEN_RULES, Method, fee


class FeeTests(unittest.TestCase):
    def test_both_designs_agree(self):
        self.assertEqual(OPEN_RULES["card"](10_000), 290)
        self.assertEqual(fee(Method.CARD, 10_000), 290)
        self.assertEqual(fee(Method.TRANSFER, 10_000), 50)


if __name__ == "__main__":
    unittest.main()
