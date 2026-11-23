---
id: 10b9b661-edb6-4886-a7d3-035f2eb9546d
---

# Observability 1: Logs

**Observability is being able to tell, from outside, what a running system is doing and why, from what it writes down as it works: logs, metrics and traces.**

## Before you start
<!-- bite: 54cf60ba-b300-45ee-8971-9b8d4ae2d76d -->

You should have finished [[backend/frameworks/axum/34-calling-services-safely-2|Calling Services Safely 2]]: three programs (the API, the worker, notifications) now work together through NATS and gRPC. Since lesson 3, the API has written a log line for every request with `tracing`; this topic builds on that.

This topic comes in three parts:

1. **Logs**: every program writes the same kind of line, one JSON object each, with what's needed and never what isn't.
2. **Following one action**: one id, the trace id, travels with Ada's payment through every program it touches, in the logs and in a trace you can see.
3. **Metrics and alerts**: numbers that say how the system is doing right now, and alerts that wake someone only when a customer would notice.

After this part you will be able to:

1. Set up the same logging in every program from one small shared crate.
2. Write logs as JSON lines a machine can search, and keep readable lines for your laptop.
3. Choose a level for each line, and say what to log and what never to log.
4. Make a type that can't leak personal details into a log, even by mistake.
5. Test what a program logs.

## What to install
<!-- bite: 4d055107-8f11-42bc-bbca-e055dc6db3a4 -->

Nothing for this part. Part 2 needs **Jaeger**, in Docker, and adds the OpenTelemetry crates; part 3 adds the metrics crates.

## Where we stopped
<!-- bite: 61a38cca-acea-46e2-85f9-f06e320b0987 -->

It's 2pm. Ada writes to support: "I paid at 12:40 and never got a receipt." Support asks you. Where do you look?

1. The API's logs? Each copy of the API prints lines like `paystack webhook … outcome=Paid`, with no way to connect them to Ada's missing email.
2. The worker's relay? Did it publish? It writes nothing when things go well.
3. Notifications? Did it get the event? Did it call the API for her contact? Did the breaker open? Did the mailer fail?

Three programs, three log streams, no common thread. You'd be reading timestamps and guessing. And separately: is the API slow today? Slower than last week? Is the outbox backing up right now? Nobody knows until a customer complains.

## The kid version
<!-- bite: f8b529b4-2966-4c8e-b4c7-2ca7e2c41e09 -->

Mama Put's business has grown, and Mama can't watch everything herself. So she does three things.

She keeps a **notebook** by the till, and everyone writes a line when something happens: "12:40, order 42, paid". That's logs.

For the strange cases, she gives each order a **coloured ribbon**. Whoever touches the order (the till, the kitchen, the boy who sends texts) notes the ribbon's colour beside what they did. When something goes wrong with Ada's order, Mama finds every note with Ada's ribbon colour, in order, from every corner of the shop. That's a trace.

And she puts a **tally board** on the wall: plates sold today, plates left, how long the queue is. She glances at it and knows how the day is going without reading the notebook. That's metrics.

**Where the picture stops working.** In a real shop, people forget to write in the notebook. In our programs, most of the notes are written automatically, by the libraries, as long as we wire them up once. That's most of this topic.

## Terms used in this part
<!-- bite: 2d7a0b19-4ba2-421d-abb7-3ed4afdedeea -->

1. **Structured log**: This is a log line made of named fields (`"order_id": 42`), usually as JSON, instead of a sentence. Machines can search and filter it.
2. **Log level**: This is how important a line is: `DEBUG`, `INFO`, `WARN` or `ERROR`. Production usually keeps `INFO` and up.
3. **Subscriber**: This is `tracing`'s name for whatever receives log events and spans and does something with them, like writing them out. Each program sets one up, once.
4. **Span**: This is a piece of work with a start and an end, like "handling this request". Log lines written inside it carry its fields.

## Step 1: one way to log, for every program
<!-- bite: 54ac1524-f192-4bf8-b204-7057821128fb -->

Since lesson 3, `main` set up logging with one line, `tracing_subscriber::fmt().with_env_filter(...).init()`, and the worker and notifications copied it. Three programs, three copies, each a little different. Now they share a crate, `telemetry`, beside `contracts` in the workspace (and, like `contracts`, knowing nothing about either service). `telemetry/src/lib.rs` starts:

```rust
/// What can go wrong setting up. A concrete type, so `?` works whatever error type `main` uses.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("can't make the span exporter: {0}")]
    Exporter(#[from] opentelemetry_otlp::ExporterBuildError),
    #[error("logging was already set up: {0}")]
    AlreadySetUp(#[from] tracing_subscriber::util::TryInitError),
}

/// Keeps the tracer going. `shutdown` sends any spans still waiting; call it before the program ends.
pub struct Telemetry {
    provider: SdkTracerProvider,
}

impl Telemetry {
    pub fn shutdown(self) {
        if let Err(e) = self.provider.shutdown() {
            eprintln!("couldn't send the last spans: {e}");
        }
    }
}

/// Logging and tracing for the program called `service`, with `filter` (like `mama_put=info`) unless
/// RUST_LOG says otherwise. Logs are JSON, one object per line; LOG_FORMAT=text gives readable lines
/// for a laptop. Spans go to OTEL_EXPORTER_OTLP_ENDPOINT if it's set, and nowhere otherwise.
pub fn init(service: &'static str, filter: &str) -> Result<Telemetry, Error> {
    let provider = tracer_provider(service, std::env::var_os("OTEL_EXPORTER_OTLP_ENDPOINT").is_some())?;
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(filter));
    if std::env::var("LOG_FORMAT").as_deref() == Ok("text") {
        let traces = tracing_opentelemetry::layer().with_tracer(provider.tracer(service));
        tracing_subscriber::registry().with(filter).with(traces).with(fmt::layer()).try_init()?;
    } else {
        subscriber(&provider, service, filter, std::io::stdout).try_init()?;
    }
    Ok(Telemetry { provider })
}
```

And the API's `main` now begins:

```rust
let telemetry = telemetry::init("api", "mama_put=info,tower_http=info")?;
```

(the worker's says `"worker"`, notifications' says `"notifications"`), and ends with `telemetry.shutdown()`, which part 2 explains.

1. **JSON by default.** A log system can find every line with `"trace_id": "88f9…"` in milliseconds; it can't search sentences. One JSON object per line is what every log collector expects.
2. **`LOG_FORMAT=text`** for your laptop, where you read lines by eye. Lesson 3's readable format is still there for that.
3. **`RUST_LOG` overrides the default filter** (`EnvFilter::try_from_default_env`), so you can turn on `DEBUG` for one module while chasing something: `RUST_LOG=notifications=debug`.
4. **A concrete error type.** `init`'s errors are an enum, not a boxed error, so `?` works in `main` whichever error type it returns. (A first try returned a boxed `Send + Sync` error, and the API's `main`, which returns a plain boxed error, wouldn't accept it.)

The subscriber itself:

```rust
/// Spans become OpenTelemetry spans, and every log line is a JSON object written to `writer`, with the
/// spans it happened inside (and so their trace ids). Used by `init`, and by tests that read the logs.
pub fn subscriber<W>(provider: &SdkTracerProvider, service: &'static str, filter: EnvFilter, writer: W) -> impl tracing::Subscriber + Send + Sync
where
    W: for<'w> fmt::MakeWriter<'w> + Send + Sync + 'static,
{
    let traces = tracing_opentelemetry::layer().with_tracer(provider.tracer(service));
    let logs = fmt::layer().json().with_current_span(false).with_span_list(true).with_writer(writer);
    tracing_subscriber::registry().with(filter).with(traces).with(logs)
}
```

Three layers, each wrapping the next: a **filter** (which lines to keep), the **traces** layer (part 2), and the **logs** layer, writing JSON. `with_span_list(true)` puts every span the line happened inside into the line, with its fields: that's how a line written deep inside a handler still carries the request's id.

A line from notifications, sending a receipt, looks like this:

```json
{"timestamp":"2026-11-23T06:32:46.869103Z","level":"INFO","fields":{"message":"email (not really sent)","to":"tola@example.com","subject":"Mama Put receipt for order 27","text":"Thank you, Tola! 1 × Moi moi, ₦700.00."},"target":"notifications::providers","spans":[{"id":"36f334ce-33ff-4fbb-b270-2fd5c37c22c7","kind":"order.paid","trace_id":"ff85f0e8359114d64d7d813a9f159458","name":"event"}]}
```

`fields` is what the line itself said; `spans` is where it happened (part 2 explains `trace_id`).

Look at `"to":"tola@example.com"`. That line breaks step 3's rule below, and it's there on purpose: `ConsoleMailer` exists to show, on a laptop, exactly what would be sent, address and all. It must never run in production. The real mailer would log the event id and the customer id, and nothing about Tola. `target` says which crate and module wrote it (`notifications::providers`), so lines from different programs are easy to tell apart. When the programs run in containers (lesson 38), the log collector adds the container's name too.

## Step 2: what to log
<!-- bite: 25812167-ad63-4c4d-9000-612ec1a73bd6 -->

Log what you'd need to answer a question later:

1. **Every request**, once, at the end: method, path, status, how long (lesson 3's `TraceLayer` does this).
2. **Every change that matters**: order placed, payment settled (reference, outcome), status changed, event handled, message sent.
3. **Every decision the system made by itself**: a retry, a breaker changing state, an event dropped, a quote expired, a rate limit hit. Lessons 18 to 34 already write these at `WARN`.
4. **Every unexpected error**, in full, at `ERROR`, with what was being done.

**Levels**, so a person can filter:

1. **`INFO`** for things that happened (order placed, payment settled, event handled).
2. **`WARN`** for things that went wrong but were handled (a retry, the breaker opened, a bad event dropped).
3. **`ERROR`** for things a person should look at (a payment amount that doesn't match, a panic, a failure we can't recover from).
4. **`DEBUG`** is off in production. Turn it on for one module with `RUST_LOG` while you're chasing something.

**Fields, not sentences.** `tracing::info!(order_id = order.id, outcome = ?outcome, "payment settled")` puts `order_id` and `outcome` in their own JSON fields, which a log system can filter on. `info!("payment settled for order {}", order.id)` buries them in a sentence.

## Step 3: what never to log
<!-- bite: de9590da-d4b9-47bb-924e-a6859de877b1 -->

1. **Secrets**: passwords, tokens of every kind (access, refresh, service, MCP), API keys, webhook secrets, the `Authorization` header.
2. **Personal details**: email addresses, phone numbers, names, addresses. Log the customer's **id**. Support can look the person up when they need to; logs are read by far more people, kept far longer, and copied to more places than the database.
3. **Card details**, ever. We never see them anyway: Paystack's page takes them.
4. **Whole request or response bodies.** They contain all of the above, sooner or later.

Rust can make a type refuse to leak. `tracing` writes a value with `?` using its `Debug`, so a type whose `Debug` hides the details is safe to log, even by mistake. Notifications' `Contact` used to `#[derive(Debug)]`; now, in `notifications/src/api.rs`:

```rust
/// `{:?}` shows whether there's an email and a phone, never what they are: a `Contact` logged by
/// mistake leaks nothing. Logs are read by more people, and kept longer, than the database.
impl std::fmt::Debug for Contact {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Contact").field("has_email", &!self.email.is_empty()).field("has_phone", &self.phone.is_some()).finish()
    }
}

#[async_trait]
pub trait Customers: Send + Sync {
    async fn contact(&self, customer_id: i64) -> Result<Contact, Failure>;
}

#[async_trait]
pub trait Menu: Send + Sync {
    /// The dish's name, or "" if it can't be had quickly: the message is worded without it.
    async fn dish_name(&self, dish_id: i64) -> String;
}
```

and its test, in the same file:

```rust
    #[test]
    fn a_contact_in_a_log_line_shows_nothing_personal() {
        let ada = Contact { first_name: "Ada".into(), email: "ada@example.com".into(), phone: Some("+2348012345678".into()) };
        assert_eq!(format!("{ada:?}"), "Contact { has_email: true, has_phone: true }");
    }
}
```

Now `tracing::warn!(contact = ?contact, "…")` writes `Contact { has_email: true, has_phone: true }`, not Ada's email. The safe thing becomes the thing that happens without anyone remembering. Lesson 12's `Keys` and lesson 33's `Signer` already never print their secrets: neither derives `Debug` at all, so they can't be logged with `?`.

## Step 4: testing what you log
<!-- bite: 746763f8-6af9-4afb-b8cf-4470cb32a2d9 -->

Logs are output like any other, and they break like any other: a field renamed, a line that stopped carrying its id. `subscriber` takes any writer, so a test can give it a buffer and read the JSON back. In `telemetry/src/lib.rs`:

```rust
    /// Log lines, kept in memory.
    #[derive(Clone, Default)]
    struct Lines(Arc<Mutex<Vec<u8>>>);

    impl std::io::Write for Lines {
        fn write(&mut self, bytes: &[u8]) -> std::io::Result<usize> {
            self.0.lock().unwrap().extend_from_slice(bytes);
            Ok(bytes.len())
        }
        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }
```

`tracing::subscriber::with_default` uses a subscriber for one closure only, so a test doesn't change logging for the rest of the program. Part 2 shows the test that uses it, checking a line's fields and the trace id it carries.

## The Rust in this part
<!-- bite: 4100a8a7-9031-4092-8a8c-beae9c331ab1 -->

1. **A crate shared by every program in the workspace**, `telemetry`, depended on by path like `contracts`.
2. **`tracing_subscriber` layers**, `registry().with(filter).with(traces).with(logs)`: each `.with` wraps another layer around the ones before.
3. **`impl tracing::Subscriber + Send + Sync` as a return type**: the real type is long and nobody needs to name it.
4. **A generic writer**, `W: for<'w> fmt::MakeWriter<'w>`: stdout in the program, a buffer in a test. `for<'w>` says it works for any lifetime the subscriber asks for.
5. **A hand-written `Debug`**, with `f.debug_struct(...).field(...).finish()`: what `{:?}`, and so `tracing`'s `?field`, shows.
6. **An error enum with `#[from]`**, so `?` converts each library's error, and the enum converts into any boxed error type a caller uses.
7. **`impl std::io::Write`** for a test type: two methods, and anything that writes bytes can write into it.

## Your project so far
<!-- bite: 07abf544-3720-4c7c-969c-894ca552478b -->

```text
mama-put/
├── Cargo.toml                    ← members gain "telemetry"; telemetry as a dependency
├── telemetry/                    ← NEW crate: init, subscriber, tracer_provider (part 2), trace helpers (part 2)
├── src/main.rs                   ← telemetry::init("api", …), telemetry.shutdown()
├── src/bin/worker.rs             ← telemetry::init("worker", …)
└── notifications/
    └── src/
        ├── main.rs               ← telemetry::init("notifications", …)
        └── api.rs                ← Contact's Debug shows nothing personal
```

## Common mistakes
<!-- bite: 80b0d586-fa06-4395-9047-48bd7e13672b -->

1. **Sentences instead of fields.** Nobody can filter on a number buried in a sentence.
2. **Logging secrets or personal details**, often by logging a whole struct or a whole request. Log ids; make types that can't leak.
3. **Everything at `INFO`**, or everything at `ERROR`. Levels are for filtering; use them for what they mean.
4. **Each program setting up logging its own way.** Then their lines don't match, and can't be searched together.
5. **Not testing logs.** A renamed field breaks every saved search silently.

## Check your understanding
<!-- bite: f6275c7d-8a97-4836-9563-4692c0e6f634 -->

1. Why JSON lines in production, and when would you use `LOG_FORMAT=text`?
2. A line is written deep inside a handler. How does it end up carrying the request's id?
3. What level would you use for: an order placed; a retry; a payment amount that doesn't match its order?
4. Why is `Contact`'s hand-written `Debug` safer than remembering not to log contacts?

<details>
<summary>Answers, after your attempt</summary>

1. A machine can search and filter named fields in JSON; it can't do that reliably with sentences. Text lines are for reading by eye on your own laptop.
2. The request's span holds the id as a field, and the JSON layer writes every span a line is inside (`with_span_list(true)`) into the line.
3. `INFO`, `WARN` and `ERROR`: something happened; something went wrong but was handled; a person must look.
4. Because anyone logging a `Contact` with `?`, now or years from now, gets the safe version without having to remember anything.

</details>

## Practice
<!-- bite: 503c720b-f00b-462a-a5f2-c03054fceab6 -->

1. Run the API with `LOG_FORMAT=text`, then without, and compare the same request's line.
2. Find a log line in lessons 17 to 34 that puts a value in a sentence instead of a field, and change it.
3. Give lesson 12's `User` a `Debug` that shows only its id and role, and a test for it.

**Done when** all three programs log JSON through `telemetry::init`, `LOG_FORMAT=text` gives readable lines, and the `Contact` test passes.

## Before moving on
<!-- bite: 207c60a8-9370-4823-8a59-70ba092de92f -->

Every program now writes the same kind of line, searchable, and safe to read. But Ada's question is still hard: the API's line for her payment and notifications' line for her receipt don't share anything. Part 2 gives them something to share: one id that travels with her payment through every program it touches.

## Related
<!-- bite: a15cedce-601a-4442-853e-95fed39ae767 -->

- [[backend/frameworks/axum/36-observability-2|Next: Observability 2: Following One Action]]
- [[backend/frameworks/net-http/27-observability|The same topic in net/http]] — `log/slog`, and `LogValue` instead of `Debug`
- [[backend/frameworks/axum/03-middleware|Middleware]] — where the request log line began

## About this lesson
<!-- bite: 2b436cdc-668a-429f-a179-85b664b867cf -->

**Level:** Advanced. Part 1 of 3 on observability, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), tracing 0.1 and tracing-subscriber 0.3. Covers one shared crate setting up logging for every program, JSON lines with the spans each line happened in, readable text for development, `RUST_LOG`, a concrete setup error type, levels, what to log and what never to log, a hand-written `Debug` that can't leak personal details, and testing logs with an in-memory writer.
