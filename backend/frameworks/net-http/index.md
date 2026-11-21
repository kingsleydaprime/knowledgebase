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

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination, allow-lists, and turning query values into safe SQL. *(to write)*
10. **Versioning**: breaking changes, the path, header, media-type and query styles, v1 and v2 side by side, and deprecating a version. *(to write)*
11. **API docs with OpenAPI**: a spec, generated docs for both versions, and keeping it honest. *(to write)*

**Part 3: who can do what**

12. **Authentication**: argon2id password hashing, sessions versus JWTs, rotating refresh tokens, and the user in the context. *(to write)*
13. **Authorization**: a policy written once, role and ownership checks, and 401 versus 403 versus 404. *(to write)*
14. **Security**: security headers, CORS, rate limiting with `x/time/rate`, trusting proxies, size limits and timeouts, and safe photo uploads. *(to write)*
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice. *(to write)*
16. [[backend/frameworks/net-http/16-testing|Testing]]: `httptest`, fakes, table-driven tests, integration tests against a real database, and the race detector. *(an older reference note, being rewritten)*

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks to a delivery partner. *(to write)*
18. **Background jobs and queues**: work the customer shouldn't wait for, on Redis. *(to write)*
19. **Caching with Redis**: caching the menu with go-redis, and keeping the cache honest. *(to write)*
20. **Real-time updates**: a live kitchen screen with server-sent events. *(to write)*

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with gqlgen, and when it beats REST. *(to write)*
22. **gRPC**: Protocol Buffers and a gRPC service with grpc-go. *(to write)*
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official Go SDK. *(to write)*
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits. *(to write)*

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

Written for Go 1.24 or later. Lessons 1–8 were written in November 2026; the rest are being written in order. Until then, lesson 16 is an older reference note that covers the same ground more briefly.
