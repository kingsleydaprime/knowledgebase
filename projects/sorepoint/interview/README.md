# Sorepoint — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). Sorepoint scans local businesses, finds each one's single worst
fixable flaw via six competing "agents", and builds + mails the fix.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked.

## Files

| File | Covers |
|---|---|
| [01-pipeline-and-crawling.md](01-pipeline-and-crawling.md) | Worker-not-route, source adapters, OSM, cache-first/resumable, the crawler, honest failures |
| [02-postgres-and-supabase.md](02-postgres-and-supabase.md) | Local stack on rootless Podman, migrations, TypeGen, GRANTs vs RLS, idempotent upserts |
| [03-product-decisions-and-story.md](03-product-decisions-and-story.md) | Honest UI, evidence-weighted ranking, the ethics of unsolicited outreach, behavioural |

---

## Before anything else: the 60-second pitch

> Sorepoint scans local businesses in a city+niche, and for each one identifies the single worst
> *fixable* flaw — six agents compete on evidence, one wins — then builds the fix and mails it. The
> pipeline runs as a standalone worker script writing to Postgres, not as an API route, because the
> external calls outlive a serverless request and have to be resumable. Two things I'd defend
> hardest: every source sits behind one normalised interface, which is what let us swap Google
> Places for OpenStreetMap in an afternoon when billing blocked us; and the whole system is built
> to be **honest about what it doesn't know** — a signal we couldn't determine is `null`, never a
> defaulted `false`, and a site that blocked our crawler is recorded as evidence about *us*, not as
> a flaw of theirs.

The "null, not false" line is the one to lead with. It's a one-sentence demonstration of data
integrity thinking.
