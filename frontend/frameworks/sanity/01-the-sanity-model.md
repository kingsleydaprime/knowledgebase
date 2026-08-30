# The Sanity Model

**Part of [[frontend/frameworks/sanity/README|frameworks/sanity]].** `[reference]`
**Concepts:** [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modelling and headless CMS]] · **Real code:** [[projects/munakalati/learning/03-sanity/01-setup-and-mental-model|munakalati]]

---

## What it is

**A hosted document database, plus an admin UI generated from a schema you write in JavaScript.** No templating, no theming, no opinion about rendering. You get JSON over an API and a React editing app; the website is entirely yours.

Three things ship in one project:

| | What | Where it lives |
|---|---|---|
| **The content backend** | schema definitions, a hosted dataset, an API | `sanity/schemaTypes/`, hosted |
| **The Studio** | a React SPA generated from the schema | `sanity.config.ts`, mounted at a route or deployed separately |
| **The site** | anything that can fetch JSON | your framework |

**The Studio and the site are two applications**, even when they deploy from one repo. That single fact explains most of what's initially confusing — why `sanity.config.ts` starts with `'use client'` while the pages reading the content are Server Components, for instance.

## The four coordinates

Every read and write needs the same four values:

```ts
export const apiVersion = process.env.NEXT_PUBLIC_SANITY_API_VERSION || '2026-05-07'
export const dataset    = assertValue(process.env.NEXT_PUBLIC_SANITY_DATASET, 'Missing …DATASET')
export const projectId  = assertValue(process.env.NEXT_PUBLIC_SANITY_PROJECT_ID, 'Missing …PROJECT_ID')
```

1. **`projectId`** — the project. Public; it appears in every image URL.
2. **`dataset`** — a named silo of documents inside it (`production`, `staging`). **The unit of copying** — `sanity dataset export` / `import`.
3. **`apiVersion`** — a **date**, see below.
4. **A token** — writes only. Reads of a public dataset are unauthenticated.

**Centralise and assert these in one module.** A missing env var should fail at import with a named error, not become `undefined` inside a URL that 404s three layers deeper.

### The API version is a date, not a semver

`apiVersion: '2026-05-07'` means *"behave the way you behaved on 7 May 2026."*

Sanity changes GROQ semantics and endpoint behaviour over time. Saying "latest" would let a change on their side silently alter your query results in production. Pinning a date freezes the contract; you bump it deliberately, read the changelog, and test.

**Practical rule:** pick today's date when you start, then leave it. **Keep every client in the project on the same date** — the app, the scripts, the Studio, the Vision plugin. A query returning one shape in the app and another in a script is a nasty bug class.

## Two clients, and the `useCdn` decision

```ts
// reading, to display
export const client = createClient({ projectId, dataset, apiVersion, useCdn: true })

// reading in order to write
const sanity = createClient({ projectId, dataset, apiVersion, token, useCdn: false })
```

**`token`** is required for `create`, `createOrReplace`, `patch`, `delete` and `assets.upload`. It is a secret — never expose it to the browser. In Next terms, that means **not** naming it `NEXT_PUBLIC_*`; that prefix is a security boundary, not a style choice.

**`useCdn: true`** routes reads through a cache — fast, cheap, seconds-stale. **`useCdn: false`** hits the live API.

> **The rule: any read whose result decides a write must use `useCdn: false`.** Deciding what to delete from a stale snapshot is how you delete the wrong document.

And when the framework does its own caching (ISR, tag revalidation), **the staleness of the layers composes.** A CDN in front of a page cache means the freshness you actually ship is the sum, not the tighter of the two.

## Schemas

```ts
export default defineType({
  name: "post",            // machine name — appears in GROQ as _type == "post"
  title: "Blog Post",      // what the editor sees
  type: "document",        // top-level, independently addressable
  fields: [
    defineField({ name: "title", type: "string", validation: (r) => r.required() }),
    defineField({ name: "slug",  type: "slug",   options: { source: "title", maxLength: 96 } }),
    defineField({ name: "author", type: "reference", to: [{ type: "author" }] }),
    defineField({
      name: "coverImage", type: "image",
      options: { hotspot: true },
      fields: [defineField({ name: "alt", type: "string" })],   // extra fields on the image
    }),
    defineField({
      name: "category", type: "string",
      options: { list: [{ title: "News", value: "news" }, /* … */] },
    }),
  ],
  preview: {
    select: { title: "title", author: "author.name", media: "coverImage" },
    prepare: ({ title, author, media }) => ({ title, subtitle: author ? `by ${author}` : "No author", media }),
  },
});
```

**A schema does three jobs simultaneously**, and the third is the one developers underrate:

1. **Validation** — what the API will accept.
2. **UI generation** — the form an editor sees is derived entirely from this.
3. **Documentation** — `title` and `description` are the only instructions a non-technical editor gets, delivered at exactly the moment they're needed.

**`defineField` / `defineType` are not decoration.** They're identity functions that give TypeScript the context to narrow the object type, so `options: { hotspot: true }` typechecks on an `image` and errors on a `string`. Always use them.

**`preview` is purely a Studio concern** — how a document appears in a list. It matters far more than it looks at scale: without a `media` and `subtitle`, four hundred documents are four hundred identical rows. Give the subtitle an explicit fallback (`"No author"`) so broken data is visible rather than blank.

### `required()` is a form check, not a constraint

> **The API accepts documents that violate your schema.** `validation: (r) => r.required()` runs in the Studio. A migration, a script, or any direct API write bypasses it entirely — and it never applies retroactively to documents created before a field existed.

The consequence is a defensive habit in queries:

```groq
*[_type == "post" && defined(publishedAt) && publishedAt <= now()]
*[_type == "stat" && (context == "home" || !defined(context))]
```

Both those fields are `required()`. Both are guarded anyway. **If you need a real guarantee, enforce it in the query with `defined()` or run a script over the dataset** — never assume stored data satisfies the current schema.

## Singletons are a convention, not a feature

There's no "only one of these" flag. A singleton is **a document with a well-known ID that every reader agrees to use**, held in place by three cooperating conventions:

```ts
// 1. Structure Builder links the sidebar straight to that one ID, and hides the type from the generic list
S.listItem().title("Hero Content").id("heroContent")
  .child(S.document().schemaType("heroContent").documentId("heroContent")),
…S.documentTypeListItems().filter((item) => !["heroContent"].includes(item.getId() ?? "")),
```

```groq
// 2. the query pins the ID rather than taking [0] of all of them
*[_type == "heroContent" && _id == "heroContent"][0] { … }
```

```ts
// 3. and to actually prevent creation:
__experimental_actions: ['update', 'publish']    // no create, no delete
```

**The pinned `_id` in the query is the load-bearing part.** Without it, a stray second document could silently start winning. With it, a duplicate is inert.

## Structure Builder

By default the Studio lists every document type alphabetically — **a developer's view of the content model.** An editor thinks in *pages and tasks*. Structure Builder is where you translate:

```ts
export const structure: StructureResolver = (S) =>
  S.list().title("Content").items([
    /* pinned singletons */,
    S.divider(),
    ...S.documentTypeListItems().filter(/* minus the pinned ones */),
  ]);
```

Beyond pinning: filtered lists (`S.documentTypeList("post").filter('featured == true')`), grouping related types under one folder, and per-type preview panes. **Roughly a dozen document types is where this stops being optional.**

## The embedded Studio

Mounting the Studio inside the app (rather than deploying it separately) is four decisions in ten lines:

```tsx
'use client'
import dynamic from 'next/dynamic'
import config from '../../../../sanity.config'

const NextStudio = dynamic(() => import('next-sanity/studio').then((m) => m.NextStudio), { ssr: false })
export default function StudioPage() { return <NextStudio config={config} /> }
```

- **`[[...tool]]` optional catch-all route** — the Studio is a client-routed SPA owning every path under `/studio`, *including the bare `/studio`*, which a plain `[...tool]` would 404.
- **`'use client'`** — it's a stateful editor touching `window` and `localStorage`.
- **`ssr: false`** — `'use client'` alone still pre-renders to HTML at build time, which would throw. This says never render on the server at all.
- **`dynamic()`** — puts the (large) Studio in its own chunk, so a visitor reading a blog post never downloads a byte of it. **The pattern for any heavy, route-specific, browser-only dependency.**

**Embed** for one deploy, one domain, no CORS — right for a small team. **Deploy separately** when content editors must keep working through a frontend incident, since embedding means a broken site deploy takes the CMS down with it.

## TypeGen — use it

```bash
npx sanity typegen generate
```

Reads your schema **and** every `groq`-tagged query, and emits a type per query — so a projection that selects three fields produces a three-field type.

**Hand-written types drift, and in the dangerous direction: declaring more than the data has.** The classic failure is typing a projection's result as the full document type — code reads `related[0].author.name`, it typechecks, and it throws at runtime because that query never selected `author`. The `groq` tag costs nothing and is the prerequisite.

## Related
- [[frontend/frameworks/sanity/02-groq|02 — GROQ]] · [[frontend/frameworks/sanity/03-portable-text-and-images|03 — Portable Text and images]]
- [[projects/munakalati/learning/03-sanity/README|munakalati — Sanity in practice]]
- [[devops/09-secret-management/README|secret management]]
