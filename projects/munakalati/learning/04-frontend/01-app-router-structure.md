# Next.js App Router — How This Site Is Laid Out

**Split from:** the munakalati frontend domain. **See also:** [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|02 — data fetching]] · [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|03 — rendering CMS content]]
**General version:** [[frontend/frameworks/next/README|frontend/frameworks/next/]] · [[frontend/03-structuring-a-frontend/01-components-and-composition|structuring a frontend]]

Next.js **16.2.4**, React **19.2.4**, App Router, Tailwind **4**.

---

## The tree

```
src/app/
├── layout.tsx                    # root: <html>, fonts, metadata
├── not-found.tsx                 # 404 — renders its own Navbar/Footer, see below
├── globals.css                   # Tailwind 4 @theme tokens
├── (site)/                       # route group — never appears in a URL
│   ├── layout.tsx                # Navbar + <main> + Footer
│   ├── page.tsx                  # /
│   ├── about/page.tsx            # /about
│   ├── blog/page.tsx             # /blog
│   ├── blog/[slug]/page.tsx      # /blog/anything
│   ├── contact/page.tsx
│   ├── engage/{,creator,donate,partner,volunteer}/page.tsx
│   ├── our-work/{,agency,app,magazine,muna-studio,muna-tv}/page.tsx
│   └── _resources/…              # underscore = private, NOT routed
└── studio/[[...tool]]/page.tsx   # the Sanity Studio SPA
```

**Four of Next's routing conventions are in use here, and each solves a different problem.** Worth learning as a set, because they're easy to confuse:

| Syntax | Name | In the URL? | Used here for |
|---|---|---|---|
| `(site)` | route group | **no** | giving the whole public site one shared shell |
| `[slug]` | dynamic segment | yes | `/blog/<post>` |
| `[[...tool]]` | optional catch-all | yes | handing every `/studio/*` path to one page |
| `_resources` | private folder | **not routed at all** | hiding a finished section from the MVP |

## `(site)` — a route group

Parentheses group files **without adding a URL segment**. `src/app/(site)/about/page.tsx` serves `/about`, not `/(site)/about`.

The payoff is that the group can carry its own layout:

```tsx
// src/app/(site)/layout.tsx
export default function SiteLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      <Footer />
    </>
  );
}
```

Every public page gets the navbar and footer; **`/studio` doesn't**, because it sits outside the group. That's the whole reason the group exists — the Studio is a full-screen application and would look absurd wearing the marketing site's chrome. Without route groups you'd need either a URL prefix like `/site/about` or a conditional in the root layout checking the pathname, and the second is exactly the kind of creeping conditional that makes layouts unreadable.

**The root layout is what everything shares** — `<html>`, the font variables, the metadata:

```tsx
<html lang="en" className={`${baloo.variable} ${nunito.variable}`} suppressHydrationWarning data-scroll-behavior="smooth">
  <body>{children}</body>
</html>
```

### Two things wrong in the root layout, and they're instructive

**Unused imports.** `Navbar` and `Footer` are imported and never rendered — leftovers from before `(site)/layout.tsx` existed. Harmless to output (tree-shaken), but they're a false signal: someone reading the root layout reasonably concludes the nav is global, and it isn't. `next lint` flags this. Two commented-out `next/font` imports (`Fraunces`, `DM_Sans`) sit above them, and `globals.css` opens with a 25-line commented-out block of the `create-next-app` default theme. **Commented-out code is the one kind of comment that reliably lies** — git remembers the old fonts; the file shouldn't have to.

**`suppressHydrationWarning` on `<html>`.** This tells React to ignore server/client mismatches on that element. It's the correct fix for exactly one situation: a browser extension or a pre-hydration theme script mutating `<html>` before React attaches. Commit `f0c8510` added it "for improved rendering stability", alongside adding it to `Partners`, which suggests it was reached for to silence a warning rather than after diagnosing one.

**It's worth being precise about why that's risky**: the attribute suppresses the warning *one level deep* on that element, so on `<html>` it's fairly contained. But the habit is the problem — a hydration warning is React telling you the server HTML and the first client render disagree, which is a real bug (usually `Date.now()`, `Math.random()`, or `localStorage` read during render). Suppressing it hides the symptom and leaves the mismatch. **Diagnose first; suppress only when you know which external mutation you're suppressing.**

## `_resources` — the underscore trick

Commit `42f3e19` cut the Resources section from the MVP:

```
src/app/(site)/{resources => _resources}/media-library/page.tsx | 0
src/app/(site)/{resources => _resources}/page.tsx               | 0
src/app/(site)/{resources => _resources}/publications/page.tsx  | 0
src/app/(site)/{resources => _resources}/toolkits/page.tsx      | 0
src/components/layout/Navbar.tsx                                | 2 --
```

**A folder prefixed with `_` is a "private folder"** — Next excludes it and everything under it from routing entirely. The four pages (760 lines of finished work) still compile and still live in the repo; `/resources` is a 404.

**This is the right way to hide an unfinished feature**, and better than the alternatives:

- *Deleting it* loses the work and makes restoring it a git archaeology exercise.
- *A feature flag* means shipping the code and adding runtime branching for something with no users.
- *A branch* means the work rots out of sync with `main` for months.

Restoring is `mv _resources resources` plus re-adding two nav links. The commit message says exactly that: *"Easy to restore when the section is ready."* **A reversible change with the reversal written down in the commit message** — the pattern worth copying.

**The trap it left behind, though**, is the subject of [[projects/munakalati/learning/06-bugs-and-postmortems|06]]: six links elsewhere in the site still pointed at `/resources/*`, and un-routing the pages turned them into 404s. Hiding a route does not find the links to it. Commit `3442c85` cleaned them up two days later.

### `_` vs `(...)` vs `[...]` — the disambiguation

Easy to mix up, and the difference is total:

- **`(group)`** — organisational, invisible in the URL, **still routed**.
- **`_private`** — **not routed at all**. Use for colocating components, utilities, or, as here, parked pages.
- **`[dynamic]`** — a URL parameter.

## `not-found.tsx` at the root, and why it repeats itself

```tsx
// src/app/not-found.tsx
export default function NotFound() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-cream flex flex-col">…</main>
      <Footer />
    </>
  );
}
```

It renders `Navbar` and `Footer` **itself**, duplicating `(site)/layout.tsx`. That looks like a mistake and isn't: `not-found.tsx` lives at `src/app/`, outside the `(site)` group, so it only inherits the *root* layout — which has no chrome. Without the duplication, a 404 would be a bare page with no way to navigate away.

**The alternative** is a second `not-found.tsx` *inside* `(site)/`, which would inherit that group's layout and need no duplication. The root one would still be needed for anything outside the group. Six duplicated lines versus an extra file — genuinely a coin flip, and worth knowing both exist.

`notFound()` from `next/navigation`, called in the blog detail page, is what routes to this. It throws a special error Next catches and turns into the nearest `not-found.tsx` with a 404 status — **the status code matters**, because a "not found" page served as 200 gets indexed as a real page. Added late, in commit `ec37af7`; before that, an unknown slug got Next's default 404.

## Server and Client Components: where the boundary sits

**Everything is a Server Component unless it says otherwise.** Exactly five files in `src/` carry `"use client"`:

```
src/components/home/cms/HeroCarousel.tsx
src/components/home/Hero.tsx
src/components/home/Partners.tsx
src/components/layout/Navbar.tsx
src/components/PartnerLogoGrid.tsx
```

Navbar (mobile menu toggle), the carousels (timers and state), the marquee. **Everything else — every page, every CMS-backed section — runs only on the server and ships zero JavaScript.** For a content site that's the correct default and most of why it should feel fast.

The hero shows the pattern done properly:

```tsx
// cms/Hero.tsx — Server Component: async, fetches, no "use client"
export default async function Hero() {
  const [content, banners] = await Promise.all([
    client.fetch<HeroContent | null>(heroContentQuery),
    client.fetch<HeroBanner[]>(heroBannersQuery),
  ]);

  const panels = banners.length > 0
    ? banners.map((b) => ({ id: b._id, src: urlFor(b.image).width(1400).url(), alt: b.image.alt ?? "" }))
    : FALLBACK_PANELS;

  return (
    <section>
      {/* …static headline, CTAs — server-rendered, no JS… */}
      <HeroCarousel panels={panels} />
    </section>
  );
}
```

```tsx
// cms/HeroCarousel.tsx — Client Component: the interactive part only
"use client";
export default function HeroCarousel({ panels }: { panels: Panel[] }) {
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  // …auto-advance timer, prev/next…
}
```

**Fetch on the server, pass plain serialisable data down, keep the client component as small as the interaction requires.** The carousel receives an array of `{id, src, alt}` — it knows nothing about Sanity, GROQ, or image URL building. The Sanity client never enters the browser bundle.

**Two rules the boundary imposes**, both easy to trip over:

1. **Props crossing the boundary must be serialisable.** Plain objects, arrays, strings, numbers. No functions, no class instances, no `Date`. Note `urlFor(...).url()` is called *on the server* — passing the builder object itself would fail.
2. **`"use client"` is a boundary, not a label.** Everything imported by a client component becomes client code too. One misplaced directive high in the tree drags the subtree with it — which is why the directive is on `HeroCarousel` and not on `Hero`.

A small wrinkle in that list: `src/components/home/Hero.tsx` (the non-CMS one) is `"use client"` while `cms/Hero.tsx` is a Server Component. Both exist; the page imports the CMS one. See [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|03]] for the duplicate-component situation.

## Fonts

```tsx
const baloo  = Baloo_2({ subsets: ["latin"], variable: "--font-display", display: "swap" });
const nunito = Nunito({ subsets: ["latin"], variable: "--font-body",   display: "swap" });
```

`next/font/google` **downloads the font at build time and self-hosts it**. No runtime request to `fonts.googleapis.com` — which removes a third-party round trip on the critical path, removes a privacy/GDPR consideration, and lets Next inline a size-adjusted fallback so the swap doesn't shift layout.

`variable:` exposes each as a CSS custom property, applied to `<html>`, and Tailwind 4's `@theme` block binds them to utility classes:

```css
@theme {
  --font-display: "Baloo 2", sans-serif;
  --font-body: "Nunito", sans-serif;
  --color-primary: #E8500A;
  /* … */
}
```

So `className="font-display"` and `className="text-primary"` are generated from the same token list the CSS uses. **Tailwind 4's big change is exactly this** — the theme is CSS custom properties in a `@theme` block rather than a JavaScript `tailwind.config.js`. `display: "swap"` shows the fallback immediately rather than blocking text on the font download.

## Related
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — the `/resources` 404 cascade]]
- [[frontend/02-rendering/02-hydration-and-the-server-boundary|the server boundary]] — the concept behind `"use client"`
- [[frontend/05-styling/01-css-architecture|CSS architecture]] — design tokens
