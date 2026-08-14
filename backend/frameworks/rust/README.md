# Rust Backends — scaffold

No course written yet. The shape, for when there is one:

**Concurrency model: async/await on a runtime (usually tokio)** — green threads with explicit colouring. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

| Option | Character |
|---|---|
| **Axum** | built on `tower`/`hyper`; middleware is composable `tower` layers. The current default choice |
| **Actix Web** | actor-influenced, very fast, its own ecosystem |

## The things to know
- **Middleware is `tower::Layer`** — the same composable-service abstraction used by gRPC tooling, so retries/timeouts/rate limits are reusable layers rather than framework-specific.
- **Extractors** pull typed values out of the request (path, query, JSON body, state) — validation and parsing happen in the type system, which is [[backend/01-foundations/03-the-request-lifecycle|"parse, don't validate"]] enforced by the compiler.
- **Blocking in an async task starves the runtime** — same failure as Node. Use `spawn_blocking` for CPU or blocking I/O.
- The borrow checker makes [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|DI]] look different: shared state is usually `Arc<AppState>` rather than a container.

## Related
- [[backend/frameworks/README|frameworks/]]
