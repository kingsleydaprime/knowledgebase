# Scalability & Performance

**[reference]** — from the roadmap.sh system-design roadmap. The vocabulary that's constantly confused — and getting it precise is half of system-design competence.

## Performance vs scalability — not the same thing

- **Performance** — how fast the system is for *one* user / one request (latency).
- **Scalability** — how well it handles *more* load (users, data, requests) without falling over.

A system can be fast for one user and collapse at 10,000 (fast but not scalable), or handle millions while each request is sluggish (scalable but not performant). The pointed diagnostic: **if performance degrades as load rises, you have a scalability problem; if it's slow even under light load, you have a performance problem.** They need different fixes, so name which one you have.

## Latency vs throughput

- **Latency** — time for a single operation (the round-trip for one request). Measured in ms; you care about the *distribution*, especially tail latency (**p99**), not the average — a 50ms average hiding a 2s p99 means 1% of users have a terrible time ([[devops/10-observability/01-observability-fundamentals|observability]]).
- **Throughput** — operations completed per unit time (requests/sec, rows/sec).

They trade off and interact: batching improves throughput but adds latency; a queue smooths throughput at the cost of latency. Aim to maximize throughput at an *acceptable* latency, rather than optimizing one blindly.

## Vertical vs horizontal scaling

The two ways to handle more load:

| | Vertical (scale up) | Horizontal (scale out) |
|---|---|---|
| How | a bigger machine (more CPU/RAM) | more machines |
| Simplicity | simple — no code changes, no distribution | complex — needs [[architecture/02-building-blocks/01-load-balancing-and-proxies\|load balancing]], stateless design, [[architecture/04-distributed-systems/README\|distributed-systems]] concerns |
| Ceiling | hard limit (biggest machine you can buy) | effectively unlimited |
| Failure | single point of failure | survives node loss (redundancy) |
| Cost | expensive at the top end | commodity hardware, but more of it |

**Start vertical** (simpler, and modern machines are huge — don't distribute before you must), **scale horizontally when you hit the ceiling or need fault tolerance.** Horizontal scaling is the path to real scale, but it *requires statelessness*: application servers must hold no per-user state locally, so any server can handle any request (state goes to a shared [[architecture/02-building-blocks/03-databases-at-scale|database]]/[[architecture/02-building-blocks/02-caching|cache]]). This statelessness is the single most important enabler of scale.

## The scaling toolkit (a preview)

When one server isn't enough, the standard moves — each its own note:

1. **Add a [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancer]]** + more stateless app servers (horizontal scaling of compute).
2. **[[architecture/02-building-blocks/02-caching|Cache]]** hot data to take read load off the database (usually the first bottleneck).
3. **[[architecture/02-building-blocks/03-databases-at-scale|Scale the database]]** — read replicas for read-heavy load, sharding for write-heavy.
4. **[[architecture/02-building-blocks/04-messaging-and-async|Go async]]** — offload slow work to a queue so requests return fast.
5. **[[architecture/02-building-blocks/01-load-balancing-and-proxies|CDN]]** for static content near users.

## The core insight

Scaling is a sequence of **finding the current bottleneck and relieving it** — there's always a bottleneck (compute, database, network, a hot key), and scaling is whack-a-mole against it. This is why [[devops/10-observability/README|measurement]] matters: you scale what the metrics say is the constraint, not what you assume. And it's why the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|record-generator pipeline's]] real bottleneck was the database write path, not the file reading — you have to measure to know.

## Related
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability & Reliability]] — horizontal scaling also buys fault tolerance
- [[architecture/02-building-blocks/README|Building Blocks]] — the tools in the scaling toolkit
- [[ai-ml/02-ml-engineer/README|ML Engineer]]'s data pipelines — throughput/latency in another domain
