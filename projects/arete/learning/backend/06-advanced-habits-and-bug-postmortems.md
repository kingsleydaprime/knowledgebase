# Arete Backend — Advanced Habits & Bug Postmortems

Split out from the original single-file `backend-learning.md`. Covers general advanced habits
plus four real launch-week bug postmortems: the seed race, the shared-cache leak, disagreeing
rankings, and the inert rate limiter.

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

