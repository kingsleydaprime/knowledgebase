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
