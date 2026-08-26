# Theming and Styling

**[Intermediate]** — The colour variables, what each one *actually* drives (not what its name suggests), and how `custom.scss` extends the base theme without forking it.

## The colour model

Quartz defines eight colours per mode. They become CSS custom properties (`--secondary`, `--lightgray`, …) available everywhere, and — importantly — they're also read by **JavaScript** components that paint to canvas.

```yaml
colors:
  darkMode:
    light: "#17161a"      # PAGE BACKGROUND (the name is a lie — see below)
    lightgray: "#4a4653"  # borders, table rules, graph links, indent guides
    gray: "#6f6a75"       # muted text, graph links on hover
    darkgray: "#d6d2cc"   # BODY TEXT
    dark: "#eceae6"       # HEADINGS
    secondary: "#e08a54"  # links and headings accent — copper here
    tertiary: "#6fb3a5"   # hover accent — teal here
    highlight: rgba(224, 138, 84, 0.12)   # internal-link background tint
    textHighlight: "#d9a44e66"            # ==marked text==
```

**The names describe the light-mode palette, not the role.** In dark mode `light` is the near-black background and `dark` is the near-white heading colour. This trips up everyone once. Read them as slots, not as colours:

| Variable | Actual role |
|---|---|
| `light` | page background |
| `lightgray` | borders, rules, **graph links**, explorer indent guides |
| `gray` | muted/secondary text, **graph links on hover** |
| `darkgray` | body text |
| `dark` | headings |
| `secondary` | link colour, accent |
| `tertiary` | hover accent |

## The trap: `lightgray` is not just borders

This one cost a real debugging session, so it's worth stating plainly.

The graph view paints to a **canvas** (PIXI), and it reads its colours from the CSS variables at draw time:

```js
// @quartz-community/graph
ee = getPropertyValue("--gray")        // link colour on hover
te = getPropertyValue("--lightgray")   // link colour normally
// ...
l.alpha = 1;  l.color = l.active ? ee : te
```

Links are drawn at **full opacity always**; hovering only swaps the colour. So if `--lightgray` sits too close to `--light`, every edge in the graph is invisible until you hover it — and it looks like a broken feature rather than a palette problem.

This vault had exactly that: `lightgray: #2f2d33` on `light: #17161a` is ~1.3:1 contrast. Lifting `lightgray` to `#4a4653` fixed the graph *and* revealed the explorer's indent guides, which ship as `border-left: 1px solid var(--lightgray)` and were invisible for the same reason.

**The general lesson:** because canvas components read these variables, you cannot fix them with CSS. `--lightgray` is the only lever, and it's shared with every border on the site. Lift the variable for the canvas, then soften the borders in `custom.scss`:

```scss
border-bottom: 1px solid color-mix(in srgb, var(--lightgray) 60%, transparent);
```

That decoupling — bright variable, dimmed usage — is the pattern for any conflict between a canvas component and page chrome.

## Choosing a palette that works for long-form reading

The theme here is deliberately calm: warm paper rather than clinical white, copper accent, teal hover. Some reasoning worth keeping:

- **Don't use pure white or pure black.** `#fbf9f5` and `#17161a` instead of `#fff`/`#000`. Maximum contrast is fatiguing over thousands of words, and pure black backgrounds cause smearing on OLED during scroll.
- **Body text should not be the heading colour.** `darkgray` for body, `dark` for headings, gives hierarchy without needing size alone to carry it.
- **Accents are for links, not decoration.** A copper link in a paragraph is a signal. Copper anywhere else competes with it.
- **Check the accent in both modes separately.** `#9c4221` reads well on paper and turns to mud on near-black, which is why dark mode lifts it to `#e08a54`. A single accent colour across both modes almost never works.

## Typography

```yaml
typography:
  header: Schibsted Grotesk
  body: Source Sans Pro
  code: IBM Plex Mono
fontOrigin: googleFonts
cdnCaching: true
```

`fontOrigin: googleFonts` fetches at build time; the alternative is `local` with fonts in `static/`. For a site that's mostly prose, the body font is the one that matters — pick something with a large x-height and real italics.

## `custom.scss`

The extension point. It lives at `quartz/styles/custom.scss` and is compiled into the bundle, so it can override anything in `base.scss` without forking Quartz.

The rule that keeps it maintainable: **use the CSS variables, never raw hex.** Then one stylesheet serves both light and dark mode automatically, and re-theming means editing YAML rather than hunting through SCSS.

```scss
@use "./variables.scss" as *;   // gives you $semiBoldWeight, breakpoints, etc.

article {
  table { /* base.scss ships NO table styling at all */ }
  blockquote { border-left: 3px solid var(--secondary); }
}
```

What's in this vault's `custom.scss` and why:

- **Tables** — Quartz ships none. This vault is table-heavy (nearly every course note compares options), so unstyled tables were the single biggest visual problem. Includes `display: block; overflow-x: auto` so wide tables scroll inside themselves rather than making the page scroll sideways on mobile.
- **Blockquotes** — used constantly for "the honest note" and golden-rule callouts.
- **Headings** — `h2` gets a bottom rule, because 3,000-word notes need visible section boundaries.
- **Explorer** — hover pills, an active-page rule, chevron alignment for wrapping folder names, subtree-aware indent guides.
- **Graph panel** — taller than the 250px default, since `localGraph.depth: 2` shows more nodes.

### Scoping to a single page

Quartz puts the slug on the body element:

```html
<body data-slug="git/01-how-git-works" data-basepath>
```

So page-specific styling needs no plugin:

```scss
body[data-slug="PRIMETECHIE"] article { max-width: 50rem; }
```

### Check it compiles before rebuilding

A SCSS error fails the whole build with a stack trace that isn't always obvious. Faster to check directly:

```bash
cd quartz && node -e "
const sass=require('sass');
try { const r=sass.compile('quartz/styles/custom.scss',{loadPaths:['quartz/styles']});
      console.log('SCSS OK —', r.css.length, 'bytes'); }
catch(e){ console.error('SCSS ERROR:', e.message); process.exit(1); }"
```

---

## Related
- [[tools/quartz/05-the-graph-view|The Graph View]] — the component most affected by these variables
- [[tools/quartz/02-configuration|Configuration]] — where the theme block lives
- [[frontend/frameworks/react/README|React]] — the component model Preact mirrors
- [[tools/quartz/README|Quartz notes]]
