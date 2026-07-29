# Understanding AI Agents

An LLM by itself only does one thing: turn text into more text (see [[03-llms|llms]]). An **agent** is an LLM wired into a loop where it can also take actions in the world — run code, search the web, read/write files, call an API — observe the result, and decide what to do next. The model itself doesn't change; what changes is the scaffolding around it that turns "predict the next tokens" into "accomplish a multi-step task."

## The agentic loop

The core pattern behind essentially every agent framework:

```
1. Give the model a goal, plus a list of tools it's allowed to use
2. Model decides: respond directly, OR call a tool
3. If it calls a tool -> execute the tool, feed the result back to the model
4. Model sees the result, decides again: respond, or call another tool
5. Repeat until the model produces a final answer instead of another tool call
```

```
User: "What's the weather in Lagos, then convert that temp to Fahrenheit"

Model: calls get_weather("Lagos")
Tool result: {"temp_c": 29}
Model: calls convert_temp(29, "C", "F")
Tool result: {"temp_f": 84.2}
Model: "It's 29°C (84.2°F) in Lagos right now."
```

Nothing here required a new kind of model — it required a system around the model that can parse "the model wants to call `get_weather`," actually execute that function, and feed the result back into the next call to the model. This loop (sometimes named **ReAct** — Reasoning + Acting — in early agent research) is the mechanical backbone almost every agent framework implements, whether it's called an "agent," "assistant," or something more specific.

## Tool calling — how a model "decides" to use a tool

Models are trained (via instruction-tuning, see [[03-llms|llms]]) to recognize when a task needs a tool and to output a structured request for it (a function name plus arguments, often as JSON) instead of a plain-text answer. The application layer around the model is responsible for defining what tools exist, actually executing them when the model requests one, and returning the result in a format the model can read. The model is never actually *running* code itself — it's producing a request that trusted application code fulfills.

## Why agents can do more than a single LLM call, and why that's risky

A single LLM call is stateless and can't verify anything outside its training data or the text you gave it directly. An agent, by contrast, can check its own work — run a test, read the actual file it just edited, search for a fact instead of guessing — which is why agentic coding tools can catch and fix their own mistakes across several steps in a way a single question-answer exchange can't. The tradeoff: more autonomy means more surface area for something to go wrong across many steps (a bad tool call, a misinterpreted result, compounding errors across a long loop) — which is why agent design leans heavily on scoping what tools an agent can access, and often on requiring confirmation before higher-stakes actions (this exact principle shows up in how this assistant is instructed to behave around destructive or hard-to-reverse actions).

## Multi-agent systems

Some tasks are split across multiple agent instances instead of one — a "planner" agent that breaks a task down and delegates pieces to "worker" agents, or several agents with different tool access/specializations coordinating on a shared goal. This adds complexity (coordination, shared context, cost) and is worth reaching for only when a single agent genuinely can't hold the whole task's context or tool surface at once — not a default starting point.

## MCP (Model Context Protocol)

A standardized way for an application to expose tools/data to any compatible LLM client, instead of every application inventing its own custom tool-calling integration. Rather than hand-coding "here's how this specific model calls this specific API," MCP defines a common protocol so a tool built once can be used by any MCP-compatible agent — worth knowing the name exists as tool integration becomes more standardized across the ecosystem, without needing to implement the protocol itself at this stage.

## Gotchas

- "Agent" is used loosely across the industry — sometimes meaning "an LLM with tool access," sometimes "any product with an LLM in it at all." Ask specifically what tools/autonomy a system has rather than trusting the label.
- More tool-calling steps means more tokens (and cost) per task, and more opportunities for one bad step to derail the rest — agent design is partly about giving enough autonomy to be useful without giving so much that errors compound unchecked.
- An agent's tool *results* go back into the model's context window (see [[03-llms|llms]]) just like anything else — a tool that returns a huge amount of text can consume context budget fast.

## Related
- [[03-llms|llms]]
- [[07-prompting|prompting]]
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
