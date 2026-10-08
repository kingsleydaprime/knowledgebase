# 07 — Time: days, "any time", quiet hours and weeks

*MyPaddie (written up 2026-10-08). Files: `src/shared/time.ts`, `src/features/xp/xp.ts`
(`lateAfter`, `anyTimeEndsAt`), `src/features/today/focus.ts`, `src/features/settings/schedule.ts`,
`src/features/reviews/periods.ts`, `src/features/tasks/recurrence.ts`.*
See also: [[02-rules-engine-design]] (never read the clock; local calendar days) · [[06-scheduling-and-push]]

Most of MyPaddie's subtle bugs were about time. Each section is one idea and the
bug or request that taught it.

## Store instants, reason in local days

The database stores `timestamptz` (an instant). Every rule asks local questions:
"what day is this *for them*?", "is it before their quiet hours?". So there are
two kinds of value, and they never mix:

```ts
dayKey(at, tz)              // instant → "2026-10-08" (their calendar day)
localTimeOf(at, tz)         // instant → "21:30"
zonedInstant(day, time, tz) // "2026-10-08" + "21:30" → the instant
addDays("2026-10-08", 1)    // pure date arithmetic on the string, no zone involved
```

Day arithmetic happens on `"YYYY-MM-DD"` strings (`addDays`), never by adding
86 400 000 ms to a `Date`. That way a DST change can't move a day.

## A sentinel value and its cost: "any time" = 23:59

"Do it any time today" was stored as **due 23:59** on that day: a real
timestamp, so it sorts, filters and counts for capacity. It's convenient, but
it's a **sentinel**: a magic value meaning something other than what it says.
Every reader has to know about it:

- The task page shows an empty time, not 23:59.
- Overdue checks treat it as "the day's end", not "late after 23:59".
- Labels say "any time", not "23:59". This was missed in one place (Today said
  "23:59"), and Paddie was shown "23:59" too.
- Reminders at 23:59 fall in quiet hours, so any-time **must-dos never
  escalated**. The escalation rule (due time passed, it's today) could never be
  true while the user was awake.

And there's a **second** shape of "any time": a recurring task with no time has
`due_at = null` and only `occurs_on` (its day). One fix had to handle both:

```ts
export function anyTimeEndsAt(dueAt: Date | null, occursOn: string | null, dayEndsAt: string): Date | null {
  const day = dueAt === null ? occursOn : localTimeOf(dueAt, tz) === "23:59" ? dayKey(dueAt, tz) : null;
  return day === null ? null : endOfActiveDay(day, dayEndsAt);
}
```

**Lesson:** a sentinel is cheap to write and expensive to read. If you use one,
put the "is this the sentinel?" check in **one function**, and grep for the raw
value (`"23:59"`) to find every reader that skipped it.

## The day ends at quiet hours, not midnight

The user's rule: the day's tasks belong before quiet hours (22:00). So "any time"
means *before 22:00*:

- Done after 22:00 → **late** (reduced XP, still worth doing).
- Today shows it as overdue after 22:00, including yesterday's leftovers.
- **Missed** (the point deduction for ignoring a need) is still judged at
  **midnight**, the same as timed tasks. The late evening is for recovering, not
  for losing points.

**Late** and **missed** are separate deadlines, each with its own reason. The
first draft said both would move to 22:00; tracing the code showed they
shouldn't.

Quiet hours that start after midnight (night owls) mean the day runs to 23:59:

```ts
export function dayEndsAt(s: { quietStart: string }) { return s.quietStart >= "12:00" ? s.quietStart : "23:59"; }
```

## A first occurrence has to be a real day

A Tuesday habit set up on a Wednesday got a stray Wednesday row, which took
Wednesday's capacity and could become a slip. `firstOccurrence(rule, start, now,
time)` returns the first day **from the start** that the rule includes, skipping
today if its time has already passed. Every recurring task is created through it.

The visible side effect: a routine set up at 07:30 with a 06:00 start begins
**tomorrow**. That's correct, but it confused the user ("my routine doesn't show
up"). The fix was **showing it**: the Tasks tab says "Next: Tomorrow · 06:00"
instead of nothing.

## "Later": a time far off shouldn't outrank now

Today ranked "must-dos still to come today" first, however far off. An evening
routine at 21:00 sat on top all morning. Now a task with a set time more than
`showTimedWithin` minutes away (a setting, default 60) is **later**:

```ts
const isLater = (t) => !t.startedAt && !t.anyTimeEndsAt && t.dueAt !== null
  && t.dueAt.getTime() - now.getTime() > soonMinutes * 60_000
  && !(t.routine && begun.has(t.routine.id));
rank = (isLater(t) ? 100 : 0) + group * 6 + priority * 2 + (overdue ? 0 : 1);
```

The `+100` keeps the usual order *within* the later group, so must-dos still
come first among things hours away. The morning brief (SQL) uses the same rule
and the same setting, so the notification and the screen agree.

## Whose week? Sunday or Monday

Reviews, trends and "this week" used Monday–Sunday. The user's week is
Sunday–Saturday, and the app has other users, so it's a setting (`weekStart`),
not a new fixed rule:

```ts
const start = addDays(day, -(weekStart === "sunday" ? weekdayOf(day) : (weekdayOf(day) + 6) % 7));
```

- `weekdayOf` is 0 = Sunday … 6 = Saturday, so for Sunday weeks the offset is
  the weekday itself.
- In SQL, `extract(isodow …)` is 1 = Monday … 7 = Sunday, so a Sunday week ends
  when `isodow = 6`.

The two numbering schemes are a classic off-by-one trap, and the tests pin both.

Two things fall out of making the week a setting:
- **Stored data keeps its own truth.** Reviews written under Monday weeks keep
  "Week of 5 Oct" from their own start date. Don't re-derive old labels with the
  new rule.
- **Not every "week" is the calendar week.** "Can I take on a weekly
  commitment?" is measured over the **next 7 days**. On a Friday, a
  calendar-week window is two days long, and the verdict would swing with the
  weekday. The Commitments screen shows the calendar week ("this week, 3 days
  left"); the decision uses the rolling window.

## Escalation from a time of day, as a setting

An any-time must-do now escalates from 15:00 (`anyTimeNudgeFrom`). The rule is
one SQL condition, `t.any_time_day = t.today and t.local_time >= sc.any_time_from`.
The validation is the same as every other schedule time: a time inside quiet
hours or a phone-free window is refused, because it would never arrive.
