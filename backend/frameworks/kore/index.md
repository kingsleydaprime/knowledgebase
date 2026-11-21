# Kore (C Backend)

## What Kore is

**Kore is a full web framework for C, built around security.** Routing, TLS, WebSockets and PostgreSQL support are built in. Its worker processes run with the least power possible, so if an attacker breaks one, the damage stays small.

## Lessons so far

1. [[backend/frameworks/kore/01-kore|Kore]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Kore way: a food-ordering API with a well-designed REST interface, GraphQL, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Kore is and a first app**: a handler, a config file, and privilege separation — written in part: [[backend/frameworks/kore/01-kore|Kore]]
2. **Routing and config**: routes, regex params, methods
3. **Hooks**: parent and worker hooks
4. **Structure**: the `kodev` project layout
5. **Validation**: Kore's built-in parameter validators
6. **Input validation**: Kore's JSON API
7. **Errors and structured responses**: status codes and failure paths in handlers, and one response shape for success and failure
8. **Data**: async PostgreSQL queries with `kore_pgsql`

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with Kore's validated parameters, keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with route blocks per version
11. **API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **Authentication**: Kore's authentication blocks
13. **Authorization**: roles and owning your own orders, with Kore authentication blocks and ownership checks
14. **Security**: privilege separation, `seccomp`, TLS by default — written in part: [[backend/frameworks/kore/01-kore|Kore]]
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Background work**: tasks and WebSockets

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with Kore tasks
19. **Caching**: caching hot reads with hiredis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with Kore WebSockets

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with why GraphQL in C is rarely worth it, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with protobuf-c and the gRPC core

**Part 6: more than one service**

23. **Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
24. **Calling other services safely**: Kore's curl integration, circuit breakers, service-to-service auth

**Part 7: production**

25. **Observability**: logs, request IDs across services, metrics and tracing with Kore's logging and counters
26. **Production config and Docker**: building with `kodev`, deploying a Kore binary; a Kore build in Docker, Docker Compose for the whole system
27. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
