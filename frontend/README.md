# Frontend

**Mixed.** `03-gsap/`, `04-framer-motion/` and `05-threejs/` are full written courses. `01-react/` and `02-next/` are scaffold — **but the material they plan to cover is already written, in `projects/`.** See the index below before assuming it doesn't exist.

Framework-agnostic concepts live in [[concepts/02-frontend/README|concepts/frontend/]] — read that first. This folder is the framework-specific layer on top.

## Structure

1. [[frontend/01-react/README|01-react/]] — **[Intermediate]** — scaffold; see the index below for where React is actually taught
2. [[frontend/02-next/README|02-next/]] — **[Intermediate → Advanced]** — scaffold; ditto for Next.js
3. [[frontend/03-gsap/README|03-gsap/]] — **[Beginner → Advanced]** — full course: tweens, easing, timelines, ScrollTrigger, other plugins (Draggable/Flip/SplitText), React integration, performance
4. [[frontend/04-framer-motion/README|04-framer-motion/]] — **[Beginner → Advanced]** — full course: animate props, gestures, variants, AnimatePresence, layout animations, scroll-linked values, performance
5. [[frontend/05-threejs/README|05-threejs/]] — **[Beginner → Advanced]** — full course: scene/camera/renderer, geometries/materials, lighting, transformations, textures, controls/raycasting, React Three Fiber, performance

## ⚠️ The React/Next material exists — it's in `projects/`

A sweep in August 2026 found that `01-react/` + `02-next/` hold **419 words**, while the project learning logs hold **~44,000 words** teaching the same subjects against real code. A 105× ratio, and the scaffold READMEs were listing "planned" topics that had already been written.

Nothing has been moved — a project note teaches a topic *as it showed up in that project*, with the real bug attached, which is different from (and often better than) a standalone course note. But it should be findable from here. Index by topic:

| Topic | Where it's actually taught | Words |
|---|---|---|
| **App Router, routing, rendering model** | [[projects/nextvibe/learning/frontend/01-routing\|nextvibe — routing]] · [[projects/socioboom/learning/frontend/02-nextjs-app-router\|socioboom — App Router]] | 6.6k |
| **State management** (Redux Toolkit, RTK Query) | [[projects/nextvibe/learning/frontend/02-state-management\|nextvibe — state]] | 1.7k |
| **Server state** (TanStack Query, polling) | [[projects/socioboom/learning/frontend/05-data-fetching\|socioboom — data fetching]] | 1.4k |
| **Auth, tokens, login redirects** | [[projects/nextvibe/learning/frontend/03-auth\|nextvibe — auth]] | 2.9k |
| **Presigned uploads, error handling** | [[projects/nextvibe/learning/frontend/05-uploads-errors\|nextvibe — uploads]] · [[projects/socioboom/learning/frontend/09-media-uploads\|socioboom — media]] | 5.1k |
| **Real-time UI** (Socket.IO, chat, notifications) | [[projects/nextvibe/learning/frontend/06-realtime\|nextvibe — realtime]] | 7.4k |
| **Payments UI** | [[projects/nextvibe/learning/frontend/07-payments-games\|nextvibe — payments]] · [[projects/nextvibe/learning/frontend/09-payouts-and-multicurrency-ui\|payouts & multicurrency]] | 8.5k |
| **Performance & debugging** | [[projects/nextvibe/learning/frontend/08-performance-debugging\|nextvibe — performance]] | 1.7k |
| **TypeScript + React + JSX foundations** | [[projects/socioboom/learning/frontend/01-foundations\|socioboom — foundations]] | 1.3k |
| **Tailwind v4, shadcn/ui, dark mode** | [[projects/socioboom/learning/frontend/03-styling-and-ui\|socioboom — styling]] | 1.6k |
| **Project architecture & navigation** | [[projects/socioboom/learning/frontend/04-architecture\|socioboom — architecture]] | 1.3k |
| **Common pitfalls, honest UI** | [[projects/socioboom/learning/frontend/07-pitfalls-and-honest-ui\|socioboom — pitfalls]] | 1.1k |

**Tailwind and shadcn appear nowhere else in the vault** — that socioboom note is the only coverage of either.

### What should happen eventually

Distil the recurring material into `01-react/` and `02-next/` — the parts that are true regardless of which project you met them in — and leave the project-specific war stories where they are, cross-linked. That's the same split [[backend/README|backend/]] already uses: sections 01–07 hold in any language, `frameworks/` is how a given stack does it.

Until that happens, this index is the honest answer, and it beats a reader concluding the vault has nothing on Next.js.

## Also

`vue/` exists as an untouched, empty placeholder — not part of the current plan.

## Related
- [[concepts/02-frontend/README|frontend concepts]] — the framework-agnostic ideas these tracks implement
- [[projects/README|projects/]] — the full project↔domain map this index is one slice of
- [[frontend/interview/README|frontend interview bank]]
