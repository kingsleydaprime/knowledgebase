# Arete Backend — Game/Product Logic Case Studies

Split out from the original single-file `backend-learning.md`. Covers making streaks winnable and
the streak evaluator state machine. See also `06-advanced-habits-and-bug-postmortems.md`.

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

