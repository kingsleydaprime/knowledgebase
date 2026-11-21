---
id: c3b7e75b-381b-4867-ae92-b9f9a75153de
---

# Availability & Reliability

## Availability, reliability, and the distinction
<!-- bite: 4bb57295-0be9-4e28-b89e-863650a85d2f -->

- **Availability** — the % of time the system is operational and serving requests. The headline metric.
- **Reliability** — the system works *correctly* (right answers, no data loss), not just "responds."

A system can be available but unreliable (returns wrong data fast) — you want both. Availability is what "the nines" measure.

## The nines
<!-- bite: 432ea272-3a92-49a1-b62e-17a93a1b8e8c -->

Availability is quoted as a percentage of uptime, and each nine is an order of magnitude harder and costlier:

| Availability | Downtime per year | Called |
|---|---|---|
| 99% | ~3.65 days | "two nines" |
| 99.9% | ~8.75 hours | "three nines" |
| 99.99% | ~52 minutes | "four nines" |
| 99.999% | ~5 minutes | "five nines" |

The practical lessons: **each nine costs disproportionately more** (five-nines requires redundancy, automation, and rigor that most systems don't need), so match the target to the actual business need — a photo-sharing app and a payment system have very different requirements. And when services depend on each other, **availability multiplies**: a service at 99.9% that depends on three other 99.9% services is at most ~99.6% — dependencies compound, so a chain of services is less available than any link.

## SLA, SLO, SLI
<!-- bite: bf6a2421-2b84-4064-871f-a7c1670621f8 -->

The vocabulary for committing to availability (shared with [[devops/07-observability/01-observability-fundamentals/index|observability]]):

- **SLI** (Indicator) — the measured signal (% of successful requests, p99 latency).
- **SLO** (Objective) — your internal target (99.95% over 30 days).
- **SLA** (Agreement) — the *contractual* promise to customers, with penalties. Deliberately looser than the SLO, so you have margin before breaching the contract.
- **Error budget** — the inverse of the SLO (99.9% availability = 0.1% budget for failure/risky deploys). Spend it on shipping features; when it's exhausted, freeze and stabilize.

## Designing for availability
<!-- bite: 0349adeb-d114-4f1f-9bef-0c43b77e800b -->

The core principle: **eliminate single points of failure through redundancy.** If any one component's failure takes down the system, that component needs a backup.

- **Redundancy** — run multiple instances of everything (app servers, databases). If one dies, others carry the load.
  - **Active-active** — all instances serve traffic (also load-balances); on failure, survivors absorb it.
  - **Active-passive (failover)** — a standby takes over when the primary fails; simpler but the standby sits idle.
- **Failover** — detecting a failure and switching to a backup. The hard parts are *fast, correct* detection (health checks — [[architecture/03-architectural-patterns/04-microservices-patterns|health monitoring]]) and avoiding **split-brain** (two nodes both think they're primary — a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] problem).
- **Geographic distribution** — spread across availability zones/regions ([[devops/08-cloud/01-cloud-fundamentals|cloud regions/AZs]]) so a data-center outage doesn't take you down.
- **Graceful degradation** — when a dependency fails, serve a reduced experience (stale cache, a default) instead of an error ([[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]]). The site stays up with less functionality.

## Reliability: don't lose data
<!-- bite: 77e870c0-f634-454e-8adc-3fb8e227c450 -->

Availability keeps you serving; reliability keeps the data correct:

- **Replication** — multiple copies of data so a disk/node failure doesn't lose it ([[architecture/04-distributed-systems/05-replication|replication]]).
- **Backups** — point-in-time copies to recover from corruption/mistakes/ransomware (test the *restore*, not just the backup).
- **Durability** — once the system acknowledges a write, it must survive failures (the "D" in ACID; why databases fsync to disk before ack'ing).

## The mindset
<!-- bite: 3353405b-6251-40aa-8890-f829e93a63a7 -->

The core shift for reliability engineering: **assume everything fails** — disks, networks, machines, whole data centers — and design so that failure is *contained and survivable* rather than catastrophic. This is the same "design for failure" instinct behind the [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]] and the entire [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|distributed-systems]] discipline.

## Related
<!-- bite: 83918d9b-ac2b-441f-9e82-1c03298f6082 -->
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the availability-vs-consistency tradeoff
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience Patterns]] — designing for graceful failure
- [[devops/07-observability/index|Observability (devops)]] — measuring and alerting on availability

## About this lesson
<!-- bite: 286f22cb-7d22-4492-8b23-bd1922f2fd3b -->

**Level:** reference. **Covers:** from the roadmap.sh system-design roadmap. Designing systems that stay up — because at scale, hardware *will* fail, and the design decides whether that's a blip or an outage.
