# The Request Lifecycle

**[Beginner→Intermediate]** — What happens between "a request arrives" and "a response leaves", in the order it happens. Every framework implements the same nine stages; only the names differ. Learn the stages and you can read any framework's docs in an afternoon. This lesson builds all nine by hand on Node's `http` module, about 300 lines with no framework, so you can see each one work and then break it by putting it in the wrong order.

## Before you start

You can already:

- Read an HTTP request and response: method, path, headers, body and status code → [[networking/11-http-evolution/index|HTTP and its evolution]].
- Write `async` functions and `await` a promise in TypeScript.
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Name the nine stages of a request in order, and say which class of doubt each one removes.
2. Write middleware as an onion, and predict what runs, and in what order, when a handler succeeds or throws.
3. Place rate limiting, CORS, authentication and error handling in the right order, and name the symptom each wrong order produces.
4. Keep a backend's boundary honest: parse input into types, check ownership in the query, serialise through an allowlist, and map errors in one place.

**Study route:** sections 2 and 3 are the model; read them first. Sections 4 to 8 each take one stage and show what goes wrong there. Stop at each prediction and answer it before opening the answer. Section 10 is the lab.

## The kid version first

A letter arrives at a big office. Before it reaches the person who answers it, it passes a row of desks: security (are you allowed in the building?), the mailroom (which department?), a clerk (is the form filled in properly?), and then **the person who actually answers**. On the way out, it passes a desk that puts the reply in an envelope and stamps it.

Every backend framework is that corridor of desks. The desks are **middleware**; the person at the end is your **handler**.

**Where the analogy stops working.** In an office, each desk is passed once, going in. Middleware is passed twice: once on the way in and again, in reverse order, on the way out, which is how one piece of code can start a timer before the handler and stop it after. And in an office, swapping two desks changes little. In a backend, swapping two pieces of middleware can let attackers guess passwords for free, or break every browser while every test you run from the command line still passes.

## 1. Why this exists

The shop's API works in every test the team runs with `curl`. Then four things happen in one week. The new web frontend can't place orders, although the same request works from Postman. A customer notices that `GET /me` returns their password hash. Someone reads another customer's order by changing `o1` to `o2` in the URL. And the metrics backend falls over, because a dashboard keyed by URL now has a million series, one per order ID. Each of these is one stage of the lifecycle done wrong, or done in the wrong order. None of them is about the shop's actual business logic.

## Terms used in this lesson

1. **Middleware**: This is a function that runs for a request before (and usually after) the handler, doing one job such as logging, authentication or compression, and then passing the request on with `next()`.
2. **Handler**: This is the function that does the one thing a route is for, such as placing an order.
3. **Route template**: This is the pattern a router matches paths against, such as `/orders/:id`, where `:id` matches any one path segment and becomes a parameter.
4. **Authentication (authn)**: This is establishing who the caller is, from a session cookie, a token or a client certificate.
5. **Authorisation (authz)**: This is deciding whether that caller may do this particular thing to this particular record.
6. **IDOR (insecure direct object reference)**: The letters stand for those words. It's a bug where changing an ID in a request returns someone else's data, because the code checked who you are but not whether the record is yours.
7. **DTO (data transfer object)**: The letters stand for those words. It's a type describing exactly what crosses the boundary, such as the fields a request may contain or a response may reveal.
8. **Mass assignment**: This is copying every field from a request body into a record, so a caller can set fields they should never control, such as `status: "paid"`.
9. **Request ID**: This is a unique identifier given to a request when it arrives, returned in a response header and written on every log line, so one request can be followed through the logs. It's also called a correlation ID.
10. **CORS (cross-origin resource sharing)**: The letters stand for those words. It's the browser rule that a page from one origin may call an API on another only if the API says so in its response headers.
11. **Preflight**: This is the `OPTIONS` request a browser sends before a cross-origin request with custom headers, asking whether the real request is allowed. It never carries credentials.
12. **Cardinality**: In metrics, this is the number of distinct series, one per combination of label values. Each series costs memory in the metrics backend, forever.

## 2. The nine stages

```
request
   │
   ├─ 1. accept + parse        server: TCP → HTTP message; header and body size limits
   ├─ 2. global middleware     request ID, CORS, rate limit, body parsing, compression
   ├─ 3. routing               match method + path → a handler and its parameters
   ├─ 4. auth                  who are you (authn) → may you (authz)
   ├─ 5. validation            untrusted bytes → a typed value, or a 422
   ├─ 6. HANDLER               controller → service → repository
   ├─ 7. serialisation         domain object → response DTO → JSON
   ├─ 8. error mapping         domain error → status code
   └─ 9. response middleware   headers, access log, metrics
response
```

**1. Accept and parse.** The server accepts a TCP connection and parses the HTTP message. It's usually not your code, but it's where header limits, body limits and keep-alive live, and those are security controls: a server that will read a 2 GB body will be sent one. → [[networking/06-tcp-connection-lifecycle|TCP]] · [[networking/11-http-evolution/index|HTTP]]

**2. Global middleware.** This runs for every request. Assign the **request ID first**, so everything downstream can log it. Then CORS, rate limiting, body parsing with a size cap, and compression.

**3. Routing.** Match method and path to a handler, and pull out path parameters. Frameworks differ in mechanism (decorators, a router object, files in folders), not in effect. One detail most get right and hand-written routers get wrong: a path that exists under a different method is `405 Method Not Allowed` with an `Allow` header, not `404`.

**4. Authentication, then authorisation.** Two different questions, in that order. Authentication establishes identity. Authorisation decides permission, and it has two levels: the route ("may customers place orders?") and the record ("is order `o2` yours?"). The route level can't answer the record question, which is why section 5 puts it in the query. → [[backend/05-auth/index|auth]]

**5. Validation.** Turn the untrusted body into a typed value, or reject it. Do it once, at the boundary: past this line, code trusts its inputs.

**6. The handler.** Controller, then service, then repository. This is the only stage about *your product*; the other eight are plumbing. → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|layers]]

**7. Serialisation.** Domain object to response body, through an explicit list of fields. This is where data leaks happen.

**8. Error mapping.** One table that turns errors into status codes, so services can throw errors in their own words and stay ignorant of HTTP.

**9. Response middleware.** Headers, the access log, metrics: status, route template, duration.

The key idea is that the lifecycle is **a funnel of decreasing distrust.** At stage 1 you trust nothing: these are bytes from a stranger. Each stage removes one class of doubt: is it well-formed, who are you, may you, is the input valid. By stage 6, the business logic works on trusted, typed data and can think about the product instead of the attacker. **When a backend feels tangled, the funnel is usually out of order**: validation after the handler, authorisation inside a controller, error mapping scattered across forty `catch` blocks.

## 3. Middleware: an onion, not a queue

Each layer can act on the way in *and* on the way out, because it calls `next()` to run everything inside it and then continues when that finishes:

```ts
const timing: Middleware = async (ctx, next) => {
  const start = performance.now(); // on the way in
  await next();                     // everything inside: other middleware, then the handler
  record(performance.now() - start); // on the way out
};
```

The lab's `compose` is the whole mechanism, and it's twelve lines. It's the same idea as Koa's and Express's middleware chains, ASP.NET Core's pipeline and Go's `func(http.Handler) http.Handler` wrappers:

```ts
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
```

**Prediction.** The stack is `[timing, auth, handler]`, where `timing` and `auth` both push `"<name> in"`, call `next()`, then push `"<name> out"`, and the handler pushes `"handler"`. What's the trace?

<details>
<summary>Answer</summary>

`["timing in", "auth in", "handler", "auth out", "timing out"]`. The first in is the last out, like nested function calls, because that's exactly what they are: `timing` calls `next`, which calls `auth`, which calls `next`, which calls the handler.

</details>

**Prediction.** Now the handler throws. The stack is `[catcher, timing, auth, handler, never]`. `catcher` wraps `next()` in `try`/`catch`; `timing` records in a `finally`; `auth` pushes `"auth out"` after `await next()`, with no `try`. What's in the trace?

<details>
<summary>Answer</summary>

`["timing out (finally)", "caught: boom"]`. The throw skips `never` (the rest of the way in) and skips `auth`'s line after `await next()` (that line is never reached). `timing`'s `finally` still runs, and `catcher` catches. So: **the error handler goes outermost, so it wraps everything that can throw; and anything that must run on failure, like timing, uses `finally`.**

</details>

Three consequences:

- **Order matters enormously.** Section 7 is three worked examples.
- **An error unwinds outward through every layer**, so code after `await next()` without a `finally` silently doesn't run on failures. Metrics that miss every failed request look wonderful.
- **Global middleware runs on every request, including your health check.** Heavy global middleware is a latency tax on all traffic.

## 4. Stage 5: parse, don't validate

The weak version checks a blob and passes the blob along:

```ts
if (body.quantity > 0) placeOrder(body); // body may still contain status: "paid", and quantity may be "2" or 1.5
```

The strong version **parses**: it converts untrusted input into a type that can't hold invalid data, and everything after it takes that type.

```ts
export type PositiveInt = number & { readonly __brand: "PositiveInt" }; // only parseCreateOrder makes one
export interface CreateOrder { productId: string; quantity: PositiveInt }
```

`placeOrder(input: CreateOrder)` can't be called with an unparsed body, so "did anyone validate this?" is answered by the compiler. The lab's `parseCreateOrder` also checks an **allowlist** of fields, so a body containing `status` or `customerId` is rejected. Copying a body into a record with `Object.assign(order, body)` is mass assignment: the caller chooses which fields to set. Frameworks offer both responses to unknown fields. NestJS's `ValidationPipe` with `whitelist` strips them, and with `forbidNonWhitelisted` it rejects them. Rejecting is stricter and finds client bugs sooner.

The parser reports **every problem at once**, not the first. A client fixing one 422 at a time is a client making five round trips.

**Prediction.** What does `parseCreateOrder({ productId: "p1", quantity: "2" })` return?

<details>
<summary>Answer</summary>

It throws a `ValidationError` with `["quantity must be a whole number from 1 to 100"]`. The string `"2"` isn't a number. JavaScript would happily compare `"2" > 0` as true, which is exactly why the check is `typeof quantity === "number"` and `Number.isInteger`, not `> 0`.

</details>

## 5. Stage 4b: authorisation belongs in the query

Authentication says Ada is `c7`. The route `GET /orders/:id` is allowed for customers. Neither fact says whether `o2` is Ada's. The IDOR-shaped repository fetches by ID alone:

```ts
findById: (id) => orders.get(id), // any order, whoever asks
```

The fix puts ownership into the query itself, so it can't be forgotten in one handler out of forty. In SQL this is `WHERE id = $1 AND customer_id = $2`:

```ts
findOwned: (id, customerId) => {
  const order = orders.get(id);
  return order?.customerId === customerId ? order : undefined;
},
```

**Prediction.** Ada asks for `o2`, which exists and belongs to Bo. Should the answer be `403 Forbidden` or `404 Not Found`?

<details>
<summary>Answer</summary>

`404`, identical in status and body to an order that doesn't exist (the lab checks both). A `403` tells an attacker "this ID exists, you just can't see it", which lets them enumerate valid IDs. When even the existence of a record is private, a missing record and someone else's must look the same. `403` is right when the caller already knows the thing exists and is being refused an action on it, for example a customer trying an admin-only route.

</details>

## 6. Stages 7 and 8: serialise through an allowlist, map errors in one place

**Serialisation is where data leaks.** The user record has `passwordHash`; the order has `internalNotes` with a fraud score. `return user` sends them. The lab returns `toUserResponse(user)`, which lists the fields that may leave: `id`, `name`, `email`. Adding a field to the entity later doesn't add it to the response, which is the point.

**Error mapping** is one function, `toHttp`, and it's the only code that knows status codes:

| Thrown | Status | Body |
|---|---|---|
| `ValidationError` | 422 | `invalid input` and every issue |
| `BadRequestError` (unparseable JSON) | 400 | the reason |
| `UnauthorizedError` | 401 | with `WWW-Authenticate: Bearer` |
| `NotFoundError` | 404 | `not found` |
| `MethodNotAllowedError` | 405 | with `Allow: POST` |
| `OutOfStockError` | 409 | `out of stock` |
| `PayloadTooLargeError` | 413 | `body too large` |
| `TooManyRequestsError` | 429 | with `Retry-After` |
| anything else | 500 | `internal error` and the request ID, nothing more |

The last row is the important one. Anything unexpected is a bug, and its detail (here a database host and user, `ECONNREFUSED db.internal:5432 as shop_admin`) goes to the log with the request ID, **never to the client**. A stack trace in a response tells an attacker your file layout, library versions and internal hostnames. The client gets the request ID to quote to support, and you find the full story in the logs with one search.

**Body limits are checked before parsing.** `readJson` refuses a body whose declared `Content-Length` is too large without reading it, and counts bytes while reading in case the length was missing or false.

## 7. Order matters: three worked examples

The lab's `startApp` takes the middleware order as a parameter, so the tests can run the same app in the wrong order and watch what breaks. The right order:

```
requestId → metrics → errors → cors → rateLimit → authenticate → router (validation, handler, serialisation)
```

**Request ID first, metrics outside errors.** The request ID must exist before anything can fail, or the failure can't be logged with it. Metrics sit outside the error handler, so they see the final status, after the error has been turned into a 404 or a 500. Both are written so that they can't throw; that's what lets them sit outside the error handler.

**Rate limit before authentication.** Checking a token is the expensive part (a session lookup, a signature check). A rate limit is a counter. With the limit at 5 per second and eight guessed tokens, the right order answers five `401`s and three `429`s, and only **5** token checks run. In the wrong order, authentication throws on every bad token before the request ever reaches the rate limit, so all eight get `401`, all **8** are checked, and a password-guessing script is never slowed down at all.

**CORS before authentication.** A browser sends a preflight `OPTIONS` before a cross-origin `POST` with an `Authorization` header, and the preflight carries no credentials. With a global auth guard in front of CORS, the preflight gets `401`, the browser never sends the real request, and the frontend fails. From Postman or `curl`, which don't send preflights, the same `POST` succeeds. This is the first row of every "works in Postman, fails in the browser" investigation.

**Prediction.** The error handler is moved inside the rate limiter: `[requestId, metrics, cors, rateLimit, errors, authenticate]`. A client goes over the limit. What does it get?

<details>
<summary>Answer</summary>

A `500`, not a `429`. The rate limiter throws `TooManyRequestsError` outside the error handler, so nothing maps it, and it escapes the whole stack. The lab's server catches anything that escapes as a last resort and answers `500`. Without that last resort, the request would hang or the process would log an unhandled rejection. The client that should have been told to back off is told the server broke, and it'll probably retry immediately.

</details>

## 8. Stage 9: metrics by template, logs by request ID

Record **status, route template and duration** for every request. Use the template (`GET /orders/:id`), never the raw path (`GET /orders/o12345`). In the lab, twenty different order IDs make **2** series, one for `200` and one for `404`. Keyed by raw path, they'd make **20**, and in production a new series per order, per user, per search query. Each series is memory in Prometheus or Datadog, so unbounded cardinality is how a dashboard takes down the metrics backend, and also how it gets expensive.

The router sets `ctx.route` to the template that matched, and a request that matched nothing is recorded as `unmatched`. Without that, a scanner trying ten thousand random paths makes ten thousand series.

## 9. Where requests actually go wrong

| Symptom | Stage | Cause |
|---|---|---|
| Works in Postman, fails in the browser | 2 | CORS: preflight blocked, often by auth in front of it |
| Large uploads fail | 1 | a body size limit, here or in a proxy in front |
| Validation decorators silently ignored | 5 | the validation pipe was never applied; decorators do nothing alone |
| Extra fields reach the database | 5 | no allowlist on the DTO: mass assignment |
| Customers can read each other's records | 4 | ownership not checked in the query: IDOR |
| Password hash in a response | 7 | returning the entity instead of a response DTO |
| Every error is a 500 | 8 | domain errors unmapped, or the error handler not outermost |
| Stack traces in responses | 8 | the framework's development error page left on |
| Logs can't be correlated | 2 | no request ID, or assigned after something already logged |
| Metrics backend overloaded | 9 | metrics keyed by raw path |
| One slow endpoint stalls everything | 6 | blocking the event loop, or pool exhaustion → [[backend/01-foundations/04-runtime-and-concurrency-models/index\|runtime and concurrency models]] |

## 10. The lab: all nine stages, by hand

`lifecycle.ts` is a whole small framework: `compose`, the middleware, a router, `readJson` with a limit, the parser, the response DTOs, `toHttp`, and `startApp`, which serves it all on a random port with a fresh in-memory shop. The tests call it with `fetch`, so every response is a real HTTP response.

```ts
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
```

```ts
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
```

**Run it:** `python3 labs/run.py the-request-lifecycle/typescript`, or `node --test` in the lab folder.

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/01-foundations/03-the-request-lifecycle/labs/typescript).

## Common pitfalls

1. **Returning the entity.** `return user` or `res.json(order)` sends every field the record has now, and every field added later. Always serialise through a response DTO.
2. **Checking authorisation at the route only.** "Customers may read orders" isn't "this customer may read this order". Put ownership in the query.
3. **Validating without parsing.** An `if` that checks a field, followed by passing the raw body on, leaves every other field unchecked and the guarantee nowhere in the types.
4. **Error handler in the wrong place.** If it isn't outermost (apart from code that can't throw), some errors escape it, and those are the ones that become 500s or hang.
5. **Code after `await next()` with no `finally`.** It doesn't run when anything inside throws, so timings and logs quietly skip every failure.
6. **Metrics or logs keyed by raw path or user input.** Unbounded cardinality, and attacker-controlled strings in your logs. Use route templates, and validate incoming request IDs.
7. **Leaking detail in 500s.** Stack traces, SQL and hostnames belong in the log, tagged with the request ID.

## Check your understanding

1. Why must the request ID be assigned before the error handler runs, and why is it safe to put it outside the error handler?
2. Why is a `404` the right answer when a customer asks for someone else's order, and when would `403` be right?
3. The validation decorators on a NestJS DTO are present and correct, but invalid bodies reach the service. What's the most likely cause?
4. A team keys request metrics by `req.url`. Name two ways this goes wrong.
5. Why does putting the rate limiter after authentication mean it never limits a password-guessing script in the lab?
6. What's the difference between rejecting unknown fields and stripping them, and which would you choose for a public API?

<details>
<summary>Answers — after your attempt</summary>

1. The error handler logs failures with the request ID, and the 500 body includes it, so it has to exist before anything can fail. It's safe outside because it can't throw: it reads one header, checks it against a pattern, and generates a UUID if needed.
2. Because a `403` reveals that the order exists, and a `404` doesn't, so an attacker can't map out valid IDs. `403` is right when existence isn't a secret: the caller knows the resource exists and is being refused an action on it, such as a non-admin calling an admin route.
3. The validation pipe was never applied, globally or on that route. Decorators only attach metadata; something has to read it and act.
4. Cardinality: every distinct URL (order IDs, query strings) becomes a new series, without limit, which overloads the metrics backend and costs money. And query strings may carry personal data or tokens into a system with wide read access.
5. The guess fails authentication, which throws before the request reaches the rate limiter, so the limiter never counts it. Only successful requests are counted, and a guessing script makes almost none.
6. Rejecting returns a 422 naming the unknown field; stripping silently drops it and carries on. For a public API, rejecting finds client mistakes, like a typo in a field name, instead of quietly ignoring them. Stripping suits APIs that must tolerate newer clients sending fields this version doesn't know.

</details>

## Practice — independent task

**Add `PATCH /orders/:id` to the lab's framework, stage by stage.**

The customer may change only `quantity` (1 to 100), only on their own order, and only while the order's status is `placed`. Add a `shipped` status to the seed data so you can test that.

1. Write `parseUpdateOrder` with an allowlist. A body with `status` in it must be rejected.
2. Check ownership in the query. Someone else's order must be indistinguishable from a missing one.
3. Throw a new `OrderShippedError` when the order has shipped, and map it to `409` in `toHttp` only.
4. Adjust the stock correctly when the quantity goes up or down, and refuse an increase that stock can't cover.

**Done when:** you have one test per stage (401, 404 for someone else's order, 405 for `PUT`, 422 with every issue, 409 for shipped, 409 for out of stock, 200 with exactly the response DTO's fields), the stock adds up after a sequence of changes, and no `catch` block outside `errors` was added.

## Before moving on

You can name the nine stages in order, predict the trace of an onion with and without a throw, put rate limiting, CORS, auth and error handling in the right order with a reason for each, and keep the boundary honest with parsing, ownership in the query, response DTOs and one error-mapping table.

**Recap.** A request passes nine stages: accept and parse, global middleware, routing, authentication and authorisation, validation, the handler, serialisation, error mapping, and response middleware. Middleware is an onion: each layer runs on the way in and the way out, so the error handler goes outermost and anything that must run on failure uses `finally`. The stages form a funnel of decreasing distrust. Parse input into types, check ownership in the query, serialise through an allowlist, and map errors in one table that hides detail behind a request ID. Order matters: rate limit before auth, CORS before auth, request ID first. Metrics are keyed by route template, never raw path.

## Related

- [[backend/01-foundations/02-http-servers|HTTP Servers]]: the layer underneath
- [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and concurrency models]]: how stage 6 actually runs, and what blocks it
- [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers]]: what stage 6 looks like inside
- [[backend/05-auth/index|Auth]]: stage 4 in depth
- [[cybersecurity/04-web-security/index|Web security]]: the attacks each stage defends against
