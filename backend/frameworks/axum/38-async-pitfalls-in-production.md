---
id: 077ceead-3852-409d-8429-318188e73279
---

# Async Pitfalls in Production

**Async code is code that can pause while it waits, for a database or the network, and let other work run in the meantime; a few easy mistakes undo that, and make an async service slower, or quietly broken, in ways that only show under real traffic.**

## Before you start
<!-- bite: ca0f532d-ef54-4cd2-b8b7-09c771ed8ecc -->

You should have finished [[backend/frameworks/axum/37-observability-3|Observability 3]]. This lesson collects the async mistakes Mama Put has already met, one by one, across lessons 12 to 37, and adds the one it hadn't fixed. It's mostly reading code you've already written, with new eyes.

After this lesson you will be able to:

1. Spot work that blocks the runtime, and move it off.
2. Hold locks correctly in async code, and know when an async lock is right.
3. Run independent waits at the same time, with a limit.
4. Reason about what happens when a future is dropped half-way.
5. Make sure a background task can never die without anyone knowing.
6. Read the compiler's `Send` errors, and keep compile times bearable.

## Where we stopped
<!-- bite: 3588ae88-da73-475f-b95d-35f78872d97a -->

Mama Put is three programs, observed from outside. Every one of them is async: thousands of requests, events and calls share a few threads, each one pausing at `.await` while it waits. That's what lets one small server answer many people at once. It's also where the strangest production bugs live, because the rules for sharing a few threads are easy to break without the compiler noticing.

## The kid version
<!-- bite: 24d9178e-f63a-425f-b706-71570f7049f9 -->

Mama Put has four cooks and forty orders. Each cook starts an order, and whenever it's waiting (the rice boiling, the stew simmering), puts it down and picks up another. Four cooks keep forty orders moving.

Now one cook decides to wash every plate in the stall before doing anything else. For twenty minutes, that cook moves no orders. A quarter of the kitchen has stopped, and from outside it just looks slow.

That's blocking the runtime. The fix is a dishwasher: a separate person for slow jobs that can't be put down halfway.

**Where the picture stops working.** A cook knows when they're washing plates. A Rust task doesn't know a function blocks; nothing warns it. You have to know which calls are slow and send them to the dishwasher yourself.

## Terms used in this lesson
<!-- bite: c8b247e9-6d86-48b1-a12a-9ae617f78c49 -->

1. **Runtime**: This is Tokio: a few worker threads that run many tasks, switching between them at each `.await`.
2. **Task**: This is one piece of async work the runtime runs, like handling one request.
3. **Blocking**: This means a call that holds its thread without pausing at an `.await`: heavy computing, a synchronous file read, `std::thread::sleep`.
4. **Cancellation**: This is a future being dropped before it finishes. Nothing after the `.await` it was paused at ever runs.
5. **`Send`**: This means a value may move to another thread. Tokio can move a task between threads at any `.await`, so everything a task holds across one must be `Send`.

## Step 1: blocking the runtime
<!-- bite: 7488b03c-37d4-4b12-bdb5-b22bf837e4ce -->

The most damaging mistake, and the easiest to make:

```rust
async fn handler() -> String {
    let data = std::fs::read_to_string("file.txt").unwrap(); // BLOCKS the worker thread
    std::thread::sleep(Duration::from_secs(1));               // so does this
    expensive_cpu_work();                                      // and this
    data
}
```

Tokio runs many tasks on each worker thread, and a task only gives the thread back at an `.await`. **Block a worker and every task waiting for it stalls.** With 8 workers, 8 requests that block at once freeze the whole server.

Mama Put has two kinds of deliberately slow work, and both go to Tokio's **blocking pool**, a separate set of threads where blocking is expected. Lesson 12's password hashing, in `src/auth/password.rs`:

```rust
pub async fn hash(password: String) -> Result<String, argon2::password_hash::Error> {
    // Deliberately slow work: off the async threads, so other requests keep moving.
    tokio::task::spawn_blocking(move || Ok(Argon2::default().hash_password(password.as_bytes())?.to_string()))
        .await
        .expect("the hashing task doesn't panic")
}
```

and lesson 18's photo resizing, in `src/menu/process.rs`:

```rust
    // Decoding and resizing keep a CPU core busy for a second or more: not on the threads that answer requests.
    let made = tokio::task::spawn_blocking(move || -> Result<(Vec<u8>, Vec<u8>), ImageError> {
```

For waiting, use the async versions: `tokio::fs`, `tokio::time::sleep`, sqlx, reqwest. They pause at `.await` and give the thread back.

**Why this is worse in Rust than in Go:** Go's runtime notices a goroutine stuck in a blocking system call and hands its processor to another. Tokio can't; it has no way to know your function is blocking. Async Rust is less forgiving here.

To find blocking you didn't know about, **tokio-console** shows each task and how long each poll took; a task with long polls is blocking. Part 3 of observability's request-time histogram shows the symptom: everything slow at once, not one route.

## Step 2: locks and `.await`
<!-- bite: 4871f104-49cd-41e8-89a8-90689e92a8c0 -->

```rust
let mut cache = state.cache.lock().await;
let data = fetch_from_db().await?; // every other task waits for this lock, for a whole database trip
cache.insert(key, data);
```

Correct, and it makes the server one-at-a-time. Do the slow work outside the lock, and hold it for microseconds:

```rust
let data = fetch_from_db().await?;
state.cache.lock().unwrap().insert(key, data);
```

**Prefer `std::sync::Mutex`, and never hold it across an `.await`.** That's what lesson 33's circuit breaker does: its state is behind a plain `Mutex`, taken for a moment before the call and again after, never while waiting. And if you do hold a `std` guard across an `.await` by mistake, the compiler usually refuses: the guard isn't `Send` (step 5). That error is the compiler catching a slowness bug.

**When an async lock is right.** Sometimes waiting *is* the point. Lesson 19's cache makes everyone asking for the same missing key wait in one line while the first one loads it from Postgres, so the database is asked once. In `src/cache/mod.rs`:

```rust
    fn line_for(&self, key: &str) -> Arc<tokio::sync::Mutex<()>> {
        self.loading.lock().unwrap().entry(key.to_owned()).or_default().clone()
    }

    /// The last one out takes the line away, so the map doesn't grow for ever.
    fn leave_line(&self, key: &str, line: &Arc<tokio::sync::Mutex<()>>) {
        let mut lines = self.loading.lock().unwrap();
        if Arc::strong_count(line) == 2 {
            lines.remove(key); // only the map and us still hold it
        }
```

Each key's line is a `tokio::sync::Mutex<()>`, held across the load on purpose; the map of lines is a plain `Mutex`, held only to find or tidy a line.

**The same mistake with spans.** Observability part 2 met its cousin: `let _guard = span.enter();` held across an `.await` keeps the span "current" while the task is paused, so other work on that thread gets logged under it. `.instrument(span)` is the fix.

## Step 3: waits that should happen together
<!-- bite: f8926c46-fb10-4346-b957-1b3fdc65ae4f -->

```rust
let contact = customers.contact(id).await?;  // 20 ms
let dish = menu.dish_name(dish_id).await;    // 15 ms: 35 ms in all
```

`.await` waits until the thing finishes, so two awaits in a row happen one after the other. When the second doesn't need the first's answer, run them together:

```rust
let (contact, dish) = tokio::join!(customers.contact(id), menu.dish_name(dish_id)); // 20 ms
```

`join!` runs both at once on the same task; `try_join!` stops at the first error. Notifications' receipt handler could do exactly this (practice 1). For many at once, **always with a limit**:

```rust
use futures::StreamExt;
let names: Vec<String> = futures::stream::iter(dish_ids)
    .map(|id| menu.dish_name(id))
    .buffer_unordered(10) // at most 10 calls at once
    .collect()
    .await;
```

`buffer_unordered(n)` is the async worker pool. Unlimited, ten thousand ids become ten thousand calls at once, and the API's breaker (lesson 33) opens for everyone.

## Step 4: cancellation
<!-- bite: b26fc5a0-5d4a-4d7b-85a8-f655319888bc -->

When a client hangs up, Axum drops the handler's future, **at whatever `.await` it was paused on**. Nothing after that point runs.

That's often fine. A transaction that never reaches `commit()` rolls back when it's dropped, which is why lesson 17's `mark_succeeded` does everything inside one. But some things aren't safe to stop half-way, and Mama Put has met three:

1. **Lesson 19's loading lines.** If the task loading a key is dropped, the next in line must take over, or everyone waits for ever. The line is a `Mutex` guard, and a guard is released when it's dropped, however that happens. Cancel-safe by `Drop`.
2. **Lesson 33's breaker.** A trial call dropped half-way would never report back, and the breaker would stay half-open for ever. The report is a `Drop` guard, so it reports either way.
3. **The stream reader's `select!`.** `tokio::select!` drops whichever branch didn't finish. The reader only selects between "next message" and "shut down", and asking for the next message is safe to abandon (the message stays in the stream). The handling happens *outside* the `select!`, so a shutdown never cuts an event in half.

The rule: **anything that must finish once started belongs in a transaction, a `Drop` guard, or a spawned task**, which isn't cancelled when its caller goes away. Tokio's documentation says, for each method, whether it's cancel-safe; check before putting one in a `select!`.

## Step 5: `Send`, and what the error means
<!-- bite: 513b70dd-3575-41aa-8d18-bd83beb7dc2c -->

```text
error: future cannot be sent between threads safely
note: future is not `Send` as this value is used across an await
      `std::rc::Rc<T>` which is not `Send`
```

Tokio can move a task to another thread at any `.await`, so a task's future must be `Send`, which means **nothing it holds across an `.await` may be non-`Send`**: `Rc`, `RefCell`, a `std` `MutexGuard`, a raw pointer.

The fixes: `Arc` instead of `Rc`; or end the guard before the `.await`, with a block:

```rust
let value = {
    let state = shared.lock().unwrap(); // the guard lives only inside these braces
    state.value.clone()
};
do_async_thing(value).await;
```

That block is worth learning as a reflex; it's the answer most of the time.

We met a cousin of this error in the microservice topic: `?` couldn't turn a `Box<dyn Error + Send + Sync>` into a plain `Box<dyn Error>`. Errors that cross tasks need `Send + Sync` too, and a crate's setup function returning a concrete error type (observability part 1's `telemetry::Error`) works with either.

**Async traits.** Lesson 8's stores are `#[async_trait]` traits behind `Arc<dyn …>`. Rust's own `async fn` in traits (stable since 1.75) doesn't promise its future is `Send`, so a `dyn` trait object used from many tasks needs `#[async_trait]`, which boxes each call's future. Our generic code and plain `impl` blocks use native `async fn`.

## Step 6: background tasks that die silently
<!-- bite: 429f3896-3541-432e-99a4-73a23a133904 -->

```rust
tokio::spawn(kitchen::listen(pool.clone(), kitchen.hub.clone()));
```

That's how `main` started lesson 20's kitchen listener, and the worker started lesson 17's webhook sender the same way. If either panicked, the panic would be kept in the task's `JoinHandle`, and nobody was holding the handle. **The task would die with no log line**, and the kitchen screens, or Okada's webhooks, would just stop.

So `telemetry` gained a helper:

```rust
/// Runs `task` in the background for the life of the program, and logs at ERROR if it ever stops,
/// by panicking or by returning. A spawned task whose handle nobody awaits dies silently: no log line,
/// and whatever it did (the kitchen's events, the partner webhooks) just stops.
pub fn spawn_watched<F>(name: &'static str, task: F)
where
    F: std::future::Future<Output = ()> + Send + 'static,
{
    let handle = tokio::spawn(task);
    tokio::spawn(async move {
        match handle.await {
            Ok(()) => tracing::error!(task = name, "background task stopped"),
            Err(e) if e.is_panic() => tracing::error!(task = name, cause = %e, "background task panicked"),
            Err(_) => {} // cancelled: the program is shutting down
        }
    });
}
```

and both now start with it:

```rust
telemetry::spawn_watched("kitchen-events", kitchen::listen(pool.clone(), kitchen.hub.clone()));
```

A second task awaits the first one's handle and logs at `ERROR` if it ever ends. Its test makes a task panic and checks the line:

```rust
    #[tokio::test]
    async fn a_background_task_that_panics_is_reported() {
        let provider = tracer_provider("test", false).unwrap();
        let lines = Lines::default();
        let writer = lines.clone();
        let _subscriber = tracing::subscriber::set_default(subscriber(&provider, "test", EnvFilter::new("info"), move || writer.clone()));
        spawn_watched("kitchen-events", async { panic!("the listener broke") });
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        let text = String::from_utf8(lines.0.lock().unwrap().clone()).unwrap();
        let line = text.lines().find(|l| l.contains("background task panicked")).expect("reported");
        let line: serde_json::Value = serde_json::from_str(line).unwrap();
        assert_eq!((line["level"].as_str(), line["fields"]["task"].as_str()), (Some("ERROR"), Some("kitchen-events")));
        assert!(line["fields"]["cause"].as_str().unwrap().contains("panicked"), "{line}");
    }
}
```

Tasks whose handles *are* awaited don't need it: the worker joins its relay and reader at shutdown, and the gRPC server's task logs its own error.

## Step 7: compile times
<!-- bite: 10ab652b-1bb6-413f-984d-bbe403dc98ff -->

The honest cost. This project builds clean in many minutes on a laptop with two compile jobs, and Docker's release build takes longer still (lesson 40 has the number). What actually helps, most of it already in use here:

1. **`cargo check`** while writing: no machine code, much faster than `cargo build`.
2. **Optimise only the slow crates in development**, so tests stay fast without slowing every build. Lessons 16 and 18 did it for Argon2 and the image crates:

```toml
# Resizing photos is slow without optimisation, even while developing. Optimise just those crates.
[profile.dev.package.image]
opt-level = 3

# So is hashing passwords: unoptimised, Argon2 takes seconds, and a test run full of sign-ups hits
# the app's 10-second timeout. Optimising it (and its hash function) changes nothing but speed.
[profile.dev.package.argon2]
opt-level = 3
```

3. **A workspace** (the microservice topic): crates that don't depend on each other compile at the same time, and changing notifications doesn't rebuild the API.
4. **A faster linker**, like `mold` on Linux. Linking is often a large part of each rebuild.
5. **Fewer features.** `tokio = { features = ["full"] }` pulls in more than most programs use.
6. **`cargo-chef` in Docker** (lesson 40): dependencies built once and kept, so a change to our code rebuilds only our code.

## Step 8: when async is the wrong choice
<!-- bite: 64ebfa49-bd82-4610-ad30-b1eca003854a -->

Async has a real cost: function colouring (an `async fn` can only be awaited from async code, so it spreads through everything), harder stack traces, and every pitfall above. It pays for itself with many connections that mostly wait: Mama Put's HTTP requests, gRPC calls, live streams and NATS reader.

A service with modest traffic doing mostly CPU work, like a report generator or a batch job, is often simpler with plain threads and blocking code. Choose async because the work waits a lot, not because the framework is async.

## The Rust in this lesson
<!-- bite: eeaebb49-d541-42b7-adf4-a91d844f001c -->

1. **`tokio::task::spawn_blocking(move || …)`**: runs a closure on the blocking pool and gives back a future of its result.
2. **`std::sync::Mutex` versus `tokio::sync::Mutex`**: a `std` lock for moments, never across `.await`; an async lock only when waiting in line is the point.
3. **`tokio::join!` and `try_join!`**: several futures at once, on one task.
4. **`StreamExt::buffer_unordered(n)`**: at most `n` futures running at once, results in the order they finish.
5. **A block as a scope**, `let value = { let guard = …; … };`: the guard is dropped at the closing brace.
6. **`JoinHandle` and `JoinError::is_panic()`**: awaiting a spawned task's handle gives its result, or the panic that ended it.
7. **`#[async_trait]`** versus native `async fn` in traits: boxing for `dyn` objects shared between tasks.

## Your project so far
<!-- bite: a7b283d5-1184-43a0-98d6-01d461b6fd02 -->

```text
mama-put/
├── telemetry/src/lib.rs          ← spawn_watched, and its test
├── src/main.rs                   ← the kitchen listener, watched
└── src/bin/worker.rs             ← the webhook sender, watched
```

## Common mistakes
<!-- bite: 51b2446f-3159-40ac-aea8-b8f950feb9ae -->

1. **Heavy work on the async threads.** Hashing, resizing, big parsing: `spawn_blocking`.
2. **A lock held across an `.await`.** Do the slow work first; lock for a moment.
3. **Awaits one after another that could run together.** `join!`, or `buffer_unordered` with a limit.
4. **Unlimited concurrency.** It finds the smallest limit downstream and breaks it.
5. **Work that mustn't stop half-way, in a future that can be dropped.** A transaction, a `Drop` guard, or a spawned task.
6. **A spawned task nobody watches.** It dies silently. Await its handle, or watch it.
7. **Reaching for `Rc` or `RefCell` in async code.** `Arc`, and a `Mutex` held briefly.

## Check your understanding
<!-- bite: bdd419e2-80f6-4f5a-b2fc-4d6b8bc3f3aa -->

1. Why does one blocking call affect requests that have nothing to do with it?
2. Lesson 19's cache holds an async lock across a database load. Why is that right there, and wrong in step 2's first example?
3. A client hangs up while `mark_succeeded` is waiting on Postgres. What happens to the payment?
4. What was wrong with `tokio::spawn(kitchen::listen(...))`, and what does `spawn_watched` change?
5. The compiler says a future "is not `Send` as this value is used across an await". What does that mean, and what's the usual fix?

<details>
<summary>Answers, after your attempt</summary>

1. Tasks share a few worker threads and only give a thread back at an `.await`. A blocking call holds its thread, so every other task waiting for that thread waits too.
2. There, waiting in line is the point: everyone asking for the same missing key waits while one loads it, so Postgres is asked once. In step 2, the lock protects the whole cache, so every request waits for one database trip, even for different keys.
3. The future is dropped before `commit`, so the transaction rolls back: the payment isn't marked settled. Paystack sends the webhook again, and it's settled then. Nothing is half-done.
4. Its `JoinHandle` was dropped, so a panic would end the task with nothing logged, and the kitchen screens would silently stop updating. `spawn_watched` awaits the handle in a second task and logs at `ERROR` if the first ever stops.
5. Tokio may move the task to another thread at that `.await`, and something held across it (like an `Rc` or a `std` `MutexGuard`) can't move between threads. Use `Arc`, or end the guard in a block before the `.await`.

</details>

## Practice
<!-- bite: 2cc3a743-4415-4062-bf7f-5fc319fc7a80 -->

1. In notifications' receipt handler, fetch the contact and the dish name with `tokio::join!`, and measure the difference with part 2 of observability's trace.
2. Find every other `tokio::spawn` in the workspace and decide, for each, whether its handle is awaited, watched, or neither.
3. Install tokio-console, run the API with it, and find the requests that hash passwords: what does a `spawn_blocking` task look like there?

**Done when** the kitchen listener and the webhook sender start with `spawn_watched`, its test passes, and you can say for each `tokio::spawn` in the project who would notice if it died.

## Before moving on
<!-- bite: 1ed66c4f-fd46-43fa-9483-ca704e61e7f8 -->

The code is ready for production's long hours: nothing blocks the threads, nothing waits needlessly, nothing stops half-way, and nothing dies unnoticed. Next, the settings around the code: how each program reads its config and secrets, how it tells the world it's healthy, and how it stops politely when told to.

## Related
<!-- bite: ba5bf20d-0059-4841-8b73-b3ca594d9ac6 -->

- [[backend/frameworks/axum/39-config-secrets-and-health|Next: Config, Secrets and Health]]
- [[backend/frameworks/axum/05-state-and-dependency-injection|State and Dependency Injection]] — the locking decisions
- [[languages/03-rust/14-async-and-tokio|Rust: Async and Tokio]] — the model underneath
- [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and Concurrency Models]]

## About this lesson
<!-- bite: a6ec31b6-3927-4047-9371-39aa0238ee50 -->

**Level:** Advanced. Lesson 38 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96) and Tokio 1. Covers blocking the runtime and the blocking pool, `std` and async locks and when each is right, running waits together with a limit, cancellation and what must not be stopped half-way, `Send` errors and async traits, background tasks that die silently and a watched spawn, compile times, and when async is the wrong choice, all shown in Mama Put's own code.
