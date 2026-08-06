# Failure Detection & Membership

**[reference]** · **⏳ outline — deep note in progress** (part of the distributed-systems deep-curriculum build).

[[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] established that **failure is a decision, not an observation** — you can't perfectly tell dead from slow. This note is how real systems make that decision well, and how a cluster keeps an agreed view of *who is currently alive* (membership).

## Will cover
- **Heartbeats and timeouts** — the baseline, and the unavoidable false-positive/false-negative tradeoff of any fixed timeout.
- **Phi-accrual failure detection** — instead of a boolean "dead/alive," output a continuous **suspicion level** (φ) from the *statistical distribution* of recent heartbeat inter-arrival times, so the detector adapts to network conditions and callers pick their own threshold. Used in Cassandra/Akka.
- **Gossip protocols** — epidemic-style dissemination: each node periodically exchanges state with a few random peers, and information spreads in `O(log n)` rounds. Scalable, robust to failures, eventually-consistent membership.
- **SWIM** — Scalable Weakly-consistent Infection-style process Membership: gossip + a smarter failure detector (indirect pings via peers to cut false positives), the basis of HashiCorp Serf/Consul membership.
- **Anti-entropy** — background reconciliation (Merkle-tree diffs) that repairs replica divergence, the partner to read-repair in [[architecture/04-distributed-systems/05-replication|leaderless replication]].
- **Split-brain** — what happens when failure detection is wrong and two halves both think they're in charge; why [[architecture/04-distributed-systems/07-consensus-and-paxos|quorums]] and [[architecture/04-distributed-systems/09-coordination-services|fencing]] are the guardrails.

## Related
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] · [[architecture/04-distributed-systems/13-partitioning|Partitioning]] · [[architecture/04-distributed-systems/05-replication|Replication]] · [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]]
