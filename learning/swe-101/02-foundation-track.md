# Track B — Foundation

> Weeks 1–52+. Your original 15 phases, re-sequenced for job relevance and mapped onto notes that already exist. Roughly 2–4 h/week — the Tuesday slot, plus whatever Saturday has left.

**This track continues past employment.** It always was going to. Treating it as a prerequisite for applying is what pushed the original plan to 52 weeks before a single CV went out.

---

## What got cut, and why

Not a criticism of the scheme — it's a well-built *beginner-to-senior* curriculum. It's just aimed at someone who isn't you.

| Original | Weeks | Verdict |
|---|---|---|
| **Phase 1** — what is software / SDLC / types of engineer | 1 | **Cut.** You are one, across twelve projects. One evening skimming SDLC vocabulary for interviews, not a week. |
| **Phase 2–3** — computational thinking, complexity | 2–3 | **Folded into DSA.** Big-O and recursion get learned *through* problems, not before them. |
| **Phase 4–7** — variables, loops, functions, OOP | 4–7 | **Cut.** Four weeks on material nextvibe and the Java projects already prove. The single largest saving in the plan. |
| **Phase 5** — Git, Linux, tooling | 13–14 | **Cut to a checklist.** You use these daily; [[git/README|git/]] and [[devops/01-linux/README|linux/]] are written. Skim for gaps only. |
| **Phase 10** — testing | 30–32 | **Compressed to 1 week.** `gees-arise/learning/07-testing` and the strictenv/json-healer banks show this is owned. |
| **Phase 12** — DevOps | 38–41 | **Compressed to 1 week.** nextvibe/socioboom/gees-arise all have deployment notes; the vault's own CI/CD is yours. |
| **Phase 15** — projects | 49–52 | **Moved to week 3** and made the flagship. Projects are not the graduation ceremony. |

**Net saving: about 20 weeks**, all of it spent proving things already proven.

---

## The re-sequenced order

Re-ordered on one principle: **what gets asked in an interview and what makes the flagship better comes first.** Depth-for-its-own-sake comes after the offer.

| # | Topic | Weeks | Read | Why here |
|---|---|---|---|---|
| 1 | **Software design** — modularity, coupling/cohesion, SOLID, patterns, DI, layering, clean architecture | 3 | [[concepts/03-design-patterns/README\|patterns]] · [[concepts/04-best-practices/README\|best practices]] · [[backend/03-structuring-a-backend/README\|structuring a backend]] | First because it improves the flagship *while you build it*, and code-quality questions start at junior level |
| 2 | **Architecture & system design** | 4 | [[architecture/01-system-design-fundamentals/README\|fundamentals]] · [[architecture/02-building-blocks/README\|building blocks]] · [[architecture/interview/01-system-design-round\|the round]] | Moved from week 45. It's an interview round from junior upward — cannot be at the end |
| 3 | **Databases, deep** — internals, indexes, transactions, MVCC, query plans | 3 | [[databases/README\|the course]] (01–10) · [[databases/interview/README\|bank]] | You use Postgres daily without seeing underneath. `EXPLAIN ANALYZE` is the highest-value single skill here |
| 4 | **Networking & web** | 4 | [[foundations/networking/README\|the course]] · [[foundations/networking/interview/README\|bank]] | "What happens when you type google.com" is still asked. Also underpins every latency question |
| 5 | **Security** | 2 | [[cybersecurity/04-web-security/README\|web security]] · [[cybersecurity/05-cryptography/README\|crypto]] · [[cybersecurity/interview/README\|bank]] | Moved from week 42. Small, high-yield, and **prompt injection is an AI-engineering interview question** |
| 6 | **Backend consolidation** — API design, authz, caching, rate limiting, jobs, versioning | 2 | [[backend/README\|backend]] · [[backend/05-auth/README\|auth]] | Mostly consolidation of what you've shipped — reconstruct, don't relearn |
| 7 | **AI engineering depth** — RAG, agents, **evals**, cost/latency, structured output | 4 | [[ai-ml/03-ai-engineer/README\|the track]], Part II especially [[ai-ml/03-ai-engineer/12-evals\|12-evals]] | **Not in the original scheme at all**, and it's half your target role |
| 8 | **Testing & quality** | 1 | [[concepts/04-best-practices/README\|practices]] · [[concepts/interview/01-apis-auth-and-practices\|bank]] | Compressed — gap-fill only |
| 9 | **DevOps & deployment** | 1 | [[devops/README\|devops]] · [[devops/06-ci-cd/README\|CI/CD]] | Compressed — gap-fill only |
| 10 | **Concurrency & distributed systems** | 5 | [[architecture/04-distributed-systems/README\|the 15-note course]] | Kept deep, moved late. Genuinely valuable, rarely decisive for a first offer |
| 11 | **CS spine** — OS, complexity, architecture | ongoing | [[foundations/os/README\|OS]] · [[foundations/theory-of-computation/README\|theory]] · [[foundations/computer-architecture/README\|architecture]] | Post-offer. This is the "understand why software is built this way" objective, and it has no deadline |

**≈ 29 weeks of foundation, running under a 28-week hire track**, then item 11 continues indefinitely.

---

## System design exercises

Your list, kept as-is — it's the right list. One per fortnight from week 12, **out loud, on the board, 45 minutes, before reading anything.**

URL shortener → chat app → notification system → payment system → social feed → ride-sharing → video platform

Then compare against [[architecture/README|the notes]]. The gap between your answer and the note is the actual lesson; write only that gap in the notebook.

**Do the payment system one carefully** — you built a payments ledger in nextvibe and a direct-debit sandbox in Java. That's a design question you can answer from experience rather than theory, and interviewers can hear the difference.

---

## The design exercise from your scheme

> *Design a banking system. Don't code it. Think about entities, relationships, responsibilities, interfaces, data, failures, security, scalability.*

Keep this exactly as written. It's the best single exercise in the original document, and "don't code it" is the instruction that makes it work.
