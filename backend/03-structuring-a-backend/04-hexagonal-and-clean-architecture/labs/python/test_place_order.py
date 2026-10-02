import unittest

from shop.adapters.memory import FakePayments, InMemoryOrders
from shop.domain import PaymentDeclined, place_order


class PlaceOrderTests(unittest.TestCase):
    def test_paid_order_is_saved(self):
        orders = InMemoryOrders()
        order = place_order(orders, FakePayments(1_000_000), "o1", "c1", 250_000)
        self.assertTrue(order.paid)
        self.assertEqual(len(orders.saved), 1)

    def test_declined_saves_nothing(self):
        orders = InMemoryOrders()
        with self.assertRaises(PaymentDeclined):
            place_order(orders, FakePayments(100), "o2", "c1", 250_000)
        self.assertEqual(orders.saved, [])


if __name__ == "__main__":
    unittest.main()
