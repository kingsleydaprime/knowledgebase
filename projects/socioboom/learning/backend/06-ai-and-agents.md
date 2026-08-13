# SocioBoom Backend — AI Providers, Agents & Structured Output

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/05-queues-and-jobs.md` (why agent runs are queued, not synchronous),
`learning/backend/07-feature-case-studies.md` (the two features these techniques power), and
`learning/backend/04-auth-and-security.md` (BYOK key storage and encryption).

This file covers: the AI provider abstraction and swapping between Anthropic and OpenRouter, the
difference between a single-shot prompt and a real agent loop (and how to tell which one your
problem needs), forcing structured output with tool use instead of parsing regex out of prose, and
grounding an agent safely — URL allowlists, page fetching, and the SSRF risk that makes the
allowlist non-optional.

---

## 11. AI Provider Abstraction

### The Problem

You want to call an AI model. But which model? Anthropic's API is different from OpenAI's API. If you hard-code Anthropic calls everywhere, switching to another provider means changing dozens of files.

### The Solution

Create a single function that is the only thing the rest of the codebase calls. Hide which provider is used behind an environment variable.

```ts
// src/api/v1/shared/services/ai.ts
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';

// Read provider at startup (not per request — avoids overhead)
const provider = (process.env.AI_PROVIDER || 'anthropic') as 'anthropic' | 'openrouter';

// Initialize the Anthropic client once
const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// The only export — the single interface the rest of the codebase uses
export async function generateText(systemPrompt: string, userPrompt: string): Promise<string> {
  if (provider === 'openrouter') {
    return generateWithOpenRouter(systemPrompt, userPrompt);
  }
  return generateWithAnthropic(systemPrompt, userPrompt);
}
```

Every service that needs AI calls `generateText(system, user)` and gets back a string. It does not know or care which model ran.

### Anthropic Implementation (Extended Thinking)

```ts
async function generateWithAnthropic(systemPrompt: string, userPrompt: string): Promise<string> {
  const stream = anthropic.messages.stream({
    model: 'claude-opus-4-8',
    max_tokens: 8000,
    thinking: { type: 'adaptive' }, // Adaptive thinking: model decides when to think deeply
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
  });

  // Wait for the full response (streaming resolves to the final message)
  const message = await stream.finalMessage();

  // The response can contain thinking blocks (internal reasoning) and text blocks
  // We only want the text blocks
  for (const block of message.content) {
    if (block.type === 'text') return block.text;
  }
  return '';
}
```

`thinking: { type: 'adaptive' }` tells the model to use extended thinking when the query warrants it. The model produces "thinking" content blocks (its internal reasoning chain) followed by text blocks (the actual answer). The code filters for text blocks only.

`stream.finalMessage()` waits for the complete response even though we're using the streaming API. The reason to use the streaming API anyway: it allows real-time progress reporting and has better timeout handling for long-running responses.

### OpenRouter Implementation

```ts
async function generateWithOpenRouter(systemPrompt: string, userPrompt: string): Promise<string> {
  const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-opus-4-8';

  const { data } = await axios.post(
    'https://openrouter.ai/api/v1/chat/completions',
    {
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
    },
    {
      headers: {
        Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': process.env.APP_URL || 'http://localhost:3000',
        // HTTP-Referer is required by OpenRouter for rate limiting and attribution
      },
    },
  );

  return (data.choices[0]?.message?.content as string) ?? '';
}
```

OpenRouter's API follows the OpenAI ChatCompletion format. The response shape is `{ choices: [{ message: { content: string } }] }`. The optional chaining (`?.`) and nullish coalescing (`?? ''`) handle edge cases where the response is malformed.

### When to Use Which Provider

- **`AI_PROVIDER=anthropic`** (default): Direct Anthropic API with extended thinking. Best for quality. Requires `ANTHROPIC_API_KEY`.
- **`AI_PROVIDER=openrouter`**: Routes through OpenRouter, which aggregates many model providers. Useful for fallback, cost comparison, or accessing models not directly available. Requires `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL`.

Switching providers requires only changing `.env`. Zero code changes.

---


## 22. Single-Shot Prompts vs AI Agents

The original Pain-Point Discovery was a **pipeline**: three fixed steps, each a single LLM call.

```
extractKeywords(description)      → 1 LLM call, returns phrases
webSearch(phrases) per platform   → fixed queries, snippets only
generateText(filter prompt)       → 1 LLM call over 5,000 chars of snippets
```

It worked, but every weakness traced back to the same root cause: **the pipeline can't react to what it finds.**

- If the extracted keywords were bad, the whole session was bad — nothing could reformulate.
- It only ever saw search *snippets*, never the actual posts, so "pain points" were often truncated titles.
- If a search returned 2 results, it shipped 2 results instead of trying a different angle.

The rewrite replaced the pipeline with an **agent**: one model in a loop with tools, deciding for itself what to do next.

```
loop (max N steps):
  model looks at everything so far
  → calls search_web / search_reddit / fetch_page / save_pain_point
  → tool results are appended to the conversation
  → repeat until the model stops calling tools (or budget runs out)
```

The core loop (`shared/services/agent.ts`) is ~60 lines per provider. The Anthropic version:

```ts
const messages: Anthropic.MessageParam[] = [{ role: 'user', content: prompt }];

while (steps < maxSteps) {
  steps++;
  const outOfBudget = steps === maxSteps;
  const res = await client.messages.create({
    model, max_tokens: 4000, system, messages,
    tools: anthropicTools,
    // Last turn: force a text wrap-up instead of more tool calls
    ...(outOfBudget ? { tool_choice: { type: 'none' as const } } : {}),
  });
  messages.push({ role: 'assistant', content: res.content });

  const toolUses = res.content.filter((b) => b.type === 'tool_use');
  if (!toolUses.length) return { finalText: lastText, steps, toolCalls };

  const results = [];
  for (const tu of toolUses) {
    results.push({
      type: 'tool_result',
      tool_use_id: tu.id,
      content: await safeExecute(toolMap.get(tu.name), tu.name, tu.input),
    });
  }
  messages.push({ role: 'user', content: results });
}
```

Key mechanics worth memorizing:

1. **Every `tool_use` block must be answered with a `tool_result`** in the next user message, matched by `tool_use_id`. If you drop one, the API rejects the request.
2. **Tool errors go back as text, not exceptions.** `safeExecute` catches everything and returns `"Error: ..."` — the agent reads the error and adapts (retries with different input, tries another tool). An unhandled throw would kill the whole run over one bad URL.
3. **Cap tool-result size** (we truncate at 6,000 chars). A fetched web page can be 500 KB of HTML; without a cap one tool call blows the context window and your budget.
4. **Budget the loop with `maxSteps`, and force a wrap-up on the last step** using `tool_choice: 'none'` so you always get a final summary instead of a half-finished tool call.
5. The OpenRouter version is the same loop with OpenAI-style `tools`/`tool_calls`/`role: "tool"` messages — writing both keeps BYOK users on whichever provider they configured.

**When to use which** (the actual decision framework applied to this codebase):

| Task | Shape | Choice |
|---|---|---|
| Topic → platform posts | one input, one output | single-shot |
| Review → social post | one input, one output | single-shot |
| Pain point → reply | one input, one output | single-shot |
| Find pain points across the web | search → read → judge → refine → repeat | **agent** |
| Find reviews of a business | search → open review pages → extract | **agent (small budget)** |

An agent adds latency and cost per run, so it must buy you something: *iteration* (reformulating failed searches) and *tool access* (reading the actual page). If the task has neither — it's a pure text transformation — an agent is just a slower prompt.

---

## 23. Structured Output: Forced Tool Use Instead of Regex

The old code asked the model for JSON and then went fishing:

```ts
const raw = await generateText(system, userPrompt, aiKeys);
const match = raw.match(/\[[\s\S]*\]/);   // find something array-shaped
if (!match) return [];                    // silently give up
const posts = JSON.parse(match[0]);       // hope it parses
```

Three failure modes, all silent:
- The model wraps the JSON in prose or markdown fences → regex may grab garbage.
- The model apologizes instead of answering → `return []` looks identical to "no results."
- The JSON parses but has the wrong shape → crash later, far from the cause.

The fix on Anthropic is **forced tool use**. You define a tool whose `input_schema` is your output schema, then force the model to "call" it. The model physically cannot reply with prose — the only legal output is arguments matching your schema:

```ts
const message = await client.messages.create({
  model, max_tokens: 4000, system,
  messages: [{ role: 'user', content: userPrompt }],
  tools: [{ name: 'emit_result', description: 'Emit the structured result.', input_schema: schema }],
  tool_choice: { type: 'tool', name: 'emit_result' },   // ← the forcing
});
const block = message.content.find((b) => b.type === 'tool_use');
return block.input as T;   // already parsed, already schema-shaped
```

Gotchas learned the hard way:

1. **The schema root must be `type: "object"`.** If you want an array, wrap it: `{ keywords: string[] }` instead of `string[]`.
2. **Forced `tool_choice` is incompatible with extended thinking** — thinking only allows `auto`/`none`. `generateJSON` therefore doesn't pass `thinking`, while free-text `generateText` does.
3. OpenRouter doesn't support Anthropic's forcing across all models, so the fallback is `response_format: { type: 'json_object' }` plus a *tolerant* parser (strip fences, then find the first `{...}`/`[...]`). Tolerance is the fallback, not the default.

Also fixed in the same pass: `generate.controller` passes `enum: platforms` on the platform field, so the model can't invent `"Twitter/X"` when the frontend expects `"twitter"`. Push every constraint you have into the schema — each one is a class of bug the model can no longer produce.

---


## 25. Grounding an Agent: URL Allowlists, Page Fetching, SSRF

### The hallucinated-URL bug (a real one)

The old validation tried to detect fake URLs with a pattern check:

```ts
const isReal = url && (realUrls.has(url)
  || /reddit\.com\/r\/\w+\/comments\//.test(url)    // ← the hole
  || /twitter\.com|x\.com/.test(url));
```

See the flaw? A model that invents `https://reddit.com/r/startups/comments/abc123/fake_post/` produces a **well-formed** URL — the regex happily passes it. Users would click through to 404s. You cannot validate provenance with a format check.

The fix: **an allowlist of URLs the system actually observed.** Every search result and every successfully fetched page registers its URL in a `Set`:

```ts
export interface ResearchContext {
  seenUrls: Set<string>;   // populated by search_web and fetch_page
  ...
}

// in save_pain_point:
const urlVerified = !!postUrl && ctx.seenUrls.has(postUrl);
// unverified → saved with postUrl: undefined, and the agent is told:
return `Saved, but the URL was dropped — it never appeared in your search results. Do not invent URLs.`;
```

Two properties make this robust: the check is *exact membership*, not pattern matching; and the agent gets **feedback** when it misbehaves, which corrects it mid-run.

### Reading pages properly

Search snippets are ~150 chars. The `fetch_page` tool gets the real content, with a platform-specific trick worth knowing: **append `.json` to any Reddit thread URL** and you get the post *and comments* as clean JSON — no HTML scraping:

```ts
const jsonUrl = `https://www.reddit.com${url.pathname.replace(/\/$/, '')}.json?limit=15`;
// data[0] = the post, data[1] = the comment tree
```

Comments are often better pain points than the post itself ("came here to say I have this exact problem").

For everything else: strip `<script>`/`<style>`, strip tags, decode entities, collapse whitespace. Crude but sufficient for an LLM reader.

### SSRF: the security cost of `fetch_page`

The moment your server fetches URLs an *LLM chose*, you've built a potential Server-Side Request Forgery gadget: a manipulated agent could request `http://localhost:3001/api/...` or a cloud metadata endpoint *from inside your network*. Guard before every fetch:

```ts
const host = url.hostname.toLowerCase();
const isPrivate =
  host === 'localhost' || host.endsWith('.local') || host.endsWith('.internal') ||
  /^127\.|^10\.|^192\.168\.|^169\.254\.|^0\./.test(host) ||
  /^172\.(1[6-9]|2\d|3[01])\./.test(host) ||
  host === '::1' || host.startsWith('fd') || host.startsWith('fe80');
if (isPrivate) throw new Error('URL points to a private address');
```

Plus `timeout` and `maxContentLength` on the request itself — a hanging or 2 GB response shouldn't stall a worker.

---


