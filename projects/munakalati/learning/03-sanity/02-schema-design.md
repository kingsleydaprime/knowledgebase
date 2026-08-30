# Sanity — Schema Design

**Split from:** the munakalati Sanity domain. **See also:** [[projects/munakalati/learning/03-sanity/01-setup-and-mental-model|01 — setup]] · [[projects/munakalati/learning/03-sanity/03-groq-queries|03 — GROQ]] · [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|04 — images & Portable Text]]
**General version:** [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modeling and headless CMS]]

---

## What a schema actually is here

A Sanity schema is **plain JavaScript that describes documents**, and it does three jobs at once:

1. **Validation** — what the API will accept.
2. **UI generation** — the Studio form an editor sees is derived entirely from it.
3. **Documentation** — `title` and `description` on a field are the only instructions a non-technical editor gets.

That third job is the one developers underrate. There is no separate "how to use the CMS" doc for the Muna team; `description: 'Small label above the headline, e.g. "Africa\'s Children\'s Media Ecosystem"'` **is** the documentation, and it's read at exactly the moment it's needed.

The whole vocabulary in one type — `src/sanity/schemaTypes/post.ts`:

```ts
export default defineType({
  name: "post",           // the machine name — appears in GROQ as _type == "post"
  title: "Blog Post",     // what the editor sees
  type: "document",       // a top-level, independently addressable thing
  fields: [ /* ... */ ],
  preview: { /* how it appears in lists */ },
});
```

**`defineField` / `defineType` are not decoration.** They're identity functions whose only job is to give TypeScript enough context to narrow the object type — so that `options: { hotspot: true }` typechecks on an `image` and errors on a `string`. Without them you get a widened object and no help at all. Always use them.

## The sixteen types, grouped by what they really are

Munakalati has 16 registered types (`src/sanity/schemaTypes/index.ts`). They fall into four distinct shapes, and recognising the shapes is more useful than memorising the list:

| Shape | Types | Characteristic |
|---|---|---|
| **Real content** | `post`, `author` | Many rows, editor-created, referenced by each other |
| **Ordered collections** | `partner`, `testimonial`, `initiative`, `program`, `stat`, `timeline`, `teamMember`, `boardMember`, `ambassador`, `award`, `pressFeature`, `heroBanner` | A hand-curated list rendered as a section; `order` field drives sequence |
| **Singletons** | `heroContent`, `videoOverview` | Exactly one document should ever exist |

**Twelve of sixteen types are "ordered collection".** That's what a marketing site's CMS mostly is: not a database, a set of editable page sections. Seeing that clearly is what tells you the interesting modelling questions here are about *ordering, singletons, and presentation coupling* — not about relations and normalisation.

## Pattern 1 — the `order` field

Every collection type carries the same three-part pattern:

```ts
// 1. the field
defineField({ name: "order", title: "Order", type: "number", initialValue: 0 }),

// 2. tell the Studio it can sort by it
orderings: [
  { title: "Order", name: "orderAsc", by: [{ field: "order", direction: "asc" }] },
],
```

```groq
// 3. and the query actually applies it
*[_type == "partner"] | order(order asc) { _id, name, logo { asset, alt }, href, category }
```

**All three are needed and they do different things.** The field stores it; `orderings` makes the Studio *list* sortable so an editor can see the running order while editing; the `| order()` in GROQ is what the *website* obeys. Skip the third and the site renders in Sanity's internal order (roughly creation order) no matter what the editor does — a classic "I changed it in the CMS and nothing happened" report.

**The known weakness of integer ordering:** every item defaults to `0`, so an editor's first experience is a list with no order at all, and reordering means retyping numbers on several documents. Sanity's own answer for a genuinely reorderable list is an **array of references on a parent document** (drag-to-reorder in the Studio, order is the array index) or the `@sanity/orderable-document-list` plugin. Integer `order` is the cheap version — completely fine for a dozen partners, painful at a hundred.

## Pattern 2 — singletons, enforced only by convention

`heroContent` and `videoOverview` should each have exactly one document. Nothing in the schema says so. The enforcement is spread across three places, and it's worth seeing that it's **three coordinated hacks, not a feature**:

```ts
// 1. structure.ts — the Studio sidebar links straight to one fixed document ID
S.listItem()
  .title("Hero Content")
  .id("heroContent")
  .child(S.document().schemaType("heroContent").documentId("heroContent")),

// ...and then hides the type from the generic "all document types" list
...S.documentTypeListItems().filter(
  (item) => !["heroContent", "videoOverview"].includes(item.getId() ?? "")
),
```

```groq
// 2. the query hardcodes the same ID rather than taking [0] of all of them
*[_type == "heroContent" && _id == "heroContent"][0] { badge, headlineStart, ... }
```

```ts
// 3. and the preview refuses to show a title, since there's only ever one
preview: { prepare() { return { title: "Hero Content" }; } },
```

**The `&& _id == "heroContent"` in the query is the load-bearing part.** Without it, `*[_type == "heroContent"][0]` returns *some* hero document — and if a stray second one ever got created (via the API, or a draft, or an import), the site could silently start rendering the wrong one, with no error anywhere. Pinning the ID means a stray document is inert.

What's still missing, and would be the improvement: nothing prevents *creating* a second one. Sanity's `__experimental_actions: ['update', 'publish']` on the type removes the create/delete actions from the Studio entirely. Worth adding if this were ongoing.

**The general principle** — the one that transfers beyond Sanity: *a singleton in a document store is a document with a well-known ID.* You don't get "one row" for free; you pick an ID, and every reader agrees to use it. Same trick as `DEFAULT_AUTHOR_ID = "author-muna-kalati"` in the migration script.

## Pattern 3 — the discriminator field

`stat` is used in two different places on the site with different fields showing. Rather than two document types, it has a `context`:

```ts
defineField({
  name: "context",
  type: "string",
  options: { list: [ /* home | traction */ ] },
  validation: (r) => r.required(),
}),
```

```groq
*[_type == "stat" && (context == "home" || !defined(context))] | order(order asc) { _id, value, label }
*[_type == "stat" && context == "traction"] | order(order asc) { _id, value, label, icon }
```

**Read the `!defined(context)` clause carefully — that's a migration artifact turned into a default.** `context` is `required()` *now*, but documents created before the field existed have no `context` at all, and `required()` only runs in the Studio, never retroactively against stored data. So the home query treats "missing" as "home", which is both a backwards-compatibility shim and an accidental default.

**This is the single most important thing to internalise about CMS validation:** `validation: (r) => r.required()` is a **Studio-time form check**, not a database constraint. The API will happily accept a document without the field — which is exactly how every migrated post got in. If you need a real guarantee, you enforce it in the query (`defined(x)`) or you run a script over the dataset. Never assume stored data satisfies the current schema.

That assumption shows up in `allPostsQuery` too: `defined(publishedAt) && publishedAt <= now()` — belt-and-braces against migrated posts with a missing or future date, even though `publishedAt` is `required()`.

## Where the modelling gets debatable: presentation in the content layer

Two types store what are effectively design decisions.

**`heroContent` splits the headline into three fields:**

```ts
headlineStart      // "Stories that"
headlineHighlight  // "shape"      ← rendered in the brand colour
headlineEnd        // "Africa's future"
```

**`initiative` stores colours:**

```ts
bgColor      // required
accentColor  // optional
```

The case *against*: the CMS now knows about the design. An editor who wants to highlight a *different* word has to think in terms of three fields; a rebrand means editing content documents, not CSS; and `bgColor` lets a non-designer put `#FF00FF` on the homepage.

The case *for*, which is real: the alternative — one `headline` string plus Portable Text or markdown so the editor can mark the highlight themselves — is **more** conceptual load for a small team, and richer authoring surfaces get misused in different ways. Three labelled string fields with `description` examples are unambiguous and impossible to break.

**The honest verdict:** three-field headline is a reasonable trade for a small site with two or three editors. `bgColor`/`accentColor` as free strings is the weaker one — if presentation must live in the CMS, it should be `options: { list: [...] }` with named brand choices ("Sunrise", "Deep"), not an arbitrary colour. That keeps editors inside the design system while still giving them the control. **Constrain the choice, don't remove it.**

## Pattern 4 — `preview` is for the editor, not the website

```ts
preview: {
  select: { title: "title", author: "author.name", media: "coverImage" },
  prepare({ title, author, media }) {
    return { title, subtitle: author ? `by ${author}` : "No author", media };
  },
},
```

`select` maps document paths (dot-notation reaches *through* the `author` reference) to named values; `prepare` turns them into the `{title, subtitle, media}` a Studio list row displays. Purely a Studio concern — no effect on the API or the site.

**It matters more than it looks with 434 migrated posts.** Without a `media` and a `subtitle`, a document list is 434 identical-looking rows and the CMS becomes unusable. The `"No author"` fallback in particular is good practice: a preview that renders `undefined` or an empty row makes broken data invisible, and this one makes it obvious at a glance.

## Where the types drifted

`src/sanity/lib/types.ts` is **hand-written** — TypeScript interfaces maintained in parallel with the schema. Predictably, they disagreed:

- `TeamMember` and `BoardMember` both declare `localPhoto?: string`. **No schema defines it.** It's a leftover from when the About page used files in `/public` before the CMS took over.
- `Post.body` is typed `unknown[]`, so Portable Text needs a cast at the call site: `value={post.body as Parameters<typeof PortableText>[0]["value"]}`. That cast is a type hole wearing a hat.
- The interfaces describe the *documents*, but queries return **projections** — `relatedPostsQuery` selects no `author`, yet the result is still typed `Post[]`, which declares `author` as non-optional. Any code reading `related[0].author.name` would typecheck and then throw at runtime.

**The fix is Sanity TypeGen**, and this is the concrete argument for it: `sanity typegen generate` reads the schema *and* every `groq` tagged query and emits a type per query — so a projection that omits `author` produces a type without `author`, and the mistake above becomes a compile error. The `groq` tag on every query in `queries.ts` is already exactly what TypeGen needs to find them; the project got 90% of the way there and stopped.

**The transferable lesson:** hand-written types against an external system aren't types, they're **hopeful comments**. Generate them from the source of truth or expect drift — and the drift will be in the direction of "declares more than the data has", which is the dangerous direction.

## Related
- [[projects/munakalati/learning/03-sanity/03-groq-queries|03 — GROQ queries]] — where the `defined()` guards pay off
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — bugs and postmortems]]
- [[databases/database-design-reference|database design reference]] — the relational counterpart to this
- [[concepts/04-best-practices/01-clean-code|clean code]]
