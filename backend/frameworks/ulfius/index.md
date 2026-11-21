# Ulfius (C Backend)

## What Ulfius is

**Ulfius is a C framework for building REST APIs, built on top of libmicrohttpd.** It adds the parts that library leaves out: routes with path parameters, JSON, and a chain of callbacks that works like middleware. It is the closest thing C has to a normal REST framework.

## Lessons so far

1. [[backend/frameworks/ulfius/01-ulfius|Ulfius]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Ulfius way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Ulfius is and a first endpoint**: routing and JSON on top of libmicrohttpd — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
2. **Routing**: endpoints, prefixes, URL params — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
3. **Callback chains**: priorities and `U_CALLBACK_CONTINUE`, used like middleware — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
4. **Structure**: an endpoint file per feature
5. **Shared data**: `user_data` in place of DI
6. **Input validation**: Jansson, checking every field
7. **Errors and structured responses**: status codes and error bodies, and one response shape for success and failure
8. **Data**: Hoel, the same author's database library

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with `u_map_get` on `map_url`, keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with an endpoint prefix per version
11. **API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **Authentication**: an auth callback, JWTs
13. **Authorization**: roles and owning your own orders, with an auth callback with a higher priority
14. **Security**: CORS, uploads, WebSockets
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: Ulfius's client functions in tests

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with a worker thread
19. **Caching**: caching hot reads with hiredis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with Ulfius WebSockets

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with why GraphQL in C is rarely worth it, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with protobuf-c and the gRPC core
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
26. **Calling other services safely**: Ulfius's client functions with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with Yder logging and counters
28. **Production config and Docker**: TLS, hardening, a reverse proxy; a hardened Docker image behind nginx, Docker Compose for the whole system
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]] — what Ulfius is built on

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
