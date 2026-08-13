# Supabase — Gees Arise

Notes on Supabase concepts as we actually use them in this project. Starts as a skeleton — filled in progressively as each concept comes up in the build.

---

## 1. Two different Supabase clients, and why

Next.js's App Router renders in two very different places — the server (Server Components, Route Handlers) and the browser (Client Components) — and each needs its own way of reading the logged-in user's session, because sessions live in cookies and only the server can reliably read *and write* cookies during a request.

We set up three files for this (`@supabase/ssr` package, not the plain `@supabase/supabase-js` client alone):

- `src/lib/supabase/client.ts` — `createBrowserClient(...)`. Used inside Client Components (`"use client"` files). Reads the session cookie the normal browser way.
- `src/lib/supabase/server.ts` — `createServerClient(...)`, reading cookies via Next's `cookies()` API. Used inside Server Components and Route Handlers. Notably: a Server Component is **read-only** for cookies (it can see them but can't set new ones), so its `setAll` is wrapped in a `try/catch` that just no-ops if writing fails — that's expected, not a bug, because of point 2 below.
- `src/proxy.ts` — runs on *every* request before it reaches a page. This is the one place that's allowed to actually rewrite the session cookie if Supabase decides it needs refreshing (e.g. the access token expired but the refresh token is still valid). Without this, a Server Component reading a stale/expired cookie would silently see the user as logged out.

**Mental model:** the proxy keeps the cookie fresh on the way in; the server client reads whatever the proxy left; the browser client is a completely separate, independent read of the same cookie from JS running in the user's browser.

**Naming gotcha, specific to this project's Next.js version (16.2.12):** almost every Supabase+Next.js tutorial you'll find online calls this file `middleware.ts` with an exported `middleware` function — that was correct through Next 15, but **Next 16 renamed the convention to `proxy.ts` / `export function proxy(...)`**, specifically to stop people confusing it with Express.js-style middleware (this "runs before every route" file was never a request pipeline you chain handlers onto — it's one function, more like a network proxy sitting in front of the app). The old `middleware.ts` name still technically works but is deprecated; Next even ships a codemod (`npx @next/codemod@canary middleware-to-proxy .`) to auto-rename it. If a tutorial's code doesn't run, check whether it's written for pre-16 Next.js before assuming your code is wrong. See `learning/frontend.md` for more Next 16-specific gotchas.

**Follow-up (still 2026-07-27) — a habit worth building: when a doc detail could go either way, check the live docs instead of trusting memory/tutorials.** You asked whether Supabase's own docs use `middleware.ts`/a `utils/` folder instead of what we built, guessing the docs might be "descriptive, not authoritative" if they disagreed. Fetching the *current* live Supabase docs (not relying on training data, which skews older) settled it directly: current docs already say `lib/supabase` (framed as "or wherever fits your project," not mandatory) and already say "Proxy," not `middleware.ts` — so what we'd built already matched. The lesson isn't "the docs happened to agree with us" — it's that checking beats guessing either way, and would have caught it immediately if they'd disagreed instead.

## 1b. Two more things that changed recently, caught the same way

**API keys were renamed — `anon` → "publishable key", `service_role` → "secret key".** This isn't just a label change: new-format keys look like `sb_publishable_...` / `sb_secret_...` (not the old long JWT string), and Supabase now issues the new format by default on the API Keys settings page. Old and new keys *coexist* — an older project's legacy `anon`/`service_role` keys keep working unless you explicitly disable them in Settings — but if you copy a fresh key from the dashboard today, you'll get the new format. This bit us directly: `.env.local` got `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (the value actually in the dashboard now), but `client.ts`/`server.ts`/`proxy.ts` were still written to read `NEXT_PUBLIC_SUPABASE_ANON_KEY` — a variable that simply didn't exist, so the app would have silently failed to create a Supabase client at runtime. Fixed by renaming the env var references to match. **Lesson:** an env var typo/mismatch like this doesn't show up in `tsc --noEmit` (TypeScript has no way to know what's *in* your `.env.local`) — it only surfaces at runtime, so it's worth actually eyeballing your `.env.local` against what the code reads, not just assuming they match because you wrote both.

**`getClaims()` is now preferred over `getUser()` specifically inside `proxy.ts`.** Both ask "is this request's session valid," but:
- `getUser()` makes a real network call to Supabase's Auth server every time it's invoked — authoritative (catches a banned/deleted user immediately) but slower.
- `getClaims()` verifies the session JWT's signature *locally*, no network round-trip — much faster, and Supabase's current guidance is to use it for exactly this "runs on every single request" scenario (a Proxy file), reserving `getUser()` for places that specifically need a guaranteed-fresh user record.

Swapped `proxy.ts` from `getUser()` to `getClaims()` for this reason — worth remembering as "use `getClaims()` by default to check identity; reach for `getUser()` only when you specifically need live server-side confirmation."

## 2. What Supabase actually is

Managed Postgres + Auth + Storage + Realtime + Edge Functions, bundled behind one API — instead of standing up your own Postgres instance, writing your own JWT auth system, and configuring your own S3-compatible storage bucket separately, Supabase gives you all of it pre-wired, with a dashboard on top. The trade-off vs. rolling your own backend: less flexibility/control, much less setup time — right trade for a project this size.

## 3. Deleting a user for real — cascades, the service-role client, and why Storage needed it too

Building "delete account" surfaced three separate Supabase concepts at once.

**`public.users` has no foreign key to `auth.users` at all.** It's a completely separate table, populated by a trigger (`handle_new_user()`, fires `after insert on auth.users`) — not linked by an `on delete cascade` FK the way you might assume. That matters a lot for deletion: deleting the `auth.users` row (Supabase's actual login identity) does **nothing** to `public.users` or anything hanging off it. The only way to clean up the app-data side is an explicit `delete from public.users where id = ...` — which then *does* cascade, because every other table (`tasks`, `task_completions`, `proofs`, `circle_memberships`, etc.) already has `references users(id) on delete cascade`. One deliberate delete, many free cascades — but only because that first delete has to be triggered on purpose.

**Deleting an `auth.users` row can't be done in plain SQL/RPC at all — it needs the Admin API.** There's no `delete from auth.users` you can run as a SECURITY DEFINER function; `auth.users` is managed by Supabase's Auth service, and the only sanctioned way to remove an identity is `supabase.auth.admin.deleteUser(userId)` — a method that only exists on a client built with the **service-role key** (renamed "secret key," see §1b), never the anon/publishable key. This is why `src/lib/supabase/admin.ts` exists as its own file: a client using `SUPABASE_SECRET_KEY`, built once, used only from trusted server-side code (Server Actions), never sent to the browser. Service-role bypasses RLS *entirely* — every table, every bucket — so it's the "break glass" client, reached for only when a task genuinely can't be done any other way (deleting another auth identity, or in this case, also deleting Storage objects a normal user's own RLS policies don't allow — the `proofs` bucket has no delete policy for anyone, not even the file's own uploader).

**Order matters when tearing down a user.** Storage paths (`proofs.image_url`, `users.avatar_url`) have to be read out *before* calling the cascade-delete, since the DB rows that point to them won't exist to query afterward — there's no "trash" to recover them from once cascaded. So the actual sequence is: read the file paths → run the DB cascade (`delete_own_account` RPC) → clean up Storage (admin client) → delete the `auth.users` row (admin client) → sign out. Doing it in the opposite order (delete storage/auth first) risks leaving DB rows referencing files that no longer exist, or an authenticated session with no `public.users` row behind it.

## To cover as we build

- [x] Auth (email/password): sign up / log in / log out via Server Actions in `src/app/(auth)/actions.ts`, session cookie handled by `proxy.ts` (§1). Route protection also lives in `proxy.ts`: unauthenticated → redirected to `/login`; authenticated visiting `/login` or `/signup` → redirected to `/`.
  - **Found while testing (2026-07-27):** Supabase's *built-in* email service (used to send the signup confirmation email) has a low default rate limit — two signup attempts in a row while testing hit "email rate limit exceeded." Fine for now, but before real users sign up, this needs a **custom SMTP provider** configured in Supabase Auth settings (Project Settings → Auth → SMTP Settings) — we're already using Resend for nudges (PRD.md §4.4), so the natural move is pointing Supabase's auth emails through Resend too instead of running two separate email setups.
  - **Done (2026-07-28):** Custom SMTP configured — Supabase Dashboard → Project Settings → Authentication → SMTP Settings, pointed at Resend's SMTP relay (`smtp.resend.com`, port 587, username literally `resend`, password = the Resend API key — same key already used for nudges). Sender address: `auth@spectroniqlimited.com`. This is also what unlocked *editing* the auth email templates properly — Supabase gates full template customization behind having a custom SMTP provider configured, not just the built-in service. Confirmed working end-to-end via a real password-reset email.
- [ ] Google OAuth setup (separate follow-up — needs a Google Cloud OAuth client)
- [x] Row Level Security (RLS) — see `learning/sys-design.md` §6 for the full writeup, including the recursive-policy trap we hit and how it's fixed
- [x] Storage buckets — see `learning/sys-design.md` §8 for the full writeup (private bucket + path-based RLS + signed URLs, plus the `!inner` embedded-filter trick used to build the audit feed query)
- [ ] Realtime subscriptions — how the audit feed could update live without polling
- [ ] `pg_cron` / scheduled Edge Functions — used for auto-verifying completions and detecting missed cycles (see `learning/sys-design.md` §4 for *why* this is needed)
- [ ] **Generate real Supabase types** (`supabase gen types typescript`) — this project still has zero generated types, so every `.rpc()`/`.from()` call is implicitly `any`-shaped. Has caused two real TS errors now (a discriminated-union return-type gotcha in `learning/sys-design.md` §9, and `circle_preview`'s `.rpc().single()` needing a manual type assertion) that generated types would catch or avoid entirely — worth doing properly rather than continuing to hand-write casts one RPC at a time.

## 4. Two things learned building multi-circle (2026-08-04)

### Postgres functions are identified by their *argument signature*, not just their name

We wanted to "allow joining multiple circles," which meant undoing the single-circle guard added in `00000000000018`. That migration looked like it guarded `create_circle` and `join_circle`. But the app kept letting you *create* extra circles while blocking *joining* them — a contradiction that only made sense once we looked at the signatures:

- `00000000000008` created `create_circle(text, time, text)` — 3 args, the version the app calls (it passes a description).
- `00000000000018` then wrote `create or replace function create_circle(circle_name text, circle_reset_time time ...)` — 2 args.

In Postgres, `foo(text, time)` and `foo(text, time, text)` are **two different functions** that happen to share a name (overloading). `create or replace` matches on the *whole signature*, so migration 18 didn't replace the 3-arg function — it created a brand-new 2-arg overload that nothing ever called, and put the guard there. The real code path never had a guard.

**Takeaways:**
- To *change* a function's parameter list you must `drop function` the old signature first (migration 8 does exactly this: `drop function if exists public.create_circle(text, time);` before recreating with 3 args). `create or replace` alone can't do it — it'll silently leave a stale overload behind.
- `grant execute` is also per-signature — dropping/recreating a signature drops its grants, which is why these migrations re-`grant execute on function create_circle(text, time, text)` each time.
- When two overloads of a function exist, a call resolves to whichever signature matches the arguments passed. Ambiguity here is a real (confusing) bug source. `00000000000034` deletes the dead 2-arg overload precisely so there's only ever one `create_circle`.
- How we'd have caught it faster: `\df create_circle` in `psql` (or querying `pg_proc`) lists *every* overload with its argument types — the source of truth over "what the latest migration file looks like."

### The "active record" pointer + resolver pattern

Once a user can be in many circles, every page needs to know *which* circle to show. Two moving parts:

1. **A pointer column** — `users.active_circle_id uuid references circles(id) on delete set null`. `on delete set null` means a deleted circle can never leave a dangling pointer. We also **backfilled** it (`update users set active_circle_id = (select ... order by joined_at desc limit 1)`) so behaviour is identical to before on day one — a freshly added nullable column is `null` for every existing row until you populate it.

2. **A resolver that never trusts the pointer blindly** (`src/lib/active-circle.ts`). The pointer can be *stale* (you left that circle) or *null* (brand-new user). So the resolver: read the pointer → confirm you still have a membership in it → if not, fall back to your most-recently-joined membership → `null` only if you're in no circles. This means a page can *never* render against a circle you're not in, even if the stored pointer is wrong.

The split that kept it clean: **reads happen in TS** (the resolver, running under normal RLS — it only ever reads the caller's own `users` row and own memberships), while **writes happen in `SECURITY DEFINER` RPCs** (`set_active_circle`, plus `create_circle`/`join_circle`/`leave_circle` maintaining the pointer as a side effect). `set_active_circle` re-checks membership before writing, so a caller can never point `active_circle_id` at a circle they don't belong to — don't rely on a table's UPDATE policy being tight enough for that.

**Stale-pointer self-healing:** when an admin removes someone with `remove_member`, we *don't* bother clearing that user's `active_circle_id` (it's another user's row). The resolver's fallback fixes it automatically on their next page load. Leaning on the resolver instead of special-casing every mutation is the whole point of having a resolver.

---

## The general version of this
- [[concepts/01-backend/06-authorization|Authorization (concepts)]] — RBAC/ABAC and why authz belongs at the data layer
- [[cybersecurity/04-web-security/README|Web security]] — the attacks RLS is defending against
- [[databases/sql-reference|SQL reference]]

↑ [[projects/README|All projects and the domains they exercise]]
