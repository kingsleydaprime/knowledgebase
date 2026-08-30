# frontend/frameworks/ — The Implementations

**Sections `01`–`07` are the course — true regardless of framework. This folder is how a given stack does it.** Same convention as [[backend/frameworks/README|backend/frameworks/]].

**Not numbered** — there's no reading order. Pick the one you're using.

## The map

| | Covers | Status |
|---|---|---|
| **[[frontend/frameworks/react/README\|react/]]** | The React model, hooks, error boundaries | 2 notes + a routed index into `projects/` |
| **[[frontend/frameworks/next/README\|next/]]** | App Router, RSC, caching, `next/image` | Scaffold + a routed index |
| **[[frontend/frameworks/css/README\|css/]]** | **Tailwind, Sass** | 2 notes |
| **[[frontend/frameworks/sanity/README\|sanity/]]** | **Headless CMS** — the document model, GROQ, Portable Text | **Full course — 3 notes** |
| **[[frontend/frameworks/gsap/README\|gsap/]]** | Tweens, timelines, ScrollTrigger, plugins | **Full course — 7 notes** |
| **[[frontend/frameworks/framer-motion/README\|framer-motion/]]** | Animate props, gestures, variants, layout | **Full course — 8 notes** |
| **[[frontend/frameworks/threejs/README\|threejs/]]** | Scene/camera/renderer, materials, R3F | **Full course — 8 notes** |

**Note the shape of that table.** The animation and 3D courses are the deepest material here — unusual, and worth leaning into: **most frontend candidates cannot talk about the compositor, `requestAnimationFrame`, or why `transform` beats `top`** → [[frontend/interview/README|interview prep]].

## The same concepts, per stack

| Course concept | React | Vue | Svelte |
|---|---|---|---|
| **Component** | function returning JSX | SFC | `.svelte` file |
| **Local state** | `useState` | `ref` / `reactive` | `$state` (runes) |
| **Derived value** | compute in render | `computed` | `$derived` |
| **Side effect** | `useEffect` | `watchEffect` | `$effect` |
| **Ambient value** | Context | `provide`/`inject` | context API |
| **Reactivity model** | **re-run the component** | **fine-grained proxies** | **compiled fine-grained** |

**That last row is the real difference.** React re-runs your whole component function and diffs; Vue and Svelte track dependencies precisely and update only what changed. **It's why React needs `memo` and the others largely don't** → [[frontend/frameworks/react/01-the-react-model|the React model]].

## The filing rule

- *True whether you use React, Vue or Svelte?* → a numbered section in [[frontend/README|the course]]
- *How one stack does it?* → here
- *How it went in one of my projects?* → [[projects/README|projects/]]

## Related
- [[frontend/README|the frontend course]] · [[backend/frameworks/README|backend/frameworks/]]
