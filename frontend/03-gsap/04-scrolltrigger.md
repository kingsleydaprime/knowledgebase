# ScrollTrigger

ScrollTrigger links any tween or timeline to scroll position — the animation plays, reverses, pins, or scrubs based on where the user has scrolled to, instead of running once on page load. It's the plugin behind almost every "animate in as you scroll" and "pin this section while content scrolls past it" effect on modern marketing sites.

Free since GSAP 3.13 (previously Club GreenSock-only) — see [[01-intro|intro]].

## Installing / registering

Plugins must be explicitly registered before use — GSAP doesn't auto-include them, to keep the core bundle small:

```js
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
```

## Basic trigger

```js
gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",     // element whose position determines when this fires
    start: "top 80%",     // when the trigger's top hits 80% down the viewport
    end: "top 20%",        // when the trigger's top hits 20% down the viewport
    scrub: true,             // tie animation progress directly to scroll position
    markers: true,            // visual debug markers — dev only, remove for production
  },
});
```

`start`/`end` strings follow `"<trigger-position> <viewport-position>"`. `"top 80%"` reads as: "when the trigger element's **top** edge reaches **80% down** the viewport."

## `scrub` vs. a one-shot animation

This is the key conceptual fork in ScrollTrigger:

- **No `scrub`** (default): the animation plays once, like a normal tween, the moment `start` is crossed. Scrolling back up reverses it if `toggleActions` allows that. Good for "fade this card in as it enters view."
- **`scrub: true`**: the animation's progress is *directly bound* to scroll position between `start` and `end` — scroll down, it advances; scroll up, it reverses; stop scrolling, it stops exactly there. `scrub: 0.5` adds a 0.5s smoothing lag instead of an instant 1:1 link. Good for "this element should visibly track my scroll," like a horizontal gallery or a parallax layer.

## Pinning

`pin: true` fixes the trigger element in place (like `position: fixed`) for the duration of the scroll range, letting content animate "on top of" a section that isn't scrolling away yet — the classic scrollytelling effect:

```js
gsap.timeline({
  scrollTrigger: {
    trigger: ".panel",
    start: "top top",
    end: "+=1000",   // pin for 1000px of additional scroll distance
    pin: true,
    scrub: 1,
  },
})
.to(".panel h1", { opacity: 0 })
.to(".panel .step-2", { opacity: 1 });
```

**Why pinning needs `end: "+=1000"` rather than a viewport-relative string**: pinning holds the element fixed while the *page* keeps scrolling underneath it — so the end condition is naturally expressed as "how much scroll distance should this pin last," not "what viewport position."

## `toggleActions`

Controls what happens at each of the four transitions (enter / leave / enter back / leave back) for non-scrubbed animations:

```js
scrollTrigger: {
  trigger: ".card",
  start: "top 80%",
  toggleActions: "play reverse play reverse",  // onEnter onLeave onEnterBack onLeaveBack
}
```

Common values per slot: `play`, `pause`, `resume`, `reverse`, `restart`, `none`. `"play none none reverse"` (play once going down, only reverse when scrolling back past the start) is a very common default for entrance animations.

## Cleanup matters

Every `ScrollTrigger` instance attaches scroll/resize listeners. In a single-page app where components mount/unmount (React, Next.js), failing to kill triggers on unmount leaves listeners firing against elements that no longer exist — see [[06-react-integration|react integration]] for the cleanup pattern (`useGSAP`'s automatic `revert()`, or manually calling `ScrollTrigger.getAll().forEach(t => t.kill())`).

## Related
- [[03-timelines|timelines]] — `scrollTrigger` can be attached to a whole timeline, not just one tween
- [[06-react-integration|react integration]] — registration and cleanup inside components
- [[07-performance-and-gotchas|performance and gotchas]] — scrub animations and layout thrash
