import { test } from "node:test";
import assert from "node:assert/strict";
import { createApp } from "./app.mjs";

// Start a fresh app per test, with a controllable clock, a captured log and a fake card processor.
async function start({ charge } = {}) {
  let now = Date.parse("2026-10-05T09:00:00Z");
  const lines = [];
  const charges = [];
  let n = 0;
  const server = createApp({
    clock: { now: () => now },
    write: (line) => lines.push(line),
    charge: charge ?? (async (p) => { charges.push(p); return `ch_${charges.length}`; }),
    newId: () => `req_${++n}`,
  }).listen(0);
  await new Promise((r) => server.once("listening", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const pay = (body, { key = "key-1", user = "u1" } = {}) =>
    fetch(`${base}/payments`, {
      method: "POST",
      headers: { "content-type": "application/json", "idempotency-key": key, "x-user-id": user },
      body: typeof body === "string" ? body : JSON.stringify(body),
    });
  return { pay, lines, charges, advance: (ms) => { now += ms; }, close: () => server.close() };
}

const valid = { amountKobo: 500_000, currency: "NGN", cardToken: "tok_visa_4242" };

test("validation: every problem reported at once, in the error contract", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await app.pay({ amountKobo: -5, currency: "naira" });
  assert.equal(res.status, 400);
  assert.deepEqual(await res.json(), {
    error: {
      code: "validation_failed",
      message: "the request body is invalid",
      details: [
        { field: "amountKobo", problem: "must be a positive whole number" },
        { field: "currency", problem: "must be a 3-letter code, like NGN" },
        { field: "cardToken", problem: "must be a card token" },
      ],
      requestId: "req_1",
    },
  });
});

test("an unexpected error: full detail in the log, nothing internal in the response", async (t) => {
  const app = await start({ charge: async () => { throw new Error("ECONNRESET talking to processor at 10.0.4.17"); } });
  t.after(app.close);
  const res = await app.pay(valid);
  assert.equal(res.status, 500);
  assert.deepEqual(await res.json(), { error: { code: "internal_error", message: "something went wrong", requestId: "req_1" } });
  const logged = JSON.parse(app.lines.at(-1));
  assert.equal(logged.requestId, "req_1");               // the same ID the client got: support can find it
  assert.match(logged.message, /10\.0\.4\.17/);          // the detail is kept — internally
});

test("logs are JSON lines, and card tokens never reach them", async (t) => {
  const app = await start(); t.after(app.close);
  await app.pay(valid);
  const entry = JSON.parse(app.lines[0]);
  assert.equal(entry.event, "payment.charged");
  assert.equal(entry.cardToken, "[redacted]");
  assert.ok(!app.lines[0].includes("tok_visa_4242"));
});

test("idempotency: a retried request is charged once and gets the same answer", async (t) => {
  const app = await start(); t.after(app.close);
  const first = await app.pay(valid);
  const retry = await app.pay(valid); // same key, same body — e.g. the client timed out and retried
  assert.deepEqual(await first.json(), { chargeId: "ch_1" });
  assert.deepEqual(await retry.json(), { chargeId: "ch_1" });
  assert.equal(retry.headers.get("idempotent-replayed"), "true");
  assert.equal(app.charges.length, 1);
});

test("idempotency: the same key with a different body is rejected, not silently replayed", async (t) => {
  const app = await start(); t.after(app.close);
  await app.pay(valid);
  const res = await app.pay({ ...valid, amountKobo: 9_000_000 });
  assert.equal(res.status, 422);
  assert.equal((await res.json()).error.code, "idempotency_key_reused");
  assert.equal(app.charges.length, 1);
});

test("rate limiting: three at once, then 429 with Retry-After, then refilled over time", async (t) => {
  const app = await start(); t.after(app.close);
  const statuses = [];
  for (let i = 1; i <= 4; i++) statuses.push((await app.pay(valid, { key: `k${i}` })).status);
  assert.deepEqual(statuses, [201, 201, 201, 429]);

  const limited = await app.pay(valid, { key: "k5" });
  assert.equal(limited.headers.get("retry-after"), "2");   // 0.5 tokens per second: 2 seconds for one
  assert.equal((await app.pay(valid, { key: "k6", user: "u2" })).status, 201); // limits are per user

  app.advance(2_000);
  assert.equal((await app.pay(valid, { key: "k7" })).status, 201);
});
