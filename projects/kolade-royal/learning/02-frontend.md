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

## 9. An asymmetric two-column layout, and why `minmax(0, …)` is there

The Chairman's section is a narrow identity column (name, titles, location) beside a
wide body column (biography, figures, board history):

```tsx
<div className="mt-12 grid gap-12 md:grid-cols-[minmax(0,20rem)_1fr]">
```

Reading the arbitrary value out loud: on `md` and up, two columns — the first at most
`20rem` and allowed to shrink to nothing, the second taking whatever is left. Below
`md` there is no `grid-cols-*` at all, so the grid falls back to a single column and
the two blocks stack. Mobile is the *absence* of a rule, not an extra rule.

Note the underscore in `[minmax(0,20rem)_1fr]`. Tailwind's arbitrary-value syntax
can't contain a literal space (a space would end the class name), so `_` is the escape
for one. It becomes `grid-template-columns: minmax(0,20rem) 1fr`.

### Why not `[20rem_1fr]`?

Because a fixed `20rem` can't shrink. If the narrow column ever contains something
that won't fit — a long unbroken string, an image with its own intrinsic width — the
track stays `20rem` wide while its contents spill out of it, and the grid pushes past
the container instead of the content wrapping. `minmax(0, 20rem)` says "up to 20rem,
but you may go smaller", which restores the ability to shrink.

This is the same trap as the well-known `1fr` overflow problem, from the other
direction. `1fr` is shorthand for `minmax(auto, 1fr)`, and that `auto` minimum means a
grid track will refuse to shrink below its content's *min-content* size — which is why
a long word or a `<pre>` block in a `1fr` column can blow out a whole layout, and why
the fix is spelling it `minmax(0, 1fr)`. Same principle both times: **a grid track's
default minimum is its content, not zero.**

### Sizing the columns as a ratio instead

`md:grid-cols-[1fr_2fr]` would also have produced a narrow-and-wide split. The
difference is what happens on a very wide monitor: the ratio version keeps growing the
identity column forever, eventually giving a two-word job title a 40rem-wide track.
The `minmax` version caps it and hands the surplus to the prose. Cap the column whose
content has a natural maximum size; let the one with real content take the remainder.

---

## 10. `key` on a list you generated from prose

Three of the four lists in this section key off the content itself:

```tsx
{chairman.boards.map((b) => (
  <li key={b}>…</li>
))}

{chairman.bio.map((para) => (
  <p key={para.slice(0, 24)}>{para}</p>
))}
```

React uses `key` to match elements between renders — it is how it knows "this is the
same `<li>` that was here before, moved" versus "this is a new one". The rule is that
a key must be **stable** (same item, same key next render) and **unique among its
siblings**.

`key={index}` satisfies unique but not stable: insert an item at the top and every
subsequent item's key shifts by one, so React thinks every element changed. For static
content rendered once from a constant, that costs nothing real — which is why it is
tempting — but it silently becomes a bug the day the list is reordered or filtered.
Keying off content is stable by construction.

`para.slice(0, 24)` is the compromise for paragraphs: full paragraph text works as a
key but makes the DOM inspector unreadable, and the first 24 characters are already
unique across three paragraphs that start "A seasoned…", "He is a lyricist…" and
"He has authored…". If two paragraphs could ever share an opening, this breaks and you
would want an explicit `id` on each entry in the data instead. The general shape of
the rule: **derive the key from something the data guarantees is distinct**, and if the
data guarantees nothing, add a field that does.

---

## 11. Where new copy goes — following the existing seam

The Chairman's profile went into `src/lib/content.ts`, not into `about/page.tsx`, for
the reason already set out in §6: that file is the group-level copy and the page
components are structure. The specific judgment call this time was *which* file — and
the answer came from `DECISIONS.md` rather than from the code.

The project draws a line between group-level facts and Nigerian-entity facts:
`lib/content.ts` holds the parent group's positioning, `lib/objects.ts` holds the
Nigerian company's own registered objects. The Chairman chairs the **parent** and
presides over the **foundation**; he holds no stated office at the Nigerian company.
So the data belongs with the group copy, and the comment above it says so explicitly,
because the next person to touch it will not have read the decisions log.

Worth generalising: a decisions log earns its keep at exactly this moment — not when
the decision is made, but months later, when a new piece of content arrives and the
question "where does this go?" has an answer that isn't visible anywhere in the code.

---

## 12. `mix-blend-mode` — deleting a background that has no alpha

The Kolade crest arrived as two JPEGs: gold artwork on a solid black square, and the
same artwork on a solid white square. JPEG has no alpha channel, so there is no
transparency to fall back on, and the page background is `#150E20` — near-black, but
not black. Dropping the dark JPEG straight in would show a visible black tile.

```tsx
className="mix-blend-screen"
```

That is the whole fix. To see why it is exact rather than approximate, look at the
formula. **Screen** is:

```
result = 1 - (1 - source) x (1 - backdrop)
```

Substitute a black source (`0`):

```
result = 1 - (1 - 0) x (1 - backdrop) = 1 - (1 - backdrop) = backdrop
```

Pure black under `screen` returns the backdrop **unchanged**. Not "close to". The black
square becomes literally the page background, whatever colour that is — which also means
the same file keeps working if the palette changes again.

**Multiply** is the mirror image, `result = source x backdrop`, so a pure white source
returns the backdrop unchanged. That is the one to use for the light-background version
of an asset sitting on a light section.

| Asset background | Blend mode | Why |
| --- | --- | --- |
| Pure black `#000` | `screen` | black → backdrop |
| Pure white `#fff` | `multiply` | white → backdrop |

**This only works if the background is *exactly* `#000` / `#fff`.** At `(4,2,6)` the
maths leaves a faint but real rectangle. Measure it before relying on it — see
[[01-shell]] §7 for the one-liner. JPEG compression also means the pixels immediately
around the artwork are not pure, so expect slight haze at the edges of fine detail; a
transparent PNG or SVG is still the better asset if you can get one.

### The trap: blending is confined to a stacking context

`mix-blend-mode` blends an element with its *backdrop* — but only within the nearest
**isolated group**. Any element that creates a stacking context forms one. So this bites
in both directions:

- The sticky nav uses `backdrop-blur`, and `backdrop-filter` creates a stacking context.
  That is what stops the logo blending with light page sections scrolling underneath —
  it blends with the nav's own background instead. Here the isolation is doing us a
  favour.
- The reverse trap: wrapping a blended element in a div and adding `isolate` or
  `opacity-90` or `transform` to that div gives it a *transparent* backdrop, and
  screen-against-transparent leaves black as black. The "safety wrapper" is what breaks
  it.

The rule to remember: **`isolation: isolate` on an ancestor changes what a blend sees.**
If a blend suddenly stops working, look up the tree for a new stacking context, not at
the blend itself.

---

## 13. `next/image` — the three props that are not optional

```tsx
<Image
  src="/logos/logo-dark.jpg"
  width={1600}
  height={1600}
  alt="The Kolade coat of arms"
  sizes="(min-width: 768px) 16rem, 12rem"
  priority
  className="mb-8 w-48 md:w-64"
/>
```

- **`width`/`height` are the *intrinsic* dimensions**, not the display size. They exist
  so the browser can reserve the right box before the file arrives, which is what stops
  the page jumping as images load (cumulative layout shift). The actual rendered size
  comes from the CSS — `w-48 md:w-64` here. Getting the ratio wrong distorts nothing
  visually but reserves the wrong space, so the shift comes back.
- **`sizes` is a promise about CSS width, not a request.** It tells the browser how wide
  the image will *be* at each breakpoint so it can pick the right file from the srcset
  before layout is computed. Omit it and Next assumes `100vw`, and every phone downloads
  a desktop-width file. The values must track the classes: `w-48` is 12rem, `md:w-64` is
  16rem, and `md:` is `min-width: 768px` — which is exactly what the string above says.
- **`priority`** disables lazy loading and preloads. Correct for the hero crest, which is
  above the fold; wrong for everything below it, because preloading everything is the
  same as preloading nothing.

### `alt` is a decision, not a description

Three images in this project, three different answers:

| Where | `alt` | Why |
| --- | --- | --- |
| Hero crest | `"The Kolade coat of arms"` | Content. Carries meaning a screen-reader user would otherwise lose. |
| Nav + footer crest | `alt=""` + `aria-hidden` | Decorative *here* — the company name sits next to it as real text. Announcing "Kolade coat of arms, Kolade Royal" makes the reader say everything twice. |
| Carousel slides | the caption | The image *is* the content. |

The mistake is treating `alt` as a property of the file. It is a property of the file's
role **on this page** — the identical crest is content in the hero and noise in the nav.

---

## 14. A carousel that does not fail its keyboard and touch users

The four things that separate a real carousel from a pair of arrows:

```tsx
const go = useCallback(
  (delta: number) => setIndex((i) => (i + delta + slides.length) % slides.length),
  [slides.length],
);
```

**Wrapping in both directions.** `(i + delta) % n` is wrong going backwards: from slide 0,
`-1 % 5` is `-1` in JavaScript, not `4`. JS `%` is *remainder*, which keeps the sign of
the left operand — it is not the mathematical modulo. Adding `n` before the `%` puts the
value in positive territory first. This is the same reason `-1 % 5 === -1` surprises
people coming from Python, where it is `4`.

**Functional `setIndex(i => ...)`** rather than `setIndex(index + delta)`. The updater
form reads the value React is about to commit, so two rapid clicks both count. Closing
over `index` means the second click computes from a stale value and one of them is lost.

**A swipe threshold.** `Math.abs(dx) > 50` — without it, any tap registers a
one-or-two-pixel delta and randomly advances the slide, and a vertical scroll that drifts
sideways does the same.

**Controls that exist at every size.** The round arrow buttons are `hidden sm:flex`, so
below `sm` the only remaining control was an 8px dot. Touch targets need ~44px, hence the
explicit Previous/Next pair for small screens. "It is swipeable" is not an answer —
swipe is undiscoverable and not everyone can perform one.

### `aria-live` on the caption, not the image

```tsx
<figcaption aria-live="polite">{current.caption}</figcaption>
```

The slide changes with no page navigation and no focus move, so a screen reader would
otherwise announce nothing at all — the user presses Next and hears silence. `aria-live`
on the text that changes makes the new caption and position ("3 / 5") announce itself.
`polite` waits for a pause rather than interrupting.

---

## 15. Autoplay: the timer is the easy half

Making the carousel advance on its own is four lines. Making it *acceptable* is the rest
of this section — and the reason to write them at the same time is that "add the pause
control later" reliably means never.

```tsx
useEffect(() => {
  if (!autoplay) return;
  const id = setInterval(() => go(1), 6000);
  return () => clearInterval(id);
}, [autoplay, go, index]);
```

### The cleanup function is not optional

`return () => clearInterval(id)` is what stops the timer when the component unmounts.
Without it the interval keeps firing against a component that is gone, React warns about
setting state on an unmounted component, and every navigation back to the page starts a
*second* interval on top of the first — the slides begin advancing twice as fast, then
three times, and it looks like a mysterious speed bug rather than a leak. Same shape as
the `removeEventListener` in §8, and the same rule: **anything you start in an effect,
stop in its cleanup.**

### `index` in the dependency array is a feature

Listing `index` means every slide change tears the interval down and builds a new one.
That is deliberate: click Next 200ms before a tick was due and you would otherwise get
two advances in a quarter second. Rebuilding gives every slide a full interval, however
it was reached.

### WCAG 2.2.2 "Pause, Stop, Hide"

> For any moving, blinking or scrolling information that starts automatically, lasts
> more than five seconds, and is presented in parallel with other content, there is a
> mechanism for the user to pause, stop, or hide it.

A six-second auto-rotating carousel is squarely inside that. It is not a nicety — content
that moves on its own is actively hostile to people reading with a screen magnifier, and
to anyone whose reading speed is slower than the rotation. Three mechanisms here:

1. **An explicit pause button**, which is the one the success criterion actually asks for.
2. **Pause on hover and on focus-within**, so reading or tabbing through stops the motion
   without anyone having to find a control.
3. **No autoplay at all under `prefers-reduced-motion`.**

### The media query has to be checked in JavaScript

`globals.css` already has a blanket reduced-motion block that flattens transitions. It
has **no reach over a `setInterval`** — CSS cannot stop a timer. A component that moves
on its own has to ask the question itself:

```tsx
useEffect(() => {
  const query = window.matchMedia("(prefers-reduced-motion: reduce)");
  setReducedMotion(query.matches);
  const onChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}, []);
```

Two details. `window.matchMedia` must be inside the effect, not in the render body —
there is no `window` during server rendering, so touching it at module or render level
crashes the build. And subscribing to `change` rather than only reading `.matches` once
means it responds if the OS setting is toggled while the page is open.

### Three states, not one boolean

```tsx
const autoplay = playing && !suspended && !reducedMotion;
```

The instinct is a single `paused` flag, and it breaks immediately: the user pauses
explicitly, then moves the mouse away, and hover-unpause silently overrides their
choice. `playing` is the user's stated intent, `suspended` is transient hover/focus, and
`reducedMotion` is a system preference that outranks both. Keeping them separate means
none of them can clobber another. **When two different things can "pause" something, they
need two different variables.**

### `onPointerEnter` with a `pointerType` guard, not `onMouseEnter`

Touch browsers fire *emulated* mouse events, so a tap raises `mouseenter` — and then
frequently never raises `mouseleave`, because the finger is gone rather than moved away.
The result: autoplay suspends on the first swipe and never resumes.

```tsx
onPointerEnter={(e) => { if (e.pointerType !== "touch") setSuspended(true); }}
```

Pointer events carry `pointerType` (`"mouse" | "pen" | "touch"`), so the hover-to-pause
behaviour can be limited to devices that actually have a hover state. Worth generalising:
**any "on hover" behaviour needs an answer for what it does on touch**, and the answer is
usually "nothing", not "whatever the emulated event happens to do".

### `aria-live` has to change with the mode

```tsx
aria-live={autoplay ? "off" : "polite"}
```

The live region added in §14 is right when the user drives the carousel and wrong when it
drives itself — a screen reader announcing a new caption every six seconds, over whatever
the user was actually reading, is unusable. Silent while rotating, live once they take
control.

---

## See also

- [[01-shell]] — the `sed`/`grep` mechanics of the rename itself.
