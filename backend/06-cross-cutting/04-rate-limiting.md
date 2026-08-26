# Rate Limiting

> **[Intermediate]** · The four algorithms, what to key on, and why doing it in-process silently doesn't work.

**Rate limiting protects a shared resource from any single consumer** — deliberate abuse, an accidental infinite loop in someone's client, or a retry storm you caused yourself.

## The four algorithms

**Fixed window** — count requests per calendar minute; reset at the boundary.
✓ Trivial, one counter.
✗ **The boundary burst**: 100 requests at 11:59:59 and 100 at 12:00:00 is 200 in one second, all "within limit."

**Sliding window log** — store a timestamp per request; count those inside the window.
✓ Exact.
✗ Memory proportional to request count. Expensive at scale.

**Sliding window counter** — weight the previous window's count by how far into the current one you are.
✓ **Close to exact, cheap.** The common production choice.

**Token bucket** — tokens refill at a fixed rate up to a capacity; each request spends one.
✓ **Allows bursts up to the capacity**, then settles to the refill rate. Usually what you actually want — a client doing 10 requests at once then idling is fine.
✗ Two parameters to tune.

**Leaky bucket** — requests queue and drain at a constant rate. Smooths output; adds latency.

**The default recommendation: token bucket**, because real clients are bursty and punishing that is user-hostile.

## What to key on

**Getting this wrong makes the limiter either useless or an outage:**

| Key | Use for | Watch out |
|---|---|---|
| **API key / user ID** | Authenticated APIs. **The best key** | Needs auth to run first |
| **IP address** | Anonymous endpoints | **NAT and mobile carriers share IPs** — you'll limit a whole office |
| IP + endpoint | Login, password reset | |
| **Global** | Protecting a fragile dependency | Blunt |

**Limit expensive endpoints separately.** A search endpoint hitting the database and a static health check should not share a budget.

**Behind a proxy, the client IP is the proxy's** unless you configure forwarded headers — so you rate-limit your own load balancer and either block everyone or nobody. **And `X-Forwarded-For` is client-controlled**: trust it only from proxies you control, and take the right entry in the chain → [[devops/08-networking-and-web/README|networking and web]].

## In-process doesn't work

**The mistake that looks fine in staging.** An in-memory limiter is per-instance:

```
limit 100/min, 4 instances behind a load balancer
→ the actual limit is 400/min
→ and it changes when you autoscale
```

**Worse, it's inconsistent:** a client's requests land on different instances, so behaviour depends on load-balancer hashing.

**The fix is shared state — Redis, normally.** An atomic increment-and-expire, or a Lua script for token bucket:

```
INCR key
EXPIRE key 60 NX        -- only set TTL on first increment
```

**Do it atomically.** `GET` then `SET` races under concurrency and lets bursts through → [[databases/09-mvcc-and-concurrency-control|concurrency]].

**In-process is legitimate in exactly two cases:** a single-instance service, or a *second* layer protecting one instance from local overload beneath a distributed limiter.

## The response

```http
HTTP/1.1 429 Too Many Requests
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 42
Retry-After: 42
```

**`Retry-After` is the important one** — without it clients guess, and they guess badly.

**Return the headers on successful responses too**, so a well-behaved client can slow down *before* being blocked rather than discovering the wall.

## Where it goes

**Layered, because each layer catches what the one below can't:**

1. **CDN / WAF** — volumetric attacks. Never reaches you
2. **Load balancer / API gateway** — coarse per-IP limits
3. **Application** — per-user, per-endpoint business limits
4. **The dependency itself** — a connection pool cap is a rate limit

**Put crude limits as far out as possible.** Rate limiting in your application still costs you a request, a thread and a Redis round trip — so it cannot protect you from a genuine flood.

## Adjacent, and often confused

**Throttling** — slowing rather than rejecting.
**Quotas** — a longer-window budget (per day/month), usually billing-related.
**Concurrency limits** — *simultaneous* requests, not rate. Often the more useful control for expensive endpoints.
**Load shedding** — dropping requests when *you* are overloaded, regardless of who sent them. **A rate limiter protects against one client; load shedding protects against all of them** → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]].

**Backpressure** is the general form: signal upstream to slow down rather than accepting work you can't do.

## Getting it wrong

**Limits set by guessing.** Measure normal usage first; set the limit above the 99th percentile of legitimate traffic.

**No exemptions.** Health checks, internal services and your own monitoring should not be limited by the public policy.

**Rate limiting authentication too loosely** — brute-forcing passwords is exactly what this prevents. **Limit by account *and* by IP**, or an attacker rotates IPs against one account → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]].

**Retries without jitter**, which turns a limit into a synchronised stampede → [[backend/06-cross-cutting/05-idempotency-and-retries|note 05]].

## Related
- [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]] — the client side
- [[backend/frameworks/cross-language-recipes|cross-language recipes]] — implementations
- [[architecture/interview/01-system-design-round|system design]] — the distributed problem
- [[architecture/02-building-blocks/README|building blocks]]

*Source: [reference] — written Aug 2026.*
