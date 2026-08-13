# my-applicant — Pipeline & System Design

From [`../learning/03-sys-design.md`](../learning/03-sys-design.md). The most transferable part of
the project — every idea here generalises to any batch/agentic pipeline.

---

### Q1. [Intermediate] 🔥 Walk me through the pipeline stages and explain the ordering.

**Strong answer covers:** `discover → prefilter → score → tailor → route`, with costs
`network → free → cheap LLM → expensive LLM → free`. The ordering isn't stylistic — each stage
exists to **reduce what the next stage sees**. `prefilter` is pure local string matching (title
contains "intern", location mismatch), so it costs nothing and runs before any model call. `score`
is a batched, cheap LLM call. `tailor` is a large per-job call and only runs above `minScore`.

**The rule to state explicitly:** put the cheap filter before the expensive one, and make the
expensive stage's input as small as possible. A tenfold reduction at the free stage is a tenfold
saving at the paid stage.

**Bonus that lands well:** this is the same shape as a query planner pushing predicates down, or a
build system checking timestamps before recompiling. Naming the analogy shows you recognised a
pattern rather than invented a one-off.

---

### Q2. [Intermediate] 🔥 The tool runs unattended at 3am. What does that requirement force?

**Strong answer covers:** **running it twice must not do the work twice.** Idempotency isn't a nice
property here, it's the precondition for unattended operation — because there's nobody to notice a
crash halfway through, and the recovery strategy has to be "just run it again." The database
provides it: jobs are recorded at discovery, applications at every state change, and each run
checks `isAlreadyHandled(job.id)` before doing anything. A crashed run needs no special recovery
logic; the already-handled check absorbs the overlap.

---

### Q3. [Advanced] 🔥 `skipped` counts as "already handled." Why record a negative decision?

**Strong answer covers:** a job scored below threshold is recorded as *deliberately skipped*, not
left absent. If it were absent, every future run would re-discover and re-score it, paying for the
same judgement forever. **Recording a negative decision is as valuable as recording a positive
one** — it's what makes the work monotonically decrease across runs instead of staying constant.

**Follow-up worth pre-empting:** *"What if your scoring criteria change?"* — then the skip records
are stale by design, and you need either a criteria version stamped on the record or an explicit
re-score command. Volunteering that limit is stronger than being caught by it.

---

### Q4. [Intermediate] 🔥 Why isn't the source-assigned job ID enough for deduplication?

**Strong answer covers:** IDs are only unique *within* a source. The same job is
`greenhouse:stripe:12345` and `remotive:98765` — different IDs, identical job. So there's a second,
**semantic** key: normalised company + normalised title (`lowercase`, collapse whitespace, trim),
joined. It's approximate by nature, and that's acceptable because the cost of a false merge here is
low compared to applying twice.

---

### Q5. [Advanced] 🔥 When two sources have the same job, you keep the higher-ranked one: ATS (3) > HackerNews (2) > aggregators (1) > LinkedIn (0). Is that a data-quality ranking?

**Strong answer covers:** **No — it's a capability ranking.** Only the ATS record carries a
driveable application form. Keeping the Remotive echo of a Greenhouse job would silently demote an
auto-appliable job into the manual queue, without anything looking broken. The generalisable rule:
**when deduping, prefer the record that can do the most, not the one that arrived first** (or the
one that looks cleanest).

This is one of the best questions in the set because "first write wins" / "last write wins" is
everyone's default and both are wrong here.

---

### Q6. [Advanced] 🔥 How did you decide what the system may do automatically versus what it must queue?

**Strong answer covers:** entirely from one asymmetry — a queued application costs about ten seconds
of review; a wrongly submitted application **cannot be unsent** and carries your name. Given that,
every ambiguous case queues. The routing function queues on: an unfamiliar source, a scorer concern,
a tailoring violation, a missing PDF, a per-run ceiling, *and* a failed submission attempt. Inside
the submitter, any required field still empty aborts rather than submitting something half-filled.

**The rule to state:** ask of any automated action — *what does a wrong call cost, and can I take it
back?* Cheap and reversible, automate freely. Expensive and irreversible, make the machine ask. And
the default behaviour on confusion is **stop**, not **guess**.

---

### Q7. [Intermediate] 🔥 `Promise.allSettled` instead of `Promise.all`. Why, and what's the general principle?

**Strong answer covers:** `Promise.all` rejects the instant any promise rejects — one stale LinkedIn
selector or one typo'd board slug would sink the entire night's run before the other sources
returned anything. `allSettled` waits for all and reports each outcome, so a broken adapter costs
that source's jobs and nothing else. Errors are **collected and reported**, not discarded: visible
but not fatal.

**Generalise it:** decide *per component* whether a failure is fatal or degrading. Most are
degrading, and `Promise.all` gives you no way to say so. The same idea appears in the PDF renderer —
a PDF failure returns `pdfError` and the Markdown and HTML still get written, because a missing PDF
is a degraded result, not a failed application.

---

### Q8. [Intermediate] What do you retry, and what do you refuse to retry?

**Strong answer covers:** `429` and `5xx` only — those are transient, so waiting genuinely helps.
`404` and `401` are permanent: a wrong board slug or a revoked key will still be wrong in two
seconds. Retrying them is pure noise, and hammering a public API on a permanent error is how an IP
gets blocked. Also: honour `retry-after` when the server sends it — the server's own guidance beats
your exponential-backoff guess.

**Follow-up:** *"What about a 403?"* — genuinely ambiguous; it can be a rate limit in disguise or a
permanent block. Treating it as permanent (and surfacing it loudly) is the safer default for a
system that runs unattended against someone else's API.

---

### Q9. [Intermediate] Where does state live, and why a database rather than files or in-memory?

**Strong answer covers:** the database *is* the idempotency mechanism (Q2/Q3), so it has to survive
a crash mid-run and be queryable ("have I handled this?", "what's in the review queue?"). Files
would work but you'd hand-roll the query and the atomicity. In-memory is a non-starter for an
unattended process whose recovery plan is "run it again."

---

### Q10. [Advanced] How would this change if it had to run for a thousand users instead of one?

**Strong answer covers:** the stage architecture survives; the execution model doesn't. Single-user
runs as one sequential process; multi-user needs per-stage queues so one user's slow crawl doesn't
block others, per-user rate-limit accounting against shared external APIs (the board doesn't care
that your thousand users are separate people), per-user key isolation (BYOK becomes a
secret-management problem rather than an env var), and a much harder version of the ethics question,
because a thousand tailored applications a night to the same board is a different thing from one
person's job search. Volunteering that last point is the strongest part of the answer.

---

### Q11. [Beginner] What's the failure mode you're most worried about, and how would you detect it?

**Strong answer covers:** silent quality decay — the system keeps running, keeps submitting, and the
tailoring gets subtly worse (or the scorer drifts) without anything erroring. Detection is a
counting problem, not an exception problem: track violations-per-run, queue-rate, and score
distribution over time. A sudden jump in violations means the model or the profile changed; a queue
rate of zero means the guardrails stopped firing, which is more alarming than a high one.
