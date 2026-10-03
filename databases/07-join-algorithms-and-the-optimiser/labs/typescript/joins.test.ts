import { test } from "node:test";
import assert from "node:assert/strict";
import { hashJoin, indexNestedLoop, independentEstimate, mergeJoin, nestedLoop, rowsReadForPage, type Row } from "./joins.ts";

const ORDERS: Row[] = Array.from({ length: 10_000 }, (_, i) => [1 + (i % 1_000), `order ${i}`]);
const CUSTOMERS: Row[] = Array.from({ length: 1_000 }, (_, i) => [i + 1, `customer ${i + 1}`]);
const byKey = (rows: readonly Row[]) => [...rows].sort((a, b) => a[0] - b[0]); // sort is stable: equal keys keep their order
const canonical = (rows: [string, string][]) => rows.map((r) => r.join("|")).sort();

test("all three algorithms give the same answer", () => {
  const expected = canonical(nestedLoop(ORDERS, CUSTOMERS)[0]);
  assert.equal(expected.length, 10_000);
  assert.deepEqual(canonical(indexNestedLoop(ORDERS, CUSTOMERS)[0]), expected);
  assert.deepEqual(canonical(hashJoin(ORDERS, CUSTOMERS)[0]), expected);
  assert.deepEqual(canonical(mergeJoin(byKey(ORDERS), CUSTOMERS)[0]), expected);
});

test("they differ enormously in work", () => {
  assert.deepEqual(
    [nestedLoop(ORDERS, CUSTOMERS)[1], indexNestedLoop(ORDERS, CUSTOMERS)[1], hashJoin(ORDERS, CUSTOMERS)[1], mergeJoin(byKey(ORDERS), CUSTOMERS)[1]],
    [10_000_000, 99_780, 11_000, 10_999],
  );
});

test("a small outer side makes the indexed nested loop cheapest", () => {
  const oneCustomer = ORDERS.filter(([k]) => k === 42);
  assert.deepEqual([indexNestedLoop(oneCustomer, CUSTOMERS)[1], hashJoin(oneCustomer, CUSTOMERS)[1]], [100, 1_010]);
});

test("correlated columns and pagination", () => {
  assert.deepEqual([Math.round(independentEstimate(30_000, 0.1, 0.3)), Math.round(independentEstimate(30_000, 0.1))], [900, 3_000]);
  assert.deepEqual([rowsReadForPage(100_000, 20, false), rowsReadForPage(100_000, 20, true)], [100_020, 20]);
});
