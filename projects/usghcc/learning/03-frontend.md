# 03 — Frontend

Next.js 16 / React patterns from the usghcc.org rebuild — images, third-party
embeds, accessibility, and the layout bugs that only a designer notices.

See also: [01-shell.md](01-shell.md) · [02-content-modelling.md](02-content-modelling.md) ·
[index.md](index.md)

---

## 1. `next/image` needs intrinsic dimensions, and why

```ts
const imageSchema = z.object({
  src: z.string().min(1),
  alt: z.string(),
  width: z.number().int().positive(),   // required
  height: z.number().int().positive(),  // required
});
```

Width and height are mandatory in the schema, not optional conveniences.

**The reason is Cumulative Layout Shift.** The browser lays out text
immediately but does not know how tall an image is until enough of it has
downloaded. Without dimensions it reserves zero height, paints the text, then
shoves everything down when the image arrives. The reader loses their place;
Google measures it and ranks on it.

Given width and height, the browser computes the **aspect ratio** and reserves
the right box before a single byte of image arrives. The numbers are not the
display size — CSS still controls that — they are the ratio.

`fill` is the alternative: the image absorbs a positioned ancestor's box, and
that ancestor supplies the reserved space instead. Used here for the video
poster frame, where the container is already `aspect-video`.

### `sizes` is not optional either

```tsx
sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
```

`sizes` tells the browser **how wide the image will be displayed**, so it can
pick the right candidate from the generated `srcset` *before* layout. Omit it
and the browser assumes `100vw` — so a card image one third of the width
downloads a full-width file. Three times the bytes, for nothing.

Read it right-to-left: default `100vw`, but at ≥640px it is half the viewport,
and at ≥1024px a third.

---

## 2. A logo with a baked-in background

The supplied logo was a **JPEG** — 1115×371, full colour lockup on opaque
white. JPEG has no alpha channel, so "the white background" is real pixels.

**On the white header:**

```tsx
className="h-9 w-auto mix-blend-multiply sm:h-11"
```

`mix-blend-multiply` multiplies each channel with what is behind it.
Multiplying by white (1.0) leaves the backdrop unchanged, so **white becomes
effectively transparent**; darker pixels stay dark. For a dark mark on white it
is close to free transparency.

This matters more than it first appears: the header turns translucent on scroll
(`bg-surface/90` + `backdrop-blur-md`), and page content passes behind it. An
opaque white rectangle would be plainly visible sliding over blurred content.

Blend modes composite against the **current stacking context**, so an
intervening `isolate`, `transform` or `opacity` changes what it blends with.

**On the dark footer**, multiply is useless — multiplying dark ink by a black
wordmark leaves black on black. The honest answer is to stop fighting the asset
and place it deliberately:

```tsx
className="inline-block rounded-xl bg-white p-4"
```

A white plaque reads as a design decision. A bare white rectangle reads as a
bug. **When you cannot fix the asset, make the constraint look intentional.**

The real fix is a transparent PNG/SVG plus a knockout-white variant — logged in
`DECISIONS.md` D14 so the workaround is removed when the assets arrive, rather
than becoming permanent by accident.

---

## 3. Alt text, and the double-announcement trap

```tsx
<Link href="/" aria-label={`${site.name} — home`}>
  <Image src={logo.src} alt="" ... />
</Link>
```

Three rules, all counter-intuitive at first:

**The link needs the accessible name, not the image.** A screen reader
announces a link by its content. If the image carried
`alt="US-Ghana Chamber of Commerce logo"`, the user hears "link, US-Ghana
Chamber of Commerce logo" — and "logo" is noise. The `aria-label` on the link
says what the link *does*: goes home.

**`alt=""` means "decorative — skip this".** It is not the same as a missing
`alt`. A missing `alt` makes some screen readers read out the *filename*. An
empty `alt` is an active instruction, which is why the schema types it as
required-but-possibly-empty: you must decide, and the decision is recorded.

**Never write "image of" or "logo of".** The technology already announces that
it is an image.

Applied to the hero: the background photograph sits under a scrim running
85–92% opaque. It is atmosphere, the heading carries the meaning — so `alt=""`.
The About-section photograph is content, so it gets a real description of what
is happening in it.

---

## 4. The YouTube facade

Dropping an `<iframe>` embed on a page costs roughly **a megabyte of player
JavaScript** and sets third-party cookies **on load** — for every visitor,
including the large majority who never press play.

The facade: render the poster frame and a play button; mount the real player
only on click.

```tsx
const [playing, setPlaying] = useState(false);

{playing ? (
  <iframe src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`} ... />
) : (
  <button onClick={() => setPlaying(true)}>
    <span className="sr-only">{`Play video: ${videoTitle}`}</span>
    <Image src={`https://i.ytimg.com/vi/${videoId}/maxresdefault.jpg`} alt="" fill ... />
  </button>
)}
```

Details that matter:

- **`autoplay=1` is correct here**, and only here. Autoplay is normally hostile,
  but the player only exists as the direct result of a click — without it the
  user would have to click twice.
- **`youtube-nocookie.com`** defers the tracking cookie until someone actually
  watches.
- **A real `<button>`**, not a `div` with `onClick`. Buttons are focusable, fire
  on Enter and Space, and are announced as buttons. The `sr-only` span names it.
- **`alt=""` on the poster** — the button already has an accessible name;
  describing the thumbnail as well would double up.

Remote images must be allowed explicitly:

```ts
images: {
  remotePatterns: [
    { protocol: "https", hostname: "i.ytimg.com", pathname: "/vi/**" },
  ],
}
```

This is a **security control**, not a formality. Without it, any URL in your
content could make your server fetch and re-serve arbitrary remote content —
turning the image optimiser into an open proxy. Keep `pathname` as narrow as
the use allows.

---

## 5. Grid orphans

The old page had four cards in a three-column grid: three on the first row, one
stranded on the second.

Fixed columns are the bug. Derive them from the count:

```tsx
const columns =
  pillars.length === 4 ? "sm:grid-cols-2 lg:grid-cols-4"
  : pillars.length === 2 ? "sm:grid-cols-2"
  : "sm:grid-cols-2 lg:grid-cols-3";
```

Four goes 2×2 then 4-across; three goes 3-across. Then **cap the count in the
schema** (`.min(2).max(4)`) so content cannot produce a layout the component
has no answer for. The schema and the component agree by construction.

Tailwind note: these must be **complete class strings**. Tailwind scans source
text statically, so `lg:grid-cols-${n}` produces nothing — the class never gets
generated.

---

## 6. Alternating surfaces: the coupling to avoid

The first renderer did this:

```tsx
tone={index % 2 === 0 ? "default" : "alt"}
```

Backgrounds derived from position in a section array. Insert one section and
every surface below it flips. Nothing in the diff shows it.

With named fields the page states it outright:

```tsx
<MediaText {...page.intro} />
<Pillars   {...page.whatWeDo} tone="alt" />
<Sectors   {...page.whyGhana} />
```

More characters, no spooky action. **Derived-from-position is convenient until
the position changes.**

---

## 7. `setState` inside an effect

ESLint (`react-hooks/set-state-in-effect`) flagged:

```tsx
useEffect(() => {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    setShown(true);
  }
}, []);
```

Setting state synchronously in an effect causes a **cascading render**: React
renders, runs the effect, sets state, renders again — before paint.

Here it is not just inefficient, it is **redundant**, because the same element
already carries `motion-reduce:opacity-100 motion-reduce:transition-none`.
Tailwind's `motion-reduce:` variant compiles to the same
`prefers-reduced-motion` media query, so CSS already handles it with no render
at all.

**The general shape: prefer CSS for anything CSS can express.** A media query
needs no JavaScript, no hydration, and works before React loads.

The related case — resetting state when a route changes — is better expressed
with a `key` on the component (remount it) than with an effect that watches
`pathname`.

---

## 8. Reduced motion is a real accessibility requirement

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Vestibular disorders make large transforms genuinely unpleasant — nausea, not
mild annoyance. This is not a preference toggle.

`0.01ms` rather than `0` so that `transitionend` handlers still fire; code that
waits for a transition to finish will not hang.

Paired with a `<noscript>` rule so scroll-reveal content is not invisible
without JavaScript:

```html
<noscript><style>[data-reveal]{opacity:1!important;transform:none!important}</style></noscript>
```

**Content must never depend on JavaScript to be readable.**

---

## Outstanding — promote to the general vault

- [ ] `next/image`: intrinsic dimensions and CLS, `sizes` vs `srcset`,
      `remotePatterns` as an SSRF control → `frontend/`
- [ ] Alt text decision tree, `aria-label` on a wrapping link, decorative vs
      informative images → `frontend/` accessibility
- [ ] Third-party embed facades as a performance and privacy pattern
- [ ] `prefers-reduced-motion` and the `0.01ms` trick
