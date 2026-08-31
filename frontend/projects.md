# Frontend — Projects

*The domain most vulnerable to tutorial-following. The reps that matter here are the ones with a **measurable** outcome — a Lighthouse score, a bundle size, an axe-core report — because "it looks right" is not a result.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 **Make one real page accessible** — keyboard-only navigation, visible focus, correct landmarks and labels, and a screen-reader pass. **Done when:** you complete the page's main task with the monitor off. Exercises: [[frontend/06-cross-cutting/README|accessibility]].

- 🟢 **Cut a bundle in half** — analyse a real build, find what's big (a date library? an icon set? a duplicated dep?), and fix it with code-splitting and tree-shaking. **Done when:** you have before/after numbers and know what each byte was. Exercises: [[frontend/07-practices/README|performance]].

- 🟢 **Fix a Core Web Vitals failure** — measure LCP/CLS/INP on something you built, find the cause, fix it. **Done when:** the field score moves, not just the lab score. Exercises: [[frontend/07-practices/README|practices]].

- 🟡 ⭐ **Build the same app three ways** — one feature, implemented with local state, then a server-state library (TanStack Query), then RSC/server-first. **Done when:** you can say which one you'd choose for which situation and why — that's the [[frontend/04-state-and-data/README|"server state is a cache, not state"]] insight earned rather than read.

- 🟡 **A component library with real constraints** — 8–10 components, typed props, documented in Storybook, tested, published to npm. **Done when:** you consume it from a separate project and it hurts, and you fix what hurt. Exercises: [[frontend/03-structuring-a-frontend/README|structuring]].

- 🟡 **Offline-first** — a real app that works with no network: optimistic updates, a sync queue, and conflict resolution. **Done when:** you can go offline, act, come back, and end in a correct state. Exercises: [[frontend/04-state-and-data/README|state and data]].

- 🟡 **Animate something properly** — a real interaction using GSAP or Framer Motion with `prefers-reduced-motion` honoured and no layout thrash. **Done when:** it holds 60fps in the performance panel. Exercises: [[frontend/frameworks/gsap/README|GSAP]], [[frontend/frameworks/framer-motion/README|Framer Motion]].

- 🔴 **Build your own React** — the guide is written: [[build-your-own-shit/13-your-own-react|13-your-own-react]]. **Done when:** `useState` works via an array and a cursor, and the hook rules have become consequences rather than rules.

- 🔴 ⭐ **A real-time collaborative editor** — multiple cursors, presence, and conflict-free merging with a CRDT (Yjs). **Done when:** two browsers edit simultaneously and converge. Exercises: [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution|CRDTs]], [[frontend/04-state-and-data/README|state]].

## If you only do one

**The same app three ways.** Frontend's hardest idea is where state should live, and it's the one thing you cannot learn by reading — you have to feel the third version get simpler.

## Related
- [[frontend/README|the frontend course]] · [[frontend/interview/README|interview bank]]
- [[frontend/frameworks/README|frameworks]] — React, Next, CSS, Three.js
- [[project-ideas|Project Ideas]] — the vault-wide index
