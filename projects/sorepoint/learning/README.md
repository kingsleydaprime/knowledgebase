# Sorepoint — Learning Notes

Learning journal for **Sorepoint**, a system that scans local businesses, finds
each one's single worst fixable flaw (six competing "agents", one winner), and
builds + mails the fix. Product spec and build plan live in the app repo at
`~/code/spectroniq/sorepoint/docs/` (`SPEC.md`, `PLAN.md`).

> On the name: "Sorepoint" = a *sore point*, the one painful problem. Chosen
> 2026-07-31 after checking npm + web for collisions (see `shell.md`).

## How these files are organised

One file per domain, teaching *why* not just *what changed*, beginner → advanced.
Files get a number prefix once a domain grows into an actual reading sequence;
for now they stay flat and unnumbered until there's enough to order.

Domains expected to come into play (created only as work actually touches them):

- `shell.md` — command-line techniques used along the way *(started)*
- `supabase.md` — Postgres schema, RLS, TypeGen, the data model *(started)*
- `backend.md` — the pipeline worker (Places pull → crawl → agents → rank)
- `sys-design.md` — why worker-not-route, cache-first/resumable, evidence-weighted ranking
- `frontend.md` — the Next.js dashboard, honest coverage UI *(started)*
- `git.md`, `testing.md` — as those come up

Nothing here is a stub-for-the-sake-of-it — a file appears when there's real,
earned content to put in it.
