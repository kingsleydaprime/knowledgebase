# net/http (Go Backend)

## What net/http is

**net/http is the package built into Go for writing web servers, and in Go it is often all you need.** Go was made for exactly this, so a small amount of code goes a long way.

**Concurrency model: goroutines** — green threads, since Go 1.0. You write blocking code; the runtime multiplexes onto OS threads. No `async`/`await`, so no "coloured function" split in the ecosystem. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]]

**~11,000 words across 6 notes.** `[reference]` — no Go service in this vault yet. Assumes [[languages/02-go/index|the Go course]] and the [[backend/index|backend course]]; these notes cover only what those don't.

> **The thing that makes Go's HTTP ecosystem different:** everything is `http.Handler`, one interface with one method. A Chi router, a Gin engine, your own function, and every middleware in the ecosystem all satisfy it — so they interoperate without adapters. Most ecosystems have framework-specific middleware that can't be reused; Go got composability by agreeing on the narrowest possible interface early.

## Lessons so far

1. [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]] — **[Intermediate]** — the `Handler` interface, Go 1.22 routing, and the server configuration that separates a toy from production. **`http.ListenAndServe` has no timeouts**
2. [[backend/frameworks/net-http/02-middleware-as-composition|Middleware as Composition]] — **[Intermediate]** — `func(Handler) Handler`, the essential middleware, and why wrapping `ResponseWriter` breaks `Flusher` and `Hijacker`
3. [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]] — **[Intermediate]** — DI without a container, handlers as methods, and error→status mapping in one place
4. [[backend/frameworks/net-http/04-database-access|Database Access]] — **[Intermediate]** — `database/sql`, the pool settings that decide whether you survive load, and why Go is sceptical of ORMs
5. [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]] — **[Intermediate]** — `httptest`, fakes without a mocking framework, observability, and the container gotchas

## The stdlib-is-enough argument, honestly

Go 1.22 gave `http.ServeMux` method matching and path wildcards, which removed most of the reason to take a router dependency. `net/http` is a production HTTP server — not a toy you replace.

What the stdlib still doesn't give you: route groups with shared middleware, a chaining helper, correct `ResponseWriter` wrapping, and request validation. Each is 10–50 lines you write once.

**So: start with the stdlib, add [[backend/frameworks/chi/index|Chi]] when route grouping starts hurting.** The migration is mechanical because Chi uses the identical types. That deferrable framework decision is unusual — in most ecosystems it's load-bearing and early.

## The framework table

| | stdlib | [[backend/frameworks/chi/index\|Chi]] | [[backend/frameworks/gin/index\|Gin]] | Echo | Fiber |
|---|---|---|---|---|---|
| `net/http` compatible | ✅ | ✅ | partial | partial | ❌ |
| Route groups | ❌ | ✅ | ✅ | ✅ | ✅ |
| Binding + validation | ❌ | ❌ | ✅ | ✅ | ✅ |
| Lock-in | none | none | real | real | **total** |

Fiber is built on fasthttp and is **not** `net/http` compatible — you lose the entire middleware, tracing and metrics ecosystem for throughput you almost certainly don't need.

## What Go does badly here

- **No request validation in the stdlib.** You write it, or take `go-playground/validator`, or use Gin's binding
- **No dependency injection.** Deliberate, and it means wiring is explicit and verbose
- **`ResponseWriter` has no status getter** — a genuine design wart, and the reason every logging middleware wraps it
- **ORMs are weak by comparison.** `sqlc` is the good answer; GORM works and generates SQL you didn't write
- **Error handling is manual.** No `@ControllerAdvice`; you write the error→status switch. More code, and no framework knowledge needed to read it

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the net/http way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What net/http is and a first server**: `http.Handler`, and why `ListenAndServe` has no timeouts — written in part: [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]]
2. **Routing**: Go 1.22 `ServeMux` patterns: methods and path wildcards — written in part: [[backend/frameworks/net-http/01-net-http-in-depth|`net/http` in Depth]]
3. **Middleware**: `func(Handler) Handler`, and wrapping `ResponseWriter` correctly — written in part: [[backend/frameworks/net-http/02-middleware-as-composition|Middleware as Composition]]
4. **Structure**: package layout, handlers as methods — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
5. **Wiring**: DI in `main`, interfaces declared by the consumer — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
6. **Input validation**: strict JSON decoding, `go-playground/validator`
7. **Errors and structured responses**: mapping errors to status codes in one place, and one response shape for success and failure — written in part: [[backend/frameworks/net-http/03-structuring-a-go-service|Structuring a Go Service]]
8. **Data**: `database/sql`, pool settings, sqlc, migrations — written in part: [[backend/frameworks/net-http/04-database-access|Database Access]]

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with parsing `r.URL.Query()` into a filter struct, keyset pagination in SQL
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a mux per version, or header-based routing
11. **API docs**: generating OpenAPI docs with an OpenAPI spec with oapi-codegen

**Part 3: who can do what**

12. **Authentication**: JWT and session middleware, the user in `context`
13. **Authorization**: roles and owning your own orders, with middleware and service checks for roles and ownership
14. **Security**: CORS, rate limiting with `x/time/rate`, `MaxBytesReader` for uploads, idempotency
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `httptest`, fakes, table-driven tests — written in part: [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]]

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with a worker pool, or asynq on Redis
19. **Caching**: caching hot reads with go-redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with server-sent events and WebSockets

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with gqlgen, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with grpc-go
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official Go SDK on `net/http`
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over NATS, the outbox pattern
26. **Calling other services safely**: `http.Client` with timeouts and context, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with slog, Prometheus and OpenTelemetry
28. **Production config and Docker**: graceful shutdown, observability, containers; a scratch Docker image, Docker Compose for the whole system — written in part: [[backend/frameworks/net-http/05-testing-and-production|Testing and Production]]
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[languages/02-go/index|The Go course]] — the language
- [[backend/frameworks/axum/index|Axum]] — the other no-runtime option
- [[networking/09-sockets-and-the-network-api|Sockets]] — what `net/http` sits on
