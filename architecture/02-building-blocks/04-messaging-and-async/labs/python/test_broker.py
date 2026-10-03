import asyncio
import unittest

from broker import Broker, PartitionedLog, idempotent, level_load, partition_for


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def broker(clock=None):
    return Broker(clock or Clock(), visibility_ms=30_000, max_attempts=3)


class Messaging(unittest.IsolatedAsyncioTestCase):
    def test_queue_gives_each_message_to_one_consumer_topic_copies_it(self):
        b = broker()
        b.subscribe("orders", "invoices")
        b.subscribe("orders", "analytics")
        b.publish("orders", "order 1")
        b.publish("orders", "order 2")
        self.assertEqual([b.receive("invoices").body, b.receive("invoices").body], ["order 1", "order 2"])
        self.assertIsNone(b.receive("invoices"))
        self.assertEqual([b.receive("analytics").body, b.receive("analytics").body], ["order 1", "order 2"])
        b.publish("refunds", "refund 1")
        self.assertEqual(b.depth("invoices") + b.depth("analytics"), 4)

    def test_unacknowledged_comes_back_then_goes_to_the_dead_letter_queue(self):
        clock = Clock()
        b = broker(clock)
        b.subscribe("orders", "invoices")
        b.publish("orders", "order 1")
        self.assertEqual(b.receive("invoices").attempt, 1)
        self.assertIsNone(b.receive("invoices"))
        for now, attempt in [(30_000, 2), (60_000, 3)]:
            clock.now = now
            self.assertEqual(b.receive("invoices").attempt, attempt)
        clock.now = 90_000
        self.assertIsNone(b.receive("invoices"))
        self.assertEqual(b.dead_letters("invoices"), ["order 1"])
        self.assertEqual(b.depth("invoices"), 0)

    def test_crash_before_ack_charges_twice_unless_idempotent(self):
        for safe in [False, True]:
            clock = Clock()
            b = broker(clock)
            b.subscribe("orders", "payments")
            b.publish("orders", "charge £40 for order 1")
            charges = []
            charge = lambda body: charges.append(body)
            handle = idempotent(charge, set()) if safe else (lambda d: charge(d.body))
            handle(b.receive("payments"))  # charged, then the consumer crashes before acknowledging
            clock.now = 30_000
            again = b.receive("payments")
            handle(again)
            b.ack("payments", again.id)
            self.assertEqual(len(charges), 1 if safe else 2)

    def test_a_queue_absorbs_a_sale_spike(self):
        spike = [300] * 10 + [20] * 50
        two = level_load(spike, 100)
        self.assertEqual(two["sync"], {"served": 2_000, "rejected": 2_000})
        self.assertEqual(two["queued"], {"peak_depth": 2_000, "cleared_after_seconds": 35, "max_wait_seconds": 20})
        self.assertEqual(level_load(spike, 200)["queued"], {"peak_depth": 1_000, "cleared_after_seconds": 16, "max_wait_seconds": 5})

    def test_redelivery_reorders_a_partition_keeps_order_a_new_group_replays(self):
        clock = Clock()
        b = broker(clock)
        b.subscribe("orders", "shipping")
        for e in ["created", "paid", "shipped"]:
            b.publish("orders", f"order 7 {e}", "order-7")
        seen = []
        for fail in [False, True, False]:
            d = b.receive("shipping")
            if not fail:
                seen.append(d.body)
                b.ack("shipping", d.id)
        clock.now = 30_000
        seen.append(b.receive("shipping").body)
        self.assertEqual(seen, ["order 7 created", "order 7 shipped", "order 7 paid"])

        log = PartitionedLog(4)
        for e in ["created", "paid", "shipped"]:
            log.append("order-7", f"order 7 {e}")
        p, in_order, failed_once = partition_for("order-7", 4), [], False
        while (m := log.poll("shipping", p)) is not None:
            if m.endswith("paid") and not failed_once:
                failed_once = True  # no commit: the same message comes back
                continue
            in_order.append(m)
            log.commit("shipping", p)
        self.assertEqual(in_order, ["order 7 created", "order 7 paid", "order 7 shipped"])
        self.assertEqual(log.poll("analytics", p), "order 7 created")

    def test_a_key_always_lands_in_the_same_partition(self):
        self.assertEqual(partition_for("order-7", 4), partition_for("order-7", 4))
        counts = [0] * 4
        for i in range(10_000):
            counts[partition_for(f"order-{i}", 4)] += 1
        self.assertTrue(all(abs(n - 2_500) < 200 for n in counts), counts)

    async def test_asyncio_queue_pushes_back(self):
        q: asyncio.Queue[int] = asyncio.Queue(maxsize=3)
        accepted = []
        for n in [1, 2, 3, 4]:
            try:
                q.put_nowait(n)
                accepted.append(True)
            except asyncio.QueueFull:  # full: refused at once
                accepted.append(False)
        self.assertEqual(accepted, [True, True, True, False])
        self.assertEqual([q.get_nowait() for _ in range(3)], [1, 2, 3])

        events = []

        async def producer():
            for n in range(1, 6):
                await q.put(n)  # waits while the queue is full
                events.append(f"put {n}")

        task = asyncio.create_task(producer())
        for _ in range(5):
            await asyncio.sleep(0)  # let the producer run until it's blocked
        self.assertEqual(events, ["put 1", "put 2", "put 3"])
        events.append(f"took {await q.get()}")
        for _ in range(5):
            await asyncio.sleep(0)
        self.assertEqual(events[3:], ["took 1", "put 4"])
        for _ in range(4):
            await q.get()
        await task
        self.assertEqual(sum(e.startswith("put") for e in events), 5)
        self.assertTrue(q.empty())


if __name__ == "__main__":
    unittest.main()
