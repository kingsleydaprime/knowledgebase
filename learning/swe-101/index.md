# SWE 101 — Building a Production Codebase, and Graphs Under Pressure

**Status:** active — the one active course (see [[learning/catalogue|catalogue]]) · **Length:** 8 weeks · **Starts:** Monday 2026-10-05
**Where the reps happen:** the board and the physical notebook. This file is the map, not the notes.
**Then:** [[learning/swe-102/index|SWE 102 — AI engineering]] (6 weeks) → [[learning/swe-103/index|SWE 103 — systems and interviews]] (11 weeks).

---

## The SWE series

### The objective

**Land a remote full-stack / AI-engineering role, and be a genuinely better engineer on the way there.**

The target profile is one thing, not two: **a TypeScript full-stack engineer who ships AI product features and can prove they work.** Today's AI-engineering jobs are mostly exactly that — streaming UIs, retrieval, tool calls, evals, cost and latency — and it's where remote junior hiring is still happening. Java/Spring, mobile, embedded and robotics stay parked: a CV aimed at four roles reads as aimed at none.

### Why three short courses instead of one long plan

The first version of SWE 101 was a 30-week scheme beside a 28-week hire track, in four documents. It didn't hold: the weeks weren't followed, reading drifted across the vault, and the two tracks contradicted each other — the flagship needed tests in week 4 and evals in week 9, while the scheme taught them in weeks 24 and 23. (The old files are in [[learning/swe-101/archive/index|the archive]].)

A course you can finish in two months has a finish line you can see — the condition the JAMB result came from. So the series is three courses run **one after another**, each with a measurable finish line:

| Course | Weeks | Finish line |
|---|---|---|
| **SWE 101** — production codebase + graphs | 8 | Flagship deployed, structured, tested in CI, threat-modelled · graph mediums solved cold |
| [[learning/swe-102/index\|SWE 102]] — AI engineering | 6 | Flagship's AI feature has evals running in CI, with numbers you can quote · DP and linked lists cold |
| [[learning/swe-103/index\|SWE 103]] — systems and interviews | 11 | Two system-design mocks and two coding mocks passed · the project story at three lengths |

**Applications never stop for a course.** They already produced the most useful finding so far: the graph questions in real DSA rounds.

### Where I'm starting from

Twelve projects in [[projects/index|projects/]], about 1,150 notes in this vault, and real interviews already taken.

**Already proven — don't re-learn it:** Node/NestJS backends, auth, realtime and a payments ledger (nextvibe, arete, socioboom) · queues, retries, idempotency (socioboom, record-id-generator, direct-debit-sandbox) · Postgres, Supabase, RLS, Prisma (gees-arise, sorepoint, nextvibe) · React, Next, React Native · deployment, CI/CD, Linux, git · published libraries (strictenv, json-healer) · AI SDK, BYOK, agents (my-applicant, socioboom, nextvibe).

**The real gaps, most binding first:**

1. **DSA under interview conditions — graphs, confirmed by real interviews.** Read, typed, but not owned under time pressure.
2. **No flagship.** Twelve projects and no single "start here" a stranger can click.
3. **Evals for AI features.** What separates "built a chatbot" from "AI engineer". → SWE 102
4. **System design out loud, under time.** The notes are written; the reps are zero. → SWE 103
5. **Visibility.** Finished blog drafts unpublished; the Quartz site isn't linked from the CV.

### How every week works

**Four lanes, in priority order.** When a week collapses — and with school in session, some will — drop from the bottom up:

| Lane | Hours | When the week collapses |
|---|---|---|
| **DSA** — two sessions, problems solved cold | ~3 | Never dropped |
| **Apply** — Friday, plus a same-day debrief after any interview | ~1 | Never dropped |
| **Build** — this week's flagship milestone | ~3–4 | Shrinks; never skipped |
| **Learn** — two core lessons and one practice task | 2–4 | Optional lessons go first, then core |

**About 10–12 hours a week.** The rotation is one thing per day, not everything every day:

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|---|---|---|---|---|---|---|
| DSA | Learn | DSA | Build | Apply · Learn practice | Build block | Reconstruct & explain |

**Sunday is not optional.** Close everything and teach the week to the board from memory. It's step 3 of [[learning/02-the-learning-loop|the learning loop]], and the one that gets skipped.

**The rules for each lane:**

- **DSA — solve cold.** Attempt each problem on the board first, for up to 25 minutes. Open its file in [[dsa/neetcode-150/index|NeetCode 150]] only after a real attempt. Log every problem in the notebook: pattern, cold or not, minutes taken. **If you can't restate the pattern on a blank page before starting, you're matching, not knowing.**
- **Learn — core first.** Each week lists two core lessons. Read them, close them, write the notebook page, do the practice task. Optional lessons are for when the audit says **D**.
- **Build — the practice task is the build** wherever a lesson allows it. Studying and building should be the same hours.
- **Apply — write the questions down within the hour.** The graph questions from your last interviews are gone because nobody wrote them down. After any interview, the same day, in the notebook: what was asked, what you tried, where it broke.

**The notebook:** [[learning/swe-101/03-notebook-method|the method]] is unchanged, except that sections are numbered **course.week** — section 101.3 is SWE 101, week 3. Core topics get the full 8-part page; optional topics get one line in the index.

**Week 1's first job is the audit.** Go through every core and optional lesson in this course and mark each **K** (could explain it now, closed book), **H** (met it, would need to look it up) or **D** (don't know it). K → skip it, H → core only, D → core plus optional.

---

## SWE 101 — the eight weeks

**Course finish line, every item checkable:**

- [ ] Flagship deployed at a public URL, with a README that opens with what it does and a GIF
- [ ] Its structure is feature-based, with a lint rule that fails on a cross-feature import
- [ ] Real tests running in CI on every push
- [ ] A written threat model: the top five risks, and what was done about each
- [ ] An architecture note explaining one hard trade-off
- [ ] **Graphs:** three unseen graph mediums, each solved cold in under 30 minutes
- [ ] About 38 DSA problems logged, at least 25 of them cold
- [ ] Applications every Friday; every interview debriefed in writing the same day

### Week 1 — Pick the flagship, and structure it

- **DSA — graphs I, DFS:** 080 number of islands · 082 max area of island · 081 clone graph · 084 surrounded regions · 090 number of connected components. Refresh first, only if needed: [[dsa/04-patterns/11-dfs-pattern|DFS pattern]].
- **Learn (core):** [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|layers]] · [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|layer vs feature]]
- **Learn (optional):** [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/in-compiled-languages|layer vs feature in compiled languages]] · [[software-engineering/01-what-software-engineering-is|what software engineering is]] · [[software-engineering/02-the-software-development-lifecycle|the SDLC]]
- **Build:** **pick the flagship** — harden nextvibe or my-applicant rather than starting fresh. Then the audit, and decide its folder structure.
- **Apply:** Friday hour. Link the Quartz site and the flagship from the CV.
- **By Sunday:** the flagship is named, its structure is drawn on the board, and the audit is done.

### Week 2 — Wire it, and test it

- **DSA — graphs II, BFS:** 085 rotting oranges · 086 walls and gates · 083 Pacific Atlantic water flow · 091 graph valid tree · 092 word ladder. Refresh: [[dsa/04-patterns/12-bfs-pattern|BFS pattern]].
- **Learn (core):** [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|dependency injection and wiring]] · [[concepts/04-best-practices/04-testing-fundamentals/index|testing fundamentals]]
- **Learn (optional):** [[backend/07-practices/02-testing-a-backend|testing a backend]] · [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/in-other-languages|DI in other languages]]
- **Build:** a composition root, a boundary lint rule, and the first real tests running in CI.
- **Apply:** Friday hour.
- **By Sunday:** CI is green on the flagship, and a pull request that breaks a test turns it red.

### Week 3 — Measure the coupling

- **DSA — graphs III, ordering and weights:** 087 course schedule · 088 course schedule II · 089 redundant connection · 095 network delay time · 094 min cost to connect all points. Refresh: [[dsa/02-data-structures/06-graphs/06-algorithms/01-topological-sort|topological sort]] · [[dsa/02-data-structures/06-graphs/06-algorithms/02-dijkstra|Dijkstra]].
- **Learn (core):** [[concepts/04-best-practices/08-coupling-and-cohesion/index|coupling and cohesion]] · [[concepts/04-best-practices/05-solid-principles/index|SOLID]]
- **Learn (optional):** [[concepts/04-best-practices/01-clean-code/index|clean code]]
- **Build:** run the coupling tool on the flagship (`node concepts/04-best-practices/08-coupling-and-cohesion/labs/javascript/coupling.mjs <flagship>/src`). Fix one cycle or one dependency pointing the wrong way.
- **Apply:** Friday hour.
- **By Sunday:** before-and-after coupling output for the flagship, and one graph medium solved cold under 30 minutes.

### Week 4 — Patterns in the core feature

- **DSA — trees:** 048 diameter of binary tree · 053 level order traversal · 054 right side view · 056 validate BST · 058 construct tree from preorder and inorder. Refresh: [[dsa/04-patterns/10-binary-tree-traversal-pattern|binary tree traversal]].
- **Learn (core):** [[concepts/03-design-patterns/03-behavioral-patterns/index|behavioural patterns]] · [[concepts/03-design-patterns/02-structural-patterns/index|structural patterns]]
- **Learn (optional):** [[concepts/03-design-patterns/01-creational-patterns/index|creational patterns]]
- **Build:** the flagship's core feature, end to end. Use one pattern where it genuinely fits — a state machine for a lifecycle, or wrappers around an external API.
- **Apply:** Friday hour.
- **By Sunday:** one sentence on which pattern you used in the flagship, and why it beat the plain version.

### Week 5 — Boundaries that last

- **DSA — backtracking:** 071 subsets · 072 combination sum · 073 permutations · 076 word search · 079 N-queens. Refresh: [[dsa/04-patterns/14-backtracking|backtracking]].
- **Learn (core):** [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|hexagonal architecture]] · [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|modular monolith to services]]
- **Learn (optional):** [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]]
- **Build:** put the one external API most likely to change — payments, email, or the model provider — behind a port, with a fake adapter in tests.
- **Apply:** Friday hour.
- **By Sunday:** the flagship's core logic has a test that runs with no network.

### Week 6 — Hardening

- **DSA — two pointers and sliding window:** 012 3sum · 013 container with most water · 016 longest substring without repeating characters · 017 longest repeating character replacement · 019 minimum window substring.
- **Learn (core):** [[backend/07-practices/01-backend-best-practices/index|backend best practices]] (validation, error contracts, rate limits, idempotency) · [[devops/10-observability/01-observability-fundamentals/index|observability fundamentals]]
- **Learn (optional):** [[devops/10-observability/02-the-observability-stack|the observability stack]]
- **Build:** consistent error responses, rate limits on the expensive routes, and structured logs.
- **Apply:** Friday hour.
- **By Sunday:** you can answer "is it up, is it fast, and what broke last" for the flagship without opening the code.

### Week 7 — Securing what you built

- **DSA — binary search and heaps:** 030 Koko eating bananas · 032 search in rotated sorted array · 066 K closest points · 067 Kth largest element · 070 find median from data stream.
- **Learn (core):** [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation and output encoding]] · [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|security headers and same-origin policy]]
- **Learn (optional):** [[devops/09-secret-management/01-secret-management|secret management]] · [[backend/05-auth/01-authentication-flows|authentication flows]]
- **Build:** threat-model the flagship and fix the top risk.
- **Apply:** Friday hour.
- **By Sunday:** the threat model is written — top five risks, and what was done about each.

### Week 8 — Ship it, and a timed mock

- **DSA — timed mock:** three unseen mediums, 45 minutes each, back to back: 098 cheapest flights within K stops · 068 task scheduler · 131 merge intervals. Score honestly.
- **Learn:** no new lessons. Re-read only what the mock exposed.
- **Build:** README with a GIF and a live URL at the top, the architecture note, and a short write-up you could post.
- **Apply:** Friday hour, with the flagship link in every application from now on.
- **By Sunday:** every box in the course finish line is ticked — or the unticked ones have a date. **Then SWE 102 starts the following Monday.**

---

## If a week goes wrong

- **A week lost to school:** repeat it; don't skip it. The course is 8 weeks of work, not 8 calendar weeks.
- **Graph mocks still failing at week 8:** add a ninth week of graph reps before SWE 102. That's the gap interviews have already exposed, so it outranks everything else in the plan.
- **An interview turns up a new gap:** write it down that day. If it's DSA, it goes into next week's DSA lane. If it's anything else, it goes into the parking lot below, and is checked at the start of the next course.

**Gaps found in interviews, waiting for a slot:**

| Date | Gap | Where it goes |
|---|---|---|
| Before 2026-10-01 | Graph questions in DSA rounds — the questions weren't recorded | SWE 101 weeks 1–3 and the week 8 mock |

## Related

- [[learning/swe-101/03-notebook-method|The notebook method]] · [[learning/swe-101/06-lesson-quality|lesson quality]] — which lessons meet the course standard
- [[learning/02-the-learning-loop|The learning loop]] · [[learning/04-one-active-course|one active course]]
- [[dsa/neetcode-150/interview-playbook|The interview playbook]] — the process to run on every problem, out loud
