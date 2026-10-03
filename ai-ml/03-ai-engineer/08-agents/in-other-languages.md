# Agents in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/08-agents/index|agents]], which builds the agent loop with its controls, the same refund question as a fixed workflow, and a trajectory scorer in TypeScript. This page builds them in Python, Go, Java, Rust and C#. Each lab imports **that language's tools lab** (the order store, the tools and their checks) and **evals lab** (the keyword router), so there is one set of rules per language, and every lab produces the same stop reasons, traces and workflow results. The one part that really changes between languages is how the agent runs read-only tool calls **at the same time**, and that is most of this page.

## Before you start

You can already:

- Explain workflows versus agents, the loop's controls and trajectory scoring → [[ai-ml/03-ai-engineer/08-agents/index|the main lesson]].
- Read the tools lab in your language → [[ai-ml/03-ai-engineer/07-tools-and-mcp/in-other-languages|tools and MCP in other languages]].

After this lesson you will be able to:

1. Run independent tool calls concurrently in your language, and keep their results in the order they were asked for.
2. Say what your language does to stop two calls corrupting shared state.
3. Name your ecosystem's agent frameworks, and what they would replace in the lab.

## The kid version

A cook with three jobs — fetch the milk, fetch the eggs, then pay at the till — sends two helpers for the milk and the eggs at the same time, and only goes to the till once both are back. Whoever comes back first, the shopping goes on the counter in the order it was on the list. Five kitchens do this in five ways: one shouts "go!" to both helpers, one gives each a walkie-talkie, one hires a temporary helper for each job. The shopping ends up the same.

**Where the analogy stops working.** Two helpers can't spill each other's milk. Two threads writing to the same list at once can corrupt it, and each language has its own way of stopping that.

## 1. The tools, by ecosystem

| Language | Running reads at the same time | What keeps shared state safe | Agent frameworks |
|---|---|---|---|
| TypeScript | `Promise.all` | one thread: nothing runs in between `await`s | Vercel AI SDK agents, LangGraph.js, OpenAI Agents SDK |
| Python | **`asyncio.gather`** (or `TaskGroup`) | one event-loop thread, like TypeScript | LangGraph, OpenAI Agents SDK, PydanticAI, Claude Agent SDK |
| Go | **goroutines** with `sync.WaitGroup` (or `errgroup`) | each goroutine writes only its own slot; a `Mutex` for anything shared | `adk-go`, Genkit for Go |
| Java | **virtual threads** | `Collections.synchronizedList`, concurrent maps | LangChain4j, Spring AI, Embabel |
| Rust | **scoped threads** (`std::thread::scope`), or tokio's `join_all` | the compiler: data shared between threads must be `Sync` | `rig` |
| C# | **`Task.WhenAll`** | `ConcurrentDictionary`, `lock` | Microsoft Agent Framework, Semantic Kernel |
| C, C++ | — | — | — |

The frameworks run the same loop as the lab: call the model, run the tools it asks for, append the results, repeat until it answers or a limit stops it. The lab writes the loop by hand so you can see each control. When you adopt a framework, look for the same controls by name: a step or turn limit, a token or cost budget, approval for tools with side effects, and a trace.

There's no C or C++ section, for the same reason as in the other AI-engineering companions.

## 2. The same results, in every language

| Check | Expected in every language |
|---|---|
| the A123 question | answered in 2 steps; step 1 called `get_order` and `get_refund`; the trajectory scorer finds nothing wrong |
| two reads (30 ms and 10 ms) and a write | both reads start together, the 10 ms one ends first, the write starts only after both; results come back as 1, 2, 3 |
| a model that wanders | stopped by the step limit after 3 steps |
| the same call again and again | stuck after 3 steps, with a limit of 20 |
| a token budget of 50,000 at 25,500 a step | stopped after 2 steps |
| a status question answered with a refund | `never called get_refund`, `called issue_refund`, and the answer doesn't match |
| the workflow | one model call for A123; "ask" without an order number; the address question handed off as *feature*; D012's note never in the prompt |

Three things differ in detail, all for reasons from earlier companions:

- **Status names** print as `step_limit` in TypeScript, Python, Go and Java, and as `StepLimit` in Rust and C#, which use enums. An enum means a typo in a status is a compile error rather than a silent mismatch.
- **The refund in the workflow's prompt** comes out with its keys sorted in Rust, because `serde_json::Value` sorts them, so the prompt's bytes differ from the other languages'.
- **The regular expression in the scorer's message** is written `(?i)no refund` in the five languages here and `/no refund/i` in TypeScript.

## Terms used in this lesson

1. **Concurrency**: This means several tasks in progress at the same time, such as two tool calls waiting on the network together. **Parallelism** means they're actually running at the same instant, on different processor cores.
2. **Event loop**: This is the single thread that Python's `asyncio` and JavaScript run on. Tasks take turns at each `await`, so they never run at the same instant.
3. **Data race**: This is two threads accessing the same memory at the same time, at least one of them writing, with nothing ordering them. The result can be corrupted data.
4. **Virtual thread**: In Java, this is a thread managed by the JVM rather than the operating system, cheap enough to start one per task.
5. **Scoped thread**: In Rust, this is a thread guaranteed to finish before a given block of code ends, so it may borrow data from that block safely.

## 3. Python

`asyncio.gather` starts all the reads and waits for them together, on the one event-loop thread, so the tools never run at the same instant and can't race each other. They only take turns while waiting. That suits tools that wait on networks, which is what model tools usually do. A tool that does heavy computation would block every other one; that needs a thread or process pool. `asyncio.TaskGroup` is the stricter alternative: if one task fails, it cancels the others. The lab's `execute` never raises, so `gather` is enough.

```python
"""The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
Imports the tools lab (the store, the tools and `execute`) and the evals lab (the keyword router)."""
import asyncio
import json
import re
import sys
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

LABS = Path(__file__).parents[3]
sys.path[:0] = [str(LABS / "07-tools-and-mcp" / "labs" / "python"), str(LABS / "12-evals" / "labs" / "python")]
from evals import keywords  # noqa: E402
from tools import Tool, ToolCall, execute  # noqa: E402

# One model turn: text, the calls it asks for, and the tokens it used.
Model = Callable[[list[dict], list[dict]], Awaitable[tuple[str, list[ToolCall], int]]]


@dataclass
class Limits:
    max_steps: int = 8
    max_tokens: int = 50_000
    max_repeats: int = 2


@dataclass
class Step:
    step: int
    calls: list[tuple[str, str, bool]] = field(default_factory=list)  # name, arguments, is_error
    tokens: int = 0


@dataclass
class Outcome:
    status: str  # answered, step_limit, token_limit or stuck
    answer: str | None
    trace: list[Step]
    messages: list[dict]


async def run_agent(model: Model, messages: list[dict], tools: list[Tool], limits: Limits = Limits(),
                    approve=lambda name, args: False) -> Outcome:
    history, trace, seen, tokens = list(messages), [], {}, 0
    side_effects = {t.name for t in tools if t.side_effects}
    for step in range(1, limits.max_steps + 1):
        text, calls, used = await model(history, [t.spec() for t in tools])
        tokens += used
        history.append({"role": "assistant", "content": text, "tool_calls": calls})
        record = Step(step, tokens=used)
        trace.append(record)
        if not calls:
            return Outcome("answered", text, trace, history)

        for call in calls:  # the same call, again and again, is going round in circles
            key = f"{call.name} {call.arguments}"
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > limits.max_repeats:
                return Outcome("stuck", None, trace, history)

        # Read-only calls at the same time; side effects alone, in order, after them.
        reads = [c for c in calls if c.name not in side_effects]
        results = dict(zip([c.id for c in reads], await asyncio.gather(*(execute(c, tools, approve) for c in reads))))
        for c in calls:
            if c.name in side_effects:
                results[c.id] = await execute(c, tools, approve)

        for call in calls:  # results in the order of the calls, whatever order they finished in
            r = results[call.id]
            history.append({"role": "tool", "tool_call_id": call.id, "content": f"ERROR: {r.content}" if r.is_error else r.content})
            record.calls.append((call.name, call.arguments, r.is_error))
        if tokens > limits.max_tokens:
            return Outcome("token_limit", None, trace, history)
    return Outcome("step_limit", None, trace, history)


async def refund_status(question: str, tools: list[Tool], write: Callable[[str], Awaitable[str]]) -> dict:
    """The same question as fixed steps: route, extract, look up, then one model call with no tools."""
    if (label := keywords(question)) != "billing":
        return {"kind": "handoff", "reason": f"classified as {label}"}
    if not (match := re.search(r"\b([A-Za-z])(\d{3})\b", question)):
        return {"kind": "ask", "text": "Could you tell me your order number? It looks like A123."}
    order_id = match[1].upper() + match[2]
    refund = await execute(ToolCall("w1", "get_refund", json.dumps({"order_id": order_id})), tools, lambda n, a: False)
    if refund.is_error:
        return {"kind": "ask", "text": f"I couldn't find order {order_id}. Could you check the number?"}
    text = await write("Write a one-sentence reply to a customer about their refund, using only these facts.\n"
                       f"Order: {order_id}\nRefund: {refund.content}\nTheir question: {question}")
    return {"kind": "answer", "text": text, "model_calls": 1, "tool_calls": 1}


def score_trajectory(outcome: Outcome, status: str | None = None, must_call: tuple = (), must_not_call: tuple = (),
                     max_steps: int | None = None, answer_matches: str | None = None) -> list[str]:
    called = [name for step in outcome.trace for name, _, _ in step.calls]
    failures = []
    if status and outcome.status != status:
        failures.append(f"ended {outcome.status}, expected {status}")
    failures += [f"never called {n}" for n in must_call if n not in called]
    failures += [f"called {n}" for n in must_not_call if n in called]
    if max_steps and len(outcome.trace) > max_steps:
        failures.append(f"took {len(outcome.trace)} steps, expected at most {max_steps}")
    if answer_matches and not re.search(answer_matches, outcome.answer or ""):
        failures.append(f"answer doesn't match {answer_matches}")
    return failures
```

```python
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
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/python). `python3 labs/run.py agents/python`.

## 4. Go

Each read runs in its own goroutine, started with `sync.WaitGroup.Go` (new in Go 1.25). The goroutines really do run at the same time, on several cores, so shared state matters. The lab sidesteps it: each goroutine writes only its own slot of a results slice made in advance, and slots don't overlap, so no lock is needed. The test's tools append to one shared log, so that log has a `Mutex`. The parallel test runs inside `testing/synctest`, so the 30 ms and 10 ms tools finish in a fixed order on a fake clock, and the test never depends on real timing. `errgroup` from `golang.org/x/sync` is the usual alternative when goroutines can fail and the rest should stop.

```go
// Package agents: the agent loop with its controls, the same question as a workflow, and a trajectory
// scorer. Imports the tools lab (the store, the tools and Execute) and the evals lab (the keyword router).
package agents

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"sync"

	"evals"
	"tools"
)

type Limits struct{ MaxSteps, MaxTokens, MaxRepeats int }

var DefaultLimits = Limits{MaxSteps: 8, MaxTokens: 50_000, MaxRepeats: 2}

type StepCall struct {
	Name, Arguments string
	IsError         bool
}
type Step struct {
	Step, Tokens int
	Calls        []StepCall
}
type Outcome struct {
	Status   string // answered, step_limit, token_limit or stuck
	Answer   string
	Trace    []Step
	Messages []tools.Message
}

// Model returns one turn: text, the calls it asks for, and the tokens it used.
type Model func(ctx context.Context, history []tools.Message) (text string, calls []tools.Call, tokens int, err error)

func RunAgent(ctx context.Context, model Model, history []tools.Message, ts []tools.Tool, limits Limits, approve tools.Approve) (Outcome, error) {
	var trace []Step
	seen := map[string]int{}
	total := 0
	end := func(status, answer string) (Outcome, error) { return Outcome{status, answer, trace, history}, nil }
	sideEffects := map[string]bool{}
	for _, t := range ts {
		sideEffects[t.Name] = t.SideEffects
	}
	for step := 1; step <= limits.MaxSteps; step++ {
		text, calls, used, err := model(ctx, history)
		if err != nil {
			return Outcome{}, err
		}
		total += used
		history = append(history, tools.Message{Role: "assistant", Content: text, Calls: calls})
		trace = append(trace, Step{Step: step, Tokens: used})
		if len(calls) == 0 {
			return end("answered", text)
		}
		for _, c := range calls { // the same call, again and again, is going round in circles
			key := c.Name + " " + c.Arguments
			if seen[key]++; seen[key] > limits.MaxRepeats {
				return end("stuck", "")
			}
		}

		// Read-only calls run in their own goroutines; side effects run alone, in order, after them.
		results := make([]tools.Result, len(calls))
		var wg sync.WaitGroup
		for i, c := range calls {
			if !sideEffects[c.Name] {
				wg.Go(func() { results[i] = tools.Execute(ctx, c, ts, approve) }) // each writes only its own slot
			}
		}
		wg.Wait()
		for i, c := range calls {
			if sideEffects[c.Name] {
				results[i] = tools.Execute(ctx, c, ts, approve)
			}
		}

		for i, c := range calls { // results in the order of the calls, whatever order they finished in
			content := results[i].Content
			if results[i].IsError {
				content = "ERROR: " + content
			}
			history = append(history, tools.Message{Role: "tool", ToolCallID: c.ID, Content: content})
			trace[len(trace)-1].Calls = append(trace[len(trace)-1].Calls, StepCall{c.Name, c.Arguments, results[i].IsError})
		}
		if total > limits.MaxTokens {
			return end("token_limit", "")
		}
	}
	return end("step_limit", "")
}

type WorkflowResult struct {
	Kind, Text, Reason string // Kind: answer, ask or handoff
	ModelCalls         int
}

var orderID = regexp.MustCompile(`\b([A-Za-z])(\d{3})\b`)

// RefundStatus answers the same question with fixed steps: route, extract, look up, then one model
// call with no tools.
func RefundStatus(ctx context.Context, question string, ts []tools.Tool, write func(prompt string) (string, error)) (WorkflowResult, error) {
	if label, _ := evals.Keywords(question); label != "billing" {
		return WorkflowResult{Kind: "handoff", Reason: "classified as " + label}, nil
	}
	m := orderID.FindStringSubmatch(question)
	if m == nil {
		return WorkflowResult{Kind: "ask", Text: "Could you tell me your order number? It looks like A123."}, nil
	}
	id := strings.ToUpper(m[1]) + m[2]
	args, _ := json.Marshal(map[string]string{"order_id": id})
	refund := tools.Execute(ctx, tools.Call{ID: "w1", Name: "get_refund", Arguments: string(args)}, ts, func(string, json.RawMessage) bool { return false })
	if refund.IsError {
		return WorkflowResult{Kind: "ask", Text: fmt.Sprintf("I couldn't find order %s. Could you check the number?", id)}, nil
	}
	text, err := write(fmt.Sprintf("Write a one-sentence reply to a customer about their refund, using only these facts.\n"+
		"Order: %s\nRefund: %s\nTheir question: %s", id, refund.Content, question))
	return WorkflowResult{Kind: "answer", Text: text, ModelCalls: 1}, err
}

type Expect struct {
	Status            string
	MustCall, MustNot []string
	MaxSteps          int
	AnswerMatches     *regexp.Regexp
}

func ScoreTrajectory(o Outcome, e Expect) []string {
	var called, failures []string
	for _, s := range o.Trace {
		for _, c := range s.Calls {
			called = append(called, c.Name)
		}
	}
	if e.Status != "" && o.Status != e.Status {
		failures = append(failures, fmt.Sprintf("ended %s, expected %s", o.Status, e.Status))
	}
	for _, n := range e.MustCall {
		if !slices.Contains(called, n) {
			failures = append(failures, "never called "+n)
		}
	}
	for _, n := range e.MustNot {
		if slices.Contains(called, n) {
			failures = append(failures, "called "+n)
		}
	}
	if e.MaxSteps > 0 && len(o.Trace) > e.MaxSteps {
		failures = append(failures, fmt.Sprintf("took %d steps, expected at most %d", len(o.Trace), e.MaxSteps))
	}
	if e.AnswerMatches != nil && !e.AnswerMatches.MatchString(o.Answer) {
		failures = append(failures, "answer doesn't match "+e.AnswerMatches.String())
	}
	return failures
}
```

```go
package agents

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"sync"
	"testing"
	"testing/synctest"
	"time"

	"github.com/google/jsonschema-go/jsonschema"

	"tools"
)

func load(t *testing.T) []tools.Tool {
	orders, err := tools.LoadOrders("../../../07-tools-and-mcp/labs/shared/orders.json")
	if err != nil {
		t.Fatal(err)
	}
	return tools.SupportTools(orders)
}

func call(name, args, id string) tools.Call { return tools.Call{ID: id, Name: name, Arguments: args} }
func no(string, json.RawMessage) bool       { return false }

type turn struct {
	text   string
	calls  []tools.Call
	tokens int
}

func scripted(turns ...turn) Model {
	return func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		t := turns[0]
		turns = turns[1:]
		return t.text, t.calls, t.tokens, nil
	}
}

var ask = []tools.Message{{Role: "user", Content: "Where is my refund for A123?"}}

func names(o Outcome) [][]string {
	var out [][]string
	for _, s := range o.Trace {
		step := []string{}
		for _, c := range s.Calls {
			step = append(step, c.Name)
		}
		out = append(out, step)
	}
	return out
}

func TestATwoStepAnswerWithATrace(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("get_order", `{"order_id":"A123"}`, "c1"), call("get_refund", `{"order_id":"A123"}`, "c2")}, 0},
		turn{"Your refund of 49.99 is being processed.", nil, 0})
	o, _ := RunAgent(t.Context(), model, ask, load(t), DefaultLimits, no)
	if o.Status != "answered" || fmt.Sprint(names(o)) != "[[get_order get_refund] []]" {
		t.Fatal(o.Status, names(o))
	}
	if f := ScoreTrajectory(o, Expect{Status: "answered", MustCall: []string{"get_refund"}, MustNot: []string{"issue_refund"}, MaxSteps: 3}); len(f) > 0 {
		t.Error(f)
	}
}

func TestReadsRunTogetherAndASideEffectWaits(t *testing.T) {
	synctest.Test(t, func(t *testing.T) { // a fake clock: the 30 ms and 10 ms waits finish in a fixed order, instantly
		var mu sync.Mutex
		var log []string
		slow := func(name string, sideEffects bool, d time.Duration) tools.Tool {
			return tools.Tool{Name: name, Schema: &jsonschema.Schema{Type: "object"}, SideEffects: sideEffects,
				Run: func(context.Context, json.RawMessage) (any, error) {
					mu.Lock()
					log = append(log, "start "+name)
					mu.Unlock()
					time.Sleep(d)
					mu.Lock()
					log = append(log, "end "+name)
					mu.Unlock()
					return name, nil
				}}
		}
		ts := []tools.Tool{slow("read_a", false, 30*time.Millisecond), slow("read_b", false, 10*time.Millisecond), slow("write_c", true, time.Millisecond)}
		model := scripted(turn{"", []tools.Call{call("write_c", `{}`, "1"), call("read_a", `{}`, "2"), call("read_b", `{}`, "3")}, 0}, turn{"done", nil, 0})
		o, _ := RunAgent(t.Context(), model, nil, ts, DefaultLimits, func(string, json.RawMessage) bool { return true })
		ends := slices.DeleteFunc(slices.Clone(log), func(s string) bool { return strings.HasPrefix(s, "start") })
		if !slices.Equal(ends, []string{"end read_b", "end read_a", "end write_c"}) || log[len(log)-2] != "start write_c" {
			t.Error(log) // the two reads start together (in either order), the write starts after both end
		}
		var ids []string
		for _, m := range o.Messages {
			if m.Role == "tool" {
				ids = append(ids, m.ToolCallID)
			}
		}
		if !slices.Equal(ids, []string{"1", "2", "3"}) {
			t.Error(ids)
		}
	})
}

func TestAStepLimitStopsAWanderingAgent(t *testing.T) {
	n := 100
	wandering := func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		n++
		return "", []tools.Call{call("get_order", fmt.Sprintf(`{"order_id":"A%d"}`, n), fmt.Sprint(n))}, 0, nil
	}
	o, _ := RunAgent(t.Context(), wandering, ask, load(t), Limits{MaxSteps: 3, MaxTokens: 1e9, MaxRepeats: 5}, no)
	if o.Status != "step_limit" || len(o.Trace) != 3 || !slices.Equal(ScoreTrajectory(o, Expect{Status: "answered"}), []string{"ended step_limit, expected answered"}) {
		t.Error(o.Status, len(o.Trace))
	}
}

func TestTheSameCallAgainAndAgainIsStuck(t *testing.T) {
	repeating := func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		return "", []tools.Call{call("get_refund", `{"order_id":"Z999"}`, "x")}, 0, nil
	}
	o, _ := RunAgent(t.Context(), repeating, ask, load(t), Limits{MaxSteps: 20, MaxTokens: 1e9, MaxRepeats: 2}, no)
	if o.Status != "stuck" || len(o.Trace) != 3 {
		t.Error(o.Status, len(o.Trace))
	}
}

func TestATokenBudget(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("get_order", `{"order_id":"A123"}`, "c1")}, 25_500},
		turn{"", []tools.Call{call("get_order", `{"order_id":"B456"}`, "c2")}, 25_500}, turn{"never reached", nil, 25_500})
	o, _ := RunAgent(t.Context(), model, ask, load(t), Limits{MaxSteps: 10, MaxTokens: 50_000, MaxRepeats: 2}, no)
	if o.Status != "token_limit" || len(o.Trace) != 2 || o.Trace[1].Tokens != 25_500 {
		t.Error(o.Status, o.Trace)
	}
}

func TestTheScorerNamesEachBrokenExpectation(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("issue_refund", `{"order_id":"B456","amount":120}`, "c1")}, 0}, turn{"I've asked for a refund.", nil, 0})
	o, _ := RunAgent(t.Context(), model, ask, load(t), DefaultLimits, no)
	got := ScoreTrajectory(o, Expect{MustCall: []string{"get_refund"}, MustNot: []string{"issue_refund"}, AnswerMatches: regexp.MustCompile(`(?i)no refund`)})
	if !slices.Equal(got, []string{"never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund"}) {
		t.Error(got)
	}
}

func TestTheWorkflow(t *testing.T) {
	ts, ctx := load(t), t.Context()
	var prompts []string
	write := func(p string) (string, error) {
		prompts = append(prompts, p)
		return "Your refund of 49.99 for A123 is being processed.", nil
	}
	r, _ := RefundStatus(ctx, "Where is my refund for order a123?", ts, write)
	if r.Kind != "answer" || r.ModelCalls != 1 || !strings.Contains(prompts[0], `Refund: {"status":"processing","amount":49.99,"requested":"2026-09-28"}`) {
		t.Fatal(r, prompts)
	}
	if r, _ := RefundStatus(ctx, "Has my refund come through?", ts, write); r.Kind != "ask" {
		t.Error(r)
	}
	// "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
	if r, _ := RefundStatus(ctx, "Can you change my delivery address?", ts, write); r.Kind != "handoff" || r.Reason != "classified as feature" {
		t.Error(r)
	}
	RefundStatus(ctx, "Where is my refund for D012?", ts, write)
	if strings.Contains(prompts[len(prompts)-1], "IGNORE") || len(prompts) != 2 {
		t.Error(prompts)
	}
}
```

`go.mod` brings in the tools and evals labs with `replace` directives.

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/go). `python3 labs/run.py agents/go`.

## 5. Java

Java runs each read on its own **virtual thread**. A virtual thread blocked on a slow tool costs almost nothing, so the tools can be plain blocking code, and an executor per step is cheap. The executor is created in a `try`-with-resources block, whose close waits for every task to finish, so no read can outlive its step. Each step's results go into a map the loop owns; the test's shared log uses `Collections.synchronizedList` because several threads append to it. `StructuredTaskScope` expresses "run these, wait for all, cancel the rest on failure" directly, but it is still a preview feature, in Java 25 as in Java 21, which this lab targets.

```java
package agents;

import evals.Evals;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.BiPredicate;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import support.Tools;
import support.Tools.Message;
import support.Tools.Tool;
import support.Tools.ToolCall;
import support.Tools.ToolResult;
import tools.jackson.databind.JsonNode;

/** The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
 *  Imports the tools lab (support.Tools) and the evals lab (Evals.keywords). */
public final class Agent {
    private Agent() {}

    public record Limits(int maxSteps, int maxTokens, int maxRepeats) {
        public static final Limits DEFAULT = new Limits(8, 50_000, 2);
    }

    public record StepCall(String name, String arguments, boolean isError) {}

    public record Step(int step, int tokens, List<StepCall> calls) {}

    /** status: answered, step_limit, token_limit or stuck. */
    public record Outcome(String status, String answer, List<Step> trace, List<Message> messages) {}

    /** One model turn: text, the calls it asks for, and the tokens it used. */
    public record Turn(String content, List<ToolCall> calls, int tokens) {}

    public interface Model {
        Turn respond(List<Message> history);
    }

    public static Outcome runAgent(Model model, List<Message> messages, List<Tool> tools, Limits limits,
                                   BiPredicate<String, JsonNode> approve) throws Exception {
        var history = new ArrayList<>(messages);
        var trace = new ArrayList<Step>();
        var seen = new HashMap<String, Integer>();
        int total = 0;
        Set<String> sideEffects = tools.stream().filter(Tool::sideEffects).map(Tool::name).collect(Collectors.toSet());
        for (int step = 1; step <= limits.maxSteps(); step++) {
            Turn turn = model.respond(List.copyOf(history));
            total += turn.tokens();
            history.add(new Message("assistant", turn.content(), null, turn.calls()));
            var record = new Step(step, turn.tokens(), new ArrayList<>());
            trace.add(record);
            if (turn.calls().isEmpty()) return new Outcome("answered", turn.content(), trace, history);

            for (ToolCall c : turn.calls()) { // the same call, again and again, is going round in circles
                if (seen.merge(c.name() + " " + c.arguments(), 1, Integer::sum) > limits.maxRepeats()) {
                    return new Outcome("stuck", null, trace, history);
                }
            }

            // Read-only calls each get a virtual thread; side effects run alone, in order, after them.
            Map<String, ToolResult> results = new HashMap<>();
            try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                var reads = new HashMap<String, Future<ToolResult>>();
                for (ToolCall c : turn.calls()) {
                    if (!sideEffects.contains(c.name())) reads.put(c.id(), executor.submit(() -> Tools.execute(c, tools, approve)));
                }
                for (var e : reads.entrySet()) results.put(e.getKey(), e.getValue().get());
            }
            for (ToolCall c : turn.calls()) {
                if (sideEffects.contains(c.name())) results.put(c.id(), Tools.execute(c, tools, approve));
            }

            for (ToolCall c : turn.calls()) { // results in the order of the calls, whatever order they finished in
                ToolResult r = results.get(c.id());
                history.add(new Message("tool", r.isError() ? "ERROR: " + r.content() : r.content(), c.id(), List.of()));
                record.calls().add(new StepCall(c.name(), c.arguments(), r.isError()));
            }
            if (total > limits.maxTokens()) return new Outcome("token_limit", null, trace, history);
        }
        return new Outcome("step_limit", null, trace, history);
    }

    /** kind: answer, ask or handoff. */
    public record WorkflowResult(String kind, String text, int modelCalls) {}

    private static final Pattern ORDER_ID = Pattern.compile("\\b([A-Za-z])(\\d{3})\\b");

    /** The same question as fixed steps: route, extract, look up, then one model call with no tools. */
    public static WorkflowResult refundStatus(String question, List<Tool> tools, java.util.function.UnaryOperator<String> write) {
        String label = Evals.keywords(question);
        if (!label.equals("billing")) return new WorkflowResult("handoff", "classified as " + label, 0);
        var m = ORDER_ID.matcher(question);
        if (!m.find()) return new WorkflowResult("ask", "Could you tell me your order number? It looks like A123.", 0);
        String id = m.group(1).toUpperCase() + m.group(2);
        ToolResult refund = Tools.execute(new ToolCall("w1", "get_refund", "{\"order_id\":\"" + id + "\"}"), tools, (n, a) -> false);
        if (refund.isError()) return new WorkflowResult("ask", "I couldn't find order " + id + ". Could you check the number?", 0);
        String text = write.apply("Write a one-sentence reply to a customer about their refund, using only these facts.\n"
                + "Order: " + id + "\nRefund: " + refund.content() + "\nTheir question: " + question);
        return new WorkflowResult("answer", text, 1);
    }

    public record Expect(String status, List<String> mustCall, List<String> mustNotCall, int maxSteps, Pattern answerMatches) {}

    public static List<String> scoreTrajectory(Outcome o, Expect e) {
        var called = o.trace().stream().flatMap(s -> s.calls().stream().map(StepCall::name)).toList();
        var failures = new ArrayList<String>();
        if (e.status() != null && !o.status().equals(e.status())) failures.add("ended " + o.status() + ", expected " + e.status());
        for (String n : e.mustCall()) if (!called.contains(n)) failures.add("never called " + n);
        for (String n : e.mustNotCall()) if (called.contains(n)) failures.add("called " + n);
        if (e.maxSteps() > 0 && o.trace().size() > e.maxSteps()) failures.add("took " + o.trace().size() + " steps, expected at most " + e.maxSteps());
        if (e.answerMatches() != null && !e.answerMatches().matcher(o.answer() == null ? "" : o.answer()).find()) {
            failures.add("answer doesn't match " + e.answerMatches().pattern());
        }
        return failures;
    }
}
```

```java
package agents;

import agents.Agent.Expect;
import agents.Agent.Limits;
import agents.Agent.Outcome;
import agents.Agent.Turn;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;
import support.Tools;
import support.Tools.Message;
import support.Tools.Tool;
import support.Tools.ToolCall;

/** Checks, run with `java -ea`. The same scenarios and results as every other language. */
public final class AgentCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static List<Tool> load() throws Exception {
        return Tools.supportTools(Tools.loadOrders(Path.of("..", "..", "..", "07-tools-and-mcp", "labs", "shared", "orders.json")));
    }

    static ToolCall call(String name, String args, String id) {
        return new ToolCall(id, name, args);
    }

    static Agent.Model scripted(Turn... turns) {
        var queue = new ArrayDeque<>(List.of(turns));
        return history -> queue.removeFirst();
    }

    static List<List<String>> names(Outcome o) {
        return o.trace().stream().map(s -> s.calls().stream().map(Agent.StepCall::name).toList()).toList();
    }

    static final List<Message> ASK = List.of(new Message("user", "Where is my refund for A123?", null, List.of()));
    static final Expect NOTHING = new Expect(null, List.of(), List.of(), 0, null);

    public static void main(String[] args) throws Exception {
        // a two-step answer, with a trace
        var o = Agent.runAgent(scripted(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1"), call("get_refund", "{\"order_id\":\"A123\"}", "c2")), 0),
                new Turn("Your refund of 49.99 is being processed.", List.of(), 0)), ASK, load(), Limits.DEFAULT, (n, a) -> false);
        check(o.status().equals("answered") && names(o).equals(List.of(List.of("get_order", "get_refund"), List.of())), names(o));
        check(Agent.scoreTrajectory(o, new Expect("answered", List.of("get_refund"), List.of("issue_refund"), 3, null)).isEmpty(), "trajectory");

        // reads run together on virtual threads; a side effect waits
        var log = Collections.synchronizedList(new ArrayList<String>());
        java.util.function.BiFunction<String, Long, Tools.Run> slow = (name, ms) -> a -> {
            log.add("start " + name);
            try {
                Thread.sleep(ms);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            log.add("end " + name);
            return name;
        };
        var any = Tools.JSON.readTree("{\"type\":\"object\"}");
        var slowTools = List.of(new Tool("read_a", "", any, false, slow.apply("read_a", 30L)),
                new Tool("read_b", "", any, false, slow.apply("read_b", 10L)), new Tool("write_c", "", any, true, slow.apply("write_c", 1L)));
        var p = Agent.runAgent(scripted(new Turn("", List.of(call("write_c", "{}", "1"), call("read_a", "{}", "2"), call("read_b", "{}", "3")), 0),
                new Turn("done", List.of(), 0)), List.of(), slowTools, Limits.DEFAULT, (n, a) -> true);
        check(log.stream().filter(s -> s.startsWith("end")).toList().equals(List.of("end read_b", "end read_a", "end write_c"))
                && log.get(4).equals("start write_c"), log);
        check(p.messages().stream().filter(m -> m.role().equals("tool")).map(Message::toolCallId).toList().equals(List.of("1", "2", "3")), "order");

        // a step limit stops a wandering agent
        int[] n = {100};
        var wandering = Agent.runAgent(h -> new Turn("", List.of(call("get_order", "{\"order_id\":\"A" + ++n[0] + "\"}", "c" + n[0])), 0),
                ASK, load(), new Limits(3, 1_000_000_000, 5), (x, a) -> false);
        check(wandering.status().equals("step_limit") && wandering.trace().size() == 3, wandering.status());
        check(Agent.scoreTrajectory(wandering, new Expect("answered", List.of(), List.of(), 0, null)).equals(List.of("ended step_limit, expected answered")), "scored");

        // the same call again and again is stuck
        var stuck = Agent.runAgent(h -> new Turn("", List.of(call("get_refund", "{\"order_id\":\"Z999\"}", "x")), 0),
                ASK, load(), new Limits(20, 1_000_000_000, 2), (x, a) -> false);
        check(stuck.status().equals("stuck") && stuck.trace().size() == 3, stuck.status());

        // a token budget
        var budget = Agent.runAgent(scripted(new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1")), 25_500),
                new Turn("", List.of(call("get_order", "{\"order_id\":\"B456\"}", "c2")), 25_500), new Turn("never reached", List.of(), 25_500)),
                ASK, load(), new Limits(10, 50_000, 2), (x, a) -> false);
        check(budget.status().equals("token_limit") && budget.trace().stream().map(Agent.Step::tokens).toList().equals(List.of(25_500, 25_500)), budget);

        // the scorer names each broken expectation
        var refunded = Agent.runAgent(scripted(new Turn("", List.of(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1")), 0),
                new Turn("I've asked for a refund.", List.of(), 0)), ASK, load(), Limits.DEFAULT, (x, a) -> false);
        var failures = Agent.scoreTrajectory(refunded, new Expect(null, List.of("get_refund"), List.of("issue_refund"), 0, Pattern.compile("(?i)no refund")));
        check(failures.equals(List.of("never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund")), failures);

        // the workflow
        var tools = load();
        var prompts = new ArrayList<String>();
        java.util.function.UnaryOperator<String> write = prompt -> {
            prompts.add(prompt);
            return "Your refund of 49.99 for A123 is being processed.";
        };
        var answered = Agent.refundStatus("Where is my refund for order a123?", tools, write);
        check(answered.kind().equals("answer") && answered.modelCalls() == 1, answered);
        check(prompts.getFirst().contains("Refund: {\"status\":\"processing\",\"amount\":49.99,\"requested\":\"2026-09-28\"}"), prompts.getFirst());
        check(Agent.refundStatus("Has my refund come through?", tools, write).kind().equals("ask"), "ask");
        // "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
        check(Agent.refundStatus("Can you change my delivery address?", tools, write).text().equals("classified as feature"), "handoff");
        Agent.refundStatus("Where is my refund for D012?", tools, write);
        check(!prompts.getLast().contains("IGNORE") && prompts.size() == 2, prompts);

        System.out.println("all agent checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/java). `check.sh` compiles the tools lab's `Tools.java` (Jackson 3) and the evals lab's `Evals.java` (Jackson 2) alongside this lab; the two Jacksons use different package names, so both fit on one classpath. `python3 labs/run.py agents/java`.

## 6. Rust

Rust runs each read on a **scoped thread**. `std::thread::scope` guarantees every thread it starts is joined before the scope ends, so the threads may borrow `tools` and the calls directly, with no `Arc` and no cloning. The compiler then checks everything that crosses a thread boundary. That's why `run_agent` takes `approve` as `&(dyn Fn(..) -> bool + Sync)`: several threads may call it at once, and without `Sync` the code doesn't compile. A tool whose state couldn't be shared safely would be rejected the same way, before it ever ran. With async tools on tokio, `futures::future::join_all` plays the same part.

```rust
//! The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
//! Uses the tools lab (`support_tools`) and the evals lab (`evals::keywords`).
use regex::Regex;
use serde_json::{Value, json};
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;
use support_tools::{Message, Tool, ToolCall, ToolResult, execute};

pub struct Limits {
    pub max_steps: usize,
    pub max_tokens: u32,
    pub max_repeats: u32,
}

pub const DEFAULT_LIMITS: Limits = Limits {
    max_steps: 8,
    max_tokens: 50_000,
    max_repeats: 2,
};

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Status {
    Answered,
    StepLimit,
    TokenLimit,
    Stuck,
}

#[derive(Debug)]
pub struct Step {
    pub tokens: u32,
    pub calls: Vec<(String, String, bool)>, // name, arguments, is_error
}

#[derive(Debug)]
pub struct Outcome {
    pub status: Status,
    pub answer: Option<String>,
    pub trace: Vec<Step>,
    pub messages: Vec<Message>,
}

/// One model turn: text, the calls it asks for, and the tokens it used.
pub type Turn = (String, Vec<ToolCall>, u32);

/// `approve` must be `Sync`: read-only calls run on several threads at once, and each may need it.
pub fn run_agent(
    model: &mut dyn FnMut(&[Message]) -> Turn,
    messages: Vec<Message>,
    tools: &[Tool],
    limits: &Limits,
    approve: &(dyn Fn(&str, &Value) -> bool + Sync),
) -> Outcome {
    let (mut history, mut trace, mut seen, mut total) = (messages, Vec::new(), HashMap::new(), 0);
    let side_effects: HashSet<&str> = tools
        .iter()
        .filter(|t| t.side_effects)
        .map(|t| t.name)
        .collect();
    for _ in 0..limits.max_steps {
        let (text, calls, used) = model(&history);
        total += used;
        history.push(Message::Assistant {
            content: text.clone(),
            calls: calls.clone(),
        });
        trace.push(Step {
            tokens: used,
            calls: vec![],
        });
        if calls.is_empty() {
            return Outcome {
                status: Status::Answered,
                answer: Some(text),
                trace,
                messages: history,
            };
        }
        for call in &calls {
            // the same call, again and again, is going round in circles
            let count = seen
                .entry(format!("{} {}", call.name, call.arguments))
                .or_insert(0);
            *count += 1;
            if *count > limits.max_repeats {
                return Outcome {
                    status: Status::Stuck,
                    answer: None,
                    trace,
                    messages: history,
                };
            }
        }

        // Read-only calls on scoped threads, which may borrow `tools` because they're joined before the
        // scope ends; side effects alone, in order, after them.
        let mut results: HashMap<&str, ToolResult> = std::thread::scope(|scope| {
            let reads: Vec<_> = calls
                .iter()
                .filter(|c| !side_effects.contains(c.name.as_str()))
                .map(|c| {
                    (
                        c.id.as_str(),
                        scope.spawn(move || execute(c, tools, approve)),
                    )
                })
                .collect();
            reads
                .into_iter()
                .map(|(id, handle)| (id, handle.join().expect("a tool thread panicked")))
                .collect()
        });
        for c in calls
            .iter()
            .filter(|c| side_effects.contains(c.name.as_str()))
        {
            results.insert(c.id.as_str(), execute(c, tools, approve));
        }

        for call in &calls {
            // results in the order of the calls, whatever order they finished in
            let r = results
                .remove(call.id.as_str())
                .expect("every call has a result");
            let content = if r.is_error {
                format!("ERROR: {}", r.content)
            } else {
                r.content
            };
            history.push(Message::Tool {
                call_id: call.id.clone(),
                content,
            });
            trace.last_mut().unwrap().calls.push((
                call.name.clone(),
                call.arguments.clone(),
                r.is_error,
            ));
        }
        if total > limits.max_tokens {
            return Outcome {
                status: Status::TokenLimit,
                answer: None,
                trace,
                messages: history,
            };
        }
    }
    Outcome {
        status: Status::StepLimit,
        answer: None,
        trace,
        messages: history,
    }
}

#[derive(Debug, PartialEq)]
pub enum Workflow {
    Answer { text: String, model_calls: u32 },
    Ask(String),
    Handoff(String),
}

static ORDER_ID: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\b([A-Za-z])(\d{3})\b").unwrap());

/// The same question as fixed steps: route, extract, look up, then one model call with no tools.
pub fn refund_status(
    question: &str,
    tools: &[Tool],
    write: &mut dyn FnMut(&str) -> String,
) -> Workflow {
    let label = evals::keywords(question);
    if label != "billing" {
        return Workflow::Handoff(format!("classified as {label}"));
    }
    let Some(m) = ORDER_ID.captures(question) else {
        return Workflow::Ask("Could you tell me your order number? It looks like A123.".into());
    };
    let id = format!("{}{}", m[1].to_uppercase(), &m[2]);
    let args = json!({ "order_id": id }).to_string();
    let refund = execute(
        &ToolCall {
            id: "w1".into(),
            name: "get_refund".into(),
            arguments: args,
        },
        tools,
        &|_, _| false,
    );
    if refund.is_error {
        return Workflow::Ask(format!(
            "I couldn't find order {id}. Could you check the number?"
        ));
    }
    let text = write(&format!(
        "Write a one-sentence reply to a customer about their refund, using only these facts.\nOrder: {id}\nRefund: {}\nTheir question: {question}",
        refund.content
    ));
    Workflow::Answer {
        text,
        model_calls: 1,
    }
}

#[derive(Default)]
pub struct Expect<'a> {
    pub status: Option<Status>,
    pub must_call: &'a [&'a str],
    pub must_not_call: &'a [&'a str],
    pub max_steps: Option<usize>,
    pub answer_matches: Option<Regex>,
}

pub fn score_trajectory(o: &Outcome, e: &Expect) -> Vec<String> {
    let called: Vec<&str> = o
        .trace
        .iter()
        .flat_map(|s| s.calls.iter().map(|c| c.0.as_str()))
        .collect();
    let mut failures = vec![];
    if let Some(status) = e.status.filter(|s| *s != o.status) {
        failures.push(format!("ended {:?}, expected {status:?}", o.status));
    }
    failures.extend(
        e.must_call
            .iter()
            .filter(|n| !called.contains(n))
            .map(|n| format!("never called {n}")),
    );
    failures.extend(
        e.must_not_call
            .iter()
            .filter(|n| called.contains(n))
            .map(|n| format!("called {n}")),
    );
    if let Some(max) = e.max_steps.filter(|m| o.trace.len() > *m) {
        failures.push(format!(
            "took {} steps, expected at most {max}",
            o.trace.len()
        ));
    }
    if let Some(re) = e
        .answer_matches
        .as_ref()
        .filter(|re| !re.is_match(o.answer.as_deref().unwrap_or("")))
    {
        failures.push(format!("answer doesn't match {re}"));
    }
    failures
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;
    use std::time::Duration;
    use support_tools::{load_orders, support_tools};

    fn load() -> Vec<Tool> {
        support_tools(&load_orders(
            "../../../07-tools-and-mcp/labs/shared/orders.json",
        ))
    }
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
    fn scripted(turns: Vec<Turn>) -> impl FnMut(&[Message]) -> Turn {
        let mut turns = turns.into_iter();
        move |_| turns.next().expect("the script ran out")
    }
    fn ask() -> Vec<Message> {
        vec![Message::User("Where is my refund for A123?".into())]
    }
    fn names(o: &Outcome) -> Vec<Vec<&str>> {
        o.trace
            .iter()
            .map(|s| s.calls.iter().map(|c| c.0.as_str()).collect())
            .collect()
    }

    #[test]
    fn a_two_step_answer_with_a_trace() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![
                    call("get_order", r#"{"order_id":"A123"}"#, "c1"),
                    call("get_refund", r#"{"order_id":"A123"}"#, "c2"),
                ],
                0,
            ),
            ("Your refund of 49.99 is being processed.".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, ask(), &load(), &DEFAULT_LIMITS, &no);
        assert_eq!(
            (o.status, names(&o)),
            (
                Status::Answered,
                vec![vec!["get_order", "get_refund"], vec![]]
            )
        );
        let expect = Expect {
            status: Some(Status::Answered),
            must_call: &["get_refund"],
            must_not_call: &["issue_refund"],
            max_steps: Some(3),
            ..Default::default()
        };
        assert!(score_trajectory(&o, &expect).is_empty());
    }

    #[test]
    fn reads_run_together_and_a_side_effect_waits() {
        let log = std::sync::Arc::new(Mutex::new(vec![]));
        let slow = |name: &'static str, side_effects: bool, ms: u64| {
            let log = log.clone();
            Tool {
                name,
                description: "",
                schema: json!({ "type": "object" }),
                side_effects,
                run: Box::new(move |_| {
                    log.lock().unwrap().push(format!("start {name}"));
                    std::thread::sleep(Duration::from_millis(ms));
                    log.lock().unwrap().push(format!("end {name}"));
                    Ok(json!(name))
                }),
            }
        };
        let tools = [
            slow("read_a", false, 30),
            slow("read_b", false, 10),
            slow("write_c", true, 1),
        ];
        let mut model = scripted(vec![
            (
                String::new(),
                vec![
                    call("write_c", "{}", "1"),
                    call("read_a", "{}", "2"),
                    call("read_b", "{}", "3"),
                ],
                0,
            ),
            ("done".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, vec![], &tools, &DEFAULT_LIMITS, &|_, _| true);
        let log = log.lock().unwrap();
        let ends: Vec<_> = log.iter().filter(|s| s.starts_with("end")).collect();
        assert_eq!(ends, ["end read_b", "end read_a", "end write_c"]);
        assert_eq!(log[4], "start write_c");
        let ids: Vec<_> = o
            .messages
            .iter()
            .filter_map(|m| {
                if let Message::Tool { call_id, .. } = m {
                    Some(call_id.as_str())
                } else {
                    None
                }
            })
            .collect();
        assert_eq!(ids, ["1", "2", "3"]);
    }

    #[test]
    fn a_step_limit_stops_a_wandering_agent() {
        let mut n = 100;
        let mut wandering = |_: &[Message]| {
            n += 1;
            (
                String::new(),
                vec![call(
                    "get_order",
                    &format!(r#"{{"order_id":"A{n}"}}"#),
                    &n.to_string(),
                )],
                0,
            )
        };
        let o = run_agent(
            &mut wandering,
            ask(),
            &load(),
            &Limits {
                max_steps: 3,
                max_tokens: u32::MAX,
                max_repeats: 5,
            },
            &no,
        );
        assert_eq!((o.status, o.trace.len()), (Status::StepLimit, 3));
        let expect = Expect {
            status: Some(Status::Answered),
            ..Default::default()
        };
        assert_eq!(
            score_trajectory(&o, &expect),
            ["ended StepLimit, expected Answered"]
        );
    }

    #[test]
    fn the_same_call_again_and_again_is_stuck() {
        let mut repeating = |_: &[Message]| {
            (
                String::new(),
                vec![call("get_refund", r#"{"order_id":"Z999"}"#, "x")],
                0,
            )
        };
        let o = run_agent(
            &mut repeating,
            ask(),
            &load(),
            &Limits {
                max_steps: 20,
                max_tokens: u32::MAX,
                max_repeats: 2,
            },
            &no,
        );
        assert_eq!((o.status, o.trace.len()), (Status::Stuck, 3));
    }

    #[test]
    fn a_token_budget() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"A123"}"#, "c1")],
                25_500,
            ),
            (
                String::new(),
                vec![call("get_order", r#"{"order_id":"B456"}"#, "c2")],
                25_500,
            ),
            ("never reached".into(), vec![], 25_500),
        ]);
        let o = run_agent(
            &mut model,
            ask(),
            &load(),
            &Limits {
                max_steps: 10,
                max_tokens: 50_000,
                max_repeats: 2,
            },
            &no,
        );
        assert_eq!(
            (
                o.status,
                o.trace.iter().map(|s| s.tokens).collect::<Vec<_>>()
            ),
            (Status::TokenLimit, vec![25_500, 25_500])
        );
    }

    #[test]
    fn the_scorer_names_each_broken_expectation() {
        let mut model = scripted(vec![
            (
                String::new(),
                vec![call(
                    "issue_refund",
                    r#"{"order_id":"B456","amount":120}"#,
                    "c1",
                )],
                0,
            ),
            ("I've asked for a refund.".into(), vec![], 0),
        ]);
        let o = run_agent(&mut model, ask(), &load(), &DEFAULT_LIMITS, &no);
        let expect = Expect {
            must_call: &["get_refund"],
            must_not_call: &["issue_refund"],
            answer_matches: Some(Regex::new("(?i)no refund").unwrap()),
            ..Default::default()
        };
        assert_eq!(
            score_trajectory(&o, &expect),
            [
                "never called get_refund",
                "called issue_refund",
                "answer doesn't match (?i)no refund"
            ]
        );
    }

    #[test]
    fn the_workflow() {
        let tools = load();
        let mut prompts = vec![];
        let mut write = |p: &str| {
            prompts.push(p.to_string());
            "Your refund of 49.99 for A123 is being processed.".to_string()
        };
        assert_eq!(
            refund_status("Where is my refund for order a123?", &tools, &mut write),
            Workflow::Answer {
                text: "Your refund of 49.99 for A123 is being processed.".into(),
                model_calls: 1
            }
        );
        assert!(matches!(
            refund_status("Has my refund come through?", &tools, &mut write),
            Workflow::Ask(_)
        ));
        // "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
        assert_eq!(
            refund_status("Can you change my delivery address?", &tools, &mut write),
            Workflow::Handoff("classified as feature".into())
        );
        refund_status("Where is my refund for D012?", &tools, &mut write);
        assert!(prompts[0].contains(
            r#"Refund: {"amount":49.99,"requested":"2026-09-28","status":"processing"}"#
        )); // serde_json sorts keys
        assert!(!prompts[1].contains("IGNORE") && prompts.len() == 2);
    }
}
```

`Cargo.toml` depends on the tools and evals labs by path.

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/rust). `python3 labs/run.py agents/rust`.

## 7. C#

C# starts each read with `Task.Run` and waits with `Task.WhenAll`. Because the lab's tools are synchronous, `Task.Run` moves each one onto a thread-pool thread; tools doing asynchronous I/O would return their own tasks and need no `Task.Run`. The results go into a `ConcurrentDictionary`, which several threads can write to safely, and the test's shared log takes a `lock` on .NET 9's `Lock` type. `WorkflowResult` is a closed set of records (`Answer`, `Ask`, `Handoff`), so the tests compare whole results with `==`.

```csharp
// The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
// Links the tools lab's Tools.cs (the store, the tools and Execute) and the evals lab's Evals.cs (the keyword router).
using System.Collections.Concurrent;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

public sealed record Limits(int MaxSteps = 8, int MaxTokens = 50_000, int MaxRepeats = 2);
public sealed record StepCall(string Name, string Arguments, bool IsError);
public sealed record Step(int Number, int Tokens, List<StepCall> Calls);
public enum Status { Answered, StepLimit, TokenLimit, Stuck }
public sealed record Outcome(Status Status, string? Answer, List<Step> Trace, List<Message> Messages);

/// <summary>One model turn: text, the calls it asks for, and the tokens it used.</summary>
public sealed record AgentTurn(string Content, IReadOnlyList<ToolCall> Calls, int Tokens = 0);

public abstract record WorkflowResult
{
    public sealed record Answer(string Text, int ModelCalls) : WorkflowResult;
    public sealed record Ask(string Text) : WorkflowResult;
    public sealed record Handoff(string Reason) : WorkflowResult;
}

public sealed record Expect(Status? Status = null, string[]? MustCall = null, string[]? MustNotCall = null, int? MaxSteps = null, Regex? AnswerMatches = null);

public static partial class Agent
{
    public static async Task<Outcome> Run(Func<IReadOnlyList<Message>, AgentTurn> model, IEnumerable<Message> messages,
        IReadOnlyList<Tool> tools, Limits limits, Func<string, JsonObject, bool> approve)
    {
        var history = messages.ToList();
        var trace = new List<Step>();
        var seen = new Dictionary<string, int>();
        var total = 0;
        var sideEffects = tools.Where(t => t.SideEffects).Select(t => t.Name).ToHashSet();
        for (var step = 1; step <= limits.MaxSteps; step++)
        {
            var turn = model([.. history]);
            total += turn.Tokens;
            history.Add(new("assistant", turn.Content, Calls: turn.Calls));
            var record = new Step(step, turn.Tokens, []);
            trace.Add(record);
            if (turn.Calls.Count == 0) return new(Status.Answered, turn.Content, trace, history);

            foreach (var c in turn.Calls) // the same call, again and again, is going round in circles
            {
                var key = $"{c.Name} {c.Arguments}";
                seen[key] = seen.GetValueOrDefault(key) + 1;
                if (seen[key] > limits.MaxRepeats) return new(Status.Stuck, null, trace, history);
            }

            // Read-only calls on the thread pool at the same time; side effects alone, in order, after them.
            var results = new ConcurrentDictionary<string, ToolResult>();
            await Task.WhenAll(turn.Calls.Where(c => !sideEffects.Contains(c.Name))
                .Select(c => Task.Run(() => results[c.Id] = Tools.Execute(c, tools, approve))));
            foreach (var c in turn.Calls.Where(c => sideEffects.Contains(c.Name))) results[c.Id] = Tools.Execute(c, tools, approve);

            foreach (var c in turn.Calls) // results in the order of the calls, whatever order they finished in
            {
                var r = results[c.Id];
                history.Add(new("tool", r.IsError ? $"ERROR: {r.Content}" : r.Content, c.Id));
                record.Calls.Add(new(c.Name, c.Arguments, r.IsError));
            }
            if (total > limits.MaxTokens) return new(Status.TokenLimit, null, trace, history);
        }
        return new(Status.StepLimit, null, trace, history);
    }

    [GeneratedRegex(@"\b([A-Za-z])(\d{3})\b")] private static partial Regex OrderId();

    /// <summary>The same question as fixed steps: route, extract, look up, then one model call with no tools.</summary>
    public static WorkflowResult RefundStatus(string question, IReadOnlyList<Tool> tools, Func<string, string> write)
    {
        var label = Evals.Keywords(question);
        if (label != "billing") return new WorkflowResult.Handoff($"classified as {label}");
        var m = OrderId().Match(question);
        if (!m.Success) return new WorkflowResult.Ask("Could you tell me your order number? It looks like A123.");
        var id = m.Groups[1].Value.ToUpperInvariant() + m.Groups[2].Value;
        var refund = Tools.Execute(new("w1", "get_refund", new JsonObject { ["order_id"] = id }.ToJsonString()), tools, (_, _) => false);
        if (refund.IsError) return new WorkflowResult.Ask($"I couldn't find order {id}. Could you check the number?");
        var text = write("Write a one-sentence reply to a customer about their refund, using only these facts.\n" +
            $"Order: {id}\nRefund: {refund.Content}\nTheir question: {question}");
        return new WorkflowResult.Answer(text, 1);
    }

    public static List<string> ScoreTrajectory(Outcome o, Expect e)
    {
        var called = o.Trace.SelectMany(s => s.Calls.Select(c => c.Name)).ToList();
        var failures = new List<string>();
        if (e.Status is { } status && o.Status != status) failures.Add($"ended {o.Status}, expected {status}");
        failures.AddRange((e.MustCall ?? []).Where(n => !called.Contains(n)).Select(n => $"never called {n}"));
        failures.AddRange((e.MustNotCall ?? []).Where(called.Contains).Select(n => $"called {n}"));
        if (e.MaxSteps is { } max && o.Trace.Count > max) failures.Add($"took {o.Trace.Count} steps, expected at most {max}");
        if (e.AnswerMatches is { } re && !re.IsMatch(o.Answer ?? "")) failures.Add($"answer doesn't match {re}");
        return failures;
    }
}
```

```csharp
// Checks: the same scenarios and results as every other language.
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static List<Tool> Load() => Tools.SupportTools(Tools.LoadOrders("../../../07-tools-and-mcp/labs/shared/orders.json"));
static ToolCall Call(string name, string args, string id) => new(id, name, args);
static bool No(string name, JsonObject args) => false;
static Func<IReadOnlyList<Message>, AgentTurn> Scripted(params AgentTurn[] turns)
{
    var queue = new Queue<AgentTurn>(turns);
    return _ => queue.Dequeue();
}
static string Names(Outcome o) => string.Join(" | ", o.Trace.Select(s => string.Join(",", s.Calls.Select(c => c.Name))));
Message[] ask = [new("user", "Where is my refund for A123?")];

// a two-step answer, with a trace
var o = await Agent.Run(Scripted(
    new("", [Call("get_order", """{"order_id":"A123"}""", "c1"), Call("get_refund", """{"order_id":"A123"}""", "c2")]),
    new("Your refund of 49.99 is being processed.", [])), ask, Load(), new(), No);
Check(o.Status == Status.Answered && Names(o) == "get_order,get_refund | ", Names(o));
Check(Agent.ScoreTrajectory(o, new(Status.Answered, ["get_refund"], ["issue_refund"], 3)).Count == 0, "trajectory");

// reads run together on the thread pool; a side effect waits
var log = new List<string>();
var gate = new Lock();
Run Slow(string name, int ms) => _ =>
{
    lock (gate) log.Add($"start {name}");
    Thread.Sleep(ms);
    lock (gate) log.Add($"end {name}");
    return name;
};
var any = new JsonObject { ["type"] = "object" };
List<Tool> slow = [new("read_a", "", any, false, Slow("read_a", 30)), new("read_b", "", any.DeepClone().AsObject(), false, Slow("read_b", 10)),
    new("write_c", "", any.DeepClone().AsObject(), true, Slow("write_c", 1))];
var p = await Agent.Run(Scripted(new("", [Call("write_c", "{}", "1"), Call("read_a", "{}", "2"), Call("read_b", "{}", "3")]), new("done", [])),
    [], slow, new(), (_, _) => true);
Check(log.Where(s => s.StartsWith("end")).SequenceEqual(["end read_b", "end read_a", "end write_c"]) && log[4] == "start write_c", string.Join(", ", log));
Check(p.Messages.Where(m => m.Role == "tool").Select(m => m.ToolCallId).SequenceEqual(["1", "2", "3"]), "results in call order");

// a step limit stops a wandering agent
var n = 100;
var wandering = await Agent.Run(_ => { n++; return new("", [Call("get_order", $$"""{"order_id":"A{{n}}"}""", $"c{n}")]); },
    ask, Load(), new(MaxSteps: 3, MaxTokens: int.MaxValue, MaxRepeats: 5), No);
Check(wandering.Status == Status.StepLimit && wandering.Trace.Count == 3, wandering.Status);
Check(Agent.ScoreTrajectory(wandering, new(Status.Answered)).SequenceEqual(["ended StepLimit, expected Answered"]), "scored");

// the same call again and again is stuck
var stuck = await Agent.Run(_ => new("", [Call("get_refund", """{"order_id":"Z999"}""", "x")]), ask, Load(), new(MaxSteps: 20, MaxTokens: int.MaxValue), No);
Check(stuck.Status == Status.Stuck && stuck.Trace.Count == 3, stuck.Status);

// a token budget
var budget = await Agent.Run(Scripted(new("", [Call("get_order", """{"order_id":"A123"}""", "c1")], 25_500),
    new("", [Call("get_order", """{"order_id":"B456"}""", "c2")], 25_500), new("never reached", [], 25_500)), ask, Load(), new(MaxSteps: 10), No);
Check(budget.Status == Status.TokenLimit && budget.Trace.Select(s => s.Tokens).SequenceEqual([25_500, 25_500]), budget.Status);

// the scorer names each broken expectation
var refunded = await Agent.Run(Scripted(new("", [Call("issue_refund", """{"order_id":"B456","amount":120}""", "c1")]), new("I've asked for a refund.", [])),
    ask, Load(), new(), No);
var failures = Agent.ScoreTrajectory(refunded, new(MustCall: ["get_refund"], MustNotCall: ["issue_refund"], AnswerMatches: new Regex("(?i)no refund")));
Check(failures.SequenceEqual(["never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund"]), string.Join(" | ", failures));

// the workflow
var tools = Load();
var prompts = new List<string>();
string Write(string prompt) { prompts.Add(prompt); return "Your refund of 49.99 for A123 is being processed."; }
Check(Agent.RefundStatus("Where is my refund for order a123?", tools, Write) == new WorkflowResult.Answer("Your refund of 49.99 for A123 is being processed.", 1), "answer");
Check(prompts[0].Contains("""Refund: {"status":"processing","amount":49.99,"requested":"2026-09-28"}"""), prompts[0]);
Check(Agent.RefundStatus("Has my refund come through?", tools, Write) is WorkflowResult.Ask, "ask");
// "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
Check(Agent.RefundStatus("Can you change my delivery address?", tools, Write) == new WorkflowResult.Handoff("classified as feature"), "handoff");
Agent.RefundStatus("Where is my refund for D012?", tools, Write);
Check(!prompts[^1].Contains("IGNORE") && prompts.Count == 2, string.Join("\n", prompts));

Console.WriteLine("all agent checks passed");
```

The project links the tools lab's `Tools.cs` and the evals lab's `Evals.cs`; `container.sh` copies them, laid out as in the vault, into the .NET SDK container.

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/08-agents/labs/csharp). `python3 labs/run.py agents/csharp` (needs Podman).

## Common pitfalls

1. **Running side effects in parallel.** Two refunds started together can both pass the "no refund yet" check before either writes. Keep side effects sequential, as every lab does.
2. **Results in finishing order.** The fastest tool finishes first, but the model asked in a particular order, and some providers check it. Put results back in call order.
3. **Shared state without protection.** Goroutines, virtual threads and thread-pool tasks really run at once. Give each its own slot, or use a lock or a concurrent collection.
4. **Blocking an event loop.** In Python and JavaScript, a tool that computes for a second without awaiting stalls every other tool and the whole agent. Move heavy work to a thread or process.
5. **Timing tests on a real clock.** "The 10 ms tool ends first" can fail on a busy machine. Go's `synctest` and tokio's paused clock make it deterministic; elsewhere, keep the time gap wide.
6. **A framework without the controls.** Check that your agent framework has a step limit, a budget, approval and tracing turned on. Defaults vary.

## Check your understanding

1. Why can't two Python tools running under `asyncio.gather` corrupt a shared list, when two Go goroutines can?
2. How does the Go lab collect results from goroutines without a lock?
3. Why does Rust make `approve` take `+ Sync`, and when would the code fail to compile?
4. Why does the Java lab create a new virtual-thread executor every step, inside `try`-with-resources?
5. Every lab runs side effects one at a time, after the reads. What could go wrong if two `issue_refund` calls ran in parallel?
6. In the C# lab, why is `Task.Run` there, and when would you leave it out?

<details>
<summary>Answers — after your attempt</summary>

1. `asyncio` runs every task on one thread, and a task only gives way at an `await`, so two tasks never touch the list at the same instant. Goroutines run on several threads at once, so two can append simultaneously.
2. It makes a results slice with one slot per call before starting them, and each goroutine writes only its own index. Different slots are different memory, so there's no race, and `wg.Wait()` makes all the writes visible before the loop reads them.
3. Several threads may call `approve` at the same moment, so it must be safe to share between threads, which is what `Sync` means. A closure that changed a plain shared counter, say, wouldn't be `Sync`, and the compiler would reject the call instead of letting it race.
4. So every read started in a step is finished before the step ends: closing the executor waits for all its tasks. Virtual threads are cheap enough that a fresh executor per step costs almost nothing.
5. Both could read the order, both see no refund, and both write one, paying twice. Running side effects one at a time means the second sees the first's refund and refuses.
6. The lab's tools are synchronous, so calling them directly would run them one after another on the current thread. `Task.Run` puts each on a thread-pool thread so they overlap. Tools that do asynchronous I/O already return tasks, so you'd call them and `await Task.WhenAll` without `Task.Run`.

</details>

## Practice — independent task

**Find the race, then remove it.**

1. In your language's lab, change the loop so side-effecting calls run in parallel with everything else.
2. Write a test in which the model asks for two `issue_refund` calls on B456 in one turn, with approval granted, and the tool's `run` waits a little between its check and its write.
3. Run it until it fails: both refunds succeed. Then put the sequential rule back and watch the test pass every time.

**Done when:** you have a test that fails with parallel side effects and passes with sequential ones, and you can explain the failure in one sentence.

## Before moving on

You can run tool calls concurrently in your language, keep their results in order, keep shared state safe, and say what an agent framework in your ecosystem would replace.

**Recap.** The loop, the controls and the scorer are the same everywhere. Concurrency is what differs. Python's `asyncio` and JavaScript take turns on one thread. Go's goroutines, Java's virtual threads and C#'s thread-pool tasks really run at once, so they need separate slots, locks or concurrent collections. Rust's scoped threads borrow safely, and its compiler refuses anything shared that isn't `Sync`. In every language, reads run together, side effects run alone, and results go back in the order they were asked for.

## Related
- [[ai-ml/03-ai-engineer/08-agents/index|Agents]] — the main lesson
- [[ai-ml/03-ai-engineer/07-tools-and-mcp/in-other-languages|Tools and MCP in other languages]] — the tools each lab imports
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/in-other-languages|Reliability and plumbing in other languages]] — cancellation and fake clocks in each language
- [[os/06-concurrency-primitives|Concurrency primitives]] — locks, races and what's underneath
