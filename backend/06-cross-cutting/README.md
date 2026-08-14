# 06 — Cross-Cutting Concerns

The things every feature needs and no feature owns. **Scaffold — not yet written**, but the material mostly exists elsewhere in the vault, so this README is a map rather than a placeholder.

| Concern | Where the material is now |
|---|---|
| **Validation & DTOs** | [[backend/01-foundations/03-the-request-lifecycle\|request lifecycle]] — "parse, don't validate"; [[backend/frameworks/javascript/03-nest/README\|Nest pipes]] |
| **Configuration & secrets** | [[devops/09-secret-management/README\|secret management]]; [[backend/frameworks/javascript/01-node-runtime/01-env-validation\|env validation]] |
| **Error handling** | [[backend/interview/02-node-runtime-and-api\|Node interview Q5]]; [[backend/frameworks/javascript/01-node-runtime/02-error-handling\|Node error handler]] |
| **Logging & observability** | [[devops/10-observability/README\|observability]]; [[backend/interview/01-production-debugging\|what to log and why]] |
| **Caching** | [[architecture/02-building-blocks/02-caching\|caching]] — strategies, stampede, penetration, avalanche |
| **Background jobs & scheduling** | [[architecture/02-building-blocks/04-messaging-and-async\|messaging & async]]; [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq\|RabbitMQ]] |
| **Rate limiting** | [[architecture/interview/01-system-design-round\|system design Q2]] — algorithms and the distributed problem |
| **Idempotency & retries** | [[backend/interview/01-production-debugging\|production debugging Q5–Q6]] |
| **File uploads** | not covered anywhere yet — a genuine gap |

## Why these are grouped
Each one is needed by every feature, which means each one should be **solved once, centrally**, and applied by convention — not reimplemented per controller. That's what middleware, interceptors, and filters are *for*. When you see the same try/catch or the same permission check pasted into twenty handlers, a cross-cutting concern has escaped into feature code.

## Related
- [[backend/README|Backend course]] · [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]]
