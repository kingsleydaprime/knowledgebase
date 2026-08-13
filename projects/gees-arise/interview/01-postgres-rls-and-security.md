# Gees Arise — Postgres, RLS & Security

From [`../learning/09-sys-design.md`](../learning/09-sys-design.md) and
[`04-supabase.md`](../learning/04-supabase.md). The best database-security material in the vault.

---

### Q1. [Intermediate] 🔥🔥 Why use RLS at all instead of checking permissions in your API routes?

**Strong answer covers:** Supabase auto-generates a REST API (PostgREST) over every table in the
`public` schema, reachable with the **publishable key — which is embedded in every client-side JS
bundle**, so it's effectively public. Without RLS, "only circle members can see this circle's data"
would be true only because the app's own routes happen to check it. Anyone can skip the app entirely
and query the table directly.

**The framing that lands:** RLS moves the access rule *into the database*, so it holds no matter what
calls it — the app, a bug in the app, or someone hitting the REST API with curl. Route-level checks
protect one code path; a policy protects the data.

---

### Q2. [Advanced] 🔥🔥 You write the obvious policy on your memberships table and Postgres errors out. What happened?

**This is the single best question in the project. Know it cold.**

**Strong answer covers:** nearly every table's policy reduces to "can the current user see rows
belonging to a circle they're a member of?" — a lookup against `circle_memberships`. That's fine for
`tasks`, `proofs`, and everything else. But `circle_memberships` itself needs a policy ("members can
see the roster of their own circles"), and *that* policy's check is also "is this user a member of
circle X" — which queries `circle_memberships`, **from inside `circle_memberships`'s own policy**.

Postgres recurses into the same policy check and errors out. Any self-referencing membership or team
table hits this the moment you write the natural policy.

**The fix — a tightly scoped `SECURITY DEFINER` helper:**
```sql
create schema if not exists private;

create or replace function private.is_circle_member(target_circle_id uuid)
returns boolean language sql security definer set search_path = '' stable as $$
  select exists (
    select 1 from public.circle_memberships
    where circle_id = target_circle_id and user_id = (select auth.uid())
  );
$$;
```
`SECURITY DEFINER` runs the function with its **owner's** privileges, so its internal query skips RLS
and the recursion breaks.

**Why it's safe here — three reasons, and you must give all three:**
1. It only ever checks the **caller's own** `auth.uid()`. There's no parameter for "is *someone else*
   a member of X", so it can't be used to enumerate other users' memberships.
2. It lives in a **`private` schema**, and PostgREST only serves schemas listed in the API settings
   (`public` by default) — so it isn't reachable through the REST API at all, only from inside other
   SQL.
3. `set search_path = ''` plus fully-qualified table references (`public.circle_memberships`)
   prevents **search_path hijacking**, where a malicious role creates a same-named object earlier in
   the search path to trick a `SECURITY DEFINER` function into operating on the wrong table.

**The honest framing to end on:** `SECURITY DEFINER` is a foot-gun and the standard advice is never
to add it to resolve a permission error, because it silently removes access control. A self-contained
boolean parameterised only by the caller's own identity and kept out of the exposed API surface is
the one well-established exception.

---

### Q3. [Advanced] 🔥 When do you use an RLS policy, and when do you use an RPC function?

**Strong answer covers three tools with a clear rule for each:**

1. **A plain RLS policy** — for "which existing rows can this user see or touch," expressible as a
   single `using`/`with check` boolean. Most of the schema.
2. **A `private`-schema `SECURITY DEFINER` helper** — for a rule that would otherwise recurse into
   itself. Never called directly; only used *inside* policies.
3. **A `public`-schema `SECURITY DEFINER` RPC** (`create_circle`, `join_circle`), called from the
   client via `supabase.rpc(...)` — for an **action** rather than a visibility rule, when it needs
   to either touch multiple tables atomically or read data the caller can't normally read in order
   to make a decision the function itself enforces.

**The rule of thumb to state:** if the rule is "can this row be seen or touched," reach for RLS. If
it's "this whole operation must happen atomically with business logic between the reads and the
writes," reach for an RPC.

**The two concrete motivating cases:**
- `create_circle` inserts the circle **and** the creator's ADMIN membership together — if the second
  insert failed after the first, you'd have an orphaned adminless circle.
- `join_circle` must check `active_members_count >= max_members` for a circle the joining user isn't
  a member of *yet*. The ordinary SELECT policy correctly blocks that read for everyone else, but
  the function needs it internally. **Plain RLS cannot express "let me read this table just long
  enough to decide whether to write to it"** — that's exactly the shape `SECURITY DEFINER` RPCs
  exist for.

**Non-negotiable detail:** authorization inside an RPC always keys off `auth.uid()`, never a
caller-supplied user id.

---

### Q4. [Advanced] 🔥 "No UPDATE policy is sometimes the correct policy." Explain.

**Strong answer covers:** `task_completions.status` (DONE_PENDING_AUDIT → VERIFIED/REJECTED) and
`penalties.status` (PENDING → CLEARED) change based on **computed logic** — an audit-window timer, a
vote majority — never a user directly editing a status field. So neither table has a client-facing
UPDATE policy for those columns at all. The only thing that changes them is the scheduled job using
the `service_role` key, which bypasses RLS by design.

**The point to land:** the **absence** of a policy is itself a security decision. It means "nothing
except trusted server-side code can touch this," which is strictly stronger than writing a
permissive-looking UPDATE policy and hoping the app always calls it correctly.

---

### Q5. [Intermediate] 🔥 There are two Supabase clients in this codebase. What's the difference and why does it matter?

**Strong answer covers:** the **anon/publishable** client carries the user's session and is subject
to RLS — it's what the browser and user-facing server code use, and its key is public by design. The
**service-role** client bypasses RLS entirely and must exist only in trusted server-side code
(scheduled jobs, admin operations). Leaking the service-role key to the browser defeats every policy
in the database simultaneously.

**The concrete case from the project:** deleting a user for real requires the service-role client —
cascades handle the relational rows, but **Storage objects needed it too**, because the files live in
`storage.objects` and the deleting session doesn't necessarily have policy access to another user's
paths. Knowing that Storage is subject to the same rules, and therefore the same escape hatch, is the
detail that shows real familiarity.

---

### Q6. [Advanced] 🔥 How do you secure a private storage bucket, and how does the file path help?

**Strong answer covers:** Supabase Storage isn't a separate system — every file is a **row in
`storage.objects`** (with `bucket_id` and `name` columns), and that table takes RLS policies like any
other. The `proofs` bucket is created `public: false`.

**The path convention is a design decision:** `{circle_id}/{completion_id}/{filename}` puts
`circle_id` as the **first path segment** specifically so the policy can extract it with
`(storage.foldername(name))[1]` and reuse the same `private.is_circle_member()` helper — no second
lookup table, no join. Encoding the authorization key into the path is the trick worth naming.

---

### Q7. [Advanced] 🔥 A private bucket means `<img src="...">` can't fetch the file. How do you display proof images?

**Strong answer covers:** a private object requires an `Authorization` header, which a plain `<img>`
tag has no way to send. The fix is a **signed URL** —
`supabase.storage.from("proofs").createSignedUrl(path, 3600)` — a temporary unauthenticated URL
that's valid because **the server already proved it was allowed to read that file**: RLS is checked
once, at signing time, and the signature stands in for auth from then on. There is no fresh
permission check on each image load.

**The placement rule:** this must happen **server-side** (in the Server Component rendering the audit
feed), never in the browser, because only the server holds a properly authenticated session at that
point. And the expiry is a real security parameter — a signed URL is a bearer token, so an hour is a
deliberate choice, not a default to ignore.

---

### Q8. [Advanced] 🔥 Your audit feed showed *every* circle's pending completions instead of just yours. Why?

**Strong answer covers:** `circle_id` isn't a column on `task_completions` — it's only reachable via
the `tasks` relationship. PostgREST *can* filter on an embedded resource's column
(`.eq("tasks.circle_id", circleId)`), but **only if the embed is written as an inner join**:
`tasks!inner(title, circle_id)` in the `.select()`. Written as a plain embed, **the filter is
silently ignored** — no error, just every circle's rows.

**Why this is a great answer:** the failure is silent and permissive, i.e. it's a data-leak-shaped
bug produced by a syntax detail. `!inner` means exactly what it means in SQL: rows with no matching
`tasks` row are excluded rather than returned with `tasks: null`.

---

### Q9. [Intermediate] Your error log table needed a policy covering both unauthenticated and authenticated writers. Why is that awkward?

**Strong answer covers:** errors happen **before** login too — a failure on the sign-in page has no
`auth.uid()`. So the insert policy has to permit the anonymous role as well as the authenticated one,
while reads stay restricted (an error log holds stack traces and user identifiers). That's two
distinct cases in one table's policy set, and getting it wrong means either losing exactly the errors
you most need (pre-auth failures) or exposing a log of everyone's failures.

**Why it earned its place:** the error log is what surfaced the PostgREST embed-ambiguity failure
immediately when a query started returning nothing — a permanent, queryable error record turned an
invisible bug into a one-line diagnosis.

---

### Q10. [Intermediate] How do you enforce the circle size cap so it can't be bypassed?

**Strong answer covers:** at the **constraint layer**, not in application code. Application-level
checks are bypassable by anyone hitting the REST API directly, and racy even when they aren't — two
simultaneous joins can both read "9 of 10" and both insert. The cap is enforced inside `join_circle`,
which is `SECURITY DEFINER` and therefore the only path that can perform the join at all (there's no
client-facing INSERT policy on `circle_memberships` to race against).

**The generalisable rule from the notes:** prevent abuse at the constraint layer, not just in
application code — a rule you can only express in TypeScript is a rule that only applies to people
using your TypeScript.

---

### Q11. [Intermediate] What's the difference between a GRANT and an RLS policy?

**Strong answer covers:** a **GRANT** decides whether a role may touch a table at all; an **RLS
policy** decides which rows it may see or change once it can. They're independent gates — and
`service_role` bypasses RLS but still needs the GRANT. Worth knowing because a `42501 permission
denied` on Supabase is usually a GRANT problem, not a policy problem, and the error's `hint` field
says so directly.

---

### Q12. [Advanced] Someone gets your publishable key and starts hitting the REST API directly. What can they do?

**Strong answer covers:** exactly what an anonymous or authenticated user of the app can do, and
nothing more — which is the whole point of putting the rules in the database. Concretely: they can
read rows their policies allow, insert where an INSERT policy permits, and can't touch the
status columns at all because there are no UPDATE policies for them. They can't enumerate other
circles' memberships because `private.is_circle_member` takes no arbitrary user id and isn't exposed
through the API.

**The honest caveats to volunteer:** they can hammer the API (rate limiting is a separate concern),
and any RPC in the `public` schema is a callable endpoint whose entire authorization story is its
function body — so an RPC that trusted a caller-supplied user id would be a complete
authentication bypass. That's why the "always key off `auth.uid()`" rule is non-negotiable rather
than stylistic.
