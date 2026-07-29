# Backend Engineering — Beginner to Advanced
### Everything used in the Arete backend (NestJS 11 + Prisma + PostgreSQL + Redis + BullMQ), and why

---

## Part 1 — Absolute Beginner

### What a backend actually does

The mobile app is a face. The backend is the brain and the vault:
- **Owns the truth** (database) — the app only holds copies.
- **Enforces rules** — the app can be decompiled and faked; the server cannot. That's why Arete's "5-minute minimum before completing a quest" lives in `quests.service.ts`, not in the app.
- **Does work while nobody's watching** — cron jobs generate quests at midnight and evaluate streaks at 23:59.

### HTTP in five lines

```
GET    /quests/today          → read (no side effects, safe to repeat)
POST   /quests/optional/start → create
PATCH  /quests/:id/complete   → partial update
DELETE /users/me              → remove
Status: 200 ok · 201 created · 400 your fault · 401 not logged in · 404 missing · 500 my fault
```

Requests and responses carry JSON. The client sends `Authorization: Bearer <token>` to prove identity.

### The Arete stack at a glance

| Piece | Role |
|---|---|
| **NestJS** | HTTP framework — routing, validation, dependency injection |
| **Prisma** | ORM — typed database access + migrations |
| **PostgreSQL** | The database — the single source of truth |
| **Redis** | Fast in-memory store — caching + BullMQ's backbone |
| **BullMQ** | Job queues — cron jobs and background work |
| **bun** | JS runtime & package manager (faster npm/node) |

---

## Part 2 — NestJS: the shape of everything

NestJS organizes code into **modules**, each containing **controllers** (HTTP in/out) and **services** (business logic). Arete: `auth`, `quests`, `tasks`, `progression`, `pillars`, `messages`, `notifications`, `onboarding`, `jobs`, `redis`, `prisma`, `users`, `email`.

### Controller → Service → Database

```ts
// quests.controller.ts — thin. Parses HTTP, delegates, returns.
@Controller('quests')
@UseGuards(JwtAuthGuard)                       // every route requires a valid JWT
export class QuestsController {
  constructor(private quests: QuestsService) {} // ← dependency injection

  @Get('today')
  getToday(@Request() req: any) {
    return this.quests.getTodayQuests(req.user.id);
  }

  @Patch(':id/complete')
  complete(@Request() req: any, @Param('id') id: string) {
    return this.quests.completeQuest(req.user.id, id);
  }
}
```

```ts
// quests.service.ts — fat. All the rules live here.
@Injectable()
export class QuestsService {
  constructor(
    private prisma: PrismaService,      // injected automatically
    private xpService: XpService,
    private notifications: NotificationService,
  ) {}
  // ...
}
```

**Dependency injection (DI)** means you never write `new QuestsService(...)`. Nest builds the object graph from constructor signatures. Why care: services are swappable in tests, and wiring is declared, not hand-assembled. A service must be listed in its module's `providers`, and `exports` if other modules need it — forgetting this is the classic Nest error ("Nest can't resolve dependencies of...").

### Guards, DTOs, validation

```ts
// A guard runs before the handler. JwtAuthGuard verifies the token
// and attaches the user to the request.
@UseGuards(JwtAuthGuard)

// A DTO declares and validates input shape:
export class CompleteOnboardingDto {
  @IsString() timezone: string;
  @IsOptional() @IsString() faithBackground?: string;
  @IsOptional() @IsString() equipmentAccess?: string;
}
```

Rule: **never trust the client**. Validate at the edge (DTOs), enforce in the service.

---

## Part 3 — Prisma & Data Modeling

### The schema is the contract

```prisma
model DailyQuest {
  id        String  @id @default(uuid())
  userId    String
  taskId    String
  variantId String?

  questDate   DateTime @db.Date
  isCompleted Boolean  @default(false)
  xpEarned    Int      @default(0)

  user    User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  task    Task         @relation(fields: [taskId], references: [id])
  variant TaskVariant? @relation(fields: [variantId], references: [id])

  @@unique([userId, taskId, questDate])   // ← THE key design decision
  @@map("daily_quests")
}
```

Design decisions to study in this one model:

1. **`@@unique([userId, taskId, questDate])`** — the database itself guarantees "one quest per user per task per day". Application code *tries* to prevent duplicates; constraints *guarantee* it. This is what makes `upsert` possible.
2. **`onDelete: Cascade`** on user — delete a user, their quests vanish. But tasks have *no* cascade — you must not delete a task that history references.
3. **`@db.Date`** vs `DateTime` — quest dates are calendar days, not instants. (Gotcha: Prisma returns them as UTC midnight — compare them as dates, never as local times.)
4. **`variantId String?`** — nullable, because old rows predate the feature. New columns on live tables must be nullable or defaulted, or your migration breaks existing rows.

### Migrations — how schema changes ship

```bash
# development: edit schema.prisma, then
bunx prisma migrate dev --name add_task_variants   # generates SQL + applies + regenerates client

# production: apply already-generated migrations, never generate there
bunx prisma migrate deploy

# after any schema change:
bunx prisma generate                                # regenerate the typed client
```

Migrations are numbered SQL files in `prisma/migrations/` and are **append-only history** — never edit an applied one; write a new migration to fix a mistake. (For the variants migration we generated the SQL offline with `prisma migrate diff` — see devops notes.)

### The queries you'll use daily

```ts
// upsert = insert-or-do-nothing/update. Idempotent by construction.
await prisma.dailyQuest.upsert({
  where: { userId_taskId_questDate: { userId, taskId, questDate } }, // compound unique key
  create: { userId, taskId, pillarId, questDate, variantId },
  update: {},                                   // exists already? touch nothing
});

// include = join related rows in one query (avoids N+1):
const quests = await prisma.dailyQuest.findMany({
  where: { userId, questDate: today },
  include: { task: true, pillar: true, variant: true },
});

// aggregate without loading rows:
const stillOpen = await prisma.dailyQuest.count({
  where: { userId, questDate, isOptional: false, isCompleted: false },
});
```

**N+1 warning:** a loop that queries per item (`for (task of tasks) await prisma.taskVariant.findMany({where:{taskId: task.id}})`) fires N queries. Batch instead — one `findMany({ where: { taskId: { in: ids } } })` then group in memory (see `getVariantsByTask` in quests.service.ts).

### Transactions — all or nothing

```ts
// Array form: independent writes that must succeed together
await this.prisma.$transaction([
  prisma.dailyQuest.update({ ... }),          // mark complete
  prisma.xpTransaction.create({ ... }),       // ledger entry
  prisma.userPillar.update({ ... }),          // pillar XP
  prisma.user.update({ ... }),                // total XP + gems
]);

// Interactive form: when a later step depends on an earlier result
await this.prisma.$transaction(async (tx) => {
  const result = await tx.user.updateMany({
    where: { id: userId, gems: { gte: SHIELD_COST } },  // guard inside the txn
    data: { gems: { decrement: SHIELD_COST } },
  });
  if (result.count === 0) throw new BadRequestException('Not enough gems');
  await tx.streakEvent.create({ ... });
});
```

If completing a quest wrote XP but crashed before writing gems, the user's economy silently corrupts. Transactions make partial writes impossible.

---

## Part 4 — Patterns Worth Stealing (all live in this codebase)

### 4.1 Guarded decrement — race-condition-proof spending

**Broken version** (time-of-check-to-time-of-use bug):
```ts
const user = await prisma.user.findUnique(...);
if (user.gems >= 150) {                       // check
  await prisma.user.update({ decrement: 150 }); // act — but two parallel requests both pass the check!
}
```

**Correct version** (`streak-shield.service.ts`) — the check and the write are one atomic statement:
```ts
const result = await tx.user.updateMany({
  where: { id: userId, gems: { gte: 150 } },  // condition INSIDE the update
  data: { gems: { decrement: 150 } },
});
if (result.count === 0) throw new BadRequestException('Not enough gems');
```
Two parallel purchases: the database serializes them; the second finds `gems < 150` and matches 0 rows. This one pattern prevents every "negative balance" bug ever written.

### 4.2 Idempotency — safe to call twice

Mobile networks retry. Users double-tap. Every mutation should tolerate replays:

```ts
if (quest.startedAt) return { startedAt: quest.startedAt.toISOString() }; // startQuest: already started? return same answer
if (quest.isPaused) return { isPaused: true };                            // pauseQuest: no-op
// perfect-day bonus: awarded once per day via a natural key
const already = await prisma.xpTransaction.findFirst({
  where: { userId, reason: 'perfect_day', referenceId: '2026-07-14' },    // date = idempotency key
});
```

Three techniques: **return early with the same response**, **upsert on a unique key**, **check a ledger before awarding**.

### 4.3 The ledger pattern (event sourcing lite)

Arete never just mutates counters — it also appends events:

- `XpTransaction` rows record every XP change (`quest_complete`, `streak_penalty`, `perfect_day`) with amount + reason + reference.
- `StreakEvent` rows record `continue` / `grace` / `reset` / `shield` / `shield_used` per day.

Why this is superior to bare counters:
1. **Dedupe:** "did this day already count?" = "does a `continue` event exist for this date?" — the counter alone can't answer that.
2. **Audit:** you can explain any balance by replaying its ledger.
3. **Derived features for free:** streak shields inventory = `count('shield') - count('shield_used')`. No new column, no migration.

### 4.4 Deterministic pseudo-randomness (FNV-1a hashing)

Requirement: each user gets a *different* daily mission that *rotates* daily but *never changes on refresh*. `Math.random()` fails the last part. Hash instead:

```ts
function fnv1a(s: string): number {          // tiny, fast, good-enough spread
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);              // integer multiply without float drift
  }
  return h >>> 0;                            // force unsigned 32-bit
}

const variant = eligible[fnv1a(`${userId}:${taskId}:${dateStr}`) % eligible.length];
```

Same inputs → same output, forever. Different user or different day → different pick. Zero storage; the "assignment" is pure math. Used twice in Arete: variant selection and the 3-per-pillar daily task rotation.

### 4.5 Cache-aside with explicit invalidation (Redis)

```ts
// READ path
const cached = await this.cache.get(`progression:${userId}`);
if (cached) return cached;
const result = await expensiveQueries();
await this.cache.set(`progression:${userId}`, result, 60);   // 60s TTL
return result;

// WRITE path — any mutation that changes the answer must invalidate:
await this.cache.del(`progression:${userId}`);               // in completeQuest, purchaseShield...
```

Rules: short TTLs as a safety net even with invalidation; key names include the user id; **every** mutation path deletes the keys it stales — grep for `cache.del` when adding a mutation.

### 4.6 Background jobs with BullMQ

Cron work is registered idempotently on boot (`jobs.module.ts`):

```ts
await this.questQueue.upsertJobScheduler(
  'daily-quest-gen',
  { pattern: '0 0 * * *' },        // cron: minute hour day month weekday
  { name: 'generate', data: {} },
);
```

Arete's schedule (all UTC — Lagos is UTC+1):
```
0 0 * * *    daily-quest-generator   midnight: create everyone's quests
59 23 * * *  streak-evaluator        23:59: judge yesterday — continue/grace/shield/reset
0 6 * * *    quest-reminder          7 AM WAT: "3 quests today. Start with X"
0 21 * * *   streak-reminder         10 PM WAT: "your streak is on the line, X is waiting"
0 * * * *    xp-aggregator           hourly
0 */6 * * *  leaderboard-updater     every 6h
```

Each processor extends `WorkerHost`, wraps per-user work in try/catch so **one bad user doesn't kill the whole batch**, and logs counts:

```ts
for (const user of users) {
  try { await this.quests.generateQuestsForUser(user.id); generated++; }
  catch (err) { this.logger.error(`Failed for ${user.id}: ${err}`); }
}
```

Why a queue instead of `setInterval`: survives restarts (state in Redis), one scheduler across multiple server instances, retries and observability built in.

### 4.7 Non-fatal side effects

The streak update and Perfect Day bonus inside `completeQuest` are wrapped in their own try/catch:

```ts
try {
  // streak bookkeeping...
} catch {
  liveStreak = freshPillar!.currentStreak;   // quest completion still succeeds
}
this.notifications.sendToUser(...).catch(() => null);  // fire-and-forget
```

Taxonomy: the **core mutation** (mark complete + XP) must succeed or the request fails. **Enhancements** (streak, bonus, push) degrade gracefully. Decide the tier of every side effect explicitly.

### 4.8 Server-side display substitution

`getTodayQuests` swaps variant text into the task payload:

```ts
task: {
  name: q.variant?.name ?? q.task.name,          // specific mission, generic fallback
  description: q.variant?.description ?? q.task.description,
  ...
}
```

The app renders whatever arrives — shipping 281 new missions required no app update. **Own strings server-side whenever possible.**

### 4.9 Seeding as idempotent content deployment

`prisma/seed.ts` can run on every deploy safely because everything is an upsert keyed on a **slug** (natural key):

```ts
await prisma.taskVariant.upsert({
  where: { slug: v.slug },        // stable human-readable key, not a uuid
  update: { name: v.name, ... },  // re-running updates content in place
  create: { taskId: task.id, slug: v.slug, ... },
});
```

Content (281 task variants, 210 daily messages) lives in plain TS files (`task-variants.ts`, `daily-messages.ts`) — reviewable in diffs, no CMS needed at this stage. Messages have no natural key, so their strategy is different: wipe-and-recreate when the library grows (safe because nothing references them by id).

---

## Part 5 — Auth, Properly

### Passwords: bcrypt. Reset tokens: SHA-256. Different jobs.

```ts
// Passwords — bcrypt, deliberately SLOW (that's the security):
const hash = await bcrypt.hash(password, 10);
const ok = await bcrypt.compare(password, user.passwordHash);
```

Slow hashing means a stolen database resists brute force. But Arete uses **SHA-256** for password-reset tokens — why the "weaker" hash?

Because of the lookup problem: to find *which user* a reset token belongs to, you must search by the token's hash. bcrypt produces a different hash every time (random salt), so you can't `WHERE token_hash = ?` — you'd have to bcrypt-compare against every row. SHA-256 is deterministic → indexable lookup. And the input isn't a weak human password; it's a 256-bit random token, so slow hashing adds nothing.

**Lesson: security decisions follow from the data's properties, not from "use the strongest thing everywhere."**

### JWT: two tokens

- **Access token** (15 min): sent on every request; short life limits damage if stolen.
- **Refresh token** (30 days): only ever sent to `/auth/refresh` to mint new access tokens.

Server-side, the guard verifies the signature — no DB hit per request. That's the JWT trade: stateless speed, at the cost of not being able to revoke an access token before it expires (hence the short TTL).

---

## Part 6 — Game/Product Logic Case Studies

### Making streaks winnable (the QUESTS_PER_PILLAR fix)

Original design: every unlocked task becomes a mandatory daily quest, and a streak day requires 100% completion. At C-rank: 19 mandatory quests/day → streaks mathematically doomed → churn. Fix: cap at 3 per pillar, rotate via hash, but never serve an all-trivial day:

```ts
const ranked = [...tasks].sort((a, b) => rankOf(a) - rankOf(b)); // rankOf = fnv1a(user:pillar:date:task)
const picked = ranked.slice(0, 3);
if (!picked.some((t) => t.difficulty >= 2)) {                    // quality floor
  const substantial = ranked.find((t) => t.difficulty >= 2);
  if (substantial) picked[picked.length - 1] = substantial;
}
```

**Lesson: every "engagement" mechanic needs a difficulty-curve audit — does it stay winnable as the user progresses?**

### The streak state machine (streak-evaluator, 23:59 daily)

```
yesterday all complete?  ── yes → 'continue' event (unless live update already logged it)
        │ no
some complete?           ── yes → nothing (partial days neither extend nor break)
        │ none
free grace this month?   ── yes → 'grace' event, streak preserved
        │ no
shield in inventory?     ── yes → 'shield_used' event, streak preserved
        │ no
                          'reset' event, streak → 0, 10% XP penalty
```

Note the double-entry protection: quest completion updates streaks *live* for instant UI feedback, and the nightly evaluator is the *authoritative fallback* — both check for an existing `continue` event before writing, so they can't double-count. **When two code paths can perform the same mutation, an idempotency check is mandatory in both.**

---

## Part 7 — Advanced Habits

- **Read paths return DTO shapes, not raw rows.** `getTodayQuests` builds an explicit response object — never `return prisma.user.findUnique()` (you'll leak `passwordHash` eventually).
- **Time is UTC everywhere in storage.** Convert only at the notification/display edge. `dayjs().startOf('day')` + `@db.Date` columns; user `timezone` field exists for future per-user scheduling.
- **Indexes follow queries.** `@@index([taskId])` on variants because generation filters by task. Every frequent `WHERE` deserves an index; every unique business rule deserves a `@@unique`.
- **Config via environment.** `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET` — never in code. Different `.env` per environment; secrets rotated when leaked.
- **Errors are typed and helpful:** `NotFoundException('Quest not found')` vs `BadRequestException('Keep going. 3 minutes remaining.')` — 4xx errors are UX copy too.

## Part 8 — Case Studies: Bugs That Actually Happened (launch week)

Real bugs teach more than patterns. All four of these shipped, got caught, and got fixed in this codebase.

### 8.1 The seed race — vacuous success

**Symptom:** user completes onboarding, gets "no quests today, complete onboarding" forever.
**Cause:** the account was registered 77 seconds *before* the database seed ran. Onboarding did:

```ts
const pillars = await this.prisma.pillar.findMany({ where: { slug: { in: [...] } } });
await this.prisma.$transaction(pillars.map((p) => upsertUserPillar(p)));  // pillars = [] !
await this.prisma.user.update({ data: { onboardingComplete: true } });    // still runs!
```

`[].map()` produces an empty transaction, which **succeeds**. Nothing threw, so the code marched on and marked onboarding complete — with zero pillars attached. This is *vacuous success*: an operation that did nothing reporting that it worked.

**The three-part fix (memorize this shape):**
1. **Repair the data** — backfill the missing rows for affected users.
2. **Fail loudly at the source** — `if (pillars.length < 3) throw new BadRequestException('Server content not initialized')`. A visible error beats a silently corrupted account.
3. **Self-heal downstream** — quest generation now detects "onboarded but no pillars" and creates them. Any user already in the bad state gets fixed on their next request, no support ticket needed.

**Lesson:** whenever a loop/map drives writes, ask "what happens if the collection is empty?" If the answer is "we silently pretend success," add a guard.

### 8.2 The shared-cache leak — per-user data in a global key

**Symptom:** two users both at 0 XP; one's "YOUR POSITION #1" card appears on the *other's* screen.
**Cause:**

```ts
const cacheKey = `leaderboard:${page}:${limit}`;          // ← no user id!
const result = { ...board, userPosition: userPos };       // userPos is PERSONAL
await this.cache.set(cacheKey, result, 30);               // ...cached for everyone
```

First user in a 30-second window caches *their* position; everyone else gets served it.

**Fix:** split the cacheable from the personal. The board (same for everyone) stays under the global key; `userPosition` is computed fresh per request and merged after the cache read.

**Lesson:** before every `cache.set`, ask "is any field in this payload different per user?" If yes, either the key includes the user id or the field stays out of the cache. This bug class (cache-key scoping) also causes real-world data breaches — treat it as security, not just correctness.

### 8.3 Rankings that disagreed — two formulas for one number

**Symptom:** position card says #1, leaderboard list says #2, same user, same instant.
**Cause:** the list sorted by (overallRank, totalXp) and numbered positionally; the card computed `count(users with totalXp > mine) + 1` — a different formula that ignores overallRank and gives ties the same number. Two code paths, two answers.

**Fix:** one private `getRankedUsers()` is now the single source of truth; the list, the position card, and the worldRank cron all derive from that one ordering. Ties are broken deterministically (rank → XP → earliest `createdAt` → id) so refreshes can't shuffle order — JS `.sort()` on ties otherwise inherits arbitrary DB return order.

**Lesson:** any number shown in two places must be computed in exactly one place. And every sort that feeds a user-visible ranking needs a total order — always add a final unique tiebreaker.

### 8.4 The inert rate limiter — configured but never enforced

**Symptom (near-miss):** `ThrottlerModule.forRoot(...)` configured, `@Throttle({...})` decorators on every auth route... and none of it did anything.
**Cause:** NestJS throttling has three parts — module (config), decorators (per-route overrides), and **guard** (enforcement). Without binding the guard, the first two are decoration:

```ts
providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }],   // the missing line
```

**Verification, not vibes:** proved it works by firing 7 rapid logins — got `401 ×5`, then `429 ×2`. Security controls get *tested*, not assumed:

```bash
for i in $(seq 1 7); do
  curl -s -o /dev/null -w "attempt $i: %{http_code}\n" -X POST \
    http://localhost:3000/v1/auth/login -H "Content-Type: application/json" \
    -d '{"email":"x@x.com","password":"wrong"}'
done
```

**Lesson:** config ≠ enforcement. For any security middleware, find the line that *activates* it, then write the request that proves it fires.

### 8.5 Bonus pattern: determinism buys you time travel

Because daily quest selection is a pure hash of `(userId, date)`, a preview endpoint can compute **any future day's quests without storing anything** — `GET /quests/preview?date=2026-07-20` just runs the same selection with a future date string. Deterministic functions make features like forecasts, replays, and reproducible tests nearly free. If the selection had used `Math.random()`, this feature would have required persisting pre-generated rows for every user × day.

## Part 9 — Study Path

1. **Weeks 1–2:** HTTP + REST + JSON. Build a 3-route Express/Nest toy API. Learn status codes by breaking things.
2. **Weeks 3–4:** Prisma + Postgres. Model User/Task/DailyQuest yourself; write the migration; break a unique constraint on purpose and read the error.
3. **Month 2:** Auth end-to-end (bcrypt, JWT, refresh flow). Then transactions and the guarded-decrement pattern until they're reflex.
4. **Month 3:** Redis caching + invalidation discipline; BullMQ cron jobs; the ledger pattern.
5. **Advanced:** idempotency everywhere, race conditions (write a test that fires 10 parallel purchases), N+1 hunting, observability (structured logs, request IDs), and reading production incident write-ups.
