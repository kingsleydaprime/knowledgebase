# Theoretical Limits

**[reference]** — from the canon (FLP 1985, Brewer's CAP + Gilbert & Lynch's proof, Abadi's PACELC, the CALM theorem). The [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|models]] in the previous note produce hard *impossibility results* — things no algorithm can do, no matter how clever. Knowing these stops you chasing the impossible and tells you exactly which tradeoff you're forced to make. This is the theory that makes the rest of the course make sense.

## The kid version first

Some things aren't just *hard* — they're **impossible**, and no amount of cleverness fixes them. Knowing which is which saves you from trying forever. Three examples you'll meet below:
- **You and a friend want to jump in the pool at the *exact* same second, but you can only plan by passing notes** that might get lost. Can you *guarantee* you both jump together? No — the last note sent is never confirmed, so someone is always unsure. (That's "Two Generals.")
- **A group can't always agree on an answer if even one member might have secretly wandered off**, because "wandered off" looks the same as "just being slow." (That's "FLP.")
- **When your walkie-talkies stop reaching each other, you have to choose: keep answering (maybe with old info) or stay silent until you reconnect** — you can't do both. (That's "CAP.")

This note is the short list of walls the universe puts up. Every real design is a choice about *which wall you'll lean against.*

## Two Generals — agreement over a lossy channel is impossible

The oldest result, and the cleanest intuition. Two generals must attack at the same time to win; they can only communicate by messengers who might be captured. General A sends "attack at dawn." Did it arrive? A needs an ack. B sends the ack — did *that* arrive? B now needs an ack of the ack. **No finite exchange of messages ever lets both sides be *certain* the other will attack** — every message needs confirmation, and the last message sent is always unconfirmed. 

The consequence you live with daily: **there is no such thing as guaranteed exactly-once delivery over an unreliable network.** TCP doesn't solve this — it gives you *reliable-ish* delivery with retries, but the fundamental uncertainty (did my last packet land?) remains. This is why distributed systems lean on **idempotency** ([[architecture/04-distributed-systems/10-distributed-transactions|transactions]]) instead: you can't guarantee a message arrives *exactly* once, so you make it *safe* to arrive more than once.

## FLP — consensus can't be guaranteed to terminate

**The result (Fischer, Lynch, Paterson, 1985):** in a fully **asynchronous** system where **even one node may crash**, there is *no* deterministic algorithm that guarantees [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] always **terminates**. Not "it's hard" — it's provably impossible to guarantee.

**The intuition:** in an asynchronous model you cannot distinguish a crashed node from an infinitely slow one ([[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|partial failure]]). The proof shows there's always some "bivalent" state — a state where the outcome isn't yet decided — and an adversarial scheduler can delay exactly the right message to keep the system in bivalent states forever. No crash actually has to happen; the mere *possibility* of one, plus arbitrary timing, is enough.

**Crucially, FLP is about *guaranteed termination*, not safety or usual-case behavior.** Consensus algorithms remain **always safe** (they never decide *wrong*), they just can't promise to always *finish* in bounded time. Real systems escape FLP not by breaking it but by **weakening the model**:
- **Timeouts / partial synchrony** — assume the network is *eventually* well-behaved; make progress during good periods (Raft, Paxos). This is the standard escape.
- **Randomization** — a coin flip breaks the adversary's ability to force the worst schedule; consensus terminates with probability 1 (some BFT protocols).

So FLP's practical lesson isn't "consensus is impossible" — it's "**consensus can stall during a bad network, and that's not a bug, it's a theorem.**" A cluster that stops accepting writes during a partition is FLP made visible.

## CAP — during a partition, pick C or A

**The result:** when a **network partition** (P) splits your nodes so they can't all communicate, you must choose between:
- **Consistency (C)** — every read sees the latest write (linearizable). To guarantee this during a partition, the minority side must **refuse** requests (it can't be sure it has the latest data) → you lose availability.
- **Availability (A)** — every request gets a (non-error) response. To stay available during a partition, both sides must answer from their own (possibly stale/divergent) state → you lose consistency.

You cannot have both *during a partition* — a direct consequence of unreliable networks. The famous "pick 2 of 3" framing is misleading: **partitions are not optional** (the network *will* partition), so P is a given, and the real choice is **C vs A when P happens.**

- **CP systems** (choose consistency): consensus stores (etcd, ZooKeeper, [[architecture/04-distributed-systems/09-coordination-services|Spanner]]), most SQL primaries. The minority side stops serving writes — correctness over uptime.
- **AP systems** (choose availability): [[architecture/04-distributed-systems/05-replication|Dynamo-style]] stores (Cassandra, Dynamo). Both sides keep serving, and you reconcile the divergence later ([[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]], last-write-wins) — uptime over correctness.

CAP is also **not** a whole-system label — it's per-operation. One database can offer linearizable reads for some data and eventual for other data. See the fundamentals treatment in [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]].

## PACELC — the tradeoff that never sleeps

CAP only describes the *partition* case, which is rare. **PACELC** (Abadi) completes it: **if Partition, choose Availability or Consistency; Else (normal operation), choose Latency or Consistency.**

The "else" clause is the one that bites every day: even with a perfectly healthy network, **strong consistency costs latency** — a linearizable write must reach a quorum ([[architecture/04-distributed-systems/07-consensus-and-paxos|consensus round-trip]]) before it can be acknowledged, while an eventually-consistent write can be acked by one node and propagated lazily. So:
- **PC/EC** — consistent always, paying latency in normal operation too (Spanner, most consensus systems).
- **PA/EL** — available and low-latency, giving up consistency in both cases (Dynamo, Cassandra by default).

PACELC is the more useful framework in practice, because you spend ~99.9% of your time in the **E** (no-partition) case, and that's where the consistency-vs-latency dial actually lives. "Strong consistency isn't free even when nothing is broken" is the whole point.

## The consistency/latency tradeoff is fundamental, not a limitation to engineer away

A recurring beginner instinct is "surely with a fast enough network we get strong consistency *and* low latency." No: the two are in fundamental tension because **strong consistency requires coordination** (agreeing on an order), and coordination requires communication, and communication takes time and can be interrupted. The stronger the [[architecture/04-distributed-systems/04-consistency-models|consistency model]] you promise readers, the more coordination you must do, the more latency you pay, and the less available you are under partition. Weaker models (causal, eventual) need less coordination → faster, more available, but readers see anomalies. **Choosing a consistency model is choosing a point on this curve — there is no free corner.**

## CALM — when you can drop coordination entirely

The optimistic counterweight (Hellerstein & Alvaro). **CALM: Consistency As Logical Monotonicity.** A computation can be made **consistent *without any coordination*** if and only if it is **monotonic** — roughly, once a fact becomes true it stays true, and adding more inputs only ever *adds* to the output, never retracts.

- **Monotonic** operations (set union, "has this ever happened?", grow-only counters, thresholds) can run coordination-free on every replica and always converge to the same answer — this is exactly why [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]] work.
- **Non-monotonic** operations (counting *distinct* values then deciding, "was this the *last* write?", anything that can be invalidated by later input) *require* coordination to be consistent.

CALM reframes the design question from "how do I coordinate?" to "**can I model this so it doesn't need coordination at all?**" The cheapest consensus is the one you proved you didn't need.

## How the limits map to the rest of the course

| Limit | Says you can't… | So the course does… |
|---|---|---|
| Two Generals | guarantee exactly-once delivery | idempotency + at-least-once ([[architecture/04-distributed-systems/10-distributed-transactions\|transactions]]) |
| FLP | guarantee consensus terminates (async) | partial synchrony + timeouts ([[architecture/04-distributed-systems/07-consensus-and-paxos\|Raft/Paxos]]) |
| CAP | have C and A during a partition | pick CP or AP per operation ([[architecture/04-distributed-systems/05-replication\|replication]]) |
| PACELC | have C without latency, ever | pick a [[architecture/04-distributed-systems/04-consistency-models\|consistency model]] on the curve |
| CALM | drop coordination for non-monotonic logic | model as monotonic → [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution\|CRDTs]] where possible |

## Key insight

**These aren't engineering limitations to optimize away — they're proofs of what's impossible, and every real design is a chosen point inside them.** You can't get exactly-once delivery (so you make things idempotent), you can't guarantee consensus terminates under asynchrony (so you assume eventual synchrony and accept stalls), and you can't have strong consistency without paying latency and sacrificing availability under partition (PACELC) — *unless* your logic is monotonic, in which case CALM lets you skip coordination entirely. Knowing the wall is there is what stops you running into it.

## Related
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — the models these results are proved against
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — the spectrum PACELC makes you choose from
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus & Paxos]] — what FLP bounds and timeouts rescue
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the fundamentals-level view
