# System design — my-applicant

The architectural ideas in this project that generalise beyond it.

---

## Separate the pipeline into stages with different costs

```
discover  →  prefilter  →  score   →  tailor  →  route
(network)    (free)        (cheap    (expensive  (free)
                            LLM)      LLM)
```

The ordering isn't arbitrary — each stage is deliberately cheaper than the one
after it, and its job is to **reduce what the next stage sees**.

- `prefilter` is pure local string matching. It costs nothing, so it runs
  before any model call and removes obviously-wrong jobs (title contains
  "intern", location doesn't match).
- `score` is a batched LLM call — cheap per job.
- `tailor` is a large LLM call per job, and only runs for jobs above
  `minScore`.

The design rule: **put the cheap filter before the expensive one, and make the
expensive stage's input as small as you can.** A tenfold reduction at the free
stage is a tenfold saving at the paid stage.

This is the same shape as a database query planner pushing predicates down, or
a build system checking timestamps before recompiling.

---

## Idempotency is what makes unattended work safe

The tool is meant to run at 3am with nobody watching. That imposes one hard
requirement: **running it twice must not do the work twice.**

The database provides it:

```ts
if (store.isAlreadyHandled(job.id)) continue;   // submitted | queued | skipped
```

Jobs are recorded on discovery; applications are recorded at every state
change. A crashed run can be re-run with no special recovery logic — the
already-handled check absorbs the overlap.

Notice `skipped` is in that set. A job scored below threshold is recorded as
deliberately skipped, not left absent — otherwise every future run would
re-score it and pay for the same judgement repeatedly. **Recording a negative
decision is as valuable as recording a positive one.**

---

## Dedupe with a semantic key, not just an ID

Source-assigned IDs are useless across sources: the same job is
`greenhouse:stripe:12345` and `remotive:98765`.

So there's a second key:

```ts
export function jobKey(job) {
  const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ').trim();
  return `${norm(job.company)}::${norm(job.title)}`;
}
```

And when two sources collide, the higher-ranked one wins:

```
ATS (3) > HackerNews (2) > aggregators (1) > LinkedIn (0)
```

The ranking isn't about data quality — it's about **capability**. Only the ATS
record carries a driveable application form. Keeping the Remotive echo of a
Greenhouse job would silently demote an auto-appliable job into the manual
queue. When deduping, prefer the record that can do the most, not the one that
arrived first.

---

## Enforce constraints in code, not in the prompt

The most important idea in this project.

The tailoring prompt says "do not invent skills". That's a **request**. The
model usually complies. Usually isn't good enough when the failure mode is a
fabricated line on a resume you have to defend in an interview.

So after generation, `verify()` checks every claim against the profile and
strips what doesn't match:

```ts
const canonical = knownSkills.get(skill.toLowerCase().trim());
if (canonical) { keep(canonical); }
else { violations.push({ kind: 'unknown-skill', ... }); }
```

Three properties worth copying:

1. **The check is mechanical.** It compares against a set, with no judgement.
2. **Violations are surfaced, not swallowed.** A model that keeps inventing
   skills is information — about the model, or about a too-sparse profile.
3. **Violations change the routing.** Any violation forces the application
   into the review queue even in auto mode. A model that fabricated one thing
   may have fabricated another the checker can't see.

Generalise: **when an LLM output feeds an irreversible action, validate it
against ground truth you control.** Prompts shape behaviour; code guarantees it.

---

## Design around what you cannot undo

The autonomy tiering follows entirely from one asymmetry:

- A queued application costs ~10 seconds of review.
- A wrongly submitted application **cannot be unsent**, and carries your name.

Given that, every ambiguous case should queue. So the routing function queues
on: an unfamiliar source, a scorer concern, a tailoring violation, a missing
PDF, a per-run ceiling, *and* a failed submission attempt.

The same principle inside `submit.ts`:

```ts
// Bail on anything required that is still empty.
if (unfilled.length > 0) return { ok: false, reason: '...' };
```

An unfamiliar form aborts rather than submitting something half-empty. The
default behaviour on confusion is **stop**, not **guess**.

Ask of any automated action: *what does a wrong call cost, and can I take it
back?* Cheap and reversible → automate freely. Expensive and irreversible →
make the machine ask.

---

## Let one failing component degrade, not collapse

`Promise.allSettled`, not `Promise.all`:

```ts
const settled = await Promise.allSettled(sources.map((s) => s.fetch(ctx)));
```

`Promise.all` rejects the moment any promise rejects — one stale LinkedIn
selector or one typo'd board slug would sink the entire night's run.
`allSettled` waits for all of them and reports each outcome, so a broken
adapter costs you that source's jobs and nothing else.

The errors are collected and reported rather than discarded — visible, but not
fatal. Same idea in the PDF renderer: a PDF failure returns `pdfError` and the
Markdown and HTML still get written, because a missing PDF is a degraded
result, not a failed application.

**Decide per-component whether a failure is fatal or degrading.** Most are
degrading, and `Promise.all` doesn't let you say so.

---

## Retry only what retrying can fix

```ts
const retryable = res.status === 429 || res.status >= 500;
```

429 (rate limited) and 5xx (server problems) are transient — waiting helps.
404 and 401 are **permanent**: a wrong board slug or a revoked key will still
be wrong in two seconds. Retrying those is pure noise, and hammering a public
API on a permanent error is how an IP gets blocked.

Also worth copying: honour the server's own guidance when it gives it.

```ts
const retryAfter = Number(res.headers.get('retry-after'));
```

If a server tells you when to come back, that beats your exponential backoff
guess.
