---
id: 96a9a11e-0af4-4a6f-9051-ef7d413292bc
---

# Splitting Out a Microservice 4: The Notifications Service

**The notifications service is a second program with its own database and its own settings: it reads `order.paid` and `order.ready` from the stream, asks the API over gRPC how to reach the customer, and sends the message once.**

## Before you start
<!-- bite: 89fdc1e8-3a84-4a98-9e72-e4fbc21c6b5a -->

You should have finished [[backend/frameworks/axum/31-splitting-out-a-microservice-3|part 3]]: the stream keeps every event, and `contracts::stream::consume` reads it. This part leans on lesson 8 (migrations), lesson 16 (`#[sqlx::test]` and fakes behind traits) and lesson 22 (gRPC with tonic).

After this part you will be able to:

1. Build a second service in the workspace, with its own database, migrations and settings.
2. Write handlers that are safe when an event arrives twice, and that say clearly what to retry and what to drop.
3. Add a gRPC service to the API for another service to call, and call it with a deadline.
4. Run the whole system and watch an event cross from one service to the other, even with one of them stopped for a while.

## Where we stopped
<!-- bite: 5226bcfc-6e94-4e8f-bea8-24fd1d74c5a1 -->

Events reach the stream once each, and the worker already reads `order.ready` for Okada. The notifications crate from part 1 still has nothing in it but its boundary test.

## Step 1: the crate
<!-- bite: 327440e8-e81c-4dde-b05a-fcccb1413b6c -->

```text
notifications/
├── Cargo.toml        ← contracts, async-nats, sqlx, tonic, tokio, tracing… never mama-put
├── .env              ← its own settings
├── sqlx.toml         ← which variable sqlx's query checks read
├── build.rs          ← the API's .proto files, as clients only
├── migrations/       ← 0001_sent_notifications.sql, 0002_preferences.sql
├── src/
│   ├── main.rs       ← the program
│   ├── lib.rs        ← the modules, and the generated gRPC clients
│   ├── handlers.rs   ← one function per kind of message
│   ├── store.rs      ← Sent, Preferences: its own tables
│   ├── api.rs        ← Customers and Menu: what it asks the API
│   └── providers.rs  ← Mailer and Sms, and console versions for development
└── tests/
    ├── handlers.rs
    └── boundary.rs   ← part 1
```

Its dependencies, from `notifications/Cargo.toml`:

```toml
[dependencies]
async-nats = "0.53"
async-trait = "0.1.92"
contracts = { version = "0.1.0", path = "../contracts" }
dotenvy = "0.15.7"
prost = "0.14.6"
serde_json = "1.0.154"
sqlx = { version = "0.9.1", features = ["runtime-tokio", "postgres", "macros", "migrate", "sqlx-toml"] }
thiserror = "2.0.21"
tokio = { version = "1.54.1", features = ["full"] }
tonic = "0.14.9"
tonic-prost = "0.14.9"
tracing = "0.1.44"
tracing-subscriber = { version = "0.3.23", features = ["env-filter"] }

[build-dependencies]
protox = "0.10"
tonic-prost-build = "0.14.9"

[dev-dependencies]
serde_json = "1.0.154"
```

### Its own settings, and a trap

`notifications/.env`:

```bash
# This service's settings. Run it from this folder, so these are the ones it reads.
DATABASE_URL=postgres://notifications@localhost:5544/mamaput_notifications
# The same database, for sqlx's compile-time checks (see sqlx.toml).
NOTIFICATIONS_DATABASE_URL=postgres://notifications@localhost:5544/mamaput_notifications
NATS_URL=nats://localhost:4222
API_GRPC_URL=http://127.0.0.1:50051
```

Run it from the `notifications` folder and these are the settings it reads. `DATABASE_URL` is *its* database, and `#[sqlx::test]` reads it too, to make each test's database.

The second line is there because of a trap I fell into. sqlx's query macros check every query against a real database while compiling, and look for `DATABASE_URL` in `.env` files from the crate's folder **up to the workspace root, with the last one read winning**. The workspace root's `.env` is the API's, so the notifications queries were checked against the API's database, and failed:

```text
error: error returned from database: relation "sent_notifications" does not exist
```

sqlx 0.9's answer is a config file per crate, `notifications/sqlx.toml` (with sqlx's `sqlx-toml` feature on):

```toml
# The query checks for THIS crate read NOTIFICATIONS_DATABASE_URL. Without this, they'd read DATABASE_URL,
# and the workspace's .env (the API's database) would win over ours.
[common]
database-url-var = "NOTIFICATIONS_DATABASE_URL"
```

Now this crate's checks read `NOTIFICATIONS_DATABASE_URL`, which only `notifications/.env` sets.

### Its own tables

`migrations/0001_sent_notifications.sql` and `0002_preferences.sql`, run by the service itself when it starts (`sqlx::migrate!()`): it's the only program that uses this database.

```sql
-- Every message sent, so the same event never sends it twice, and support can see what a customer got.
CREATE TABLE sent_notifications (
  event_id     text        NOT NULL,
  kind         text        NOT NULL,     -- 'receipt-email', 'ready-text'
  customer_id  bigint      NOT NULL,
  sent_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event_id, kind)
);
```

```sql
-- What each customer wants to hear by. No row: both, the default.
CREATE TABLE preferences (
  customer_id  bigint  PRIMARY KEY,
  emails       boolean NOT NULL DEFAULT true,
  texts        boolean NOT NULL DEFAULT true
);
```

`src/store.rs` reads and writes them:

```rust
/// Which messages have been sent.
#[derive(Clone)]
pub struct Sent {
    pool: PgPool,
}

impl Sent {
    pub fn new(pool: PgPool) -> Self {
        Sent { pool }
    }

    pub async fn was_sent(&self, event_id: &str, kind: &str) -> Result<bool, sqlx::Error> {
        sqlx::query_scalar!(
            r#"SELECT EXISTS (SELECT 1 FROM sent_notifications WHERE event_id = $1 AND kind = $2) AS "sent!""#,
            event_id,
            kind
        )
        .fetch_one(&self.pool)
        .await
    }

    /// Records a message as sent. A second record of the same one changes nothing.
    pub async fn record(&self, event_id: &str, kind: &str, customer_id: i64) -> Result<(), sqlx::Error> {
        sqlx::query!(
            "INSERT INTO sent_notifications (event_id, kind, customer_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            event_id,
            kind,
            customer_id
        )
        .execute(&self.pool)
        .await?;
        Ok(())
    }
}
```

`ON CONFLICT DO NOTHING` with the `(event_id, kind)` primary key: a message can be *recorded* only once, whatever happens.

## Step 2: asking the API
<!-- bite: b68396ce-89d6-46ff-a595-e8efa2554e81 -->

Notifications needs a customer's email and phone number, which belong to the API. It asks over gRPC, with a second service beside lesson 22's `MenuService`. `proto/mamaput/customers/v1/customers.proto`:

```proto
syntax = "proto3";

package mamaput.customers.v1;

// Contact details, for Mama Put's own services. Personal data: callers must be allowed (lesson 30).
service CustomersService {
  // How to reach one customer. NOT_FOUND if there's no such customer.
  rpc GetContact(GetContactRequest) returns (GetContactResponse);
}

message GetContactRequest {
  int64 customer_id = 1;
}

message GetContactResponse {
  string first_name = 1;
  string email = 2;
  optional string phone = 3;
}
```

The **first name**, not the full name, and nothing else: exactly what a message needs. The phone number is a new column, `migrations/0014_users_phone.sql` (`ALTER TABLE users ADD COLUMN phone text`), which customers fill in through the app. `optional` because many won't.

On the API's side, `build.rs` now compiles both `.proto` files, and `src/grpc/customers.rs` answers with one store query:

```rust
/// The `CustomersService` from `customers.proto`: how to reach a customer, for the notifications service.
#[derive(Clone)]
pub struct CustomersApi {
    pub users: PgAuthStore,
}

#[tonic::async_trait]
impl CustomersService for CustomersApi {
    async fn get_contact(&self, request: Request<GetContactRequest>) -> Result<Response<GetContactResponse>, Status> {
        let id = request.into_inner().customer_id;
        let contact = self.users.contact(id).await.map_err(|e| status(ApiError::internal(e)))?;
        let contact = contact.ok_or_else(|| Status::not_found(format!("there's no customer {id}")))?;
        // The first name and nothing else: what a message needs.
        let first_name = contact.name.split_whitespace().next().unwrap_or_default().to_owned();
        Ok(Response::new(GetContactResponse { first_name, email: contact.email, phone: contact.phone }))
    }
}
```

`grpc::serve` takes it as a second service, beside the menu, with its own health status. A test in `tests/grpc.rs` asks for Ada's contact over a real connection, and for customer 999 (`NotFound`).

`GetContact` hands personal data to anyone who can reach port 50051. On `127.0.0.1` that's only programs on the same machine, but that won't last, and it's the first thing lesson 33 fixes, with service-to-service authentication.

On notifications' side, `build.rs` generates **clients only** (`build_server(false)`) from the same `.proto` files, in `../proto`. The `.proto` files are the contract; each crate generates the half it needs. `src/api.rs` wraps them in two small traits, so the handlers can be tested with fakes (lesson 5):

```rust
/// How to reach a customer.
#[derive(Clone, Debug, PartialEq)]
pub struct Contact {
    pub first_name: String,
    pub email: String,
    pub phone: Option<String>,
}

#[async_trait]
pub trait Customers: Send + Sync {
    async fn contact(&self, customer_id: i64) -> Result<Contact, Failure>;
}

#[async_trait]
pub trait Menu: Send + Sync {
    async fn dish_name(&self, dish_id: i64) -> Result<String, Failure>;
}

/// Every call waits at most this long: the API answers in milliseconds, or it isn't answering.
const DEADLINE: Duration = Duration::from_millis(500);
```

and the real one:

```rust
#[async_trait]
impl Customers for GrpcApi {
    async fn contact(&self, customer_id: i64) -> Result<Contact, Failure> {
        let mut request = Request::new(GetContactRequest { customer_id });
        request.set_timeout(DEADLINE);
        match CustomersServiceClient::new(self.channel.clone()).get_contact(request).await {
            Ok(answer) => {
                let c = answer.into_inner();
                Ok(Contact { first_name: c.first_name, email: c.email, phone: c.phone })
            }
            // They deleted their account: they'll never come back, so don't try again.
            Err(status) if status.code() == Code::NotFound => Err(Failure::Skip(format!("customer {customer_id} is gone"))),
            Err(status) => Err(retry(status)),
        }
    }
}
```

1. **500 ms per call**, with `set_timeout`, lesson 22's deadline. The API answers in milliseconds, or it isn't answering.
2. **`NotFound` is `Skip`**: a customer who deleted their account won't come back.
3. **Anything else is `Retry`**: the API is down, restarting, or slow; it will be back.

## Step 3: the handlers
<!-- bite: 8e617f90-d36b-431a-91d8-c767d45844c3 -->

`src/handlers.rs`:

```rust
pub struct Handlers {
    pub customers: Arc<dyn Customers>,
    pub menu: Arc<dyn Menu>,
    pub sent: Sent,
    pub preferences: Preferences,
    pub mailer: Arc<dyn Mailer>,
    pub sms: Arc<dyn Sms>,
}

impl Handlers {
    pub async fn handle(&self, event: Envelope) -> Result<(), Failure> {
        if let Some(paid) = event.data::<OrderPaidV1>() {
            let paid = paid.map_err(|e| Failure::Skip(format!("unreadable order.paid: {e}")))?;
            return self.receipt(&event.id, &paid).await;
        }
        if let Some(ready) = event.data::<OrderReadyV1>() {
            let ready = ready.map_err(|e| Failure::Skip(format!("unreadable order.ready: {e}")))?;
            return self.ready_text(&event.id, &ready).await;
        }
        Ok(()) // a type or version we don't know: not for us, and that's fine
    }

    async fn receipt(&self, event_id: &str, paid: &OrderPaidV1) -> Result<(), Failure> {
        let Some(customer_id) = paid.customer_id else {
            return Ok(()); // an anonymous v1 order: nobody to tell
        };
        if self.sent.was_sent(event_id, "receipt-email").await.map_err(retry)? {
            return Ok(());
        }
        if !self.preferences.of(customer_id).await.map_err(retry)?.emails {
            return Ok(());
        }
        // Fresh from the API, at the moment of sending: never a copy kept here.
        let contact = self.customers.contact(customer_id).await?;
        let dish = self.menu.dish_name(paid.dish_id).await?;
        let what = if dish.is_empty() { format!("{} plates", paid.quantity) } else { format!("{} × {dish}", paid.quantity) };
        let text = format!("Thank you, {}! {what}, ₦{}.", contact.first_name, naira(paid.total_kobo));
        let subject = format!("Mama Put receipt for order {}", paid.order_id);
        self.mailer.send(&contact.email, &subject, &text).await.map_err(retry)?;
        // Sent, then recorded: a crash between the two sends it twice. A second receipt beats none.
        self.sent.record(event_id, "receipt-email", customer_id).await.map_err(retry)
    }

    async fn ready_text(&self, event_id: &str, ready: &OrderReadyV1) -> Result<(), Failure> {
        let Some(customer_id) = ready.customer_id else { return Ok(()) };
        if self.sent.was_sent(event_id, "ready-text").await.map_err(retry)? {
            return Ok(());
        }
        if !self.preferences.of(customer_id).await.map_err(retry)?.texts {
            return Ok(());
        }
        let contact = self.customers.contact(customer_id).await?;
        let Some(phone) = contact.phone else {
            return Ok(()); // no number, no text
        };
        let text = format!("{}, your Mama Put order {} is ready. Come and collect it!", contact.first_name, ready.order_id);
        self.sms.send(&phone, &text).await.map_err(retry)?;
        self.sent.record(event_id, "ready-text", customer_id).await.map_err(retry)
    }
}
```

1. **Each event type it knows, by `data::<E>()`**, and `Ok(())` for anything else. The API will publish events notifications doesn't care about (`order.placed`), and new versions before notifications has learned them. Ignoring them is what lets the API add events without breaking anyone.
2. **Unreadable data is `Skip`.** Retrying twenty times won't fix the JSON.
3. **`was_sent`, then send, then `record`.** If the service crashes after sending but before recording, the event comes again and the receipt is sent twice. A second receipt is better than none, and the primary key means the record itself can't be doubled. (Some email providers accept an idempotency key with each send; when yours does, pass the event id, and the provider drops the duplicate for you.)
4. **Contact details come from the API, at the moment of sending**: never from the event, never from a copy kept here.
5. **If the API is unreachable, the handler returns `Retry`.** The customer gets the receipt a little late. **That's the whole point of the split:** the API being down for a minute delays texts; texts being broken never delays orders.

The receipt says "2 × Jollof rice", so it asks the menu too, over lesson 22's `GetDish`. A dish taken off the menu since gives an empty name, and the receipt still goes, without it.

## Step 4: the program
<!-- bite: 590dfbfd-2a32-4ff2-aac4-e1e47ae6c3d8 -->

`src/main.rs`, the same shape as the API's `main` since lesson 5, building its own world:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    dotenvy::dotenv().ok();
    tracing_subscriber::fmt().with_env_filter("notifications=info,contracts=info").init();

    // Its own database: the API's is none of its business (and its user can't even connect to it).
    let pool = PgPoolOptions::new().max_connections(5).connect(&env("DATABASE_URL")?).await?;
    sqlx::migrate!().run(&pool).await?;

    let nats = async_nats::ConnectOptions::new().name("notifications").connect(env("NATS_URL")?).await?;
    let js = jetstream::new(nats.clone());
    stream::ensure_stream(&js).await?; // whichever service starts first makes it; same settings either way

    // Connected lazily: the service starts even while the API is down, and calls fail (and are retried) until it's up.
    let channel = Endpoint::from_shared(env("API_GRPC_URL")?)?.connect_timeout(Duration::from_secs(2)).connect_lazy();
    let api = Arc::new(GrpcApi::new(channel));
    let handlers = Handlers {
        customers: api.clone(),
        menu: api,
        sent: Sent::new(pool.clone()),
        preferences: Preferences::new(pool),
        mailer: Arc::new(ConsoleMailer),
        sms: Arc::new(ConsoleSms),
    };

    info!("notifications started");
    // Every copy of this service reads through the one durable consumer, so each event goes to one copy.
    let reader = Reader { durable: "notifications", subjects: &["orders.paid", "orders.ready"], max_deliver: 20 };
    stream::consume(&js, reader, stopping(), |event| handlers.handle(event)).await?;
    nats.drain().await?; // send anything still on its way, then close
    info!("notifications stopped");
    Ok(())
}

async fn stopping() {
    tokio::signal::ctrl_c().await.expect("can't listen for Ctrl+C");
}

fn env(name: &str) -> Result<String, String> {
    std::env::var(name).map_err(|_| format!("set {name}"))
}
```

1. **Its own database, migrated by itself.**
2. **`ensure_stream` here too.** Whichever service starts first makes the stream; the settings come from `contracts`, so they're the same either way.
3. **`connect_lazy`**: the service starts even while the API is down. Calls fail (and their events are retried) until it's up.
4. **`ConsoleMailer` and `ConsoleSms`** write what they would send to the log. Real providers come with real keys, and those now belong to this service alone: the API no longer holds the email provider's key at all, one more reason for the split.
5. **`nats.drain()`** before leaving: anything still on its way is sent, then the connection closes.

## Step 5: testing
<!-- bite: 50fe553a-2aa2-4629-a9a3-d2de42e1dc36 -->

`tests/handlers.rs` tests the handlers with a pretend API and pretend providers, and this service's own real database (`#[sqlx::test]`, from its `.env`):

```rust
const PAID: OrderPaidV1 = OrderPaidV1 { order_id: 42, customer_id: Some(7), dish_id: 1, quantity: 2, total_kobo: 300000 };

#[sqlx::test]
async fn a_paid_order_gets_one_receipt_however_often_the_event_comes(pool: PgPool) {
    let s = setup(pool);
    s.handlers.handle(event("e1", &PAID)).await.unwrap();
    s.handlers.handle(event("e1", &PAID)).await.unwrap(); // delivered again
    assert_eq!(*s.emails.0.lock().unwrap(), [("ada@example.com".to_owned(), "Thank you, Ada! 2 × Jollof rice, ₦3,000.00.".to_owned())]);
}
```

The others check: an anonymous order and a customer who turned emails off get nothing; `order.ready` sends a text to the customer's phone; and, in one test, the API being down is `Retry` (and works once it's back), a deleted customer is `Skip`, unreadable data is `Skip`, and an event type it doesn't know is fine.

Across the workspace, `cargo test --workspace` (with `NATS_URL` set) now runs 104 tests: the API's, `contracts`' (including part 3's reader test) and notifications'.

## Step 6: the whole thing, running
<!-- bite: a6df41ff-301c-4658-91e4-780261ccc426 -->

Three programs, three terminals. The API and the worker from the project folder, notifications from its own:

```bash
cargo run                          # the API
cargo run --bin worker             # the relay, Okada's reader, and the jobs
cd notifications && cargo run      # the notifications service, with its own .env
```

**A trap on the way.** My first try started them from a script that had loaded the API's `.env` into the shell (`set -a; . ./.env`). Notifications stopped at once:

```text
Error: VersionMissing(3)
```

dotenvy never overrides a variable that's already set, so notifications got the **API's** `DATABASE_URL`, connected to the API's database, found 14 migrations it had never heard of, and refused to go on. That refusal is sqlx's migrator doing its job: it won't run against a database whose history doesn't match its own. The fix was not exporting the API's settings; lesson 36 gives each service its own settings in its own container, where this can't happen.

Then Tola (a customer, with a phone number) orders, and Paystack's signed webhook pays for it, as in lesson 17. Notifications' log, within a second:

```text
INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 15" text="Thank you, Tola! 1 × Moi moi, ₦700.00."
INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 18" text="Thank you, Tola! 1 × Moi moi, ₦700.00."
```

Two receipts, for one payment? Order 18 is the one just paid. Order 15 was paid during the failed first try, while notifications was refusing to start. Its `order.paid` waited in the stream, and went out the moment notifications first started properly. Nobody planned that test; the stream passed it anyway.

The outbox, after the relay's turn:

```text
     type     | order_id | sent
--------------+----------+------
 order.paid   | 18       | t
 order.placed | 18       | t
```

Now **stop notifications** (Ctrl+C), pay for two more orders, and start it again. Its log, 20 milliseconds apart:

```text
06:02:26.493617Z  INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 19" …
06:02:26.511001Z  INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 20" text="Thank you, Tola! 1 × Ofada stew, ₦3,000.00."
```

The API never noticed notifications was gone: both webhooks were answered `200`, both events waited in the stream, and the durable consumer `notifications` remembered where it had stopped.

The kitchen marks order 20 ready. Notifications:

```text
INFO notifications::providers: text (not really sent) to="+2348098765432" text="Tola, your Mama Put order 20 is ready. Come and collect it!"
```

and the worker's reader has saved Okada's delivery, from the event:

```text
 event_type  |                                          payload                                          | from_an_event
-------------+-------------------------------------------------------------------------------------------+---------------
 order.ready | {"dishId": "5", "orderId": "20", "readyAt": "2026-11-23T06:02:30.459862Z", "quantity": 1} | t
```

And NATS's monitoring page (`http://localhost:8222/jsz?consumers=true`) shows both readers caught up:

```text
partner-webhooks pending 0 unanswered 0
notifications    pending 0 unanswered 0
```

Okay!!!!! Two services, one truth.

## The Rust in this part
<!-- bite: 4fe3c70d-ceef-4cd8-a37c-822f550cf06e -->

1. **`sqlx.toml` with `database-url-var`**: which environment variable a crate's query macros read, so two crates in one workspace can check against two databases.
2. **`tonic_prost_build::configure().build_server(false)`**: generates clients only.
3. **Nested modules for generated code**, `pub mod pb { pub mod menu { tonic::include_proto!(…) } … }`: two packages' code, side by side.
4. **`Request::set_timeout`**: a deadline sent with the call, which the server sees too.
5. **`Endpoint::connect_lazy()`**: a channel that connects on first use, and reconnects by itself.
6. **Traits with `#[async_trait]` behind `Arc<dyn …>`**: the handlers hold "something that can find a customer", real in `main`, pretend in tests.
7. **`if let Some(paid) = event.data::<OrderPaidV1>()`**, then `?` on the inner `Result` with `map_err`: "is it ours?" and "is it readable?" as two separate steps.
8. **Struct update syntax in tests**, `OrderPaidV1 { customer_id: None, ..PAID }`: one field changed from a `const` example.
9. **`usize::is_multiple_of(3)`**: clearer than `% 3 == 0`, and Clippy suggests it.

## Your project so far
<!-- bite: 773bff87-446c-4370-96f0-6956aa729929 -->

The whole topic, all four parts:

```text
mama-put/
├── Cargo.toml                    ← [workspace] members; contracts; async-nats
├── .env                          ← NATS_URL
├── proto/mamaput/
│   ├── menu/v1/menu.proto
│   └── customers/v1/customers.proto   ← NEW: CustomersService.GetContact
├── migrations/
│   ├── 0013_outbox.sql           ← NEW: outbox; webhook_deliveries.event_id
│   └── 0014_users_phone.sql      ← NEW: users.phone
├── build.rs                      ← both .proto files
├── contracts/                    ← NEW crate
│   ├── src/events.rs             ← Envelope, Event, the four order events, subject
│   ├── src/stream.rs             ← ensure_stream, Failure, Reader, consume, retry_delay
│   └── tests/consume.rs
├── notifications/                ← NEW crate: the notifications service
│   ├── .env · sqlx.toml · build.rs
│   ├── migrations/               ← sent_notifications, preferences
│   ├── src/                      ← main, handlers, store, api, providers
│   └── tests/                    ← handlers, boundary
├── src/
│   ├── outbox.rs                 ← NEW: add, Relay
│   ├── bin/worker.rs             ← the relay and the partner-webhooks reader; no receipts
│   ├── grpc/customers.rs         ← NEW: CustomersApi
│   ├── auth/store.rs             ← contact()
│   ├── orders/                   ← events in the store's transactions; no OrderEvents
│   ├── payments/                 ← order.paid in mark_succeeded; receipts.rs deleted
│   └── webhooks/                 ← Okada from events; enqueue_once
└── tests/
    ├── events.rs                 ← NEW: the relay, against NATS
    └── grpc.rs                   ← a customer's contact details
```

## Common mistakes
<!-- bite: 1bb507c9-b6d7-4461-9990-2aa7c58cd468 -->

1. **Reading another service's tables "just this once".** Ask its API.
2. **Copying contact details into your own database.** They go stale, and you now hold personal data you have to protect. Ask when you need them.
3. **Sending, then not recording**, or recording before sending. Record after sending: a rare duplicate beats a lost message.
4. **Calling another service with no deadline.** One slow call holds the event, and then the next one.
5. **Failing on an event type you don't know.** Ignore it: that's how other services add events without breaking you.
6. **One `.env` for the whole workspace.** The last one read wins in sqlx's checks; give each service its own, and `sqlx.toml` where needed.
7. **Settings exported in the shell.** They beat every `.env` file. Start each service with only its own settings.

## Check your understanding
<!-- bite: 839c1b9c-ac3d-4df7-9723-903e919ed546 -->

1. Follow a payment from Paystack's webhook to Ada's receipt, naming each step and what happens if a process crashes right after it.
2. Notifications is stopped while two orders are paid. What happens when it starts again, and why?
3. The SMS provider is down for ten minutes. What happens to `order.ready` events, and to the API?
4. Why does notifications ask the API for Ada's email instead of reading it from the event, or keeping a copy?
5. Why did notifications' query checks first run against the API's database, and how does `sqlx.toml` fix it?

<details>
<summary>Answers, after your attempt</summary>

1. The webhook reaches `settle`; `mark_succeeded` updates the payment and the order and writes `order.paid` to the outbox in one transaction (a crash before `COMMIT` changes nothing, and Paystack sends the webhook again). The relay publishes it and marks it published (a crash before its `COMMIT` means it's published again, and JetStream drops the copy). The `notifications` reader gets it; the handler asks the API for Ada's contact, sends the email and records it (a crash before the answer means it comes again: `was_sent` catches it if `record` ran, otherwise Ada gets a second receipt), and then it's acked.
2. The stream kept both events, and the durable consumer `notifications` remembers it hasn't finished them. When it starts, it reads from where it stopped, and both receipts go out.
3. `ready_text` fails to send, returns `Retry`, and the reader naks each event with a growing delay until the provider is back; then they're sent and acked. The API doesn't notice: it wrote its events and carried on.
4. Events are stored and read by every reader, so personal details don't belong in them, and a copy kept by notifications would go stale when Ada changes her email. Asking at the moment of sending is always right.
5. sqlx reads `.env` files from the crate's folder up to the workspace root, and the last one wins: the root's, which is the API's. `sqlx.toml` makes this crate's checks read `NOTIFICATIONS_DATABASE_URL` instead, which only notifications' own `.env` sets.

</details>

## Practice
<!-- bite: 5924cdfe-8eeb-4df0-83b0-8c62cf57ecd6 -->

1. Move lesson 18's reminders about unpaid orders into notifications. Which event starts the clock, and how would notifications wait 15 minutes? (Hint: a delayed `Nak` is one way; a table of its own is another. Which survives a restart?)
2. Add a way for customers to turn texts off: who owns that setting, and how does the app reach it?
3. Make a crash between sending and recording happen (return early after `mailer.send`), and see the duplicate receipt. Then check whether a real email provider you know accepts an idempotency key.

**Done when** a paid order produces exactly one receipt in notifications' log; stopping notifications and paying for two orders delivers both receipts when it starts again; an order marked ready sends a text and one Okada delivery; and `cargo test --workspace` passes with NATS running.

## Before moving on
<!-- bite: 54806f91-277f-4d1a-b34a-ebdb23d6b30a -->

Okay!!!!! Mama Put is two services now. The API owns orders and payments and says what happened; the notifications service listens and tells customers. They share a contracts crate and the `.proto` files, and nothing else: not code (Cargo, and a test, make sure), not a database (a Postgres user makes sure). The outbox means an event can't be lost or invented, the message id means a crash doesn't double it, and the reader means a broken SMS provider makes texts late and nothing else.

But look at `GrpcApi::contact`: notifications calls the API, and the API might be slow, or down, or deploying. A 500 ms deadline helps, but what if every call times out for a minute? Which calls are safe to retry, and how many times? And right now anything that can reach port 50051 can ask for a customer's phone number. Calling other services safely is a skill of its own. That's the next lesson.

## Related
<!-- bite: c43eb9e8-bb2e-4660-8c4f-c6142c4e51ab -->

- [[backend/frameworks/axum/33-calling-services-safely-1|Next: Calling Services Safely 1: Deadlines, Retries and the Breaker]]
- [[backend/frameworks/net-http/25-splitting-out-a-microservice|The same topic in net/http]] — one Go module, and a hand-written consumer
- [[backend/frameworks/axum/22-grpc|gRPC]] — the contract notifications calls the API through
- [[backend/frameworks/axum/16-testing|Testing]] — fakes behind traits, and `#[sqlx::test]`

## About this lesson
<!-- bite: 286fc68a-8720-4f4c-926f-f7b6bb9c1f5c -->

**Level:** Advanced. Part 4 of 4 on splitting out a microservice, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), async-nats 0.53, sqlx 0.9 and tonic 0.14. Covers a second service crate with its own database, migrations and settings, sqlx's `.env` order and `sqlx.toml`, idempotent handlers that record what they sent, retry versus skip, a `CustomersService` on the API with only what a message needs, generated gRPC clients with deadlines and a lazy connection, console providers for development, handler tests with fakes and a real database, and the whole system running with one service stopped and started again.
