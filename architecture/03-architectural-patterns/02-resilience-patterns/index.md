# Resilience patterns

> **[Intermediate]** · Covers the patterns that keep one failing dependency from taking a whole service down: timeouts, retries, circuit breakers, bulkheads, load shedding, back-pressure and graceful degradation, and the arithmetic that says when you need them. The worked example simulates a service with two endpoints and one slow dependency, minute by minute, and shows a cascade happen, a timeout fail to stop it, and bulkheads contain it, with the same numbers on every run. It also contains a real concurrency bug from writing the bulkhead, and the test that caught it.

## Before you start

You can already:

- Write a retry with backoff and jitter, a timeout and a circuit breaker → [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]] (that lesson builds them in detail, for model calls; this one applies them to any dependency and adds the rest).
- Explain why a remote call can be slow or fail → [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|what makes distributed systems hard]].
- Use `async`/`await` and promises.

After this lesson you will be able to:

1. Explain how a slow dependency becomes an outage for unrelated features, and use Little's law to predict when it will.
2. Choose between timeouts, retries, circuit breakers, bulkheads and load shedding for a given failure, and say what each can't do.
3. Build a bulkhead that hands a freed place to the caller who was waiting, and test that it never exceeds its limit.

**Study route.** Read §1–3, stop at the prediction in §3, then §4–5 and the lab.

## The kid version

A ship is divided into watertight rooms. If the hull cracks, only one room floods, and the ship stays afloat. Without the walls, one crack sinks everything. A service is like a ship whose rooms are its workers: if one slow thing it depends on is allowed to use every worker, a crack in that one thing floods the whole service, even the parts that never touch it. So you put up walls (bulkheads), close the door on a room that's flooding (a circuit breaker), stop waiting for anyone forever (timeouts), and turn people away politely at the door when it's full, instead of letting them stand in the corridor until they give up (load shedding).

**Where the analogy stops working.** A flooded room stays flooded. A slow dependency usually recovers, and the patterns have to let traffic back in when it does, carefully, without flooding it again.

## 1. Why this exists

A service has two endpoints. `/search` calls a search engine; `/profile` reads from its own database. They share one pool of 50 workers. One afternoon the search engine slows from 200 ms to 5 seconds per request. Nothing has *failed*; it's just slow. Within seconds, every worker is waiting on a search, `/profile` requests queue behind them, callers give up, and the profile page, which never touches the search engine, is down. This is a **cascading failure**, and it's how most outages spread. The patterns here keep a partial failure partial.

## Terms used in this lesson

1. **Dependency**: This is anything a service calls to do its work: a database, another service, an external API.
2. **Cascading failure**: This is a failure that spreads from one component to others that depend on it, or that share resources with it, until much more is down than the original fault.
3. **Worker pool**: This is the fixed number of threads, connections or request slots a service can use at once. Every request in progress holds one.
4. **Little's law**: This states that the average number of requests in a system equals the rate at which they arrive multiplied by the average time each one stays.
5. **Timeout**: This is a limit on how long a call may take before it's abandoned.
6. **Circuit breaker**: This is a guard that stops calling a dependency after repeated failures and fails fast instead, then lets a trial call through after a cool-down to test whether it has recovered.
7. **Bulkhead**: This is a separate, limited share of resources for one dependency or one kind of work, so that it can't use up what the rest of the service needs.
8. **Load shedding**: This means turning requests away immediately when the service is full, rather than letting them queue until they time out.
9. **Back-pressure**: This means a busy component signalling to whatever feeds it to slow down, instead of accepting work it can't finish.
10. **Graceful degradation**: This means giving a reduced result, such as cached data or a placeholder, when a non-essential dependency fails, instead of an error.

## 2. Why a slow dependency is worse than a dead one

A dead dependency fails fast: the connection is refused, the request errors in milliseconds, and the worker is free again. A **slow** dependency holds the worker for as long as it takes. **Little's law** says how many workers that means: the number of requests in progress equals the arrival rate times how long each one holds a worker.

$$\text{workers busy} = \text{arrival rate} \times \text{time per request}$$

Healthy, the service sees 20 searches a second at 0.2 s and 30 profile views a second at 0.1 s: 4 + 3 = **7** workers busy on average, out of 50. When search slows to 5 seconds, searches alone need 20 × 5 = **100** workers. There are 50. The queue grows without limit, and every request in it, profile or search, waits until its caller gives up.

That's the whole mechanism: the pool is shared, so the slow dependency's demand is taken from everyone.

## 3. The patterns, and what each can't do

**Timeouts.** Never wait without a limit: a timeout releases the worker when the dependency is too slow. Many libraries default to *no* timeout, which is how one slow database takes down a fleet. But a timeout only shortens how long each request holds a worker. If rate × timeout is still more than the pool, the pool still fills.

**Retries** with exponential backoff and jitter recover from transient failures, but only for idempotent operations, only for failures a retry can fix, and with a cap ([[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency]]). Against a slow dependency, retries make the arithmetic worse: each retry is another request holding a worker.

**Circuit breakers** stop calling a dependency that keeps failing, so requests fail in microseconds and the dependency gets room to recover. They act on *failures*, so they help most once timeouts are turning slowness into failures.

**Bulkheads** give each dependency its own limited share of workers. Search can use 20, profile 30, and neither can take the other's. Search's trouble stays search's trouble.

**Load shedding.** A bulkhead with a short queue turns extra requests away immediately. A caller who gets a fast "busy, try later" can retry, fall back or tell the user; a caller kept waiting 30 seconds for a failure helps nobody, and holds resources while waiting.

**Graceful degradation.** When a non-essential dependency fails, return something reduced: a cached result, a default, "recommendations aren't available right now". The page works with less.

The timeout, retry, circuit-breaker and fallback code, with tests, is in [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]]; this lesson's lab adds the bulkhead and the simulation.

**Predict before reading on.** The search engine slows to 5 s. You add a 3-second timeout on search's call to it, and keep the shared pool of 50. Does `/profile` recover?

No. With a 3-second timeout, each search holds a worker for 3 seconds, and 20 × 3 = **60** workers are needed: still more than 50. The simulation agrees: profile succeeds 270 times out of 1,800. A 1-second timeout would fit (20 × 1 = 20 workers), and profile recovers completely, but you can't always set a timeout that short, and a slightly busier minute would push it over again. Bulkheads don't depend on the arithmetic working out.

## 4. Back-pressure and queues

Queues absorb bursts, but a queue in front of a service that's slower than its arrivals only grows, and every request in it gets older. Two rules follow. **Bound every queue**, and decide what happens when it's full: reject, as load shedding does, or slow the producer down. And when one component feeds another through a message queue, let the consumer's pace set the producer's ([[architecture/02-building-blocks/04-messaging-and-async|messaging and async]]): that's back-pressure. A queue that's allowed to grow forever hides a failure until it becomes a much bigger one.

## Worked example — a cascade, a timeout and bulkheads

The simulation runs one minute of traffic in 100 ms ticks: 20 searches and 30 profile views a second, callers who give up after waiting 2 seconds, and a search engine that takes 5 seconds. Each tick, finished work frees its worker, callers who waited too long give up, new requests arrive (or are turned away if their queue is full), and free workers take the oldest requests. Being a simulation, it gives the same numbers on every run; it simplifies by assuming a caller who has started being served waits for the answer.

```ts
// simulate.ts — a service with two endpoints and one slow dependency, simulated tick by tick, so the
// cascade is visible and the numbers are the same on every run. One tick is 100 ms.

export type Kind = "search" | "profile";
export type Outcome = "ok" | "failed" | "timedOut" | "rejected" | "unfinished";

export type Config = {
  pools: Record<Kind, string>; // which worker pool each endpoint uses; the same name means a shared pool
  sizes: Record<string, number>; // workers per pool
  queueLimit: number; // waiting requests per pool before new ones are turned away (Infinity: never)
  dependencyTimeoutTicks: number; // how long search waits for the slow dependency (Infinity: forever)
};

export type Load = {
  ticks: number;
  arrivalsPerTick: Record<Kind, number>;
  serviceTicks: Record<Kind, number>; // how long each request needs a worker, if nothing times out
  clientTimeoutTicks: number; // how long a caller waits in the queue before giving up
};

type Request = { kind: Kind; arrived: number; endsAt?: number; outcome?: Outcome };

export function simulate(config: Config, load: Load): Record<Kind, Record<Outcome, number>> {
  const counts = { search: blank(), profile: blank() };
  const queues = new Map<string, Request[]>();
  const running = new Map<string, Request[]>();
  for (const pool of Object.keys(config.sizes)) (queues.set(pool, []), running.set(pool, []));

  for (let t = 0; t < load.ticks; t++) {
    for (const [pool, list] of running) { // 1. finished work frees its worker
      running.set(pool, list.filter((r) => (r.endsAt! <= t ? (counts[r.kind][r.outcome!]++, false) : true)));
    }
    for (const [pool, queue] of queues) { // 2. callers who waited too long give up
      queues.set(pool, queue.filter((r) => (t - r.arrived >= load.clientTimeoutTicks ? (counts[r.kind].timedOut++, false) : true)));
    }
    for (const kind of ["search", "profile"] as const) { // 3. new requests arrive, or are turned away
      const queue = queues.get(config.pools[kind])!;
      for (let i = 0; i < load.arrivalsPerTick[kind]; i++) {
        if (queue.length >= config.queueLimit) counts[kind].rejected++; // load shedding: a fast "no" beats a slow one
        else queue.push({ kind, arrived: t });
      }
    }
    for (const [pool, queue] of queues) { // 4. free workers take requests, oldest first
      const busy = running.get(pool)!;
      while (busy.length < config.sizes[pool] && queue.length) {
        const r = queue.shift()!;
        const needs = load.serviceTicks[r.kind];
        const limit = r.kind === "search" ? config.dependencyTimeoutTicks : Infinity;
        r.endsAt = t + Math.min(needs, limit); // a timeout frees the worker early, but the request fails
        r.outcome = needs > limit ? "failed" : "ok";
        busy.push(r);
      }
    }
  }
  for (const list of [...queues.values(), ...running.values()]) for (const r of list) counts[r.kind].unfinished++;
  return counts;
}

const blank = (): Record<Outcome, number> => ({ ok: 0, failed: 0, timedOut: 0, rejected: 0, unfinished: 0 });

/** Little's law: the average number of requests in a system is their arrival rate times how long each
 *  stays. If that's more than the workers you have, the queue grows until something gives. */
export const workersNeeded = (perSecond: number, seconds: number) => perSecond * seconds;
```

The results, out of 1,800 profile requests and 1,200 searches:

| Setup | Profile succeeded | Search |
|---|---|---|
| healthy, shared pool of 50 | **1,797** | 1,196 succeeded |
| search engine slow, shared pool, no timeout | **72** | 550 succeeded, slowly; 560 gave up waiting |
| … with a 3 s timeout | **270** | all that ran failed at 3 s |
| … with a 1 s timeout | **1,797** | 1,180 failed fast |
| bulkheads: 20 for search, 30 for profile, queues of 10, 3 s timeout | **1,797** | 380 failed, 190 gave up, **600 turned away at once** |

(The few short of 1,800 and 1,200 are requests still in progress when the minute ended.)

The second row is the cascade: profile never calls the search engine and still lost 96% of its requests. The bulkheads row is the containment: profile is unaffected, even with the 3-second timeout that failed in the shared pool, and the 600 searches turned away got their answer immediately instead of after a long wait.

### The bulkhead, and a bug worth knowing

A bulkhead for real asynchronous code: at most `maxConcurrent` calls at once, at most `maxQueue` waiting, an immediate `BulkheadFull` beyond that.

```ts
// bulkhead.ts — a limit on how much of the service one dependency may use: at most `maxConcurrent` calls
// at once, at most `maxQueue` waiting, and an immediate rejection beyond that.

export class BulkheadFull extends Error {
  override name = "BulkheadFull";
}

export class Bulkhead {
  private active = 0;
  private readonly waiting: (() => void)[] = [];
  private readonly maxConcurrent: number;
  private readonly maxQueue: number;

  constructor(maxConcurrent: number, maxQueue: number) {
    this.maxConcurrent = maxConcurrent;
    this.maxQueue = maxQueue;
  }

  get stats() {
    return { active: this.active, waiting: this.waiting.length };
  }

  async run<T>(fn: () => Promise<T>): Promise<T> {
    if (this.active < this.maxConcurrent) {
      this.active++;
    } else if (this.waiting.length < this.maxQueue) {
      await new Promise<void>((resolve) => this.waiting.push(resolve)); // woken holding a place already counted
    } else {
      // A fast "no" now is better than a slow failure later, for the caller and for everyone else.
      throw new BulkheadFull(`${this.active} running and ${this.waiting.length} waiting`);
    }
    try {
      return await fn();
    } finally {
      // Hand the place straight to the oldest waiting call, without freeing it first. Freeing it and then
      // waking the waiter would let a call arriving in between take it: two running in a bulkhead of one.
      const next = this.waiting.shift();
      if (next) next();
      else this.active--;
    }
  }
}
```

The first version of `run` was the obvious one: when a call finished, it decremented `active` and woke the oldest waiting call, which then incremented `active` again. All six tests passed. But reviewing it turned up a gap: between the decrement and the waiter actually resuming, which happens on a later turn of the event loop, another request's callback can run, see a free place, and take it. Then the waiter runs too, and two calls are running in a bulkhead of one. It only shows up when other work is already queued at that exact moment, which in a busy server is all the time.

The fix is to **hand the place over instead of freeing it**: if anyone is waiting, the finishing call wakes them without decrementing, and the waiter starts holding a place that was never released. The last test reproduces the race, a second request arriving at the very moment a place frees up, and failed (two running at once) before the fix:

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { Bulkhead, BulkheadFull } from "./bulkhead.ts";
import { type Config, type Load, simulate, workersNeeded } from "./simulate.ts";

// 60 seconds of traffic: 20 searches and 30 profile views a second. Callers give up after waiting 2 s.
const healthy: Load = { ticks: 600, arrivalsPerTick: { search: 2, profile: 3 }, serviceTicks: { search: 2, profile: 1 }, clientTimeoutTicks: 20 };
const degraded: Load = { ...healthy, serviceTicks: { search: 50, profile: 1 } }; // search's dependency now takes 5 s
const shared = { pools: { search: "shared", profile: "shared" }, sizes: { shared: 50 } } as const;

test("Little's law: workers needed = arrival rate × time each request holds a worker", () => {
  assert.equal(workersNeeded(20, 0.2) + workersNeeded(30, 0.1), 7); // healthy: 7 of 50 workers busy on average
  assert.equal(workersNeeded(20, 5), 100); // the dependency slows to 5 s: search alone needs 100 of the 50
  assert.equal(workersNeeded(20, 3), 60); // a 3 s timeout still needs 60: more than the pool
  assert.equal(workersNeeded(20, 1), 20); // a 1 s timeout fits
});

test("healthy: everything succeeds (a few are still running when the minute ends)", () => {
  const r = simulate({ ...shared, queueLimit: Infinity, dependencyTimeoutTicks: Infinity }, healthy);
  assert.deepEqual([r.search.ok, r.profile.ok, r.profile.timedOut], [1196, 1797, 0]);
});

test("the cascade: a slow dependency of search takes profile down too, through the shared pool", () => {
  const r = simulate({ ...shared, queueLimit: Infinity, dependencyTimeoutTicks: Infinity }, degraded);
  assert.equal(r.profile.ok, 72); // of 1,800: profile never touches the slow dependency, but can't get a worker
  assert.equal(r.profile.timedOut, 1668);
});

test("a timeout alone isn't enough when rate × timeout is bigger than the pool", () => {
  const threeSeconds = simulate({ ...shared, queueLimit: Infinity, dependencyTimeoutTicks: 30 }, degraded);
  assert.equal(threeSeconds.profile.ok, 270); // still mostly down: search needs 60 workers for 3 s each
  const oneSecond = simulate({ ...shared, queueLimit: Infinity, dependencyTimeoutTicks: 10 }, degraded);
  assert.equal(oneSecond.profile.ok, 1797); // 20 workers: fits, so profile recovers
  assert.equal(oneSecond.search.failed, 1180); // and every search fails fast, which is honest
});

test("bulkheads: search gets its own 20 workers, so its trouble stays its own", () => {
  const bulkheads: Config = { pools: { search: "search", profile: "profile" }, sizes: { search: 20, profile: 30 }, queueLimit: 10, dependencyTimeoutTicks: 30 };
  const r = simulate(bulkheads, degraded);
  assert.equal(r.profile.ok, 1797); // untouched, even with the 3 s timeout that failed above
  assert.deepEqual([r.search.failed, r.search.timedOut, r.search.rejected], [380, 190, 600]); // 600 turned away at once
});

test("the bulkhead class: a limit, a short queue, and an immediate no", async () => {
  const bulkhead = new Bulkhead(2, 1);
  const releases: (() => void)[] = [];
  const work = () => new Promise<string>((resolve) => releases.push(() => resolve("done")));
  const a = bulkhead.run(work);
  const b = bulkhead.run(work);
  const c = bulkhead.run(work); // waits: two are running
  await Promise.resolve();
  assert.deepEqual(bulkhead.stats, { active: 2, waiting: 1 });
  await assert.rejects(bulkhead.run(work), BulkheadFull); // the queue is full: rejected without waiting
  releases.shift()!(); // a finishes, and c takes its place
  assert.equal(await a, "done");
  await new Promise((r) => setImmediate(r));
  assert.deepEqual(bulkhead.stats, { active: 2, waiting: 0 });
  releases.forEach((release) => release());
  assert.deepEqual(await Promise.all([b, c]), ["done", "done"]);
  assert.deepEqual(bulkhead.stats, { active: 0, waiting: 0 });
});

test("a freed place goes to the caller who was waiting, not to one who arrives at the same moment", async () => {
  const bulkhead = new Bulkhead(1, 1);
  let running = 0, most = 0;
  const releases: (() => void)[] = [];
  const work = () => new Promise<void>((resolve) => {
    most = Math.max(most, ++running);
    releases.push(() => (running--, resolve()));
  });
  const first = bulkhead.run(work);
  const waiter = bulkhead.run(work); // queued behind first
  await Promise.resolve();
  // In a busy server, other requests' callbacks are already queued when a place frees up. Here, one is
  // queued right behind first's ending, and it calls run() before the waiter has had a chance to start.
  let latecomer: Promise<void> | undefined;
  let openGate!: () => void;
  new Promise<void>((r) => (openGate = r)).then(() => (latecomer = bulkhead.run(work).catch(() => {})));
  releases.shift()!(); // first finishes...
  openGate(); // ...and, in the same moment, someone else asks for the place
  await first;
  await new Promise((r) => setImmediate(r));
  assert.equal(most, 1); // never two at once in a bulkhead of one
  while (releases.length) {
    releases.shift()!();
    await new Promise((r) => setImmediate(r));
  }
  await Promise.all([waiter, latecomer]);
  assert.deepEqual(bulkhead.stats, { active: 0, waiting: 0 });
});
```

**Lab:** the code is in [`architecture/03-architectural-patterns/02-resilience-patterns/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/02-resilience-patterns/labs/typescript). From the vault root, `python3 labs/run.py resilience-patterns/typescript` runs the simulation and the tests, and checks this page still shows the same code.

## Common pitfalls

1. **No timeout.** The default in many libraries. One slow dependency then holds every worker.
2. **Trusting a timeout alone.** If arrival rate × timeout is more than your pool, the pool still fills.
3. **One shared pool for everything.** The slowest dependency takes from all the others.
4. **Unbounded queues.** They hide an overload until every request in them is too old to be useful.
5. **Retrying into a slow dependency.** Each retry is another request holding a worker.
6. **Freeing a place before handing it on.** The obvious bulkhead lets latecomers barge in. Hand places to waiters directly, and test it under contention.
7. **Patterns without numbers.** Size pools, timeouts and queues with Little's law, then check with a load test.

## Check your understanding

1. Why is a dependency that takes 5 seconds often worse for your service than one that's completely down?
2. With 40 requests a second, each holding a worker for 0.5 seconds, how many workers are busy on average?
3. Why did the 3-second timeout fail to save `/profile` in the simulation, when the 1-second one worked?
4. What does a bulkhead with a queue of 10 do with the 11th waiting request, and why is that better for the caller?
5. Describe the race in the first version of the bulkhead, and how the fix closes it.
6. When would you choose back-pressure instead of load shedding?

<details>
<summary>Answers — after your attempt</summary>

1. A dead dependency fails fast, so workers are freed in milliseconds. A slow one holds each worker for the full 5 seconds, so far fewer requests can be served at once, and the pool fills.
2. 40 × 0.5 = 20 workers, by Little's law.
3. With 3 seconds per search, 20 searches a second need 60 workers, more than the 50 in the pool, so it still filled. With 1 second, they need 20, which fits.
4. It rejects it immediately with `BulkheadFull`. The caller learns at once that the service is busy and can fall back, retry later or tell the user, instead of waiting until it gives up, while holding resources.
5. The finishing call freed its place and woke the waiter, but the waiter only resumed on a later turn of the event loop. A request arriving in between saw a free place and took it, so both ran. The fix hands the place straight to the waiter without ever freeing it, so there's no gap for anyone to slip into.
6. When the work comes from a component you control and can slow down, such as a producer feeding a message queue. Load shedding suits requests from outside, such as users, where you can't slow the sender and a fast refusal is the kindest answer.

</details>

## Practice — independent task

**Size the bulkheads for your own service.**

1. Pick a service you've built (your flagship works) and list its dependencies, with each one's normal and worst-case latency.
2. For each, use Little's law with your expected peak rate to work out how many workers it needs normally and when it's slow.
3. Change the lab's simulation to your numbers: find the smallest timeout that keeps your most important endpoint healthy in a shared pool, then the bulkhead sizes that keep it healthy without depending on that timeout.

**Done when:** you have a table of workers needed per dependency, normal and slow, and simulation results showing your most important endpoint staying above 99% success while one dependency is slow.

## Before moving on

You can explain how a slow dependency cascades, predict it with Little's law, choose the right pattern for a failure, and build a bulkhead that's correct under contention.

**Recap.** Dependencies fail, and slow ones are worse than dead ones, because they hold workers. Little's law (workers busy = arrival rate × time held) says when a pool fills. Timeouts shorten the hold but don't help if rate × timeout is still too much; circuit breakers stop calling what keeps failing; bulkheads give each dependency its own limited share; load shedding turns extra work away fast; back-pressure slows the producer; graceful degradation returns less instead of nothing. Bound every queue, and hand freed places to waiters directly.

**Next.** [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices patterns]], where every service call is a dependency that needs these.

## Related
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|Reliability and plumbing]] — timeouts, retries, breakers and fallbacks, built and tested
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud design patterns]] — the same patterns from the operations side
- [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices patterns]] — where they're needed most
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability and reliability]] — what these patterns protect
- [[architecture/02-building-blocks/04-messaging-and-async|Messaging and async]] — queues and back-pressure

*Source: the roadmap.sh system-design roadmap.*
