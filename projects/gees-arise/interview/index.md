# Gees Arise — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). Gees Arise is an accountability app: circles of friends set tasks,
submit proof, audit each other, and take penalties — built on Next.js 16 + Supabase (Postgres, RLS,
Storage, RPC functions, cron).

**This is the strongest project in the vault for database and security questions.** The
[`09-sys-design.md`](../learning/09-sys-design.md) notes contain a genuinely unusual amount of
real Postgres/RLS depth: recursive policy traps, `SECURITY DEFINER` used correctly, partial unique
indexes, triggers as cross-feature glue, and several bugs that no type system could have caught.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked. 🔥🔥 = build your prep around it.

## Files

| File | Covers |
|---|---|
| [01-postgres-rls-and-security.md](01-postgres-rls-and-security.md) | RLS, the recursion trap, `SECURITY DEFINER`, RPC vs policy, storage policies, signed URLs |
| [02-data-modeling-and-invariants.md](02-data-modeling-and-invariants.md) | Rule vs log tables, state machines, constraints over app code, triggers, partial unique indexes, fan-out |
| [03-nextjs-and-frontend.md](03-nextjs-and-frontend.md) | Route groups, Server Components/Actions, the upload-limit story, optimistic UI, stale layouts, Playwright |
| [04-bugs-and-story.md](04-bugs-and-story.md) | The silent bugs, git workflow, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> Gees Arise is a group accountability app — you and a circle of friends commit to tasks, submit
> proof, and the circle audits each other; missed or flagged tasks become penalties, resolved by
> vote. It's Next.js 16 on Supabase, and the interesting engineering is almost entirely in the
> database. Supabase auto-exposes a REST API over every public table with a key that ships in the
> browser bundle, so **the access rules have to live in Postgres, not in my route handlers** —
> otherwise "only circle members can see this" is only true because my app happens to check it.
> That pushed a lot of design into RLS policies, `SECURITY DEFINER` RPC functions for atomic
> multi-table actions, database constraints for the abuse guarantees, and triggers so one feature
> can react to another's writes without either knowing the other exists.

The second half is the pitch. "The security boundary is the database, because the client key is
public" is a one-sentence demonstration that you understand the platform rather than just using it.
