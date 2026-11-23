---
id: e10d716f-e379-47f2-8fd8-ad61def73fd8
---

# Modern Distributed Transactions

Modern distributed transactions are newer ways of making changes across many computers that are both safe and fast, even across the whole world. Older methods made you choose between safe and slow or fast and less safe. This lesson looks at how systems built at companies like Google got both.

## The kid version first
<!-- bite: 486b3a32-3644-4018-a81c-18a5928b0fa5 -->

The last note said you can have money-safe transactions across rooms (2PC) *or* fast-and-always-available ones (sagas) — but the safe one is slow and freezes if the referee faints. For years, "go big" meant "give up the safe kind."

Then the big kids (Google) found ways to have **both** — safe *and* fast, across the *whole world*:
- **Spanner's trick:** buy **super-accurate clocks** (GPS + atomic) so every room *does* share a nearly-perfect sense of time, then use it to order transactions globally — and just **wait a few milliseconds** to be sure the clocks agree before saying "done."
- **Calvin's trick:** don't argue about order *during* the transaction — **agree on the exact order of everyone's transactions first**, then everyone runs them the same way, so there's nothing left to coordinate mid-flight.

This note is those tricks and the open-source systems (CockroachDB) that copied them.

## Google Spanner — global ACID with special clocks
<!-- bite: d54630be-01b4-41e2-93b3-af197873a808 -->

Spanner is the landmark: **serializable, externally-consistent transactions across a planet-spanning database.** How it stacks the pieces from this whole course:
- Data is **[[architecture/04-distributed-systems/13-partitioning|sharded]]** into ranges; **each shard is a [[architecture/04-distributed-systems/07-consensus-and-paxos|Paxos]] group** (replicated for fault tolerance). So the base unit is "a consensus-replicated shard."
- Cross-shard transactions use **[[architecture/04-distributed-systems/10-distributed-transactions|2PC]]**, but with each participant being a *Paxos group* (not a single fragile node), so a coordinator/participant crash doesn't block — the missing piece that made 2PC's blocking flaw survivable.
- **[[architecture/04-distributed-systems/03-time-and-ordering|TrueTime]]** gives globally-meaningful commit timestamps. Because TrueTime returns an *interval* with a bounded error, Spanner does **commit-wait** — it deliberately pauses until the commit timestamp is *definitely* in the past everywhere before releasing locks. That wait is what guarantees **external consistency** (linearizable global order): any transaction that starts after another finished is guaranteed a later timestamp.

Spanner proved global strong consistency is *achievable* — at the cost of special hardware and a few ms of commit-wait latency ([[architecture/04-distributed-systems/02-theoretical-limits|the PACELC price]], paid deliberately).

## Percolator — snapshot-isolation transactions on top of a key-value store
<!-- bite: 6da540b4-d418-4900-ad10-4a5b026e755c -->

Google's **Percolator** added multi-row **[[architecture/04-distributed-systems/10-distributed-transactions|snapshot-isolation]]** transactions on top of BigTable (which had none), to incrementally update the search index. The trick: a **client-driven 2PC using a special "primary lock"** stored *in the data itself* — one row's lock is the transaction's source of truth, and committing that primary atomically commits the whole transaction; a timestamp oracle hands out ordered timestamps for [[architecture/04-distributed-systems/10-distributed-transactions|MVCC]] snapshots. No central transaction coordinator process — the coordination is encoded in the rows. It's the template many later systems (TiDB) followed.

## Calvin — agree on the order first, then execute deterministically
<!-- bite: 4c94d1a0-af46-4320-a95d-a273490cadc0 -->

**Calvin** flips the usual model. Normal systems figure out a serial order *as a side-effect* of locking and 2PC *during* execution. Calvin instead:
1. **Runs all transactions through a [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] log first** to fix a single global order (before touching data).
2. Then **every replica executes that ordered sequence deterministically** — same order, same deterministic logic → same result, with **no commit protocol needed** (there's nothing to disagree about; the order was already agreed).

The trade: you give up some flexibility (transactions' read/write sets must be known up front) to **eliminate 2PC entirely** — a completely different point in the design space, and the root of "deterministic databases" (FaunaDB and others).

## CockroachDB / YugabyteDB — the open-source Spanner lineage
<!-- bite: 510fd7d6-d61c-4063-b0f8-c51d68750514 -->

The open-source descendants make this reachable without Google's clock hardware:
- **[[architecture/04-distributed-systems/13-partitioning|Range-sharded]]**, each range a **[[architecture/04-distributed-systems/08-raft-in-depth|Raft]] group** (Raft instead of Paxos — same idea, buildable).
- **[[architecture/04-distributed-systems/03-time-and-ordering|Hybrid Logical Clocks]]** instead of TrueTime (no atomic clocks — accept a bit more uncertainty and handle clock-skew edge cases in software).
- **Serializable isolation** by default, distributed [[architecture/04-distributed-systems/10-distributed-transactions|MVCC]], with a SQL interface. This is "Spanner you can `docker run`."

## When you *can't* have distributed ACID — sagas revisited
<!-- bite: 094207d2-d84a-4401-87d9-95990e6fb0d5 -->

Across independent [[architecture/03-architectural-patterns/04-microservices-patterns|services]] with separate databases and owners, a single distributed transaction usually isn't available or appropriate — so you fall back to **[[architecture/04-distributed-systems/10-distributed-transactions|sagas]]** (local commits + compensations + idempotency), accepting eventual consistency at the *business-workflow* boundary while using strong transactions *within* each service's own store. Knowing which boundary you're at — inside one distributed database (use its serializable transactions) vs across service boundaries (use sagas) — is the practical judgment.

## Key insight
<!-- bite: 4a9bf9f5-44f9-4c8a-acde-1e1d88731d85 -->

**"Distributed means no transactions" is obsolete — modern systems get serializable, cross-shard ACID by combining everything in this course.** Spanner = sharded Paxos groups + 2PC-over-consensus + **TrueTime commit-wait** for global external consistency; **Calvin** = agree on the order first, then execute deterministically to *skip* 2PC; **CockroachDB** = the same with Raft + HLC and no special hardware. The [[architecture/04-distributed-systems/02-theoretical-limits|PACELC]] cost is still paid — just deliberately, and bounded to a few milliseconds. Across service boundaries where distributed ACID doesn't fit, sagas remain the answer.

## Check your understanding
<!-- bite: 6f7d8b11-14fd-48bd-aeb2-343788a40d57 -->

Try each one before you open the answer.

1. <!-- q: mcq id="9688e1eb" -->
   Spanner uses 2PC across shards, yet a crash does not freeze participants. Why?

   - [ ] It never uses locks
   - [x] Each participant and the coordinator is a Paxos group, not a single node
   - [ ] It retries the prepare phase forever
   - [ ] It uses sagas instead

   <details><summary>Answer</summary>

   With every participant replicated by consensus, one machine crashing does not lose the decision, so the blocking flaw of 2PC becomes survivable.

   </details>

2. <!-- q: gap id="5aa1bc0b" answers="commit-wait|commit wait" -->
   Fill in the gap. TrueTime returns a time interval with a bounded error. Before releasing locks, Spanner pauses until the commit timestamp is definitely in the past everywhere. This pause is called ___.

   <details><summary>Answer</summary>

   Commit-wait. It costs a few milliseconds and guarantees external consistency: a transaction that starts after another finished gets a later timestamp.

   </details>

3. <!-- q: mcq id="7a556285" -->
   How does Calvin avoid a commit protocol like 2PC?

   - [x] It fixes a global order of transactions through a consensus log first, then every replica runs them deterministically in that order
   - [ ] It uses atomic clocks
   - [ ] It gives up isolation
   - [ ] It lets the client decide the order

   <details><summary>Answer</summary>

   Once the order is agreed, there is nothing to disagree about during execution. The cost is that each transaction's read and write sets must be known up front.

   </details>

4. <!-- q: mcq id="27062fae" -->
   What do CockroachDB and YugabyteDB use in place of Spanner's pieces? Choose all that apply.

   - [x] Raft instead of Paxos
   - [x] Hybrid Logical Clocks instead of TrueTime hardware
   - [ ] Sagas instead of transactions
   - [ ] Eventual consistency instead of serializability

   <details><summary>Answer</summary>

   Range shards replicated by Raft, HLC timestamps, and serializable isolation with MVCC, all without atomic clocks.

   </details>

5. <!-- q: mcq id="3b339bba" -->
   In Percolator, where does the transaction's source of truth live?

   - [ ] In a central coordinator process
   - [x] In a primary lock stored in one of the rows the transaction writes
   - [ ] In TrueTime
   - [ ] In the client's memory only

   <details><summary>Answer</summary>

   Committing the primary lock atomically commits the whole transaction. The coordination is written into the data itself.

   </details>

6. <!-- q: open id="dd69c8c2" -->
   You have one distributed SQL database inside a service, and several services that each own their own database. Where would you use serializable transactions, and where would you use sagas?

   <details><summary>Answer</summary>

   Inside the one distributed database, use its serializable transactions. Across service boundaries, with separate databases and owners, use sagas with compensations and idempotency, accepting eventual consistency for the business workflow.

   </details>

## Related
<!-- bite: 1552c035-1db8-4a02-a113-d8b3c30955db -->
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]] — the classics these build on (2PC, isolation, MVCC)
- [[architecture/04-distributed-systems/03-time-and-ordering|Time & Ordering]] — TrueTime and HLC, the clocks that make it work
- [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]] — each shard is a consensus group
- [[architecture/04-distributed-systems/13-partitioning|Partitioning]] — shard, then replicate each shard

## About this lesson
<!-- bite: ac6cf4c8-c5af-4a72-b853-a9d0697fc3e5 -->

**Level:** reference. **Covers:** from the canon (the Spanner, Percolator, and Calvin papers; the CockroachDB design docs). [[architecture/04-distributed-systems/10-distributed-transactions|Distributed transactions]] gave the classics (2PC, sagas, isolation). This note is how *modern* systems get **serializable, cross-shard transactions at scale** — the thing that made "NewSQL" possible after a decade of "going distributed means giving up transactions."
