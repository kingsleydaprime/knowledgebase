# Architecture Interview — The System Design Round

From [[architecture/01-system-design-fundamentals/README|01-fundamentals]], [[architecture/02-building-blocks/README|02-building-blocks]], [[architecture/03-architectural-patterns/README|03-patterns]].

**This round is not a knowledge test — it's a "can I work with you" test.** The interviewer is watching you handle ambiguity, make a call, and say why. Candidates fail far more often by jumping to a diagram than by not knowing what a CDN is.

---

## The framework (use it every time)

```
1. REQUIREMENTS   (5 min)  functional, non-functional, explicitly out of scope
2. ESTIMATION     (5 min)  QPS, storage, bandwidth — round numbers, out loud
3. API + DATA     (5 min)  the interface, then the model
4. HIGH LEVEL    (10 min)  boxes and arrows, happy path only
5. DEEP DIVE     (15 min)  they pick, or you offer the interesting bottleneck
6. TRADEOFFS      (5 min)  what breaks, what you'd do differently at 10×
```

**The single most common failure is skipping step 1.** Designing before you know whether it's 1,000 or 100 million users is designing the wrong thing, and it reads as someone who'd do the same on a real project.

**Numbers to have memorised:**
- 1M requests/day ≈ **12 QPS**. 1B/day ≈ **12,000 QPS**.
- Read:write is usually **100:1** or worse for consumer products — say so, because it justifies caching and read replicas.
- A single Postgres box handles thousands of QPS comfortably. **Don't shard on slide one.**
- 1 KB × 1M/day ≈ 1 GB/day ≈ **365 GB/year**.

---

### Q1. [Intermediate] 🔥 Design a URL shortener.

**What they're testing:** whether you handle the *interesting* part or just draw a database.

**Strong answer covers:** functional (shorten, redirect, maybe analytics/expiry), scale (heavily read-dominated, ~100:1), the API, then the **actual design decision — how you generate the short key:**
- **Hash the URL and truncate** — needs collision handling, and identical URLs collide by design (sometimes desirable).
- **Auto-increment + base62 encode** — no collisions, but sequential IDs are enumerable, which is an information-disclosure problem.
- **Pre-generated key pool** — a service hands out unused keys in batches. No coordination on the write path, no collisions. Usually the best answer.

Then: redirect uses **301 vs 302** — and this is a real tradeoff worth naming: 301 is cached by the browser so subsequent hits never reach you (great for load, fatal for analytics); 302 keeps every hit visible.

**The deep dive to steer toward:** caching. It's read-heavy with a small hot set, so an LRU cache in front of the store absorbs almost everything. → [[architecture/02-building-blocks/02-caching|caching]]

---

### Q2. [Intermediate→Advanced] 🔥 Design a rate limiter.

**Strong answer covers the algorithms and why you'd pick each:**

| Algorithm | Behaviour | Trade |
|---|---|---|
| **Fixed window** | count per clock window | simple; **2× burst at the boundary** |
| **Sliding window log** | timestamps of every request | exact; memory-heavy |
| **Sliding window counter** | weighted blend of two windows | good approximation, cheap — usual choice |
| **Token bucket** | tokens refill at a rate, burst up to capacity | **allows bursts deliberately** — best for APIs |
| **Leaky bucket** | fixed outflow rate | smooths traffic, no bursts |

**The distributed part is the real question:** per-instance counters mean N instances allow N× the limit. Options: centralised Redis (a network hop on every request, and Redis becomes a dependency and a SPOF), or local counters with an approximate sync (faster, less exact). Say which you'd pick and why — for most APIs, Redis with a Lua script for atomicity is right; for extreme throughput, local buckets with periodic reconciliation.

**Details that score:** return `429` with `Retry-After` and `X-RateLimit-*` headers; decide fail-open vs fail-closed when Redis is down (fail-open for availability, fail-closed for abuse protection — *name the choice*); and rate-limit by API key, not IP, when you can, because NAT means many users share an IP.

**You have this in the vault** — the token-bucket exercise in [[languages/01-java/02-jvm-and-concurrency/exercises/README|the concurrency exercises]]. Build it.

---

### Q3. [Advanced] 🔥 Design a news feed (Twitter/Instagram timeline).

**Strong answer covers the central tradeoff, which is the entire question — fan-out on write vs fan-out on read:**

- **Fan-out on write (push)** — when you post, write into every follower's precomputed feed. Reads are trivially fast (one lookup). But a celebrity with 50M followers triggers 50M writes per post — the **hot key / celebrity problem**.
- **Fan-out on read (pull)** — assemble the feed at read time by querying everyone you follow. Cheap writes, expensive reads, and it scales badly for users following thousands of accounts.

**The answer that separates candidates: a hybrid.** Push for normal users, pull for celebrities, merge at read time. That's what Twitter actually does, and knowing *why* — that the distribution of follower counts is extremely skewed, so no single strategy fits — is the insight.

**Deep dives available:** ranking vs chronological, pagination (**cursor-based, not offset** — offset pagination breaks when items are inserted, and gets slower with depth), and cache invalidation on edit/delete.

---

### Q4. [Intermediate] 🔥 When would you *not* use microservices?

**Strong answer covers:** microservices trade **local complexity for distributed complexity**. You buy independent deploys, independent scaling, and team autonomy. You pay with network calls that fail, distributed transactions you now can't have, eventual consistency, distributed tracing, and an operational burden that needs a platform team.

**Say the unpopular thing, because it's correct:** for a small team or an unproven product, **start with a modular monolith**. You can't draw correct service boundaries before you understand the domain, and wrong boundaries are far more expensive to fix once they're network calls instead of function calls. Extract services when you have a *specific* reason — a component with genuinely different scaling needs, or a team that's blocked on someone else's deploy cadence.

**The pattern to name:** [[architecture/03-architectural-patterns/03-data-and-integration-patterns|strangler fig]] — extract incrementally behind a facade rather than rewriting.

---

### Q5. [Intermediate] 🔥 Where would you cache, and what's the hardest part?

**Strong answer covers the layers:** browser → CDN → API gateway → application (in-process) → distributed cache (Redis) → database buffer pool. Each is cheaper and closer than the next.

**Strategies:** cache-aside (lazy, most common), read-through, write-through (consistent, slower writes), write-behind (fast, risks loss).

**The hardest part — and this is the answer:** **invalidation**. Then name the three failure modes, because they're what production actually throws at you:
- **Stampede / thundering herd** — a hot key expires and 10,000 requests hit the database at once. Fix: a lock or single-flight so one request refills while others wait, plus jittered TTLs so keys don't expire together.
- **Cache penetration** — repeated requests for a key that doesn't exist bypass the cache every time. Fix: cache the negative result, or a Bloom filter.
- **Cache avalanche** — everything expires simultaneously (e.g. after a restart). Fix: jitter, warmup.

---

### Q6. [Intermediate] Explain CAP correctly — and why most people quoting it are wrong.

**Strong answer covers:** during a **network partition**, you must choose consistency or availability. That's the whole theorem, and it's narrower than the folklore.

**The three corrections that show you actually understand it:**
1. **"CA" is not a real option.** Partitions are not something you choose to have — they happen. Any distributed system is either CP or AP.
2. It says nothing about behaviour when there's **no** partition — which is nearly all the time. **PACELC** completes it: *if Partitioned, choose A or C; Else, choose Latency or Consistency.* That "else" branch is where systems actually live day to day, and it's why Dynamo-style stores are fast even when healthy.
3. "Consistency" here is **linearizability**, not the C in ACID. Different word, different meaning.

→ [[architecture/04-distributed-systems/02-theoretical-limits|theoretical limits]]

---

### Q7. [Intermediate] How do you scale a database that's become the bottleneck?

**Strong answer covers the ladder, in order — and the order is the point:**
1. **Measure first.** Which queries? `EXPLAIN` them. Most "we need to shard" problems are a missing index.
2. **Indexes and query fixes** — including killing N+1s.
3. **Caching** — take reads off the database entirely.
4. **Vertical scaling** — genuinely underrated. Modern hardware is enormous and a bigger box costs less than an engineer-quarter.
5. **Read replicas** — for read-heavy loads. Now you must handle **replication lag** and read-your-own-writes.
6. **Partitioning/sharding** — last, because it costs you cross-shard joins, distributed transactions, rebalancing, and hot shards.

**What scores:** "sharding is the last resort, not the first" plus a named shard-key concern (a poorly chosen key gives you a hot shard, and changing it later is a migration nightmare). → [[architecture/04-distributed-systems/13-partitioning|partitioning]]

---

### Q8. [Intermediate] 🔥 How do you design for failure?

**Strong answer covers the patterns and, crucially, what each is *for*:**
- **Timeouts** — the default is often infinite; that's how one slow dependency exhausts your thread pool.
- **Retries with exponential backoff *and jitter*** — without jitter, retries synchronise into a thundering herd. Only retry idempotent operations.
- **Circuit breaker** — after N failures, stop calling and fail fast. Prevents you from hammering a dying service and from tying up your own resources waiting.
- **Bulkhead** — separate resource pools so one failing dependency can't consume every thread.
- **Graceful degradation** — serve stale cache or a reduced feature set rather than an error.
- **Backpressure** — reject work you can't handle instead of queueing forever. A queue that grows without bound is just a slower way to fail.

**The framing that lands:** the goal isn't preventing failure, it's **containing the blast radius**. Then mention testing it — chaos engineering, or at minimum a game day. → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

---

### Q9. [Advanced] Design a system where correctness matters more than availability — say, payments.

**Strong answer covers:** flip the usual defaults. Choose **CP**: refuse to process rather than risk a double-charge. Every operation gets an **idempotency key**. Use a **saga** with explicit compensating transactions rather than 2PC across services (2PC blocks if the coordinator dies, and holds locks the whole time). Maintain an **append-only ledger** as the source of truth — never mutate a balance in place; balances are derived from immutable entries, which makes every state reconstructible and auditable.

**Reconciliation is the part people forget:** an out-of-band job that compares your ledger against the provider's and flags divergence. Distributed systems drift; assume it and detect it rather than assuming correctness.

**Lead with your own experience** — you've built [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|a direct-debit sandbox]]. Real domain experience beats a textbook answer every time.

---

### Q10. [Intermediate] The interviewer says "now make it 10× bigger." What do you do?

**Strong answer covers:** don't redesign — **find the first thing that breaks**. Walk the request path and name the constraint at each hop: is it the database's write throughput? Connection count? A single-instance component? The cache's memory? Fan-out amplification?

**The behaviour they're grading:** identifying *the* bottleneck rather than uniformly scaling everything. Uniform scaling is what people do when they can't tell where the limit is. Then say what you'd measure to confirm before spending money.

**A strong closer:** "and at 10× I'd want to know whether the traffic is uniform or bursty, because those need completely different answers" — bringing it back to requirements shows the framework wasn't just a ritual at the start.
