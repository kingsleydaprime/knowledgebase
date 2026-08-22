# SWE 101

**Started:** 2026-08-21 · **Status:** active (the one active course — see [[learning/catalogue|catalogue]])
**Where the reps happen:** physical notebook + the board. This folder is the map, not the notes.

---

## 1. Objective

**Land a remote full-stack / AI-engineering role, and be a genuinely better engineer on the way there — in that order of urgency, not that order of importance.**

Measurable version, so there's something to tick:

| Target | By |
|---|---|
| 150 DSA problems solved cold, by pattern | week 28 |
| 1 flagship project deployed, tested, with an evals harness, publicly linkable | week 12 |
| 100 applications sent | week 20 |
| 5 real interview loops entered | week 24 |
| Offer | month 6–9 |

## 2. What the role actually involves

Two targets, and they converge — this is the important realisation:

**Full-stack (TS)** and **AI engineering** are not two prep surfaces. Today's AI-engineering job is overwhelmingly *a TypeScript full-stack engineer who ships LLM product features* — streaming UIs, RAG, agents, tool calls, evals, cost and latency control. That is nextvibe's games/AI work, my-applicant's BYOK pipeline, and socioboom's agents, already.

So the profile is one thing:

> **A TS full-stack engineer who ships AI product features and can prove they work.**

That's also the answer to "remote juniors don't get hired." Generic junior full-stack, remote, is the most competitive segment in the market. The AI-product angle is where remote junior hiring is actually still happening, and it's where the existing portfolio is unusually strong for someone with no full-time role yet.

**Parked, not dropped** — Java/Spring, mobile, embedded/hardware, robotics. All real, all evidenced, none of them on the CV for *this* job search. A CV aimed at four roles reads as aimed at none. See [[learning/04-one-active-course|One Active Course]].

## 3. Honest timeline

**10–15 focused hours/week, school in session, remote-first, no full-time experience yet: 6–9 months to offer.**

That's not a softer version of the 52-week plan — it's the same duration, spent differently. The 52-week scheme wasn't wrong about how long this takes. It was wrong about *ordering*: it put projects at week 49 and applications nowhere at all.

**What remote-first specifically costs, and it is a real cost:**
- No referral network by default → public artifacts have to do the work a referral would
- Competing globally, not locally → the DSA bar is higher at the companies that pay well
- Remote hiring skews senior, because junior mentorship is expensive over async → the portfolio has to close that gap
- Slower loops, more silence, more rejection volume

**What's already in hand for it:** WAT is UTC+1, which is clean overlap with EU and workable with US East mornings. Written English is strong. And there's a published Quartz knowledgebase, which almost no junior applicant has.

## 4. Where I'm starting from

**Not week one.** Twelve projects in [[projects/README|projects/]], ~1,150 notes in this vault. The audit below is evidence-based, not self-assessment — it's what the project notes actually show.

### Strong evidence — do not re-learn this

| Area | Where it's proven |
|---|---|
| Node / NestJS backend, auth, realtime, payments ledger | nextvibe (142k words), arete, socioboom |
| Queues, async, retries, idempotency | socioboom, record-id-generator, direct-debit-sandbox |
| Postgres / Supabase / RLS / Prisma, data modelling | gees-arise, sorepoint, nextvibe |
| React / Next / React Native | gees-arise, nextvibe, arete |
| **Testing** | `gees-arise/learning/07-testing`, strictenv + json-healer testing/packaging banks |
| **Deployment, CI/CD, Linux, git** | nextvibe `09-devops`, socioboom `08-devops-and-deployment`, gees-arise `08-devops` |
| Library design + packaging | strictenv, json-healer (both published) |
| AI SDK, BYOK, agents | my-applicant, socioboom, nextvibe |

**This is why Phases 1–7 of the original scheme get cut, and Phases 10 and 12 get compressed.** Seven weeks on variables, loops and inheritance, and a fresh testing phase at week 30, are weeks spent proving something the repos already prove.

### Real gaps — this is what the course is actually for

1. **DSA under interview conditions.** Read, typed, not owned. The #1 blocker for remote.
2. **Evals for AI features.** Two incidental mentions across twelve projects. The single highest-leverage gap, because it's the thing that separates "built a chatbot" from "AI engineer."
3. **Public visibility.** Three finished blog drafts unpublished. The Quartz site isn't linked from anywhere a hiring manager looks.
4. **System design articulation under time pressure.** [[architecture/README|The notes]] are excellent; the reps are zero.
5. **Application volume.** Zero. This is a gap, not a later step.
6. **A single flagship a stranger can click.** Twelve projects, no clear "start here."

## 5. The two tracks

The whole restructure is this: **one track produces the job, the other produces the engineer. They run in parallel, and the first one is front-loaded.**

**Start here in week 1: [[learning/swe-101/05-week-1-audit|the audit]]** — 148 topics, tick K/H/D, and it decides how long every week below actually takes.

**The syllabus itself — [[learning/swe-101/04-scheme-of-work|the scheme of work]]** — is the unit-by-unit outline you write into the notebook: 12 units plus a DSA section, each with its textbook chapters, topic list, exercise and closed-book question.

- **[[learning/swe-101/01-hire-track|Track A — Hire]]** · weeks 1–28. DSA continuously, flagship shipped by week 12, applications from week 7. This is what gets the offer.
- **[[learning/swe-101/02-foundation-track|Track B — Foundation]]** · weeks 1–52+. The original 15 phases, re-sequenced and mapped onto the vault. Continues after employment — most of it always was going to.

**Track A wins every conflict.** In a week where school eats everything, DSA and applications survive; the foundation reading is what gets dropped. Naming that in advance is what stops it being decided by whichever felt more interesting on the day.

## 6. The notebook

[[learning/swe-101/03-notebook-method|The method]] — the 8-part topic structure, and the rule that keeps this notebook from duplicating 1,150 notes that already exist.

## 7. Review

Every 4 weeks, in the notebook, three lines: what's ticked, what slipped, what changes. Not a journal — a checkpoint. The first one that says "applications: 0" is the one that matters.
