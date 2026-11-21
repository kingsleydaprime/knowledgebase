# ASP.NET Core (C# Backend)

## What ASP.NET Core is

**ASP.NET Core is Microsoft's framework for building websites and APIs in C#.** It is one of the fastest mainstream frameworks, and many companies use it.

**~2,900 words across 4 notes.** Built August 2026. `[reference]`.

Minimal APIs and MVC are two styles *within* ASP.NET Core, not competing frameworks, so they share this one subject.

> **The one idea:** ASP.NET Core is **batteries-included but unopinionated about structure.** DI, configuration, logging, health checks, rate limiting and OpenAPI are in the box; **layering, boundaries and where your business logic lives are entirely yours** → [[backend/03-structuring-a-backend/index|structuring a backend]].

## Lessons so far

1. [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|ASP.NET Core and the Pipeline]] — **[Intermediate]** — the two-phase program, **middleware order as behaviour**, DI lifetimes, configuration, Kestrel
2. [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|Minimal APIs and MVC]] — **[Intermediate]** — the two styles, which to pick, validation, `ProblemDetails`, and **how the OpenAPI story differs from FastAPI's**
3. [[backend/frameworks/aspnet-core/03-data-access|Data Access]] — **[Intermediate]** — EF Core and Dapper, **the three mistakes behind most slow endpoints**, migrations, concurrency
4. [[backend/frameworks/aspnet-core/04-testing-and-production|Testing and Production]] — **[Intermediate]** — `WebApplicationFactory`, Testcontainers, OpenTelemetry, Docker, **and the production checklist**

## The things worth carrying

1. **Register before `Build()`, compose after.** Two phases, and mixing them is the first thing to go wrong → [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|01]]
2. **Middleware order *is* behaviour** — `UseAuthorization` before `UseAuthentication` makes every request anonymous, silently → [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|01]]
3. **A scoped service injected into middleware or a singleton is captured forever** → [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|01]]
4. **Use `IHttpClientFactory`.** A new `HttpClient` per request exhausts sockets; a static one misses DNS changes → [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|01]]
5. **Route constraints match; they don't validate.** `{id:int}` gives a 404, not a 400 → [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|02]]
6. **Minimal APIs scale fine — but *you* impose the structure**, or you get a 900-line `Program.cs` → [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|02]]
7. **`.ToList()` in the wrong place moves the filter out of SQL** and loads the table → [[backend/frameworks/aspnet-core/03-data-access|03]]
8. **`Include` or you have an N+1.** Watch the query count, not the wall clock → [[backend/frameworks/aspnet-core/03-data-access|03]]
9. **`AsNoTracking` on read-only queries is free performance** → [[backend/frameworks/aspnet-core/03-data-access|03]]
10. **Read generated migrations. A rename can be detected as drop-and-create** → [[backend/frameworks/aspnet-core/03-data-access|03]]
11. **`HasPrecision` on money.** Floating-point currency is a bug at the schema level → [[backend/frameworks/aspnet-core/03-data-access|03]]
12. **Test against a real database in Testcontainers**, not the In-Memory provider — which passes tests that fail against real SQL → [[backend/frameworks/aspnet-core/04-testing-and-production|04]]
13. **Liveness and readiness are different questions.** A database check in liveness restarts pods over a blip → [[backend/frameworks/aspnet-core/04-testing-and-production|04]]

## How it compares

| | ASP.NET Core | [[backend/frameworks/fastapi/01-fastapi\|FastAPI]] | [[backend/frameworks/spring-boot/index\|Spring Boot]] | [[backend/frameworks/express/index\|Express]] |
|---|---|---|---|---|
| **DI** | **Built in** | `Depends()` | Built in | Manual |
| **Validation** | DataAnnotations / FluentValidation | **Pydantic — same model as the schema** | Bean Validation | Manual (zod) |
| **OpenAPI** | Generated from types + attributes | **Derived from the validator — cannot drift** | Add-on | Add-on |
| **Concurrency** | **async, thread pool** | ASGI event loop | Virtual threads (21+) | Event loop |
| **Structure** | **Yours** | Yours | Prescribed-ish | Yours |

**The comparison worth internalising is the OpenAPI row.** FastAPI derives the schema from the *same* Pydantic model that validates, so documentation and behaviour cannot diverge. ASP.NET Core generates the schema from types and attributes while validation may live in a separate FluentValidation class — **so drift is possible**, and it's a genuine structural difference rather than a maturity gap.

## The honest note

**`[reference]`** — no ASP.NET Core in this vault's [[projects/index|projects/]]; the backend work here is Node/Nest and Java/Spring.

**What would close the gap:**

1. **`dotnet new webapi`, one endpoint, EF Core against Postgres in Testcontainers.** An afternoon, and it makes all four notes concrete
2. **Cause the N+1 deliberately**, see it in the SQL log, fix it with `Include`, record the query counts
3. **Reverse `UseAuthentication` and `UseAuthorization`** and watch every request become anonymous with no error. **Note 01's central claim, verified in a minute**
4. **Write one `WebApplicationFactory` test** — it's the feature most worth stealing conceptually even if you work in another stack

**What's missing:** authentication and authorization in depth (JWT, cookies, policies, Identity), SignalR and WebSockets, background services and hosted workers, Blazor, gRPC, output caching, and YARP.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the ASP.NET Core way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What ASP.NET Core is and a first app**: `WebApplication`, the two phases, Kestrel — written in part: [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|ASP.NET Core and the Pipeline]]
2. **Endpoints**: Minimal APIs and controllers, and which to pick — written in part: [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|Minimal APIs and MVC]]
3. **The middleware pipeline**: why order is behaviour — written in part: [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|ASP.NET Core and the Pipeline]]
4. **Structure**: endpoint groups and feature folders, so `Program.cs` stays small — written in part: [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|Minimal APIs and MVC]]
5. **Dependency injection**: lifetimes, and the captured scoped service — written in part: [[backend/frameworks/aspnet-core/01-aspnet-core-and-the-pipeline|ASP.NET Core and the Pipeline]]
6. **Input validation**: DataAnnotations and FluentValidation — written in part: [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|Minimal APIs and MVC]]
7. **Errors and structured responses**: `ProblemDetails` and the exception handler, and one response shape for success and failure — written in part: [[backend/frameworks/aspnet-core/02-minimal-apis-and-mvc|Minimal APIs and MVC]]
8. **Data**: EF Core, Dapper, migrations, concurrency — written in part: [[backend/frameworks/aspnet-core/03-data-access|Data Access]]

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with EF Core `Skip`/`Take`, keyset pagination and query binding
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with Asp.Versioning: URL, header, query and media type
11. **API docs**: generating OpenAPI docs with the built-in OpenAPI generator and Scalar

**Part 3: who can do what**

12. **Authentication**: authentication schemes, JWT bearer, cookies, policies, Identity
13. **Authorization**: roles and owning your own orders, with authorization policies and resource-based handlers
14. **Security**: CORS, the rate limiting middleware, output caching, `IHttpClientFactory`, background services
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `WebApplicationFactory` and Testcontainers — written in part: [[backend/frameworks/aspnet-core/04-testing-and-production|Testing and Production]]

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with hosted services and a queue
19. **Caching**: caching hot reads with `HybridCache` on Redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with SignalR

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with Hot Chocolate, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with Grpc.AspNetCore
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official C# SDK, ModelContextProtocol.AspNetCore
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over MassTransit on RabbitMQ, the outbox pattern
26. **Calling other services safely**: `IHttpClientFactory` with Polly resilience, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with OpenTelemetry and health checks
28. **Production config and Docker**: configuration, OpenTelemetry, health checks, Docker; a Docker image and .NET Aspire, Docker Compose for the whole system — written in part: [[backend/frameworks/aspnet-core/04-testing-and-production|Testing and Production]]
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[languages/07-csharp/index|the C# course]] — the language, per [[languages/index|the rule]]
- [[backend/frameworks/index|frameworks/]] · [[backend/index|the backend course]]
