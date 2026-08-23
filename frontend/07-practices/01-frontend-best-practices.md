# Frontend Best Practices — Accessibility, Performance, Component Design

The practices that separate a frontend that works on your machine, with your mouse, on your fast connection, from one that actually works for everyone it's shipped to.

## Accessibility (a11y) — not an edge case

A meaningful fraction of users rely on assistive technology (screen readers, keyboard-only navigation, voice control) or simply have different needs (low vision, motor impairments) — accessibility isn't a niche feature, it's making the product actually usable by the people who are already trying to use it.

- **Semantic HTML** — using `<button>` for a button and `<nav>` for navigation, not a `<div>` with a click handler styled to look like one. Semantic elements come with built-in keyboard behavior and screen-reader announcements for free; a styled `<div>` provides neither unless you manually reimplement all of it.
- **Keyboard navigation** — every interactive element should be reachable and operable via keyboard alone (Tab, Enter, Space, arrow keys where appropriate) — a real, common way many users navigate, not just an edge case.
- **ARIA attributes** — supplement semantic HTML when it genuinely isn't sufficient (`aria-label` for an icon-only button with no visible text, `aria-live` for content that updates dynamically without a page reload) — a supplement to semantic HTML, not a replacement for it; reaching for ARIA before exhausting plain semantic HTML is a common overuse mistake.
- **Color contrast** — text needs sufficient contrast against its background to be readable for users with low vision or color blindness — checkable with automated tools, and a common, easy-to-fix accessibility failure when overlooked.

```html
<!-- inaccessible: no keyboard support, no screen-reader semantics -->
<div onclick="submitForm()">Submit</div>

<!-- accessible: keyboard support and semantics come for free -->
<button onclick="submitForm()">Submit</button>
```

## Performance — what users actually feel

- **Bundle size** — every kilobyte of JavaScript has to be downloaded, parsed, and executed before the page is interactive (see [[frontend/02-rendering/01-rendering-strategies|rendering strategies]]'s hydration section) — code-splitting (loading only the JavaScript a given page actually needs, not the entire app's bundle upfront) is the standard fix for apps that have grown large.
- **Lazy loading** — deferring the loading of images, components, or routes until they're actually needed (about to scroll into view, or about to be navigated to) rather than loading everything upfront.
- **Core Web Vitals** — Google's standardized performance metrics, worth knowing by name since they've become an industry-common vocabulary: **LCP** (Largest Contentful Paint — how long until the main content is visible), **CLS** (Cumulative Layout Shift — how much visible content unexpectedly jumps around as the page loads), **INP** (Interaction to Next Paint — how responsive the page feels to actual clicks/taps).
- **Image optimization** — serving appropriately sized, modern-format (WebP/AVIF) images instead of a single oversized original — frequently one of the single highest-impact, lowest-effort performance fixes available on a typical content-heavy page.

## Component design

- **Composition over configuration** — building complex UI by combining small, focused components rather than one large component with a growing pile of conditional props controlling its every possible variation. A component with 15 boolean props is usually a sign it should be several smaller, composable components instead.
- **Colocation** — keeping a component's logic, styles, and tests physically near each other (often in the same folder) rather than separated into far-apart, parallel directory structures organized purely by file type — easier to find everything relevant to one component when it's actually all in one place.
- **Prop drilling awareness** — passing data down through several intermediate components that don't themselves use it, purely to reach a distant descendant, is a sign that data might belong in shared state instead (see [[frontend/04-state-and-data/01-state-management|state-management]]) — though as covered there, reaching for global state before this genuinely becomes painful is its own, opposite mistake.

## Gotchas

- Accessibility is often treated as a final polish pass instead of a design-time consideration — retrofitting it onto an already-built, non-semantic UI is significantly more work than building with semantic HTML and keyboard support from the start.
- Performance optimization applied without measuring first (profiling, Lighthouse, real user monitoring) risks optimizing something that was never actually the bottleneck — measure before optimizing, the same discipline that applies to backend performance work.
- A component broken down purely for the sake of "small components" without a genuine reuse or clarity benefit adds indirection (more files to jump between to understand one flow) without a real payoff — composition should serve clarity/reuse, not be a rule followed for its own sake.

## Related
- [[frontend/02-rendering/01-rendering-strategies|rendering strategies]]
- [[frontend/04-state-and-data/01-state-management|state-management]]
- [[cybersecurity/04-web-security/README|web-security]]
