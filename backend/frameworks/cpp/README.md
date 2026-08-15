# C++ Backends

**Concurrency model: usually an async event loop, sometimes a thread pool.** C++ has no runtime, so the framework brings one — nearly always [asio](https://think-async.com/Asio/) underneath, which is the de facto standard async I/O library and the basis of the long-proposed `std::net`. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

**~11,000 words across 5 notes.** `[reference]`. Assumes [[languages/05-cpp/README|the C++ course]].

> **The thing that most changes C++ web work: coroutines.** The callback-based API — two callbacks per async operation, nesting one level per chained call — is why C++ web development felt archaic. `co_await` turns it into linear code with one `try/catch`, and it removes an entire class of dangling-capture bugs because locals live in the coroutine frame. If you're writing C++ on the server today, use the coroutine API.

## Reading order

1. [[backend/frameworks/cpp/01-drogon-and-the-landscape|Drogon and the Landscape]] — **[Intermediate → Advanced]** — the options, Drogon's callback vs coroutine APIs, and lifetime across the async boundary
2. [[backend/frameworks/cpp/02-async-models-and-asio|Async Models and asio]] — **[Advanced]** — the library underneath everything, its three programming models, completion tokens, and why `std::net` still isn't standard
3. [[backend/frameworks/cpp/03-json-and-serialisation|JSON and Serialisation]] — **[Intermediate]** — **the gap C++ feels most.** No reflection means every mapping is hand-written
4. [[backend/frameworks/cpp/04-database-and-production|Database and Production]] — **[Intermediate → Advanced]** — Drogon's ORM, the connection-count trap, and deployment
5. [[backend/frameworks/cpp/05-when-to-choose-cpp|When to Choose C++]] — **[Intermediate]** — the decision, argued against Rust and Go

## The options

| Option | Character |
|---|---|
| **Drogon** | the most complete: HTTP/1.1+2, WebSockets, ORM, templates, **coroutines**. The usual first choice |
| **Crow** | header-only, Flask-like routing. Small and pleasant for embedding |
| **oat++** | zero-dependency, API-documentation-first, aimed at microservices |
| **Pistache** | modern C++ REST framework, Linux-focused |
| **Boost.Beast** | not a framework — HTTP/WebSocket *primitives* on asio. What you build on when you want control |
| **cpp-httplib** | single header, blocking, genuinely tiny. Great for a test server or a tool |

## What's genuinely different here

**RAII transactions.** An exception or early return destroys the transaction object, which rolls back. No `defer`, no `finally` — the same property Rust has, and one of the pleasant parts of C++ database work.

**`std::string_view` and `std::span` for zero-copy parsing** — a pointer and a length into the buffer that already exists.

**Strands instead of mutexes.** asio serialises related handlers without locking, which composes better with async operations than a mutex does.

## What it costs

- **No reflection.** Every struct-to-JSON mapping is hand-written or macro-listed. This is the single biggest ergonomic gap versus every other stack here, and it's felt on every endpoint. C++26 reflection fixes it; it isn't usable yet
- **Lifetime across async boundaries.** A lambda capturing by reference in a handler that returns immediately is a use-after-free with no warning. `shared_from_this` is the pattern; coroutines mostly remove the problem
- **No shared async vocabulary.** `drogon::Task`, `asio::awaitable` and `cppcoro::task` don't interoperate — C++ standardised the coroutine *mechanism* without a common awaitable type
- **~100MB container images**, because the binary is dynamically linked against libstdc++, libssl, libpq and friends
- **Timeouts are something you build.** They aren't defaults in asio

## The honest position

**C++ on the server is defensible far more often than [[backend/frameworks/c/README|C]]** — RAII and containers remove the easy memory bugs while keeping the performance. It is still not memory-safe.

**For a new standalone service with no existing C++ and no C++-only libraries, [[backend/frameworks/rust/README|Rust]] is the better choice** — same performance, guarantees instead of discipline, and a much better web ecosystem. Or [[backend/frameworks/go/README|Go]], which wins decisively on everything except raw performance and footprint.

**Where C++ is right:** the process is already C++ (a game server, a trading system, a simulation engine needing an admin API), or the domain libraries are C++ (vision, numerics, physics, codecs). Its niche on the server is **extending, not starting**. Note 05 argues this properly.

## Related
- [[backend/frameworks/README|frameworks/]] · [[languages/05-cpp/README|the C++ course]]
- [[backend/frameworks/c/README|C backends]] — the layer below
- [[backend/frameworks/rust/README|Rust backends]] — the same niche, with guarantees
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]]
