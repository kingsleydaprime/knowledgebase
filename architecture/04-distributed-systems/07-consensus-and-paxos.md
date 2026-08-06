# Consensus & Paxos

**[reference]** — from the canon (Lamport's *Paxos Made Simple*, DDIA ch. 9, MIT 6.824). The **crown jewel** of distributed systems: getting a group of unreliable machines to *agree* on one thing, despite crashes and a lying network. This note is the *problem*, why it's everywhere, the **quorum** idea that makes it possible, and **Paxos** (the original solution). **Raft** — the modern, understandable version — gets its own implementation-depth note ([[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]]).

## The kid version first

A group of friends has to pick **one** restaurant, and they'll all go to whatever gets picked. Trouble: some friends might **leave partway** (crash), some **texts get lost** (network), and you often **can't tell** who's still around. How do you get *everyone who's still there* to agree on the **same** choice, and never end up with half going to pizza and half going to tacos?

The trick that works is a **majority vote**. Here's the magic part: **any two groups that are each "more than half" must share at least one person.** So if "pizza" won a majority, there is *no* way "tacos" also won a majority — because the one friend in both groups can't have voted for both. That single fact — **majorities always overlap** — is the seed of every consensus algorithm. Everything below is machinery to run that vote correctly even while friends drop out and texts vanish.

## The problem, precisely

**Consensus:** get a set of nodes to agree on a single value (or a single *order* of operations), satisfying four properties:
- **Agreement** — no two nodes decide *different* values. *(the critical one)*
- **Validity (integrity)** — the decided value was actually proposed by someone (not invented).
- **Termination** — every non-failed node eventually decides. *(the hard one)*

Agreement and validity are **[[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|safety]]** — they must hold *always*, even under total network chaos. Termination is **liveness** — and [[architecture/04-distributed-systems/02-theoretical-limits|FLP]] proves you *can't* guarantee it in a fully asynchronous network. So real algorithms are built to be **always safe** (never decide two different values) and to **terminate once the network behaves** (partial synchrony, via timeouts). *You never trade away agreement; you accept that progress can stall during a bad partition.*

## Quorums — why "more than half" is the whole trick

The overlap property, stated precisely: in a cluster of **N** nodes, a **quorum** is any set of **⌊N/2⌋ + 1** nodes (a strict majority). **Any two quorums intersect in at least one node.** That shared node is what makes agreement possible — it "remembers" the previous decision and prevents a second, conflicting one from forming.

Consequences you can feel:
- Clusters are **odd-sized** (3, 5, 7) — an even size wastes a node (4 tolerates the same 1 failure as 3, but needs 3 for a quorum).
- An **N-node cluster tolerates ⌊(N−1)/2⌋ failures** — 3 survives 1 down, 5 survives 2 down.
- If a partition leaves **no side with a majority**, *nobody* can make progress — the cluster stops accepting writes rather than risk two conflicting decisions ([[architecture/04-distributed-systems/02-theoretical-limits|CP under CAP]]).

## Why you need consensus constantly

It hides under a surprising range of features — all of them "get everyone to agree on one thing":
- **Leader election** — agree on *which* node is the leader ([[architecture/04-distributed-systems/05-replication|replication failover]]) — and avoid two leaders (split-brain).
- **A replicated log / [[architecture/04-distributed-systems/12-the-log-and-state-machines|state machine]]** — agree on the *order* of operations, which is what gives [[architecture/04-distributed-systems/04-consistency-models|linearizable]] strong consistency.
- **Atomic commit** — agree to commit-or-abort a [[architecture/04-distributed-systems/10-distributed-transactions|transaction]] across shards.
- **Locks, configuration, membership** — one agreed source of truth.

This is why **etcd** and **ZooKeeper** ([[architecture/04-distributed-systems/09-coordination-services|coordination services]]) exist: they package consensus as a service so other systems ([[devops/05-orchestration/01-kubernetes|Kubernetes]] stores everything in etcd) don't reinvent it.

## Paxos — the original, correct, famously baffling

**Paxos** (Lamport, 1998) was the first *proven-correct* consensus algorithm, and everything since is a descendant. Three roles (a node can play several): **proposers** suggest values, **acceptors** vote, **learners** find out the result. Single-decree Paxos (agree on *one* value) runs two phases, both gated on a majority:

**Phase 1 — Prepare / Promise.** A proposer picks a **proposal number** `n` (globally unique, ever-increasing) and asks a majority of acceptors to *prepare* for `n`. An acceptor that hasn't already promised a *higher* number **promises** not to accept anything below `n`, and — crucially — **reports back any value it has already accepted**.

**Phase 2 — Accept / Accepted.** If the proposer got promises from a majority, it sends an *accept* request for value `v`. But **which `v`?** Here's the safety rule that makes Paxos correct: **if any acceptor reported an already-accepted value, the proposer MUST re-propose the one with the highest proposal number** (it cannot use its own preferred value). Only if *no* acceptor had accepted anything is the proposer free to choose. Acceptors accept unless they've since promised a higher number. Once a majority accepts `v`, `v` is **chosen** — permanently.

**Why it's correct (the intuition):** proposal numbers give a total order to attempts, the majority overlap guarantees any new proposer *sees* a previously-chosen value (via that shared acceptor), and the "re-propose the highest accepted value" rule forces it to *keep* that value. So once a value is chosen, every later proposal re-chooses the same one → **agreement holds** even with competing proposers, crashes, and lost messages.

**Multi-Paxos** extends single-decree to a *sequence* of values (a log): elect a stable leader, run Phase 1 *once*, then stream Phase-2-only accepts for each new log slot — amortizing the expensive part. This is what real systems (Google Chubby, Spanner) actually run.

**Why Paxos has a bad reputation:** single-decree Paxos is elegant, but turning it into a *practical, log-replicating, leader-based, membership-changing* system (Multi-Paxos) is underspecified in the paper and notoriously hard to implement correctly. Frustration with exactly this is what produced **Raft** — see [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]], which packages the same guarantees into something you can actually build.

## The costs and limits (true of all consensus)

- **Latency** — every committed operation needs a majority round-trip, so consensus is *slower* than a lone node. Use it for what *must* be consistent (metadata, leader election, config, the commit point), never the high-throughput data path.
- **Availability** — needs a majority alive; lose the majority and writes stop (CP).
- **It does not scale writes** — more nodes = more fault tolerance but a *bigger* quorum = *slower*. Consensus clusters stay small (3–7); for scale you run **many** small consensus groups and [[architecture/04-distributed-systems/13-partitioning|shard]] across them (each shard its own Raft/Paxos group — the Spanner model).
- **Crash-fault-tolerant only** — Paxos/Raft assume nodes fail by *stopping*, not *lying*. Malicious/arbitrary nodes need **[[architecture/04-distributed-systems/09-coordination-services|Byzantine]]** consensus (`3f+1` nodes), which is much costlier and reserved for trustless settings.

## Key insight

**Consensus is "get everyone still here to agree on one value, forever," and it's possible only because majorities overlap** — any two majorities share a node that remembers the last decision, so a second, conflicting decision can't form. You hold **agreement always** and accept that **progress can stall** when no majority is reachable (FLP). **Paxos** achieves this with proposal-numbered prepare/accept rounds and the safety rule "re-propose the highest already-accepted value"; **Multi-Paxos** turns it into a log via a stable leader. It's correct but painful to build — which is why the next note is **Raft**, the same guarantees made understandable.

## Related
- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — the same problem solved in a buildable way (the recommended study path)
- [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]] — consensus packaged as etcd/ZooKeeper; BFT
- [[architecture/04-distributed-systems/05-replication|Replication]] — what strong consistency and safe failover require
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — atomic commit is a consensus problem
- [[architecture/05-case-studies/README|Case Studies]] — the build-your-own Raft KV-store
