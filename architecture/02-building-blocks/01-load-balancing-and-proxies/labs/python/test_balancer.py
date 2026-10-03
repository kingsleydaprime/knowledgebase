import unittest

from balancer import (Health, HashRing, NoHealthyServers, least_outstanding, modulo, pick_healthy, random_pick,
                      round_robin, simulate, smooth_weighted, two_choices)

KEYS = [f"user:{i}" for i in range(10_000)]
FOUR = ["cache-a", "cache-b", "cache-c", "cache-d"]


class Balancing(unittest.TestCase):
    def test_round_robin_takes_turns_least_outstanding_looks(self):
        pick, queues = round_robin(), [5, 0, 0]
        self.assertEqual([pick(queues, None) for _ in range(6)], [0, 1, 2, 0, 1, 2])
        self.assertEqual(least_outstanding(queues, None), 1)

    def test_smooth_weighted_round_robin(self):
        pick = smooth_weighted({"a": 5, "b": 1, "c": 1})
        self.assertEqual("".join(pick() for _ in range(7)), "aabacaa")

    def test_algorithms_that_look_at_queues_win_in_the_tail(self):
        run = lambda pick: simulate(pick, 4, 0.8, 100_000, 7)
        self.assertEqual(run(round_robin()), {"mean": 214, "p50": 138, "p99": 1_158})
        self.assertEqual(run(random_pick), {"mean": 255, "p50": 159, "p99": 1_588})
        self.assertEqual(run(least_outstanding), {"mean": 68, "p50": 17, "p99": 466})
        self.assertEqual(run(two_choices), {"mean": 96, "p50": 25, "p99": 495})

    def test_three_failures_to_go_down_two_successes_to_come_back(self):
        health = Health(3, 2)
        for ok in [False, False, True, False, False]:
            health.record(ok)
        self.assertTrue(health.up)
        health.record(False)
        self.assertFalse(health.up)
        health.record(True)
        self.assertFalse(health.up)
        health.record(True)
        self.assertTrue(health.up)

    def test_skips_down_servers_and_fails_when_all_are_down(self):
        servers = [(name, Health(3, 2)) for name in ["app-1", "app-2", "app-3"]]
        for _ in range(3):
            servers[1][1].record(False)
        self.assertEqual([pick_healthy(servers, t) for t in range(4)], ["app-1", "app-3", "app-1", "app-3"])
        for _, health in servers:
            for _ in range(3):
                health.record(False)
        with self.assertRaises(NoHealthyServers):
            pick_healthy(servers, 0)

    def test_modulo_moves_four_in_five_a_ring_about_one_in_five(self):
        five = FOUR + ["cache-e"]
        moved_by_modulo = sum(modulo(k, FOUR) != modulo(k, five) for k in KEYS)
        self.assertLess(abs(moved_by_modulo - 8_000), 200)
        ring = HashRing(FOUR, 100)
        before = [ring.server_for(k) for k in KEYS]
        ring.add("cache-e")
        moved = [k for k, b in zip(KEYS, before) if ring.server_for(k) != b]
        self.assertLess(abs(len(moved) - 2_000), 300)
        self.assertTrue(all(ring.server_for(k) == "cache-e" for k in moved))
        ring.remove("cache-e")
        self.assertEqual([ring.server_for(k) for k in KEYS], before)

    def test_virtual_nodes_even_out_the_keys(self):
        def busiest(replicas):
            ring, counts = HashRing(FOUR, replicas), {}
            for k in KEYS:
                counts[ring.server_for(k)] = counts.get(ring.server_for(k), 0) + 1
            return max(counts.values()) / (len(KEYS) / 4)

        self.assertGreater(busiest(1), 1.4)
        self.assertLess(busiest(100), 1.2)


if __name__ == "__main__":
    unittest.main()
