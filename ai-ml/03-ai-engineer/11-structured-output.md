# Structured Output

**Source:** Part II of the AI-engineer track — depth on a topic that was scattered across [[ai-ml/03-ai-engineer/04-calling-models|calling models]] and [[ai-ml/03-ai-engineer/05-prompt-engineering|prompt engineering]] but never owned. This is the single most important technique for using an LLM as a **reliable software component** rather than a chat toy. Code is illustrative shape — verify signatures against your SDK's version-matched docs.

## The problem: a string is not an interface

An LLM returns text. Software needs *typed data* — a `Customer` object, a `boolean`, an array of tags. The gap between "here's a paragraph" and "here's a validated record my code can branch on" is where most brittle AI features break: you prompt for JSON, the model wraps it in ```` ```json ```` fences, or adds a "Sure! Here's the data:" preamble, or emits a trailing comma, and your `JSON.parse` throws in production.

**Structured output closes that gap by constraining the model to a schema** — you hand it the shape you want, and you get back data that fits it. This is what lets you drop an LLM into a pipeline as a *function*: `extract(text) -> Invoice`, `classify(ticket) -> Priority`.

## Three mechanisms, increasingly strong

### 1. Prompt-and-parse (weakest)
Ask for JSON in the prompt, parse the response yourself. Works, but the model can still deviate — you *must* wrap the parse in a retry (see below). Only reach for this when the provider offers nothing better.

### 2. JSON mode / response format
The provider guarantees the output is *syntactically valid JSON* (no fences, no preamble). It does **not** guarantee your *shape* — you still validate the fields. A meaningful step up from prompt-and-parse because the "it wasn't even valid JSON" failure class disappears.

### 3. Schema-constrained decoding (strongest)
You supply a JSON Schema; the provider constrains generation so the output **provably conforms** — right fields, right types, required keys present. Under the hood the decoder masks tokens that would violate the schema at each step, so an invalid document is literally unrepresentable. This is the mechanism behind "strict" tool calling and typed-object helpers.

```ts
// ILLUSTRATIVE — the durable idea, not an exact API.
import { generateObject } from "ai";
import { z } from "zod";

const Invoice = z.object({
  vendor: z.string(),
  total_cents: z.number().int(),        // ask for cents — floats drift
  due_date: z.string().date(),
  line_items: z.array(z.object({ description: z.string(), amount_cents: z.number().int() })),
  is_overdue: z.boolean(),
});

const { object } = await generateObject({ model, schema: Invoice, prompt: invoiceText });
//        ^ typed as z.infer<typeof Invoice>, already validated
```

The schema is doing double duty: it constrains the model **and** documents the contract **and** (with a library like Zod/Pydantic) gives you a runtime validator and a static type from one definition.

## Structured output vs. tool calling — same machinery

Tool calling ([[ai-ml/03-ai-engineer/07-tools-and-mcp|tools & MCP]]) *is* structured output pointed at a different target: the model emits a typed argument object for a function instead of a typed answer for you. "Strict" tools use the exact same schema-constrained decoding. So there are two ways to get structured data:
- **`generateObject`-style** — the model's *answer* is the structured data (extraction, classification).
- **A single forced tool call** — define one tool whose parameters are your schema, force the model to call it. Useful when your stack only exposes structured data through the tool path.

## The discipline that makes it production-grade

- **Validate at the boundary anyway.** Even schema-constrained output can be *schema-valid but wrong* — a hallucinated `vendor`, a `total` that doesn't match the line items. Schema conformance is a syntax guarantee, not a correctness one. Re-check business invariants in code.
- **Retry on invalid.** With the weaker mechanisms, wrap the call: parse → on failure, feed the parse error back to the model ("your output failed with: *unexpected token* — return only valid JSON matching the schema") and retry once or twice. Cap the retries; a persistent failure is a signal to simplify the schema.
- **Keep schemas flat and shallow.** Deeply nested, deeply optional schemas raise the error rate and the token cost. Model the *minimum* structure your code consumes.
- **Prefer enums over free strings** for anything categorical (`priority: "low" | "med" | "high"`). It removes a whole class of "the model said `Medium` but my switch checks `med`" bugs.
- **Ask for machine-friendly units.** Integer cents over dollar floats, ISO-8601 over "next Tuesday", explicit `null` over an omitted key.
- **Watch the known schema limits.** Constrained decoding usually supports types, `enum`, `required`, nesting, and `additionalProperties: false`, but often **not** `minLength`/`maximum`/regex constraints — enforce those in your own validator after the fact.

## Gotchas

- **`additionalProperties: false` is usually mandatory** for strict schemas — without it the model may bolt on extra keys. Most typed-object helpers set it for you; raw-schema callers must add it.
- **A refusal breaks the shape.** If the model declines for safety reasons, the output won't match your schema — check for the refusal signal *before* trusting the parse ([[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]).
- **Hitting the token cap truncates the JSON** into invalid mid-object garbage. Size `max_tokens` for the whole object, and treat a truncation stop-reason as a retry, not a parse.
- **First call with a new schema can be slower** — some providers compile the schema and cache it; subsequent identical-schema calls are fast.

## Key insight

**Structured output is what turns "an LLM" into "a function."** The strongest form (schema-constrained decoding) makes malformed output impossible by construction; the discipline (validate business rules anyway, retry on failure, keep schemas flat, use enums and machine units) is what makes the function trustworthy inside a real pipeline. Everything downstream — [[ai-ml/03-ai-engineer/08-agents|agents]] deciding actions, [[ai-ml/03-ai-engineer/12-evals|evals]] scoring runs, extraction feeding a database — depends on this contract holding.

## Related
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — where structured output rides on the request
- [[ai-ml/03-ai-engineer/07-tools-and-mcp|Tools & MCP]] — the same schema machinery aimed at function arguments
- [[ai-ml/03-ai-engineer/12-evals|Evals]] — structural checks are the cheapest, most reliable eval
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — validating and containing model output
