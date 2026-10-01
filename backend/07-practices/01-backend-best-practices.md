# Backend Best Practices — Errors, Validation, Logging, Rate Limits, Idempotency

> **[Intermediate]** · What separates a backend that works from one you can run in production: it fails predictably, rejects bad input at the door, leaves a useful trail, can't be flooded, and doesn't charge a customer twice when their phone retries. Most of what makes being on call bearable comes from these five.

## Before you start

You can already:

- Build an HTTP endpoint and split it into controller, service and repository → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]].
- Test code with stubs, spies and fake clocks → [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]].

After this lesson you will be able to:

1. Give every error the same response shape, from one central handler, without leaking internals.
2. Validate input at the boundary with an allowlist, and report every problem at once.
3. Write structured logs that carry a request ID and never contain secrets.
4. Rate-limit an endpoint with a token bucket, and make a payment endpoint safe to retry with an idempotency key.

**Study route.** The kid version and §1–6, then the worked example — make the predictions first. The practice task is SWE 101's week 6 milestone.

## The kid version

Think of a good post office counter. It checks your form before taking it, and tells you **every** box you got wrong, not one at a time. When something goes wrong in the back, the clerk says "sorry, there's a problem — here's your ticket number", not the details of the broken machine. It keeps a logbook, so a supervisor can find out later what happened to ticket 4071 — but it never writes your PIN in it. One person can't hand in a thousand forms and block the queue. And if you hand the same stamped form in twice because you weren't sure it went through, they recognise it and don't send your parcel twice.

**Where the analogy stops working.** A clerk can recognise a form by looking at it. A server can't tell "the same request again" from "a new, identical request" — two ₦5,000 payments in a row might be a retry or a genuine second purchase. That's why the client has to send an **idempotency key**: the stamp has to be on the form.

## 1. Why this exists

A customer taps "Pay" on a slow connection. The request reaches the server, the card is charged, but the response is lost on the way back. The app retries. The server charges again. Support gets a complaint, searches the logs, and finds free-text lines with no way to tie them to this customer's request — and, worse, a card token printed in plain text. Meanwhile a script hammering the login endpoint has slowed everyone down. **None of this is exotic. Each is the default outcome when the five practices below are skipped.**

## Terms used in this lesson

1. **Error contract**: This is the fixed shape every error response has — for example `{ error: { code, message, details, requestId } }` — so clients can handle errors with code instead of reading messages.
2. **Central error handler**: This is the one place where thrown errors become HTTP responses, so every route fails the same way.
3. **Allowlist validation**: This means defining exactly what valid input looks like and rejecting everything else, as opposed to a **denylist**, which tries to list everything bad.
4. **Structured logging**: This means writing each log entry as data — usually one JSON object per line — instead of free text, so logs can be searched and counted.
5. **Request ID**: This is also known as a **correlation ID**. It is a unique ID given to each request, written in every log line about it and returned to the client, so one request can be traced end to end.
6. **Redaction**: This means removing or masking sensitive values — passwords, tokens, card details — before they're written to a log.
7. **Rate limiting**: This means capping how many requests a client can make in a period, answering the excess with `429 Too Many Requests`.
8. **Token bucket**: This is a rate-limiting method. Each client has a bucket holding up to a fixed number of tokens; each request spends one; tokens refill at a steady rate. It allows short bursts but limits the average.
9. **Idempotency key**: This is a unique value the client sends with a request — in an `Idempotency-Key` header — so that if the same request arrives twice, the server does the work once and returns the same answer.

## 2. Errors — fail predictably, not silently or catastrophically

Every error must be handled somewhere: recovered from, or turned into a clear response. Never swallowed — an empty `catch` is the commonest source of "it's broken and nothing tells us why".

**One central handler, one error shape.** Routes throw; one handler decides the response. Errors you anticipated — validation, not found, rate limited — carry their own status and code. **Anything else is a bug:** log everything about it, and tell the client only that something went wrong, plus the request ID, so support can find the log line.

```javascript
// Express-style central handler — fragment
app.use((err, req, res, next) => {
  if (err instanceof AppError) {
    return res.status(err.status).json({ error: { code: err.code, message: err.message, requestId: req.id } });
  }
  logger.error({ requestId: req.id, message: err.message, stack: err.stack });
  res.status(500).json({ error: { code: "internal_error", message: "something went wrong", requestId: req.id } });
});
```

Never return stack traces or raw error messages to clients. They reveal internals useful to an attacker — file paths, library versions, internal hostnames — and they're bad API design. A Node-specific implementation is in [[backend/frameworks/javascript/01-node-runtime/02-error-handling|Node error handling]].

## 3. Validation — at the boundary, every time

Every input crossing into the system — request bodies, query parameters, headers, messages from a queue — is checked against an explicit shape **before** anything else touches it. Server-side, always: client-side checks are for user experience and stop nobody, because an attacker doesn't have to use your form.

Two habits make validation good rather than merely present:

- **Report every problem at once.** One round trip per mistake is a bad experience.
- **Pass on only the fields you checked.** Copying the whole body through lets an attacker add fields you never meant to accept — `isAdmin: true` is the classic. This is called **mass assignment**.

In real projects, use a schema library instead of hand-written checks:

```javascript
// with zod — fragment
const Payment = z.object({
  amountKobo: z.number().int().positive(),
  currency: z.string().regex(/^[A-Z]{3}$/),
  cardToken: z.string().startsWith("tok_"),
});
const result = Payment.safeParse(req.body); // unknown keys are stripped by default
if (!result.success) throw new AppError(400, "validation_failed", "the request body is invalid", result.error.issues);
```

Validate **configuration at startup** on the same principle: if a required environment variable is missing, crash immediately with a clear message, not an hour later deep in business logic → [[backend/frameworks/javascript/01-node-runtime/01-env-validation|environment validation]].

Validation is not the whole defence against injection or XSS — that's [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation and output encoding]], next week.

## 4. Logging — for the person reading at 3am

Logs are for whoever is reconstructing an incident under pressure. Write them for that reader.

- **Structured** — one JSON object per line, so you can filter by `requestId` or count by `event` instead of grepping prose.
- **Levelled** — `info`, `warn`, `error` — so routine noise doesn't bury real failures, and verbosity can change per environment.
- **Correlated** — the request ID in every line, and returned to the client in a header, so "my payment failed, here's the ID" leads straight to the log.
- **Redacted** — never log passwords, tokens, full card numbers or authorization headers. Logs usually have looser access controls than the database, and leaked logs are a common way sensitive data gets out. Redact by key, centrally, so a forgetful developer can't bypass it.

Logging *everything* is its own failure: storage cost, noisy search, and more places for sensitive data to leak.

## 5. Rate limiting — nobody gets to flood the queue

Without a limit, one client — a bug, a scraper, someone guessing passwords — can consume capacity meant for everyone. **Limit per identity** (the user ID when logged in, the IP when not), answer the excess with `429`, and send a `Retry-After` header so well-behaved clients know when to come back.

**The token bucket**, step by step, with a capacity of 3 and a refill of 0.5 tokens per second:

```
t = 0s   bucket: 3.0   request → allowed   bucket: 2.0
t = 0s   bucket: 2.0   request → allowed   bucket: 1.0
t = 0s   bucket: 1.0   request → allowed   bucket: 0.0
t = 0s   bucket: 0.0   request → 429, Retry-After: 2  (one token needs 1 ÷ 0.5 = 2 seconds)
t = 2s   bucket: 1.0   request → allowed   bucket: 0.0
```

It allows a burst of 3, then settles to one request every 2 seconds. The common alternative, a **fixed window** ("100 per minute"), is simpler but lets a client send 200 in two seconds across a minute boundary.

**Limit the expensive and the sensitive first:** login, password reset, sign-up, anything that sends email or SMS, and anything that calls a paid API — including LLM calls. In production with more than one server, the counters have to live somewhere shared, such as Redis, or each server enforces its own separate limit.

## 6. Idempotency — safe to retry

Networks lose responses. Clients — and payment providers sending webhooks — retry. For anything that moves money or sends something, **a retry must not do the work twice.**

The standard mechanism, used by Stripe and most payment APIs:

1. The client generates a unique key per *intended* action — a new one for a new purchase, the same one for a retry of the same purchase — and sends it as `Idempotency-Key`.
2. The server records the key with the response it produced.
3. If the key comes again **with the same request**, the server returns the stored response without doing the work again.
4. If the key comes again **with a different request**, that's a client bug — reject it with `422` rather than guess which one was meant.

The same idea, without a header, is why consumers of queues and webhooks deduplicate on an event ID → [[backend/03-structuring-a-backend/05-modular-monolith-to-services|modular monolith]] · [[architecture/03-architectural-patterns/05-transactional-outbox|transactional outbox]].

## Worked example — one payments endpoint, all five practices

One `POST /payments` endpoint on Node's built-in HTTP server, so nothing needs installing. The clock, the log writer, the card processor and the request IDs are all passed in, so the tests control them.

```javascript
// practices.mjs — the pieces, each small enough to test on its own.

// ---- Errors: one shape for every failure the client sees ----
export class AppError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// ---- Validation: an allowlist of fields and shapes, checked at the boundary ----
export function validatePayment(body) {
  const issues = [];
  if (typeof body !== "object" || body === null) throw new AppError(400, "invalid_body", "body must be a JSON object");
  if (!Number.isInteger(body.amountKobo) || body.amountKobo <= 0) issues.push({ field: "amountKobo", problem: "must be a positive whole number" });
  if (!/^[A-Z]{3}$/.test(body.currency ?? "")) issues.push({ field: "currency", problem: "must be a 3-letter code, like NGN" });
  if (typeof body.cardToken !== "string" || !body.cardToken.startsWith("tok_")) issues.push({ field: "cardToken", problem: "must be a card token" });
  if (issues.length) throw new AppError(400, "validation_failed", "the request body is invalid", issues);
  return { amountKobo: body.amountKobo, currency: body.currency, cardToken: body.cardToken }; // only known fields pass
}

// ---- Logging: one JSON object per line, with secrets removed before writing ----
const SECRET_KEYS = /token|password|secret|authorization|card/i;
export function redact(value) {
  if (Array.isArray(value)) return value.map(redact);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, SECRET_KEYS.test(k) ? "[redacted]" : redact(v)]));
  }
  return value;
}
export function makeLogger(write, clock) {
  const log = (level) => (fields) => write(JSON.stringify(redact({ time: new Date(clock.now()).toISOString(), level, ...fields })));
  return { info: log("info"), warn: log("warn"), error: log("error") };
}

// ---- Rate limiting: a token bucket per key ----
// Each key gets `capacity` requests at once, refilled at `perSecond`. The clock is passed in.
export function tokenBucket({ capacity, perSecond, clock }) {
  const buckets = new Map();
  return function take(key) {
    const now = clock.now();
    const b = buckets.get(key) ?? { tokens: capacity, at: now };
    b.tokens = Math.min(capacity, b.tokens + ((now - b.at) / 1000) * perSecond);
    b.at = now;
    buckets.set(key, b);
    if (b.tokens >= 1) {
      b.tokens -= 1;
      return { allowed: true };
    }
    return { allowed: false, retryAfterSeconds: Math.ceil((1 - b.tokens) / perSecond) };
  };
}

// ---- Idempotency: the same key gets the same answer, and the work happens once ----
export function idempotencyStore() {
  const seen = new Map(); // key -> { fingerprint, response }
  return {
    async run(key, fingerprint, work) {
      const prior = seen.get(key);
      if (prior && prior.fingerprint !== fingerprint) {
        throw new AppError(422, "idempotency_key_reused", "this Idempotency-Key was used with a different request");
      }
      if (prior) return { ...prior.response, replayed: true };
      const response = await work();
      seen.set(key, { fingerprint, response });
      return { ...response, replayed: false };
    },
  };
}
```

```javascript
// app.mjs — a payments endpoint that uses every piece, plus one central error handler.
import { createServer } from "node:http";
import { randomUUID } from "node:crypto";
import { AppError, idempotencyStore, makeLogger, tokenBucket, validatePayment } from "./practices.mjs";

export function createApp({ clock, write, charge, newId = randomUUID }) {
  const log = makeLogger(write, clock);
  const limit = tokenBucket({ capacity: 3, perSecond: 0.5, clock });
  const idempotency = idempotencyStore();

  async function handle(req, requestId) {
    if (req.method !== "POST" || req.url !== "/payments") throw new AppError(404, "not_found", "no such route");

    const verdict = limit(req.headers["x-user-id"] ?? req.socket.remoteAddress);
    if (!verdict.allowed) {
      throw new AppError(429, "rate_limited", "too many requests", { retryAfterSeconds: verdict.retryAfterSeconds });
    }

    const key = req.headers["idempotency-key"];
    if (!key) throw new AppError(400, "idempotency_key_required", "send an Idempotency-Key header");

    let raw = "";
    for await (const chunk of req) raw += chunk;
    let body;
    try { body = JSON.parse(raw); } catch { throw new AppError(400, "invalid_json", "body is not valid JSON"); }
    const payment = validatePayment(body);

    const result = await idempotency.run(key, raw, async () => {
      const chargeId = await charge(payment);
      log.info({ requestId, event: "payment.charged", chargeId, amountKobo: payment.amountKobo, cardToken: payment.cardToken });
      return { status: 201, body: { chargeId } };
    });
    return { status: result.status, body: result.body, headers: { "idempotent-replayed": String(result.replayed) } };
  }

  return createServer(async (req, res) => {
    const requestId = newId();
    try {
      const { status, body, headers = {} } = await handle(req, requestId);
      res.writeHead(status, { "content-type": "application/json", "x-request-id": requestId, ...headers });
      res.end(JSON.stringify(body));
    } catch (err) {
      // The one place errors become responses. Known errors keep their status and code;
      // anything else is a bug: log everything, tell the client nothing internal.
      const known = err instanceof AppError;
      const status = known ? err.status : 500;
      if (!known) log.error({ requestId, event: "unhandled", message: err.message, stack: err.stack });
      const headers = { "content-type": "application/json", "x-request-id": requestId };
      if (status === 429) headers["retry-after"] = String(err.details.retryAfterSeconds);
      res.writeHead(status, headers);
      res.end(JSON.stringify({
        error: {
          code: known ? err.code : "internal_error",
          message: known ? err.message : "something went wrong",
          ...(known && err.details ? { details: err.details } : {}),
          requestId,
        },
      }));
    }
  });
}
```

**Predict before running.**

1. A body with a negative amount, the currency `"naira"`, and no card token: how many problems come back?
2. The card processor throws `ECONNRESET talking to processor at 10.0.4.17`. What does the client see, and where does the IP address end up?
3. The same payment is sent twice with the same `Idempotency-Key`. How many charges?
4. One user sends four payments at once, then waits two seconds. Which statuses come back?

```javascript
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
```

**Lab:** these files are in `labs/backend-best-practices/`. From the vault root, `python3 labs/run.py backend-best-practices` runs them and checks this page still shows the same code.

**Run it.** From `labs/backend-best-practices/`, run `node --test` (Node 22 or later; checked with Node 26). Expected:

```
ℹ tests 6
ℹ pass 6
ℹ fail 0
```

**The answers.**

1. **Three problems, in one response**, in the error contract, with the request ID.
2. The client sees `internal_error` and **"something went wrong"** with the request ID — nothing about the processor or its address. The log line has the full message and stack, under the **same request ID**, so support can go from the customer's complaint straight to it.
3. **One charge.** The retry gets the same `chargeId`, marked `idempotent-replayed: true`.
4. **201, 201, 201, 429** with `Retry-After: 2`. Another user is unaffected. After two seconds, one more is allowed.

**Notice:** the card token is in the code's log call, and it's still not in the log. Redaction lives in the logger, by key, so it doesn't depend on every developer remembering.

**The limits of this version.** Both the rate-limit counters and the idempotency records live in memory: they vanish on restart and aren't shared between servers. In production both go in a shared store, such as Redis or a database table with a unique constraint on the key. Idempotency keys should also be scoped per user and expire after a day or so. And two identical requests arriving at the *same instant* would both start the work — production stores mark a key as "in progress" first, so the second waits or gets a `409`.

## Common pitfalls

1. **Empty `catch` blocks** — the error is gone, and so is the evidence.
2. **Leaking internals** — stack traces, SQL errors, internal hostnames in responses.
3. **Client-only validation** — enforced in the browser means enforced nowhere.
4. **Passing the whole request body through** — mass assignment.
5. **Free-text logs with no request ID** — unsearchable during the incident when you need them.
6. **Logging the request body or headers wholesale** — that's how tokens and passwords end up in logs.
7. **Rate limits held in one server's memory** behind a load balancer — each server enforces its own, so the real limit is multiplied.
8. **Retrying payments without an idempotency key** — and its mirror image, generating a *new* key on each retry, which defeats the point.

## Check your understanding

1. Why should a `500` response contain a request ID but not the error message?
2. What is mass assignment, and which validation habit prevents it?
3. A token bucket has capacity 10 and refills 1 token per second. A client sends 15 requests at once. How many succeed, and when can the next one go through?
4. What's the difference between a retry and a second identical purchase, from the server's point of view — and how does the idempotency key resolve it?
5. Why reject a reused idempotency key with a different body, instead of just replaying the stored response?

<details>
<summary>Answers — after your attempt</summary>

1. The ID lets support find the full error in the logs; the message could reveal internals to an attacker and means nothing to a user.
2. Copying unchecked fields from the request into your data — such as `isAdmin: true`. Prevent it by passing on only the fields you validated.
3. Ten succeed and five get `429`. The next one can go through after one second, once one token has refilled.
4. To the server they look identical. The client decides: the same key means "this is a retry of the same action"; a new key means "this is a new action".
5. A different body under the same key means the client has a bug — it reused a key for a different action. Replaying would silently return a response for a request it didn't make; rejecting surfaces the bug.

</details>

## Practice — independent task

**This is SWE 101's week 6 milestone: harden the flagship.**

1. Add a central error handler and an error contract. Make every route throw instead of formatting its own errors. Write a test that a thrown unknown error produces a `500` with a request ID and no internal detail.
2. Validate every request body with a schema library, reporting all problems at once and passing on only known fields.
3. Switch to structured JSON logs with a request ID on every line, returned in a response header. Add key-based redaction, and a test that a token never reaches the log.
4. Rate-limit the flagship's most expensive route — the LLM call, sign-up or login — with a test using a fake clock.
5. If the flagship takes payments or sends anything costly, add idempotency keys to that endpoint, with the retry test.

**Done when:** all tests pass in random order, a deliberately broken route returns the error contract rather than a stack trace, and you can take a request ID from a response and find every log line for that request.

## Before moving on

You can make errors predictable, validate at the boundary, write logs someone can use during an incident, rate-limit a route, and make a payment safe to retry.

**Recap.** One error shape from one handler; internals stay in the logs. Allowlist validation at the boundary, all problems at once, known fields only. Structured, levelled, correlated, redacted logs. Token-bucket rate limits on expensive and sensitive routes, with shared storage in production. Idempotency keys wherever a retry could double the effect.

**Next.** [[devops/10-observability/01-observability-fundamentals|Observability fundamentals]] — the other half of week 6: turning those logs into answers to "is it up, and is it fast?"

## Related
- [[backend/frameworks/javascript/01-node-runtime/02-error-handling|Node error handling]] · [[backend/frameworks/javascript/01-node-runtime/01-env-validation|environment validation]]
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|Input validation and output encoding]] — the security half of validation
- [[backend/05-auth/01-authentication-flows|Authentication flows]] — where rate limiting matters most
- [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic attacks and best practices]] — handling secrets
