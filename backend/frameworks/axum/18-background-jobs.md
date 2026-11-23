---
id: 8c176a9e-ab09-4ea8-93fb-b6b1c126cdfe
---

# Background Jobs and Queues

**A background job is work the server writes down to do later, instead of doing it while the customer waits: sending a receipt, shrinking a photo, checking on a payment. A queue is where those jobs wait, and a worker is a separate program that takes them one by one and does them, trying again when something fails.** In this subject the jobs wait in PostgreSQL, the database we already have, so a job can be added in the same transaction as the change it's about. A payment and its receipt job are saved together, or not at all.

## Before you start
<!-- bite: 989698db-26bf-4c90-8e74-8ba6afb1ebab -->

You should have:

1. Finished [[backend/frameworks/axum/17-payments-and-webhooks|lesson 17]], so payments settle through `settle`, Okada Riders gets webhooks, and `cargo test` runs 54 tests.

After this lesson you will be able to:

1. Decide which work belongs in a request and which belongs in a job.
2. Add jobs in the same transaction as the change they're about, so neither can happen without the other.
3. Run a worker program beside the API, with a worker per queue, each with its own concurrency, retries and backoff.
4. Make every job safe to run twice, and stop retrying jobs that can never work.
5. Run jobs later, and on a timetable, without running them twice when several workers are up.
6. Stop workers politely, watch the queues, and test jobs.

## What to install
<!-- bite: af5ba6c4-6b7f-45dd-979e-5827de8a92a6 -->

```bash
cargo add apalis apalis-postgres
cargo add apalis-cron --no-default-features --features jiff,serde
cargo add jiff-cron
cargo add image --no-default-features --features jpeg,png,webp
```

1. **`apalis`** is a job library for Rust. Its workers are built from **Tower** layers, the same `tower` as Axum's middleware: concurrency limits, retries and timeouts are the layers you already know, put around a job instead of a request.
2. **`apalis-postgres`** keeps the jobs in PostgreSQL, in tables of its own in a schema called `apalis`. It needs the `hstore` extension, which it adds itself.
3. **`apalis-cron`** runs things on a timetable (step 8). The `jiff` feature reads the timetable with jiff, which we already use for time. **`jiff-cron`** is the crate it uses for that; we name its `TimeZone` type ourselves. (It uses an older jiff, 0.2, so the project now has two versions of jiff. That's allowed in Rust, and harmless here: the timetable's time zone is the only place they meet.)
4. **`image`** decodes and encodes pictures, for the photo job (step 4). Only the formats we accept are turned on, so it builds faster.

Decoding photos without optimisation is very slow, and `cargo build` doesn't optimise by default. Add this to the end of `Cargo.toml`, and those crates alone are built optimised, even while you develop:

```toml
# Resizing photos is slow without optimisation, even while developing. Optimise just those crates.
[profile.dev.package.image]
opt-level = 3
[profile.dev.package.zune-jpeg]
opt-level = 3
[profile.dev.package.png]
opt-level = 3
```

The photo test went from 11 seconds to under 2.

There's no new server to start. That's the point of the next two steps.

## Where we stopped
<!-- bite: de4dd57b-0892-4965-8820-c9b17fc23fd5 -->

At the end of lesson 17 we had built, without saying so, a little job queue: the `webhook_deliveries` table, a task that wakes every 5 seconds, a lease so two servers don't send the same webhook, backoff with jitter.

It works. But look at what's coming:

1. **Receipts.** When a payment succeeds, Ada should get an email.
2. **Reminders.** If Ada orders and doesn't pay within 15 minutes, a nudge.
3. **Photos.** Lesson 14 checked uploaded photos by their bytes. Real systems also re-encode every photo and make a small copy for lists. That's a second or two of hard work per photo.
4. **The safety net.** Lesson 17 promised an hourly check on payments still `started`, in case a webhook never arrived.
5. **Cleaning up.** Lesson 15 promised that old idempotency keys would be deleted after a day.

Write a table, a loop and a lease for each, and you have five little queues, each with its own bugs. Time for a real one.

## The kid version
<!-- bite: 054f94aa-9478-4dc4-8211-e686c9a9b293 -->

At Mama Put, the person who takes your order isn't the person who cooks it. The waiter writes your order on a slip and pins it to the board in the kitchen. Then he's free to take the next customer's order.

The cooks take slips off the board, one at a time, and cook. If there's a rush, Mama calls in another cook, and two people take slips off the same board. If a cook burns a pot, he puts the slip back up and tries again.

The board is the queue. Each slip is a job. The cooks are workers. And the waiter, who just pins slips up and moves on, is our API.

**Where the picture stops working.** At Mama Put, the waiter writes the slip and the order in the same book, at the same moment, so they can't disagree. In software they usually live in two different places, and a crash between writing one and the other loses a job, or makes one for nothing. Keeping both in one database is how we get Mama's book back.

## Terms used in this lesson
<!-- bite: 8c079ae6-b8d1-4d7b-93d3-e852cc5cd2ea -->

1. **Job**: This is also called a **task**. It's one piece of work to do later, with a kind and a little data, like `receipts` with `{"paymentId": 17}`.
2. **Queue**: This is where jobs wait. Ours is a table in Postgres, and each kind of job has its own queue.
3. **Producer**: This is the code that adds jobs. Our API is a producer.
4. **Worker**: This is the code that takes jobs from a queue and runs them. Ours is its own program, `src/bin/worker.rs`, separate from the web server.
5. **Concurrency**: This is how many jobs one worker runs at the same time.
6. **Retry** and **backoff**: A retry runs a failed job again; backoff is waiting longer between each try.
7. **Delayed job**: This is a job that mustn't start until a certain time, like "in 15 minutes".
8. **Scheduled job**: This is a job added again and again on a timetable, like "at five past every hour", written as a **cron** pattern.
9. **Killed job**: This is apalis's name for a job that was told it can never work, so it's never tried again. It stays in the table so a person can look.
10. **`LISTEN` and `NOTIFY`**: These are Postgres's way of sending a message to whoever is listening, the moment a transaction commits. Workers listen, so they hear about a new job at once instead of checking the table over and over.

## Step 1: what goes in a job?
<!-- bite: 46897c1c-eda4-45bf-9ffe-bdfbd3687bed -->

Ask one question about every piece of work in a request: **does the customer need the result in this answer?**

| Work | Needs it now? | Where it goes |
|---|---|---|
| Check the order, take the plates, write the row | Yes: the answer says "order placed" | In the request |
| Mark the payment paid (from the webhook) | Yes: it *is* the webhook's job | In the request |
| Send the receipt email | No | A job |
| Nudge Ada if she hasn't paid in 15 minutes | No: it's for later | A delayed job |
| Re-encode a photo and make a thumbnail | No: show the original until it's done | A job |
| Check payments stuck in `started` | Nobody asked; it's on a timer | A scheduled job |

Two more signs something should be a job:

1. **It talks to a service that can be slow or down.** Email providers, partners' servers. You don't want their bad day to become your customer's error.
2. **It's heavy.** Resizing an image keeps a CPU core busy for a second or more. Tokio runs every request on a few shared threads, and lesson 1 warned that blocking one of them stalls every request waiting behind it. `spawn_blocking` moves the work to a thread of its own, but on a two-core server twenty photos at once still slow everything down. Heavy work belongs in a program you can size and count separately.

And one sign it should **not** be a job: if the work failing must make the request fail. "Take the plates" can't be a job, because if it fails, Ada must hear "sorry, finished", not "order placed".

## Step 2: why the jobs live in Postgres
<!-- bite: d308ca7c-a547-45bf-855d-896f7161476d -->

Most job systems keep their queue in Redis, a very fast in-memory database. The net/http and Express versions of this lesson do. So why not here?

Picture the receipt. The payment is marked paid in Postgres, and then the receipt job is added to Redis. Two different databases. If the app crashes between those two lines, or Redis is down for a moment, the payment is paid and the receipt job never exists. Nothing will ever send it. There's no transaction that covers both Postgres and Redis, so those lessons need a **sweeper**: a job every 10 minutes that looks for paid payments with no receipt and queues them again.

With the jobs in Postgres, that gap isn't there. The payment, the order and the receipt job are written in **one transaction**. If anything fails, all three roll back, and Paystack's retry starts again from nothing. If it commits, all three are there. No sweeper needed.

The cost: Postgres can't hand out jobs as fast as Redis. A Redis queue can take tens of thousands of jobs a second; Postgres comfortably handles hundreds. Mama Put sends a few thousand emails a day, so that's plenty, and one less server to run, back up and watch. If you ever need more, apalis has a Redis backend too, and the work functions in this lesson wouldn't change.

The jobs need somewhere to record what they did, so that a job that runs twice can see it already did its work. `migrations/0010_job_bookkeeping.sql`:

```sql
-- What jobs have done, so a job that runs twice can see it already did its work.
ALTER TABLE payments ADD COLUMN receipt_sent_at timestamptz;
ALTER TABLE orders ADD COLUMN reminded_at timestamptz;
ALTER TABLE dishes ADD COLUMN photo_thumb text;
```

```bash
sqlx migrate run
```

apalis's own tables come from apalis, not from our migrations. `jobs::setup` (next step) runs apalis's migrations, which it keeps in its own table, `apalis._sqlx_migrations`, so they never mix with ours.

## Step 3: one door into the queue
<!-- bite: 5dba125c-6382-4853-979e-4930d5f6d377 -->

The rest of the app should never see apalis, the way it never sees SQL outside a store. `src/jobs/mod.rs`:

```rust
//! The one door into the job queue. Only this module and the worker program know apalis.
//!
//! Jobs wait in Postgres, in apalis's own tables, so a job can be added in the same transaction
//! as the change it's about: both happen, or neither does.

use std::time::Duration;

use apalis::{
    layers::retry::backoff::{ExponentialBackoff, ExponentialBackoffMaker, MakeBackoff},
    prelude::{AbortError, BackendExt, BackoffRetryPolicy, PollWith, RetryIfPolicy, RetryPolicy, Strategy, TaskBuilder},
};
use apalis_postgres::{Config, PostgresStorage, Pubsub, queries::push_tasks};
use serde::{Serialize, de::DeserializeOwned};
use sqlx::{Acquire, PgConnection, PgPool};

use crate::db::StoreError;

/// One kind of work to do later. The data is small: ids, never copies of what's in the database.
pub trait Job: Serialize + DeserializeOwned + Clone + Send + Sync + Unpin + 'static {
    /// The queue it waits in. Each queue has its own worker, with its own concurrency.
    const QUEUE: &'static str;
    /// Tries in all, before it's left as failed for a person to look at.
    const MAX_ATTEMPTS: usize;
    /// A name for this piece of work. A second job with the same key is never added.
    fn key(&self) -> String;
}

/// Adds a job, to run as soon as a worker is free.
pub async fn add<J: Job>(conn: &mut PgConnection, job: &J) -> Result<(), StoreError> {
    add_after(conn, job, Duration::ZERO).await
}

/// Adds a job that waits `delay` before it may run.
/// Inside a transaction, it's part of the transaction: if that rolls back, the job was never added.
pub async fn add_after<J: Job>(conn: &mut PgConnection, job: &J, delay: Duration) -> Result<(), StoreError> {
    let args = serde_json::to_vec(job).expect("a job is always JSON");
    let task = TaskBuilder::new(args).idempotency_key(job.key()).max_attempts(J::MAX_ATTEMPTS).run_after(delay).build();

    // A savepoint: if the key is already taken, only this insert is undone, not the caller's transaction.
    let mut savepoint = conn.begin().await?;
    match push_tasks(&mut *savepoint, J::QUEUE, vec![task]).await {
        Ok(()) => Ok(savepoint.commit().await?),
        // Already queued, or already done: adding it again is harmless, which is the point of the key.
        Err(apalis_postgres::Error::Database(e)) => match StoreError::from(e) {
            e if e.is_unique_violation() => Ok(()),
            e => Err(e),
        },
        Err(e) => Err(sqlx::Error::Encode(e.into()).into()),
    }
}
```

Each kind of job is a type that implements `Job`: its data, its queue, how many tries it gets, and its **key**. Four decisions sit in those forty lines.

**Every job has a key we choose.** apalis keeps a unique index on each queue's keys, so a second job with the same key is refused, and `add_after` treats that refusal as success. If the receipt for payment 17 is already queued, or already sent, adding `receipt-17` again does nothing. It's lesson 15's idempotency key again: a name for the work makes "add it again" harmless. And unlike some queues, which forget a key once the job is finished, apalis keeps it for as long as the row is in the table.

**The data is tiny: ids, not copies.** A receipt job carries `{"paymentId": 17}`, not Ada's email and her order. The job might run a minute later, or after retries an hour later, and Ada might have changed her email by then; the job reads the current data when it runs. And job data ends up in dashboards and in logs when a job fails. An id tells nobody anything.

**The connection can be a transaction.** `add` takes a `&mut PgConnection`, and a transaction is one (it derefs to the connection it holds). So a store passes its transaction, and the job becomes part of it.

**The savepoint.** In Postgres, when one statement in a transaction fails, the whole transaction is spoiled: every statement after it is refused until you roll back. So if `push_tasks` hit the unique index inside the payment's transaction, the payment would fail too, just because its receipt was already queued. `conn.begin()` on a connection that's *already* in a transaction doesn't start a new one; sqlx makes a **savepoint** instead, a point inside the transaction to roll back to. If the insert fails, dropping `savepoint` undoes only the insert, and the payment's transaction carries on. Lesson 8's "a transaction rolls back on `Drop`", one level down.

The rest of the file is what the worker needs:

```rust
/// Where a worker reads jobs of kind `J` from. It hears about a new job the moment the transaction that
/// added it commits (Postgres's `LISTEN`/`NOTIFY`), and looks every 5 seconds for jobs that were waiting until later.
pub fn storage<J: Job>(pool: &PgPool) -> PollWith<PostgresStorage<J>, Strategy> {
    let told = Pubsub::new(pool.clone(), J::QUEUE.to_owned());
    PostgresStorage::new(pool)
        .with_config(Config::default().queue(J::QUEUE))
        .poll_with_strategy(Strategy::new().stream(told).interval(Duration::from_secs(5)))
}

/// Creates apalis's tables (in their own `apalis` schema) if they aren't there yet.
pub async fn setup(pool: &PgPool) -> Result<(), apalis_postgres::Error> {
    PostgresStorage::<()>::setup(pool).await
}

/// What a job's work returns when it fails: any error at all. The worker logs it, and tries again.
pub type Failure = Box<dyn std::error::Error + Send + Sync>;

/// A failure that no number of tries will fix: a file that's gone, a photo that won't decode.
/// apalis marks the job `Killed`, and it's never handed out again.
pub fn hopeless(why: impl Into<String>) -> Failure {
    Box::new(AbortError::new(why.into()))
}

/// Was this failure `hopeless`?
pub fn is_hopeless(failure: &Failure) -> bool {
    failure.is::<AbortError>()
}

/// How a worker retries `J`: up to `MAX_ATTEMPTS` tries in all, waiting longer each time
/// (about 1 s, 2 s, 4 s ... up to a minute, with jitter), and never for a `hopeless` failure.
pub fn retries<J: Job>() -> RetryIfPolicy<BackoffRetryPolicy<ExponentialBackoff>, fn(&Failure) -> bool> {
    let backoff = ExponentialBackoffMaker::new(Duration::from_secs(1), Duration::from_secs(60), 0.5, Default::default())
        .expect("valid backoff settings")
        .make_backoff();
    RetryPolicy::retries(J::MAX_ATTEMPTS - 1).with_backoff(backoff).retry_if(worth_retrying)
}

fn worth_retrying(failure: &Failure) -> bool {
    !is_hopeless(failure)
}

/// What a job did. Both are successes: `Skipped` means the work was already done, or no longer needed.
#[derive(Debug, PartialEq, Eq)]
pub enum Ran {
    Done,
    Skipped,
}

/// For adding jobs outside a transaction, from a handler. Cheap to clone.
#[derive(Clone)]
pub struct Queue {
    pool: PgPool,
}

impl Queue {
    pub fn new(pool: PgPool) -> Self {
        Queue { pool }
    }

    pub async fn add<J: Job>(&self, job: &J) -> Result<(), StoreError> {
        add(&mut *self.pool.acquire().await?, job).await
    }
}
```

1. **`storage`** is where a worker reads one kind of job from. `Pubsub` listens with Postgres's `LISTEN`; apalis's tables send a `NOTIFY` when a job is added that's due now, and Postgres delivers it the moment the adding transaction commits. A job added in a transaction that rolls back is never announced, because it never existed. The 5-second `interval` is for jobs that were waiting until later: nothing announces "it's time now", so the worker looks.
2. **`Failure`** is what a job's work returns when it fails: any error at all, boxed. `?` turns a store error, a mail error or an I/O error into one.
3. **`hopeless`** is for failures no retry can fix. Step 7 shows why it has to be an `AbortError`.
4. **`Queue`** is for code that isn't in a transaction, like a handler. `AppState` gains `jobs: jobs::Queue`, built in `main` with `jobs::Queue::new(pool.clone())`.

`main` also runs `jobs::setup(&pool).await?` right after our own migrations.

## Step 4: the work itself, as plain functions
<!-- bite: 9f8fc0cf-4d1c-4b2d-80b1-85cc46cfb161 -->

Each job's work is an ordinary async function that takes what it needs and the job's data. No apalis inside, so it's easy to test.

**Receipts**, `src/payments/receipts.rs`:

```rust
//! The receipt job: an email after a payment succeeds.

use serde::{Deserialize, Serialize};

use super::store::PgPaymentStore;
use crate::{
    jobs::{Failure, Job, Ran},
    mail::Mailer,
    money::Kobo,
};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SendReceipt {
    pub payment_id: i64,
}

impl Job for SendReceipt {
    const QUEUE: &'static str = "receipts";
    const MAX_ATTEMPTS: usize = 5;

    fn key(&self) -> String {
        format!("receipt-{}", self.payment_id)
    }
}

pub struct ReceiptDetails {
    pub order_id: i64,
    pub amount: Kobo,
    pub sent: bool,
    pub email: String,
    pub name: String,
}

/// Emails the receipt for one paid payment. Safe to run twice: a receipt already sent is skipped.
pub async fn send_receipt(store: &PgPaymentStore, mail: &dyn Mailer, payment_id: i64) -> Result<Ran, Failure> {
    let Some(r) = store.receipt_details(payment_id).await? else {
        return Ok(Ran::Skipped); // gone, or never paid: nothing will make it come back
    };
    if r.sent {
        return Ok(Ran::Skipped);
    }
    let subject = format!("Mama Put receipt for order {}", r.order_id);
    let text = format!("Thank you, {}! We received ₦{} for order {}.", r.name, r.amount.naira_text(), r.order_id);
    // Send first, then mark: a crash in between means two receipts, never none.
    mail.send(&r.email, &subject, &text).await?;
    store.mark_receipt_sent(payment_id).await?;
    Ok(Ran::Done)
}
```

(`receipt_details` joins payments, orders and users; `mark_receipt_sent` sets the new column. Both are in `PgPaymentStore`. `naira_text` is a new `Kobo` method that writes `120000` as `1,200.00`.)

Now the question you must ask of **every** job: *what if it runs twice?*

apalis promises each job runs at least once, not exactly once. Picture the worker sending the email and then crashing before it marks the job done. The job comes round again (step 9 shows how), and Ada gets two receipts.

Can we stop that completely? Not here: we can't send an email and write to Postgres as one step. So we choose which way to be wrong:

1. **Mark sent, then send**: a crash in between means Ada gets **no** receipt.
2. **Send, then mark sent**: a crash in between means Ada gets **two**.

For a receipt, two is far better than none, so we send first. The `sent` check at the top still stops every *normal* repeat. For money, lesson 17 made the opposite choice: the guarded `UPDATE` makes "twice" impossible. Every job deserves this question, and the answer depends on what "twice" costs.

**Reminders**, `src/orders/reminders.rs`:

```rust
/// Reminds the customer, if the order is still unpaid and nobody has reminded them yet.
/// The job was added fifteen minutes ago: what was true then may not be now, so look again.
pub async fn remind_unpaid(pool: &PgPool, mail: &dyn Mailer, order_id: i64) -> Result<Ran, Failure> {
    let unpaid = sqlx::query!(
        r#"SELECT o.total_kobo AS "total: Kobo", u.email, u.name
           FROM orders o JOIN users u ON u.id = o.customer_id
           WHERE o.id = $1 AND o.paid_at IS NULL AND o.reminded_at IS NULL"#,
        order_id
    )
    .fetch_optional(pool)
    .await?;
    let Some(unpaid) = unpaid else {
        return Ok(Ran::Skipped); // paid, already reminded, or gone
    };
    let text = format!("{}, your order {order_id} (₦{}) is waiting for payment.", unpaid.name, unpaid.total.naira_text());
    mail.send(&unpaid.email, "Your Mama Put order is waiting", &text).await?;
    sqlx::query!("UPDATE orders SET reminded_at = now() WHERE id = $1", order_id).execute(pool).await?;
    Ok(Ran::Done)
}
```

The job was added fifteen minutes ago, so it looks again before acting. By now Ada may have paid, and the `WHERE` finds nothing. Jobs that run later must check what's true *now*, not trust what was true when they were added. (`RemindUnpaid` is a `Job` like `SendReceipt`: queue `reminders`, three tries, key `remind-unpaid-<order>`.)

**Photos**, `src/menu/process.rs`:

```rust
/// Makes `<name>-large.jpg` (at most 1200 pixels a side) and `<name>-thumb.jpg` (400 × 400),
/// and swaps them in, unless a newer photo arrived first.
pub async fn process_photo(menu: &MenuService, photos: &Photos, job: &ProcessPhoto) -> Result<Ran, Failure> {
    let bytes = match tokio::fs::read(photos.dir().join(&job.file_name)).await {
        Err(e) if e.kind() == ErrorKind::NotFound => return Err(hopeless(format!("{} is gone", job.file_name))),
        read => read?,
    };

    // Decoding and resizing keep a CPU core busy for a second or more: not on the threads that answer requests.
    let made = tokio::task::spawn_blocking(move || -> Result<(Vec<u8>, Vec<u8>), ImageError> {
        let image = image::load_from_memory(&bytes)?;
        let large = if image.width() > 1200 || image.height() > 1200 { image.resize(1200, 1200, FilterType::Lanczos3) } else { image.clone() };
        let thumb = image.resize_to_fill(400, 400, FilterType::Lanczos3);
        Ok((jpeg(&large, 82)?, jpeg(&thumb, 75)?))
    })
    .await?;
    let (large, thumb) = made.map_err(|e| hopeless(format!("can't read {} as an image: {e}", job.file_name)))?;

    let base = job.file_name.rsplit_once('.').map_or(job.file_name.as_str(), |(base, _)| base);
    let (large_name, thumb_name) = (format!("{base}-large.jpg"), format!("{base}-thumb.jpg"));
    tokio::fs::write(photos.dir().join(&large_name), large).await?;
    tokio::fs::write(photos.dir().join(&thumb_name), thumb).await?;

    if menu.set_processed_photo(job.dish_id, &job.file_name, &large_name, &thumb_name).await? {
        Ok(Ran::Done)
    } else {
        Ok(Ran::Skipped) // the cook uploaded a newer photo while we worked
    }
}

/// A brand-new JPEG from the pixels alone: no metadata, so no GPS position from the phone.
fn jpeg(image: &DynamicImage, quality: u8) -> Result<Vec<u8>, ImageError> {
    let mut out = Vec::new();
    JpegEncoder::new_with_quality(&mut out, quality).encode_image(&image.to_rgb8())?;
    Ok(out)
}
```

Four things are going on:

1. **Re-encoding.** `load_from_memory` turns the file into plain pixels, and `JpegEncoder` writes a brand-new file from them. Anything hidden in the original (lesson 14's worry) doesn't survive that, and neither does the metadata, including the GPS position phones put in photos. `to_rgb8` drops any transparency, which JPEG can't hold.
2. **`spawn_blocking`.** Decoding and resizing are pure CPU work with no `.await` in them. On Tokio's own threads they'd stall everything else this program is doing; `spawn_blocking` runs them on a thread kept for blocking work, and `.await` waits for the answer. The first `?` after it is for the thread itself (it can panic), the `map_err` for the image.
3. **`hopeless` for failures no retry can fix.** A file that won't decode will never decode, and a file that's gone won't come back.
4. **`set_processed_photo` checks the original's name.** Its SQL is `UPDATE dishes SET photo = $3, photo_thumb = $4 WHERE id = $1 AND photo = $2`. If the cook uploaded a *newer* photo while this job was running, the old job's result doesn't overwrite it. Jobs run late, and late work must not undo newer work.

`resize` keeps the shape, so a 2400 × 1600 photo becomes 1200 × 800. `resize_to_fill` crops the middle to make a square. `DishV2` gains `thumbnailUrl`, `null` until the job has made one.

## Step 5: adding the jobs
<!-- bite: 3348699d-a88b-40af-92ad-ebceb7fb6e81 -->

**Receipts**, in the payment's own transaction. `mark_succeeded` from lesson 17 now ends like this:

```rust
    /// Marks the payment succeeded and its order paid, together, and queues the receipt in the same
    /// transaction. Only the first caller changes anything.
    pub async fn mark_succeeded(&self, reference: &str) -> Result<Outcome, StoreError> {
        let mut tx = self.pool.begin().await?;
        let settled = sqlx::query!(
            "UPDATE payments SET status = 'succeeded', settled_at = now()
             WHERE reference = $1 AND status = 'started'
             RETURNING id, order_id",
            reference
        )
        .fetch_optional(&mut *tx)
        .await?;
        let Some(settled) = settled else {
            return Ok(Outcome::AlreadySettled); // someone settled it first; dropping `tx` ends it
        };
        let paid = sqlx::query!("UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL", settled.order_id)
            .execute(&mut *tx)
            .await?
            .rows_affected();
        if paid == 0 {
            tx.commit().await?;
            return Ok(Outcome::OrderWasAlreadyPaid);
        }
        // Paid, and the receipt is on its way: both, or (if anything here fails) neither.
        jobs::add(&mut tx, &SendReceipt { payment_id: settled.id }).await?;
        tx.commit().await?;
        Ok(Outcome::Paid)
    }
```

Two small changes from lesson 17. `RETURNING id, order_id` gives the payment's id for the job. And the receipt is added only on `Paid`: the one call that actually changed the payment. Repeats of the webhook get `AlreadySettled` and queue nothing; a second payment for an order already paid gets no receipt, but a refund.

**Reminders**, in the order's transaction, in `place_taking_portions`, just before the commit:

```rust
        // A nudge in fifteen minutes, if it's still unpaid then. v1's orders have nobody to nudge.
        if order.customer_id.is_some() {
            jobs::add_after(&mut tx, &RemindUnpaid { order_id: order.id }, REMIND_AFTER).await?;
        }
```

A retried order (lesson 15) returns the first order before reaching this line, so it doesn't add a second reminder; and if it did, the key would refuse it.

**Photos**, from the upload handler, which has no transaction to join:

```rust
    let dish = menu.set_photo(id, &name).await?;
    // The thumbnail is made in the background. If queueing fails, the original still shows: log it, don't refuse.
    if let Err(e) = jobs.add(&ProcessPhoto { dish_id: id, file_name: name }).await {
        tracing::error!(cause = %e, "couldn't queue the photo job");
    }
    Ok(Data(dish.into()))
```

(The handler gains `State(jobs): State<Queue>`, and the router a `Queue: FromRef<S>` bound.) A failure to queue is **logged, not returned**. The photo is saved and it shows; only the thumbnail is missing. Refusing the upload over that would be worse for the cook than a missing thumbnail.

## Step 6: the worker program
<!-- bite: 4944d1ae-8b45-40b1-acd4-10d6caf74b02 -->

The worker is a **second program** in the same crate. Cargo builds every file in `src/bin/` as a program of its own, with the library as its dependency, exactly like `main.rs`. `src/bin/worker.rs`:

```rust
//! The worker: a second program, beside the API, that runs jobs. It answers no HTTP at all.
//!
//! cargo run --bin worker

use std::{str::FromStr, sync::Arc, time::Duration};

use apalis::prelude::*;
use apalis_cron::{CronScheduler, Tick, jiff::JiffSchedule};
use jiff_cron::jiff::tz::TimeZone;
use mama_put::{
    auth::PgAuthStore,
    clock::Clock,
    db,
    jobs::{self, Failure, retries},
    mail::{LogMailer, Mailer},
    maintenance::{self, CheckUnsettled, CleanUp},
    menu::{MenuService, Photos, PgMenuStore, ProcessPhoto, process_photo},
    orders::{OrderService, PgOrderStore, RemindUnpaid, remind_unpaid},
    payments::{PaymentService, Paystack, PgPaymentStore, SendReceipt, send_receipt},
    webhooks::{Deliveries, OkadaRiders, Sender},
};
use sqlx::PgPool;
use tracing::info;

/// Everything the jobs need. Each worker gets a clone.
#[derive(Clone)]
struct Deps {
    pool: PgPool,
    payment_store: PgPaymentStore,
    payments: PaymentService,
    menu: MenuService,
    photos: Photos,
    mail: Arc<dyn Mailer>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    tracing_subscriber::fmt().with_env_filter("mama_put=info,worker=info,apalis=warn").init();

    let pool = db::connect(&env("DATABASE_URL")?).await?;
    jobs::setup(&pool).await?;

    // The same pieces the API builds, for the jobs that need them.
    let menu = MenuService::new(Arc::new(PgMenuStore::new(pool.clone())));
    let deliveries = Deliveries::new(pool.clone());
    let okada = OkadaRiders { deliveries: deliveries.clone(), url: env("OKADA_WEBHOOK_URL")?, clock: Clock::system() };
    let orders = OrderService::new(Arc::new(PgOrderStore::new(pool.clone())), menu.clone(), Arc::new(okada), Clock::system())?;
    let client = reqwest::Client::builder().timeout(Duration::from_secs(8)).build()?;
    let paystack_url = std::env::var("PAYSTACK_BASE_URL").unwrap_or_else(|_| "https://api.paystack.co".into());
    let paystack = Paystack::new(paystack_url.parse()?, &env("PAYSTACK_SECRET_KEY")?, client);
    let payment_store = PgPaymentStore::new(pool.clone());
    let payments = PaymentService::new(payment_store.clone(), orders, PgAuthStore::new(pool.clone()), Arc::new(paystack), &env("PUBLIC_URL")?);
    let photos = Photos::new(std::env::var("UPLOAD_DIR").unwrap_or_else(|_| "uploads".into()));
    let deps = Deps { pool: pool.clone(), payment_store, payments, menu, photos, mail: Arc::new(LogMailer) };

    // Lesson 17's webhooks to Okada Riders now go out from here, not from the API.
    let sender = Sender::new(deliveries, &env("OKADA_WEBHOOK_SECRET")?, Clock::system())?;
    tokio::spawn(sender.run(Duration::from_secs(5)));

    // Two copies of this program must not share worker names.
    let me = format!("{:08x}", getrandom::u32()?);
    let lagos = TimeZone::get("Africa/Lagos")?;

    info!("Mama Put worker started");
    // One worker per queue. `register` takes a closure it may call again to restart a worker, so each
    // closure owns its own clones: the `{ let deps = ...; move |_| ... }` blocks.
    Monitor::new()
        .register({
            let (deps, me) = (deps.clone(), me.clone());
            move |_| {
                WorkerBuilder::new(format!("receipts-{me}"))
                    .backend(jobs::storage::<SendReceipt>(&deps.pool))
                    .concurrency(4) // emails mostly wait on the network: four at once costs little
                    .retry(retries::<SendReceipt>())
                    .data(deps.clone())
                    .build(receipt)
            }
        })
        .register({
            let (deps, me) = (deps.clone(), me.clone());
            move |_| {
                WorkerBuilder::new(format!("reminders-{me}"))
                    .backend(jobs::storage::<RemindUnpaid>(&deps.pool))
                    .concurrency(4)
                    .retry(retries::<RemindUnpaid>())
                    .data(deps.clone())
                    .build(reminder)
            }
        })
        .register({
            let (deps, me) = (deps.clone(), me.clone());
            move |_| {
                WorkerBuilder::new(format!("photos-{me}"))
                    .backend(jobs::storage::<ProcessPhoto>(&deps.pool))
                    .concurrency(1) // CPU work: two at once just take twice as long each
                    .retry(retries::<ProcessPhoto>())
                    .data(deps.clone())
                    .build(photo)
            }
        })
        .register({
            let (deps, me) = (deps.clone(), me.clone());
            move |_| {
                WorkerBuilder::new(format!("check-unsettled-{me}"))
                    .backend(jobs::storage::<CheckUnsettled>(&deps.pool))
                    .retry(retries::<CheckUnsettled>())
                    .data(deps.clone())
                    .build(check_unsettled)
            }
        })
        .register({
            let (deps, me) = (deps.clone(), me.clone());
            move |_| {
                WorkerBuilder::new(format!("clean-up-{me}"))
                    .backend(jobs::storage::<CleanUp>(&deps.pool))
                    .retry(retries::<CleanUp>())
                    .data(deps.clone())
                    .build(clean_up)
            }
        })
        // The timetable. Each tick only *adds* a job, keyed by the time it was meant for,
        // so however many workers run this, the job itself is added once.
        .register({
            let (pool, me, lagos) = (deps.pool.clone(), me.clone(), lagos.clone());
            move |_| {
                let every_hour = JiffSchedule::from_str("0 5 * * * *").expect("a valid cron pattern"); // 5 past every hour
                WorkerBuilder::new(format!("timetable-hourly-{me}"))
                    .backend(CronScheduler::new(every_hour).with_timezone(lagos.clone()))
                    .data(pool.clone())
                    .build(add_check_unsettled)
            }
        })
        .register({
            let (pool, me) = (deps.pool.clone(), me.clone());
            move |_| {
                let every_morning = JiffSchedule::from_str("0 30 3 * * *").expect("a valid cron pattern"); // 3:30 every morning
                WorkerBuilder::new(format!("timetable-nightly-{me}"))
                    .backend(CronScheduler::new(every_morning).with_timezone(lagos.clone()))
                    .data(pool.clone())
                    .build(add_clean_up)
            }
        })
        // When told to stop, wait up to 25 seconds for running jobs to finish.
        .shutdown_timeout(Duration::from_secs(25))
        .run_with_signal(tokio::signal::ctrl_c())
        .await?;
    info!("worker stopped");
    Ok(())
}
```

and each job's handler is three lines, calling the plain function:

```rust
async fn receipt(job: SendReceipt, deps: Data<Deps>) -> Result<(), Failure> {
    let ran = send_receipt(&deps.payment_store, &*deps.mail, job.payment_id).await?;
    info!(payment_id = job.payment_id, ?ran, "receipt");
    Ok(())
}
```

```bash
cargo run --bin worker
```

in a second terminal, next to `cargo run --bin mama-put` (the API's name is the package's name). Read it, because each line is a decision.

1. **Why a separate program?** Because the two pull in different directions. The API must answer every request quickly; a worker resizing photos uses whole CPU cores. Separate, you can run three APIs and one worker, or one API and five workers at lunchtime, and a crashing photo job can never take the website down with it.
2. **One worker per queue.** Each `register` builds a `WorkerBuilder` for one kind of job, so each queue has its own concurrency: four receipts at once, because emails mostly wait on the network, but **one photo at a time**, because photos are CPU work and two at once just take twice as long each. A thousand photos waiting can't hold up Ada's receipt: they're in another queue, with another worker.
3. **`concurrency` and `retry` are Tower layers.** `concurrency(4)` is `tower::limit::ConcurrencyLimitLayer`, the same kind of layer as lesson 7's timeout. And the order matters, as it did in lesson 3. Put `retry` before `concurrency`, and apalis warns that "each retry may consume a separate concurrency slot": the retry layer would sit outside the limit, so every retry would queue for a new slot instead of keeping its own. Limit first, then retry inside it.
4. **`data(deps.clone())`** gives the handler its dependencies, like `State` in a handler. `Data<Deps>` dereferences to `Deps`, so `deps.payment_store` just works.
5. **`register` takes a closure it may call again**, to restart a worker that stopped. So each closure must own clones of what it uses, and `{ let deps = deps.clone(); move |_| ... }` is the usual Rust way to write that: clone first, then `move` the clones into the closure.
6. **Worker names are unique per program.** apalis records every worker in `apalis.workers`, and a job is locked by a worker's name. Two copies of the program with the same names would look like one worker to apalis, so each copy adds a random suffix.
7. **The Okada Riders sender moved here.** Lesson 17's `tokio::spawn(sender.run(...))` is gone from the API's `main`. The API answers requests; the worker does the sending.

Why didn't the webhooks become apalis jobs too? Because of how their retries work. A webhook to a partner may wait **six hours** between tries. apalis's retries, as the next step shows, wait in the worker's memory, holding a place in its concurrency while they wait. That's fine for "try again in a few seconds", and wrong for "try again this afternoon". Lesson 17's table, with `next_attempt_at` and its lease, already does long waits properly. A good tool isn't the right tool for every job.

## Step 7: retries, honestly
<!-- bite: b1664d06-9038-49ae-89b1-8ccabe7ba016 -->

`jobs::retries`, from step 3:

```rust
/// How a worker retries `J`: up to `MAX_ATTEMPTS` tries in all, waiting longer each time
/// (about 1 s, 2 s, 4 s ... up to a minute, with jitter), and never for a `hopeless` failure.
pub fn retries<J: Job>() -> RetryIfPolicy<BackoffRetryPolicy<ExponentialBackoff>, fn(&Failure) -> bool> {
    let backoff = ExponentialBackoffMaker::new(Duration::from_secs(1), Duration::from_secs(60), 0.5, Default::default())
        .expect("valid backoff settings")
        .make_backoff();
    RetryPolicy::retries(J::MAX_ATTEMPTS - 1).with_backoff(backoff).retry_if(worth_retrying)
}

fn worth_retrying(failure: &Failure) -> bool {
    !is_hopeless(failure)
}
```

Tower's `ExponentialBackoff` waits between 1 second and a minute, doubling, with jitter (`0.5`), and `retry_if` stops for failures not worth retrying. I didn't trust that from reading it, so I ran it: a real worker, on a real job, three ways.

| The job | Tries | Waits between | Ended as |
|---|---|---|---|
| Fails twice, then works | 3 | about 1 s, then 2 s | `Done` |
| Always fails | 4 | about 1 s, 2 s, 5 s | `Failed`, attempts 4 |
| Hopeless, written as our own error type | 4 | **none** | `Failed` |
| Hopeless, written as `AbortError` | 1 | | `Killed` |

The third row was a surprise, and it's why `hopeless` returns an `AbortError`. `retry_if` did stop the retries inside the worker. But the job was then saved as `Failed` with 1 attempt out of 4, and apalis hands out `Failed` jobs that still have attempts left. So it came straight back, three more times, with no wait at all. Only a job whose error is an `AbortError` is marked `Killed`, and `Killed` jobs are never handed out again. Read the library's own code when something matters; then test it.

Two things follow:

1. **Retries are for the short term.** They happen in the worker, within a minute or so. A job that's still failing after `MAX_ATTEMPTS` is left as `Failed`, for a person (or lesson 37's alerts) to see.
2. **`MAX_ATTEMPTS` is in two places on purpose.** The job's `max_attempts` in the table, and `retries(MAX_ATTEMPTS - 1)` in the worker, both come from one constant, so the table never thinks a job has tries left that the worker has already used.

## Step 8: later, and on a timetable
<!-- bite: e4efc6d6-a6ec-4413-8913-0055a57dba9b -->

**Delayed jobs.** The reminder is `add_after(..., REMIND_AFTER)`, which sets the job's `run_at` 15 minutes ahead. It waits in the table, and a restart of the API or the worker doesn't lose it, because it isn't in either program at all. Postgres only announces jobs that are due *now*, so the worker's 5-second look in `storage` is what finds it when its time comes.

**Scheduled jobs.** Lesson 17's safety net, once an hour: ask Paystack about every payment still `started` after 15 minutes. And lesson 15's cleanup, once a night. In the worker above, two `CronScheduler`s tick on a timetable in Lagos time.

The patterns have **six** fields in jiff-cron, the first being seconds: seconds, minutes, hours, day of the month, month, day of the week. `0 5 * * * *` means "second 0 of minute 5, every hour". `0 30 3 * * *` is "3:30 every morning". I checked what they mean by asking for their next times:

```text
0 5 * * * *: ["2026-11-22T22:05:00+01:00[Africa/Lagos]", "2026-11-22T23:05:00+01:00[Africa/Lagos]"]
0 30 3 * * *: ["2026-11-23T03:30:00+01:00[Africa/Lagos]", "2026-11-24T03:30:00+01:00[Africa/Lagos]"]
```

**Many workers, one timetable.** Run three copies of the worker, and three timetables tick at 5 past the hour. With most job systems you then make sure only one process runs the timetable. Here, a tick doesn't do the work. It only *adds* a job, and the job's key holds the moment it was meant for. `src/maintenance.rs`:

```rust
/// Ask Paystack about payments left `started`. Every hour, at 5 past.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CheckUnsettled {
    /// The moment the timetable meant, in seconds since 1970.
    pub due: u64,
}

impl Job for CheckUnsettled {
    const QUEUE: &'static str = "check-unsettled";
    const MAX_ATTEMPTS: usize = 2;

    fn key(&self) -> String {
        format!("check-unsettled-{}", self.due)
    }
}
```

All three timetables add `check-unsettled-1795381500` (22:05 in Lagos, as seconds since 1970). The first one in wins; the other two hit the unique key, and `add` shrugs. So the check runs once, whichever worker's clock ticked first, and no process is special. (If every worker is down at 5 past, that hour's check is simply missed. The next one, at 6:05, checks the same payments.)

And every scheduled job is safe to run twice anyway, which is the real guarantee. The check ends in `settle`:

```rust
    /// Asks Paystack about payments that have been `started` for a while: the safety net under the webhook.
    /// Each one goes through `settle`, so one already settled another way is simply skipped.
    pub async fn check_unsettled(&self) -> Result<usize, PaymentError> {
        let stuck = self.store.started_between(Duration::from_secs(15 * 60), Duration::from_secs(24 * 60 * 60)).await?;
        for reference in &stuck {
            let seen = self.provider.verify(reference).await?;
            self.settle(reference, seen).await?;
        }
        Ok(stuck.len())
    }
```

That's three doors into one room: the webhook, the verify route and this check all settle through `settle`, and the room is safe to enter twice. The cleanup deletes in bites:

```rust
/// Deletes idempotency keys older than a day, webhook events received over 30 days ago, and webhooks
/// delivered over 90 days ago. In bites of 5,000, so one big delete never holds a busy table for long.
pub async fn clean_up(pool: &PgPool) -> Result<u64, StoreError> {
    let mut deleted = 0;
    loop {
        let bite = sqlx::query!(
            "DELETE FROM idempotency_keys WHERE ctid IN (
               SELECT ctid FROM idempotency_keys WHERE created_at < now() - interval '1 day' LIMIT 5000)"
        )
        .execute(pool)
        .await?
        .rows_affected()
            + sqlx::query!(
                "DELETE FROM webhook_events_received WHERE ctid IN (
                   SELECT ctid FROM webhook_events_received WHERE handled_at < now() - interval '30 days' LIMIT 5000)"
            )
            .execute(pool)
            .await?
            .rows_affected()
            + sqlx::query!(
                "DELETE FROM webhook_deliveries WHERE ctid IN (
                   SELECT ctid FROM webhook_deliveries WHERE delivered_at < now() - interval '90 days' LIMIT 5000)"
            )
            .execute(pool)
            .await?
            .rows_affected();
        deleted += bite;
        if bite == 0 {
            return Ok(deleted);
        }
    }
}
```

`ctid` is the row's physical address in Postgres. `DELETE ... WHERE ctid IN (SELECT ctid ... LIMIT 5000)` deletes 5,000 rows at a time, in a loop until nothing's left, so one huge delete never holds a busy table for minutes. Deleting old rows twice deletes nothing the second time.

## Step 9: stopping workers politely
<!-- bite: dfca0019-ed57-4a0e-822f-3111d5893162 -->

When you deploy a new version, the old worker is asked to stop (`SIGTERM`, or `SIGINT` when you press Ctrl+C). If it just died, a photo halfway through would be lost work, and a receipt halfway through might be sent twice.

`run_with_signal(tokio::signal::ctrl_c())` handles this. When the signal comes, the monitor:

1. Stops every worker taking new jobs.
2. Waits for running jobs to finish, for up to `shutdown_timeout`, 25 seconds here.
3. Returns, so `main` prints "worker stopped" and ends.

```text
2026-11-22T20:28:24.288297Z  INFO worker: Mama Put worker started
2026-11-22T20:28:27.172987Z  INFO worker: worker stopped
```

And if a worker *doesn't* stop politely (the machine loses power, or it's killed after the 25 seconds)? Every worker writes a heartbeat to `apalis.workers` every 30 seconds. A job locked by a worker that has missed its heartbeats is put back to `Pending`, and another worker takes it. That's the lease from lesson 17, done for you, and it's also why every job must be safe to run twice.

This is why jobs should be short. A job that takes 20 minutes can't finish politely in the 25 seconds a deploy gives it. Split long work into many small jobs. Lesson 38 does the same for the web server.

## Step 10: watching the queues
<!-- bite: dab8f0a2-a386-4d19-8627-75f35a57b4c5 -->

You'll want to know: how many jobs are waiting? Which failed, and why? A queue that's quietly growing is a problem you want to see on Tuesday, not discover on Friday.

The queue is a table, so it's one query away:

```bash
psql "$DATABASE_URL" -c "SELECT job_type, status, count(*) FROM apalis.jobs GROUP BY job_type, status ORDER BY job_type"
```

```text
 job_type | status | count
----------+--------+-------
 photos   | Done   |     1
 receipts | Done   |     2
```

`SELECT id, last_error FROM apalis.jobs WHERE status IN ('Failed', 'Killed')` lists what went wrong. Done jobs stay in the table, so the cleanup job is the place to delete old ones too (a practice below).

There's also **apalis-board**, a ready-made web page listing every queue and job, with their errors and a "retry" button. It shows job data and errors, so it must only ever be reachable by admins, never on the open internet. (One more reason job data holds ids, not personal details.) Lesson 37 turns the counts into graphs and alerts.

## Step 11: testing jobs
<!-- bite: a2411bad-0adb-421b-9df8-cba5636265a1 -->

**`TestApp` sets up apalis's tables.** `#[sqlx::test]` runs our migrations for each test's fresh database, but not apalis's. So `TestApp::new` and `TestApp::with` now begin with `jobs::setup(&pool).await`, which makes them `async`: every test says `TestApp::new(pool).await`. The order service's own tests in `src/orders/service.rs` call `jobs::setup` too, because a customer's order now adds a reminder.

**apalis's tables aren't checked when you compile.** sqlx's `query!` checks a query against your development database, which has only *our* tables until the API has run once. So tests that look at `apalis.jobs` use `sqlx::query_scalar(...)` without the `!`, which is checked when it runs instead.

`tests/jobs.rs` has six tests. The receipt one shows the transaction and the key working together:

```rust
#[sqlx::test]
async fn a_payment_queues_one_receipt_and_it_is_sent_once(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let ada = app.user("ada@example.com", "customer").await;
    let order = app.order(&ada, app.dish("Jollof rice", 1500, 40).await).await;
    let started = app.post(&format!("/v2/orders/{order}/payments")).bearer(&ada).send().await;
    let reference = started.body["data"]["reference"].as_str().unwrap().to_owned();

    // The webhook, its retry and the app's check, all at once: one settles, so one receipt is queued.
    let seen = Seen { succeeded: true, amount: Kobo(150000), currency: "NGN".into() };
    join_all((0..3).map(|_| app.payments.settle(&reference, seen.clone()))).await;
    assert_eq!(waiting(&app.pool, "receipts").await, 1);

    // And the job itself, run twice, sends one email.
    let payment_id: i64 = sqlx::query_scalar!("SELECT id FROM payments").fetch_one(&app.pool).await.unwrap();
    let (store, outbox) = (PgPaymentStore::new(app.pool.clone()), Outbox::default());
    assert_eq!(send_receipt(&store, &outbox, payment_id).await.unwrap(), Ran::Done);
    assert_eq!(send_receipt(&store, &outbox, payment_id).await.unwrap(), Ran::Skipped);
    assert_eq!(*outbox.0.lock().unwrap(), [("ada@example.com".to_owned(), format!("Mama Put receipt for order {order}"))]);
}
```

`Outbox` is a fake `Mailer` that keeps emails in a `Vec` instead of sending them. The others:

1. `an_unpaid_order_gets_one_reminder_later`: Ada's order adds one reminder, due in about 15 minutes; a v1 order adds none; the reminder runs once.
2. `a_duplicate_job_leaves_the_transaction_alone`: a second job with the same key, in the same transaction, doesn't spoil it; and a job added in a transaction that rolls back was never added.
3. `a_photo_gets_a_thumbnail_unless_a_newer_one_came_first`: a real 2000 × 1000 PNG becomes 1200 × 600 and 400 × 400 JPEGs, the menu shows the thumbnail, a late job for an older photo is `Skipped`, and a missing file is hopeless.
4. `a_failing_job_is_tried_again` and `a_hopeless_job_is_tried_once`: step 7's table, kept as tests, running a real worker.

The worker tests need to stop the worker when the job is finished. A worker runs until it's told to stop, so the test races it against a loop that watches the job's status:

```rust
/// Runs a real worker on one `Flaky` job until it's finished. Returns how often it ran, and how it ended.
async fn run_worker(pool: &PgPool, job: Flaky) -> (usize, String) {
    jobs::setup(pool).await.unwrap();
    jobs::add(&mut pool.acquire().await.unwrap(), &job).await.unwrap();
    let tries = Arc::new(AtomicUsize::new(0));
    let worker = WorkerBuilder::new(job.key())
        .backend(jobs::storage::<Flaky>(pool))
        .retry(jobs::retries::<Flaky>())
        .data(tries.clone())
        .build(flaky);
    let finished = async {
        loop {
            tokio::time::sleep(Duration::from_millis(100)).await;
            let status: String = sqlx::query_scalar("SELECT status FROM apalis.jobs").fetch_one(pool).await.unwrap();
            if status == "Done" || status == "Killed" {
                return status;
            }
        }
    };
    tokio::select! {
        _ = worker.run() => unreachable!("a worker runs until it's stopped"),
        status = finished => (tries.load(Ordering::SeqCst), status),
    }
}
```

`tokio::select!` runs both futures at once on this one task, and takes whichever finishes first. When `finished` returns, the worker's future is dropped, which stops it. (I first tried `tokio::spawn` for the worker, and it didn't compile: "implementation of `FnOnce` is not general enough", one of the rough edges of lifetimes in async Rust. `select!` needs no spawning, so the problem never comes up.)

```bash
cargo test
```

60 tests, all passing.

## The Rust in this lesson
<!-- bite: 5485cca6-3586-4d10-9cf9-0c7476d4ca1e -->

1. **`src/bin/`**: Each file there is a separate program, built with the library as a dependency. `cargo run --bin worker` runs one by name.
2. **A trait with associated constants**, `const QUEUE: &'static str;`: Each type that implements `Job` says its own queue and tries, and generic code reads them as `J::QUEUE`.
3. **Generic functions over a trait**, `fn add<J: Job>(...)`: One function for every kind of job. `jobs::storage::<SendReceipt>(&pool)` picks the kind with a turbofish.
4. **`conn.begin()` inside a transaction**: sqlx makes a savepoint, and dropping it without `commit` rolls back to it, not the whole transaction.
5. **`&mut tx` where a `&mut PgConnection` is wanted**: A transaction derefs to its connection, so it can be passed anywhere a connection can.
6. **`Box<dyn Error + Send + Sync>`** and **`.is::<T>()`**: Any error at all, boxed, so `?` works with every error type. `is` asks what type is really inside the box.
7. **`tokio::task::spawn_blocking(move || ...)`**: Runs CPU-heavy or blocking code on a thread kept for it, and gives back a future for the result.
8. **`match` with a binding and a guard**, `Err(e) if e.kind() == ErrorKind::NotFound => ...`, and **`read => read?`**: A name in a pattern catches whatever is left.
9. **`rsplit_once('.')`** and **`map_or`**: Splits at the *last* dot. `map_or(default, f)` gives `default` for `None`, or `f` of the value.
10. **`{ let (deps, me) = (deps.clone(), me.clone()); move |_| ... }`**: A block whose last expression is a closure. Clone first, then `move` the clones in, so the closure owns everything it uses and can be called again.
11. **`tokio::select!`**: Runs several futures at once and takes the first to finish; the others are dropped.
12. **`Arc<AtomicUsize>`** and **`fetch_add`**: A counter many tasks can add to safely, without a lock.
13. **`[profile.dev.package.image] opt-level = 3`**: Optimises one dependency in development builds, leaving your own code quick to compile.
14. **`sqlx::query_scalar(...)` without the `!`**: The same query, checked when it runs instead of when it compiles, for tables your development database doesn't know.

## Your project so far
<!-- bite: 7be37ce5-49ff-4009-8b50-c7c5dce08e1a -->

```text
mama-put/
├── Cargo.toml                    ← apalis, apalis-postgres, apalis-cron (jiff), jiff-cron, image; image crates optimised in dev
├── migrations/
│   └── 0010_job_bookkeeping.sql  ← NEW: payments.receipt_sent_at, orders.reminded_at, dishes.photo_thumb
├── src/
│   ├── main.rs                   ← jobs::setup; jobs::Queue in the state; no more webhook sender here
│   ├── bin/
│   │   └── worker.rs             ← NEW: the worker program: a worker per queue, the timetable, the webhook sender
│   ├── lib.rs                    ← AppState.jobs
│   ├── jobs/mod.rs               ← NEW: Job, add/add_after (savepoint, keys), storage (LISTEN + 5 s), retries, hopeless, Queue
│   ├── mail.rs                   ← NEW: Mailer, LogMailer
│   ├── maintenance.rs            ← NEW: CheckUnsettled, CleanUp (keyed by their tick), clean_up in bites
│   ├── money.rs                  ← Kobo::naira_text
│   ├── menu/
│   │   ├── process.rs            ← NEW: ProcessPhoto: re-encode on spawn_blocking, thumbnail, newer photo wins
│   │   ├── photos.rs             ← upload queues the photo job (logged, not refused, if it can't)
│   │   └── store.rs, model.rs, versions.rs ← photo_thumb, set_processed_photo, thumbnailUrl
│   ├── orders/
│   │   ├── reminders.rs          ← NEW: RemindUnpaid, 15 minutes later, looks again before sending
│   │   └── store.rs              ← the reminder added in the order's transaction
│   └── payments/
│       ├── receipts.rs           ← NEW: SendReceipt: send, then mark sent
│       ├── store.rs              ← the receipt added in the settling transaction; receipt details; started_between
│       └── service.rs            ← check_unsettled
└── tests/
    ├── common/mod.rs             ← TestApp::new and ::with are async, and set up apalis's tables
    └── jobs.rs                   ← NEW: 6 tests, two with a real worker
```

## Common mistakes
<!-- bite: 41f41c14-a830-4d97-a637-21ff81c491c9 -->

1. **Doing slow work in the request.** The customer waits for your email provider. Add a job.
2. **Adding the job outside the transaction it belongs to.** A crash in between loses it, or adds one for nothing. Pass the transaction to `jobs::add`.
3. **Adding a job inside a transaction without a savepoint.** One duplicate key spoils the whole transaction.
4. **Putting whole objects in job data.** Stale by the time it runs, and personal data in dashboards and logs. Put ids in, and read the rest when it runs.
5. **Jobs that aren't safe to run twice.** They will run twice. Decide which way to be wrong, and check what's already done first.
6. **Trusting what was true when the job was added.** Fifteen minutes later, Ada may have paid. Look again.
7. **Retrying what can never work.** It wastes tries and hides real failures. Make it `hopeless`, and check it really stops.
8. **Heavy CPU work on Tokio's own threads.** It stalls everything else. Use `spawn_blocking`, and keep heavy queues at a low concurrency.
9. **`retry` before `concurrency`.** Each retry takes another slot. Limit first, then retry.
10. **Two worker programs with the same worker names.** apalis can't tell them apart. Make each name unique.
11. **Very long jobs.** They can't stop politely in a deploy. Split them.

## Check your understanding
<!-- bite: 87f123f7-634a-40e4-b1ef-39ab076e8600 -->

1. Which of these belong in a job, and why: taking the plates, sending a receipt, making a thumbnail?
2. Why does putting the jobs in Postgres remove the need for net/http's sweeper?
3. `add_after` uses a savepoint. What would go wrong without it, in the payment's transaction?
4. The receipt job sends first and marks sent second. What does a crash between the two cost, and why is that the better way round?
5. Why does the photo worker run one job at a time, when the receipt worker runs four?
6. A hopeless job written as our own error type was still tried four times. Why, and what fixed it?
7. Three workers run the timetable. Why does the hourly payment check run once, not three times?
8. Why do the webhooks to Okada Riders stay in lesson 17's table instead of becoming apalis jobs?

<details>
<summary>Answers, after your attempt</summary>

1. Taking the plates stays in the request: if it fails, the answer must say so. The receipt is a job: Ada doesn't need it in the answer, and the email service can be slow or down. The thumbnail is a job: it's heavy CPU work, and the original photo shows until it's ready.
2. Because the job is written in the same transaction as the payment. If anything fails, both roll back; if it commits, both are there. With the queue in Redis, a crash between the two writes loses the job, so something must look for lost jobs later.
3. Postgres spoils a whole transaction when one statement fails. If the receipt's key was already taken, the failed insert would make the payment's transaction fail too. The savepoint undoes only the insert.
4. Two receipts instead of one. The other way round, a crash would mean no receipt at all, which is worse: Ada would have paid with nothing to show for it.
5. Photos are CPU work: on a small server, two at once each take twice as long, and they slow everything else. Receipts mostly wait on the network, so four at once cost almost nothing.
6. The retry layer stopped, but the job was saved as `Failed` with attempts left, and apalis hands those out again at once. Returning an `AbortError` marks it `Killed`, which is never handed out again.
7. Each timetable only adds a job, keyed by the moment it was meant for. The first one in wins, and the other two hit the unique key and are ignored. And the check ends in `settle`, which is safe twice anyway.
8. Their retries can wait hours, and apalis's retries wait in the worker's memory, holding a concurrency slot. The table's `next_attempt_at` and lease handle long waits properly.

</details>

## Practice
<!-- bite: b69f014c-4c16-48a4-a408-0ab803cdea54 -->

1. Add `AskForReview`: an email an hour after an order is `collected`, asking how the food was. Add it in the same transaction as the status change. (Hint: `OrderEvents` gains a `collected` method, or `set_status` gets the job's door.)
2. Make `clean_up` also delete `Done` jobs from `apalis.jobs` that finished more than a week ago, in bites.
3. Add `GET /v2/admin/queues` for admins, returning each queue's counts by status, with a new permission in the policy and a row in the permissions test.
4. Write a test that a photo that isn't really an image (HTML named `.png`) is hopeless.
5. Run two worker programs at once, add 20 receipts, and check from the log that each was sent once.

**Done when** paying for an order logs its receipt email from the worker within a second; an unpaid order has a reminder due in 15 minutes; an uploaded photo gains a `thumbnailUrl`; Ctrl+C stops the worker with "worker stopped"; and `cargo test` runs 60 tests and passes.

## Before moving on
<!-- bite: c7fda08a-8a0c-47b6-a7c9-0b0948c3d598 -->

Mama Put now does its slow work in the background. Receipts, reminders and thumbnails happen without anyone waiting; every job is written in the same transaction as the change it's about, safe to run twice, tried again when it can help and never when it can't; and the timetable checks on payments and tidies up, once, however many workers run it.

One worry is left at lunchtime: the menu. Every phone opens the app and asks for it, hundreds of times a minute, and every time Postgres works it out again, though it changes a few times a day. Keeping the answer ready, and making sure it's never wrong, is caching: the next lesson.

## Related
<!-- bite: f127566a-8118-4873-9683-e1c1677606dd -->

- [[backend/frameworks/axum/19-caching|Next: Caching]]
- [[backend/frameworks/net-http/18-background-jobs|The same lesson in net/http]] — jobs in Redis with asynq, and the sweeper that needs
- [[backend/frameworks/axum/17-payments-and-webhooks|Payments and Webhooks]] — the hand-made queue this lesson starts from
- [[backend/frameworks/axum/03-middleware|Middleware]] — Tower layers, and why their order matters

## About this lesson
<!-- bite: d92b11a1-eacc-46e0-b7dd-39790acab56c -->

**Level:** Advanced. Lesson 18 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), apalis 1.2 with apalis-postgres and apalis-cron, jiff-cron 0.3 and image 0.25. Covers what belongs in a job, why the queue lives in Postgres and how that closes the gap a Redis queue needs a sweeper for, a `Job` trait with keys, adding jobs inside a transaction with a savepoint, `LISTEN`/`NOTIFY` with a polling fallback for delayed jobs, receipts, reminders and photo re-encoding on `spawn_blocking` as plain functions safe to run twice, a worker program in `src/bin` with a worker per queue, Tower concurrency and retry layers and their order, retries tested for real and `AbortError` for hopeless jobs, delayed jobs, a timetable deduplicated by keys, batched cleanup, polite shutdown and heartbeats, watching the queue with SQL, and testing jobs with a fake mailer and real workers.
