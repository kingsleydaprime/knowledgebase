# How to Approach System Design

**[reference]** — from the roadmap.sh system-design roadmap. The repeatable framework for designing (or explaining, or interviewing on) any system — so you're never staring at a blank whiteboard.

## The trap, and the fix

The mistake under pressure is jumping straight to a solution ("use Kafka and microservices!") before understanding the problem. The fix is a **framework you run every time**, so the process carries you when inspiration doesn't. It also happens to be exactly what a system-design interview scores.

## The framework

### 1. Clarify requirements (don't skip this)

Nail down *what you're building* before *how*:

- **Functional requirements** — what the system does (users post tweets, followers see them). Scope it — you can't build everything, so agree on the core.
- **Non-functional requirements** — the qualities that shape the architecture: expected **scale** (users, requests/sec, data volume), **latency** targets, **availability** needs, read-vs-write ratio, consistency needs. *These drive every later decision* — a read-heavy system at 10 req/s and a write-heavy one at 1M req/s are entirely different designs.

The most important sentence: **"what are we optimizing for?"** You cannot design well without knowing which tradeoffs matter here.

### 2. Estimate (back-of-the-envelope)

Rough numbers to size the system and justify choices: requests/sec, storage/year, bandwidth, memory for caching. You don't need precision — you need the *order of magnitude* (is this gigabytes or petabytes? thousands or millions of QPS?), because that determines whether one database suffices or you need [[architecture/02-building-blocks/03-databases-at-scale|sharding]]. Know the [latency numbers every engineer should know](https://gist.github.com/jboner/2841832) (memory ~100ns, SSD ~100µs, network round-trip ~500µs–150ms) to reason about what's feasible.

### 3. High-level design

Draw the big boxes and how requests flow: client → [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancer]] → application servers → [[architecture/02-building-blocks/02-caching|cache]] / [[architecture/02-building-blocks/03-databases-at-scale|database]], plus any [[architecture/02-building-blocks/04-messaging-and-async|queues]] for async work. Define the core APIs and the data model. Get the *shape* right before optimizing any piece.

### 4. Deep dive

Zoom into the 1–2 components that are hardest or most critical for *this* system's requirements: how to shard the database, the caching strategy, how to keep the feed fresh, how to handle the write hotspot. This is where the interesting engineering (and the interview signal) lives.

### 5. Identify bottlenecks & tradeoffs

Find the single points of failure, the hot paths, the scaling limits — and address them ([[architecture/01-system-design-fundamentals/03-availability-and-reliability|redundancy]], [[architecture/02-building-blocks/02-caching|caching]], [[architecture/02-building-blocks/03-databases-at-scale|replication]]). Crucially, **state the tradeoffs out loud**: "I'm choosing eventual consistency here to get availability, which means a user might briefly see a stale count — acceptable for likes, not for account balance." There is no perfect design; there are only tradeoffs you chose deliberately vs. ones that bit you.

## The meta-skill

System design has no single right answer — it rewards **structured reasoning about tradeoffs** under specific requirements. The engineer who says "it depends — on the read/write ratio, the consistency needs, and the scale — and here's how each changes the design" is demonstrating exactly the judgment senior roles screen for. Every other note in this course is an input to this process.

## Related
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance|Scalability & Performance]] — the scaling tradeoffs step 5 navigates
- [[architecture/05-case-studies/01-designing-real-systems|Designing Real Systems]] — this framework applied to concrete problems
- [[architecture/system-design-reference|System Design Reference]] — the dense cheat-sheet
