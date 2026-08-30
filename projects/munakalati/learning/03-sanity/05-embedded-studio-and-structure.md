# Sanity — The Embedded Studio and Structure Builder

**Split from:** the munakalati Sanity domain. **See also:** [[projects/munakalati/learning/03-sanity/01-setup-and-mental-model|01 — setup]] · [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]]

---

## One repo, two applications

The Studio is a full React SPA. Munakalati serves it from inside the Next.js app at `/studio` rather than deploying it separately to `*.sanity.studio`:

```tsx
// src/app/studio/[[...tool]]/page.tsx
'use client'

import dynamic from 'next/dynamic'
import config from '../../../../sanity.config'

const NextStudio = dynamic(
  () => import('next-sanity/studio').then((mod) => mod.NextStudio),
  { ssr: false }
)

export default function StudioPage() {
  return <NextStudio config={config} />
}
```

Four separate decisions are packed into those ten lines, and each is doing real work.

**`[[...tool]]` — an optional catch-all route.** One bracket pair `[slug]` is one segment; `[...slug]` is one or more; **`[[...slug]]` is zero or more**. The Studio is a client-side-routed SPA that owns every path under `/studio` — `/studio`, `/studio/structure`, `/studio/desk/post;abc123`, `/studio/vision`. The optional catch-all hands all of them, including the bare `/studio`, to this one page and lets the Studio's own router take over. A plain `[...tool]` would 404 on `/studio` itself.

**`'use client'` — the Studio cannot be server-rendered.** It's a stateful editor that talks to `window`, `localStorage`, and a realtime connection. Note the direction of the constraint: this is *not* "Next.js is client-first". Everything under `(site)/` is a Server Component; this one route opts out because its content genuinely is an interactive application.

**`dynamic(..., { ssr: false })` — belt and braces, and the important one.** `'use client'` alone still means Next pre-renders the component to HTML on the server at build time. The Studio would throw on any `window` access during that pass. `ssr: false` says "never render this on the server, not even at build" — the component is loaded only in the browser.

**And it keeps the Studio out of the site's bundle.** `dynamic()` puts `next-sanity/studio` in its own chunk, fetched only when someone visits `/studio`. The Studio is a *large* dependency; a visitor reading a blog post never downloads a byte of it. **This is the pattern for any heavy, route-specific, browser-only dependency** — an editor, a charting library, a 3D canvas.

### Why embed at all?

**For:** one deploy, one domain, one set of env vars, no CORS configuration, and the Studio is available anywhere the site is. For a small team that's a real simplification.

**Against:** the Studio's build is now coupled to the site's — a Next upgrade can break the CMS, and vice versa. A broken site deploy takes the editing UI down with it, exactly when someone might want to fix content. And `/studio` is a public route: it's protected by Sanity's own login, but its existence is discoverable.

For munakalati — one small site, two or three editors — embedding is clearly right. For something where content editors must keep working through a frontend incident, separate deploys are the safer shape.

### `sanity.cli.ts` — the third consumer of the same config

```ts
export default defineCliConfig({ api: { projectId, dataset } })
```

Small file, easy to skip, and it's what lets `sanity dataset export production` or `sanity documents query '...'` run in this directory without flags. **Three things now read the same project/dataset pair** — the website client, the Studio config, and the CLI — which is precisely why `src/sanity/env.ts` centralises them instead of each reading `process.env` itself.

Note it reads `process.env` directly rather than importing `env.ts`, and so has no `assertValue` guard — the CLI just fails with a less helpful message. Minor, but it's the one place the centralisation leaks.

## Structure Builder — designing the editor's sidebar

By default the Studio lists every document type alphabetically. `src/sanity/structure.ts` overrides that:

```ts
export const structure: StructureResolver = (S) =>
  S.list()
    .title("Content")
    .items([
      S.listItem()
        .title("Hero Content")
        .id("heroContent")
        .child(S.document().schemaType("heroContent").documentId("heroContent")),
      S.listItem()
        .title("Video Overview")
        .id("videoOverview")
        .child(S.document().schemaType("videoOverview").documentId("videoOverview")),
      S.divider(),
      ...S.documentTypeListItems().filter(
        (item) => !["heroContent", "videoOverview"].includes(item.getId() ?? "")
      ),
    ]);
```

Read it as three moves:

1. **Two singletons pinned at the top**, each linking *directly to one known document ID* — clicking "Hero Content" opens the editor for that exact document, skipping the pointless list-of-one.
2. **`S.divider()`** — a visual separator. Trivial, and it's what makes the sidebar read as "the two special things, then everything else".
3. **`...S.documentTypeListItems().filter(...)`** — take the default list of all types, **remove the two already pinned**, and spread the rest back in.

**That filter is the load-bearing line.** Without it the singletons appear twice — once as a pinned document, once as a normal type list where an editor could hit "＋ Create" and make a second hero. It doesn't *prevent* creation (the API still would), but it removes the path a human would take. Combined with the query pinning `_id == "heroContent"`, that's the full singleton story from [[projects/munakalati/learning/03-sanity/02-schema-design|02]] — no single mechanism enforces it; three cooperating conventions do.

**`.id()` must be unique among siblings** and is unrelated to the document ID — it just happens to match here. Duplicate list-item IDs are a runtime Studio error, and a confusing one.

### What Structure Builder is really for

This file is small because the site is small, but the tool scales to genuinely reshaping the editing experience:

- **Filtered lists** — `S.documentTypeList("post").filter('_type == "post" && featured == true')` for a "Featured posts" view.
- **Grouping** — nesting all the About-page types (`teamMember`, `boardMember`, `ambassador`, `timeline`) under one "About page" folder, which for this site would be a real usability win: an editor currently sees sixteen flat types with no indication of which page each one feeds.
- **Per-type views** — attaching a live preview pane next to the form.

**The principle worth carrying:** the Studio's default is a *developer's* view of the content model — one entry per type, alphabetical. An editor thinks in **pages and tasks**, not document types. Structure Builder is where you translate between the two, and it's cheap to do. Sixteen alphabetical types is exactly the point where it starts being worth it.

## The Vision plugin

```ts
plugins: [
  structureTool({ structure }),
  visionTool({ defaultApiVersion: apiVersion }),
],
```

`visionTool` adds a **GROQ playground inside the Studio** at `/studio/vision` — write a query, bind parameters, see JSON. This is the right place to develop every query in `queries.ts`: iterate against real production data with instant feedback, then paste the finished query into the file. Far faster than editing a Next.js page and reloading.

Passing `defaultApiVersion: apiVersion` matters more than it looks — it makes the playground use **the same date-pinned API version as the app**, so a query that works in Vision works in the site. Leave it off and you can debug against different semantics than you ship.

**It ships to production**, gated behind Studio login. That's the standard setup, and the thing to be aware of: anyone who can log into the Studio can run arbitrary GROQ against the dataset. For a two-editor marketing site that's a non-issue; where the dataset holds anything sensitive, it's a real consideration.

## Related
- [[projects/munakalati/learning/04-frontend/01-app-router-structure|frontend/01 — route groups and the rest of the routing]]
- [[frontend/frameworks/next/README|Next.js]] — `dynamic`, catch-all routes
- [[frontend/07-practices/02-performance|performance]] — why the Studio chunk must stay out of the site bundle
