# Frontend — A Course, Not a Framework Tutorial

**Frontend is a domain. React is one way of building one.** This folder is organised that way: sections `01`–`07` are the course — true regardless of framework — and [[frontend/frameworks/README|frameworks/]] holds the implementations.

**Restructured August 2026**, mirroring [[backend/README|backend/]]. Previously the framework-agnostic concepts lived in `concepts/02-frontend/` while this folder held only library courses — so anyone looking for frontend material had to know to check two places. `concepts/README` had flagged the problem and said *"arguably belongs in frontend/. Not moved yet."* Now moved.

**~7,000 words of new course material** plus the existing library courses. `[reference]`.

> **The one idea:** a frontend runs on **hardware you don't own, over a network you don't control, for a user who won't read your error message.** Every difficulty in the domain follows from that.

## Sections

### [[frontend/01-foundations/README|01 — Foundations]]
1. [[frontend/01-foundations/01-what-a-frontend-is|What a Frontend Actually Is]] — **[Beginner]** — the four responsibilities, one thread does everything, **why the platform outlives the framework**
2. [[frontend/01-foundations/02-the-browser-and-the-dom|The Browser and the DOM]] — **[Beginner → Intermediate]** — URL to pixels, **reflow vs repaint vs composite**, delegation, the APIs worth knowing

### [[frontend/02-rendering/README|02 — Rendering]]
1. [[frontend/02-rendering/01-rendering-strategies|Rendering Strategies]] — CSR, SSR, SSG, ISR
2. [[frontend/02-rendering/02-hydration-and-the-server-boundary|Hydration and the Server Boundary]] ⭐ — **[Intermediate → Advanced]** — the window where a page looks ready and isn't, mismatches, streaming, islands, **what RSC actually changes**

### [[frontend/03-structuring-a-frontend/README|03 — Structuring a Frontend]]
1. [[frontend/03-structuring-a-frontend/01-components-and-composition|Components and Composition]] — **the prop-drilling trap**, feature folders, when to extract

### [[frontend/04-state-and-data/README|04 — State and Data]] ⭐
**The heart of the course.**
1. [[frontend/04-state-and-data/01-state-management|State Management]] · 2. [[frontend/04-state-and-data/02-data-fetching-and-server-state|Data Fetching and Server State]] — **server state is a cache, not state**; the race condition every hand-rolled fetch has

### [[frontend/05-styling/README|05 — Styling]]
1. [[frontend/05-styling/01-css-architecture|CSS Architecture]] — global scope and the specificity ratchet, what each solution fixes, modern CSS, tokens

### [[frontend/06-cross-cutting/README|06 — Cross-Cutting Concerns]]
1. [[frontend/06-cross-cutting/01-accessibility|Accessibility]] — **a correctness requirement, often a legal one**, and the area where most candidates are weakest

### [[frontend/07-practices/README|07 — Practices]]
1. [[frontend/07-practices/01-frontend-best-practices|Frontend Best Practices]] · 2. [[frontend/07-practices/02-performance|Performance]] — Core Web Vitals, network vs CPU, a budget in CI

---

## [[frontend/frameworks/README|frameworks/]] — the implementations

- **[[frontend/frameworks/react/README|react/]]** — the model, hooks, error boundaries
- **[[frontend/frameworks/next/README|next/]]** — App Router, RSC, caching
- **[[frontend/frameworks/css/README|css/]]** — **[[frontend/frameworks/css/tailwind|Tailwind]]** and **[[frontend/frameworks/css/sass|Sass]]**
- **[[frontend/frameworks/gsap/README|gsap/]]** · **[[frontend/frameworks/framer-motion/README|framer-motion/]]** · **[[frontend/frameworks/threejs/README|threejs/]]** — **full courses, 23 notes between them**

## [[frontend/interview/README|interview/]]
React and rendering · **the JS/TS language round** · state, data, accessibility and RSC.

---

## ⚠️ The React/Next depth is in `projects/`

**~44,000 words** teaching React and Next.js against real code, with the real bugs attached — routing, state, auth, uploads, real-time, payments, performance, Tailwind and shadcn.

**Nothing was moved, deliberately.** A project note teaches a topic *as it showed up in that project*, which is different from and often better than a standalone course note — and [[projects/README|projects/]] is where the vault's non-`[reference]` material lives. **The index is in [[frontend/frameworks/react/README|frameworks/react/]] and [[frontend/frameworks/next/README|frameworks/next/]].**

## The filing rule

- *True whether you use React, Vue or Svelte?* → a numbered section here
- *How one stack does it?* → [[frontend/frameworks/README|frameworks/]]
- *Belongs to no domain at all?* → [[concepts/README|concepts/]]
- *How it went in one of my projects?* → [[projects/README|projects/]]

## The honest note

**`[reference]` for the course sections, and genuinely not for the rest** — the animation and 3D courses came from building things, and `projects/` is real shipped work.

**What's missing, named rather than implied:** forms and validation at depth, i18n, error boundaries as a pattern, offline/PWA, testing (Playwright and Testing Library have no notes — a real gap given the [[learning/catalogue|hire track]] targets frontend), build tooling (Vite, bundlers, module formats), and Vue/Svelte beyond the comparison table.

**And the deepest gap is reps, not notes** — see [[project-ideas|project ideas]].

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[backend/README|Backend]] — the structure this mirrors, and the other half of a full-stack app
- [[concepts/README|concepts/]] · [[INTERVIEW|Interview index]] · [[BUILD-PLAN|Build Plan]]
