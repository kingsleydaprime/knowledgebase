import asyncio
import unittest

from resilience import INF, Bulkhead, BulkheadFull, simulate, workers_needed

HEALTHY = {"ticks": 600, "arrivals_per_tick": {"search": 2, "profile": 3}, "service_ticks": {"search": 2, "profile": 1}, "client_timeout_ticks": 20}
DEGRADED = {**HEALTHY, "service_ticks": {"search": 50, "profile": 1}}  # search's dependency now takes 5 s
SHARED = {"pools": {"search": "shared", "profile": "shared"}, "sizes": {"shared": 50}}
BULKHEADS = {"pools": {"search": "search", "profile": "profile"}, "sizes": {"search": 20, "profile": 30}, "queue_limit": 10, "dependency_timeout_ticks": 30}


class Resilience(unittest.IsolatedAsyncioTestCase):
    def test_littles_law(self):
        self.assertEqual([workers_needed(20, 0.2) + workers_needed(30, 0.1), workers_needed(20, 5), workers_needed(20, 3), workers_needed(20, 1)],
                         [7, 100, 60, 20])

    def test_the_same_numbers_as_typescript(self):
        healthy = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": INF}, HEALTHY)
        self.assertEqual((healthy["search"]["ok"], healthy["profile"]["ok"]), (1196, 1797))
        cascade = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": INF}, DEGRADED)
        self.assertEqual((cascade["profile"]["ok"], cascade["profile"]["timedOut"]), (72, 1668))
        self.assertEqual(simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": 30}, DEGRADED)["profile"]["ok"], 270)
        one = simulate({**SHARED, "queue_limit": INF, "dependency_timeout_ticks": 10}, DEGRADED)
        self.assertEqual((one["profile"]["ok"], one["search"]["failed"]), (1797, 1180))
        walls = simulate(BULKHEADS, DEGRADED)
        self.assertEqual((walls["profile"]["ok"], walls["search"]["failed"], walls["search"]["timedOut"], walls["search"]["rejected"]), (1797, 380, 190, 600))

    async def test_a_limit_a_short_queue_and_an_immediate_no(self):
        bulkhead, gates = Bulkhead(2, 1), []

        async def work():
            gate = asyncio.Event()
            gates.append(gate)
            await gate.wait()
            return "done"

        tasks = [asyncio.create_task(bulkhead.run(work)) for _ in range(3)]
        await asyncio.sleep(0)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (2, 1))
        with self.assertRaises(BulkheadFull):
            await bulkhead.run(work)
        while gates or not all(t.done() for t in tasks):
            if gates:
                gates.pop(0).set()
            await asyncio.sleep(0)
        self.assertEqual([await t for t in tasks], ["done"] * 3)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (0, 0))

    async def test_a_freed_place_goes_to_the_waiter_not_a_latecomer(self):
        bulkhead, running, most, gates = Bulkhead(1, 1), 0, 0, []

        async def work():
            nonlocal running, most
            running += 1
            most = max(most, running)
            gate = asyncio.Event()
            gates.append(gate)
            await gate.wait()
            running -= 1

        first = asyncio.create_task(bulkhead.run(work))
        waiter = asyncio.create_task(bulkhead.run(work))
        await asyncio.sleep(0)
        gates.pop(0).set()  # first finishes...
        latecomer = asyncio.create_task(bulkhead.run(work))  # ...and someone arrives at the same moment
        for _ in range(5):
            await asyncio.sleep(0)
        self.assertEqual(most, 1)
        while gates or not all(t.done() for t in (first, waiter, latecomer)):
            if gates:
                gates.pop(0).set()
            await asyncio.sleep(0)
        self.assertEqual((bulkhead.active, len(bulkhead.waiting)), (0, 0))

    async def test_a_caller_who_gives_up_does_not_take_a_place_with_them(self):
        bulkhead, gate = Bulkhead(1, 1), asyncio.Event()
        first = asyncio.create_task(bulkhead.run(gate.wait))
        await asyncio.sleep(0)
        with self.assertRaises(TimeoutError):
            await asyncio.wait_for(bulkhead.run(gate.wait), timeout=0.01)  # the client gives up
        gate.set()
        await first
        self.assertEqual(bulkhead.active, 0)  # the place came back instead of going to the caller who left


if __name__ == "__main__":
    unittest.main()
