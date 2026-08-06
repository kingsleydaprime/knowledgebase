# Reliability & Plumbing

**Source:** Part II of the AI-engineer track. [[ai-ml/03-ai-engineer/04-calling-models|Calling models]] shows you *how* to make a call; this note is everything between "it works on my machine" and "it survives real traffic." None of it is glamorous — retries, timeouts, rate limits, fallbacks — and all of it is the difference between a demo and a service. Code is illustrative shape.

## The core reality: model calls are unreliable network calls

A call to an LLM API is a slow HTTP request to someone else's overloaded servers. It will, routinely:
- **time out** (generation is slow; big outputs take tens of seconds),
- **rate-limit you** (HTTP 429 — you exceeded requests- or tokens-per-minute),
- **fail transiently** (500/503/overloaded — retry usually fixes it),
- **fail permanently** (400 bad request, 401 auth — retrying is pointless).

Treat every model call with the same defensive posture you'd give any flaky third-party dependency. The failure classes above map directly to how you respond.

## Retries with exponential backoff + jitter

The default response to a *transient* failure (429, 5xx, connection drop) is: wait, then try again — with the wait growing each attempt so you don't hammer a struggling server.

```ts
// ILLUSTRATIVE — most SDKs do this for you; know what it's doing.
async function withRetry(call, { max = 4, base = 500 } = {}) {
  for (let attempt = 0; ; attempt++) {
    try {
      return await call();
    } catch (err) {
      const retryable = err.status === 429 || err.status >= 500 || err.isConnectionError;
      if (!retryable || attempt >= max) throw err;      // 4xx (except 429) → give up now
      const wait = err.retryAfter ?? base * 2 ** attempt // exponential…
                 + Math.random() * base;                 // …+ jitter to avoid thundering herds
      await sleep(wait);
    }
  }
}
```

Two rules that matter:
- **Honor `Retry-After`.** A 429 usually tells you exactly how long to wait — use it instead of guessing.
- **Add jitter.** If a thousand clients all back off by exactly `2^attempt` seconds, they retry in sync and re-spike the server. Randomizing spreads them out.
- **Never retry a 400/401/permission error.** It'll fail identically forever and burns your budget. Only retry the transient classes.

Most official SDKs retry 429/5xx automatically (often 2 retries by default). Know your SDK's defaults before hand-rolling — usually you just *tune* `max_retries`, not reimplement the loop.

## Timeouts

Generation can take a long time, and a hung connection is worse than a fast failure. Two knobs:
- **Set a request timeout** appropriate to the call. A short classification can time out at 10s; a long agentic run needs minutes.
- **Beware "per-chunk" vs "total" timeouts.** Many HTTP clients' timeout is *per byte received*, not wall-clock — a slowly-trickling stream resets it forever and can hang indefinitely. For a hard deadline, track wall-clock time yourself at the call site.
- **Stream long or large outputs.** Streaming ([[ai-ml/03-ai-engineer/04-calling-models|calling models]]) sidesteps the timeout entirely — bytes keep arriving, the connection never idles — and it's the standard fix for "my big-output request keeps timing out." (It also improves perceived latency; see [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost, caching & latency]].)

## Rate limits — design for them, don't just retry them

Providers cap you on **requests per minute (RPM)** and **tokens per minute (TPM)**, per tier. Retrying a 429 handles a blip; *sustained* 429s mean you're structurally over the limit and need to shape traffic:
- **Client-side throttling** — a queue or token-bucket limiter that paces requests under your quota rather than firing them all and eating 429s.
- **Batch the batchable.** Non-latency-sensitive work (nightly enrichment, bulk classification) often has a **batch API** that runs asynchronously at ~half price and doesn't count against your live RPM. Use it for anything a user isn't waiting on.
- **Request a tier bump** when legitimate traffic outgrows the quota — but throttle first; a bigger quota you blow through instantly is just a bigger 429.

## Fallbacks — degrade instead of dying

When a provider (or a specific model) is down, overloaded, or refuses, don't 500 the user — fall back:
- **Cross-model / cross-provider fallback.** Primary model errors → retry the request on a secondary (a different model, or the same model on a different provider). This is a major reason to keep prompts provider-portable and to route through an **AI gateway**.
- **Graceful degradation.** For a non-critical feature, a failed AI call should fall back to a non-AI path (cached answer, a simpler heuristic, "try again shortly") — never a hard error.
- **Idempotency.** If a call might be retried (by you or the SDK), make sure a duplicated request can't double-charge, double-send, or double-write. Attach an idempotency key to any side-effecting operation.

## AI gateways — the plumbing layer

An **AI gateway** (LiteLLM, Portkey, a provider's own, or a thin in-house proxy) sits between your app and the model providers and centralizes exactly this plumbing:
- one API and one key for many providers (swap models by changing a string),
- retries, timeouts, and **fallback routing** across providers in one place,
- **rate-limit handling and load-balancing** across keys/regions,
- **caching** ([[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost, caching & latency]]), **cost tracking**, and **observability** (logging every call's prompt, tokens, latency, cost).

The payoff: your application code stays about the *feature*, and the cross-cutting reliability concerns live in one swappable layer. For a prototype a gateway is optional; for anything multi-provider or production-facing it's usually the right backbone. (This is the LLM-shaped slice of general [[devops/10-observability/README|observability]] and resilience engineering — the patterns are the same ones you'd apply to any critical downstream dependency.)

## Gotchas

- **Retrying non-idempotent side effects double-executes them.** The email sends twice, the row inserts twice. Guard side-effecting calls with idempotency keys before enabling retries.
- **A retry storm can amplify an outage.** Aggressive retries against a struggling provider make it worse and burn your quota. Cap attempts, back off, add jitter, and add a circuit breaker for sustained failures.
- **The SDK is already retrying.** Wrapping an auto-retrying SDK in your own retry loop multiplies attempts (2 × 4 = 8) and latency. Know the default and configure it rather than stacking loops.
- **Streaming can fail mid-stream.** You may have a partial response when the connection drops — decide whether to discard, resume, or surface the partial, per feature.

## Key insight

**A model call is a slow, flaky network call, and shipping AI is mostly the boring engineering around that fact.** Retry the transient failures (backoff + jitter, honor `Retry-After`), never the permanent ones; set real timeouts and stream long outputs; shape traffic to rate limits (throttle, batch, tier up) instead of just absorbing 429s; and fall back across models/providers so an outage degrades instead of dies — ideally centralizing all of it behind an AI gateway. The capability is the easy part; **making it dependable is the job.**

## Related
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — the call this note hardens
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|Cost, Caching & Latency]] — the same gateway layer, aimed at spend and speed
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — reliability is one axis of "production-ready"
- [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|MLOps: Serving & Monitoring]] — the classical-serving sibling
