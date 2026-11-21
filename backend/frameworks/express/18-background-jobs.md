---
id: 82f5efb9-529e-4536-a85f-536bd7baef58
---

# Background Jobs and Queues

**A background job is a piece of work the server does *after* it has answered the request, or on a timer, instead of while the customer waits. A queue is the list those jobs wait in, and a worker is the program that takes jobs off the list and does them.** Ada taps "Pay", and her screen should say "Paid!" in a second. The receipt email, the delivery partner's webhook, the photo resizing: none of that needs to happen *before* she sees it. It just needs to happen, reliably, soon.

## Before you start
<!-- bite: e7ff5eff-c5eb-4873-8137-c8eb56bffd96 -->

You should have payments and webhooks from [[backend/frameworks/express/17-payments-and-webhooks|lesson 17]], including its hand-made webhook sender, because this lesson replaces it.

You'll also run **Redis**, a small, very fast database that keeps its data in memory. You'll start it with Docker, like Postgres.

After this lesson you will be able to:

1. Say which work belongs in the request and which belongs in a job.
2. Run Redis and BullMQ, add jobs from Express, and process them in a separate worker program.
3. Make jobs safe to run more than once, with retries, backoff, and jobs that should never be retried.
4. Run jobs later (delayed) and on a schedule (every hour).
5. Catch jobs that got lost between Postgres and Redis, with a sweeper.
6. Shut workers down without dropping half-done work, and test jobs without Redis.

## Where we stopped
<!-- bite: 919fd95b-d166-409e-be31-b3d5380b9b87 -->

At the end of lesson 17 we had built, without saying so, a little job queue: the `webhook_deliveries` table, a loop that wakes every 5 seconds, a lease so two servers don't send the same webhook, backoff with jitter.

It works. But look at what's coming:

1. **Receipts.** When a payment succeeds, Ada should get an email.
2. **Photos.** Lesson 14 said real systems re-encode every uploaded photo and make smaller copies. That takes a second or two of hard work per photo.
3. **The safety net.** Lesson 17 promised an hourly check on payments still `started`, in case a webhook never arrived.
4. **Webhooks** to Okada Riders, which already have their own loop.

Write a table, a loop and a lease for each of those, and you have four little queues, each with its own bugs. Time for a real one.

## The kid version
<!-- bite: 33d99bbc-05df-414f-af27-6a77a0747319 -->

At Mama Put, the person who takes your order isn't the person who cooks it. The waiter writes your order on a slip and pins it to the board in the kitchen. Then he's free to take the next customer's order.

The cooks take slips off the board, one at a time, and cook. If there's a rush, Mama calls in another cook, and two people take slips off the same board. If a cook burns a pot, he puts the slip back up and tries again.

The board is the queue. Each slip is a job. The cooks are workers. And the waiter, who just pins slips up and moves on, is our Express app.

**Where the picture stops working.** At Mama Put, if the board falls off the wall, the slips are on the floor and someone picks them up. In software, if the queue loses a job, nobody knows it was ever there. So we'll also keep a record in Postgres, and check it now and then.

## Terms used in background jobs
<!-- bite: 7c302ec3-1991-4905-8cdf-8b9bb81eb628 -->

1. **Job**: This is one piece of work to do later, with a name and a little data, like `send-receipt` with `{ paymentId: "17" }`.
2. **Queue**: This is where jobs wait. Ours live in Redis.
3. **Producer**: This is the code that adds jobs. Our Express app is a producer.
4. **Worker**: This is the code that takes jobs from a queue and runs them. Ours runs as its own program, `worker.ts`, separate from the web server.
5. **Concurrency**: This is how many jobs one worker runs at the same time.
6. **Retry** and **backoff**: A retry runs a failed job again; backoff is waiting longer between each try.
7. **Delayed job**: This is a job that shouldn't start until a certain time, like "in 10 minutes".
8. **Scheduled (repeating) job**: This is a job added again and again on a timetable, like "at five past every hour".
9. **Stalled job**: This is a job a worker took but never finished, because the worker crashed or froze. The queue notices and gives it to someone else.
10. **Redis**: This is an in-memory database. BullMQ uses it to hold queues, because Redis can hand out jobs very fast and safely to many workers at once.

## Step 1: what goes in a job?
<!-- bite: e6b67e04-a577-4e35-8834-015d88de3867 -->

Ask one question about every piece of work in a request: **does the customer need the result in this answer?**

| Work | Needs it now? | Where it goes |
|---|---|---|
| Check the order, take the portions, write the row | Yes: the answer says "order placed" | In the request |
| Mark the payment paid (from the webhook) | Yes: it *is* the webhook's job | In the request |
| Send the receipt email | No | A job |
| Tell Okada Riders the order is ready | No | A job |
| Re-encode a photo and make a thumbnail | No: show the original until it's done | A job |
| Check payments stuck in `started` | Nobody asked; it's on a timer | A scheduled job |

Two more signs something should be a job:

1. **It talks to a service that can be slow or down.** Email providers, partners' servers. You don't want their bad day to become your customer's error.
2. **It's heavy.** Resizing an image uses the CPU for a second or more. Node runs your JavaScript on one thread (lesson 1), so a second of image work in the web server is a second where *no* request gets answered.

And one sign it should **not**: if the work failing must make the request fail. "Take the portions" can't be a job, because if it fails, Ada must hear "sorry, finished", not "order placed".

## Step 2: Redis and BullMQ
<!-- bite: 1022f480-0ad6-42b6-8885-6c6a680c67d3 -->

Start Redis in Docker:

```bash
docker run -d --name mama-put-redis -p 6379:6379 redis:7 \
  redis-server --appendonly yes --maxmemory-policy noeviction
```

The two settings matter for a queue:

1. **`--appendonly yes`** writes every change to disk too. Without it, restarting Redis empties every queue.
2. **`--maxmemory-policy noeviction`** says "if memory is full, refuse new data; never delete old data to make room". The default for some Redis setups is to quietly delete keys when memory runs low, which is fine for a cache (lesson 19) and terrible for a queue: your jobs would just disappear. BullMQ warns you at start-up if this isn't set.

Then:

```bash
npm install bullmq ioredis sharp
```

`bullmq` is the queue library. `ioredis` is the Redis client it uses. `sharp` is for the photo work in step 5.

In `.env`:

```text
REDIS_URL=redis://localhost:6379
```

## Step 3: the queues, and one door into them
<!-- bite: f331548b-28ad-4599-95fa-e8b3b2ad395c -->

`src/jobs/queues.ts`:

```ts
import { Queue } from "bullmq";
import { Redis } from "ioredis";

export const QUEUES = ["emails", "webhooks", "photos", "maintenance"] as const;
export type QueueName = (typeof QUEUES)[number];

export function createRedis(url: string) {
  return new Redis(url, { maxRetriesPerRequest: null });
}

export function createQueues(connection: Redis) {
  const make = (name: QueueName) =>
    new Queue(name, {
      connection,
      defaultJobOptions: {
        attempts: 5,
        backoff: { type: "exponential", delay: 10_000 },  // 10 s, 20 s, 40 s, ...
        removeOnComplete: { age: 24 * 60 * 60, count: 1000 },
        removeOnFail: { age: 7 * 24 * 60 * 60 },
      },
    });

  return {
    emails: make("emails"),
    webhooks: make("webhooks"),
    photos: make("photos"),
    maintenance: make("maintenance"),
  };
}

export type Queues = ReturnType<typeof createQueues>;
```

Why four queues, not one? So each kind of work has its own workers and its own speed. A thousand photos waiting to be resized shouldn't hold up Ada's receipt.

The default job options, in words:

1. **`attempts: 5`**: try up to five times.
2. **`backoff: exponential, 10 s`**: wait 10 seconds before the second try, 20 before the third, then 40, 80.
3. **`removeOnComplete`**: keep finished jobs for a day (at most 1,000), so you can look at recent ones, then clean them up. Without this, Redis fills up with every job ever done.
4. **`removeOnFail`**: keep failed jobs for a week, so a person can see what failed and why.

(`maxRetriesPerRequest: null` is something BullMQ requires of its Redis connection. It means "if Redis is briefly unreachable, keep waiting instead of throwing", which is what a worker that waits for jobs needs.)

Now, the rest of the app should not know BullMQ exists. The orders service doesn't know about SQL, and it won't know about queues. It gets a small type with one method per job.

`src/jobs/jobs.ts`:

```ts
import type { Queues } from "./queues.ts";

export type Jobs = {
  sendReceipt(paymentId: string): Promise<void>;
  deliverWebhook(deliveryId: string): Promise<void>;
  processPhoto(dishId: string, fileName: string): Promise<void>;
};

export function createBullJobs(queues: Queues): Jobs {
  return {
    async sendReceipt(paymentId) {
      await queues.emails.add("send-receipt", { paymentId }, { jobId: `receipt-${paymentId}` });
    },
    async deliverWebhook(deliveryId) {
      await queues.webhooks.add(
        "deliver-webhook",
        { deliveryId },
        { jobId: `webhook-${deliveryId}`, attempts: 15, backoff: { type: "webhook" } },
      );
    },
    async processPhoto(dishId, fileName) {
      await queues.photos.add("process-photo", { dishId, fileName }, { jobId: `photo-${fileName}` });
    },
  };
}
```

Two habits here that matter more than they look.

**Every job has a `jobId` we choose.** BullMQ won't add a job whose id already exists. So if the payment webhook arrives twice and both try to queue Ada's receipt, the second `add` does nothing. Same idea as the idempotency keys in lesson 15: a name for the work makes "add it again" harmless. (BullMQ doesn't allow `:` in a custom id, which is why these use `-`.)

**The job data is tiny: ids, not objects.** `send-receipt` carries `{ paymentId: "17" }`, not Ada's email address and her order. Three reasons:

1. **Freshness.** The job might run a minute later, or (after retries) an hour later. Ada might have changed her email by then. The worker reads the current data from Postgres when it runs.
2. **Privacy.** Job data sits in Redis, shows up in queue dashboards, and often ends up in logs when a job fails. An id there tells nobody anything. An email address and a phone number tell them a lot.
3. **Size.** Redis keeps everything in memory. A million small ids is fine; a million copies of order details isn't.

## Step 4: the worker program
<!-- bite: ed2cb5d3-5e92-4057-8efe-37af9e9ec625 -->

The worker is a **second program**, with its own composition root, like `server.ts`. Same code folder, same repositories and services, but it doesn't listen on a port. It just takes jobs and runs them.

Why separate? Because the two jobs pull in different directions. The web server must answer every request quickly; a worker resizing photos hogs the CPU. Separate, you can run three web servers and one worker, or one web server and five workers at lunchtime, and a crashing photo job can never take the website down with it.

First, the work itself, as **plain functions** that take their dependencies and the job's data. No BullMQ in them, which makes them easy to test.

`src/jobs/processors/send-receipt.ts`:

```ts
import type { PaymentsRepository } from "../../payments/payments.pg-repository.ts";
import type { Mailer } from "../../shared/mailer.ts";

export async function sendReceipt(
  deps: { payments: PaymentsRepository; mailer: Mailer },
  data: { paymentId: string },
) {
  const receipt = await deps.payments.receiptDetails(data.paymentId);
  if (!receipt || receipt.receiptSentAt) return "skipped";    // gone, or already sent

  await deps.mailer.send({
    to: receipt.email,
    subject: `Mama Put receipt for order ${receipt.orderId}`,
    text: `Thank you, ${receipt.name}! We received ₦${(receipt.amountKobo / 100).toLocaleString("en-NG")} for order ${receipt.orderId}.`,
  });
  await deps.payments.markReceiptSent(data.paymentId);
  return "sent";
}
```

(`receiptDetails` joins payments, orders and users to get what the email needs. `markReceiptSent` sets a new column, `payments.receipt_sent_at`, from `migrations/013_job_bookkeeping.sql`, which also adds `dishes.thumbnail`. The `Mailer` is a type with one method, `send`; in development it just prints the email to the terminal, and in production it calls whichever email service Mama picks.)

Now the question you must ask of **every** job: *what if it runs twice?*

BullMQ promises each job runs at least once, not exactly once. Picture the worker sending the email, and then crashing before it tells Redis "done". The job looks stalled, and another worker runs it again. Ada gets two receipts.

Can we stop that completely? Not here: we can't send an email and write to Postgres as one atomic step. So we choose which way to be wrong:

1. **Mark sent, then send**: a crash in between means Ada gets **no** receipt.
2. **Send, then mark sent**: a crash in between means Ada gets **two**.

For a receipt, two is far better than none, so we send first. The `receiptSentAt` check at the top still stops every *normal* repeat (the jobId already stops most of them). For money, we made the opposite kind of choice in lesson 17, where the database's conditional `UPDATE` makes "twice" impossible. Every job deserves this question, and the answer depends on what "twice" costs.

`src/jobs/processors/deliver-webhook.ts` is lesson 17's `send`, now run by BullMQ:

```ts
export async function deliverWebhook(
  deps: { deliveries: Deliveries; secret: string },
  data: { deliveryId: string },
) {
  const delivery = await deps.deliveries.findById(data.deliveryId);
  if (!delivery || delivery.deliveredAt) return "skipped";

  try {
    await signAndSend(delivery, deps.secret);   // lesson 17's send(), moved into its own function
  } catch (err) {
    await deps.deliveries.recordFailure(delivery.id, err instanceof Error ? err.message : String(err));
    throw err;                                  // tell BullMQ it failed, so it retries
  }
  await deps.deliveries.markDelivered(delivery.id);
  return "sent";
}
```

The `throw err` after recording is the important line. A processor tells BullMQ "this failed, try again later" by throwing. Catch an error and *not* rethrow it, and BullMQ thinks the job succeeded.

Now the worker program, `src/worker.ts`:

```ts
import pg from "pg";
import { Worker, type Job } from "bullmq";
import { createRedis } from "./jobs/queues.ts";
import { backoffSeconds } from "./webhooks/backoff.ts";
import { sendReceipt } from "./jobs/processors/send-receipt.ts";
import { deliverWebhook } from "./jobs/processors/deliver-webhook.ts";
import { processPhoto } from "./jobs/processors/process-photo.ts";
import { runMaintenance } from "./jobs/processors/maintenance.ts";
// ...the repositories, mailer and provider, built exactly as in server.ts

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const connection = createRedis(process.env.REDIS_URL!);
// const payments = ..., deliveries = ..., mailer = ..., and so on

const workers = [
  new Worker("emails", (job) => sendReceipt({ payments, mailer }, job.data), {
    connection,
    concurrency: 5,
  }),
  new Worker("webhooks", (job) => deliverWebhook({ deliveries, secret }, job.data), {
    connection,
    concurrency: 10,
    settings: {
      backoffStrategy: (attemptsMade: number) => backoffSeconds(attemptsMade) * 1000,
    },
  }),
  new Worker("photos", (job) => processPhoto({ menuRepository, photosFolder }, job.data), {
    connection,
    concurrency: 1,
  }),
  new Worker("maintenance", (job) => runMaintenance(maintenanceDeps, job), {
    connection,
    concurrency: 1,
  }),
];

for (const worker of workers) {
  worker.on("failed", (job: Job | undefined, err: Error) => {
    const willRetry = job != null && job.attemptsMade < (job.opts.attempts ?? 1);
    console.error(JSON.stringify({
      msg: willRetry ? "job failed, will retry" : "job failed for good",
      queue: worker.name, job: job?.name, id: job?.id, attempt: job?.attemptsMade, error: err.message,
    }));
  });
}

console.log("worker started");
```

Run it in a second terminal, next to the server:

```json
"scripts": {
  "dev": "node --env-file=.env --watch src/server.ts",
  "worker": "node --env-file=.env --watch src/worker.ts"
}
```

```bash
npm run worker
```

Things to notice:

1. **Concurrency is chosen per queue.** Emails and webhooks mostly *wait* on the network, so one worker can usefully have 5 or 10 going at once. Photos are CPU work, and one at a time is right on a small server. Two photo jobs at once just take twice as long each.
2. **The webhook backoff is lesson 17's**, moved to `src/webhooks/backoff.ts`: 30 seconds, then doubling up to 6 hours, with jitter. Jobs say `backoff: { type: "webhook" }`, and the worker's `backoffStrategy` says how long that means. With `attempts: 15`, that's still about a day and a half before giving up.
3. **`failed` fires on every failed attempt**, not just the last. Comparing `attemptsMade` with `attempts` tells you which it was. "Failed for good" is the one a person needs to see (lesson 27 sends it to an alert).

And in `server.ts`, the producer side is two lines:

```ts
const redis = createRedis(process.env.REDIS_URL!);
const jobs = createBullJobs(createQueues(redis));
```

`jobs` goes into `deps`, like everything else.

## Step 5: using the jobs
<!-- bite: f7d97fd1-c341-4742-98b9-0f76341f7f82 -->

**Receipts.** In the payments service's `settle`, from lesson 17:

```ts
const result = await payments.markSucceeded(reference);
if (result === "paid") await jobs.sendReceipt(payment.id);
```

Only on `"paid"`: the one call that actually changed the payment. Repeats of the webhook return `"already-settled"` and queue nothing.

**Webhooks.** In the orders service, `deliveries.enqueue` now returns the new row's id, and the job is added right after:

```ts
const deliveryId = await deliveries.enqueue(deliveryWebhookUrl, "order.ready", { orderId: order.id, ... });
await jobs.deliverWebhook(deliveryId);
```

Delete lesson 17's `sender.ts`, `claimDue` and the `setInterval`. BullMQ now does the timing, the retries, and makes sure two workers never take the same job. `webhook_deliveries` stays as our **record** of every webhook: what was sent, when it was delivered, the last error. That's what the admin route from lesson 17's practice reads, and its "retry" button now just calls `jobs.deliverWebhook(id)` again.

**Photos.** In the photo upload route from lesson 14, after `setPhoto`:

```ts
await jobs.processPhoto(id, fileName);
```

and the processor, `src/jobs/processors/process-photo.ts`:

```ts
import sharp from "sharp";
import { UnrecoverableError } from "bullmq";

export async function processPhoto(
  deps: { menuRepository: MenuRepository; photosFolder: URL },
  data: { dishId: string; fileName: string },
) {
  const original = new URL(data.fileName, deps.photosFolder);
  const base = data.fileName.replace(/\.[a-z]+$/, "");
  const large = `${base}-large.webp`;
  const thumb = `${base}-thumb.webp`;

  try {
    const image = sharp(original.pathname).rotate();   // turn it the right way up
    await image.clone().resize({ width: 1200, withoutEnlargement: true }).webp({ quality: 80 })
      .toFile(new URL(large, deps.photosFolder).pathname);
    await image.clone().resize({ width: 400, height: 400, fit: "cover" }).webp({ quality: 75 })
      .toFile(new URL(thumb, deps.photosFolder).pathname);
  } catch (err) {
    // A file sharp can't read will never become readable. Don't retry it 5 times.
    throw new UnrecoverableError(`can't process ${data.fileName}: ${(err as Error).message}`);
  }

  await deps.menuRepository.setProcessedPhoto(data.dishId, data.fileName, { large, thumb });
}
```

Three things are going on:

1. **Re-encoding.** sharp decodes the image into plain pixels and writes a brand-new WebP. Anything hidden in the original file (lesson 14's worry) doesn't survive that. By default sharp also leaves out the metadata, including the GPS location phones put in photos. `.rotate()` with no arguments first turns the picture the right way up, using the phone's orientation note, before that note is thrown away.
2. **`UnrecoverableError`.** Some failures will never succeed, however often you try: a corrupt file, a missing dish. Throwing `UnrecoverableError` tells BullMQ "fail this now, no retries". Retrying hopeless jobs wastes time and hides the real failures among noise.
3. **`setProcessedPhoto(dishId, fileName, ...)` checks the file name.** Its SQL is `UPDATE dishes SET photo = $3, thumbnail = $4 WHERE id = $1 AND photo = $2`. If the cook uploaded a *newer* photo while this job was running, the old job's result doesn't overwrite it. Jobs run late, and late work must not undo newer work.

Until the job finishes, the menu shows the original photo; after, the presenter shows the `large` and `thumbnail` versions. Ada never waits for any of it.

## Step 6: later, and on a timetable
<!-- bite: cd4dfd86-e9aa-418d-9a92-b2d75b999b62 -->

**Delayed jobs.** Some work should happen *later*. Say Mama wants a "how was your food?" email an hour after an order is collected:

```ts
await queues.emails.add("ask-for-review", { orderId }, { jobId: `review-${orderId}`, delay: 60 * 60 * 1000 });
```

The job sits in the queue as *delayed* and becomes ready after an hour. Redis holds it, so a restart of our app doesn't lose it.

**Scheduled jobs.** Lesson 17's safety net: once an hour, check every payment that's still `started` after 15 minutes. In `worker.ts`:

```ts
await queues.maintenance.upsertJobScheduler(
  "check-unsettled-payments",
  { pattern: "5 * * * *" },                   // at 5 minutes past every hour
  { name: "check-unsettled-payments" },
);
await queues.maintenance.upsertJobScheduler(
  "sweep-lost-jobs",
  { every: 10 * 60 * 1000 },                  // every 10 minutes
  { name: "sweep-lost-jobs" },
);
```

`upsertJobScheduler` means "create this schedule, or update it if it already exists". Run five workers and they all call it, and there's still exactly **one** schedule, and each hour's job runs once. That's the big difference from a `setInterval` in each worker, which would run five times an hour.

The `pattern` is a **cron** pattern: five fields for minute, hour, day of the month, month, and day of the week. `5 * * * *` means "minute 5, every hour, every day". `0 7 * * 1` would be "7:00 every Monday".

The maintenance processor looks at the job's name:

```ts
export async function runMaintenance(deps: MaintenanceDeps, job: Job) {
  switch (job.name) {
    case "check-unsettled-payments": {
      const stuck = await deps.payments.startedBetween("15 minutes", "24 hours");
      for (const payment of stuck) {
        await deps.paymentsService.settle(payment.reference, await deps.provider.verify(payment.reference));
      }
      return { checked: stuck.length };
    }
    case "sweep-lost-jobs":
      return sweepLostJobs(deps);
    default:
      throw new UnrecoverableError(`unknown maintenance job ${job.name}`);
  }
}
```

Every payment goes through the same `settle` as the webhook and the verify route. That's three doors into one room, and the room is safe to enter twice.

## Step 7: the gap between Postgres and Redis
<!-- bite: c3f721df-fbb9-4b89-92df-40928aa2a3cb -->

Look at the receipts code again:

```ts
const result = await payments.markSucceeded(reference);   // Postgres
if (result === "paid") await jobs.sendReceipt(payment.id); // Redis
```

Two different databases. If our app crashes between those two lines, or Redis is down for a moment, the payment is marked paid and the receipt job never exists. Nothing will ever send it. And there's no transaction that covers both Postgres and Redis.

The fix is to let **Postgres** be the truth and check it now and then. Everything a job is about is already written down in Postgres: a paid payment with no `receipt_sent_at`, a webhook delivery with no `delivered_at`. So every 10 minutes, the sweeper looks for those and queues them again:

```ts
async function sweepLostJobs(deps: MaintenanceDeps) {
  const receipts = await deps.payments.paidWithoutReceipt("10 minutes");
  for (const id of receipts) await deps.jobs.sendReceipt(id);

  const webhooks = await deps.deliveries.undeliveredOlderThan("10 minutes");
  for (const id of webhooks) await deps.jobs.deliverWebhook(id);

  return { receipts: receipts.length, webhooks: webhooks.length };
}
```

This is safe because of the jobIds from step 3. If the job does exist (it's just waiting for its next retry), adding it again with the same id does nothing. If it was really lost, now it exists. The "older than 10 minutes" stops the sweeper from racing with work that was queued a second ago and is about to run.

(`undeliveredOlderThan` leaves out the deliveries we gave up on. When the last attempt fails, the `failed` handler marks the row as given up, so the sweeper doesn't bring it back to life every 10 minutes.)

There's a neater way to close this gap, where the job is written into Postgres *in the same transaction* as the change, and a relay moves it to the queue. That's the **outbox** in [[backend/frameworks/express/25-splitting-out-a-microservice|lesson 25]]. The sweeper is the simpler cousin, and for receipts it's enough.

## Step 8: stopping workers politely
<!-- bite: d011bba6-577a-40c5-81af-edc71e121ac8 -->

When you deploy a new version, the old worker gets a signal to stop (`SIGTERM`). If it just dies, the photo it was halfway through becomes a stalled job. BullMQ will notice and run it again (after about 30 seconds), so it isn't lost. But it's wasted work, and a webhook halfway through might be sent twice.

Better to finish what's in hand, and take nothing new. At the end of `worker.ts`:

```ts
let stopping = false;
async function shutdown(signal: string) {
  if (stopping) return;
  stopping = true;
  console.log(`${signal}: finishing current jobs`);
  await Promise.all(workers.map((worker) => worker.close()));  // waits for running jobs
  await connection.quit();
  await pool.end();
  process.exit(0);
}
process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));   // Ctrl+C
```

`worker.close()` stops taking new jobs and waits for the running ones to finish. Then we close Redis and Postgres and exit. Press Ctrl+C on `npm run worker` while a photo is processing and watch it finish first.

This is the reason jobs must be fairly short. A job that takes 20 minutes can't finish politely in the few seconds a deploy gives it. Split long work into many small jobs. [[backend/frameworks/express/28-production-config-and-docker|Lesson 28]] does the same for the web server.

## Step 9: watching the queues
<!-- bite: 9d58c001-b6c6-4fbc-b69f-539b89784606 -->

You'll want to know: how many jobs are waiting? Which failed, and why? A queue that's quietly growing is a problem you want to see on Tuesday, not discover on Friday.

1. **Counts.** `await queues.emails.getJobCounts("waiting", "active", "delayed", "failed")` gives the numbers. Add them to an admin-only route, `GET /v2/admin/queues`. Lesson 27 turns them into graphs and alerts.
2. **A dashboard.** **Bull Board** (`@bull-board/express`) is a ready-made web page that lists every queue and job, shows the errors, and has a "retry" button. It's very useful, and it shows job data and errors, so it must only ever be reachable by admins, never on the open internet. (That's one more reason job data holds ids, not personal details.)

## Step 10: testing jobs
<!-- bite: f0ab51cb-743e-49e5-859d-5d2504a862b1 -->

**Processors are plain functions**, so they're tested like services, with no Redis at all:

```ts
it("sends one receipt, then skips", async () => {
  const sent: string[] = [];
  const mailer = { send: async (mail: { to: string }) => { sent.push(mail.to); } };
  const payments = fakePaymentsWithOnePaid({ paymentId: "17", email: "ada@test.example" });

  assert.equal(await sendReceipt({ payments, mailer }, { paymentId: "17" }), "sent");
  assert.equal(await sendReceipt({ payments, mailer }, { paymentId: "17" }), "skipped");
  assert.deepEqual(sent, ["ada@test.example"]);
});
```

**HTTP tests use a fake `Jobs`** that just records what was asked:

```ts
export function createRecordingJobs() {
  const added: { name: string; args: string[] }[] = [];
  const record = (name: string) => async (...args: string[]) => { added.push({ name, args }); };
  return {
    added,
    sendReceipt: record("sendReceipt"),
    deliverWebhook: record("deliverWebhook"),
    processPhoto: record("processPhoto"),
  };
}
```

Then a test can check "a signed `charge.success` webhook queues exactly one receipt, and sending it three times still queues one".

**An integration test with real Redis** checks the wiring once: start a `Worker` on a test queue, add a job that fails twice and then succeeds, and check it ran three times. Point it at a separate Redis database (`redis://localhost:6379/1`) and empty it with `flushdb` before each test, the same care as lesson 16's `_test` Postgres database.

## The TypeScript in this lesson
<!-- bite: 89392a1c-8457-49b4-9abc-b97489872e1d -->

1. **`import { Redis } from "ioredis"`**: ioredis gives its client class as a named export. `new Redis(url, {...})` connects.
2. **`(typeof QUEUES)[number]`**: `QUEUES` is an `as const` array, so its type is the exact list `readonly ["emails", "webhooks", ...]`. Indexing that type with `number` means "the type of any item", which is `"emails" | "webhooks" | "photos" | "maintenance"`. The list of names and the type can never drift apart.
3. **`const make = (name: QueueName) => new Queue(...)`**: A small arrow function inside `createQueues`, so the shared options are written once.
4. **`new Worker("emails", (job) => sendReceipt(...), {...})`**: The second argument is the processor: a function BullMQ calls with each job. Whatever it returns (or the promise resolves to) is saved as the job's result; if it throws, the job failed.
5. **`import { Worker, type Job } from "bullmq"`**: `type` inside the braces imports `Job` only as a type, which `verbatimModuleSyntax` requires for things used only as types. `Worker` is a real class we use at runtime, so it's a normal import.
6. **`job: Job | undefined`**: BullMQ may call `failed` without a job in rare cases (when the job couldn't even be loaded), so the type allows `undefined`, and the code uses `job?.name`.
7. **`job.opts.attempts ?? 1`**: The job's options may not set `attempts`. `??` uses 1 if it's missing.
8. **`(err as Error).message`**: `as` tells TypeScript "treat this as an `Error`". It checks nothing at runtime; it's us promising. It's acceptable here because sharp only throws `Error`s; in general prefer `err instanceof Error ? ... : ...`, as in `deliverWebhook`.
9. **`image.clone()`**: Not TypeScript, but worth knowing: a sharp image is a recipe of steps. `clone()` lets two different recipes (large and thumbnail) start from the same decoded picture.
10. **`switch (job.name) { case "...": {...} }`**: Picks a branch by the value. The `{ }` after a `case` gives it its own block, so `const stuck` in one case can't clash with a `const` in another. `default` catches every other value.
11. **`const record = (name: string) => async (...args: string[]) => {...}`**: A function that *returns* a function. `record("sendReceipt")` makes a recording function for that name. `...args` collects however many arguments it's called with into an array.
12. **`process.on("SIGTERM", () => shutdown("SIGTERM"))`**: Runs our function when the operating system asks the program to stop. Without a handler, Node just exits.

## Your project so far
<!-- bite: b9b0645e-e4d9-4963-af16-3ea285a53188 -->

```text
mama-put-api/
├── .env · .env.example           ← NEW: REDIS_URL
├── .env.test · .gitignore · tsconfig.json
├── package.json                  ← bullmq, ioredis, sharp; NEW "worker" script
├── migrations/
│   ├── 001 … 012
│   └── 013_job_bookkeeping.sql   ← NEW: payments.receipt_sent_at, dishes.thumbnail
├── uploads/photos/               ← originals, plus -large.webp and -thumb.webp made by the worker
├── openapi/ · test/integration/  ← + a real-Redis test of retries
└── src/
    ├── server.ts                 ← the producer: builds Redis, queues and Jobs; no sender loop any more
    ├── worker.ts                 ← NEW: the second program: four Workers, schedules, polite shutdown
    ├── jobs/
    │   ├── queues.ts             ← NEW: queue names, createRedis, createQueues with default retries
    │   ├── jobs.ts               ← NEW: the Jobs type and its BullMQ version, with our own jobIds
    │   ├── recording-jobs.ts     ← NEW: the fake Jobs for tests
    │   └── processors/
    │       ├── send-receipt.ts   ← NEW: send, then mark sent (two is better than none)
    │       ├── deliver-webhook.ts ← NEW: lesson 17's send, records failures and rethrows
    │       ├── process-photo.ts  ← NEW: sharp re-encode, large + thumbnail, UnrecoverableError
    │       ├── maintenance.ts    ← NEW: check-unsettled-payments, sweep-lost-jobs
    │       └── *.test.ts         ← NEW: processors tested as plain functions
    ├── webhooks/
    │   ├── deliveries.ts         ← enqueue returns the id; findById, recordFailure, undeliveredOlderThan
    │   └── backoff.ts            ← backoffSeconds, moved out of the old sender.ts (deleted)
    ├── payments/                 ← settle queues a receipt on "paid"; new repository queries for the jobs
    ├── menu/                     ← photo upload queues processPhoto; setProcessedPhoto checks the file name
    ├── shared/
    │   └── mailer.ts             ← NEW: the Mailer type; a console version for development
    └── orders/ · auth/ · admin/ · docs/ · db/ · types/ · test-support/
```

## Common mistakes
<!-- bite: b2b90e26-f4c5-4e9c-8646-51b55a2d26b4 -->

1. **Putting must-succeed work in a job.** If the customer must hear about a failure, it belongs in the request.
2. **Heavy work in the web server.** One photo resize blocks every request for a second. Do it in the worker.
3. **Whole objects in job data.** They go stale, take up memory, and leak personal details into Redis, dashboards and logs. Send ids.
4. **No jobId.** Then every repeat of a webhook queues another receipt.
5. **Catching an error in a processor and not rethrowing it.** BullMQ thinks the job succeeded and never retries.
6. **Retrying hopeless jobs.** A corrupt file fails five times and buries the real failures. Throw `UnrecoverableError`.
7. **Forgetting that jobs run at least once.** Ask "what if this runs twice?" of every job, and pick which way to be wrong.
8. **Redis that can throw jobs away.** Without `noeviction` and `appendonly`, memory pressure or a restart silently loses queued work.
9. **A `setInterval` for scheduled work.** It runs once per copy of the app. Use a job scheduler, which runs once however many workers you have.
10. **Trusting Redis to remember everything.** Keep the truth in Postgres and sweep for work that got lost.

## Check your understanding
<!-- bite: 73d34cf1-fda7-4a86-a09c-fa5ec306aa70 -->

1. Which of these should be jobs? (a) Checking Ada's password at login. (b) Sending Bayo a "your order is ready" text message. (c) Taking the portions for an order. (d) Making a PDF of last month's sales for Mama.
2. Why does the receipt job carry `{ paymentId }` instead of `{ email, name, amount }`?
3. The webhook arrives three times. How many receipt jobs exist, and what makes it that number?
4. Why does `send-receipt` send the email *before* marking it sent?
5. You run three copies of `worker.ts`. How many times an hour does `check-unsettled-payments` run, and why?
6. The app marks a payment paid, then crashes before `jobs.sendReceipt`. What happens to Ada's receipt?

<details>
<summary>Answers, after your attempt</summary>

1. (b) and (d). Sending a text talks to a slow outside service, and Bayo doesn't need it inside any response. A sales PDF is heavy and nobody's waiting on a click for it. (a) and (c) must give their answer in the response: "wrong password", "sorry, finished".
2. The worker reads the current details from Postgres when it runs, so they're fresh even after retries. And an id in Redis, dashboards and error logs reveals nothing about Ada, while her email and payment would.
3. One. Only the first call to `markSucceeded` returns `"paid"`, so only one call queues a receipt. Even if two calls did, they'd both use the jobId `receipt-17`, and BullMQ ignores a second job with an id that already exists.
4. Because we have to pick a way to be wrong when the worker crashes in the middle. Send-then-mark risks a duplicate receipt; mark-then-send risks no receipt at all. A duplicate receipt is a small annoyance; a missing one is a customer wondering if they paid.
5. Once. `upsertJobScheduler` keeps a single schedule in Redis, however many workers call it, and each scheduled job is taken by exactly one worker.
6. Within about 10 minutes, the sweeper finds a paid payment with no `receipt_sent_at` and queues the receipt. Postgres remembered the work even though Redis never heard of it.

</details>

## Practice
<!-- bite: dad5e69a-410d-4ff2-88c5-cb195f815ea6 -->

1. Write `migrations/013_job_bookkeeping.sql` and the repository queries the jobs use: `receiptDetails`, `markReceiptSent`, `paidWithoutReceipt`, `startedBetween`, and `undeliveredOlderThan`.
2. In the `failed` handler, when a webhook job fails for good, mark its delivery row as given up (set `next_attempt_at` to `'infinity'` like lesson 17), so the sweeper skips it.
3. Add `thumbnailUrl` to the v2 dish presenter (and to `DishV2Schema`, so the contract test from lesson 16 still passes). It's `null` until the worker has made the thumbnail. `photoUrl` needs no change: it shows the original until the job swaps in the large WebP.
4. Add `GET /v2/admin/queues` (admin only) that returns the waiting, active, delayed and failed counts for each queue.
5. Add the "how was your food?" email as a delayed job, queued when an order becomes `collected`. Check what happens if the order is collected twice.
6. Write the processor tests from step 10, and one integration test with real Redis showing a job that fails twice, then succeeds.

**Done when** paying for an order sends exactly one receipt (printed by the console mailer) even when the webhook arrives three times; uploading a photo returns at once and a `-thumb.webp` appears a moment later; stopping `npm run worker` for a few minutes and starting it again delivers everything that was waiting; deleting a receipt job from Redis by hand gets it sent anyway by the next sweep; and Ctrl+C during a photo job lets it finish first.

## Before moving on
<!-- bite: ca947493-6f57-4a8c-bc71-03712313ee6d -->

Mama Put API now has two programs: the web server, which answers quickly, and the worker, which does the slow and unreliable things in the background, with retries, schedules, and a sweeper that catches anything that slipped through.

And now Redis is running. It's very good at one more thing. Every time someone opens the app, we ask Postgres for the menu, the same menu, hundreds of times a minute at lunch. Mama changes the menu maybe twice a day. Asking the database the same question again and again, when the answer barely changes, is the job a **cache** is made for. That's the next lesson, and the hard part isn't storing the answer. It's knowing when the stored answer has gone stale.

## Related
<!-- bite: 8e621751-bae3-4d78-abac-3da4a9bd0387 -->

- [[backend/frameworks/express/19-caching|Next: Caching with Redis]]
- [[backend/frameworks/express/17-payments-and-webhooks|Payments and Webhooks]] — the hand-made queue this lesson replaced
- [[backend/frameworks/express/15-idempotency|Idempotency]] — the same "a name for the work makes repeats harmless" idea
- [[backend/frameworks/express/25-splitting-out-a-microservice|Splitting Out a Microservice]] — the outbox, which closes the Postgres-to-queue gap properly

## About this lesson
<!-- bite: 6002e881-c6c8-4d96-b323-57b1eba697bb -->

**Level:** Intermediate → Advanced. Lesson 18 of [[backend/frameworks/express/index|Express]]. Covers deciding what belongs in a request and what belongs in a job, Redis in Docker with `appendonly` and `noeviction`, BullMQ queues with default attempts, exponential backoff and cleanup, a `Jobs` type that hides BullMQ from services, our own jobIds so repeats are ignored, small job data for freshness, privacy and size, a separate worker program with per-queue concurrency and a custom backoff strategy, processors as plain functions, at-least-once delivery and choosing which way a job may be wrong, rethrowing to retry and `UnrecoverableError` to stop, re-encoding photos with sharp, delayed jobs, cron-style job schedulers that run once however many workers there are, sweeping Postgres for jobs lost on the way to Redis, polite shutdown with `worker.close()`, watching queues, and testing processors, a recording fake, and real Redis.
