# NextVibe — System Design & Architecture Decisions

This file is one of several domain-scoped learning files split out from the original flat
`learning.md` and `frontend-learning.md` (kept in the project root, untouched, for reference).
See also `learning/backend-core.md`, `learning/backend-modules.md`, `learning/backend-auth.md`,
`learning/backend-realtime.md`, `learning/backend-games-ai.md`, `learning/devops.md`, and the
`learning/frontend-*.md` files for the rest of the material.

This file covers: the big-picture architecture decision (monolith vs microservices), the full
technology stack rationale (why PostgreSQL / MongoDB / Redis / MySQL each would or wouldn't fit),
database design and normalisation principles, the domain-by-domain schema walkthrough, database
indexing theory, other cross-cutting design decisions worth understanding, how to think about
improving an inherited codebase, and the engineering mental model for trade-offs in general.

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

**What's missing:** The `notifications` table has no index on `[recipientId, isRead]`. The unread count query is `WHERE recipientId = ? AND isRead = false`. Without this compound index, every page load that shows a notification badge does a full scan of all notifications for that user. At 100 notifications per user and 10,000 users making simultaneous requests, this becomes a problem fast. This is noted in `learning/backend-modules.md` (Part 20 — What is Missing).

**How to know if you're missing an index in production:**

Use `EXPLAIN ANALYZE` in PostgreSQL:
```sql
EXPLAIN ANALYZE SELECT * FROM notifications WHERE recipient_id = 'uuid' AND is_read = false;
```

If you see `Seq Scan` (sequential scan) in the output, PostgreSQL is scanning every row. If you see `Index Scan`, an index is being used. Always run EXPLAIN ANALYZE on your most frequent queries to verify indexes are being used.

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
