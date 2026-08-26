# 06 — Cross-Cutting Concerns

The things every feature needs and no feature owns.

**~5,600 words across 7 notes.** Built August 2026 — **this section was a map pointing elsewhere until then**, and one row of that map said "file uploads — not covered anywhere yet — a genuine gap." That's note 07.

> **The one idea:** each of these is needed by **every** feature, which means each should be **solved once, centrally, and applied by convention.** When the same try/catch or the same permission check is pasted into twenty handlers, a cross-cutting concern has escaped into feature code — and that's what middleware, filters and interceptors exist to prevent.

## Reading order

1. [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] — **[Intermediate]** — **parse, don't validate**, why the boundary is the only place, and what a DTO actually protects you from
2. [[backend/06-cross-cutting/02-configuration-and-secrets|Configuration and Secrets]] — **[Intermediate]** — layering, **validating config at startup**, why secrets differ from config, and feature flags that never die
3. [[backend/06-cross-cutting/03-error-handling|Error Handling]] — **[Intermediate]** — one handler at the edge, `ProblemDetails`, the status-code map, **and the line between what the client sees and what you log**
4. [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] — **[Intermediate]** — the four algorithms, what to key on, **and why in-process limiting silently doesn't work**
5. [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — **[Intermediate]** — **a timeout doesn't tell you whether it happened**, idempotency keys, backoff with jitter, circuit breakers
6. [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers and CORS]] — **[Intermediate]** — the nearly-free headers, CSP properly, **and what CORS actually protects** (not your server)
7. [[backend/06-cross-cutting/07-file-uploads|File Uploads]] — **[Intermediate]** — presigned URLs, magic-byte validation, decompression bombs, and the checklist

## The things worth carrying

1. **After your check, can a downstream function still receive bad data?** If yes, you validated rather than parsed → [[backend/06-cross-cutting/01-validation-and-dtos|01]]
2. **Returning your database entity directly is how `passwordHash` reaches a client** → [[backend/06-cross-cutting/01-validation-and-dtos|01]]
3. **Validate all config at startup.** A container that refuses to boot beats one that fails at 3 a.m. → [[backend/06-cross-cutting/02-configuration-and-secrets|02]]
4. **A leaked secret is not fixed by deleting the commit.** Rotate first → [[backend/06-cross-cutting/02-configuration-and-secrets|02]]
5. **401 means "I don\'t know who you are"; 403 means "I know, and no."** And 403 on a resource that exists confirms it exists → [[backend/06-cross-cutting/03-error-handling|03]]
6. **Log the exception object, not `ex.Message`** → [[backend/06-cross-cutting/03-error-handling|03]]
7. **In-process rate limiting multiplies your limit by your instance count** → [[backend/06-cross-cutting/04-rate-limiting|04]]
8. **Behind a proxy you rate-limit your own load balancer** unless forwarded headers are configured → [[backend/06-cross-cutting/04-rate-limiting|04]]
9. **Three outcomes, not two: succeeded, failed, and unknown** → [[backend/06-cross-cutting/05-idempotency-and-retries|05]]
10. **Retry at one layer.** Three layers × 3 retries is 27 requests to a struggling database → [[backend/06-cross-cutting/05-idempotency-and-retries|05]]
11. **Jitter, or an outage recovery becomes a retry storm** → [[backend/06-cross-cutting/05-idempotency-and-retries|05]]
12. **CORS protects your users\' other tabs, not your server.** A CORS error means the request probably ran → [[backend/06-cross-cutting/06-security-headers-and-cors|06]]
13. **Extension and `Content-Type` are client-supplied text.** Check magic bytes → [[backend/06-cross-cutting/07-file-uploads|07]]

## Still covered elsewhere, deliberately

Not everything cross-cutting belongs here — some of it has a better home and this section links rather than duplicates:

| Concern | Where |
|---|---|
| **Caching** | [[architecture/02-building-blocks/02-caching\|caching]] — strategies, stampede, penetration |
| **Logging & observability** | [[devops/10-observability/README\|observability]] · [[backend/interview/01-production-debugging\|what to log]] |
| **Background jobs** | [[architecture/02-building-blocks/04-messaging-and-async\|messaging & async]] |
| **Auth itself** | [[backend/05-auth/README\|05-auth]] — flows, authorization, OAuth |
| **Secret storage** | [[devops/09-secret-management/README\|secret management]] |

## Per language

**These notes are stack-agnostic on purpose.** For the implementations side by side — rate limiting, auth, headers, graceful shutdown in six stacks — see **[[backend/frameworks/cross-language-recipes|cross-language recipes]]**.

## Related
- [[backend/README|Backend course]] · [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]]
- [[backend/frameworks/README|frameworks/]] · [[cybersecurity/04-web-security/README|web security]]
