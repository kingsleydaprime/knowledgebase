# The Standard Library and Ecosystem

> **[Intermediate]** · What .NET ships with, the packages everyone uses, and dependency injection as a first-class citizen.

## The BCL

.NET's Base Class Library is large and unusually coherent — one vendor, one design review, consistent naming.

| Need | Type |
|---|---|
| Files and paths | `File`, `Directory`, `Path`, `FileStream` |
| HTTP | **`HttpClient`** |
| JSON | **`System.Text.Json`** |
| Dates | `DateTime`, **`DateTimeOffset`**, `TimeSpan`, `DateOnly`/`TimeOnly` |
| Regex | `System.Text.RegularExpressions` |
| Crypto | `System.Security.Cryptography`, `RandomNumberGenerator` |
| Concurrency | `Task`, `Channel<T>`, `SemaphoreSlim`, `Interlocked`, `Concurrent*` |
| Logging abstraction | `Microsoft.Extensions.Logging` |
| Config | `Microsoft.Extensions.Configuration` |
| DI | `Microsoft.Extensions.DependencyInjection` |

**Three traps worth naming, because each has caused real production incidents:**

**`HttpClient` must be reused, not created per request.** A `using var client = new HttpClient()` in a loop exhausts sockets — disposed clients leave connections in `TIME_WAIT` → [[foundations/networking/06-tcp-connection-lifecycle|TCP]]. **Use `IHttpClientFactory`**, which also handles DNS rotation, which a long-lived static `HttpClient` does not.

**`DateTime` is ambiguous; `DateTimeOffset` isn't.** `DateTime` carries a `Kind` (Utc/Local/Unspecified) that is easy to lose across serialisation. **Store UTC, use `DateTimeOffset` for anything with a real instant**, and `DateOnly` for birthdays and calendar dates → [[languages/06-python/11-the-standard-library|the same rule in Python]].

**`Random` is not secure.** For tokens, passwords or anything an attacker benefits from predicting, use `RandomNumberGenerator` → [[cybersecurity/05-cryptography/README|cryptography]].

## Dependency injection, built in

**This is a genuine structural difference from most ecosystems.** DI isn't a framework you add; it's in the platform, and the whole ASP.NET Core stack is built on it.

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<IClock, SystemClock>();      // one, forever
builder.Services.AddScoped<IOrderService, OrderService>(); // one per request
builder.Services.AddTransient<IEmailSender, SmtpSender>(); // one per resolution
builder.Services.AddHttpClient<GitHubClient>();

var app = builder.Build();
```

**The three lifetimes, and the bug they cause:**

| | One instance per | Use for |
|---|---|---|
| **Singleton** | Process | Stateless services, caches, config |
| **Scoped** | Request | Anything holding per-request state — a `DbContext` |
| **Transient** | Resolution | Cheap, stateless, short-lived |

**The classic bug: injecting a Scoped service into a Singleton.** The scoped service is then captured for the lifetime of the singleton — so a `DbContext` meant to live for one request lives forever, accumulating tracked entities and becoming thread-unsafe. **.NET detects this at startup in development** (`ValidateScopes`), which is worth leaving on.

**Why this matters beyond convenience:** because DI is universal here, C# code is *structurally* testable — you substitute an interface rather than patching. It's the practical answer to the Singleton problem → [[concepts/interview/02-patterns-code-quality-and-review|why Singleton is global state]].

## The packages you'll actually meet

| | |
|---|---|
| **ASP.NET Core** | Web APIs, MVC, Blazor, SignalR — **in the SDK, not a package** |
| **Entity Framework Core** | The default ORM → [[databases/README\|databases]] |
| **Dapper** | Micro-ORM; you write the SQL. Faster, more control |
| **Serilog** | Structured logging → [[devops/10-observability/README\|observability]] |
| **xUnit / NUnit** | Testing → [[languages/07-csharp/12-testing-and-tooling\|note 12]] |
| **FluentValidation** | Validation rules as code |
| **MediatR** | In-process messaging; popular, and easy to overuse |
| **Polly** | Retries, circuit breakers, timeouts |
| **BenchmarkDotNet** | **The standard microbenchmark tool**, and genuinely excellent |
| **AutoMapper** | Object mapping. Widely used, widely regretted — it hides mistakes the compiler would catch |

**NuGet** is the package manager; `dotnet add package` is the interface.

## EF Core, and the trap

```csharp
var orders = await db.Orders
    .Include(o => o.Customer)                     // eager load — avoids N+1
    .Where(o => o.Total > 100)
    .AsNoTracking()                               // read-only: faster
    .ToListAsync(ct);
```

**The N+1 problem is identical to every other ORM's** → [[backend/frameworks/python/02-django/README|Django]]:

```csharp
foreach (var o in db.Orders.ToList())     // 1 query
    Console.WriteLine(o.Customer.Name);   // + 1 per order
```

**`Include` is the fix; lazy loading is the cause.** And `AsNoTracking` on read-only queries is free performance — the change tracker is doing work you're throwing away.

**The `IQueryable` boundary matters most here** — `.ToList()` in the wrong place moves the filter from SQL into C# and loads the whole table → [[languages/07-csharp/04-collections-and-linq|note 04]].

## What .NET does badly

**Windows-shaped assumptions** persist in older libraries and in a lot of documentation, even though the platform is genuinely cross-platform now.

**The ecosystem is narrower than the JVM's or Python's** for data science, ML and scientific computing — ML.NET exists and is not where the field is.

**Microsoft dependency.** Open source, .NET Foundation governed, and still overwhelmingly one company's roadmap. **Some people consider that a risk; it's a legitimate input to a trade study** → [[foundations/systems-engineering/05-trade-studies|trade studies]].

## Related
- [[languages/07-csharp/12-testing-and-tooling|testing and tooling]]
- [[backend/README|the backend course]] — the concepts ASP.NET Core implements
- [[databases/README|databases]] — what EF generates

*Source: [reference] — from the .NET documentation, Aug 2026.*
