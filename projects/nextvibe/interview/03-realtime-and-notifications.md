# NextVibe — Realtime & Notifications

From [`../learning/backend/05-realtime.md`](../learning/backend/05-realtime.md) and
[`../learning/frontend/06-realtime.md`](../learning/frontend/06-realtime.md).

The richest realtime material in the vault — several race conditions with real root causes.

---

### Q1. [Intermediate] 🔥 ws, wss, and Socket.IO — what's the relationship?

**Strong answer covers:** **WebSocket** is the protocol: an HTTP request with an `Upgrade` header
that, once accepted, becomes a persistent bidirectional connection. `ws://` and `wss://` are its
plain and TLS schemes — `wss` is to `ws` what `https` is to `http`, and in production it's the only
acceptable one, not least because middleboxes routinely mangle plain `ws`.

**Socket.IO is not WebSocket.** It's a library *on top of* it that adds automatic reconnection with
backoff, named events, rooms, acknowledgements, namespaces, and a long-polling fallback when a
WebSocket can't be established. The consequence: a Socket.IO client cannot talk to a raw WebSocket
server, and vice versa — the handshake and framing are its own.

**The trade to name:** you get reconnection and rooms for free, and you're locked into the library on
both ends with a slightly heavier wire protocol.

---

### Q2. [Advanced] 🔥 How do you authenticate a WebSocket connection properly?

**Strong answer covers:** at the **handshake**, not per message. The client passes its token in the
connection auth payload; the gateway verifies it in the connection handler, attaches the resulting
user to the socket, and disconnects immediately if it's invalid. Every subsequent event is then
trusted to belong to that user, because the socket's identity was established once.

**The critical rule:** never take the user id from the **event payload**. A client that emits
`{ userId: someoneElse }` must not be believed — the identity lives on the socket, established from
a verified token. This is the socket version of "derive it server-side."

**Follow-ups worth having ready:** the token can expire mid-connection, so long-lived sockets need
either re-authentication or a bounded lifetime; and room membership must be authorised at join time
(`join:dm` for a conversation you're not part of must be rejected), otherwise rooms are a
free-for-all.

---

### Q3. [Advanced] 🔥 Why doesn't throwing inside a WebSocket handler behave like throwing in a controller?

**Strong answer covers:** there's no request/response pair to turn into a 400. An HTTP exception
filter maps a thrown error to a status code; a socket event has no status code and often no client
waiting on a reply, so a thrown error either vanishes into the gateway's error handling or kills the
connection — neither of which the client can interpret.

**What to do instead:** emit an explicit error **event** back to the socket (or use an
acknowledgement callback so the emitter gets a result), and treat "the operation failed" as a normal
message in the protocol rather than as an exception. Design the failure into the event vocabulary.

---

### Q4. [Advanced] 🔥🔥 Messages arrived sometimes and not others; the UI said "connected". Diagnose it.

**The best realtime bug in the project.**

**Strong answer covers the mechanism:** joining a room is an event the client must emit
(`join:dm`). The original code guarded that emit behind React state:

```ts
useEffect(() => {
  if (!isConnected) return;              // ← React state
  socket.emit("join:dm", { conversationId });
  socket.on("new:dm", handler);
  return () => socket.off("new:dm", handler);
}, [isConnected, status, conversationId, socketRef]);
```

On paper it's fine: `isConnected` flips true when the socket connects, the effect re-runs, the join
is emitted. **The problem is that the re-run has to travel through React's rendering pipeline** —
socket connects → `setStatus` → re-render → effect re-runs → emit. Meanwhile the socket is already
live and the server is already broadcasting. Any message in that window is missed, and on a
*reconnect* the socket may connect and disconnect faster than React re-renders at all — so the join
never happens and the user sits in a connected socket, in no room, receiving nothing.

**The fix:** bind to the socket's **own** lifecycle events rather than to derived React state —
subscribe to `connect` on the socket and emit the join there, so joining is driven by the socket's
event loop, not by a render. And re-join on every `connect`, because a reconnect is a *new* socket
session with no room membership.

**The generalisable lesson:** React state is a **lagging, lossy mirror** of an external event
source. When correctness depends on reacting to an external system's transition, subscribe to that
system's events directly — using rendered state as a trigger inserts a scheduler between the event
and your response.

---

### Q5. [Advanced] 🔥 Your own messages appear twice. Why, and how do you fix it without losing optimism?

**Strong answer covers the mechanism:** you add an optimistic bubble locally for instant feedback,
then the server saves the message and broadcasts `new:dm` **to everyone in the room including the
sender**, so the handler appends a second bubble. The database has one row; the UI has two.

**The fix — replace, don't append.** Track pending optimistic messages in a `Map` (keyed by body
text), assign the optimistic message a local id like `opt-${Date.now()}`, and when `new:dm` arrives
from yourself, look up the pending entry and **swap** the optimistic bubble for the real one rather
than appending.

**The weaknesses to volunteer, because an interviewer will probe:** keying by body text breaks if you
send the identical message twice in quick succession. The robust version is a **client-generated
id** sent with the message and echoed back by the server — then the match is exact. That's the
answer to "how would you improve it", and having it ready is what makes the whole answer land.

**The alternative design:** don't echo to the sender at all. Simpler, but then the sender's copy never
gets the server's canonical id or timestamp, which you need for editing, deletion and ordering.

---

### Q6. [Advanced] 🔥🔥 "Notifications don't show up." Where do you look first?

**Strong answer covers the framing before the fix:** a notification system has two halves that fail
independently —
- **the consumer side** (the table, the gateway that pushes over WebSocket, the frontend list, the
  socket listener) — the *plumbing*, which delivers whatever it's given;
- **the producer side** — the `notifications.create(...)` calls scattered across feature services
  that actually put something into the plumbing.

The instinct is to debug the socket. But the plumbing was fine: `toggleLike` and `addComment` wrote
their rows and returned, **never calling `notifications.create`**. The enum values existed, the page
worked, the gateway worked — the event was simply never *produced*.

**The diagnosis was one command:** `grep -rn "notifications\." src/modules/postcards` returned
**nothing** — the service didn't even inject `NotificationsService`.

**The lesson to state:** when an end-to-end pipeline is silent, find which *end* is broken before
poking the middle. A grep at each end is cheaper than any amount of socket debugging.

---

### Q7. [Intermediate] 🔥 Why does the self-notification guard live in `create()` rather than in each caller?

**Strong answer covers:** `NotificationsService.create()` starts with
`if (data.actorId && data.recipientId === data.actorId) return null;` — so callers can fire
notifications unconditionally (liking your own post, commenting on your own) and `create` quietly
no-ops. `toggleLike` just passes `recipientId: postcard.authorId, actorId: userId` with no `if`.

**The principle:** put a universal invariant in the **one place that can't be skipped**, not in every
call site that has to remember it. There are already several producers and there will be more; the
guard shouldn't be a thing each new one must know about.

---

### Q8. [Intermediate] 🔥 Every notification call ends in `.catch(() => null)`. Justify that.

**Strong answer covers:** a notification is a **side effect** of the real action — the like was
already saved. If the mail provider is down or the notification insert fails, the user's like must
still succeed. **Never let a best-effort side channel throw into the main flow.**

**The honest caveat to add:** swallowing the error entirely means a systematic failure (misconfigured
provider, broken migration) is invisible. The better form logs the failure while still not
propagating it — silence is the right *control flow* and the wrong *observability*.

---

### Q9. [Intermediate] What's the difference between an in-app notification and a transactional email here?

**Strong answer covers:** they answer different questions. In-app is ambient, high-volume, and
cheap — likes, comments, someone joined. Email is for things the user must know **when they're not
in the app**: a ticket purchase, a payment result, an event change. Sending every in-app event as an
email trains people to filter you; sending nothing by email means a purchase confirmation nobody
receives. So the split is by *consequence*, not by convenience — and the email versions carry rich
content because they may be the only record the user keeps.

---

### Q10. [Intermediate] The unread badge uses "pendingIds vs a counter." What's the distinction?

**Strong answer covers:** a bare counter can't be reconciled — increment on arrival, decrement on
read, and any missed event or double-fire leaves the number permanently wrong with no way to
recompute it. Tracking a **set of pending ids** means the badge is `size`, marking one read is a
delete, and a server refresh can replace the set wholesale. It's idempotent under duplicate events,
which is exactly what an at-least-once realtime channel gives you.

**The same principle appears elsewhere in the vault:** a ledger over a counter (Arete). Store the
things; derive the number.

---

### Q11. [Advanced] Per-conversation unread badges merge local and server state. Why is that hard?

**Strong answer covers:** the server knows what's been read across devices; the client knows what
just arrived over the socket a second ago and what the user is currently looking at. Neither alone is
right — server-only lags behind live events, client-only forgets on reload and disagrees across
devices. So the badge merges them, and the merge needs a rule for conflicts: locally-read beats
server-unread (the user *just* read it), server-unread beats local-absent (another device didn't read
it).

**The related trap:** the conversations list holds a cached list that a new message must update, or
the list shows a stale preview and no badge while the conversation itself shows the message. Any
cached collection that a realtime event mutates needs the event wired into the cache, not just into
the open view.

---

### Q12. [Intermediate] 🔥 Tab switching broke the socket listeners. What was the cause?

**Strong answer covers:** **effect dependencies.** An effect that subscribes to socket events and
returns an unsubscribe cleanup re-runs whenever its dependencies change. If a dependency is a value
recreated on each render (an inline object, a non-memoised callback), the effect tears down and
re-subscribes constantly — and on tab switch you get a window with no listener attached, so messages
arriving in that window are lost.

**The fix:** stabilise the dependencies (`useCallback`/`useRef` for handlers, primitives rather than
objects in the array), and keep the socket instance itself in a ref so it isn't recreated by
rendering at all. **A subscription's lifetime should be tied to what it's subscribing to, not to a
render.** Same underlying lesson as Q4.

---

### Q13. [Intermediate] Message order — why does prepend vs append matter in event chat?

**Strong answer covers:** history pagination loads *older* messages and must **prepend**; live
socket messages are *newer* and must **append**. Using one path for both puts history at the bottom
or new messages at the top. It also interacts with scroll: prepending shifts the viewport, so you
have to preserve scroll position when loading history, while appending should only auto-scroll if the
user was already at the bottom — otherwise you yank them away from what they're reading.

---

### Q14. [Beginner] You synthesised notification sounds with the Web Audio API rather than shipping an mp3. Why?

**Strong answer covers:** no asset to load, no request, no cache concern, and a few lines of
oscillator + gain envelope gives a clean short tone. It's a good fit for a UI blip specifically
because the sound is simple. The constraint to name: browsers block audio until a user gesture has
occurred, so the audio context must be created or resumed on a real interaction — otherwise the
first notification is silent and it looks like a bug.
