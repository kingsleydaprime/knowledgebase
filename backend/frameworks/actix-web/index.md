# Actix Web (Rust Backend)

## What Actix Web is

**Actix Web is a fast, mature framework for building web servers in Rust.** It is the main alternative to Axum. It has its own middleware system and gives each CPU core its own worker with its own state.

## Lessons so far

1. [[backend/frameworks/actix-web/01-actix-web|Actix Web]]

## Actix Web next to Axum

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros |
| Ecosystem reuse | high | lower |
| Model | shared state | thread-per-core |

[[backend/frameworks/axum/index|Axum]] is the usual default, mostly because of `tower`. Actix is mature, marginally faster, and a fine choice. Its async rules are the same → [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]].

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Actix Web way: a food-ordering API with a well-designed REST interface, GraphQL, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Actix Web is and a first server**: `HttpServer`, `App`, and how it differs from Axum — written in part: [[backend/frameworks/actix-web/01-actix-web|Actix Web]]
2. **Routing**: attribute macros, `web::resource`, scopes
3. **Middleware**: `wrap`, `wrap_fn`, and the `Transform` trait
4. **Structure**: a `configure` function per feature
5. **State**: `web::Data`, and state per worker in a thread-per-core model
6. **Input validation**: `web::Json<T>`, extractor config, validation crates
7. **Errors and structured responses**: the `ResponseError` trait, and one response shape for success and failure
8. **Data**: sqlx with Actix, and `web::block` for blocking work

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with `web::Query` into a filter struct, keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a `web::scope` per version, or guards on a header
11. **API docs**: generating OpenAPI docs with utoipa

**Part 3: who can do what**

12. **Authentication**: `FromRequest` extractors for auth, sessions and identity
13. **Authorization**: roles and owning your own orders, with extractors and guards for permissions
14. **Security**: `actix-cors`, rate limiting with `actix-governor`, multipart uploads
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `actix_web::test`

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with background tasks on Redis
19. **Caching**: caching hot reads with deadpool-redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with actix-ws

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with async-graphql, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with tonic next to Actix

**Part 6: more than one service**

23. **Splitting out a microservice**: a separate notifications service, events over NATS or RabbitMQ with lapin, the outbox pattern
24. **Calling other services safely**: awc or reqwest with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

25. **Observability**: logs, request IDs across services, metrics and tracing with tracing-actix-web and OpenTelemetry
26. **Production config and Docker**: worker count, graceful shutdown, tracing; a small Docker image, Docker Compose for the whole system
27. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/axum/index|Axum]] — the other main Rust option
- [[languages/03-rust/index|The Rust course]]

## About this subject

`[reference]`. Until November 2026 Actix Web was one section inside the Rust subject, which is now [[backend/frameworks/axum/index|Axum]].
