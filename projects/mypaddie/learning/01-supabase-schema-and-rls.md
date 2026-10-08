# 01 — Supabase schema and row-level security

*MyPaddie, Day 1 (2026-10-05). File: `supabase/migrations/…_core_schema.sql`.*
See also: [[02-rules-engine-design]] · [[03-testing]] · [[databases/sql-reference]] · [[backend/05-auth/02-authorization]]

## The problem RLS solves

The phone app talks to Postgres almost directly, through Supabase's Data API.
That means *the database itself* has to decide who sees which rows — there's no
backend in the middle to filter. Row-level security (RLS) is a filter Postgres
adds to every query: "only rows where this condition is true exist for you".

```sql
alter table public.items enable row level security;

create policy "owner can read" on public.items
  for select to authenticated
  using ((select auth.uid()) = user_id);
```

Read it as: *for SELECTs, by signed-in users, only show rows whose `user_id` is
the caller.* Three details, each one a real trap:

| Detail | Why |
|---|---|
| `to authenticated` | Without it the policy also runs for `anon` (logged-out visitors). Name the role every time. |
| `(select auth.uid())` not `auth.uid()` | Wrapped in a `select`, Postgres computes it **once per query** instead of once per row. Same answer, much faster on big tables. |
| One policy per operation | `for all` hides which operation each rule was meant for. Four small policies are easier to audit than one clever one. |

### UPDATE needs both `using` and `with check`

```sql
create policy "owner can update" on public.items
  for update to authenticated
  using ((select auth.uid()) = user_id)        -- which rows you may touch
  with check ((select auth.uid()) = user_id);  -- what the row may look like afterwards
```

Without `with check`, you could update your own row and set `user_id` to someone
else's id — handing them a row (or planting one in their account).

### `user_id default auth.uid()`

The client never sends `user_id`. Postgres fills it from the signed-in user's
token. One less thing a client can get wrong or lie about.

## The hole plain RLS leaves: foreign keys

Scenario: the intruder somehow learns the id of Kingsley's "Rhapsody" item. They
insert a task of their own pointing at it:

```sql
insert into tasks (item_id, title) values ('<kingsley's item id>', 'sneaky');
```

The task row is the intruder's own, so RLS lets it in. And **foreign-key checks
ignore RLS** — Postgres just checks the item id exists. Now the intruder's task is
linked to Kingsley's item.

**Fix: a composite foreign key** that includes the owner:

```sql
-- on items:
unique (id, user_id)
-- on tasks:
foreign key (item_id, user_id) references public.items (id, user_id)
```

Now the pair (item id, *intruder's* user id) has to exist in `items`. It doesn't,
so the insert fails with `23503` (foreign key violation). The pgTAP test proves it.

`on delete set null (item_id)` — the column list (Postgres 15+) means "only null
out `item_id`", because nulling `user_id` too would break `not null`.

## Rules that span several rows: deferred constraint triggers

"A task's pillar weights sum to 100" can't be a `check` constraint — a `check`
only sees one row. It needs a trigger that sums all the task's rows.

But if it ran after *every* insert, you could never build up a split:

```
insert physical 50  → sum is 50  → ✗ rejected
```

So the trigger is **deferred**: it waits until `COMMIT`, then checks.

```sql
create constraint trigger task_pillars_sum_to_100
  after insert or update or delete on public.task_pillars
  deferrable initially deferred
  for each row execute function private.check_task_weights();
```

```
begin;
insert physical 50;   -- no check yet
insert mental 30;     -- no check yet
insert emotional 20;  -- no check yet
commit;               -- now: sum = 100 ✓
```

## A ledger with a derived total

`xp_log` is the source of truth: every gain and deduction, forever. `pillars.xp`
is just a running total of it, kept up to date by a trigger. Two rules make that
safe:

1. **The ledger is append-only.** Clients get `select, insert` grants only — no
   `update`, no `delete`. History can't be rewritten.
2. **The total is read-only to clients.** Only the trigger writes `pillars.xp`, so
   it can never drift from the ledger.

The trigger is `security definer` (runs with the owner's rights) because clients
can't write `pillars` themselves. That's normally a red flag, so it's done
carefully: it lives in a `private` schema the API doesn't expose, it only runs as
a trigger, and it only touches `new.user_id` — a value RLS already checked.

### Idempotency with a partial unique index

A phone on bad signal retries "complete task". Without protection, you'd earn the
XP twice.

```sql
create unique index xp_log_once_per_task_reason
  on public.xp_log (task_id, pillar, reason) where task_id is not null;
```

The second insert hits the unique index and fails with `23505`. "Partial" (the
`where`) because rows without a task (e.g. logging a transaction) can repeat.

**There's a name for this: idempotency.** It means doing something twice has the
same effect as doing it once. I'm bringing it up because every "award", "charge"
or "send" action in a system that can retry needs it.

## The 2026 grants change (verify-against-docs moment)

Supabase changelog, 2026-04-28: *"New tables in the public schema will no longer
be exposed to the Supabase Data API by default"* — enforced for all projects from
**2026-10-30**. RLS decides *which rows*; grants decide *whether the table is
reachable at all*. So the migration is explicit:

```sql
revoke all on public.items from anon, authenticated;
grant select, insert, update, delete on public.items to authenticated;
```

`anon` gets nothing. Found by reading the changelog before writing SQL, not from
memory — a tutorial from 2025 would have missed it.

## Interview questions this answers

- *Why isn't RLS enough to stop cross-tenant foreign keys?* — FK checks bypass RLS; use composite FKs.
- *How do you enforce a rule across multiple rows?* — deferred constraint trigger.
- *How do you keep a running total consistent with a history table?* — append-only ledger + trigger-maintained, client-read-only total.
- *How do you make an "award points" endpoint safe to retry?* — unique constraint on the natural key of the award.

## Day 2: OAuth without a secret key

Claude needs to call MyPaddie on your behalf. The usual shortcut is giving the
server Supabase's `service_role` key — which **bypasses RLS on every table**. One
leak and everything is readable.

Instead, Supabase Auth acts as an **OAuth 2.1 server**:

```
Claude ──► /api/mcp            401 + "metadata is at /.well-known/…"
Claude ──► /.well-known/…      "tokens come from https://<ref>.supabase.co/auth/v1"
Claude ──► Supabase Auth       → redirects you to /oauth/consent
You    ──► log in, click Allow  → Supabase redirects back to Claude with a code
Claude ──► Supabase Auth       code + PKCE verifier → access token (a normal user JWT)
Claude ──► /api/mcp            Authorization: Bearer <token>
Server ──► Postgres            same token → RLS sees auth.uid() = you
```

**PKCE** (say "pixie"): the client invents a random secret, sends only its hash
at the start, and reveals the secret when trading the code for a token. Someone
who steals the code from the redirect can't use it without the secret.

Why it's safer: the server holds nothing worth stealing. Each token is one user,
short-lived, and still filtered by RLS.

## Day 2: idempotency patterns in SQL

```sql
-- One row per habit per day, however many requests race:
add constraint one_occurrence_per_day unique (series_id, occurs_on);
insert … on conflict (series_id, occurs_on) do nothing returning id;

-- No conflict target → skip ANY unique violation, including partial indexes:
insert into xp_log … on conflict do nothing;

-- "Mark done" only if not done yet — the WHERE is the guard:
update tasks set status = 'done' where id = $1 and status in ('pending','skipped');
if not found then … -- someone (maybe our own retry) got there first
```

Two concurrent `complete_task` calls: the first `update` locks the row; the second
waits, then re-checks `status in (…)`, finds `done`, updates nothing, and pays
nothing. No application-level locking needed.

## Undo in an append-only ledger: reverse, don't delete (2026-10-07)

The XP ledger (`xp_log`) is insert-only for clients, a trigger adds each row
to a running total, and a partial unique index stops a task paying twice:

```sql
create unique index xp_log_once_per_task_reason
  on public.xp_log (task_id, pillar, reason) where task_id is not null;
```

Undo has to take XP back without breaking any of those. Deleting rows would
break the total (the trigger only fires on insert) and erase history. The
accounting answer is a **reversing entry**:

1. Insert a negative row per pillar (`reason = 'undo'`). The insert trigger
   subtracts it, so totals are right with no update trigger needed.
2. Mark the originals `reversed_at = now()` (the undo rows too).
3. Make the "pay once" index ignore reversed rows, so really doing the task
   later pays again:

```sql
create unique index xp_log_once_per_task_reason
  on public.xp_log (task_id, pillar, reason)
  where task_id is not null and reversed_at is null;
```

Allowing that one edit without opening the table up:

```sql
grant update (reversed_at) on public.xp_log to authenticated;   -- column-level grant
create policy "owner can mark reversed" on public.xp_log for update to authenticated
  using      (auth.uid() = user_id and reversed_at is null)       -- rows you may touch
  with check (auth.uid() = user_id and reversed_at is not null);  -- what they must look like after
```

`using` filters which rows the update can see; `with check` validates the
row *after* the change. Together they make the mark one-way: an attempt to
set it back to null finds no rows (`using` hides already-reversed ones).

## Deferring work by forgetting it: one transaction, one now() (2026-10-07)

The push job (`private.send_nudges`, every minute via pg_cron) runs several
collectors. Each one picks what's due, **records** it in `private.nudges`
(the record is what stops it being sent twice), and returns the payload.

A new rule said that some users must not be pushed right now (asleep, in
class), but the push shouldn't be lost either. Editing five collectors to
understand "holds" would have been a big, risky change. The fix leans on a
Postgres guarantee instead:

> `now()` returns the start time of the **current transaction**. It's the same
> value no matter how many times you call it, or how long the transaction runs.

Each collector writes `sent_at = p_now`, where `p_now` defaults to `now()`.
They all run inside one call to `send_nudges`, so every record from this run
has exactly the same `sent_at`. That makes this run's records easy to pick out
and undo:

```sql
delete from private.nudges n
using private.holds(now()) h
where n.user_id = h.user_id and n.sent_at = now();   -- this run's records, for held users
```

With the record gone, the next minute's run finds the nudge due again, and it
keeps doing so until the hold lifts. Then it goes out. The collectors never
knew holds existed.

`clock_timestamp()` is the one that keeps moving within a transaction. Using
it here would break the trick.
