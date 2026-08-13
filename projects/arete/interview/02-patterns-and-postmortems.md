# Arete — Patterns & Postmortems

From [`../learning/backend/03-patterns-worth-stealing.md`](../learning/backend/03-patterns-worth-stealing.md)
and [`06-advanced-habits-and-bug-postmortems.md`](../learning/backend/06-advanced-habits-and-bug-postmortems.md).

**The single most valuable file in the vault for a senior interview.** Every item is a named
pattern or a real production bug with a real root cause.

---

### Q1. [Advanced] 🔥🔥 A user spends 150 gems. Two requests arrive at once. How do you stop the balance going negative?

**The broken version (time-of-check-to-time-of-use):**
```ts
const user = await prisma.user.findUnique(...);
if (user.gems >= 150) {                          // check
  await prisma.user.update({ decrement: 150 });  // act — both requests passed the check
}
```

**The correct version — the condition lives inside the write:**
```ts
const result = await tx.user.updateMany({
  where: { id: userId, gems: { gte: 150 } },   // condition INSIDE the update
  data:  { gems: { decrement: 150 } },
});
if (result.count === 0) throw new BadRequestException('Not enough gems');
```

**Strong answer covers:** the database serialises the two statements; the second finds `gems < 150`,
matches **zero rows**, and `count === 0` is the signal to reject. The check and the write are one
atomic statement, so there is no window between them.

**Say this line:** *"This one pattern prevents every negative-balance bug ever written."* It applies
to inventory, seat booking, rate limits, coupon redemption — anywhere a read-then-write decides
whether a write is allowed.

**Follow-up:** *"Why not a transaction with SELECT FOR UPDATE?"* — that also works and is the right
answer when the decision needs multiple reads. The guarded update is preferable when the condition is
expressible in the `WHERE`, because it's one round-trip and holds no lock across application code.

---

### Q2. [Intermediate] 🔥 Mobile networks retry and users double-tap. How do you make mutations safe to call twice?

**Strong answer covers three techniques, all used in Arete:**
1. **Return early with the same response** — `startQuest` sees `quest.startedAt` already set and
   returns it rather than restarting; `pauseQuest` on an already-paused quest is a no-op that
   returns the same state.
2. **Upsert on a unique key** — the write itself is idempotent.
3. **Check a ledger before awarding** — the perfect-day bonus looks for an `XpTransaction` with
   `reason: 'perfect_day'` and `referenceId: '2026-07-14'` before granting. **The date is the
   idempotency key.**

**The framing that lands:** idempotency isn't a special feature for payment endpoints. On a mobile
client, *every* mutation will eventually be delivered twice, so "what does calling this twice do?"
is a question every endpoint has to answer.

---

### Q3. [Advanced] 🔥🔥 You store XP as a counter *and* as a ledger. Isn't that redundant?

**Strong answer covers:** `XpTransaction` rows record every change with amount, reason
(`quest_complete`, `streak_penalty`, `perfect_day`) and reference; `StreakEvent` rows record
`continue`/`grace`/`reset`/`shield`/`shield_used` per day. Three things the counter alone cannot do:

1. **Dedupe.** "Did this day already count?" is answerable as "does a `continue` event exist for this
   date?" A counter has no memory of *why* it has the value it has.
2. **Audit.** Any balance can be explained by replaying its ledger — which matters the first time a
   user says "my XP is wrong."
3. **Derived features for free.** Streak-shield inventory is
   `count('shield') - count('shield_used')`. **No new column, no migration.**

**The name to use:** event sourcing lite. You keep the counter for fast reads and the log for truth.

**Follow-up they may push:** *"What's the cost?"* — write amplification, table growth, and the risk
of the counter and the ledger disagreeing. Which is a real risk, and the mitigation is that every
write to the counter goes through the same code path that appends the event.

---

### Q4. [Advanced] 🔥 Each user needs a different daily mission that rotates daily but never changes on refresh. `Math.random()` fails. What do you do?

**Strong answer covers:** hash instead of randomise —

```ts
function fnv1a(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
const variant = eligible[fnv1a(`${userId}:${taskId}:${dateStr}`) % eligible.length];
```

Same inputs → same output, forever. Different user or different day → different pick. **Zero
storage** — the assignment is pure maths rather than a row in a table.

**Details that show you understand the code:** `Math.imul` does a true 32-bit integer multiply
without float precision drift; `>>> 0` forces an unsigned 32-bit result. FNV-1a is chosen because
it's tiny, fast, and has good enough spread — it is *not* a cryptographic hash and doesn't need to
be.

**Bonus from the notes:** determinism buys you time travel — you can compute what any user's mission
*was* on any past date, or *will be* tomorrow, without having stored anything.

---

### Q5. [Intermediate] 🔥 Describe cache-aside with explicit invalidation, and the rule that comes with it.

**Strong answer covers:** read path — check Redis, on miss run the expensive queries, `set` with a
short TTL (60s), return. Write path — **every mutation that changes the answer deletes the key**.

**The rules to state:**
- Keep a short TTL *even with* invalidation, as a safety net for the invalidation you forgot.
- Key names include the user id where the data is per-user.
- When adding a new mutation, grep for `cache.del` and ask which keys it stales.

That last habit is what the next question is about.

---

### Q6. [Advanced] 🔥🔥 Two users both at 0 XP. One sees the *other's* "YOUR POSITION #1" card. What happened?

**Strong answer covers the exact mechanism:**
```ts
const cacheKey = `leaderboard:${page}:${limit}`;   // ← no user id
const result = { ...board, userPosition: userPos }; // userPosition is PERSONAL
await this.cache.set(cacheKey, result, 30);         // ...cached for everyone
```
The first user in a 30-second window caches *their* position, and every other user is served it.

**The fix:** split cacheable from personal. The board (identical for everyone) stays under the global
key; `userPosition` is computed fresh per request and merged in after the cache read.

**The lesson, and say the last sentence:** before every `cache.set`, ask "is any field in this payload
different per user?" If yes, either the key includes the user id or the field stays out of the cache.
**This bug class causes real-world data breaches — treat cache-key scoping as security, not just
correctness.**

This is the best bug in the vault. It's simple enough to explain in ninety seconds and serious
enough that every interviewer has seen a version of it.

---

### Q7. [Advanced] 🔥 A user completes onboarding and is told forever to complete onboarding. Debug it.

**Strong answer covers:** the account was registered **77 seconds before the seed ran**, so
`pillar.findMany` returned `[]`. Then:

```ts
await this.prisma.$transaction(pillars.map(p => upsertUserPillar(p)));  // empty array
await this.prisma.user.update({ data: { onboardingComplete: true } });  // still runs
```

`[].map()` produces an empty transaction, which **succeeds**. Nothing threw, so the code marched on
and marked onboarding complete with zero pillars attached — **vacuous success**.

**The three-part fix — memorise this shape, it's reusable for any data bug:**
1. **Repair the data** — backfill the missing rows for affected users.
2. **Fail loudly at the source** — `if (pillars.length < 3) throw new BadRequestException('Server
   content not initialized')`. A visible error beats a silently corrupted account.
3. **Self-heal downstream** — quest generation detects "onboarded but no pillars" and creates them,
   so anyone already in the bad state is fixed on their next request with no support ticket.

**The lesson:** whenever a loop or `map` drives writes, ask what happens when the collection is
empty. If the answer is "we silently pretend success," add a guard.

---

### Q8. [Advanced] 🔥 The position card says #1 and the list says #2, for the same user at the same instant. Why?

**Strong answer covers:** two formulas for one number. The list sorted by
`(overallRank, totalXp)` and numbered positionally; the card computed
`count(users with totalXp > mine) + 1` — which ignores `overallRank` and gives ties the same number.
Two code paths, two answers, both "correct" in isolation.

**The fix:** one private `getRankedUsers()` as the single source of truth — the list, the position
card, and the worldRank cron all derive from that one ordering.

**The second half, which is the more transferable part:** ties are broken deterministically
(rank → XP → earliest `createdAt` → id), because JavaScript's `.sort()` on equal keys otherwise
inherits arbitrary database return order, so a refresh reshuffles equal users. **Every sort feeding a
user-visible ranking needs a total order — always add a final unique tiebreaker.**

**The lesson in one line:** any number shown in two places must be computed in exactly one place.

---

### Q9. [Intermediate] 🔥 "The rate limiter was configured but never enforced." How does that happen, and how do you catch it?

**Strong answer covers:** the module was registered with limits, but nothing applied the guard to the
routes — so the configuration existed, looked correct in review, and did nothing. This is the same
family as validation decorators with no `ValidationPipe` and CORS options that are never wired in.

**How you catch it:** the only reliable way is a test that **exceeds the limit and asserts a 429**.
Reading configuration proves configuration. The general rule: for any protective control — rate
limit, auth guard, validation, CSRF — the test must attempt the thing that should be blocked. If
your test suite only exercises the happy path, every protection in the system is unverified.

---

### Q10. [Intermediate] What are "non-fatal side effects" and where do they matter?

**Strong answer covers:** a push notification that fails to send must not fail the quest completion
that triggered it. So secondary effects are wrapped and logged rather than propagated — the primary
transaction commits, the side effect is best-effort.

**The discipline:** be explicit about which effects are part of the transaction and which are
best-effort, and *log the best-effort failures*, because silently swallowed side effects become "the
notifications stopped working three weeks ago and nobody noticed."

---

### Q11. [Intermediate] Server-side display substitution — why does the server decide the wording?

**Strong answer covers:** the variant system means the server sends the display text for a task, not
just an ID the client maps to a string. Copy changes ship without an app-store release — which is
the entire argument on mobile, where a client update takes days and reaches users unevenly. The cost
is a chattier payload and text that can't be localised client-side; the mitigation is that the
*selection* is deterministic (Q4), so the server isn't storing per-user copy either.

---

### Q12. [Intermediate] Seeding as "idempotent content deployment" — what does that mean?

**Strong answer covers:** the seed defines content (pillars, tasks, variants) and must be safe to run
on every deploy, so it's written with upserts on stable keys rather than inserts. That makes content
a **deployable artefact** rather than a one-off setup step. The seed race in Q7 is the cautionary
tale for the ordering: content must exist before users can depend on it, and the code that depends on
it must fail loudly when it doesn't.
