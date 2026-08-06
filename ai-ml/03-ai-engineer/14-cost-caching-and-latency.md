# Cost, Caching & Latency

**Source:** Part II of the AI-engineer track. [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & production]] called cost "a first-class design constraint" and left it at two bullets. This note is the levers. Cost and latency are the two forces that decide whether an AI feature is *shippable at scale* — a demo that costs $2/query or takes 15 seconds is a demo forever. Code is illustrative shape; prices move constantly, so treat any number here as an order-of-magnitude, not a quote.

## How LLM cost actually works

You pay **per token**, split into **input** (everything you send — system prompt, history, retrieved context, the question) and **output** (what the model generates), with output typically **~4–5× the input price**. So cost scales with *both* how much context you stuff in *and* how much the model writes back. Two consequences drive every lever below:
- **Context is not free.** A giant system prompt or a fat RAG payload is billed on *every single call*. Trimming context is often the biggest cost win available.
- **Model choice dominates.** Frontier models cost **roughly 5–25× more per token** than small/fast models in the same family. Picking the right size for the task is the single highest-leverage cost decision.

## Lever 1 — right-size the model (model routing / cascading)

Most requests don't need your most capable model. The pattern:
- **Match model to task.** Classification, extraction, short rewrites, routing → a small fast model. Hard reasoning, long-horizon agentic work, nuanced generation → a frontier model. (This is the decision process from [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|the AI-engineer role]] and [[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]], now viewed through cost.)
- **Cascade / route.** Try the cheap model first; **escalate to the expensive one only when the cheap answer fails a check** (low confidence, a validator rejects it, a classifier flags it as hard). A well-tuned cascade serves the easy majority cheaply and reserves the frontier model for the tail — often cutting cost several-fold with little quality loss.
- **A small model plus good context often beats a big model with poor context.** Retrieval and prompt quality frequently substitute for raw model size — cheaper *and* more grounded.

## Lever 2 — prompt caching (the biggest single win for repeated context)

When many requests **share a long, stable prefix** — a big system prompt, a fixed few-shot block, a large document you ask many questions about — you shouldn't re-pay full price to process those same tokens every time. **Prompt caching** stores the processed prefix so subsequent calls re-use it: cached input tokens are read at **roughly a tenth of the normal price** (and faster, since the model skips re-processing them).

The mechanic that governs everything: **caching is a prefix match.** The cache key is the exact bytes up to a cache point, so **any change anywhere in the prefix invalidates everything after it.** Design the prompt around this:
- **Freeze the front, vary the end.** Put stable content first (frozen system prompt, deterministic tool list, fixed examples); put volatile content (the user's specific question, timestamps, per-request IDs) **last**, after the cached span.
- **Hunt silent invalidators.** A `Date.now()`, a UUID, an unsorted-key JSON dump, or a per-user string interpolated into the *front* of the prompt changes the prefix every request → the cache never hits and you pay full price with zero benefit. If your cache-hit rate is zero across identical-looking requests, a silent invalidator is why.
- **Mind the economics.** A cache *write* costs slightly more than a normal token (~1.25×) and entries have a short time-to-live (minutes). So caching pays off when the shared prefix is **large** and **reused often within the window** — a few reads and you're ahead; a prefix used once, never.

```ts
// ILLUSTRATIVE — mark the stable boundary; keep the question after it.
generate({
  system: FROZEN_SYSTEM_PROMPT,   // large + identical every call → cache this
  cachePoint: true,               // (provider-specific; some auto-cache the prefix)
  prompt: userQuestion,           // varies per request → NOT cached, sits last
});
```

**Semantic caching** is a different, coarser idea: cache the *whole answer* keyed by the *meaning* of the query (embed the query, and if a near-identical past query exists, return its stored answer without calling the model at all). Great for FAQ-shaped traffic with lots of repeats; risky where answers must be fresh or queries are all unique.

## Lever 3 — latency (real and perceived)

Latency has two halves, and you attack them differently:
- **Perceived latency — stream.** Sending tokens as they generate ([[ai-ml/03-ai-engineer/04-calling-models|calling models]]) means the user sees output in ~1 second instead of staring at a blank screen for ten. It doesn't make the model faster; it makes the wait *feel* gone. This is the single biggest UX lever and the default for anything chat-shaped. **Time-to-first-token** is the number users actually feel.
- **Real latency — do less, in parallel.**
  - **Smaller/faster models** are lower-latency as well as cheaper — the same right-sizing lever pays twice.
  - **Shorter outputs** finish sooner (output tokens are generated one at a time, so length ≈ time). Cap `max_tokens`; ask for the terse form.
  - **Parallelize independent calls.** Fan out concurrent, independent requests (multiple tool calls, a batch of items) instead of awaiting them serially. Careful: N identical requests fired at once all miss a shared cache — warm it with one request first, then fan out the rest.
  - **Prompt caching cuts latency too** — skipping re-processing of the cached prefix lowers time-to-first-token, not just cost.

## Lever 4 — trim what you send

Because you pay per token on every call, the cheapest token is the one you don't send:
- **Retrieve precisely.** In RAG ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & embeddings]]), fewer, more-relevant chunks beat dumping everything in — cheaper, faster, *and* usually more accurate (irrelevant context dilutes attention).
- **Compact history.** In long chats/agents, summarize or prune old turns instead of resending the whole transcript every call — the transcript is billed in full on every turn.
- **Batch offline work** at ~half price via a batch API (see [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|reliability & plumbing]]) for anything no user is waiting on.

## Making it visible

You can't optimize what you can't see. Log **tokens, cost, and latency per call** (a natural job for the AI gateway from [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|reliability & plumbing]]), broken down by feature and model. Watch cache-hit rate, p95 latency, and cost-per-request as first-class dashboards — the same way you'd watch any [[devops/10-observability/README|production system]]. Most "why is this so expensive?" mysteries are a missing cache hit, an oversized model, or unbounded context, and you only find them by measuring.

## Gotchas

- **Zero cache hits.** A silent invalidator (timestamp/UUID/unsorted JSON early in the prompt) or a prefix below the cacheable minimum. Diff two "identical" requests byte-for-byte.
- **Output price dominates on generation-heavy tasks.** For long-form generation the ~5× output multiplier, not the input, is where the money goes — cap and shorten outputs.
- **Semantic-cache staleness.** Returning a cached answer for a query whose correct answer has since changed. Scope it to genuinely stable Q&A, and expire aggressively.
- **Parallel fan-out re-misses the cache.** Concurrent identical requests can't read a cache the first one is still writing — warm with one, then fan out.
- **A cascade needs a good escalation check.** If the "was the cheap answer good enough?" test is weak, you either escalate everything (no savings) or ship bad cheap answers. The check quality *is* the cascade quality.

## Key insight

**Cost and latency are engineered, not accepted.** The levers, in order of impact: right-size the model (and cascade cheap→expensive), cache the stable prefix (freeze the front, vary the end, hunt invalidators), stream to erase perceived latency, and trim every token you send. Measure tokens/cost/latency per call so the waste is visible. A feature that's 10× cheaper and feels instant is the same capability made *shippable* — and that gap is pure engineering.

## Related
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|Reliability & Plumbing]] — the gateway that centralizes caching, routing, and cost tracking
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — streaming and the token knobs
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — precise retrieval as a cost lever
- [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|The AI-Engineer Role]] — choosing the right tool/model for the task
