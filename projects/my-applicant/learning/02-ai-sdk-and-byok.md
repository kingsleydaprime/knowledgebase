# AI SDK v7 and the BYOK pattern — my-applicant

What "bring your own key" actually means in code, and the AI SDK details that
bit during this build.

---

## Why an SDK abstraction instead of calling Anthropic directly

If the tool only ever talked to Claude, the Anthropic SDK would be simpler and
better. The reason to add an abstraction layer is that **provider choice is the
product** here: the pitch is "your key, your model", and that only holds if
switching provider is a config line rather than a rewrite.

The Vercel AI SDK (`ai`) gives one `generateText` interface over Anthropic,
OpenAI, Google, OpenRouter, Ollama, and anything OpenAI-compatible. The whole
provider layer collapses to a switch statement returning a `LanguageModel`:

```ts
const { model } = resolveModel(config.llm, apiKey);
const { text } = await generateText({ model, prompt });
```

Everything downstream — scoring, tailoring, HN parsing — is provider-agnostic.

**The general lesson:** add an abstraction when *varying the thing* is a
requirement, not because varying it is conceivable. Here it was the
requirement. Most of the time it isn't, and the abstraction is a cost.

---

## Never write this SDK from memory

The single most useful habit from this build. The AI SDK changes across majors
and training data goes stale fast. Two APIs that "obviously" existed did not:

| Remembered (v5-era) | Actual (v7) |
|---|---|
| `system: '...'` | `instructions: '...'` |
| `generateObject({ schema })` | `generateText({ output: Output.object({ schema }) })` |

Both would have compiled as plausible-looking wrong code and failed at runtime.

The fix is that the package **ships its own docs**, version-matched:

```
node_modules/ai/docs/03-ai-sdk-core/10-generating-structured-data.mdx
node_modules/@ai-sdk/anthropic/docs/05-anthropic.mdx
```

Reading those beats any web search, because they cannot be out of sync with
what's installed.

Generalise it: **when a library ships docs or `.d.ts` files in
`node_modules`, that's the authoritative source.** It's on disk, it matches
your version, and it's faster than searching.

---

## Where the key comes from — and where it doesn't

The BYOK rule that shapes the config schema:

```yaml
llm:
  apiKeyEnv: ANTHROPIC_API_KEY   # the NAME of the variable
```

The config file names the environment variable; it never contains the key. So:

- `config.yaml` is safe to read over someone's shoulder.
- `.gitignore` still excludes it, because `profile.yaml` beside it holds
  personal data — belt and braces.
- The key lives only in the process environment, where it belongs.

This is a small pattern with a big payoff: **config names the secret, the
environment holds it.** It's why `git push` on this repo can never leak a key.

---

## Local providers break the "key is required" assumption

Ollama runs on `127.0.0.1` and authenticates against nothing. Demanding a key
would be an invented requirement — and Ollama is the main reason to want BYOK
at all.

So the loader splits providers into two sets:

```ts
const PROVIDERS_REQUIRING_KEY = new Set([
  'anthropic', 'openai', 'google', 'openrouter', 'gateway',
]);
```

`ollama` and `custom` are absent, so a missing key is fine for them.

The lesson is about **validation that assumes the common case**. "An API needs
a key" is true often enough to feel universal, and hard-coding it would have
silently blocked the offline use case. When you write a required-field check,
ask which legitimate configuration it makes impossible.

---

## Structured output, and degrading when it isn't available

Frontier hosted models can be *constrained* to a JSON schema — the API
guarantees the shape:

```ts
const { output } = await generateText({
  model,
  output: Output.object({ schema: myZodSchema }),
});
```

Small local models generally cannot. They'll return valid JSON wrapped in
prose, or fenced in ```` ```json ````, or with an invented extra field.

Two options: refuse to run locally, or degrade. This project degrades, in
`src/llm/structured.ts`:

1. Ask for JSON in the prompt.
2. Extract the first balanced JSON value from whatever came back.
3. Validate it with **the same Zod schema**.
4. On failure, retry once with the validation errors fed back as text.

Step 4 is the interesting one — feeding a model its own validation errors is
a surprisingly effective repair loop, and it costs one extra call only when
something went wrong.

The balanced-bracket scanner in `extractJson` is worth reading: naive
`text.indexOf('{')` … `lastIndexOf('}')` breaks the moment a JSON string value
contains a brace. It tracks string state and escapes so braces inside
`"reason": "we use {x} notation"` don't throw off the depth count.

---

## Schema-once, use-everywhere

One Zod schema does three jobs here:

1. Constrains generation (`Output.object({ schema })`).
2. Validates the fallback path's parsed JSON.
3. Produces the TypeScript type via `z.infer<typeof schema>`.

That's the real argument for Zod over hand-written types plus separate
validation: the type and the runtime check **cannot drift apart**, because
they're the same declaration.

---

## Batch model calls when the work is comparative

Scoring runs 8 jobs per call rather than 1:

```ts
const BATCH_SIZE = 8;
```

Two reasons, and the second is the non-obvious one:

- **Cost.** The candidate profile and instructions are resent on every call.
  Batching amortises that fixed prefix across 8 jobs instead of 1 — close to
  an order of magnitude on this workload.
- **Consistency.** The model sees the jobs side by side, so the scores are
  calibrated against each other. Scoring in isolation produces drift, where
  job #40 gets a 78 that means something different from job #3's 78.

The guard that makes batching safe:

```ts
const job = batch[s.index];
if (!job) continue;   // hallucinated index → drop, don't misattribute
```

Without it, a model returning `index: 9` for an 8-item batch would attach a
score to the wrong job — and this tool would then write a tailored resume for
a different role than the one it applies to. **When a model returns an index
into your data, always bounds-check it.**
