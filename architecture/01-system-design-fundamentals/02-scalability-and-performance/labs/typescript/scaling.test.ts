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
