# Hexagonal & Clean Architecture

**[Intermediate→Advanced]** — layering with the dependency direction actually enforced. Also known as ports and adapters, onion architecture, and clean architecture — **largely the same idea under four names**, which is itself worth knowing so you don't think they're four things to learn.

## The kid version first

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

## The dependency inversion, concretely

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

## What you actually get

1. **The domain is testable with zero infrastructure.** No database, no HTTP, no containers, no framework. Tests run in milliseconds and never flake. This is the real prize.
2. **Multiple entry points for free.** HTTP, a CLI, a queue consumer, and a scheduled job are four driving adapters over one use case. No duplication.
3. **Infrastructure decisions become deferrable and reversible.** Start with an in-memory repository, add Postgres when you know the access patterns. Swapping Stripe for Paystack is one adapter.
4. **The business rules are findable.** In a typical CRUD codebase, "what are the rules for placing an order?" is answered by reading a controller, a service, three ORM hooks and a database constraint. Here, there's one file.

## The honest cost

This is where most write-ups stop, and they shouldn't. Hexagonal architecture is **genuinely expensive** and frequently misapplied:

- **More files, more indirection.** A simple create-read-update-delete resource becomes an entity, a port, an adapter, a use case, a DTO, and two mappers. For a CRUD screen, that's a poor trade — you've paid an abstraction tax for flexibility you'll never spend.
- **Mapping fatigue.** Domain objects ≠ ORM entities ≠ DTOs means writing and maintaining mapping code between all three. Real, ongoing, boring cost.
- **You give up your ORM's conveniences.** Lazy loading, change tracking, and query builders all want to reach across the boundary you just drew.
- **Team cost.** Everyone has to understand it or they'll route around it, and a half-applied hexagonal architecture is worse than plain layering — you get the file count without the guarantee.

**Where it's worth it:** complex, long-lived domains with real business rules — payments, logistics, insurance, scheduling, anything with invariants that matter and a long life ahead of it.

**Where it isn't:** CRUD services, thin API gateways, most internal tools, and anything where the "business logic" is genuinely `INSERT` and `SELECT`. Use [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|plain layering]] there and don't apologise for it.

## The four names, briefly

- **Hexagonal / Ports & Adapters** (Cockburn, 2005) — the original. The hexagon shape means nothing; it's just "many sides, many adapters."
- **Onion Architecture** (Palermo, 2008) — same rule, drawn as concentric rings.
- **Clean Architecture** (Martin, 2012) — same rule plus named rings (entities, use cases, interface adapters, frameworks) and the explicit **Dependency Rule**: *source code dependencies point only inward.*
- **DDD's layered architecture** — compatible, and adds the vocabulary for what goes *inside* the domain: aggregates, value objects, domain events, bounded contexts.

Treat them as one idea with four vocabularies. Knowing that saves you from reading four books to learn one rule.

## A pragmatic middle ground

Most teams should not go all-in. What you can adopt cheaply and get most of the value:

- **Keep HTTP out of services.** Domain errors, not status codes. (Free, huge payoff.)
- **Define the interface where it's consumed**, not where it's implemented — even without a full domain layer.
- **Push one thing behind a port: the one most likely to change.** Usually a third-party API (payments, email, storage), not the database.
- **Keep the pure rules pure.** Extract the genuinely tricky logic — pricing, eligibility, state transitions — into functions with no I/O. They become trivially testable and you've captured 80% of the benefit for 10% of the cost.

## Key insight

Layering organises code; hexagonal architecture **inverts a dependency**. The move is that the inner layer *declares* what it needs and the outer layer *conforms* — so your business rules stop being a passenger in someone else's framework and become the thing everything else plugs into. That's genuinely valuable when the rules are the hard part. When the rules are `INSERT INTO orders`, you've built scaffolding around an empty room.

## Related
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers]] — the cheaper default
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency Injection]] — the mechanism that makes inversion possible
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — boundaries at the next scale up
- [[concepts/03-design-patterns/02-structural-patterns|Structural Patterns]] — adapter, facade
- [[architecture/03-architectural-patterns/README|Architectural Patterns]] — the system-level view
