# Gees Arise — Next.js, Frontend & Testing

From [`../learning/06-frontend.md`](../learning/06-frontend.md),
[`07-testing.md`](../learning/07-testing.md), and the frontend sections of
[`09-sys-design.md`](../learning/09-sys-design.md).

---

### Q1. [Beginner] 🔥 What are route groups and why does this app use `(marketing)`, `(auth)`, `(app)`?

**Strong answer covers:** parentheses around a folder name mean it **doesn't appear in the URL** —
it exists purely to group routes that share a layout. So `(marketing)` gets the public
header/footer, `(auth)` gets a bare centred layout, and `(app)` gets the authenticated shell with
navigation. Three completely different chromes, no URL segment, no layout conditionals checking
"am I on a marketing page?"

**The rule that goes with it:** route-group layouts own the chrome; pages render only content. Once
that's established, a page never renders navigation and a layout never renders page-specific data.

---

### Q2. [Intermediate] 🔥 shadcn/ui isn't a normal npm dependency. What is it, and what's the trade-off?

**Strong answer covers:** the CLI **copies component source into your repo** — you own the files, they
show up in your diffs, and you edit them directly rather than fighting a library's props API to
achieve a design change. The trade: no version bumps, no upstream bug fixes, and no single place to
change a component's behaviour across projects. It's the right model when the design is yours and
the components are a starting point; the wrong one when you want a maintained dependency.

---

### Q3. [Advanced] 🔥🔥 You raised Next's Server Action body limit to 8MB and photo uploads still failed. What was actually wrong?

**This is the best frontend story in the project. Tell it in four beats.**

1. **The first design:** `<input type="file">` inside `<form action={serverAction}>` genuinely
   works — the browser packages the file into `FormData` as a real `File`, and
   `supabase.storage.upload(path, image)` accepts it directly.
2. **The anticipated limit:** Next caps Server Action bodies at **1MB** by default, so
   `serverActions.bodySizeLimit` was pre-emptively raised to `8mb`. Reasonable-looking, and wrong.
3. **The real ceiling:** **Vercel hard-caps serverless request bodies at 4.5MB**, enforced by the
   platform. Next's `bodySizeLimit` has no effect on it whatsoever. So the "fixed" 8MB config would
   have failed again on the first 5MB photo.
4. **The actual fix — route the file around the server entirely.** A small `createCompletion()`
   Server Action (no file, just a task id) returns a `completionId`; the browser uploads the image
   **directly to Supabase Storage** with the browser client; then a tiny `attachProof()` action
   records the resulting storage **path**, not the bytes. Only the browser and Supabase's storage
   servers ever see the image. The `bodySizeLimit` override was removed afterwards, because it was
   solving the wrong layer.

**The lesson to state:** a **platform-level** hard limit always wins over an **application-level**
config knob that merely looks like it controls the same thing. Check which layer owns a limit before
trying to raise it.

**Bonus:** this is the same shape as presigned/direct-to-storage uploads everywhere — the API should
grant permission and record metadata, never proxy the bytes.

---

### Q4. [Advanced] 🔥 Splitting that flow into two Server Actions surfaced a TypeScript bug. What was it?

**Strong answer covers:** `createCompletion()` returns either `{ error: string }` or
`{ completionId, circleId }` depending on a branch. **Without an explicit return-type annotation,
TypeScript doesn't infer a clean union** — it infers one merged shape where every field from every
branch is present but optional: `{ error?: string; completionId?: string; circleId?: string }`.

That broke the caller's `"error" in result` narrowing: `error` technically exists as a key on every
branch (just `undefined` on success), so the `in` check narrowed nothing and `result.error` stayed
`string | undefined` even after it.

**The fix:** annotate explicitly —
`Promise<{ error: string } | { completionId: string; circleId: string }>` — which forces TypeScript
to keep two real shapes instead of merging them.

**The lesson:** inference optimises for "what type describes all the return statements," **not** for
"what union lets a caller discriminate cleanly." If a function returns different shapes on different
branches and the caller needs to narrow, annotate the return type.

---

### Q5. [Intermediate] 🔥 A shared layout stayed stale after the data it depends on changed. What's going on?

**Strong answer covers:** layouts don't re-render on navigation between their child routes — that's
the point of a layout, and it's normally a performance win. But when the layout renders data (a
member count, a circle name) that a *child page's* mutation changes, the layout keeps showing the old
value while the page updates.

**The fixes, in order of preference:** `revalidatePath` on the layout's path after the mutation so
the server re-renders it; moving the volatile piece out of the layout into the page that owns it; or
lifting it into a client component subscribed to the change. The general point: **rendering data in
a layout is a caching decision**, not a placement decision — anything mutable in a layout needs an
invalidation story.

---

### Q6. [Intermediate] Next.js 16, not 14 — what actually changed that mattered?

**Strong answer covers:** rather than reciting a changelog, name the habit — the project reads the
**installed** version's docs rather than relying on remembered patterns, because most Next.js answers
online target whichever version was current when they were written and the App Router has moved
substantially. Concretely, things like async request APIs and caching defaults changed between
versions in ways that silently alter behaviour rather than erroring.

**The honest version of this answer** is "here's how I avoid being wrong about this," which is more
useful than a half-remembered feature list.

---

### Q7. [Intermediate] What did the design/UX pass fix, and why was the whole app gray?

**Strong answer covers:** the default shadcn/Tailwind palette applied without deliberate token
choices produces a uniformly gray interface — every surface uses the same neutral, so there's no
visual hierarchy and nothing signals which element matters. The fix is establishing tokens
intentionally: a real accent colour for primary actions, distinct surface levels so cards separate
from background, and semantic colours (success/warning/destructive) that carry meaning rather than
decoration.

**The engineering-adjacent point:** design tokens, not per-component magic values — otherwise a
palette change is a hundred edits.

---

### Q8. [Intermediate] 🔥 You use Playwright in an unusual way. Explain.

**Strong answer covers:** two modes — the **test runner** (`*.spec.ts` files, assertions, CI), and
**driving a real browser to verify something manually during development**. This project leans on the
second: an agent or developer opens the real app against the dev server and checks that a flow
actually works, rather than trusting that the code looks right.

**Why it matters here:** most of the interesting logic lives in the database (RLS policies, RPC
functions, triggers), and the only way to know a policy behaves correctly for a *real authenticated
session* is to exercise it through the real client. Unit tests around the app code wouldn't touch it.

**The `e2e/auth.spec.ts` shape worth describing:** navigate, fill, submit, assert on the resulting
page — plus the config's `webServer` block, which starts the dev server so the suite doesn't assume
one is already running.

---

### Q9. [Intermediate] What's hard about testing this app specifically?

**Strong answer covers:** the behaviour under test is **time-dependent and job-driven** — an audit
window closing, a missed cycle detected, a penalty going overdue. A test can't wait a day, so those
paths need either a date-parameterised job you can invoke for a chosen date (which the design already
supports) or seeded data that's already in the target state. And RLS means tests must run as a real
authenticated user, because service-role access bypasses exactly the logic you want to verify.

---

### Q10. [Beginner] How do you actually run and verify things during development?

**Strong answer covers:** dev server in the background, Playwright to drive the real browser, the
linter run directly rather than relying only on the pre-commit hook, and `tsc`/build to verify
compilation separately from tests. The habit underneath: **check the installed thing, don't trust
memory** — read the version in `package.json` (watching for the caret, which means what's installed
may differ from what's written), and read docs bundled with the dependency rather than searching.

---

### Q11. [Intermediate] 🔥 Why Husky pre-commit hooks, and what belongs in one?

**Strong answer covers:** a hook makes git **physically refuse** a bad commit — lint and typecheck
run before the commit is created, so broken code never enters history and CI isn't the first thing to
notice. What belongs: fast, deterministic checks (lint, format, typecheck). What doesn't: a full test
suite or anything slow, because a hook people routinely bypass with `--no-verify` is worse than no
hook.

**Related habit worth mentioning:** `git add -p` for interactive staging, which is how one messy
working tree becomes several honest commits rather than one "various changes" blob.
