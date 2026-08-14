# Concurrency

**[Advanced]** — Threads, the memory model that made them well-defined, and the fact that nothing here is checked.

## Before C++11 there was nothing

Until 2011 the C++ standard had **no concept of a thread**. Multithreaded C++ was pthreads or Win32 plus a set of assumptions about what the compiler wouldn't reorder — assumptions with no basis in the standard.

C++11 added threads, mutexes, atomics, and — most importantly — a **memory model** that defines what concurrent execution actually means. That model was then adopted almost verbatim by C11, Rust and others, so it's the shared vocabulary now.

## Threads

```cpp
#include <thread>

void work(int id) { std::cout << "thread " << id << '\n'; }

std::thread t(work, 1);
t.join();                     // wait for it
// or
t.detach();                   // let it run independently
```

> **A `std::thread` that is neither joined nor detached calls `std::terminate` in its destructor.** Not a leak — an immediate crash. This is deliberate: the alternatives (implicit join, implicit detach) are both worse.

`std::jthread` (C++20) fixes this properly and is what you should use:

```cpp
#include <stop_token>

std::jthread t([](std::stop_token st) {
    while (!st.stop_requested()) { do_work(); }
});
// joins automatically on destruction, and requests stop first
```

`jthread` is RAII for threads plus a built-in cooperative cancellation token. There's little reason to use plain `std::thread` in new code.

```cpp
std::thread t([&data] { process(data); });     // lambda — beware capture lifetimes
std::this_thread::sleep_for(std::chrono::milliseconds(100));
unsigned n = std::thread::hardware_concurrency();   // a HINT; may return 0
```

These are **OS threads**, 1:1 — roughly 8MB of virtual stack each. Fine for tens, wrong for tens of thousands. C++ has no green threads; coroutines (C++20) are the async story and are still low-level.

## Mutexes

```cpp
#include <mutex>

std::mutex mu;
int shared = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mu);      // RAII — unlocks on scope exit
    ++shared;
}
```

**Never call `.lock()`/`.unlock()` directly.** An early return, a `break`, or an exception between them leaves the mutex held forever. [[languages/05-cpp/03-classes-and-raii|RAII]] is what makes this safe, and it's the clearest everyday demonstration of why RAII matters.

```cpp
std::lock_guard lock(mu);                       // simplest; CTAD since C++17
std::unique_lock lock(mu);                      // movable, can unlock/relock; needed for condvars
std::scoped_lock lock(mu1, mu2);                // C++17 — multiple mutexes, DEADLOCK-FREE ordering
std::shared_lock lock(shared_mu);               // reader lock for std::shared_mutex
```

**`std::scoped_lock` for multiple mutexes.** It uses a deadlock-avoidance algorithm rather than locking in the order you wrote — which removes the classic "thread A locks 1 then 2, thread B locks 2 then 1" deadlock.

```cpp
std::shared_mutex mu;                            // C++17 readers-writer lock
{ std::shared_lock r(mu); read(); }              // many readers
{ std::unique_lock w(mu); write(); }             // one writer
```

Worth it only when reads genuinely dominate — it's slower than a plain mutex under contention.

## The critical difference from Rust

```cpp
std::mutex mu;
int shared = 0;         // nothing connects these two
```

The mutex and the data it protects are related **only by convention and a comment**. Nothing stops you touching `shared` without the lock, and the compiler will never mention it.

[[languages/03-rust/13-concurrency|Rust puts the data inside the mutex]] — `Mutex<T>` owns `T`, so there is no way to reach the data without locking. That's the single clearest example of the difference between "safe if you're careful" and "safe".

The C++ approximation, worth doing:

```cpp
template <typename T>
class Guarded {
    T data_;
    mutable std::mutex mu_;
public:
    template <typename F>
    auto with(F &&f) { std::lock_guard lock(mu_); return f(data_); }
};

Guarded<std::vector<int>> v;
v.with([](auto &vec) { vec.push_back(1); });
```

Not enforced — you can still leak a reference out of the lambda — but it makes the correct thing the easy thing.

## Condition variables

```cpp
#include <condition_variable>

std::mutex mu;
std::condition_variable cv;
std::queue<Task> queue;
bool done = false;

void producer(Task t) {
    { std::lock_guard lock(mu); queue.push(std::move(t)); }
    cv.notify_one();
}

void consumer() {
    std::unique_lock lock(mu);
    cv.wait(lock, [] { return !queue.empty() || done; });   // predicate form — USE THIS
    if (!queue.empty()) { auto t = std::move(queue.front()); queue.pop(); }
}
```

**Always use the predicate form of `wait`.** Without it you must loop manually, because of **spurious wakeups** — a condition variable may wake for no reason at all, and code that assumes a wakeup means the condition holds is broken.

`unique_lock` rather than `lock_guard`, because `wait` needs to unlock and relock.

## Atomics

```cpp
#include <atomic>

std::atomic<int> counter{0};
counter.fetch_add(1);                  // atomic increment
counter++;                              // same
int v = counter.load();
counter.store(5);
counter.compare_exchange_strong(expected, desired);   // CAS

std::atomic<bool> ready{false};
std::atomic<Node *> head{nullptr};
```

Atomics avoid a mutex for single values. `std::atomic<T>::is_lock_free()` tells you whether it's a real instruction or a hidden lock — types larger than a machine word usually aren't.

## The memory model

The hard part. Modern CPUs and compilers **reorder** memory operations for performance, so without synchronisation, thread B may observe thread A's writes in a different order than they were written.

```cpp
std::memory_order_relaxed    // atomic, no ordering guarantees at all
std::memory_order_acquire    // no reads/writes after this can move before it
std::memory_order_release    // no reads/writes before this can move after it
std::memory_order_acq_rel
std::memory_order_seq_cst    // total global order — the DEFAULT
```

```cpp
// The acquire/release handshake — the canonical pattern
std::atomic<bool> ready{false};
int data = 0;

// thread A
data = 42;
ready.store(true, std::memory_order_release);   // everything before is visible...

// thread B
while (!ready.load(std::memory_order_acquire)) {}   // ...to anything after this
assert(data == 42);                                  // guaranteed
```

> **Use the default `seq_cst` unless you can prove you need weaker.** The orderings are genuinely hard, the performance difference is usually irrelevant, and a mistake produces bugs that appear only on ARM, only under load, only in production. `relaxed` is safe for a statistics counter nobody synchronises on.

**A data race is undefined behaviour**, not "a stale read". Two unsynchronised accesses with one write, and the standard says your entire program is meaningless — the compiler may have optimised on the assumption it couldn't happen.

## `std::async` and futures

```cpp
#include <future>

std::future<int> f = std::async(std::launch::async, [] { return expensive(); });
int result = f.get();                        // blocks until ready

auto f = std::async(compute);                // launch policy unspecified — MAY run lazily
```

**Always pass `std::launch::async` explicitly.** Without it the implementation may choose deferred execution, meaning your "concurrent" work runs synchronously inside `get()`.

The other trap: **the destructor of a future from `std::async` blocks** until the task completes. `std::async(...)` as a statement, discarding the future, is therefore synchronous — a genuinely surprising piece of design.

```cpp
std::promise<int> p;
std::future<int> f = p.get_future();
std::thread t([&p] { p.set_value(42); });
f.get();
```

C++ has no thread pool in the standard library, which is a real gap. In practice: a hand-rolled pool, Intel TBB, or the parallel algorithms from [[languages/05-cpp/10-iterators-and-algorithms|Iterators and Algorithms]]:

```cpp
std::sort(std::execution::par, v.begin(), v.end());
```

## Coroutines (C++20)

```cpp
Task<int> fetch() {
    auto data = co_await http_get(url);
    co_return parse(data);
}
```

C++20 coroutines are **a language mechanism, not a library**. The standard provides `co_await`, `co_yield`, `co_return` and the machinery to build coroutine types — but no ready-made `Task`, no executor, no scheduler.

So using them means adopting a library (cppcoro, libunifex, asio, folly) or writing several hundred lines of promise-type boilerplate. This is the same "no runtime in the standard" position as [[languages/03-rust/14-async-and-tokio|Rust's async]], except Rust at least standardised `Future`. C++23's `std::generator` is the first concrete coroutine type to ship.

Powerful and genuinely not beginner material.

## Finding the bugs

```bash
g++ -fsanitize=thread -g prog.cpp        # ThreadSanitizer — data race detection
valgrind --tool=helgrind ./prog
```

**ThreadSanitizer is the tool.** It finds races on paths that execute, with both stack traces. It's ~10× slower and incompatible with ASan, so it's a separate CI job.

Note that this is *dynamic* detection — the same position [[languages/02-go/07-concurrency-patterns|Go]] is in. Rust's is static and total.

## Practical rules

1. **`std::jthread` over `std::thread`.**
2. **`lock_guard`/`scoped_lock` — never manual lock/unlock.**
3. **`scoped_lock` for multiple mutexes**, to avoid deadlock.
4. **Predicate form of `cv.wait`**, always.
5. **`seq_cst` unless you've proven otherwise.**
6. **Explicit `std::launch::async`.**
7. **Group the mutex with its data**, structurally if you can.
8. **Run TSan in CI.**
9. **Prefer message passing and immutability** over shared mutable state, as everywhere.

---

## Related
- [[languages/05-cpp/03-classes-and-raii|Classes and RAII]] — what makes `lock_guard` work
- [[languages/03-rust/13-concurrency|Rust: Concurrency]] — the same primitives, statically checked
- [[languages/02-go/07-concurrency-patterns|Go: Concurrency Patterns]] — the dynamic-checking alternative
- [[foundations/os/fundamentals|OS Fundamentals]] — threads and scheduling underneath
- [[languages/05-cpp/README|C++ course map]]
