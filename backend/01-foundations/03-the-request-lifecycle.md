# The Request Lifecycle

**[Beginner→Intermediate]** — what happens between "a request arrives" and "a response leaves," in the order it happens. Every framework implements these stages; only the names differ. Learn the stages and you can read any framework's docs in an afternoon.

## The kid version first

A letter arrives at a big office. Before it reaches the person who answers it, it passes through a series of desks:

security (are you allowed in the building?) → the mailroom (which department?) → a clerk (is this form filled in correctly?) → **the person who actually answers** → and then back out past a desk that puts it in an envelope and stamps it.

Every backend framework is that corridor of desks. The desks are **middleware**; the person at the end is your **handler**.

## The stages

```
request
   │
   ├─ 1. accept + parse        server: TCP → HTTP message
   ├─ 2. global middleware     logging, request id, CORS, body parsing, rate limit
   ├─ 3. routing               match method + path → a handler
   ├─ 4. auth                  who are you (authn) → may you (authz)
   ├─ 5. validation            is the input well-formed? → DTO
   ├─ 6. HANDLER               controller → service → repository
   ├─ 7. serialisation         domain object → JSON, hide internal fields
   ├─ 8. error mapping         domain error → status code
   └─ 9. response middleware   compression, headers, access log, metrics
response
```

**1. Accept and parse.** The server accepts a TCP connection and parses the HTTP message. Usually not your code — but it's where body-size limits, header limits, and keep-alive live, and those are security controls. → [[foundations/networking/06-tcp-connection-lifecycle|TCP]] · [[foundations/networking/11-http-evolution|HTTP]]

**2. Global middleware.** Runs for every request. Assign a **correlation ID here, first** — everything downstream logs it, and without it you cannot follow one request through your logs. Also: CORS, body parsing (with a size cap), compression, rate limiting.

**3. Routing.** Match method + path to a handler, extract path parameters. Frameworks differ in mechanism (decorators, a router object, file-system routing) and not in effect.

**4. Authentication, then authorization.** Two distinct things, in that order. **Authn** establishes identity (session cookie, bearer token, mTLS). **Authz** decides permission — and it must be re-checked at the *data* layer too, because route-level checks can't know whether *this* user owns *that* record. That gap is IDOR. → [[backend/05-auth/README|auth]]

**5. Validation.** Parse the input into a typed object and reject what doesn't fit. **Validate at the boundary, once** — after this line, code should be able to trust its inputs.

The rule that matters: **parse, don't validate.** Don't check a blob and pass the blob along; convert it into a type that *cannot* hold invalid data. `CreateOrderDto` with a validated `quantity: PositiveInt` beats `if (body.quantity > 0)` followed by passing `body` around, because the type now carries the guarantee.

**6. The handler.** Controller → service → repository. This is the only stage that's about *your product*; everything else is plumbing. → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]]

**7. Serialisation.** Domain object → response body. **This is where data leaks happen** — returning a user entity that still has `passwordHash` or `internalNotes` on it. Use an explicit response DTO or an allowlist; never `return user`.

**8. Error mapping.** One place that turns domain errors into HTTP responses:

```ts
OutOfStockError   → 409 Conflict
NotFoundError     → 404
ValidationError   → 422
UnauthorizedError → 401
(anything else)   → 500, log the detail, return a generic message + request id
```
Because this exists, services can throw meaningful domain errors and stay ignorant of HTTP. **Never leak a stack trace to the client** — it's information disclosure.

**9. Response middleware.** Compression, cache headers, access log, metrics. Record **status, route (the *template*, not the raw path), and duration** — raw paths create unbounded metric cardinality and will take down your metrics backend.

## Middleware: the one mental model

Middleware is an **onion**, not a queue. Each layer can act on the way in *and* on the way out:

```
  timing  ─┐                                     ┌─ record duration
    auth   ─┐                                   ┌─ (nothing)
   handler  ●  ← the request reaches the middle
```

```ts
async function timing(req, res, next) {
  const start = performance.now();     // on the way in
  await next();                         // everything inside
  metrics.observe(performance.now() - start);   // on the way out
}
```

Three consequences worth knowing:
- **Order matters enormously.** Body parsing before validation. Rate limiting before auth (so unauthenticated floods are cheap to reject). Error handling registered so it wraps everything.
- **An error thrown inside skips the remaining inward layers** but should still unwind through the outward ones — which is why the error handler goes outermost.
- **Anything registered globally runs on every request, including your health check.** Heavy global middleware is a latency tax on 100% of traffic.

## Where requests actually go wrong

| Symptom | Stage | Cause |
|---|---|---|
| Works in Postman, fails in browser | 2 | CORS/preflight |
| Large uploads fail | 1 | body size limit (or a proxy's, upstream) |
| Validation decorators silently ignored | 5 | the validation pipe was never applied — decorators are inert alone |
| Extra fields reach the database | 5 | no allowlist/whitelist on the DTO — mass assignment |
| Password hash in a response | 7 | returning the entity instead of a DTO |
| Every response is 500 | 8 | domain errors unmapped |
| Logs can't be correlated | 2 | no request ID assigned first |
| One slow endpoint stalls everything | 6 | blocking the event loop, or pool exhaustion → [[backend/interview/01-production-debugging\|p99 debugging]] |

## Key insight

The lifecycle is **a funnel of decreasing distrust.** At stage 1 you trust nothing — bytes from a stranger. Each stage removes one class of doubt: is it well-formed, who are you, may you, is the input valid. By stage 6 your business logic can operate on trusted, typed data and think about the *product* instead of the attacker. **When a backend feels tangled, it's usually because that funnel is out of order** — validation after the handler, authorization inside the repository, error mapping scattered through controllers.

## Related
- [[backend/01-foundations/02-http-servers|HTTP Servers]] — the layer underneath
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — how stage 6 executes, and why frameworks differ
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — what stage 6 looks like inside
- [[cybersecurity/04-web-security/README|Web Security]] — the attacks each stage defends against
