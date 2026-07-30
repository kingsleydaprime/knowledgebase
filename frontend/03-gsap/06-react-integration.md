# GSAP in React

GSAP predates React and doesn't know anything about components, so using it inside React means bridging two different mental models: GSAP wants to imperatively grab a DOM node and mutate it; React wants to declaratively describe what the DOM should look like. Refs are the bridge.

## The naive approach, and why it's incomplete

```jsx
useEffect(() => {
  gsap.to(".box", { x: 100 });
}, []);
```

This *works* but has two real problems:
1. **Selector scope** — `".box"` matches *any* `.box` in the whole document, not just this component's instance. In a list of repeated components, this breaks immediately.
2. **No cleanup** — tweens, timelines, and ScrollTriggers all attach listeners/state that outlive the component if you don't kill them on unmount, especially painful in Next.js dev mode where effects run twice (Strict Mode) or in any route that mounts/unmounts the component repeatedly.

## `useGSAP`: the official hook

GSAP ships a first-party React hook (`@gsap/react`) that solves both problems automatically:

```bash
npm install @gsap/react
```

```jsx
import { useRef } from "react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

function Card() {
  const container = useRef(null);

  useGSAP(() => {
    // gsap.utils.selector-style scoping: only matches .box inside `container`
    gsap.to(".box", { x: 100, duration: 1 });
  }, { scope: container });

  return (
    <div ref={container}>
      <div className="box">...</div>
    </div>
  );
}
```

What `useGSAP` does that a plain `useEffect` doesn't:
- **`scope`** automatically scopes selector text (`".box"`) to descendants of the given ref, so two `<Card>` instances on the same page don't animate each other's boxes.
- **Automatic cleanup** — every tween/timeline/ScrollTrigger created inside the callback is tracked in a GSAP `Context`, and reverted (killed, and DOM styles reset) automatically on unmount. You get this for free without writing a `return () => tl.kill()` yourself.
- **Dependency array support**, same semantics as `useEffect`'s second argument, for re-running the animation when specific values change.

## Refs instead of selector strings (the more idiomatic pattern)

Once you're inside a component, prefer refs over string selectors — it avoids any ambiguity about scope and is more "React-ish":

```jsx
function Card() {
  const container = useRef(null);
  const boxRef = useRef(null);

  useGSAP(() => {
    gsap.to(boxRef.current, { x: 100, duration: 1 });
  }, { scope: container });

  return (
    <div ref={container}>
      <div ref={boxRef} className="box">...</div>
    </div>
  );
}
```

## ScrollTrigger + Next.js specifics

Register plugins once, and be aware ScrollTrigger measures the DOM — if content loads asynchronously (images, fonts) after the trigger is created, positions can be stale. Call `ScrollTrigger.refresh()` after any layout-affecting async load, and in Next.js App Router, do plugin registration and animation setup client-side only (`"use client"` at the top of the file) since GSAP touches the DOM directly and has no meaning during server rendering.

```jsx
"use client";

import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, useGSAP);
```

## Related
- [[03-timelines|timelines]] — what you'll typically build inside `useGSAP`
- [[04-scrolltrigger|ScrollTrigger]] — registration/cleanup concerns are sharpest here
- [[../02-next/README|Next.js]] — `"use client"` boundary and App Router specifics
