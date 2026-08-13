# Availability & Reliability

**[reference]** — from the roadmap.sh system-design roadmap. Designing systems that stay up — because at scale, hardware *will* fail, and the design decides whether that's a blip or an outage.

## Availability, reliability, and the distinction

- **Availability** — the % of time the system is operational and serving requests. The headline metric.
- **Reliability** — the system works *correctly* (right answers, no data loss), not just "responds."

A system can be available but unreliable (returns wrong data fast) — you want both. Availability is what "the nines" measure.

## The nines

Availability is quoted as a percentage of uptime, and each nine is an order of magnitude harder and costlier:

| Availability | Downtime per year | Called |
|---|---|---|
| 99% | ~3.65 days | "two nines" |
| 99.9% | ~8.75 hours | "three nines" |
| 99.99% | ~52 minutes | "four nines" |
| 99.999% | ~5 minutes | "five nines" |

The practical lessons: **each nine costs disproportionately more** (five-nines requires redundancy, automation, and rigor that most systems don't need), so match the target to the actual business need — a photo-sharing app and a payment system have very different requirements. And when services depend on each other, **availability multiplies**: a service at 99.9% that depends on three other 99.9% services is at most ~99.6% — dependencies compound, so a chain of services is less available than any link.

## SLA, SLO, SLI

The vocabulary for committing to availability (shared with [[devops/10-observability/01-observability-fundamentals|observability]]):

- **SLI** (Indicator) — the measured signal (% of successful requests, p99 latency).
- **SLO** (Objective) — your internal target (99.95% over 30 days).
- **SLA** (Agreement) — the *contractual* promise to customers, with penalties. Deliberately looser than the SLO, so you have margin before breaching the contract.
- **Error budget** — the inverse of the SLO (99.9% availability = 0.1% budget for failure/risky deploys). Spend it on shipping features; when it's exhausted, freeze and stabilize.

## Designing for availability

The core principle: **eliminate single points of failure through redundancy.** If any one component's failure takes down the system, that component needs a backup.

- **Redundancy** — run multiple instances of everything (app servers, databases). If one dies, others carry the load.
  - **Active-active** — all instances serve traffic (also load-balances); on failure, survivors absorb it.
  - **Active-passive (failover)** — a standby takes over when the primary fails; simpler but the standby sits idle.
- **Failover** — detecting a failure and switching to a backup. The hard parts are *fast, correct* detection (health checks — [[architecture/03-architectural-patterns/04-microservices-patterns|health monitoring]]) and avoiding **split-brain** (two nodes both think they're primary — a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] problem).
- **Geographic distribution** — spread across availability zones/regions ([[devops/03-cloud/01-cloud-fundamentals|cloud regions/AZs]]) so a data-center outage doesn't take you down.
- **Graceful degradation** — when a dependency fails, serve a reduced experience (stale cache, a default) instead of an error ([[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]). The site stays up with less functionality.

## Reliability: don't lose data

Availability keeps you serving; reliability keeps the data correct:

- **Replication** — multiple copies of data so a disk/node failure doesn't lose it ([[architecture/04-distributed-systems/05-replication|replication]]).
- **Backups** — point-in-time copies to recover from corruption/mistakes/ransomware (test the *restore*, not just the backup).
- **Durability** — once the system acknowledges a write, it must survive failures (the "D" in ACID; why databases fsync to disk before ack'ing).

## The mindset

The core shift for reliability engineering: **assume everything fails** — disks, networks, machines, whole data centers — and design so that failure is *contained and survivable* rather than catastrophic. This is the same "design for failure" instinct behind the [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]] and the entire [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|distributed-systems]] discipline.

## Related
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the availability-vs-consistency tradeoff
- [[architecture/03-architectural-patterns/02-resilience-patterns|Resilience Patterns]] — designing for graceful failure
- [[devops/10-observability/README|Observability (devops)]] — measuring and alerting on availability
