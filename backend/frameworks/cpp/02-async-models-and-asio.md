# Async Models and asio

**[Advanced]** — The library underneath every C++ network framework, its three programming models, and the executor question that has kept `std::net` out of the standard for a decade.

## asio is the substrate

Boost.Asio (and its identical standalone version) is the de facto standard C++ networking library. Drogon, Beast, and most serious C++ network code sit on it — the same position [[backend/frameworks/rust/01-axum-and-the-tower-stack|tokio]] holds in Rust.

The core abstraction is the **io_context**: an event loop you run explicitly.

```cpp
#include <asio.hpp>

asio::io_context ctx;

asio::ip::tcp::acceptor acceptor(ctx, {asio::ip::tcp::v4(), 8080});
acceptor.async_accept([](std::error_code ec, asio::ip::tcp::socket sock) {
    if (!ec) handle(std::move(sock));
});

ctx.run();                     // BLOCKS, processing events until there's no work left
```

`ctx.run()` is the event loop from [[backend/frameworks/c/01-the-accept-loop-and-event-loops|the C note]] — `epoll` on Linux, `kqueue` on BSD, IOCP on Windows — with the portability handled.

**Scaling across cores** is a thread pool all calling `run()` on the same context:

```cpp
std::vector<std::thread> threads;
for (unsigned i = 0; i < std::thread::hardware_concurrency(); ++i)
    threads.emplace_back([&ctx] { ctx.run(); });
```

Any thread may execute any completion handler, so **your handlers must be thread-safe**. The alternative is one `io_context` per thread (thread-per-core), which Drogon uses — no cross-thread synchronisation on the hot path, at the cost of uneven load distribution.

When several handlers touch shared state, a **strand** serialises them without a mutex:

```cpp
auto strand = asio::make_strand(ctx);
asio::post(strand, [] { /* runs serialised with other work on this strand */ });
```

Strands are asio's answer to data races: rather than locking, you guarantee that related handlers never run concurrently. It's the actor model, and it's usually better than a mutex here because it composes with the async operations.

## The three models

asio supports three ways to express the same operation, which is a real source of confusion when reading examples.

**1. Callbacks** — the original:

```cpp
socket.async_read_some(asio::buffer(data),
    [](std::error_code ec, std::size_t n) {
        if (!ec) { /* ... */ }
    });
```

Every chained operation nests one level deeper, and error handling repeats at each. Beyond about three steps it becomes unreadable — the same callback hell as [[backend/frameworks/cpp/01-drogon-and-the-landscape|Drogon's callback API]].

**2. Coroutines (C++20)** — what you should write now:

```cpp
asio::awaitable<void> session(asio::ip::tcp::socket socket) {
    try {
        char data[1024];
        for (;;) {
            std::size_t n = co_await socket.async_read_some(
                asio::buffer(data), asio::use_awaitable);
            co_await asio::async_write(socket, asio::buffer(data, n), asio::use_awaitable);
        }
    } catch (const std::exception &e) {
        // connection closed, or a real error
    }
}

asio::co_spawn(ctx, session(std::move(sock)), asio::detached);
```

Linear code, one `try/catch`, no nesting. `asio::use_awaitable` is the **completion token** that tells asio to return an awaitable rather than take a callback.

`co_spawn` launches a coroutine on an executor. `asio::detached` means "don't wait for it"; you can pass a completion handler instead to be notified when it finishes — which you should, since a detached coroutine that throws gives you nothing.

**3. Stackful coroutines** — `asio::spawn` with Boost.Coroutine. Predates C++20, still in older codebases, largely superseded.

## Completion tokens

The design that makes asio unusual: **the last argument decides what the operation returns.**

```cpp
socket.async_read_some(buf, [](auto ec, auto n) {});     // callback
co_await socket.async_read_some(buf, asio::use_awaitable);  // awaitable
auto fut = socket.async_read_some(buf, asio::use_future);   // std::future
socket.async_read_some(buf, asio::deferred);                 // lazy — compose then run
```

One API, four calling conventions. It's elegant and it's why asio's function signatures are so intimidating — they're templated on the token type with a trait computing the return type.

`asio::redirect_error(asio::use_awaitable, ec)` gets you a coroutine that reports errors via an error code rather than an exception, which matters when you can't afford exceptions.

## Timeouts

There's no timeout parameter. You race a timer against the operation:

```cpp
asio::steady_timer timer(ctx);
timer.expires_after(std::chrono::seconds(30));

// C++20 asio — parallel_group races them properly
auto [order, ec_timer, ec_read, n] = co_await asio::experimental::make_parallel_group(
    timer.async_wait(asio::deferred),
    socket.async_read_some(buf, asio::deferred)
).async_wait(asio::experimental::wait_for_one(), asio::use_awaitable);

if (order[0] == 0) { /* the timer won — timed out */ }
```

Older code uses `cancel()` on the socket when the timer fires. Either way, **timeouts are something you build**, and forgetting them is how a C++ server accumulates stuck connections. Compare with Go's `http.Server` fields or tokio's `timeout()` — both give you one line.

## Buffers and lifetime

The most dangerous part.

```cpp
void bad() {
    char data[1024];                                  // STACK
    asio::async_read(socket, asio::buffer(data), handler);
}                                                      // data is GONE; asio writes into freed memory
```

**An async operation's buffer must remain valid until the completion handler runs.** `asio::buffer` does not copy or own — it's a pointer and a length, exactly like [[languages/05-cpp/09-the-stl-containers|`std::span`]].

The standard fix is the `shared_from_this` pattern, keeping the object that owns the buffer alive:

```cpp
class Session : public std::enable_shared_from_this<Session> {
    asio::ip::tcp::socket socket_;
    std::array<char, 1024> buffer_;                   // owned by the Session

public:
    void start() { read(); }

private:
    void read() {
        auto self = shared_from_this();                // +1 refcount for the duration
        socket_.async_read_some(asio::buffer(buffer_),
            [this, self](std::error_code ec, std::size_t n) {
                if (!ec) { process(n); read(); }        // self keeps us alive across the chain
            });
    }
};
```

Capturing both `this` (for member access) and `self` (for lifetime) is the idiom. Capturing only `this` compiles and is a use-after-free.

**Coroutines improve this substantially** — locals live in the heap-allocated coroutine frame, so a buffer declared inside an `awaitable` function survives every suspension:

```cpp
asio::awaitable<void> session(asio::ip::tcp::socket socket) {
    char data[1024];                                   // in the coroutine frame — SAFE
    co_await socket.async_read_some(asio::buffer(data), asio::use_awaitable);
}
```

That's the single strongest practical argument for coroutines over callbacks here: an entire bug class disappears.

## Executors, and why `std::net` isn't standard

asio has been the basis of a proposed standard networking library since roughly 2014. It hasn't shipped, and the reason is **executors** — the abstraction for "where does this work run".

The committee spent a decade on the executor design, twice, because it has to serve networking, parallel algorithms, GPU offload, and coroutines simultaneously. `std::execution` (senders/receivers, P2300) landed for C++26 and is the intended foundation; networking will be built on it afterwards.

Practically: **there is no standard C++ networking, and won't be before C++29.** Use asio (which tracks the proposals closely) and expect the eventual standard to look similar.

This is the same "no runtime in the standard library" position as [[languages/03-rust/14-async-and-tokio|Rust's async]], with an important difference — Rust standardised the `Future` trait, so different runtimes share a vocabulary. C++ standardised the coroutine *mechanism* with no common awaitable type, so `drogon::Task`, `asio::awaitable`, and `cppcoro::task` don't interoperate.

## Blocking the loop

Same rule as every event-loop system, and worth restating because it's the most common performance bug:

```cpp
asio::awaitable<void> handler() {
    auto result = expensive_cpu_work();               // BLOCKS this thread's event loop
    std::this_thread::sleep_for(1s);                   // same
    auto data = read_file_synchronously();             // same
}
```

Every connection assigned to that thread stalls. Offload:

```cpp
asio::thread_pool pool(4);
auto result = co_await asio::co_spawn(pool,
    []() -> asio::awaitable<Result> { co_return expensive_cpu_work(); },
    asio::use_awaitable);
```

Or `asio::post` to a separate pool with a completion handler. The rule from [[backend/frameworks/rust/04-async-pitfalls|Rust's async pitfalls]] applies identically: **the event loop thread does I/O, not computation.**

---

## Related
- [[backend/frameworks/cpp/01-drogon-and-the-landscape|Drogon and the Landscape]] — what's built on this
- [[backend/frameworks/c/01-the-accept-loop-and-event-loops|C: The Accept Loop]] — the same loop, unwrapped
- [[languages/05-cpp/13-concurrency|C++: Concurrency]] — coroutines, threads, the memory model
- [[backend/frameworks/rust/04-async-pitfalls|Rust: Async Pitfalls]] — the same failure modes
- [[backend/frameworks/cpp/README|C++ backends]]
