# munakalati — Learning Notes

**Next.js 16 + Sanity CMS**, built for Muna Kalati / MunaWorld — a Cameroon-founded organisation building African children's media. **The content-migration project**: 434 blog posts moved from Wix into Sanity, which is where nearly all the interesting engineering lives.

Written up at handover (August 2026), so these notes are retrospective and include the things you only see on the way out — the dead code, the standing bugs, and the three files that were never committed.

## Reading order

1. [[projects/munakalati/learning/01-git|01 — Git]] — two remotes, sync merges, and **a `.gitignore` that excluded the main migration script** → general: [[git/README|the git course]]
2. [[projects/munakalati/learning/02-shell|02 — Shell]] — bun as an ops runner, `curl` before code, the audit commands used to write these notes, heredoc technique → [[devops/01-linux/README|linux]]
3. [[projects/munakalati/learning/03-sanity/README|03 — Sanity]] ⭐ *(5 notes)* — setup, schema design, GROQ, images and Portable Text, the embedded Studio → [[frontend/frameworks/sanity/README|frameworks/sanity]]
4. [[projects/munakalati/learning/04-frontend/README|04 — Frontend]] *(3 notes)* — App Router structure, ISR and fetch waterfalls, **the CMS fallback pattern** → [[frontend/README|frontend]] · [[frontend/frameworks/next/README|next]]
5. [[projects/munakalati/learning/05-migration/README|05 — Migration]] ⭐ *(5 notes)* — the whole Wix→Sanity story: anatomy, reading a hostile API, idempotency and reruns, rich-text conversion, repair scripts → [[concepts/04-best-practices/06-data-migrations|data migrations]]
6. [[projects/munakalati/learning/06-bugs-and-postmortems|06 — Bugs and Postmortems]] ⭐ — six real failures written up end to end, plus a standing-issues table
7. [[projects/munakalati/learning/07-study-path|07 — Study Path]] — what this exercised, what it didn't, and the five things to do next

## The stack

| | |
|---|---|
| **Framework** | Next.js 16.2.4, React 19.2.4, App Router, React Compiler on |
| **Styling** | Tailwind 4 (`@theme` tokens), `next/font` self-hosting Baloo 2 + Nunito |
| **CMS** | Sanity 5 — 16 document types, Studio embedded at `/studio` |
| **Runtime** | bun (scripts), Vercel (deploy) |
| **Source system** | Wix Blog API v3 — 434 posts |
| **Scale** | ~9,900 lines, 45 commits, 2 contributors |

## If you read one thing

[[projects/munakalati/learning/06-bugs-and-postmortems|06 — Bugs and Postmortems]]. **Five of its six failures were silent** — no exception, no failing build, just wrong output that looked right. The slug encoding saga in particular (three commits to get one thing right) is the best single story this project produced.

## The five things worth remembering

**Normalise at the boundary, in the idempotent direction.** Decoded is safe to apply twice; encoded is not.

**An ID scheme is a contract with your own future re-runs.** Changing it mid-migration turned 434 posts into 868.

**`fetch` resolves on 401** — and a pagination bug that under-fetches raises nothing at all. Reconcile counts before you transform.

**The default must be safe.** `bun run dedup` previews; `bun run dedup:apply` destroys.

**A fallback that renders perfectly when the query breaks is worse than a crash.** Log when the safety net fires.

## Also here
- [[projects/munakalati/interview/README|interview/]] — the same material as questions with model answers

## Related
- [[projects/README|All projects and the domains they exercise]]
- [[projects/gees-arise/learning/README|gees-arise]] — the other Next.js project, where the depth is auth and Postgres RLS rather than content and migration
