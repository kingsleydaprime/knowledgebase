# Animate Props: initial, animate, exit, transition

## `initial` and `animate`

```jsx
<motion.div
  initial={{ opacity: 0, scale: 0.8 }}
  animate={{ opacity: 1, scale: 1 }}
/>
```

`initial` sets the state at mount (before any animation runs); `animate` is the target state it animates to immediately after mounting. If `animate` changes on a later render (because state/props changed), Framer Motion animates from whatever the *current* rendered values are to the new `animate` values — you don't need to track "previous state" yourself, the DOM's current interpolated position is the implicit starting point.

Setting `initial={false}` skips the mount animation entirely — useful when a component's *first* render shouldn't animate (e.g. content that's already visible on page load and shouldn't visibly "pop in").

## `transition`

Controls timing/easing, and can be set globally on the component or per-property:

```jsx
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    duration: 0.5,
    ease: "easeOut",         // or a cubic-bezier array: [0.17, 0.67, 0.83, 0.67]
    delay: 0.2,
  }}
/>

// per-property overrides
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { duration: 0.8, ease: "easeOut" },
    opacity: { duration: 0.3 },
  }}
/>
```

### Spring vs. tween

Framer Motion's default transition type is actually a **spring**, not a fixed-duration tween — this is a meaningfully different model from GSAP, which is tween-first:

```jsx
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>
```

- `stiffness` — how strongly the spring pulls toward the target (higher = faster, snappier)
- `damping` — how much the spring's oscillation is resisted (higher = less bounce/overshoot)
- `mass` — inertia of the animated value (higher = slower to start and stop)

**Why spring is the default**: springs model physical motion continuously — if the target value changes again mid-animation (e.g. a draggable element released, then immediately re-dragged), a spring naturally picks up from the current velocity rather than restarting a fixed-duration curve from scratch. This is a much better match for interactive, interruptible UI than a duration-based tween. Use `type: "tween"` explicitly when you want an exact, predictable duration instead (e.g. matching a specific timing to a video or another synced element).

## `exit` (requires `AnimatePresence`)

`exit` defines how a component animates *out* when it's removed from the tree — but React normally unmounts a component immediately, before any exit animation could play. `exit` only works wrapped in `AnimatePresence`, covered in depth in [[05-animate-presence|AnimatePresence]]:

```jsx
<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

## Animating values that aren't natively CSS-animatable

Framer Motion can interpolate values a browser can't animate directly — like a `borderRadius` mismatch between shapes, or color strings, or even between different `display` values — by understanding the value types itself rather than delegating entirely to CSS animation. It also auto-detects units, so `x: 100` becomes `translateX(100px)` and `borderRadius: "50%"` interpolates correctly even from a pixel value.

## Related
- [[01-intro|intro]] — the `motion` component
- [[04-variants|variants]] — naming and orchestrating `animate` states across multiple children
- [[05-animate-presence|AnimatePresence]] — making `exit` actually work
