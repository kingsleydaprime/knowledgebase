# Architecture — System Design & Distributed Systems

How to design systems that scale, stay up, and stay correct — and the distributed-systems theory underneath. This is the highest-signal domain for senior engineering judgment: it ties together everything else in the vault (databases, [[devops/README|devops]], the [[languages/01-java/06-applied-systems/README|Java systems work]], caching, messaging) into "how do you actually build something big and reliable."

## How this is organized

Two bodies of knowledge, in reading order:

- **System design** (sections 01–03) — the practical discipline of designing a system to meet scale/availability/latency requirements. Cross-referenced against the [roadmap.sh system-design roadmap](https://roadmap.sh/system-design).
- **Distributed systems** (section 04) — the deeper theory of *why* systems across multiple machines are hard, and the algorithms that tame it (consensus, replication, consistency, ordering). roadmap.sh has no distributed-systems roadmap, so this is sourced from the canon — *Designing Data-Intensive Applications* (DDIA), the distributed-systems literature (MIT 6.824) — and marked as such.

The existing [[architecture/system-design-reference|system-design-reference]] is kept as a **cheat-sheet companion** — a dense "everything to draw any system" lookup, complementing this pedagogical course.

## Sections

### [[architecture/01-system-design-fundamentals/README|01 — System Design Fundamentals]]
The mental model and the core tradeoffs.
1. [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|How to Approach System Design]] — the framework (requirements → estimation → high-level design → deep dive → tradeoffs); also how to pass the interview
2. [[architecture/01-system-design-fundamentals/02-scalability-and-performance|Scalability & Performance]] — vertical vs horizontal scaling, latency vs throughput, performance vs scalability
3. [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability & Reliability]] — the nines, SLA/SLO, redundancy, failover, fault tolerance
4. [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the CAP theorem, consistency models, and the availability-vs-consistency choice

### [[architecture/02-building-blocks/README|02 — Building Blocks]]
The reusable components every large system is assembled from.
1. [[architecture/02-building-blocks/01-load-balancing-and-proxies|Load Balancing & Proxies]] — L4/L7 load balancing, algorithms, reverse proxy, API gateway, CDN
2. [[architecture/02-building-blocks/02-caching|Caching]] — cache strategies, where to cache, eviction, and the invalidation problem
3. [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — SQL vs NoSQL, replication, sharding/partitioning, indexing, denormalization
4. [[architecture/02-building-blocks/04-messaging-and-async|Messaging & Async]] — message queues, pub/sub, event-driven, back-pressure, queue-based load leveling
5. [[architecture/02-building-blocks/05-communication|Communication]] — REST vs gRPC vs GraphQL, sync vs async, and the protocols underneath

### [[architecture/03-architectural-patterns/README|03 — Architectural Patterns]]
How components are arranged into whole architectures.
1. [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|Monolith / Microservices / Serverless]] — the big structural choice and when each fits
2. [[architecture/03-architectural-patterns/02-resilience-patterns|Resilience Patterns]] — circuit breaker, bulkhead, retry, timeout, throttling — designing for failure
3. [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — CQRS, event sourcing, saga, materialized views, strangler fig
4. [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices Patterns]] — service discovery, API gateway, sidecar/ambassador, BFF, leader election

### [[architecture/04-distributed-systems/README|04 — Distributed Systems]]
The theory. Harder, more foundational, and exactly what your build-your-own-Redis/DB/Raft projects need.
1. [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — partial failure, unreliable networks, no global clock, the 8 fallacies, FLP
2. [[architecture/04-distributed-systems/02-time-and-ordering|Time & Ordering]] — physical vs logical clocks, Lamport & vector clocks, causality
3. [[architecture/04-distributed-systems/03-replication-and-consistency|Replication & Consistency]] — leader/leaderless replication, quorums, the consistency-model spectrum, CRDTs
4. [[architecture/04-distributed-systems/04-consensus|Consensus]] — why it's hard, Paxos, Raft, leader election
5. [[architecture/04-distributed-systems/05-distributed-transactions|Distributed Transactions]] — 2PC/3PC, saga, isolation across nodes
6. [[architecture/04-distributed-systems/06-partitioning-and-fault-tolerance|Partitioning & Fault Tolerance]] — sharding strategies, consistent hashing, failure detection, gossip

### [[architecture/05-case-studies/README|05 — Case Studies & Practice]]
Applying it: designing real systems, and the **build-your-own** projects that are the actual reps.

## Related
- [[architecture/system-design-reference|system-design-reference]] — the dense cheat-sheet companion
- [[databases/database-design-reference|databases]] — the storage layer these systems are built on
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns (devops)]] — the resilience patterns from the ops angle
- [[project-ideas|Project Ideas]] — the build-your-own-X systems projects
