# Tailwind CSS

> **[Intermediate]** · Utility-first — the argument for it, the honest objection, and v4's changes.

**Tailwind appeared nowhere in this vault except one project note** until Aug 2026, despite being one of the most-used styling approaches in the ecosystem.

## The idea

**Compose styles from single-purpose utility classes in the markup**, rather than writing CSS in a separate file.

```html
<button class="px-4 py-2 rounded-md bg-blue-600 text-white font-medium
               hover:bg-blue-700 focus-visible:ring-2 disabled:opacity-50">
  Submit
</button>
```

## Why it works, despite looking wrong

**The objection is immediate — "this is inline styles with extra steps" — and it's worth answering properly, because the answer is the whole case:**

**You never name anything.** Naming is the hard part of CSS, and utilities remove it entirely. No more `.card__header--compact` → [[frontend/05-styling/01-css-architecture|CSS architecture]].

**Styles are colocated with markup**, so deleting a component deletes its styles. **CSS files only ever grow** because nobody dares remove a rule they can't prove is unused.

**Specificity is flat.** No cascade wars, no `!important` ratchet.

**It's a constrained design system, not arbitrary values.** `p-4` is one step on a scale. That constraint is why Tailwind sites look coherent — the tokens are enforced by the API surface.

**The generated CSS is tiny and stops growing.** Only used utilities are emitted, and utilities are shared across the whole app — so a 10-page site and a 500-page site have similar CSS sizes.

**The honest cost: markup is verbose and less readable at a glance**, and there is a real vocabulary to learn. That's a genuine trade, not a misunderstanding — and the counter is that you're reading *one* file instead of two.

## v4 — what changed

**Configuration moved into CSS:**

```css
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.6 0.2 250);
  --font-display: "Satoshi", sans-serif;
  --spacing-huge: 8rem;
}
```

**No more `tailwind.config.js`** for most projects. Theme values become **native CSS custom properties**, so they're readable at runtime and by other tooling → [[frontend/05-styling/01-css-architecture|custom properties]].

Also: a **much faster Rust engine** (Oxide), automatic content detection (no `content` globs), and native `@layer`, container queries and `oklch` colours.

## Using it without making a mess

**Extract a component, not a CSS class.** The reflex to `@apply` everything recreates the naming problem you just escaped:

```jsx
function Button({ variant, ...props }) {          // ✓ the component is the abstraction
  return <button className={cn(base, variants[variant])} {...props} />;
}
```

**`@apply` sparingly** — it's an escape hatch, and heavy use means you've rebuilt semantic CSS with worse ergonomics.

**Use `cn()`** (clsx + tailwind-merge) so conditional classes and overrides resolve predictably — without `tailwind-merge`, `px-2` and `px-4` both end up in the class list and the winner is whichever CSS rule came last.

**Class order doesn't matter in the markup** — it's the generated stylesheet order that decides. This surprises people.

**Use the official Prettier plugin** to sort classes. Consistent order makes diffs readable and stops bikeshedding.

**Don't build dynamic class names by string concatenation:**
```jsx
className={`text-${color}-500`}     // ✗ the scanner can't see it; the class isn't generated
className={color === "red" ? "text-red-500" : "text-blue-500"}   // ✓ full strings
```
**This is the number one Tailwind bug**, and it fails silently — the style just doesn't appear.

## Where it fits

**Good for:** application UI, design systems with a component layer, teams that want consistency without a CSS review culture, and anywhere styles-die-with-components matters.

**Less good for:** content-heavy pages where you don't control markup (a CMS's HTML), teams with a dedicated CSS specialist who'd rather write CSS, and situations where markup readability is paramount.

**With component libraries:** **shadcn/ui** is the common pairing — it copies Radix-based components *into your repo* rather than installing them as a dependency, so you own and can edit them. That combination — Radix for accessibility, Tailwind for styling, your repo for ownership — is close to a default for React apps in 2026 → [[frontend/03-structuring-a-frontend/01-components-and-composition|headless components]].

## Related
- [[frontend/frameworks/css/README|css/]] · [[frontend/frameworks/css/sass|Sass]]
- [[frontend/05-styling/01-css-architecture|CSS architecture]] — where utility-first sits among the options
- [[frontend/06-cross-cutting/01-accessibility|accessibility]] — Tailwind styles it; Radix makes it correct

*Source: [reference] — from the Tailwind CSS v4 documentation, Aug 2026.*
