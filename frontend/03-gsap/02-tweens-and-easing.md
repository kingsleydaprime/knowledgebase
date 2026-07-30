# Tweens, Stagger, and Easing

A **tween** is a single animation instance — the object returned by `gsap.to()`/`.from()`/`.fromTo()`. This module covers the vars you'll reach for on almost every tween.

## Common tween vars

```js
gsap.to(".box", {
  x: 100,
  duration: 1,        // seconds (default 0.5)
  delay: 0.3,          // wait before starting
  ease: "power2.out",  // rate-of-change curve, see below
  repeat: 2,            // repeat 2 extra times (3 total plays); -1 = infinite
  yoyo: true,            // alternate direction on each repeat instead of snapping back
  repeatDelay: 0.5,       // pause between repeats
  onComplete: () => console.log("done"),
  onStart: () => console.log("started"),
});
```

`repeat` + `yoyo` together is the standard way to build a pulsing/breathing effect without manually reversing anything:

```js
gsap.to(".pulse", { scale: 1.1, duration: 0.6, repeat: -1, yoyo: true, ease: "sine.inOut" });
```

## Staggering multiple targets

When a selector matches multiple elements, GSAP animates them all in parallel by default. `stagger` offsets their start times so they cascade instead:

```js
gsap.to(".list-item", {
  y: 0,
  opacity: 1,
  duration: 0.5,
  stagger: 0.1,   // each item starts 0.1s after the previous one
});
```

`stagger` also accepts an object for non-linear patterns:

```js
gsap.to(".grid-item", {
  scale: 1,
  stagger: {
    each: 0.05,
    from: "center",   // ripple outward from the center element instead of index 0
    grid: "auto",       // auto-detect rows/cols for 2D stagger
  },
});
```

**Why this matters over manually looping with `setTimeout`**: GSAP computes all the offsets against a single internal clock, so they stay synchronized under throttling/tab-switching in a way that stacked `setTimeout` calls don't — and `from: "center"`/`"random"`/index patterns would be tedious to hand-roll.

## Easing

Easing controls the *rate* of change over the tween's duration — not just linear interpolation. GSAP's default is `"power1.out"`. The naming convention is `"<curve>.<direction>"`:

- **Curve** (intensity): `power1` → `power4` (increasingly dramatic), `sine`, `expo`, `circ`, `back` (overshoots), `elastic` (springs past and settles), `bounce`
- **Direction**:
  - `.in` — starts slow, accelerates (good for exits — something leaving picks up speed)
  - `.out` — starts fast, decelerates (good for entrances — something arriving settles in) — **this is the one you'll use most**
  - `.inOut` — slow-fast-slow (good for anything that starts and ends at rest, e.g. a modal that opens and will later close)

```js
gsap.to(".ball", { y: 300, duration: 1, ease: "bounce.out" });   // lands with a bounce
gsap.to(".panel", { x: 0, duration: 0.6, ease: "back.out(1.7)" }); // overshoots then settles, 1.7 = overshoot strength
gsap.to(".el", { rotation: 180, duration: 1, ease: "elastic.out(1, 0.3)" }); // spring physics
```

**Why `.out` is the default reach**: most UI animation is something entering or responding to a user action — a fast start reads as responsive, and the deceleration into rest reads as natural (this mirrors real-world physics — moving objects don't stop instantly, they decelerate). `linear` easing looks robotic for UI because nothing in the physical world moves at a perfectly constant rate.

Custom eases (`CustomEase`, cubic-bezier strings, or a plain function `t => t*t`) exist for cases the named curves don't cover, but the built-in library covers the vast majority of real use.

## Related
- [[01-intro|intro]] — `.to()`/`.from()`/`.fromTo()`
- [[03-timelines|timelines]] — sequencing tweens together
- [[07-performance-and-gotchas|performance and gotchas]]
