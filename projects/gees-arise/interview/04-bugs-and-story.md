# Gees Arise — Bugs, Workflow & Project Story

The behavioural half. This project's bugs are unusually good interview material because most of them
are **silent** — no error, no type failure, just wrong data.

---

### Q1. [Advanced] 🔥🔥 Tell me about a bug that no test or type system could have caught.

**Pick one and tell it properly. The three best, in order:**

**1. The second foreign key.** Adding circle tags gave `circle_memberships` a `peer_tag_set_by`
column referencing `users(id)` — a **second** FK into `users`, alongside `user_id`. The Gees page
immediately showed "The Gees (0/7)" with no members. Cause:
`PGRST201 — Could not embed because more than one relationship was found`.

Any query doing a **bare** `users(...)` embed on `circle_memberships` is only unambiguous while
exactly one FK path exists. The moment a second appears, every such query breaks **with no code
change of its own**. Three call sites used the bare form and broke; three others happened to be
written as `users:user_id(...)` and survived — not because that's the documented disambiguation
mechanism, but by luck. PostgREST's own error `hint` gave the supported fix:
`users!circle_memberships_user_id_fkey(...)`, naming the constraint explicitly. Every call site was
standardised on that form rather than leaving the accidentally-working ones alone.

**The lesson:** adding a foreign key is a breaking change to **every other query in the codebase**
that embeds that table without a hint. Before adding a second FK from A to B, grep every
`.from("A")` and check its `.select(...)` for a bare `B(...)`.

**2. `.limit(1)` with no `ORDER BY`** across eight files — see
[02-data-modeling-and-invariants.md](02-data-modeling-and-invariants.md) Q12.

**3. A migration in the repo that was never applied.** The audit-feed bug that "correct code +
correct RLS" analysis could not explain, because the analysis was of a policy that didn't exist in
the running database. See Q3 below.

**The thread connecting all three, and this is the answer to give:** each was a pattern that was safe
under one **unstated assumption** — "only one FK path exists", "a user is in exactly one circle",
"the repo's migrations are what's live". Nothing in the compiler or the type system can check an
assumption that was never written down. Only grep, or the runtime error, will.

---

### Q2. [Advanced] 🔥 How did you find these, given none of them threw in the code that was wrong?

**Strong answer covers:** the permanent **`error_logs` table**. When the Gees page went to zero
members, the cause was sitting in `error_logs` the moment it was checked — `PGRST201` with the exact
relationship ambiguity spelled out, plus a `hint` containing the fix. Without a persisted error
record, a PostgREST error surfaces as an empty result set in the UI and you go looking in the
application code, which is correct.

**The generalisable habit:** for any system where the *data layer* can fail in ways the *application
layer* reports as "no rows", persist the errors somewhere queryable. Console logs in a serverless
environment are gone by the time you're asked about them.

---

### Q3. [Advanced] 🔥 "A migration existing in the repo doesn't mean it's live." Unpack that.

**Strong answer covers:** the audit feed misbehaved, the code was correct, and the RLS policy in the
repo was correct — so analysis of the source could never find it, because the *running database*
didn't have that migration applied. The mental model failure is treating the repo as the source of
truth about production state; the repo is the source of truth about *intent*.

**The habit that follows:** verify the live state rather than reading the intended state — check the
applied-migrations table, and for a policy or grant, actually attempt the operation as the target
role. "The migration ran" and "the intended rule exists" are different claims.

---

### Q4. [Intermediate] 🔥 Your Vouch button doesn't exist. Explain that decision.

**Strong answer covers:** the wireframe showed a "Vouch 👍" button, but per the state machine
**nothing needs to happen when you vouch** — a proof auto-verifies once its audit window closes with
fewer than two flags. So building the button would have created a control that *looks* interactive
and is secretly inert: a write nobody reads. Instead the feed states the reasoning directly ("no
flags yet — auto-verifies at end of day") and wires up only `Flag`, the one action with real
downstream effect.

**The pattern to name:** match the UI to what the data model actually does, rather than building a
control because a mockup shows one. Inert controls are worse than absent ones — they teach users
that their input matters when it doesn't.

---

### Q5. [Intermediate] Proactive excuses reuse the penalty/vote mechanic instead of getting their own. Why?

**Strong answer covers:** an excuse and a penalty dispute are the *same* underlying operation — "the
circle decides whether this counts" — so they share the vote mechanic, the tie-break, and the state
machine. A parallel system would mean two vote implementations that must agree on quorum, ties, and
timing, and would drift the first time one was changed.

**Note the same instinct elsewhere:** `cast_penalty_vote` is shaped exactly like `flag_completion`.
Recognising that two features are one mechanism with different labels is the reusable skill.

---

### Q6. [Intermediate] 🔥 How do you work with git on this project, and why that way?

**Strong answer covers:** small, frequent commits in **Conventional Commits** format
(`type(scope): description`), one branch per feature or fix, interactive staging (`git add -p`) to
split a messy working tree into several honest commits, `git stash` to switch branches cleanly with
work in progress, and pre-commit hooks that make a bad commit physically impossible.

**The reason to give:** commit messages are the only documentation guaranteed to still exist and
still be accurate in a year. A commit that does one thing, with a message saying what and why, is
what makes `git log` and `git bisect` usable — and bisect is exactly the tool you want for a silent
data bug like Q1.

**Project-specific detail:** two remotes on purpose, mirroring to two GitHub orgs. Worth knowing that
`git push` targets one remote and mirroring is a deliberate, explicit act rather than something git
does for you.

---

### Q7. [Beginner] 🔥 Explain Gees Arise to a non-technical interviewer.

**Strong answer covers:** it's group accountability — you and a few friends form a circle, commit to
habits, and submit proof when you do them. The circle reviews the proof, and missed or disputed
tasks turn into penalties the group votes on. The engineering challenge is that everyone in a circle
can see and act on shared data, so the rules about who can see and change what have to be enforced
by the database itself, not by the app — because anyone can talk to the database directly.

That last clause is the technical hook stated in plain language, which is exactly what this question
tests.

---

### Q8. [Advanced] 🔥 What's the most important design decision in this project?

**Strong answer covers — commit to one:** putting the security boundary in Postgres. Everything else
follows from it — RLS policies as the default, `SECURITY DEFINER` RPCs for atomic actions, the
absence of UPDATE policies as a deliberate lock, constraints rather than application checks for the
abuse guarantees, and triggers so a new feature can react to an existing one without editing it.

**The cost, which you should volunteer:** the logic is spread across migrations rather than sitting
in application code, so it's less discoverable — a developer reading the TypeScript sees only half
the system. Mitigations: a `DECISIONS.md`, comments at insert sites pointing at triggers, and
migration filenames that describe what they do.

---

### Q9. [Advanced] What would you change if you started over?

**Strong answer covers — concrete, from the notes:**
- **Enforce single-circle membership from migration one**, rather than discovering that eight pages
  had baked in an unenforced assumption.
- **Standardise on explicit FK hints in every embed from the start** — the bare-embed form is a
  time bomb that only detonates when someone adds an unrelated column.
- **Direct-to-storage uploads from the beginning**, rather than routing bytes through the server and
  discovering the platform limit in production.
- **Treat `DECISIONS.md` as a first-class artefact** — most of the "why is this like this" answers
  in this project are non-obvious from the code, and the ones that got written down are the ones
  that survived.

---

### Q10. [Intermediate] 🔥 What have you learned from this project that changed how you build things generally?

**Strong answer covers — pick one and go deep:**
- **"An unstated assumption is a bug waiting for a schema change."** All three silent bugs are the
  same shape, and the fix in each case was to *enforce* the assumption rather than to work around its
  violation.
- **"Prevent it at the constraint layer, not in application code."** A rule expressible only in
  TypeScript applies only to people using your TypeScript.
- **"Absence of a policy is a security decision."** Not writing an UPDATE policy is stronger than
  writing a permissive one and hoping the app behaves.

Any of the three is a genuinely senior thing to say, and each one is backed by a specific incident in
this codebase — which is what makes it credible rather than aphoristic.
