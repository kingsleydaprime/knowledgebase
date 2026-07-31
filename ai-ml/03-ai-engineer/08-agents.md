# Agents

**Source:** re-homed from the old `01-fundamentals/06-agents.md`, deepened with the [roadmap.sh ai-agents](https://roadmap.sh/ai-agents) roadmap (memory, multi-agent, frameworks, observability, evals).

An LLM by itself only turns text into text. An **agent** wires an LLM into a loop where it can also take actions — run code, search, read/write files, call APIs — observe results, and decide what to do next. The model doesn't change; the scaffolding around it turns "predict tokens" into "accomplish a multi-step task."

## The agentic loop

The pattern behind essentially every agent framework:

```
1. Give the model a goal + a set of tools it may use
2. Model decides: answer directly, OR call a tool
3. If tool → execute it (your code), feed the result back into context
4. Model sees the result, decides again: answer, or call another tool
5. Repeat until it produces a final answer instead of a tool call
```

This is **ReAct** (Reason + Act) — the model reasons about what to do, acts via a [[ai-ml/03-ai-engineer/07-tools-and-mcp|tool call]], observes, repeats. It's the mechanical backbone whether the product is called an "agent," "assistant," or "copilot."

## Why agents can do more than one call — and why that's risky

A single LLM call is stateless and can't verify anything beyond its training data and the given text. An agent can **check its own work** — run a test, read the file it just edited, search for a fact instead of guessing — which is why agentic coding tools catch and fix their own mistakes across steps. The tradeoff: more autonomy = more surface for things to go wrong (a bad tool call, a misread result, errors compounding across a long loop). So agent design leans on **scoping tools tightly** and often **requiring confirmation before high-stakes actions** — the same principle by which this assistant is instructed to confirm destructive operations.

## Memory

The loop above is stateless beyond the [[ai-ml/03-ai-engineer/02-how-llms-work|context window]]. Real agents need memory:

- **Short-term** — the current conversation/task context (the window itself), often summarized/compacted as it fills.
- **Long-term** — persisted across sessions, usually via [[ai-ml/03-ai-engineer/06-rag-and-embeddings|embeddings + a vector store]]: the agent writes facts/experiences and retrieves relevant ones later. This is how an assistant "remembers" you across sessions — the product layer stores and re-injects context, since the model itself doesn't.

Distinguishing *episodic* memory (what happened) from *semantic* memory (learned facts) is a useful frame when designing what an agent should persist.

## Multi-agent systems

Some tasks split across multiple agents — a **planner** that decomposes and delegates to **workers**, or specialists with different tools coordinating on a shared goal. This adds real complexity (coordination, shared context, cost, more failure surface) and is worth reaching for only when a single agent genuinely can't hold the task's context or tool surface — **not** a default. Most "I need multiple agents" turns out to be "I need better tools and a clearer prompt."

## Frameworks and observability

- **Frameworks** — LangChain / LangGraph, CrewAI, AutoGen, and the SDK-native agent abstractions (e.g. the AI SDK's agent/tool-loop helpers, [[ai-ml/03-ai-engineer/04-calling-models|calling models]]) handle the loop, tool wiring, and state so you don't hand-roll it. Useful, but understand the underlying loop first — frameworks hide it, and you debug what you understand.
- **Observability** — agents are hard to debug because behavior spans many nondeterministic steps. Tracing tools (LangSmith, Langfuse, and general [[devops/10-observability/README|observability]] adapted for LLMs) capture each step — prompts, tool calls, token usage, latency — so you can see *why* an agent did what it did. Non-negotiable for anything beyond a toy.
- **Evals** — because output is nondeterministic, you can't "unit test" an agent conventionally. You build **evaluation sets** (representative tasks + criteria) and measure success rate as you change prompts/tools/models ([[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]).

## Gotchas

- "Agent" is used loosely — sometimes "an LLM with tools," sometimes "any product with an LLM in it." Ask what tools/autonomy a system actually has rather than trusting the label.
- More steps = more tokens (cost) and more chances for one bad step to derail the rest. Agent design is giving enough autonomy to be useful without so much that errors compound unchecked.
- Tool *results* re-enter the [[ai-ml/03-ai-engineer/02-how-llms-work|context window]] — a tool returning a huge blob burns context fast; scope tool output.

## Related
- [[ai-ml/03-ai-engineer/07-tools-and-mcp|Tools & MCP]] — the tool-calling primitive agents are built on
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — the substrate for long-term memory
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — evals, guardrails, sandboxing
