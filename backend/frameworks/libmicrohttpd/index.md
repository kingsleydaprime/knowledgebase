# libmicrohttpd (C Backend)

## What libmicrohttpd is

**libmicrohttpd is a small GNU library that adds an HTTP server to a C program.** You give it one callback, and it calls that for every request. It is the usual choice when a program that already exists needs a web interface, because it can run inside the event loop you already have.

## Lessons so far

1. [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|01 — libmicrohttpd]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the libmicrohttpd way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What libmicrohttpd is and a first server**: one callback for everything — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
2. **02 — Routing**: dispatching on URL and method yourself
3. **03 — Reading the body**: the `con_cls` state machine, the post processor — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
4. **04 — Threading modes**: thread per connection, a pool, or driving it from your own loop — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
5. **05 — Structure**: a handler table and per-request state
6. **06 — Input validation**: parsing input with a JSON library, checking every field
7. **07 — Errors and structured responses**: status codes, and the memory modes that decide who frees what, and one response shape for success and failure — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
8. **08 — Data**: libpq from inside a handler

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with `MHD_lookup_connection_value` for query parameters, keyset pagination
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with routing on the path prefix or a header
11. **11 — API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **12 — Authentication**: the basic and digest auth helpers, TLS with GnuTLS
13. **13 — Authorization**: roles and owning your own orders, with permission checks in the dispatcher
14. **14 — Security**: connection limits, timeouts, memory limits
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: curl-driven tests, ASan

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with a worker thread
19. **19 — Caching**: caching hot reads with hiredis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with libmicrohttpd's connection upgrade

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with why GraphQL in C is rarely worth it, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with protobuf-c and the gRPC core
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
26. **26 — Calling other services safely**: libcurl with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with syslog and counters
28. **28 — Production config and Docker**: hardening, and a reverse proxy in front; a hardened Docker image behind nginx, Docker Compose for the whole system
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/ulfius/index|Ulfius]] — routing and JSON on top of libmicrohttpd

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
