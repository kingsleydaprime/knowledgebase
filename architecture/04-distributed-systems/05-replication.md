# Replication

**[reference]** — from the canon (DDIA ch. 5, the Dynamo paper). Keeping multiple copies of the same data on multiple machines — the *mechanism* underneath availability, read-scaling, and the [[architecture/04-distributed-systems/04-consistency-models|consistency]] promises. This note is *how you keep copies*; [[architecture/04-distributed-systems/04-consistency-models|consistency models]] is *what you promise readers*, and [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|conflict resolution]] is *what to do when copies disagree*.

## The kid version first

You have a favorite notebook. You make **three copies** and keep them in three different rooms. Why bother?
- **If one is lost** (juice spilled on it), you still have the others → **survives failure**.
- **A friend in another room** can read the nearby copy instead of walking to yours → **faster reads, closer to people**.
- **Lots of friends can read at once** from different copies → **handles more readers**.

The catch — and it's the *entire* difficulty of the topic: **when you change one copy, how do the other copies find out, and what happens if a room is locked (a machine or the network is down) right when you try to update it?** Everything below is a different answer to that one question.

## Architecture 1 — Single-leader (one boss notebook)

**Kid version:** one notebook is the **boss**. Anyone who wants to *change* something tells the boss; the boss writes it and then tells the copies "update to match." Anyone who just wants to *read* can look at any copy.

**Precise:** all **writes** go to one **leader**; the leader streams its changes (a replication log) to **followers**; **reads** can hit any replica. This is the most common setup — nearly every SQL database (Postgres, MySQL) works this way. It's popular because writes have a single place that decides the order, so there are **no write conflicts**.

The interesting decisions:

- **Synchronous vs asynchronous replication** — *does the boss wait for a copy to say "got it" before telling you "done"?*
  - **Sync:** the leader waits for a follower to confirm before acknowledging your write. **Safe** (the write survives the leader dying) but **slow**, and it *stalls completely* if that follower is down.
  - **Async:** the leader says "done" immediately and copies in the background. **Fast**, but if the leader crashes before copying, that just-confirmed write is **lost** (the juice spilled on the boss's notebook before anyone copied the new line).
  - **Semi-sync** (the common compromise): wait for *one* follower, not all. Most systems accept a tiny durability risk for speed.

- **Replication lag** — *the copies are a few seconds behind the boss*, like a live-TV broadcast delay. This causes the anomalies that the [[architecture/04-distributed-systems/04-consistency-models|session guarantees]] fix: you write a comment, your read hits a lagging copy, and your comment "vanishes" (needs **read-your-writes**); or you refresh and the score appears to go *backwards* (needs **monotonic reads**).

- **Failover** — *the boss is out sick; pick a new boss.* Promote a follower to leader. This is trickier than it sounds:
  - Which follower? It needs [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] to agree, or you get **split-brain** — *two kids both think they're the boss*, each accepting different writes, corrupting the data. Split-brain is the nightmare; [[architecture/04-distributed-systems/09-coordination-services|fencing tokens]] and quorums are the guardrails.
  - With **async** replication, the old leader may have had writes the new leader never received → those writes are **lost** on failover.

## Architecture 2 — Multi-leader (several bosses)

**Kid version:** each *region* (say, one classroom per city) has its own boss notebook, so kids write to their *nearby* boss instead of a far-away one. The bosses then tell each other what changed.

**Precise:** multiple leaders each accept writes and replicate to one another. Great for **write latency** (write locally) and **write availability** (a region keeps working even if cut off from the others) — common for multi-datacenter and offline-capable apps. The price: **the same data can be changed in two places at once**, so you get **write conflicts** (two cities edit the same profile field differently). Now you *must* resolve conflicts — see [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|conflict resolution]].

## Architecture 3 — Leaderless (no boss — ask the crowd)

**Kid version:** there's *no* boss. To **change** something, you tell **several** friends directly. To **read** something, you *ask several friends* and take the most recent answer. As long as the group you tell and the group you ask **overlap**, at least one friend you ask will know the latest.

**Precise:** any replica accepts writes; the client (or a coordinator) writes to *several* replicas and reads from *several*, using **quorums** for consistency. This is the **Dynamo / Cassandra** model — extremely available (no leader to fail over, no single point of failure) at the cost of the client handling staleness and conflicts.

### Quorums — consistency from counting
The neat trick that makes leaderless work. With **N** copies, require **W** copies to acknowledge each **write** and **R** copies to answer each **read**. If

$$W + R > N$$

then the write-set and any read-set **must share at least one copy** — so a read is guaranteed to touch a replica that has the latest write.

**Kid version:** 3 friends know the secret (N=3). You *tell* 2 of them the new secret (W=2) and later *ask* 2 of them (R=2). Since `2 + 2 > 3`, the two you ask can't *both* be the one friend you didn't tell — at least one of them has the new secret. 

Tuning W and R slides you along the tradeoff: `W=N, R=1` → fast reads, slow/fragile writes; `W=1, R=N` → fast writes, slow reads; `W=R=⌈(N+1)/2⌉` → balanced. Leaderless systems expose these knobs so you get **tunable consistency** per query. Two repair mechanisms keep lagging replicas honest: **read-repair** (on a read, push the latest value to any replica found stale) and **anti-entropy** (a background process that compares replicas — via [[architecture/04-distributed-systems/14-failure-detection-and-membership|Merkle trees]] — and fixes differences).

> **Quorums are weaker than they look.** `W+R>N` guarantees *overlap*, not linearizability — with concurrent writes, sloppy quorums, or a failed write that partially applied, you can still read stale or conflicting values. Leaderless ≠ strong consistency; it's *tunable, mostly-fresh* consistency.

## Choosing an architecture

| | Writes | Best for | Conflict risk |
|---|---|---|---|
| **Single-leader** | one place | most apps; anything needing simple strong-ish consistency | none (one writer) |
| **Multi-leader** | many places (per region) | multi-datacenter, offline-first | yes → need [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|resolution]] |
| **Leaderless** | any replica | max availability, no failover (Cassandra/Dynamo) | yes → quorums + [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|resolution]] |

The instinct: **single-leader for the data that must be correct** (money, accounts); **leaderless/eventual for the data that must be available** (feeds, carts, telemetry). And it pairs with [[architecture/04-distributed-systems/13-partitioning|partitioning]] — real systems *shard* data across many groups and *replicate* each shard, so the two techniques combine (each shard is a little single-leader or leaderless cluster).

## Key insight

**Replication is "keep copies so you survive failure and serve readers nearby," and the whole art is how copies learn about changes when machines and networks fail.** One boss (single-leader) avoids conflicts but needs careful failover to dodge split-brain; many bosses (multi-leader) and no boss (leaderless) buy availability and low write-latency but *create* conflicts you must resolve. Leaderless leans on **quorums** (`W+R>N` guarantees the reader touches a copy that saw the latest write) for tunable, mostly-fresh consistency. What readers are actually *promised* is the [[architecture/04-distributed-systems/04-consistency-models|consistency model]]; what you do when copies clash is [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|conflict resolution]].

## Related
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — what these architectures promise readers
- [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs & Conflict Resolution]] — resolving multi-leader / leaderless conflicts
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — what safe failover and strong consistency require
- [[architecture/04-distributed-systems/13-partitioning|Partitioning]] — the partner technique; shard, then replicate each shard
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — replication as a scaling tool
