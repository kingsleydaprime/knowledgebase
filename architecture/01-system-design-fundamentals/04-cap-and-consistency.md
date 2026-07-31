# CAP & Consistency

**[reference]** — from the roadmap.sh system-design roadmap. The theorem every system-design discussion invokes (often wrongly), and the consistency spectrum underneath it. The bridge from system-design fundamentals into [[architecture/04-distributed-systems/README|distributed systems]].

## The CAP theorem

For any distributed data store, when a **network partition** happens (nodes can't talk to each other — which *will* happen), you can guarantee at most **two** of:

- **Consistency (C)** — every read sees the most recent write (all nodes agree).
- **Availability (A)** — every request gets a (non-error) response.
- **Partition tolerance (P)** — the system keeps working despite dropped/delayed messages between nodes.

## Reading CAP correctly (most people get this wrong)

The popular "pick 2 of 3" framing is misleading. In a real distributed system, **partitions are not optional** — networks fail, so you *must* tolerate P. That means the real choice, **during a partition**, is between **C and A**:

- **CP** — when nodes can't agree, refuse to serve (return errors) rather than risk returning stale/conflicting data. Choose when correctness is non-negotiable (a bank balance, inventory). Example: a system that rejects writes if it can't reach a quorum.
- **AP** — keep serving on both sides of the partition, accepting that they may temporarily diverge and reconcile later. Choose when being up matters more than being perfectly current (social feeds, shopping carts, DNS).

**When there's *no* partition, you get both C and A** — CAP only forces the choice during the failure. So the honest statement is: "*during a network partition*, do you sacrifice consistency or availability?"

## The consistency spectrum

"Consistency" isn't binary — it's a spectrum of guarantees, from strongest (and most expensive) to weakest (and most available). This is the more useful lens than CAP:

- **Strong / linearizable** — every read sees the latest write, as if there were one copy. Simplest to reason about, most expensive (needs coordination — a [[architecture/04-distributed-systems/04-consensus|consensus]]/quorum round-trip), limits availability and adds latency.
- **Sequential / causal** — weaker but preserves useful orderings (e.g. causally-related events are seen in order — you never see a reply before the message it answers). A pragmatic middle ground.
- **Eventual consistency** — if writes stop, all replicas *eventually* converge; in the meantime, reads may be stale. Cheap, highly available, low latency — the default for AP systems. The cost: your application must tolerate (and sometimes resolve) stale/conflicting reads.

## Choosing, in practice

The design question is always "**how consistent does *this data* need to be?**" — and the answer differs *per feature within one system*:

- A **like count** can be eventually consistent (briefly wrong is fine) → favor availability.
- An **account balance** or **inventory decrement** needs strong consistency (double-spend is unacceptable) → favor consistency, pay the coordination cost.

Mature systems mix models: strong consistency for the money, eventual for the feed. The instinct to build — *from the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|requirements]], decide the weakest consistency each piece of data can tolerate, because weaker is cheaper and more available* — is exactly the senior judgment CAP is really about. The mechanisms that implement these guarantees (quorums, replication, consensus, conflict resolution/CRDTs) are the subject of [[architecture/04-distributed-systems/03-replication-and-consistency|distributed systems]].

## Related
- [[architecture/04-distributed-systems/03-replication-and-consistency|Replication & Consistency]] — how these guarantees are actually implemented
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability & Reliability]] — the A in CAP
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — where you pick a database's consistency model
