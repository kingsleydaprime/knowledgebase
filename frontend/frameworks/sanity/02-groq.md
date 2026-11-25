---
id: 5ccbc489-a329-4b09-9bda-5994ba4452a7
---

# GROQ

**Part of [[frontend/frameworks/sanity/index|frameworks/sanity]].** `[reference]`
**Real code:** munakalati — 24 queries against 434 posts · **Compare:** [[databases/sql-reference|SQL reference]]

---

## Every query has the same three parts
<!-- bite: d1ddec60-881e-4b69-9816-f8c55f250741 -->

```groq
*[ filter ] | order(...) [slice] { projection }
```

```groq
*[_type == "post" && defined(publishedAt) && publishedAt <= now()]
  | order(publishedAt desc)
  [0...20]
  { _id, title, slug, excerpt, publishedAt,
    coverImage { asset, alt },
    author-> { name, photo, role } }
```

1. **`*`** — every document in the dataset. There are no tables; one flat pool.
2. **`[...]`** — the filter. `_type == "post"` is the nearest thing to a `FROM`, and it's just a predicate.
3. **`| order()` and `[0...20]`** — sort and slice. The range is **end-exclusive**, three dots. A second `[...]` after a filter is a slice, not another filter.
4. **`{...}`** — the **projection**. What comes back. **This is where performance lives.**

## Translating from SQL
<!-- bite: bde47579-d2fd-412b-958b-53e9f12d9b6e -->

| SQL | GROQ |
|---|---|
| `SELECT a, b` | trailing `{ a, b }` |
| `FROM posts` | `*[_type == "post"]` |
| `WHERE x = $y` | the same `[...]`, ANDed |
| `ORDER BY d DESC` | `\| order(d desc)` |
| `LIMIT 20` | `[0...20]` |
| `OFFSET 40 LIMIT 20` | `[40...60]` |
| `JOIN authors ON …` | `author->` |
| `COUNT(*)` | `count(*[…])` |
| `IS NOT NULL` | `defined(x)` |
| `NOW()` | `now()` |

**The difference that matters: the projection is a shape, not a column list.** `coverImage { asset, alt }` returns a *nested object* with those two keys. You describe the JSON you want back, and it nests arbitrarily. No join tables, no result flattening, no second query.

## `->` is the entire join story
<!-- bite: 972e807b-834d-4f27-b545-a05a7633ec34 -->

```groq
author-> { name, photo, role }
```

A reference field stores `{_type: "reference", _ref: "author-xyz"}`. **`->` follows it and inlines the target document**; the `{...}` then projects fields off it. It chains — `author->photo.asset->url` is two hops returning one string — and **every hop runs server-side in one request**, which is exactly what a hand-rolled REST client can't do without over-fetching or a second round trip.

**Renaming and flattening** uses a quoted key with an expression:

```groq
*[_type == "post" && defined(slug.current)]{ "slug": slug.current }
```

That turns `{slug: {current: "x"}}` into `{slug: "x"}` — the caller gets exactly the shape it wants, and nothing else travels.

## Parameters, not interpolation
<!-- bite: e779eaa8-bc1e-440a-9de0-24621e40083e -->

```groq
*[_type == "post" && slug.current == $slug][0] { … }
```

```ts
client.fetch(query, { slug })
```

**`$slug` is bound, sent alongside the query text, never spliced into it** — the same protection a prepared statement gives in SQL. A value containing `"] || *[_type == "user"` is data, not syntax.

> **Never build a GROQ string by interpolating user input.** It's especially tempting because the queries already live inside JS template literals.

**The `groq` tag** (`` groq`…` ``) does nothing at runtime — it returns the string unchanged. Its value is tooling: editor highlighting, and **TypeGen finds queries by looking for it.** Free to add; the prerequisite for generated types.

## `[0]` — one thing or a list
<!-- bite: c65ba7f0-a8f1-472e-a316-8bd206f758b2 -->

```groq
*[_type == "post" && slug.current == $slug][0] { … }   // → object, or null
*[_type == "post" && category == $category] { … }      // → array, possibly empty
```

**Always `[0]` when you want one**, then null-check. Without it you get a one-element array, every field access is `undefined`, and the page renders blanks instead of a 404.

Note the asymmetry when handling results: a single-document query returns `null` when it misses, but **a list query returns `[]`, never `null`** — and `[] ?? fallback` gives you `[]`, because an empty array is truthy. Use `.length > 0`, not `||`.

## Conditional filters without a dynamic query
<!-- bite: 0b783901-58ed-4f67-ac66-57c615f3f450 -->

```groq
*[_type == "post" && ($category == "all" || category == $category)]
  | order(publishedAt desc) [$start...$end] { … }
```

**One static query serving both "everything" and "one category".** Passing `"all"` makes the left side true and the clause a no-op.

Why this beats concatenating a filter fragment: the query text stays constant (so it's cacheable and plan-reusable), and it doesn't reintroduce the injection surface parameters exist to remove. **Slices take parameters too** — `[$start...$end]` is what makes real pagination possible.

## `count()` and the two-query pagination shape
<!-- bite: 638e8317-cdb8-4c71-b94c-c68fc35b915b -->

GROQ has no window functions, so a paginated list needs the page and the total as separate queries:

```groq
count(*[_type == "post" && ($category == "all" || category == $category)])
```

```ts
const [posts, total] = await Promise.all([
  client.fetch(pagedQuery, { category, start, end }),
  client.fetch(countQuery, { category }),
]);
```

**Fire them together.** Sequential awaits on independent queries is the most common performance bug in server-rendered data fetching, and nothing about the code looks wrong.

**The trap this creates:** the filter is now written twice and must stay identical, or the page count won't match the pages. Change one, get a phantom empty last page.

## One query, many keys
<!-- bite: 39f823d0-afa6-4a34-b40a-0564929c1a20 -->

A top-level object projection runs several queries in one request:

```groq
{
  "hero":         *[_type == "heroContent" && _id == "heroContent"][0]{ … },
  "stats":        *[_type == "stat" && context == "home"] | order(order asc){ … },
  "testimonials": *[_type == "testimonial"] | order(order asc){ … }
}
```

**The answer to a page whose every section fetches its own data.** Colocated per-component fetching is more modular; this is one round trip. Which wins depends entirely on whether the page is cached — under ISR, several fetches per hour is nothing; on a dynamic page it's the whole latency budget.

## `defined()`, `now()` and defending against your own data
<!-- bite: 1686007b-8ac3-4741-b65a-6d2a5517cdc0 -->

- **`defined(x)`** — the field exists and isn't null. **Necessary because `required()` in a schema is a Studio form check**, so anything written by a script or a migration can violate it → [[frontend/frameworks/sanity/01-the-sanity-model|01]].
- **`now()`** — server-side current time. `publishedAt <= now()` is **scheduled publishing for free**: set a future date and the document is invisible until it isn't. No cron, no publish job. The catch is that it composes with your page cache — under a 60-second revalidate, a scheduled post appears up to a minute late.
- **`match`** — wildcard text matching. `_id match "wix-*"` scopes a destructive script to migrated documents only.

## The projection is the optimisation
<!-- bite: fed2f2f7-f1f1-4fe6-8fad-5a9aa4a50dba -->

The highest-value habit in GROQ, and the one people miss because they're used to `SELECT *` being fine:

```groq
// before: fetches 20 complete posts — body, images, author — to read 20 slugs
*[_type == "post" …] | order(publishedAt desc) [0...20] { _id, title, slug, excerpt, body, coverImage{…}, author->{…} }

// after: the same filter, ~40 bytes per document, no cap
*[_type == "post" && defined(slug.current)]{ "slug": slug.current }
```

**When a GROQ query feels slow, look at the `{...}` before you look at the `[...]`.** And beware reusing a query written for another purpose — a `[0...20]` that was correct on a listing page becomes a silent 95% coverage gap when the same query is reused to enumerate every route.

## Finding dead queries
<!-- bite: 6ece7716-0cb8-4e82-91bb-84833582478d -->

Because queries are exported constants, dead ones are findable:

```bash
for q in $(grep -oP 'export const \K\w+Query' src/sanity/lib/queries.ts); do
  echo "$(grep -rl "$q" src --include='*.ts*' | grep -vc queries.ts)  $q"
done | sort -n
```

Anything with `0` is a candidate → the shell techniques.

## Related
<!-- bite: acdd1e38-ee5c-471c-be40-22b55b1532d8 -->
- [[frontend/frameworks/sanity/01-the-sanity-model|01 — the Sanity model]] · [[frontend/frameworks/sanity/03-portable-text-and-images|03 — Portable Text]]
- [[databases/sql-reference|SQL reference]] · [[cybersecurity/04-web-security/index|web security]]
