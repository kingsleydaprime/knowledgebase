# Idempotency and Retries

> **[Intermediate]** · Networks lose responses, not just requests — and everything here follows from that one fact.

## The problem

**A timeout does not tell you whether the operation happened.**

```
client → POST /payments → server: charges the card
client ← ✗ timeout ←──────────────  response lost in transit
```

The client sees a failure. **The charge went through.** If it retries, the customer is charged twice.

**This is not an edge case.** Any distributed call has three outcomes, not two: succeeded, failed, and **unknown**. The third is the one that needs designing for → [[architecture/04-distributed-systems/README|distributed systems]].

## Idempotency

**An operation is idempotent if performing it twice has the same effect as performing it once.**

| | Idempotent? |
|---|---|
| `GET /orders/1` | ✓ |
| `PUT /orders/1 {status: "paid"}` | ✓ — absolute value |
| `DELETE /orders/1` | ✓ — second one is a no-op (return 204 or 404, consistently) |
| `POST /orders` | ✗ — creates a new one each time |
| `PATCH /accounts/1 {balance: +10}` | ✗ — **relative change** |

**Two design rules that make most of this go away:**

**Prefer absolute values to increments.** "Set status to `paid`" is safe repeated; "add £10" is not.

**Make `PUT` and `DELETE` genuinely idempotent**, per the HTTP spec. Plenty of APIs don't, and clients that trust the spec then break → [[backend/02-api-design/01-apis-and-rest|APIs and REST]].

## Idempotency keys

**For operations that are inherently not idempotent — creating a payment, sending an email — the client supplies a key:**

```http
POST /payments
Idempotency-Key: 8f14e45f-ea6a-4d1f-9f2a-9b1c3d4e5f60
```

**The server:**
1. Looks up the key. **Found and complete?** Return the stored response — do not re-execute
2. **Found and in progress?** Return **409**, or wait
3. **Not found?** Record the key as in-progress, execute, store the response against the key, return it

**Three details that decide whether it actually works:**

**The client generates the key**, once, and reuses it across retries. A key generated per attempt does nothing.

**Store the key and the result in the same transaction as the work.** If the charge commits and the key doesn't, you've built an elaborate no-op → [[databases/08-transactions-and-acid|transactions]].

**Expire keys** — 24 hours is typical. Storing them forever is a slow leak.

**Stripe's implementation is the reference**, and worth reading rather than reinventing.

## Retries

**Retry only what's safe to retry:**

| | Retry? |
|---|---|
| Timeout | **Only if idempotent** |
| 429 | **Yes** — honour `Retry-After` |
| 500, 502, 503, 504 | Yes, with backoff |
| Connection refused / reset | Yes |
| 400, 401, 403, 404, 422 | **No.** Retrying won't change the answer |
| 409 | Usually no — resolve the conflict |

**Exponential backoff with jitter**, a maximum attempt count, and a cap:

```
attempt 1 → wait ~1s
attempt 2 → wait ~2s
attempt 3 → wait ~4s
give up
```

**Jitter is the part that gets omitted and the part that matters at scale.** Without it, every client that failed during an outage retries in lockstep the instant recovery starts — and knocks the service over again. **That's a retry storm, and it turns a 30-second blip into a 20-minute outage** → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]].

**Full jitter** — `sleep = random(0, min(cap, base * 2^attempt))` — is the standard, and it beats "backoff plus a small random" measurably.

## Retry amplification

**The failure mode that catches teams with retries at every layer:**

```
gateway retries 3× → service A retries 3× → service B retries 3×
                   = 27 requests to the database
```

**A struggling dependency now receives 27× its normal load, precisely when it can least handle it.**

**Retry at one layer.** Usually the one closest to the failure, or the outermost. **Not both.** And make it explicit in your architecture which layer owns retries → [[architecture/04-distributed-systems/README|distributed systems]].

## Circuit breakers

**When a dependency is failing, stop calling it.**

```
CLOSED  → failures exceed threshold → OPEN
OPEN    → all calls fail immediately, no network attempt
        → after a cooldown → HALF-OPEN
HALF-OPEN → allow a few probes → success? CLOSED. failure? OPEN
```

**Two things this buys you:** you fail fast instead of waiting on timeouts (so your threads aren't all blocked on a dead service), and **you stop hammering something that's trying to recover.**

**Pair it with a timeout and a bulkhead** — a bounded pool per dependency, so one slow downstream can't consume every connection you have. **"Slow" is worse than "down"**: a down dependency fails fast; a slow one exhausts your pool and takes you with it.

Libraries: Polly (.NET), resilience4j (Java), `tower` middleware (Rust), `gobreaker` (Go), `cockatiel` (Node).

## Exactly-once doesn't exist

**Worth stating plainly, because the phrase appears in marketing:**

Message delivery gives you **at-most-once** or **at-least-once**. Not both. "Exactly-once processing" is achieved by **at-least-once delivery plus idempotent processing** — which is to say, by everything above.

**So: assume duplicates, and design the handler to tolerate them.** That's the whole answer → [[architecture/02-building-blocks/04-messaging-and-async|messaging and async]].

## Related
- [[backend/06-cross-cutting/04-rate-limiting|rate limiting]] — the server side of the same pressure
- [[backend/06-cross-cutting/03-error-handling|error handling]] — which failures are retryable
- [[architecture/04-distributed-systems/README|distributed systems]]
- [[ai-automation/05-error-handling-and-retries|the same problem in workflow automation]]

*Source: [reference] — written Aug 2026.*
