# Frontend Interview — React, Rendering & Performance

From [[frontend/README|frontend]], [[frontend/frameworks/gsap/07-performance-and-gotchas|GSAP performance]], [[frontend/frameworks/threejs/08-performance-and-gotchas|Three.js performance]].

---

### Q1. [Beginner→Intermediate] 🔥 What actually happens when React state changes?

**Strong answer covers:** `setState` schedules a re-render. React calls your component function again, producing a new element tree, **diffs** it against the previous one (reconciliation), and applies the minimum set of DOM mutations. Rendering is not the same as touching the DOM — a re-render that produces identical output costs CPU but no DOM work.

**Details that matter:**
- **Updates are batched** — multiple `setState` calls in one event handler produce one render (and since React 18, this holds in promises and timeouts too, not just event handlers).
- **State updates are asynchronous** with respect to the current function scope — reading the state variable right after setting it gives you the old value. Use the updater form (`setX(x => x + 1)`) when the new value depends on the old.
- **Keys drive reconciliation.** Using an array index as a key means React matches the wrong elements when the list reorders, producing wrong state in children — the classic "the checkbox moved to the wrong row" bug. Use a stable id.

---

### Q2. [Intermediate] 🔥 Why does my `useEffect` run twice / loop forever?

**Strong answer covers:**
- **Twice in development** is React 18's StrictMode intentionally double-invoking effects to surface missing cleanup. It's a *feature* — if double-mounting breaks your component, it has a real bug (an unremoved listener, an unaborted fetch). It doesn't happen in production.
- **Infinite loop** means the dependency array contains something recreated every render — an inline object, array, or function. Each render makes a new reference, the effect reruns, sets state, renders again. Fix with `useMemo`/`useCallback`, or by moving the value out, or by restructuring so the effect isn't needed.

**The senior point:** most `useEffect` uses are unnecessary. Effects are for **synchronising with something outside React** (a subscription, a timer, an imperative animation library, a WebSocket). Deriving state from props, transforming data for rendering, or responding to a user event should not be effects — calculate during render or handle it in the event handler.

---

### Q3. [Intermediate] 🔥 CSR, SSR, SSG, ISR — pick one and defend it.

**Strong answer covers:**

| Strategy | Rendered | Good for | Costs |
|---|---|---|---|
| **CSR** | in the browser | app-like, authenticated dashboards | slow first paint, bad SEO |
| **SSR** | per request on the server | personalised + needs SEO | server cost, TTFB includes your data fetching |
| **SSG** | at build time | content that rarely changes | rebuild to update; bad at scale of pages |
| **ISR** | build + revalidate | large content sites | stale window, more complex |

**The framing that scores:** it's a per-route decision, not a per-app one. A marketing page is SSG; a dashboard is CSR; a product page needing SEO and fresh stock levels is SSR or ISR. Modern frameworks let you mix, and a candidate who picks per-route shows they've actually shipped.

**On hydration — worth raising unprompted:** SSR sends HTML *and* the JS to make it interactive, so you pay for the markup twice, and there's a window where the page looks ready but doesn't respond. That's the gap **React Server Components** and streaming/selective hydration target: send components that never need client JS as pure output, and hydrate interactive islands independently.

---

### Q4. [Intermediate] What are Core Web Vitals and how do you fix each?

**Strong answer covers:**
- **LCP** (Largest Contentful Paint) — when the main content appears. Usually fixed at the **network** layer, not in JS: preload the hero image, use a CDN, serve modern formats, reduce round trips before the image is discoverable. → [[foundations/networking/15-network-performance|network performance]]
- **INP** (Interaction to Next Paint, which replaced FID) — responsiveness across the whole session. Fixed by breaking up long tasks, deferring non-critical JS, and moving work off the main thread.
- **CLS** (Cumulative Layout Shift) — visual stability. Fixed by reserving space: width/height on images, `aspect-ratio`, no injecting content above existing content, and `font-display: optional`/`swap` with a matched fallback metric.

**The point that lifts this:** most LCP problems are **network** problems (round trips, render-blocking resources) and most INP problems are **main-thread** problems. Knowing which axis you're on tells you where to look — the same bisect-the-layers instinct as [[foundations/networking/16-debugging-networks|network debugging]].

---

### Q5. [Intermediate] 🔥 Why is animating `transform` faster than animating `top`/`left`?

**Strong answer covers the browser's rendering pipeline** — style → layout → paint → composite:

- Animating `top`/`left`/`width` changes **geometry**, so the browser must re-run **layout** (reflow) and **paint** on every frame, for that element and potentially its siblings.
- Animating `transform` and `opacity` can be handled **entirely by the compositor**, often on the GPU, skipping layout and paint completely.

At 60fps you have **16.7ms per frame** for everything. Layout on a complex tree can eat that alone.

**Details that show real experience:**
- `will-change: transform` (or a 3D transform) promotes an element to its own compositor layer — but **overusing it costs memory** and can make things worse. Promote deliberately, not defensively.
- **Layout thrashing** — reading a layout property (`offsetHeight`) after writing one forces a **synchronous reflow**. In a loop that's O(n) forced reflows and a frozen page. Batch reads, then writes.
- Use `requestAnimationFrame`, not `setInterval`, so you're aligned with the frame budget.

This is straight from [[frontend/frameworks/gsap/07-performance-and-gotchas|the GSAP performance note]], and it's the kind of answer most candidates can't give.

---

### Q6. [Intermediate] How do you handle state management, and when do you need a library?

**Strong answer covers the categories, because conflating them is the mistake:**
- **Server state** — data owned by the backend. Needs caching, revalidation, and dedup. **TanStack Query / SWR**, not Redux.
- **Client state** — UI state (modals, form drafts, filters). `useState`, or Zustand/Jotai when shared widely.
- **URL state** — filters, pagination, tabs. Should live in the URL so it's shareable and survives refresh. Chronically under-used.
- **Form state** — its own problem; React Hook Form et al.

**The answer that scores:** *"most 'we need Redux' problems are actually server state being cached badly."* Once you pull server data into a query library, the remaining global client state is usually small enough for context or a tiny store. Start with local state and lift only when there's an actual need — premature global state is the frontend equivalent of premature microservices.

---

### Q7. [Intermediate] How do you make a web app accessible, and why does it matter beyond compliance?

**Strong answer covers:** **semantic HTML first** — a `<button>` gives you keyboard activation, focus, and screen-reader semantics for free; a `<div onClick>` gives you none of it and you'll reimplement all three badly. ARIA is for what HTML can't express, and **incorrect ARIA is worse than none**.

Then: keyboard navigation for every interactive element, visible focus indicators (don't `outline: none` without a replacement), sufficient colour contrast, labelled form inputs, alt text that conveys purpose, and `prefers-reduced-motion` respected for animation.

**Why beyond compliance:** semantic markup improves SEO, keyboard support helps power users, and `prefers-reduced-motion` prevents genuine harm — vestibular disorders make parallax and large motion physically nauseating. **In an animation-heavy codebase, honouring `prefers-reduced-motion` is the single highest-value accessibility control**, and it's a one-media-query change. → [[frontend/frameworks/framer-motion/08-performance-and-gotchas|Framer Motion gotchas]]

---

### Q8. [Intermediate] 🔥 Where do you store an auth token in a browser?

**Strong answer covers the tradeoff honestly:**
- **`localStorage`** — readable by **any** JavaScript on your page, so a single XSS (or a compromised npm dependency) exfiltrates every user's token. Convenient, and the common choice for the wrong reasons.
- **`httpOnly` cookie** — invisible to JS, so XSS can't read it. But it's sent automatically, so you need **CSRF** protection — `SameSite=Lax`/`Strict` covers most of it now.
- **In memory** — safest, lost on refresh; pair with a refresh token in an `httpOnly` cookie.

**The strongest position:** `httpOnly`, `Secure`, `SameSite` cookies for the refresh token, access token in memory. And note that **if you have XSS, you have lost anyway** — an attacker with script execution can make authenticated requests from the user's session whether or not they can read the token. So token storage is a mitigation, not a substitute for preventing XSS. → [[cybersecurity/interview/01-appsec-crypto-and-defence|web security]]

---

### Q9. [Intermediate] How would you debug "the page is slow"?

**Strong answer covers a method:**
1. **Which slow?** Initial load, interaction, or scroll/animation? Completely different investigations.
2. **Network tab** — waterfall. Render-blocking resources? Too many round trips? Huge unoptimised images? Is TTFB high (server's problem) or is transfer slow (payload/network)?
3. **Performance panel** — record. Long tasks over 50ms block interaction. Look for layout thrashing (purple layout bars in a loop) and excessive scripting.
4. **React Profiler** — which components re-render and why. Often a context value recreated each render is re-rendering the whole tree.
5. **Coverage tab** — how much shipped JS/CSS is unused? Bundle analysis usually finds a date library or an icon set imported wholesale.

**The framing:** **measure before optimising**, and measure on a **throttled CPU and network** profile. Everything is fast on a developer laptop on office Wi-Fi; the users you're losing are on a mid-range Android on 3G.
