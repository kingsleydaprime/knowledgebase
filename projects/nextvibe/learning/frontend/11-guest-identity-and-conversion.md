# 11 — Guest Identity & Conversion

*Written 2026-09-21, from adding the post-score login prompt to the games.*

See also: [[projects/nextvibe/learning/frontend/03-auth|03 — Auth]],
[[projects/nextvibe/learning/frontend/07-payments-games|07 — Payments & Games]],
[[projects/nextvibe/learning/frontend/10-typed-api-contracts|10 — Typed API Contracts]]

---

## The problem shape

People scan a QR code at an event, play the game, see their score, and leave
without ever signing in. Their score is real — it just never reaches the
leaderboard, because the leaderboard is keyed on accounts.

The temptation is to force signup before play. That kills the thing that makes
it work at a party: **zero friction between scanning and playing.** So the
architecture has to let someone be a real participant *before* they are a user,
and then convert them later without losing anything.

That's the pattern worth understanding, and it generalises well beyond games —
guest carts, anonymous drafts, trial workspaces.

---

## Two-sided anonymous identity

```
Browser                              Server
───────                              ──────
localStorage "nv_anon_game"          Redis "anon:game:<id>"
  anonymousId: "V1Stg…"       ←→       sessions[]
  expiresAt:   +7 days                   submissions[] { roundId, score, … }
  pendingSessions[]                    TTL: 7 days
```

The client holds an opaque id; the server holds the actual gameplay under that
id. Two details make this work rather than merely function:

**1. The TTLs match, deliberately.** localStorage carries its own `expiresAt`
and the Redis key carries `ANON_TTL_SECS` — both 7 days, both refreshed on
every submit. A mismatch here is a silent, confusing bug class: if the client
outlived the server, you'd offer people a merge that quietly does nothing; if
the server outlived the client, orphaned data would accumulate forever.

**2. Scores are computed and stored server-side even for guests.** The score is
not sitting in React state waiting to be lost. That single decision is what
makes the prompt *safe* — a guest who ignores it, refreshes, or navigates away
loses nothing, because the score is already durable under their anonymous id.

> **Design rule:** make the anonymous path durable *first*, then add the
> conversion prompt. A prompt on top of ephemeral state is a trap — it raises
> the cost of dismissing it.

---

## In-place auth beats a redirect

The version that already existed sent people to `/auth/login?from=/game/abc`.
That works, but look at what it costs:

- full page unload, so anything in memory is gone
- the score screen is replaced by a login form — the reward vanishes
- you need `?from=` plumbing, and validation that `from` is a safe internal path
- the other game surface had grown an entire `sessionStorage`
  save-and-auto-resubmit path *just to survive the round trip*

`AuthBottomSheet` already existed and does login/register **in place** via
mutations and an `onSuccess()` callback. Using it means:

```tsx
<AuthBottomSheet
  open={open}
  prompt={`You'd be #${rank} — sign in to claim your spot on the leaderboard.`}
  onClose={…}
  onSuccess={…}
/>
```

No navigation. No `from=`. No restore logic. The score stays on screen the
whole time, which is also what makes the pitch coherent.

**The transferable lesson:** when a flow needs auth *mid-task*, a modal/sheet
that resolves auth without unmounting the task is almost always worth more than
the redirect it replaces — and it deletes the state-restoration code the
redirect forced you to write.

---

## The beat, and why the cleanup matters

```tsx
useEffect(() => {
  if (eventId && isScorePromptDismissed(eventId)) return;
  const timer = setTimeout(() => setOpen(true), BEAT_MS);
  return () => clearTimeout(timer);   // ← not optional
}, [eventId]);
```

`BEAT_MS = 1800` is a product decision with a reason: the prompt says *"You'd be
#3"*, and that only persuades if they have already read the #3. Firing on the
same frame as the score covers the reward before it registers.

**The cleanup is a real bug fix, not ceremony.** Without it, a player who taps
"Back to Lobby" during the 1.8s window gets an auth sheet popping up over the
lobby — the timer fires against an unmounted component's intent. Any
`setTimeout` that ends in `setState` needs its `clearTimeout`, and "the delay is
short" is not a defence; it's exactly the window a user can act inside.

---

## Where dismissal state belongs

"Show it once per event, and remember 'not now'" needs persistence. The obvious
move is a new localStorage key. The better move was to put it **inside the
existing anonymous store**:

```ts
interface AnonGameStore {
  anonymousId: string;
  expiresAt: number;
  pendingSessions: AnonPendingSession[];
  dismissedPrompts?: Record<string, number>;   // eventId → timestamp
}
```

Three things fall out for free:

- **It inherits the 7-day TTL.** A guest returning a week later is a fresh
  prospect, not a permanently silenced one. A standalone key would have
  suppressed the prompt forever, which nobody would ever notice was wrong.
- **`clearAnonGameData()` wipes it on a successful merge** — correct, because
  once they're signed in the prompt is moot anyway.
- One key to reason about instead of two that can disagree.

It also **fails open**:

```ts
export function isScorePromptDismissed(eventId: string): boolean {
  if (!eventId) return false;
  return Boolean(readStore()?.dismissedPrompts?.[eventId]);
}
```

Missing store, unreadable JSON, absent field — all return `false`, so a storage
problem shows the prompt rather than silently suppressing it. **For suppression
flags, failing open is almost always right:** the failure is visible and
recoverable, where failing closed is invisible and permanent.

---

## Derived data should refuse to guess

The anonymous submit endpoint returns `{ score, roundId, shareToken }` — no
rank, because guests have no `GameSessionEntry` to rank. But the session
leaderboard is a public endpoint whose entries are already on screen, so the
rank can be derived client-side:

```ts
export function wouldBeRank(entries: unknown, score: number): number | null {
  if (!Array.isArray(entries)) return null;
  if (entries.length === 0) return 1;

  const scores = entries.map((e) => e?.totalScore ?? e?.score ?? 0);
  const ahead = scores.filter((s) => s > score).length;

  // The API returns at most 50 entries. Behind every one of a full board means
  // the true rank is unknowable — say nothing rather than claim #51.
  if (ahead === entries.length && entries.length >= LEADERBOARD_CAP) return null;

  return ahead + 1;
}
```

The `take: 50` guard is the part worth internalising. Deriving a value from a
**truncated** list is the classic way to produce confident nonsense. Any time
you compute over an API response, ask whether that response is complete — and
if it can be capped, handle the capped case explicitly.

Returning `null` then drives honest copy at the call site:

```tsx
rank
  ? `You'd be #${rank} — sign in to claim your spot on the leaderboard.`
  : "Sign in to save your score to the leaderboard."
```

**A wrong number is worse than no number when the number *is* the pitch.**

---

## Escalate, don't replace

The passive banner ("Log in to see the full leaderboard & keep your score")
stayed. The sheet was added alongside it.

They do different jobs: the sheet asks **once**, loudly, at peak intent; the
banner is the quiet path that's always there for someone who dismissed the
sheet or comes back later. Deleting the banner would have left dismissers with
no route at all.

The general version: when adding an interruptive prompt, keep the ambient
affordance. The prompt is a one-shot with a memory; the affordance is
permanent. Removing the second because the first is "better" strands everyone
who said no once.

---

## Still open: the partial-merge bug

Worth recording because the prompt makes it more reachable, not less.

`mergeAnonymousSessions` merges only the events the user confirmed, then runs
`redis.del(key)` on the **whole** anonymous cache. A guest who played three
events and confirms one loses the other two permanently. `AnonymousMergeDialog`
lets them uncheck events, so this is reachable today.

The client half mirrors it — `mergeAndClear` calls `clearAnonGameData()` in a
`finally`, so a failed merge still destroys the local record of what was
pending.

**The pattern to recognise:** a non-transactional two-phase operation across a
network boundary, where the cleanup is unconditional. Cleanup should be scoped
to what actually succeeded — delete the merged sessions, keep the rest — and it
should not run at all on failure.
