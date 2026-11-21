---
id: 2458e16d-ccf2-4809-8319-07fc0e1f89fc
---

# Real-time Updates

**Real-time updates mean the server tells the client the moment something changes, instead of the client asking again and again. The connection stays open, and the server writes to it whenever there's news.** Every response so far ended when it was sent. This lesson's response doesn't end: the kitchen screen opens one connection in the morning, and new orders arrive on it all day.

## Before you start
<!-- bite: dad67e03-adf5-4065-a399-fbaf7a4bbfb8 -->

You should have caching and both Redis servers from [[backend/frameworks/express/19-caching|lesson 19]], and the "only paid orders get cooked" rule from [[backend/frameworks/express/17-payments-and-webhooks|lesson 17]].

After this lesson you will be able to:

1. Compare polling, long polling, server-sent events and WebSockets, and pick one.
2. Stream events from Express with server-sent events, with heartbeats and clean-up.
3. Log a browser in to a stream when `EventSource` can't send an `Authorization` header.
4. Make it work with several servers, using Redis publish/subscribe.
5. Never lose an order when the screen's connection drops, with "snapshot, then changes".

## Where we stopped
<!-- bite: 1629a0ee-0e51-4e0e-8e69-0fd039ee3b66 -->

The kitchen has a tablet on the wall showing open orders. It calls `GET /v2/orders?status=pending&paid=true` when the cook taps refresh.

At 12:40, Ada pays. Her order is in the database, paid, ready to cook. And it sits there until someone wipes their hands and taps refresh. Maybe 30 seconds, maybe 3 minutes. Ada watches the clock.

The obvious fix, "refresh every 2 seconds by itself", is called polling. It works, but count it: one tablet, 30 requests a minute, 43,000 a day, nearly all answering "nothing new". Five branches, a customer-facing "where's my order" screen on every phone... it adds up to most of your traffic, all saying nothing.

## The kid version
<!-- bite: d4226027-c5b7-4752-8439-7546a8566d37 -->

Bayo is waiting for his food. He can walk up to the counter every minute and ask "is it ready?". Mama says "no" fifty times and gets annoyed.

Or Mama can say "sit down, I'll shout your name". Bayo sits. The moment it's ready, Mama shouts "Bayo!".

Asking every minute is polling. "I'll shout your name" is a server-sent event: Bayo keeps listening, and Mama speaks only when there's something to say.

**Where the picture stops working.** If Bayo steps outside to take a call, he misses the shout, and Mama doesn't shout twice. Our screens will step outside too (Wi-Fi drops), so when they come back, they must be able to ask "what did I miss?".

## Terms used in real-time updates
<!-- bite: 2bbf602a-e45c-4f8e-aba7-eed9ac320dd2 -->

1. **Polling**: This is the client asking again on a timer, "anything new?". Simple, wasteful.
2. **Long polling**: This is the client asking, and the server *holding* the request open until there's news (or a timeout), then the client asks again straight away.
3. **Server-sent events (SSE)**: This is one long HTTP response that the server keeps writing small text events into. One direction: server to client.
4. **WebSocket**: This is a two-way connection that starts as HTTP and then switches to its own protocol. Both sides can send at any time.
5. **`EventSource`**: This is the browser's built-in SSE client. It connects, reads events, and reconnects by itself if the connection drops.
6. **Heartbeat**: This is a tiny message sent every so often just to keep the connection alive, so proxies don't close it for being quiet.
7. **Publish/subscribe (pub/sub)**: This is a messaging style where publishers send messages to a named channel, and every subscriber to that channel receives them. Redis has it built in.
8. **Fan-out**: This is one event being sent to many listeners.

## Step 1: choosing
<!-- bite: 12ac10b4-01c3-4ec9-8782-71c4ae4a0441 -->

| | Direction | Works through ordinary HTTP | Reconnects by itself | Good for |
|---|---|---|---|---|
| Polling | client asks | yes | n/a | rare checks ("every 5 minutes") |
| Long polling | client asks, server waits | yes | you write it | old systems |
| **SSE** | server → client | **yes** | **yes** (`EventSource`) | feeds, dashboards, notifications, "your order is ready" |
| WebSocket | both ways | needs an upgrade | you write it | chat, games, collaborative editing |

The kitchen screen only *listens*. When a cook taps "ready", that's a normal `PATCH` request, which we already have. So the stream is one-way: server to screen. That's exactly what SSE is for.

SSE is also just HTTP. Our middleware, auth, logging, proxies and HTTPS all work on it unchanged. A WebSocket switches away from HTTP after the first request, so middleware stops applying, and proxies need extra setup. Choose WebSockets when you really need both directions at high speed (Ada chatting with her rider, say). The `ws` package is the usual choice in Node then.

## Step 2: what an SSE response looks like
<!-- bite: 529c14a1-d91d-4ac7-888f-5bb39f055d87 -->

An SSE response is plain text, with a special content type, and it doesn't end:

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 1700000000123-0
event: order.paid
data: {"id":"42","dishId":"1","quantity":2,"paidAt":"2026-11-21T12:40:03.000Z"}

: ping

id: 1700000004311-0
event: order.status
data: {"id":"42","status":"ready"}

```

Each event is a few lines, ended by a **blank line**:

1. **`event:`** names the kind of event. The browser can listen for each name separately.
2. **`data:`** is the content. We send JSON on one line.
3. **`id:`** is the event's id. If the connection drops, `EventSource` reconnects and sends the last id it saw in a `Last-Event-ID` header.
4. A line starting with **`:`** is a comment. The browser ignores it, which makes it the perfect heartbeat.

## Step 3: the stream in Express
<!-- bite: ab708eca-28f8-434b-a05e-dafcbc3b56c4 -->

`src/kitchen/sse.ts`, a tiny helper that knows the format:

```ts
import type { Response } from "express";

export function openStream(res: Response) {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache, no-transform",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",        // tells nginx-style proxies not to hold events back
  });
  res.flushHeaders();
  res.write("retry: 3000\n\n");        // if we disconnect, reconnect after 3 s

  const heartbeat = setInterval(() => res.write(": ping\n\n"), 25_000);

  return {
    send(event: string, data: unknown, id?: string) {
      if (id) res.write(`id: ${id}\n`);
      res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
    },
    close() {
      clearInterval(heartbeat);
    },
  };
}
```

`res.writeHead` sends the status and headers right away; `res.write` sends a piece of the body and keeps the response open. We never call `res.end()` or `res.json()`; the response ends only when someone disconnects.

The heartbeat every 25 seconds matters more than it looks. Proxies and load balancers close connections that have been quiet for a while (often 60 seconds). A quiet kitchen at 3 p.m. would be disconnected again and again. A comment line every 25 seconds keeps it awake.

`JSON.stringify` never produces a raw newline inside its output (newlines in strings become `\n`), so the `data:` is always one line, which keeps the format safe. If you ever send plain text, each line needs its own `data:` prefix.

The route, `src/kitchen/kitchen.routes.ts`:

```ts
router.get("/orders/stream", requireStreamTicket, async (req, res) => {
  const stream = openStream(res);

  // 1. Everything open right now.
  const open = await ordersService.openForKitchen(req.user!);
  stream.send("snapshot", open.map(presentKitchenOrder));

  // 2. Then every change, as it happens.
  const unsubscribe = kitchenEvents.subscribe((event) => {
    stream.send(event.type, event.data, event.id);
  });

  req.on("close", () => {
    unsubscribe();
    stream.close();
  });
});
```

`req.on("close")` fires when the tablet goes away: the browser tab closes, the Wi-Fi drops, the cook pulls the plug. Forget it, and every disconnected screen leaves a subscriber and a timer behind, still trying to write into a dead connection. A few days of that, and the server runs out of memory. **Every open must have a close.**

And the order of 1 and 2 is the next step's whole point.

## Step 4: never miss an order
<!-- bite: a962513f-92cf-4f6f-bd42-552ea1e90883 -->

The tablet's Wi-Fi drops for 20 seconds. In that time, two orders are paid. `EventSource` reconnects. Did the kitchen miss them?

Redis pub/sub (step 6) doesn't store messages: if you weren't listening when it was sent, it's gone. So the stream starts with a **snapshot**: the full list of open, paid orders, straight from Postgres. Then it sends changes.

On every connection, including every reconnection, the screen gets the whole truth first. It throws away what it had and draws the snapshot. The two missed orders are in it. Nothing is lost, and we didn't need to store every event in a replay log.

One small gap: an order paid in the instant *between* reading the snapshot and subscribing would be in neither. Swap the order to close it: subscribe first (holding events in a short list), then read the snapshot, then send the snapshot and the held events. The screen may get an event for an order already in the snapshot, so it must handle "update order 42" by replacing, not adding a second card. Handling duplicates gracefully is cheaper than preventing them perfectly. (The practice task does this.)

What about `Last-Event-ID`? A system that keeps every event (Redis Streams can, and we'll meet them in [[backend/frameworks/express/25-splitting-out-a-microservice|lesson 25]]) can use it to send just what was missed. For a kitchen with maybe 30 open orders, a fresh snapshot is simpler and always right.

## Step 5: logging in a browser stream
<!-- bite: a21d7992-1c69-4d4b-b378-d3497e20b451 -->

Here's a snag. Every route uses `Authorization: Bearer <token>`. The browser's `EventSource` **can't send custom headers**. Its only option is `new EventSource(url)`.

Three ways out:

1. **Put the access token in the URL**: `?token=eyJ...`. Don't. URLs end up in server logs, proxy logs and browser history, and the token is a 15-minute key to the account.
2. **Use a fetch-based SSE client** in the browser, which can send headers. It works, and some teams prefer it. You lose `EventSource`'s built-in reconnection unless the library rebuilds it.
3. **A short-lived, one-use stream ticket.** The screen asks for a ticket with its normal token, then opens the stream with the ticket.

We'll do 3, because it keeps `EventSource` and keeps tokens out of URLs.

```ts
// POST /v2/kitchen/stream-tickets  (normal Bearer auth, staff only)
router.post("/stream-tickets", requirePermission("kitchen:watch"), async (req, res) => {
  const ticket = randomBytes(24).toString("base64url");
  await redis.set(`ticket:${ticket}`, JSON.stringify(req.user), "EX", 30);
  res.status(201).json({ data: { ticket, expiresInSeconds: 30 } });
});
```

```ts
// src/kitchen/require-stream-ticket.ts
export function createRequireStreamTicket(redis: Redis) {
  return async (req: Request, _res: Response, next: NextFunction) => {
    const ticket = typeof req.query.ticket === "string" ? req.query.ticket : "";
    const stored = ticket ? await redis.getdel(`ticket:${ticket}`) : null;
    if (!stored) throw new AppError("unauthenticated", "bad-stream-ticket", "Ask for a new stream ticket.");
    req.user = JSON.parse(stored);
    next();
  };
}
```

The ticket is still in a URL, so it might be logged, but look at what it's worth to anyone who finds it: it worked for 30 seconds, and only once. `GETDEL` reads and deletes in one command, so two requests can't both use it. (Store tickets in the **queue** Redis, the one that doesn't evict.)

And the kitchen permission is a new action in lesson 13's policy table: `"kitchen:watch": isStaff`. Add it, and TypeScript tells you everywhere it needs handling.

When `EventSource` reconnects after a drop, it reuses the same URL, with the ticket that's already been used, and gets a 401. So the screen's code listens for the error, fetches a new ticket, and opens a new `EventSource`:

```js
// on the kitchen screen (browser JavaScript)
async function connect() {
  const { data } = await api.post("/v2/kitchen/stream-tickets");
  const source = new EventSource(`/v2/kitchen/orders/stream?ticket=${data.ticket}`);
  source.addEventListener("snapshot", (e) => drawAll(JSON.parse(e.data)));
  source.addEventListener("order.paid", (e) => upsertCard(JSON.parse(e.data)));
  source.addEventListener("order.status", (e) => upsertCard(JSON.parse(e.data)));
  source.onerror = () => {
    source.close();
    setTimeout(connect, 3000);
  };
}
connect();
```

## Step 6: more than one server
<!-- bite: 4d0d4225-030f-4b05-8bfa-3af8f502b977 -->

So far, `kitchenEvents.subscribe` could be a simple in-memory list of listeners. Then think about two servers behind a load balancer:

1. The kitchen tablet is connected to **server A**.
2. Paystack's webhook for Ada's payment lands on **server B**.
3. Server B marks the order paid and tells *its* listeners. It has none. The tablet, on A, hears nothing.

Each server only knows its own connections. So the news must go through something they all share, and that's Redis **pub/sub**: B **publishes** "order 42 paid" to a channel; A and B both **subscribe** to that channel; each passes it on to its own screens.

`src/kitchen/kitchen-events.ts`:

```ts
import { Redis } from "ioredis";

export type KitchenEvent = { id: string; type: "order.paid" | "order.status"; data: unknown };
type Listener = (event: KitchenEvent) => void;

const CHANNEL = "kitchen";

export function createKitchenEvents(redisUrl: string, log: (m: string, d: object) => void) {
  const publisher = new Redis(redisUrl);
  const subscriber = new Redis(redisUrl);       // a subscribing connection can't do anything else
  const listeners = new Set<Listener>();

  subscriber.subscribe(CHANNEL).catch((err) => log("kitchen subscribe failed", { error: err.message }));
  subscriber.on("message", (_channel, message) => {
    const event = JSON.parse(message) as KitchenEvent;
    for (const listener of listeners) {
      try {
        listener(event);
      } catch (err) {
        log("kitchen listener failed", { error: (err as Error).message });
      }
    }
  });

  return {
    async publish(type: KitchenEvent["type"], data: unknown) {
      const event: KitchenEvent = { id: `${Date.now()}-${crypto.randomUUID().slice(0, 8)}`, type, data };
      await publisher.publish(CHANNEL, JSON.stringify(event));
    },
    subscribe(listener: Listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    async close() {
      await Promise.all([publisher.quit(), subscriber.quit()]);
    },
  };
}

export type KitchenEvents = ReturnType<typeof createKitchenEvents>;
```

The design keeps Redis connections fixed: **one** subscription per server, however many screens are watching. Each screen is just an entry in the `listeners` set. A hundred screens don't mean a hundred Redis connections.

The subscriber needs its own connection because, once a Redis connection subscribes, it can only receive messages. Normal commands on it fail. So: one connection to publish, one to listen.

Which Redis? Pub/sub messages aren't stored, so eviction doesn't matter, but use the queue Redis anyway. The cache Redis is allowed to go down without harm; the kitchen feed shouldn't be.

**Publishing.** In the payments service, where `settle` gets `"paid"`:

```ts
if (result === "paid") {
  await jobs.sendReceipt(payment.id);
  await kitchenEvents.publish("order.paid", presentKitchenOrder(await ordersRepository.findById(payment.orderId)));
}
```

and in the orders service after a status change, `publish("order.status", { id, status })`. `settle` also runs in the worker (lesson 18's hourly check), and that's fine: the worker publishes to the same Redis channel, and every API server passes it on. Anything that can publish to Redis can reach the kitchen.

If the publish fails, the order is still paid; the kitchen just doesn't hear about it until its next snapshot. That's why the snapshot matters: the live feed is a convenience on top of the truth, never the truth itself. (For extra safety, the screen can reconnect every few minutes on purpose, which gets a fresh snapshot.)

`presentKitchenOrder` sends what the kitchen needs (order id, dish, quantity, when it was paid, the customer's first name for calling out) and nothing else. No phone numbers on a tablet hanging on a wall that anyone in the shop can read.

## Step 7: limits and the rest of the app
<!-- bite: 30e67eba-f878-4072-bc48-2ae75b54d24a -->

A stream holds a connection open for hours. A few things to check:

1. **Lesson 14's timeouts.** `server.requestTimeout` limits how long the *request* may take to arrive. A GET has no body, so it arrives at once, and the long *response* is fine. But a proxy in front may have its own response timeout; the heartbeat keeps most of them happy, and lesson 28 sets the proxy up properly.
2. **Compression.** If you ever add the `compression` middleware, it buffers output to compress it, and events get held back. Skip it for `text/event-stream` (its filter option does this), or let the proxy compress.
3. **Rate limits.** Opening a stream is one request, but the ticket route should be rate-limited like login, so nobody can make thousands of tickets.
4. **Connection count.** Each open stream is a socket. Thousands are fine for Node. Count them (a number that goes up on open and down on close) so lesson 27 can graph it, and so a leak shows up as a line that only goes up.
5. **Shutting down.** When the server stops (lesson 28), it should end every stream so screens reconnect to a healthy server, instead of waiting for a timeout.

## Step 8: a stream for customers too
<!-- bite: 1b4dddd8-500c-46f0-8d7d-a962eba49006 -->

Ada would like to see "Your order is being cooked... Ready!" on her phone. Same building blocks:

1. `GET /v2/orders/:id/stream`, with a ticket that also records the order id, checked with lesson 13's `owns` rule, so Ada can only watch her own order.
2. A snapshot first (the order's current status), then `order.status` events **for that order only**: the listener checks `event.data.id === orderId` before sending.
3. Close the stream from the server when the order is `collected`. There's nothing more to say.

Filtering by order id on each server is fine at Mama Put's size. A very large system would use a channel per order (`order:42`) instead, so servers only receive what their listeners care about.

## Step 9: testing
<!-- bite: fb3a491e-7a25-4fd4-b932-c289d1dd1ab5 -->

1. **The format** is a pure function: test that `send("order.paid", {...}, "1")` writes exactly `id: 1\nevent: order.paid\ndata: {...}\n\n`.
2. **`createKitchenEvents`** gets an in-memory version for tests (a set of listeners, no Redis), with the same `publish` and `subscribe`.
3. **The route**: supertest waits for the response to finish, and this one never does. Use Node's own `http.get` against `app.listen(0)` (port 0 means "any free port"), read the first chunk, and check it holds the snapshot. Then publish an event and check it arrives. Then destroy the request and check the listener count went back to zero, which is the leak test.
4. **Tickets**: a ticket works once; the second use is 401; a ticket older than 30 seconds is 401 (fake the clock, or set the TTL to 1 in the test).

## The TypeScript in this lesson
<!-- bite: 3c1d7c07-9642-42de-9ea7-441b5771778c -->

1. **`res.writeHead(200, {...})` and `res.write(...)`**: These come from Node's own response object, under Express. `writeHead` sends the status and headers; `write` sends a piece of the body without ending it.
2. **`setInterval(...)` and `clearInterval(heartbeat)`**: `setInterval` returns a handle; passing it to `clearInterval` stops the timer.
3. **`req.on("close", () => {...})`**: Requests are event emitters. `"close"` fires when the connection is gone, for whatever reason.
4. **`type KitchenEvent = { ...; type: "order.paid" | "order.status"; ... }`** and **`KitchenEvent["type"]`**: An indexed access type: "the type of the `type` field of `KitchenEvent`". The `publish` parameter can never drift from the event definition.
5. **`new Set<Listener>()`**: A collection with no duplicates and fast add and delete. Good for "everyone currently listening".
6. **`return () => listeners.delete(listener)`**: `subscribe` returns its own undo function, the same pattern as lesson 17's `start`.
7. **`typeof req.query.ticket === "string" ? req.query.ticket : ""`**: Query values can be a string, an array (`?ticket=a&ticket=b`), or missing. Checking `typeof` narrows it to exactly a string.
8. **`redis.getdel(key)`**: Gets and deletes in one command, so only one request can ever get the value.
9. **`for (const listener of listeners)`**: `for...of` works on sets as well as arrays.
10. **`crypto.randomUUID()` without an import**: In Node, `crypto` is also available globally, like in browsers. Importing it from `node:crypto` is the same thing, and clearer.

## Your project so far
<!-- bite: 2a2a262e-a565-4c62-8270-b3ec2c56c00b -->

```text
mama-put-api/
├── migrations/   001 … 013
└── src/
    ├── server.ts                 ← builds kitchenEvents (queue Redis), passes it to payments and orders
    ├── worker.ts                 ← builds kitchenEvents too, so the hourly check can publish
    ├── kitchen/
    │   ├── sse.ts                ← NEW: openStream: headers, retry, heartbeat, send, close
    │   ├── kitchen-events.ts     ← NEW: Redis pub/sub, one subscription per server, a set of listeners
    │   ├── kitchen-events.memory.ts ← NEW: the in-memory version for tests
    │   ├── require-stream-ticket.ts ← NEW: one-use, 30-second tickets with GETDEL
    │   ├── kitchen.routes.ts     ← NEW: POST /stream-tickets, GET /orders/stream (snapshot, then changes)
    │   ├── kitchen.presenter.ts  ← NEW: presentKitchenOrder: only what a wall screen should show
    │   └── kitchen.routes.test.ts ← NEW: snapshot arrives, events arrive, no leak after disconnect
    ├── auth/policy.ts            ← NEW action: kitchen:watch
    ├── orders/                   ← openForKitchen(); publishes order.status; GET /:id/stream for customers
    ├── payments/                 ← settle publishes order.paid
    └── jobs/ · shared/ · menu/ · webhooks/ · admin/ · docs/ · db/ · types/ · test-support/
```

## Common mistakes
<!-- bite: 5edf7d00-5345-4272-b805-5eb3dea407f1 -->

1. **Polling when you mean "tell me".** Thousands of requests saying "nothing new".
2. **No heartbeat.** Proxies close quiet connections, and the screen silently stops getting orders.
3. **No clean-up on `close`.** Every disconnect leaks a listener and a timer.
4. **Trusting the live feed alone.** Pub/sub forgets. Send a snapshot on every connection.
5. **Access tokens in the URL.** They end up in logs. Use a short, one-use ticket.
6. **In-memory events with more than one server.** The event happens on one server and the screen is on another. Go through Redis.
7. **One Redis subscription per screen.** Subscribe once per server and fan out in memory.
8. **Sending more than the screen needs.** A wall tablet is a public place.
9. **Choosing WebSockets for one-way updates.** SSE is simpler and stays inside normal HTTP.

## Check your understanding
<!-- bite: 62403484-5ce4-4bf6-8618-4adde549e56b -->

1. Why SSE instead of WebSockets for the kitchen screen?
2. The tablet is on server A; the payment webhook arrives at server B. Trace how the order reaches the tablet.
3. The Wi-Fi drops for a minute and three orders are paid. How does the kitchen find out about them?
4. Why can't the stream route use `requireUser`, like every other route?
5. Why does each server subscribe to Redis once, not once per screen?
6. What would happen, over a week, if the route forgot `req.on("close")`?

<details>
<summary>Answers, after your attempt</summary>

1. The screen only listens; actions are ordinary `PATCH` requests. SSE is plain HTTP, so auth, logging and proxies work as they are, and `EventSource` reconnects by itself. WebSockets add a second protocol for a two-way channel we don't need.
2. B's `settle` returns `"paid"` and publishes `order.paid` to the `kitchen` channel in Redis. Redis sends it to every subscriber, including A's one subscription. A loops over its listeners, and the tablet's listener writes the event into its open response.
3. When it reconnects, the stream starts with a snapshot of every open, paid order from Postgres, and the three are in it. Nothing depends on having heard the live events.
4. `requireUser` reads the `Authorization` header, and `EventSource` can't send one. The screen gets a one-use, 30-second ticket with its normal token, and the stream checks the ticket instead.
5. So Redis connections stay fixed however many screens connect. Each screen is just a function in the server's set of listeners.
6. Every disconnected screen would leave its listener in the set and its heartbeat timer running. Memory would climb all week, the server would keep trying to write to dead connections, and eventually it would slow down or crash. The connection count graph would only ever go up.

</details>

## Practice
<!-- bite: 9e1e504a-6d67-45fd-9d4b-10d97a79477e -->

1. Close the snapshot gap: subscribe first and hold events in an array, read the snapshot, send it, then send the held events and switch to sending live.
2. Write the customer stream, `GET /v2/orders/:id/stream`, with tickets that record the order id, the `owns` check, filtering, and closing when the order is collected.
3. Count open streams, and show the number in `GET /v2/admin/queues`.
4. On shutdown (`SIGTERM`), end every open stream before the server stops, so screens reconnect elsewhere.
5. Write the tests from step 9, including the leak test.

**Done when** a test payment makes a card appear on the kitchen screen within a second without anyone refreshing, it still works with two servers on different ports (screen on one, webhook sent to the other), turning the Wi-Fi off and on shows every order paid in between, a used ticket gets 401, and the open-streams count goes back to zero after closing every tab.

## Before moving on
<!-- bite: 4b068fce-b53b-46d4-9330-535c46513051 -->

The kitchen now hears about every paid order the moment it happens, across any number of servers, and never misses one, because each connection starts from the truth.

That's the end of Part 4. Mama Put API is a full product: accounts, payments, webhooks, jobs, caching, live updates, all over one style of API, REST. But not every client wants REST. The new phone app team says: "the order screen needs the order, its dish, the dish's photo and the customer's last three orders, and that's four REST calls on a slow network". They want to ask for exactly what they need, in one request. That's GraphQL, and it starts Part 5: other ways to talk.

## Related
<!-- bite: b89170ce-9eae-4fd0-a916-32988011fe0e -->

- [[backend/frameworks/express/21-graphql|Next: GraphQL]]
- [[backend/frameworks/express/19-caching|Caching with Redis]] — the other Redis, and why the feed doesn't use it
- [[backend/frameworks/express/13-authorization|Authorization]] — `kitchen:watch` joins the policy table
- [[backend/frameworks/express/25-splitting-out-a-microservice|Splitting Out a Microservice]] — Redis Streams, which keep events instead of forgetting them

## About this lesson
<!-- bite: bf49fb07-6d75-404c-939c-dc0217e4a4d6 -->

**Level:** Intermediate → Advanced. Lesson 20 of [[backend/frameworks/express/index|Express]]. Covers polling, long polling, server-sent events and WebSockets and how to choose, the SSE wire format with `event`, `data`, `id`, `retry` and comment heartbeats, streaming from Express with `writeHead` and `write`, cleaning up on `close`, snapshot-then-changes so reconnects never miss anything, one-use stream tickets with `GETDEL` because `EventSource` can't send headers, Redis publish/subscribe for several servers with one subscription per server and in-memory fan-out, publishing from both the API and the worker, showing only what a public screen should, proxy, compression, rate-limit and shutdown concerns, a per-order customer stream, and testing streams and leaks.
