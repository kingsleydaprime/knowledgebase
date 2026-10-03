# Modular Monolith → Services

**[Intermediate→Advanced]** — the structural decision people get wrong most expensively, because both failure modes take a year to become obvious.

## Before you start

You can already:

- Organise code by feature and enforce boundaries with a lint rule → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|layer vs feature]].
- Use the observer pattern to react to events → [[concepts/03-design-patterns/03-behavioral-patterns/index|behavioural patterns]].

After this lesson you will be able to:

1. State what microservices buy and what they cost, in one sentence each.
2. Build a modular monolith whose modules talk through a published API and events, and own their own data.
3. Show why moving to a message broker demands **idempotent consumers**, and write one.
4. Name a legitimate reason to extract a service, and the strangler-fig steps to do it safely.

**Study route.** Kid version and §1–4, then the worked example. §6 (what changes over a network) is the interview-relevant part.

## The kid version first

You're organising a big house.

- **One room, everything in it** (the *big ball of mud*): fast to start, impossible to find anything later.
- **Separate buildings across town** (*microservices*): each is tidy, but now every conversation needs a phone call that might not connect, and moving furniture between them is a logistics project.
- **One house, with walls and doors** (the *modular monolith*): rooms are separate, but walking between them is free and instant.

Almost everyone who jumps to separate buildings does it **before knowing where the walls should go** — and a wall in the wrong place is a renovation; a *building* in the wrong place is a demolition.

**Where the analogy stops working.** Walls in a house stay where you built them. Walls in code get walked through the moment there's a deadline — a quick database join, a direct import. A modular monolith's walls only exist if a tool enforces them.

## 1. Why this exists

A startup splits its first app into eight microservices on day one. Six months later, placing an order calls four services synchronously. A slow inventory service makes checkout time out. A customer is charged but has no order, because the two services couldn't share a transaction. And half the team's time goes to keeping eight deploy pipelines green. None of the eight services needed to scale on its own. **They paid distributed-systems costs for a benefit they didn't have** — and the boundaries were in the wrong places anyway, because nobody knew the domain yet.

## Terms used in this lesson

1. **Monolith**: This is an application deployed as a single unit — one process (or several identical copies), one codebase, usually one database.
2. **Big ball of mud**: This is a monolith with no internal boundaries, where any code can call or query anything.
3. **Modular monolith**: This is a monolith split into modules with enforced boundaries: each owns its data and is reached only through its published API or events.
4. **Microservices**: This is an architecture where each module is a separately deployed service, talking to the others over the network.
5. **Message broker**: This is a separate system — RabbitMQ, Kafka, SQS — that stores events and delivers them to subscribers, even if they're temporarily down.
6. **At-least-once delivery**: This is the guarantee most brokers give. Every event arrives, but some may arrive more than once.
7. **Idempotent**: This describes an operation that has the same effect whether it runs once or several times. "Set paid to true" is idempotent; "add ₦5,000 to the balance" is not.
8. **Saga**: This is a multi-step operation across services where each step has a **compensating action** that undoes it if a later step fails, because no single transaction can cover them all.
9. **Strangler fig**: This is a pattern for replacing or extracting part of a system gradually, routing traffic piece by piece to the new path while the old one still works.

## 2. What you're actually buying and paying

Microservices trade **local complexity for distributed complexity.** That's the entire trade, and it should be stated that plainly.

| You buy | You pay |
|---|---|
| Independent deployment | network calls that fail, retry, and time out |
| Independent scaling | no transactions across services → sagas, eventual consistency |
| Independent tech choices | distributed tracing, or you debug blind |
| Team autonomy (the real driver) | operational burden: CI/CD ×N, service discovery, versioning |
| Fault isolation (*if* you design for it) | a function call becomes an API contract you can't refactor atomically |

**The honest version:** microservices are primarily an **organisational** solution — they let teams deploy without coordinating. If you don't have that problem, you're paying the cost for a benefit you don't need.

## 3. Why "start with a monolith" is right

Not conservatism — an information argument. **Service boundaries are the hardest thing to get right, and you know least about them on day one.**

- A wrong boundary inside a monolith is a **refactor**: move some files, change some imports, your compiler finds every call site. An afternoon.
- A wrong boundary between services is a **migration**: two deployables, two databases, an API contract, data backfill, coordinated release. Weeks, and a period where the system is worse.

So: **discover the boundaries where getting them wrong is cheap, then extract.** By the time you've built the domain for a year, you know where the seams actually are — and they're usually not where you'd have guessed.

## 4. The modular monolith

One deployable, one codebase, one database — with **enforced internal boundaries**:

```
src/
├── orders/
│   ├── api/           ← the ONLY thing other modules may import
│   ├── internal/      ← private: entities, repositories, services
│   └── orders.module.ts
├── payments/
│   ├── api/
│   └── internal/
└── shared/            ← genuinely cross-cutting only (logging, config, db handle)
```

The rules that make it real:

1. **Modules talk only through a published interface.** `orders/api`, not `orders/internal/whatever`.
2. **No shared tables across modules.** Each module owns its tables; another module reads them through the owner's API, not by joining. **This is the single most important rule** — it's the one that determines whether extraction is possible later, and the one everybody breaks first because a join is *right there*.
3. **Prefer events for cross-module reactions.** `payments` publishes `PaymentSucceeded`; `orders` subscribes. That's an in-process event bus now, a message broker later, with no call-site changes.
4. **Enforce it mechanically.** ESLint `import/no-restricted-paths`, dependency-cruiser, Java modules, .NET internal visibility, or ArchUnit-style tests. **Boundaries that rely on discipline do not survive a deadline.** → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|by-feature organisation]]

You keep transactions, atomic refactors, one deploy, one place to debug — while building the boundary knowledge you'd need to split.

## 5. When to actually extract a service

Extract for a **specific, named reason**, not a vibe:

- **Independent scaling** — one component's resource profile is genuinely different (video transcoding vs. CRUD).
- **Team autonomy** — a team is blocked on someone else's release cadence. The most legitimate reason, and the original one.
- **Fault isolation** — a component must not take the system down with it.
- **Different technology** — genuinely needs Rust, or a GPU, or a different runtime.
- **Compliance/data residency** — a hard boundary is required.
- **Independent lifecycle** — deploys 20× a day while the rest deploys weekly.

**Not reasons:** the codebase feels big; microservices are modern; you want clean architecture; a conference talk.

### How to extract, when you do

The **strangler fig** pattern — incremental, reversible at every step:

1. **Make it a clean module first.** If it isn't already isolated in the monolith, extracting it will fail. This step is most of the work, and doing it may reveal you don't need to extract at all.
2. **Put a facade in front** so all callers go through one interface.
3. **Separate the data.** Stop cross-module joins; the module owns its tables exclusively. **Usually the hardest step, and where most extractions stall.**
4. **Move the module out**, keeping the same interface — now over the network.
5. **Switch traffic gradually** behind a flag, with the ability to switch back.
6. **Delete the old path** once it's been quiet for a while.

Steps 1–3 deliver most of the benefit and are reversible. If you stop after step 3, you have a well-modularised monolith, which is a perfectly good place to stop.

## 6. What changes the moment it's over a network

The things people forget, and then rediscover in an incident:

- **Every call can fail, hang, or be slow.** You need timeouts, retries with jitter, and circuit breakers on every one. → [[backend/interview/01-production-debugging|retry storms]]
- **No transactions.** A cross-service operation needs a saga with compensating actions — and compensation is a *business* decision (you can't un-send an email), not a technical one.
- **Duplicate delivery.** At-least-once messaging means idempotent consumers, always.
- **Tail latency multiplies.** One request fanning out to 10 services waits for the slowest of 10.
- **Versioning is now permanent.** You can no longer change a function signature and fix all callers in one commit. Every interface change needs a backward-compatible rollout.
- **Debugging needs distributed tracing** before you need it, not after.

→ [[architecture/04-distributed-systems/index|distributed systems]] · [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]]

## 7. Worked example — two modules, one event, and a broker that delivers twice

Two modules in one process. `payments` publishes `PaymentSucceeded`; `orders` subscribes and tracks how much each order has been paid. **`orders` never imports `payments`** — they share only the event's shape, in `shared/`.

```
mono/
├── mono.test.ts
└── src/
    ├── shared/bus.ts       event types + the bus: the seam between modules
    ├── payments/api.ts
    └── orders/api.ts
```

```ts
// src/shared/bus.ts — the seam between modules. In-process today; a broker later.
export type PaymentSucceeded = { type: "PaymentSucceeded"; eventId: string; orderId: string; amountKobo: number };
export type Event = PaymentSucceeded;
export type Handler = (event: Event) => Promise<void>;

export interface EventBus {
  publish(event: Event): Promise<void>;
  subscribe(type: Event["type"], handler: Handler): void;
}

export function inProcessBus(): EventBus {
  const handlers: Handler[] = [];
  return {
    subscribe: (_type, handler) => { handlers.push(handler); },
    publish: async (event) => { for (const h of handlers) await h(event); },
  };
}

// What a message broker really promises: at-least-once. This one delivers every event twice.
export function atLeastOnceBus(): EventBus {
  const inner = inProcessBus();
  return {
    subscribe: inner.subscribe,
    publish: async (event) => { await inner.publish(event); await inner.publish(event); },
  };
}
```

```ts
// src/payments/api.ts — the only file other modules may import from payments/
import type { EventBus } from "../shared/bus.ts";

export function makePayments(bus: EventBus) {
  let n = 0;
  return {
    async recordSuccess(orderId: string, amountKobo: number) {
      n++;
      await bus.publish({ type: "PaymentSucceeded", eventId: `evt_${n}`, orderId, amountKobo });
    },
  };
}
```

```ts
// src/orders/api.ts — orders reacts to payments without importing payments/ at all
import type { EventBus } from "../shared/bus.ts";

export function makeOrders(bus: EventBus, options: { idempotent: boolean }) {
  const paidKobo = new Map<string, number>(); // orders' own table: nobody else touches it
  const seen = new Set<string>();

  bus.subscribe("PaymentSucceeded", async (event) => {
    if (options.idempotent) {
      if (seen.has(event.eventId)) return; // already handled this exact event
      seen.add(event.eventId);
    }
    paidKobo.set(event.orderId, (paidKobo.get(event.orderId) ?? 0) + event.amountKobo);
  });

  return { paidSoFar: (orderId: string) => paidKobo.get(orderId) ?? 0 };
}
```

**Predict before running.** You replace the in-process bus with the at-least-once one, as if you'd moved to a real broker. The orders module is unchanged and not idempotent. A ₦5,000 payment (500,000 kobo) succeeds. What does `paidSoFar("o1")` return?

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { atLeastOnceBus, inProcessBus } from "./src/shared/bus.ts";
import { makeOrders } from "./src/orders/api.ts";
import { makePayments } from "./src/payments/api.ts";

test("in-process: one payment, recorded once", async () => {
  const bus = inProcessBus();
  const orders = makeOrders(bus, { idempotent: false });
  await makePayments(bus).recordSuccess("o1", 500_000);
  assert.equal(orders.paidSoFar("o1"), 500_000);
});

test("at-least-once delivery + a naive consumer = the customer is credited twice", async () => {
  const bus = atLeastOnceBus();
  const orders = makeOrders(bus, { idempotent: false });
  await makePayments(bus).recordSuccess("o1", 500_000);
  assert.equal(orders.paidSoFar("o1"), 1_000_000);
});

test("at-least-once delivery + an idempotent consumer = correct", async () => {
  const bus = atLeastOnceBus();
  const orders = makeOrders(bus, { idempotent: true });
  const payments = makePayments(bus);
  await payments.recordSuccess("o1", 500_000);
  await payments.recordSuccess("o1", 250_000); // a genuinely second payment still counts
  assert.equal(orders.paidSoFar("o1"), 750_000);
});
```

**Lab:** these files are in [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/typescript). From the vault root, `python3 labs/run.py modular-monolith-to-services/typescript` runs them and checks this page still shows the same code.

**Run it.** From `mono/`: `node --test` (Node 23.6 or later; checked with Node 26). Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

**The answer: 1,000,000 kobo** — the customer has been credited twice for one payment. The second test asserts that wrong value on purpose. Nothing in `orders` or `payments` changed. The only thing that changed was the transport, and that's the point: **the event seam lets you swap the transport without touching the call sites, but it doesn't make the network's guarantees go away.** The fix is in the consumer — remember each `eventId` you've handled — and the third test shows it still counts a genuinely second payment, which has a new `eventId`.

**In production**, `seen` would be a database table with a unique constraint on `event_id`, written in the same transaction as the balance update, so a crash can't record one without the other. The producer side has the matching problem — saving and publishing as one step — and the [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]] solves it.

## Check your understanding

1. In one sentence: what do microservices buy, and what do they cost?
2. Why is "start with a monolith" an information argument, not a conservative one?
3. Which modular-monolith rule decides whether a module can ever be extracted, and why does everyone break it first?
4. Give two legitimate reasons to extract a service, and two that aren't.
5. In the worked example, why does the duplicate only appear after switching buses, even though the orders code didn't change?

<details>
<summary>Answers — after your attempt</summary>

1. They buy independent deployment, scaling and team autonomy; they cost network failure, no cross-service transactions, and operational overhead.
2. Boundaries are hardest to get right and you know least about them at the start. Inside a monolith, a wrong boundary is a cheap refactor; between services, it's an expensive migration. So you discover them where mistakes are cheap.
3. No shared tables — each module owns its data. A cross-module join is the quickest way to get a feature done, so it's broken first, and it ties two modules' storage together so they can't be separated.
4. Legitimate (any two): independent scaling, team autonomy, fault isolation, different technology, compliance, a different deploy cadence. Not (any two): the codebase feels big, it's modern, clean architecture, a conference talk.
5. The in-process bus delivers exactly once, so the consumer's lack of idempotency was invisible. The at-least-once bus exposes it. A network transport changes the guarantees, not the code.

</details>

## Practice — independent task

**Extend the worked example into a three-module monolith.**

1. Add an `inventory` module that reserves stock when it receives `PaymentSucceeded`, and publishes `StockReserved` or `StockUnavailable`.
2. Make `orders` mark an order `confirmed` on `StockReserved`, and publish `RefundRequested` on `StockUnavailable` — a compensating action, as in a saga.
3. Make every consumer idempotent, and run the whole flow on `atLeastOnceBus`.
4. Add an ESLint `no-restricted-paths` zone (or a `grep` test) proving no module imports another module's files — only `shared/`.

**Done when:** on the at-least-once bus, an out-of-stock order ends with exactly one refund request and an in-stock order with exactly one reservation, and the boundary check fails if you add a cross-module import.

## Before moving on

You can argue monolith-first with reasons, build modules that talk through events and own their data, and explain why a broker forces idempotency.

**Recap.** Microservices trade local complexity for distributed complexity, and are mainly an organisational tool. Find boundaries in a modular monolith first: published APIs, no shared tables, events between modules, enforced by tooling. Extract for a named reason, using the strangler fig. Over a network, everything can fail, duplicate or arrive late.

**Next.** That closes the Software design block. Week 5 starts architecture with [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|how to approach system design]].

## Key insight

The choice isn't monolith vs microservices — it's **where your boundaries are and how strongly they're enforced.** A modular monolith and a microservice architecture can have identical boundaries; they differ only in whether crossing one is a function call or a network call. So get the boundaries right *first*, in the cheap medium, and treat the network as a deployment decision you make later for a specific reason. **A distributed big ball of mud is the worst of both worlds, and it is the most common outcome of starting with microservices.**

## Related
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services/in-other-languages|The Modular Monolith in Other Languages]] — event plumbing and idempotent consumers in seven languages
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|By layer vs by feature]] — the module boundaries this depends on
- [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|Monolith / Microservices / Serverless]] — the system-design framing
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — saga, event sourcing, strangler fig
- [[architecture/interview/01-system-design-round|System design interview]] — "when would you *not* use microservices?"
