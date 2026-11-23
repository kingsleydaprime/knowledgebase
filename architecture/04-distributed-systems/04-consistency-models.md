---
id: a3e376e0-ebfd-4411-b5a5-7497c28fda73
---

# Consistency Models

A consistency model is a rule about what you are allowed to see when you read data that is copied across many computers.

## What a consistency model is
<!-- bite: a4eaf14f-108f-46fc-80e4-3042999f5a62 -->

A consistency model is a rule about what a read may show when data is copied across computers.

Sometimes you post a comment and it doesn't show up on your other device for a moment. This lesson walks through the different rules, from strict to relaxed, and what each one costs.

## The kid version first
<!-- bite: bbb4a49f-a96e-4929-899b-856b223b7fb8 -->

Imagine a group of friends keeping score in a game. Instead of one shared scoreboard, **each friend has their own little notebook** and they shout updates to each other ("+1 for the red team!"). Copying data across machines is exactly this: many notebooks that are *supposed* to say the same thing but take a moment to catch up.

## The kid version: strict and loose promises
<!-- bite: fdde4a44-7a67-4542-87d7-01152cb46a65 -->

The notebooks story leads to one question, with a strict answer and a loose one.

A **consistency model** answers one question: *when you glance at a notebook, what are you allowed to see?*
- The **strictest** promise: every notebook always shows the exact latest score, as if there were really only **one** shared scoreboard. Nice to think about — but keeping all the notebooks perfectly in lockstep is slow, because everyone has to check with everyone before writing.
- The **loosest** promise: your notebook will *eventually* match everyone else's… but right now it might be a little behind. Fast and always available, but you might see an old score.

Everything below is just naming the points *between* "always perfectly in sync" and "eventually in sync," because that choice is the single biggest decision in a distributed system.

## Why there's a spectrum at all
<!-- bite: 501d812f-9f39-4635-a40c-b9618a5f8fd5 -->

From [[architecture/04-distributed-systems/02-theoretical-limits|the limits]]: a strong promise ("you always see the latest") requires **coordination** — the notebooks must talk to each other *before* answering, which costs time and fails if they can't reach each other. A weak promise ("you'll see it eventually") needs *no* coordination — answer from your own notebook instantly. So **the strength of the promise = how much coordination = how slow and how fragile-under-partition.** Picking a model is picking how much you're willing to pay for how fresh a read.

Two big families, then the ladder:

- **Strong consistency** — behaves like a single copy; you reason about it as if the distribution weren't there. Expensive.
- **Weak / eventual consistency** — copies can disagree for a while; you (the app) must cope with staleness and conflicts. Cheap and available.

## The ladder, strongest → weakest
<!-- bite: 4f021e1c-8ab5-4f57-92e1-50f51efa5028 -->

### Linearizability (the gold standard)
**Kid version:** it's as if there's only **one** scoreboard that everyone shares. The instant someone writes, the very next person to look sees it — no exceptions.

**Precise:** every operation appears to take effect **instantaneously at some single point** between when it started and when it finished, and that single order **respects real time** — if write A finished before read B started (by the wall clock), B *must* see A. This is the "recency" guarantee: a read always returns the *latest completed* write.

- **Cost:** requires [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]/quorum coordination on operations, so it's the slowest and, under a partition, the *unavailable* choice ([[architecture/04-distributed-systems/02-theoretical-limits|CP in CAP]]).
- **Where:** etcd, ZooKeeper, a single-leader SQL primary's reads, Spanner.
- **Note:** linearizability is about **one object at a time** (one key, one register). Making *multiple* objects change together atomically is a *transaction* isolation question — see below.

## The ladder: sequential consistency
<!-- bite: 4b459f7e-854b-4b27-ba92-470c404088fd -->

One step down the ladder, everyone sees the same order, but maybe late.

**Kid version:** everyone watches the *same replay of the game in the same order* — but some friends started watching a bit later. They all agree on the order of goals; they just might be at different points.

**Precise:** all nodes see all operations in **one agreed total order**, and each client's own operations keep their order — **but** that order need not match real time. So a write can be "seen" by others a little after it really happened, as long as *everyone* sees the same sequence. Strictly weaker than linearizable (drops the real-time tie).

## The ladder: causal consistency
<!-- bite: e2ffb481-34cb-4ce1-8968-f9c233af0a03 -->

Next down, only things linked by cause and effect must appear in order.

**Kid version:** you'll always see a **question before its answer** — anything that *caused* something else shows up first. But two unrelated things (two different friends' unrelated comments) might show up in different orders for different people, and that's fine.

**Precise:** operations related by [[architecture/04-distributed-systems/03-time-and-ordering|happens-before]] are seen in that order by everyone; **concurrent** operations may be seen in different orders on different nodes. This is the **strongest model you can have while staying available under partition** ([[architecture/04-distributed-systems/02-theoretical-limits|CALM]]/COPS result) — the sweet spot for many AP systems, because it kills the most confusing anomalies (you never see a reply before its message) without paying for full coordination.

## The ladder: eventual consistency
<!-- bite: 2a638338-f86d-4f78-8786-d21667eeebca -->

At the bottom of the ladder, copies only promise to agree in the end.

**Kid version:** like a rumor spreading through the playground. For a while, different kids have heard different versions — but if everyone stops adding to it, **eventually** everyone ends up with the same story.

**Precise:** *if writes stop, all replicas eventually converge to the same value.* That's the **only** promise — no ordering, no recency. Until convergence, reads can be stale, out of order, or flip-flop. Cheapest, most available, most anomalies for the app to handle. Cassandra/Dynamo default.

## Session guarantees — the practical middle most apps actually want
<!-- bite: 4ed945a7-e761-432a-af94-847f95f8d59e -->

Full linearizability is often overkill, but raw eventual consistency is *surprising* (you edit your profile, refresh, and your change is gone). **Session guarantees** are cheap, per-user promises that remove the *jarring* anomalies without global coordination:

- **Read-your-writes** — after *you* write something, *you* always see it (even if other people don't yet). *"I posted a comment, so I should see my own comment."*
- **Monotonic reads** — you never see time go **backwards**: once you've seen a value, you won't later see an older one. *"The score was 5; it shouldn't show 3 on my next refresh."*
- **Monotonic writes** — your own writes are applied in the order you made them.
- **Writes-follow-reads** — if you reply to something you read, your reply appears *after* the thing it replied to, for everyone.

These are usually implemented by pinning a user to a replica or tracking a little version token — far cheaper than linearizability, and they cover the anomalies users actually notice.

## Seeing read-your-writes break
<!-- bite: 2c56e42e-977a-4c02-8356-23310fe59faa -->

Time runs to the right. Your save reaches the leader at once, but the grey copy takes a while to reach the follower. Your first read lands on the follower before the copy does, so you see your old bio, which is exactly the anomaly read-your-writes rules out.

![Replication lag breaking read-your-writes: you save a new bio on the leader; the copy to the follower lags; your first read, sent to the follower too early, returns the old bio; a later read, after the copy arrives, returns the new bio. The fix is to read from the leader for a moment after writing.](../images/sd-read-your-writes.svg)

## Consistency ≠ isolation (the classic confusion)
<!-- bite: 289eab68-6fdc-40fc-80e6-c4673fc9833b -->

Two different words that both sound like "correctness":
- **Consistency (this note)** = recency/ordering of reads on a **single object**. Its strongest form is *linearizability*.
- **Isolation** ([[architecture/04-distributed-systems/10-distributed-transactions|transactions]]) = how concurrent **multi-object transactions** interleave. Its strongest form is *serializability*.

They're **orthogonal** — a system can be linearizable but not serializable, or vice-versa. **"Strict serializability"** is the combination of both (serializable *and* respecting real-time order), which is what Spanner offers and what most people picture when they say "strong consistency." Keeping the two ideas separate saves you endless confusion.

## Key insight
<!-- bite: a5f69d5e-184f-4c5e-b136-c77aa7c5e72f -->

**A consistency model is a promise about what a read may return, and its strength is exactly its price.** Linearizable = "as if one shared scoreboard" (freshest, slowest, unavailable under partition); sequential = "same replay, different start times"; **causal = "cause before effect" (the strongest you can keep while staying available)**; eventual = "the rumor eventually settles" (cheapest, most anomalies). Most real apps don't need the top of the ladder — they need cheap **session guarantees** (see your own writes, never go backwards) that kill the anomalies users *notice*. And don't confuse single-object **consistency** with multi-object transaction **isolation** — "strict serializability" is both at once.

## Check your understanding
<!-- bite: 1671b0eb-bd32-4c32-8b20-4822d20283f2 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c634f11b" -->
   Put these consistency models in order from strongest to weakest.

   - [ ] Eventual, causal, sequential, linearizable
   - [x] Linearizable, sequential, causal, eventual
   - [ ] Sequential, linearizable, eventual, causal
   - [ ] Causal, linearizable, sequential, eventual

   <details><summary>Answer</summary>

   Linearizable, then sequential (drops the real-time rule), then causal (only cause-and-effect is ordered), then eventual (only promises convergence once writes stop).

   </details>

2. <!-- q: mcq id="3906ea38" -->
   Write W finishes at 10:00:01. Read R starts at 10:00:02 on another node and returns the old value. Which model does this break, even though sequential consistency could allow it?

   - [x] Linearizability
   - [ ] Causal consistency
   - [ ] Eventual consistency

   <details><summary>Answer</summary>

   Linearizability ties the order to real time: if a write finished before a read started, the read must see it. Sequential consistency drops that real-time rule.

   </details>

3. <!-- q: exact id="703d0213" answer="causal" accept="causal consistency" -->
   Which consistency model is the strongest one a system can keep while staying available during a network partition?

   <details><summary>Answer</summary>

   Causal consistency. It keeps cause before effect (you never see a reply before its message) without full coordination.

   </details>

4. <!-- q: mcq id="f02bf4ef" -->
   A user saw a score of 5, refreshed, and now sees 3. Which session guarantee was broken?

   - [ ] Read-your-writes
   - [x] Monotonic reads
   - [ ] Monotonic writes
   - [ ] Writes-follow-reads

   <details><summary>Answer</summary>

   Monotonic reads promises time never goes backwards for you: once you see a value, you never see an older one.

   </details>

5. <!-- q: gap id="855cdd9d" answers="linearizability|linearizable;serializability|serializable" -->
   Fill in the gaps. The strongest form of single-object consistency is ___. The strongest form of multi-object transaction isolation is ___. Having both together is called strict serializability.

   <details><summary>Answer</summary>

   Linearizability for one object, serializability for transactions. They are separate ideas; Spanner offers both.

   </details>

6. <!-- q: open id="88d86324" -->
   Why do most apps use session guarantees instead of full linearizability?

   <details><summary>Answer</summary>

   Linearizability needs coordination on every operation, so it is slow and unavailable during a partition. Session guarantees such as read-your-writes and monotonic reads are cheap per-user promises (pin a user to a replica or carry a version token) that remove the anomalies users actually notice.

   </details>

## Related
<!-- bite: c3d646f3-1164-4f87-8a9b-dc086152662a -->
- [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — why strength costs coordination (PACELC), and CALM
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — happens-before, which *defines* causal consistency
- [[architecture/04-distributed-systems/05-replication|Replication]] — the mechanism that produces (and must uphold) these promises
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — isolation, the transaction cousin of consistency
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals-level view

## About this lesson
<!-- bite: 2ae27688-d81f-4965-b857-bd8949570eab -->

**Level:** reference. **Covers:** from the canon (DDIA ch. 9, Herlihy & Wing on linearizability, Jepsen's consistency map). A **consistency model** is the *promise* a storage system makes about what a read is allowed to return. [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]] said you *must* pick a point on a spectrum; this note is the spectrum, from strongest to weakest.
