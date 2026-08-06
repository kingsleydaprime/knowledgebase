# Distributed Transactions

**[reference]** — from the canon (DDIA ch. 7 & 9). How to make an **all-or-nothing** operation span multiple nodes or services — the *atomicity* problem — and the **isolation** problem (how concurrent transactions interfere). This is the transaction cousin of [[architecture/04-distributed-systems/04-consistency-models|consistency models]]: consistency is about single-object recency; isolation is about multi-object interleaving.

## The kid version first

You want to move **$50 from your piggy bank to your sister's piggy bank** — but the two banks are in **different rooms**. The rule you need is **"both change, or neither does"**: it must never happen that $50 leaves yours and *doesn't* arrive in hers (money vanished) or arrives *without* leaving yours (money duplicated). Easy when both banks are on your desk. Hard when a room can get **locked** (a machine or network fails) *right in the middle*. Two ways people handle it:
1. **A referee counts everyone in.** *"Everyone ready to do their part? … Yes? … Okay — GO!"* If anyone says "not ready," nobody goes. (That's **Two-Phase Commit**.) The danger: if the **referee faints** right after "ready?" but before "GO!", everyone's frozen holding their breath. 
2. **Just do each step for real, and undo if needed.** Take $50 out of yours; put $50 in hers; if putting-in fails, **put the $50 back** in yours. No freezing, but for a moment an onlooker *can* see the money mid-flight. (That's a **Saga**.)

Everything below is those two ideas, made precise — plus the *other* transaction question: when **lots of kids** read and write the shared banks at once, what confusing things are they allowed to see? (That's **isolation**.)

## Atomicity across nodes — Two-Phase Commit (2PC)

A single-database ACID transaction gives atomicity for free. Spread the data across nodes ([[architecture/04-distributed-systems/13-partitioning|sharding]], or [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|microservices]] each with their own DB) and "debit A on node 1, credit B on node 2, atomically" gets hard — either node can fail mid-way. **2PC** is the classic protocol, run by a **coordinator**:

1. **Prepare phase** — coordinator asks every participant *"can you commit?"* Each does the work tentatively, **locks the data**, writes it to durable storage, and votes **yes** ("I *promise* I can commit if told to") or **no**. A yes-vote is a binding promise it cannot take back.
2. **Commit phase** — if *all* voted yes, the coordinator writes its decision durably and tells everyone *"commit"*; if *any* voted no (or timed out), *"abort."* Participants that promised must obey.

Atomicity — at a steep price:
- **It's a *blocking* protocol (the fatal flaw).** If the coordinator crashes *after* participants promised but *before* announcing the decision, participants are **stuck**: they've locked resources and promised, but can't unilaterally decide (committing or aborting alone might contradict the coordinator's decision, which some other participant may already have heard). They must wait for the coordinator to recover. **3PC** adds a phase to reduce blocking but assumes bounded network delay, so it's rarely used.
- **Latency & lock contention** — multiple round-trips, and data stays locked across the *whole* protocol, crushing throughput.
- **Availability multiplies down** — one slow/down participant blocks the entire transaction ([[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability multiplies]]).

**Making 2PC less fragile:** the blocking flaw is the coordinator being a single point of failure — so production systems make the **coordinator itself a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] group** (its decision log replicated via Raft/Paxos), so a coordinator crash doesn't freeze everyone. In fact **atomic commit is itself a consensus problem** — "get all participants to agree commit-or-abort." 2PC is used *within* databases and via XA transaction managers, but across microservices it's usually avoided.

## Isolation — what concurrent transactions may see

Atomicity is "all-or-nothing per transaction." **Isolation** is the *other* half: when many transactions run at once, which interleavings are allowed? Weaker isolation = faster + more concurrency, but more anomalies. The ladder (weak → strong), each level *forbidding* one more anomaly:

| Level | Forbids | Anomaly it still allows |
|---|---|---|
| **Read Uncommitted** | (almost nothing) | **dirty reads** — seeing another txn's uncommitted change that may be rolled back |
| **Read Committed** | dirty reads/writes | **non-repeatable reads** — re-reading a row gives a different value (someone committed in between) |
| **Snapshot Isolation (Repeatable Read)** | non-repeatable reads | **write skew** & **phantoms** — two txns read an overlapping set, each makes a decision valid alone but not together |
| **Serializable** | *everything* — as if txns ran one-at-a-time | (none) — the gold standard |

*Kid version of the anomalies:* a **dirty read** is peeking at a change someone might still erase; a **non-repeatable read** is the price changing while you're still shopping; **write skew** is two doctors each going off-call because they each saw *the other* was still on — individually fine, together nobody's covering.

**MVCC (Multi-Version Concurrency Control)** is how modern databases give strong isolation without everyone blocking on locks: keep **multiple versions** of each row, and give each transaction a consistent **snapshot** (as of its start). Readers never block writers and vice-versa — they just read the version their snapshot points to. MVCC powers snapshot isolation and serializable-snapshot isolation in Postgres, Oracle, and the [[architecture/04-distributed-systems/11-modern-distributed-transactions|distributed databases]] in the next note. **Serializability** (isolation's strongest) and **linearizability** ([[architecture/04-distributed-systems/04-consistency-models|consistency's strongest]]) together are **strict serializability** — what Spanner offers.

## Sagas — the pragmatic alternative

Because 2PC is so costly, most cross-service systems use the **saga** pattern ([[architecture/03-architectural-patterns/03-data-and-integration-patterns|data & integration patterns]]): a sequence of *local* transactions, each committing independently, with **compensating transactions** to undo earlier steps if a later one fails (refund, cancel, release).

The key difference: a saga gives **eventual consistency, not atomic isolation.** Nothing is globally locked; each step commits and is *immediately visible*, and failure triggers *semantic* rollbacks. So an observer *can* briefly see intermediate state (money debited, not yet credited) — the app must tolerate that. In exchange: no blocking, no distributed locks, independent service availability. For most business workflows, that trade is right. Sagas come in two shapes — **orchestration** (a central coordinator drives the steps) and **choreography** (services react to each other's events).

## Idempotency — the load-bearing requirement

Because messages get [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|lost, duplicated, and retried]], **every step** (saga *or* 2PC) must be **idempotent** — safe to apply more than once with the same effect. "Debit $50" applied twice on a retry is a bug; "apply debit with idempotency-key K, skip if K already seen" is safe. This is the [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency-key pattern]] from the real pipeline — **mandatory, not optional.**

## Exactly-once — the honest truth

Everyone wants "exactly-once" processing; at the messaging layer it's [[architecture/04-distributed-systems/02-theoretical-limits|impossible to guarantee]] (you can't tell a lost message from a lost ack — Two Generals). What you actually build is **at-least-once delivery + idempotent processing = effectively-once *outcome*.** "Exactly-once is idempotency, not magic" is a mark of real understanding.

## Key insight

**Distributed transactions are two problems: atomicity ("both piggy banks change or neither") and isolation ("what can concurrent transactions see").** For atomicity, **2PC** gives all-or-nothing but *blocks* if the coordinator dies (fix: make the coordinator a consensus group — atomic commit *is* consensus); **sagas** trade atomic isolation for availability via local commits + compensations. For isolation, weaker levels allow more anomalies (dirty/non-repeatable reads, write skew); **MVCC** delivers strong isolation without lock contention via snapshots; serializable + linearizable = strict serializability. And underneath it all, everything must be **idempotent**, because "exactly-once" is just at-least-once + idempotency.

## Related
- [[architecture/04-distributed-systems/11-modern-distributed-transactions|Modern Distributed Transactions]] — Spanner/Calvin: serializable, cross-shard, at scale
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — isolation's single-object cousin; strict serializability
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — atomic commit as a consensus problem
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — sagas, orchestration vs choreography
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|Idempotency (Java)]] — the pattern in real code
