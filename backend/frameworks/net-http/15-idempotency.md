---
id: c92959bc-988e-4e89-8135-b1679aca6de9
---

# Idempotency

**An operation is idempotent when doing it twice has the same effect as doing it once, and idempotency, for an API, is making sure a request that arrives twice by accident only *happens* once.** Networks drop answers. Phones retry. People double-tap. Without it, "place order" sent twice is two orders and two payments; with it, the second copy just gets the first answer back.

## Before you start
<!-- bite: c8579fa2-2bd6-46ce-9bbe-578e09cb48b3 -->

You should have:

1. Finished [[backend/frameworks/net-http/14-security|lesson 14]], so every v2 order has a logged-in customer.
2. Met the guarded `UPDATE` (lesson 8) and the single-use refresh token (lesson 12). This lesson uses the same trick a third time.

After this lesson you will be able to:

1. Say which HTTP methods are idempotent already, and which need help.
2. Make `POST /v2/orders` safe to retry with the `Idempotency-Key` header.
3. Write a middleware that buffers a handler's answer, stores it, and replays it for retries.
4. Handle the four cases (new, done, still running, reused for a different request) and the crash in between.
5. Back the stored answers with a unique constraint in the same transaction as the order, so a duplicate is impossible even when the first layer fails.

## Where we stopped
<!-- bite: e157b2d2-0853-478f-bdf9-7197d88d0381 -->

Lesson 14 ended with Ada in a tunnel:

1. She taps "Place order". The request reaches us.
2. We take the portions, write the order, and send back `201`.
3. The answer is lost: the train went under a hill.
4. Ada's app waits, gives up, and tries again. A good app *should* retry: most failures are brief.
5. We take the portions again and write a **second** order.

From our side, both requests looked perfectly valid. Nothing in lessons 1 to 14 can tell "Ada wants two plates" from "Ada's phone asked twice". And it doesn't only happen in tunnels: proxies retry, load balancers retry, people double-tap.

## The kid version
<!-- bite: 67f38425-fd5c-44a7-afa2-b3db2df16ed4 -->

Ada sends her little brother to Mama Put with a paper: "1 jollof, for Ada". On the way back, he drops the food. He runs back and hands Mama the same paper again.

If Mama just reads the paper, she cooks and charges a second plate. But Ada's papers are numbered: this one says **"Order slip 7"**. Mama keeps every slip she's served in a box. She checks: "Slip 7? I already served this one. Here's your plate, and you've already paid." No second charge.

The slip number is the **idempotency key**. The box is our database table.

**Where the picture stops working.** Mama would cook a fresh plate. An API **replays the same answer**: the same order, with the same ID, so Ada's phone ends up exactly where it would have been if the first answer had arrived.

## Terms used in this lesson
<!-- bite: d7ec6238-ccab-4b2c-921d-1513dcd8a9ca -->

1. **Idempotent**: This describes an operation where doing it many times has the same effect as doing it once. Setting a light switch to "on" is idempotent; flicking it is not.
2. **Retry**: This is sending the same request again because the first answer didn't arrive, or was an error that might be temporary.
3. **Idempotency key**: This is a unique value the client makes for one action (one tap of "Place order") and sends with every retry of that action, in the `Idempotency-Key` header. A new action gets a new key.
4. **Replay**: This is answering a retry with the stored answer from the first time, instead of doing the work again.
5. **Request fingerprint**: This is a hash of the request's method, path and body, stored with the key, so we can tell if someone reuses a key for a *different* request.
6. **Buffering**: This means collecting a whole answer in memory before sending any of it, instead of sending each piece as it's written.

## Step 1: which methods are already safe?
<!-- bite: e0dfb504-5fa7-42ea-b5c7-f99f31182910 -->

The HTTP rules already say which methods must be idempotent:

1. **GET**: reading the menu twice changes nothing. Idempotent.
2. **PUT**: "set dish 3 to *exactly this*". Doing it twice leaves the same dish. Idempotent.
3. **DELETE**: "remove dish 3". The second time, it's already gone; the *effect* is the same. (The second answer may be 404 instead of 204, and that's fine: idempotency is about the effect, not the answer.)
4. **PATCH**: it depends. `{"status": "ready"}` sent twice is the same; "add one to the quantity" twice is not. Ours only set values, so they're idempotent.
5. **POST**: "create a new order". Twice means two orders. **Not idempotent.**

That's why clients, proxies and libraries happily retry GET, PUT and DELETE, and are careful with POST. Go's own HTTP client does the same: it will quietly resend a GET whose connection broke, and never a POST. Our job is to make the POSTs that matter (placing an order today, paying in lesson 17) safe to retry too.

## Step 2: the plan
<!-- bite: 2f4fca7d-0aeb-4ebb-99e7-6950bfcac414 -->

The client makes a key, usually a UUID, when the customer taps "Place order", and sends it on the first attempt and every retry:

```text
POST /v2/orders
Authorization: Bearer eyJ...
Idempotency-Key: 9b2f6c1e-4a0d-4f5b-8f33-1c7e2a9d5b10
Content-Type: application/json

{"dishId":"1","quantity":2}
```

When it arrives, our middleware does one of four things:

1. **A new key**: claim it, run the handler, store its answer, send it.
2. **A key we've finished**: send the stored answer again, without running anything.
3. **A key still in progress** (the retry arrived before the first one finished): answer `409 Conflict`, "still working on it, try again in a moment".
4. **A key we've seen, with a different body** (same key, now asking for 5 plates): refuse with `422`. Reusing a key for a different request is a bug in the client, and guessing what it meant would be worse.

The key belongs to the **user**: Ada's key `abc` and Bayo's key `abc` are different keys. Otherwise one customer could be replayed another's order, with their name on it.

v2 makes the header **required** on `POST /v2/orders`. Adding a required header is a breaking change, so that's only possible because v2 isn't released yet (lesson 13 used the same window). On a released version, you'd accept it as optional first, and require it in the next version. v1's orders have no customer to own a key, so v1 stays as it is.

## Step 3: the table
<!-- bite: 6058a71c-fb88-495f-9545-a5991e5b2f1a -->

`migrations/010_idempotency.sql`:

```sql
CREATE TABLE idempotency_keys (
  user_id          bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  key              text   NOT NULL,
  request_hash     text   NOT NULL,
  state            text   NOT NULL DEFAULT 'in_progress' CHECK (state IN ('in_progress', 'done')),
  response_status  integer,
  response_headers jsonb,
  response_body    bytea,
  claimed_at       timestamptz NOT NULL DEFAULT now(),
  created_at       timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, key)
);

ALTER TABLE orders ADD COLUMN idempotency_key text;
CREATE UNIQUE INDEX orders_customer_idempotency_idx
  ON orders (customer_id, idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

Two layers, on purpose:

1. **`idempotency_keys`** stores each key and its whole answer (status, headers and body), so we can **replay** it exactly. It works for any route.
2. **The unique index on `orders`** makes a second order with the same customer and key **impossible**, at the database level. If anything ever goes wrong with the first layer (step 6 shows how it can), the database still refuses the duplicate.

The body is `bytea`, Postgres's type for raw bytes, so the replay is byte-for-byte what the first answer was, even an empty body. The headers are `jsonb`, because they're a small map. The index is **partial** (`WHERE idempotency_key IS NOT NULL`), so old orders and v1 orders, which have no key, aren't in it at all.

`claimed_at` is for the crash case in step 6. `created_at` is for cleaning up: nobody retries a tap from last week, so keys can be deleted after a day. Lesson 18's jobs do that.

```bash
make migrate
```

## Step 4: the store
<!-- bite: 55280786-852d-4c13-8fd7-f28c8c38f380 -->

A new package, `internal/idempotency`, because the middleware needs both `httpx` and `auth` (keys belong to users), and `httpx` mustn't import `auth`. `internal/idempotency/store.go`:

```go
// Package idempotency makes retried requests happen only once.
package idempotency

import (
	"context"
	"errors"
	"fmt"
	"net/http"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Response struct {
	Status int
	Header http.Header
	Body   []byte
}

type Record struct {
	RequestHash string
	Done        bool
	Response    Response
}

type PostgresStore struct{ pool *pgxpool.Pool }

func NewPostgresStore(pool *pgxpool.Pool) *PostgresStore { return &PostgresStore{pool: pool} }

// Claim tries to make this request the owner of the key. If it can't, it returns
// what's stored for the key, so the caller can replay it or refuse.
func (s *PostgresStore) Claim(ctx context.Context, userID int64, key, hash string) (bool, Record, error) {
	tag, err := s.pool.Exec(ctx, `
		INSERT INTO idempotency_keys (user_id, key, request_hash)
		VALUES ($1, $2, $3)
		ON CONFLICT (user_id, key) DO UPDATE SET claimed_at = now()
		 WHERE idempotency_keys.state = 'in_progress'
		   AND idempotency_keys.request_hash = EXCLUDED.request_hash
		   AND idempotency_keys.claimed_at < now() - interval '1 minute'`,
		userID, key, hash)
	if err != nil {
		return false, Record{}, fmt.Errorf("claim idempotency key: %w", err)
	}
	if tag.RowsAffected() == 1 {
		return true, Record{}, nil
	}

	var rec Record
	var state string
	err = s.pool.QueryRow(ctx, `
		SELECT request_hash, state, coalesce(response_status, 0),
		       coalesce(response_headers, '{}'), coalesce(response_body, '')
		  FROM idempotency_keys WHERE user_id = $1 AND key = $2`,
		userID, key).Scan(&rec.RequestHash, &state, &rec.Response.Status, &rec.Response.Header, &rec.Response.Body)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, Record{}, ErrInProgress // released a moment ago; the retry can try again
	}
	if err != nil {
		return false, Record{}, fmt.Errorf("read idempotency key: %w", err)
	}
	rec.Done = state == "done"
	return false, rec, nil
}

func (s *PostgresStore) Complete(ctx context.Context, userID int64, key string, resp Response) error {
	_, err := s.pool.Exec(ctx, `
		UPDATE idempotency_keys
		   SET state = 'done', response_status = $3, response_headers = $4, response_body = $5
		 WHERE user_id = $1 AND key = $2`,
		userID, key, resp.Status, resp.Header, resp.Body)
	return err
}

func (s *PostgresStore) Release(ctx context.Context, userID int64, key string) error {
	_, err := s.pool.Exec(ctx, "DELETE FROM idempotency_keys WHERE user_id = $1 AND key = $2", userID, key)
	return err
}
```

The heart of it is `Claim`, and it's the trick you've now seen three times (the last plate in lesson 8, the refresh token in lesson 12). `INSERT ... ON CONFLICT` either inserts the key, meaning **we** are the first and own it, or finds it already there. Two retries arriving at the same instant can't both own the key: the primary key makes Postgres pick exactly one, and the other changes no rows.

The `DO UPDATE ... WHERE` part is for one rare case: a key stuck `in_progress` because the server crashed while running it. If a retry comes **more than a minute** after the last claim, with the **same** request, it takes the key over and runs again. Nothing legitimate takes a minute (the server's `WriteTimeout` is 30 seconds), and if the crashed attempt *had* placed the order, step 6's constraint catches it. Without this, a crash at the wrong moment would make that key answer "still in progress" for ever.

`pgx` turns `http.Header`, which is a `map[string][]string`, into JSON for the `jsonb` column, and back again when scanning. `coalesce` turns the `NULL`s of an unfinished record into empty values, so the scan never has to deal with them.

## Step 5: the middleware
<!-- bite: 3c3423f2-f6a7-4ac6-b337-e2e3d79a1337 -->

Here's where Go makes this lesson simpler than it is in Express. A Go handler is a function call: when `next.ServeHTTP` **returns**, the handler has finished. So the middleware can give the handler a **pretend** `ResponseWriter` that collects everything in memory, wait for it to return, save what it collected, and only *then* send it to the client.

`internal/idempotency/middleware.go`:

```go
package idempotency

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"

	"mamaput/internal/apperr"
	"mamaput/internal/auth"
	"mamaput/internal/httpx"
)

var (
	ErrKeyRequired = apperr.New(apperr.Invalid, "idempotency-key-required",
		"Send an Idempotency-Key header: a new random value for each action, the same value on every retry.")
	ErrBadKey = apperr.New(apperr.Invalid, "bad-idempotency-key",
		"Idempotency-Key must be 8 to 128 letters, digits, '-' or '_'.")
	ErrKeyReused = apperr.New(apperr.RuleBroken, "idempotency-key-reused",
		"This Idempotency-Key was already used for a different request. Use a new key for a new action.")
	ErrInProgress = apperr.New(apperr.Conflict, "request-in-progress",
		"The same request is still being processed. Try again in a moment.")
	errBodyTooLarge = apperr.New(apperr.TooLarge, "body-too-large", "The request body is too large.")
)

var keyPattern = regexp.MustCompile(`^[A-Za-z0-9_-]{8,128}$`)

const maxBody = 64 << 10

type Store interface {
	Claim(ctx context.Context, userID int64, key, hash string) (bool, Record, error)
	Complete(ctx context.Context, userID int64, key string, resp Response) error
	Release(ctx context.Context, userID int64, key string) error
}

type keyCtx struct{}

// KeyFrom gives a handler the key this request was claimed under.
func KeyFrom(ctx context.Context) string {
	k, _ := ctx.Value(keyCtx{}).(string)
	return k
}

// Require makes a route safe to retry. It must run after auth: keys belong to users.
func Require(store Store) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return httpx.HandlerFunc(func(w http.ResponseWriter, r *http.Request) error {
			who, err := auth.Current(r.Context())
			if err != nil {
				return err
			}
			key := r.Header.Get("Idempotency-Key")
			if key == "" {
				return ErrKeyRequired
			}
			if !keyPattern.MatchString(key) {
				return ErrBadKey
			}

			body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, maxBody))
			if err != nil {
				return errBodyTooLarge
			}
			r.Body = io.NopCloser(bytes.NewReader(body)) // the handler reads it again
			hash := fingerprint(r, body)

			claimed, rec, err := store.Claim(r.Context(), who.UserID, key, hash)
			if err != nil {
				return err
			}
			if !claimed {
				switch {
				case rec.RequestHash != hash:
					return ErrKeyReused
				case !rec.Done:
					w.Header().Set("Retry-After", "2")
					return ErrInProgress
				}
				w.Header().Set("Idempotent-Replayed", "true")
				rec.Response.writeTo(w)
				return nil
			}

			// We own the key. Saving must finish even if the client has gone away.
			saveCtx := context.WithoutCancel(r.Context())
			defer func() {
				if p := recover(); p != nil {
					store.Release(saveCtx, who.UserID, key)
					panic(p) // RecoverPanic, further out, still logs it and answers 500
				}
			}()

			buf := &bufferedWriter{header: http.Header{}}
			next.ServeHTTP(buf, r.WithContext(context.WithValue(r.Context(), keyCtx{}, key)))
			resp := buf.response()

			if resp.Status >= 500 {
				err = store.Release(saveCtx, who.UserID, key)
			} else {
				err = store.Complete(saveCtx, who.UserID, key, resp)
			}
			if err != nil {
				httpx.LoggerFrom(r.Context()).Error("idempotency store failed", "key", key, "error", err)
			}
			resp.writeTo(w)
			return nil
		})
	}
}

// fingerprint hashes the method, the path and the body. The body is decoded and
// encoded again first, so the same JSON written differently gives the same hash.
func fingerprint(r *http.Request, body []byte) string {
	h := sha256.New()
	fmt.Fprintf(h, "%s %s\n", r.Method, r.URL.Path)

	dec := json.NewDecoder(bytes.NewReader(body))
	dec.UseNumber()
	var v any
	if dec.Decode(&v) == nil {
		if canonical, err := json.Marshal(v); err == nil {
			body = canonical
		}
	}
	h.Write(body)
	return hex.EncodeToString(h.Sum(nil))
}
```

And the pretend writer, in `internal/idempotency/buffer.go`:

```go
package idempotency

import (
	"bytes"
	"net/http"
)

// bufferedWriter is a ResponseWriter that keeps everything in memory.
type bufferedWriter struct {
	header http.Header
	status int
	body   bytes.Buffer
}

func (b *bufferedWriter) Header() http.Header { return b.header }

func (b *bufferedWriter) WriteHeader(status int) {
	if b.status == 0 {
		b.status = status
	}
}

func (b *bufferedWriter) Write(p []byte) (int, error) {
	if b.status == 0 {
		b.status = http.StatusOK
	}
	return b.body.Write(p)
}

func (b *bufferedWriter) response() Response {
	if b.status == 0 {
		b.status = http.StatusOK
	}
	return Response{Status: b.status, Header: b.header, Body: b.body.Bytes()}
}

func (resp Response) writeTo(w http.ResponseWriter) {
	for name, values := range resp.Header {
		w.Header()[name] = values
	}
	w.WriteHeader(resp.Status)
	w.Write(resp.Body)
}
```

Walk through `Require`:

1. **The key is checked like any input**: required, and a sensible shape. A UUID fits.
2. **The body is read once, in full** (capped at 64 KB, like every body since lesson 14), hashed, and put back as a fresh reader, so the handler's `httpx.Decode` reads it exactly as before.
3. **The fingerprint** is a hash of the method, the path and the body, with the body written in one standard way first. `{"dishId":"1","quantity":2}` and `{ "quantity": 2, "dishId": "1" }` mean the same thing, and Go's `json.Marshal` always writes a map's keys in sorted order, so both give the same fingerprint. `UseNumber` keeps numbers exactly as written, instead of turning them into `float64`, which would make two different very large numbers look the same.
4. **`Claim`** decides which of the four cases we're in.
5. **Replays** send the stored status, headers and body, plus an `Idempotent-Replayed: true` header, so the client (and you, when debugging) can see it was a replay. The stored headers include `Location`, so a replayed `201` still says where the new order lives.
6. **When we own the key**, the handler writes into `bufferedWriter`, not to the client. The handler can't tell the difference: it's an `http.ResponseWriter` like any other. When it returns, we have its whole answer.
7. **Save first, then send.** The answer is stored *before* the client sees any of it, so a retry can never arrive and find "in progress" for an answer the client already has.
8. **5xx answers release the key** instead of storing it. A 500 means *we* failed, perhaps for a moment, and the client must be able to retry and have it actually work. A 4xx (say, `not-enough-portions`) is stored and replayed: retrying won't make the pot fuller.
9. **A panic releases the key too**, then panics again so `RecoverPanic` (lesson 3, further out in the chain) still logs it and answers 500.

Two Go details are doing important work:

**`context.WithoutCancel`.** A request's context is cancelled the moment the client disconnects, which is exactly the tunnel case. If we saved with `r.Context()`, the save would fail with "context canceled" precisely when it matters most: the order is placed, the client is gone, and its retry is on the way. `context.WithoutCancel` (Go 1.21) makes a context that keeps the request's values (the logger, the request ID) but is never cancelled, so the save finishes.

**Buffering has a cost.** The whole answer sits in memory until the handler finishes. For an order, that's a few hundred bytes, which is nothing. Never put this middleware on a route that streams (lesson 20's live kitchen screen) or sends big files: there, the client would get nothing until the end, and memory would hold all of it.

The route gains one wrapper, **inside** `RequireUser`, because the key belongs to the user. In `orders.Register`, `POST` becomes:

```go
mux.Handle("POST "+p+"/orders", customer(h.idempotent(httpx.HandlerFunc(h.place))))
```

`orders.Handler` gets an `idempotent func(http.Handler) http.Handler` field. v2's is `idempotency.Require(store)`; v1's is the do-nothing `anyone` from lesson 12. And in `run`, `idempotency.NewPostgresStore(pool)` goes into `app.Deps`.

## Step 6: the second layer, in the database
<!-- bite: f4461e21-0e78-40b9-8496-9280b0177e66 -->

Step 5 saves the answer *after* the handler has committed the order. What if the server crashes in that gap: the order is in the database, but `Complete` never ran? The key stays `in_progress`. A retry a minute later takes it over (step 4), and runs `place` again. Without something more, that's a second order.

That's what the unique index on `orders` is for. The key travels into the order itself. In the orders handler, `place` passes it on:

```go
in.IdempotencyKey = idempotency.KeyFrom(r.Context())
```

`NewOrder` gains `IdempotencyKey string` with the tag `` `json:"-"` ``. The `-` means `encoding/json` never reads or writes this field, so a client can't set it from the body; and since our decoder refuses unknown fields (lesson 6), a body that tries gets a 400.

Then the Postgres store's `PlaceTakingPortions` takes the whole order, `(ctx, customerID *int64, in NewOrder)`, instead of the dish and quantity separately, and the insert inside the lesson 8 transaction becomes:

```go
var errDuplicateOrder = errors.New("an order with this idempotency key already exists")

// inside pgx.BeginFunc, after the portions are taken:
order, err = scanOrder(tx.QueryRow(ctx, `
	INSERT INTO orders (customer_id, dish_id, quantity, total_kobo, idempotency_key)
	VALUES ($1, $2, $3, $4, NULLIF($5, ''))
	ON CONFLICT (customer_id, idempotency_key) WHERE idempotency_key IS NOT NULL DO NOTHING
	RETURNING `+orderColumns,
	customerID, in.DishID, in.Quantity, total, in.IdempotencyKey))
if errors.Is(err, ErrOrderNotFound) {
	return errDuplicateOrder // no row came back: this order already exists
}
return err
```

and after `BeginFunc` returns:

```go
if errors.Is(err, errDuplicateOrder) {
	return scanOrder(s.pool.QueryRow(ctx,
		"SELECT "+orderColumns+" FROM orders WHERE customer_id = $1 AND idempotency_key = $2",
		customerID, in.IdempotencyKey))
}
```

Follow what happens on the crash-then-retry:

1. The retry takes the portions again, inside the transaction.
2. The insert hits the unique index, `DO NOTHING` inserts nothing, and `RETURNING` gives no row. `scanOrder` turns "no row" into `ErrOrderNotFound`, and we turn that into `errDuplicateOrder`.
3. Returning an error from the `BeginFunc` function **rolls back** the transaction, which gives back the portions taken in step 1.
4. We look up the order that already exists, and return it as if we'd just made it.

Whatever happened to the first layer, the customer gets one order and pays for one plate. `NULLIF($5, '')` turns an empty key into `NULL`, so v1 orders, which have none, are left out of the index and never clash with each other.

That's the pattern for anything involving money: **the key lives in the same transaction as the effect it protects.** The table of answers makes retries smooth; the constraint makes duplicates impossible.

## Trying it
<!-- bite: 697f277f-285e-436e-b241-05b1e5db6339 -->

```bash
KEY=$(uuidgen)   # or: cat /proc/sys/kernel/random/uuid

curl -si -X POST localhost:8080/v2/orders \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}' | head -1
# HTTP/1.1 201 Created

# The "retry": exactly the same request, same key
curl -si -X POST localhost:8080/v2/orders \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}' \
  | grep -E '^HTTP|^Idempotent-Replayed|"id"'
```

Predict before you run the second one: what status, which order ID, and how many portions are left? It answers `201` again, with `Idempotent-Replayed: true` and **the same order ID**, and the portions only went down once.

Then:

1. Same key, `"quantity":5`. Predict: 422 `idempotency-key-reused`.
2. No key at all. Predict: 400 `idempotency-key-required`.
3. Twenty copies of one request with a **new** key, all at once:

```bash
KEY=$(uuidgen)
for i in $(seq 20); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8080/v2/orders \
    -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
    -H "Content-Type: application/json" -d '{"dishId":"1","quantity":1}' &
done | sort | uniq -c
wait
```

`-o /dev/null` throws the body away, `-w "%{http_code}\n"` prints only the status, and `sort | uniq -c` counts each one. Predict: some `201`s and some `409`s, never anything else. Then count the orders with that key in `psql`: exactly one. Okay!!!!! Twenty taps, one plate.

## What the client must do
<!-- bite: 4bed1887-a4de-43e7-be95-7bdf1fb0c5ce -->

Idempotency is a promise between both sides. The phone app's half:

1. **Make a new key when the customer acts**, not per request. One tap of "Place order" is one key.
2. **Reuse that key on every retry** of that action, even after an app restart if it can (save it with the unsent order).
3. **Retry with growing gaps**: wait 1 second, then 2, then 4, with a little randomness, so a struggling server isn't hammered by every phone at once. Lesson 26 builds exactly this for our own services.
4. **On 409 `request-in-progress`**, wait `Retry-After` seconds and try again.

## The Go in this lesson
<!-- bite: e19fd66a-79f1-432b-8d48-6c4410e09156 -->

1. **A type that satisfies `http.ResponseWriter`**: `bufferedWriter` has the three methods, `Header`, `Write` and `WriteHeader`, so the handler accepts it like the real one. This is the interface idea from lesson 1 doing real work: the handler only depends on the interface, so we can hand it anything that fits.
2. **`bytes.Buffer`**: A growable slice of bytes with a `Write` method. Its zero value is an empty buffer, ready to use, so `bufferedWriter` needs no constructor for it.
3. **`io.ReadAll`**, then **`io.NopCloser(bytes.NewReader(body))`**: Read the body once into memory, then give the request a new body that reads the same bytes. `NopCloser` adds the `Close` method an `http.Request`'s body must have.
4. **`context.WithoutCancel(ctx)`** (Go 1.21): A context with the same values that's never cancelled. Use it for work that must finish after the client has gone, like saving what you already did.
5. **`recover()` then `panic(p)` again**: Catch a panic only to clean up, then let it carry on to the code whose job is handling it. The deferred function runs whether the handler returns normally or panics.
6. **`json.Decoder.UseNumber()`**: Numbers decode as `json.Number`, which is the number's exact text, instead of `float64`. `json.Marshal` writes a `json.Number` back exactly as it was.
7. **Sorted keys from `json.Marshal`**: Encoding a `map[string]any` always writes the keys in sorted order. It's a documented promise, which is why it can be used for a fingerprint.
8. **`sha256.New()`** with **`fmt.Fprintf(h, ...)`** and **`h.Sum(nil)`**: A hash is an `io.Writer`; anything you write into it is hashed. `Sum(nil)` gives the result.
9. **`` `json:"-"` ``**: Tells `encoding/json` to skip the field completely, in both directions.
10. **`w.Header()[name] = values`**: Writing to the header map directly copies every value of a header at once. `Set` would keep only one.
11. **`NULLIF($5, '')`**: SQL, not Go: `NULLIF(a, b)` is `NULL` when `a` equals `b`, otherwise `a`. It turns "no key" into a real `NULL`.

## Your project so far
<!-- bite: 75b20d54-9d07-480f-99ee-a1d3beec8ca4 -->

```text
mama-put/
├── migrations/
│   ├── 001 … 009
│   └── 010_idempotency.sql        ← NEW: idempotency_keys; orders.idempotency_key, unique per customer
├── openapi/
│   └── v2.yaml                    ← Idempotency-Key header on POST /v2/orders; 409 and 422 documented
├── cmd/
│   └── api/main.go                ← builds the idempotency store
└── internal/
    ├── app/
    │   └── app.go                 ← Deps.Idempotency; v2 orders get Require, v1 gets anyone
    ├── idempotency/               ← NEW package
    │   ├── store.go               ← Claim (INSERT … ON CONFLICT, takeover after a minute), Complete, Release
    │   ├── middleware.go          ← Require: the four cases, fingerprint, save then send, KeyFrom
    │   └── buffer.go              ← bufferedWriter, writeTo
    └── orders/
        ├── orders.go              ← NewOrder.IdempotencyKey (json:"-")
        ├── handlers.go            ← place passes KeyFrom on; POST wrapped in the idempotency guard
        └── postgres.go            ← key stored with the order; a duplicate rolls back and returns the original
```

## Common mistakes
<!-- bite: 8b46fb40-a12d-4865-b679-98fb0f7cd1df -->

1. **A new key per retry.** Then every retry looks new, and you're back to duplicates. One key per *action*.
2. **Keys not scoped to the user.** One customer could be replayed another's answer. Key on `(user_id, key)`.
3. **Ignoring a changed body.** Same key, different body is a client bug. Refuse it with 422; don't guess.
4. **Storing 5xx answers.** Then a brief failure is "remembered", and every retry fails too. Release the key on 5xx.
5. **Check-then-insert for claiming keys.** Two retries at the same instant both see "no key" and both run. Let the primary key decide.
6. **Saving with the request's context.** It's cancelled when the client leaves, which is exactly when the save matters. Use `context.WithoutCancel`.
7. **Sending before saving.** Then a fast retry can find "in progress" for an answer the client already has. Buffer, save, then send.
8. **Only the middleware, for money.** The stored answer can be lost in a crash. Put the key in the same transaction as the effect, with a unique constraint.
9. **Buffering a streaming route.** The client gets nothing until the end. Keep this middleware to small, ordinary answers.
10. **Keeping keys for ever.** The table grows without end. Keep them for a day or so; lesson 18 adds the cleanup job.

## Check your understanding
<!-- bite: a6a4d7bc-96cd-4517-812f-5c63f821da88 -->

1. Why does the server answer `201` with the *same* order ID on a retry, instead of `409 "already exists"`?
2. Ada's first request is still taking portions when her retry arrives. What does the retry get, and why not just wait?
3. Why are 4xx answers stored and replayed, but 5xx answers released?
4. Ada's phone loses signal just as her order commits, so the request's context is cancelled. Why does the save still work?
5. The server crashes right after committing Ada's order, before `Complete` runs. Two minutes later, her app retries with the same key. Follow it through: what stops a second order, and what does she get back?

<details>
<summary>Answers, after your attempt</summary>

1. Because the client should end up exactly where it would have been if the first answer had arrived. Its code for "order placed" just works. A 409 would force every client to write special code for something that's normal.
2. A `409 request-in-progress` with `Retry-After: 2`. Holding the retry open until the first finishes would tie up a connection, and could wait for ever if the first one hung. A quick, clear "try again shortly" is simpler and safer.
3. A 4xx is about the request itself (bad input, a finished dish), so retrying the same request will give the same answer, and storing it is correct. A 5xx is our failure, often temporary, so the client must be allowed to retry and succeed.
4. Because the save uses `context.WithoutCancel(r.Context())`, a context that keeps the request's values but can't be cancelled. The store's queries run to the end even though the client has gone.
5. The key is still `in_progress`, claimed over a minute ago, with the same fingerprint, so `Claim` lets the retry take it over. `place` runs again and takes the portions, but the insert hits the unique index on `(customer_id, idempotency_key)` and inserts nothing. The transaction rolls back, giving the portions back; the store finds the original order and returns it. The middleware saves that answer as `done`. Ada gets `201` with her original order, and paid for one plate.

</details>

## Practice
<!-- bite: 8fcf3d6b-fa08-4887-842d-3991a387bfd0 -->

1. Make `POST /v2/orders/{id}/cancel` (lesson 13's practice) idempotent with the same middleware. Cancelling an already-cancelled order with a *new* key should still give `409 already-cancelled`, not give the portions back twice.
2. Write `TestRequire` with `httptest` and a fake `Store` (a map behind a mutex): a first request runs the handler; a retry replays it without running it (count the calls); a changed body gets 422; a handler that answers 500 leaves no key behind.
3. Give `Require` an option for routes where the key is welcome but not required, so it can be added to a released version without breaking it: no key, just run the handler as normal.
4. Write a SQL query, saved as `scripts/stale-idempotency-keys.sql`, that lists keys stuck `in_progress` for more than 10 minutes. These are what step 6 protects against; it's worth being able to see them.

**Done when** a replayed order has `Idempotent-Replayed: true` and the same ID; twenty parallel requests with one key create exactly one order; a changed body with the same key gets 422; and `make test` passes with `TestRequire`.

## Before moving on
<!-- bite: 7d510950-d413-4f4a-9924-b32c9f758467 -->

Mama Put API can now be retried safely. Same key, same answer, one order, whether the retry comes from a tunnel, a proxy or a double tap, and a database constraint backs it up when the first layer can't.

We've built a lot now: fifteen lessons of rules, checks and edge cases. And almost every time, we checked them by hand with `curl`. Change one thing in the auth service tomorrow, and you'd have to run all of those `curl`s again to know nothing broke. Nobody does that. So the next lesson writes it all down as tests that run in seconds.

## Related
<!-- bite: e96db89c-5d61-4c52-b4db-d68950ceee6b -->

- [[backend/frameworks/net-http/16-testing|Next: Testing]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — the idea in any framework
- [[backend/frameworks/net-http/08-data-with-postgres|Data with PostgreSQL]] — the transaction this builds on
- [[backend/frameworks/express/15-idempotency|The same lesson in Express]] — wrapping `res.json` and saving on `finish`

## About this lesson
<!-- bite: b302d9e5-53d4-4ea1-8a31-6c1c595cb2e5 -->

**Level:** Advanced. Lesson 15 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`context.WithoutCancel` needs 1.21) and pgx v5. Covers idempotent and non-idempotent methods, the `Idempotency-Key` header, a key store claimed atomically with `INSERT … ON CONFLICT`, taking over keys stuck by a crash, request fingerprints with canonical JSON, the four cases, a buffering `ResponseWriter` that saves before it sends, `context.WithoutCancel` for saves that must finish, releasing keys on 5xx and panics, and a unique constraint in the same transaction as the order.
