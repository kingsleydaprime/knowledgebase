# NextVibe Frontend — Real-Time: Socket.IO, Chat UI & Notification Badges

Split out from the original flat `frontend-learning.md` (kept untouched in the project root).
See also `learning/frontend-auth.md` (the cookie/token plumbing this system's `auth: { token }`
handshake depends on), `learning/frontend-state-management.md` (RTK Query cache that the socket
handlers refetch into), `learning/frontend-routing.md`, `learning/frontend-forms-ui.md`, and —
for the backend half of this exact real-time system (gateway JWT verification, namespaces,
rooms, the Messaging and Notifications modules) — `learning/backend-realtime.md` and
`learning/backend-modules.md`.

This file covers: the `useSocket` hook and why Socket.IO is used instead of raw WebSocket; the
event-driven join pattern that fixes a real React-vs-socket.io race condition; a cookie-expiry
bug that silently killed socket auth; optimistic message deduplication; chat UI patterns (grouped
bubbles, `min-h-0` for scrollable flex children, full-screen escape from layout chrome);
synthesised notification sounds via the Web Audio API; the notification badge double-count fix;
WebSockets from first principles (`ws`/`wss`, the Socket.IO handshake, namespaces vs rooms); the
conversations list stale-cache fix; per-conversation and bottom-nav unread badges; event chat
message ordering (prepend vs append); and the effect-dependency rule for socket handlers that
must re-join a different room when a tab changes.

---

## 12. Real-Time with Socket.IO

The backend exposes two Socket.IO namespaces:

| Namespace | Purpose |
|---|---|
| `/messaging` | DM conversations + event chat rooms |
| `/notifications` | Per-user real-time notifications |

### Why Socket.IO, not raw WebSocket?

Socket.IO adds on top of WebSocket:
- Automatic reconnection
- Room management (server-side groups)
- Named events (`.emit("join:dm", data)` vs parsing JSON manually)
- Fallback to HTTP long-polling if WebSocket is blocked

The earlier implementation used native `WebSocket` with JSON-wrapped events — this was fundamentally wrong for a Socket.IO backend. (See section 42 below for the full first-principles comparison of raw WebSocket vs Socket.IO.)

### The `useSocket` hook

```ts
// src/hooks/useSocket.ts
export function useSocket(namespace: "messaging" | "notifications", { enabled = true } = {}) {
  const [status, setStatus] = useState<SocketStatus>("disconnected");
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!enabled) return;
    const token = Cookies.get("accessToken");
    if (!token) { setStatus("error"); return; }

    const socket = io(`${SOCKET_BASE}/${namespace}`, {
      auth: { token },          // ← sent in the handshake, not a query param
      transports: ["websocket"],
    });
    socketRef.current = socket;

    socket.on("connect", () => setStatus("connected"));
    socket.on("disconnect", () => setStatus("disconnected"));

    return () => { socket.disconnect(); socketRef.current = null; };
  }, [namespace, enabled]);

  return { socketRef, status, isConnected: status === "connected" };
}
```

**Key design decisions:**
- `socketRef` is a `useRef` (not `useState`) so the socket instance doesn't cause re-renders. `status` is `useState` so components can react when connection state changes.
- Auth is via `auth: { token }` in the handshake — this is what the Socket.IO server reads. Query params (the old approach `?token=...`) are less secure and non-standard. (See `learning/frontend-auth.md` Part 37 for a real bug where a wrong cookie expiry silently broke this token read.)

### Registering event handlers

There are two approaches. The first looks sensible but has a subtle flaw. The second is correct.

#### ❌ Approach 1 — Guard with `isConnected` (has a race condition)

```tsx
const { socketRef, isConnected, status } = useSocket("messaging");

useEffect(() => {
  if (!isConnected) return;      // ← "only run if connected"
  const socket = socketRef.current;
  if (!socket) return;

  socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });

  const handleMessage = (msg: ChatMessage) => {
    setMessages(prev => [...prev, msg]);
  };
  socket.on("new:event-chat", handleMessage);

  return () => {
    socket.off("new:event-chat", handleMessage);
  };
}, [isConnected, status, eventId, socketRef]);
```

**Why this seems to work**: `isConnected` is React state. When the socket connects, `setStatus("connected")` fires → React re-renders → `isConnected` becomes `true` → the effect re-runs and emits `join:event-chat`.

**Why it sometimes doesn't work**: `isConnected` changing from `false` to `true` is a React state update. React may batch that update with other renders, or the timing between the socket's internal connect event and React's re-render cycle may not align. If the effect's re-run is delayed or missed, `join:event-chat` is never emitted and the user is in the chat screen but the server never put them in the room — messages arrive for the other person but not for this user.

This produced the symptom: "messages work sometimes, not others, the socket status shows `connected` but messages don't come through."

#### ✅ Approach 2 — Listen on the socket's own `"connect"` event (correct)

```tsx
const { socketRef } = useSocket("messaging");

useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  // joinRoom is called every time the socket connects (including reconnects)
  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });
  };

  const handleMessage = (msg: ChatMessage) => {
    setMessages(prev => [...prev, msg]);
  };

  // Register the join as a handler for the socket's "connect" event
  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleMessage);

  // If the socket was ALREADY connected when this effect ran,
  // "connect" won't fire again — so call joinRoom() immediately
  if (socket.connected) {
    joinRoom();
  }

  return () => {
    socket.off("connect", joinRoom);
    socket.off("new:event-chat", handleMessage);
  };
}, [eventId]);  // no need for isConnected/status in deps — we use events now
```

**Why this works**: `socket.on("connect", joinRoom)` registers `joinRoom` as a listener inside **socket.io's own event system**, not React's. When the socket successfully connects, socket.io fires this event synchronously and `joinRoom` runs immediately — no waiting for React to re-render and re-run an effect. The `if (socket.connected)` fallback handles the case where the socket connected before this effect even ran (both `useSocket`'s effect and this effect run after the same render — if the connection is instant, `connected` is already `true`).

**Bonus — reconnects are free**: If the network drops and the socket reconnects, socket.io fires `"connect"` again. `joinRoom` runs again automatically. The old `isConnected` approach would also handle this via `false → true`, but the event-driven approach is guaranteed to work even if React batching delays the state update.

`socket.on("new:event-chat", handleMessage)` registers a passive listener. It doesn't fire anything to the server — it just waits. Socket.io keeps this listener alive across disconnect/reconnect cycles. You don't need to re-register it on reconnect.

(See section 36 below for the full write-up of this exact race condition — the DM-room version of the same bug and fix — and section 48 for the effect-dependency rule needed when the room itself can change, e.g. switching event-chat tabs.)

### Enum values matter

The backend uses uppercase enums. The UI uses readable strings. Map them explicitly:

```ts
const SECTION_KEY = {
  "pre-event":  "PRE_EVENT",
  "during":     "DURING_EVENT",
  "post-event": "POST_EVENT",
} as const;

// Wrong ❌
socket.emit("join:event-chat", { section: "pre-event" });

// Right ✅
socket.emit("join:event-chat", { section: SECTION_KEY[activeSection] });
```

---

## 36. Socket.IO — Event-Driven Join (The isConnected Race Condition)

### Background — what is a "room"?

In Socket.IO, a **room** is a server-side group that a socket can join. When the server calls `socket.join("room-abc")`, that socket starts receiving any event the server broadcasts to `"room-abc"`. Rooms are how one-to-one DMs work: User A and User B both join the room for their conversation, and when either sends a message the server emits it to the room so both receive it.

The client tells the server "put me in this room" by emitting a named event — in this project `join:dm` for DMs and `join:event-chat` for event chats. If you forget to emit that event, or if it fails to reach the server, you never get added to the room and you never receive messages.

### The symptom

Messages would work sometimes, fail others. The socket status showed `"connected"` in the UI. The server was clearly receiving messages (the other person could see them). But the recipient's screen stayed blank. Intermittent — worked on first load, broke after navigating away and back, or after the socket reconnected.

### Why the original pattern was fragile

```ts
// ❌ Original — guards the join behind React state
useEffect(() => {
  if (!isConnected) return;   // ← "only proceed if connected"
  const socket = socketRef.current;
  if (!socket) return;

  socket.emit("join:dm", { conversationId }); // ← join the room
  socket.on("new:dm", handler);               // ← listen for messages
  return () => socket.off("new:dm", handler);

}, [isConnected, status, conversationId, socketRef]);
```

On paper, this looks fine: `isConnected` is `false` on mount (socket is still connecting), the effect bails. When the socket connects, `setStatus("connected")` fires inside `useSocket`, React re-renders, `isConnected` becomes `true`, the effect re-runs, and `join:dm` gets emitted.

The problem is that this re-run goes through **React's rendering pipeline**:

```
Socket connects (socket.io event loop)
  ↓
setStatus("connected") called inside useSocket
  ↓
React schedules a re-render (batched with other state updates)
  ↓
React commits the render
  ↓
useEffect cleanup runs (removes old listeners)
  ↓
useEffect setup runs (emits join:dm, adds new listeners)
```

Every step in that chain is a potential point of failure. React 18's concurrent rendering can batch or defer updates. The timing between step 1 (socket.io event loop) and step 6 (effect runs) is non-deterministic. If anything in between delays or skips a step — maybe the component re-renders for a different reason at the wrong moment, maybe React batches the state update together with another re-render that short-circuits the effect — `join:dm` never fires.

This is a **race condition** between socket.io's event system and React's rendering pipeline.

### The fix — use socket.io's own event system

```ts
// ✅ Event-driven — bypasses React's rendering pipeline entirely
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const joinRoom = () => {
    // This runs inside socket.io's event loop — guaranteed timing
    socket.emit("join:dm", { conversationId });
  };

  const handleNewDm = (msg: Message) => {
    setLocalMessages(prev => [...prev, msg]);
  };

  // Register joinRoom as a handler for the socket's OWN "connect" event.
  // socket.io fires this immediately when the handshake completes.
  socket.on("connect", joinRoom);
  socket.on("new:dm", handleNewDm);

  // The socket might already be connected when this effect runs
  // (both useSocket's effect and this effect run after the same render).
  // If it is, "connect" won't fire again — so join right now.
  if (socket.connected) {
    joinRoom();
  }

  return () => {
    socket.off("connect", joinRoom);
    socket.off("new:dm", handleNewDm);
  };
}, [conversationId]);
// socketRef is a stable useRef — it never changes, so no need in deps
// isConnected / status removed — we don't need React to mediate anymore
```

**What changed and why it works:**

`socket.on("connect", joinRoom)` registers `joinRoom` as a listener inside **socket.io's own internal event emitter**. When the socket successfully handshakes with the server, socket.io fires `"connect"` synchronously in its own event loop — completely outside React's rendering cycle. `joinRoom` runs immediately. No batching, no deferred renders, no race.

`socket.on("new:dm", handleNewDm)` registers a passive listener. Socket.io keeps this alive across disconnect/reconnect cycles — you don't need to re-register it. It just sits there waiting for the server to push messages.

The `if (socket.connected)` check handles the case where `useSocket`'s effect already ran and the socket is already up by the time this effect runs. Since "connect" already fired, it won't fire again — so we call `joinRoom()` directly.

**Reconnects are free:** if the network drops and socket.io reconnects, it fires `"connect"` again. `joinRoom` emits `join:dm` again. The server adds this socket back to the room. No extra code needed.

### For passive listeners (no join emit needed)

Some namespaces put you in a room automatically based on who you are (the server reads your JWT on connect and adds you to your personal notification room). In that case there's no join event to emit — just register the listener:

```ts
// Notifications — server handles room assignment on auth
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const handler = (notif: Notification) => {
    setPendingIds(prev => new Set([...prev, notif.id]));
    refetch();
  };

  // No join needed — just listen
  // Socket.io keeps this registered across disconnects/reconnects
  socket.on("notification", handler);
  return () => socket.off("notification", handler);
}, [socketRef]);
// ❌ Don't add isConnected to deps — it's not needed and causes the same race condition
```

### Quick reference — both patterns

```ts
// ── Room-based (DMs, event chat) — must emit join ──────────────────────────
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const join = () => socket.emit("join:room", { roomId });
  const onMessage = (msg) => setMessages(prev => [...prev, msg]);

  socket.on("connect", join);     // fires on connect AND reconnect
  socket.on("new:message", onMessage);
  if (socket.connected) join();   // already connected? join right now

  return () => {
    socket.off("connect", join);
    socket.off("new:message", onMessage);
  };
}, [roomId]);

// ── Passive (notifications, server decides room) — no join needed ───────────
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const onNotif = (n) => handleNotif(n);
  socket.on("notification", onNotif);
  return () => socket.off("notification", onNotif);
}, [socketRef]);
```

(See `learning/backend-realtime.md` Part 39 for the server-side confirmation of why this bug was invisible from the backend's perspective — the room-join call simply never reached it.)

---

## 38. Optimistic Messages — Deduplication Pattern

### The double-bubble problem

When you send a message via Socket.IO:
1. Frontend adds an optimistic bubble locally (instant feedback)
2. Server receives `send:dm`, saves it, and broadcasts `new:dm` to everyone in the room — **including the sender**
3. `handleNewDm` appends the server message as another bubble

Result: the sender sees the message twice. The server stores it once (correct), but the UI shows two bubbles.

### The fix — replace, don't append

Track optimistic messages in a `Map` keyed by body text. When `new:dm` arrives from yourself, look up the pending entry and **replace** the optimistic bubble with the real one:

```ts
// Track: body text → optimistic id
const pendingOptimisticRef = useRef<Map<string, string>>(new Map());

// On send:
const optimisticId = `opt-${Date.now()}`;
pendingOptimisticRef.current.set(body, optimisticId);
const optimistic: Message = {
  id: optimisticId,
  senderId: currentUserId,
  body,
  createdAt: new Date().toISOString(),
};
setLocalMessages(prev => [...prev, optimistic]);

// In handleNewDm:
const handleNewDm = (msg: Message) => {
  if (msg.senderId === currentUserId) {
    const optId = pendingOptimisticRef.current.get(msg.body);
    if (optId) {
      pendingOptimisticRef.current.delete(msg.body);
      // Replace the optimistic bubble with the real one (correct id + server timestamp)
      setLocalMessages(prev => prev.map(m => m.id === optId ? msg : m));
      return;
    }
  }
  // Message from the other person — just append + play sound
  setLocalMessages(prev => [...prev, msg]);
};
```

### Why a ref, not state?

`pendingOptimisticRef` is a `useRef<Map>`. It needs to be:
- **Readable inside the `new:dm` socket handler** (a closure that runs async)
- **Writable without triggering a re-render** (it's bookkeeping, not UI state)

If it were `useState`, the handler would close over a stale snapshot of the Map and the lookup would fail. Refs are mutable and always current.

### Benefits of replacement over skipping

Replacing with the real server message means:
- The message gets the real server-assigned `id` (important for dedup on future page loads)
- The timestamp becomes the server's authoritative time
- If the server modifies the body (e.g. trims it), the UI reflects that

(See section 47 below for the equivalent optimistic-bubble pattern used in event chat, including why those bubbles must be *prepended* rather than appended.)

---

## 39. Chat UI — Grouped Bubbles, Avatars, and Full-Screen Escape

### Grouped message bubbles

WhatsApp/iMessage style: consecutive messages from the same sender form a "group". The avatar appears only on the last message of each group; the bubble corners flatten on connecting sides.

```tsx
{localMessages.map((message, index) => {
  const isMine = message.senderId === currentUserId;
  const prev = localMessages[index - 1];
  const next = localMessages[index + 1];
  const isFirstInGroup = !prev || prev.senderId !== message.senderId;
  const isLastInGroup  = !next || next.senderId !== message.senderId;

  return (
    <div key={message.id} className={cn(
      "flex items-end gap-2",
      isMine ? "justify-end" : "justify-start",
      isLastInGroup && index !== localMessages.length - 1 && "mb-2",
    )}>
      {/* Fixed-width avatar column keeps all received bubbles aligned */}
      {!isMine && (
        <div className="w-7 shrink-0 self-end">
          {isLastInGroup ? (
            <Avatar className="h-7 w-7">
              <AvatarImage src={conversation.participant.avatarUrl} />
              <AvatarFallback>{conversation.participant.username?.[0]}</AvatarFallback>
            </Avatar>
          ) : null /* spacer is always rendered, avatar only on last */}
        </div>
      )}

      <div className={cn("flex flex-col max-w-[75%]", isMine && "items-end")}>
        <div className={cn(
          "px-4 py-2 text-sm rounded-2xl",
          isMine ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
          // Flatten connecting corners within a group
          isMine  && !isFirstInGroup && "rounded-tr-[6px]",
          isMine  && !isLastInGroup  && "rounded-br-[6px]",
          !isMine && !isFirstInGroup && "rounded-tl-[6px]",
          !isMine && !isLastInGroup  && "rounded-bl-[6px]",
        )}>
          {message.body}
        </div>
        {/* Timestamp only at the bottom of each group */}
        {isLastInGroup && (
          <p className="text-[10px] mt-1 px-1 text-muted-foreground">
            {formatTime(message.createdAt)}
          </p>
        )}
      </div>
    </div>
  );
})}
```

**Key insight**: the `w-7` spacer div is rendered for **every** received message, even ones that don't show the avatar. This keeps all received bubbles horizontally aligned — without it, bubbles shift left on non-avatar rows.

### `min-h-0` for scrollable flex children

A common Tailwind trap: a `flex-1 overflow-y-auto` div inside a flex column doesn't scroll.

```tsx
{/* ❌ Doesn't scroll — flex-1 grows the div but doesn't cap its height */}
<div className="flex-1 overflow-y-auto">

{/* ✅ min-h-0 overrides flex's default min-height: auto, capping the height */}
<div className="flex-1 min-h-0 overflow-y-auto">
```

**Why**: In a flex column, `flex-1` makes the child expand to fill available space. But flex items have `min-height: auto` by default, which means they can grow beyond their container to fit content. `overflow-y-auto` only activates when height is explicitly constrained. `min-h-0` overrides the default and lets the flex container actually cap the height.

### Escaping the layout chrome for full-screen views

The messages chat view needs to cover the entire viewport — no navbar, no bottom nav. Two approaches:

**Approach 1 — `fixed inset-0` with high z-index**

```tsx
<div className="fixed inset-0 z-[1100000] bg-background flex flex-col">
```

The z-index must be higher than the navbar (`z-[1000000]` in this project). Easy to mess up — if you use `z-[9999]` you get the navbar bleeding through.

**Approach 2 — Redux `setHideHeader` (recommended)**

```ts
// In the full-screen component:
const dispatch = useDispatch();
useEffect(() => {
  dispatch(setHideHeader(true));
  return () => { dispatch(setHideHeader(false)); };
}, [dispatch]);
```

The `DashboardNavbar` and `BottomNav` both read `hideHeader` from Redux and return `null` when it's true. No z-index battle. The UI components completely unmount, freeing memory and preventing any bleed-through. Used in the vibetag editor, postcard viewer, and now the chat view.

**Rule**: use `setHideHeader` when you control the navigation chrome. Use `fixed inset-0 z-[...]` only for components that render outside the normal layout tree (e.g. portals, dialogs). (See `learning/frontend-state-management.md` for the `ui` Redux slice this `hideHeader` flag lives in.)

---

## 40. Synthesised Notification Sounds — Web Audio API

### No files needed

Instead of shipping an audio file in `/public`, use the Web Audio API to synthesise a notification ping in code:

```ts
function playNotifSound() {
  try {
    const AudioCtx = window.AudioContext ?? (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx() as AudioContext;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    // 1400 Hz → 900 Hz sweep over 120ms = a classic "ding"
    osc.type = "sine";
    osc.frequency.setValueAtTime(1400, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + 0.12);

    // Short attack, longer decay
    gain.gain.setValueAtTime(0, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.18, ctx.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);

    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.35);
  } catch {
    // Browsers may block AudioContext without a prior user gesture — fail silently
  }
}
```

### How Web Audio works

- `AudioContext` is the engine. Create one per sound (or reuse a persistent one).
- `OscillatorNode` generates a waveform. `type: "sine"` is smooth; `"square"` is harsher.
- `GainNode` controls volume. `gain.gain` is an `AudioParam` — you can schedule ramp animations on it using `linearRampToValueAtTime` and `exponentialRampToValueAtTime`.
- Connect nodes: `oscillator → gain → ctx.destination` (speakers).
- `start()` / `stop()` use `ctx.currentTime` (the audio clock, not wall time).

### The user gesture requirement

Browsers block `new AudioContext()` until the user has interacted with the page. In a chat app this is never a problem — the user had to tap a conversation to get to the chat screen. The `try/catch` handles the rare case where sound is blocked silently.

### When to play it

Only play for messages from the other person — never for your own sends:

```ts
const handleNewDm = (msg: Message) => {
  if (msg.senderId === currentUserId) {
    // echo of own message — dedup it, don't sound
    return;
  }
  playNotifSound();  // incoming message from other person
  setLocalMessages(prev => [...prev, msg]);
};
```

---

## 41. Real-Time Notification Badge — pendingIds vs Counter

### The double-count problem

The original notification bell used a `realtimeCount` counter:

```ts
const [realtimeCount, setRealtimeCount] = useState(0);

// On new notification:
setRealtimeCount(c => c + 1);
refetch();  // ← pulls updated list from server

// Badge:
const unreadCount = (data?.data?.meta?.unreadCount ?? 0) + realtimeCount;
```

When `refetch()` resolves, `meta.unreadCount` from the server already includes the new notification. But `realtimeCount` still holds 1. Result: the badge shows `serverCount + 1` — one too many.

### The fix — track pending IDs, subtract once fetched

```ts
const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());

// On new notification:
const handleNotification = (notif: Notification) => {
  setPendingIds(prev => new Set([...prev, notif.id ?? `rt-${Date.now()}`]));
  refetch();
};

// Once REST data comes back, remove IDs that are now in the list:
useEffect(() => {
  if (!data) return;
  const fetchedIds = new Set(notifications.map(n => n.id));
  setPendingIds(prev => {
    const stillPending = new Set([...prev].filter(id => !fetchedIds.has(id)));
    return stillPending.size === prev.size ? prev : stillPending;  // avoid re-render if unchanged
  });
}, [data]);

// Badge — only count IDs not yet confirmed by the server
const unreadCount = restUnread + pendingIds.size;
```

### Why this works

- When a notification arrives, it's added to `pendingIds`. Badge increments immediately.
- `refetch()` runs. The server response includes the new notification in `meta.unreadCount`.
- The cleanup effect sees the notification's `id` in the fetched list and removes it from `pendingIds`.
- Badge = `restUnread + 0` = correct value, no double count.

### The `stillPending.size === prev.size ? prev : stillPending` optimisation

Returning the **same Set reference** when nothing changed prevents React from re-rendering. `new Set([...prev])` always creates a new object even if the contents are identical — React would see a new reference and re-render unnecessarily.

### Notification badge — full pattern

```
New notification arrives via socket
  ↓
Add id to pendingIds → badge shows +1 immediately
  ↓
refetch() — pulls updated list from server
  ↓
Server responds with new unreadCount + notification in list
  ↓
Cleanup effect: id is in fetchedIds → remove from pendingIds
  ↓
Badge = server's unreadCount + 0 (pending now empty)  ← correct
```

(See section 46 below for the analogous "instant dot, then confirmed count" pattern used for the bottom-nav Messages badge.)

---

## 42. WebSockets from First Principles — ws, wss, and Socket.IO

If you have never touched real-time communication before, start here. This explains the whole stack from the protocol up.

### The problem HTTP has

Every HTTP request follows this pattern:

```
Browser:  "Hey server, give me the events list"
Server:   "Here you go" → closes connection
```

The server can only talk to the browser when the browser asks first. If something changes on the server (new message, new notification), the server has no way to tell the browser. The browser has to keep asking ("polling"):

```
Browser → "any new messages?" → Server: "no"
Browser → "any new messages?" → Server: "no"
Browser → "any new messages?" → Server: "yes, here's one"
```

Polling every second is wasteful — 999 out of 1000 requests get "no". Polling every 30 seconds means 30-second delays on messages.

### What WebSocket is

WebSocket is a different protocol that creates a **persistent two-way connection**:

```
Browser → Server: "I want to upgrade this HTTP connection to WebSocket"
Server:           "Agreed"
─────────────── connection stays open ───────────────
Server → Browser: "New message from Alice: hey!"   (any time)
Browser → Server: "I'm typing..."                  (any time)
Server → Browser: "Alice is also typing"           (any time)
─────────────── either side can close it ────────────
```

Once the upgrade handshake happens, either side can send data to the other at any time without waiting to be asked. This is what makes chat, live notifications, and collaborative editing possible.

### `ws://` and `wss://`

WebSocket has its own URL schemes:

| Scheme | What it is | When to use |
|---|---|---|
| `ws://` | Plain WebSocket — data travels unencrypted | Development only (`ws://localhost:3000`) |
| `wss://` | WebSocket **Secure** — encrypted with TLS (same as HTTPS) | Always in production |

The relationship mirrors HTTP/HTTPS exactly:
- `http://` → unencrypted → `https://` → encrypted
- `ws://` → unencrypted → `wss://` → encrypted

In production, using `ws://` means anyone between the browser and server (WiFi router, ISP, CDN) can read every message. Always use `wss://` in production.

You don't usually set `ws://` or `wss://` manually in this project — the Socket.IO client derives it automatically from `NEXT_PUBLIC_API_URL`. If that URL starts with `https://`, socket.io uses `wss://`. If it starts with `http://` (local dev), it uses `ws://`.

### What Socket.IO is (and how it relates to WebSocket)

Raw WebSocket is just a pipe — it sends raw bytes or strings. You have to invent your own protocol on top of it:

```js
// Raw WebSocket — you have to parse everything yourself
const ws = new WebSocket("wss://api.nextvibe.com");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);   // hope it's JSON
  if (data.type === "new_message") { ... }
  if (data.type === "user_joined") { ... }
  // ... handle every type manually
};
ws.send(JSON.stringify({ type: "join_room", roomId: "abc" }));
```

Socket.IO wraps WebSocket (and falls back to HTTP long-polling if WebSocket is blocked) and gives you:

| Feature | Raw WebSocket | Socket.IO |
|---|---|---|
| Named events | ❌ manual JSON parsing | ✅ `socket.on("new:dm", handler)` |
| Rooms (server-side groups) | ❌ must implement yourself | ✅ built in |
| Auto reconnect | ❌ must implement yourself | ✅ built in, with backoff |
| Namespaces | ❌ must implement yourself | ✅ `/messaging`, `/notifications` |
| Auth in handshake | ❌ manual | ✅ `io(url, { auth: { token } })` |
| Fallback transports | ❌ | ✅ falls back to polling if WS blocked |

Socket.IO's "named events" are the key win for this project:

```ts
// Socket.IO — clean and readable
socket.emit("join:dm", { conversationId: "abc123" });
socket.on("new:dm", (message) => { /* ... */ });

// Equivalent raw WebSocket — verbose and fragile
ws.send(JSON.stringify({ event: "join:dm", data: { conversationId: "abc123" } }));
ws.onmessage = (e) => {
  const parsed = JSON.parse(e.data);
  if (parsed.event === "new:dm") { /* ... */ }
};
```

### The connection lifecycle

```
1. io() called
   ↓ Socket.IO tries WebSocket first (wss://)
   ↓ If blocked, falls back to HTTP long-polling

2. HTTP upgrade handshake
   Client → Server: "Upgrade: websocket"
   Server → Client: "101 Switching Protocols"
   ↓ Connection is now a persistent WebSocket

3. Socket.IO auth
   Client sends: { auth: { token } }
   Server validates JWT — if invalid, closes the connection

4. "connect" event fires on client
   → This is when it's safe to emit join:* events

5. Normal operation
   Either side can emit named events at any time

6. Disconnect (network drop, server restart, etc.)
   → Socket.IO automatically tries to reconnect (exponential backoff)
   → "connect" fires again on successful reconnect
   → Must re-emit join:* events (rooms are not persisted across connections)
```

Step 6 is why `socket.on("connect", joinRoom)` is the correct pattern — it fires at step 4 and again after every step 6 reconnect. (See section 36 above for the full derivation of why this beats the naive `isConnected`-guarded effect.)

### How this project's `useSocket` hook works under the hood

```ts
const socket = io(`${SOCKET_BASE}/${namespace}`, {
  auth: { token },            // sent in the handshake (step 3)
  transports: ["websocket"],  // skip long-polling, go straight to WebSocket
});
```

`transports: ["websocket"]` skips Socket.IO's default "try polling first, then upgrade" behaviour. This is faster but means if WebSocket is blocked (rare in modern environments), the connection simply fails rather than falling back. Acceptable for this project.

`auth: { token }` sends the JWT during the handshake. The server reads it and can reject the connection before a single event is exchanged. This is more secure than query params (`?token=...`) which appear in server logs. (See `learning/backend-realtime.md` Part 26 for the server-side JWT verification this handshake triggers.)

---

## 44. Conversations List — Real-Time Updates and Stale Cache

### The symptom

Two separate bugs that felt like one:

1. You open the messages page. Someone sends you a message. The list doesn't update — the last message preview and unread count stay stale until you manually refresh.
2. You open a conversation you last visited 10 minutes ago. It shows the old messages from 10 minutes ago, then a moment later jumps to the latest. Confusing.

### Why both happened

**Bug 1 — stale list:** The `Messages` component (the conversation list) used `useGetConversationsQuery()` once on mount. No socket was connected at list level. The socket only existed inside `ChatView`, and only for real-time message delivery. Nobody was listening for "new message arrived, refresh the list."

**Bug 2 — stale chat:** RTK Query caches query results. By default, `useGetMessagesQuery({ conversationId })` returns the cached result from the last time you visited that conversation and fetches a fresh copy in the background. The user sees old data first, then it updates. This is called "stale-while-revalidate" and it's the default RTK Query behaviour. (See `learning/frontend-state-management.md` for the general RTK Query caching model this default behaviour comes from.)

### Fix 1 — real-time list: add a socket at list level

```ts
// ❌ Before — no socket at the list level, list only updates on page refresh
const { data, isLoading, isError, refetch } = useGetConversationsQuery();
// ...no socket...
```

```ts
// ✅ After — socket connected while list is visible
const { data, isLoading, isError, refetch } = useGetConversationsQuery();
const conversations = data?.data ?? [];

// Disabled when ChatView is open — ChatView has its own socket,
// and we don't want two simultaneous connections to the same namespace.
const { socketRef: listSocketRef } = useSocket("messaging", {
  enabled: !selectedConversation,
});

useEffect(() => {
  if (selectedConversation) return;
  const socket = listSocketRef.current;
  if (!socket) return;

  // Join every conversation room so the server sends new:dm for any of them
  const joinAll = () => {
    conversations.forEach((c) => {
      socket.emit("join:dm", { conversationId: c.id });
    });
  };

  const handleNewDm = (msg: any) => {
    refetch(); // pull fresh lastMessage + unreadCount for all conversations
    // (also bump local badge — see section 45)
  };

  socket.on("connect", joinAll);
  socket.on("new:dm", handleNewDm);
  if (socket.connected) joinAll();

  return () => {
    socket.off("connect", joinAll);
    socket.off("new:dm", handleNewDm);
  };
}, [selectedConversation, listSocketRef, conversations, refetch]);
```

**Key insight:** you join ALL conversation rooms at once. The server sends `new:dm` events to each room. Joining multiple rooms from the same socket is cheap — it's just the server routing events to this socket's session.

**Why `enabled: !selectedConversation`?** When `ChatView` is open, `selectedConversation` is non-null. `ChatView` has its own `useSocket("messaging")` call. If the list also kept its socket alive, you'd have two sockets connected to the same namespace from the same user at the same time. That works, but it wastes a connection. Disabling the list socket when the chat is open means exactly one socket is active at all times.

### Fix 2 — stale chat: force fresh fetch on mount

```ts
// ❌ Before — RTK Query returns cached data first, fetches fresh in background
const { data, isLoading } = useGetMessagesQuery({ conversationId: conversation.id });
```

```ts
// ✅ After — always fetch fresh messages when opening a conversation
const { data, isLoading } = useGetMessagesQuery(
  { conversationId: conversation.id },
  { refetchOnMountOrArgChange: true }
);
```

`refetchOnMountOrArgChange: true` tells RTK Query: "every time this component mounts or the argument changes, fire a fresh request — don't serve cache." The user always sees up-to-date messages when they open a chat.

The trade-off: one extra network request per chat open. That's acceptable — messages must be fresh.

---

## 45. Per-Conversation Unread Badge — Local + Server Merge

### The problem

The `Conversation` type has an `unreadCount` field from the server. The badge showed `conversation.unreadCount`. But:

- The server count only updates after `refetch()` completes (network round-trip takes ~200–500ms)
- Some backends don't reliably track `unreadCount` per user at all
- Between the socket event and the refetch landing, there's a window where the badge shows the wrong number

### The two-layer approach

**Layer 1 — server count (authoritative):** `conversation.unreadCount` from RTK Query. Accurate after refetch.

**Layer 2 — local count (instant):** A `Record<string, number>` state that increments the moment a `new:dm` socket event arrives (if the server includes `conversationId` in the payload).

```ts
const [localUnread, setLocalUnread] = useState<Record<string, number>>({});

// In the socket handler:
const handleNewDm = (msg: any) => {
  refetch();
  const convId: string | undefined = msg?.conversationId;
  if (convId) {
    setLocalUnread((prev) => ({
      ...prev,
      [convId]: (prev[convId] ?? 0) + 1,
    }));
  }
};

// In the render, merge both:
const unread = (conversation.unreadCount ?? 0) + (localUnread[conversation.id] ?? 0);
```

### Preventing double-count

After `refetch()` lands, the server's `unreadCount` now includes the new message. If we kept the local count too, we'd show `server(1) + local(1) = 2` for a single unread. Fix: clear local entries once the server confirms them.

```ts
useEffect(() => {
  if (!conversations.length) return;
  setLocalUnread((prev) => {
    const changed = conversations.some((c) => c.unreadCount > 0 && prev[c.id]);
    if (!changed) return prev; // avoid re-render if nothing changed
    const next = { ...prev };
    conversations.forEach((c) => {
      // Server now tracks this conversation's unread — our local copy is redundant
      if (c.unreadCount > 0) delete next[c.id];
    });
    return next;
  });
}, [conversations]);
```

**The fallback:** if the server always returns 0 (backend doesn't track reads), the local count stays and the badge still works.

### Clear on open

When the user taps a conversation, clear its local count immediately — they're about to read those messages.

```ts
const handleSelectConversation = (conv: Conversation) => {
  setLocalUnread((prev) => {
    if (!prev[conv.id]) return prev; // nothing to clear, don't re-render
    const next = { ...prev };
    delete next[conv.id];
    return next;
  });
  setSelectedConversation(conv);
};
```

### Badge design (WhatsApp style)

Moved from avatar corner → right side of the row, next to the last message preview. Also bold name + bold preview text when unread.

```tsx
const unread = (conversation.unreadCount ?? 0) + (localUnread[conversation.id] ?? 0);

<Card className={cn("cursor-pointer", unread > 0 && "border-primary/30 bg-primary/5")}>
  <div className="flex items-center gap-3">
    <Avatar className="h-12 w-12 shrink-0">...</Avatar>

    <div className="flex-1 min-w-0">
      <div className="flex items-center justify-between gap-2">
        <h3 className={cn("truncate", unread > 0 ? "font-bold" : "font-semibold")}>
          {conversation.participant.username}
        </h3>
        <span className={cn("text-xs shrink-0", unread > 0 ? "text-primary font-semibold" : "text-muted-foreground")}>
          {formatTime(conversation.lastMessage?.createdAt)}
        </span>
      </div>

      <div className="flex items-center justify-between gap-2 mt-0.5">
        <p className={cn("text-sm truncate", unread > 0 ? "text-foreground font-medium" : "text-muted-foreground")}>
          {conversation.lastMessage?.body}
        </p>
        {unread > 0 && (
          <span className="shrink-0 min-w-5 h-5 rounded-full bg-primary text-primary-foreground text-[11px] font-bold flex items-center justify-center px-1.5 leading-none">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </div>
    </div>
  </div>
</Card>
```

---

## 46. Bottom Nav Real-Time Badge — Shared Cache + Conditional Socket

### The goal

The Messages icon in the bottom nav should show a badge with the total unread count, updating in real time — even when the user is on the events page, profile page, or anywhere else.

### The shared cache trick

RTK Query caches query results globally. Every component that calls `useGetConversationsQuery()` shares the same cached data. When the messages page calls `refetch()` on a new `new:dm` event, the cache updates — and every other component reading that cache updates too, for free.

This means the bottom nav badge doesn't need its own fetch. It just reads the same cache:

```ts
const { data, refetch } = useGetConversationsQuery();
const conversations = data?.data ?? [];
const serverUnread = conversations.reduce((s, c) => s + (c.unreadCount ?? 0), 0);
```

### The gap: when not on /messages

When the user is on `/events` or `/profile`, the messages page isn't mounted, so its socket isn't active. Nobody is calling `refetch()`. The cache goes stale. The bottom nav badge doesn't update.

Fix: the bottom nav runs its own socket — but only when NOT on `/messages`, to avoid a double connection.

```ts
function useUnreadMessages(isOnMessagesPage: boolean) {
  const { data, refetch } = useGetConversationsQuery();
  const conversations = data?.data ?? [];
  const serverUnread = conversations.reduce((s, c) => s + (c.unreadCount ?? 0), 0);

  const [pendingNew, setPendingNew] = useState(false);

  // Once server confirms the count, clear the optimistic dot
  useEffect(() => {
    if (serverUnread > 0) setPendingNew(false);
  }, [serverUnread]);

  // Socket — disabled when /messages is open (that page has its own socket)
  const { socketRef } = useSocket("messaging", { enabled: !isOnMessagesPage });

  useEffect(() => {
    if (isOnMessagesPage) return;
    const socket = socketRef.current;
    if (!socket) return;

    const joinAll = () => {
      conversations.forEach((c) => socket.emit("join:dm", { conversationId: c.id }));
    };

    const handleNewDm = () => {
      setPendingNew(true); // dot appears immediately
      refetch();           // server count updates ~200ms later
    };

    socket.on("connect", joinAll);
    socket.on("new:dm", handleNewDm);
    if (socket.connected) joinAll();

    return () => {
      socket.off("connect", joinAll);
      socket.off("new:dm", handleNewDm);
    };
  }, [isOnMessagesPage, socketRef, conversations, refetch]);

  return { unread: serverUnread, pendingNew };
}
```

In the bottom nav:

```tsx
const isOnMessagesPage = pathname.startsWith("/messages");
const { unread, pendingNew } = useUnreadMessages(isOnMessagesPage);
const showBadge = unread > 0 || pendingNew;
```

Badge renders:

```tsx
{isMessages && showBadge && (
  <span className="absolute -top-1.5 -right-1.5 min-w-4 h-4 rounded-full bg-primary text-primary-foreground text-[9px] font-bold flex items-center justify-center px-0.5 leading-none">
    {unread > 0 ? (unread > 99 ? "99+" : unread) : ""}
  </span>
)}
```

When `pendingNew` is true but `unread` is still 0 (refetch in flight), the badge renders as an empty red dot — instant visual feedback, no stale count shown.

### Socket coverage summary

| Where the user is | Which socket runs | What triggers refetch |
|---|---|---|
| `/messages` list view | List-level socket (`enabled: !selectedConversation`) | `handleNewDm` in Messages component |
| `/messages` chat open (ChatView) | ChatView socket | Dedicated to real-time messages, list updates when back |
| Any other page | Bottom nav socket (`enabled: !isOnMessagesPage`) | `handleNewDm` in `useUnreadMessages` |

No page ever runs two sockets to the same namespace simultaneously.

---

## 47. Event Chat — Message Order and Prepend vs Append

### The symptom

"When I add a new message it shows at the bottom, but when I refresh it shows at the top."

### Why it happened

The server returns event chat history **newest-first** (most recent message at index 0). The history was stored directly: `setMessages(json?.data?.data ?? [])`. When rendered top-to-bottom, the newest message appears at the top. That's the intended design — it's a comment section, not a chat bubble list.

But the socket handler did:

```ts
// ❌ Appending — puts new message at the end (bottom)
return [...prev, msg];
```

And the optimistic bubble also appended:

```ts
// ❌ Appending
setMessages((prev) => [...prev, optimistic]);
```

Result: history renders newest-at-top, but new messages land at the bottom. They disagree.

### The fix: prepend

```ts
// ✅ Prepend — new message goes to the front (index 0 = top of list)
return [msg, ...prev];
```

```ts
// ✅ Optimistic bubble also prepended
setMessages((prev) => [optimistic, ...prev]);
```

No reversal of the history array needed. The server already gave us the right order. We just had to match it.

### Why not reverse the history?

An alternative would be to `.reverse()` the history on load (oldest first) and keep appending. This is what DM chat does — oldest at top, newest at bottom, scroll-to-bottom pattern.

For event chat, the user specifically wanted "newest at top, like a comment section." Reversing would be:
1. Extra computation on every history load (not huge, but unnecessary)
2. Requires keeping the `bottomRef` + scroll-to-bottom behaviour
3. Goes against what the server already gives you

The server chose newest-first for a reason. Trust it, match it with prepend.

### Scroll behaviour

With newest at top, there's nothing to scroll to on new messages. They just appear at the top where the user is already looking. So the `bottomRef` div and the `scrollIntoView` effects were removed entirely.

```ts
// ❌ Before — scroll to bottom on every new message
useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages.length]);

// ...
<div ref={bottomRef} />  // sentinel div at the end

// ✅ After — nothing needed, newest is already at the top
// No auto-scroll comment left to explain the decision:
// "No auto-scroll needed — newest messages appear at the top naturally."
```

### Optimistic bubbles for event chat

Added the same `pendingOptimisticRef` Map pattern as DM chat (see section 38 above):

```ts
const pendingOptimisticRef = useRef<Map<string, string>>(new Map());

const handleSend = () => {
  const text = message.trim();
  if (!text || !isConnected) return;

  socket?.emit("send:event-chat", { eventId, section: SECTION_KEY[activeSection], body: text });

  const optimisticId = `opt-${Date.now()}`;
  pendingOptimisticRef.current.set(text, optimisticId);

  const me = meData?.data as any;
  const optimistic: ChatMessage = {
    id: optimisticId,
    body: text,
    senderId: myId,
    sender: { id: myId, displayName: me?.displayName, username: me?.username, avatarUrl: me?.avatarUrl },
    createdAt: new Date().toISOString(),
  };
  setMessages((prev) => [optimistic, ...prev]); // prepend
  setMessage("");
};
```

When the server echoes the message back via `new:event-chat`, the deduplication in `handleNewMessage` finds the matching body in `pendingOptimisticRef` and replaces the optimistic entry with the real message (correct server ID and timestamp) instead of creating a duplicate.

Clear pending optimistics when switching sections (pre-event → during → post-event):

```ts
useEffect(() => {
  setMessages([]);
  pendingOptimisticRef.current.clear(); // stale optimistics from old section
  fetchHistory(activeSection);
}, [activeSection, fetchHistory]);
```

---

## 48. Tab Switching and Sockets — Effect Dependencies

### The question

"If I switch between Pre-Event / During / Post-Event tabs and come back, will the socket still work? Will real-time messages still come through?"

### Yes — because `activeSection` is in the effect dependency array

The socket effect in `EventChatTab` has this signature:

```ts
useEffect(() => {
  // ...
}, [eventId, activeSection, socketRef]);
```

When `activeSection` changes (user switches tabs), React:
1. Runs the **cleanup** of the old effect — `socket.off("connect", oldJoinRoom)` and `socket.off("new:event-chat", oldHandler)`, where `oldJoinRoom` is the closure that captured the old section value
2. Runs the **new effect** — registers new listeners that capture the new section, and emits `join:event-chat` with the new section key

The socket itself **does not disconnect or reconnect**. It stays alive. Only the room membership changes.

```ts
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const section = SECTION_KEY[activeSection]; // captures current section

  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section }); // joins the right room
  };

  const handleNewMessage = (msg: ChatMessage) => {
    // This handler only runs while this section is active.
    // When the tab switches, this specific closure is removed and replaced.
    setMessages((prev) => {
      if (msg.id && prev.some((m) => m.id === msg.id)) return prev;
      // ... dedup and prepend
    });
  };

  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleNewMessage);
  if (socket.connected) joinRoom(); // already connected → join immediately

  return () => {
    // Cleanup: remove THIS section's listeners
    socket.off("connect", joinRoom);
    socket.off("new:event-chat", handleNewMessage);
  };
}, [eventId, activeSection, socketRef]); // ← activeSection here is the key
```

### What would happen without `activeSection` in the deps

```ts
// ❌ Missing activeSection in deps — stale closure bug
useEffect(() => {
  const section = SECTION_KEY[activeSection]; // captured once, never updated

  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section }); // always "PRE_EVENT"!
  };

  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleNewMessage);
  if (socket.connected) joinRoom();

  return () => { /* only runs on unmount */ };
}, [eventId, socketRef]); // activeSection NOT here
```

The closure captures `section = "PRE_EVENT"` on first render and never updates. Switching to "During" tab → `setActiveSection("during")` → `section` in the closure is still `"PRE_EVENT"` → socket is still joined to the pre-event room → real-time messages from "during" never arrive.

### The general rule

Any value used inside a `useEffect` that can change over time must be in the dependency array. React will re-run the effect (running cleanup first) whenever any dep changes. For socket effects this means: closing old listeners, opening new ones, re-joining the correct room.

### Stale closure — the broader concept

A **stale closure** is when a function captures a variable from its surrounding scope, but that variable later changes and the function doesn't know about it.

```ts
let count = 0;
const log = () => console.log(count); // captures count = 0

count = 5;
log(); // logs 0, not 5 — stale closure
```

In React, every render creates new function instances. If your effect uses a function from the current render, the deps array tells React when to create a fresh one. Missing a dep = stale closure = bugs that are hard to track down because the code looks correct. (See `learning/frontend-payments-games.md` Part 51 for another real stale-closure bug in this codebase — the anonymous game submit handler reading React state instead of localStorage directly.)

---

## Quick Reference

### Socket.IO pattern

```tsx
const { socketRef, isConnected } = useSocket("messaging");

useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;
  const join = () => socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });
  const handler = (msg) => setMessages(prev => [...prev, msg]);
  socket.on("connect", join);
  socket.on("new:event-chat", handler);
  if (socket.connected) join();
  return () => {
    socket.off("connect", join);
    socket.off("new:event-chat", handler);
  };
}, [eventId]);
```
