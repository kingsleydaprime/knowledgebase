# Modular Monolith → Services

**[Intermediate→Advanced]** — the structural decision people get wrong most expensively, because both failure modes take a year to become obvious.

## The kid version first

You're organising a big house.

- **One room, everything in it** (the *big ball of mud*): fast to start, impossible to find anything later.
- **Separate buildings across town** (*microservices*): each is tidy, but now every conversation needs a phone call that might not connect, and moving furniture between them is a logistics project.
- **One house, with walls and doors** (the *modular monolith*): rooms are separate, but walking between them is free and instant.

Almost everyone who jumps to separate buildings does it **before knowing where the walls should go** — and a wall in the wrong place is a renovation; a *building* in the wrong place is a demolition.

## What you're actually buying and paying

Microservices trade **local complexity for distributed complexity.** That's the entire trade, and it should be stated that plainly.

| You buy | You pay |
|---|---|
| Independent deployment | network calls that fail, retry, and time out |
| Independent scaling | no transactions across services → sagas, eventual consistency |
| Independent tech choices | distributed tracing, or you debug blind |
| Team autonomy (the real driver) | operational burden: CI/CD ×N, service discovery, versioning |
| Fault isolation (*if* you design for it) | a function call becomes an API contract you can't refactor atomically |

**The honest version:** microservices are primarily an **organisational** solution — they let teams deploy without coordinating. If you don't have that problem, you're paying the cost for a benefit you don't need.

## Why "start with a monolith" is right

Not conservatism — an information argument. **Service boundaries are the hardest thing to get right, and you know least about them on day one.**

- A wrong boundary inside a monolith is a **refactor**: move some files, change some imports, your compiler finds every call site. An afternoon.
- A wrong boundary between services is a **migration**: two deployables, two databases, an API contract, data backfill, coordinated release. Weeks, and a period where the system is worse.

So: **discover the boundaries where getting them wrong is cheap, then extract.** By the time you've built the domain for a year, you know where the seams actually are — and they're usually not where you'd have guessed.

## The modular monolith

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
4. **Enforce it mechanically.** ESLint `import/no-restricted-paths`, dependency-cruiser, Java modules, .NET internal visibility, or ArchUnit-style tests. **Boundaries that rely on discipline do not survive a deadline.** → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|by-feature organisation]]

You keep transactions, atomic refactors, one deploy, one place to debug — while building the boundary knowledge you'd need to split.

## When to actually extract a service

Extract for a **specific, named reason**, not a vibe:

- **Independent scaling** — one component's resource profile is genuinely different (video transcoding vs. CRUD).
- **Team autonomy** — a team is blocked on someone else's release cadence. The most legitimate reason, and the original one.
- **Fault isolation** — a component must not take the system down with it.
- **Different technology** — genuinely needs Rust, or a GPU, or a different runtime.
- **Compliance/data residency** — a hard boundary is required.
- **Independent lifecycle** — deploys 20× a day while the rest deploys weekly.

**Not reasons:** the codebase feels big; microservices are modern; you want clean architecture; a conference talk.

## How to extract, when you do

The **strangler fig** pattern — incremental, reversible at every step:

1. **Make it a clean module first.** If it isn't already isolated in the monolith, extracting it will fail. This step is most of the work, and doing it may reveal you don't need to extract at all.
2. **Put a facade in front** so all callers go through one interface.
3. **Separate the data.** Stop cross-module joins; the module owns its tables exclusively. **Usually the hardest step, and where most extractions stall.**
4. **Move the module out**, keeping the same interface — now over the network.
5. **Switch traffic gradually** behind a flag, with the ability to switch back.
6. **Delete the old path** once it's been quiet for a while.

Steps 1–3 deliver most of the benefit and are reversible. If you stop after step 3, you have a well-modularised monolith, which is a perfectly good place to stop.

## What changes the moment it's over a network

The things people forget, and then rediscover in an incident:

- **Every call can fail, hang, or be slow.** You need timeouts, retries with jitter, and circuit breakers on every one. → [[backend/interview/01-production-debugging|retry storms]]
- **No transactions.** A cross-service operation needs a saga with compensating actions — and compensation is a *business* decision (you can't un-send an email), not a technical one.
- **Duplicate delivery.** At-least-once messaging means idempotent consumers, always.
- **Tail latency multiplies.** One request fanning out to 10 services waits for the slowest of 10.
- **Versioning is now permanent.** You can no longer change a function signature and fix all callers in one commit. Every interface change needs a backward-compatible rollout.
- **Debugging needs distributed tracing** before you need it, not after.

→ [[architecture/04-distributed-systems/README|distributed systems]] · [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

## Key insight

The choice isn't monolith vs microservices — it's **where your boundaries are and how strongly they're enforced.** A modular monolith and a microservice architecture can have identical boundaries; they differ only in whether crossing one is a function call or a network call. So get the boundaries right *first*, in the cheap medium, and treat the network as a deployment decision you make later for a specific reason. **A distributed big ball of mud is the worst of both worlds, and it is the most common outcome of starting with microservices.**

## Related
- [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|By layer vs by feature]] — the module boundaries this depends on
- [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|Monolith / Microservices / Serverless]] — the system-design framing
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — saga, event sourcing, strangler fig
- [[architecture/interview/01-system-design-round|System design interview]] — "when would you *not* use microservices?"
