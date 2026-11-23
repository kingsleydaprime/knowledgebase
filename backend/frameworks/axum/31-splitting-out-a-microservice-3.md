---
id: 509932a2-17df-4a92-9250-8d2bba8024c4
---

# Splitting Out a Microservice 3: Streams and Readers

**A stream keeps every event in order until each of its readers has finished with it, and a durable reader is a named place in that stream the server remembers, so a service can stop, start again, and carry on where it left off.**

## Before you start
<!-- bite: 4834a7b0-c75c-4307-ad0a-d68bf8b42370 -->

You should have finished [[backend/frameworks/axum/30-splitting-out-a-microservice-2|part 2]]: events go into the outbox with every change, and the relay moves them into NATS. This part leans on lesson 17 (webhooks to Okada Riders, and backoff between tries) and lesson 18 (work that's safe to do twice).

After this part you will be able to:

1. Set up a JetStream stream: where it listens, how long it keeps messages, and its duplicate window.
2. Read it with a durable reader that several copies of a service share.
3. Answer every message one of three ways: done, try again later, or never again.
4. Feed Okada Riders' webhooks from the stream, once per event.

## Where we stopped
<!-- bite: 0e98f853-7b89-4209-a033-aa8646971d6c -->

The relay publishes to subjects like `orders.paid`. Something has to keep those messages, and something has to read them: notifications (part 4), and the API's own worker, which sends Okada Riders their "order ready" webhooks.

## Terms used in this part
<!-- bite: c2360bdb-c954-4858-9610-bc58b4708f43 -->

1. **Stream**: This is an ordered log of messages that stay there after being read. In JetStream, a stream collects every message sent to the subjects it listens to.
2. **Durable consumer**: This is a named reader of a stream that the server remembers. It keeps track of which messages its readers have finished, even when every reader is offline.
3. **Acknowledge (ack)**: This is a reader telling the server "I've finished this message", so it isn't given out again.
4. **Eventual consistency**: This means different services see a change at slightly different times. For a moment the API knows order 42 is paid and notifications doesn't yet. Soon they agree.

## Step 1: the stream
<!-- bite: ad5c92ef-44ce-4364-afb0-16ab933ad630 -->

The stream's settings are part of the contract, so they live in `contracts/src/stream.rs`, and whichever service starts first creates it:

```rust
/// Every order event, under `orders.>`.
pub const STREAM: &str = "ORDERS";

/// Creates the ORDERS stream, or updates its settings. Safe to run at every start.
pub async fn ensure_stream(js: &jetstream::Context) -> Result<stream::Info, jetstream::context::CreateStreamError> {
    let config = stream::Config {
        name: STREAM.into(),
        subjects: vec!["orders.>".into()],
        storage: StorageType::File,              // on disk: a NATS restart loses nothing
        max_age: Duration::from_secs(7 * 24 * 3600), // older messages are deleted
        duplicate_window: Duration::from_secs(10 * 60), // a second message with the same id within 10 minutes is dropped
        ..Default::default()
    };
    js.create_or_update_stream(config).await
}
```

1. **`subjects: orders.>`**: everything published to `orders.paid`, `orders.ready` and so on lands in this stream.
2. **`StorageType::File`**: kept on disk, so a NATS restart loses nothing. (Lesson 36 gives the NATS container a volume.)
3. **`max_age: 7 days`**: older messages are deleted. A reader broken for more than a week has a bigger problem than missed receipts, and a stream that grows for ever is a disk that fills up.
4. **`duplicate_window: 10 minutes`**: the window in which part 2's message ids drop copies.
5. **`create_or_update_stream`** is safe to run at every start: it makes the stream, or brings its settings up to date.

## Step 2: durable readers
<!-- bite: 2d10b442-cd2c-4c98-bdeb-b30edbf13d5b -->

A **durable consumer** is a named reader of the stream that the server remembers: which messages it has finished, which are out with a reader, which to give out next. Several copies of the notifications service can read through the *same* durable consumer, and JetStream gives each message to one of them, so they share the work. A *different* durable consumer, like the worker's `partner-webhooks`, gets every message too, with its own progress:

```text
ORDERS stream ──┬──► consumer "notifications"     → notifications copy 1, copy 2 (share the work)
                └──► consumer "partner-webhooks"  → the API's worker
```

Both services read the same way, so the reading loop lives in `contracts` too:

```rust
/// What a handler says about an event it couldn't handle.
#[derive(Debug, thiserror::Error)]
pub enum Failure {
    /// It might work later: the API was down, the mail provider was slow. Try again after a pause.
    #[error("{0}")]
    Retry(String),
    /// It will never work: a body we can't read, a customer who's gone. Never deliver it again.
    #[error("{0}")]
    Skip(String),
}

/// How a durable consumer reads the stream.
pub struct Reader<'a> {
    /// The consumer's name, remembered by the server: every copy of a service shares it.
    pub durable: &'a str,
    /// Only these subjects, like `orders.paid`.
    pub subjects: &'a [&'a str],
    /// Give up on a message after this many tries.
    pub max_deliver: i64,
}

/// How long the server waits for an answer before giving the message to another reader.
const ACK_WAIT: Duration = Duration::from_secs(30);
/// How long one event may take. Less than ACK_WAIT, so we give up before the server does.
const HANDLE_TIMEOUT: Duration = Duration::from_secs(20);

/// Reads the stream as `reader` until `shutdown` finishes, one event at a time, handing each to `handle`.
/// An event finished when shutdown comes is answered first; the rest stay in the stream for next time.
pub async fn consume<H, Fut>(
    js: &jetstream::Context,
    reader: Reader<'_>,
    shutdown: impl Future<Output = ()>,
    handle: H,
) -> Result<(), async_nats::Error>
where
    H: Fn(Envelope) -> Fut,
    Fut: Future<Output = Result<(), Failure>>,
{
    let config = pull::Config {
        durable_name: Some(reader.durable.into()),
        filter_subjects: reader.subjects.iter().map(|s| s.to_string()).collect(),
        ack_policy: AckPolicy::Explicit, // done only when we say so, after the handler succeeded
        ack_wait: ACK_WAIT,
        max_deliver: reader.max_deliver,
        deliver_policy: DeliverPolicy::All,
        ..Default::default()
    };
    let consumer = js.get_stream(STREAM).await?.get_or_create_consumer(reader.durable, config).await?;
    let mut messages = consumer.messages().await?;
    tokio::pin!(shutdown);

    loop {
        let message = tokio::select! {
            _ = &mut shutdown => return Ok(()),
            next = messages.next() => match next {
                Some(message) => message?,
                None => return Ok(()),
            },
        };
        let delivered = message.info().map(|i| i.delivered).unwrap_or(1);
        let Ok(envelope) = serde_json::from_slice::<Envelope>(&message.payload) else {
            tracing::warn!(subject = %message.subject, "an event we can't read; dropping it");
            answer(&message, AckKind::Term).await;
            continue;
        };
        let (id, kind) = (envelope.id.clone(), envelope.kind.clone());
        let outcome = tokio::time::timeout(HANDLE_TIMEOUT, handle(envelope)).await.unwrap_or_else(|_| Err(Failure::Retry("took too long".into())));
        match outcome {
            Ok(()) => answer(&message, AckKind::Ack).await,
            Err(Failure::Skip(why)) => {
                tracing::warn!(%id, %kind, %why, "event can't be handled; dropping it");
                answer(&message, AckKind::Term).await;
            }
            Err(Failure::Retry(why)) => {
                tracing::warn!(%id, %kind, %why, attempt = delivered, "event failed; will try again");
                // A plain Nak would come straight back, hammering whatever is down.
                answer(&message, AckKind::Nak(Some(retry_delay(delivered)))).await;
            }
        }
    }
}

async fn answer(message: &jetstream::Message, kind: AckKind) {
    if let Err(e) = message.ack_with(kind).await {
        // Not fatal: unanswered, the server gives it out again after ACK_WAIT.
        tracing::warn!(cause = %e, "couldn't answer the server about a message");
    }
}

/// Longer after each failed try: 1s, 2s, 4s ... up to 2 minutes.
pub fn retry_delay(delivered: i64) -> Duration {
    let doublings = (delivered.max(1) - 1).min(7) as u32;
    Duration::from_secs(1 << doublings).min(Duration::from_secs(120))
}
```

The ideas that matter:

1. **`filter_subjects`**: a reader only receives what it asks for. `order.placed` stays in the stream for anyone who wants it; `partner-webhooks` never sees it.
2. **`AckPolicy::Explicit`**: a message counts as done only when we say so, and we say so only **after** the handler has succeeded.
3. **`ack_wait: 30 seconds`**: if a reader takes a message and doesn't answer within 30 seconds (it crashed, or hung), JetStream gives the message to another reader. That's lesson 18's "stalled job", handled by the server. Our handler may take 20 seconds at most, so it gives up before the server does, and two readers never work on one message.
4. **Three answers to a message.** `Ack`: done. `Nak` with a delay: failed, try again later. `Term`: this can never work, never deliver it again. A message that isn't even a readable envelope is `Term`ed before any handler sees it. A handler that knows the event is hopeless returns `Failure::Skip`. Everything else, including taking too long, is `Failure::Retry`.
5. **A delay on every `Nak`.** A plain `Nak` puts the message straight back, and a provider that's down would be hammered in a tight loop. `retry_delay` doubles the wait each time: 1, 2, 4, 8 seconds and so on, up to 2 minutes, lesson 17's backoff again. `1 << n` is "one, doubled n times".
6. **`max_deliver: 20`**: after 20 tries JetStream stops delivering it. With those delays, that's about half an hour of trying. Lesson 35 adds an alert for messages that reach the limit, so a person looks at them.
7. **One event at a time, per copy.** `consume` handles a message, answers it, then takes the next. For more at once, run more copies: they share the durable consumer. And `tokio::select!` only looks at `shutdown` between messages, so the event in hand is always answered before a copy stops. Messages it had fetched but not started go back to the stream after `ack_wait`.
8. **`consume` takes the handler as a closure**, `H: Fn(Envelope) -> Fut`, so each service brings its own, and none of them deals with NATS messages directly.

**Order isn't promised.** With two copies, two events are handled at the same time, and a retried event comes back after ones that were behind it. Handlers mustn't depend on order: an `order.ready` arriving before its `order.paid` must still do the right thing. Ours only look at the event in front of them, so they're fine.

### Proving it

`contracts/tests/consume.rs`, against a real NATS. It publishes three messages to a subject of its own: one whose handler fails the first time, one whose handler says it's hopeless, and one that isn't JSON at all. Then it reads them for four seconds:

```rust
    let calls: Arc<Mutex<HashMap<String, Vec<Instant>>>> = Arc::default();
    let started = Instant::now();
    let reader = Reader { durable: &me, subjects: &[&subject], max_deliver: 5 };
    stream::consume(&js, reader, tokio::time::sleep(Duration::from_secs(4)), |event| {
        let calls = calls.clone();
        async move {
            let mut calls = calls.lock().unwrap();
            let tries = calls.entry(event.id.clone()).or_default();
            tries.push(Instant::now());
            match (event.id.as_str(), tries.len()) {
                ("flaky", 1) => Err(Failure::Retry("the API is down".into())),
                ("hopeless", _) => Err(Failure::Skip("this customer is gone".into())),
                _ => Ok(()),
            }
        }
    })
    .await
    .unwrap();

    {
        let calls = calls.lock().unwrap();
        assert_eq!(calls["flaky"].len(), 2, "failed once, then handled");
        assert!(calls["flaky"][1] - calls["flaky"][0] >= Duration::from_millis(900), "and only after a pause");
        assert_eq!(calls["hopeless"].len(), 1, "skipped: never again");
        assert_eq!(calls.len(), 2, "the unreadable one never reached the handler");
        assert!(started.elapsed() < Duration::from_secs(6));
    }
```

It passes: the flaky event was handled twice, the second time after the 1-second delay; the hopeless one once; the broken one never reached the handler. And then the consumer's own numbers:

```rust
    let info = js.get_stream(stream::STREAM).await.unwrap().consumer_info(&me).await.unwrap();
    assert_eq!((info.num_pending, info.num_ack_pending), (0, 0), "nothing waiting, nothing unanswered");
    js.get_stream(stream::STREAM).await.unwrap().delete_consumer(&me).await.unwrap();
}
```

Nothing waiting, nothing out with a reader unanswered.

## Step 3: Okada Riders, from the stream
<!-- bite: a903a9ac-a040-412d-8a14-191403189fac -->

Part 2 took `OrderEvents` out of the orders service. Okada now hears about ready orders through the worker's own durable reader. `src/webhooks/okada.rs`:

```rust
/// Okada Riders, the delivery company Mama works with. They hear when an order is ready, by webhook.
/// The worker's `partner-webhooks` consumer calls this for every `order.ready` event.
#[derive(Clone)]
pub struct OkadaRiders {
    pub deliveries: Deliveries,
    pub url: String,
}

impl OkadaRiders {
    /// Queues the webhook, once per event, however many times the event arrives.
    pub async fn order_ready(&self, event_id: &str, ready: &OrderReadyV1, at: Timestamp) -> Result<(), StoreError> {
        // Only what a rider needs. No name, no email, no phone: what we send, we can't take back.
        let data = json!({
            "orderId": ready.order_id.to_string(),
            "dishId": ready.dish_id.to_string(),
            "quantity": ready.quantity,
            "readyAt": at.to_string(),
        });
        self.deliveries.enqueue_once(event_id, &self.url, "order.ready", &data).await
    }
}
```

The event can arrive more than once (a relay crash outside the duplicate window, or a reader that crashed before answering). Okada must still get one webhook. So the delivery is saved with the event's id, and `event_id` is `UNIQUE` (part 2's migration). In `src/webhooks/deliveries.rs`:

```rust
    /// Like `enqueue`, but only the first time for `event_id`: a repeated event queues nothing.
    pub async fn enqueue_once(&self, event_id: &str, url: &str, event_type: &str, data: &impl Serialize) -> Result<(), StoreError> {
        let payload = serde_json::to_value(data).expect("event data is always JSON");
        sqlx::query!(
            "INSERT INTO webhook_deliveries (event_id, url, event_type, payload) VALUES ($1, $2, $3, $4)
             ON CONFLICT (event_id) DO NOTHING",
            event_id,
            url,
            event_type,
            payload
        )
        .execute(&self.pool)
        .await?;
        Ok(())
    }
```

`ON CONFLICT (event_id) DO NOTHING`: the second time, nothing happens, and the reader acks as if it had worked, because it has. Lesson 17's `Sender` then delivers it, as before.

And the worker reads, in `src/bin/worker.rs`:

```rust
    // Lesson 17's webhooks to Okada Riders now go out from here, not from the API.
    let okada = OkadaRiders { deliveries: deliveries.clone(), url: env("OKADA_WEBHOOK_URL")? };
    let sender = Sender::new(deliveries, &env("OKADA_WEBHOOK_SECRET")?, Clock::system())?;
    tokio::spawn(sender.run(Duration::from_secs(5)));

    // Events: the stream, the relay that fills it from the outbox, and Okada's reader.
    let nats = async_nats::ConnectOptions::new().name("mama-put-worker").connect(env("NATS_URL")?).await?;
    let js = async_nats::jetstream::new(nats);
    stream::ensure_stream(&js).await?;
    let relay = tokio::spawn(Relay { pool: pool.clone(), js: js.clone() }.run(stopping()));
    let partners = tokio::spawn(async move {
        let reader = Reader { durable: "partner-webhooks", subjects: &["orders.ready"], max_deliver: 20 };
        let read = stream::consume(&js, reader, stopping(), |event| {
            let okada = &okada;
            async move {
                match event.data::<OrderReadyV1>() {
                    None => Ok(()), // not an event we know: not ours
                    Some(Err(e)) => Err(EventFailure::Skip(format!("unreadable order.ready: {e}"))),
                    Some(Ok(ready)) => {
                        okada.order_ready(&event.id, &ready, event.occurred_at).await.map_err(|e| EventFailure::Retry(e.to_string()))
                    }
                }
            }
        });
        if let Err(e) = read.await {
            tracing::error!(cause = %e, "partner-webhooks reader stopped");
        }
    });
```

1. **`ensure_stream`** at start, so the worker can publish even on a brand-new NATS.
2. **The relay and the reader each get `stopping()`**, a future that finishes on Ctrl+C, and run as their own tasks. At the end of `main`, after the jobs have stopped, `tokio::join!(relay, partners)` waits for both to finish what they're doing.
3. **The handler matches on `event.data::<OrderReadyV1>()`**: not ours (`None`) is fine, unreadable is `Skip`, and a database error saving the delivery is `Retry`.
4. **`let okada = &okada;` inside the closure**: the closure is called once per event, and each `async move` block borrows Okada for as long as that one event takes. `consume` doesn't return until it stops, so the borrow is always valid.

The receipts worker is gone from the worker's list of jobs; part 4 sends receipts from the notifications service.

## The Rust in this part
<!-- bite: a1535bfc-4252-4491-a46e-9ae7561bf49f -->

1. **`tokio::select!`** with a pinned `shutdown` future: wait for whichever finishes first, the next message or the signal to stop. `tokio::pin!` lets the same future be polled again on every loop.
2. **`StreamExt::next()`** on async-nats's message stream: the next message, or `None` when the stream ends.
3. **`tokio::time::timeout(d, fut)`**: `Err` if `fut` takes longer than `d`, and the unfinished future is dropped.
4. **`unwrap_or_else(|_| …)`** on that result: a timeout becomes `Failure::Retry`.
5. **A generic function over a closure**, `fn consume<H, Fut>(…, handle: H) where H: Fn(Envelope) -> Fut, Fut: Future<Output = …>`: any async handler fits.
6. **`#[derive(thiserror::Error)]` with `#[error("{0}")]`**: an error enum whose message is the text inside it.
7. **`1 << doublings`**: shifting left doubles a number once per step; `.min(Duration::from_secs(120))` caps it.
8. **`tokio::join!`**: waits for several futures (here, two task handles) and gives all their results.

## Your project so far
<!-- bite: 737ed89d-d71c-4e14-8493-e15bcac4846c -->

```text
mama-put/
├── contracts/
│   ├── src/stream.rs             ← NEW: STREAM, ensure_stream, Failure, Reader, consume, retry_delay
│   └── tests/consume.rs          ← NEW: a failure comes back later, a skip never does
└── src/
    ├── bin/worker.rs             ← NATS, ensure_stream, the relay, the partner-webhooks reader; no receipts
    └── webhooks/
        ├── okada.rs              ← order_ready, from an event, not from the orders service
        └── deliveries.rs         ← enqueue_once: one delivery per event id
```

## Common mistakes
<!-- bite: df631da4-3276-4beb-a94a-d4c341a85089 -->

1. **Acking before handling.** A crash mid-handler loses the event. Ack after.
2. **A plain `Nak` on failure.** The message comes straight back and hammers whatever's broken. Nak with a growing delay.
3. **Retrying what can never work.** A broken body, a deleted customer: `Term` them.
4. **A handler slower than `ack_wait`.** The server gives the message to another reader while the first is still working. Time out first.
5. **Handlers that assume order.** Two copies, retries and backoff all reorder events. Look at the event, not at what came before.
6. **A reaction that isn't safe twice.** Events can arrive again. Key the work by the event id, like `enqueue_once`.

## Check your understanding
<!-- bite: 86f3b385-43a9-482a-98b5-859ca5631089 -->

1. What's the difference between two copies of notifications sharing one durable consumer, and the worker having a consumer of its own?
2. Why does the handler's timeout (20 s) have to be shorter than `ack_wait` (30 s)?
3. Okada's endpoint is down for ten minutes. What happens to `order.ready` events, and to the API?
4. The same `order.ready` reaches the worker twice. Why does Okada still get one webhook?
5. What does `Term` do that a `Nak` doesn't, and when is each right?

<details>
<summary>Answers, after your attempt</summary>

1. Copies sharing a consumer share its messages: each event goes to one of them. A different consumer has its own progress and gets every event too.
2. If the handler were still working when `ack_wait` ran out, JetStream would give the same message to another copy, and two copies would do the same work at once. Giving up first means the message is answered (with a delayed `Nak`) before the server hands it to anyone else.
3. Nothing changes on the reader's side: it saves the delivery, which works, and acks. Lesson 17's `Sender` then fails to deliver and retries with its own backoff until Okada is back. The API doesn't notice: it wrote its events to the outbox and carried on.
4. Because the delivery is saved with the event's id, `event_id` is unique, and `ON CONFLICT (event_id) DO NOTHING` makes the second save do nothing.
5. `Term` tells the server never to deliver it again; a `Nak` asks for it again (after a delay). `Term` for what can never work (unreadable, or about something that's gone); `Nak` for what might work later.

</details>

## Practice
<!-- bite: 3c7dfa44-a60c-4a6b-9156-6ffee59bc4ce -->

1. Stop the worker, mark two orders ready, start it again, and check both deliveries appear, once each. Then look at `http://localhost:8222/jsz?consumers=true` and find `partner-webhooks`.
2. Change `max_deliver` to 3 for `partner-webhooks`, make its handler always return `Retry`, and watch a message stop coming back after three tries.
3. Feed lesson 20's kitchen screens from the stream instead of `pg_notify`: what kind of consumer suits a live screen that only wants what happens from now on? (Look up JetStream's *ordered consumers*.)

**Done when** the reader test passes against a real NATS, and an order marked ready produces exactly one Okada delivery, even when its event is read twice.

## Before moving on
<!-- bite: 8af13bbf-60dd-4926-8549-7ca857068280 -->

The stream keeps every event, and readers handle each one, retrying what might work later and dropping what never will. The worker is the first reader. The second is the reason for all of this: a service of its own that tells customers what happened to their food. Part 4 builds it.

## Related
<!-- bite: 2f81c17e-6205-48a0-92d6-48381fac52d0 -->

- [[backend/frameworks/axum/32-splitting-out-a-microservice-4|Next: Splitting Out a Microservice 4: The Notifications Service]]
- [[backend/frameworks/axum/17-payments-and-webhooks|Payments and Webhooks]] — the `Sender` that delivers what the reader saves, with its own retries
- [[backend/frameworks/axum/18-background-jobs|Background Jobs]] — stalled jobs and retries, which JetStream now does for events

## About this lesson
<!-- bite: 8d299d1c-0bab-41aa-9007-cb6b796f992f -->

**Level:** Advanced. Part 3 of 4 on splitting out a microservice, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), async-nats 0.53 and NATS Server 2.10 or later with JetStream on. Covers a stream with file storage, an age limit and a duplicate window, durable consumers shared by copies of a service, explicit acks, an ack wait with a shorter handler timeout, delayed naks with growing backoff, terminated messages, a maximum number of deliveries, one event at a time per copy with a clean stop, order not being promised, a shared reading loop that takes a closure, and Okada Riders' webhooks fed from the stream, once per event id, tested against a real NATS.
