import { test } from "node:test";
import assert from "node:assert/strict";
import { HashRing, Health, leastOutstanding, modulo, pickHealthy, random, roundRobin, simulate, smoothWeighted, twoChoices } from "./balancer.ts";

test("round-robin takes turns; least-outstanding looks at the queues", () => {
  const pick = roundRobin();
  const queues = [5, 0, 0]; // server 0 is stuck on slow requests
  assert.deepEqual([1, 2, 3, 4, 5, 6].map(() => pick(queues, Math.random)), [0, 1, 2, 0, 1, 2]); // still gets its turn
  assert.equal(leastOutstanding(queues, Math.random), 1);
});

test("smooth weighted round-robin gives a bigger server more turns, spread out", () => {
  const pick = smoothWeighted({ a: 5, b: 1, c: 1 });
  assert.equal(Array.from({ length: 7 }, pick).join(""), "aabacaa"); // 5 of 7 to a, but never five in a row
});

test("when some requests are slow, the algorithms that look at the queues win, most of all in the tail", () => {
  // 4 servers, 80% busy, 100,000 requests: 95% take 10 ms and 5% take 200 ms. Latency in ms.
  const run = (pick: Parameters<typeof simulate>[0]) => simulate(pick, 4, 0.8, 100_000, 7);
  assert.deepEqual(run(roundRobin()), { mean: 214, p50: 138, p99: 1_158 }); // a fast request waits behind a slow one
  assert.deepEqual(run(random), { mean: 255, p50: 159, p99: 1_588 });
  assert.deepEqual(run(leastOutstanding), { mean: 68, p50: 17, p99: 466 }); // sees every queue
  assert.deepEqual(run(twoChoices), { mean: 96, p50: 25, p99: 495 }); // sees only two queues, and gets most of the gain
});

test("a server needs three failed checks to go down and two good ones to come back", () => {
  const health = new Health(3, 2);
  for (const ok of [false, false, true, false, false]) health.record(ok); // a success resets the count
  assert.equal(health.up, true);
  health.record(false);
  assert.equal(health.up, false); // three failures in a row
  health.record(true);
  assert.equal(health.up, false); // one success isn't enough
  health.record(true);
  assert.equal(health.up, true);
});

test("the balancer skips servers that are down, and has nothing to offer when all are", () => {
  const servers = ["app-1", "app-2", "app-3"].map((name) => ({ name, health: new Health(3, 2) }));
  for (let i = 0; i < 3; i++) servers[1].health.record(false);
  assert.deepEqual([0, 1, 2, 3].map((turn) => pickHealthy(servers, turn)), ["app-1", "app-3", "app-1", "app-3"]);
  for (const s of servers) for (let i = 0; i < 3; i++) s.health.record(false);
  assert.throws(() => pickHealthy(servers, 0), /no healthy servers/);
});

test("adding a fifth server: modulo hashing moves 4 keys in 5, a hash ring moves about 1 in 5", () => {
  const keys = Array.from({ length: 10_000 }, (_, i) => `user:${i}`);
  const four = ["cache-a", "cache-b", "cache-c", "cache-d"];
  const five = [...four, "cache-e"];
  const movedByModulo = keys.filter((k) => modulo(k, four) !== modulo(k, five)).length;
  assert.ok(Math.abs(movedByModulo - 8_000) < 200, `modulo moved ${movedByModulo}`);

  const ring = new HashRing(four, 100);
  const before = keys.map((k) => ring.serverFor(k));
  ring.add("cache-e");
  const after = keys.map((k) => ring.serverFor(k));
  const moved = keys.filter((_, i) => before[i] !== after[i]);
  assert.ok(Math.abs(moved.length - 2_000) < 300, `ring moved ${moved.length}`);
  assert.ok(moved.every((k) => ring.serverFor(k) === "cache-e")); // every key that moved went to the new server

  ring.remove("cache-e"); // and taking it out puts them back where they were
  assert.deepEqual(keys.map((k) => ring.serverFor(k)), before);
});

test("virtual nodes even out how many keys each server gets", () => {
  const keys = Array.from({ length: 10_000 }, (_, i) => `user:${i}`);
  const busiest = (replicas: number) => {
    const ring = new HashRing(["cache-a", "cache-b", "cache-c", "cache-d"], replicas);
    const counts = new Map<string, number>();
    for (const k of keys) counts.set(ring.serverFor(k), (counts.get(ring.serverFor(k)) ?? 0) + 1);
    return Math.max(...counts.values()) / (keys.length / 4); // 1.0 would be perfectly even
  };
  assert.ok(busiest(1) > 1.4, `one point each: busiest ${busiest(1)}`);
  assert.ok(busiest(100) < 1.2, `100 points each: busiest ${busiest(100)}`);
});
