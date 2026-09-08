# SocioBoom — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). SocioBoom is a social-media scheduling and content tool — Express +
Prisma + BullMQ backend, Next.js 16 App Router frontend, publishing to X, LinkedIn, Reddit,
Facebook, Instagram and TikTok, with AI-driven review posting and pain-point discovery.

**This is the best project in the vault for two interview tracks:** *AI engineering* (a real agent
with tools, grounding and SSRF defence) and *integration/reliability engineering* (six platform
APIs, OAuth token chains, queues, and idempotent retries).

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked. 🔥🔥 = build your prep around it.

## Files

| File | Covers |
|---|---|
| [01-backend-architecture.md](01-backend-architecture.md) | Express/TS bootstrap, the five-file module pattern, middleware chain, Prisma, auth & security |
| [02-queues-and-deployment.md](02-queues-and-deployment.md) | BullMQ, retries without double-posting, the worker that never ran, health checks, Docker, 502s/CORS |
| [03-ai-and-agents.md](03-ai-and-agents.md) | Provider abstraction, single-shot vs agent loops, forced tool use, URL grounding, SSRF |
| [04-social-publishing-and-media.md](04-social-publishing-and-media.md) | OAuth token chains, Facebook Pages, Instagram containers, TikTok scopes, R2 presigned, Prisma JSON |
| [05-frontend-and-story.md](05-frontend-and-story.md) | App Router, TanStack Query, polling background jobs, honest UI, upload bugs, behavioural |

---

## Before anything else: the 60-second pitch

> SocioBoom schedules and publishes content across six social platforms, with AI features that
> research pain points and draft posts. Express + Prisma + BullMQ on the backend, Next.js 16 on the
> front, R2 for media. Two things I'd want to talk about. First, **retries demand idempotency** —
> the publish worker posts to several platforms in one job, so a naive retry after a partial failure
> would tweet twice; the fix records which platforms already succeeded *inside the job's own data*,
> so a retry resumes rather than repeats. Second, the research agent had a real hallucinated-URL
> bug: it was validating URLs with a regex, and a well-formed invented Reddit link passes a regex
> perfectly. The fix was an **allowlist of URLs the system actually observed** — exact set
> membership, not pattern matching — plus telling the agent when its URL was dropped, which corrects
> it mid-run.

Either half is a complete answer. The URL grounding one is stronger for an AI-focused interview;
the idempotent retry one is stronger for a backend interview.

---

## The five stories to have ready

| Story | One-line hook |
|---|---|
| Retries without double-posting | Adding retries created a worse bug than the one it fixed |
| The worker that never ran | Correct, compiled code that **nothing anywhere started** |
| The hallucinated URL | You cannot validate provenance with a format check |
| Facebook's four-token chain | A Page token inherits the lifetime of the user token it came from |
| Prisma's three-valued JSON | `null`, `undefined` and `DbNull` are three different instructions |
