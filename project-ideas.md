# Project Ideas — turning notes into ability

The notes in this vault are a **map**. Projects are the **territory** — what turns "I read about it" into "I built it and can prove it." Reading is not reps; building is.

**This file is now the index.** Every course domain has its own `projects.md` sitting next to its notes, so the reps are findable from the course rather than from here.

## How to use this

- **Pick one and finish it.** One shipped project beats five half-started ones. Finishing — deployed, tested, written up — is the skill.
- **Extend your real projects where you can.** Adding CI/CD or benchmarks to something you already built is higher-signal than a toy, and faster to start → [[projects/README|projects/]].
- **Write it up.** A short README with the *why* and what you learned turns a project into portfolio signal.
- **Every entry has a *done when*.** If you can't say when a project is finished, you'll either stop early or never stop.

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

---

## The per-domain ladders

| Domain | The one to do first |
|---|---|
| [[backend/projects\|Backend]] | Load-test and fix your own p99 |
| [[frontend/projects\|Frontend]] | The same app three ways — local state, server state, RSC |
| [[databases/projects\|Databases]] | A zero-downtime migration on a live table |
| [[data-engineering/projects\|Data Engineering]] | The end-to-end mini-pipeline, then break its idempotency |
| [[architecture/projects\|Architecture]] | **A Raft key-value store** |
| [[devops/projects\|DevOps]] | Containerize and deploy one app end to end |
| [[cybersecurity/projects\|Cybersecurity]] | PortSwigger's Academy, then secure your own app |
| [[web3/projects\|Web3]] | Token and wallet from scratch, then break your own contract |
| [[ai-ml/projects\|AI & ML]] | **RAG over this vault** |
| [[foundations/projects\|Foundations]] | The regex engine — one evening, theory becomes code |
| [[languages/projects\|Languages]] | The same program in three languages |
| [[mobile/projects\|Mobile]] | Survive process death, then **ship a small app to a store** |
| [[git/projects\|Git]] | The disaster drill — an hour, and git stops being scary |
| [[hardware/projects\|Hardware]] | Rev 2 of the IoT Bridge |
| [[robotics/projects\|Robotics]] | Something moving in ROS 2 + Gazebo |
| [[game-development/projects\|Game Dev]] | Ship a game jam entry |
| [[engineering/projects\|Engineering]] | Balance a physical inverted pendulum |

---

## If you only do five

Highest signal for where you're aiming, across all four columns of [[PRIMETECHIE|the path]]:

1. 🔴 ⭐ **The order-book matching engine** (Java / systems) — below
2. 🔴 ⭐ **RAG over this vault** (AI engineering) → [[ai-ml/projects|ai-ml projects]]
3. 🔴 ⭐ **An end-to-end MLOps project** (ML engineering) → [[ai-ml/projects|ai-ml projects]]
4. 🟢 ⭐ **Containerize + deploy one app** (DevOps) → [[devops/projects|devops projects]]
5. 🟡 ⭐ **Secure your own app, then attack your own lab** (security) → [[cybersecurity/projects|cybersecurity projects]]

**Hardware is the exception** — the one column where you already have more built than written, so it needs the fewest new projects and gives the fastest returns → [[hardware/projects|hardware projects]].

---

## Java / JVM & Systems
*The low-latency / systems signal — what a firm doing market-data / FPGA work actually screens for. This is where you have the most to prove and the most upside. Kept here rather than in [[languages/projects|languages/projects]] because it's a career target, not a language tour.*

- 🟢 **Solve the concurrency exercises** — the [[languages/01-java/02-jvm-and-concurrency/exercises/README|bounded blocking queue and token-bucket rate limiter]] already have a red→green test harness. Do both — once with `synchronized`, once lock-free with `ReentrantLock`/atomics. Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|concurrency]].
- 🟡 **Lock-free ring buffer (SPSC/MPSC queue)** — a bounded ring buffer using `AtomicLong` cursors and CAS, no locks. Benchmark it against `ArrayBlockingQueue`. The canonical low-latency data structure (the LMAX Disruptor's core). Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|atomics/CAS]], [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|memory model]].
- 🔴 ⭐ **In-memory order book + matching engine** — a limit-order book (price levels, bid/ask, add/cancel/match) with a matching engine, single-threaded on the hot path for determinism. Feed it a synthetic order stream, measure throughput and p99 latency. *This is the single most on-target project for a trading firm* — it's literally the domain.
- 🟡 **Market-data feed parser** — parse a binary/CSV market-data feed (or a simplified FIX/ITCH-style format) at high throughput, zero-allocation on the hot path. Ties [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batch/streaming]] to [[languages/01-java/01-language/01-fundamentals|the language]].
- 🟡 **JMH benchmark + GC tuning study** on your record-generator pipeline — add [[languages/01-java/03-tooling/04-testing|JMH]] microbenchmarks, then run it under different collectors (Parallel vs G1 vs ZGC), capture GC logs / a JFR recording, and write up the latency-vs-throughput tradeoff. Exercises: [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]] — GC/JIT in practice, the exact thing the notes say only *doing* teaches.
- 🟢 **Add a real test suite** to one of your Java projects — JUnit + Mockito + a Testcontainers integration test against real MySQL/RabbitMQ. The projects shipped without tests; fixing that is direct engineering-maturity signal. Exercises: [[languages/01-java/03-tooling/04-testing|testing]].

---

## ⭐ Build-Your-Own — systems mastery
*The deepest reps in the vault. Each one turns a whole topic from words into bone-deep understanding.*

> **These now have full build guides in [[build-your-own-shit/README|build-your-own-shit/]]** — numbered milestones, each independently testable, with per-language toolkits and a "where to stop". Read the guide rather than this list; the entries below are the one-line pitch and the difficulty rating.

| | Guide | Why |
|---|---|---|
| 🟠 | [[build-your-own-shit/01-http-server\|HTTP server]] | **Start here.** A weekend; a real browser is the test |
| 🟠 | [[build-your-own-shit/07-your-own-shell\|Shell]] | The smallest one that teaches the most — `fork`/`exec`, fds, pipes |
| 🟠 | [[build-your-own-shit/08-your-own-container\|Container]] | ~200 lines, one evening, and Docker stops being magical |
| 🔴 | [[build-your-own-shit/02-your-own-git\|Git]] | Real Git reads your repository. Permanently demystifies it |
| 🔴 ⭐ | [[build-your-own-shit/03-your-own-redis\|Redis]] | Data structures + networking + durability. The real `redis-cli` connects |
| 🔴 | [[build-your-own-shit/04-your-own-language\|Language / interpreter]] | The deepest single lesson. → [[foundations/compilers/README\|compilers]] is the course behind it |
| 🔴 | [[build-your-own-shit/06-your-own-database\|Database]] | B-tree, SQL subset, WAL. `kill -9` mid-write and the data survives |
| 🔴 | [[build-your-own-shit/05-your-own-os\|Operating system]] | Weeks, not a weekend. Boots from a USB stick → [[foundations/os/README\|os]] |

**Not yet a guide, and the best distributed-systems project there is:**

- 🔴 ⭐ **A Raft key-value store** — [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] made real: leader election, log replication, safety, then a replicated KV store on top, tested against crashes and partitions. It forces you to confront every edge case the [[architecture/04-distributed-systems/README|theory]] describes. (MIT 6.824 labs are the gold standard.)

Pair each with a short write-up of what you learned; these are portfolio-grade signal on their own.

---

## Related
- [[build-your-own-shit/README|Build Your Own Shit]] — the sixteen full build guides
- [[BUILD-PLAN|Build Plan]] — what gets written next
- [[PRIMETECHIE|The Primetechie Path]] — where these sit as rank gates
- [[INTERVIEW|Interview Prep Index]] — the other half of proving ability
