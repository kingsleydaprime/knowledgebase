# CRDTs & Conflict Resolution

**[reference]** — from the canon (Shapiro et al. on CRDTs, the Dynamo paper, Automerge/Yjs). When [[architecture/04-distributed-systems/05-replication|multi-leader or leaderless replication]] lets two copies change *the same thing at the same time*, they disagree — and you need a rule to **merge them back together** that never loses data and always lands on the same answer. This is that rule, and its most elegant form (CRDTs).

## The kid version first

Two friends, Ada and Ben, are coloring the **same picture** — but each has their own copy because they're in different rooms. Ada colors the sun yellow; at the exact same moment, Ben colors the sun orange. Later they compare copies. **Now what?**

- **Throw one away?** Someone's work is lost. Sad, and often wrong.
- **Guess who was "later" using a clock?** But their clocks disagree ([[architecture/04-distributed-systems/03-time-and-ordering|clock skew]]), so you might throw away the one that was *actually* newer. Also sad.
- **The clever trick:** design what you're storing so that **merging always works automatically and always gives the same result** — no matter who did what first. Like adding numbers: `2 + 3` and `3 + 2` both give `5`. If your "merge" behaves like addition, the order stops mattering and nothing is lost.

That clever trick is a **CRDT**. Everything below is either "the not-so-clever ways to handle a conflict" or "how to build data that merges like addition."

## First: detect the conflict

You can't resolve a conflict you didn't notice. The tool is [[architecture/04-distributed-systems/03-time-and-ordering|version vectors]] (from the time-and-ordering note): comparing two versions tells you exactly whether one **came after** the other (fine — keep the newer) or whether they were **concurrent** (a real conflict — Ada and Ben coloring at once). A system that skips this and just uses timestamps will *silently overwrite* concurrent writes and never even know.

## The not-so-clever resolutions (and their costs)

- **Last-Write-Wins (LWW)** — keep the copy with the higher timestamp, discard the other. *Kid version:* "whoever's clock says later, wins." Dead simple, and it's what Cassandra does by default — but it **loses data** (Ben's orange is gone) and is **unreliable** because clocks lie. Fine for data where losing a concurrent write is acceptable (a "last seen" timestamp); dangerous for anything you care about.
- **Keep both as "siblings"** — store *both* values and hand them to the application (or the user) to merge. *Kid version:* "keep both drawings, let a person decide." Safe (nothing lost) but pushes the work onto the app, and users hate being asked "which version did you mean?" This is Dynamo's classic approach.
- **Application-specific merge** — write custom code that knows how to combine the two (e.g. union two shopping carts). Works, but you write and test merge logic for every data type, and it's easy to get subtly wrong.

CRDTs are the way to get the *safety* of "keep both" with the *automation* of a merge that's provably correct.

## CRDTs — data that merges like addition

A **CRDT** (Conflict-free Replicated Data Type) is a data structure whose **merge operation is guaranteed to converge** — every replica that has seen the same set of updates ends up **identical**, regardless of the order they arrived, whether some arrived twice, or which replica does the merging.

The math (kid-friendly): merge must be like addition in three ways —
- **Commutative** — order doesn't matter (`a merge b` = `b merge a`), so it's fine that updates arrive in different orders on different replicas.
- **Associative** — grouping doesn't matter, so batching updates any which way is fine.
- **Idempotent** — merging the same thing twice changes nothing, so a message arriving *twice* (which [[architecture/04-distributed-systems/02-theoretical-limits|Two Generals]] says *will* happen) is harmless.

Any operation with these three properties can run on every replica **with zero coordination** and still converge — which is exactly [[architecture/04-distributed-systems/02-theoretical-limits|CALM]] (consistency without coordination requires monotonicity) made concrete. That's why CRDTs are so powerful: **no consensus, no leader, no locking — just merge whenever you reconnect.**

### The catalogue (with kid pictures)
- **G-Counter** (grow-only counter) — *each friend keeps their own tally on their own line; the total is the sum of everyone's lines.* Two friends both counting claps never conflict — you just add their counts. To also allow *decrements*, use a **PN-Counter** (one grow-only counter for +'s, one for −'s, subtract).
- **G-Set / OR-Set** — *a shared sticker album.* A grow-only set (G-Set) merges by **union** — throw everyone's stickers in one pile, done. The hard part is *removing* a sticker while someone else is *adding* it; an **OR-Set** (Observed-Remove Set) tags each add with a unique id so a remove only cancels the specific adds it saw — "add wins" over a concurrent remove.
- **LWW-Register** — a single value with LWW baked in (for one field where last-write-wins is acceptable).
- **Sequence CRDTs** (RGA, Logoot, the ones in **Yjs / Automerge**) — *a shared sentence multiple people type into at once.* They give every character a position that merges without the letters getting jumbled — the engine behind **real-time collaborative editing** (Google-Docs-style) and **local-first** apps.

### Two flavors
- **State-based (CvRDT)** — replicas periodically ship their *whole state* and merge. Robust (tolerates lost/duplicate/reordered messages — merge is idempotent), but sends more data.
- **Operation-based (CmRDT)** — replicas ship individual *operations* ("add sticker X"). Smaller messages, but requires the network to deliver each op once, in [[architecture/04-distributed-systems/03-time-and-ordering|causal]] order.

**Where used:** Redis (CRDT types), Riak, **Automerge / Yjs** (the libraries powering multiplayer editors and offline-first apps like Figma-style collaboration), and increasingly any app that wants to work offline and sync later without a server refereeing every keystroke.

## The catch: CRDTs can't do everything

CRDTs only work for **monotonic** logic — where "adding more information" never has to *take something back*. They handle counters, sets, and collaborative text beautifully. They **cannot** enforce a rule like *"this username can only be claimed by one person"* or *"the account balance must never go below zero"* — those are **non-monotonic** (a later fact can invalidate an earlier one), and by [[architecture/04-distributed-systems/02-theoretical-limits|CALM]] they *require* [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]. So the design rule is: **use CRDTs for everything you can model as monotonic, and pay for consensus only on the genuinely non-monotonic parts.**

## Key insight

**When two copies change the same thing at once, don't guess a winner (you'll lose data) — merge in a way that can't lose data and always lands the same.** First *detect* real conflicts with [[architecture/04-distributed-systems/03-time-and-ordering|version vectors]]; then resolve with LWW (simple, lossy), siblings (safe, annoying), or — best — a **CRDT**, a structure whose merge is commutative + associative + idempotent, so it converges with **no coordination** no matter the order or duplication. CRDTs power collaborative editing and offline-first apps, but only for **monotonic** logic; genuine uniqueness and invariants still need [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]].

## Related
- [[architecture/04-distributed-systems/05-replication|Replication]] — where the conflicts come from (multi-leader / leaderless)
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — version vectors that *detect* concurrency
- [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — CALM: why monotonic data merges coordination-free
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — what non-monotonic invariants (uniqueness, balances) require
