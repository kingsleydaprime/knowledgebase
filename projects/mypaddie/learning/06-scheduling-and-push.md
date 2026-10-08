# 06 — Scheduling and push: the database decides, the app delivers

*MyPaddie (written up 2026-10-08). Files: `supabase/migrations/*` (`private.send_nudges`,
`collect_nudges`, `apply_holds`, `pause_for_events`), `src/app/api/push/route.ts`,
`src/features/push/{copy,bundle}.ts`, `supabase/tests/push.test.sql`.*
See also: [[05-mcp-server]] · [[07-time]] · [[01-supabase-schema-and-rls]] · [[03-testing]]

## Why the database runs the clock

Reminders have to go out when the app is **closed**: at 09:50 for a 10:00 task,
at 15:00 to escalate a must-do, and when a meeting starts. Something has to wake
up on its own. MyPaddie uses **`pg_cron`** inside Supabase Postgres:

```sql
select cron.schedule('mypaddie-nudges', '* * * * *', 'select private.send_nudges()');
```

Every minute, one SQL function runs. It started as `*/10` (every 10 minutes);
reminders like "in 10 minutes" forced every minute.

Why the database and not a Vercel cron or a worker?
- The data is already there. Deciding "who needs what now" is a set of joins.
- One transaction: record "sent" and decide, together.
- No extra service to keep alive.

## The pipeline

```
pg_cron (every minute)
  └─ private.send_nudges()
       ├─ prune_dead_subscriptions()        devices that stopped accepting pushes
       ├─ spawn_today()                     today's rows for recurring tasks
       ├─ pause_for_events()                an event starting pauses the running task (runs even if push isn't set up)
       ├─ if push isn't configured → stop
       ├─ collect_nudges() || collect_application_nudges() || … || paused     ← each returns a jsonb array
       ├─ apply_holds(payload, now())      drop what a status ("in class") holds back
       └─ net.http_post(url, { nudges }, x-push-secret)   → /api/push
                                                            ├─ checks the secret (constant-time)
                                                            ├─ words each nudge (copy.ts)
                                                            ├─ bundles a pile into one (bundle.ts)
                                                            └─ web-push → the phone
```

Two halves, deliberately split:
- **The database decides** *what* is due and *for whom*. All the rules live in
  SQL: escalation ladders, quiet hours, each person's own settings.
- **The app route has no database access at all.** It gets a list of decided
  nudges, writes the words, and sends them. Its only secret is the shared
  header. If it's compromised it can't read anyone's data. Wording lives in
  TypeScript, where it's easy to test (`copy.test.ts`).

Secrets (the push URL and the shared secret) live in **Supabase Vault**
(`vault.decrypted_secrets`), not in SQL files. Locally they're not set, so
`send_nudges` returns early. That's why the pgTAP tests call the `collect_*`
functions directly with a fixed `p_now`.

## Sending once: unique indexes as the memory

A job that runs every minute will see "the 10-minute reminder is due" ten times.
Each send is **recorded** in `private.nudges`, and partial unique indexes make a
duplicate impossible:

```sql
create unique index nudges_task_kind_level_day on private.nudges (task_id, kind, level, day) where task_id is not null;
create unique index nudges_event_level_occurrence on private.nudges (event_id, level, occurs_on) where event_id is not null;
```

The collector inserts with `on conflict do nothing … returning`, and **only what
was actually inserted gets sent**. That's idempotency enforced by the database,
not by careful code. The `level` column is the rung of a ladder: evening before
(1), morning of (2), 30 minutes (3), 10 minutes (4), and so on. Adding a rung
(important events: 10 minutes = 5, at the start = 6) needs no schema change.

## Rules that read each person's settings

Everyone's schedule is one jsonb row in `public.settings`. SQL reads a field with
a default, so a person who never set it gets the old behaviour:

```sql
private.setting_time(st.value, 'anyTimeNudgeFrom', '15:00')
private.setting_int(st.value, 'showTimedWithin', 60)
coalesce(st.value->>'weekStart', 'monday')
```

Turning a constant into a setting is therefore three changes:
1. The zod schema and default in `schedule.ts`.
2. The settings form and Paddie's `update_settings`.
3. One `setting_*` read in SQL.

There's no migration of data. The default *is* the old constant.

## Holds: statuses that quiet the phone

"In class", "sleeping" and "deep work" hold everything; "with friends" lets
reminders and events through. `apply_holds` drops held nudges from the payload
**and deletes their records from this run** (`sent_at = now`), so they're
retried after the hold ends instead of being lost.

### The bug that rule caused, and the lesson

The event auto-pause records a marker ("already paused for this meeting", level
7) in the same `private.nudges` table, so that a task the user deliberately
resumes during the meeting isn't paused again. It was recorded with
`sent_at = p_now`, like a message. On a full hold, `apply_holds` deleted it as
"held, retry later". A minute later the pause ran again and paused the task the
user had just resumed.

```sql
-- the fix: a marker is not a message, so don't stamp it as this run's message
select …, p_now - interval '1 millisecond' from starting
```

**Lesson:** when one table does two jobs ("messages sent" and "things that
happened"), any clean-up written for one job will hit the other. The pgTAP test
reproduces it (deep-work status, meeting starts, resume, next minute), and it was
checked **red on the old code, green on the fix** before trusting it. A test you
haven't seen fail might not be testing anything.

## Doing things, not just saying them: `pause_for_events`

The job doesn't only send messages. When a timed event's start passes,
`pause_for_events` updates the user's running task, banking its minutes into
`spent_minutes` and clearing `started_at`, exactly as `pause_task` does. It
returns a push ("Paused: Essay — Supervisor call has started").

It runs **before** the "is push configured?" check, because the pause must happen
even when notifications don't. The update and the marker are one statement
(chained CTEs: `insert … returning` feeds the `update … from`), so they can't
half-happen.

## Changing a big SQL function safely

`collect_nudges` is about 150 lines, and every rule change means a new migration
that **re-creates the whole function** (`create or replace`). Copying it by hand
risks losing an earlier change. That almost happened: two later migrations had
already redefined `spawn_occurrence`, and copying from an older one would have
silently dropped a column. The routine:

1. Find the **latest** definition: `grep -ln "function private.collect_nudges" supabase/migrations/*.sql | sort | tail -1`.
2. Extract it, change only the lines you mean to, and write the migration (`awk` + `sed`; see [[04-shell]]).
3. `diff` the old function against the new one, so the only differences are
   your change.
4. Apply locally, run pgTAP.

## Testing time-based SQL

Every collector takes `p_now timestamptz default now()`. Tests walk one fake day:

```sql
select is((select count(*)::int from pg_temp.mine('2026-10-06 14:55+01') n where n->>'kind' = 'nudge'),
  0, 'an any-time must-do doesn''t escalate before 15:00');
select is((select n->>'level' from pg_temp.mine('2026-10-06 15:05+01') n where n->>'kind' = 'nudge'),
  '1', 'from 15:00 it escalates');
```

- `pg_temp.mine()` filters to the test's own devices, because on a real database
  other users' nudges come back too.
- Assert on **one kind** when other kinds can legitimately fire at the same
  moment. A "no nudge at 14:55" test first failed because the task's normal
  morning-of reminder fired. That was correct behaviour, so the test was what
  needed fixing.
- Tests in one file share state through the day: insert what a test needs, and
  close or delete it afterwards so later assertions aren't affected.
