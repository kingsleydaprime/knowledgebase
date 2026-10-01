# Hexagonal & Clean Architecture

**[Intermediate→Advanced]** — layering with the dependency direction actually enforced. Also known as ports and adapters, onion architecture, and clean architecture — **largely the same idea under four names**, which is itself worth knowing so you don't think they're four things to learn.

## Before you start

You can already:

- Separate a controller, a service and a repository, and explain why services throw domain errors → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]].
- Explain dependency inversion — "depend on what you need, not on a vendor" → [[concepts/04-best-practices/05-solid-principles|SOLID]].

After this lesson you will be able to:

1. Draw the hexagon and say which way every dependency arrow points.
2. Define a port in the domain, implement it in an adapter, and explain why *where the interface lives* is the whole trick.
3. Test a use case with in-memory adapters and prove the domain imports nothing from infrastructure.
4. Decide whether a given service deserves this structure, or plain layering.

**Study route.** Kid version, §1–3, then the worked example. *The honest cost* (§5) is core reading — most teams that adopt this should adopt less of it.

## The kid version

A wall socket doesn't care what you plug into it — a lamp, a phone charger, a kettle. The socket was designed first, and every appliance is built to fit **it**. The house doesn't get rewired when you buy a new kettle. **Hexagonal architecture makes your business rules the wall socket**: they say what shape of plug they accept, and databases, payment providers and web frameworks are the appliances built to fit.

**Where the analogy stops working.** Wall sockets are standardised by law, so they almost never change. Your ports *will* change as you learn what the business needs — and every adapter then has to change with them. Ports are cheaper than rewiring, not free.

## 1. Why this exists

Plain [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layering]] says: controller → service → repository. But look at what that means in code — the service *imports* the repository, and the repository imports the Postgres driver. So your business logic transitively depends on Postgres. The layers are stacked, but the dependency still points **outward**, toward infrastructure.

Hexagonal architecture asks: what if the arrow pointed the other way?

**The business logic defines the socket. Infrastructure builds the plug.**

Your domain declares *"I need something that can save an order"* — a **port**, an interface it owns. Postgres, Mongo, or an in-memory map each provide an **adapter** that fits. The domain doesn't know which is plugged in and can't find out.

```
        HTTP  CLI  Queue                    ← driving adapters (they call you)
           ↓    ↓    ↓
        ┌──────────────────┐
        │   APPLICATION    │               ← use cases
        │  ┌────────────┐  │
        │  │   DOMAIN   │  │               ← entities + rules. Depends on NOTHING.
        │  └────────────┘  │
        └──────────────────┘
           ↑    ↑    ↑
      Postgres  S3  Stripe                 ← driven adapters (you call them)
```

**Every arrow points inward.** That's the entire idea; the rest is bookkeeping.

## Terms used in this lesson

1. **Domain**: This is the code that holds the business's entities and rules — what an order is, when it's valid. It knows nothing about databases or HTTP.
2. **Use case**: This is also known as an **application service**. It is one thing a user can do ("place an order"), written as a function or class that coordinates domain rules and ports.
3. **Port**: This is an interface the domain or application *owns* that describes something it needs, such as "save an order" or "charge a customer".
4. **Adapter**: This is code that implements a port using a real technology — Postgres, Stripe, an in-memory array. Adapters depend on the domain; the domain never depends on them.
5. **Driving adapter**: This is also known as a **primary adapter**. It *calls into* the application — an HTTP controller, a CLI command, a queue consumer.
6. **Driven adapter**: This is also known as a **secondary adapter**. It *is called by* the application — a database repository, a payment client, an email sender.
7. **Dependency rule**: This is the rule that source-code imports point only inward, toward the domain.
8. **Composition root**: This is the one place, at startup, where real adapters are created and handed to the use cases.

## 2. The dependency inversion, concretely

```ts
// ── domain layer: owns the interface, imports nothing ──────────────
export interface OrderRepository {          // the PORT — defined by the domain
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}

export class PlaceOrder {                   // a use case
  constructor(private readonly orders: OrderRepository) {}   // depends on the port
  async execute(cmd: PlaceOrderCommand): Promise<Order> { /* pure business rules */ }
}

// ── infrastructure layer: implements it, imports the domain ────────
import { OrderRepository } from '../domain/order-repository';   // ← arrow points INWARD

export class PostgresOrderRepository implements OrderRepository {
  async save(order: Order) { /* SQL */ }
  async findById(id: OrderId) { /* SQL */ }
}
```

The detail that makes it work: **the interface lives in the domain folder, not the infrastructure folder.** If `OrderRepository` sits next to `PostgresOrderRepository`, the domain has to import from infrastructure and you've achieved nothing but extra files. *Who owns the interface* is the whole game.

## 3. What you actually get

1. **The domain is testable with zero infrastructure.** No database, no HTTP, no containers, no framework. Tests run in milliseconds and never flake. This is the real prize.
2. **Multiple entry points for free.** HTTP, a CLI, a queue consumer, and a scheduled job are four driving adapters over one use case. No duplication.
3. **Infrastructure decisions become deferrable and reversible.** Start with an in-memory repository, add Postgres when you know the access patterns. Swapping Stripe for Paystack is one adapter.
4. **The business rules are findable.** In a typical CRUD codebase, "what are the rules for placing an order?" is answered by reading a controller, a service, three ORM hooks and a database constraint. Here, there's one file.

## 4. Worked example — a checkout with a payment port

**Before reading, predict:** in the folder tree below, which files may import from `adapters/`?

```
hex/
├── place-order.test.ts
└── src/
    ├── domain/order.ts              entity, rules, and the two ports
    ├── application/place-order.ts   the use case
    └── adapters/in-memory.ts        driven adapters (a real app adds postgres.ts, paystack.ts)
```

```ts
// src/domain/order.ts — entities, rules and ports. Imports nothing outside domain/.
export type Order = { id: string; customerId: string; totalKobo: number; status: "pending" | "paid" };

export class InvalidTotalError extends Error {}
export class PaymentDeclinedError extends Error {}

export function newOrder(id: string, customerId: string, totalKobo: number): Order {
  if (!Number.isInteger(totalKobo) || totalKobo <= 0) throw new InvalidTotalError(`bad total: ${totalKobo}`);
  return { id, customerId, totalKobo, status: "pending" };
}

// Ports: the domain says what it needs, in its own words.
export interface OrderRepository {
  save(order: Order): Promise<void>;
}
export interface PaymentGateway {
  charge(customerId: string, amountKobo: number): Promise<{ ok: true; reference: string } | { ok: false }>;
}
```

```ts
// src/application/place-order.ts — one use case. Depends only on the domain.
import { newOrder, PaymentDeclinedError, type Order, type OrderRepository, type PaymentGateway } from "../domain/order.ts";

export function makePlaceOrder(deps: { orders: OrderRepository; payments: PaymentGateway; nextId: () => string }) {
  return async function placeOrder(customerId: string, totalKobo: number): Promise<Order> {
    const order = newOrder(deps.nextId(), customerId, totalKobo);
    const result = await deps.payments.charge(customerId, order.totalKobo);
    if (!result.ok) throw new PaymentDeclinedError(order.id);
    const paid: Order = { ...order, status: "paid" };
    await deps.orders.save(paid);
    return paid;
  };
}
```

```ts
// src/adapters/in-memory.ts — driven adapters. They import the domain; never the reverse.
import type { Order, OrderRepository, PaymentGateway } from "../domain/order.ts";

export class InMemoryOrders implements OrderRepository {
  saved: Order[] = [];
  async save(order: Order) {
    this.saved.push(order);
  }
}

export class FakePayments implements PaymentGateway {
  declineAbove: number;
  constructor(declineAbove: number) {
    this.declineAbove = declineAbove;
  }
  async charge(_customerId: string, amountKobo: number) {
    return amountKobo > this.declineAbove ? { ok: false as const } : { ok: true as const, reference: "ref_1" };
  }
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { makePlaceOrder } from "./src/application/place-order.ts";
import { FakePayments, InMemoryOrders } from "./src/adapters/in-memory.ts";
import { InvalidTotalError, PaymentDeclinedError } from "./src/domain/order.ts";

function setup(declineAbove = 1_000_000) {
  const orders = new InMemoryOrders();
  const placeOrder = makePlaceOrder({ orders, payments: new FakePayments(declineAbove), nextId: () => "o1" });
  return { orders, placeOrder };
}

test("a paid order is saved with status paid", async () => {
  const { orders, placeOrder } = setup();
  await placeOrder("c1", 250_000);
  assert.deepEqual(orders.saved, [{ id: "o1", customerId: "c1", totalKobo: 250_000, status: "paid" }]);
});

test("a declined payment saves nothing", async () => {
  const { orders, placeOrder } = setup(100);
  await assert.rejects(placeOrder("c1", 250_000), PaymentDeclinedError);
  assert.equal(orders.saved.length, 0);
});

test("the domain rejects a fractional total before any payment is attempted", async () => {
  const { orders, placeOrder } = setup();
  await assert.rejects(placeOrder("c1", 99.5), InvalidTotalError);
  assert.equal(orders.saved.length, 0);
});
```

**Lab:** these files are in `labs/hexagonal-architecture/`. From the vault root, `python3 labs/run.py hexagonal-architecture` runs them and checks this page still shows the same code.

**Run it.** From the `hex/` folder: `node --test`. Node 23.6 or later runs these `.ts` files directly; checked with Node 26. Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

The answer to the prediction: **none of the `src/` code imports `adapters/`** — only the test, which plays the role of the composition root. You can check the dependency rule from the `hex/` folder with:

```bash
grep -rn 'from "\.\./adapters' src/domain src/application || echo "no violations"
```

which prints `no violations`. In a real project, make it a lint failure with ESLint's `import/no-restricted-paths` (zone: target `./src/domain`, from `./src/adapters`), as shown in [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|layer vs feature]].

**Why `FakePayments` has a plain field instead of `constructor(private readonly …)`.** Node's built-in TypeScript support only strips types; parameter properties generate code, so it rejects them. The fragment in §2 uses them because a normal `tsc` build supports them.

**What a real Paystack adapter changes.** One new file implementing `PaymentGateway` by calling the provider's API, and one line in the composition root. `place-order.ts` and `order.ts` don't change — and their tests keep running in milliseconds without a network.

## 5. The honest cost

This is where most write-ups stop, and they shouldn't. Hexagonal architecture is **genuinely expensive** and frequently misapplied:

- **More files, more indirection.** A simple create-read-update-delete resource becomes an entity, a port, an adapter, a use case, a DTO, and two mappers. For a CRUD screen, that's a poor trade — you've paid an abstraction tax for flexibility you'll never spend.
- **Mapping fatigue.** Domain objects ≠ ORM entities ≠ DTOs means writing and maintaining mapping code between all three. Real, ongoing, boring cost.
- **You give up your ORM's conveniences.** Lazy loading, change tracking, and query builders all want to reach across the boundary you just drew.
- **Team cost.** Everyone has to understand it or they'll route around it, and a half-applied hexagonal architecture is worse than plain layering — you get the file count without the guarantee.

**Where it's worth it:** complex, long-lived domains with real business rules — payments, logistics, insurance, scheduling, anything with invariants that matter and a long life ahead of it.

**Where it isn't:** CRUD services, thin API gateways, most internal tools, and anything where the "business logic" is genuinely `INSERT` and `SELECT`. Use [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|plain layering]] there and don't apologise for it.

## 6. The four names, briefly

- **Hexagonal / Ports & Adapters** (Cockburn, 2005) — the original. The hexagon shape means nothing; it's just "many sides, many adapters."
- **Onion Architecture** (Palermo, 2008) — same rule, drawn as concentric rings.
- **Clean Architecture** (Martin, 2012) — same rule plus named rings (entities, use cases, interface adapters, frameworks) and the explicit **Dependency Rule**: *source code dependencies point only inward.*
- **DDD's layered architecture** — compatible, and adds the vocabulary for what goes *inside* the domain: aggregates, value objects, domain events, bounded contexts.

Treat them as one idea with four vocabularies. Knowing that saves you from reading four books to learn one rule.

## 7. A pragmatic middle ground

Most teams should not go all-in. What you can adopt cheaply and get most of the value:

- **Keep HTTP out of services.** Domain errors, not status codes. (Free, huge payoff.)
- **Define the interface where it's consumed**, not where it's implemented — even without a full domain layer.
- **Push one thing behind a port: the one most likely to change.** Usually a third-party API (payments, email, storage), not the database.
- **Keep the pure rules pure.** Extract the genuinely tricky logic — pricing, eligibility, state transitions — into functions with no I/O. They become trivially testable and you've captured 80% of the benefit for 10% of the cost.

## Check your understanding

1. In plain layering, why does the business logic still depend on Postgres, even though it never imports the Postgres driver directly?
2. Where must the `OrderRepository` interface live for the dependency to be inverted? What happens if it lives next to the Postgres implementation?
3. Is an HTTP controller a driving or a driven adapter? Is a Stripe client?
4. Give one kind of service where hexagonal architecture is worth its cost and one where it isn't.
5. Which item from the pragmatic middle ground would you adopt first in a CRUD codebase, and why?

<details>
<summary>Answers — after your attempt</summary>

1. Transitively: the service imports the repository, and the repository imports the driver. The arrow points outward through the chain.
2. In the domain (or application) layer — the side that *uses* it. If it lives with the implementation, the domain has to import from infrastructure, and nothing has been inverted.
3. A controller is driving — it calls into the application. A Stripe client is driven — the application calls it.
4. Worth it: payments, logistics, insurance, scheduling — long-lived domains with real invariants. Not worth it: CRUD admin tools, thin gateways, services whose logic is `INSERT` and `SELECT`.
5. Usually "keep HTTP out of services" — it's free and gives most of the testability. Second: put the one third-party API most likely to change behind a port.

</details>

## Practice — independent task

**Add a driving adapter and a second driven adapter to the worked example.**

1. Write an `http.ts` driving adapter: a function taking `{ customerId, totalKobo }` and returning `{ status, body }` — `201` on success, `402` on `PaymentDeclinedError`, `400` on `InvalidTotalError`.
2. Write a `RecordingPayments` adapter that never declines and records every charge, and use it in a test that checks a 250,000 kobo order charges exactly once.
3. Add the ESLint zone (or a test using `grep`) that fails if anything in `src/domain` imports from `src/adapters` or `src/application`.

**Done when:** `place-order.ts` and `order.ts` are unchanged, all tests pass, and deliberately adding `import "../adapters/in-memory.ts"` to `order.ts` makes your check fail.

## Before moving on

You can draw the hexagon with its arrows, build a use case against ports, and argue whether a given codebase should pay for it.

**Recap.** The domain owns the interfaces (ports); infrastructure implements them (adapters); every import points inward. The prize is a domain testable with no infrastructure and replaceable vendors. The cost is files, mapping and team discipline — adopt the cheap parts first.

**Next.** [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency injection and wiring]] — how the composition root builds all of this at startup (week 3).

## Key insight

Layering organises code; hexagonal architecture **inverts a dependency**. The move is that the inner layer *declares* what it needs and the outer layer *conforms* — so your business rules stop being a passenger in someone else's framework and become the thing everything else plugs into. That's genuinely valuable when the rules are the hard part. When the rules are `INSERT INTO orders`, you've built scaffolding around an empty room.

## Related
- [[backend/03-structuring-a-backend/04b-hexagonal-architecture-in-other-languages|Hexagonal Architecture in Other Languages]] — how each language's build enforces the dependency rule
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — the cheaper default
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency Injection]] — the mechanism that makes inversion possible
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — boundaries at the next scale up
- [[concepts/03-design-patterns/02-structural-patterns|Structural Patterns]] — adapter, facade
- [[architecture/03-architectural-patterns/index|Architectural Patterns]] — the system-level view
