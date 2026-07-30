# Gestures: whileHover, whileTap, drag, whileInView

Framer Motion treats user interaction as just another animation trigger — a `while*` prop defines the state to animate to *while* a gesture is active, and it automatically animates back when the gesture ends. This is meaningfully less code than the CSS equivalent (`:hover`/`:active` pseudo-classes can't be animated with a spring, and JS event listeners for enter/leave would need manual state tracking).

## `whileHover` and `whileTap`

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

Animates when the element scrolls into the viewport — Framer Motion's equivalent of GSAP's non-scrubbed [[../03-gsap/04-scrolltrigger|ScrollTrigger]] trigger, built on the browser's native `IntersectionObserver` rather than a scroll listener:

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}  // fire once, when 30% visible
/>
```

`viewport.once: true` prevents it from re-animating every time the element scrolls in and out — worth setting explicitly for entrance animations, since the default is to replay every time.

## `drag`

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
- `dragMomentum` (default `true`) lets the element keep moving briefly after release based on release velocity, like GSAP's Draggable + InertiaPlugin combination (see [[../03-gsap/05-other-plugins|GSAP other plugins]])

## Combining gestures with variants

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
- [[01-intro|intro]] — the `motion` component and declarative model
- [[04-variants|variants]] — naming gesture states for reuse
- [[07-scroll-animations|scroll animations]] — `useScroll`/`useTransform` for continuous scroll-linked values, vs. the one-shot `whileInView`
