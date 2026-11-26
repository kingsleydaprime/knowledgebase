---
id: 0035c5ad-2208-4888-b761-fa490287d03c
kind: interview-bank
---

# Backend Interview Questions: Production Debugging

These questions ask one thing: when a live system is slow or failing, can you narrow down the cause instead of guessing? Every one of them was asked in a real interview in August 2026, one that went badly, which is why they're worth drilling. It's [[PRIMETECHIE|Rank II, the Diagnostician]].

## Reading the signals

### Your p99 latency spikes
<!-- q: interview id="5d0c9a31" level="intermediate" hot="2" pace="5" -->

Your service's p99 latency is spiking. Talk me through what you check, and in what order.

<details><summary>Strong answer</summary>

**Strong answer covers:**

- It first asks whether p50 is up too. Both up means something systemic (saturation, a slow downstream, a queue). Only p99 up means something stalls a few requests now and then.
- It asks whether the spikes are periodic, or started at a set time, and checks them against deploys, traffic and dependency changes.
- It names event loop delay as the first thing to check in Node: one thread, so any synchronous work (a big `JSON.parse`, sync crypto, a heavy regex, a large sort) makes every request that arrives meanwhile slow.
- It names garbage-collection pauses as the next suspect, checked with `--trace-gc`.
- It checks CPU per process, not per host (one Node process uses one core), and cgroup CPU throttling in containers, which hides behind a low average CPU.
- It checks time spent waiting for a database connection or an HTTP socket, which never shows up in the query's own duration.
- It names the tool for each suspect rather than listing causes, for example "event loop delay percentiles first, because that's Node's p99-up, p50-flat shape".

**Follow-up:** How would you actually measure event loop delay in a running service?

**Detail worth adding:** Node has it built in, in `perf_hooks`. Export it as a metric, and use `clinic doctor` or `0x` for a flame graph when it's high:

```js
const { monitorEventLoopDelay } = require('node:perf_hooks');
const h = monitorEventLoopDelay({ resolution: 10 });
h.enable();
setInterval(() => {
  console.log({ p50: h.percentile(50), p99: h.percentile(99), max: h.max });
  h.reset();
}, 10_000).unref();
```

**Revise:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and concurrency models]], [[backend/07-practices/03-load-and-performance-testing|Load and performance testing]].

</details>

### Request counts per availability zone
<!-- q: interview id="9b47e2c0" level="intermediate" hot="1" pace="3" -->

Your team tracks request counts per availability zone (AZ). Why would you do that?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- It gives two reasons, not one.
- The first: tagging every metric with its AZ tells you where a failure lives. Errors piled up in one AZ point at the infrastructure; errors spread evenly point at your own code.
- The second: uneven request counts are a warning before any error appears. Some instances are running hot, and theirs is the p99 that goes first.
- It names the usual causes of uneven counts: unhealthy targets quietly dropped from the load balancer, cross-zone load balancing turned off, sticky sessions clumping, or DNS and client-side balancing skew.

**Follow-up:** To save on cross-AZ costs, your team turns on zone-aware routing. What new problem can that create?

**Detail worth adding:** Cross-AZ traffic costs money and adds about 1–2 ms, so zone-aware routing keeps traffic in its own zone. But then an AZ with fewer healthy instances still gets the same share of traffic as one with more, so those instances run hot. You've swapped a cost problem for a load problem, and you need request counts per AZ *and* per instance to see it.

**Revise:** [[networking/interview/04-debugging-and-scenarios|Networking: debugging scenarios]].

</details>

### AZ problem or bad deploy?
<!-- q: interview id="e2a6f417" level="advanced" hot="2" pace="5" -->

Errors are spiking. Either one availability zone is impaired, or the deploy that just went out is broken. How do you tell which, and what do you do while you find out?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- It splits errors by AZ: piled up in one AZ points at the zone; spread evenly points at the deploy.
- It splits errors by version: concentrated on the new build points at the deploy.
- It compares old and new instances in the same AZ. Only the new ones failing means the deploy.
- It checks timing (did errors start with the deploy, or when the rollout passed some share of the fleet?) and the cloud's own health signals (failing status checks, fewer healthy hosts in one AZ, your database or disks also struggling).
- It stops the damage before finishing the diagnosis: roll back, or move traffic away from the AZ, whichever is cheaper and faster. Whichever one fixes it also tells you the cause.
- It points out that if metrics are already tagged with AZ and version, this is one dashboard query, not an investigation.

**Follow-up:** Your rollout goes out one zone at a time. How could that fool you?

**Detail worth adding:** A zone-by-zone rollout makes a bad deploy *look* like a zone problem, because at first the new version lives in only one AZ. So before blaming the zone, check how the rollout runs, and compare old and new instances inside that same zone.

**Revise:** [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]].

</details>

## Regressions and retries

### An N+1 query regression shipped
<!-- q: interview id="41fd8b6e" level="intermediate" hot="2" pace="5" -->

An N+1 query regression made it to production. How did it get in, why did it hurt the whole service, and how do you catch and fix it?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- How it gets in: innocently, such as a lazy ORM relation read inside a loop, or a serialiser that starts including a nested field. It works fine on small dev data: 10 rows is 11 queries, 5,000 rows is 5,001.
- Why it hurts everything: each N+1 request holds a database connection the whole time, so a few at once empty the pool and every other endpoint starts queueing. One endpoint becomes a service-wide p99 spike.
- How to catch it before production: count queries in tests and fail when the count is too high.
- How to see it in production: a trace shows a long fence of identical query spans.
- How to fix it: load the related rows up front with a join or the ORM's `include`, or batch the loads with `DataLoader`, or select only the fields the response needs.
- It says eager-loading everything is *not* the fix, because that drags the whole object graph into every query.

**Follow-up:** You fix it with `DataLoader`. What must your batch function do, or it gives wrong answers?

**Detail worth adding:** It must return exactly one result per key, in the same order as the keys, with `null` where a row is missing. The database returns rows in its own order and skips missing ones, so map them back:

```js
const userLoader = new DataLoader(async (ids) => {
  const rows = await db.user.findMany({ where: { id: { in: ids } } });
  const byId = new Map(rows.map(r => [r.id, r]));
  return ids.map(id => byId.get(id) ?? null);
});
```

`DataLoader` batches every load asked for in one tick of the event loop into a single query, and caches results per request.

**Revise:** [[backend/04-data-and-persistence/01-databases-in-the-backend|Databases in the backend]].

</details>

### Is it safe to retry a timed-out request?
<!-- q: interview id="b8c3105d" level="intermediate" hot="2" pace="4" -->

A request to another service timed out. Is it safe to retry it?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- A timeout doesn't tell you whether the request worked. The server may have done the work and only the reply got lost, and you can't tell those apart.
- So it's only safe if the operation is idempotent, meaning that doing it twice has the same effect as doing it once.
- `GET`, `HEAD`, `PUT` and `DELETE` are idempotent by definition. `POST` and `PATCH` aren't, unless you make them so.
- You make them safe with an idempotency key: the client creates one key per operation and sends the same key on every retry. The server stores the result against the key and returns it on a repeat instead of doing the work again.
- Where you can, choose operations that are naturally idempotent: "set the balance to 100" can run twice safely; "add 10 to the balance" can't.

**Follow-up:** Two retries with the same idempotency key arrive at the same moment. How do you stop both of them doing the work?

**Detail worth adding:** Store the key and do the work in **one transaction**, with a unique constraint on the key, so the database lets only one of them in. If you check "have I seen this key?" and then insert it as two separate steps, both retries pass the check and you've just moved the race.

**Revise:** [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and retries]], [[architecture/04-distributed-systems/10-distributed-transactions|Distributed transactions]].

</details>

### Preventing a retry storm
<!-- q: interview id="7f2e9ac4" level="advanced" hot="2" pace="5" -->

How do you stop retries from turning a short blip in a dependency into a long outage?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- It describes the failure: the dependency slows, everyone retries, the extra load hits just when it's weakest, and it stays down even after the original cause is gone, because the retries are now the load.
- It backs off exponentially between retries, with random jitter.
- It caps retries with a budget across all traffic (for example, retries may be at most 10% of requests), not just a per-request attempt limit.
- It retries at one layer only. Retries multiply: 3 attempts at each of 3 layers is 27 times the load at the bottom.
- It uses a circuit breaker: after repeated failures, stop calling for a while, then let one probe through.
- It retries only errors that can change (timeouts, connection errors, 502, 503, 504, and 429 with `Retry-After`), never a 400 or 422.
- It passes the caller's remaining time downstream so retries stop once the caller has given up, and has the server reject quickly (429 or 503) when its queue is too deep.

**Follow-up:** Why full jitter, rather than plain exponential backoff?

**Detail worth adding:** Without jitter, every client that failed at the same moment retries at the same moment, wave after wave: a synchronised herd. Full jitter picks a random delay anywhere between zero and the backoff ceiling, which spreads the retries out:

```js
const delay = Math.random() * Math.min(cap, base * 2 ** attempt);
```

**Revise:** [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and retries]], [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]].

</details>

## The thread running through them

Every question here is the same question: when it breaks, can you narrow the search instead of guessing? The p99 question splits a latency distribution, the AZ question splits by metric tag, the N+1 question splits a regression down to a code change, and the retry questions are about not making things worse while you look.

All of it depends on one decision made *before* the incident: tagging your metrics with what you'll need to split by (AZ, version, instance, route).

## Related

- [[backend/interview/02-node-runtime-and-api|Node runtime and API]]: the language half of the same interview.
- [[networking/interview/04-debugging-and-scenarios|Networking: debugging scenarios]]: the same method one layer down.
- [[devops/interview/01-linux-containers-and-operations|DevOps: incidents and observability]].
- [[PRIMETECHIE|The Primetechie Path]]: this is Rank II in full.
