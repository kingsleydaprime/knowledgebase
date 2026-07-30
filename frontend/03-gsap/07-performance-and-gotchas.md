# Performance and Gotchas

## Animate transforms and opacity, not layout properties

This is the single most important performance rule and applies to CSS animation generally, not just GSAP — covered briefly in [[01-intro|intro]], expanded here:

```js
// Cheap: compositor-only, no reflow
gsap.to(".box", { x: 100, y: 50, scale: 1.2, opacity: 0.5 });

// Expensive: triggers layout recalculation on every frame
gsap.to(".box", { left: 100, top: 50, width: 200 });
```

`x`/`y` are GSAP's shorthand for `translateX`/`translateY` — using them instead of `left`/`top` means the browser can run the whole animation on the compositor thread (GPU-accelerated, independent of the main thread's layout/paint work). `width`/`height`/`top`/`left`/`margin` all force a reflow (layout recalculation) on every single frame, which is where visible jank comes from on lower-powered devices.

## `will-change` — use sparingly, remove after

Hinting the browser to promote an element to its own compositor layer *before* an animation starts can help:

```css
.box { will-change: transform, opacity; }
```

But leaving `will-change` on permanently, or applying it to many elements, backfires — it reserves GPU memory for every hinted element indefinitely, and too many layers can *slow down* compositing rather than speed it up. GSAP itself handles layer promotion reasonably well automatically for transform animations; reach for manual `will-change` only if profiling actually shows a problem, and remove it via `onComplete` once the animation finishes.

## Killing tweens and memory leaks

Every tween is tracked internally until it's killed or completes. In an SPA context, uncleaned tweens/timelines/ScrollTriggers targeting removed DOM nodes are a real leak:

```js
const tween = gsap.to(".box", { x: 100 });
tween.kill();                          // stop and discard this one tween

gsap.killTweensOf(".box");             // kill all tweens targeting this selector

ScrollTrigger.getAll().forEach(st => st.kill()); // nuke all ScrollTriggers
```

In React, `useGSAP`'s automatic context cleanup (see [[06-react-integration|react integration]]) handles this for you — this matters most when writing plain `useEffect` + imperative GSAP calls without that hook.

## `gsap.context()` for manual scoping/cleanup

If not using `useGSAP`, `gsap.context()` is the lower-level primitive it's built on — groups animations so they can all be reverted together:

```js
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to(".box", { x: 100 });
  }, containerRef);

  return () => ctx.revert(); // kills everything created inside, resets inline styles
}, []);
```

## Forced reflow from reading layout mid-animation

Reading a layout-dependent property (`element.offsetWidth`, `getBoundingClientRect()`) *while* a transform animation is running forces the browser to synchronously flush pending style changes to answer the query — a "layout thrash" that can stall the animation for a frame. Batch reads and writes separately (read all needed values first, then apply all animations) rather than interleaving them in a loop.

## `ease` typos fail silently

Passing an invalid ease string (a typo, or a plugin-specific ease that wasn't registered) doesn't throw — GSAP just falls back to the default ease and the animation still runs, just not the way you expected. If a custom ease "isn't working," check the spelling and that the required plugin (e.g. `CustomEase`) is registered before assuming the API is broken.

## Related
- [[01-intro|intro]] — transform vs. layout properties
- [[04-scrolltrigger|ScrollTrigger]] — scrub animations are especially sensitive to reflow cost
- [[06-react-integration|react integration]] — `useGSAP` context/cleanup
