# Hydration and the Server Boundary

> **[Intermediate → Advanced]** · Why SSR pages look ready before they work, and what RSC actually changes.

[[frontend/02-rendering/01-rendering-strategies|Note 01]] covers CSR, SSR, SSG and ISR — *where* HTML is produced. **This is what happens next**, and it's where the real complexity lives.

## The hydration problem

**Server-rendered HTML is inert.** It looks like the page; nothing is wired up. Buttons don't respond, state doesn't exist.

**Hydration** is the client framework walking the server HTML, attaching event listeners and rebuilding component state so the markup becomes interactive.

**Which produces the uncanny window:**

```
0ms    HTML arrives      → looks complete
       ...JS downloads   → still looks complete, does nothing
       ...JS parses      → still nothing
       ...hydration      → NOW it works
```

**The page is visible and unresponsive for the whole gap.** Users click, nothing happens, they click again — and on a slow device that window is seconds, not milliseconds. **This is why a "fast" SSR page can feel worse than a CSR one that showed a spinner honestly.**

**You pay for the content twice:** once as HTML, once as the JS and serialised state needed to reproduce it.

## Hydration mismatches

**The server rendered one thing; the client rendered another.** The framework notices and complains — or worse, silently patches over it.

**The reliable causes:**

```jsx
{new Date().toLocaleTimeString()}       // ✗ different on server and client
{Math.random()}                          // ✗
{window.innerWidth}                      // ✗ no window on the server
{localStorage.getItem("theme")}          // ✗ same
```

**Anything non-deterministic, time-dependent, or browser-only will mismatch.**

The fixes:
- **Render it client-only** — an effect after mount, or a dynamic import with SSR disabled
- **Pass the value from the server** so both sides agree
- **`suppressHydrationWarning`** for genuinely unavoidable cases like timestamps — narrowly, not as a blanket

**The dark-mode flash is this bug in its most visible form.** The theme is in `localStorage`, the server can't read it, so the page renders light and snaps to dark after hydration. The standard fix is a tiny **blocking** inline script in `<head>` that sets a class before first paint — deliberately blocking, because correctness beats the few milliseconds here.

## The strategies for closing the gap

**Streaming SSR** — send the HTML shell immediately, stream slower regions as they resolve. A slow database query no longer blocks first paint.

```jsx
<Suspense fallback={<Skeleton />}>
  <SlowComponent />
</Suspense>
```

**Selective / progressive hydration** — hydrate interactive regions independently, prioritising what the user is looking at or interacting with, rather than one monolithic pass.

**Islands architecture** — the page is mostly static HTML with small independently-hydrated interactive "islands". **Astro** is built on this, and for content sites it ships dramatically less JavaScript.

**Resumability** — Qwik's approach: serialise enough state into the HTML that the client can *resume* without re-executing component code at all. **The most radical answer**, and the least mainstream.

## React Server Components

**The current mainstream answer, and it's a different idea from SSR** — which is the thing most people get wrong.

| | SSR | RSC |
|---|---|---|
| Runs on the server | ✓ | ✓ |
| Ships component JS to the client | **✓ (for hydration)** | **✗ — never** |
| Can hold state / effects | ✓ after hydration | **✗** |
| Re-renders on interaction | ✓ | ✗ |

**A Server Component's code never reaches the browser.** Its *output* does. So a component using a 300 KB markdown parser costs zero client bytes.

```jsx
// Server Component — the default in Next's App Router
async function ProductPage({ id }) {
  const product = await db.products.find(id);     // direct DB access, no API layer
  return <><h1>{product.name}</h1><AddToCart id={id} /></>;
}

"use client";                                      // ← the boundary
function AddToCart({ id }) { const [n, setN] = useState(1); /* … */ }
```

**The rules that follow:**

- **`"use client"` marks a boundary, not a file.** Everything imported below it becomes client code — **so one misplaced directive near the root ships your whole tree**
- **Props crossing the boundary must be serialisable.** No functions, no class instances
- Server Components can render Client Components; **the reverse only via `children`**
- No `useState`, `useEffect` or browser APIs in a Server Component

**The honest assessment:** RSC is a genuine reduction in shipped JavaScript and a real increase in mental overhead. **The benefit scales with how content-heavy the app is.** A dashboard that's interactive throughout gains little; a commerce or content site gains a lot → [[frontend/frameworks/next/README|Next.js]].

## Choosing

**Per route, not per app** — and that's the framing that scores in an interview and works in practice:

| Route | Strategy |
|---|---|
| Marketing page | **SSG** |
| Blog / docs | SSG or ISR, islands if mostly static |
| Product page — SEO + fresh stock | **SSR or ISR** |
| Authenticated dashboard | **CSR**, or SSR shell + client data |
| Highly interactive editor | **CSR** |

**And be honest about whether you need SSR at all.** If the app is behind a login, SEO is irrelevant, and a CSR app with a good loading state is simpler, cheaper and often faster to interactive.

## Related
- [[frontend/02-rendering/01-rendering-strategies|rendering strategies]] — CSR/SSR/SSG/ISR
- [[frontend/frameworks/next/README|Next.js]] — where most of this is implemented
- [[frontend/07-practices/README|practices]] — measuring the result
- [[frontend/01-foundations/02-the-browser-and-the-dom|the browser]] — why blocking matters

*Source: [reference] — written Aug 2026.*
