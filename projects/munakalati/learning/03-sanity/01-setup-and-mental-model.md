# Sanity — Setup and the Mental Model

**Domain:** Sanity CMS, as it showed up in [[projects/munakalati/learning/README|munakalati]] (the Muna Kalati / MunaWorld site).
**See also:** [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]] · [[projects/munakalati/learning/03-sanity/03-groq-queries|03 — GROQ]] · [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|04 — images & Portable Text]] · [[projects/munakalati/learning/03-sanity/05-embedded-studio-and-structure|05 — the embedded Studio]]
**General version:** [[frontend/frameworks/sanity/README|frontend/frameworks/sanity/]] · concept-level: [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modeling and headless CMS]]

---

## The one idea

**Sanity is a hosted document database with a schema you write in JavaScript and an editing UI generated from that schema.** It is not a website builder, and — unlike WordPress or Wix — it has no opinion whatsoever about how the content is displayed. You get a queryable JSON store plus an admin app; the rendering is entirely yours.

That single split is what "headless" means, and it's the reason this project has *two* things in one repo:

| | What it is | Where it lives |
|---|---|---|
| **The content backend** | Schema definitions, a hosted dataset, an API | `src/sanity/schemaTypes/`, hosted at `ava7z1hl` / dataset `production` |
| **The editing UI** | The Studio — a React app Sanity generates from your schema | mounted at `/studio` via `src/app/studio/[[...tool]]/page.tsx` |
| **The website** | Next.js, fetching from the API | `src/app/(site)/**` |

**The Studio and the website are two separate apps that happen to be deployed from one Next.js project.** Understanding that stops a lot of confusion — e.g. why `sanity.config.ts` sits at the repo root and starts with `'use client'` while the pages that read the content are Server Components.

## The four coordinates that identify content

Every read or write needs the same four things, and they're centralised in `src/sanity/env.ts`:

```ts
export const apiVersion =
  process.env.NEXT_PUBLIC_SANITY_API_VERSION || '2026-05-07'

export const dataset = assertValue(
  process.env.NEXT_PUBLIC_SANITY_DATASET,
  'Missing environment variable: NEXT_PUBLIC_SANITY_DATASET'
)

export const projectId = assertValue(
  process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  'Missing environment variable: NEXT_PUBLIC_SANITY_PROJECT_ID'
)

function assertValue<T>(v: T | undefined, errorMessage: string): T {
  if (v === undefined) throw new Error(errorMessage)
  return v
}
```

1. **`projectId`** — the Sanity project (`ava7z1hl` here). Public; it's in the URL of every image and every API call.
2. **`dataset`** — a named silo of documents inside the project (`production`). You can have `staging`, `development`, etc. **Datasets are the unit of copying** — `sanity dataset export production` / `import` is how you snapshot or clone content.
3. **`apiVersion`** — a **date**, not a semver. More on this below; it's the single most surprising piece of the setup.
4. **A token** — only for *writes*. Reads of a public dataset need none, which is why `src/sanity/lib/client.ts` has no token at all and the migration scripts do.

### `assertValue` is worth stealing

Note what that helper buys: a missing env var fails **at import time with a named error** rather than producing `undefined` that quietly flows into a URL and 404s three layers deeper. This is the same instinct as [[projects/strictenv/learning|strictenv]] — validate config at the boundary, once, loudly. Cheap to write, and it turns a mystifying runtime bug into a one-line startup error.

The lint here is that `apiVersion` uses `||` with a fallback while the other two assert. That's deliberate — a missing API version has a sane default, a missing project ID does not.

## API versioning by date — the bit that trips everyone

`apiVersion: '2026-05-07'` is **not** "version 2026.5.7 of the client library". It's a **date-pinned contract with Sanity's API**: you are saying *"behave the way you behaved on 7 May 2026."*

Why this design: Sanity changes GROQ semantics and endpoint behaviour over time. If your app just said "latest", a change on their side could silently alter your query results in production. Pinning a date freezes the behaviour. When you want newer features, you bump the date **deliberately**, read the changelog, and test.

**Practical rule:** pick today's date when you start a project, then leave it alone. Every client in this repo uses the same `2026-05-07` — the app client, the migration script, the dedup script, the backfill script — and they should stay in sync, because a query that returns one shape in the app and another in a script is a genuinely nasty bug class.

## Two clients, and why the difference matters

**The app client** — `src/sanity/lib/client.ts`:

```ts
export const client = createClient({
  projectId,
  dataset,
  apiVersion,
  useCdn: true, // Set to false if statically generating pages, using ISR or tag-based revalidation
})
```

**The script client** — e.g. `src/fix-slugs.js`:

```ts
const sanity = createClient({
  projectId: PROJECT_ID,
  dataset: DATASET,
  apiVersion: "2026-05-07",
  token: SANITY_TOKEN,   // ← writes need this
  useCdn: false,         // ← never read a stale cache when you're about to patch
});
```

Two differences, both meaningful:

**`token`.** Reads of a public dataset are unauthenticated. Writes — `create`, `createOrReplace`, `patch`, `delete`, `assets.upload` — need a token with Editor or Admin rights, created at `manage.sanity.io`. The token is a **secret**: note it is `SANITY_API_TOKEN`, with no `NEXT_PUBLIC_` prefix, so Next never inlines it into the client bundle. Anything named `NEXT_PUBLIC_*` is shipped to the browser — that naming convention is a security boundary, not a style choice.

**`useCdn`.** `true` routes reads through `apicdn.sanity.io`, a cache that is fast and cheap but can serve content a few seconds stale. `false` hits the live API. The rule:

- **Reading to display, and a few seconds of staleness is fine** → `useCdn: true`.
- **Reading in order to then write** (dedup finding duplicates, fix-slugs finding encoded slugs, migration checking what's already imported) → **`useCdn: false`, always.** Deciding what to delete based on a stale snapshot is how you delete the wrong document.

There's a live inconsistency in this repo worth knowing about: `client.ts` sets `useCdn: true` while its own comment says *"Set to false if statically generating pages, using ISR or tag-based revalidation"* — and the pages **do** use ISR (`export const revalidate = 60`). In practice it's benign here (the CDN's staleness window is far shorter than the 60s revalidate window, so the ISR cache dominates), but it's the kind of thing that becomes a real "why is my published edit not showing" bug on a shorter revalidate. See [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|frontend/02 — data fetching and caching]].

## `defineLive` — set up, not used

`src/sanity/lib/live.ts` exists and exports `sanityFetch` / `SanityLive`:

```ts
import { defineLive } from "next-sanity/live";
import { client } from './client'

export const { sanityFetch, SanityLive } = defineLive({ client });
```

This is Sanity's **Live Content API** — the pieces for content that updates in the browser without a reload. It requires rendering `<SanityLive />` in a layout and fetching with `sanityFetch` instead of `client.fetch`. **Neither happens in this project**, so the file is dead scaffolding from `create-sanity-app`. Every page uses `client.fetch` plus `revalidate = 60` instead.

Worth being honest about rather than pretending it's wired up: it's a leftover, and if this site ever wants real-time preview it's the file to start from. Recognising generated-but-unused scaffolding in your own repo is a useful habit — the same eye that spots the unused `Navbar`/`Footer` imports in `src/app/layout.tsx`.

## The file layout this project settled on

```
sanity.config.ts              # Studio config — schema, plugins, basePath. Root, 'use client'
sanity.cli.ts                 # so the `sanity` CLI knows the project/dataset
src/sanity/
├── env.ts                    # the four coordinates, validated
├── structure.ts              # Studio sidebar layout (singletons pinned to the top)
├── lib/
│   ├── client.ts             # read client for the website
│   ├── image.ts              # urlFor() image URL builder
│   ├── live.ts               # Live Content API (unused here)
│   ├── queries.ts            # every GROQ query in the app, in one file
│   └── types.ts              # hand-written TS interfaces for query results
└── schemaTypes/              # one file per document type + index.ts barrel
```

**The two decisions in there worth copying:** all GROQ in one `queries.ts` rather than inline in components (you can read the whole content API of the site in one screen, and it makes the *n+1 fetch* pattern visible), and one schema file per type with an `index.ts` barrel (so adding a type is one file plus one line, and `git log` per content type is meaningful).

**The one worth *not* copying:** `types.ts` is hand-written. Sanity ships **TypeGen** (`sanity typegen generate`) which derives types from your schema *and* your GROQ queries, so a query that selects three fields produces a three-field type. Hand-written types drift — and they drifted here (`TeamMember` and `BoardMember` both declare a `localPhoto?: string` field that no schema defines). See [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]] for the full drift list.

## Related
- [[projects/munakalati/learning/README|munakalati learning index]]
- [[frontend/frameworks/sanity/01-the-sanity-model|general: the Sanity model]]
- [[devops/09-secret-management/README|secret management]] — why `NEXT_PUBLIC_` is a boundary
