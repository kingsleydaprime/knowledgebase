# Async Pitfalls

**[Advanced]** — The failures that make an async Rust service slower than a blocking one, and the compiler errors that mean something other than what they say.

## Blocking the runtime

The most damaging mistake, and the easiest to make:

```rust
async fn handler() -> String {
    let data = std::fs::read_to_string("file.txt").unwrap();   // BLOCKS THE WORKER THREAD
    std::thread::sleep(Duration::from_secs(1));                 // same
    expensive_cpu_work();                                        // same
    data
}
```

Tokio's multi-threaded runtime defaults to one worker thread per core. Each runs many tasks cooperatively — a task yields at `.await`, and only there. **Block a worker and every task scheduled on it stalls.** With 8 workers, 8 concurrent blocking calls freeze the entire server.

The fixes:

```rust
tokio::fs::read_to_string("file.txt").await?;         // async I/O
tokio::time::sleep(Duration::from_secs(1)).await;     // async sleep

let result = tokio::task::spawn_blocking(move || {    // for genuinely blocking work
    expensive_cpu_work()
}).await?;
```

`spawn_blocking` moves the work to a separate, much larger pool (512 threads by default) where blocking is expected. Use it for CPU-heavy work, synchronous database drivers, and any C library that blocks.

For long CPU work that can't be chunked, `rayon` with a channel back is better — `spawn_blocking`'s pool isn't sized for sustained parallel compute.

**Why this is worse in Rust than in [[languages/02-go/README|Go]]:** Go's runtime detects a blocking syscall and detaches the thread, handing the processor to another. Tokio has no such mechanism — it cannot know your function is blocking. Async Rust is less forgiving here, and it's a real argument for Go in services doing mixed workloads.

Detect it with `tokio-console`, or the runtime's own warning:

```rust
// RUSTFLAGS="--cfg tokio_unstable" and enable the console subscriber
console_subscriber::init();
```

`tokio-console` shows per-task poll times. A task with a long poll duration is blocking.

## Holding a lock across `.await`

```rust
let mut cache = state.cache.lock().await;
let data = fetch_from_db().await?;          // every other task waits for this lock
cache.insert(key, data);
```

Correct, and it serialises your server. The lock is held for the duration of a database round-trip, so concurrent requests queue behind it and throughput stops scaling with cores.

```rust
let data = fetch_from_db().await?;          // slow work OUTSIDE the lock
state.cache.lock().await.insert(key, data); // lock held for microseconds
```

With `std::sync::Mutex` you usually get a compile error instead — the guard isn't `Send`, and the future must be. That error is the compiler catching a performance bug, which is a good reason to prefer `std::sync::Mutex` where you can. → [[backend/frameworks/rust/03-state-and-shared-data|State and Shared Data]]

## Sequential awaits that should be concurrent

```rust
let user = fetch_user(id).await?;           // 50ms
let posts = fetch_posts(id).await?;         // 50ms  → 100ms total
```

`.await` suspends until completion, so consecutive awaits are **sequential**. This is the most common source of quietly slow handlers.

```rust
let (user, posts) = tokio::try_join!(fetch_user(id), fetch_posts(id))?;   // 50ms
```

`join!` runs futures concurrently on one task; `try_join!` short-circuits on the first error. For a collection:

```rust
let results = futures::future::try_join_all(ids.into_iter().map(fetch_user)).await?;

// bounded — don't open 10,000 connections at once
use futures::StreamExt;
let results: Vec<_> = futures::stream::iter(ids)
    .map(|id| fetch_user(id))
    .buffer_unordered(10)
    .collect()
    .await;
```

**`buffer_unordered(n)` is the async worker pool.** Unbounded concurrency will exhaust your connection pool, your file descriptors, or the downstream service.

## Cancellation safety

The subtle one. When a client disconnects, Axum drops the handler's future — **at whatever `.await` point it was suspended on**. Anything after that point never runs.

```rust
let mut tx = pool.begin().await?;
tx.execute("UPDATE ...").await?;
some_slow_call().await?;              // ← dropped here
tx.commit().await?;                    // never runs — transaction rolls back. Fine.
```

That case is safe. This one isn't:

```rust
let item = queue.pop().await?;         // removed from the queue
process(item).await?;                  // ← dropped here → ITEM LOST
```

**In `tokio::select!` this matters most**, because losing branches are cancelled at their current await point:

```rust
tokio::select! {
    msg = rx.recv() => { }             // recv IS cancel-safe
    _ = timeout => { }
}
```

Documentation for tokio types states cancel safety explicitly. `recv()` is safe; `read_exact()` is not (it may have consumed half a message). When you need a non-cancel-safe operation in `select!`, move it into a `tokio::spawn` and select on the `JoinHandle` — a spawned task isn't cancelled when the parent future drops.

## `Send` bounds and their error messages

```
error: future cannot be sent between threads safely
note: future is not `Send` as this value is used across an await
      `std::rc::Rc<T>` which is not `Send`
```

Tokio's multi-threaded runtime can move a task between threads at any await point, so futures must be `Send`. That means **nothing held across an `.await` may be non-`Send`**: `Rc`, `RefCell`, `MutexGuard` from `std`, or a raw pointer.

The fixes: `Arc` instead of `Rc`, `tokio::sync::Mutex` if the guard genuinely must span an await, or restructure so it doesn't:

```rust
let value = {                          // scope the guard so it drops before the await
    let guard = state.lock().unwrap();
    guard.value.clone()
};
do_async_thing(value).await;
```

That block-scoped-guard pattern is worth learning as a reflex — it's the answer most of the time.

## Async traits

```rust
trait Store {
    async fn get(&self, id: u64) -> Result<User>;    // stable since Rust 1.75
}
```

Native async fn in traits works, with one catch: **the returned future isn't automatically `Send`**, so `Box<dyn Store>` used across threads doesn't work directly.

```rust
#[async_trait]                          // boxes the future; adds an allocation per call
trait Store {
    async fn get(&self, id: u64) -> Result<User>;
}
```

Use native for inherent impls and generic code; `#[async_trait]` when you need `Arc<dyn Store + Send + Sync>`, which in a web service you usually do.

## Spawned tasks and panics

```rust
tokio::spawn(async move {
    background_work().await;            // if this panics, NOTHING reports it
});
```

The panic is captured in the `JoinHandle`. If nobody awaits it, the task dies silently and your background job simply stops running — with no log line, no alert, nothing.

```rust
let handle = tokio::spawn(async move { background_work().await });
tokio::spawn(async move {
    if let Err(e) = handle.await {
        tracing::error!("background task died: {e}");
    }
});
```

Or set a panic hook, or use `TaskTracker` to supervise. **A silently dead background task is one of the more painful production surprises in async Rust.**

## Compile times

The honest operational cost. An Axum service with `sqlx`, `serde`, `tower-http` and `tracing` takes minutes to build clean, and a full rebuild after touching a core type is slow enough to break flow.

What actually helps:

```toml
[profile.dev]
debug = 1                    # less debug info; noticeably faster linking

[profile.dev.package."*"]
opt-level = 3                # optimise DEPENDENCIES once, keep your crate fast to build
```

```bash
cargo check                  # no codegen — use this in your watch loop
cargo install cargo-nextest  # faster test runner
```

- **`cargo check` in a watch loop**, `cargo build` only when running
- **Split into workspace crates** — they compile in parallel
- **A faster linker**: `mold` on Linux, `lld` elsewhere. Often the single biggest win
- **Trim features** — `tokio = { features = ["full"] }` pulls in far more than most services use
- **`sccache`** for shared caching

## Streaming and SSE

```rust
async fn download(State(s): State<AppState>) -> impl IntoResponse {
    let stream = ReaderStream::new(tokio::fs::File::open(path).await?);
    Body::from_stream(stream)                    // constant memory
}

async fn events() -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let stream = BroadcastStream::new(rx)
        .map(|msg| Ok(Event::default().data(msg.unwrap())));
    Sse::new(stream).keep_alive(KeepAlive::default())
}
```

**Stream large responses rather than buffering.** Reading a 4GB file into a `Vec<u8>` to return it will OOM; `Body::from_stream` uses constant memory.

`keep_alive` on SSE matters — proxies close idle connections, and without periodic comments your event stream dies after 60 seconds for reasons that look like a bug in your code.

## When async is the wrong choice

Worth stating: **async has a real complexity cost**, and it buys you concurrency for **I/O-bound** work.

If your service handles modest traffic and does CPU work, a thread-per-request design with `std::net` or a blocking framework is simpler, easier to debug (real stack traces), and fast enough. Async earns its place at high connection counts — thousands of concurrent, mostly-idle connections.

Function colouring is the ongoing tax: `async fn` can only be awaited from async context, so it spreads through everything and you end up with sync and async variants of libraries. That's the concrete thing Go's goroutines avoid.

---

## Related
- [[backend/frameworks/rust/03-state-and-shared-data|State and Shared Data]] — locking decisions
- [[languages/03-rust/14-async-and-tokio|Rust: Async and Tokio]] — the model underneath
- [[backend/frameworks/rust/05-database-and-persistence|Database and Persistence]] — where most awaits go
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]]
- [[backend/frameworks/rust/README|Rust backends]]
