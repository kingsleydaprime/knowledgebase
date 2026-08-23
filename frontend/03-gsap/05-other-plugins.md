# Other Plugins: Draggable, Flip, SplitText, MotionPath

Beyond ScrollTrigger, GSAP ships several special-purpose plugins — all free as of GSAP 3.13 (see [[01-intro|intro]]). Each targets a specific hard problem that would be painful to hand-roll.

## Draggable

Makes an element draggable with physics (inertia, bounds, snapping) and integrates directly with tweens/timelines:

```js
import { Draggable } from "gsap/Draggable";
gsap.registerPlugin(Draggable);

Draggable.create(".slider-handle", {
  type: "x",             // constrain to horizontal movement
  bounds: ".slider-track", // stay within this element's box
  inertia: true,           // requires the (also free) InertiaPlugin for momentum/throw physics
  onDrag: function () {
    console.log(this.x);   // current x position during drag
  },
});
```

## Flip

Solves the "animate a layout change" problem: an element that instantly jumps to a new position/size (e.g. it moved to a different parent, or a CSS class changed its layout) can instead be made to *animate smoothly* between the two states.

```js
import { Flip } from "gsap/Flip";
gsap.registerPlugin(Flip);

// 1. capture state BEFORE the layout change
const state = Flip.getState(".card");

// 2. make the actual DOM/class change (instant, no animation)
document.querySelector(".card").classList.add("expanded");

// 3. animate FROM the captured state TO the new layout
Flip.from(state, { duration: 0.6, ease: "power2.inOut" });
```

**Why this exists**: browsers can't animate between two different layout states directly — you can't tween "this element used to be 100px in the DOM flow, now it's `position: fixed` full-screen" with a normal tween. Flip works by measuring the First and Last states, Inverting the visual result with a transform so it *looks* like it hasn't moved yet, then letting the browser Play a normal transform tween back to the real position — hence the name (First, Last, Invert, Play). This is the same core idea as the [[frontend/04-framer-motion/06-layout-animations|`layout` prop in Framer Motion]], implemented explicitly instead of automatically.

## SplitText

Splits text into individual characters, words, or lines (each wrapped in its own `<div>`/`<span>`) so they can be animated independently — the mechanism behind staggered letter-by-letter reveal effects:

```js
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);

const split = new SplitText(".headline", { type: "chars, words" });

gsap.from(split.chars, {
  opacity: 0,
  y: 20,
  stagger: 0.02,
  ease: "power2.out",
});
```

## MotionPathPlugin

Animates an element along an arbitrary SVG path, rather than a straight line:

```js
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
gsap.registerPlugin(MotionPathPlugin);

gsap.to(".rocket", {
  motionPath: {
    path: "#flightPath",   // reference to an SVG <path> element
    align: "#flightPath",
    autoRotate: true,       // rotate the element to follow the path's direction
  },
  duration: 4,
  ease: "power1.inOut",
});
```

## When to reach for a plugin vs. plain tweens

All four solve problems that are either impossible or very fiddly with `.to()`/`.from()` alone: drag physics, layout-change animation, per-character text splitting, and curved-path motion each require dedicated measurement/DOM logic under the hood. If you find yourself manually calculating character offsets or writing your own drag-with-momentum math, that's usually the sign a plugin already covers it.

## Related
- [[01-intro|intro]] — plugin registration pattern
- [[04-scrolltrigger|ScrollTrigger]] — the plugin you'll use most often
- [[frontend/04-framer-motion/06-layout-animations|Framer Motion layout animations]] — the declarative equivalent of Flip
