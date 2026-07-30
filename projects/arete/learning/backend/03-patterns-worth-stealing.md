# Arete Backend — Patterns Worth Stealing

Split out from the original single-file `backend-learning.md`. Covers guarded decrements,
idempotency, the ledger pattern, deterministic pseudo-randomness, cache-aside with invalidation,
BullMQ background jobs, non-fatal side effects, server-side display substitution, and idempotent
seeding. See also `02-prisma-and-data-modeling.md`.

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

