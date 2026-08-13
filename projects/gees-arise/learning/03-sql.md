# SQL — Gees Arise

Not Supabase-the-platform (that's `supabase.md`) — this is plain SQL/Postgres
query mechanics, taught through the actual queries run against this
project's database, in the order we ran them.

---

## 1. The basic shape: SELECT ... FROM ... WHERE

Every query we ran is a variation on one skeleton:

```sql
select <columns>
from <table>
where <condition>
order by <column> [asc|desc]
limit <n>;
```

Read it in this order, not top-to-bottom: **FROM first** (which table), **WHERE next** (which rows), **SELECT last** (which columns of those rows) — even though you *type* `select` first, Postgres conceptually builds the result that way. Then `order by`/`limit` trim and arrange whatever WHERE left you with.

Our very first diagnostic query:

```sql
select jobid, jobname, schedule, active from cron.job;
```

`cron.job` here is a **schema-qualified table name** — `cron` is the schema (a namespace, like a folder), `job` is the table inside it. `pg_cron` (the extension powering your scheduled tasks) creates its own tables in its own `cron` schema rather than dumping them into `public` alongside your app's tables — this is exactly why the migration files write `public.task_completions` explicitly instead of just `task_completions`: being explicit about the schema is the norm here, not an app-specific quirk.

---

## 2. JOIN — combining rows from two tables that share a key

The second cron query needed something `cron.job_run_details` doesn't have on its own — a human-readable job name (it only stores `jobid`, a number):

```sql
select j.jobname, r.status, r.start_time, r.return_message
from cron.job_run_details r
join cron.job j on j.jobid = r.jobid
order by r.start_time desc
limit 20;
```

**What's happening:** `cron.job_run_details` (aliased `r`) has a row per cron *run*; `cron.job` (aliased `j`) has a row per cron *job definition*. They're linked by `jobid` — every run row says which job it belongs to, by number. `join ... on j.jobid = r.jobid` tells Postgres: "for every run row, go find the one job row whose `jobid` matches, and stitch their columns together into one wide row." Without the join, you'd only ever see `jobid = 3` in the run log — meaningless without cross-referencing the job table by hand.

**Aliases (`r`, `j`)** are just short local nicknames for a table, scoped to that one query — they let you write `r.status` instead of `cron.job_run_details.status` everywhere, and they're *required* once two tables in the same query might have a column with the same name (both tables here have a `jobid` column, so `jobid` alone would be ambiguous — Postgres wouldn't know which table's `jobid` you meant).

The task_completions diagnostic query used the exact same pattern, three tables deep:

```sql
select tc.id, tc.status, tc.created_at, tc.audit_deadline_at, tc.cycle_key,
       t.title, c.reset_time_utc, now() as db_now
from task_completions tc
join tasks t on t.id = tc.task_id
join circles c on c.id = t.circle_id
where tc.task_id in ('bb85331e-...', '68b13211-...')
order by tc.created_at desc
limit 10;
```

Same idea, chained: `task_completions` → `tasks` (via `task_id`) → `circles` (via `circle_id`). Each `join` only needs to know how to link to a table *already in the query* — the third join (`circles`) links to `t` (tasks), not back to `tc`, because that's where `circle_id` actually lives.

---

## 3. WHERE conditions: `=`, `in (...)`, `ilike`, and why one attempt returned nothing

`where tc.task_id in ('bb85...', '68b1...')` — `in (...)` is shorthand for "equals any of these" (equivalent to `task_id = 'bb85...' or task_id = '68b1...'`, just shorter and clearer once you have more than one or two values).

Earlier, this exact-match attempt returned **zero rows**:

```sql
where t.title in ('post my progress on both x and linkedin', 'acctualy follow the roadmap')
```

even though those tasks definitely existed. The reason: the real stored titles had a **trailing space** (`'post my progress on both x and linkedin '`) that wasn't visible in the app's UI (browsers collapse trailing whitespace visually) but very much mattered to `=`/`in`, which compare strings byte-for-byte — `'roadmap'` and `'roadmap '` are simply different strings as far as SQL is concerned, no matter how similar they look.

The fix was switching to a **fuzzy** match to find the real rows first:

```sql
where title ilike '%roadmap%' or title ilike '%progress on both%'
```

`ilike` is "case-insensitive LIKE" — pattern matching instead of exact equality. `%` is a wildcard meaning "anything (including nothing) can go here," so `'%roadmap%'` matches any string that merely *contains* "roadmap" anywhere in it, trailing spaces and all. **General lesson:** reach for `ilike '%...%'` when you're searching for something a human typed and might not match byte-for-byte (titles, names, free text); reach for `=` / `in (...)` when you have an exact, machine-generated value like a UUID `id` that you copied from a previous query's output — which is exactly the pattern used across these queries: `ilike` to *find* the task, then the exact `id` from that result to *query* it precisely afterward.

---

## 4. Aggregations and computed columns you'll see a lot in this schema

- `now()` — a function call, not a column; returns the database's current timestamp at the moment the query runs. Aliasing it (`now() as db_now`) puts it in the result set as its own column, which is exactly how we visually compared a stored deadline against "the actual current time" in the same row, instead of trusting our own guess about what time it was.
- `count(*)` — appears throughout the migration functions (`detect_missed_cycles`, `cast_penalty_vote`) to tally rows matching a condition, e.g. counting how many `CLEAR` votes a penalty has so far.

---

## To fill in as we go

- `group by` / `having` (not hit yet in our diagnostics, but `count(*)` almost always pairs with one eventually)
- Subqueries (`exists (select 1 from ... where ...)`) — already all over the migration functions (`flag_completion`, `leave_circle`), worth a dedicated pass once we're reading those functions together rather than running ad-hoc diagnostics
- `insert ... on conflict ... do update/nothing` — the "upsert" pattern already used in `cast_penalty_vote` and `detect_missed_cycles`

---

## The general version of this
- [[databases/sql-reference|SQL reference]] · [[databases/database-design-reference|Database design]]
- [[databases/interview/01-sql-modelling-and-internals|Databases interview]] — indexes, isolation levels, query plans

↑ [[projects/README|All projects and the domains they exercise]]
