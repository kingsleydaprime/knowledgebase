# Build Your Own Raft Key-Value Store

> **[Advanced]** · Leader election, log replication, and a replicated store on top. **Kill the leader mid-write and the data is still there, still consistent, on every surviving node.**

## What you're building

**A consensus algorithm, and a key-value store that uses it.** Three to five processes, each holding a full copy of the data. Clients `put` and `get`; any node can be killed at any moment, the network can be partitioned arbitrarily, and every surviving node still agrees on exactly what happened and in what order.

**And what you're deliberately not:** sharding across multiple Raft groups, competing with etcd on throughput, or handling Byzantine failures. **Crash-stop and network partitions are the whole curriculum** — they are hard enough, and they are what actually happens.

This is the guide [[project-ideas|project-ideas.md]] has named as *"the best distributed-systems project there is"* since the file was written. **It is also the only project here where your intuition is actively wrong** and the code is the thing that corrects it.

## What you need first

- **Why distributed systems are hard** — specifically, that you cannot tell a crashed node from a slow one → [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|what makes them hard]]
- **The impossibility results**, so you know what you are not allowed to achieve → [[architecture/04-distributed-systems/02-theoretical-limits|theoretical limits]]
- **Consensus, and what it is for** → [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] · [[architecture/04-distributed-systems/08-raft-in-depth|Raft in depth]]
- **The replicated state machine model** — the idea the whole thing rests on → [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log and state machines]]
- **RPC, and concurrency you trust** → [[architecture/02-building-blocks/05-communication|communication]]
- **The Raft paper itself**, *In Search of an Understandable Consensus Algorithm* (Ongaro and Ousterhout, 2014). **Figure 2 is one page and it is the entire specification.** Print it.

**Go is the canonical language** — MIT's 6.824 labs are in Go, the reference implementations are in Go, and goroutines plus channels map onto this problem unusually well. **Rust** works and its type system genuinely helps with the state transitions. **Java** is fine. **Python** is fine if you are honest about the concurrency.

## The build order

**1. Nodes that can call each other.**
Three processes, a config file of peer addresses, and RPC in both directions. **Raft needs exactly two remote calls** — `RequestVote` and `AppendEntries` — plus `InstallSnapshot` later. Everything else is local state.
*Works when:* node 1 can call a no-op RPC on nodes 2 and 3, and the call fails cleanly when a node is down.

**2. Leader election.**
Each node is a **follower**, a **candidate** or a **leader**. A follower that hears nothing for a randomised timeout becomes a candidate, increments its term and requests votes; a majority makes it leader.

**The randomisation is not a detail.** With fixed timeouts every node campaigns simultaneously, splits the vote, and the cluster elects nobody, forever. Pick uniformly from a range about 10× your heartbeat interval — say heartbeats every 50 ms and timeouts drawn from 250–500 ms.
*Works when:* you start three nodes and **exactly one** declares itself leader; you kill it and another is elected within a second; you restart the old one and it quietly becomes a follower rather than starting a fight.

**3. Heartbeats.**
The leader sends empty `AppendEntries` on an interval. That is all a heartbeat is — the same RPC with no entries in it.
*Works when:* the cluster stays stable for ten minutes with no spurious elections. **If the term number is still climbing, your timer is not being reset where it should be.**

**4. The log, and replication.**
A client command becomes an entry `{term, index, command}` appended to the leader's log and shipped to followers. Each `AppendEntries` carries `prevLogIndex` and `prevLogTerm`; a follower **rejects it unless its log matches there**. On rejection the leader decrements `nextIndex` for that follower and retries, walking backwards until the logs converge.
*Works when:* a follower started from an empty log catches up to a leader with a thousand entries, and a follower with *conflicting* entries has them overwritten.

**5. Commitment — and the rule everyone gets wrong.**
An entry is committed when it is stored on a majority. **But a leader may only advance `commitIndex` for an entry from its own current term.**

This is Figure 8 of the paper, and it is the subtlest thing in it. A leader that counted replicas of an *old* entry could commit it, then be replaced by a leader that never had it — and committed data would vanish. Once an entry from the current term commits, everything before it commits along with it.
*Works when:* you can explain that paragraph to yourself without looking. Until then, assume this is where your bug is.

**6. Apply to a state machine.**
Once `commitIndex` passes `lastApplied`, feed the command into a hash map: `put`, `get`, `delete`. **Every node applies the same commands in the same order, so every node holds the same map** — which is the entire point of the exercise.
*Works when:* a `put` through the leader is visible on all three nodes' maps.

**7. Persistence, in the right order.**
`currentTerm`, `votedFor` and the log must be on disk — **`fsync`'d before you respond to any RPC**, not after. A node that votes, crashes, restarts and votes differently in the same term breaks the algorithm's central safety argument.
*Works when:* `kill -9` on all three nodes followed by a restart recovers the data with no committed entry lost.

**8. Clients, and exactly-once.**
Clients do not know who the leader is: they try a node, get redirected, retry on timeout. **Which means a retried `put` may be applied twice** — and a duplicated `append` or `increment` is a wrong answer, not a slow one.

Give every client an id and every request a sequence number; have the state machine remember the last sequence applied per client and return the cached result for a repeat. **The deduplication table is part of the replicated state**, so it must be in the log and in the snapshot too.
*Works when:* a client whose request times out mid-flight, and retries, sees the operation applied exactly once.

**9. Snapshots and log compaction.**
The log cannot grow forever. Serialise the state machine, discard the prefix, and add the `InstallSnapshot` RPC for followers too far behind to catch up from entries.
*Works when:* a node that has been down for 100,000 operations rejoins and catches up via a snapshot rather than a replay.

**10. Break it on purpose.**
This is the milestone that separates a Raft that works from a Raft you can trust. Build a test harness that can **drop, delay, duplicate and reorder messages between any pair of nodes**, then run: leader killed mid-append; a partition isolating the leader with a minority; a partition healing; every node restarted at a random moment.
*Works when:* a few hundred randomised runs all pass. **These bugs are probabilistic — a single passing run means nothing.**

**11. Optional: membership changes and read leases.**
Adding and removing nodes at runtime (add one at a time and it stays simple). Serving reads from the leader without a round trip, via a lease. Both are real and both are refinements.

## The parts that will bite you

**You skipped a rule in Figure 2.** Almost every Raft bug is this. The rules look redundant — several say "if you see a higher term, become a follower and update your term" in slightly different contexts. **They are not redundant.** When a test fails, re-read Figure 2 line by line against your code before you debug anything else.

**Resetting the election timer in the wrong places.** Reset it on a heartbeat from the *current* leader and on granting a vote. **Do not** reset it for a rejected `AppendEntries` or a stale-term message, or a partitioned old leader can suppress elections indefinitely.

**Holding a lock across an RPC.** The classic deadlock: node A holds its mutex while calling node B, which is calling A. Snapshot the state you need, release the lock, then make the call.

**Applying entries out of order.** With concurrent `AppendEntries` responses it is easy to apply index 7 before index 6. One applier goroutine reading from a channel in order is the fix, and it is simpler than the alternative.

**Treating `get` as free.** A read served by a node that does not know it has been deposed returns stale data. Either route reads through the log like writes, or implement leases properly — **but do not quietly assume the leader is still the leader.**

**Heisenbugs.** Timing-dependent failures that appear once in fifty runs. Run your tests in a loop, with a `-race` detector where you have one, and keep the seed of any run that fails.

## How to know it works

1. **The 6.824 (now 6.5840) test suite** is the gold standard and is publicly available. If you write in Go, you can run the real thing against your implementation
2. **Chaos tests**, run hundreds of times with different seeds — kill, partition, heal, restart
3. **A linearizability checker** — [Porcupine](https://github.com/anishathalye/porcupine) for Go, Knossos for the Jepsen ecosystem. Record a history of client operations and have it verify that *some* sequential ordering explains what every client saw. **This catches the bugs your assertions cannot**, because it tests the property you actually care about rather than one you thought to check → [[architecture/04-distributed-systems/15-testing-distributed-systems|testing distributed systems]]
4. **No committed entry is ever lost**, under every failure you can produce
5. **Availability**: the cluster keeps serving with one node down out of three, and correctly refuses to serve with two down

## Where to stop

**Stop when the chaos tests pass consistently and a linearizability checker agrees.**

**Not worth it here:** sharding into multiple Raft groups, batching and pipelining for throughput, or a production storage engine underneath. All three are what turns this into etcd, and all three teach less per hour than what you have already done.

**You will have learned** the thing that only building it teaches: that **a distributed system is not a program that runs in several places, it is a program where every line might be the last one this node executes.** Terms, majorities and the commit rule stop being mechanisms you memorised and become the only possible answers to questions you have now personally been asked. [[architecture/04-distributed-systems/04-consistency-models|Consistency models]] read completely differently afterwards, and so does every outage postmortem you will ever read.

## Related

- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in depth]] — the reference note for this guide
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|The log and state machines]] — the idea underneath
- [[build-your-own-shit/06-your-own-database|Your Own Database]] — the single-node storage this replicates
- [[build-your-own-shit/14-your-own-blockchain|Your Own Blockchain]] — consensus without trusted participants, for contrast
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
