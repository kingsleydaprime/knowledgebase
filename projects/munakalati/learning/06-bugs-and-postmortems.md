# Bugs and Postmortems

**Real failures from [[projects/munakalati/learning/README|munakalati]], written up properly** — what broke, why, how it was found, what the actual fix was, and what generalises.

This is the file to reread before an interview. **A candidate who can narrate a real bug end to end is rarer and more convincing than one who can recite definitions.**

---

## 1. The slug encoding saga — three commits to get one thing right

**Symptom:** blog posts with non-English titles 404'd. A French post's URL looked like `/blog/l%C3%A9ducation-des-enfants` in the address bar instead of `/blog/léducation-des-enfants`, and clicking it produced "not found" even though the post was visibly in Sanity.

### The chain

Wix stores the slug for a non-ASCII title **already percent-encoded**: `l%C3%A9ducation-des-enfants`. The migration copied it verbatim, so Sanity's `slug.current` contained the *encoded* string as literal text.

Then the request path:

1. Browser requests `/blog/l%C3%A9ducation-des-enfants` — every non-ASCII byte in a URL must be percent-encoded on the wire, so this is normal and correct.
2. **Next.js decodes the route param**, handing the page `params.slug === "léducation-des-enfants"`.
3. The query asks Sanity for `slug.current == "léducation-des-enfants"`.
4. Sanity holds the literal string `"l%C3%A9ducation-des-enfants"`.
5. No match. `notFound()`.

**Two layers each doing the right thing individually, disagreeing about what the value *is*.** Next decodes because a decoded param is what application code wants. Wix encoded because a URL-safe slug is what a URL wants. Neither is wrong; nobody owns the seam.

### Fix attempt 1 — try both, encoded second

```tsx
// Next.js URL-decodes route params, but slugs migrated from Wix may be stored
// percent-encoded. Try the decoded form first, fall back to the encoded form.
let post: Post = await client.fetch(postBySlugQuery, { slug });
if (!post) {
  post = await client.fetch(postBySlugQuery, { slug: encodeURIComponent(slug) });
}
```

Worked, and was wrong in an important way. `encodeURIComponent` encodes `/` as `%2F` — fine here since a slug is one segment — but the deeper problem is that it **enshrined the bad data**. The database now permanently holds a value nobody wants: the Studio shows `l%C3%A9ducation...` as the slug, an editor copying it gets a double-encoded URL, and every future consumer of that field has to know the quirk. **Every read path pays forever for a write path that was wrong once.**

### Fix attempt 2 — fix the data, normalise the read (`50e4791`, `f2b69dc`)

Three coordinated changes:

**Fix the source, so new imports are clean** — in `migration.js`:

```js
slug: { _type: "slug", current: decodeURIComponent(listing.slug) },
```

**Fix the existing data** — `fix-slugs.js`, whose entire detection logic is *if decoding changes it, it was encoded*:

```js
const toFix = posts.filter((p) => {
  try { return decodeURIComponent(p.slug) !== p.slug; } catch { return false; }
});
// …then: await sanity.patch(post._id).set({ slug: { _type: "slug", current: decoded } }).commit();
```

**Normalise the read, in the safe direction:**

```tsx
// Normalize the slug: always query with the decoded form since slugs are
// stored decoded in Sanity. Next.js may pass the segment still percent-encoded
// depending on the server context.
let decoded: string;
try { decoded = decodeURIComponent(slug); } catch { decoded = slug; }

let post: Post = await client.fetch(postBySlugQuery, { slug: decoded });
if (!post && decoded !== slug) {
  post = await client.fetch(postBySlugQuery, { slug });
}
```

### Why the second version is genuinely better, not just different

- **The canonical form is now decoded, everywhere.** Storage, queries and the Studio agree.
- **`decodeURIComponent` is idempotent for already-decoded strings** — `decodeURIComponent("hello") === "hello"`. So normalising on read is safe whichever form arrives. `encodeURIComponent` is *not* idempotent (`%C3%A9` → `%25C3%25A9`), which is exactly why normalising towards *decoded* is the correct direction and normalising towards encoded would have been a trap.
- **`try/catch` around the decode.** `decodeURIComponent("%zz")` throws `URIError`. Uncaught in a Server Component, that's a 500 on a malformed URL — trivially triggerable by anyone typing a stray `%`. The catch turns it into a normal 404.
- **The fallback is guarded by `decoded !== slug`** so the identical query never runs twice.

### What generalises

**Normalise at the boundary, and pick the direction that's idempotent.** When two systems disagree about a value's representation, don't teach every consumer both forms — convert once at the edge, store one canonical form, and choose the direction where applying the conversion twice is harmless.

**A `try/catch` around every decode of user-supplied input.** `decodeURIComponent`, `JSON.parse` and `new URL()` all throw on malformed input, and all three routinely sit on a path reachable by an arbitrary string from the internet.

**Fixing the read without fixing the data is a loan.** Attempt 1 shipped in minutes and would have been paid for indefinitely. Two commits later there is a permanent fix, a repair script, and a comment explaining the invariant.

**Related:** [[projects/munakalati/learning/05-migration/05-repair-scripts|migration/05]] · [[foundations/networking/README|networking]] (percent-encoding is RFC 3986)

---

## 2. The `/resources` 404 cascade — hiding a route doesn't find its links

**Symptom:** several CTAs across the site led to a 404 — "Browse Toolkits", "Media Library", "Publications", "Browse All Issues".

**Cause:** commit `42f3e19` renamed `(site)/resources/` to `(site)/_resources/` to cut the section from the MVP. The underscore prefix makes Next skip the folder entirely, so `/resources/toolkits` stopped existing. **Six `<Link href="/resources/...">` elsewhere in the codebase were not updated**, because nothing forces them to be.

The commit updated `Navbar.tsx` — the *obvious* place — and stopped there. Two days later, `3442c85` fixed the rest.

**And it wasn't only the Resources links.** The same commit fixed a second, unrelated class of broken link, which is the interesting part:

```diff
-              href="/donate"
+              href="/engage/donate"
-              href="/engage#partner"
+              href="/engage/partner"
```

Those are wrong from an **earlier** restructure — pages moved under `/engage/` at some point and a handful of links kept pointing at where they used to be. They had presumably been broken for weeks. Nobody noticed, because **a broken internal link produces no error anywhere**: no build failure, no console warning, no exception. It fails only in a human's browser, only if that human clicks it.

The fixes for the resources links are also worth reading, because they aren't uniform — each was redirected to *the most sensible surviving page*, not mechanically to the homepage:

```diff
-  { label: "Media Library", href: "/resources/media-library" },
+  { label: "Media Library", href: "/blog" },
-  { label: "Publications",  href: "/resources/publications" },
+  { label: "Publications",  href: "/our-work/magazine" },
```

That's the right instinct — a user clicking "Publications" wants publications, and the magazine page is the closest thing that exists. Redirecting everything to `/` would have been faster and worse.

### What generalises

**`href` is an untyped string, and it's the largest unchecked surface in a Next.js app.** TypeScript verifies nothing about it. Next 16's `typedRoutes` fixes exactly this — it generates a union type of valid routes so `href="/resources/toolkits"` becomes a **compile error** the moment the folder is renamed. This project doesn't enable it, and it's the single highest-value config change available to it:

```ts
// next.config.ts
const nextConfig: NextConfig = { typedRoutes: true, /* … */ };
```

**Grep before you rename, and grep after.** One command would have caught all six:

```bash
grep -rn 'href="/resources' src --include='*.tsx'
```

**A link checker in CI** catches the residue that typing can't (external links, links built by string concatenation). For a content site where broken links are the main user-visible defect class, it's worth more than most unit tests.

**Related:** [[projects/munakalati/learning/04-frontend/01-app-router-structure|frontend/01]]

---

## 3. The 868-post duplication

**Symptom:** every blog post appeared twice.

**Cause:** `wix-blog-migrate.js` (v1) wrote `_id: post.id` — the raw Wix UUID. The rewritten `migration.js` (v2) writes `_id: "wix-" + id`. Both had been run. Since `createOrReplace` keys on `_id`, and the two scripts generated *different* IDs for the same source post, v2 created a second copy of all 434 rather than replacing the first.

**Fix:** `dedup.js` — group by slug, keep the `wix-` prefixed document, delete the rest.

```js
const keeper = group.find((p) => p._id.startsWith("wix-")) ?? group[0];
```

### What generalises

**A deterministic ID scheme is a contract with your own future re-runs.** Idempotency is a property of *(ID scheme, write verb)* as a pair — `createOrReplace` alone guarantees nothing if the ID changes between runs. Changing the ID format mid-migration is changing a primary key, and the reconciliation is part of that change, not a surprise afterwards.

**The prefix was the right call and should have been there from commit one.** It gives provenance (`_id match "wix-*"` finds every migrated post), scoping for destructive queries, and collision safety. Cheap at the start, expensive to add later.

**Related:** [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|migration/01]] · [[projects/munakalati/learning/05-migration/05-repair-scripts|migration/05]]

---

## 4. The silent pagination bug — one page of 434 posts

**Symptom:** none. That is the entire point of this one.

**Cause:** v1's `fetchAllPosts` assumed cursor pagination:

```js
let cursor = null;
do {
  // …fetch…
  cursor = data.meta?.nextCursor;
} while (cursor);
```

The Wix list endpoint returns `metaData.count` / `metaData.offset` / `metaData.total` — **offset pagination, no cursor**. `data.meta?.nextCursor` is `undefined`, the loop ends after one iteration, and the script reports success having fetched the first page.

**Fix:** v2 reads the real fields, with three independent safety nets — `total = Infinity` initially, `?? page.length` if `metaData` is missing, and `if (page.length === 0) break` regardless of the arithmetic.

### What generalises

**A bug that under-fetches is invisible.** No exception, no warning, a clean report — just less data than there should be. The class includes truncated pagination, a `LIMIT` left in from development, a filter that's too narrow, an API silently capping page size below what you asked for.

**The only defence is reconciliation.** After any bulk extract, assert the count against the source's own reported total *before transforming anything*:

```js
if (posts.length !== reportedTotal)
  throw new Error(`Fetched ${posts.length} of ${reportedTotal} — refusing to continue`);
```

Three lines, and it converts an invisible failure into a loud one.

**`?.` is not free.** Optional chaining on a field name you *assumed* exists turns a would-be `TypeError` — which would have pointed straight at the problem — into `undefined` flowing quietly onward. It's the right tool for genuinely optional fields, and a silencer on fields you believe are mandatory.

**Related:** [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|migration/02]]

---

## 5. `fetch` doesn't throw on 401 — and neither did the script

**Symptom:** the migration ran, printed no errors, and imported nothing.

**Cause:** v1 never checked `res.ok`:

```js
const res = await fetch(url, { headers });
const data = await res.json();      // parses the *error* body quite happily
posts = posts.concat(data.posts || []);   // undefined → [] → silence
```

**`fetch` rejects only on network failure.** A 401 resolves normally with `res.ok === false`, `res.status === 401`, and a JSON body like `{"message": "..."}`. `data.posts` is `undefined`, `|| []` swallows it.

**Fix:**

```js
if (!res.ok) {
  const body = await res.text();
  throw new Error(`List posts failed (${res.status}): ${body}`);
}
```

**Including the response body is what actually solved a downstream problem**, not just improved the message. Reading the real 401 text is what revealed that the `RICH_CONTENT` fieldset needs elevated permissions for some posts — which led directly to the graceful-degradation loop that let 434 posts import with metadata even when their bodies were forbidden.

### What generalises

**Know your HTTP client's error semantics.** `fetch` resolves on 4xx/5xx; `axios` rejects by default; Python's `requests` needs `raise_for_status()`. Getting this wrong produces silent data loss, not a crash.

**Put the response body in the error.** `Wix 401` is a dead end. `Wix 401: {"message":"RICH_CONTENT fieldset requires elevated permissions"}` is a fix.

**Related:** [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|migration/02]]

---

## 6. `generateStaticParams` silently capping at 20

**Symptom:** none visible. 414 of 434 blog posts were rendered on demand instead of pre-rendered — slower first hit for each, and more Sanity traffic, but every page still worked.

**Cause:** `generateStaticParams` reused `allPostsQuery`, which is `[0...20]` and selects every field, because it was written for the blog listing page where 20 recent posts is exactly right.

**Fix (`f2b69dc`):** a purpose-built query.

```groq
// Used only for generateStaticParams — fetches every slug with no limit.
*[_type == "post" && defined(slug.current)]{ "slug": slug.current }
```

### What generalises

**A query written for one purpose is usually wrong for another**, and the failure is silent because the limit that was correct in context is invisible at the new call site. Naming helps — `recentPostsQuery` would not have been reused this way; `allPostsQuery`, which was capped at 20, actively invited it. **A name that lies is worse than no name.**

**Build-time code deserves the same scrutiny as request-time code.** Nobody watches the build for correctness or performance, which is why a 20× over-fetch and a 95% coverage gap sat there unnoticed.

**Related:** [[projects/munakalati/learning/03-sanity/03-groq-queries|sanity/03]] · [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|frontend/02]]

---

## Standing issues — known, not yet fixed

Not postmortems; open items, honestly listed. Anyone picking this project up should start here.

| Issue | Impact | Where |
|---|---|---|
| **`src/migration.js`, `src/backfill-images.js`, `src/docs.md` are gitignored** | The main migration tooling exists on one machine. A fresh clone has `package.json` scripts pointing at missing files | [[projects/munakalati/learning/01-git|01 — git]] |
| **Featured post appears twice on `/blog` page 1** | `featuredId: ""` never matches, so `_id != $featuredId` excludes nothing | [[projects/munakalati/learning/03-sanity/03-groq-queries|sanity/03]] |
| **Every migrated hyperlink is plain text** | `wixMarks()` maps BOLD/ITALIC/UNDERLINE and drops LINK. 434 posts affected | [[projects/munakalati/learning/05-migration/04-portable-text-conversion|migration/04]] |
| **All 434 posts are `category: "news"`** | The blog's category filter is effectively useless | [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|migration/01]] |
| **433 backfilled cover images have no alt text** | Accessibility debt | [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|sanity/04]] |
| **Nine components exist in duplicate** (`home/X.tsx` and `home/cms/X.tsx`) | Dead code that looks live; edits to the wrong copy do nothing | [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|frontend/03]] |
| **CMS fallbacks fire silently** | A broken GROQ query renders hardcoded content with no error | [[projects/munakalati/learning/04-frontend/03-rendering-cms-content|frontend/03]] |
| **`--retry` synthesises a stub listing** | Retried posts get their Wix UUID as their slug | [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|migration/03]] |
| **Hand-written types drift from the schema** | `localPhoto` is declared and doesn't exist; projections are typed as full documents | [[projects/munakalati/learning/03-sanity/02-schema-design|sanity/02]] |
| **No CI, no tests, no pre-commit hooks** | Nothing catches any of the above automatically | — |

## The pattern across all six

Five of the six were **silent**. No exception, no failing build, no red console — just wrong output that looked like right output. That's not coincidence; it's what bugs in data-pipeline and content code *are*:

- a decoded/encoded mismatch → a 404 that looks like missing content
- a renamed route → a link that just doesn't work
- a changed ID scheme → duplicates that look like a content problem
- a missing cursor field → a smaller dataset that looks like a smaller dataset
- an unchecked status code → an empty import that reports success
- a reused query → a slower page that still renders

**The defences are correspondingly unglamorous**, and every one of them is cheap: check the status code, reconcile the count, type the routes, assert before you write, log when a fallback fires. **Not one of these bugs needed a debugger. All of them needed something to have been asserted earlier.**

## Related
- [[projects/munakalati/interview/04-bugs-and-story|interview: bugs and story]] — these, as questions
- [[concepts/04-best-practices/06-data-migrations|data migrations]]
- [[problem-solving/thinking-patterns|thinking patterns]]
