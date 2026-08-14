# Layers — Controllers, Services, Repositories

**[Beginner→Intermediate]** — the structure almost every backend converges on, in every language. Spring calls them `@RestController`/`@Service`/`@Repository`; NestJS calls them controller/service/repository; Django calls them views/services/managers; Rails calls them controllers/services/models. **Same three jobs, different vocabulary** — which is exactly why this note lives in the course and not in a framework folder.

## The kid version first

A restaurant.

- The **waiter** takes your order. They don't cook, and they don't go to the fridge. They translate between "a human at a table" and "the kitchen."
- The **chef** decides what actually happens — the recipe, the rules, whether you can have the steak when there's one left and someone else just ordered it.
- The **pantry** stores and fetches ingredients. It doesn't know what's being cooked.

Swap the restaurant for a phone-order service and **you only replace the waiter**. The chef and the pantry are unchanged. That's the whole argument for layering: *the part that talks to the outside world is the part most likely to change, so isolate it.*

## The three layers

| Layer | Knows about | Must NOT know about |
|---|---|---|
| **Controller** (waiter) | HTTP: routes, status codes, headers, request/response shapes | business rules |
| **Service** (chef) | business rules, orchestration, transactions | HTTP, SQL |
| **Repository** (pantry) | the database: queries, mapping rows to objects | business rules |

**The rule, stated as a test you can apply:**

> **The controller is the API. The service is the product. The repository is the storage.**
>
> If a service returns a 404, or a controller contains an `if` about business rules, or a repository decides whether an order is valid — the layering has failed.

### Controller

```ts
// controller — HTTP only. No business logic, no SQL.
@Post('/orders')
async create(@Body() dto: CreateOrderDto, @CurrentUser() user: User) {
  const order = await this.orders.place(user.id, dto.items);  // delegate immediately
  return OrderResponse.from(order);                            // shape the response
}
```

Its entire job: parse and validate input, call one service method, map the result (or an error) to an HTTP response. **If a controller method is longer than about ten lines, business logic has leaked into it.**

### Service

```ts
// service — the actual product. Knows nothing about HTTP.
async place(userId: string, items: Item[]): Promise<Order> {
  if (items.length === 0) throw new EmptyOrderError();          // a domain error, not a 400
  return this.db.transaction(async (tx) => {
    const reserved = await this.inventory.reserve(tx, items);   // may throw OutOfStockError
    const order    = await this.orders.create(tx, userId, reserved);
    await this.events.publish(new OrderPlaced(order.id));
    return order;
  });
}
```

Two things to notice, because they're the ones people get wrong:

- **It throws domain errors, not HTTP errors.** `OutOfStockError`, not `ConflictException`. A layer above maps domain errors to status codes. The moment your service imports an HTTP type, it can only ever be called from HTTP — no CLI, no queue consumer, no scheduled job, and no test without a mock request.
- **Transaction boundaries live here**, not in the repository. The service knows which operations must succeed or fail together; the repository doesn't.

### Repository

```ts
// repository — data access only.
async findActiveByUser(tx, userId: string): Promise<Order[]> {
  return tx.order.findMany({ where: { userId, status: 'ACTIVE' } });
}
```

Its job is to be the only place that knows how data is stored. Swap Postgres for DynamoDB and only this layer changes — *in theory*. See the honest caveat below.

## Why bother — the arguments that actually hold

Most defences of layering are vague ("separation of concerns"). Here are the ones with teeth:

1. **Testability.** A service with no HTTP and no SQL dependency can be tested with plain function calls and a fake repository — fast, no framework, no database. That's the single biggest practical payoff, and it's why constructor injection matters ([[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|note 03]]).
2. **The same logic serves multiple entry points.** An HTTP request, a queue consumer, a cron job, and a CLI command can all call `orders.place()`. If that logic lives in a controller, three of those four have to duplicate it — and they will drift.
3. **Change isolation.** The API shape changes most often (clients demand it). Business rules change less. Storage changes least. Layering means a frequent change touches one layer.
4. **It's a shared vocabulary.** A new engineer who knows the pattern knows where to look. That's worth more than architectural purity.

## The honest caveats

Layering is a default, not a law, and the failure modes are real:

- **The anaemic pass-through.** `Controller → Service → Repository` where the service is a one-line forward to the repository. That's three files doing one file's work. If a service adds nothing, **it is ceremony, not architecture** — let the controller call the repository, and add the service when a real rule appears.
- **"Swappable database" is mostly a myth.** You will not swap Postgres for Mongo. The repository's real value is *testability* and *having one place where queries live*, not portability. Claiming portability sets an expectation the abstraction can't meet, and leads people to avoid useful database-specific features to preserve an option they'll never exercise.
- **Leaky abstraction via the ORM.** If your repository returns ORM entities with lazy relations, the service can trigger a database query just by touching a property — the boundary is decorative. This is precisely how [[backend/interview/01-production-debugging|N+1 queries]] appear. Return plain objects or explicitly-loaded entities.
- **It's not a dependency rule by itself.** Layering says *what* the parts are; it doesn't stop the service from depending on a concrete database class. That's what [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] adds.

## Where the layers grow

Real systems add a few more, and it's worth knowing the names:

- **DTOs** — the shape crossing the API boundary, separate from your domain objects, so an internal rename isn't a breaking API change. → [[backend/06-cross-cutting/README|validation]]
- **Mappers** — DTO ↔ domain ↔ persistence conversion.
- **Domain model** — where entities own their own invariants, rather than services manipulating dumb data bags. The difference between a "rich" and an "anaemic" domain model.
- **Middleware / filters / interceptors** — cross-cutting concerns before or after the controller. → [[backend/01-foundations/03-the-request-lifecycle|request lifecycle]]

## Key insight

Layering isn't about having three folders — it's about **which direction knowledge flows**. The outer layers may know about the inner ones; the inner ones must never know about the outer. A service that knows what HTTP is has been welded to one delivery mechanism, and every test, every reuse, and every future entry point pays for it forever. If you remember one thing: **the dependency arrow points inward, toward the business rules.**

## Related
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by layer vs by feature]] — how these map onto folders
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency Injection]] — how the layers get connected
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — layering with the dependency rule enforced
- [[concepts/03-design-patterns/README|Design Patterns]] — repository, adapter, and friends
