# net/http (Go Backend)

## What net/http is

**`net/http` is the package that comes with Go for writing web servers, and in Go it is often all you need.** Go was made for network servers, so its standard library has a production-grade HTTP server and router built in. This subject builds a full production backend on it, and adds only small, focused packages where the standard library really has nothing (a Postgres driver, JWTs, Redis).

## What you'll build

The whole subject builds **one** app, a step at a time: **Mama Put API**, the backend for a roadside food seller whose customers now order on their phones. It's the same app the [[backend/frameworks/express/index|Express]] subject builds, written the Go way.

It starts in lesson 1 as a server that answers "Mama Put is open!". By lesson 29 it's a production system:

1. A main API with a menu, orders, customer accounts and kitchen-staff roles, stored in PostgreSQL.
2. A well-designed API: one response shape everywhere, pagination, filtering, searching, sorting and field selection, two versions running side by side, and OpenAPI docs.
3. Payments through Paystack, webhooks in and out, idempotency so nothing happens twice, background jobs, Redis caching, and a kitchen screen that shows new orders live.
4. The same data offered over **GraphQL**, and as an **MCP server** so AI assistants can browse the menu and order for a customer, and a **second service** for notifications that the main API talks to over events and **gRPC**.
5. Tests at every level, logs, metrics and tracing across both services, Docker for the whole system, and automatic deployment when you push.

Every lesson ends with **your project so far** (the folder tree and what each file holds) and explains **the Go it used**, so you don't need to know the language well before you start.

## Lessons

**Part 1: the core backend**

1. [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|What net/http Is, and Your First Server]]: a Go module, the `Handler` interface, writing status, headers and body in order, and why `ListenAndServe` has no timeouts.
2. [[backend/frameworks/net-http/02-routing|Routing]]: Go 1.22 patterns, path values, query values, bodies, status codes, which pattern wins, and a mutex proved with the race detector.
3. [[backend/frameworks/net-http/03-middleware|Middleware]]: `func(Handler) Handler`, logging with a status recorder, catching panics, a staff key, and why order is behaviour.
4. [[backend/frameworks/net-http/04-structuring-a-go-service|Structuring a Go Service]]: `cmd/` and `internal/`, feature packages, handlers as methods, sentinel errors, and the one-way import rule.
5. [[backend/frameworks/net-http/05-wiring-dependencies|Wiring Dependencies]]: interfaces declared by the user, a clock as a dependency, `run` as the composition root, and the first table-driven tests.
6. [[backend/frameworks/net-http/06-validation|Input Validation]]: strict JSON decoding, `MaxBytesReader`, `go-playground/validator`, a generic `Decode[T]`, and validation versus business rules.
7. [[backend/frameworks/net-http/07-errors|Errors and Structured Responses]]: wrapping, one `apperr` type, handlers that return errors, problem details, request IDs in the context, and the `{ data }` envelope.
8. [[backend/frameworks/net-http/08-data-with-postgres|Data with PostgreSQL]]: pgx and a sized pool, embedded migrations, placeholders and SQL injection, a context on every query, and a transaction so the last plate goes to one customer.

**Part 2: designing the API properly**

9. [[backend/frameworks/net-http/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]]: a query reader that collects every mistake, allow-lists, a safe `WHERE` builder, offset and cursor pagination, and the indexes behind them.
10. [[backend/frameworks/net-http/10-versioning|Versioning]]: breaking changes, the four styles, domain types versus wire types, prices stored in kobo, v1 and v2 side by side, and deprecating v1 with `Deprecation`, `Sunset` and a 410.
11. [[backend/frameworks/net-http/11-api-docs|API Docs with OpenAPI]]: spec-first, v2's types generated with oapi-codegen as a Go tool, Swagger UI for both versions, and a contract test with kin-openapi.

**Part 3: who can do what**

12. [[backend/frameworks/net-http/12-authentication|Authentication]]: argon2id in the PHC format, sessions versus JWTs, golang-jwt with every option pinned, rotating refresh tokens that catch thieves, and the identity in the context.
13. [[backend/frameworks/net-http/13-authorization|Authorization]]: a policy as a table with default deny, `RequirePermission`, ownership checks in services that take the actor, and 401 versus 403 versus 404.
14. [[backend/frameworks/net-http/14-security|Security]]: security headers and CORS by hand, rate limiting with `x/time/rate`, trusting proxies, size limits, and photo uploads checked to the pixel inside an `os.Root`.
15. [[backend/frameworks/net-http/15-idempotency|Idempotency]]: the `Idempotency-Key` header, a buffering middleware that saves before it sends, and a unique constraint in the order's own transaction.
16. [[backend/frameworks/net-http/16-testing|Testing]]: table tests with fakes, the whole app in memory with `httptest`, a permissions table, integration tests behind a build tag, and store contract tests.

**Part 4: what real products need**

17. [[backend/frameworks/net-http/17-payments-and-webhooks|Payments and Webhooks]]: a Paystack client with timeouts, one idempotent `Settle`, HMAC-checked webhooks on their own middleware chain, and signed webhooks out from a Postgres queue.
18. [[backend/frameworks/net-http/18-background-jobs|Background Jobs and Queues]]: asynq on Redis, a worker program, weighted queues and a semaphore, schedules that are safe with many workers, and a sweeper for what Redis loses.
19. [[backend/frameworks/net-http/19-caching|Caching with Redis]]: a fail-open cache with go-redis, `singleflight` against stampedes, generation-based invalidation, hand-written ETags, and shared rate limits.
20. [[backend/frameworks/net-http/20-real-time|Real-time Updates]]: server-sent events with `http.ResponseController`, one writer goroutine, a hub that drops slow screens, snapshots, Redis pub/sub and one-use tickets.

**Part 5: other ways to talk**

21. [[backend/frameworks/net-http/21-graphql|GraphQL]]: gqlgen bound to the domain types, the binding trap for private fields, a per-request dataloader across goroutines, an error presenter and complexity limits that count lists.
22. [[backend/frameworks/net-http/22-grpc|gRPC]]: a `.proto` contract, buf and both generators as Go tools, interceptors for errors and panics, deadlines that reach the database, streaming, `buf breaking` and `bufconn` tests.
23. [[backend/frameworks/net-http/23-mcp-server|Building an MCP Server]]: typed tools with the official Go SDK, schemas from struct tags, errors the model may read, a resource and a prompt, and stateless Streamable HTTP.
24. [[backend/frameworks/net-http/24-mcp-in-production|MCP in Production]]: OAuth tokens checked against a JWKS, always a customer with scopes on top, quote then order, asking the person without a session, prompt injection and a fail-closed daily cap.

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events, and the outbox pattern. *(to write)*
26. **Calling other services safely**: timeouts and context, retries, circuit breakers, and service-to-service auth. *(to write)*

**Part 7: production**

27. **Observability**: `slog`, request IDs across services, Prometheus metrics and OpenTelemetry tracing. *(to write)*
28. **Production config and Docker**: validated config, health checks, graceful shutdown, a tiny Docker image, and Docker Compose for the whole system. *(to write)*
29. **CI and deployment**: GitHub Actions running the tests, migrations on deploy, deploying to a real server, and rolling back. *(to write)*

## What to know

- **Everything is `http.Handler`.** One interface with one method. A Chi router, your own function and every middleware in the ecosystem all satisfy it, so they fit together with no adapters.
- **Never ship `http.ListenAndServe`.** It has no timeouts. Build an `http.Server` with them.
- **Every request has its own goroutine.** Shared data needs a lock, or a database. Run with `-race` while you develop.
- **Start with the standard library, add [[backend/frameworks/chi/index|Chi]] when route groups start hurting.** Chi uses the same types, so the move is mechanical.
- **What Go makes you write yourself:** validation (or take `go-playground/validator`), the error-to-status mapping, and a `ResponseWriter` wrapper to see the status. Each is written once, in lessons 3, 6 and 7.

## Related

- [[backend/frameworks/index|All frameworks]]
- [[languages/02-go/index|The Go course]] — the language
- [[backend/frameworks/chi/index|Chi]] — the same app with a router on top
- [[backend/frameworks/gin/index|Gin]] — the same app with a full framework
- [[backend/frameworks/express/index|Express]] — the same app in TypeScript
- [[backend/index|The backend course]] — the ideas these lessons put into practice

## About this subject

Written for Go 1.24 or later. Lessons 1–24 were written in November 2026; the rest are being written in order.
