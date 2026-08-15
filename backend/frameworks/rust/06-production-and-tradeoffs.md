# Production and Tradeoffs

**[Intermediate → Advanced]** — Observability, deployment, and the honest answer to whether you should be writing this service in Rust at all.

## Tracing

Rust's observability story runs through `tracing`, which is structured logging and distributed tracing in one crate:

```rust
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

tracing_subscriber::registry()
    .with(tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| "info,tower_http=debug,sqlx=warn".into()))
    .with(tracing_subscriber::fmt::layer().json())
    .init();
```

```rust
#[tracing::instrument(skip(state), fields(user_id = %id))]
async fn get_user(State(state): State<AppState>, Path(id): Path<u64>) -> Result<Json<User>> {
    tracing::info!("fetching user");
    let user = state.db.get(id).await?;
    tracing::debug!(?user, "found");
    Ok(Json(user))
}
```

`#[instrument]` creates a **span** around the function, and every log inside it inherits the span's fields — so `user_id` appears on every line without being passed around. Spans nest, which gives you a call tree rather than a flat log.

**`skip(state)`** matters: without it, `#[instrument]` tries to `Debug`-format every argument, which for a connection pool is noise and for a password is a leak. Skip anything large or sensitive.

The sigils: `%` uses `Display`, `?` uses `Debug`.

```rust
let app = Router::new()
    .route("/users", get(list))
    .layer(TraceLayer::new_for_http());          // request/response spans, free
```

OpenTelemetry export:

```rust
.with(tracing_opentelemetry::layer().with_tracer(tracer))
```

→ [[devops/10-observability/README|Observability]]

## Metrics

```rust
use metrics::{counter, histogram};

counter!("http_requests_total", "method" => method, "route" => route).increment(1);
histogram!("http_request_duration_seconds", "route" => route).record(elapsed);
```

Same cardinality rule as everywhere: **label with the route pattern (`/users/{id}`), never the actual path.** Unbounded label values will take down your Prometheus.

`axum-prometheus` wires the standard HTTP metrics as a layer.

## Deployment

Rust's deployment story is the same as Go's — a static binary, no runtime:

```dockerfile
FROM rust:1.85-slim AS build
WORKDIR /app

# cache dependencies separately from source
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && cargo build --release && rm -rf src

COPY . .
RUN touch src/main.rs && cargo build --release

FROM gcr.io/distroless/cc-debian12
COPY --from=build /app/target/release/myservice /myservice
USER nonroot:nonroot
ENTRYPOINT ["/myservice"]
```

The dummy-`main.rs` trick caches the dependency build, which is the slow part — otherwise every source change rebuilds 300 crates. `cargo-chef` does this properly and is worth adopting for anything real.

**`distroless/cc`** rather than `static` because the default target links glibc. For a genuinely static binary:

```bash
rustup target add x86_64-unknown-linux-musl
cargo build --release --target x86_64-unknown-linux-musl     # then FROM scratch works
```

musl's allocator is noticeably slower under multi-threaded load; if you go musl, swap in `jemalloc` or `mimalloc`.

```toml
[profile.release]
lto = "fat"
codegen-units = 1
strip = true
panic = "abort"        # smaller and faster, IF you don't catch panics anywhere
```

`panic = "abort"` interacts with Axum: a panicking handler normally returns 500 via `CatchPanicLayer`; with `abort` it kills the process. Choose deliberately.

## Configuration and secrets

```rust
#[derive(serde::Deserialize)]
struct Config {
    #[serde(default = "default_addr")]
    addr: String,
    database_url: SecretString,          // from `secrecy` — redacted in Debug output
    #[serde(default)]
    log_level: String,
}

let config: Config = envy::from_env().context("loading config")?;
```

**Validate config at startup and fail loudly.** A service that boots with a missing database URL and fails on first request is worse than one that refuses to start.

`secrecy::SecretString` prevents the classic accident of a `#[derive(Debug)]` config struct printing your database password into the logs. → [[devops/09-secret-management/README|Secret Management]]

## The health check split

```rust
async fn live() -> StatusCode { StatusCode::OK }      // checks NOTHING external

async fn ready(State(s): State<AppState>) -> Result<StatusCode, AppError> {
    sqlx::query("SELECT 1").execute(&s.db).await?;
    Ok(StatusCode::OK)
}
```

**Liveness must not check dependencies.** If it does, a database blip makes Kubernetes restart every healthy pod and turns a partial outage into a total one. → [[devops/05-orchestration/README|Orchestration]]

## Should you use Rust for this service?

The honest section, because the answer is often no.

**What you actually get:**

- **No GC pauses.** Predictable tail latency — p99 that tracks p50 rather than spiking. This is the strongest argument, and it matters for trading, real-time bidding, game backends, and anything with a latency SLO
- **Memory efficiency.** Often 5–10× less RAM than a JVM service, which is real money at scale and decisive on small instances
- **Compile-time correctness.** Not just memory safety — exhaustive `match`, `Option` instead of null, and the [[backend/frameworks/rust/02-extractors-and-responses|extractor pattern]] making an unauthenticated handler unrepresentable
- **Fearless refactoring.** Change a type, fix the errors, and it works. This compounds over a codebase's life more than anything else here
- **A static binary**, like Go

**What it costs:**

- **Development speed.** A CRUD endpoint takes meaningfully longer than in [[backend/frameworks/java/README|Spring Boot]] or [[languages/02-go/README|Go]]. Not 10×, but not 1× either
- **Compile times.** Minutes for a clean build; enough to break flow → [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]]
- **Hiring and onboarding.** A competent engineer needs weeks to be productive, not days
- **Ecosystem gaps.** Fewer mature libraries for business-domain problems — payment SDKs, enterprise auth, reporting. Improving fast, still behind Java and Node
- **Async complexity.** Function colouring, `Send` bounds, cancellation safety, `Pin` in the error messages

**The decision, stated plainly:**

| Situation | Use |
|---|---|
| Latency SLO a GC can't meet | **Rust** |
| Very high throughput per instance, RAM-constrained | **Rust** |
| Correctness genuinely critical (payments, infra, security) | **Rust** |
| A long-lived system where refactoring cost dominates | **Rust** |
| Ordinary CRUD, team of 5, ship in a month | **[[languages/02-go/README\|Go]]** or Spring Boot |
| Heavy business logic, rich domain libraries needed | **JVM** |
| Prototype, uncertain requirements | **almost anything else** |

> **The steel-man for Rust that isn't performance:** the type system eliminates a class of bug that testing catches unreliably — forgotten auth checks, unhandled cases, null dereferences, data races. If you're building something where those bugs are expensive, the development-speed cost buys real insurance.
>
> **The steel-man against:** most services are not latency-critical, most bugs are logic bugs the compiler can't catch, and shipping three months earlier is usually worth more than p99 latency. Go gets you 80% of the operational benefits at 40% of the cost.

Both are true. The question is which side of it your service is on — and the honest default for a typical web service is that Rust is the wrong tool, chosen for reasons that are more aesthetic than operational.

## Where Rust is unambiguously right

Not general web services, but adjacent:

- **Proxies, gateways, load balancers** — Cloudflare's Pingora, Linkerd's proxy
- **Databases and storage engines** — TiKV, SurrealDB, InfluxDB 3
- **Data-processing pipelines** — Vector, Polars, DataFusion
- **CLI tooling** — ripgrep, fd, uv, ruff
- **WASM** on the edge
- **Anything embedded** in another language's runtime via FFI

The pattern: **infrastructure that many services depend on**, where the performance is amortised across every consumer and the correctness cost of a bug is high. That's where the trade is clearly favourable.

---

## Related
- [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — compile times and the runtime traps
- [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and the Tower Stack]] — graceful shutdown
- [[languages/03-rust/18-performance-and-zero-cost|Rust: Performance]] — what "zero cost" claims
- [[devops/10-observability/README|Observability]] · [[devops/02-docker/README|Docker]]
- [[backend/frameworks/rust/README|Rust backends]]
