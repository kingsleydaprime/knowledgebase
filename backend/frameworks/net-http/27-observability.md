---
id: 20198cb2-4690-4f76-a8f9-7950bec1472a
---

# Observability

**Observability is being able to tell what your running system is doing, and why, from the outside, without adding new code first. It comes from three kinds of signal: logs (what happened, line by line), metrics (numbers over time: how many, how fast, how full) and traces (one request's whole journey through every program it touched).** When Ada says "I paid at 12:40 and never got a receipt", observability is the difference between answering in two minutes and guessing for two hours.

## Before you start
<!-- bite: 248b184e-cd64-4087-83d4-442a5fe53e8c -->

You should have finished [[backend/frameworks/net-http/26-calling-services-safely|lesson 26]], with the API, the worker and the notifications service running. You've been logging since lesson 3 and putting a request ID in the context since lesson 7; this lesson builds on both.

After this lesson you will be able to:

1. Write structured JSON logs with `log/slog`, the same way in every service, with trace IDs on every line.
2. Follow one request across HTTP, gRPC and NATS with a single trace ID.
3. Decide what to log and what never to log, and make Go types hide their own secrets.
4. Measure the four golden signals and the business numbers with Prometheus's Go client, with labels that don't explode.
5. Trace requests with OpenTelemetry, and see them in Jaeger.
6. Write a few alerts that matter, and test that your logs and metrics say what you think.

## What to install
<!-- bite: ba801b88-1127-4d74-b26f-d3b1806b2819 -->

Two programs to look at the signals, in Docker:

```bash
docker run -d --name mamaput-jaeger -p 16686:16686 -p 4317:4317 jaegertracing/all-in-one:latest
docker run -d --name mamaput-prometheus -p 9090:9090 \
  -v "$PWD/deploy/prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus:latest
```

1. **Jaeger** receives traces and shows them: the web page is `http://localhost:16686`, and `4317` is where services send traces, using **OTLP**, OpenTelemetry's standard protocol.
2. **Prometheus** collects metrics by asking each service for them every few seconds, and stores them. Its page is `http://localhost:9090`. It reads `deploy/prometheus.yml`, which step 4 writes.

Lesson 28 moves both into Docker Compose with everything else.

And the Go modules:

```bash
go get github.com/prometheus/client_golang@latest
go get go.opentelemetry.io/otel@latest go.opentelemetry.io/otel/sdk@latest
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc@latest
go get go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp@latest
go get go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc@latest
```

1. **`client_golang`** is Prometheus's own Go library for counting and timing things.
2. **`otel`** and **`otel/sdk`** are OpenTelemetry for Go: the API you call, and the machinery that collects and sends.
3. **`otlptracegrpc`** sends traces over OTLP to Jaeger (or any collector).
4. **`otelhttp`** and **`otelgrpc`** trace HTTP and gRPC for you, in and out.

## Where we stopped
<!-- bite: 164f8c27-3824-4181-b7e7-ffb8e10838c7 -->

It's 2pm. Ada writes to support: "I paid at 12:40 and never got a receipt." Support asks you. Where do you look?

1. The API's logs? Which of the API servers? Each prints lines like `payment settled` with no way to connect them to Ada.
2. The worker's relay? Did it publish? The log says "published 100" every half second, all afternoon.
3. Notifications? Did it get the event? Did it call the API for her contact? Did the breaker open? Did the mailer fail?

Five programs, three log streams, no common thread. You'd be reading timestamps and guessing. And separately: is the API slow today? Is it slower than last week? Is the outbox backing up right now? Nobody knows until a customer complains.

## The kid version
<!-- bite: 6958db62-f9e5-4047-990c-ea7b59eb3d56 -->

Mama Put's business has grown, and Mama can't watch everything herself. So she does three things.

She keeps a **notebook** by the till, and everyone writes a line when something happens: "12:40, order 42, Ada, paid". That's logs.

She puts a **tally board** on the wall: plates sold today, plates left, how long the queue is. She glances at it and knows how the day is going without reading the notebook. That's metrics.

And for the strange cases, she gives each order a **coloured ribbon**. Whoever touches the order (the till, the kitchen, the boy who sends texts) notes the ribbon's colour and the time. When something goes wrong with Ada's order, Mama finds every note with Ada's ribbon colour, in order, from every corner of the shop. That's a trace.

**Where the picture stops working.** In a real shop, people forget to write in the notebook. In our programs, most of the notes are written automatically, by the libraries, as long as we wire them up once. That's most of this lesson.

## Terms used in this lesson
<!-- bite: 8f5f3e98-c102-450c-b0c6-20f3b3025c63 -->

1. **Structured log**: This is a log line made of named fields (`"order_id": 42`), usually as JSON, instead of a sentence. Machines can search and filter it.
2. **Log level**: This is how important a line is: `DEBUG`, `INFO`, `WARN` or `ERROR`. Production usually keeps `INFO` and up.
3. **Metric**: This is a number measured over time. A **counter** only goes up (requests answered); a **gauge** goes up and down (requests in flight); a **histogram** sorts measurements into ranges (request times), so you can work out percentiles.
4. **Label**: This is a name-value pair that splits a metric into series, like `route="GET /v2/menu/{id}"`. Each combination of labels is a separate series stored over time.
5. **Cardinality**: This is how many different series a metric has. A label with a million possible values makes a million series, and takes Prometheus down.
6. **Percentile**: This is "p95 = 120 ms" meaning 95% of requests took 120 ms or less. Averages hide the slow ones; percentiles show them.
7. **Trace**: This is the whole journey of one request, made of **spans**.
8. **Span**: This is one piece of work in a trace, with a start, an end, a name and a parent: "the API handled `POST /webhooks/paystack`", "notifications called `GetContact`".
9. **Context propagation**: This is passing the trace ID from one program to the next, in an HTTP header, gRPC metadata or a message header, so the spans join up into one trace.
10. **Sampling**: This is keeping only some traces (say 10%), because keeping every one costs too much.

## Step 1: structured logs, the same in every service
<!-- bite: 3bff393c-e452-44f9-9692-67dc0ee4693d -->

Since lesson 3 we've logged with `log/slog`, Go's standard structured logger. Now every service makes its logger the same way, in a small shared package. `internal/obs/logs.go`:

```go
package obs

import (
	"context"
	"io"
	"log/slog"

	"go.opentelemetry.io/otel/trace"
)

// traceHandler adds the trace and span IDs from the context to every log line.
type traceHandler struct{ slog.Handler }

func (h traceHandler) Handle(ctx context.Context, r slog.Record) error {
	if sc := trace.SpanContextFromContext(ctx); sc.IsValid() {
		r.AddAttrs(slog.String("trace_id", sc.TraceID().String()), slog.String("span_id", sc.SpanID().String()))
	}
	return h.Handler.Handle(ctx, r)
}

func (h traceHandler) WithAttrs(as []slog.Attr) slog.Handler { return traceHandler{h.Handler.WithAttrs(as)} }
func (h traceHandler) WithGroup(n string) slog.Handler       { return traceHandler{h.Handler.WithGroup(n)} }

// NewLogger writes JSON lines, each naming the service, with trace IDs when there's a trace.
func NewLogger(w io.Writer, service, version string, level slog.Level) *slog.Logger {
	h := slog.NewJSONHandler(w, &slog.HandlerOptions{Level: level})
	return slog.New(traceHandler{h}).With("service", service, "version", version)
}
```

Each service's `run` starts with `logger := obs.NewLogger(stdout, "api", version, level)` (or `"notifications"`, `"worker"`). A line from inside a gRPC handler, from the test:

```json
{"time":"2026-11-22T07:12:17.545+01:00","level":"INFO","msg":"in handler","service":"api","version":"test","trace_id":"88f9a9f56d5913c89277f9d6b4ec0c06","span_id":"daf0376ca5f8fd9a"}
```

1. **A `slog.Handler` wrapper.** slog splits "making a log record" (the `Logger`) from "writing it" (the `Handler`). Our `traceHandler` embeds the JSON handler and changes one method, `Handle`, to add two fields before passing the record on. It's the same embedding trick as lesson 26's `wrappedStream`.
2. **The trace ID comes from the context.** That's why lesson 7 told you to use `InfoContext(ctx, ...)` and `ErrorContext(ctx, ...)`, not `Info(...)`: without the context, the handler has nothing to read the trace from. Every line logged while handling Ada's payment, in any service, now carries the same `trace_id`.
3. **`WithAttrs` and `WithGroup`** must be wrapped too, or a logger made with `logger.With("order_id", 42)` would quietly lose the trace fields. An easy thing to forget; the test catches it.
4. **`service` and `version` on every line.** When five programs' logs land in one place, the first question is always "which one said this?", and the second, during a deploy, is "the old version or the new one?". `version` comes from lesson 29's build, through `-ldflags`.
5. **JSON in production, always.** Lesson 3's text handler is pleasant on a laptop; set `LOG_FORMAT=text` there if you like. A log system can search `trace_id = "88f9..."` in JSON in milliseconds; it can't search sentences.

**Levels.** `INFO` for things that happened (order placed, payment settled, event handled), `WARN` for things that went wrong but were handled (retry, breaker opened, bad event dropped), `ERROR` for things a person should look at (a payment amount mismatch, a panic). `DEBUG` is off in production. `slog.LevelVar` lets you turn it on while running, with an admin route, when you're chasing something.

## Step 2: one ID across every service
<!-- bite: 713ace6e-05e2-4e02-b3cc-9e56c4594866 -->

Lesson 7's request ID tied together the lines of **one request in one program**. Now a single action (Ada's payment) crosses four: the API receives the webhook, the worker relays the event, notifications handles it, and notifications calls the API back over gRPC. We need an ID that travels with the work.

That ID is the **trace ID**, and OpenTelemetry carries it for us in a standard header, `traceparent`:

```text
traceparent: 00-88f9a9f56d5913c89277f9d6b4ec0c06-daf0376ca5f8fd9a-01
             │  └── trace ID (the whole journey)  └── parent span    └── sampled
             └── version
```

`otelhttp` reads it on incoming HTTP requests and writes it on outgoing ones; `otelgrpc` does the same with gRPC metadata. NATS messages are ours to handle (step 5). I tested it end to end: one span started in a test, a gRPC call through `otelgrpc` to a server, and a NATS message's headers; the trace ID was `88f9a9f56d5913c89277f9d6b4ec0c06` in the client, in the server's handler, in the message, and in the log line.

**And the request ID?** Keep it. It's what customers and the phone team see (lesson 7 put it in every problem response), and it's short and simple. Log both on the API's request lines. Support gets "request ID `r-7Gq2...`" from Ada's screenshot, searches the logs for it, finds the `trace_id` on that line, and then searches for the trace ID to see everything, everywhere.

## Step 3: what to log, and what never to log
<!-- bite: c701257c-7f26-40ca-a86c-ede9b17ddf6a -->

**Log** what you'd need to answer a question later:

1. **Every request**, once, at the end: method, route, status, duration, request ID (lesson 3 does this).
2. **Every change that matters**: order placed (ID, customer ID, dish ID, quantity), payment settled (reference, outcome), status changed, event handled (event ID, type), message sent (event ID, kind, customer ID).
3. **Every decision the system made by itself**: retry, breaker state change, event dropped, quote expired, rate limit hit.
4. **Every unexpected error**, in full, at `ERROR`, with the context.

**Never log**:

1. **Secrets**: passwords, tokens (access, refresh, service, MCP), API keys, webhook secrets, the `Authorization` header.
2. **Personal details**: email addresses, phone numbers, names, addresses. Log the customer's **ID**. Support can look the person up when they need to; the logs are read by far more people, kept far longer, and copied to more places than the database.
3. **Card details**, ever. We never see them anyway: Paystack's page takes them.
4. **Whole request or response bodies.** They contain all of the above, sooner or later.

Go can make a type refuse to leak. Any type with a `LogValue() slog.Value` method is logged as whatever that method returns. In `internal/notifications`:

```go
// LogValue keeps contact details out of logs, even if someone logs a Contact by mistake.
func (c Contact) LogValue() slog.Value {
	return slog.GroupValue(
		slog.Bool("has_email", c.Email != ""),
		slog.Bool("has_phone", c.Phone != ""),
	)
}
```

Now `log.Info("got contact", "contact", contact)` writes `"contact":{"has_email":true,"has_phone":false}`, not Ada's email. Give the same method to `auth.User` (just the ID and role) and to anything holding a token. The safe thing becomes the thing that happens without anyone remembering.

## Step 4: metrics with Prometheus
<!-- bite: 7ec9fa19-f50f-412c-9903-1d67bb845cc7 -->

Logs tell you about one event. Metrics tell you about all of them at once: how many orders a minute, how slow, how many errors, how full. Prometheus asks each service for its numbers every 15 seconds and keeps them, so you can graph them and alert on them.

### What to measure

For every service, the **four golden signals**:

1. **Traffic**: how many requests (or events) per second.
2. **Errors**: how many of them failed.
3. **Latency**: how long they took, as percentiles.
4. **Saturation**: how full the things that can fill up are: requests in flight, the database pool, the outbox, the consumer's backlog.

And the **business** numbers, because "the API is up" and "Mama is selling food" aren't the same thing: orders placed, payments settled by outcome, receipts sent.

### HTTP metrics

`internal/obs/metrics.go`:

```go
package obs

import (
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

type HTTPMetrics struct {
	requests *prometheus.CounterVec
	duration *prometheus.HistogramVec
	inFlight prometheus.Gauge
}

func NewHTTPMetrics(reg prometheus.Registerer) *HTTPMetrics {
	f := promauto.With(reg)
	return &HTTPMetrics{
		requests: f.NewCounterVec(prometheus.CounterOpts{
			Name: "http_requests_total", Help: "HTTP requests answered, by route and status code.",
		}, []string{"route", "code"}),
		duration: f.NewHistogramVec(prometheus.HistogramOpts{
			Name: "http_request_duration_seconds", Help: "How long HTTP requests took, by route.",
			Buckets: []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		}, []string{"route"}),
		inFlight: f.NewGauge(prometheus.GaugeOpts{
			Name: "http_requests_in_flight", Help: "HTTP requests being handled right now.",
		}),
	}
}

type rec struct {
	http.ResponseWriter
	status int
}

func (r *rec) WriteHeader(c int)          { r.status = c; r.ResponseWriter.WriteHeader(c) }
func (r *rec) Unwrap() http.ResponseWriter { return r.ResponseWriter }

// Wrap goes directly around a mux, so r.Pattern is the route that matched.
func (m *HTTPMetrics) Wrap(mux http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		m.inFlight.Inc()
		defer m.inFlight.Dec()
		sr := &rec{ResponseWriter: w, status: http.StatusOK}
		mux.ServeHTTP(sr, r)
		route := r.Pattern
		if route == "" {
			route = "unmatched" // never the raw path: every typo would become a new series
		}
		m.requests.WithLabelValues(route, strconv.Itoa(sr.status)).Inc()
		m.duration.WithLabelValues(route).Observe(time.Since(start).Seconds())
	})
}
```

The important part is the **`route` label**, and Go 1.22's router makes it easy. Since Go 1.23, after a `ServeMux` picks a route, it records the **pattern** that matched in `r.Pattern`: `"GET /v2/menu/{id}"`, not `"/v2/menu/7"`. That's exactly the label we want: one series per route, however many dishes there are. A label of `r.URL.Path` would make a new series for every dish ID, every order ID and every bot trying `/wp-admin.php`, and Prometheus would eventually fall over. **Labels must come from a small, fixed set.**

There's a Go catch, and I only found it by testing. The mux writes `r.Pattern` onto the **`*http.Request` it was given**. Our middleware chain (request ID, `Authenticate` and others) makes copies of the request with `r.WithContext`, so a metrics middleware at the top of the chain holds the original, which the mux never touches, and sees an empty pattern. The test showed it plainly:

```text
/v2/menu/7: outermost="" at-mux="GET /v2/menu/{id}"
/v1/menu/7: outermost="" at-mux="/v1/"
```

So `Wrap` goes **directly around the mux**, inside the chain, where it holds the very request the mux fills in. In `app.New`:

```go
root.Handle("/", httpx.Chain(d.HTTPMetrics.Wrap(httpx.MuxProblems(api)),
	httpx.RequestID, httpx.LogRequests(d.Logger), httpx.RecoverPanic,
	httpx.SecurityHeaders, httpx.CORS(d.CORS),
	httpx.RateLimit(d.GeneralLimit, d.ClientIP), auth.Authenticate(d.Tokens)))
```

(and the same around the webhook and MCP chains' muxes). The second line of the test shows a smaller catch: all of v1 is one route, `/v1/`, because lesson 10 mounted v1's mux behind `http.StripPrefix`, which makes yet another copy. For a frozen version on its way out, one series is fine.

`rec` is lesson 3's status recorder again, with `Unwrap` so lesson 20's streams can still flush through it. (Lesson 20's streams also count as "in flight" for hours; give `/v2/kitchen/orders/stream` its own gauge, from `hub.Connected()`, and leave it out of the duration histogram, or its p95 will read "6 hours".)

### Business metrics, and saturation

Counters where things happen, registered on the same registry:

```go
ordersPlaced := promauto.With(reg).NewCounterVec(prometheus.CounterOpts{
	Name: "mamaput_orders_placed_total", Help: "Orders placed, by where they came from.",
}, []string{"via"}) // app, graphql, mcp: three values, fixed

paymentsSettled := promauto.With(reg).NewCounterVec(prometheus.CounterOpts{
	Name: "mamaput_payments_settled_total", Help: "Payments settled, by outcome.",
}, []string{"outcome"}) // paid, failed, mismatch, already-settled, ...
```

The orders service calls `ordersPlaced.WithLabelValues(string(in.Source.Via)).Inc()` after a successful place; `Settle` counts each outcome. Lesson 17's `Mismatch` outcome gets its own alert in step 6: it should never happen.

Some numbers are cheapest to measure when Prometheus asks. A **`GaugeFunc`** calls your function at scrape time:

```go
promauto.With(reg).NewGaugeFunc(prometheus.GaugeOpts{
	Name: "mamaput_outbox_oldest_unpublished_seconds",
	Help: "How long the oldest unpublished outbox event has waited.",
}, func() float64 {
	ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()
	var age float64
	pool.QueryRow(ctx, `SELECT COALESCE(EXTRACT(EPOCH FROM now() - min(occurred_at)), 0)
	                      FROM outbox WHERE published_at IS NULL`).Scan(&age)
	return age
})
```

It uses lesson 25's partial index, so it's a millisecond's work every 15 seconds. **This one number tells you whether the whole event system is healthy**: if it's above a few seconds, the relay is stuck, NATS is down, or the worker isn't running, and no receipt, partner webhook or kitchen update is going anywhere.

More saturation numbers worth having:

1. **The database pool**: pgx's `pool.Stat()` has `AcquiredConns()`, `MaxConns()` and `EmptyAcquireCount()` (how often a query had to wait for a connection). Three `GaugeFunc`s.
2. **Kitchen streams**: `hub.Connected()` from lesson 20, as a `GaugeFunc`.
3. **Breakers**: lesson 26's `OnStateChange` sets a gauge, `mamaput_breaker_open{breaker="customers"}`, to 1 when open and 0 otherwise.
4. **Consumers**: notifications counts `mamaput_events_handled_total{type, result}` (`ok`, `retry`, `dropped`), and the NATS server itself reports each consumer's backlog (its monitoring port, 8222, scraped with the official NATS exporter).

The Go client also gives you, for free, the Go runtime's own numbers (goroutines, memory, garbage collection) with `collectors.NewGoCollector()`, and the process's (CPU, open files) with `collectors.NewProcessCollector(...)`. Register both. A goroutine count that only ever goes up is a leak, and this is how you'll spot it.

### Serving `/metrics`

```go
reg := prometheus.NewRegistry()
reg.MustRegister(collectors.NewGoCollector(), collectors.NewProcessCollector(collectors.ProcessCollectorOpts{}))

admin := http.NewServeMux()
admin.Handle("GET /metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{}))
go serveAdmin(ctx, getenv("ADMIN_ADDR"), admin) // ":9100", with lesson 1's timeouts
```

1. **Our own registry**, not the global default one, so tests can make a fresh one each time and nothing registers metrics behind our back.
2. **A separate port, 9100**, on its own small server. The public proxy (lesson 28) never forwards to it. Metrics reveal a lot (route names, traffic, error rates) and nobody outside needs them. Lesson 28's health checks will live here too.

`deploy/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: api
    static_configs: [{ targets: ["host.docker.internal:9100"] }]
  - job_name: worker
    static_configs: [{ targets: ["host.docker.internal:9101"] }]
  - job_name: notifications
    static_configs: [{ targets: ["host.docker.internal:9102"] }]
```

(`host.docker.internal` is how a container reaches your laptop. On Linux, add `--add-host=host.docker.internal:host-gateway` to the `docker run`. In lesson 28 these become service names.)

Open `http://localhost:9090`, and try a few queries in its **PromQL** language:

```text
sum by (route) (rate(http_requests_total[5m]))                                      # requests per second, by route
sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) # share of 5xx answers
histogram_quantile(0.95, sum by (le, route) (rate(http_request_duration_seconds_bucket[5m])))  # p95 by route
mamaput_outbox_oldest_unpublished_seconds
```

`rate(...[5m])` turns an ever-growing counter into "per second, over the last 5 minutes". `histogram_quantile` works out a percentile from the histogram's buckets, which is why the buckets matter: choose them around the times you care about (5 ms to 10 s for us).

## Step 5: traces with OpenTelemetry
<!-- bite: 348abab5-a39f-47ac-a0f8-f8754c56c899 -->

Logs say *what*, metrics say *how much*; a trace shows *where the time went*, across every service, for one request. `internal/obs/tracing.go`:

```go
// Package obs sets up logs, metrics and traces the same way in every service.
package obs

import (
	"context"
	"errors"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

// SetupTracing sends this service's traces to an OpenTelemetry collector (or Jaeger) at endpoint.
// With no endpoint, tracing still works inside the process (IDs in logs), and nothing is sent.
// The returned function flushes waiting spans; call it on shutdown.
func SetupTracing(ctx context.Context, service, version, endpoint string, sampleRatio float64) (func(context.Context) error, error) {
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(propagation.TraceContext{}, propagation.Baggage{}))

	res, err := resource.Merge(resource.Default(), resource.NewWithAttributes(semconv.SchemaURL,
		semconv.ServiceName(service), semconv.ServiceVersion(version)))
	if err != nil && !errors.Is(err, resource.ErrSchemaURLConflict) {
		return nil, err
	}
	opts := []sdktrace.TracerProviderOption{
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(sampleRatio))),
	}
	if endpoint != "" {
		exp, err := otlptracegrpc.New(ctx, otlptracegrpc.WithEndpoint(endpoint), otlptracegrpc.WithInsecure())
		if err != nil {
			return nil, err
		}
		opts = append(opts, sdktrace.WithBatcher(exp))
	}
	tp := sdktrace.NewTracerProvider(opts...)
	otel.SetTracerProvider(tp)
	return tp.Shutdown, nil
}
```

In each `run`, near the top:

```go
shutdownTracing, err := obs.SetupTracing(ctx, "api", version, getenv("OTEL_ENDPOINT"), sampleRatio)
if err != nil {
	return err
}
defer shutdownTracing(context.WithoutCancel(ctx))
```

1. **The propagator** decides how trace IDs travel: `TraceContext` is the W3C `traceparent` header from step 2. Set it once, globally, and every instrumented library uses it.
2. **The resource** says who's sending: `service.name` is how Jaeger groups spans by service.
3. **The sampler.** `TraceIDRatioBased(0.1)` keeps 10% of traces; `1.0` keeps them all (development). `ParentBased` means "if the caller's trace was kept, keep mine too", so a trace is never kept in one service and dropped in the next. In production, 10% of Mama Put's traffic is plenty to see where time goes.
4. **`WithBatcher`** sends spans in batches in the background, so tracing never slows a request down by waiting on Jaeger. The shutdown function sends the last batch: without it, the spans from the final seconds before a restart are lost. It gets `context.WithoutCancel` because `ctx` is already cancelled by the time it runs (lesson 15's trick).
5. **No endpoint, no sending**, but spans and trace IDs still exist, so logs still carry `trace_id`. Tests and laptops don't need Jaeger running.

### HTTP in, HTTP out

Wrap the whole root handler in `run`:

```go
srv := &http.Server{
	Addr:    getenv("ADDR"),
	Handler: otelhttp.NewHandler(app.New(deps), "http.server"),
	// ... lesson 1's timeouts
}
```

`otelhttp.NewHandler` starts a span for every request, continuing the caller's trace if there's a `traceparent` header, and puts the span in `r.Context()`, so everything below (logs, gRPC calls, queries) joins it. It starts before the mux, so it can't know the route; `HTTPMetrics.Wrap`, sitting at the mux, renames the span once it does, with one more line after `mux.ServeHTTP`:

```go
trace.SpanFromContext(r.Context()).SetName(r.Method + " " + route)
```

Now spans are named `GET /v2/menu/{id}`, the same as the metrics' labels.

For calls out, give lesson 17's Paystack client a traced transport:

```go
client := &http.Client{Timeout: 10 * time.Second, Transport: otelhttp.NewTransport(http.DefaultTransport)}
```

Every call to Paystack becomes a span, with its duration and status, inside whatever request made it. When checkout is slow, the trace shows whether it was us or them. (The `traceparent` header goes to Paystack too; it's harmless, and some providers even use it.)

### gRPC

One option on each side, lesson 22's server and lesson 25's client:

```go
grpc.NewServer(grpc.StatsHandler(otelgrpc.NewServerHandler()), /* interceptors as before */)
grpc.NewClient(addr, grpc.WithStatsHandler(otelgrpc.NewClientHandler()), /* credentials as before */)
```

A **stats handler** sees every call's start and end, below the interceptors, so it measures the whole call. The test's spans, both sides of one call in one trace:

```text
mamaput.menu.v1.MenuService/GetDish kind=server
mamaput.menu.v1.MenuService/GetDish kind=client
handle order.paid kind=internal
```

### NATS, through the outbox

NATS messages have headers, like HTTP, so the trace can ride in them. But our events don't go straight from the request to NATS: they wait in the outbox, and the relay sends them later, from another program. By then the request's trace is long gone. So the trace context is saved **with the event**, when it's written. `migrations/017_outbox_trace.sql`:

```sql
ALTER TABLE outbox ADD COLUMN trace_parent text;
```

In `outbox.Add`, capture it from the context:

```go
carrier := propagation.MapCarrier{}
otel.GetTextMapPropagator().Inject(ctx, carrier)
_, err = tx.Exec(ctx, "INSERT INTO outbox (type, version, data, trace_parent) VALUES ($1, $2, $3, NULLIF($4, ''))",
	eventType, version, b, carrier.Get("traceparent"))
```

The relay puts it in the message's headers, publishing with `PublishMsg` instead of `Publish`:

```go
msg := nats.NewMsg(events.Subject(e.Type))
msg.Data = b
if traceParent != "" {
	msg.Header.Set("traceparent", traceParent)
}
_, err := r.JS.PublishMsg(ctx, msg, jetstream.WithMsgID(e.ID))
```

and notifications' consumer picks it up and starts its span as a child:

```go
ctx := otel.GetTextMapPropagator().Extract(ctx, propagation.HeaderCarrier(http.Header(msg.Headers())))
ctx, span := otel.Tracer("notifications").Start(ctx, "handle "+e.Type,
	trace.WithSpanKind(trace.SpanKindConsumer),
	trace.WithAttributes(attribute.String("event.id", e.ID)))
defer span.End()
```

`nats.Header` is a `map[string][]string`, the same shape as `http.Header`, so it converts directly and `HeaderCarrier` reads and writes it. (Because `HeaderCarrier` uses `http.Header`'s rules, it writes the key as `Traceparent`; reading it back the same way works either way.)

Now open Jaeger, pick the `api` service, and find Ada's payment. One trace, in order: the API receiving Paystack's webhook and settling, then (after a short gap while the event waited for the relay) notifications handling `order.paid`, calling `GetContact` (a span in notifications *and* its twin in the API), calling `GetDish`, and sending. The gap is the outbox's wait, measured. If the receipt never came, the trace stops where it went wrong, and the log lines with that `trace_id` say why.

**Databases.** For a span per query, add `github.com/exaring/otelpgx` as pgx's tracer (`config.ConnConfig.Tracer = otelpgx.NewTracer()`). Useful when you're hunting a slow query; leave it off until then, because a span per query is a lot of spans.

**Your own spans** for work worth seeing: `ctx, span := otel.Tracer("payments").Start(ctx, "settle")` and `defer span.End()`. On failure, `span.RecordError(err)` and `span.SetStatus(codes.Error, "...")`. Don't wrap every function; wrap the steps someone would ask about.

## Step 6: alerts that matter
<!-- bite: d50ee15c-b4e2-42fe-92c9-e939b3637684 -->

An alert wakes someone up, so each one must mean "a person needs to act, now". Alert on **symptoms customers feel**, not on every cause:

```yaml
# deploy/alerts.yml
groups:
  - name: mama-put
    rules:
      - alert: ManyServerErrors
        expr: sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.02
        for: 5m
        annotations: { summary: "More than 2% of API requests are failing" }

      - alert: SlowAPI
        expr: histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route!~".*stream.*"}[5m]))) > 1
        for: 10m
        annotations: { summary: "p95 latency over 1 second for 10 minutes" }

      - alert: EventsStuck
        expr: mamaput_outbox_oldest_unpublished_seconds > 60
        for: 2m
        annotations: { summary: "Events have waited over a minute: receipts, partner webhooks and the kitchen are behind" }

      - alert: PaymentMismatch
        expr: increase(mamaput_payments_settled_total{outcome="mismatch"}[10m]) > 0
        annotations: { summary: "A payment amount didn't match its order. Look now." }

      - alert: NoOrders
        expr: sum(increase(mamaput_orders_placed_total[30m])) == 0 and on() hour() >= 7 and on() hour() < 20
        annotations: { summary: "No orders for 30 minutes during opening hours" }
```

1. **`for: 5m`** means the condition must hold for 5 minutes before anyone is woken. One bad scrape isn't an emergency.
2. **`EventsStuck`** covers a whole family of causes (NATS down, relay stuck, worker crashed) with one symptom.
3. **`PaymentMismatch`** has no `for`: one is too many.
4. **`NoOrders`** catches the failures every other alert misses: a broken deploy where everything answers 200 but nobody can actually order. (`hour()` is in UTC, which Prometheus always uses; Lagos is UTC+1, so this is 8am to 9pm there.)

The breaker opening, a retry, a dropped event: those are `WARN` logs and dashboard graphs, not alerts. If notifications' breaker is open for long, `EventsStuck` won't fire (the outbox is fine), but receipts are late; add a gentler alert, sent to a chat channel instead of a phone, for `mamaput_breaker_open == 1` for 10 minutes.

Prometheus decides when an alert fires; a companion program, **Alertmanager**, decides who hears about it (email, chat, phone) and stops the same alert arriving fifty times. Lesson 29's server runs it beside Prometheus.

## Step 7: testing what you log and measure
<!-- bite: b88b03d9-4152-47d3-8010-51ef237c0b25 -->

Logs, metrics and traces are output like any other, and they break like any other.

1. **Logs**: give the logger a `bytes.Buffer` as its writer, do the thing, and decode the JSON lines. Check a settled payment logs `reference` and `outcome`; check a log line made inside a span has `trace_id`; check a logged `Contact` shows `has_email` and **not** the address.
2. **Metrics**: a fresh `prometheus.NewRegistry()` per test, and `testutil` from `client_golang`. The test for `Wrap`:

```go
func TestHTTPMetricsUseTheRoute(t *testing.T) {
	reg := prometheus.NewRegistry()
	m := NewHTTPMetrics(reg)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /v2/menu/{id}", func(w http.ResponseWriter, r *http.Request) {
		if r.PathValue("id") == "99" {
			w.WriteHeader(http.StatusNotFound)
		}
	})
	h := m.Wrap(mux)
	for _, p := range []string{"/v2/menu/1", "/v2/menu/2", "/v2/menu/99", "/wp-admin.php"} {
		h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", p, nil))
	}

	err := testutil.GatherAndCompare(reg, strings.NewReader(`
# HELP http_requests_total HTTP requests answered, by route and status code.
# TYPE http_requests_total counter
http_requests_total{code="200",route="GET /v2/menu/{id}"} 2
http_requests_total{code="404",route="GET /v2/menu/{id}"} 1
http_requests_total{code="404",route="unmatched"} 1
`), "http_requests_total")
	if err != nil {
		t.Fatal(err)
	}
}
```

Four requests, three series, and no `/v2/menu/1` or `/wp-admin.php` in sight. That's the cardinality rule, tested.

3. **Traces**: `tracetest.NewInMemoryExporter()` from the OpenTelemetry SDK, with `sdktrace.WithSyncer(exp)` so spans arrive at once. Make a gRPC call through `bufconn` with both stats handlers and check the client's and server's spans share a trace ID; publish through the relay with a span in the context and check the message's `traceparent` header has that trace ID. (These ran while writing this lesson.)

## The Go in this lesson
<!-- bite: 62c5d744-3a60-425c-ab3d-e869ef88531c -->

1. **Wrapping a `slog.Handler`**: Embed it and replace `Handle` (and `WithAttrs`, `WithGroup`) to add fields to every record.
2. **`LogValue() slog.Value`**: The `slog.LogValuer` interface. A type with it decides how it's logged, so secrets can't leak by accident.
3. **`*Context` logging, `log.InfoContext(ctx, ...)`**: Gives the handler the context, which is where the trace lives.
4. **`r.Pattern`** (Go 1.23): The route pattern a `ServeMux` matched, set on the request it handled. Copies made with `r.WithContext` don't see it.
5. **`promauto.With(reg)`**: Makes metrics already registered on your own registry. `CounterVec`, `HistogramVec` and `Gauge` are the shapes; `WithLabelValues` picks a series.
6. **`NewGaugeFunc`**: A gauge whose value comes from your function each time Prometheus asks.
7. **`promhttp.HandlerFor(reg, ...)`**: An `http.Handler` that serves a registry's metrics in Prometheus's text format.
8. **`otel.SetTracerProvider` and `otel.SetTextMapPropagator`**: Set once in `run`; every instrumented library uses them.
9. **`otelhttp.NewHandler`, `otelhttp.NewTransport`**: Spans for HTTP in and out, with the trace in the context and the `traceparent` header.
10. **`grpc.StatsHandler(otelgrpc.NewServerHandler())`**: Spans for every gRPC call, on each side.
11. **`propagation.MapCarrier` and `propagation.HeaderCarrier`**: Somewhere to write and read trace headers: a map for the outbox, `http.Header` (and so `nats.Header`) for messages.
12. **A type conversion between same-shaped maps, `http.Header(msg.Headers())`**: Both are `map[string][]string`, so Go converts one to the other directly.
13. **`testutil.GatherAndCompare`** and **`tracetest.NewInMemoryExporter`**: Check exactly which metrics and spans your code produced.

## Your project so far
<!-- bite: 6062e113-c3f0-4cf9-acf9-e6b93c598af7 -->

```text
mama-put/
├── go.mod                         ← client_golang, otel, otel/sdk, otlptracegrpc, otelhttp, otelgrpc
├── deploy/
│   ├── prometheus.yml             ← NEW: scrape api, worker and notifications every 15 s
│   └── alerts.yml                 ← NEW: errors, latency, events stuck, payment mismatch, no orders
├── migrations/
│   └── 017_outbox_trace.sql       ← NEW: outbox.trace_parent
├── cmd/
│   ├── api/main.go                ← obs.NewLogger, SetupTracing, otelhttp.NewHandler, admin server with /metrics
│   ├── worker/main.go             ← the same, on :9101
│   └── notifications/main.go      ← the same, on :9102; otelgrpc client handler
└── internal/
    ├── obs/                       ← NEW: shared by every service
    │   ├── logs.go                ← NewLogger: JSON, service and version, trace_id and span_id
    │   ├── tracing.go             ← SetupTracing: propagator, resource, sampler, batcher, shutdown
    │   ├── metrics.go             ← HTTPMetrics.Wrap at the mux, labelled by r.Pattern; renames the span
    │   └── obs_test.go            ← trace fields in logs, route labels, gRPC and NATS propagation
    ├── app/app.go                 ← HTTPMetrics.Wrap around each mux
    ├── outbox/outbox.go           ← Add saves traceparent; the relay publishes it as a header
    ├── orders/ · payments/        ← business counters; outbox age, pool and stream gauges
    ├── grpcapi/server.go          ← otelgrpc server handler
    └── notifications/
        ├── consumer.go            ← a consumer span from the message's traceparent; events_handled_total
        └── customers.go           ← Contact.LogValue hides the details
```

## Common mistakes
<!-- bite: 8dea43b3-6dd2-4322-b379-5fc31ff3ec7b -->

1. **Logging sentences.** Nobody can search them. Named fields, as JSON.
2. **`log.Info` instead of `log.InfoContext`.** The line loses its trace ID.
3. **Logging personal details or tokens.** Logs are read by many and kept long. IDs only; `LogValue` for anything sensitive.
4. **A label from the raw path, a user ID or an email.** Cardinality explodes. Labels come from small fixed sets: route patterns, status codes, outcomes.
5. **Metrics middleware outside the `r.WithContext` copies.** `r.Pattern` is empty. Wrap the mux itself.
6. **Averages instead of percentiles.** The average hides the customers who waited 8 seconds.
7. **`/metrics` on the public port.** It tells strangers a lot. A separate admin port.
8. **No tracer shutdown.** The last spans before every restart are lost.
9. **Losing the trace across the outbox.** Save `traceparent` with the event.
10. **Sampling each service separately.** Half-kept traces are useless. `ParentBased`.
11. **Alerts on causes, and too many of them.** People learn to ignore them. Alert on what customers feel, with `for:`.
12. **No test for the logs and metrics.** They break silently, and you find out during the incident.

## Check your understanding
<!-- bite: 5f214173-9114-4779-a2ff-017db272c711 -->

1. Ada never got her receipt. Walk through how you'd find out why, starting from the request ID on her payment screen.
2. Why is `route="GET /v2/menu/{id}"` a good label, and `path="/v2/menu/7"` a dangerous one?
3. A metrics middleware placed first in the chain reports every request as `unmatched`. Why, and where should it go?
4. Why does the outbox save `traceparent`, when `otelhttp` and `otelgrpc` carry it automatically?
5. Which single metric would tell you that receipts, partner webhooks and kitchen updates are all behind, and why does it catch so many different causes?
6. Why `ParentBased(TraceIDRatioBased(0.1))`, and not just `TraceIDRatioBased(0.1)` in each service?

<details>
<summary>Answers, after your attempt</summary>

1. Search the API's logs for the request ID; that line has the `trace_id`. Open the trace in Jaeger (or search all logs for the `trace_id`): it shows the webhook being settled, then whether notifications handled `order.paid`, whether `GetContact` and `GetDish` worked, and whether the send happened. Wherever the trace stops is where it went wrong, and the log lines with that `trace_id` from that service give the error. If there's no notifications part at all, check `mamaput_outbox_oldest_unpublished_seconds`: the event may still be waiting.
2. A route pattern comes from a small, fixed set (one per route in the code), so it makes a handful of series. A raw path has a new value for every dish ID, order ID and bot's guess, so each becomes a new series stored forever, until Prometheus runs out of memory.
3. The mux writes `r.Pattern` onto the request it was given, and the middleware below the first one made copies with `r.WithContext`, so the first middleware's request is never filled in. Put `Wrap` directly around the mux, inside the chain.
4. Because the event leaves the request behind: it waits in a table and is published later by another program, the relay, where the original request's context no longer exists. Saving `traceparent` with the event lets the relay put it on the message, so notifications can continue the same trace.
5. `mamaput_outbox_oldest_unpublished_seconds`. Every one of those depends on events leaving the outbox, so NATS being down, the relay being stuck or the worker not running all show up as one number climbing.
6. With `ParentBased`, a service follows its caller's decision: if the trace was kept upstream, it's kept here too, so every trace is either whole or not kept at all. Sampling 10% separately in each service would keep a different 10% in each, leaving traces with missing pieces.

</details>

## Practice
<!-- bite: 6e246705-06d6-4753-ab8e-e3dd2d644d29 -->

1. Write `internal/obs` and its tests: trace fields in logs (including through `logger.With`), the route-label test above, and gRPC propagation with `tracetest`.
2. Add `LogValue` to `notifications.Contact` and `auth.User`, and a test that a logged user shows only the ID and role.
3. Add the business counters and the gauges (outbox age, pool, kitchen streams, breakers), and look at each in Prometheus while you place and pay for orders.
4. Save `traceparent` in the outbox, publish it as a header, continue it in notifications, and find one payment's whole trace in Jaeger, across three services.
5. Load `deploy/alerts.yml` into Prometheus (`rule_files:` in `prometheus.yml`), stop the worker, and watch `EventsStuck` go from pending to firing on Prometheus's Alerts page.
6. Make a small Prometheus dashboard (or Grafana, if you like) with the four golden signals for the API.

**Done when** every log line is JSON with `service`, `version` and, inside a request or event, `trace_id`; no log line contains an email address, phone number or token; `/metrics` on the admin port shows `http_requests_total` labelled by route pattern; one payment shows as a single trace across the API and notifications in Jaeger; stopping the worker makes `EventsStuck` fire; and `make test` passes.

## Before moving on
<!-- bite: 86d18a73-159f-4ee9-a60a-f94833bed8d9 -->

Mama Put can see itself now. Every service writes the same JSON lines with the same trace ID; Prometheus counts and times what matters, with labels that stay small; a trace follows Ada's payment from Paystack's webhook through the outbox and NATS into notifications and back to the API; and five alerts say "act now" only when customers would notice.

All of it, so far, runs on your laptop as separate `go run` commands and `docker run`s, with settings scattered across environment variables you have to remember. Production needs it packaged and predictable: settings checked when a program starts, health checks a machine can ask, programs that stop politely, small images, and the whole system started with one command. That's the next lesson.

## Related
<!-- bite: a29019c8-29cf-4159-bff4-843a7a7eb677 -->

- [[backend/frameworks/net-http/28-production-config-and-docker|Next: Production Config and Docker]]
- [[backend/frameworks/express/27-observability|The same lesson in Express]] — pino, prom-client and the Node OpenTelemetry SDK
- [[backend/frameworks/net-http/03-middleware|Middleware]] — the first logger and the status recorder
- [[backend/frameworks/net-http/07-errors|Errors and Structured Responses]] — request IDs in the context
- [[backend/frameworks/net-http/25-splitting-out-a-microservice|Splitting Out a Microservice]] — the outbox the trace now passes through

## About this lesson
<!-- bite: c276e078-cbdf-43ba-8ce7-82232a0a9072 -->

**Level:** Advanced. Lesson 27 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`r.Pattern` needs 1.23), Prometheus's `client_golang`, and OpenTelemetry for Go with the `otelhttp` and `otelgrpc` instrumentation. Covers logs, metrics and traces and what each answers, a shared JSON `slog` logger with trace IDs through a wrapped handler, request IDs and trace IDs together, what never to log and `LogValue` for types that hide their own secrets, the four golden signals and business metrics, route labels from `r.Pattern` and why the middleware must wrap the mux, cardinality, gauges computed at scrape time, the Go and process collectors, an admin port for `/metrics`, PromQL basics, OpenTelemetry setup with a propagator, resource, parent-based sampling and a batching OTLP exporter, tracing HTTP in and out, gRPC with stats handlers, carrying the trace through the outbox and NATS headers, alerts on symptoms with Alertmanager, and testing logs, metrics and traces.
