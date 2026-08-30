# 03 — Sanity

**The CMS half of [[projects/munakalati/learning/README|munakalati]].** Five notes, in reading order.

Sanity is the domain this project taught most thoroughly — a headless CMS is the first place many frontend developers meet **content modelling** as a design activity in its own right, separate from both database design and component design.

1. [[projects/munakalati/learning/03-sanity/01-setup-and-mental-model|01 — Setup and the Mental Model]] — **[Beginner]** — projectId/dataset/apiVersion/token, **why the API version is a date**, `useCdn` and when it must be `false`, the two-client split
2. [[projects/munakalati/learning/03-sanity/02-schema-design|02 — Schema Design]] ⭐ — **[Beginner → Intermediate]** — the sixteen types and the four shapes they fall into, the `order` pattern, **singletons as a convention not a feature**, `required()` is a form check and not a constraint, presentation leaking into the content layer, and how the hand-written types drifted
3. [[projects/munakalati/learning/03-sanity/03-groq-queries|03 — GROQ]] ⭐ — **[Beginner → Intermediate]** — the three parts of every query, `->` as the whole join story, **the projection is the optimisation**, parameters vs. injection, conditional filters, and two dead queries found by grep
4. [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|04 — Images and Portable Text]] — **[Intermediate]** — asset references, `hotspot`, the `urlFor` chain, two CDNs in the path, **why rich text isn't HTML**, `markDefs` indirection, the four renderer buckets
5. [[projects/munakalati/learning/03-sanity/05-embedded-studio-and-structure|05 — The Embedded Studio and Structure Builder]] — **[Intermediate]** — `[[...tool]]` optional catch-all, `ssr: false` and keeping the Studio out of the site bundle, singletons in the sidebar, Vision

## The three things to take away

**A headless CMS is a database whose schema doubles as its admin UI and its documentation.** Every `title` and `description` you skip is an instruction an editor never receives.

**`required()` in a schema is a form check, not a constraint.** Anything that entered through the API — every one of the 434 migrated posts — can violate it. Guard in the query with `defined()`.

**The projection is where GROQ performance lives.** Swapping a 20-field projection for `{"slug": slug.current}` was the fix in commit `f2b69dc`, not a change to the filter.

## Related
- General: [[frontend/frameworks/sanity/README|frontend/frameworks/sanity/]] · [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modeling and headless CMS]]
- [[projects/munakalati/learning/05-migration/README|05 — the migration]] — how the content got in
- [[projects/munakalati/interview/01-sanity-and-content-modeling|interview: Sanity and content modelling]]
