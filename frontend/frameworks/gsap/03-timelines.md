# Timelines

A **timeline** is a container that sequences multiple tweens against a single, controllable playhead. This is GSAP's biggest advantage over CSS animations: instead of manually calculating `animation-delay` on every element to make them line up, you build a timeline and add tweens to it in order — GSAP handles the offsets.

```js
const tl = gsap.timeline();

tl.to(".title", { opacity: 1, y: 0, duration: 0.5 })
  .to(".subtitle", { opacity: 1, y: 0, duration: 0.5 })
  .to(".cta-button", { opacity: 1, scale: 1, duration: 0.4 });
```

By default, each tween added to a timeline starts **immediately after the previous one ends** — no manual delay math required. If you reorder the array of elements to animate, the sequence just works; nothing needs recalculating.

## The position parameter

The real power is the optional third argument to `.to()`/`.from()`, which controls exactly when a tween starts relative to the timeline:

```js
tl.to(".a", { x: 100 })
  .to(".b", { x: 100 }, "-=0.3")   // start 0.3s before the previous tween ends (overlap)
  .to(".c", { x: 100 }, "+=0.2")   // start 0.2s after the previous tween ends (gap)
  .to(".d", { x: 100 }, 0)          // start at the absolute 0s mark (in parallel with .a)
  .to(".e", { x: 100 }, "<");        // start at the same time the previous tween started
```

| Syntax | Meaning |
|---|---|
| (omitted) | right after the previous tween ends |
| `"+=0.5"` | 0.5s gap after the previous tween ends |
| `"-=0.5"` | overlap 0.5s into the previous tween |
| `1.5` | absolute time, 1.5s from timeline start |
| `"<"` | same start time as the previous tween |
| `"<0.2"` | 0.2s after the previous tween's start |

## Labels

Labels are named markers on the timeline — useful for jumping to a section, or anchoring several tweens to the same point without hardcoding a time:

```js
tl.addLabel("introDone")
  .to(".header", { y: 0 }, "introDone")
  .to(".nav", { opacity: 1 }, "introDone+=0.2");
```

## Controlling playback

Because a timeline is a single object with a playhead, you get transport controls for the *entire sequence* at once:

```js
tl.play();
tl.pause();
tl.reverse();      // play backwards from current position
tl.seek(1.2);       // jump to 1.2s
tl.progress(0.5);   // jump to 50% through
tl.timeScale(2);    // play at 2x speed
```

This is the pattern behind scroll-driven and drag-driven animation — you're not writing new tweens as the user scrolls/drags, you're just calling `tl.progress()` or `tl.seek()` against a percentage derived from scroll position. [[04-scrolltrigger|ScrollTrigger]] is built entirely on this idea.

## Nesting timelines

Timelines can contain other timelines, which is how complex multi-stage sequences (intro → main content → outro) stay organized instead of becoming one giant flat list of tweens:

```js
const intro = gsap.timeline();
const main = gsap.timeline();

const master = gsap.timeline();
master.add(intro).add(main, "+=0.5");
```

## Related
- [[02-tweens-and-easing|tweens and easing]] — the vars used inside each `.to()` call
- [[04-scrolltrigger|ScrollTrigger]] — drives a timeline's `progress()` from scroll position
- [[06-react-integration|react integration]] — where to create timelines in a component lifecycle
