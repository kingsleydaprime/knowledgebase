# NextVibe — Backend Real-Time: WebSocket Gateways & Socket.io

Split out from the original flat `learning.md` (moved to `learning/archive/`). See also
`learning/backend/01-core.md`, `learning/backend/03-modules.md` (Part 13 — Notifications Module, Part
16 — Messaging Module, which this file's gateway patterns serve), `learning/backend/02-auth.md`,
`learning/00-sys-design.md`, `learning/09-devops.md`, and — for the frontend half of this same
real-time system (the `useSocket` hook, event-driven join pattern, chat UI, notification badges) —
`learning/frontend/06-realtime.md`.

This file covers: doing WebSocket gateway authentication correctly (the difference between
"checking a token is present" and actually verifying it), why `@UseGuards` doesn't protect
`handleConnection`, documenting WebSocket events in Swagger (which has no native concept of
sockets), the full WebSocket / WSS / Socket.io picture from HTTP up through namespaces and rooms,
and why throwing exceptions inside a `@SubscribeMessage` handler behaves differently than in an
HTTP controller.

---

## Part 26 — WebSocket Gateway Authentication Done Right

### The Problem You'll Hit First

If you look at a NestJS WebSocket gateway and see this pattern, it looks reasonable:

```typescript
async handleConnection(client: Socket) {
  const token = client.handshake?.auth?.token;
  if (!token) {
    client.disconnect();
    return;
  }
  // ... token is present but never verified
}
```

This is **not authentication**. It's presence checking. Any client can send any string as `token` and get past this check. The user is not authenticated — you just know they sent something.

### The Correct Pattern

Inject `JwtService` and `ConfigService` into your gateway, then verify the token in `handleConnection` and store the payload on `client.data`:

```typescript
@WebSocketGateway({ namespace: '/messaging', cors: { origin: '*' } })
export class MessagingGateway implements OnGatewayConnection {
  constructor(
    private messagingService: MessagingService,
    private jwtService: JwtService,
    private configService: ConfigService,
  ) {}

  async handleConnection(client: Socket) {
    const token = client.handshake?.auth?.token;
    if (!token) {
      client.disconnect();
      return;
    }
    try {
      const payload = this.jwtService.verify<JwtPayload>(token, {
        secret: this.configService.get<string>('JWT_ACCESS_SECRET'),
      });
      client.data.user = payload;
    } catch {
      client.disconnect();
    }
  }
}
```

The `try/catch` is mandatory — `jwtService.verify` throws on invalid or expired tokens. Any exception means the token is invalid, so disconnect.

### Why `@UseGuards` Doesn't Work Here

`@UseGuards(WsJwtGuard)` works on `@SubscribeMessage` handlers — it runs *after* the connection is established. It does not run during `handleConnection`. If you only use guards and skip `handleConnection` validation, any client can connect (even without a token), they just can't call guarded message handlers. The socket connection itself is open, leaking it from room subscriptions and connection events.

Always validate in `handleConnection` as the gate. Guards are a second layer for specific message handlers.

### `client.data.user` — The Socket-Level User Store

`client.data` is a plain object that persists for the lifetime of the socket connection. It's the right place to store the verified JWT payload. Every subsequent handler for this client can access the verified identity without re-validating the token.

Never trust the user's identity from message body fields like `senderId`. Always derive it from `client.data.user`:

```typescript
@SubscribeMessage('send:dm')
async handleSendDm(
  @ConnectedSocket() client: Socket,
  @MessageBody() data: { conversationId: string; body?: string; mediaUrl?: string },
) {
  const senderId = client.data.user?.sub;  // from verified JWT
  if (!senderId) return;  // belt-and-suspenders: should already be disconnected
  // ...
}
```

The `data.senderId` (from the client's message body) is user-controlled input. A malicious client can put any userId there and impersonate anyone. The JWT payload cannot be forged without the server's secret.

### Make TypeScript Happy with `@WebSocketServer()`

```typescript
@WebSocketServer() server!: Server;
```

Without `!`, TypeScript strict mode will error: "Property 'server' has no initializer and is not definitely assigned in the constructor." The `!` is the definite assignment assertion — you're telling TypeScript that NestJS assigns this via the decorator, not the constructor. This is correct; NestJS does assign it.

### Module Setup for Gateway JWT

Your gateway's module must import `AuthModule` (which exports `JwtModule`) so `JwtService` is injectable:

```typescript
@Module({
  imports: [AuthModule, PrismaModule],
  providers: [MessagingGateway, MessagingService],
  controllers: [MessagingController],
})
export class MessagingModule {}
```

`AuthModule` exports `JwtModule`, which provides `JwtService`. Without this import, NestJS will throw "JwtService is not a provider" at startup.

---

## Part 29 — Documenting WebSocket Events in Swagger

### The Problem

OpenAPI (Swagger) is an HTTP specification. It has no concept of WebSocket connections, socket events, or persistent connections. NestJS's `@ApiOperation`, `@ApiBody`, `@ApiResponse` decorators only apply to HTTP route handlers — they cannot describe `@SubscribeMessage` handlers.

### The Solution: `addTag` with a Markdown Description

`DocumentBuilder.addTag(name, description)` in `main.ts` lets you add a tag entry with an arbitrary markdown description to the Swagger UI. This description appears in the tag's expandable section — a good place to put WebSocket documentation.

```typescript
const config = new DocumentBuilder()
  .setTitle('NextVibe API')
  .setVersion('1.0')
  .addBearerAuth()
  .addTag('Messaging', `
## WebSocket: /messaging namespace

Connect with Socket.io to \`ws://<host>/messaging\`.

**Authentication:** Send the JWT access token (no "Bearer " prefix) in the handshake auth object:
\`\`\`js
const socket = io('/messaging', { auth: { token: 'your.jwt.token' } });
\`\`\`

### Events You Can Emit

| Event | Payload | Description |
|---|---|---|
| \`join:dm\` | \`{ conversationId }\` | Join a DM room |
| \`send:dm\` | \`{ conversationId, body?, mediaUrl? }\` | Send a DM |
| \`typing:dm\` | \`{ conversationId }\` | Broadcast typing indicator |
| \`join:event-chat\` | \`{ eventId, section }\` | Join event chat room |
| \`send:event-chat\` | \`{ eventId, section, body?, mediaUrl? }\` | Send event chat message |

### Events You Will Receive

| Event | Payload | Description |
|---|---|---|
| \`new:dm\` | message object | New DM received |
| \`typing:dm\` | \`{ userId }\` | Someone is typing |
| \`new:event-chat\` | message object | New event chat message |

**section values:** \`PRE_EVENT\` | \`DURING_EVENT\` | \`POST_EVENT\`
  `)
  .build();
```

### Limitations

- The description is static text — it doesn't get the interactive "try it" button that HTTP endpoints have
- You can't describe request/response schemas with JSON Schema inside tag descriptions
- It's purely documentation; no machine-readable contract

### Alternative: Dedicated WebSocket Docs Page

For complex WebSocket APIs, consider a separate docs page (a `WEBSOCKET.md` file or a dedicated route serving an HTML page) linked from Swagger. The `addTag` approach works well for simple socket APIs where the team just needs to know event names and shapes.

---

## Part 39 — WebSockets, WSS, and Socket.io — The Full Picture

### HTTP vs WebSocket: The Fundamental Difference

Every request you've made so far in this codebase uses HTTP. HTTP is a **request-response** protocol — the client speaks, the server responds, the connection closes. The server can never speak first. To simulate real-time with HTTP you have to poll: "do you have a new message? no. do you have one now? no. now? no." — this is wasteful, slow, and burns battery on mobile.

**WebSocket** is a different protocol entirely. It starts as HTTP (a special "upgrade" request), then both sides agree to switch protocols, and from that point the TCP connection stays open. Either side can send a message at any time without waiting for the other to ask. One persistent connection instead of hundreds of short ones.

```
HTTP:
  Client → Server: GET /messages        (request)
  Server → Client: [messages]           (response, connection closes)
  Client → Server: GET /messages        (ask again 2 seconds later)
  ...

WebSocket:
  Client → Server: [upgrade request]    (one-time handshake)
  Server → Client: [upgrade confirmed]
  --- connection stays open forever ---
  Server → Client: new message!         (server speaks first, no request needed)
  Client → Server: typing indicator     (client speaks without waiting)
  Server → Client: another message!
```

### WS vs WSS

`ws://` is plain WebSocket — the data is sent unencrypted over the network, just like `http://`.

`wss://` is WebSocket over TLS — the same WebSocket protocol but encrypted, just like `https://`. In production you **always** use `wss://`. Modern browsers will block `ws://` connections from `https://` pages (mixed content policy).

The TLS termination usually happens at your reverse proxy (Nginx, Railway, Cloudflare), not in your Node.js process. Your Node.js app just sees a plain WebSocket connection — the encryption layer is handled before traffic reaches it. This means even if your NestJS app listens on `ws://localhost:5000` internally, the outside world connects via `wss://api.mynextvibe.com`.

### What Socket.io Is (and Is Not)

Socket.io is **not** a WebSocket library. It is a real-time messaging library that **uses** WebSocket when available, but adds its own protocol layer on top with features WebSocket alone doesn't have:

| Feature | Raw WebSocket | Socket.io |
|---|---|---|
| Auto-reconnect | No — you implement it | Built-in, exponential backoff |
| Rooms | No — you implement it | Built-in |
| Namespaces | No | Built-in |
| Acknowledgements | No | Built-in |
| Fallback to polling | No | Built-in (for restrictive networks) |
| Event names | No — just raw binary frames | Built-in (`emit('event', data)`) |
| Broadcasting | No — you implement it | Built-in |

The tradeoff: Socket.io clients can only talk to Socket.io servers. You can't use a raw WebSocket client to connect to a Socket.io server — the protocol is different.

### The Socket.io Handshake (What Actually Happens)

When a client calls `io('wss://api.mynextvibe.com/messaging')`:

1. **Polling handshake** — the client sends a regular HTTP GET to `/socket.io/?EIO=4&transport=polling`. The server responds with a session ID (`sid`) and connection parameters.
2. **Namespace connection** — the client sends a namespace connect packet for `/messaging`.
3. **Transport upgrade** — the client sends an HTTP `Upgrade: websocket` request. The server confirms. The TCP connection is now a WebSocket.
4. **Your `handleConnection` fires** — this is where JWT validation happens. If you call `client.disconnect()` here, the client sees `connect_error`.

This means Socket.io CORS applies to step 1 (polling HTTP request), NOT to the WebSocket upgrade itself. If your CORS blocks the initial polling request, the whole connection fails.

### Why the Connection Was Failing in This Codebase

The browser console showed:

```
[chat] socket status → disconnected   ← initial state
[chat] join effect: socket not available yet   ← component fired before socket ready
[chat] socket status → disconnected
[chat] join effect: socket not available yet
[chat] socket status → error   ← connection attempt FAILED
```

`status → error` means `connect_error` — the server rejected the handshake. Our `handleConnection` calls `client.disconnect()` when no token is present. The frontend was creating the socket at component mount before the access token was loaded into state, so `auth: { token: undefined }` was sent. Server sees no token → disconnect → client gets `error`.

### The Room System — Why Real-Time Can Still Fail After Connecting

Connecting to a Socket.io namespace just means you have a pipe to the server. You are not in any room yet. `server.to('room').emit(...)` only sends to sockets that have joined that room via `socket.join('room')`.

In this codebase, the DM flow requires:

```
1. User A connects to /messaging namespace   ← has a pipe
2. User A emits 'join:dm' { conversationId }  ← enters the room
   Server: client.join('dm:{conversationId}')
3. User B connects to /messaging namespace   ← has a pipe
4. User B emits 'join:dm' { conversationId }  ← enters the room
5. User A emits 'send:dm' { conversationId, body }
   Server: server.to('dm:{conversationId}').emit('new:dm', message)
6. User B receives 'new:dm'   ← because they're in the room
```

If User B never emits `join:dm`, they are connected but not in any room. Step 6 never reaches them. They'd have to poll the REST API to see new messages. **This is exactly why messages weren't real-time** — the frontend was connecting but not emitting `join:dm`. (See `learning/frontend/06-realtime.md` Part 36 for the exact frontend race condition — `isConnected` React state vs socket.io's own `"connect"` event — that caused this.)

### NestJS + Socket.io Setup (Server Side)

**Install:**
```bash
pnpm add @nestjs/websockets @nestjs/platform-socket.io socket.io
```

**The gateway:**
```typescript
import {
  WebSocketGateway, WebSocketServer,
  SubscribeMessage, MessageBody, ConnectedSocket,
  OnGatewayConnection, OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { JwtService } from '@nestjs/jwt';

@WebSocketGateway({
  namespace: '/messaging',        // clients connect to /messaging, not root
  cors: { origin: '*' },          // Socket.io CORS — separate from app CORS
  transports: ['websocket'],      // optional: skip polling, go straight to WS
})
export class MessagingGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server!: Server;  // ! = definite assignment (NestJS sets this)

  constructor(private jwtService: JwtService) {}

  // Fires when ANY client connects — validate here
  async handleConnection(client: Socket) {
    const token = client.handshake?.auth?.token;
    if (!token) {
      client.emit('exception', { message: 'No token provided' });
      client.disconnect();
      return;
    }
    try {
      const payload = this.jwtService.verify(token, { secret: process.env.JWT_ACCESS_SECRET });
      client.data.user = payload;   // store on client, accessible in all handlers
    } catch (err: any) {
      client.emit('exception', { message: 'Invalid or expired token' });
      client.disconnect();
    }
  }

  handleDisconnect(client: Socket) {
    // clean up anything tied to client.id
  }

  @SubscribeMessage('join:dm')
  handleJoin(@ConnectedSocket() client: Socket, @MessageBody() data: { conversationId: string }) {
    client.join(`dm:${data.conversationId}`);
    return { event: 'joined:dm', data };  // acknowledgement back to emitter
  }

  @SubscribeMessage('send:dm')
  async handleSend(@ConnectedSocket() client: Socket, @MessageBody() data: any) {
    const senderId = client.data.user?.sub;
    if (!senderId) return { error: 'Unauthorized' };

    const message = await this.saveMessage(data);

    // emit to everyone in the room (including sender)
    this.server.to(`dm:${data.conversationId}`).emit('new:dm', message);

    // emit to everyone EXCEPT sender:
    // client.to(`dm:${data.conversationId}`).emit('new:dm', message);

    return message;  // acknowledgement to the sender
  }
}
```

**The module:**
```typescript
@Module({
  imports: [AuthModule],   // AuthModule exports JwtModule → JwtService injectable
  providers: [MessagingGateway, MessagingService],
})
export class MessagingModule {}
```

**Register in AppModule** — just import `MessagingModule`. NestJS handles registering the gateway automatically.

### Client Side (React / React Native)

**Install:**
```bash
npm install socket.io-client
```

**The golden rule: only connect after the token is ready.**

```typescript
import { io, Socket } from 'socket.io-client';
import { useEffect, useRef } from 'react';

function useMessagingSocket(accessToken: string | null, conversationId: string) {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!accessToken) return;  // ← WAIT for token. Don't connect without it.

    const socket = io('wss://api.mynextvibe.com/messaging', {
      auth: { token: accessToken },      // sent in handshake, NOT as a header
      transports: ['websocket'],          // skip polling for lower latency
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socketRef.current = socket;

    // Join the room immediately after connection is confirmed
    socket.on('connect', () => {
      console.log('connected, joining room');
      socket.emit('join:dm', { conversationId });
    });

    socket.on('new:dm', (message) => {
      // update your local messages state here
    });

    socket.on('exception', (err) => {
      // server rejected with reason — token expired, etc.
      console.error('socket rejected:', err.message);
    });

    socket.on('connect_error', (err) => {
      // connection failed entirely
      console.error('connect_error:', err.message);
    });

    // CRITICAL: disconnect and recreate on cleanup
    // this runs when: component unmounts, accessToken changes, conversationId changes
    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [accessToken, conversationId]);  // ← recreate socket when token or conversation changes

  return socketRef;
}
```

(This is the earlier, simpler version of the hook. See `learning/frontend/06-realtime.md` for the production `useSocket` hook this evolved into, and the event-driven join fix for the race condition described above.)

### `server.to()` vs `client.to()` — The Difference

```typescript
// server.to() — sends to ALL sockets in the room, INCLUDING the sender
this.server.to('dm:abc').emit('new:dm', message);

// client.to() — sends to all sockets in the room EXCEPT the sender
client.to('dm:abc').emit('typing:dm', { userId });
```

Use `server.to()` for messages (sender should also see the message confirmed). Use `client.to()` for indicators like typing (you don't need to tell yourself you're typing).

### Namespaces vs Rooms

These are two different levels of isolation:

**Namespace** (`/messaging`, `/notifications`) — a completely separate channel. Sockets on different namespaces cannot communicate. Each namespace has its own set of rooms, events, and middleware. A client must explicitly connect to a namespace: `io('/messaging')`.

**Room** (`dm:abc`, `chat:eventId:PRE_EVENT`) — a group within a namespace. A socket can join multiple rooms. `server.to('room').emit(...)` reaches everyone in the room. Rooms don't need to be declared — they're created automatically when the first socket joins and destroyed when the last one leaves.

Think of it like: namespaces are different apps, rooms are groups within an app.

### Common Socket.io Bugs and What They Mean

| Symptom | Cause |
|---|---|
| `status → error` immediately | Server rejected handshake — usually no/invalid token |
| Connected but no real-time messages | User never emitted `join:room` — not in the room |
| Messages received twice | Both `server.to()` (sends to all) and `return message` (acknowledgement) — sender gets two copies |
| Works in Postman/test, fails in browser | CORS issue — Socket.io CORS and app CORS may need to match |
| Works locally, fails on deploy | `ws://` vs `wss://` — production needs `wss://` |
| Second user can't connect | Frontend uses socket as a singleton — old user's socket is reused with wrong token |
| `@UseGuards` not working in gateway | Guards work on `@SubscribeMessage` handlers but NOT on `handleConnection` — validate JWT there manually |

---

## Part 45 — WebSocket Error Handling: Why Throwing Doesn't Work the Same Way

### HTTP vs WebSocket Error Propagation

In HTTP handlers, you throw and NestJS handles it:

```typescript
@Get(':id')
async getEvent(@Param('id') id: string) {
  const event = await this.eventsService.findById(id);
  if (!event) throw new NotFoundException('Event not found');
  // NestJS catches this, returns { statusCode: 404, message: "Event not found" }
}
```

In WebSocket handlers (`@SubscribeMessage`), throwing behaves differently. NestJS does catch it and converts it to an `exception` event emitted back to the sender — but only if you use `WsException`:

```typescript
@SubscribeMessage('send:dm')
async handleSend(@ConnectedSocket() client: Socket) {
  throw new WsException('Unauthorized');
  // Client receives: socket.on('exception', { message: 'Unauthorized' })
}
```

If you throw a regular HTTP exception (`NotFoundException`, `ForbiddenException`) inside a WebSocket handler, NestJS may or may not handle it gracefully depending on configuration. The safest pattern in this codebase is to **return an error object instead of throwing**:

```typescript
@SubscribeMessage('send:dm')
async handleSendDm(@ConnectedSocket() client: Socket, @MessageBody() data: any) {
  const senderId = client.data.user?.sub;
  if (!senderId) return { error: 'Unauthorized' };  // return, don't throw

  // business logic errors — also return
  const conversation = await this.messagingService.findConversation(data.conversationId);
  if (!conversation) return { error: 'Conversation not found' };

  const message = await this.messagingService.saveMessage(...);
  this.server.to(`dm:${data.conversationId}`).emit('new:dm', message);
  return message;  // acknowledgement to sender
}
```

The returned value from a `@SubscribeMessage` handler is sent back to the **emitting client only** as an acknowledgement. The broadcast (`this.server.to(...).emit(...)`) goes to the room. These are two different channels.

### The `exception` Event Convention

When the server emits `exception` back to the client, the client should listen for it globally:

```typescript
socket.on('exception', (error) => {
  console.error('Server error:', error.message);
  // handle the error in UI
});
```

In this codebase, `handleConnection` emits `exception` before disconnecting an unauthorized client — giving the frontend a chance to show a "session expired" message rather than silently failing.

### `handleConnection` Errors Are Different

Errors thrown or returned from `handleConnection` do NOT use the `exception` event — because the client isn't fully connected yet. The only way to communicate a rejection reason during connection is:

```typescript
async handleConnection(client: Socket) {
  if (!token) {
    client.emit('exception', { message: 'No token' });  // emit before disconnect
    client.disconnect();  // then disconnect
  }
}
```

This is why `handleConnection` in this codebase emits `exception` first, then calls `disconnect()`. Without the emit, the client just sees a generic `connect_error` with no reason.

## Part 46 — The Producer/Consumer Split: Why "Notifications Don't Show Up"

A notification system has two halves, and they fail independently:

- **The consumer side** — the DB table, the `NotificationsGateway` that pushes over WebSocket, the frontend page that lists them, the socket listener. This is the *plumbing*: it delivers whatever it's given.
- **The producer side** — the actual `this.notifications.create(...)` calls scattered across the feature services (postcards, games, payments...) that *put something into* the plumbing.

When "I'm not seeing notifications for likes/comments," the instinct is to debug the socket or the frontend. But the plumbing was fine — the bug was that **the producer side never existed**. `PostcardsService.toggleLike` and `addComment` wrote their rows and returned, never calling `notifications.create`. The `LIKE`/`COMMENT` enum values existed, the frontend page worked, the gateway worked — the event was simply never *produced*.

Debugging lesson: when an end-to-end pipeline is silent, find which *end* is broken before poking the middle. A quick `grep -rn "notifications\." src/modules/postcards` returning **nothing** was the whole diagnosis — the service didn't even inject `NotificationsService`.

### The self-notification guard lives in `create()`, not the caller

`NotificationsService.create()` starts with:

```typescript
if (data.actorId && data.recipientId === data.actorId) return null;
```

So callers can fire notifications unconditionally — liking your own postcard, commenting on your own — and `create()` quietly no-ops. The producer doesn't need to re-check "is the actor also the recipient?". This is why `toggleLike` can just pass `recipientId: postcard.authorId, actorId: userId` without an `if`.

### Best-effort producers: `.catch(() => null)`

Every producer call is `await this.notifications.create({...}).catch(() => null)`. A notification is a *side effect* of the real action (the like was already saved). If Resend is down or the notification insert fails, the user's like must still succeed. Never let a best-effort side channel throw into the main flow.

## Part 47 — Rich Transactional Emails vs. In-App Notifications

`notifyGameReward` (added for game winners) does **both**: an in-app `create()` *and* a full HTML `sendEmail()`. They serve different moments:

- In-app notification → the user is already in the app; a lightweight row is enough.
- Email → reaches the user when they're *not* in the app, and carries the call-to-action ("Redeem Your Prize" → `${FRONTEND_URL}/rewards`).

Two small helpers keep the email human:
- `ordinal(n)` → `1 → "1st", 2 → "2nd", 23 → "23rd"` for "You finished 2nd".
- `rewardTypeLabel(type)` → a `Record<RewardType, string>` mapping the enum to display copy (`COUPON → "Coupon"`). Using a `Record<RewardType, string>` (not a loose object) means **adding a new `RewardType` to the enum is a compile error here until you give it a label** — the type system forces you to handle it.

### Deduping when winners are a subset of a notified group

`distributeRoundRewards` used to notify *every* ranked player with a generic `GAME_RESULT`. Now winners get the richer reward notification+email instead. To avoid a winner getting *two* `GAME_RESULT` rows, collect winner ids in a `Set` and notify only the non-winners generically:

```typescript
const winnerUserIds = new Set<string>();
// ...create reward + notifyRewardWinner(...); winnerUserIds.add(id)...
for (const entry of entries) {
  if (entry.userId && !winnerUserIds.has(entry.userId)) {
    this.notifications.create({ /* generic GAME_RESULT */ }).catch(() => null);
  }
}
```

---

## The general version of this
- [[architecture/02-building-blocks/04-messaging-and-async|Messaging & Async]] — push vs pull as a design choice
- [[foundations/networking/11-http-evolution|HTTP evolution]] — what WebSockets sit on top of
- [[foundations/networking/06-tcp-connection-lifecycle|TCP lifecycle]] — why idle connections die and you need heartbeats

↑ [[projects/README|All projects and the domains they exercise]]

---

## Part N — Push notifications for the mobile app (2026-08-22, moved to FCM 2026-09-02)

The gateway in this file solves half the problem. A WebSocket reaches a user
whose app is **open and in the foreground** — which is exactly when they least
need to be told something happened. Push notifications are the other half: they
reach a phone that's locked, backgrounded, or has the app killed.

### The delivery chain, and where you plug into it

This is the mental model to hold, because both designs below are the same
picture with a different entry point:

```
your server → [FCM (Android) / APNs (iOS)] → the device
```

You never talk to a phone directly. You hand a message to Google's or Apple's
service, which owns the persistent connection to the device. The only question
is whether you talk to those two yourself, or let a broker do it:

```
direct:  server → firebase-admin → FCM ─┐
                                        ├→ device
         server → APNs (key, .p8, JWT) ─┘

via Expo: server → expo-server-sdk → Expo → FCM/APNs → device
```

### We built it on Expo first, then switched to direct FCM

Worth keeping both halves of this, because the reasoning didn't turn out to be
wrong — the priorities changed.

**The original call (2026-08-22):** the app is Expo, so it already gets a token
from `getExpoPushTokenAsync()`. Expo brokers both platforms behind one token
format and one API, so we skipped the APNs signing key, the service account, and
two sets of error semantics. The `FIREBASE_*` env vars sat stubbed and unused.

**The switch (2026-09-02):** dropped the broker to stop depending on Expo's
service being up. The cost is real and it lands almost entirely on the *client*:

- Expo Go can't receive push any more — FCM needs native config, so the app needs
  a development build with `google-services.json` / `GoogleService-Info.plist`.
- iOS needs an APNs auth key uploaded to Firebase. Without it FCM accepts your
  sends and delivers **nothing, with no error** — precisely the failure mode the
  first decision was avoiding.
- The client must send `messaging().getToken()`. On iOS,
  `getDevicePushTokenAsync()` returns the raw **APNs** token, which FCM won't
  accept as a registration token — it registers fine and fails on every send.

The general lesson: **a broker is not a lazy choice.** Removing one buys you
independence and costs you the integration work it was doing on your behalf. Be
able to name what that work is before you decide it's worth taking on.

### Credentials: the escaped-newline trap

A service-account private key is multi-line PEM, and a `.env` file can't hold
real newlines. So the value is stored with literal `\n` and unescaped at load:

```typescript
privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
```

Skip this and the SDK fails at the *first send* with "Invalid PEM formatted
message" — not at boot, which is where you'd look for a config error.

Related, and a deliberate choice: if any of the three `FIREBASE_*` vars are
missing, `PushService` logs a warning and sets `messaging` to `null` rather than
throwing. Push then no-ops. A local environment shouldn't need a Firebase
service account to run the API, and an unconfigured optional subsystem shouldn't
take down the routes that merely *trigger* it.

### Storing tokens: key on the token, not on the user

```prisma
model DeviceToken {
  token    String         @unique
  userId   String
  platform DevicePlatform @default(UNKNOWN)
}
```

The non-obvious part is `@unique` on `token` rather than `@@unique([userId, token])`.

A push token identifies **an app install on a device**, not a person. One person
has several devices, and — the case that bites — one device gets signed into
different accounts over its life. Upserting on the token means re-registering
after a new sign-in *moves* the row to whoever is signed in now:

```typescript
return this.prisma.deviceToken.upsert({
  where: { token: dto.token },
  create: { userId, token: dto.token, platform },
  update: { userId, platform, lastUsedAt: new Date() },
});
```

Key it on `(userId, token)` instead and you get a second row, the old row
survives, and the previous user's notifications keep arriving on a phone they
no longer own. **When a row represents a physical thing, the identifier of that
thing is the key — not the identifier of whoever currently holds it.**

### Dead tokens must be deleted, or they accumulate forever

`sendEachForMulticast` returns a `BatchResponse` whose `responses` array is
**positionally aligned** with the tokens you sent. That alignment is the only
thing tying a result back to a token — nothing in the response identifies it:

```typescript
responses.forEach((response, index) => {
  if (response.success) return;
  const code = response.error?.code;
  if (code && DEAD_TOKEN_CODES.has(code)) dead.push(chunk[index]);
});
```

Without this cleanup the table only grows, and every future notification pays to
retry addresses guaranteed to fail.

**The trap: not every error means a dead token.** The obvious set to delete on is
"anything that looks like a bad token", and that's how you empty your own
database. `messaging/invalid-argument` is returned both for a bad token *and*
for a malformed message payload. Include it, ship one bad payload shape, and
every token in the batch fails with it — so you delete every device row you have,
and push stays silently broken for every user until each phone happens to
re-register. So the delete set is only the two codes that are unambiguously
token-scoped:

```typescript
const DEAD_TOKEN_CODES = new Set([
  'messaging/registration-token-not-registered',  // uninstalled / revoked
  'messaging/invalid-registration-token',         // malformed
]);
```

**Generalise it:** before writing a rule that deletes data in response to an
error code, ask what *else* returns that code. An error that can be caused by
your own bug must never trigger destructive cleanup.

**Also gone in the move:** Expo's two-stage ticket/receipt model. Expo accepted a
message (ticket) and reported real delivery ~15 min later (receipt), and we never
polled receipts — so some dead tokens lingered. FCM has no equivalent second
stage, so that gap closed by accident rather than by design.

### Validation got weaker, and that's not fixable

Expo tokens were checkable: `Expo.isExpoPushToken()` matched the
`ExponentPushToken[...]` wrapper. FCM tokens are **opaque** — no documented
format, and the length varies by platform and SDK version. So the strongest
honest check is:

```typescript
typeof token === 'string' && token.length >= 32 && !/\s/.test(token)
```

Anything stricter starts rejecting legitimate tokens the next time Google
changes the format. The consequence: an iOS APNs token sent by mistake passes
registration and only fails at send time. **When you can't validate at the
boundary, you have to detect at use — which is exactly what the dead-token
cleanup above is for.**

There's one exception worth seeing, because it's where the two rules collide.
The table still held old `ExponentPushToken[...]` values, and those are ~41
characters with no whitespace — so the loose check waves them through, and FCM
may reject them as `invalid-argument`, which the rule above deliberately does
*not* delete on. Result: dead rows retried on every notification, forever. So
that one known-dead format is matched explicitly:

```typescript
const EXPO_TOKEN_PATTERN = /^Expo(nent)?PushToken\[/i;
```

**The lesson: "detect at use" only works if the failure is actually
distinguishable.** When you already know a specific value is dead, encode that
knowledge directly instead of hoping the error path infers it. This is also the
whole data migration — no SQL, no backfill script, just a filter that empties
the stale rows on first send.

### Data payloads are string→string only

FCM will not carry a number, a boolean, or a nested object in `data`. Everything
gets encoded on the way out:

```typescript
out[key] = typeof value === 'string' ? value : JSON.stringify(value);
```

Today every field is already a string, so this does nothing visible — it's there
so that adding a numeric field later fails on the client's `JSON.parse` rather
than silently shipping `"[object Object]"`.

### Chunking is mandatory, not an optimisation

FCM rejects a multicast of more than 500 tokens. Unlike `expo-server-sdk`, which
had `chunkPushNotifications()`, `firebase-admin` gives you no helper — you slice
yourself:

```typescript
for (let i = 0; i < valid.length; i += FCM_MULTICAST_LIMIT) {
  const chunk = valid.slice(i, i + FCM_MULTICAST_LIMIT);
}
```

Skipping this works fine in dev with two test devices and fails the day a real
event fans out.

**Use `sendEachForMulticast`, not the older `sendMulticast`.** The former sends
one request per token, so a single bad token fails only itself; the latter failed
the entire batch. The per-token isolation is what makes the dead-token cleanup
above safe to run.

### A deprecation to know about

`firebase-admin` 14 deprecates token-based sending in favour of **FIDs**
(Firebase Installation IDs) and will remove `tokens` in the next major:

```typescript
export interface MulticastMessage { fids?: string[]; tokens: string[]; }  // deprecated
export interface FidMulticastMessage { fids: string[]; }                  // the future
```

We stayed on `tokens` deliberately — a FID is a *different identifier* that the
client would have to fetch and register instead, so migrating is client-led work,
not a server-side find-and-replace. **Worth noticing how this was found:** by
reading the installed `.d.ts` files, not by recalling the API. For a library
that's had a major version recently, the types on disk are the primary source.

### Fire-and-forget, deliberately

Both channels fan out from the same funnel in `persist()`:

```typescript
this.gateway.pushToUser(data.recipientId, notification);

void this.push.sendToUser(recipientId, payload).catch((e) => this.logger.error(...));
```

`void` plus `.catch` says "start this, don't wait, don't let it throw". An HTTP
round-trip to FCM must not sit inside the request that triggered the
notification — someone liking a post shouldn't wait on Google to get their 200.
And a push failure must not roll back an in-app notification that was written
successfully.

The `void` operator is how you tell both a reader and the `no-floating-promises`
lint rule that the promise is unawaited on purpose. `.catch()` is still required:
an unhandled rejection in a floating promise can take the process down.

### Both channels fire, and the app dedupes

A foregrounded user gets the socket event *and* the push. Rather than trying to
know on the server whether a socket is currently live (it's racy — a connection
can drop between the check and the send), the push payload carries the
notification id and the app drops what it has already shown:

```typescript
data: { notificationId, type, targetType, targetId }
```

**Send both and let the receiver deduplicate**, rather than trying to be clever
server-side about which channel to use. The client is the only place that knows
what it actually displayed.

That `data` object is also what deep linking runs on — the app routes on
`targetType`/`targetId` rather than parsing the body text.

### The preference column that nothing read

`UserPreference.pushNotifications` existed from the start and no code had ever
checked it. `sendToUser` now does:

```typescript
if (preference && !preference.pushNotifications) return;
```

Note `preference &&` — a missing preference row means "send", not "don't". A
user whose row was never created should still get notifications; only an
explicit `false` suppresses them. Worth being deliberate about which way a
missing setting falls.
