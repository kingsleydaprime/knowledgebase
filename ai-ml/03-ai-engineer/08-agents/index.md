# Agents

> **[Intermediate]** · Covers what turns the tool-calling loop into an agent, and the harder question of when not to build one: workflows versus agents, the controls an agent's loop needs (step and token limits, stopping when it repeats itself, approval, a trace), evaluating the path an agent took as well as its answer, memory, and multi-agent systems. The worked example runs the support assistant as an agent and as a fixed workflow on the same questions. **Most tasks that look like they need an agent need a workflow.**

## Before you start

You can already:

- Run the tool-calling round trip, with validation, approval and untrusted tool results → [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tools and MCP]].
- Score a feature on a golden set, and evaluate the parts of a pipeline separately → [[ai-ml/03-ai-engineer/12-evals/index|evals]].
- Explain why every call resends the whole history, and what that costs → [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|cost, caching and latency]].

After this lesson you will be able to:

1. Say whether a task needs an agent or a workflow, and give the reasons an agent would be the wrong architecture.
2. Put the controls on an agent's loop — step limit, token budget, stuck detection, approval, trace — and explain what each one prevents.
3. Evaluate an agent on its trajectory as well as its final answer.
4. Explain short-term and long-term memory, and when more than one agent is worth the cost.

**Study route.** Read §1–3 first: they answer this week's closed-book question. Then §4–5, stopping at the prediction in §4, then the lab, then §6–8.

## The kid version

There are two ways to make dinner. You can follow a recipe: the same steps every time, easy to check, and you know how long it takes. Or you can hand a cook some money and say "make something nice", and they decide as they go: look in the fridge, go to the shop, change plans. The cook can handle surprises the recipe can't. But you'd give them a time limit, a budget, and a rule that anything expensive needs your OK, and you'd want them to tell you what they did. And if dinner is the same every night, you'd just use the recipe.

**Where the analogy stops working.** A cook remembers last week's dinner. A model doesn't remember anything between runs unless your code stores it and puts it back in the prompt. And a cook doesn't usually take orders from a note they found in the fridge; a model might.

## 1. Why this exists

The tools lesson's loop answered "Where is my refund for A123?" in two steps. Now the requests vary. "Where is my refund?" needs an order number first. "Compare my last three orders and cancel whichever hasn't shipped" needs an unknown number of lookups, then a decision, then an action. Writing a branch in code for every possible request is impossible, and that's the case for an **agent**: let the model decide the next step from what it has found so far.

But look at what the first question actually needed: find the order number, look up the refund, phrase the answer. The steps were known before the question arrived. Run it as an agent and you pay for two or three model calls instead of one, the path changes from run to run, and a model that can choose tools can be talked into choosing the wrong one. **Giving the model control over the steps is a cost, paid in money, latency, predictability and safety.** It's worth paying only when the steps can't be known in advance.

## Terms used in this lesson

1. **Agent**: This is a system in which a model decides its own next steps, which tools to call and when to stop, in a loop, until a task is done.
2. **Workflow**: This is a system in which models and tools run along paths written in code. The model may do some steps, but your code decides which steps happen, in what order.
3. **Agentic loop**: This is also known as **ReAct**, from "reason and act". It is the cycle of the model choosing an action, your code carrying it out, and the model reading the result and choosing again.
4. **Step**: This is one turn of the loop: one model call and the tool calls it asked for.
5. **Trajectory**: This is the full path an agent took: every step, every tool call and its result, in order.
6. **Stop reason**: This is why a run ended: the model answered, or a limit stopped it.
7. **Budget**: This is a limit on what a run may use: steps, tokens, money or time.
8. **Stuck**: An agent is stuck when it repeats the same action without making progress. Detecting it means stopping early instead of wasting the rest of the budget.
9. **Trace**: This is a record of every step of a run, kept so a person can see why the agent did what it did.
10. **Short-term memory**: This is the conversation history the model sees in its context window during a run.
11. **Compaction**: This means shrinking the history during a long run, by summarising or dropping old steps, so it fits the context and costs less.
12. **Long-term memory**: This is information stored outside the model between runs, such as facts about a user, and put back into the prompt when relevant.
13. **Multi-agent system**: This is a design in which several agents, often one coordinating **orchestrator** and several **workers**, split a task between them.

## 2. Workflows and agents

The useful line is not "uses a model" but **who decides the steps**. In a workflow, your code does; in an agent, the model does. Between them are a handful of workflow patterns that cover most real features:

- **Chaining.** Fixed steps in sequence, each one's output feeding the next, with code checks in between. Extract the order number, look it up, write the reply.
- **Routing.** Classify the input, then send it down one of several fixed paths. Billing questions go one way, bug reports another.
- **Parallel calls.** Split a task into independent parts and run them at the same time, or run the same task several times and combine the answers.
- **Orchestrator and workers.** One model call breaks a task into subtasks, workers handle them, and the results are combined. The subtasks vary, but the shape is fixed.
- **Evaluate and improve.** One call produces an answer, another checks it against criteria, and the first revises, up to a fixed number of rounds.

An **agent** is the loop from the tools lesson with the steps left open: the model keeps choosing tools until it decides the task is done. The worked example's `refundStatus` is a workflow that chains and routes: keyword rules route, a regular expression extracts the order number, code calls `get_refund`, and one model call writes the sentence. The model in it has no tools at all.

## 3. When an agent is the wrong architecture

Use this list before building one. Any "yes" is a reason to build a workflow, or a single model call, instead.

1. **Are the steps known in advance?** If you can draw the flowchart, write it in code. It's cheaper, faster, the same every time, and each step can be tested on its own.
2. **Would one well-prepared model call do?** Many "agents" are one call with better context: the right documents retrieved and the right facts looked up by code first.
3. **Are mistakes expensive and hard to undo?** An agent will sometimes choose wrongly. If a wrong choice moves money or deletes data, and no person checks each action, the agent's flexibility is a liability.
4. **Can you tell whether it worked?** If you can't check an agent's results with an eval, you can't improve it or know when it's broken.
5. **Is the budget tight?** Every step is a model call that resends the whole history. A run of eight steps sends the opening context eight times and the early results seven times. If a user is waiting, or each request must cost fractions of a cent, a fixed path wins.
6. **Will it read untrusted content while holding powerful tools?** Every web page, email or customer note an agent reads is a chance for an injected instruction to steer its next choice. A workflow whose model has no tools can't be steered into calling one.

**An agent is the right tool** when the steps really do depend on what's found along the way, the task is valuable enough to justify the cost and the waiting, mistakes can be caught (by tests, by review, by a person approving each action), and you can evaluate the results. Coding agents fit well: the steps are open-ended, and tests check each change.

The lab shows the difference on one question. For "Where is my refund for order a123?" the workflow makes **one** model call and **one** tool call, the same every time. The agent makes at least two model calls, and the second resends the first's results. For D012, whose order note carries an injected instruction, the workflow only ever reads the refund, so the note never reaches the model. The agent may look the order up, read the note, and depend on its controls to stop what follows.

## 4. The loop, with its controls

When an agent is the right design, the loop from the tools lesson needs more controls, because it now runs for longer with more freedom. The lab's `runAgent` adds them, and each one prevents a specific failure:

- **A step limit** stops a run that never finishes. Without it, a confused agent loops until something times out, spending all the while.
- **A token budget** stops a run that's getting expensive. Each step resends the history, so cost grows faster than the number of steps: with a 2,000-token opening and 500 new tokens a step, eight steps send 2,000 + 2,500 + … + 5,500 = **30,000** input tokens.
- **Stuck detection** stops an agent that repeats the same call with the same arguments. That's the most common way agents waste a budget, and it can be caught many steps before the step limit.
- **Approval** for side effects, as in the tools lesson. More autonomy makes it more important, not less.
- **Read-only calls in parallel, side effects alone.** Lookups can run at the same time. Anything that changes the world runs on its own, in order, after them. The results still go back in the order the model asked for them.
- **A trace and a stop reason.** Every run returns how it ended (`answered`, `step_limit`, `token_limit` or `stuck`) and what happened at each step. Without the trace, a wrong answer from a ten-step run is impossible to debug.

**Predict before reading on.** An agent asks for `get_refund Z999` every step, and gets the same error every time. With `maxRepeats` of 2 and a step limit of 20, how many steps does the run take, and what is its stop reason?

The answer: three steps, `stuck`. The first two identical calls are allowed (a retry after an error is reasonable); the third is refused, and the run ends 17 steps before the limit would have stopped it.

Notice what the controls don't do: they don't make the agent's choices better. They limit how much damage and waste a bad run can cause, and they make every run explainable afterwards.

## 5. Evaluating an agent

An agent's answer can be right for the wrong reasons: it guessed, or it called a tool it shouldn't have and was saved by a declined approval. So score the **trajectory** as well as the answer:

- **The outcome:** did it end with an answer, and is the answer right?
- **The path:** did it call the tools the task needs, and avoid the ones it shouldn't touch? A status question must not lead to `issue_refund`, even if a person declined it.
- **The efficiency:** how many steps and tokens did it take, compared with what the task needs?

The lab's `scoreTrajectory` checks these and names each failure, in the style of the evals lesson's gate. Two more things matter for agents:

- **Run each task several times.** An agent's path varies between runs. A task it passes two runs in three isn't reliable. Report how often it passes **every** run of a task (sometimes written pass^k), not only whether it passed once.
- **Test the limits deliberately.** Include tasks that can't be done, such as an order that doesn't exist, and check that the agent stops with an honest answer or a clean stop reason, rather than looping or inventing.

## 6. Memory

**Short-term memory** is the history in the context window. In a long run it grows until it's slow, expensive or too big. The usual fixes are to drop old tool results once they've been used, or to replace older steps with a summary, keeping the opening instructions and the most recent steps intact. Keep the start of the history fixed where you can, so the [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|prompt cache]] still hits.

**Long-term memory** is anything kept between runs: a user's preferences, facts learned earlier, what happened last time. The model keeps none of it. Your application writes it to a store, usually with embeddings so it can be searched ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG and embeddings]]), and puts the relevant parts back into the prompt next time. It helps to separate **episodic** memory (what happened) from **semantic** memory (facts that are true). Decide deliberately what gets written: a memory that an injected instruction managed to write is an injection that comes back in every future run.

## 7. More than one agent

A **multi-agent** design splits a task between agents: typically an orchestrator that plans and delegates, and workers with narrower tools and their own context windows. It helps when a task really is too big for one context, such as researching many sources at once, or when parts need different tools and permissions.

It also multiplies everything in §3. Each agent has its own loop, its own tokens and its own chance to go wrong, and they have to pass context to each other without losing it. Traces become trees. Start with one agent with good tools; most "we need several agents" turns out to be "we need better tools and a clearer task".

## 8. Frameworks and observability

Frameworks run the loop for you: LangGraph, the OpenAI Agents SDK, the Vercel AI SDK's agent classes, the Claude Agent SDK, and hosted agent services from the model providers. They're useful, but each hides the loop in this lesson behind its own names, so learn the loop first. When an agent misbehaves, you debug the loop, not the framework.

**Observability** for agents means a trace per run: every model call with its prompt, tokens and time, every tool call with its arguments and result, and the stop reason. Tools such as Langfuse and LangSmith collect them, and OpenTelemetry has conventions for recording model calls, so they fit into the [[devops/10-observability/index|observability]] you'd use for any service. The lab's trace is the smallest useful version.

## Worked example — the support assistant, as an agent and as a workflow

The agent's loop, with its controls. It imports the tools lesson's `execute`, so validation, approval and the tool's own rules all still apply:

```ts
// agent.ts — the tool loop from the tools lesson, with the controls that make it safe to give more freedom:
// limits on steps and tokens, a stop when it repeats itself, a trace of every step, and a reason it ended.
import type { Message, Turn } from "../../../07-tools-and-mcp/labs/typescript/loop.ts";
import { type Approve, execute, specs, type Tool, type ToolSpec } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";

export type AgentTurn = Turn & { usage?: { inputTokens: number; outputTokens: number } };
export type AgentModel = (messages: Message[], tools: ToolSpec[]) => Promise<AgentTurn>;

export type Limits = { maxSteps: number; maxTokens: number; maxRepeats: number };
export const DEFAULT_LIMITS: Limits = { maxSteps: 8, maxTokens: 50_000, maxRepeats: 2 };

export type Step = { step: number; calls: { name: string; arguments: string; isError: boolean }[]; tokens: number; text: string };
export type Outcome = {
  status: "answered" | "step_limit" | "token_limit" | "stuck";
  answer?: string;
  trace: Step[];
  messages: Message[];
};

export async function runAgent(
  model: AgentModel,
  messages: Message[],
  tools: Tool[],
  { limits = DEFAULT_LIMITS, approve = () => false }: { limits?: Limits; approve?: Approve } = {},
): Promise<Outcome> {
  const history = [...messages];
  const trace: Step[] = [];
  const seen = new Map<string, number>(); // how many times each exact call has been made
  let tokens = 0;
  const end = (status: Outcome["status"], answer?: string): Outcome => ({ status, answer, trace, messages: history });

  for (let step = 1; step <= limits.maxSteps; step++) {
    const turn = await model(history, specs(tools));
    const used = (turn.usage?.inputTokens ?? 0) + (turn.usage?.outputTokens ?? 0);
    tokens += used;
    history.push({ role: "assistant", content: turn.content, toolCalls: turn.toolCalls });
    const record: Step = { step, calls: [], tokens: used, text: turn.content };
    trace.push(record);
    if (turn.toolCalls.length === 0) return end("answered", turn.content);

    // The same call with the same arguments, again and again, means the agent is going round in circles.
    for (const call of turn.toolCalls) {
      const key = `${call.name} ${call.arguments}`;
      seen.set(key, (seen.get(key) ?? 0) + 1);
      if (seen.get(key)! > limits.maxRepeats) return end("stuck");
    }

    // Read-only calls run at the same time; anything with side effects runs alone, in order, after them.
    const sideEffects = new Set(tools.filter((t) => t.sideEffects).map((t) => t.name));
    const results = new Map<string, Awaited<ReturnType<typeof execute>>>();
    const readOnly = turn.toolCalls.filter((c) => !sideEffects.has(c.name));
    await Promise.all(readOnly.map(async (c) => results.set(c.id, await execute(c, tools, approve))));
    for (const c of turn.toolCalls.filter((c) => sideEffects.has(c.name))) results.set(c.id, await execute(c, tools, approve));

    for (const call of turn.toolCalls) { // results go back in the order of the calls, whatever order they finished in
      const result = results.get(call.id)!;
      history.push({ role: "tool", toolCallId: call.id, content: result.isError ? `ERROR: ${result.content}` : result.content });
      record.calls.push({ name: call.name, arguments: call.arguments, isError: result.isError });
    }
    if (tokens > limits.maxTokens) return end("token_limit");
  }
  return end("step_limit");
}
```

The same refund question as a workflow:

```ts
// workflow.ts — the same refund question answered by fixed steps written in code. The model writes one
// sentence at the end and has no tools at all. When the steps are known in advance, this is the better design.
import { keywords } from "../../../12-evals/labs/typescript/baselines.ts";
import { execute, type Tool } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";

export type Write = (prompt: string) => Promise<string>; // one plain model call, no tools

export type WorkflowResult =
  | { kind: "answer"; text: string; modelCalls: number; toolCalls: number }
  | { kind: "ask"; text: string } // we need something from the customer first
  | { kind: "handoff"; reason: string }; // not a question this workflow handles

export async function refundStatus(question: string, tools: Tool[], write: Write): Promise<WorkflowResult> {
  // 1. Route: the evals lab's keyword rules, free and instant.
  const label = await keywords(question);
  if (label !== "billing") return { kind: "handoff", reason: `classified as ${label}` };

  // 2. Extract the order ID with a pattern, not a model.
  const id = question.match(/\b([A-Za-z])(\d{3})\b/);
  if (!id) return { kind: "ask", text: "Could you tell me your order number? It looks like A123." };
  const orderId = id[1].toUpperCase() + id[2];

  // 3. Look the refund up: a fixed call, chosen by code.
  const refund = await execute({ id: "w1", name: "get_refund", arguments: JSON.stringify({ order_id: orderId }) }, tools, () => false);
  if (refund.isError) return { kind: "ask", text: `I couldn't find order ${orderId}. Could you check the number?` };

  // 4. One model call to phrase the facts. It has no tools, so nothing it reads can make it act.
  const text = await write(
    `Write a one-sentence reply to a customer about their refund, using only these facts.\n` +
      `Order: ${orderId}\nRefund: ${refund.content}\nTheir question: ${question}`,
  );
  return { kind: "answer", text, modelCalls: 1, toolCalls: 1 };
}
```

The trajectory scorer:

```ts
// trajectory.ts — score how an agent got there, not only where it ended up.
import type { Outcome } from "./agent.ts";

export type Expect = {
  status?: Outcome["status"];
  mustCall?: string[]; // tools that must appear somewhere in the trace
  mustNotCall?: string[]; // tools that must never be requested
  maxSteps?: number;
  answerMatches?: RegExp;
};

/** Every expectation the trace breaks, in words. An empty list is a pass. */
export function scoreTrajectory(outcome: Outcome, expect: Expect): string[] {
  const called = outcome.trace.flatMap((s) => s.calls.map((c) => c.name));
  const failures: string[] = [];
  if (expect.status && outcome.status !== expect.status) failures.push(`ended ${outcome.status}, expected ${expect.status}`);
  for (const name of expect.mustCall ?? []) if (!called.includes(name)) failures.push(`never called ${name}`);
  for (const name of expect.mustNotCall ?? []) if (called.includes(name)) failures.push(`called ${name}`);
  if (expect.maxSteps && outcome.trace.length > expect.maxSteps) failures.push(`took ${outcome.trace.length} steps, expected at most ${expect.maxSteps}`);
  if (expect.answerMatches && !expect.answerMatches.test(outcome.answer ?? "")) failures.push(`answer doesn't match ${expect.answerMatches}`);
  return failures;
}
```

The tests use scripted models, so every stop reason can be produced exactly:

```ts
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
```

Look at the address test before moving on: the keyword router sends "change my delivery address" down the wrong branch because "address" contains "add", the same flaw the [[ai-ml/03-ai-engineer/12-evals/index|evals]] lesson found in an Italian ticket. In this workflow it does no harm, because every branch except billing ends with a person. Choose routes so that a wrong turn is cheap.

### Against a real model

```ts
// live.ts — the agent and the workflow on the same questions, with a local model.
// Not run by the lab runner. Needs Ollama; about 3 model calls per question for the agent, 1 for the workflow.
//   node live.ts               # qwen3.5:4b
import { openAITools } from "../../../07-tools-and-mcp/labs/typescript/openai-tools.ts";
import { loadOrders, supportTools } from "../../../07-tools-and-mcp/labs/typescript/support-tools.ts";
import { runAgent } from "./agent.ts";
import { refundStatus } from "./workflow.ts";

const name = process.argv[2] ?? "qwen3.5:4b";
const base = "http://127.0.0.1:11434/v1";
const agentModel = openAITools({ baseUrl: base, model: name, extraBody: { reasoning_effort: "none", temperature: 0 } });
const write = async (prompt: string) => {
  const res = await fetch(`${base}/chat/completions`, {
    method: "POST",
    body: JSON.stringify({ model: name, messages: [{ role: "user", content: prompt }], reasoning_effort: "none", temperature: 0 }),
  });
  return (await res.json()).choices[0].message.content.trim();
};
const system = "You are a support assistant. Use the tools to look orders up; never guess. Answer in one or two sentences.";

for (const question of ["Where is my refund for order A123?", "Where is my refund for D012?", "Has my refund come through?"]) {
  console.log(`Q: ${question}`);
  let started = performance.now();
  const outcome = await runAgent(agentModel, [{ role: "system", content: system }, { role: "user", content: question }], supportTools(loadOrders()));
  const calls = outcome.trace.flatMap((s) => s.calls.map((c) => `${c.name}${c.isError ? "!" : ""}`));
  console.log(`  agent:    ${outcome.status}, ${outcome.trace.length} model calls [${calls.join(", ")}], ${((performance.now() - started) / 1000).toFixed(1)} s`);
  console.log(`            ${outcome.answer ?? "(no answer)"}`);
  started = performance.now();
  const flow = await refundStatus(question, supportTools(loadOrders()), write);
  const said = flow.kind === "handoff" ? `handoff: ${flow.reason}` : flow.text;
  console.log(`  workflow: ${flow.kind}, ${((performance.now() - started) / 1000).toFixed(1)} s\n            ${said}\n`);
}
```

**Not measured yet.** Predict first. For A123, how many model calls does the agent make, and how much slower is it than the workflow? For D012, does the agent look up the order, and does its answer mention the injected note? For "Has my refund come through?", what does each one do without an order number? Then run it on a quiet laptop and record the output here.

**Lab:** the code is in [`ai-ml/03-ai-engineer/08-agents/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/typescript). It imports the tools lab and the evals lab. From the vault root, `python3 labs/run.py agents/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama: run it from the lab folder with `node live.ts`.

## Common pitfalls

1. **An agent where a workflow would do.** If you can draw the flowchart, write it in code.
2. **No limits.** Every agent loop needs a step limit and a budget, and it should stop early when it repeats itself.
3. **Judging by the final answer only.** A right answer from a wrong path is a failure waiting to happen. Score the trajectory.
4. **One run per task.** Agents vary between runs. Run each task several times, and count the tasks that pass every time.
5. **No trace.** Without a record of each step, you can't explain a bad run, let alone fix it.
6. **Unbounded history.** Long runs resend everything, every step. Compact or drop old results, and keep the start fixed for caching.
7. **Writing memories without checking them.** Anything written to long-term memory comes back in future prompts, including injected instructions.
8. **Several agents by default.** Each one multiplies cost, failure points and debugging. Start with one.

## Check your understanding

1. What's the difference between a workflow and an agent, in one sentence?
2. Give four reasons an agent might be the wrong architecture for a task.
3. In the lab, why can't D012's injected note affect the workflow's answer?
4. An eight-step run starts with 2,000 tokens of instructions and tools and adds 500 tokens a step. How many input tokens does it send in total, and why so many?
5. What does stuck detection catch that a step limit doesn't, and why is it worth having both?
6. An agent answers a refund-status question correctly, but its trace shows a declined `issue_refund` call. Did it pass?
7. When is a multi-agent design worth its cost?

<details>
<summary>Answers — after your attempt</summary>

1. In a workflow your code decides the steps; in an agent the model decides them, one at a time, from what it has found.
2. Any four of: the steps are known in advance; one well-prepared model call would do; mistakes are expensive and unchecked; there's no way to evaluate the results; the cost or latency budget is tight; it would read untrusted content while holding powerful tools.
3. The workflow only calls `get_refund`, which doesn't return the order's note, and its model has no tools. The note never reaches the model, and even if it did, the model couldn't call anything.
4. 30,000: each step resends the whole history, so step one sends 2,000, step two 2,500, and so on up to 5,500 at step eight. The opening context is paid for eight times.
5. It catches a run that repeats the same call without progress, and stops it as soon as that's clear, many steps before the limit. The step limit still catches runs that wander without repeating exactly.
6. No. A status question should never lead to a refund request; the person's refusal saved it, not the agent. Score the path, not only the answer.
7. When the task really can't fit one context or one set of permissions, such as many independent research threads, and is valuable enough to pay for several loops, more tokens and harder debugging.

</details>

## Practice — independent task

**This week's closed-book question, then a leash.**

1. **Closed-book:** without notes, write down when an agent is the wrong architecture, with a reason for each point. Then compare with §3.
2. **For your flagship:** list its tasks, and for each, say whether it needs a workflow, a single call or an agent, and why. Most should not be agents.
3. **Exercise 11** in [[ai-ml/03-ai-engineer/19-practice-exercises|practice exercises]]: an agent with two or three tools, a step limit and a trace. Add stuck detection and a token budget from the lab.
4. Write three agent eval tasks with expected trajectories (tools that must and mustn't be called, a step limit), one of them impossible. Run each three times.

**Done when:** your written answer covers at least four of the six reasons, your flagship's task list has a decision for each task, and your agent has stopped on its own at least once for each of `answered`, `step_limit` and `stuck`, with the trace to show it.

## Tradeoffs, limits and extensions

- **Plan first, then act.** Some agents write a plan, show it to a person, and only then start. It's slower, and easier to approve and audit.
- **Sandboxes.** Agents that run code or use a computer need an isolated environment with limited network and file access, not your machine ([[ai-ml/03-ai-engineer/10-safety-and-production/index|safety and production]]).
- **Context engineering.** Long-running agents depend on what's kept in context: clearing old tool results, summarising, and writing notes to files the agent can reread.
- **Hosted agents.** Model providers now run the loop and a sandbox for you. The controls in this lesson still apply; you configure them rather than write them.

## Before moving on

You can say when an agent is the wrong design and what to build instead, add the controls an agent's loop needs, score a trajectory, and explain memory and multi-agent tradeoffs.

**Recap.** In a workflow code decides the steps; in an agent the model does, at a cost in money, latency, predictability and safety. Prefer a single call or a workflow (chain, route, parallel calls, orchestrator and workers, evaluate and improve) whenever the steps are known, mistakes are costly, results can't be checked, budgets are tight or untrusted content meets powerful tools. When an agent is right, give its loop a step limit, a token budget, stuck detection, approval for side effects, and a trace with a stop reason. Evaluate the trajectory as well as the answer, over several runs. Short-term memory is the history, so compact it; long-term memory is your store, so write to it carefully. Start with one agent.

**Next.** Week 6: [[ai-ml/03-ai-engineer/10-safety-and-production/index|safety and production]] — prompt injection and personal data, which agents make both more likely and more costly.

## Related
- [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|Tools and MCP]] — the loop and the controls on each call
- [[ai-ml/03-ai-engineer/12-evals/index|Evals]] — golden sets and gates, which trajectory scoring extends
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|Cost, caching and latency]] — why long runs get expensive
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG and embeddings]] — the usual store for long-term memory
- [[ai-ml/03-ai-engineer/10-safety-and-production/index|Safety and production]] — injection, sandboxing, guardrails

## Seen in the wild
- [[projects/socioboom/interview/03-ai-and-agents|socioboom]] — agents doing real publishing work
- [[projects/my-applicant/learning/02-ai-sdk-and-byok|my-applicant]] — the AI SDK, BYOK, and pipeline design
- [[ai-ml/interview/01-ai-engineering|Interview: Q6–Q7]] — why agents are hard, and prompt injection

*Source: Part II of the AI-engineer track, deepened with the roadmap.sh AI-agents roadmap; the workflow patterns follow Anthropic's "Building effective agents" (December 2024).*
