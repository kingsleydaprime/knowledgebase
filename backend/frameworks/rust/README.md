# Rust Backends

**Concurrency model: async/await on a runtime (usually tokio)** — green threads with explicit colouring. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

**~12,000 words across 6 notes.** `[reference]` — no Rust service in this vault yet. Assumes [[languages/03-rust/README|the Rust course]] and the [[backend/README|backend course]]; these cover only what those don't.

> **The thing Rust does that no other stack here structurally can:** a handler taking `AuthUser` as a parameter **cannot be called unauthenticated.** Not "shouldn't" — there is no path into the function body that skips the extractor. Authorisation bugs are a top-3 cause of real breaches and they're usually "this endpoint forgot the check". Here, forgetting it is a compile error. → [[backend/frameworks/rust/02-extractors-and-responses|note 02]]

## Reading order

1. [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and the Tower Stack]] — **[Intermediate → Advanced]** — the tokio/hyper/tower/axum layers, the `Service` trait, and why `poll_ready` gives you backpressure nothing else has
2. [[backend/frameworks/rust/02-extractors-and-responses|Extractors and Responses]] — **[Intermediate]** — request parsing in the type system, custom extractors as auth, and errors as responses
3. [[backend/frameworks/rust/03-state-and-shared-data|State and Shared Data]] — **[Intermediate → Advanced]** — `Arc<AppState>`, DI without a container, and the locking decisions that decide whether you scale
4. [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — **[Advanced]** — blocking the runtime, sequential awaits, cancellation safety, and compile times
5. [[backend/frameworks/rust/05-database-and-persistence|Database and Persistence]] — **[Intermediate → Advanced]** — `sqlx` checking your SQL against a real schema at compile time
6. [[backend/frameworks/rust/06-production-and-tradeoffs|Production and Tradeoffs]] — **[Intermediate → Advanced]** — observability, deployment, and **the honest answer to whether you should use Rust at all**

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

## Axum vs Actix Web

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros |
| Ecosystem reuse | high | lower |
| Model | shared state | thread-per-core |

**Axum is the current default**, mostly for `tower` compatibility. Actix is mature, marginally faster, and a fine choice.

## The honest verdict

Note 06 argues this properly. The short version: **for an ordinary CRUD service with a team of five and a deadline, Rust is usually the wrong tool** — [[languages/02-go/README|Go]] gets you most of the operational benefit at a fraction of the cost.

Rust is unambiguously right for **infrastructure many services depend on**: proxies, databases, data pipelines, CLI tooling, anything with a latency SLO a GC can't meet. That's where the performance amortises and the correctness guarantees pay for themselves.

## Related
- [[backend/frameworks/README|frameworks/]] — the same concepts across every stack
- [[languages/03-rust/README|The Rust course]] — the language
- [[backend/frameworks/go/README|Go backends]] — the other no-GC option, and the usual alternative
- [[backend/frameworks/cpp/README|C++ backends]] — the same niche, without the guarantees
