# Gin (Go Backend)

## What Gin is

**Gin is the most popular web framework for Go. It gives you routing, request binding and validation, and its own context type.** Your handlers take a `*gin.Context` instead of the standard `http.ResponseWriter` and `*http.Request`. You get a lot of helpers, but your code belongs to Gin.

## Lessons so far

1. [[backend/frameworks/gin/01-gin|Gin]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Gin way: a food-ordering API with a well-designed REST interface, GraphQL, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Gin is and a first server**: `gin.Default()`, `*gin.Context`, and the lock-in trade — written in part: [[backend/frameworks/gin/01-gin|Gin]]
2. **Routing**: groups, `c.Param`, `c.Query` — written in part: [[backend/frameworks/gin/01-gin|Gin]]
3. **Middleware**: `gin.HandlerFunc`, `c.Next`, `c.Abort`
4. **Structure**: a route group per feature, handlers kept thin
5. **Wiring**: dependencies through structs and closures, and why `c.Set` isn't DI
6. **Input validation**: `ShouldBind*` and `binding` tags — written in part: [[backend/frameworks/gin/01-gin|Gin]]
7. **Errors and structured responses**: `c.Error`, an error middleware, `AbortWithStatusJSON`, and one response shape for success and failure
8. **Data**: GORM or sqlc behind a repository

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with `ShouldBindQuery` into a filter struct, keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a route group per version
11. **API docs**: generating OpenAPI docs with swaggo/swag

**Part 3: who can do what**

12. **Authentication**: JWT middleware and role checks
13. **Authorization**: roles and owning your own orders, with role middleware and ownership checks
14. **Security**: `gin-contrib/cors`, rate limiting, `c.FormFile` uploads
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `httptest` with `gin.TestMode`

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with asynq on Redis
19. **Caching**: caching hot reads with go-redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with server-sent events with `c.Stream`

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with gqlgen on Gin, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with grpc-go next to Gin

**Part 6: more than one service**

23. **Splitting out a microservice**: a separate notifications service, events over NATS, the outbox pattern
24. **Calling other services safely**: `http.Client` with timeouts and context, circuit breakers, service-to-service auth

**Part 7: production**

25. **Observability**: logs, request IDs across services, metrics and tracing with Prometheus middleware and OpenTelemetry
26. **Production config and Docker**: release mode, trusted proxies and `ClientIP`, graceful shutdown through `http.Server`; a scratch Docker image, Docker Compose for the whole system
27. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/chi/index|Chi]] — the stdlib-compatible alternative, and the full comparison
- [[backend/frameworks/net-http/index|net/http]] — what Gin sits on
- [[languages/02-go/index|The Go course]]

## About this subject

`[reference]`. Until November 2026 Chi and Gin were one lesson inside the Go subject, which is now [[backend/frameworks/net-http/index|net/http]].
