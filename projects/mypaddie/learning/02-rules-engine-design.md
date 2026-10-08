# 02 — Rules engine design

*MyPaddie, Day 1 (2026-10-05). Files: `src/features/{xp,mode,money}`, `src/shared`.*
See also: [[01-supabase-schema-and-rls]] · [[03-testing]]

## Pure functions: plain data in, plain data out

Two clients (the AI chat via MCP, and the phone app) must never disagree about
XP, mode or money stage. So the rules live in **one module that knows nothing
about where it's called from** — no Supabase, no Next.js, no `fetch`.

```ts
computeMode({ now, slips, ignoredNeeds, checkins, override }) // → { mode, reasons }
```

The caller (MCP tool, API route, cron job) loads rows, calls the function, saves
the result. The function only does the thinking. That's what makes it testable in
milliseconds with no database.

## Never read the clock inside the engine

```ts
// ✗ untestable: the answer depends on when the test runs
function isLate(task) { return new Date() > task.dueAt; }

// ✓ testable: the caller passes the moment
function isLate(task, doneAt: Date) { return doneAt > task.dueAt; }
```

"Is this need ignored yet?", "was this slip in the last 7 days?", "is it day 31 of
the audit?" all depend on *now*. Pass it in, and a test can stand at any instant
— 23:59 on the due day, one minute past midnight, a DST change.

## "Day" means a local calendar day

A need due at 07:00 isn't "ignored" at 07:01 — there's the rest of the day to
recover. It's ignored once its **Lagos calendar day** has ended. Two traps:

- UTC midnight is 01:00 in Lagos. Using UTC days would end the day an hour early.
- "Last 7 days" by 24-hour blocks behaves strangely around midnight. Counting
  calendar days (`dayKey` → `"2026-10-05"`) doesn't.

## Splitting without losing points: largest remainder

10 XP across 34/33/33 → exact shares 3.4 / 3.3 / 3.3. Round each → 3+3+3 = 9. A
point vanished. Round up → 12. Points invented.

**Largest remainder**: give everyone the floor (3/3/3 = 9), then hand the leftover
point(s) to the largest fractional parts (.4 wins) → 4/3/3 = 10. ✓ Ties broken by
a fixed rule (bigger weight, then pillar order) so the result is the same every
run. Same method splits money in the waterfall: every naira accounted for.

## Return the reasons, not just the answer

```ts
{ mode: "strict", reasons: [{ kind: "repeated_slip", key: "item-rhapsody", count: 2 }] }
```

The AI needs to say *"Second time this week. What's different?"* — it can only do
that if the engine tells it *why* it chose strict. Facts in, tone out.

## The bug a test caught: rolling windows flap

First version: after the audit, compare needs vs income over **the last 30 days**.
A test failed on day 31 — income showed as 0. Why?

```
day 1:  monthly salary lands
day 31: "last 30 days" = days 2–31 → the salary just slid out → DEFICIT
day 32: still deficit... until next payday slides in → SURPLUS
```

A rolling window over a once-a-month event flips the answer depending on where
payday sits. Paddie would tell you you're broke on Tuesday and fine on Thursday.

**Fix: fixed periods.** Count 30-day periods from the first log (period 1 = the
audit). The stage comes from the last *complete* period, so it holds steady for a
whole period, and the first verdict after the audit is exactly what the audit
measured.

Lesson worth keeping: **rolling windows are fine for frequent events (slips per
week), bad for rare, lumpy ones (monthly salary).**

## Interview framing

*"Why keep business rules out of the API handlers?"* — one source of truth for
several clients; fast tests with no I/O; the rules can move (MCP server → cron →
PWA) without being rewritten.

## Your call: who decides a reason is "valid"? (2026-10-05)

You said slips protect a need "if the reason is valid", then picked **(c): Paddie
judges, and a fixed rule backs it up**. Sharpened:

> Judgement and rules fail in opposite ways. An AI judge can be talked round by a
> good story; a counter can't, but a counter can't tell a real emergency from a
> lazy morning. Put the judge first and let the rule only ever turn a yes into a
> no — then neither failure is unbounded.

Implementation: `judgeSlip` in `src/features/slips`. The 3rd time the same reason
is given for the same habit within 7 days, it's an excuse. "Same reason" uses a
short category Paddie assigns ("tired"), falling back to normalised text, because
exact string matching would treat "tired" and "I was tired." as different.

Interview framing: *"How do you combine an ML/LLM decision with hard business
rules?"* — the model proposes, deterministic guardrails constrain; guardrails
should be monotonic (only make the outcome safer), so the combination is never
less safe than the rule alone.

## Day 2: rules stay pure, the repo does the I/O

```
features/tasks/
  recurrence.ts      pure: which days need a row        (tested with fixed dates)
  tasks.repo.ts      I/O: load rows → call pure fn → save result
  tasks.tools.ts     MCP: validate input → call repo → shape the reply
```

The repo is the only file that knows Supabase exists. If Day 3's PWA needs the
same logic, it calls the repo; the rules never change.

### Your call: catch up on demand (2026-10-05)

You picked (a): `get_today` settles what's owed before answering, instead of a
nightly job. Sharpened: *lazy evaluation* — compute state when someone asks,
make the computation idempotent, and you don't need a scheduler or a privileged
key. The cost: work happens on the request path, and nothing happens while
nobody asks (fine for deductions, not for push notifications — Day 3).

## Rules where the AI judges and the engine decides

The purchase check splits the work deliberately:

| Question | Who answers | Why |
|---|---|---|
| Is this a need in disguise? | the AI | needs context and judgement ("a laptop for school" vs "a second laptop") |
| Does it serve a goal? | the AI | matching free text to goals is language work |
| Are needs covered? Is there room in the wants bucket? | the engine | arithmetic on real numbers must be exact and repeatable |

The engine then applies a fixed rule order. Same idea as the slip check: the
model supplies judgement, deterministic code supplies the guarantees. Ask in an
interview: *"where would you not trust an LLM to decide?"* — anywhere the answer
is arithmetic over data you already have.

## Envelopes and idempotent money moves

A bucket is an *envelope*: a budget label, not a bank account. Spending draws
it down (floored at 0); income only fills envelopes when a split is accepted.
"Accept" must be safe to retry, so the income row itself records that it was
split:

```sql
update transactions set split_applied_at = now()
  where id = $1 and direction = 'in' and split_applied_at is null
  returning amount;   -- no row back = already split (or not yours): add nothing
```

The guard and the claim are one statement, so two simultaneous "accept"s can't
both win.

## Day 3: how a push notification actually reaches a phone

```
pg_cron (every 10 min) ─► private.send_nudges()
   1. spawn today's habit rows
   2. collect_nudges(now): what's due? record it so it never repeats
   3. net.http_post ──► /api/push  (shared secret from Vault)
                           └─ words it in Paddie's voice
                           └─ web-push: sign with VAPID private key
                                   ──► Google's push service (FCM)
                                           ──► your phone's service worker
                                                   └─ showNotification()
```

- **Service worker** (`public/sw.js`): a script the browser keeps registered
  even when the app is closed. It wakes for a `push` event, shows the
  notification, and handles the tap. Must be served uncached, or phones keep
  running an old version.
- **VAPID keys**: a key pair that proves notifications come from *your* server.
  The browser gets the public half when it subscribes; every send is signed with
  the private half, so nobody else can push to your subscription.
- **A subscription** is an address at the push service (an `endpoint` URL plus
  encryption keys). The service answers 404/410 when it's dead (app
  uninstalled) — that's the signal to delete it.
- **Why the database schedules it**: Vercel's free cron runs once a day. `pg_cron`
  runs every minute if asked, and deciding *who* to nudge in SQL means the web
  route needs no database key at all.
- **Testing a scheduler**: `collect_nudges(p_now)` takes the time as a parameter
  — the same "never read the clock inside the logic" rule as the TS engine — so
  the pgTAP test walks a whole day: 06:30 quiet, 07:10 nudge 1, 07:40 nothing,
  08:10 brief + nudge 2, … 13:00 stops after 4.

A test bug worth remembering: steps in a time-walking test must run in time
order. Querying 12:30 before 11:20 "used up" the 11:20 nudge and the test failed —
the function was right, the test was out of order.

## Learning log: spaced repetition in one table

Forgetting is predictable: the less sure you were, the sooner it fades. So the
interval before a topic comes back depends on the last confidence you gave it:

| Confidence | Review after |
|---|---|
| 1 shaky | 1 day |
| 2 | 2 days |
| 3 | 4 days |
| 4 | 7 days |
| 5 solid | 14 days |

**There's a name for this: the Leitner system** — flashcards move between boxes
reviewed at growing intervals; a miss sends a card back to box 1. Anki uses a
fancier formula (SM-2) that adjusts per card; Leitner-style fixed steps are
enough here and fit in one table.

Two small but real details:
- **Topics are grouped case-insensitively** ("Sliding window" = "sliding window ")
  — otherwise one topic splits into several with half the history each.
- **The latest *given* confidence wins**, not the latest session: a quick session
  where you didn't rate yourself shouldn't erase the "shaky" from last time.

## Idempotency: guard the intent, not just the row (2026-10-07)

Paying a monthly bill does two things: log the spend, and move `next_due` to
next month. To stop a double tap paying twice, the SQL used compare-and-set:

```sql
update bills set next_due = :following
where id = :bill and next_due = :due_i_read;   -- 0 rows → someone already paid it
```

Two calls that race on the *same* read are safe. But a smoke test made two
calls *one after the other*, and each one read the bill fresh:

1. Call 1 reads `next_due = Oct 31`, pays it, and moves the bill to Nov 30.
2. Call 2 reads `next_due = Nov 30`, and the compare-and-set succeeds — it
   pays November.

Every row-level guard passed, but the user only meant to pay once. That's
what a retried AI call or a double tap looks like. The fix has two parts, one
for each caller:

- **The app knows what it showed.** The button sends the due date on screen
  (`forDue`). If the bill has already moved on, that's a repeat.
- **The AI doesn't.** So a business rule decides: paying again within half a
  period of the last payment is almost certainly a repeat, so it's refused
  (`recently_paid`). Paying early on purpose has to say so (`ahead: true`).

The general lesson: an idempotency key has to identify *the user's intent*
("pay October's data"), not just "the current row". Compare-and-set protects
against concurrent writes. It does nothing against a sequential repeat that
re-reads.

## Options per item, not per screen (2026-10-07)

The close-out offers three things for each unfinished task: move, drop, or
"it slipped". The obvious build is three buttons on every row. But two of those
combinations break other rules in the system:

- **Dropping a need** would cancel it, and cancelled tasks are never "ignored",
  so the ignored-need deduction would quietly stop working. A new screen would
  have become a loophole in an old rule.
- **Moving a habit's day** would collide with tomorrow's own row of that habit.

So the rules decide which options each task gets (`optionsFor(task)`), and
both the AI tool and the app read from that one list. The check runs again on
the server (`checkDecision`), because a hidden button is not a rule. When you
add a new way to change something, ask: *which existing rules assumed this
change couldn't happen?*

## Greedy planning with reservations (2026-10-07)

The meal planner fills slots one at a time, in time order, and takes the best
recipe for each. That's a **greedy** algorithm: it never looks ahead, and it
never goes back to change an earlier pick.

Greedy alone has a classic bug. With 2 cups of rice, Monday lunch and Monday
dinner would both score Jollof as "makeable", because each was checked against
the full pantry. The fix is a **reservation**: when a slot takes a recipe,
subtract its ingredients from a working copy of the stock, so the next slot
sees only what's really left. The same pattern shows up anywhere you hand out
something limited: seats, budget, stock, capacity minutes in plan_day.

Ranking by a list of tie-breakers (`a || b || c` inside `sort`) keeps the rule
readable. Each comparison returns 0 on a tie, and `||` falls through to the
next criterion:

```ts
.sort((a, b) =>
  Number(a.missing.length > 0) - Number(b.missing.length > 0) ||   // makeable first
  Number(tooRecent(a)) - Number(tooRecent(b)) ||                   // then variety
  a.name.localeCompare(b.name))                                    // then stable by name
```

When ranking can't express a rule, use a filter instead. "Never the same dish
twice in a day" isn't a preference to weigh against stock; it removes options
outright. A smoke run showed that as a ranking it lost to "makeable" and served
Jollof twice.
