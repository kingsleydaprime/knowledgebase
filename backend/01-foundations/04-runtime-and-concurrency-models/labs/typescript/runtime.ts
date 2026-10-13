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
