import asyncio
import json
import unittest

from agent import Limits, refund_status, run_agent, score_trajectory
from tools import Tool, ToolCall, load_orders, support_tools


def call(name: str, args: dict, id_: str) -> ToolCall:
    return ToolCall(id_, name, json.dumps(args))


def scripted(turns: list):
    async def model(history, specs):
        return turns.pop(0)

    return model


ASK = [{"role": "user", "content": "Where is my refund for A123?"}]


class Agents(unittest.IsolatedAsyncioTestCase):
    async def test_a_two_step_answer_with_a_trace(self):
        model = scripted([
            ("", [call("get_order", {"order_id": "A123"}, "c1"), call("get_refund", {"order_id": "A123"}, "c2")], 0),
            ("Your refund of 49.99 is being processed.", [], 0),
        ])
        outcome = await run_agent(model, ASK, support_tools(load_orders()))
        self.assertEqual(outcome.status, "answered")
        self.assertEqual([[n for n, _, _ in s.calls] for s in outcome.trace], [["get_order", "get_refund"], []])
        self.assertEqual(score_trajectory(outcome, "answered", ("get_refund",), ("issue_refund",), 3), [])

    async def test_reads_run_together_and_a_side_effect_waits(self):
        log = []

        def slow(name, side_effects, seconds):
            async def run(args):
                log.append(f"start {name}")
                await asyncio.sleep(seconds)
                log.append(f"end {name}")
                return name
            return Tool(name, name, {"type": "object"}, side_effects, run)

        tools = [slow("read_a", False, 0.03), slow("read_b", False, 0.01), slow("write_c", True, 0.001)]
        model = scripted([("", [call("write_c", {}, "1"), call("read_a", {}, "2"), call("read_b", {}, "3")], 0), ("done", [], 0)])
        outcome = await run_agent(model, [{"role": "user", "content": "go"}], tools, approve=lambda n, a: True)
        self.assertEqual(log, ["start read_a", "start read_b", "end read_b", "end read_a", "start write_c", "end write_c"])
        self.assertEqual([m["tool_call_id"] for m in outcome.messages if m["role"] == "tool"], ["1", "2", "3"])

    async def test_a_step_limit_stops_a_wandering_agent(self):
        n = iter(range(100, 200))

        async def wandering(history, specs):
            i = next(n)
            return "", [call("get_order", {"order_id": f"A{i}"}, f"c{i}")], 0

        outcome = await run_agent(wandering, ASK, support_tools(load_orders()), Limits(max_steps=3, max_tokens=10**9, max_repeats=5))
        self.assertEqual((outcome.status, len(outcome.trace)), ("step_limit", 3))
        self.assertEqual(score_trajectory(outcome, status="answered"), ["ended step_limit, expected answered"])

    async def test_the_same_call_again_and_again_is_stuck(self):
        async def repeating(history, specs):
            return "", [call("get_refund", {"order_id": "Z999"}, "x")], 0

        outcome = await run_agent(repeating, ASK, support_tools(load_orders()), Limits(max_steps=20, max_tokens=10**9, max_repeats=2))
        self.assertEqual((outcome.status, len(outcome.trace)), ("stuck", 3))

    async def test_a_token_budget(self):
        model = scripted([
            ("", [call("get_order", {"order_id": "A123"}, "c1")], 25_500),
            ("", [call("get_order", {"order_id": "B456"}, "c2")], 25_500),
            ("never reached", [], 25_500),
        ])
        outcome = await run_agent(model, ASK, support_tools(load_orders()), Limits(max_steps=10, max_tokens=50_000, max_repeats=2))
        self.assertEqual((outcome.status, [s.tokens for s in outcome.trace]), ("token_limit", [25_500, 25_500]))

    async def test_the_scorer_names_each_broken_expectation(self):
        model = scripted([("", [call("issue_refund", {"order_id": "B456", "amount": 120}, "c1")], 0), ("I've asked for a refund.", [], 0)])
        outcome = await run_agent(model, ASK, support_tools(load_orders()))
        self.assertEqual(score_trajectory(outcome, must_call=("get_refund",), must_not_call=("issue_refund",), answer_matches="(?i)no refund"),
                         ["never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund"])

    async def test_the_workflow(self):
        tools, prompts = support_tools(load_orders()), []

        async def write(prompt):
            prompts.append(prompt)
            return "Your refund of 49.99 for A123 is being processed."

        answered = await refund_status("Where is my refund for order a123?", tools, write)
        self.assertEqual(answered, {"kind": "answer", "text": "Your refund of 49.99 for A123 is being processed.", "model_calls": 1, "tool_calls": 1})
        self.assertIn('Refund: {"status":"processing","amount":49.99,"requested":"2026-09-28"}', prompts[0])
        self.assertEqual((await refund_status("Has my refund come through?", tools, write))["kind"], "ask")
        # "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
        self.assertEqual(await refund_status("Can you change my delivery address?", tools, write), {"kind": "handoff", "reason": "classified as feature"})
        await refund_status("Where is my refund for D012?", tools, write)
        self.assertNotIn("IGNORE", prompts[-1])  # the injected note is on the order, which this workflow never reads
        self.assertEqual(len(prompts), 2)


if __name__ == "__main__":
    unittest.main()
