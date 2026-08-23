# Performance

> **[Intermediate]** · Core Web Vitals, the method, and the fixes that actually move the numbers.

## Measure first, and measure the right thing

**Lab data** (Lighthouse, on your machine) is reproducible and unrepresentative. **Field data** (real users, real devices) is noisy and true.

**Chrome's Core Web Vitals are the standard**, and each maps to a different cause:

| Metric | Measures | Good | Usually caused by |
|---|---|---|---|
| **LCP** | Largest element painted | < 2.5s | Slow server, render-blocking resources, unoptimised images |
| **INP** | Responsiveness to interaction | < 200ms | **Long tasks blocking the main thread** |
| **CLS** | Unexpected layout shift | < 0.1 | Images/ads without dimensions, late-loading fonts |

**INP replaced FID in 2024** and is harder to satisfy — FID measured only the *first* interaction's delay; INP measures every interaction end to end.

**The diagnostic order:**
1. Which metric is bad?
2. **Network or CPU?** The waterfall vs the Performance panel's long tasks
3. Fix one thing
4. **Measure again**

**Guessing is the expensive path** — the same method as [[foundations/computer-architecture/12-performance|performance method]] several layers down.

## Network

**JavaScript is the most expensive byte you ship**, because it must be downloaded, parsed, compiled *and* executed — unlike an image, which is only decoded.

- **Code splitting per route** — the biggest single lever in most apps
- **Tree shaking** — and check it works. A CommonJS dependency, or one with side effects, silently defeats it
- **Analyse the bundle** (`rollup-plugin-visualizer`, `@next/bundle-analyzer`) — **there is nearly always a surprise**, usually a date library or an icon set imported whole
- **Modern formats** — AVIF/WebP, responsive `srcset`, and **always set `width`/`height`** so the browser reserves space (that's the CLS fix)
- **Lazy-load below the fold**; **preload the LCP image**
- **`font-display: swap`** plus `<link rel="preload">` for fonts, and prefer variable fonts
- **Compress** — Brotli over gzip

**The single biggest win in many real apps is third-party scripts.** Analytics, chat widgets, tag managers, A/B tools. **Audit them, defer them, and delete the ones nobody can name an owner for** — it's the least technical and most effective performance work available.

## CPU

**Long tasks are what INP measures**, and the main thread does layout, paint and input alongside your JavaScript → [[frontend/01-foundations/02-the-browser-and-the-dom|the browser]].

- **Break up long tasks** — `scheduler.yield()`, or chunk the work
- **Web Workers** for genuinely heavy computation. **The only real parallelism you have**
- **Virtualise long lists** — render the visible window, not 10,000 rows
- **Memoise expensive subtrees** — deliberately, after profiling, not by reflex
- **Debounce/throttle** high-frequency handlers; better, use `IntersectionObserver` instead of `scroll`

**Animate `transform` and `opacity` only** — those run on the compositor. Anything else forces layout or paint per frame → [[frontend/01-foundations/02-the-browser-and-the-dom|reflow and repaint]].

## The React-specific ones

**Most "React is slow" is one of four things:**

1. **Rendering the whole tree on every keystroke** — state too high. Move it down → [[frontend/03-structuring-a-frontend/01-components-and-composition|components]]
2. **A context whose value is a new object each render** — every consumer re-renders → [[frontend/04-state-and-data/01-state-management|state]]
3. **Unstable props** — inline objects, arrays and functions break `memo`
4. **Unvirtualised long lists**

**Profile with React DevTools before memoising anything.** `useMemo` and `useCallback` are not free — they cost memory and comparison, and applied blindly they make things slower while looking like optimisation. **React Compiler (19+) automates much of this**, which is a good reason not to hand-optimise pre-emptively.

## A budget beats a vibe

**Set numbers, enforce them in CI:**

```
JS  ≤ 170 KB compressed on the critical path
LCP ≤ 2.5s on a mid-tier Android over 4G
INP ≤ 200ms
CLS ≤ 0.1
```

**Fail the build when a budget is exceeded.** Otherwise performance degrades by a kilobyte a week and nobody can point at the commit that did it — the same argument as an [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|error budget]].

**Test on a real mid-range Android**, or at minimum throttle to 4× CPU slowdown. **Your laptop is the least representative device you own** — and this is the single most common reason a "fast" site is slow for actual users.

## What not to bother with

**Micro-optimising JavaScript.** `for` vs `forEach` is irrelevant next to a 300 KB bundle.

**Optimising before measuring.** The bottleneck is rarely where you assume.

**Chasing a Lighthouse 100.** It's a lab proxy. **Field data is the thing users experience**, and a perfect lab score with bad field INP is common.

## Related
- [[frontend/07-practices/01-frontend-best-practices|frontend best practices]]
- [[frontend/01-foundations/02-the-browser-and-the-dom|the browser and the DOM]]
- [[frontend/02-rendering/README|rendering]] — strategy affects LCP directly
- [[foundations/computer-architecture/12-performance|performance method]]

*Source: [reference] — from web.dev and the Core Web Vitals documentation, Aug 2026.*
