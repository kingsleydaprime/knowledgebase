# my-applicant — Judgement, Ethics & Project Story

The questions that aren't about code. For this project they matter more than the code ones.

---

### Q1. [Intermediate] 🔥🔥 You built a bot that applies to jobs for you. Isn't that spam?

**This is the question. Prepare it properly.**

**Strong answer covers, in this order:**
1. **Take the concern seriously first.** Mass low-effort applications are a real cost imposed on
   recruiters, and any honest answer starts by conceding that rather than defending the category.
2. **Name what the design does about it.** The system isn't built for volume — it's built for
   *filtering*. `prefilter` and a `minScore` threshold exist to make the system apply to *fewer*
   things than a human spraying applications would, and each application is individually tailored
   rather than a template blast. There's a per-run ceiling.
3. **The verification guardrail.** Nothing goes out containing a claim that isn't in the profile.
   The output is a truthful application, generated faster — not a fabricated one.
4. **Human-in-the-loop by default on ambiguity.** Unfamiliar source, scorer concern, tailoring
   violation, missing PDF → queue for review, not submit.
5. **The line you'd hold.** Don't defend a version of the system that ignores a site's terms, or
   that applies to everything regardless of fit. If pushed on where the ethical line is: it's
   between "reduce the mechanical cost of a genuine application" and "increase the number of
   applications a recruiter must read."

**What not to do:** don't get defensive, don't dismiss it as "everyone does it", and don't oversell
the guardrails as making it a solved problem. An interviewer asking this wants to see you reason
about externalities, not win the argument.

---

### Q2. [Advanced] 🔥 What's the most dangerous thing this system can do, and what stops it?

**Strong answer covers:** submit a fabricated claim under your name to a company, irreversibly.
Three layers stop it — mechanical verification against the profile (Q5 in
[02-ai-and-llm-engineering.md](02-ai-and-llm-engineering.md)), violation-forced routing to the
review queue, and an abort-on-unfilled-required-field rule in the submitter so an unfamiliar form
never gets a half-empty submission. The second-most dangerous is quieter: applying to the *wrong*
job because a dedupe or scoring error passed it through, which is embarrassing rather than
damaging but has no automatic detection.

---

### Q3. [Intermediate] 🔥 Which single design decision are you proudest of, and which would you reverse?

**Strong answer covers (proudest):** enforcing constraints in code rather than in the prompt. It's
the decision that generalises furthest and it's the one that would still be right if the model
changed tomorrow.

**(Reverse / would revisit):** pick something real, not a humblebrag. Candidates —
- The semantic dedupe key is `company::title` normalised, which merges genuinely distinct roles at
  large companies ("Software Engineer" at three different teams). A location or requisition
  component would help.
- Skip records don't carry the criteria version that produced them, so changing the scoring rubric
  leaves stale negative decisions with no clean way to invalidate them.

---

### Q4. [Intermediate] How do you avoid getting blocked by the sources you pull from?

**Strong answer covers:** retry only what retrying can fix (429/5xx, never 404/401), honour
`retry-after`, one identifying User-Agent, bounded concurrency rather than unbounded fan-out, and
a design that prefers official ATS endpoints over scraping where both exist. Add the honest part:
LinkedIn is ranked lowest partly *because* driving it is fragile and adversarial, and a source
that requires fighting the site is a source whose adapter will break constantly.

---

### Q5. [Intermediate] Talk me through a shell habit from this project that you'd bring to a team.

**Strong answer covers (pick one or two, from `01-shell.md`):**
- **Probing an API before writing code against it** — a `curl` against the real endpoint to see the
  actual response shape beats writing a client from documentation and discovering the mismatch in a
  debugger.
- **Grepping a package's `.d.ts` for its exports** — the fastest authoritative answer to "what does
  this library actually export in the version I have installed," same instinct as reading the
  bundled docs.
- **The caret trap in `package.json`** — `^7.0.0` means the installed version can differ from what
  you think, which is precisely how you end up writing v5-era API calls against a v7 install.
- **Running a typechecker without emitting files** (`tsc --noEmit`) as a distinct check from tests.

The theme to name: **verify against what's actually installed, not against what you remember.**

---

### Q6. [Advanced] Suppose the model provider is down mid-run at 3am. What happens?

**Strong answer covers:** it should degrade, not corrupt. Discovery already succeeded and its
results are persisted, so those jobs are recorded and won't be re-fetched. Scoring/tailoring calls
fail; retryable statuses back off, permanent ones don't. Anything that can't be scored simply
isn't routed — it stays unhandled, so the next run picks it up. The key property is that the
already-handled check is driven by **recorded state transitions**, not by "this run reached this
job", so a partial run leaves a consistent world rather than a half-applied one.

---

### Q7. [Beginner] How would you explain this project to a non-technical hiring manager?

**Strong answer covers:** one sentence on the problem (job searching is mostly mechanical repetition
with a small amount of judgement in the middle), one on what the tool does (finds openings, filters
to genuine fits, drafts a tailored application, and either submits the confident ones or hands the
rest to me), and one on the safeguard (it can only say things that are actually on my CV, and
anything uncertain waits for me). Avoid stack names entirely. If you can't do this version, you
don't understand the project as well as you think.

---

### Q8. [Advanced] What would you need to change to hand this to someone else to use?

**Strong answer covers:** the profile is the ground truth for verification, so onboarding is
entirely "how does a new user express their real experience precisely enough for a mechanical
check?" — a sparse profile makes `verify()` strip legitimate content and flood the review queue,
which reads as the tool being broken. Also: secret handling moves from one env var to real
per-user key storage, per-user rate-limit accounting against shared APIs, and defaults that are
much more conservative than a single-user tool needs, because the person running it may not read
the review queue at all.

---

### Q9. [Intermediate] What did you learn from this project that changed how you build things generally?

**Strong answer covers:** pick one and go deep rather than listing four.
- **"Prompts shape behaviour; code guarantees it"** — the strongest and the one that transfers to
  every LLM feature.
- **Cost-ordered stages** — put the free filter first; the discipline applies to database queries,
  builds, and CI pipelines identically.
- **Design around what you cannot undo** — reversibility, not confidence, is what determines how
  much autonomy an action gets.
