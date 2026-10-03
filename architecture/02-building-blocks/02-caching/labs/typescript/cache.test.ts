import { test } from "node:test";
import assert from "node:assert/strict";
import { averageReadMs, CacheAside, hitRatio, jittered, LruCache, storeReadsPerSecond, zipf } from "./cache.ts";
import { seeded } from "../../../../01-system-design-fundamentals/02-scalability-and-performance/labs/typescript/scaling.ts";

test("a full LRU cache evicts the entry used longest ago", () => {
  const cache = new LruCache<string>(3, () => 0);
  cache.set("a", "A", 1_000);
  cache.set("b", "B", 1_000);
  cache.set("c", "C", 1_000);
  cache.get("a"); // reading a makes it the most recently used
  cache.set("d", "D", 1_000); // full: b is evicted, not a
  assert.deepEqual(cache.keys(), ["c", "a", "d"]);
  assert.equal(cache.get("b"), undefined);
});

test("an entry is served until its TTL runs out, then it's a miss", () => {
  let now = 0;
  const cache = new LruCache<number>(10, () => now);
  cache.set("price:42", 10, 60_000);
  now = 59_999;
  assert.equal(cache.get("price:42"), 10);
  now = 60_000;
  assert.equal(cache.get("price:42"), undefined);
});

test("cache-aside: the first read misses and loads, the rest hit", async () => {
  const db = new Map([["product:7", "kettle"]]);
  let loads = 0;
  const products = new CacheAside(new LruCache<string>(100, () => 0), async (key) => {
    loads++;
    return db.get(key)!;
  }, { ttlMs: 60_000 });
  for (let i = 0; i < 5; i++) assert.equal(await products.get("product:7"), "kettle");
  assert.deepEqual({ loads, hits: products.hits, misses: products.misses }, { loads: 1, hits: 4, misses: 1 });
  assert.equal(hitRatio(products.hits, products.misses), 0.8);
});

test("the hit ratio decides how much the database still sees", () => {
  // 5,000 reads a second; the cache answers in 1 ms, the database in 20 ms.
  assert.deepEqual([0.8, 0.9, 0.99].map((h) => Math.round(storeReadsPerSecond(5_000, h))), [1_000, 500, 50]);
  assert.deepEqual([0, 0.8, 0.99].map((h) => averageReadMs(h, 1, 20).toFixed(1)), ["21.0", "5.0", "1.2"]);
  // If the cache goes down, the hit ratio is 0: the database gets all 5,000 a second at once.
  assert.equal(storeReadsPerSecond(5_000, 0), 5_000);
});

test("with skewed traffic, a small cache answers most reads, and each doubling adds less", () => {
  // 200,000 reads over 50,000 products, Zipf-distributed. The first 50,000 reads warm the cache and aren't counted.
  const ratios = [500, 2_500, 5_000, 10_000].map((size) => {
    const next = zipf(50_000, 1, seeded(1));
    const cache = new LruCache<boolean>(size, () => 0);
    let hits = 0;
    let misses = 0;
    for (let i = 0; i < 200_000; i++) {
      const key = String(next());
      const hit = cache.get(key) !== undefined;
      if (!hit) cache.set(key, true, Infinity);
      if (i >= 50_000) hit ? hits++ : misses++;
    }
    return hitRatio(hits, misses).toFixed(2);
  });
  // 1% of the catalogue answers nearly half the reads; 20% of it answers four in five.
  assert.deepEqual(ratios, ["0.48", "0.65", "0.72", "0.80"]);
});

test("a stampede: a hot key expires and every waiting request hits the database, unless they share one load", async () => {
  for (const coalesce of [false, true]) {
    let now = 0;
    let loads = 0;
    const products = new CacheAside(new LruCache<string>(100, () => now), async () => {
      loads++;
      await new Promise((resolve) => setTimeout(resolve, 5)); // the database takes a while
      return "kettle";
    }, { ttlMs: 60_000, coalesce });
    await products.get("product:7");
    now = 60_000; // the entry expires...
    loads = 0;
    const all = await Promise.all(Array.from({ length: 100 }, () => products.get("product:7"))); // ...as 100 reads arrive
    assert.ok(all.every((name) => name === "kettle"));
    assert.equal(loads, coalesce ? 1 : 100);
  }
});

test("delete-on-write can still leave a stale value, until the TTL runs out", async () => {
  let now = 0;
  const db = new Map([["price:42", 10]]);
  let release!: () => void;
  const slowRead = new Promise<void>((resolve) => (release = resolve));
  let first = true;
  const prices = new CacheAside(new LruCache<number>(100, () => now), async (key) => {
    const value = db.get(key)!; // the read happens now...
    if (first) {
      first = false;
      await slowRead; // ...but the answer is delayed
    }
    return value;
  }, { ttlMs: 60_000 });

  const reader = prices.get("price:42"); // 1. a reader misses and reads 10 from the database
  await prices.write("price:42", 12, async (key, value) => void db.set(key, value)); // 2. a writer saves 12 and deletes the cached copy (there isn't one yet)
  release();
  assert.equal(await reader, 10); // 3. the reader finishes and caches the old 10
  assert.equal(await prices.get("price:42"), 10); // stale: the database says 12
  now = 60_000;
  assert.equal(await prices.get("price:42"), 12); // the TTL is what puts a bound on the damage
});

test("jitter spreads out expiry, so keys cached together don't all miss together", () => {
  const random = seeded(3);
  const expiries = Array.from({ length: 1_000 }, () => jittered(60_000, 0.1, random));
  assert.ok(Math.min(...expiries) >= 54_000 && Math.max(...expiries) <= 66_000);
  const perSecond = new Map<number, number>();
  for (const ms of expiries) perSecond.set(Math.floor(ms / 1_000), (perSecond.get(Math.floor(ms / 1_000)) ?? 0) + 1);
  // Without jitter, all 1,000 would miss in the same second. With ±10%, they spread over 12 seconds.
  assert.ok(Math.max(...perSecond.values()) < 120, `busiest second: ${Math.max(...perSecond.values())}`);
});
