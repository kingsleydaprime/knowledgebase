# direct-debit-sandbox-java — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). A Spring Boot sandbox that simulates a direct-debit provider —
subscriptions, mandates, preauthorizations, callbacks, retries — without a real bank behind it.

This is a strong **Java/Spring backend** interview project because it's full of real API-design
decisions (idempotency, state machines, config-once patterns, error-code conventions) rather than
CRUD.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked.

## Files

| File | Covers |
|---|---|
| [01-java-and-spring-boot.md](01-java-and-spring-boot.md) | Java fundamentals in context, DI, the three layers, validation, interceptors, Lombok/builder |
| [02-domain-and-api-design.md](02-domain-and-api-design.md) | Provision pattern, scenario engine, subscriptions vs mandates vs preauth, error-code convention |
| [03-storage-async-and-retries.md](03-storage-async-and-retries.md) | `ConcurrentHashMap`, secondary indexes, composite keys, `@Async`, `@Scheduled`, the retry state machine |
| [04-api-docs-and-story.md](04-api-docs-and-story.md) | OpenAPI/springdoc, Swagger UI, the custom docs portal, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> A Spring Boot sandbox that lets a merchant integrate against a direct-debit API before any real
> bank is involved. It handles subscriptions, mandates and preauthorizations, fires asynchronous
> callbacks, and drives failed debits through a retry state machine on a scheduler. The design
> ideas I'd defend: the **scenario engine** — the last three digits of the debit account determine
> the outcome, so a tester can deterministically trigger "insufficient funds" or "timeout" by
> choosing an account number, no bank cooperation required; and the **provision pattern** — a
> merchant registers their callback URL and catalogue config once for a `merchantId + productId`
> pair instead of repeating it on every one of a thousand requests. It follows the banking
> convention of returning HTTP 200 with a business `responseCode` in the body rather than 4xx, so
> clients handle one error path, not two.

Lead with the scenario engine. It's the idea most interviewers won't have seen and it explains the
entire purpose of a sandbox in one sentence.
