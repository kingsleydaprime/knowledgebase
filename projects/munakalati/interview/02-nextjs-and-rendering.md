# munakalati — Next.js and Rendering

From [[projects/munakalati/learning/04-frontend/README|learning/04-frontend]]. Next **16**, React **19**, App Router. **The strongest angle here is rendering strategy and cache reasoning** — most candidates can describe SSR vs SSG and stop.

---

### Q1. [Beginner] 🔥 What's a route group, and why does this project use one?

**Strong answer covers:** a folder in parentheses — `(site)` — organises files **without adding a URL segment**. `app/(site)/about/page.tsx` serves `/about`.

The reason here: the group carries `layout.tsx` with the Navbar and Footer, so every public page gets the site chrome — and **`/studio` sits outside the group, so the Sanity Studio renders with none of it.** The Studio is a full-screen application; the marketing shell around it would be absurd.

**The alternative you avoided:** without route groups you'd need either a URL prefix like `/site/about`, or a conditional in the root layout checking `pathname` — and conditionals in layouts are how layouts become unreadable.

**Have the full set ready**, because they're easy to confuse: `(group)` is invisible in the URL but still routed; `_private` is **not routed at all**; `[dynamic]` is a parameter; `[[...catchall]]` matches zero or more segments.

---

### Q2. [Intermediate] 🔥 How did you hide an unfinished section without deleting the code?

**Strong answer covers:** renamed `(site)/resources/` to `(site)/_resources/`. **A folder prefixed with `_` is excluded from routing entirely** — the four pages (760 lines of finished work) still live in the repo and still compile; `/resources` is a 404.

**Why that beats the alternatives:** deleting loses the work; a feature flag means shipping runtime branching for something with no users; a branch means the work rots out of sync for months. Restoring is `mv _resources resources` plus two nav links — and the commit message says exactly that.

**Then volunteer the failure**, because it's the better half of the answer: *"It also taught me the limit of the technique. Six links elsewhere still pointed at `/resources/*` and became 404s. Hiding a route doesn't find the links to it — `href` is an untyped string and nothing checks it. Two days later I had a follow-up commit fixing them, and the real fix is one line: `typedRoutes: true` in `next.config.ts` makes an invalid `href` a compile error."*

---

### Q3. [Intermediate] 🔥🔥 What does `export const revalidate = 60` actually do?

**Don't say "it refreshes every 60 seconds."** That's the wrong mental model.

1. The page renders to HTML at build time or on first request.
2. Every visitor for 60 seconds gets that HTML instantly from cache — no Sanity call.
3. After 60s the *next* visitor still gets the **stale** page immediately, and their request triggers a background re-render.
4. The visitor after that gets the fresh one.

**The property that matters: nobody ever waits for a re-render.** Static-file speed with self-updating content.

**The trade:** an editor publishing sees the change between 60 seconds and 60 seconds plus one page view later — and on a page nobody visits, the stale version sits there indefinitely.

**Why 60:** *"Honestly, for a site that changes a few times a week, an hour would be cheaper and just as correct. 60 was chosen for the editor's feedback loop — publish, wait a minute, refresh. The proper answer is webhook revalidation: Sanity fires on publish, a route handler calls `revalidateTag()`, and it's instant with no polling. More moving parts, and where I'd go next."*

---

### Q4. [Advanced] 🔥 Your Sanity client has `useCdn: true` and your pages use ISR. Is that a problem?

**The question is testing whether you can reason about stacked caches.** The answer is "not here, and here's exactly why."

Two caches in the path: Sanity's CDN in front of the dataset, and Next's ISR cache in front of the rendered page. **Worst-case staleness is roughly the sum, not the tighter of the two.**

In practice Sanity's CDN window is seconds and is dominated by the 60-second ISR window, so the re-render pulls content at most a few seconds behind. **Where it would bite is a short revalidate** — `revalidate = 5` with a CDN read can serve content older than the window promises, and that's a genuinely confusing bug because the config *says* five seconds.

**The generalisation:** *"Any time there's a CDN in front of a cache in front of a store, the freshness you actually ship is the sum of the layers. The client's own comment says to set `useCdn: false` when using ISR — I'd follow it, because the correctness argument doesn't depend on the current numbers staying where they are."*

---

### Q5. [Intermediate] 🔥🔥 Show me a performance bug that's invisible in code review.

**The fetch waterfall.** These look nearly identical:

```tsx
const featured = await client.fetch(featuredPostQuery);
const posts    = await client.fetch(pagedPostsQuery, { … });
const total    = await client.fetch(postCountQuery, { … });
```

```tsx
const [featured, posts, total] = await Promise.all([
  client.fetch(featuredPostQuery),
  client.fetch(pagedPostsQuery, { … }),
  client.fetch(postCountQuery, { … }),
]);
```

The first is **three times the latency for identical work**, and nothing about it looks wrong.

**The rule:** `await` sequentially only when the second call needs the first call's result.

**Then show you know the difference from a real dependency** — from the same codebase:

```tsx
const post = await client.fetch(postBySlugQuery, { slug: decoded });
if (!post) notFound();
const related = await client.fetch(relatedPostsQuery, { category: post.category, slug: post.slug.current });
```

*"That one's sequential and correctly so — the related-posts query takes the post's category as a parameter, so it can't start earlier. Telling a waterfall from a genuine data dependency is the whole skill; the fix isn't 'always use `Promise.all`'."*

---

### Q6. [Advanced] Each section component fetches its own data. Good or bad?

**Both, and say both.**

**For:** each section owns its query, its types and its fallback, and can be dropped onto another page with no wiring. Async Server Components make colocated fetching possible without prop-drilling or a client data library. That's real modularity.

**Against:** the homepage makes **eleven requests to Sanity** across eight components. React renders siblings concurrently so they aren't serialised, but it's still eleven round trips where GROQ can express one:

```groq
{ "hero": *[…][0]{…}, "stats": *[…]{…}, "testimonials": *[…]{…} }
```

**The verdict:** *"Here modularity wins, because ISR means those queries run once per 60 seconds, not once per visitor. On a dynamically-rendered page the calculus flips completely. The thing I'd actually flag is that **the cost is invisible** — nobody reading the homepage component can see that it costs eleven queries."*

---

### Q7. [Intermediate] 🔥 Which components are client components, and how did you decide?

**Strong answer covers:** five files in ~10,000 lines — the Navbar (mobile menu toggle), two carousels (timers and index state), and a marquee. **Everything else, including every page and every CMS-backed section, is a Server Component and ships zero JavaScript.**

**The pattern, with the hero as the example:** `cms/Hero.tsx` is an async Server Component that fetches from Sanity, builds image URLs with `urlFor()`, and passes a plain array of `{id, src, alt}` down to `HeroCarousel`, which is the `"use client"` part. **The carousel knows nothing about Sanity, GROQ, or image building — the Sanity client never enters the browser bundle.**

**Two rules the boundary imposes:**

1. **Props crossing it must be serialisable** — no functions, no class instances. Note `urlFor(...).url()` is called on the server; passing the builder object itself would fail.
2. **`"use client"` is a boundary, not a label.** Everything imported below it becomes client code, so one misplaced directive near the root ships the whole tree.

---

### Q8. [Intermediate] What changed in Next 16 that breaks older tutorials?

**Strong answer covers:** **`params` and `searchParams` are Promises.**

```tsx
export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
```

Next 15 deprecated the synchronous form; **16 removed it**. Any code written against 14/15 destructures directly and fails at runtime — this is the single most common Next 16 migration error.

**Why:** accessing a request-time value is what makes a route dynamic, and making it a Promise lets Next render the static parts before the request values are needed.

**Also worth having:** `middleware.ts` → `proxy.ts`, Turbopack as the default bundler, and every export from a `"use server"` file having to be async.

---

### Q9. [Intermediate] 🔥 `searchParams` is user input. What do you do with it?

```tsx
const category = categories.find((c) => c.value === categoryParam)?.value ?? "all";
const page = Math.max(1, parseInt(pageParam ?? "1", 10) || 1);
```

**Strong answer covers: whitelist enumerables, clamp numerics.**

- The category is checked against a **known list**, not passed through — `?category=<script>` becomes `"all"`.
- `parseInt` then `|| 1` catches `NaN` from `?page=abc`; `Math.max(1, …)` catches zero and negatives.

**Why the clamp matters specifically here:** both values flow into a GROQ slice. `?page=-5` would produce `[-60...-48]` — **not an error, just wrong results.** Bound parameters prevent injection; they don't prevent nonsense.

---

### Q10. [Advanced] 🔥 Explain the CMS fallback pattern and its biggest risk.

**Strong answer covers the shape:** every CMS-backed section keeps its original hardcoded content as a `FALLBACK`, plus a **view-model type** and a `toRender()` adapter, so the JSX never learns where the data came from:

```tsx
const testimonials = sanity.length > 0 ? toRender(sanity) : FALLBACK;
```

The key move is that `photoSrc` is a plain string in the view model — fallbacks point at `/public`, CMS entries go through `urlFor()`, and by the time JSX sees it the difference is gone. No `{cms ? … : hardcoded}` branching in the markup.

**Why it exists:** the site was designed and built before the CMS, and the client would populate content later. It decouples frontend work from content entry, and every page is always renderable — this site would survive a Sanity outage looking normal.

**The risk, and this is the answer they're looking for:** *"If a GROQ query breaks — a renamed field, a typo — the fetch returns an empty array and the page renders the fallback **perfectly, with no error**. You lose the CMS integration and the site looks fine. That's worse than a crash, because a crash gets fixed the same day. The one-line fix is to `console.warn` when the fallback fires, so it lands in the platform logs; the stronger version is a `CMS_STRICT` env flag that throws in production and falls back in development."*

**And the honest coda:** *"There's also a `.length > 0` there rather than a null check, deliberately — `client.fetch` on a list query returns `[]`, never null, and an empty array is truthy, so `banners || FALLBACK` would silently render nothing."*

## Related
- [[projects/munakalati/learning/04-frontend/README|learning/04-frontend]]
- [[frontend/02-rendering/README|rendering strategies]] · [[frontend/frameworks/next/README|Next.js]]
