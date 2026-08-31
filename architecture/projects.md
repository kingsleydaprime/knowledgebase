# Architecture — Projects

*The hardest domain to get reps in, because real architecture needs scale you don't have. The workaround: **build the small version and then break it deliberately.** A three-node system you can partition teaches more than a diagram of a hundred.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 **Write a design doc for something you already built** — context, constraints, options considered, decision, trade-offs accepted. **Done when:** someone else could rebuild it from the doc, and you've named at least one thing you'd do differently. Exercises: [[architecture/01-system-design-fundamentals/README|fundamentals]].

- 🟢 **Do five system-design questions on a whiteboard, out loud, timed** — 45 minutes each, using [[architecture/system-design-reference|the cheat sheet]] only afterwards to check yourself. **Done when:** you stop drawing boxes and start naming numbers (QPS, storage, bandwidth).

- 🟡 **Cache invalidation, for real** — put Redis in front of a real read path in one of your apps. **Done when:** you've handled a stampede, chosen a TTL you can justify, and can describe the staleness window a user might see. Exercises: [[architecture/02-building-blocks/README|caching]].

- 🟡 ⭐ **Break your own system** — take a service you built, run it with a dependency behind a proxy (Toxiproxy), and inject latency, packet loss, and hard failures. **Done when:** you've found at least one failure mode you didn't know you had, and fixed it. Exercises: [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|why this is hard]].

- 🟡 **Idempotency and exactly-once, honestly** — build a payment-ish flow with an outbox, at-least-once delivery, and an idempotent consumer. **Done when:** you can explain to someone why exactly-once delivery doesn't exist but exactly-once *effect* does. Exercises: [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]].

- 🟡 **Event sourcing something small** — an append-only log plus a projection. **Done when:** you can rebuild current state from the log alone, and you've hit the first schema-evolution problem. Exercises: [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log]].

- 🔴 ⭐ **A Raft key-value store** — leader election, log replication, safety, then a replicated KV store on top. Test it against crashes and partitions. **Done when:** you kill the leader mid-write and the cluster stays consistent. (MIT 6.824 is the gold standard.) **The best distributed-systems rep that exists** — and the one that turns [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] from reading into knowledge.

- 🔴 **Implement a CRDT and prove convergence** — a G-counter, then an LWW-set, then a text CRDT. **Done when:** randomised concurrent operations in any order converge, verified by a property test. Exercises: [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]].

- 🔴 **Rebuild one case study** — pick something from [[architecture/05-case-studies/README|case studies]] and actually build a toy of it end to end. **Done when:** it handles a load test and you've written up where your design diverges from the real one.

## If you only do one

**Raft.** Every distributed-systems idea in this folder — leaders, terms, quorums, split brain, linearisability — stops being vocabulary the first time your own cluster elects a leader after you killed one.

## Related
- [[architecture/README|the architecture course]] · [[architecture/interview/README|interview bank]]
- [[architecture/system-design-reference|system design cheat sheet]]
- [[project-ideas|Project Ideas]] — the vault-wide index
