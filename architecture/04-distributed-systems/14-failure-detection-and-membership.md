# Failure Detection & Membership

**[reference]** — from the canon (the phi-accrual paper, the SWIM paper, DDIA ch. 8, the Dynamo paper). [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] established the uncomfortable truth: **failure is a decision, not an observation** — you can't perfectly tell a dead node from a slow one. This note is how real systems make that decision *well*, and how a cluster keeps an agreed, current view of **who is alive** (membership).

## The kid version first

You're playing a game on a big playground and need to know: **has Sam left, or is Sam just being slow to answer?** You can't see the whole playground, so you rely on Sam periodically shouting **"here!"** (a heartbeat). If you stop hearing it… did Sam leave? Or is Sam just far away and quiet for a moment? **You genuinely can't be sure** — and if you *wrongly* declare Sam gone, you might give away Sam's turn while Sam's still playing (bad!).

So real playgrounds (clusters) use three tricks:
1. **Don't rely on just yourself — ask around** ("hey, anyone heard Sam?"). News spreads kid-to-kid until everyone knows. (That's **gossip**.)
2. **Use a *worry meter*, not a yes/no.** The longer since "here!", the *more worried* you get — and you only act when worry crosses a line *you* choose. (That's **phi-accrual**.)
3. **Everyone agree on the official roster** so two kids don't disagree about whether Sam's in the game. (That's **membership**, and it leans on [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]].)

## Heartbeats and the timeout tradeoff

The baseline: each node periodically sends "I'm alive" (a **heartbeat**); miss enough in a row and you *suspect* failure. But every fixed **timeout** is a lose-lose tradeoff (straight from [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|the impossibility of perfect failure detection]]):
- **Too short** → you declare *live-but-slow* nodes dead → needless failovers, data reshuffles, and **split-brain** risk.
- **Too long** → you're slow to react to real deaths → requests keep going to a corpse, hurting availability.

There is no "correct" timeout — only a tradeoff you tune to your network. The better detectors below stop pretending it's binary.

## Phi-accrual failure detection — a suspicion level, not a boolean

Instead of "dead/alive," a **phi-accrual detector** outputs a continuous number **φ** — *how suspicious we are right now* — computed from the **statistical distribution of recent heartbeat arrival times.** If heartbeats usually arrive every 1s ± 0.1s and it's been 1.05s, φ is low (relax); if it's been 5s, φ is high (worry a lot). The caller picks its **own threshold** ("act when φ > 8"), and different callers can choose differently for the same node.

The elegance: it **adapts automatically** to network conditions — on a jittery network the "normal" distribution is wider, so the detector is naturally more patient; on a snappy network it reacts faster. Used in **Cassandra** and **Akka**. It turns the timeout tradeoff from a hardcoded guess into a tunable, self-adjusting knob.

## Gossip protocols — decentralized awareness

A central monitor watching everyone is a bottleneck and a single point of failure. **Gossip** (epidemic protocols) spreads information the way a rumor spreads on the playground: **each node periodically picks a few random peers and exchanges state** ("here's who I think is alive, and their versions"). Any piece of news reaches the whole cluster in **`O(log n)` rounds** — exponentially fast, with no central authority, and robust to individual failures (there's no one to knock out).

Gossip carries **membership** (who's in the cluster), **failure suspicions**, and version metadata. It's how **Cassandra, Consul, Riak, and Dynamo** track membership and failures at scale. The tradeoff: it's **eventually consistent** — for a brief window, different nodes may have slightly different views of who's alive. That's fine for routing hints; it's *not* fine for decisions that must be atomic (which is why authoritative membership uses consensus — below).

## SWIM — gossip done efficiently

**SWIM** (Scalable Weakly-consistent Infection-style process Membership — the basis of HashiCorp **Serf/Consul**) is a refined gossip design that separates two concerns and fixes gossip's false-positive problem:
- **Failure detection by indirect pings:** node A pings B; if no reply, instead of immediately declaring B dead, A asks **`k` other nodes to *each* ping B on A's behalf.** Only if *all* the indirect pings also fail does A suspect B. This filters out "A↔B link is flaky but B is fine" false positives cheaply.
- **Dissemination piggybacked on the pings** (membership updates ride along on the ping traffic, no separate broadcast).

The result is failure detection whose cost-per-node stays roughly **constant** as the cluster grows, with far fewer false alarms than naive heartbeat-timeout.

## Anti-entropy — repairing divergence

Detecting failure is half of "keeping copies honest"; the other half is fixing the divergence that failures cause. **Anti-entropy** is a background process where [[architecture/04-distributed-systems/05-replication|replicas]] periodically **compare their data and reconcile differences.** Comparing everything byte-by-byte is too expensive, so replicas exchange **Merkle trees** (a tree of hashes): if two roots match, the data is identical — done; if not, you descend only into the *differing* branches, pinpointing exactly which keys diverged with minimal data transfer. This is the partner to **read-repair** (fix-on-read) in leaderless replication — read-repair fixes what you happen to read, anti-entropy sweeps the rest.

## Membership and split-brain

**Membership** = the agreed answer to "which nodes are currently in the cluster?" Gossip gives a *fast, eventually-consistent* view — great for routing. But some decisions need an **authoritative, atomic** membership (who's allowed to vote, which nodes own which [[architecture/04-distributed-systems/13-partitioning|shards]]), and for those, gossip's brief disagreements are dangerous. The nightmare is **split-brain**: a network partition where **both sides think the other is dead** and each elects its own leader / accepts its own writes → divergent, conflicting data.

The guardrails, all from earlier notes:
- **[[architecture/04-distributed-systems/07-consensus-and-paxos|Quorums]]** — a side without a majority refuses to act, so *at most one* side can make progress (the minority "loses" rather than forming a second brain).
- **Authoritative membership via consensus** — the official roster changes go through a [[architecture/04-distributed-systems/09-coordination-services|coordination service]] (etcd/ZooKeeper), so everyone agrees who's in.
- **[[architecture/04-distributed-systems/09-coordination-services|Fencing tokens]]** — even if a stale node *thinks* it's still a member/leader, the resource rejects its out-of-date token.

So the two views coexist by design: **gossip for fast, approximate awareness; consensus for the rare, must-be-correct membership decision.**

## Key insight

**You can't observe failure, only decide it — so decide well.** Fixed heartbeat timeouts are a lose-lose guess; **phi-accrual** replaces them with an adaptive *suspicion level* you threshold yourself. **Gossip** spreads membership and failure news cluster-wide in `O(log n)` rounds with no central point; **SWIM** makes it cheap and false-positive-resistant via indirect pings; **anti-entropy** (Merkle-tree diffs) repairs the divergence failures cause. And because gossip is only *eventually* consistent, the must-be-atomic decisions — official membership, leader — go through **[[architecture/04-distributed-systems/07-consensus-and-paxos|quorums/consensus]] and [[architecture/04-distributed-systems/09-coordination-services|fencing]]** to prevent **split-brain**.

## Related
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — why perfect failure detection is impossible
- [[architecture/04-distributed-systems/13-partitioning|Partitioning]] — the sibling operational topic (rebalancing on membership change)
- [[architecture/04-distributed-systems/05-replication|Replication]] — read-repair + anti-entropy keep replicas honest
- [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]] — ephemeral nodes as a liveness signal; authoritative membership
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — quorums as the split-brain guardrail
