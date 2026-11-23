# Axum (Rust Backend)

## What Axum is

**Axum is a framework for building web servers in Rust.** It is very fast, and it catches many mistakes before the code ever runs.

**Concurrency model: async/await on a runtime (usually tokio)** — green threads with explicit colouring. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~12,000 words across 6 notes.** `[reference]` — no Rust service in this vault yet. Assumes [[languages/03-rust/index|the Rust course]] and the [[backend/index|backend course]]; these cover only what those don't.

> **The thing Rust does that no other stack here structurally can:** a handler taking `AuthUser` as a parameter **cannot be called unauthenticated.** Not "shouldn't" — there is no path into the function body that skips the extractor. Authorisation bugs are a top-3 cause of real breaches and they're usually "this endpoint forgot the check". Here, forgetting it is a compile error. → [[backend/frameworks/axum/02-routing-and-extractors|note 02]]

## Lessons so far

1. [[backend/frameworks/axum/01-what-axum-is-and-a-first-server|01 — What Axum Is, and Your First Server]] — **[Beginner → Intermediate]**
2. [[backend/frameworks/axum/02-routing-and-extractors|02 — Routing and Extractors]] — **[Beginner → Intermediate]**
3. [[backend/frameworks/axum/03-middleware|03 — Middleware]] — **[Intermediate]**
4. [[backend/frameworks/axum/04-structuring-an-axum-service|04 — Structuring an Axum Service]] — **[Intermediate]**
5. [[backend/frameworks/axum/05-state-and-dependency-injection|05 — State and Dependency Injection]] — **[Intermediate → Advanced]**
6. [[backend/frameworks/axum/06-validation|06 — Input Validation]] — **[Intermediate]**
7. [[backend/frameworks/axum/07-errors|07 — Errors and Structured Responses]] — **[Intermediate → Advanced]**
8. [[backend/frameworks/axum/08-data-with-postgres|08 — Data with PostgreSQL]] — **[Intermediate → Advanced]**
9. [[backend/frameworks/axum/09-listing|09 — Pagination, Filtering, Searching, Sorting and Field Selection]] — **[Intermediate → Advanced]**
10. [[backend/frameworks/axum/10-versioning|10 — Versioning]] — **[Advanced]**
11. [[backend/frameworks/axum/11-api-docs|11 — API Docs]] — **[Intermediate]**
12. [[backend/frameworks/axum/12-authentication|12 — Authentication]] — **[Advanced]**
13. [[backend/frameworks/axum/13-authorization|13 — Authorization]] — **[Advanced]**
14. [[backend/frameworks/axum/14-security|14 — Security]] — **[Advanced]**
15. [[backend/frameworks/axum/15-idempotency|15 — Idempotency]] — **[Advanced]**
16. [[backend/frameworks/axum/16-testing|16 — Testing]] — **[Intermediate → Advanced]**
17. [[backend/frameworks/axum/17-payments-and-webhooks|17 — Payments and Webhooks]] — **[Advanced]**
18. [[backend/frameworks/axum/18-background-jobs|18 — Background Jobs and Queues]] — **[Advanced]**
19. [[backend/frameworks/axum/19-caching|19 — Caching]] — **[Advanced]**
20. [[backend/frameworks/axum/20-real-time|20 — Real-time Updates]] — **[Advanced]**
21. [[backend/frameworks/axum/21-graphql|21 — GraphQL]] — **[Advanced]**
22. [[backend/frameworks/axum/22-grpc|22 — gRPC]] — **[Advanced]**
23. [[backend/frameworks/axum/23-mcp-server|23 — Building an MCP Server]] — **[Advanced]**
24. [[backend/frameworks/axum/24-mcp-in-production-1|24 — MCP in Production 1: Logging In]] — **[Advanced]**
25. [[backend/frameworks/axum/25-mcp-in-production-2|25 — MCP in Production 2: The Door and the Person's Permissions]] — **[Advanced]**
26. [[backend/frameworks/axum/26-mcp-in-production-3|26 — MCP in Production 3: Quotes and Asking the Person]] — **[Advanced]**
27. [[backend/frameworks/axum/27-mcp-in-production-4|27 — MCP in Production 4: Prompt Injection and Limits]] — **[Advanced]**
28. [[backend/frameworks/axum/28-mcp-in-production-5|28 — MCP in Production 5: Trying It and Testing]] — **[Advanced]**
29. [[backend/frameworks/axum/29-splitting-out-a-microservice-1|29 — Splitting Out a Microservice 1: Should You, and Where the Line Goes]] — **[Advanced]**
30. [[backend/frameworks/axum/30-splitting-out-a-microservice-2|30 — Splitting Out a Microservice 2: Events and the Outbox]] — **[Advanced]**
31. [[backend/frameworks/axum/31-splitting-out-a-microservice-3|31 — Splitting Out a Microservice 3: Streams and Readers]] — **[Advanced]**
32. [[backend/frameworks/axum/32-splitting-out-a-microservice-4|32 — Splitting Out a Microservice 4: The Notifications Service]] — **[Advanced]**
33. [[backend/frameworks/axum/33-calling-services-safely-1|33 — Calling Services Safely 1: Deadlines, Retries and the Breaker]] — **[Advanced]**
34. [[backend/frameworks/axum/34-calling-services-safely-2|34 — Calling Services Safely 2: Who's Calling?]] — **[Advanced]**
35. [[backend/frameworks/axum/35-observability-1|35 — Observability 1: Logs]] — **[Advanced]**
36. [[backend/frameworks/axum/36-observability-2|36 — Observability 2: Following One Action]] — **[Advanced]**
37. [[backend/frameworks/axum/37-observability-3|37 — Observability 3: Metrics and Alerts]] — **[Advanced]**
38. [[backend/frameworks/axum/38-async-pitfalls-in-production|38 — Async Pitfalls in Production]] — **[Advanced]**
39. [[backend/frameworks/axum/39-config-secrets-and-health|39 — Config, Secrets and Health]] — **[Advanced]**
40. [[backend/frameworks/axum/40-docker|40 — Docker]] — **[Advanced]**
41. [[backend/frameworks/axum/41-ci-and-deployment|41 — CI and Deployment]] — **[Advanced]**

## What's genuinely different here

**Middleware is `tower::Layer`** — the same abstraction gRPC tooling and database pools use, so retries, timeouts and rate limits are reusable across protocols rather than framework-specific.

**Extractors mean "parse, don't validate" is enforced.** By the time your handler's first line runs, the path parameter is a `u64` and the body is a validated struct. Anything that failed never reached you.

**Transactions roll back via `Drop`.** An early `?` return rolls back automatically — no `defer`, no `finally`. RAII applied to database transactions.

**`Router` is a `Service`, so `oneshot` tests the whole stack** — middleware included — with no network and no port. The neatest testing story of the four stacks here.

## What it costs

- **Development speed.** A CRUD endpoint takes meaningfully longer than in Go or Spring Boot
- **Compile times.** Minutes for a clean build
- **Async complexity.** Function colouring, `Send` bounds, cancellation safety, `Pin` in error messages
- **Blocking is unforgiving.** Go's runtime detaches a thread on a blocking syscall; tokio cannot. One `std::fs::read` in a handler stalls a worker
- **Ecosystem gaps** in business-domain libraries — payments, enterprise auth, reporting

## Axum next to Actix Web

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros |
| Ecosystem reuse | high | lower |
| Model | shared state | thread-per-core |

**Axum is the current default**, mostly for `tower` compatibility. Actix is mature, marginally faster, and a fine choice → [[backend/frameworks/actix-web/index|Actix Web]].

## The honest verdict

Note 06 argues this properly. The short version: **for an ordinary CRUD service with a team of five and a deadline, Rust is usually the wrong tool** — [[languages/02-go/index|Go]] gets you most of the operational benefit at a fraction of the cost.

Rust is unambiguously right for **infrastructure many services depend on**: proxies, databases, data pipelines, CLI tooling, anything with a latency SLO a GC can't meet. That's where the performance amortises and the correctness guarantees pay for themselves.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Axum way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson, or a few numbered parts when a topic is too big for one sitting. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. [[backend/frameworks/axum/01-what-axum-is-and-a-first-server|01 — What Axum Is, and Your First Server]]: the Tokio, hyper, Tower and Axum layers, handlers as plain async functions, graceful shutdown, and why `axum::serve` has no timeout for slow clients.
2. [[backend/frameworks/axum/02-routing-and-extractors|02 — Routing and Extractors]]: the menu as REST routes, `Path`, `Query`, `Json` and `State`, a menu behind `Arc<Mutex<>>`, and the two compile errors everyone meets.
3. [[backend/frameworks/axum/03-middleware|03 — Middleware]]: `from_fn` middleware, logging with `tracing`, `CatchPanicLayer`, a staff key with `route_layer`, and why the last layer added is the outermost.
4. [[backend/frameworks/axum/04-structuring-an-axum-service|04 — Structuring an Axum Service]]: a library crate beside `main`, a module per feature with a model, store, service and handlers, `pub use` as each feature's front counter, error enums that become status codes in one place, orders, and why Rust allows cycles between modules.
5. [[backend/frameworks/axum/05-state-and-dependency-injection|05 — State and Dependency Injection]]: stores as traits behind `Arc<dyn>`, the "not dyn compatible" error, the clock as a dependency and a shop-hours rule, one `AppState` with `FromRef`, `main` as the composition root, first unit tests, and locking decisions.
6. [[backend/frameworks/axum/06-validation|06 — Input Validation]]: `deny_unknown_fields`, `validator` rules reported all at once, a `ValidatedJson` extractor of our own, a body limit, and the line between the door and the service.
7. [[backend/frameworks/axum/07-errors|07 — Errors and Structured Responses]]: one `ApiError` reached with `From` and `?`, problem details written in one middleware, request IDs on every response and log line, JSON for unknown routes, panics and timeouts, `{"data": ...}`, and the layer stack with `ServiceBuilder`.
8. [[backend/frameworks/axum/08-data-with-postgres|08 — Data with PostgreSQL]]: Postgres in a container, migrations with sqlx, queries the compiler checks against the real schema, async store traits with `async_trait`, the last plate in a guarded `UPDATE` inside a transaction that rolls back on `Drop`, and `#[sqlx::test]`.

**Part 2: designing the API properly**

9. [[backend/frameworks/axum/09-listing|09 — Pagination, Filtering, Searching, Sorting and Field Selection]]: a `ValidatedQuery`, an enum allowlist for sort and fields, dynamic SQL with `QueryBuilder`, safe `ILIKE` search with a trigram index, offset pages for the menu and cursor pages for the kitchen.
10. [[backend/frameworks/axum/10-versioning|10 — Versioning]]: breaking changes, prices in kobo, domain and wire types, handlers written once and generic over a `MenuVersion` trait, v1 and v2 side by side, and deprecating v1 with `Sunset` and a 410.
11. [[backend/frameworks/axum/11-api-docs|11 — API Docs]]: OpenAPI from the real v2 types with utoipa, routes described on empty functions because the handlers are generic, a Scalar docs page, and a test that sends every documented operation to the real app.

**Part 3: who can do what**

12. [[backend/frameworks/axum/12-authentication|12 — Authentication]]: argon2id on `spawn_blocking`, short HS256 JWTs with the algorithm pinned, rotating refresh tokens that catch theft, an `AuthUser` extractor, and v2 orders needing a login through the version's `Customer` type.
13. [[backend/frameworks/axum/13-authorization|13 — Authorization]]: a policy as one tested `match`, permissions as types with `Can<P>`, a kitchen guard per version as a generic associated type, ownership answering 404, lists scoped in SQL, and safe role changes.
14. [[backend/frameworks/axum/14-security|14 — Security]]: security headers and a docs-page CSP, CORS from the environment, a token-bucket rate limit on password routes, the client's real address behind a proxy, and photo uploads checked by their bytes.
15. [[backend/frameworks/axum/15-idempotency|15 — Idempotency]]: `Idempotency-Key` claimed in one statement, a middleware that runs once and replays, refusals released, stale claims taken over, and a unique index so a crash can't make two orders.
16. [[backend/frameworks/axum/16-testing|16 — Testing]]: integration tests in `tests/` with one `TestApp` (a stopped clock, a fresh database), `oneshot` through the whole router, a role-by-route permission table, concurrent orders with `join_all`, and mutation checks.

**Part 4: what real products need**

17. [[backend/frameworks/axum/17-payments-and-webhooks|17 — Payments and Webhooks]]: a Paystack client on `reqwest` with a timeout under the app's own, one `settle` guarded in SQL, webhook signatures checked on raw `Bytes`, the verify call as a backup, paid before cooked, and signed webhooks to Okada Riders from a Postgres queue with backoff and jitter.
18. [[backend/frameworks/axum/18-background-jobs|18 — Background Jobs and Queues]]: jobs in Postgres with apalis, added in the same transaction as the change they're about, a worker program with a worker per queue, Tower concurrency and retry layers, hopeless jobs that stop, delayed jobs, a timetable that runs once however many workers run it, and polite shutdown.
19. [[backend/frameworks/axum/19-caching|19 — Caching]]: the menu in Redis through a lazy connection with short timeouts, a cache that fails open, one load per stampede, generations to keep it honest, `ETag` and 304, `no-store` for anything personal, and a login limit shared across servers.
20. [[backend/frameworks/axum/20-real-time|20 — Real-time Updates]]: a kitchen screen on server-sent events that starts from a snapshot, a broadcast hub that cuts off lagging screens, Postgres `NOTIFY` sent in the same transaction as the news, one-use stream tickets, and a WebSocket for a customer's own order.

**Part 5: other ways to talk**

21. [[backend/frameworks/axum/21-graphql|21 — GraphQL]]: code-first types with async-graphql calling the same services as REST, a per-request dataloader against N+1, REST's error codes inside GraphQL errors, depth and complexity limits, and a published `schema.graphql` checked by a test.
22. [[backend/frameworks/axum/22-grpc|22 — gRPC]]: a `.proto` contract compiled in `build.rs` with protox, a tonic service on the same `MenuService` beside the HTTP server, health and reflection, REST's error codes as gRPC statuses with `ErrorInfo`, a stream of stock changes from the hub, and what does and doesn't end a stream.
23. [[backend/frameworks/axum/23-mcp-server|23 — Building an MCP Server]]: read-only menu tools with rmcp, whose names, doc comments and schemas are what the model reads, results and errors shaped for a model, a resource and a prompt, and Streamable HTTP inside the Axum app with allowed hosts.
24. [[backend/frameworks/axum/24-mcp-in-production-1|24 — MCP in Production 1: Logging In]]: the MCP OAuth flow and the metadata clients read, fetching the authorization server's keys safely, checking access tokens to the last claim, and always acting as a customer.
25. [[backend/frameworks/axum/25-mcp-in-production-2|25 — MCP in Production 2: The Door and the Person's Permissions]]: a token check in front of rmcp, the 401 clients expect, the person handed to tools by an extractor of our own, and scopes on top of the services' own policy.
26. [[backend/frameworks/axum/26-mcp-in-production-3|26 — MCP in Production 3: Quotes and Asking the Person]]: three layers so a model can't spend money on a guess: no payment by the AI, one-use quotes, and a question the person answers, even on a server with no sessions.
27. [[backend/frameworks/axum/27-mcp-in-production-4|27 — MCP in Production 4: Prompt Injection and Limits]]: keeping power out of text, a per-person call limit, a fail-closed daily cap, and a record of where every order came from.
28. [[backend/frameworks/axum/28-mcp-in-production-5|28 — MCP in Production 5: Trying It and Testing]]: a pretend authorization server, a real order by hand over the 2026-07-28 protocol, and tests with signed tokens and hosts that confirm, decline or can't ask.

**Part 6: more than one service**

29. [[backend/frameworks/axum/29-splitting-out-a-microservice-1|29 — Splitting Out a Microservice 1: Should You, and Where the Line Goes]]: when a second service is worth it, a Cargo workspace with the API as its root package, a boundary the compiler enforces and a test that guards it, and a database of its own.
30. [[backend/frameworks/axum/30-splitting-out-a-microservice-2|30 — Splitting Out a Microservice 2: Events and the Outbox]]: events as a versioned contract in a shared crate, the outbox written in the same transaction as the change, and a relay that never loses an event or doubles one in the stream.
31. [[backend/frameworks/axum/31-splitting-out-a-microservice-3|31 — Splitting Out a Microservice 3: Streams and Readers]]: a JetStream stream, durable readers shared by copies of a service, done, try-again-later and never-again answers, and Okada's webhooks fed from the stream once per event.
32. [[backend/frameworks/axum/32-splitting-out-a-microservice-4|32 — Splitting Out a Microservice 4: The Notifications Service]]: the second program with its own database and settings, idempotent handlers, a gRPC call to the API for contact details, and the whole system running with one service stopped and started.
33. [[backend/frameworks/axum/33-calling-services-safely-1|33 — Calling Services Safely 1: Deadlines, Retries and the Breaker]]: why slow is worse than down, one deadline carried through every try, retries only for blips, with jitter, a circuit breaker with a Drop guard for abandoned trials, and fallbacks.
34. [[backend/frameworks/axum/34-calling-services-safely-2|34 — Calling Services Safely 2: Who's Calling?]]: short-lived service tokens signed with each service's own key, checked per method in a Tower layer with default deny and a test that every method has a rule, and TLS.

**Part 7: production**

35. [[backend/frameworks/axum/35-observability-1|35 — Observability 1: Logs]]: one shared crate setting up logging for every program, JSON lines with the spans they happened in, levels, what never to log, and a `Debug` that can't leak personal details.
36. [[backend/frameworks/axum/36-observability-2|36 — Observability 2: Following One Action]]: the trace id carried by `traceparent` through HTTP, gRPC, the outbox and NATS, so one payment shows as one trace across three programs, in the logs and in Jaeger.
37. [[backend/frameworks/axum/37-observability-3|37 — Observability 3: Metrics and Alerts]]: the golden signals and business numbers with the `metrics` crate, HTTP metrics by route never by path, Prometheus reading all three programs, and alerts on what customers feel, checked by promtool.
38. [[backend/frameworks/axum/38-async-pitfalls-in-production|38 — Async Pitfalls in Production]]: blocking the runtime, locks and awaits, waits that should run together, cancellation, `Send`, background tasks that die silently, compile times, and when async is the wrong choice, all in Mama Put's own code.
39. [[backend/frameworks/axum/39-config-secrets-and-health|39 — Config, Secrets and Health]]: every setting read once with all problems reported together, a `Secret` type and `_FILE`, liveness and readiness, draining, stopping on SIGTERM, a self-checking health command, and whether Rust was the right choice.
40. [[backend/frameworks/axum/40-docker|40 — Docker]]: sqlx's offline query cache, a cargo-chef Dockerfile with three distroless non-root images, and Compose for the whole system with an internal network, secret files and Caddy in front.
41. [[backend/frameworks/axum/41-ci-and-deployment|41 — CI and Deployment]]: a GitHub Actions pipeline that checks, tests against real Postgres and NATS, builds images by commit and deploys over a single-command SSH key, rolling deploys, rollback, and expand-and-contract migrations.

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[languages/03-rust/index|The Rust course]] — the language
- [[backend/frameworks/net-http/index|net/http]] — the other no-GC option, and the usual alternative
- [[backend/frameworks/drogon/index|Drogon]] — the same niche, without the guarantees
