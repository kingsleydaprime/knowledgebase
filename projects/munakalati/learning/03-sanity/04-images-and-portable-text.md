# Sanity — Images and Portable Text

**Split from:** the munakalati Sanity domain. **See also:** [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]] · [[projects/munakalati/learning/05-migration/04-portable-text-conversion|migration/04 — converting *into* Portable Text]]
**General version:** [[frontend/frameworks/sanity/03-portable-text-and-images|frontend/frameworks/sanity/03]]

---

## Part 1 — Images

### An image field stores a pointer, not a picture

```ts
defineField({
  name: "coverImage",
  type: "image",
  options: { hotspot: true },
  fields: [ defineField({ name: "alt", type: "string" }) ],
}),
```

What's actually stored on the document is tiny:

```json
{
  "_type": "image",
  "asset": { "_type": "reference", "_ref": "image-abc123def456-1600x900-jpg" },
  "alt": "Children reading in a classroom"
}
```

**The binary lives once in a shared asset store; documents hold references.** Two consequences that matter in practice:

- **Deduplication is automatic.** Upload the same file twice and Sanity returns the same asset ID — which is why the migration's `imageCache` (a `Map` from source URL to asset ref) is an optimisation for *bandwidth and time*, not for correctness.
- **The asset ID encodes the dimensions** — `image-<hash>-1600x900-jpg`. That's how the URL builder can compute an aspect ratio without a round trip, and it's why you can sanity-check a broken image by reading its `_ref`.

### `fields:` on an image type — the alt-text lesson

The `fields:` array adds **extra fields alongside** the asset reference. That's how `alt` (and `caption`, on body images) get stored per-usage.

**Per-usage is the right call, and it's a genuine accessibility point:** alt text describes an image *in the context where it appears*. The same photo might be "Muna Kalati team at the 2024 summit" on the About page and "Our founder accepting the award" in a blog post. Attaching alt to the *asset* would force one description everywhere; attaching it to the *field* lets each use say what it needs.

What the project doesn't do — and should — is `validation: (r) => r.required()` on `alt`. Every usage site is written defensively instead:

```tsx
alt={post.coverImage.alt ?? post.title}     // fall back to the title
alt={value.alt ?? ""}                        // body images: empty = decorative
```

The `?? ""` is not lazy: an empty `alt` is the correct, meaningful signal to a screen reader that an image is decorative and should be skipped. **Omitting the attribute entirely is the bug; `alt=""` is a deliberate statement.** Still — 433 backfilled cover images all have no alt text at all, which is a real accessibility debt this site carries.

### `hotspot: true` — the one option to always turn on

Without it, cropping an image to a different aspect ratio centre-crops. Faces get beheaded. With `hotspot: true` the editor drags a focal point and a crop region in the Studio, and the URL builder respects it when it resizes. **Costs nothing, prevents the single most common CMS complaint.** On by default in every image field here — correct.

### `urlFor()` — building a transformation URL

```ts
const builder = createImageUrlBuilder({ projectId, dataset });
export const urlFor = (source: SanityImageSource) => builder.image(source);
```

```tsx
<Image src={urlFor(post.coverImage).width(1600).url()} alt={...} fill className="object-cover" priority />
```

`urlFor(...)` returns a **chainable builder**; `.url()` is what finally produces the string. The chain compiles to query params on `cdn.sanity.io`, and **the transformation happens on Sanity's CDN, on demand, then caches**. You upload one 4000px original and serve a 600px card thumbnail from the same asset.

The sizes are deliberately matched to the slot:

| Where | Call | Why |
|---|---|---|
| Article hero | `.width(1600)` | full-bleed `21/9` banner |
| Body image | `.width(1200)` | article column |
| Card thumbnail | `.width(600)` | 3-up grid |
| Author avatar | `.width(80)` / `.width(96)` | 40px and 48px circles at 2× |

**That last row is the habit worth naming: request 2× the CSS pixel size for small fixed-size images.** A 40px avatar at `.width(80)` is crisp on a retina screen and still ~4KB.

Things the chain can do that this project doesn't use: `.format('webp')`, `.quality(80)`, `.auto('format')` (content-negotiated AVIF/WebP), `.fit('crop')`. **`.auto('format')` in particular is close to free bytes** — worth adding to a shared wrapper rather than per call site.

### Wiring it to `next/image`

Next refuses to optimise remote images from unlisted hosts — a deliberate anti-abuse measure, since otherwise anyone could point your optimiser at any URL and bill you for the CPU. So `next.config.ts` has to allow the host:

```ts
const sanityPattern: RemotePattern = { hostname: 'cdn.sanity.io' }

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: { remotePatterns: [sanityPattern] },
};
```

**Two CDNs are now in the path**, and it's worth being clear that this is not a mistake: `urlFor().width(600)` resizes on *Sanity's* CDN, then `next/image` fetches that and re-encodes/serves it from *Next's* optimiser. The second pass is what produces the `srcset` and modern formats. Requesting a sensibly-sized image from Sanity first means Next's optimiser isn't handed a 4000px original to chew on.

The rendering pattern is consistent across the site and correct:

```tsx
<div className="relative aspect-video rounded-2xl overflow-hidden">
  <Image src={...} alt={...} fill className="object-cover" />
</div>
```

`fill` makes the image absolutely positioned to fill its nearest positioned ancestor — which is **why the wrapper must have `relative`, and must have its own height** (here from `aspect-video`). This is the pattern that reserves layout space before the image loads, so there's no cumulative layout shift. `priority` on the article hero tells Next to preload it rather than lazy-load — right for the LCP element, wrong for anything below the fold.

## Part 2 — Portable Text

### Why rich text isn't HTML

`post.body` is `type: "array"` of `block` and `image`. What's stored is **structured JSON, not markup**:

```json
{
  "_type": "block",
  "_key": "a1b2c3d4",
  "style": "h2",
  "markDefs": [],
  "children": [
    { "_type": "span", "_key": "e5f6", "text": "Stories that shape", "marks": ["strong"] }
  ]
}
```

The argument for this over an HTML string is the whole reason Portable Text exists: **an HTML blob is only renderable as HTML.** The same content here can render to React on the web, to native components in an app, to plain text for a search index, or to whatever comes next — because it never encoded a rendering decision. It's also *safely* renderable: there is no arbitrary markup to sanitise, because there is no markup. And it's diffable and queryable — GROQ can reach inside blocks.

The cost is that **nothing renders until you say how**, which is Part 3.

### The four things in the format

- **`block`** — a paragraph-level unit. `style` is `normal | h2 | h3 | blockquote | ...`; `listItem` and `level` handle lists.
- **`span`** — a run of text inside a block, split wherever formatting changes. "This is **bold** text" is three spans, not one.
- **`marks`** — an array of strings on a span. Either a simple decorator (`"strong"`, `"em"`) **or a `_key` pointing into `markDefs`**.
- **`markDefs`** — block-level definitions for marks that carry data. A link is `markDefs: [{_key: "x1", _type: "link", href: "https://..."}]` and the span carries `marks: ["x1"]`.

**That indirection is the piece people get wrong.** A link's `href` is *not* on the span; the span references a definition on its parent block. It's a normalisation — the same annotation can cover several spans without repeating its data.

### `_key` is mandatory, and forgetting it bites later

Every block and every span needs a `_key`, unique among its siblings. Sanity uses it to diff arrays for real-time collaboration — without stable keys, two editors typing in the same document produce garbage. The migration generates them:

```js
function key() { return Math.random().toString(36).slice(2, 10); }
```

`Math.random().toString(36)` renders a random float in base 36 (`0-9a-z`), and `.slice(2, 10)` drops the leading `0.` and keeps eight characters. Good enough — ~2.8 × 10¹² combinations against a handful of siblings. **Not** what you'd use for anything security-relevant; `crypto.randomUUID()` is the correct reach if it ever matters.

## Part 3 — Rendering it

`<PortableText>` walks the array and calls a renderer per node. The `components` map in `src/app/(site)/blog/[slug]/page.tsx` is the whole design system for article bodies:

```tsx
const portableTextComponents = {
  block: {
    normal: ({ children }) => <p className="text-[17px] text-mid leading-relaxed mb-6">{children}</p>,
    h2:     ({ children }) => <h2 className="font-display text-[28px] font-bold ... mt-12 mb-5">{children}</h2>,
    blockquote: ({ children }) => <blockquote className="border-l-4 border-primary pl-6 my-8">...</blockquote>,
  },
  list:  { bullet: ..., number: ... },
  marks: {
    strong: ({ children }) => <strong className="font-semibold text-dark">{children}</strong>,
    link: ({ value, children }) => (
      <a href={value?.href} target="_blank" rel="noopener noreferrer" className="...">{children}</a>
    ),
  },
  types: {
    image: ({ value }) => (
      <figure className="my-10">
        <div className="relative aspect-video rounded-2xl overflow-hidden">
          <Image src={urlFor(value).width(1200).url()} alt={value.alt ?? ""} fill className="object-cover" />
        </div>
        {value.caption && <figcaption className="...">{value.caption}</figcaption>}
      </figure>
    ),
  },
};
```

**Four buckets, and knowing which is which is most of the skill:**

- **`block`** — keyed by `style`. Your `h2`/`h3`/`normal`/`blockquote`.
- **`list`** — the `<ul>`/`<ol>` wrappers (`listItem` handles the `<li>`).
- **`marks`** — inline. Both decorators (`strong`) and annotations (`link`, which receives the `markDefs` entry as `value`).
- **`types`** — **non-text blocks.** Anything in the schema's `of: [...]` that isn't `block`. Here, images. This is the extension point: add a `{ type: "youtube" }` to the schema and it renders here.

**The `types.image` renderer is why the format pays off.** Images inside article bodies are not HTML `<img>` tags being sanitised and hoped over — they're structured nodes that go through `next/image` with a hotspot-aware CDN URL, wrapped in a semantic `<figure>` with a real `<figcaption>`. You cannot do that from an HTML string without parsing and rewriting it.

**`rel="noopener noreferrer"` on external links** is not boilerplate: `noopener` stops the opened page from reaching back through `window.opener` and navigating your tab somewhere hostile. Modern browsers imply it for `target="_blank"`, but writing it is still correct.

### The type hole

```tsx
<PortableText value={post.body as Parameters<typeof PortableText>[0]["value"]} components={portableTextComponents} />
```

That cast exists because `types.ts` declares `body?: unknown[]` by hand. It reads as sophisticated TypeScript — `Parameters<typeof X>[0]["value"]` extracts the first parameter's `value` property type — but all it's doing is **telling the compiler to stop asking**. TypeGen would type `body` properly from the schema and the cast would delete itself. Any time a cast is this baroque, the real fix is upstream of it.

## Related
- [[projects/munakalati/learning/05-migration/04-portable-text-conversion|migration/04 — building Portable Text from Wix nodes]]
- [[frontend/07-practices/02-performance|performance]] — images are most of a content site's bytes
- [[frontend/06-cross-cutting/01-accessibility|accessibility]] — the alt-text debt above
