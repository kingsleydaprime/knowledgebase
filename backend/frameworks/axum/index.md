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

Older reference notes, still to be rewritten into the lesson plan below: [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]], [[backend/frameworks/axum/05-database-and-persistence|Database and Persistence]] and [[backend/frameworks/axum/06-production-and-tradeoffs|Production and Tradeoffs]].

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

This subject builds **one production backend** from the first lesson to the last, the Axum way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. [[backend/frameworks/axum/01-what-axum-is-and-a-first-server|01 — What Axum Is, and Your First Server]]: the Tokio, hyper, Tower and Axum layers, handlers as plain async functions, graceful shutdown, and why `axum::serve` has no timeout for slow clients.
2. [[backend/frameworks/axum/02-routing-and-extractors|02 — Routing and Extractors]]: the menu as REST routes, `Path`, `Query`, `Json` and `State`, a menu behind `Arc<Mutex<>>`, and the two compile errors everyone meets.
3. [[backend/frameworks/axum/03-middleware|03 — Middleware]]: `from_fn` middleware, logging with `tracing`, `CatchPanicLayer`, a staff key with `route_layer`, and why the last layer added is the outermost.
4. [[backend/frameworks/axum/04-structuring-an-axum-service|04 — Structuring an Axum Service]]: a library crate beside `main`, a module per feature with a model, store, service and handlers, `pub use` as each feature's front counter, error enums that become status codes in one place, orders, and why Rust allows cycles between modules.
5. [[backend/frameworks/axum/05-state-and-dependency-injection|05 — State and Dependency Injection]]: stores as traits behind `Arc<dyn>`, the "not dyn compatible" error, the clock as a dependency and a shop-hours rule, one `AppState` with `FromRef`, `main` as the composition root, first unit tests, and locking decisions.
6. [[backend/frameworks/axum/06-validation|06 — Input Validation]]: `deny_unknown_fields`, `validator` rules reported all at once, a `ValidatedJson` extractor of our own, a body limit, and the line between the door and the service.
7. [[backend/frameworks/axum/07-errors|07 — Errors and Structured Responses]]: one `ApiError` reached with `From` and `?`, problem details written in one middleware, request IDs on every response and log line, JSON for unknown routes, panics and timeouts, `{"data": ...}`, and the layer stack with `ServiceBuilder`.
8. **08 — Data**: sqlx, transactions, migrations — written in part: [[backend/frameworks/axum/05-database-and-persistence|Database and Persistence]]

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with the `Query` extractor into a filter struct, keyset pagination with sqlx
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a nested `Router` per version, or a header extractor
11. **11 — API docs**: generating OpenAPI docs with utoipa

**Part 3: who can do what**

12. **12 — Authentication**: custom extractors as auth, JWTs and sessions — written in part: [[backend/frameworks/axum/02-routing-and-extractors|Extractors and Responses]]
13. **13 — Authorization**: roles and owning your own orders, with extractors that prove permissions
14. **14 — Security**: `tower-http` CORS and headers, rate limiting, body limits, multipart uploads
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `oneshot` against the whole router, with no network and no port; the first unit tests are in [[backend/frameworks/axum/05-state-and-dependency-injection|lesson 5]]

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with tokio tasks, or apalis on Redis
19. **19 — Caching**: caching hot reads with deadpool-redis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with Axum WebSockets and SSE

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with async-graphql, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with tonic
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with rmcp, the official Rust SDK, as an Axum service
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over NATS with async-nats, the outbox pattern
26. **26 — Calling other services safely**: reqwest with timeouts and tower retries, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with tracing, Prometheus and OpenTelemetry
28. **28 — Production config and Docker**: async pitfalls, tracing, config, deployment, and whether to use Rust at all; a small Docker image with cargo-chef, Docker Compose for the whole system — written in part: [[backend/frameworks/axum/06-production-and-tradeoffs|Production and Tradeoffs]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[languages/03-rust/index|The Rust course]] — the language
- [[backend/frameworks/net-http/index|net/http]] — the other no-GC option, and the usual alternative
- [[backend/frameworks/drogon/index|Drogon]] — the same niche, without the guarantees
