---
id: 0481f0d8-e356-49fb-961d-41ba81bce203
---

# Background Jobs and Queues

**A background job is a piece of work the server writes down to do *later*, instead of doing it while the customer waits, and a queue is where those jobs wait until a worker picks them up.** Receipts, emails, image processing, calls to slow partners: the customer's request just leaves a note saying "please do this", answers at once, and a separate program does the work, retrying it if it fails.

## Before you start
<!-- bite: bbc2082b-451a-4a55-b793-f3b8a6c0e8a3 -->

You should have:

1. Finished [[backend/frameworks/net-http/17-payments-and-webhooks|lesson 17]], with payments, the Okada Riders webhooks and their hand-made sender loop.
2. Docker, for running Redis next to Postgres.

After this lesson you will be able to:

1. Decide which work belongs in the request and which belongs in a job.
2. Run Redis for a queue, and add jobs with asynq through one small door the rest of the app knows nothing about.
3. Write a worker program with its own `run`, handlers that are plain functions, retries, and failures that should never be retried.
4. Delay jobs and run them on a timetable, safely, however many workers you run.
5. Close the gap between Postgres and Redis with a sweeper, stop workers politely, watch the queues, and test it all.

## Where we stopped
<!-- bite: 4d250f8f-c037-4ff1-8542-fe2b3d5c4c6a -->

At the end of lesson 17 we had built, without saying so, a little job queue: the `webhook_deliveries` table, a goroutine that wakes every 5 seconds, a lease so two servers don't send the same webhook, backoff with jitter.

It works. But look at what's coming:

1. **Receipts.** When a payment succeeds, Ada should get an email.
2. **Photos.** Lesson 14 said real systems re-encode every uploaded photo and make smaller copies. That's a second or two of hard work per photo.
3. **The safety net.** Lesson 17 promised an hourly check on payments still `started`, in case a webhook never arrived.
4. **Cleaning up.** Lesson 15 promised that old idempotency keys would be deleted after a day.
5. **Webhooks** to Okada Riders, which already have their own loop.

Write a table, a loop and a lease for each, and you have five little queues, each with its own bugs. Time for a real one.

## The kid version
<!-- bite: 87f7393e-7900-495c-a682-e0c062874773 -->

At Mama Put, the person who takes your order isn't the person who cooks it. The waiter writes your order on a slip and pins it to the board in the kitchen. Then he's free to take the next customer's order.

The cooks take slips off the board, one at a time, and cook. If there's a rush, Mama calls in another cook, and two people take slips off the same board. If a cook burns a pot, he puts the slip back up and tries again.

The board is the queue. Each slip is a job. The cooks are workers. And the waiter, who just pins slips up and moves on, is our API.

**Where the picture stops working.** At Mama Put, if the board falls off the wall, the slips are on the floor and someone picks them up. In software, if the queue loses a job, nobody knows it was ever there. So we'll keep the truth in Postgres too, and check it now and then.

## Terms used in this lesson
<!-- bite: 450966c0-f8cc-4e55-acde-c5f36e0a383f -->

1. **Job**: This is also called a **task**. It's one piece of work to do later, with a type and a little data, like `receipt:send` with `{"paymentId": 17}`.
2. **Queue**: This is where jobs wait. Ours live in Redis.
3. **Producer**: This is the code that adds jobs. Our API is a producer.
4. **Worker**: This is the code that takes jobs from a queue and runs them. Ours is its own program, `cmd/worker`, separate from the web server.
5. **Concurrency**: This is how many jobs one worker runs at the same time.
6. **Retry** and **backoff**: A retry runs a failed job again; backoff is waiting longer between each try.
7. **Delayed job**: This is a job that shouldn't start until a certain time, like "in an hour".
8. **Scheduled job**: This is a job added again and again on a timetable, like "at five past every hour", written as a **cron** pattern.
9. **Archived job**: This is asynq's name for a job that failed for good: it ran out of retries, or was told not to retry. It's kept so a person can look.
10. **Redis**: This is an in-memory database. asynq uses it to hold queues, because Redis can hand jobs out very fast, and safely, to many workers at once.

## Step 1: what goes in a job?
<!-- bite: 55a1ff0f-b599-404e-8167-27c7dee7bb25 -->

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
2. **It's heavy.** Resizing an image uses a CPU core for a second or more. Go runs every request in its own goroutine, so one slow photo doesn't freeze other requests the way it would in Node. But it still uses a whole core, and twenty photos at once on a two-core server would make every request slow. Heavy work belongs on machines you can size and count separately.

And one sign it should **not**: if the work failing must make the request fail. "Take the portions" can't be a job, because if it fails, Ada must hear "sorry, finished", not "order placed".

## What to install
<!-- bite: 4b0cae48-4c2b-4494-87e1-03e6fb179b41 -->

Start Redis in Docker:

```bash
docker run -d --name mama-put-redis -p 6379:6379 redis:7 \
  redis-server --appendonly yes --maxmemory-policy noeviction
```

The two settings matter for a queue:

1. **`--appendonly yes`** writes every change to disk too. Without it, restarting Redis empties every queue.
2. **`--maxmemory-policy noeviction`** says "if memory is full, refuse new data; never delete old data to make room". Some Redis setups quietly delete keys when memory runs low, which is fine for a cache (lesson 19) and terrible for a queue: your jobs would just disappear.

Then the queue library, and the Go team's image package for resizing:

```bash
go get github.com/hibiken/asynq
go get golang.org/x/image/draw
```

**asynq** is the job queue most Go projects reach for: jobs in Redis, retries with backoff, delays, schedules, unique jobs, and a web dashboard. (It's the Go cousin of BullMQ in the Express subject, and of Sidekiq in Ruby.) And its command-line tool, for looking inside the queues:

```bash
go get -tool github.com/hibiken/asynq/tools/asynq
```

In `.env`:

```text
REDIS_URL=redis://localhost:6379/0
```

## Step 2: the jobs, and one door into them
<!-- bite: 7a62427b-f056-444d-a8aa-3bac6f5c9332 -->

Each kind of job has a **type** (a name) and a **payload** (its data, as JSON). `internal/jobs/jobs.go`:

```go
// Package jobs is the one door into the job queue. Nothing else imports asynq.
package jobs

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/hibiken/asynq"
)

const (
	TypeSendReceipt    = "receipt:send"
	TypeDeliverWebhook = "webhook:deliver"
	TypeProcessPhoto   = "photo:process"
	TypeAskForReview   = "review:ask"

	// Maintenance jobs, added on a timetable (step 5).
	TypeCheckUnsettled = "payments:check-unsettled"
	TypeSweepLostJobs  = "jobs:sweep-lost"
	TypeCleanUp        = "maintenance:clean-up"
)

type ReceiptPayload struct {
	PaymentID int64 `json:"paymentId"`
}

type WebhookPayload struct {
	DeliveryID string `json:"deliveryId"`
}

type PhotoPayload struct {
	DishID   int64  `json:"dishId"`
	FileName string `json:"fileName"`
}

type ReviewPayload struct {
	OrderID int64 `json:"orderId"`
}

// Client adds jobs. The API holds one.
type Client struct{ c *asynq.Client }

func NewClient(redis asynq.RedisConnOpt) *Client { return &Client{c: asynq.NewClient(redis)} }

func (c *Client) Close() error { return c.c.Close() }

func (c *Client) add(ctx context.Context, typ string, payload any, opts ...asynq.Option) error {
	data, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	_, err = c.c.EnqueueContext(ctx, asynq.NewTask(typ, data), opts...)
	if errors.Is(err, asynq.ErrTaskIDConflict) {
		return nil // already queued: adding it again is harmless, which is the point
	}
	if err != nil {
		return fmt.Errorf("queue %s: %w", typ, err)
	}
	return nil
}

func (c *Client) SendReceipt(ctx context.Context, paymentID int64) error {
	return c.add(ctx, TypeSendReceipt, ReceiptPayload{paymentID},
		asynq.Queue("emails"), asynq.TaskID(fmt.Sprintf("receipt-%d", paymentID)), asynq.MaxRetry(5))
}

func (c *Client) DeliverWebhook(ctx context.Context, deliveryID string) error {
	return c.add(ctx, TypeDeliverWebhook, WebhookPayload{deliveryID},
		asynq.Queue("webhooks"), asynq.TaskID("webhook-"+deliveryID), asynq.MaxRetry(15))
}

func (c *Client) ProcessPhoto(ctx context.Context, dishID int64, fileName string) error {
	return c.add(ctx, TypeProcessPhoto, PhotoPayload{dishID, fileName},
		asynq.Queue("photos"), asynq.TaskID("photo-"+fileName), asynq.MaxRetry(3), asynq.Timeout(time.Minute))
}

func (c *Client) AskForReview(ctx context.Context, orderID int64) error {
	return c.add(ctx, TypeAskForReview, ReviewPayload{orderID},
		asynq.Queue("emails"), asynq.TaskID(fmt.Sprintf("review-%d", orderID)), asynq.ProcessIn(time.Hour))
}
```

The rest of the app never sees asynq. The payments service doesn't know about SQL, and it won't know about queues either. In `internal/payments/service.go`, it declares what it needs, the lesson 5 way:

```go
type Receipts interface {
	SendReceipt(ctx context.Context, paymentID int64) error
}
```

and `*jobs.Client` satisfies it without saying so. A test hands over a fake that records what was asked.

Two habits here matter more than they look.

**Every job has a `TaskID` we choose.** asynq refuses a job whose ID is already in the queue, with `ErrTaskIDConflict`, and `add` treats that as success. So if the payment webhook arrives twice and both try to queue Ada's receipt, the second does nothing. Same idea as lesson 15's idempotency keys: a name for the work makes "add it again" harmless.

**The payload is tiny: IDs, not objects.** `receipt:send` carries `{"paymentId": 17}`, not Ada's email address and her order. Three reasons:

1. **Freshness.** The job might run a minute later, or (after retries) an hour later. Ada might have changed her email by then. The worker reads the current data from Postgres when it runs.
2. **Privacy.** Job data sits in Redis, shows up in queue dashboards, and often ends up in logs when a job fails. An ID tells nobody anything. An email address and a phone number tell them a lot.
3. **Size.** Redis keeps everything in memory. A million small IDs is fine; a million copies of order details isn't.

Why four queues, not one? So each kind of work has its own priority. A thousand photos waiting to be resized shouldn't hold up Ada's receipt. Step 3 gives each queue its weight.

In `run`, the producer side is two lines:

```go
redisOpt, err := asynq.ParseRedisURI(getenv("REDIS_URL"))
if err != nil {
	return fmt.Errorf("REDIS_URL: %w", err)
}
jobClient := jobs.NewClient(redisOpt)
defer jobClient.Close()
```

and `jobClient` goes to whichever services need it, like every other dependency.

## Step 3: the worker program
<!-- bite: cb1bf9c0-a737-4bf8-a189-c8c4cd8ae05e -->

The worker is a **second program**, with its own `main` and its own `run`, in `cmd/worker/`. Same module, same packages, same stores and services, but it doesn't listen for HTTP. It just takes jobs and runs them.

Why separate? Because the two pull in different directions. The web server must answer every request quickly; a worker resizing photos uses whole CPU cores. Separate, you can run three web servers and one worker, or one web server and five workers at lunchtime, and a crashing photo job can never take the website down with it.

### The work itself, as plain functions

First, each job's work, as an ordinary function that takes its dependencies and its data. No asynq inside, which makes them easy to test. `internal/payments/receipts.go`:

```go
type Mailer interface {
	Send(ctx context.Context, to, subject, text string) error
}

type ReceiptDetails struct {
	PaymentID     int64
	OrderID       int64
	Email, Name   string
	Amount        money.Kobo
	ReceiptSentAt *time.Time
}

// SendReceipt emails the receipt for one paid payment. It's safe to run twice:
// a receipt already sent is skipped.
func SendReceipt(ctx context.Context, store ReceiptStore, mail Mailer, paymentID int64) (string, error) {
	r, err := store.ReceiptDetails(ctx, paymentID)
	if errors.Is(err, ErrPaymentNotFound) {
		return "skipped", nil // gone: nothing will ever make it come back
	}
	if err != nil {
		return "", err
	}
	if r.ReceiptSentAt != nil {
		return "skipped", nil
	}

	text := fmt.Sprintf("Thank you, %s! We received ₦%s for order %d.", r.Name, r.Amount.NairaText(), r.OrderID)
	if err := mail.Send(ctx, r.Email, fmt.Sprintf("Mama Put receipt for order %d", r.OrderID), text); err != nil {
		return "", err
	}
	return "sent", store.MarkReceiptSent(ctx, paymentID)
}
```

(`ReceiptDetails` joins payments, orders and users to get what the email needs; `MarkReceiptSent` sets a new column, `payments.receipt_sent_at`. Both are in `ReceiptStore`, an interface with those two methods. `NairaText` is a new `money.Kobo` method that writes `300000` as `3,000.00`. The `Mailer` in development just logs the email; in production it calls whichever email service Mama picks.)

`migrations/013_job_bookkeeping.sql`:

```sql
ALTER TABLE payments ADD COLUMN receipt_sent_at timestamptz;
ALTER TABLE dishes ADD COLUMN photo_large text, ADD COLUMN photo_thumb text;
ALTER TABLE webhook_deliveries ADD COLUMN gave_up_at timestamptz;
```

Now the question you must ask of **every** job: *what if it runs twice?*

asynq promises each job runs at least once, not exactly once. Picture the worker sending the email, and then crashing before it tells Redis "done". asynq notices the job was never finished and runs it again. Ada gets two receipts.

Can we stop that completely? Not here: we can't send an email and write to Postgres as one atomic step. So we choose which way to be wrong:

1. **Mark sent, then send**: a crash in between means Ada gets **no** receipt.
2. **Send, then mark sent**: a crash in between means Ada gets **two**.

For a receipt, two is far better than none, so we send first. The `ReceiptSentAt` check at the top still stops every *normal* repeat (the `TaskID` already stops most of them). For money, we made the opposite choice in lesson 17, where the guarded `UPDATE` makes "twice" impossible. Every job deserves this question, and the answer depends on what "twice" costs.

Lesson 17's webhook `send` moves into `internal/webhooks` as `Deliver(ctx, deliveries, sender, id)`: find the delivery, skip it if it's already delivered, send it, mark it delivered. When the send fails, it records `last_error` and returns the error, so the job is retried. The sending code itself (the signature, the timestamp, the event ID, no redirects) doesn't change at all.

### Turning jobs into calls

The worker's handlers are thin: decode the payload, call the plain function. `internal/jobs/handlers.go`:

```go
// Decode reads a job's payload. A payload that can't be read never will be: don't retry it.
func Decode[T any](t *asynq.Task) (T, error) {
	var v T
	if err := json.Unmarshal(t.Payload(), &v); err != nil {
		return v, fmt.Errorf("bad %s payload: %v: %w", t.Type(), err, asynq.SkipRetry)
	}
	return v, nil
}
```

`asynq.SkipRetry` is how a handler says "this will never work; don't try again". Wrapped in the error with `%w`, asynq finds it with `errors.Is` and archives the job at once, instead of retrying it five times. Retrying hopeless jobs wastes time and buries the real failures in noise.

Now `cmd/worker/main.go`:

```go
package main

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"os"
	"time"

	"github.com/hibiken/asynq"

	"mamaput/internal/db"
	"mamaput/internal/jobs"
	"mamaput/internal/menu"
	"mamaput/internal/payments"
	"mamaput/internal/webhooks"
)

func main() {
	if err := run(os.Getenv, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "mama-put worker:", err)
		os.Exit(1)
	}
}

func run(getenv func(string) string, stdout io.Writer) error {
	logger := slog.New(slog.NewTextHandler(stdout, nil))
	ctx := context.Background()

	pool, err := db.Open(ctx, getenv("DATABASE_URL"))
	if err != nil {
		return err
	}
	defer pool.Close()
	redisOpt, err := asynq.ParseRedisURI(getenv("REDIS_URL"))
	if err != nil {
		return fmt.Errorf("REDIS_URL: %w", err)
	}

	// ... the stores, mailer, photos folder and sender, built exactly as in cmd/api
	paymentStore := payments.NewPostgresStore(pool)
	deliveries := webhooks.NewDeliveries(pool)
	sender := webhooks.NewSender(deliveries, getenv("OKADA_WEBHOOK_SECRET"), logger)
	mailer := payments.LogMailer{Log: logger}
	photos, err := menu.OpenPhotos(getenv("PHOTOS_DIR"))
	if err != nil {
		return err
	}
	photoSlot := make(chan struct{}, 1) // one photo at a time

	mux := asynq.NewServeMux()
	mux.HandleFunc(jobs.TypeSendReceipt, func(ctx context.Context, t *asynq.Task) error {
		p, err := jobs.Decode[jobs.ReceiptPayload](t)
		if err != nil {
			return err
		}
		_, err = payments.SendReceipt(ctx, paymentStore, mailer, p.PaymentID)
		return err
	})
	mux.HandleFunc(jobs.TypeDeliverWebhook, func(ctx context.Context, t *asynq.Task) error {
		p, err := jobs.Decode[jobs.WebhookPayload](t)
		if err != nil {
			return err
		}
		return webhooks.Deliver(ctx, deliveries, sender, p.DeliveryID)
	})
	mux.HandleFunc(jobs.TypeProcessPhoto, func(ctx context.Context, t *asynq.Task) error {
		p, err := jobs.Decode[jobs.PhotoPayload](t)
		if err != nil {
			return err
		}
		select {
		case photoSlot <- struct{}{}:
			defer func() { <-photoSlot }()
		case <-ctx.Done():
			return ctx.Err()
		}
		return menu.ProcessPhoto(ctx, menuStore, photos, p.DishID, p.FileName)
	})
	// ... TypeAskForReview, and the maintenance jobs from step 5

	srv := asynq.NewServer(redisOpt, asynq.Config{
		Concurrency:     10,
		Queues:          map[string]int{"emails": 4, "webhooks": 4, "photos": 1, "maintenance": 1},
		RetryDelayFunc:  retryDelay,
		ShutdownTimeout: 25 * time.Second,
		ErrorHandler: asynq.ErrorHandlerFunc(func(ctx context.Context, t *asynq.Task, err error) {
			retried, _ := asynq.GetRetryCount(ctx)
			max, _ := asynq.GetMaxRetry(ctx)
			logger.Error("job failed", "type", t.Type(), "attempt", retried+1,
				"for_good", retried >= max || errors.Is(err, asynq.SkipRetry), "error", err)
		}),
	})

	logger.Info("Mama Put worker started")
	return srv.Run(mux)
}

func retryDelay(n int, err error, t *asynq.Task) time.Duration {
	if t.Type() == jobs.TypeDeliverWebhook {
		return webhooks.Backoff(n + 1) // lesson 17's: 30 s doubling to 6 h, with jitter
	}
	return asynq.DefaultRetryDelayFunc(n, err, t)
}
```

(Add `"errors"` to the imports; `menuStore` is built with the others.)

Read the config, because each line is a decision:

1. **`Concurrency: 10`**: this worker runs up to ten jobs at once, each in its own goroutine. Emails and webhooks mostly *wait* on the network, so ten at once costs almost nothing.
2. **`Queues` with weights**: out of every 10 jobs taken, about 4 are emails, 4 webhooks, 1 photo, 1 maintenance, when all four queues have work waiting. An empty queue's share goes to the others. That's how a pile of photos can't starve Ada's receipt.
3. **`photoSlot`, a channel with room for one.** asynq's concurrency is for the whole worker, not per queue. Photos are CPU work, and two at once on a small server just take twice as long each. So the photo handler must put a token into `photoSlot` before it starts, and takes it out when it's done. A second photo job waits at the `select` until the first finishes, or gives up if its context is cancelled. A buffered channel used this way is called a **semaphore**, and it's the standard Go way to say "at most N at once".
4. **`RetryDelayFunc`**: how long to wait before each retry. Webhooks use lesson 17's backoff, now exported from `webhooks` as `Backoff`. Everything else gets asynq's default, which grows quickly from seconds to minutes, with jitter.
5. **`ErrorHandler`** runs after every failed attempt, not just the last. `GetRetryCount` and `GetMaxRetry` tell you which it was. "Failed for good" is the one a person needs to see; lesson 27 sends it to an alert.
6. **`srv.Run(mux)`** blocks until the worker is told to stop. Step 6 is what happens then.

The `Makefile` gets one more target, and you run it in a second terminal next to `make run`:

```makefile
worker:
	go run ./cmd/worker
```

```bash
make worker
```

## Step 4: using the jobs
<!-- bite: c7545ad4-de9e-4ddc-9bc0-5aaa3b83b11e -->

**Receipts.** In the payments service's `Settle`, from lesson 17:

```go
outcome, err := s.store.MarkSucceeded(ctx, reference)
if err != nil {
	return "", err
}
if outcome == Paid {
	if err := s.receipts.SendReceipt(ctx, p.ID); err != nil {
		s.log.Error("could not queue receipt", "payment", p.ID, "error", err) // the sweeper will catch it
	}
}
```

(`Service` gains a `receipts Receipts` field, passed in to `NewService`.) Only on `Paid`: the one call that actually changed the payment. Repeats of the webhook get `AlreadySettled` and queue nothing.

Notice a failure to queue is **logged, not returned**. The payment *is* settled; that's what the webhook was about. If we returned an error, Paystack would retry, `Settle` would find it already settled, and we still wouldn't queue the receipt. Step 7's sweeper is what catches it.

**Webhooks.** `Deliveries.Enqueue` now returns the new row's ID, and the orders adapter from lesson 17 queues the job right after writing the row:

```go
id, err := deliveries.Enqueue(ctx, okadaURL, "order.ready", payload)
if err != nil {
	return err
}
return jobClient.DeliverWebhook(ctx, id)
```

Delete lesson 17's `Sender.Run`, `RunOnce`, `ClaimDue` and the `go sender.Run(...)` line in `run`. asynq now does the timing and the retries, and makes sure two workers never take the same job. `webhook_deliveries` stays as our **record** of every webhook: what was sent, when it was delivered, the last error. An admin's "retry" button just calls `DeliverWebhook(ctx, id)` again.

When a webhook fails for good, `Deliver` can't know it was the last try, but the error handler can. In the worker's `ErrorHandler`, for a `webhook:deliver` that failed for good, set `gave_up_at` on the row, so the sweeper in step 7 leaves it alone.

**Photos.** In lesson 14's upload handler, after `SetPhoto`:

```go
if err := h.jobs.ProcessPhoto(r.Context(), id, name); err != nil {
	httpx.LoggerFrom(r.Context()).Error("could not queue photo", "error", err) // the original still shows
}
```

and the work, in `internal/menu/process.go`:

```go
// ProcessPhoto writes a large and a thumbnail JPEG for one uploaded photo.
func ProcessPhoto(ctx context.Context, store Store, photos *Photos, dishID int64, fileName string) error {
	f, err := photos.root.Open(fileName)
	if errors.Is(err, fs.ErrNotExist) {
		return fmt.Errorf("photo %s is gone: %w", fileName, asynq.SkipRetry)
	}
	if err != nil {
		return err
	}
	img, _, err := image.Decode(f)
	f.Close()
	if err != nil {
		return fmt.Errorf("can't decode %s: %v: %w", fileName, err, asynq.SkipRetry)
	}

	base := strings.TrimSuffix(fileName, path.Ext(fileName))
	large, thumb := base+"-large.jpg", base+"-thumb.jpg"
	if err := photos.writeJPEG(large, fit(img, 1200), 82); err != nil {
		return err
	}
	if err := photos.writeJPEG(thumb, square(img, 400), 75); err != nil {
		return err
	}
	return store.SetProcessedPhoto(ctx, dishID, fileName, large, thumb)
}
```

`fit` scales an image down so its longest side is at most `n` pixels, and `square` crops the middle and scales it to `n` by `n`. Both use `golang.org/x/image/draw`:

```go
func fit(src image.Image, n int) image.Image {
	b := src.Bounds()
	w, h := b.Dx(), b.Dy()
	if w <= n && h <= n {
		return src
	}
	if w >= h {
		w, h = n, h*n/w
	} else {
		w, h = w*n/h, n
	}
	dst := image.NewRGBA(image.Rect(0, 0, w, h))
	draw.CatmullRom.Scale(dst, dst.Bounds(), src, b, draw.Over, nil)
	return dst
}
```

(`square` is the same with a crop first; write it in the practice. `writeJPEG` creates the file through the `os.Root` from lesson 14 and calls `jpeg.Encode` with the quality given.)

Three things are going on:

1. **Re-encoding.** `image.Decode` turns the file into plain pixels, and `jpeg.Encode` writes a brand-new file from them. Anything hidden in the original (lesson 14's worry) doesn't survive that, and neither does the metadata, including the GPS location phones put in photos: Go's encoder writes none. (Go's decoder also ignores the phone's "this photo is sideways" note, so some phone photos come out on their side. Reading that note needs a small EXIF library; it's a practice item.)
2. **`asynq.SkipRetry` for hopeless failures.** A file that won't decode will never decode, and a file that's gone won't come back. Fail now, no retries.
3. **`SetProcessedPhoto(ctx, dishID, fileName, large, thumb)` checks the file name.** Its SQL is `UPDATE dishes SET photo_large = $3, photo_thumb = $4 WHERE id = $1 AND photo = $2`. If the cook uploaded a *newer* photo while this job was running, the old job's result doesn't overwrite it. Jobs run late, and late work must not undo newer work.

Until the job finishes, the menu shows the original photo; after, v2's presenter adds `photoLargeUrl` and `thumbnailUrl`. Ada never waits for any of it.

## Step 5: later, and on a timetable
<!-- bite: 7ff88ade-26be-4338-92ff-67c45553003f -->

**Delayed jobs.** Some work should happen *later*. Mama wants a "how was your food?" email an hour after an order is collected. That's `AskForReview` from step 2, with `asynq.ProcessIn(time.Hour)`: the job waits in Redis as **scheduled** and becomes ready after an hour. A restart of our API doesn't lose it, because it isn't in our API at all. Call it from `SetStatus` when an order becomes `collected`.

**Scheduled jobs.** Lesson 17's safety net, once an hour: check every payment still `started` after 15 minutes. And lesson 15's cleanup, once a night. asynq's **scheduler** adds a job each time a cron pattern comes round. In `cmd/worker`'s `run`, before `srv.Run`:

```go
lagos, err := time.LoadLocation("Africa/Lagos")
if err != nil {
	return err
}
scheduler := asynq.NewScheduler(redisOpt, &asynq.SchedulerOpts{Location: lagos})

every := []struct {
	cron string
	typ  string
	once time.Duration
}{
	{"5 * * * *", jobs.TypeCheckUnsettled, 50 * time.Minute},  // 5 past every hour
	{"*/10 * * * *", jobs.TypeSweepLostJobs, 9 * time.Minute}, // every 10 minutes
	{"30 3 * * *", jobs.TypeCleanUp, 23 * time.Hour},          // 3:30 every morning
}
for _, e := range every {
	_, err := scheduler.Register(e.cron, asynq.NewTask(e.typ, nil),
		asynq.Queue("maintenance"), asynq.Unique(e.once), asynq.MaxRetry(2))
	if err != nil {
		return fmt.Errorf("schedule %s: %w", e.typ, err)
	}
}
if getenv("RUN_SCHEDULER") == "true" {
	if err := scheduler.Start(); err != nil {
		return err
	}
	defer scheduler.Shutdown()
}
```

The **cron** pattern is five fields: minute, hour, day of the month, month, day of the week. `5 * * * *` means "minute 5, every hour, every day". `30 3 * * *` is "3:30 every morning", in Lagos time because of `Location`. `*/10` means "every 10th minute".

**Many workers, one timetable.** Each scheduler adds its jobs on its own. Run five worker processes, each with a scheduler, and five copies of "check unsettled payments" go in at 5 past the hour. Three layers stop that being a problem:

1. **Only one process runs the scheduler.** The worker starts it only when `RUN_SCHEDULER=true`, and you set that on exactly one worker. The others just run jobs. (The scheduler is tiny; if its process is down for a while, the jobs simply start late, and the sweeper catches up on anything that matters.)
2. **`asynq.Unique(e.once)` as a backstop**, for the minutes during a deploy when an old and a new scheduler both run. It makes asynq refuse a task identical (same type, same payload, same queue) to one already queued, with `ErrDuplicateTask`. But read the small print: the lock is let go as soon as the first task **finishes**, so a quick job that's already done doesn't block a late copy. `Unique` stops duplicates that pile up; it doesn't promise "once".
3. **Every scheduled job is safe to run twice.** Checking unsettled payments ends in `Settle`; the sweeper's re-queues are deduped by `TaskID`; deleting old rows twice deletes nothing the second time. That's the real guarantee, as it was for webhooks in lesson 17.

(The Express subject's BullMQ has a "job scheduler" that stores one schedule in Redis however many workers ask for it. asynq leaves that to you. Every queue library handles this differently; always check what yours actually promises.)

The maintenance handlers are plain functions too:

```go
// CheckUnsettled asks Paystack about payments that have been "started" for a while.
func (s *Service) CheckUnsettled(ctx context.Context) (int, error) {
	stuck, err := s.store.StartedBetween(ctx, 15*time.Minute, 24*time.Hour)
	if err != nil {
		return 0, err
	}
	for _, p := range stuck {
		seen, err := s.provider.Verify(ctx, p.Reference)
		if err != nil {
			return 0, err // the whole job retries; payments already settled are skipped next time
		}
		if _, err := s.Settle(ctx, p.Reference, seen); err != nil {
			return 0, err
		}
	}
	return len(stuck), nil
}
```

Every payment goes through the same `Settle` as the webhook and the verify route. That's three doors into one room, and the room is safe to enter twice.

`TypeCleanUp` runs three `DELETE`s: idempotency keys older than a day (lesson 15), received webhook events older than 30 days, and delivered webhooks older than 90. Each `DELETE` takes `LIMIT`-sized bites (`DELETE FROM ... WHERE ctid IN (SELECT ctid FROM ... LIMIT 5000)`, in a loop until nothing's deleted), so one huge delete never locks a busy table for minutes.

## Step 6: stopping workers politely
<!-- bite: a1572893-608c-4951-9028-4000f77bf2a2 -->

When you deploy a new version, the old worker gets a signal to stop (`SIGTERM`, or `SIGINT` when you press Ctrl+C). If it just died, the photo it was halfway through would be lost work, and a webhook halfway through might be sent twice.

`srv.Run` handles this for you. When the signal comes, asynq:

1. Stops taking new jobs.
2. Waits for running jobs to finish, for up to `ShutdownTimeout` (25 seconds in our config).
3. If some are still running after that, **cancels their contexts**, and puts those jobs back in the queue so another worker runs them again.
4. Returns from `Run`, so `run` returns, and every `defer` runs: the scheduler stops, and the database pool closes.

Point 3 is why every job handler must **respect its context**: pass `ctx` to every query and every HTTP call, and the job stops promptly when asked. The photo handler's `select` on `ctx.Done()` is the same idea, for a job waiting on the semaphore. A handler that ignores `ctx` can't be stopped, only killed.

Press Ctrl+C on `make worker` while a photo is processing, and watch it finish first.

This is also why jobs must be fairly short. A job that takes 20 minutes can't finish politely in the 25 seconds a deploy gives it. Split long work into many small jobs. Lesson 28 does the same for the web server.

## Step 7: the gap between Postgres and Redis
<!-- bite: 31265502-8f94-4357-b900-20b054934ccd -->

Look at the receipts code again:

```go
outcome, err := s.store.MarkSucceeded(ctx, reference) // Postgres
// ...
s.receipts.SendReceipt(ctx, p.ID)                      // Redis
```

Two different databases. If our app crashes between those two lines, or Redis is down for a moment, the payment is marked paid and the receipt job never exists. Nothing will ever send it. And there's no transaction that covers both Postgres and Redis.

The fix is to let **Postgres** be the truth, and check it now and then. Everything a job is about is already written down in Postgres: a paid payment with no `receipt_sent_at`, a webhook delivery with no `delivered_at`. So every 10 minutes, the sweeper looks for those and queues them again:

```go
func SweepLostJobs(ctx context.Context, payments LostReceipts, deliveries LostWebhooks, q Queue) error {
	ids, err := payments.PaidWithoutReceipt(ctx, 10*time.Minute)
	if err != nil {
		return err
	}
	for _, id := range ids {
		if err := q.SendReceipt(ctx, id); err != nil {
			return err
		}
	}
	hooks, err := deliveries.Undelivered(ctx, 10*time.Minute) // not delivered, not given up
	if err != nil {
		return err
	}
	for _, id := range hooks {
		if err := q.DeliverWebhook(ctx, id); err != nil {
			return err
		}
	}
	return nil
}
```

This is safe because of the `TaskID`s from step 2. If the job does exist (it's just waiting for its next retry), adding it again gets `ErrTaskIDConflict`, which `add` treats as success, and nothing happens. If it was really lost, now it exists. The "older than 10 minutes" stops the sweeper racing with work that was queued a second ago and is about to run. And `Undelivered` leaves out deliveries with a `gave_up_at`, so the sweeper doesn't bring the hopeless ones back to life every 10 minutes.

One detail about `TaskID`: asynq only remembers an ID while the job is in the queue (waiting, scheduled, retrying or archived). Once it **completes**, the ID is free again. That's exactly what we want for the sweeper (a finished receipt is never found by `PaidWithoutReceipt`, so it's never queued again), but it means the `TaskID` alone isn't a promise that work happens only once. The `ReceiptSentAt` check inside `SendReceipt` is.

There's a neater way to close this gap, where the job is written into Postgres *in the same transaction* as the change, and a relay moves it to the queue. That's the **outbox** in lesson 25. The sweeper is the simpler cousin, and for receipts it's enough.

## Step 8: watching the queues
<!-- bite: 02bfff40-a521-4edf-83d8-12908628e9c1 -->

You'll want to know: how many jobs are waiting? Which failed, and why? A queue that's quietly growing is a problem you want to see on Tuesday, not discover on Friday.

1. **The command line.** asynq's tool, added in "What to install":

   ```bash
   go tool asynq --uri redis://localhost:6379/0 stats
   go tool asynq --uri redis://localhost:6379/0 task ls --queue emails --state archived
   ```

   The first shows every queue's waiting, running, scheduled, retrying and archived counts; the second lists the jobs that failed for good, with their last error.

2. **An admin route.** `asynq.NewInspector(redisOpt)` reads the same numbers from Go. `GET /v2/admin/queues`, behind a new `admin:read-queues` action, returns each queue's sizes from `inspector.GetQueueInfo(name)`. Lesson 27 turns them into graphs and alerts.

3. **A dashboard.** **Asynqmon** is a ready-made web page that lists every queue and job, shows the errors, and has a "retry" button. It's very useful, and it shows job payloads and errors, so it must only ever be reachable by admins, never on the open internet. (That's one more reason job data holds IDs, not personal details.)

## Step 9: testing jobs
<!-- bite: d05b3b78-9180-484a-b11d-3a845e081f2f -->

**The work is plain functions**, so it's tested like services, with no Redis at all:

```go
func TestSendReceiptOnce(t *testing.T) {
	store := &fakeReceipts{details: ReceiptDetails{PaymentID: 17, OrderID: 42,
		Email: "ada@test.example", Name: "Ada", Amount: 300000}}
	mail := &recordingMailer{}

	first, err := SendReceipt(t.Context(), store, mail, 17)
	if err != nil || first != "sent" {
		t.Fatalf("first: %q, %v", first, err)
	}
	second, err := SendReceipt(t.Context(), store, mail, 17)
	if err != nil || second != "skipped" {
		t.Fatalf("second: %q, %v", second, err)
	}
	if len(mail.sent) != 1 || mail.sent[0] != "ada@test.example" {
		t.Errorf("sent %v, want exactly one, to Ada", mail.sent)
	}
}
```

(`fakeReceipts.MarkReceiptSent` sets `details.ReceiptSentAt`, as the real store does.)

**HTTP tests use a fake queue** that records what was asked. In `apptest`:

```go
type RecordingJobs struct {
	mu       sync.Mutex
	Receipts []int64
	Webhooks []string
	Photos   []string
}

func (j *RecordingJobs) SendReceipt(_ context.Context, id int64) error {
	j.mu.Lock()
	defer j.mu.Unlock()
	j.Receipts = append(j.Receipts, id)
	return nil
}

// DeliverWebhook and ProcessPhoto the same way.
```

Then a test can check "a signed `charge.success` webhook queues exactly one receipt, and sending it three times still queues one". (The fake records every call; asynq's `TaskID` is what dedupes in real life. So the test checks the more important thing: that only the call that really settled the payment asked at all.)

**An integration test with real Redis** checks the wiring once: start an `asynq.Server` on a test Redis database, add a job whose handler fails twice and then succeeds, and check it ran three times. Point it at a separate Redis database number (`redis://localhost:6379/15`), and empty it before each test with `FLUSHDB`, the same care as lesson 16's `_test` Postgres database. Put it behind the `integration` build tag, and use a `RetryDelayFunc` that returns a few milliseconds, so the test doesn't wait for real backoff.

## The Go in this lesson
<!-- bite: d975584e-e62f-48e7-9184-d7368e8b93c1 -->

1. **A second `main` package**, `cmd/worker`: One module can build many programs. Each folder under `cmd/` with `package main` is one, sharing everything in `internal/`.
2. **`asynq.NewTask(type, payload)`** and **`client.EnqueueContext(ctx, task, opts...)`**: A job is a type name and some bytes; options like `asynq.Queue`, `asynq.TaskID`, `asynq.MaxRetry`, `asynq.ProcessIn` and `asynq.Unique` are functional options, as in lesson 12.
3. **`errors.Is(err, asynq.ErrTaskIDConflict)`**: A sentinel error from a library, checked like our own.
4. **`fmt.Errorf("...: %w", asynq.SkipRetry)`**: Wrapping a library's sentinel so the library can recognise it in your error. Errors as values, carrying a message back to whoever runs your code.
5. **`func Decode[T any](t *asynq.Task) (T, error)`**: A generic helper, like lesson 6's, for job payloads.
6. **`asynq.NewServeMux()`** and **`mux.HandleFunc(type, func(ctx, *asynq.Task) error)`**: The same shape as `net/http`'s mux, for jobs: a type name instead of a path, an error instead of a response.
7. **`make(chan struct{}, 1)` as a semaphore**: Sending puts a token in; when it's full, the next sender waits. `struct{}` takes no memory; the channel only counts.
8. **`select` with `ctx.Done()`**: Wait for a token *or* for cancellation, whichever comes first, so waiting never outlives the job.
9. **`defer func() { <-photoSlot }()`**: Takes the token back out when the handler returns, however it returns.
10. **`image.Decode`**, **`image.NewRGBA`** and **`jpeg.Encode`**: Decode any registered format into pixels, make a new blank image, write pixels as a JPEG. `b.Dx()` and `b.Dy()` are a rectangle's width and height.
11. **`draw.CatmullRom.Scale(dst, dst.Bounds(), src, src.Bounds(), draw.Over, nil)`**: A high-quality scaler from `golang.org/x/image/draw`. `CatmullRom` is the slowest and best of its scalers; `ApproxBiLinear` is faster.
12. **`strings.TrimSuffix(name, path.Ext(name))`**: `path.Ext` gives `.jpg`; `TrimSuffix` takes it off the end.
13. **An anonymous struct slice for a table**, `[]struct{ cron, typ string; once time.Duration }`: The table-test shape, used in real code to keep a list of similar things readable.
14. **`asynq.ErrorHandlerFunc(func(...))`**: A function type with a method, so a plain function satisfies an interface. It's `http.HandlerFunc` from lesson 1, in another library.

## Your project so far
<!-- bite: d199d064-462a-491b-bf27-6636578008e2 -->

```text
mama-put/
├── .env                           ← REDIS_URL; RUN_SCHEDULER=true on one worker only
├── Makefile                       ← worker target
├── go.mod                         ← hibiken/asynq; x/image; asynq CLI as a tool
├── migrations/
│   └── 013_job_bookkeeping.sql    ← NEW: receipt_sent_at, photo_large/photo_thumb, gave_up_at
├── cmd/
│   ├── api/main.go                ← builds jobs.Client; the sender goroutine is gone
│   └── worker/main.go             ← NEW: the worker: handlers, queues and weights, retries, scheduler
└── internal/
    ├── jobs/                      ← NEW: the one door into asynq
    │   ├── jobs.go                ← types, payloads, Client (TaskIDs, queues, retries, delays)
    │   └── handlers.go            ← Decode[T] (bad payloads skip retries)
    ├── payments/
    │   ├── service.go             ← Settle queues a receipt on Paid; CheckUnsettled
    │   ├── receipts.go            ← NEW: SendReceipt (send, then mark), Mailer, LogMailer
    │   └── postgres.go            ← ReceiptDetails, MarkReceiptSent, StartedBetween, PaidWithoutReceipt
    ├── menu/
    │   ├── process.go             ← NEW: ProcessPhoto, fit, square, writeJPEG
    │   ├── handlers.go            ← upload queues the photo job
    │   └── postgres.go            ← SetProcessedPhoto (only if the photo hasn't changed)
    ├── webhooks/
    │   ├── deliver.go             ← NEW: Deliver, one delivery, for the job
    │   ├── sender.go              ← send and Backoff stay; Run, RunOnce and ClaimDue are gone
    │   └── deliveries.go          ← Enqueue returns the ID; Undelivered; MarkGaveUp
    ├── maintenance/
    │   └── maintenance.go         ← NEW: SweepLostJobs, CleanUp in small bites
    └── apptest/
        └── jobs.go                ← NEW: RecordingJobs
```

## Common mistakes
<!-- bite: 53a65bba-70ae-4cb2-a450-fe044b577a72 -->

1. **Putting objects in job payloads.** They go stale, they leak personal data into Redis and logs, and they fill memory. Send IDs, read fresh data in the worker.
2. **No `TaskID`.** Then every repeat of the trigger adds another job. Name the work.
3. **Retrying hopeless jobs.** A file that won't decode won't decode on try five. Wrap `asynq.SkipRetry`.
4. **Catching an error in a handler and returning `nil`.** asynq thinks the job worked, and never retries it. Return the error.
5. **Not asking "what if it runs twice?"** Every job runs at least once, and sometimes twice. Decide which way to be wrong, on purpose.
6. **A scheduler in every worker.** Five workers, five runs an hour. Run it in one, and make the jobs safe to repeat anyway.
7. **Trusting Redis to remember everything.** A job can be lost between Postgres and Redis. Keep the truth in Postgres, and sweep.
8. **Ignoring `ctx` in handlers.** Then a deploy can't stop them, only kill them.
9. **Long jobs.** They can't finish in a shutdown. Split them.
10. **Redis set to evict keys.** Queues silently lose jobs. Use `noeviction` for the queue's Redis.
11. **A queue dashboard on the open internet.** It shows payloads and errors. Admins only.
12. **Huge `DELETE`s in cleanup jobs.** They lock busy tables. Delete in bites.

## Check your understanding
<!-- bite: 6434cba7-2804-4f26-b551-a7475935c76f -->

1. Which of these should be a job: sending the receipt; taking the portions; telling Okada Riders an order is ready; checking the Idempotency-Key? Why?
2. The receipt job sends the email, then the worker crashes before marking it sent. What happens next, and why was that the better way to be wrong?
3. Why does `SendReceipt` check `ReceiptSentAt`, when the job already has a `TaskID`?
4. You run three workers. How many times does the hourly payment check run, and what makes that safe?
5. Redis is down for ten seconds just as Ada's payment settles. Follow her receipt: how does it still get sent?
6. Why does the photo handler use a channel when asynq already has a `Concurrency` setting?

<details>
<summary>Answers, after your attempt</summary>

1. The receipt and the Okada Riders message are jobs: Ada doesn't need them in her answer, and both talk to services that can be slow or down. Taking the portions and checking the key are not: the answer depends on them, and if they fail, the request must fail.
2. asynq sees the job was never finished and runs it again; `ReceiptSentAt` is still empty, so Ada gets a second receipt. The other order (mark, then send) would risk her getting none. For a receipt, a duplicate is a small annoyance; a missing one is a customer with no proof of payment.
3. Because asynq only remembers a `TaskID` while the job is in the queue. Once it completes, the same ID can be added again (the sweeper, an admin's retry button). And a job can run twice after a crash. The `TaskID` stops most repeats; the check in the work itself is what guarantees it.
4. Normally once, because only the worker with `RUN_SCHEDULER=true` adds it. During a deploy, an old and a new scheduler might both add it; `Unique` refuses the second while the first is still queued or running, and if a copy slips through anyway, the check ends in `Settle`, which is safe to run twice. The promise comes from the job being safe to repeat, not from the queue.
5. `MarkSucceeded` works (Postgres is fine), and `SendReceipt` fails to queue (Redis is down). The failure is logged and the webhook still gets its 200. Within 10 minutes, the sweeper finds a paid payment with no `receipt_sent_at`, older than 10 minutes, and queues it. Redis is back by then, and the worker sends it.
6. Because asynq's concurrency is for the whole worker, across every queue. Ten email jobs at once is fine; ten photos at once would fight over the CPU. The channel limits photos alone to one at a time, while emails and webhooks keep using the other slots.

</details>

## Practice
<!-- bite: 4cea7c7d-ae5a-4057-9d96-37c53ad9ca0b -->

1. Write `square(img, n)`: crop the largest centred square from the image, then scale it to `n` by `n`. Test it with an `image.NewRGBA` of 800 by 600, and check the result is 400 by 400.
2. Write `TypeCleanUp`'s three bite-sized `DELETE`s, and an integration test that inserts 12,000 old idempotency keys and checks they're all gone after one run.
3. Make the worker's error handler set `gave_up_at` when a `webhook:deliver` job fails for good, and write `Undelivered` so the sweeper skips those.
4. Add `GET /v2/admin/queues` with `asynq.NewInspector`, behind a new `admin:read-queues` action (and a `TestPermissions` row).
5. Read the EXIF orientation of uploaded JPEGs (a small library such as `github.com/rwcarlsen/goexif` can), and rotate the pixels before writing the large and thumbnail copies.

**Done when** paying for an order logs a receipt email from the worker (not the API); marking an order ready delivers the Okada webhook through a job, with lesson 17's signature; an uploaded photo gets large and thumbnail copies within seconds; `go tool asynq stats` shows the four queues; stopping Redis for a minute and starting it again still ends with every receipt sent; and `make test` passes.

## Before moving on
<!-- bite: 972bba99-269e-4dfd-b0a7-0b275cba9ace -->

Mama Put API now does slow work in the background. The API just writes a note; a separate worker sends receipts, delivers webhooks, processes photos, checks unsettled payments every hour and cleans up every night, with retries, priorities, and schedules that are safe however many workers there are. And Postgres stays the truth: anything Redis loses, the sweeper finds.

With Redis in the house, a different question comes up. Every phone that opens the app asks for the menu. Every time, we ask Postgres, which reads the same forty dishes and builds the same JSON. Lunchtime means thousands of identical answers, worked out from scratch. That's caching, the next lesson.

## Related
<!-- bite: 99d8085e-ebb0-40ee-b923-2623a420de8b -->

- [[backend/frameworks/net-http/19-caching|Next: Caching with Redis]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — why "at least once" needs work that's safe twice
- [[backend/frameworks/express/18-background-jobs|The same lesson in Express]] — BullMQ and job schedulers
- [[backend/frameworks/net-http/17-payments-and-webhooks|Payments and Webhooks]] — the hand-made queue this replaces

## About this lesson
<!-- bite: 9f5eff77-99c7-48a6-820e-d75cc1a8c925 -->

**Level:** Advanced. Lesson 18 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, asynq and Redis 7, with `golang.org/x/image/draw`. Covers what belongs in a job, Redis settings for a queue, one package as the door into asynq with task IDs and small payloads, a worker program with weighted queues, a semaphore for CPU work, per-type retry delays and `SkipRetry`, delayed and scheduled jobs (one scheduler, `Unique` as a backstop, jobs safe to repeat), graceful shutdown and context, a sweeper for the Postgres-to-Redis gap, watching queues, and testing jobs as plain functions.
