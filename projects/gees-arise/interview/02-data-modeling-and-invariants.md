# Gees Arise — Data Modeling, State Machines & Invariants

From [`../learning/09-sys-design.md`](../learning/09-sys-design.md) and
[`03-sql.md`](../learning/03-sql.md).

---

### Q1. [Intermediate] 🔥 Explain "rule tables" versus "instance/log tables."

**Strong answer covers:** a **rule** table holds the definition — a task, its frequency, its
schedule. An **instance/log** table holds what actually happened — a completion, a penalty, a streak
event. The rule says "this should happen daily"; the log says "on 2026-08-04, it did."

**Why the split matters:** you cannot answer "did this happen yesterday?", "how many times has this
been missed?", or "what did the schedule look like when this was completed?" from a rule table
alone — editing the rule would rewrite history. Keeping instances separate is what makes the past
immutable and the present editable.

---

### Q2. [Advanced] 🔥 How do you model several different recurrence shapes — daily, negative habits, one-offs, day-of-week — without a table per type?

**Strong answer covers:** one log table for all of them, with the *type* as a column and the
recurrence as data rather than as structure. The strongest evidence this was the right call: adding
**day-of-week scheduling** was a new *dimension bolted onto* DAILY/NEGATIVE, not a new task type. If
each shape had its own table, that feature would have meant a fifth table and touching every query.

**The rule:** model variation as data when the *behaviour* is shared and only the parameters differ;
model it as separate tables when the behaviour genuinely diverges. The test is whether a new variant
requires new queries or just new rows.

---

### Q3. [Intermediate] Streaks and "today's %" only count DAILY/NEGATIVE tasks, and the streak counts from *yesterday*. Why both of those?

**Strong answer covers:** one-off tasks aren't a rhythm — including them makes a completion percentage
meaningless (finish a one-off and today is suddenly 150%). And a streak counted from *today* is
always provisional, because today isn't over: you'd either show a streak the user might still lose,
or reset it at midnight for everyone who hasn't started yet. Counting from yesterday means the streak
is a statement about **settled** days only.

**Generalise it:** any metric over a period must decide what an incomplete period does. Most streak
bugs are that decision left implicit.

---

### Q4. [Advanced] 🔥 Optimistic UI backed by a state machine — why does the state machine matter?

**Strong answer covers:** optimistic UI shows the result before the server confirms it. That's only
safe if there's a defined set of states and legal transitions, so the UI can show an *intermediate*
state honestly — `DONE_PENDING_AUDIT` is not `VERIFIED`, and pretending otherwise means the user
believes something the system hasn't decided yet. The state machine is what lets the interface be
fast and truthful at once: instant feedback, accurate label.

**The related detail worth naming:** the "Auditing" label has **zero fallback logic of its own** —
it's a pure mirror of a database column that only a cron job ever changes. That's deliberate. If the
client tried to *infer* "this is probably still auditing" from timestamps, the client and the job
would eventually disagree, and the client would be wrong. One writer, one reader, no derived guesses.

---

### Q5. [Intermediate] 🔥 Why do some things need a scheduled job rather than a request handler?

**Strong answer covers:** because the event is the **passage of time**, and nobody makes a request
when time passes. An audit window closing, a cycle being missed, a penalty going overdue — these must
happen whether or not anyone opens the app. Doing them lazily on next read means a user who never
logs in never gets penalised, and two users reading at different times see different worlds.

**The consequence for design:** the job needs the service-role key (it has no user session), and it
must be **idempotent and date-parameterised**, so a missed run can be re-run for the specific date
rather than "catching up" ambiguously.

---

### Q6. [Advanced] 🔥 A cron job created penalties for tasks that didn't exist yet. What was the bug?

**Strong answer covers:** `detect_missed_cycles` never checked whether the task **existed yet** at the
time of the cycle it was evaluating — so a task created today generated a "missed" penalty for
yesterday, when it didn't exist. The general class: a job that iterates over *time periods* and
cross-references *entities* must bound the iteration by the entity's own creation, or it invents
history.

**Why it's worth telling:** it's a reported bug (a user noticed, not a test), and the fix is a
one-clause change with a clear invariant behind it — a period before an entity's creation is not a
period that entity can have failed.

---

### Q7. [Advanced] 🔥🔥 Explain the trigger that forfeits a stake, and why it isn't inside the functions that create penalties.

**Strong answer covers:** the rule is "if a member gets a penalty while their circle has a live
stake, they forfeit their share." The tempting place is inside the functions that insert penalties —
but there are already **three** of them (`flag_completion`, `detect_missed_cycles`, `submit_excuse`),
and every future one would have to remember the same logic. Miss one and stakes silently stop working
for that path.

**Instead:** an `AFTER INSERT ON penalties` trigger (`private.forfeit_active_stake`). It fires
whenever a row lands in `penalties`, regardless of which function put it there — **including
functions written after the trigger existed**.

**When to reach for a trigger:** when the rule is "whenever X happens, also do Y" and Y is
conceptually a *different feature* from whatever caused X. `penalties` doesn't need to know Stakes
exists; Stakes doesn't need to hook into three call sites; the trigger is the one place that knows
both.

**The trade-off you must volunteer:** trigger logic is **less discoverable**. Reading
`flag_completion` top to bottom won't tell you a stake forfeiture may also happen — you have to know
to check the table's triggers (`\d penalties`). The mitigation is a comment at the insert site.
Naming the discoverability cost is what separates this from "triggers are cool."

---

### Q8. [Advanced] 🔥 What's a partial unique index and why did you need one?

**Strong answer covers:** `unique index ... where status = 'ACTIVE'` — Postgres enforces uniqueness
only among rows matching the `WHERE`. A plain unique constraint on `circle_id` would mean a circle
could never have a second stake *ever*, even after the first settles. Scoping the uniqueness to the
rows that currently matter means any number of `SETTLED` stakes coexist, with only one `ACTIVE` at a
time.

**The second use, for a different reason:** `penalties_task_cycle_unique` uses
`where cycle_key is not null`, because rejection-triggered penalties don't use `cycle_key` at all —
so there, the partial index means "only some rows have a meaningful key to dedupe on." Same tool, two
motivations: *only some rows represent a live state* versus *only some rows have the key*. Being able
to give both is the strong version.

---

### Q9. [Advanced] 🔥 How do you create one row per member from a single authoring action, and what breaks afterwards?

**Strong answer covers:** the creation half is a single statement, not a loop —
`insert into tasks (...) select ..., cm.user_id, ... from circle_memberships cm where cm.circle_id = X`.
One atomic `INSERT ... SELECT`: simpler than a `plpgsql` loop and with no per-row failure mode.

**The harder half, which is the real answer:** a goal fanned out at creation time only reaches members
who existed *then*. A late joiner never gets a task for it. Rather than bolting a "sync goals" step
somewhere in the join flow, the fan-out is duplicated inside `join_circle` itself — the same
`INSERT ... SELECT` shape run **from the other direction** (new member → all active goals, instead of
goal → all current members).

**The general lesson:** whenever an action fans out a per-member side effect at creation time, ask
what happens when a new member arrives afterwards. The answer is usually "the same fan-out, run from
the other direction" — not a background job or a catch-up script.

**The judgement call to add:** Stakes deliberately did *not* get this treatment. Enrolling a late
joiner into an already-created goal is cheap and safe (worst case, an instantly-overdue one-off
task); enrolling them into an already-active **money** stake is a real product decision — are they on
the hook for an amount they never agreed to? Knowing which side of that line a fan-out sits on before
automating it is the point.

---

### Q10. [Advanced] 🔥 Task deletion can't double as evidence-tampering. How do you prevent that?

**Strong answer covers:** if deleting a task cascades away its completions, proofs and penalties, then
"delete the task" becomes "erase the evidence that I failed" — in an app whose entire purpose is
accountability, that's not a data-integrity concern, it's the product being defeated. So deletion is
a **soft** operation (deactivate the rule, keep the log), and the historical instances survive
independently of the rule that created them.

**This is the payoff of Q1's rule/log split** — because instances are separate rows rather than
children of a mutable rule, history *can* outlive the rule. Connecting the two is the strong answer.

---

### Q11. [Intermediate] 🔥 The penalty vote can deadlock at 50/50. How did you resolve it?

**Strong answer covers:** "majority" alone can **mathematically never** resolve an even split — it's
not an edge case to handle later, it's a property of the rule. So there has to be a tie-break: an
admin decision. Note the pattern reuse — `cast_penalty_vote` is shaped exactly like
`flag_completion`, and proactive excuses reuse the penalty/vote mechanic rather than introducing a
parallel one.

**The generalisable point:** when a rule is a vote, enumerate the outcomes *including the ones with no
winner*, before building it. "We'll handle ties later" means shipping a state the system can enter and
never leave.

---

### Q12. [Advanced] 🔥🔥 `.limit(1).maybeSingle()` with no `ORDER BY` — what's wrong with it?

**Strong answer covers:** `.limit(1)` without `.order()` does **not** mean "the first one." Postgres
makes no ordering guarantee for a query with no `ORDER BY` — which row comes back is a query-planner
implementation detail, not a contract. Eight different pages answered "which circle is this user in?"
with exactly that pattern.

**Why it was invisible:** with exactly one membership row there's only one possible answer, so the
pattern ships everywhere and never misbehaves. It becomes a user-visible bug the moment a second row
exists — and then it isn't even *consistently* wrong: different pages, or the same page on reload,
could show different circles.

**The fix, and this is the part that matters:** it wasn't "add `ORDER BY joined_at` to eight
queries." That papers over the symptom while leaving the real premise — a user can be in more than one
circle — silently true. The fix closed it at the source: `create_circle` and `join_circle` now refuse
to create a second membership row, so the eight call sites' unstated assumption goes back to being
*actually* true instead of usually true.

**The general lesson:** `.limit(1)` / `.single()` is a **claim that the query can only ever match one
row**. Treat it as an assertion to verify — is there a unique constraint or enforced invariant that
guarantees it? — not as a convenient way to unwrap an array. Without the invariant, it doesn't create
false precision; it silently picks an arbitrary one of however many rows exist.

---

### Q13. [Intermediate] Proofs were redesigned to allow an optional image plus **either** a link or a note, never both. Why constrain that?

**Strong answer covers:** because "or" in a product spec has to become a constraint in the schema, or
it's just a hope. Allowing both makes every consumer of a proof handle four combinations and makes
"what is this proof?" ambiguous in the audit feed, where reviewers need to compare like with like.
Enforced at the database level (a `CHECK` constraint), it's true for every writer including the REST
API — which is the same argument as Q10 in
[01-postgres-rls-and-security.md](01-postgres-rls-and-security.md).

---

### Q14. [Beginner] Which SQL do you actually use daily here, and what tripped you up?

**Strong answer covers:** `SELECT ... FROM ... WHERE`, `JOIN` on a shared key, aggregations
(`count`, `sum`) with `GROUP BY`, and computed columns. The gotcha worth naming: `=` versus `IN (...)`
versus `ILIKE` — a query returning nothing is usually a matching problem, not a data problem.
`ILIKE` is case-insensitive `LIKE`, and needs wildcards (`%foo%`) to match anything but an exact
string, which is the specific mistake that returned zero rows.
