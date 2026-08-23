# Accessibility

> **[Intermediate]** · A correctness requirement, frequently a legal one — and the area where most candidates are weakest, which makes it cheap to be good at.

**Roughly 15% of people have a disability.** Accessibility also covers the temporary (a broken arm), the situational (bright sunlight, a noisy train, one hand on a phone), and simply being older. **It is not an edge case.**

**And it is increasingly law** — the European Accessibility Act, the ADA in the US, and equivalents elsewhere. WCAG 2.2 AA is the usual conformance target.

## Semantic HTML does most of the work

**The single highest-leverage rule: use the right element.**

```html
<div onclick="submit()">Submit</div>          <!-- ✗ -->
<button onclick="submit()">Submit</button>    <!-- ✓ -->
```

**What the `<button>` gives you for free:** keyboard focusable, Enter *and* Space activate it, announced as "button" by screen readers, a native disabled state, and correct behaviour in a form.

**Reproducing that on a `div` takes `tabindex`, `role`, two keydown handlers and `aria-disabled` — and you'll still get it subtly wrong.** More work, worse result.

The elements that carry meaning: `<button>`, `<a href>` (**navigates** — if it doesn't navigate, it's a button), `<nav>`, `<main>`, `<header>`, `<footer>`, `<h1>`–`<h6>` **in order**, `<ul>`/`<ol>`, `<label>`, `<table>` with `<th scope>`, `<dialog>`.

**Headings are a navigation structure, not font sizes.** Screen-reader users jump between them, so skipping from `<h1>` to `<h4>` because it looked right breaks the outline. **Style with CSS, structure with the tag.**

## Keyboard

**Everything operable by mouse must be operable by keyboard.** Test by unplugging the mouse and using the site.

- **Tab order follows the DOM.** If CSS reorders things visually, focus order can become nonsense — a real risk with `flex-direction: row-reverse` and `order`
- **Focus must be visible.** `outline: none` without a replacement is the single most common accessibility failure on the web. Use `:focus-visible` to style it well rather than remove it
- **No keyboard traps** — focus must always be able to leave
- **A skip link** to `#main` so keyboard users can bypass the nav

**Modals are where this is usually broken.** A correct dialog: moves focus in on open, **traps focus inside**, closes on Escape, and **returns focus to the trigger** on close. **`<dialog>` does all of it natively**, and headless libraries (Radix, React Aria) do it correctly too — which is a strong argument for using one rather than building your own → [[frontend/03-structuring-a-frontend/01-components-and-composition|headless components]].

## ARIA — the rules

**"No ARIA is better than bad ARIA"**, and this is the official position, not a slogan. Wrong ARIA *overrides* correct native semantics, so it actively makes things worse.

**Use it when semantics run out**, not by default:

```html
<button aria-expanded="false" aria-controls="menu">Menu</button>
<div role="alert">Your session expired</div>            <!-- announced immediately -->
<div aria-live="polite">3 results</div>                 <!-- announced when idle -->
<img src="chart.png" alt="Revenue rose 20% in Q3">      <!-- describe the MEANING -->
<img src="decoration.svg" alt="">                       <!-- decorative: empty alt, not omitted -->
```

**`aria-live` is the one worth knowing well.** A single-page app that swaps content without a page load announces *nothing* — the screen reader has no idea anything changed. Route changes, form errors, async results and toasts all need announcing.

**Alt text describes the information, not the picture.** For a chart, that's the trend. For a decorative image, `alt=""` — an omitted `alt` makes screen readers read the filename.

## Forms

**Where accessibility failures cost real money**, because a failed form is an abandoned transaction.

- **A real `<label>`** tied by `for`/`id`. Placeholder text is not a label — it disappears on input and often fails contrast
- **Group related fields** in `<fieldset>` with a `<legend>`
- **Errors announced, not just coloured** — `aria-describedby` pointing at the message, `aria-invalid`, and the message adjacent to the field
- **Never colour alone.** Red border plus an icon plus text
- **Correct `autocomplete` and `inputmode`** — a numeric keypad for a phone number is an accessibility feature

## Visual

- **Contrast** — 4.5:1 for body text, 3:1 for large text and UI components. Check it; don't eyeball it
- **Don't disable zoom.** `user-scalable=no` blocks a fundamental accommodation
- **Support 200% zoom and 320 px** without horizontal scrolling
- **Respect `prefers-reduced-motion`** — vestibular disorders make parallax and large transitions genuinely unpleasant:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

**Animation libraries need this explicitly** → [[frontend/frameworks/framer-motion/README|Framer Motion]] · [[frontend/frameworks/gsap/README|GSAP]].

## Testing it

**Automated tooling catches perhaps 30–40%.** It's necessary and nowhere near sufficient.

1. **axe DevTools / Lighthouse** — the cheap pass; put `axe-core` in CI
2. **Keyboard only** — one complete flow, no mouse. **The highest-value manual test**
3. **A screen reader** — VoiceOver (macOS/iOS, built in), NVDA (Windows, free). **Half an hour with one is more instructive than any amount of reading**
4. **200% zoom, and 320 px wide**
5. **Real users**, if you can

## Related
- [[frontend/03-structuring-a-frontend/01-components-and-composition|components]] — headless libraries get this right
- [[frontend/05-styling/01-css-architecture|CSS architecture]] — contrast, zoom, motion
- [[frontend/interview/03-state-data-and-architecture|the interview round]] — where this is a differentiator

*Source: [reference] — from WCAG 2.2 and WAI-ARIA authoring practices, Aug 2026.*
