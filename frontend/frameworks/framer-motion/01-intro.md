# Framer Motion (Motion): Intro

Framer Motion is a declarative animation library built specifically for React. Where [[frontend/frameworks/gsap/README|GSAP]] is imperative — you call `gsap.to(el, {...})` and it mutates the DOM directly — Framer Motion expresses animation as **props on a component**, matching how React already thinks about UI: state changes, and the render describes what should be on screen.

## The rebrand: "Motion"

In 2024 the library was renamed **Motion** and made framework-agnostic (it now has a vanilla-JS API alongside React), but the React package is still published as `framer-motion` on npm (a `motion` package also exists as an alias). You'll see both names in docs and blog posts referring to the same library — this course uses "Framer Motion" since that's the more common name in existing React codebases, but expect `motion.dev` as the current docs domain rather than `framer.com`.

## Installing

```bash
npm install framer-motion
```

```jsx
import { motion } from "framer-motion";
```

## The `motion` component

Any HTML or SVG tag has a `motion.*` equivalent that accepts animation props on top of all its normal props:

```jsx
function Box() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    />
  );
}
```

- **`initial`** — the state before the component mounts (or before `animate` takes over)
- **`animate`** — the state to animate *to*
- **`transition`** — timing/easing config for how it gets there

This is the direct declarative equivalent of GSAP's `.from()` — see [[02-animate-props|animate props]] for the full breakdown.

## Why declarative animation fits React specifically

The core win: `animate` accepts values that can be **derived from component state or props**, so the animation automatically stays in sync with your data without any manual re-triggering logic:

```jsx
function Toggle({ isOpen }) {
  return (
    <motion.div
      animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
      transition={{ duration: 0.3 }}
    />
  );
}
```

Change `isOpen`, re-render, and Framer Motion detects the prop diff and animates between the old and new `animate` values automatically — no `useEffect`, no manually calling `.play()`/`.reverse()`. This is the fundamental difference in mental model from GSAP: GSAP animations are *commands you issue*; Framer Motion animations are *a description of state that gets interpolated automatically when the description changes*.

## When to reach for this vs. GSAP

Framer Motion is the natural default for component-driven UI animation in React — modals, toggles, list reordering, page transitions — because it composes with React's data flow. GSAP tends to win for anything timeline-heavy, scroll-driven scrollytelling, SVG path animation, or animating non-React/canvas content, because its timeline model and plugin ecosystem (ScrollTrigger, MotionPath, Flip) are more mature for those specific problems. Many real projects use both.

## Related
- [[02-animate-props|animate props]] — `initial`/`animate`/`exit`/`transition` in depth
- [[04-variants|variants]] — reusable, orchestrated animation state
- [[frontend/frameworks/gsap/README|GSAP]] — the imperative alternative
