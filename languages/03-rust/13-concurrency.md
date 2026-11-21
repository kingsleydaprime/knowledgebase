---
id: 63817849-bc7c-4693-ab92-2de9931e95bc
---

# Concurrency

**[Intermediate → Advanced]** — "Fearless concurrency" is a marketing phrase for a real result: the ownership rules you already learned eliminate data races at compile time.

## The claim
<!-- bite: b9cdd5b8-8af2-406d-8e86-ce338dea9398 -->

A **data race** requires three things: two or more threads accessing the same memory, at least one writing, with no synchronisation.

The borrow rule from [[languages/03-rust/04-borrowing-and-references|Borrowing]] — one mutable reference *or* any number of immutable ones — makes that unrepresentable. If a thread has `&mut T`, no other reference exists. If several threads have `&T`, nobody is writing.

This wasn't the goal. Ownership was designed for memory management and turned out to solve data races for free, which is the most genuinely surprising result in the language's design.

**Worth being precise:** Rust prevents *data races*, not *race conditions*. Two threads taking a lock in different orders still deadlocks; a logically wrong interleaving is still logically wrong. What's gone is the memory-corrupting kind, where the compiler and CPU reorder around unsynchronised access and produce nonsense.

Contrast: [[languages/01-java/02-jvm-and-concurrency/index|Java]] and [[languages/02-go/07-concurrency-patterns|Go]] are memory-safe but will happily let two threads write one field. Go ships a *dynamic* race detector precisely because it can't check statically.

## Threads
<!-- bite: c0d9951d-45a4-4ce8-a1d9-607062dc1446 -->

```rust
use std::thread;

let handle = thread::spawn(|| {
    println!("from a thread");
    42
});
let result = handle.join().unwrap();     // waits; Result because the thread might panic
```

These are **OS threads**, 1:1, not green threads. Cheaper than Java's used to be, far more expensive than a goroutine. For tens of thousands of concurrent tasks you want async instead. → [[languages/03-rust/14-async-and-tokio|Async and Tokio]]

```rust
let data = vec![1, 2, 3];
thread::spawn(move || println!("{data:?}"));   // `move` is mandatory
```

`move` is required because the closure must own what it captures — the thread may outlive the spawning scope, so borrowing is unsound. This is the `F: 'static` bound from [[languages/03-rust/05-lifetimes|Lifetimes]] doing its job, and it's where beginners meet that bound for the first time.

**Scoped threads** (Rust 1.63+) let you borrow safely, because the scope guarantees the threads finish first:

```rust
let mut data = vec![1, 2, 3];
thread::scope(|s| {
    s.spawn(|| println!("{:?}", &data));    // borrow is fine — scope joins before returning
});
data.push(4);
```

## `Send` and `Sync`
<!-- bite: 59b09d6a-9b74-4d95-b14f-dad3c9907a8b -->

Two marker traits that encode thread safety in the type system:

- **`Send`** — safe to *move* to another thread
- **`Sync`** — safe to *share by reference* across threads (`T: Sync` ⟺ `&T: Send`)

Both are auto-derived: a type is `Send`/`Sync` if all its fields are. Almost everything is. The exceptions are what matter:

| Type | `Send` | `Sync` | Why |
|---|---|---|---|
| `Rc<T>` | ✗ | ✗ | non-atomic refcount would race |
| `Arc<T>` | ✓ | ✓ | atomic refcount |
| `RefCell<T>` | ✓ | ✗ | its borrow flag isn't atomic |
| `Mutex<T>` | ✓ | ✓ | that's the point |
| raw pointers | ✗ | ✗ | no guarantees available |

This is why `thread::spawn` requires `F: Send + 'static` — and why passing an `Rc` to a thread produces a compile error rather than a heisenbug. The check is entirely static and costs nothing at runtime.

## `Arc<Mutex<T>>`
<!-- bite: f904de4f-0c55-43f5-971d-d0f816f09248 -->

The threaded mirror of `Rc<RefCell<T>>`:

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut n = counter.lock().unwrap();   // blocks; returns a guard
        *n += 1;
    }));                                        // guard drops here → UNLOCKED
}
for h in handles { h.join().unwrap(); }
println!("{}", *counter.lock().unwrap());       // 10
```

Three things Rust gets right here that most languages don't:

**The data is *inside* the mutex.** `Mutex<T>` owns `T`, so there is no way to touch the data without taking the lock. Compare Java, where `synchronized` and the field it protects are related only by convention and a comment.

**The guard unlocks on drop.** No `unlock()` to forget, no `finally` block. Exiting the scope — including by panic — releases it.

**`.lock()` returns a `Result`.** If a thread panicked while holding the lock, the mutex is *poisoned* and every later `lock()` returns `Err`. That's a deliberate signal that the protected data may be in a half-updated state. Most code `.unwrap()`s it; production code should think about it.

`RwLock<T>` allows many readers or one writer — worth it only when reads genuinely dominate, since it's slower than `Mutex` under contention.

**Deadlock is still entirely possible.** Rust does not solve lock ordering. Take locks in a consistent order; don't hold one across an `.await`.

## Channels
<!-- bite: 965125b7-010c-4f24-b26f-5c36438cc8f6 -->

```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();       // multi-producer, single-consumer

for i in 0..3 {
    let tx = tx.clone();
    thread::spawn(move || tx.send(i).unwrap());
}
drop(tx);                              // drop the original or rx never sees the end

for received in rx { println!("{received}"); }   // ends when all senders drop
```

The standard channel is **mpsc** — many senders, one receiver. The `crossbeam-channel` crate provides mpmc, `select!`, and better performance; it's the usual choice for real work.

Ownership makes channels safer than elsewhere: sending **moves** the value, so the sender provably cannot touch it afterwards. Go's channels pass the value but nothing stops you keeping a pointer to it.

## Atomics
<!-- bite: bbe3db28-318a-44dd-834d-5f00a4039758 -->

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

static COUNTER: AtomicUsize = AtomicUsize::new(0);
COUNTER.fetch_add(1, Ordering::Relaxed);
COUNTER.load(Ordering::SeqCst);
```

Rust exposes the full C++11 memory model — `Relaxed`, `Acquire`, `Release`, `AcqRel`, `SeqCst`.

**Use `SeqCst` unless you can prove you need weaker.** The orderings are genuinely hard, the performance difference is usually irrelevant, and getting them wrong produces bugs that appear only on ARM under load. `Relaxed` is safe for a statistics counter nobody synchronises on.

## `rayon` — parallelism for free
<!-- bite: 6e851b21-96c9-4890-9b50-6cffdb45b7e3 -->

The crate to reach for when the problem is data-parallel:

```rust
use rayon::prelude::*;

let sum: i64 = data.par_iter().map(|x| expensive(x)).sum();
data.par_sort();
```

Change `iter()` to `par_iter()` and it runs across a work-stealing thread pool. That this is *safe* — no possibility of a data race — is entirely down to `Send`/`Sync` bounds. In C++ the same one-word change is a coin flip.

Use it for CPU-bound work over collections. It does nothing useful for I/O-bound work; that's async.

## Choosing a model
<!-- bite: d8247076-da32-4de2-aba2-59eea94ffb83 -->

| Workload | Use |
|---|---|
| CPU-bound, data-parallel | `rayon` |
| A few long-lived workers | `thread::spawn` |
| Borrowing local data in parallel | `thread::scope` |
| Shared mutable state | `Arc<Mutex<T>>` |
| Passing ownership between threads | channels |
| A counter or flag | atomics |
| Tens of thousands of I/O tasks | async → [[languages/03-rust/14-async-and-tokio\|Tokio]] |

The rule of thumb that survives: **threads for CPU, async for I/O.** Mixing them is normal — `tokio::task::spawn_blocking` exists exactly for that boundary.

---

## Related
<!-- bite: f2180bf7-3a3c-4b69-987a-3f5dbb8d93c6 -->
- [[languages/03-rust/14-async-and-tokio|Async and Tokio]] — the other concurrency model
- [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers]] — `Rc<RefCell<T>>`, the single-threaded mirror
- [[languages/02-go/07-concurrency-patterns|Go: Concurrency Patterns]] — the same problems, checked dynamically
- [[architecture/04-distributed-systems/index|Distributed Systems]] — where these problems stop being local
- [[languages/03-rust/index|Rust course map]]
