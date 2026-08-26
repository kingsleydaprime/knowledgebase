# C# Backends — ASP.NET Core

**~2,900 words across 4 notes.** Built August 2026. `[reference]`.

**Flat notes by concern**, per [[backend/frameworks/README|the folder test]]: C# has **one dominant framework**. Minimal APIs and MVC are two styles *within* ASP.NET Core, not competing frameworks — so a note about one applies to the other, and the material is really about the language's approach.

> **The one idea:** ASP.NET Core is **batteries-included but unopinionated about structure.** DI, configuration, logging, health checks, rate limiting and OpenAPI are in the box; **layering, boundaries and where your business logic lives are entirely yours** → [[backend/03-structuring-a-backend/README|structuring a backend]].

## Reading order

1. [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|ASP.NET Core and the Pipeline]] — **[Intermediate]** — the two-phase program, **middleware order as behaviour**, DI lifetimes, configuration, Kestrel
2. [[backend/frameworks/csharp/02-minimal-apis-and-mvc|Minimal APIs and MVC]] — **[Intermediate]** — the two styles, which to pick, validation, `ProblemDetails`, and **how the OpenAPI story differs from FastAPI's**
3. [[backend/frameworks/csharp/03-data-access|Data Access]] — **[Intermediate]** — EF Core and Dapper, **the three mistakes behind most slow endpoints**, migrations, concurrency
4. [[backend/frameworks/csharp/04-testing-and-production|Testing and Production]] — **[Intermediate]** — `WebApplicationFactory`, Testcontainers, OpenTelemetry, Docker, **and the production checklist**

## The things worth carrying

1. **Register before `Build()`, compose after.** Two phases, and mixing them is the first thing to go wrong → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|01]]
2. **Middleware order *is* behaviour** — `UseAuthorization` before `UseAuthentication` makes every request anonymous, silently → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|01]]
3. **A scoped service injected into middleware or a singleton is captured forever** → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|01]]
4. **Use `IHttpClientFactory`.** A new `HttpClient` per request exhausts sockets; a static one misses DNS changes → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|01]]
5. **Route constraints match; they don't validate.** `{id:int}` gives a 404, not a 400 → [[backend/frameworks/csharp/02-minimal-apis-and-mvc|02]]
6. **Minimal APIs scale fine — but *you* impose the structure**, or you get a 900-line `Program.cs` → [[backend/frameworks/csharp/02-minimal-apis-and-mvc|02]]
7. **`.ToList()` in the wrong place moves the filter out of SQL** and loads the table → [[backend/frameworks/csharp/03-data-access|03]]
8. **`Include` or you have an N+1.** Watch the query count, not the wall clock → [[backend/frameworks/csharp/03-data-access|03]]
9. **`AsNoTracking` on read-only queries is free performance** → [[backend/frameworks/csharp/03-data-access|03]]
10. **Read generated migrations. A rename can be detected as drop-and-create** → [[backend/frameworks/csharp/03-data-access|03]]
11. **`HasPrecision` on money.** Floating-point currency is a bug at the schema level → [[backend/frameworks/csharp/03-data-access|03]]
12. **Test against a real database in Testcontainers**, not the In-Memory provider — which passes tests that fail against real SQL → [[backend/frameworks/csharp/04-testing-and-production|04]]
13. **Liveness and readiness are different questions.** A database check in liveness restarts pods over a blip → [[backend/frameworks/csharp/04-testing-and-production|04]]

## How it compares

| | ASP.NET Core | [[backend/frameworks/python/01-fastapi/README\|FastAPI]] | [[backend/frameworks/java/README\|Spring Boot]] | [[backend/frameworks/javascript/02-express/README\|Express]] |
|---|---|---|---|---|
| **DI** | **Built in** | `Depends()` | Built in | Manual |
| **Validation** | DataAnnotations / FluentValidation | **Pydantic — same model as the schema** | Bean Validation | Manual (zod) |
| **OpenAPI** | Generated from types + attributes | **Derived from the validator — cannot drift** | Add-on | Add-on |
| **Concurrency** | **async, thread pool** | ASGI event loop | Virtual threads (21+) | Event loop |
| **Structure** | **Yours** | Yours | Prescribed-ish | Yours |

**The comparison worth internalising is the OpenAPI row.** FastAPI derives the schema from the *same* Pydantic model that validates, so documentation and behaviour cannot diverge. ASP.NET Core generates the schema from types and attributes while validation may live in a separate FluentValidation class — **so drift is possible**, and it's a genuine structural difference rather than a maturity gap.

## The honest note

**`[reference]`** — no ASP.NET Core in this vault's [[projects/README|projects/]]; the backend work here is Node/Nest and Java/Spring.

**What would close the gap:**

1. **`dotnet new webapi`, one endpoint, EF Core against Postgres in Testcontainers.** An afternoon, and it makes all four notes concrete
2. **Cause the N+1 deliberately**, see it in the SQL log, fix it with `Include`, record the query counts
3. **Reverse `UseAuthentication` and `UseAuthorization`** and watch every request become anonymous with no error. **Note 01's central claim, verified in a minute**
4. **Write one `WebApplicationFactory` test** — it's the feature most worth stealing conceptually even if you work in another stack

**What's missing:** authentication and authorization in depth (JWT, cookies, policies, Identity), SignalR and WebSockets, background services and hosted workers, Blazor, gRPC, output caching, and YARP.

## Related
- [[languages/07-csharp/README|the C# course]] — the language, per [[languages/README|the rule]]
- [[backend/frameworks/README|frameworks/]] · [[backend/README|the backend course]]
