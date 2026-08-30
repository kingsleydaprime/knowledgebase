# Portable Text and Images

**Part of [[frontend/frameworks/sanity/README|frameworks/sanity]].** `[reference]`
**Real code:** [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|munakalati]] · **Converting *into* it:** [[projects/munakalati/learning/05-migration/04-portable-text-conversion|the Wix migration]]

---

## Part 1 — Portable Text

### Why rich text isn't stored as HTML

Portable Text is rich text as **structured JSON**:

```json
{ "_type": "block", "_key": "a1b2c3d4", "style": "h2", "markDefs": [],
  "children": [ { "_type": "span", "_key": "e5f6", "text": "Stories that shape", "marks": ["strong"] } ] }
```

Four arguments against an HTML blob, in order of weight:

1. **An HTML blob is only renderable as HTML.** The same content here renders to React on the web, native components in an app, or plain text for a search index — because it never encoded a rendering decision.
2. **Safe by construction.** Nothing to sanitise, because there is no markup.
3. **Diffable and queryable.** The query language can reach inside blocks; the CMS can merge concurrent edits.
4. **Custom embeds are first-class.** An image in an article body is a structured node, so it can go through your framework's image pipeline inside a semantic `<figure>` — not an `<img>` parsed out of a string.

**The cost: nothing renders until you say how.**

### The four things in the format

- **`block`** — a paragraph-level unit. `style` is `normal | h2 | h3 | blockquote | …`; `listItem` and `level` handle lists.
- **`span`** — a run of text inside a block, split wherever formatting changes. "This is **bold** text" is three spans.
- **`marks`** — strings on a span. Either a **decorator** (`"strong"`, `"em"`) or a **`_key` pointing into `markDefs`**.
- **`markDefs`** — block-level definitions for marks carrying data. A link is `markDefs: [{_key: "x1", _type: "link", href: "…"}]` with the span carrying `marks: ["x1"]`.

> **The indirection is the part people get wrong.** A link's `href` is *not* on the span; the span references a definition on its parent block. It's a normalisation, so one annotation can cover several spans without repeating its data — and it's why writing a converter that handles bold is trivial and one that handles links is not.

**`_key` is mandatory** on every block and span, unique among siblings. It's what lets the CMS diff arrays for real-time collaboration; without stable keys, two editors typing in one document produce garbage.

### Rendering: four buckets

```tsx
const components = {
  block: {                                   // keyed by `style`
    normal:     ({ children }) => <p className="…">{children}</p>,
    h2:         ({ children }) => <h2 className="…">{children}</h2>,
    blockquote: ({ children }) => <blockquote className="…">{children}</blockquote>,
  },
  list:  { bullet: …, number: … },           // the <ul>/<ol> wrappers
  marks: {                                   // inline
    strong: ({ children }) => <strong>{children}</strong>,
    link:   ({ value, children }) => (       // `value` is the markDefs entry
      <a href={value?.href} target="_blank" rel="noopener noreferrer">{children}</a>
    ),
  },
  types: {                                   // non-text blocks from the schema's `of: [...]`
    image: ({ value }) => (
      <figure>
        <div className="relative aspect-video">
          <Image src={urlFor(value).width(1200).url()} alt={value.alt ?? ""} fill className="object-cover" />
        </div>
        {value.caption && <figcaption>{value.caption}</figcaption>}
      </figure>
    ),
  },
};
```

**Knowing which bucket a thing goes in is most of the skill.** `types` is the extension point — anything in the schema's `of: [...]` that isn't a `block`. Add `{ type: "youtube" }` to the schema and it renders here.

**`rel="noopener noreferrer"` on external links isn't boilerplate:** `noopener` stops the opened page reaching back through `window.opener` to navigate your tab somewhere hostile. Browsers imply it for `target="_blank"` now; writing it is still correct.

## Part 2 — Images

### An image field stores a pointer

```json
{ "_type": "image",
  "asset": { "_type": "reference", "_ref": "image-abc123-1600x900-jpg" },
  "alt": "Children reading in a classroom" }
```

The binary lives once in a shared asset store. Two consequences:

- **Deduplication is automatic** — uploading the same file twice returns the same asset ID.
- **The ID encodes the dimensions** (`-1600x900-`), so an aspect ratio is computable without a round trip.

### Extra fields on the image type

```ts
defineField({
  name: "coverImage", type: "image",
  options: { hotspot: true },
  fields: [defineField({ name: "alt", type: "string" })],
})
```

**Alt text belongs on the field, not the asset** — an image describes itself differently depending on where it appears. The same photo is "the team at the 2024 summit" on an About page and "our founder accepting the award" in a post.

Two habits: **validate `alt` as required** (a step this is usually skipped, and accessibility debt accumulates fast at bulk-import scale), and know that **`alt=""` is a deliberate statement** that the image is decorative and should be skipped by a screen reader. Omitting the attribute entirely is the bug.

### `hotspot: true` — always turn it on

Without it, cropping to a different aspect ratio centre-crops and beheads people. With it, the editor drags a focal point in the Studio and the URL builder respects it when resizing. **Costs nothing; prevents the most common CMS complaint.**

### The URL builder

```tsx
<Image src={urlFor(post.coverImage).width(1600).url()} alt={…} fill className="object-cover" priority />
```

A chainable builder; `.url()` produces the string. The chain compiles to query params on the CDN, and **the transformation happens on demand, then caches** — upload one 4000px original, serve a 600px thumbnail from it.

Match the width to the slot, and **request 2× the CSS size for small fixed images** (a 40px avatar at `.width(80)` is crisp on retina and still a few KB). Worth adding to a shared wrapper: **`.auto('format')`** for content-negotiated AVIF/WebP, which is close to free bytes.

### Two CDNs, on purpose

With `next/image` (or any framework optimiser) there are now two: the CMS CDN resizes, then the framework's optimiser re-encodes and serves the `srcset`. That's not a mistake — **requesting a sensibly-sized image from the CMS first means the optimiser isn't handed a 4000px original to chew on.**

Remote hosts must be allowlisted, and the reason is worth knowing: otherwise anyone could point your optimiser at any URL and bill you for the CPU.

```ts
images: { remotePatterns: [{ hostname: 'cdn.sanity.io' }] }
```

### The layout pattern

```tsx
<div className="relative aspect-video overflow-hidden">
  <Image src={…} alt={…} fill className="object-cover" />
</div>
```

`fill` absolutely positions the image to fill its nearest positioned ancestor — **so the wrapper needs `relative` and its own height** (here from `aspect-video`). That's what reserves layout space before load and prevents cumulative layout shift. `priority` for the LCP element only; never below the fold.

## Related
- [[frontend/frameworks/sanity/01-the-sanity-model|01 — the Sanity model]] · [[frontend/frameworks/sanity/02-groq|02 — GROQ]]
- [[frontend/06-cross-cutting/01-accessibility|accessibility]] · [[frontend/07-practices/02-performance|performance]]
