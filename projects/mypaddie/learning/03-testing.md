# 03 — Testing

*MyPaddie, Day 1 (2026-10-05). Files: `src/**/*.test.ts`, `supabase/tests/rls.test.sql`.*
See also: [[02-rules-engine-design]] · [[01-supabase-schema-and-rls]]

## `bun test`

Bun has a Jest-compatible test runner built in — no Vitest/Jest dependency.

```ts
import { describe, expect, test } from "bun:test";

test("one second late pays the late share", () => {
  expect(total(completionXp(task(), at("2026-10-05T07:00:01")))).toBe(5);
});
```

```bash
bun test src          # run everything under src/  (also: bun run test)
bun test xp           # only files whose path matches "xp"
bun test --watch      # rerun on save
```

Tests sit **next to** the code (`xp.ts` + `xp.test.ts`) — the feature-based layout.

## Testing time: build dates in the zone you mean

```ts
const at = (local: string) => new Date(`${local}+01:00`); // Lagos wall-clock
at("2026-10-05T07:00:00") // 07:00 in Lagos, unambiguous
```

`new Date("2026-10-05T07:00:00")` with no offset uses the *machine's* zone — a test
that passes on your laptop and fails in CI. Always give an offset or a `Z`.

## Edge cases worth a test — the boundaries

The bugs live at the edges, so the tests stand on them:
- exactly at the due time (on time) vs one second after (late)
- 23:59 on the due day (not ignored yet) vs 00:00 next day (ignored)
- 22:30 UTC vs 23:30 UTC on the same date (different Lagos days)
- day 30 of the audit vs day 31
- weights summing to 99, 100, 101; a weight of 0; a duplicate pillar
- 1 XP split three ways; 0 XP; negative XP
- needs exactly equal to income

## Table tests: `test.each`

One test body, many inputs:

```ts
test.each(["want", "goal", "wish", "dream", null] as const)(
  "a %p task is never deducted for being skipped",
  (tier) => { expect(ignoredNeedDeduction(task({ tier }), [], later)).toEqual([]); },
);
```

## Property-style checks

Instead of one example, assert something that must hold for *many* inputs:

```ts
for (const amount of [1, 2, 3, 7, 10, 11, 33, 99, 101, 12345]) {
  expect(sum(splitXp(amount, exercise))).toBe(amount); // nothing lost to rounding
}
```

## pgTAP: testing RLS in the database itself

Unit tests can't prove the *database* stops user B reading user A's rows. pgTAP
runs assertions inside Postgres. The trick is pretending to be a user:

```sql
set local role authenticated;
set local request.jwt.claims = '{"sub":"2222…","role":"authenticated"}';
select is_empty($$select 1 from public.items$$, 'intruder sees no items');
```

`auth.uid()` reads `sub` from those claims, so every policy now runs as the
intruder. The whole file is wrapped in `begin; … rollback;` so it leaves nothing
behind.

Error codes asserted with `throws_ok`: `42501` permission denied · `23503` FK
violation · `23505` unique violation · `23514` check violation.

```bash
bunx supabase test db   # (bun run db:test)
```

## Gotcha: two ways `auth.uid()` reads the user

The first pgTAP run failed on the very first insert: *"new row violates
row-level security policy"*. Not a policy bug — read the function before
changing anything:

```bash
podman exec mypaddie_db psql -U postgres -tAc \
  "select pg_get_functiondef('auth.uid()'::regprocedure)"
# → select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid;
```

The bare Postgres image ships an **older** `auth.uid()` reading
`request.jwt.claim.sub`; the full stack/hosted Supabase reads
`request.jwt.claims ->> 'sub'`. The test now sets both, so it passes on either.
Lesson: when a security test fails, find out *which side* is wrong before
loosening a policy to make it green.

## Running pgTAP without the CLI

```bash
podman exec -i mypaddie_db psql -U postgres -X -q -tA -v ON_ERROR_STOP=1 \
  < supabase/tests/rls.test.sql
```
Output is TAP: `1..22` then `ok 1 - …`. `-X` skips `~/.psqlrc`, `-tA` prints bare
rows (no headers/alignment) so the TAP lines come out clean.

## Day 3: two test failures that were the test's fault

Both in the push suite, both from tests that walk through a day by calling
`collect_nudges(p_now)` at increasing times:

1. **Out of order.** Asking "what's due at 12:30?" before "what's due at 11:20?"
   meant 12:30 sent the 4th nudge, so 11:20 had nothing left. Time-walking tests
   must run in time order, because each call *changes state* (it records what
   it sent).
2. **Too narrow an expectation.** At 09:50 a heads-up was due — and so was the
   reading's 3rd escalation (100 minutes after the 2nd). The test assumed one
   row and crashed on `more than one row returned by a subquery`.

The rule for both: when a test fails, first ask *is the expectation right?*
Read what the function actually returned before changing the function.

## A hidden input isn't in the form at all (2026-10-07)

The add-quest form shows different fields per tier (needs have money amounts,
goals have a target and deadline). The server action parsed
`Object.fromEntries(formData)` with:

```ts
const optionalText = z.string().trim().transform((v) => v || null);
```

That handles an *empty* field (`""` → `null`) but not a *missing* one: a
conditionally rendered `<input>` that isn't on screen sends no key at all, so
`z.string()` gets `undefined` and fails. Adding a need or a goal never worked.

Fix — accept both shapes of "nothing":

```ts
const optionalText = z.string().trim().optional().transform((v) => v || null);
```

Found by checking the schema against a two-line script (`bun file.ts` with
`schema.safeParse({ title: "x" })`) instead of reasoning about it. Lesson for
tests: a form schema needs a case for *each* variant of the form, not just
the one with every field filled in.

## A smoke script against the local stack (2026-10-07)

Unit tests cover the pure rules and pgTAP covers the SQL, but the repo layer
(TypeScript calling Postgres through RLS) sat between them untested. A
throwaway script fills that gap without a test framework:

1. Create a user with the local **admin** API (the local secret key comes from
   `supabase status -o json` — it's a fixed demo key, never a real one).
2. Sign in as them with the publishable key to get a real access token.
3. Call the real repo functions with a client built from that token, so RLS
   applies exactly as in production.

```sh
J=$(supabase status -o json)
SECRET=$(echo "$J" | python3 -c 'import json,sys; print(json.load(sys.stdin)["SECRET_KEY"])') \
  bun --tsconfig-override ./tsconfig.json /tmp/smoke.ts
```

`--tsconfig-override` makes Bun use the project's `@/…` path aliases for a
script that lives outside the project.

It caught a test-setup trap straight away: `created_at` comes from the
database's `now()`, not from the `now` passed to the function, so a task
"created an hour ago" in the script was really created a millisecond before
being done. That matched the "logged after the fact" rule and was cancelled
rather than reopened. The rule was right; the fixture was wrong. When a rule
reads a timestamp the database sets, the test has to set it explicitly.
