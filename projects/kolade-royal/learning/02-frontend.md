# Frontend — kolade-royal

Next.js 14 (App Router) + Tailwind. This file covers the design-token system and the
brand recolour from gold/parchment to purple/lilac.

---

## 1. Design tokens: why the recolour was a 1-file job (almost)

The site never hardcoded colours in components. Every colour lived in
`tailwind.config.ts` under `theme.extend.colors`:

```ts
colors: {
  ink: "#0D1210",
  parchment: "#F3EEE1",
  brass: "#B8873F",
  // ...
}
```

Components then referenced them by name — `bg-ink`, `text-brassLight`,
`border-stone/15`. That indirection is what a **design token** is: a named decision,
used everywhere, defined once. The payoff is exactly the request that came in here —
"change the colours" — which becomes an edit to one config file plus a mechanical
rename, instead of hunting 68 hardcoded hex values across 9 files.

**The lesson to carry forward:** the moment you write the same hex twice, it should be
a token.

### Where the abstraction leaked

Three places still held raw hex and had to be edited by hand — worth knowing because
they're the usual suspects in any Tailwind project:

1. **`globals.css`** — `body { background-color: #0D1210 }`, `::selection`,
   `:focus-visible`. Plain CSS can't see Tailwind's token names.
2. **`rgba()` values** in custom classes (`.ledger-rule`, `.ghost-stamp`) — these need
   an alpha channel, so they were written as raw `rgba(184, 135, 63, 0.18)` rather than
   as a token.
3. **Semantics baked into names.** More on this next.

Fix for (1) and (2) in a future project: define tokens as CSS custom properties on
`:root`, and have Tailwind read *those*. Then `globals.css` and the config share a
single source:

```css
:root { --ink: 21 14 32; }          /* space-separated RGB channels, no rgb() wrapper */
```
```ts
colors: { ink: "rgb(var(--ink) / <alpha-value>)" }
```

`<alpha-value>` is a Tailwind placeholder it substitutes when you write `bg-ink/60`.
That's what makes opacity modifiers keep working — a plain `var(--ink)` holding a full
`rgb(...)` string would break them.

---

## 2. Name tokens by role, not by hue

The old palette was named after what the colours *looked like*: `brass`, `parchment`,
`stone`, `rust`. Readable, but it meant that "make it purple" invalidated every name —
a token literally called `brass` holding `#C6ABF7` is a lie that the next person (or
future you) has to decode.

So the rename was hue-accurate again:

| old | new | role |
|---|---|---|
| `ink` `#0D1210` | `ink` `#150E20` | page background (near-black aubergine) |
| — | `ink2` `#1D1430` | raised surface, card hover |
| `green` `#223B2C` | `plum` `#2A1B44` | deep band sections (CTA strips) |
| `brass` `#B8873F` | `violet` `#7C3AED` | large decorative type, faint rules |
| `brassLight` `#D8B067` | `lilac` `#C6ABF7` | primary accent on dark — links, buttons, eyebrows |
| `rust` `#7B3324` | `lilacDeep` `#5B21B6` | accent for use **on the light surface** |
| `parchment` `#F3EEE1` | `mist` `#F4F0FB` | light surface / body text |
| `stone` `#C9C2AE` | `heather` `#A99CC2` | muted meta text, borders |

The genuinely durable alternative is naming by **role**: `surface`, `surfaceRaised`,
`accent`, `accentMuted`, `textPrimary`, `textMuted`. Then a rebrand touches only hex
values and *no* class names anywhere. The cost is that `bg-surface` reads more
abstractly than `bg-mist` while you're building. For a nine-file marketing site,
hue-accurate names are a defensible call; for a design system consumed by other teams,
role names win. Know which trade you're making rather than defaulting.

---

## 3. Contrast: the part that isn't taste

Swapping a **light** accent for a **dark** one silently breaks text. The old buttons
were:

```tsx
className="bg-brass text-ink hover:bg-brassLight"   // dark text on mid-gold ✅
```

The obvious purple equivalent is a mid-purple like `#6D28D9`. But run the numbers:

| pairing | contrast ratio | WCAG AA (4.5:1 normal text) |
|---|---|---|
| `#150E20` text on `#6D28D9` | **2.66:1** | ❌ fails badly |
| white text on `#6D28D9` | 7.12:1 | ✅ |
| `#150E20` text on `#C6ABF7` (lilac) | **9.3:1** | ✅ |

Gold and purple sit in very different places on the luminance scale: a mid-gold is
*light* (dark text works on it), a mid-purple is *dark* (dark text does not). So the
button fill became **lilac with ink text**, keeping the original "light chip on a dark
page" look rather than the naive same-saturation swap.

### How the ratio is actually computed

Worth understanding once instead of just pasting hexes into a checker.

1. Take each channel as 0–1: `r = R/255`.
2. **Linearise** it (undo the sRGB gamma curve):
   `c ≤ 0.03928 ? c/12.92 : ((c+0.055)/1.055)^2.4`
3. Relative luminance `L = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin`.
   Note the weights — green carries ~72% of perceived brightness, blue only 7%. That
   is exactly why deep blues and purples are so dark despite looking "vivid".
4. Contrast = `(L_lighter + 0.05) / (L_darker + 0.05)`.

Thresholds: **4.5:1** normal text, **3:1** large text (≥24px, or ≥18.66px bold) and UI
component boundaries.

The 3:1 large-text allowance is what licenses `violet` (`#7C3AED`, 3.3:1 on ink) for
the 5xl clause letters on `/services` — decorative, huge, and it adds a mid-tone the
palette otherwise lacked. The same colour as body text would have failed.

### Every pairing in the new palette

| foreground | background | ratio |
|---|---|---|
| `mist` body text | `ink` | 16.8 ✅ |
| `heather` meta | `ink` | 7.4 ✅ |
| `lilac` accent | `ink` | 9.3 ✅ |
| `violet` (large only) | `ink` | 3.3 ✅ large |
| `ink` | `lilac` button | 9.3 ✅ |
| `mist` | `plum` band | 13.9 ✅ |
| `lilacDeep` | `mist` light section | 8.0 ✅ |

---

## 4. Two bugs the mechanical rename created

A find-and-replace is text, not design. Both of these type-checked fine and would have
shipped silently.

### Dead hover states

The old palette had *two* golds, and buttons used both:

```tsx
bg-brass          hover:bg-brassLight     // mid gold → light gold
```

Both mapped onto `lilac`, so four buttons ended up as:

```tsx
bg-lilac          hover:bg-lilac          // hover does nothing
```

No error, no visual bug on a screenshot — just an interaction that quietly stopped
existing. Caught by grepping for the pattern rather than by looking:

```bash
grep -rn 'hover:bg-' src
```

Fixed by sending hover *brighter*, to `hover:bg-mist`, preserving the original
"lightens on hover" behaviour.

**Generalisable:** whenever a rename collapses two tokens into one, every place that
used *both* is now a potential no-op. Grep for co-occurrence deliberately.

### A hover that was already doing something subtle

```tsx
<div className="group bg-ink p-8 transition hover:bg-ink/60">
```

`bg-ink/60` on a card sitting on an `ink` page looks like a no-op — same colour. It
wasn't: the grid uses `gap-px` over a `bg-stone/15` parent, so the card's 60% opacity
let the *lighter grid background* show through, lightening the card on hover. Clever,
but fragile and unreadable. Replaced with an explicit token, `hover:bg-ink2`, which
states the intent instead of relying on a stacking-context side effect.

---

## 5. Tailwind gotcha: string tokens destroy built-in scales

```ts
extend: { colors: { violet: "#7C3AED" } }
```

Tailwind ships a `violet` palette (`violet-50` … `violet-950`). Assigning a **string**
to that key replaces the whole scale — after this, `bg-violet-500` no longer exists and
`bg-violet` is the only option. Same was already true of the old config's
`green: "#223B2C"`, which had shadowed Tailwind's greens.

That's fine here (nothing uses the numeric scales), but it's a genuine trap if someone
later reaches for `text-violet-400` and gets an unstyled element with no error. If you
want both, nest an object and use a `DEFAULT` key:

```ts
violet: { DEFAULT: "#7C3AED", 400: "#a78bfa" }   // bg-violet AND bg-violet-400 both work
```

Also worth knowing: Tailwind scans for **complete class strings**. `bg-${color}` never
works — the class must appear literally in the source for the scanner in `content:` to
see it.

---

## 6. Separating copy from structure

When the site's text was rebuilt from the parent company's, the same content appeared on
more than one page — the three solution areas render on both `/` and `/services`. So
they moved out of the components into `src/lib/content.ts`, alongside the existing
`lib/objects.ts`:

```ts
export type Solution = { n: string; title: string; blurb: string };

export const solutions: Solution[] = [
  { n: "01", title: "Business Consulting", blurb: "Expert guidance to…" },
  // …
];
```

```tsx
{solutions.map((s) => (
  <div key={s.n} className="bg-ink p-8">…</div>
))}
```

Three things this buys you:

1. **One place to edit.** A copy change from the client is a one-file edit, not a hunt
   through JSX. Same argument as design tokens in §1 — the pattern generalises: *data
   in one place, structure in another*.
2. **The page component becomes readable as layout.** You can see the shape of the page
   without wading through paragraphs of marketing prose.
3. **It's the shape a CMS would want.** If this ever moves to Sanity or similar,
   `content.ts` is already the schema — `solutions` becomes a document type with
   `n`, `title`, `blurb` fields. Structuring content as data *before* you need a CMS
   makes that migration mechanical instead of a rewrite.

The `type Solution = …` annotation is doing real work: it means a typo like `titel` in
one entry is a compile error, and the `.map()` in the component gets autocomplete. A
bare array would give you neither.

### When *not* to extract

The founding-subscribers table on `/about` stayed as a local `const` in the page file.
It's used once, on one page. Extracting single-use data to a shared module just adds an
import and a file to open — the rule is **extract on the second use**, not in
anticipation of one.

---

## 7. `next build` as a check — but never while `next dev` is running

> **Learned the hard way, 2026-08-17.** Running `next build` while the dev server was
> live broke the running site completely — every page rendered as raw unstyled HTML.
> Both commands write to the **same `.next/` directory**. `next build` overwrote the
> manifests and static CSS that the running dev server had open, and the dev server
> kept serving HTML pointing at assets that no longer matched.
>
> Recovery: `Ctrl+C` the dev server, `rm -rf .next`, `npm run dev` again. Nothing in
> `src/` was ever wrong — `.next/` is a disposable build cache, which is why deleting
> it is always safe and is the first thing to try for any inexplicable Next.js
> behaviour.
>
> The generalisable rule: **`tsc --noEmit` is safe to run any time because it writes
> nothing. A framework build is not, because it writes to state a running process
> owns.** Same applies to Vite, Astro, Nuxt, SvelteKit. Stop the dev server first, or
> don't run the build.

```bash
npx next build   # only with the dev server stopped
```

With that caveat, it's worth running before a deploy. It does three things
`tsc --noEmit` doesn't:

- runs the App Router's own type validation (route params, `metadata` exports),
- **actually renders** every static page, so a runtime error in a component — an
  undefined `.map()`, a bad import — fails the build rather than waiting to blow up in
  the browser,
- prints the route table, which tells you the rendering strategy per page:

```
Route (app)                    Size     First Load JS
┌ ○ /                          175 B            94 kB
├ ○ /about                     137 B          87.2 kB
└ ○ /services                  175 B            94 kB
○  (Static)  prerendered as static content
```

`○ (Static)` means the page was prerendered to HTML at build time — no server work per
request. That's what you want for a marketing site. If a page unexpectedly shows as
`λ`/`ƒ` (dynamic), something in it opted out of static rendering — usually reading
`headers()`, `cookies()`, or `searchParams`. Catching that at build time is much
cheaper than wondering later why the site got slow.

Note the two client components (`Nav`, `ContactForm`, both marked `"use client"`) don't
prevent static rendering — they're prerendered to HTML too, then hydrated. `"use client"`
controls *interactivity*, not *when* the HTML is generated. Easy thing to conflate early
on.

---

## 8. A back-to-top button: four small decisions

`components/BackToTop.tsx` is twenty lines, but nearly every line is a choice worth
understanding.

### Passive scroll listeners

```ts
window.addEventListener("scroll", onScroll, { passive: true });
```

`passive: true` promises the browser that the handler will **never call
`preventDefault()`**. Without that promise, the browser has to run your JavaScript
*before* it can scroll the page, in case you cancel the scroll — which means a slow
handler stutters the scroll. With it, the browser scrolls immediately and runs your
handler alongside. Free performance on the one event that fires most often. Chrome
already defaults this to `true` for `scroll` on `window`, but being explicit is right:
it documents the intent and covers browsers that don't.

### Always clean up the listener

```ts
useEffect(() => {
  // ...
  return () => window.removeEventListener("scroll", onScroll);
}, []);
```

The function an effect returns is its **cleanup**, run when the component unmounts (and
before every re-run of the effect). Skip it and every client-side navigation leaves
another dead listener attached to `window`, all firing on every scroll forever. This is
the single most common React memory leak. Note the removal has to reference *the same
function object* — `removeEventListener("scroll", () => {...})` with a fresh arrow
function removes nothing, silently.

### Set the initial state explicitly

```ts
onScroll(); // the page may load already scrolled
```

The listener only fires on *future* scrolls. Load a page at an anchor, or hit reload
halfway down, and without this line the button stays hidden until you happen to scroll.
The general shape: **an event handler tells you about changes, so you still have to read
the current value once at setup.**

### Let CSS own the animation

```ts
onClick={() => window.scrollTo({ top: 0 })}
```

No `behavior` key. `behavior` defaults to `"auto"`, which resolves to the element's
computed `scroll-behavior` — and `globals.css` already sets `scroll-behavior: smooth` on
`html`, with a `prefers-reduced-motion` block that forces it back to `auto`. So the
smooth scroll works, and it automatically switches off for users who've asked their OS
for reduced motion. Writing `behavior: "smooth"` in JavaScript would have **overridden**
the media query and animated the page for someone who explicitly asked it not to.

Worth generalising: when a CSS mechanism and a JS mechanism both exist, prefer the CSS
one — user preferences (reduced motion, dark mode, forced colours) are expressed to CSS,
so CSS gets them right by default and JS has to re-implement them by hand.

### Hiding it without stranding keyboard users

```tsx
className={`... ${show ? "opacity-100" : "invisible opacity-0"}`}
```

`opacity-0` alone would leave an invisible but still **focusable and clickable** button
floating over the page — a keyboard user tabs into something they can't see. Adding
`invisible` (`visibility: hidden`) removes it from the tab order and from pointer
events. The trade-off: `visibility` isn't in Tailwind's default `transition` property
list, so it flips instantly — the fade-in animates, the fade-out doesn't. Acceptable
here; the alternative is animating `visibility` explicitly with a delay.

---

## See also

- [[01-shell]] — the `sed`/`grep` mechanics of the rename itself.
