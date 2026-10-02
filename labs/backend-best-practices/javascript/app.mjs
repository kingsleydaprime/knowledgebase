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
