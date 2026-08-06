# Time & Ordering

**[reference]** — from the canon (Lamport's "Time, Clocks, and the Ordering of Events in a Distributed System," 1978 — one of the most cited papers in CS; DDIA ch. 8–9). How to reason about "what happened before what" when there's [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|no global clock]]. This is the conceptual bedrock under [[architecture/04-distributed-systems/04-consistency-models|consistency models]], [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|conflict resolution]], and [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]].

## The kid version first

You and a friend are in **different rooms**, and you both shout **"I got here first!"** How do you settle it? You *can't* use your watches — they disagree by a little, so your watch might say 3:00:01 while the "later" event shows 3:00:00 on the other watch. Clocks are liars here.

But there's one thing you *can* always trust: **cause and effect.** If your friend **shouted back an answer to your question**, then your question *must* have come first — because they couldn't answer something they hadn't heard yet. So instead of asking *"what time was it?"* (unanswerable), you ask *"did this cause that?"* (always answerable). This whole note is about ordering events by **who-could-have-heard-whom**, using **counters** passed along with messages instead of clocks on the wall.

## Why ordering is the whole game

Distributed systems constantly need to know the order of events: which write is newer, did this read happen before that write, which of two concurrent updates wins. On one machine, a lock or a single clock gives you order for free. Across machines — clocks disagree, messages arrive out of order — establishing order is genuinely hard, and getting it wrong *loses data* (a stale write silently overwrites a fresh one). Lamport's reframing is the key move: **stop asking "when did this happen?" and start asking "in what causal order?"**

## The trap: physical timestamps can't order cross-node events

Recall from [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|the models]]: wall-clock time can jump backward and drifts between nodes; monotonic clocks don't drift but are incomparable across nodes. So the tempting **"last write wins by timestamp"** silently corrupts data:

```
Node A clock is 50ms AHEAD of Node B.
  t=100 (A's clock)  A writes  x = "cat"     → timestamp 100
  t=60  (B's clock)  B writes  x = "dog"     → timestamp 60   (LATER in real time!)
LWW keeps the higher timestamp → "cat" wins → B's newer write is LOST.
```

The write that actually happened later got the *lower* timestamp because B's clock lagged. Clock skew makes physical-timestamp ordering fundamentally unreliable — which is why we need **logical** order instead.

## Happens-before (→) — causal order without clocks

Lamport's definition of the only ordering you can actually establish. Event **A happens-before B** (written `A → B`) if any of:
1. **Same node, A first** — A occurred before B in the same process.
2. **Message** — A is a `send` and B is the matching `receive`.
3. **Transitivity** — `A → C` and `C → B` imply `A → B`.

If **neither `A → B` nor `B → A`**, the events are **concurrent** (`A ∥ B`) — there is *genuinely no order* between them, and pretending there is one is the bug. Happens-before is a **partial order**: it captures causality (X *could have influenced* Y) and deliberately leaves unrelated events unordered. Everything below is machinery to *track* this relation with counters.

## Lamport clocks — a total order consistent with causality

Each node keeps one integer counter `C`:
- **Local event:** `C = C + 1`.
- **Send:** `C = C + 1`, then attach `C` to the message.
- **Receive(msg):** `C = max(C, msg.C) + 1`.

**Worked trace** (P1, P2, P3; `e:C` = event with its Lamport value):

```
P1:  a:1 ── b:2 ──────────────► (send m to P2 at b)
                    \
P2:        c:1 ──────► d:3 (recv m: max(1,2)+1) ── e:4 ──► (send n to P3)
                                                        \
P3:  f:1 ── g:2 ──────────────────────────────────────────► h:5 (recv n: max(2,4)+1)
```

The guarantee: **if `A → B` then `Lamport(A) < Lamport(B)`.** Break ties with node ID and you get a **total order** — every event gets a distinct, causality-respecting rank. That total order is exactly what **total-order broadcast** and Lamport's mutual-exclusion algorithm are built on, and it's a stepping stone to [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]].

**The one thing Lamport clocks can't do:** the converse fails. `Lamport(A) < Lamport(B)` does **not** imply `A → B` — they might be concurrent (in the trace, `g:2` on P3 and `d:3` on P2 are concurrent, yet `2 < 3`). Lamport clocks can *impose* an order but can't *detect* whether two events were truly causal or merely concurrent. When you need that distinction, go to vector clocks.

## Vector clocks — detecting concurrency exactly

Each node keeps a **vector** `V` of counters, one entry per node. Node `i`:
- **Local event / send:** `V[i] = V[i] + 1`; attach the whole vector to sends.
- **Receive(msg):** `V[k] = max(V[k], msg.V[k])` for every `k`, then `V[i] = V[i] + 1`.

Compare two vectors elementwise:
- `Va ≤ Vb` on **every** entry (and `≠`) → **`A → B`** (A causally precedes B).
- `Vb ≤ Va` → **`B → A`**.
- **Neither dominates** (each is bigger in some entry) → **`A ∥ B`, concurrent** → a genuine conflict.

**Worked example** — two clients write the same key through a Dynamo-style store:

```
start:  V = [0,0,0]  (nodes A,B,C)
A writes:  [1,0,0]   "cat"
B writes:  [0,1,0]   "dog"      ← [1,0,0] vs [0,1,0]: neither dominates → CONCURRENT
                                  the store keeps BOTH (siblings), surfaces the conflict
client reads both, resolves to "cat-dog", writes with merged clock [1,1,0]
later A writes:            [2,1,0]   → [2,1,0] ≥ [1,1,0] → descends it, no conflict
```

This is precisely how [[architecture/04-distributed-systems/05-replication|leaderless (Dynamo) replication]] avoids silently losing a write: it *detects* the concurrent pair and either keeps both as **siblings** for the app to merge, or feeds them to a [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDT]] that merges deterministically. The cost is size: the vector grows with the number of writers, so systems bound it (per-replica, not per-client; prune old entries) — **dotted version vectors** are a refinement that keeps them compact.

## Hybrid Logical Clocks (HLC) — the practical middle

Logical clocks give correct causality but their numbers mean nothing to a human ("event 4,182" — when was that?). Physical clocks are human-meaningful but unsafe for ordering. **HLC** (used by CockroachDB, MongoDB) fuses them: each timestamp is `(physical_time, logical_counter)`. It tracks causality like a logical clock (bumping the counter on causally-later events) **while staying within a small bound of real wall-clock time** — so timestamps are both causally correct *and* roughly interpretable as "when," and they're monotonic even across NTP jumps. HLC is the pragmatic default when you want causal ordering *and* timestamps that mean something.

## TrueTime — buying certainty with hardware

Google's Spanner takes the opposite bet: instead of avoiding physical clocks, **make them trustworthy enough to order by.** **TrueTime** equips every datacenter with **GPS receivers and atomic clocks**, and the API returns not a timestamp but an **interval** `[earliest, latest]` with a *guaranteed bound* on the uncertainty (typically a few milliseconds). To commit a transaction at time `T`, Spanner **waits out the uncertainty** — it deliberately pauses until `T` is definitely in the past everywhere (`now.earliest > T`), so no other transaction can be assigned an overlapping timestamp. This "commit wait" is how Spanner offers **externally-consistent (linearizable) global transactions** ([[architecture/04-distributed-systems/11-modern-distributed-transactions|modern transactions]]) — it trades a few ms of latency for a globally meaningful order. The lesson: you *can* order by physical time, but only if you pay to bound the uncertainty and then wait it out; almost everyone else uses logical/hybrid clocks because that's free.

## Why this feeds everything else

- **[[architecture/04-distributed-systems/04-consistency-models|Consistency models]]** are *defined* in terms of which orderings are guaranteed — **causal consistency** literally means "respects happens-before," no more, no less.
- **[[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|Conflict resolution]]** uses version vectors to know *which* writes actually conflict (concurrent) vs which supersede.
- **[[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]]** is, in large part, machinery to impose a single agreed **total order** on operations despite all of the above — a replicated log is a totally-ordered sequence of commands.

## Key insight

**"When" is the wrong question across machines — "in what causal order" is the right one, and you answer it with counters and message-passing, not clocks.** Lamport clocks give a total order consistent with causality but can't detect concurrency; **vector clocks** detect it exactly (and power conflict detection in leaderless replication); **HLC** makes logical order human-readable; **TrueTime** is the expensive exception that makes physical time trustworthy by bounding and waiting out its error. Master happens-before and the rest of the course — consistency, conflict resolution, consensus — stops being mysterious.

## Related
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — orderings-as-guarantees; causal consistency = happens-before
- [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs & Conflict Resolution]] — version vectors deciding what conflicts
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — imposing a single total order (the replicated log)
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency (Java)]] — happens-before on a single machine (the JVM memory model)
