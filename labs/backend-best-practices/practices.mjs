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
