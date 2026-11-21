import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { keywords } from "../../../12-evals/labs/typescript/baselines.ts";
import { CircuitBreaker, CircuitOpenError } from "./breaker.ts";
import { Cassette, MissingRecording } from "./cassette.ts";
import { firstThatWorks } from "./fallback.ts";
import { TokenBucket } from "./limiter.ts";
import { resilient } from "./resilient.ts";
import { backoff, CallError, isRetryable, parseRetryAfter, withRetry, withTimeout } from "./retry.ts";

/** A pretend clock: sleeping moves time forward instantly, so tests about waiting take no time. */
function fakeClock() {
  const clock = { t: 0, slept: [] as number[] };
  return {
    clock,
    now: () => clock.t,
    sleep: async (ms: number) => {
      clock.slept.push(ms);
      clock.t += ms;
    },
  };
}

/** A pretend model that fails with each status in turn, then answers. */
function flaky(statuses: number[], reply = "billing") {
  const calls: number[] = [];
  return {
    calls,
    run: async () => {
      const status = statuses[calls.length];
      calls.push(status ?? 200);
      if (status) throw new CallError(status);
      return reply;
    },
  };
}

test("only failures a second try could fix are retryable", () => {
  for (const status of [408, 429, 500, 502, 503, 529]) assert.equal(isRetryable(new CallError(status)), true, `${status}`);
  for (const status of [400, 401, 403, 404, 422]) assert.equal(isRetryable(new CallError(status)), false, `${status}`);
  assert.equal(isRetryable(new DOMException("slow", "TimeoutError")), true);
  assert.equal(isRetryable(new TypeError("fetch failed")), true); // no response at all
  assert.equal(isRetryable(new TypeError("Cannot read properties of undefined")), false); // a bug in our code
});

test("Retry-After comes as seconds or as a date", () => {
  const now = Date.parse("2026-10-02T12:00:00Z");
  assert.equal(parseRetryAfter("7", now), 7000);
  assert.equal(parseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", now), 30_000);
  assert.equal(parseRetryAfter(null, now), undefined);
  assert.equal(parseRetryAfter("soon", now), undefined);
});

test("backoff doubles its ceiling each attempt, up to a cap, and jitter picks a point below it", () => {
  const top = () => 0.999999;
  assert.deepEqual([1, 2, 3, 4, 5, 6].map((n) => backoff(n, 500, 10_000, top)), [500, 1000, 2000, 4000, 8000, 10000]);
  assert.equal(backoff(3, 500, 10_000, () => 0.5), 1000); // half of the 2000 ms ceiling
});

test("a transient failure is retried until it succeeds", async () => {
  const { sleep, now, clock } = fakeClock();
  const model = flaky([503, 429]);
  const reply = await withRetry(model.run, { sleep, now, random: () => 0.5 });
  assert.equal(reply, "billing");
  assert.deepEqual(model.calls, [503, 429, 200]);
  assert.deepEqual(clock.slept, [250, 500]);
});

test("a 400 fails at once: sending the same bad request again can't help", async () => {
  const model = flaky([400]);
  await assert.rejects(withRetry(model.run, fakeClock()), { status: 400 });
  assert.equal(model.calls.length, 1);
});

test("Retry-After beats our own guess, and the attempts run out", async () => {
  const { sleep, now, clock } = fakeClock();
  const calls: number[] = [];
  const limited = async () => {
    calls.push(1);
    throw new CallError(429, "rate limited", 7000);
  };
  await assert.rejects(withRetry(limited, { sleep, now, maxAttempts: 3 }), { status: 429 });
  assert.equal(calls.length, 3);
  assert.deepEqual(clock.slept, [7000, 7000]);
});

test("the deadline stops a retry whose wait would overrun it", async () => {
  const { sleep, now, clock } = fakeClock();
  const model = flaky([503, 503, 503, 503]);
  const retry = { sleep, now, random: () => 0.999999, maxAttempts: 10, baseMs: 1000, deadlineMs: 5000 };
  await assert.rejects(withRetry(model.run, retry), { status: 503 });
  assert.deepEqual(clock.slept, [1000, 2000]); // waiting 4000 more would end at 7000 ms, past the 5000 ms deadline
  assert.equal(model.calls.length, 3);
});

test("a timeout cancels a call that would hang forever", async () => {
  let aborted = false;
  const hangs = (signal: AbortSignal) =>
    new Promise<string>(() => signal.addEventListener("abort", () => (aborted = true)));
  await assert.rejects(withTimeout(hangs, 20), { name: "TimeoutError" });
  assert.equal(aborted, true);
  assert.equal(await withTimeout(async () => "fast", 1000), "fast");
});

test("the breaker opens after repeated failures, then lets one trial through after a cool-down", async () => {
  const { now, clock } = fakeClock();
  const breaker = new CircuitBreaker({ threshold: 3, coolDownMs: 30_000, now });
  const down = flaky([503, 503, 503, 503, 503]);
  for (let i = 0; i < 3; i++) await assert.rejects(breaker.call(down.run), { status: 503 });
  assert.equal(breaker.current(), "open");
  await assert.rejects(breaker.call(down.run), CircuitOpenError); // fails fast, without calling
  assert.equal(down.calls.length, 3);

  clock.t += 30_000;
  assert.equal(breaker.current(), "half-open");
  await assert.rejects(breaker.call(down.run), { status: 503 }); // the trial fails, so it opens again
  assert.equal(breaker.current(), "open");

  clock.t += 30_000;
  assert.equal(await breaker.call(async () => "ok"), "ok"); // the trial works, so it closes
  assert.equal(breaker.current(), "closed");
});

test("a 400 doesn't trip the breaker: it's our bug, not the provider's outage", async () => {
  const breaker = new CircuitBreaker({ threshold: 2 });
  const bad = flaky([400, 400, 400]);
  for (let i = 0; i < 3; i++) await assert.rejects(breaker.call(bad.run), { status: 400 });
  assert.equal(breaker.current(), "closed");
});

test("fallback tries each option in turn, logs every failure, and won't hide a bad request", async () => {
  const failures: string[] = [];
  const log = (name: string, error: unknown) => failures.push(`${name}: ${(error as CallError).status}`);
  const result = await firstThatWorks(
    [
      { name: "primary", run: flaky([503]).run },
      { name: "secondary", run: flaky([], "bug").run },
    ],
    log,
  );
  assert.deepEqual(result, { by: "secondary", value: "bug" });
  assert.deepEqual(failures, ["primary: 503"]);

  await assert.rejects(firstThatWorks([{ name: "primary", run: flaky([400]).run }, { name: "secondary", run: flaky([]).run }]), { status: 400 });
  await assert.rejects(firstThatWorks([{ name: "only", run: flaky([503]).run }]), AggregateError);
});

test("all the layers together: retries, then the breaker opens and the keyword rules take over", async () => {
  const { sleep, now } = fakeClock();
  const lines: string[] = [];
  const model = flaky(Array(20).fill(503));
  const classify = resilient("model", async () => model.run(), {
    timeoutMs: 1000,
    retry: { sleep, now, random: () => 0.5, maxAttempts: 3 },
    breaker: new CircuitBreaker({ threshold: 4, now }),
    fallback: keywords,
    log: (line) => lines.push(line),
  });

  assert.deepEqual(await classify("I was charged twice."), { by: "fallback", value: "billing" });
  assert.equal(model.calls.length, 3);
  assert.deepEqual(await classify("The app crashes on start."), { by: "fallback", value: "bug" });
  assert.equal(model.calls.length, 4); // the 4th failure opened the circuit, so no 5th or 6th call
  assert.deepEqual(lines, [
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
    "model: gave up (HTTP 503)",
    "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
    "model: gave up (CircuitOpenError)",
  ]);
});

test("a token bucket allows a burst, then paces to the steady rate", async () => {
  const { sleep, now, clock } = fakeClock();
  const bucket = new TokenBucket({ capacity: 3, perSecond: 1, now });
  const startedAt: number[] = [];
  for (let i = 0; i < 6; i++) {
    await bucket.take(1, sleep);
    startedAt.push(clock.t);
  }
  assert.deepEqual(startedAt, [0, 0, 0, 1000, 2000, 3000]);
  assert.throws(() => bucket.tryTake(5), RangeError);
});

test("a cassette records once, replays exactly, and misses when the request changes", async () => {
  const path = join(mkdtempSync(join(tmpdir(), "cassette-")), "replies.jsonl");
  const request = { model: "m", prompt: "Classify: help", options: { temperature: 0 } };
  let sent = 0;
  const send = async () => (sent++, "other");
  assert.equal(await new Cassette(path).record(request, send), "other");
  assert.equal(await new Cassette(path).record(request, send), "other");
  assert.equal(sent, 1); // the second run read the file instead of calling the model

  const replayed = new Cassette(path);
  assert.equal(replayed.replay(request), "other");
  assert.throws(() => replayed.replay({ ...request, prompt: "Classify:  help" }), MissingRecording); // one extra space
});

test("the CI gate exits 0 to pass, 1 to block and 2 when a recording is missing", () => {
  const run = (...args: string[]) => spawnSync(process.execPath, ["ci-gate.ts", ...args], { cwd: import.meta.dirname, encoding: "utf8" });
  const pass = run("--model", "keywords", "--floor", "0.7");
  assert.equal(pass.status, 0);
  assert.match(pass.stdout, /keywords: 15\/20 = 75% \(95% interval 53%–89%\)\ngate: pass/);
  const fail = run("--model", "keywords", "--floor", "0.8");
  assert.equal(fail.status, 1);
  assert.match(fail.stdout, /✗ pass rate 75% is below the floor of 80%/);
  const missing = run("--model", "qwen3.5:4b");
  assert.equal(missing.status, 2);
});
