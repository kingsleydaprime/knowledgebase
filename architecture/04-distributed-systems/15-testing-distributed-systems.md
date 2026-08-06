# Testing Distributed Systems

**[reference]** — from the field (Kyle Kingsbury's Jepsen, the FoundationDB and TigerBeetle simulation work, Lamport's TLA+, Netflix's chaos engineering). The capstone. Everything in this course is subtle, and the bugs live in the **rare, timing- and failure-dependent interleavings** ordinary tests never reach — a partition that heals at the *exact* wrong microsecond. This note is how the field actually catches them, and it's what separates "I read about consensus" from "I can trust my consensus code."

## The kid version first

Imagine a toy that works *perfectly* every time you play with it gently on the carpet — but breaks **only** if you drop it, on the corner, while the battery is low, at the same moment your sister bumps the table. You'll never find that bug by playing normally. You'd have to **deliberately try to break it in the meanest ways**, at the worst possible moments, over and over.

Distributed bugs are exactly like that toy. So instead of *hoping* to stumble on the bad timing, engineers:
1. **Hire a gremlin** whose *whole job* is to cut wires, pause machines, and mess up clocks at the nastiest moments — then check the rules never broke. (**Jepsen**.)
2. **Run the entire system inside a fake, controllable world** where they can replay the exact same "bad day" as many times as they want. (**Deterministic simulation**.)
3. **Break things on purpose in real life**, gently, to make sure the safety nets actually work. (**Chaos engineering**.)
4. **Prove the *design* is correct with math**, before writing any code. (**TLA+**.)

## Why normal testing fails here

A green unit-test suite tells you almost *nothing* about distributed correctness. Unit tests exercise the happy path with everything up and fast. But the bugs are in the interleavings of **[[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|partial failure]] × concurrency × timing**: a leader crashing *between* two specific messages, a partition healing *while* a client retries, a clock jumping *during* a commit. There are astronomically many such orderings, ordinary tests hit a vanishing fraction of them, and the dangerous ones are precisely the rare ones. You cannot *wait* for these — you must *force* them.

## Jepsen — empirically breaking real systems

**Jepsen** is the tool (and the body of work) that has embarrassed nearly every major distributed database. Its method:
1. **Generate** a workload of concurrent operations from many clients against the real system.
2. **Inject faults with a "nemesis"** — the gremlin — that creates [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|network partitions]], kills and restarts nodes, pauses processes, and skews [[architecture/04-distributed-systems/03-time-and-ordering|clocks]], *timed* to hit vulnerable moments.
3. **Record a history** of every operation's invocation and result (with real timestamps).
4. **Check that history against the claimed [[architecture/04-distributed-systems/04-consistency-models|consistency model]]** with a *linearizability checker* (**Knossos**, and the newer **Elle** which also finds transaction-isolation anomalies): does there exist *any* valid single-machine ordering consistent with what was observed? If not, the system violated its promise — and Jepsen produces the exact counterexample.

Jepsen's lesson for a builder: **a system's marketing claims ("we're strongly consistent!") are hypotheses until fault-injected and checked.** Reading Jepsen reports is one of the best ways to internalize how these systems really fail.

## Deterministic simulation testing — the most powerful technique

The problem with Jepsen-style testing is **reproducibility**: a bug that appears once in a million random schedules is agony to reproduce and debug. **Deterministic simulation** solves this completely:

- Run the **entire system single-threaded**, on a **simulated network and clock**, driven by a **seeded random number generator.**
- The simulation controls *everything* — message delays, reorderings, drops, process pauses, disk faults — all decided by the seed.
- So **any bug is perfectly reproducible**: the seed replays the exact same "bad day" every time. And you can **explore millions of schedules** overnight by sweeping seeds, deliberately steering toward nasty timings.

**FoundationDB** built its whole reputation this way — they wrote a deterministic simulator *first* and the database *inside it*, so they could test years of simulated failure scenarios before shipping. **TigerBeetle** does the same. It's arguably **the single most effective technique that exists** for distributed correctness — the catch is you must *design the system for it* from day one (all nondeterminism — time, randomness, I/O — routed through the simulator).

## Chaos engineering — breaking production on purpose

**Chaos engineering** (pioneered by Netflix's **Chaos Monkey**) injects *real* faults into staging or production — randomly killing instances, adding latency, cutting network links — to **verify the system degrades the way you designed it to.** The philosophy: you don't actually know your failover, retries, and [[architecture/04-distributed-systems/13-partitioning|rebalancing]] work until you've *seen* them handle a real failure. Better to trigger it at 2pm on a Tuesday with engineers watching than at 3am during a real outage. It tests the [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure-handling]] you *think* you have, end to end, including the parts (monitoring, alerts, humans) that unit tests can't reach.

## Formal methods — proving the design before coding

Everything above tests an *implementation*. **Formal methods** check the **design** itself. **TLA+** (Lamport's specification language, with the **PlusCal** front-end) lets you write a precise model of a protocol and then **model-check it** — exhaustively explore every reachable state to prove that safety properties (like "never two leaders," "committed data is never lost") *cannot* be violated. This catches **spec-level bugs before a line of code exists** — the cheapest place to fix them. **AWS uses TLA+ heavily** on services like S3 and DynamoDB and credits it with finding subtle bugs no test would have; the **Raft and Paxos** safety properties are themselves TLA+-verified. Formal methods don't prove your *code* matches the spec (that's what the testing above is for) — they prove the *plan* is sound.

## The everyday layer

Beneath the heavy artillery: **fault injection** in integration tests (kill a dependency mid-request), **property-based testing** (generate random valid inputs, assert invariants hold), and **jepsen-lite** in-house harnesses. The mindset that ties it all together: **assume every failure will happen at the worst moment, and force it in a test rather than waiting for production to force it for you.**

## Key insight

**Distributed bugs hide in rare bad timing, so you must *force* the bad timing, not wait for it.** **Jepsen** hires a fault-injecting "nemesis" and checks the recorded history against the claimed [[architecture/04-distributed-systems/04-consistency-models|consistency model]] (turning marketing claims into tested hypotheses); **deterministic simulation** (FoundationDB/TigerBeetle) runs the whole system in a seeded fake world so any bug is perfectly reproducible and millions of schedules are explorable — the most powerful technique, if you design for it; **chaos engineering** breaks real infrastructure on purpose to verify the safety nets; and **TLA+** proves the *design* correct before any code. Assume the worst-case interleaving *will* occur, and make a test cause it.

## Related
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — the partial-failure × timing bugs these hunt
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — what Jepsen's checkers verify against
- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — the edge cases you'll want to test (and TLA+-verify)
- [[architecture/05-case-studies/README|Case Studies]] — test your own Raft KV-store this way
