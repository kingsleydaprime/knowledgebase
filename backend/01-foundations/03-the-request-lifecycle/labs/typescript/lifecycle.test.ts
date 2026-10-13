import { test } from "node:test";
import assert from "node:assert/strict";
import { ALLOWED_ORIGIN, compose, newCtx, parseCreateOrder, seedStore, startApp, ValidationError, type Middleware } from "./lifecycle.ts";

const ada = { authorization: "Bearer token-ada" };

async function call(url: string, path: string, init: RequestInit = {}) {
  const res = await fetch(url + path, init);
  const text = await res.text();
  return { status: res.status, headers: res.headers, text, body: text ? JSON.parse(text) : null };
}

test("the onion: each layer runs on the way in and on the way out", async () => {
  const layer = (name: string): Middleware => async (ctx, next) => {
    ctx.trace.push(`${name} in`);
    await next();
    ctx.trace.push(`${name} out`);
  };
  const ctx = newCtx();
  await compose([layer("timing"), layer("auth"), async (c) => void c.trace.push("handler")])(ctx);
  assert.deepEqual(ctx.trace, ["timing in", "auth in", "handler", "auth out", "timing out"]);
});

test("a throw skips the rest of the way in, and the way out of every layer without a finally", async () => {
  const ctx = newCtx();
  const catcher: Middleware = async (c, next) => {
    try {
      await next();
    } catch (err) {
      c.trace.push(`caught: ${(err as Error).message}`);
    }
  };
  const timing: Middleware = async (c, next) => {
    try {
      await next();
    } finally {
      c.trace.push("timing out (finally)");
    }
  };
  const auth: Middleware = async (c, next) => {
    await next();
    c.trace.push("auth out"); // never runs: no finally
  };
  const handler: Middleware = async () => {
    throw new Error("boom");
  };
  const never: Middleware = async (c) => void c.trace.push("never reached");
  await compose([catcher, timing, auth, handler, never])(ctx);
  assert.deepEqual(ctx.trace, ["timing out (finally)", "caught: boom"]);
  await assert.rejects(compose([async (_c, next) => { await next(); await next(); }])(newCtx()), /next\(\) called twice/);
});

test("parse, don't validate: one typed value out, or every problem at once", () => {
  assert.deepEqual(parseCreateOrder({ productId: "p1", quantity: 2 }), { productId: "p1", quantity: 2 });
  const issues = (input: unknown) => {
    try {
      parseCreateOrder(input);
      return [];
    } catch (err) {
      return (err as ValidationError).issues;
    }
  };
  assert.deepEqual(issues({ productId: "p1", quantity: 2, status: "paid", customerId: "c8" }), ["unknown field: status", "unknown field: customerId"]);
  assert.deepEqual(issues({ productId: "'; drop table", quantity: 1.5 }), ["productId must look like p1", "quantity must be a whole number from 1 to 100"]);
  assert.deepEqual(issues({ productId: "p1", quantity: "2" }), ["quantity must be a whole number from 1 to 100"]); // a string isn't a number
  assert.deepEqual(issues([1, 2]), ["body must be a JSON object"]);
});

test("the happy path: authenticated, parsed, handled, serialised", async () => {
  const app = await startApp();
  try {
    const placed = await call(app.url, "/orders", { method: "POST", headers: { ...ada, "content-type": "application/json" }, body: JSON.stringify({ productId: "p1", quantity: 2 }) });
    assert.equal(placed.status, 201);
    assert.deepEqual(placed.body, { id: "o3", productId: "p1", quantity: 2, status: "placed" }); // no customerId, no internalNotes
    assert.equal(app.state.store.stock.get("p1"), 1);
    assert.deepEqual((await call(app.url, "/me", { headers: ada })).body, { id: "c7", name: "Ada", email: "ada@example.test" }); // no passwordHash
  } finally {
    await app.close();
  }
});

test("authorisation lives in the query: someone else's order is a 404, exactly like a missing one", async () => {
  const store = seedStore();
  assert.equal(store.findById("o2")?.customerId, "c8"); // the IDOR-shaped query would hand it to anyone
  assert.equal(store.findOwned("o2", "c7"), undefined);
  const app = await startApp();
  try {
    assert.equal((await call(app.url, "/orders/o1", { headers: ada })).status, 200);
    const theirs = await call(app.url, "/orders/o2", { headers: ada });
    const missing = await call(app.url, "/orders/o99", { headers: ada });
    assert.deepEqual([theirs.status, theirs.text], [missing.status, missing.text]); // nothing to tell them apart
  } finally {
    await app.close();
  }
});

test("one error-mapping table: each failure gets its own status, and a 500 says nothing useful to an attacker", async () => {
  const app = await startApp({ bodyLimit: 1024 });
  const post = (body: string, headers = ada) => call(app.url, "/orders", { method: "POST", headers: { ...headers, "content-type": "application/json" }, body });
  try {
    assert.equal((await call(app.url, "/me")).status, 401);
    assert.equal((await call(app.url, "/me")).headers.get("www-authenticate"), "Bearer");
    assert.equal((await call(app.url, "/nowhere", { headers: ada })).status, 404);
    const wrongMethod = await call(app.url, "/orders", { method: "DELETE", headers: ada });
    assert.deepEqual([wrongMethod.status, wrongMethod.headers.get("allow")], [405, "POST"]);
    assert.equal((await post("{not json")).status, 400);
    assert.deepEqual((await post(JSON.stringify({ productId: "p1", quantity: 0 }))).body, { error: "invalid input", issues: ["quantity must be a whole number from 1 to 100"] });
    assert.equal((await post(JSON.stringify({ productId: "p1", quantity: 1, note: "x".repeat(2000) }))).status, 413); // refused before parsing
    assert.equal((await post(JSON.stringify({ productId: "p1", quantity: 4 }))).status, 409); // only 3 in stock

    const boom = await call(app.url, "/boom", { headers: ada });
    const id = boom.headers.get("x-request-id");
    assert.deepEqual([boom.status, boom.body], [500, { error: "internal error", requestId: id }]);
    assert.ok(!boom.text.includes("db.internal") && !boom.text.includes("at ")); // no detail, no stack trace
    const logged = app.state.logs.find((l) => l.requestId === id);
    assert.match(logged!.message, /ECONNREFUSED db\.internal:5432/); // the detail is in the log, findable by the ID
  } finally {
    await app.close();
  }
});

test("the request ID: honoured when sane, replaced when not", async () => {
  const app = await startApp();
  try {
    assert.equal((await call(app.url, "/health", { headers: { "x-request-id": "edge-7f3a" } })).headers.get("x-request-id"), "edge-7f3a");
    const forged = (await call(app.url, "/health", { headers: { "x-request-id": "a".repeat(500) } })).headers.get("x-request-id");
    assert.match(forged!, /^[0-9a-f-]{36}$/); // a fresh UUID instead of 500 bytes of someone else's choosing in our logs
  } finally {
    await app.close();
  }
});

test("order matters: a rate limit in front of auth makes guessing tokens cheap to refuse", async () => {
  const guess = async (url: string) => {
    const statuses = [];
    for (let i = 0; i < 8; i++) statuses.push((await call(url, "/me", { headers: { authorization: `Bearer guess-${i}` } })).status);
    return statuses;
  };
  const right = await startApp({ rateLimit: 5 });
  const wrong = await startApp({ rateLimit: 5, stack: (p) => [p.requestId, p.metrics, p.errors, p.cors, p.authenticate, p.rateLimit] });
  try {
    assert.deepEqual(await guess(right.url), [401, 401, 401, 401, 401, 429, 429, 429]);
    assert.equal(right.state.authChecks, 5); // three guesses never reached the expensive check
    assert.deepEqual(await guess(wrong.url), [401, 401, 401, 401, 401, 401, 401, 401]);
    assert.equal(wrong.state.authChecks, 8); // every guess checked, and a failed guess never even reaches the limit
  } finally {
    await right.close();
    await wrong.close();
  }
});

test("order matters: auth in front of CORS breaks every browser, while curl works fine", async () => {
  const preflight = { method: "OPTIONS", headers: { origin: ALLOWED_ORIGIN, "access-control-request-method": "POST", "access-control-request-headers": "authorization" } };
  const right = await startApp();
  const wrong = await startApp({ stack: (p) => [p.requestId, p.metrics, p.errors, p.rateLimit, p.authenticate, p.cors] });
  try {
    const ok = await call(right.url, "/orders", preflight);
    assert.deepEqual([ok.status, ok.headers.get("access-control-allow-origin")], [204, ALLOWED_ORIGIN]);
    assert.equal((await call(wrong.url, "/orders", preflight)).status, 401); // the preflight has no token, so the browser never sends the POST
    assert.equal((await call(wrong.url, "/me", { headers: ada })).status, 200); // and from Postman or curl, which skip preflights, all looks fine
  } finally {
    await right.close();
    await wrong.close();
  }
});

test("metrics by route template: 20 different order IDs are 2 series, not 20", async () => {
  const app = await startApp();
  try {
    for (let i = 1; i <= 20; i++) await call(app.url, `/orders/o${i}`, { headers: ada });
    const keys = [...app.state.metrics.series.keys()].sort();
    assert.deepEqual(keys, ["GET /orders/:id 200", "GET /orders/:id 404"]);
    assert.equal(app.state.metrics.series.get("GET /orders/:id 200")!.length, 1);
    assert.equal(app.state.metrics.rawPaths.size, 20); // keyed by raw path, every new ID would be a new series, forever
  } finally {
    await app.close();
  }
});

test("order matters: an error handler inside the rate limiter turns 'slow down' into 'we broke'", async () => {
  const app = await startApp({ rateLimit: 1, stack: (p) => [p.requestId, p.metrics, p.cors, p.rateLimit, p.errors, p.authenticate] });
  try {
    assert.equal((await call(app.url, "/me", { headers: ada })).status, 200);
    assert.equal((await call(app.url, "/me", { headers: ada })).status, 500); // the 429 escaped unmapped
  } finally {
    await app.close();
  }
});
