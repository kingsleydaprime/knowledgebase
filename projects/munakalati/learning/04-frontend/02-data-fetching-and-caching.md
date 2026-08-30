# Data Fetching, ISR and Caching

**Split from:** the munakalati frontend domain. **See also:** [[projects/munakalati/learning/04-frontend/01-app-router-structure|01 — App Router structure]] · [[projects/munakalati/learning/03-sanity/03-groq-queries|sanity/03 — the queries themselves]]
**General version:** [[frontend/02-rendering/01-rendering-strategies|rendering strategies]] · [[frontend/04-state-and-data/02-data-fetching-and-server-state|data fetching and server state]]

---

## `export const revalidate = 60` — what it actually does

This line appears in nine files: every CMS-backed page and several CMS-backed components.

```ts
export const revalidate = 60;
```

It selects **ISR — Incremental Static Regeneration** — and the mechanic is worth getting exactly right, because "it refreshes every 60 seconds" is a misleading summary:

1. The page is rendered to HTML at build time (or on first request).
2. Every visitor for the next 60 seconds gets that HTML **instantly, from cache**. No Sanity call.
3. After 60s, the *next* visitor still gets the **stale** page immediately — and their request triggers a background re-render.
4. The visitor *after that* gets the fresh one.

**Nobody ever waits for a re-render.** That's the property that makes ISR the right default for a content site: static-file speed, with content that updates on its own. The trade is that an editor publishing in the Studio sees their change on the live site somewhere between 60 seconds and 60 seconds plus one page view later — and if nobody visits, the stale page can sit there indefinitely.

**Why 60 and not 3600?** For a marketing site whose content changes a few times a week, an hour would be perfectly defensible and cheaper. 60s is chosen for the *editor's* experience — publish, wait a minute, refresh, see it. That's a reasonable priority, and worth recognising as a deliberate trade of infrastructure cost against editorial feedback speed rather than an arbitrary number.

The alternative Sanity offers is **tag-based revalidation**: a webhook from Sanity hits a Next route on publish, which calls `revalidateTag()` and invalidates precisely the affected pages. Instant updates, no polling, no arbitrary window. More moving parts — a webhook, a secret, a route handler — and worth it once "60 seconds" stops being good enough.

## The `useCdn: true` / ISR interaction

`src/sanity/lib/client.ts` sets `useCdn: true`, directly under a comment saying *"Set to false if statically generating pages, using ISR or tag-based revalidation"* — and the pages do use ISR.

**Two caches are now stacked:** Sanity's CDN in front of the dataset, and Next's ISR cache in front of the rendered page. Worst-case staleness is roughly the sum.

In practice it's benign here, and it's worth understanding *why* rather than just noting the contradiction: Sanity's CDN staleness window is on the order of seconds, and it's dominated by the 60-second ISR window. The re-render fires after 60s and pulls content that's at most a few seconds behind. The bug it *would* cause is on a short revalidate — `revalidate = 5` with a CDN read could genuinely serve content older than the window promises.

**The general lesson is the one about layered caches:** each layer's staleness composes with the next, and the guarantee you actually ship is the sum, not the tightest one. Any time you have a CDN in front of a cache in front of a store, work out the total before promising a freshness window.

## `Promise.all` — the waterfall you don't see until you look

```tsx
// blog/page.tsx
const [featured, posts, total]: [Post, Post[], number] = await Promise.all([
  client.fetch(featuredPostQuery),
  client.fetch(pagedPostsQuery, { category, featuredId: "", start, end }),
  client.fetch(postCountQuery, { category }),
]);
```

Three independent queries, one round-trip's worth of latency. Written the obvious way —

```tsx
const featured = await client.fetch(featuredPostQuery);   // ~100ms
const posts    = await client.fetch(pagedPostsQuery, …);  // ~100ms  (starts after)
const total    = await client.fetch(postCountQuery, …);   // ~100ms  (starts after)
```

— it's three times the latency for identical work, and **nothing in the code looks wrong.** This is the single most common performance bug in Server Components, and it's invisible in code review unless you're specifically watching for sequential `await`s on independent data.

**The rule:** `await` sequentially only when the second call *needs* the first call's result. Otherwise `Promise.all`. `cms/Hero.tsx` does the same thing correctly for its two queries.

**The counter-example is in the same file.** `blog/[slug]/page.tsx`:

```tsx
let post: Post = await client.fetch(postBySlugQuery, { slug: decoded });
if (!post && decoded !== slug) post = await client.fetch(postBySlugQuery, { slug });
if (!post) notFound();

const related: Post[] = await client.fetch(relatedPostsQuery, {
  category: post.category,     // ← needs the post
  slug: post.slug.current,
});
```

Sequential, and **correctly so** — `relatedPostsQuery` takes the post's category as a parameter, so it cannot start earlier. That's a genuine data dependency, not a waterfall. The distinction is the whole skill.

(The second fetch is the slug-decoding fallback → [[projects/munakalati/learning/06-bugs-and-postmortems|06]]. It only runs on a miss, so the common path is one query.)

## Component-level fetching, and the fan-out it creates

The homepage is a Server Component that renders eleven section components:

```tsx
export default function HomePage() {
  return (
    <>
      <Hero /> <StatsStrip /> <Mission /> <Initiatives /> <VideoOverview />
      <Testimonials /> <InMedia /> <BlogPreview /> <Partners /> <DonateCTA />
    </>
  );
}
```

**The page itself fetches nothing.** Each CMS-backed section fetches its own data:

```tsx
export default async function Testimonials() {
  const sanity = await client.fetch<Testimonial[]>(testimonialsQuery);
  const testimonials = sanity.length > 0 ? toRender(sanity) : FALLBACK;
  // …
}
```

**For:** each section is self-contained — it owns its query, its types and its fallback, and you can drop it onto another page with no wiring. That's real modularity, and it's a genuine strength of async Server Components: colocated data fetching without prop-drilling and without a client-side data library.

**Against:** the homepage makes **eleven separate requests to Sanity** across eight components (`Hero` and `InMedia` and `BlogPreview` make two each). React renders sibling Server Components concurrently, so they aren't serialised — but they're still eleven round trips instead of one combined GROQ query returning a key per section:

```groq
{
  "hero": *[_type == "heroContent" && _id == "heroContent"][0]{ … },
  "stats": *[_type == "stat" && context == "home"] | order(order asc){ … },
  "testimonials": *[_type == "testimonial"] | order(order asc){ … }
}
```

GROQ makes that trivially expressible — an object projection at the top level with a query per key, one request, one round trip. **This is the classic modularity-vs-round-trips trade**, and here modularity is arguably the right call: ISR means these queries run once per 60 seconds, not once per visitor, so the cost is negligible. On a dynamically-rendered page the calculus flips completely.

Worth naming as the thing to watch for: **the number of fetches on a page is invisible when each component fetches its own data.** Nobody reading `HomePage` can see that it costs seven queries.

## `revalidate` on components

Several of these components export `revalidate = 60` themselves. **Route segment config is only read from `page.tsx` and `layout.tsx`** — an export from a component file is inert. It's harmless, and it's cargo-culted: the pages that render these components already set it, which is what actually applies.

Not worth a refactor; worth knowing so you don't spend twenty minutes wondering why changing it in a component has no effect.

## `generateStaticParams` — and the cap that wasn't

```tsx
export async function generateStaticParams() {
  const slugs: { slug: string }[] = await client.fetch(allSlugQuery);
  return slugs.map(({ slug }) => ({ slug }));
}
```

This tells Next which dynamic routes to pre-render at build time. Every returned slug becomes a static page in the build output; anything not listed is rendered on first request and then cached (ISR's default fallback behaviour).

**The version before commit `f2b69dc` was importantly broken:**

```tsx
const posts: Post[] = await client.fetch(allPostsQuery);   // ← [0...20], full documents
return posts.map((post) => ({ slug: post.slug.current }));
```

`allPostsQuery` is capped at `[0...20]` and selects every field — body, cover image, author. So it **fetched twenty complete blog posts in order to extract twenty strings**, and with 434 posts in the dataset, only the 20 most recent were ever pre-rendered. The other 414 fell back to on-demand rendering.

The replacement query is three lines and fixes both:

```groq
*[_type == "post" && defined(slug.current)]{ "slug": slug.current }
```

No cap, and a projection of one string per document — roughly 40 bytes instead of several kilobytes each.

**Two habits from this.** First: *a query written for one purpose is usually wrong for another.* `allPostsQuery` was written for a listing page where 20 recent posts is correct; reused for `generateStaticParams` the same limit is a silent bug. Second: **build-time fetches deserve the same scrutiny as request-time ones.** Nobody watches the build for performance, which is exactly why a 20× over-fetch sat there unnoticed.

## `searchParams` and `params` are async in Next 16

```tsx
export default async function BlogPage({
  searchParams,
}: { searchParams: Promise<{ page?: string; category?: string }> }) {
  const { page: pageParam, category: categoryParam } = await searchParams;
```

```tsx
export default async function BlogPostPage({
  params,
}: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
```

**Both are Promises now.** Next 15 deprecated the synchronous form; **Next 16 removed it**. Any tutorial or generated code written against 14/15 will destructure them directly and fail — and this is the single most common Next 16 migration error.

The reason is streaming: accessing a request-time value is what makes a route dynamic, and making it a Promise lets Next start rendering the static parts before the request values are needed.

**Validate them, always** — they're user input:

```tsx
const category = categories.find((c) => c.value === categoryParam)?.value ?? "all";
const page = Math.max(1, parseInt(pageParam ?? "1", 10) || 1);
```

The category is checked against a **known list** rather than passed through — so `?category=<script>` becomes `"all"`. The page number is parsed, `|| 1` catches `NaN` (`parseInt("abc")`), and `Math.max(1, …)` catches negatives and zero. `?page=-5` would otherwise produce a GROQ slice of `[-60...-48]`, which is not an error — just wrong results.

**That's the pattern: whitelist enumerables, clamp numerics.** Both parameters flow into a GROQ query, and while bound parameters prevent injection, they don't prevent nonsense.

## Related
- [[projects/munakalati/learning/03-sanity/03-groq-queries|sanity/03 — GROQ]] · [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|03 — the fallback pattern]]
- [[frontend/02-rendering/01-rendering-strategies|rendering strategies]] — CSR/SSR/SSG/ISR
- [[architecture/02-building-blocks/02-caching|caching]] — layered caches and staleness
