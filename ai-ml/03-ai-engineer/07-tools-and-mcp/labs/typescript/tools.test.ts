import { test } from "node:test";
import assert from "node:assert/strict";
import { answerWithTools, type Message, type ToolModel, type Turn } from "./loop.ts";
import { openAITools, toWire } from "./openai-tools.ts";
import { loadOrders, supportTools } from "./support-tools.ts";
import { execute, specs, validate, type ToolCall } from "./tools.ts";

const call = (name: string, args: unknown, id = "c1"): ToolCall => ({ id, name, arguments: typeof args === "string" ? args : JSON.stringify(args) });

/** A pretend model that plays back a script of turns and records what it was sent. */
function scripted(turns: Turn[]) {
  const seen: Message[][] = [];
  const model: ToolModel = async (messages) => {
    seen.push(structuredClone(messages));
    const turn = turns.shift();
    if (!turn) throw new Error("the script ran out");
    return turn;
  };
  return { model, seen };
}

test("the model sees names, descriptions and schemas, never the functions", () => {
  const visible = specs(supportTools(loadOrders()));
  assert.deepEqual(visible.map((t) => t.name), ["get_order", "get_refund", "issue_refund"]);
  assert.deepEqual(Object.keys(visible[0]), ["name", "description", "inputSchema"]);
});

test("validation gives messages a model can act on", () => {
  const schema = supportTools(loadOrders())[2].inputSchema;
  assert.deepEqual(validate(schema, { order_id: "A123", amount: 10 }), []);
  assert.deepEqual(validate(schema, { order_id: "a-1", amount: 0, note: "hi" }), [
    "arguments.order_id: must match ^[A-Z][0-9]{3}$",
    "arguments.amount: must be at least 0.01",
    "arguments.note: not allowed",
  ]);
  assert.deepEqual(validate(schema, { amount: "ten" }), ["arguments.order_id: required", "arguments.amount: expected number, got string"]);
});

test("every way a call can go wrong becomes a result, not a crash", async () => {
  const tools = supportTools(loadOrders());
  const no = () => false;
  assert.deepEqual(await execute(call("get_order", { order_id: "B456" }), tools, no), {
    id: "c1",
    isError: false,
    content: '{"status":"shipped","total":120,"tracking":"LG-88213"}',
  });
  const content = async (c: ToolCall) => (await execute(c, tools, no)).content;
  assert.equal(await content(call("delete_order", {})), 'unknown tool "delete_order"; available: get_order, get_refund, issue_refund');
  assert.equal(await content(call("get_order", "{order_id: A123")), "arguments are not valid JSON");
  assert.equal(await content(call("get_order", { order_id: "Z999" })), "get_order failed: no order Z999");
  assert.equal(await content(call("issue_refund", { order_id: "B456", amount: 120 })), "the user declined this action");
});

test("a side effect runs only after approval, and only if it's valid", async () => {
  const orders = loadOrders();
  const tools = supportTools(orders);
  const asked: unknown[] = [];
  const yes = (c: unknown) => (asked.push(c), true);
  const invalid = await execute(call("issue_refund", { order_id: "B456", amount: -5 }), tools, yes);
  assert.equal(invalid.isError, true);
  assert.deepEqual(asked, []); // nobody was asked to approve a malformed call
  const ok = await execute(call("issue_refund", { order_id: "B456", amount: 120 }), tools, yes);
  assert.equal(ok.isError, false);
  assert.deepEqual(asked, [{ name: "issue_refund", args: { order_id: "B456", amount: 120 } }]);
  assert.equal(orders.B456.refund?.status, "processing");
  const again = await execute(call("issue_refund", { order_id: "B456", amount: 120 }), tools, yes);
  assert.equal(again.content, "issue_refund failed: order B456 already has a refund"); // the tool checks its own rules too
});

test("the round trip: two lookups, then an answer", async () => {
  const { model, seen } = scripted([
    { content: "", toolCalls: [call("get_order", { order_id: "A123" }, "c1"), call("get_refund", { order_id: "A123" }, "c2")] },
    { content: "Your refund of 49.99 for order A123 is being processed; it was requested on 28 September.", toolCalls: [] },
  ]);
  const user: Message = { role: "user", content: "Where is my refund for order A123?" };
  const { answer, messages, rounds } = await answerWithTools(model, [user], supportTools(loadOrders()));
  assert.equal(rounds, 2);
  assert.match(answer, /49\.99/);
  assert.deepEqual(seen[1].slice(2), [
    { role: "tool", toolCallId: "c1", content: '{"status":"delivered","total":49.99}' },
    { role: "tool", toolCallId: "c2", content: '{"status":"processing","amount":49.99,"requested":"2026-09-28"}' },
  ]);
  assert.equal(messages.length, 5); // user, assistant with calls, two tool results, assistant answer
});

test("an error goes back to the model, which corrects its own call", async () => {
  const { model, seen } = scripted([
    { content: "", toolCalls: [call("get_refund", { order_id: "a123" })] },
    { content: "", toolCalls: [call("get_refund", { order_id: "A123" }, "c2")] },
    { content: "It's being processed.", toolCalls: [] },
  ]);
  await answerWithTools(model, [{ role: "user", content: "refund for a123?" }], supportTools(loadOrders()));
  assert.deepEqual(seen[1].at(-1), { role: "tool", toolCallId: "c1", content: "ERROR: arguments.order_id: must match ^[A-Z][0-9]{3}$" });
});

test("text inside a tool result is data, and can't approve anything", async () => {
  const orders = loadOrders();
  const { model, seen } = scripted([
    { content: "", toolCalls: [call("get_order", { order_id: "D012" })] },
    // Suppose the model is fooled by the note and asks for the refund it describes:
    { content: "", toolCalls: [call("issue_refund", { order_id: "D012", amount: 500 }, "c2")] },
    { content: "I can't issue that refund.", toolCalls: [] },
  ]);
  await answerWithTools(model, [{ role: "user", content: "What's the status of D012?" }], supportTools(orders), { approve: () => false });
  assert.match(String(seen[1].at(-1)?.content), /IGNORE ALL PREVIOUS INSTRUCTIONS/); // the injection reached the model
  assert.equal(seen[2].at(-1)?.content, "ERROR: the user declined this action"); // the person saw the exact call and said no
  assert.equal(orders.D012.refund, null);
  // And had they clicked yes, the tool's own rule would still have refused:
  const approved = await execute(call("issue_refund", { order_id: "D012", amount: 500 }), supportTools(orders), () => true);
  assert.equal(approved.content, "issue_refund failed: refund 500 is more than the order total 30");
});

test("a model that never stops asking for tools is cut off", async () => {
  const forever: ToolModel = async () => ({ content: "", toolCalls: [call("get_order", { order_id: "A123" })] });
  await assert.rejects(answerWithTools(forever, [{ role: "user", content: "?" }], supportTools(loadOrders()), { maxRounds: 3 }), /no answer after 3 rounds/);
});

test("the OpenAI wire format: tools as functions, calls and results matched by id", async () => {
  let body: any;
  const fakeFetch = (async (_url: string, init: RequestInit) => {
    body = JSON.parse(String(init.body));
    const message = { content: null, tool_calls: [{ id: "call_9", type: "function", function: { name: "get_order", arguments: { order_id: "A123" } } }] };
    return new Response(JSON.stringify({ choices: [{ message }] }));
  }) as typeof fetch;
  const model = openAITools({ baseUrl: "http://x/v1", model: "m", fetch: fakeFetch });
  const history: Message[] = [
    { role: "user", content: "hi" },
    { role: "assistant", content: "", toolCalls: [call("get_refund", { order_id: "C789" }, "call_1")] },
    { role: "tool", toolCallId: "call_1", content: '{"status":"paid"}' },
  ];
  const turn = await model(history, specs(supportTools(loadOrders())).slice(0, 1));
  assert.deepEqual(body.tools[0].function.name, "get_order");
  assert.deepEqual(body.messages.slice(1), toWire(history).slice(1));
  assert.deepEqual(body.messages[2], { role: "tool", tool_call_id: "call_1", content: '{"status":"paid"}' });
  assert.deepEqual(turn, { content: "", toolCalls: [{ id: "call_9", name: "get_order", arguments: '{"order_id":"A123"}' }] }); // object arguments normalised to a string
});
