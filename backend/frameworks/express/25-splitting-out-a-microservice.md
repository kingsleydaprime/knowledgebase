---
id: b5842dc4-4cfb-4654-aaf2-be091e670530
---

# Splitting Out a Microservice

**A microservice is a separate program, with its own code, its own data and its own deploys, that does one part of a bigger system's job and talks to the other parts only through the network. Splitting one out means taking a job your main app does today and giving it to a new service of its own.** So far Mama Put has been one program (plus its worker). This lesson makes it two services, and the hard part isn't writing the second one. It's how they talk without becoming one program again, tangled across a network.

## Before you start
<!-- bite: a18be7aa-a1cd-4a59-ab37-98ebcd1348e0 -->

You should have everything up to [[backend/frameworks/express/24-mcp-in-production|lesson 24]], and especially the jobs from [[backend/frameworks/express/18-background-jobs|lesson 18]] and the gRPC server from [[backend/frameworks/express/22-grpc|lesson 22]].

After this lesson you will be able to:

1. Say honestly when splitting a service is worth it, and what it costs.
2. Choose a good first service to split out, and decide which data it owns.
3. Design events: names, envelopes, versions, and how much data they carry.
4. Publish events reliably with the **outbox** pattern, so a change and its event can never disagree.
5. Consume events with Redis Streams consumer groups, safely, even when messages arrive twice.
6. Build the notifications service, which gets what else it needs from the main API over gRPC.

## Where we stopped
<!-- bite: e34e3a71-0f18-415d-9d16-91c0f6a600eb -->

Look at everything the API's worker does to talk to customers:

1. Receipt emails (lesson 18), through an email provider, with its own API key.
2. "How was your food?" emails, delayed an hour.
3. Soon: a text message when the order is ready, through an SMS provider, with another key.

And look at what happened last Tuesday (pretend). The SMS provider was slow for an hour. The worker's `emails` queue filled up, retries piled on, the worker used all its CPU, and lesson 17's partner webhooks to Okada Riders, in the same worker, ran late. One provider's bad hour reached our delivery partner.

Also, Mama has hired someone to look after customer messages: wording, templates, which messages to send when. Every small change to a template means deploying the *whole* API, payments and all.

Those are the two real reasons to split something out: **one part's failures shouldn't reach the rest**, and **one part should change on its own schedule**. Notifications has both.

## The kid version
<!-- bite: 0865ec04-e257-4bcc-9755-9d811f0b4504 -->

When Mama Put was small, Mama took orders, cooked, collected money and shouted "Bayo, your food is ready!", all herself.

Now it's busy. She hires a boy just for calling names and sending texts. He has his own corner, his own phone, his own list of customers' numbers. Mama doesn't tell him how to send a text; she just rings a little bell and calls "order 42 is ready" into the room. Anyone whose job involves ready orders hears it. The boy hears, looks up who ordered 42, and texts them.

If the boy's phone runs out of credit, Mama keeps cooking. The orders don't stop. The texts are late, and that's all.

The bell and the call into the room are **events**. The boy is the notifications service. "Mama doesn't care who's listening" is the point.

**Where the picture stops working.** In a room, if the boy steps out, he misses the call. Our events must wait for him: when he comes back, everything called while he was away must still be there, in order. That's what a stream with consumer groups gives us.

## Terms used in microservices
<!-- bite: 0aa08098-5041-47b9-9ad2-b68fd272e79b -->

1. **Monolith**: This is one program that does everything. Not an insult: most good systems start as one, and many stay one.
2. **Service boundary**: This is the line around what a service owns: its job, its code, its data.
3. **Event**: This is a message saying something **already happened**, like `order.paid`. The sender doesn't know or care who's listening.
4. **Command**: This is a message asking someone to **do** something, like "send this email". Compare with an event: a command has a target; an event doesn't.
5. **Outbox**: This is a table where a service writes the events it wants to publish, in the same database transaction as the change itself. A separate process then publishes them.
6. **Stream**: This is an ordered log of messages that stay there after being read. Redis Streams are one kind.
7. **Consumer group**: This is a named group of readers sharing one stream. Each message goes to one member of the group, and the group remembers how far it has read.
8. **Acknowledge (ack)**: This is a consumer telling the stream "I've finished this message", so it isn't given out again.
9. **Eventual consistency**: This means different services see a change at slightly different times. For a moment, the API knows order 42 is paid and notifications doesn't yet. Soon, they agree.

## Step 1: should you, really?
<!-- bite: 8245a85d-2457-4a00-912d-5fd2f9a2b018 -->

Microservices are fashionable, and many teams regret them. Be honest about the costs before paying them:

| You get | You pay |
|---|---|
| A failure in one service stays there | Every call between services can fail, be slow, or arrive twice |
| Each service deploys on its own | Changes that span services need careful ordering (versions, both shapes for a while) |
| Each service keeps its own secrets and data | Data is in several places; "join" across services means network calls |
| Teams can own their service | Debugging means following one request through several programs (lesson 27) |
| Scale only the busy part | More to run, watch, secure and pay for |

The usual good advice is **"monolith first"**: build one well-structured program, with clear folders and services inside (lessons 4 and 5), and split only when a real reason appears. Feature folders that only talk through service interfaces are already most of the way there. That's why this split will be fairly painless.

Mama Put, honestly, could stay one program for years. We're splitting notifications to learn how, and because it's the classic **good first candidate**:

1. It has clear edges: "something happened; tell the customer".
2. It doesn't need to answer anyone in a hurry. A receipt a minute late is fine.
3. It talks to unreliable outside providers, whose failures we want kept away from orders and payments.
4. Nothing else needs to wait for it. Nobody's request fails because a text wasn't sent.

A **bad** first candidate would be "payments" or "menu": the API needs them in the middle of placing an order, so every order would become a network call that can fail.

## Step 2: the new layout
<!-- bite: 27cdc9e3-4a70-4286-9895-7c3ec8981215 -->

Two services, plus things they share, in one repository (a **monorepo**):

```text
mama-put/
├── api/              ← the old mama-put-api, moved down one folder
├── notifications/    ← NEW: the notifications service
├── proto/            ← moved up from api/: .proto files both services use
└── contracts/        ← NEW: event definitions both services use
```

A monorepo keeps shared contracts in one place, lets one pull request change both sides, and runs all tests together (lesson 29). Some companies use one repository per service instead; then shared contracts go in their own repository or package. Both work. For two services and one team, a monorepo is simpler.

Each service still has its own `package.json`, its own dependencies, its own tests and (in lesson 28) its own Docker image. Sharing a repository is not sharing a program.

One file ties the folders together, `mama-put/package.json`:

```json
{
  "name": "mama-put",
  "private": true,
  "workspaces": ["api", "notifications", "contracts"]
}
```

These are **npm workspaces**. Run `npm install` once in `mama-put/`, and npm installs every folder's dependencies into one `node_modules` at the top, with one `package-lock.json`. That matters for `contracts/`: its file imports `zod`, and Node looks for `zod` in `node_modules` folders *above* the file. With workspaces, `mama-put/node_modules/zod` is right there. (`contracts/` gets a tiny `package.json` of its own, listing `zod` as its dependency.) From now on, run `npm install` at the top, and run a service's scripts with `npm run dev -w api` or `npm run dev -w notifications`.

### Who owns which data

The most important rule in this lesson: **a service's database is private.** The notifications service never reads the API's tables, and the API never reads notifications' tables. Everything goes through events or APIs.

Why so strict? Because a shared table is a hidden contract. If notifications reads `users.email` directly, then renaming that column in the API breaks notifications, with no warning, and the two services can never deploy separately again. You'd have a monolith with network problems.

So the notifications service gets its own database, on the same Postgres server for now, with its own user that can't see the API's database:

```sql
CREATE DATABASE mama_put_notifications;
CREATE USER notifications WITH PASSWORD '...';
GRANT ALL ON DATABASE mama_put_notifications TO notifications;
```

It owns:

1. **`sent_notifications`**: every message sent, so we never send the same one twice and support can see what a customer got.
2. **`preferences`**: whether each customer wants texts, emails or both. The API doesn't need to know.

It does **not** own customers' email addresses and phone numbers. Those belong to the API, which is where people edit them. When notifications needs them, it asks (step 6).

## Step 3: designing events
<!-- bite: f6a7ab26-5706-4619-89f8-7a5034399e66 -->

An event says what happened, in the past tense, from the point of view of the service that owns the thing:

1. `order.placed`: a customer placed an order.
2. `order.paid`: an order's payment succeeded.
3. `order.ready`: the kitchen marked it ready.
4. `order.collected`: it was picked up.

Every event has the same **envelope**, `contracts/events.ts`:

```ts
import { z } from "zod";

export const Envelope = z.object({
  id: z.uuid(),                 // unique per event; consumers use it to skip duplicates
  type: z.string(),             // "order.paid"
  version: z.number().int(),    // the version of THIS type's data shape
  occurredAt: z.iso.datetime(), // when it happened, not when it was sent
  source: z.string(),           // "api"
  data: z.unknown(),
});
export type Envelope = z.infer<typeof Envelope>;

export const OrderPaidV1 = z.object({
  orderId: z.string(),
  customerId: z.string(),
  dishId: z.string(),
  quantity: z.number().int(),
  totalKobo: z.number().int(),
  paidAt: z.iso.datetime(),
});

export const OrderReadyV1 = z.object({
  orderId: z.string(),
  customerId: z.string(),
  readyAt: z.iso.datetime(),
});

export const EVENTS = {
  "order.paid": { 1: OrderPaidV1 },
  "order.ready": { 1: OrderReadyV1 },
} as const;
```

Both services import this file, so the shape is written once.

**Versions, because lesson 10 promised.** Events are an API too: other services depend on their shape. The same rules apply. Adding a field is safe (consumers ignore fields they don't know, because our zod objects aren't `.strict()`). Removing or changing a field is breaking: publish `version: 2` *alongside* `version: 1` for a while, move every consumer to v2, then stop publishing v1.

**How much data should an event carry?** Two styles:

1. **Thin events**: just ids. `{ orderId: "42" }`. Consumers call back to get the rest. Always fresh, but every event causes a call.
2. **Fat events**: everything a consumer might want, including copies of data. No calls needed, but you're spreading copies of data everywhere, and they go stale.

Ours sit in between: the **facts of what happened** (who, what, how much, when), but not copies of data that lives elsewhere and changes on its own, like the customer's email address or the dish's name. Personal contact details especially don't belong in events: events are stored, replayed and read by every consumer, now and in the future.

## Step 4: the outbox
<!-- bite: 8310496c-cf1a-4a23-a48d-a4535b4c873c -->

Here's the problem lesson 17 and lesson 18 kept pointing at. In `markSucceeded`, we update Postgres, then publish to Redis:

```ts
await payments.markSucceeded(reference);    // Postgres
await events.publish("order.paid", {...});  // Redis
```

Crash between the two lines, and the order is paid but nobody ever hears about it. Swap them, and a crash means everyone hears about a payment that never got saved. There's no transaction across Postgres and Redis.

The **outbox** fixes it by writing the event to **Postgres**, in the **same transaction** as the change:

`api/migrations/015_outbox.sql`:

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

`api/src/events/outbox.ts`:

```ts
import type pg from "pg";

export async function addToOutbox(tx: pg.PoolClient, type: string, version: number, data: object) {
  await tx.query("INSERT INTO outbox (type, version, data) VALUES ($1, $2, $3)", [type, version, JSON.stringify(data)]);
}
```

and in `markSucceeded`, inside the transaction it already had:

```ts
return inTransaction(pool, async (tx) => {
  const updated = await tx.query(/* the conditional UPDATE from lesson 17 */);
  if (updated.rowCount === 0) return "already-settled" as const;

  const order = await tx.query(/* UPDATE orders SET paid_at = now() ... RETURNING * */);
  if (order.rowCount === 0) return "order-was-already-paid" as const;

  const row = order.rows[0];
  await addToOutbox(tx, "order.paid", 1, {
    orderId: row.id,
    customerId: row.customer_id,
    dishId: row.dish_id,
    quantity: row.quantity,
    totalKobo: row.total_kobo,
    paidAt: row.paid_at.toISOString(),
  });
  return "paid" as const;
});
```

Now "the order is paid" and "there's an `order.paid` event to send" are committed together, or not at all. Postgres guarantees it. The same goes in `updateStatus` for `order.ready` and `order.collected`, and in `place` for `order.placed`.

### The relay

Something must move events from the outbox to the stream. That's the **relay**, a small loop in the API's worker:

```ts
// api/src/events/relay.ts
export function createOutboxRelay(deps: { pool: pg.Pool; redis: Redis; log: Log }) {
  async function runOnce() {
    return inTransaction(deps.pool, async (tx) => {
      const { rows } = await tx.query(
        `SELECT id, type, version, data, occurred_at FROM outbox
          WHERE published_at IS NULL
          ORDER BY occurred_at
          LIMIT 100
          FOR UPDATE SKIP LOCKED`,
      );
      for (const row of rows) {
        const envelope = {
          id: row.id, type: row.type, version: row.version,
          occurredAt: row.occurred_at.toISOString(), source: "api", data: row.data,
        };
        await deps.redis.xadd("events:orders", "MAXLEN", "~", "100000", "*", "event", JSON.stringify(envelope));
        await tx.query("UPDATE outbox SET published_at = now() WHERE id = $1", [row.id]);
      }
      return rows.length;
    });
  }

  return {
    start(everyMs = 500) {
      let stopped = false;
      (async function loop() {
        while (!stopped) {
          const sent = await runOnce().catch((err) => { deps.log("outbox relay failed", { error: err.message }); return 0; });
          if (sent === 0) await new Promise((r) => setTimeout(r, everyMs));
        }
      })();
      return () => { stopped = true; };
    },
    runOnce,
  };
}
```

`FOR UPDATE SKIP LOCKED` is lesson 17's trick again: run the relay in two workers, and they take different rows. When there's a backlog, it loops without waiting; when it's empty, it rests 500 ms.

`XADD events:orders MAXLEN ~ 100000 * event <json>` appends to the stream called `events:orders`. `*` lets Redis choose the message id (a timestamp and a counter). `MAXLEN ~ 100000` keeps roughly the last 100,000 events, so the stream doesn't grow forever; `~` lets Redis trim efficiently instead of exactly. Use the **queue** Redis (lesson 18): `noeviction` and `appendonly`, because events must not vanish.

Can the relay publish an event twice? Yes: if it crashes after `XADD` but before the transaction commits, the row is still unpublished, and it's sent again next time. That's at-least-once delivery, the same deal as Paystack's webhooks and BullMQ's jobs. Which is why every event has an `id`, and every consumer skips ids it has already handled.

### What this replaces

Look back at the honest gaps from earlier lessons:

1. **Lesson 17**: "the status change and the `enqueue` are two separate queries". Now the API's worker has its own consumer of `order.ready` that creates the partner webhook delivery. The event can't be lost, because it was committed with the status change.
2. **Lesson 18**: the sweeper for receipts. The receipt job is gone from the API entirely; notifications sends receipts from `order.paid`.
3. **Lesson 20**: the kitchen feed can be fed from the same stream, so it hears about every paid order even when a direct publish would have failed.

One reliable source of "what happened", many readers.

## Step 5: consuming with consumer groups
<!-- bite: 82806047-de09-407c-8403-5b9f5c0c0a0c -->

A Redis Stream keeps its messages after they're read. A **consumer group** is a named reader with a bookmark: "group `notifications` has read up to message X". Several copies of the notifications service can join the same group; each message goes to **one** of them, and the group's bookmark moves on. A different group (the API's `partner-webhooks`) has its own bookmark and gets *every* message too.

```text
events:orders ──┬──► group "notifications"     → notifications copy 1, copy 2 (share the work)
                └──► group "partner-webhooks"  → api worker (its own bookmark)
```

`notifications/src/consumer.ts`:

```ts
import { Redis } from "ioredis";
import { Envelope } from "../../contracts/events.ts";

const STREAM = "events:orders";

export function createConsumer(deps: {
  redis: Redis;
  group: string;
  name: string;                                     // this copy's name, e.g. its hostname
  handle: (event: Envelope) => Promise<void>;
  log: (m: string, d: object) => void;
}) {
  const { redis, group, name } = deps;

  async function ensureGroup() {
    try {
      await redis.xgroup("CREATE", STREAM, group, "$", "MKSTREAM");
    } catch (err) {
      if (!String(err).includes("BUSYGROUP")) throw err;   // already exists: fine
    }
  }

  async function processEntries(entries: [string, string[]][]) {
    for (const [messageId, fields] of entries) {
      const raw = fields[fields.indexOf("event") + 1];
      const parsed = Envelope.safeParse(JSON.parse(raw ?? "null"));
      if (!parsed.success) {
        deps.log("bad event, skipping", { messageId });
        await redis.xack(STREAM, group, messageId);
        continue;
      }
      try {
        await deps.handle(parsed.data);
        await redis.xack(STREAM, group, messageId);
      } catch (err) {
        deps.log("event handling failed, will retry", { messageId, type: parsed.data.type, error: (err as Error).message });
        // not acked: it stays pending and is picked up again below
      }
    }
  }

  async function loop(isStopped: () => boolean) {
    await ensureGroup();
    while (!isStopped()) {
      // 1. Messages another copy took and never finished (it crashed): claim them after 60 s.
      const [, stuck] = (await redis.xautoclaim(STREAM, group, name, 60_000, "0-0", "COUNT", 10)) as [string, [string, string[]][]];
      if (stuck.length) await processEntries(stuck);

      // 2. New messages, waiting up to 5 s for some to arrive.
      const result = (await redis.xreadgroup("GROUP", group, name, "COUNT", 10, "BLOCK", 5000, "STREAMS", STREAM, ">")) as
        | [string, [string, string[]][]][]
        | null;
      if (result) await processEntries(result[0][1]);
    }
  }

  return { loop };
}
```

The important ideas:

1. **`XGROUP CREATE ... $ MKSTREAM`** creates the group once, starting from "now" (`$`), and creates the stream if it doesn't exist yet. Running it again gives a `BUSYGROUP` error, which just means "already there".
2. **`XREADGROUP ... STREAMS events:orders >`**: `>` means "messages nobody in my group has been given yet". `BLOCK 5000` waits up to 5 seconds for new ones instead of asking in a tight loop.
3. **`XACK` only after handling succeeded.** Until then the message is *pending*: given to this copy, not finished.
4. **`XAUTOCLAIM`**: if a copy crashed while holding messages, they stay pending forever. Every loop, we claim pending messages older than 60 seconds and handle them ourselves. That's lesson 18's "stalled job", done by hand. A message that keeps failing would come back forever, so in the practice you'll count deliveries (`XPENDING` tells you) and move a message that's failed many times to a "dead letters" stream for a person to look at.
5. **A bad message is acked and logged**, not retried. It will never become valid.
6. **One consumer reads in order**, but with two copies, messages are processed side by side, so order across copies isn't guaranteed. Our handlers don't depend on order (step 6 checks the current state rather than trusting the order of events). If you ever need strict order per order, partition by order id. That's where systems like Kafka shine.

Redis Streams are a good fit for Mama Put: already running, simple, fast. Bigger systems use Kafka, NATS JetStream or RabbitMQ for the same idea with more guarantees, more tools, and more to run. The patterns here (outbox, envelopes, groups, acks, idempotent handlers) carry over unchanged.

## Step 6: the notifications service
<!-- bite: f2113482-cab4-45f6-9474-6fc741ee2a8e -->

`notifications/` is a new Node project, same setup as the API: TypeScript run directly, zod, pg, ioredis, `@grpc/grpc-js`.

```text
notifications/
├── package.json · tsconfig.json · .env.example
├── migrations/
│   ├── 001_sent_notifications.sql
│   └── 002_preferences.sql
└── src/
    ├── main.ts               ← composition root: db, redis, grpc clients, providers, consumer
    ├── consumer.ts           ← the consumer group loop
    ├── handlers.ts           ← one function per event type
    ├── sent.ts               ← sent_notifications: wasSent, record
    ├── clients/              ← gRPC clients for the API: menu, customers
    ├── providers/            ← mailer.ts, sms.ts (console versions for development)
    └── health.ts             ← a tiny HTTP server: GET /health
```

`notifications/migrations/001_sent_notifications.sql`:

```sql
CREATE TABLE sent_notifications (
  event_id     uuid        NOT NULL,
  kind         text        NOT NULL,     -- 'receipt-email', 'ready-sms', ...
  customer_id  text        NOT NULL,
  sent_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (event_id, kind)
);
```

The handlers, `notifications/src/handlers.ts`:

```ts
import { EVENTS, type Envelope } from "../../contracts/events.ts";

export function createHandlers(deps: Deps) {
  async function onOrderPaid(event: Envelope) {
    const data = EVENTS["order.paid"][1].parse(event.data);
    if (await deps.sent.wasSent(event.id, "receipt-email")) return;

    const [customer, dish] = await Promise.all([
      deps.customers.getContact(data.customerId),
      deps.menu.getDish(data.dishId),
    ]);
    if (!customer.email || !(await deps.preferences.wantsEmail(data.customerId))) return;

    await deps.mailer.send({
      to: customer.email,
      subject: `Mama Put receipt for order ${data.orderId}`,
      text: `Thank you, ${customer.firstName}! ${data.quantity} × ${dish.name}, ₦${(data.totalKobo / 100).toLocaleString("en-NG")}.`,
    });
    await deps.sent.record(event.id, "receipt-email", data.customerId);
  }

  async function onOrderReady(event: Envelope) {
    const data = EVENTS["order.ready"][1].parse(event.data);
    if (await deps.sent.wasSent(event.id, "ready-sms")) return;
    const customer = await deps.customers.getContact(data.customerId);
    if (!customer.phone || !(await deps.preferences.wantsSms(data.customerId))) return;
    await deps.sms.send(customer.phone, `Mama Put: order ${data.orderId} is ready. Come and enjoy!`);
    await deps.sent.record(event.id, "ready-sms", data.customerId);
  }

  return async function handle(event: Envelope) {
    if (event.type === "order.paid" && event.version === 1) return onOrderPaid(event);
    if (event.type === "order.ready" && event.version === 1) return onOrderReady(event);
    // Anything else: not for us. Returning normally acks it.
  };
}
```

1. **Unknown types and versions are ignored**, not errors. The API will publish events notifications doesn't care about (`order.placed`), and new versions before notifications has learned them. Ignoring them is what lets the API change without asking notifications first.
2. **`wasSent` then send then `record`**: lesson 18's choice. If the service crashes after sending but before recording, the message is redelivered and sent again. A duplicate receipt is better than none. The primary key `(event_id, kind)` stops normal repeats.
3. **Contact details come from the API**, fresh, at the moment of sending, via gRPC: a new `CustomersService.GetContact` in `proto/mamaput/customers/v1/customers.proto`, served by the API next to `MenuService`. It returns first name, email and phone, and nothing else.
4. **If a gRPC call fails, the handler throws**, the message isn't acked, and it's retried. The customer gets the receipt a little late. That's the whole point of the split: the API being briefly unreachable delays texts; it never loses them, and texts being slow never delays orders.

`GetContact` returns personal data to another service. Right now, anything that can reach port 50051 could call it. That's not acceptable for long, and it's the first thing lesson 26 fixes, with service-to-service authentication. Until then, the port must stay on the internal network only.

`main.ts` builds everything and runs the loop, with a polite shutdown like lesson 18's worker: on `SIGTERM`, set `stopped`, let the current message finish, close Redis, Postgres and the gRPC clients.

Run it in a third terminal:

```bash
npm run dev -w notifications
```

Pay for an order (or send yourself a signed test webhook, lesson 17), and watch: the API commits the payment and the outbox row together; the relay publishes it; the notifications service reads it, calls the API over gRPC for the contact and dish name, and the console mailer prints the receipt.

## Step 7: what changes in the API
<!-- bite: 15e2c9d2-2741-4c38-a155-53ec6c8a64ad -->

1. **Deleted**: the `send-receipt` job and processor, the `emails` queue, the `Mailer`, the receipts part of the sweeper, the email provider's key. The API no longer sends any email at all.
2. **Added**: the outbox, the relay (in the worker), `addToOutbox` in `markSucceeded`, `updateStatus` and `place`, and `CustomersService` on the gRPC server.
3. **Changed**: partner webhooks now come from the API's own consumer group, `partner-webhooks`, reading `order.ready`, instead of from inside `updateStatus`.

Count what the notifications team can now do without touching the API: change any message's wording, add a WhatsApp channel, switch email providers, add quiet hours. And what the API team can do without touching notifications: everything, as long as the events keep their shape.

## Step 8: testing across services
<!-- bite: 40e31770-d188-4fa6-97b4-9d5b958c3f8c -->

1. **Handlers, alone**: fake `customers`, `menu`, `mailer`, `sent`. Feed an `order.paid` envelope; check one email. Feed it again; check still one. Feed an unknown type; check nothing happens and nothing throws.
2. **The outbox, against Postgres** (lesson 16's integration tests): `markSucceeded` leaves exactly one `order.paid` row; a second call leaves still one; a failed transaction leaves none.
3. **The relay**: after `runOnce`, rows have `published_at` and the stream has the events. Point it at a test Redis database.
4. **The consumer**: put three events in a test stream; run one loop; check they're acked. Make the handler throw once; check the message is still pending, then gets handled after `XAUTOCLAIM`.
5. **The contract**: both sides import `contracts/events.ts`, so a test in the API that builds every event it publishes and parses it with the contract schema catches drift before it ships. Lesson 29 runs the tests of both services on every change, which is the real payoff of the monorepo.

## The TypeScript in this lesson
<!-- bite: d7e24102-f661-4fd9-8a80-bcd88f65dbbb -->

1. **`import { Envelope } from "../../contracts/events.ts"`**: An import from outside the service's own folder, using a relative path. Both services do this, so there's one copy of the contract. (Lesson 28 makes sure the Docker builds include `contracts/`.)
2. **`export const Envelope = z.object(...)` and `export type Envelope = z.infer<typeof Envelope>`**: The same name for a value (the schema) and a type (its shape). TypeScript keeps values and types apart, so this is allowed and common with zod.
3. **`z.uuid()`, `z.iso.datetime()`**: zod 4's top-level checks for a UUID and for an ISO 8601 date-time string like `2026-11-21T12:40:03.000Z`.
4. **`EVENTS["order.paid"][1].parse(event.data)`**: Looks up the schema for a type and version, then checks the data. Because `EVENTS` is `as const`, TypeScript knows exactly which schema that is, and `data` gets its real type.
5. **`(await redis.xreadgroup(...)) as [string, [string, string[]][]][] | null`**: Stream commands return deeply nested arrays, and ioredis types them loosely. The cast writes out what Redis really returns: a list of streams, each with a list of `[messageId, [field, value, field, value...]]`.
6. **`for (const [messageId, fields] of entries)`**: Destructuring each entry into its two parts right in the loop.
7. **`fields[fields.indexOf("event") + 1]`**: Stream fields come as a flat list, `["event", "{...}"]`. The value is the item after the field's name.
8. **`(async function loop() { ... })()`**: An async function started immediately and not awaited, so `start` returns at once while the loop runs on.
9. **`await new Promise((r) => setTimeout(r, everyMs))`**: A promise that resolves after a delay: the usual way to "sleep" in async code.
10. **`return onOrderPaid(event)`** inside an `async` function: returning a promise from an async function waits for it, so errors from the handler still reach the consumer's `catch`.

## Your project so far
<!-- bite: fc9417f6-7ed3-47e5-9928-d8ab8988e0f1 -->

```text
mama-put/
├── proto/
│   └── mamaput/
│       ├── menu/v1/menu.proto
│       └── customers/v1/customers.proto   ← NEW: CustomersService.GetContact
├── package.json · package-lock.json      ← NEW: npm workspaces: api, notifications, contracts
├── node_modules/                         ← NEW: one, shared, at the top
├── contracts/
│   ├── package.json                      ← NEW: depends on zod
│   └── events.ts                         ← NEW: Envelope, OrderPaidV1, OrderReadyV1, EVENTS
├── api/                                  ← the old mama-put-api
│   ├── migrations/   001 … 014
│   │   └── 015_outbox.sql                ← NEW
│   └── src/
│       ├── events/
│       │   ├── outbox.ts                 ← NEW: addToOutbox(tx, ...)
│       │   ├── relay.ts                  ← NEW: outbox → events:orders, SKIP LOCKED
│       │   └── partner-webhooks.consumer.ts ← NEW: order.ready → webhook delivery (closes lesson 17's gap)
│       ├── grpc/customers.server.ts      ← NEW: GetContact
│       ├── payments/ · orders/           ← write their events into the outbox, in the same transaction
│       ├── worker.ts                     ← runs the relay and the partner-webhooks consumer; no more emails
│       └── jobs/ · mcp/ · graphql/ · kitchen/ · menu/ · auth/ · shared/ · webhooks/ · admin/ · docs/ · db/
└── notifications/                        ← NEW service
    ├── package.json · tsconfig.json · .env.example
    ├── migrations/   001_sent_notifications.sql · 002_preferences.sql
    └── src/
        ├── main.ts                       ← composition root, polite shutdown
        ├── consumer.ts                   ← XGROUP, XREADGROUP, XACK, XAUTOCLAIM
        ├── handlers.ts                   ← order.paid → receipt email; order.ready → text
        ├── sent.ts · preferences.ts
        ├── clients/menu.ts · clients/customers.ts
        ├── providers/mailer.ts · providers/sms.ts
        ├── health.ts
        └── *.test.ts
```

## Common mistakes
<!-- bite: 5edc0259-8f7c-49b5-aa8a-06f5da1fa497 -->

1. **Splitting too early, or the wrong thing.** A service the main flow waits on turns every request into network calls that can fail.
2. **Sharing a database.** A shared table is a hidden contract, and the two services can never deploy apart.
3. **Publishing straight after committing.** A crash in between loses the event for good. Use the outbox.
4. **Publishing before committing.** Everyone hears about something that then didn't happen.
5. **Acking before handling.** A crash loses the message. Ack after.
6. **Assuming each event arrives once.** The relay and the stream both deliver at least once. Skip ids you've handled.
7. **Treating unknown event types as errors.** Then every new event the API adds breaks every consumer.
8. **Personal data in events.** Events are stored and read by everyone, forever. Carry ids; fetch details when needed.
9. **Commands dressed as events.** `send-receipt-email` from the API means the API still decides what notifications does. Say what happened (`order.paid`), and let notifications decide.
10. **No plan for messages that always fail.** They come back forever. Count attempts and move them aside.

## Check your understanding
<!-- bite: c0096644-3f5a-4dba-8883-a84d517a6724 -->

1. Why is notifications a better first service to split out than payments?
2. Why can't the notifications service just read `users.email` from the API's database?
3. The API commits a payment and crashes before the relay runs. Is the `order.paid` event lost?
4. The relay publishes an event and crashes before marking it published. What happens, and why is it safe?
5. Two copies of notifications are in the same consumer group. Does each send a receipt?
6. The API starts publishing `order.placed`, which notifications has never heard of. What does notifications do?

<details>
<summary>Answers, after your attempt</summary>

1. Nothing in the main flow waits for notifications: a receipt can be late without any request failing. Payments is needed in the middle of an order, so splitting it out would turn every order into a network call that can fail. Notifications also talks to unreliable providers whose problems we want kept away from orders.
2. Because then the table is a hidden contract: rename or change the column, and notifications breaks without warning, and the two services can't be deployed separately any more. Each service's database is private; data crosses only through events and APIs.
3. No. The event was written to the outbox in the same transaction as the payment, so it's in Postgres. When the worker starts again, the relay finds it unpublished and publishes it.
4. The row is still unpublished, so the next run publishes it again: the stream gets two copies of the same event, with the same `id`. Consumers check `sent_notifications` by event id and skip the second, so the customer gets one receipt.
5. No. A consumer group gives each message to one member. They share the work; each event is handled once by the group (or occasionally twice after a crash, which the event id handles).
6. Ignores it. The handler only acts on the types and versions it knows; anything else returns normally and is acked. That's what lets the API add events without coordinating with every consumer.

</details>

## Practice
<!-- bite: f58828f3-a206-494b-92a9-3fe9967b1e9a -->

1. Write `customers.proto` and `CustomersService.GetContact` in the API, returning only first name, email and phone.
2. Add `addToOutbox` to `updateStatus` (`order.ready`, `order.collected`) and `place` (`order.placed`), each inside its transaction.
3. Write the API's `partner-webhooks` consumer, and delete the `deliveries.enqueue` call from `updateStatus`.
4. Add dead letters: use `XPENDING` to find messages delivered more than 5 times, copy them to `events:dead` with the error, and ack them. Add an admin route in the API (or a script) to look at them.
5. Move the "how was your food?" email to notifications: on `order.collected`, schedule it an hour later (BullMQ in notifications' own Redis queue, or a `send_at` column and a loop).
6. Write the tests from step 8.

**Done when** paying for an order sends one receipt from the notifications service while the API has no email code left; stopping the notifications service, paying for three orders, and starting it again sends all three receipts; killing the API's worker in the middle of relaying and starting it again still delivers every event (and no customer gets two receipts); and the notifications database user can't read any table in `mama_put`.

## Before moving on
<!-- bite: 67cee14c-74fc-4f72-871e-60e1b1c12c4a -->

Mama Put is now two services: the API, which owns orders, payments and customers, and notifications, which owns how and when customers hear from us. They share no tables. The API says what happened, reliably, through the outbox and a stream; notifications listens, at its own pace, and asks the API for details over gRPC.

That gRPC call is the new weak spot. Notifications calls `GetContact` and `GetDish` for every message. What happens when the API is slow, or restarting, or overloaded? Right now, notifications waits, retries in a tight loop, and piles more load onto an API that's already struggling. And anything on the internal network can call `GetContact` and read customers' details. Calling other services *safely* is a skill of its own: deadlines, careful retries, circuit breakers, and proving who's calling. That's the next lesson.

## Related
<!-- bite: 1569b4b4-bcce-48b3-9494-74ef41e151af -->

- [[backend/frameworks/express/26-calling-services-safely|Next: Calling Other Services Safely]]
- [[backend/frameworks/express/22-grpc|gRPC]] — the calls notifications makes back to the API
- [[backend/frameworks/express/18-background-jobs|Background Jobs and Queues]] — at-least-once delivery, the first time
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — monoliths, modules and where to draw boundaries

## About this lesson
<!-- bite: 5c0a7e6a-2a88-4122-8d97-aa50c092a24d -->

**Level:** Advanced. Lesson 25 of [[backend/frameworks/express/index|Express]]. Covers the real reasons to split a service and the costs, "monolith first", choosing a good first service, a monorepo layout, private databases per service, events versus commands, event envelopes, versions and how much data to carry, keeping personal data out of events, the outbox pattern written in the same transaction as the change, a relay with `FOR UPDATE SKIP LOCKED` and `XADD` with trimming, at-least-once delivery and event ids, Redis Streams consumer groups with `XGROUP`, `XREADGROUP`, `XACK` and `XAUTOCLAIM`, ignoring unknown events, idempotent handlers, the notifications service fetching fresh details over gRPC, what moved out of the API, and testing handlers, the outbox, the relay, the consumer and the shared contract.
