# Drogon (C++ Backends)

## What Drogon is

**Drogon is the most complete web framework for C++: routing, an ORM, WebSockets and coroutines in one package.** People write C++ backends for services that must be very fast, like trading systems and game servers, and Drogon is the usual choice for a real application. This subject also holds the lessons that are true of any C++ backend, such as JSON and when to choose C++ at all.

**Concurrency model: usually an async event loop, sometimes a thread pool.** C++ has no runtime, so the framework brings one — nearly always [asio](https://think-async.com/Asio/) underneath, which is the de facto standard async I/O library and the basis of the long-proposed `std::net`. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~9,000 words across 4 notes.** `[reference]`. Assumes [[languages/05-cpp/index|the C++ course]].

> **The thing that most changes C++ web work: coroutines.** The callback-based API — two callbacks per async operation, nesting one level per chained call — is why C++ web development felt archaic. `co_await` turns it into linear code with one `try/catch`, and it removes an entire class of dangling-capture bugs because locals live in the coroutine frame. If you're writing C++ on the server today, use the coroutine API.

## Lessons so far

The asio lesson moved to [[backend/frameworks/boost-beast/index|Boost.Beast]], which is built on asio.

1. [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]] — **[Intermediate → Advanced]** — the options, Drogon's callback vs coroutine APIs, and lifetime across the async boundary
2. [[backend/frameworks/drogon/02-json-and-serialisation|JSON and Serialisation]] — **[Intermediate]** — **the gap C++ feels most.** No reflection means every mapping is hand-written
3. [[backend/frameworks/drogon/03-database-and-production|Database and Production]] — **[Intermediate → Advanced]** — Drogon's ORM, the connection-count trap, and deployment
4. [[backend/frameworks/drogon/04-when-to-choose-cpp|When to Choose C++]] — **[Intermediate]** — the decision, argued against Rust and Go

## The options

| Option | Character |
|---|---|
| **Drogon** | the most complete: HTTP/1.1+2, WebSockets, ORM, templates, **coroutines**. The usual first choice |
| **[[backend/frameworks/crow/index\|Crow]]** | header-only, Flask-like routing. Small and pleasant for embedding |
| **oat++** | zero-dependency, API-documentation-first, aimed at microservices |
| **Pistache** | modern C++ REST framework, Linux-focused |
| **[[backend/frameworks/boost-beast/index\|Boost.Beast]]** | not a framework — HTTP/WebSocket *primitives* on asio. What you build on when you want control |
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

**C++ on the server is defensible far more often than [[backend/frameworks/c-sockets/index|C]]** — RAII and containers remove the easy memory bugs while keeping the performance. It is still not memory-safe.

**For a new standalone service with no existing C++ and no C++-only libraries, [[backend/frameworks/axum/index|Rust]] is the better choice** — same performance, guarantees instead of discipline, and a much better web ecosystem. Or [[backend/frameworks/net-http/index|Go]], which wins decisively on everything except raw performance and footprint.

**Where C++ is right:** the process is already C++ (a game server, a trading system, a simulation engine needing an admin API), or the domain libraries are C++ (vision, numerics, physics, codecs). Its niche on the server is **extending, not starting**. [[backend/frameworks/drogon/04-when-to-choose-cpp|When to Choose C++]] argues this properly.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Drogon way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Drogon is and a first app**: the C++ landscape, and Drogon's place in it — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
2. **Controllers and routing**: `HttpController`, `METHOD_LIST`, typed path params, callbacks versus coroutines — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
3. **Filters and middleware**: Drogon filters and AOP advices
4. **Structure**: controllers, plugins, and the `drogon_ctl` project layout
5. **Wiring**: plugins as services, `app().getPlugin`
6. **Validation and JSON**: JsonCpp, and mapping every field by hand — written in part: [[backend/frameworks/drogon/02-json-and-serialisation|JSON and Serialisation]]
7. **Errors**: exceptions in coroutines, and lifetime across the async boundary — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
8. **Data**: the ORM, `DbClient`, transactions — written in part: [[backend/frameworks/drogon/03-database-and-production|Database and Production]]
9. **Auth**: sessions, and a JWT filter
10. **Security and cross-cutting**: CORS through advices, rate limiting, uploads with `MultiPartParser`
11. **Testing**: `drogon::test`, sanitizers in CI — written in part: [[backend/frameworks/drogon/03-database-and-production|Database and Production]]
12. **Production**: `config.json`, logging, deployment, graceful shutdown, and when to choose C++ — written in part: [[backend/frameworks/drogon/04-when-to-choose-cpp|When to Choose C++]]

## Related
- [[backend/frameworks/index|frameworks/]] · [[languages/05-cpp/index|the C++ course]]
- [[backend/frameworks/c-sockets/index|Sockets and epoll]] — the layer below
- [[backend/frameworks/axum/index|Axum]] — the same niche, with guarantees
- [[networking/09-sockets-and-the-network-api|Sockets and the Network API]]
