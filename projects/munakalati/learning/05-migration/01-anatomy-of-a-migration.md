# Anatomy of a Content Migration

**Split from:** the munakalati migration domain. **See also:** [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|02 — the Wix API]] · [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|03 — idempotency and reruns]] · [[projects/munakalati/learning/05-migration/05-repair-scripts|05 — repair scripts]]
**General version:** [[concepts/04-best-practices/06-data-migrations|concepts/04 — data migrations]]

---

## What actually happened

Muna Kalati's blog lived on Wix. The new site is Next.js + Sanity. **434 posts had to move**, with their images, their formatting, their publication dates and their URLs — because the URLs were already indexed and linked from elsewhere.

Final state, from the run reports checked into the working tree:

```json
// migration-report.json          // backfill-report.json
{ "total": 434,                   { "total": 433,
  "skipped": 208,                   "patched": 418,
  "failedCount": 0,                 "failed": [] }
  "failed": [] }
```

**Zero failures — on the last run.** That framing matters, and it's the first real lesson: the reports record the state of the *final* pass, after several earlier passes that failed in interesting ways, produced duplicates, and had to be repaired by three separate scripts. A clean report is the *output* of the process, not evidence the process was clean.

## The shape every content migration has

Five phases. Munakalati has a script per phase, which is not an accident — **the phases have genuinely different failure modes and genuinely different rerun semantics**, and merging them produces something you can't safely re-run.

| Phase | Here | The question it answers |
|---|---|---|
| **1. Extract** | `fetchAllPosts()` / `fetchPost()` | Can I get all the source data out, reliably and completely? |
| **2. Transform** | `toPortableText()`, `buildDoc()` | What does a source record become in the target model? |
| **3. Load** | `createOrReplace()`, `assets.upload()` | Can I write it, idempotently? |
| **4. Verify** | `migration-report.json`, GROQ spot checks | Did everything land, and is it right? |
| **5. Repair** | `dedup.js`, `fix-slugs.js`, `backfill-images.js` | Fix what phase 4 found, without re-running everything |

**Phase 5 is the one people don't plan for and always need.** It is not a sign the migration was done badly. Source data is inconsistent in ways you cannot know until you've pulled all of it — here: posts whose rich content 401s, images stored under an internal `wix:image://` scheme, slugs percent-encoded for non-English titles. You discover these at scale, after loading, and you fix them with small targeted scripts rather than by re-running the whole import.

## The mapping is the design work

Before any code, the real task is a table — source field to target field, and what to do when it doesn't fit:

| Wix | Sanity | The decision |
|---|---|---|
| `id` (UUID) | `_id: "wix-" + id` | **Prefix it.** See below — this is the most consequential line in the script |
| `title` | `title` | direct |
| `slug` | `slug.current`, `decodeURIComponent`'d | Source stores it percent-encoded; the frontend needs it decoded |
| `excerpt` | `excerpt`, `.slice(0, 200)` | Target schema validates `max(200)`; source has no limit |
| `firstPublishedDate` | `publishedAt` | Falls back to `lastPublishedDate`, then `null` |
| `content.nodes[]` | `body` (Portable Text) | The hard one → [[projects/munakalati/learning/05-migration/04-portable-text-conversion\|note 04]] |
| `media.wixMedia.image` | `coverImage` | Three fallback sources → [[projects/munakalati/learning/05-migration/02-reading-the-wix-api\|note 02]] |
| `categoryIds[]` (UUIDs) | `category: "news"` | **Punted.** See below |
| `memberId` | `author` → one default author | **Punted.** See below |

**Two fields were deliberately not migrated, and saying so out loud is the point:**

```js
category: "news", // Wix categoryIds are UUIDs — update manually in Studio
author: { _type: "reference", _ref: authorId },  // everything → one "Muna Kalati" author
```

Wix categories are UUID references into a separate collection; mapping them would mean a second extract, a lookup table, and a decision about which Wix categories map onto the seven the new schema defines. Wix authors are `memberId`s into the site's member system, which the API key may not even have access to.

**Both were scoped out in favour of shipping, and both are recorded in a comment at the point of the decision.** That's the correct handling of a punt: it isn't hidden, and the person who later wonders "why is every post categorised as news?" finds the answer on the line that did it. The cost is real and should be stated — 434 posts all sitting in one category makes the blog's category filter close to useless, and it's manual work in the Studio to undo.

**The general rule:** a migration where every field maps cleanly is a migration you didn't look at hard enough. Decide explicitly what you're dropping, write down why, and put the note where the code makes the choice.

## `_id: "wix-" + id` — the ID namespace decision

```js
return {
  _type: "post",
  _id: `wix-${listing.id}`,
  ...
};
```

Setting `_id` explicitly (rather than letting Sanity generate one) is what makes the whole thing re-runnable: `createOrReplace` on a deterministic ID is idempotent, so running the script twice produces one document, not two → [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|note 03]].

The **prefix** buys three separate things:

1. **Provenance.** `wix-c9402bb3-...` announces where the document came from. A year from now, `*[_type == "post" && _id match "wix-*"]` tells you exactly which posts are migrated and which were authored natively — a distinction you will want and cannot reconstruct otherwise.
2. **A safe scope for destructive queries.** `backfill-images.js` filters on `_id match "wix-*"` precisely so it can never touch a hand-written post.
3. **Collision avoidance.** Wix UUIDs and Sanity IDs share a keyspace. Unprefixed, a Wix UUID could in principle collide with an ID generated by something else.

**And the first version didn't do it** — `wix-blog-migrate.js` used `_id: post.id`, the raw UUID. When the rewritten `migration.js` switched to the prefix, every post that had been imported by the old script got imported *again* under a new ID. **434 posts became 868**, and `dedup.js` exists solely to clean that up.

That is the single most instructive failure in this project, and the lesson generalises well beyond Sanity: **an ID scheme is a contract with your own future re-runs.** Changing it mid-migration is equivalent to changing a primary key. Decide the ID format before the first run, and if you must change it, plan the reconciliation as part of the change rather than discovering it afterwards.

## Why there are two migration scripts

`src/wix-blog-migrate.js` (240 lines) is the first attempt; `src/migration.js` (414 lines) is the rewrite that actually ran. Reading them side by side is the best available summary of what a first draft doesn't know yet:

| | `wix-blog-migrate.js` (v1) | `migration.js` (v2) |
|---|---|---|
| **IDs** | `_id: post.id` | `_id: "wix-" + id` |
| **Pagination** | `cursor` / `meta.nextCursor` | `paging.offset` / `metaData.total` — **v1's cursor never existed in the response, so it fetched one page and stopped** |
| **Errors** | `const data = await res.json()` — no status check | `if (!res.ok) throw new Error(...)` with the response body |
| **Auth edge case** | none | retries without `RICH_CONTENT` on 401 |
| **Image URLs** | uses `node.image.url` as-is | `resolveWixUrl()` handles the `wix:image://` scheme |
| **Portable Text** | top-level `PARAGRAPH`/`HEADING`, text joined with `" "` | recurses containers, preserves bold/italic marks, emits `_key`s |
| **Cover image** | first body image only | three sources in priority order |
| **Concurrency** | `p-limit` (a dependency) | 25-line hand-rolled limiter |
| **Reruns** | none — full re-import every time | skip-if-done, `--force`, `--retry` |
| **Client** | imports the app's `client` (`@/sanity/lib/client`) | its own client with a token and `useCdn: false` |

**That last row is a bug, not a preference.** v1 imports the *website's* read client — no token, `useCdn: true`. It could not have written anything; every `createOrReplace` would have been rejected as unauthorised. It also imports via the `@/` alias, which is a Next.js/tsconfig path mapping that a bare `bun run src/wix-blog-migrate.js` does not necessarily resolve. v1 is best read as a sketch that never fully ran.

**The pagination row is the one worth dwelling on.** v1 loops `while (cursor)`, reading `data.meta?.nextCursor` — a field the Wix endpoint does not return. `undefined` ends the loop after one iteration, silently. No error, no warning: it just quietly migrated the first page and reported success. **A pagination bug that under-fetches is invisible unless you check the count**, which is exactly why phase 4 (verify) is a phase and not an afterthought. The general habit: after any bulk extract, assert that what you got matches the source's own reported total *before* you transform anything.

## Related
- [[concepts/04-best-practices/06-data-migrations|the general playbook]] — the framework-agnostic version of this note
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — bugs and postmortems]]
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data and integration patterns]]
