# Sanity

**A full course — 3 notes.** The headless CMS: a hosted document store, a query language of its own, and a schema that doubles as the editing UI.

Sanity is the **implementation**; the framework-agnostic half — what a headless CMS is for, and how to model content — lives in [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|04 — content modelling and headless CMS]]. Read that first if you've never modelled content before.

## The notes

1. [[frontend/frameworks/sanity/01-the-sanity-model|01 — The Sanity Model]] — **[Beginner → Intermediate]** — projects, datasets and **the API version that's a date**, schemas as JS, `useCdn` and when it must be `false`, singletons as convention, **`required()` is a form check, not a constraint**, the embedded Studio
2. [[frontend/frameworks/sanity/02-groq|02 — GROQ]] ⭐ — **[Beginner → Intermediate]** — the three parts of every query, `->` as the entire join story, **the projection is the optimisation**, parameters vs. injection, conditional filters, `count()` and pagination
3. [[frontend/frameworks/sanity/03-portable-text-and-images|03 — Portable Text and Images]] — **[Intermediate]** — why rich text isn't HTML, blocks/spans/marks/**`markDefs` indirection**, the four renderer buckets, asset references, hotspots, the URL builder, stacking two CDNs

## The one idea

**Sanity is a hosted document database whose schema is written in JavaScript and generates its own admin UI.** It has no opinion about presentation — that split is what "headless" means, and everything else follows from it.

Three consequences worth holding onto:

- **Your schema is three artifacts at once** — validation, the editor's form, and the only documentation a non-technical editor will ever read. A skipped `description` is an instruction never delivered.
- **`required()` is enforced by the Studio, not the API.** Anything written by a script or a migration can violate it. Guard in the query with `defined()`.
- **The projection, not the filter, is where query performance lives.** GROQ returns the shape you ask for; ask for less.

## Where the material actually is

**~7,000 words against real code** — 16 document types, 24 queries, and 434 posts migrated in from Wix:

- [[projects/munakalati/learning/03-sanity/README|munakalati — Sanity]] *(5 notes)*
- [[projects/munakalati/learning/05-migration/README|munakalati — the Wix→Sanity migration]] *(5 notes)* — the harder half

## Related
- [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modelling and headless CMS]] — the concepts this implements
- [[frontend/frameworks/next/README|Next.js]] — the framework it's usually paired with
- [[frontend/frameworks/README|frameworks/]]
