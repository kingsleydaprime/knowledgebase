# Raft in Depth

**[reference]** — from the Raft paper (Ongaro & Ousterhout, *In Search of an Understandable Consensus Algorithm*, 2014) and MIT 6.824. [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] covered *why* agreement is hard and the original solution. This note is **Raft at the level where you can actually build one** — the field's most-implemented consensus algorithm, and the topic that most rewards writing the code ([[architecture/05-case-studies/README|build-your-own Raft KV-store]]). The details below feel obvious in prose and bite you in the implementation; that gap is the whole point.

## The kid version first

A group keeps a shared **to-do list** that must stay identical for everyone, even as kids come and go. Raft's plan:
1. **Pick one captain.** Only the captain writes on the list; everyone else **copies the captain's list**. One writer = no arguments about order.
2. **Copy before it counts.** The captain only calls a line "official" once **more than half** the group has copied it down. That way, even if the captain vanishes, a majority already has every official line.
3. **New captain if the old one goes quiet.** If nobody hears from the captain for a while, someone raises their hand and asks for votes; whoever a **majority** picks becomes the new captain — but *only if their list is at least as complete as everyone who votes*, so no official line is ever lost.
4. **Numbered rounds so ghosts are ignored.** Each "who's captain" round has a number (a **term**). If an old captain who fell asleep wakes up and starts giving orders with an *old* number, everyone says "that number's expired" and ignores them.

That's Raft. The rest is making each of those four rules airtight against the exact worst-case timing.

## The pieces: roles, terms, the log

- **Three roles:** every node is a **Follower** (passive, copies the leader), a **Candidate** (running to be leader), or the **Leader** (handles all client writes). Normal operation = one leader + followers.
- **Terms** = a logical clock ([[architecture/04-distributed-systems/03-time-and-ordering|logical time]]). Time is divided into numbered terms, each starting with an election and having **at most one leader**. *Every message carries the sender's term.* The rule that makes stale leaders harmless: **if you ever see a term higher than yours, adopt it and become a follower; if you receive a message with a term lower than yours, reject it.** Terms are how the group ignores ghosts from the past.
- **The log** = each node's copy of the ordered list of commands. Each entry stores `(term when it was created, command)`. Once an entry is **committed**, it's applied to the state machine ([[architecture/04-distributed-systems/12-the-log-and-state-machines|replicated state machine]]) — and committing a log of commands *is* consensus on their order.

## The two RPCs, field by field

Everything in Raft is these two remote calls. Knowing *why each field exists* is knowing Raft.

### `RequestVote` (candidates → everyone, during elections)
| Field | Why it's there |
|---|---|
| `term` | the candidate's term; a voter with a higher term rejects it |
| `candidateId` | who's asking |
| `lastLogIndex`, `lastLogTerm` | **the up-to-date check** — the voter grants its vote *only if the candidate's log is at least as up-to-date as its own* (see Safety). This is what stops a node missing committed entries from ever winning. |

A voter grants its vote if the candidate's term is current, it hasn't already voted this term, and the candidate's log is at least as up-to-date as its own.

### `AppendEntries` (leader → followers; also the heartbeat)
| Field | Why it's there |
|---|---|
| `term`, `leaderId` | which leader/term is speaking |
| `prevLogIndex`, `prevLogTerm` | **the consistency check** — the entry *immediately before* the new ones. The follower accepts the new entries **only if it has a matching entry at `prevLogIndex` with `prevLogTerm`.** This single check enforces the Log Matching Property. |
| `entries[]` | the new log entries (empty = a pure **heartbeat**) |
| `leaderCommit` | the leader's commit index, so followers learn what's now safe to apply |

If the consistency check **fails**, the follower rejects; the leader **decrements `prevLogIndex` and retries**, walking backward until it finds the last point where their logs agree, then overwrites everything after it with its own. The leader's log is the source of truth; divergent follower tails get rewritten.

## Leader election (rule 3, precisely)

A follower that hears nothing from a leader within its **election timeout** becomes a candidate: it increments its term, votes for itself, and sends `RequestVote` to all. Outcomes: it wins a **majority** → becomes leader and starts sending heartbeats; or it hears from a legitimate leader (equal/higher term) → steps back to follower; or the vote **splits** (nobody wins) → a new election.

The trick that prevents endless split votes: **randomized election timeouts** (e.g. each node picks 150–300 ms randomly). One node almost always times out first, wins before others wake up, and starts heartbeating — split votes become rare and self-heal fast.

## Log replication & the Log Matching Property

All client writes go to the leader, which appends to its log and sends `AppendEntries`. The **Log Matching Property** is Raft's backbone invariant:
> If two logs contain an entry with the **same index and term**, then (a) they store the same command, *and* (b) the logs are **identical in all entries up to that point.**

Why it holds: (a) a leader creates at most one entry per index per term; (b) the `prevLogIndex/prevLogTerm` check means a follower only appends if the *previous* entry already matched — inductively, a match at index `i` implies a match all the way back. So one matching `(index, term)` pair proves the entire prefix matches. This is what lets the leader repair a follower by walking backward to the first agreement point and overwriting forward.

## The subtle part everyone gets wrong: the commitment rule (Figure 8)

Naively you'd think: "an entry is committed once it's replicated on a majority." **This is wrong and it's the single most-missed detail in Raft.**

The danger: an entry from a *previous* term can be replicated on a majority and *still later be overwritten* by a new leader — because a different node with a longer log could win a subsequent election and force its own entries. If you committed (applied) that entry based only on majority replication, you'd have applied something that later disappears → a **safety violation**.

**Raft's rule:** a leader may only **commit an entry from its *own current term*** (once that entry is on a majority). Committing a current-term entry **drags all preceding entries with it** (by Log Matching, they're on that majority too), so old entries *do* get committed — but only *indirectly*, once something from the new term sits on top of them. A brand-new leader therefore often appends an empty **no-op** entry immediately, so it has a current-term entry to commit and can safely commit the inherited backlog. Miss this rule and your implementation loses committed data on a specific leader-crash-and-recover sequence; the paper's "Figure 8" is exactly that scenario.

## Safety: why a new leader has every committed entry

The **up-to-date restriction** in `RequestVote` guarantees it. "Up-to-date" is defined as: **higher `lastLogTerm` wins; if equal, longer log wins.** A candidate needs a majority to win; a committed entry is (by definition) on a majority; any two majorities overlap → at least one voter has the committed entry, and it will *refuse* to vote for a candidate whose log is less up-to-date. Therefore **no candidate missing a committed entry can ever assemble a majority.** Committed data survives every leader change — the property that makes Raft correct.

## Cluster membership changes

Adding/removing nodes is dangerous: if nodes switch from the old to the new configuration at different times, you can briefly have **two disjoint majorities** (old-majority and new-majority) that each elect a leader → split brain. Raft's answers:
- **Joint consensus** (the paper's general method): a transitional configuration `C_old,new` in which decisions require majorities from **both** the old and new sets simultaneously, so no split is possible; then transition to `C_new`.
- **Single-server changes** (the common simplification): add or remove **one** node at a time — a one-node change can't create two disjoint majorities, so it's safe without joint consensus.

## Log compaction & snapshots

The log can't grow forever. Each node periodically **snapshots** its state machine (the compacted state up to some index) and discards the log entries before it. A leader that needs to update a follower whose required entries were already discarded sends an **`InstallSnapshot`** RPC (the whole state) instead of `AppendEntries`. This bounds disk/memory and speeds up rejoining far-behind nodes.

## Linearizable client semantics (the details real systems need)

Consensus on the log isn't enough for a correct *service*:
- **Duplicate commands:** a client retries a write after a timeout (it never saw the ack), so the same command reaches the log twice → applied twice (double-charge!). Fix: each client gets a **client id + monotonic sequence number**; the state machine remembers the last sequence applied per client and **ignores duplicates** — giving exactly-once *effect* despite at-least-once delivery ([[architecture/04-distributed-systems/02-theoretical-limits|Two Generals]]).
- **Linearizable reads without writing to the log:** naively, a read must go through the log (expensive) to be sure it's current. Optimizations: **ReadIndex** — the leader records its current commit index, confirms it's *still* leader via one heartbeat round-trip to a majority, then serves the read once it has applied up to that index (no log append). **Lease reads** — the leader holds a time-based lease (renewed by heartbeats) during which it *knows* no other leader exists, so it can serve reads locally with zero round-trips (relying on bounded clock drift — a weaker but faster guarantee).

## A worked failure trace (why the rules earn their keep)

1. Leader **L1** (term 4) appends entry `X` and replicates it to a **minority** before crashing. `X` is *not* committed.
2. Timeout → election. **L2** wins term 5. Whether `X` survives depends on whether a majority had it: if not, L2's log lacks `X`, and when L2 appends its own entries, the `prevLog` check makes followers that had `X` **overwrite** it. No harm — `X` was never committed, so no client was ever told it succeeded.
3. **L1 recovers** and, still thinking it's leader in term 4, sends `AppendEntries` with `term=4`. Every node now at term 5 sees `4 < 5` and **rejects** it; L1 sees the higher term in the replies and **steps down** to follower. The ghost is ignored.
4. L2 appends a term-5 entry, replicates to a majority, and **commits it — which retroactively commits any inherited entries beneath it** (the Figure-8 rule). The list is consistent and no committed line was ever lost.

Every rule above maps to one step of this trace — that's why they exist.

## Key insight

**Raft = one captain writes the shared list, everyone copies it, a line counts only once a majority has it, and a new captain must have every counted line — all tagged with numbered terms so ghosts from old rounds are ignored.** The buildable details that matter: the two RPCs and *why each field exists* (`prevLog*` enforces Log Matching; `lastLog*` enforces the up-to-date restriction), randomized timeouts to avoid split votes, the **Figure-8 commitment rule** (commit only a *current-term* entry, which drags the rest), snapshots for compaction, and client-id dedup + ReadIndex/lease for a correct, fast *service*. Read it, then **build it** — the edge cases only become real in code.

## Related
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — the problem Raft solves and the original algorithm
- [[architecture/04-distributed-systems/09-coordination-services|Coordination Services]] — etcd/ZooKeeper run this under the hood; fencing, leases
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|The Log & State Machines]] — what the committed log feeds
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — terms as a logical clock
- [[architecture/05-case-studies/README|Case Studies]] — build the Raft KV-store (do this)
