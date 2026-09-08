# Arete — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). Arete is a gamified habit/quest app — NestJS 11 + Prisma +
PostgreSQL + Redis + BullMQ on the backend, Expo SDK 54 / React Native on mobile.

It's the most *complete* project in the vault — a real backend, a real mobile app, real cron jobs,
and four documented production bugs from launch week. The postmortems are the strongest interview
material you own for a senior conversation.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked. 🔥🔥 = build your prep around it.

## Files

| File | Covers |
|---|---|
| [01-backend-and-data.md](01-backend-and-data.md) | NestJS structure, guards/DTOs, Prisma, transactions, auth, JWT, background jobs |
| [02-patterns-and-postmortems.md](02-patterns-and-postmortems.md) | Guarded decrement, idempotency, ledgers, determinism, caching — and the four launch-week bugs |
| [03-mobile-react-native.md](03-mobile-react-native.md) | Expo Router, Zustand, the axios refresh queue, timers, optimistic UI, push, deep links |
| [04-devops-and-shell.md](04-devops-and-shell.md) | Docker/Podman, Prisma migrations, seeding, grep/find/sed/awk, regex dialects |
| [05-product-and-story.md](05-product-and-story.md) | Product logic, streaks, trade-offs, behavioural questions |

---

## Before anything else: the 60-second pitch

> Arete is a gamified self-improvement app — daily quests across pillars, XP, streaks, leaderboards
> — with a NestJS/Prisma/Postgres backend, Redis for caching, BullMQ for scheduled work, and an
> Expo React Native client. The parts I'd want to talk about are the concurrency and correctness
> patterns: spending gems is a **guarded decrement** — the condition lives inside the `UPDATE`
> statement, so two parallel purchases can never both pass the check; XP and streaks are stored as
> an append-only **ledger** as well as counters, so the system can answer "did this already count?"
> and derive inventory without new columns; and daily mission assignment uses **deterministic
> hashing** rather than randomness, so it rotates daily and never changes on refresh, with zero
> storage. Launch week produced four bugs worth talking about — including a cache key without a user
> id that served one user's leaderboard position to everyone.

The guarded decrement and the cache-key bug are the two to lead with. One shows you can prevent a
race; the other shows you can find one.

---

## The four launch-week bugs (memorise the one-liners)

| Bug | One-line cause | One-line lesson |
|---|---|---|
| Seed race | `[].map()` produced an empty transaction that **succeeded** | Ask what an empty collection does to a write loop |
| Shared-cache leak | Per-user field cached under a global key | Before every `cache.set`, ask "is any field per-user?" |
| Disagreeing rankings | Two formulas computing one number | A number shown twice must be computed once |
| Inert rate limiter | Configured but never enforced | Configuration is not enforcement — test the limit |

These four are worth more in an interview than any feature you built.
