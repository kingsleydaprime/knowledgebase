---
id: 383fe95e-d1b7-424e-b8ac-ced991608209
---

# Error Handling

> **[Intermediate]** · One handler at the edge, one response shape, and the line between what the client sees and what you log.

## The shape
<!-- bite: d8fb5a0c-6b61-4c50-b6fe-67526c201c1c -->

**Every error leaves through one place.** A central handler — middleware, an exception filter, a `ControllerAdvice` — maps thrown errors to HTTP responses.

**The alternative is try/catch in every handler**, which guarantees inconsistency: twenty endpoints, twenty error shapes, and one of them leaks a stack trace.

```
handler throws  →  central handler  →  map to status + body  →  log with context
```

## Use `ProblemDetails` (RFC 9457)
<!-- bite: a159d927-9a4c-4825-990f-8d6b3dc90b16 -->

**There is a standard, and inventing your own shape has no upside:**

```json
{
  "type": "https://example.com/problems/insufficient-funds",
  "title": "Insufficient funds",
  "status": 409,
  "detail": "Requested £120.00 but the balance is £45.30",
  "instance": "/accounts/123/withdrawals",
  "traceId": "0af7651916cd43dd8448eb211c80319c"
}
```

**Include the trace ID.** It's the single most useful field in the body — a user pastes it into a support ticket and you find the exact request in your logs → [[devops/07-observability/index|observability]].

## Mapping to status codes
<!-- bite: b29a0c25-82e7-49eb-9353-62f5657d106f -->

| Cause | Status |
|---|---|
| Malformed / failed validation | **400** |
| Not authenticated | **401** |
| Authenticated, not permitted | **403** |
| Not found | **404** |
| Method not allowed | 405 |
| Conflict — version mismatch, duplicate | **409** |
| Payload too large | 413 |
| Unprocessable — syntactically fine, semantically wrong | 422 |
| Rate limited | **429** → [[backend/06-cross-cutting/04-rate-limiting\|note 04]] |
| Unhandled | **500** |
| Dependency failed | **502 / 503 / 504** |

**401 vs 403 is the pair people get wrong.** 401 means *"I don't know who you are"* — the client should authenticate. 403 means *"I know who you are and no."* Sending 401 for a permission failure sends the client into a pointless re-login loop.

**404 vs 403 is a security decision.** Returning 403 for a resource that exists but isn't yours **confirms it exists** — that's an enumeration oracle. For sensitive resources, **return 404 for both**.

## What the client sees vs what you log
<!-- bite: 803da457-9e46-4345-8fdd-baea6226d1a6 -->

**The most important rule in this note:**

```
Client:  a stable error code, a safe message, a trace ID
Logs:    the exception, the stack trace, the inputs, the user, the trace ID
```

**Never send a stack trace, a SQL error, or an internal path to a client.** `ORA-00933` tells an attacker your database; a file path tells them your directory structure; an ORM error tells them your schema → [[cybersecurity/06-attacks-and-threats/index|attacks]].

**And never let framework debug pages reach production.** ASP.NET Core's developer exception page, Flask's debugger, Rails' error page — each is gated on an environment variable, and each has been shipped enabled.

**Log the exception object, not `ex.Message`.** The message without the stack trace is nearly useless, and this is the single most common logging mistake → [[languages/06-python/09-errors-and-exceptions|Python]] · [[languages/07-csharp/09-error-handling|C#]].

## Expected failures aren't exceptions
<!-- bite: 7a83155c-fc7d-4021-ba7f-0245b9693225 -->

**"Not found" and "invalid input" are normal operation.** Using exceptions for them is expensive (a throw costs microseconds), noisy in logs, and easy to catch too broadly.

**The pragmatic split most codebases land on:**

- **Return a result** for expected outcomes — `Order | NotFound`, `TryGet`, `Result<T>`
- **Throw** for genuinely exceptional and unrecoverable conditions

→ [[languages/02-go/05-errors|Go's errors as values]] · [[languages/03-rust/index|Rust's `Result`]] · [[languages/07-csharp/09-error-handling|the debate in C#]]

## Errors from dependencies
<!-- bite: 6e33e0a0-0bb1-4b0f-acd0-8d90d1a4fb2d -->

**Your database is down. What does the client get?**

**Not 500 by default.** Distinguish:

- **Timeout / unavailable** → **503**, with `Retry-After` if you can estimate it
- **A dependency returned a 4xx because *you* called it wrong** → **500**, because that's your bug
- **A dependency is degraded but you can serve stale data** → **200 with a staleness indicator**, which is often the best answer → [[architecture/02-building-blocks/02-caching/index|caching]]

**Don't let a dependency's error shape leak through.** Translate it. A client should never see a Stripe error object from your API.

**And bound the failure.** A slow dependency exhausts your connection pool and takes the whole service down — which is why timeouts and circuit breakers belong here → [[backend/06-cross-cutting/05-idempotency-and-retries|note 05]] · [[architecture/04-distributed-systems/index|distributed systems]].

## Stable error codes
<!-- bite: b3bc53c5-26d8-40bb-87bc-c874ecb4a668 -->

**A machine-readable code that never changes**, separate from the human message:

```json
{ "code": "INSUFFICIENT_FUNDS", "detail": "..." }
```

Clients branch on `code`. **`detail` is for humans and may be reworded or localised freely.** Clients that string-match your prose will break when you fix a typo — and some of them will.

## Related
<!-- bite: f85c7882-033a-42b5-b00a-3bd227eef1b0 -->
- [[backend/06-cross-cutting/01-validation-and-dtos|validation]] — where 400s come from
- [[backend/06-cross-cutting/04-rate-limiting|rate limiting]] — where 429s come from
- [[backend/02-api-design/index|API design]] · [[devops/07-observability/index|observability]]

*Source: [reference] — written Aug 2026.*
