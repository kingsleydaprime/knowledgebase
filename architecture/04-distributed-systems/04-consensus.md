# Consensus

**[reference]** — from the canon (the Raft and Paxos papers, DDIA, MIT 6.824). The crown jewel of distributed systems: getting a group of unreliable nodes to *agree* on something, despite failures. This is what your **build-your-own Raft KV-store** project ([[architecture/05-case-studies/README|case studies]]) implements — and the fastest way to truly understand it.

## The problem

**Consensus** is getting multiple nodes to agree on a single value (or a single ordering of operations), such that: everyone agrees on the *same* value (agreement), it's a value someone actually proposed (validity), and the process eventually finishes (termination). Sounds trivial; it's one of the hardest problems in the field, because [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|nodes crash and the network drops/delays messages]] mid-agreement — and [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|FLP]] proves you can't *guarantee* termination in an asynchronous system. Real algorithms sidestep FLP with timeouts (guaranteeing termination only during periods of network stability — which is almost always).

## Why you need it constantly

Consensus is the foundation under things that seem unrelated:

- **Leader election** — agreeing which node is the leader ([[architecture/04-distributed-systems/03-replication-and-consistency|replication failover]], [[architecture/03-architectural-patterns/04-microservices-patterns|coordinator election]]).
- **Strong consistency / linearizability** — agreeing on the order of operations.
- **Distributed locks, configuration, membership** — one agreed source of truth.
- **Atomic commit** — agreeing to commit or abort a [[architecture/04-distributed-systems/05-distributed-transactions|transaction]].

This is why systems like **etcd** and **ZooKeeper** exist: they package consensus as a service, and other systems ([[devops/05-orchestration/01-kubernetes|Kubernetes]] uses etcd) lean on them rather than implementing it.

## Paxos — correct and famously baffling

**Paxos** (Lamport) was the first proven-correct consensus algorithm. It works via proposers, acceptors, and a majority-quorum protocol (prepare/promise, accept/accepted phases). It's correct and influential — but notoriously hard to understand and to implement correctly, which held the field back for years. Multi-Paxos extends it to a sequence of values (a log).

## Raft — consensus designed to be understandable

**Raft** was created explicitly to be *understandable* (its paper is titled "In Search of an Understandable Consensus Algorithm") and is now the common choice (etcd, Consul, CockroachDB). It decomposes consensus into three digestible pieces:

1. **Leader election** — nodes are Follower, Candidate, or Leader. If a follower hears nothing from a leader within a randomized **election timeout**, it becomes a candidate and requests votes; a candidate that wins a **majority** becomes leader. Randomized timeouts make split votes rare. Time is divided into **terms**, each with at most one leader.
2. **Log replication** — all writes go to the leader, which appends to its log and replicates to followers; once a **majority** have it, the entry is **committed** and applied. This gives a single agreed, ordered log of operations (a replicated state machine).
3. **Safety** — rules ensuring a new leader has all committed entries (a candidate can't win without an up-to-date log), so committed data is never lost even across leader changes.

The key mechanism throughout is **majority quorums**: any decision needs >half the nodes, and any two majorities overlap — so a new leader's majority必 includes a node that saw the last commit. This is why consensus clusters are odd-sized (3, 5) and tolerate `(N-1)/2` failures (a 5-node cluster survives 2 down).

## The costs and limits

- **Latency** — every committed operation needs a majority round-trip, so consensus is *slower* than a single node. You use it for the things that *must* be consistent (metadata, leader election, config), not high-throughput data paths.
- **Availability** — needs a majority up; a cluster that loses its majority (a partition with no majority side) stops accepting writes (choosing [[architecture/01-system-design-fundamentals/04-cap-and-consistency|consistency over availability]] — CP).
- **It doesn't scale writes** — adding nodes adds fault tolerance, not throughput (more nodes = larger quorum = *slower*). Consensus clusters stay small; you shard *across* many small consensus groups for scale.

## Byzantine fault tolerance (briefly)

Raft/Paxos assume nodes are honest-but-crashy (they fail by stopping, not lying). **Byzantine fault tolerance** (BFT) handles nodes that are *malicious or arbitrarily faulty* (send conflicting messages) — much harder and more expensive, needed in trustless settings (blockchains use BFT-style consensus). For normal internal systems, crash-fault-tolerant Raft is what you want.

## Why build it

Consensus is the topic that *most* rewards implementation — reading Raft feels clear until you hit the edge cases (a leader crashing mid-replication, a partition healing, a stale leader returning). Implementing a Raft KV-store surfaces all of it and is the single best distributed-systems learning project. It also makes the [[architecture/04-distributed-systems/03-replication-and-consistency|replication]] and [[architecture/04-distributed-systems/05-distributed-transactions|transaction]] material concrete.

## Related
- [[architecture/04-distributed-systems/03-replication-and-consistency|Replication & Consistency]] — what consensus provides strong consistency for
- [[architecture/04-distributed-systems/05-distributed-transactions|Distributed Transactions]] — atomic commit, a consensus problem
- [[architecture/05-case-studies/README|Case Studies]] — the build-your-own Raft KV-store
