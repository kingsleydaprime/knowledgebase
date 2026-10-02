import { test } from "node:test";
import assert from "node:assert/strict";
import type { Message } from "../../../07-tools-and-mcp/labs/typescript/loop.ts";
import { loadOrders, supportTools } from "../../../07-tools-and-mcp/labs/typescript/support-tools.ts";
import type { Tool, ToolCall } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";
import { type AgentModel, type AgentTurn, runAgent } from "./agent.ts";
import { scoreTrajectory } from "./trajectory.ts";
import { refundStatus } from "./workflow.ts";

const call = (name: string, args: object, id: string): ToolCall => ({ id, name, arguments: JSON.stringify(args) });
const ask = (content: string): Message[] => [{ role: "user", content }];

/** A pretend model that plays back a script of turns. */
function scripted(turns: AgentTurn[]): AgentModel {
  return async () => {
    const turn = turns.shift();
    if (!turn) throw new Error("the script ran out");
    return turn;
  };
}

test("a two-step answer, with a trace of every step", async () => {
  const model = scripted([
    { content: "", toolCalls: [call("get_order", { order_id: "A123" }, "c1"), call("get_refund", { order_id: "A123" }, "c2")] },
    { content: "Your refund of 49.99 is being processed.", toolCalls: [] },
  ]);
  const outcome = await runAgent(model, ask("Where is my refund for A123?"), supportTools(loadOrders()));
  assert.equal(outcome.status, "answered");
  assert.deepEqual(outcome.trace.map((s) => s.calls.map((c) => c.name)), [["get_order", "get_refund"], []]);
  assert.deepEqual(scoreTrajectory(outcome, { status: "answered", mustCall: ["get_refund"], mustNotCall: ["issue_refund"], maxSteps: 3 }), []);
});

test("read-only calls run at the same time; a side effect waits and runs alone", async () => {
  const log: string[] = [];
  const slow = (name: string, sideEffects: boolean, ms: number): Tool => ({
    name,
    description: name,
    inputSchema: { type: "object" },
    sideEffects,
    run: async () => {
      log.push(`start ${name}`);
      await new Promise((r) => setTimeout(r, ms));
      log.push(`end ${name}`);
      return name;
    },
  });
  const tools = [slow("read_a", false, 30), slow("read_b", false, 10), slow("write_c", true, 1)];
  const model = scripted([
    { content: "", toolCalls: [call("write_c", {}, "1"), call("read_a", {}, "2"), call("read_b", {}, "3")] },
    { content: "done", toolCalls: [] },
  ]);
  const outcome = await runAgent(model, ask("go"), tools, { approve: () => true });
  assert.deepEqual(log, ["start read_a", "start read_b", "end read_b", "end read_a", "start write_c", "end write_c"]);
  assert.deepEqual(outcome.messages.filter((m) => m.role === "tool").map((m) => m.toolCallId), ["1", "2", "3"]); // results in call order
});

test("a step limit stops an agent that never finishes", async () => {
  let n = 0;
  const wandering: AgentModel = async () => ({ content: "", toolCalls: [call("get_order", { order_id: `A${100 + n}` }, `c${n++}`)] });
  const outcome = await runAgent(wandering, ask("find my order"), supportTools(loadOrders()), {
    limits: { maxSteps: 3, maxTokens: 1e9, maxRepeats: 5 },
  });
  assert.equal(outcome.status, "step_limit");
  assert.equal(outcome.trace.length, 3);
  assert.deepEqual(scoreTrajectory(outcome, { status: "answered" }), ["ended step_limit, expected answered"]);
});

test("the same call again and again is caught as stuck, long before the step limit", async () => {
  const repeating: AgentModel = async () => ({ content: "", toolCalls: [call("get_refund", { order_id: "Z999" }, "x")] });
  const outcome = await runAgent(repeating, ask("refund for Z999?"), supportTools(loadOrders()), {
    limits: { maxSteps: 20, maxTokens: 1e9, maxRepeats: 2 },
  });
  assert.equal(outcome.status, "stuck");
  assert.equal(outcome.trace.length, 3); // two tries were allowed; the third identical call stopped it
});

test("a token budget stops a run that's getting expensive", async () => {
  const usage = { inputTokens: 25_000, outputTokens: 500 }; // the whole history is resent every step
  const model = scripted([
    { content: "", toolCalls: [call("get_order", { order_id: "A123" }, "c1")], usage },
    { content: "", toolCalls: [call("get_order", { order_id: "B456" }, "c2")], usage },
    { content: "never reached", toolCalls: [], usage },
  ]);
  const outcome = await runAgent(model, ask("compare my orders"), supportTools(loadOrders()), {
    limits: { maxSteps: 10, maxTokens: 50_000, maxRepeats: 2 },
  });
  assert.equal(outcome.status, "token_limit");
  assert.deepEqual(outcome.trace.map((s) => s.tokens), [25_500, 25_500]);
});

test("the trajectory scorer names each broken expectation", async () => {
  const model = scripted([
    { content: "", toolCalls: [call("issue_refund", { order_id: "B456", amount: 120 }, "c1")] },
    { content: "I've asked for a refund.", toolCalls: [] },
  ]);
  const outcome = await runAgent(model, ask("Where is my refund for B456?"), supportTools(loadOrders()));
  assert.deepEqual(scoreTrajectory(outcome, { mustCall: ["get_refund"], mustNotCall: ["issue_refund"], answerMatches: /no refund/i }), [
    "never called get_refund",
    "called issue_refund", // it was declined, but asking at all is the failure: a status question needs no refund
    "answer doesn't match /no refund/i",
  ]);
});

test("the workflow: fixed steps, one model call, and nothing the model reads can make it act", async () => {
  const tools = supportTools(loadOrders());
  const prompts: string[] = [];
  const write = async (prompt: string) => (prompts.push(prompt), "Your refund of 49.99 for A123 is being processed.");

  const answered = await refundStatus("Where is my refund for order a123?", tools, write);
  assert.deepEqual(answered, { kind: "answer", text: "Your refund of 49.99 for A123 is being processed.", modelCalls: 1, toolCalls: 1 });
  assert.match(prompts[0], /Refund: \{"status":"processing","amount":49.99,"requested":"2026-09-28"\}/);

  assert.deepEqual(await refundStatus("Has my refund come through?", tools, write), {
    kind: "ask",
    text: "Could you tell me your order number? It looks like A123.",
  });
  // "address" contains "add", so the keyword rules say feature: the same flaw the evals lesson found in t15.
  // Harmless here, because anything that isn't billing goes to a person either way.
  assert.deepEqual(await refundStatus("Can you change my delivery address?", tools, write), { kind: "handoff", reason: "classified as feature" });

  // D012's injected note is on the order, not the refund, so this workflow never even reads it.
  await refundStatus("Where is my refund for D012?", tools, write);
  assert.doesNotMatch(prompts.at(-1)!, /IGNORE/);
  assert.equal(prompts.length, 2); // the "ask" and "handoff" paths made no model call at all
});
