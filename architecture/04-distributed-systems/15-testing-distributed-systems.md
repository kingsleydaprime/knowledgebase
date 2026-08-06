# Testing Distributed Systems

**[reference]** · **⏳ outline — deep note in progress** (part of the distributed-systems deep-curriculum build). The capstone: distributed bugs live in the rare interleavings — a partition healing at the exact wrong moment — that ordinary tests never hit. This is how the field actually catches them.

## Will cover
- **Why normal testing fails here** — the bugs are in timing- and failure-dependent interleavings ([[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|partial failure]] × concurrency); a green unit-test suite says almost nothing about correctness under partition.
- **Jepsen** (Kyle Kingsbury) — the standard for *empirically* breaking distributed databases: generate concurrent operations, inject faults with a **nemesis** (partitions, clock skew, crashes, pauses), record a history, then use a **linearizability checker** (Knossos/Elle) to prove whether that history is consistent with the claimed [[architecture/04-distributed-systems/04-consistency-models|consistency model]]. Has embarrassed nearly every major DB — invaluable reading.
- **Deterministic simulation testing** — run the *entire* system single-threaded on a simulated network/clock with a seeded RNG, so any bug is perfectly reproducible and you can explore millions of schedules. FoundationDB and TigerBeetle build their whole engineering culture on this; arguably the most effective technique that exists.
- **Chaos engineering** — inject real faults in production/staging (Netflix's Chaos Monkey) to verify the system degrades as designed; testing the [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure-handling]] you *think* you have.
- **Formal methods** — **TLA+** (and its PlusCal front-end) to model-check a protocol's design *before* implementing, catching spec-level bugs (AWS uses it heavily); the Raft and Paxos safety properties are TLA+-verified.
- **Fault injection & property-based testing** as the everyday layer beneath the above.

## Related
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] · [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] · [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] · [[architecture/05-case-studies/README|Case Studies]]
