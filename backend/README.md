# Backend — A Course, Not a Framework Tutorial

**Backend is a domain. Frameworks are different ways of building one.** This folder is organised that way: sections `01`–`07` are the course — true regardless of language — and [[backend/frameworks/README|frameworks/]] holds the implementations.

Restructured August 2026. Previously the concepts lived in `concepts/01-backend/` and this folder held only framework notes, which meant anyone looking for backend material had to know to check two places. **Navigation should follow how people read, not how the author filed things.**

## Sections

### [[backend/01-foundations/README|01 — Foundations]]
1. [[backend/01-foundations/01-what-a-backend-is|What a Backend Actually Is]] — **[Beginner]** — the four responsibilities, and "never trust the client" as the rule everything follows from
2. [[backend/01-foundations/02-http-servers|HTTP Servers]] — **[Beginner]** — how requests physically arrive
3. [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]] — **[Beginner→Intermediate]** — the nine stages, the middleware onion, symptom→stage debugging
4. [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — **[Intermediate]** ⭐ — thread-per-request vs event loop vs green threads, and **why frameworks differ at all**

### [[backend/02-api-design/README|02 — API Design]]
The contract you can't easily change. REST semantics, status codes, idempotency.

### [[backend/03-structuring-a-backend/README|03 — Structuring a Backend]] ⭐
**The heart of the course.**
1. [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers — Controllers, Services, Repositories]] — the three jobs, and the test for when you've broken them
2. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|By Layer vs by Feature]] — change locality, deletability, how `shared/` rots
3. [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency Injection & Wiring]] — be handed your tools, don't make them
4. [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — inverting the dependency, and what it honestly costs
5. [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — discover boundaries where being wrong is cheap

### [[backend/04-data-and-persistence/README|04 — Data & Persistence]]
Transactions, concurrent writes, connection pools, N+1, migrations.

### [[backend/05-auth/README|05 — Auth]]
1. [[backend/05-auth/01-authentication-flows|Authentication Flows]] · 2. [[backend/05-auth/02-authorization|Authorization]] · 3. [[backend/05-auth/03-oauth-provider-integrations|OAuth Provider Integrations]]

### [[backend/06-cross-cutting/README|06 — Cross-Cutting Concerns]]
**Built out Aug 2026 — 7 notes.** The things every feature needs and no feature owns.
1. [[backend/06-cross-cutting/01-validation-and-dtos|Validation & DTOs]] · 2. [[backend/06-cross-cutting/02-configuration-and-secrets|Config & Secrets]] · 3. [[backend/06-cross-cutting/03-error-handling|Error Handling]] · 4. [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] · 5. [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency & Retries]] · 6. [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers & CORS]] · 7. [[backend/06-cross-cutting/07-file-uploads|File Uploads]]

*Caching, observability and background jobs stay in [[architecture/02-building-blocks/README|building blocks]] and [[devops/10-observability/README|observability]] — linked, not duplicated. For the per-language implementations, see [[backend/frameworks/cross-language-recipes|cross-language recipes]].*

### [[backend/07-practices/README|07 — Practices]]
[[backend/07-practices/01-backend-best-practices|Backend best practices]].

---

## [[backend/frameworks/README|frameworks/]] — the implementations

Not numbered; there's no reading order. Pick yours.

- **[[backend/frameworks/javascript/README|JavaScript/TypeScript]]** — [[backend/frameworks/javascript/01-node-runtime/README|Node runtime]], [[backend/frameworks/javascript/02-express/README|Express]], [[backend/frameworks/javascript/03-nest/README|Nest]] — event loop
- **[[backend/frameworks/java/README|Java]]** — [[backend/frameworks/java/01-spring-boot|Spring Boot]] — thread-per-request, virtual threads from 21. Moved here from `languages/01-java/`
- **[[backend/frameworks/python/README|Python]]** — FastAPI, Django, Flask — mixed WSGI/ASGI
- **[[backend/frameworks/csharp/README|C#]]** — ASP.NET Core — async, thread pool
- **[[backend/frameworks/go/README|Go]]** — net/http, Chi, Gin — goroutines
- **[[backend/frameworks/rust/README|Rust]]** — Axum, Actix — async/tokio
- **[[backend/frameworks/cpp/README|C++]]** · **[[backend/frameworks/c/README|C]]** — when you'd actually reach for them, and when you wouldn't
- **[[backend/frameworks/cross-language-recipes|Cross-Language Recipes]]** ⭐ — **rate limiting, JWT, CORS, headers, graceful shutdown and structured logging in all six, side by side**

**Read [[backend/01-foundations/04-runtime-and-concurrency-models|note 01.4]] before any of them.** Frameworks look like twenty things to learn; they're three concurrency models wearing different vocabularies.

## [[backend/interview/README|interview/]]

**Built from a real interview** (August 2026) rather than guessed:
- [[backend/interview/01-production-debugging|Production Debugging]] — p99 spikes, per-AZ metrics, AZ impaired vs bad deploy, N+1 regressions, retry safety, retry storms
- [[backend/interview/02-node-runtime-and-api|Node Runtime & API]] — `Promise.all` at scale, `Buffer` allocation, the event loop, streams, errors

## The filing rule

- *Is it true whether you use Nest, Spring, or Axum?* → a numbered section here
- *Is it how one stack does it?* → `frameworks/<language>/<framework>/`
- *Does it belong to no domain at all* (clean code, PR structure, design patterns)? → [[concepts/README|concepts/]]
- *Is it how it went in one of my projects?* → [[projects/README|projects/]]

## Related
- [[architecture/README|Architecture]] — the same questions at system scale
- [[databases/interview/README|Databases]] · [[foundations/networking/README|Networking]] · [[devops/README|DevOps]]
- [[PRIMETECHIE|The Primetechie Path]] · [[INTERVIEW|Interview index]]
