---
id: d1a106e3-bae4-4621-97e3-afced7f06f9e
---

# CRDTs & Conflict Resolution

Conflict resolution is deciding what to do when two people change the same data at the same time on different copies. You see this in Google Docs, where two people type in the same document and both edits survive. A CRDT is a kind of data that can always merge such edits without losing anyone's work, and this lesson shows how.

## The kid version first
<!-- bite: faa641f0-fbd6-490c-baed-35b12b8a7666 -->

Two friends, Ada and Ben, are coloring the **same picture** — but each has their own copy because they're in different rooms. Ada colors the sun yellow; at the exact same moment, Ben colors the sun orange. Later they compare copies. **Now what?**

- **Throw one away?** Someone's work is lost. Sad, and often wrong.
- **Guess who was "later" using a clock?** But their clocks disagree ([[architecture/04-distributed-systems/03-time-and-ordering|clock skew]]), so you might throw away the one that was *actually* newer. Also sad.
- **The clever trick:** design what you're storing so that **merging always works automatically and always gives the same result** — no matter who did what first. Like adding numbers: `2 + 3` and `3 + 2` both give `5`. If your "merge" behaves like addition, the order stops mattering and nothing is lost.

That clever trick is a **CRDT**. Everything below is either "the not-so-clever ways to handle a conflict" or "how to build data that merges like addition."

## First: detect the conflict
<!-- bite: 342681b6-5be4-4e8c-b161-83a966c279f9 -->

You can't resolve a conflict you didn't notice. The tool is [[architecture/04-distributed-systems/03-time-and-ordering|version vectors]] (from the time-and-ordering note): comparing two versions tells you exactly whether one **came after** the other (fine — keep the newer) or whether they were **concurrent** (a real conflict — Ada and Ben coloring at once). A system that skips this and just uses timestamps will *silently overwrite* concurrent writes and never even know.

## The not-so-clever resolutions (and their costs)
<!-- bite: 8f260e0b-e978-4dd4-a31d-1ecb8b9c0440 -->

- **Last-Write-Wins (LWW)** — keep the copy with the higher timestamp, discard the other. *Kid version:* "whoever's clock says later, wins." Dead simple, and it's what Cassandra does by default — but it **loses data** (Ben's orange is gone) and is **unreliable** because clocks lie. Fine for data where losing a concurrent write is acceptable (a "last seen" timestamp); dangerous for anything you care about.
- **Keep both as "siblings"** — store *both* values and hand them to the application (or the user) to merge. *Kid version:* "keep both drawings, let a person decide." Safe (nothing lost) but pushes the work onto the app, and users hate being asked "which version did you mean?" This is Dynamo's classic approach.
- **Application-specific merge** — write custom code that knows how to combine the two (e.g. union two shopping carts). Works, but you write and test merge logic for every data type, and it's easy to get subtly wrong.

CRDTs are the way to get the *safety* of "keep both" with the *automation* of a merge that's provably correct.

## CRDTs — data that merges like addition
<!-- bite: f782467b-7168-4b5b-b87c-03244d4d257f -->

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
<!-- bite: a0c98fa1-f037-41bf-ba9a-4098b1fedd56 -->

CRDTs only work for **monotonic** logic — where "adding more information" never has to *take something back*. They handle counters, sets, and collaborative text beautifully. They **cannot** enforce a rule like *"this username can only be claimed by one person"* or *"the account balance must never go below zero"* — those are **non-monotonic** (a later fact can invalidate an earlier one), and by [[architecture/04-distributed-systems/02-theoretical-limits|CALM]] they *require* [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]]. So the design rule is: **use CRDTs for everything you can model as monotonic, and pay for consensus only on the genuinely non-monotonic parts.**

## Key insight
<!-- bite: 230e1771-2efd-4a33-a9bc-81c776e11c9a -->

**When two copies change the same thing at once, don't guess a winner (you'll lose data) — merge in a way that can't lose data and always lands the same.** First *detect* real conflicts with [[architecture/04-distributed-systems/03-time-and-ordering|version vectors]]; then resolve with LWW (simple, lossy), siblings (safe, annoying), or — best — a **CRDT**, a structure whose merge is commutative + associative + idempotent, so it converges with **no coordination** no matter the order or duplication. CRDTs power collaborative editing and offline-first apps, but only for **monotonic** logic; genuine uniqueness and invariants still need [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]].

## Check your understanding
<!-- bite: ed358913-2b38-42bb-a2d7-b40fcdc7bc81 -->

Try each one before you open the answer.

1. <!-- q: mcq id="172e856b" -->
   Before resolving a conflict you must detect it. Which tool tells you whether two versions were concurrent or one came after the other?

   - [ ] Wall-clock timestamps
   - [x] Version vectors
   - [ ] A checksum of the value
   - [ ] The replica's IP address

   <details><summary>Answer</summary>

   Version vectors. Timestamps alone silently overwrite concurrent writes and never notice the conflict.

   </details>

2. <!-- q: mcq id="e66390a9" -->
   Two replicas hold different values for the same key. Last-write-wins keeps the one with the higher timestamp. What are its problems? Choose all that apply.

   - [x] The other concurrent write is thrown away
   - [x] Clock skew can make it keep the older write
   - [ ] It needs consensus on every write
   - [ ] It can never converge

   <details><summary>Answer</summary>

   LWW is simple but loses data, and since clocks disagree, the "later" timestamp may not be the later write. It suits things like a "last seen" time.

   </details>

3. <!-- q: gap id="8318bb1e" answers="commutative;associative;idempotent" -->
   Fill in the gaps. A CRDT merge always converges because it is ___ (order does not matter), ___ (grouping does not matter) and ___ (merging the same thing twice changes nothing).

   <details><summary>Answer</summary>

   Commutative, associative and idempotent. Together they let replicas merge in any order, with duplicates, and still agree.

   </details>

4. <!-- q: mcq id="31125c6b" -->
   Which rule can a CRDT NOT enforce on its own?

   - [ ] Count the total number of likes
   - [ ] Keep a shared set of tags
   - [x] Each username can be claimed by only one person
   - [ ] Merge text typed by two people at once

   <details><summary>Answer</summary>

   Unique usernames are non-monotonic: a later claim can invalidate an earlier one. By CALM that needs coordination (consensus), not a CRDT.

   </details>

5. <!-- q: mcq id="e70b7011" -->
   What is the difference between a state-based and an operation-based CRDT?

   - [x] State-based ships the whole state and tolerates lost or duplicate messages; operation-based ships each operation and needs each delivered once, in causal order
   - [ ] State-based needs a leader; operation-based does not
   - [ ] They are two names for the same thing
   - [ ] Operation-based sends more data

   <details><summary>Answer</summary>

   State-based is robust but sends more data. Operation-based sends small messages but asks more of the network.

   </details>

6. <!-- q: open id="b435be9d" -->
   How does an OR-Set handle one person removing an item while another person adds it at the same time?

   <details><summary>Answer</summary>

   Every add is tagged with a unique id. A remove only cancels the specific add ids it has seen. A concurrent add has a new id the remover never saw, so it survives: add wins.

   </details>

## Check your understanding: worked problems
<!-- bite: ab2be4ee-4966-4090-9e37-2bcd3212f45b -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="4f3b1052" answers="5;4;1;10" -->
   Fill in the gaps. A G-Counter keeps one count per node, merges by taking the maximum of each node's entry, and its value is the sum. Two replicas hold:

   | Replica | A | B | C |
   |---|---|---|---|
   | R1 | 5 | 2 | 0 |
   | R2 | 3 | 4 | 1 |

   After merging, A = ___, B = ___, C = ___, and the counter's value is ___.

   <details><summary>Answer</summary>

   Max per entry: A = 5, B = 4, C = 1. The value is 5 + 4 + 1 = 10. Adding the two totals (7 + 8) would double-count.

   </details>

2. <!-- q: exact id="ae61e3fe" answer="4" -->
   A PN-Counter keeps one grow-only counter for increments (P) and one for decrements (N). The value is sum(P) − sum(N). P = {A: 7, B: 3} and N = {A: 2, B: 4}. What is the value?

   <details><summary>Answer</summary>

   (7 + 3) − (2 + 4) = 10 − 6 = 4.

   </details>

3. <!-- q: exact id="9831337e" answer="4" -->
   A G-Set merges by union. Replica 1 holds {a, b, c} and replica 2 holds {b, d}. How many items are in the merged set?

   <details><summary>Answer</summary>

   {a, b, c, d}: 4 items. The shared item b appears once.

   </details>

## Related
<!-- bite: 1caa3999-c25a-4f75-aeba-7643c674c496 -->
- [[architecture/04-distributed-systems/05-replication|Replication]] — where the conflicts come from (multi-leader / leaderless)
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — version vectors that *detect* concurrency
- [[architecture/04-distributed-systems/02-theoretical-limits|Theoretical Limits]] — CALM: why monotonic data merges coordination-free
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — what non-monotonic invariants (uniqueness, balances) require

## About this lesson
<!-- bite: 0f7d03f8-bee6-449c-8888-743075f14ded -->

**Level:** reference. **Covers:** from the canon (Shapiro et al. on CRDTs, the Dynamo paper, Automerge/Yjs). When [[architecture/04-distributed-systems/05-replication|multi-leader or leaderless replication]] lets two copies change *the same thing at the same time*, they disagree — and you need a rule to **merge them back together** that never loses data and always lands on the same answer. This is that rule, and its most elegant form (CRDTs).
