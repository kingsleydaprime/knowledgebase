# Crow (C++ Backend)

## What Crow is

**Crow is a small C++ web framework that you add by including one header file.** Its routes look like Python's Flask, and it runs handlers on a thread pool. It is good for putting a small API inside an existing C++ program, not for building a large service.

## Lessons so far

1. [[backend/frameworks/crow/01-crow|Crow]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Crow way: a food-ordering API with a well-designed REST interface, GraphQL, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Crow is and a first app**: the single header, `CROW_ROUTE`, and where it fits — written in part: [[backend/frameworks/crow/01-crow|Crow]]
2. **Routing**: typed params, methods, blueprints
3. **Middleware**: Crow middleware structs, `before_handle` and `after_handle`
4. **Structure**: a blueprint per feature
5. **Wiring**: app context, and passing dependencies into lambdas
6. **Input validation**: `crow::json`, checking every field
7. **Errors and structured responses**: `crow::response` codes and exception handling, and one response shape for success and failure
8. **Data**: bringing your own database library, such as libpqxx, and pooling

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with parsing `req.url_params`, keyset pagination in SQL
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a blueprint per version
11. **API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **Authentication**: a middleware that checks a token
13. **Authorization**: roles and owning your own orders, with middleware that checks roles and ownership
14. **Security**: CORS middleware, multipart, limits
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `app.handle` without a socket

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with a worker thread pool
19. **Caching**: caching hot reads with redis-plus-plus, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with Crow WebSockets

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with cppgraphqlgen, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with gRPC C++

**Part 6: more than one service**

23. **Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
24. **Calling other services safely**: cpr or Beast with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

25. **Observability**: logs, request IDs across services, metrics and tracing with spdlog and prometheus-cpp
26. **Production config and Docker**: multithreading, logging, embedding Crow in an existing program; a Docker image, Docker Compose for the whole system
27. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/drogon/index|Drogon]] — the full-stack C++ option
- [[languages/05-cpp/index|The C++ course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C++ subject, which is now [[backend/frameworks/drogon/index|Drogon]].
