# 03 — Architectural Patterns

How the [[architecture/02-building-blocks/README|building blocks]] are arranged into whole-system architectures, and the patterns that make them resilient and evolvable. Part of the [[architecture/README|Architecture course]].

1. [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|Monolith / Microservices / Serverless]] — **[Intermediate]** — the fundamental structural choice, and the honest tradeoffs (microservices are not a default)
2. [[architecture/03-architectural-patterns/02-resilience-patterns|Resilience Patterns]] — **[Advanced]** — circuit breaker, bulkhead, retry, timeout, throttling — designing so partial failure stays partial
3. [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — **[Advanced]** — CQRS, event sourcing, saga, materialized views, strangler fig
4. [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices Patterns]] — **[Advanced]** — service discovery, API gateway/aggregation, sidecar/ambassador, backends-for-frontends, leader election

## Related
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns (devops)]] — the same resilience patterns from the ops angle
- [[devops/05-orchestration/README|Orchestration (devops)]] — what microservices run on
- [[architecture/04-distributed-systems/README|Distributed Systems]] — the theory these patterns manage
