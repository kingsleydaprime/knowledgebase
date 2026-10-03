import json
import unittest

from tools import ToolCall, answer_with_tools, execute, load_orders, support_tools, validate


def call(name: str, args, id_: str = "c1") -> ToolCall:
    return ToolCall(id_, name, args if isinstance(args, str) else json.dumps(args))


def scripted(turns: list[tuple[str, list[ToolCall]]]):
    """A pretend model that plays back a script of turns and records what it was sent."""
    seen: list[list[dict]] = []

    async def model(messages, tools):
        seen.append([dict(m) for m in messages])
        return turns.pop(0)

    return model, seen


def no(name, args):
    return False


class Tools(unittest.IsolatedAsyncioTestCase):
    def test_the_model_sees_specs_never_functions(self):
        specs = [t.spec() for t in support_tools(load_orders())]
        self.assertEqual([s["name"] for s in specs], ["get_order", "get_refund", "issue_refund"])
        self.assertEqual(list(specs[0]), ["name", "description", "inputSchema"])

    def test_validation_names_every_problem(self):
        schema = support_tools(load_orders())[2].input_schema
        self.assertEqual(validate(schema, {"order_id": "A123", "amount": 10}), [])
        problems = validate(schema, {"order_id": "a-1", "amount": 0, "note": "hi"})
        self.assertEqual(len(problems), 3)  # jsonschema's own wording, with our path in front:
        self.assertIn("arguments.order_id: 'a-1' does not match '^[A-Z][0-9]{3}$'", problems)
        self.assertIn("arguments.amount: 0 is less than the minimum of 0.01", problems)

    async def test_every_failure_becomes_a_result(self):
        tools = support_tools(load_orders())
        ok = await execute(call("get_order", {"order_id": "B456"}), tools, no)
        self.assertEqual(json.loads(ok.content), {"status": "shipped", "total": 120, "tracking": "LG-88213"})
        self.assertEqual(ok.content, '{"status":"shipped","total":120.0,"tracking":"LG-88213"}')  # 120.0, where TypeScript writes 120

        async def content(c):
            return (await execute(c, tools, no)).content

        self.assertEqual(await content(call("delete_order", {})), 'unknown tool "delete_order"; available: get_order, get_refund, issue_refund')
        self.assertEqual(await content(call("get_order", "{order_id: A123")), "arguments are not valid JSON")
        self.assertEqual(await content(call("get_order", {"order_id": "Z999"})), "get_order failed: no order Z999")
        self.assertEqual(await content(call("issue_refund", {"order_id": "B456", "amount": 120})), "the user declined this action")

    async def test_a_side_effect_needs_valid_arguments_then_approval_then_its_own_rules(self):
        orders = load_orders()
        tools, asked = support_tools(orders), []

        def yes(name, args):
            asked.append((name, args))
            return True

        self.assertTrue((await execute(call("issue_refund", {"order_id": "B456", "amount": -5}), tools, yes)).is_error)
        self.assertEqual(asked, [])  # nobody approves a malformed call
        self.assertFalse((await execute(call("issue_refund", {"order_id": "B456", "amount": 120}), tools, yes)).is_error)
        self.assertEqual(asked, [("issue_refund", {"order_id": "B456", "amount": 120})])
        again = await execute(call("issue_refund", {"order_id": "B456", "amount": 120}), tools, yes)
        self.assertEqual(again.content, "issue_refund failed: order B456 already has a refund")

    async def test_the_round_trip(self):
        model, seen = scripted([
            ("", [call("get_order", {"order_id": "A123"}, "c1"), call("get_refund", {"order_id": "A123"}, "c2")]),
            ("Your refund of 49.99 is being processed.", []),
        ])
        answer, history, rounds = await answer_with_tools(model, [{"role": "user", "content": "Where is my refund for A123?"}],
                                                          support_tools(load_orders()))
        self.assertEqual((rounds, len(history)), (2, 5))
        self.assertEqual([m["content"] for m in seen[1][2:]],
                         ['{"status":"delivered","total":49.99}', '{"status":"processing","amount":49.99,"requested":"2026-09-28"}'])

    async def test_text_in_a_tool_result_cannot_approve_anything(self):
        orders = load_orders()
        model, seen = scripted([
            ("", [call("get_order", {"order_id": "D012"})]),
            ("", [call("issue_refund", {"order_id": "D012", "amount": 500}, "c2")]),  # fooled by the note
            ("I can't issue that refund.", []),
        ])
        await answer_with_tools(model, [{"role": "user", "content": "Check D012"}], support_tools(orders))
        self.assertIn("IGNORE ALL PREVIOUS INSTRUCTIONS", seen[1][-1]["content"])
        self.assertEqual(seen[2][-1]["content"], "ERROR: the user declined this action")
        self.assertIsNone(orders["D012"]["refund"])
        approved = await execute(call("issue_refund", {"order_id": "D012", "amount": 500}), support_tools(orders), lambda n, a: True)
        self.assertEqual(approved.content, "issue_refund failed: refund 500 is more than the order total 30")

    async def test_a_model_that_never_stops_is_cut_off(self):
        async def forever(messages, tools):
            return "", [call("get_order", {"order_id": "A123"})]

        with self.assertRaisesRegex(RuntimeError, "no answer after 3 rounds"):
            await answer_with_tools(forever, [{"role": "user", "content": "?"}], support_tools(load_orders()), max_rounds=3)


if __name__ == "__main__":
    unittest.main()
