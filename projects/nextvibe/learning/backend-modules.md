# NextVibe — Backend Domain Modules

Split out from the original flat `learning.md` (kept untouched in the project root). See also
`learning/backend-core.md` (NestJS/Prisma fundamentals and cross-cutting gotchas),
`learning/backend-auth.md`, `learning/backend-realtime.md` (WebSocket gateway internals),
`learning/backend-games-ai.md` (AI generation + anonymous play — a deeper dive on top of the
Games Module overview below), `learning/sys-design.md` (the schema this all sits on), and
`learning/devops.md`.

This file walks through each feature-domain module in the backend: Events, Games (core
mechanics), Billing (pricing), Payments (webhook-driven Juicyway flow), Notifications
(real-time + email), Social (follows/likes/comments), Discovery + Analytics, Messaging (DMs +
event chat REST/gateway split), Storage, Admin, Pledges (platform donations), and the Ercaspay
payment internals + notification coverage audit that were added later.

---

## Part 9 — The Events Module

Events are the core domain. Let's trace the full lifecycle.

### Event Lifecycle

```
DRAFT → PUBLISHED → ENDED / CANCELLED
```

A DRAFT event exists but is invisible to attendees. Before publishing:
- An organizer adds ticket tiers, game sessions, VibeTags
- If the event has games or VibeTags, they pay a platform fee (billing flow)
- On `PATCH /events/:id/status` with `{ status: "PUBLISHED" }`, the event goes live

After publication, the event is visible in discovery. Attendees can RSVP or buy tickets. Games unlock. VibeTags activate.

### The RSVP vs Ticket Distinction

This is subtle but important. RSVPs are for free events or to express interest. Tickets are paid entry passes.

An event can have both: attendees who bought VIP tickets AND attendees who got free RSVPs for the general area. The RSVP and Ticket systems are independent — you can RSVP without buying a ticket and vice versa.

The `CheckIn` table bridges both: both ticket holders and RSVP holders can check in at the venue.

### Events Service: Soft Deletes

The codebase uses `deletedAt` on game sessions:
```typescript
where: { id: sessionId, deletedAt: null }
```

This is a soft delete — instead of removing the row, you set a timestamp. Why:
- Deleted data can be recovered
- Analytics still work (you can count how many sessions were deleted)
- Foreign key references don't break

The downside: every query must include `deletedAt: null` or you'll accidentally show deleted records. This is easy to forget and is a common source of bugs. (See `learning/backend-core.md` Part 20 — soft delete is not applied consistently across the domain.)

---

## Part 10 — The Games Module (Most Complex Logic)

The games module has the most business logic in the codebase. Understanding it teaches you how to model complex state machines. (For the AI generation side of Games and the anonymous/guest play system, see `learning/backend-games-ai.md`.)

### The Payment Gate

When an organizer creates a game session:
1. If within their paid quota → session is created with `status: PENDING`, ready to use
2. If over quota → session is created with `status: PENDING` but `paymentRequired: true` via the linked `OrganizerPayment`

The status lifecycle enforces the payment gate:

```
PENDING → UNLOCKED (payment completed) → ACTIVE (organizer activates) → ENDED
```

You cannot skip from PENDING to ACTIVE:
```typescript
if (dto.status === 'ACTIVE' && session.status !== 'UNLOCKED') {
  throw new BadRequestException('Game session must be unlocked before activation');
}
```

This is a **state machine**. The business rule ("you must pay before you can run the game") is encoded as a state transition rule, enforced in application code. This is more reliable than checking "was this paid for?" on every activation — because the state itself encodes whether payment happened.

### Viral Participation via Share Tokens

```typescript
shareToken: nanoid(10)  // generates: "V1StGXR8_Z"
```

A 10-character `nanoid` gives you ~1 quadrillion possible values — effectively impossible to guess. This token becomes the public join link. When someone joins via the token, `isViral = true` is set:

```typescript
async joinSessionByToken(token: string, userId: string) {
  const session = await this.findSessionByToken(token);
  return this.joinSession(session.id, userId, true);  // isViral = true → isSpectator
}
```

Spectators can play the game but are excluded from:
- The leaderboard
- Rewards
- Session ranks

**Why allow spectators at all?** It drives engagement and virality. People who weren't at the event can still play, share results, and bring attention back to the event. They just can't win prizes.

### Score Calculation

```typescript
private calculateScore(gameType, config, dto): number {
  switch(gameType) {
    case 'TRIVIA': // index-based: user submits option index, compare to correctAnswerIndex
    case 'WORD_PUZZLE': // string-based: normalize case and whitespace, compare
    case 'THIS_OR_THAT': // participation-based: any answer gets points
  }
}
```

Different game types score differently. The key insight: the correct answer is stored in the `config` JSON column, server-side. The client never sees it. This prevents cheating — clients can't inspect the questions JSON to find the answer before submitting.

**Trade-off of storing questions as JSON:** You get flexibility (different question shapes per game type) but lose queryability. You can't do `WHERE question.points > 10` without JSON path operators. For a gaming feature, this trade-off is fine — you query sessions, not individual questions.

(See `learning/backend-games-ai.md` Part 53 and Part 56 for later changes to this scoring logic — a serialization bug in `WORD_PUZZLE` config, and the pivot of `THIS_OR_THAT` from a participation game to a real True/False knowledge game.)

### Reward Distribution

When a round ends:
1. Query all `GameEntry` rows for that round, ordered by score DESC, completedAt ASC (ties broken by who finished first)
2. For each `GameRewardTier`, find the winner at that rank
3. Create a `Reward` record

```typescript
for (const tier of round.rewardTiers) {
  const winnerEntry = entries[tier.rank - 1];  // rank 1 = entries[0]
  if (winnerEntry) {
    await this.prisma.reward.create({ ... });
  }
}
```

The `entries[tier.rank - 1]` trick: array indices are 0-based, ranks are 1-based. Rank 1 = index 0.

**Loop bug:** The rewards are created in a sequential `for...of` loop with individual `await`s. If there are 10 reward tiers, this is 10 sequential database writes. Better: `await Promise.all(rewardTiers.map(...))`. At small scale this doesn't matter; at scale it creates unnecessary latency.

---

## Part 11 — The Billing Module (Pricing Logic)

### The Price Table Pattern

```typescript
const PLAN_PRICES: Record<OrganizerPlanType, Record<EventTier, number>> = {
  VIBETAGS_SINGLE: { MICRO: 5000, SMALL: 10000, ... },
  ...
};
```

Prices are hardcoded in the service, not in the database.

**Trade-off:**
- Hardcoded: Fast (no DB query to get prices), but changing prices requires a code deploy
- Database: Flexible (admin can change prices in the dashboard), but adds a DB query to every pricing calculation

For this product, hardcoded is the right choice. Prices don't change frequently. The operational simplicity outweighs the flexibility.

### The Quote Before Payment Pattern

Before initiating any payment, a quote is calculated:

```typescript
const quote = await this.pricingService.quotePlan(organizerId, planType, tier, couponCode);
```

The quote:
1. Looks up the base price
2. Counts the organizer's events in the last 12 months → volume discount
3. Validates and applies coupon
4. Returns the breakdown: base, volumeDiscount, couponDiscount, final

The quote is shown to the user BEFORE they pay. After payment is confirmed, the same quote is recalculated and snapshotted into the `OrganizerPayment` record. This snapshot means historical payments always show what the customer was charged, even if prices change.

### Volume Discounts

```typescript
function getVolumeDiscountPercent(eventsInLast12Months: number): number {
  if (eventsInLast12Months >= 12) return 20;
  if (eventsInLast12Months >= 6) return 15;
  if (eventsInLast12Months >= 3) return 10;
  return 0;
}
```

The discount is based on `OrganizerPayment` records with status `COMPLETED` and type `PLAN_PURCHASE` in the last 12 months. This is smart: it counts events that actually got paid for, not just created.

**Race condition risk:** Two concurrent payment initiations for the same organizer could both calculate a discount based on the same event count, then both complete. Both would get the discount. This is probably acceptable — a small revenue leak at low frequency. At scale, you'd use a database lock or a more sophisticated discount calculation.

---

## Part 12 — The Payments Module (Webhook-Driven Architecture)

### The Juicyway Widget Pattern

The payment flow is:

1. Backend creates a pending payment record, returns `paymentReference`
2. **Frontend** opens the Juicyway widget directly with the public key + reference
3. User completes payment in the widget
4. Juicyway fires a **webhook** to the backend
5. Backend's webhook handler verifies and activates features

This is called **webhook-as-source-of-truth**. The webhook is the canonical confirmation of payment. The `onSuccess` callback on the widget is just for immediate UX feedback (don't make the user wait for the webhook). The actual activation always waits for the webhook.

**Why not trust the frontend's `onSuccess`?** The frontend can be tampered with. A user could fire `onSuccess` without paying. The webhook comes directly from Juicyway's servers — you verify it with an HMAC signature. It cannot be faked.

### HMAC Webhook Verification

```typescript
verifyWebhookChecksum(payload: JuicywayWebhookPayload): boolean {
  // hash the payload with your secret key
  // compare against the checksum Juicyway sent
}
```

HMAC (Hash-based Message Authentication Code) works like this: Juicyway knows your secret key. When they send a webhook, they hash the payload with your secret and include the hash. You hash the payload with your secret and compare. If the hashes match, the payload was definitely sent by someone who knows your secret — only Juicyway and you know it.

**What happens if you skip this check?** Anyone on the internet could send fake webhook payloads to your endpoint and make your backend think payments completed. Never skip webhook signature verification.

### The Idempotency Pattern

```typescript
if (payment.paymentStatus === 'COMPLETED') return;
```

This check appears in every webhook handler. If a webhook fires twice (Juicyway retries on network failures), you don't process the payment twice. The first call marks it `COMPLETED`, the second call sees `COMPLETED` and returns. This makes the handler **idempotent** — calling it multiple times has the same effect as calling it once.

Without idempotency: a user could get double the tickets, a game could be activated twice, a reward distributed twice.

### The Verify Endpoint (Polling)

```typescript
async verifyPayment(purchaseId: string) {
  switch (purchase.paymentStatus) {
    case 'COMPLETED': return { status: 'already_completed', ... };
    case 'FAILED': return { status: 'failed', ... };
    default: return { status: 'pending', ... };
  }
}
```

The frontend polls this endpoint after `onSuccess`. Why? There's a race condition: `onSuccess` fires before the webhook arrives. The frontend needs to show the user their tickets, but the webhook hasn't processed yet.

The frontend polls every second or two until status is not `pending`. This is a simple solution. The alternative — Server-Sent Events or WebSocket notification when the webhook arrives — is more elegant but more complex.

(This project later moved off Juicyway to Ercaspay for ticket/pledge/organizer-plan payments — see Part 51 below for the differences: NGN vs kobo amounts, and the multi-branch webhook dispatcher.)

---

## Part 13 — The Notifications Module (Real-Time + Email)

### Two-Layer Notification Architecture

Every notification fires in both channels:
1. **In-app** (WebSocket) — immediate delivery if user is connected
2. **Email** (Resend) — reaches the user even if they're offline

```typescript
async create(data: {...}) {
  const notification = await this.prisma.notification.create({ ... });  // persist
  this.gateway.pushToUser(data.recipientId, notification);              // real-time
  return notification;
}
```

Persistence first, then push. If the push fails, the notification still exists in the database for the next time the user opens the app.

### WebSocket Architecture: The `/notifications` Namespace

```typescript
@WebSocketGateway({ cors: { origin: '*' }, namespace: '/notifications' })
```

The gateway runs on the same process as the API but on a different Socket.io namespace. Authentication happens on connect:

```typescript
async handleConnection(client: Socket) {
  const token = client.handshake.auth?.token;
  const payload = this.jwtService.verify(token);
  client.join(`user:${payload.sub}`);  // join room named "user:UUID"
}
```

The token must be passed in the handshake `auth` object — not in HTTP headers:

```typescript
// frontend connection
const socket = io('/notifications', { auth: { token: accessToken } });
```

If the token is missing or invalid, the server calls `client.disconnect()` immediately. There is no retry — the client must reconnect with a valid token.

When a notification needs to reach user `abc`, you emit to room `user:abc`:

```typescript
this.server.to(`user:abc`).emit('notification', notification);
```

Only the socket in that room (i.e., that user's connection) receives it. This is how Socket.io rooms work: a room is a named group of connected sockets. Emitting to the room sends to all members of that group. Since room `user:abc` contains only the socket belonging to user `abc`, it is effectively a private channel.

The client side only needs to listen for one event:

```typescript
socket.on('notification', (notification) => {
  // update badge count, show toast, etc.
});
```

There is also a `ping`/`pong` keep-alive pair:

```typescript
socket.emit('ping');
socket.on('pong', () => { /* connection confirmed alive */ });
```

Use this to verify the connection is still active without waiting for a real notification to arrive.

**Scaling problem:** Socket.io rooms are in-memory in this process. If you run two API instances, a user connected to instance 1 won't receive events emitted by instance 2. The fix: Socket.io Redis adapter (the `redis.service.ts` even exposes `getClient()` for this exact reason). This is one of the first things to add when you need horizontal scaling. (See `learning/backend-core.md` Part 20 for this same gap in the wider "what's missing" list.)

(For the full generic WebSocket gateway authentication pattern — verifying the JWT, not just checking presence — see `learning/backend-realtime.md` Part 26.)

### The Actor Pattern

Every notification has:
- `recipientId` — who receives it
- `actorId` — who caused it (or `'SYSTEM'` for automated ones)
- `type` — what happened (FOLLOW, LIKE, PAYMENT_CONFIRMED, etc.)
- `targetType` + `targetId` — what it's about

This model lets the frontend render any notification format:
- `"@kingsley liked your postcard"` → actor.username + type + target
- `"Your payment was confirmed"` → type + target + no actor display

The self-action guard:
```typescript
if (data.actorId && data.recipientId === data.actorId) return null;
```
You don't notify yourself when you like your own post.

(See `learning/backend-core.md` Part 28 for the full convention on what `targetId` should point to for each notification type — including a real bug where `FOLLOW` notifications had `targetId` set to the actor instead of the target.)

### Notification Types and What Triggers Them

Every notification has a `type` and a `targetType`. The `type` describes what happened; the `targetType` describes what entity it happened to. Together they tell the frontend exactly what link to show when the user taps the notification.

| Type | What triggers it | targetType | targetId points to |
|---|---|---|---|
| `FOLLOW` | User A followed User B | `USER` | actor's user ID |
| `LIKE` | Someone liked a postcard | `POSTCARD` | postcard ID |
| `COMMENT` | Someone commented on a postcard | `POSTCARD` | postcard ID |
| `TAG` | User was tagged in content | `POSTCARD` | postcard ID |
| `RSVP` | RSVP confirmed or waitlisted | `EVENT` | event ID |
| `GAME_RESULT` | Game round result available | `GAME` | game session ID |
| `EVENT_REMINDER` | Cron job fires before event starts | `EVENT` | event ID |
| `CHECK_IN` | User checked in at event | `EVENT` | event ID |
| `PAYMENT_CONFIRMED` | Payment webhook confirmed success | `PAYMENT` | payment record ID |
| `PAYMENT_FAILED` | Payment webhook reported failure | `PAYMENT` | payment record ID |
| `EVENT_PUBLISHED` | Organizer's event went live | `EVENT` | event ID |
| `TICKET_PURCHASED` | Ticket purchase confirmed | `TICKET` | purchase ID |
| `GAME_UNLOCKED` | Game session unlocked after payment | `GAME` | game session ID |
| `VIBETAG_ACTIVATED` | VibeTags activated for an event | `EVENT` | event ID |

### Notification Object Shape

What the `notification` socket event delivers, and what `GET /v1/notifications` returns per item:

```typescript
interface Notification {
  id: string;
  recipientId: string;
  actorId?: string;        // undefined means system-generated (cron, payment webhook)
  type: NotificationType;
  targetType: NotificationTarget;
  targetId: string;
  isRead: boolean;         // always false on delivery via socket
  createdAt: string;       // ISO 8601
  actor?: {                // populated on REST fetch; may be absent on socket push
    id: string;
    username: string;
    displayName?: string;
    avatarUrl?: string;
  };
}
```

### Notification REST Endpoints

The socket delivers notifications in real time, but it is not the source of truth. On app load, the client fetches history and the unread count via REST:

```
GET  /v1/notifications?page=1&limit=50   — paginated list; response includes meta.unreadCount
POST /v1/notifications/:id/read          — mark one notification as read
POST /v1/notifications/read-all          — mark all unread as read → { updatedCount: number }
```

The correct integration pattern: on app open, call `GET /v1/notifications` to initialise the badge count from `meta.unreadCount`. Then connect the socket and listen for `notification` events to increment the badge in real time. When the user opens the notification panel, call `POST /v1/notifications/read-all` and reset the badge to zero.

(Note: `learning/backend-core.md` Part 30 covers a real HTTP-method mismatch bug on the `:id/read` endpoint — the controller used `@Post` while some clients expected `PATCH`, producing a misleading 404.)

---

## Part 14 — The Social Module

### The Follow System — How Social Graphs Work

A social graph is the network of relationships between users. "A follows B" is an edge in that graph. This project stores it in the `Follow` table:

```
follows: id | followerId | followingId | createdAt
```

`followerId` — the person doing the following ("I follow you")
`followingId` — the person being followed ("you are followed by me")

So if Kingsley follows Ada: `{ followerId: "kingsley-id", followingId: "ada-id" }`.

**Getting followers** (who follows me?) — query where `followingId = myUserId`:
```typescript
this.prisma.follow.findMany({ where: { followingId: userId } })
// returns all rows where someone follows me
```

**Getting following** (who do I follow?) — query where `followerId = myUserId`:
```typescript
this.prisma.follow.findMany({ where: { followerId: userId } })
// returns all rows where I am the follower
```

That's why the `Follow` table has two separate indexes — `@@index([followingId])` for the "followers" query and `@@index([followerId])` for the "following" query. Without these, both queries do a full table scan.

**Mutual followers (getMutuals)**

A "mutual" means: I follow you AND you follow me. This is used in this project to gatekeep direct messaging — you can only DM users who follow you back.

The logic:
```typescript
async getMutuals(userId: string) {
  // Step 1: get everyone I follow
  const following = await prisma.follow.findMany({
    where: { followerId: userId },
    select: { followingId: true },
  });
  const followingIds = following.map(f => f.followingId);

  // Step 2: from that list, find who also follows me back
  const mutuals = await prisma.follow.findMany({
    where: {
      followingId: userId,          // they follow me
      followerId: { in: followingIds },  // AND I follow them
    },
  });
}
```

Two queries: get my following list, then find the intersection where they also follow me. This is an O(n) operation where n is your following count. At scale (millions of follows), you'd use a Redis set intersection instead.

**The follow action itself:**

```typescript
async follow(followerId: string, followingId: string) {
  // guard: can't follow yourself
  if (followerId === followingId) throw new BadRequestException('...');

  // upsert: if already following, do nothing (idempotent)
  await prisma.follow.upsert({
    where: { followerId_followingId: { followerId, followingId } },
    create: { followerId, followingId },
    update: {},
  });

  // check if the follow is mutual (do they also follow me?)
  const reverseFollow = await prisma.follow.findUnique({
    where: { followerId_followingId: { followerId: followingId, followingId: followerId } },
  });

  return { following: true, isMutual: !!reverseFollow };
}
```

The `upsert` with empty `update: {}` is the idempotency pattern for follows — calling follow twice has the same result as calling it once. No duplicate rows, no error.

After following, a notification fires to the person being followed (wired up in `UsersService` → `NotificationsService`).

### Polymorphic Design for Likes and Comments

Instead of `EventLike`, `PostcardLike`, `EventComment`, `PostcardComment` tables (four tables), the design uses:

```
likes: id | userId | targetType | targetId
comments: id | userId | targetType | targetId | body
```

Adding a new content type (e.g., `GameResult`) that can be liked doesn't require a new table — just a new enum value in `LikeTarget`.

The cost: no foreign key constraint. The application must validate that `targetId` refers to a real entity. Both `LikesService` and `CommentsService` have `verifyTarget` methods for this.

### Counter Cache Pattern

```typescript
await this.prisma.postcard.update({
  where: { id: targetId },
  data: { likeCount: { increment: value } },
});
```

`likeCount` is a counter cache — a denormalised count stored directly on the postcard. Every time you like/unlike, you update both the `likes` table AND the postcard's count.

**Why?** `SELECT COUNT(*) FROM likes WHERE targetId = 'x'` on every postcard fetch is expensive at scale. If a postcard has 50,000 likes and you display 20 postcards on a feed, that's 20 COUNT queries. With a counter cache, you read one integer per postcard — the count is already there.

**Risk:** The counter and the actual rows can drift out of sync (e.g., if a background job deletes old likes without decrementing the counter). A periodic reconciliation job (`SELECT COUNT(*) ... GROUP BY targetId`) can fix drift.

---

## Part 15 — The Discovery Module

Discovery is how users find events. The key query:

Without seeing the implementation, but based on the schema indices (`@@index([status])`, `@@index([startsAt])`, `@@index([organizerId])`), the discovery query likely filters on:
- `status = 'PUBLISHED'`
- `startsAt >= now()` (upcoming events)
- Optionally: category, location, date range

**What's missing from this schema for proper discovery:** A full-text search index on `name` and `description`. PostgreSQL has native full-text search (`tsvector`/`tsquery`) but it requires additional setup. For a production product, you'd want either PostgreSQL full-text search or Elasticsearch for fuzzy event name search.

---

## Part 15b — Analytics

The project has an `analytics.service.ts` file. Analytics answers questions like:
- How many tickets were sold for this event?
- What's the revenue for this organizer this month?
- How many users signed up this week?
- Which events have the most RSVPs?

**How analytics is built on top of the existing schema:**

Every number you'd want to track is derivable from the data already in the database:

```sql
-- Total revenue for an organizer this month
SELECT SUM(final_amount) FROM organizer_payments
WHERE organizer_id = ? AND payment_status = 'COMPLETED'
AND paid_at >= DATE_TRUNC('month', NOW());

-- Ticket sales by tier for an event
SELECT tt.name, COUNT(t.id) as sold, SUM(tt.price) as revenue
FROM tickets t
JOIN ticket_tiers tt ON t.ticket_tier_id = tt.id
WHERE t.event_id = ?
GROUP BY tt.name;

-- Daily new user signups
SELECT DATE(created_at) as day, COUNT(*) as signups
FROM users
GROUP BY day
ORDER BY day DESC;
```

**The trade-off with running analytics on your main database:**

Heavy analytics queries scan a lot of rows. Running them on the same PostgreSQL instance that serves your API can slow down user-facing requests. At scale, the solution is:
- A **read replica** — a copy of your database that only accepts reads. Analytics queries run there, leaving the primary database free for writes and fast reads
- A **data warehouse** — a separate system (BigQuery, Redshift, Snowflake) optimised for analytical queries, synced nightly from your main database

At the current scale of this project, running analytics on the main database is fine. The queries are infrequent (dashboards, not every page load) and the dataset is manageable. Note this as a future scaling concern, not a current problem.

**What the analytics module likely exposes:**
- Event-level stats for organizers (tickets sold, revenue, RSVP count, check-in rate)
- Platform-level stats for admins (total events, total users, revenue by period)
- Game engagement stats (participation rate, average score, reward claims)

These are all read-only queries against existing tables — no new data model needed.

---

## Part 16 — The Messaging Module

The messaging module exposes one Socket.io gateway (`/messaging` namespace) and a REST controller. The gateway handles real-time delivery; the REST controller handles conversation creation and history loading. You need both.

### The Two Gateways

The project now has two gateways running alongside the HTTP API:

| Namespace | Purpose |
|---|---|
| `/messaging` | DM conversations and event chat rooms |
| `/notifications` | Per-user notification push |

Both are on the same process and port as the HTTP API. Socket.io separates them by namespace — `/messaging` traffic never mixes with `/notifications` traffic. Clients connect to each independently, with the same JWT token.

### Direct Messages: The Full Flow

DMs involve a REST call to create the conversation, then socket events for all subsequent interaction.

**Step 1 — Create the conversation via REST (once per pair of users):**

```
POST /v1/conversations
Body: { "userId": "<target-user-uuid>" }
```

Both users must be mutual followers. The service checks this before creating anything. You cannot DM a stranger. The response includes `id` — the conversation ID you will use for every socket event.

**Why REST for creation, not socket?** Creating a conversation writes to the database and enforces the mutual-follow rule. REST is the right tool for operations that validate, write, and need a structured error response. Socket events are for real-time delivery of things that have already been created.

**Step 2 — Join the DM room (every time the user opens the conversation screen):**

```typescript
socket.emit('join:dm', { conversationId: '<uuid>' });
socket.on('joined:dm', ({ conversationId }) => {
  // confirmed — you're in the room, messages will be delivered
});
```

Internally, the server calls `client.join('dm:{conversationId}')`. The room name is `dm:` + the conversation UUID. Any message sent to this room reaches all sockets in it — both participants if both are connected.

**Important:** Room membership is not persisted across reconnects. Socket.io handles automatic reconnection, but when the socket reconnects, the room join must be re-emitted. Always re-emit `join:dm` inside the socket's `connect` event handler.

**Step 3 — Send messages:**

```typescript
socket.emit('send:dm', {
  conversationId: '<uuid>',
  body: 'Hey!',       // optional — text
  mediaUrl: '<url>',  // optional — image or video URL
});
```

At least one of `body` or `mediaUrl` must be provided. The `senderId` is always resolved from the JWT token on the server — the client never passes it. This prevents any possibility of spoofing who sent a message.

**Step 4 — Receive messages:**

```typescript
socket.on('new:dm', (message) => {
  appendToConversation(message);
});
```

`new:dm` is broadcast to the entire `dm:{conversationId}` room — that means both the sender and the recipient receive it. The sender's client should display the message using `new:dm`, not optimistically before the event arrives. This keeps both sides in sync.

**Step 5 — Typing indicators:**

```typescript
// emit when user starts typing (debounce — don't fire on every keystroke)
socket.emit('typing:dm', { conversationId: '<uuid>' });

// receive when the other participant is typing
socket.on('typing:dm', ({ userId }) => {
  showTypingIndicator(userId);
});
```

The server sends the `typing:dm` event only to the other participant — using `.to(room).except(socket.id)` — so you never see your own typing indicator. Debounce the emit on the client to avoid flooding: emit once when typing starts, not on every character.

### Direct Message REST Endpoints

```
GET /v1/conversations                                     — inbox list
GET /v1/conversations/:id/messages?page=1&limit=50        — paginated history
```

The inbox response shape per conversation:

```json
{
  "id": "uuid",
  "participant": { "id": "...", "username": "...", "avatarUrl": "..." },
  "lastMessage": { "body": "...", "createdAt": "..." },
  "unreadCount": 3,
  "lastMessageAt": "2026-05-20T10:00:00.000Z"
}
```

Load history via REST when the user opens a conversation (to show past messages), then keep the socket open for new messages going forward. Don't re-fetch history via REST on every new message — the socket delivers new messages in real time.

### Event Chat

Event chats are group rooms, one per event per lifecycle phase. Every event can have up to three chat rooms:

| Section | When it is active |
|---|---|
| `PRE_EVENT` | Before the event starts |
| `DURING_EVENT` | While the event is live |
| `POST_EVENT` | After the event ends |

**Access control:** The server checks that the connecting user has either RSVPed or checked into the event before allowing them to join or send messages. If neither is true, the socket call is silently rejected. This is enforced server-side — you cannot bypass it from the client.

The flow mirrors DMs:

```typescript
// join a section
socket.emit('join:event-chat', {
  eventId: '<uuid>',
  section: 'DURING_EVENT',   // 'PRE_EVENT' | 'DURING_EVENT' | 'POST_EVENT'
});

socket.on('joined:event-chat', ({ room }) => {
  // room = 'chat:<eventId>:DURING_EVENT'
  // confirmed — ready to send and receive
});

// send a message
socket.emit('send:event-chat', {
  eventId: '<uuid>',
  section: 'DURING_EVENT',
  body: 'This is great!',   // optional
  mediaUrl: '<url>',        // optional
});

// receive messages (broadcast to everyone in the room)
socket.on('new:event-chat', (message) => {
  appendToEventChat(message);
});
```

Event chat history is loaded via REST:

```
GET /v1/events/:eventId/chat/:section?page=1&limit=50
```

Where `:section` is `PRE_EVENT`, `DURING_EVENT`, or `POST_EVENT`.

### Message Object Shape

Both `new:dm` and `new:event-chat` deliver a message in this shape:

```typescript
interface Message {
  id: string;
  conversationId?: string;  // present on DM messages
  chatId?: string;          // present on event chat messages
  senderId: string;
  body?: string;
  mediaUrl?: string;
  createdAt: string;        // ISO 8601
  sender: {
    id: string;
    username: string;
    avatarUrl?: string;
    displayName?: string;
  };
}
```

### The Canonical Ordering Pattern for Conversations

When user A starts a conversation with user B, the service must guarantee only one conversation record ever exists for that pair — regardless of who initiates. The trick: before creating, sort the two user IDs alphabetically and always assign the smaller one to `userAId`:

```typescript
const [userAId, userBId] = [userId, targetUserId].sort();
await prisma.conversation.upsert({
  where: { userAId_userBId: { userAId, userBId } },
  create: { userAId, userBId },
  update: {},
});
```

This makes the `@@unique([userAId, userBId])` constraint meaningful: since the IDs are always assigned in sorted order, the pair `(A, B)` is always the same regardless of who called the endpoint first. Without the sort, user A initiating creates `(A, B)` and user B initiating creates `(B, A)` — two separate rows, two separate inboxes, diverged message history.

### The `lastMessageAt` Denormalisation

The inbox is ordered by `lastMessageAt DESC` — conversations with the most recent activity float to the top. This field is updated on every `send:dm` call:

```typescript
await prisma.conversation.update({
  data: { lastMessageAt: new Date() },
});
```

This is denormalisation: the correct value is derivable as `MAX(messages.createdAt)` for that conversation, but that requires an aggregation query across every message for every conversation in the inbox. With `lastMessageAt` pre-stored, the inbox query is a single read with no aggregation. The trade-off is one extra write per message to keep the field current — always worth it for any feature that shows a sorted inbox.

### What's Missing

**Message read receipts at scale.** The current `isRead: Boolean` on `Message` marks each message individually. At scale this means "mark as read" requires updating every unread message row. Most messaging apps use a `lastReadMessageId` per user per conversation instead — a single integer per user that the UI uses to determine which messages are "above" (read) or "below" (unread) the cursor. This is a significant improvement to make before heavy usage.

**Typing indicators for event chat.** The gateway implements `typing:dm` for DMs but there is no `typing:event-chat` event. For large group chats this is actually fine (typing indicators in group chats are noisy), but for small groups or pre-event chats it might be worth adding.

(For the general WebSocket gateway auth pattern that both `/messaging` and `/notifications` rely on, see `learning/backend-realtime.md` Part 26. For the frontend side of DMs and event chat — optimistic messages, chat UI bubbles, real-time badges — see `learning/frontend-realtime.md`.)

---

## Part 17 — The Storage Module

File uploads (avatars, event fliers, postcard media) go through the storage module. Based on `upload.service.ts` existing alongside `storage.service.ts`, uploads likely:
1. Accept multipart/form-data
2. Upload to a cloud storage provider (S3-compatible, based on `storageConfig`)
3. Return a public URL stored on the relevant model (`avatarUrl`, `flierUrl`, `mediaUrl`)

**Design consideration:** Storing file URLs in the database means if you change storage providers, you need a migration to update all URLs. A better pattern: store only the `storageKey` (the file path within your bucket) and compute the URL at read time. The `PostcardMedia` model does this right with a separate `storageKey` field.

(See `learning/backend-core.md` Part 32 for how this module's upload flow was migrated from multipart uploads through NestJS to presigned URLs, and `learning/devops.md` Part 34/35 for the MinIO configuration and presigned URL signature mechanics behind it.)

---

## Part 18 — The Admin Module

Admin routes are protected by role check:

```typescript
// users.prisma
role UserRole @default(USER)
// UserRole enum: USER | ADMIN | SUPER_ADMIN
```

The admin module likely handles: user banning, coupon creation, platform analytics, and event moderation. Role-based access control (RBAC) is the pattern — the role is stored on the user and checked in guards or service methods.

---

## Part 50 — The Pledge Module

The pledge system lets users financially support the platform. Unlike event tickets, pledges are platform-wide donations — they don't grant event access. The module lives at `src/modules/pledges/`.

### What pledges are

Pledges are voluntary support contributions. Users select a tier, pay, and get listed as a supporter. Key distinctions from tickets:
- Priced in USD internally, charged in NGN at conversion time
- Work for guests (unauthenticated users) — `email` and `name` required in body
- Eight hardcoded tiers from $5 (Vibe Watcher) to $500 (Vibe King)

### Hardcoded tiers vs database tiers

Pledge tiers are defined as constants in the service, not stored in a database table:

```typescript
const PLEDGE_TIERS: Record<string, { priceUsd: number; label: string }> = {
  vibewatcher:    { priceUsd: 5,   label: 'Vibe Watcher' },
  vibesupporter:  { priceUsd: 10,  label: 'Vibe Supporter' },
  vibefan:        { priceUsd: 25,  label: 'Vibe Fan' },
  vibeenthusiast: { priceUsd: 50,  label: 'Vibe Enthusiast' },
  vibechampion:   { priceUsd: 100, label: 'Vibe Champion' },
  vibepatron:     { priceUsd: 150, label: 'Vibe Patron' },
  vibemaestro:    { priceUsd: 250, label: 'Vibe Maestro' },
  vibeking:       { priceUsd: 500, label: 'Vibe King' },
};
```

This is appropriate when: tier prices are controlled by the platform (not configurable per-organizer), changes are infrequent, and the tier set is small enough that a code deploy is acceptable for updates. The alternative (database tiers) is better when admins need to manage tiers from a dashboard without a deploy.

### USD → NGN conversion

```typescript
const USD_TO_NGN = 1500; // set as a constant; in production this should come from a forex API or config

const amountNgn = tier.priceUsd * quantity * USD_TO_NGN;
```

The Ercaspay checkout is initiated with the NGN amount. Both `totalUsd` and `totalNgn` are stored on the `Pledge` record for display and audit.

### Guest support

`POST /pledges/initiate` is `@Public()`. For unauthenticated users, `email` and `name` are required in the request body. For authenticated users, these are pulled from the JWT-decoded user. The controller branches on whether a user is present:

```typescript
@Post('initiate')
@Public()
async initiate(@Body() dto: InitiatePledgeDto, @CurrentUser() user?: JwtPayload) {
  // user is undefined for guests — guard is @Public() so it doesn't reject
  return this.pledgesService.initiate(dto, user?.sub);
}
```

The service stores `userId: null` for guests and stores the email from the DTO for receipt purposes. If the guest later creates an account with the same email, their pledges can be linked manually or via a merge endpoint.

### The three endpoints

```
POST /v1/pledges/initiate        — @Public()
  Body: { tierId, quantity?, email?, name? }
  Returns: { pledgeId, checkoutUrl, totalNgn, totalUsd, expiresAt }

GET /v1/pledges/verify/:pledgeId — @Public()
  Returns: { status: PENDING|COMPLETED|FAILED|EXPIRED, pledge: {...} }

GET /v1/pledges/my               — auth required
  Returns: paginated list of user's pledges, newest first
```

(See `learning/backend-auth.md` Part 46 for the `@Public()` + optional-user pattern this endpoint relies on.)

---

## Part 51 — Ercaspay Payment Internals: NGN Amounts, Webhook Branching, and Notification Enrichment

### Ercaspay stores amounts in NGN, not kobo

Unlike Stripe (which uses the smallest currency unit — kobo for NGN), Ercaspay uses **full currency amounts**. ₦5,000 is stored as `5000`, not `500000`. This distinction matters because:

- If you divide by 100 before displaying, ₦5,000 becomes ₦50 — a 100× error
- The database stores the number Ercaspay returned — no conversion needed on read

The bug that appeared: the ticket purchase email had `totalAmount / 100` carried over from a previous Monnify integration. Monnify used kobo; Ercaspay does not. Fix: `params.totalAmount.toLocaleString()` with no division.

**Rule:** always check whether a payment provider uses major currency units (NGN) or minor units (kobo/cents). Ercaspay = NGN. Stripe = kobo/cents.

### Webhook dispatch branching

The single Ercaspay webhook endpoint routes a `payment_reference` to different processors in order. Each processor returns `null` if the reference doesn't belong to its domain:

```
Webhook arrives with payment_reference
      │
      ▼
Branch A: Is this an organizer plan payment?
  orgPaymentsService.processPayment(reference)
  → Found: { status: 'ORGANIZER_PLAN_ACTIVATED' }
  → Not found: returns null → fall through
      │
      ▼
Branch B: Is this a pledge?
  pledgesService.processWebhookPayment(reference)
  → Found: { status: 'PLEDGE_COMPLETED', ... }
  → Not found: returns null → fall through
      │
      ▼
Branch C: Must be a ticket purchase
  paymentsService.processWebhookPayment(reference)
```

This pattern lets a single webhook URL handle all payment types without separate endpoints registered per domain. Each service only processes references it created — branches never conflict.

### Public UUID-as-access-token pattern

`GET /v1/payments/purchases/:purchaseId/summary` is `@Public()`. The purchase UUID (128-bit, 2^122 possible values) is the access control — computationally infeasible to brute-force. No login required to fetch the confirmation data.

This pattern is appropriate when:
- The protected data (a purchase receipt) is the user's own — not sensitive to other users
- The confirmation page needs to work even if the user isn't logged in at that moment (e.g. checkout opened in a different browser session)
- You don't want to force a login flow just to show "your tickets are confirmed"

**Route ordering is critical:** `GET /purchases/:id/summary` must be declared BEFORE `GET /purchases/:id` in the controller. Otherwise NestJS matches the literal string `"summary"` as the `:id` param and tries to parse it as a UUID, producing a 400. This is a specific instance of the static-before-parameterized rule from `learning/backend-core.md` Part 42.

(See `learning/frontend-payments-games.md` Part 53 for the frontend confirmation page that consumes this endpoint, including the webhook-delay polling pattern.)

### Enriched ticket purchase email

`notifyTicketPurchased` was updated to send a full HTML email with event context and individual ticket numbers. New signature:

```typescript
async notifyTicketPurchased(params: {
  userId: string; email: string; displayName: string; purchaseId: string;
  eventName: string; description?: string | null; eventDate: Date;
  eventEndDate?: Date | null; locationName?: string | null;
  tickets: { ticketNumber: string; tierName: string }[];
  totalAmount: number;  // in NGN, no division — display directly
})
```

The webhook handler builds the ticket list after issuing tickets:

```typescript
const tierMap: Record<string, string> = {};
for (const t of purchase.event.ticketTiers) { tierMap[t.id] = t.name; }

this.notificationsService.notifyTicketPurchased({
  ...purchaseData,
  tickets: issuedTickets.map(t => ({
    ticketNumber: t.ticketNumber,
    tierName: tierMap[t.ticketTierId] ?? 'General',
  })),
}).catch(e => this.logger.error(`notifyTicketPurchased failed: ${e?.message}`));
```

The `.catch()` is mandatory — a failed email must not crash the webhook handler. Tickets have already been issued; the confirmation email is best-effort.

---

## Part 52 — Notification Coverage Audit

Not all `NotificationType` enum values are wired to actual calls in the codebase. Tracking this prevents silent gaps where users expect a notification but receive nothing.

### Current status

| Type | Status | Where it fires |
|---|---|---|
| `TICKET_PURCHASED` | ✅ Wired | `payments.service.ts` — after Ercaspay webhook |
| `GAME_RESULT` | ✅ Wired (added June 2026) | `games.service.ts` — in `distributeRoundRewards` |
| `GAME_UNLOCKED` | ✅ Wired | `organizer-payments.service.ts` — on plan activation |
| `PAYMENT_CONFIRMED` | ✅ Wired | organizer payment webhook |
| `PAYMENT_FAILED` | ✅ Wired | organizer payment webhook |
| `EVENT_PUBLISHED` | ✅ Wired | events service on publish |
| `VIBETAG_ACTIVATED` | ✅ Wired | vibetag service |
| `EVENT_REMINDER` | ✅ Wired | daily cron job |
| `FOLLOW` | ✅ Wired | social service |
| `LIKE` | ✅ Wired | social service |
| `COMMENT` | ✅ Wired | social service |
| `RSVP` | ✅ Wired | events service |
| `CHECK_IN` | ❌ Not wired | No code calls this — would fire when an attendee checks in |
| `TAG` | ❌ Not wired | No code calls this — would fire when tagged in a postcard |

### How GAME_RESULT was added

`GamesService.distributeRoundRewards` loops through all entries to calculate rewards. After the loop, a notification fires for each participant:

```typescript
// 1. GamesModule imports NotificationsModule
@Module({
  imports: [PaymentsModule, NotificationsModule],
  ...
})

// 2. GamesService constructor
constructor(
  private prisma: PrismaService,
  private payments: PaymentsService,
  private notifications: NotificationsService,
) {}

// 3. Inside distributeRoundRewards, after the reward creation loop:
for (const entry of entries) {
  if (entry.userId) {
    this.notifications.create({
      recipientId: entry.userId,
      type: NotificationType.GAME_RESULT,
      targetType: NotificationTarget.GAME,
      targetId: roundId,  // frontend deep-links to the round's results screen
    }).catch(() => null);  // best-effort — notification failure does not affect rewards
  }
}
```

Note: anonymous players (`entry.userId === null`) don't get notifications — they have no account to receive them. The `if (entry.userId)` guard handles this. (See `learning/backend-games-ai.md` Part 49 for the full anonymous game play system this guard interacts with.)

### Avoiding circular imports

`GamesModule` already imports `PaymentsModule`. Adding `NotificationsModule` is safe because `NotificationsModule` doesn't import `GamesModule` — no cycle. If a circular dependency appeared, the fix would be to move the notification call out of `GamesService` into an event-emitter or a separate coordination service.
