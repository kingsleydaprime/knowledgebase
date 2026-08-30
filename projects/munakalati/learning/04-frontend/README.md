# 04 — Frontend

**The Next.js half of [[projects/munakalati/learning/README|munakalati]].** Next **16.2.4**, React **19.2.4**, App Router, Tailwind **4** — a content site where nearly everything is a Server Component and almost no JavaScript ships.

1. [[projects/munakalati/learning/04-frontend/01-app-router-structure|01 — App Router Structure]] — **[Beginner → Intermediate]** — route groups vs private folders vs dynamic segments vs optional catch-all, **`_resources` as the way to park a finished feature**, why `not-found.tsx` repeats the chrome, where the `"use client"` boundary sits, Tailwind 4 `@theme` tokens
2. [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|02 — Data Fetching, ISR and Caching]] ⭐ — **[Intermediate]** — what `revalidate = 60` actually does, **stacked caches compose their staleness**, `Promise.all` vs a genuine data dependency, eleven fetches on one page, the `generateStaticParams` 20-post cap, **`params`/`searchParams` are Promises in Next 16**
3. [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|03 — Rendering CMS Content: The Fallback Pattern]] ⭐ — **[Intermediate]** — the view-model adapter that makes JSX source-agnostic, why an empty array is truthy, **the safety net hides the fall**, and the `cms/` duplication a finished migration left behind

## The three things to take away

**Sequential `await`s on independent data is the most common Server Component performance bug**, and nothing about the code looks wrong.

**A fallback that renders perfectly when the CMS query breaks is worse than a crash.** Log when it fires.

**A migration scaffold needs a demolition date.** Nine components exist twice, and the dead half still compiles.

## Related
- General: [[frontend/frameworks/next/README|Next.js]] · [[frontend/02-rendering/README|rendering]] · [[frontend/04-state-and-data/README|state and data]]
- [[projects/munakalati/learning/03-sanity/README|03 — Sanity]] — where the data comes from
- [[projects/munakalati/interview/02-nextjs-and-rendering|interview: Next.js and rendering]]
