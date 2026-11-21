---
id: 27125b0a-3c59-422a-b8c2-68bb4e551a04
---

# Data & Integration Patterns

Data and integration patterns are ways of keeping data correct when it is spread across many services and databases instead of one. With one database, a single transaction can update everything at once. Once the data is split, you need other methods, and this lesson covers the main ones.

## The problem these solve
<!-- bite: d84d103a-d367-4f72-8b4e-64574524a8c2 -->

In a monolith, one database and ACID transactions handle everything. Once data is split across services/stores, you lose the easy transaction and the single query — so you need patterns to keep data consistent, queryable, and evolvable across boundaries. All of these trade the simplicity of one strongly-consistent database for scale and decoupling, at the cost of [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]] and more moving parts.

## CQRS (Command Query Responsibility Segregation)
<!-- bite: 4fa63d62-7dae-4995-b16d-9d22302acab9 -->

Separate the **write** model from the **read** model. Instead of one representation serving both, commands (writes) go to a write-optimized store, and queries (reads) hit one or more read-optimized stores (denormalized, indexed for specific queries, often a different database).

- **Why** — reads and writes have very different needs and volumes; separating them lets each scale and be optimized independently (a read model shaped exactly for a screen, updated from write events).
- **Cost** — two models to keep in sync (usually via [[architecture/02-building-blocks/04-messaging-and-async/index|events]]), so the read side is eventually consistent, and it's more complex. Reach for it when read/write asymmetry is genuinely painful — not by default.

## Event Sourcing
<!-- bite: af81663f-e0ac-47d9-8d7b-aee19b5cedf5 -->

Instead of storing the *current state*, store the **sequence of events** that produced it (append-only log). Current state is derived by replaying events.

- **Why** — a perfect audit log (every change, forever), the ability to reconstruct any past state or fix a bug and replay, and a natural fit with [[architecture/02-building-blocks/04-messaging-and-async/index|event-driven]] systems and CQRS (events update the read models).
- **Cost** — a big mental shift, event schema evolution is tricky, and "what's the current state?" requires replay (or snapshots). Powerful for domains where history/audit is first-class (finance, ledgers — the [[languages/01-java/06-applied-systems/index|payment domain]]); overkill for simple CRUD.

CQRS and event sourcing pair naturally but are independent — you can use either alone.

## Saga — distributed transactions without 2PC
<!-- bite: 49d5ef2b-65c1-464f-bd96-a0186899f6f4 -->

The answer to "I need a transaction across services, but there's no shared database." A **saga** is a sequence of local transactions, one per service, coordinated so that if any step fails, **compensating transactions** undo the previous steps (a semantic rollback — "refund the payment" rather than a DB rollback):

```text
Order → Payment → Inventory → Shipping
  if Inventory fails: compensate Payment (refund), compensate Order (cancel)
```

- **Orchestration** — a central coordinator tells each service what to do and triggers compensations. Clearer control flow, but the orchestrator is a component to build.
- **Choreography** — each service reacts to events and emits its own, no central brain. More decoupled, but the flow is implicit and harder to follow.

Sagas give you eventual consistency across services (not the atomic isolation of a real [[architecture/04-distributed-systems/10-distributed-transactions|distributed transaction]]) — a mid-saga observer can see partial state. Usually the right tradeoff, because true distributed transactions (2PC) are slow and fragile.

Each step must save its local change **and** announce the next step reliably — which is exactly the dual-write problem. The standard answer is the [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]]: write the event in the same local transaction as the change, and let a relay publish it.

## Materialized View
<!-- bite: 725fbd86-0e75-4aeb-b755-928b374f2121 -->

A precomputed, stored result of an expensive query (a join/aggregation), refreshed as data changes — so reads are a cheap lookup instead of recomputing every time. A [[architecture/02-building-blocks/02-caching/index|caching]]/[[architecture/02-building-blocks/03-databases-at-scale|denormalization]] idea at the database level, and often *how* a CQRS read model is built.

## Strangler Fig
<!-- bite: 9ed71ebb-2a90-4124-bd58-f7e9d11460e3 -->

The pattern for **incrementally** migrating a [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|monolith to microservices]] (or replacing any legacy system) without a risky big-bang rewrite. Put a [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|proxy/gateway]] in front, then extract functionality one piece at a time — routing that piece's traffic to the new service while everything else still hits the monolith. The new system grows around the old (like a strangler fig around a tree) until the old one can be retired. The safe, boring, correct way to modernize — vastly less risky than a rewrite.

## The through-line
<!-- bite: 37ba5424-0a6f-4a5d-81ee-003bcf3e29f5 -->

Every pattern here manages the same fundamental loss: **once data crosses a transaction/service boundary, you trade strong consistency and simple queries for scale and decoupling.** CQRS/materialized views recover query performance; event sourcing recovers history; sagas recover cross-service "transactions" (as eventual consistency); strangler fig lets you get there safely. Adopt each only when its specific pain is real — they all add complexity you don't want prematurely.

## Related
<!-- bite: f777c3ea-1958-4692-a2f4-96e8f790b2d6 -->
- [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional Outbox]] — how each saga step announces itself reliably
- [[architecture/02-building-blocks/04-messaging-and-async/index|Messaging & Async]] — the event backbone these run on
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — 2PC, the alternative sagas avoid
- [[languages/01-java/06-applied-systems/index|Applied Systems (Java)]] — a real payment/ledger domain

## About this lesson
<!-- bite: 69c9cdf3-bee6-4a06-ab07-8fc53e3be787 -->

**Level:** reference. **Covers:** from the roadmap.sh system-design roadmap. The patterns for managing data and integration in systems too big for one database and one transaction — especially [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|microservices]], where each service owns its own data.
