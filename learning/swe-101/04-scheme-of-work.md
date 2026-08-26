# SWE 101 — Scheme of Work

> **Week by week.** Each week has a topic, its sub-topics, and a link straight to the chapter in this vault. Read the link, close the laptop, write the notebook page.
>
> **Week number = notebook section number.** Topic 13.4 in this file is page-marked 13.4 in the book.

**Companion files:** [[learning/swe-101/01-hire-track|Track A — Hire]] · [[learning/swe-101/02-foundation-track|why it's ordered this way]] · [[learning/swe-101/03-notebook-method|notebook method]]

---

## How to read a week

```
## Week N — Title
Read:      the chapters, in order
Topics:    N.1, N.2 …  → one notebook page each (or fewer — see the method)
DSA:       the pattern for that week, back of the book
By Sunday: what must be true before the week closes
```

**Section D (DSA) runs every single week**, two sessions, from week 1. It is never a block you finish. That is the main correction to the original scheme, where DSA sat in weeks 8–12 and went untouched for forty weeks before anyone tested it.

**Notebook layout:** index on pages 1–4 · number every page before you start · one week = one tabbed section · **Section D worked from the back of the book forward** so 30 weeks of patterns don't cut through the units · budget ≈ 160 pages.

**A link with no chapter behind it is marked ⚠️** — that topic has no coverage in the vault yet, so either skip it or it's a gap worth filling.

---

## The 30 weeks at a glance

| Weeks | Block | Depth |
|---|---|---|
| 1 | **Introduction to software engineering** & the audit | Skim |
| 2–4 | Software design | **Write** |
| 5–8 | Architecture & system design | **Write** |
| 9–11 | Databases | **Write** |
| 12–15 | Networking & the web | **Write** |
| 16–17 | Security | **Write** |
| 18–19 | Backend consolidation | Reconstruct |
| 20–23 | AI engineering | **Write** |
| 24 | Testing & quality | Gap-fill |
| 25 | DevOps & delivery | Gap-fill |
| 26–29 | Concurrency & distributed systems | **Write** |
| 30 | Review & mock loops | — |
| 31+ | The CS spine | Ongoing |
| **D** | **DSA — every week, weeks 1–30** | **Write** |

*"Reconstruct" = you've shipped it; write from memory, then diff against your code. "Gap-fill" = read the chapter, write only what surprised you. Week 1's audit sets these.*

---

---

---

---

## Contents

**This doubles as the notebook index.** The header says *week number = notebook section number* and *index on pages 1–4* — this is what goes on those pages. Topic `13.4` here is page-marked 13.4 in the book.

**Generated, not hand-written** — run `python3 learning/swe-101/scripts/generate-contents.py` after editing any week. Edit a week, regenerate, never both.

<!-- CONTENTS:START -->

**Week 1 · Introduction**

- **1 — Introduction to Software Engineering, and the audit**  ·  *D1*
    - `1.1` Programming vs engineering; where the time actually goes
    - `1.2` The SDLC: requirements → design → implementation → testing → deployment → maintenance, **and what breaks when each is skipped**
    - `1.3` The engineering roles — and the honest way to tell them apart (*the failure you fear*)
    - `1.4` Abstraction, decomposition, trade-offs
    - `1.5` **The audit**

**Weeks 2–4 · Software design**

- **2 — Design principles**  ·  *D2*
    - `2.1` Modularity — what a module is, and what makes a bad one
    - `2.2` Coupling and cohesion
    - `2.3` Abstraction and interfaces
    - `2.4` Separation of concerns
    - `2.5` DRY, KISS, YAGNI — **and where each one is wrong**
    - `2.6` SOLID, one letter at a time — **and when it's over-engineering**
    - `2.7` Composition over inheritance
- **3 — Design patterns**  ·  *D3*
    - `3.1` Creational — factory, builder, **and why singleton is usually a mistake**
    - `3.2` Structural — adapter, decorator, facade, proxy
    - `3.3` Behavioural — strategy, observer, command, state
    - `3.4` Dependency injection and wiring
- **4 — Structuring a codebase**  ·  *D4*
    - `4.1` Layers: controllers, services, repositories
    - `4.2` Organising by layer vs by feature
    - `4.3` Hexagonal and clean architecture
    - `4.4` Modular monolith → services, and when to split

**Weeks 5–8 · Architecture & system design**

- **5 — How to approach system design**  ·  *D5*
    - `5.1` The sequence, so you never freeze
    - `5.2` Functional vs non-functional requirements
    - `5.3` Back-of-envelope estimation
    - `5.4` Scalability and performance, vertical vs horizontal
- **6 — Availability, caching, load balancing**  ·  *D6*
    - `6.1` Availability, reliability, what "three nines" actually costs
    - `6.2` CAP and consistency
    - `6.3` Load balancing, proxies, reverse proxies
    - `6.4` Caching, and cache invalidation
- **7 — Data, messaging, communication**  ·  *D7*
    - `7.1` Databases at scale
    - `7.2` Messaging and async
    - `7.3` REST, gRPC, GraphQL, WebSockets
- **8 — Architectural patterns and trade-offs**  ·  *D8*
    - `8.1` Monolith vs microservices vs serverless
    - `8.2` Resilience: timeouts, retries, backoff, circuit breakers, bulkheads
    - `8.3` Data and integration patterns
    - `8.4` Microservices patterns
    - `8.5` **Trade-off articulation** — saying "I'd choose X because Y" instead of "it depends"

**Weeks 9–11 · Databases**

- **9 — The relational model and SQL**  ·  *D9*
    - `9.1` What a database actually is
    - `9.2` The relational model — tables, rows, keys, relationships
    - `9.3` Normalisation, and when to denormalise on purpose
    - `9.4` SQL: SELECT, JOIN, GROUP BY, aggregates, subqueries, CTEs
- **10 — Database internals**  ·  *D10*
    - `10.1` Storage and page layout
    - `10.2` B-trees and indexes
    - `10.3` LSM trees, and why new engines choose them
    - `10.4` The query pipeline
    - `10.5` Join algorithms and the optimiser
    - `10.6` **`EXPLAIN ANALYZE` — estimated vs actual rows as *the* diagnostic**
- **11 — Transactions, durability, operations**  ·  *D11*
    - `11.1` Transactions and ACID
    - `11.2` Isolation levels and MVCC
    - `11.3` Durability, the WAL, recovery
    - `11.4` Replication and scaling — *"replication is not a backup"*
    - `11.5` Operating: migrations, `lock_timeout`, pooling, backups

**Weeks 12–15 · Networking & the web**

- **12 — The network and IP**  ·  *D12*
    - `12.1` What a network is; the layered model
    - `12.2` The link layer, MAC addresses
    - `12.3` IP addressing and subnetting
    - `12.4` Routing
- **13 — TCP and UDP**  ·  *D13*
    - `13.1` UDP and ports
    - `13.2` TCP connection lifecycle — handshake, teardown, states
    - `13.3` Reliability and flow control
    - `13.4` Congestion control
    - `13.5` Sockets and the network API
- **14 — DNS, HTTP, TLS**  ·  *D14*
    - `14.1` DNS in depth
    - `14.2` HTTP and its evolution — 1.1, 2, 3
    - `14.3` TLS and transport security
    - `14.4` QUIC
    - `14.5` Cookies, sessions, headers
- **15 — The edge, performance, debugging**  ·  *D15a*
    - `15.1` NAT, firewalls, middleboxes
    - `15.2` Proxies, reverse proxies, CDNs
    - `15.3` Latency vs bandwidth, RTT, head-of-line blocking
    - `15.4` Debugging: `dig`, `curl -v`, `ss`, `tcpdump`

**Weeks 16–17 · Security**

- **16 — Identity: authentication and authorisation**  ·  *D15b*
    - `16.1` Authentication vs authorisation
    - `16.2` Password hashing — bcrypt/argon2, **and why not SHA-256**
    - `16.3` Sessions vs JWT, **and when JWT is the wrong choice**
    - `16.4` OAuth 2.0 / OIDC
    - `16.5` Least privilege
- **17 — Attacks and defences**  ·  *mixed review begins — 5 problems/week, patterns drawn at random. **This is what interviews actually are.***
    - `17.1` Input validation and output encoding
    - `17.2` Injection: SQL, command, template
    - `17.3` XSS, CSRF, SSRF
    - `17.4` Security headers and same-origin policy
    - `17.5` Symmetric, asymmetric, signatures, PKI
    - `17.6` TLS in practice
    - `17.7` Secrets management
    - `17.8` **Prompt injection and LLM-specific risk**

**Weeks 18–19 · Backend consolidation**

- **18 — Backend: the request path**  ·  *mixed review, 5 problems*
    - `18.1` What a backend is
    - `18.2` HTTP servers; rate limiting at the edge
    - `18.3` The request lifecycle end to end
    - `18.4` Runtime and concurrency models — **the Node event loop**
    - `18.5` REST design and resource modelling
    - `18.6` ⚠️ API versioning — *no dedicated chapter; thin coverage only*
- **19 — Backend: cross-cutting concerns**  ·  *mixed review, 5 problems*
    - `19.1` Validation, error handling, error contracts
    - `19.2` Rate limiting
    - `19.3` Structured logging and configuration
    - `19.4` Databases in the backend; pooling, migrations
    - `19.5` Background jobs and queues
    - `19.6` Idempotency
    - `19.7` Caching layers

**Weeks 20–23 · AI engineering**

- **20 — LLMs: the ground floor**  ·  *mixed review, 5 problems*
    - `20.1` What the role actually is
    - `20.2` How LLMs work — enough to reason about *why* they fail
    - `20.3` The model landscape
    - `20.4` Calling models: streaming, tokens, temperature, context windows
- **21 — Prompting, structure, retrieval**  ·  *mixed review, 5 problems*
    - `21.1` Prompt engineering; prompts as versioned artifacts
    - `21.2` Structured output
    - `21.3` RAG and embeddings — chunking, hybrid search, reranking
- **22 — Tools and agents**  ·  *mixed review, 5 problems*
    - `22.1` Tools and MCP
    - `22.2` Agents, **and when not to use one**
    - `22.3` Multimodal
- **23 — Evals and production ⭐**  ·  *mixed review, 5 problems*
    - `23.1` **Evals — golden sets, scorers, regression runs in CI**
    - `23.2` Reliability and plumbing — retries, fallbacks, timeouts
    - `23.3` Cost, caching, latency
    - `23.4` Safety in production — PII, output filtering
    - `23.5` Practice

**Week 24 · Testing & quality**

- **24 — Testing and quality**  ·  *mixed review, 5 problems*
    - `24.1` The pyramid: unit, integration, e2e
    - `24.2` Test doubles: stub, mock, fake, spy
    - `24.3` **What not to test**; flaky tests
    - `24.4` Code review, giving and receiving
    - `24.5` Observability: logs, metrics, traces

**Week 25 · DevOps & delivery**

- **25 — DevOps and delivery**  ·  *mixed review, 5 problems*
    - `25.1` Docker — layers, caching, multi-stage
    - `25.2` CI/CD concepts
    - `25.3` CI pipelines — what runs on every push
    - `25.4` CD, deployment strategies, releases
    - `25.5` Pipeline security and secrets
    - `25.6` Troubleshooting workflows

**Weeks 26–29 · Concurrency & distributed systems**

- **26 — Concurrency**  ·  *mixed review + **first timed mock**, 45 min, unseen medium*
    - `26.1` Processes vs threads
    - `26.2` Scheduling
    - `26.3` Concurrency vs parallelism; **the Node event loop**
    - `26.4` Locks, mutexes, deadlock, race conditions
- **27 — What makes distributed systems hard**  ·  *mixed + timed mock*
    - `27.1` What makes them hard
    - `27.2` Theoretical limits
    - `27.3` Time and ordering — **why you can't trust clocks**
    - `27.4` Consistency models
- **28 — Replication, partitioning, consensus**  ·  *mixed + timed mock*
    - `28.1` Replication
    - `28.2` Partitioning and sharding
    - `28.3` Consensus
    - `28.4` Raft
- **29 — Transactions, logs, failure**  ·  *mixed + timed mock*
    - `29.1` Distributed transactions and saga
    - `29.2` The log and event-driven architecture
    - `29.3` Idempotency and retry storms
    - `29.4` Failure detection
    - `29.5` Testing distributed systems

**Week 30 · Review**

- **30 — Review and mock loops**
    - `30.1` Full system-design mock: **ride-sharing**, then **video platform**
    - `30.2` Two timed coding mocks
    - `30.3` The project story — 2 minutes, 5 minutes, 20 minutes of depth
    - `30.4` Behavioural — six STAR stories from real projects
    - `30.5` Re-audit weeks 2–29; anything still *don't know it* gets a fortnight

**Week 31+ · The CS spine**

- **31 — The CS spine (ongoing)**
    - `31.1` How a program runs — compile, link, load
    - `31.2` Memory: stack, heap, process layout
    - `31.3` Virtual memory and the MMU
    - `31.4` The memory hierarchy and caches
    - `31.5` Syscalls and the kernel boundary
    - `31.6` Complexity classes, P vs NP — **knowing when to stop looking**
    - `31.7` Automata — why regexes and parsers look the way they do
    - `31.8` Compilers: lexer → parser → IR → codegen
    - `31.9` Garbage collection
    - `31.10` Why one O(n) loop is 30× slower than another

*153 topics across 31 weeks. Generated from the weeks below — regenerate rather than hand-edit.*

<!-- CONTENTS:END -->
---

# Week 1 — Introduction to Software Engineering, and the audit

**Read:** [[foundations/software-engineering/README|Introduction to Software Engineering]] (01–03) · [[projects/README|projects/README]] — what you've already built and which domains it exercises

**Topics**
- **1.1** Programming vs engineering; where the time actually goes → [[foundations/software-engineering/01-what-software-engineering-is|01]]
- **1.2** The SDLC: requirements → design → implementation → testing → deployment → maintenance, **and what breaks when each is skipped** → [[foundations/software-engineering/02-the-software-development-lifecycle|02]]
- **1.3** The engineering roles — and the honest way to tell them apart (*the failure you fear*) → [[foundations/software-engineering/03-the-engineering-roles|03]]
- **1.4** Abstraction, decomposition, trade-offs → [[foundations/software-engineering/01-what-software-engineering-is|01]] · [[PRIMETECHIE|PRIMETECHIE]] frames the whole vault this way
- **1.5** **The audit** → [[learning/swe-101/05-week-1-audit|the checklist]] — mark every topic in weeks 2–30 *know it / half know it / don't know it*

**DSA:** D1 → [[foundations/dsa/06-patterns/01-prefix-sum|Prefix sum]]

**By Sunday:** the audit is done, and "What is a software engineer?" is written in your own words, one page, nothing open.

> **This gap is now closed.** Topics 1.1–1.3 had no chapter — the vault is written for practitioners and never wrote down what the profession *is*. [[foundations/software-engineering/README|foundations/software-engineering/]] was written to fill exactly this week. It's deliberately short: you're twelve projects deep, so most of it will confirm what you already know by doing, and its real value is vocabulary. **1.5 is still the actual deliverable of the week.**

---

# Week 2 — Design principles

**Read:** [[concepts/04-best-practices/01-clean-code|clean code]] · [[concepts/04-best-practices/05-solid-principles|SOLID principles]]

**Topics**
- **2.1** Modularity — what a module is, and what makes a bad one → [[concepts/04-best-practices/01-clean-code|clean code]]
- **2.2** Coupling and cohesion → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]]
- **2.3** Abstraction and interfaces → [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal & clean architecture]]
- **2.4** Separation of concerns → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|by layer vs by feature]]
- **2.5** DRY, KISS, YAGNI — **and where each one is wrong** → [[concepts/04-best-practices/01-clean-code|clean code]]
- **2.6** SOLID, one letter at a time — **and when it's over-engineering** → [[concepts/04-best-practices/05-solid-principles|SOLID principles]]
- **2.7** Composition over inheritance → [[concepts/03-design-patterns/02-structural-patterns|structural patterns]]

**DSA:** D2 → [[foundations/dsa/06-patterns/02-two-pointers|Two pointers]]

**By Sunday:** closed-book — *name three places in your own code where coupling hurt you.*

---

# Week 3 — Design patterns

**Read:** [[concepts/03-design-patterns/README|design patterns]], all three chapters

**Topics**
- **3.1** Creational — factory, builder, **and why singleton is usually a mistake** → [[concepts/03-design-patterns/01-creational-patterns|creational]]
- **3.2** Structural — adapter, decorator, facade, proxy → [[concepts/03-design-patterns/02-structural-patterns|structural]]
- **3.3** Behavioural — strategy, observer, command, state → [[concepts/03-design-patterns/03-behavioral-patterns|behavioural]]
- **3.4** Dependency injection and wiring → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|DI & wiring]]

**DSA:** D3 → [[foundations/dsa/06-patterns/03-sliding-window|Sliding window]]

**By Sunday:** closed-book — *pick three patterns; for each, the problem it solves and what it costs you.*

---

# Week 4 — Structuring a codebase

**Read:** [[backend/03-structuring-a-backend/README|structuring a backend]], all five chapters

**Topics**
- **4.1** Layers: controllers, services, repositories → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]]
- **4.2** Organising by layer vs by feature → [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|by layer vs feature]]
- **4.3** Hexagonal and clean architecture → [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal]]
- **4.4** Modular monolith → services, and when to split → [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith]]

**DSA:** D4 → [[foundations/dsa/06-patterns/04-fast-slow-pointers|Fast & slow pointers]]

**By Sunday:** **Design a banking system. Don't code it.** Entities, relationships, responsibilities, interfaces, data, failures, security, scalability. *(Your original exercise, kept — it's the best one in the document, and "don't code it" is what makes it work.)*

---

# Week 5 — How to approach system design

**Read:** [[architecture/01-system-design-fundamentals/README|system design fundamentals]] 01–02

**Topics**
- **5.1** The sequence, so you never freeze → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|how to approach it]]
- **5.2** Functional vs non-functional requirements → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|same chapter]]
- **5.3** Back-of-envelope estimation → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|same chapter]]
- **5.4** Scalability and performance, vertical vs horizontal → [[architecture/01-system-design-fundamentals/02-scalability-and-performance|scalability]]

**DSA:** D5 → [[foundations/dsa/06-patterns/05-linked-list-reversal|Linked list reversal]]

**By Sunday:** design a **URL shortener** on the board, 45 minutes, out loud, *before* reading anything. Then compare and write only the gap.

---

# Week 6 — Availability, caching, load balancing

**Read:** [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability]] · [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP]] · [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancing]] · [[architecture/02-building-blocks/02-caching|caching]]

**Topics**
- **6.1** Availability, reliability, what "three nines" actually costs → [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability]]
- **6.2** CAP and consistency → [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP]]
- **6.3** Load balancing, proxies, reverse proxies → [[architecture/02-building-blocks/01-load-balancing-and-proxies|LB & proxies]]
- **6.4** Caching, and cache invalidation → [[architecture/02-building-blocks/02-caching|caching]]

**DSA:** D6 → [[foundations/dsa/06-patterns/06-monotonic-stack|Monotonic stack]]

**By Sunday:** design a **chat application**.

---

# Week 7 — Data, messaging, communication

**Read:** [[architecture/02-building-blocks/03-databases-at-scale|databases at scale]] · [[architecture/02-building-blocks/04-messaging-and-async|messaging]] · [[architecture/02-building-blocks/05-communication|communication]]

**Topics**
- **7.1** Databases at scale → [[architecture/02-building-blocks/03-databases-at-scale|at scale]]
- **7.2** Messaging and async → [[architecture/02-building-blocks/04-messaging-and-async|messaging]]
- **7.3** REST, gRPC, GraphQL, WebSockets → [[architecture/02-building-blocks/05-communication|communication]]

**DSA:** D7 → [[foundations/dsa/06-patterns/07-top-k-elements|Top-K elements]]

**By Sunday:** design a **notification system**. You have real RabbitMQ reps — this one should come from experience.

---

# Week 8 — Architectural patterns and trade-offs

**Read:** [[architecture/03-architectural-patterns/README|architectural patterns]] 01–04 · [[architecture/interview/01-system-design-round|the interview round]]

**Topics**
- **8.1** Monolith vs microservices vs serverless → [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|the three]]
- **8.2** Resilience: timeouts, retries, backoff, circuit breakers, bulkheads → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience]]
- **8.3** Data and integration patterns → [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data & integration]]
- **8.4** Microservices patterns → [[architecture/03-architectural-patterns/04-microservices-patterns|microservices]]
- **8.5** **Trade-off articulation** — saying "I'd choose X because Y" instead of "it depends" → [[architecture/interview/01-system-design-round|the round]]

**DSA:** D8 → [[foundations/dsa/06-patterns/08-overlapping-intervals|Overlapping intervals]]

**By Sunday:** design a **payment system**. Do this one carefully — you built a payments ledger in nextvibe and a direct-debit sandbox in Java, and interviewers can hear the difference between experience and theory.

---

# Week 9 — The relational model and SQL

**Read:** [[databases/01-what-a-database-is|what a database is]] · [[databases/02-the-relational-model|the relational model]] · [[databases/sql-reference|SQL reference]] · [[databases/database-design-reference|design reference]]

**Topics**
- **9.1** What a database actually is → [[databases/01-what-a-database-is|01]]
- **9.2** The relational model — tables, rows, keys, relationships → [[databases/02-the-relational-model|02]]
- **9.3** Normalisation, and when to denormalise on purpose → [[databases/database-design-reference|design reference]]
- **9.4** SQL: SELECT, JOIN, GROUP BY, aggregates, subqueries, CTEs → [[databases/sql-reference|SQL reference]]

**DSA:** D9 → [[foundations/dsa/06-patterns/09-modified-binary-search|Modified binary search]]

**By Sunday:** closed-book — *draw the schema of one of your own projects from memory, then diff it against the real one.*

---

# Week 10 — Database internals

**Read:** [[databases/03-storage-and-page-layout|storage]] · [[databases/04-b-trees-and-indexes|B-trees]] · [[databases/05-lsm-trees|LSM]] · [[databases/06-the-query-pipeline|query pipeline]] · [[databases/07-join-algorithms-and-the-optimiser|joins & optimiser]]

**Topics**
- **10.1** Storage and page layout → [[databases/03-storage-and-page-layout|03]]
- **10.2** B-trees and indexes → [[databases/04-b-trees-and-indexes|04]]
- **10.3** LSM trees, and why new engines choose them → [[databases/05-lsm-trees|05]]
- **10.4** The query pipeline → [[databases/06-the-query-pipeline|06]]
- **10.5** Join algorithms and the optimiser → [[databases/07-join-algorithms-and-the-optimiser|07]]
- **10.6** **`EXPLAIN ANALYZE` — estimated vs actual rows as *the* diagnostic** → [[databases/07-join-algorithms-and-the-optimiser|07]]

**DSA:** D10 → [[foundations/dsa/06-patterns/10-binary-tree-traversal-pattern|Binary tree traversal]]

**By Sunday:** take a genuinely slow query from a real project, `EXPLAIN ANALYZE` it, fix it, record before/after and *why*.

---

# Week 11 — Transactions, durability, operations

**Read:** [[databases/08-transactions-and-acid|ACID]] · [[databases/09-mvcc-and-concurrency-control|MVCC]] · [[databases/10-durability-and-recovery|durability]] · [[databases/11-replication-and-scaling|replication]] · [[databases/12-operating-a-database|operations]]

**Topics**
- **11.1** Transactions and ACID → [[databases/08-transactions-and-acid|08]]
- **11.2** Isolation levels and MVCC → [[databases/09-mvcc-and-concurrency-control|09]]
- **11.3** Durability, the WAL, recovery → [[databases/10-durability-and-recovery|10]]
- **11.4** Replication and scaling — *"replication is not a backup"* → [[databases/11-replication-and-scaling|11]]
- **11.5** Operating: migrations, `lock_timeout`, pooling, backups → [[databases/12-operating-a-database|12]]

**DSA:** D11 → [[foundations/dsa/06-patterns/11-dfs-pattern|DFS]]

**By Sunday:** closed-book — *why does adding an index sometimes make things slower?*

---

# Week 12 — The network and IP

**Read:** [[foundations/networking/01-what-a-network-is|01]] → [[foundations/networking/04-routing|04]]

**Topics**
- **12.1** What a network is; the layered model → [[foundations/networking/01-what-a-network-is|01]]
- **12.2** The link layer, MAC addresses → [[foundations/networking/02-the-link-layer|02]]
- **12.3** IP addressing and subnetting → [[foundations/networking/03-ip-addressing-and-subnetting|03]]
- **12.4** Routing → [[foundations/networking/04-routing|04]]

**DSA:** D12 → [[foundations/dsa/06-patterns/12-bfs-pattern|BFS]]

**By Sunday:** subnet a /24 by hand, no calculator.

---

# Week 13 — TCP and UDP

**Read:** [[foundations/networking/05-udp-and-ports|05]] → [[foundations/networking/09-sockets-and-the-network-api|09]]

**Topics**
- **13.1** UDP and ports → [[foundations/networking/05-udp-and-ports|05]]
- **13.2** TCP connection lifecycle — handshake, teardown, states → [[foundations/networking/06-tcp-connection-lifecycle|06]]
- **13.3** Reliability and flow control → [[foundations/networking/07-tcp-reliability-and-flow-control|07]]
- **13.4** Congestion control → [[foundations/networking/08-congestion-control|08]]
- **13.5** Sockets and the network API → [[foundations/networking/09-sockets-and-the-network-api|09]]

**DSA:** D13 → [[foundations/dsa/06-patterns/13-matrix-traversal|Matrix traversal]]

**By Sunday:** closed-book — *draw the TCP state machine for a connection that opens, transfers, and closes.*

---

# Week 14 — DNS, HTTP, TLS

**Read:** [[foundations/networking/10-dns-in-depth|10]] → [[foundations/networking/13-quic-and-modern-transport|13]]

**Topics**
- **14.1** DNS in depth → [[foundations/networking/10-dns-in-depth|10]]
- **14.2** HTTP and its evolution — 1.1, 2, 3 → [[foundations/networking/11-http-evolution|11]]
- **14.3** TLS and transport security → [[foundations/networking/12-tls-and-transport-security|12]]
- **14.4** QUIC → [[foundations/networking/13-quic-and-modern-transport|13]]
- **14.5** Cookies, sessions, headers → [[backend/05-auth/01-authentication-flows|auth flows]]

**DSA:** D14 → [[foundations/dsa/06-patterns/14-backtracking|Backtracking]]

**By Sunday:** **"What actually happens when I type google.com?"** — one page, from memory. This is the question that gets asked.

---

# Week 15 — The edge, performance, debugging

**Read:** [[foundations/networking/14-nat-firewalls-and-middleboxes|14]] → [[foundations/networking/16-debugging-networks|16]]

**Topics**
- **15.1** NAT, firewalls, middleboxes → [[foundations/networking/14-nat-firewalls-and-middleboxes|14]]
- **15.2** Proxies, reverse proxies, CDNs → [[architecture/02-building-blocks/01-load-balancing-and-proxies|LB & proxies]]
- **15.3** Latency vs bandwidth, RTT, head-of-line blocking → [[foundations/networking/15-network-performance|15]]
- **15.4** Debugging: `dig`, `curl -v`, `ss`, `tcpdump` → [[foundations/networking/16-debugging-networks|16]]

**DSA:** D15a → [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic programming]], part 1

**By Sunday:** rewrite the google.com answer and diff it against week 14's version.

---

# Week 16 — Identity: authentication and authorisation

**Read:** [[backend/05-auth/README|auth]] 01–03 · [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]]

**Topics**
- **16.1** Authentication vs authorisation → [[backend/05-auth/01-authentication-flows|flows]] · [[backend/05-auth/02-authorization|authz]]
- **16.2** Password hashing — bcrypt/argon2, **and why not SHA-256** → [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing]]
- **16.3** Sessions vs JWT, **and when JWT is the wrong choice** → [[backend/05-auth/01-authentication-flows|flows]]
- **16.4** OAuth 2.0 / OIDC → [[backend/05-auth/03-oauth-provider-integrations|OAuth]]
- **16.5** Least privilege → [[backend/05-auth/02-authorization|authz]]

**DSA:** D15b → [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic programming]], part 2

**By Sunday:** closed-book — *draw your flagship's full auth flow, including refresh and logout.*

---

# Week 17 — Attacks and defences

**Read:** [[cybersecurity/04-web-security/README|web security]] 01–04 · [[cybersecurity/05-cryptography/README|cryptography]] 01–06

**Topics**
- **17.1** Input validation and output encoding → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|01]]
- **17.2** Injection: SQL, command, template → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|01]]
- **17.3** XSS, CSRF, SSRF → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|headers & SOP]]
- **17.4** Security headers and same-origin policy → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|04]]
- **17.5** Symmetric, asymmetric, signatures, PKI → [[cybersecurity/05-cryptography/02-symmetric-encryption|02]] · [[cybersecurity/05-cryptography/04-asymmetric-encryption|04]] · [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|05]]
- **17.6** TLS in practice → [[cybersecurity/04-web-security/03-https-and-tls|HTTPS & TLS]]
- **17.7** Secrets management → [[devops/09-secret-management/01-secret-management|secrets]]
- **17.8** **Prompt injection and LLM-specific risk** → [[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]

**DSA:** mixed review begins — 5 problems/week, patterns drawn at random. **This is what interviews actually are.**

**By Sunday:** threat-model your flagship. Top five risks, and what you did about each.

---

# Week 18 — Backend: the request path

**Read:** [[backend/01-foundations/README|backend foundations]] 01–04 · [[backend/02-api-design/01-apis-and-rest|APIs & REST]]

**Depth: reconstruct.** Write from memory first, then diff against your own code. The diff is the lesson.

**Topics**
- **18.1** What a backend is → [[backend/01-foundations/01-what-a-backend-is|01]]
- **18.2** HTTP servers; rate limiting at the edge → [[backend/01-foundations/02-http-servers|02]]
- **18.3** The request lifecycle end to end → [[backend/01-foundations/03-the-request-lifecycle|03]]
- **18.4** Runtime and concurrency models — **the Node event loop** → [[backend/01-foundations/04-runtime-and-concurrency-models|04]]
- **18.5** REST design and resource modelling → [[backend/02-api-design/01-apis-and-rest|APIs & REST]]
- **18.6** ⚠️ API versioning — *no dedicated chapter; thin coverage only*

**DSA:** mixed review, 5 problems

**By Sunday:** closed-book — *draw the complete path of one request through your flagship, including every failure point.*

---

# Week 19 — Backend: cross-cutting concerns

**Read:** [[backend/07-practices/01-backend-best-practices|best practices]] · [[backend/07-practices/02-testing-a-backend|testing a backend]] · [[backend/04-data-and-persistence/01-databases-in-the-backend|persistence]]

**Topics**
- **19.1** Validation, error handling, error contracts → [[backend/07-practices/01-backend-best-practices|practices]]
- **19.2** Rate limiting → [[backend/07-practices/01-backend-best-practices|practices]]
- **19.3** Structured logging and configuration → [[backend/07-practices/01-backend-best-practices|practices]]
- **19.4** Databases in the backend; pooling, migrations → [[backend/04-data-and-persistence/01-databases-in-the-backend|persistence]]
- **19.5** Background jobs and queues → [[architecture/02-building-blocks/04-messaging-and-async|messaging & async]]
- **19.6** Idempotency → [[concepts/interview/01-apis-auth-and-practices|APIs, auth & practices]]
- **19.7** Caching layers → [[architecture/02-building-blocks/02-caching|caching]]

**DSA:** mixed review, 5 problems

**By Sunday:** write your flagship's API documentation from memory, then check it and note every gap.

> ⚠️ **`backend/06-cross-cutting/` is a README with no chapters.** Several topics here are covered from `07-practices` and `architecture/` instead. That's the thinnest corner of the vault this course leans on.

---

# Week 20 — LLMs: the ground floor

**Read:** [[ai-ml/03-ai-engineer/README|the AI engineer track]] 01–04

**Topics**
- **20.1** What the role actually is → [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|01]]
- **20.2** How LLMs work — enough to reason about *why* they fail → [[ai-ml/03-ai-engineer/02-how-llms-work|02]]
- **20.3** The model landscape → [[ai-ml/03-ai-engineer/03-the-model-landscape|03]]
- **20.4** Calling models: streaming, tokens, temperature, context windows → [[ai-ml/03-ai-engineer/04-calling-models|04]]

**DSA:** mixed review, 5 problems

**By Sunday:** closed-book — *why does a model hallucinate, mechanically?*

---

# Week 21 — Prompting, structure, retrieval

**Read:** [[ai-ml/03-ai-engineer/05-prompt-engineering|05]] · [[ai-ml/03-ai-engineer/11-structured-output|11]] · [[ai-ml/03-ai-engineer/06-rag-and-embeddings|06]]

**Topics**
- **21.1** Prompt engineering; prompts as versioned artifacts → [[ai-ml/03-ai-engineer/05-prompt-engineering|05]]
- **21.2** Structured output → [[ai-ml/03-ai-engineer/11-structured-output|11]]
- **21.3** RAG and embeddings — chunking, hybrid search, reranking → [[ai-ml/03-ai-engineer/06-rag-and-embeddings|06]]

**DSA:** mixed review, 5 problems

**By Sunday:** closed-book — *your RAG returns the wrong chunk. List the six things that could be causing it.*

---

# Week 22 — Tools and agents

**Read:** [[ai-ml/03-ai-engineer/07-tools-and-mcp|07]] · [[ai-ml/03-ai-engineer/08-agents|08]] · [[ai-ml/03-ai-engineer/09-multimodal|09]]

**Topics**
- **22.1** Tools and MCP → [[ai-ml/03-ai-engineer/07-tools-and-mcp|07]]
- **22.2** Agents, **and when not to use one** → [[ai-ml/03-ai-engineer/08-agents|08]]
- **22.3** Multimodal → [[ai-ml/03-ai-engineer/09-multimodal|09]]

**DSA:** mixed review, 5 problems

**By Sunday:** closed-book — *when is an agent the wrong architecture?*

---

# Week 23 — Evals and production ⭐

**Read:** [[ai-ml/03-ai-engineer/12-evals|12 — evals]] · [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|13]] · [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|14]] · [[ai-ml/03-ai-engineer/10-safety-and-production|10]]

**Topics**
- **23.1** **Evals — golden sets, scorers, regression runs in CI** → [[ai-ml/03-ai-engineer/12-evals|12]]
- **23.2** Reliability and plumbing — retries, fallbacks, timeouts → [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|13]]
- **23.3** Cost, caching, latency → [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|14]]
- **23.4** Safety in production — PII, output filtering → [[ai-ml/03-ai-engineer/10-safety-and-production|10]]
- **23.5** Practice → [[ai-ml/03-ai-engineer/19-practice-exercises|exercises]] · [[ai-ml/03-ai-engineer/20-practice-exercises-solutions|solutions]]

**DSA:** mixed review, 5 problems

**By Sunday:** **the evals harness for your flagship is running in CI, with numbers you can quote.**

> **23.1 is the highest-leverage topic in this entire scheme.** Twelve projects, two incidental mentions of evals. It's what separates "built a chatbot" from "AI engineer", and it's half your job target.

---

# Week 24 — Testing and quality

**Read:** [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] · [[backend/07-practices/02-testing-a-backend|testing a backend]] · [[concepts/04-best-practices/02-pr-structure|PR structure]] · [[devops/10-observability/01-observability-fundamentals|observability]]

**Depth: gap-fill.** Read, write only what surprised you.

**Topics**
- **24.1** The pyramid: unit, integration, e2e → [[concepts/04-best-practices/04-testing-fundamentals|fundamentals]]
- **24.2** Test doubles: stub, mock, fake, spy → [[concepts/04-best-practices/04-testing-fundamentals|fundamentals]]
- **24.3** **What not to test**; flaky tests → [[backend/07-practices/02-testing-a-backend|testing a backend]]
- **24.4** Code review, giving and receiving → [[concepts/04-best-practices/02-pr-structure|PR structure]]
- **24.5** Observability: logs, metrics, traces → [[devops/10-observability/01-observability-fundamentals|observability]] · [[devops/10-observability/02-the-observability-stack|the stack]]

**DSA:** mixed review, 5 problems

**By Sunday:** flagship's critical path (money, auth, or data-loss) is covered.

---

# Week 25 — DevOps and delivery

**Read:** [[devops/02-docker/README|docker]] · [[devops/06-ci-cd/README|CI/CD]] 01, 08, 09 · [[devops/09-secret-management/01-secret-management|secrets]]

**Depth: gap-fill.**

**Topics**
- **25.1** Docker — layers, caching, multi-stage → [[devops/02-docker/01-new-docker|docker]] · [[devops/02-docker/04-multi-stage-builds|multi-stage]]
- **25.2** CI/CD concepts → [[devops/06-ci-cd/01-ci-cd-concepts|concepts]]
- **25.3** CI pipelines — what runs on every push → [[devops/06-ci-cd/08-ci-pipelines|CI pipelines]]
- **25.4** CD, deployment strategies, releases → [[devops/06-ci-cd/09-cd-and-deployment|CD & deployment]]
- **25.5** Pipeline security and secrets → [[devops/06-ci-cd/10-pipeline-security|pipeline security]] · [[devops/09-secret-management/01-secret-management|secrets]]
- **25.6** Troubleshooting workflows → [[devops/06-ci-cd/12-troubleshooting-workflows|troubleshooting]]

**DSA:** mixed review, 5 problems

**By Sunday:** flagship deploys on merge to main with **no manual step**.

---

# Week 26 — Concurrency

**Read:** [[foundations/os/02-processes-and-threads|processes & threads]] · [[foundations/os/03-scheduling|scheduling]] · [[foundations/os/06-concurrency-primitives|primitives]] · [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

**Topics**
- **26.1** Processes vs threads → [[foundations/os/02-processes-and-threads|02]]
- **26.2** Scheduling → [[foundations/os/03-scheduling|03]]
- **26.3** Concurrency vs parallelism; **the Node event loop** → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]
- **26.4** Locks, mutexes, deadlock, race conditions → [[foundations/os/06-concurrency-primitives|primitives]]

**DSA:** mixed review + **first timed mock**, 45 min, unseen medium

**By Sunday:** closed-book — *what blocks the event loop, and how would you find out that it's blocked?*

---

# Week 27 — What makes distributed systems hard

**Read:** [[architecture/04-distributed-systems/README|distributed systems]] 01–04

**Topics**
- **27.1** What makes them hard → [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|01]]
- **27.2** Theoretical limits → [[architecture/04-distributed-systems/02-theoretical-limits|02]]
- **27.3** Time and ordering — **why you can't trust clocks** → [[architecture/04-distributed-systems/03-time-and-ordering|03]]
- **27.4** Consistency models → [[architecture/04-distributed-systems/04-consistency-models|04]]

**DSA:** mixed + timed mock

**By Sunday:** closed-book — *why can't you tell a slow node from a dead one?*

---

# Week 28 — Replication, partitioning, consensus

**Read:** [[architecture/04-distributed-systems/05-replication|05]] · [[architecture/04-distributed-systems/13-partitioning|13]] · [[architecture/04-distributed-systems/07-consensus-and-paxos|07]] · [[architecture/04-distributed-systems/08-raft-in-depth|08]]

**Topics**
- **28.1** Replication → [[architecture/04-distributed-systems/05-replication|05]]
- **28.2** Partitioning and sharding → [[architecture/04-distributed-systems/13-partitioning|13]]
- **28.3** Consensus → [[architecture/04-distributed-systems/07-consensus-and-paxos|07]]
- **28.4** Raft → [[architecture/04-distributed-systems/08-raft-in-depth|08]]

**DSA:** mixed + timed mock

**By Sunday:** closed-book — *explain Raft leader election to someone who has never heard of it.*

---

# Week 29 — Transactions, logs, failure

**Read:** [[architecture/04-distributed-systems/10-distributed-transactions|10]] · [[architecture/04-distributed-systems/12-the-log-and-state-machines|12]] · [[architecture/04-distributed-systems/14-failure-detection-and-membership|14]] · [[architecture/04-distributed-systems/15-testing-distributed-systems|15]]

**Topics**
- **29.1** Distributed transactions and saga → [[architecture/04-distributed-systems/10-distributed-transactions|10]]
- **29.2** The log and event-driven architecture → [[architecture/04-distributed-systems/12-the-log-and-state-machines|12]]
- **29.3** Idempotency and retry storms → [[architecture/04-distributed-systems/14-failure-detection-and-membership|14]]
- **29.4** Failure detection → [[architecture/04-distributed-systems/14-failure-detection-and-membership|14]]
- **29.5** Testing distributed systems → [[architecture/04-distributed-systems/15-testing-distributed-systems|15]]

**DSA:** mixed + timed mock

**By Sunday:** closed-book — *why can't you have exactly-once delivery, and what do you do instead?*

---

# Week 30 — Review and mock loops

**Read:** [[INTERVIEW|the interview index]] — the banks for every domain above

**Topics**
- **30.1** Full system-design mock: **ride-sharing**, then **video platform**
- **30.2** Two timed coding mocks
- **30.3** The project story — 2 minutes, 5 minutes, 20 minutes of depth → [[projects/nextvibe/interview/05-platform-payments-and-story|story bank]]
- **30.4** Behavioural — six STAR stories from real projects
- **30.5** Re-audit weeks 2–29; anything still *don't know it* gets a fortnight

**By Sunday:** the audit is redone and the gaps are scheduled.

---

# Week 31+ — The CS spine (ongoing)

**Read:** [[foundations/os/README|OS]] · [[foundations/computer-architecture/README|architecture]] · [[foundations/theory-of-computation/README|theory]] · [[foundations/compilers/README|compilers]]

No deadline, no interviewer asking. **This is the unit that answers your actual objective — *"understand why software is built the way it is."***

- **31.1** How a program runs — compile, link, load → [[foundations/compilers/01-what-a-compiler-is|compilers 01]]
- **31.2** Memory: stack, heap, process layout → [[foundations/os/05-memory-allocation|allocation]]
- **31.3** Virtual memory and the MMU → [[foundations/os/04-virtual-memory|virtual memory]]
- **31.4** The memory hierarchy and caches → [[foundations/computer-architecture/08-the-memory-hierarchy|hierarchy]] · [[foundations/computer-architecture/09-caches-in-depth|caches]]
- **31.5** Syscalls and the kernel boundary → [[foundations/os/09-syscalls-interrupts-and-the-abi|syscalls]]
- **31.6** Complexity classes, P vs NP — **knowing when to stop looking** → [[foundations/theory-of-computation/07-complexity-classes|complexity]]
- **31.7** Automata — why regexes and parsers look the way they do → [[foundations/theory-of-computation/02-finite-automata|automata]]
- **31.8** Compilers: lexer → parser → IR → codegen → [[foundations/compilers/02-lexical-analysis|lexing]] · [[foundations/compilers/03-parsing|parsing]]
- **31.9** Garbage collection → [[foundations/compilers/10-garbage-collection|GC]]
- **31.10** Why one O(n) loop is 30× slower than another → [[foundations/computer-architecture/12-performance|performance]]

**Exercise:** `perf stat` on your own code; explain the IPC.

---

# Section D — DSA, every week

**Read:** [[foundations/dsa/README|DSA course]] → [[foundations/dsa/06-patterns/README|the 15 patterns]] · [[foundations/dsa/interview/README|the coding round]]

Back of the notebook, worked forward. One page per pattern — format in [[learning/swe-101/03-notebook-method|the method]].

| Week | Pattern |
|---|---|
| 1 | [[foundations/dsa/06-patterns/01-prefix-sum\|Prefix sum]] |
| 2 | [[foundations/dsa/06-patterns/02-two-pointers\|Two pointers]] |
| 3 | [[foundations/dsa/06-patterns/03-sliding-window\|Sliding window]] |
| 4 | [[foundations/dsa/06-patterns/04-fast-slow-pointers\|Fast & slow pointers]] |
| 5 | [[foundations/dsa/06-patterns/05-linked-list-reversal\|Linked list reversal]] |
| 6 | [[foundations/dsa/06-patterns/06-monotonic-stack\|Monotonic stack]] |
| 7 | [[foundations/dsa/06-patterns/07-top-k-elements\|Top-K elements]] |
| 8 | [[foundations/dsa/06-patterns/08-overlapping-intervals\|Overlapping intervals]] |
| 9 | [[foundations/dsa/06-patterns/09-modified-binary-search\|Modified binary search]] |
| 10 | [[foundations/dsa/06-patterns/10-binary-tree-traversal-pattern\|Binary tree traversal]] |
| 11 | [[foundations/dsa/06-patterns/11-dfs-pattern\|DFS]] |
| 12 | [[foundations/dsa/06-patterns/12-bfs-pattern\|BFS]] |
| 13 | [[foundations/dsa/06-patterns/13-matrix-traversal\|Matrix traversal]] |
| 14 | [[foundations/dsa/06-patterns/14-backtracking\|Backtracking]] |
| 15–16 | [[foundations/dsa/06-patterns/15-dynamic-programming\|Dynamic programming]] |
| 17–30 | **Mixed review, patterns drawn at random, 5/week + timed mocks from week 26** |

**Weeks 17–30 are the important half.** Solving a sliding-window problem in sliding-window week is recognition. Solving one when you don't know what kind it is, is the actual skill — and that's what an interview measures.

**Complexity, recursion and Big-O are learned *through* these**, not as a block beforehand — that's why the original Phases 2–3 were folded in here.

**Target: 150 problems, ~60% medium**, logged with pattern / cold? / time / what I missed.

---

## Where this ends

**Weeks 1–30 plus 150 problems plus a shipped flagship with evals is a hirable full-stack / AI engineer.** Week 31+ is what makes you a good one, and it doesn't stop.

> The progression you named, and it still holds:
> **Programming → Computer Science → Software Engineering → Systems Thinking → Architecture.**
