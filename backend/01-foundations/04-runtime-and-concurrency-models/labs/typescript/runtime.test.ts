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
