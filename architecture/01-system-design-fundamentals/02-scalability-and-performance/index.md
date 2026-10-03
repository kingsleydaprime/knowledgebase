# Scalability & Performance

> **[Intermediate]** · From the roadmap.sh system-design roadmap. The vocabulary that's constantly confused, made precise: performance and scalability, latency and throughput, averages and percentiles, scaling up and scaling out. It also covers the arithmetic underneath: why a server's response time explodes as it nears full, why a system is only as fast as its slowest stage, and why adding machines eventually stops helping. The worked example follows a checkout service through a sale, from "it's slow" to a diagnosis and a fix. The lab checks every number.

## Before you start

You can already:

- Run the five-step design method, including finding bottlenecks in step 5 → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|how to approach system design]].
- Explain Little's law: the number of requests in a system equals the arrival rate times the time each one stays → [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]] (helpful, not required).
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Tell a performance problem from a scalability problem by comparing latency under light and heavy load, and name the fix for each.
2. Read a latency distribution: work out p50, p95 and p99, and explain why the average misleads.
3. Predict how a server's response time grows with utilisation, and say why to keep servers well below full.
4. Find a system's bottleneck from its stages' capacities, and explain why adding machines has a ceiling.

**Study route:** sections 1–4 build the ideas. Stop at the predictions in section 5 and try them before reading on. Section 6 is the lab.

## The kid version

A school canteen has one dinner lady. With five children in the queue, everyone is served in a minute; with fifty, the last child waits twenty. Her serving speed didn't change, but the queue did. If she's slow even with no queue, she needs a faster method, which is a **performance** problem. If she's quick alone but swamped at lunchtime, she needs help, which is a **scalability** problem. Adding a second server helps, until both are waiting on the one person who refills the trays. Then the trays are the bottleneck.

**Where the analogy stops working.** In a canteen you can see the queue. In a system it's hidden inside servers, connection pools and databases, so you only see it in the measurements, as the slow tail of response times. That's why this lesson leans on percentiles.

## 1. Why this exists

An online shop runs a sale. Before it starts, checkout answers in about 45 milliseconds. An hour in, customers complain it takes seconds, and some give up. Someone says "the code is slow, let's optimise it", and someone else says "add more servers". They can't both be right, and each fix costs days. The first question decides which: **is checkout slow when it's quiet, or only when it's busy?** This lesson gives you the words and numbers to answer it, and to predict the next limit before the next sale finds it.

## Terms used in scalability and performance

1. **Performance**: This is how fast the system is for one request, when nothing else is competing for it.
2. **Scalability**: This is how well the system keeps its performance as load grows: more users, requests or data.
3. **Latency**: This is the time one request takes, from being sent to its answer arriving. It's measured in milliseconds.
4. **Throughput**: This is how many requests the system completes in a unit of time, such as requests a second.
5. **Percentile**: This is the value that a given share of measurements fall at or below. **p50**, also called the **median**, is the latency that half of requests beat. **p99** is the latency that 99% beat, so 1 in 100 requests is slower.
6. **Tail latency**: This is the latency of the slowest requests, usually p99 or p99.9. It matters because a page making many calls waits for its slowest one, and busy users make many requests.
7. **Utilisation**: This is the share of time a server is busy. It equals the arrival rate times the time each request takes: 80 requests a second of 10 ms each keep a server 80% busy.
8. **Vertical scaling**: This is also known as **scaling up**. It means handling more load by moving to a bigger machine, with more processors and memory.
9. **Horizontal scaling**: This is also known as **scaling out**. It means handling more load by adding more machines and spreading the requests across them.
10. **Stateless server**: This is a server that keeps nothing about a user between requests, so any server can handle any request. Sessions and data live in a shared database or cache instead.
11. **Bottleneck**: This is the stage that limits the whole system's throughput, because every request passes through it and it runs out first.
12. **Contention**: This is machines or threads waiting for something only one can use at a time, such as a lock or a single database row.
13. **Coherence cost**: This is the work machines do to keep each other up to date, such as copying changes to each other. It grows with every pair of machines, not just with each machine.

## 2. Performance versus scalability

A system can be fast for one user and collapse at 10,000, which is fast but doesn't scale. Or it can handle millions while each request is sluggish, which scales but performs badly. The diagnostic: **if latency grows as load rises, you have a scalability problem; if it's slow even under light load, you have a performance problem.** They need different fixes, so say which one you have.

- A **performance** problem is fixed by doing less work per request: a better query, an index, a cache, a faster algorithm. More servers won't help, because each request is still slow on its own.
- A **scalability** problem is fixed by adding capacity or removing the thing everyone waits for: more servers, splitting the load, removing a lock. Faster code helps only as much as it shortens the queue.

## 3. Latency, throughput, and why the average lies

**Latency** is the time for one request; **throughput** is how many complete a second. They interact. Batching raises throughput but adds latency, because the first item in a batch waits for the last. A queue smooths throughput at the cost of latency. Aim for the most throughput at an *acceptable* latency, not for either one alone.

Latency is a distribution, not a number. Look at 1,000 requests where 98% take 40–60 ms and 2% hit something slow, such as a cold cache, a lock or a retry, and take 1.5–2.5 seconds:

```
average   93 ms   ← describes no actual request
p50       50 ms   ← the typical request
p95       59 ms
p99    2,208 ms   ← 1 in 100 requests: over 2 seconds
```

The average is nearly double the typical request, yet far below what the unlucky 1% see. That's why service targets are written as percentiles: "p99 under 300 ms" ([[devops/10-observability/01-observability-fundamentals/index|observability]] covers measuring them). Tail latency matters more than it looks. A page that makes 20 calls has about an 18% chance that at least one of them is slower than p99 (1 − 0.99^20), and your most active users make the most requests.

To work out a percentile by the **nearest-rank method**: sort the measurements, and take the one at position ⌈p/100 × n⌉. For p99 of 1,000 measurements, that's the 990th smallest.

## 4. Why waiting explodes as a server fills up

In words: a request's time in a server is its work plus its wait in the queue, and the wait grows faster and faster as the server gets busier. When requests arrive at random, as real traffic does, the classic model (called M/M/1) gives the average time in the server as the work time divided by the share of time the server is idle.

With $S$ for the time one request's work takes and $\rho$ (rho) for utilisation, from 0 to 1:

$$T = \frac{S}{1 - \rho}$$

For a request with 10 ms of work:

```
utilisation   50%    80%    90%    95%    99%    100%
average time  20 ms  50 ms  100 ms 200 ms 1 s    no limit
```

Going from 50% to 80% busy adds 30 ms; going from 90% to 99% adds 900 ms. The tail is worse still. In this model, p99 is about 4.6 times the average, so at 90% busy a 10 ms job has a p99 near half a second. That's why servers are run well below full, often at 50–70% at peak. The headroom isn't waste; it's what keeps the queue short. The lab simulates the server request by request and checks that it agrees with the formula.

The model assumes one server, random arrivals and random work times. A real server has several workers, so its curve stays flatter for longer and then rises more steeply near full. The shape, slow and then sudden, holds either way.

## 5. Worked example: checkout during a sale

**The measurements.** Before the sale, checkout's p50 is 45 ms. During it, p99 is around 2 seconds.

**Predict before reading on.** Is this a performance or a scalability problem? What would you check next?

<details>
<summary>After your prediction</summary>

It's fast when quiet and slow when busy, so it's a **scalability** problem: more requests are waiting, not each one working longer. The next thing to check is utilisation: how busy each stage is during the sale.

</details>

**Step 1: find the utilisation.** Each checkout needs about 10 ms of a server's time, so one server can do at most 100 a second. During the sale, 95 a second arrive: 95% busy. The formula predicts an average of 200 ms, with a p99 several times that. That matches what customers see.

**Step 2: compare with a performance problem.** If instead each checkout needed 300 ms of work, the server would take 333 ms on average even at 10% busy. A second server would barely help (316 ms), because nothing is queueing. Only faster code would.

**Step 3: scale out.** A second server halves the load on each, to 47.5%, and the average drops to 19 ms. But that only works if any server can handle any request. Checkout keeps the basket in server memory, so a customer's second request might land on a server that doesn't have it. The basket has to move to a shared store first, which makes the servers **stateless**. That's the most important enabler of horizontal scaling.

**Step 4: find the next bottleneck.** Now look at the whole path:

```
load balancer      50,000 a second
app servers         3,200 a second   (4 servers × 800)
database writes     2,000 a second   ← the bottleneck
```

Every checkout writes to the database, so the system handles 2,000 a second, however many app servers there are. Doubling them to eight changes nothing. The next sale's fix is in the database: batching writes, moving slow work to a queue, or splitting the data. Scaling is a sequence of finding the current bottleneck and relieving it, and each fix moves the bottleneck somewhere else.

## 6. Vertical versus horizontal scaling

There are two ways to handle more load:

| | Vertical (scale up) | Horizontal (scale out) |
|---|---|---|
| How | a bigger machine (more processors and memory) | more machines |
| Simplicity | simple: no code changes, no distribution | complex: needs [[architecture/02-building-blocks/01-load-balancing-and-proxies\|load balancing]], stateless servers, [[architecture/04-distributed-systems/index\|distributed-systems]] concerns |
| Ceiling | a hard limit: the biggest machine you can buy | much higher, but not unlimited (below) |
| Failure | a single point of failure | survives losing a machine |
| Cost | expensive at the top end | commodity hardware, but more of it |

**Start vertical**, because it's simpler and modern machines are huge; don't distribute before you must. **Scale horizontally when you hit the ceiling or need to survive a machine failing.** Horizontal scaling needs statelessness: application servers hold no per-user state, so any server can serve any request, and state lives in a shared [[architecture/02-building-blocks/03-databases-at-scale|database]] or [[architecture/02-building-blocks/02-caching|cache]].

### Why adding machines has a ceiling

**Amdahl's law** says, in words: if part of the work can't be split across machines, that part sets a limit on the speed-up, however many machines you add. With $s$ for the share of work that can't be split and $n$ machines:

$$\text{speed-up}(n) = \frac{1}{s + \frac{1 - s}{n}}$$

If 5% can't be split, 8 machines give 5.9 times the speed, and no number of machines gives more than $1/s = 20$.

**The universal scalability law** adds what Amdahl leaves out. Machines also wait for each other (**contention**, $\alpha$) and must keep each other in step (**coherence**, $\beta$). Coherence grows with every *pair* of machines, so past a certain point adding machines lowers capacity:

$$C(n) = \frac{n}{1 + \alpha(n - 1) + \beta n(n - 1)}$$

With 5% contention and 0.1% coherence cost, capacity peaks at about $\sqrt{(1 - \alpha)/\beta} \approx 31$ machines, at 9 times one machine. At 60 machines it's back down to 8 times, and at 100 machines 6.3 times. The numbers are illustrative; in practice $\alpha$ and $\beta$ are fitted from load-test measurements. The lesson is real, though: the fix for a contended lock or a chatty protocol is to remove it, not to add machines.

### The scaling toolkit (a preview)

When one server isn't enough, these are the standard moves, each with its own lesson:

1. **Add a [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancer]]** and more stateless app servers, to scale compute horizontally.
2. **[[architecture/02-building-blocks/02-caching|Cache]]** hot data to take reads off the database, which is usually the first bottleneck.
3. **[[architecture/02-building-blocks/03-databases-at-scale|Scale the database]]**: read replicas for read-heavy load, sharding for write-heavy load.
4. **[[architecture/02-building-blocks/04-messaging-and-async|Go asynchronous]]**: move slow work to a queue so requests return quickly.
5. **Use a [[architecture/02-building-blocks/01-load-balancing-and-proxies|CDN]]** to serve static content from near users.

## 7. Runnable example: the numbers behind this lesson

`scaling.ts` has percentiles, the queueing formula, a request-by-request server simulation with a seeded random generator (so every run sees the same traffic), the bottleneck rule, and both scaling laws. `scaling.test.ts` checks every number used above.

```ts
// scaling.ts — the arithmetic behind performance and scalability: percentiles, how waiting grows as a server
// fills up, the bottleneck that sets a system's throughput, and why adding machines stops helping.
// These are models: each function says what it assumes.

/** The value at or below which p% of samples fall (the nearest-rank method). p99 of 1,000 samples is the 990th smallest. */
export function percentile(samples: readonly number[], p: number): number {
  if (samples.length === 0) throw new RangeError("no samples");
  const sorted = [...samples].sort((a, b) => a - b);
  const rank = Math.max(1, Math.ceil((p / 100) * sorted.length));
  return sorted[rank - 1];
}

export function mean(samples: readonly number[]): number {
  return samples.reduce((sum, x) => sum + x, 0) / samples.length;
}

/** A small seeded random number generator (mulberry32), so every run sees the same "random" traffic. */
export function seeded(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** An exponentially distributed wait with the given mean: how long until the next random event. */
function exponential(random: () => number, mean: number): number {
  return -mean * Math.log(1 - random());
}

/**
 * Average time a request spends in a single server, waiting plus being served, when requests arrive at random
 * and service times vary at random (the M/M/1 queueing model): service time ÷ (1 − utilisation).
 * Utilisation is the fraction of time the server is busy: arrival rate × service time.
 */
export function responseTime(serviceMs: number, utilisation: number): number {
  return utilisation >= 1 ? Infinity : serviceMs / (1 - utilisation);
}

/** The same server, simulated request by request, to check the formula and to see the tail it doesn't show. */
export function simulateServer(serviceMs: number, utilisation: number, requests: number, seed: number) {
  const random = seeded(seed);
  const gapMs = serviceMs / utilisation; // average time between arrivals
  let arrives = 0;
  let free = 0; // when the server finishes its current request
  const times: number[] = [];
  for (let i = 0; i < requests; i++) {
    arrives += exponential(random, gapMs);
    const starts = Math.max(arrives, free); // wait if the server is busy
    free = starts + exponential(random, serviceMs);
    times.push(free - arrives);
  }
  return { mean: mean(times), p50: percentile(times, 50), p99: percentile(times, 99) };
}

export interface Stage {
  name: string;
  perSecond: number; // the most requests this stage can handle a second
}

/** A request passes through every stage, so the system handles only as many as its slowest stage. */
export function throughput(stages: readonly Stage[]): { perSecond: number; bottleneck: string } {
  const slowest = stages.reduce((a, b) => (b.perSecond < a.perSecond ? b : a));
  return { perSecond: slowest.perSecond, bottleneck: slowest.name };
}

/** Amdahl's law: n machines speed up the part that can be split, not the part that can't (`serial`, 0 to 1). */
export function amdahl(n: number, serial: number): number {
  return 1 / (serial + (1 - serial) / n);
}

/**
 * The universal scalability law: capacity of n machines relative to one, when they also wait for each other
 * (contention, alpha) and must keep each other in step (coherence, beta). Past a point, adding machines lowers it.
 */
export function usl(n: number, alpha: number, beta: number): number {
  return n / (1 + alpha * (n - 1) + beta * n * (n - 1));
}

/** Where the universal scalability law peaks: the number of machines that gives the most capacity. */
export function uslPeak(alpha: number, beta: number): number {
  return Math.sqrt((1 - alpha) / beta);
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { amdahl, mean, percentile, responseTime, seeded, simulateServer, throughput, usl, uslPeak } from "./scaling.ts";

test("percentiles, by the nearest-rank method", () => {
  const tens = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5]; // order doesn't matter
  assert.deepEqual([50, 90, 99, 100].map((p) => percentile(tens, p)), [5, 9, 10, 10]);
  assert.throws(() => percentile([], 50), RangeError);
});

test("an average hides the slow requests that p99 shows", () => {
  const random = seeded(42);
  const latencies: number[] = [];
  for (let i = 0; i < 1_000; i++) {
    const slow = random() < 0.02; // 2% of requests hit something slow: a cold cache, a lock, a retry
    latencies.push(slow ? 1_500 + 1_000 * random() : 40 + 20 * random());
  }
  const [avg, p50, p95, p99] = [mean(latencies), ...[50, 95, 99].map((p) => percentile(latencies, p))].map(Math.round);
  assert.deepEqual({ avg, p50, p95, p99 }, { avg: 93, p50: 50, p95: 59, p99: 2_208 });
  // The average describes nobody: 98% of requests take 40–60 ms, and 1 in 100 takes over 2 seconds.
});

test("waiting grows slowly, then all at once, as a server fills up", () => {
  const ms = [0.5, 0.8, 0.9, 0.95, 0.99].map((busy) => Math.round(responseTime(10, busy)));
  assert.deepEqual(ms, [20, 50, 100, 200, 1_000]); // 10 ms of work; the rest is queueing
  assert.equal(responseTime(10, 1), Infinity); // at 100% the queue grows without limit
});

test("the simulated server agrees with the formula, and shows the tail it hides", () => {
  for (const busy of [0.5, 0.8, 0.9]) {
    const sim = simulateServer(10, busy, 200_000, 7);
    const model = responseTime(10, busy);
    assert.ok(Math.abs(sim.mean - model) / model < 0.1, `${busy}: simulated ${sim.mean}, model ${model}`);
    // In this model, p99 is about ln(100) ≈ 4.6 times the mean: at 90% busy, a 10 ms job has a p99 near half a second.
    assert.ok(Math.abs(sim.p99 / sim.mean - Math.log(100)) < 0.5, `${busy}: p99 ${sim.p99}, mean ${sim.mean}`);
  }
});

test("performance problem or scalability problem? Look at it under light load", () => {
  const slowCode = responseTime(300, 0.1); // 300 ms of work, almost idle
  const busyServer = responseTime(10, 0.95); // 10 ms of work, nearly full
  assert.equal(Math.round(slowCode), 333); // slow even when idle: a performance problem; more servers won't help
  assert.equal(Math.round(busyServer), 200); // fast when idle, slow when busy: a scalability problem
  assert.equal(Math.round(responseTime(10, 0.95 / 2)), 19); // a second server halves the load: fixed
  assert.equal(Math.round(responseTime(300, 0.1 / 2)), 316); // a second server barely helps the slow code
});

test("a system handles only as many requests as its slowest stage", () => {
  const stages = [
    { name: "load balancer", perSecond: 50_000 },
    { name: "app servers", perSecond: 4 * 800 },
    { name: "database writes", perSecond: 2_000 },
  ];
  assert.deepEqual(throughput(stages), { perSecond: 2_000, bottleneck: "database writes" });
  stages[1].perSecond = 8 * 800; // four more app servers...
  assert.deepEqual(throughput(stages), { perSecond: 2_000, bottleneck: "database writes" }); // ...change nothing
});

test("why adding machines stops helping, and can make things worse", () => {
  // Amdahl: if 5% of the work can't be split, 8 machines give under 6 times the speed, and no number gives more than 20.
  assert.equal(amdahl(8, 0.05).toFixed(2), "5.93");
  assert.ok(amdahl(1_000_000, 0.05) < 20);
  // The universal scalability law, with 5% contention and 0.1% coherence cost: capacity peaks near 31 machines.
  assert.equal(Math.round(uslPeak(0.05, 0.001)), 31);
  assert.deepEqual([8, 31, 60, 100].map((n) => usl(n, 0.05, 0.001).toFixed(1)), ["5.7", "9.0", "8.0", "6.3"]);
});
```

**Lab:** the code is in [`architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/02-scalability-and-performance/labs/typescript). From the vault root, `python3 labs/run.py scalability-and-performance/typescript` runs the tests and checks this page still shows the same code. Inside the folder, `node --test` runs the tests alone. Expect seven passing tests; the simulation takes under a second.

## Common pitfalls

1. **Using the average.** It hides the tail. Report p50, p95 and p99.
2. **Adding servers to a performance problem.** If it's slow when idle, more servers won't help.
3. **Running servers near 100%.** Waiting grows without limit as utilisation nears full. Leave headroom.
4. **Scaling the wrong stage.** More app servers do nothing when the database is the bottleneck. Find the slowest stage first.
5. **Scaling out with state on the servers.** Sessions or baskets in server memory break as soon as a second server is added.
6. **Assuming more machines always help.** Contention and coherence costs set a ceiling, and past it capacity falls.
7. **Guessing the bottleneck.** You scale what the [[devops/10-observability/index|measurements]] say is the constraint, not what you assume. In the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|record-generator pipeline]], the bottleneck was the database write path, not the file reading. You have to measure to know.

## Check your understanding

1. An endpoint takes 800 ms with one user and 850 ms with a thousand. Performance or scalability problem? What would you try first?
2. Why is the average a poor summary of latency? Give an example where it misleads.
3. A server handles requests needing 20 ms of work, and 40 arrive a second. What's its utilisation, and roughly its average response time?
4. Why do teams run servers at 50–70% at peak instead of 95%?
5. A system has a load balancer for 20,000 a second, app servers for 6,000 and a database for 1,500. What's its throughput, and what happens if you double the app servers?
6. If 10% of a job can't be split, what's the most any number of machines can speed it up?

<details>
<summary>Answers — after your attempt</summary>

1. A performance problem: it's slow even with one user, and load barely changes it. Look at what each request does (a slow query, a missing index, an external call) before adding servers.
2. A few very slow requests pull the average up while most requests are much faster, so it describes no real request and hides how bad the slow ones are. In the lab's example the average is 93 ms, but the typical request takes 50 ms and 1 in 100 takes over 2 seconds.
3. 40 × 0.02 s = 0.8, so 80% busy. The average is 20 ÷ (1 − 0.8) = 100 ms, five times the work itself.
4. Waiting grows steeply near full: at 95% busy the average is 20 times the work time, and the tail far worse. A traffic spike on a server already at 95% sends latency through the roof. Headroom keeps queues short and absorbs spikes.
5. 1,500 a second, limited by the database. Doubling the app servers changes nothing; the fix has to be in the database or in how much each request writes.
6. 10 times: the speed-up can never exceed 1 ÷ 0.1, because the part that can't be split takes at least 10% of the original time.

</details>

## Practice — independent task

**Measure your own service under load, and name its problem.**

1. Pick an endpoint on your flagship, or any service you run locally.
2. With a load tool such as `autocannon` or `k6`, measure p50, p95 and p99 at three load levels: light (a few requests a second), medium, and a level where latency clearly rises. Keep the tool and the service on the same machine, and write the machine and settings down.
3. Decide: performance problem, scalability problem, both, or neither. Use the light-load latency to decide.
4. Work out the utilisation of the stage you think is the bottleneck at your highest load, and compare the formula's predicted average with what you measured.

**A smaller step first:** in the lab, change the slow share from 2% to 5%. Predict p95 and p99 before running, then check.

**Done when:** you have a table of p50, p95 and p99 at three loads with the environment written down, a diagnosis that cites the light-load number, the bottleneck named with your evidence, and one sentence on how far the formula's prediction was from your measurement and why.

## Tradeoffs, limits and extensions

- **The queueing formula is a model.** It assumes one server and random arrivals and work times. Real servers have several workers, connection pools and garbage-collection pauses. Use it to predict the shape and to sanity-check measurements, not as a capacity plan.
- **Percentiles don't average.** The p99 of two servers isn't the average of their p99s. Combine the raw measurements, or histograms, and compute the percentile from those.
- **Latency targets usually include the network.** What users see adds round trips that server-side measurements miss; [[networking/15-network-performance|network performance]] covers that part.
- **The scaling laws need measurements.** Fit $\alpha$ and $\beta$ from load tests at several machine counts before believing a predicted peak.

## Before moving on

You can tell a performance problem from a scalability problem, read a latency distribution by its percentiles, predict how utilisation drives waiting, find the bottleneck, and explain why scaling out has a ceiling.

**Recap.** Performance is speed for one request; scalability is keeping that speed as load grows. Compare latency at light and heavy load to tell them apart. Latency is a distribution: report p50, p95 and p99, never only the average. Waiting grows as work ÷ (1 − utilisation), slowly and then suddenly, so leave headroom. A system's throughput is its slowest stage's, so find that stage before scaling. Start vertical, scale out with stateless servers, and remember that work which can't be split, contention and coherence put a ceiling on adding machines. Scaling is finding the current bottleneck and relieving it, again and again, guided by measurements.

**Next.** [[architecture/02-building-blocks/02-caching|Caching]] and [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancing]] in week 2: the first two moves in the scaling toolkit, and where they put new bottlenecks.

## Related
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|How to approach system design]] — where finding bottlenecks fits in a design
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability & Reliability]] — horizontal scaling also buys fault tolerance
- [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]] — Little's law, and what to do when a dependency is the bottleneck
- [[architecture/02-building-blocks/index|Building Blocks]] — the tools in the scaling toolkit
- [[ai-ml/02-ml-engineer/index|ML Engineer]]'s data pipelines — throughput and latency in another domain
