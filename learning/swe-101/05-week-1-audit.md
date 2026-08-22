# Week 1 — The Audit

> The first thing you do, and the only deliverable of week 1. Tick one box per topic. **Be honest — an inflated audit costs you months, because it hides the gap that's actually binding.**

**K** = I could explain this to someone right now, closed book.
**H** = I've met it, I'd need to look it up.
**D** = I don't know this.

```
K  H  D
[ ][ ][ ]   topic
```

**Do it on paper, in the notebook, section 1.** It takes about 40 minutes. Redo it in week 30 and compare — that comparison is the clearest evidence of progress you will get all year.

---


## Week 2 — Design principles

```
K  H  D
[ ][ ][ ]   2.1  Modularity — what a module is, and what makes a bad one
[ ][ ][ ]   2.2  Coupling and cohesion
[ ][ ][ ]   2.3  Abstraction and interfaces
[ ][ ][ ]   2.4  Separation of concerns
[ ][ ][ ]   2.5  DRY, KISS, YAGNI — and where each one is wrong
[ ][ ][ ]   2.6  SOLID, one letter at a time — and when it's over-engineering
[ ][ ][ ]   2.7  Composition over inheritance
```

## Week 3 — Design patterns

```
K  H  D
[ ][ ][ ]   3.1  Creational — factory, builder, and why singleton is usually a mistake
[ ][ ][ ]   3.2  Structural — adapter, decorator, facade, proxy
[ ][ ][ ]   3.3  Behavioural — strategy, observer, command, state
[ ][ ][ ]   3.4  Dependency injection and wiring
```

## Week 4 — Structuring a codebase

```
K  H  D
[ ][ ][ ]   4.1  Layers: controllers, services, repositories
[ ][ ][ ]   4.2  Organising by layer vs by feature
[ ][ ][ ]   4.3  Hexagonal and clean architecture
[ ][ ][ ]   4.4  Modular monolith
```

## Week 5 — How to approach system design

```
K  H  D
[ ][ ][ ]   5.1  The sequence, so you never freeze
[ ][ ][ ]   5.2  Functional vs non-functional requirements
[ ][ ][ ]   5.3  Back-of-envelope estimation
[ ][ ][ ]   5.4  Scalability and performance, vertical vs horizontal
```

## Week 6 — Availability, caching, load balancing

```
K  H  D
[ ][ ][ ]   6.1  Availability, reliability, what "three nines" actually costs
[ ][ ][ ]   6.2  CAP and consistency
[ ][ ][ ]   6.3  Load balancing, proxies, reverse proxies
[ ][ ][ ]   6.4  Caching, and cache invalidation
```

## Week 7 — Data, messaging, communication

```
K  H  D
[ ][ ][ ]   7.1  Databases at scale
[ ][ ][ ]   7.2  Messaging and async
[ ][ ][ ]   7.3  REST, gRPC, GraphQL, WebSockets
```

## Week 8 — Architectural patterns and trade-offs

```
K  H  D
[ ][ ][ ]   8.1  Monolith vs microservices vs serverless
[ ][ ][ ]   8.2  Resilience: timeouts, retries, backoff, circuit breakers, bulkheads
[ ][ ][ ]   8.3  Data and integration patterns
[ ][ ][ ]   8.4  Microservices patterns
[ ][ ][ ]   8.5  Trade-off articulation — saying "I'd choose X because Y" instead of "it depend
```

## Week 9 — The relational model and SQL

```
K  H  D
[ ][ ][ ]   9.1  What a database actually is
[ ][ ][ ]   9.2  The relational model — tables, rows, keys, relationships
[ ][ ][ ]   9.3  Normalisation, and when to denormalise on purpose
[ ][ ][ ]   9.4  SQL: SELECT, JOIN, GROUP BY, aggregates, subqueries, CTEs
```

## Week 10 — Database internals

```
K  H  D
[ ][ ][ ]   10.1  Storage and page layout
[ ][ ][ ]   10.2  B-trees and indexes
[ ][ ][ ]   10.3  LSM trees, and why new engines choose them
[ ][ ][ ]   10.4  The query pipeline
[ ][ ][ ]   10.5  Join algorithms and the optimiser
[ ][ ][ ]   10.6  `EXPLAIN ANALYZE` — estimated vs actual rows as the diagnostic
```

## Week 11 — Transactions, durability, operations

```
K  H  D
[ ][ ][ ]   11.1  Transactions and ACID
[ ][ ][ ]   11.2  Isolation levels and MVCC
[ ][ ][ ]   11.3  Durability, the WAL, recovery
[ ][ ][ ]   11.4  Replication and scaling — "replication is not a backup"
[ ][ ][ ]   11.5  Operating: migrations, `lock_timeout`, pooling, backups
```

## Week 12 — The network and IP

```
K  H  D
[ ][ ][ ]   12.1  What a network is; the layered model
[ ][ ][ ]   12.2  The link layer, MAC addresses
[ ][ ][ ]   12.3  IP addressing and subnetting
[ ][ ][ ]   12.4  Routing
```

## Week 13 — TCP and UDP

```
K  H  D
[ ][ ][ ]   13.1  UDP and ports
[ ][ ][ ]   13.2  TCP connection lifecycle — handshake, teardown, states
[ ][ ][ ]   13.3  Reliability and flow control
[ ][ ][ ]   13.4  Congestion control
[ ][ ][ ]   13.5  Sockets and the network API
```

## Week 14 — DNS, HTTP, TLS

```
K  H  D
[ ][ ][ ]   14.1  DNS in depth
[ ][ ][ ]   14.2  HTTP and its evolution — 1.1, 2, 3
[ ][ ][ ]   14.3  TLS and transport security
[ ][ ][ ]   14.4  QUIC
[ ][ ][ ]   14.5  Cookies, sessions, headers
```

## Week 15 — The edge, performance, debugging

```
K  H  D
[ ][ ][ ]   15.1  NAT, firewalls, middleboxes
[ ][ ][ ]   15.2  Proxies, reverse proxies, CDNs
[ ][ ][ ]   15.3  Latency vs bandwidth, RTT, head-of-line blocking
[ ][ ][ ]   15.4  Debugging: `dig`, `curl -v`, `ss`, `tcpdump`
```

## Week 16 — Identity: authentication and authorisation

```
K  H  D
[ ][ ][ ]   16.1  Authentication vs authorisation
[ ][ ][ ]   16.2  Password hashing — bcrypt/argon2, and why not SHA-256
[ ][ ][ ]   16.3  Sessions vs JWT, and when JWT is the wrong choice
[ ][ ][ ]   16.4  OAuth 2.0 / OIDC
[ ][ ][ ]   16.5  Least privilege
```

## Week 17 — Attacks and defences

```
K  H  D
[ ][ ][ ]   17.1  Input validation and output encoding
[ ][ ][ ]   17.2  Injection: SQL, command, template
[ ][ ][ ]   17.3  XSS, CSRF, SSRF
[ ][ ][ ]   17.4  Security headers and same-origin policy
[ ][ ][ ]   17.5  Symmetric, asymmetric, signatures, PKI
[ ][ ][ ]   17.6  TLS in practice
[ ][ ][ ]   17.7  Secrets management
[ ][ ][ ]   17.8  Prompt injection and LLM-specific risk
```

## Week 18 — Backend: the request path

```
K  H  D
[ ][ ][ ]   18.1  What a backend is
[ ][ ][ ]   18.2  HTTP servers; rate limiting at the edge
[ ][ ][ ]   18.3  The request lifecycle end to end
[ ][ ][ ]   18.4  Runtime and concurrency models — the Node event loop
[ ][ ][ ]   18.5  REST design and resource modelling
[ ][ ][ ]   18.6  ⚠️ API versioning — no dedicated chapter; thin coverage only
```

## Week 19 — Backend: cross-cutting concerns

```
K  H  D
[ ][ ][ ]   19.1  Validation, error handling, error contracts
[ ][ ][ ]   19.2  Rate limiting
[ ][ ][ ]   19.3  Structured logging and configuration
[ ][ ][ ]   19.4  Databases in the backend; pooling, migrations
[ ][ ][ ]   19.5  Background jobs and queues
[ ][ ][ ]   19.6  Idempotency
[ ][ ][ ]   19.7  Caching layers
```

## Week 20 — LLMs: the ground floor

```
K  H  D
[ ][ ][ ]   20.1  What the role actually is
[ ][ ][ ]   20.2  How LLMs work — enough to reason about why they fail
[ ][ ][ ]   20.3  The model landscape
[ ][ ][ ]   20.4  Calling models: streaming, tokens, temperature, context windows
```

## Week 21 — Prompting, structure, retrieval

```
K  H  D
[ ][ ][ ]   21.1  Prompt engineering; prompts as versioned artifacts
[ ][ ][ ]   21.2  Structured output
[ ][ ][ ]   21.3  RAG and embeddings — chunking, hybrid search, reranking
```

## Week 22 — Tools and agents

```
K  H  D
[ ][ ][ ]   22.1  Tools and MCP
[ ][ ][ ]   22.2  Agents, and when not to use one
[ ][ ][ ]   22.3  Multimodal
```

## Week 23 — Evals and production ⭐

```
K  H  D
[ ][ ][ ]   23.1  Evals — golden sets, scorers, regression runs in CI
[ ][ ][ ]   23.2  Reliability and plumbing — retries, fallbacks, timeouts
[ ][ ][ ]   23.3  Cost, caching, latency
[ ][ ][ ]   23.4  Safety in production — PII, output filtering
[ ][ ][ ]   23.5  Practice
```

## Week 24 — Testing and quality

```
K  H  D
[ ][ ][ ]   24.1  The pyramid: unit, integration, e2e
[ ][ ][ ]   24.2  Test doubles: stub, mock, fake, spy
[ ][ ][ ]   24.3  What not to test; flaky tests
[ ][ ][ ]   24.4  Code review, giving and receiving
[ ][ ][ ]   24.5  Observability: logs, metrics, traces
```

## Week 25 — DevOps and delivery

```
K  H  D
[ ][ ][ ]   25.1  Docker — layers, caching, multi-stage
[ ][ ][ ]   25.2  CI/CD concepts
[ ][ ][ ]   25.3  CI pipelines — what runs on every push
[ ][ ][ ]   25.4  CD, deployment strategies, releases
[ ][ ][ ]   25.5  Pipeline security and secrets
[ ][ ][ ]   25.6  Troubleshooting workflows
```

## Week 26 — Concurrency

```
K  H  D
[ ][ ][ ]   26.1  Processes vs threads
[ ][ ][ ]   26.2  Scheduling
[ ][ ][ ]   26.3  Concurrency vs parallelism; the Node event loop
[ ][ ][ ]   26.4  Locks, mutexes, deadlock, race conditions
```

## Week 27 — What makes distributed systems hard

```
K  H  D
[ ][ ][ ]   27.1  What makes them hard
[ ][ ][ ]   27.2  Theoretical limits
[ ][ ][ ]   27.3  Time and ordering — why you can't trust clocks
[ ][ ][ ]   27.4  Consistency models
```

## Week 28 — Replication, partitioning, consensus

```
K  H  D
[ ][ ][ ]   28.1  Replication
[ ][ ][ ]   28.2  Partitioning and sharding
[ ][ ][ ]   28.3  Consensus
[ ][ ][ ]   28.4  Raft
```

## Week 29 — Transactions, logs, failure

```
K  H  D
[ ][ ][ ]   29.1  Distributed transactions and saga
[ ][ ][ ]   29.2  The log and event-driven architecture
[ ][ ][ ]   29.3  Idempotency and retry storms
[ ][ ][ ]   29.4  Failure detection
[ ][ ][ ]   29.5  Testing distributed systems
```

## Week 30 — Review and mock loops

```
K  H  D
[ ][ ][ ]   30.1  Full system-design mock: ride-sharing, then video platform
[ ][ ][ ]   30.2  Two timed coding mocks
[ ][ ][ ]   30.3  The project story — 2 minutes, 5 minutes, 20 minutes of depth
[ ][ ][ ]   30.4  Behavioural — six STAR stories from real projects
[ ][ ][ ]   30.5  Re-audit weeks 2–29; anything still don't know it gets a fortnight
```

## Week 31+ — The CS spine (ongoing)

```
K  H  D
[ ][ ][ ]   31.1  How a program runs — compile, link, load
[ ][ ][ ]   31.2  Memory: stack, heap, process layout
[ ][ ][ ]   31.3  Virtual memory and the MMU
[ ][ ][ ]   31.4  The memory hierarchy and caches
[ ][ ][ ]   31.5  Syscalls and the kernel boundary
[ ][ ][ ]   31.6  Complexity classes, P vs NP — knowing when to stop looking
[ ][ ][ ]   31.7  Automata — why regexes and parsers look the way they do
[ ][ ][ ]   31.8  Compilers: lexer
[ ][ ][ ]   31.9  Garbage collection
[ ][ ][ ]   31.10  Why one O(n) loop is 30× slower than another
```

---

## What to do with the result

**148 topics.** Now convert the ticks into a plan:

| Mostly | That week becomes |
|---|---|
| **D** | **Write** — full treatment, the 8-part notebook structure, every topic gets a page |
| **H** | **Reconstruct** — write from memory first, *then* read the chapter, and note only the diff |
| **K** | **Skip the reading.** Do the week's exercise and the closed-book question only. If both go cleanly, skip the week entirely |

**Banking the skipped time is the point.** Every week you skip goes into DSA and the flagship — the two things that actually produce the offer. A 30-week scheme where you honestly skip five weeks is better than a 30-week scheme you pad out to feel thorough.

**The one rule that keeps this honest:** you may only mark **K** for something you could explain *closed-book, out loud, right now*. Recognition feels identical to knowledge and isn't — that gap is exactly what an interview measures. If you're unsure, it's **H**.

## Watch for these

- **Week 18–19 (backend) will look like all Ks.** Probably fair — you've shipped it. Still do the closed-book questions; "draw the full request path including every failure point" catches more gaps than people expect.
- **Week 23 (evals) is almost certainly D**, and it's the highest-leverage topic in the scheme.
- **Weeks 26–29 (distributed systems) will feel like H** because you've used RabbitMQ and written idempotency keys. Using a queue and understanding failure detection are different things — be strict here.
- **Don't mark D out of modesty.** It wastes the same time as marking K out of ego.

---

**Related:** [[learning/swe-101/04-scheme-of-work|the scheme of work]] · [[learning/swe-101/03-notebook-method|notebook method]] · [[learning/swe-101/01-hire-track|hire track]]
