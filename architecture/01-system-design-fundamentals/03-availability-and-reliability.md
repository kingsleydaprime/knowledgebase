---
id: c3b7e75b-381b-4867-ae92-b9f9a75153de
---

# Availability & Reliability

Availability is how much of the time a system is up and answering, and reliability is whether it gives the right answers without losing data. A bank app that opens but shows the wrong balance is available but not reliable. This lesson shows how both are measured and how systems are built to keep them high.

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

## Check your understanding
<!-- bite: 88b1e087-bb9f-4fca-b6f2-40a459efce88 -->

Try each one before you open the answer.

1. <!-- q: mcq id="71cdbf84" -->
   A bank app opens quickly every time, but sometimes shows the wrong balance. Which is it?

   - [x] Available but not reliable
   - [ ] Reliable but not available
   - [ ] Both available and reliable
   - [ ] Neither

   <details><summary>Answer</summary>

   Availability is the share of time the system is up and answering. Reliability is whether it answers correctly without losing data. This app answers, but wrongly.

   </details>

2. <!-- q: gap id="74b57b84" answers="SLI;SLO;SLA" -->
   Fill in the gaps. The measured signal, such as the share of successful requests, is the ___. Your internal target, such as 99.95% over 30 days, is the ___. The contractual promise to customers, with penalties, is the ___.

   <details><summary>Answer</summary>

   SLI (indicator), SLO (objective) and SLA (agreement). The SLA is set looser than the SLO, so there is a margin before the contract is breached.

   </details>

3. <!-- q: mcq id="7e7eabe0" -->
   A service at 99.9% availability depends on three other services, each also at 99.9%. What is the most the whole chain can manage?

   - [ ] 99.9%, the same as each link
   - [x] About 99.6%, because availabilities multiply
   - [ ] 99.97%, because there are more services to share the load
   - [ ] 97%, because each dependency takes off 1%

   <details><summary>Answer</summary>

   0.999 × 0.999 × 0.999 × 0.999 ≈ 0.996. A request needs every link to be up, so a chain is less available than any one of its links.

   </details>

4. <!-- q: mcq id="2cc4aed1" -->
   Two database nodes lose touch with each other during a failover, and both decide they are the primary. What is this called?

   - [ ] Graceful degradation
   - [ ] Active-active
   - [x] Split-brain
   - [ ] An error budget

   <details><summary>Answer</summary>

   Split-brain. Avoiding it is one of the hard parts of failover, and it's a consensus problem: the nodes must agree on a single primary.

   </details>

5. <!-- q: open id="bcdf7953" -->
   Why shouldn't every system aim for five nines (99.999%) of availability?

   <details><summary>Answer</summary>

   Each extra nine costs disproportionately more: five nines needs redundancy, automation and rigour most systems don't need. The target should match the business need. A payment system may justify it; a photo-sharing app doesn't.

   </details>

6. <!-- q: open id="8dd40311" -->
   A team backs up its database every night but has never tried a restore. Why is that a reliability risk?

   <details><summary>Answer</summary>

   A backup is only useful if you can restore from it. Without testing the restore, you don't know whether the backups are complete, uncorrupted or fast enough to recover from, and you find out during the disaster.

   </details>

## Check your understanding: worked problems
<!-- bite: 7c678deb-0c2a-4cbe-9b97-e40b02a66d8d -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="221c47a5" answer="4.38" sigfigs="2" -->
   A service promises 99.95% availability. How many hours of downtime does that allow in a year of 365 days?

   <details><summary>Answer</summary>

   About 4.4 hours. The allowed downtime is 0.05% of the year: 365 × 24 × 0.0005 = 4.38 hours.

   </details>

2. <!-- q: exact id="55227e4e" answer="99.7402249300" sigfigs="3" accept="0.997|0.9974" -->
   A request passes through four services in a chain. Their availabilities are 99.9%, 99.95%, 99.99% and 99.9%. What is the most the whole chain can manage, as a percentage?

   <details><summary>Answer</summary>

   About 99.74%. Availabilities multiply: 0.999 × 0.9995 × 0.9999 × 0.999 ≈ 0.9974. That's lower than the weakest link.

   </details>

3. <!-- q: exact id="3c00555c" answer="43.2" sigfigs="2" -->
   A team's SLO is 99.9% availability over 30 days. Its error budget is the 0.1% left over. How many minutes of downtime is that?

   <details><summary>Answer</summary>

   43.2 minutes. 30 × 24 × 60 = 43,200 minutes, and 0.1% of that is 43.2.

   </details>

4. <!-- q: exact id="e430ff10" answer="6.6" sigfigs="2" -->
   A team's SLO is 99.95% over 30 days. A bad deploy this month has already caused 15 minutes of downtime. How many minutes of error budget are left?

   <details><summary>Answer</summary>

   6.6 minutes. The budget is 0.05% of 43,200 minutes = 21.6 minutes, and 21.6 − 15 = 6.6. With so little left, the team should slow down risky deploys.

   </details>

## Related
<!-- bite: 83918d9b-ac2b-441f-9e82-1c03298f6082 -->
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the availability-vs-consistency tradeoff
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience Patterns]] — designing for graceful failure
- [[devops/07-observability/index|Observability (devops)]] — measuring and alerting on availability

## About this lesson
<!-- bite: 286f22cb-7d22-4492-8b23-bd1922f2fd3b -->

**Level:** reference. **Covers:** from the roadmap.sh system-design roadmap. Designing systems that stay up — because at scale, hardware *will* fail, and the design decides whether that's a blip or an outage.
