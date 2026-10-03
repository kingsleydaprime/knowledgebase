import sqlite3
import unittest

from outbox import (Crash, FakeBroker, IdempotentConsumer, count_orders, open_db, place_order_publish_then_save,
                    place_order_save_then_publish, place_order_with_outbox, relay)


class Outbox(unittest.TestCase):
    def test_save_then_publish_loses_the_event(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaises(Crash):
            place_order_save_then_publish(db, broker, "o1", 500_000, crash_between=True)
        self.assertEqual((count_orders(db), len(broker.sent)), (1, 0))

    def test_publish_then_save_leaves_a_phantom(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "CHECK constraint failed"):
            place_order_publish_then_save(db, broker, "o2", -1)
        self.assertEqual((count_orders(db), len(broker.sent)), (0, 1))

    def test_outbox_a_crash_before_the_relay_loses_nothing(self):
        db, broker = open_db(), FakeBroker()
        place_order_with_outbox(db, "o3", 500_000)
        self.assertEqual(relay(db, broker), 1)
        self.assertEqual(broker.sent, [{"eventId": "evt-o3", "type": "OrderPlaced", "orderId": "o3"}])
        self.assertEqual(relay(db, broker), 0)

    def test_outbox_a_failed_order_rolls_back_its_event(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "CHECK constraint failed"):
            place_order_with_outbox(db, "o4", -1)
        self.assertEqual((count_orders(db), relay(db, broker)), (0, 0))

    def test_relay_crash_sends_twice_consumer_applies_once(self):
        db, broker = open_db(), FakeBroker()
        place_order_with_outbox(db, "o5", 500_000)
        with self.assertRaises(Crash):
            relay(db, broker, crash_before_mark=True)
        relay(db, broker)
        self.assertEqual(len(broker.sent), 2)
        consumer = IdempotentConsumer()
        self.assertEqual([consumer.handle(e) for e in broker.sent], ["applied", "duplicate"])
        self.assertEqual(consumer.applied, ["o5"])


if __name__ == "__main__":
    unittest.main()
