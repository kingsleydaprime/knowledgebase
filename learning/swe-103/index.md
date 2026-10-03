# SWE 103 — Systems and Interviews

**Status:** queued — starts the Monday after [[learning/swe-102/index|SWE 102]]'s finish line is met · **Length:** 11 weeks
**How every week works:** the four lanes, the rotation and the rules are in [[learning/swe-101/index#How every week works|SWE 101]]. Notebook sections are numbered 103.1–103.11.

---

## Why this course

By now the flagship is real and its AI feature is measured. What's left is what senior-leaning interviews probe: **designing a system out loud in 45 minutes**, and the database, web and distributed-systems knowledge underneath it. The notes for all of it are written; the reps are not. So the **Build** lane becomes a **design** lane: one system design every other week, on the board, out loud, timed.

**What moved out on purpose:** link layer, subnetting, routing, congestion control, QUIC, NAT, database page layout, LSM trees, durability internals, Paxos and Raft. All good knowledge, rarely asked of a junior TypeScript or AI engineer. They're in [[#After the series — the CS spine|the CS spine]] below — later, not never.

## Course finish line

- [ ] Four system designs done out loud and timed: URL shortener, notification system, payment system, chat
- [ ] Two full system-design mocks (45 minutes, with someone else asking if possible) and two timed coding mocks
- [ ] "What happens when I type google.com", one page from memory
- [ ] One slow query from a real project fixed with `EXPLAIN ANALYZE`, before and after recorded
- [ ] The project story at three lengths: 2 minutes, 5 minutes, 20 minutes of depth
- [ ] Six behavioural stories in STAR form, from real projects
- [ ] DSA: mixed review, five a week, plus one timed mock a week

**Week 1's first job is the audit** of this course's lessons.

## DSA in this course

No new patterns. **Every week: five problems drawn at random from NeetCode 150 problems not yet logged, plus one timed 45-minute mock.** This is what interviews actually are — the pattern isn't announced. Draw at least one graph problem every week; that's the gap interviews exposed.

## The eleven weeks

### Week 1 — How to approach a design

- **Learn (core):** [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|how to approach system design]] · [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]]
- **Learn (optional):** [[architecture/interview/01-system-design-round|the system design round]]
- **Design:** **URL shortener** — 45 minutes, out loud, *before* reading anything else. Then write only the gap.

### Week 2 — Caching and load balancing

- **Learn (core):** [[architecture/02-building-blocks/02-caching/index|caching]] · [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|load balancing and proxies]]
- **Learn (optional):** [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability]] · [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP and consistency]]
- **By Sunday:** closed-book — *where would you put a cache in the URL shortener, and what goes stale?*

### Week 3 — Messaging and communication

- **Learn (core):** [[architecture/02-building-blocks/04-messaging-and-async/index|messaging and async]] · [[architecture/02-building-blocks/05-communication/index|REST, gRPC, GraphQL, WebSockets]]
- **Learn (optional):** [[architecture/02-building-blocks/03-databases-at-scale|databases at scale]]
- **Design:** **notification system**. You have real RabbitMQ reps — this one should come from experience.

### Week 4 — Architecture choices

- **Learn (core):** [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/index|monolith, microservices, serverless]] · [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]]
- **Learn (optional):** [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data and integration patterns]] · [[architecture/03-architectural-patterns/04-microservices-patterns|microservices patterns]]
- **By Sunday:** closed-book — *when would you not use microservices?* — said as "I'd choose X because Y", not "it depends".

### Week 5 — Databases I: querying well

- **Learn (core):** [[databases/04-b-trees-and-indexes|B-trees and indexes]] · [[databases/07-join-algorithms-and-the-optimiser|join algorithms, the optimiser, and EXPLAIN ANALYZE]]
- **Learn (optional):** [[databases/01-what-a-database-is|what a database is]] · [[databases/02-the-relational-model|the relational model]] · [[databases/06-the-query-pipeline|the query pipeline]]
- **Design:** **payment system** — from your nextvibe ledger and the direct-debit sandbox. Interviewers can hear experience.
- **By Sunday:** one slow query from a real project, `EXPLAIN ANALYZE`d and fixed, before and after recorded.

### Week 6 — Databases II: changing data safely

- **Learn (core):** [[databases/08-transactions-and-acid|transactions and ACID]] · [[databases/09-mvcc-and-concurrency-control|isolation and MVCC]]
- **Learn (optional):** [[databases/12-operating-a-database|operating a database]] · [[databases/11-replication-and-scaling|replication and scaling]]
- **By Sunday:** closed-book — *why does adding an index sometimes make things slower?*

### Week 7 — The web, end to end

- **Learn (core):** [[networking/10-dns-in-depth|DNS]] · [[networking/11-http-evolution|HTTP and its evolution]] · [[networking/12-tls-and-transport-security|TLS]] — three this week; they're one story.
- **Learn (optional):** [[networking/06-tcp-connection-lifecycle|TCP connection lifecycle]]
- **Design:** **chat application**.
- **By Sunday:** **"What happens when I type google.com?"** — one page, from memory.

### Week 8 — The request path and the event loop

- **Learn (core):** [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]] · [[backend/01-foundations/04-runtime-and-concurrency-models|runtime and concurrency models]]
- **Learn (optional):** [[networking/16-debugging-networks|debugging networks]] · [[os/06-concurrency-primitives|locks, races and deadlock]]
- **By Sunday:** closed-book — *what blocks the Node event loop, and how would you find out it's blocked?*

### Week 9 — Identity

- **Learn (core):** [[backend/05-auth/01-authentication-flows|sessions vs JWT]] · [[backend/05-auth/03-oauth-provider-integrations|OAuth and OIDC]]
- **Learn (optional):** [[backend/05-auth/02-authorization|authorisation]] · [[cybersecurity/05-cryptography/03-hashing-and-integrity|password hashing]] · [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]]
- **By Sunday:** draw the flagship's full auth flow from memory, including refresh and logout.

### Week 10 — Distributed systems, the essentials

- **Learn (core):** [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|what makes distributed systems hard]] · [[architecture/04-distributed-systems/04-consistency-models|consistency models]]
- **Learn (optional):** [[architecture/04-distributed-systems/05-replication|replication]] · [[architecture/04-distributed-systems/13-partitioning|partitioning]] · [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]]
- **By Sunday:** closed-book — *why can't you have exactly-once delivery, and what do you do instead?*

### Week 11 — Mock loops

- Two full system-design mocks: **ride-sharing**, then **video platform**.
- Two timed coding mocks.
- The project story at 2, 5 and 20 minutes → [[projects/nextvibe/interview/05-platform-payments-and-story|the nextvibe story bank]] is the model.
- Six STAR stories from real projects. Remote roles probe async communication hard.
- The interview banks: [[INTERVIEW|13 domains]]. Cover the answer, say it out loud, then compare.
- **By Sunday:** every finish-line box ticked, or dated.

## After the series — the CS spine

Not a course yet. When the series is done, or once employed, this becomes its own course through the usual [[learning/03-the-course-system|make-a-course]] step:

- **How a program runs:** [[compilers/01-what-a-compiler-is|compilers]] · [[os/05-memory-allocation|memory allocation]] · [[os/04-virtual-memory|virtual memory]] · [[os/09-syscalls-interrupts-and-the-abi|syscalls]]
- **Hardware and performance:** [[computer-architecture/08-the-memory-hierarchy|the memory hierarchy]] · [[computer-architecture/09-caches-in-depth|caches]] · [[computer-architecture/12-performance|performance]]
- **Theory:** [[theory-of-computation/07-complexity-classes|complexity classes]] · [[theory-of-computation/02-finite-automata|automata]] · [[compilers/02-lexical-analysis|lexing]] · [[compilers/03-parsing|parsing]] · [[compilers/11-garbage-collection|garbage collection]]
- **Moved here from the old scheme:** [[networking/02-the-link-layer|link layer]] · [[networking/03-ip-addressing-and-subnetting|subnetting]] · [[networking/04-routing|routing]] · [[networking/08-congestion-control|congestion control]] · [[networking/13-quic-and-modern-transport|QUIC]] · [[networking/14-nat-firewalls-and-middleboxes|NAT and firewalls]] · [[databases/03-storage-and-page-layout|page layout]] · [[databases/05-lsm-trees|LSM trees]] · [[databases/10-durability-and-recovery|durability]] · [[architecture/04-distributed-systems/07-consensus-and-paxos|consensus]] · [[architecture/04-distributed-systems/08-raft-in-depth|Raft]]

## Related

- [[learning/swe-101/index|SWE 101]] — the series overview and the weekly rules
- [[architecture/interview/01-system-design-round|The system design round]] · [[INTERVIEW|the interview banks]]
