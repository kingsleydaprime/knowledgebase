---
id: 79ae84f7-4a06-4108-9b7c-2d2b23e04f51
---

# Observability

**Observability is how well you can tell what your running system is doing, and why, from the outside, without changing its code or stopping it. You get it from three kinds of signal: logs (what happened, one event at a time), metrics (numbers over time), and traces (the path of one request through every service it touched).** Tests tell you the code was right before it shipped. Observability tells you what it's doing *now*, with real customers, at 12:40 on a Friday.

## Before you start
<!-- bite: 6ac7397c-648e-41bc-9070-da542ec37dc2 -->

You should have both services and the safe calls between them from [[backend/frameworks/express/26-calling-services-safely|lesson 26]].

You'll run two more containers: **Jaeger**, to see traces, and **Prometheus**, to collect metrics. Both are free.

After this lesson you will be able to:

1. Replace `console.log` with structured JSON logs from pino, with request ids, levels, and secrets hidden.
2. Carry one id through HTTP, gRPC and events, so one order can be followed across services.
3. Add metrics with prom-client: request rates, errors and durations, plus the numbers that matter to Mama Put.
4. Add tracing with OpenTelemetry, mostly without writing code, and see one payment's whole journey in Jaeger.
5. Choose alerts that wake someone up only when customers are affected.

## Where we stopped
<!-- bite: c53f0358-de90-424b-b47f-3b5506d92cf4 -->

Friday, 12:45. Bayo phones Mama: "I paid ten minutes ago, I got no receipt, and the app still says 'waiting for payment'."

Where do you start? The webhook could have failed its signature check. `settle` could have found an amount mismatch. The outbox relay could be stuck. The stream could be fine but notifications' breaker open. The email provider could be down. Each of those is in a different program, and today their only record is `console.log` lines scrolling past in three terminals, mixed with everyone else's lunch orders.

You'd want to type "show me everything that happened to Bayo's payment" and see it, in order, across every service. That's what this lesson builds.

## The kid version
<!-- bite: f1febbe2-bcb7-4b8b-820c-92d557cb294c -->

Mama keeps three things.

A **notebook** where she writes what happens: "12:40 Bayo paid. 12:41 jollof finished. 12:43 Ada complained the stew was cold." That's logs.

A **board** with tallies: plates sold this hour, complaints today, how long people waited. She glances at it and knows if today is a good day. That's metrics.

And for one order, she can follow the slip: taken at the counter, pinned in the kitchen, cooked, called out, collected. Each stop has a time. That's a trace.

**Where the picture stops working.** Mama's notebook is short. Ours would get a thousand lines a minute. So our "notebook" must be searchable by machine, which means every line has a fixed shape, not free sentences.

## Terms used in observability
<!-- bite: 1ed59271-99d9-40d0-aefa-eba9409109a4 -->

1. **Structured log**: This is a log line written as data (JSON) with named fields, like `{"level":"info","msg":"payment settled","orderId":"42"}`, so a machine can search and filter it.
2. **Log level**: This is how serious a log line is: `debug`, `info`, `warn`, `error`, `fatal`.
3. **Correlation id**: This is one id carried through every step of one piece of work, so its log lines can be found together. Our request id from lesson 7 becomes one.
4. **Metric**: This is a number measured over time, like "requests per second" or "how long checkout takes".
5. **Counter**, **gauge**, **histogram**: A counter only goes up (requests served). A gauge goes up and down (open streams). A histogram records how many measurements fell into each size range (so you can ask "how slow were the slowest 5%?").
6. **Cardinality**: This is how many different values a metric's labels can take. High cardinality (a label per user) makes metrics systems slow and expensive.
7. **Trace** and **span**: A trace is the whole journey of one request. A span is one step of it ("SQL query", "gRPC call to GetContact"), with a start, an end, and a parent.
8. **OpenTelemetry**: This is an open standard and set of libraries for producing traces, metrics and logs in one common format, which many tools can read.
9. **p95** (95th percentile): This is the time that 95% of requests were faster than. Averages hide the slow requests; percentiles show them.

## Step 1: structured logs with pino
<!-- bite: 8a0b7ac0-4048-4559-8860-03fbeaba6cca -->

```bash
npm install pino pino-http -w api
npm install pino -w notifications
npm install --save-dev pino-pretty -w api
```

`api/src/shared/logger.ts`:

```ts
import pino from "pino";

export function createLogger(service: string, level = process.env.LOG_LEVEL ?? "info") {
  return pino({
    level,
    base: { service },
    timestamp: pino.stdTimeFunctions.isoTime,
    redact: {
      paths: [
        "req.headers.authorization",
        "req.headers.cookie",
        "req.headers[\"x-paystack-signature\"]",
        "*.password",
        "*.refreshToken",
        "*.accessToken",
        "*.email",
        "*.phone",
      ],
      censor: "[hidden]",
    },
  });
}

export type Logger = ReturnType<typeof createLogger>;
```

A pino log line is one line of JSON:

```json
{"level":30,"time":"2026-11-21T12:40:03.512Z","service":"api","reqId":"9f1c...","msg":"payment settled","orderId":"42","result":"paid"}
```

1. **One line, one event, named fields.** Search for `orderId = 42` across a day, count `result = "mismatch"`, find every `error`. You can't do that with `console.log("Payment for order " + id + " done!!")`.
2. **`base: { service }`**: every line says which service wrote it, so logs from all services can live in one place.
3. **`redact`**: these fields are replaced with `[hidden]` wherever they appear. Lesson 14 promised: no tokens, no passwords in logs. And here we also hide emails and phone numbers, because logs are read by many people and kept a long time. Log ids (`customerId: "7"`), not personal details.
4. **Levels**: `info` for normal events worth keeping ("payment settled"), `warn` for something odd but handled ("webhook for unknown reference"), `error` for something broken that a person should look at. `debug` for detail you only want while investigating, off in production.

Readable in development, with `pino-pretty`:

```json
"dev": "node --env-file=.env --watch src/server.ts | pino-pretty"
```

In production, the JSON goes to standard output, and the platform (Docker, lesson 28) collects it. A log collector (Loki, Elasticsearch, a hosted service) makes it searchable. Programs should only write to standard output; where logs end up is the platform's job.

### Request logs

Lesson 3's hand-written `logRequests` middleware is replaced by `pino-http`:

```ts
import { pinoHttp } from "pino-http";

app.use(
  pinoHttp({
    logger,
    genReqId: (req, res) => res.getHeader("x-request-id") as string,   // the id from lesson 7's middleware
    customLogLevel: (_req, res, err) => (err || res.statusCode >= 500 ? "error" : res.statusCode >= 400 ? "warn" : "info"),
    customProps: (req) => ({ userId: req.user?.id, apiVersion: req.baseUrl.split("/")[1] }),
    autoLogging: { ignore: (req) => req.url === "/health/live" },
  }),
);
```

It goes right after the request-id middleware, before everything else. Each request gets one log line when it finishes, with method, path, status, time taken, request id, and our extra fields. And `req.log` is a **child logger** that already has `reqId` set:

```ts
req.log.info({ orderId: order.id, result }, "payment settled");
```

Every line written through `req.log` carries the request id, without you passing it around. In services that don't see `req`, pass the logger in as a dependency, like everything else (that's what all those `log` parameters in lessons 17 to 26 were waiting for).

**The error handler** (lesson 7) logs unexpected errors with `req.log.error({ err }, "unhandled error")`. pino prints the error's message and stack. That's where the full detail goes, while the client gets the calm problem response.

**Lesson 10's v1 metric** starts as a log field: `apiVersion` above. In step 4 it becomes a real counter.

## Step 2: one id across every service
<!-- bite: d9a3c6d4-a082-4113-aea4-b079cc20facf -->

A request id works inside one service. Bayo's payment crosses four: the webhook arrives at the API, the outbox row is written, the relay publishes to the stream, notifications reads it and calls the API back over gRPC. To follow it, the id must travel with it.

1. **HTTP**: lesson 7 already reads `X-Request-Id` from incoming requests if it's there, and sends it back.
2. **gRPC**: send it in metadata. In notifications' `unary` helper, `metadata.set("x-request-id", id)`; in the API's handlers, read `call.metadata.get("x-request-id")` and make a child logger with it.
3. **Events**: put it in the envelope. Add an optional `correlationId` to `contracts/events.ts`; `addToOutbox` takes it from the request that caused the change; notifications reads it and logs with it.

Then "everything that happened to Bayo's payment" is one search: `reqId = 9f1c...` across all services.

In practice, step 5's tracing does most of this for you, with a standard id called a **trace id** that tools understand. But the idea is exactly this, and the events part (the stream) still needs your help.

## Step 3: what to log, and what not to
<!-- bite: 3e53ac6b-2ebd-45bb-ab58-e609b90d5d57 -->

Good log lines answer "what happened, to what, with what result":

1. **Business events**: order placed, payment settled (with the result: `paid`, `already-settled`, `mismatch`), order ready, webhook signature failed, refund needed, MCP tool called.
2. **Decisions and refusals**: rate limit hit, permission denied, circuit opened.
3. **Failures with context**: which call, to whom, how long it took, the error code.

Don't log:

1. **Secrets**: tokens, passwords, API keys, signatures. Redaction is the safety net, not the plan.
2. **Personal data**: emails, phone numbers, names, addresses. Ids are enough.
3. **Whole request and response bodies.** They contain both of the above, sooner or later.
4. **Every loop iteration.** One line per thing that happened, not per line of code.

Remember lesson 24: MCP tool calls are logged with who, which client, which tool, how long and the result code, and not their arguments.

## Step 4: metrics with prom-client
<!-- bite: d2368c88-43d9-4dd4-b2a9-8dd4b4af4382 -->

Logs tell you about one event. Metrics tell you about all of them at once: "how many payments failed in the last 5 minutes?" is a metric question.

```bash
npm install prom-client -w api -w notifications
```

`api/src/shared/metrics.ts`:

```ts
import client from "prom-client";

export const registry = new client.Registry();
client.collectDefaultMetrics({ register: registry });     // memory, CPU, event-loop lag

export const httpDuration = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "How long HTTP requests take",
  labelNames: ["method", "route", "status"] as const,
  buckets: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
  registers: [registry],
});

export const apiVersionRequests = new client.Counter({
  name: "api_version_requests_total",
  help: "Requests per API version",
  labelNames: ["version"] as const,
  registers: [registry],
});

export const paymentsSettled = new client.Counter({
  name: "payments_settled_total",
  help: "Results of settling payments",
  labelNames: ["result"] as const,            // paid, already-settled, mismatch, failed, unknown
  registers: [registry],
});

export const openStreams = new client.Gauge({
  name: "sse_open_streams",
  help: "Server-sent event streams open right now",
  registers: [registry],
});

export const outboxBacklog = new client.Gauge({
  name: "outbox_unpublished",
  help: "Outbox rows not yet published",
  registers: [registry],
});
```

The HTTP histogram is filled by a small middleware:

```ts
export function measureRequests(req: Request, res: Response, next: NextFunction) {
  const stop = httpDuration.startTimer();
  res.on("finish", () => {
    const route = req.route?.path ? `${req.baseUrl}${req.route.path}` : "unmatched";
    stop({ method: req.method, route, status: String(res.statusCode) });
  });
  next();
}
```

**The route label is the pattern, not the URL.** `/v2/orders/:id`, not `/v2/orders/42`. With the real URL, every order id would make a new set of numbers (that's high cardinality), and the metrics system would slowly drown. Labels must have a **small, fixed set of values**: methods, route patterns, status codes, results. Never user ids, order ids, emails or free text.

The others are one line each where the thing happens: `paymentsSettled.inc({ result })` in `settle`, `openStreams.inc()` and `.dec()` in lesson 20's stream, `apiVersionRequests.inc({ version })` in lesson 10's routers, a job in the worker that sets `outboxBacklog` from `SELECT count(*) ... WHERE published_at IS NULL` every 15 seconds. In notifications: messages handled by type and result, provider send failures, breaker state changes (lesson 26's practice).

The metrics are served for Prometheus to read, on a **separate, internal port**, never on the public API:

```ts
import http from "node:http";

http
  .createServer(async (req, res) => {
    if (req.url !== "/metrics") return res.writeHead(404).end();
    res.writeHead(200, { "Content-Type": registry.contentType });
    res.end(await registry.metrics());
  })
  .listen(9464, "0.0.0.0");
```

Metrics reveal a lot about your business (orders per minute, failure rates), so they're for your team only. In lesson 28, Docker keeps port 9464 inside the private network.

Run Prometheus with a small config, `ops/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: api
    scrape_interval: 15s
    static_configs:
      - targets: ["host.docker.internal:9464"]
  - job_name: notifications
    static_configs:
      - targets: ["host.docker.internal:9465"]
```

```bash
docker run -d --name prometheus -p 9090:9090 \
  --add-host host.docker.internal:host-gateway \
  -v "$PWD/ops/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus
```

Open `http://localhost:9090` and try queries:

1. Requests per second, by route: `sum by (route) (rate(http_request_duration_seconds_count[5m]))`
2. The share that are errors: `sum(rate(http_request_duration_seconds_count{status=~"5.."}[5m])) / sum(rate(http_request_duration_seconds_count[5m]))`
3. How slow the slowest 5% are: `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`
4. v1 traffic per day, for lesson 10's sunset decision: `sum(increase(api_version_requests_total{version="v1"}[1d]))`

Those first three are **RED**: **R**ate, **E**rrors, **D**uration. For every service, they're the first three graphs to draw. (Grafana is the usual tool for dashboards on top of Prometheus.)

## Step 5: traces with OpenTelemetry
<!-- bite: 02eb65a3-2f72-47c5-b98d-510bc136cc81 -->

Logs and metrics tell you *something* is slow. A trace tells you *where*. One payment's trace looks like this:

```text
POST /webhooks/paystack                                   [api]          48 ms
├── pg: SELECT payments WHERE reference = ...             [api]           2 ms
├── pg: BEGIN / UPDATE payments / UPDATE orders /
│       INSERT outbox / COMMIT                            [api]           9 ms
└── redis: PUBLISH kitchen                                [api]           1 ms
outbox relay: publish order.paid                          [api-worker]    3 ms
handle order.paid                                         [notifications] 412 ms
├── grpc: CustomersService/GetContact                     [notifications]  6 ms
│   └── grpc server: GetContact                           [api]            4 ms
│       └── pg: SELECT users ...                          [api]            1 ms
├── grpc: MenuService/GetDish                             [notifications]  3 ms
└── POST https://email-provider.example/send              [notifications] 398 ms   ← there it is
```

The receipt was slow because the email provider took 398 ms. Found in one look.

The good news: most of this is **automatic**. OpenTelemetry has instrumentations for Express, `http`, `pg`, `ioredis`, gRPC and `fetch` that create spans without you changing their code.

```bash
npm install @opentelemetry/api @opentelemetry/auto-instrumentations-node -w api -w notifications
```

Run Jaeger, which receives traces and shows them:

```bash
docker run -d --name jaeger -p 16686:16686 -p 4318:4318 jaegertracing/jaeger
```

(Pin a version tag in real use, as with every image.) Then start the API with the instrumentation loaded **before** your code, and a few settings in the environment:

```text
# api/.env
OTEL_SERVICE_NAME=api
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=none
OTEL_LOGS_EXPORTER=none
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

```json
"dev": "node --env-file=.env --import @opentelemetry/auto-instrumentations-node/register --watch src/server.ts | pino-pretty"
```

`--import` loads the instrumentation first, so it can wrap Express, `pg` and the rest as they're loaded. (It has to be first: anything imported before it isn't traced. If your OpenTelemetry version wants a different flag for `import`-style modules, its Node.js docs show the current one.) Do the same for the worker and notifications, with their own `OTEL_SERVICE_NAME`. We turned off OpenTelemetry's metrics and logs exporters because prom-client and pino already do those jobs.

Place an order, open `http://localhost:16686`, choose the `api` service, and find the trace.

**Across services, automatically**: the HTTP and gRPC instrumentations add a standard header, `traceparent`, to outgoing calls, and read it on incoming ones. So notifications' `GetContact` span and the API's handler span join into one trace by themselves.

**Across the stream, by hand**: Redis Streams aren't HTTP; nothing adds `traceparent` to our envelope. So we do, with OpenTelemetry's propagation API:

```ts
// api: when writing to the outbox
import { context, propagation } from "@opentelemetry/api";

const carrier: Record<string, string> = {};
propagation.inject(context.active(), carrier);           // fills carrier.traceparent
await addToOutbox(tx, "order.paid", 1, data, carrier);   // stored with the event

// notifications: when handling
const parent = propagation.extract(context.active(), event.trace ?? {});
await context.with(parent, () =>
  tracer.startActiveSpan(`handle ${event.type}`, async (span) => {
    try {
      await handle(event);
    } finally {
      span.end();
    }
  }),
);
```

Now the handling of `order.paid` in notifications appears in the same trace as the webhook that caused it, minutes apart if need be. (`trace` is a new optional field in the envelope, next to `correlationId`; once tracing is on, the trace id *is* the correlation id.)

**Your own spans**, for steps that aren't a library call:

```ts
import { trace } from "@opentelemetry/api";
const tracer = trace.getTracer("mama-put-api");

await tracer.startActiveSpan("settle payment", async (span) => {
  span.setAttribute("payment.reference", reference);
  try {
    const result = await settleInner(reference, seen);
    span.setAttribute("payment.result", result);
    return result;
  } finally {
    span.end();
  }
});
```

Attributes follow the same rule as logs: ids and results, never personal data.

**Logs and traces together.** The auto-instrumentations include one for pino, which adds `trace_id` and `span_id` to every log line written inside a span. From a slow trace in Jaeger, copy the trace id and search your logs for it. From an error log, jump to its trace.

**Sampling.** Tracing every request is fine for Mama Put. Big systems record only some (`OTEL_TRACES_SAMPLER=parentbased_traceidratio` with `OTEL_TRACES_SAMPLER_ARG=0.1` keeps 10%), and smarter setups keep every trace that had an error.

## Step 6: alerts that matter
<!-- bite: d593a443-55b8-4b3e-9d96-744a1039f066 -->

Graphs are only useful when someone looks. Alerts are graphs that look for you. The hard part is choosing, because an alert that fires for nothing teaches people to ignore alerts.

**Alert on what customers feel**, not on every cause:

| Alert | Why it matters | Rough rule |
|---|---|---|
| Error rate high | Customers see failures | More than 2% of requests 5xx for 5 minutes |
| Slow | Customers wait | p95 over 1 s for 10 minutes |
| Payments not settling | Money taken, orders not paid | `payments_settled_total{result="paid"}` flat for 30 minutes at lunchtime, or any `mismatch` |
| Outbox stuck | Nothing downstream hears anything | `outbox_unpublished` above 100 for 5 minutes |
| Jobs failing for good | Work silently lost | Any webhook delivery or job "failed for good" |
| Dead letters | Events nobody could handle | Any message in `events:dead` |
| Breaker open | A service can't reach another | Open for more than 2 minutes |

**Don't** alert on "CPU at 80%" or "one request failed". High CPU with happy customers is a busy day, not an emergency. Put those on a dashboard instead.

Each alert should say what's wrong, how bad, and where to look first, ideally with a link to a short "what to do" note (a **runbook**). Prometheus's Alertmanager or Grafana sends alerts by email, Slack, or a phone call for the serious ones.

**Health checks are not alerts.** `/health/live` and `/health/ready` (lesson 28) tell the *platform* whether to restart a container or send it traffic. Alerts tell *people*.

## Step 7: testing what you log and measure
<!-- bite: 44d00173-e2ad-4f09-92e6-55f52be717d3 -->

1. **Redaction**: make a logger that writes to an in-memory stream (pino accepts a destination stream), log `{ password: "x", user: { email: "ada@test.example" } }`, and check neither value appears in the output.
2. **The route label**: request `/v2/orders/42` and `/v2/orders/43` in a test, then read `registry.metrics()` and check there's one `route="/v2/orders/:id"` series, not two.
3. **Business counters**: settling a payment twice gives `paid` once and `already-settled` once.
4. **No metrics on the public port**: `GET /metrics` on the Express app is 404.

## The TypeScript in this lesson
<!-- bite: 628e2a2c-e1d8-4250-bbb4-fd8f9fd57b66 -->

1. **`import pino from "pino"` and `import { pinoHttp } from "pino-http"`**: a default import and a named import. Packages decide which they offer; their README says.
2. **`ReturnType<typeof createLogger>`**: the logger's type, from the factory, as always.
3. **`labelNames: ["method", "route", "status"] as const`**: `as const` keeps the exact names, so `stop({ method, route, status })` is checked: a typo like `stauts` is a type error.
4. **`const stop = httpDuration.startTimer(); ... stop({...})`**: `startTimer` returns a function; calling it later records how long it's been, with the labels you give.
5. **`req.route?.path`**: `req.route` is only set once a route has matched. For a 404, it's `undefined`, so `?.` avoids a crash and we label it `"unmatched"`.
6. **`res.on("finish", ...)`**: runs when the response has been sent, which is when we know the status and the time.
7. **`res.getHeader("x-request-id") as string`**: `getHeader` can return a number or a list too; our middleware always sets a string, so we say so.
8. **`const carrier: Record<string, string> = {}`**: an empty object of text keys and values, which `propagation.inject` fills.
9. **`context.with(parent, () => ...)`**: runs a function with `parent` as the "current" trace context, so spans started inside belong to that trace.
10. **`tracer.startActiveSpan(name, async (span) => {...})`**: starts a span, makes it current for everything inside the function (including library calls, which become its children), and gives it to you to add attributes and end.

## Your project so far
<!-- bite: 134c6b71-3464-4bcd-98b4-399544514295 -->

```text
mama-put/
├── ops/
│   └── prometheus.yml                    ← NEW: scrape api (9464) and notifications (9465)
├── contracts/events.ts                   ← envelope gains optional correlationId and trace
├── api/
│   ├── .env.example                      ← NEW: LOG_LEVEL, OTEL_* settings
│   ├── package.json                      ← NEW: pino, pino-http, prom-client, OpenTelemetry; dev pipes to pino-pretty
│   └── src/
│       ├── shared/
│       │   ├── logger.ts                 ← NEW: createLogger with redaction
│       │   ├── metrics.ts                ← NEW: registry, http histogram, business counters and gauges
│       │   ├── measure-requests.ts       ← NEW: route-pattern labels
│       │   └── metrics-server.ts         ← NEW: /metrics on internal port 9464
│       ├── log-requests.ts               ← DELETED: replaced by pino-http
│       ├── events/outbox.ts              ← stores traceparent and correlationId with each event
│       └── payments/ · orders/ · kitchen/ · grpc/ · mcp/ · ... ← req.log / injected logger; counters; spans
└── notifications/
    └── src/
        ├── logger.ts · metrics.ts        ← NEW: the same, service "notifications", port 9465
        ├── consumer.ts                   ← continues the trace from the event; logs with its ids
        └── clients/call.ts               ← sends x-request-id in gRPC metadata
```

## Common mistakes
<!-- bite: 828c16e9-a7ee-43a2-81a8-07d5b5a6d752 -->

1. **`console.log` sentences.** Unsearchable, unfilterable, no levels. Structured JSON, named fields.
2. **Secrets and personal data in logs.** Logs are read by many and kept for ages. Redact, and log ids.
3. **Real URLs or user ids as metric labels.** Cardinality explodes. Route patterns and small fixed sets only.
4. **Averages.** A 50 ms average can hide a 5-second slowest 5%. Use percentiles.
5. **Metrics on the public port.** They tell competitors and attackers your business.
6. **Loading the tracing after your code.** Anything imported first isn't instrumented. `--import` it first.
7. **Traces that stop at the queue.** Streams and queues need the context carried in the message by hand.
8. **Alerting on causes.** CPU, memory, single errors: noise. Alert on what customers feel.
9. **Alerts nobody can act on.** Every alert needs a "what to do first".

## Check your understanding
<!-- bite: a00bc598-c2cb-4a5e-bbb5-f6d4c41750d2 -->

1. Why is `{"msg":"payment settled","orderId":"42","result":"paid"}` more useful than `console.log("Payment 42 settled: paid")`?
2. Why is `route` labelled `/v2/orders/:id` and not `/v2/orders/42`?
3. Which three numbers would you graph first for a new service, and what do they tell you?
4. How does the notifications span for `GetContact` end up in the same trace as the API's handler, with no code from us?
5. Why did we have to carry `traceparent` in the event envelope ourselves?
6. CPU is at 85% at lunchtime, and error rate and p95 are normal. Should someone be woken up?

<details>
<summary>Answers, after your attempt</summary>

1. A machine can search and count it: every line with `orderId = 42`, every `result = mismatch` today. The sentence version has to be read by a person, and its wording can change at any time.
2. Each different label value makes a separate series. Real ids would make one per order, forever growing, until the metrics system slows down or falls over. The route pattern has a small fixed set of values.
3. Rate (requests per second), errors (the share that fail), and duration (how long they take, as percentiles). Together they say whether the service is busy, broken, or slow.
4. The gRPC instrumentation in notifications adds a `traceparent` header to the call's metadata; the gRPC instrumentation in the API reads it and starts its span as a child of that trace.
5. Messages on a Redis Stream aren't HTTP or gRPC calls, so no instrumentation adds or reads trace headers for them. We inject the context into the envelope when writing to the outbox and extract it when handling.
6. No. Customers are fine: errors and speed are normal. High CPU on a busy day is a dashboard item, maybe a reason to plan more capacity, not an alert.

</details>

## Practice
<!-- bite: af9d368a-e2f4-4ad2-8aea-f9fc34542c4a -->

1. Replace every `console.*` and every `log` parameter in both services with the injected pino logger, and delete `log-requests.ts`.
2. Add the counters and gauges listed in step 4, in both services, including the outbox backlog job.
3. Carry `x-request-id` through gRPC metadata and `correlationId` through events, then search the logs of all three processes for one request's id.
4. Turn on tracing in the API, the worker and notifications. Pay for an order and find the whole trace in Jaeger, from webhook to email.
5. Write the four tests from step 7.
6. Write the alert rules from step 6 as Prometheus rules (an `ops/alerts.yml`), even if nothing sends them yet.

**Done when** no `console.log` is left; logs are JSON with `service`, `reqId` and (inside spans) `trace_id` on every line, and a test proves tokens and emails are hidden; Prometheus shows RED graphs for the API and a `payments_settled_total` that goes up when you pay; and Jaeger shows one trace from Paystack's webhook through the outbox, the stream and notifications to the gRPC call back into the API.

## Before moving on
<!-- bite: 19a33fc1-a5e7-4d73-9fba-311b816de94f -->

When Bayo phones now, you search one trace id and see his payment's whole journey, across three processes, with the slow step highlighted. And alerts would probably have told you before he phoned.

Now look at how all of this runs: four terminals, Postgres, two Redis servers, Jaeger and Prometheus in separate `docker run` commands, settings scattered across `.env` files, and nothing that checks a setting is missing until something fails at lunchtime. That's fine on a laptop. It can't go to a real server. Next lesson packs the whole system into containers, checks every setting at start-up, adds health checks and polite shutdowns, and starts everything with one command.

## Related
<!-- bite: cb89c7a8-61ff-43fa-b73e-c9cf7517ee90 -->

- [[backend/frameworks/express/28-production-config-and-docker|Next: Production Config and Docker]]
- [[backend/frameworks/express/07-errors|Errors and Structured Responses]] — where the request id started
- [[backend/frameworks/express/10-versioning|Versioning]] — the v1 traffic number that decides its sunset
- [[backend/06-cross-cutting/index|Cross-cutting Concerns]] — logging, metrics and tracing in any framework

## About this lesson
<!-- bite: 332b2ba9-8abc-478a-bd82-3d9909d16611 -->

**Level:** Advanced. Lesson 27 of [[backend/frameworks/express/index|Express]]. Covers logs, metrics and traces, structured JSON logging with pino, levels, redaction of secrets and personal data, request logging with pino-http and child loggers, carrying one id through HTTP, gRPC metadata and event envelopes, what to log and what not to, metrics with prom-client (counters, gauges, histograms, default metrics), route-pattern labels and cardinality, an internal metrics port, Prometheus queries for rate, errors and duration and percentiles, tracing with OpenTelemetry's auto-instrumentations loaded with `--import`, Jaeger, `traceparent` across HTTP and gRPC, carrying trace context through Redis Streams by hand, custom spans, logs with trace ids, sampling, alerts on customer-facing symptoms with runbooks, and testing redaction, labels and counters.
