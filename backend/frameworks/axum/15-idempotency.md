---
id: 77e8a7c0-2a9d-4580-9621-06b5c0af71b9
---

# Idempotency

**A request is idempotent when sending it twice has the same effect as sending it once.** Networks fail in the worst possible place: after the server has done the work, before the client hears the answer. The client can't tell "it failed" from "it worked and the answer got lost", so it retries, and a retried "place this order" places two. The fix is an **`Idempotency-Key`**: the client names each attempt, and the server makes sure a name only ever does the work once.

## Before you start
<!-- bite: 4b935618-543a-402c-a080-efa1ae9e565b -->

You should have:

1. Finished [[backend/frameworks/axum/14-security|lesson 14]], so v2 needs logins, is rate-limited, and `cargo test` passes.
2. Read [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] if you want the idea first. Not required.

After this lesson you will be able to:

1. Say which HTTP methods are idempotent already, and which need help.
2. Design an `Idempotency-Key` scheme: claim, run once, save, replay.
3. Claim a key safely when two copies of a request arrive at the same instant.
4. Write it as Axum middleware that buffers the request and response bodies.
5. Add a second layer in the database, so even a crash in the wrong place can't make two orders.

## Where we stopped
<!-- bite: ed74df87-cdb2-4cba-9d0a-24fe0818f329 -->

Ada orders jollof on the bus. The request reaches Mama Put; the plates are taken and the order saved. Then the bus goes into a tunnel, and the answer never arrives. Ada's app waits, gives up, and does what every good app does: it tries again. Mama cooks two jollofs. Ada gets one and pays for two.

Nothing in our code is wrong. Each request did exactly what it should. The problem is that two requests were really one *intention*, and the server can't tell.

## The kid version
<!-- bite: 7c4bedcb-048d-4de6-aba9-06340fc1ea60 -->

Ada sends her little brother to Mama's with an order slip. He comes back without the food: "I don't know if she got it, it was busy." So Ada writes a new slip and sends him again. Now Mama has two slips, and cooks twice.

So Ada starts numbering her slips. "Order 17: one jollof." If the brother isn't sure, he takes *the same slip* back. Mama checks her notebook: "17? Already done, here's your receipt." One jollof.

The number is the **idempotency key**. Mama's notebook is the table that remembers each key and its answer.

**Where the picture stops working.** Mama can see the brother waiting while she's still cooking order 17. Our server can get the second copy of a request *while the first is still running*, on another thread or another copy of the app. So "check the notebook" must be a single step that two requests can't do at the same time.

## Terms used in this lesson
<!-- bite: 4a55c73b-1afb-4d0b-bc88-1e37487c448c -->

1. **Idempotent**: This describes a request whose effect is the same however many times it's sent.
2. **Idempotency key**: This is a unique value the client makes for each *intention* (each order, not each attempt), sent in the `Idempotency-Key` header, the same on every retry.
3. **Claim**: This is the server marking a key as "being worked on", so a second copy of the request knows to wait.
4. **Replay**: This is answering a retry with the saved answer to the first request, without doing the work again.
5. **Request fingerprint**: This is a hash of what the request asked for, so the server can tell a retry from a different request that reused a key by mistake.

## Step 1: which methods are already safe?
<!-- bite: d690388f-ee33-4f72-9208-ed9ae4801ca0 -->

By HTTP's rules:

1. **`GET`** only reads. Send it a hundred times; nothing changes.
2. **`PUT`** and **`DELETE`** are idempotent by meaning: "make the dish *this*", "make order 7 gone". The second time finds it already so. (Lesson 8's `DELETE` answers 404 the second time, which is a different answer but the same effect.)
3. **`PATCH`** depends on what it says. "Set `portionsLeft` to 20" is idempotent; "add 5 plates" wouldn't be. Ours all set values, so they're safe.
4. **`POST`** means "do this", and doing it twice does it twice. **`POST /v2/orders` is the one that needs help**, and it's the one with money attached.

## Step 2: the plan
<!-- bite: 46530000-5ead-41e2-a22a-a20031390692 -->

The client makes a key per order (a UUID is perfect), sends it as `Idempotency-Key`, and sends *the same key* on every retry of that order. On the server, for a `POST` with a key:

1. **Fingerprint the request**: a hash of its path and body.
2. **Claim the key**, for this customer, in one statement.
3. **If we got the claim**, run the request. If it succeeded, save its status, body and `Location`. If it was refused, give the key back.
4. **If someone else holds it and it's answered**, and the fingerprint matches, **replay** the saved answer. If the fingerprint differs, refuse: that's a different request reusing a key, which is a client bug.
5. **If someone else holds it and it isn't answered yet**, answer 409 "still working on it", with `Retry-After: 1`.

Keys belong to a customer, so Ada's key `order-1` and Bayo's `order-1` never clash. That's why this is for v2, where every order has a logged-in customer.

**Why only save successes?** Lesson 7 put the writing of error bodies in `write_problems`, the outermost layer. This middleware sits further in, so when a handler refuses with an `ApiError`, the response passing through here has a status and no body yet. More importantly, a refusal *changed nothing*: no plates taken, no order saved. Retrying it is safe, and might even work (Mama may have cooked more). So a refusal gives the key back, and only a success is saved for replaying.

## Step 3: the table
<!-- bite: 52c83e43-a231-44d9-a0ab-9c474c835309 -->

`migrations/0007_idempotency.sql`:

```sql
-- One row per (customer, key): the first request's fingerprint, and its answer once there is one.
CREATE TABLE idempotency_keys (
  user_id           bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  key               text   NOT NULL CHECK (length(key) BETWEEN 1 AND 255),
  request_hash      text   NOT NULL,
  response_status   smallint,            -- NULL while the first request is still running
  response_body     bytea,
  response_location text,
  created_at        timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, key)
);

-- The second layer: whatever happens to the table above, one key can only ever make one order.
ALTER TABLE orders ADD COLUMN idempotency_key text;
CREATE UNIQUE INDEX orders_customer_idempotency_key_idx ON orders (customer_id, idempotency_key);
```

1. **`PRIMARY KEY (user_id, key)`**: one row per customer and key, enforced by Postgres. That's what makes the claim safe.
2. **`response_status` is `NULL` while the first request runs.** "Claimed but not answered" and "answered" are the same row, told apart by this column.
3. **`bytea`** stores bytes: the response body, exactly as it was sent.
4. **The second half is step 6.** Read past it for now.

## Step 4: the store
<!-- bite: 2ab9122a-f029-4f0e-b9bb-c92f8eeb2228 -->

`src/http/idempotency.rs`. The claim:

```rust
    /// Claims the key for this request, in one statement, so two requests at once can't both win.
    /// A claim that was never answered (the server stopped mid-request) is taken over after a minute.
    pub async fn claim(&self, user_id: i64, key: &str, request_hash: &str) -> Result<Claim, StoreError> {
        let won = sqlx::query_scalar!(
            r#"INSERT INTO idempotency_keys (user_id, key, request_hash) VALUES ($1, $2, $3)
               ON CONFLICT (user_id, key) DO UPDATE SET request_hash = EXCLUDED.request_hash, created_at = now()
                 WHERE idempotency_keys.response_status IS NULL AND idempotency_keys.created_at < now() - interval '1 minute'
               RETURNING true AS "won!""#,
            user_id,
            key,
            request_hash
        )
        .fetch_optional(&self.pool)
        .await?;
        if won.is_some() {
            return Ok(Claim::New);
        }
```

This is the most important statement in the lesson. Read it in three parts:

1. **`INSERT ...`**: try to add the row. If no row has this customer and key, it goes in, `RETURNING true` gives a row back, and we've won the claim.
2. **`ON CONFLICT (user_id, key) DO UPDATE ... WHERE ...`**: if the row is already there, *usually* do nothing, so no row comes back and we've lost. The one exception is the `WHERE`: a claim that was never answered and is over a minute old. That's a request whose server stopped half-way (a crash, a deploy). Without this, its key would be stuck at "still working on it" forever. With it, a retry a minute later takes the claim over.
3. **It's one statement.** Two copies of a request arriving at the same instant both try to insert; the primary key lets exactly one in. The other sees the conflict. There's no gap between "check" and "claim" for anything to slip into. It's the last plate from lesson 8, again.

(`AS "won!"` tells sqlx the column can't be `NULL`; the `!` is how its macros say "trust me".)

If we lost, we look at what's there, and say what we found:

```rust
/// What `claim` found.
pub enum Claim {
    /// Nobody has used this key: it's ours now, so run the request.
    New,
    /// Another request with this key is still running.
    InProgress,
    /// It's been answered. Replay the answer, if the request is the same one.
    Done { request_hash: String, status: u16, body: Vec<u8>, location: Option<String> },
}
```

```rust
        Ok(match (row.response_status, row.response_body) {
            (Some(status), Some(body)) => Claim::Done {
                request_hash: row.request_hash,
                status: status as u16,
                body,
                location: row.response_location,
            },
            _ => Claim::InProgress,
        })
```

`complete` fills in the answer, and `release` deletes an unanswered claim (`AND response_status IS NULL`, so it can never delete a saved answer).

## Step 5: the middleware
<!-- bite: f0135138-6ebf-4add-a15f-ba6286dea674 -->

The rest of the file. It needs a store and the token keys, so its state is a small struct with `#[derive(FromRef)]`:

```rust
/// What the middleware needs: somewhere to keep keys, and a way to tell who's asking.
#[derive(Clone, FromRef)]
pub struct Idempotency {
    pub store: IdempotencyStore,
    pub keys: Keys,
}
```

The start: who takes part, and the fingerprint:

```rust
pub async fn idempotent(State(state): State<Idempotency>, req: Request, next: Next) -> Response {
    // Only a POST with a key takes part. Everything else passes straight through.
    let Some(key) = req.headers().get("idempotency-key").cloned() else {
        return next.run(req).await;
    };
    if req.method() != axum::http::Method::POST {
        return next.run(req).await;
    }
    let key = match key.to_str() {
        Ok(k) if (1..=255).contains(&k.len()) => k.to_owned(),
        _ => return bad_key("Use 1 to 255 plain characters, like a UUID.").into_response(),
    };
    // Keys belong to a customer. No valid token: let the handler give its 401.
    let token = req.headers().get(header::AUTHORIZATION).and_then(|v| v.to_str().ok()).and_then(|v| v.strip_prefix("Bearer "));
    let Some(who) = token.and_then(|t| state.keys.check_access(t)) else {
        return next.run(req).await;
    };

    // The fingerprint of this request: the same key with a different body is a mistake, not a retry.
    let (parts, body) = req.into_parts();
    let Ok(bytes) = to_bytes(body, 16 * 1024).await else {
        return ApiError::new(StatusCode::PAYLOAD_TOO_LARGE, "body-too-large", "Body too large", "At most 16 KB.").into_response();
    };
    let request_hash = hex::encode(Sha256::new().chain_update(parts.uri.path()).chain_update(b"\n").chain_update(&bytes).finalize());
```

1. **No key, or not a `POST`: pass straight through.** The key is optional. A client that doesn't send one gets exactly the old behaviour.
2. **No valid token: pass through too**, and the handler's `AuthUser` gives its usual 401. The middleware doesn't repeat that job; it only needs to know whose key this is. It reads the token directly, because a `from_fn` middleware's extractors use the middleware's own state, not `AppState`.
3. **`req.into_parts()`** splits the request into its head and its body. The body is a stream that can only be read once, so we read it all (`to_bytes`, capped at lesson 6's 16 KB), hash it, and later build a new request from the head and the bytes, for the handler to read as if nothing happened.
4. **The fingerprint is the path and the body.** `Sha256::new().chain_update(...)` feeds pieces into one hash; the `\n` between them stops `/a` + `bc` and `/ab` + `c` hashing the same.

Then the four outcomes:

```rust
    match state.store.claim(who.user_id, &key, &request_hash).await {
        Err(e) => ApiError::internal(e).into_response(),
        Ok(Claim::InProgress) => {
            let mut response =
                ApiError::new(StatusCode::CONFLICT, "idempotency-in-progress", "Still working on it", "The first request with this key hasn't finished. Try again in a second.")
                    .into_response();
            response.headers_mut().insert(header::RETRY_AFTER, HeaderValue::from_static("1"));
            response
        }
        Ok(Claim::Done { request_hash: first, status, body, location }) => {
            if first != request_hash {
                return ApiError::new(
                    StatusCode::UNPROCESSABLE_ENTITY,
                    "idempotency-key-reused",
                    "Key already used",
                    "That key was used for a different request. Use a new key for a new request.",
                )
                .into_response();
            }
            replay(status, body, location)
        }
        Ok(Claim::New) => {
            let response = next.run(Request::from_parts(parts, Body::from(bytes))).await;
            if !response.status().is_success() {
                // Refused or failed: nothing happened, so the same key may try again.
                if let Err(e) = state.store.release(who.user_id, &key).await {
                    tracing::error!(cause = %e, "couldn't release an idempotency key");
                }
                return response;
            }
            let (mut head, body) = response.into_parts();
            let Ok(body) = to_bytes(body, MAX_SAVED_RESPONSE).await else {
                return ApiError::internal("a response too big to save for replaying").into_response();
            };
            let location = head.headers.get(header::LOCATION).and_then(|v| v.to_str().ok());
            if let Err(e) = state.store.complete(who.user_id, &key, head.status.as_u16(), &body, location).await {
                tracing::error!(cause = %e, "couldn't save a response for replaying");
            }
            head.headers.remove(header::CONTENT_LENGTH);
            Response::from_parts(head, Body::from(body))
        }
    }
}
```

1. **`Claim::New`**: run the real request, rebuilt from its parts. Then, on success, read the *response's* body too (the same one-time stream problem), save it, and send it on, rebuilt.
2. **If saving fails, the customer still gets their answer.** The order *was* placed; refusing to say so would be worse. The error is logged, and step 6 makes sure a retry still can't place a second order.
3. **`Claim::Done` with a different fingerprint**: a 422. It's a client bug (a key reused for a new order), and replaying the old order would be wrong in a way they'd never notice.

And the replay itself:

```rust
/// The first answer, again, marked so the client can tell.
fn replay(status: u16, body: Vec<u8>, location: Option<String>) -> Response {
    let status = StatusCode::from_u16(status).unwrap_or(StatusCode::OK);
    let mut response = (status, [(header::CONTENT_TYPE, "application/json")], body).into_response();
    response.headers_mut().insert("idempotent-replayed", HeaderValue::from_static("true"));
    if let Some(location) = location.and_then(|l| HeaderValue::from_str(&l).ok()) {
        response.headers_mut().insert(header::LOCATION, location);
    }
    response
}
```

The same status, the same body, the same `Location`, plus **`Idempotent-Replayed: true`**, so a client (or someone debugging) can see this was a replay. Lesson 14's CORS layer adds it to `expose_headers`, so a web app can read it.

### Where it goes

Only v2's orders, in `app`:

```rust
        .merge(
            orders::router::<_, version::V2>()
                .route_layer(middleware::from_fn_with_state(state.idempotency.clone(), http::idempotent)),
        )
```

`route_layer` on the v2 orders router alone: the `GET`s there pass straight through (not a `POST`), and v1, frozen, is untouched. `AppState` gains `idempotency: http::Idempotency`, built in `main` from the pool and the keys. And the docs say so: `place_order` gains a header parameter, `Idempotency-Key`, with a description telling the phone team what to send.

## Step 6: the second layer, in the database
<!-- bite: 87d84f00-35f6-40a5-b376-febfc02bffd5 -->

There's still one gap. The handler commits the order, and then, before `complete` saves the answer, the server dies. The claim stays unanswered. A minute later, Ada's retry takes the claim over (step 4), runs the request again, and places a second order.

The middleware can't close that gap, because the order and the saved answer are written by two different statements. So the order itself remembers its key. The unique index from step 3, on `(customer_id, idempotency_key)`, and in the store:

```rust
        let order = sqlx::query_as!(
            Order,
            r#"INSERT INTO orders (customer_id, idempotency_key, dish_id, quantity, total_kobo) VALUES ($1, $2, $3, $4, $5)
               ON CONFLICT (customer_id, idempotency_key) DO NOTHING
               RETURNING id, customer_id, dish_id, quantity, total_kobo AS "total: Kobo", status AS "status: Status""#,
            customer_id,
            idempotency_key,
            dish_id,
            quantity,
            price * i64::from(quantity)
        )
        .fetch_optional(&mut *tx)
        .await?;

        let Some(order) = order else {
            // This customer already placed an order with this key. Roll back the plate we just took
            // (dropping `tx` does it), and give back the first order.
            drop(tx);
            let first = sqlx::query_as!(
                Order,
                r#"SELECT id, customer_id, dish_id, quantity, total_kobo AS "total: Kobo", status AS "status: Status"
                   FROM orders WHERE customer_id = $1 AND idempotency_key = $2"#,
                customer_id,
                idempotency_key
            )
            .fetch_one(&self.pool)
            .await?;
            return Ok(Some(first));
        };
```

1. **`ON CONFLICT ... DO NOTHING`**: a second order with the same customer and key isn't inserted, and no row comes back.
2. **`drop(tx)`** rolls back the transaction, giving back the plate the guarded `UPDATE` just took. Lesson 8's rollback-on-`Drop`, called on purpose. (`drop` would happen at the `return` anyway; writing it says it's meant.)
3. **Then the first order is returned**, as if it had just been placed.
4. **`NULL`s never clash in a unique index.** v1's orders have no customer, and orders without a key have no key, so neither is affected.

The handler reads the key with a tiny extractor, `IdempotencyKey(Option<String>)`, that never refuses, and passes it through `OrderService::place` to the store. So the guarantee is in two places, for two different failures: the middleware replays answers and stops races; the index stops a second order, whatever else goes wrong.

A database test for the second layer:

```rust
    #[sqlx::test]
    async fn one_key_makes_one_order_and_takes_one_plate(pool: PgPool) {
        let orders = service_at(&pool, 12).await;
        sqlx::query!("INSERT INTO users (email, name, password_hash) VALUES ('ada@example.com', 'Ada', 'x')").execute(&pool).await.unwrap();

        let new = || NewOrder { dish_id: 1, quantity: 2 };
        let first = orders.place(new(), Some(1), Some("phone-retry-1")).await.unwrap();
        let again = orders.place(new(), Some(1), Some("phone-retry-1")).await.unwrap();
        assert_eq!(first.id, again.id, "the same order back");

        let left = sqlx::query_scalar!("SELECT portions_left FROM dishes WHERE id = 1").fetch_one(&pool).await.unwrap();
        assert_eq!(left, 3, "5 plates, minus 2, once");
    }
```

It calls the service twice, skipping the middleware entirely, as a crash-and-retry would: one order, and the plates taken once.

## Trying it
<!-- bite: af0ca0fe-d48d-44b8-9d8c-7324652a680b -->

From a run of this lesson's code, as Ada:

```text
$ first try, key A
HTTP/1.1 201 Created
location: /v2/orders/8
{"data":{"id":8,"dishId":2,"quantity":2,"total":{"amount":240000,"currency":"NGN"},"status":"pending"}}

$ the retry, key A
HTTP/1.1 201 Created
idempotent-replayed: true
location: /v2/orders/8
{"data":{"id":8,"dishId":2,"quantity":2,"total":{"amount":240000,"currency":"NGN"},"status":"pending"}}

$ key A, different body
HTTP/1.1 422 Unprocessable Entity
{"type":".../problems/idempotency-key-reused","title":"Key already used",...}

$ two at the same instant, key B
HTTP/1.1 409 Conflict
{"type":".../problems/idempotency-in-progress","title":"Still working on it",...}
HTTP/1.1 201 Created
location: /v2/orders/9

$ key C, no plates left
HTTP/1.1 422 Unprocessable Entity
{"type":".../problems/not-enough-portions",...}

$ key C again, after Mama cooks more
HTTP/1.1 201 Created
location: /v2/orders/10
```

The retry is the same order 8, byte for byte. The two at once got one order and one "wait". The refused order gave its key back, so the same key worked once there were plates. And the database ends with three orders that have keys, one per key.

`cargo test` runs 25.

## What the client must do
<!-- bite: f3b5a856-1e79-444e-ada8-9628906e164e -->

The server can only keep its half of the promise. The phone app must:

1. **Make one key per intention**, a fresh UUID when the customer taps "order", and keep it until that order is settled.
2. **Send the same key on every retry** of that order, and a new key for a new order. Making a fresh key per attempt defeats the whole thing.
3. **On 409 `idempotency-in-progress`**, wait `Retry-After` seconds and retry with the same key.
4. **Back off between retries** (wait 1 second, then 2, then 4), so a struggling server isn't flooded with retries.

The docs page says so, in `place_order`'s description of the header.

## The Rust in this lesson
<!-- bite: 689c2d19-fdc7-4900-a430-e85feb6a0bf3 -->

1. **`INSERT ... ON CONFLICT ... DO UPDATE ... WHERE ... RETURNING`** in a checked query, and **`AS "won!"`** to say a column is never `NULL`.
2. **An enum for a store's answer**, `Claim`, with a variant carrying named fields.
3. **`#[derive(FromRef)]` on a middleware's own state**, so it can hold several things.
4. **`Request::into_parts` and `Request::from_parts`**, and the same for `Response`: take apart, read the body, put back together.
5. **`axum::body::to_bytes(body, limit)`**: read a whole body, refusing one over the limit.
6. **`Body::from(bytes)`**: a body from bytes in memory.
7. **`Sha256::new().chain_update(...).finalize()`**: hash several pieces as one.
8. **`StatusCode::from_u16` and `is_success`**.
9. **`drop(tx)`**: end a value's life early, on purpose, here to roll back.
10. **A match guard on a `Result`**, `Ok(k) if (1..=255).contains(&k.len()) =>`.

## Your project so far
<!-- bite: a49c8856-1ee6-40f5-a85d-d9d338d656e2 -->

```text
mama-put/
├── migrations/
│   └── 0007_idempotency.sql   ← idempotency_keys; orders.idempotency_key, unique per customer
└── src/
    ├── main.rs            ← + Idempotency { store, keys }
    ├── lib.rs             ← AppState.idempotency; the middleware on v2's orders router
    ├── docs.rs            ← place_order documents the Idempotency-Key header
    ├── http/
    │   ├── idempotency.rs ← IdempotencyStore (claim, complete, release), Claim, idempotent, replay, IdempotencyKey
    │   └── security.rs    ← CORS exposes Idempotent-Replayed
    └── orders/
        ├── store.rs       ← the order INSERT carries the key; ON CONFLICT returns the first order
        ├── service.rs     ← place takes the key; 1 more test
        └── handlers.rs    ← place reads IdempotencyKey
```

## Common mistakes
<!-- bite: 4b9ef14f-dc0f-4d27-848e-59cefbbaea74 -->

1. **"Check, then claim" in two statements.** Two copies at the same instant both see nothing and both run. Claim in one statement.
2. **A key per attempt instead of per intention.** Every retry looks new. The key is made once, when the customer taps.
3. **Replaying for a different body.** A reused key replays the wrong order. Fingerprint the request.
4. **Claims that never expire.** A crash leaves the key "in progress" forever. Let an old, unanswered claim be taken over.
5. **Keys shared between customers.** Ada's `order-1` replays to Bayo. Scope them by user.
6. **Saving refusals.** A 422 for no plates would replay forever, even after Mama cooks more. A refusal changed nothing; let it run again.
7. **Only the middleware.** A crash between the order and the saved answer still makes two orders. Put the key on the order too.
8. **Reading a body twice.** It's a stream. Read it once into bytes, then rebuild the request.

## Check your understanding
<!-- bite: f9c03cbc-b3f1-4009-8020-97a5557f1ce3 -->

1. Why is `POST /v2/orders` the route that needs an idempotency key, and `PATCH /v2/menu/{id}` doesn't?
2. Two copies of a request with the same key arrive at the same instant. What does Postgres do with the two `INSERT`s, and what does each client get?
3. What is the `WHERE` in the claim's `ON CONFLICT ... DO UPDATE` for?
4. Why does the middleware fingerprint the body, and what happens when the fingerprint differs?
5. Why are refusals not saved for replaying?
6. Why does the middleware read the request body into bytes and build a new request?
7. What failure does the unique index on `(customer_id, idempotency_key)` cover that the middleware can't?
8. Why must the phone app make the key when the customer taps "order", not when it sends the request?

<details>
<summary>Answers, after your attempt</summary>

1. Because `POST` means "do this", and doing it twice does it twice: two orders, two charges. Our `PATCH`es set values ("portionsLeft is 20"), so sending one twice leaves things the same as sending it once.
2. The primary key on `(user_id, key)` lets exactly one insert in. That one gets a row back from `RETURNING` and runs the request. The other conflicts, gets nothing back, reads the row, finds no answer yet, and gets a 409 "still working on it" with `Retry-After: 1`.
3. To take over a claim that was never answered and is over a minute old: a request whose server stopped half-way. Without it, that key would say "still working on it" forever.
4. So a retry can be told from a different request that reused a key by mistake. If the fingerprint differs, the answer is a 422 `idempotency-key-reused`, instead of replaying an order the client didn't mean.
5. Because a refusal changed nothing, so running the request again is safe, and might work (more plates, the shop now open). Saving it would replay the old refusal forever. Also, at this layer a refusal has no body yet: `write_problems` writes it further out.
6. Because a body is a stream that can only be read once. The middleware needs the bytes to fingerprint them, so it reads them, then builds a new request from the head and those bytes, so the handler can read the body as usual.
7. The server dying after the order is committed but before the answer is saved. The claim stays unanswered; a later retry takes it over and runs again. The unique index means that run can't insert a second order, and returns the first one instead.
8. Because the key names the intention, "this order", not the attempt. Made at send time, every retry would get a new key and look like a new order.

</details>

## Practice
<!-- bite: 7b67db89-82e1-4411-b2df-bade26b8fd89 -->

1. Delete keys older than 24 hours: write the SQL, and decide where it should run (lesson 18 has a home for it).
2. Make the fingerprint include the user's id and the method too. Is either needed, given the table's key and the `POST` check?
3. Add idempotency to `POST /v2/menu`. What should the second layer be for dishes?
4. Write a `oneshot` test that sends the same order twice through the whole app and checks the second has `idempotent-replayed: true` and the same body.
5. Replay the original `Content-Type` instead of assuming `application/json`: save it in a new column, with a migration.

**Done when** a v2 `POST` with an `Idempotency-Key` runs once and replays its answer to retries (marked `Idempotent-Replayed`), a reused key with a different body is a 422, two at once give one result and one 409, refusals release the key, a stuck claim is taken over after a minute, the same customer and key can never make two orders even if the middleware is skipped, and `cargo test` passes.

## Before moving on
<!-- bite: 4147f248-6420-4f85-b411-4901944bdd54 -->

Mama Put now knows who's calling, what each person may do, defends itself against the everyday attacks, and a retried order happens exactly once. With this lesson's key and lesson 8's guarded plate together, a customer on a bus can tap "order" as many times as the tunnel makes them, and get one jollof.

There are 25 tests now, but they grew one lesson at a time: some test services, some test SQL, two test the whole app with `oneshot`, and there's no shared way to build an app for a test, log in as Ada, or check a problem response. Next lesson closes Part 3: testing, with one test app builder, `oneshot` against the whole router, a test for every rule from lessons 12 to 15, and what's worth testing at each level.

## Related
<!-- bite: 48a3d7b3-0595-43e6-bb40-fcfe3cc745c0 -->

- [[backend/frameworks/axum/16-testing|Next: Testing]]
- [[backend/frameworks/net-http/15-idempotency|The same lesson in net/http]] — a response recorder, and the same two layers
- [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — the idea, and how clients should retry
- [[backend/frameworks/axum/08-data-with-postgres|Data with PostgreSQL]] — the guarded update and rollback on `Drop` this lesson leans on

## About this lesson
<!-- bite: 7f395080-b8eb-493e-98d1-72223faf781a -->

**Level:** Advanced. Lesson 15 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8 and sqlx 0.9. Covers which HTTP methods are idempotent, an `Idempotency-Key` scheme scoped per customer, claiming a key in one `INSERT ... ON CONFLICT ... DO UPDATE ... WHERE` with takeover of stale claims, a request fingerprint over path and body, a middleware that buffers request and response bodies with `into_parts`, `to_bytes` and `from_parts`, replaying saved answers with `Idempotent-Replayed`, 409 with `Retry-After` while in progress and 422 for a reused key, releasing the key on refusals and why refusals aren't saved in this design, a second layer with a unique index and `ON CONFLICT DO NOTHING` that returns the first order and rolls back with `drop(tx)`, and what the client must do.
