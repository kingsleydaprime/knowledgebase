"""Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
Arguments are checked with the jsonschema library instead of a hand-written validator."""
import inspect
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ORDERS = Path(__file__).parent.parent / "shared" / "orders.json"


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    side_effects: bool
    run: Callable[[dict], Any]

    def spec(self) -> dict:  # what the model sees: never `run` or `side_effects`
        return {"name": self.name, "description": self.description, "inputSchema": self.input_schema}


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # a JSON string, as models send it


@dataclass
class ToolResult:
    id: str
    content: str
    is_error: bool


Approve = Callable[[str, dict], bool | Awaitable[bool]]


def validate(schema: dict, value: Any) -> list[str]:
    """Every problem, as 'arguments.field: message'. The library finds them; we only format the path."""
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: list(e.absolute_path))
    return [".".join(["arguments", *map(str, e.absolute_path)]) + f": {e.message}" for e in errors]


async def execute(call: ToolCall, tools: list[Tool], approve: Approve, max_chars: int = 2000) -> ToolResult:
    def fail(content: str) -> ToolResult:
        return ToolResult(call.id, content, True)

    tool = next((t for t in tools if t.name == call.name), None)
    if tool is None:
        return fail(f'unknown tool "{call.name}"; available: {", ".join(t.name for t in tools)}')
    try:
        args = json.loads(call.arguments or "{}")
    except json.JSONDecodeError:
        return fail("arguments are not valid JSON")
    if problems := validate(tool.input_schema, args):
        return fail("; ".join(problems))
    if tool.side_effects:
        approved = approve(tool.name, args)
        if inspect.isawaitable(approved):
            approved = await approved
        if not approved:
            return fail("the user declined this action")
    try:
        result = tool.run(args)
        if inspect.isawaitable(result):
            result = await result
    except Exception as error:  # the message, never a traceback
        return fail(f"{tool.name} failed: {error}")
    content = json.dumps(result, separators=(",", ":"))
    return ToolResult(call.id, content[:max_chars] + " …[truncated]" if len(content) > max_chars else content, False)


def load_orders() -> dict:
    return json.loads(ORDERS.read_text())


ORDER_ID = {"type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits"}


def support_tools(orders: dict) -> list[Tool]:
    def find(order_id: str) -> dict:
        if order_id not in orders:
            raise LookupError(f"no order {order_id}")
        return orders[order_id]

    def issue_refund(args: dict) -> dict:
        order = find(args["order_id"])
        if order["refund"]:
            raise ValueError(f"order {args['order_id']} already has a refund")
        if args["amount"] > order["total"]:
            raise ValueError(f"refund {args['amount']:g} is more than the order total {order['total']:g}")
        order["refund"] = {"status": "processing", "amount": args["amount"], "requested": "today"}
        return order["refund"]

    one_id = {"type": "object", "properties": {"order_id": ORDER_ID}, "required": ["order_id"], "additionalProperties": False}
    return [
        Tool("get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
             one_id, False, lambda a: {k: v for k, v in find(a["order_id"]).items() if k != "refund"}),
        Tool("get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
             one_id, False, lambda a: find(a["order_id"])["refund"] or {"status": "none"}),
        Tool("issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
             {"type": "object", "properties": {"order_id": ORDER_ID, "amount": {"type": "number", "minimum": 0.01}},
              "required": ["order_id", "amount"], "additionalProperties": False},
             True, issue_refund),
    ]


# One model turn: text, and zero or more calls. No calls means "this is my answer".
Model = Callable[[list[dict], list[dict]], Awaitable[tuple[str, list[ToolCall]]]]


async def answer_with_tools(model: Model, messages: list[dict], tools: list[Tool], approve: Approve = lambda n, a: False,
                            max_rounds: int = 5) -> tuple[str, list[dict], int]:
    history = list(messages)
    for round_ in range(1, max_rounds + 1):
        text, calls = await model(history, [t.spec() for t in tools])
        history.append({"role": "assistant", "content": text, "tool_calls": calls})
        if not calls:
            return text, history, round_
        for call in calls:  # one result per call, in the order of the calls
            result = await execute(call, tools, approve)
            history.append({"role": "tool", "tool_call_id": call.id,
                            "content": f"ERROR: {result.content}" if result.is_error else result.content})
    raise RuntimeError(f"no answer after {max_rounds} rounds of tool calls")
