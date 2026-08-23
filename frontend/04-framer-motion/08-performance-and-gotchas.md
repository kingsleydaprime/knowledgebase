# Performance and Gotchas

## Animate transforms and opacity, same rule as everywhere else

The [[frontend/03-gsap/07-performance-and-gotchas|compositor-only properties rule]] applies identically here: `x`, `y`, `scale`, `rotate`, `opacity` are cheap; `width`, `height`, `top`, `left` force layout recalculation every frame. Framer Motion's `layout` prop (see [[06-layout-animations|layout animations]]) exists specifically so you *can* animate layout-affecting changes while still only touching `transform` under the hood — reach for it instead of literally animating `width`/`height` whenever the two achieve the same visual result.

## `LazyMotion`: reducing bundle size

The full `motion` import includes gesture, drag, and layout animation support whether or not a given component uses them. For projects sensitive to bundle size, `LazyMotion` + the `m` component load only a minimal animation core up front, with extra features loaded on demand:

```jsx
import { LazyMotion, domAnimation, m } from "framer-motion";

function App() {
  return (
    <LazyMotion features={domAnimation}>
      <m.div animate={{ opacity: 1 }} />
    </LazyMotion>
  );
}
```

Worth knowing this exists, but not worth reaching for until bundle size is an actual measured problem — `motion.div` directly is the right default for most projects.

## Server-side rendering / hydration

`motion` components render real DOM elements with `initial` styles applied inline — this is generally SSR-safe (Next.js App Router works fine with `"use client"` on the file), but a common visible glitch is a flash where the `initial` state renders on the server/first paint before JS hydrates and the animation kicks in. If the "before" state (e.g. `opacity: 0`) is visually jarring even briefly, consider whether that specific element needs an entrance animation at all versus just an inherent part of the layout.

## `layout` animations and `position: sticky`/`fixed`

Elements using `position: sticky` or `fixed` inside a `layout`-animated parent can behave unexpectedly, since FLIP-style layout animation works by measuring bounding boxes relative to normal document flow — sticky/fixed positioning breaks that assumption. If a `layout` animation on a container with sticky children looks wrong, that's the likely cause, not a bug in the animation values themselves.

## Don't animate values that don't need `motion`

A very common overcorrection: wrapping every element in `motion.div` "just in case," even ones with no `initial`/`animate`/`whileHover` props at all. A `motion` component carries real overhead (motion value tracking, gesture listener setup) compared to a plain `<div>` — only use it on elements that are actually being animated.

## Debugging: "my animation isn't running"

The most common real-world causes, in order of likelihood:
1. Missing/mismatched `key` inside `AnimatePresence` (see [[05-animate-presence|AnimatePresence]]) — React treats it as an update, not a mount/unmount, so no enter/exit fires
2. `exit` defined without any `AnimatePresence` wrapper at all
3. A `variants` object where the child's variant key doesn't match any key the parent is currently in
4. Animating a property that's also being set via a competing CSS rule with higher specificity (Framer Motion sets inline styles, which usually win, but `!important` rules elsewhere in the app can override them)

## Related
- [[06-layout-animations|layout animations]]
- [[07-scroll-animations|scroll animations]]
- [[frontend/03-gsap/07-performance-and-gotchas|GSAP performance and gotchas]] — the shared underlying browser-rendering concepts
