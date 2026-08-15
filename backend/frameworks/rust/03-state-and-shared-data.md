# State and Shared Data

**[Intermediate → Advanced]** — `Arc<AppState>`, why there's no DI container, and the locking decisions that decide whether your async service scales.

## Ownership meets a web server

A web server is the awkward case for [[languages/03-rust/03-ownership|ownership]]: many concurrent tasks, on many threads, all needing the same database pool and config. There is no single owner.

The answer is `Arc` — atomic reference counting, so every task holds a cheap clone.

```rust
#[derive(Clone)]
struct AppState {
    db: PgPool,                    // internally Arc — cheap to clone by design
    config: Arc<Config>,           // immutable after startup
    http: reqwest::Client,         // internally Arc; ONE client, reused
}

let state = AppState { db, config: Arc::new(config), http: reqwest::Client::new() };
let app = Router::new().route("/users", get(list)).with_state(state);
```

**State must be `Clone`, and it's cloned per request.** So every field should be cheap to clone: `Arc<T>` for anything expensive, and note that `PgPool` and `reqwest::Client` are already internally reference-counted — cloning them is a refcount bump, and creating one per request is a serious bug that defeats connection pooling.

Two shapes, both common:

```rust
#[derive(Clone)]
struct AppState { db: PgPool, config: Arc<Config> }     // fields individually Arc'd

struct Inner { db: PgPool, config: Config }
type AppState = Arc<Inner>;                              // one Arc around everything
```

The second is simpler; the first lets handlers extract just what they need via `FromRef`.

## Dependency injection, or the absence of it

Rust has no DI container. Like [[backend/frameworks/go/04-structuring-a-go-service|Go]], dependencies are struct fields assembled in `main`:

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let config = Config::from_env()?;
    let db = PgPoolOptions::new()
        .max_connections(25)
        .connect(&config.database_url).await
        .context("connecting to database")?;

    sqlx::migrate!("./migrations").run(&db).await?;

    let state = AppState { db, config: Arc::new(config), http: Client::new() };
    let app = routes(state);

    let listener = TcpListener::bind("0.0.0.0:8080").await?;
    axum::serve(listener, app).with_graceful_shutdown(shutdown()).await?;
    Ok(())
}
```

Explicit, ordered, and checked at compile time. No annotation scanning, no startup reflection, no "bean not found" at runtime.

For testability, generics over a trait rather than a concrete type:

```rust
trait UserStore: Send + Sync + 'static {
    fn get(&self, id: u64) -> impl Future<Output = Result<Option<User>>> + Send;
}

#[derive(Clone)]
struct AppState<S: UserStore> { store: S }
```

`Send + Sync + 'static` is the bound you'll write constantly — the state crosses threads (`Send`), is shared by reference (`Sync`), and must outlive the request (`'static`). → [[languages/03-rust/13-concurrency|Concurrency]]

Generics propagate through the router signature and get noisy, so `Arc<dyn UserStore>` is the common pragmatic alternative — one vtable indirection, far less type plumbing.

## Mutable shared state

Most state is immutable after startup, which needs no locking. When you do need mutation:

```rust
use tokio::sync::RwLock;

#[derive(Clone)]
struct AppState {
    cache: Arc<RwLock<HashMap<String, Value>>>,
}

let value = state.cache.read().await.get(key).cloned();     // many readers
state.cache.write().await.insert(key, value);                // one writer
```

### `std::sync::Mutex` vs `tokio::sync::Mutex`

The distinction that causes real production bugs:

| | `std::sync::Mutex` | `tokio::sync::Mutex` |
|---|---|---|
| Blocks | the OS thread | the task only |
| Across `.await` | **guard isn't `Send`** — usually won't compile, deadlocks where it does | fine |
| Speed | fast | slower (allocates, scheduler involvement) |

> **Use `std::sync::Mutex` unless you must hold the guard across an `.await`.** And usually you shouldn't hold it across an await at all.

```rust
// BAD — holds the lock across an await, serialising every request
let mut cache = state.cache.write().await;
let data = fetch_from_db(key).await?;          // every other task waits here
cache.insert(key, data);
```

```rust
// GOOD — do the slow thing outside the lock
let data = fetch_from_db(key).await?;
state.cache.write().await.insert(key, data);   // lock held for microseconds
```

Holding a lock across an `.await` is the async equivalent of holding a lock across a network call. Under load it turns your concurrent server into a serial one, and the symptom is throughput that doesn't improve with more cores.

**The best answer is usually not to lock at all:**

- `DashMap` — a concurrent map with internal sharding
- `arc-swap` — atomic replacement of an entire `Arc<T>`, ideal for config reloaded occasionally
- `tokio::sync::watch` — broadcast a value to many readers
- An actor: one task owns the data, others send messages over a channel

```rust
// the actor pattern — no locks at all
let (tx, mut rx) = mpsc::channel::<Command>(100);
tokio::spawn(async move {
    let mut state = State::new();               // owned by exactly ONE task
    while let Some(cmd) = rx.recv().await {
        match cmd { Command::Get { key, reply } => { let _ = reply.send(state.get(&key)); } }
    }
});
```

That's ownership doing what it's good at — the data has one owner, and concurrency comes from message passing rather than shared access.

## Per-request data

Application state is `State`; per-request data goes in extensions, inserted by middleware:

```rust
async fn auth(mut req: Request, next: Next) -> Result<Response, StatusCode> {
    let claims = verify(&req)?;
    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}

async fn handler(Extension(claims): Extension<Claims>) { }
```

**`Extension` fails at runtime if the layer wasn't applied.** A custom extractor is strictly better where possible, because it can't be forgotten — see [[backend/frameworks/rust/02-extractors-and-responses|Extractors]].

## Background tasks

```rust
let state = state.clone();
tokio::spawn(async move {
    let mut interval = tokio::time::interval(Duration::from_secs(60));
    loop {
        interval.tick().await;
        if let Err(e) = cleanup(&state).await {
            tracing::error!("cleanup failed: {e:?}");
        }
    }
});
```

Two things to get right:

**A spawned task needs `'static`** — it may outlive the spawner, so it must own everything it uses. Hence `state.clone()` and `async move`.

**A panic in a spawned task doesn't crash the process**, unlike a panic in a thread. The `JoinHandle` returns `Err`, and if nobody checks it the task silently dies. A background loop that quietly stopped is a genuinely annoying bug — log the panic, or supervise the task and restart it.

For graceful shutdown, `tokio_util::task::TaskTracker` plus a `CancellationToken` lets you wait for background work to finish rather than dropping it mid-flight.

## Connection pools

```rust
let db = PgPoolOptions::new()
    .max_connections(25)
    .min_connections(5)
    .acquire_timeout(Duration::from_secs(3))
    .idle_timeout(Duration::from_secs(600))
    .max_lifetime(Duration::from_secs(1800))
    .connect(&url).await?;
```

Same reasoning as [[backend/frameworks/go/05-database-access|Go's pool settings]]: `max_connections × replicas` must stay under the database's limit, and `acquire_timeout` is what stops a request queueing forever when the pool is exhausted.

The async-specific hazard: **tasks are cheap, so it's easy to spawn ten thousand and exhaust the pool instantly.** Bound concurrency at the source — `buffer_unordered(n)` on a stream, or a `Semaphore`:

```rust
let permits = Arc::new(Semaphore::new(50));
let _permit = permits.acquire().await?;      // held until it drops
```

## Testing

```rust
#[tokio::test]
async fn test_get_user() {
    let state = AppState { store: FakeStore::with(vec![user()]), ..test_state() };
    let app = routes(state);

    let response = app
        .oneshot(Request::builder().uri("/users/1").body(Body::empty()).unwrap())
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
}
```

`tower::ServiceExt::oneshot` sends a request through the whole router — middleware included — with **no network and no port binding**. It's the neatest testing story of any framework here, and it comes free from `Router` being a `Service`.

For database tests, `sqlx::test` gives each test its own transaction, rolled back afterwards:

```rust
#[sqlx::test]
async fn creates_user(pool: PgPool) {
    let store = PgUserStore::new(pool);
    store.create(&user()).await.unwrap();
}
```

---

## Related
- [[backend/frameworks/rust/02-extractors-and-responses|Extractors and Responses]] — how state reaches a handler
- [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — blocking, and what else stalls the runtime
- [[languages/03-rust/13-concurrency|Rust: Concurrency]] — `Arc<Mutex<T>>` and `Send`/`Sync`
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|DI and Wiring]] — the concept
- [[backend/frameworks/rust/README|Rust backends]]
