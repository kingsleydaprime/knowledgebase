import unittest

from orders import IllegalTransition, Order


class OrderTests(unittest.TestCase):
    def test_observers_and_history(self):
        audit = []
        order = Order("o1")
        order.on_change(lambda oid, a, b: audit.append(f"{a.value}->{b.value}"))
        for action in ("pay", "ship", "deliver"):
            order.apply(action)
        self.assertEqual(audit, ["pending->paid", "paid->shipped", "shipped->delivered"])
        self.assertEqual(list(order.history()), ["pending", "paid", "shipped", "delivered"])

    def test_illegal_transition_is_rejected_and_not_announced(self):
        audit = []
        order = Order("o2")
        order.on_change(lambda *e: audit.append(e))
        order.apply("pay"); order.apply("ship")
        with self.assertRaises(IllegalTransition):
            order.apply("cancel")
        self.assertEqual(len(audit), 2)


if __name__ == "__main__":
    unittest.main()
