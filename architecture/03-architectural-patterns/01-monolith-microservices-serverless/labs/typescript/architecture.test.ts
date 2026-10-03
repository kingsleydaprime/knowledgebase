import { test } from "node:test";
import assert from "node:assert/strict";
import { boundaryViolations, breakEvenRequests, coldShare, coordinationLinks, extract, findCycle, releaseBreaks, serverlessMonthly, simulateColdShare } from "./architecture.ts";

test("coordination grows with the square of the people", () => {
  assert.deepEqual([4, 8, 50].map(coordinationLinks), [6, 28, 1_225]);
});

test("a shared release breaks far more often than one team's", () => {
  // Eight teams put 40 changes a week into one monolith release; each change has a 1% chance of breaking something.
  assert.equal((releaseBreaks(40, 0.01) * 100).toFixed(1), "33.1"); // one release in three is held up
  assert.equal((releaseBreaks(5, 0.01) * 100).toFixed(1), "4.9"); // one team's own five changes
});

test("a chatty module gets slow and fragile behind the network; a coarse interface doesn't", () => {
  // Checkout asks pricing 40 times per request. In process, that's nanoseconds and can't fail on its own.
  const chatty = extract(40, 1, 0.9999);
  assert.equal(chatty.addedMs, 40);
  assert.equal((chatty.availability * 100).toFixed(2), "99.60"); // forty chances to fail
  const coarse = extract(1, 1, 0.9999); // one call that prices the whole basket
  assert.deepEqual({ ms: coarse.addedMs, pct: (coarse.availability * 100).toFixed(2) }, { ms: 1, pct: "99.99" });
});

test("pay per request until the traffic is steady, then a server is cheaper", () => {
  const price = { perMillionRequests: 0.2, perGbSecond: 0.0000166667 }; // illustrative, close to AWS Lambda's list price
  // Invoice rendering: 200 ms at 512 MB.
  assert.equal(serverlessMonthly(1_000_000, 200, 0.5, price).toFixed(2), "1.87"); // a million invoices: under $2
  assert.equal(serverlessMonthly(50_000_000, 200, 0.5, price).toFixed(2), "93.33"); // fifty million: three times a $30 server
  const breakEven = breakEvenRequests(30, 200, 0.5, price);
  assert.equal(Math.round(breakEven / 1e5) / 10, 16.1); // about 16 million a month: 6 a second, around the clock
});

test("cold starts hit quiet functions hardest", () => {
  // An instance stays warm for 5 minutes after a request.
  assert.deepEqual([10, 1, 0.1].map((perMinute) => (coldShare(perMinute, 5) * 100).toFixed(2)), ["0.00", "0.67", "60.65"]);
  for (const perMinute of [1, 0.1]) {
    const simulated = simulateColdShare(perMinute, 5, 100_000, 7);
    assert.ok(Math.abs(simulated - coldShare(perMinute, 5)) < 0.005, `${perMinute}/min: ${simulated}`);
  }
});

test("a modular monolith's boundaries: no reaching inside, no cycles", () => {
  const shop = [
    { name: "orders", imports: ["billing", "catalog/internal/prices"] }, // reaches inside catalog
    { name: "billing", imports: ["customers"] },
    { name: "catalog", imports: ["catalog/internal/prices"] }, // inside itself: fine
    { name: "customers", imports: [] },
  ];
  assert.deepEqual(boundaryViolations(shop), ["orders → catalog/internal/prices"]);
  assert.equal(findCycle(shop), undefined);
  shop[3].imports.push("orders"); // customers now needs orders: orders → billing → customers → orders
  assert.deepEqual(findCycle(shop), ["orders", "billing", "customers", "orders"]);
});
