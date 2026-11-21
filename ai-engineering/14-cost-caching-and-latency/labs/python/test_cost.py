import json
import statistics
import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from cost import (PRICES, Tier, break_even_calls, cascade, cost, percentile, shared_prefix, stable_json,
                  time_stream)

sys.path.insert(0, str(Path(__file__).parents[3] / "12-evals" / "labs" / "python"))
from evals import keywords, load_golden  # noqa: E402  the shared golden set and the keyword rules

SONNET = PRICES["claude-sonnet-5-5"]


class Cost(unittest.IsolatedAsyncioTestCase):
    def test_output_costs_five_times_input(self):
        self.assertEqual(cost(SONNET, input_tokens=2000, output_tokens=500), Decimal("0.009"))

    def test_caching_a_6000_token_prefix_across_1000_calls(self):
        uncached = 1000 * cost(SONNET, input_tokens=6150, output_tokens=100)
        first = cost(SONNET, cache_write_tokens=6000, input_tokens=150, output_tokens=100)
        each = cost(SONNET, cache_read_tokens=6000, input_tokens=150, output_tokens=100)
        cached = first + sum([each] * 999)
        self.assertEqual((uncached, cached), (Decimal("13.30"), Decimal("2.5138")))  # exact, to the last digit
        self.assertEqual(round(1000 * cost(SONNET, output_tokens=100) / cached * 100), 40)

        # The same sum in floats drifts: a running total of 999 small amounts isn't 2.5138.
        float_total = float(first) + sum([float(each)] * 999)
        self.assertNotEqual(float_total, 2.5138)
        self.assertAlmostEqual(float_total, 2.5138, places=9)

    def test_a_cache_write_pays_for_itself_on_the_second_call(self):
        self.assertEqual(break_even_calls(SONNET), 2)
        one_hour = replace(SONNET, cache_write=Decimal("4"))  # 1-hour entries cost 2× to write
        self.assertEqual(break_even_calls(one_hour), 3)

    def test_a_timestamp_at_the_front_leaves_nothing_to_cache(self):
        system = "You classify support tickets. Label by what the team has to do next. " * 20
        front = lambda date: f"Today is {date}.\n{system}\nhelp"  # noqa: E731
        end = lambda date: f"{system}\nToday is {date}.\nhelp"  # noqa: E731
        a, b = "2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z"
        self.assertEqual(shared_prefix(front(a), front(b)), 27)
        self.assertEqual(shared_prefix(end(a), end(b)), len(system) + 28)

    def test_unsorted_json_changes_the_bytes(self):
        a = {"tools": ["search"], "user": {"tier": "pro", "id": 7}}
        b = {"user": {"id": 7, "tier": "pro"}, "tools": ["search"]}
        self.assertNotEqual(json.dumps(a), json.dumps(b))
        self.assertEqual(json.dumps(b, sort_keys=True), '{"tools": ["search"], "user": {"id": 7, "tier": "pro"}}')  # spaces
        self.assertEqual(stable_json(a), stable_json(b))
        self.assertEqual(stable_json(b), '{"tools":["search"],"user":{"id":7,"tier":"pro"}}')  # byte for byte what TypeScript gives

    def test_a_cascade_from_keywords_to_a_big_model(self):
        golden = load_golden()
        label = {c["ticket"]: c["label"] for c in golden}
        big = Tier("big", Decimal("0.002"), label.__getitem__, lambda a: True)  # a stand-in that is always right
        cheap = Tier("keywords", Decimal(0), keywords, lambda a: a != "other")
        results = [(c, *cascade(c["ticket"], [cheap, big])) for c in golden]
        self.assertEqual([c["id"] for c, _, by, _ in results if by == "big"], ["t04", "t10", "t12", "t14", "t17", "t19"])
        self.assertEqual([c["id"] for c, answer, _, _ in results if answer != c["label"]], ["t15", "t20"])
        self.assertEqual(sum(spent for *_, spent in results), Decimal("0.012"))

    def test_p95_and_why_libraries_disagree(self):
        ms = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000]
        self.assertEqual((percentile(ms, 50), percentile(ms, 95), statistics.mean(ms)), (1000, 9000, 1819))
        # Same data, other definitions of "p95". Say which one a dashboard uses.
        self.assertEqual(statistics.quantiles(ms, n=20)[-1], 12510)  # the default extrapolates past the slowest call
        self.assertAlmostEqual(statistics.quantiles(ms, n=20, method="inclusive")[-1], 5490)  # numpy's default too
        self.assertEqual(statistics.median(ms), 1010)  # the median interpolates between 1000 and 1020

    async def test_time_to_first_token_is_measured_apart(self):
        clock = {"t": 0}

        async def stream():
            clock["t"] += 800
            yield "Your"
            for word in [" refund", " is", " on", " its", " way."]:
                clock["t"] += 100
                yield word

        self.assertEqual(await time_stream(stream(), lambda: clock["t"]), ("Your refund is on its way.", 800, 1300))


if __name__ == "__main__":
    unittest.main()
