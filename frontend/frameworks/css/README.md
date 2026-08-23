# css/ — Styling Approaches

**~1,250 words across 2 notes.** `[reference]`.

The concepts — cascade, specificity, tokens, modern CSS — are in [[frontend/05-styling/README|05-styling]]. **This is how specific tools do it.**

## Files
- [[frontend/frameworks/css/tailwind|Tailwind CSS]] — **[Intermediate]** — the utility-first argument and the honest objection, v4's move into CSS, `cn()`, **and the dynamic-class-name bug that fails silently**
- [[frontend/frameworks/css/sass|Sass]] — **[Intermediate]** — what it gave CSS, **how much is now native**, what it still does better, and whether to start a new project with it

## Choosing

| | Use when |
|---|---|
| **Tailwind** | Application UI, a component layer, consistency without a CSS review culture |
| **CSS Modules** | You want scoping and plain CSS. **The boring correct answer for a lot of projects** |
| **Sass** | Maintaining existing Sass, or you genuinely need loops to generate scales |
| **CSS-in-JS** | Highly dynamic styling — and mind the runtime cost and RSC fit |
| **vanilla-extract / Panda** | Types and zero runtime |

**Whatever you choose, choose one.** The bad outcome is Tailwind *and* styled-components *and* three global stylesheets — at which point nobody can predict what a change does → [[frontend/05-styling/01-css-architecture|CSS architecture]].

## Related
- [[frontend/05-styling/README|05-styling]] — the concepts
- [[frontend/frameworks/README|frameworks/]] · [[frontend/06-cross-cutting/01-accessibility|accessibility]]
