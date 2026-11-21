---
id: e5ed515b-2caf-4c2d-b82f-8c2080cffe36
---

# The Browser and the DOM

## From URL to pixels
<!-- bite: eb1f7203-777c-427b-858c-d7b4c9d48c2c -->

```
DNS → TCP → TLS → HTTP request → HTML arrives
   → parse HTML → DOM tree
   → parse CSS  → CSSOM
   → DOM + CSSOM → render tree
   → layout (where is everything?)
   → paint (what colour is each pixel?)
   → composite (stack the layers)
```

**The first four steps are [[networking/index|networking]]** and are often the bulk of the time on a first visit.

**Each later step depends on the one before**, which is why the order of your `<head>` matters and why "just move the script tag" is real advice rather than folklore.

## The critical rendering path
<!-- bite: 9f455c12-98d7-4c59-b8b7-ff9816d0ac7c -->

**Two blocking behaviours account for most slow first paints:**

**CSS blocks rendering.** The browser will not paint until it has the CSSOM, because painting with unstyled content then restyling is worse than waiting. **So a large stylesheet in `<head>` delays *everything*.**

**Synchronous scripts block parsing.** A `<script>` without `async` or `defer` stops HTML parsing, downloads, executes, then resumes — because the script might call `document.write`.

```html
<script src="app.js"></script>          <!-- blocks parsing -->
<script src="app.js" defer></script>    <!-- downloads in parallel, runs after parse, in order -->
<script src="app.js" async></script>    <!-- downloads in parallel, runs ASAP, any order -->
```

**Use `defer` for anything that touches the DOM. `async` only for independent things** like analytics — because `async` scripts can run before the DOM they need exists.

## Reflow and repaint
<!-- bite: 807ed5fa-5e98-4d1a-9b79-e699337c807b -->

**Reflow (layout)** — recompute geometry. Expensive, and can cascade to the whole document.
**Repaint** — redraw pixels without changing geometry. Cheaper.
**Composite** — reposition existing layers on the GPU. **Cheapest.**

**This is why the animation advice you've seen exists:**

```css
.slow { left: 100px; }              /* reflow → repaint → composite */
.fast { transform: translateX(100px); }  /* composite only */
```

**`transform` and `opacity` can be animated on the compositor**, off the main thread. Everything else cannot. That single fact is most of web animation performance → [[frontend/frameworks/gsap/07-performance-and-gotchas|GSAP performance]].

**Layout thrashing** is the classic bug: reading a layout property forces the browser to flush pending changes.

```js
for (const el of items) {
  el.style.width = el.offsetWidth + 10 + "px";   // ✗ write, then READ, every iteration
}
```

Each read after a write forces a synchronous reflow. **Batch reads, then batch writes** — or use `requestAnimationFrame`. The pattern has a name, *read-write separation*, and it turns O(n) reflows into one.

## The DOM is a tree, and it's slow to touch
<!-- bite: 59ceab18-2969-4984-be35-68be8f621e2b -->

The DOM is a live tree of nodes. Mutating it triggers the pipeline above.

**It is genuinely slower than people expect** — not because the tree is slow, but because each mutation may invalidate layout for a subtree.

**Which is what frameworks are optimising.** React's virtual DOM, Svelte's compiled updates and Vue's reactivity all exist to **batch and minimise real DOM mutations** → [[frontend/06-rendering/index|rendering]].

**And it's why `key` matters in every framework's list rendering** — it tells the reconciler which DOM node corresponds to which item, and getting it wrong moves state to the wrong row.

## Events
<!-- bite: c5e81b0d-2d69-4ea1-9746-09ab3a4becec -->

**Events propagate in three phases:** capture (root → target), target, then **bubble** (target → root).

```js
el.addEventListener("click", handler);           // bubble phase (default)
el.addEventListener("click", handler, true);     // capture phase
```

**Event delegation** uses bubbling: one listener on a container handles clicks on any child, including ones added later.

```js
list.addEventListener("click", (e) => {
  const item = e.target.closest("[data-id]");
  if (item) select(item.dataset.id);
});
```

**One listener instead of a thousand** — less memory, and it works for dynamically added rows. React does this internally, which is why its event objects are not raw DOM events.

**`preventDefault()` stops the browser's default action; `stopPropagation()` stops the event travelling.** They're different, and reaching for the second is usually a sign of a design problem.

## The APIs worth knowing
<!-- bite: 7a3453fb-540f-4831-9acd-e15bb1a26218 -->

| API | For |
|---|---|
| **`fetch`** | HTTP, with `AbortController` for cancellation |
| **`IntersectionObserver`** | "Is this visible?" — lazy loading, infinite scroll. **Replaces scroll handlers** |
| **`ResizeObserver`** | Element size changes without polling |
| **`MutationObserver`** | DOM changes |
| **`requestAnimationFrame`** | Run before the next paint |
| **`requestIdleCallback`** | Run when the browser is idle |
| **Web Workers** | **Real parallelism**, off the main thread |
| `localStorage` / `sessionStorage` | Small, synchronous, string-only. **Synchronous means it blocks** |
| **IndexedDB** | Large structured storage, async |
| **History API** | Client-side routing |

**The observers are the ones people miss.** A `scroll` listener firing hundreds of times a second, each doing `getBoundingClientRect()`, is a classic jank source. `IntersectionObserver` does the same job off the main thread.

## Related
<!-- bite: 4cc282ef-7e23-4282-be16-77e684191597 -->
- [[frontend/06-rendering/index|rendering]] — CSR, SSR, hydration
- [[frontend/07-practices/index|practices]] — Core Web Vitals
- [[networking/11-http-evolution/index|HTTP]] — the first four steps
- [[computer-graphics/index|computer graphics]] — what paint and composite actually do

## About this lesson
<!-- bite: 8a6b3227-ae91-4d17-9149-fed1958a8685 -->

**Level:** Beginner → Intermediate. **Covers:** What happens between a URL and pixels — and why that pipeline explains most performance advice.

*Source: [reference] — written Aug 2026.*
