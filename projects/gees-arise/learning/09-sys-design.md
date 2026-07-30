# System Design — Gees Arise

Beginner → advanced notes on the architecture decisions behind Gees Arise, written as we make them (not after the fact).

---

## 1. "Rule" tables vs "instance" (log) tables

**The beginner problem:** when you model something that repeats (a daily habit, a task due every 2 weeks), it's tempting to put a single `status` column on the task and just flip it back and forth: `PENDING` → `DONE` → back to `PENDING` tomorrow.

This breaks the moment you need history. If "yesterday" and "today" share the same row, marking today done erases the fact that yesterday happened at all. You lose streaks, you lose audit trails, and you can't answer "did they actually do this on July 12th?"

**The fix — split into two tables:**

- A **rule** table (`tasks`) describes the recurrence pattern itself: what it is, how often, how many times per cycle. It does *not* hold "today's" state.
- A **log/instance** table (`task_completions`) gets a brand new row every single time the rule is actually fulfilled. Nothing is overwritten — ever. History is just "all the rows for this task_id."

This is a very general pattern, not specific to habit trackers — it's the same reasoning behind why you don't store "current balance" only, you store a ledger of transactions and derive the balance. Rule vs. log, definition vs. occurrence — same shape, different domains (cron jobs & their run history, subscriptions & their billing events, recipes & times cooked).

## 2. Modeling different recurrence shapes with one log table

Instead of a separate table per task type, we use one `task_completions` table for all of them, distinguished by a `cycle_key` — a string that identifies "which occurrence is this."

| Task type | Example | `cycle_key` | How progress is computed |
|---|---|---|---|
| `DAILY` | "Read 20 mins" | the calendar date, e.g. `'2026-07-27'` | 1 completion per day expected |
| `NEGATIVE` | "Screen time < 3h" | the calendar date | same as DAILY, just an "avoid this" framing |
| `ONE_OFF` | "Submit visa form by Friday" | fixed literal `'ONCE'` | exactly 1 completion, ever |
| `INTERVAL` | "Post 2x every 2 weeks" | a **window index**, e.g. `'0'`, `'1'`, `'2'`... | count completions sharing that index vs `target_count` |

The `INTERVAL` case is the trickiest one, worth slowing down on. We store, on the `tasks` row:

- `window_days` — how long one cycle lasts (14, for "every 2 weeks")
- `window_anchor_at` — a fixed starting timestamp (when the task was created)
- `target_count` — how many completions are needed per window (2, for "2x")

To find which window "right now" belongs to:

```
window_index = floor((now - window_anchor_at) / window_days)
```

Day 0–13 after the anchor → window `0`. Day 14–27 → window `1`. And so on forever, with no need to ever "reset" anything manually — the arithmetic just keeps producing the next index as time passes. Progress bar = `count(completions where cycle_key = current window_index) / target_count`.

**Why this matters beyond this app:** this is the same idea behind rate limiting ("N requests per rolling window"), billing cycles, and sprint/iteration boundaries in project tools — a fixed-length window anchored to a start time, with a formula (not a stored "current window" value you'd have to remember to update) telling you which bucket "now" falls into.

## 3. Optimistic UI + async trust, backed by a state machine

The product idea ("mark done immediately, get audited later") is a UX pattern with a real backing state machine on `task_completions.status`:

```
DONE_PENDING_AUDIT → VERIFIED   (happy path: time runs out, nobody objected)
DONE_PENDING_AUDIT → REJECTED   (>= 2 distinct people flagged it in time)
```

Two design decisions worth noticing:

1. **The audit deadline is computed once, at creation time**, and stored (`audit_deadline_at`), rather than computed on the fly every time someone checks. Storing it means a scheduled job can cheaply ask "which rows have `audit_deadline_at < now()` and are still `DONE_PENDING_AUDIT`?" without recomputing anything.
2. **"Flip to VERIFIED because nothing happened" needs an active trigger.** A database row doesn't change itself when a timestamp passes — something has to come along and update it. That's the scheduled-job note below.

## 4. Why some things need a scheduled job, not just a request handler

Most of an app's logic runs in response to a user action (submit proof → insert a row). But two things in Gees Arise need to happen *because time passed*, with nobody in the app doing anything:

- Auto-verifying a completion once its audit window closes without enough flags.
- Detecting a "silent miss" — an `INTERVAL` window that closed under target, or a `ONE_OFF` deadline that passed with zero submissions — and opening a tribunal penalty for it.

Neither of these has a natural HTTP request to hang off of. This is what cron-style scheduled jobs are for (Supabase's is `pg_cron`, running SQL/functions on a timer, e.g. every 15 minutes) — see `learning/supabase.md` as that gets filled in.

**Implemented 2026-07-27** in `supabase/migrations/00000000000006_scheduled_jobs_and_rejection.sql`. Two `pg_cron` schedules:

- `auto_verify_completions()` — every 15 min, a single `UPDATE ... WHERE status = 'DONE_PENDING_AUDIT' AND audit_deadline_at < now()`. Simple by design: anything that *was* going to be rejected already got moved out of `DONE_PENDING_AUDIT` immediately when the 2nd flag landed (see the `flag_completion` fix below), so this sweep never has to re-check flag counts — it only ever has to ask "has time run out."
- `detect_missed_cycles()` — hourly, a `plpgsql` function looping over every active task and branching per `type`, mirroring `src/app/tasks/cycle.ts`'s logic **in SQL** rather than calling out to it. See `DECISIONS.md` for why this duplication was accepted (Vercel Cron's once-daily Hobby-plan limit would have broken the precise end-of-day deadline this whole design depends on).

**A new idempotency problem this introduced, and how it's solved differently from the flag path:** `detect_missed_cycles()` runs on a recurring timer, so the same missed cycle could get detected and penalized on every single run if nothing stopped it. The fix is a **partial unique index**: `unique (task_id, cycle_key) where cycle_key is not null`, paired with `insert ... on conflict (task_id, cycle_key) where cycle_key is not null do nothing`. The `where` clause has to appear in *both* places — on the index (so Postgres knows this uniqueness rule only applies to miss-triggered penalties, not rejection-triggered ones, which leave `cycle_key` null) and on the `ON CONFLICT` clause (so Postgres knows which partial index to check against). This is a different idempotency mechanism than `flag_completion` needs (see below) — worth noticing *why* they differ: the sweep is re-invoked repeatedly with no memory of its own past runs, so the database itself has to be the thing remembering "already handled"; `flag_completion` only runs once per flag, so a plain status-guard in the `UPDATE ... WHERE status = 'DONE_PENDING_AUDIT'` is enough to stop a 3rd/4th flag from re-triggering.

**The flag→reject transition was a real gap the audit feed shipped without.** The original `flagCompletion` action just inserted a row into `audit_flags` — nothing ever checked whether that was the *2nd* flag and flipped `task_completions.status` to `REJECTED`, and nothing ever opened the tribunal penalty PRD.md §4.3 describes for a rejected proof. Fixed by replacing the plain insert with a `flag_completion(completion_id, reason)` RPC function — same "RLS for visibility, RPC for atomic multi-step action" pattern as `create_circle`/`join_circle` (§7): insert the flag, count flags, and — only if the count just crossed 2 — flip the status and insert the penalty, all as one atomic call. Being `SECURITY DEFINER`, it re-implements the authorization checks (circle membership, can't flag your own proof) explicitly in the function body rather than relying on `audit_flags`'s RLS policy, which is bypassed for this function's own internal writes.

## 5. Preventing abuse at the constraint layer, not just in application code

Two rules that matter for the product ("2 distinct flags to reject", "don't spam a nudge") could be enforced purely in app code — but pushing them into the database schema itself means they hold even if there's a bug in the API layer:

- `UNIQUE(completion_id, flagged_by)` on `audit_flags` — the database physically refuses a second flag row from the same person on the same completion, so "one member flags twice to fake 2 votes" isn't just discouraged, it's impossible.
- `UNIQUE(penalty_id, voter_id)` on `penalty_votes` — same idea for the "majority clears a penalty" vote.
- The nudge cooldown, by contrast, is **not** a hard uniqueness constraint — a time-based cooldown ("only once per 6 hours") isn't expressible as a simple `UNIQUE` (that would mean "only once, ever"). Postgres *can* do time-window exclusion with `EXCLUDE` constraints over range types, but that's genuinely more machinery than an MVP needs — so this one is deliberately left as an application-level check (read the most recent nudge row, compare timestamps, reject if too soon).

**Takeaway:** "can this be a hard constraint, or does it need app logic?" is worth asking for every business rule. Hard constraints are stronger (can't be bypassed by a bug) but only work for rules that don't depend on *when* something happened relative to *now*.

## 6. Row Level Security — and the recursive-policy trap it's easy to fall into

**Why RLS at all, not just "check permissions in the API route":** Supabase auto-generates a REST API (PostgREST) over every table in the `public` schema, reachable with the *publishable* key — which is embedded in every client-side JS bundle, so effectively public. Without RLS, "only circle members can see this circle's data" would only be true because the app's own routes happen to check it — anyone could bypass the app entirely and query the table directly. RLS moves the access rule *into the database itself*, so it holds no matter what calls it — the app, a bug in the app, or someone hitting the API directly.

**The core pattern:** almost every table's policy boils down to "can the current user (`auth.uid()`) see rows belonging to a circle they're a member of?" That check — "is this user a member of circle X?" — is a lookup against `circle_memberships`. Fine for `tasks`, `proofs`, etc. But `circle_memberships` *itself* needs a policy too ("members can see the roster of their own circles") — and that policy's check is *also* "is this user a member of circle X," which means checking `circle_memberships` again... **from inside `circle_memberships`'s own policy.**

That's a real trap, not a hypothetical: Postgres will actually recurse into the same policy check forever and error out. Any self-referencing membership/team table hits this the moment you write the "obvious" policy.

**The fix — a `SECURITY DEFINER` escape hatch, scoped tightly:**
```sql
create schema if not exists private;

create or replace function private.is_circle_member(target_circle_id uuid)
returns boolean
language sql
security definer
set search_path = ''
stable
as $$
  select exists (
    select 1 from public.circle_memberships
    where circle_id = target_circle_id
      and user_id = (select auth.uid())
  );
$$;
```
`SECURITY DEFINER` means the function runs with *its owner's* privileges, not the caller's — so its internal query against `circle_memberships` skips RLS entirely, breaking the recursion. This sounds dangerous (bypassing RLS is exactly what we don't want!) but it's safe here specifically because:
1. It only ever checks the *caller's own* `auth.uid()` — there's no parameter letting you ask "is *someone else* a member of X," so it can't be used to snoop on other users' memberships.
2. It lives in a `private` schema, not `public`. PostgREST (the auto-REST-API layer) only serves schemas explicitly listed in the project's API settings (`public` by default) — so even though the function is technically callable by any authenticated Postgres role, it's *not reachable at all* through the public REST API, only from inside other SQL (like our RLS policies).
3. `set search_path = ''` plus fully-qualifying every table reference (`public.circle_memberships`, not just `circle_memberships`) prevents a specific attack class called *search_path hijacking*, where a malicious role creates a same-named object earlier in the search path to trick a `SECURITY DEFINER` function into operating on the wrong table.

**General lesson, beyond this one function:** `SECURITY DEFINER` is a real foot-gun most of the time (per the security checklist we're following — "never add it to resolve a permission error, it silently removes access control") — but a self-contained boolean check like this, parameterized only by the caller's own identity and kept out of the exposed API surface, is the one well-established exception to "avoid it."

**One more pattern worth naming — no UPDATE policy is sometimes the correct policy.** `task_completions.status` (DONE_PENDING_AUDIT → VERIFIED/REJECTED) and `penalties.status` (PENDING → CLEARED) both change based on computed logic (an audit-window timer, a vote majority) — never a user directly editing a status field. So neither table has a client-facing `UPDATE` policy for those columns at all. The only way those rows change is the scheduled job (§4) using the `service_role` key, which bypasses RLS by design. **Absence of a policy is itself a security decision** — it means "nothing except our own trusted server-side code can touch this," which is stronger than writing a permissive-looking `UPDATE` policy and hoping the app always calls it correctly.

## 7. RLS policies vs. RPC functions — two different tools for two different rules

By this point the schema has three distinct ways of controlling what a user can do, and it's worth being explicit about when each applies:

1. **A plain RLS policy** (§6) — for rules that are just "which existing rows can this user see/touch," expressible as a single `using`/`with check` boolean expression. Most of the schema is this.
2. **A `private`-schema `SECURITY DEFINER` helper** (§6) — for a rule that would otherwise recurse into itself. Not something you call directly; only used *inside* other policies.
3. **A `public`-schema `SECURITY DEFINER` RPC function** — new as of building the circle-creation/joining flow (`create_circle`, `join_circle` in `supabase/migrations/00000000000003_circle_functions.sql`). This is for an *action*, not a *visibility rule* — something that needs to:
   - touch more than one table as a single atomic unit (creating a circle **and** the creator's ADMIN membership row together — if the second insert failed after the first succeeded, you'd get an orphaned adminless circle), or
   - read data the caller isn't normally allowed to read, but only to make a decision the function itself enforces (`join_circle` needs to count `circle_memberships` rows for a circle the joining user *isn't a member of yet* — the ordinary SELECT policy would correctly block that read for anyone else, but the function needs it internally to enforce the `max_members` cap before deciding whether to let them in).

The key difference from the `private` helper: these are deliberately kept in the `public` schema and called directly from the client via `supabase.rpc("create_circle", {...})` — they're meant to be a real, callable API surface, just one where the authorization logic lives in the function body (always keyed off `auth.uid()`, never a caller-supplied user id) instead of in a declarative policy. **Rule of thumb:** if the rule is "can this row be seen/touched," reach for RLS; if the rule is "this whole operation must happen atomically, with business logic in between the reads and the writes," reach for an RPC function.

**Concrete gotcha this caught:** the invite-code join flow needs to answer "is this circle already full?" *before* letting someone in — but per the PRD's guardrail (§2.2, `active_members_count >= max_members`), that check inherently requires reading membership rows for a circle you don't belong to yet. Plain RLS can't express "let me read this table just long enough to decide whether to write to it" — that's exactly the shape of problem `SECURITY DEFINER` RPC functions exist for.

## 8. Private storage + signed URLs, and the audit feed's join-filter

**Storage buckets get RLS too, on a different table.** Supabase Storage isn't a separate system from Postgres — every file is a row in `storage.objects` (columns include `bucket_id` and `name`, the full path), and that table can have RLS policies exactly like any other. The `proofs` bucket is created `public: false`, and the path convention `{circle_id}/{completion_id}/{filename}` is deliberate — it puts the circle_id as the *first path segment* specifically so the policy can extract it with `(storage.foldername(name))[1]` and reuse the same `private.is_circle_member()` helper from §6, without a second lookup table.

**A private bucket means `<img src="...">` can't just point at the file directly.** A private object requires an `Authorization` header to fetch — something a plain `<img>` tag has no way to send. The fix is a **signed URL**: `supabase.storage.from("proofs").createSignedUrl(path, 3600)` generates a temporary (here, 1-hour) unauthenticated URL that's valid specifically because *the server already proved it was allowed to read that file* (RLS checked once, at signing time) — the signature in the URL is what stands in for auth from then on, not a fresh permission check on every image load. This has to happen server-side (in the Server Component rendering the audit feed, `src/app/audit/audit-feed.tsx`), never in the browser, since only the server holds a real authenticated Supabase session at that point.

**First attempt: file uploads straight through a Server Action — worked, until it didn't.** `<input type="file">` inside a `<form action={serverAction}>` genuinely does work — the browser packages the file into `FormData` as a real Web API `File` object, `formData.get("image")` on the server gets that same `File`, and `supabase.storage.from("proofs").upload(path, image, {...})` accepts it directly. Anticipating Next's **1MB-by-default** Server Action body cap (`serverActions.bodySizeLimit`), it was pre-emptively raised to `8mb` in `next.config.ts` — reasonable-looking, but wrong in a way that only showed up on the first real (non-test) photo: `"Body exceeded 8mb limit"` from an actual phone photo.

**The real ceiling wasn't Next's config at all — it was Vercel's platform.** Vercel serverless functions hard-cap the request body at **4.5MB**, and this is enforced by the platform itself — Next.js's `bodySizeLimit` config has no effect on it whatsoever. So even the "fixed" 8MB config would have started failing again in production the moment someone uploaded a 5MB photo, config or no config. **The actual fix wasn't a bigger number — it was routing the file around the Next.js server entirely**: `submit-proof-dialog.tsx` now calls a small `createCompletion()` Server Action (no file, just a task id) to get back a `completionId`, then uploads the image **directly from the browser to Supabase Storage** using the browser client (`@/lib/supabase/client`), then calls a second tiny `attachProof()` Server Action (just the resulting storage path, not the file bytes) to record the proof row. Only the browser and Supabase's storage servers ever see the actual image bytes — Next.js never does. `next.config.ts`'s size-limit override was removed afterward since it was solving the wrong layer of the problem. **Lesson:** a platform-level hard limit (Vercel, here) always wins over an application-level config knob (Next.js's) that merely *looks* like it controls the same thing — worth checking which layer actually owns a limit before trying to raise it.

**A TypeScript gotcha the split surfaced: inferred return types can silently un-discriminate a union.** `createCompletion()` returns either `{ error: string }` or `{ completionId, circleId }` depending on a branch. Without an explicit return-type annotation, TypeScript doesn't infer a clean two-branch union — it infers *one* merged object shape where every field from every branch is present but optional (`{ error?: string; completionId?: string; circleId?: string }`). That broke the calling code's `"error" in result` check: since `error` technically exists as a key on *every* branch (just `undefined` on the success one), the `in` check didn't narrow anything away, and `result.error` stayed typed as `string | undefined` even after the check. The fix was adding an explicit return-type annotation — `Promise<{ error: string } | { completionId: string; circleId: string }>` — which forces TypeScript to keep the two shapes as a real discriminated union instead of merging them. **Lesson:** if a function returns different-shaped objects on different branches and the caller needs to narrow between them, annotate the return type explicitly rather than trusting inference — inference optimizes for "what type describes all the return statements," not for "what union lets a caller discriminate cleanly."

**The audit feed's query needed `!inner` to filter on a joined table.** The feed needs "pending completions, but only for tasks in *this* circle" — circle_id isn't a column on `task_completions` directly, only reachable via its `tasks` relationship. PostgREST (Supabase's auto-REST layer) supports filtering by an embedded/joined resource's column (`.eq("tasks.circle_id", circleId)`), but **only if the embed is written as an inner join** (`tasks!inner(title, circle_id)` in the `.select()`, not just `tasks(title, circle_id)`). Left as a plain embed, the circle filter is silently ignored — you'd get every circle's pending completions, not just your own. `!inner` here means the same thing it does in raw SQL: rows with no matching `tasks` row (shouldn't happen given the FK, but in principle) get excluded rather than returned with `tasks: null`.

**Vouching isn't a database write — its absence *is* the mechanism.** No `vouches` table exists (see §3's original design note). The wireframe shows a "Vouch 👍" button, but per the PRD's actual state machine, nothing needs to happen when you vouch — a proof reaches `VERIFIED` automatically once its audit window closes with fewer than 2 flags. So instead of building a button that writes a row nobody reads, the audit feed just shows the reasoning directly ("no flags yet auto-verifies at end of day") and only wires up `Flag`, which is the one action with real downstream effect. Worth naming as a pattern: **matching the UI to what the data model actually does, rather than building a control just because a mockup shows one**, avoids a feature that *looks* interactive but is secretly inert.

## 9. A permanent error log, and the RLS policy that has to cover *two* different unauthenticated-vs-authenticated cases

Every Server Action returns `{ error: message }` to whoever triggered it, but until now nothing was ever recorded server-side — if the person who hit the error didn't mention it, it was gone the moment the response left the server. `error_logs` (see `DECISIONS.md` for why a plain table instead of Sentry) fixes that: a `logError(context, error, userId)` helper (`src/lib/log-error.ts`) gets called in every action's error branch, right before returning the message to the client.

**The RLS policy here has to handle a case none of the earlier tables did: writes from someone who isn't logged in yet.** Most actions that can fail (creating a task, joining a circle) require a session — but `signUp` and `signIn` can fail *before* any session exists, meaning the connecting Postgres role is `anon`, not `authenticated`, and `auth.uid()` is `null`. A policy written only `to authenticated` would silently refuse to log exactly the errors that happen earliest in the funnel (a failed signup). The fix is one policy granted to **both** roles, with a check that branches on which case it is:
```sql
create policy "Log an error as yourself, or anonymously pre-auth"
on error_logs for insert
to authenticated, anon
with check (
  ((select auth.uid()) is null and user_id is null)
  or user_id = (select auth.uid())
);
```
The `anon` branch requires `user_id` to also be `null` — so an anonymous request can log an error, but can't claim to be logging it on behalf of some other user's id.

**A TypeScript gotcha: Supabase's error classes don't have an index signature, so they fail against any type that declares one.** `logError` was first typed to accept `{ message: string; stack?: string | null; [key: string]: unknown }` — meant to let extra fields (like a Postgrest error's `code`/`details`/`hint`) flow through as metadata. That broke every call site: `AuthError`/`PostgrestError` are real classes with fixed, known properties, and TypeScript's structural typing requires the *source* type to also have a matching index signature before it'll accept it as one — a concrete class without one isn't assignable, even though every actual property lines up fine. The fix was to stop asserting a specific shape at all: accept `error: unknown`, then duck-type the handful of fields actually cared about (`message`, `stack`, `code`, `details`, `hint`) one at a time with `typeof` checks inside the function. **Lesson:** an index-signature type (`{ [key: string]: unknown }`) is a much stronger constraint than it looks — it doesn't just mean "any extra properties are fine," it means "the caller's value must *itself* be typed as having arbitrary properties," which rules out passing real, concrete class instances (errors, most SDK response types) even when they'd satisfy every field structurally.

## 10. A pattern repeats: `cast_penalty_vote` is `flag_completion` shaped exactly the same way

Building the Hall of Shame's majority-vote clearing made the RPC pattern from §7/§9 show up a third time, and by now it's worth naming as a template rather than three separate one-off decisions: **any action that needs to (a) write a row and (b) immediately recompute a tally across rows the caller may not otherwise be allowed to read in full, to decide whether to trigger a second write** — `create_circle`+membership, `flag_completion`+rejection, and now `cast_penalty_vote`+clearing — all resolve to the same shape: a `SECURITY DEFINER` RPC that does the insert, recomputes the count, and conditionally does the second write, all in one atomic call, with authorization re-checked explicitly in the function body since RLS is bypassed for the function's own internal reads. Recognizing "this is that pattern again" is faster than re-deriving the RLS-can't-do-this reasoning from scratch each time.

**One deliberate gap, left as a known simplification:** PRD.md's admin tie-break vote isn't implemented — every vote (including the admin's) counts equally toward a plain majority (`clear_votes > eligible_voters / 2`), and a genuine 50/50 tie among eligible voters (everyone except the offender) just sits unresolved rather than being broken by the admin. Noted in the migration itself rather than silently skipped, so it's a documented gap, not a forgotten one.

## 11. Streak and "today's %" only ever look at DAILY/NEGATIVE tasks, and streak counts from yesterday

Two design choices in `src/app/tasks/streak.ts`, worth being explicit about:

**Only `DAILY`/`NEGATIVE` tasks count.** `INTERVAL` tasks ("2x every 14 days") and `ONE_OFF` deadlines don't have a "due today" concept in the same sense a daily habit does — folding them into a single streak/percentage number would need a much fuzzier definition of "was today a success." Left out entirely for now rather than approximated badly.

**The streak counts consecutive fully-completed days ending *yesterday*, never including today.** Today isn't "closed" yet — someone could still submit proof for every daily task in the next hour. If the streak counted today and today wasn't finished, an unfinished-but-still-in-progress day would look identical to a genuinely broken streak, and the number would flicker down to 0 every morning before anyone's had a chance to do anything. Today's own progress is shown separately, as the "% done today" figure — a live, changeable number — while the streak stays a stable count of *already-decided* days.

## 12. A real bug: a shared layout stayed stale after the data it depends on changed

Reported directly: right after finishing onboarding (creating a circle), the dashboard showed the *pre-circle* chrome — plain header, no sidebar, no colors, no profile menu — even though the dashboard's own content clearly knew a circle existed. A hard reload fixed it, which was the tell: **this wasn't a bug in the layout's logic, it was stale client-side caching.**

`(app)/layout.tsx` and `(app)/dashboard/page.tsx` each independently query for circle membership. The layout had already rendered once *for the onboarding page*, at a point where no circle existed yet, with `circle = null`. When `createCircle`'s Server Action ran `redirect("/dashboard")` afterward, Next.js's client-side **Router Cache** (distinct from the server-side data cache) reused that already-rendered layout output for the shared layout segment, rather than re-fetching it — because nothing told the router that data feeding *that specific layout* had changed. The dashboard *page* re-rendered correctly (new navigation, new page segment), but the *layout wrapping it* didn't, since layouts persist across sibling-route navigations by design — that's the whole point of a shared layout, normally a good thing, but it means "silently stale" is the failure mode when the layout's own data changes out from under it.

**The fix:** `revalidatePath("/", "layout")` in both `createCircle` and `joinCircle`, before the `redirect`. The second argument, `"layout"`, is the important part — a bare `revalidatePath("/dashboard")` would only have invalidated the dashboard *page* segment (which didn't need it, it was already correct), not the shared `(app)` layout actually holding the stale data. **Lesson:** when a Server Action changes data that a *layout* (not just the page you're navigating to) depends on, the layout needs its own explicit revalidation — reaching the right page isn't enough if the shell around it was cached from before the data changed.

## 13. Proofs redesigned: an optional image plus EITHER a link or a note, never both

The original `proofs` schema modeled one `proof_type` enum (`IMAGE`/`URL`/`TEXT`) with a single `content_url` value — pick exactly one kind of proof. Changed (2026-07-27) to three nullable columns instead: `image_url`, `link_url`, `text_note`, with two `check` constraints doing the actual rule enforcement at the database layer:

```sql
alter table proofs add constraint proofs_not_both_link_and_text
  check (link_url is null or text_note is null);

alter table proofs add constraint proofs_has_some_content
  check (image_url is not null or link_url is not null or text_note is not null);
```

Same reasoning as the `UNIQUE` constraints from §5 (`audit_flags`, `penalty_votes`) — this is a rule that could be enforced purely in the Server Action, and *is* (the same two checks are mirrored in `attachProof` so the error message reads clearly instead of a raw Postgres constraint violation) — but the database-level constraint means the rule holds even if a future code path forgets to check it. **A photo can now genuinely stand alone, or be paired with either a link or a short note — just never a link and a note together**, matching how the feature was actually asked for.

## 14. Day-of-week scheduling — a new dimension bolted onto DAILY/NEGATIVE, not a new task type

"Every Monday" or "every 2 weeks on Friday" *sounds* like it needs a new task type, but it's really just a **refinement of what DAILY/NEGATIVE already do** — the underlying mechanic (one `task_completions` row per occurrence, keyed by calendar date) doesn't change at all; what changes is *which* calendar dates actually expect one. Two new nullable-with-safe-defaults columns: `days_of_week smallint[]` (which weekdays, `0`=Sunday..`6`=Saturday) and `week_interval int default 1` (skip N-1 weeks between occurrences). `NULL`/`1` respectively means exactly the old behavior — every existing task is unaffected.

**Reused `window_anchor_at` rather than adding a second anchor column.** `window_anchor_at` already existed (previously only read by `INTERVAL` tasks, for their window-index math). "Every 2 weeks on Friday" needs its own reference point too — *which* Fridays count as "on" weeks vs. skipped ones — and rather than introduce a parallel anchor field with the same job, `isTaskDueOn()` (`src/app/tasks/cycle.ts`) just reuses the one that's already there: `weeksSinceAnchor = floor((date - window_anchor_at) / 7 days)`, then `weeksSinceAnchor % week_interval === 0` decides on/off weeks. One column, two independent uses (window-count math for `INTERVAL`, week-parity math for `DAILY`/`NEGATIVE`) — worth noticing when an existing field can be reused as a reference point instead of adding a near-duplicate one.

**This single new helper (`isTaskDueOn`) had to be threaded through every place that previously assumed "DAILY/NEGATIVE = due every day":**
- `streak.ts`'s `computeTodayPercent`/`computeStreak` — previously took plain task **ids**; now take full task objects (needing `days_of_week`/`week_interval`/`window_anchor_at`), and filter to only the tasks actually due on each date being considered *before* computing percentages/streaks. Getting this wrong would have meant a Monday-only task tanking your streak on every Tuesday–Sunday, since "not done" and "not due" look identical unless something explicitly distinguishes them.
- The dashboard's task list — a due-but-not-yet-submitted task still shows "Submit Proof"; a **not-due-today** task shows a plain "Not due today" line instead, so the button doesn't sit there implying something's expected when it isn't.
- `detect_missed_cycles` (SQL) — mirrors `isTaskDueOn`'s logic a second time in `plpgsql` (same duplication tradeoff as §4's original port, same reason: the sweep runs inside Postgres, not the Next.js app). Getting *this* side wrong would have been worse than a UI inconsistency — it would have opened tribunal penalties for days a task was never actually due.

**Lesson worth generalizing:** adding a new *filter* on top of an existing recurrence concept ("every day" → "every day, but only some of them") isn't free just because the storage/audit mechanics don't change — every place that previously iterated "all applicable tasks" without checking due-ness needs to learn the new check, or it'll silently do the wrong thing on exactly the tasks the new feature was built for.

## 15. Task deletion can't be allowed to double as evidence-tampering

Real gap caught directly: nothing originally stopped marking a task done and then deleting the task entirely — on an app whose entire premise is peer-audited accountability, that's not a UX rough edge, it's a way to dodge both verification *and* a rejection's tribunal penalty. Fixed in `deleteTask` (`src/app/tasks/actions.ts`): before soft-deleting, it checks whether a `task_completions` row exists for the **current** cycle (any status — pending, verified, *or* rejected all count, since hiding any of them defeats the audit) and refuses if so. A completion from a **previous** cycle doesn't block it — the restriction is specifically "not while it's live," not "never again."

**The other half, explicitly requested alongside the restriction:** being able to genuinely undo a *mistaken* submission — not to dodge accountability, but because people fat-finger the wrong task or want to redo a proof. `undoCompletion` allows exactly one narrow case: retract a completion **only while it's `DONE_PENDING_AUDIT`** (nobody's weighed in yet) — once `VERIFIED` (permanently locked, §3) or `REJECTED` (already triggered a penalty), it can't be undone, enforced both in the action and via a matching RLS `DELETE` policy (`00000000000011_undo_completion.sql`) so the restriction holds even if a bug ever bypassed the app-level check. Undoing also cleans up the uploaded image from Storage first (best-effort — a cleanup failure is logged but doesn't block the undo itself), so retracting a mistaken photo doesn't leave it orphaned in the bucket.

**Why these two rules don't conflict:** delete blocks on *any* current-cycle completion; undo only works on a *pending* one. So the actual flow for "I want to delete a task I already marked done today" is: undo the completion first (only possible while still pending), *then* delete — which is exactly the right shape, since undoing first means there's nothing left to have been "evidence" of in the first place.

## 16. A real, reported bug: `detect_missed_cycles` never checked whether a task existed yet

Reported directly: seeing a self-penalty in Hall of Shame for a task that was, in fact, correctly submitted today (showing "Auditing" — genuinely fine). The bug: `detect_missed_cycles` (§4) checks "did yesterday have a completion?" for every active `DAILY`/`NEGATIVE` task — but nothing ever checked whether the task **existed** yesterday. Create a task today, and the very next hourly sweep dutifully checks it against yesterday, finds zero completions (impossible to have any — the task didn't exist), and opens a penalty for a day before the task was ever created.

**Fixed with one guard clause** — `if t.created_at::date > missed_date then continue; end if;` — skipping the whole check for any task that didn't exist yet on the date being examined. Also cleaned up the existing false-positive rows a targeted `delete ... using` (matching on `cycle_key` looking like a date *and* `created_at` being after that date, so it can't accidentally touch a legitimate miss or an `INTERVAL`/rejection-triggered penalty).

**Why `INTERVAL` and `ONE_OFF` were never at risk of the same bug, worth understanding rather than just patching everything defensively:** `INTERVAL`'s window index is computed from `window_anchor_at`, which *is* the task's creation moment — `prev_window_index >= 0` already can't go negative relative to when the task started existing. `ONE_OFF`'s deadline is inherently set at or after creation (nobody creates a task with a deadline already in the past). Only `DAILY`/`NEGATIVE`'s "check yesterday, unconditionally, for every active task" had no notion of *when* the rule started applying — worth noticing that the other two types were "accidentally correct" by virtue of their anchor already being creation-relative, not because anyone had reasoned it through at the time.

**The general lesson, worth carrying into any future scheduled sweep:** a query that walks "every active X and checks some point in the recent past" has an implicit assumption baked in — that X existed throughout that past. That assumption is almost always true for old rows and silently false for brand-new ones, which is exactly why it's easy to miss in testing (you'd have to test with a task that's simultaneously *brand new* and *old enough for the sweep to have already run once*) and easy to hit in real use (create a task, come back in an hour, sweep's already run).


## 17. Proactive excuses — reusing the penalty/vote mechanic instead of building a parallel one

The ask: let someone log a reason for a task they can't get to *before* the cycle ends, not just get caught after the fact by `detect_missed_cycles`. The temptation is a whole new `excuses` table with its own status machine and its own review-deadline logic — but everything an excuse needs already exists on `penalties`.

**`submit_excuse` (`00000000000015_excuse_penalties.sql`) just inserts a `penalties` row with `penalty_type = 'EXCUSE'`, status `PENDING`, the reason as `description`.** That's it — no new table. It reuses `cast_penalty_vote`'s existing majority-clear mechanic verbatim: a `CLEAR` vote from a majority of the circle (minus the offender) clears it, same as any miss penalty.

**Two things fall out of that reuse for free, worth noticing:**
1. `penalties_task_cycle_unique (task_id, cycle_key) where cycle_key is not null` (§4/§6) already guarantees one penalty per task-per-cycle slot. So once an excuse claims a cycle's slot, `detect_missed_cycles`'s own `on conflict ... do nothing` silently no-ops instead of opening a *second*, redundant miss penalty for the same missed cycle later that day. Zero changes needed to `detect_missed_cycles` itself.
2. There's deliberately **no expiry / review-deadline column**. An `EXCUSE` penalty just sits `PENDING` forever until voted `CLEAR`, exactly like a plain miss penalty. This was a real design fork: a cycle-bound deadline (e.g. "must be reviewed within 24h") sounds more disciplined, but it would mean a solo user's excuse *always* lapses before any second circle member could possibly exist to vote on it — permanently unclearable by construction, not just by circumstance. No expiry means the same "eligible_voters computed fresh from current membership, not snapshotted at creation" property already established for miss-penalty backlogs (§ — solo-circle voting gap) applies to excuses too: whenever a real gee eventually joins, they immediately become an eligible voter on every backlogged `PENDING` excuse, no matter how long the solo period was.

**Net effect matches the stated rule exactly:** solo + proof submitted → auto-verifies, passes (nobody exists to flag it). Solo + excuse submitted, or nothing submitted at all → sits `PENDING` (`eligible_voters = 0`, unclearable) → reads as a fail. Once gees exist, they can vote on the whole backlog — including excuses filed while nobody was around — at any point after joining, not just going forward.

`getTaskStatus` (`src/app/tasks/status.ts`) gained a third state check (`EXCUSED`, checked before the due/not-due branch) fed by a same-cycle `PENDING`/`EXCUSE` lookup against `penalties` — same "thread the new distinction through every place that assumed only two outcomes" lesson as §14's day-of-week work.

## 18. Admin tie-break — why "majority" alone can mathematically never resolve a 50/50 split

`cast_penalty_vote` (§7/§17) clears a penalty when `clear_votes > eligible_voters / 2` — a **strict** inequality. That single detail means an exact 50/50 split can never clear through this check alone, no matter how long you wait: if `eligible_voters = 4` and `clear_votes = 2`, `2 > 2` is false forever. This was flagged as a known gap the moment the majority mechanic was first written, and stayed open until now.

**The fix isn't "count the admin's vote as worth more"** — it's a second, narrower check that only fires once the first one has already failed *and* the situation is provably a genuine deadlock, not just an incomplete vote: every eligible voter has actually cast a vote (`clear_votes + keep_votes = eligible_voters`), and it's exactly even (`clear_votes = keep_votes`). Checking `eligible_voters > 0 and clear_votes = keep_votes` **without** also requiring full participation would have been wrong — e.g. 2 CLEAR votes in out of 5 eligible, with 3 people simply not having voted *yet*, isn't a deadlock at all; the next voter could still tip it either way. Triggering the tie-break there would let the admin jump the queue before everyone's had a chance to weigh in, which defeats the whole point of a majority vote.

**Once it's a genuine deadlock, the resolution reuses the admin's own already-cast vote** rather than adding a separate "override" action — `exists (... cm.role = 'ADMIN' and pv.vote = 'CLEAR')` checks whether any admin among the voters said `CLEAR`; if so, that's enough to break the tie in favor of clearing. No attempt to handle multiple disagreeing admins specially (picks up any `CLEAR`, doesn't care about a second admin's `KEEP`) — not asked for, and rare enough (one admin per circle in practice) not to be worth the extra complexity. If the admin is the offender themselves — ineligible to vote on their own penalty at all, per the very first check in this function — there's no admin vote to look at, and the tie just stays unresolved, exactly as it did before this fix. That's a known, accepted gap, not a regression: PRD's own phrasing ("the Admin Gee's vote, *or an explicit override*") already hints a second mechanism might eventually be needed for that case — not built here since nothing has asked for it yet.

**Correction, added later:** this whole section was written describing the fix as already shipped, under migration number `00000000000017` — but that migration file was never actually created; only this design writeup survived. `cast_penalty_vote` kept doing plain majority voting with no tie-break for two more sessions until the gap was noticed (twice) and finally implemented for real in `00000000000027_admin_tiebreak_vote.sql`. The design above turned out to be correct and needed no changes — it just hadn't been built. Worth remembering: a learning-file entry describing a fix is not proof the fix shipped — cross-check against the actual migration file existing on disk, especially for anything written in a session that might have ended before verification.

## 19. `.limit(1).maybeSingle()` with no `ORDER BY` is a silent multi-row trap

A real bug caught *before* it ever happened, not after: nothing stopped a user from ending up in two `circle_memberships` rows at once — `create_circle` had no check at all, and `join_circle` only blocked re-joining the *same* circle, not a different one. That alone sounds survivable ("so they're in two circles, so what") until you notice every single page that answers "which circle is this user in" — dashboard, Hall of Shame, Gees, circle-settings, profile, history, the roster, onboarding, eight files in total — does it the same way:

```ts
const { data: membership } = await supabase
  .from("circle_memberships")
  .select("circle_id")
  .eq("user_id", userId)
  .limit(1)
  .maybeSingle();
```

**`.limit(1)` with no `.order()` before it doesn't mean "the first one you joined."** Postgres makes no ordering guarantee at all for a query without `ORDER BY` — which row comes back first is an implementation detail of the query planner, not a contract. With exactly one membership row this is invisible (there's only one possible answer), which is exactly why it's easy to ship this pattern everywhere and never notice — it only becomes a real, user-visible bug the moment a second row exists, and at that point it wouldn't even be *consistently* wrong (same wrong circle every time) — different pages, or even the same page on a reload, could show different circles.

**The fix wasn't "add `ORDER BY joined_at` to eight queries."** That would have papered over the symptom while leaving the actual premise — a user can be in more than one circle — silently true. The real fix closes it at the source: `create_circle`/`join_circle` (00000000000018) now refuse to create a second membership row at all, so the eight call sites' unstated assumption ("there's exactly one") goes back to being actually true, instead of usually true.

**General lesson:** `.limit(1)` (or `.single()`/`.maybeSingle()`) is a claim that the query can only ever match one row — worth treating that as an assertion to verify (is there a unique constraint, or app-level invariant, that actually guarantees it?), not just a convenient way to unwrap an array. If the invariant isn't enforced somewhere, `.limit(1)` doesn't create false precision — it just picks an arbitrary one of however many rows actually exist, silently.

## 20. `getTaskStatus`'s "Auditing" label has zero fallback logic of its own — it's a pure mirror of a DB column that only a cron job ever changes

Reported bug: a task still showed "Auditing" a full day after its review deadline had clearly passed. The instinct is to look at `src/app/tasks/status.ts` or the deadline math in `cycle.ts` — but neither is where the transition actually happens. `getTaskStatus` just maps `task_completions.status === 'DONE_PENDING_AUDIT'` straight to `"AUDITING"`; it never itself compares `audit_deadline_at` to `now`. The comparison lives entirely in Postgres, in `private.auto_verify_completions()` (`00000000000006_scheduled_jobs_and_rejection.sql`), run every 15 minutes by pg_cron:

```sql
update public.task_completions
set status = 'VERIFIED'
where status = 'DONE_PENDING_AUDIT' and audit_deadline_at < now();
```

**Why this matters for debugging:** if that cron job isn't actually registered/active on the live Supabase project (e.g. the migration's `create extension if not exists pg_cron;` + `cron.schedule(...)` calls were never applied, or failed silently), a completion can sit `DONE_PENDING_AUDIT` forever — no amount of real time passing fixes it, because nothing in the request path ever re-checks the deadline. A one-day-stale "Auditing" status is way past one 15-minute tick, which is what actually points at "the cron job itself, not the deadline math" as the thing to check first. Diagnosis has to happen in the database, not the app — `select * from cron.job;` and `select * from cron.job_run_details order by start_time desc limit 20;` in the Supabase SQL editor tell you whether the job exists, is active, and is actually succeeding on each run.

**General pattern:** any status that's supposed to change "once some time has passed" but isn't recomputed on every read (i.e., lives in a column, not a live computation) has an implicit dependency on *something* actually sweeping it — a cron job, a webhook, a queue worker. When that something goes silent, the bug looks like "the app's date logic is wrong," but the app never had any date logic to begin with; the fix (or at least the diagnosis) is entirely on the scheduler side.

**This time, though, the cron job checked out fine** — `select * from cron.job_run_details` showed `auto-verify-completions` succeeding every 15 minutes, and `select ... from task_completions where task_id = ...` showed the actual stuck-looking row's `audit_deadline_at` (`2026-07-28 23:59:00+00`) genuinely hadn't passed `now()` (`2026-07-28 09:28:58+00`) yet — 14 hours still to go. So it wasn't stuck at all; it just looked that way. **The real cause was a timezone label problem, not a scheduler problem:** `circle-settings-form.tsx` asks for "Daily reset time (**UTC**)," but for a circle whose members are all in a UTC+1 timezone (Nigeria/WAT), entering `23:59` there — the natural "end of my day" value — actually sets the cutoff to 12:59 AM *local* time, not 11:59 PM. Right around local midnight, this makes a task look stuck on "Auditing" a day past when the user expects, even though the row is behaving exactly per its (correctly UTC) deadline. Fix was a config change the admin can make themselves (set reset time to `22:59` UTC to get an 11:59 PM WAT cutoff), not a code fix — but it's the same underlying gap noted in `DECISIONS.md`'s circle-settings history: there's no actual per-circle timezone concept, just a raw UTC time-of-day field labeled honestly but easy to misread as "my local end of day." **Lesson: before assuming a stuck-looking scheduled state is a scheduler bug, check the actual stored deadline against the actual DB clock first** — it's a much cheaper query than auditing the cron job, and it's the only way to catch "the value's right, the reader's timezone assumption is wrong" instead of chasing a nonexistent scheduler failure.

## 21. A migration existing in the repo doesn't mean it's live — the Audit feed bug that "correct code + correct RLS" analysis couldn't catch

A different feed — the dashboard's "Audit the Gees" tab — was reported empty even though a specific member's tasks were visibly stuck in "Auditing" on their own profile page. Read `audit-feed.tsx`'s query line by line, re-checked every RLS policy on `task_completions`, `tasks`, `proofs`, and `audit_flags` — all of it read as correct. No bug findable by reading code and migrations alone.

**The actual cause only showed up once the swallowed `error` (see §20's neighbor entry — the fix that added `logError` to this same file) got checked against `error_logs`:** `column proofs_1.image_url does not exist`. The live database's `proofs` table still had the *original* `proof_type`/`content_url` columns — `00000000000009_proof_shape.sql`, which renames those into `image_url`/`link_url`/`text_note`, exists in `supabase/migrations/` but had never actually been run against the live project. The query, the RLS, the TypeScript — all of it was written against a schema that only existed in the migration files, not in the actual database being queried.

**This is the second time in one session this exact class of gap showed up** — `00000000000017_admin_tiebreak_vote.sql` doesn't even exist on disk despite being referenced elsewhere as shipped (a different failure mode: never *written*, vs. this one: written but never *applied*). Both point at the same root issue: **migrations here are applied by hand, copy-pasted into the Supabase SQL editor, with no `supabase link` + `supabase db push` and no tracked migration history table.** Nothing enforces "every file in `supabase/migrations/` has actually run against production" — the repo and the live database can silently diverge, and a schema mismatch like this produces a runtime error that reads exactly like an app bug (empty feed, no obvious cause) rather than what it actually is (a deployment gap).

**Lesson:** when code and RLS both check out but a feature still doesn't work, don't assume the live schema matches the migration files — check `information_schema.columns` (or `pg_proc` for functions) against what the latest migrations expect, especially for any feature that hasn't been visibly working since its migration was written. This is exactly the kind of thing that would be caught automatically by adopting `supabase db push` with tracked migration history instead of manual SQL-editor copy-paste — worth prioritizing if these silent-drift bugs keep recurring.

**Addendum, same session, third occurrence:** after migration 9 got applied live, a *different* page (the member profile page) started showing every task as "Not started" instead of "Auditing" — same underlying cause, different query. `profile/[userId]/page.tsx`'s own `task_completions` query had picked up a `proofs(...)` embed (to show proof previews) and later a `completion_vouches(...)` embed (for the vouch feature, migration 21) — and that query had never had error-checking added to it, unlike `audit-feed.tsx` which got the `logError` fix earlier. A missing `completion_vouches` table (if migration 21 hadn't been run yet) would produce the exact same silent-failure shape: query errors, `completions` comes back `null`, every task falls back to its no-completion-found status. **Once you've found and fixed this bug shape once in a session, actively check every other query that got a new embed added in the same session** — the fix (add `error` destructuring + `logError`) is cheap and should be applied proactively to any query whose result silently drives UI branching, not just the one that happened to get reported first.

## 22. A second foreign key to the same table breaks every existing bare embed of it — PostgREST-wide, not just the new query

Adding circle tags (§ DECISIONS.md 2026-07-28) meant giving `circle_memberships` a `peer_tag_set_by` column referencing `users(id)` — a second FK into `users`, alongside the pre-existing `user_id`. The Gees page immediately started showing "The Gees (0/7)" with zero members, even though the members obviously still existed. `error_logs` had the real cause the moment it was checked: `PGRST201 — Could not embed because more than one relationship was found for 'circle_memberships' and 'users'`.

**What actually broke, and why some queries survived:** any query doing a bare `users(...)` embed on `circle_memberships` — no relationship specified — is only unambiguous as long as exactly one FK path exists between the two tables. The moment a second one exists, PostgREST can no longer guess which one you meant, and every such query starts failing, immediately, with no code change of its own. Three call sites (`gees/page.tsx`, `gees-roster.tsx`, `circle-settings/page.tsx`) used the bare form and broke. Three others (`layout.tsx`, `nudges/actions.ts`, the profile page's own membership query) had already been written as `users:user_id(...)` and kept working — not because that syntax is documented as the disambiguation mechanism, but because it happened to. Don't rely on that: PostgREST's own error told us the actual supported fix directly in its `hint` field — `users!circle_memberships_user_id_fkey(...)`, naming the constraint explicitly. Standardized every call site on that form rather than leaving the `:user_id` ones as "already working, don't touch."

**General lesson:** adding a new foreign key to a table is a breaking change to *every other query in the codebase* that embeds that table without a hint — not just the feature you're building. Before adding a second (or third) FK from table A to table B, grep for `.from("A")` across the whole app and check every `.select(...)` for a bare `B(...)` embed; each one just became ambiguous whether or not you touch its file. Same category of lesson as §19 (`.limit(1)` with no `ORDER BY`): a pattern that was safe under one specific, unstated assumption (here: "only one FK path exists") breaks silently the moment that assumption stops holding, with no compiler or type system able to catch it — only grep, or the runtime error itself, will.

## 23. A trigger lets one feature react to another feature's writes without either one knowing the other exists

Circle Stakes needed a new rule: "if a member gets a penalty while their circle has a live stake, they forfeit their share." The tempting place to put that check is inside `flag_completion` and `detect_missed_cycles` — the two existing places that already insert into `penalties`. That would work, but it means every current and *future* place that ever inserts a `penalties` row (there are already three: `flag_completion`, `detect_missed_cycles`, `submit_excuse`) has to remember to also carry the stakes-forfeit logic — miss updating one, and stakes silently stop working for that one path.

**The alternative used here:** an `AFTER INSERT ON penalties` trigger (`private.forfeit_active_stake`, `00000000000030_circle_stakes.sql`). It doesn't live inside any of the three penalty-creating functions at all — it fires automatically whenever a row lands in `penalties`, regardless of which function put it there, including ones written after this trigger existed. This is the same shape as `private.prevent_duplicate_completions` (§ DECISIONS.md 2026-07-28, migration 23): a `BEFORE INSERT` trigger enforcing a rule that would otherwise need to be duplicated inside every insert path.

**When to reach for a trigger instead of putting the check inside the writer:** when the rule is "whenever X happens, also do Y" and Y is conceptually a *different feature* from whatever's causing X. `penalties` doesn't need to know Stakes exists, and Stakes doesn't need to hook into three separate call sites — the trigger is the one place that knows both. The tradeoff: trigger logic is less discoverable than a plain function call — reading `flag_completion` top to bottom won't tell you a stake forfeiture might also happen; you have to know to check for triggers on the table. Worth a comment at the point of insert (or in the trigger itself) pointing this out, since `\d penalties` in `psql` (or Supabase's table editor) is the only way to rediscover it later otherwise.

**The other new pattern in the same migration:** `circle_stakes_one_active`, a **partial unique index** (`unique index ... where status = 'ACTIVE'`) instead of a plain `unique` column constraint. A plain unique constraint on `circle_id` would mean a circle could never have *any* second stake, ever, even after the first one settles. `where status = 'ACTIVE'` scopes the uniqueness to only the rows that currently matter — Postgres only enforces uniqueness among rows matching the `where` clause, so any number of `SETTLED` stakes can coexist for the same circle, but only one `ACTIVE` one at a time. `penalties_task_cycle_unique` (§2, migration 6) uses the same trick for a different reason (`where cycle_key is not null`, to exclude rejection-triggered penalties which don't use `cycle_key` at all) — same tool, two different motivations: there it's "only some rows have a meaningful key to dedupe on," here it's "only some rows represent a currently-live state."

## 24. Fanning out one row per member from a single authoring action — and keeping a late joiner in sync

Circle Goals needed "one member starts a goal, every member gets their own task for it." The RPC (`create_circle_goal`) does this with a plain `insert into tasks (...) select ... from circle_memberships cm where cm.circle_id = ...` — a single `INSERT ... SELECT`, not a loop inserting one row at a time. This is the same shape as `open_stake`'s stake-entry enrollment (§ DECISIONS.md 2026-07-30): whenever "create N related rows, one per current member" comes up, `insert into child_table (...) select ..., cm.user_id, ... from circle_memberships cm where cm.circle_id = X` does it as one atomic statement instead of a `plpgsql` loop — simpler, and there's no per-row failure mode to handle since it's a single INSERT.

**The harder part wasn't creation, it was staying in sync afterward.** A goal fanned out at creation time only reaches members who existed *then* — anyone who joins the circle later would never get a task for it unless something else creates one. Rather than adding a "sync goals" step somewhere in the join flow as an afterthought, the fan-out logic was duplicated directly into `join_circle` itself (the same `insert into tasks (...) select ...` shape, this time `from circle_goals cg where cg.circle_id = target_circle.id and cg.is_active`, `select`ing the *new* member's `auth.uid()` as the constant instead of pulling multiple member ids). **General lesson: whenever an action fans out a per-member side effect at creation time, ask "what happens when a new member arrives after that"** — the answer is usually "they need the exact same fan-out, run from the other direction" (goal → all current members, vs. new member → all current goals), not a background job or a one-time catch-up script. Same underlying question as `DECISIONS.md`'s explicit callout that Stakes didn't get this treatment: enrolling late joiners into an *already-created* goal is cheap and safe (worst case, an instantly-overdue `ONE_OFF` task); enrolling them into an *already-active money stake* is a real product decision (are they on the hook for an amount they never agreed to?), not just a symmetry fix — worth pausing on which side of that line a given fan-out feature sits on before wiring the join-time half up automatically.
