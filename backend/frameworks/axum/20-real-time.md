---
id: be009213-6a51-4800-b9b7-918c354907a0
---

# Real-time Updates

**Real-time updates means the server tells the client the moment something changes, instead of the client asking again and again.** The kitchen screen at Mama Put shouldn't ask "any new orders?" every few seconds all day; it should be *told* when an order is paid. The usual tools are **server-sent events (SSE)**, one long HTTP response that the server keeps adding to, and **WebSockets**, a connection both sides can talk on. Axum has both built in.

## Before you start
<!-- bite: e015e14a-69c5-4733-bdb8-90f481d82056 -->

You should have:

1. Finished [[backend/frameworks/axum/19-caching|lesson 19]], so `cargo test` runs 65 tests.
2. A browser, if you want to watch the stream with a few lines of JavaScript (step 9). `curl` is enough otherwise.

After this lesson you will be able to:

1. Choose between polling, SSE and WebSockets for a feature.
2. Stream server-sent events from Axum, with a snapshot first and a heartbeat.
3. Pass events to many screens with a broadcast channel, and cut off a screen that can't keep up.
4. Tell every copy of the app about an event with Postgres's `NOTIFY`, sent in the same transaction as the change.
5. Let a browser open a stream without putting its token in the URL.
6. Write a WebSocket handler, and test both kinds of stream.

## Where we stopped
<!-- bite: 06ed329c-d40f-4c41-8523-94198367b82d -->

The kitchen has a tablet on the wall. Right now its page would have to ask `GET /v2/orders?status=pending` every few seconds: hundreds of requests an hour, nearly all answering "nothing new", and still up to a few seconds late. And Ada, waiting at home, keeps opening her order to see if it's ready yet.

Mama wants the screen to show each paid order the moment it's paid, and Ada's app to change to "ready" the moment the cook taps it.

## The kid version
<!-- bite: a0cdd442-58f5-45bd-9512-094a5c454738 -->

At a busy buka, there are two ways to know when your food is ready. You can keep walking up to the counter: "is mine ready? is mine ready?" That's polling. Or Mama can call out your name when it's done. That's real-time.

Calling out works because everyone waiting is in the room, listening. On the internet, "in the room" means a connection kept open: the screen connects once, and stays connected, and the server speaks down it whenever there's news.

**Where the picture stops working.** In the buka, everyone hears Mama at once. A server with three copies has three rooms, and a payment that lands in one room must be heard in all three. Step 6 is how.

## Terms used in this lesson
<!-- bite: 2ec64f2f-41c8-47a9-83e1-78addabdeb7e -->

1. **Polling**: This is the client asking again and again on a timer. Simple, wasteful, and always a little late.
2. **Server-sent events (SSE)**: This is one HTTP response that never finishes. The server writes a small text **event** into it whenever there's news, and the browser's `EventSource` reads each one as it comes, and reconnects by itself if the connection drops.
3. **WebSocket**: This is a connection that starts as an HTTP request, then **upgrades** into a two-way channel where both sides can send messages at any time.
4. **Heartbeat** (or **keep-alive**): This is a tiny message sent now and then on a quiet connection, so proxies along the way don't decide it's dead and close it.
5. **Snapshot**: This is the full current state, sent first when a screen connects, so it never depends on having heard every event before.
6. **Broadcast channel**: This is a Tokio channel where every message sent is copied to every receiver.
7. **`NOTIFY` and `LISTEN`**: These are Postgres's messages. `NOTIFY` sends one on a named channel when its transaction commits; every connection that ran `LISTEN` on that channel receives it.
8. **Stream ticket**: This is a short-lived, one-use code that lets a browser open a stream without putting its access token in the URL.

## Step 1: choosing
<!-- bite: f54e2f0c-ff2c-4ba8-9528-b098df315dee -->

| | Direction | Plain HTTP all the way | Reconnects by itself | Good for |
|---|---|---|---|---|
| Polling | client asks | yes | not needed | rare checks ("every 5 minutes") |
| **SSE** | server → client | **yes** | **yes** (`EventSource`) | feeds, dashboards, "your order is ready" |
| **WebSocket** | both ways | upgrades after the first request | you write it | chat, games, editing together, and phones that want one connection for everything |

The kitchen screen only *listens*. When a cook taps "ready", that's an ordinary `PATCH`, which we already have. So the kitchen feed is one-way: server to screen, and that's exactly what SSE is for. It's also just HTTP, so our layers, logging, proxies and HTTPS all work on it unchanged.

For Ada's order, we'll use a WebSocket, to see the other tool too. Mobile apps often prefer WebSockets: one connection that can carry more kinds of message later, in both directions. Both are in Axum: SSE in `axum::response::sse`, WebSockets behind the `ws` feature.

## What to install
<!-- bite: a9869c93-b7f5-4eda-b5ea-10315a49056f -->

```bash
cargo add axum --features ws
cargo add tokio-stream --features sync
cargo add futures
cargo add --dev tokio-tungstenite
```

1. **`ws`** turns on Axum's WebSocket support.
2. **`tokio-stream`** has `BroadcastStream`, which turns a broadcast channel into a stream; `sync` is the feature that includes it.
3. **`futures`** moves from `[dev-dependencies]` to the real ones, for `StreamExt` in tests and handlers.
4. **`tokio-tungstenite`** is a WebSocket *client*, for tests. Axum's own WebSockets are built on the same tungstenite underneath.

No new server. Step 6 says why.

## Step 2: what an SSE response looks like
<!-- bite: 0c11638d-d1d5-4f31-ac7c-e7dc1ed549b3 -->

An SSE response is plain text, with its own content type, and it doesn't end. Here is the real kitchen stream, from `curl -N`:

```text
HTTP/1.1 200 OK
content-type: text/event-stream
cache-control: no-cache

event: snapshot
retry: 3000
data: [{"id":6,"dish":"Beans and plantain","quantity":1,"paidAt":"2026-11-22T20:24:11Z","name":"Ada"},{"id":8,"dish":"Beans and plantain","quantity":2,"paidAt":"2026-11-22T20:25:50Z","name":"Ada"}]

event: order.paid
data: {"id":9,"dish":"Beans and plantain","quantity":1,"paidAt":"2026-11-22T21:08:25Z","name":"Ada"}

:
```

Each event is a few lines, ended by a **blank line**:

1. **`event:`** names the kind of event. The browser can listen for each name separately.
2. **`data:`** is the content. We send JSON on one line.
3. **`retry:`** tells the browser how many milliseconds to wait before reconnecting after a drop.
4. A line starting with **`:`** is a comment. The browser ignores it, which makes it the perfect heartbeat. The `:` at the end is Axum's, 25 seconds after the last event.

`serde_json` never writes a raw newline in its output (a newline inside a string becomes `\n`), so each `data:` is always one line. If you ever send plain text, Axum's `Event::data` splits it into several `data:` lines for you; writing the format by hand, one newline in a dish name would break the stream.

## Step 3: the kitchen's events
<!-- bite: e147f572-ec5f-4e5b-86c9-71fc9bd105be -->

What can happen that the kitchen cares about? An order is paid, or an order's status changes. `src/kitchen/events.rs` starts:

```rust
//! Kitchen events: announced with Postgres's `NOTIFY` inside the transaction that made them true, heard by
//! every server with `LISTEN`, and passed to that server's screens through a broadcast channel.

use std::time::Duration;

use serde::{Deserialize, Serialize};
use sqlx::{PgConnection, PgPool, postgres::PgListener};
use tokio::sync::broadcast;

use crate::{db::StoreError, orders::Status};

const CHANNEL: &str = "kitchen";

/// An order as the kitchen screen shows it: what to cook, and whose name to call. Nothing else:
/// no phone number, no email, on a tablet anyone in the shop can read.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct KitchenOrder {
    pub id: i64,
    pub dish: String,
    pub quantity: i32,
    pub paid_at: String,
    /// The customer's first name, to call out. `None` for orders without an account.
    pub name: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum KitchenEvent {
    /// Paid, online or in cash: time to cook.
    #[serde(rename = "order.paid")]
    Paid { order: KitchenOrder },
    #[serde(rename = "order.status")]
    Status { id: i64, status: Status },
    /// Events may have been missed: every screen should start again from a snapshot.
    Resync,
}
```

`KitchenOrder` is the kitchen's own view of an order: what to cook, and the customer's first name to call out. No phone numbers, no emails: this is on a tablet on the wall, where anyone in the shop can read it.

`KitchenEvent` is tagged with a `type` field in its JSON: `{"type":"order.paid","order":{...}}`. (Lesson 17 found that serde's tagged enums can't skip a variant they don't know. That was Paystack's JSON, which we don't control. This is our own, both written and read by this program, so every variant is known.)

`Resync` isn't news about an order. It means "you may have missed something", and step 6 shows when it's sent.

## Step 4: the stream
<!-- bite: 3ef40b82-b177-424c-a895-6b6cc09e2a64 -->

`src/kitchen/stream.rs`:

```rust
//! `GET /v2/kitchen/stream`: server-sent events for the kitchen screen.

use std::{convert::Infallible, time::Duration};

use axum::{
    extract::State,
    http::StatusCode,
    response::sse::{Event, KeepAlive, Sse},
};
use tokio::sync::broadcast;
use tokio_stream::{Stream, StreamExt, wrappers::BroadcastStream};

use super::{Kitchen, KitchenEvent, events::open_orders, tickets::StreamTicket};
use crate::{
    auth::{Action, allows},
    http::ApiError,
};

pub(super) async fn stream(
    StreamTicket(who): StreamTicket,
    State(kitchen): State<Kitchen>,
) -> Result<Sse<impl Stream<Item = Result<Event, Infallible>>>, ApiError> {
    if !allows(who, Action::KitchenWatch, None) {
        return Err(ApiError::new(StatusCode::FORBIDDEN, "forbidden", "Not allowed", "Only the kitchen sees this."));
    }
    // Listen first, then read the snapshot: an order paid in between waits in `live` instead of being missed.
    let live = kitchen.hub.subscribe();
    let open = open_orders(&kitchen.pool).await.map_err(ApiError::internal)?;
    let snapshot = Event::default()
        .event("snapshot")
        .retry(Duration::from_secs(3)) // after a drop, the browser tries again in 3 seconds
        .json_data(&open)
        .expect("orders are always JSON");

    let events = tokio_stream::once(snapshot).chain(live_events(live)).map(Ok);
    // A comment line every 25 seconds, so proxies don't close a quiet stream.
    Ok(Sse::new(events).keep_alive(KeepAlive::new().interval(Duration::from_secs(25))))
}

/// The kitchen's events as SSE, until this screen falls behind or a resync is called for. Then the
/// stream ends, the browser reconnects by itself, and the new connection starts with a fresh snapshot.
pub(super) fn live_events(live: broadcast::Receiver<KitchenEvent>) -> impl Stream<Item = Event> {
    BroadcastStream::new(live).map_while(|got| match got {
        Ok(KitchenEvent::Paid { order }) => Some(Event::default().event("order.paid").json_data(order).expect("JSON")),
        Ok(KitchenEvent::Status { id, status }) => {
            Some(Event::default().event("order.status").json_data(serde_json::json!({"id": id, "status": status})).expect("JSON"))
        }
        Ok(KitchenEvent::Resync) => None,
        Err(lagged) => {
            tracing::warn!(%lagged, "a kitchen screen fell behind; it will reconnect");
            None
        }
    })
}
```

Read it top to bottom.

1. **`StreamTicket(who)`** is who's asking (step 7), and `KitchenWatch` is a new row in lesson 13's policy, for staff and admins only.
2. **Subscribe first, then read the snapshot.** If we read the snapshot first and subscribed second, an order paid in the instant between would be in neither. Subscribed first, any event in that instant waits in `live` until the snapshot has been sent.
3. **The snapshot comes first, on every connection.** Including every *reconnection*: the tablet's Wi-Fi drops for 20 seconds, two orders are paid, `EventSource` reconnects, and the snapshot has them. The screen throws away what it had and draws the snapshot. It never has to have heard every event.
4. **`Sse::new(events)`** takes any stream of events, and writes each one as it comes. **`KeepAlive`** sends the `:` comment when nothing else has been sent for 25 seconds. Proxies and load balancers close connections that have been quiet for a while (often 60 seconds); a quiet kitchen at 3pm would be cut off again and again without it.
5. **`tokio_stream::once(snapshot).chain(...)`**: one event, then all the live ones. `.map(Ok)` wraps each in `Ok`, because `Sse` takes a stream of `Result`s. Ours never fail, so the error type is `Infallible`, the type with no values.

There's nothing to do when the screen goes away. When the tablet closes the connection, hyper drops the response body, which drops the stream, which drops the `BroadcastStream`, which drops the receiver and unsubscribes it. Go's version needed a `select` loop and a deferred unsubscribe; here, the whole clean-up is `Drop`.

And nothing to change in our layers. Lesson 7's 10-second timeout covers the time until a response *starts*, not how long its body takes, so it doesn't cut streams. I checked by holding one open for 30 seconds:

```text
event: order.paid
data: {"id":9,...}

:
```

the `:` arriving at 25 seconds, and the stream still open. (Lesson 15's idempotency layer must never be on a stream, because it collects the whole answer before sending any. It isn't: it's only on v2's order and payment routes.)

## Step 5: the hub, and screens that can't keep up
<!-- bite: 1102b07f-555a-4de7-9a69-bfa48a0afcd4 -->

Every screen connected to this server needs every event. That's a **broadcast channel**: `tokio::sync::broadcast`, where each message sent is copied to every receiver. In `events.rs`:

```rust
/// This server's screens. Each one subscribes; every event is copied to all of them.
#[derive(Clone)]
pub struct Hub(broadcast::Sender<KitchenEvent>);

impl Hub {
    /// Room for 64 events per screen. A screen that falls further behind is cut off (it reconnects).
    pub fn new() -> Self {
        Hub(broadcast::channel(64).0)
    }

    pub fn subscribe(&self) -> broadcast::Receiver<KitchenEvent> {
        self.0.subscribe()
    }

    /// Passes an event to every screen on this server. Nobody listening is fine.
    pub fn send(&self, event: KitchenEvent) {
        let _ = self.0.send(event);
    }

    /// How many screens are connected to this server.
    pub fn screens(&self) -> usize {
        self.0.receiver_count()
    }
}

impl Default for Hub {
    fn default() -> Self {
        Hub::new()
    }
}
```

`broadcast::channel(64)` keeps the last 64 events. A screen that reads slower than events arrive falls behind, and when it's more than 64 behind, its next read gets `Err(Lagged(n))`: "you missed `n` events". The sender never waits for anyone: one tablet on terrible Wi-Fi can't hold up the others.

What should a lagging screen do? It has missed events, so its picture is wrong. `live_events` ends its stream:

```rust
/// The kitchen's events as SSE, until this screen falls behind or a resync is called for. Then the
/// stream ends, the browser reconnects by itself, and the new connection starts with a fresh snapshot.
pub(super) fn live_events(live: broadcast::Receiver<KitchenEvent>) -> impl Stream<Item = Event> {
    BroadcastStream::new(live).map_while(|got| match got {
        Ok(KitchenEvent::Paid { order }) => Some(Event::default().event("order.paid").json_data(order).expect("JSON")),
        Ok(KitchenEvent::Status { id, status }) => {
            Some(Event::default().event("order.status").json_data(serde_json::json!({"id": id, "status": status})).expect("JSON"))
        }
        Ok(KitchenEvent::Resync) => None,
        Err(lagged) => {
            tracing::warn!(%lagged, "a kitchen screen fell behind; it will reconnect");
            None
        }
    })
}
```

`map_while` passes items on until its closure returns `None`, and then the stream ends. For `Lagged` and for `Resync`, the stream ends, the connection closes, `EventSource` reconnects after the 3 seconds `retry` asked for, and the new connection starts with a fresh snapshot. A screen that falls behind gets cut off and catches up; it never shows a wrong picture.

## Step 6: more than one server, with Postgres
<!-- bite: 54cd0dd9-11d2-4966-b39e-1d0b0c1f8acd -->

So far, the hub knows only its own server's screens. Now think about two servers behind a load balancer:

1. The kitchen tablet is connected to **server A**.
2. Paystack's webhook for Ada's payment lands on **server B**.
3. Server B marks the order paid. Its hub has no screens. The tablet, on A, hears nothing.

The news must go through something every server shares. The other subjects in this vault use Redis's publish/subscribe for this. We have something already shared that can do it: **Postgres**. `NOTIFY kitchen, '...'` sends a message to every connection that has run `LISTEN kitchen`. And there's one property Redis can't give us: **a `NOTIFY` inside a transaction is sent when the transaction commits, and never if it rolls back.** The kitchen can't hear about a payment that didn't happen.

Sending, in `events.rs`:

```rust
/// Tells everyone listening, when the transaction `conn` is in commits. Never, if it rolls back.
pub async fn announce(conn: &mut PgConnection, event: &KitchenEvent) -> Result<(), StoreError> {
    let payload = serde_json::to_string(event).expect("an event is always JSON");
    sqlx::query!("SELECT pg_notify($1, $2)", CHANNEL, payload).execute(conn).await?;
    Ok(())
}

/// One paid order, as the kitchen sees it.
pub async fn order_for_kitchen(conn: &mut PgConnection, order_id: i64) -> Result<KitchenOrder, StoreError> {
    let order = sqlx::query_as!(
        KitchenOrder,
        r#"SELECT o.id, d.name AS dish, o.quantity,
                  to_char(o.paid_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS "paid_at!",
                  split_part(u.name, ' ', 1) AS name
           FROM orders o JOIN dishes d ON d.id = o.dish_id LEFT JOIN users u ON u.id = o.customer_id
           WHERE o.id = $1"#,
        order_id
    )
    .fetch_one(conn)
    .await?;
    Ok(order)
}
```

`pg_notify($1, $2)` is the function form of `NOTIFY`, which takes its channel and message as parameters. (A message must be under 8,000 bytes; one order's view is about a hundred.)

Each door that pays an order or changes its status announces it **in its own transaction**. In `mark_succeeded` (lessons 17 and 18), after the receipt job:

```rust
        // Paid, the receipt on its way and the kitchen told: all of it, or (if anything here fails) none.
        jobs::add(&mut tx, &SendReceipt { payment_id: settled.id }).await?;
        // And the kitchen hears of it, at the moment it's true.
        let order = kitchen::order_for_kitchen(&mut tx, settled.order_id).await?;
        kitchen::announce(&mut tx, &KitchenEvent::Paid { order }).await?;
        tx.commit().await?;
```

So one payment's transaction now holds four things: the payment settled, the order paid, the receipt job, and the kitchen's news. All of them, or none. `PgOrderStore::mark_paid` (cash) does the same, and `set_status` now runs in a transaction so it can too:

```rust
        if let Some(order) = &order {
            // Heard by every screen when this commits, and never if it doesn't.
            kitchen::announce(&mut tx, &KitchenEvent::Status { id: order.id, status: order.status }).await?;
        }
```

The worker's hourly payment check (lesson 18) settles through the same `mark_succeeded`, so its payments reach the kitchen too, with no extra code: the worker's `NOTIFY` goes to the same Postgres, and every API server is listening.

Listening, once per server:

```rust
/// Listens for kitchen events from every server (and the worker), and passes them to `hub`.
/// One connection per server, however many screens. Runs for as long as the program does.
pub async fn listen(pool: PgPool, hub: Hub) {
    loop {
        let mut listener = match PgListener::connect_with(&pool).await {
            Ok(listener) => listener,
            Err(e) => {
                tracing::error!(cause = %e, "can't listen for kitchen events; trying again");
                tokio::time::sleep(Duration::from_secs(1)).await;
                continue;
            }
        };
        if let Err(e) = listener.listen(CHANNEL).await {
            tracing::error!(cause = %e, "can't listen for kitchen events; trying again");
            tokio::time::sleep(Duration::from_secs(1)).await;
            continue;
        }
        loop {
            match listener.try_recv().await {
                Ok(Some(note)) => match serde_json::from_str(note.payload()) {
                    Ok(event) => hub.send(event),
                    Err(e) => tracing::warn!(cause = %e, "a kitchen event we can't read"),
                },
                // The connection dropped, and has been remade: anything sent meanwhile is lost.
                Ok(None) => {
                    tracing::warn!("kitchen listener reconnected; screens will reload");
                    hub.send(KitchenEvent::Resync);
                }
                Err(e) => {
                    tracing::error!(cause = %e, "kitchen listener failed; starting again");
                    hub.send(KitchenEvent::Resync);
                    break;
                }
            }
        }
    }
}
```

and in `main`:

```rust
    // This server's screens, and one Postgres connection listening for every server's kitchen events.
    let kitchen = Kitchen { hub: Hub::new(), pool: pool.clone() };
    tokio::spawn(kitchen::listen(pool.clone(), kitchen.hub.clone()));
```

(`Kitchen` holds the hub and the pool, and is in `AppState`, so the handlers can reach both.)

The design keeps Postgres connections fixed: **one** `LISTEN` per server, however many screens are watching. Each screen is just a receiver on the hub. A hundred screens don't mean a hundred database connections.

`PgListener` holds a connection of its own (a listening connection can't go back to the pool). `try_recv` gives each notification as it comes, and if the connection drops, sqlx makes a new one and `LISTEN`s again before answering `Ok(None)`: "I'm back, but anything sent meanwhile is gone". That's exactly when screens may have missed something, so we send `Resync`, every stream ends, and every screen reconnects to a fresh snapshot. I tested it by killing the listener's connection from `psql`:

```bash
psql "$DATABASE_URL" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query ILIKE 'LISTEN%'"
```

```text
WARN mama_put::kitchen::events: kitchen listener reconnected; screens will reload
```

The open stream ended, the next one began with a snapshot, and a cash payment a moment later arrived as `order.paid` on the new connection.

That's the rule for any live feed: **the live feed is a convenience on top of the truth, never the truth itself.** The truth is the snapshot, read from Postgres. Events make the screen quick; the snapshot makes it right.

## Step 7: logging in from a browser stream
<!-- bite: e284719d-6c50-4d5b-a615-71d527286823 -->

Here's a snag. Every route uses `Authorization: Bearer <token>`. A browser's `EventSource` **can't send headers**: its only option is `new EventSource(url)`. The browser's `WebSocket` can't either.

Three ways out:

1. **Put the access token in the URL**: `?token=eyJ...`. Don't. URLs end up in proxy logs and browser history, and the token is a key to the account for 15 minutes.
2. **Use a fetch-based SSE library** in the browser, which can send headers. It works; you lose `EventSource`'s built-in reconnecting unless the library rebuilds it. And it doesn't help WebSockets.
3. **A short-lived, one-use stream ticket.** The page asks for a ticket with its normal token, then opens the stream with the ticket.

We'll do 3: it keeps `EventSource`, works for WebSockets too, and keeps tokens out of URLs. The tickets live in Postgres, `migrations/0011_stream_tickets.sql`:

```sql
-- One-use tickets for opening a live stream, because a browser's EventSource and WebSocket can't send
-- an Authorization header. Each lasts 30 seconds; only its hash is kept, like refresh tokens.
CREATE TABLE stream_tickets (
  ticket_hash text PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  role        text NOT NULL,
  expires_at  timestamptz NOT NULL
);
```

`src/kitchen/tickets.rs`:

```rust
/// `POST /v2/stream-tickets`: anyone logged in may have one. What it opens is checked by each stream.
pub(super) async fn issue(AuthUser(who): AuthUser, State(kitchen): State<Kitchen>) -> Result<(StatusCode, Data<TicketV2>), ApiError> {
    let mut bytes = [0u8; 32];
    getrandom::fill(&mut bytes).expect("the operating system gives random bytes");
    let ticket = hex::encode(bytes);
    sqlx::query!(
        "INSERT INTO stream_tickets (ticket_hash, user_id, role, expires_at) VALUES ($1, $2, $3, now() + interval '30 seconds')",
        hash(&ticket),
        who.user_id,
        who.role as Role
    )
    .execute(&kitchen.pool)
    .await
    .map_err(ApiError::internal)?;
    Ok((StatusCode::CREATED, Data(TicketV2 { ticket, expires_in: 30 })))
}

fn hash(ticket: &str) -> String {
    hex::encode(Sha256::digest(ticket.as_bytes()))
}

/// Whoever a `?ticket=` was issued to. Using it uses it up: a second try with the same ticket is a 401.
pub struct StreamTicket(pub Identity);

#[derive(Deserialize)]
struct TicketParam {
    ticket: String,
}

impl<S> FromRequestParts<S> for StreamTicket
where
    S: Send + Sync,
    Kitchen: FromRef<S>,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let bad = || ApiError::new(StatusCode::UNAUTHORIZED, "bad-stream-ticket", "Ticket not valid", "Ask for a new stream ticket.");
        let Query(TicketParam { ticket }) = Query::try_from_uri(&parts.uri).map_err(|_| bad())?;
        // Delete and read in one statement: two requests with one ticket can't both win.
        let found = sqlx::query!(
            r#"DELETE FROM stream_tickets WHERE ticket_hash = $1 AND expires_at > now() RETURNING user_id, role AS "role: Role""#,
            hash(&ticket)
        )
        .fetch_optional(&Kitchen::from_ref(state).pool)
        .await
        .map_err(ApiError::internal)?;
        let found = found.ok_or_else(bad)?;
        Ok(StreamTicket(Identity { user_id: found.user_id, role: found.role }))
    }
}
```

1. **Only a hash is stored**, like lesson 12's refresh tokens: a leaked table holds no usable tickets.
2. **`DELETE ... RETURNING` uses the ticket up in one statement.** Two requests with one ticket can't both get in: one deletes the row, and the other finds nothing.
3. **30 seconds** is plenty to open a stream, and little use to anyone who copies it from a log. Lesson 18's nightly cleanup deletes tickets that expired over an hour ago.
4. **Anyone logged in may have a ticket.** A ticket only says who you are; each stream checks what you may open. The kitchen stream wants `KitchenWatch`; Ada's order wants it to be hers.
5. **`Query::try_from_uri`** reads the query string inside an extractor, the way `Query<T>` would in a handler.

Our request logs show the path, not the query string (lesson 7's `request_span`), so tickets don't end up in our logs at all.

The routes, in `src/kitchen/mod.rs`:

```rust
/// What the live routes need: the hub this server's screens listen to, and the database.
#[derive(Clone)]
pub struct Kitchen {
    pub hub: Hub,
    pub pool: PgPool,
}

/// `POST /stream-tickets`, `GET /kitchen/stream` (SSE) and `GET /orders/{id}/live` (WebSocket). v2 only.
pub fn router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    Kitchen: FromRef<S>,
    OrderService: FromRef<S>,
    Keys: FromRef<S>,
{
    Router::new()
        .route("/stream-tickets", post(tickets::issue))
        .route("/kitchen/stream", get(stream::stream))
        .route("/orders/{id}/live", get(live::live))
}
```

merged into v2 in `src/lib.rs` with `.merge(kitchen::router().layer(http::no_store()))`: a ticket is a secret, and must not be kept anywhere.

## Step 8: a WebSocket for Ada's order
<!-- bite: 76b63abc-8994-41b0-8d6f-5eba718ebc85 -->

Ada's app wants one thing: her order's status, the moment it changes. `src/kitchen/live.rs`:

```rust
pub(super) async fn live(
    StreamTicket(who): StreamTicket,
    State(kitchen): State<Kitchen>,
    State(orders): State<OrderService>,
    Path(id): Path<i64>,
    upgrade: WebSocketUpgrade,
) -> Result<Response, ApiError> {
    // Listen first, then read: a change in between waits in `live` instead of being missed.
    let live = kitchen.hub.subscribe();
    let order = orders.get(id, who).await?; // someone else's order is a 404, before anything is upgraded
    Ok(upgrade.on_upgrade(move |socket| watch(socket, order, live)))
}

fn update(id: i64, status: Status, paid: bool) -> Message {
    Message::Text(json!({"id": id, "status": status, "paid": paid}).to_string().into())
}

/// From here on it's no longer HTTP: a two-way socket, until either side closes it.
async fn watch(mut socket: WebSocket, order: Order, mut live: broadcast::Receiver<KitchenEvent>) {
    let (mut status, mut paid) = (order.status, order.paid);
    if socket.send(update(order.id, status, paid)).await.is_err() {
        return;
    }
    loop {
        tokio::select! {
            event = live.recv() => {
                match event {
                    Ok(KitchenEvent::Paid { order: o }) if o.id == order.id => paid = true,
                    Ok(KitchenEvent::Status { id, status: s }) if id == order.id => status = s,
                    // Missed events: close, and the app reconnects and starts again from the real status.
                    Ok(KitchenEvent::Resync) | Err(RecvError::Lagged(_)) => return close(socket, "missed updates; reconnect").await,
                    Ok(_) => continue, // someone else's order
                    Err(RecvError::Closed) => return,
                }
                if socket.send(update(order.id, status, paid)).await.is_err() {
                    return;
                }
                if status == Status::Collected {
                    return close(socket, "collected").await; // nothing more will happen to it
                }
            }
            // The phone has nothing to say to us, but we must read to notice it leaving.
            // (Pings are answered by axum itself.)
            message = socket.recv() => match message {
                None | Some(Err(_)) | Some(Ok(Message::Close(_))) => return,
                Some(Ok(_)) => {}
            },
        }
    }
}

async fn close(mut socket: WebSocket, why: &'static str) {
    let frame = CloseFrame { code: close_code::NORMAL, reason: why.into() };
    let _ = socket.send(Message::Close(Some(frame))).await;
}
```

1. **`WebSocketUpgrade`** is an extractor: it checks the request really asks to upgrade. The handler answers with `upgrade.on_upgrade(...)`, which sends `101 Switching Protocols` and, once the connection has switched, runs `watch` with the socket.
2. **Everything that can refuse happens before the upgrade**: the ticket, and `orders.get(id, who)`, which hides Bayo's view of Ada's order as a 404 (lesson 13). Once the connection has switched, it's no longer HTTP: there's no status code left to send.
3. **After the upgrade, our layers are gone.** The 101 went through them, but the WebSocket itself is outside HTTP, so no timeout, no logging per message, no problem details. Everything `watch` needs, it must do itself.
4. **`tokio::select!`** waits for whichever comes first: an event from the hub, or a message from the phone. We must keep reading the socket even though Ada's app sends nothing, because that's how we notice it leaving, and Axum answers the phone's pings while we read.
5. **`status == Collected` closes the socket.** Nothing more will happen to the order, so we say goodbye properly with a close frame, and the task ends.
6. **`Lagged` and `Resync` close it too**, and the app reconnects and starts from the order's real status, which is the first message every connection sends. The same rule as the kitchen: start from the truth, then follow the news.

Each connected socket is a task waiting on two things, so ten thousand of them cost a little memory each, and no threads.

## Step 9: the screen's side
<!-- bite: f5ee0996-c772-4f74-9aca-23a012a122d6 -->

The kitchen page, in the browser, is a few lines:

```js
const { data } = await fetch("/v2/stream-tickets", {
  method: "POST", headers: { Authorization: `Bearer ${token}` },
}).then((r) => r.json());

const stream = new EventSource(`/v2/kitchen/stream?ticket=${data.ticket}`);
stream.addEventListener("snapshot", (e) => draw(JSON.parse(e.data)));
stream.addEventListener("order.paid", (e) => add(JSON.parse(e.data)));
stream.addEventListener("order.status", (e) => remove(JSON.parse(e.data).id));
```

One catch: when `EventSource` reconnects by itself, it uses the same URL, with a ticket that's already used up, and gets a 401. So the page listens for `error`, closes the stream, gets a new ticket and opens a new one. That's the price of keeping tokens out of URLs: a few lines of reconnecting by hand.

## Step 10: testing
<!-- bite: 06e9bf25-9892-45a2-b92a-969dfad272ef -->

Lesson 16's `TestApp` now builds a `Kitchen` and starts its listener, on the test's own database, so `NOTIFY` works in tests exactly as in production. `tests/kitchen.rs` has three tests.

**Tickets**: a cook's ticket opens the kitchen stream once and then gets 401, a made-up one gets 401, and a customer's gets 403.

**The SSE stream, through the whole app**. `send` from lesson 16 reads the whole body, and a stream never finishes, so this test reads it a piece at a time:

```rust
/// The next whole event on an SSE stream (they end with a blank line), skipping keep-alive comments.
async fn next_event(body: &mut BodyDataStream, buffer: &mut String) -> String {
    loop {
        if let Some(end) = buffer.find("\n\n") {
            let event: String = buffer.drain(..end + 2).collect();
            if !event.starts_with(':') {
                return event;
            }
            continue;
        }
        let chunk = tokio::time::timeout(Duration::from_secs(3), body.next()).await.expect("an event within 3 s");
        buffer.push_str(std::str::from_utf8(&chunk.unwrap().unwrap()).unwrap());
    }
}
```

`into_data_stream` turns the body into a stream of chunks. The helper collects them until a blank line ends an event, skips heartbeats, and gives up after 3 seconds, so a missing event fails the test instead of hanging it. Then:

```rust
#[sqlx::test]
async fn the_kitchen_sees_a_snapshot_then_each_payment(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let cook = app.user("cook@example.com", "staff").await;
    let ada = app.user("ada@example.com", "customer").await;
    let dish = app.dish("Jollof rice", 1500, 40).await;
    let first = app.order(&ada, dish).await;
    app.post(&format!("/v2/orders/{first}/paid-in-cash")).bearer(&cook).send().await;

    let request = Request::get(format!("/v2/kitchen/stream?ticket={}", ticket(&app, &cook).await)).body(Body::empty()).unwrap();
    let response = app.router.clone().oneshot(request).await.unwrap();
    assert_eq!(response.headers()["content-type"], "text/event-stream");
    let (mut body, mut buffer) = (response.into_body().into_data_stream(), String::new());

    let snapshot = next_event(&mut body, &mut buffer).await;
    assert!(snapshot.contains("event: snapshot") && snapshot.contains(&format!("\"id\":{first}")), "{snapshot}");
    assert!(snapshot.contains("\"name\":\"Test\""), "the customer's first name, to call out");
    assert!(!snapshot.contains("ada@example.com"), "no email on the kitchen wall");

    // Another order is paid, through another door: the stream hears of it.
    let second = app.order(&ada, dish).await;
    app.post(&format!("/v2/orders/{second}/paid-in-cash")).bearer(&cook).send().await;
    let paid = next_event(&mut body, &mut buffer).await;
    assert!(paid.contains("event: order.paid") && paid.contains(&format!("\"id\":{second}")), "{paid}");

    app.patch(&format!("/v2/orders/{second}/status")).bearer(&cook).json(json!({"status": "ready"})).send().await;
    let ready = next_event(&mut body, &mut buffer).await;
    assert!(ready.contains("event: order.status") && ready.contains("\"status\":\"ready\""), "{ready}");
}
```

That's the whole path: an order paid in cash, a `NOTIFY` in its transaction, the listener, the hub, the stream.

**The WebSocket, on a real port.** `oneshot` can't upgrade a connection, so this test runs the app with `axum::serve` on `127.0.0.1:0` and connects with tokio-tungstenite, as a phone would:

```rust
    // A WebSocket needs a real connection, so this test runs the app on a real port.
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let router = app.router.clone();
    tokio::spawn(async move { axum::serve(listener, router).await.unwrap() });
    let url = |t: &str| format!("ws://{address}/v2/orders/{order}/live?ticket={t}");

    let not_hers = tokio_tungstenite::connect_async(url(&ticket(&app, &bayo).await)).await;
    let refused = not_hers.expect_err("Bayo can't watch Ada's order");
    assert!(refused.to_string().contains("404"), "{refused}");

    let (mut socket, _) = tokio_tungstenite::connect_async(url(&ticket(&app, &ada).await)).await.unwrap();
    let mut next = async || -> Value {
        let message = tokio::time::timeout(Duration::from_secs(3), socket.next()).await.unwrap().unwrap().unwrap();
        serde_json::from_str(message.to_text().unwrap()).unwrap()
    };
    assert_eq!(next().await, json!({"id": order, "status": "pending", "paid": false}));

    app.post(&format!("/v2/orders/{order}/paid-in-cash")).bearer(&cook).send().await;
    assert_eq!(next().await, json!({"id": order, "status": "pending", "paid": true}));
    app.patch(&format!("/v2/orders/{order}/status")).bearer(&cook).json(json!({"status": "collected"})).send().await;
    assert_eq!(next().await, json!({"id": order, "status": "collected", "paid": true}));

    let closed = tokio::time::timeout(Duration::from_secs(3), socket.next()).await.unwrap().unwrap().unwrap();
    assert!(matches!(closed, Message::Close(_)), "nothing more will happen, so the server closes it");
```

`async ||` is an **async closure**: a closure whose body can `.await`, and which can borrow `socket` mutably each time it's called.

There's also a unit test in `stream.rs`: a screen that never reads, sent 100 events, ends at once instead of delivering the 64 it kept. And the permissions table gets a row: `POST /v2/stream-tickets` is 401 for nobody and 201 for everyone else.

```bash
cargo test
```

69 tests, all passing.

## The Rust in this lesson
<!-- bite: 1a82808a-3064-4bfa-80e1-7df9cb522b66 -->

1. **`Sse::new(stream).keep_alive(...)`** and **`Event::default().event(...).json_data(...)`**: An SSE response from any stream of events, with heartbeats.
2. **`impl Stream<Item = ...>` in a return type**: "some stream of these", without naming its long, real type.
3. **`tokio::sync::broadcast`**: One sender, many receivers, each getting every message. A receiver too far behind gets `Lagged`; the sender never waits.
4. **`BroadcastStream`**: A broadcast receiver as a `Stream`, so stream tools work on it.
5. **`map_while`**: Passes items through until its closure returns `None`, then ends the stream.
6. **`tokio_stream::once(x).chain(rest)`**: A stream of one item, then all of another.
7. **`Infallible`**: The error type for things that can't fail. There are no values of it.
8. **Cleaning up by `Drop`**: A closed connection drops the stream, which drops the receiver, which unsubscribes it. No unsubscribe code at all.
9. **`#[serde(tag = "type")]`**: An enum written as JSON with a field saying which variant it is.
10. **`PgListener`** and **`try_recv`**: A connection that receives `NOTIFY` messages; `Ok(None)` means it reconnected and messages may have been lost.
11. **`WebSocketUpgrade`** and **`on_upgrade`**: Accept the upgrade, then run a task with the socket once it's switched.
12. **`tokio::select!` in a loop**: Wait for whichever of several things happens first, again and again.
13. **Match guards on enum variants**, `Ok(KitchenEvent::Status { id, status: s }) if id == order.id`: Match a variant and check a condition in one arm. Arms are tried in order, so the catch-all `Ok(_)` comes last.
14. **`Query::try_from_uri`**: The `Query` extractor's parsing, used by hand inside an extractor of our own.
15. **Async closures**, `async || { ... }`: A closure that can `.await` inside.

## Your project so far
<!-- bite: 414275c7-4bf3-47f0-a025-34dccd6a689e -->

```text
mama-put/
├── Cargo.toml                    ← axum "ws"; tokio-stream (sync); futures; tokio-tungstenite (dev)
├── migrations/
│   └── 0011_stream_tickets.sql   ← NEW: one-use, 30-second stream tickets (hashed)
├── src/
│   ├── main.rs                   ← a Kitchen (hub + pool) in the state; the listener task
│   ├── lib.rs                    ← kitchen routes in v2, with no_store
│   ├── kitchen/                  ← NEW
│   │   ├── mod.rs                ← Kitchen; the three routes
│   │   ├── events.rs             ← KitchenOrder, KitchenEvent, announce (NOTIFY), the Hub, listen (LISTEN), Resync
│   │   ├── stream.rs             ← GET /v2/kitchen/stream: subscribe, snapshot, live events, keep-alive
│   │   ├── live.rs               ← GET /v2/orders/{id}/live: a WebSocket per customer's order
│   │   └── tickets.rs            ← POST /v2/stream-tickets; StreamTicket, used up in one DELETE
│   ├── auth/policy.rs            ← KitchenWatch, for staff and admins
│   ├── orders/store.rs           ← set_status and mark_paid announce in their transactions
│   ├── payments/store.rs         ← mark_succeeded announces "paid" in its transaction
│   └── maintenance.rs            ← the nightly cleanup deletes old tickets
└── tests/
    ├── common/mod.rs             ← TestApp has a Kitchen and runs its listener
    ├── kitchen.rs                ← NEW: tickets, the SSE stream end to end, a real WebSocket
    └── permissions.rs            ← a row for stream tickets
```

## Common mistakes
<!-- bite: c13bad8f-629d-485c-9ed8-eaf61fdbc08a -->

1. **Reading the snapshot before subscribing.** An event in between is lost. Subscribe first.
2. **No snapshot, only events.** One missed event and the screen is wrong until someone reloads it. Start every connection from the truth.
3. **No heartbeat.** Proxies close quiet connections. Send a comment every 25 seconds.
4. **Waiting for slow screens.** One bad connection freezes everyone's feed. Let them lag, and cut them off.
5. **Announcing outside the transaction.** The kitchen hears of a payment that then rolls back. `NOTIFY` in the same transaction.
6. **Access tokens in URLs.** They end up in logs and history. Use one-use tickets.
7. **Refusing after the upgrade.** There's no status code left to send. Check everything before `on_upgrade`.
8. **Not reading a WebSocket you only write to.** You never notice the other side leave.
9. **A listener per screen.** A hundred screens, a hundred database connections. One per server, and a hub.
10. **Treating the live feed as the truth.** It's a convenience; the snapshot is the truth.

## Check your understanding
<!-- bite: 3a5cd768-4763-4da3-86b5-f1fca3b6a304 -->

1. Why is SSE right for the kitchen screen, and when would you pick a WebSocket?
2. Why does the stream subscribe to the hub *before* reading the snapshot?
3. A tablet's Wi-Fi drops for 20 seconds and two orders are paid. How does the screen end up right?
4. What happens to a screen that falls more than 64 events behind, and why not just wait for it?
5. Server B settles a payment; the tablet is on server A. Follow the news from B to the tablet.
6. Why is `NOTIFY` inside the payment's transaction better than publishing after it commits?
7. Why can't the kitchen page just send its access token, and what does the ticket fix?
8. Why must the WebSocket handler check the order belongs to Ada *before* calling `on_upgrade`?

<details>
<summary>Answers, after your attempt</summary>

1. The screen only listens, and SSE is one-way, plain HTTP, and reconnects by itself. A WebSocket is for when both sides talk, or when one connection should carry many kinds of message, as mobile apps often want.
2. So nothing falls between them. Subscribed first, an event that happens while the snapshot is being read waits in the receiver and is sent right after it.
3. `EventSource` reconnects (after the 3 seconds `retry` asked for, with a new ticket), and every connection starts with a snapshot of all open, paid orders from Postgres. The two orders are in it.
4. Its next read gets `Lagged`, its stream ends, and it reconnects to a fresh snapshot. Waiting for it would hold up every other screen on the server, because they all share one sender.
5. B's `mark_succeeded` runs `pg_notify` inside its transaction. When it commits, Postgres sends the message to every connection listening on `kitchen`, including server A's listener. A's listener passes it to A's hub, and the hub to the tablet's stream.
6. Because the message is sent only if the transaction commits. Publishing after the commit can fail or be forgotten; publishing before it can announce a payment that then rolls back. Inside the transaction, the news and the payment can't disagree.
7. `EventSource` and the browser's `WebSocket` can't send headers, and a token in the URL ends up in logs and history. A ticket is in the URL instead, but it lasts 30 seconds, works once, and is stored only as a hash.
8. Because after the upgrade the connection isn't HTTP any more, so there's no way to send a 404. Every refusal has to happen while it's still a request.

</details>

## Practice
<!-- bite: 0d22a6e0-5d35-41d2-9d83-5362c5b90e3c -->

1. Add an `order.ready` sound to the kitchen page from step 9, and make the page get a new ticket and reconnect on `error`.
2. Send the screen count, `hub.screens()`, in a log line every minute. Lesson 27 turns it into a graph.
3. Add a `customer` view to the WebSocket's messages: the dish name, read once at the start.
4. Write a test that a payment's transaction rolling back sends no `order.paid`. (Hint: call `kitchen::announce` in a transaction you roll back, and check the stream gets nothing within a second.)
5. Make the kitchen stream end after 30 minutes on purpose, so screens get a fresh snapshot now and then even if every event arrived.

**Done when** `curl -N` with a staff ticket shows a snapshot and then `order.paid` the moment an order is paid on any server; a quiet stream gets a `:` every 25 seconds; a customer's ticket gets 403; Ada's WebSocket shows her order move to collected and then closes; killing the listener's connection makes screens reload; and `cargo test` runs 69 tests and passes.

## Before moving on
<!-- bite: d4ea8150-a70c-4d02-b200-2739042786d6 -->

Part 4 is done. Mama Put takes payments and sends webhooks, does its slow work in the background, keeps the menu fast and honest, and now tells the kitchen and the customer the moment anything changes, on every server, without a single event that a rollback could make untrue.

So far every client has spoken REST. Part 5 looks at other ways to talk to the same system, starting with a phone team who'd like to ask for exactly the fields they need, in one request: GraphQL.

## Related
<!-- bite: a3c34873-4736-42f9-9299-8d87462e0456 -->

- [[backend/frameworks/axum/21-graphql|Next: GraphQL]]
- [[backend/frameworks/net-http/20-real-time|The same lesson in net/http]] — Redis pub/sub, and a hand-written select loop
- [[backend/frameworks/axum/18-background-jobs|Background Jobs]] — the other place `LISTEN`/`NOTIFY` works for us
- [[backend/frameworks/axum/12-authentication|Authentication]] — tokens, and why they stay out of URLs

## About this lesson
<!-- bite: e4ac0b55-1427-4183-9162-42f107c91e6d -->

**Level:** Advanced. Lesson 20 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8 with `ws`, tokio-stream 0.1, sqlx 0.9 and tokio-tungstenite 0.29. Covers choosing between polling, SSE and WebSockets, the SSE format, an `Sse` stream that subscribes before its snapshot, keep-alive comments, clean-up by `Drop`, a broadcast hub that cuts off lagging screens, Postgres `NOTIFY` sent inside the transaction that made the news true and one `LISTEN` per server with a resync after reconnecting, one-use hashed stream tickets, a WebSocket handler that refuses before upgrading and follows one order, the browser's side, and testing a stream through the whole app and a WebSocket on a real port.
