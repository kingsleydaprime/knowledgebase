# ASP.NET Core and the Pipeline

> **[Intermediate]** · The hosting model, the middleware pipeline, and the DI container that everything plugs into.

**ASP.NET Core is not a package you install — it's in the SDK.** `dotnet new webapi` gives you a working server with routing, DI, configuration, logging and health checks already wired.

## The whole program

```csharp
var builder = WebApplication.CreateBuilder(args);

// 1. REGISTER services (the DI container)
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddDbContext<AppDb>(o => o.UseNpgsql(builder.Configuration.GetConnectionString("Db")));
builder.Services.AddProblemDetails();

var app = builder.Build();

// 2. COMPOSE the middleware pipeline — ORDER MATTERS
app.UseExceptionHandler();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapGet("/orders/{id:int}", async (int id, IOrderService svc) => await svc.GetAsync(id));

app.Run();
```

**Two phases, and conflating them is the commonest beginner error.** Before `Build()` you register *what exists*. After it you compose *what happens per request*. You cannot register services after `Build()`.

## The middleware pipeline

**The single most important concept in the framework.** A request passes down through middleware, hits an endpoint, and the response passes back up.

```
Request  → Exception handler → HTTPS → Auth → Authorization → Endpoint
Response ←                                                   ←
```

Each middleware is a delegate taking `HttpContext` and a `next`:

```csharp
app.Use(async (context, next) =>
{
    var sw = Stopwatch.StartNew();
    await next(context);                    // call the rest of the pipeline
    logger.LogInformation("{Path} took {Ms}ms", context.Request.Path, sw.ElapsedMilliseconds);
});
```

**Three rules that cause real bugs:**

**Order is behaviour.** `UseAuthorization()` before `UseAuthentication()` means nobody is authenticated when authorisation runs — every request is anonymous. **The framework won't warn you.**

**Not calling `next` short-circuits.** That's how a caching or auth middleware returns early — deliberate, and accidental omission means requests silently never reach your endpoint.

**Middleware is a singleton.** It's constructed once. **Injecting a scoped service into its constructor captures it forever** → [[languages/07-csharp/11-the-standard-library-and-ecosystem|note 11]]. Inject scoped services into `InvokeAsync` instead.

**This is the onion/decorator pattern**, and it's the same shape as Express middleware, Django middleware and `tower` layers → [[backend/frameworks/README|frameworks]].

## Dependency injection

**Built into the platform**, not a library you choose → [[languages/07-csharp/11-the-standard-library-and-ecosystem|note 11]].

```csharp
builder.Services.AddSingleton<IClock, SystemClock>();       // one, forever
builder.Services.AddScoped<IOrderService, OrderService>();  // one per REQUEST
builder.Services.AddTransient<IEmailSender, SmtpSender>();  // one per resolution
builder.Services.AddHttpClient<GitHubClient>();             // pooled HttpClient
```

**Scoped means per-request**, which is why `DbContext` is scoped — it accumulates tracked entities and isn't thread-safe.

**`AddHttpClient` matters more than it looks.** It gives you `IHttpClientFactory`, which pools handlers and rotates DNS. A `new HttpClient()` per request exhausts sockets; a long-lived static one never notices a DNS change → [[foundations/networking/06-tcp-connection-lifecycle|TCP]].

**Leave scope validation on.** In development the container detects a scoped service captured by a singleton and throws at startup — catching a bug that would otherwise be a slow leak.

## Configuration

Layered, with later sources overriding earlier:

```
appsettings.json → appsettings.{Environment}.json → user secrets → environment variables → CLI args
```

```csharp
builder.Services.Configure<StripeOptions>(builder.Configuration.GetSection("Stripe"));
// then inject IOptions<StripeOptions>
```

**The options pattern binds config to a typed class**, so a typo is a startup failure rather than a null at 3 a.m. `IOptionsSnapshot<T>` re-reads per request; `IOptionsMonitor<T>` pushes changes.

**Never put secrets in `appsettings.json`** — it's committed. Use user secrets locally and environment variables or a vault in production → [[devops/09-secret-management/README|secret management]].

## Hosting

**Kestrel** is the built-in cross-platform server, and it is genuinely fast — routinely near the top of TechEmpower benchmarks.

**Reverse proxy or not?** Kestrel can face the internet directly and is designed to. Putting nginx or YARP in front buys you TLS termination, static file serving, rate limiting and shared-port routing → [[devops/08-networking-and-web/README|networking and web]]. **Behind a proxy, configure `ForwardedHeaders`** or every request appears to come from the proxy's IP — which breaks logging, rate limiting and geo rules.

**The concurrency model is async all the way down** — a thread-pool thread per *active* request, released during I/O waits, rather than one thread pinned per connection → [[languages/07-csharp/07-async-await-and-tasks|note 07]] · [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]].

## Related
- [[backend/frameworks/csharp/02-minimal-apis-and-mvc|minimal APIs and MVC]] — the two endpoint styles
- [[languages/07-csharp/README|the C# course]] — the language
- [[backend/03-structuring-a-backend/README|structuring a backend]] — the layering this doesn't give you

*Source: [reference] — from the ASP.NET Core documentation, Aug 2026.*
