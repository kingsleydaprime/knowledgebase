# CSS Architecture

> **[Intermediate]** · The cascade, why CSS at scale is hard, and what each solution is actually solving.

## Why CSS is hard at scale

**Not the syntax. The two properties that make it different from any other code you write:**

**Everything is global.** A selector written anywhere applies everywhere it matches. **There is no module boundary**, so a rule added in one feature can restyle another.

**Specificity resolves conflicts, and it's a ranking, not a scope.**

```
inline style  >  #id  >  .class / [attr] / :pseudo  >  element  >  *
```

**The failure mode this produces is a one-way ratchet:** someone can't override a rule, so they add `#app .card .title`. Now the *next* person needs something stronger. Eventually `!important`, and then `!important` on top of that.

**Every solution below is an answer to one or both of those problems.**

## The solutions, and what each actually fixes

| | Fixes | Costs |
|---|---|---|
| **BEM** (naming convention) | Global collisions, **by discipline** | Nothing enforces it |
| **CSS Modules** | Global collisions, **mechanically** | Build step; awkward for dynamic values |
| **CSS-in-JS** (styled-components, Emotion) | Collisions + dynamic styling | **Runtime cost**; poor RSC fit |
| **Utility-first** (Tailwind) | Collisions, **and the naming problem entirely** | Verbose markup; learning curve |
| **Zero-runtime CSS-in-JS** (vanilla-extract, Panda) | Collisions + types, no runtime | Newer, smaller ecosystems |

**BEM** — `block__element--modifier`. Flat specificity by convention. Works, and depends entirely on everyone following it.

**CSS Modules** — the build tool rewrites `.title` to `.Card_title__a3f9`. **Scoping without a runtime**, and it's still the boring correct answer for a lot of projects.

**CSS-in-JS** — colocation and full access to props. **The runtime cost is real** — generating and injecting styles during render — and it fits Server Components poorly, which is why the ecosystem has moved toward zero-runtime alternatives.

**Utility-first** — → [[frontend/frameworks/css/tailwind|Tailwind]]. The genuine insight: **most CSS problems are naming problems**, and utilities remove naming.

## Modern CSS you may not be using

**A lot of what needed a preprocessor or JavaScript is now native**, and this is the fastest-moving part of the platform:

```css
:root { --brand: #0055ff; --space: 1rem; }        /* custom properties — RUNTIME, unlike Sass vars */
.card { padding: var(--space); }

.card { container-type: inline-size; }            /* container queries */
@container (min-width: 400px) { .card { display: grid; } }

.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

.parent:has(> img) { padding: 0; }                /* :has() — the "parent selector" */

@layer base, components, utilities;               /* cascade layers — explicit precedence */

.a { color: light-dark(#111, #eee); }             /* respects the colour scheme */
```

**Custom properties are runtime values**, which is the key difference from Sass variables — they cascade, they can be changed by JavaScript, and they're how theming and dark mode are done now without duplicating a stylesheet.

**Container queries are the bigger deal than they look.** Media queries ask about the *viewport*; a reusable component doesn't care about the viewport, it cares about **its own** width. Container queries finally make components genuinely context-independent.

**`@layer` fixes the specificity ratchet** by letting you declare precedence explicitly instead of escalating selectors.

## Design tokens

**Name the decisions, not the values:**

```css
--color-primary: #0055ff;      /* not --blue-500 */
--space-md: 1rem;
--radius-sm: 4px;
```

**Semantic names survive a rebrand; literal ones don't.** `--blue-500` used for a warning is a lie the day the brand changes.

**Tokens are the boundary between design and code**, and they're what design-system tooling (Style Dictionary, Figma variables) exchanges → [[foundations/systems-engineering/04-architecture-and-interfaces|interfaces]].

## Responsive, and the two habits

**Mobile-first**: write the small-screen styles unprefixed, then add complexity with `min-width`. Simpler base, less to override.

**Fluid over fixed breakpoints** where you can:
```css
font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem);
```

**Test at 200% browser zoom and 320 px width.** Both are real users, both break layouts that only got tested at desktop defaults, and one of them is an accessibility requirement → [[frontend/06-cross-cutting/README|accessibility]].

## What to actually do

**A new project:** Tailwind if the team is on board; CSS Modules if not. Both are defensible; **the wrong answer is neither** — no convention at all.

**An existing project:** adopt `@layer` and custom properties without rewriting anything. Both are additive.

**Whatever you choose, choose one.** The genuinely bad outcome is a codebase with Tailwind, styled-components, three global stylesheets and a `!important` graveyard — because then no one can predict what a change will do.

## Related
- [[frontend/frameworks/css/README|css/]] — Tailwind and Sass specifically
- [[frontend/01-foundations/02-the-browser-and-the-dom|the browser]] — why CSS blocks rendering
- [[frontend/06-cross-cutting/README|accessibility]] — colour contrast, zoom, motion

*Source: [reference] — written Aug 2026.*
