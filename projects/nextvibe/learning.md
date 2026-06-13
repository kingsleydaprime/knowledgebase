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

**What's missing:** The `notifications` table has no index on `[recipientId, isRead]`. The unread count query is `WHERE recipientId = ? AND isRead = false`. Without this compound index, every page load that shows a notification badge does a full scan of all notifications for that user. At 100 notifications per user and 10,000 users making simultaneous requests, this becomes a problem fast. This is noted in Part 20.

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
- Stolen access token? Damage window = however long until expiry (currently infinite — bug, see Part 20)
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

---

## Part 17 — The Storage Module

File uploads (avatars, event fliers, postcard media) go through the storage module. Based on `upload.service.ts` existing alongside `storage.service.ts`, uploads likely:
1. Accept multipart/form-data
2. Upload to a cloud storage provider (S3-compatible, based on `storageConfig`)
3. Return a public URL stored on the relevant model (`avatarUrl`, `flierUrl`, `mediaUrl`)

**Design consideration:** Storing file URLs in the database means if you change storage providers, you need a migration to update all URLs. A better pattern: store only the `storageKey` (the file path within your bucket) and compute the URL at read time. The `PostcardMedia` model does this right with a separate `storageKey` field.

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

## Part 19 — Cross-Cutting Concerns

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

## Part 20 — What is Missing and Should Be Built

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

## Part 21 — Design Decisions Worth Understanding

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

## Part 22 — How to Think About Improving This Codebase

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

## Part 23 — The Mental Model for Being a Good Engineer

Everything you build is a trade-off. The question is never "what's the perfect solution?" — it's always "what's the right trade-off for this context?"

**Monolith vs microservices?** Right answer depends on team size, product maturity, traffic patterns.

**Hardcoded prices vs database prices?** Right answer depends on how often prices change and who needs to change them.

**Soft delete vs hard delete?** Right answer depends on regulatory requirements and audit needs.

**Polling vs WebSocket for notifications?** Right answer depends on how real-time you need it and how much infrastructure complexity you can manage.

The engineers who built this codebase made reasonable decisions for where the product is. As the product grows, some decisions will need to be revisited — not because they were wrong, but because the context changed.

Your job as an engineer is not to write perfect code. It's to understand the trade-offs, make the best call given the current context, and leave the system better than you found it.

Every design decision in this codebase was made for a reason. When you encounter code that seems wrong, ask "why might someone have written it this way?" before assuming it's a mistake. Often you'll find a constraint or context you weren't aware of.

---

## Part 24 — Deploying to Production: CI/CD, Build Pipelines, and the Mistakes That Break Them

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

## Part 25 — Development Environment Problems and How to Solve Them

These are errors that happen on your local machine during development, not in production. They feel catastrophic the first time you see them. Once you understand what they mean, they take less than a minute to fix.

---

### `ENOSPC: System limit for number of file watchers reached`

**The full error:**

```
Error: ENOSPC: System limit for number of file watchers reached,
watch '/home/.../src/generated/prisma/wasm-edge-light-loader.mjs'
    at FSWatcher.<computed> (node:internal/fs/watchers:247:19)
    ...
  errno: -28,
  code: 'ENOSPC',
```

**What you were doing when it appeared:** Running `pnpm run start:dev` — the NestJS watch mode compiler. Everything compiled fine (`Found 0 errors. Watching for file changes.`), then the process crashed.

**Why `ENOSPC` is misleading:** `ENOSPC` stands for "No Space on Device." Your first instinct is to check disk space. That's wrong. This error has nothing to do with disk space. It's about a Linux kernel resource called **inotify**.

**What inotify is:**

Linux uses a kernel subsystem called `inotify` to implement file watching. When a program wants to know when a file changes, it asks the kernel to "watch" that file. The kernel maintains a list of all active watches across all processes on the machine.

By default, Linux caps this list at **65,536 watches total** across all processes. When the cap is hit, the error code is `ENOSPC` — because the kernel reports "no space" in the watch table, even though your disk is fine.

**Why this project hits the limit:**

The NestJS watch mode compiler (via `chokidar`) registers an inotify watch on every file it monitors. This project has a `src/generated/prisma/` directory containing many generated files from Prisma. Combined with the rest of `src/`, `node_modules/.pnpm/`, and any other projects or editors you have open on the same machine (VS Code alone consumes thousands of watches), the total exceeds 65,536.

**How to check the current limit:**

```bash
cat /proc/sys/fs/inotify/max_user_watches
# outputs: 65536
```

**The fix — increase the limit permanently:**

```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

`/etc/sysctl.conf` is the kernel parameter configuration file. Changes here survive reboots. `sysctl -p` reloads the file immediately without rebooting. After this, the limit is 524,288 — eight times the default, more than enough for any development machine.

**For an immediate fix without rebooting (does not survive reboot):**

```bash
sudo sysctl fs.inotify.max_user_watches=524288
```

**Why 524,288?** It is the standard recommended value in the documentation for VS Code, Webpack, Jest, and other watch-heavy tools. It's high enough that you will never hit the ceiling in normal development, while still being a finite cap that prevents a runaway process from consuming unlimited kernel resources.

**After applying the fix:** Restart `pnpm run start:dev`. The error will not appear again.

**Key lesson:** `ENOSPC` in Node.js file watcher errors does not mean disk space. It means a kernel resource table is full. Always check the full error message — `code: 'ENOSPC'` combined with `syscall: 'watch'` is the giveaway that it's inotify, not disk.

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

## Part 27 — Duplicate Controller Routes: The Silent Killer

### The Setup

You have two NestJS modules, both with controllers decorated `@Controller('organizer-payments')`:

- `BillingModule` → loads first in `AppModule.imports`
- `OrganizerPaymentsModule` → loads second

Both controllers define routes like `POST /organizer-payments/initiate`, `GET /organizer-payments/history`, etc.

### What NestJS Does

NestJS registers routes in the order modules are loaded. When `BillingModule` loads first, its controller claims `/organizer-payments/*`. When `OrganizerPaymentsModule` loads, NestJS silently ignores the duplicate routes — no error, no warning. The first controller wins every request.

This means:
- Every `POST /organizer-payments/initiate` hits the billing controller's handler
- The newer, cleaner service in `OrganizerPaymentsModule` is never called
- You see no errors — requests succeed (or fail) with the wrong service

### How to Detect It

Look at your `AppModule.imports` array and grep for `@Controller('same-path')` across the codebase. If two files have the same controller prefix and both their modules are imported, you have a conflict.

```bash
grep -r "@Controller('organizer-payments')" src/
```

### The Fix

Remove the controller from whichever module should not own the route. In this codebase, `BillingModule` handled organizer payments while the dedicated `OrganizerPaymentsModule` was being built. Once `OrganizerPaymentsModule` was ready, `BillingModule`'s controller was removed — but the provider and exports stayed:

```typescript
@Module({
  imports: [HttpModule.register({ timeout: 30000, maxRedirects: 5 }), ConfigModule, PrismaModule, NotificationsModule],
  // controllers: [] — removed OrganizerPaymentsController entirely
  providers: [PricingService, CouponsService, OrganizerPaymentsService, ErcaspayService],
  exports: [PricingService, CouponsService, OrganizerPaymentsService, ErcaspayService],
})
export class BillingModule {}
```

The key insight: removing a controller from a module does not remove the service. Other modules that depend on the exported services continue to work fine.

### Lesson

When a feature "isn't working" and you can't find any error, check for duplicate route registration. It's invisible in logs and easy to miss during refactors where responsibility for a domain shifts from one module to another.

---

## Part 28 — Notification `targetId` Convention

### The Rule

`targetId` in a notification record should be the **entity acted upon**, not the actor.

The notification schema has:
- `actorId` — who performed the action (always the logged-in user)
- `recipientId` — who receives the notification
- `targetId` — what entity was acted upon
- `targetType` — the type of that entity (`USER`, `EVENT`, `POSTCARD`, etc.)

### FOLLOW Notification Example

When user A follows user B:
- `actorId` = A (the follower — who did the action)
- `recipientId` = B (who gets notified)
- `targetType` = `'USER'`
- `targetId` = B (the user who was followed — the entity acted upon)

The original code had `targetId: followerId` — the same value as `actorId`. This was redundant (you already have `actorId`) and inconsistent with how every other notification type works.

```typescript
// WRONG — targetId is the actor, redundant with actorId
this.notifications.create({
  recipientId: followingId,
  actorId: followerId,
  type: 'FOLLOW',
  targetType: 'USER',
  targetId: followerId,  // ← this is the actor, not the target
});

// CORRECT — targetId is the entity acted upon
this.notifications.create({
  recipientId: followingId,
  actorId: followerId,
  type: 'FOLLOW',
  targetType: 'USER',
  targetId: followingId,  // ← the user who was followed
});
```

### Why It Matters

Frontend reads `targetId` to know where to navigate when the user taps the notification. For a FOLLOW notification, tapping it should go to the followed user's profile — which is `followingId`. If `targetId` was `followerId`, you'd navigate to the actor's profile, which is the wrong person.

Applying this consistently across notification types:
- `LIKE` on a postcard → `targetId` = postcard's id, `targetType` = `'POSTCARD'`
- `COMMENT` on an event → `targetId` = event's id, `targetType` = `'EVENT'`
- `RSVP` to an event → `targetId` = event's id, `targetType` = `'EVENT'`
- `FOLLOW` → `targetId` = the followed user's id, `targetType` = `'USER'`

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

## Part 30 — HTTP Method Mismatches: Why Your Endpoint Returns 404 Instead of 405

### The Symptom

```
PATCH /v1/notifications/28ea18b6-2552-4566-862a-43886333eaa9/read  404  2.866 ms
```

The route exists. The ID is valid. But you get a 404. You check the database — the record is there. You check the guard — it would pass. Nothing seems wrong.

### The Cause

NestJS (and Express underneath it) matches routes by **both path and HTTP method**. If the controller registers `@Post(':id/read')` but the client sends a `PATCH`, NestJS finds no matching route and returns 404 — not 405 Method Not Allowed. The 404 is misleading because the *path* exists, just not for that method.

```typescript
// Controller has this:
@Post(':id/read')
markAsRead(@Param('id') id: string, @CurrentUser() user: JwtPayload) {
  return this.notificationsService.markAsRead(id, user.sub);
}

// Client is calling:
PATCH /v1/notifications/:id/read   ← wrong method → 404
```

### How to Spot It

Look at the startup logs. NestJS prints every registered route:

```
[RouterExplorer] Mapped {/v1/notifications/:id/read, POST} route
```

The log says `POST`. If your client is sending `PATCH`, that's your mismatch. Always check the startup log first when a route returns 404 and you're sure the path is correct.

### Why 404 and Not 405?

HTTP 405 (Method Not Allowed) is the *correct* response when a path exists but the method doesn't. NestJS/Express return 404 instead because they don't store "this path exists but not for this method" — they only store complete path+method combinations. If `PATCH /x` isn't registered, there is no registered route at all, and 404 is the fallback.

This is a known and somewhat annoying behaviour. The fix is always to match the method in the controller to what the client sends — or vice versa.

### Which Method Is Correct for "Mark as Read"?

Semantically, marking a notification as read is a partial update to a resource. The correct HTTP method is `PATCH`. `POST` is for creating things or non-idempotent actions. In this codebase, the controller used `@Post` but should use `@Patch` — or the frontend should send `POST` to match. Either works as long as both sides agree.

```typescript
// Correct:
@Patch(':id/read')
markAsRead(@Param('id') id: string, @CurrentUser() user: JwtPayload) {
  return this.notificationsService.markAsRead(id, user.sub);
}
```

### Key Rule

When a route you know exists returns 404:
1. Check the startup logs for the method NestJS registered it under
2. Check what method the client is sending
3. Fix the mismatch — usually one line in the controller decorator

---

## Part 31 — Reading Server Startup Logs to Detect Problems Before They Bite

### What the Startup Logs Tell You

Every time NestJS starts, `RouterExplorer` prints every registered route:

```
[RouterExplorer] Mapped {/v1/admin/coupons, POST} route
[RouterExplorer] Mapped {/v1/admin/coupons, POST} route   ← same route twice
```

Two lines for the same route is a red flag. It means two controllers are registered at the same path. As covered in Part 27, NestJS silently uses the first one and ignores the second. This log is your only warning — there is no error at runtime.

### Subtle Path Param Naming Differences

```
[RouterExplorer] Mapped {/v1/events/:id/rsvp, POST} route
[RouterExplorer] Mapped {/v1/events/:eventId/rsvp, POST} route
```

These look different (`:id` vs `:eventId`) so NestJS registers both. But they match the same incoming URLs — `/v1/events/abc/rsvp` matches both. The first one registered wins every request. The second controller's handler is dead code. You won't see an error. You'll see the wrong service being called.

**How to catch it:** After adding a new controller or route, scan the startup logs for:
- Identical path+method pairs (exact duplicates)
- Paths that differ only in param name (`:id` vs `:eventId`) — structurally identical

```bash
# Quick check: count routes, look for duplicates
grep "RouterExplorer.*Mapped" logs.txt | sort | uniq -d
```

### What Else to Watch in Startup Logs

| Log message | What it means |
|---|---|
| `[NestFactory] Starting Nest application...` | Bootstrap started |
| `[InstanceLoader] XModule dependencies initialized` | Module DI wired |
| `[RoutesResolver] XController {/v1/path}` | Controller scope registered |
| `[RouterExplorer] Mapped {/v1/path, METHOD}` | Individual route registered |
| `[NestApplication] Nest application successfully started` | Ready to serve |

If the app hangs between `InstanceLoader` and `RoutesResolver`, a provider constructor is likely blocking (synchronous DB call, infinite loop, missing env var causing a crash). If it hangs after all routes are mapped, the `listen()` call is failing (port in use, permission denied for ports < 1024).

### Reading a 403 from Logs Alongside Prior Events

Production logs tell a story. One example from this codebase:

```
09:26:01  POST /v1/users/A/follow      201   ← user 1 follows user A
09:26:31  POST /v1/users/B/follow      201   ← user 1 follows user B
09:43:50  POST /v1/auth/oauth/google   200   ← user 2 logs in
09:45:19  POST /v1/conversations       403   ← user 2 tries to DM someone
09:46:16  POST /v1/users/X/follow      201   ← user 2 starts following people
09:47:44  POST /v1/users/Y/follow      201
```

The 403 on `/conversations` isn't an auth problem — the user just logged in successfully. It's a **mutual follow** problem. User 2 is trying to DM someone they're not mutually following yet. The follow actions *after* the 403 confirm they're trying to fix it. You can read the sequence of events and understand intent from timestamps alone.

This skill — reading log timelines to understand what a user was doing — is one of the most valuable debugging tools you have in production.

---

## Part 32 — Migrating from Multipart File Upload to Presigned URLs

### The Problem with Multipart Upload Through NestJS

The original event creation flow used `FileFieldsInterceptor` — the client sent a `multipart/form-data` request with the binary file embedded in the HTTP body:

```
POST /v1/events
Content-Type: multipart/form-data

[text fields] + [binary file bytes]
```

NestJS receives the request, buffers the entire file into memory, then uploads it to MinIO. This means:
- A 50MB video stays in NestJS process memory during the entire upload
- If two users upload simultaneously, memory doubles
- Large files hit NestJS body size limits (default: `1mb` in many configs)
- The NestJS server becomes the bottleneck for something that has nothing to do with business logic

### The Presigned URL Solution

Instead of routing the binary through NestJS, you generate a **presigned URL** — a time-limited, signed URL that authorises the client to upload directly to MinIO/S3 without going through your server:

```
1. Client → NestJS:  POST /v1/storage/presigned-url   { filename, contentType }
2. NestJS → Client:  { uploadUrl, fileUrl }
3. Client → MinIO:   PUT uploadUrl   (binary file, direct — NestJS not involved)
4. Client → NestJS:  POST /v1/events { ..., flierUrl: fileUrl }
```

NestJS only handles step 1 (generates the URL, tiny request) and step 4 (receives the public URL as a JSON string, no binary). The heavy binary transfer happens directly between the client and storage, bypassing your application server entirely.

### What Changed in This Codebase

**Before:**

```typescript
// Controller used FileFieldsInterceptor
@UseInterceptors(FileFieldsInterceptor([
  { name: 'flier', maxCount: 1 },
  { name: 'video', maxCount: 1 },
]))
create(
  @CurrentUser() user: JwtPayload,
  @UploadedFiles() files: { flier?: Express.Multer.File[], video?: Express.Multer.File[] },
  @Body() dto: CreateEventDto,
) {
  return this.eventsService.create(user.sub, dto, files.flier?.[0], files.video?.[0]);
}

// Service required and uploaded the file
async create(organizerId: string, dto: CreateEventDto, flierFile?: Express.Multer.File) {
  if (!flierFile) {
    throw new BadRequestException('Event flier (image) is required');
  }
  const flierUrl = await this.uploadService.uploadFile(flierFile, 'event-fliers');
  // ...
}
```

**After:**

```typescript
// Controller: no interceptor, no file params — just JSON body
create(
  @CurrentUser() user: JwtPayload,
  @Body() dto: CreateEventDto,
) {
  return this.eventsService.create(user.sub, dto);
}

// DTO: flierUrl is now a plain optional string
export class CreateEventDto {
  // ...existing fields...

  @IsString()
  @IsOptional()
  @ApiPropertyOptional({ example: 'https://cdn.nextvibe.com/events/flier.jpg' })
  flierUrl?: string;

  @IsString()
  @IsOptional()
  @ApiPropertyOptional({ example: 'https://cdn.nextvibe.com/events/promo.mp4' })
  promoVideoUrl?: string;
}

// Service: no file parameter, no upload — reads URL directly from DTO
async create(organizerId: string, dto: CreateEventDto) {
  const flierUrl = dto.flierUrl ?? null;
  const promoVideoUrl = dto.promoVideoUrl ?? null;
  // ...rest of creation logic unchanged...
}
```

### Why `flierUrl` Became Optional

In the old multipart flow, the file was required — if no file was attached, you had nothing to upload. In the presigned URL flow, the client uploads the file directly to storage *before* calling `POST /v1/events`. But the event might still be valid to create as a draft without a flier yet — the organiser may upload the flier later. Making `flierUrl` optional gives this flexibility without any special handling.

### What Happens to the Error `"Event flier (image) is required"`

That error was thrown in the service when `!flierFile`. Once the file parameter is removed from the service signature, the error disappears because there is no longer a concept of "file not attached." The URL either comes from the DTO or it's `null`. If you want to enforce a flier for published events (not drafts), that validation belongs in the publish flow, not the creation flow.

### The 3-Step Flow for the Frontend

```javascript
// Step 1: Get a presigned URL
const { uploadUrl, fileUrl } = await api.post('/v1/storage/presigned-url', {
  filename: file.name,
  contentType: file.type,
  folder: 'events',
});

// Step 2: Upload directly to storage (NestJS is not involved)
await axios.put(uploadUrl, file, {
  headers: { 'Content-Type': file.type },
  onUploadProgress: (e) => setProgress(Math.round(e.loaded * 100 / e.total)),
});

// Step 3: Create the event with the storage URL as a plain string
await api.post('/v1/events', {
  name: 'Tech Summit 2026',
  flierUrl: fileUrl,  // the public URL, not the binary
  // ...other fields
});
```

The `uploadUrl` is a signed, short-lived URL only MinIO/S3 will accept. The `fileUrl` is the permanent public URL of the stored file — this is what goes into your database.

---

## Part 33 — Robust Process Error Handling

### Why the Basic Pattern Is Insufficient

The basic pattern most tutorials show:

```javascript
process
  .on('uncaughtException', (err) => console.error(err))
  .on('unhandledRejection', (err) => console.error(err))
```

has two critical problems:
1. It logs the error but **doesn't exit**. The process continues running in an undefined state after an uncaught exception. The Node.js documentation explicitly says the process should be considered unsafe after `uncaughtException` — memory may be corrupted, async state may be inconsistent.
2. It handles only two events. There are several others that matter in production.

### The Full Set of Process Events That Matter

| Signal / Event | Who sends it | What to do |
|---|---|---|
| `uncaughtException` | Node.js runtime | Log, exit 1 |
| `unhandledRejection` | Node.js runtime | Log, exit 1 |
| `SIGTERM` | Docker, Kubernetes, `kill <pid>` | Graceful shutdown, exit 0 |
| `SIGINT` | Ctrl+C in terminal | Graceful shutdown, exit 0 |
| `SIGHUP` | Terminal closed (Unix) | Graceful shutdown, exit 0 |
| `SIGUSR2` | nodemon (restart) | Cleanup, re-raise signal |
| `warning` | Node.js runtime | Log only, do not exit |

### The Force-Exit Timeout — The Part Everyone Misses

When you call `server.close()` or `app.close()`, you stop accepting **new** connections. But existing connections are allowed to finish. If a long-running request never finishes (e.g., a client that opened a connection and went silent), the server close never completes — the process hangs.

In Docker/Kubernetes, this means the container stays alive until Kubernetes gives up and sends SIGKILL (the nuclear option with no cleanup at all). You want to control this yourself:

```javascript
const timer = setTimeout(() => {
  console.error('Graceful shutdown timed out — forcing exit');
  process.exit(1);
}, 10_000);  // 10 seconds

timer.unref();  // ← this is critical
```

**Why `.unref()`?** A timer with a reference keeps the Node.js event loop alive. If everything else (server, connections) has closed, you want the process to exit naturally — not stay alive waiting for a timeout that should only fire if something went wrong. `.unref()` tells the event loop "don't count this timer as a reason to stay alive." The timer still fires if the process hasn't exited, but it doesn't prevent natural exit.

### SIGUSR2 and nodemon

`nodemon` sends `SIGUSR2` to restart your process during development. If you don't handle it, nodemon still works — but you miss the opportunity to cleanly close DB connections and release resources before the restart. The correct pattern is to clean up and then **re-raise** the signal so nodemon knows the process acknowledged it:

```javascript
process.once('SIGUSR2', async () => {
  await app.close();  // or server.close()
  process.kill(process.pid, 'SIGUSR2');  // re-raise, nodemon proceeds
});
```

Note `process.once` — not `process.on`. nodemon only sends this once. Using `once` avoids accumulating handlers across multiple restarts.

### Plain Node.js Implementation

```javascript
// error-handler.js
function registerProcessErrorHandlers(server) {
  function shutdown(signal, code = 0) {
    console.log(`[${signal}] Shutting down gracefully...`);

    const timer = setTimeout(() => {
      console.error('[shutdown] Timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    server.close((err) => {
      if (err) {
        console.error('[shutdown] Error closing server:', err);
        process.exit(1);
      }
      process.exit(code);
    });
  }

  process.on('uncaughtException', (err) => {
    console.error(`[uncaughtException] ${err.message}\n${err.stack}`);
    process.exit(1);  // always exit — process state is undefined after this
  });

  process.on('unhandledRejection', (reason) => {
    const msg = reason instanceof Error ? reason.stack : String(reason);
    console.error(`[unhandledRejection] ${msg}`);
    process.exit(1);
  });

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));
  process.on('SIGHUP',  () => shutdown('SIGHUP'));

  process.once('SIGUSR2', () => {
    console.log('[SIGUSR2] nodemon restart — closing server');
    server.close(() => process.kill(process.pid, 'SIGUSR2'));
  });

  process.on('warning', (w) => {
    console.warn(`[warning:${w.name}] ${w.message}`);
  });
}

const server = app.listen(3000);
registerProcessErrorHandlers(server);
```

### Express.js — Adding the 4-Argument Error Handler

Express has its own error-handling middleware convention on top of process-level handlers. The key rule: **error middleware must have exactly four parameters**. Express detects error handlers by parameter count — if your function only has 3 parameters, Express treats it as regular middleware.

```javascript
// Must come AFTER all routes and regular middleware
function globalErrorHandler(err, req, res, next) {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  console.error(`[error] ${req.method} ${req.url} — ${status}: ${message}`);

  res.status(status).json({
    success: false,
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message,
      // only expose stack trace in development
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
    },
  });
}

// 404 handler — for routes that don't match anything
function notFoundHandler(req, res) {
  res.status(404).json({
    success: false,
    error: { code: 'NOT_FOUND', message: `Cannot ${req.method} ${req.path}` },
  });
}

app.use(yourRoutes);
app.use(notFoundHandler);    // after routes, before error handler
app.use(globalErrorHandler); // last middleware registered
```

Triggering the error handler from a route:

```javascript
// Express 4 — pass errors to next()
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await db.findUser(req.params.id);
    if (!user) {
      const err = new Error('User not found');
      err.status = 404;
      return next(err);
    }
    res.json(user);
  } catch (err) {
    next(err);
  }
});

// Express 5 / with express-async-errors patch — throw directly
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  if (!user) throw Object.assign(new Error('User not found'), { status: 404 });
  res.json(user);
});
```

### NestJS Implementation

```typescript
// src/common/process-error-handler.ts
import { INestApplication, Logger } from '@nestjs/common';

const logger = new Logger('Process');

export function registerProcessErrorHandlers(app: INestApplication) {
  async function shutdown(signal: string, code = 0) {
    logger.log(`${signal} received — closing application`);

    const timer = setTimeout(() => {
      logger.error('Graceful shutdown timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    await app.close(); // triggers OnApplicationShutdown hooks on all providers
    process.exit(code);
  }

  process.on('uncaughtException', (err: Error) => {
    logger.error(`Uncaught Exception: ${err.message}`, err.stack);
    process.exit(1);
  });

  process.on('unhandledRejection', (reason: unknown) => {
    const message = reason instanceof Error ? reason.stack : String(reason);
    logger.error(`Unhandled Rejection: ${message}`);
    process.exit(1);
  });

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));
  process.on('SIGHUP',  () => shutdown('SIGHUP'));

  process.once('SIGUSR2', async () => {
    logger.log('SIGUSR2 received (nodemon restart)');
    await app.close();
    process.kill(process.pid, 'SIGUSR2');
  });

  process.on('warning', (warning: Error) => {
    logger.warn(`[${warning.name}] ${warning.message}`);
  });
}
```

**Why `app.close()` matters in NestJS:** It calls `OnApplicationShutdown` lifecycle hooks on every provider. This is how you cleanly close database connections, flush message queues, and drain in-flight requests. Without it, those connections leak — Postgres connection pools don't get released, Redis clients stay open, and your next deploy may hit connection limits.

### The Five Rules to Remember

1. **Always exit after `uncaughtException`** — Node.js documentation says the process is in an undefined state. Trying to serve more requests after this is gambling.
2. **Always exit after `unhandledRejection`** — future Node.js versions exit automatically; handle it yourself now.
3. **Always set a force-exit timeout on shutdown signals** — `server.close()` waits for connections to drain; if one hangs, so does your process.
4. **Always call `.unref()` on that timeout** — without it, the timer itself keeps the event loop alive even after everything has closed.
5. **Re-raise `SIGUSR2` after cleanup** — don't exit on it; nodemon needs the re-raised signal to know it can restart.

---

## Part 34 — MinIO Configuration: Two URLs, Two Different Jobs

### The Core Confusion

MinIO storage involves two URLs that serve completely different purposes, and mixing them up is one of the most common bugs when deploying:

| Variable | What it is | Who uses it |
|---|---|---|
| `MINIO_ENDPOINT` | The address NestJS uses to talk to MinIO | Your NestJS server (server-to-server) |
| `CDN_BASE_URL` / `MINIO_EXTERNAL_URL` | The address clients use to access stored files | Browsers, mobile apps |

These two can be — and often *are* — different addresses for the same MinIO instance.

### Why They Can Differ

Imagine MinIO running inside a Docker network. Other containers can reach it at `minio:9000` (the internal Docker DNS name). But browsers outside the network need to use `https://files.yourdomain.com`. So:

- `MINIO_ENDPOINT=minio:9000` — NestJS connects here (internal)
- `CDN_BASE_URL=https://files.yourdomain.com/nextvibe` — clients use this (external)

In this codebase, MinIO runs on Railway at `minio-production-5cff.up.railway.app`. NestJS connects to it there, and clients also access files from the same domain. So both values should point to the same Railway domain. The bug was that `CDN_BASE_URL` was left as `http://localhost:9000/nextvibe` — the local dev value — even after MinIO moved to Railway.

### How the Code Resolves the Public Base URL

```typescript
this.publicBaseUrl =
  this.configService.get('MINIO_EXTERNAL_URL') ??   // explicit override wins
  this.configService.get('CDN_BASE_URL') ??          // fallback
  `${protocol}://${host}:${port}/${bucket}`;         // auto-constructed from MINIO_ENDPOINT
```

Priority: `MINIO_EXTERNAL_URL` → `CDN_BASE_URL` → constructed from `MINIO_ENDPOINT`. If you set `CDN_BASE_URL` wrong, you'll get wrong public URLs in every API response. If you set neither, it auto-constructs from `MINIO_ENDPOINT` — which works if your MinIO endpoint is already public-facing.

### The Classic Bug This Produces

```
// .env (production — wrong)
MINIO_ENDPOINT=minio-production-5cff.up.railway.app   ✅ correct
CDN_BASE_URL=http://localhost:9000/nextvibe            ❌ dev leftover

// Result:
uploadUrl = https://minio-production-5cff.up.railway.app/nextvibe/events/file.jpg?X-Amz-...  ✅
fileUrl   = http://localhost:9000/nextvibe/events/file.jpg                                     ❌

// uploadUrl works (browser can upload there)
// fileUrl goes into the database
// Every image/video reference in every API response points to localhost:9000
// No images or videos load in production
```

The `uploadUrl` is generated by the MinIO client (which uses `MINIO_ENDPOINT` — correct). The `fileUrl` is built using `publicBaseUrl` (which uses `CDN_BASE_URL` — wrong). That's why the upload worked but the stored URLs were broken.

### Fix

```
CDN_BASE_URL=https://minio-production-5cff.up.railway.app/nextvibe
```

### Also: MinIO Needs to Know Its Own External URL

MinIO itself has a configuration variable called `MINIO_SERVER_URL`. This tells MinIO what its own public address is — it affects things like presigned URL generation when MinIO is behind a reverse proxy. If MinIO generates presigned URLs using its internal address, and a browser tries to use those URLs, it won't be able to reach MinIO.

On Railway, MinIO's `MINIO_SERVER_URL` should be set to `https://minio-production-5cff.up.railway.app`. This is separate from anything in your NestJS `.env` — it's a MinIO server environment variable.

---

## Part 35 — Presigned URLs: How the Signature Actually Works

### What a Presigned URL Is

A presigned URL is a regular HTTPS URL with an authentication signature embedded in its query parameters. It allows someone (like a browser) to perform a specific S3/MinIO operation *without* having the MinIO credentials. The credentials stay on your server; only the signature goes to the client.

An example presigned PUT URL:

```
https://minio-production-5cff.up.railway.app/nextvibe/events/file.jpg
  ?X-Amz-Algorithm=AWS4-HMAC-SHA256
  &X-Amz-Credential=minioadmin%2F20260522%2Fus-east-1%2Fs3%2Faws4_request
  &X-Amz-Date=20260522T102959Z
  &X-Amz-Expires=900
  &X-Amz-SignedHeaders=host
  &X-Amz-Signature=7270ad47...
```

Breaking this down:
- `X-Amz-Algorithm` — signing algorithm used (HMAC-SHA256)
- `X-Amz-Credential` — who signed it + date + region + service
- `X-Amz-Date` — when the signature was created (ISO 8601)
- `X-Amz-Expires` — how long the URL is valid in seconds (900 = 15 minutes)
- `X-Amz-SignedHeaders` — which request headers are covered by the signature
- `X-Amz-Signature` — the actual cryptographic signature

### What the Signature Covers

The signature is an HMAC-SHA256 hash over:
- The HTTP method (`PUT`)
- The bucket and object key (`/nextvibe/events/file.jpg`)
- The expiry time
- The credentials used

This means:
- You **cannot** change the file path — the signature will be invalid
- You **cannot** use the URL after it expires — MinIO checks the date + expiry
- You **cannot** use it for a different HTTP method (a PUT URL won't work for GET)
- You **can** use it from any IP address — there is no IP binding by default

### The Expiry Window

In this codebase, URLs expire in 15 minutes (`15 * 60 = 900` seconds). This means the frontend must start the upload within 15 minutes of requesting the presigned URL. For large files with slow connections, you may need to increase this. For very sensitive data, keep it short.

### Content-Type Constraint

When generating a presigned URL, you can optionally lock it to a specific Content-Type. If you do, MinIO will reject any PUT that doesn't send exactly that Content-Type header.

In this codebase, `presignedPutObject` is called without a Content-Type — so MinIO accepts any file type. This is flexible but means you can't enforce "only images" at the storage layer. If you want that, you'd need to pass the Content-Type when generating:

```typescript
// Locked to a specific content type (more secure)
const uploadUrl = await this.minioClient.presignedPutObject(
  this.bucketName,
  storageKey,
  expiresSeconds,
  { 'Content-Type': contentType },  // MinIO enforces this
);
```

### Browser CORS: The Hidden Requirement

When a browser sends a `PUT` request to a different domain (like uploading to MinIO from your app at `app.mynextvibe.com`), the browser first sends a **preflight `OPTIONS` request** to check if MinIO allows cross-origin uploads.

MinIO must respond to that `OPTIONS` with the right CORS headers:

```
Access-Control-Allow-Origin: https://app.mynextvibe.com
Access-Control-Allow-Methods: PUT
Access-Control-Allow-Headers: Content-Type
```

If MinIO doesn't have CORS configured, the preflight fails, and the actual `PUT` never happens. The browser shows a CORS error. **This is the most common reason presigned URL uploads work in testing (Postman, curl) but fail in the browser** — because Postman doesn't do CORS preflight.

### Configuring CORS on MinIO

In MinIO, CORS is configured via the MinIO admin console or the `mc` CLI:

```bash
# Using MinIO client (mc)
mc alias set myminio https://minio-production-5cff.up.railway.app minioadmin minioadmin
mc admin config set myminio/ api cors_allow_origin="https://app.mynextvibe.com"
```

Or via MinIO's web console (browser UI at your MinIO domain) → Administrator → Configuration → API → CORS.

For development, you can allow all origins (`*`), but in production, restrict to your actual frontend domain.

---

## Part 36 — Prisma's `undefined` vs `null`: The Silent Security Bug

### The Difference

In Prisma queries, `undefined` and `null` are **not the same thing** and their difference has security implications:

```typescript
// undefined — Prisma IGNORES this field entirely (no filter applied)
await prisma.follow.findMany({
  where: { followerId: undefined }
});
// ↑ This is equivalent to: findMany({ where: {} })
// Returns ALL follow records in the database

// null — Prisma filters for records where followerId IS NULL
await prisma.follow.findMany({
  where: { followerId: null }
});
// ↑ This filters for records where the column is actually null
```

### Why This Is a Security Bug

If your `userId` comes from a JWT and the JWT decoding fails or returns `undefined`, and you pass that directly to Prisma:

```typescript
async getFollowers(userId: string) {
  return prisma.follow.findMany({
    where: { followingId: userId },  // if userId is undefined...
  });
}
```

Prisma ignores the `where` clause entirely and returns **every follow record in the database**. A brand new user with no followers suddenly appears to be followed by the entire platform.

This was an actual bug described in the codebase documentation — new users appeared to have thousands of followers because the JWT payload wasn't parsed correctly at the social controller layer.

### The Fix Pattern

Always validate that your identifier is actually a string before passing it to Prisma:

```typescript
async getFollowers(userId: string) {
  if (!userId) throw new BadRequestException('User ID is required');

  return prisma.follow.findMany({
    where: { followingId: userId },
  });
}
```

Or at the guard level — if `@CurrentUser()` ever returns `undefined`, the JWT guard should have rejected the request before it reached the service. The root cause is usually a guard that isn't properly applied, or a JWT payload shape that doesn't match what the decorator extracts.

### The General Rule

Any time you have a `where` clause that's built from user-supplied or runtime-derived values, validate them explicitly before the query:

```typescript
// Dangerous — if organizerId is undefined, returns all events
const events = await prisma.event.findMany({
  where: { organizerId }
});

// Safe
if (!organizerId) throw new ForbiddenException();
const events = await prisma.event.findMany({
  where: { organizerId }
});
```

This is especially important for multi-tenant data — you never want to accidentally return another user's data because a filter was silently dropped.

---

## Part 37 — How `class-validator` Actually Works in NestJS

### What `ValidationPipe` Does

In `main.ts`, this is registered globally:

```typescript
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,     // strips properties not in the DTO
  transform: true,     // converts types (e.g. "123" → 123 for @IsNumber())
  forbidNonWhitelisted: false,
}));
```

When a request comes in, NestJS:
1. Takes the raw JSON body
2. Instantiates the DTO class
3. Runs all `class-validator` decorators
4. If `whitelist: true`, strips any properties not decorated in the DTO
5. If validation fails, returns a 400 with all failing constraints listed

### What `@IsOptional()` Actually Does

`@IsOptional()` does not mean "this field is optional in the API." It means: **if this field is `undefined` or `null`, skip all other validation on it.**

```typescript
@IsString()
@IsOptional()
bio?: string;
```

Without `@IsOptional()`: if `bio` is missing from the request body, `@IsString()` runs and fails because `undefined` is not a string — you'd get a 400 even when the field isn't sent.

With `@IsOptional()`: if `bio` is missing, all validation on `bio` is skipped entirely — no error.

You still need `@IsString()` alongside it because if `bio` IS provided, you still want to ensure it's a string and not, say, a number.

### The `whitelist: true` Security Feature

`whitelist: true` is a security measure. Without it, a client can send:

```json
{
  "username": "alice",
  "isAdmin": true,    ← not in DTO, but would pass through to the service
  "role": "ADMIN"
}
```

With `whitelist: true`, any property not decorated in the DTO is silently stripped before the controller handler runs. `isAdmin` and `role` never reach your service.

`forbidNonWhitelisted: true` goes further — instead of silently stripping unknown properties, it returns a 400 error if any unknown property is present. This is stricter and useful for catching client bugs early.

### `@Transform()` and Type Coercion

NestJS receives all incoming data as strings (from query params) or JSON primitives (from body). `@Transform()` lets you convert them:

```typescript
@IsNumber()
@IsOptional()
@Transform(({ value }) => (value ? Number(value) : value))
capacity?: number;
```

Without `@Transform()`, a query param `?capacity=100` would be the string `"100"`. `@IsNumber()` would fail because `"100"` is not a number. With `@Transform()`, it's converted to `100` first, then validated.

The `transform: true` option on `ValidationPipe` does automatic coercion for some types, but explicit `@Transform()` decorators give you full control over the conversion logic.

### `@Type()` for Nested Objects

When a DTO has nested objects, `class-transformer` needs a hint about which class to instantiate:

```typescript
@IsArray()
@ValidateNested({ each: true })
@Type(() => CreateTicketTierDto)
ticketTiers?: CreateTicketTierDto[];
```

Without `@Type(() => CreateTicketTierDto)`, the nested objects stay as plain JavaScript objects and `@ValidateNested()` has nothing to run — the nested validators never fire. `@Type()` tells `class-transformer` to instantiate the right class, which then has its own decorators that `class-validator` can execute.

---

## Part 38 — Environment Variables: The Dev/Prod Split That Always Catches You

### The Pattern of the Bug

The most common production bug isn't a code bug — it's an env var that was set up for local development and never updated for production. The pattern:

1. During development, you run MinIO locally at `localhost:9000`
2. You set `CDN_BASE_URL=http://localhost:9000/nextvibe` in your `.env`
3. You deploy — MinIO moves to Railway, NestJS moves to Railway
4. You update `MINIO_ENDPOINT=minio-production-5cff.up.railway.app`
5. You forget to update `CDN_BASE_URL`
6. NestJS connects to MinIO correctly (MINIO_ENDPOINT is right)
7. Every file URL stored in the database is `http://localhost:9000/...`
8. No images load in production

The fix is one line. The debugging takes an hour because the upload *succeeds* — the data just isn't right.

### The Rule: Separate Concerns in Your `.env`

Every URL in your `.env` that a **browser or mobile app** will use must point to a public address. Every URL that only your **server** uses can be an internal address. When you deploy, go through every variable and ask: "who uses this URL?"

| Variable | User | Must be public? |
|---|---|---|
| `MINIO_ENDPOINT` | NestJS server | No — can be internal |
| `CDN_BASE_URL` | Browser (image URLs) | **Yes** |
| `DATABASE_URL` | NestJS server | No |
| `WEB_APP_URL` | Used in emails/QR codes sent to users | **Yes** |
| `REDIS_HOST` | NestJS server | No |

### The `.env.example` Contract

`.env.example` is a contract for anyone setting up the project. Every value in it should be a safe placeholder that makes it obvious what the format should be — not a working local value that someone might use as-is in production.

```bash
# Bad — someone copies this to .env, deploys, and it silently uses localhost
CDN_BASE_URL=http://localhost:9000/nextvibe

# Good — obviously a placeholder, no one will use it as-is
CDN_BASE_URL=https://your-minio-host/nextvibe
```

This is why the `.env.example` in this codebase was updated to the generic placeholder form, not the Railway-specific URL — `.env.example` should work for *any* deployment, not be tied to one specific infrastructure.

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

If User B never emits `join:dm`, they are connected but not in any room. Step 6 never reaches them. They'd have to poll the REST API to see new messages. **This is exactly why messages weren't real-time** — the frontend was connecting but not emitting `join:dm`.

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

## Part 40 — Debugging a 401 on Login

### The Login Endpoint Architecture

The login route is decorated with `@Public()`:

```typescript
@Public()
@Post('login')
login(@Body() dto: LoginDto) {
  return this.authService.login(dto);
}
```

And the JWT guard handles `@Public()` like this:

```typescript
async canActivate(context: ExecutionContext): Promise<boolean> {
  const isPublic = this.reflector.getAllAndOverride(IS_PUBLIC_KEY, [...]);
  if (isPublic) {
    try {
      await super.canActivate(context);  // attempt auth if token present
    } catch (_) {}                        // swallow the error
    return true;                          // always let through
  }
  return super.canActivate(context);
}
```

On `@Public()` routes the guard **always returns `true`** regardless of whether a token is present or valid. So a 401 on `POST /auth/login` is **never coming from the guard** — it's always coming from the service throwing `UnauthorizedException`.

### The Three Causes of a 401 on Login

**1. Email not found**
```typescript
const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
if (!user || !user.passwordHash) {
  throw new UnauthorizedException('Invalid credentials');
}
```
The user doesn't exist in the database. Check: wrong email, different environment (dev DB vs prod DB), or they never registered.

**2. OAuth user trying email/password login**
Same code block — `!user.passwordHash`. A user who signed up with Google OAuth has no password hash. If they try to log in with email + password, they hit this check. The error message deliberately says "Invalid credentials" (not "use Google OAuth") so you don't leak that the account exists.

**3. Wrong password**
```typescript
const passwordValid = await argon2.verify(user.passwordHash, dto.password);
if (!passwordValid) {
  throw new UnauthorizedException('Invalid credentials');
}
```
The user exists and has a password, but the password is wrong.

### How to Distinguish Them from Logs

The response time tells you which branch was hit:
- **Fast 401 (~5ms)** — user not found or no passwordHash. Prisma query returned immediately, no argon2 run.
- **Slow 401 (~100–200ms)** — wrong password. Argon2 verification ran (intentionally slow to resist brute force), found mismatch.

Looking at the actual logs:
```
POST /v1/auth/login  401  161ms   ← argon2 ran → user found, wrong password
POST /v1/auth/login  401   68ms   ← argon2 didn't run → user not found or no passwordHash
```

### Case Sensitivity

Postgres string comparisons are case-sensitive by default. If a user registered as `John@Gmail.com` and logs in as `john@gmail.com`, `findUnique({ where: { email: 'john@gmail.com' } })` returns null — a fast 401.

Fix: normalise emails to lowercase before storing and before querying.

```typescript
// On registration:
email: dto.email.toLowerCase()

// On login:
where: { email: dto.email.toLowerCase() }
```

---

---

## Part 41 — Deriving Values Server-Side: The Tier-Capacity Pattern

### The Problem With Letting Users Set Their Own Capacity

When the events service accepted a raw `capacity` field from the DTO, an organizer could pay for the cheapest `MICRO` tier (1–50 attendees) but pass `capacity: 5000` in the request body. The pricing is based on tier, so they'd get enterprise-scale capacity at micro-scale price.

### The Fix: Remove Capacity From the Input, Derive It From Tier

The DTO now takes a `tier` field (an enum), and the service maps that to capacity server-side:

```typescript
// Outside the class — immutable lookup table
const TIER_CAPACITY_MAP: Record<string, number> = {
  MICRO: 50,
  SMALL: 200,
  MEDIUM: 500,
  LARGE: 2000,
  ENTERPRISE: 999999,
};

async create(organizerId: string, dto: CreateEventDto) {
  const calculatedCapacity = TIER_CAPACITY_MAP[dto.tier.toUpperCase()] ?? 50;
  // dto.capacity is no longer accepted — capacity is derived from tier
}
```

The client can no longer send a capacity at all. They pick a tier; the server decides what that tier means in terms of headcount.

### The General Principle: Derived Fields Belong on the Server

Anytime a value is logically determined by another input, don't accept the derived value from the client — compute it:

| Client sends | Server derives |
|---|---|
| `tier: 'LARGE'` | `capacity: 2000` |
| `isPublic: false` | `accessKey: 'VIBE-XYZ123'` |
| `eventId` | `qrCode: 'https://...'` |
| `userId` (from JWT) | never accepts it from body |

This pattern prevents clients from sending inconsistent or manipulated data. The server is always the source of truth for computed values.

### The `@Transform()` Pairing

The tier field uses:
```typescript
@IsEnum(EventTier)
@Transform(({ value }) => typeof value === 'string' ? value.toUpperCase() : value)
tier: EventTier;
```

`@Transform()` runs before `@IsEnum()`. It normalises `'medium'` → `'MEDIUM'` before validation, so both `"medium"` and `"MEDIUM"` pass. Without the transform, `"medium"` would fail `@IsEnum(EventTier)` because the enum values are uppercase. This pairing is also used on the `mode` field — any field where the enum is uppercase but you want to accept any casing from the client.

---

## Part 42 — NestJS Route Ordering: The Static vs Parameterized Gotcha

### The Bug

You add this to your controller:

```typescript
@Get('me')
getMe(@CurrentUser() user: JwtPayload) {
  return this.usersService.getMe(user.sub);
}

@Get(':id')
getUser(@Param('id') id: string) {
  return this.usersService.findById(id);
}
```

You call `GET /users/me`. Instead of hitting `getMe`, it hits `getUser` with `id = "me"`. Your service does `findById("me")`, Prisma looks for a user with id `"me"`, finds nothing, throws `NotFoundException`.

### Why It Happens

NestJS registers and matches routes in the order they're declared in the class. `:id` is a wildcard — it matches *any* path segment, including the literal string `"me"`. If `getUser` is declared before `getMe`, `:id` intercepts first.

The same happens with:
- `GET /users/search` shadowed by `GET /users/:id`
- `GET /events/featured` shadowed by `GET /events/:id`
- `GET /notifications/read-all` shadowed by `GET /notifications/:id`

### The Fix: Always Declare Static Routes Before Parameterized Ones

```typescript
// Static routes first
@Get('me')
getMe() { ... }

@Get('search')
search() { ... }

@Get('featured')
getFeatured() { ... }

// Parameterized routes after
@Get(':id')
getUser(@Param('id') id: string) { ... }
```

NestJS tries routes in declaration order. Once it finds a match, it stops. Static routes like `/me` and `/search` must be registered before `:id` or they'll always be shadowed.

### The Same Problem Exists Across Controllers

If two controllers have routes that could match the same URL (e.g., `BillingController` and `OrganizerPaymentsController` both using `/organizer-payments`), the module loaded first in `AppModule.imports` wins — as covered in Part 27. The principle is the same: registration order determines which handler runs.

---

## Part 43 — Prisma Transactions: Two Patterns, Two Use Cases

### Pattern 1: Sequential Transaction (Array Form)

```typescript
const [result1, result2] = await this.prisma.$transaction([
  this.prisma.user.update({ where: { id }, data: { balance: { decrement: amount } } }),
  this.prisma.ledger.create({ data: { userId: id, amount, type: 'DEBIT' } }),
]);
```

Prisma sends all operations to PostgreSQL in a single transaction. They succeed or fail together. The return value is an array with each operation's result.

**Limitation:** You cannot use the result of one operation as input to the next. All queries are defined upfront before any of them run.

### Pattern 2: Interactive Transaction (Callback Form)

```typescript
const event = await this.prisma.$transaction(async (tx) => {
  const newEvent = await tx.event.create({ data: { ... } });

  // use newEvent.id for the next operations
  await tx.eventChat.createMany({
    data: [
      { eventId: newEvent.id, section: 'PRE_EVENT' },
      { eventId: newEvent.id, section: 'DURING_EVENT' },
    ],
  });

  await tx.event.update({
    where: { id: newEvent.id },
    data: { qrCode: `${webAppUrl}/events/${newEvent.id}` },
  });

  return newEvent;
});
```

`tx` is a Prisma transaction client — it has all the same methods as `this.prisma` but every operation goes through the same transaction. The callback runs inside the transaction. If you `throw` inside the callback, the entire transaction rolls back automatically.

**Use this when:** Later operations depend on the results of earlier ones (like using the new event's `id`).

### The `tx` Proxy: Why Not Just Use `this.prisma`?

Inside the callback, you MUST use `tx`, not `this.prisma`. `this.prisma` opens a separate connection — any `this.prisma.xxx` call inside the transaction callback runs outside the transaction. It won't roll back with the others if something fails.

```typescript
await this.prisma.$transaction(async (tx) => {
  await tx.event.create({ ... });          // ✅ inside transaction
  await this.prisma.event.create({ ... }); // ❌ outside transaction — won't roll back
});
```

### When to Use Transactions

Use a transaction anytime **two or more writes must succeed or fail together**:
- Creating an event + creating its chat rooms + creating its QR code
- Activating a payment + updating the event plan + publishing the event
- Creating a ticket + decrementing the tier's available quantity

If only one write fails, the others roll back automatically — no partial state, no orphaned records.

### The Timeout Default

Prisma interactive transactions have a default timeout of **5 seconds**. If the callback takes longer, Prisma rolls back and throws `TransactionExpiredError`. For operations involving external API calls (e.g., calling Juicyway inside a transaction), keep the external call outside the transaction and only put the database writes inside:

```typescript
// ❌ Don't put external calls inside a transaction
await this.prisma.$transaction(async (tx) => {
  const payment = await juicywayService.initiate(amount);  // could take 3+ seconds
  await tx.payment.create({ data: { reference: payment.ref } });
});

// ✅ External call outside, DB writes inside
const payment = await juicywayService.initiate(amount);  // outside
await this.prisma.$transaction(async (tx) => {           // fast DB writes only
  await tx.payment.create({ data: { reference: payment.ref } });
  await tx.event.update({ data: { status: 'PENDING_PAYMENT' } });
});
```

---

## Part 44 — NestJS Lifecycle Hooks

NestJS providers can hook into the application lifecycle by implementing specific interfaces. These run at predictable moments during startup and shutdown.

### The Four Lifecycle Moments

```
bootstrap() called
    │
    ▼
[Module initialization — constructors run, DI wired]
    │
    ▼
OnModuleInit.onModuleInit()     ← provider is ready, safe to use injected services
    │
    ▼
OnApplicationBootstrap.onApplicationBootstrap()  ← all modules initialized
    │
    ▼
[Server starts listening on port]
    │
    ▼
[Application running...]
    │
    ▼
app.close() called (SIGTERM, SIGINT, etc.)
    │
    ▼
OnApplicationShutdown.onApplicationShutdown(signal)  ← clean up resources
    │
    ▼
[Process exits]
```

### Real Example: PrismaService Uses `OnModuleInit`

```typescript
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit() {
    await this.$connect();  // establish DB connection when module is ready
  }

  async onModuleDestroy() {
    await this.$disconnect();  // release connection on shutdown
  }
}
```

`onModuleInit` fires after NestJS finishes dependency injection for that module. It's safe to call `this.$connect()` here because `PrismaService` is fully constructed. Putting the connect call in the constructor would run before DI is complete — fine for Prisma specifically, but risky for services that depend on injected config.

### `OnApplicationShutdown` — Why `app.close()` Matters

`app.close()` triggers `onApplicationShutdown()` on every provider that implements it. This is the mechanism behind "graceful shutdown" — it gives every service the chance to clean up:

```typescript
@Injectable()
export class RedisService implements OnApplicationShutdown {
  async onApplicationShutdown() {
    await this.client.quit();  // release Redis connections
  }
}
```

Without this, the process exits with open database connections, unflushed buffers, and mid-flight messages. The next deploy may see connection limit errors because the old connections were never released.

### The `enableShutdownHooks()` Requirement

For `OnApplicationShutdown` to fire on OS signals (SIGTERM, SIGINT), you must call this in `main.ts`:

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableShutdownHooks();  // ← required for SIGTERM/SIGINT to trigger onApplicationShutdown
  await app.listen(3000);
}
```

Without it, `app.close()` you call manually will still trigger the hooks, but OS signals won't. This is a common gotcha in production — the app shuts down without running cleanup because `enableShutdownHooks()` was never called.

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

---

## Part 46 — The `@Public()` Guard Pattern: How Opt-Out Auth Works

### Secure by Default

The `JwtGuard` is applied globally in `AppModule`:

```typescript
app.useGlobalGuards(new JwtGuard(reflector));
// or in AppModule providers:
{ provide: APP_GUARD, useClass: JwtGuard }
```

This means **every single route** is protected by default. You never forget to add auth to a sensitive endpoint because auth is automatic. You only opt out explicitly with `@Public()`.

The alternative (opt-in auth with `@UseGuards()` on each route) means forgetting to add the guard on a sensitive endpoint exposes it publicly. Secure by default avoids this class of mistake entirely.

### How `@Public()` Works Technically

`@Public()` is a custom decorator that sets metadata on the route handler:

```typescript
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

`SetMetadata` stores a key-value pair on the route handler's metadata. The guard reads it:

```typescript
const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
  context.getHandler(),  // check method-level metadata first
  context.getClass(),    // fall back to class-level metadata
]);
if (isPublic) return true;
```

`getAllAndOverride` means: check the handler first (method decorator), then the class (controller decorator). If either has `isPublic: true`, the route is public.

### The Try/Catch on Public Routes

```typescript
if (isPublic) {
  try {
    await super.canActivate(context);  // attempt to validate JWT if present
  } catch (_) {}                        // ignore if no token or invalid token
  return true;                          // always allow through
}
```

This is subtle: even on `@Public()` routes, the guard *tries* to validate the JWT. Why? Because some public routes benefit from knowing who's calling — even if authentication isn't required.

For example, `GET /events/:id` is public (anyone can view an event) but if the user IS logged in, the response includes `isRsvped: true` and `isCheckedIn: true`. The guard tries to parse the JWT; if it succeeds, `req.user` is populated and the controller can read it with `@CurrentUser()`. If there's no token or it's invalid, the try/catch swallows the error, `req.user` is undefined, and the public response is returned without the user-specific fields.

This is why `@CurrentUser()` on a `@Public()` route returns `undefined` when not authenticated — and you see patterns like `@CurrentUser() user?: JwtPayload` (note the `?`) on those handlers.

---

## Part 47 — The Prisma Schema-Code Sync Error

### The Error

```
error TS2353: Object literal may only specify known properties,
and 'tier' does not exist in type '... EventUncheckedCreateInput ...'
```

You wrote `tier: dto.tier` in the service. TypeScript knows the Prisma-generated types. The generated types say `tier` doesn't exist on the `Event` model. You get a compile error.

### The Cause

You added a field to the service and DTO but never added it to the Prisma schema file (`events.prisma`). The generated client (`src/generated/prisma/`) is built from the schema — if the schema doesn't have the field, the generated types don't have it either, and TypeScript refuses to compile.

The same error appeared for `vibetagsEnabled` on `GameSession` — used in `organizer-payments.service.ts` but missing from `games.prisma`.

### The Fix: Schema First, Always

The correct order when adding a new field:

```
1. Add the field to the .prisma schema file
   tier  EventTier @default(MICRO)    ← events.prisma

2. Run prisma migrate dev (creates migration + regenerates client)
   pnpm prisma migrate dev --name add_tier_to_events

3. Now use the field in service/DTO code — TypeScript is happy
```

**Never go code-first with Prisma.** The schema is the single source of truth. Code that uses a field that doesn't exist in the schema compiles in your head but fails the TypeScript compiler, because the compiler reads from the generated types, which come from the schema.

### `prisma generate` vs `prisma migrate dev`

| Command | What it does | When to run |
|---|---|---|
| `prisma generate` | Regenerates the client from the current schema. No database changes. | When you pull schema changes from git but the DB is already migrated |
| `prisma migrate dev` | Creates a new migration SQL file AND runs `prisma generate`. Changes the database. | When you add/change fields in the schema and want them in the DB |
| `prisma migrate deploy` | Applies pending migrations in production. Does NOT generate. | In CI/CD build pipeline |

In local development you almost always want `prisma migrate dev` — it does everything in one step.

---

## Part 48 — OpenRouter: One API for Every AI Model

### What OpenRouter Is

OpenRouter is a routing layer that sits in front of dozens of AI model providers (OpenAI, Anthropic, Google, Mistral, Perplexity, Meta, etc.) and exposes them all through a single, unified API. Instead of managing separate API keys and SDKs for each provider, you have one key and one endpoint.

```
Your app
    │
    ▼
OpenRouter  (https://openrouter.ai/api/v1)
    │
    ├── OpenAI         (gpt-4o, o3, o1)
    ├── Anthropic      (claude-3.5-sonnet, claude-3-haiku)
    ├── Google         (gemini-2.5-flash, gemini-2.5-pro)
    ├── Perplexity     (sonar-pro, sonar-reasoning)
    ├── Meta           (llama-3.3-70b, llama-4-scout)
    ├── Mistral        (mistral-large, codestral)
    └── ...50+ more
```

### Why Use It Instead of Direct Provider APIs

- **One key to manage** — single `OPENROUTER_API_KEY`, not separate keys for OpenAI + Anthropic + Google
- **Easy model switching** — change one string (`"gpt-4o"` → `"claude-3.5-sonnet"`) to compare models or fall back if one is down
- **Fallbacks and load balancing** — OpenRouter can automatically fall back to another model if your primary is rate-limited
- **Unified billing** — one invoice, one dashboard for all usage across providers
- **Cost visibility** — see exactly what each model costs per token before you commit

### The OpenAI SDK as a Universal AI Client

OpenRouter uses the same request/response format as OpenAI's Chat Completions API. This means you can use the `openai` npm package to talk to OpenRouter — just change the `baseURL` and `apiKey`:

```typescript
import OpenAI from 'openai';

// OpenAI directly
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// OpenRouter — same SDK, different URL + key
const openRouter = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.ai/api/v1',
  defaultHeaders: {
    'HTTP-Referer': 'https://yourapp.com',   // identifies your app to OpenRouter
    'X-Title': 'Your App Name',              // shown in OpenRouter dashboard
  },
});

// Calling either one is identical
const response = await openRouter.chat.completions.create({
  model: 'anthropic/claude-3.5-sonnet',
  messages: [{ role: 'user', content: 'Hello' }],
});
```

This is the OpenAI-compatible API pattern — many providers (Mistral, Together AI, Groq, Ollama for local models) expose the same interface. One SDK, many providers.

### Web Search in AI: Online Models

Some AI models can search the web in real time before generating a response. This solves the fundamental LLM problem: training data has a cutoff date. A model trained on data from 2024 doesn't know about an event that happened last week.

For game generation, web search means:
- "Generate trivia about the FIFA 2026 World Cup" → model can search for actual recent results, correct scores, real players
- "Generate questions about [artist]'s latest album" → model searches for the actual track list instead of hallucinating
- "Create a word puzzle about Nigerian fintech news" → model pulls current companies and events, not outdated training data

**Perplexity Sonar** is the primary web-search AI provider. Their models always search the web — it's not optional. `perplexity/sonar-pro` is their most capable search-augmented model.

**The `:online` suffix** — on OpenRouter, any model can have web search added by appending `:online`:
```
google/gemini-2.5-flash          ← no web search
google/gemini-2.5-flash:online   ← web search enabled
openai/gpt-4o:online             ← GPT-4o with web search
```

OpenRouter handles the search plumbing — the model gets web results injected into its context automatically.

### Structured JSON Output on OpenRouter

Gemini enforces JSON via a `responseSchema` object in its generation config. OpenRouter uses the OpenAI standard:

```typescript
response_format: { type: 'json_object' }
```

This tells the model to always return valid JSON — no markdown fences, no explanation text, just the JSON object. Not all models honour this (especially smaller open-source ones), but all major commercial models do.

For even stricter control, OpenAI-compatible APIs also support JSON Schema via:
```typescript
response_format: {
  type: 'json_schema',
  json_schema: { name: 'game_draft', schema: yourSchemaObject }
}
```

### The Model ID Format on OpenRouter

```
{provider}/{model-name}:{variant}

anthropic/claude-3.5-sonnet
google/gemini-2.5-flash
openai/gpt-4o
perplexity/sonar-pro
meta-llama/llama-3.3-70b-instruct
openai/gpt-4o:online              ← with web search
google/gemini-2.5-flash:online    ← Gemini with web search
```

Browse available models and their costs at `openrouter.ai/models`.

### In This Codebase

`generateGameDraftViaOpenRouter()` is the new method. It uses `perplexity/sonar-pro` for web-grounded game generation. The `generateGameDraft()` method (Gemini) is kept as-is. To switch which one the games controller calls, change one method name in the game generation controller.

The `HTTP-Referer` and `X-Title` headers are required by OpenRouter — they appear in your usage dashboard and help OpenRouter attribute traffic to your app. If omitted, some models may reject the request.

---

*Document covers codebase as of May 2026. Module list: Auth, Users, Events (+ RSVP), Tickets, Payments (Juicyway + Ercaspay), Billing (Pricing, Coupons, OrganizerPayments), Games (Sessions, Rounds, Rewards, AI generation via Gemini + OpenRouter), Notifications (WebSocket + Resend), Social (Follows, Likes, Comments, Shares, Feed), Messaging (DMs + EventChat), Storage, Discovery, Admin, VibeTags, Postcards.*
