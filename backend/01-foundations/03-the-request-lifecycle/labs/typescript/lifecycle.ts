// lifecycle.ts — the nine stages of a request, built by hand on node:http so nothing is hidden: an onion of
// middleware, a router that knows route templates, authentication before the handler and ownership checked in the
// query, parse-don't-validate, response DTOs, one error-mapping table, a rate limit in front of auth, a request ID
// on everything, and metrics keyed by route template.
import http, { type IncomingHttpHeaders, type IncomingMessage } from "node:http";
import { randomUUID } from "node:crypto";

// ---------- Errors: what went wrong, in the code's own words. Only toHttp knows about status codes. ----------

export class AppError extends Error {}
export class NotFoundError extends AppError {}
export class OutOfStockError extends AppError {}
export class UnauthorizedError extends AppError {}
export class BadRequestError extends AppError {}
export class PayloadTooLargeError extends AppError {}
export class TooManyRequestsError extends AppError {}
export class ValidationError extends AppError {
  issues: string[];
  constructor(issues: string[]) {
    super(issues.join("; "));
    this.issues = issues;
  }
}
export class MethodNotAllowedError extends AppError {
  allow: string[];
  constructor(allow: string[]) {
    super(`allowed: ${allow.join(", ")}`);
    this.allow = allow;
  }
}

export interface HttpError {
  status: number;
  body: Record<string, unknown>;
  headers?: Record<string, string>;
}

/** Stage 8, in one place. Anything not on the list is a bug: 500, a generic message, and the request ID to quote. */
export function toHttp(err: unknown, requestId: string): HttpError {
  if (err instanceof ValidationError) return { status: 422, body: { error: "invalid input", issues: err.issues } };
  if (err instanceof BadRequestError) return { status: 400, body: { error: err.message } };
  if (err instanceof UnauthorizedError) return { status: 401, body: { error: "unauthorized" }, headers: { "www-authenticate": "Bearer" } };
  if (err instanceof NotFoundError) return { status: 404, body: { error: "not found" } };
  if (err instanceof MethodNotAllowedError) return { status: 405, body: { error: "method not allowed" }, headers: { allow: err.allow.join(", ") } };
  if (err instanceof OutOfStockError) return { status: 409, body: { error: "out of stock" } };
  if (err instanceof PayloadTooLargeError) return { status: 413, body: { error: "body too large" } };
  if (err instanceof TooManyRequestsError) return { status: 429, body: { error: "too many requests" }, headers: { "retry-after": "1" } };
  return { status: 500, body: { error: "internal error", requestId } };
}

// ---------- The context every stage reads and writes, and the onion that runs the stages. ----------

export interface User {
  id: string;
  name: string;
  email: string;
  passwordHash: string; // must never leave the server
}

export interface Ctx {
  method: string;
  path: string;
  headers: IncomingHttpHeaders;
  ip: string;
  req?: IncomingMessage; // the body is still unread on here
  requestId: string;
  route?: string; // the template that matched, such as "/orders/:id"
  params: Record<string, string>;
  user?: User;
  status: number;
  body: unknown;
  responseHeaders: Record<string, string>;
  trace: string[];
}

export function newCtx(fields: Partial<Ctx> = {}): Ctx {
  return { method: "GET", path: "/", headers: {}, ip: "127.0.0.1", requestId: "", params: {}, status: 404, body: null, responseHeaders: {}, trace: [], ...fields };
}

export type Next = () => Promise<void>;
export type Middleware = (ctx: Ctx, next: Next) => Promise<void>;

/**
 * Runs middleware as an onion: each one gets `next`, which runs everything inside it. Code before `await next()`
 * runs on the way in, code after it on the way out.
 */
export function compose(stack: Middleware[]): (ctx: Ctx) => Promise<void> {
  return (ctx) => {
    let last = -1;
    const run = async (i: number): Promise<void> => {
      if (i <= last) throw new Error("next() called twice");
      last = i;
      if (i < stack.length) await stack[i](ctx, () => run(i + 1));
    };
    return run(0);
  };
}

// ---------- Stage 5: parse, don't validate. ----------

export type PositiveInt = number & { readonly __brand: "PositiveInt" }; // only parseCreateOrder makes one

export interface CreateOrder {
  productId: string;
  quantity: PositiveInt;
}

/** Turns untrusted JSON into a CreateOrder, or says everything that's wrong with it at once. */
export function parseCreateOrder(input: unknown): CreateOrder {
  if (typeof input !== "object" || input === null || Array.isArray(input)) throw new ValidationError(["body must be a JSON object"]);
  const fields = input as Record<string, unknown>;
  const issues: string[] = [];
  for (const key of Object.keys(fields)) {
    if (key !== "productId" && key !== "quantity") issues.push(`unknown field: ${key}`); // an allowlist: no mass assignment
  }
  const { productId, quantity } = fields;
  if (typeof productId !== "string" || !/^p\d+$/.test(productId)) issues.push("productId must look like p1");
  if (typeof quantity !== "number" || !Number.isInteger(quantity) || quantity < 1 || quantity > 100) issues.push("quantity must be a whole number from 1 to 100");
  if (issues.length > 0) throw new ValidationError(issues);
  return { productId: productId as string, quantity: quantity as PositiveInt };
}

// ---------- Stage 6's data, and stage 7's response shapes. ----------

export interface Order {
  id: string;
  customerId: string;
  productId: string;
  quantity: number;
  status: "placed";
  internalNotes: string; // must never leave the server either
}

export function toUserResponse(user: User) {
  return { id: user.id, name: user.name, email: user.email }; // an allowlist of fields, never `return user`
}

export function toOrderResponse(order: Order) {
  return { id: order.id, productId: order.productId, quantity: order.quantity, status: order.status };
}

export function seedStore() {
  const users = new Map<string, User>([
    ["token-ada", { id: "c7", name: "Ada", email: "ada@example.test", passwordHash: "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$aGFzaA" }],
    ["token-bo", { id: "c8", name: "Bo", email: "bo@example.test", passwordHash: "$argon2id$v=19$m=65536,t=3,p=4$c2FsdDI$aGFzaDI" }],
  ]);
  const orders = new Map<string, Order>([
    ["o1", { id: "o1", customerId: "c7", productId: "p1", quantity: 1, status: "placed", internalNotes: "fraud score 0.12" }],
    ["o2", { id: "o2", customerId: "c8", productId: "p2", quantity: 2, status: "placed", internalNotes: "fraud score 0.81" }],
  ]);
  const stock = new Map([["p1", 3], ["p2", 10]]);
  return {
    users,
    orders,
    stock,
    /** The IDOR-shaped query: any order, whoever asks. */
    findById: (id: string) => orders.get(id),
    /** Authorisation in the query itself: only an order this customer owns. Someone else's looks exactly like a missing one. */
    findOwned: (id: string, customerId: string) => {
      const order = orders.get(id);
      return order?.customerId === customerId ? order : undefined;
    },
  };
}

// ---------- Middleware: stages 2, 4 and 9. ----------

export interface Metrics {
  series: Map<string, number[]>; // "GET /orders/:id 200" → durations in ms
  rawPaths: Set<string>; // what the series would be keyed by if we used the raw path
}

export interface State {
  store: ReturnType<typeof seedStore>;
  metrics: Metrics;
  logs: { requestId: string; message: string }[];
  authChecks: number;
}

const VALID_REQUEST_ID = /^[\w-]{1,64}$/;

/** Stage 2, first of all: every request gets an ID, echoed on the response and on every log line. */
export const requestId: Middleware = async (ctx, next) => {
  const incoming = ctx.headers["x-request-id"];
  ctx.requestId = typeof incoming === "string" && VALID_REQUEST_ID.test(incoming) ? incoming : randomUUID(); // never trust it blindly: it goes into logs
  ctx.responseHeaders["x-request-id"] = ctx.requestId;
  await next();
};

/** Stage 9: duration and outcome per route template. `finally`, so failures are measured too. */
export function metrics(m: Metrics): Middleware {
  return async (ctx, next) => {
    const start = performance.now();
    try {
      await next();
    } finally {
      const key = `${ctx.method} ${ctx.route ?? "unmatched"} ${ctx.status}`;
      m.series.set(key, [...(m.series.get(key) ?? []), performance.now() - start]);
      m.rawPaths.add(`${ctx.method} ${ctx.path}`);
    }
  };
}

/** Wraps everything that can throw, and turns what's thrown into a response. The detail goes to the log, not the client. */
export function errors(logs: State["logs"]): Middleware {
  return async (ctx, next) => {
    try {
      await next();
    } catch (err) {
      const mapped = toHttp(err, ctx.requestId);
      if (mapped.status === 500) logs.push({ requestId: ctx.requestId, message: (err as Error).stack ?? String(err) });
      ctx.status = mapped.status;
      ctx.body = mapped.body;
      Object.assign(ctx.responseHeaders, mapped.headers);
    }
  };
}

/** Answers browsers' CORS preflights. They carry no credentials, so this must come before anything that demands them. */
export function cors(allowedOrigin: string): Middleware {
  return async (ctx, next) => {
    if (ctx.headers.origin === allowedOrigin) ctx.responseHeaders["access-control-allow-origin"] = allowedOrigin;
    if (ctx.method === "OPTIONS" && ctx.headers["access-control-request-method"]) {
      Object.assign(ctx.responseHeaders, { "access-control-allow-methods": "GET, POST", "access-control-allow-headers": "authorization, content-type" });
      ctx.status = 204;
      return; // a preflight never reaches auth or the router
    }
    await next();
  };
}

/** A fixed-window limit per client address: cheap, so it goes in front of the expensive stages. */
export function rateLimit(limit: number, windowMs: number, now: () => number = Date.now): Middleware {
  const windows = new Map<string, { start: number; count: number }>();
  return async (ctx, next) => {
    const t = now();
    let w = windows.get(ctx.ip);
    if (!w || t - w.start >= windowMs) windows.set(ctx.ip, (w = { start: t, count: 0 }));
    if (++w.count > limit) throw new TooManyRequestsError();
    await next();
  };
}

/** Stage 4a, authentication: a global guard. Every path needs a valid bearer token except the public ones. */
export function authenticate(state: State, publicPaths: string[]): Middleware {
  return async (ctx, next) => {
    if (!publicPaths.includes(ctx.path)) {
      state.authChecks++; // in real life: a session lookup or a signature check, the expensive part
      const token = /^Bearer (\S+)$/.exec(ctx.headers.authorization ?? "")?.[1];
      ctx.user = token ? state.store.users.get(token) : undefined;
      if (!ctx.user) throw new UnauthorizedError();
    }
    await next();
  };
}

// ---------- Stage 3, routing, and stage 6, the handlers. ----------

interface Route {
  method: string;
  template: string;
  handle: (ctx: Ctx) => Promise<void>;
}

function match(template: string, path: string): Record<string, string> | undefined {
  const want = template.split("/");
  const got = path.split("/");
  if (want.length !== got.length) return undefined;
  const params: Record<string, string> = {};
  for (let i = 0; i < want.length; i++) {
    if (want[i].startsWith(":")) params[want[i].slice(1)] = decodeURIComponent(got[i]);
    else if (want[i] !== got[i]) return undefined;
  }
  return params;
}

/** Finds the route for method + path. A path that exists under another method is a 405, not a 404. */
export function router(routes: Route[]): Middleware {
  return async (ctx) => {
    const candidates = routes.flatMap((r) => {
      const params = match(r.template, ctx.path);
      return params ? [{ route: r, params }] : [];
    });
    if (candidates.length === 0) throw new NotFoundError();
    const hit = candidates.find((c) => c.route.method === ctx.method);
    if (!hit) throw new MethodNotAllowedError(candidates.map((c) => c.route.method));
    ctx.route = hit.route.template;
    ctx.params = hit.params;
    await hit.route.handle(ctx);
  };
}

/** Reads the body, refusing more than `limit` bytes: by the declared length if there is one, by counting if not. */
export async function readJson(ctx: Ctx, limit: number): Promise<unknown> {
  if (Number(ctx.headers["content-length"] ?? 0) > limit) throw new PayloadTooLargeError();
  let size = 0;
  const chunks: Buffer[] = [];
  for await (const chunk of ctx.req ?? []) {
    size += chunk.length;
    if (size > limit) throw new PayloadTooLargeError();
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new BadRequestError("body is not valid JSON");
  }
}

export function shopRoutes(state: State, bodyLimit: number): Route[] {
  const { store } = state;
  return [
    { method: "GET", template: "/health", handle: async (ctx) => void Object.assign(ctx, { status: 200, body: { status: "ok" } }) },
    { method: "GET", template: "/me", handle: async (ctx) => void Object.assign(ctx, { status: 200, body: toUserResponse(ctx.user!) }) },
    {
      method: "GET",
      template: "/orders/:id",
      handle: async (ctx) => {
        const order = store.findOwned(ctx.params.id, ctx.user!.id);
        if (!order) throw new NotFoundError();
        Object.assign(ctx, { status: 200, body: toOrderResponse(order) });
      },
    },
    {
      method: "POST",
      template: "/orders",
      handle: async (ctx) => {
        const input = parseCreateOrder(await readJson(ctx, bodyLimit)); // past this line, input is trusted and typed
        const left = store.stock.get(input.productId);
        if (left === undefined) throw new NotFoundError();
        if (left < input.quantity) throw new OutOfStockError();
        store.stock.set(input.productId, left - input.quantity);
        const order: Order = { id: `o${store.orders.size + 1}`, customerId: ctx.user!.id, ...input, status: "placed", internalNotes: "" };
        store.orders.set(order.id, order);
        Object.assign(ctx, { status: 201, body: toOrderResponse(order) });
      },
    },
    {
      method: "GET",
      template: "/boom",
      handle: async () => {
        throw new Error("connect ECONNREFUSED db.internal:5432 as shop_admin"); // the kind of detail that must not leak
      },
    },
  ];
}

// ---------- Stage 1, and putting it together. ----------

export interface Options {
  rateLimit?: number; // requests per second per address
  bodyLimit?: number; // bytes
  /** The middleware order. The default is the right one; tests pass wrong ones to see what breaks. */
  stack?: (parts: Record<"requestId" | "metrics" | "errors" | "cors" | "rateLimit" | "authenticate", Middleware>) => Middleware[];
}

export const ALLOWED_ORIGIN = "https://shop.example";

export async function startApp(options: Options = {}): Promise<{ url: string; state: State; close: () => Promise<void> }> {
  const state: State = { store: seedStore(), metrics: { series: new Map(), rawPaths: new Set() }, logs: [], authChecks: 0 };
  const parts = {
    requestId,
    metrics: metrics(state.metrics),
    errors: errors(state.logs),
    cors: cors(ALLOWED_ORIGIN),
    rateLimit: rateLimit(options.rateLimit ?? 1000, 1000),
    authenticate: authenticate(state, ["/health"]),
  };
  const order = options.stack ?? ((p) => [p.requestId, p.metrics, p.errors, p.cors, p.rateLimit, p.authenticate]);
  const app = compose([...order(parts), router(shopRoutes(state, options.bodyLimit ?? 1024))]);

  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const ctx = newCtx({ method: req.method ?? "GET", path: url.pathname, headers: req.headers, ip: req.socket.remoteAddress ?? "", req });
    try {
      await app(ctx);
    } catch {
      Object.assign(ctx, { status: 500, body: { error: "internal error" } }); // the last resort, if a stack puts errors too far in
    }
    const body = ctx.body === null ? "" : JSON.stringify(ctx.body);
    res.writeHead(ctx.status, { ...ctx.responseHeaders, ...(body ? { "content-type": "application/json" } : {}) });
    res.end(body);
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address() as { port: number };
  return {
    url: `http://127.0.0.1:${port}`,
    state,
    close: () => new Promise((resolve) => {
      server.closeAllConnections();
      server.close(() => resolve());
    }),
  };
}
