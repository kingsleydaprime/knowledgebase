import { test } from "node:test";
import assert from "node:assert/strict";
import { burnRate, errorBudget, mean, percentile, red, shouldPage } from "./signals.mjs";

// 100 requests in one minute: 97 fast, 2 slow, 1 very slow that also failed.
const logs = [
  ...Array.from({ length: 97 }, (_, i) => ({ event: "request.finished", status: 200, durationMs: 20 + (i % 10) })),
  { event: "request.finished", status: 200, durationMs: 1800 },
  { event: "request.finished", status: 200, durationMs: 2100 },
  { event: "request.finished", status: 503, durationMs: 3000 },
  { event: "payment.charged" }, // not a finished request: ignored
].map((entry) => JSON.stringify(entry));

test("the average hides the slow tail; percentiles show it", () => {
  const signals = red(logs, 60);
  assert.equal(signals.meanMs, 93);    // "about 90ms" — looks fine
  assert.equal(signals.p50Ms, 24);     // the typical request
  assert.equal(signals.p95Ms, 29);     // 95 in 100 are this fast or faster
  assert.equal(signals.p99Ms, 2100);   // 1 in 100 users waits over two seconds
  assert.equal(signals.errorRate, 0.01);
  assert.equal(signals.ratePerSecond, 100 / 60);
});

test("percentile edge cases", () => {
  assert.equal(percentile([], 99), null);
  assert.equal(percentile([5], 99), 5);
  assert.equal(mean([1, 2, 3]), 2);
});

test("error budget: 99.9% over 10 million requests allows 10,000 failures", () => {
  assert.deepEqual(errorBudget({ slo: 0.999, totalRequests: 10_000_000, failedRequests: 2_500 }), {
    allowed: 10_000, used: 2_500, remaining: 7_500, spentFraction: 0.25,
  });
});

test("burn rate, and paging only on a fast burn that is still happening", () => {
  assert.equal(Math.round(burnRate(0.001, 0.999)), 1);   // exactly on budget
  assert.equal(Math.round(burnRate(0.02, 0.999)), 20);   // 2% errors: budget gone in 1.5 days
  assert.equal(shouldPage({ errorRateLastHour: 0.02, errorRateLast5Min: 0.03, slo: 0.999 }), true);
  assert.equal(shouldPage({ errorRateLastHour: 0.02, errorRateLast5Min: 0.0, slo: 0.999 }), false); // already recovered
  assert.equal(shouldPage({ errorRateLastHour: 0.005, errorRateLast5Min: 0.5, slo: 0.999 }), false); // a brief blip
});
