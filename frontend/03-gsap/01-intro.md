# GSAP: Intro

GSAP (GreenSock Animation Platform) is a JavaScript animation engine that animates *any* numeric property on *any* object — DOM elements, SVG, Canvas/WebGL objects, plain JS objects — not just the CSS-animatable subset a browser natively supports. That's the core reason it exists: CSS transitions/animations can only tween `transform`, `opacity`, and a handful of other properties smoothly, and coordinating multiple elements with precise timing in raw CSS gets unwieldy fast. GSAP gives you one consistent API and a real timeline model for all of it.

As of GSAP 3.13 (2025), GreenSock was acquired by Webflow and **every plugin — including ScrollTrigger, SplitText, MorphSVG, Draggable, the works — is now free** for everyone, no Club GreenSock membership required. So the modules in this course cover the full toolkit without any "this part is paywalled" caveats.

## Installing

```bash
npm install gsap
```

```js
import gsap from "gsap";
```

No build step is required — GSAP works directly in a `<script>` tag too — but in a React/Next.js project (the track this sits under) you'll almost always import it as a module.

## The core method: `gsap.to()`

```js
gsap.to(".box", {
  x: 200,          // animate translateX by 200px
  rotation: 360,    // full spin
  duration: 1.5,    // seconds
  ease: "power2.out",
});
```

`gsap.to()` animates **from the element's current state to the values you specify**. Under the hood, GSAP reads the current computed style, figures out the delta, and interpolates every listed property over `duration` seconds, applying the `ease` curve to the rate of change rather than a linear crawl.

There are three sibling methods, all sharing the same property syntax:

| Method | Animates | Use when |
|---|---|---|
| `gsap.to(target, vars)` | current → specified values | the normal case — "animate this to..." |
| `gsap.from(target, vars)` | specified values → current | entrance animations — "it arrives from off-screen/invisible" |
| `gsap.fromTo(target, fromVars, toVars)` | explicit start → explicit end | you need full control over both ends, e.g. inside a loop where "current state" isn't reliable |
| `gsap.set(target, vars)` | instantly, no animation | set an initial state before a `.from()` runs, or apply styles with GSAP's unit handling |

```js
// entrance: fade + slide up from below, into place
gsap.from(".card", { y: 50, opacity: 0, duration: 0.8, ease: "power2.out" });

// explicit control over both ends — useful when replaying the same animation
gsap.fromTo(".card",
  { y: 50, opacity: 0 },
  { y: 0, opacity: 1, duration: 0.8 }
);
```

**Why `.from()` is a common gotcha**: it computes the "current" value at the moment it *runs*, not the moment it's defined. If the element has already moved by the time the animation executes (e.g. inside a delayed callback), you can get a visible jump. `.fromTo()` avoids that ambiguity entirely by pinning both ends explicitly.

## What GSAP animates well vs. what to avoid

GSAP can technically tween any numeric CSS property, but not all properties are equal performance-wise. Animating `transform` (x/y/scale/rotation) and `opacity` runs on the compositor thread — cheap, smooth, no layout recalculation. Animating `width`, `height`, `top`, `left`, or other layout-affecting properties forces the browser to reflow on every frame — expensive, and the reason janky animations happen. Prefer `x`/`y` (GSAP's shorthand for `translateX`/`translateY`) over `left`/`top` whenever position is what you're animating. More on this in [[07-performance-and-gotchas|performance and gotchas]].

## Related
- [[02-tweens-and-easing|tweens and easing]] — the full property/duration/stagger vocabulary
- [[03-timelines|timelines]] — sequencing multiple tweens
- [[../02-next/README|Next.js]] — GSAP typically runs inside `useEffect`/`useGSAP` in a React/Next context, see [[06-react-integration|react integration]]
