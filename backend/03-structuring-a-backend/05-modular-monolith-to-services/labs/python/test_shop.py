import unittest

from shop import AtLeastOnceBus, InProcessBus, Orders, Payments


class BusTests(unittest.TestCase):
    def test_in_process_delivers_once(self):
        bus = InProcessBus()
        orders = Orders(bus, idempotent=False)
        Payments(bus).record_success("o1", 500_000)
        self.assertEqual(orders.paid["o1"], 500_000)

    def test_at_least_once_with_a_naive_consumer_double_counts(self):
        bus = AtLeastOnceBus()
        orders = Orders(bus, idempotent=False)
        Payments(bus).record_success("o1", 500_000)
        self.assertEqual(orders.paid["o1"], 1_000_000)

    def test_idempotent_consumer_counts_once_but_still_counts_a_real_second_payment(self):
        bus = AtLeastOnceBus()
        orders = Orders(bus, idempotent=True)
        payments = Payments(bus)
        payments.record_success("o1", 500_000)
        payments.record_success("o1", 250_000)
        self.assertEqual(orders.paid["o1"], 750_000)


if __name__ == "__main__":
    unittest.main()
