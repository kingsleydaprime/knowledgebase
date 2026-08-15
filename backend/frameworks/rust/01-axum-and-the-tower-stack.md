# Axum and the Tower Stack

**[Intermediate → Advanced]** — Axum is a thin layer over `hyper` and `tower`. Understanding the layers below it is what makes the rest predictable.

**Source:** `[reference]`. Assumes [[languages/03-rust/README|the Rust course]], especially [[languages/03-rust/14-async-and-tokio|async]].

## The stack

```
your handlers
    │
  AXUM        routing, extractors, IntoResponse
    │
  TOWER       Service trait, Layer, middleware
    │
  HYPER       HTTP/1 + HTTP/2 protocol
    │
  TOKIO       async runtime, I/O
```

Unlike most frameworks, these are **genuinely separate crates with separate maintainers**, and you can use each without the ones above it. Axum's design goal was to add routing and ergonomics *without* inventing its own middleware system — which is why it's roughly 5,000 lines rather than 50,000.

The practical consequence: `tower` middleware written for a gRPC client works in your HTTP server, because both are `Service`s.

## The `Service` trait

The abstraction everything rests on:

```rust
trait Service<Request> {
    type Response;
    type Error;
    type Future: Future<Output = Result<Self::Response, Self::Error>>;

    fn poll_ready(&mut self, cx: &mut Context) -> Poll<Result<(), Self::Error>>;
    fn call(&mut self, req: Request) -> Self::Future;
}
```

**An async function from request to response.** That's it — and it's deliberately not HTTP-specific, which is why the same trait covers HTTP servers, HTTP clients, gRPC, and database connection pools.

`poll_ready` is the part that doesn't exist in other ecosystems: a service can say **"not yet"**. That's how backpressure works — a rate limiter or a full connection pool returns `Pending`, and the caller waits rather than queueing unboundedly. Most frameworks have no equivalent.

A `Layer` wraps one `Service` in another:

```rust
trait Layer<S> {
    type Service;
    fn layer(&self, inner: S) -> Self::Service;
}
```

Same shape as Go's `func(Handler) Handler` from [[backend/frameworks/go/02-middleware-as-composition|middleware as composition]], with types attached.

## A minimal server

```rust
use axum::{Router, routing::get, Json};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(root))
        .route("/users/{id}", get(get_user).delete(delete_user))
        .route("/users", post(create_user));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn root() -> &'static str { "hello" }
```

Note `{id}` — Axum 0.8 switched from `:id` to `{id}` to match the standard library and other ecosystems. Older tutorials use the colon form.

## Handlers are plain async functions

```rust
async fn get_user(Path(id): Path<u64>) -> Json<User> { ... }
```

No macros, no attributes, no registration. A handler is any async function whose arguments are **extractors** and whose return type implements **`IntoResponse`**.

This is the trick that makes Axum feel light: everything is expressed in the type system rather than in annotations. Compare with `#[get("/users/{id}")]` in Actix or `@GetMapping` in Spring — those need a macro or reflection to connect a route to a function; Axum just passes the function to `get()`.

The magic is a set of blanket impls: `Handler` is implemented for every async fn taking 0–16 extractors. That's also why a handler with a non-extractor argument produces a famously unhelpful error — the trait simply isn't satisfied, and the compiler explains it badly. `axum::debug_handler` fixes that:

```rust
#[axum::debug_handler]                  // turns the trait error into a readable one
async fn get_user(Path(id): Path<u64>) -> Json<User> { ... }
```

**Reach for `#[debug_handler]` the moment a handler won't compile.** It's the single most useful debugging tool in Axum.

## Tower middleware

```rust
use tower_http::{trace::TraceLayer, compression::CompressionLayer, cors::CorsLayer};
use tower::ServiceBuilder;

let app = Router::new()
    .route("/users", get(list_users))
    .layer(
        ServiceBuilder::new()
            .layer(TraceLayer::new_for_http())        // outermost
            .layer(CompressionLayer::new())
            .layer(CorsLayer::permissive())
            .layer(TimeoutLayer::new(Duration::from_secs(30)))
            .into_inner(),
    );
```

> **`ServiceBuilder` applies layers top-to-bottom (outermost first). Bare `.layer()` calls apply bottom-to-top.** This reversal catches everyone. Use `ServiceBuilder` and read it as a request travelling downward.

`tower-http` gives you the standard set without writing any of it:

```
TraceLayer            request/response tracing
CompressionLayer      gzip/br/deflate
DecompressionLayer
CorsLayer
TimeoutLayer
RequestBodyLimitLayer     ← cap body size; not on by default
SetSensitiveHeadersLayer  ← redact Authorization from logs
ServeDir / ServeFile      static files
NormalizePathLayer
```

Per-route middleware via `route_layer`, which only runs for matched routes:

```rust
let app = Router::new()
    .route("/admin", get(admin))
    .route_layer(middleware::from_fn(require_admin))    // 404s don't hit it
    .route("/public", get(public));
```

`route_layer` vs `layer` is a real distinction: `layer` also wraps the fallback, so a `layer`-applied auth middleware runs on requests to nonexistent paths.

### Writing your own

```rust
use axum::middleware::{self, Next};
use axum::extract::Request;

async fn auth(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    let token = req.headers()
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .ok_or(StatusCode::UNAUTHORIZED)?;

    let claims = verify(token).map_err(|_| StatusCode::UNAUTHORIZED)?;
    req.extensions_mut().insert(claims);        // pass it downstream
    Ok(next.run(req).await)
}

let app = Router::new().route("/", get(h)).layer(middleware::from_fn(auth));
```

`middleware::from_fn` is the ergonomic escape hatch — it saves implementing `Service` and `Layer` by hand, which is genuinely tedious (a struct, a `Layer` impl, a `Service` impl, and usually a `Pin<Box<dyn Future>>`).

Write a real `Layer` only when you need `poll_ready` for backpressure. Otherwise `from_fn`.

## Nesting and merging

```rust
let api = Router::new()
    .route("/users", get(list_users))
    .route("/users/{id}", get(get_user));

let app = Router::new()
    .nest("/api/v1", api)                       // prefix
    .merge(admin_routes)                        // same level
    .fallback(handler_404)
    .layer(TraceLayer::new_for_http());
```

`nest` prefixes paths; `merge` combines routers at the same level. Both compose `Router`s, which are themselves `Service`s.

## Server configuration

```rust
let listener = TcpListener::bind(addr).await?;

axum::serve(listener, app)
    .with_graceful_shutdown(shutdown_signal())
    .await?;

async fn shutdown_signal() {
    let ctrl_c = async { signal::ctrl_c().await.expect("ctrl_c handler") };
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("SIGTERM handler").recv().await;
    };
    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
}
```

Graceful shutdown drains in-flight requests before exiting — the same requirement as [[backend/frameworks/go/01-net-http-in-depth|Go]], and equally necessary under [[devops/05-orchestration/README|Kubernetes]].

Timeouts come from `tower` rather than the server:

```rust
.layer(TimeoutLayer::new(Duration::from_secs(30)))
.layer(RequestBodyLimitLayer::new(1024 * 1024))     // 1MB — DO set this
```

For lower-level control (HTTP/2 settings, header read timeouts) you drop to `hyper_util::server::conn::auto::Builder` directly.

## Actix Web, briefly

The other major option:

```rust
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .service(get_user)
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}

#[get("/users/{id}")]
async fn get_user(path: web::Path<u64>) -> impl Responder { ... }
```

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros or builder |
| Runtime | tokio | own (actix-rt, on tokio) |
| Per-worker state | shared | **thread-per-core**, state per worker |
| Ecosystem reuse | high | lower |

Actix is slightly faster in benchmarks and has a thread-per-core model that avoids some cross-thread synchronisation. Axum's `tower` compatibility means more reusable middleware and easier integration with `tonic` (gRPC) and other tower-based tooling.

**Axum is the current default recommendation**, largely for that ecosystem reason. Actix is mature, fast, and a perfectly good choice.

---

## Related
- [[backend/frameworks/rust/02-extractors-and-responses|Extractors and Responses]] — the type-driven request handling
- [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — what goes wrong at runtime
- [[languages/03-rust/14-async-and-tokio|Rust: Async and Tokio]] — the runtime underneath
- [[backend/frameworks/go/02-middleware-as-composition|Go: Middleware]] — the same idea, untyped
- [[backend/frameworks/rust/README|Rust backends]]
