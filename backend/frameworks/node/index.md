# Node.js (JavaScript Backend)

## What Node.js is

**Node.js is the program that runs JavaScript outside the browser, and it can be a web server on its own, with no framework.** It comes with a built-in `http` module, so you can take a request and send a response with nothing else installed. Express and NestJS are both built on top of it, so what you learn here is true in both of them.

**Concurrency model: [[backend/01-foundations/04-runtime-and-concurrency-models/index|event loop]].** One thread runs your JavaScript. Waiting on the network or disk is handed to libuv, and the results come back as callbacks. Almost everything particular to backend JavaScript follows from that one fact: async APIs everywhere, "never block the event loop", `cluster` for more cores, and `worker_threads` for heavy CPU work.

## Lessons so far

1. [[backend/frameworks/node/01-env-validation|01 — Validating .env in nodejs]]
2. [[backend/frameworks/node/02-error-handling|02 — Ways to handle errors in Node.js]]

## The runtime facts that matter most
- **The event loop is single-threaded.** Any sync work blocks every pending request → the signature p99 spike with flat p50. → [[backend/interview/01-production-debugging|p99 debugging]]
- **libuv's thread pool defaults to 4** (`UV_THREADPOOL_SIZE`) and serves `fs`, DNS, and some crypto — network I/O does *not* use it.
- **`worker_threads` for CPU, `cluster`/replicas for cores.** They solve different problems.
- **`Buffer.alloc` not `new Buffer`** — the deprecated form returned uninitialised memory and was a type-confusion trap. → [[backend/interview/02-node-runtime-and-api|Q2]]

→ Full depth in [[backend/interview/02-node-runtime-and-api|the Node runtime interview bank]], which was written from a real interview.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Node.js way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What Node.js is and a first server**: `node:http`, `createServer`, one thread and the event loop
2. **02 — Routing by hand**: parsing `req.url` with `URL`, matching method and path, a tiny route table
3. **03 — Reading and writing**: streaming the body, parsing JSON safely, body size limits, status and headers
4. **04 — Middleware without a framework**: a `compose()` function, why order matters, and why Express exists
5. **05 — Structuring a Node service**: feature folders, ES modules, one composition root
6. **06 — Input validation**: zod at the boundary, so what comes in is typed
7. **07 — Errors and structured responses**: the four error channels, why `uncaughtException` isn't recovery, errors to status codes, and one response shape for success and failure — written in part: [[backend/frameworks/node/02-error-handling|Ways to handle errors in Node.js]]
8. **08 — Data**: `pg` and a connection pool, parameterised queries, transactions, migrations

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with hand-built query parsing
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with routing by path or header yourself
11. **11 — API docs**: generating OpenAPI docs with an OpenAPI file written alongside the code

**Part 3: who can do what**

12. **12 — Authentication**: password hashing, sessions versus JWTs, checking permissions
13. **13 — Authorization**: roles and owning your own orders, with a `can(user, action, thing)` function
14. **14 — Security**: CORS and security headers by hand, rate limiting, uploads as streams
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `node:test`, testing a server without opening a port, fakes

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with BullMQ on Redis
19. **19 — Caching**: caching hot reads with node-redis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with server-sent events and `ws`

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with graphql-yoga on `node:http`, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with @grpc/grpc-js
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official TypeScript SDK (`@modelcontextprotocol/sdk`) on `node:http`
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over Redis streams or RabbitMQ, the outbox pattern
26. **26 — Calling other services safely**: `fetch` with `AbortSignal.timeout`, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with pino and OpenTelemetry
28. **28 — Production config and Docker**: validating env at boot, structured logging, graceful shutdown, `cluster` versus `worker_threads`, never blocking the loop; Docker, `node --watch` vs production start, Docker Compose for the whole system — written in part: [[backend/frameworks/node/01-env-validation|Validating .env in nodejs]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/express/index|Express]] · [[backend/frameworks/nestjs/index|NestJS]] — the two frameworks built on Node
- [[networking/09-sockets-and-the-network-api|Sockets & epoll]]

## About this subject

Built from real Node and Nest work in [[projects/index|projects/]]. Until November 2026 Node, Express and NestJS shared one subject, "JavaScript Backends". They were split so each one can teach the whole backend course in its own way.
