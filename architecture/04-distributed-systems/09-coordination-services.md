# Coordination Services

**[reference]** — from the canon (the ZooKeeper and Chubby papers, DDIA ch. 8–9, the PBFT paper). Most applications should **not** implement [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] themselves — it's too easy to get wrong. Instead they lean on a **coordination service** that has consensus built in and exposes it as simple, reliable primitives: locks, leader election, configuration, membership. This note is those services, how to use them *safely* (fencing!), and the other consensus lineages beyond Raft.

## The kid version first

Running a fair vote is hard to get right ([[architecture/04-distributed-systems/08-raft-in-depth|Raft]] proves it). So instead of *every* group of kids inventing their own voting rules, the school provides **one trusted hall monitor** who already knows how to run fair votes and remember decisions. Any group can just walk up and ask:
- *"Who's our team captain?"* → the monitor runs the election and tells everyone the same answer.
- *"Can I hold the ball? Nobody else should take it while I have it."* → the monitor hands out a **turn** and makes sure only one kid holds it.
- *"Tell me the moment Sam leaves the playground."* → the monitor **watches** and pings you.

That hall monitor is **ZooKeeper** or **etcd**. The clever part is *how* it knows a kid left (so it can free their turn) and how it stops a **daydreaming kid who thinks they still have the ball** from messing things up (fencing). Both are below.

## ZooKeeper & etcd — the workhorses

Both are small, consensus-backed ([[architecture/04-distributed-systems/07-consensus-and-paxos|ZAB / Raft]]) key-value stores whose *whole job* is coordination, not bulk data. [[devops/05-orchestration/01-kubernetes|Kubernetes]] stores **all** its cluster state in etcd; Kafka, HBase, and many others use ZooKeeper. The primitives that make them useful:

- **The data model** — a tiny filesystem-like tree of **znodes** (ZooKeeper) or a flat key-space (etcd). You store small values (config, who's-the-leader, membership lists) — kilobytes, not gigabytes.
- **Ephemeral nodes** — a znode **tied to the client's session** that **automatically disappears when that client disconnects** (its heartbeats stop). *Kid version: the moment Sam leaves, his name-tag vanishes on its own.* This is the magic ingredient — it turns "is this client alive?" into "does its ephemeral node still exist?", giving you [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure detection]], locks, and leader election almost for free.
- **Sequential nodes** — the service appends a monotonically increasing number to a node's name, so clients get a fair, ordered queue (used for locks and elections).
- **Watches** — a client registers to be **notified** when a znode changes/disappears, instead of polling. Event-driven coordination.

### Leader election, the standard recipe
Every candidate creates an **ephemeral + sequential** node under `/election/`. The one with the **lowest sequence number is the leader.** Each other node **watches** the node just below it. If the leader's client dies, its ephemeral node vanishes → the next-lowest gets notified → it becomes leader. Automatic, fair, and self-healing — all from ephemeral + sequential + watches.

## Distributed locks — and why "get a lock" is not enough

The obvious use: *"only one worker should process this job."* Ask the service for a lock, do the work, release it. **But a naive lock is unsafe**, and this is one of the most important gotchas in the field:

```
1. Worker A acquires the lock, starts writing to storage.
2. Worker A hits a stop-the-world GC pause (or VM suspend) for 15 seconds
   — from the outside, indistinguishable from dead.
3. The lock's lease expires; the service gives the lock to Worker B.
4. Worker B starts writing.
5. Worker A WAKES UP, still believing it holds the lock, and writes too.
   → TWO writers → corruption. The lock did NOT protect anything.
```

The lock service did nothing wrong — [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|a paused process can't know time passed]]. The fix is **fencing tokens**: every time the lock is granted, the service also returns a **monotonically increasing number** (a fence). Worker A got token `33`; Worker B got token `34`. The **storage system itself checks the token** and **rejects any write with a token lower than the highest it has seen.** So when zombie A wakes and writes with token `33`, storage says "I've already accepted `34` — rejected." *Kid version: each turn comes with a numbered ticket, and the ball-keeper refuses any ticket older than the newest one it's seen.*

The deep lesson: **a lock alone can't provide mutual exclusion in an asynchronous system** — you need the *protected resource* to participate via fencing. Any "distributed lock" tutorial that omits fencing is teaching a data-corruption bug.

## The other consensus lineages (beyond Raft/Paxos)

Raft and Multi-Paxos aren't the only crash-fault-tolerant consensus protocols — and they're more alike than different (all are *leader + replicated log + numbered view/term changes*):

- **Viewstamped Replication (VR)** — actually *predates* Paxos; a leader-based replication protocol with "views" (Raft's terms by another name). Independently arrived at nearly the same design — strong evidence the leader-log-view shape is the *natural* solution.
- **ZAB (ZooKeeper Atomic Broadcast)** — ZooKeeper's protocol; a leader broadcasts a totally-ordered stream of state changes, with a recovery phase on leader change. Optimized for the high-read, low-write coordination workload.

If you understand Raft, you understand all three — they differ in details, not in essence.

## Byzantine fault tolerance — when nodes can *lie*

Everything so far assumes **crash faults**: nodes fail by *stopping*, never by sending false or conflicting messages. **Byzantine Fault Tolerance (BFT)** handles nodes that are *malicious or arbitrarily broken* — sending different messages to different peers, forging data. It's fundamentally harder:
- **You need `3f + 1` nodes to tolerate `f` liars** (vs `2f + 1` for crashes), because you must out-vote not just the silent but the actively-deceptive, and confirm a supermajority independently agrees.
- **PBFT** (Practical Byzantine Fault Tolerance) was the first efficient BFT protocol; modern **blockchains** use BFT-style consensus (or proof-of-work/stake as a Sybil-resistant twist) because participants are *untrusted strangers*.
- **When you need it:** trustless/adversarial settings (public blockchains, cross-organization systems). **When you don't:** normal internal infrastructure, where you control the machines and crash-fault-tolerant Raft/Paxos is the right, far cheaper choice.

## The rule of thumb: control plane, not data plane

Every coordination primitive is a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] round-trip — correct but slow, and it doesn't scale writes. So use a coordination service for the **control plane** (who's the leader, what's the config, which nodes are members, hand out the lock) — small, infrequent, must-be-correct decisions — and **never** route your high-throughput **data plane** (every user request) through it. etcd holds "which pod is the leader," not "every row of user data."

## Key insight

**Don't build consensus — rent it.** A coordination service (ZooKeeper/etcd) is a small consensus-backed store that hands you locks, leader election, config, and membership, mostly powered by **ephemeral nodes** (auto-vanish when a client dies) + **watches**. But a "distributed lock" is *not enough on its own*: a [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|paused process]] can hold a lock it's lost, so the protected resource must enforce **fencing tokens** (reject any writer with a stale number). Raft/VR/ZAB are the same leader-log-view idea; **BFT** (`3f+1`) is the pricier version for when nodes might *lie*. And always: coordination is for the **control plane**, never the data plane.

## Related
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — what these services run inside
- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — the algorithm powering etcd/Consul
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — process pauses, the reason fencing exists
- [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection & Membership]] — ephemeral nodes as a liveness signal
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — the biggest etcd user
