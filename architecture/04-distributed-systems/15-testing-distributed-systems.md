---
id: 95c9ac98-bafa-41f6-b4cd-a13ae7ee46d8
---

# Testing Distributed Systems

Testing distributed systems is finding the bugs that only show up when messages arrive late, machines crash or events happen in an unlucky order. These bugs rarely show up in normal testing, so you can't wait to stumble on them. This lesson covers the methods engineers use to cause the bad timing on purpose.

## The kid version first
<!-- bite: 2bfb5fd4-cd31-4b5a-982d-34354f920b43 -->

Imagine a toy that works *perfectly* every time you play with it gently on the carpet — but breaks **only** if you drop it, on the corner, while the battery is low, at the same moment your sister bumps the table. You'll never find that bug by playing normally. You'd have to **deliberately try to break it in the meanest ways**, at the worst possible moments, over and over.

Distributed bugs are exactly like that toy. So instead of *hoping* to stumble on the bad timing, engineers:
1. **Hire a gremlin** whose *whole job* is to cut wires, pause machines, and mess up clocks at the nastiest moments — then check the rules never broke. (**Jepsen**.)
2. **Run the entire system inside a fake, controllable world** where they can replay the exact same "bad day" as many times as they want. (**Deterministic simulation**.)
3. **Break things on purpose in real life**, gently, to make sure the safety nets actually work. (**Chaos engineering**.)
4. **Prove the *design* is correct with math**, before writing any code. (**TLA+**.)

## Why normal testing fails here
<!-- bite: 5887570f-383c-403d-8e67-1759f61cb270 -->

A green unit-test suite tells you almost *nothing* about distributed correctness. Unit tests exercise the happy path with everything up and fast. But the bugs are in the interleavings of **[[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|partial failure]] × concurrency × timing**: a leader crashing *between* two specific messages, a partition healing *while* a client retries, a clock jumping *during* a commit. There are astronomically many such orderings, ordinary tests hit a vanishing fraction of them, and the dangerous ones are precisely the rare ones. You cannot *wait* for these — you must *force* them.

## Jepsen — empirically breaking real systems
<!-- bite: b02e814a-c59c-4345-8511-f8f828690d22 -->

**Jepsen** is the tool (and the body of work) that has embarrassed nearly every major distributed database. Its method:
1. **Generate** a workload of concurrent operations from many clients against the real system.
2. **Inject faults with a "nemesis"** — the gremlin — that creates [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|network partitions]], kills and restarts nodes, pauses processes, and skews [[architecture/04-distributed-systems/03-time-and-ordering|clocks]], *timed* to hit vulnerable moments.
3. **Record a history** of every operation's invocation and result (with real timestamps).
4. **Check that history against the claimed [[architecture/04-distributed-systems/04-consistency-models|consistency model]]** with a *linearizability checker* (**Knossos**, and the newer **Elle** which also finds transaction-isolation anomalies): does there exist *any* valid single-machine ordering consistent with what was observed? If not, the system violated its promise — and Jepsen produces the exact counterexample.

Jepsen's lesson for a builder: **a system's marketing claims ("we're strongly consistent!") are hypotheses until fault-injected and checked.** Reading Jepsen reports is one of the best ways to internalize how these systems really fail.

## Deterministic simulation testing — the most powerful technique
<!-- bite: 298c8335-8518-4f30-b62b-88ec147e5225 -->

The problem with Jepsen-style testing is **reproducibility**: a bug that appears once in a million random schedules is agony to reproduce and debug. **Deterministic simulation** solves this completely:

- Run the **entire system single-threaded**, on a **simulated network and clock**, driven by a **seeded random number generator.**
- The simulation controls *everything* — message delays, reorderings, drops, process pauses, disk faults — all decided by the seed.
- So **any bug is perfectly reproducible**: the seed replays the exact same "bad day" every time. And you can **explore millions of schedules** overnight by sweeping seeds, deliberately steering toward nasty timings.

**FoundationDB** built its whole reputation this way — they wrote a deterministic simulator *first* and the database *inside it*, so they could test years of simulated failure scenarios before shipping. **TigerBeetle** does the same. It's arguably **the single most effective technique that exists** for distributed correctness — the catch is you must *design the system for it* from day one (all nondeterminism — time, randomness, I/O — routed through the simulator).

## Chaos engineering — breaking production on purpose
<!-- bite: 8600921e-024f-4713-a6cc-fd3a841801bc -->

**Chaos engineering** (pioneered by Netflix's **Chaos Monkey**) injects *real* faults into staging or production — randomly killing instances, adding latency, cutting network links — to **verify the system degrades the way you designed it to.** The philosophy: you don't actually know your failover, retries, and [[architecture/04-distributed-systems/13-partitioning|rebalancing]] work until you've *seen* them handle a real failure. Better to trigger it at 2pm on a Tuesday with engineers watching than at 3am during a real outage. It tests the [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure-handling]] you *think* you have, end to end, including the parts (monitoring, alerts, humans) that unit tests can't reach.

## Formal methods — proving the design before coding
<!-- bite: 08d92930-22fa-4a8e-a423-c84a09c89771 -->

Everything above tests an *implementation*. **Formal methods** check the **design** itself. **TLA+** (Lamport's specification language, with the **PlusCal** front-end) lets you write a precise model of a protocol and then **model-check it** — exhaustively explore every reachable state to prove that safety properties (like "never two leaders," "committed data is never lost") *cannot* be violated. This catches **spec-level bugs before a line of code exists** — the cheapest place to fix them. **AWS uses TLA+ heavily** on services like S3 and DynamoDB and credits it with finding subtle bugs no test would have; the **Raft and Paxos** safety properties are themselves TLA+-verified. Formal methods don't prove your *code* matches the spec (that's what the testing above is for) — they prove the *plan* is sound.

## The everyday layer
<!-- bite: 8de00fa7-0cab-40ba-9d7a-23b1aaa82863 -->

Beneath the heavy artillery: **fault injection** in integration tests (kill a dependency mid-request), **property-based testing** (generate random valid inputs, assert invariants hold), and **jepsen-lite** in-house harnesses. The mindset that ties it all together: **assume every failure will happen at the worst moment, and force it in a test rather than waiting for production to force it for you.**

## Key insight
<!-- bite: 88f9ee2c-ef19-42e3-a9dd-4b2cca09e5cc -->

**Distributed bugs hide in rare bad timing, so you must *force* the bad timing, not wait for it.** **Jepsen** hires a fault-injecting "nemesis" and checks the recorded history against the claimed [[architecture/04-distributed-systems/04-consistency-models|consistency model]] (turning marketing claims into tested hypotheses); **deterministic simulation** (FoundationDB/TigerBeetle) runs the whole system in a seeded fake world so any bug is perfectly reproducible and millions of schedules are explorable — the most powerful technique, if you design for it; **chaos engineering** breaks real infrastructure on purpose to verify the safety nets; and **TLA+** proves the *design* correct before any code. Assume the worst-case interleaving *will* occur, and make a test cause it.

## Check your understanding
<!-- bite: a48e4607-4b8f-483a-8f26-85b5022ea77d -->

Try each one before you open the answer.

1. <!-- q: mcq id="bcd0af3f" -->
   Why does a fully green unit-test suite say little about a distributed system's correctness?

   - [ ] Unit tests are too slow
   - [x] The bugs live in rare interleavings of failures, concurrency and timing that happy-path tests never hit
   - [ ] Unit tests cannot test networking code
   - [ ] Distributed systems have no bugs at the unit level

   <details><summary>Answer</summary>

   There are astronomically many orderings, and the dangerous ones are rare. You have to force them rather than wait.

   </details>

2. <!-- q: mcq id="8d049659" -->
   In Jepsen, what is the nemesis?

   - [ ] The checker that verifies histories
   - [x] The component that injects faults: partitions, kills, pauses and clock skew
   - [ ] The client that generates the workload
   - [ ] The system under test

   <details><summary>Answer</summary>

   The nemesis is the gremlin. The recorded history is then checked against the claimed consistency model by a checker such as Knossos or Elle.

   </details>

3. <!-- q: mcq id="897dd8bb" -->
   What makes deterministic simulation testing so powerful?

   - [x] The whole system runs on a simulated network and clock driven by a seed, so any bug replays exactly from its seed
   - [ ] It runs in production
   - [ ] It proves the design with maths
   - [ ] It needs no changes to the system's design

   <details><summary>Answer</summary>

   Every failure is reproducible and you can sweep millions of seeds. The catch is designing for it from day one, routing all time, randomness and I/O through the simulator.

   </details>

4. <!-- q: gap id="7a4ecd86" answers="TLA+|TLA" -->
   Fill in the gap. Lamport's specification language, used by AWS on S3 and DynamoDB, which model-checks every reachable state of a protocol design, is ___.

   <details><summary>Answer</summary>

   TLA+. It proves the design is sound, not that the code matches it.

   </details>

5. <!-- q: mcq id="fd0f3c0a" -->
   Netflix's Chaos Monkey randomly kills instances in production. What is the goal?

   - [ ] To find spec-level bugs before coding
   - [x] To check that failover, retries and alerts really work, at a time when engineers are watching
   - [ ] To replace unit tests
   - [ ] To measure peak throughput

   <details><summary>Answer</summary>

   Better to trigger a failure at 2 pm on a Tuesday than discover the safety nets are broken at 3 am during a real outage.

   </details>

6. <!-- q: open id="605366f9" -->
   A database's website says it is "strongly consistent". How would Jepsen check that claim?

   <details><summary>Answer</summary>

   Run many concurrent client operations against the real system while a nemesis injects partitions, crashes, pauses and clock skew. Record every operation's start, end and result. Then check whether any single-machine ordering explains that history; if none does, the claim is broken and the checker shows the counterexample.

   </details>

## Related
<!-- bite: 095c457b-a615-4583-b72d-39c158c1f569 -->
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes It Hard]] — the partial-failure × timing bugs these hunt
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — what Jepsen's checkers verify against
- [[architecture/04-distributed-systems/08-raft-in-depth|Raft in Depth]] — the edge cases you'll want to test (and TLA+-verify)
- [[architecture/05-case-studies/index|Case Studies]] — test your own Raft KV-store this way

## About this lesson
<!-- bite: 3f09a522-d5d2-4e8f-9d5c-724a938d4c5d -->

**Level:** reference. **Covers:** from the field (Kyle Kingsbury's Jepsen, the FoundationDB and TigerBeetle simulation work, Lamport's TLA+, Netflix's chaos engineering). The capstone. Everything in this course is subtle, and the bugs live in the **rare, timing- and failure-dependent interleavings** ordinary tests never reach — a partition that heals at the *exact* wrong microsecond. This note is how the field actually catches them, and it's what separates "I read about consensus" from "I can trust my consensus code."
