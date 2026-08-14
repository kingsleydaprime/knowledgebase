# Calling Models

**Source:** new for the AI-engineer track, and the most **project-grounded** note here — this is the day-to-day of building AI features (the AI SDK / provider-API work these projects actually do). Code below is **illustrative of the shape**; AI SDKs change fast, so treat exact signatures as "verify against the docs," not gospel (see the discipline section).

## The raw layer: provider APIs and the messages format

Every LLM provider exposes an HTTP API. The near-universal request shape is a list of **messages**, each with a **role**:

```jsonc
{
  "model": "…",
  "messages": [
    { "role": "system",    "content": "You are a terse code reviewer." },  // persistent instructions
    { "role": "user",      "content": "Review this function: …" },          // the request
    { "role": "assistant", "content": "…" }                                  // prior model turns (for multi-turn)
  ],
  "temperature": 0
}
```

- **system** — stable instructions (role, tone, constraints), set once (see [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt engineering]]).
- **user** / **assistant** — the alternating conversation. To give a model "memory" of a conversation you resend prior turns each call — the model itself is stateless between requests ([[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]]).

Sampling parameters (`temperature`, `top_p`, `max_tokens`, penalties) ride along on the request — the knobs from [[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]].

## Why use an SDK instead of raw HTTP

Provider APIs differ in detail (auth, streaming format, tool-calling shape). A unified SDK — the **Vercel AI SDK** (`ai` on npm) being the common TypeScript choice — abstracts that so you write once and **swap providers by changing a model string**. Its core capabilities, conceptually:

```ts
// ILLUSTRATIVE shape — verify exact current API against the installed version's docs.
import { generateText, streamText, tool, Output } from "ai";

// 1. One-shot text
const { text } = await generateText({ model, prompt: "…" });

// 2. Streaming (token-by-token, for responsive UIs)
const { textStream } = streamText({ model, prompt: "…" });

// 3. Structured output — get typed JSON, not a string to parse
const { output } = await generateText({ model, prompt: "…", output: Output.object({ schema }) });

// 4. Tool calling — give the model functions it can invoke (see 07-tools-and-mcp)
const result = await generateText({ model, tools: { getWeather: tool({ /* … */ }) }, prompt: "…" });
```

The four capabilities that matter to an AI engineer, regardless of SDK:

- **Text generation** — the basic call.
- **Streaming** — deliver tokens as they generate, so a UI isn't blank for seconds; the standard UX for chat.
- **Structured output** — constrain the model to a schema and get back typed, validated data instead of a string you regex. This is what makes LLMs usable as reliable *components* in software (extraction, classification, form-filling) rather than just chat.
- **Tool calling** — the model can request that your code run a function; the foundation of [[ai-ml/03-ai-engineer/07-tools-and-mcp|tools/MCP]] and [[ai-ml/03-ai-engineer/08-agents|agents]].

Framework hooks (e.g. React's `useChat`) wire streaming responses into UI with minimal code — but these are the **most frequently-changed APIs**, so always check current docs before using them.

## The discipline (this is the durable part)

AI tooling moves faster than almost anything else in software. The habits that keep you correct — and that matter more than any specific API:

- **Never hardcode model IDs from memory.** Models are released and retired constantly. Fetch the current list at build time (a gateway exposes `/v1/models`) and pick the newest appropriate one, rather than pasting an ID you remember.
- **Verify APIs against version-matched docs, not recall.** The SDK ships its own docs and source inside `node_modules` (`node_modules/ai/docs/`, `node_modules/ai/src/`) — those match your installed version exactly. Trust them over memory or a blog post. This is the same "verify against primary sources for fast-moving libraries" rule that applies to any volatile dependency.
- **Keep the SDK current.** Outdated installs are the most common error source; check installed vs latest and read the migration guide before a major bump.
- **A gateway is the fastest start.** An AI gateway (e.g. Vercel's) fronts many providers behind one API/key, so you reach OpenAI/Anthropic/Google with `provider/model` strings and no per-provider package — useful for prototyping and for swapping models to compare.
- **Type-check after changes.** Most errors are remembered-but-changed APIs surfacing as type errors — re-check the current docs when they occur.

## Related
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — the sampling parameters set on each call
- [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — what goes in the messages
- [[ai-ml/03-ai-engineer/07-tools-and-mcp|Tools & MCP]] — tool calling in depth
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — validating structured output, cost, observability
