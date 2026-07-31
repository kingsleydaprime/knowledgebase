# Monolith / Microservices / Serverless

**[reference]** — from the roadmap.sh system-design roadmap. The biggest structural decision in a system's architecture — and the one most often made for the wrong reasons.

## Monolith

One deployable application containing all the functionality. The default, and — despite its reputation — usually the *right* starting point.

- **Pros** — simple to develop, test, deploy, and debug (one codebase, one process, in-process calls, easy transactions). No network between components, no distributed-systems problems. Fast to build.
- **Cons** — as it grows: slower builds, harder for many teams to work in parallel, the whole thing scales/deploys as a unit (can't scale just the hot part), and one bug can take down everything. A tangled "big ball of mud" if not kept modular.

A **modular monolith** (well-separated internal modules, one deployment) captures most of the organizational benefit of microservices without the distributed complexity — an underrated middle ground.

## Microservices

The application split into small, independently-deployable services, each owning one business capability and its own data, communicating over the network ([[architecture/02-building-blocks/05-communication|REST/gRPC]] or [[architecture/02-building-blocks/04-messaging-and-async|events]]).

- **Pros** — independent deployment and scaling (scale only the hot service), team autonomy (each team owns a service), technology diversity, and fault isolation (one service down needn't kill all).
- **Cons** — you trade code complexity for **operational and distributed-systems complexity**: network latency and failures between services, [[architecture/05-case-studies/01-designing-real-systems|distributed]] data (no cross-service transactions — you need [[architecture/03-architectural-patterns/03-data-and-integration-patterns|sagas]]), [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]], harder debugging/tracing, and a whole platform to run ([[devops/05-orchestration/README|orchestration]], [[architecture/03-architectural-patterns/04-microservices-patterns|service discovery, gateways]], distributed [[devops/10-observability/README|observability]]).

## The honest guidance

**Microservices are not a default or a maturity badge — they're a tradeoff you take on when the *organizational* scale demands it**, not when the traffic does. The real driver is usually *teams*: many teams stepping on each other in one codebase is the pain microservices relieve. Below that scale, they add enormous complexity for little benefit.

The widely-endorsed path: **start with a (modular) monolith**, and extract services *when you feel specific pain* — a component that needs independent scaling, a team that needs to deploy independently, a part with different reliability needs. The [[architecture/03-architectural-patterns/03-data-and-integration-patterns|strangler fig]] pattern does this incrementally. Premature microservices are one of the most common and costly architecture mistakes — you inherit all of distributed systems before you have the problems it solves.

## Serverless (FaaS)

Deploy functions; the platform runs and scales them, billing per-invocation, scaling to zero ([[devops/03-cloud/02-serverless|serverless]] in depth).

- **Pros** — no server management, automatic scaling, pay-per-use (great for spiky/unpredictable load), fast to ship.
- **Cons** — [[devops/03-cloud/02-serverless|cold starts]] (latency), execution limits (time, memory, statelessness), harder local dev/testing, and potential vendor lock-in. Cost flips above sustained high load (a busy VM is cheaper).

Great for event-driven glue, spiky workloads, and cron-style jobs; not for latency-critical steady-state services.

## Choosing

| Situation | Reach for |
|---|---|
| New project, small team, unproven idea | **Monolith** (start here) |
| Many teams, proven need for independent scale/deploy | **Microservices** |
| Spiky/event-driven/glue work, want zero ops | **Serverless** |

The mature answer is often **a mix**: a core monolith, a few extracted services where they earn it, and serverless for event glue — architecture chosen per-component from the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|requirements]], not by fashion.

## Related
- [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices Patterns]] — the machinery microservices require
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — strangler fig, saga (the migration + data path)
- [[devops/05-orchestration/README|Orchestration (devops)]] — what microservices run on
