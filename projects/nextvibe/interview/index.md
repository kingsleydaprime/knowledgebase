# NextVibe — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). NextVibe is a full-stack events/social platform — NestJS + Prisma
backend, Next.js App Router frontend, Socket.IO realtime, payments, AI-generated games.

It's the **largest** project in the vault, and the learning notes are unusually full of *named
bugs with root causes* — which is exactly what senior interviews are made of.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked. 🔥🔥 = build your prep around it.

## Files

| File | Covers |
|---|---|
| [01-backend-nestjs-core.md](01-backend-nestjs-core.md) | Modules/DI, controllers, validation, route ordering, Prisma gotchas, transactions, lifecycle |
| [02-auth-and-security.md](02-auth-and-security.md) | JWT, `@Public()` opt-out guard, multi-role tokens, cookies vs Redux, redirect bugs |
| [03-realtime-and-notifications.md](03-realtime-and-notifications.md) | WebSocket auth, ws/wss/Socket.IO, gateway errors, producer/consumer split, dedup, badges |
| [04-frontend-nextjs-and-state.md](04-frontend-nextjs-and-state.md) | App Router, server vs client, middleware, Suspense, RTK Query cache tags, forms, uploads |
| [05-platform-payments-and-story.md](05-platform-payments-and-story.md) | Deployment, MinIO/presigned URLs, OOM, webhooks, AI games, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> NextVibe is an events platform — organisers create events, sell tickets, run AI-generated games
> for attendees, and everyone gets realtime messaging and notifications. NestJS + Prisma +
> PostgreSQL on the backend, Next.js App Router with Redux Toolkit and RTK Query on the frontend,
> Socket.IO for realtime, MinIO/S3 for media with presigned uploads, and OpenRouter so any model can
> back the game generation. The things I'd want to talk about are the bugs, because they're the kind
> that don't throw: Prisma treats `undefined` in a `where` clause as "no filter", so an
> unparsed JWT made brand-new users appear to have thousands of followers; and the notification
> system that "didn't work" had perfectly functioning plumbing — the producer calls had simply never
> been written, which a single grep diagnosed.

Both of those are silent-failure stories with a crisp root cause. That's the register to pitch in.

---

## The bug shortlist (know these five cold)

| Bug | Root cause | Lesson |
|---|---|---|
| Thousands of phantom followers | `undefined` in a Prisma `where` = **no filter at all** | Validate identifiers before they reach the query |
| `GET /users/me` → 404 | `@Get(':id')` declared before `@Get('me')`; `:id` matched `"me"` | Static routes before parameterised ones |
| Sockets die after 15 min | `js-cookie` `expires` is in **days**; `1/96` = 15 minutes | Two login paths setting cookies two different ways |
| Notifications never appear | The producer side was never written | Find which *end* of a pipeline is broken before poking the middle |
| AI generation OOMs on 512 MB | Holding whole payloads in memory on a small dyno | Memory is a platform constraint, not an afterthought |
