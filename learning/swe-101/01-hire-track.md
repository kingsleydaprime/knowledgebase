# Track A — Hire

> Weeks 1–28. The track that produces the offer. At 10–15 h/week this is roughly 8–10 of those hours.

**The one rule:** this track wins every conflict with [[learning/swe-101/02-foundation-track|Track B]]. When a week collapses, DSA and applications survive.

---

## The weekly rotation

JAMB shape — one thing per day, fixed, not everything every day.

| Day | Focus | Hours |
|---|---|---|
| **Mon** | DSA — one pattern, 2–3 problems | 1.5 |
| **Tue** | Foundation topic (Track B) | 1.5 |
| **Wed** | DSA — same pattern, cold | 1.5 |
| **Thu** | Build — flagship | 1.5 |
| **Fri** | **Applications + outreach** | 1 |
| **Sat** | Build block | 3–4 |
| **Sun** | Reconstruct & explain — close everything, teach the week from memory | 1 |

≈ 11–12 hours. Sunday is not optional; it's step 3 of [[learning/02-the-learning-loop|the loop]] and it's the one that gets skipped.

**Friday is non-negotiable from week 7.** An hour a week of applying, forever, beats a heroic month of it later.

---

## Phase 0 — Audit and artifacts · weeks 1–2

Before any studying. These are the things that are worth more per hour than anything else in the plan, because they're already 90% done and just aren't visible.

- [ ] **Pick the flagship.** One project a stranger can click. Recommendation: **harden nextvibe or my-applicant rather than starting fresh** — a new build costs 8 weeks to reach where these already are.
- [ ] **Publish the three blog drafts** sitting in `blog-drafts/` — `four-bugs-that-shipped`, `socket-race-condition`, `reading-a-datasheet`. These are exactly the posts that get a remote junior noticed: specific, debugged, real. They are finished. Publishing them is an evening.
- [ ] **CV** — one page, targeted at TS full-stack + AI product. Projects, not coursework.
- [ ] **GitHub** — pin 4 repos, real READMEs with a screenshot/GIF and a live URL at the top. A repo with no README is invisible.
- [ ] **LinkedIn/X** — headline says what you build, not what you're studying.
- [ ] **Make the Quartz site discoverable** — link it from GitHub, CV, LinkedIn. 1,150 notes published is a genuine differentiator and right now nobody hiring can find it.
- [ ] **DSA baseline** — sit 3 unseen mediums, 45 min each, cold. Score honestly. This calibrates everything.

## Phase 1 — DSA, continuously · weeks 1–28

**Not a block. Never dropped.** Two sessions a week for the whole track, because a skill crammed in weeks 8–12 is gone by week 30.

Method is [[learning/02-the-learning-loop|yours]] and doesn't change:

> Study 1–2 worked solutions → extract *what makes it that kind of problem* → **close them** → solve new ones cold. Never copy a third.

Work through [[foundations/dsa/06-patterns/README|the 15 patterns]] already written here. One pattern per week, roughly:

arrays/hashing → two pointers → sliding window → binary search → stack → linked list → trees/BFS/DFS → heap → backtracking → graphs → intervals → greedy → DP (2 weeks) → tries → bit manipulation

**Target: 150 problems, ~60% medium.** Log every one in the notebook with pattern, whether it was cold, and time taken. The log is the visible progress — this is the board.

**Track the tell:** if you can't restate the pattern on a blank page before starting a problem, you're pattern-*matching*, not pattern-*knowing*.

## Phase 2 — The flagship · weeks 3–12

One project, shipped properly. Not five half-projects.

**What it has to have**, in order:

1. Deployed, with a URL a stranger can open — no local-only
2. A README that opens with what it does and a GIF
3. Real tests, running in CI
4. **An LLM feature with an evals harness** ← the differentiator
5. An architecture note explaining one hard trade-off you made
6. Observability — you can answer "is it up, and is it fast"

**Item 4 is the whole point.** A golden set, a scoring function, a regression run on every prompt change, and numbers you can quote. Almost nobody applying to junior AI roles has this. [[ai-ml/03-ai-engineer/12-evals|The note is already written]] — this is the reps for it.

Milestones (each independently shippable, per [[build-your-own-shit/README|the build-guide rule]]):
- **w3–4** — scope, deploy the skeleton to production on day one, CI green
- **w5–6** — the core feature end to end
- **w7–8** — the AI feature working
- **w9–10** — **evals**: golden set, scorer, CI regression
- **w11** — hardening: errors, rate limits, cost/latency numbers
- **w12** — README, architecture note, demo GIF, ship the write-up

## Phase 3 — Apply, from week 7 · weeks 7–28

**Start before it feels ready. This is the instruction most likely to be ignored, and the one that costs the most.**

Applying is not the reward for finishing. It's a diagnostic you cannot get any other way: rejections tell you which gap is actually binding, and that's information that changes what you study. Waiting until the portfolio is perfect means finding out in month 9 what you could have found out in month 2.

- **Weeks 7–12:** 5/week. Learning the machinery — CVs, cover notes, take-homes, what gets replies.
- **Weeks 13–28:** 10/week. Volume. **Target 100 by week 20.**
- **Fridays**, every week, one hour. Non-negotiable.

Where remote juniors actually get hired: AI-product startups (small, portfolio-led, often skip LeetCode for a take-home), YC company job boards, Wellfound, remote-first job boards, and — highest hit rate of all — **being visible**: writing, shipping in public, being useful in a Discord/GitHub for a tool you actually use.

Keep a spreadsheet: company, date, source, stage, outcome. **Track reply rate.** Below ~5% after 30 applications, the CV or the targeting is wrong, not the market.

## Phase 4 — Interview reps · weeks 12–28

Runs alongside applications, not after.

- **Coding rounds** — the DSA log is the prep; add timed mock sessions from week 12
- **System design** — [[architecture/interview/01-system-design-round|the round]], then one design per fortnight from [[learning/swe-101/02-foundation-track|Track B]]'s list, **out loud, whiteboard, 45 minutes**
- **The project story** — [[projects/nextvibe/interview/05-platform-payments-and-story|nextvibe's story bank]] is the model. Be able to tell the flagship in 2 minutes, 5 minutes, and 20 minutes of depth.
- **Behavioural** — 6 stories, STAR, from real projects. Remote roles probe async communication hard.
- **The banks already exist** — [[INTERVIEW|13 domains]]. Cover the answer, say it out loud, then compare. Recognition is not knowledge.

**After every real interview**, in the notebook: what was asked, what I fumbled, what I'll fix. This is the highest-value page in the book.

---

## What "on track" looks like

| Week | Should be true |
|---|---|
| 2 | Blog posts live, CV done, GitHub pinned, DSA baseline scored |
| 7 | Flagship deployed and CI green · **first applications out** |
| 12 | Flagship has evals · 30 DSA problems · applications weekly |
| 20 | 100 applications · 90 problems · interviews happening |
| 28 | 150 problems · loops in progress |

**If week 7 arrives and nothing has been applied to, that's the failure mode this whole restructure exists to prevent.** Not the DSA count. The applications.
