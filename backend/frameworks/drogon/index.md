# Drogon (C++ Backend)

## What Drogon is

**Drogon is the most complete web framework for C++: routing, an ORM, WebSockets and coroutines in one package.** People write C++ backends for services that must be very fast, like trading systems and game servers, and Drogon is the usual choice for a real application. This subject also holds the lessons that are true of any C++ backend, such as JSON and when to choose C++ at all.

**Concurrency model: usually an async event loop, sometimes a thread pool.** C++ has no runtime, so the framework brings one — nearly always [asio](https://think-async.com/Asio/) underneath, which is the de facto standard async I/O library and the basis of the long-proposed `std::net`. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~9,000 words across 4 notes.** `[reference]`. Assumes [[languages/05-cpp/index|the C++ course]].

> **The thing that most changes C++ web work: coroutines.** The callback-based API — two callbacks per async operation, nesting one level per chained call — is why C++ web development felt archaic. `co_await` turns it into linear code with one `try/catch`, and it removes an entire class of dangling-capture bugs because locals live in the coroutine frame. If you're writing C++ on the server today, use the coroutine API.

## Lessons so far

The asio lesson moved to [[backend/frameworks/boost-beast/index|Boost.Beast]], which is built on asio.

1. [[backend/frameworks/drogon/01-drogon|01 — Drogon and the C++ Landscape]] — **[Intermediate → Advanced]** — the options, Drogon's callback vs coroutine APIs, and lifetime across the async boundary
2. [[backend/frameworks/drogon/02-json-and-serialisation|02 — JSON and Serialisation]] — **[Intermediate]** — **the gap C++ feels most.** No reflection means every mapping is hand-written
3. [[backend/frameworks/drogon/03-database-and-production|03 — Database and Production]] — **[Intermediate → Advanced]** — Drogon's ORM, the connection-count trap, and deployment
4. [[backend/frameworks/drogon/04-when-to-choose-cpp|04 — When to Choose C++]] — **[Intermediate]** — the decision, argued against Rust and Go

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

This subject builds **one production backend** from the first lesson to the last, the Drogon way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What Drogon is and a first app**: the C++ landscape, and Drogon's place in it — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
2. **02 — Controllers and routing**: `HttpController`, `METHOD_LIST`, typed path params, callbacks versus coroutines — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
3. **03 — Filters and middleware**: Drogon filters and AOP advices
4. **04 — Structure**: controllers, plugins, and the `drogon_ctl` project layout
5. **05 — Wiring**: plugins as services, `app().getPlugin`
6. **06 — Input validation**: JsonCpp, and mapping every field by hand — written in part: [[backend/frameworks/drogon/02-json-and-serialisation|JSON and Serialisation]]
7. **07 — Errors and structured responses**: exceptions in coroutines, and lifetime across the async boundary, and one response shape for success and failure — written in part: [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]]
8. **08 — Data**: the ORM, `DbClient`, transactions — written in part: [[backend/frameworks/drogon/03-database-and-production|Database and Production]]

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with query parameters into ORM criteria, keyset pagination
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with path prefixes or a filter on a header
11. **11 — API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **12 — Authentication**: sessions, and a JWT filter
13. **13 — Authorization**: roles and owning your own orders, with filters that check roles and ownership
14. **14 — Security**: CORS through advices, rate limiting, uploads with `MultiPartParser`
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `drogon::test`, sanitizers in CI — written in part: [[backend/frameworks/drogon/03-database-and-production|Database and Production]]

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with Drogon's event loop timers and a worker queue
19. **19 — Caching**: caching hot reads with Drogon's Redis client, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with Drogon WebSocket controllers

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with cppgraphqlgen, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with gRPC C++
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand, since there's no official C++ SDK
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over NATS's C client or librdkafka, the outbox pattern
26. **26 — Calling other services safely**: Drogon's `HttpClient` with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with logging and prometheus-cpp
28. **28 — Production config and Docker**: `config.json`, logging, deployment, graceful shutdown, and when to choose C++; a Docker image with sanitizer builds in CI, Docker Compose for the whole system — written in part: [[backend/frameworks/drogon/04-when-to-choose-cpp|When to Choose C++]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|frameworks/]] · [[languages/05-cpp/index|the C++ course]]
- [[backend/frameworks/c-sockets/index|Sockets and epoll]] — the layer below
- [[backend/frameworks/axum/index|Axum]] — the same niche, with guarantees
- [[networking/09-sockets-and-the-network-api|Sockets and the Network API]]
