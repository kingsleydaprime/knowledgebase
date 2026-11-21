---
id: c20cb3ad-bd33-4082-a6a7-82595b3e1205
---

# Idempotency

**An operation is idempotent when doing it twice has the same effect as doing it once. Making an API request idempotent means that if a client sends the same request again, because it never got the answer, nothing happens twice: no second order, no second payment.** You've seen the opposite. A slow website, a "Pay" button pressed twice, and two charges on your card. Somewhere, a backend wasn't idempotent.

## Before you start
<!-- bite: f7b653f4-d4d2-4e90-ac46-7097f464ad78 -->

You should have logins and permissions from [[backend/frameworks/express/13-authorization|lesson 13]] and the security limits from [[backend/frameworks/express/14-security|lesson 14]].

After this lesson you will be able to:

1. Say which HTTP methods are already idempotent, and why POST isn't.
2. Explain how an `Idempotency-Key` header makes a POST safe to retry.
3. Build idempotency middleware that stores each key's result and replays it, handles a retry that arrives *while* the first request is still running, and refuses a key reused for a different request.
4. Back it up with a database constraint, so duplicates are impossible even if the middleware's record is lost.

## Where we stopped
<!-- bite: 83bb903c-873b-41a9-8dea-333581418931 -->

Lesson 14 ended with Ada in a tunnel:

1. She taps "Place order". The request reaches us.
2. We take the portions, write the order, and send back `201`.
3. The answer is lost: the train went under a hill.
4. Ada's app waits, gives up, and tries again. A good app *should* retry: most failures are brief.
5. We take the portions again and write a **second** order.

From our side, both requests looked perfectly valid. Nothing in lessons 1 to 14 can tell "Ada wants two plates" from "Ada's phone asked twice". And it doesn't only happen to apps in tunnels: proxies retry, load balancers retry, people double-tap.

## The kid version
<!-- bite: 18d8e575-ad19-4fd4-9e6d-8ca12a2f3293 -->

Ada sends her little brother to Mama Put with a paper: "1 jollof, for Ada". On the way back, he drops the food. He runs back and hands Mama the same paper again.

If Mama just reads the paper, she cooks and charges a second plate. But Ada's papers are numbered: this one says **"Order slip 7"**. Mama keeps every slip she's served in a box. She checks: "Slip 7? I already served this one. Here's the same plate again, and you've already paid." No second charge.

The slip number is the **idempotency key**. The box is our database table.

**Where the picture stops working.** Mama would cook a fresh plate. An API **replays the same answer**: the same order, with the same id, so Ada's phone ends up exactly where it would have been if the first answer had arrived.

## Terms used in idempotency
<!-- bite: e9dabb07-fa54-4161-bd1a-b5ff61d9d56a -->

1. **Idempotent**: This describes an operation where doing it many times has the same effect as doing it once. Setting a light switch to "on" is idempotent; flicking it is not.
2. **Retry**: This is sending the same request again because the first answer didn't arrive, or was an error that might be temporary.
3. **Idempotency key**: This is a unique value the client creates for one action (one tap of "Place order") and sends with every retry of that action, in the `Idempotency-Key` header. A new action gets a new key.
4. **Replay**: This is answering a retry with the stored answer from the first time, instead of doing the work again.
5. **Request fingerprint**: This is a hash of the request's method, path and body, stored with the key, so we can tell if someone reuses a key for a *different* request.

## Step 1: which methods are already safe?
<!-- bite: de3ee7d5-f034-4306-b613-77b1a11d529e -->

The HTTP rules already say which methods must be idempotent:

1. **GET**: reading the menu twice changes nothing. Idempotent.
2. **PUT**: "set dish 3 to *exactly this*". Doing it twice leaves the same dish. Idempotent.
3. **DELETE**: "remove dish 3". The second time, it's already gone; the *effect* is the same. (The second answer may be 404 instead of 204, and that's fine: idempotency is about the effect, not the answer.)
4. **PATCH**: depends. `{"status": "ready"}` set twice is the same; "add one to the quantity" twice is not. Ours only set values, so they're idempotent.
5. **POST**: "create a new order". Twice means two orders. **Not idempotent.**

That's why clients, proxies and libraries happily retry GET, PUT and DELETE, and should be careful with POST. Our job is to make the POSTs that matter (placing an order today, paying in lesson 17) safe to retry too.

## Step 2: the plan
<!-- bite: 2ba34cba-feef-4554-9482-565f8d16e3a0 -->

The client creates a key, usually a UUID, when the customer taps "Place order", and sends it on the first attempt and every retry:

```text
POST /v2/orders
Authorization: Bearer eyJ...
Idempotency-Key: 9b2f6c1e-4a0d-4f5b-8f33-1c7e2a9d5b10
Content-Type: application/json

{"dishId":"1","quantity":2}
```

When it arrives, our middleware does one of four things:

1. **A new key**: claim it, do the work, store the answer, send it.
2. **A key we've finished**: send the stored answer again, without doing anything.
3. **A key still in progress** (the retry arrived before the first one finished): answer `409 Conflict`, "still working on it, try again in a moment".
4. **A key we've seen, but with a different body** (same key, now asking for 5 plates): refuse with `422`. Reusing a key for a different request is a bug in the client, and guessing what it meant would be worse.

The key belongs to the **user**: Ada's key `abc` and Bayo's key `abc` are different keys. Otherwise one customer could replay another's order.

## Step 3: the table
<!-- bite: a2a5fd64-c95c-4384-b113-422a01704de3 -->

`migrations/010_idempotency.sql`:

```sql
CREATE TABLE idempotency_keys (
  user_id         bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  key             text   NOT NULL,
  request_hash    text   NOT NULL,
  state           text   NOT NULL DEFAULT 'in_progress' CHECK (state IN ('in_progress', 'done')),
  response_status integer,
  response_body   jsonb,
  created_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, key)
);

ALTER TABLE orders ADD COLUMN idempotency_key text;
CREATE UNIQUE INDEX orders_customer_idempotency_idx
  ON orders (customer_id, idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

Two layers, on purpose:

1. **`idempotency_keys`** stores each key and its answer, so we can **replay** the exact response. It works for any route.
2. **The unique index on `orders`** makes a second order with the same key **impossible**, at the database level. If anything ever goes wrong with the first layer (we'll see how in Step 6), the database still refuses the duplicate.

`jsonb` is Postgres's type for storing JSON, so the response body goes in as-is.

## Step 4: the store
<!-- bite: 2bc67abd-c142-42df-908e-995b74d7bcd0 -->

`src/shared/idempotency.store.ts`:

```ts
import type pg from "pg";

export type IdempotencyRecord = {
  requestHash: string;
  state: "in_progress" | "done";
  responseStatus: number | null;
  responseBody: unknown;
};

export function createPgIdempotencyStore(pool: pg.Pool) {
  return {
    async claim(userId: string, key: string, requestHash: string) {
      const inserted = await pool.query(
        `INSERT INTO idempotency_keys (user_id, key, request_hash)
         VALUES ($1, $2, $3)
         ON CONFLICT (user_id, key) DO NOTHING`,
        [userId, key, requestHash],
      );
      if (inserted.rowCount === 1) return { kind: "claimed" as const };

      const { rows } = await pool.query(
        `SELECT request_hash, state, response_status, response_body
           FROM idempotency_keys WHERE user_id = $1 AND key = $2`,
        [userId, key],
      );
      const row = rows[0];
      return {
        kind: "existing" as const,
        record: {
          requestHash: row.request_hash,
          state: row.state,
          responseStatus: row.response_status,
          responseBody: row.response_body,
        } satisfies IdempotencyRecord,
      };
    },

    async complete(userId: string, key: string, status: number, body: unknown) {
      await pool.query(
        `UPDATE idempotency_keys
            SET state = 'done', response_status = $3, response_body = $4
          WHERE user_id = $1 AND key = $2`,
        [userId, key, status, JSON.stringify(body ?? null)],
      );
    },

    async release(userId: string, key: string) {
      await pool.query("DELETE FROM idempotency_keys WHERE user_id = $1 AND key = $2", [userId, key]);
    },
  };
}

export type IdempotencyStore = ReturnType<typeof createPgIdempotencyStore>;
```

The heart of it is `claim`, and it's the same trick you've now seen twice (the last plate in lesson 8, the refresh token in lesson 12). `INSERT ... ON CONFLICT DO NOTHING` either inserts the key, meaning **we** are the first and own it, or does nothing because it's already there. Two retries arriving at the same instant can't both "own" the key: the primary key makes Postgres pick exactly one.

## Step 5: the middleware
<!-- bite: 5daac55d-f348-4e36-992b-8d2cc357e8f8 -->

`src/shared/idempotent.ts`:

```ts
import { createHash } from "node:crypto";
import type { Request, Response, NextFunction } from "express";
import { AppError, conflict } from "./errors.ts";
import type { IdempotencyStore } from "./idempotency.store.ts";

const KEY_PATTERN = /^[A-Za-z0-9_-]{8,128}$/;

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    const entries = Object.entries(value).sort(([a], [b]) => (a < b ? -1 : 1));
    return `{${entries.map(([k, v]) => `${JSON.stringify(k)}:${stableJson(v)}`).join(",")}}`;
  }
  return JSON.stringify(value ?? null);
}

function fingerprint(req: Request) {
  return createHash("sha256")
    .update(`${req.method} ${req.baseUrl}${req.path}\n${stableJson(req.body)}`)
    .digest("hex");
}

export function createIdempotent(store: IdempotencyStore) {
  return async function idempotent(req: Request, res: Response, next: NextFunction) {
    const key = req.get("Idempotency-Key");
    if (!key) {
      throw new AppError("invalid", "idempotency-key-required",
        "Send an Idempotency-Key header: a new random value for each action, the same value on every retry.");
    }
    if (!KEY_PATTERN.test(key)) {
      throw new AppError("invalid", "bad-idempotency-key", "Idempotency-Key must be 8 to 128 letters, digits, '-' or '_'.");
    }

    const userId = req.user!.id;
    const requestHash = fingerprint(req);
    const claim = await store.claim(userId, key, requestHash);

    if (claim.kind === "existing") {
      const record = claim.record;
      if (record.requestHash !== requestHash) {
        throw new AppError("rule_broken", "idempotency-key-reused",
          "This Idempotency-Key was already used for a different request. Use a new key for a new action.");
      }
      if (record.state === "in_progress") {
        res.set("Retry-After", "2");
        throw conflict("request-in-progress", "The same request is still being processed. Try again in a moment.");
      }
      res.set("Idempotent-Replayed", "true");
      res.status(record.responseStatus!).json(record.responseBody);
      return;
    }

    // We own this key. Remember what we answer, then store it when the answer has gone out.
    res.locals.idempotencyKey = key;
    let body: unknown;
    const send = res.json.bind(res);
    res.json = (value: unknown) => {
      body = value;
      return send(value);
    };

    res.on("finish", () => {
      const saved =
        res.statusCode >= 500
          ? store.release(userId, key)
          : store.complete(userId, key, res.statusCode, body);
      saved.catch((err) => console.error({ event: "idempotency-store-failed", key, err }));
    });

    next();
  };
}
```

Walk through it:

1. **The key is checked like any input**: required, and a sensible shape. A UUID fits.
2. **The fingerprint** is a hash of the method, the path and the body. `stableJson` writes the body with its keys sorted, so `{"dishId":"1","quantity":2}` and `{"quantity":2,"dishId":"1"}`, which mean the same thing, give the same fingerprint.
3. **`claim`** decides which of the four cases we're in.
4. **Replays** send the stored status and body, plus an `Idempotent-Replayed: true` header so the client (and you, when debugging) can see it was a replay.
5. **When we own the key**, we wrap `res.json` so we can *see* what the route sends, without changing the route at all. When the response has finished going out (`finish`, from lesson 3's logger), we store it.
6. **5xx answers release the key** instead of storing it. A 500 means *we* failed, maybe for a moment; the client should be able to retry and have it actually work. A 4xx (say, `dish-unavailable`) is stored and replayed: retrying won't make the pot fuller.

And the route only gains one word:

```ts
router.post("/", requireUser, idempotent, async (req, res) => {
  const input = validate(PlaceOrderSchema, req.body, "body");
  const order = await ordersService.place(req.user!, input.dishId, input.quantity, res.locals.idempotencyKey);
  res.status(201).location(`${req.baseUrl}/${order.id}`).json({ data: order });
});
```

`requireUser` comes first, because keys belong to users.

## Step 6: the second layer, in the database
<!-- bite: ac1f8995-275c-4590-8997-f00b52a7a861 -->

The middleware stores the answer *after* it has been sent. What if the server crashes in the gap: the order is committed, but `complete` never runs? The key stays `in_progress` forever, and in a day, when the key is cleaned up, a retry would place the order again.

That's what the unique index on `orders` is for. The key also travels into the order itself:

```ts
// orders.pg-repository.ts, inside placeTakingPortions
const { rows } = await tx.query<OrderRow>(
  `INSERT INTO orders (dish_id, quantity, total_naira, customer_id, idempotency_key)
   VALUES ($1, $2, $3, $4, $5)
   ON CONFLICT (customer_id, idempotency_key) WHERE idempotency_key IS NOT NULL DO NOTHING
   RETURNING *`,
  [dishId, quantity, total, customerId, idempotencyKey ?? null],
);
if (rows.length === 0) {
  // Same customer, same key: this order already exists. Undo the portions we just took.
  throw new DuplicateOrder();
}
```

Because the insert is inside the transaction from lesson 8, throwing **rolls back** the portions we took a moment ago. Then the repository looks up the existing order by `(customer_id, idempotency_key)` and returns it. Whatever happened to the middleware's record, the customer gets one order and pays for one plate.

That's the pattern for anything involving money: **the key lives in the same transaction as the effect it protects.** The table of answers makes retries smooth; the constraint makes duplicates impossible.

## Trying it
<!-- bite: 04b45ca4-e703-4ae9-962e-a1df78bde437 -->

```bash
KEY=$(node -e "console.log(crypto.randomUUID())")

curl -si -X POST http://localhost:3000/v2/orders \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}' | head -1
# HTTP/1.1 201 Created

# The "retry": exactly the same request, same key
curl -si -X POST http://localhost:3000/v2/orders \
  -H "Authorization: Bearer $TOKEN" -H "Idempotency-Key: $KEY" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}' | grep -E "HTTP|Replayed|\"id\""
```

Predict before you run the second one: what status, which order id, and how many portions are left? It answers `201` again, with `Idempotent-Replayed: true` and **the same order id**, and the portions only went down once.

Then:

1. Same key, `"quantity":5`. Predict: 422 `idempotency-key-reused`.
2. No key at all. Predict: 400 `idempotency-key-required`.
3. Two copies of the first request with a **new** key, sent at the same moment (`&`). Predict: one 201, and the other either a 409 `request-in-progress` or a replayed 201. Never two orders.

## What the client must do
<!-- bite: 3e7bafac-1f07-46e2-8e1e-549e7a4400d2 -->

Idempotency is a promise between both sides. The phone app's half:

1. **Make a new key when the customer acts**, not per request. One tap of "Place order" is one key.
2. **Reuse that key on every retry** of that action, even after an app restart if it can (save it with the unsent order).
3. **Retry with growing gaps**: wait 1 second, then 2, then 4, with a little randomness, so a struggling server isn't hammered by every phone at once. [[backend/frameworks/express/26-calling-services-safely|Lesson 26]] builds exactly this for our own services.
4. **On 409 `request-in-progress`**, wait `Retry-After` seconds and try again.

## The TypeScript in this lesson
<!-- bite: 59314bce-f1db-4181-9709-9be8d9c74c15 -->

1. **`{ kind: "claimed" as const }` and `{ kind: "existing" as const, record }`**: A discriminated union again (lesson 4). After `if (claim.kind === "existing")`, TypeScript knows `claim.record` is there.
2. **`satisfies IdempotencyRecord`**: Checks the object fits the type, without changing what TypeScript remembers about it (lesson 11).
3. **`function stableJson(value: unknown): string`** calling itself: a **recursive** function. For an object, it writes each value by calling `stableJson` on it, so nested objects get sorted too.
4. **`Array.isArray(value)`**: The safe way to ask "is this an array?". `typeof []` is `"object"`, so `typeof` alone can't tell.
5. **`.sort(([a], [b]) => (a < b ? -1 : 1))`**: Sort the `[key, value]` pairs by key. The function returns a negative number if `a` comes first. `([a], [b])` destructures each pair to just its key.
6. **`const send = res.json.bind(res)`**: Saves the original `res.json`, fixed to `res`, so our replacement can still call it. Without `.bind(res)`, calling it later would lose track of which response it belongs to.
7. **`res.json = (value: unknown) => { ...; return send(value); }`**: Replacing a method on one object, for one request only. The route doesn't know; it just calls `res.json` as always. This pattern is sometimes called **wrapping** or **monkey-patching**; use it sparingly, and keep it in one well-named place like this.
8. **`saved.catch((err) => ...)`**: `finish` handlers can't be `async` in a useful way, so we start the save and attach a `catch`, so a failure is logged instead of crashing the process as an unhandled rejection.
9. **`record.responseStatus!`**: Safe here, because a `done` record always has a status.
10. **`class DuplicateOrder extends Error {}`**: An error class with no body, used only so the repository can recognise its own signal with `instanceof` and turn it into "find the existing order".

## Your project so far
<!-- bite: a3bc9d8f-ff06-4eb1-92f0-a19719bd50cf -->

```text
mama-put-api/
├── .env · .env.example · .gitignore · package.json · tsconfig.json
├── migrations/
│   ├── 001 … 009
│   └── 010_idempotency.sql       ← NEW: idempotency_keys; orders.idempotency_key, unique per customer
├── uploads/photos/
├── openapi/      v1.json · v2.json (Idempotency-Key header on POST /orders; 409 and 422 documented)
└── src/
    ├── server.ts                 ← builds the idempotency store and middleware
    ├── app.ts · api.ts · types/express.d.ts
    ├── auth/ · admin/ · docs/ · db/ · menu/
    ├── orders/
    │   ├── orders.routes.ts      ← POST / uses requireUser, then idempotent
    │   ├── orders.service.ts     ← place() passes the key through
    │   └── orders.pg-repository.ts ← key stored with the order; a duplicate rolls back and returns the original
    └── shared/
        ├── idempotency.store.ts  ← NEW: claim (INSERT … ON CONFLICT DO NOTHING), complete, release
        ├── idempotent.ts         ← NEW: the middleware: four cases, fingerprint, replay
        └── rate-limits.ts · cursor.ts · pick.ts · errors.ts · request-id.ts · validate.ts
            log-requests.ts · not-found.ts · error-handler.ts
```

## Common mistakes
<!-- bite: 8da4e7c4-d123-4cd4-8d74-90d64459c9bb -->

1. **A new key per retry.** Then every retry looks new, and you're back to duplicates. One key per *action*.
2. **Keys that aren't scoped to the user.** One customer could replay another's response. Key on `(user_id, key)`.
3. **Ignoring a changed body.** Same key, different body is a client bug. Refuse it with 422; don't guess.
4. **Storing 5xx answers.** Then a brief failure is "remembered" and every retry fails too. Release the key on 5xx.
5. **Check-then-insert for claiming keys.** Two retries at the same instant both see "no key" and both run. Let the primary key decide.
6. **Only the middleware, for money.** The stored answer can be lost in a crash. Put the key in the same transaction as the effect, with a unique constraint.
7. **Keeping keys forever.** The table grows without end. Keep them for a day or so; we add a cleanup job in [[backend/frameworks/express/18-background-jobs|lesson 18]].

## Check your understanding
<!-- bite: 8471dde3-6b2e-467e-9f7e-ed5603834434 -->

1. Why does the server answer `201` with the *same* order id on a retry, instead of `409 "already exists"`?
2. Ada's first request is still taking portions when her retry arrives. What does the retry get, and why not just wait?
3. Why are 4xx answers stored and replayed, but 5xx answers released?
4. The server crashes right after committing Ada's order, before `complete` runs. Tomorrow, after cleanup, her app retries with the same key. What stops a second order?

<details>
<summary>Answers, after your attempt</summary>

1. Because the client should end up exactly where it would have been if the first answer had arrived. Its code for "order placed" just works. A 409 would force every client to write special code for something that's normal.
2. A `409 request-in-progress` with `Retry-After: 2`. Holding the retry open until the first finishes would tie up a connection, and could wait forever if the first one hung. A quick, clear "try again shortly" is simpler and safer.
3. A 4xx is about the request itself (bad input, a finished dish), so retrying the same request will give the same answer: storing it is correct. A 5xx is our failure, often temporary, so the client must be allowed to retry and succeed.
4. The unique index on `orders (customer_id, idempotency_key)`. The insert finds the existing order, the transaction rolls back the portions it just took, and the repository returns the original order.

</details>

## Practice
<!-- bite: c3b4f61c-89f2-4ecf-8ef1-f8c82f9c6587 -->

1. Make `POST /orders/:id/cancel` (from lesson 13) idempotent with the same middleware. Cancelling an already-cancelled order with a *new* key should still give `409 already-cancelled`, not a second refund of portions.
2. Make the key optional for staff-only routes but required for `POST /orders`, by giving `createIdempotent` an option `{ required: boolean }`.
3. Write a SQL query (save it as `scripts/stale-idempotency-keys.sql`) that lists keys stuck `in_progress` for more than 10 minutes. These are what Step 6 protects against; it's worth being able to see them.

**Done when** a replayed order has `Idempotent-Replayed: true` and the same id; 20 parallel requests with one key create exactly one order; a changed body with the same key gets 422; and cancelling twice gives back the portions only once.

## Before moving on
<!-- bite: 16fbfc99-cf4d-440d-a19a-fa2417e319b5 -->

Mama Put API can now be retried safely. Same key, same answer, one order, whether the retry comes from a tunnel, a proxy or a double tap, and a database constraint backs it up.

We've built a lot now: fifteen lessons of rules, checks and edge cases. And every time, we checked it by hand with `curl`. Change one thing in the auth service tomorrow, and you'd have to run all of those `curl`s again to know nothing broke. Nobody does that. So the next lesson writes it all down as tests that run in seconds.

## Related
<!-- bite: 4e9f3295-a6a6-4ad0-b66f-a222f0c26da6 -->

- [[backend/frameworks/express/16-testing|Next: Testing]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]] — the idea in any framework
- [[backend/frameworks/express/08-data-with-postgres|Data with PostgreSQL]] — the transaction this builds on

## About this lesson
<!-- bite: e259448c-3a21-4baa-8c06-224f07b86125 -->

**Level:** Advanced. Lesson 15 of [[backend/frameworks/express/index|Express]]. Covers idempotent and non-idempotent methods, the `Idempotency-Key` header, a key store claimed atomically with `INSERT … ON CONFLICT DO NOTHING`, request fingerprints with stable JSON, the four cases (new, done, in progress, reused for a different request), replay with `Idempotent-Replayed`, releasing keys on 5xx, wrapping `res.json`, a unique constraint in the same transaction as the order, and the client's half of the contract.
