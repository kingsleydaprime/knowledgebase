# Testing and Production

> **[Intermediate]** · `WebApplicationFactory`, Testcontainers, and getting an ASP.NET Core service into production sensibly.

## Integration testing is unusually good here

**`WebApplicationFactory<T>` spins up your entire application in-process** — real pipeline, real DI, real routing — and gives you an `HttpClient` that talks to it without a network.

```csharp
public class OrdersApiTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task Get_ReturnsNotFound_ForMissingOrder()
    {
        var client = factory.CreateClient();
        var response = await client.GetAsync("/orders/999999");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
```

**This is one of the best testing stories in any web ecosystem.** You test the actual middleware order, actual model binding, actual serialisation and actual auth — the things unit tests structurally cannot cover → [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|note 01]].

**Override dependencies for a test:**

```csharp
factory.WithWebHostBuilder(b => b.ConfigureServices(services =>
{
    services.RemoveAll<IEmailSender>();
    services.AddSingleton<IEmailSender, FakeEmailSender>();
}));
```

## Test against a real database

**Testcontainers** starts a real Postgres in Docker for the test run:

```csharp
var db = new PostgreSqlBuilder().WithImage("postgres:16").Build();
await db.StartAsync();
// point the app at db.GetConnectionString()
```

**This replaced the EF In-Memory provider**, which was a persistent source of false confidence — it doesn't enforce constraints, doesn't do real SQL translation, and passes tests that fail against an actual database. **The EF team now recommends against it for testing.**

**The general rule from [[foundations/systems-engineering/06-verification-and-validation|V&V]]: test in an environment that resembles the one that matters.** A fake database is a different environment.

## Observability

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(t => t.AddAspNetCoreInstrumentation().AddEntityFrameworkCoreInstrumentation())
    .WithMetrics(m => m.AddAspNetCoreInstrumentation().AddRuntimeInstrumentation());
```

**OpenTelemetry is the default answer**, and .NET's built-in instrumentation is genuinely good — `Activity` (spans) and `Meter` are in the BCL, not a library → [[devops/10-observability/README|observability]].

**Structured logging, not string interpolation:**

```csharp
logger.LogInformation("Order {OrderId} created for {CustomerId}", id, customerId);   // ✓
logger.LogInformation($"Order {id} created");                                        // ✗
```

The first preserves `OrderId` as a **queryable field**. The second produces a string you can only grep, and it formats even when the level is disabled → [[languages/06-python/11-the-standard-library|the same rule in Python]].

**Health checks** are built in:

```csharp
builder.Services.AddHealthChecks().AddDbContextCheck<AppDb>();
app.MapHealthChecks("/health/ready");
app.MapHealthChecks("/health/live", new() { Predicate = _ => false });
```

**Liveness and readiness are different questions.** Liveness: *is the process alive?* — restart if not. Readiness: *can it serve traffic?* — remove from the load balancer if not. **Wiring a database check into liveness means a brief database blip restarts every pod**, which turns a small problem into an outage → [[devops/05-orchestration/README|orchestration]].

## Deployment

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY *.csproj .
RUN dotnet restore                    # cached layer — restore before copying source
COPY . .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app .
USER $APP_UID                         # don't run as root
ENTRYPOINT ["dotnet", "MyApi.dll"]
```

**Restore before copying the full source** so dependency restore is cached → [[devops/02-docker/04-multi-stage-builds|multi-stage builds]].

**Runtime image, not SDK** — the SDK image is several times larger and ships a compiler into production.

**Native AOT** is worth considering for serverless and short-lived workloads — millisecond startup, small footprint — at the cost of reflection-based libraries → [[languages/07-csharp/13-performance-and-the-runtime|note 13]]. **For a long-running API, stay with JIT**; the startup cost amortises to nothing and you keep the runtime optimisations.

## Configuration and secrets in production

**Environment variables override `appsettings.json`**, and the double-underscore convention maps to nesting:

```
ConnectionStrings__Db=Host=...;Password=...
```

**Secrets belong in a secret store**, injected as env vars or fetched at startup — never in the image, never in the repo → [[devops/09-secret-management/README|secret management]].

**`ASPNETCORE_ENVIRONMENT`** drives which `appsettings.{env}.json` loads and whether the developer exception page is on. **Getting this wrong in production leaks stack traces to users.**

## The production checklist

- **HTTPS** and HSTS
- **`ForwardedHeaders`** if behind a proxy, or every client IP is the proxy's
- **Rate limiting** — built in since .NET 7 (`AddRateLimiter`)
- **CORS**, configured deliberately rather than `AllowAnyOrigin`
- **`ProblemDetails`** for errors; **no stack traces to clients**
- **Health checks** split liveness/readiness
- **Graceful shutdown** — ASP.NET Core handles SIGTERM; make sure background work honours the cancellation token
- **`dotnet list package --vulnerable`** in CI → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]]

## Related
- [[backend/frameworks/csharp/03-data-access|data access]]
- [[languages/07-csharp/12-testing-and-tooling|C#: testing and tooling]] — the unit-test layer
- [[devops/10-observability/README|observability]] · [[devops/06-ci-cd/README|CI/CD]]

*Source: [reference] — from the ASP.NET Core documentation, Aug 2026.*
