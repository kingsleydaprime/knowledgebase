# Consistency Models

**[reference]** — from the canon (DDIA ch. 9, Herlihy & Wing on linearizability, Jepsen's consistency map). A **consistency model** is the *promise* a storage system makes about what a read is allowed to return. [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]] said you *must* pick a point on a spectrum; this note is the spectrum, from strongest to weakest.

## The kid version first

Imagine a group of friends keeping score in a game. Instead of one shared scoreboard, **each friend has their own little notebook** and they shout updates to each other ("+1 for the red team!"). Copying data across machines is exactly this: many notebooks that are *supposed* to say the same thing but take a moment to catch up.

A **consistency model** answers one question: *when you glance at a notebook, what are you allowed to see?*
- The **strictest** promise: every notebook always shows the exact latest score, as if there were really only **one** shared scoreboard. Nice to think about — but keeping all the notebooks perfectly in lockstep is slow, because everyone has to check with everyone before writing.
- The **loosest** promise: your notebook will *eventually* match everyone else's… but right now it might be a little behind. Fast and always available, but you might see an old score.

Everything below is just naming the points *between* "always perfectly in sync" and "eventually in sync," because that choice is the single biggest decision in a distributed system.

## Why there's a spectrum at all

From [[architecture/04-distributed-systems/02-theoretical-limits|the limits]]: a strong promise ("you always see the latest") requires **coordination** — the notebooks must talk to each other *before* answering, which costs time and fails if they can't reach each other. A weak promise ("you'll see it eventually") needs *no* coordination — answer from your own notebook instantly. So **the strength of the promise = how much coordination = how slow and how fragile-under-partition.** Picking a model is picking how much you're willing to pay for how fresh a read.

Two big families, then the ladder:

- **Strong consistency** — behaves like a single copy; you reason about it as if the distribution weren't there. Expensive.
- **Weak / eventual consistency** — copies can disagree for a while; you (the app) must cope with staleness and conflicts. Cheap and available.

## The ladder, strongest → weakest

### Linearizability (the gold standard)
**Kid version:** it's as if there's only **one** scoreboard that everyone shares. The instant someone writes, the very next person to look sees it — no exceptions.

**Precise:** every operation appears to take effect **instantaneously at some single point** between when it started and when it finished, and that single order **respects real time** — if write A finished before read B started (by the wall clock), B *must* see A. This is the "recency" guarantee: a read always returns the *latest completed* write.

- **Cost:** requires [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]/quorum coordination on operations, so it's the slowest and, under a partition, the *unavailable* choice ([[architecture/04-distributed-systems/02-theoretical-limits|CP in CAP]]).
- **Where:** etcd, ZooKeeper, a single-leader SQL primary's reads, Spanner.
- **Note:** linearizability is about **one object at a time** (one key, one register). Making *multiple* objects change together atomically is a *transaction* isolation question — see below.

### Sequential consistency
**Kid version:** everyone watches the *same replay of the game in the same order* — but some friends started watching a bit later. They all agree on the order of goals; they just might be at different points.

**Precise:** all nodes see all operations in **one agreed total order**, and each client's own operations keep their order — **but** that order need not match real time. So a write can be "seen" by others a little after it really happened, as long as *everyone* sees the same sequence. Strictly weaker than linearizable (drops the real-time tie).

### Causal consistency
**Kid version:** you'll always see a **question before its answer** — anything that *caused* something else shows up first. But two unrelated things (two different friends' unrelated comments) might show up in different orders for different people, and that's fine.

**Precise:** operations related by [[architecture/04-distributed-systems/03-time-and-ordering|happens-before]] are seen in that order by everyone; **concurrent** operations may be seen in different orders on different nodes. This is the **strongest model you can have while staying available under partition** ([[architecture/04-distributed-systems/02-theoretical-limits|CALM]]/COPS result) — the sweet spot for many AP systems, because it kills the most confusing anomalies (you never see a reply before its message) without paying for full coordination.

### Eventual consistency
**Kid version:** like a rumor spreading through the playground. For a while, different kids have heard different versions — but if everyone stops adding to it, **eventually** everyone ends up with the same story.

**Precise:** *if writes stop, all replicas eventually converge to the same value.* That's the **only** promise — no ordering, no recency. Until convergence, reads can be stale, out of order, or flip-flop. Cheapest, most available, most anomalies for the app to handle. Cassandra/Dynamo default.

## Session guarantees — the practical middle most apps actually want

Full linearizability is often overkill, but raw eventual consistency is *surprising* (you edit your profile, refresh, and your change is gone). **Session guarantees** are cheap, per-user promises that remove the *jarring* anomalies without global coordination:

- **Read-your-writes** — after *you* write something, *you* always see it (even if other people don't yet). *"I posted a comment, so I should see my own comment."*
- **Monotonic reads** — you never see time go **backwards**: once you've seen a value, you won't later see an older one. *"The score was 5; it shouldn't show 3 on my next refresh."*
- **Monotonic writes** — your own writes are applied in the order you made them.
- **Writes-follow-reads** — if you reply to something you read, your reply appears *after* the thing it replied to, for everyone.

These are usually implemented by pinning a user to a replica or tracking a little version token — far cheaper than linearizability, and they cover the anomalies users actually notice.

## Consistency ≠ isolation (the classic confusion)

Two different words that both sound like "correctness":
- **Consistency (this note)** = recency/ordering of reads on a **single object**. Its strongest form is *linearizability*.
- **Isolation** ([[architecture/04-distributed-systems/10-distributed-transactions|transactions]]) = how concurrent **multi-object transactions** interleave. Its strongest form is *serializability*.

They're **orthogonal** — a system can be linearizable but not serializable, or vice-versa. **"Strict serializability"** is the combination of both (serializable *and* respecting real-time order), which is what Spanner offers and what most people picture when they say "strong consistency." Keeping the two ideas separate saves you endless confusion.

## Key insight

**A consistency model is a promise about what a read may return, and its strength is exactly its price.** Linearizable = "as if one shared scoreboard" (freshest, slowest, unavailable under partition); sequential = "same replay, different start times"; **causal = "cause before effect" (the strongest you can keep while staying available)**; eventual = "the rumor eventually settles" (cheapest, most anomalies). Most real apps don't need the top of the ladder — they need cheap **session guarantees** (see your own writes, never go backwards) that kill the anomalies users *notice*. And don't confuse single-object **consistency** with multi-object transaction **isolation** — "strict serializability" is both at once.

## Related
- [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — why strength costs coordination (PACELC), and CALM
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — happens-before, which *defines* causal consistency
- [[architecture/04-distributed-systems/05-replication|Replication]] — the mechanism that produces (and must uphold) these promises
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — isolation, the transaction cousin of consistency
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals-level view
