---
id: 2e934d7e-90d2-4841-8b9f-3db6afb66e46
---

# Splitting Out a Microservice 2: Events and the Outbox

**An event is a message saying something already happened, and the outbox makes sure the change and the event saying so are saved together, in one transaction, so neither can exist without the other.**

## Before you start
<!-- bite: bddd15c9-2c28-4f16-a278-b98c0bee0515 -->

You should have finished [[backend/frameworks/axum/29-splitting-out-a-microservice-1|part 1]]: the project is a workspace with `contracts` and `notifications` beside the API. This part leans on lesson 17 (`mark_succeeded` and its transaction), lesson 18 (`jobs::add`, called inside a transaction) and lesson 20 (`announce`, also inside one).

After this part you will be able to:

1. Design events as a versioned contract, shared by every service.
2. Explain why "save, then publish" and "publish, then save" are both wrong.
3. Write events to an outbox in the same transaction as the change, with a function that can't be called any other way.
4. Relay them to NATS so that a crash never loses an event, and never doubles one in the stream.

## Where we stopped
<!-- bite: 6def20e9-a473-48d2-a271-6640e6a907eb -->

The API and notifications can't reach into each other's code or data. But when Ada pays, the API has to *tell* notifications, and anyone else who cares. The tempting code, in lesson 17's `mark_succeeded`:

```rust
tx.commit().await?;                         // Postgres: the order is paid
nats.publish("orders.paid", event).await?;  // NATS: tell everyone
```

Crash between the two lines, and the order is paid but nobody ever hears about it. Swap them, and a crash means everyone hears about a payment that was never saved. There's no transaction that covers Postgres *and* NATS.

## Terms used in this part
<!-- bite: ddb9845e-2853-49aa-80e3-ee520777a30f -->

1. **Event**: This is a message saying something **already happened**, like `order.paid`. The sender doesn't know or care who's listening.
2. **Command**: This is a message asking someone to **do** something, like "send this email". A command has a target; an event doesn't.
3. **Outbox**: This is a table where a service writes the events it wants to publish, in the same database transaction as the change itself. A separate loop then publishes them.
4. **Subject**: This is NATS's name for where a message is sent, like `orders.paid`. Subjects have parts separated by dots, and `orders.>` means "anything under `orders.`".

## Step 1: designing events
<!-- bite: e01a4b3b-0e5b-4b3f-b3bd-7133425a865b -->

An event says what happened, in the past tense, from the point of view of the service that owns the thing:

1. `order.placed`: a customer placed an order.
2. `order.paid`: an order was paid for, online or in cash.
3. `order.ready`: the kitchen marked it ready.
4. `order.collected`: it was picked up.

They live in the `contracts` crate, which both services depend on, so each shape is written once. `contracts/src/events.rs`:

```rust
//! Events: things that already happened, said by the service that owns them.

use jiff::Timestamp;
use serde::{Deserialize, Serialize, de::DeserializeOwned};
use serde_json::value::RawValue;

/// Every event, on the wire. Its `data` stays raw JSON until a reader knows the type and version.
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Envelope {
    /// Unique per event: readers use it to notice an event they've already handled.
    pub id: String,
    /// `order.paid`
    #[serde(rename = "type")]
    pub kind: String,
    /// The version of THIS type's data shape.
    pub version: i32,
    /// When it happened, not when it was sent.
    pub occurred_at: Timestamp,
    /// Which service said so: `api`.
    pub source: String,
    pub data: Box<RawValue>,
}

/// An event's data, with its type and version written once, beside its shape.
pub trait Event: Serialize + DeserializeOwned {
    const TYPE: &'static str;
    const VERSION: i32;
}

impl Envelope {
    /// The data, if this envelope holds an `E`. `None` if it's another type or version: not ours to read.
    pub fn data<E: Event>(&self) -> Option<Result<E, serde_json::Error>> {
        (self.kind == E::TYPE && self.version == E::VERSION).then(|| serde_json::from_str(self.data.get()))
    }
}

/// Where an event type is published: `order.paid` goes to `orders.paid`.
pub fn subject(kind: &str) -> String {
    format!("orders.{}", kind.strip_prefix("order.").unwrap_or(kind))
}

// Plain types only (i64, not the API's Kobo): this crate must not depend on either service.
// When it happened is the envelope's `occurredAt`.

/// A customer placed an order.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderPlacedV1 {
    pub order_id: i64,
    /// `None` for v1's anonymous orders.
    pub customer_id: Option<i64>,
    pub dish_id: i64,
    pub quantity: i32,
    pub total_kobo: i64,
}

impl Event for OrderPlacedV1 {
    const TYPE: &'static str = "order.placed";
    const VERSION: i32 = 1;
}

/// An order was paid for, online or in cash.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderPaidV1 {
    pub order_id: i64,
    pub customer_id: Option<i64>,
    pub dish_id: i64,
    pub quantity: i32,
    pub total_kobo: i64,
}

impl Event for OrderPaidV1 {
    const TYPE: &'static str = "order.paid";
    const VERSION: i32 = 1;
}

/// The kitchen marked an order ready to collect.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderReadyV1 {
    pub order_id: i64,
    pub customer_id: Option<i64>,
    pub dish_id: i64,
    pub quantity: i32,
}

impl Event for OrderReadyV1 {
    const TYPE: &'static str = "order.ready";
    const VERSION: i32 = 1;
}

/// The customer collected it.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderCollectedV1 {
    pub order_id: i64,
    pub customer_id: Option<i64>,
}

impl Event for OrderCollectedV1 {
    const TYPE: &'static str = "order.collected";
    const VERSION: i32 = 1;
}
```

1. **`Envelope`** wraps every event the same way: an id, a type, a version, when it happened, who said so, and the data.
2. **`data: Box<RawValue>`** keeps the data as raw JSON inside the envelope (serde_json's `raw_value` feature). A reader looks at `kind` and `version` first, and only then reads `data` into the right struct. One envelope type carries every kind of event.
3. **The `Event` trait** puts each type's name and version beside its shape, as constants. `envelope.data::<OrderPaidV1>()` uses them: `None` if this envelope holds something else, `Some(Ok(...))` if it's ours and reads cleanly, `Some(Err(...))` if it's ours and broken.
4. **Plain types only.** `total_kobo: i64`, not the API's `Kobo`: part 1 explained why.
5. **`customer_id: Option<i64>`**, because v1 still takes orders with no customer (lesson 12). An event states the facts, including "nobody".
6. **No timestamps in the data.** When it happened is the envelope's `occurred_at`, filled in by the outbox (step 2).

**Versions, because lesson 10 promised.** Events are an API too: other services depend on their shape, and the same rules apply. Adding a field is safe: serde ignores fields a struct doesn't have, so old readers carry on (a test in `events.rs` checks exactly that, with a `newField`). Removing or changing a field is breaking: publish `version: 2` *alongside* `version: 1` for a while, move every reader to v2, then stop publishing v1.

**How much should an event carry?** Two styles:

1. **Thin events**: just ids. `{"orderId": 42}`. Readers call back to get the rest. Always fresh, but every event causes a call.
2. **Fat events**: everything a reader might want, including copies of data. No calls needed, but you're spreading copies of data everywhere, and they go stale.

Ours sit in between: the **facts of what happened** (who, what, how much), but not copies of data that lives elsewhere and changes on its own, like the customer's email or the dish's name. Personal contact details especially don't belong in events: events are stored, replayed and read by every reader, now and in the future.

## Step 2: the outbox
<!-- bite: d1ecc653-9109-4e97-82c7-978f12a94d5a -->

The outbox writes the event to **Postgres**, in the **same transaction** as the change. Then "the order is paid" and "there's an `order.paid` to send" are committed together, or not at all. `migrations/0013_outbox.sql`:

```sql
-- Events waiting to go to NATS, written in the same transaction as the change they describe.
CREATE TABLE outbox (
  id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  type          text        NOT NULL,
  version       integer     NOT NULL,
  data          jsonb       NOT NULL,
  occurred_at   timestamptz NOT NULL DEFAULT now(),
  published_at  timestamptz
);

-- Only the ones still waiting: it stays small however many have gone out.
CREATE INDEX outbox_unpublished_idx ON outbox (occurred_at) WHERE published_at IS NULL;

-- A partner hears of each event once, however many times the event reaches us.
ALTER TABLE webhook_deliveries ADD COLUMN event_id text UNIQUE;
```

(`event_id` on webhook deliveries is for part 3.) And `src/outbox.rs` starts:

```rust
/// Writes an event into the outbox. It takes a transaction, not a pool: an event is only ever
/// recorded together with the change it describes.
pub async fn add<E: Event>(tx: &mut Transaction<'_, Postgres>, event: &E) -> Result<(), StoreError> {
    let data = serde_json::to_value(event).expect("an event is always JSON");
    sqlx::query!("INSERT INTO outbox (type, version, data) VALUES ($1, $2, $3)", E::TYPE, E::VERSION, data)
        .execute(&mut **tx)
        .await?;
    Ok(())
}
```

`add` takes a **`&mut Transaction`**, not the pool. That's the whole point, and the type system enforces it: you can't call `add` without being inside a transaction. And `E: Event` means it can only write a real event, with its type and version from the trait.

You've seen this before. Lesson 18's `jobs::add` already wrote the receipt job into Postgres inside `mark_succeeded`'s transaction, and lesson 20's `announce` sends `pg_notify` inside it too. Both were the outbox idea in small: something to do later, saved with the change. That worked because the reader (our own worker, our own API servers) read the same database. The notifications service can't, so the events have to leave Postgres, and that's the relay's job (step 4).

## Step 3: where the events are written
<!-- bite: c14b9b3a-e920-44e6-9218-fe665b8658b5 -->

In lesson 17's `mark_succeeded`, the order update now returns the order, and the event goes in beside the kitchen's news. The receipt job is gone from the API: receipts are the notifications service's job now.

```rust
        let paid = sqlx::query_as!(
            Order,
            r#"UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL
               RETURNING id, customer_id, dish_id, quantity, total_kobo AS "total: Kobo", status AS "status: Status", paid_at IS NOT NULL AS "paid!""#,
            settled.order_id
        )
        .fetch_optional(&mut *tx)
        .await?;
        let Some(paid) = paid else {
            tx.commit().await?;
            return Ok(Outcome::OrderWasAlreadyPaid);
        };
        // Paid, every other service told (the receipt is the notifications service's job now),
        // and the kitchen told: all of it, or (if anything here fails) none.
        outbox::add(&mut tx, &paid_event(&paid)).await?;
        // And the kitchen hears of it, at the moment it's true.
        let order = kitchen::order_for_kitchen(&mut tx, settled.order_id).await?;
        kitchen::announce(&mut tx, &KitchenEvent::Paid { order }).await?;
```

The cash path, lesson 17's `mark_paid` in the orders store, writes the same event through the same helper:

```rust
/// `order.paid`, for an order that's just been paid: in cash here, or online in `payments`.
pub fn paid_event(order: &Order) -> OrderPaidV1 {
    OrderPaidV1 {
        order_id: order.id,
        customer_id: order.customer_id,
        dish_id: order.dish_id,
        quantity: order.quantity,
        total_kobo: order.total.0,
    }
}
```

Placing an order adds `order.placed` beside the stock announcement:

```rust
        // And every other service, through the outbox.
        let placed = OrderPlacedV1 {
            order_id: order.id,
            customer_id: order.customer_id,
            dish_id,
            quantity,
            total_kobo: order.total.0,
        };
        outbox::add(&mut tx, &placed).await?;
```

And a status change adds `order.ready` or `order.collected`, inside the transaction lesson 20 gave it:

```rust
            let (order_id, customer_id) = (order.id, order.customer_id);
            match order.status {
                Status::Ready => {
                    let ready = OrderReadyV1 { order_id, customer_id, dish_id: order.dish_id, quantity: order.quantity };
                    outbox::add(&mut tx, &ready).await?;
                }
                Status::Collected => outbox::add(&mut tx, &OrderCollectedV1 { order_id, customer_id }).await?,
                Status::Pending => {}
            }
        }
```

That last one replaced something. Lesson 17 told Okada Riders about a ready order through an `OrderEvents` trait, called by `OrderService::set_status` **after** the status change had committed: the same gap as above, one step removed. The trait is gone, and `OrderService::new` no longer takes it. Okada hears from the stream now (part 3), and `set_status` ends:

```rust
        // Whoever cares hears of it through the outbox, written in the same transaction.
        self.store.set_status(id, to, &earlier).await?.ok_or(OrderError::BadStatusChange { from: order.status, to })
    }
```

Look at what changed in the services: nothing to remember after a change. The old code had a list ("queue the receipt, tell Okada"), and each forgotten line was a bug. Now a change records one event, and everything that cares reads it. Adding a new reaction to "order ready" doesn't touch the orders code at all.

## Step 4: the relay
<!-- bite: 850908c0-1830-497f-ad76-25bb7ec745b4 -->

Something must move events from the outbox to NATS. That's the **relay**, the rest of `src/outbox.rs`:

```rust
/// Moves events from the outbox to the ORDERS stream.
pub struct Relay {
    pub pool: PgPool,
    pub js: jetstream::Context,
}

impl Relay {
    /// Publishes up to 100 waiting events, oldest first, and says how many.
    pub async fn run_once(&self) -> Result<usize, RelayError> {
        let mut tx = self.pool.begin().await?;
        // SKIP LOCKED: two relays (two workers) take different rows, never the same one.
        let waiting = sqlx::query!(
            r#"SELECT id::text AS "id!", type AS kind, version, data,
                      (extract(epoch FROM occurred_at) * 1000000)::bigint AS "micros!"
               FROM outbox WHERE published_at IS NULL
               ORDER BY occurred_at, id
               LIMIT 100
               FOR UPDATE SKIP LOCKED"#
        )
        .fetch_all(&mut *tx)
        .await?;

        for event in &waiting {
            let envelope = Envelope {
                id: event.id.clone(),
                kind: event.kind.clone(),
                version: event.version,
                occurred_at: Timestamp::from_microsecond(event.micros)?,
                source: "api".into(),
                data: RawValue::from_string(event.data.to_string())?,
            };
            // The event's own id as the message id: if we publish it again (a crash before COMMIT),
            // JetStream drops the copy.
            let message = PublishMessage::build().payload(serde_json::to_vec(&envelope)?.into()).message_id(&event.id);
            // The first await sends it; the second waits for JetStream to say it's stored.
            self.js.send_publish(subject(&event.kind), message).await?.await?;
            sqlx::query!("UPDATE outbox SET published_at = now() WHERE id = ($1::text)::uuid", event.id).execute(&mut *tx).await?;
        }
        tx.commit().await?;
        Ok(waiting.len())
    }

    /// Relays until `shutdown` finishes: straight on while there's a backlog, resting when there's nothing.
    pub async fn run(self, shutdown: impl Future<Output = ()>) {
        tokio::pin!(shutdown);
        loop {
            let rest = match self.run_once().await {
                Ok(0) => Duration::from_millis(500),
                Ok(_) => Duration::ZERO,
                Err(e) => {
                    tracing::error!(cause = %e, "outbox relay failed; will try again");
                    Duration::from_secs(2)
                }
            };
            tokio::select! {
                _ = &mut shutdown => return,
                _ = tokio::time::sleep(rest) => {}
            }
        }
    }
}
```

Read it closely; every line matters:

1. **`FOR UPDATE SKIP LOCKED`**: run the worker twice, and each relay takes different rows, never the same one. Lesson 18's job tables use the same trick.
2. **`ORDER BY occurred_at, id`**: oldest first, so events go out roughly in the order they happened.
3. **Two `.await`s on `send_publish`.** The first sends the message. The second waits for JetStream's reply that it's **stored**. If that doesn't come, `?` returns the error, the transaction rolls back, and the rows are tried again next time.
4. **`.message_id(&event.id)`** sets a header, `Nats-Msg-Id`, to the event's own id. JetStream remembers recent ids (the stream's *duplicate window*, 10 minutes, part 3) and **drops** a second message with the same id. So if the relay publishes, then crashes before `COMMIT`, the rows are still unpublished, get published again next time, and JetStream throws the copies away.
5. **The timestamp leaves Postgres as microseconds.** sqlx in this project has no date-time feature, so the query turns `occurred_at` into a number, and `Timestamp::from_microsecond` turns it back.
6. **`run` rests 500 ms when there's nothing to send**, goes straight on while there's a backlog, and waits 2 seconds after an error. It stops when `shutdown` finishes, between batches.

The worker runs it beside its jobs (part 3 shows the whole change):

```rust
    let relay = tokio::spawn(Relay { pool: pool.clone(), js: js.clone() }.run(stopping()));
```

### Proving it

`tests/events.rs` runs against a real NATS (and does nothing when `NATS_URL` isn't set):

```rust
#[sqlx::test]
async fn each_event_reaches_the_stream_once_even_if_published_twice(pool: PgPool) {
    let Some(js) = nats().await else { return };
    let app = TestApp::new(pool.clone()).await;
    let ada = app.user("ada@example.com", "customer").await;
    let order = app.order(&ada, app.dish("Jollof rice", 1500, 40).await).await;
    let started = app.post(&format!("/v2/orders/{order}/payments")).bearer(&ada).send().await;
    let reference = started.body["data"]["reference"].as_str().unwrap();
    app.payments.settle(reference, Seen { succeeded: true, amount: Kobo(150000), currency: "NGN".into() }).await.unwrap();

    let relay = Relay { pool: pool.clone(), js: js.clone() };
    assert_eq!(relay.run_once().await.unwrap(), 2, "order.placed and order.paid");
    assert_eq!(relay.run_once().await.unwrap(), 0, "nothing left");
    let ids: Vec<String> = sqlx::query_scalar!(r#"SELECT id::text AS "id!" FROM outbox"#).fetch_all(&pool).await.unwrap();

    // A pretend crash after publishing, before COMMIT: the rows look unpublished again.
    sqlx::query!("UPDATE outbox SET published_at = NULL").execute(&pool).await.unwrap();
    assert_eq!(relay.run_once().await.unwrap(), 2, "published again...");
    let copies = copies_in_stream(&js, &ids).await;
    assert!(copies.values().all(|n| *n == 1), "...but JetStream kept one copy of each: {copies:?}");
}
```

It pays for an order, relays (two events: placed and paid), then makes the rows look unpublished again, as if the relay had crashed before `COMMIT`, and relays again. Then it reads the stream and counts each event's copies. It passes: two publishes of each event, and **one** copy of each in the stream.

The dedupe only works inside the duplicate window, so a relay that's been down for an hour can still send a copy. That's why readers must cope with duplicates anyway (part 3). The window makes duplicates rare; the reader makes them harmless.

## The Rust in this part
<!-- bite: edf31459-774f-475d-958e-8f96d9d63e28 -->

1. **A trait with associated constants**, `trait Event { const TYPE: &'static str; const VERSION: i32; }`: each implementation fills them in, and generic code reads `E::TYPE`.
2. **`Box<RawValue>`** (serde_json's `raw_value` feature): JSON kept as its exact text, to read later once you know the type.
3. **`bool::then(|| …)`**: `Some(closure result)` if true, `None` if false; `data::<E>()` uses it to read only its own type.
4. **A function that only accepts a transaction**, `add(tx: &mut Transaction<'_, Postgres>, …)`: the type makes "in the same transaction" impossible to forget. `&mut **tx` reaches the connection inside it.
5. **`.await?.await?`**: `send_publish` returns a future that, once awaited, gives *another* future, for the server's acknowledgement.
6. **`#[serde(rename = "type")]`**: `type` is a Rust keyword, so the field is `kind`, written as `type` in JSON. (`r#type` is the other way, used in the tests.)

## Your project so far
<!-- bite: 8bea665c-4f58-460b-aba6-896b88182ed3 -->

```text
mama-put/
├── migrations/
│   └── 0013_outbox.sql           ← NEW: outbox; webhook_deliveries.event_id
├── contracts/src/
│   ├── lib.rs
│   └── events.rs                 ← NEW: Envelope, Event, subject, OrderPlacedV1, OrderPaidV1, OrderReadyV1, OrderCollectedV1
├── src/
│   ├── outbox.rs                 ← NEW: add (needs a transaction), Relay (SKIP LOCKED, message ids)
│   ├── payments/store.rs         ← mark_succeeded writes order.paid; no receipt job
│   ├── payments/receipts.rs      ← deleted: receipts are the notifications service's
│   ├── orders/store.rs           ← placing, cash and status changes write their events
│   └── orders/service.rs         ← no OrderEvents; nothing to call after a change
└── tests/
    ├── events.rs                 ← NEW: one copy per event in the stream, even published twice
    ├── jobs.rs                   ← a payment records one order.paid, however many settle it
    └── payments.rs               ← placed, paid and ready, in the outbox, in order
```

## Common mistakes
<!-- bite: 43703b25-2b71-41c3-abfc-021c77a845f2 -->

1. **Publishing after the commit**, or before it. A crash in between loses or invents an event. Write to the outbox in the same transaction.
2. **No message id on publish.** Every relay crash becomes a duplicate.
3. **Not waiting for JetStream's "stored".** Then a publish that never arrived is marked as sent.
4. **Personal data in events.** They're stored and read by everyone. Facts and ids; fetch contact details when you need them.
5. **Events in the services' own types.** The contracts crate must depend on neither side.

## Check your understanding
<!-- bite: a029b390-1f98-4588-b4ca-709e5e12c04a -->

1. Why are both "save, then publish" and "publish, then save" wrong?
2. What stops someone calling `outbox::add` with a plain pool connection?
3. The relay publishes three events and crashes before `COMMIT`. What happens next?
4. How were lesson 18's receipt job and lesson 20's `pg_notify` already like an outbox, and why weren't they enough here?
5. Why doesn't `order.paid` carry Ada's email address?

<details>
<summary>Answers, after your attempt</summary>

1. There's no transaction covering Postgres and NATS. A crash between the two steps either loses the event (saved, never published) or invents one (published, never saved).
2. Its type: it takes `&mut Transaction<'_, Postgres>`. A pool or a plain connection doesn't fit, so it won't compile.
3. The rows are still unpublished, so the relay publishes them again next time. They have the same `Nats-Msg-Id`, inside the 10-minute duplicate window, so JetStream drops the copies, and the stream holds each event once.
4. Both were saved inside the same transaction as the change, so they couldn't be lost or invented. But their readers read the API's own database; the notifications service can't, so the events must reach NATS, through the relay.
5. Events are kept and read by every reader, now and later, and an email address changes on its own. The event says who (`customerId`); notifications asks the API for the address when it sends.

</details>

## Practice
<!-- bite: 244fdd11-9e59-4fb6-9e4b-bde99483316f -->

1. Write a test that a status change refused by the rules (ready before paid) leaves no event in the outbox.
2. Add `order.cancelled` (version 1) to `contracts`, without writing it anywhere yet. Which crates have to be rebuilt?
3. Wake the relay with `pg_notify` from `outbox::add` instead of checking every 500 ms, the way apalis wakes its workers. Keep the timer as a backstop.

**Done when** placing, paying and marking an order ready each leave their event in the outbox, the relay test passes against a real NATS, and the API no longer has a receipt job.

## Before moving on
<!-- bite: 63085820-8b43-4c0c-8380-b44171ad6745 -->

Every event is now safe in Postgres, and the relay moves each one into NATS once. But a stream nobody reads is just a log. Part 3 sets up the stream itself, and the readers: how each service gets every event it cares about, tries again when something's down, and gives up on what can never work.

## Related
<!-- bite: 3367a317-1da0-4d99-aef1-0140ee8a1458 -->

- [[backend/frameworks/axum/31-splitting-out-a-microservice-3|Next: Splitting Out a Microservice 3: Streams and Readers]]
- [[backend/frameworks/axum/17-payments-and-webhooks|Payments and Webhooks]] — the transaction the outbox joins
- [[backend/frameworks/axum/18-background-jobs|Background Jobs]] — jobs added inside a transaction, the outbox in small
- [[backend/frameworks/axum/10-versioning|Versioning]] — the rules events follow too

## About this lesson
<!-- bite: d7b10075-6483-4f6c-ada2-6c2e9ff73ecf -->

**Level:** Advanced. Part 2 of 4 on splitting out a microservice, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), async-nats 0.53 and sqlx 0.9. Covers events as a versioned contract in a shared crate, an envelope with raw JSON data, thin and fat events, why publishing beside a commit loses or invents events, the outbox written in the same transaction through a function that only takes a transaction, where each event is written, removing the after-commit `OrderEvents` hook, and a relay with `FOR UPDATE SKIP LOCKED`, JetStream's stored acknowledgement and message ids for deduplication, tested against a real NATS.
