---
id: 0de9b60a-62c5-4d12-add1-e236f4069eda
---

# Splitting Out a Microservice

**A microservice is a small program that does one job for the system, owns its own data, and talks to the other programs only through messages and APIs, never by reaching into their code or their database. Splitting one out means moving a job out of the main program into a service of its own, so its failures and its changes stay its own.** The hard part isn't writing the second program. It's making sure the two can never silently disagree about what happened.

## Before you start
<!-- bite: 8049de46-0807-4284-9504-e4d474f77d48 -->

You should have the whole of Parts 1 to 5, up to [[backend/frameworks/net-http/24-mcp-in-production|lesson 24]]. This lesson leans hardest on lesson 17 (`Settle` and its guarded transaction), lesson 18 (jobs that are safe to run twice), and lesson 22 (the gRPC contract), and it closes a gap each of them admitted.

After this lesson you will be able to:

1. Decide honestly whether something should be its own service, and pick a good first candidate.
2. Lay out several programs in one Go module, and *prove* with a test that one doesn't import the other.
3. Give each service its own database, and design events as a versioned contract.
4. Use the outbox pattern so "the order is paid" and "tell everyone it's paid" can never come apart.
5. Publish events to NATS JetStream, and consume them with a durable consumer: acks, retries with backoff, and messages that can never succeed.
6. Build the notifications service, which reacts to events and asks the API for what it needs over gRPC.

## What to install
<!-- bite: 17d48ef7-0890-454a-a667-9606c8bd5eb0 -->

**NATS**, the message server, run in Docker like Postgres and Redis:

```bash
docker run -d --name mamaput-nats -p 4222:4222 -p 8222:8222 nats:2-alpine -js -m 8222
```

1. **`-js`** switches on **JetStream**, NATS's storage layer: without it, NATS passes messages on and forgets them; with it, messages are kept in streams until every consumer has handled them.
2. **`-m 8222`** opens a small monitoring page at `http://localhost:8222`, handy for seeing streams and consumers.

Lesson 28 moves it into Docker Compose with everything else.

And the Go client, in the `mama-put` folder:

```bash
go get github.com/nats-io/nats.go@latest
```

It includes the `jetstream` package we'll use. Optionally, the **`nats` command-line tool** lets you look inside streams by hand. It's a Go program, so it installs like grpcurl did in lesson 22:

```bash
go install github.com/nats-io/natscli/nats@latest
```

## Where we stopped
<!-- bite: 758a3df5-412d-45ed-8099-0ee6ebe7b619 -->

Look at everything the API's worker does to talk to customers:

1. Receipt emails (lesson 18), through an email provider, with its own API key.
2. "How was your food?" emails, delayed an hour.
3. Soon: a text message when the order is ready, through an SMS provider, with another key.

And look at what happened last Tuesday (pretend). The SMS provider was slow for an hour. The worker's `emails` queue filled up, retries piled on, the worker used all its CPU, and lesson 17's partner webhooks to Okada Riders, in the same worker, ran late. One provider's bad hour reached our delivery partner.

Also, Mama has hired someone to look after customer messages: wording, templates, which messages to send when. Every small change to a template means deploying the *whole* API, payments and all.

Those are the two real reasons to split something out: **one part's failures shouldn't reach the rest**, and **one part should change on its own schedule**. Notifications has both.

## The kid version
<!-- bite: 31dba463-bbd2-457d-b78e-1f5cc30bab93 -->

When Mama Put was small, Mama took orders, cooked, collected money and shouted "Bayo, your food is ready!", all herself.

Now it's busy. She hires a boy just for calling names and sending texts. He has his own corner, his own phone, his own notebook. Mama doesn't tell him how to send a text; she just writes "order 42 is ready" on a slate by the door. Anyone whose job involves ready orders reads the slate. The boy reads it, looks up who ordered 42, and texts them.

If the boy's phone runs out of credit, Mama keeps cooking. The orders don't stop. The texts are late, and that's all.

The slate is the **event stream**. The boy is the notifications service. "Mama doesn't care who reads the slate" is the point.

**Where the picture stops working.** A slate gets wiped. Our stream keeps every message until each reader has said "done", so when the boy comes back from his break, everything written while he was away is still there, in order.

## Terms used in this lesson
<!-- bite: 91efc8f6-a443-4246-adc3-a3dd3b303795 -->

1. **Monolith**: This is one program that does everything. Not an insult: most good systems start as one, and many stay one.
2. **Service boundary**: This is the line around what a service owns: its job, its code, its data.
3. **Event**: This is a message saying something **already happened**, like `order.paid`. The sender doesn't know or care who's listening.
4. **Command**: This is a message asking someone to **do** something, like "send this email". A command has a target; an event doesn't.
5. **Outbox**: This is a table where a service writes the events it wants to publish, in the same database transaction as the change itself. A separate loop then publishes them.
6. **Stream**: This is an ordered log of messages that stay there after being read. In JetStream, a stream collects every message sent to the subjects it's listening to.
7. **Subject**: This is NATS's name for where a message is sent, like `orders.paid`. Subjects have parts separated by dots, and `orders.>` means "anything under `orders.`".
8. **Durable consumer**: This is a named reader of a stream that the server remembers. It keeps track of which messages its readers have finished, even when every reader is offline.
9. **Acknowledge (ack)**: This is a reader telling the server "I've finished this message", so it isn't given out again.
10. **Eventual consistency**: This means different services see a change at slightly different times. For a moment the API knows order 42 is paid and notifications doesn't yet. Soon they agree.

## Step 1: should you, really?
<!-- bite: 70a47cdd-4374-4961-8599-0c70ee4bb9ce -->

Microservices are fashionable, and many teams regret them. Be honest about the costs before paying them:

| You get | You pay |
|---|---|
| A failure in one service stays there | Every call between services can fail, be slow, or arrive twice |
| Each service deploys on its own | Changes that span services need careful ordering (versions, both shapes for a while) |
| Each service keeps its own secrets and data | Data is in several places; a "join" across services means network calls |
| Teams can own their service | Debugging means following one request through several programs (lesson 27) |
| Scale only the busy part | More to run, watch, secure and pay for |

The usual good advice is **"monolith first"**: build one well-structured program, with feature packages that only talk through interfaces (lessons 4 and 5), and split only when a real reason appears. Our packages already declare what they need from each other as small interfaces, so most of the cutting is done.

Mama Put, honestly, could stay one program for years. We're splitting notifications to learn how, and because it's the classic **good first candidate**:

1. It has clear edges: "something happened; tell the customer".
2. It doesn't need to answer anyone in a hurry. A receipt a minute late is fine.
3. It talks to unreliable outside providers, whose failures we want kept away from orders and payments.
4. Nothing else waits for it. Nobody's request fails because a text wasn't sent.

A **bad** first candidate would be "payments" or "menu": the API needs them in the middle of placing an order, so every order would become a network call that can fail.

## Step 2: the new layout
<!-- bite: 2120af0a-5ae2-4153-82c6-5dfe3ef99158 -->

In Node, a second service means a second project with its own `package.json`. In Go, the simplest good shape is **one module, several programs**: each `cmd/` folder is its own `main` package, built into its own binary, run as its own process, shipped in its own Docker image (lesson 28).

```text
mama-put/
├── go.mod                     ← one module, mamaput
├── proto/                     ← the gRPC contracts both services use
├── cmd/
│   ├── api/                   ← the API (since lesson 1)
│   ├── worker/                ← the API's background worker (lesson 18)
│   ├── migrate/               ← the API's migrations (lesson 8)
│   └── notifications/         ← NEW: the notifications service
└── internal/
    ├── contracts/events/      ← NEW: event names and shapes, shared
    ├── gen/                   ← generated gRPC code, shared
    ├── db/                    ← lesson 8's migration runner: knows nothing about dishes, shared
    ├── notifications/         ← NEW: everything the notifications service is
    └── app/ menu/ orders/ payments/ auth/ ...   ← the API, as before
```

One repository with several services is a **monorepo**. It keeps the shared contracts in one place, lets one pull request change both sides of a contract, and runs every test together (lesson 29). One module means one `go.mod` and one set of dependency versions, which for one small team is a gift.

(The alternative is one module per service, tied together with a `go.work` file for local development. It gives each service its own dependency versions, at the cost of more files and more ways for versions to drift. Teams usually move to it when different teams own different services.)

### Proving the boundary

Here's the catch with one module. Nothing *stops* `internal/notifications` from importing `mamaput/internal/orders`: it's all the same module, and Go's `internal/` rule only keeps code out of *other* modules. One quick import "just to reuse the `Order` type", and the two services are tied together again: change `orders`, and notifications changes too, without anyone noticing.

So we make the boundary a test. `internal/notifications/boundary_test.go`:

```go
package notifications

import (
	"os/exec"
	"strings"
	"testing"
)

// The notifications service may use the shared contracts, the generated gRPC code,
// the migration runner, and its own packages. Anything else from mamaput/ belongs to the API.
var allowed = []string{
	"mamaput/cmd/notifications",
	"mamaput/internal/notifications",
	"mamaput/internal/contracts/",
	"mamaput/internal/gen/",
	"mamaput/internal/db",
}

func TestNotificationsDoesNotImportTheAPI(t *testing.T) {
	out, err := exec.Command("go", "list", "-deps", "-f", "{{.ImportPath}}", "mamaput/cmd/notifications").Output()
	if err != nil {
		t.Fatalf("go list: %v", err)
	}
	for _, pkg := range strings.Fields(string(out)) {
		if !strings.HasPrefix(pkg, "mamaput/") {
			continue // the standard library and other modules
		}
		ok := false
		for _, prefix := range allowed {
			ok = ok || strings.HasPrefix(pkg, prefix)
		}
		if !ok {
			t.Errorf("the notifications service imports %s, which belongs to the API", pkg)
		}
	}
}
```

`go list -deps` prints every package a program needs, **including the ones it needs indirectly**. I tried it by adding one innocent import of `orders` to the notifications `main.go`:

```text
--- FAIL: TestNotificationsDoesNotImportTheAPI (0.03s)
    boundary_test.go:33: the notifications service imports mamaput/internal/apperr, which belongs to the API
    boundary_test.go:33: the notifications service imports mamaput/internal/money, which belongs to the API
    boundary_test.go:33: the notifications service imports mamaput/internal/orders, which belongs to the API
FAIL
```

One import of `orders` brought `apperr` and `money` along with it. The test sees all three, and lesson 29's pipeline will refuse to merge it. That's the one-way import rule from lesson 4, written down where the computer checks it.

### Who owns which data

The most important rule in this lesson: **a service's database is private.** The notifications service never reads the API's tables, and the API never reads notifications' tables. Everything goes through events or APIs.

Why so strict? Because a shared table is a hidden contract. If notifications reads `users.email` directly, then renaming that column in the API breaks notifications, with no warning, and the two services can never deploy separately again. You'd have a monolith with network problems.

So the notifications service gets its own database, on the same Postgres server for now, with its own user who can't even connect to the API's:

```sql
CREATE DATABASE mamaput_notifications;
CREATE USER notifications WITH PASSWORD 'change-me';
GRANT ALL ON DATABASE mamaput_notifications TO notifications;
REVOKE CONNECT ON DATABASE mamaput FROM PUBLIC;
GRANT CONNECT ON DATABASE mamaput TO mamaput;
```

(Postgres lets every user connect to every database unless you take that away from `PUBLIC`; the last two lines do. Lesson 28 puts these in a setup script.)

It owns:

1. **`sent_notifications`**: every message sent, so we never send the same one twice and support can see what a customer got.
2. **`preferences`**: whether each customer wants texts, emails or both. The API doesn't need to know.

It does **not** own customers' email addresses and phone numbers. Those belong to the API, which is where people edit them. When notifications needs them, it asks (step 6).

## Step 3: designing events
<!-- bite: fe763279-f425-4b14-a473-64ffca6b422b -->

An event says what happened, in the past tense, from the point of view of the service that owns the thing:

1. `order.placed`: a customer placed an order.
2. `order.paid`: an order's payment succeeded.
3. `order.ready`: the kitchen marked it ready.
4. `order.collected`: it was picked up.

Every event has the same **envelope**. `internal/contracts/events/events.go`:

```go
// Package events is the contract between Mama Put's services: every event's name and shape.
// It imports nothing from either service, and both import it.
package events

import (
	"encoding/json"
	"time"
)

// Envelope wraps every event.
type Envelope struct {
	ID         string          `json:"id"`         // unique per event; consumers use it to skip duplicates
	Type       string          `json:"type"`       // "order.paid"
	Version    int             `json:"version"`    // the version of THIS type's data shape
	OccurredAt time.Time       `json:"occurredAt"` // when it happened, not when it was sent
	Source     string          `json:"source"`     // "api"
	Data       json.RawMessage `json:"data"`
}

const (
	OrderPlaced    = "order.placed"
	OrderPaid      = "order.paid"
	OrderReady     = "order.ready"
	OrderCollected = "order.collected"
)

// Subject is where an event type is published in NATS: "order.paid" goes to "orders.paid".
func Subject(eventType string) string {
	return "orders." + eventType[len("order."):]
}

// OrderPaidV1 is the data of order.paid, version 1.
type OrderPaidV1 struct {
	OrderID    int64     `json:"orderId"`
	CustomerID *int64    `json:"customerId"` // null for v1's anonymous orders
	DishID     int64     `json:"dishId"`
	Quantity   int       `json:"quantity"`
	TotalKobo  int64     `json:"totalKobo"`
	PaidAt     time.Time `json:"paidAt"`
}

// OrderReadyV1 is the data of order.ready, version 1.
type OrderReadyV1 struct {
	OrderID    int64     `json:"orderId"`
	CustomerID *int64    `json:"customerId"` // null for v1's anonymous orders
	ReadyAt    time.Time `json:"readyAt"`
}
```

Both services import this one package, so each shape is written once.

1. **`Data json.RawMessage`** keeps the data as raw JSON bytes inside the envelope. A consumer reads the envelope first, looks at `Type` and `Version`, and only then decodes `Data` into the right struct. One envelope type carries every kind of event.
2. **Plain types only.** `TotalKobo int64`, not `money.Kobo`; `CustomerID *int64`, not `auth.Identity`. The contract package must import nothing from either service, or importing it would drag the API's packages into notifications, and step 2's test would fail.
3. **`CustomerID` is a pointer** because v1 still takes orders with no customer (lesson 12). An event states the facts, including "nobody".

**Versions, because lesson 10 promised.** Events are an API too: other services depend on their shape, and the same rules apply. Adding a field is safe: `encoding/json` ignores fields a struct doesn't have, so old consumers carry on. Removing or changing a field is breaking: publish `version: 2` *alongside* `version: 1` for a while, move every consumer to v2, then stop publishing v1.

**How much data should an event carry?** Two styles:

1. **Thin events**: just IDs. `{"orderId": 42}`. Consumers call back to get the rest. Always fresh, but every event causes a call.
2. **Fat events**: everything a consumer might want, including copies of data. No calls needed, but you're spreading copies of data everywhere, and they go stale.

Ours sit in between: the **facts of what happened** (who, what, how much, when), but not copies of data that lives elsewhere and changes on its own, like the customer's email address or the dish's name. Personal contact details especially don't belong in events: events are stored, replayed and read by every consumer, now and in the future.

## Step 4: the outbox
<!-- bite: ec928205-342c-434b-8246-16432bb9e3f8 -->

Here's the problem lessons 17, 18 and 20 kept pointing at. In `Settle`, we update Postgres, then tell other systems:

```go
outcome, err := s.store.MarkSucceeded(ctx, reference) // Postgres
// ...then queue the receipt (Redis), tell the kitchen (Redis)
```

Crash between the two, and the order is paid but nobody ever hears about it. Do it the other way round, and a crash means everyone hears about a payment that was never saved. There's no transaction that covers Postgres *and* Redis, or Postgres *and* NATS. Lesson 18's sweeper was a patch for exactly this gap.

The **outbox** closes it by writing the event to **Postgres**, in the **same transaction** as the change. `migrations/015_outbox.sql`:

```sql
CREATE TABLE outbox (
  id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  type          text        NOT NULL,
  version       integer     NOT NULL,
  data          jsonb       NOT NULL,
  occurred_at   timestamptz NOT NULL DEFAULT now(),
  published_at  timestamptz
);

CREATE INDEX outbox_unpublished_idx ON outbox (occurred_at) WHERE published_at IS NULL;
```

`internal/outbox/outbox.go`:

```go
// Package outbox records events in the same transaction as the change, and relays them to NATS.
package outbox

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go/jetstream"

	"mamaput/internal/contracts/events"
)

// Add writes an event into the outbox, inside the caller's transaction.
func Add(ctx context.Context, tx pgx.Tx, eventType string, version int, data any) error {
	b, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("outbox: encode %s: %w", eventType, err)
	}
	_, err = tx.Exec(ctx, "INSERT INTO outbox (type, version, data) VALUES ($1, $2, $3)", eventType, version, b)
	return err
}
```

`Add` takes a **`pgx.Tx`**, not the pool. That's the whole point, and the type system enforces it: you can't call `Add` without being inside a transaction.

In lesson 17's `MarkSucceeded`, inside the `pgx.BeginFunc` it already had, the order update now returns what the event needs, and the event goes in right after:

```go
var paid events.OrderPaidV1
err = tx.QueryRow(ctx, `
	UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL
	RETURNING id, customer_id, dish_id, quantity, total_kobo, paid_at`, orderID).
	Scan(&paid.OrderID, &paid.CustomerID, &paid.DishID, &paid.Quantity, &paid.TotalKobo, &paid.PaidAt)
if errors.Is(err, pgx.ErrNoRows) {
	outcome = OrderWasAlreadyPaid
	return nil
}
if err != nil {
	return err
}
outcome = Paid
return outbox.Add(ctx, tx, events.OrderPaid, 1, paid)
```

Now "the order is paid" and "there's an `order.paid` event to send" are committed together, or not at all. Postgres guarantees it. The same goes in the orders store's status change, for `order.ready` and `order.collected`, and in `PlaceTakingPortions` for `order.placed`. (`payments` now imports `outbox` and `contracts/events`. Both are small and know nothing about payments, so the one-way rule from lesson 4 still holds.)

### The relay

Something must move events from the outbox to NATS. That's the **relay**, a loop in the API's worker:

```go
// Relay moves events from the outbox to the ORDERS stream.
type Relay struct {
	Pool *pgxpool.Pool
	JS   jetstream.JetStream
	Log  *slog.Logger
}

// RunOnce publishes up to 100 waiting events, and says how many it published.
func (r *Relay) RunOnce(ctx context.Context) (int, error) {
	sent := 0
	err := pgx.BeginFunc(ctx, r.Pool, func(tx pgx.Tx) error {
		rows, err := tx.Query(ctx, `
			SELECT id, type, version, data, occurred_at FROM outbox
			 WHERE published_at IS NULL
			 ORDER BY occurred_at, id
			 LIMIT 100
			 FOR UPDATE SKIP LOCKED`)
		if err != nil {
			return err
		}
		batch, err := pgx.CollectRows(rows, func(row pgx.CollectableRow) (events.Envelope, error) {
			var e events.Envelope
			err := row.Scan(&e.ID, &e.Type, &e.Version, &e.Data, &e.OccurredAt)
			e.Source = "api"
			return e, err
		})
		if err != nil {
			return err
		}
		for _, e := range batch {
			b, err := json.Marshal(e)
			if err != nil {
				return err
			}
			// WithMsgID: if we publish this event again (a crash before COMMIT), JetStream drops the copy.
			if _, err := r.JS.Publish(ctx, events.Subject(e.Type), b, jetstream.WithMsgID(e.ID)); err != nil {
				return fmt.Errorf("publish %s: %w", e.ID, err)
			}
			if _, err := tx.Exec(ctx, "UPDATE outbox SET published_at = now() WHERE id = $1", e.ID); err != nil {
				return err
			}
			sent++
		}
		return nil
	})
	return sent, err
}

// Run loops until ctx ends: straight on while there's a backlog, resting when there's nothing to send.
func (r *Relay) Run(ctx context.Context) {
	for ctx.Err() == nil {
		n, err := r.RunOnce(ctx)
		if err != nil && ctx.Err() == nil {
			r.Log.Error("outbox relay failed", "error", err)
		}
		if n == 0 || err != nil {
			select {
			case <-ctx.Done():
			case <-time.After(500 * time.Millisecond):
			}
		}
	}
}
```

Read it closely; every line matters:

1. **`FOR UPDATE SKIP LOCKED`** is lesson 17's trick again: run the relay in two workers, and they take different rows, never the same one.
2. **`ORDER BY occurred_at, id`**: oldest first, so events go out roughly in the order they happened. (`id` breaks ties between events in the same microsecond.)
3. **`js.Publish` waits for JetStream to say "stored".** Unlike plain NATS, a JetStream publish gets an acknowledgement back once the message is safely in the stream. If it doesn't come, `Publish` returns an error, the transaction rolls back, and the rows are tried again next time.
4. **`jetstream.WithMsgID(e.ID)`** sets a header, `Nats-Msg-Id`, to the event's own ID. JetStream remembers recent IDs (the stream's *duplicate window*, below), and **silently drops** a second message with the same ID. So if the relay publishes, then crashes before `COMMIT`, the rows are still unpublished, get published again next time, and JetStream throws the copies away.

I tested that last point against a real NATS server: four events relayed, then marked unpublished again (a pretend crash), then relayed again. The stream had **4** messages, not 8.

The dedupe only works inside the duplicate window (10 minutes, below), so a relay that's been down for an hour can still send a copy. That's why consumers must handle duplicates anyway (step 6). The window makes duplicates rare; the consumer makes them harmless.

### What this replaces

Look back at the honest gaps from earlier lessons:

1. **Lesson 17**: the status change and the partner webhook's `Enqueue` were two separate steps. Now the API's worker has a consumer of `order.ready` that creates the Okada Riders delivery. The event can't be lost, because it was committed with the status change.
2. **Lesson 18**: the receipt job and its sweeper. The receipt job is gone from the API entirely; notifications sends receipts from `order.paid`.
3. **Lesson 20**: the kitchen's Redis publish could fail and leave the screen waiting for its next snapshot. The kitchen can be fed from the stream instead, and hear about every paid order.

One reliable record of "what happened", many readers.

## Step 5: streams and consumers in JetStream
<!-- bite: ee80d154-4e56-4ca1-bed4-218b05f28fde -->

A **stream** collects every message sent to its subjects and keeps it. The worker creates ours when it starts (it's safe to run every time):

```go
// EnsureStream creates or updates the ORDERS stream. Safe to run at every start.
func EnsureStream(ctx context.Context, js jetstream.JetStream) (jetstream.Stream, error) {
	return js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
		Name:       "ORDERS",
		Subjects:   []string{"orders.>"},
		Storage:    jetstream.FileStorage,
		MaxAge:     7 * 24 * time.Hour,
		Duplicates: 10 * time.Minute,
	})
}
```

1. **`Subjects: orders.>`**: everything published to `orders.paid`, `orders.ready` and so on lands in this stream.
2. **`FileStorage`**: kept on disk, so a NATS restart loses nothing. (Lesson 28 gives the NATS container a volume.)
3. **`MaxAge: 7 days`**: older messages are deleted. A consumer that's been broken for more than a week has a bigger problem than missed receipts, and a stream that grows forever is a disk that fills up.
4. **`Duplicates: 10 minutes`**: the window in which `Nats-Msg-Id` dedupes.

A **durable consumer** is a named reader of the stream that the server remembers: which messages it has finished, which are out with a reader, which to give out next. Several copies of the notifications service can all read through the *same* durable consumer, and JetStream gives each message to one of them, so they share the work. A *different* durable consumer, say `partner-webhooks`, gets every message too, with its own progress:

```text
ORDERS stream ──┬──► consumer "notifications"     → notifications copy 1, copy 2 (share the work)
                ├──► consumer "partner-webhooks"  → the API's worker
                └──► consumer "kitchen"           → each API server
```

`internal/notifications/consumer.go`:

```go
// Package notifications is the notifications service. It must not import the API's packages.
package notifications

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"time"

	"github.com/nats-io/nats.go/jetstream"

	"mamaput/internal/contracts/events"
)

// ErrSkip tells the consumer an event can never be handled: drop it, don't retry it.
var ErrSkip = errors.New("skip this event")

type Handler func(ctx context.Context, e events.Envelope) error

// Consume reads the ORDERS stream as the durable consumer "notifications" until ctx ends.
// Every copy of the service shares the one consumer, so each event goes to one copy.
func Consume(ctx context.Context, js jetstream.JetStream, log *slog.Logger, handle Handler) error {
	cons, err := js.CreateOrUpdateConsumer(ctx, "ORDERS", jetstream.ConsumerConfig{
		Durable:        "notifications",
		FilterSubjects: []string{"orders.paid", "orders.ready"},
		AckPolicy:      jetstream.AckExplicitPolicy,
		AckWait:        30 * time.Second,
		MaxDeliver:     20,
		DeliverPolicy:  jetstream.DeliverAllPolicy,
	})
	if err != nil {
		return err
	}

	cc, err := cons.Consume(func(msg jetstream.Msg) {
		var e events.Envelope
		if err := json.Unmarshal(msg.Data(), &e); err != nil || e.ID == "" {
			log.Warn("bad event, dropping", "subject", msg.Subject())
			msg.Term()
			return
		}
		hctx, cancel := context.WithTimeout(ctx, 20*time.Second) // less than AckWait
		defer cancel()
		switch err := handle(hctx, e); {
		case err == nil:
			msg.Ack()
		case errors.Is(err, ErrSkip):
			log.Warn("event can't be handled, dropping", "id", e.ID, "type", e.Type, "error", err)
			msg.Term()
		default:
			meta, _ := msg.Metadata()
			log.Warn("event failed, will retry", "id", e.ID, "type", e.Type, "attempt", meta.NumDelivered, "error", err)
			msg.NakWithDelay(retryDelay(meta)) // try again later; a plain Nak would retry at once
		}
	})
	if err != nil {
		return err
	}
	<-ctx.Done()
	cc.Drain() // finish the messages in hand, take no more
	<-cc.Closed()
	return nil
}

// retryDelay waits longer after each failed attempt: 1s, 2s, 4s ... up to 2 minutes.
func retryDelay(meta *jetstream.MsgMetadata) time.Duration {
	attempt := uint64(1)
	if meta != nil {
		attempt = meta.NumDelivered
	}
	return min(time.Second<<min(attempt-1, 7), 2*time.Minute)
}
```

The ideas that matter:

1. **`FilterSubjects`**: this consumer only receives `orders.paid` and `orders.ready`. `order.placed` stays in the stream for anyone else, and notifications never sees it.
2. **`AckExplicitPolicy`**: a message counts as done only when we call `msg.Ack()`, and we call it only **after** the handler has succeeded.
3. **`AckWait: 30s`**: if a reader takes a message and doesn't answer within 30 seconds (it crashed, or hung), JetStream gives the message to another reader. That's lesson 18's "stalled job", handled by the server. The handler's own timeout is 20 seconds, so it gives up before the server does, and we don't end up with two readers working on one message.
4. **Three answers to a message:** `Ack` (done), `NakWithDelay` (failed, try again later), `Term` (this can never work: never deliver it again). A message that can't even be decoded is `Term`ed. A handler that knows the event is hopeless returns `ErrSkip`. Everything else is retried.
5. **`NakWithDelay`, not `Nak`.** A plain `Nak` puts the message straight back, and a provider that's down would be hammered in a tight loop. `retryDelay` doubles the wait each time, 1, 2, 4, 8 seconds and so on, up to 2 minutes: lesson 17's backoff for outgoing webhooks, again. `time.Second << n` is "one second, doubled n times".
6. **`MaxDeliver: 20`**: after 20 attempts JetStream stops delivering it. With the delays above, that's about half an hour of trying. Lesson 27 adds an alert for messages that hit the limit, so a person looks at them.
7. **`cons.Consume(func...)`** calls our function for each message, from a goroutine the library manages, and keeps fetching more in the background. **`Drain`** on shutdown stops fetching and lets the messages already in hand finish, the consumer's version of `http.Server.Shutdown`.

**Order isn't promised.** With two copies of the service, two events can be handled at the same time, and a retried event comes back later than ones behind it. Our handlers mustn't depend on order: `order.ready` arriving before `order.paid` must still do the right thing. Step 6's handlers only look at the event in front of them, so it's fine.

## Step 6: the notifications service
<!-- bite: 6c24de18-30a5-4cb6-b60a-7381014049e1 -->

```text
internal/notifications/
├── consumer.go            ← Consume (above)
├── handlers.go            ← one function per event type
├── sent.go                ← sent_notifications: WasSent, Record
├── preferences.go         ← who wants texts, who wants emails
├── customers.go           ← the gRPC client for the API's CustomersService
├── providers.go           ← Mailer and SMS interfaces, and console versions for development
├── boundary_test.go       ← step 2
└── migrations/
    ├── 001_sent_notifications.sql
    └── 002_preferences.sql
```

`internal/notifications/migrations/001_sent_notifications.sql`:

```sql
CREATE TABLE sent_notifications (
  event_id     uuid        NOT NULL,
  kind         text        NOT NULL,     -- 'receipt-email', 'ready-sms', ...
  customer_id  bigint      NOT NULL,
  sent_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event_id, kind)
);
```

Embedded with `//go:embed migrations/*.sql` and run by lesson 8's `db.Migrate`, which is exactly why it was written to know nothing about dishes. Notifications runs its migrations itself when it starts; it's the only program that uses its database.

### The handlers

`internal/notifications/handlers.go`:

```go
type Handlers struct {
	Customers   Customers
	Menu        Menu
	Sent        *SentStore
	Preferences *Preferences
	Mailer      Mailer
	SMS         SMS
}

func (h *Handlers) Handle(ctx context.Context, e events.Envelope) error {
	switch {
	case e.Type == events.OrderPaid && e.Version == 1:
		var data events.OrderPaidV1
		if err := json.Unmarshal(e.Data, &data); err != nil {
			return fmt.Errorf("%w: %v", ErrSkip, err)
		}
		return h.receipt(ctx, e.ID, data)
	case e.Type == events.OrderReady && e.Version == 1:
		var data events.OrderReadyV1
		if err := json.Unmarshal(e.Data, &data); err != nil {
			return fmt.Errorf("%w: %v", ErrSkip, err)
		}
		return h.readyText(ctx, e.ID, data)
	}
	return nil // a type or version we don't know: not for us, and that's fine
}

func (h *Handlers) receipt(ctx context.Context, eventID string, d events.OrderPaidV1) error {
	if d.CustomerID == nil {
		return nil // an anonymous v1 order: nobody to tell
	}
	if sent, err := h.Sent.WasSent(ctx, eventID, "receipt-email"); err != nil || sent {
		return err
	}
	contact, err := h.Customers.Contact(ctx, *d.CustomerID)
	if err != nil {
		return err // the API is unreachable: retry later
	}
	if contact.Email == "" || !h.Preferences.WantsEmail(ctx, *d.CustomerID) {
		return nil
	}
	dish, err := h.Menu.Dish(ctx, d.DishID)
	if err != nil {
		return err
	}
	err = h.Mailer.Send(ctx, Email{
		To:      contact.Email,
		Subject: fmt.Sprintf("Mama Put receipt for order %d", d.OrderID),
		Text: fmt.Sprintf("Thank you, %s! %d × %s, %s.",
			contact.FirstName, d.Quantity, dish.Name, naira(d.TotalKobo)),
	})
	if err != nil {
		return err
	}
	return h.Sent.Record(ctx, eventID, "receipt-email", *d.CustomerID)
}
```

(`readyText` is the same shape, for `ready-sms`, with the phone number and `h.SMS.Send`.)

1. **Unknown types and versions are ignored**, returning `nil`, so they're acked. The API will publish events notifications doesn't care about, and new versions before notifications has learned them. Ignoring them is what lets the API add events and versions without breaking anyone.
2. **A body that can't be decoded is `ErrSkip`**, wrapped with `%w` so `errors.Is` still finds it in the consumer. Retrying it twenty times won't make the JSON valid.
3. **`WasSent`, then send, then `Record`**: lesson 18's choice. If the service crashes after sending but before recording, the event is delivered again and the receipt is sent twice. A duplicate receipt is better than none. The primary key on `(event_id, kind)` means the record itself can never be doubled. (Some email providers accept an idempotency key with each send; when yours does, pass the event ID, and the provider drops the duplicate for you.)
4. **Contact details come from the API**, fresh, at the moment of sending. Not from the event, and not from a copy kept in notifications' database.
5. **If a call to the API fails, the handler returns the error**, the consumer NAKs with a delay, and it's retried. The customer gets the receipt a little late. **That's the whole point of the split:** the API being briefly unreachable delays texts; texts being broken never delays orders.

### Asking the API: `CustomersService`

A second gRPC service beside lesson 22's `MenuService`, in `proto/mamaput/customers/v1/customers.proto`:

```proto
syntax = "proto3";

package mamaput.customers.v1;

option go_package = "mamaput/internal/gen/mamaput/customers/v1;customersv1";

// Contact details for Mama Put's own services. Personal data: callers must be allowed (lesson 26).
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

It returns the **first name**, not the full name, and nothing else: exactly what a message needs. The phone number is a new column, `migrations/016_users_phone.sql` (`ALTER TABLE users ADD COLUMN phone text`), which customers fill in through the app. `optional` because many won't.

The API serves it in `internal/grpcapi/customers.go`, a thin call to `auth.Service`'s user lookup, like `MenuServer`. On the notifications side, `customers.go` wraps the generated client in the small interface the handlers use:

```go
type Contact struct {
	FirstName, Email, Phone string
}

type Customers interface {
	Contact(ctx context.Context, customerID int64) (Contact, error)
}

type GRPCCustomers struct{ Client customersv1.CustomersServiceClient }

func (g GRPCCustomers) Contact(ctx context.Context, id int64) (Contact, error) {
	ctx, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
	defer cancel()
	res, err := g.Client.GetContact(ctx, &customersv1.GetContactRequest{CustomerId: id})
	if status.Code(err) == codes.NotFound {
		return Contact{}, fmt.Errorf("%w: customer %d is gone", ErrSkip, id)
	}
	if err != nil {
		return Contact{}, err
	}
	return Contact{FirstName: res.GetFirstName(), Email: res.GetEmail(), Phone: res.GetPhone()}, nil
}
```

The handlers depend on `Customers`, the interface, so tests use a fake (lesson 5). A deleted customer is `ErrSkip`: they'll never come back. And every call has its deadline, from lesson 22.

`GetContact` returns personal data to another service. Right now, anything that can reach port 50051 could call it. That's not acceptable for long, and it's the first thing lesson 26 fixes, with service-to-service authentication.

### `cmd/notifications/main.go`

The same `run` shape as the API since lesson 5, building its own world:

```go
func run(ctx context.Context, getenv func(string) string, stdout io.Writer) error {
	logger := slog.New(slog.NewJSONHandler(stdout, nil)).With("service", "notifications")

	pool, err := pgxpool.New(ctx, getenv("NOTIFICATIONS_DATABASE_URL"))
	if err != nil {
		return err
	}
	defer pool.Close()
	if err := db.Migrate(ctx, pool, notifications.Migrations); err != nil {
		return err
	}

	nc, err := nats.Connect(getenv("NATS_URL"), nats.Name("notifications"))
	if err != nil {
		return err
	}
	defer nc.Drain()
	js, err := jetstream.New(nc)
	if err != nil {
		return err
	}

	conn, err := grpc.NewClient(getenv("API_GRPC_ADDR"), grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return err
	}
	defer conn.Close()

	h := &notifications.Handlers{
		Customers:   notifications.GRPCCustomers{Client: customersv1.NewCustomersServiceClient(conn)},
		Menu:        notifications.GRPCMenu{Client: menuv1.NewMenuServiceClient(conn)},
		Sent:        notifications.NewSentStore(pool),
		Preferences: notifications.NewPreferences(pool),
		Mailer:      notifications.ConsoleMailer{Log: logger},
		SMS:         notifications.ConsoleSMS{Log: logger},
	}

	go serveHealth(ctx, getenv("HEALTH_ADDR"), pool, nc) // GET /healthz: lesson 28
	logger.Info("notifications started")
	return notifications.Consume(ctx, js, logger, h.Handle)
}
```

Its own database URL, its own logger with `service=notifications` on every line (lesson 27 will be glad), the stream through NATS, and the API only through gRPC. Two things in `main.go` stand out:

1. **`ConsoleMailer` and `ConsoleSMS`** log what they would send. Real providers come with real keys, which belong to this service alone: the API no longer holds the email or SMS secrets at all, which is one more reason for the split.
2. **`defer nc.Drain()`** on the NATS connection, the same idea as the consumer's drain: finish what's in flight, then close.

Run it beside the API and the worker:

```bash
go run ./cmd/notifications
```

Pay for an order with lesson 17's signed webhook, and within a second the notifications log shows the receipt it would have sent. Stop notifications, pay for two more orders, start it again: both receipts appear, because the stream kept them. Okay!!!!! Two services, one truth.

## Step 7: what changes in the API
<!-- bite: 8e7d0891-2957-488b-881a-ff54ad871f2f -->

1. **The worker runs the relay** (`go relay.Run(ctx)`), and creates the stream at start-up with `EnsureStream`.
2. **Receipts move out.** `TypeSendReceipt`, its handler and the sweeper's receipt check are deleted from the API. The email provider's key is removed from the API's config.
3. **Partner webhooks hear from the stream.** The worker gets a durable consumer `partner-webhooks` filtered to `orders.ready`, whose handler calls lesson 17's `Deliveries.Enqueue` with the event ID as the delivery's idempotency key. The `Notifier` interface in the orders service is gone.
4. **`Settle` and `SetStatus` don't call anything after committing.** They write to the outbox inside their transactions, and that's all. The services got simpler.
5. **The API serves `CustomersService`** on its gRPC port.

Look at item 4 again. The old code had a list of things to remember after each change ("queue the receipt, tell the kitchen, tell Okada"). Each forgotten line was a bug. Now a change records one event, and everything that cares subscribes. Adding a new reaction to "order ready" doesn't touch the orders code at all.

## Step 8: testing across services
<!-- bite: be1b4db5-3f07-4ff8-8340-4fad767bf2da -->

1. **Handlers alone**, with fakes for `Customers`, `Menu`, `Mailer` and `SMS`, and a real `SentStore` against the test database: an `order.paid` event sends one email; the same event again sends nothing; a customer who turned emails off gets none; an unknown type returns `nil`; a broken body returns `ErrSkip`; a failing `Customers` returns an error (so it'll be retried).
2. **The outbox**, with lesson 16's integration build tag and a real NATS: settle a payment, run `RunOnce`, and check one message arrived in `ORDERS` with the event's ID as `Nats-Msg-Id`. Then mark it unpublished, run `RunOnce` again, and check the stream still has **one** message.
3. **The consumer**, with a real NATS: a handler that fails the first time is called again after the delay and then acked; `ErrSkip` is never redelivered; an event on `orders.placed` never reaches it. (This lesson's code was tested exactly like that: after one failure and one retry, the consumer had nothing pending and nothing waiting for an ack.)
4. **The boundary**: step 2's test, in every run.
5. **The whole chain, once**: lesson 28's Docker Compose file starts everything; a test pays for an order through the API and waits up to 5 seconds for the console mailer's log line. Slow, so it runs in CI only (lesson 29).

For tests that need NATS, start it like Postgres in lesson 16: a container, and `t.Skip` if `NATS_URL` isn't set. NATS also runs happily inside a Go test (the server is a Go package, `github.com/nats-io/nats-server/v2/server`), which some teams prefer to a container.

## The Go in this lesson
<!-- bite: 58a46e7b-1d8d-46aa-8634-aaea067578b2 -->

1. **Several `main` packages in one module**: Each `cmd/<name>` builds its own program: `go build ./cmd/notifications`.
2. **`go list -deps -f '{{.ImportPath}}'`**: Every package a program needs, directly or not. Run from a test with `os/exec`, it turns an architecture rule into a failing test.
3. **`json.RawMessage`**: Raw JSON bytes kept as they are, to decode later once you know the type.
4. **A function that only accepts a transaction, `Add(ctx, tx pgx.Tx, ...)`**: The type makes "this must be in the same transaction" impossible to forget.
5. **`pgx.CollectRows(rows, func(pgx.CollectableRow) (T, error))`**: Scans every row with your function and returns a slice.
6. **`jetstream.WithMsgID(id)`**: A publish option; JetStream drops a second message with the same ID inside the stream's duplicate window.
7. **`cons.Consume(func(msg jetstream.Msg))`**: Calls your function for each message, fetching more in the background, until you `Stop` or `Drain`.
8. **`msg.Ack()`, `msg.NakWithDelay(d)`, `msg.Term()`**: Done, try again later, never again.
9. **`time.Second << n`**: A `time.Duration` is a number of nanoseconds, so shifting left doubles it `n` times.
10. **`switch err := handle(hctx, e); { case err == nil: ... }`**: A `switch` with a short statement and no value: each `case` is a condition, checked in order.
11. **`fmt.Errorf("%w: %v", ErrSkip, err)`**: Wraps the sentinel with `%w` (so `errors.Is` finds it) and adds the cause as text with `%v`.
12. **`//go:embed migrations/*.sql`** into an `embed.FS`: The service's migrations travel inside its binary, as in lesson 8.

## Your project so far
<!-- bite: d86f2a04-5a20-4032-91a1-34aedeb016ab -->

```text
mama-put/
├── go.mod                         ← github.com/nats-io/nats.go
├── proto/mamaput/
│   ├── menu/v1/menu.proto
│   └── customers/v1/customers.proto      ← NEW: CustomersService.GetContact
├── migrations/
│   ├── 015_outbox.sql             ← NEW: the outbox table and its unpublished index
│   └── 016_users_phone.sql        ← NEW: users.phone
├── cmd/
│   ├── api/main.go                ← serves CustomersService too
│   ├── worker/main.go             ← EnsureStream, the relay, the partner-webhooks consumer; no receipts
│   └── notifications/main.go      ← NEW: its own database, NATS, gRPC clients, health, Consume
└── internal/
    ├── contracts/events/events.go ← NEW: Envelope, event names, Subject, OrderPaidV1, OrderReadyV1
    ├── outbox/outbox.go           ← NEW: Add (needs a pgx.Tx), Relay (SKIP LOCKED, WithMsgID), EnsureStream
    ├── payments/postgres.go       ← MarkSucceeded writes order.paid to the outbox
    ├── orders/postgres.go         ← status changes and placing write their events to the outbox
    ├── grpcapi/customers.go       ← NEW: CustomersServer
    ├── jobs/                      ← receipt job and its sweeper check removed
    └── notifications/             ← NEW: the notifications service
        ├── consumer.go            ← Consume: durable consumer, Ack / NakWithDelay / Term, Drain
        ├── handlers.go            ← receipt and ready text; unknown events ignored
        ├── sent.go · preferences.go · customers.go · providers.go
        ├── boundary_test.go       ← imports nothing of the API's
        └── migrations/            ← 001_sent_notifications.sql, 002_preferences.sql
```

## Common mistakes
<!-- bite: a561f939-108e-4b01-b57e-6e8138b429f2 -->

1. **Splitting too early, or splitting the wrong thing.** Something the main flow waits on becomes a network call that can fail. Split what can be late.
2. **Sharing a database "for now".** It becomes the hidden contract that stops either side changing. Each service owns its data.
3. **Importing the other service's packages** because it's the same module. Write the boundary test on day one.
4. **Publishing after the commit**, or before it. A crash in between loses or invents an event. Write to the outbox in the same transaction.
5. **No message ID on publish.** Every relay crash becomes a duplicate.
6. **Acking before handling.** A crash mid-handler loses the event. Ack after.
7. **A plain `Nak` on failure.** The message comes straight back and hammers whatever's broken. Nak with a growing delay.
8. **Retrying what can never work.** A broken body, a deleted customer: `Term` them.
9. **Handlers that assume order.** Two copies, retries and backoff all reorder events. Look at the event, not at what came before.
10. **Personal data in events.** They're stored and read by everyone. Facts and IDs; fetch contact details when you need them.
11. **Events in the services' own types.** The contract package must import nothing from either side.

## Check your understanding
<!-- bite: 37a7c3cf-40fa-4703-98c9-656ecbb9d24d -->

1. Why is notifications a good first service to split out, and payments a bad one?
2. Everything is one Go module. What stops `internal/notifications` importing `internal/orders`, and why does it matter?
3. Follow a payment from Paystack's webhook to Ada's receipt email, naming each step and what happens if the process crashes after it.
4. The relay publishes three events and crashes before `COMMIT`. What happens next, and why does Ada still get one receipt?
5. The SMS provider is down for ten minutes. What happens to `order.ready` events, and to the API?
6. Why does the handler's timeout (20 s) have to be shorter than `AckWait` (30 s)?

<details>
<summary>Answers, after your attempt</summary>

1. Nothing waits for notifications: a receipt a minute late is fine, it has clear edges, and its outside providers fail in ways we want kept away from orders. Payments is needed in the middle of placing and paying for an order, so splitting it would turn the main flow into network calls that can fail.
2. Nothing in Go itself, since `internal/` only protects against other modules. The boundary test does: `go list -deps` lists every package `cmd/notifications` needs, and any `mamaput/` package outside the allowed list fails the build. Without it, one import would tie the two services' code together and they could no longer change separately.
3. The webhook reaches `Settle`; `MarkSucceeded` updates the payment and the order and adds `order.paid` to the outbox in one transaction (a crash before `COMMIT` changes nothing, and Paystack retries). The relay publishes it to `ORDERS` and marks it published (a crash before its `COMMIT` means it's published again, and JetStream drops the copy). The `notifications` consumer receives it; the handler fetches Ada's contact over gRPC, sends the email and records it (a crash before `Ack` means it's delivered again: `WasSent` catches it if `Record` ran, otherwise Ada gets a second receipt), and then it's acked.
4. The rows are still unpublished, so the relay publishes them again on its next run. They have the same `Nats-Msg-Id`, inside the 10-minute duplicate window, so JetStream drops the copies, and the stream holds each event once. If the window had passed, notifications' `WasSent` check would catch the duplicate.
5. `readyText` returns the SMS error, the consumer NAKs each event with a growing delay (1, 2, 4 ... seconds), and they're retried until the provider is back, then sent and acked. The API doesn't notice: it wrote the events to its outbox and carried on.
6. If the handler were still working when `AckWait` ran out, JetStream would give the same message to another copy, and two copies would send the same text at once. Giving up first means the message is NAKed cleanly before the server hands it to anyone else.

</details>

## Practice
<!-- bite: d15ee9ed-a5a4-4709-ac48-40ea32053ecf -->

1. Write `sent.go` (`WasSent`, `Record` with `ON CONFLICT DO NOTHING`), `preferences.go` (default: emails yes, texts yes), and the handler tests from step 8.
2. Add the outbox writes for `order.ready` and `order.collected` in the orders store's status change, inside its transaction, and a test that a failed status change leaves no event behind.
3. Build the `partner-webhooks` consumer in the worker, and delete the `Notifier` interface from the orders service.
4. Feed the kitchen from the stream: an **ordered consumer** (`js.OrderedConsumer`, which needs no durable name and is perfect for a live screen) on `orders.paid` in each API server, passing events to lesson 20's hub. Keep the snapshot.
5. Write `ConsoleSMS` and `readyText`, and check an `order.ready` for a customer with no phone number is acked without sending.
6. Use `nats stream info ORDERS` and `nats consumer info ORDERS notifications` while you stop and start notifications, and watch the "unprocessed" count go up and come back down.

**Done when** a paid order produces exactly one receipt log line in notifications; stopping notifications and paying for two orders delivers both receipts when it starts again; relaying the same outbox rows twice leaves one message per event in the stream; a handler that fails once is retried after a delay; the boundary test fails if you import `orders` into notifications; and `make test` and `make test-integration` pass.

## Before moving on
<!-- bite: 8b597744-c60e-4c92-8eba-39da55fff06e -->

Mama Put is two services now. The API owns orders and payments and says what happened; the notifications service listens and tells customers. They share a contract package and a gRPC definition, and nothing else: not code (a test proves it), not a database (a Postgres user proves it). The outbox means an event can't be lost or invented, the message ID means a crash doesn't double it, and the consumer means a broken SMS provider makes texts late and nothing else.

But look at `Customers.Contact`: notifications calls the API, and the API might be slow, or down, or deploying. A 500 ms timeout helps, but what if every call times out for a minute? What about retries, and which calls are safe to retry? And right now anything on the network can ask port 50051 for a customer's phone number. Calling other services safely is a skill of its own. That's the next lesson.

## Related
<!-- bite: 0a2071b7-913a-46e4-85db-bf173a4cde2b -->

- [[backend/frameworks/net-http/26-calling-services-safely|Next: Calling Other Services Safely]]
- [[backend/frameworks/express/25-splitting-out-a-microservice|The same lesson in Express]] — npm workspaces, and Redis Streams with consumer groups instead of JetStream
- [[backend/frameworks/net-http/17-payments-and-webhooks|Payments and Webhooks]] — the transaction the outbox joins
- [[backend/frameworks/net-http/18-background-jobs|Background Jobs and Queues]] — the gap the outbox closes, and "safe to run twice"
- [[backend/frameworks/net-http/22-grpc|gRPC]] — the contract notifications calls the API through

## About this lesson
<!-- bite: a8cd607e-8d41-4481-8147-ab4eddc1d2b9 -->

**Level:** Advanced. Lesson 25 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, nats.go with its `jetstream` package, and NATS Server 2.10 or later with JetStream on. Covers when to split a service and good first candidates, several programs in one module and an import-boundary test with `go list -deps`, a private database per service, events as a versioned contract with an envelope and `json.RawMessage`, thin and fat events, the outbox in the same `pgx.Tx` as the change, a relay with `FOR UPDATE SKIP LOCKED` and JetStream message IDs for deduplication, streams with file storage, an age limit and a duplicate window, durable consumers with explicit acks, ack wait, delayed NAKs and terminated messages, draining on shutdown, idempotent handlers, a gRPC service for contact details, and testing handlers, the relay, the consumer and the boundary.
