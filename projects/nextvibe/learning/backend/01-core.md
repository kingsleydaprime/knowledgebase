# NextVibe — Backend Core: NestJS, Prisma, and Cross-Cutting Patterns

Split out from the original flat `learning.md` (moved to `learning/archive/`). See also
`learning/00-sys-design.md` (architecture + database design), `learning/backend/03-modules.md` (the
domain module walkthroughs — Events, Games, Billing, Payments, Notifications, Social, Discovery,
Messaging, Storage, Admin, Pledges), `learning/backend/02-auth.md` (JWT/OAuth/guards),
`learning/backend/05-realtime.md` (WebSocket gateways and Socket.io), `learning/backend/04-games-ai.md`
(AI generation + anonymous play), and `learning/09-devops.md` (deployment/infra).

This file covers: how to read an unfamiliar codebase, what a backend API fundamentally is, why
NestJS was chosen, controllers vs services, the NestJS module/DI system, cross-cutting concerns
(rate limiting, validation, error handling, transactions), what's missing from the codebase today,
duplicate route registration bugs, the notification `targetId` convention, HTTP method mismatches,
the multipart-to-presigned-URL migration, Prisma's `undefined` vs `null` gotcha, how
`class-validator` actually works, deriving values server-side instead of trusting client input,
NestJS route ordering (static vs parameterized), the two Prisma transaction patterns, NestJS
lifecycle hooks, and the Prisma schema-code sync error.

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

(See `learning/00-sys-design.md` Part 4 for why this project is a monolith rather than microservices, and the full technology stack rationale.)

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

This happens in the global `ValidationPipe` (typically configured in `main.ts`). See Part 37 below for the full mechanics of how this works.

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

Use transactions any time two or more writes must succeed together. See Part 43 below for the two transaction patterns Prisma supports and when to use each.

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

As mentioned in `learning/backend/05-realtime.md`, running multiple API instances breaks WebSocket notifications. Add:

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

(See `learning/backend/02-auth.md` for the full JWT access/refresh token architecture this bug lives inside.)

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

The `notifications` table (which will be queried on every page load for unread count) doesn't have a composite index on `[recipientId, isRead]`. Adding this would make the unread count query significantly faster. (See `learning/00-sys-design.md` for the full indexing theory this gap relates to.)

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

When a feature "isn't working" and you can't find any error, check for duplicate route registration. It's invisible in logs and easy to miss during refactors where responsibility for a domain shifts from one module to another. (See `learning/09-devops.md` Part 31 for how to spot this from server startup logs.)

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

(See `learning/backend/03-modules.md` for the full Notifications module architecture, including the two-layer WebSocket + email delivery pattern, and Part 52 there for the notification coverage audit.)

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

(See `learning/09-devops.md` Part 35 for exactly how the presigned URL's signature works, and `learning/frontend/05-uploads-errors.md` for the full frontend implementation, including progress bars and image compression.)

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

If two controllers have routes that could match the same URL (e.g., `BillingController` and `OrganizerPaymentsController` both using `/organizer-payments`), the module loaded first in `AppModule.imports` wins — as covered in Part 27 above. The principle is the same: registration order determines which handler runs.

(See `learning/backend/03-modules.md` Part 51 for another instance of this exact rule: `GET /purchases/:id/summary` must be declared before `GET /purchases/:id` in the payments controller.)

### Live instance in this codebase: correct today, fragile by accident (audited 2026-08-12)

`src/modules/events/events.controller.ts` declares the greedy route *first*:

```
 85:  @Get(':id')                        ← greedy, declared early
...
278:  @Post('checkin')
321:  @Get('me/created')
338:  @Get('organizer/:organizerId')
355:  @Post('upload-intent')
```

By the rule above this should already be broken — and it isn't, but only by **luck of segment counts**:

- `@Get(':id')` matches exactly *one* path segment, so `/events/me/created` (two segments) slips past it.
- The `@Post` static routes are safe only because no `@Post(':id')` exists to shadow them.

**The landmine:** the moment anyone adds a single-segment GET below line 85 — `@Get('featured')`, `@Get('trending')`, `@Get('drafts')` — `:id` swallows it silently. No error, no warning, just "Event not found" on a route that reads as correctly defined. That is a genuinely nasty debugging session, because the code looks right.

Worth pre-emptively moving `@Get(':id')` and friends to the bottom of that controller. Costs nothing and removes the trap.

**The wider lesson:** "it works" and "it's correct" are different claims. Code that only works because of an incidental property (here, segment counts) is code that will break when someone makes a change that looks entirely unrelated. When you find working code that violates a rule you believe in, check *why* it works before concluding the rule is optional.

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

(See `learning/09-devops.md` Part 33 for the full process-level signal handling — `uncaughtException`, `SIGTERM`, `SIGUSR2`, and the force-exit timeout pattern — that this hook plugs into.)

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

## Counter caches: derive, never nudge (2026-08-21)

`Postcard.likeCount` is a **counter cache** — a denormalised copy of
`SELECT COUNT(*) FROM postcard_likes WHERE postcard_id = ?`, kept so the feed
doesn't run a COUNT per card. It was maintained like this:

```ts
await this.prisma.postcard.update({
  where: { id: postcardId },
  data: { likeCount: { increment: 1 } },   // or { decrement: 1 }
});
```

That's the pattern that put postcards on a like count of **-1**.

### Why ±1 always drifts eventually

A blind `increment`/`decrement` is a *relative* write: it assumes the delta it
applies exactly matches a real change in the source table. Every way that
assumption breaks is permanent, because nothing ever re-checks:

1. **Two writers, one counter.** `/v1/postcards/:id/like` wrote a `PostcardLike`
   row; `/v1/likes` wrote a `Like` row. Different tables, *same* `likeCount`.
   One endpoint's decrement could cancel a like the other never counted.
2. **Non-idempotent increment.** `LikesService.like()` did an `upsert` (correctly
   a no-op on a repeat like) and then incremented **unconditionally**. Like
   twice, unlike once → counter is +1 forever.
3. **No floor.** Nothing stopped the value going below zero.

### The fix: recompute inside the transaction

```ts
const { liked, currentLikes } = await this.prisma.$transaction(async (tx) => {
  const existing = await tx.postcardLike.findUnique({
    where: { postcardId_userId: { postcardId, userId } },
  });

  if (existing) await tx.postcardLike.delete({ where: { id: existing.id } });
  else          await tx.postcardLike.create({ data: { postcardId, userId } });

  // Absolute write, derived from the source of truth.
  const total = await tx.postcardLike.count({ where: { postcardId } });
  await tx.postcard.update({ where: { id: postcardId }, data: { likeCount: total } });

  return { liked: !existing, currentLikes: total };
});
```

Two properties worth naming, because they're what actually buy the correctness:

- **Absolute, not relative.** `data: { likeCount: total }` overwrites. A
  duplicate request writes the same number twice — harmless. Compare
  `{ increment: 1 }`, where running twice means something different from running
  once. This is the difference between an **idempotent** and a
  **non-idempotent** write, and it's why retry-safe systems prefer absolute ones.
- **Transactional.** The COUNT and the UPDATE are in one `$transaction`, so a
  concurrent like can't land between them and get overwritten by a stale total.

The cost is one extra COUNT per toggle. On an indexed `postcardId` that's
negligible, and it buys a counter that self-heals: even if a row is inserted by
a migration, a script, or a future endpoint, the next toggle corrects the cache.

**General rule:** a counter cache should be *derived* on every write. If you
find yourself writing `{ increment: 1 }`, ask what happens when that request is
duplicated, retried, or raced — and whether anything will ever notice if it is.

### The other half: repairing rows that already drifted

Changing the code stops *new* drift; it doesn't fix rows already wrong. That
needs a backfill — `prisma/repair-like-counts.ts`, built on the same dry-run
pattern as `backfill-ledger.ts`:

```bash
npx tsx prisma/repair-like-counts.ts            # print what it would change
npx tsx prisma/repair-like-counts.ts --commit   # actually write
```

It uses `groupBy` to get every true count in **one** query rather than a COUNT
per postcard — the difference between 1 query and N:

```ts
const grouped = await prisma.postcardLike.groupBy({
  by: ['postcardId'],
  _count: { _all: true },
});
```

Note the shape: `groupBy` returns rows of `{ postcardId, _count: { _all } }`,
and postcards with **zero** likes don't appear at all — hence the
`trueCounts.get(p.id) ?? 0` when reading it back. Missing-means-zero is easy to
forget and produces exactly the bug you're trying to fix.

Any one-off data script should be **idempotent and dry-run-by-default**. This
one is idempotent by construction: it sets an absolute value computed from the
source table, so a second run finds nothing to change.

### Related: the API must return the corrected value

Fixing the database isn't enough if the client never learns the true number.
`toggleLike` returned only `{ liked }`, while the frontend did:

```ts
if (result?.currentLikes !== undefined) setLikeCount(result.currentLikes);
```

`currentLikes` was always `undefined`, so that reconciliation never ran and the
optimistic guess became permanent on screen. **A mutation that changes a
displayed number should return that number.** Otherwise every client is left
guessing, and the guesses accumulate. See also
[frontend/02-state-management.md](../frontend/02-state-management.md) on
optimistic updates.
