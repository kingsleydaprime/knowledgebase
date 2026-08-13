# Arete — Product Logic & Project Story

From [`../learning/backend/05-product-logic-case-studies.md`](../learning/backend/05-product-logic-case-studies.md),
[`../learning/mobile/06-the-home-trail-case-study.md`](../learning/mobile/06-the-home-trail-case-study.md),
and the study paths.

---

### Q1. [Intermediate] 🔥 Describe the streak state machine.

**Strong answer covers:** a nightly evaluator (23:59) judges the previous day and records one of
`continue` / `grace` / `shield` / `shield_used` / `reset` as a `StreakEvent`. `continue` when the
day's requirement was met; `grace` is a built-in allowance so a single miss doesn't destroy weeks of
progress; `shield` is an item the user bought that absorbs a miss; `reset` when nothing saved it.

**The design points worth making:**
- Every outcome is an **event**, not a mutation of a counter — so the streak is explainable and
  re-derivable, and "was this day already evaluated?" is a query. (See
  [02-patterns-and-postmortems.md](02-patterns-and-postmortems.md) Q3.)
- Shield inventory is `count('shield') - count('shield_used')` — a feature that needed no schema
  change at all.
- Grace exists for a **product** reason: a streak that's trivially destroyed stops motivating and
  starts punishing, and a user who loses a 40-day streak to one bad day usually doesn't start again.

---

### Q2. [Intermediate] 🔥 "Making streaks winnable" — what was the `QUESTS_PER_PILLAR` fix?

**Strong answer covers:** the daily requirement was set at a level that, in practice, most users
could not hit — so streaks broke constantly and the mechanic inverted from motivating to
demoralising. The fix was a **tuning** change rather than a code change: reduce the per-pillar quest
count so a normal day clears the bar.

**Why it's a good interview answer:** it's a case of a system working exactly as designed and being
wrong anyway. The bug wasn't in the code; it was in the number. Being able to say "the implementation
was correct and the product was broken, and I could tell those apart" is a genuinely useful signal —
and the diagnosis came from looking at how many users actually held streaks, not from a bug report.

---

### Q3. [Advanced] 🔥 What's the hardest correctness problem in a gamified app?

**Strong answer covers:** anything where the user's *balance* or *rank* is derived from many events
across many code paths — because every path has to agree, and disagreements are visible to users who
care intensely about the number. Concretely in Arete: two rank formulas producing different answers
(postmortem Q8), and per-user data leaking through a shared cache key (postmortem Q6). Both are
"the number is wrong" bugs, and both were invisible to tests because each path was individually
correct.

**The mitigations to name:** one function computes each user-visible number; the ledger makes any
number explainable; every ranking sort ends in a unique tiebreaker.

---

### Q4. [Intermediate] How do you decide what to compute versus what to store?

**Strong answer covers:** Arete leans hard toward **derive**, and there's a consistent rationale —
daily missions are derived from a hash (no storage, no migration, works retroactively), elapsed quest
time is derived from timestamps (survives backgrounding), the Home Trail is derived from data the
client already has (no endpoint), shield inventory is derived from the ledger (no column).

**When to store instead:** when the derivation is expensive on the read path (hence the Redis cache
for progression), when the inputs can change and you need the historical answer, or when two parties
must agree on a result they can't both compute. Say the boundary, not just the preference.

---

### Q5. [Intermediate] 🔥 Empty states — why do you keep bringing them up?

**Strong answer covers:** they're the **first thing a new user sees**. A trail with no progress, a
leaderboard with no rank, a quest list before onboarding completes — those are the day-one
experience, and designing them last means designing the most-seen screen worst. The seed race
(postmortem Q7) is the extreme version: the empty state wasn't just unpolished, it was a dead end
that told the user to do something they'd already done.

---

### Q6. [Advanced] 🔥 Walk me through the worst production incident and how you handled it.

**Strong answer covers the seed race, told as a process rather than a fact:**
1. **Symptom** — users completing onboarding are told forever to complete onboarding.
2. **Investigation** — no SQL shell available, so a throwaway Prisma script answered three
   questions in sequence: do users exist (✓), do tasks exist (✓), do user-pillars exist (✗). Root
   cause isolated in three queries.
3. **Root cause** — accounts registered 77 seconds before the seed ran, so `findMany` returned `[]`,
   and `$transaction([])` **succeeded**, so onboarding was marked complete with zero pillars.
4. **Fix, in three parts** — repair the affected data, add a loud guard at the source, and make
   quest generation self-heal anyone already in the bad state.
5. **Lesson** — whenever a loop drives writes, ask what an empty collection does.

**Why this structure works:** symptom → method → cause → three-layer fix → generalised lesson. It
shows debugging technique, not just the answer, and the self-healing step in particular reads as
someone thinking about users already affected rather than only about the code.

---

### Q7. [Intermediate] What would you do differently if you started Arete again?

**Strong answer covers — pick concrete ones:**
- **Seed content as part of the deploy, before the app accepts traffic**, rather than as a step that
  can race registration. The bug was a *sequencing* problem dressed as a code problem.
- **Establish the "one function per user-visible number" rule from day one** — both the ranking
  disagreement and the cache leak are variants of "the same fact computed in two places."
- **Write the test that violates each protective control** as the control is added — the rate limiter
  was configured and inert for weeks, and one test asserting a 429 would have caught it immediately.
- **Timezone-aware scheduling from the start**, rather than all-UTC cron against a user base in
  UTC+1.

---

### Q8. [Beginner] Explain Arete to a non-technical interviewer in three sentences.

**Strong answer covers:** it's a self-improvement app that turns habits into daily quests across a
few areas of life, with XP, streaks and leaderboards to make consistency feel like progress rather
than obligation. Each day it generates a personalised set of tasks; completing them builds a streak,
and missing one costs you unless you've earned protection. The technical work is mostly about making
the numbers trustworthy — because in an app whose entire value is a streak, getting someone's streak
wrong is the only unforgivable bug.

That last sentence is the one that lands. It connects the engineering to the product.

---

### Q9. [Advanced] How would you scale this if it went from hundreds of users to a million?

**Strong answer covers, in order of what breaks first:**
1. **The nightly per-user loops.** Generating quests and evaluating streaks by iterating every user
   in one process doesn't survive a million rows — it becomes a partitioned/fan-out job with
   per-batch checkpointing, so a failure resumes rather than restarting.
2. **The leaderboard.** Ranking every user on read is untenable; it becomes a periodically
   materialised ranking (which the six-hourly cron already gestures at) with the personal position
   computed separately — exactly the split the cache bug forced.
3. **The cache.** Per-user keys at a million users is a memory-sizing problem, and the short TTL
   becomes a thundering-herd risk on expiry.
4. **Push delivery.** Sending a million notifications at 7am is a rate-limit and batching problem in
   its own right.

The honest framing: none of this was worth building at launch scale, and the design decisions that
*do* matter — the ledger, idempotency, guarded updates — are the ones that would still be right at a
million users. Naming which choices scale and which were deliberately scale-inappropriate is the
answer.

---

### Q10. [Intermediate] 🔥 What did building both the backend and the mobile app teach you that building one wouldn't?

**Strong answer covers:** where the seam between them actually is. Three concrete examples from this
project —
- **Server-driven display text** exists because a client fix takes days to reach users and a server
  fix takes minutes; that trade only becomes obvious once you've shipped a mobile release.
- **The refresh-token queue** exists because the server's short access-token TTL creates a *client*
  concurrency problem the server never sees.
- **The Home Trail** was built with no new endpoint because owning both sides makes it obvious when
  the client already has the data.

The generalisable version: owning both sides changes what you consider a "backend problem." Most
of the interesting decisions here live in the gap between them.
