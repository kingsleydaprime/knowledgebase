---
id: b220e682-57da-46a3-ba07-c33231b415fa
---

# Payments and Webhooks

**Taking a payment means sending the customer to a payment company's page, and then waiting for that company to *tell your server*, in a signed message called a webhook, that the money really arrived.** Your server never sees a card number, and it never believes the customer's word that they paid. It believes the payment company, and only after checking the message is genuinely from them.

## Before you start
<!-- bite: 04970484-ccbf-4e7a-a2d3-87fdb1242bb8 -->

You should have:

1. Finished [[backend/frameworks/net-http/16-testing|lesson 16]], so you have `apptest`, `dbtest` and the integration-test setup.
2. A free Paystack account in **test mode**, with its test secret key (it starts `sk_test_`). Test mode moves no real money.

After this lesson you will be able to:

1. Explain why a payment can't be finished inside one request, and why the redirect back to your site proves nothing.
2. Call an outside API from Go safely: an `http.Client` with a timeout, responses checked before use, and a calm error for the customer.
3. Receive Paystack's webhooks: check the HMAC signature on the exact bytes, skip duplicates, and settle each payment exactly once.
4. Verify a payment yourself, as a backup to the webhook.
5. Send your own signed webhooks to a partner, from a queue in Postgres, with timestamps, event IDs, retries, backoff and jitter.

## Where we stopped
<!-- bite: e08c0d32-8fe1-4243-9103-20aa282dcba7 -->

Right now, placing an order writes a row and takes the portions. Nobody pays. Ada could order twenty plates of jollof and walk away.

Mama wants it simple: you order, you pay, and only then does the kitchen cook. And when the food is ready, the riders from **Okada Riders** (the delivery company Mama works with) should hear about it straight away, without someone phoning them.

So this lesson has two directions:

1. **Webhooks coming in**: Paystack telling us "this payment succeeded".
2. **Webhooks going out**: us telling Okada Riders "order 42 is ready for pickup".

## The kid version
<!-- bite: a346269d-70aa-4927-92c8-65c41b7587d0 -->

Ada buys a plate, but she pays at the bank across the road, not at Mama's table. Mama can't see the bank.

Ada comes back and says "I've paid, see?" and waves a paper. Should Mama believe the paper? Anyone can write on paper.

So Mama and the bank agree on a better way. When someone pays, the bank sends its own messenger to Mama, with a note sealed with a stamp only the bank has. Mama checks the stamp, and *then* she believes it. If the messenger comes twice with the same note, she doesn't cook twice.

The messenger is the webhook. The stamp is the signature. Ada's paper is the redirect back to our site, and we never trust it by itself.

**Where the picture stops working.** A real messenger knows when he has delivered the note. A webhook doesn't always: the request can be lost, or our server can be down. So the bank keeps sending the same note until Mama says "got it", and Mama must be ready to receive the same note many times.

## Terms used in this lesson
<!-- bite: 1b3d3ef0-c559-4bfb-9cd1-4216e5ad0e46 -->

1. **Payment provider**: This is the company that takes the card or bank transfer and moves the money, here **Paystack**. We never touch card numbers ourselves; the customer types them on Paystack's page.
2. **Checkout**: This is Paystack's payment page. We ask Paystack to start one, and it gives us a link to send the customer to.
3. **Reference**: This is a unique name *we* give each payment attempt, like `mp-42-K7Q3...`. It's how we and Paystack talk about the same payment.
4. **Webhook**: This is an HTTP POST another system sends to a URL on our server when something happens. Paystack sends one called `charge.success` when a payment succeeds.
5. **Signature**: This is a code worked out from the webhook's exact body and a secret only the sender and we know. If the code matches, the webhook really came from the sender and wasn't changed on the way.
6. **HMAC**: This stands for **hash-based message authentication code**. It's the recipe for that code: mix the secret and the message, then hash them. Without the secret, nobody can make a matching code.
7. **At-least-once delivery**: This means the sender promises every webhook arrives *at least* once, and sometimes more than once. Receivers must cope with duplicates.
8. **Verify call**: This is an API call *we* make to Paystack, asking "what really happened to payment `mp-42-...`?". It's our backup when we haven't heard a webhook.
9. **Backoff**: This is waiting longer after each failed try: 30 seconds, then a minute, then two. **Jitter** is a small random extra on each wait, so many retries don't all land at the same moment.

## What to install
<!-- bite: 0509cd68-1713-46c1-972b-edfd31cb115a -->

Nothing new in Go: `net/http` is a full HTTP **client** as well as a server, and `crypto/hmac` makes signatures. You need settings, in `.env`:

```text
PAYSTACK_SECRET_KEY=sk_test_...
PUBLIC_URL=http://localhost:8080
OKADA_WEBHOOK_URL=http://localhost:9090/hooks/mama-put
OKADA_WEBHOOK_SECRET=<another long random value, made with openssl rand -base64 32>
```

`PUBLIC_URL` is where customers' browsers reach us; Paystack sends them back there. The Okada settings point at a pretend partner on your own laptop for now; step 10 makes one.

## Step 1: why paying can't happen in one request
<!-- bite: 2fcef7b8-5eb2-475e-bcee-67388eb6cc06 -->

Every request so far went: request in, work, answer out, done. A payment can't work like that, because the middle part happens somewhere we can't see:

1. Ada asks us to pay for order 42.
2. We ask Paystack to start a checkout. Paystack gives us a link.
3. We send Ada the link. Her app opens Paystack's page.
4. Ada types her card details, and maybe a one-time code from her bank. This could take ten seconds or ten minutes. She might give up.
5. Paystack sends Ada's browser back to our site.
6. Separately, Paystack sends **us** a webhook: `charge.success` for `mp-42-...`.

Step 5 is tempting. Ada's browser lands on `https://mamaput.example/payment-done?reference=mp-42-...`, so why not mark the order paid right there?

Because anyone can type that URL. Ada (or someone less honest than Ada) can visit it without paying a kobo. And the opposite also happens: Ada pays, closes the tab before the redirect, and never lands on step 5 at all. The redirect is just the browser, and the browser is the customer's.

So, the rule for the whole lesson: **an order becomes paid only when Paystack itself says so**: through a signed webhook, or through a verify call we make to Paystack ourselves.

## Step 2: the tables
<!-- bite: 9fa81597-f684-40c5-a90c-3d10789d5ab4 -->

`migrations/011_payments.sql`:

```sql
CREATE TABLE payments (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id     bigint NOT NULL REFERENCES orders (id),
  reference    text   NOT NULL UNIQUE,
  amount_kobo  bigint NOT NULL CHECK (amount_kobo > 0),
  status       text   NOT NULL DEFAULT 'started'
               CHECK (status IN ('started', 'succeeded', 'failed')),
  created_at   timestamptz NOT NULL DEFAULT now(),
  settled_at   timestamptz
);

CREATE INDEX payments_order_id_idx ON payments (order_id);

ALTER TABLE orders ADD COLUMN paid_at timestamptz;
```

Why a separate `payments` table, instead of a `paid` column on the order? Because one order can have **several payment attempts**. Ada starts paying, her card is declined, she tries another card. Each attempt gets its own row and its own reference. The order is paid when one of them succeeds, and `orders.paid_at` records when.

`amount_kobo` is copied onto the payment when it starts. That's the amount we *asked* for, and later we'll check Paystack collected exactly that.

`migrations/012_webhooks.sql`:

```sql
-- Webhooks we've received and finished handling.
CREATE TABLE webhook_events_received (
  provider     text NOT NULL,
  event_key    text NOT NULL,
  handled_at   timestamptz NOT NULL DEFAULT now(),
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

CREATE INDEX webhook_deliveries_due_idx
  ON webhook_deliveries (next_attempt_at)
  WHERE delivered_at IS NULL;
```

The first table is for webhooks coming in, the second for webhooks going out. The index is **partial**, like lesson 15's: it only holds rows still waiting to be sent, so it stays small however many thousands have been delivered. `gen_random_uuid()` is built into Postgres since version 13.

```bash
make migrate
```

## Step 3: talking to Paystack
<!-- bite: 56342753-31a7-42eb-8914-2a4be4682e10 -->

Every outside service gets one small file that knows how to talk to it, and the rest of the app talks to it through an interface we own. It's the lesson 5 idea again: the orders service doesn't know about SQL, and the payments service won't know about Paystack's URLs.

First, one new kind of error. So far every error was the *client's* fault (400s) or a broken rule. Now there's a third case: Paystack is down, or slow, or answers nonsense. That's nobody's fault in the request, and the usual status is **502 Bad Gateway**: "I'm a gateway to another service, and it let me down". Add `Upstream` to the kinds in `apperr`, and `apperr.Upstream: http.StatusBadGateway` to `statusFor`.

`internal/payments/payments.go`:

```go
// Package payments takes payments through a provider, and settles them exactly once.
package payments

import (
	"context"
	"time"

	"mamaput/internal/apperr"
	"mamaput/internal/money"
)

type Status string

const (
	StatusStarted   Status = "started"
	StatusSucceeded Status = "succeeded"
	StatusFailed    Status = "failed"
)

type Payment struct {
	ID        int64
	OrderID   int64
	Reference string
	Amount    money.Kobo
	Status    Status
	CreatedAt time.Time
}

// Seen is what the provider says happened to a payment.
type Seen struct {
	Succeeded bool
	Amount    money.Kobo
	Currency  string
}

// Provider is a payment company, as this package needs it.
type Provider interface {
	StartCheckout(ctx context.Context, email string, amount money.Kobo, reference, callbackURL string) (checkoutURL string, err error)
	Verify(ctx context.Context, reference string) (Seen, error)
}

var (
	ErrPaymentNotFound = apperr.New(apperr.NotFound, "payment-not-found", "There's no such payment.")
	ErrAlreadyPaid     = apperr.New(apperr.Conflict, "order-already-paid", "This order is already paid.")
	errUpstream        = func(code string) *apperr.Error {
		return apperr.New(apperr.Upstream, code, "We couldn't reach the payment service. Please try again.")
	}
)
```

Now the Paystack side, `internal/payments/paystack.go`:

```go
package payments

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"

	"mamaput/internal/money"
)

type Paystack struct {
	baseURL   string
	secretKey string
	client    *http.Client
}

// NewPaystack talks to baseURL ("https://api.paystack.co" in real life; a test server in tests).
func NewPaystack(baseURL, secretKey string, client *http.Client) *Paystack {
	return &Paystack{baseURL: baseURL, secretKey: secretKey, client: client}
}

func (p *Paystack) call(ctx context.Context, method, path string, body, out any) error {
	var reqBody *bytes.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return err
		}
		reqBody = bytes.NewReader(b)
	} else {
		reqBody = bytes.NewReader(nil)
	}
	req, err := http.NewRequestWithContext(ctx, method, p.baseURL+path, reqBody)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+p.secretKey)
	req.Header.Set("Content-Type", "application/json")

	res, err := p.client.Do(req)
	if err != nil {
		return fmt.Errorf("%w: %v", errUpstream("payment-provider-unreachable"), err)
	}
	defer res.Body.Close()
	if res.StatusCode < 200 || res.StatusCode >= 300 {
		return fmt.Errorf("%w: status %d", errUpstream("payment-provider-error"), res.StatusCode)
	}
	if err := json.NewDecoder(http.MaxBytesReader(nil, res.Body, 1<<20)).Decode(out); err != nil {
		return fmt.Errorf("%w: %v", errUpstream("payment-provider-bad-response"), err)
	}
	return nil
}

func (p *Paystack) StartCheckout(ctx context.Context, email string, amount money.Kobo, reference, callbackURL string) (string, error) {
	var out struct {
		Status bool `json:"status"`
		Data   struct {
			AuthorizationURL string `json:"authorization_url"`
		} `json:"data"`
	}
	err := p.call(ctx, "POST", "/transaction/initialize", map[string]any{
		"email": email, "amount": int64(amount), "reference": reference, "callback_url": callbackURL,
	}, &out)
	if err != nil {
		return "", err
	}
	if !out.Status || out.Data.AuthorizationURL == "" {
		return "", errUpstream("payment-provider-bad-response")
	}
	return out.Data.AuthorizationURL, nil
}

func (p *Paystack) Verify(ctx context.Context, reference string) (Seen, error) {
	var out struct {
		Status bool `json:"status"`
		Data   struct {
			Status   string `json:"status"` // "success", "failed", "abandoned", ...
			Amount   int64  `json:"amount"` // in kobo
			Currency string `json:"currency"`
		} `json:"data"`
	}
	if err := p.call(ctx, "GET", "/transaction/verify/"+url.PathEscape(reference), nil, &out); err != nil {
		return Seen{}, err
	}
	if !out.Status || out.Data.Currency == "" {
		return Seen{}, errUpstream("payment-provider-bad-response")
	}
	return Seen{Succeeded: out.Data.Status == "success", Amount: money.Kobo(out.Data.Amount), Currency: out.Data.Currency}, nil
}
```

`fmt.Errorf("%w: %v", errUpstream(...), err)` wraps **our** calm error, with Paystack's details tacked on after it. `WriteError` (lesson 7) finds the `*apperr.Error` with `errors.As`, sends its calm message to Ada, and logs the whole thing, details included. Paystack's messages are written for us, not for her, and can mention things she shouldn't see.

Four habits in there, and they matter for every outside service, not just Paystack:

1. **A timeout on every call.** In `run`, the client is built as `&http.Client{Timeout: 10 * time.Second}`. **`http.DefaultClient` has no timeout at all**: if Paystack hangs, Ada's request hangs with it, for ever, and so does every request behind hers. Never use the default client for anything outside your own machine. Lesson 26 goes much further with this.
2. **The request carries the caller's context.** `NewRequestWithContext(ctx, ...)` means that if Ada gives up and her request is cancelled, our call to Paystack is cancelled too, instead of carrying on for nobody.
3. **Check what comes *back*.** We validate what clients send us (lesson 6). An outside service's answer is input too. If Paystack ever changes its response, we get a clear `payment-provider-bad-response`, not an empty checkout link quietly sent to Ada. The answer's size is capped as well: `MaxBytesReader` works on any reader, with `nil` for the writer when there's no response to close.
4. **The base URL is a setting.** In production it's `https://api.paystack.co`; in a test it's an `httptest.NewServer`'s address (step 11), so the real code runs against a pretend Paystack.

`amount` is in kobo. That's why we moved to kobo in lesson 10: ₦3,000 is `300000`. Send `3000` and Ada is asked to pay ₦30. `money.Kobo` makes the unit part of the type, so `int64(amount)` is the one, visible place it becomes a plain number.

## Step 4: starting a checkout
<!-- bite: e87dc6ee-fabd-4563-ba49-52f32c5d13e5 -->

The customer flow is a new route: "pay for this order". It creates a payment attempt, asks Paystack for a checkout link, and gives the link back.

The service needs orders (to check Ada may pay for this one), users (for her email), a store and the provider. Each is a small interface, declared here, the way lesson 5 taught. `internal/payments/service.go`:

```go
package payments

import (
	"context"
	"crypto/rand"
	"errors"
	"log/slog"
	"strconv"

	"mamaput/internal/auth"
	"mamaput/internal/money"
	"mamaput/internal/orders"
)

type Orders interface {
	Get(ctx context.Context, actor auth.Identity, id int64) (orders.Order, error)
}

type Users interface {
	Find(ctx context.Context, id int64) (auth.User, error)
}

type Store interface {
	Create(ctx context.Context, orderID int64, reference string, amount money.Kobo) error
	FindByReference(ctx context.Context, reference string) (Payment, error)
	MarkFailed(ctx context.Context, reference string) error
	MarkSucceeded(ctx context.Context, reference string) (Outcome, error)
}

type Outcome string

const (
	Paid                Outcome = "paid"
	AlreadySettled      Outcome = "already-settled"
	OrderWasAlreadyPaid Outcome = "order-was-already-paid"
	Unknown             Outcome = "unknown"
	Failed              Outcome = "failed"
	Mismatch            Outcome = "mismatch"
)

type Service struct {
	store     Store
	orders    Orders
	users     Users
	provider  Provider
	publicURL string
	log       *slog.Logger
}

func NewService(store Store, orders Orders, users Users, provider Provider, publicURL string, log *slog.Logger) *Service {
	return &Service{store: store, orders: orders, users: users, provider: provider, publicURL: publicURL, log: log}
}

type Checkout struct {
	Reference   string
	CheckoutURL string
}

func (s *Service) StartCheckout(ctx context.Context, actor auth.Identity, orderID int64) (Checkout, error) {
	order, err := s.orders.Get(ctx, actor, orderID) // 404 unless it's actor's order
	if err != nil {
		return Checkout{}, err
	}
	if order.PaidAt != nil {
		return Checkout{}, ErrAlreadyPaid
	}
	user, err := s.users.Find(ctx, actor.UserID)
	if err != nil {
		return Checkout{}, err
	}

	reference := "mp-" + strconv.FormatInt(order.ID, 10) + "-" + rand.Text()
	if err := s.store.Create(ctx, order.ID, reference, order.Total); err != nil {
		return Checkout{}, err
	}
	link, err := s.provider.StartCheckout(ctx, user.Email, order.Total, reference, s.publicURL+"/payment-done")
	if err != nil {
		return Checkout{}, err
	}
	return Checkout{Reference: reference, CheckoutURL: link}, nil
}
```

(`Order` gains `PaidAt *time.Time`, scanned from `paid_at` like `CustomerID` in lesson 12.)

Look at what `StartCheckout` reuses. `orders.Get(ctx, actor, orderID)` already hides other customers' orders as 404 (lesson 13), so Bayo can't start paying for Ada's order. And the amount comes from **our** database, `order.Total`, never from the request: there's no request body at all, so a client that sends `{"amount": 100}` has nowhere to put it.

The reference is `mp-`, the order ID, and lesson 7's `rand.Text()`. Paystack only allows letters, digits, `-`, `.` and `=` in a reference, and `rand.Text` uses only capital letters and digits. The order ID makes it readable in Paystack's dashboard; the random part makes every attempt unique, so Ada's second try doesn't clash with her first.

`payments` imports `orders` and `auth`. Nothing imports `payments` except `app` and `run`, so the arrows still point one way.

### Settling: the one place a payment becomes paid

```go
// Settle is the ONE place a payment is marked succeeded. The webhook and the
// verify call both end here, and it is safe to call any number of times.
func (s *Service) Settle(ctx context.Context, reference string, seen Seen) (Outcome, error) {
	p, err := s.store.FindByReference(ctx, reference)
	if errors.Is(err, ErrPaymentNotFound) {
		s.log.Warn("payment for an unknown reference", "reference", reference)
		return Unknown, nil
	}
	if err != nil {
		return "", err
	}
	if !seen.Succeeded {
		return Failed, s.store.MarkFailed(ctx, reference)
	}
	if seen.Currency != "NGN" || seen.Amount != p.Amount {
		s.log.Error("PAYMENT AMOUNT MISMATCH", "reference", reference,
			"expected", p.Amount, "got", seen.Amount, "currency", seen.Currency)
		return Mismatch, nil
	}
	outcome, err := s.store.MarkSucceeded(ctx, reference)
	if outcome == OrderWasAlreadyPaid {
		s.log.Error("order paid twice, refund needed", "reference", reference, "order", p.OrderID)
	}
	return outcome, err
}
```

This is the most important function in the lesson. It checks three things before believing a "success":

1. **We know this reference.** A webhook for a payment we never started gets logged and ignored.
2. **The currency and amount are exactly what we asked for.** If someone found a way to pay ₦30 for a ₦3,000 order, this is where it stops. A mismatch is logged at `Error` level, because it should never happen and a person must look.
3. **It hasn't already been counted.** That's inside `MarkSucceeded`, next.

And at the end, one awkward case. Ada opens checkout in two tabs and pays in both. Both succeed at Paystack; she's paid twice. Our database can't undo that, so we log "refund needed" and someone refunds the second payment from the Paystack dashboard. (Automating refunds is a good practice once lesson 18's jobs exist.)

`Settle` never returns an error for "unknown", "failed" or "mismatch". Those are answers, not failures: the webhook was received and understood. Only a real problem, like the database being down, is an error, and that's what makes Paystack retry later.

`internal/payments/postgres.go`, the method that matters:

```go
func (s *PostgresStore) MarkSucceeded(ctx context.Context, reference string) (Outcome, error) {
	outcome := AlreadySettled
	err := pgx.BeginFunc(ctx, s.pool, func(tx pgx.Tx) error {
		var orderID int64
		err := tx.QueryRow(ctx, `
			UPDATE payments SET status = 'succeeded', settled_at = now()
			 WHERE reference = $1 AND status = 'started'
			RETURNING order_id`, reference).Scan(&orderID)
		if errors.Is(err, pgx.ErrNoRows) {
			return nil // someone settled it first; nothing to do
		}
		if err != nil {
			return err
		}

		tag, err := tx.Exec(ctx, "UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL", orderID)
		if err != nil {
			return err
		}
		outcome = Paid
		if tag.RowsAffected() == 0 {
			outcome = OrderWasAlreadyPaid
		}
		return nil
	})
	return outcome, err
}
```

The guarded `UPDATE`, for the fourth time in this subject. `WHERE status = 'started'` means only the **first** caller changes the row. If the webhook and the verify call arrive at the same instant, Postgres locks the row for one, and the other finds the status already `succeeded` and updates nothing. No double counting, without any "check, then update" race. The transaction makes the payment and the order change together, or not at all.

The other methods (`Create`, `FindByReference` returning `ErrPaymentNotFound` for no rows, and `MarkFailed` with `WHERE status = 'started'`) are plain pgx like lesson 8. Write them in the practice.

### The route

`internal/payments/handlers.go`:

```go
func (h *Handler) Register(mux *http.ServeMux, idempotent func(http.Handler) http.Handler) {
	mux.Handle("POST /v2/orders/{id}/payments",
		auth.RequireUser(idempotent(httpx.HandlerFunc(h.start))))
	mux.Handle("GET /v2/payments/{reference}", auth.RequireUser(httpx.HandlerFunc(h.check)))
}

type checkoutV2 struct {
	Reference   string `json:"reference"`
	CheckoutURL string `json:"checkoutUrl"`
}

func (h *Handler) start(w http.ResponseWriter, r *http.Request) error {
	who, err := auth.Current(r.Context())
	if err != nil {
		return err
	}
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	c, err := h.svc.StartCheckout(r.Context(), who, id)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusCreated, checkoutV2{Reference: c.Reference, CheckoutURL: c.CheckoutURL})
}
```

`idempotent` is lesson 15's `idempotency.Require`, so a retried "Pay" tap gets the same checkout link back instead of starting a second payment. (It needs a body to fingerprint; an empty one is fine, and hashes the same every time.)

```bash
curl -s -X POST localhost:8080/v2/orders/42/payments \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: pay-42-first-try"
```

```json
{
  "data": {
    "reference": "mp-42-K7Q3VJXN2MZ4WQ6R5T7YB3HDAE",
    "checkoutUrl": "https://checkout.paystack.com/abc123xyz"
  }
}
```

Open that link in a browser and you'll see Paystack's test checkout. Paystack's docs list the test cards that succeed or fail. Pay with a successful one. Paystack now wants to tell us about it, which brings us to the webhook.

## Step 5: receiving the webhook
<!-- bite: ddcf1b97-15da-4910-9872-196a9d8f6faa -->

When the payment succeeds, Paystack sends a POST to the webhook URL you set in its dashboard (Settings → API Keys & Webhooks). The body looks like this, trimmed:

```json
{
  "event": "charge.success",
  "data": {
    "id": 4099260516,
    "reference": "mp-42-K7Q3VJXN2MZ4WQ6R5T7YB3HDAE",
    "amount": 300000,
    "currency": "NGN",
    "status": "success"
  }
}
```

And one header that matters: `x-paystack-signature`. Paystack works it out as the **HMAC SHA-512** of the exact body bytes, using your secret key, written as hex. We work out the same thing. If they match, only someone with our secret key could have made this request, and that's Paystack.

### No raw body problem in Go

In Express, this is the hard part: the JSON parser runs for every request, reads the body, turns it into an object and throws the bytes away, so the webhook route has to be mounted before it, with a special raw parser. And you can't rebuild the bytes from the object: `{"event": "charge.success"}` with a space and without one are different bytes, with different signatures.

In Go, there's no such problem. Nothing reads a body unless your handler does. The body is just bytes until **you** decide to decode it, so the webhook handler reads the bytes, checks the signature on them, and only then decodes those same bytes. Lesson 6's design, where each handler decodes its own body, pays off here without you doing anything.

### Its own small chain

There's one thing to arrange, though. Our chain from lesson 14 runs the **rate limit** on every request, per address. Paystack sends from a few addresses, and on a busy lunch hour, hundreds of payments' webhooks from those same few addresses would hit the limit, and we'd start refusing Paystack. CORS and `Authenticate` mean nothing here either: Paystack isn't a browser, and it has no login. The signature is this route's protection.

So `app.New` grows a **root mux** with two doors, each with its own chain:

```go
func New(d Deps) http.Handler {
	api := http.NewServeMux()
	// ... everything from before goes on api ...

	hooks := http.NewServeMux()
	payments.NewWebhooks(d.Payments, d.PaystackSecret, d.ReceivedEvents).Register(hooks)

	root := http.NewServeMux()
	root.Handle("/webhooks/", httpx.Chain(httpx.MuxProblems(hooks),
		httpx.RequestID, httpx.LogRequests(d.Logger), httpx.RecoverPanic))
	root.Handle("/", httpx.Chain(httpx.MuxProblems(api),
		httpx.RequestID, httpx.LogRequests(d.Logger), httpx.RecoverPanic,
		httpx.SecurityHeaders, httpx.CORS(d.CORS),
		httpx.RateLimit(d.GeneralLimit, d.ClientIP), auth.Authenticate(d.Tokens)))
	return root
}
```

`/webhooks/` is more specific than `/`, so webhooks go through the short chain: request IDs, logging and panic recovery, which every request deserves, and nothing else. Everything else goes through the full one. It's lesson 10's "a mux inside a mux" again, this time to give two groups of routes different middleware.

It also lives outside `/v1` and `/v2`. Our API versions describe *our* shapes; this route receives Paystack's shape, which we don't control.

### Checking the signature

`internal/httpx/signatures.go`, since our own outgoing webhooks will need the same:

```go
package httpx

import (
	"crypto/hmac"
	"encoding/hex"
	"hash"
)

// HMACHex is the hex HMAC of message with secret, using the hash h (sha256.New, sha512.New).
func HMACHex(h func() hash.Hash, secret string, message []byte) string {
	mac := hmac.New(h, []byte(secret))
	mac.Write(message)
	return hex.EncodeToString(mac.Sum(nil))
}

// SameHex compares two hex signatures in constant time.
func SameHex(a, b string) bool {
	x, errX := hex.DecodeString(a)
	y, errY := hex.DecodeString(b)
	return errX == nil && errY == nil && len(x) > 0 && hmac.Equal(x, y)
}
```

Why not `a == b`? Because `==` stops at the first different character. A wrong signature that starts with the right three characters takes a tiny bit longer to reject than one that's wrong from the first. With enough attempts and careful timing, an attacker can use that difference to discover the right signature one character at a time. `hmac.Equal` always compares every byte, so it takes the same time whatever the answer. It's `subtle.ConstantTimeCompare` from lesson 12 with a friendlier name. `len(x) > 0` refuses an empty signature, which would otherwise "match" an empty one.

### The webhook handler

`internal/payments/webhooks.go`:

```go
package payments

import (
	"context"
	"crypto/sha512"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"mamaput/internal/apperr"
	"mamaput/internal/httpx"
	"mamaput/internal/money"
)

type ReceivedEvents interface {
	Has(ctx context.Context, provider, key string) (bool, error)
	Record(ctx context.Context, provider, key string) error
}

type Webhooks struct {
	svc      *Service
	secret   string
	received ReceivedEvents
}

func NewWebhooks(svc *Service, secret string, received ReceivedEvents) *Webhooks {
	return &Webhooks{svc: svc, secret: secret, received: received}
}

func (h *Webhooks) Register(mux *http.ServeMux) {
	mux.Handle("POST /webhooks/paystack", httpx.HandlerFunc(h.paystack))
}

var errBadSignature = apperr.New(apperr.Unauthenticated, "bad-webhook-signature", "The webhook signature is not valid.")

func (h *Webhooks) paystack(w http.ResponseWriter, r *http.Request) error {
	// 1. Is it really from Paystack? Check the exact bytes, before anything else.
	body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, 100<<10))
	if err != nil {
		return apperr.New(apperr.TooLarge, "body-too-large", "The webhook body is too large.")
	}
	if !httpx.SameHex(httpx.HMACHex(sha512.New, h.secret, body), r.Header.Get("X-Paystack-Signature")) {
		return errBadSignature
	}

	// 2. Only now, decode it.
	var event struct {
		Event string          `json:"event"`
		Data  json.RawMessage `json:"data"`
	}
	if err := json.Unmarshal(body, &event); err != nil {
		return apperr.New(apperr.Invalid, "bad-webhook-body", "Unexpected webhook body.")
	}

	// 3. Events we don't handle: say "thanks", or Paystack keeps resending them.
	if event.Event != "charge.success" {
		w.WriteHeader(http.StatusOK)
		return nil
	}
	var charge struct {
		ID        int64  `json:"id"`
		Reference string `json:"reference"`
		Amount    int64  `json:"amount"`
		Currency  string `json:"currency"`
		Status    string `json:"status"`
	}
	if err := json.Unmarshal(event.Data, &charge); err != nil || charge.ID == 0 || charge.Reference == "" {
		return apperr.New(apperr.Invalid, "bad-webhook-body", "Unexpected charge in webhook.")
	}
	key := fmt.Sprintf("%s:%d", event.Event, charge.ID)

	// 4. Seen it already? Then we're done.
	seen, err := h.received.Has(r.Context(), "paystack", key)
	if err != nil {
		return err
	}
	if seen {
		w.WriteHeader(http.StatusOK)
		return nil
	}

	// 5. Do the work (safe to repeat), THEN record it.
	if _, err := h.svc.Settle(r.Context(), charge.Reference, Seen{
		Succeeded: charge.Status == "success", Amount: money.Kobo(charge.Amount), Currency: charge.Currency,
	}); err != nil {
		return err
	}
	if err := h.received.Record(r.Context(), "paystack", key); err != nil {
		return err
	}
	w.WriteHeader(http.StatusOK)
	return nil
}
```

Read it top to bottom; the order is the security.

1. **Signature first, before anything else.** Before decoding, before looking anything up. An unsigned request gets a 401 and costs us one hash. The body is capped at 100 KB, because even checking a signature means reading the body, and a stranger could send gigabytes.
2. **Decode only after.** We never decode bytes from a stranger. `json.RawMessage` keeps `data` as raw bytes until we know which event it is, so each event can decode it into its own shape.
3. **Answer 200 to events we don't care about.** Paystack sends other events too: transfers, refunds, subscriptions. If we answered 404, Paystack would think delivery failed and retry for days.
4. **Skip what we've handled.** Paystack's events don't carry their own event ID, so we make a key from the event name and the charge's ID, which is unique per transaction.
5. **Work first, record second.** This order is deliberate. If we recorded "handled" first and then crashed before `Settle`, Paystack's retry would be skipped as "seen", and Ada's payment would be lost for ever. Working first means the worst case is doing the work twice, and `Settle` is built to be safe twice (the guarded `UPDATE` from step 4).

Which shows something important: the received-events table is a shortcut, not the real protection. The real protection is that `Settle` is idempotent by itself. The table just saves us repeating work. Whenever you handle a webhook, ask "what if this exact one arrives twice, at the same time?", and make sure the answer is "nothing bad".

Notice also that this route doesn't use lesson 15's `idempotency.Require`. That middleware needs a logged-in user and a key the client chose. Paystack has neither; the charge ID is its natural key, and `Settle` is safe to repeat anyway.

The received-events store is two small queries: `Has` is `SELECT EXISTS (SELECT 1 FROM webhook_events_received WHERE provider = $1 AND event_key = $2)`, and `Record` is an `INSERT ... ON CONFLICT DO NOTHING`. Write them in `internal/payments/postgres.go`.

### Answer fast

Paystack waits only a short time for our 200. If we're slow, it counts as failed and sends it again. Our handler does a few quick queries, so we're fine. But if handling a payment ever means sending an email, a receipt PDF and a notification, don't do it here. Record the payment, answer 200, and do the slow work afterwards. That's exactly what lesson 18 is for.

## Step 6: testing webhooks on your own laptop
<!-- bite: 10c0483b-d261-44d1-a8b0-4df6a38fed78 -->

Paystack's servers can't reach `http://localhost:8080`. That's your laptop, not the internet.

During development, use a **tunnel**: a small program that gives you a public HTTPS address and forwards everything it receives to your laptop. [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] shows how. Start one pointing at port 8080, copy its address, and in Paystack's dashboard (test mode) set the webhook URL to `https://<your-tunnel-address>/webhooks/paystack`. Pay with a test card, and watch the request arrive in your logs.

You can also send yourself a correctly signed webhook, which is handy for checking the signature code without any tunnel:

```bash
BODY='{"event":"charge.success","data":{"id":1,"reference":"mp-42-...","amount":300000,"currency":"NGN","status":"success"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha512 -hmac "$PAYSTACK_SECRET_KEY" | sed 's/^.* //')

curl -si -X POST localhost:8080/webhooks/paystack \
  -H "Content-Type: application/json" -H "X-Paystack-Signature: $SIG" \
  --data "$BODY" | head -1
```

`openssl dgst -sha512 -hmac` makes the same HMAC our Go code makes; `sed 's/^.* //'` keeps only the hex at the end of its output. Use a real reference from step 4 instead of `mp-42-...`, and the amount of that order. Then send it again with one character of `$BODY` changed after signing: you should get the 401.

## Step 7: the backup, verifying ourselves
<!-- bite: ab8667f6-1824-45ed-97ca-b317fcdc629f -->

Webhooks are reliable, not perfect. Our server might be down for the days Paystack keeps retrying (it happens, though rarely). Or a setting in the dashboard might be wrong. So we add a second path to the truth: asking Paystack directly.

When Ada lands back on our site, her app calls `GET /v2/payments/{reference}`, and the service does:

```go
func (s *Service) Check(ctx context.Context, actor auth.Identity, reference string) (Payment, error) {
	p, err := s.store.FindByReference(ctx, reference)
	if err != nil {
		return Payment{}, err
	}
	if _, err := s.orders.Get(ctx, actor, p.OrderID); err != nil {
		return Payment{}, ErrPaymentNotFound // not Ada's: the same 404 as "no such payment"
	}
	if p.Status == StatusStarted {
		seen, err := s.provider.Verify(ctx, reference)
		if err != nil {
			return Payment{}, err
		}
		if _, err := s.Settle(ctx, reference, seen); err != nil {
			return Payment{}, err
		}
		return s.store.FindByReference(ctx, reference)
	}
	return p, nil
}
```

The browser's visit is only a *nudge* to go and ask Paystack. The answer comes from `Verify`, using our secret key, from our server, and it goes through the same `Settle` as the webhook. So whether the webhook or the verify call gets there first, the order is paid once, with the same checks.

Someone else's payment is the same `ErrPaymentNotFound` as no payment at all: lesson 13's rule, so references can't be probed.

For payments still `started` after an hour, a scheduled job can run the same verify for each. That's the safety net under the safety net, and it's one of the jobs in lesson 18.

## Step 8: only paid orders get cooked
<!-- bite: 121d8fb2-8f7f-4b88-8a67-143dbb3d9e4f -->

Now Mama's rule: the kitchen doesn't cook unpaid orders. In the orders service's `SetStatus`, after loading the order and before the change:

```go
var ErrNotPaid = apperr.New(apperr.RuleBroken, "order-not-paid", "This order hasn't been paid for yet.")

if to == StatusReady && order.PaidAt == nil {
	return Order{}, ErrNotPaid
}
```

The kitchen screen in lesson 20 will show only paid orders, but the rule lives here, in the service, where no screen can skip it.

What about v1's anonymous orders, which have no customer and so can't start a checkout? They're paid at the counter, in cash, as before: a staff route `POST /v2/orders/{id}/paid-in-cash` (guarded by a new `order:mark-paid` action) sets `paid_at`. Write it in the practice; it's lesson 13's policy, one more row.

## Step 9: sending our own webhooks
<!-- bite: ec025588-e874-4a19-b16a-285ceba1b653 -->

Now the other direction. When the kitchen marks order 42 ready, Okada Riders should hear about it at once. They've given us a URL, and we've agreed on a shared secret.

Sending a webhook is more than one `http.Post`. Everything we needed from Paystack, Okada Riders needs from us:

1. **A signature**, so they know it's really from us.
2. **A timestamp in the signature**, so nobody can record one of our webhooks and replay it next week.
3. **An event ID**, so they can ignore duplicates.
4. **Retries**, because their server will sometimes be down, and they're relying on at-least-once delivery.

### Writing it down first

When the order becomes ready, we don't call Okada Riders right there. We write the webhook into `webhook_deliveries` and move on. A separate sender picks it up. `internal/webhooks/deliveries.go`:

```go
// Package webhooks sends signed webhooks to partners, from a queue in Postgres.
package webhooks

import (
	"context"
	"encoding/json"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Delivery struct {
	ID        string
	URL       string
	EventType string
	Payload   json.RawMessage
	Attempts  int
	CreatedAt time.Time
}

type Deliveries struct{ pool *pgxpool.Pool }

func NewDeliveries(pool *pgxpool.Pool) *Deliveries { return &Deliveries{pool: pool} }

func (d *Deliveries) Enqueue(ctx context.Context, url, eventType string, data any) error {
	payload, err := json.Marshal(data)
	if err != nil {
		return err
	}
	_, err = d.pool.Exec(ctx,
		"INSERT INTO webhook_deliveries (url, event_type, payload) VALUES ($1, $2, $3)",
		url, eventType, payload)
	return err
}
```

The orders service gets a small interface for it, `type Notifier interface { OrderReady(ctx context.Context, o Order) error }`, so `orders` doesn't import `webhooks`. `run` gives it a little adapter that calls `Enqueue(ctx, okadaURL, "order.ready", ...)`. In `SetStatus`, after a successful change to `ready`:

```go
if to == StatusReady {
	if err := s.notify.OrderReady(ctx, order); err != nil {
		return Order{}, err
	}
}
```

and the adapter's payload is:

```go
map[string]any{
	"orderId":  strconv.FormatInt(o.ID, 10),
	"dishId":   strconv.FormatInt(o.DishID, 10),
	"quantity": o.Quantity,
	"readyAt":  time.Now().UTC(),
}
```

Why write it down instead of sending at once? Three reasons. The cook's tap on "ready" doesn't wait for Okada Riders' server. If their server is down, the webhook isn't lost; it's sitting in a table. And a restart of our app loses nothing, because the queue is in Postgres, not in memory.

Notice what's **not** in the payload: Ada's name, email or phone. The rider needs to know an order is ready at Mama's; they don't need her details until a delivery is booked, and then through Okada Riders' own system. Send another company only what it needs. Everything you send, you can't take back.

(One honest gap: the status change and the `Enqueue` are two separate queries. If the app crashed exactly between them, the order would be ready and the webhook never written. Putting both in one transaction fixes it, and doing that properly, for events between services, is the **outbox** in lesson 25.)

### The sender

`internal/webhooks/sender.go`:

```go
package webhooks

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log/slog"
	"math/rand/v2"
	"net/http"
	"strconv"
	"time"

	"mamaput/internal/httpx"
)

const maxAttempts = 15

func backoff(attempts int) time.Duration {
	base := 30 * time.Second << (attempts - 1) // 30 s, 1 min, 2 min, 4 min ...
	if base > 6*time.Hour || base <= 0 {
		base = 6 * time.Hour
	}
	return base + rand.N(base/5) // plus up to 20% jitter
}

type Sender struct {
	deliveries *Deliveries
	secret     string
	client     *http.Client
	log        *slog.Logger
}

func NewSender(d *Deliveries, secret string, log *slog.Logger) *Sender {
	client := &http.Client{
		Timeout: 5 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse // never follow a redirect somewhere we didn't agree to send
		},
	}
	return &Sender{deliveries: d, secret: secret, client: client, log: log}
}

func (s *Sender) send(ctx context.Context, d Delivery) error {
	body, err := json.Marshal(map[string]any{
		"id": d.ID, "type": d.EventType, "createdAt": d.CreatedAt, "data": d.Payload,
	})
	if err != nil {
		return err
	}
	ts := strconv.FormatInt(time.Now().Unix(), 10)
	sig := httpx.HMACHex(sha256.New, s.secret, append([]byte(ts+"."), body...))

	req, err := http.NewRequestWithContext(ctx, "POST", d.URL, bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("MamaPut-Event-Id", d.ID)
	req.Header.Set("MamaPut-Signature", "t="+ts+",v1="+sig)

	res, err := s.client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	if res.StatusCode < 200 || res.StatusCode >= 300 {
		return fmt.Errorf("answered %d", res.StatusCode)
	}
	return nil
}

// RunOnce sends every delivery that's due now. Tests call it directly.
func (s *Sender) RunOnce(ctx context.Context) error {
	due, err := s.deliveries.ClaimDue(ctx, 10)
	if err != nil {
		return err
	}
	for _, d := range due {
		err := s.send(ctx, d)
		if err == nil {
			if err := s.deliveries.MarkDelivered(ctx, d.ID); err != nil {
				return err
			}
			continue
		}
		giveUp := d.Attempts >= maxAttempts
		var retryIn time.Duration
		if !giveUp {
			retryIn = backoff(d.Attempts)
		}
		if err := s.deliveries.MarkFailed(ctx, d.ID, err.Error(), giveUp, retryIn); err != nil {
			return err
		}
		s.log.Warn("webhook delivery failed", "id", d.ID, "attempts", d.Attempts, "giving_up", giveUp, "error", err)
	}
	return nil
}

// Run sends due deliveries every few seconds until ctx is cancelled.
func (s *Sender) Run(ctx context.Context, every time.Duration) {
	ticker := time.NewTicker(every)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := s.RunOnce(ctx); err != nil {
				s.log.Error("webhook sender", "error", err)
			}
		}
	}
}
```

A lot of small decisions, each one learned the hard way by someone:

1. **What gets signed is `timestamp.body`**, not just the body. The receiver checks the timestamp is recent, so a webhook recorded today is useless next week, even though its signature is real.
2. **`MamaPut-Event-Id`** is the delivery's ID, the same on every retry. That's what lets Okada Riders skip duplicates.
3. **Only 2xx counts.** A redirect, a 404, a 500: all failures. Go's client follows redirects by itself, up to ten; `CheckRedirect` returning `http.ErrUseLastResponse` stops that, so a 302 comes back to us as a 302, and counts as a failure.
4. **A 5-second timeout**, on a client of its own. A slow partner mustn't hold up the queue.
5. **Backoff that grows**: 30 seconds, then 1 minute, 2, 4, ... up to 6 hours between tries. If their server is down for an hour, hammering it every 5 seconds helps nobody, and may be part of why it's down. `30 * time.Second << (attempts - 1)` doubles by shifting; the `base <= 0` check catches the shift overflowing for very large numbers.
6. **Jitter.** If 500 webhooks all failed at the same moment, without jitter they'd all retry at the same moment too, and knock the partner over again. `rand.N` from `math/rand/v2` adds a random extra. It's `math/rand`, not `crypto/rand`, on purpose: jitter needs to be spread out, not secret.
7. **Give up eventually**, and log it, so a person can look. Fifteen attempts, with the gaps capped at 6 hours, take about a day and a half.
8. **`Run` stops when its context is cancelled.** `select` waits for whichever comes first: the next tick, or `ctx.Done()`. Lesson 28 cancels that context when the server shuts down, so the sender stops cleanly between deliveries.

### Claiming work safely

`ClaimDue` is where two copies of our app could trip over each other. Run two servers (we will, in lesson 28), and both senders wake up every 5 seconds. Without care, both pick the same webhook and send it twice.

```go
func (d *Deliveries) ClaimDue(ctx context.Context, limit int) ([]Delivery, error) {
	rows, err := d.pool.Query(ctx, `
		UPDATE webhook_deliveries
		   SET attempts = attempts + 1,
		       next_attempt_at = now() + interval '1 minute'
		 WHERE id IN (
		       SELECT id FROM webhook_deliveries
		        WHERE delivered_at IS NULL AND next_attempt_at <= now()
		        ORDER BY next_attempt_at
		        LIMIT $1
		        FOR UPDATE SKIP LOCKED)
		RETURNING id, url, event_type, payload, attempts, created_at`, limit)
	if err != nil {
		return nil, err
	}
	return pgx.CollectRows(rows, func(row pgx.CollectableRow) (Delivery, error) {
		var x Delivery
		err := row.Scan(&x.ID, &x.URL, &x.EventType, &x.Payload, &x.Attempts, &x.CreatedAt)
		return x, err
	})
}
```

Two things make this safe:

1. **`FOR UPDATE SKIP LOCKED`** locks the rows this sender picks, and tells any other sender looking at the same moment to *skip* locked rows instead of waiting for them. So two senders take different webhooks.
2. **Pushing `next_attempt_at` a minute forward** is a lease: "this is mine for a minute". If our server dies mid-send, the row isn't stuck for ever. A minute later it's due again, and someone else picks it up.

`pgx.CollectRows` runs the function for each row and gathers the results into a slice, closing the rows for you: a shorter way to write lesson 9's `for rows.Next()` loop. A `uuid` column scans straight into a `string`.

`MarkDelivered` sets `delivered_at = now()`. `MarkFailed` saves `last_error` and sets `next_attempt_at = now() + retryIn`, or, when giving up, to `'infinity'`, Postgres's "later than any date", so it's never picked again but stays in the table for a person to see. Pass `retryIn` to Postgres as `$3 * interval '1 second'` with `retryIn.Seconds()`.

And yes: this is a small, hand-made job queue. In lesson 18 we hand jobs like this to a real queue library, and having built one yourself, you'll know exactly what it does for you.

Start it in `run`, before `ListenAndServe`:

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()
sender := webhooks.NewSender(deliveries, getenv("OKADA_WEBHOOK_SECRET"), logger)
go sender.Run(ctx, 5*time.Second)
```

`go` starts `Run` in its own goroutine, so it ticks away beside the HTTP server. When `run` returns, `cancel()` stops it. (Lesson 28 replaces this with a context that's cancelled when the process is asked to stop.)

### What Okada Riders does with it

They'll ask "how do we check your signature?", so write it down for them. This is roughly the code on *their* side, and writing it is a good way to check your own design:

```go
func FromMamaPut(body []byte, header, secret string, now time.Time) bool {
	var ts, sig string
	for _, part := range strings.Split(header, ",") {
		k, v, _ := strings.Cut(part, "=")
		switch k {
		case "t":
			ts = v
		case "v1":
			sig = v
		}
	}
	sent, err := strconv.ParseInt(ts, 10, 64)
	if err != nil || now.Sub(time.Unix(sent, 0)).Abs() > 5*time.Minute {
		return false // missing, or older than 5 minutes: a replay
	}
	return httpx.SameHex(httpx.HMACHex(sha256.New, secret, []byte(ts+"."+string(body))), sig)
}
```

Then they check `MamaPut-Event-Id` against the IDs they've already seen, answer 200 quickly, and do their work. It's everything we did for Paystack, from the other side. Good webhook design is just being the sender you'd want to receive from.

One more thing worth knowing. Here the URL comes from our own settings. Some products let *customers* type in their own webhook URL. Then you must check it doesn't point inside your own network, or someone sets their URL to `http://169.254.169.254/` or `http://localhost:5432` and makes your server attack itself. That's called **SSRF** (server-side request forgery), and lesson 14's rule applies: treat the URL as hostile input. In Go, the safe way is a `net.Dialer` with a `Control` function that refuses private addresses *after* the name is looked up, because a friendly-looking name can point anywhere.

## Step 10: a pretend partner, for trying it
<!-- bite: ea88fb14-7012-46ab-ade6-f41a54994d2b -->

To watch our webhooks arrive, run a tiny partner on your laptop. `cmd/fake-okada/main.go`:

```go
package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("POST /hooks/mama-put", func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		fmt.Printf("%s %s\n%s\n\n", r.Header.Get("MamaPut-Event-Id"), r.Header.Get("MamaPut-Signature"), body)
	})
	log.Fatal(http.ListenAndServe("localhost:9090", nil))
}
```

```bash
go run ./cmd/fake-okada
```

(It's a toy on your own machine, so the lesson 1 rule about timeouts doesn't apply. Never ship it.) Pay for an order, mark it ready as staff, and within 5 seconds the fake partner prints the event. Stop the fake partner, mark another order ready, wait a minute, start it again, and watch the retry arrive with the same event ID.

## Step 11: testing it
<!-- bite: 203336e6-ffa8-468f-9f6d-7c4aa163e481 -->

Lesson 16's tools cover all of this without Paystack or Okada Riders running.

**Paystack is an `httptest.NewServer`.** The real `Paystack` type talks to it, so the request-building and response-checking code is tested too:

```go
func TestVerify(t *testing.T) {
	fake := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer sk_test_x" {
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		fmt.Fprint(w, `{"status":true,"data":{"status":"success","amount":300000,"currency":"NGN"}}`)
	}))
	defer fake.Close()

	p := NewPaystack(fake.URL, "sk_test_x", fake.Client())
	seen, err := p.Verify(t.Context(), "mp-1-ABC")
	if err != nil || !seen.Succeeded || seen.Amount != 300000 {
		t.Fatalf("got %+v, %v", seen, err)
	}
}
```

Add rows for a 500 (`payment-provider-error`), a body that isn't JSON (`payment-provider-bad-response`), and a server that never answers, with a client `Timeout` of 50 ms (`payment-provider-unreachable`).

**For the app tests, the provider is a fake** that answers from a map, and `apptest` gets `a.PaystackSecret` so tests can sign webhooks exactly as Paystack would:

```go
func TestWebhookPaysOnceHoweverOftenItArrives(t *testing.T) {
	a := apptest.New(t)
	tok := a.Login(t, auth.RoleCustomer)
	orderID, total := a.PlaceOrderAs(t, tok)
	ref := a.StartCheckout(t, tok, orderID)

	body := fmt.Sprintf(`{"event":"charge.success","data":{"id":7,"reference":%q,"amount":%d,"currency":"NGN","status":"success"}}`, ref, total)
	sig := httpx.HMACHex(sha512.New, a.PaystackSecret, []byte(body))

	var wg sync.WaitGroup
	for range 3 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			rec := a.Do(t, "POST", "/webhooks/paystack", body, apptest.Header("X-Paystack-Signature", sig))
			if rec.Code != 200 {
				t.Errorf("status %d: %s", rec.Code, rec.Body)
			}
		}()
	}
	wg.Wait()

	if !a.OrderIsPaid(t, orderID) {
		t.Error("order not paid")
	}
}
```

Note `body` is a **string**, and `a.Do` sends a string exactly as given, so the bytes we signed are the bytes that arrive.

And the tests that matter just as much:

1. A wrong signature gives 401, and the order stays unpaid.
2. One changed character in a signed body gives 401.
3. An amount one kobo short is logged as a mismatch, and the order stays unpaid.
4. An event we don't handle (`transfer.success`) gets 200 and changes nothing.
5. Marking an unpaid order `ready` gives 422 `order-not-paid`.
6. For the sender: an `httptest.NewServer` partner that answers 500 twice and then 200 gets exactly one successful delivery, with the same `MamaPut-Event-Id` all three times. Call `RunOnce` directly instead of waiting for the ticker (and move `next_attempt_at` back in the test database between runs). That's why it's exported.
7. `FromMamaPut` refuses a correct signature with a timestamp 6 minutes old.

The double-payment race (the webhook and the verify call at the same instant) belongs in the Postgres integration tests, like the last-plate race in lesson 16, because only a real database shows it.

## The Go in this lesson
<!-- bite: ef0ba471-0792-4efe-9eeb-3056d0d5dd9b -->

1. **`http.Client{Timeout: ...}`**: Go's HTTP client. One client is safe to share between goroutines and keeps connections open for reuse, so make it once in `run` and pass it in. Never use `http.DefaultClient` (or `http.Get`) for outside calls: it has no timeout.
2. **`http.NewRequestWithContext(ctx, method, url, body)`** and **`client.Do(req)`**: Build a request that's cancelled with `ctx`, then send it.
3. **`defer res.Body.Close()`**: Always close a response body, or the connection can't be reused, and your program slowly runs out of them.
4. **`url.PathEscape(reference)`**: Makes text safe to put inside a URL path, so a reference with `/` or `?` in it can't change which URL we call.
5. **`fmt.Errorf("%w: %v", ourErr, theirErr)`**: Wraps our error (`%w`, so `errors.As` finds it) and adds theirs as plain text (`%v`) for the logs.
6. **Anonymous structs**, `var out struct { Status bool ... }`: A struct type written in place, used once, for decoding one response. No need to name what only one function uses.
7. **`json.RawMessage`**: Keeps part of a JSON document as raw bytes, to decode later into a type you choose once you know what it is.
8. **`hmac.New(sha512.New, key)`** and **`hmac.Equal`**: An HMAC is a `hash.Hash`; write the message into it and `Sum(nil)` gives the code. `sha512.New` is passed as a **function value**, so `hmac` can make fresh hashes inside.
9. **`hash.Hash`** and **`func() hash.Hash`**: The standard interface every hash satisfies, and the shape of a function that makes one. That's how `HMACHex` works with SHA-256 and SHA-512 alike.
10. **`30 * time.Second << (attempts - 1)`**: A `time.Duration` is a number of nanoseconds, so it can be shifted like any integer. Shifting left by one doubles it.
11. **`math/rand/v2`** and **`rand.N(d)`**: The newer random package. `rand.N` gives a random value from 0 up to (not including) `d`, and works on durations directly.
12. **`CheckRedirect` returning `http.ErrUseLastResponse`**: Tells the client "don't follow; give me the redirect itself".
13. **`time.NewTicker`**, **`select`** and **`ctx.Done()`**: A ticker sends on its channel `C` every period. `select` waits on several channels and runs the case for whichever is ready first.
14. **`go sender.Run(ctx, 5*time.Second)`**: Starts a function in a new goroutine and carries on at once.
15. **`pgx.CollectRows(rows, fn)`**: Turns query rows into a slice, one call of `fn` per row, and closes the rows.
16. **`httptest.NewServer(handler)`** and **`fake.Client()`**: A real server on a random local port, for testing code that makes HTTP calls; `Client()` is a client already set up to talk to it.

## Your project so far
<!-- bite: 0ca2beef-0aca-48cc-9ea5-f21706655939 -->

```text
mama-put/
├── .env                           ← PAYSTACK_SECRET_KEY, PUBLIC_URL, OKADA_WEBHOOK_URL, OKADA_WEBHOOK_SECRET
├── migrations/
│   ├── 011_payments.sql           ← NEW: payments (one row per attempt); orders.paid_at
│   └── 012_webhooks.sql           ← NEW: webhook_events_received; webhook_deliveries (partial index)
├── cmd/
│   ├── api/main.go                ← Paystack client with a timeout, payments service, sender goroutine
│   └── fake-okada/main.go         ← NEW: a pretend partner that prints what it receives (never shipped)
└── internal/
    ├── apperr/apperr.go           ← Upstream kind (502)
    ├── app/app.go                 ← root mux: /webhooks/ with a short chain, everything else with the full one
    ├── httpx/
    │   └── signatures.go          ← NEW: HMACHex, SameHex
    ├── orders/
    │   ├── orders.go              ← Order.PaidAt; ErrNotPaid
    │   └── service.go             ← SetStatus: ready needs paid; Notifier.OrderReady
    ├── payments/                  ← NEW package
    │   ├── payments.go            ← Payment, Seen, Provider, errors
    │   ├── paystack.go            ← StartCheckout, Verify: context, checked answers, calm errors
    │   ├── service.go             ← StartCheckout, Settle (the one place), Check (verify backup)
    │   ├── postgres.go            ← MarkSucceeded (guarded UPDATE in a transaction), received events
    │   ├── handlers.go            ← POST /v2/orders/{id}/payments, GET /v2/payments/{reference}
    │   └── webhooks.go            ← POST /webhooks/paystack: signature, decode, skip, settle, record
    └── webhooks/                  ← NEW package
        ├── deliveries.go          ← Enqueue, ClaimDue (SKIP LOCKED + lease), MarkDelivered, MarkFailed
        └── sender.go              ← signed t.body, event ID, timeout, no redirects, backoff + jitter, Run
```

## Common mistakes
<!-- bite: 5583f962-404f-405c-9d1d-4b6eedfa9bc7 -->

1. **Marking an order paid from the redirect.** Anyone can visit that URL. Only a signed webhook or your own verify call counts.
2. **Taking the amount from the request.** Read it from your database.
3. **Checking the signature on re-encoded JSON.** Sign and check the exact bytes that arrived.
4. **Comparing signatures with `==`.** Use `hmac.Equal`.
5. **`http.DefaultClient` or `http.Get` for outside calls.** No timeout. Build a client with one.
6. **Forgetting `res.Body.Close()`.** Connections leak until the program can't make new ones.
7. **Recording a webhook as handled before handling it.** A crash in between loses it for ever. Work first, record second, and make the work safe to repeat.
8. **Answering 404 or 400 to events you don't handle.** The sender retries for days. Answer 200.
9. **Rate-limiting webhooks per address.** Paystack sends from a few addresses. Give webhooks their own chain, protected by the signature.
10. **Sending partners more than they need.** No customer details in a "ready" webhook.
11. **Retrying at a fixed interval, with no jitter.** You'll hammer a struggling partner, all at once.
12. **Following redirects when sending webhooks.** Stop them, and count them as failures.

## Check your understanding
<!-- bite: b6798a36-f383-448c-89d7-09132eb959fa -->

1. Why can't Mama Put mark an order paid when Ada's browser lands on `/payment-done`?
2. Paystack sends the same `charge.success` three times at once. Follow it through: what stops the order being counted three times?
3. Why does the webhook handler run `Settle` *before* recording the event as received?
4. Express needs special care to get a webhook's raw body. Why doesn't Go?
5. Why is the timestamp inside our outgoing signature, and what does Okada Riders do with it?
6. Two copies of our app run the sender at the same moment. Why don't they send the same webhook twice?

<details>
<summary>Answers, after your attempt</summary>

1. Because the browser is the customer's: anyone can type that URL without paying, and a customer who closes the tab early never visits it. Only Paystack, through a signed webhook or our own verify call, can say a payment happened.
2. All three pass the signature check, and maybe all three find the event not yet recorded. All three call `Settle`. But `MarkSucceeded`'s `UPDATE ... WHERE status = 'started'` changes the row for only one of them; the others find it already `succeeded` and change nothing. The order's `paid_at` is set once.
3. So a crash in between can't lose the payment. If we recorded first and crashed, Paystack's retry would be skipped as "already seen". Working first means the worst case is running `Settle` twice, which is safe.
4. Because nothing in Go reads a request body unless the handler does. There's no app-wide JSON parser that consumes it first; the handler reads the bytes itself, checks the signature on them, and then decodes them.
5. So a recorded webhook can't be replayed later: the signature covers the time it was sent. Okada Riders refuses any webhook whose timestamp is more than 5 minutes from their clock, even if the signature is correct.
6. `FOR UPDATE SKIP LOCKED`: each sender locks the rows it claims, and the other skips locked rows instead of waiting for them. And the claim pushes `next_attempt_at` a minute forward, so even after the lock is released, nobody else picks it up until that lease runs out.

</details>

## Practice
<!-- bite: ef1b7c47-895a-4855-b21e-c9b7ea6c620b -->

1. Write the rest of `payments.PostgresStore`: `Create`, `FindByReference`, `MarkFailed` (guarded by `status = 'started'`), and the received-events `Has` and `Record`. Add `Deliveries.MarkDelivered` and `MarkFailed`.
2. Add `POST /v2/orders/{id}/paid-in-cash` for staff, with a new `order:mark-paid` action in the policy and a row in `TestPermissions`.
3. Write the Paystack tests from step 11, including the one that never answers.
4. Write the sender test: a partner that fails twice then succeeds, and check the event ID is the same each time and `delivered_at` is set once.
5. Add the payment routes to `openapi/v2.yaml`, with a 502 problem response on `POST /v2/orders/{id}/payments`.

**Done when** a test-mode payment marks its order paid through the webhook (with a tunnel) or through `GET /v2/payments/{reference}` (without one); a forged webhook gets 401; the kitchen can't mark an unpaid order ready; `fake-okada` prints a signed `order.ready` event; and `make test` passes.

## Before moving on
<!-- bite: 0f81fae6-8d7a-4e3c-a176-c58081183eac -->

Mama Put API now takes real money. Payments start from our own numbers, become "paid" only on Paystack's signed word or our own check, and count exactly once however many times the news arrives. And Okada Riders hears about every ready order, signed, timestamped and retried until they've got it.

But look at what the sender really is: a loop in our API process, reading a table every 5 seconds. It's fine for one kind of job. Mama now wants more: a receipt email after payment, a reminder if an order sits unpaid for 15 minutes, a nightly sales summary, those leftover-payment checks. Each could be its own little loop, but then we'd be writing a job system by hand, badly. That's background jobs, the next lesson.

## Related
<!-- bite: 50e5ae2b-b831-4ce8-bc3b-37f5b3d735fb -->

- [[backend/frameworks/net-http/18-background-jobs|Next: Background Jobs and Queues]]
- [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] — receiving webhooks on your laptop
- [[backend/frameworks/express/17-payments-and-webhooks|The same lesson in Express]] — where the raw body needs special mounting
- [[backend/frameworks/net-http/15-idempotency|Idempotency]] — why "safe to repeat" is the real protection

## About this lesson
<!-- bite: ac071e25-dd32-41a0-965f-2b235a8c39fb -->

**Level:** Advanced. Lesson 17 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later and pgx v5, against Paystack's test mode. Covers why payments span requests, a provider interface and a Paystack client with timeouts, context and checked answers, a 502 kind, one idempotent `Settle` guarded in SQL, verifying HMAC-SHA512 webhook signatures on raw bytes with `hmac.Equal`, a separate middleware chain for webhooks, the verify call as a backup, paid-before-cooked, and signed outgoing webhooks from a Postgres queue with timestamps, event IDs, `SKIP LOCKED` leases, backoff, jitter and no redirects.
