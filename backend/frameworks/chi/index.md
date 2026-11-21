# Chi (Go Backend)

## What Chi is

**Chi is a small router for Go that adds route groups and shared middleware to the standard library, and changes nothing else.** Its handlers and middleware are ordinary `net/http` types. So you can add Chi to a stdlib server, or take it out again, without rewriting a single handler.

## Lessons so far

1. [[backend/frameworks/chi/01-chi|Chi]]

**Because Chi is `net/http`**, most of the plan below uses the same tools as [[backend/frameworks/net-http/index|net/http]]. Its lessons focus on what Chi changes: grouping, its middleware package, and loading shared data once per route group.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Chi way: a food-ordering API with a well-designed REST interface, GraphQL, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Chi is**: what a router still adds after Go 1.22, and how Chi stays `net/http` compatible — written in part: [[backend/frameworks/chi/01-chi|Chi]]
2. **Routing**: `r.Route`, `r.Group`, URL params, mounting sub-routers — written in part: [[backend/frameworks/chi/01-chi|Chi]]
3. **Middleware**: Chi's `middleware` package: RequestID, RealIP, Recoverer, Timeout, `WrapResponseWriter`
4. **Structure**: a router per feature, mounted in `main`
5. **Wiring**: handlers as methods on a struct that holds their dependencies
6. **Input validation**: binding and rendering with `go-chi/render`, or a validator
7. **Errors and structured responses**: one error renderer for the whole router, and one response shape for success and failure
8. **Data**: loading a resource once with context middleware, `database/sql` underneath

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with a query-parsing middleware and keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a sub-router per version with `r.Route("/v1", ...)`
11. **API docs**: generating OpenAPI docs with oapi-codegen with Chi

**Part 3: who can do what**

12. **Authentication**: `jwtauth` and auth per route group
13. **Authorization**: roles and owning your own orders, with per-group auth middleware and ownership checks
14. **Security**: `go-chi/cors`, `httprate`, throttling
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `httptest` against a Chi router

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with asynq on Redis
19. **Caching**: caching hot reads with go-redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with server-sent events

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with gqlgen mounted on Chi, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with grpc-go next to Chi

**Part 6: more than one service**

23. **Splitting out a microservice**: a separate notifications service, events over NATS, the outbox pattern
24. **Calling other services safely**: `http.Client` with timeouts and context, circuit breakers, service-to-service auth

**Part 7: production**

25. **Observability**: logs, request IDs across services, metrics and tracing with slog, Prometheus and OpenTelemetry
26. **Production config and Docker**: timeouts, shutdown and observability, and how to swap Chi out later; a scratch Docker image, Docker Compose for the whole system
27. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/net-http/index|net/http]] — what Chi wraps
- [[backend/frameworks/gin/index|Gin]] — the batteries-included alternative
- [[languages/02-go/index|The Go course]]

## About this subject

`[reference]`. Until November 2026 Chi and Gin were one lesson inside the Go subject, which is now [[backend/frameworks/net-http/index|net/http]].
