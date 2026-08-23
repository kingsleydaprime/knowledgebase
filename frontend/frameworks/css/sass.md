# Sass

> **[Intermediate]** · What it gave CSS, how much of that is now native, and whether to start a new project with it.

## What it was for

**Sass predates most of modern CSS**, and it existed because CSS had no variables, no nesting, no modularity and no functions.

```scss
$brand: #0055ff;
$space: 1rem;

@mixin card($padding: $space) {
  padding: $padding;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,.1);
}

.card {
  @include card;
  &__title { font-weight: 600; }        // BEM-friendly nesting
  &:hover  { box-shadow: 0 4px 8px rgba(0,0,0,.15); }
}
```

**Variables, nesting, mixins, functions, partials, loops** — genuinely transformative in 2010.

## How much is now native

**Most of it**, which is the honest headline:

| Sass gave you | Native CSS now |
|---|---|
| `$variables` | **`--custom-properties`** — and these are *better*: runtime, cascading, scriptable |
| Nesting | **Native nesting** (2023+), broadly supported |
| `@import` partials | **`@import`** / `@use` in CSS, and bundlers |
| Colour functions | **`oklch()`, `color-mix()`, relative colour syntax** |
| Media query variables | **Container queries**, `@custom-media` coming |
| `@extend` | **`@layer`** solves the problem `@extend` was abused for |

**The custom-properties row is the important one.** A Sass `$variable` is compiled away — it's a build-time find-and-replace. A CSS custom property **exists at runtime**, cascades, can be overridden per-component, and can be changed by JavaScript. **That's why theming and dark mode moved to custom properties**, and it's a capability Sass structurally cannot provide → [[frontend/05-styling/01-css-architecture|CSS architecture]].

## What Sass still does better

**Genuinely, not grudgingly:**

**Loops and generated rules.**
```scss
@each $name, $value in (sm: 4px, md: 8px, lg: 16px) {
  .gap-#{$name} { gap: $value; }
}
```
CSS has no loops. If you're generating a scale, Sass still wins.

**Mixins with logic** — conditional output, argument defaults, and `@content` blocks. CSS custom properties can't emit *rules*, only values.

**Build-time computation** — maths and colour manipulation resolved before shipping, so nothing costs runtime.

**Mature module system** — `@use` with namespacing and private members is more rigorous than CSS imports.

## Should you start a new project with it?

**Usually no**, and it's worth being direct about that:

- **Tailwind** if you want utility-first → [[frontend/frameworks/css/tailwind|Tailwind]]
- **CSS Modules + native CSS** covers most of what Sass was for, with no preprocessor
- **vanilla-extract / Panda** if you want types and zero runtime

**Reach for Sass when:** you're maintaining an existing Sass codebase (don't rewrite working CSS), you genuinely need loops to generate large systematic scales, or your team already knows it well and the alternative buys nothing.

**Don't reach for it to get variables or nesting.** Those are free now.

## If you are using it

- **`@use` and `@forward`, not `@import`** — the old `@import` is deprecated, and it duplicates output and leaks globals
- **Keep nesting to ~3 levels.** Deep nesting generates high-specificity selectors, which is the specificity ratchet in a nicer syntax → [[frontend/05-styling/01-css-architecture|specificity]]
- **Avoid `@extend`.** It moves selectors around the output in ways that surprise people and can bloat the file. Use a mixin
- **Emit custom properties from Sass variables** so you get build-time ergonomics *and* runtime theming:
```scss
:root { --color-brand: #{$brand}; }
```

**Dart Sass is the only maintained implementation** — LibSass and Ruby Sass are both dead.

## Related
- [[frontend/frameworks/css/README|css/]] · [[frontend/frameworks/css/tailwind|Tailwind]]
- [[frontend/05-styling/01-css-architecture|CSS architecture]] — the modern CSS Sass no longer needs to provide

*Source: [reference] — from the Sass documentation, Aug 2026.*
