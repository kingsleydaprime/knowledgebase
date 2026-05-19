# NextVibe Backend — From Zero to Engineer

This document takes you from absolute beginner to a confident software engineer using this codebase as your textbook. It covers system design, database design, NestJS architecture, every module, every design decision, every trade-off, the loopholes that exist, and what should be improved. Read it front to back. Everything connects.

---

## Part 1 — How to Read Someone Else's Codebase

Before anything else, you need this skill. You will spend more of your career reading code than writing it.

### The Mental Model: Top-Down, Not Bottom-Up

When you open a new codebase, do not start reading files randomly. Always go top-down.

**Step 1: Understand the shape of the project.**

Look at the folder structure first. In this project:
```
src/
  modules/         ← Feature domains (auth, events, payments, etc.)
  shared/          ← Infrastructure used by everything (prisma, redis)
  common/          ← Cross-cutting utilities (guards, decorators, types)
  config/          ← Environment configuration
prisma/
  schema/          ← Database model definitions split by domain
```

Just from this you can already answer: "This is a NestJS API with a PostgreSQL database via Prisma, organised by feature modules." You haven't read a single line of logic yet.

**Step 2: Read the entry point and the app module.**

`src/app.module.ts` tells you every top-level module: Auth, Users, Events, VibeTags, Social, Games, Payments, Billing, Notifications, Messaging, Storage, Discovery, Admin. That list IS the product. You now know what the system does without reading implementation.

**Step 3: Pick a module and read the controller first.**

The controller is the contract. It tells you what HTTP endpoints exist, what input they accept, and what they return. Only then read the service to understand HOW those things are done.

**Step 4: Read the database schema for the domain.**

The schema tells you what data the feature cares about and how it relates to everything else. Relations in Prisma (`@relation`) are your map of the domain.

**Step 5: Grep for patterns, not files.**

When you want to understand how authentication works: `grep -r "JwtAuthGuard\|@Public" src/` — instantly shows you every protected and public route. When you want to find where an email is sent: `grep -r "sendEmail\|resend" src/`. The codebase talks back when you ask the right questions.

**Step 6: Understand by flow, not by file.**

Pick a user story: "User buys a ticket." Then trace the entire flow from HTTP request → controller → service → database → webhook → notification. Following a flow through multiple files teaches you more than reading files in isolation.

**What to ignore on a first pass:**
- DTOs (data validation classes) — they're boilerplate, skip until you need them
- Test files — read only when debugging
- Config files — glance at them, understand what env vars exist, move on

---

## Part 2 — What is a Backend API?

Before system design, understand what this code actually is.

A backend API is a program that:
1. Listens for HTTP requests on a port (port 3000 here)
2. Parses the request (who is calling? what do they want? what data did they send?)
3. Validates the request (is the data correct? is the user allowed to do this?)
4. Runs business logic (create a record, charge a payment, send an email)
5. Returns a response (JSON with the result or an error)

That's it. Everything else — modules, guards, decorators, services — are just organised ways to do those five things without your code becoming a mess.

---

## Part 3 — Why NestJS?

Node.js lets you write a server in raw JavaScript. Express.js gives you routing. But both let you write code however you want, which means a team of five people writes five different styles and the codebase becomes unmaintainable.

NestJS adds structure on top of Express:
- **Modules** force you to group related code together
- **Dependency injection** means services receive their dependencies through constructors rather than importing them directly — easier to test, easier to replace
- **Decorators** (`@Controller`, `@Injectable`, `@Get`) make the intent of code visible at a glance
- **Guards, pipes, interceptors** give you named hooks to intercept requests at different points

The trade-off: NestJS has a learning curve. You have to understand modules, providers, and how dependency injection works before you can be productive. A simple Express app would be faster to start. But this project has 20+ modules — without NestJS's structure it would be extremely hard to navigate.

---

## Part 4 — System Design: The Big Picture

System design is making decisions about how the pieces of a system fit together before you write code. Let's look at what was decided here and why.

### The Architecture: Monolith

This is a **monolith** — one deployable application that does everything. One process handles auth, payments, games, notifications, messaging, and everything else.

The alternative is **microservices**: separate deployable services for each domain (an auth service, a payments service, a notifications service, etc.) that communicate over a network.

**Why a monolith was the right choice here:**

1. **The product is unproven.** Microservices make sense when you have a product with known traffic patterns and clear domain boundaries. At this stage, the domain boundaries are still shifting — what belongs in billing vs payments vs events is still being figured out. With microservices, every refactor across boundaries costs you network calls, serialisation, and distributed transaction problems.

2. **Microservices add enormous operational complexity.** You need service discovery, API gateways, distributed tracing, separate deployments for each service, shared secret management. A small team would spend more time on infrastructure than product.

3. **The modular structure of NestJS gives you the benefits of clear boundaries without the deployment complexity.** `BillingModule` can't directly call `PaymentsService` internals — it has to go through the exported interface. Same as microservices, without the network call.

**When should you move to microservices?**

When a specific module has meaningfully different scaling requirements than the rest. For example: if the Games module during live events gets 50× the traffic of everything else, you might extract it. Or if the video processing (VibeTags media) is slow and you don't want it to block the API. Otherwise, don't.

### The Technology Stack

| Technology | What it does | Why this one |
|------------|-------------|--------------|
| NestJS | HTTP framework | Structure for large codebase |
| PostgreSQL | Primary database | Relational data, ACID, complex queries |
| Prisma | Database ORM | Type-safe queries, schema migrations |
| Redis | Cache + session store | Fast key-value lookups, JWT revocation |
| Socket.io | WebSocket server | Real-time notifications |
| Resend | Transactional email | Simple API, good deliverability |
| Juicyway | Payment processor | Nigerian payment market |
| Argon2 | Password hashing | Gold standard for password security |

### Why PostgreSQL Over Other Databases?

This is one of the most important decisions in system design. Let's compare — and more importantly, let's look at real examples of when you'd pick each one.

---

**PostgreSQL — use when data has relationships and must be reliable**

PostgreSQL is a relational database. Data lives in tables with rows and columns, and tables link to each other through foreign keys.

Use PostgreSQL when:
- Data has clear relationships between entities (users own tickets, tickets belong to events)
- You need ACID guarantees — meaning when you transfer a ticket, either BOTH the old owner losing it AND the new owner gaining it happen together, or neither does. No partial state
- You need complex queries — "give me all events in Lagos, in the SPORTS category, starting within 7 days, where the organizer has published at least 3 events before" — one SQL query handles this naturally
- You're storing money — PostgreSQL's `Decimal` type is exact. Floats are not

**Real examples in this project:**
- Users, Events, Tickets, Payments — all PostgreSQL. The relationships between them are complex and the data must never be inconsistent
- The ticket transfer flow (`TicketTransfer` table) requires that the old owner loses the ticket AND the new owner gains it atomically — only a transactional database gives you this guarantee

---

**MongoDB — use when data has no fixed structure and relationships are shallow**

MongoDB stores data as documents (JSON-like objects). There are no tables with fixed columns — each document can have different fields.

Use MongoDB when:
- The shape of your data changes frequently and is hard to define upfront — e.g., a product catalogue where different product types have completely different attributes (a shoe has size, a laptop has RAM and CPU)
- You have a single entity with deeply nested data that you always read together — e.g., a blog post with its content, tags, and metadata all in one document
- You don't need to query across relationships often

**When NOT to use MongoDB:**
- Anything involving money — cross-document transactions in MongoDB exist but are complex and have performance costs
- Anywhere you need to join data — "give me all users who bought tickets to events in Lagos" requires joining Users, Tickets, and Events. In MongoDB that's multiple queries stitched together in code. In PostgreSQL it's a single JOIN

**Concrete example where MongoDB would be wrong here:** The `GameRound.config` field stores questions as JSON. That JSON is inside PostgreSQL. You might think "this is document-style data, put it in MongoDB." But the game round still belongs to a game session, which belongs to an event, which belongs to an organizer. The relationships mean PostgreSQL is right for the whole domain — the JSON column is just a pragmatic escape hatch for the unstructured questions field.

---

**Redis — use when you need extreme speed and the data is temporary or supplementary**

Redis is an in-memory key-value store. It doesn't store on disk by default. It's 10–100× faster than PostgreSQL for simple lookups because data lives in RAM.

Use Redis when:
- Data expires automatically — refresh tokens should expire after 30 days. Redis has native TTL (time-to-live) — you set a key and it disappears automatically
- You need to revoke something fast — "log out all devices for this user" means deleting all refresh token keys matching `refresh:userId:*`. One command, instant
- Rate limiting — "how many requests has this IP made in the last 60 seconds?" — Redis can increment a counter and expire it in one atomic operation
- Caching hot queries — if "get all PUBLISHED events" is called 10,000 times per minute, you cache the result in Redis for 30 seconds and hit PostgreSQL only twice per minute instead

**When NOT to use Redis as your only store:**
- Never store data you can't afford to lose in Redis alone. Redis is in-memory — a server restart or crash without persistence configured loses everything
- Don't store relationships in Redis — it has no JOIN concept

**Real examples in this project:**
- `refresh:userId:token` — stores active refresh tokens with 30-day TTL. When the user logs out, the key is deleted. If the server restarts, users just log in again
- `getClient()` is exposed on `RedisService` for BullMQ job queues and Socket.io's Redis adapter — Redis as a pub/sub message broker, not a database

---

**MySQL — skip it for new projects**

MySQL and PostgreSQL are both relational databases and both are production-ready. MySQL was historically faster for simple reads; PostgreSQL was better for complex queries. In 2024 the gap has closed. PostgreSQL has better JSON support, better full-text search, better extension ecosystem (PostGIS for geolocation, pgvector for AI embeddings), and more active development. Start new projects on PostgreSQL.

---

**The decision framework:**

| Question | Answer → Database |
|---|---|
| Does the data have relationships between entities? | PostgreSQL |
| Do I need transactions across multiple records? | PostgreSQL |
| Is the data shape unpredictable or highly varied? | MongoDB |
| Does the data expire or need to be fast to revoke? | Redis |
| Am I caching results of expensive queries? | Redis |
| Am I storing money or anything financial? | PostgreSQL, always |
| Do I need to query across multiple types of data together? | PostgreSQL |

---

## Part 5 — Database Design and Normalisation

Database design is the most important thing you will do. A bad schema is nearly impossible to fix without downtime and a full migration.

### What is Normalisation?

Normalisation is the process of organising data to reduce redundancy. The goal: every piece of information should live in exactly one place.

**Bad design (denormalised):**
```
tickets table:
id | user_email | user_name | event_name | event_date | tier_name | tier_price
```

If the user changes their email, you need to update every row in the tickets table. If the event name changes, same problem. Data is duplicated everywhere.

**Good design (normalised):**
```
users table: id | email | name
events table: id | name | date
ticket_tiers table: id | event_id | name | price
tickets table: id | user_id | event_id | tier_id
```

Now if a user changes their email, you update one row in `users`. Everything that references that user automatically reflects the change.

### The Domain Split in This Project

The schema is split across multiple files, each representing a domain. This is not just organisation — it reflects how the business thinks about the data.

#### Domain 1: Identity (`user.prisma`)

**`User`** — the central entity. Everything in the system eventually traces back to a user.

Key design decisions:
- `passwordHash` is nullable — because OAuth users (Google login) have no password. The `oauthProvider` and `oauthId` fields handle that path
- `emailVerifyToken` is stored on the user — a simpler design than a separate verification table. The token expires and is cleared after use
- `role` field with `UserRole` enum — enables admin checks without a separate admin table
- `@@index([email])` and `@@index([username])` — these two fields are looked up on every login, so indexes make those queries fast. Without an index, PostgreSQL scans every row

**`Follow`** — a join table for the social graph.

```
followerId → "User A" follows followingId → "User B"
```

`@@unique([followerId, followingId])` prevents double-follows at the database level — not just in the application code. Always enforce unique constraints at both levels.

`onDelete: Cascade` means if a user is deleted, their follows are deleted too. Without this you'd have orphaned rows pointing to non-existent users.

**`UserPreference`** — separated from `User` for a reason. Preferences change rarely and are read infrequently. Keeping them in a separate table means every query on `User` doesn't drag along preference data you don't need (though you could also use `select` to avoid this).

#### Domain 2: Events (`events.prisma`)

**`Event`** — the core of the product.

Notable fields:
- `qrCode String @unique` — every event gets a unique QR code for physical check-in. `@unique` is a database-level constraint
- `latitude` and `longitude` as `Decimal` — never use Float for coordinates. Decimal maintains precision. Though a dedicated PostGIS extension would be better for geospatial queries
- `parentEventId` — self-referential relation. An event can be linked to another event (pre/post event relationship). This is a recursive foreign key
- `status EventStatus @default(DRAFT)` — events go through a lifecycle: DRAFT → PUBLISHED → ENDED/CANCELLED

**`RSVP`** — represents a user's interest in attending an event, separate from actually buying a ticket.

This is an important design distinction: RSVP is "I intend to come" (free), Ticket is "I have paid to come". They are separate tables because they represent different things:
- Not all events have tickets (free events use RSVP only)
- An RSVP can be CONFIRMED or WAITLISTED
- The `@@unique([userId, eventId])` prevents a user from RSVPing to the same event twice

**`CheckIn`** — records that a user physically arrived at the event. Links to both the user and the event. `@@unique([userId, eventId])` means you can only check in once per event.

**`EventReminder`** — stores when reminders should be sent. The cron job in `NotificationsService` reads this table. Keeping reminders in the database rather than just scheduling them in code means they survive server restarts.

#### Domain 3: Tickets (`tickets.prisma`)

This domain has three distinct models for a reason:

**`TicketTier`** — the category of ticket (VIP, Regular, Early Bird). Belongs to an Event. Has a price, quantity limit, and sale window.

**`TicketPurchase`** — a payment transaction. Records that a user paid for one or more tickets. This is separate from the actual tickets because one purchase can buy multiple tickets. The purchase records payment status, payment references (Monnify, Juicyway), and is the source of truth for whether money changed hands.

**`Ticket`** — the actual entry pass. Each ticket is issued after a purchase is confirmed. Has:
- `ticketNumber` — human-readable (e.g., `NV-EVT-001`)
- `qrCode` — machine-readable, used for scanning at the gate
- `userId` — CURRENT owner (can be transferred)
- `originalBuyerId` — who bought it (for fraud tracking even after transfer)
- `status` — VALID, USED, CANCELLED, EXPIRED, TRANSFERRED, SUSPENDED

**Why separate Purchase from Ticket?**

Consider: user buys 3 VIP tickets. That's 1 purchase, 3 tickets. If you merged them, you'd either:
- Store all 3 QR codes in one row (terrible — arrays in relational DBs are a code smell)
- Create 3 identical purchase rows (data duplication)

The separation is clean: one purchase → many tickets.

**`TicketTransfer`** — an audit log of every time a ticket changed hands. This is a history table — you never update it, only append. It answers "where has this ticket been?".

#### Domain 4: Social (`social.prisma`)

**`Like`** — a polymorphic model. `targetType` (EVENT or POSTCARD) + `targetId` lets one table track likes on any kind of content.

Trade-off: polymorphic associations lose foreign key constraints. The database can't enforce that `targetId` actually points to a real event or postcard — that's enforced in application code (`verifyTarget` in `LikesService`). This is acceptable here; the alternative (a separate `EventLike` and `PostcardLike` table) is more tables with the same query logic duplicated.

`@@unique([userId, targetType, targetId])` — prevents double-liking at the database level.

**`Comment`** — also polymorphic. The `parentId` field enables threaded replies (a comment can have a parent comment). The relation `replies Comment[] @relation("CommentReplies")` is a self-referential one-to-many.

**`Share`** — tracks shares with `platform` (WhatsApp, Twitter, CopyLink). Useful for analytics even though you can't control whether the user actually shared.

#### Domain 5: Games (`games.prisma`)

This domain is the most complex in the schema.

**`GameSession`** — a container for a game event on a specific event. Has status lifecycle: PENDING → UNLOCKED → ACTIVE → ENDED.

The `status` field is critical: a game session can only be activated after it's been UNLOCKED (meaning paid for, if it's over quota). This prevents the edge case of accidentally running a game you haven't paid for.

`shareToken String @unique` — a short random string (generated with `nanoid`) that creates a public join link like `nextvibe.com/game/join/abc123xyz`. This enables viral participation — people who weren't at the event can join via link, but they're marked as `isSpectator: true` and excluded from prizes.

**`GameRound`** — a single round within a session. `config Json` stores the questions, answers, and correct answer indices. JSON in a relational DB is a pragmatic compromise — the structure of questions varies by game type (trivia has different fields than word puzzles), so a fixed schema would be overly rigid.

**`GameEntry`** — one user's submission for one round. `@@unique([gameRoundId, userId])` enforces one answer per user per round at the database level.

**`GameSessionEntry`** — one user's participation in an entire session (across all rounds). `totalScore` accumulates across rounds. `isSpectator` differentiates viral participants from real attendees.

**Why two entry tables?** Because you need both session-level totals (for the overall leaderboard) and round-level scores (for per-round rankings and rewards). Without `GameSessionEntry`, computing "who won the overall session?" would require summing all `GameEntry` scores for every query — expensive. The session entry pre-aggregates this.

**`GameRewardTier`** — defines what winners get. `rank: Int` is the position being rewarded (1st, 2nd, 3rd). Can be attached to a session or a specific round.

**`Reward`** — records that a specific user won a specific reward. Created when a round or session ends. `isClaimed` tracks whether they've collected it.

#### Domain 6: Billing (`billing.prisma`)

**`Coupon`** — discount codes. `usageLimit Int?` where null means unlimited. `usageCount` is incremented inside a transaction to prevent race conditions where two simultaneous requests both try to use the last remaining use.

**`OrganizerPayment`** — a platform fee record. Organizers pay NextVibe to publish events with features. This is different from `TicketPurchase` (attendees paying organisers). Stores:
- `baseAmount`, `volumeDiscountPercent`, `couponDiscountAmount`, `finalAmount` — the full pricing calculation, snapshotted at the time of payment so repricing doesn't affect historical records
- `paymentReference` — your internal reference (NVO-timestamp-userid)
- `juicywayReference` — the payment processor's reference (their UUID)
- `gameSessionId @unique` — one organizer payment can pay for exactly one game session. The `@unique` enforces this

**`EventPlan`** — what features are unlocked on an event after payment. Created/updated when an organizer payment completes. This is the source of truth for "can this event run games? does it have VibeTags?".

`vibetagPhases GameActivityTiming[]` — an array column in Postgres. Stores which phases (PRE_EVENT, DURING_EVENT) are enabled.

#### Domain 7: Messaging (`messaging.prisma`)

**`Conversation`** — a 1-to-1 DM thread between two users. `@@unique([userAId, userBId])` ensures only one conversation exists between any pair. Note: the code normalises user IDs to ensure userA < userB alphabetically, preventing two separate conversations for the same pair.

`lastMessageAt DateTime?` — denormalised timestamp for sorting the inbox. You could derive this from `MAX(messages.createdAt)` per conversation but that's an expensive query. This field trades a small write cost (update it every time a message is sent) for a fast read.

**`Message`** — individual messages. `@@index([conversationId, createdAt])` — a compound index because you almost always query "messages in this conversation, ordered by time."

**`EventChat`** — separate group chat per event phase (PRE_EVENT, DURING_EVENT, POST_EVENT). `@@unique([eventId, section])` ensures only one chat per phase per event.

#### Domain 8: Postcards (`postcards.prisma`)

**`Postcard`** — user-generated content created via VibeTags. Has a `vibeTagId` — postcards are always created within the context of a VibeTags activity.

`likeCount Int @default(0)` and `commentCount Int @default(0)` — counter caches. Instead of `SELECT COUNT(*) FROM likes WHERE targetId = ?` on every request, you maintain a running total. This trades a slightly more complex write (increment/decrement the counter AND write the like row) for a much faster read. For a social feature that gets many more reads than writes, this is always worth it.

`PostcardLike` and `PostcardComment` — these appear to be duplicates of the generic `Like` and `Comment` tables in `social.prisma`. This is a design inconsistency — the codebase uses both. `PostcardLike` and `PostcardComment` seem to be legacy models that weren't fully migrated. The `likes.service.ts` and `comments.service.ts` use the generic `Like` and `Comment` tables.

#### Domain 9: VibeTags (`vibe-tags.prisma`)

**`VibeTag`** — a themed frame/filter that attendees use when creating postcards. Can be platform-default (available to all events) or event-specific. `@@unique([eventId, activityTiming])` — one VibeTags activity per phase per event.

---

### Database Indexes — What They Are, Why They Matter, How to Choose

After reading every table, you'll have noticed lines like:

```prisma
@@index([email])
@@index([organizerId])
@@index([conversationId, createdAt])
```

These are indexes. Understanding them is one of the most important skills for a backend engineer, because a missing index on the wrong table can make a fast app grind to a halt under load.

**What is an index?**

Imagine the `users` table has 1,000,000 rows. You run:

```sql
SELECT * FROM users WHERE email = 'king@example.com';
```

Without an index, PostgreSQL reads every single row top to bottom until it finds the match. That's a **full table scan** — O(n) where n is the number of rows. At 1 million users, this is slow. At 10 million, it's unusable.

With an index on `email`, PostgreSQL maintains a separate sorted data structure (a B-tree) that maps email values to their row location. Finding `king@example.com` in a sorted B-tree is O(log n) — finding 1 row in 1 million takes about 20 comparisons instead of 1,000,000. That is a staggering difference.

**When to add an index**

Add an index on any column that you:
1. **Filter on** — `WHERE email = ?`, `WHERE status = 'PUBLISHED'`
2. **Sort on** — `ORDER BY createdAt DESC`
3. **Join on** — foreign keys like `WHERE eventId = ?` (Prisma adds these automatically for `@relation` fields in many setups, but always verify)

Do NOT add an index on every column. Indexes have a cost:
- They take up disk space
- Every `INSERT`, `UPDATE`, and `DELETE` must also update all indexes on that table
- Too many indexes on a table with heavy writes makes writes slow

**Compound indexes — when one index covers multiple columns**

```prisma
@@index([conversationId, createdAt])
```

This is on the `messages` table. The query is almost always: "give me messages IN this conversation, sorted by time." A compound index on `(conversationId, createdAt)` covers this query entirely — PostgreSQL can filter on `conversationId` AND sort by `createdAt` without ever reading the actual table rows.

The order in a compound index matters. `(conversationId, createdAt)` lets you efficiently query:
- "All messages in conversation X" — uses the first column
- "All messages in conversation X since time T" — uses both columns

But NOT:
- "All messages since time T across all conversations" — the first column is unspecified, the index can't be used efficiently

Rule: put the most selective column (the one that eliminates the most rows) first. `conversationId` eliminates far more rows than `createdAt` would alone.

**Unique indexes — constraints + speed**

```prisma
@@unique([userId, eventId])  // on rsvps table
```

`@@unique` is both a uniqueness constraint (prevents duplicates at the DB level) AND an index. Every `@@unique` is automatically indexed, because the database needs to efficiently check for existing rows before inserting.

**Examples from this codebase and why each exists:**

| Table | Index | Reason |
|---|---|---|
| `users` | `@@index([email])` | Every login queries `WHERE email = ?` |
| `users` | `@@index([username])` | Profile lookup by username |
| `events` | `@@index([status])` | Discovery filters `WHERE status = 'PUBLISHED'` |
| `events` | `@@index([startsAt])` | Discovery filters upcoming events |
| `events` | `@@index([organizerId])` | "My events" query |
| `messages` | `@@index([conversationId, createdAt])` | Chat history query — filter + sort |
| `likes` | `@@index([targetType, targetId])` | "How many likes on this event?" |
| `ticket_purchases` | `@@index([paymentStatus])` | Webhook handler looks up PENDING payments |
| `follows` | `@@index([followingId])` | "Who follows this user?" (followers list) |
| `follows` | `@@index([followerId])` | "Who does this user follow?" (following list) |

**What's missing:** The `notifications` table has no index on `[recipientId, isRead]`. The unread count query is `WHERE recipientId = ? AND isRead = false`. Without this compound index, every page load that shows a notification badge does a full scan of all notifications for that user. At 100 notifications per user and 10,000 users making simultaneous requests, this becomes a problem fast. This is noted in Part 21.

**How to know if you're missing an index in production:**

Use `EXPLAIN ANALYZE` in PostgreSQL:
```sql
EXPLAIN ANALYZE SELECT * FROM notifications WHERE recipient_id = 'uuid' AND is_read = false;
```

If you see `Seq Scan` (sequential scan) in the output, PostgreSQL is scanning every row. If you see `Index Scan`, an index is being used. Always run EXPLAIN ANALYZE on your most frequent queries to verify indexes are being used.

---

## Part 6 — Controllers Are the API

Before getting into modules, this concept deserves its own section because it reframes how you read every controller file.

The entire NestJS server — the process, the database connection, the services, all of it — exists and runs. But without controllers, the outside world has no way to interact with it. The controller is the **exposed interface**. It defines:

- What URLs exist (`@Get('/events')`, `@Post('/payments/purchase')`)
- What HTTP methods they accept
- What authentication is required (`@Public()` or bearer token)
- What the input shape must be (DTOs)
- What the response looks like

The service is the brain. The controller is the face. The controller never processes — it receives, validates, delegates, and returns. If you look at any controller in this project, the method bodies are almost always a single line:

```typescript
@Post('purchase')
async initiatePurchase(@CurrentUser() user: JwtPayload, @Body() dto: InitiatePurchaseDto) {
  return this.paymentsService.initiatePurchase(user.sub, dto.eventId, dto.ticketTiers);
}
```

That's it. No logic. It just extracts what it needs (who's calling, what they sent) and hands it to the service.

**The clearest analogy:** Think of a restaurant.

- The **client** (browser, mobile app) is the **customer** — they want something done
- The **controller** is the **waiter** — they take the order, check it makes sense, and bring it to the kitchen. The waiter doesn't cook. They're the interface between the customer and the kitchen
- The **service** is the **chef** — they have all the actual skills and tools. They do the real work
- The **database** is the **pantry** — ingredients the chef reads from and writes back to

The customer never talks to the chef directly. The waiter (controller) receives the order, validates it ("we don't serve that, sir"), passes it to the chef (service), and brings the result back. The chef doesn't care how the order arrived — they just process what the waiter hands them.

This is why, when reading a new codebase, you read the controller first. The controller is the contract — it tells you what the system does. The service is the implementation — it tells you how.

---

## Part 7 — The NestJS Module System

Understanding how NestJS modules wire together is essential before reading any service.

### Dependency Injection

In NestJS, you never create service instances with `new`. Instead:

```typescript
// providers register services in a module
@Module({
  providers: [PaymentsService, JuicywayService],
})

// services declare what they need in constructors
@Injectable()
export class PaymentsService {
  constructor(
    private prisma: PrismaService,      // injected automatically
    private juicywayService: JuicywayService,  // injected automatically
  ) {}
}
```

NestJS's IoC (Inversion of Control) container creates and injects all dependencies. You don't call `new PrismaService()` — NestJS does. This means:
- You can swap `PrismaService` for a mock in tests without changing `PaymentsService`
- Circular dependencies surface at boot time, not at runtime

### Modules and Exports

A module makes its providers available to the rest of the app only if it exports them:

```typescript
@Module({
  providers: [NotificationsService, NotificationsGateway],
  exports: [NotificationsService],  // only this is available to importers
})
export class NotificationsModule {}
```

If `BillingModule` wants `NotificationsService`, it imports `NotificationsModule`. `NotificationsGateway` is internal — `BillingModule` can't access it directly.

**Why this matters:** It enforces the same encapsulation you'd get from microservices (you can only call the public API of a module) without needing a network call.

### Global Modules

`PaymentsModule` is decorated with `@Global()`. This makes its exported providers (`PaymentsService`, `MonnifyService`, `JuicywayService`) available to every module without explicit imports. Use sparingly — overusing global modules defeats the purpose of explicit dependency tracking.

### Shared Infrastructure

`PrismaModule` and `RedisModule` are in `src/shared/` rather than `src/modules/`. This signals: these are infrastructure, not features. They're needed by virtually every module so they're designed to be imported everywhere (or registered globally).

---

## Part 8 — Authentication Deep Dive

The `AuthModule` contains some of the most important patterns in the codebase.

### Password Hashing with Argon2

When a user registers, their password is never stored. Instead:

```typescript
const passwordHash = await argon2.hash(dto.password);
```

Argon2 is the winner of the Password Hashing Competition (2015). It's specifically designed to be slow (expensive to compute) and memory-hard (expensive to brute-force with GPUs). The previous standard was bcrypt, then scrypt. Argon2 is the current gold standard.

**Why not MD5 or SHA256?** Those are general-purpose hash functions designed to be fast. Fast is bad for password hashing — it makes brute-force attacks trivial. An attacker with a GPU can compute billions of MD5 hashes per second. Argon2 is deliberately designed so each hash takes meaningful memory and CPU.

**Why Argon2 specifically over bcrypt?**

bcrypt is not broken. It's been used for decades and is still considered secure. But it was designed in 1999, before GPU-based password cracking was a real threat.

The problem with bcrypt at a hardware level: each bcrypt computation uses very little memory. A modern GPU has thousands of cores and can compute thousands of bcrypt hashes in parallel. An attacker with a consumer GPU can try billions of passwords per day.

Argon2 was designed in 2015 specifically to defeat this attack. It has three tunable parameters:
- **Time cost** — how many iterations to run (like bcrypt's cost factor)
- **Memory cost** — how much RAM each hash requires (e.g., 64MB)
- **Parallelism** — how many threads to use

The memory cost is the key weapon. If each Argon2 hash requires 64MB of RAM, and a GPU has 8GB of VRAM, you can only run 128 hashes simultaneously. bcrypt has no such constraint — you can run thousands in parallel. The memory requirement means GPU attacks on Argon2 are orders of magnitude more expensive than on bcrypt.

There are three Argon2 variants:
- `Argon2d` — fastest, resistant to GPU attacks, but vulnerable to side-channel attacks (timing attacks that infer data by measuring how long an operation takes)
- `Argon2i` — resistant to side-channel attacks, slightly slower
- `Argon2id` — hybrid of the two, and the one recommended for password hashing. Most libraries (including the `argon2` npm package) default to this

**Bottom line:** bcrypt is acceptable. Argon2id is better. If you're starting fresh (as this project is), use Argon2. If you have an existing system on bcrypt, it's not worth migrating — bcrypt is still fine. The difference matters most when someone gets your password hash database and tries to crack it offline.

**Verification:**
```typescript
const passwordValid = await argon2.verify(user.passwordHash, dto.password);
```

You never decrypt a hash. You hash the input again and compare.

### JWT Tokens

JWTs (JSON Web Tokens) are how the API knows who is calling.

After login, the server issues two tokens:
- **Access token** — short-lived (typically 15min-1hr), sent with every API request
- **Refresh token** — long-lived (30 days here), used only to get a new access token

**Why two tokens?** Access tokens can't be revoked — if someone steals one, they can use it until it expires. By keeping them short-lived, the damage window is small. Refresh tokens are long-lived but stored in Redis and can be explicitly deleted (revoked) on logout.

The JWT payload (what's inside the token):
```typescript
{ sub: userId, email, username }
```

`sub` (subject) is the standard JWT claim for the user ID.

**Token rotation:** When you use a refresh token, the old one is deleted from Redis and a new pair is issued. This means a stolen refresh token can only be used once — if the attacker uses it first, the legitimate user's next refresh attempt fails (telling them their session was stolen).

### The Full JWT Flow — Frontend to Backend

This is the complete lifecycle, from first login to a request made three weeks later.

**Step 1: Login**
```
Frontend → POST /auth/login { email, password }
Backend  → returns { accessToken, refreshToken }
Frontend → stores accessToken in memory, refreshToken in secure storage
           (HttpOnly cookie or secure localStorage)
```

**Step 2: Every API request**
```
Frontend → GET /events
           Headers: { Authorization: "Bearer <accessToken>" }
Backend  → JwtAuthGuard intercepts the request
           → verifies the token signature with JWT_ACCESS_SECRET
           → decodes { sub: userId, email, username }
           → attaches user to request as req.user
           → controller runs
```

The access token is verified **without any database query**. This is the whole point of JWTs — they're self-contained. The server just checks the signature. This makes every authenticated request fast.

**Step 3: Access token expires**

The access token expires (15 minutes after login). The next API call returns `401 Unauthorized`. The frontend catches this and does not show the user a login screen. Instead:

```
Frontend → POST /auth/refresh
           Body: { refreshToken: "<stored refresh token>" }
Backend  → verifies the refresh token signature with JWT_REFRESH_SECRET
           → looks up the key "refresh:userId:refreshToken" in Redis
           → if the key exists: token is valid and not revoked
           → deletes the old key (the token is now consumed)
           → issues a NEW access token + NEW refresh token
           → stores the new refresh token key in Redis with 30-day TTL
           → returns { accessToken, refreshToken }
Frontend → updates stored tokens
           → retries the original failed request with the new access token
```

This happens silently. The user never sees a login prompt unless their refresh token has also expired or been revoked.

**Step 4: Logout**
```
Frontend → POST /auth/logout { refreshToken }
Backend  → deletes "refresh:userId:refreshToken" from Redis
           → access token is still technically valid until it expires
             but since it's short-lived, that's an acceptable window
```

**Step 5: Refresh token expires (30 days)**

The Redis key `refresh:userId:refreshToken` has a 30-day TTL. After 30 days of no activity, the key disappears. The next refresh attempt finds no key in Redis and returns `401`. The frontend now shows the login screen. The user was "remembered" for 30 days automatically.

**The security property this design gives you:**
- Stolen access token? Damage window = however long until expiry (currently infinite — bug, see Part 21)
- Stolen refresh token? Usable exactly once. If the attacker uses it first, the real user's next refresh attempt fails, alerting them something is wrong
- Logout from one device? Delete that device's refresh token key — that session is dead
- "Log out everywhere"? Delete all Redis keys matching `refresh:userId:*` — all sessions for that user are instantly revoked, regardless of how many devices they were on

**The current bug:** `expiresIn` is commented out in `generateTokens()`. Access tokens never expire. This eliminates the short-damage-window benefit entirely. Fix this before launch by uncommenting and setting `expiresIn: '15m'` for access tokens.

### Google OAuth

```typescript
const ticket = await this.googleClient.verifyIdToken({
  idToken,
  audience: GOOGLE_CLIENT_ID,
});
const payload = ticket.getPayload();
```

The frontend gets an `idToken` from Google's SDK. The backend verifies that token with Google's servers. Google tells you: "this token was issued to this user, for your application." You don't call a Google API yourself — you just verify the cryptographic signature.

**Account linking:** If a user registered with email/password and then tries to log in with Google using the same email, the code links the accounts rather than creating a duplicate. This is critical UX — users shouldn't have two accounts because they forgot which login method they used.

### Security: Email Enumeration Prevention

```typescript
// forgot password
if (!user) return { message: 'If that email exists, a reset link has been sent' };
```

If you return "user not found" when someone submits a non-existent email for password reset, you've told an attacker which emails are registered in your system. Always return the same message regardless of whether the email exists.

### Guards

`JwtAuthGuard` is applied globally in this project. Every route is protected by default. You opt OUT with `@Public()`:

```typescript
@Public()
@Post('webhook/juicyway')
```

This is the "secure by default" pattern. The alternative (protect routes explicitly with `@UseGuards()`) means forgetting to add the guard exposes a route. Secure by default means forgetting to add `@Public()` just means the route requires auth unnecessarily — a much less dangerous mistake.

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

The downside: every query must include `deletedAt: null` or you'll accidentally show deleted records. This is easy to forget and is a common source of bugs.

---

## Part 10 — The Games Module (Most Complex Logic)

The games module has the most business logic in the codebase. Understanding it teaches you how to model complex state machines.

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

### WebSocket Architecture

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

When a notification needs to reach user `abc`, you emit to room `user:abc`:
```typescript
this.server.to(`user:abc`).emit('notification', notification);
```

Only the socket in that room (i.e., that user's connection) receives it.

**Scaling problem:** Socket.io rooms are in-memory in this process. If you run two API instances, a user connected to instance 1 won't receive events emitted by instance 2. The fix: Socket.io Redis adapter (the `redis.service.ts` even exposes `getClient()` for this exact reason). This is one of the first things to add when you need horizontal scaling.

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

## Part 16 — Analytics

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

## Part 17 — The Messaging Module

DMs between users follow the mutual-follow requirement (enforced in `UserPreference.messagingPref`).

The `Conversation` model uses a canonical ordering pattern. When user A starts a conversation with user B, you ensure `userAId < userBId` alphabetically (by sorting the two IDs). This means there's only ever one conversation record for any pair — you can look it up with `@@unique([userAId, userBId])` regardless of which user initiates.

The `lastMessageAt` field on `Conversation` is updated every time a message is sent. The inbox is ordered by `lastMessageAt DESC` — conversations with recent activity float to the top.

**What's missing:** Message read receipts at scale. The current `isRead: Boolean` on `Message` doesn't handle "last read message ID" per user, which is what most messaging apps use for accurate unread counts without marking every message individually.

---

## Part 18 — The Storage Module

File uploads (avatars, event fliers, postcard media) go through the storage module. Based on `upload.service.ts` existing alongside `storage.service.ts`, uploads likely:
1. Accept multipart/form-data
2. Upload to a cloud storage provider (S3-compatible, based on `storageConfig`)
3. Return a public URL stored on the relevant model (`avatarUrl`, `flierUrl`, `mediaUrl`)

**Design consideration:** Storing file URLs in the database means if you change storage providers, you need a migration to update all URLs. A better pattern: store only the `storageKey` (the file path within your bucket) and compute the URL at read time. The `PostcardMedia` model does this right with a separate `storageKey` field.

---

## Part 19 — The Admin Module

Admin routes are protected by role check:

```typescript
// users.prisma
role UserRole @default(USER)
// UserRole enum: USER | ADMIN | SUPER_ADMIN
```

The admin module likely handles: user banning, coupon creation, platform analytics, and event moderation. Role-based access control (RBAC) is the pattern — the role is stored on the user and checked in guards or service methods.

---

## Part 20 — Cross-Cutting Concerns

These are things that apply across the entire system.

### Rate Limiting

```typescript
ThrottlerModule.forRoot([{ ttl: 60, limit: 100 }])
```

100 requests per 60 seconds per IP. This is a basic defence against:
- Brute-force attacks (trying many passwords)
- Scraping (downloading all events)
- DoS (overwhelming the server with requests)

**What's missing:** Per-route rate limits. Auth endpoints should be much more restricted (10 per minute, not 100). Payment endpoints should have their own limits. Global limits are a start but not sufficient for production.

### Request Validation

NestJS uses `class-validator` decorators in DTO classes. Every controller action receives a typed DTO, and NestJS validates the incoming JSON against it before the controller method runs. Invalid requests are rejected with 400 automatically.

This happens in the global `ValidationPipe` (typically configured in `main.ts`).

### Error Handling

NestJS has built-in exception handling. Throwing:
- `NotFoundException` → 404
- `BadRequestException` → 400
- `ForbiddenException` → 403
- `ConflictException` → 409
- `UnauthorizedException` → 401

The framework translates these to the correct HTTP status codes. You never manually set status codes in this codebase.

### Transactions

```typescript
await this.prisma.$transaction(async (tx) => {
  // all operations inside here are atomic
  await tx.organizerPayment.update({ ... });
  await tx.eventPlan.upsert({ ... });
  await tx.event.update({ status: 'PUBLISHED' });
});
```

A transaction means either ALL operations succeed or ALL are rolled back. When activating a plan payment, you want the payment marked COMPLETE, the EventPlan created, AND the event published — atomically. If the event update fails halfway through, you don't want the payment marked complete with a broken state.

Use transactions any time two or more writes must succeed together.

---

## Part 21 — What is Missing and Should Be Built

These are genuine gaps in the current codebase that would need to be addressed before a production launch.

### 1. Job Queue for Background Work (BullMQ)

Currently, the event reminder cron job runs in the same process as the API:

```typescript
@Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
async handleEventReminders() {
  // sends emails to ALL upcoming event attendees in a single run
}
```

Problems:
- If there are 10,000 RSVPs across upcoming events, this loops and sends 10,000 emails in one cron tick. The process is blocked for potentially minutes
- If the cron fails halfway, some users get reminders and some don't — no retry mechanism
- Email sending is synchronous (`await this.sendEmail(...)`) inside the loop

**The fix:** BullMQ (a Redis-based job queue). Instead of sending emails directly, enqueue one job per recipient:

```typescript
for (const rsvp of event.rsvps) {
  await emailQueue.add('event-reminder', { userId: rsvp.userId, eventId: event.id });
}
```

A separate worker process picks up jobs and processes them, with automatic retries on failure. The API stays fast, emails are processed reliably in the background.

The `redis.service.ts` already exposes `getClient()` specifically for this purpose — the infrastructure is there, the queue just needs to be wired up.

### 2. Socket.io Redis Adapter

As mentioned in Part 12, running multiple API instances breaks WebSocket notifications. Add:

```typescript
import { createAdapter } from '@socket.io/redis-adapter';
const pubClient = redisService.getClient();
const subClient = pubClient.duplicate();
io.adapter(createAdapter(pubClient, subClient));
```

Every instance subscribes to a shared Redis pub/sub channel. When instance 1 wants to notify a user connected to instance 2, it publishes to Redis, and instance 2 delivers it.

### 3. Missing `expiresIn` on JWT Tokens

```typescript
const accessToken = this.jwtService.sign(payload, {
  secret: JWT_ACCESS_SECRET,
  // expiresIn: ... ← COMMENTED OUT
});
```

This is a security vulnerability. Without `expiresIn`, access tokens never expire. If a token is stolen, it's valid forever. This must be fixed before launch.

```typescript
expiresIn: '15m',  // access token expires in 15 minutes
```

### 4. Coupon Race Condition

```typescript
// check usage limit
if (coupon.usageLimit !== null && coupon.usageCount >= coupon.usageLimit) {
  throw new BadRequestException('Coupon usage limit reached');
}
// ... time passes ...
// increment usage
await this.prisma.coupon.update({ data: { usageCount: { increment: 1 } } });
```

Between the check and the increment, another request could pass the check simultaneously. Both get past the limit check, both increment. The coupon ends up used more times than allowed.

**The fix:** Use a database-level atomic increment with a check, or a database transaction with a row lock:

```typescript
// atomic: only increments if the condition is met
await this.prisma.$executeRaw`
  UPDATE coupons 
  SET usage_count = usage_count + 1 
  WHERE id = ${couponId} AND (usage_limit IS NULL OR usage_count < usage_limit)
`;
```

Or use `SELECT FOR UPDATE` to lock the row during the transaction.

### 5. Webhook Endpoint Security: IP Allowlisting

The Juicyway webhook endpoints are `@Public()` — no authentication. The HMAC signature check is good, but for extra defence you should also verify that the request comes from Juicyway's IP ranges. If Juicyway publishes their outbound IP ranges, you can block requests from any other IP before even parsing the payload.

### 6. Missing Token Expiry on Email Verification

```typescript
emailVerifyExpiry: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24hrs
```

The verification token is set correctly. But the `TODO: queue verification email` comment shows the email is never actually sent. The token exists in the database but the user never receives the email to click. This needs to be wired up.

### 7. No Pagination on Some Endpoints

Some endpoints that could return large datasets don't paginate. For example, game session rewards and leaderboards. At scale, returning the entire leaderboard in one response is expensive and slow.

### 8. Soft Delete Not Applied Consistently

`deletedAt` is only used on `GameSession`. Other models are hard-deleted with `prisma.xxx.delete()`. This means if an organizer deletes a ticket tier, the `Ticket` rows linked to it either cascade-delete (losing ticket history) or fail (if referential integrity blocks it). A consistent soft-delete strategy across the domain would be safer.

### 9. Missing Database Indices on Hot Query Paths

The `notifications` table (which will be queried on every page load for unread count) doesn't have a composite index on `[recipientId, isRead]`. Adding this would make the unread count query significantly faster.

---

## Part 22 — Design Decisions Worth Understanding

### Why Split the Prisma Schema Across Files?

```
prisma/schema/
  user.prisma
  events.prisma
  tickets.prisma
  ...
```

Prisma supports multi-file schemas. The benefit: each domain owns its own schema file. The `billing.prisma` file is owned by the billing team; they don't touch `games.prisma`. In a monorepo with multiple engineers, this reduces merge conflicts significantly.

### Why `upsert` Instead of `create`?

```typescript
await this.prisma.follow.upsert({
  where: { followerId_followingId: { followerId, followingId } },
  create: { followerId, followingId },
  update: {},  // do nothing if already exists
});
```

`upsert` is atomic. Without it, you'd do a `findUnique` check then a `create`. Between the check and the create, a concurrent request could also pass the check and both would try to create — causing a unique constraint violation. `upsert` collapses this into a single database operation.

### Why `nanoid` Instead of `uuid` for Share Tokens?

`uuid()` generates: `550e8400-e29b-41d4-a716-446655440000` — 36 characters, not URL-friendly.

`nanoid(10)` generates: `V1StGXR8_Z` — 10 characters, URL-safe, collision probability is negligible for this use case.

Share tokens go in URLs (`/game/join/V1StGXR8_Z`). Shorter and cleaner. UUIDs are used for primary keys because they're the standard for database IDs.

### Why `Decimal` for Money?

```typescript
price Decimal @default(0) @db.Decimal(10, 2)
```

`Float` in most languages/databases is a binary floating-point number. It cannot represent every decimal fraction exactly. `0.1 + 0.2` in floating point is `0.30000000000000004`. For money, this is catastrophic — you'd have rounding errors in financial calculations.

`Decimal` stores numbers as exact decimal values. `0.10 + 0.20 = 0.30`, always. Use `Decimal` for any financial field, always.

### Why Separate `OrganizerPayment` From `TicketPurchase`?

They represent completely different business concepts:
- `TicketPurchase` — money from an attendee TO an organizer (via the platform)
- `OrganizerPayment` — money from an organizer TO NextVibe (platform fees)

Different actors, different purposes, different activation logic, different webhook handlers. Merging them would create a confusing table with many nullable columns depending on payment type.

This is the **Single Responsibility Principle** applied at the database level: each table represents one concept.

---

## Part 23 — How to Think About Improving This Codebase

When you inherit a codebase and need to improve it, always prioritise in this order:

**1. Security gaps first.** The missing JWT `expiresIn` is a P0 — fix it before anything else. Security vulnerabilities compound.

**2. Data integrity second.** The coupon race condition and missing idempotency protections can cause financial discrepancies. These are hard to detect and harder to fix after data is corrupted.

**3. Reliability third.** The synchronous email sending in the cron job will eventually fail silently. Move long-running jobs to a queue.

**4. Performance last.** Add indices and caching after you know which queries are slow, not before. Premature optimisation wastes time.

When reading code you want to improve, always ask:
- What happens if this fails halfway through?
- What happens if two requests run this simultaneously?
- What happens when the dataset is 100× larger?

If the answer to any of these is "something bad", you've found something worth improving.

---

## Part 24 — The Mental Model for Being a Good Engineer

Everything you build is a trade-off. The question is never "what's the perfect solution?" — it's always "what's the right trade-off for this context?"

**Monolith vs microservices?** Right answer depends on team size, product maturity, traffic patterns.

**Hardcoded prices vs database prices?** Right answer depends on how often prices change and who needs to change them.

**Soft delete vs hard delete?** Right answer depends on regulatory requirements and audit needs.

**Polling vs WebSocket for notifications?** Right answer depends on how real-time you need it and how much infrastructure complexity you can manage.

The engineers who built this codebase made reasonable decisions for where the product is. As the product grows, some decisions will need to be revisited — not because they were wrong, but because the context changed.

Your job as an engineer is not to write perfect code. It's to understand the trade-offs, make the best call given the current context, and leave the system better than you found it.

Every design decision in this codebase was made for a reason. When you encounter code that seems wrong, ask "why might someone have written it this way?" before assuming it's a mistake. Often you'll find a constraint or context you weren't aware of.

---

## Part 25 — Deploying to Production: CI/CD, Build Pipelines, and the Mistakes That Break Them

Deploying is the step where your working local code becomes a running server that real users hit. It fails in ways that are invisible locally, for reasons that feel baffling until you understand the concepts. This part explains those concepts using the actual production failure this project experienced.

---

### What Happens When You Deploy to Render (or Any Cloud Host)

When you push to your repo and Render picks it up, it:

1. Clones your repository onto a fresh machine — a machine that has nothing installed except the OS, Node, and the tools Render provides
2. Runs your **Build Command** — the commands that turn your TypeScript source into runnable JavaScript
3. Runs your **Start Command** — the command that starts the server

The key insight: **the build machine is a blank slate.** It does not have your local `node_modules`. It does not inherit your local environment. Every tool your build process needs must be installed from scratch.

---

### What `--frozen-lockfile` Means and Why It Exists

When you run `pnpm install` locally, pnpm reads `package.json`, resolves versions, downloads packages, and writes a snapshot of every resolved version to `pnpm-lock.yaml`. This lockfile is the exact recipe for the installation.

`--frozen-lockfile` tells pnpm: "Do not update the lockfile. If the lockfile and `package.json` are out of sync, fail immediately."

**Why does CI/CD use `--frozen-lockfile`?**

Without it, if a developer forgot to commit an updated lockfile, the CI machine would silently re-resolve packages — potentially installing different versions than what was tested locally. A bug could exist only in production because production got a slightly different package. `--frozen-lockfile` makes "lockfile matches package.json" a hard requirement. The build fails loud and early rather than silently installing the wrong thing.

**The rule:** always commit your lockfile. Always. Every `package.json` change must be followed by `pnpm install` and a commit of the updated `pnpm-lock.yaml`.

---

### Bug #1: `pnpm` in `dependencies` → Worker Exits With Code 1

The project had this in `package.json`:

```json
"dependencies": {
  ...
  "pnpm": "^11.1.2",
  ...
}
```

This caused the build to crash immediately with `Worker pnpm#1 exited with code 1`.

**Why?**

`pnpm` is a package manager — a CLI tool that manages packages. It is not a library your app imports. When you put it in `dependencies`, the running pnpm process tries to install... pnpm itself. The pnpm package has its own postinstall lifecycle scripts that try to register itself as a package manager, which conflicts with the already-running pnpm process. The worker crashes.

**The correct approach:** package managers, build tools, and CLI utilities that you don't `import` in your code do not belong in `dependencies`. They belong in one of:

| Where | What it means |
|---|---|
| `devDependencies` | Used during development/build, not at runtime |
| `engines` field | Declares the minimum version required, doesn't install anything |
| `packageManager` field | Declares the exact package manager used (Node.js Corepack feature) |

For this project, pnpm was removed from `dependencies` entirely. The correct way to declare "this project uses pnpm 11" is:

```json
"engines": {
  "node": ">=20.0.0",
  "pnpm": ">=11.0.0"
}
```

Or with Corepack:

```json
"packageManager": "pnpm@11.1.2"
```

Neither of these installs pnpm — they're just documentation constraints. pnpm is already installed globally on the build machine.

**Lesson:** `dependencies` are packages your app imports at runtime. `devDependencies` are packages used during development and build. Never put a CLI tool, package manager, or build tool in `dependencies` unless your app literally `import`s it.

---

### Bug #2: `nest: not found` → `NODE_ENV=production` Skipping DevDependencies

Even if the install succeeded, the build would then fail with:

```
sh: 1: nest: not found
```

`nest` is the NestJS CLI. It's what runs `nest build` to compile TypeScript. It's in `devDependencies`:

```json
"devDependencies": {
  "@nestjs/cli": "^11.0.0",
  ...
}
```

**Why wasn't it installed?**

Render (like most cloud hosts) sets `NODE_ENV=production` during the build. When `NODE_ENV=production`, pnpm's default behaviour is to skip `devDependencies` — because on a production server, you don't want dev tools like test runners, type checkers, and linters installed. It saves disk space and install time.

The problem: **your build tools live in devDependencies, but the build runs in production mode.**

This is a genuine tension in Node.js tooling. There are two ways to resolve it:

**Option A: Add `--prod=false` to the install command (used here)**

```
pnpm install --frozen-lockfile --prod=false
```

`--prod=false` explicitly tells pnpm "ignore `NODE_ENV`, install devDependencies too." This ensures `@nestjs/cli`, `typescript`, `ts-node`, `prisma` (the CLI, not `@prisma/client`) and all other build tools are available during the build step.

**Option B: Move build tools to `dependencies`**

Some teams move `@nestjs/cli` and `typescript` to regular `dependencies`. This works but is semantically wrong — these tools are not used by the running server, they're only used to compile it. Mixing them into `dependencies` bloats your production node_modules.

Option A is cleaner. The full Render build command for this project:

```
pnpm install --frozen-lockfile --prod=false; pnpm run db:deploy; pnpm dlx prisma generate; pnpm run build
```

---

### Understanding the Full Build Command

Let's break down each step:

```
pnpm install --frozen-lockfile --prod=false
```
Install all dependencies (including dev). Fail if lockfile is out of sync.

```
pnpm run db:deploy
```
Runs `prisma migrate deploy` — applies any pending database migrations. The `db:deploy` script in this project first uses `prisma migrate resolve --applied` to mark some historical migrations as already-applied (because they were manually applied and Prisma's migration history doesn't know about them), then runs `deploy` to apply anything new. This ensures the database schema matches the code before the code starts.

```
pnpm dlx prisma generate
```
Generates the Prisma Client TypeScript types from the schema. The generated client lives in `src/generated/prisma`. Without this step, `@prisma/client` has no types and the app can't compile. Note: `pnpm dlx` runs a command from a remote package without installing it globally — it's like `npx` for pnpm.

```
pnpm run build
```
Runs `nest build`, which uses the NestJS CLI to invoke the TypeScript compiler (tsc) and output JavaScript to `dist/`. This is the compiled server that will actually run.

---

### Why `@prisma/client` Is Listed in `dependencies` But Still Needs `prisma generate`

`@prisma/client` in `dependencies` installs the runtime client library — the JavaScript code that connects to Postgres and runs queries. But the actual TypeScript types and the generated client code are specific to your schema. They live in `src/generated/prisma` and are produced by `prisma generate`.

Without running `prisma generate`, your code can import `@prisma/client` but will get no type information and no client tailored to your schema. This is why `prisma generate` must always run as part of the build, not just when you change the schema.

The `prisma` CLI package (which runs `generate`) is in `devDependencies`. It's needed at build time, not at runtime. The `@prisma/client` package (runtime) is in `dependencies`. Two different packages, two different purposes.

---

### The `postbuild` Script: Copying Generated Files

```json
"postbuild": "pnpm run copy:prisma"
```

`copy:prisma` does:
```bash
mkdir -p dist/src/generated && cp -r src/generated/prisma dist/src/generated/
```

NestJS compiles TypeScript to `dist/`. But the Prisma-generated files in `src/generated/` are already JavaScript (generated by Prisma, not by you). `tsc` doesn't necessarily copy them into `dist/`. The `postbuild` step manually copies the generated client into the `dist/` folder so the compiled server can find it at runtime.

**The `post` prefix:** in npm/pnpm scripts, any script prefixed with `post` automatically runs after the matching script. `postbuild` runs after `build`. `pretest` would run before `test`. This is a built-in convention, not a custom feature.

---

### How to Debug a Failed Production Build

When a build fails in CI/CD, here is the process:

1. **Read the exact error message.** "Worker pnpm#1 exited with code 1" means a pnpm child process crashed. "nest: not found" means a binary isn't in PATH. "Could not resolve @prisma/client" means Prisma wasn't generated.

2. **Map the error to the step that caused it.** Build commands run sequentially. If step 1 fails, step 2 never runs. In this case, the `pnpm install` worker crash meant prisma and nest also failed — not because they had their own problems, but because the install never completed.

3. **Check `package.json` and `pnpm-lock.yaml` for inconsistencies.** Is a package in the wrong section? Is the lockfile behind? Does `package.json` have something that doesn't belong?

4. **Check whether `NODE_ENV` affects the build.** If your build host sets `NODE_ENV=production`, know that this changes install behaviour.

5. **Reproduce locally with the same flags.** Run `NODE_ENV=production pnpm install --frozen-lockfile` locally. If it fails the same way, you've reproduced it and can iterate faster than pushing and waiting for CI.

6. **Work top to bottom.** Fix the first error, see what happens next. Don't try to fix all errors at once — they may be cascading from a single root cause.

---

### Summary: What to Never Do in `package.json`

| Mistake | Why It Breaks |
|---|---|
| Put a package manager (`pnpm`, `npm`, `yarn`) in `dependencies` | Postinstall lifecycle conflicts; package managers manage other packages, not themselves |
| Put build-only tools in `dependencies` | Bloats production node_modules with unused tools |
| Forget to commit `pnpm-lock.yaml` after changes | `--frozen-lockfile` fails; CI installs different versions than local |
| Use `pnpm install --frozen-lockfile` without `--prod=false` on a host that sets `NODE_ENV=production` | devDependencies (including CLI tools) are skipped; build fails |

---

---

## Part 26 — How to Contribute

This section covers what you need to know before writing code against this codebase for the first time.

---

### Adding a New Module

Every feature in this codebase is a NestJS module. When you add a feature, you add a module. Here is the exact pattern to follow.

**Step 1: Create the folder**

```
src/modules/your-feature/
  your-feature.module.ts
  your-feature.controller.ts
  your-feature.service.ts
  dto/
    create-your-feature.dto.ts
    update-your-feature.dto.ts
```

**Step 2: Write the module file**

```typescript
@Module({
  imports: [PrismaModule],           // add shared infrastructure you need
  controllers: [YourFeatureController],
  providers: [YourFeatureService],
  exports: [YourFeatureService],     // only export if other modules need it
})
export class YourFeatureModule {}
```

**Step 3: Register it in `app.module.ts`**

```typescript
@Module({
  imports: [
    // ... existing modules
    YourFeatureModule,
  ],
})
export class AppModule {}
```

**Step 4: Keep the controller thin**

Controllers receive a request, delegate to the service, return the result. They do not contain logic. If you find yourself writing an `if` statement in a controller method, it belongs in the service.

---

### Naming Conventions

Following these consistently means any engineer can find anything without searching.

| Thing | Convention | Example |
|---|---|---|
| Module folder | kebab-case | `ticket-transfers/` |
| Class names | PascalCase | `TicketTransfersService` |
| File names | kebab-case | `ticket-transfers.service.ts` |
| DTO class | PascalCase + Dto suffix | `InitiateTransferDto` |
| Route prefix | kebab-case | `@Controller('ticket-transfers')` |
| Prisma model | PascalCase | `TicketTransfer` |
| Database table | snake_case (Prisma maps it) | `ticket_transfers` |
| Enum values | SCREAMING_SNAKE_CASE | `TRANSFER_PENDING` |

For any new table, add `@@map("snake_case_name")` in the Prisma model to be explicit about the table name — don't rely on Prisma's default inference.

---

### Adding a Database Model

The schema is split by domain in `prisma/schema/`. Put your model in the file that owns its domain. If the model doesn't belong to an existing domain, create a new `.prisma` file.

**Step 1: Add the model to the appropriate schema file**

```prisma
// prisma/schema/tickets.prisma
model TicketTransfer {
  id          String   @id @default(cuid())
  ticketId    String
  fromUserId  String
  toUserId    String
  createdAt   DateTime @default(now())

  ticket   Ticket @relation(fields: [ticketId], references: [id])
  fromUser User   @relation("TransferFrom", fields: [fromUserId], references: [id])
  toUser   User   @relation("TransferTo", fields: [toUserId], references: [id])

  @@index([ticketId])
  @@map("ticket_transfers")
}
```

**Step 2: Create and apply the migration**

```bash
# generate a new migration file (does not apply it yet)
pnpm prisma migrate dev --name add_ticket_transfers

# this also runs prisma generate automatically in dev
```

**Step 3: Never manually edit migration files**

Prisma generates SQL migration files in `prisma/migrations/`. Never edit them by hand. If you made a mistake in your schema, fix the schema file and generate a new migration. Editing migration files breaks the migration history and causes the `db:deploy` step to fail in CI.

**Step 4: Always add indexes for columns you query on**

Before adding a model, ask: what queries will I run against this table? Add `@@index` entries for every column that will appear in a `WHERE` clause or `ORDER BY`. This is especially important for foreign keys — Prisma does not automatically index them.

---

### The Migration Workflow in This Project

This project uses `prisma migrate deploy` (not `migrate dev`) in production. The difference:

- `migrate dev` — used locally. Generates new migration files from schema changes. Runs generators. Prompts you for a migration name.
- `migrate deploy` — used in CI/CD. Applies pending migrations without generating anything. Fails if there are unapplied migrations. Never prompts.

The build command on Render runs:
```
pnpm run db:deploy  # applies pending migrations
pnpm dlx prisma generate  # regenerates the client types
```

**What this means for you:** After changing the schema, run `pnpm prisma migrate dev` locally, commit both the schema change and the generated migration file, and push. The next deploy will pick up the migration automatically.

If you forget to commit the migration file, the deploy will succeed (the code compiled) but the app will crash at runtime when it tries to use a table that doesn't exist.

---

### Adding a New API Endpoint

1. Add a method to the relevant controller with the correct HTTP decorator (`@Get`, `@Post`, `@Patch`, `@Delete`)
2. Create a DTO in `dto/` for any request body using `class-validator` decorators
3. Implement the logic in the service
4. Routes are protected by default — add `@Public()` only if the endpoint genuinely needs no authentication

```typescript
// dto/create-item.dto.ts
export class CreateItemDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsNumber()
  @Min(0)
  price: number;
}

// controller
@Post()
create(@CurrentUser() user: JwtPayload, @Body() dto: CreateItemDto) {
  return this.itemsService.create(user.sub, dto);
}
```

The `@Body()` DTO is automatically validated by the global `ValidationPipe` in `main.ts`. If validation fails, NestJS returns a `400 Bad Request` before your method runs.

---

### What to Check Before Submitting

Before marking work as ready for review, go through this list:

**Correctness**
- [ ] Does the endpoint handle the case where a resource doesn't exist? (`NotFoundException`)
- [ ] Does the endpoint check that the calling user has permission to act on the resource? (`ForbiddenException`)
- [ ] If two writes must happen together, are they in a `$transaction`?

**Database**
- [ ] Have you added `@@index` entries for every column you filter or sort on?
- [ ] Is your migration file committed alongside the schema change?
- [ ] Did you run `pnpm prisma generate` after the schema change?

**Security**
- [ ] Is the route correctly protected (or deliberately `@Public()`)?
- [ ] Are you validating all user-provided input with DTO decorators?
- [ ] If handling a webhook, is the signature verified before processing?

**Reliability**
- [ ] If an operation can be called twice (by retry or duplicate request), is it idempotent?
- [ ] If the operation is long-running (sending many emails, processing many records), should it be a queued job instead of a direct call?

---

*Document covers codebase as of May 2026. Module list: Auth, Users, Events (+ RSVP), Tickets, Payments (Juicyway + Monnify), Billing (Pricing, Coupons, OrganizerPayments), Games (Sessions, Rounds, Rewards, AI generation), Notifications (WebSocket + Resend), Social (Follows, Likes, Comments, Shares, Feed), Messaging (DMs + EventChat), Storage, Discovery, Admin, VibeTags, Postcards.*
