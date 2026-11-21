---
id: 894be408-9f3b-45ff-a277-c88b83097456
---

# Scroll-Linked Animations: useScroll, useTransform, useSpring

[[03-gestures|`whileInView`]] handles the common "animate once when it enters the viewport" case, but doesn't let a value track scroll position *continuously* — for that (a progress bar that fills as you scroll, a parallax layer, an element that rotates proportionally to scroll distance), Framer Motion provides motion-value hooks. This is the direct equivalent of GSAP's [[frontend/frameworks/gsap/04-scrolltrigger|`scrub: true`]].

## Motion values
<!-- bite: da791a2d-e382-46e1-869e-9e53f5553448 -->

A `MotionValue` is Framer Motion's internal representation of an animatable number — it updates outside React's render cycle for performance (no re-render on every scroll pixel), and can be read/subscribed to directly.

## `useScroll`
<!-- bite: 1d754dfc-6935-4e7f-86e3-70a87a04fbcf -->

```jsx
import { useScroll, motion } from "framer-motion";

function Page() {
  const { scrollYProgress } = useScroll(); // 0 at page top, 1 at page bottom

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}   // progress bar that fills as you scroll
      className="progress-bar"
    />
  );
}
```

Scoped to a specific element instead of the whole page, using a ref and offset config:

```jsx
const ref = useRef(null);
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"], // progress spans from "target enters" to "target fully exits"
});
```

`offset` pairs describe `[target-position, viewport-position]`, same underlying idea as GSAP's `start`/`end` strings — `"start end"` means "the target's start edge reaches the viewport's end edge."

## `useTransform`: remap a motion value's range
<!-- bite: 615e0251-b5ef-465f-ac3c-fad6fcb93f16 -->

`scrollYProgress` is always 0–1. `useTransform` maps that range onto whatever output range the animation actually needs — pixels, degrees, opacity, even non-numeric values like colors:

```jsx
import { useScroll, useTransform, motion } from "framer-motion";

function ParallaxImage() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref });

  const y = useTransform(scrollYProgress, [0, 1], [0, -150]);        // move up to -150px
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0]); // fade in, then out

  return <motion.img ref={ref} style={{ y, opacity }} />;
}
```

The three-stop array (`[0, 0.5, 1]` → `[0, 1, 0]`) is a common pattern for "fade in during the first half, fade out during the second" — `useTransform` interpolates piecewise between each pair of stops.

## `useSpring`: smooth out a jumpy input
<!-- bite: f4402257-652c-49a3-8873-df60ab7ca7ac -->

Raw scroll progress updates in discrete jumps (however often the browser fires scroll events), which can look mechanical for a value driving something like a rotating 3D-ish element. Wrapping a motion value in `useSpring` adds physical smoothing on top:

```jsx
const smoothProgress = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });
```

Same `stiffness`/`damping` vocabulary as spring `transition`s (see [[02-animate-props|animate props]]) — here applied to smooth a continuously-changing input value rather than a one-shot animation target.

## Why `style={{ y: motionValue }}` instead of `animate={{ y: ... }}`
<!-- bite: 9ba093f9-1898-48a5-8fa2-b981d9388df8 -->

Motion values bypass React's render cycle for a reason: scroll events can fire dozens of times per second, and re-rendering the component on every one (as `animate` prop changes normally would) would be wasteful and could itself cause jank. Passing a `MotionValue` directly to `style` lets Framer Motion update just that DOM property imperatively, without going through React's reconciliation at all — a genuinely different code path from every other example in this course.

## Related
<!-- bite: 2533294e-d511-40ab-a362-cccb0c4e4dca -->
- [[03-gestures|gestures]] — `whileInView` for the simpler one-shot case
- [[frontend/frameworks/gsap/04-scrolltrigger|GSAP: ScrollTrigger]] — the imperative equivalent, with pinning support Framer Motion doesn't have natively
- [[08-performance-and-gotchas|performance and gotchas]]
