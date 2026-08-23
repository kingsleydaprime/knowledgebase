# Frontend Interview — State, Data & Architecture

The round that separates *"I can build a component"* from *"I can structure an application."* It's where senior frontend interviews spend most of their time, and where the answers are judgement rather than recall.

From [[concepts/02-frontend/02-state-management|state management]], [[concepts/02-frontend/03-rendering|rendering]], and the React/Next material in [[projects/README|projects/]].

---

### Q1. [Intermediate] 🔥 How do you decide where state lives?

**Strong answer covers:** start local, lift only when genuinely shared, and reach for a global store last. The real skill is recognising that **most "state management problems" are actually data-fetching problems.**

**The categories, which is the framing that scores:**

| Kind | Example | Belongs in |
|---|---|---|
| **Local UI** | is this dropdown open | `useState` in the component |
| **Shared UI** | theme, sidebar collapsed | context, or a small store |
| **Form** | field values, validation | a form library, or local |
| **URL** | filters, page, tab, search | **the URL** |
| **Server cache** | the user, the product list | **a query library** |

**The two most common mistakes:**
- **Putting server data in a global store.** It isn't state, it's a *cache* of someone else's state — it goes stale, needs revalidation, refetching, and loading/error handling. React Query / SWR / RTK Query exist because hand-rolling that in Redux is thousands of lines of the same code
- **Not using the URL.** Filters and pagination in `useState` mean the page isn't shareable, bookmarkable, or back-button-correct. **If a user would expect to share the link and see the same thing, it belongs in the URL**

**The senior point:** since server-cache libraries took over, the amount of genuine *client* state in a typical app is small — often a theme and a couple of toggles. Candidates who still reach for Redux first are describing 2018.

---

### Q2. [Intermediate] 🔥 Context re-renders everything. Discuss.

**Strong answer covers:** when a context's **value** changes, every consumer re-renders — `memo` doesn't help, because it isn't a prop change. And the value is a new object every render unless memoised:

```jsx
<Ctx.Provider value={{ user, setUser }}>   {/* ✗ new object each render */}
```

**Fixes, in order of preference:**
1. **`useMemo` the value** — the minimum
2. **Split contexts** — a rarely-changing `UserContext` and a frequently-changing one, so consumers subscribe only to what they need
3. **Separate state and dispatch contexts** — dispatch is stable, so components that only dispatch never re-render
4. **Use a store with selectors** (Zustand, Jotai, Redux) when consumers need *fine-grained* subscription — that's the thing context structurally cannot do

**The senior point:** context is a **dependency-injection mechanism**, not a state manager. It's excellent for things that rarely change (theme, locale, the current user, a client instance) and a poor fit for high-frequency updates.

---

### Q3. [Intermediate] 🔥 Walk me through fetching data properly.

**Strong answer covers** the states people forget: loading, error, **empty**, stale, and refetching. Then:

- **Race conditions.** Type fast in a search box and responses return out of order — the *older* one can land last and win. Fix with `AbortController` cancellation, or by discarding responses that don't match the current query key
- **Caching and revalidation** — stale-while-revalidate: show cached data instantly, refetch in the background
- **Deduplication** — three components asking for the same user should produce one request
- **Waterfalls.** Sequential dependent fetches down the component tree. Fix by hoisting the fetch, prefetching on the route, or fetching on the server
- **Optimistic updates**, and rolling them back on failure
- **Pagination vs infinite scroll**, and keeping the cache coherent across pages

**The senior point:** *"I'd use React Query rather than hand-roll this"* is a strong answer **only if you can list what it's doing for you** — dedupe, cache, retry, background revalidation, cancellation, and the request lifecycle. Naming the library without the list reads as cargo-culting.

---

### Q4. [Intermediate] How do you structure a frontend codebase that four people work in?

**Strong answer covers:** **feature-based over type-based.** `features/checkout/{components,hooks,api,types}` rather than a top-level `components/` with 200 files.

**Why:** a change to checkout touches one directory. Type-based grouping means every feature change touches five directories, and two people working on different features constantly collide → [[foundations/systems-engineering/04-architecture-and-interfaces|coupling and cohesion]].

**Other things worth raising:**
- **A shared `ui/` layer** of genuinely generic primitives — and the discipline to keep business logic out of it
- **Import boundaries** — features shouldn't import each other's internals. Enforceable with ESLint rules
- **Colocate tests** with the code
- **Where the API layer lives** — one typed client, not `fetch` scattered through components
- **Barrel files** (`index.ts`) help imports and can hurt tree-shaking and build time — know the trade

**The senior point:** Conway's law applies to frontends too. **Structure the code the way you want teams to be able to work in parallel** → [[foundations/systems-engineering/04-architecture-and-interfaces|Conway]].

---

### Q5. [Intermediate] 🔥 How do you make a component accessible? Give specifics.

**Strong answer covers** — and this is a genuine differentiator, because most candidates say "use semantic HTML" and stop:

- **Semantic HTML first.** A `<button>` gives you focus, Enter/Space, and the right role for free. `<div onClick>` gives you none of it, and adding them back correctly is more work than using the button
- **Keyboard.** Everything reachable and operable by keyboard; **visible focus indicators** (removing the outline without replacing it is the single most common accessibility failure)
- **Focus management** — a modal traps focus, returns it on close, and closes on Escape
- **ARIA only when semantics run out**, and correctly: `aria-label`, `aria-expanded`, `aria-live` for async updates. **Wrong ARIA is worse than none** — it overrides the correct native semantics
- **Forms** — real `<label>`s tied to inputs; errors announced, not just coloured
- **Colour is never the only signal**; contrast ≥ 4.5:1 for body text
- **Test it**: keyboard-only for one flow, then a screen reader, then axe/Lighthouse

**The senior point:** it's a legal requirement in many markets (EAA, ADA, WCAG 2.2), and it's the frontend area where most candidates are weakest — which makes it cheap to stand out in.

---

### Q6. [Advanced] The page is slow. How do you diagnose it?

**Strong answer covers** a method rather than a list of fixes:

1. **Measure first** — Lighthouse for a lab baseline, then **field data** (real users, real devices). Lab numbers on a fast laptop mislead
2. **Which metric?** LCP → the largest element loads late. INP → the main thread is blocked. CLS → layout shifting
3. **Network or CPU?** The waterfall tells you. Large bundle, unoptimised images, no compression, blocking requests — versus long tasks in the Performance panel
4. **For CPU:** find long tasks, look at the flame chart, check for excessive re-renders with the React Profiler
5. **Fix, then re-measure**

**The fixes worth naming:** code splitting per route, `next/image`-style responsive images with modern formats, preloading the LCP resource, deferring third-party scripts (**usually the biggest single win, and the least technical**), virtualising long lists, memoising genuinely expensive subtrees.

**The senior point:** *"I'd profile before optimising"* is the answer, and the follow-up that scores is naming the **specific** tool and metric you'd look at first — the same method as [[foundations/computer-architecture/12-performance|performance method]] one layer down.

---

### Q7. [Advanced] Where would you put the rendering boundary in a Next.js app?

**Strong answer covers:** Server Components render on the server and ship **no JS**; Client Components hydrate. The boundary is a **per-subtree** decision, and the goal is to push it as far down the tree as possible.

**Details that matter:**
- Data fetching, secrets and heavy dependencies belong on the server — a date library used only in a Server Component never reaches the bundle
- `"use client"` marks a boundary: everything imported below it becomes client code. **One badly-placed directive near the root ships the whole tree**
- Server Components can render Client ones, but you can't pass functions across the boundary — only serialisable props
- **Streaming + Suspense** lets you send the shell immediately and fill slow regions as they resolve, so a slow query doesn't block first paint

**The senior point:** the honest framing is that this is a **bundle-size and data-locality** optimisation with real added complexity — and worth it in proportion to how content-heavy the app is. A highly interactive dashboard gains far less than a commerce site.

---

## Related
- [[frontend/interview/01-react-rendering-and-performance|React, rendering & performance]]
- [[frontend/interview/02-javascript-and-typescript|JavaScript & TypeScript]]
- [[concepts/interview/01-apis-auth-and-practices|APIs, auth & practices]]
- [[architecture/interview/README|Architecture interview prep]] — the system-design round

*Source: [reference] — assembled Aug 2026.*
