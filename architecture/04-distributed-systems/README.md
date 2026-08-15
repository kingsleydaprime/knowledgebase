# 04 — Distributed Systems

The theory of systems that span multiple machines — *why* they're fundamentally hard, and the algorithms that tame the hardness. The hardest and most foundational material in the [[architecture/README|Architecture course]], and exactly what the **build-your-own Redis / DB / Raft-KV** projects need.

**Source:** roadmap.sh has no distributed-systems roadmap, so this is from the canon — Kleppmann's *Designing Data-Intensive Applications*, MIT 6.824, and the primary papers (Lamport, FLP, CAP/Gilbert-Lynch, Raft, Spanner). `[reference]` — deep theory to study *and build*; you won't fully grasp it without implementing (esp. [[architecture/04-distributed-systems/08-raft-in-depth|Raft]]).

**A deep curriculum, grouped into five parts.** Every note opens with a plain-language *"kid version first"* intuition before going to full depth, and ends with a **Key insight**. Read A→C, then build a Raft KV-store, then D→E.

## Part A — Foundations (the models & limits)
1. [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — **[Advanced]** — partial failure, the failure/timing/clock models, process pauses, why perfect failure detection is impossible, safety vs liveness, the 8 fallacies
2. [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — **[Advanced]** — Two Generals, FLP, CAP → PACELC, the consistency/latency tradeoff, CALM
3. [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — **[Advanced]** — happens-before, Lamport & vector clocks (worked traces), Hybrid Logical Clocks, TrueTime

## Part B — Consistency & Replication
4. [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — **[Advanced]** — linearizable → sequential → causal → eventual, session guarantees, the cost of strong consistency
5. [[architecture/04-distributed-systems/05-replication|Replication]] — **[Advanced]** — leader / multi-leader / leaderless, quorums, read-repair, anti-entropy, the Dynamo lineage
6. [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs & Conflict Resolution]] — **[Advanced]** — LWW, state/op CRDTs, causal merge, version vectors, where it's used

## Part C — Consensus
7. [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — **[Advanced]** — why agreement is hard, Paxos & Multi-Paxos, quorums, where it's used (etcd, ZooKeeper)
8. [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — **[Advanced]** — RPCs field-by-field, log matching, the Figure-8 commitment rule, membership changes, snapshots, linearizable client sessions, ReadIndex
9. [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]] — **[Advanced]** — ZooKeeper/etcd, leases, fencing tokens, VR/ZAB, BFT/PBFT

## Part D — Transactions & Storage
10. [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — **[Advanced]** — 2PC/3PC, isolation levels, MVCC, the saga pattern, idempotency
11. [[architecture/04-distributed-systems/11-modern-distributed-transactions|Modern Distributed Transactions]] — **[Advanced]** — Spanner/TrueTime, Percolator, Calvin, CockroachDB
12. [[architecture/04-distributed-systems/12-the-log-and-state-machines|The Log & State Machines]] — **[Advanced]** — replicated state machines, Kafka, LSM-trees, CDC, event sourcing

## Part E — Partitioning & Operations
13. [[architecture/04-distributed-systems/13-partitioning|Partitioning]] — **[Advanced]** — sharding strategies, consistent hashing, rebalancing, hotspots
14. [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection & Membership]] — **[Advanced]** — heartbeats, phi-accrual, gossip, SWIM, anti-entropy, split-brain
15. [[architecture/04-distributed-systems/15-testing-distributed-systems|Testing Distributed Systems]] — **[Advanced]** — Jepsen, deterministic simulation, chaos, TLA+

## How to actually learn this

Reading isn't enough here — distributed systems reward *implementation* more than any other topic in the vault. The path that sticks: read Part A–C, then **build a Raft KV-store** ([[architecture/05-case-studies/README|case studies]]) — it forces every consensus edge case to become real. Then the transactions / storage / ops parts land, because you've felt why they're hard.

## Related
- [[databases/README|Databases]] — the single-node view: MVCC, WAL, and the operator's side of replication and sharding
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals-level view of what this section proves
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — the single-machine version of many of these problems
- [[architecture/05-case-studies/README|Case Studies]] — the build-your-own projects that make this real
