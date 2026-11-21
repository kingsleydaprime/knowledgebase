---
id: 63b60362-91cb-4260-86a3-9ad737b40698
---

# Payments and Webhooks

**A webhook is an HTTP request that another system sends to *your* server when something happens on its side. Instead of you asking "has Ada paid yet?" every few seconds, the payment company calls you and says "Ada just paid".** Payments are where you meet webhooks first, because a payment finishes on someone else's website, in someone else's time, and the only reliable way to hear about it is for them to tell you.

## Before you start
<!-- bite: 086edf79-6311-4b66-beb8-a457976e4f9d -->

You should have tested, idempotent orders from [[backend/frameworks/express/16-testing|lesson 16]], with money in kobo (from the practice in [[backend/frameworks/express/10-versioning|lesson 10]]).

You also need a free Paystack account in **test mode**. Test mode uses pretend money and test cards, so nothing real is charged. Your test secret key starts with `sk_test_`.

After this lesson you will be able to:

1. Explain why a payment can't be finished inside one request, and why the redirect back to your site can't be trusted.
2. Start a Paystack checkout from Express, with an amount in kobo and a reference you control.
3. Receive Paystack's webhooks: read the raw body, check the signature, and mark an order paid exactly once, however many times the webhook arrives.
4. Check a payment yourself as a backup, through Paystack's verify call.
5. Send your **own** signed webhooks to a delivery partner, with retries, so they can trust them the same way you trust Paystack.

## Where we stopped
<!-- bite: 16748712-d97c-454c-9de5-043f1bb78dc7 -->

Right now, placing an order writes a row and takes the portions. Nobody pays. Ada could order twenty plates of jollof and walk away.

Mama wants it simple: you order, you pay, and only then does the kitchen cook. And when the food is ready, the okada riders from **Okada Riders** (the delivery company Mama works with) should hear about it straight away, without someone phoning them.

So this lesson has two directions:

1. **Webhooks coming in**: Paystack telling us "this payment succeeded".
2. **Webhooks going out**: us telling Okada Riders "order 42 is ready for pickup".

## The kid version
<!-- bite: a6b716af-e2d5-4d9a-a59f-03a16d851c7a -->

Ada buys a plate, but she pays at the bank across the road, not at Mama's table. Mama can't see the bank.

Ada comes back and says "I've paid, see?" and waves a paper. Should Mama believe the paper? Anyone can write on paper.

So Mama and the bank agree on a better way. When someone pays, the bank sends its own messenger to Mama, with a note sealed with a stamp only the bank has. Mama checks the stamp, and *then* she believes it. If the messenger comes twice with the same note, she doesn't cook twice.

The messenger is the webhook. The stamp is the signature. Ada's paper is the redirect back to our website, and we never trust it by itself.

**Where the picture stops working.** A real messenger knows when he has delivered the note. A webhook doesn't always: the request can be lost, or our server can be down. So the bank keeps sending the same note until Mama says "got it", and Mama must be ready to receive the same note many times.

## Terms used in payments and webhooks
<!-- bite: 65a3da5b-c9ed-418d-bb1e-b468050af33f -->

1. **Payment provider**: This is the company that takes the card or bank transfer and moves the money, here **Paystack**. We never touch card numbers ourselves; the customer types them on Paystack's page.
2. **Checkout**: This is Paystack's payment page. We ask Paystack to start one, and it gives us a link to send the customer to.
3. **Reference**: This is a unique name *we* give each payment attempt, like `mp-42-0c9e…`. It's how we and Paystack talk about the same payment.
4. **Webhook**: This is an HTTP POST another system sends to a URL on our server when something happens. Paystack sends one called `charge.success` when a payment succeeds.
5. **Signature**: This is a code computed from the webhook's exact body and a secret only the sender and we know. If the code matches, the webhook really came from the sender and wasn't changed on the way.
6. **HMAC**: This is the recipe for that code: mix the secret and the message, then hash them. Without the secret, nobody can make a matching code.
7. **Raw body**: This is the request body exactly as the bytes arrived, before any JSON parsing. A signature is computed over those exact bytes.
8. **At-least-once delivery**: This means the sender promises every webhook arrives *at least* once, and sometimes more than once. Receivers must cope with duplicates.
9. **Verify call**: This is an API call *we* make to Paystack, asking "what really happened to payment `mp-42-…`?". It's our backup when we haven't heard a webhook.

## Step 1: why paying can't happen in one request
<!-- bite: 8b00f80d-67de-4486-8ada-9f0d51c46b03 -->

Every request so far went: request in, work, answer out, done. A payment can't work like that, because the middle part happens somewhere we can't see:

1. Ada asks us to pay for order 42.
2. We ask Paystack to start a checkout. Paystack gives us a link.
3. We send Ada the link. Her app opens Paystack's page.
4. Ada types her card details, and maybe a one-time code from her bank. This could take ten seconds or ten minutes. She might give up.
5. Paystack sends Ada's browser back to our site.
6. Separately, Paystack sends **us** a webhook: `charge.success` for `mp-42-…`.

Step 5 is tempting. Ada's browser lands on `https://mamaput.example/payment-done?reference=mp-42-…`, so why not mark the order paid right there?

Because anyone can type that URL. Ada (or someone less honest than Ada) can visit it without paying a kobo. And the opposite also happens: Ada pays, closes the tab before the redirect, and never lands on step 5 at all. The redirect is just the browser, and the browser is the customer's.

So, the rule for the whole lesson: **an order becomes paid only when Paystack itself says so**: through a signed webhook, or through a verify call we make to Paystack ourselves.

## Step 2: the tables
<!-- bite: 37fe285f-fb76-4b7f-b270-71bb7fd09512 -->

`migrations/011_payments.sql`:

```sql
CREATE TABLE payments (
  id           bigint  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  order_id     bigint  NOT NULL REFERENCES orders (id),
  reference    text    NOT NULL UNIQUE,
  amount_kobo  integer NOT NULL CHECK (amount_kobo > 0),
  status       text    NOT NULL DEFAULT 'started'
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

The first table is for webhooks coming in, the second for webhooks going out. We'll fill each in its own step. (The index has a `WHERE`, which makes it a **partial index**: it only holds rows that still need sending, so it stays small however many thousands have been delivered.)

Run `npm run migrate`.

## Step 3: talking to Paystack
<!-- bite: 21ec5efc-f045-4678-9d23-8e5b6e092488 -->

Every outside service gets one small file that knows how to talk to it, and the rest of the app talks to that file through a type we own. It's the same idea as the repositories: the orders service doesn't know about SQL, and the payments service won't know about Paystack's URLs.

`src/payments/payments.types.ts`:

```ts
export type PaymentProvider = {
  startCheckout(input: {
    email: string;
    amountKobo: number;
    reference: string;
    callbackUrl: string;
  }): Promise<{ checkoutUrl: string }>;

  verify(reference: string): Promise<{
    succeeded: boolean;
    amountKobo: number;
    currency: string;
  }>;
};

export type PaymentStatus = "started" | "succeeded" | "failed";

export type Payment = {
  id: string;
  orderId: string;
  reference: string;
  amountKobo: number;
  status: PaymentStatus;
};
```

Before writing the Paystack file, one new kind of error. So far every error was the *client's* fault (400s) or a broken rule. Now there's a third case: Paystack is down, or slow, or answers nonsense. That's nobody's fault in the request, and the usual status is **502 Bad Gateway**: "I'm a gateway to another service, and it let me down". In `src/shared/errors.ts`, add one more kind:

```ts
export type ErrorKind =
  | "invalid"
  | "unauthenticated"
  | "forbidden"
  | "not_found"
  | "conflict"
  | "rule_broken"
  | "upstream";       // a service we depend on failed
```

and in the error handler's table, `upstream: 502`. TypeScript won't compile until you add it, thanks to `Record<ErrorKind, number>` from [[backend/frameworks/express/07-errors|lesson 7]].

Now `src/payments/paystack.ts`:

```ts
import { z } from "zod";
import { AppError } from "../shared/errors.ts";
import type { PaymentProvider } from "./payments.types.ts";

const BASE_URL = "https://api.paystack.co";

const InitializeResponse = z.object({
  status: z.literal(true),
  data: z.object({ authorization_url: z.url(), reference: z.string() }),
});

const VerifyResponse = z.object({
  status: z.literal(true),
  data: z.object({
    status: z.string(),          // "success", "failed", "abandoned", ...
    amount: z.number().int(),    // in kobo
    currency: z.string(),
  }),
});

const upstream = (code: string) =>
  new AppError("upstream", code, "We couldn't reach the payment service. Please try again.");

export function createPaystack(secretKey: string): PaymentProvider {
  async function call<T>(path: string, schema: z.ZodType<T>, init: RequestInit = {}): Promise<T> {
    let res: Response;
    try {
      res = await fetch(`${BASE_URL}${path}`, {
        ...init,
        headers: {
          Authorization: `Bearer ${secretKey}`,
          "Content-Type": "application/json",
        },
        signal: AbortSignal.timeout(10_000),
      });
    } catch {
      throw upstream("payment-provider-unreachable");
    }
    if (!res.ok) throw upstream("payment-provider-error");

    const parsed = schema.safeParse(await res.json().catch(() => null));
    if (!parsed.success) throw upstream("payment-provider-bad-response");
    return parsed.data;
  }

  return {
    async startCheckout({ email, amountKobo, reference, callbackUrl }) {
      const body = await call("/transaction/initialize", InitializeResponse, {
        method: "POST",
        body: JSON.stringify({ email, amount: amountKobo, reference, callback_url: callbackUrl }),
      });
      return { checkoutUrl: body.data.authorization_url };
    },

    async verify(reference) {
      const body = await call(`/transaction/verify/${encodeURIComponent(reference)}`, VerifyResponse);
      return {
        succeeded: body.data.status === "success",
        amountKobo: body.data.amount,
        currency: body.data.currency,
      };
    },
  };
}
```

Three habits in there, and they matter for every outside service, not just Paystack:

1. **A timeout on every call.** `AbortSignal.timeout(10_000)` gives up after 10 seconds. Without it, if Paystack hangs, Ada's request hangs with it, and so does every request behind hers. [[backend/frameworks/express/26-calling-services-safely|Lesson 26]] goes much further with this.
2. **Validate what comes *back*.** We validate what clients send us (lesson 6). An outside service's answer is input too. If Paystack ever changes its response, we get a clear `payment-provider-bad-response`, not `Cannot read properties of undefined` somewhere deep in our code.
3. **Don't pass their errors to our customers.** Paystack's error messages are written for us, not for Ada, and can mention things she shouldn't see. She gets a calm "please try again"; the details go in our logs.

`amount` is in kobo. That's why we moved to kobo in lesson 10: ₦3,000 is `300000`. Send `3000` and Ada is asked to pay ₦30.

## Step 4: starting a checkout
<!-- bite: 228685c2-efea-46ac-a364-d42c8f9fcc4e -->

The customer flow is a new route: "pay for this order". It creates a payment attempt, asks Paystack for a checkout link, and gives the link back.

`src/payments/payments.service.ts`:

```ts
import { randomUUID } from "node:crypto";
import { conflict } from "../shared/errors.ts";
import type { AuthUser } from "../auth/auth.types.ts";
import type { OrdersService } from "../orders/orders.service.ts";
import type { UsersRepository } from "../auth/users.types.ts";
import type { PaymentsRepository } from "./payments.pg-repository.ts";
import type { PaymentProvider } from "./payments.types.ts";

export function createPaymentsService(deps: {
  payments: PaymentsRepository;
  ordersService: OrdersService;
  users: UsersRepository;
  provider: PaymentProvider;
  publicUrl: string;
  log: (message: string, details: object) => void;
}) {
  const { payments, ordersService, users, provider, publicUrl, log } = deps;

  return {
    async startCheckout(actor: AuthUser, orderId: string) {
      const order = await ordersService.get(actor, orderId);   // 404 if it isn't Ada's
      if (order.paidAt) throw conflict("order-already-paid", "This order is already paid.");

      const user = await users.findById(actor.id);
      if (!user) throw conflict("account-missing", "Your account no longer exists.");

      const reference = `mp-${order.id}-${randomUUID()}`;
      await payments.create({ orderId: order.id, reference, amountKobo: order.totalKobo });

      const { checkoutUrl } = await provider.startCheckout({
        email: user.email,
        amountKobo: order.totalKobo,
        reference,
        callbackUrl: `${publicUrl}/payment-done`,
      });
      return { reference, checkoutUrl };
    },

    // The ONE place that marks a payment as succeeded. Both the webhook and the
    // verify call end up here, and it's safe to call many times.
    async settle(reference: string, seen: { succeeded: boolean; amountKobo: number; currency: string }) {
      const payment = await payments.findByReference(reference);
      if (!payment) {
        log("payment for an unknown reference", { reference });
        return "unknown" as const;
      }
      if (!seen.succeeded) {
        await payments.markFailed(reference);
        return "failed" as const;
      }
      if (seen.currency !== "NGN" || seen.amountKobo !== payment.amountKobo) {
        log("PAYMENT AMOUNT MISMATCH", { reference, expected: payment.amountKobo, got: seen.amountKobo, currency: seen.currency });
        return "mismatch" as const;
      }
      const result = await payments.markSucceeded(reference);
      if (result === "order-was-already-paid") {
        log("order paid twice, refund needed", { reference, orderId: payment.orderId });
      }
      return result;
    },
  };
}

export type PaymentsService = ReturnType<typeof createPaymentsService>;
```

Look at what `startCheckout` reuses. `ordersService.get(actor, orderId)` already hides other customers' orders as 404 (lesson 13), so Bayo can't start paying for Ada's order. The amount comes from **our** database, never from the request: a client that sends `{ "amount": 100 }` has nowhere to put it.

The reference is `mp-` + the order id + a random UUID. Paystack only allows letters, digits, `-`, `.` and `=` in a reference, which is why it's dashes and not underscores. The order id makes it readable in Paystack's dashboard; the random part makes every attempt unique, so Ada's second try doesn't clash with her first.

Now `settle`, the most important function in this lesson. It checks three things before believing a "success":

1. **We know this reference.** A webhook for a payment we never started gets logged and ignored.
2. **The currency and amount are exactly what we asked for.** If someone found a way to pay ₦30 for a ₦3,000 order, this is where it stops. A mismatch is logged loudly, because it should never happen and someone must look.
3. **It hasn't already been counted.** That's inside `markSucceeded`, next.

And at the end, one awkward case. Ada opens checkout in two tabs and pays in both. Both succeed at Paystack; she's paid twice. Our database can't undo that, so we log "refund needed" and someone refunds the second payment from the Paystack dashboard. (Automating refunds is a good practice task once background jobs exist.)

`src/payments/payments.pg-repository.ts`, the important method:

```ts
async markSucceeded(reference: string) {
  return inTransaction(pool, async (tx) => {
    const updated = await tx.query<{ order_id: string }>(
      `UPDATE payments SET status = 'succeeded', settled_at = now()
        WHERE reference = $1 AND status = 'started'
       RETURNING order_id`,
      [reference],
    );
    if (updated.rowCount === 0) return "already-settled" as const;

    const order = await tx.query(
      "UPDATE orders SET paid_at = now() WHERE id = $1 AND paid_at IS NULL",
      [updated.rows[0].order_id],
    );
    return order.rowCount === 1 ? ("paid" as const) : ("order-was-already-paid" as const);
  });
},
```

The same trick for the third time: a conditional `UPDATE`. `WHERE status = 'started'` means only the **first** caller changes the row. If the webhook arrives twice at the same instant, Postgres locks the row for the first, and the second finds the status already `succeeded` and updates nothing. No double counting, without any "check, then update" race. The transaction makes sure the payment and the order change together, or not at all.

The other methods (`create`, `findByReference`, `markFailed` with `WHERE status = 'started'`) are plain SQL like lesson 8. Write them in the practice.

The route, in `src/payments/payments.routes.ts`:

```ts
router.post("/orders/:id/payments", requireUser, idempotent, async (req, res) => {
  const { id } = validate(IdParams, req.params, "params");
  const checkout = await paymentsService.startCheckout(req.user!, id);
  res.status(201).json({ data: checkout });
});
```

`idempotent` is lesson 15's middleware, so a retried "Pay" tap gets the same checkout link back instead of starting a second payment.

```bash
curl -X POST http://localhost:3000/v2/orders/42/payments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: pay-42-first-try"
```

```json
{
  "data": {
    "reference": "mp-42-0c9e2b7e-3f4a-4d61-9a55-1d2b8e6f7a10",
    "checkoutUrl": "https://checkout.paystack.com/abc123xyz"
  }
}
```

Open that link in a browser and you'll see Paystack's test checkout. Paystack's docs list the test cards that succeed or fail. Pay with a successful one. Paystack now wants to tell us about it, which brings us to the webhook.

## Step 5: receiving the webhook
<!-- bite: 544790f5-bc84-4c41-bb50-3eb5789facaa -->

When the payment succeeds, Paystack sends a POST to the webhook URL you set in its dashboard (Settings → API Keys & Webhooks). The body looks like this, trimmed:

```json
{
  "event": "charge.success",
  "data": {
    "id": 4099260516,
    "reference": "mp-42-0c9e2b7e-3f4a-4d61-9a55-1d2b8e6f7a10",
    "amount": 300000,
    "currency": "NGN",
    "status": "success"
  }
}
```

And one header that matters: `x-paystack-signature`. Paystack computes it as the **HMAC SHA-512** of the exact body bytes, using your secret key, written as hex. We compute the same thing. If they match, only someone with our secret key could have made this request, and that's Paystack.

### The raw body problem

Here's the catch, and it's specific to how Express works. `app.use(express.json())` runs for every request. It reads the body bytes, parses them into an object, and throws the bytes away. By the time our route runs, `req.body` is an object.

Can't we just `JSON.stringify(req.body)` to get the bytes back? No. Paystack might send `{"event": "charge.success"}` with a space; `JSON.stringify` gives `{"event":"charge.success"}` with none. Different bytes, different signature, and every real webhook fails. The signature must be checked on the bytes **exactly as they arrived**.

So the webhook route reads the body itself, with `express.raw`, and it must be mounted **before** `express.json()` in `app.ts`:

```ts
// src/app.ts
app.use(helmet());
app.use(requestId);
app.use("/webhooks/paystack", createPaystackWebhookRouter(deps));  // ← before express.json
app.use(generalLimit);
app.use(express.json({ limit: "20kb" }));
// ...the versioned API, docs, notFound, errorHandler
```

Middleware runs in order (lesson 3). When a webhook arrives, our router handles it and answers, and the request never reaches `express.json()`. Every other request walks past the webhook router, because the path doesn't match.

Notice it also sits above `generalLimit`. Paystack sends from a few addresses. On a busy lunch hour, hundreds of payments' webhooks from those same few addresses would hit our per-address limit, and we'd start refusing Paystack. The signature check is what protects this route instead.

It also lives outside `/v1` and `/v2`. Our API versions describe *our* shapes; this route receives Paystack's shape, which we don't control.

### Checking the signature

`src/shared/signatures.ts`:

```ts
import { createHmac, timingSafeEqual } from "node:crypto";

export function hmacHex(algorithm: "sha256" | "sha512", secret: string, message: Buffer | string) {
  return createHmac(algorithm, secret).update(message).digest("hex");
}

export function sameHex(a: string, b: string) {
  const x = Buffer.from(a, "hex");
  const y = Buffer.from(b, "hex");
  return x.length > 0 && x.length === y.length && timingSafeEqual(x, y);
}
```

Why not just `a === b`? Because `===` stops at the first different character. A wrong signature that starts with the right three characters takes a tiny bit longer to reject than one that's wrong from the first. With enough attempts and careful timing, an attacker can use that difference to discover the right signature one character at a time. `timingSafeEqual` always compares every byte, so it takes the same time whatever the answer. It throws if the two lengths differ, hence the length check first. And `Buffer.from("not hex!", "hex")` gives an empty buffer, hence `x.length > 0`.

### The webhook router

`src/payments/paystack.webhook.ts`:

```ts
import express from "express";
import { z } from "zod";
import { AppError } from "../shared/errors.ts";
import { hmacHex, sameHex } from "../shared/signatures.ts";
import type { PaymentsService } from "./payments.service.ts";
import type { ReceivedEvents } from "./received-events.ts";

const Envelope = z.object({ event: z.string(), data: z.looseObject({}) });

const Charge = z.object({
  id: z.number(),
  reference: z.string(),
  amount: z.number().int(),
  currency: z.string(),
  status: z.string(),
});

export function createPaystackWebhookRouter(deps: {
  paystackSecretKey: string;
  paymentsService: PaymentsService;
  receivedEvents: ReceivedEvents;
}) {
  const router = express.Router();

  router.post("/", express.raw({ type: "application/json", limit: "100kb" }), async (req, res) => {
    // 1. Is it really from Paystack?
    const signature = req.get("x-paystack-signature") ?? "";
    const raw: unknown = req.body;
    if (!Buffer.isBuffer(raw) || !sameHex(hmacHex("sha512", deps.paystackSecretKey, raw), signature)) {
      throw new AppError("unauthenticated", "bad-webhook-signature", "The webhook signature is not valid.");
    }

    // 2. Only now, parse it.
    const parsed = Envelope.safeParse(JSON.parse(raw.toString("utf8")));
    if (!parsed.success) throw new AppError("invalid", "bad-webhook-body", "Unexpected webhook body.");
    const { event, data } = parsed.data;

    // 3. Events we don't handle: say "thanks", or Paystack keeps resending them.
    if (event !== "charge.success") return res.sendStatus(200);

    const charge = Charge.parse(data);
    const eventKey = `${event}:${charge.id}`;

    // 4. Seen it already? Then we're done.
    if (await deps.receivedEvents.has("paystack", eventKey)) return res.sendStatus(200);

    // 5. Do the work (safe to repeat), THEN record it.
    await deps.paymentsService.settle(charge.reference, {
      succeeded: charge.status === "success",
      amountKobo: charge.amount,
      currency: charge.currency,
    });
    await deps.receivedEvents.record("paystack", eventKey);

    res.sendStatus(200);
  });

  return router;
}
```

Read it top to bottom; the order is the security.

1. **Signature first, before anything else.** Before parsing, before looking up anything. An unsigned request gets a 401 and costs us one hash. `Buffer.isBuffer(raw)` guards against a request with a different `Content-Type`: `express.raw` only reads `application/json`, so anything else leaves `req.body` empty, and that fails too.
2. **Parse only after.** We never run `JSON.parse` on bytes from a stranger. (A bad body that *is* signed by Paystack would be very strange; we answer 400 and it shows in our logs.)
3. **Answer 200 to events we don't care about.** Paystack sends other events too: transfers, refunds, subscriptions. If we answered 404, Paystack would think delivery failed and retry for days.
4. **Skip what we've handled.** Paystack's events don't carry their own event id, so we make a key from the event name and the charge's id, which is unique per transaction.
5. **Work first, record second.** This order is deliberate. If we recorded "handled" first and then crashed before `settle`, Paystack's retry would be skipped as "seen", and Ada's payment would be lost forever. Working first means the worst case is doing the work twice, and `settle` is built to be safe twice (the conditional `UPDATE` from step 4).

Which shows something important: the received-events table is a shortcut, not the real protection. The real protection is that `settle` is idempotent by itself. The table just saves us repeating work. Whenever you handle a webhook, ask "what if this exact one arrives twice, at the same time?", and make sure the answer is "nothing bad".

`src/payments/received-events.ts` is two small queries:

```ts
export function createReceivedEvents(pool: pg.Pool) {
  return {
    async has(provider: string, eventKey: string) {
      const { rowCount } = await pool.query(
        "SELECT 1 FROM webhook_events_received WHERE provider = $1 AND event_key = $2",
        [provider, eventKey],
      );
      return rowCount === 1;
    },
    async record(provider: string, eventKey: string) {
      await pool.query(
        `INSERT INTO webhook_events_received (provider, event_key) VALUES ($1, $2)
         ON CONFLICT DO NOTHING`,
        [provider, eventKey],
      );
    },
  };
}

export type ReceivedEvents = ReturnType<typeof createReceivedEvents>;
```

### Answer fast

Paystack waits only a short time for our 200. If we're slow, it counts as failed and sends it again. Our handler does two quick queries, so we're fine. But if handling a payment ever means sending an email, a receipt PDF, and a notification, don't do it here. Record the payment, answer 200, and do the slow work afterwards. That's exactly what [[backend/frameworks/express/18-background-jobs|lesson 18]] is for.

## Step 6: testing webhooks on your own laptop
<!-- bite: 49391bef-bfce-4f06-8383-65451d2300e7 -->

Paystack's servers can't reach `http://localhost:3000`. That's your laptop, not the internet.

During development, use a **tunnel**: a small program that gives you a public HTTPS address and forwards everything it receives to your laptop. [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] shows how. Start one pointing at port 3000, copy its address, and in Paystack's dashboard (test mode) set the webhook URL to `https://<your-tunnel-address>/webhooks/paystack`. Pay with a test card, and watch the request arrive in your logs.

You can also send yourself a correctly signed webhook, which is handy for checking the signature code without any tunnel:

```bash
BODY='{"event":"charge.success","data":{"id":1,"reference":"mp-42-...","amount":300000,"currency":"NGN","status":"success"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha512 -hmac "$PAYSTACK_SECRET_KEY" | sed 's/^.* //')

curl -X POST http://localhost:3000/webhooks/paystack \
  -H "Content-Type: application/json" \
  -H "x-paystack-signature: $SIG" \
  --data "$BODY"
```

Use a real reference from step 4 instead of `mp-42-...`. Then try it with one character of `$BODY` changed after signing: you should get the 401.

## Step 7: the backup, verifying ourselves
<!-- bite: bb3c192f-deb7-432d-bddb-d5cded58c464 -->

Webhooks are reliable, not perfect. Our server might be down for the 72 hours Paystack keeps retrying (it happens, though rarely). Or a setting in the dashboard might be wrong. So we add a second path to the truth: asking Paystack directly.

When Ada lands back on our site, her app calls:

```ts
// src/payments/payments.routes.ts
router.get("/payments/:reference", requireUser, async (req, res) => {
  const { reference } = validate(ReferenceParams, req.params, "params");
  const payment = await paymentsService.check(req.user!, reference);
  res.json({ data: payment });
});
```

and in the service:

```ts
async check(actor: AuthUser, reference: string) {
  const payment = await payments.findByReference(reference);
  if (!payment) throw notFound("Payment", reference);
  await ordersService.get(actor, payment.orderId);       // 404 unless it's actor's order

  if (payment.status === "started") {
    await this.settle(reference, await provider.verify(reference));
  }
  const latest = await payments.findByReference(reference);
  return { reference, status: latest!.status };
},
```

The browser's visit is only a *nudge* to go and ask Paystack. The answer comes from `provider.verify`, using our secret key, from our server, and it goes through the same `settle` as the webhook. So whether the webhook or the verify call gets there first, the order is paid once, with the same checks.

(`this.settle` works because `check` and `settle` are methods on the same returned object, and `check` is called as `paymentsService.check(...)`. If you find `this` confusing, pull `settle` out into a plain function above the `return`, and call it from both. That's what the finished code in the practice does.)

For payments still `started` after an hour, a scheduled job can run the same verify for each. That's the safety net under the safety net, and it's one of the jobs in lesson 18.

## Step 8: only paid orders get cooked
<!-- bite: c529bf5f-48be-430a-94c9-1408fa911dc9 -->

Now Mama's rule: the kitchen doesn't cook unpaid orders. In the orders service's `updateStatus`, before the change:

```ts
if (status === "ready" && !order.paidAt) {
  throw ruleBroken("order-not-paid", "This order hasn't been paid for yet.");
}
```

(`Order` gains `paidAt: string | null`, read from `paid_at` in `toOrder`.) The kitchen screen in [[backend/frameworks/express/20-real-time|lesson 20]] will show only paid orders, but the rule lives here, in the service, where no screen can skip it.

## Step 9: sending our own webhooks
<!-- bite: fc52240b-0725-4426-9732-47680de60198 -->

Now the other direction. When the kitchen marks order 42 ready, Okada Riders should hear about it at once. They've given us a URL, `https://okada-riders.example/hooks/mama-put`, and we've agreed on a shared secret.

Sending a webhook is more than one `fetch`. Everything we needed from Paystack, Okada Riders needs from us:

1. **A signature**, so they know it's really from us.
2. **A timestamp in the signature**, so nobody can record one of our webhooks and replay it next week.
3. **An event id**, so they can ignore duplicates.
4. **Retries**, because their server will sometimes be down, and they're relying on at-least-once delivery.

### Writing it down first

When the order becomes ready, we don't call Okada Riders right there. We write the webhook into `webhook_deliveries` and move on. A separate sender picks it up.

`src/webhooks/deliveries.ts`:

```ts
import type pg from "pg";

export function createDeliveries(pool: pg.Pool) {
  return {
    async enqueue(url: string, eventType: string, data: object) {
      await pool.query(
        `INSERT INTO webhook_deliveries (url, event_type, payload)
         VALUES ($1, $2, $3)`,
        [url, eventType, JSON.stringify(data)],
      );
    },
    // ...claimDue, markDelivered, markFailed: below
  };
}
```

and in the orders service, after a successful change to `ready`:

```ts
await deliveries.enqueue(deliveryWebhookUrl, "order.ready", {
  orderId: order.id,
  readyAt: new Date().toISOString(),
  quantity: order.quantity,
  dishId: order.dishId,
});
```

Why write it down instead of sending at once? Three reasons. The cook's tap on "ready" doesn't wait for Okada Riders' server. If their server is down, the webhook isn't lost; it's sitting in a table. And a restart of our app loses nothing, because the queue is in Postgres, not in memory.

Notice what's **not** in the payload: Ada's name, email or phone. The rider needs to know an order is ready at Mama's; they don't need her details until a delivery is booked, and then through Okada Riders' own system. Send another company only what it needs. Everything you send, you can't take back.

(One honest gap: the status change and the `enqueue` are two separate queries. If the app crashed exactly between them, the order would be ready and the webhook never written. Putting both in one transaction fixes it, and doing that properly, for events between services, is the **outbox** in [[backend/frameworks/express/25-splitting-out-a-microservice|lesson 25]].)

### The sender

`src/webhooks/sender.ts`:

```ts
import { randomInt } from "node:crypto";
import { hmacHex } from "../shared/signatures.ts";
import type { Deliveries, Delivery } from "./deliveries.ts";

const MAX_ATTEMPTS = 15;

function backoffSeconds(attempts: number) {
  const base = Math.min(30 * 2 ** (attempts - 1), 6 * 60 * 60);   // 30 s, 1 min, 2 min, ... up to 6 h
  return base + randomInt(0, Math.ceil(base / 5));                // plus up to 20% jitter
}

export function createWebhookSender(deps: { deliveries: Deliveries; secret: string; log: (m: string, d: object) => void }) {
  async function send(delivery: Delivery) {
    const timestamp = Math.floor(Date.now() / 1000);
    const body = JSON.stringify({
      id: delivery.id,
      type: delivery.eventType,
      createdAt: delivery.createdAt,
      data: delivery.payload,
    });
    const signature = hmacHex("sha256", deps.secret, `${timestamp}.${body}`);

    const res = await fetch(delivery.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "MamaPut-Event-Id": delivery.id,
        "MamaPut-Signature": `t=${timestamp},v1=${signature}`,
      },
      body,
      redirect: "manual",
      signal: AbortSignal.timeout(5_000),
    });
    if (res.status < 200 || res.status >= 300) throw new Error(`answered ${res.status}`);
  }

  async function runOnce() {
    const due = await deps.deliveries.claimDue(10);
    for (const delivery of due) {
      try {
        await send(delivery);
        await deps.deliveries.markDelivered(delivery.id);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        const giveUp = delivery.attempts >= MAX_ATTEMPTS;
        await deps.deliveries.markFailed(delivery.id, message, giveUp ? null : backoffSeconds(delivery.attempts));
        deps.log(giveUp ? "webhook delivery gave up" : "webhook delivery failed, will retry", {
          id: delivery.id,
          attempts: delivery.attempts,
          error: message,
        });
      }
    }
  }

  return {
    start(everyMs = 5_000) {
      const timer = setInterval(() => runOnce().catch((err) => deps.log("webhook sender crashed", { err })), everyMs);
      return () => clearInterval(timer);
    },
    runOnce,
  };
}
```

A lot of small decisions, each one learned the hard way by someone:

1. **What gets signed is `timestamp.body`**, not just the body. The receiver checks the timestamp is recent, so a webhook recorded today is useless next week, even though its signature is real.
2. **`MamaPut-Event-Id`** is the delivery's id, the same on every retry. That's what lets Okada Riders skip duplicates.
3. **Only 2xx counts.** A redirect, a 404, a 500: all failures. `redirect: "manual"` stops `fetch` from quietly following a redirect somewhere we didn't agree to send.
4. **A 5-second timeout.** A slow partner mustn't hold up the queue.
5. **Backoff that grows**: 30 seconds, then 1 minute, 2, 4, ... up to 6 hours between tries. If their server is down for an hour, hammering it every 5 seconds helps nobody, and may be part of why it's down.
6. **Jitter.** If 500 webhooks all failed at the same moment, without jitter they'd all retry at the same moment too, and knock the partner over again. A random extra spreads them out.
7. **Give up eventually**, and log it, so a person can look. Fifteen attempts, with the gaps capped at 6 hours, take about a day and a half.

### Claiming work safely

`claimDue` is where two copies of our app could trip over each other. Run two servers (we will, in lesson 28), and both senders wake up every 5 seconds. Without care, both pick the same webhook and send it twice.

```ts
async claimDue(limit: number): Promise<Delivery[]> {
  const { rows } = await pool.query(
    `UPDATE webhook_deliveries
        SET attempts = attempts + 1,
            next_attempt_at = now() + interval '1 minute'
      WHERE id IN (
        SELECT id FROM webhook_deliveries
         WHERE delivered_at IS NULL AND next_attempt_at <= now()
         ORDER BY next_attempt_at
         LIMIT $1
         FOR UPDATE SKIP LOCKED
      )
     RETURNING *`,
    [limit],
  );
  return rows.map(toDelivery);
},
```

Two things make this safe:

1. **`FOR UPDATE SKIP LOCKED`** locks the rows this sender picks, and tells any other sender looking at the same moment to *skip* locked rows instead of waiting for them. So two senders take different webhooks.
2. **Pushing `next_attempt_at` a minute forward** is a lease: "this is mine for a minute". If our server dies mid-send, the row isn't stuck forever. A minute later it's due again and someone else picks it up.

`markDelivered` sets `delivered_at = now()`. `markFailed` saves `last_error` and sets `next_attempt_at = now() + backoff`, or, when giving up, sets it to a far future date (`'infinity'` in Postgres) so it's never picked again but stays in the table for a person to see.

And yes: this is a small, hand-made job queue. In [[backend/frameworks/express/18-background-jobs|lesson 18]] we hand this job to BullMQ, and having built one yourself, you'll know exactly what it does for you.

Start it in `server.ts`, next to `listen`:

```ts
const stopSender = createWebhookSender({ deliveries, secret: deliveryWebhookSecret, log }).start();
```

### What Okada Riders does with it

They'll ask "how do we check your signature?", so write it down for them. This is roughly the code on *their* side, and it's a good way to check your own design:

```ts
function isFromMamaPut(rawBody: Buffer, header: string, secret: string) {
  const parts = Object.fromEntries(header.split(",").map((part) => part.split("=", 2)));
  const timestamp = Number(parts.t);
  if (!Number.isInteger(timestamp)) return false;
  if (Math.abs(Date.now() / 1000 - timestamp) > 5 * 60) return false;   // older than 5 minutes: replay

  const expected = hmacHex("sha256", secret, `${timestamp}.${rawBody.toString("utf8")}`);
  return sameHex(expected, parts.v1 ?? "");
}
```

Then they check `MamaPut-Event-Id` against the ids they've already seen, answer 200 quickly, and do their work. It's everything we did for Paystack, from the other side. Good webhook design is just being the sender you'd want to receive from.

One more thing worth knowing. Here the URL comes from our own config. Some products let *customers* type in their own webhook URL. Then you must check it doesn't point inside your own network, or someone sets their URL to `http://169.254.169.254/` or `http://localhost:5432` and makes your server attack itself. That's called **SSRF** (server-side request forgery), and [[backend/frameworks/express/14-security|lesson 14]]'s ideas apply: treat the URL as hostile input.

## Step 10: testing it
<!-- bite: e1d8b5a3-bfca-4192-8660-dde6ec13f238 -->

Lesson 16's tools cover all of this without Paystack or Okada Riders running.

**The provider is a fake.** `buildTestApp` gets a `PaymentProvider` that answers from memory:

```ts
export function createFakeProvider() {
  const results = new Map<string, { succeeded: boolean; amountKobo: number; currency: string }>();
  return {
    results,
    async startCheckout({ reference }: { reference: string }) {
      return { checkoutUrl: `https://checkout.test/${reference}` };
    },
    async verify(reference: string) {
      return results.get(reference) ?? { succeeded: false, amountKobo: 0, currency: "NGN" };
    },
  } satisfies PaymentProvider & { results: unknown };
}
```

**Webhooks are signed in the test,** with the test secret, exactly as Paystack would:

```ts
it("marks the order paid once, however many times the webhook arrives", async () => {
  const { app, login, seed, secrets } = await buildTestApp();
  const { token } = await login();
  const order = await seed.anOrderFor(token);
  const checkout = await request(app)
    .post(`/v2/orders/${order.id}/payments`)
    .set("Authorization", `Bearer ${token}`)
    .set("Idempotency-Key", "test-pay-0001");

  const body = JSON.stringify({
    event: "charge.success",
    data: { id: 7, reference: checkout.body.data.reference, amount: order.totalKobo, currency: "NGN", status: "success" },
  });
  const signature = hmacHex("sha512", secrets.paystack, body);
  const deliver = () =>
    request(app).post("/webhooks/paystack")
      .set("Content-Type", "application/json")
      .set("x-paystack-signature", signature)
      .send(body);

  const results = await Promise.all([deliver(), deliver(), deliver()]);
  assert.deepEqual(results.map((r) => r.status), [200, 200, 200]);

  const after = await request(app).get(`/v2/orders/${order.id}`).set("Authorization", `Bearer ${token}`);
  assert.ok(after.body.data.paidAt);
});
```

Note `.send(body)` with a **string**. supertest sends a string exactly as given, so the bytes we signed are the bytes that arrive. Send an object and supertest would serialise it itself, maybe differently.

And the tests that matter just as much:

1. A wrong signature gives 401, and the order stays unpaid.
2. One changed character in a signed body gives 401.
3. An amount one kobo short is logged as a mismatch, and the order stays unpaid.
4. An event we don't handle (`transfer.success`) gets 200 and changes nothing.
5. Marking an unpaid order `ready` gives 422 `order-not-paid`.
6. For the sender: a fake partner server that fails twice and then succeeds gets exactly one successful delivery, with the same `MamaPut-Event-Id` all three times. (Call `runOnce` directly in the test instead of waiting for the timer. That's why it's returned.)

The double-payment race (two webhooks at the same instant) belongs in the Postgres integration tests, like the last-plate race in lesson 16, because only a real database shows it.

## The TypeScript in this lesson
<!-- bite: 1027d5cc-a81a-411f-801b-eb5630a89efb -->

1. **`z.literal(true)`**: A schema that accepts only that exact value. `status: z.literal(true)` means "Paystack must say `status: true`", so a `false` response fails validation.
2. **`z.url()`**: In zod 4, the check for a valid URL is its own function at the top level, not `z.string().url()`.
3. **`z.looseObject({})`**: An object schema that keeps any fields it doesn't list, instead of dropping them. We need the webhook's `data` intact, because different events put different things in it, and we parse it properly once we know which event it is.
4. **`async function call<T>(path: string, schema: z.ZodType<T>, ...): Promise<T>`**: A generic function. `T` is whatever shape the schema describes, so passing `VerifyResponse` makes `call` return exactly that shape, fully typed, with no casting.
5. **`let res: Response;` then assigned inside `try`**: Declaring it before the `try` means it's still usable after. `Response` here is the built-in `fetch` response type, not Express's `Response`. They're different things with the same name, and this file never imports Express's.
6. **`init: RequestInit = {}`**: `RequestInit` is the built-in type for `fetch`'s options (method, headers, body). `= {}` is a default, used when the caller passes nothing.
7. **`{ ...init, headers: {...} }`**: Copies everything from `init`, then sets `headers`. Later properties win, so our headers always replace any passed in.
8. **`await res.json().catch(() => null)`**: If the body isn't valid JSON, `json()` fails. `.catch(() => null)` turns that failure into `null`, which then fails our schema with a clear error.
9. **`AbortSignal.timeout(10_000)`**: Makes a signal that cancels the `fetch` after 10,000 milliseconds. The `_` in `10_000` is just for reading; it's the number 10000.
10. **`"unknown" as const`**: Makes the returned value the exact word `"unknown"`, not just `string`. So `settle` returns `"unknown" | "failed" | "mismatch" | "paid" | ...`, and code that checks the result gets help from the editor.
11. **`const raw: unknown = req.body;` and `Buffer.isBuffer(raw)`**: `req.body` is typed `any`, which turns off checking. Putting it in an `unknown` variable forces us to prove what it is. After `Buffer.isBuffer(raw)` is true, TypeScript knows `raw` is a `Buffer`.
12. **`req.get("x-paystack-signature") ?? ""`**: `req.get` reads a header (ignoring upper or lower case), and gives `undefined` if it's missing. `?? ""` turns a missing header into an empty string, which then fails the comparison.
13. **`Buffer.from(a, "hex")`**: Turns hex text like `"a3f0"` into the bytes it represents. `raw.toString("utf8")` goes the other way, bytes to text.
14. **`2 ** (attempts - 1)`**: `**` is "to the power of". `2 ** 3` is 8.
15. **`err instanceof Error ? err.message : String(err)`**: In a `catch`, `err` is `unknown`, because JavaScript lets you throw anything, even a number. This gets a message whatever was thrown.
16. **`Object.fromEntries(header.split(",").map((part) => part.split("=", 2)))`**: Turns `"t=1700000000,v1=ab12"` into `{ t: "1700000000", v1: "ab12" }`. `split(",")` makes the pieces, each piece splits on the first `=` into a pair, and `fromEntries` builds an object from the pairs.
17. **`satisfies PaymentProvider & { results: unknown }`**: Checks the fake has everything a `PaymentProvider` needs, *plus* `results`, while keeping its real type, so tests can still reach `fake.results`. `&` combines two types into one that has both.
18. **`return () => clearInterval(timer)`**: `start` returns a function that stops the timer. Returning a "stop" function is a common way to let the caller undo what you started, without exposing the timer itself.

## Your project so far
<!-- bite: e6401f60-5b28-4e1e-8292-e6ef71c9e63d -->

```text
mama-put-api/
├── .env · .env.example           ← NEW settings: PAYSTACK_SECRET_KEY, PUBLIC_URL,
│                                    DELIVERY_WEBHOOK_URL, DELIVERY_WEBHOOK_SECRET
├── .env.test · .gitignore · package.json · tsconfig.json
├── migrations/
│   ├── 001 … 010
│   ├── 011_payments.sql          ← NEW: payments (one row per attempt), orders.paid_at
│   └── 012_webhooks.sql          ← NEW: webhook_events_received, webhook_deliveries
├── uploads/photos/ · openapi/    (POST /orders/{id}/payments and GET /payments/{reference} documented)
├── test/integration/             ← + two webhooks at once settle one payment
└── src/
    ├── server.ts                 ← builds Paystack, the payments service; starts the webhook sender
    ├── app.ts                    ← /webhooks/paystack mounted BEFORE express.json and the rate limit
    ├── api.ts                    ← mounts the payments routes in each version
    ├── payments/
    │   ├── payments.types.ts     ← NEW: PaymentProvider, Payment, PaymentStatus
    │   ├── paystack.ts           ← NEW: the only file that knows Paystack's URLs; timeouts, checked responses
    │   ├── payments.service.ts   ← NEW: startCheckout, settle (the one place that marks paid), check
    │   ├── payments.pg-repository.ts ← NEW: create, findByReference, markSucceeded (conditional), markFailed
    │   ├── payments.routes.ts    ← NEW: POST /orders/:id/payments, GET /payments/:reference
    │   ├── paystack.webhook.ts   ← NEW: raw body → signature → parse → skip seen → settle → record
    │   ├── received-events.ts    ← NEW: has(), record()
    │   └── *.test.ts             ← NEW: signed webhooks, wrong signatures, mismatches, the fake provider
    ├── webhooks/
    │   ├── deliveries.ts         ← NEW: enqueue, claimDue (SKIP LOCKED + lease), markDelivered, markFailed
    │   ├── sender.ts             ← NEW: sign t.body, 2xx only, backoff with jitter, give up after 15
    │   └── sender.test.ts        ← NEW: a fake partner that fails twice
    ├── orders/
    │   ├── orders.types.ts       ← Order gains paidAt
    │   └── orders.service.ts     ← "ready" needs paidAt; enqueues order.ready
    ├── shared/
    │   ├── errors.ts             ← NEW kind: upstream (502)
    │   ├── signatures.ts         ← NEW: hmacHex, sameHex (timing-safe)
    │   └── idempotent.ts · idempotency.store.ts · validate.ts · error-handler.ts · ...
    └── auth/ · admin/ · menu/ · docs/ · db/ · types/ · test-support/
```

## Common mistakes
<!-- bite: 0caee482-2a07-4a7f-b835-0896819c43b0 -->

1. **Marking the order paid on the redirect.** Anyone can visit `/payment-done?reference=...`. Only a signed webhook or your own verify call counts.
2. **Checking the signature on `JSON.stringify(req.body)`.** The bytes differ from what was signed, so real webhooks fail, and someone "fixes" it by turning the check off. Use the raw body, and mount the route before `express.json()`.
3. **Comparing signatures with `===`.** Use `timingSafeEqual`, with a length check first.
4. **Trusting the amount without checking it.** Compare the amount and the currency with what *you* asked for.
5. **Answering 4xx or 5xx to events you don't handle.** The sender retries for days. Say 200 and ignore them.
6. **Recording "handled" before doing the work.** A crash in between loses the event for good. Work first (and make the work safe to repeat), record after.
7. **Slow work inside the webhook handler.** The sender times out and resends. Answer fast; queue the slow bits.
8. **Amounts in naira.** Paystack counts kobo. `3000` is ₦30.
9. **Your own webhooks with no timestamp, no event id, or no retries.** Every one of those is a support call from your partner later.
10. **The live secret key in `.env.example`, a test, or a commit.** It can move money. Test keys while building, the live key only in production config, never in git. (Lesson 28 covers where secrets live.)

## Check your understanding
<!-- bite: 3b116494-1253-4f64-a0d4-a8ba246a1d69 -->

1. Ada pays, then closes the tab before Paystack redirects her back. Is her order marked paid? How?
2. Why must the Paystack webhook route come before `app.use(express.json())`?
3. The webhook handler records the event *after* calling `settle`. What goes wrong if you swap them?
4. Two copies of the same `charge.success` arrive at the same instant, on two different servers. Walk through why the order is paid exactly once.
5. Why do we sign `timestamp.body` in our own webhooks instead of just the body?
6. Okada Riders' server is down for two hours. What happens to the `order.ready` webhooks during that time, and after?

<details>
<summary>Answers, after your attempt</summary>

1. Yes. The redirect never happens, but Paystack still sends the `charge.success` webhook to our server, and that's what marks it paid. The redirect was never part of the truth.
2. `express.json()` reads and parses the body for every request that reaches it, and the original bytes are gone. The signature is computed over those exact bytes, so the webhook route must read them first, with `express.raw`, before `express.json()` gets the chance.
3. If the app crashes after recording but before `settle`, Paystack's retry is skipped as "already seen", and Ada's payment is never counted. Working first means a crash just leads to doing it again, which `settle` makes harmless.
4. Both pass the signature check, and both may get past `receivedEvents.has` (neither has recorded yet). Both call `markSucceeded`. Its `UPDATE ... WHERE status = 'started'` locks the row; the first changes it to `succeeded` and goes on to set `paid_at`; the second waits, then finds the status isn't `started` any more, updates nothing, and returns `already-settled`. One payment, one `paid_at`.
5. So an old webhook can't be replayed. Someone who captures a real signed webhook can resend it unchanged, and the signature would still be valid. With the timestamp inside the signature, the receiver rejects anything older than five minutes, and the timestamp can't be changed without breaking the signature.
6. They wait in `webhook_deliveries`. Each failed attempt is retried after a growing gap (30 s, 1 min, 2, 4, 8, 16, 32, 64 minutes, plus jitter), so within about an hour of their server coming back, every webhook is delivered, each with its original event id. Nothing is lost, and nothing was sent in a flood.

</details>

## Practice
<!-- bite: f0614753-eb8d-4610-92ae-19860b4888f5 -->

1. Write the rest of `payments.pg-repository.ts`: `create`, `findByReference` (with a `toPayment` that turns a row into a `Payment`), and `markFailed`, which only changes a payment that's still `started`.
2. Pull `settle` out of the returned object into a plain function, so `check` calls it without `this`.
3. Write `deliveries.ts` in full: `toDelivery`, `markDelivered`, and `markFailed(id, error, retryInSeconds | null)`, where `null` means give up.
4. Add an admin-only route, `GET /v2/admin/webhook-deliveries?status=failed`, that lists deliveries that gave up, using lesson 9's pagination, and `POST /v2/admin/webhook-deliveries/:id/retry`, which makes one due again.
5. Write the six tests listed in step 10.
6. Run the full flow with a tunnel: start a checkout, pay with a Paystack test card, and watch the webhook arrive and the order become paid. Then use the `curl` from step 6 with a changed body and see the 401.

**Done when** a Paystack test payment marks the order paid exactly once (check `paid_at` and the payment's `status` in the database), the same webhook sent three times changes nothing more, a wrong or missing signature gets 401, the kitchen can't mark an unpaid order ready, and stopping a fake partner server for a few minutes delays `order.ready` webhooks without losing any.

## Before moving on
<!-- bite: 344c16f5-ef4a-4b72-b1dd-2a82f32d03d7 -->

Mama Put now takes real money. The customer pays on Paystack's page, Paystack tells us with a signed webhook, we check every detail, and the order is paid exactly once, whatever arrives twice. When the food is ready, Okada Riders hears about it through our own signed webhooks, with retries that survive their bad days.

But look at what we built by hand along the way: a table of work to do, a loop that wakes up every 5 seconds, retries with backoff, a lease so two servers don't collide. That's a job queue, and we'll need many more: receipts by email, the hourly check on unsettled payments, resizing dish photos, refunds. Writing a little queue for each would be a mess. In the next lesson we use a real one: BullMQ, on Redis.

## Related
<!-- bite: 10cbd8f2-29be-4c66-a4d1-a7f302417bbb -->

- [[backend/frameworks/express/18-background-jobs|Next: Background Jobs and Queues]]
- [[backend/frameworks/express/15-idempotency|Idempotency]] — the same "safe to repeat" idea, for requests coming from our own customers
- [[backend/frameworks/express/14-security|Security]] — why the secret key must never reach the browser, and treating URLs as hostile input
- [[devops/02-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] — letting Paystack reach your laptop during development
- [[backend/02-api-design/index|API Design]] — webhooks among the other ways systems talk

## About this lesson
<!-- bite: 79a9b590-b2b2-48dd-bac9-e66fca9a36f2 -->

**Level:** Intermediate → Advanced. Lesson 17 of [[backend/frameworks/express/index|Express]]. Covers why a payment spans several requests and why the redirect can't be trusted, a payments table with one row per attempt, a Paystack client with timeouts, validated responses and a new `upstream` (502) error kind, starting a checkout in kobo with a reference we control, receiving webhooks with `express.raw` mounted before `express.json`, HMAC SHA-512 signatures checked with `timingSafeEqual`, at-least-once delivery and settling a payment exactly once with a conditional `UPDATE` in a transaction, working before recording, the verify call as a backup, the "only paid orders get cooked" rule, sending our own webhooks from a Postgres-backed queue with signed timestamps, event ids, backoff with jitter and `FOR UPDATE SKIP LOCKED` leases, what a receiver should check, SSRF for customer-supplied URLs, and testing webhooks with signed bodies and a fake provider.
