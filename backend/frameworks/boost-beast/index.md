# Boost.Beast (C++ Backend)

## What Boost.Beast is

**Boost.Beast is a C++ library that reads and writes HTTP and WebSocket messages on top of asio. It is a toolkit, not a framework.** It has no routing, middleware or JSON, so you build those yourself. What you get is a correct, well-tested parser and asio's async model, which is why other frameworks and proxies are built on it.

## Lessons so far

1. [[backend/frameworks/boost-beast/01-boost-beast|01 — Boost.Beast]]
2. [[backend/frameworks/boost-beast/02-async-models-and-asio|02 — Async Models and asio]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Boost.Beast way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What Boost.Beast is**: HTTP primitives on asio, and when to build on them — written in part: [[backend/frameworks/boost-beast/01-boost-beast|Boost.Beast]]
2. **02 — asio and the async models**: callbacks, futures and coroutines, completion tokens, timeouts — written in part: [[backend/frameworks/boost-beast/02-async-models-and-asio|Async Models and asio]]
3. **03 — A routing layer of your own**: a map from method and target to handler
4. **04 — Middleware**: functions that wrap handlers
5. **05 — Sessions and lifetime**: `shared_from_this`, strands
6. **06 — Input validation**: body types, body limits, JSON with Boost.JSON
7. **07 — Errors and structured responses**: `beast::error_code`, timeouts with `tcp_stream`, and one response shape for success and failure
8. **08 — Data**: calling a database without blocking the `io_context`

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with parsing the target's query string, keyset pagination
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with routing on the path prefix or a header
11. **11 — API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **12 — Authentication**: reading auth headers, `ssl_stream`
13. **13 — Authorization**: roles and owning your own orders, with checks in your own routing layer
14. **14 — Security**: `websocket::stream`
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `beast::test::stream`

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with asio thread pools and timers
19. **19 — Caching**: caching hot reads with a Redis client on asio, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with Beast WebSockets

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with cppgraphqlgen, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with gRPC C++ next to Beast
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand, on Beast
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over NATS or AMQP on asio, the outbox pattern
26. **26 — Calling other services safely**: a Beast client with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with logging and prometheus-cpp
28. **28 — Production config and Docker**: a thread pool on one `io_context`, graceful shutdown, fuzzing; a Docker image and fuzzing in CI, Docker Compose for the whole system
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/drogon/index|Drogon]] — what a full framework gives you instead
- [[backend/frameworks/c-sockets/index|Sockets and epoll]] — the layer below asio
- [[languages/05-cpp/index|The C++ course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C++ subject, which is now [[backend/frameworks/drogon/index|Drogon]]. The asio lesson used to be lesson 02 of that subject.
