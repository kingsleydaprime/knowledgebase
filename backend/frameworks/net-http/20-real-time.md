---
id: 7454965e-3e03-431c-bbf9-97137f5bce43
---

# Real-time Updates

**Real-time updates mean the server tells the screen the moment something changes, instead of the screen asking again and again "anything new?".** The kitchen's tablet opens one connection and keeps it open; when Ada's payment lands, a small message travels down that connection and her order appears on the wall within a second. The standard, simplest way to do it over plain HTTP is called **server-sent events**.

## Before you start
<!-- bite: ad6c0656-a831-48b6-a93f-c44fafb39cfd -->

You should have:

1. Finished [[backend/frameworks/net-http/19-caching|lesson 19]], with both Redis servers running.
2. Met lesson 3's status recorder (and its `Unwrap` method), and lesson 1's server timeouts.

After this lesson you will be able to:

1. Choose between polling, server-sent events and WebSockets.
2. Write an SSE stream in Go: the format, flushing with `http.ResponseController`, heartbeats, and lifting the write timeout for this one response.
3. Keep every write to a `ResponseWriter` in one goroutine, with events arriving on a channel, and disconnect a screen that can't keep up.
4. Never miss an order: subscribe first, then send a snapshot, then changes.
5. Log a browser stream in with a one-use ticket, and reach every screen on every server with Redis pub/sub.

## Where we stopped
<!-- bite: 8067cfcc-39e2-4f95-99db-3da0f23fa4ef -->

The kitchen has a tablet on the wall showing open orders. It calls `GET /v2/orders?status=pending` when the cook taps refresh.

At 12:40, Ada pays. Her order is in the database, paid, ready to cook. And it sits there until someone wipes their hands and taps refresh. Maybe 30 seconds, maybe 3 minutes. Ada watches the clock.

The obvious fix, "refresh every 2 seconds by itself", is called polling. It works, but count it: one tablet, 30 requests a minute, 43,000 a day, nearly all answering "nothing new". Five branches, a "where's my order" screen on every phone... it adds up to most of your traffic, all saying nothing.

## The kid version
<!-- bite: d3c92264-05b7-4de1-a373-bdd6fbad2cd1 -->

Bayo is waiting for his food. He can walk up to the counter every minute and ask "is it ready?". Mama says "no" fifty times and gets annoyed.

Or Mama can say "sit down, I'll shout your name". Bayo sits. The moment it's ready, Mama shouts "Bayo!".

Asking every minute is polling. "I'll shout your name" is a server-sent event: Bayo keeps listening, and Mama speaks only when there's something to say.

**Where the picture stops working.** If Bayo steps outside to take a call, he misses the shout, and Mama doesn't shout twice. Our screens will step outside too (Wi-Fi drops), so when they come back, they must be able to find out what they missed.

## Terms used in this lesson
<!-- bite: c9e2f9ac-9b1e-4c34-8c31-6472a02d294a -->

1. **Polling**: This is the client asking again on a timer, "anything new?". Simple, wasteful.
2. **Server-sent events**: This is also written **SSE**. It's one long HTTP response that the server keeps writing small text events into. One direction: server to client.
3. **WebSocket**: This is a two-way connection that starts as HTTP and then switches to its own protocol. Both sides can send at any time.
4. **`EventSource`**: This is the browser's built-in SSE client. It connects, reads events, and reconnects by itself if the connection drops.
5. **Flush**: This means pushing what's been written so far out to the client now, instead of waiting for more.
6. **Heartbeat**: This is a tiny message sent every so often just to keep the connection alive, so proxies don't close it for being quiet.
7. **Publish/subscribe**: This is also written **pub/sub**. Publishers send messages to a named channel, and every subscriber to that channel receives them. Redis has it built in.
8. **Fan-out**: This is one event being sent to many listeners.
9. **Snapshot**: This is the full current state (every open order), sent first, so a screen that missed events still ends up right.

## Step 1: choosing
<!-- bite: acbb5343-b91e-47ce-ac90-1166f771488f -->

| | Direction | Works through ordinary HTTP | Reconnects by itself | Good for |
|---|---|---|---|---|
| Polling | client asks | yes | not needed | rare checks ("every 5 minutes") |
| **SSE** | server → client | **yes** | **yes** (`EventSource`) | feeds, dashboards, notifications, "your order is ready" |
| WebSocket | both ways | needs an upgrade | you write it | chat, games, editing together |

The kitchen screen only *listens*. When a cook taps "ready", that's a normal `PATCH` request, which we already have. So the stream is one-way: server to screen. That's exactly what SSE is for.

SSE is also just HTTP. Our middleware, logging, proxies and HTTPS all work on it unchanged, and Go's standard library is all it needs. A WebSocket switches away from HTTP after the first request, so middleware stops applying, proxies need extra setup, and Go needs a package for it (`github.com/coder/websocket` is the usual choice). Choose WebSockets when you really need both directions at high speed: Ada chatting with her rider, say.

## Step 2: what an SSE response looks like
<!-- bite: 1c8f0f84-95be-4632-82f9-99cbd1c92673 -->

An SSE response is plain text, with a special content type, and it doesn't end:

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-store

retry: 3000

event: snapshot
data: [{"id":"41","dish":"Jollof rice","quantity":1,"paidAt":"2026-11-23T12:38:51Z","name":"Bayo"}]

: ping

id: 1795950003123-4f2a
event: order.paid
data: {"id":"42","dish":"Jollof rice","quantity":2,"paidAt":"2026-11-23T12:40:03Z","name":"Ada"}

```

Each event is a few lines, ended by a **blank line**:

1. **`event:`** names the kind of event. The browser can listen for each name separately.
2. **`data:`** is the content. We send JSON on one line.
3. **`id:`** is the event's ID. If the connection drops, `EventSource` reconnects and sends the last ID it saw in a `Last-Event-ID` header.
4. **`retry:`** tells the browser how many milliseconds to wait before reconnecting.
5. A line starting with **`:`** is a comment. The browser ignores it, which makes it the perfect heartbeat.

`json.Marshal` never writes a raw newline in its output (a newline inside a string becomes `\n`), so the `data:` is always one line, which keeps the format safe. If you ever send plain text, each of its lines needs its own `data:` prefix, or one newline in a dish name breaks the stream.

## Step 3: a stream in Go
<!-- bite: 1099595c-dcf3-4517-84d9-ae7ea511945e -->

`internal/sse/sse.go`, a small helper that knows the format:

```go
// Package sse writes server-sent events.
package sse

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type Stream struct {
	w  http.ResponseWriter
	rc *http.ResponseController
}

// Open starts an event stream. After this, only the calling goroutine may use it.
func Open(w http.ResponseWriter) (*Stream, error) {
	rc := http.NewResponseController(w)
	// The server's WriteTimeout (lesson 1) would end this response after 30 s. Lift it, for this one.
	if err := rc.SetWriteDeadline(time.Time{}); err != nil {
		return nil, fmt.Errorf("stream: can't lift write deadline: %w", err)
	}

	h := w.Header()
	h.Set("Content-Type", "text/event-stream")
	h.Set("Cache-Control", "no-store")
	h.Set("X-Accel-Buffering", "no") // tells nginx-style proxies not to hold events back
	w.WriteHeader(http.StatusOK)

	s := &Stream{w: w, rc: rc}
	io.WriteString(w, "retry: 3000\n\n")
	return s, s.flush()
}

func (s *Stream) Send(event string, data any, id string) error {
	b, err := json.Marshal(data)
	if err != nil {
		return err
	}
	if id != "" {
		fmt.Fprintf(s.w, "id: %s\n", id)
	}
	fmt.Fprintf(s.w, "event: %s\ndata: %s\n\n", event, b)
	return s.flush()
}

func (s *Stream) Ping() error {
	io.WriteString(s.w, ": ping\n\n")
	return s.flush()
}

func (s *Stream) flush() error { return s.rc.Flush() }
```

Three Go details do the real work here.

**1. Flushing.** Go's server collects what you write in a buffer and sends it in large pieces, which is efficient for normal responses. For a stream, an event sitting in a buffer is an event the kitchen doesn't see. `Flush` pushes it out now. `http.ResponseController` (Go 1.20) is the modern way to reach the flush, and every write is followed by one.

**2. Lifting the write deadline.** Lesson 1 gave the server `WriteTimeout: 30 * time.Second`, a promise that no response takes longer than 30 seconds to write. A stream *is* a response that takes hours. Without `SetWriteDeadline(time.Time{})` (the zero time means "no deadline"), every kitchen screen would be cut off after 30 seconds, reconnect, and be cut off again. The `ResponseController` changes the deadline **for this one connection**, so every other route keeps its protection. That's much better than raising the server-wide timeout for everyone because one route needs it.

**3. It works through our middleware because of `Unwrap`.** The `w` our handler gets isn't the server's own writer: lesson 3's status recorder is wrapped around it, so the logger can see the status. A wrapper doesn't have `Flush` or `SetWriteDeadline` itself. `NewResponseController` looks for an `Unwrap() http.ResponseWriter` method and follows it down to the real writer underneath. Lesson 3 added `Unwrap` for exactly this day. (Lesson 7's `MuxProblems` wrapper has no `Unwrap`, and doesn't need one: it only wraps the writer when *no* route matched, so a stream's request passes it untouched.) A wrapper without it would make `Flush` fail with `http.ErrNotSupported`, which is why `Open` checks the error and refuses to start a stream it can't flush.

(One wrapper must never be on a stream route: lesson 15's idempotency middleware, which collects the whole answer before sending any of it. A stream never finishes, so nothing would ever be sent. Lesson 15 warned about this.)

## Step 4: one goroutine writes; everyone else sends on a channel
<!-- bite: 3971ffeb-6a31-4bb1-8dbe-b0e3be3f66a4 -->

An `http.ResponseWriter` is **not safe to use from more than one goroutine**. Events will come from Redis, on another goroutine; the heartbeat comes from a ticker. If each wrote to `w` directly, two writes could interleave and the browser would get half an event glued to half a ping.

The Go answer: the handler's own goroutine is the **only** one that writes. Everything else sends to it on a channel, and the handler loops, waiting on all of them at once with `select`. `internal/kitchen/stream.go`:

```go
func (h *Handler) stream(w http.ResponseWriter, r *http.Request) error {
	who, err := auth.Current(r.Context())
	if err != nil {
		return err
	}

	// 1. Listen first, so nothing that happens from now on is missed.
	events, unsubscribe := h.hub.Subscribe()
	defer unsubscribe()

	// 2. Then read the whole truth.
	open, err := h.orders.OpenForKitchen(r.Context(), who)
	if err != nil {
		return err // nothing written yet, so a normal problem response still works
	}

	s, err := sse.Open(w)
	if err != nil {
		return err
	}
	if err := s.Send("snapshot", presentAll(open), ""); err != nil {
		return nil
	}

	// 3. Then every change, as it happens, until the screen goes away.
	heartbeat := time.NewTicker(25 * time.Second)
	defer heartbeat.Stop()
	for {
		select {
		case <-r.Context().Done():
			return nil // the tablet went away
		case e, ok := <-events:
			if !ok {
				return nil // the hub dropped us for being slow; the screen will reconnect
			}
			if err := s.Send(e.Type, e.Data, e.ID); err != nil {
				return nil
			}
		case <-heartbeat.C:
			if err := s.Ping(); err != nil {
				return nil
			}
		}
	}
}
```

Read the `select` as "whichever happens first":

1. **`r.Context().Done()`** closes when the client goes away: the tab closes, the Wi-Fi drops, the cook pulls the plug. Go cancels a request's context the moment its connection closes. We return, and the `defer`s run: `unsubscribe()` and `heartbeat.Stop()`. **Every open has a close**, and `defer` makes it impossible to forget. Without it, every disconnected screen would leave a subscription behind, still being sent events nobody reads, and after a few days of tablets coming and going the server would run out of memory.
2. **An event** arrives from the hub: send it.
3. **The heartbeat** every 25 seconds. Proxies and load balancers close connections that have been quiet for a while (often 60 seconds). A quiet kitchen at 3pm would be cut off again and again; a comment line every 25 seconds keeps it awake.

When a write fails, we just return `nil`. The client is gone; there's nobody to send a problem response to, and the headers were sent long ago anyway. Once a stream has started, errors can only end it.

Notice the order of 1, 2 and 3, which is the next step.

## Step 5: never miss an order
<!-- bite: ce514c92-273f-4962-ad58-5059c14718d3 -->

The tablet's Wi-Fi drops for 20 seconds. In that time, two orders are paid. `EventSource` reconnects. Did the kitchen miss them?

Redis pub/sub (step 7) doesn't store messages: if you weren't listening when one was sent, it's gone. So every connection, including every reconnection, starts with a **snapshot**: the full list of open, paid orders, straight from Postgres. The screen throws away what it had and draws the snapshot. The two missed orders are in it. Nothing is lost, and we didn't need to keep every event in a replay log.

And there's a gap to close. If we read the snapshot first and subscribed second, an order paid in the instant between would be in neither. So the handler **subscribes first**. Any event in that instant waits in the subscription's channel while the snapshot is read and sent, and then it's sent right after. The screen may get an `order.paid` for an order that's already in the snapshot, so it must handle every event as "put this card in, replacing any with the same ID", never "add another card". Handling a duplicate is cheap; preventing one perfectly is not.

What about `Last-Event-ID`? A system that keeps every event (Redis Streams can, and we'll meet them in lesson 25) can use it to send just what was missed. For a kitchen with maybe 30 open orders, a fresh snapshot is simpler and always right.

`OpenForKitchen` is a new orders service method: open, paid orders, oldest first, limited to 200, and only for an actor who may watch the kitchen. A new action in lesson 13's policy, `kitchen:watch`, for staff and admins, with its row in `TestPermissions`.

## Step 6: the hub, and screens that can't keep up
<!-- bite: 525b2cc7-714b-4b05-8aa7-783b47c35252 -->

The hub keeps the list of who's listening on this server. `internal/kitchen/hub.go`:

```go
type Event struct {
	ID   string `json:"id"`
	Type string `json:"type"` // "order.paid", "order.status"
	Data any    `json:"data"`
}

// Hub passes events to every screen connected to this server.
type Hub struct {
	mu        sync.Mutex
	listeners map[chan Event]struct{}
	connected atomic.Int64
}

func NewHub() *Hub { return &Hub{listeners: map[chan Event]struct{}{}} }

func (h *Hub) Subscribe() (<-chan Event, func()) {
	ch := make(chan Event, 32)
	h.mu.Lock()
	h.listeners[ch] = struct{}{}
	h.mu.Unlock()
	h.connected.Add(1)

	var once sync.Once
	return ch, func() {
		once.Do(func() {
			h.mu.Lock()
			if _, ok := h.listeners[ch]; ok {
				delete(h.listeners, ch)
				close(ch)
			}
			h.mu.Unlock()
			h.connected.Add(-1)
		})
	}
}

// Deliver sends an event to every listener. A listener whose channel is full is
// too slow: it's dropped, and its screen reconnects and gets a fresh snapshot.
func (h *Hub) Deliver(e Event) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for ch := range h.listeners {
		select {
		case ch <- e:
		default:
			delete(h.listeners, ch)
			close(ch)
		}
	}
}

func (h *Hub) Connected() int64 { return h.connected.Load() }
```

The interesting line is the `select` with a `default`. `ch <- e` would normally **wait** until there's room in the channel. With `default`, if there's no room *right now*, it takes the `default` branch instead of waiting. So `Deliver` never blocks.

Why it matters: picture one tablet on terrible Wi-Fi, its events piling up because they can't be written fast enough. If `Deliver` waited for that tablet, every other screen on the server would wait too, and one bad connection would freeze the whole kitchen feed. Instead, each listener has room for 32 waiting events. A screen that falls 32 behind is **dropped**: its channel is closed, the handler's `case e, ok := <-events` sees `ok == false` and returns, the connection ends, and `EventSource` reconnects in 3 seconds and gets a fresh snapshot. A slow screen loses nothing in the end, and nobody else waits for it.

Two smaller details:

1. **`map[chan Event]struct{}`** is a set of channels. Channels can be map keys, and `struct{}` takes no memory, so this is the standard Go way to write "a set of things".
2. **`sync.Once` in the unsubscribe function** makes it safe to call twice, and safe to call after the hub has already dropped and closed the channel. Closing a channel twice panics; the `if _, ok` check and the `Once` make sure it only ever happens once. `connected` counts open streams, for lesson 27 to graph: a line that only goes up is a leak.

## Step 7: more than one server
<!-- bite: 79a7d5c5-1c9c-4a2f-b29f-0a7617a45a92 -->

So far, the hub knows only its own server's screens. Now think about two servers behind a load balancer:

1. The kitchen tablet is connected to **server A**.
2. Paystack's webhook for Ada's payment lands on **server B**.
3. Server B marks the order paid and tells *its* hub. It has no screens. The tablet, on A, hears nothing.

Each server only knows its own connections. So the news must go through something they all share, and that's Redis **pub/sub**: B **publishes** "order 42 paid" to a channel; A and B both **subscribe** to that channel; each passes it to its own hub. `internal/kitchen/events.go`:

```go
const channel = "kitchen"

// Events publishes kitchen events to Redis, and feeds everything published (by any server) into hub.
type Events struct {
	rdb *redis.Client
	hub *Hub
	log *slog.Logger
}

func NewEvents(rdb *redis.Client, hub *Hub, log *slog.Logger) *Events {
	return &Events{rdb: rdb, hub: hub, log: log}
}

func (e *Events) Publish(ctx context.Context, typ string, data any) error {
	b, err := json.Marshal(Event{ID: newEventID(), Type: typ, Data: data})
	if err != nil {
		return err
	}
	return e.rdb.Publish(ctx, channel, b).Err()
}

// Listen runs until ctx is cancelled. Start it once per server, in its own goroutine.
func (e *Events) Listen(ctx context.Context) {
	sub := e.rdb.Subscribe(ctx, channel)
	defer sub.Close()
	for {
		select {
		case <-ctx.Done():
			return
		case msg, ok := <-sub.Channel():
			if !ok {
				return
			}
			var ev Event
			if err := json.Unmarshal([]byte(msg.Payload), &ev); err != nil {
				e.log.Warn("bad kitchen event", "error", err)
				continue
			}
			e.hub.Deliver(ev)
		}
	}
}

func newEventID() string {
	return strconv.FormatInt(time.Now().UnixMilli(), 10) + "-" + rand.Text()[:4]
}
```

The design keeps Redis connections fixed: **one** subscription per server, however many screens are watching. Each screen is just a channel in the hub. A hundred screens don't mean a hundred Redis connections.

go-redis's `Subscribe` holds a connection of its own, because once a Redis connection subscribes, it can only receive messages. `sub.Channel()` is a Go channel that go-redis fills from a goroutine of its own, and it **reconnects and re-subscribes by itself** if the connection drops. (Messages published while it was disconnected are lost, which is exactly why step 5's snapshot exists.)

The `data` arrives as JSON and is decoded into `any`, so it becomes a `map[string]any`. That's fine: the stream only encodes it again, unchanged.

Which Redis? Pub/sub messages aren't stored, so eviction doesn't matter, but use the **queue** Redis anyway: the cache Redis is allowed to go down without harm (lesson 19), and the kitchen feed shouldn't.

In `run`:

```go
hub := kitchen.NewHub()
events := kitchen.NewEvents(queueRedis, hub, logger)
go events.Listen(ctx)
```

**Publishing.** In the payments service, where `Settle` gets `Paid`, through a small `Kitchen` interface declared in `payments`:

```go
if outcome == Paid {
	// ... queue the receipt, as in lesson 18
	if err := s.kitchen.OrderPaid(ctx, p.OrderID); err != nil {
		s.log.Warn("kitchen not told about payment", "order", p.OrderID, "error", err)
	}
}
```

and in the orders service after a status change, `OrderStatus(ctx, id, status)`. Both end in `events.Publish`. `Settle` also runs in the worker (lesson 18's hourly check), and that's fine: the worker publishes to the same Redis channel, and every API server passes it on. Anything that can publish to Redis can reach the kitchen.

If the publish fails, the order is still paid; the kitchen just doesn't hear about it until its next snapshot. That's why the snapshot matters: **the live feed is a convenience on top of the truth, never the truth itself.** (For extra safety, the screen can reconnect every few minutes on purpose, which gets a fresh snapshot.)

The kitchen's view of an order sends what the kitchen needs (order ID, dish name, quantity, when it was paid, the customer's first name for calling out) and nothing else. No phone numbers on a tablet hanging on a wall that anyone in the shop can read.

## Step 8: logging in a browser stream
<!-- bite: a3f07ff6-1005-4f6c-9122-ec5af88932ff -->

Here's a snag. Every route uses `Authorization: Bearer <token>`. The browser's `EventSource` **can't send custom headers**. Its only option is `new EventSource(url)`.

Three ways out:

1. **Put the access token in the URL**: `?token=eyJ...`. Don't. URLs end up in server logs, proxy logs and browser history, and the token is a 15-minute key to the account.
2. **Use a fetch-based SSE client** in the browser, which can send headers. It works, and some teams prefer it. You lose `EventSource`'s built-in reconnection unless the library rebuilds it.
3. **A short-lived, one-use stream ticket.** The screen asks for a ticket with its normal token, then opens the stream with the ticket.

We'll do 3, because it keeps `EventSource` and keeps tokens out of URLs. `internal/kitchen/tickets.go`:

```go
const ticketTTL = 30 * time.Second

type Tickets struct{ rdb *redis.Client }

func (t *Tickets) Issue(ctx context.Context, who auth.Identity) (string, error) {
	ticket := rand.Text()
	b, _ := json.Marshal(who)
	if err := t.rdb.Set(ctx, "ticket:"+ticket, b, ticketTTL).Err(); err != nil {
		return "", err
	}
	return ticket, nil
}

var ErrBadTicket = apperr.New(apperr.Unauthenticated, "bad-stream-ticket", "Ask for a new stream ticket.")

// RequireTicket turns a one-use ?ticket= into the caller's identity.
func (t *Tickets) RequireTicket(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ticket := r.URL.Query().Get("ticket")
		b, err := t.rdb.GetDel(r.Context(), "ticket:"+ticket).Bytes()
		var who auth.Identity
		if ticket == "" || err != nil || json.Unmarshal(b, &who) != nil {
			httpx.WriteError(w, r, ErrBadTicket)
			return
		}
		next.ServeHTTP(w, r.WithContext(auth.WithIdentity(r.Context(), who)))
	})
}
```

and the routes, in the kitchen `Register`:

```go
mux.Handle("POST /v2/kitchen/stream-tickets",
	auth.RequirePermission(auth.KitchenWatch)(httpx.HandlerFunc(h.issueTicket)))
mux.Handle("GET /v2/kitchen/orders/stream",
	h.tickets.RequireTicket(auth.RequirePermission(auth.KitchenWatch)(httpx.HandlerFunc(h.stream))))
```

The ticket is still in a URL, so it might be logged, but look at what it's worth to anyone who finds it: it worked for 30 seconds, and only once. **`GETDEL`** reads and deletes in one command, so two requests can't both use it. The identity it carries is the one the access token proved, and `RequirePermission` checks it again on the stream. Store tickets in the **queue** Redis, the one that doesn't evict. And rate-limit the ticket route like login, so nobody can make thousands of them.

(`auth.Identity` has no `json` tags, so it's stored as `{"UserID":3,"Role":"staff"}`. It's our own internal copy, read back by our own code, so Go's field names are fine.)

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

`upsertCard` is step 5's rule in code: put the card in, replacing any with the same ID.

Try it from the terminal. `curl -N` turns off curl's own buffering, so events print as they arrive:

```bash
TICKET=$(curl -s -X POST localhost:8080/v2/kitchen/stream-tickets -H "Authorization: Bearer $STAFF" \
  | grep -o '"ticket":"[^"]*"' | cut -d'"' -f4)
curl -N "localhost:8080/v2/kitchen/orders/stream?ticket=$TICKET"
```

You'll see `retry: 3000` and the snapshot. In another terminal, pay for an order (send the signed webhook from lesson 17), and watch `order.paid` appear in the first. Run the same `curl` again with the same ticket: 401. Okay!!!!! The kitchen is live.

## Step 9: the rest of the app
<!-- bite: b25221c0-0102-4170-8969-f1b1358e4543 -->

A stream holds a connection open for hours. A few things to check:

1. **Timeouts.** `ReadTimeout` and `ReadHeaderTimeout` only limit how long the *request* takes to arrive. A GET has no body, so it arrives at once, and the long *response* is fine once `Open` has lifted the write deadline. A proxy in front may have its own response timeout; the heartbeat keeps most happy, and lesson 28 sets the proxy up properly.
2. **Compression.** Go's server doesn't compress responses by itself. If you ever add compression middleware, it buffers output to compress it, and events get held back: skip it for `text/event-stream`, or let the proxy compress.
3. **Connection count.** Each open stream is one socket and one goroutine. Go is happy with tens of thousands of both. `hub.Connected()` is the number to watch; lesson 27 graphs it.
4. **Shutting down.** When the server stops, `http.Server.Shutdown` waits for active requests to finish, and a stream never finishes by itself, so it would wait until its deadline. Lesson 28 uses `srv.RegisterOnShutdown` to tell every stream "end now", so screens reconnect to a healthy server straight away.

## Step 10: a stream for customers too
<!-- bite: 5f895a58-084b-41a4-93ab-f6fa9b1e63b0 -->

Ada would like to see "Your order is being cooked... Ready!" on her phone. Same building blocks:

1. `GET /v2/orders/{id}/stream`, with a ticket from `POST /v2/orders/{id}/stream-tickets`. Issuing the ticket calls `orders.Service.Get(ctx, actor, id)`, so lesson 13's ownership check runs: Ada can only watch her own order, and someone else's is a 404.
2. A snapshot first (the order's current status), then `order.status` events **for that order only**: the handler's loop skips events whose ID isn't this order's.
3. The server ends the stream itself when the order is `collected`. There's nothing more to say.

Filtering by order ID on each server is fine at Mama Put's size. A very large system would use a Redis channel per order (`order:42`) instead, so each server only receives what its listeners care about.

## Step 11: testing
<!-- bite: 73bb5979-2c39-4304-8f1a-e00761a411b1 -->

1. **The format** is a pure function of what's written: give `sse.Open` an `httptest.NewRecorder()`, `Send("order.paid", map[string]string{"id": "42"}, "1")`, and check the body ends with exactly `id: 1\nevent: order.paid\ndata: {"id":"42"}\n\n`. (`httptest.ResponseRecorder` supports `Flush`, and its `SetWriteDeadline` returns `ErrNotSupported`, so make `Open` tolerate that one error in tests, or test `Send` on a `Stream` built directly.)
2. **The hub**, with no Redis: subscribe, deliver, receive. Then the slow-screen test: subscribe and never read, deliver 33 events, and check the channel was closed and `Connected()` went down.
3. **The route**, through a real server. A recorder can't show events arriving over time, so use `httptest.NewServer(a.Handler)`, `http.Get` the stream URL with a ticket, and read it line by line with a `bufio.Scanner`: first `retry: 3000`, then the snapshot. Then publish through the hub, and check the event arrives. Then close the response body, and check `hub.Connected()` drops back to zero: the leak test.
4. **Tickets**: a ticket works once; the second use is 401; a customer's ticket can't open the kitchen stream (403); an expired ticket is 401 (use a 1-millisecond TTL in the test).

## The Go in this lesson
<!-- bite: 69d3556f-d440-403c-9b10-7d3e0526fbfb -->

1. **`http.NewResponseController(w)`** (Go 1.20): Reaches features of the real connection through any wrappers that have `Unwrap`. `Flush` sends buffered output now; `SetWriteDeadline` changes the write timeout for this response only.
2. **`time.Time{}`**: The zero time. As a deadline, it means "none".
3. **`Unwrap() http.ResponseWriter`** on a wrapper: The convention that lets `ResponseController` find the writer underneath. Write it on every `ResponseWriter` wrapper you make.
4. **One writer goroutine, many senders**: A `ResponseWriter` isn't safe for concurrent use, so other goroutines send on channels and only the handler writes.
5. **`select` with several cases**: Waits for whichever channel is ready first: cancellation, an event, or a tick.
6. **`e, ok := <-ch`**: `ok` is `false` once the channel is closed and empty. That's how a receiver learns "no more".
7. **`select` with `default`**: A send (or receive) that doesn't wait: if it can't happen right now, `default` runs instead.
8. **`map[chan Event]struct{}`**: A set, with channels as keys.
9. **`close(ch)`**: Tells receivers there will be no more values. Only the sender should close a channel, and only once; closing twice panics.
10. **`sync.Once`**: Runs a function at most once, however many times `Do` is called, from however many goroutines.
11. **`atomic.Int64`**: A number many goroutines can add to and read without a mutex.
12. **`rdb.Subscribe(ctx, channel)`** and **`sub.Channel()`**: go-redis's pub/sub. The Go channel delivers `*redis.Message` values; the client reconnects by itself.
13. **`rdb.GetDel(ctx, key)`**: Redis's `GETDEL`: read a key and delete it in one step, so it can only ever be read once.
14. **`curl -N`**: Not Go, but you'll use it: no buffering, so a stream prints as it arrives.

## Your project so far
<!-- bite: 7971834a-4866-4dc6-bd04-c9f3b667905e -->

```text
mama-put/
├── cmd/
│   └── api/main.go                ← hub, kitchen events (Listen goroutine), tickets
└── internal/
    ├── sse/
    │   └── sse.go                 ← NEW: Open (flush, lifted write deadline), Send, Ping
    ├── kitchen/                   ← NEW package
    │   ├── hub.go                 ← Subscribe (buffered, safe to unsubscribe twice), Deliver (drops slow screens)
    │   ├── events.go              ← Publish and Listen on Redis pub/sub
    │   ├── tickets.go             ← Issue, RequireTicket (GETDEL, 30 s)
    │   ├── stream.go              ← subscribe, snapshot, then select on done/events/heartbeat
    │   └── handlers.go            ← POST stream-tickets, GET orders/stream
    ├── auth/
    │   └── policy.go              ← kitchen:watch
    ├── orders/
    │   ├── service.go             ← OpenForKitchen; status changes tell the kitchen
    │   └── handlers.go            ← the customer's own-order stream
    └── payments/
        └── service.go             ← Settle tells the kitchen on Paid
```

## Common mistakes
<!-- bite: 26738310-4c70-4c0e-a497-db5358e8b897 -->

1. **Polling every few seconds "for now".** It becomes most of your traffic. Stream.
2. **Forgetting to flush.** Events sit in Go's buffer and arrive in clumps, or not at all.
3. **Raising the server's `WriteTimeout` for everyone because streams need it.** Lift it per stream with `SetWriteDeadline`.
4. **A `ResponseWriter` wrapper without `Unwrap`.** Flushing fails through it.
5. **Writing to `w` from more than one goroutine.** Events and pings interleave. One writer; everyone else sends on a channel.
6. **No cleanup when the client leaves.** Subscriptions pile up until memory runs out. `defer unsubscribe()` and watch `r.Context().Done()`.
7. **A blocking send to each screen.** One slow tablet freezes everyone. Buffer, and drop the slow.
8. **Trusting the live feed alone.** Pub/sub forgets. Start every connection with a snapshot, and subscribe before reading it.
9. **Access tokens in stream URLs.** Use a one-use, short ticket.
10. **No heartbeat.** Proxies close quiet connections.
11. **Personal details on a shared screen.** First names, not phone numbers.
12. **The idempotency middleware on a stream.** It waits for an end that never comes.

## Check your understanding
<!-- bite: fbe64af7-bcba-4d5c-939d-5d72b5fd8fde -->

1. Why SSE and not WebSockets for the kitchen screen?
2. What would happen to every kitchen screen without `rc.SetWriteDeadline(time.Time{})`, and why is that better than raising the server's `WriteTimeout`?
3. Why does the handler subscribe to the hub *before* reading the snapshot?
4. One tablet's Wi-Fi is so bad that it can't take events as fast as they come. What happens to it, and to the other screens?
5. The kitchen tablet is on server A; Paystack's webhook lands on server B. Follow the event from B to the tablet.
6. Why can't the stream use the access token like every other route, and why is a ticket in the URL acceptable when a token isn't?

<details>
<summary>Answers, after your attempt</summary>

1. The screen only listens; anything it does (marking an order ready) is an ordinary request. SSE is one-way, is plain HTTP so all our middleware and proxies work, needs nothing beyond the standard library, and `EventSource` reconnects by itself.
2. The server would end each stream after 30 seconds of writing, so every screen would disconnect, reconnect and disconnect again. Lifting the deadline for the stream's own connection leaves every other route with its 30-second protection; raising it for the whole server would take that protection away from everything.
3. So nothing falls into the gap. Events from the moment of subscribing wait in the channel while the snapshot is read; anything that happens before the subscription is in the snapshot. The worst case is an event for an order already in the snapshot, which the screen handles by replacing the card.
4. Its channel fills up (32 waiting events). `Deliver` can't send without waiting, so it takes the `default` branch: it removes and closes that channel. The handler sees the channel closed and ends the stream; the tablet reconnects and gets a fresh snapshot. The other screens never wait for it, because `Deliver` never blocks.
5. Server B's `Settle` gets `Paid` and publishes `order.paid` to the `kitchen` channel in Redis. Both servers' `Listen` goroutines receive it from their subscriptions; each calls its own hub's `Deliver`. Server A's hub sends it on the tablet's channel; the tablet's handler goroutine receives it in its `select`, writes it with `Send`, and flushes.
6. Because `EventSource` can't send headers. A token in a URL would be written into logs and history while it's still a 15-minute key to the account. A ticket works only once and only for 30 seconds, so by the time anyone reads it in a log, it's worthless.

</details>

## Practice
<!-- bite: 9f3c857f-c877-47fb-b7ab-b55f52a50100 -->

1. Write the hub tests from step 11, including the slow-screen test and the double-unsubscribe test.
2. Write the stream test through `httptest.NewServer`: the snapshot arrives, a delivered event arrives, and closing the body brings `Connected()` back to zero.
3. Build the customer stream from step 10, and make it end the stream from the server when the order is `collected`.
4. Make the kitchen screen reconnect on purpose every 10 minutes (the server can end the stream after 10 minutes, and `EventSource` reconnects), so even a missed publish is fixed by a fresh snapshot within 10 minutes.
5. Add `GET /v2/admin/streams` for admins, returning `hub.Connected()` for this server.

**Done when** a payment made with lesson 17's signed webhook appears on a `curl -N` kitchen stream within a second; the stream survives longer than 30 seconds (watch the pings); two API servers on different ports both deliver an event published by either; a used ticket gets 401; closing the stream leaves `Connected()` at zero; and `make test` passes.

## Before moving on
<!-- bite: a4244e59-0f75-476c-b020-0fd9419e6b1d -->

Mama Put API now talks first. The kitchen sees each paid order the moment it lands, on every server, through flaky Wi-Fi, with a snapshot so nothing is ever missed, a heartbeat so proxies leave it alone, and a hub that never lets one slow tablet freeze the rest. Ada can watch her own order cook.

That's the end of Part 4: payments, jobs, caching and real-time updates, the things real products need. Part 5 is about other ways to talk to the same app. The phone team says the menu screen makes four requests to draw one page (dishes, their photos, today's specials, the customer's last order) and asks: could they ask for exactly what the screen needs, in one request? That's GraphQL, the next lesson.

## Related
<!-- bite: 43e797f9-1c6d-4aca-9e94-7e7f19933641 -->

- [[backend/frameworks/net-http/21-graphql|Next: GraphQL]]
- [[backend/frameworks/express/20-real-time|The same lesson in Express]] — `res.write`, ioredis pub/sub, and `req.on("close")`
- [[backend/frameworks/net-http/03-middleware|Middleware]] — where the status recorder got its `Unwrap`

## About this lesson
<!-- bite: be293f68-a012-4b15-aaf8-ae52ae0ca863 -->

**Level:** Advanced. Lesson 20 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`http.ResponseController` needs 1.20), go-redis v9 and Redis 7. Covers polling, SSE and WebSockets, the SSE format, flushing and per-response write deadlines with `ResponseController`, one writer goroutine with `select` over cancellation, events and heartbeats, a hub that drops slow listeners with non-blocking sends, subscribe-then-snapshot, Redis pub/sub across servers, one-use stream tickets with `GETDEL`, and testing streams through a real test server.
