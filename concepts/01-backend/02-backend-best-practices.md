# Backend Best Practices — Error Handling, Logging, Validation, Security

The practices that separate a backend that merely works from one that's actually operable in production — most of what makes an on-call rotation bearable or miserable traces back to whether these were taken seriously from the start.

## Error handling — fail predictably, not silently or catastrophically

Every error should be handled at some level — either recovered from, or turned into a clear, appropriate response, never silently swallowed (an empty `catch` block is one of the most common sources of "this is broken but nothing tells us why").

```javascript
app.use((err, req, res, next) => {           // Express-style centralized error handler
  logger.error({ err, path: req.path, userId: req.user?.id });
  if (err instanceof ValidationError) {
    return res.status(400).json({ error: err.message });
  }
  res.status(500).json({ error: "Internal server error" });   // never leak internal error details externally
});
```

A **centralized** error handler (rather than repeating try/catch-and-format logic in every route) keeps error responses consistent and makes sure nothing falls through uncaught — see `backend/nodejs/nodejs-errorhandler.md` in this vault for a concrete Node/Express implementation of exactly this pattern.

## Logging — what you'll actually need during an incident

Logs are for future-you (or whoever's on call) trying to reconstruct what happened during an incident, often under time pressure — write them with that reader in mind, not as an afterthought.

- **Structured logging** (JSON, not free-text strings) — machine-parseable, so logs can actually be searched/filtered/aggregated at scale rather than grepped by hand.
- **Log levels** (debug/info/warn/error) — so verbosity can be tuned per environment without changing code, and so a genuine error doesn't get lost in routine debug noise.
- **Correlation IDs** — a unique ID generated per request and included in every log line related to it, so a single request's full journey through multiple services/log lines can be traced together, especially valuable once a system involves more than one service.

```javascript
logger.info({ correlationId: req.id, userId: req.user?.id, action: "order.created", orderId: order.id });
```

Never log secrets (passwords, tokens, full credit card numbers) — logs frequently have looser access control than the primary database, and a leaked log is a surprisingly common real-world way sensitive data ends up exposed (see [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]] on key/secret handling generally).

## Validation — at the boundary, every time

Every input crossing into your system (request bodies, query parameters, even values from a message queue) should be validated against an explicit schema before being trusted anywhere — see [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]] for why this matters from a security angle specifically, not just a correctness one.

```javascript
const schema = z.object({
  email: z.string().email(),
  age: z.number().int().positive().max(120),
});
const result = schema.safeParse(req.body);
if (!result.success) return res.status(400).json({ errors: result.error.issues });
```

Validating environment configuration at startup (see `backend/nodejs/node-env-validation.md` in this vault) is the exact same principle applied to configuration instead of request data — fail loudly and immediately if something required is missing, rather than failing confusingly deep inside unrelated business logic minutes or hours later.

## Security basics that belong in every backend, not just "security-focused" ones

- Rate limiting on authentication and other sensitive endpoints (see [[05-authentication-flows|authentication-flows]]).
- HTTPS everywhere, never plain HTTP for anything handling real data (see [[03-https-and-tls|https-and-tls]]).
- Dependency updates — a backend's own code being secure doesn't help if a dependency it pulls in has a known vulnerability; keeping dependencies current (and knowing what's in your dependency tree at all) is part of this list, not a separate concern.
- Secrets (API keys, database credentials, signing keys) belong in a secrets manager or environment variables, never hardcoded or committed to source control.

## Gotchas

- Returning raw internal error messages/stack traces to an external client is both an information-disclosure risk (it can reveal internal implementation details useful to an attacker) and just poor API design — return a generic message externally, log the full detail internally.
- Logging too much (every field of every request, indiscriminately) creates its own problem: expensive storage, noisy search results, and a much larger surface area for sensitive data to accidentally leak into logs.
- Validation done only on the client side, mirroring the same mistake covered in [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]], provides no actual protection — server-side validation is non-negotiable regardless of what the client already checks.

## Related
- [[01-http-servers|http-servers]]
- [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]
- [[05-authentication-flows|authentication-flows]]
