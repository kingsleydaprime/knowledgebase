---
id: da35efb2-4aca-4bc6-b26b-355b81a0d69d
---

# Observability 2: Following One Action

**A trace is the whole journey of one action through every program it touches, and the trace id is the one id that travels with it, so every log line and every span along the way can be found together.**

## Before you start
<!-- bite: 474c273c-c906-47b4-a073-5915ff0e7f92 -->

You should have finished [[backend/frameworks/axum/35-observability-1|part 1]]: every program logs JSON lines through `telemetry::init`. This part leans on lesson 7 (request ids), the microservice topic (the outbox, the relay and the reader) and lesson 33 (an interceptor on every gRPC call).

After this part you will be able to:

1. Explain traces, spans and the `traceparent` header.
2. Start or continue a trace for every HTTP request and gRPC call.
3. Carry a trace across NATS, through the outbox, so an event's handler continues the trace of the change that caused it.
4. Send spans to Jaeger and follow one payment through three programs.

## What to install
<!-- bite: a4274ea1-1ae6-42e9-9fb2-d87178ee0017 -->

**Jaeger**, which stores traces and shows them, in Docker:

```bash
docker run -d --name mamaput-jaeger -p 16686:16686 -p 4317:4317 jaegertracing/jaeger:2.11.0
```

Port **4317** takes spans (OTLP over gRPC, OpenTelemetry's standard way to send them); port **16686** is its web page, at `http://localhost:16686`.

And four crates, in `telemetry` only:

```bash
cargo add -p telemetry opentelemetry@0.33 tracing-opentelemetry@0.34
cargo add -p telemetry opentelemetry_sdk@0.33 --features rt-tokio
cargo add -p telemetry opentelemetry-otlp@0.33 --features grpc-tonic
```

1. **opentelemetry** and **opentelemetry_sdk**: **OpenTelemetry** is the standard, shared by every language, for traces (and metrics and logs). The SDK makes spans, gives them ids and sends them on.
2. **opentelemetry-otlp**: sends them over OTLP. `grpc-tonic` uses tonic, which we already have; `cargo tree` shows the same tonic 0.14.9, so nothing is built twice.
3. **tracing-opentelemetry**: turns our `tracing` spans into OpenTelemetry spans. We don't write OpenTelemetry code in the services; we keep writing `tracing`.

The versions must match each other: tracing-opentelemetry 0.34 is for opentelemetry 0.33.

## Where we stopped
<!-- bite: 3acad673-5fd9-4a08-ab66-2b1cdd11ac43 -->

Each program logs searchable lines, but nothing joins them. Ada's payment is handled by the API (the webhook), recorded in the outbox, relayed by the worker into NATS, read by notifications, which calls the API back over gRPC twice. Five steps, three programs. We need one id that travels with the work.

## Terms used in this part
<!-- bite: f3652f59-f888-4df0-9750-fe1a5f6431c6 -->

1. **Trace**: This is the whole journey of one action, made of spans.
2. **Span**: This is one piece of work in a trace, with a start, an end, a name and a parent: "the API handled `POST /webhooks/paystack`", "notifications handled event `order.paid`".
3. **Trace id**: This is the id every span in one trace shares: 32 hex characters.
4. **Context propagation**: This is passing the trace id from one program to the next, in an HTTP header, gRPC metadata or a message header, so the spans join up into one trace.
5. **Sampling**: This is keeping only some traces (say 10%), because keeping every one costs too much.

## Step 1: `traceparent`
<!-- bite: c9e7a0fd-e1a9-4ac7-a92d-d5ed4b883475 -->

OpenTelemetry carries the trace in a standard header, **`traceparent`** (from the W3C), the same in every language:

```text
traceparent: 00-88f9a9f56d5913c89277f9d6b4ec0c06-daf0376ca5f8fd9a-01
             │  └── trace id (the whole journey)  └── parent span    └── sampled
             └── version
```

Whoever receives it makes their span a child of that parent, in that trace. Whoever sends work on writes their own span as the new parent. In Go, the libraries do both for HTTP and gRPC by themselves (`otelhttp`, `otelgrpc`), and the trace travels in `context.Context`. In Rust, the current span plays the part of the context, and we write the two ends ourselves, in three small functions in `telemetry`:

```rust
/// The trace id `span` belongs to, as 32 hex characters, if it belongs to one.
pub fn trace_id(span: &Span) -> Option<String> {
    let context = span.context();
    let span_context = context.span().span_context().clone();
    span_context.is_valid().then(|| span_context.trace_id().to_string())
}

/// `traceparent` for the current span: send it wherever the work goes next.
pub fn traceparent() -> Option<String> {
    let mut carrier = HashMap::new();
    global::get_text_map_propagator(|p| p.inject_context(&Span::current().context(), &mut carrier));
    carrier.remove("traceparent")
}

/// Makes `span` part of the trace `traceparent` names (if there is one), and writes its trace id into
/// its `trace_id` field, so every log line inside it shows it. Call it before entering the span.
pub fn continue_trace(span: &Span, traceparent: Option<&str>) {
    if let Some(traceparent) = traceparent {
        let carrier = HashMap::from([("traceparent".to_owned(), traceparent.to_owned())]);
        let parent = global::get_text_map_propagator(|p| p.extract(&carrier));
        let _ = span.set_parent(parent);
    }
    if let Some(id) = trace_id(span) {
        span.record("trace_id", id);
    }
}
```

1. **`trace_id(span)`** reads the id from the span's OpenTelemetry context, if there is one.
2. **`traceparent()`** writes the *current* span's context as a `traceparent`, for whatever the work goes to next: a gRPC call, an outbox row.
3. **`continue_trace(span, traceparent)`** makes a new span the child of one that came from elsewhere, and records the trace id in the span's `trace_id` field, so part 1's JSON lines show it. It must run **before the span is entered**: once work has started under it, its trace can't change.
4. **The global propagator** (`TraceContextPropagator`, set in `tracer_provider`) knows the `traceparent` format; `HashMap` is the simplest thing for it to write into and read from.

And the rest of `telemetry`'s setup:

```rust
/// Traces are made even when nothing collects them, so every log line still carries its trace id.
pub fn tracer_provider(service: &'static str, export: bool) -> Result<SdkTracerProvider, Error> {
    global::set_text_map_propagator(TraceContextPropagator::new());
    let mut builder = SdkTracerProvider::builder().with_resource(Resource::builder().with_service_name(service).build());
    if export {
        // OTLP over gRPC, to a collector or straight to Jaeger: OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
        builder = builder.with_batch_exporter(opentelemetry_otlp::SpanExporter::builder().with_tonic().build()?);
    }
    Ok(builder.build())
}
```

Spans are always **made**, so every log line has a trace id; they're only **sent** when `OTEL_EXPORTER_OTLP_ENDPOINT` says where. The batch exporter sends them in groups, in the background, which is why `main` ends with `telemetry.shutdown()`: without it, the last few seconds of spans would be lost when the program stops.

The test, with a `traceparent` "from another service":

```rust
    #[test]
    fn a_trace_from_another_service_continues_here_and_shows_in_the_logs() {
        let provider = tracer_provider("test", false).unwrap();
        let lines = Lines::default();
        let writer = lines.clone();
        let subscriber = subscriber(&provider, "test", EnvFilter::new("info"), move || writer.clone());
        let (here, sent_on) = tracing::subscriber::with_default(subscriber, || {
            // As if another service had sent this with its call.
            let span = tracing::info_span!("event", trace_id = tracing::field::Empty);
            continue_trace(&span, Some("00-88f9a9f56d5913c89277f9d6b4ec0c06-daf0376ca5f8fd9a-01"));
            let _entered = span.enter();
            tracing::info!(order_id = 42, "receipt sent");
            (trace_id(&span), traceparent())
        });
        assert_eq!(here.as_deref(), Some("88f9a9f56d5913c89277f9d6b4ec0c06"), "the same trace");
        let sent_on = sent_on.unwrap();
        assert!(sent_on.starts_with("00-88f9a9f56d5913c89277f9d6b4ec0c06-") && !sent_on.contains("daf0376ca5f8fd9a"), "same trace, our own span: {sent_on}");

        let text = String::from_utf8(lines.0.lock().unwrap().clone()).unwrap();
        let line: serde_json::Value = serde_json::from_str(text.lines().next().unwrap()).unwrap();
        assert_eq!(line["fields"]["message"], "receipt sent");
        assert_eq!(line["fields"]["order_id"], 42);
        assert_eq!(line["spans"][0]["trace_id"], "88f9a9f56d5913c89277f9d6b4ec0c06", "{line}");
    }
}
```

The span continues trace `88f9…`; the `traceparent` it would send on has the same trace and a new span id (its own); and the JSON line has the trace id in its span list.

## Step 2: HTTP and gRPC in
<!-- bite: 65a3df32-493c-4167-a269-6326a00834b8 -->

Lesson 3's request span, in `src/lib.rs`, now continues the caller's trace if they sent one, and starts a new one if not:

```rust
/// One span per request, so every log line inside it carries the request ID, and the trace ID: the
/// caller's, if it sent a `traceparent`, or a new one.
fn request_span<B>(req: &Request<B>) -> tracing::Span {
    let header = |name: &str| req.headers().get(name).and_then(|v| v.to_str().ok());
    let request_id = header("x-request-id").unwrap_or("");
    let span = info_span!("request", method = %req.method(), path = req.uri().path(), request_id, trace_id = tracing::field::Empty);
    telemetry::continue_trace(&span, header("traceparent"));
    span
}
```

`trace_id = tracing::field::Empty` declares the field with no value yet; `continue_trace` records it. The gRPC server does the same, with its own span, in `src/grpc/mod.rs`:

```rust
/// One span per call, continuing the caller's trace.
fn grpc_span<B>(request: &axum::http::Request<B>) -> tracing::Span {
    let span = tracing::info_span!("grpc", method = request.uri().path(), trace_id = tracing::field::Empty);
    telemetry::continue_trace(&span, request.headers().get("traceparent").and_then(|v| v.to_str().ok()));
    span
}
```

used as `TraceLayer::new_for_grpc().make_span_with(grpc_span)`.

**And the request id?** Keep it. It's what customers and the phone team see (lesson 7 put it in every problem response), and it's short. Both are on the request's span, so both are on its lines. Support gets "request id `3a19…`" from Ada's screenshot, searches the logs for it, finds the `trace_id` on that line, then searches for the trace id to see everything, everywhere.

## Step 3: gRPC out
<!-- bite: 29e35444-a356-439d-a930-49399d7d5d1b -->

Notifications' calls to the API already pass through lesson 33's signer. It becomes one part of an interceptor that adds both, in `notifications/src/api.rs`:

```rust
/// What every call to the API carries: our service token, and the trace we're working in.
#[derive(Clone)]
pub struct Outgoing(pub Signer);

impl Interceptor for Outgoing {
    fn call(&mut self, request: Request<()>) -> Result<Request<()>, Status> {
        let mut request = self.0.call(request)?;
        if let Some(traceparent) = telemetry::traceparent().and_then(|t| MetadataValue::try_from(t).ok()) {
            request.metadata_mut().insert("traceparent", traceparent);
        }
        Ok(request)
    }
}

type Signed = InterceptedService<Channel, Outgoing>;
```

tonic gives a client one interceptor, so `Outgoing` wraps the signer: the token first, then the trace.

## Step 4: NATS, through the outbox
<!-- bite: 21f617ee-077f-481b-aec5-1a47e4f163d6 -->

Here the trace has to survive a database. The change happens in the API's request (with its trace); the event is published later, by the worker, which has no idea what request it came from. So the outbox keeps the trace beside the event. `migrations/0015_outbox_traceparent.sql`:

```sql
-- The trace each event was recorded in, so whoever handles it carries on the same trace.
ALTER TABLE outbox ADD COLUMN traceparent text;
```

`outbox::add` saves the current one:

```rust
    // The trace this change happened in: whoever handles the event carries it on.
    let traceparent = telemetry::traceparent();
    sqlx::query!("INSERT INTO outbox (type, version, data, traceparent) VALUES ($1, $2, $3, $4)", E::TYPE, E::VERSION, data, traceparent)
```

The relay sends it as a NATS header (NATS messages have headers, like HTTP):

```rust
            let mut message = PublishMessage::build().payload(serde_json::to_vec(&envelope)?.into()).message_id(&event.id);
            if let Some(traceparent) = &event.traceparent {
                message = message.header("traceparent", traceparent.as_str()); // NATS headers carry it, like HTTP's
            }
```

And the reader, in `contracts/src/stream.rs`, makes one span per event, continuing that trace, and handles *and answers* the event inside it:

```rust
        let (id, kind) = (envelope.id.clone(), envelope.kind.clone());
        // One span per event, in the trace the event was recorded in.
        let span = tracing::info_span!("event", id = %id, kind = %kind, trace_id = tracing::field::Empty);
        let traceparent = message.headers.as_ref().and_then(|h| h.get("traceparent")).map(|v| v.as_str());
        telemetry::continue_trace(&span, traceparent);
        // Handling and answering both happen inside the event's span, so their log lines carry its trace id.
        async {
            let outcome = tokio::time::timeout(HANDLE_TIMEOUT, handle(envelope)).await.unwrap_or_else(|_| Err(Failure::Retry("took too long".into())));
            let answer_name = match &outcome {
                Ok(()) => "done",
                Err(Failure::Retry(_)) => "retry",
                Err(Failure::Skip(_)) => "skip",
            };
            let labels = [("reader", reader.durable.to_owned()), ("kind", kind.clone()), ("outcome", answer_name.to_owned())];
            metrics::counter!("mamaput_events_handled_total", &labels).increment(1);
            match outcome {
                Ok(()) => answer(&message, AckKind::Ack).await,
                Err(Failure::Skip(why)) => {
                    tracing::warn!(%why, "event can't be handled; dropping it");
                    answer(&message, AckKind::Term).await;
                }
                Err(Failure::Retry(why)) => {
                    tracing::warn!(%why, attempt = delivered, "event failed; will try again");
                    // A plain Nak would come straight back, hammering whatever is down.
                    answer(&message, AckKind::Nak(Some(retry_delay(delivered)))).await;
                }
            }
        }
        .instrument(span)
        .await;
    }
}
```

**`.instrument(span)`** runs a future inside a span: every time it's polled, the span is current. My first version used `let _guard = span.enter();` and then awaited the answer to NATS while holding it. That's a known mistake with `tracing` in async code: an entered span stays "current" while the task is paused at `.await`, so other work on the same thread can be logged under it. `.instrument` enters and leaves on each poll, which is always right.

A test in `tests/traces.rs` checks the whole path inside the API: a request sent with a known `traceparent` leaves that trace in the outbox row for `order.placed`, and the relay's NATS message carries the same `traceparent` header.

```rust
    let trace = "4bf92f3577b34da6a3ce929d0e0e4736";
    let placed = app
        .post("/v2/orders")
        .bearer(&ada)
        .header("traceparent", &format!("00-{trace}-00f067aa0ba902b7-01"))
        .json(json!({"dishId": dish, "quantity": 1}))
        .send()
        .await;
    assert_eq!(placed.status, axum::http::StatusCode::CREATED);

    let saved = sqlx::query_scalar!("SELECT traceparent FROM outbox WHERE type = 'order.placed'").fetch_one(&pool).await.unwrap().unwrap();
    assert!(saved.starts_with(&format!("00-{trace}-")), "the outbox kept the request's trace: {saved}");
```

It sits in a test file of its own, for a reason that cost me a failing run. The test sets a `tracing` subscriber with `set_default`, which covers **its own thread only**. Run beside another test whose thread has no subscriber, and whichever reaches the request span first can make `tracing` remember, for the whole program, that nobody wants that span. Alone it passed; beside `tests/events.rs`' other test, the outbox row had no `traceparent`. One test per file gives it a program to itself.

## Step 5: one payment, followed
<!-- bite: 3bafc61d-76c3-450b-93f0-20289ee2fcf3 -->

Jaeger running, and all three programs started with somewhere to send their spans:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
cargo run                          # the API
cargo run --bin worker
cd notifications && cargo run
```

Tola orders, and Paystack's signed webhook pays for it (lesson 17). The API's line for the webhook:

```json
{"timestamp":"2026-11-23T06:32:46.403064Z","level":"INFO","fields":{"message":"finished processing request","latency":"16 ms","status":200},"target":"tower_http::trace::on_response","spans":[{"method":"POST","path":"/webhooks/paystack","request_id":"ffd148dd-47c2-41d8-b996-06b036a88e5a","trace_id":"ff85f0e8359114d64d7d813a9f159458","name":"request"}]}
```

Paystack sent no `traceparent`, so the API started a new trace, `ff85f0e8…`. Searching every program's logs for it:

```text
api            mama_put::payments::webhook     | paystack webhook {'reference': 'mp-27-209F…', 'outcome': 'Paid'}
api            tower_http::trace::on_response  | finished processing request {'latency': '16 ms', 'status': 200}
notifications  notifications::providers        | email (not really sent)   (inside span "event")
api            mama_put::grpc::customers       | contact details read {'service': 'notifications', 'customer_id': 6}
api            tower_http::trace::on_response  | finished processing request {'latency': '21 ms'}   (GetContact)
api            tower_http::trace::on_response  | finished processing request {'latency': '13 ms'}   (GetDish)
```

The webhook, the receipt in another program, and that program's two calls back to the API: one search. And in Jaeger, the same trace as spans, from its API (`/api/traces/ff85f0e8359114d64d7d813a9f159458`, which is what its page draws):

```text
+   0.0 ms  api            request    16.3 ms  parent=-        /webhooks/paystack
+ 435.5 ms  notifications  event      50.2 ms  parent=request  order.paid
+ 442.0 ms  api            grpc       22.2 ms  parent=event    /mamaput.customers.v1.CustomersService/GetContact
+ 467.4 ms  api            grpc       13.7 ms  parent=event    /mamaput.menu.v1.MenuService/GetDish
```

Read the parents: the event is a child of the webhook request, though a different program handled it, after a trip through Postgres and NATS; the two gRPC calls are children of the event. And look at the **435 ms** before notifications started. That's not slowness anywhere: it's the relay resting between looks at the outbox (it checks every 500 ms when there's nothing to send). A trace shows where time goes, including time nobody's working. (Microservice part 2's practice wakes the relay at once with `pg_notify`.)

The worker doesn't appear: the relay publishes the saved `traceparent` without a span of its own. That's a choice; practice 2 adds one.


## Step 6: sampling, and what not to put in spans
<!-- bite: a1ab568e-cbe7-46fc-8f6d-bc71fb6b160e -->

Keeping every trace is fine for Mama Put. A busy system keeps a sample: the SDK's `Sampler::TraceIdRatioBased(0.1)` keeps 10%, wrapped in `ParentBased` so a trace is kept or dropped *whole*, in every service, by the decision of the first one (the `01` at the end of `traceparent` is that decision). Many teams keep 100% of traces with errors and a small share of the rest, which needs a collector between the services and Jaeger.

Spans are kept and shown like logs, so part 1's rules apply: ids and outcomes, never secrets or personal details. Our spans carry methods, paths, event ids and kinds, and nothing else.

## The Rust in this part
<!-- bite: aea2fb35-7462-44b1-84ed-7925e8d912ca -->

1. **`tracing::field::Empty`**: declares a span field with no value yet; `span.record("trace_id", …)` fills it later.
2. **An extension trait**, `OpenTelemetrySpanExt`: tracing-opentelemetry adds `.context()` and `.set_parent()` to `tracing::Span`, once you `use` it.
3. **`global::get_text_map_propagator(|p| …)`**: runs a closure with the program's one propagator, without passing it around.
4. **`.instrument(span)`** (from `tracing::Instrument`): a future that's inside the span every time it runs. Never hold `span.enter()` across an `.await`.
5. **`async { … }.instrument(span).await`**: an async block, wrapped and awaited in place, to run a few steps inside a span.
6. **An interceptor that wraps another**, `Outgoing(Signer)`: one value per client, doing two jobs in order.
7. **`Option<&str>` from a header**, `.headers.as_ref().and_then(|h| h.get("traceparent")).map(|v| v.as_str())`: no headers, no such header, or its text.

## Your project so far
<!-- bite: 28f1077c-221e-428b-b7e1-9d0dba6d28cb -->

```text
mama-put/
├── migrations/
│   └── 0015_outbox_traceparent.sql   ← NEW: outbox.traceparent
├── telemetry/src/lib.rs              ← tracer_provider (OTLP when configured), trace_id, traceparent, continue_trace, a test
├── contracts/src/stream.rs           ← one span per event, continuing its trace
├── src/
│   ├── lib.rs                        ← the request span continues the caller's trace
│   ├── grpc/mod.rs                   ← grpc_span, the same for gRPC
│   └── outbox.rs                     ← saves the trace; the relay sends it as a header
├── tests/events.rs                   ← the trace travels with the event
└── notifications/src/api.rs          ← Outgoing: the token and the trace on every call
```

## Common mistakes
<!-- bite: 2aeb43d8-4ff3-4c17-83c4-07a4a93b0704 -->

1. **Starting a fresh trace in every program.** Then nothing joins up. Continue the caller's `traceparent`.
2. **Forgetting the hop through a database.** An outbox row has no "current span" when the relay reads it. Save the trace with the event.
3. **Holding `span.enter()` across an `.await`.** Use `.instrument`.
4. **Setting a span's parent after it has started.** `continue_trace` first, then enter.
5. **Not flushing on shutdown.** The batch exporter holds the last spans; `shutdown()` sends them.
6. **Personal details in span fields.** They're stored and shown like logs.
7. **Crate versions that don't match.** tracing-opentelemetry is built for one opentelemetry version; check `cargo tree` shows one copy.

## Check your understanding
<!-- bite: 71c4c2cd-cf03-441a-bb60-c1b2e674c7cb -->

1. What's in a `traceparent`, and what does the receiver do with it?
2. Why does the outbox need a `traceparent` column, when HTTP and gRPC don't need anything stored?
3. Support has Ada's request id from her screenshot. How do they get to everything that happened to her payment?
4. Why `.instrument(span)` rather than `let _g = span.enter();` around awaits?
5. Why does `main` call `telemetry.shutdown()`?

<details>
<summary>Answers, after your attempt</summary>

1. A version, the trace id, the sender's span id (the parent) and the sampling decision. The receiver makes its span a child of that parent, in that trace, and sends on its own span id as the next parent.
2. HTTP and gRPC calls happen while the caller's span is current, so the trace can be written into the call there and then. The event is published later by a different program, with no span from the original request, so the trace has to be saved with the event and read back.
3. Search the logs for the request id; the request's line also has its `trace_id`; search for that, in every program's logs or in Jaeger, and every line and span from that payment appears.
4. An entered span stays current while the task is paused at an `.await`, so other work on that thread could be logged under it. `.instrument` enters it only while the future is actually running.
5. Spans are sent in batches in the background. Without `shutdown`, the ones still waiting when the program stops are lost.

</details>

## Practice
<!-- bite: 3287f658-38f0-43af-bf96-146b6b6706fb -->

1. Open Jaeger's page, find `POST /webhooks/paystack`, and look at the trace's timeline. Which step took longest?
2. Add a span around `Relay::run_once`'s publish, as a child of each event's saved trace, so the worker shows in the trace too.
3. Turn on sampling at 50% with `ParentBased(TraceIdRatioBased(0.5))`, place ten orders, and count how many traces Jaeger has. Are any of them missing their notifications spans? Why not?

**Done when** one paid order shows as one trace in Jaeger with spans from the API and notifications, its lines in both programs' logs share one trace id, and `cargo test --workspace` passes, with NATS running.

## Before moving on
<!-- bite: d90f44a5-ed9f-4f1c-97cc-b038162b0a55 -->

Ada's question now has an answer in seconds: one id, every program, every step. But we only look when someone asks. Is the API slow today? Is the outbox backing up right now? Is anyone ordering at all? Part 3 adds the numbers that answer those questions all the time, and the alerts that ask a person to look only when a customer would notice.

## Related
<!-- bite: 7124425d-c152-4359-a7f9-b27828fde7d0 -->

- [[backend/frameworks/axum/37-observability-3|Next: Observability 3: Metrics and Alerts]]
- [[backend/frameworks/net-http/27-observability|The same topic in net/http]] — `otelhttp` and `otelgrpc` do the HTTP and gRPC ends by themselves
- [[backend/frameworks/axum/30-splitting-out-a-microservice-2|Splitting Out a Microservice 2]] — the outbox the trace now travels through

## About this lesson
<!-- bite: 82e2c06c-840a-4581-8be5-0125e1c39c63 -->

**Level:** Advanced. Part 2 of 3 on observability, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), opentelemetry 0.33, tracing-opentelemetry 0.34 and Jaeger 2. Covers traces, spans and the W3C `traceparent`, spans always made but only exported when configured, continuing and sending on a trace with three small helpers, HTTP and gRPC spans that continue the caller's trace, an interceptor adding the trace to every outgoing gRPC call, carrying a trace through the outbox and a NATS header to the event's reader, `.instrument` instead of holding an entered span across awaits, a payment followed through three programs in logs and in Jaeger, and sampling.
