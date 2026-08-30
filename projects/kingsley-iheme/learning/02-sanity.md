# 02 — Sanity (schemas, GROQ, Portable Text, embedded Studio)

Part of the [[projects/kingsley-iheme/learning/README|kingsley-iheme learning log]]. Siblings: [[projects/kingsley-iheme/learning/01-frontend|01-frontend]] · [[projects/kingsley-iheme/learning/03-backend-api|03-backend-api]] · [[projects/kingsley-iheme/learning/04-devops|04-devops]].

> **How this relates to the vault's other Sanity notes.** [[projects/munakalati/learning/03-sanity/README|munakalati]] has a deeper five-note Sanity course (11k words) covering content modelling at larger scale, `->` joins, `markDefs`, Structure Builder, and a Wix migration. The general folder `frontend/frameworks/sanity/` is an empty stub, so **both instances live only under `projects/`**.
>
> This file is the smaller, differently-shaped instance: two document types instead of sixteen, a **discriminated union** as the central modelling decision, and a graceful-degradation fetch wrapper that munakalati has no equivalent of. Written to stand alone — where it independently reaches the same conclusion as munakalati (API version as a date, schema validation ≠ database constraint, `defined()` in queries), that agreement is the point.

---

## 1. What Sanity actually is, and why it was picked here

Sanity is a **headless CMS**: it stores structured content and exposes it over an API, with no opinion about how you render it. Three parts:

| Part | What it is | Where it lives here |
|---|---|---|
| **Content Lake** | Hosted document store. Schemaless at rest — documents are JSON with a `_type` | Sanity's servers |
| **Studio** | The editing UI. A React app *you* configure and deploy | `/studio` route in this Next app |
| **GROQ** | Query language for pulling content out | `src/sanity/lib/queries.ts` |

**The requirement that chose it.** From `PLAN.md`: *"He wants to self-manage content going forward without needing a developer."* That single line eliminates the MDX-files-in-the-repo blog that would otherwise be the obvious choice for a portfolio site. Kingsley is a writer, not a git user — asking him to open a PR to publish a blog post means he never publishes a blog post.

That reframes the whole decision. The question isn't "which CMS has the nicest API" — it's **"who edits this in two years, and what happens the first time they want to change something?"** A CMS is a handover artifact. Weigh it as one.

**The critical property: schemaless at rest, schema-on-write in the Studio.** The Content Lake will happily store any JSON. Your schema definitions are validation and UI configuration for the *editing experience* — they are not database constraints. This is the single biggest thing to internalise, and §4 is where it bites.

---

## 2. Schema design — the discriminated union

The blog has a genuine modelling problem. Kingsley publishes in two places: essays written for this site, and pieces published on Medium/LinkedIn that should still appear in the blog index but link *out*.

Three ways to model that:

1. **Two document types** (`post` and `externalPost`). Clean separation, but now every query is a union, the Studio has two menu items that mean nearly the same thing, and sorting a merged list by date needs client-side work.
2. **One type, nullable fields.** Simple, but nothing tells an editor which fields matter, and nothing stops a post having both a body and an external URL.
3. **One type with a discriminator field.** ✅

```ts
// src/sanity/schemaTypes/post.ts
defineField({
  name: "postType",
  type: "string",
  options: {
    list: [
      { title: "Native (written on this site)", value: "native" },
      { title: "External (published elsewhere)", value: "external" },
    ],
    layout: "radio",
  },
  initialValue: "native",
  validation: (rule) => rule.required(),
}),
```

This is a **tagged/discriminated union**, the same construct as a Rust enum or a TypeScript union with a literal `kind` field. One type, one query, one sorted list — with a field that says which shape you're looking at.

`layout: "radio"` matters more than it looks: a dropdown hides the options until clicked, and this choice changes which *other* fields appear. Making it two visible radio buttons means the editor understands the decision they're making before they make it.

### Conditional fields: `hidden` is UX, `validation` is the contract

```ts
defineField({
  name: "body",
  type: "array",
  of: [{ type: "block" }],
  hidden: ({ document }) => document?.postType !== "native",       // ← UI only
  validation: (rule) =>
    rule.custom((value, context) => {                              // ← the actual rule
      const doc = context.document as { postType?: string } | undefined;
      if (doc?.postType === "native" && (!value || value.length === 0)) {
        return "Body is required for native posts";
      }
      return true;
    }),
}),
```

The same pairing repeats for `externalUrl` and `externalSource`, inverted.

**The distinction is the lesson.** `hidden` is a *presentation* predicate — it declutters the form so an editor writing a native post never sees "External URL". It enforces nothing; a hidden field can still hold a value (switch a post from external to native and the old `externalUrl` is still sitting in the document, just invisible).

`validation` is what actually blocks a publish. And note it must be `rule.custom()` rather than `rule.required()`, because the requirement is *conditional* — required only when `postType === "native"`. `context.document` gives the sibling-field access that makes cross-field rules possible.

**Returning a string from a validator = the error message shown to the editor. Returning `true` = valid.** Write those messages for the person in the Studio, not for yourself: "Body is required for native posts" tells an editor exactly what to do. "Invalid" does not.

The general habit — **hide for clarity, validate for correctness, and never confuse the two** — applies well beyond Sanity. It's the same reason a disabled submit button is not input validation.

### Previews: make the list view readable

```ts
preview: {
  select: { title: "title", postType: "postType", media: "coverImage" },
  prepare({ title, postType, media }) {
    return { title, subtitle: postType === "external" ? "External" : "Native", media };
  },
},
```

Without this, the Studio's document list shows titles and nothing else, and an editor can't tell a native post from an external one without opening each. Ten documents in, that's mildly annoying; a hundred in, it's the difference between a usable CMS and one they stop using.

`select` maps document paths to preview keys; `prepare` derives the display values. The `book` schema uses the shorthand — `select: { title, media, subtitle: "platform" }` with no `prepare` — because no derivation is needed. **Reach for `prepare` only when you're computing something.**

**Preview config is not decoration.** It's the main lever you have on whether the CMS is pleasant to use, and it costs four lines. Skipping it is the most common way a technically-correct Sanity setup ends up disliked by the people who have to live in it.

### `slug` and the hotspot flag

```ts
defineField({ name: "slug", type: "slug", options: { source: "title", maxLength: 96 } })
defineField({ name: "coverImage", type: "image", options: { hotspot: true } })
```

`source: "title"` gives the Studio a "Generate" button that slugifies the title — the editor never hand-writes a URL. `hotspot: true` lets the editor drag a focal point on the image; crops at any aspect ratio then keep the subject's face in frame instead of centre-cropping it off. On a site full of book covers and portraits, that's the difference between usable auto-cropping and beheaded author photos.

---

## 3. The embedded Studio

```ts
// sanity.config.ts
export default defineConfig({
  basePath: "/studio",              // ← must match the route folder
  name: "kingsley-iheme",
  projectId, dataset,
  schema: { types: schemaTypes },
  plugins: [structureTool(), visionTool({ defaultApiVersion: apiVersion })],
});
```

Mounted at `src/app/(studio)/studio/[[...tool]]/`. Two things to read there:

- **`[[...tool]]`** — double brackets are an *optional* catch-all. It matches `/studio` **and** `/studio/desk/post;abc`. A single-bracket `[...tool]` would 404 on the bare `/studio`. The Studio is a client-side router that needs to own every path beneath its base.
- **`(studio)`** — the route group from [[projects/kingsley-iheme/learning/01-frontend|01 §1]], keeping the site header/footer off it.

**Embedded vs. standalone.** Sanity can deploy the Studio separately (`sanity deploy` → `yourproject.sanity.studio`). Embedded won here for a single-maintainer site: one deploy, one domain, one set of env vars, and the schema lives next to the code that consumes it — so a schema change and the query change that depends on it land in the same commit. The cost is that Studio code is part of your Next build (slower builds, bigger `node_modules`). For a team with dedicated editors and a separate release cadence, standalone is often better.

**`visionTool` is the one to know about.** It adds a GROQ playground inside the Studio — write a query, see live results against real data. Every query in `queries.ts` is much faster to develop there than by editing TypeScript and refreshing the site. `defaultApiVersion` is passed so Vision matches the app's API version rather than defaulting to something else.

**Auth is Sanity's, not yours.** No login code was written for `/studio`; the Studio authenticates against Sanity's own service and permissions are managed in the Sanity dashboard. This is why `/studio` being a public *route* isn't a security problem — the page loads, then demands a login. That's also why `robots.txt` disallowing it is SEO hygiene rather than protection ([[projects/kingsley-iheme/learning/01-frontend|01 §6]]).

---

## 4. `sanityFetch` — the graceful-degradation wrapper, and its cost

This 15-line function is the most consequential piece of code in the project.

```ts
// src/sanity/lib/client.ts
export const client = createClient({
  projectId: projectId || "placeholder",
  dataset, apiVersion,
  useCdn: true,
});

export async function sanityFetch<T>(
  query: string,
  params: Record<string, unknown> = {},
  fallback: T
): Promise<T> {
  if (!isSanityConfigured) return fallback;
  try {
    return await client.fetch<T>(query, params);
  } catch {
    return fallback;
  }
}
```

**The requirement it satisfies**, from the README: *"The site runs and looks correct even with no CMS, booking tool, or email service connected."*

That's not a nicety — it's a handover requirement. This site is built for someone else to take over. If a missing `NEXT_PUBLIC_SANITY_PROJECT_ID` crashed the build, then the first `bun run dev` after cloning would fail with a stack trace, and every deploy before the CMS was wired up would be red.

Three design choices, each worth understanding:

**1. `projectId: projectId || "placeholder"`.** `createClient` throws on an empty `projectId` — at *module load*, which in Next means the whole route fails to render. Since this module is imported by the home page, the sitemap, and the OG image generator, an unconfigured project would take down the entire site rather than one page. The placeholder makes construction always succeed; the `isSanityConfigured` guard makes sure it's never actually used.

**2. The `fallback` parameter is required and typed.** Not optional, not defaulted to `null`. Every call site must state what "no data" looks like *for that call*:

```ts
const posts   = await sanityFetch<Post[]>(ALL_POSTS_QUERY, {}, []);          // empty list
const book    = await sanityFetch<Book | null>(FEATURED_BOOK_QUERY, {}, null); // no book
const slugs   = await sanityFetch<string[]>(ALL_POST_SLUGS_QUERY, {}, []);     // nothing to prerender
```

This is the good bit of the design. A generic `catch → return null` would push `null` checks into every consumer and make `posts.map()` a crash waiting to happen. Forcing a typed, call-site-appropriate empty value means the pages downstream are written against a total function — `posts` is *always* an array — and the empty states (`{posts.length === 0 ? <p>No posts yet</p> : ...}`) fall out naturally rather than being defensive extras.

**3. `useCdn: true`.** Reads go through Sanity's cached API edge instead of hitting the origin. Faster and cheaper, at the cost of content being up to ~60s stale. Paired with `revalidate = 60` that's coherent: two caches of the same order, so worst case is roughly two minutes from publish to live. Worth knowing: `useCdn: true` is **wrong** for draft/preview mode and for any authenticated read, which want fresh data from the origin.

### The cost: `catch {}` erases the difference between broken and empty

```ts
} catch {
  return fallback;
}
```

A bare catch with no binding. Sanity down, network partition, malformed GROQ, revoked token, typo'd dataset name — every one of these produces exactly the same visible outcome as *"the CMS is working fine and there are genuinely no posts yet."*

The page says "No posts yet — check back soon." The build goes green. Nobody is paged. In the most damaging version, `generateStaticParams` returns `[]` during a transient failure, **the build succeeds with zero blog pages prerendered**, and the site quietly ships without its blog.

That is the classic failure mode of graceful degradation: *it degrades gracefully past the point where you wanted to know.* Compare the deliberate distinction drawn in [[projects/kingsley-iheme/learning/03-backend-api|03]], where the contact API returns a **503 `not_configured`** that is explicitly different from a 502 send failure — the API separates "not set up" from "broken", and this fetcher doesn't.

**The fix is small and doesn't sacrifice the behaviour:**

```ts
} catch (error) {
  console.error(`[sanity] query failed: ${query.slice(0, 80)}`, error);
  return fallback;
}
```

Still degrades, still never crashes a page — but now the failure is visible in Vercel's function logs, which is where you'd actually look. Keeping the user experience soft and the operator experience loud is the goal; a silent catch gives up the second half for nothing.

This connects to a standing habit from [[projects/gees-arise/learning/09-sys-design|gees-arise]]: *read errors and logs fully before reacting.* You can't do that if the code never wrote one down.

---

## 5. GROQ

GROQ (Graph-Relational Object Queries) is Sanity's query language. Structure of a query:

```groq
*[_type == "post"] | order(publishedAt desc)[0...3]{ _id, title, slug }
 └───┬──────────┘   └────────┬────────────┘└──┬──┘└────────┬───────┘
  filter            ordering        slice      projection
```

- **`*`** — every document in the dataset. Everything else narrows it.
- **`[...]`** — filter. `_type == "post" && slug.current == $slug`. `$slug` is a parameter, passed separately — **this is also the injection-safe path**; never interpolate user input into the query string.
- **`| order(...)`** — pipe into an ordering. Multi-key works: `order(publishedYear desc, _createdAt desc)` — a deterministic tiebreak, so two books from the same year don't shuffle between requests.
- **`[0...3]`** — slice, zero-indexed, end-exclusive. **`[0]` (single index) returns an object; `[0...1]` returns a one-element array.** That's why `FEATURED_BOOK_QUERY` ends in `[0]` and is typed `Book | null`, while `LATEST_POSTS_QUERY` ends in `[0...3]` and is typed `Post[]`. Getting this wrong yields `posts.map is not a function`.
- **`{...}`** — projection: the fields to return. **You always specify these.** There is no `SELECT *` by default, which is the right default — a projection is a contract, and it means adding a field to a schema never silently changes a payload.

Three techniques from `queries.ts` worth stealing:

```groq
// 1. Fetch only what you need — this returns a flat array of STRINGS, not objects
*[_type == "post" && postType == "native" && defined(slug.current)].slug.current
```
Trailing `.slug.current` after the filter projects a single field per document and flattens. Consumed as `string[]` with no `.map(d => d.slug)` on the JS side.

```groq
// 2. defined() guards against missing/null fields
*[_type == "post" && defined(slug.current)]
```
Because the Content Lake is **schemaless at rest** (§1), a document *can* exist without a slug — schema validation runs in the Studio, but a document created via the API, imported, or written before the field existed bypasses it entirely. `defined()` is not paranoia; it's an acknowledgement of where the constraints actually live. Skipping it here would put `/blog/undefined` in `generateStaticParams`.

```groq
// 3. Rename on projection
*[...]{ "slug": slug.current, publishedAt, _updatedAt }
```
`SITEMAP_POSTS_QUERY` flattens the nested slug object into a plain string named `slug`, so the sitemap consumes `post.slug` directly. Quoted key + path = SQL's `AS`.

Also note `_updatedAt` — Sanity maintains `_id`, `_type`, `_createdAt`, `_updatedAt` and `_rev` on every document for free. `_updatedAt` powers the correct `lastModified` in the sitemap ([[projects/kingsley-iheme/learning/01-frontend|01 §6]]).

### 🐛 Bug: the detail query is missing its `postType` filter

Compare these two, both from `queries.ts`:

```groq
ALL_POST_SLUGS_QUERY:  *[_type == "post" && postType == "native" && defined(slug.current)].slug.current
POST_BY_SLUG_QUERY:    *[_type == "post" && slug.current == $slug][0]{ ..., body, ... }
                                          ↑ no postType filter
```

`generateStaticParams` correctly prerenders only native posts. But `/blog/<slug-of-an-external-post>` isn't prerendered — it's rendered on demand, the query **finds the document**, `notFound()` is never called, and the visitor gets a post page with a title, a date, and no body, because external posts have no `body`.

The blog index links external posts straight to `post.externalUrl`, so nothing in the UI produces this URL. It shows up via a shared link, a stale bookmark, or a crawler — and a thin bodiless page is exactly what Google penalises.

**Fix** — one clause, making the query say what the route actually means:

```groq
*[_type == "post" && postType == "native" && slug.current == $slug][0]{ ... }
```

Then the existing `if (!post) notFound()` does the right thing and returns a real 404.

**The general lesson:** when two queries encode the same rule (*"only native posts have detail pages"*), they will drift, because nothing links them. The rule lived in one query and not the other, and the only reason it wasn't caught is that the happy path never generates the URL. Worth a scan whenever you see a filter in one query that's absent from its sibling.

---

## 6. Portable Text

Sanity does not store HTML or Markdown. Rich text is stored as **Portable Text**: a JSON array of block objects.

```json
[{ "_type": "block", "style": "h2", "children": [
    { "_type": "span", "text": "Hello", "marks": ["strong"] }] }]
```

Why this is right, and not over-engineering:

- **It's structured, so it's queryable and transformable.** You can find every post containing a given link, or every H2, with a query. Try that against a blob of HTML.
- **It's presentation-agnostic.** The same document renders to a web page, an RSS feed, a native mobile app, or a plain-text email. HTML in a database has already decided it's going to a browser.
- **It's safe by construction.** There is no HTML to sanitise, so **there is no XSS vector in the content itself** — you render known node types through components you wrote. Compare a Markdown CMS with `dangerouslySetInnerHTML`, where every post is a potential injection.

The cost: you can't just print it. You need a renderer.

```tsx
// src/app/(site)/blog/[slug]/page.tsx
import { PortableText } from "@portabletext/react";
<PortableText value={post.body} />
```

`@portabletext/react` walks the array and maps node types to React components. Defaults handle paragraphs, headings, lists and marks; a `components` prop overrides any of it. **The moment the schema grows a custom block type** — an inline image, a pull-quote, an embed — the renderer needs a matching entry, or that block renders as nothing. Currently `of: [{ type: "block" }]` is plain text only, so defaults suffice. Adding `{ type: "image" }` to the schema without adding an `image` component to the renderer is the classic "why is my image invisible" bug.

The body is styled with `@tailwindcss/typography` (loaded via `@plugin` in `globals.css`) — one `prose` class styles all the generated markup, which is the reason that plugin exists.

---

## 7. Images: URL-based transformation

```ts
// src/sanity/lib/image.ts
const imageBuilder = createImageUrlBuilder({ projectId, dataset });
export function urlForImage(source: Image) { return imageBuilder.image(source); }
```

```tsx
<Image src={urlForImage(featuredBook.coverImage).width(400).height(600).url()} fill />
```

Sanity stores an asset reference; the builder turns it into a CDN URL with transformations encoded as query params. Resizing, cropping, format conversion and quality all happen **on Sanity's CDN**, cached, with no image processing in your app and no originals in your repo.

The chainable API (`.width().height().url()`) is a builder pattern — nothing happens until `.url()`. And it respects the `hotspot` set in the Studio (§2), so a 400×600 crop of a portrait keeps the face.

This is why `next.config.ts` must allowlist `cdn.sanity.io` ([[projects/kingsley-iheme/learning/01-frontend|01 §9]]) — two image pipelines in sequence: Sanity crops and resizes, `next/image` handles format negotiation and lazy loading.

---

## 8. Types: hand-written, when they could be generated

```ts
// src/sanity/lib/types.ts — hand-maintained
export interface Post {
  _id: string;
  title: string;
  slug: { current: string };
  postType: "native" | "external";
  publishedAt: string;          // ISO string, not a Date — it crossed a JSON boundary
  excerpt: string;
  coverImage?: Image;
  body?: PortableTextBlock[];
  externalUrl?: string;
  externalSource?: string;
}
```

Reasonable, and note the discriminator is typed as a literal union mirroring the schema. Two observations:

**`publishedAt: string`.** Sanity's `datetime` arrives as an ISO 8601 string, because it came over JSON. Hence `new Date(post.publishedAt).toLocaleDateString(...)` at every render site. Don't type it `Date` and hope.

**The optionality is a lie the type system can't catch.** `body?` and `externalUrl?` are optional because *either* may be absent. But the real invariant is stronger: `postType: "native"` ⟹ `body` present and `externalUrl` absent, and vice versa. A discriminated union in TypeScript would encode that:

```ts
type Post = { _id: string; title: string; /* ...shared... */ } & (
  | { postType: "native";   body: PortableTextBlock[] }
  | { postType: "external"; externalUrl: string; externalSource: string }
);
```

That would make the non-null assertion on the home page — `post.postType === "external" ? post.externalUrl! : ...` — unnecessary, because narrowing on `postType` would prove `externalUrl` exists. **Every `!` is a place the type system knows less than you do**, and here it's avoidable: the shape of the type doesn't match the shape of the data.

### The bigger miss: `defineQuery` is present and unexploited

```ts
import { defineQuery } from "next-sanity";
export const ALL_POSTS_QUERY = defineQuery(`*[_type == "post"] | order(...){...}`);
```

At runtime `defineQuery` is an identity function — it returns the string unchanged. Its entire purpose is to be a **static marker** that Sanity's TypeGen can find. The workflow it enables:

```bash
bunx sanity schema extract    # schema definitions  → schema.json
bunx sanity typegen generate  # schema.json + every defineQuery() → sanity.types.ts
```

TypeGen parses each GROQ query, works out the exact shape that *projection* returns, and emits a precise type per query. Not "a Post" — the specific subset of fields that query asked for, with correct optionality derived from the schema.

Neither `schema.json` nor `sanity.types.ts` exists here, and there's no typegen script in `package.json`. So `defineQuery` is currently doing nothing at all, and `types.ts` is hand-maintained in parallel with the schema.

**Why that's worth fixing.** Hand-written types can silently disagree with the query in ways that compile fine and break at runtime — add a field to a projection and forget the interface, rename a schema field and the interface still claims the old name, or (the sharp one) `ALL_POSTS_QUERY` doesn't project `body` yet everything is typed as `Post`, which *declares* `body?`. Code that reads `post.body` off a list item typechecks and is always `undefined`. Generated types would have caught that at compile time, because the list query's type wouldn't have a `body` field at all.

Two commands and a `package.json` script away — the scaffolding is already in the code. Good candidate for the next commit.

---

## 9. API versioning

```ts
export const apiVersion = process.env.NEXT_PUBLIC_SANITY_API_VERSION || "2024-01-01";
```

Sanity versions its API **by date**. You pin one, and that date's behaviour is frozen for you — GROQ semantics and response shapes won't shift underneath a deployed site. Upgrading is a deliberate act: change the date, test, ship.

This is a genuinely good API design pattern worth borrowing (Stripe does the same). It converts "we shipped a change and your integration broke" into "you chose to move to a newer version." The failure mode is the opposite one: pin a date, never revisit it, and drift years behind. Pinning is a commitment to occasional upgrades, not a way to avoid them.

---

## Takeaways

1. **Pick a CMS by asking who edits the content in two years.** "The author must publish without a developer" eliminated MDX before any API comparison mattered.
2. **Model either/or content as a discriminated union**, not two document types and not nullable fields. One type, one query, one sorted list.
3. **`hidden` is UX; `validation` is the contract.** Hidden fields still hold data. Use `rule.custom()` with `context.document` for conditional requirements, and write error messages for the editor.
4. **Sanity is schemaless at rest.** Schema = Studio validation, not database constraints. Hence `defined()` in queries.
5. **Configure `preview`.** Four lines decide whether the CMS is usable at 100 documents.
6. **Force call sites to declare their empty value.** A required, typed `fallback` beats `catch → null` and makes downstream code total.
7. **Never `catch {}` silently.** Log the error, still return the fallback. Soft for the user, loud for the operator — this code gets the first half only.
8. **GROQ `[0]` returns an object; `[0...1]` returns an array.** Parameterise with `$var`; project explicitly; use `defined()`.
9. **Duplicated rules across sibling queries drift.** The missing `postType == "native"` in the detail query is exactly that.
10. **Portable Text is structured, portable, and XSS-free by construction** — but a new block type in the schema needs a matching renderer component.
11. **If you're calling `defineQuery`, run TypeGen.** Otherwise you're maintaining types by hand next to a tool that would generate exact ones.
