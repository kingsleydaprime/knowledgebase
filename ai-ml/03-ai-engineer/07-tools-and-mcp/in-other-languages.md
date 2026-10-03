# Tools and MCP in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tools and MCP]], which builds the support assistant's three tools, the checks before each call, the round trip and an MCP server by hand in TypeScript. This page does the same in Python, Go, Java, Rust and C#, with each language's usual JSON Schema library, and builds each MCP server with that language's **official MCP SDK** where the SDK speaks the current protocol. Every server, in every language, is then checked by **the same official TypeScript client, pinned to protocol revision 2026-07-28**. That check caught a real omission in one of them.

## Before you start

You can already:

- Explain the tool round trip, the order of checks before a side effect, and why a tool's result is untrusted → [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|the main lesson]].
- Explain what changed in MCP's 2026-07-28 revision → the main lesson's §5.
- Read code in at least one language below.

After this lesson you will be able to:

1. Check tool arguments with your language's JSON Schema library, and judge whether its messages are good enough for a model to act on.
2. Build an MCP server with your language's official SDK, and say which protocol revisions that SDK speaks.
3. Check any MCP server, in any language, against the official client.

## The kid version

Six shops build the same vending machine from the same drawing. They each use their own screws and their own wiring, but every machine has to accept the same coins and give the same snacks. So before any machine leaves a shop, the same inspector visits with the same bag of test coins, including some fakes. One machine, it turns out, forgot to print its price list on the front, which the drawing said was required. The inspector found it in seconds.

**Where the analogy stops working.** Vending machines either take a coin or don't. Software can disagree in small ways that still work, such as printing `120` or `120.0` for the same price, and you have to decide which differences matter.

## 1. The tools, by ecosystem

| Language | Checking arguments | Schema from a type | Official MCP SDK (October 2026) | Speaks 2026-07-28? |
|---|---|---|---|---|
| TypeScript | Ajv or Zod (the main lesson writes a small one) | Zod schemas | `@modelcontextprotocol/client` and `/server` 2.3 (`@modelcontextprotocol/sdk` 1.x is the older line) | v2 yes; 1.x no |
| Python | **`jsonschema`** | Pydantic models and type hints | **`mcp` 2.2** (`MCPServer`) | yes |
| Go | **`google/jsonschema-go`** | inferred from structs | **`go-sdk` 1.8** | yes |
| Java | **networknt `json-schema-validator`** | victools `jsonschema-generator` | `io.modelcontextprotocol.sdk` 2.0.1 | **no**: 2025-11-25 |
| Rust | **`jsonschema`** | `schemars` | **`rmcp` 3.5** | yes |
| C# | **JsonSchema.Net** | `System.Text.Json`'s schema exporter | **`ModelContextProtocol` 2.2** | yes |
| C, C++ | — | — | — | — |

An SDK either "speaks 2026-07-28" or doesn't: the Python, Go, Rust and C# SDKs, and the TypeScript v2 packages, mention the revision throughout their code and docs, and the conformance check below confirms it for the servers built with them. The Java SDK's newest release only knows 2025-11-25, so the Java server here is written by hand, as the TypeScript one is in the main lesson. An SDK that lags the spec is normal for a few months after a revision. Check before you choose one, rather than assuming the latest SDK speaks the latest protocol.

There's no C or C++ section: AI applications and MCP servers are almost never written in C or C++, and no official SDK exists for either.

## 2. What comes out the same, and what doesn't

Every lab asserts these results on the shared `orders.json`:

| Check | Expected in every language |
|---|---|
| what the model sees | name, description and input schema, and nothing else |
| unknown tool | `unknown tool "delete_order"; available: get_order, get_refund, issue_refund` |
| broken JSON | `arguments are not valid JSON` |
| missing order | `get_order failed: no order Z999` |
| a side effect without approval | `the user declined this action`, and a malformed call is never shown to the person |
| refunding twice | `issue_refund failed: order B456 already has a refund` |
| the round trip for A123 | 2 rounds, 5 messages |
| the D012 injection | the note reaches the model; the refund is declined; approved, it's refused with `refund 500 is more than the order total 30` |
| a model that never stops | `no answer after 3 rounds of tool calls` |
| the MCP server, checked by the official client | three tools in a fixed order with annotations, the C789 refund, a tool error naming `order_id` for a bad ID, and an unknown tool refused |

And these differ, which is worth knowing because the model reads every byte:

- **The same number, written three ways.** `get_order B456` returns a total of `120` in TypeScript and Go, `120.0` in Python, Java and Rust, and `120.00` in C#, whose `JsonNode` keeps the number exactly as the file wrote it. All are the same value; a prompt cache or a recorded cassette would see them as different.
- **Key order.** Rust's `serde_json::Value` sorts keys, so its refund comes back as `{"amount":…,"requested":…,"status":…}` where the others keep the file's order.
- **Validation messages.** Python's `jsonschema`, networknt and Rust's `jsonschema` report every problem in plain words. Go's `jsonschema-go` stops at the first problem, and words it for developers. JsonSchema.Net reports summaries as well as the problems themselves, so the lab filters them out, and its pattern message doesn't say which pattern failed. A model can only fix what the message tells it, so read your library's messages as the model will.
- **An unknown tool.** The spec's tools page lists it among protocol errors. Python's `MCPServer` reports it as a tool error instead (`isError: true`); the others return a JSON-RPC error. The page describes the two kinds without making either a requirement, so both are refusals, and the conformance check accepts either and prints which.

## 3. One check for every server

The conformance check is a short script in the TypeScript lab. It starts a server as a subprocess, connects with the official client **pinned** to 2026-07-28, so it can't fall back to the old handshake, and checks the tool list, a successful call, a tool error and an unknown tool:

```ts
// conformance.ts — check any language's support-tools MCP server with the official client, pinned to 2026-07-28.
//   node conformance.ts <command> [args...]      e.g. node conformance.ts python3 server.py
// The client starts the server itself, over stdio. Exits non-zero on the first broken expectation.
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";

const [command, ...args] = process.argv.slice(2);
const client = new Client({ name: "conformance", version: "1.0.0" }, { versionNegotiation: { mode: { pin: "2026-07-28" } } });
await client.connect(new StdioClientTransport({ command, args, stderr: "pipe" }));

type Result = Awaited<ReturnType<typeof client.callTool>>;
// SDKs may send the value as structured content, as JSON text, or both. Compare values, not bytes.
const value = (r: Result) => r.structuredContent ?? JSON.parse(r.content.map((c) => (c.type === "text" ? c.text : "")).join(""));
const text = (r: Result) => r.content.map((c) => (c.type === "text" ? c.text : "")).join("");

try {
  const { tools } = await client.listTools();
  assert.deepEqual(tools.map((t) => t.name), ["get_order", "get_refund", "issue_refund"], "three tools, in a fixed order");
  assert.equal(tools[0].annotations?.readOnlyHint, true, "get_order is marked read-only");
  assert.equal(tools[2].annotations?.destructiveHint, true, "issue_refund is marked destructive");
  console.log("tools/list: get_order, get_refund, issue_refund, with annotations");

  const refund = await client.callTool({ name: "get_refund", arguments: { order_id: "C789" } });
  assert.notEqual(refund.isError, true);
  assert.deepEqual(value(refund), { status: "paid", amount: 15, paid: "2026-09-20" });
  console.log("tools/call get_refund C789: the refund");

  const bad = await client.callTool({ name: "get_order", arguments: { order_id: "nope" } });
  assert.equal(bad.isError, true, "a bad argument is a tool error the model can read");
  assert.match(text(bad), /order_id/, "and the message names the argument");
  console.log(`tools/call get_order "nope": tool error: ${text(bad).split("\n")[0].slice(0, 100)}`);

  const unknown = await client.callTool({ name: "drop_tables", arguments: {} }).then(
    (r) => `a tool error (isError ${r.isError})`,
    (e) => `a protocol error (${e.code})`,
  );
  // The spec's tools page lists an unknown tool among protocol errors, without a MUST; SDKs differ.
  // Either way it must be refused, so print which.
  console.log(`tools/call drop_tables: ${unknown}`);
  assert.match(unknown, /a protocol error \(-32602\)|a tool error \(isError true\)/, "an unknown tool is refused");
  console.log("conformance: pass");
} finally {
  await client.close();
}
```

Each language's lab runs it on its own server through this wrapper, which installs the client the first time:

```sh
#!/bin/sh
# Checks a language's MCP server with the official TypeScript client: sh ../shared/conformance.sh <command> [args...]
# Run from a language's lab folder. Installs the client into ../typescript on first use.
set -eu
here=$(cd "$(dirname "$0")/../typescript" && pwd)
[ -d "$here/node_modules" ] || (cd "$here" && npm ci --silent)
exec node "$here/conformance.ts" "$@"
```

That check is what caught the Rust server's missing cache hints. The 2026-07-28 revision **requires** `ttlMs` and `cacheScope` on every `tools/list` result, the official client rejects a list without them, and `rmcp` leaves them to the server. The fix was one line. Without the check, the server would have looked fine to anyone reading the code.

## Terms used in this lesson

1. **Official SDK**: This is a library maintained by the MCP project itself for one language, as opposed to a community one.
2. **Conformance check**: This is a test that runs an implementation against an independent one, here the official client, to show it follows the protocol rather than just the author's reading of it.
3. **Schema from a type**: This means generating a JSON Schema from a type in your language, such as a Pydantic model or a Go struct, instead of writing the schema by hand.
4. **Low-level handler**: This is an SDK hook that lets your code answer a protocol method such as `tools/list` directly, instead of registering each tool through the SDK's decorators or macros.

## 4. Python

Python's argument check is the `jsonschema` library; the lab only formats its errors with the argument's path. The MCP server uses the official SDK's `MCPServer`, and shows its main idea: **type hints are the schema**. `order_id: OrderId`, where `OrderId` is a `str` with a Pydantic `pattern`, becomes the `inputSchema`, and the SDK validates every call against it before your function runs. The functions themselves call the same tools the loop uses, so the store and its rules exist once.

```python
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
```

```python
"""The support tools as an MCP server, with the official Python SDK (mcp 2.x speaks 2026-07-28).
    python server.py              all three tools, over stdio
    python server.py --read-only  only the tools that change nothing
The type hints are the schema: the SDK turns them into inputSchema and validates every call against it."""
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from tools import load_orders, support_tools

OrderId = Annotated[str, Field(pattern=r"^[A-Z][0-9]{3}$", description="Like A123: one capital letter, three digits")]
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False)

tools = {t.name: t for t in support_tools(load_orders())}  # the same order store and rules as the tool loop
mcp = MCPServer("support-tools")


@mcp.tool(annotations=READ_ONLY)
def get_order(order_id: OrderId) -> dict:
    """Look up an order's status, total and tracking number. Use it before answering any question about an order."""
    return tools["get_order"].run({"order_id": order_id})


@mcp.tool(annotations=READ_ONLY)
def get_refund(order_id: OrderId) -> dict:
    """Look up the refund on an order, if there is one: its status, amount and dates."""
    return tools["get_refund"].run({"order_id": order_id})


if "--read-only" not in sys.argv:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    def issue_refund(order_id: OrderId, amount: Annotated[float, Field(ge=0.01)]) -> dict:
        """Refund money to the customer. Only when the customer asks for a refund and none exists yet."""
        return tools["issue_refund"].run({"order_id": order_id, "amount": amount})  # the tool's own rules still apply


if __name__ == "__main__":
    mcp.run()  # stdio by default; logs go to stderr
```

```python
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
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/07-tools-and-mcp/labs/python). `python3 labs/run.py tools-and-mcp/python` runs the tests, then the conformance check on `server.py`.

## 5. Go

Go's schema comes from the argument struct: `jsonschema.For[RefundArgs]()` makes fields without `omitempty` required and forbids other properties, and the lab adds what a Go type can't say, the order-ID pattern and the minimum amount, to the inferred schema. The same package, the one the official Go SDK uses, then validates calls. The server registers each tool with `mcp.AddTool`, whose handler receives the already-decoded, already-validated struct, and returns a value or an error; the SDK turns the value into the result and an error into a tool error. Go 1.26's `new(0.01)` builds the pointer the schema's `Minimum` field needs.

```go
// Package tools: tools for a support assistant, with the same checks, round trip and results as the
// TypeScript lab. Each tool's schema is inferred from a Go struct, with the jsonschema-go package the
// official MCP Go SDK uses, and the same package validates the arguments.
package tools

import (
	"cmp"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/google/jsonschema-go/jsonschema"
)

// IDArgs and RefundArgs are the argument types: their fields are the schema.
type IDArgs struct {
	OrderID string `json:"order_id" jsonschema:"Like A123: one capital letter, three digits"`
}
type RefundArgs struct {
	OrderID string  `json:"order_id" jsonschema:"Like A123: one capital letter, three digits"`
	Amount  float64 `json:"amount"`
}

// SchemaFor infers a schema from T, then adds the rules a Go type can't express.
func SchemaFor[T any]() *jsonschema.Schema {
	s, err := jsonschema.For[T](nil) // fields without omitempty are required; no other properties allowed
	if err != nil {
		panic(err)
	}
	s.Properties["order_id"].Pattern = "^[A-Z][0-9]{3}$"
	if amount, ok := s.Properties["amount"]; ok {
		amount.Minimum = new(0.01)
	}
	return s
}

type Tool struct {
	Name        string
	Description string
	Schema      *jsonschema.Schema
	SideEffects bool
	Run         func(ctx context.Context, args json.RawMessage) (any, error)
}

type Call struct{ ID, Name, Arguments string }
type Result struct {
	ID      string
	Content string
	IsError bool
}

// Approve is asked before any tool with side effects runs.
type Approve func(name string, args json.RawMessage) bool

func Execute(ctx context.Context, call Call, tools []Tool, approve Approve) Result {
	fail := func(format string, a ...any) Result { return Result{call.ID, fmt.Sprintf(format, a...), true} }
	var tool *Tool
	var names []string
	for i := range tools {
		names = append(names, tools[i].Name)
		if tools[i].Name == call.Name {
			tool = &tools[i]
		}
	}
	if tool == nil {
		return fail("unknown tool %q; available: %s", call.Name, strings.Join(names, ", "))
	}
	raw := json.RawMessage(cmp.Or(call.Arguments, "{}"))
	var value any
	if json.Unmarshal(raw, &value) != nil {
		return fail("arguments are not valid JSON")
	}
	resolved, err := tool.Schema.Resolve(nil)
	if err != nil {
		return fail("%s has an invalid schema: %v", tool.Name, err)
	}
	if err := resolved.Validate(value); err != nil {
		return fail("%s", strings.TrimPrefix(err.Error(), "validating root: ")) // the library's words, first problem only
	}
	if tool.SideEffects && !approve(tool.Name, raw) {
		return fail("the user declined this action")
	}
	out, err := tool.Run(ctx, raw)
	if err != nil {
		return fail("%s failed: %v", tool.Name, err)
	}
	content, _ := json.Marshal(out)
	if len(content) > 2000 {
		return Result{call.ID, string(content[:2000]) + " …[truncated]", false}
	}
	return Result{call.ID, string(content), false}
}

type Refund struct {
	Status    string  `json:"status"`
	Amount    float64 `json:"amount,omitempty"`
	Requested string  `json:"requested,omitempty"`
	Paid      string  `json:"paid,omitempty"`
}

type Order struct {
	Status   string  `json:"status"`
	Total    float64 `json:"total"`
	Tracking string  `json:"tracking,omitempty"`
	Refund   *Refund `json:"refund"`
	Note     string  `json:"note,omitempty"`
}

func LoadOrders(path string) (map[string]*Order, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var orders map[string]*Order
	return orders, json.Unmarshal(data, &orders)
}

func SupportTools(orders map[string]*Order) []Tool {
	find := func(id string) (*Order, error) {
		if o, ok := orders[id]; ok {
			return o, nil
		}
		return nil, fmt.Errorf("no order %s", id)
	}
	byID := func(f func(*Order) any) func(context.Context, json.RawMessage) (any, error) {
		return func(_ context.Context, raw json.RawMessage) (any, error) {
			var a IDArgs
			if err := json.Unmarshal(raw, &a); err != nil {
				return nil, err
			}
			o, err := find(a.OrderID)
			if err != nil {
				return nil, err
			}
			return f(o), nil
		}
	}
	return []Tool{
		{"get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
			SchemaFor[IDArgs](), false, byID(func(o *Order) any {
				return struct { // everything but the refund, which has its own tool
					Status   string  `json:"status"`
					Total    float64 `json:"total"`
					Tracking string  `json:"tracking,omitempty"`
					Note     string  `json:"note,omitempty"`
				}{o.Status, o.Total, o.Tracking, o.Note}
			})},
		{"get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
			SchemaFor[IDArgs](), false, byID(func(o *Order) any {
				if o.Refund == nil {
					return Refund{Status: "none"}
				}
				return o.Refund
			})},
		{"issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
			SchemaFor[RefundArgs](), true, func(_ context.Context, raw json.RawMessage) (any, error) {
				var a RefundArgs
				if err := json.Unmarshal(raw, &a); err != nil {
					return nil, err
				}
				o, err := find(a.OrderID)
				switch {
				case err != nil:
					return nil, err
				case o.Refund != nil:
					return nil, fmt.Errorf("order %s already has a refund", a.OrderID)
				case a.Amount > o.Total:
					return nil, fmt.Errorf("refund %g is more than the order total %g", a.Amount, o.Total)
				}
				o.Refund = &Refund{Status: "processing", Amount: a.Amount, Requested: "today"}
				return o.Refund, nil
			}},
	}
}

type Message struct {
	Role, Content, ToolCallID string
	Calls                     []Call
}

// Model returns one turn: text, and zero or more calls. No calls means "this is my answer".
type Model func(ctx context.Context, history []Message, tools []Tool) (string, []Call, error)

func AnswerWithTools(ctx context.Context, model Model, history []Message, tools []Tool, approve Approve, maxRounds int) (string, []Message, error) {
	for round := 1; round <= maxRounds; round++ {
		text, calls, err := model(ctx, history, tools)
		if err != nil {
			return "", history, err
		}
		history = append(history, Message{Role: "assistant", Content: text, Calls: calls})
		if len(calls) == 0 {
			return text, history, nil
		}
		for _, c := range calls { // one result per call, in the order of the calls
			r := Execute(ctx, c, tools, approve)
			content := r.Content
			if r.IsError {
				content = "ERROR: " + content
			}
			history = append(history, Message{Role: "tool", ToolCallID: c.ID, Content: content})
		}
	}
	return "", history, fmt.Errorf("no answer after %d rounds of tool calls", maxRounds)
}
```

```go
// The support tools as an MCP server, with the official Go SDK (go-sdk v1.8 speaks 2026-07-28).
//
//	go run ./cmd/server              all three tools, over stdio
//	go run ./cmd/server --read-only  only the tools that change nothing
package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"slices"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"tools"
)

// add registers one tool. In is the argument type: the SDK decodes and validates the call into it
// before the handler runs, so the handler only re-encodes it for the tool's own Run.
func add[In any](server *mcp.Server, t tools.Tool) {
	annotations := &mcp.ToolAnnotations{ReadOnlyHint: !t.SideEffects, DestructiveHint: new(t.SideEffects)}
	mcp.AddTool(server, &mcp.Tool{Name: t.Name, Description: t.Description, InputSchema: t.Schema, Annotations: annotations},
		func(ctx context.Context, _ *mcp.CallToolRequest, in In) (*mcp.CallToolResult, any, error) {
			raw, err := json.Marshal(in)
			if err != nil {
				return nil, nil, err
			}
			out, err := t.Run(ctx, raw) // an error here becomes a tool error the model can read
			return nil, out, err
		})
}

func main() {
	orders, err := tools.LoadOrders("../shared/orders.json")
	if err != nil {
		log.Fatal(err) // log writes to stderr, so it never corrupts the protocol on stdout
	}
	byName := map[string]tools.Tool{}
	for _, t := range tools.SupportTools(orders) {
		byName[t.Name] = t
	}
	server := mcp.NewServer(&mcp.Implementation{Name: "support-tools", Version: "1.0.0"}, nil)
	add[tools.IDArgs](server, byName["get_order"])
	add[tools.IDArgs](server, byName["get_refund"])
	if !slices.Contains(os.Args[1:], "--read-only") {
		add[tools.RefundArgs](server, byName["issue_refund"])
	}
	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}
```

```go
package tools

import (
	"context"
	"encoding/json"
	"slices"
	"strings"
	"testing"
)

const ordersPath = "../shared/orders.json"

func load(t *testing.T) map[string]*Order {
	orders, err := LoadOrders(ordersPath)
	if err != nil {
		t.Fatal(err)
	}
	return orders
}

func call(name, args, id string) Call { return Call{ID: id, Name: name, Arguments: args} }
func no(string, json.RawMessage) bool { return false }

// scripted plays back a list of turns and records what the model was sent.
func scripted(turns [][]Call, texts []string, seen *[][]Message) Model {
	return func(_ context.Context, history []Message, _ []Tool) (string, []Call, error) {
		*seen = append(*seen, slices.Clone(history))
		i := len(*seen) - 1
		return texts[i], turns[i], nil
	}
}

func TestTheSchemaComesFromTheType(t *testing.T) {
	b, _ := json.Marshal(SchemaFor[RefundArgs]())
	want := `{"type":"object","properties":{"order_id":{"type":"string","description":"Like A123: one capital letter, three digits","pattern":"^[A-Z][0-9]{3}$"},"amount":{"type":"number","minimum":0.01}},"required":["order_id","amount"],"additionalProperties":false}`
	if string(b) != want {
		t.Error(string(b))
	}
}

func TestEveryFailureBecomesAResult(t *testing.T) {
	tools, ctx := SupportTools(load(t)), t.Context()
	if r := Execute(ctx, call("get_order", `{"order_id":"B456"}`, "c1"), tools, no); r.Content != `{"status":"shipped","total":120,"tracking":"LG-88213"}` || r.IsError {
		t.Error(r)
	}
	for args, want := range map[[2]string]string{
		{"delete_order", `{}`}:                               `unknown tool "delete_order"; available: get_order, get_refund, issue_refund`,
		{"get_order", `{order_id: A123`}:                     "arguments are not valid JSON",
		{"get_order", `{"order_id":"Z999"}`}:                 "get_order failed: no order Z999",
		{"issue_refund", `{"order_id":"B456","amount":120}`}: "the user declined this action",
		{"get_order", `{"order_id":"a-1"}`}:                  `validating /properties/order_id: pattern: "a-1" does not match regular expression "^[A-Z][0-9]{3}$"`,
	} {
		if r := Execute(ctx, call(args[0], args[1], "c1"), tools, no); r.Content != want || !r.IsError {
			t.Errorf("%v: got %q", args, r.Content)
		}
	}
}

func TestASideEffectNeedsValidArgumentsThenApprovalThenItsOwnRules(t *testing.T) {
	orders := load(t)
	tools, ctx := SupportTools(orders), t.Context()
	var asked []string
	yes := func(name string, args json.RawMessage) bool {
		asked = append(asked, name+" "+string(args))
		return true
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":-5}`, "c1"), tools, yes); !r.IsError || len(asked) != 0 {
		t.Fatal("a malformed call must never reach the person", r)
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":120}`, "c1"), tools, yes); r.IsError || orders["B456"].Refund.Status != "processing" {
		t.Fatal(r)
	}
	if !slices.Equal(asked, []string{`issue_refund {"order_id":"B456","amount":120}`}) {
		t.Error(asked)
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":120}`, "c1"), tools, yes); r.Content != "issue_refund failed: order B456 already has a refund" {
		t.Error(r.Content)
	}
}

func TestTheRoundTrip(t *testing.T) {
	var seen [][]Message
	model := scripted([][]Call{{call("get_order", `{"order_id":"A123"}`, "c1"), call("get_refund", `{"order_id":"A123"}`, "c2")}, nil},
		[]string{"", "Your refund of 49.99 is being processed."}, &seen)
	answer, history, err := AnswerWithTools(t.Context(), model, []Message{{Role: "user", Content: "Where is my refund for A123?"}}, SupportTools(load(t)), no, 5)
	if err != nil || len(history) != 5 || !strings.Contains(answer, "49.99") {
		t.Fatal(err, len(history), answer)
	}
	if seen[1][2].Content != `{"status":"delivered","total":49.99}` || seen[1][3].Content != `{"status":"processing","amount":49.99,"requested":"2026-09-28"}` {
		t.Error(seen[1][2:])
	}
}

func TestTextInAToolResultCannotApproveAnything(t *testing.T) {
	orders := load(t)
	var seen [][]Message
	model := scripted([][]Call{{call("get_order", `{"order_id":"D012"}`, "c1")}, {call("issue_refund", `{"order_id":"D012","amount":500}`, "c2")}, nil},
		[]string{"", "", "I can't issue that refund."}, &seen)
	AnswerWithTools(t.Context(), model, []Message{{Role: "user", Content: "Check D012"}}, SupportTools(orders), no, 5)
	if !strings.Contains(seen[1][2].Content, "IGNORE ALL PREVIOUS INSTRUCTIONS") || seen[2][4].Content != "ERROR: the user declined this action" || orders["D012"].Refund != nil {
		t.Fatal(seen)
	}
	approved := Execute(t.Context(), call("issue_refund", `{"order_id":"D012","amount":500}`, "c3"), SupportTools(orders), func(string, json.RawMessage) bool { return true })
	if approved.Content != "issue_refund failed: refund 500 is more than the order total 30" {
		t.Error(approved.Content)
	}
}

func TestAModelThatNeverStopsIsCutOff(t *testing.T) {
	forever := func(context.Context, []Message, []Tool) (string, []Call, error) {
		return "", []Call{call("get_order", `{"order_id":"A123"}`, "c1")}, nil
	}
	_, _, err := AnswerWithTools(t.Context(), forever, []Message{{Role: "user", Content: "?"}}, SupportTools(load(t)), no, 3)
	if err == nil || err.Error() != "no answer after 3 rounds of tool calls" {
		t.Error(err)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/07-tools-and-mcp/labs/go). `python3 labs/run.py tools-and-mcp/go` vets, tests, then runs the conformance check on `go run ./cmd/server`.

## 6. Java

Java's newest official SDK speaks only 2025-11-25, so the server is written by hand against 2026-07-28, line for line like the main lesson's TypeScript one: a loop over stdin, one JSON-RPC message per line, `_meta` checked on every request. JSON is **Jackson 3**, whose packages moved from `com.fasterxml.jackson` to `tools.jackson` (the lab's own package is called `support`, to stay clear of them). Arguments are checked with networknt's validator, which reports every problem; its messages are clear, but start with a path such as `/order_id`, so the model sees where.

```java
package support;

import com.networknt.schema.Error;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BiPredicate;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

/** Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
 *  JSON is Jackson 3; arguments are checked with networknt's json-schema-validator. */
public final class Tools {
    private Tools() {}

    public static final JsonMapper JSON = JsonMapper.shared();
    private static final SchemaRegistry SCHEMAS = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_2020_12);

    /** What can go wrong inside a tool, said in words the model can act on. */
    public static final class ToolFailure extends RuntimeException {
        public ToolFailure(String message) { super(message); }
    }

    public interface Run {
        Object apply(JsonNode args);
    }

    public record Tool(String name, String description, JsonNode inputSchema, boolean sideEffects, Run run) {
        public ObjectNode spec() { // what the model sees: never run or sideEffects
            return JSON.createObjectNode().put("name", name).put("description", description).set("inputSchema", inputSchema);
        }
    }

    public record ToolCall(String id, String name, String arguments) {}

    public record ToolResult(String id, String content, boolean isError) {}

    public static List<String> validate(JsonNode schema, JsonNode value) {
        return SCHEMAS.getSchema(schema.toString()).validate(value).stream().map(Error::toString).toList();
    }

    public static ToolResult execute(ToolCall call, List<Tool> tools, BiPredicate<String, JsonNode> approve) {
        Tool tool = tools.stream().filter(t -> t.name().equals(call.name())).findFirst().orElse(null);
        if (tool == null) {
            var names = String.join(", ", tools.stream().map(Tool::name).toList());
            return fail(call, "unknown tool \"" + call.name() + "\"; available: " + names);
        }
        JsonNode args;
        try {
            args = JSON.readTree(call.arguments() == null || call.arguments().isEmpty() ? "{}" : call.arguments());
        } catch (JacksonException e) {
            return fail(call, "arguments are not valid JSON");
        }
        var problems = validate(tool.inputSchema(), args);
        if (!problems.isEmpty()) return fail(call, String.join("; ", problems));
        if (tool.sideEffects() && !approve.test(tool.name(), args)) return fail(call, "the user declined this action");
        try {
            String content = JSON.writeValueAsString(tool.run().apply(args));
            return new ToolResult(call.id(), content.length() > 2000 ? content.substring(0, 2000) + " …[truncated]" : content, false);
        } catch (ToolFailure e) { // the message, never a stack trace
            return fail(call, tool.name() + " failed: " + e.getMessage());
        }
    }

    private static ToolResult fail(ToolCall call, String content) {
        return new ToolResult(call.id(), content, true);
    }

    public static ObjectNode loadOrders(Path path) throws Exception {
        return (ObjectNode) JSON.readTree(Files.readString(path));
    }

    private static final String ORDER_ID = """
            {"type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits"}""";

    public static List<Tool> supportTools(ObjectNode orders) {
        JsonNode oneId = JSON.readTree("""
                {"type": "object", "properties": {"order_id": %s}, "required": ["order_id"], "additionalProperties": false}"""
                .formatted(ORDER_ID));
        JsonNode refundArgs = JSON.readTree("""
                {"type": "object", "properties": {"order_id": %s, "amount": {"type": "number", "minimum": 0.01}},
                 "required": ["order_id", "amount"], "additionalProperties": false}""".formatted(ORDER_ID));
        java.util.function.Function<JsonNode, ObjectNode> find = args -> {
            JsonNode order = orders.get(args.get("order_id").asString());
            if (order == null) throw new ToolFailure("no order " + args.get("order_id").asString());
            return (ObjectNode) order;
        };
        return List.of(
                new Tool("get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
                        oneId, false, args -> find.apply(args).deepCopy().without("refund")),
                new Tool("get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
                        oneId, false, args -> {
                            JsonNode refund = find.apply(args).get("refund");
                            return refund.isNull() ? JSON.createObjectNode().put("status", "none") : refund;
                        }),
                new Tool("issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
                        refundArgs, true, args -> {
                            ObjectNode order = find.apply(args);
                            double amount = args.get("amount").asDouble(), total = order.get("total").asDouble();
                            if (!order.get("refund").isNull()) throw new ToolFailure("order " + args.get("order_id").asString() + " already has a refund");
                            if (amount > total) throw new ToolFailure("refund %s is more than the order total %s".formatted(plain(amount), plain(total)));
                            order.set("refund", JSON.createObjectNode().put("status", "processing").put("amount", amount).put("requested", "today"));
                            return order.get("refund");
                        }));
    }

    /** 500.0 as "500", 49.99 as "49.99": what the other languages print. */
    static String plain(double x) {
        return new java.math.BigDecimal(Double.toString(x)).stripTrailingZeros().toPlainString();
    }

    public record Message(String role, String content, String toolCallId, List<ToolCall> toolCalls) {}

    /** One model turn: text, and zero or more calls. No calls means "this is my answer". */
    public record Turn(String content, List<ToolCall> toolCalls) {}

    public interface Model {
        Turn respond(List<Message> history, List<ObjectNode> tools);
    }

    public record Answer(String text, List<Message> history, int rounds) {}

    public static Answer answerWithTools(Model model, List<Message> messages, List<Tool> tools, BiPredicate<String, JsonNode> approve, int maxRounds) {
        var history = new ArrayList<>(messages);
        var specs = tools.stream().map(Tool::spec).toList();
        for (int round = 1; round <= maxRounds; round++) {
            Turn turn = model.respond(List.copyOf(history), specs);
            history.add(new Message("assistant", turn.content(), null, turn.toolCalls()));
            if (turn.toolCalls().isEmpty()) return new Answer(turn.content(), history, round);
            for (ToolCall call : turn.toolCalls()) { // one result per call, in the order of the calls
                ToolResult r = execute(call, tools, approve);
                history.add(new Message("tool", r.isError() ? "ERROR: " + r.content() : r.content(), call.id(), List.of()));
            }
        }
        throw new IllegalStateException("no answer after " + maxRounds + " rounds of tool calls");
    }
}
```

```java
package support;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import support.Tools.Tool;
import support.Tools.ToolCall;
import support.Tools.ToolResult;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.node.ObjectNode;

/** The support tools as an MCP server over stdio, protocol revision 2026-07-28, by hand.
 *  The official Java SDK (mcp 2.0.1) speaks 2025-11-25, so this one is written the way the
 *  TypeScript lab's is: one JSON-RPC message per line on stdin and stdout.
 *    java support.McpServer              all three tools
 *    java support.McpServer --read-only  only the tools that change nothing */
public final class McpServer {
    static final String VERSION = "2026-07-28", KEY = "io.modelcontextprotocol/";

    static ObjectNode handle(JsonNode message, List<Tool> tools) {
        if (!message.has("id")) return null; // a notification: nothing to reply to
        JsonNode id = message.get("id"), params = message.path("params"), meta = params.path("_meta");
        // No handshake: every request says which protocol version it speaks and what the client can do.
        if (!meta.has(KEY + "protocolVersion") || !meta.has(KEY + "clientCapabilities")) {
            return error(id, -32602, "every request must carry protocolVersion and clientCapabilities in _meta", null);
        }
        String version = meta.get(KEY + "protocolVersion").asString();
        if (!version.equals(VERSION)) {
            var data = Tools.JSON.createObjectNode().put("requested", version);
            data.putArray("supported").add(VERSION);
            return error(id, -32022, "unsupported protocol version " + version, data);
        }
        return switch (message.path("method").asString()) {
            case "server/discover" -> {
                var r = Tools.JSON.createObjectNode();
                r.putArray("supportedVersions").add(VERSION);
                r.putObject("capabilities").putObject("tools");
                r.put("instructions", "Order and refund tools for a support assistant. Look an order up before answering about it.");
                yield result(id, r.put("ttlMs", 3_600_000).put("cacheScope", "public"));
            }
            case "tools/list" -> {
                var r = Tools.JSON.createObjectNode();
                var list = r.putArray("tools"); // always the same order, for the client's cache and the model's
                for (Tool t : tools) {
                    var spec = t.spec();
                    spec.putObject("annotations").put("readOnlyHint", !t.sideEffects()).put("destructiveHint", t.sideEffects());
                    list.add(spec);
                }
                yield result(id, r.put("ttlMs", 300_000).put("cacheScope", "public"));
            }
            case "tools/call" -> {
                String name = params.path("name").asString();
                if (tools.stream().noneMatch(t -> t.name().equals(name))) yield error(id, -32602, "Unknown tool: " + name, null);
                // Approval is the host's job: it asks the person before calling a destructive tool.
                ToolResult outcome = Tools.execute(new ToolCall(id.toString(), name, params.path("arguments").toString()), tools, (n, a) -> true);
                var r = Tools.JSON.createObjectNode();
                r.putArray("content").addObject().put("type", "text").put("text", outcome.content());
                yield result(id, r.put("isError", outcome.isError()));
            }
            default -> error(id, -32601, "Method not found: " + message.path("method").asString(), null);
        };
    }

    static ObjectNode result(JsonNode id, ObjectNode body) {
        var full = Tools.JSON.createObjectNode().put("resultType", "complete");
        full.setAll(body);
        full.putObject("_meta").putObject(KEY + "serverInfo").put("name", "support-tools").put("version", "1.0.0");
        var reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0").set("id", id);
        return reply.set("result", full);
    }

    static ObjectNode error(JsonNode id, int code, String text, ObjectNode data) {
        var err = Tools.JSON.createObjectNode().put("code", code).put("message", text);
        if (data != null) err.set("data", data);
        var reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0").set("id", id);
        return reply.set("error", err);
    }

    public static void main(String[] args) throws Exception {
        var all = Tools.supportTools(Tools.loadOrders(Path.of("..", "shared", "orders.json")));
        var tools = Arrays.asList(args).contains("--read-only") ? all.stream().filter(t -> !t.sideEffects()).toList() : all;
        System.err.println("support-tools MCP server: " + String.join(", ", tools.stream().map(Tool::name).toList())); // logs: stderr only
        var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        for (String line; (line = in.readLine()) != null; ) { // null: stdin closed, so exit
            if (line.isBlank()) continue;
            ObjectNode reply;
            try {
                reply = handle(Tools.JSON.readTree(line), tools);
            } catch (tools.jackson.core.JacksonException e) {
                reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0");
                reply.putObject("error").put("code", -32700).put("message", "Parse error");
            }
            if (reply != null) {
                System.out.println(Tools.JSON.writeValueAsString(reply));
                System.out.flush();
            }
        }
    }
}
```

```java
package support;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import support.Tools.Message;
import support.Tools.ToolCall;
import support.Tools.Turn;
import tools.jackson.databind.JsonNode;

/** Checks, run with `java -ea`. The same results as every other language. */
public final class ToolsCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static final Path ORDERS = Path.of("..", "shared", "orders.json");

    static ToolCall call(String name, String args, String id) {
        return new ToolCall(id, name, args);
    }

    /** A pretend model that plays back a script of turns and records what it was sent. */
    static Tools.Model scripted(List<Turn> turns, List<List<Message>> seen) {
        var script = new ArrayList<>(turns);
        return (history, tools) -> {
            seen.add(history);
            return script.removeFirst();
        };
    }

    public static void main(String[] args) throws Exception {
        var tools = Tools.supportTools(Tools.loadOrders(ORDERS));
        check(tools.stream().map(t -> t.spec().propertyNames().stream().toList()).toList().getFirst()
                .equals(List.of("name", "description", "inputSchema")), "the model sees specs, never functions");

        var problems = Tools.validate(tools.get(2).inputSchema(), Tools.JSON.readTree("{\"order_id\":\"a-1\",\"amount\":0,\"note\":\"hi\"}"));
        check(problems.size() == 3, problems); // networknt's own wording, every problem found
        System.out.println("validation: " + String.join(" | ", problems));

        var ok = Tools.execute(call("get_order", "{\"order_id\":\"B456\"}", "c1"), tools, (n, a) -> false);
        check(ok.content().equals("{\"status\":\"shipped\",\"total\":120.0,\"tracking\":\"LG-88213\"}"), ok); // 120.0, like Python
        java.util.function.Function<ToolCall, String> content = c -> Tools.execute(c, tools, (n, a) -> false).content();
        check(content.apply(call("delete_order", "{}", "c1")).equals("unknown tool \"delete_order\"; available: get_order, get_refund, issue_refund"), "unknown");
        check(content.apply(call("get_order", "{order_id: A123", "c1")).equals("arguments are not valid JSON"), "bad JSON");
        check(content.apply(call("get_order", "{\"order_id\":\"Z999\"}", "c1")).equals("get_order failed: no order Z999"), "no order");
        check(content.apply(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1")).equals("the user declined this action"), "declined");

        // a side effect: valid arguments, then approval, then the tool's own rules
        var orders = Tools.loadOrders(ORDERS);
        var fresh = Tools.supportTools(orders);
        var asked = new ArrayList<String>();
        java.util.function.BiPredicate<String, JsonNode> yes = (n, a) -> asked.add(n + " " + a);
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":-5}", "c1"), fresh, yes).isError() && asked.isEmpty(), "malformed");
        check(!Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1"), fresh, yes).isError(), "approved");
        check(asked.equals(List.of("issue_refund {\"order_id\":\"B456\",\"amount\":120}")), asked);
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1"), fresh, yes).content()
                .equals("issue_refund failed: order B456 already has a refund"), "twice");

        // the round trip
        var seen = new ArrayList<List<Message>>();
        var model = scripted(List.of(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1"), call("get_refund", "{\"order_id\":\"A123\"}", "c2"))),
                new Turn("Your refund of 49.99 is being processed.", List.of())), seen);
        var answer = Tools.answerWithTools(model, List.of(new Message("user", "Where is my refund for A123?", null, List.of())), tools, (n, a) -> false, 5);
        check(answer.rounds() == 2 && answer.history().size() == 5, answer);
        check(seen.get(1).get(2).content().equals("{\"status\":\"delivered\",\"total\":49.99}"), seen.get(1).get(2));
        check(seen.get(1).get(3).content().equals("{\"status\":\"processing\",\"amount\":49.99,\"requested\":\"2026-09-28\"}"), seen.get(1).get(3));

        // text in a tool result can't approve anything
        var injected = Tools.loadOrders(ORDERS);
        var seen2 = new ArrayList<List<Message>>();
        var fooled = scripted(List.of(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"D012\"}", "c1"))),
                new Turn("", List.of(call("issue_refund", "{\"order_id\":\"D012\",\"amount\":500}", "c2"))),
                new Turn("I can't issue that refund.", List.of())), seen2);
        Tools.answerWithTools(fooled, List.of(new Message("user", "Check D012", null, List.of())), Tools.supportTools(injected), (n, a) -> false, 5);
        check(seen2.get(1).getLast().content().contains("IGNORE ALL PREVIOUS INSTRUCTIONS"), "the injection reached the model");
        check(seen2.get(2).getLast().content().equals("ERROR: the user declined this action") && injected.get("D012").get("refund").isNull(), "declined");
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"D012\",\"amount\":500}", "c3"), Tools.supportTools(injected), (n, a) -> true).content()
                .equals("issue_refund failed: refund 500 is more than the order total 30"), "the tool's own rule");

        // a model that never stops is cut off
        Tools.Model forever = (h, t) -> new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1")));
        try {
            Tools.answerWithTools(forever, List.of(new Message("user", "?", null, List.of())), tools, (n, a) -> false, 3);
            check(false, "should have stopped");
        } catch (IllegalStateException e) {
            check(e.getMessage().equals("no answer after 3 rounds of tool calls"), e.getMessage());
        }
        System.out.println("all tools checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/07-tools-and-mcp/labs/java). `check.sh` downloads nine jars on the first run, compiles with plain `javac`, runs the checks, then the conformance check. `python3 labs/run.py tools-and-mcp/java`.

## 7. Rust

Rust shares the order store between tools as `Arc<Mutex<Value>>`, because the MCP server calls tools from async tasks on several threads. Each tool's closure holds its own handle and takes the lock only for the length of one call. The server uses the official `rmcp` SDK through its low-level `ServerHandler` trait: `list_tools` and `call_tool` hand over to the same registry and checks the loop uses, so `rmcp` deals only with the protocol and the transport. (`rmcp`'s `#[tool]` macros generate a schema from a type with `schemars`, which suits tools whose rules a type can express.) Note the line that adds `with_ttl_ms` and `with_cache_scope`: that's the fix for the omission the conformance check caught.

```rust
//! Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
//! Arguments are checked with the `jsonschema` crate; the order store is shared behind a mutex
//! because the MCP server calls tools from async tasks.
use serde_json::{Value, json};
use std::sync::{Arc, Mutex};

pub type Run = Box<dyn Fn(&Value) -> Result<Value, String> + Send + Sync>;

pub struct Tool {
    pub name: &'static str,
    pub description: &'static str,
    pub schema: Value,
    pub side_effects: bool,
    pub run: Run,
}

impl Tool {
    /// What the model sees: never `run` or `side_effects`.
    pub fn spec(&self) -> Value {
        json!({ "name": self.name, "description": self.description, "inputSchema": self.schema })
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct ToolCall {
    pub id: String,
    pub name: String,
    pub arguments: String, // a JSON string, as models send it
}

#[derive(Debug, Clone, PartialEq)]
pub struct ToolResult {
    pub id: String,
    pub content: String,
    pub is_error: bool,
}

/// Every problem, as "arguments/field: message".
pub fn validate(schema: &Value, value: &Value) -> Vec<String> {
    let validator = jsonschema::validator_for(schema).expect("a tool's schema is itself valid");
    validator
        .iter_errors(value)
        .map(|e| format!("arguments{}: {e}", e.instance_path()))
        .collect()
}

pub fn execute(
    call: &ToolCall,
    tools: &[Tool],
    approve: &dyn Fn(&str, &Value) -> bool,
) -> ToolResult {
    let fail = |content: String| ToolResult {
        id: call.id.clone(),
        content,
        is_error: true,
    };
    let Some(tool) = tools.iter().find(|t| t.name == call.name) else {
        let names: Vec<_> = tools.iter().map(|t| t.name).collect();
        return fail(format!(
            "unknown tool \"{}\"; available: {}",
            call.name,
            names.join(", ")
        ));
    };
    let Ok(args) = serde_json::from_str::<Value>(if call.arguments.is_empty() {
        "{}"
    } else {
        &call.arguments
    }) else {
        return fail("arguments are not valid JSON".into());
    };
    let problems = validate(&tool.schema, &args);
    if !problems.is_empty() {
        return fail(problems.join("; "));
    }
    if tool.side_effects && !approve(tool.name, &args) {
        return fail("the user declined this action".into());
    }
    match (tool.run)(&args) {
        Ok(value) => {
            let content = value.to_string();
            let content = if content.len() > 2000 {
                format!("{} …[truncated]", &content[..2000])
            } else {
                content
            };
            ToolResult {
                id: call.id.clone(),
                content,
                is_error: false,
            }
        }
        Err(message) => fail(format!("{} failed: {message}", tool.name)), // the message, never a panic
    }
}

pub type Orders = Arc<Mutex<Value>>;

pub fn load_orders(path: &str) -> Orders {
    let text = std::fs::read_to_string(path).expect("the orders are beside the labs");
    Arc::new(Mutex::new(serde_json::from_str(&text).expect("valid JSON")))
}

pub fn support_tools(orders: &Orders) -> Vec<Tool> {
    let order_id = json!({ "type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits" });
    let one_id = json!({ "type": "object", "properties": { "order_id": order_id }, "required": ["order_id"], "additionalProperties": false });
    let refund_args = json!({ "type": "object", "properties": { "order_id": order_id, "amount": { "type": "number", "minimum": 0.01 } },
        "required": ["order_id", "amount"], "additionalProperties": false });
    // Each tool gets its own handle on the shared store; the lock is held only inside one call.
    let with_order = |orders: Orders, f: fn(&mut Value, &Value) -> Result<Value, String>| -> Run {
        Box::new(move |args| {
            let id = args["order_id"].as_str().unwrap_or_default();
            let mut all = orders.lock().unwrap();
            let order = all.get_mut(id).ok_or(format!("no order {id}"))?;
            f(order, args)
        })
    };
    vec![
        Tool {
            name: "get_order",
            description: "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
            schema: one_id.clone(),
            side_effects: false,
            run: with_order(orders.clone(), |order, _| {
                let mut copy = order.clone();
                copy.as_object_mut().unwrap().remove("refund"); // the refund has its own tool
                Ok(copy)
            }),
        },
        Tool {
            name: "get_refund",
            description: "Look up the refund on an order, if there is one: its status, amount and dates.",
            schema: one_id,
            side_effects: false,
            run: with_order(orders.clone(), |order, _| {
                Ok(if order["refund"].is_null() {
                    json!({ "status": "none" })
                } else {
                    order["refund"].clone()
                })
            }),
        },
        Tool {
            name: "issue_refund",
            description: "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
            schema: refund_args,
            side_effects: true,
            run: with_order(orders.clone(), |order, args| {
                let (amount, total) = (
                    args["amount"].as_f64().unwrap(),
                    order["total"].as_f64().unwrap(),
                );
                if !order["refund"].is_null() {
                    return Err(format!(
                        "order {} already has a refund",
                        args["order_id"].as_str().unwrap()
                    ));
                }
                if amount > total {
                    return Err(format!(
                        "refund {amount} is more than the order total {total}"
                    ));
                }
                order["refund"] =
                    json!({ "status": "processing", "amount": amount, "requested": "today" });
                Ok(order["refund"].clone())
            }),
        },
    ]
}

#[derive(Debug, Clone, PartialEq)]
pub enum Message {
    User(String),
    Assistant {
        content: String,
        calls: Vec<ToolCall>,
    },
    Tool {
        call_id: String,
        content: String,
    },
}

/// One model turn: text, and zero or more calls. No calls means "this is my answer".
pub type Turn = (String, Vec<ToolCall>);

pub fn answer_with_tools(
    model: &mut dyn FnMut(&[Message], &[Value]) -> Turn,
    messages: Vec<Message>,
    tools: &[Tool],
    approve: &dyn Fn(&str, &Value) -> bool,
    max_rounds: usize,
) -> Result<(String, Vec<Message>, usize), String> {
    let mut history = messages;
    let specs: Vec<Value> = tools.iter().map(Tool::spec).collect();
    for round in 1..=max_rounds {
        let (content, calls) = model(&history, &specs);
        history.push(Message::Assistant {
            content: content.clone(),
            calls: calls.clone(),
        });
        if calls.is_empty() {
            return Ok((content, history, round));
        }
        for call in &calls {
            // one result per call, in the order of the calls
            let r = execute(call, tools, approve);
            let content = if r.is_error {
                format!("ERROR: {}", r.content)
            } else {
                r.content
            };
            history.push(Message::Tool {
                call_id: call.id.clone(),
                content,
            });
        }
    }
    Err(format!("no answer after {max_rounds} rounds of tool calls"))
}

#[cfg(test)]
mod tests {
    use super::*;

    const ORDERS: &str = "../shared/orders.json";

    fn call(name: &str, args: &str, id: &str) -> ToolCall {
        ToolCall {
            id: id.into(),
            name: name.into(),
            arguments: args.into(),
        }
    }
    fn no(_: &str, _: &Value) -> bool {
        false
    }

    /// A pretend model that plays back a script of turns and records what it was sent.
    fn scripted(
        turns: Vec<Turn>,
        seen: &mut Vec<Vec<Message>>,
    ) -> impl FnMut(&[Message], &[Value]) -> Turn + '_ {
        let mut turns = turns.into_iter();
        move |history, _| {
            seen.push(history.to_vec());
            turns.next().expect("the script ran out")
        }
    }

    #[test]
    fn validation_names_every_problem() {
        let tools = support_tools(&load_orders(ORDERS));
        assert_eq!(
            validate(
                &tools[2].schema,
                &json!({ "order_id": "a-1", "amount": 0, "note": "hi" })
            ),
            [
                "arguments/amount: 0 is less than the minimum of 0.01",
                "arguments/order_id: \"a-1\" does not match \"^[A-Z][0-9]{3}$\"",
                "arguments: Additional properties are not allowed ('note' was unexpected)",
            ]
        );
    }

    #[test]
    fn every_failure_becomes_a_result() {
        let tools = support_tools(&load_orders(ORDERS));
        let ok = execute(
            &call("get_order", r#"{"order_id":"B456"}"#, "c1"),
            &tools,
            &no,
        );
        assert_eq!(
            ok.content,
            r#"{"status":"shipped","total":120.0,"tracking":"LG-88213"}"#
        ); // 120.0, like Python
        let content = |c| execute(&c, &tools, &no).content;
        assert_eq!(
            content(call("delete_order", "{}", "c1")),
            r#"unknown tool "delete_order"; available: get_order, get_refund, issue_refund"#
        );
        assert_eq!(
            content(call("get_order", "{order_id: A123", "c1")),
            "arguments are not valid JSON"
        );
        assert_eq!(
            content(call("get_order", r#"{"order_id":"Z999"}"#, "c1")),
            "get_order failed: no order Z999"
        );
        assert_eq!(
            content(call(
                "issue_refund",
                r#"{"order_id":"B456","amount":120}"#,
                "c1"
            )),
            "the user declined this action"
        );
    }

    #[test]
    fn a_side_effect_needs_valid_arguments_then_approval_then_its_own_rules() {
        let orders = load_orders(ORDERS);
        let tools = support_tools(&orders);
        let asked = Mutex::new(vec![]);
        let yes = |name: &str, args: &Value| {
            asked.lock().unwrap().push(format!("{name} {args}"));
            true
        };
        assert!(
            execute(
                &call("issue_refund", r#"{"order_id":"B456","amount":-5}"#, "c1"),
                &tools,
                &yes
            )
            .is_error
        );
        assert!(asked.lock().unwrap().is_empty()); // nobody approves a malformed call
        assert!(
            !execute(
                &call("issue_refund", r#"{"order_id":"B456","amount":120}"#, "c1"),
                &tools,
                &yes
            )
            .is_error
        );
        assert_eq!(
            *asked.lock().unwrap(),
            [r#"issue_refund {"amount":120,"order_id":"B456"}"#]
        ); // serde_json sorts keys
        let again = execute(
            &call("issue_refund", r#"{"order_id":"B456","amount":120}"#, "c1"),
            &tools,
            &yes,
        );
        assert_eq!(
            again.content,
            "issue_refund failed: order B456 already has a refund"
        );
    }

    #[test]
    fn the_round_trip() {
        let mut seen = vec![];
        let turns = vec![
            (
                String::new(),
                vec![
                    call("get_order", r#"{"order_id":"A123"}"#, "c1"),
                    call("get_refund", r#"{"order_id":"A123"}"#, "c2"),
                ],
            ),
            ("Your refund of 49.99 is being processed.".into(), vec![]),
        ];
        let tools = support_tools(&load_orders(ORDERS));
        let (_, history, rounds) = answer_with_tools(
            &mut scripted(turns, &mut seen),
            vec![Message::User("Where is my refund for A123?".into())],
            &tools,
            &no,
            5,
        )
        .unwrap();
        assert_eq!((rounds, history.len()), (2, 5));
        assert_eq!(
            seen[1][2],
            Message::Tool {
                call_id: "c1".into(),
                content: r#"{"status":"delivered","total":49.99}"#.into()
            }
        );
        assert_eq!(
            seen[1][3],
            Message::Tool {
                call_id: "c2".into(),
                content: r#"{"amount":49.99,"requested":"2026-09-28","status":"processing"}"#
                    .into()
            }
        );
    }

    #[test]
    fn text_in_a_tool_result_cannot_approve_anything() {
        let orders = load_orders(ORDERS);
        let tools = support_tools(&orders);
        let mut seen = vec![];
        let turns = vec![
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"D012"}"#, "c1")],
            ),
            (
                String::new(),
                vec![call(
                    "issue_refund",
                    r#"{"order_id":"D012","amount":500}"#,
                    "c2",
                )],
            ), // fooled by the note
            ("I can't issue that refund.".into(), vec![]),
        ];
        answer_with_tools(
            &mut scripted(turns, &mut seen),
            vec![Message::User("Check D012".into())],
            &tools,
            &no,
            5,
        )
        .unwrap();
        let Message::Tool { content, .. } = &seen[1][2] else {
            panic!()
        };
        assert!(content.contains("IGNORE ALL PREVIOUS INSTRUCTIONS"));
        assert_eq!(
            seen[2][4],
            Message::Tool {
                call_id: "c2".into(),
                content: "ERROR: the user declined this action".into()
            }
        );
        assert!(orders.lock().unwrap()["D012"]["refund"].is_null());
        let approved = execute(
            &call("issue_refund", r#"{"order_id":"D012","amount":500}"#, "c3"),
            &tools,
            &|_, _| true,
        );
        assert_eq!(
            approved.content,
            "issue_refund failed: refund 500 is more than the order total 30"
        );
    }

    #[test]
    fn a_model_that_never_stops_is_cut_off() {
        let tools = support_tools(&load_orders(ORDERS));
        let mut forever = |_: &[Message], _: &[Value]| {
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"A123"}"#, "c1")],
            )
        };
        let result = answer_with_tools(
            &mut forever,
            vec![Message::User("?".into())],
            &tools,
            &no,
            3,
        );
        assert_eq!(
            result.unwrap_err(),
            "no answer after 3 rounds of tool calls"
        );
    }
}
```

```rust
//! The support tools as an MCP server, with the official Rust SDK (rmcp 3.5 speaks 2026-07-28).
//!     cargo run --bin server              all three tools, over stdio
//!     cargo run --bin server -- --read-only  only the tools that change nothing
//! rmcp handles the protocol and the transport; `list_tools` and `call_tool` hand over to the
//! same registry and checks the tool loop uses.
use rmcp::model::{
    CacheScope, CallToolRequestParams, CallToolResponse, CallToolResult, ContentBlock,
    ListToolsResult, PaginatedRequestParams, ServerCapabilities, ServerConfig, Tool,
    ToolAnnotations,
};
use rmcp::service::{RequestContext, RoleServer};
use rmcp::{ErrorData, ServerHandler, ServiceExt};
use support_tools::{ToolCall, execute, load_orders, support_tools};

struct Support {
    tools: Vec<support_tools::Tool>,
}

impl ServerHandler for Support {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().build())
    }

    async fn list_tools(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, ErrorData> {
        let tools = self.tools.iter().map(|t| {
            let schema = t.schema.as_object().cloned().unwrap_or_default();
            let hints = ToolAnnotations::from_raw(
                None,
                Some(!t.side_effects),
                Some(t.side_effects),
                None,
                None,
            );
            Tool::new(t.name, t.description, schema).with_annotations(hints)
        });
        // Always the same order; and 2026-07-28 requires cache hints on every list, which rmcp leaves to us.
        Ok(ListToolsResult::with_all_items(tools.collect())
            .with_ttl_ms(300_000)
            .with_cache_scope(CacheScope::Public))
    }

    async fn call_tool(
        &self,
        request: CallToolRequestParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, ErrorData> {
        if !self.tools.iter().any(|t| t.name == request.name) {
            // a protocol error: the request itself is wrong
            return Err(ErrorData::invalid_params(
                format!("Unknown tool: {}", request.name),
                None,
            ));
        }
        let arguments =
            serde_json::Value::Object(request.arguments.unwrap_or_default()).to_string();
        let call = ToolCall {
            id: "mcp".into(),
            name: request.name.to_string(),
            arguments,
        };
        // Approval is the host's job: it asks the person before calling a destructive tool.
        let outcome = execute(&call, &self.tools, &|_, _| true);
        let content = vec![ContentBlock::text(outcome.content)];
        Ok(if outcome.is_error {
            CallToolResult::error(content)
        } else {
            CallToolResult::success(content)
        }
        .into())
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut tools = support_tools(&load_orders("../shared/orders.json"));
    if std::env::args().any(|a| a == "--read-only") {
        tools.retain(|t| !t.side_effects);
    }
    eprintln!(
        "support-tools MCP server: {}",
        tools.iter().map(|t| t.name).collect::<Vec<_>>().join(", ")
    ); // stderr only
    let server = Support { tools }.serve(rmcp::transport::stdio()).await?;
    server.waiting().await?; // returns when the client closes stdin
    Ok(())
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/07-tools-and-mcp/labs/rust). `python3 labs/run.py tools-and-mcp/rust` checks formatting, runs the tests, then the conformance check on `cargo run --bin server`.

## 8. C#

C# uses `System.Text.Json`'s mutable `JsonNode` for the orders and JsonSchema.Net for the arguments. The server uses the official `ModelContextProtocol` SDK's low-level `McpServerHandlers`: a `ListToolsHandler` that also sets `TimeToLive` and `CacheScope`, and a `CallToolHandler` that throws `McpProtocolException` for an unknown tool and returns a `CallToolResult` with `IsError` for everything else. For a server whose tools are plain methods, the SDK's `[McpServerTool]` attributes and `AddMcpServer().WithStdioServerTransport()` hosting are the shorter route. One program holds both halves: `dotnet Tools.dll` runs the checks, and `dotnet Tools.dll serve` runs the server.

```csharp
// Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
// JSON is System.Text.Json's mutable JsonNode; arguments are checked with JsonSchema.Net.
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;
using Json.Schema;

public delegate JsonNode? Run(JsonObject args);

public sealed record Tool(string Name, string Description, JsonObject InputSchema, bool SideEffects, Run Run)
{
    // What the model sees: never Run or SideEffects.
    public JsonObject Spec() => new() { ["name"] = Name, ["description"] = Description, ["inputSchema"] = InputSchema.DeepClone() };
}

public sealed record ToolCall(string Id, string Name, string Arguments);
public sealed record ToolResult(string Id, string Content, bool IsError);

/// <summary>What can go wrong inside a tool, in words the model can act on.</summary>
public sealed class ToolFailure(string message) : Exception(message);

public sealed record Message(string Role, string Content, string? ToolCallId = null, IReadOnlyList<ToolCall>? Calls = null);
public sealed record Turn(string Content, IReadOnlyList<ToolCall> Calls);

public static class Tools
{
    public static List<string> Validate(JsonObject schema, JsonNode? value)
    {
        var results = JsonSchema.FromText(schema.ToJsonString())
            .Evaluate(JsonSerializer.SerializeToElement(value), new EvaluationOptions { OutputFormat = OutputFormat.List });
        return (results.Details ?? [])
            .Where(d => d.Errors is { Count: > 0 })
            // Drop the summaries ("some properties did not match") and the bare false-schema leaf: keep one line per problem.
            .SelectMany(d => d.Errors!.Where(e => e.Key is not ("properties" or "")).Select(e => $"arguments{d.InstanceLocation}: {e.Value}"))
            .ToList();
    }

    public static ToolResult Execute(ToolCall call, IReadOnlyList<Tool> tools, Func<string, JsonObject, bool> approve)
    {
        ToolResult Fail(string content) => new(call.Id, content, true);
        var tool = tools.FirstOrDefault(t => t.Name == call.Name);
        if (tool is null) return Fail($"unknown tool \"{call.Name}\"; available: {string.Join(", ", tools.Select(t => t.Name))}");
        JsonObject? args;
        try
        {
            args = JsonNode.Parse(string.IsNullOrEmpty(call.Arguments) ? "{}" : call.Arguments) as JsonObject;
        }
        catch (JsonException)
        {
            return Fail("arguments are not valid JSON");
        }
        if (args is null) return Fail("arguments are not valid JSON");
        var problems = Validate(tool.InputSchema, args);
        if (problems.Count > 0) return Fail(string.Join("; ", problems));
        if (tool.SideEffects && !approve(tool.Name, args)) return Fail("the user declined this action");
        try
        {
            var content = tool.Run(args)?.ToJsonString() ?? "null";
            return new(call.Id, content.Length > 2000 ? content[..2000] + " …[truncated]" : content, false);
        }
        catch (ToolFailure e) // the message, never a stack trace
        {
            return Fail($"{tool.Name} failed: {e.Message}");
        }
    }

    public static JsonObject LoadOrders(string path) => JsonNode.Parse(File.ReadAllText(path))!.AsObject();

    const string OrderId = """{"type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits"}""";

    public static List<Tool> SupportTools(JsonObject orders)
    {
        var oneId = JsonNode.Parse($$$"""{"type": "object", "properties": {"order_id": {{{OrderId}}}}, "required": ["order_id"], "additionalProperties": false}""")!.AsObject();
        var refundArgs = JsonNode.Parse($$$"""
            {"type": "object", "properties": {"order_id": {{{OrderId}}}, "amount": {"type": "number", "minimum": 0.01}},
             "required": ["order_id", "amount"], "additionalProperties": false}
            """)!.AsObject();
        JsonObject Find(JsonObject args)
        {
            var id = args["order_id"]!.GetValue<string>();
            return orders[id]?.AsObject() ?? throw new ToolFailure($"no order {id}");
        }
        static string Plain(decimal x) => x.ToString("0.##", CultureInfo.InvariantCulture); // 500, 49.99
        return
        [
            new("get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
                oneId, false, args =>
                {
                    var copy = Find(args).DeepClone().AsObject();
                    copy.Remove("refund"); // the refund has its own tool
                    return copy;
                }),
            new("get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
                oneId.DeepClone().AsObject(), false, args => Find(args)["refund"]?.DeepClone() ?? new JsonObject { ["status"] = "none" }),
            new("issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
                refundArgs, true, args =>
                {
                    var order = Find(args);
                    decimal amount = args["amount"]!.GetValue<decimal>(), total = order["total"]!.GetValue<decimal>();
                    if (order["refund"] is not null) throw new ToolFailure($"order {args["order_id"]} already has a refund");
                    if (amount > total) throw new ToolFailure($"refund {Plain(amount)} is more than the order total {Plain(total)}");
                    order["refund"] = new JsonObject { ["status"] = "processing", ["amount"] = amount, ["requested"] = "today" };
                    return order["refund"]!.DeepClone();
                }),
        ];
    }

    public static (string Answer, List<Message> History, int Rounds) AnswerWithTools(
        Func<IReadOnlyList<Message>, IReadOnlyList<JsonObject>, Turn> model, IEnumerable<Message> messages, IReadOnlyList<Tool> tools,
        Func<string, JsonObject, bool> approve, int maxRounds = 5)
    {
        var history = messages.ToList();
        var specs = tools.Select(t => t.Spec()).ToList();
        for (var round = 1; round <= maxRounds; round++)
        {
            var turn = model([.. history], specs);
            history.Add(new("assistant", turn.Content, Calls: turn.Calls));
            if (turn.Calls.Count == 0) return (turn.Content, history, round);
            foreach (var call in turn.Calls) // one result per call, in the order of the calls
            {
                var r = Execute(call, tools, approve);
                history.Add(new("tool", r.IsError ? $"ERROR: {r.Content}" : r.Content, call.Id));
            }
        }
        throw new InvalidOperationException($"no answer after {maxRounds} rounds of tool calls");
    }
}
```

```csharp
// The support tools as an MCP server, with the official C# SDK (ModelContextProtocol 2.2 speaks 2026-07-28).
//   dotnet Tools.dll serve              all three tools, over stdio
//   dotnet Tools.dll serve --read-only  only the tools that change nothing
// The SDK handles the protocol and the transport; the two handlers hand over to the same registry
// and checks the tool loop uses.
using System.Text.Json;
using ModelContextProtocol;
using ModelContextProtocol.Protocol;
using ModelContextProtocol.Server;
using McpTool = ModelContextProtocol.Protocol.Tool;

public static class Server
{
    public static async Task Run(string[] args)
    {
        var all = Tools.SupportTools(Tools.LoadOrders("../shared/orders.json"));
        var tools = args.Contains("--read-only") ? all.Where(t => !t.SideEffects).ToList() : all;
        Console.Error.WriteLine($"support-tools MCP server: {string.Join(", ", tools.Select(t => t.Name))}"); // stderr only
        var options = new McpServerOptions
        {
            ServerInfo = new Implementation { Name = "support-tools", Version = "1.0.0" },
            Handlers = new McpServerHandlers
            {
                ListToolsHandler = (request, ct) => ValueTask.FromResult(new ListToolsResult
                {
                    Tools = [.. tools.Select(t => new McpTool
                    {
                        Name = t.Name,
                        Description = t.Description,
                        InputSchema = JsonSerializer.SerializeToElement(t.InputSchema),
                        Annotations = new ToolAnnotations { ReadOnlyHint = !t.SideEffects, DestructiveHint = t.SideEffects },
                    })],
                    TimeToLive = TimeSpan.FromMinutes(5), // 2026-07-28 requires cache hints on every list
                    CacheScope = CacheScope.Public,
                }),
                CallToolHandler = (request, ct) =>
                {
                    var name = request.Params!.Name;
                    if (tools.All(t => t.Name != name))
                        throw new McpProtocolException($"Unknown tool: {name}", McpErrorCode.InvalidParams); // a protocol error
                    var arguments = JsonSerializer.Serialize(request.Params.Arguments ?? new Dictionary<string, JsonElement>());
                    // Approval is the host's job: it asks the person before calling a destructive tool.
                    var outcome = Tools.Execute(new ToolCall("mcp", name, arguments), tools, (_, _) => true);
                    return ValueTask.FromResult(new CallToolResult { Content = [new TextContentBlock { Text = outcome.Content }], IsError = outcome.IsError });
                },
            },
        };
        await using var server = McpServer.Create(new StdioServerTransport("support-tools"), options);
        await server.RunAsync(); // returns when the client closes stdin
    }
}
```

```csharp
// Checks: the same results as every other language. `dotnet Tools.dll serve` runs the MCP server instead.
using System.Text.Json.Nodes;

if (args.FirstOrDefault() == "serve")
{
    await Server.Run(args[1..]);
    return;
}

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

const string Orders = "../shared/orders.json";
static ToolCall Call(string name, string args, string id = "c1") => new(id, name, args);
static bool No(string name, JsonObject args) => false;

// A pretend model that plays back a script of turns and records what it was sent.
static Func<IReadOnlyList<Message>, IReadOnlyList<JsonObject>, Turn> Scripted(Queue<Turn> turns, List<IReadOnlyList<Message>> seen) =>
    (history, _) =>
    {
        seen.Add(history);
        return turns.Dequeue();
    };

var tools = Tools.SupportTools(Tools.LoadOrders(Orders));
Check(string.Join(",", tools[0].Spec().Select(p => p.Key)) == "name,description,inputSchema", "the model sees specs, never functions");

var problems = Tools.Validate(tools[2].InputSchema, JsonNode.Parse("""{"order_id":"a-1","amount":0,"note":"hi"}"""));
Console.WriteLine("validation: " + string.Join(" | ", problems));
Check(problems.Count == 3, problems.Count); // JsonSchema.Net's own wording, every problem found

var ok = Tools.Execute(Call("get_order", """{"order_id":"B456"}"""), tools, No);
Check(ok.Content == """{"status":"shipped","total":120.00,"tracking":"LG-88213"}""", ok.Content); // the number exactly as the file wrote it
string Content(ToolCall c) => Tools.Execute(c, tools, No).Content;
Check(Content(Call("delete_order", "{}")) == "unknown tool \"delete_order\"; available: get_order, get_refund, issue_refund", "unknown");
Check(Content(Call("get_order", "{order_id: A123")) == "arguments are not valid JSON", "bad JSON");
Check(Content(Call("get_order", """{"order_id":"Z999"}""")) == "get_order failed: no order Z999", "no order");
Check(Content(Call("issue_refund", """{"order_id":"B456","amount":120}""")) == "the user declined this action", "declined");

// a side effect: valid arguments, then approval, then the tool's own rules
var orders = Tools.LoadOrders(Orders);
var fresh = Tools.SupportTools(orders);
var asked = new List<string>();
bool Yes(string name, JsonObject args) { asked.Add($"{name} {args.ToJsonString()}"); return true; }
Check(Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":-5}"""), fresh, Yes).IsError && asked.Count == 0, "malformed");
Check(!Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":120}"""), fresh, Yes).IsError, "approved");
Check(asked.SequenceEqual(["""issue_refund {"order_id":"B456","amount":120}"""]), string.Join(" ", asked));
Check(Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":120}"""), fresh, Yes).Content == "issue_refund failed: order B456 already has a refund", "twice");

// the round trip
var seen = new List<IReadOnlyList<Message>>();
var model = Scripted(new([
    new("", [Call("get_order", """{"order_id":"A123"}""", "c1"), Call("get_refund", """{"order_id":"A123"}""", "c2")]),
    new("Your refund of 49.99 is being processed.", []),
]), seen);
var (answer, history, rounds) = Tools.AnswerWithTools(model, [new("user", "Where is my refund for A123?")], tools, No);
Check(rounds == 2 && history.Count == 5, (rounds, history.Count));
Check(seen[1][2].Content == """{"status":"delivered","total":49.99}""", seen[1][2].Content);
Check(seen[1][3].Content == """{"status":"processing","amount":49.99,"requested":"2026-09-28"}""", seen[1][3].Content);

// text in a tool result can't approve anything
var injected = Tools.LoadOrders(Orders);
var seen2 = new List<IReadOnlyList<Message>>();
var fooled = Scripted(new([
    new("", [Call("get_order", """{"order_id":"D012"}""")]),
    new("", [Call("issue_refund", """{"order_id":"D012","amount":500}""", "c2")]),
    new("I can't issue that refund.", []),
]), seen2);
Tools.AnswerWithTools(fooled, [new("user", "Check D012")], Tools.SupportTools(injected), No);
Check(seen2[1][^1].Content.Contains("IGNORE ALL PREVIOUS INSTRUCTIONS"), "the injection reached the model");
Check(seen2[2][^1].Content == "ERROR: the user declined this action" && injected["D012"]!["refund"] is null, "declined");
var approved = Tools.Execute(Call("issue_refund", """{"order_id":"D012","amount":500}""", "c3"), Tools.SupportTools(injected), (_, _) => true);
Check(approved.Content == "issue_refund failed: refund 500 is more than the order total 30", approved.Content);

// a model that never stops is cut off
try
{
    Tools.AnswerWithTools((_, _) => new("", [Call("get_order", """{"order_id":"A123"}""")]), [new("user", "?")], tools, No, maxRounds: 3);
    Check(false, "should have stopped");
}
catch (InvalidOperationException e)
{
    Check(e.Message == "no answer after 3 rounds of tool calls", e.Message);
}

Console.WriteLine("all tools checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/07-tools-and-mcp/labs/csharp). `container.sh` builds and checks inside the .NET SDK container, then runs the conformance check with the client on your machine and the server in the container: `podman run -i` connects the container's stdin and stdout to the client, which is all stdio needs. Restored NuGet packages are kept in `~/.cache/knowledgebase-labs/nuget`. `python3 labs/run.py tools-and-mcp/csharp` (needs Podman).

## Common pitfalls

1. **Trusting an SDK to speak the newest protocol.** Java's official SDK doesn't yet. Look at what the SDK says it supports, and test it.
2. **Trusting an SDK to fill in what the spec requires.** `rmcp` leaves the `tools/list` cache hints to you. Only a check against an independent client shows that.
3. **Validation messages no model can use.** "The string value is not a match for the indicated regular expression" doesn't say which expression. Put the rule in the schema's description, or rewrite the message.
4. **Comparing tool results as bytes across languages.** `120`, `120.0` and `120.00` are the same total. Compare parsed values, as the conformance check does.
5. **Holding a lock across an await.** The Rust tools lock the store inside one synchronous call only. Holding it across an `.await` would block every other tool call for as long as the slowest one takes.
6. **Assuming every SDK reports an unknown tool the same way.** Some return a protocol error, some a tool error. Your host should handle both.

## Check your understanding

1. Why is the Java server written by hand, when the Python, Go, Rust and C# ones use their official SDKs?
2. What did the conformance check catch in the Rust server, and why couldn't the Rust tests have caught it?
3. `get_order B456` gives `120`, `120.0` or `120.00` depending on the language. Does it matter, and when?
4. In Python's `MCPServer` and Go's `AddTool`, where does the tool's input schema come from, and what does the SDK do with it?
5. Go's validator reports only the first problem with a call. What does that cost a model trying to fix its arguments?
6. Why does the conformance check pin the client to 2026-07-28 instead of letting it negotiate?

<details>
<summary>Answers — after your attempt</summary>

1. The Java SDK's newest release speaks only 2025-11-25, with the `initialize` handshake. A server built with it couldn't pass a check pinned to 2026-07-28.
2. `tools/list` had no `ttlMs` or `cacheScope`, which the 2026-07-28 revision requires. The Rust tests check the tools themselves, not the protocol messages; only a client that knows the protocol's rules could notice something missing from them.
3. Not to the meaning: all three are the same value, and a model reads them the same. It matters when bytes are compared, such as a prompt cache, a recorded cassette or a test that compares strings. Compare parsed values in tests, and keep one serialiser per prompt.
4. From the function's types: Python's type hints with Pydantic constraints, Go's argument struct. The SDK publishes the schema in `tools/list` and validates every call against it before your function runs.
5. Extra rounds. With three problems, the model fixes one, calls again, learns about the second, and so on: each round is another model call and another chance to give up. Reporting every problem lets it fix them all at once.
6. So the check can't pass by falling back to the older handshake. Pinned, a server either speaks the current revision or fails.

</details>

## Practice — independent task

**Give your own server to the inspector.**

1. In your language, add a fourth tool to the lab's server: `list_orders`, read-only, returning the IDs and statuses of all orders.
2. Extend `conformance.ts` to check that `list_orders` appears, is marked read-only, and returns four orders.
3. Run the check against your server. Then break your server on purpose (drop the annotations, or return the list in a random order) and confirm the check catches it.

**Done when:** your server passes the extended check, and each deliberate break makes it fail with a message that says what's wrong.

## Before moving on

You can check tool arguments with your language's library, build an MCP server with your language's official SDK or by hand, and check any server against the official client.

**Recap.** The checks, the round trip and the defences are the same in every language; the libraries differ, and so do their messages, number formatting and key order. Python, Go, Rust and C# have official SDKs that speak 2026-07-28; Java's doesn't yet, so its server is hand-written. Python and Go derive schemas from types; Rust and C# use low-level handlers that hand over to the lab's own checks. One conformance check with the official client, pinned to the current revision, tests every server the same way, and it caught a required field one SDK leaves to you.

## Related
- [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|Tools and MCP]] — the main lesson
- [[ai-ml/03-ai-engineer/11-structured-output/in-other-languages|Structured output in other languages]] — schemas and validation in each language
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/in-other-languages|Cost, caching and latency in other languages]] — why bytes differ between languages, and why it matters
- [[ai-ml/03-ai-engineer/08-agents/index|Agents]] — the loop these tools run in
