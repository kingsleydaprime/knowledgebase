# Distributed Transactions

**[reference]** — from the canon (DDIA chapter 9). How to make an atomic "all-or-nothing" operation span multiple nodes/services — and why it's hard enough that the industry mostly avoids it.

## The problem

A single-database [[databases/database-design-reference|ACID]] transaction gives you atomicity for free: either all changes commit or none do. Split the data across nodes (sharding, or [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|microservices]] each with their own DB), and "transfer money from account A on node 1 to account B on node 2, atomically" becomes genuinely hard — because either node can fail mid-operation, leaving money debited but not credited.

## Two-Phase Commit (2PC)

The classic protocol for atomic commit across nodes, coordinated by a **transaction coordinator**:

1. **Prepare phase** — the coordinator asks every participant "can you commit?" Each does the work tentatively, locks the data, and votes **yes** (I promise I can commit) or **no**.
2. **Commit phase** — if *all* voted yes, the coordinator tells everyone "commit"; if *any* voted no, it tells everyone "abort." Participants that promised must obey.

This gives atomicity — but at a steep price:

- **Blocking / coordinator failure** — if the coordinator crashes *after* participants promised but *before* telling them commit-or-abort, participants are stuck: locked, holding resources, unable to decide alone. This is 2PC's fatal flaw — it's a **blocking** protocol. (**3PC** adds a phase to reduce blocking but assumes bounded network delays, so it's rarely used.)
- **Latency & locks** — multiple round-trips, and data stays locked across the whole protocol, killing throughput.
- **Availability** — one slow/down participant blocks the whole transaction ([[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability multiplies down]]).

2PC is used *within* some databases and distributed transaction managers (XA), but across services/microservices it's usually avoided precisely because of the blocking and coupling.

## Sagas — the pragmatic alternative

Because 2PC is so costly, most distributed systems use the **saga** pattern ([[architecture/03-architectural-patterns/03-data-and-integration-patterns|data & integration patterns]]) instead: a sequence of *local* transactions, each committing independently, with **compensating transactions** to undo prior steps if a later one fails.

The crucial difference: a saga gives you **eventual consistency, not atomic isolation.** There's no moment where everything is locked; instead, each step commits and is visible immediately, and failure triggers semantic rollbacks (refund, cancel). So an observer *can* see intermediate state (money debited, not yet credited) briefly — which the application must tolerate. In exchange, you get no blocking, no distributed locks, and independent service availability. For most business workflows, that trade is right.

## Idempotency: the load-bearing requirement

Because messages can be [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|lost, duplicated, or retried]], every step in a distributed transaction (saga *or* 2PC) must be **idempotent** — safe to apply more than once with the same effect. "Debit $50" applied twice on a retry is a bug; "set balance to X" or "apply debit with idempotency-key K (skip if seen)" is safe. This is exactly the [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency-key pattern]] from the real pipeline — and it's *mandatory*, not optional, in distributed transactions.

## Exactly-once, and the honest truth

Everyone wants "exactly-once" processing; in a distributed system it's [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|impossible to guarantee at the messaging layer]] (you can't tell a lost ack from a lost message). What you actually build is **at-least-once delivery + idempotent processing = effectively-once** *outcome*. Internalizing that "exactly-once is idempotency, not magic" is a mark of real distributed-systems understanding.

## Choosing

| Need | Use |
|---|---|
| Atomicity across a few nodes, can tolerate locking/blocking, same trust domain | **2PC** (rare, mostly within DBs) |
| Cross-service workflow, availability matters, can tolerate eventual consistency | **Saga** (the common choice) |
| Any of the above | **idempotent** operations, always |

## Related
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — sagas, orchestration vs choreography
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — atomic commit as a consensus problem
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|Idempotency (Java)]] — the idempotency-key pattern in real code
