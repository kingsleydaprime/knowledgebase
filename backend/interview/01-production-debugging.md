# Node Interview — Production Debugging

**Written from a real interview (August 2026)** that went badly. Every question below was actually asked. They form one coherent theme — *can you diagnose a production incident?* — which is [[PRIMETECHIE|Rank II, the Diagnostician]]. Not obscure trivia: the layer that separates people.

---

### Q1. 🔥 Your p99 latency spikes. What do you check?

**The framing first, because it halves the search space before you look at anything:**

> **Is p50 also up, or only p99?**
> - **Both up** → systemic. Saturation, a slow downstream, connection-pool queueing.
> - **Only p99, p50 flat** → episodic. Something *periodically* stalls a subset of requests: GC, a blocked event loop, CPU throttling, a lock.
>
> **Is it periodic?** A regular sawtooth points at GC, a cron job, or synchronised cache expiry. **Did it start at a specific time?** Correlate with deploys, traffic, and dependency changes.

**Then, Node-specific, in order of likelihood:**

1. **Event loop lag — the number one cause in Node, and the thing they're really asking about.** Node is single-threaded; *any* synchronous work blocks **every** queued request. A 200ms sync operation doesn't make one request slow, it makes every request that arrives during those 200ms slow. That's exactly the shape of "p99 spikes, p50 fine, CPU looks fine."

   Usual culprits: `JSON.parse`/`stringify` on a large payload, sync crypto (`pbkdf2Sync`, `randomBytes` sync form), sync zlib, `fs.*Sync`, a big `.map`/`.sort` over thousands of rows, **catastrophic regex backtracking (ReDoS)** on user input, and template rendering.

   Measure it — don't guess:
   ```js
   const { monitorEventLoopDelay } = require('node:perf_hooks');
   const h = monitorEventLoopDelay({ resolution: 10 });
   h.enable();
   setInterval(() => {
     console.log({ p50: h.percentile(50), p99: h.percentile(99), max: h.max });
     h.reset();
   }, 10_000).unref();
   ```
   Export that as a metric. `clinic doctor` and `0x` give you the flame graph.

2. **GC pauses.** `--trace-gc`, or `perf_hooks` GC observer. Major (old-space) collections stop the world. Rising heap between collections means a leak; high allocation rate means churn. Check whether spike magnitude ≈ pause duration.

3. **CPU saturation on one core.** One Node process = one core for JS. Check per-process CPU, not host average. If you're at 100% of one core on a 8-core box, the host looks 12% busy and you're completely saturated. `cluster` or multiple containers behind the LB.

4. **cgroup CPU throttling.** In Kubernetes/ECS, a CPU *limit* is enforced by throttling within a 100ms period. A bursty service gets throttled while showing low average CPU. Check `container_cpu_cfs_throttled_seconds_total`. **This is the single most misdiagnosed container latency problem.**

5. **Connection pool / socket queueing.** Time spent *waiting for* a database connection or an HTTP agent socket doesn't appear in the query duration. Instrument pool wait time separately. A pool of 10 with 50 concurrent requests means 40 are queued and invisible.

6. **Downstream latency.** Traces, not logs. And check *its* p99, not its average.

7. **Tail amplification.** If one request fans out to N downstream calls, you wait for the slowest. At p99=1s and N=200, you hit it essentially every time. → Q3.

8. **Infrastructure:** noisy neighbour, autoscaling cold starts, TLS handshakes from connection churn (no keep-alive), DNS timeouts, [[foundations/networking/15-network-performance|RTO after tail loss or incast]].

**What scores:** name your instrument for each hypothesis rather than listing causes. "I'd look at event loop delay percentiles first, because Node's failure mode is that one blocking operation makes a burst of requests slow, which is the p99-up/p50-flat shape."

---

### Q2. 🔥 You track request counts per availability zone. Why?

**Two separate reasons, and strong answers give both:**

1. **To localise a failure.** Tag every metric with an `az` dimension. If errors or latency concentrate in one AZ, it's infrastructure. If they're spread evenly, it's your application. This is the discriminator that answers Q3.

2. **Because uneven counts are themselves a bug signal.** If AZ-a is serving 60% of traffic and AZ-b 20%, something is wrong *before* any errors appear: unhealthy targets silently removed from a target group, cross-zone load balancing disabled, sticky sessions clumping, or DNS/client-side balancing skew. Uneven request distribution over even capacity means some instances are running hot — and *those* are the ones whose p99 goes first.

**The detail that shows operational experience:** cross-AZ traffic costs money and adds ~1–2ms, so people enable zone-aware routing — which then means **an AZ with fewer healthy instances gets the same share of traffic as one with more.** You've traded a cost problem for a load-imbalance problem, and you need per-AZ request *and* per-instance metrics to see it.

---

### Q3. 🔥 Errors are spiking. Is an AZ impaired, or did the recent deploy break it?

**The discriminators, in the order you'd check them:**

| Signal | Points to AZ impairment | Points to the deploy |
|---|---|---|
| **Errors by `az` tag** | concentrated in one AZ | spread evenly across all AZs |
| **Errors by `version`/build tag** | spread across old and new | concentrated on the new version |
| **Old vs new instances in the *same* AZ** | both bad | only new ones bad |
| **Onset time** | no correlation with deploy | matches deploy start, or the rollout crossing a % of fleet |
| **Cloud health signals** | EC2 status checks failing, LB healthy-host count down in one AZ, cross-AZ latency up | normal |
| **Blast radius** | your *dependencies* are also degraded (RDS failover, EBS latency) | only your service |

**The answer they want:** *"if my metrics are tagged with both `az` and `version`, this is a single dashboard query, not an investigation."* The real skill is having built the diagnostic capability before the incident — that's the point of Q2.

**And mitigate before you finish diagnosing** — both candidates have a fast, reversible action:
- **Roll back the deploy.** If it recovers → it was the deploy.
- **Evacuate the AZ** (shift traffic away / remove from the LB). If it recovers → it was the AZ.

Do the cheaper/faster one first. You are not obliged to know the answer before acting — you're obliged to stop the bleeding and *then* find out. Saying that out loud is what separates a senior answer here.

**The confounder worth naming:** a deploy can *look* AZ-localised if your rollout is zone-by-zone. Check whether your deployment strategy rolls per-AZ before concluding.

---

### Q4. 🔥 An N+1 query regression shipped. How did it get in, how do you catch it, how do you fix it?

**How it gets in:** almost always innocently. Someone accesses a lazy ORM relation inside a loop; a serialiser starts including a nested field; a GraphQL resolver gets a new child field. The code looks fine and **works perfectly on dev data**. With 10 rows it's 11 queries; with 5,000 rows it's 5,001.

**Why it's a *latency* incident and not just a slow endpoint — this is the part most people miss:** N+1 doesn't only make one route slow. It **holds a database connection for the entire duration** and issues thousands of round trips. With a pool of 10, a handful of concurrent N+1 requests exhaust the pool and **every other endpoint starts queueing**. That's how one careless `.map` produces a service-wide p99 spike — which ties this question straight back to Q1.

**How to catch it:**
- **Assert query counts in tests.** Instrument the driver, wrap the request, `expect(queryCount).toBeLessThan(5)`. This is the only method that catches it *before* production.
- APM / OpenTelemetry spans per query — an N+1 is visually unmistakable in a trace: a picket fence of identical spans.
- Log slow-request query counts in production.

**How to fix it:**
- **Eager load / `JOIN`** — Prisma `include`, TypeORM `relations`, Sequelize `include`, or a raw join.
- **`DataLoader`** — *the* Node answer, and the one they were probably fishing for. It batches all loads requested within one tick of the event loop into a single query, and caches per request. It's the standard fix for GraphQL N+1 and works fine outside GraphQL.
  ```js
  const userLoader = new DataLoader(async (ids) => {
    const rows = await db.user.findMany({ where: { id: { in: ids } } });
    const byId = new Map(rows.map(r => [r.id, r]));
    return ids.map(id => byId.get(id) ?? null);   // MUST return in input order, same length
  });
  ```
  The ordering contract is the thing people get wrong — return one result per input key, in order, nulls included.
- **Projections / DTO queries** — select exactly what the response needs.

**Not a fix:** switching everything to eager loading. That drags the whole object graph into every query and creates the opposite problem.

---

### Q5. 🔥 A request timed out. Is it safe to retry?

**Only if the operation is idempotent — and a timeout tells you nothing about whether it succeeded.** The server may have processed it fully and the *response* was lost. You cannot distinguish "never arrived" from "arrived, succeeded, reply lost." That ambiguity is fundamental, not an implementation gap.

**So:**
- **Safe to retry automatically:** `GET`, `HEAD`, `PUT`, `DELETE` — idempotent by definition.
- **Not safe:** `POST`, `PATCH` — unless you've *made* them safe.

**How you make them safe — idempotency keys:**
```js
// client sends a stable key it generates once and reuses across retries
headers: { 'Idempotency-Key': requestId }

// server, inside ONE transaction:
//   1. INSERT the key (unique constraint) — if it conflicts, this is a retry
//   2. do the work
//   3. store the response body against the key
// on a retry: return the stored response, don't re-execute
```
The critical detail: **the key insert and the effect must be in the same transaction** (or the key must have a unique constraint enforced by the database). If you check-then-insert in two steps, two concurrent retries both pass the check and you've just moved the race.

**Also worth saying:** natural idempotency is better than bolted-on. `SET balance = 100` is idempotent; `INCREMENT balance BY 10` isn't. Where you can express the operation as a desired state rather than a delta, do.

→ [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]] · [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency in depth]]

---

### Q6. 🔥 How do you prevent a retry storm?

**The failure mode:** a dependency slows down → everyone retries → the dependency gets *more* load precisely when it's least able to handle it → it fails harder → more retries. A **metastable failure**: the system stays down even after the original trigger is gone, because retries are now the load. This is how a 30-second blip becomes a 40-minute outage.

**The controls, roughly in order of importance:**

1. **Exponential backoff with jitter — and *full* jitter, not "backoff plus a little randomness."**
   ```js
   // AWS "Exponential Backoff And Jitter" — full jitter
   const delay = Math.random() * Math.min(cap, base * 2 ** attempt);
   ```
   Without jitter, every client that failed at the same moment retries at the same moment. You've built a synchronised thundering herd with extra steps. **Jitter is the part people forget and it's the part that matters most.**

2. **Retry budgets, not just attempt caps.** Cap retries as a *fraction of total request volume* — e.g. retries may not exceed 10% of requests. A per-request cap of 3 still permits 3× amplification fleet-wide; a budget bounds the aggregate. This is what gRPC and Envoy implement, and naming it is a strong senior signal.

3. **Don't retry at every layer.** Retries **multiply**: 3 attempts at 3 layers is 27× load on the bottom service. Pick **one** layer to retry at and make the others fail fast. This is the most common real-world cause of amplification.

4. **Circuit breaker.** After N failures, stop calling entirely for a cooldown, then let one probe through. Protects the dependency *and* frees your own resources instead of tying them up in doomed calls.

5. **Only retry retryable things.** Timeouts, connection errors, 502/503/504, and 429 *with* `Retry-After`. Never retry a 400 or a 422 — the answer will not change.

6. **Deadline propagation.** Pass the caller's remaining time budget downstream so retries can't exceed it. Retrying after the client has already given up is pure waste.

7. **Server-side load shedding.** The receiving side must protect itself — reject fast with 429/503 when the queue is deep. You can't rely on every client being well-behaved.

→ [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]

---

## The through-line

Every question here is one question: **when it breaks, can you narrow the search space instead of guessing?** Q1 is bisecting a latency distribution, Q3 is bisecting by metric dimension, Q4 is bisecting a regression to a code change, Q5–Q6 are about not making it worse.

The prerequisite for all of it is **having tagged your telemetry with the dimensions you'll need** (az, version, instance, route) *before* the incident. That's the actual senior skill, and it's a design decision, not a debugging one.

## Related
- [[backend/interview/02-node-runtime-and-api|Node Runtime & API]] — the language half of the same interview
- [[foundations/networking/interview/04-debugging-and-scenarios|Networking: debugging scenarios]] — the same method one layer down
- [[devops/interview/01-linux-containers-and-operations|DevOps: incidents & observability]]
- [[PRIMETECHIE|The Primetechie Path]] — this is Rank II, in full
