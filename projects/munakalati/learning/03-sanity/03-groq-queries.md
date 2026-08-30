# GROQ — Querying Sanity

**Split from:** the munakalati Sanity domain. **See also:** [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]] · [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|frontend/02 — data fetching]]
**General version:** [[frontend/frameworks/sanity/02-groq|frontend/frameworks/sanity/02 — GROQ]]

---

## Reading GROQ: three parts, always in the same order

GROQ (Graph-Relational Object Queries) looks alien for about ten minutes and then becomes obvious, because **every query is the same three parts**:

```groq
*[ filter ] | order(...) [slice] { projection }
```

Take the real one from `src/sanity/lib/queries.ts`:

```groq
*[_type == "post" && defined(publishedAt) && publishedAt <= now()]
  | order(publishedAt desc)
  [0...20]
  {
    _id, title, slug, excerpt, category, publishedAt, featured,
    coverImage { asset, alt },
    author-> { name, photo, role }
  }
```

1. **`*`** means "every document in the dataset". Everything starts here — there are no tables to pick from, one flat pool of documents.
2. **`[...]`** filters it. `_type == "post"` is the closest thing to a `FROM` clause and it's just a predicate on a field.
3. **`| order(...)`** and **`[0...20]`** sort and slice. Note `[0...20]` is a **range** (three dots, end-exclusive) and it's positional — a second `[...]` after a filter means slice, not filter.
4. **`{ ... }`** is the **projection**: what to return. **This is the part that matters most for performance and correctness**, and the part SQL people underuse.

**The mental translation from SQL:**

| SQL | GROQ |
|---|---|
| `SELECT a, b` | the trailing `{ a, b }` |
| `FROM posts` | `*[_type == "post"]` |
| `WHERE x = $y` | the same `[...]`, ANDed |
| `ORDER BY d DESC` | `| order(d desc)` |
| `LIMIT 20` | `[0...20]` |
| `JOIN authors ON ...` | `author->` |
| `COUNT(*)` | `count(*[...])` |

**The big difference: the projection is a shape, not a list.** `coverImage { asset, alt }` returns a *nested object* with only those two keys. You are describing the JSON you want back, and it can nest arbitrarily. There is no join table, no result flattening, and no second query.

## `->` is the whole join story

```groq
author-> { name, photo, role }
```

`post.author` is stored as `{_type: "reference", _ref: "author-muna-kalati"}`. The `->` **follows the reference and inlines the target document**, then the `{...}` projects fields off it. One arrow, no join syntax, no N+1.

It composes: `author->photo.asset->url` would follow the author reference, then the image asset reference, and return a single string. **Every arrow is a hop, and hops are cheap because they run server-side in one request** — which is precisely the thing a hand-rolled REST client can't do without either over-fetching or making a second round trip.

**Field-level shorthand vs. projection:** `author-> { name }` gives `{author: {name: "..."}}`, while `"authorName": author->name` gives `{authorName: "..."}`. The second form — a quoted key with an expression — is how you rename or compute:

```groq
*[_type == "post" && defined(slug.current)]{ "slug": slug.current }
```

That's `allSlugQuery`, and the `"slug": slug.current` **flattens `{slug: {current: "x"}}` down to `{slug: "x"}`** so the caller gets exactly the shape `generateStaticParams` wants.

## Parameters — and why `$` is not string interpolation

```groq
export const postBySlugQuery = groq`
  *[_type == "post" && slug.current == $slug][0] { ... }
`;
```

```ts
const post = await client.fetch(postBySlugQuery, { slug: decoded });
```

`$slug` is a **bound parameter**, sent alongside the query and never spliced into its text. Same protection as a prepared statement in SQL: a slug containing `"] || *[_type == "user"` is data, not syntax. **Never build a GROQ string with template interpolation of user input** — GROQ injection is a real class of bug, and it's especially tempting here because the queries are already inside JS template literals.

The `groq` tag itself does nothing at runtime — it returns the string unchanged. Its value is tooling: editor syntax highlighting, and **Sanity TypeGen finds queries by looking for this tag**. Free to add, and it's the prerequisite for generated types (see [[projects/munakalati/learning/03-sanity/02-schema-design|02 — schema design]] on the type drift it would have prevented).

## `[0]` — the difference between a document and a list

```groq
*[_type == "post" && slug.current == $slug][0] { ... }   // → an object, or null
*[_type == "post" && category == $category] { ... }      // → an array, possibly empty
```

**Always `[0]` when you want one thing**, and then null-check. Without it you get a one-element array, `post.title` is `undefined`, and the page renders blanks instead of hitting your `notFound()`. The blog detail page gets this right:

```ts
let post: Post = await client.fetch(postBySlugQuery, { slug: decoded });
if (!post) notFound();
```

## Conditional filters without building the query string

This is the cleverest query in the file, and the pattern is worth stealing:

```groq
export const pagedPostsQuery = groq`
  *[_type == "post"
     && defined(publishedAt) && publishedAt <= now()
     && ($category == "all" || category == $category)
     && _id != $featuredId]
  | order(publishedAt desc) [$start...$end] { ... }
`;
```

**`($category == "all" || category == $category)`** — one static query serving both "all posts" and "posts in one category". When the caller passes `"all"`, the left side is true and the clause short-circuits to a no-op; otherwise it filters. The alternative — concatenating a `&& category == "..."` fragment when a category is present — means the query text varies per request, which kills query-plan reuse *and* reintroduces the injection surface parameters just removed.

**`[$start...$end]`** proves slices take parameters too, which is what makes real pagination possible.

**One live bug in how it's called.** `src/app/(site)/blog/page.tsx` passes `featuredId: ""`:

```ts
client.fetch(pagedPostsQuery, { category, featuredId: "", start, end }),
```

The `_id != $featuredId` clause was clearly meant to keep the featured post from appearing twice — once in the featured hero, once in the grid below. Passing `""` matches no document, so the exclusion never happens and **the featured post also shows up in the grid on page 1**. Fixing it is one line (`featuredId: featured?._id ?? ""`), but the featured post is fetched in the same `Promise.all` as the paged list, so it isn't available yet — the fetches would have to be sequenced, or the filtering done in JS after both resolve. A good small example of **a parallel-fetch optimisation quietly breaking a data dependency**.

## `count()` and the two-query pagination shape

```groq
export const postCountQuery = groq`
  count(*[_type == "post" && defined(publishedAt) && publishedAt <= now()
          && ($category == "all" || category == $category)])
`;
```

Pagination needs two things — the page, and the total — and GROQ has no `SELECT ... OVER()`. So: two queries, fired together.

```ts
const [featured, posts, total] = await Promise.all([
  client.fetch(featuredPostQuery),
  client.fetch(pagedPostsQuery, { category, featuredId: "", start, end }),
  client.fetch(postCountQuery, { category }),
]);
```

**`Promise.all` here is the whole performance story of the page.** Three sequential awaits would be three round trips to Sanity stacked end to end before the page can render; in parallel it's one round trip's worth of latency. This is the single highest-value habit in server-component data fetching → [[frontend/04-state-and-data/02-data-fetching-and-server-state|the general note on fetch waterfalls]].

**The duplication trap it creates:** the filter is now written twice — once in `pagedPostsQuery`, once inside `count()` in `postCountQuery` — and they must stay identical or the page count won't match the pages. They *are* identical here (minus the `_id != $featuredId`, which is itself the bug above). It's a real maintenance hazard: change one, get a phantom empty last page.

## `defined()`, `now()`, and defending against your own data

```groq
*[_type == "post" && defined(publishedAt) && publishedAt <= now()]
```

- **`defined(x)`** — "the field exists and isn't null". Necessary because, as covered in [[projects/munakalati/learning/03-sanity/02-schema-design|02]], `required()` is a Studio form check and migrated documents never passed through the Studio. 434 imported posts is exactly the situation where a `defined()` guard earns its keep.
- **`now()`** — server-side current time, so `publishedAt <= now()` is **scheduled publishing for free**: set a future date and the post is invisible until it isn't. No cron, no publish job. Worth appreciating — it's a genuinely elegant use of a filter.
- **The catch:** combined with ISR (`revalidate = 60`), a scheduled post appears up to 60 seconds late. Fine here; would not be fine for an embargoed press release.

## Two queries that are dead, and why that's a finding

`postsByCategoryQuery` and `allPostsQuery` are both exported from `queries.ts` and **neither is referenced anywhere in `src/`** — `allPostsQuery` was orphaned by commit `f2b69dc`, which swapped `generateStaticParams` over to the lighter `allSlugQuery`.

That swap is itself the good bit. The old version fetched **twenty full post documents — body, images, author, everything — in order to read twenty slugs**, and it was capped at `[0...20]`, so with 434 posts **only the 20 most recent were ever statically generated.** The replacement:

```groq
// Used only for generateStaticParams — fetches every slug with no limit.
export const allSlugQuery = groq`
  *[_type == "post" && defined(slug.current)]{ "slug": slug.current }
`;
```

Two fixes in three lines: no cap, and a projection of exactly one string per document. **The projection is the optimisation** — the same filter, but returning ~40 bytes per post instead of several kilobytes. When a GROQ query feels slow, look at the `{...}` before you look at the `[...]`.

Finding the dead ones is a one-liner, and worth running before any refactor:

```bash
# for each exported query name, count references outside queries.ts itself
grep -oP 'export const \K\w+(?=Query)' src/sanity/lib/queries.ts \
  | while read q; do echo "$(grep -rl "${q}Query" src --include='*.tsx' --include='*.ts' | grep -vc queries.ts) ${q}Query"; done \
  | sort -n
```

`grep -o` prints only the matched part rather than the whole line, and `\K` drops everything before it from the match — so you get bare query names, one per line, ready to loop over. See [[projects/munakalati/learning/02-shell|02 — shell]].

## Related
- [[projects/munakalati/learning/04-frontend/02-data-fetching-and-caching|frontend/02 — where these queries get called]]
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — bugs and postmortems]] — the slug-matching saga
- [[databases/sql-reference|SQL reference]] — the language this is deliberately not
- [[cybersecurity/04-web-security/README|web security]] — why `$params` and not interpolation
