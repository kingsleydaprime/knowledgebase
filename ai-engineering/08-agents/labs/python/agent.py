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
