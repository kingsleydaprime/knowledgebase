---
id: d6aec3ff-9724-44a7-b504-b8d9bbb42914
---

# Observability 3: Metrics and Alerts

**A metric is a number the system keeps about itself over time, like requests answered or orders placed, and an alert is a rule that asks a person to look when those numbers say customers are being hurt.**

## Before you start
<!-- bite: c3348ffa-376c-4f21-aaec-3b312007b64a -->

You should have finished [[backend/frameworks/axum/36-observability-2|part 2]]: logs and traces answer "what happened to Ada's payment?". This part answers "how is the system doing right now?", without anyone asking about one payment.

After this part you will be able to:

1. Say what to measure in every service: the four golden signals, and the business's own numbers.
2. Record counters, gauges and histograms with the `metrics` crate, and serve them for Prometheus.
3. Label HTTP metrics by route, never by path, and explain why that matters.
4. Run Prometheus against all three programs and ask it questions.
5. Write alerts on what customers feel, check them with `promtool`, and test metrics.

## What to install
<!-- bite: 25c743ff-0f79-4e71-ac72-5fc0718afd14 -->

Two crates in `telemetry`, and one in each crate that records numbers:

```bash
cargo add -p telemetry metrics@0.24
cargo add -p telemetry metrics-exporter-prometheus@0.18 --no-default-features --features http-listener
cargo add metrics@0.24                       # the API
cargo add -p contracts metrics@0.24
cargo add -p notifications metrics@0.24
```

1. **metrics** is a *facade*, like `tracing` is for logs: code says `metrics::counter!("…").increment(1)`, and doesn't know or care where the number goes.
2. **metrics-exporter-prometheus** keeps the numbers and serves them in Prometheus's text format. `http-listener` lets it serve `/metrics` on an address of its own.

And **Prometheus**, which reads every program's numbers every few seconds, keeps them, answers questions, and fires alerts. In Docker, in step 5.

## Where we stopped
<!-- bite: a1227909-6fc0-4b1c-b34e-008fd77239ca -->

Ada's question gets answered in seconds now. But nobody asked "is the API slow today?", "is the outbox backing up?", "has anyone ordered in the last half hour?". Those need numbers kept all the time, not lines searched afterwards.

## Terms used in this part
<!-- bite: f249b720-a9d0-4808-bd88-cb9e621446b6 -->

1. **Metric**: This is a number measured over time. A **counter** only goes up (requests answered); a **gauge** goes up and down (requests in flight); a **histogram** sorts measurements into ranges (request times), so you can work out percentiles.
2. **Label**: This is a name-value pair that splits a metric into series, like `route="/v2/menu/{id}"`. Each combination of labels is a separate series, stored over time.
3. **Cardinality**: This is how many different series a metric has. A label with a million possible values makes a million series, and takes Prometheus down.
4. **Percentile**: This is "p95 = 120 ms" meaning 95% of requests took 120 ms or less. Averages hide the slow ones; percentiles show them.
5. **Scrape**: This is Prometheus fetching a program's `/metrics` page, every 15 seconds here.

## Step 1: what to measure
<!-- bite: 8f237e72-4578-46ba-b803-a4ea9026647d -->

For every service, the **four golden signals**:

1. **Traffic**: how many requests (or events) per second.
2. **Errors**: how many of them failed.
3. **Latency**: how long they took, as percentiles.
4. **Saturation**: how full the things that can fill up are: requests in flight, the outbox's backlog, a breaker that's open.

And the **business** numbers, because "the API is up" and "Mama is selling food" aren't the same thing: orders placed, payments settled by outcome, receipts sent.

## Step 2: keeping and serving the numbers
<!-- bite: a115dc76-da29-4f21-8ee8-fc04ed2a5125 -->

In `telemetry/src/lib.rs`:

```rust
/// Serves `/metrics` on `addr`, for Prometheus to read. Keep `addr` private (127.0.0.1, or the internal
/// network): metrics are for us, not for the internet. Call it inside the Tokio runtime.
pub fn serve_metrics(addr: SocketAddr) -> Result<(), Error> {
    metrics_recorder().with_http_listener(addr).install()?;
    Ok(())
}

/// How every program's metrics are kept: anything measured in seconds is sorted into these buckets,
/// so Prometheus can work out percentiles across every copy of a program.
pub fn metrics_recorder() -> PrometheusBuilder {
    const BUCKETS: [f64; 11] = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0];
    PrometheusBuilder::new().set_buckets_for_metric(Matcher::Suffix("_seconds".into()), &BUCKETS).expect("the buckets aren't empty")
}
```

and in each program's `main`, after `telemetry::init`:

```rust
// /metrics, for Prometheus, on a private address: never the public port.
let metrics_addr = std::env::var("METRICS_ADDR").unwrap_or_else(|_| "127.0.0.1:9100".into());
telemetry::serve_metrics(metrics_addr.parse()?)?;
```

(9101 for the worker, 9102 for notifications.)

1. **A separate, private address.** Metrics say a lot about the business (orders per hour, payment failures). They're for us. The public API on 8080 doesn't serve them; lesson 38 puts these ports on the internal network only.
2. **Buckets for anything in seconds.** Without them, the exporter sends a *summary*: percentiles worked out inside each copy of a program, which can't be added up across copies. With buckets, Prometheus gets a histogram and works out percentiles across every copy itself. The buckets run from 5 ms to 10 seconds, the range where a web request lives.
3. **One recorder per program**, installed once. After that, any `metrics::counter!` anywhere in that program reaches it.

## Step 3: HTTP metrics, by route
<!-- bite: 80465d07-9db3-4341-b379-1e76b212e71f -->

`src/http/request_metrics.rs`:

```rust
/// Middleware: `http_requests_total`, `http_request_duration_seconds` and `http_requests_in_flight`.
pub async fn record_metrics(req: Request, next: Next) -> Response {
    // The route's pattern, from the router. A path no route matched is "unmatched": otherwise every
    // scanner trying `/wp-admin.php` would make a new series, for ever.
    let route = req.extensions().get::<MatchedPath>().map(|p| p.as_str().to_owned()).unwrap_or_else(|| "unmatched".into());
    let method = req.method().to_string();
    let started = Instant::now();
    let in_flight = metrics::gauge!("http_requests_in_flight");
    in_flight.increment(1.0);
    let response = next.run(req).await;
    in_flight.decrement(1.0);

    let labels = [("method", method), ("route", route), ("code", response.status().as_u16().to_string())];
    metrics::counter!("http_requests_total", &labels).increment(1);
    metrics::histogram!("http_request_duration_seconds", &labels).record(started.elapsed().as_secs_f64());
    response
}
```

added in `lib.rs` just inside the request log, so timeouts and panics further in are counted too:

```rust
        // Counted and timed by route, whatever happens further in (timeouts and panics included).
        .layer(middleware::from_fn(http::record_metrics))
```

**The route, never the path.** `MatchedPath` is the pattern the router matched: `/v2/menu/{id}`, not `/v2/menu/4`. If the label were the real path, every dish id would be a new series, every order id another, and every scanner trying `/wp-admin.php`, `/.env` and ten thousand other paths yet more. That's cardinality, and it's the most common way to break Prometheus. A path no route matched is just `unmatched`.

Axum adds `MatchedPath` to the request when it routes it, and layers added with `Router::layer` run after routing, which is why our middleware can read it.

Streams (lesson 20's kitchen events, the WebSocket) stay open for minutes, so their "duration" is huge and means nothing. The alerts in step 6 leave them out of the latency rule.

## Step 4: the business's own numbers
<!-- bite: d93c0ada-f16c-4728-9a19-08957f885723 -->

One line each, where the thing happens. Orders, in `OrderService::place`:

```rust
        // Is Mama selling food? "The API is up" doesn't answer that; this does.
        metrics::counter!("mamaput_orders_placed_total", "via" => new.source.via()).increment(1);
```

Payments, in `PaymentService::settle`, by outcome:

```rust
    pub async fn settle(&self, reference: &str, seen: Seen) -> Result<Outcome, PaymentError> {
        let outcome = self.decide(reference, seen).await?;
        // How payments are going, by outcome: "mismatch" or "order_was_already_paid" need a person.
        metrics::counter!("mamaput_payments_settled_total", "outcome" => outcome.as_str()).increment(1);
        Ok(outcome)
    }
```

The outbox's backlog, measured by the relay on every turn (a gauge: it goes up and down):

```rust
    /// How long the oldest unpublished event has waited, in seconds (0 when none are waiting).
    /// If this grows, receipts, partner webhooks and everything else that reads events are behind.
    pub async fn oldest_waiting(&self) -> Result<f64, sqlx::Error> {
        let seconds = sqlx::query_scalar!(
            r#"SELECT coalesce(extract(epoch FROM now() - min(occurred_at)), 0)::float8 AS "seconds!" FROM outbox WHERE published_at IS NULL"#
        )
        .fetch_one(&self.pool)
        .await?;
        Ok(seconds)
    }
```

Every event a reader handles, and how it went, in `contracts/src/stream.rs`:

```rust
            let answer_name = match &outcome {
                Ok(()) => "done",
                Err(Failure::Retry(_)) => "retry",
                Err(Failure::Skip(_)) => "skip",
            };
            let labels = [("reader", reader.durable.to_owned()), ("kind", kind.clone()), ("outcome", answer_name.to_owned())];
            metrics::counter!("mamaput_events_handled_total", &labels).increment(1);
```

And in notifications: `mamaput_messages_sent_total{kind}` after each send, and `mamaput_breaker_open{breaker}` (1 while open) where part 1 of the previous topic logged the breaker changing.

The label values are all from small fixed lists: `app`, `graphql` or `mcp`; six payment outcomes; four event kinds; `done`, `retry` or `skip`. Never an order id, a customer id or an email.

## Step 5: Prometheus, reading all three
<!-- bite: 020aadcc-0a68-46ac-a27c-01be16cb2dd6 -->

`deploy/prometheus.yml`:

```yaml
# Reads every program's /metrics every 15 seconds. Lesson 38 points these at the containers instead.
global:
  scrape_interval: 15s
rule_files:
  - alerts.yml
scrape_configs:
  - job_name: api
    static_configs: [{ targets: ["127.0.0.1:9100"] }]
  - job_name: worker
    static_configs: [{ targets: ["127.0.0.1:9101"] }]
  - job_name: notifications
    static_configs: [{ targets: ["127.0.0.1:9102"] }]
```

```bash
docker run -d --name mamaput-prometheus --network host \
  -v "$PWD/deploy":/etc/prometheus prom/prometheus:v3.7.3 --config.file=/etc/prometheus/prometheus.yml
```

`--network host` lets Prometheus, in its container, reach the three programs on `127.0.0.1`. (Lesson 38 puts it on the same Docker network as the programs instead.)

With all three running, five menu requests, a missing dish, a scanner's `/wp-admin.php`, and one order paid by webhook, the API's own `/metrics` (`curl localhost:9100/metrics`) shows:

```text
mamaput_payments_settled_total{outcome="paid"} 1
mamaput_orders_placed_total{via="app"} 1
http_requests_total{method="GET",route="unmatched",code="404"} 1
http_requests_total{method="POST",route="/webhooks/paystack",code="200"} 1
http_requests_total{method="GET",route="/v2/menu/{id}",code="404"} 1
http_requests_total{method="GET",route="/v2/menu/{id}",code="200"} 5
http_requests_total{method="POST",route="/v2/orders",code="201"} 1
```

Notifications' and the worker's:

```text
mamaput_events_handled_total{reader="notifications",kind="order.paid",outcome="done"} 4
mamaput_events_handled_total{reader="notifications",kind="order.paid",outcome="retry"} 1
mamaput_messages_sent_total{kind="receipt-email"} 4
mamaput_outbox_oldest_unpublished_seconds 0
```

Four receipts for one payment? Three were events left over from earlier runs, waiting in the stream for notifications to come back. And the one `retry` was real: notifications started a moment before the API was answering, its first `GetContact` timed out (tonic's `Cancelled`, "Timeout expired", in its log), and the stream gave the event back a second later. The numbers told that story before I'd read a single log line.

Prometheus's targets page (`http://localhost:9090/targets`) shows `api`, `worker` and `notifications` all **up**. And it answers questions in **PromQL**, its query language. Requests by route and code, across every copy of the API:

```text
sum by (route, code) (http_requests_total)

  {code="200", route="/v2/menu/{id}"}            5
  {code="404", route="/v2/menu/{id}"}            1
  {code="404", route="unmatched"}                1
  {code="201", route="/v2/orders"}               1
  {code="200", route="/webhooks/paystack"}       1
```

and the 95th percentile of `GET /v2/menu/{id}` over the last two minutes:

```text
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route="/v2/menu/{id}"}[2m])))

  0.008
```

8 ms. (`rate` needs at least two scrapes inside its window, so the same question asked in the first 15 seconds came back empty.)

## Step 6: alerts that matter
<!-- bite: b65c38fa-9cc0-4bc6-9f35-d04ee29542d4 -->

An alert wakes someone up, so each one must mean "a person needs to act, now". Alert on **symptoms customers feel**, not on every cause. `deploy/alerts.yml`:

```yaml
# Alerts wake a person, so each one means "someone must act now", about something a customer feels.
groups:
  - name: mama-put
    rules:
      - alert: ManyServerErrors
        expr: sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.02
        for: 5m
        annotations: { summary: "More than 2% of API requests are failing" }

      - alert: SlowAPI
        # Live streams stay open for minutes; they'd make every percentile look terrible.
        expr: histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route!~".*(events|live|stream).*"}[5m]))) > 1
        for: 10m
        annotations: { summary: "p95 latency over 1 second for 10 minutes" }

      - alert: EventsStuck
        expr: max(mamaput_outbox_oldest_unpublished_seconds) > 60
        for: 2m
        annotations: { summary: "Events have waited over a minute: receipts, texts and partner webhooks are behind" }

      - alert: PaymentMismatch
        expr: sum(increase(mamaput_payments_settled_total{outcome=~"mismatch|order_was_already_paid"}[10m])) > 0
        annotations: { summary: "A payment didn't match its order, or an order was paid twice. Look now." }

      - alert: NoOrders
        # hour() is UTC; Lagos is UTC+1, so this is 8am to 9pm in Lagos.
        expr: sum(increase(mamaput_orders_placed_total[30m])) == 0 and on() hour() >= 7 and on() hour() < 20
        annotations: { summary: "No orders for 30 minutes during opening hours" }

  - name: mama-put-gentle
    rules:
      - alert: BreakerOpen
        expr: max by (breaker) (mamaput_breaker_open) == 1
        for: 10m
        labels: { severity: chat }
        annotations: { summary: "A circuit breaker has been open for 10 minutes: messages are late" }
```

1. **`for: 5m`** means the condition must hold for 5 minutes before anyone is woken. One bad scrape isn't an emergency.
2. **`EventsStuck`** covers a whole family of causes (NATS down, the relay stuck, the worker crashed) with one symptom: events waiting.
3. **`PaymentMismatch`** has no `for`: one is too many.
4. **`NoOrders`** catches the failures every other alert misses: a broken deploy where everything answers 200 but nobody can actually order.
5. **`BreakerOpen`** is gentle (`severity: chat`): a breaker open for long means late messages, worth a message to a chat channel, not a phone call at 3 a.m. Prometheus decides when an alert fires; its companion, **Alertmanager**, decides who hears about it, by its labels, and stops the same alert arriving fifty times.

Prometheus's own checker, `promtool`, in the same image:

```bash
docker run --rm -v "$PWD/deploy":/deploy --entrypoint promtool prom/prometheus:v3.7.3 check config /deploy/prometheus.yml
```

```text
  SUCCESS: 1 rule files found
 SUCCESS: /deploy/prometheus.yml is valid prometheus config file syntax

Checking /deploy/alerts.yml
  SUCCESS: 6 rules found
```

and on the rules page, with everything healthy, all six are `inactive`. Lesson 39's pipeline runs `promtool` on every change, so a typo in an alert never ships.

## Step 7: testing metrics
<!-- bite: a1443eb1-f4d4-4a40-8791-809ee973ca0b -->

`tests/metrics.rs`:

```rust
#[sqlx::test]
async fn requests_are_counted_by_route_never_by_path(pool: PgPool) {
    let recorder = telemetry::metrics_recorder().build_recorder();
    let numbers = recorder.handle();
    // For this thread only: `#[sqlx::test]` runs the whole test on one thread.
    let _recorder = metrics::set_default_local_recorder(&recorder);

    let app = TestApp::new(pool).await;
    let dish = app.dish("Jollof rice", 1500, 40).await;
    for path in [format!("/v2/menu/{dish}"), format!("/v2/menu/{dish}"), "/v2/menu/999".into(), "/wp-admin.php".into()] {
        app.get(&path).send().await;
    }
    let ada = app.user("ada@example.com", "customer").await;
    app.post("/v2/orders").bearer(&ada).json(json!({"dishId": dish, "quantity": 1})).send().await;

    let text = numbers.render();
    for line in [
        r#"http_requests_total{method="GET",route="/v2/menu/{id}",code="200"} 2"#,
        r#"http_requests_total{method="GET",route="/v2/menu/{id}",code="404"} 1"#,
        r#"http_requests_total{method="GET",route="unmatched",code="404"} 1"#,
        r#"mamaput_orders_placed_total{via="app"} 1"#,
    ] {
        assert!(text.contains(line), "missing {line}\n{text}");
    }
    assert!(!text.contains(&format!("/v2/menu/{dish}\"")) && !text.contains("wp-admin"), "never a real path in a label");
    assert!(text.contains("http_request_duration_seconds_bucket{"), "times, in buckets, for percentiles");
}
```

1. **A recorder of its own.** `set_default_local_recorder` makes this test's numbers go to its own recorder, on its thread, so tests running at the same time don't add to each other's counts. (`#[sqlx::test]` runs a test on one thread, so the whole request happens there.)
2. **Four requests, three series**, and no `/v2/menu/1` or `/wp-admin.php` anywhere: the cardinality rule, tested.
3. **`_bucket` lines** prove request times are histograms, not summaries.

With this, `cargo test --workspace` runs 115 tests, with NATS running.

## The Rust in this part
<!-- bite: 1c25d53c-d03b-437a-b0d7-50a845eadbc9 -->

1. **A facade crate**, `metrics`: macros that record numbers anywhere, and one recorder per program that keeps them.
2. **`metrics::counter!(name, "label" => value)`** and **`metrics::counter!(name, &labels)`**: labels inline, or as a slice of pairs when they're worked out first.
3. **Gauges and histograms**: `gauge!(…).set(x)`, `.increment(1.0)` and `.decrement(1.0)`; `histogram!(…).record(seconds)`.
4. **`Instant::elapsed().as_secs_f64()`**: how long since, as seconds with a fraction, the unit Prometheus expects.
5. **`req.extensions().get::<MatchedPath>()`**: the router left the matched pattern on the request, as a value found by its type.
6. **A `const` array**, `BUCKETS: [f64; 11]`, passed as a slice with `&BUCKETS`.
7. **`metrics::set_default_local_recorder(&recorder)`** returns a guard; while it lives, this thread's numbers go to that recorder.

## Your project so far
<!-- bite: 8d379e8e-c174-4bf1-bb12-1ac0cb1c8127 -->

The whole topic, all three parts:

```text
mama-put/
├── telemetry/                    ← NEW crate: init, subscriber, tracer_provider, trace helpers, serve_metrics, metrics_recorder
├── deploy/
│   ├── prometheus.yml            ← NEW: scrape api 9100, worker 9101, notifications 9102
│   └── alerts.yml                ← NEW: six alerts, checked by promtool
├── migrations/0015_outbox_traceparent.sql   ← NEW
├── contracts/src/stream.rs       ← a span per event; mamaput_events_handled_total
├── src/
│   ├── main.rs · bin/worker.rs   ← telemetry::init, serve_metrics, shutdown
│   ├── lib.rs                    ← request span continues traces; record_metrics layer
│   ├── http/request_metrics.rs   ← NEW: by route, never by path
│   ├── grpc/mod.rs               ← grpc_span
│   ├── outbox.rs                 ← traceparent saved and sent; oldest_waiting gauge
│   ├── orders/service.rs         ← mamaput_orders_placed_total
│   └── payments/service.rs       ← mamaput_payments_settled_total by outcome
├── tests/
│   ├── traces.rs                 ← NEW: the trace travels with the event
│   └── metrics.rs                ← NEW: counted by route; orders counted
└── notifications/src/
    ├── main.rs                   ← telemetry::init, serve_metrics
    ├── api.rs                    ← Outgoing (token + trace); Contact's safe Debug
    ├── handlers.rs               ← mamaput_messages_sent_total
    └── resilience.rs             ← mamaput_breaker_open
```

## Common mistakes
<!-- bite: 376d3f11-e418-40ec-a73b-58bfc5b3df4d -->

1. **Labels with ids or paths in them.** Every new value is a new series, for ever. Routes, outcomes, kinds: small fixed lists.
2. **Summaries instead of histograms.** Percentiles from each copy can't be added together. Give anything in seconds buckets.
3. **Serving `/metrics` on the public port.** It tells strangers how the business is doing.
4. **Averages.** One slow request in a hundred disappears in an average. Look at p95 and p99.
5. **Alerts on causes**, like "CPU is high". Alert on what customers feel; graph the causes.
6. **Alerts that fire on one bad moment.** Give them a `for`, unless one is already too many.
7. **Only technical numbers.** Everything can be green while nobody can order. Count the business too.

## Check your understanding
<!-- bite: 02cac259-64db-49ae-b597-e4a4b5e7cac3 -->

1. What are the four golden signals, and which of our metrics covers each?
2. Why is `route` the pattern and not the real path? What would `/v2/menu/4` as a label do over a year?
3. Why give request times buckets, so they're histograms?
4. Why does `EventsStuck` cover more problems than an alert for "NATS is down" would?
5. Why does `PaymentMismatch` have no `for`, and `ManyServerErrors` have `for: 5m`?

<details>
<summary>Answers, after your attempt</summary>

1. Traffic and errors: `http_requests_total` by code (and `mamaput_events_handled_total` by outcome). Latency: `http_request_duration_seconds`. Saturation: `http_requests_in_flight`, `mamaput_outbox_oldest_unpublished_seconds`, `mamaput_breaker_open`.
2. Every distinct value is a series kept over time. Real paths would make one per dish, per order and per scanner's guess: millions over a year, until Prometheus falls over. The pattern is one series per route.
3. So Prometheus can work out percentiles across every copy of a program. A summary's percentiles are worked out inside each copy and can't be combined.
4. Because it watches the symptom, events waiting, and that one symptom has many causes: NATS down, the relay stuck, the worker crashed, Postgres slow. An alert per cause would miss the cause nobody thought of.
5. A mismatched payment is serious and rare: one is already worth waking someone. Server errors happen in small bursts that fix themselves; five minutes of them is a real problem.

</details>

## Practice
<!-- bite: 248149a2-3c3d-4b18-9dfe-56221b802e9f -->

1. Add `mamaput_v1_requests_total{client}` from lesson 10's deprecated v1, using the User-Agent's product name only (a small list), and write the PromQL for "v1 requests per day".
2. Add a histogram for how long notifications' handlers take, and an alert if its p95 is over 5 seconds for 10 minutes.
3. Run Alertmanager beside Prometheus, and send `BreakerOpen` to a webhook you can watch (lesson 17's `fake_okada` example will do).
4. Pause the API with `kill -STOP` and watch `mamaput_breaker_open` and `mamaput_events_handled_total{outcome="retry"}` in Prometheus.

**Done when** all three programs serve `/metrics` on private ports, Prometheus shows them up, requests are counted by route, `promtool` accepts the alerts, and `cargo test --workspace` passes.

## Before moving on
<!-- bite: 7b539e9a-c7f4-494c-b958-8c9a4e14aaba -->

Mama Put can be seen from outside now: lines to search, a trace for each action across every program, numbers kept all the time, and alerts that wake someone only when customers are hurt. What's left is running it somewhere other than this laptop. The next lesson packs each program into a small Docker image, reads its settings safely, and starts the whole system, Postgres, Redis, NATS, Jaeger and Prometheus included, with one command.

## Related
<!-- bite: 9ba18155-38df-461f-9353-aa688eff8cf3 -->

- [[backend/frameworks/axum/38-production-config-and-docker|Next: Production Config and Docker]]
- [[backend/frameworks/net-http/27-observability|The same topic in net/http]] — `client_golang`, and `testutil` for metrics tests
- [[backend/frameworks/axum/10-versioning|Versioning]] — the v1 counter this makes real

## About this lesson
<!-- bite: 865d2d46-723b-4719-a447-6cd13cc077e6 -->

**Level:** Advanced. Part 3 of 3 on observability, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), metrics 0.24, metrics-exporter-prometheus 0.18 and Prometheus 3. Covers the four golden signals and business metrics, a facade and one recorder per program, `/metrics` on a private address, histograms with buckets instead of summaries, HTTP metrics by matched route and the cardinality rule, counters and gauges for orders, payments, the outbox's backlog, events, messages and the breaker, Prometheus scraping three programs and PromQL questions, alerts on symptoms with `for`, gentle alerts and Alertmanager, `promtool`, and testing metrics with a local recorder.
