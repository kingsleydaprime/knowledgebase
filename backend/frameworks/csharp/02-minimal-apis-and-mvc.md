# Minimal APIs and MVC

> **[Intermediate]** · Two endpoint styles in one framework — what differs, what doesn't, and which to pick.

**Both are ASP.NET Core.** Same pipeline, same DI, same routing engine. They differ in *how you declare an endpoint*, not in what happens underneath.

## Minimal APIs

```csharp
app.MapGet("/orders/{id:int}", async (int id, IOrderService svc) =>
        await svc.GetAsync(id) is { } order
            ? Results.Ok(order)
            : Results.NotFound())
   .WithName("GetOrder")
   .Produces<Order>()
   .RequireAuthorization();

app.MapPost("/orders", async (CreateOrder cmd, IOrderService svc) =>
{
    var created = await svc.CreateAsync(cmd);
    return Results.Created($"/orders/{created.Id}", created);
});
```

**Parameters are resolved by convention:** route values by name, complex types from the JSON body, registered services from DI, and `[FromQuery]`/`[FromHeader]` when you need to be explicit.

**Route constraints (`{id:int}`) are matching rules, not validation** — `/orders/abc` produces a 404, not a 400, because the route simply didn't match.

## Controllers (MVC)

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController(IOrderService svc) : ControllerBase
{
    [HttpGet("{id:int}")]
    [ProducesResponseType<Order>(StatusCodes.Status200OK)]
    public async Task<ActionResult<Order>> Get(int id)
        => await svc.GetAsync(id) is { } order ? Ok(order) : NotFound();
}
```

**`[ApiController]` is doing real work** — automatic model-state validation returning a 400 with `ProblemDetails`, inference of binding sources, and attribute routing requirements. Without it you'd hand-write `if (!ModelState.IsValid)` in every action.

## Which to use

| | Minimal APIs | Controllers |
|---|---|---|
| Ceremony | **Low** | Higher |
| Discoverability | Endpoints scattered unless you organise | **Grouped by class** |
| Filters / conventions | Endpoint filters | **Mature, richer** |
| Native AOT | **Supported** | Limited |
| Views / Razor | No | **Yes** |
| Large teams | Needs discipline | **Structure comes free** |

**The pragmatic answer:** Minimal APIs for new services, small APIs and anything targeting AOT. Controllers for large APIs where the class structure is genuine organisation, and for anything server-rendered.

**Minimal APIs are not "for small apps".** They scale fine — but *you* must impose the structure. `MapGroup` is the tool:

```csharp
var orders = app.MapGroup("/orders").RequireAuthorization().WithTags("Orders");
orders.MapGet("/{id:int}", GetOrder);
orders.MapPost("/", CreateOrder);
```

**Put handlers in separate static classes and register them per feature**, or you get a 900-line `Program.cs` — which is the real failure mode → [[backend/03-structuring-a-backend/README|structuring a backend]].

## Validation

**Neither style validates a request body by itself** beyond type binding.

- **Controllers + `[ApiController]`** — DataAnnotations (`[Required]`, `[Range]`) are checked automatically
- **Minimal APIs** — nothing built in until recently. **FluentValidation** is the common answer

```csharp
public class CreateOrderValidator : AbstractValidator<CreateOrder>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.Quantity).GreaterThan(0).LessThanOrEqualTo(100);
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
    }
}
```

**Validate at the boundary** — the same argument as Pydantic in [[backend/frameworks/python/01-fastapi/README|FastAPI]] and zod in TypeScript. **Type annotations describe intent; only a validator enforces it at runtime** → [[languages/07-csharp/02-the-type-system|note 02]].

## Errors → status codes

```csharp
builder.Services.AddProblemDetails();
app.UseExceptionHandler();
```

**`ProblemDetails` (RFC 9457) is the standardised error body**, and ASP.NET Core produces it by default. Use it rather than inventing a shape → [[backend/02-api-design/README|API design]].

**Map domain exceptions to status codes in one place** — an `IExceptionHandler` or an exception-handling middleware — rather than try/catch in every endpoint. **Never let a raw stack trace reach a client in production** → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

## OpenAPI

.NET 9+ ships built-in OpenAPI document generation (`AddOpenApi`/`MapOpenApi`); **Swashbuckle** and **NSwag** remain common and offer more.

**The honest comparison with FastAPI:** there, the schema is *derived from the same Pydantic model that validates* — so drift between docs and behaviour is structurally impossible. **In ASP.NET Core the schema is generated from types and attributes, and can drift** from a separately-defined validator. Worth knowing rather than assuming parity.

## The concept translation

| Course concept | ASP.NET Core |
|---|---|
| **Controller** | `MapGet` handler, or a `ControllerBase` action |
| **Service** | Your class, registered in DI |
| **Repository** | Your class, or `DbContext` directly |
| **Middleware** | `app.Use…` / endpoint filters |
| **DI** | **Built in** |
| **Validation** | DataAnnotations or FluentValidation |
| **Errors → status** | `ProblemDetails` + `IExceptionHandler` |

## Related
- [[backend/frameworks/csharp/01-aspnet-core-and-the-pipeline|the pipeline]]
- [[backend/frameworks/csharp/03-data-access|data access]]
- [[backend/02-api-design/README|API design]] — what you're building

*Source: [reference] — from the ASP.NET Core documentation, Aug 2026.*
