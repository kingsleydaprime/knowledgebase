import math
import unittest

from scaling import amdahl, mean, percentile, response_time, seeded, simulate_server, throughput, usl, usl_peak


def round_half_up(x: float) -> int:
    return math.floor(x + 0.5)  # Python's round() sends halves to the even number; JavaScript's goes up


class Scaling(unittest.TestCase):
    def test_percentiles_by_nearest_rank(self):
        tens = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]
        self.assertEqual([percentile(tens, p) for p in [50, 90, 99, 100]], [5, 9, 10, 10])
        with self.assertRaises(ValueError):
            percentile([], 50)

    def test_the_average_hides_the_tail(self):
        random = seeded(42)
        latencies = []
        for _ in range(1_000):
            slow = random() < 0.02
            latencies.append(1_500 + 1_000 * random() if slow else 40 + 20 * random())
        got = [round_half_up(x) for x in [mean(latencies), *(percentile(latencies, p) for p in [50, 95, 99])]]
        self.assertEqual(got, [93, 50, 59, 2_208])

    def test_waiting_grows_slowly_then_all_at_once(self):
        self.assertEqual([round_half_up(response_time(10, b)) for b in [0.5, 0.8, 0.9, 0.95, 0.99]], [20, 50, 100, 200, 1_000])
        self.assertEqual(response_time(10, 1), math.inf)

    def test_the_simulation_agrees_with_the_formula(self):
        for busy in [0.5, 0.8, 0.9]:
            sim, model = simulate_server(10, busy, 200_000, 7), response_time(10, busy)
            self.assertLess(abs(sim["mean"] - model) / model, 0.1)
            self.assertLess(abs(sim["p99"] / sim["mean"] - math.log(100)), 0.5)

    def test_performance_or_scalability(self):
        got = [response_time(300, 0.1), response_time(10, 0.95), response_time(10, 0.95 / 2), response_time(300, 0.05)]
        self.assertEqual([round_half_up(x) for x in got], [333, 200, 19, 316])

    def test_the_slowest_stage(self):
        stages = [("load balancer", 50_000), ("app servers", 4 * 800), ("database writes", 2_000)]
        self.assertEqual(throughput(stages), (2_000, "database writes"))
        stages[1] = ("app servers", 8 * 800)
        self.assertEqual(throughput(stages), (2_000, "database writes"))

    def test_why_adding_machines_stops_helping(self):
        self.assertEqual(f"{amdahl(8, 0.05):.2f}", "5.93")
        self.assertLess(amdahl(1_000_000, 0.05), 20)
        self.assertEqual(round_half_up(usl_peak(0.05, 0.001)), 31)
        self.assertEqual([f"{usl(n, 0.05, 0.001):.1f}" for n in [8, 31, 60, 100]], ["5.7", "9.0", "8.0", "6.3"])


if __name__ == "__main__":
    unittest.main()
