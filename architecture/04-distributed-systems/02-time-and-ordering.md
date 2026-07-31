# Time & Ordering

**[reference]** — from the canon (Lamport's "Time, Clocks, and the Ordering of Events," DDIA). How to reason about "what happened before what" when there's [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|no global clock]] — a surprisingly deep problem that underpins consistency and consensus.

## Why ordering is the whole game

Distributed systems constantly need to know the order of events: which write is newer, did this happen before that, which update wins. On one machine a clock or a lock gives you order for free. Across machines, with clocks that disagree and messages that arrive out of order, establishing order is genuinely hard — and getting it wrong causes lost updates and inconsistency.

## Physical clocks and why they fail you

Two kinds of physical clock, both problematic for ordering:

- **Time-of-day clocks** (wall-clock) — synced via NTP, but they *jump* (forward/backward on sync) and drift. Two machines' wall clocks differ by milliseconds+.
- **Monotonic clocks** — only move forward (good for measuring elapsed time on *one* machine) but are meaningless *across* machines (no shared zero).

The trap: **using wall-clock timestamps to order events across nodes.** "Last write wins by timestamp" can silently *lose data* — if node A's clock is 50ms ahead of B, A's older write can have a *later* timestamp than B's newer write, so the newer write is discarded. Clock skew makes timestamp-ordering across nodes fundamentally unreliable. (Google's Spanner spends real engineering — TrueTime, atomic clocks + GPS — to bound this uncertainty, which shows how hard it is.)

## Logical clocks — order without time

Lamport's insight: for ordering, you don't need *real time* — you need a consistent notion of **"happens-before."** Logical clocks capture causal order using counters, not wall time.

### Happens-before (→)

Event A "happens-before" B (A → B) if: they're on the same node and A came first, OR A is a message send and B is its receive, OR transitively. If neither A → B nor B → A, they're **concurrent** — genuinely no defined order, and that's OK.

### Lamport clocks

Each node keeps a counter:
- Increment on each local event.
- Attach the counter to every message sent.
- On receive, set your counter to `max(local, received) + 1`.

This guarantees: **if A → B, then Lamport(A) < Lamport(B).** So Lamport timestamps give a total order consistent with causality (ties broken by node ID). The limitation: the converse *doesn't* hold — `Lamport(A) < Lamport(B)` does **not** mean A → B; they might be concurrent. Lamport clocks can *order* but can't *detect concurrency*.

### Vector clocks

To actually *detect* causality vs concurrency, use a **vector clock** — each node tracks a vector of counters (one per node). Comparing two vectors tells you exactly: A → B (A's vector ≤ B's elementwise), B → A, or **concurrent** (neither dominates). This is how [[architecture/04-distributed-systems/03-replication-and-consistency|leaderless replication]] (Dynamo-style) detects conflicting concurrent writes so it can resolve them, instead of silently losing one. The cost: the vector grows with the number of nodes.

## Why this feeds everything else

- **Consistency models** ([[architecture/04-distributed-systems/03-replication-and-consistency|next]]) are defined in terms of what orderings are guaranteed — causal consistency literally means "respects happens-before."
- **Conflict resolution** in [[architecture/04-distributed-systems/03-replication-and-consistency|replication]] uses vector clocks to know which writes conflict.
- **Consensus** ([[architecture/04-distributed-systems/04-consensus|Raft/Paxos]]) is, in part, machinery to impose a single agreed *total order* on operations despite all this.

The deep lesson: **in a distributed system, "when" is the wrong question — "in what causal order" is the right one**, and you get that from logical clocks and message-passing, not from timestamps. This reframing is one of the most important ideas in the field.

## Related
- [[architecture/04-distributed-systems/03-replication-and-consistency|Replication & Consistency]] — consistency models defined via ordering; vector-clock conflict resolution
- [[architecture/04-distributed-systems/04-consensus|Consensus]] — imposing a single total order
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — happens-before on a single machine (the JVM memory model)
