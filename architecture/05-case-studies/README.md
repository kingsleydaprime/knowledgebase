# 05 — Case Studies & Practice

Where the theory becomes skill: applying the framework to design real systems, and the **build-your-own** projects that are the actual reps. Part of the [[architecture/README|Architecture course]].

1. [[architecture/05-case-studies/01-designing-real-systems|Designing Real Systems]] — **[Advanced]** — the classic design problems (URL shortener, a news feed, a rate limiter, a chat system) worked through the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|framework]], and how to reason about each

## Build it to learn it

Reading distributed-systems theory without implementing it is famously ineffective — the reps are in the building. The flagship systems projects (in [[project-ideas|Project Ideas]]):

- **Your own Redis** — in-memory data structures + a network protocol + persistence
- **Your own database** — a storage engine (B-tree/LSM), indexing, transactions
- **Your own git** — content-addressable storage, DAGs, the object model
- **A Raft key-value store** — [[architecture/04-distributed-systems/04-consensus|consensus]] made concrete: leader election, log replication, fault tolerance

Each one turns a section of this course from words into something you understand in your bones.

## Related
- [[architecture/README|Architecture course map]]
- [[project-ideas|Project Ideas]] — the build-your-own-X projects
- [[architecture/system-design-reference|system-design-reference]] — the cheat-sheet for the interview
