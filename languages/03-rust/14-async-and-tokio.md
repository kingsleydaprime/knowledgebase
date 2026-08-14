# Async and Tokio

**[Advanced]** — Rust's async model, why the runtime isn't in the language, and the mistakes that make an async program slower than a blocking one.

## `Future`

```rust
trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context) -> Poll<Self::Output>;
}

enum Poll<T> { Ready(T), Pending }
```

A `Future` is a value that will produce something later. It does **nothing until polled** — this is the first thing to internalise, and it's different from JavaScript, where a promise starts running the moment it's created.

```rust
let fut = fetch_data();      // NOTHING has happened yet
let data = fut.await;        // now it runs
```

`async fn` is sugar: the compiler rewrites the body into a state machine implementing `Future`, where each `.await` is a state transition. The whole thing lives in one struct, sized at compile time, with no allocation unless you box it.

That's why Rust's async is described as zero-cost: an async function that never suspends compiles to roughly the same code as the sync version.

## No runtime in the standard library

Rust ships the `Future` trait and the `async`/`await` syntax, and **no executor**. Something has to poll those futures, and that something is a library you choose:

- **`tokio`** — the default. Multi-threaded work-stealing scheduler, full I/O stack, timers, channels. Most of the ecosystem assumes it.
- **`async-std`** — mirrors the std API; largely superseded.
- **`smol`** — small and embeddable.
- **`embassy`** — for embedded, no allocator.

This is genuinely unusual — Go bakes its scheduler in, Node has exactly one event loop — and it's the source of the ecosystem's main wart: libraries are often tied to a specific runtime, so mixing them causes "there is no reactor running" panics at runtime rather than compile errors.

**In practice: use Tokio unless you have a specific reason not to.**

```rust
#[tokio::main]
async fn main() {
    let data = fetch().await;
}

// what the macro expands to, roughly:
fn main() {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all().build().unwrap()
        .block_on(async { let data = fetch().await; });
}
```

## Concurrency vs parallelism

```rust
let a = fetch_a().await;
let b = fetch_b().await;     // SEQUENTIAL — a finishes before b starts
```

`.await` suspends until that future completes. Writing two awaits in a row is not concurrent, and this is the most common async mistake.

```rust
let (a, b) = tokio::join!(fetch_a(), fetch_b());        // concurrent

let results = futures::future::try_join_all(urls.iter().map(fetch)).await?;

tokio::select! {                                        // first to finish wins
    a = fetch_a() => println!("a: {a:?}"),
    b = fetch_b() => println!("b: {b:?}"),
    _ = tokio::time::sleep(Duration::from_secs(5)) => println!("timeout"),
}
```

`join!` runs futures concurrently on **one task** — cooperative, not parallel. To get them onto different threads, spawn:

```rust
let handle = tokio::spawn(async { expensive_io().await });   // a new TASK
let result = handle.await?;
```

A `tokio::spawn`ed task is the async analogue of a goroutine — cheap (a few hundred bytes), scheduled onto the runtime's threads. Spawning is what gives you parallelism; `join!` only gives you concurrency.

## The three mistakes

**1. Blocking inside async.**

```rust
async fn bad() {
    std::thread::sleep(Duration::from_secs(1));    // BLOCKS THE WHOLE WORKER THREAD
    let data = std::fs::read_to_string("f")?;      // same problem
}
```

An async task must yield promptly. Block the thread and every other task scheduled on it stalls. With Tokio's default worker-per-core, a handful of blocking calls can freeze the server.

```rust
tokio::time::sleep(...).await;                       // async sleep
tokio::fs::read_to_string("f").await?;               // async file I/O
let r = tokio::task::spawn_blocking(|| cpu_heavy()).await?;   // for genuinely blocking work
```

This is exactly the failure mode as [[languages/02-go/06-goroutines-and-channels|Go]] — except Go's runtime detects a blocking syscall and detaches the thread, so it degrades instead of stalling. Rust's does not. Async Rust is less forgiving here.

**2. Holding a `std::sync::Mutex` across `.await`.**

```rust
let guard = mutex.lock().unwrap();
do_async_thing().await;              // the guard is held across a suspension point
```

The task can be moved between threads while suspended, and a `std::sync::MutexGuard` isn't `Send` — usually a compile error, but the pattern deadlocks where it does compile. Use `tokio::sync::Mutex` if a lock genuinely must span an await, and otherwise restructure so it doesn't. `tokio::sync::Mutex` is slower; the usual right answer is to shorten the critical section.

**3. Forgetting that futures are lazy.**

```rust
async fn log_it() { }
log_it();          // warning: unused implementer of `Future` — nothing happened
log_it().await;
```

## Async traits

```rust
trait Repo {
    async fn get(&self, id: u64) -> Result<User>;   // stable since Rust 1.75
}
```

Native `async fn` in traits works now, with one restriction: the returned future isn't automatically `Send`, so it's awkward for `dyn` trait objects used across threads. For public traits, `#[async_trait]` (which boxes the future) is still common:

```rust
#[async_trait]
trait Repo { async fn get(&self, id: u64) -> Result<User>; }
```

Use native for inherent impls and private traits; `#[async_trait]` when you need `Box<dyn Repo + Send + Sync>`.

## Streams

The async equivalent of `Iterator`:

```rust
use tokio_stream::StreamExt;

let mut stream = tokio_stream::iter(vec![1, 2, 3]);
while let Some(v) = stream.next().await { }

let results: Vec<_> = stream::iter(urls)
    .map(|u| fetch(u))
    .buffer_unordered(10)     // at most 10 concurrent — bounded concurrency
    .collect()
    .await;
```

`buffer_unordered(n)` is the async worker pool, and it's the tool for "fetch 10,000 URLs, 10 at a time" — bounding concurrency so you don't DoS the target or exhaust file descriptors.

## `Pin`, briefly

`Pin<&mut Self>` in `poll` exists because an async block's state machine can hold references *into itself* across an await — a self-referential struct. Moving it would invalidate those references, so `Pin` guarantees it won't move.

**You almost never touch this directly.** It surfaces when hand-implementing `Future` or storing futures in a struct, where `Box::pin(fut)` is the answer. If you're writing application code and `Pin` appears in an error, you probably want `Box::pin`.

## Async vs threads, honestly

| | Threads | Async |
|---|---|---|
| Cost per unit | ~8KB stack + kernel | a few hundred bytes |
| Good for | CPU-bound | I/O-bound |
| Scale | thousands | hundreds of thousands |
| Complexity | low | high — colouring, `Pin`, runtime choice |
| Debugging | normal stack traces | harder |

**Function colouring is a real cost.** `async fn` can only be awaited from async context, so async spreads through a codebase and you end up with sync and async versions of libraries. This is the concrete thing Go avoided with goroutines, and it's the strongest argument for Go over Rust in ordinary network services.

Use async when you have many concurrent I/O-bound tasks — a web server, a proxy, a crawler. Use threads for CPU-bound work. Don't make a CLI async because it's fashionable.

---

## Related
- [[languages/03-rust/13-concurrency|Concurrency]] — threads, and when to prefer them
- [[backend/frameworks/rust/README|Rust Backends]] — Axum, built on Tokio
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — where this sits among the alternatives
- [[languages/02-go/06-goroutines-and-channels|Go: Goroutines]] — the no-colouring alternative
- [[languages/03-rust/README|Rust course map]]
