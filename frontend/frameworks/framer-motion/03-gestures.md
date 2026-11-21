---
id: a5a09173-77c0-4f44-a8d2-24a3f2a6620c
---

# Gestures: whileHover, whileTap, drag, whileInView

Framer Motion treats user interaction as just another animation trigger — a `while*` prop defines the state to animate to *while* a gesture is active, and it automatically animates back when the gesture ends. This is meaningfully less code than the CSS equivalent (`:hover`/`:active` pseudo-classes can't be animated with a spring, and JS event listeners for enter/leave would need manual state tracking).

## `whileHover` and `whileTap`
<!-- bite: b8d320d3-9ee4-486f-9747-c180a24e47df -->

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

No `useState` for hover/pressed tracking required — Framer Motion attaches the pointer listeners internally and manages the transition in and out for you.

## `whileInView`
<!-- bite: ed19981e-24df-4d56-b78c-7f19e151cc0f -->

Animates when the element scrolls into the viewport — Framer Motion's equivalent of GSAP's non-scrubbed [[frontend/frameworks/gsap/04-scrolltrigger|ScrollTrigger]] trigger, built on the browser's native `IntersectionObserver` rather than a scroll listener:

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}  // fire once, when 30% visible
/>
```

`viewport.once: true` prevents it from re-animating every time the element scrolls in and out — worth setting explicitly for entrance animations, since the default is to replay every time.

## `drag`
<!-- bite: 90d29b3b-f94e-421e-a1e6-b674d97c3eaa -->

```jsx
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: 0, bottom: 0 }}
  dragElastic={0.2}   // how much it can be pulled past the constraint boundary (0-1)
  onDragEnd={(event, info) => console.log(info.offset, info.velocity)}
/>
```

- `drag="x"` / `drag="y"` constrains to one axis instead of `drag={true}` (both)
- `dragConstraints` can also be a `ref` to another element, so drag is bounded by that element's actual box rather than fixed pixel values
- `dragMomentum` (default `true`) lets the element keep moving briefly after release based on release velocity, like GSAP's Draggable + InertiaPlugin combination (see [[frontend/frameworks/gsap/05-other-plugins|GSAP other plugins]])

## Combining gestures with variants
<!-- bite: 31724f8d-1ed0-4104-aee2-a730d1d0588b -->

`while*` props accept a variant name string instead of an inline object, which lets you define the hover/tap/drag states alongside `animate` in one place — see [[04-variants|variants]] for the full pattern:

```jsx
<motion.div
  variants={cardVariants}
  initial="rest"
  whileHover="hover"
  whileTap="tap"
/>
```

## Related
<!-- bite: 26fe1a67-eda7-49f0-bb7d-c73079c0d91a -->
- [[01-intro|intro]] — the `motion` component and declarative model
- [[04-variants|variants]] — naming gesture states for reuse
- [[07-scroll-animations|scroll animations]] — `useScroll`/`useTransform` for continuous scroll-linked values, vs. the one-shot `whileInView`
