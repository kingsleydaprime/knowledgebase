# Architecture Interview — Distributed Systems Depth

From [[architecture/04-distributed-systems/README|04-distributed-systems]]. The round for infrastructure, platform, and senior backend roles — where they check whether your system design answers rest on understanding or on pattern-matching.

---

### Q1. [Advanced] 🔥 Why is exactly-once delivery impossible, and what do you build instead?

**Strong answer covers:** the sender cannot distinguish "my message was lost" from "the reply was lost." If it retries, the receiver may process twice; if it doesn't, the message may be lost. No protocol resolves this, because the ambiguity is in the *failure model*, not the implementation.

**What you build:** **at-least-once delivery plus an idempotent receiver** — sometimes marketed as "effectively-once." Deduplicate on a message ID, or make the operation naturally idempotent (`SET x = 5` rather than `INCREMENT x`).

**The nuance that impresses:** Kafka's "exactly-once semantics" is real but narrow — it's exactly-once *within Kafka*, via idempotent producers and transactional writes to Kafka topics. The moment you write to an external database, you're back to needing idempotency. Vendors blur this; knowing where the boundary is signals you've read the design rather than the marketing.

---

### Q2. [Advanced] 🔥 Explain consensus. Why is Raft easier to understand than Paxos?

**Strong answer covers:** consensus is getting N nodes to agree on a value despite failures, with **safety** (never disagree) and **liveness** (eventually decide). **FLP** proves you can't guarantee both in a fully asynchronous system with even one faulty node — so real systems use timeouts, sacrificing guaranteed liveness for practical progress.

**Raft vs Paxos:** Paxos is described as independent proposals reaching agreement, with the practical protocol (Multi-Paxos) left largely as an exercise — famously hard to implement correctly. **Raft decomposes the problem explicitly** into leader election, log replication, and safety, and adds the **strong leader** constraint: all entries flow leader→follower, never the reverse. That constraint removes enormous case-analysis. Raft was *designed for understandability* as a stated goal, which is unusual and worth noting.

**Key mechanisms to name:** terms as a logical clock; the log matching property; a candidate can only win if its log is at least as up-to-date as the voter's (which is what guarantees a committed entry is never lost); and the Figure 8 rule — **a leader may not commit an entry from a previous term by counting replicas alone**; it must commit an entry from its own term first. That last one is the subtlest part of the protocol and naming it proves you read the paper.

**The strongest possible answer:** "I implemented it." → [[project-ideas|the Raft KV store]] is a 🔴 ⭐ project and the single highest-value thing you could build for this round.

---

### Q3. [Advanced] 🔥 Why can't you use timestamps to order events across machines?

**Strong answer covers:** **clock skew.** Physical clocks drift, NTP corrects in jumps (so time can go *backwards*), and VM pauses and GC can freeze a process for seconds. Two events microseconds apart on different machines can carry timestamps in the wrong order — so last-write-wins with wall clocks **silently loses data**.

**What to use instead:** **logical clocks**. Lamport clocks give you a total order consistent with causality (but `L(a) < L(b)` doesn't prove causation). **Vector clocks** can distinguish "happened-before" from "concurrent" — which is what you need to *detect* a conflict rather than silently overwrite one.

**The modern answer:** **Hybrid Logical Clocks** (physical + logical, keeping both causality and rough wall-clock meaning), and Google Spanner's **TrueTime**, which makes bounded-uncertainty timestamps work by *waiting out* the uncertainty interval with GPS and atomic clocks. Spanner is essentially "buy your way out of the clock problem with hardware."

→ [[architecture/04-distributed-systems/03-time-and-ordering|time & ordering]]

---

### Q4. [Advanced] Walk the consistency models from strongest to weakest.

**Strong answer covers:**
- **Linearizable** — behaves like a single copy; every read sees the most recent write, and operations appear to take effect instantaneously. Requires coordination, so it costs latency; can't be maintained during a partition (CP).
- **Sequential** — all nodes see operations in the same order, but not necessarily real-time order.
- **Causal** — causally related operations are ordered everywhere; concurrent ones may differ. **The strongest model available without coordination** — which is why it's such an interesting point on the spectrum.
- **Eventual** — replicas converge if writes stop. Says nothing about when, or what you see meanwhile.

**Session guarantees worth naming** because they're what users actually notice: read-your-writes (you see your own comment after posting — the classic bug when reads go to a lagging replica), monotonic reads (you don't see time go backwards), consistent prefix.

**The framing that scores:** these are a **cost spectrum, not a quality ranking**. Stronger consistency = more coordination = more latency and less availability. Choose per operation, not per system — a "like" count can be eventual; an account balance cannot.

---

### Q5. [Advanced] What are CRDTs and when would you reach for one?

**Strong answer covers:** data structures whose merge is **commutative, associative, and idempotent** — so replicas converge regardless of the order updates arrive, whether they arrive twice, or who merges. Merge behaves like addition, so order stops mattering.

**Why it's powerful:** convergence **without coordination** — no consensus, no leader, no locking. Just merge on reconnect.

**Examples:** G-Counter/PN-Counter, OR-Set (add-wins over concurrent remove), sequence CRDTs (RGA/Yjs/Automerge) powering collaborative editors.

**When to reach for one:** offline-first and collaborative applications — Figma-style multiplayer, local-first apps, shopping carts that must never lose an item.

**The honest limitation, which you should volunteer:** CRDTs guarantee *convergence*, not that the converged value is what a user wanted. An OR-Set that resolves "add wins" will resurrect a deleted item. And they can't express global invariants — you cannot build "balance must never go negative" as a CRDT, because that requires coordination by definition. → [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]]

---

### Q6. [Advanced] 🔥 2PC vs saga — when do you use each?

**Strong answer covers:**
- **2PC** — a coordinator asks all participants to prepare, then commits if all agree. Gives atomicity, but it's a **blocking** protocol: if the coordinator dies after prepare, participants hold locks indefinitely, unable to decide. Bad availability, and it doesn't scale past a few tightly-coupled participants.
- **Saga** — a sequence of local transactions, each with a **compensating** transaction to undo it. Non-blocking and scalable, but you get **no isolation** — intermediate states are visible, so another transaction can observe a half-completed saga.

**When to use each:** 2PC within one trust/latency domain where you truly need atomicity (a distributed database's internals). Sagas across services — which is nearly always the case in application architecture.

**The detail that shows real thought:** compensation is **not** rollback. You can't un-send an email or un-ship a package; you send an apology or process a return. Designing the compensating action is a *business* decision, not a technical one, and that's the hardest part of adopting sagas.

---

### Q7. [Advanced] How does a system detect that a node has failed?

**Strong answer covers:** it fundamentally **can't** — you cannot distinguish a crashed node from a slow one or a partitioned one. Every failure detector is a **timeout heuristic**, trading detection speed against false positives.

**Mechanisms:** heartbeats with a fixed timeout (crude); **phi-accrual** detectors that output a *suspicion level* from the observed distribution of heartbeat intervals rather than a boolean, letting the application choose its own threshold; **gossip** for scalable membership (each node talks to a few random peers, information spreads epidemically in O(log n) rounds); **SWIM**, which adds indirect probing — before declaring a node dead, ask other nodes to probe it, dramatically cutting false positives from a single bad network path.

**The consequence to name:** **split-brain**. Two halves of a partition each believe the other is dead and both elect a leader. Prevented by quorum (a majority is required to act, and there can only be one majority) and **fencing tokens** — a monotonically increasing number so that a resurrected old leader's writes are rejected by the storage layer. Naming fencing tokens specifically is a strong signal; it's the mechanism most people miss.

---

### Q8. [Advanced] Why is "the log" such a fundamental abstraction?

**Strong answer covers:** an append-only, totally-ordered sequence of records. Because it's ordered and immutable, **any two replicas that apply the same log get the same state** — that's the replicated state machine principle, and it's how consensus systems, database replication, and Kafka all work.

**Where the same idea appears:** write-ahead logs (durability before mutation), database replication streams, Kafka's partitions, event sourcing, CDC pipelines, and Raft's log.

**The insight to state:** the log **turns state into a derivative of history.** Instead of "what is the value," you have "what happened, in order" — and state becomes a materialised view you can rebuild, replay, or project differently. That's what makes event sourcing, CDC, and stream processing all the same idea wearing different clothes. → [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log]]

---

### Q9. [Advanced] How do you test a distributed system?

**Strong answer covers:** normal tests don't find these bugs, because the bugs live in *interleavings and partial failures* that don't occur under happy-path conditions.

- **Jepsen** — generate operations against a real cluster while injecting partitions and clock skew, then check the history for linearizability violations. It has found serious correctness bugs in most commercial distributed databases, which is the point worth making: this is genuinely hard and vendors get it wrong.
- **Deterministic simulation** (FoundationDB's approach) — run the whole system in a simulated single-threaded environment with controllable clocks and message delivery, so any bug found is **reproducible from a seed**. The most powerful technique in the list.
- **Chaos engineering** — inject failure in production, with a hypothesis and a blast-radius limit.
- **TLA+ / formal methods** — model-check the protocol *before* implementing it. AWS uses it for S3/DynamoDB.

**The point to make:** you're not testing that it works, you're testing **that it doesn't break in ways you can't imagine** — which means generating the interleavings rather than enumerating them by hand. → [[architecture/04-distributed-systems/15-testing-distributed-systems|testing distributed systems]]

---

### Q10. [Advanced] 🔥 What's the hardest thing about distributed systems?

An open question — they want to see how you think, not a fact.

**A strong answer:** *"Partial failure. In a single process, things either work or crash. In a distributed system, a call can succeed, fail, or — the hard one — hang forever with no way to tell 'dead' from 'slow.' Every hard problem in the field falls out of that one impossibility: consensus needs timeouts because of it, exactly-once is impossible because of it, split-brain happens because of it, and idempotency exists to survive it."*

Then ground it in something you've actually hit — an idempotency bug, a duplicate message, a replication-lag issue. **A concrete story beats an elegant abstraction**, and having both is the best answer available.
