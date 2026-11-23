---
id: a3f6630f-b315-4e4d-b009-3f2cbb3fcee0
---

# Payments and Webhooks

**Taking a payment means sending the customer to a payment company's page, and then waiting for that company to *tell your server*, in a signed message called a webhook, that the money really arrived.** Your server never sees a card number, and it never believes the customer's word that they paid. It believes the payment company, and only after checking that the message really came from them. In Axum, the webhook route takes its body as plain `Bytes`, so the exact bytes the signature covers are there to check before anything reads them as JSON.

## Before you start
<!-- bite: 19428e14-e689-4a5d-8c3b-299f591c4629 -->

You should have:

1. Finished [[backend/frameworks/axum/16-testing|lesson 16]], so you have `TestApp` in `tests/common/` and `cargo test` runs 41 tests.
2. A free Paystack account in **test mode**, with its test secret key (it starts `sk_test_`). Test mode moves no real money.

After this lesson you will be able to:

1. Explain why a payment can't be finished inside one request, and why the redirect back to your site proves nothing.
2. Call an outside API from Rust safely: one shared `reqwest::Client` with a timeout, answers checked before use, and a calm 502 for the customer.
3. Receive Paystack's webhooks: check the HMAC signature on the exact bytes, skip duplicates, and settle each payment exactly once.
4. Verify a payment yourself, as a backup to the webhook.
5. Send your own signed webhooks to a partner, from a queue in Postgres, with timestamps, event IDs, retries, backoff and jitter.

## What to install
<!-- bite: 2a16ac01-844a-4c1f-a278-a2ce2238f185 -->

```bash
cargo add reqwest --features json
cargo add hmac
```

1. **`reqwest`** is the usual HTTP **client** for Rust: the side that *makes* requests. It's built on hyper, the same engine under Axum, so it fits the Tokio runtime we already have. `json` lets it send a body made with `serde`. By default it speaks HTTPS with **rustls**, a TLS library written in Rust, so it needs nothing installed on your computer. The first build takes a minute longer while its cryptography compiles.
2. **`hmac`** makes and checks HMAC signatures (step 5). It works with any hash from the same family of crates, including the `sha2` we added in lesson 12.

And four settings, in `.env`:

```text
PAYSTACK_SECRET_KEY=sk_test_...
PUBLIC_URL=http://localhost:8080
OKADA_WEBHOOK_URL=http://localhost:9090/hooks/mama-put
OKADA_WEBHOOK_SECRET=<another long random value, made with openssl rand -base64 32>
```

`PUBLIC_URL` is where customers' browsers reach us, and Paystack sends them back there. The Okada settings point at a pretend partner on your own laptop for now; step 10 makes one.

## Where we stopped
<!-- bite: 66e1a475-fe54-43f7-a86c-c42d705b9d4d -->

Right now, placing an order writes a row and takes the plates. Nobody pays. Ada could order twenty plates of jollof and walk away.

Mama wants it simple: you order, you pay, and only then does the kitchen cook. And when the food is ready, the riders from **Okada Riders** (the delivery company Mama works with) should hear about it straight away, without someone phoning them.

So this lesson has two directions:

1. **Webhooks coming in**: Paystack telling us "this payment succeeded".
2. **Webhooks going out**: us telling Okada Riders "order 42 is ready for pickup".

## The kid version
<!-- bite: 954330c1-4f20-481b-a66d-9f4eb1138517 -->

Ada buys a plate, but she pays at the bank across the road, not at Mama's table. Mama can't see the bank.

Ada comes back and says "I've paid, see?" and waves a paper. Should Mama believe the paper? Anyone can write on paper.

So Mama and the bank agree on a better way. When someone pays, the bank sends its own messenger to Mama, with a note sealed with a stamp only the bank has. Mama checks the stamp, and *then* she believes it. If the messenger comes twice with the same note, she doesn't cook twice.

The messenger is the webhook. The stamp is the signature. Ada's paper is the redirect back to our site, and we never trust it by itself.

**Where the picture stops working.** A real messenger knows when he has delivered the note. A webhook doesn't always: the request can be lost, or our server can be down. So the bank keeps sending the same note until Mama says "got it", and Mama must be ready to receive the same note many times.

## Terms used in this lesson
<!-- bite: fec30b1d-85ba-4a8a-8a55-4fdf14c48a88 -->

1. **Payment provider**: This is the company that takes the card or bank transfer and moves the money, here **Paystack**. We never touch card numbers ourselves; the customer types them on Paystack's page.
2. **Checkout**: This is Paystack's payment page. We ask Paystack to start one, and it gives us a link to send the customer to.
3. **Reference**: This is a unique name *we* give each payment attempt, like `mp-42-0782ADB6...`. It's how we and Paystack talk about the same payment.
4. **Webhook**: This is an HTTP POST another system sends to a URL on our server when something happens. Paystack sends one called `charge.success` when a payment succeeds.
5. **Signature**: This is a code worked out from the webhook's exact body and a secret only the sender and we know. If the code matches, the webhook really came from the sender and wasn't changed on the way.
6. **HMAC**: This stands for **hash-based message authentication code**. It's the recipe for that code: mix the secret and the message, then hash them. Without the secret, nobody can make a matching code.
7. **At-least-once delivery**: This means the sender promises every webhook arrives *at least* once, and sometimes more than once. Receivers must cope with duplicates.
8. **Verify call**: This is an API call *we* make to Paystack, asking "what really happened to payment `mp-42-...`?". It's our backup when we haven't heard a webhook.
9. **Backoff**: This is waiting longer after each failed try: 30 seconds, then a minute, then two. **Jitter** is a small random extra on each wait, so many retries don't all land at the same moment.
10. **HTTP client**: This is code that sends requests to other servers, the opposite of everything we've built so far. Ours is `reqwest`.

## Step 1: why paying can't happen in one request
<!-- bite: df6a74da-80d7-46e9-9b0c-953a421bb158 -->

Every request so far went: request in, work, answer out, done. A payment can't work like that, because the middle part happens somewhere we can't see:

1. Ada asks us to pay for order 42.
2. We ask Paystack to start a checkout. Paystack gives us a link.
3. We send Ada the link. Her app opens Paystack's page.
4. Ada types her card details, and maybe a one-time code from her bank. This could take ten seconds or ten minutes. She might give up.
5. Paystack sends Ada's browser back to our site.
6. Separately, Paystack sends **us** a webhook: `charge.success` for `mp-42-...`.

Step 5 is tempting. Ada's browser lands on `https://mamaput.example/payment-done?reference=mp-42-...`, so why not mark the order paid right there?

Because anyone can type that URL. Ada (or someone less honest than Ada) can visit it without paying a kobo. And the opposite also happens: Ada pays, closes the tab before the redirect, and never lands on step 5 at all. The redirect is just the browser, and the browser is the customer's.

So, the rule for the whole lesson: **an order becomes paid only when Paystack itself says so**, through a signed webhook or through a verify call we make to Paystack ourselves.

## Step 2: the tables
<!-- bite: a0bc0f5c-13ba-4e7a-93e1-3fc1b4feb3ff -->

`migrations/0008_payments.sql`:

```sql
-- One row per attempt to pay. A declined card and a second try are two rows, for one order.
CREATE TABLE payments (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id    bigint NOT NULL REFERENCES orders (id),
  reference   text   NOT NULL UNIQUE,
  amount_kobo bigint NOT NULL CHECK (amount_kobo > 0),   -- what we asked for, copied from the order
  status      text   NOT NULL DEFAULT 'started'
              CHECK (status IN ('started', 'succeeded', 'failed')),
  created_at  timestamptz NOT NULL DEFAULT now(),
  settled_at  timestamptz
);

CREATE INDEX payments_order_id_idx ON payments (order_id);

-- When the order was paid, online or in cash. NULL: not yet.
ALTER TABLE orders ADD COLUMN paid_at timestamptz;
```

Why a separate `payments` table, instead of a `paid` column on the order? Because one order can have **several payment attempts**. Ada starts paying, her card is declined, she tries another card. Each attempt gets its own row and its own reference. The order is paid when one of them succeeds, and `orders.paid_at` records when.

`amount_kobo` is copied onto the payment when it starts. That's the amount we *asked* for, and later we'll check Paystack collected exactly that.

`migrations/0009_webhooks.sql`:

```sql
-- Webhooks we've received and finished handling.
CREATE TABLE webhook_events_received (
  provider   text NOT NULL,
  event_key  text NOT NULL,
  handled_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (provider, event_key)
);

-- Webhooks we send, and how far each has got.
CREATE TABLE webhook_deliveries (
  id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  url             text        NOT NULL,
  event_type      text        NOT NULL,
  payload         jsonb       NOT NULL,
  attempts        integer     NOT NULL DEFAULT 0,
  next_attempt_at timestamptz NOT NULL DEFAULT now(),
  delivered_at    timestamptz,
  last_error      text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- Only the ones still waiting: it stays small however many have been delivered.
CREATE INDEX webhook_deliveries_due_idx
  ON webhook_deliveries (next_attempt_at)
  WHERE delivered_at IS NULL;
```

The first table is for webhooks coming in, the second for webhooks going out. The index is **partial**: it holds only the rows still waiting to be sent, so it stays small however many thousands have been delivered. `gen_random_uuid()` is built into Postgres since version 13.

```bash
sqlx migrate run
```

The code needs to know whether an order is paid, but not when, so `Order` in `src/orders/model.rs` gains one field:

```rust
    /// Paid for, online or in cash. Only paid orders get cooked.
    pub paid: bool,
```

and every query in `src/orders/store.rs` that returns an order adds one column to its list:

```rust
paid_at IS NOT NULL AS "paid!"
```

`IS NOT NULL` turns the time into a yes or no in SQL. The `!` tells sqlx the answer is never `NULL`, so the type is `bool`, not `Option<bool>`. Because the queries are checked against the database (lesson 8), forgetting the column in any one of them is a compile error: `Order` has a field the query doesn't fill.

`OrderV2` gains `paid: bool` too, so the app can show "paid". Adding a field isn't a breaking change (lesson 10): old clients ignore it. `OrderV1` stays exactly as it was.

## Step 3: talking to Paystack
<!-- bite: 8c96bcfd-492e-4c0a-9b7e-ea2de4990ff5 -->

Every outside service gets one file that knows how to talk to it, and the rest of the app talks to it through a trait we own. It's lesson 5 again: the order service doesn't know about SQL, and the payment service won't know about Paystack's URLs.

There's also a new kind of failure. So far every error was the *client's* fault (a 4xx) or ours (a 500). Now there's a third case: Paystack is down, or slow, or answers nonsense. That's nobody's fault in the request. The usual status is **502 Bad Gateway**: "I'm a gateway to another service, and it let me down".

`src/payments/provider.rs`:

```rust
use async_trait::async_trait;

use super::model::Seen;
use crate::money::Kobo;

/// A payment company, as this module needs it. Paystack in real life; a fake in tests.
#[async_trait]
pub trait Provider: Send + Sync {
    /// Starts a checkout and returns the link to send the customer to.
    async fn start_checkout(&self, email: &str, amount: Kobo, reference: &str, callback_url: &str) -> Result<String, ProviderError>;
    /// Asks what really happened to a payment.
    async fn verify(&self, reference: &str) -> Result<Seen, ProviderError>;
}

/// The payment company let us down. Nobody's fault in the request, so it's a 502, never a 500.
#[derive(Debug, thiserror::Error)]
pub enum ProviderError {
    #[error("couldn't reach the payment company: {0}")]
    Unreachable(String),
    #[error("the payment company answered {0}")]
    Refused(u16),
    #[error("the payment company's answer made no sense: {0}")]
    BadResponse(String),
}
```

The trait is what the payment service uses. Paystack is one thing that can stand behind it; in tests, a fake will (step 11). That's the reason it's a trait at all: payments have a second implementation from day one.

Now Paystack itself, `src/payments/paystack.rs`:

```rust
//! Paystack's API: the only file that knows its URLs and its JSON.

use async_trait::async_trait;
use reqwest::{Client, Response, Url};
use serde::{Deserialize, de::DeserializeOwned};
use serde_json::json;

use super::{
    model::Seen,
    provider::{Provider, ProviderError},
};
use crate::money::Kobo;

/// The biggest answer we'll read from Paystack. Its answers are a few kilobytes.
const MAX_ANSWER: usize = 1024 * 1024;

pub struct Paystack {
    base_url: Url,
    secret_key: String,
    client: Client,
}

impl Paystack {
    /// Talks to `base_url`: `https://api.paystack.co` in real life, a pretend Paystack in tests.
    /// `client` must have a timeout: `main` builds it.
    pub fn new(base_url: Url, secret_key: &str, client: Client) -> Self {
        Paystack { base_url, secret_key: secret_key.to_owned(), client }
    }

    /// The base URL with `segments` added, each one escaped: a `/` or `?` in a reference can't change the address.
    fn url(&self, segments: &[&str]) -> Url {
        let mut url = self.base_url.clone();
        url.path_segments_mut().expect("an http(s) URL has a path").pop_if_empty().extend(segments);
        url
    }

    /// Reads Paystack's answer, checking it the way we check what clients send us.
    async fn answer<T: DeserializeOwned>(response: Result<Response, reqwest::Error>) -> Result<T, ProviderError> {
        let mut response = response.map_err(|e| ProviderError::Unreachable(e.to_string()))?;
        if !response.status().is_success() {
            return Err(ProviderError::Refused(response.status().as_u16()));
        }
        let mut body = Vec::new();
        while let Some(chunk) = response.chunk().await.map_err(|e| ProviderError::Unreachable(e.to_string()))? {
            if body.len() + chunk.len() > MAX_ANSWER {
                return Err(ProviderError::BadResponse("answer too big".into()));
            }
            body.extend_from_slice(&chunk);
        }
        let answer: Answer<T> = serde_json::from_slice(&body).map_err(|e| ProviderError::BadResponse(e.to_string()))?;
        match answer {
            Answer { status: true, data: Some(data) } => Ok(data),
            _ => Err(ProviderError::BadResponse("status false, or no data".into())),
        }
    }
}

/// Every Paystack answer: `{"status": true, "message": "...", "data": {...}}`.
#[derive(Deserialize)]
struct Answer<T> {
    status: bool,
    data: Option<T>,
}

#[derive(Deserialize)]
struct Initialized {
    authorization_url: String,
}

#[derive(Deserialize)]
struct Transaction {
    status: String, // "success", "failed", "abandoned", ...
    amount: i64,    // in kobo
    currency: String,
}

#[async_trait]
impl Provider for Paystack {
    async fn start_checkout(&self, email: &str, amount: Kobo, reference: &str, callback_url: &str) -> Result<String, ProviderError> {
        let body = json!({"email": email, "amount": amount.0, "reference": reference, "callback_url": callback_url});
        let sent = self.client.post(self.url(&["transaction", "initialize"])).bearer_auth(&self.secret_key).json(&body).send().await;
        let started: Initialized = Self::answer(sent).await?;
        if !started.authorization_url.starts_with("https://") {
            return Err(ProviderError::BadResponse("no https checkout link".into()));
        }
        Ok(started.authorization_url)
    }

    async fn verify(&self, reference: &str) -> Result<Seen, ProviderError> {
        let sent = self.client.get(self.url(&["transaction", "verify", reference])).bearer_auth(&self.secret_key).send().await;
        let found: Transaction = Self::answer(sent).await?;
        Ok(Seen { succeeded: found.status == "success", amount: Kobo(found.amount), currency: found.currency })
    }
}
```

Four habits in there. They matter for every outside service, not just Paystack:

1. **A timeout on every call.** `main` builds the client with `.timeout(Duration::from_secs(8))` (step 4). **A `reqwest::Client` has no timeout unless you give it one**, so if Paystack hangs, Ada's request hangs with it, until our own 10-second layer from lesson 7 gives up with a bare 408. Eight seconds is under that, so a slow Paystack gets *our* clear 502 first. And never use `reqwest::get(...)` for outside calls: it's a shortcut that makes a new client each time, with no timeout. Lesson 33 goes much further with this.
2. **Giving up when Ada does.** If Ada closes the app, hyper drops her request's future, and everything it was awaiting stops with it, our call to Paystack included. In Rust a future does nothing unless something polls it, so cancelling is just dropping. Go needs a `context` passed to every call for this; Rust gets it for free.
3. **Check what comes *back*.** We validate what clients send us (lesson 6). An outside service's answer is input too. `answer` reads it in pieces with `chunk()`, refusing more than 1 MB, so a broken or hostile server can't fill our memory. Then serde checks its shape, `status: true` and `data` must be there, and a checkout link must be `https://`. If Paystack ever changes its answers, we get a clear `BadResponse`, not an empty link quietly sent to Ada.
4. **The base URL is a setting.** In production it's `https://api.paystack.co`; in a test it's a pretend Paystack on a local port (step 11), so the real code runs against it. `url()` adds the path with `path_segments_mut`, which escapes each piece. A reference with a `/` or `?` in it can't change which address we call.

`amount` is sent as `amount.0`, in kobo. That's why we moved to kobo in lesson 10: ₦3,000 is `300000`. Send `3000` and Ada is asked to pay ₦30. `Kobo` makes the unit part of the type, so `.0` is the one, visible place it becomes a plain number.

## Step 4: starting a checkout
<!-- bite: d3525c52-912a-4e2b-a14b-a44100b5d719 -->

The customer's side is a new route: "pay for this order". It creates a payment attempt, asks Paystack for a checkout link, and gives the link back.

First the types, `src/payments/model.rs`:

```rust
use serde::Serialize;
use utoipa::ToSchema;

use crate::money::Kobo;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, sqlx::Type, ToSchema)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "text", rename_all = "lowercase")]
pub enum PaymentStatus {
    Started,
    Succeeded,
    Failed,
}

/// One attempt to pay for an order.
#[derive(Clone, Debug)]
pub struct Payment {
    pub order_id: i64,
    /// Our name for this attempt, shared with Paystack: `mp-42-9F3A…`.
    pub reference: String,
    /// What we asked for. A success for any other amount doesn't count.
    pub amount: Kobo,
    pub status: PaymentStatus,
}

/// A checkout that's been started: where to send the customer.
#[derive(Clone, Debug)]
pub struct Checkout {
    pub reference: String,
    pub checkout_url: String,
}

/// What the payment company says happened to a payment.
#[derive(Clone, Debug, PartialEq)]
pub struct Seen {
    pub succeeded: bool,
    pub amount: Kobo,
    pub currency: String,
}

/// What settling a payment did. None of these is an error: each is a clear answer.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Outcome {
    /// This news paid the order.
    Paid,
    /// We'd already settled this payment: nothing to do.
    AlreadySettled,
    /// The payment succeeded, but another payment had already paid the order. Someone must refund one.
    OrderWasAlreadyPaid,
    /// A payment we never started.
    Unknown,
    Failed,
    /// The wrong amount or currency. Never believed; a person must look.
    Mismatch,
}
```

The service needs the order service (to check Ada may pay for this order), the users (for her email), a store and a provider. `src/payments/service.rs`:

```rust
use std::sync::Arc;

use super::{
    model::{Checkout, Outcome, Payment, PaymentStatus, Seen},
    provider::{Provider, ProviderError},
    store::PgPaymentStore,
};
use crate::{
    auth::{Action, Identity, PgAuthStore, allows},
    db::StoreError,
    orders::{OrderError, OrderService},
};

#[derive(Debug, thiserror::Error)]
pub enum PaymentError {
    #[error("there's no such payment")]
    NotFound,
    #[error("this order is already paid")]
    AlreadyPaid,
    #[error(transparent)]
    Order(#[from] OrderError),
    #[error(transparent)]
    Provider(#[from] ProviderError),
    #[error(transparent)]
    Store(#[from] StoreError),
}

#[derive(Clone)]
pub struct PaymentService {
    store: PgPaymentStore,
    orders: OrderService,
    users: PgAuthStore,
    provider: Arc<dyn Provider>,
    /// Where customers' browsers reach us. Paystack sends them back here.
    public_url: Arc<str>,
}

impl PaymentService {
    pub fn new(store: PgPaymentStore, orders: OrderService, users: PgAuthStore, provider: Arc<dyn Provider>, public_url: &str) -> Self {
        PaymentService { store, orders, users, provider, public_url: public_url.into() }
    }

    /// Starts paying for an order: a new attempt, with its own reference, and a checkout link.
    pub async fn start_checkout(&self, who: Identity, order_id: i64) -> Result<Checkout, PaymentError> {
        let order = self.orders.get(order_id, who).await?; // 404 unless they may see it
        if !allows(who, Action::OrderPay, order.customer_id) {
            return Err(OrderError::NotFound(order_id).into());
        }
        if order.paid {
            return Err(PaymentError::AlreadyPaid);
        }
        // The account was deleted after the token was made: as good as no order.
        let user = self.users.find(who.user_id).await?.ok_or(OrderError::NotFound(order_id))?;

        let reference = format!("mp-{}-{}", order.id, random_text());
        self.store.create(order.id, &reference, order.total).await?;
        let callback = format!("{}/payment-done", self.public_url);
        let checkout_url = self.provider.start_checkout(&user.email, order.total, &reference, &callback).await?;
        Ok(Checkout { reference, checkout_url })
    }
```

Look at what `start_checkout` reuses. `orders.get(order_id, who)` already hides other customers' orders as 404 (lesson 13). Staff can see every order, though, and staff shouldn't start a payment with *their* email on Ada's receipt, so there's one new row in the policy, `OrderPay`, which only the owner has:

```rust
        Action::OrderPay => owns, // only the customer pays online, with their own email on the receipt
```

To anyone else it's the same 404 as no order at all. And the amount comes from **our** database, `order.total`, never from the request. There's no request body at all, so a client that sends `{"amount": 100}` has nowhere to put it.

The reference is `mp-`, the order's id, and 24 random characters, at the end of the same file:

```rust
/// 24 capital letters and digits: what Paystack allows in a reference, and enough that nobody guesses one.
fn random_text() -> String {
    let mut bytes = [0u8; 12];
    getrandom::fill(&mut bytes).expect("the operating system gives random bytes");
    hex::encode_upper(bytes)
}
```

Twelve random bytes, written as hex in capitals, give 24 characters from `0`–`9` and `A`–`F`, which are all characters Paystack allows in a reference. The id makes it readable in Paystack's dashboard; the random part makes every attempt unique, so Ada's second try doesn't clash with her first.

`payments` uses `orders` and `auth`. Nothing in `orders` uses `payments`.

### Settling: the one place a payment becomes paid

```rust
    /// The ONE place a payment becomes succeeded. The webhook and the verify call both end here,
    /// and it's safe to call any number of times, at the same moment.
    pub async fn settle(&self, reference: &str, seen: Seen) -> Result<Outcome, PaymentError> {
        let Some(payment) = self.store.find(reference).await? else {
            tracing::warn!(reference, "payment news for a reference we never made");
            return Ok(Outcome::Unknown);
        };
        if !seen.succeeded {
            self.store.mark_failed(reference).await?;
            return Ok(Outcome::Failed);
        }
        if seen.currency != "NGN" || seen.amount != payment.amount {
            tracing::error!(reference, expected = payment.amount.0, got = seen.amount.0, currency = seen.currency, "PAYMENT AMOUNT MISMATCH");
            return Ok(Outcome::Mismatch);
        }
        let outcome = self.store.mark_succeeded(reference).await?;
        if outcome == Outcome::OrderWasAlreadyPaid {
            tracing::error!(reference, order_id = payment.order_id, "order paid twice, refund needed");
        }
        Ok(outcome)
    }
```

This is the most important function in the lesson. It checks three things before it believes a "success":

1. **We know this reference.** News about a payment we never started is logged and ignored.
2. **The currency and amount are exactly what we asked for.** If someone found a way to pay ₦30 for a ₦3,000 order, this is where it stops. A mismatch is logged at `error` level, because it should never happen and a person must look.
3. **It hasn't already been counted.** That's inside `mark_succeeded`, next.

And at the end, one awkward case. Ada opens checkout in two tabs and pays in both. Both succeed at Paystack, so she's paid twice. Our database can't undo that, so we log "refund needed", and someone refunds the second payment from the Paystack dashboard. (Doing refunds automatically is a good practice once lesson 18's jobs exist.)

`settle` never returns an error for "unknown", "failed" or "mismatch". Those are answers, not failures: the news was received and understood. Only a real problem, like the database being down, is an error, and that's what makes Paystack try again later.

`src/payments/store.rs`, the method that matters:

```rust
    /// Marks the payment succeeded and its order paid, together. Only the first caller changes anything.
    pub async fn mark_succeeded(&self, reference: &str) -> Result<Outcome, StoreError> {
        let mut tx = self.pool.begin().await?;
        let order_id = sqlx::query_scalar!(
            "UPDATE payments SET status = 'succeeded', settled_at = now()
             WHERE reference = $1 AND status = 'started'
             RETURNING order_id",
            reference
        )
        .fetch_optional(&mut *tx)
        .await?;
        let Some(order_id) = order_id else {
            return Ok(Outcome::AlreadySettled); // someone settled it first; dropping `tx` ends it
        };
        let paid = sqlx::query!("UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL", order_id)
            .execute(&mut *tx)
            .await?
            .rows_affected();
        tx.commit().await?;
        Ok(if paid == 1 { Outcome::Paid } else { Outcome::OrderWasAlreadyPaid })
    }
```

The guarded `UPDATE`, for the fourth time in this subject. `WHERE status = 'started'` means only the **first** caller changes the row. If the webhook and the verify call arrive at the same instant, Postgres locks the row for one, and the other finds it already `succeeded` and changes nothing. There's no "check, then update" gap for two callers to slip through. The transaction makes the payment and the order change together, or not at all, and an early `return` drops `tx`, which rolls it back (lesson 8).

The rest of the store (`create`, `find`, `mark_failed` with the same `status = 'started'` guard, and the webhook bookkeeping in step 5) is plain sqlx like lesson 8. `PgPaymentStore` has no trait, like the auth store in lesson 12: tests run it on a real database, and the provider is the part they fake.

### The routes

`src/payments/handlers.rs`:

```rust
use axum::{
    Router,
    extract::{FromRef, State},
    http::StatusCode,
    routing::{get, post},
};
use serde::Serialize;
use utoipa::ToSchema;

use super::{
    model::{Payment, PaymentStatus},
    provider::ProviderError,
    service::{PaymentError, PaymentService},
};
use crate::{
    auth::{AuthUser, Keys},
    http::{ApiError, Data, Path},
    money::Amount,
};

/// Paying for orders. v2 only: v1's orders have no customer, so they're paid at the counter.
pub fn router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    PaymentService: FromRef<S>,
    Keys: FromRef<S>,
{
    Router::new().route("/orders/{id}/payments", post(start)).route("/payments/{reference}", get(check))
}

#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct CheckoutV2 {
    reference: String,
    /// Send the customer here to pay.
    checkout_url: String,
}

#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct PaymentV2 {
    reference: String,
    order_id: i64,
    amount: Amount,
    status: PaymentStatus,
}

impl From<Payment> for PaymentV2 {
    fn from(p: Payment) -> Self {
        PaymentV2 { reference: p.reference, order_id: p.order_id, amount: p.amount.into(), status: p.status }
    }
}

impl From<PaymentError> for ApiError {
    fn from(err: PaymentError) -> Self {
        match err {
            PaymentError::NotFound => {
                ApiError::new(StatusCode::NOT_FOUND, "payment-not-found", "Payment not found", "There's no such payment.")
            }
            PaymentError::AlreadyPaid => {
                ApiError::new(StatusCode::CONFLICT, "order-already-paid", "Already paid", "This order is already paid.")
            }
            PaymentError::Order(e) => e.into(),
            PaymentError::Provider(e) => {
                // Paystack's words are for us, not for the customer: log them, answer calmly.
                tracing::warn!(cause = %e, "the payment provider let us down");
                let code = match e {
                    ProviderError::Unreachable(_) => "payment-provider-unreachable",
                    ProviderError::Refused(_) => "payment-provider-error",
                    ProviderError::BadResponse(_) => "payment-provider-bad-response",
                };
                ApiError::new(
                    StatusCode::BAD_GATEWAY,
                    code,
                    "Payment service unavailable",
                    "We couldn't reach the payment service. Please try again.",
                )
            }
            PaymentError::Store(e) => ApiError::internal(e),
        }
    }
}

async fn start(
    AuthUser(who): AuthUser,
    State(payments): State<PaymentService>,
    Path(order_id): Path<i64>,
) -> Result<(StatusCode, Data<CheckoutV2>), ApiError> {
    let checkout = payments.start_checkout(who, order_id).await?;
    Ok((StatusCode::CREATED, Data(CheckoutV2 { reference: checkout.reference, checkout_url: checkout.checkout_url })))
}

async fn check(
    AuthUser(who): AuthUser,
    State(payments): State<PaymentService>,
    Path(reference): Path<String>,
) -> Result<Data<PaymentV2>, ApiError> {
    Ok(Data(payments.check(who, &reference).await?.into()))
}
```

`From<PaymentError> for ApiError` is lesson 7's pattern: the service says what went wrong, and this one `match` decides what the client sees. An order error is passed on to the order module's own `From` with `e.into()`. A provider error is logged with Paystack's words, and Ada gets a calm sentence and one of three codes. Paystack's messages are written for us, not for her, and can mention things she shouldn't see.

In `src/lib.rs`, the payment routes join v2, behind lesson 15's idempotency middleware like the order routes:

```rust
    let idempotent = middleware::from_fn_with_state(state.idempotency.clone(), http::idempotent);
    let v2 = Router::new()
        .merge(menu::router::<_, version::V2>())
        .merge(orders::router::<_, version::V2>().route_layer(idempotent.clone()))
        .merge(payments::router().route_layer(idempotent))
```

`from_fn_with_state` returns a layer, and a layer can be cloned, so both routers share one. With it, a retried "Pay" tap gets the same checkout link back instead of starting a second payment. An empty body is fine: it fingerprints the same every time. `AppState` gains `payments: payments::PaymentService` and `paystack_secret` (step 5), and `main` builds them:

```rust
    // One client for Paystack, made once and shared: it keeps connections open. Never without a timeout,
    // and this one is under the app's own 10 seconds, so a slow Paystack gets our 502, not a bare 408.
    let paystack_key = env("PAYSTACK_SECRET_KEY")?;
    let client = reqwest::Client::builder().timeout(Duration::from_secs(8)).build()?;
    let paystack_url = std::env::var("PAYSTACK_BASE_URL").unwrap_or_else(|_| "https://api.paystack.co".into());
    let paystack = Paystack::new(paystack_url.parse()?, &paystack_key, client);
    let payments =
        PaymentService::new(PgPaymentStore::new(pool.clone()), orders.clone(), PgAuthStore::new(pool.clone()), Arc::new(paystack), &env("PUBLIC_URL")?);
```

**One `reqwest::Client`, made once.** A client keeps a pool of open connections, so the second call to Paystack skips the TLS handshake. It's cheap to clone (there's an `Arc` inside), so pass clones around; never build a new one per request.

```bash
curl -s -X POST localhost:8080/v2/orders/11/payments \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: pay-11-first-try"
```

```json
{
    "data": {
        "reference": "mp-11-0782ADB6E985A44A7B19963E",
        "checkoutUrl": "https://checkout.paystack.com/0peioxfhpn"
    }
}
```

Send it again with the same key and the same answer comes back, with `idempotent-replayed: true`. Open the link in a browser and you'll see Paystack's test checkout; its docs list test cards that succeed and fail. Pay with one that succeeds. Now Paystack wants to tell us, which brings us to the webhook.

## Step 5: receiving the webhook
<!-- bite: acbe006c-9aca-481f-9d23-c6b60a3fbc52 -->

When the payment succeeds, Paystack sends a POST to the webhook URL you set in its dashboard (Settings → API Keys & Webhooks). The body looks like this, trimmed:

```json
{
  "event": "charge.success",
  "data": {
    "id": 4099260516,
    "reference": "mp-11-0782ADB6E985A44A7B19963E",
    "amount": 300000,
    "currency": "NGN",
    "status": "success"
  }
}
```

And one header that matters: `x-paystack-signature`. Paystack works it out as the **HMAC SHA-512** of the exact body bytes, using your secret key, written as hex. We work out the same thing. If they match, only someone with our secret key could have made this request, and that's Paystack.

### The exact bytes, in Axum

You can't check a signature on JSON that's been read and written again. `{"event":"charge.success"}` and `{"event": "charge.success"}` mean the same thing, but they're different bytes, with different signatures. The check needs the bytes exactly as they arrived.

So the handler doesn't take `Json<T>`. `Json` reads the body, turns it into a struct and throws the bytes away. It takes **`Bytes`**, an extractor that reads the whole body and hands it over untouched. The handler checks the signature on those bytes, and only then reads them as JSON itself.

A body is a stream that can be read only once, so in Axum only the **last** argument of a handler may take it (lesson 2). `HeaderMap` and `State` read only the request's head, so they go first and `body: Bytes` goes last. Express has to mount a special raw parser before its JSON parser for this; in Axum, choosing the extractor is the whole job.

### Its own place

The webhook needs the opposite of most of our protections. It has no login: the signature is its protection. It isn't part of our API versions either: `/v1` and `/v2` describe *our* shapes, and this route receives Paystack's. So it lives at `/webhooks/paystack`, outside both.

In net/http this route needed a separate middleware chain, because its rate limit ran on every request. Ours never did: lesson 14 put the limiter on the password routes only, and logins are extractors, not layers. So the webhook simply leaves out what it doesn't need. It only has to raise one limit. Paystack's events carry more than a webhook of ours ever will, and lesson 6's 16 KB body limit is too small. `DefaultBodyLimit` works by leaving a note on the request, and the layer nearest the handler writes last, so the **innermost limit wins**.

The end of `src/payments/webhook.rs` shows the handler; the start is the route and the types:

```rust
//! `POST /webhooks/paystack`: Paystack telling us what happened to a payment.

use std::sync::Arc;

use axum::{
    Router,
    body::Bytes,
    extract::{DefaultBodyLimit, FromRef, State},
    http::{HeaderMap, StatusCode},
    routing::post,
};
use serde::Deserialize;

use super::{model::Seen, service::PaymentService};
use crate::{
    http::ApiError,
    money::Kobo,
    signing::{HmacSha512, verify_hex},
};

/// The key Paystack signs webhooks with: our secret key. Cheap to clone; never printed.
#[derive(Clone)]
pub struct WebhookSecret(Arc<str>);

impl WebhookSecret {
    pub fn new(secret: &str) -> Self {
        WebhookSecret(secret.into())
    }
}

/// Outside `/v1` and `/v2`: our versions describe our shapes, and this is Paystack's.
pub fn webhook_router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    PaymentService: FromRef<S>,
    WebhookSecret: FromRef<S>,
{
    // Paystack's events can be bigger than anything our clients send. The innermost limit wins.
    Router::new().route("/webhooks/paystack", post(paystack).layer(DefaultBodyLimit::max(100 * 1024)))
}

/// What Paystack sends. `event` says which kind; `data`'s shape depends on it, so it waits as plain JSON.
#[derive(Deserialize)]
struct Event {
    event: String,
    #[serde(default)]
    data: serde_json::Value,
}

#[derive(Deserialize)]
struct Charge {
    id: i64,
    reference: String,
    amount: i64,
    currency: String,
    status: String,
}
```

and in `src/lib.rs`, next to the other routes:

```rust
        .merge(payments::webhook_router())
```

### Checking the signature

`src/signing.rs`, since our own webhooks will need signatures too:

```rust
//! HMAC signatures, for webhooks in both directions: checking Paystack's, and making our own.

use hmac::{Hmac, KeyInit, Mac};
use sha2::{Sha256, Sha512};

/// What Paystack signs its webhooks with.
pub type HmacSha512 = Hmac<Sha512>;
/// What we sign ours with.
pub type HmacSha256 = Hmac<Sha256>;

/// The HMAC of `message` with `secret`, as hex. `M` picks the hash: `HmacSha256` or `HmacSha512`.
pub fn sign_hex<M: Mac + KeyInit>(secret: &[u8], message: &[u8]) -> String {
    let mut mac = M::new_from_slice(secret).expect("HMAC takes a key of any length");
    mac.update(message);
    hex::encode(mac.finalize().into_bytes())
}

/// Is `signature` (hex) the HMAC of `message` with `secret`? Compared in constant time.
/// A signature that's empty, not hex, or the wrong length never matches.
pub fn verify_hex<M: Mac + KeyInit>(secret: &[u8], message: &[u8], signature: &[u8]) -> bool {
    let Ok(signature) = hex::decode(signature) else {
        return false;
    };
    let mut mac = M::new_from_slice(secret).expect("HMAC takes a key of any length");
    mac.update(message);
    mac.verify_slice(&signature).is_ok()
}
```

Why not compare the two hex strings with `==`? Because `==` stops at the first different character. A wrong signature that starts with the right three characters takes a tiny bit longer to refuse than one that's wrong from the first. With enough tries and careful timing, an attacker can use that difference to find the right signature one character at a time. `verify_slice` always compares every byte, so it takes the same time whatever the answer. It's lesson 3's `ct_eq` for the staff key, built into the HMAC.

`verify_slice` also refuses a signature of the wrong length, so an empty header can't "match" anything. And `hex::decode` refuses anything that isn't hex, so a strange header is a plain "no", never a panic.

`sign_hex` and `verify_hex` are **generic** over `M`, the kind of HMAC. `M: Mac + KeyInit` means "any type that can be made from a key and works as a MAC". `Hmac<Sha512>` is one, `Hmac<Sha256>` another, and the type aliases give them short names. The caller chooses with `::<>`: `verify_hex::<HmacSha512>(...)`. That's how the same two functions check Paystack's SHA-512 signatures and make our SHA-256 ones.

### The webhook handler

```rust
async fn paystack(
    State(payments): State<PaymentService>,
    State(secret): State<WebhookSecret>,
    headers: HeaderMap,
    body: Bytes,
) -> Result<StatusCode, ApiError> {
    // 1. Really from Paystack? Check the exact bytes that arrived, before anything else.
    let signature = headers.get("x-paystack-signature").map(|v| v.as_bytes()).unwrap_or_default();
    if !verify_hex::<HmacSha512>(secret.0.as_bytes(), &body, signature) {
        return Err(ApiError::new(
            StatusCode::UNAUTHORIZED,
            "bad-webhook-signature",
            "Signature not valid",
            "The webhook signature is not valid.",
        ));
    }

    // 2. Only now, read it.
    let bad_body = || ApiError::new(StatusCode::BAD_REQUEST, "bad-webhook-body", "Unexpected webhook", "Unexpected webhook body.");
    let event: Event = serde_json::from_slice(&body).map_err(|_| bad_body())?;
    // 3. An event we don't handle: say thanks anyway, or Paystack sends it again for days.
    if event.event != "charge.success" {
        return Ok(StatusCode::OK);
    }
    let charge: Charge = serde_json::from_value(event.data).map_err(|_| bad_body())?;
    let key = format!("charge.success:{}", charge.id);

    // 4. Handled it already? Then we're done.
    if payments.seen_event("paystack", &key).await? {
        return Ok(StatusCode::OK);
    }

    // 5. Do the work (it's safe twice), THEN record it.
    let seen = Seen { succeeded: charge.status == "success", amount: Kobo(charge.amount), currency: charge.currency };
    let outcome = payments.settle(&charge.reference, seen).await?;
    payments.record_event("paystack", &key).await?;
    tracing::info!(reference = charge.reference, ?outcome, "paystack webhook");
    Ok(StatusCode::OK)
}
```

Read it from top to bottom: the order is what keeps it safe.

1. **The signature first, before anything else.** Before reading the JSON, before looking anything up. An unsigned request gets a 401 and costs us one hash. The body is capped at 100 KB, because even checking a signature means reading the body, and a stranger could send gigabytes.
2. **Read it only after.** We never parse bytes from a stranger. `data` waits as a plain `serde_json::Value` until we know which event it is, and `from_value` then reads it as a `Charge`. (A neater idea, an enum with one variant per event and `#[serde(other)]` for the rest, doesn't work here: serde can't skip the `data` of an event it doesn't know. A test caught that, which is what tests are for.)
3. **Answer 200 to events we don't handle.** Paystack sends other events too: transfers, refunds, subscriptions. If we answered 404, Paystack would think delivery failed and send it again for days.
4. **Skip what we've handled.** Paystack's events don't carry an event ID of their own, so we make a key from the event's name and the charge's id, which is unique per payment.
5. **Work first, record second.** This order is on purpose. If we recorded "handled" first and then crashed before `settle`, Paystack's retry would be skipped as "seen", and Ada's payment would be lost for ever. Working first means the worst case is doing the work twice, and `settle` is built to be safe twice.

So the received-events table is a shortcut, not the real protection. The real protection is that `settle` is safe to repeat by itself; the table just saves repeating work. Whenever you handle a webhook, ask "what if this exact one arrives twice, at the same moment?", and make sure the answer is "nothing bad".

This route doesn't use lesson 15's idempotency middleware either. That needs a logged-in customer and a key they chose. Paystack has neither; the charge's id is its natural key, and `settle` is safe to repeat anyway.

`seen_event` and `record_event` are two small queries in the store: `SELECT EXISTS (...)`, and an `INSERT ... ON CONFLICT DO NOTHING`.

### Answer fast

Paystack waits only a short time for our 200. If we're slow, it counts as failed and comes again. Our handler runs a few quick queries, so we're fine. But if handling a payment ever means sending an email, a receipt and a notification, don't do it here. Record the payment, answer 200, and do the slow work afterwards. That's exactly what lesson 18 is for.

## Step 6: testing webhooks on your own laptop
<!-- bite: a0ac3769-29bc-4ac1-a42f-5a6a175dde72 -->

Paystack's servers can't reach `http://localhost:8080`. That's your laptop, not the internet.

During development, use a **tunnel**: a small program that gives you a public HTTPS address and passes everything it receives to your laptop. [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] shows how. Start one pointing at port 8080, copy its address, and in Paystack's dashboard (test mode) set the webhook URL to `https://<your-tunnel-address>/webhooks/paystack`. Pay with a test card, and watch the request arrive in your logs.

You can also sign a webhook yourself, which checks the signature code without any tunnel:

```bash
BODY='{"event":"charge.success","data":{"id":4099260516,"reference":"mp-11-0782ADB6E985A44A7B19963E","amount":300000,"currency":"NGN","status":"success"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha512 -hmac "$PAYSTACK_SECRET_KEY" | sed 's/^.* //')

curl -si -X POST localhost:8080/webhooks/paystack \
  -H "Content-Type: application/json" -H "X-Paystack-Signature: $SIG" \
  --data "$BODY" | head -1
```

```text
HTTP/1.1 200 OK
```

`openssl dgst -sha512 -hmac` makes the same HMAC our Rust code makes, and `sed 's/^.* //'` keeps only the hex at the end of its output. Use your own reference from step 4, and that order's amount. The log shows what happened:

```text
INFO request{method=POST path="/webhooks/paystack" ...}: mama_put::payments::webhook: paystack webhook reference="mp-11-0782ADB6E985A44A7B19963E" outcome=Paid
```

Send it again and you get another 200, with no log line: it was skipped as already handled. Now change one character after signing, with `--data "${BODY/300000/30000}"`, which pretends the amount was ₦300:

```text
HTTP/1.1 401 Unauthorized
{"type":"https://mamaput.example/problems/bad-webhook-signature","title":"Signature not valid","status":401,"detail":"The webhook signature is not valid.","code":"bad-webhook-signature","requestId":"88fd5dc5-3d27-4294-8aa2-bc43bb9aab73"}
```

## Step 7: the backup, verifying ourselves
<!-- bite: fca62369-ed53-4389-8b75-27342675eb1f -->

Webhooks are reliable, not perfect. Our server might be down for all the days Paystack keeps trying (it's rare, but it happens). Or a setting in the dashboard might be wrong. So there's a second path to the truth: asking Paystack directly.

When Ada lands back on our site, her app calls `GET /v2/payments/{reference}`, and the service does:

```rust
    /// A payment, for someone who may see its order. Still `started`? Ask Paystack ourselves first:
    /// the backup for a webhook that never came.
    pub async fn check(&self, who: Identity, reference: &str) -> Result<Payment, PaymentError> {
        let payment = self.store.find(reference).await?.ok_or(PaymentError::NotFound)?;
        // Someone else's payment is "no such payment", so references can't be probed.
        self.orders.get(payment.order_id, who).await.map_err(|e| match e {
            OrderError::NotFound(_) => PaymentError::NotFound,
            e => e.into(),
        })?;
        if payment.status != PaymentStatus::Started {
            return Ok(payment);
        }
        let seen = self.provider.verify(reference).await?;
        self.settle(reference, seen).await?;
        self.store.find(reference).await?.ok_or(PaymentError::NotFound)
    }
```

The browser's visit is only a *nudge* to go and ask Paystack. The answer comes from `verify`, made from our server with our secret key, and it goes through the same `settle` as the webhook. So whether the webhook or the verify call gets there first, the order is paid once, with the same checks.

```bash
curl -s localhost:8080/v2/payments/mp-12-8541E82DBE59839F159E7624 -H "Authorization: Bearer $TOKEN"
```

```json
{
    "data": {
        "reference": "mp-12-8541E82DBE59839F159E7624",
        "orderId": 12,
        "amount": {
            "amount": 300000,
            "currency": "NGN"
        },
        "status": "succeeded"
    }
}
```

Someone else's payment is the same `payment-not-found` as no payment at all: lesson 13's rule, so references can't be probed.

For payments still `started` after an hour, a scheduled job can run the same verify for each. That's the safety net under the safety net, and it's one of the jobs in lesson 18.

## Step 8: only paid orders get cooked
<!-- bite: f2ac69d7-580f-4b0f-8b70-634d53136905 -->

Now Mama's rule: the kitchen doesn't cook unpaid orders. In `src/orders/service.rs`, `set_status` now looks at the order first:

```rust
    /// Moves an order forward: pending → ready → collected. Never back, and never past pending unpaid.
    pub async fn set_status(&self, id: i64, to: Status) -> Result<Order, OrderError> {
        let order = self.store.find(id).await?.ok_or(OrderError::NotFound(id))?;
        // Checking first is safe here, unlike with plates: an order can't become unpaid again.
        if to != Status::Pending && !order.paid {
            return Err(OrderError::NotPaid);
        }
        let earlier: Vec<Status> = Status::ALL.into_iter().filter(|s| *s < to).collect();
        let Some(order) = self.store.set_status(id, to, &earlier).await? else {
            return Err(OrderError::BadStatusChange { from: order.status, to });
        };
        if to == Status::Ready {
            self.events.ready(&order).await?;
        }
        Ok(order)
    }
```

Checking first and changing after is the gap the guarded `UPDATE` exists to close, so why is it fine here? Because `paid` only ever goes one way. Two cooks can't both take the last plate, so plates needed one guarded statement. But an order can't become *unpaid* between the check and the change, so the check can't go stale in a way that matters. Always ask "can this change back in between?" before you choose.

The `self.events.ready(...)` line is for step 9. The kitchen screen in lesson 20 will show only paid orders, but the rule lives here, in the service, where no screen can skip it.

```text
{"type":"https://mamaput.example/problems/order-not-paid","title":"Not paid for yet","status":409,"detail":"this order hasn't been paid for yet","code":"order-not-paid", ...}
```

What about v1's orders, which have no customer and so can't start a checkout? And customers who simply pay at the counter? They pay in cash, and the kitchen records it:

```rust
/// For customers who pay at the counter: v1's, and anyone without a card.
async fn paid_in_cash<V: OrderVersion>(
    _kitchen: V::Kitchen<OrderMarkPaid>,
    State(orders): State<OrderService>,
    Path(id): Path<i64>,
) -> Result<Data<V::Order>, ApiError> {
    Ok(Data(orders.mark_paid(id).await?.into()))
}
```

with `.route("/orders/{id}/paid-in-cash", post(paid_in_cash::<V>))` in the order router, and a new permission, `OrderMarkPaid`, for staff. Because the guard is `V::Kitchen<OrderMarkPaid>` (lesson 13's generic associated type), v1's kitchen marks cash with the staff key and v2's with a staff login, from one handler. `OrderService::mark_paid` is a guarded `UPDATE ... WHERE id = $1 AND paid_at IS NULL`, so marking it twice is a 409 `order-already-paid`, not a second payment.

## Step 9: sending our own webhooks
<!-- bite: e3c31ce4-88b2-43e8-80ac-2a08ee68aaea -->

Now the other direction. When the kitchen marks order 42 ready, Okada Riders should hear about it at once. They've given us a URL, and we've agreed on a shared secret.

Sending a webhook is more than one POST. Everything we needed from Paystack, Okada Riders needs from us:

1. **A signature**, so they know it's really from us.
2. **A time inside the signature**, so nobody can record one of our webhooks and replay it next week.
3. **An event ID**, so they can ignore duplicates.
4. **Retries**, because their server will sometimes be down, and they're counting on at-least-once delivery.

### Writing it down first

When the order becomes ready, we don't call Okada Riders right there. We write the webhook into `webhook_deliveries` and carry on, and a separate sender picks it up.

The order service mustn't know about webhooks or Okada Riders, so it gets a trait, in `src/orders/service.rs`:

```rust
/// Whoever wants to hear when an order moves on. Orders only know this trait; `main` decides who listens.
#[async_trait]
pub trait OrderEvents: Send + Sync {
    async fn ready(&self, order: &Order) -> Result<(), StoreError>;
}
```

`OrderService` holds an `Arc<dyn OrderEvents>`, and `new` takes one: `OrderService::new(store, menu, events, clock)`. The order module says *what* it announces; `main` decides *who* hears. In `src/webhooks/okada.rs`:

```rust
use async_trait::async_trait;
use serde_json::json;

use super::Deliveries;
use crate::{
    clock::Clock,
    db::StoreError,
    orders::{Order, OrderEvents},
};

/// Okada Riders, the delivery company Mama works with. They hear when an order is ready, by webhook.
pub struct OkadaRiders {
    pub deliveries: Deliveries,
    pub url: String,
    pub clock: Clock,
}

#[async_trait]
impl OrderEvents for OkadaRiders {
    async fn ready(&self, order: &Order) -> Result<(), StoreError> {
        // Only what a rider needs. No name, no email, no phone: what we send, we can't take back.
        let data = json!({
            "orderId": order.id.to_string(),
            "dishId": order.dish_id.to_string(),
            "quantity": order.quantity,
            "readyAt": self.clock.now().to_string(),
        });
        self.deliveries.enqueue(&self.url, "order.ready", &data).await
    }
}
```

Notice what's **not** in the data: Ada's name, email or phone. The rider needs to know an order is ready at Mama's; they don't need her details until a delivery is booked, and then through Okada Riders' own system. Send another company only what it needs. Everything you send, you can't take back.

The queue, `src/webhooks/deliveries.rs`:

```rust
use std::time::Duration;

use serde::Serialize;
use serde_json::Value;
use sqlx::PgPool;

use crate::db::StoreError;

/// One webhook to send.
#[derive(Clone, Debug)]
pub struct Delivery {
    /// The same on every try, so the partner can skip duplicates.
    pub id: String,
    pub url: String,
    pub event_type: String,
    pub payload: Value,
    /// Tries so far, counting the one about to happen.
    pub attempts: i32,
}

/// The queue of webhooks to send, in PostgreSQL, so a restart loses none.
#[derive(Clone)]
pub struct Deliveries {
    pool: PgPool,
}

impl Deliveries {
    pub fn new(pool: PgPool) -> Self {
        Deliveries { pool }
    }

    pub async fn enqueue(&self, url: &str, event_type: &str, data: &impl Serialize) -> Result<(), StoreError> {
        let payload = serde_json::to_value(data).expect("event data is always JSON");
        sqlx::query!("INSERT INTO webhook_deliveries (url, event_type, payload) VALUES ($1, $2, $3)", url, event_type, payload)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    /// Takes up to `limit` webhooks that are due, for this sender alone, for one minute.
    pub async fn claim_due(&self, limit: i64) -> Result<Vec<Delivery>, StoreError> {
        let due = sqlx::query_as!(
            Delivery,
            r#"UPDATE webhook_deliveries
                  SET attempts = attempts + 1,
                      next_attempt_at = now() + interval '1 minute'
                WHERE id IN (
                      SELECT id FROM webhook_deliveries
                       WHERE delivered_at IS NULL AND next_attempt_at <= now()
                       ORDER BY next_attempt_at
                       LIMIT $1
                       FOR UPDATE SKIP LOCKED)
            RETURNING id::text AS "id!", url, event_type, payload, attempts"#,
            limit
        )
        .fetch_all(&self.pool)
        .await?;
        Ok(due)
    }

    pub async fn mark_delivered(&self, id: &str) -> Result<(), StoreError> {
        sqlx::query!("UPDATE webhook_deliveries SET delivered_at = now(), last_error = NULL WHERE id = $1::text::uuid", id)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    /// Tries again after `retry_in`, or never (`None`): it stays in the table for a person to see.
    pub async fn mark_failed(&self, id: &str, error: &str, retry_in: Option<Duration>) -> Result<(), StoreError> {
        sqlx::query!(
            "UPDATE webhook_deliveries
                SET last_error = $2,
                    next_attempt_at = CASE WHEN $3::float8 IS NULL THEN 'infinity' ELSE now() + $3 * interval '1 second' END
              WHERE id = $1::text::uuid",
            id,
            error,
            retry_in.map(|d| d.as_secs_f64())
        )
        .execute(&self.pool)
        .await?;
        Ok(())
    }
}
```

Why write it down instead of sending at once? Three reasons. The cook's tap on "ready" doesn't wait for Okada Riders' server. If their server is down, the webhook isn't lost; it's sitting in a table. And a restart of our app loses nothing, because the queue is in Postgres, not in memory.

The ids are `uuid`s, and the sqlx macros would want the `uuid` crate to read them. We never do anything with an id except pass it back, so `id::text AS "id!"` reads it as text, and `$1::text::uuid` turns it back. `payload` is `jsonb`, which sqlx reads as a `serde_json::Value`. (Postgres keeps `jsonb` keys in its own order, so `dishId` comes back before `orderId`. JSON doesn't care.)

(One honest gap: the status change and the `enqueue` are two separate queries. If the app crashed exactly between them, the order would be ready and the webhook never written. Putting both in one transaction fixes it, and doing that properly, for events between services, is the **outbox** in lesson 29.)

### The sender

`src/webhooks/sender.rs`:

```rust
use std::{sync::Arc, time::Duration};

use axum::http::header;
use reqwest::{Client, redirect};
use serde_json::json;

use super::deliveries::{Deliveries, Delivery};
use crate::{
    clock::Clock,
    db::StoreError,
    signing::{HmacSha256, sign_hex, verify_hex},
};

/// After this many tries, about a day and a half, we stop and leave it for a person.
const MAX_ATTEMPTS: i32 = 15;

/// Sends the webhooks that are due, a few at a time.
pub struct Sender {
    deliveries: Deliveries,
    secret: Arc<str>,
    client: Client,
    clock: Clock,
}

impl Sender {
    pub fn new(deliveries: Deliveries, secret: &str, clock: Clock) -> Result<Self, reqwest::Error> {
        let client = Client::builder()
            .timeout(Duration::from_secs(5)) // a slow partner mustn't hold up the queue
            .redirect(redirect::Policy::none()) // never follow them somewhere we didn't agree to send
            .build()?;
        Ok(Sender { deliveries, secret: secret.into(), client, clock })
    }

    async fn send(&self, delivery: &Delivery) -> Result<(), String> {
        let body = json!({"id": delivery.id, "type": delivery.event_type, "data": delivery.payload}).to_string();
        let sent_at = self.clock.now().as_second();
        // The time is inside what's signed, so a recorded webhook is useless later.
        let signature = sign_hex::<HmacSha256>(self.secret.as_bytes(), format!("{sent_at}.{body}").as_bytes());

        let response = self
            .client
            .post(&delivery.url)
            .header(header::CONTENT_TYPE, "application/json")
            .header("mamaput-event-id", &delivery.id)
            .header("mamaput-signature", format!("t={sent_at},v1={signature}"))
            .body(body)
            .send()
            .await
            .map_err(|e| e.to_string())?;
        if response.status().is_success() { Ok(()) } else { Err(format!("answered {}", response.status())) }
    }

    /// Sends every webhook that's due now, and says how many it tried. Tests call it directly.
    pub async fn run_once(&self) -> Result<usize, StoreError> {
        let due = self.deliveries.claim_due(10).await?;
        for delivery in &due {
            match self.send(delivery).await {
                Ok(()) => self.deliveries.mark_delivered(&delivery.id).await?,
                Err(error) => {
                    let retry_in = (delivery.attempts < MAX_ATTEMPTS).then(|| backoff(delivery.attempts));
                    self.deliveries.mark_failed(&delivery.id, &error, retry_in).await?;
                    tracing::warn!(id = delivery.id, attempts = delivery.attempts, giving_up = retry_in.is_none(), error, "webhook not delivered");
                }
            }
        }
        Ok(due.len())
    }

    /// Sends what's due every `every`, for as long as the program runs.
    pub async fn run(self, every: Duration) {
        let mut ticks = tokio::time::interval(every);
        loop {
            ticks.tick().await;
            if let Err(e) = self.run_once().await {
                tracing::error!(cause = %e, "webhook sender");
            }
        }
    }
}

/// 30 s, 1 min, 2, 4, ... up to 6 hours between tries, plus up to a fifth more, at random.
fn backoff(attempts: i32) -> Duration {
    let doublings = u32::try_from(attempts - 1).unwrap_or(0);
    let base = Duration::from_secs(30).saturating_mul(2u32.saturating_pow(doublings)).min(Duration::from_secs(6 * 60 * 60));
    let random = f64::from(getrandom::u32().unwrap_or(0)) / f64::from(u32::MAX); // 0.0 to 1.0
    base + base.mul_f64(random / 5.0)
}
```

A lot of small decisions, each one learned the hard way by someone:

1. **What's signed is `time.body`**, not just the body. The receiver checks the time is recent, so a webhook recorded today is useless next week, even though its signature is real.
2. **`mamaput-event-id`** is the delivery's id, the same on every retry. That's what lets Okada Riders skip duplicates.
3. **Only 2xx counts.** A redirect, a 404, a 500: all failures. reqwest follows redirects by itself, up to ten. `redirect::Policy::none()` stops that, so a 302 comes back to us as a 302, and counts as a failure.
4. **A 5-second timeout**, on a client of its own. A slow partner mustn't hold up the queue.
5. **Backoff that grows**: 30 seconds, then 1 minute, 2, 4, and so on, up to 6 hours between tries. If their server is down for an hour, knocking every 5 seconds helps nobody, and may be part of why it's down. In Rust, numbers that grow too big **panic** in a debug build, so `saturating_pow` and `saturating_mul` stop at the biggest value instead, and `.min` caps it at 6 hours.
6. **Jitter.** If 500 webhooks failed at the same moment, without jitter they'd all retry at the same moment too, and knock the partner over again. A random fifth extra spreads them out. `getrandom` is stronger randomness than jitter needs, but it's already in the project and it's cheap.
7. **Give up eventually**, and log it, so a person can look. Fifteen tries, with the gaps capped at 6 hours, take about a day and a half. A delivery we give up on gets `next_attempt_at = 'infinity'`, Postgres's "later than any date", so it's never picked again but stays in the table.
8. **`run` takes `self`, not `&self`.** It runs for as long as the program does, in a task of its own, and a task must own everything it uses.

### Claiming work safely

`claim_due` is where two copies of our app could trip over each other. Run two servers (we will, in lesson 36), and both senders wake up every 5 seconds. Without care, both pick the same webhook and send it twice. Two things in its SQL make that safe:

1. **`FOR UPDATE SKIP LOCKED`** locks the rows this sender picks, and tells any other sender looking at the same moment to *skip* locked rows instead of waiting for them. So two senders take different webhooks.
2. **Pushing `next_attempt_at` a minute forward** is a lease: "this is mine for a minute". If our server dies halfway through a send, the row isn't stuck for ever. A minute later it's due again, and someone else picks it up.

And yes: this is a small, hand-made job queue. In lesson 18 we hand jobs like this to a real queue, and having built one yourself, you'll know exactly what it does for you.

`main` starts it, beside the server:

```rust
    // Okada Riders' webhooks go out from here, beside the server, every 5 seconds.
    let sender = Sender::new(deliveries, &env("OKADA_WEBHOOK_SECRET")?, Clock::system())?;
    tokio::spawn(sender.run(Duration::from_secs(5)));
```

`tokio::spawn` starts `run` as its own task and carries on at once, so it ticks away while the server answers requests. When `main` returns, the runtime stops, and the task stops with it at its next `.await`. (Lesson 36 makes stopping tidier, so a delivery half sent is finished first.)

### What Okada Riders does with it

They'll ask "how do we check your signature?", so write it down for them. This is the check on *their* side. It lives in `sender.rs`, so our tests can check our webhooks exactly the way a partner would:

```rust
/// What Okada Riders runs to check a webhook is from us: the right signature, sent in the last 5 minutes.
/// It lives here so our tests can check our own webhooks the way a partner would.
pub fn is_from_mama_put(body: &[u8], header: &str, secret: &str, now: jiff::Timestamp) -> bool {
    let (mut sent_at, mut signature) = (None, None);
    for part in header.split(',') {
        match part.split_once('=') {
            Some(("t", value)) => sent_at = value.parse::<i64>().ok(),
            Some(("v1", value)) => signature = Some(value),
            _ => {}
        }
    }
    let (Some(sent_at), Some(signature)) = (sent_at, signature) else {
        return false;
    };
    if (now.as_second() - sent_at).abs() > 5 * 60 {
        return false; // older than 5 minutes: a replay
    }
    let mut message = format!("{sent_at}.").into_bytes();
    message.extend_from_slice(body);
    verify_hex::<HmacSha256>(secret.as_bytes(), &message, signature.as_bytes())
}
```

Then they check `mamaput-event-id` against the ids they've already seen, answer 200 quickly, and do their work. It's everything we did for Paystack, from the other side. Good webhook design is being the sender you'd want to receive from.

One more thing worth knowing. Here the URL comes from our own settings. Some products let *customers* type in their own webhook URL. Then you must check it doesn't point inside your own network, or someone sets their URL to `http://169.254.169.254/` or `http://localhost:5432` and makes your server attack itself. That's called **SSRF** (server-side request forgery), and lesson 14's rule applies: treat the URL as hostile input. Check the address *after* the name is looked up, because a friendly-looking name can point anywhere.

## Step 10: a pretend partner, for trying it
<!-- bite: f36db0aa-87b0-4ef9-ac3b-06e7e11be061 -->

To watch our webhooks arrive, run a tiny partner on your laptop. Rust has a place for small extra programs that use your library: the `examples/` folder. `examples/fake_okada.rs`:

```rust
//! A pretend Okada Riders, for watching our webhooks arrive. A toy for your own laptop: never ship it.
//!
//! cargo run --example fake_okada

use axum::{Router, body::Bytes, http::HeaderMap, routing::post};
use mama_put::webhooks::is_from_mama_put;

#[tokio::main]
async fn main() {
    dotenvy::dotenv().ok();
    let secret = std::env::var("OKADA_WEBHOOK_SECRET").expect("set OKADA_WEBHOOK_SECRET");
    let hook = move |headers: HeaderMap, body: Bytes| async move {
        let header = |name: &str| headers.get(name).and_then(|v| v.to_str().ok()).unwrap_or("").to_owned();
        let signed = is_from_mama_put(&body, &header("mamaput-signature"), &secret, jiff::Timestamp::now());
        println!("{} signed={signed}\n{}\n", header("mamaput-event-id"), String::from_utf8_lossy(&body));
    };
    let listener = tokio::net::TcpListener::bind("127.0.0.1:9090").await.unwrap();
    axum::serve(listener, Router::new().route("/hooks/mama-put", post(hook))).await.unwrap();
}
```

```bash
cargo run --example fake_okada
```

Run it from the project folder, where `.env` is. (It's a toy on your own machine, so the lesson 1 rule about timeouts doesn't apply. Never ship it.) Pay for an order, mark it ready as staff, and within 5 seconds the pretend partner prints:

```text
219fd91f-963f-41c4-9f93-685982a55104 signed=true
{"id":"219fd91f-963f-41c4-9f93-685982a55104","type":"order.ready","data":{"dishId":"5","orderId":"11","readyAt":"2026-11-22T19:51:43.693884125Z","quantity":1}}
```

Now stop it, mark another order ready, and look at the delivery:

```text
 attempts | delivered | retry_in_s |                              last_error
----------+-----------+------------+----------------------------------------------------------------------
        1 | f         |         29 | error sending request for url (http://localhost:9090/hooks/mama-put)
```

Start it again. Within a couple of minutes the retry arrives, with the same event id as the try that failed, and `signed=true`.

## Step 11: testing it
<!-- bite: 441d7d40-9339-491d-bac6-641ef4992bd5 -->

Lesson 16's harness covers all of this without Paystack or Okada Riders running.

**First, a test that broke.** `src/docs.rs` had its own test, from lesson 11, that built `AppState` by hand. The two new fields broke it, which is exactly what lesson 16's first practice warned about. It now lives in `tests/docs.rs` and uses `TestApp`, so the next new field changes one place. Another old test broke too: the order service test that empties its tables with `TRUNCATE orders, dishes`. Postgres refuses to empty `orders` while `payments` points at it; `TRUNCATE ... CASCADE` empties the tables that point at it as well.

**Paystack, for the client's own tests, is a real server on a local port.** The real `Paystack` type talks to it, so the code that builds requests and checks answers is tested too. At the end of `src/payments/paystack.rs`:

```rust
#[cfg(test)]
mod tests {
    use std::time::Duration;

    use axum::{Router, http::HeaderMap, routing::get};
    use tokio::net::TcpListener;

    use super::*;

    /// A pretend Paystack on a random local port, answering every request with `app`.
    async fn pretend_paystack(app: Router) -> Url {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let address = listener.local_addr().unwrap();
        tokio::spawn(async move { axum::serve(listener, app).await.unwrap() });
        format!("http://{address}").parse().unwrap()
    }

    fn client(timeout: Duration) -> Client {
        Client::builder().timeout(timeout).build().unwrap()
    }

    #[tokio::test]
    async fn verify_reads_a_success() {
        let app = Router::new().route(
            "/transaction/verify/{reference}",
            get(|headers: HeaderMap| async move {
                if headers["authorization"] != "Bearer sk_test_x" {
                    return (axum::http::StatusCode::UNAUTHORIZED, String::new());
                }
                (axum::http::StatusCode::OK, r#"{"status":true,"data":{"status":"success","amount":300000,"currency":"NGN"}}"#.into())
            }),
        );
        let paystack = Paystack::new(pretend_paystack(app).await, "sk_test_x", client(Duration::from_secs(5)));

        let seen = paystack.verify("mp-1-ABC").await.unwrap();
        assert_eq!(seen, Seen { succeeded: true, amount: Kobo(300000), currency: "NGN".into() });
    }

    #[tokio::test]
    async fn verify_turns_every_letdown_into_a_provider_error() {
        let cases: [(&str, Router, Duration); 3] = [
            ("a 500", Router::new().fallback(|| async { axum::http::StatusCode::INTERNAL_SERVER_ERROR }), Duration::from_secs(5)),
            ("not JSON", Router::new().fallback(|| async { "<html>oops</html>" }), Duration::from_secs(5)),
            (
                "never answers",
                Router::new().fallback(|| async {
                    tokio::time::sleep(Duration::from_secs(10)).await;
                    "too late"
                }),
                Duration::from_millis(50),
            ),
        ];
        for (name, app, timeout) in cases {
            let paystack = Paystack::new(pretend_paystack(app).await, "sk_test_x", client(timeout));
            let got = paystack.verify("mp-1-ABC").await;
            let ok = match name {
                "a 500" => matches!(got, Err(ProviderError::Refused(500))),
                "not JSON" => matches!(got, Err(ProviderError::BadResponse(_))),
                _ => matches!(got, Err(ProviderError::Unreachable(_))),
            };
            assert!(ok, "{name}: got {got:?}");
        }
    }
}
```

`127.0.0.1:0` asks for any free port, so tests never fight over one. The pretend server runs in a spawned task and stops when the test ends. The "never answers" case gives the client a 50 ms timeout and makes the server sleep for 10 seconds, so the test proves a hanging Paystack becomes `Unreachable`, quickly.

**For the whole-app tests, the provider is a fake** that answers `verify` from a map. In `tests/common/mod.rs`:

```rust
/// A pretend Paystack: checkout links that go nowhere, and whatever answers a test sets for `verify`.
#[derive(Default)]
pub struct FakePaystack {
    pub answers: Mutex<HashMap<String, Seen>>,
}

#[async_trait::async_trait]
impl Provider for FakePaystack {
    async fn start_checkout(&self, _email: &str, _amount: Kobo, reference: &str, _callback: &str) -> Result<String, ProviderError> {
        Ok(format!("https://checkout.paystack.test/{reference}"))
    }

    async fn verify(&self, reference: &str) -> Result<Seen, ProviderError> {
        let answers = self.answers.lock().unwrap();
        answers.get(reference).cloned().ok_or(ProviderError::Refused(404))
    }
}
```

`TestApp` builds the real `PaymentService` with it, gives the app `WebhookSecret::new(PAYSTACK_SECRET)`, points Okada Riders at a URL nobody answers, and gains three helpers: `order` places one, `paystack_webhook` signs a body exactly as Paystack would, and `is_paid` asks the database. The signing one:

```rust
    /// Sends a webhook signed exactly as Paystack would sign it.
    pub fn paystack_webhook(&self, body: &str) -> Call<'_> {
        let signature = sign_hex::<HmacSha512>(PAYSTACK_SECRET.as_bytes(), body.as_bytes());
        self.post("/webhooks/paystack").header("x-paystack-signature", &signature).raw(body)
    }
```

`raw` sends a body exactly as given, as a string, so the bytes we signed are the bytes that arrive. `tests/payments.rs` has seven tests. The one that matters most:

```rust
#[sqlx::test]
async fn a_webhook_pays_once_however_often_it_arrives(pool: PgPool) {
    let app = TestApp::new(pool);
    let (_, order, reference) = ada_starts_paying(&app).await;
    let body = charge(&reference, 150000);

    // Paystack sends the same news three times at once.
    let replies = join_all((0..3).map(|_| app.paystack_webhook(&body).send())).await;
    assert!(replies.iter().all(|r| r.status == StatusCode::OK), "{replies:?}");

    assert!(app.is_paid(order).await);
    let settled = sqlx::query_scalar!(r#"SELECT count(*) AS "n!" FROM payments WHERE status = 'succeeded'"#).fetch_one(&app.pool).await.unwrap();
    assert_eq!(settled, 1);
}
```

And the others:

1. `a_checkout_is_for_our_amount_and_only_the_owner_starts_one`: the payment row asks for ₦1,500 in kobo, and Bayo gets 404 for Ada's order.
2. `the_webhook_and_the_verify_call_at_once_settle_once`: `settle` three times at once gives one `Paid` and two `AlreadySettled`.
3. `a_forged_webhook_changes_nothing`: no signature, an empty one, and a signed body changed on the way all get 401, and the order stays unpaid.
4. `the_wrong_amount_is_never_believed`: one kobo short gets 200 but no payment, and `transfer.success` gets 200 and changes nothing.
5. `without_a_webhook_we_ask_paystack_ourselves`: the fake says "success", `GET /v2/payments/{reference}` pays the order, and Bayo gets 404.
6. `only_paid_orders_get_cooked`: `ready` is 409 until the cook takes cash, and then one `order.ready` delivery is waiting, with nothing about Ada in it.

The permissions table from lesson 16 gets two rows: paying for Ada's order (nobody 401, Ada 201, the cook and the admin 404) and taking cash (nobody 401, Ada 403, the cook 200, and the admin 409, because by then it's paid).

**The sender is tested against a pretend Okada Riders**, in `tests/webhooks.rs`, which fails twice and then says 200, checking each signature with `is_from_mama_put`:

```rust
#[sqlx::test]
async fn a_webhook_is_retried_until_it_lands_with_the_same_id(pool: PgPool) {
    let (url, received) = okada_riders(2).await;
    let deliveries = Deliveries::new(pool.clone());
    deliveries.enqueue(&url, "order.ready", &json!({"orderId": "42"})).await.unwrap();
    let sender = Sender::new(deliveries, SECRET, Clock::system()).unwrap();

    for _ in 0..3 {
        assert_eq!(sender.run_once().await.unwrap(), 1, "one delivery was due");
        // Don't wait out the backoff: make it due again now.
        sqlx::query!("UPDATE webhook_deliveries SET next_attempt_at = now()").execute(&pool).await.unwrap();
    }
    assert_eq!(sender.run_once().await.unwrap(), 0, "delivered, so nothing is due");

    let row = sqlx::query!(r#"SELECT attempts, delivered_at IS NOT NULL AS "delivered!" FROM webhook_deliveries"#).fetch_one(&pool).await.unwrap();
    assert_eq!((row.attempts, row.delivered), (3, true));
    let received = received.lock().unwrap();
    assert_eq!(received.len(), 3, "two failures, then a success");
    assert!(received.iter().all(|(id, signed)| *id == received[0].0 && *signed), "same id, signed, every time: {received:?}");
}
```

`run_once` is public for exactly this: the test calls it three times instead of waiting for the timer, and moves `next_attempt_at` back between tries instead of waiting out the backoff. A second test checks `is_from_mama_put` refuses a correct signature that's 6 minutes old.

**A mutation check, as in lesson 16.** Take `AND status = 'started'` out of `mark_succeeded` and run the tests. The race test fails:

```text
assertion `left == right` failed: [Paid, OrderWasAlreadyPaid, OrderWasAlreadyPaid]
  left: (1, 0)
 right: (1, 2)
```

The order is still paid once, because of the `paid_at IS NULL` guard on the order. But without the guard on the payment, the two late callers each think a *second* payment arrived, and each logs "order paid twice, refund needed". Someone would refund Ada money she never paid twice. Put the guard back.

```bash
cargo test
```

54 tests, all passing.

## The Rust in this lesson
<!-- bite: b113fddb-e8b8-49c0-8d3d-8a07332f5aa4 -->

1. **`reqwest::Client::builder().timeout(...).build()?`**: Builds an HTTP client. It keeps a pool of connections, and cloning it is cheap, so make one and share it. A client has no timeout unless you set one.
2. **`client.post(url).bearer_auth(key).json(&body).send().await`**: A request built step by step, then sent. `json` turns any `Serialize` value into the body; `bearer_auth` adds `Authorization: Bearer ...`.
3. **`while let Some(chunk) = response.chunk().await?`**: Reads a response a piece at a time, so the code can stop once it has read too much. `while let` loops for as long as the pattern matches.
4. **`url.path_segments_mut()...extend(segments)`**: Adds pieces to a URL's path, escaping each one.
5. **`Bytes`, as an extractor**: The whole body, untouched. A body can be read once, so only a handler's last argument may take it.
6. **Generic functions with trait bounds**, `fn sign_hex<M: Mac + KeyInit>(...)`: One function for any type with those abilities. The caller picks the type with a **turbofish**, `sign_hex::<HmacSha256>(...)`, when Rust can't work it out alone.
7. **Type aliases**, `pub type HmacSha512 = Hmac<Sha512>;`: A short name for a longer type. They're the same type, not a new one.
8. **`mac.verify_slice(&tag)`**: Compares a MAC in constant time, and refuses a tag of the wrong length.
9. **`serde_json::Value`** and **`serde_json::from_value`**: Any JSON at all, kept to be read later into the type you choose once you know what it is. `#[serde(default)]` lets the field be missing.
10. **`#[async_trait]` traits as events**, `Arc<dyn OrderEvents>`: The order module announces; whoever `main` plugs in listens. The same tool as lesson 5's stores.
11. **`bool::then`**, `(attempts < MAX).then(|| backoff(attempts))`: `Some(...)` when true, `None` when false. The closure only runs when it's needed.
12. **`saturating_pow`, `saturating_mul`, `Duration::min`, `mul_f64`**: Arithmetic that stops at the biggest value instead of overflowing, and a `Duration` multiplied by a fraction.
13. **`u32::try_from(n).unwrap_or(0)`**: A careful conversion between number types: negative numbers don't fit in a `u32`, so they become 0.
14. **`tokio::spawn(future)`** and **`tokio::time::interval`**: Runs a future as its own task, beside the server. An interval ticks every period, and its first tick comes at once.
15. **`split_once('=')`** and **patterns with literals**, `Some(("t", value))`: Splits a string in two at the first `=`; the pattern matches only when the first half is exactly `"t"`.
16. **`let (Some(a), Some(b)) = (x, y) else { ... }`**: Two things that must both be there, checked in one line.
17. **`examples/`** and **`cargo run --example name`**: Small extra programs that use your library. They're built only when you ask.
18. **`TcpListener::bind("127.0.0.1:0")`**: Any free port, for a test server that never clashes with another test.

## Your project so far
<!-- bite: ead6af18-7173-4860-81ac-c3d7ded592b9 -->

```text
mama-put/
├── .env                          ← PAYSTACK_SECRET_KEY, PUBLIC_URL, OKADA_WEBHOOK_URL, OKADA_WEBHOOK_SECRET
├── Cargo.toml                    ← reqwest (json), hmac
├── migrations/
│   ├── 0008_payments.sql         ← NEW: payments (one row per attempt); orders.paid_at
│   └── 0009_webhooks.sql         ← NEW: webhook_events_received; webhook_deliveries (partial index)
├── examples/
│   └── fake_okada.rs             ← NEW: a pretend partner that prints and checks what it receives (never shipped)
├── src/
│   ├── main.rs                   ← Paystack client with an 8 s timeout, payments, Okada Riders, the sender task
│   ├── lib.rs                    ← payments in v2 behind idempotency; /webhooks/paystack outside the versions
│   ├── signing.rs                ← NEW: sign_hex, verify_hex, generic over the HMAC
│   ├── auth/policy.rs            ← OrderPay (owner only), OrderMarkPaid (staff)
│   ├── orders/
│   │   ├── model.rs              ← Order.paid
│   │   ├── store.rs              ← paid in every query; mark_paid
│   │   ├── service.rs            ← OrderEvents; set_status: not past pending unpaid; mark_paid
│   │   ├── handlers.rs           ← POST /orders/{id}/paid-in-cash; order-not-paid, order-already-paid
│   │   └── versions.rs           ← OrderV2.paid
│   ├── payments/                 ← NEW
│   │   ├── mod.rs                ← the front counter
│   │   ├── model.rs              ← Payment, Checkout, Seen, Outcome
│   │   ├── provider.rs           ← Provider trait, ProviderError (502)
│   │   ├── paystack.rs           ← start_checkout, verify: escaped URLs, capped and checked answers
│   │   ├── service.rs            ← start_checkout, settle (the one place), check (the verify backup)
│   │   ├── store.rs              ← mark_succeeded (guarded UPDATE in a transaction), received events
│   │   ├── handlers.rs           ← POST /v2/orders/{id}/payments, GET /v2/payments/{reference}
│   │   └── webhook.rs            ← POST /webhooks/paystack: Bytes, signature, read, skip, settle, record
│   └── webhooks/                 ← NEW
│       ├── mod.rs                ← the front counter
│       ├── deliveries.rs         ← enqueue, claim_due (SKIP LOCKED + lease), mark_delivered, mark_failed
│       ├── okada.rs              ← OkadaRiders: OrderEvents as an order.ready webhook, no customer details
│       └── sender.rs             ← signed time.body, event id, timeout, no redirects, backoff + jitter; is_from_mama_put
└── tests/
    ├── common/mod.rs             ← FakePaystack, paystack_webhook, raw bodies, order, is_paid
    ├── docs.rs                   ← NEW: lesson 11's docs test, moved here onto TestApp
    ├── payments.rs               ← NEW: 7 tests
    ├── permissions.rs            ← two more rows: paying, and taking cash
    └── webhooks.rs               ← NEW: retried until delivered with one id; old signatures refused
```

## Common mistakes
<!-- bite: 5d1ae4be-adfd-4c8b-a63d-3fc836971915 -->

1. **Marking an order paid from the redirect.** Anyone can visit that URL. Only a signed webhook or your own verify call counts.
2. **Taking the amount from the request.** Read it from your database.
3. **Taking the webhook body as `Json<T>`.** The bytes are gone before you can check them. Take `Bytes`, check, then parse.
4. **Comparing signatures with `==`.** Use `verify_slice`, which takes the same time whatever the answer.
5. **A `reqwest::Client` with no timeout, or `reqwest::get` for outside calls.** One hanging service hangs your requests. Set a timeout under your own.
6. **A new `Client` for every request.** It throws away the connection pool, and every call pays for a new TLS handshake. Make one and clone it.
7. **Recording a webhook as handled before handling it.** A crash in between loses it for ever. Work first, record second, and make the work safe to repeat.
8. **Answering 404 or 400 to events you don't handle.** The sender retries for days. Answer 200.
9. **Sending partners more than they need.** No customer details in a "ready" webhook.
10. **Retrying at a fixed interval, with no jitter.** You'll knock on a struggling partner's door, all at once, again and again.
11. **Following redirects when sending webhooks.** Stop them, and count them as failures.

## Check your understanding
<!-- bite: 26f5f3a6-aa8e-49d7-8185-44cfe6814321 -->

1. Why can't Mama Put mark an order paid when Ada's browser lands on `/payment-done`?
2. Paystack sends the same `charge.success` three times at once. Follow it through: what stops the order being counted three times?
3. Why does the webhook handler run `settle` *before* recording the event as received?
4. Why does the webhook handler take `Bytes` and not `Json<Event>`, and why must `body` be its last argument?
5. The net/http version gave webhooks their own middleware chain. Why doesn't the Axum version need one?
6. `set_status` checks `paid` first and changes the status after. Why is that safe here, when the last plate needed one guarded statement?
7. Why is the time inside our outgoing signature, and what does Okada Riders do with it?
8. Two copies of our app run the sender at the same moment. Why don't they send the same webhook twice?

<details>
<summary>Answers, after your attempt</summary>

1. Because the browser is the customer's: anyone can type that URL without paying, and a customer who closes the tab early never visits it. Only Paystack, through a signed webhook or our own verify call, can say a payment happened.
2. All three pass the signature check, and all three may find the event not yet recorded, so all three call `settle`. But `mark_succeeded`'s `UPDATE ... WHERE status = 'started'` changes the row for only one of them; the others find it already `succeeded` and get `AlreadySettled`. The order's `paid_at` is set once.
3. So a crash in between can't lose the payment. If we recorded first and crashed, Paystack's retry would be skipped as "already seen". Working first means the worst case is running `settle` twice, which is safe.
4. The signature covers the exact bytes, and `Json` throws them away once it has made the struct; JSON written again can differ byte by byte. `Bytes` hands them over untouched. A body can be read only once, so Axum lets only the last argument take it; `HeaderMap` and `State` read only the head, so they go first.
5. Because nothing we'd need to leave out runs on every request. The rate limit is only on the password routes, logins are extractors that a handler asks for, and idempotency is only on v2's order and payment routes. The webhook route just doesn't ask for them. All it changes is the body limit, and the innermost limit wins.
6. Because `paid` only ever goes from no to yes. Between the check and the change, an order can't become unpaid, so the check can't go stale in a way that matters. Plates can be taken by someone else in between, so they needed the check and the change in one statement.
7. So a recorded webhook can't be replayed later: the signature covers the time it was sent. Okada Riders refuses any webhook whose time is more than 5 minutes from their clock, even when the signature is right.
8. `FOR UPDATE SKIP LOCKED`: each sender locks the rows it claims, and the other skips locked rows instead of waiting for them. And the claim pushes `next_attempt_at` a minute forward, so even after the lock is released, nobody else picks it up until that lease runs out.

</details>

## Practice
<!-- bite: 2fa04d0e-fa26-42ec-a2e7-7e32345f0e3f -->

1. Add the payment routes to lesson 11's docs: `#[utoipa::path]` on empty functions for `POST /v2/orders/{id}/payments` (with a 502 problem response) and `GET /v2/payments/{reference}`, and `CheckoutV2` and `PaymentV2` in the schemas. The docs test's count goes from 16 to 18, and the test proves both are real routes.
2. Write a `#[sqlx::test]` for `PgPaymentStore` on its own: `mark_failed` changes only a `started` payment, and `record_event` twice is fine.
3. Add a test that a webhook to a partner answering `302` counts as a failure, not a delivery.
4. Add `Paystack::start_checkout` tests like the `verify` ones, including an answer whose `authorization_url` is `http://`.
5. Do a mutation check of your own: swap the order of `settle` and `record_event` in the webhook handler. Does any test fail? If not, write one that would. (Hint: make `settle` fail once.)

**Done when** a test-mode payment marks its order paid through the webhook (with a tunnel) or through `GET /v2/payments/{reference}` (without one); a forged webhook gets 401; the kitchen can't mark an unpaid order ready; `cargo run --example fake_okada` prints a signed `order.ready` event; and `cargo test` runs 54 tests and passes.

## Before moving on
<!-- bite: 98fd5d9d-40e7-4023-8408-ee10299bafb0 -->

Mama Put API now takes real money. Payments start from our own numbers, become "paid" only on Paystack's signed word or our own check, and count exactly once however many times the news arrives. And Okada Riders hears about every ready order, signed, timed and retried until they've got it.

But look at what the sender really is: a loop in our API process, reading a table every 5 seconds. It's fine for one kind of job. Mama now wants more: a receipt email after payment, a reminder if an order sits unpaid for 15 minutes, a sales summary every night, and those checks on payments left `started`. Each could be its own little loop, but then we'd be writing a job system by hand, badly. That's background jobs, the next lesson.

## Related
<!-- bite: 07d3c63a-fffd-4bd3-a78e-31613ea87975 -->

- [[backend/frameworks/axum/18-background-jobs|Next: Background Jobs and Queues]]
- [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] — receiving webhooks on your laptop
- [[backend/frameworks/net-http/17-payments-and-webhooks|The same lesson in net/http]] — where webhooks need their own middleware chain
- [[backend/frameworks/axum/15-idempotency|Idempotency]] — why "safe to repeat" is the real protection

## About this lesson
<!-- bite: c7d3e011-f549-448c-b5c8-a49882f0e05f -->

**Level:** Advanced. Lesson 17 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, sqlx 0.9, reqwest 0.13 and hmac 0.13, against Paystack's test mode. Covers why payments span requests, a provider trait and a Paystack client with a timeout under the app's own, cancellation by dropping, capped and checked answers and escaped URLs, 502 for an outside service, one idempotent `settle` guarded in SQL, an owner-only payment permission, verifying HMAC-SHA512 webhook signatures on raw `Bytes` with `verify_slice`, why the webhook needs no separate middleware stack and the innermost body limit, the verify call as a backup, paid before cooked and cash at the counter, an `OrderEvents` trait, and signed outgoing webhooks from a Postgres queue with times, event IDs, `SKIP LOCKED` leases, saturating backoff, jitter and no redirects, a pretend partner in `examples/`, and tests with a pretend Paystack on a local port, a fake provider and a mutation check.
