# 04 — Distributed Systems

The theory of systems that span multiple machines — *why* they're fundamentally hard, and the algorithms that tame the hardness. Harder and more foundational than the system-design sections, and exactly what your **build-your-own Redis / DB / Raft-KV** projects need. Part of the [[architecture/README|Architecture course]].

**Source:** roadmap.sh has no distributed-systems roadmap, so this is from the canon — *Designing Data-Intensive Applications* (Kleppmann), the distributed-systems literature (MIT 6.824, the Raft/Paxos papers). `[reference]` — deep theory to study and *build*, not something you'll fully grasp without implementing.

1. [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — **[Advanced]** — partial failure, unreliable networks, no global clock, the 8 fallacies, the FLP result
2. [[architecture/04-distributed-systems/02-time-and-ordering|Time & Ordering]] — **[Advanced]** — physical vs logical clocks, Lamport & vector clocks, happens-before/causality
3. [[architecture/04-distributed-systems/03-replication-and-consistency|Replication & Consistency]] — **[Advanced]** — leader/multi-leader/leaderless replication, quorums, the consistency-model spectrum (linearizable → eventual), CRDTs
4. [[architecture/04-distributed-systems/04-consensus|Consensus]] — **[Advanced]** — why agreement is hard, Paxos, Raft, leader election, and where they're used (etcd, ZooKeeper)
5. [[architecture/04-distributed-systems/05-distributed-transactions|Distributed Transactions]] — **[Advanced]** — 2PC/3PC, the saga pattern, isolation across nodes
6. [[architecture/04-distributed-systems/06-partitioning-and-fault-tolerance|Partitioning & Fault Tolerance]] — **[Advanced]** — sharding strategies, consistent hashing, failure detection, gossip, rebalancing

## Related
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals view of what this section proves
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — the single-machine version of many of these problems
- [[architecture/05-case-studies/README|Case Studies]] — the build-your-own projects that make this real
