# Axum (Rust Backends)

## What Axum is

**Axum is a framework for building web servers in Rust.** It is very fast, and it catches many mistakes before the code ever runs.

**Concurrency model: async/await on a runtime (usually tokio)** — green threads with explicit colouring. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~12,000 words across 6 notes.** `[reference]` — no Rust service in this vault yet. Assumes [[languages/03-rust/index|the Rust course]] and the [[backend/index|backend course]]; these cover only what those don't.

> **The thing Rust does that no other stack here structurally can:** a handler taking `AuthUser` as a parameter **cannot be called unauthenticated.** Not "shouldn't" — there is no path into the function body that skips the extractor. Authorisation bugs are a top-3 cause of real breaches and they're usually "this endpoint forgot the check". Here, forgetting it is a compile error. → [[backend/frameworks/axum/02-extractors-and-responses|note 02]]

## Lessons so far

1. [[backend/frameworks/axum/01-axum-and-the-tower-stack|Axum and the Tower Stack]] — **[Intermediate → Advanced]** — the tokio/hyper/tower/axum layers, the `Service` trait, and why `poll_ready` gives you backpressure nothing else has
2. [[backend/frameworks/axum/02-extractors-and-responses|Extractors and Responses]] — **[Intermediate]** — request parsing in the type system, custom extractors as auth, and errors as responses
3. [[backend/frameworks/axum/03-state-and-shared-data|State and Shared Data]] — **[Intermediate → Advanced]** — `Arc<AppState>`, DI without a container, and the locking decisions that decide whether you scale
4. [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]] — **[Advanced]** — blocking the runtime, sequential awaits, cancellation safety, and compile times
5. [[backend/frameworks/axum/05-database-and-persistence|Database and Persistence]] — **[Intermediate → Advanced]** — `sqlx` checking your SQL against a real schema at compile time
6. [[backend/frameworks/axum/06-production-and-tradeoffs|Production and Tradeoffs]] — **[Intermediate → Advanced]** — observability, deployment, and **the honest answer to whether you should use Rust at all**

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

This subject teaches the whole [[backend/index|backend course]] the Axum way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Axum is and a first server**: the tokio, hyper, tower and axum layers — written in part: [[backend/frameworks/axum/01-axum-and-the-tower-stack|Axum and the Tower Stack]]
2. **Routing and handlers**: `Router`, nesting and merging, handlers as async functions — written in part: [[backend/frameworks/axum/01-axum-and-the-tower-stack|Axum and the Tower Stack]]
3. **Middleware**: tower layers, and writing your own — written in part: [[backend/frameworks/axum/01-axum-and-the-tower-stack|Axum and the Tower Stack]]
4. **Structure**: a module per feature, routers merged in `main`
5. **State and DI**: `Arc<AppState>`, and locking decisions — written in part: [[backend/frameworks/axum/03-state-and-shared-data|State and Shared Data]]
6. **Validation**: extractors, and the `validator` crate — written in part: [[backend/frameworks/axum/02-extractors-and-responses|Extractors and Responses]]
7. **Errors**: `IntoResponse` and one `AppError` type — written in part: [[backend/frameworks/axum/02-extractors-and-responses|Extractors and Responses]]
8. **Data**: sqlx, transactions, migrations — written in part: [[backend/frameworks/axum/05-database-and-persistence|Database and Persistence]]
9. **Auth**: custom extractors as auth, JWTs and sessions — written in part: [[backend/frameworks/axum/02-extractors-and-responses|Extractors and Responses]]
10. **Security and cross-cutting**: `tower-http` CORS and headers, rate limiting, body limits, multipart uploads
11. **Testing**: `oneshot` against the whole router — written in part: [[backend/frameworks/axum/03-state-and-shared-data|State and Shared Data]]
12. **Production**: async pitfalls, tracing, config, deployment, and whether to use Rust at all — written in part: [[backend/frameworks/axum/06-production-and-tradeoffs|Production and Tradeoffs]]

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[languages/03-rust/index|The Rust course]] — the language
- [[backend/frameworks/net-http/index|net/http]] — the other no-GC option, and the usual alternative
- [[backend/frameworks/drogon/index|Drogon]] — the same niche, without the guarantees
