# Runtime and Concurrency Models

**[Intermediate]** — Why backend frameworks differ at all. Once you know which concurrency model a framework sits on, most of its API design, its performance under load and its failure modes follow. There are three models: a thread per request, an event loop, and green threads. This lesson explains all three, then measures the one you'll run most, Node's event loop: one request's CPU work stalling ten others, how to detect that, the hidden four-thread pool, and the limits that actually cap your concurrency. The lab runs on your machine with no setup.

## Before you start

You can already:

- Explain the difference between a process and a thread → [[os/02-processes-and-threads|processes and threads]].
- Use `async`/`await` and `Promise.all` in TypeScript.
- Use Little's law: requests in progress = arrival rate × time each takes → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]].

After this lesson you will be able to:

1. Name the three concurrency models, the runtimes that use each, and what happens in each when a request blocks.
2. Size a thread pool with Little's law, and explain why a slow dependency kills a thread-per-request server while its CPU sits idle.
3. Say what blocks Node's event loop, recognise the symptom, and find it with event-loop delay.
4. Find the concurrency limits that are actually in charge: libuv's thread pool, an unbounded fan-out, and the database connection pool.

**Study route:** sections 2 and 3 are the model. Sections 4 to 7 are Node, measured; stop at each prediction. Section 9 is how all this shapes frameworks. Section 11 is the lab. This week's "by Sunday" question is closed-book, *what blocks the Node event loop, and how would you find out it's blocked?*, so read sections 4 and 5 twice, then close the page and answer it.

## The kid version first

A restaurant, many tables, and the question of how many waiters.

- **Thread per request:** one waiter per table. Simple: each waiter follows their table from start to finish. But waiters are expensive, and most of the time they're standing still, waiting for the kitchen.
- **Event loop:** one waiter, always moving. Take an order, hand it to the kitchen, go straight to the next table, come back when the food is ready. Wonderfully efficient, **until one customer asks the waiter to sit down and do their taxes**, and every other table waits.
- **Green threads:** it *looks* like one waiter per table, so it's easy to organise, but the restaurant secretly has a few real waiters and swaps them between tables whenever one would be standing idle.

**Where the analogy stops working.** A waiter doing someone's taxes is obviously busy, and you'd notice. A blocked event loop isn't obvious from outside: the machine's overall CPU can look low (one core pinned out of eight), the average response time barely moves, and the only sign is that the slowest 1% of requests got much slower. And "waiting for the kitchen" is too gentle for the thread model's real failure: when the kitchen slows down, every waiter ends up standing at the hatch, and new customers aren't seated at all.

## 1. Why this exists

Two services fail on the same day, in opposite ways. The Node API's average latency is fine, its CPU looks low, and yet its 99th-percentile latency (p99) jumps from 20 ms to 400 ms several times an hour. Someone added a report endpoint that builds a large JSON response synchronously. The Java service, running on a 200-thread server, stops answering completely when the database slows down, with its CPU at 3%. Neither service has a bug in its business logic. Each is its concurrency model doing exactly what it does. This lesson is about knowing what that is.

## Terms used in this lesson

1. **Concurrency**: This is dealing with many tasks in overlapping time periods, switching between them; they need not run at the same instant.
2. **Parallelism**: This is running tasks at literally the same instant, on different CPU cores.
3. **OS thread**: This is a thread the operating system schedules onto CPU cores. Each has its own stack, reserved up front, and switching between threads costs a trip through the kernel.
4. **Blocking call**: This is a call that doesn't return until its work is done, such as reading a file synchronously, so the thread that made it can do nothing else meanwhile.
5. **Event loop**: This is a single thread that repeatedly takes the next ready callback from its queues and runs it to completion, asking the operating system which sockets are ready in between.
6. **Readiness API**: This is the operating system call an event loop uses to wait for many sockets at once and learn which are ready, such as `epoll` on Linux and `kqueue` on macOS.
7. **Microtask**: In JavaScript, this is a callback queued by a resolved promise, including the code after an `await`. The loop runs every queued microtask before it moves on to timers or I/O.
8. **libuv**: This is the C library under Node that runs the event loop and also a small pool of threads for work the operating system can't do asynchronously.
9. **Worker thread**: In Node, this is a second JavaScript thread with its own event loop, used for CPU-heavy work. It shares no variables with the main thread and communicates by messages.
10. **Green thread**: This is a lightweight thread managed by a language runtime rather than the operating system. The runtime runs many of them on a few OS threads (M:N scheduling) and parks one whenever it waits for I/O. Goroutines and Java's virtual threads are green threads.
11. **Function colouring**: This is the split, in `async`/`await` languages, between async functions and ordinary ones: an async function can only be awaited from another async function, so the whole call chain must be async.
12. **Pinning**: This is a green thread that can't be parked while it waits, so it holds on to its OS thread and stops other green threads from using it.
13. **Event-loop delay**: This is how late a timer fires compared with when it was due. It's the direct measure of how long the loop was busy and couldn't run anything else.

## 2. The three models

| | **Thread per request** | **Event loop** | **Green threads** |
|---|---|---|---|
| Unit of concurrency | an OS thread | a callback or promise continuation on one thread | a runtime-managed task, M:N onto OS threads |
| Cost per waiting request | a stack (often 1 MB reserved) and a kernel-scheduled thread | a closure: bytes | a small growable stack: a few KB |
| A request blocks | fine: the OS runs another thread | **every request on the loop waits** | fine: the runtime parks it |
| Code style | sequential | callbacks, promises, `async`/`await` | sequential |
| CPU-heavy work | fine, up to the core count | must leave the loop | fine, up to the core count |
| Examples | Java servlets before Loom, Rails (Puma), Django on WSGI, PHP-FPM | **Node.js**, nginx, Redis, Python's asyncio | Go, Java 21+ virtual threads, Erlang/Elixir; Rust's tokio and C#'s tasks are close cousins (below) |

**Thread per request.** Each request gets an OS thread, and blocking is free from the programmer's point of view: `db.query()` just waits, and the operating system runs another thread. The cost is per *waiting* request, not per unit of work. 10,000 connections need 10,000 threads. Most of their 1 MB stacks is reserved address space rather than memory actually used, but the threads are real: thousands of kernel-scheduled threads mean scheduler overhead, context switches and memory for the parts of each stack that are touched. That ceiling is the **C10K problem**, handling ten thousand connections on one machine. → [[networking/09-sockets-and-the-network-api|sockets]]

**Event loop.** One thread and a readiness API. Idle connections cost almost nothing, so one core handles tens of thousands of them. The defining constraint: **any synchronous work blocks everything**. It doesn't make one request slow; it makes every request that arrives during it slow. Everything distinctive about Node follows from that: async-by-default APIs, `worker_threads` for CPU work, one process per core, and the rule "never block the event loop".

**Green threads.** The runtime runs many lightweight tasks on a few OS threads, parking a task when it waits for I/O and resuming it when the data arrives. **You write blocking-style code and get event-loop efficiency.** Goroutines have always worked this way; Java 21's virtual threads brought it to the JVM. The realisation behind it: the *programming model* (sequential, readable, debuggable) and the *execution model* (multiplexed onto a few threads) never had to match. Once a runtime can separate them, thread-per-request comes back, at a million threads.

**The `async`/`await` cousins.** Rust's tokio, C#'s `Task`s and Python's asyncio get the same efficiency with explicit `await` points rather than invisible parking. Tokio and .NET run tasks on a pool of threads across all cores. asyncio, like Node, runs on one thread. The price of `await` is **function colouring**: an async function can only be awaited from async code, so libraries split in two (sync and async clients for the same database). Go and Java's virtual threads avoid it, because to the programmer, everything is ordinary blocking code.

## 3. Thread per request, and Little's law

How many threads does a thread-per-request server need? Little's law answers it directly: **requests in progress = arrival rate × time each one takes**. Each request in progress holds a thread.

| Traffic | Time each request takes | Threads busy | Pool of 200 |
|---|---|---|---|
| 150 requests/s | 100 ms (normal) | 15 | fine |
| 150 requests/s | 2 s (the database slows down) | **300** | **exhausted** |
| 150 requests/s | capped at 500 ms by a timeout | 75 | fine; the slow calls fail fast |

The second row is the Java service from section 1. Nothing about the *work* changed: the CPU has even less to do, since every thread is parked waiting. But 300 threads are needed and 200 exist, so new requests queue for a thread, the queue grows by 100 requests every second, and the service is effectively dead with its CPU at 3%.

**Prediction.** The team's first idea is to raise the pool to 400 threads. Does that fix it?

<details>
<summary>Answer</summary>

Only until the database gets a little slower, and it makes the database's problem worse. 400 threads means up to 400 concurrent queries against a database that's already struggling, which slows it further, which needs more threads. **The fix is timeouts and bulkheads, not a bigger pool.** A 500 ms timeout caps the time each request can hold a thread, so the pool needs 75. A bulkhead (a separate, small pool for calls to that one dependency) stops the slow dependency from taking every thread, so the rest of the service keeps working. → [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]]

</details>

## 4. The event loop, measured

Node's loop goes round in phases: timers that are due, then I/O callbacks for sockets the operating system says are ready, then `setImmediate` callbacks, and round again. After each callback, it runs every queued microtask (promise continuations) before taking the next one. Only one callback runs at a time, to completion.

So when a request handler runs 300 ms of synchronous code, nothing else happens for 300 ms: no other request is read, no response is written, no timer fires. The lab puts this to a test. A server has a `/fast` route and a `/work` route that does 300 ms of CPU work on the loop. The test starts one `/work`, then 20 ms later sends ten `/fast` requests:

| Where the 300 ms of work runs | Fastest of the ten `/fast` requests | Slowest |
|---|---|---|
| on the event loop | about **300 ms** | about 305 ms |
| in a worker thread | about **8 ms** | about 15 ms |

Ten requests with no work to do took 300 ms each, because they arrived while the loop was busy. The server runs in a child process in the test: in the test's own process, blocking the server would have blocked the test's client too, so the client would have sent its requests late and measured nothing. (The first version of the lab made exactly that mistake and reported 15 ms.)

**Prediction.** The server handles 1,000 requests a minute. One request in a hundred is the slow report. What happens to p50 and p99 latency?

<details>
<summary>Answer</summary>

p50 barely moves: most requests arrive while the loop is free. p99 jumps by up to the full block, because the unlucky 1% arrive during one of the blocks and wait behind it. That's the signature of a blocked event loop: **a p99 spike with a flat p50**, and the machine's overall CPU looks modest, because one core out of eight at 100% is 12.5%. → [[backend/interview/01-production-debugging|p99 debugging]]

</details>

**What blocks the event loop.** Anything synchronous and slow, on the request path:

- CPU work in JavaScript: big loops, sorting or filtering large arrays, building reports.
- `JSON.parse` and `JSON.stringify` of large payloads: tens of megabytes take hundreds of milliseconds.
- The `Sync` APIs: `fs.readFileSync`, `crypto.pbkdf2Sync`, `zlib.gzipSync`. A `Sync` call in a library you use on a server is a warning sign.
- A regular expression with catastrophic backtracking on hostile input (ReDoS), which can run for seconds on a 30-character string.
- Synchronous native addons, such as an image library without an async API.

**The fixes.** Move CPU work to a **worker thread** (the lab's second row), or out of the process into a job queue. Break long loops into chunks and yield between them with `setImmediate`. Stream large JSON instead of parsing it whole. Use the async versions of every API.

## 5. How to find out the loop is blocked

You can't see a blocked loop in the code that blocks it; you see it from the outside, in timing. Ask for a timer every 10 ms and measure how late each one fires. A free loop fires it on time, give or take a millisecond. A loop blocked for 250 ms fires it 250 ms late. That lateness is **event-loop delay**:

```ts
export function lagProbe(intervalMs = 10) {
  let expected = performance.now() + intervalMs;
  let worst = 0;
  const timer = setInterval(() => {
    const now = performance.now();
    worst = Math.max(worst, now - expected);
    expected = now + intervalMs;
  }, intervalMs);
  // ... and perf_hooks.monitorEventLoopDelay(), the built-in version, measured alongside
}
```

In the lab, the worst lag with nothing running is a few milliseconds; with `busyWait(250)` in the middle it's over 200 ms, and `monitorEventLoopDelay` agrees. In production:

1. **Export event-loop delay as a metric** (p99 and max of `monitorEventLoopDelay`, which most Node metrics libraries already offer) and alert on it. A blocked loop shows up there before customers notice.
2. **Correlate** delay spikes with the requests in flight at the time: the access log of slow requests by route usually names the culprit.
3. **Profile** to find the exact function: `node --cpu-prof` writes a profile to open in Chrome DevTools, and a flame graph shows the wide, flat bar where the loop spent its time.

## 6. The hidden thread pool

Node isn't quite single-threaded. Some work can't be done asynchronously by the operating system, so libuv runs it on a **pool of 4 threads**: file system calls, `dns.lookup` (which is what `http.get("example.com")` uses), `crypto.pbkdf2`, `crypto.scrypt`, `crypto.randomBytes` and `zlib`. The loop hands the work over and stays free, but only 4 jobs run at a time, and the rest queue.

The lab starts four `pbkdf2` hashes at once, about 75 ms each, in a child process with `UV_THREADPOOL_SIZE=1` and then with the default:

| Thread pool | When each of the four hashes finished (one run) |
|---|---|
| 1 thread | 75, 151, 236, 345 ms: a queue |
| 4 threads (default) | 72, 74, 74, 124 ms: roughly together |

The trap: a login endpoint that hashes passwords with `pbkdf2`, under load, fills all 4 threads, and now every `fs.readFile` and every outgoing HTTP request's DNS lookup waits behind password hashes. The event loop looks idle and the delay metric is fine, but everything that touches the pool is slow. You can raise the pool with `UV_THREADPOOL_SIZE` (set before the pool is first used; the maximum is 1024), but more threads than cores doesn't make CPU-bound work faster. On this 4-core laptop, over four runs, eight hashes took 210 to 250 ms with 4 threads and 185 to 215 ms with 8: a little faster, nowhere near twice.

## 7. Microtasks can starve everything else

The loop runs **every** queued microtask before it takes the next timer or I/O callback, and a microtask can queue another. So a long chain of `await`s on already-resolved promises never gives the loop back:

```ts
for (let i = 0; i < steps; i++) {
  done++;
  await null; // resumes as a microtask: no timer, no I/O, until the loop ends
}
```

**Prediction.** A 0 ms timer is set, then this loop runs a million steps. How many steps have run when the timer fires? And if the loop yields with `await new Promise((r) => setImmediate(r))` every 1,000 steps?

<details>
<summary>Answer</summary>

All 1,000,000: the timer can't fire until the microtask queue is empty, which is when the loop has finished. With a `setImmediate` yield every 1,000 steps, the loop goes back round its phases each time, and the timer fires after a few thousand steps (the lab checks under 100,000). So `await` alone doesn't make a loop "async" in the sense that matters: it doesn't let other requests in.

</details>

## 8. The limits that are actually in charge

Event loop, threads or green threads, your real concurrency limit is usually somewhere else.

**An unbounded fan-out.** `Promise.all(items.map(callDownstream))` on 1,000 items sends 1,000 concurrent requests to the downstream service; the lab's fake downstream counts **1,000** in flight at once. That's how one batch job takes down a dependency. A limit fixes it: `mapLimit(items, 10, fn)` runs a fixed set of 10 workers pulling from a queue, so the downstream sees **10**. It takes longer (100 calls at 20 ms, 10 at a time: 200 ms), and that's the point.

**The connection pool.** A database pool of 10 caps you at 10 concurrent queries, however many requests, threads or tasks you have. The lab sends 100 requests through a pool of 10, each holding a connection for a 20 ms query:

- The database never sees more than **10** queries at once.
- The first ten requests get a connection immediately; the last waits about **180 ms** (nine rounds of 20 ms).
- The average wait for a connection is about **90 ms**, more than four times the query itself.

**Prediction.** That service's dashboards show query time (20 ms) and total request time. Where does the other 90 ms appear?

<details>
<summary>Answer</summary>

Nowhere, unless you measure it. It isn't query time, because the query hasn't started, and it's part of the total but labelled as nothing. That's why the lab's `Pool` records `waitsMs`: **time waiting for a connection is a top cause of mysterious latency**, and most pools can report it (HikariCP's `connectionTimeout` and pending-threads metrics, `pg-pool`'s `waitingCount`). The fix is rarely just a bigger pool, because the database has its own limit on connections. Look for slow queries, transactions held open across network calls, and too many service replicas each holding a full pool.

</details>

## 9. Why this determines framework design

Read a framework's API and you can usually infer its model:

- **Everything returns a promise or future, nothing is synchronous**: an event loop or an async runtime. Express, NestJS, Fastify, FastAPI's `async def` routes, axum.
- **Handlers look synchronous, and blocking is fine**: thread per request or green threads. Spring MVC, Django, Rails, Go's `net/http`.
- **There's a separate "reactive" variant**: the framework was built for thread per request and added an event-loop option later. Spring MVC and Spring WebFlux are the example, and virtual threads remove most of the reason to choose WebFlux, which is a live debate worth knowing.

It also determines **how you scale**. An event-loop process uses one core for JavaScript, so you run one process per core (`cluster`, or more replicas). Thread-per-request and green-thread runtimes use every core in one process, so you scale up before you scale out.

And **how you tune**. Thread per request: the pool size, set by Little's law, plus timeouts. Event loop: the dial is "what's blocking?", plus the number of processes. Green threads: usually nothing, which is the point, apart from the connection pool, which is everyone's dial.

### The things that bite, per model

- **Thread per request:** pool exhaustion under a slow dependency: every thread parked, the service dead, the CPU idle. Fix it with timeouts and bulkheads.
- **Event loop:** synchronous work on the hot path; an unbounded `Promise.all`; libuv's 4 threads full while the loop looks idle; long chains of microtasks.
- **Green threads:** spawning without limit, because tasks are cheap; pinning (a Java virtual thread inside `synchronized` was pinned to its OS thread until JDK 24); blocking calls the runtime can't see, such as a native driver, which hold an OS thread.

## 10. Key insight

A backend framework is mostly **a set of ergonomic choices made on top of one concurrency model**, and the model is the part that decides behaviour under load. Learn the three models and frameworks stop being twenty things to memorise: they become three ideas and twenty vocabularies. The model also tells you the first question to ask about any new codebase: *"what happens here if something blocks?"* The answer is different in Nest and in Spring, and that difference is the whole reason both exist.

## 11. The lab: Node's concurrency, measured

`runtime.ts` has Little's law, a server that does its slow work on the loop or in a worker, the lag probe, `pbkdf2` completion times, the microtask-starvation loop, `mapLimit`, and a connection pool that records waits. The timing tests use generous margins (a blocked request must take over 200 ms; a free one under 100 ms), so they pass on a busy laptop.

```ts
// runtime.ts — Node's concurrency model, measured: one blocked event loop stalling every request, how to see it
// (event-loop delay), moving the work to a worker thread, libuv's four-thread pool, microtasks starving timers, and
// the limits that actually cap concurrency: a bounded fan-out and a connection pool. Plus Little's law, which says
// how many threads a thread-per-request server needs.
import http from "node:http";
import { pbkdf2 } from "node:crypto";
import { monitorEventLoopDelay } from "node:perf_hooks";
import { Worker } from "node:worker_threads";

/** Little's law: the average number of requests in progress = arrival rate × time each one takes. */
export function inProgress(arrivalsPerSecond: number, secondsEach: number): number {
  return arrivalsPerSecond * secondsEach;
}

/** Synchronous CPU work: the loop can do nothing else until it returns. */
export function busyWait(ms: number): void {
  const end = performance.now() + ms;
  while (performance.now() < end);
}

const WORKER_SOURCE = `
const { parentPort } = require("node:worker_threads");
parentPort.on("message", (ms) => {
  const end = performance.now() + ms;
  while (performance.now() < end);
  parentPort.postMessage("done");
});`;

/**
 * A server with a fast route and a slow, CPU-bound one. `inline` does the slow work on the event loop; `worker` sends
 * it to a worker thread and awaits the reply, so the loop stays free.
 */
export async function startServer(mode: "inline" | "worker", workMs = 300) {
  const worker = mode === "worker" ? new Worker(WORKER_SOURCE, { eval: true }) : undefined;
  const offLoop = (ms: number) => new Promise<void>((resolve) => {
    worker!.once("message", () => resolve());
    worker!.postMessage(ms);
  });
  const server = http.createServer(async (req, res) => {
    if (req.url === "/work") {
      if (worker) await offLoop(workMs);
      else busyWait(workMs);
      res.end("worked");
    } else {
      res.end("fast");
    }
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address() as { port: number };
  return {
    port,
    close: async () => {
      server.closeAllConnections();
      await new Promise((resolve) => server.close(resolve));
      await worker?.terminate();
    },
  };
}

function get(port: number, path: string): Promise<string> {
  return new Promise((resolve, reject) => {
    http.get({ port, path, host: "127.0.0.1", agent: false }, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => resolve(body));
    }).on("error", reject);
  });
}

/** Starts one /work request, then 10 /fast ones 20 ms later; returns how long each fast one took, in ms. Run it
 * against a server in another process (see the end of this file). */
export async function fastLatenciesDuringWork(port: number): Promise<number[]> {
  const work = get(port, "/work");
  await new Promise((resolve) => setTimeout(resolve, 20));
  const fast = Array.from({ length: 10 }, async () => {
    const start = performance.now();
    await get(port, "/fast");
    return performance.now() - start;
  });
  const latencies = await Promise.all(fast);
  await work;
  return latencies;
}

/**
 * How you find out the loop is blocked: ask for a timer every `intervalMs` and measure how late it fires. A free loop
 * fires it on time; a blocked one fires it late by however long it was blocked. This is what
 * perf_hooks.monitorEventLoopDelay measures too.
 */
export function lagProbe(intervalMs = 10) {
  let expected = performance.now() + intervalMs;
  let worst = 0;
  const timer = setInterval(() => {
    const now = performance.now();
    worst = Math.max(worst, now - expected);
    expected = now + intervalMs;
  }, intervalMs);
  const histogram = monitorEventLoopDelay({ resolution: intervalMs });
  histogram.enable();
  return {
    stop: () => {
      clearInterval(timer);
      histogram.disable();
      return { worstLagMs: worst, monitorMaxMs: histogram.max / 1e6 };
    },
  };
}

/**
 * Starts `tasks` pbkdf2 hashes at once and returns when each finished, in ms from the start. pbkdf2 runs on libuv's
 * thread pool, which has 4 threads unless UV_THREADPOOL_SIZE says otherwise, set before the pool is first used.
 */
export async function hashCompletionTimes(tasks: number, iterations = 100_000): Promise<number[]> {
  const start = performance.now();
  const done = Array.from({ length: tasks }, (_, i) => new Promise<number>((resolve, reject) => {
    pbkdf2(`password ${i}`, "salt", iterations, 32, "sha256", (err) => (err ? reject(err) : resolve(performance.now() - start)));
  }));
  return (await Promise.all(done)).sort((a, b) => a - b);
}

/**
 * Runs `steps` steps of work, each followed by an await, with a 0 ms timer set before the first. Returns how many steps
 * had run when the timer fired. `await null` resumes as a microtask, and the loop runs every queued microtask before
 * any timer, so the timer waits for all of them; yielding with setImmediate every `yieldEvery` steps lets it in.
 */
export async function stepsBeforeTimer(steps: number, yieldEvery?: number): Promise<number> {
  let done = 0;
  let firedAt = -1;
  const fired = new Promise<void>((resolve) => setTimeout(() => {
    firedAt = done;
    resolve();
  }, 0));
  for (let i = 0; i < steps; i++) {
    done++;
    if (yieldEvery && done % yieldEvery === 0) await new Promise((resolve) => setImmediate(resolve));
    else await null;
  }
  await fired;
  return firedAt;
}

/** A downstream service that counts how many calls it has in progress at once. */
export function fakeDownstream(ms: number) {
  const state = { inFlight: 0, maxInFlight: 0 };
  return {
    state,
    call: async () => {
      state.inFlight++;
      state.maxInFlight = Math.max(state.maxInFlight, state.inFlight);
      await new Promise((resolve) => setTimeout(resolve, ms));
      state.inFlight--;
    },
  };
}

/** Like Promise.all(items.map(fn)), but with at most `limit` calls in progress: a fixed set of workers pulling from a queue. */
export async function mapLimit<T, R>(items: T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const i = next++; // safe without a lock: nothing else runs between reading and incrementing on one thread
      results[i] = await fn(items[i]);
    }
  });
  await Promise.all(workers);
  return results;
}

/** A connection pool: `size` connections, first come first served, recording how long each caller waited for one. */
export class Pool {
  waitsMs: number[] = [];
  #free: number;
  #queue: (() => void)[] = [];

  constructor(size: number) {
    this.#free = size;
  }

  async use<R>(fn: () => Promise<R>): Promise<R> {
    const asked = performance.now();
    if (this.#free > 0) this.#free--;
    else await new Promise<void>((resolve) => this.#queue.push(resolve)); // a connection is handed over directly on release
    this.waitsMs.push(performance.now() - asked);
    try {
      return await fn();
    } finally {
      const nextInLine = this.#queue.shift();
      if (nextInLine) nextInLine();
      else this.#free++;
    }
  }
}

// The tests run these in a child process: a server in the test's own process would block the test's client too, so
// the stall would never show in the client's timings. `node runtime.ts serve inline` prints the port and keeps
// serving; `node runtime.ts hashes 4` prints completion times, run with whatever UV_THREADPOOL_SIZE the test sets.
if (process.argv[2] === "serve") {
  const { port } = await startServer(process.argv[3] as "inline" | "worker");
  console.log(port);
} else if (process.argv[2] === "hashes") {
  console.log(JSON.stringify(await hashCompletionTimes(Number(process.argv[3]))));
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawn } from "node:child_process";
import { once } from "node:events";
import { busyWait, fakeDownstream, fastLatenciesDuringWork, inProgress, lagProbe, mapLimit, Pool, stepsBeforeTimer } from "./runtime.ts";

const RUNTIME = new URL("./runtime.ts", import.meta.url).pathname;

/** Starts the server in its own process, so blocking it can't block this one. */
async function serverProcess(mode: "inline" | "worker") {
  const child = spawn(process.execPath, [RUNTIME, "serve", mode], { stdio: ["ignore", "pipe", "inherit"] });
  const [line] = await once(child.stdout!, "data");
  return { port: Number(String(line).trim()), stop: () => child.kill() };
}

test("Little's law: how many threads a thread-per-request server needs", () => {
  assert.equal(inProgress(150, 0.1), 15); // 150 requests/s at 100 ms: 15 threads busy, a pool of 200 is plenty
  assert.equal(inProgress(150, 2), 300); // the database slows to 2 s: 300 needed, 200 exist, the pool is exhausted
  assert.equal(inProgress(150, 0.5), 75); // a 500 ms timeout caps it: failing fast keeps the server alive
});

test("one blocked event loop stalls every request: 300 ms of CPU work on the loop delays ten unrelated fast requests", async () => {
  const server = await serverProcess("inline");
  try {
    const latencies = await fastLatenciesDuringWork(server.port);
    assert.ok(Math.min(...latencies) > 200, `fastest was ${Math.min(...latencies)} ms`); // all of them waited for the work
  } finally {
    server.stop();
  }
});

test("the same work in a worker thread: the loop stays free and the fast requests stay fast", async () => {
  const server = await serverProcess("worker");
  try {
    const latencies = await fastLatenciesDuringWork(server.port);
    assert.ok(Math.max(...latencies) < 100, `slowest was ${Math.max(...latencies)} ms`);
  } finally {
    server.stop();
  }
});

test("finding out the loop is blocked: timers fire late by as long as it was blocked", async () => {
  const quiet = lagProbe();
  await new Promise((resolve) => setTimeout(resolve, 200));
  const free = quiet.stop();
  assert.ok(free.worstLagMs < 50, `worst lag ${free.worstLagMs} ms with nothing running`);

  const probe = lagProbe();
  await new Promise((resolve) => setTimeout(resolve, 30));
  busyWait(250);
  await new Promise((resolve) => setTimeout(resolve, 30));
  const blocked = probe.stop();
  assert.ok(blocked.worstLagMs > 200, `worst lag ${blocked.worstLagMs} ms`); // the hand-made probe sees it
  assert.ok(blocked.monitorMaxMs > 200, `monitorEventLoopDelay max ${blocked.monitorMaxMs} ms`); // and so does the built-in
});

test("libuv's thread pool: with one thread, four hashes queue up one after another", () => {
  const run = (env: Record<string, string>) => JSON.parse(execFileSync(process.execPath, [RUNTIME, "hashes", "4"], { env: { ...process.env, ...env }, encoding: "utf8" })) as number[];
  const oneThread = run({ UV_THREADPOOL_SIZE: "1" });
  const fourThreads = run({}); // the default is 4
  const spread = (times: number[]) => times[times.length - 1] / times[0]; // last finish ÷ first finish
  assert.ok(spread(oneThread) >= 2.5, `one thread: ${oneThread.map(Math.round)}`); // a queue: about 1×, 2×, 3×, 4×
  assert.ok(spread(oneThread) > spread(fourThreads), `four threads: ${fourThreads.map(Math.round)}`); // together, roughly
});

test("microtasks run before timers: a long chain of awaits starves a 0 ms timer until it ends", async () => {
  assert.equal(await stepsBeforeTimer(1_000_000), 1_000_000); // the timer fired only after every step
  assert.ok((await stepsBeforeTimer(1_000_000, 1_000)) < 100_000); // yielding with setImmediate lets it in early
});

test("an unbounded Promise.all sends everything at once; a limit is a limit", async () => {
  const flooded = fakeDownstream(20);
  await Promise.all(Array.from({ length: 1000 }, () => flooded.call()));
  assert.equal(flooded.state.maxInFlight, 1000); // a thousand concurrent calls to one downstream

  const limited = fakeDownstream(20);
  const start = performance.now();
  await mapLimit(Array.from({ length: 100 }), 10, () => limited.call());
  assert.equal(limited.state.maxInFlight, 10);
  assert.ok(performance.now() - start >= 190); // 100 calls, 10 at a time, 20 ms each: 10 rounds
});

test("the connection pool is the real limit, and the waiting for it is invisible unless you measure it", async () => {
  const pool = new Pool(10);
  const db = fakeDownstream(20);
  await Promise.all(Array.from({ length: 100 }, () => pool.use(() => db.call()))); // 100 'concurrent' requests
  assert.equal(db.state.maxInFlight, 10);
  const waits = pool.waitsMs;
  const average = waits.reduce((a, b) => a + b) / waits.length;
  assert.equal(waits.filter((w) => w < 1).length, 10); // the first ten got a connection at once
  assert.ok(Math.max(...waits) >= 170, `longest wait ${Math.max(...waits)} ms`); // the last waited nine rounds of 20 ms
  assert.ok(average >= 80, `average wait ${average} ms`); // 0 to 180 ms in steps: about 90 ms, for a 20 ms query
});
```

**Run it:** `python3 labs/run.py runtime-and-concurrency-models/typescript`, or `node --test` in the lab folder. Running `node runtime.ts hashes 8` with different `UV_THREADPOOL_SIZE` values shows section 6's numbers on your machine.

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/01-foundations/04-runtime-and-concurrency-models/labs/typescript).

## Common pitfalls

1. **Synchronous work in a Node request handler.** Large `JSON.parse`, `Sync` APIs, big loops. Move it to a worker thread or a job queue.
2. **Watching average latency and overall CPU only.** A blocked loop hides from both. Watch p99 and event-loop delay.
3. **Raising the thread pool when a dependency is slow.** It adds load to the thing that's struggling. Add timeouts and bulkheads.
4. **`Promise.all` over an unbounded list.** It's a load test against your own dependency. Use a concurrency limit.
5. **Assuming `await` yields.** Awaiting resolved promises runs as microtasks and never lets timers or I/O in.
6. **Forgetting libuv's 4 threads.** Heavy `pbkdf2`, `zlib` or file I/O delays every `dns.lookup` behind it.
7. **Not measuring connection-pool waits.** The wait is often bigger than the query and appears on no dashboard.

## Check your understanding

1. Why does a thread-per-request server die when its database slows down, even though its CPU is nearly idle?
2. One Node endpoint does 200 ms of synchronous work. Why does it make *other* endpoints slow, and what's the latency signature?
3. How does event-loop delay detect a blocked loop, and why can't the blocking code detect it itself?
4. Your Node service's file reads are slow, yet event-loop delay is near zero and CPU is moderate. What do you suspect?
5. What's function colouring, and how do Go and Java's virtual threads avoid it?
6. Why is the connection pool often the real concurrency limit, whatever the model?

<details>
<summary>Answers — after your attempt</summary>

1. Each request holds a thread for its whole duration, including the time it waits on the database. By Little's law, when the database takes 20 times longer, 20 times as many threads are busy. The pool runs out, new requests queue for a thread, and nothing is served, while the threads that exist are all parked doing nothing.
2. The work runs on the only thread that serves requests, so for 200 ms no other request can be read or answered. Requests arriving during that time wait for it. The signature is a p99 spike with a flat p50, and overall CPU that looks modest because only one core is busy.
3. It measures how late a regularly scheduled timer fires. A timer can only fire when the loop is free, so its lateness is how long the loop was busy. The blocking code can't detect it because, while it runs, nothing else runs, including any code that would measure it.
4. libuv's thread pool is full, probably with CPU-heavy pool work such as `pbkdf2`, `scrypt` or `zlib`. File reads queue behind it on the pool's 4 threads, while the loop itself is free.
5. In `async`/`await` languages, an async function can only be awaited from async code, so every caller up the chain must become async too, and libraries split into sync and async versions. Go and virtual threads make ordinary blocking calls park the green thread instead, so there's only one kind of function.
6. Every request that touches the database needs a connection, and the pool has a fixed number. However many threads, tasks or callbacks you have, only that many queries run at once, and the rest wait, invisibly unless the pool's waits are measured.

</details>

## Practice — independent task

**Find and fix a blocked event loop, the way you would in production.**

1. Start from the lab's `startServer`, and add a `/report` route that builds a 50,000-item array of objects, sorts it, and returns it with `JSON.stringify`, all synchronously.
2. Add a `/metrics` route that reports the p50, p99 and max of `monitorEventLoopDelay` since the last call.
3. Write a load script (in another process) that sends 50 `/fast` requests per second for 10 seconds, plus one `/report` per second. Record the p50 and p99 of the `/fast` latencies, and the event-loop delay.
4. Fix it twice: first by moving the report into a worker thread, then by building it in chunks that yield with `setImmediate`. Measure both.

**Done when:** you have a table of `/fast` p50, `/fast` p99 and event-loop delay p99 for the three versions; the p99 drops by at least 5 times from the original to the worker version; and you can say in two sentences which fix you'd choose for a report that took 5 seconds, and why.

## Before moving on

You can name the three models with examples, size a pool with Little's law and say why timeouts beat a bigger pool, explain what blocks Node's loop and how event-loop delay reveals it, and find the hidden limits: libuv's 4 threads, an unbounded `Promise.all` and the connection pool.

**Recap.** There are three concurrency models. A thread per request is simple, and a slow dependency exhausts it while its CPU idles, because each waiting request holds a thread (Little's law). An event loop serves huge numbers of idle connections on one thread, and any synchronous work stalls every request on it: the signature is a p99 spike with a flat p50, the detector is event-loop delay, and the fixes are worker threads, chunking and async APIs. Green threads let you write blocking code that runs like an event loop. Node also hides a 4-thread pool for file, DNS and crypto work. Whatever the model, the real limit is often a concurrency cap you didn't choose consciously: a fan-out without a limit, or a connection pool whose waits nobody measures.

## Related

- [[backend/01-foundations/03-the-request-lifecycle/index|The request lifecycle]]: the stages each request passes, which this lesson runs
- [[backend/frameworks/index|Frameworks]]: each framework's model, named
- [[os/08-io-models|I/O models]] and [[networking/09-sockets-and-the-network-api|sockets]]: `select`, `epoll` and `io_uring` from the operating system's side
- [[os/06-concurrency-primitives|Locks, races and deadlock]]: what goes wrong when threads share memory
- [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual threads (Java)]] · [[languages/02-go/06-goroutines-and-channels|goroutines]] · [[languages/03-rust/14-async-and-tokio|tokio]] · [[languages/06-python/17-asyncio-in-depth|asyncio]]
- [[backend/interview/02-node-runtime-and-api|Node runtime interview]] · [[backend/interview/01-production-debugging|p99 debugging]]
