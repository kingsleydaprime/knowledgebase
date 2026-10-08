# 08 — Data modelling: small choices with big consequences

*MyPaddie (written up 2026-10-08). The full reasoning for each is in the repo's
`DECISIONS.md`; this file pulls out the transferable lessons.*
See also: [[01-supabase-schema-and-rls]] · [[05-mcp-server]] · [[07-time]]

## A column, not a new status: "in progress" is `started_at`

Tasks have a status enum (`pending`, `done`, `skipped`, `cancelled`). "In
progress" looked like a fifth value. But every rule already reads `pending`:
capacity, reminders, overdue, ignored needs, Today's list. A new status means
teaching *all* of them that `in_progress` is also open, and missing one is a bug.

Instead:
- In progress = `pending` **and** `started_at is not null`. Every existing rule
  keeps working unchanged.
- Pause = bank the stretch into `spent_minutes`, clear `started_at`.
- Done = `spent_minutes` + the current stretch is how long it took.
- A stretch over 12 hours is treated as a forgotten start, not time spent.

**Ask first:** is this really a new *state*, or a fact about an existing state?

## Derive what you can, store what you must

An event is "in progress" from its start time until it ends. That needs no
column and no job to flip it; it's computed from the time (`inProgress(e, now)`).
Only *starting early* is stored (`events.started_at`), because the clock can't
know that.

Stored state can disagree with reality (a job didn't run, a write failed).
Derived state can't.

## A jsonb column vs a table: the checklist

Steps inside a task are stored as `tasks.checklist jsonb` (`[{ text, done }]`, at
most 30, checked by a constraint), not a `task_steps` table. Steps aren't
scheduled, paid XP or reminded on their own. Nothing joins to them. A table would
add joins and RLS policies for no query that needs them.

Use a table when rows have **their own life** (queries, foreign keys, per-row
permissions). Use jsonb when it's a property of the parent that's read and
written as a whole. One awkward bit: a recurring task's next day must copy the
steps **unticked**, so the SQL that creates it rewrites the array:

```sql
(select jsonb_agg(jsonb_set(step, '{done}', 'false'::jsonb) order by n)
   from jsonb_array_elements(template.checklist) with ordinality as s(step, n))
```

`with ordinality` plus `order by n` keeps the steps in order. Without it,
`jsonb_agg` order isn't guaranteed.

## A flag the user sets, not a guess: self-care

Capacity (work hours) was eating into routines and workouts. Three ways to tell
"self-care" from work:

| Option | Problem |
|---|---|
| By pillar (physical/spiritual = self-care) | Studying for a theology exam, training for a competition |
| Anything in a routine | A workout isn't in a routine |
| **A flag per task, with good defaults** ✓ | One more field, but nobody has to set it most of the time |

`is_self_care` defaults to true for routine steps and workouts, false otherwise;
events default by kind (social, birthday, wedding → true). The general rule is
**a defaulted flag beats an inferred category**: the default covers 95% of
cases, and the flag handles the rest without exceptions in code.

## Two limits instead of one

Once self-care existed, a day has **two** limits:
1. Work hours: the capacity setting.
2. The **waking day**: from when quiet hours end to when they start. Everything
   counts against this one.

Not counting self-care at all would let a day be overbooked with no warning.
A refusal says which limit it hit (`full: "work" | "day"`). When a single number
hides two different questions, split it.

## All or nothing, or say exactly what didn't happen

Creating a routine wrote the routine, then each step. A refused step left a
half-made routine reported as "created" ([[05-mcp-server]]).

- **Creating:** all or nothing. The first refusal deletes what was written.
  Delete the child rows first: the foreign key is `on delete set null`, so
  deleting the routine first would leave orphan tasks.
- **Editing** can't easily undo, so it reports precisely: `notAdded: [...]`, and
  the steps list excludes them.

## A setting, not a constant, but only when it's personal

These became settings with defaults equal to the old constants: when any-time
must-dos start escalating (15:00), how far ahead timed tasks rise (60 min), where
the week starts (Monday). Each is a value **people genuinely differ on**. Things
that are rules of the app (four nudges at most, a 12-hour forgotten-start limit)
stayed constants. Every setting is UI, validation and a test, and not every
number deserves that.

## Give the database the same rule

Today's ranking (TypeScript) and the morning brief's top three (SQL) are two
implementations of one rule. Each change (priority, "later", the setting) had to
land in both, with a test on each side. When a rule must run in two languages,
make the tests mirror each other, so drift shows up as a failing test rather
than a user noticing that the notification and the screen disagree.
