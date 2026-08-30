# 01 — Frontend (Next.js 16, React 19, Tailwind v4)

Part of the [[projects/kingsley-iheme/learning/README|kingsley-iheme learning log]]. Siblings: [[projects/kingsley-iheme/learning/02-sanity|02-sanity]] · [[projects/kingsley-iheme/learning/03-backend-api|03-backend-api]] · [[projects/kingsley-iheme/learning/04-devops|04-devops]].

General reference for the same material: [[frontend/frameworks/next/README|frontend/frameworks/next]] and [[frontend/frameworks/react/README|react]]. This file teaches it as it showed up here — Next **16** specifically, with real files.

---

## 0. The rule that made this project different: read the shipped docs

The repo's `AGENTS.md` says one thing:

> This is NOT the Next.js you know. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code.

That's not paranoia. Next ships its own documentation *inside the installed package*, versioned with the code you actually have:

```bash
# the docs that match YOUR installed version, not a blog post from 2023
ls node_modules/next/dist/docs/01-app/01-getting-started/

# every breaking change from 15 → 16, straight from the horse's mouth
grep -n '^#\{2,3\} ' node_modules/next/dist/docs/01-app/02-guides/upgrading/version-16.md
```

That second command lists ~35 headings. Writing these notes, it corrected things I would otherwise have written from memory — see §3 and §5. **This generalises**: `node_modules/<pkg>/` frequently contains the real README, the real types, and sometimes the real docs. It is the closest primary source you have without leaving your machine, and it can't be out of date, because it *is* your version.

Related habit in [[projects/gees-arise/learning/09-sys-design|gees-arise]]: this same reflex caught Next 16's `middleware` → `proxy` rename.

---

## 1. Route groups: folders that shape the layout tree without touching the URL

```
src/app/
├── layout.tsx              ← root layout: <html>, <body>, fonts, global metadata
├── (site)/
│   ├── layout.tsx          ← header + footer + motion provider
│   ├── page.tsx            → /
│   ├── about/page.tsx      → /about
│   ├── blog/page.tsx       → /blog
│   └── ...
├── (studio)/
│   └── studio/[[...tool]]  → /studio     ← Sanity Studio, NO header/footer
└── api/contact/route.ts    → /api/contact
```

A folder wrapped in parentheses is a **route group**. It participates in the layout tree but contributes *nothing* to the URL. `(site)/about/page.tsx` serves `/about`, not `/(site)/about`.

**Why it exists here, concretely.** The site needs a header and footer on every page. The embedded Sanity Studio at `/studio` must have *neither* — it's a full-screen application with its own chrome, and wrapping it in the site header would look broken and steal keyboard focus. Without route groups you'd have exactly two bad options:

1. Put header/footer in the root layout and then fight to hide them on `/studio` (needs a client component reading `usePathname()`, which drags interactivity into your outermost layout for a purely structural problem).
2. Repeat `<Header/>` and `<Footer/>` in every single page file.

Route groups make it structural instead. Two sibling groups, two different layout chains, one URL space.

```tsx
// src/app/(site)/layout.tsx — applies to every site page, and only site pages
const SiteLayout = ({ children }: { children: React.ReactNode }) => (
  <MotionProvider>
    <Header />
    <main className="flex-1">{children}</main>
    <Footer />
  </MotionProvider>
);
```

**The generalisable idea:** a route group is how you say *"these routes share a shell"* without that statement leaking into the URL. Reach for one whenever a subset of routes needs a different wrapper — marketing vs. app, authed vs. public, admin vs. site.

**Layout composition note.** The root layout sets `min-h-full flex flex-col` on `<body>`, and `(site)/layout.tsx` gives `<main>` a `flex-1`. That pair is what pins the footer to the bottom of short pages without `position: absolute` hacks: body is a full-height column, main absorbs all leftover space. It only works because *both halves* are present — a footer that mysteriously floats up the page is nearly always one of these two classes missing.

---

## 2. The Server/Client boundary — and the thing that surprised me

Every component in the App Router is a **Server Component** by default: it runs at build or request time on the server, never ships its JavaScript to the browser, and can be `async`. Adding `"use client"` at the top of a file opts it and its import subtree into the browser bundle.

Actual split in this project (17 components):

```bash
# classify every component by whether it opens with "use client"
for f in $(find src/components -type f | sort); do
  [ "$(head -1 "$f")" = '"use client";' ] && tag=CLIENT || tag=server
  printf "%-8s %s\n" "$tag" "$f"
done
```

| Client (5) | Why it genuinely needs the browser |
|---|---|
| `header.tsx` | `usePathname()` for active-link state, `useState` for the mobile menu, a scroll listener |
| `contact-form.tsx` | `useState` + `onSubmit` + `fetch` |
| `counseling-booking.tsx` | `useState` for the selected session type |
| `cal-booking.tsx` | `useEffect` to configure a third-party embed |
| `fade-in.tsx` / `motion-provider.tsx` | animation needs the DOM |

Everything else — cards, containers, page headers, the whole of `/about` — is a Server Component, ships zero JS, and renders to static HTML.

### The surprise: `"use client"` is inherited, not declared

`search-input.tsx`, `select-input.tsx` and `pagination.tsx` have **no `"use client"` directive** — yet all three take function props and wire up `onClick`/`onChange` handlers:

```tsx
// src/components/pagination.tsx — no directive at the top of this file
export function Pagination({ page, totalPages, onChange }: {
  page: number; totalPages: number; onChange: (page: number) => void;
}) {
  ...
  <button onClick={() => onChange(page - 1)} disabled={page <= 1}>Prev</button>
}
```

This works, and understanding *why* is the single most important mental-model correction in the App Router.

**`"use client"` does not mark a component as a Client Component. It marks a *boundary*.** It says: "from this import onwards, everything is client." Files below that boundary in the import graph get pulled into the client bundle automatically, no directive needed. `Pagination` is only ever imported by `blog-list.tsx`, which *does* declare `"use client"` — so `Pagination` is compiled as a Client Component by inheritance.

The corollary is what actually bites people: **a component with no directive is not "a Server Component." It's *unmarked*, and it becomes whichever kind its importer is.** The same file can compile as a Server Component in one route and a Client Component in another. The directive count is not the client-bundle count.

The practical rule: put `"use client"` as deep in the tree as you can. Here, `blog-list.tsx` is the boundary and the *page* stays a Server Component that does the Sanity fetch. Pushing the boundary one level up — into `blog/page.tsx` — would ship the data fetching to the browser and lose the server render entirely.

### Server fetches, client filters — the composition pattern

```tsx
// src/app/(site)/blog/page.tsx — SERVER: fetches, renders shell
export default async function BlogPage() {
  const posts = await sanityFetch<Post[]>(ALL_POSTS_QUERY, {}, []);
  return <Container>{posts.length === 0 ? <EmptyState/> : <BlogList posts={posts} />}</Container>;
}
```

```tsx
// src/app/(site)/blog/blog-list.tsx — CLIENT: search, filter, paginate
"use client";
export function BlogList({ posts }: { posts: Post[] }) {
  const [query, setQuery] = useState("");
  ...
}
```

The server does the network I/O and hands finished data across the boundary as props. The client does the interactivity. This is the App Router's central idiom and it's worth internalising as a shape, not a rule: **fetch high (server), interact low (client), pass data down across the boundary.**

**Its limit, which this project is quietly sitting on.** `BlogList` receives *every* post and filters in memory:

```tsx
const filtered = useMemo(() => posts.filter((post) => {
  const haystack = `${post.title} ${post.excerpt}`.toLowerCase();
  return haystack.includes(query.trim().toLowerCase()) && matchesSource;
}), [posts, query, source]);
```

At a dozen posts this is *correct and fast* — search is instant with no network round-trip, and pagination is free. At a thousand posts you're shipping the entire blog index to every visitor before they see anything. The honest read: this is the right call for the actual data size, and the migration path when it stops being right is to move `query`/`source`/`page` into URL search params and let the server do the filtering in GROQ. Knowing *which* trade you made, and what the exit looks like, is the difference between a shortcut and a mistake.

(Anything crossing the boundary must be serialisable — plain objects, arrays, primitives. No functions, no class instances, no `Date` methods you rely on surviving. Note the date formatting on the home page happens *after* the string crosses over: `new Date(post.publishedAt).toLocaleDateString(...)`.)

---

## 3. Async request APIs — the Next 16 breaking change you cannot ignore

Straight from the shipped upgrade guide:

> Version 15 introduced Async Request APIs as a breaking change, with **temporary** synchronous compatibility. Starting with **Next.js 16, synchronous access is fully removed.**

Affected: `cookies`, `headers`, `draftMode`, `params` (in `layout`, `page`, `route`, `default`, `opengraph-image`, `twitter-image`, `icon`, `apple-icon`), and `searchParams` in `page`.

So this is now the only correct shape:

```tsx
// src/app/(site)/blog/[slug]/page.tsx
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;   // ← await, or you get a Promise object
  ...
}
```

**Why a Promise, when the router obviously knows the slug?** Because of streaming and Partial Prerendering. Next wants to start rendering the static shell of a page *before* it knows the request-specific parts. Making `params` a Promise turns "I need the slug" into an explicit suspension point the framework can schedule around, rather than something that forces the whole route to be dynamic from line one. The awkward `await` is the price of the render not blocking.

This catches **`opengraph-image.tsx` too** — a separate breaking change with its own heading in the guide, and an easy one to miss because the file barely looks like a page:

```tsx
// src/app/(site)/blog/[slug]/opengraph-image.tsx
export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await sanityFetch<Post | null>(POST_BY_SLUG_QUERY, { slug }, null);
  ...
}
```

There's a codemod (`npx next upgrade`, or `npx @next/codemod@canary upgrade latest` before 16.1) and a typegen helper (`npx next typegen`) that generates `PageProps<'/blog/[slug]'>` so you get the route's param types for free instead of hand-writing `Promise<{ slug: string }>`. Worth adopting on the next project.

---

## 4. Caching: this project is on the *previous* model, deliberately

Both `blog/page.tsx` and the home page carry:

```tsx
export const revalidate = 60;
```

That's ISR: render at build, serve from cache, regenerate at most once every 60 seconds. Editor publishes in Sanity → live within a minute, with no rebuild and no webhook. For a site whose content changes a few times a month, that's the whole caching strategy, and it's the right one.

**The Next 16 nuance worth knowing.** Next 16 introduces **Cache Components**, opt-in via `cacheComponents: true` in `next.config.ts`, which replaces segment-level `revalidate` with a `use cache` directive plus `cacheLife`/`cacheTag`:

```tsx
// the new model — NOT what this project uses
export async function getProducts() {
  'use cache'
  cacheLife('hours')      // named profiles: seconds | minutes | hours | days | weeks | max
  return db.query('SELECT * FROM products')
}
```

This project's `next.config.ts` sets only `images`, so Cache Components is **off** and `export const revalidate` is still fully supported — the docs file it under "Caching and Revalidating (Previous Model)". Two things follow:

- Don't panic-migrate. The previous model isn't deprecated, it's the non-opt-in path.
- Do read `02-guides/caching-without-cache-components.md` rather than a tutorial, because *which* model a given article assumes is now the main way Next.js advice goes stale.

One gotcha from that file, cheap to trip over:

> The revalidate value needs to be statically analyzable. `revalidate = 600` is valid, but `revalidate = 60 * 10` is **not**.

It's read by the compiler from the source text, not evaluated. Same reason applies to `export const dynamic`, `runtime`, etc.

Also: **in development, pages are always rendered on-demand and never cached.** If you're testing whether ISR works, `bun run build && bun run start` — `bun run dev` will lie to you.

### `generateStaticParams` — prerendering the dynamic route

```tsx
export async function generateStaticParams() {
  const slugs = await sanityFetch<string[]>(ALL_POST_SLUGS_QUERY, {}, []);
  return slugs.map((slug) => ({ slug }));
}
```

At build time, ask the CMS for every native post slug and prerender each `/blog/<slug>` to static HTML. Combined with `revalidate = 60`, posts created *after* the build still work — they're rendered on first request and then cached.

Note the query behind it filters to `postType == "native"`, which is correct: external posts have no on-site body to render. There's a matching bug in the *detail* query — see [[projects/kingsley-iheme/learning/02-sanity|02-sanity §5]].

---

## 5. Tailwind CSS v4 — the config file is gone

If your Tailwind knowledge includes `tailwind.config.js`, it's out of date. This project has no such file. v4 configures itself **in CSS**:

```css
/* src/app/globals.css — the entire configuration */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

:root {
  --color-cream:     #faf7f1;
  --color-paper:     #f4efe4;
  --color-ink:       #211e1b;
  --color-ink-muted: #5b564f;
  --color-accent:    #9c4a2a;
  --color-border:    #e6dfd0;
}

@theme inline {
  --color-cream: var(--color-cream);
  --color-ink:   var(--color-ink);
  ...
  --font-serif: var(--font-fraunces);
  --font-sans:  var(--font-inter);
}
```

What changed, and why each bit matters:

- **`@import "tailwindcss"`** replaces the old `@tailwind base/components/utilities` triple.
- **`@plugin "..."`** loads plugins from CSS instead of a JS `plugins: []` array.
- **`@theme`** is the config. Every custom property declared inside it *generates utility classes*. `--color-ink` → `text-ink`, `bg-ink`, `border-ink`. `--font-serif` → `font-serif`. This is the whole design system: six colours and two fonts, and the class names follow automatically.
- **`@theme inline`** — the `inline` keyword means the utilities reference the variable's *value* rather than re-wrapping it in another `var()` indirection. The pattern here (declare real values in `:root`, re-export them through `@theme inline`) keeps the palette usable as plain CSS (`background: var(--color-cream)` in the `body` rule) *and* as Tailwind utilities, from one definition.
- **No content/purge paths.** v4 detects source files automatically.

The build wiring is correspondingly tiny — v4 is a single PostCSS plugin:

```js
// postcss.config.mjs
const config = { plugins: { "@tailwindcss/postcss": {} } };
```

**The design lesson underneath the syntax.** A six-token palette with semantic names (`ink`, `paper`, `cream`, `accent`) rather than scale names (`gray-900`, `orange-700`) means the site is visually coherent by construction — you cannot accidentally reach for a seventh grey, because there isn't one. Constraining the palette *in the config* is more effective than intending to be consistent.

### Fonts: `next/font` and the CSS-variable handoff

```tsx
// src/app/layout.tsx
const fraunces = Fraunces({ variable: "--font-fraunces", subsets: ["latin"], style: ["normal", "italic"] });
const inter    = Inter({ variable: "--font-inter", subsets: ["latin"] });

<html className={`${fraunces.variable} ${inter.variable} h-full antialiased`}>
```

`next/font/google` downloads the font files **at build time** and self-hosts them from your own origin. Three consequences worth knowing:

1. **Zero network requests to Google at runtime** — faster, and it removes a third-party dependency from your critical path.
2. **No layout shift.** Next generates a size-adjusted fallback so the fallback font occupies almost exactly the metrics of the real one — the CLS problem web fonts are famous for, solved at the framework level.
3. **A privacy/compliance win** that's easy to overlook: no visitor IP is ever sent to Google Fonts. That's an actual GDPR issue in the EU, not a theoretical one.

The `variable` option is what stitches it to Tailwind: the font object exposes a class that defines `--font-fraunces`, applied on `<html>`; `@theme inline` maps `--font-serif: var(--font-fraunces)`; and `font-serif` in markup resolves through the chain. Font loading, theme config and utility class stay decoupled — swapping Fraunces for Playfair is a one-line change in `layout.tsx`.

### `suppressHydrationWarning` on `<html>` and `<body>`

Both carry it. This is the standard escape hatch for the case where browser extensions (password managers, dark-mode injectors, Grammarly) mutate those two elements *before* React hydrates, producing a server/client mismatch React would otherwise log loudly.

**Know what you're silencing.** It suppresses the warning for that element's attributes only — it is not a general "make hydration errors go away" switch, and using it deeper in the tree to quiet a *real* mismatch hides a genuine bug. On `<html>`/`<body>` specifically, the mismatch is caused by software you don't control, so suppressing it is correct.

---

## 6. Metadata: file conventions doing work libraries used to do

Next 16's metadata layer is unusually complete, and this project leans on nearly all of it. Worth cataloguing because most of it replaces something you'd otherwise hand-roll or npm-install.

### The title template

```tsx
// src/app/layout.tsx
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: SITE_TITLE, template: "%s | Kingsley Iheme" },
  ...
};
```

Any child page exporting `title: "About"` renders `About | Kingsley Iheme`. `metadataBase` is what lets every other field use **relative** URLs — `alternates: { canonical: "/about" }` resolves against it, so the same code produces correct absolute URLs on localhost, preview, and production.

### The template's blind spot — and the helper written for it

There's a genuinely non-obvious gap here, and the codebase documents it in a comment:

```ts
// src/lib/metadata.ts
// generateMetadata title in openGraph doesn't inherit the root layout's
// "%s | Kingsley Iheme" template, so it's spelled out here to keep social
// previews in sync with the <title> shown in the browser tab.
export function pageMetadata({ title, description, path, fullTitle }: {...}): Metadata {
  const resolvedTitle = fullTitle ?? `${title} | ${SITE_NAME}`;
  const url = `${SITE_URL}${path}`;
  return {
    title,                                          // ← template applies here
    description,
    alternates: { canonical: path },
    openGraph: { title: resolvedTitle, description, url, type: "website" },
    twitter:   { card: "summary_large_image", title: resolvedTitle, description },
  };
}
```

**The trap:** `title.template` applies to the document `<title>`. It does **not** cascade into `openGraph.title` or `twitter.title`. Set only `title: "About"` and your browser tab reads "About | Kingsley Iheme" while the LinkedIn preview reads a bare "About" — a discrepancy that is invisible locally, invisible in code review, and only shows up when someone shares the link.

The fix is the right one: one helper, called by every static page, that computes the full title once and fans it out to all three places. The `fullTitle` escape hatch exists for the home page, which wants `Kingsley Iheme — Pastor & Counselor` rather than the doubled-up `Kingsley Iheme | Kingsley Iheme`.

**The generalisable habit:** when a framework gives you a convenience that applies to *some* of a set of related fields, write the helper that covers the whole set. Cross-field consistency that depends on remembering is consistency you don't have.

### Generated OG images with `ImageResponse`

```tsx
// src/app/opengraph-image.tsx
import { ImageResponse } from "next/og";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(<div style={{ ... }}>{SITE_NAME}</div>, { ...size });
}
```

You write JSX; Next renders it to a PNG at the edge. The per-post version at `blog/[slug]/opengraph-image.tsx` fetches the post and puts its title on the card, so every article gets a bespoke social image with no design tool in the loop.

**Two constraints that will bite you**, both visible in this code:

1. **Every element with more than one child needs an explicit `display: flex`.** Look at the divider `<div>` — it's a 64×4 coloured bar and it *still* sets `display: "flex"`. The renderer (Satori) implements a flexbox subset and does not assume block layout. The error message when you forget is unhelpful.
2. **Only inline styles.** No Tailwind classes, no external CSS. Hence the hardcoded `#faf7f1` / `#9c4a2a` instead of the theme tokens — a real duplication, and if the palette changes these files won't follow. Worth a comment pointing back at `globals.css`.

### `sitemap.ts` and `robots.ts`

Both are just functions returning typed objects — no XML strings, no `next-sitemap` package.

```ts
// src/app/sitemap.ts — static routes + every native post, from the CMS
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await sanityFetch<SitemapPost[]>(SITEMAP_POSTS_QUERY, {}, []);
  const staticEntries = staticRoutes.map((route) => ({
    url: `${SITE_URL}${route.path}`, lastModified: new Date(),
    changeFrequency: route.changeFrequency, priority: route.priority,
  }));
  const postEntries = posts.map((post) => ({
    url: `${SITE_URL}/blog/${post.slug}`,
    lastModified: new Date(post._updatedAt || post.publishedAt),  // ← nice touch
    changeFrequency: "monthly", priority: 0.6,
  }));
  return [...staticEntries, ...postEntries];
}
```

`post._updatedAt || post.publishedAt` is the detail worth stealing: `lastModified` should reflect **the last edit**, not the publish date. Sanity maintains `_updatedAt` for free, so a post corrected two years after publication correctly signals freshness to crawlers.

```ts
// src/app/robots.ts
disallow: ["/studio", "/api/"]
```

Correct instinct — keep the CMS login and the API surface out of search results. **But be clear about what `robots.txt` is**: a politeness convention honoured by well-behaved crawlers. It is *not* access control. `/studio` is genuinely protected because Sanity requires authentication; `/api/contact` is protected because it validates input and only sends mail to a fixed address. `robots.txt` is doing SEO hygiene here, not security — and treating a `Disallow` line as a security boundary is a classic finding in [[cybersecurity/04-web-security/README|web security]] reviews. (Worse, `robots.txt` is public and readable by anyone, so it happily advertises the paths you'd rather nobody visited.)

### JSON-LD structured data

```tsx
// src/components/json-ld.tsx
export function JsonLd({ data }: { data: object }) {
  return <script type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }} />;
}
```

Schema.org markup that tells Google *what* a page is — `/about` declares a `Person`, `/counseling` declares a `Service` with an `OfferCatalog` built from the same `sessionTypes` array the UI renders. One source of truth for the buttons and the structured data.

**The `.replace(/</g, "\\u003c")` is the load-bearing line, and it is not decoration.** Inside a `<script>` block, the HTML parser has one job: find `</script>`. If any user-controlled string in that JSON contains `</script><img src=x onerror=alert(1)>`, the browser closes the script tag early and executes the rest as markup — **stored XSS**, straight through `dangerouslySetInnerHTML`. Escaping `<` as its `<` unicode escape is valid JSON that parses to the identical string, but is invisible to the HTML parser, so the tag can never be closed early. Currently the data here is all hardcoded, but the component is generic and the guard means it stays safe if CMS content is ever fed into it. Cross-reference: [[cybersecurity/04-web-security/README|XSS]].

---

## 7. Animation: `motion` with a global accessibility default

```tsx
// src/components/motion-provider.tsx
"use client";
export function MotionProvider({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
```

`MotionConfig` wraps the whole site in `(site)/layout.tsx`. `reducedMotion="user"` honours the OS-level `prefers-reduced-motion` setting — for a visitor with vestibular sensitivity, every animation below is disabled automatically.

**This is the pattern worth copying: accessibility set once, at the provider, rather than per-component.** The alternative — remembering a `useReducedMotion()` check in every animated component — is a rule you will eventually forget. Encoding it in a provider means the forgetting is harmless.

(`motion` is the current package name for what most tutorials still call `framer-motion`; imports come from `motion/react`.)

```tsx
// src/components/fade-in.tsx
<motion.div
  initial={{ opacity: 0, y: 16 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-80px" }}
  transition={{ duration: 0.5, delay, ease: "easeOut" }}
/>
```

One reusable component, used everywhere, with a `delay` prop for stagger (`delay={index * 0.1}` across a grid). `whileInView` uses IntersectionObserver under the hood; `once: true` means it fires a single time rather than re-animating on every scroll-past — which is the difference between "elegant" and "seasick". `margin: "-80px"` shrinks the trigger area so the animation starts *slightly before* the element is fully visible, which reads as more responsive.

The restraint is the point: 16px of travel and half a second. Editorial sites are ruined by animation that announces itself.

---

## 8. Third-party embeds: `key` as a remount instruction

```tsx
// src/components/counseling-booking.tsx
const [selected, setSelected] = useState(sessionTypes[0]);
...
<CalBooking calLink={`${username}/${selected.slug}`} />
```

```tsx
// src/components/cal-booking.tsx
<Cal key={calLink} calLink={calLink} ... />
```

That `key={calLink}` is the whole trick, and it's a genuinely useful React idiom.

Normally React *reuses* a component instance when only its props change. That's the desired behaviour almost always — but the Cal.com embed initialises an iframe in an effect and doesn't necessarily re-read `calLink` on a prop change. So clicking "Couples session" would update the prop and leave the calendar showing the intro call.

**Changing the `key` forces React to unmount the old instance and mount a fresh one** — new effects, new iframe, correct calendar. `key` isn't only for lists; it's the general "treat this as a different thing, not the same thing updated" signal, and it's the standard escape hatch for third-party widgets that own their own state and don't expect props to change under them.

The alternative — resetting the embed imperatively through its API on every change — is more code, more coupling to their SDK, and more to go wrong.

### Copy bugs found in `cal-sessions.ts`

Reviewing this file for the notes turned up mistakes that are invisible in code review but very visible to a paying visitor:

```ts
{
  slug: "counseling-individual-session",
  label: "Basic Invidiual Session",      // ← "Invidiual" → "Individual"
  duration: "15 min",                    // ← individual session, same as an intro call?
  description:
    "A short call to talk through what you're looking for and see if it's a fit.",
                                         // ← copy-pasted verbatim from the intro call
},
```

Three problems in one object, and all three render straight onto the booking page. Worth fixing in one pass, and worth the general note: **arrays of user-facing copy deserve the same review attention as logic.** A typo in a `label` reaches more people than most bugs, and the diff for this file looked "not code" enough to skim past.

There's also a structural fragility: each `slug` must exactly match a Cal.com event-type slug configured in a completely different system. Nothing validates that. A rename in the Cal.com dashboard produces a silently broken calendar — the embed just fails to find the event type. This is the standard cost of config-by-convention across a system boundary; the mitigation is a comment (present) and, ideally, a note in the README (also present).

---

## 9. Images

```ts
// next.config.ts
images: { remotePatterns: [{ protocol: "https", hostname: "cdn.sanity.io" }] }
```

`next/image` refuses to optimise images from arbitrary hosts — an allowlist is mandatory. Without it, the CMS images throw at runtime rather than at build, which is exactly the sort of thing that ships.

**Why the allowlist exists at all:** without one, `/_next/image?url=<anything>` is an open image proxy — anyone can point it at any URL and burn your optimisation budget (and your bandwidth bill) resizing other people's images through your domain. `remotePatterns` closes that.

Two Next 16 notes from the upgrade guide worth carrying forward: **`images.domains` is deprecated** in favour of `remotePatterns` (this project is already correct), and the **`minimumCacheTTL` and `qualities` defaults changed** — if optimised images look different or re-fetch more often after an upgrade, that's where to look.

The `ImageSlot` component is a small pattern worth reusing: one component that renders a real `next/image` when given a `src` and a labelled placeholder box when not.

```tsx
// src/components/image-slot.tsx
{src ? <Image src={src} alt={alt} fill className="object-cover" />
     : <div className="absolute inset-0 flex ..."><svg .../>{label}</div>}
```

It keeps layout dimensions identical whether or not the asset exists, which means design work and content work can proceed independently — the page never collapses because a photo hasn't been chosen yet. Same philosophy as the env-gated integrations in [[projects/kingsley-iheme/learning/03-backend-api|03]]: **the site must look finished at every stage of being unfinished.**

`fill` + a positioned parent + `object-cover` is the standard recipe for "fill this box, crop as needed"; `aspect` is passed as a Tailwind class (`aspect-[4/5]`) so each call site controls the shape.

---

## Takeaways

1. **Read the docs inside `node_modules/`.** They match your version. Blog posts don't. This corrected two things in this file alone.
2. **`"use client"` is a boundary, not a label.** Unmarked components inherit the kind of whoever imports them. Put the boundary as deep as possible.
3. **Route groups separate layout structure from URL structure.** Reach for one whenever a subset of routes needs a different shell.
4. **`params` is a Promise in Next 16** — pages, layouts, route handlers, *and* the OG-image files. Synchronous access is fully removed, not deprecated.
5. **Tailwind v4 configures in CSS.** `@theme` generates the utilities; there is no config file; a deliberately small token set makes visual consistency structural.
6. **`title.template` doesn't reach `openGraph.title`.** Wrap metadata construction in a helper so cross-field consistency doesn't depend on memory.
7. **Escape `<` in JSON-LD.** `dangerouslySetInnerHTML` in a `<script>` is an XSS vector the moment CMS content flows into it.
8. **Set accessibility defaults at the provider.** `reducedMotion="user"` once beats a per-component check you'll forget.
9. **`key` is the remount escape hatch** for third-party widgets that own their own state.
10. **Review copy arrays like code.** Three user-facing bugs sat in one 8-line object.
