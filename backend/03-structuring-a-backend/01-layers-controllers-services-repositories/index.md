# Layers — Controllers, Services, Repositories

**[Beginner→Intermediate]** — the structure almost every backend converges on, in every language. Spring calls them `@RestController`/`@Service`/`@Repository`; NestJS calls them controller/service/repository; Django calls them views/services/managers; Rails calls them controllers/services/models. **Same three jobs, different vocabulary** — which is exactly why this note lives in the course and not in a framework folder.

## Before you start

You can already:

- Build an HTTP endpoint in any backend framework — Express, NestJS, Django, Flask, Spring.
- Explain cohesion and coupling → [[concepts/04-best-practices/01-clean-code/index|clean code]], and dependency inversion → [[concepts/04-best-practices/05-solid-principles/index|SOLID]].

After this lesson you will be able to:

1. Say what each of the three layers knows about and must not know about.
2. Move a business rule out of a controller into a service that throws domain errors, and map those errors to status codes in one place.
3. Test a business rule with plain function calls — no HTTP, no database.
4. Recognise the two failure modes: the anaemic pass-through and the leaky ORM.

**Study route.** Read the kid version and §1–3, run the worked example, then stop at *Check your understanding*. The caveats section is core, not optional.

## The kid version first

A restaurant.

- The **waiter** takes your order. They don't cook, and they don't go to the fridge. They translate between "a human at a table" and "the kitchen."
- The **chef** decides what actually happens — the recipe, the rules, whether you can have the steak when there's one left and someone else just ordered it.
- The **pantry** stores and fetches ingredients. It doesn't know what's being cooked.

Swap the restaurant for a phone-order service and **you only replace the waiter**. The chef and the pantry are unchanged. That's the whole argument for layering: *the part that talks to the outside world is the part most likely to change, so isolate it.*

**Where the analogy stops working.** A restaurant's waiter and chef are different people who can't accidentally merge. In code, nothing stops you writing the recipe inside the waiter — the layers only exist if you, or a lint rule, keep them apart.

## 1. Why this exists

An Express route handler validates the body, checks stock with a SQL query, inserts the order, sends a confirmation email, and returns `409` if anything is out of stock — forty lines, all in one function. Then the business wants orders from a WhatsApp bot (a queue consumer) and a nightly import (a script). Neither has a request or a response object. **The only way to reuse the logic is to copy it**, and from then on, three copies of the stock rule drift apart. Layering is the structure that prevents this.

## Terms used in this lesson

1. **Layer**: This is a group of code that does one kind of job and depends only on the layers inside it.
2. **Controller**: This is also known as a **handler**, a **view** (in Django) or a **route**. It is the layer that speaks HTTP — it turns a request into a function call and the result into a response.
3. **Service**: This is also known as the **use-case** or **application** layer. It holds the business rules and decides which operations must succeed or fail together.
4. **Repository**: This is also known as the **data-access layer**. It is the only code that knows how and where data is stored.
5. **Domain error**: This is an error named in the business's language, such as `OutOfStockError`, rather than in HTTP's, such as `409 Conflict`.
6. **Entry point**: This is any way work arrives in the system — an HTTP request, a queue message, a scheduled job, a command-line command.
7. **Transaction**: This is a group of database operations that either all happen or none happen.
8. **Anaemic**: This describes a layer or model that holds data or forwards calls but contains no logic of its own.

## 2. The three layers

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

## 3. Why bother — the arguments that actually hold

Most defences of layering are vague ("separation of concerns"). Here are the ones with teeth:

1. **Testability.** A service with no HTTP and no SQL dependency can be tested with plain function calls and a fake repository — fast, no framework, no database. That's the single biggest practical payoff, and it's why constructor injection matters ([[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|note 03]]).
2. **The same logic serves multiple entry points.** An HTTP request, a queue consumer, a cron job, and a CLI command can all call `orders.place()`. If that logic lives in a controller, three of those four have to duplicate it — and they will drift.
3. **Change isolation.** The API shape changes most often (clients demand it). Business rules change less. Storage changes least. Layering means a frequent change touches one layer.
4. **It's a shared vocabulary.** A new engineer who knows the pattern knows where to look. That's worth more than architectural purity.

## 4. Coupling and cohesion, seen through layers

Layers are cohesion and coupling made concrete. Each layer is **cohesive** — everything in the controller is about HTTP, everything in the repository is about storage. And the layers are **loosely coupled** — the service knows the repository only through the operations it calls, so a test can hand it a fake. When a service imports an HTTP type, coupling has gone up: the service can no longer be used without HTTP.

## 5. Worked example — three layers, no framework

Frameworks hide the layering behind decorators, so this version uses none. Read it as a template for what Express, Nest or Django do for you. **Before reading, predict:** which layer decides that "out of stock" is a `409`?

```ts
// orders.ts — three layers, no framework. Run the tests with: node --test
export type Item = { sku: string; quantity: number };
export type Order = { id: number; userId: string; items: Item[] };

// ---- domain errors: the service's vocabulary, not HTTP's ----
export class EmptyOrderError extends Error {}
export class OutOfStockError extends Error {
  sku: string;
  constructor(sku: string) {
    super(`out of stock: ${sku}`);
    this.sku = sku;
  }
}

// ---- repository: the only code that knows how data is stored ----
export interface OrdersRepository {
  stockOf(sku: string): number;
  reserve(sku: string, quantity: number): void;
  create(userId: string, items: Item[]): Order;
}

export function inMemoryRepository(stock: Record<string, number>): OrdersRepository {
  const orders: Order[] = [];
  return {
    stockOf: (sku) => stock[sku] ?? 0,
    reserve: (sku, quantity) => { stock[sku] -= quantity; },
    create: (userId, items) => {
      const order = { id: orders.length + 1, userId, items };
      orders.push(order);
      return order;
    },
  };
}

// ---- service: the business rules; knows nothing about HTTP ----
export function makeOrdersService(repo: OrdersRepository) {
  return {
    place(userId: string, items: Item[]): Order {
      if (items.length === 0) throw new EmptyOrderError("an order needs at least one item");
      for (const item of items) {
        if (repo.stockOf(item.sku) < item.quantity) throw new OutOfStockError(item.sku);
      }
      for (const item of items) repo.reserve(item.sku, item.quantity);
      return repo.create(userId, items);
    },
  };
}

// ---- controller: HTTP in, HTTP out; maps domain errors to status codes ----
type HttpRequest = { userId: string; body: { items?: Item[] } };
type HttpResponse = { status: number; body: unknown };

export function makeOrdersController(service: ReturnType<typeof makeOrdersService>) {
  return {
    create(req: HttpRequest): HttpResponse {
      try {
        const order = service.place(req.userId, req.body.items ?? []);
        return { status: 201, body: { id: order.id } };
      } catch (err) {
        if (err instanceof EmptyOrderError) return { status: 400, body: { error: err.message } };
        if (err instanceof OutOfStockError) return { status: 409, body: { error: err.message, sku: err.sku } };
        throw err; // unknown errors are bugs: let the framework turn them into a 500
      }
    },
  };
}
```

The answer to the prediction: **the controller**. The service only knows that stock ran out; deciding that this means `409` is an HTTP concern. A queue consumer calling the same `place()` would instead retry or dead-letter the message.

Notice also that `place` checks *every* item before reserving *any*. In a real database, both loops would run inside one transaction in the service, so a crash between them can't leave half an order reserved.

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { inMemoryRepository, makeOrdersController, makeOrdersService, OutOfStockError } from "./orders.ts";

test("service: the business rule is tested with plain calls, no HTTP", () => {
  const service = makeOrdersService(inMemoryRepository({ mug: 1 }));
  assert.throws(() => service.place("u1", [{ sku: "mug", quantity: 2 }]), OutOfStockError);
});

test("service: a successful order reserves stock", () => {
  const stock = { mug: 3 };
  const service = makeOrdersService(inMemoryRepository(stock));
  service.place("u1", [{ sku: "mug", quantity: 2 }]);
  assert.equal(stock.mug, 1);
});

test("controller: domain errors become status codes", () => {
  const controller = makeOrdersController(makeOrdersService(inMemoryRepository({ mug: 1 })));
  assert.equal(controller.create({ userId: "u1", body: { items: [] } }).status, 400);
  assert.deepEqual(controller.create({ userId: "u1", body: { items: [{ sku: "mug", quantity: 5 }] } }), {
    status: 409,
    body: { error: "out of stock: mug", sku: "mug" },
  });
  assert.deepEqual(controller.create({ userId: "u1", body: { items: [{ sku: "mug", quantity: 1 }] } }), {
    status: 201,
    body: { id: 1 },
  });
});
```

**Lab:** these files are in [`backend/03-structuring-a-backend/01-layers-controllers-services-repositories/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/01-layers-controllers-services-repositories/labs/typescript). From the vault root, `python3 labs/run.py layers-controllers-services-repositories/typescript` runs them and checks this page still shows the same code.

**Run it.** Save both files in one folder and, from that folder, run `node --test`. Node 23.6 or later runs TypeScript files directly by stripping the types; this was checked with Node 26. Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

The first two tests never build a request: that's the testability argument from §3, demonstrated.

## 6. The honest caveats

Layering is a default, not a law, and the failure modes are real:

- **The anaemic pass-through.** `Controller → Service → Repository` where the service is a one-line forward to the repository. That's three files doing one file's work. If a service adds nothing, **it is ceremony, not architecture** — let the controller call the repository, and add the service when a real rule appears.
- **"Swappable database" is mostly a myth.** You will not swap Postgres for Mongo. The repository's real value is *testability* and *having one place where queries live*, not portability. Claiming portability sets an expectation the abstraction can't meet, and leads people to avoid useful database-specific features to preserve an option they'll never exercise.
- **Leaky abstraction via the ORM.** If your repository returns ORM entities with lazy relations, the service can trigger a database query just by touching a property — the boundary is decorative. This is precisely how [[backend/interview/01-production-debugging|N+1 queries]] appear. Return plain objects or explicitly-loaded entities.
- **It's not a dependency rule by itself.** Layering says *what* the parts are; it doesn't stop the service from depending on a concrete database class. That's what [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|hexagonal architecture]] adds.

## 7. Where the layers grow

Real systems add a few more, and it's worth knowing the names:

- **DTOs** — the shape crossing the API boundary, separate from your domain objects, so an internal rename isn't a breaking API change. → [[backend/06-cross-cutting/index|validation]]
- **Mappers** — DTO ↔ domain ↔ persistence conversion.
- **Domain model** — where entities own their own invariants, rather than services manipulating dumb data bags. The difference between a "rich" and an "anaemic" domain model.
- **Middleware / filters / interceptors** — cross-cutting concerns before or after the controller. → [[backend/01-foundations/03-the-request-lifecycle|request lifecycle]]

## Check your understanding

1. In one sentence each: what does the controller, the service and the repository know about?
2. Why should a service throw `OutOfStockError` rather than a `ConflictException`?
3. Where do transaction boundaries belong, and why not in the repository?
4. Your service method is `return this.repo.findById(id)`. Is that a problem? What would you do?
5. A repository returns ORM entities with lazy relations. What goes wrong, and where does it show up?

<details>
<summary>Answers — after your attempt</summary>

1. Controller: HTTP — routes, status codes, request and response shapes. Service: business rules, orchestration, transactions. Repository: the database — queries and mapping rows to objects.
2. An HTTP exception ties the service to HTTP, so a queue consumer, a script or a test has to deal with HTTP concepts to call it. A domain error lets each entry point decide what it means.
3. In the service, because only the service knows which operations must succeed or fail together. The repository sees one query at a time.
4. It's an anaemic pass-through. If there's no rule to add, let the controller call the repository directly and introduce the service when a real rule appears — or keep it for consistency if your team's convention demands it, knowing it's ceremony.
5. The service triggers a query just by reading a property, so the storage boundary is decorative. It shows up as N+1 queries — one query per item in a loop.

</details>

## Practice — independent task

**Add a second entry point to the worked example.** Without changing `makeOrdersService`:

1. Write a `handleQueueMessage(message)` function that calls `place()` and returns `"ack"` on success, `"retry"` on `OutOfStockError`, and `"dead-letter"` on `EmptyOrderError`.
2. Write tests for all three outcomes.
3. Add a rule — "an order may not contain more than 10 of one item" — and decide which layer it belongs in. Test it once, at that layer, and show both entry points enforce it.

**Done when:** the service file is unchanged by steps 1–2, the new rule is written exactly once, and both the controller and the queue handler reject an 11-item order through their own error mapping.

## Before moving on

You can say what each layer may and may not know, place a new rule in the right layer, and test business logic without HTTP.

**Recap.** Controller, service, repository: HTTP, rules, storage. Services throw domain errors; one place maps them to status codes. Transactions live in the service. Skip the service when it adds nothing, and don't promise a swappable database.

**Next.** [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by layer vs by feature]] — how these three files map onto folders, in five frameworks.

## Key insight

Layering isn't about having three folders — it's about **which direction knowledge flows**. The outer layers may know about the inner ones; the inner ones must never know about the outer. A service that knows what HTTP is has been welded to one delivery mechanism, and every test, every reuse, and every future entry point pays for it forever. If you remember one thing: **the dependency arrow points inward, toward the business rules.**

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/in-other-languages|Layers in Other Languages]] — how each language represents and maps domain errors
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|Organising by layer vs by feature]] — how these map onto folders
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection]] — how the layers get connected
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|Hexagonal & Clean Architecture]] — layering with the dependency rule enforced
- [[concepts/03-design-patterns/index|Design Patterns]] — repository, adapter, and friends
