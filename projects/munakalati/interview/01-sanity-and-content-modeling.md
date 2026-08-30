# munakalati — Sanity and Content Modelling

From [[projects/munakalati/learning/03-sanity/README|learning/03-sanity]]. **Content modelling is a design activity most candidates have never had to do deliberately** — which makes it a good differentiator if you can talk about the trade-offs rather than the API.

---

### Q1. [Beginner] 🔥 What is a headless CMS, and why use one instead of WordPress?

**Strong answer covers:** a headless CMS stores structured content and exposes it over an API, with **no opinion about presentation**. WordPress couples content, templating and hosting; headless splits them.

The concrete pull for this project: the site needed to be a modern React app with animations, a carousel and a custom design system, and the content needed to be editable by non-technical staff in Cameroon. WordPress would have meant fighting the theme layer; Sanity meant the frontend was just a Next.js app that fetched JSON.

**The cost, and say it unprompted:** you now build and maintain everything WordPress gives free — every page template, every list, every 404. And you have two deploy targets rather than one.

**The line that lands:** *"Headless is right when the presentation is the differentiated part. If the site is a blog with a standard theme, WordPress is genuinely the better engineering decision."*

---

### Q2. [Intermediate] 🔥🔥 Walk me through how you modelled the content.

**Strong answer covers:** sixteen document types, but the useful framing is that they fall into **three shapes**, not sixteen things:

- **Real content** — `post`, `author`. Many rows, editor-created, referenced.
- **Ordered collections** — twelve of the sixteen (`partner`, `testimonial`, `initiative`, `teamMember`…). A curated list rendered as a page section, sequenced by an `order` field.
- **Singletons** — `heroContent`, `videoOverview`. Exactly one document each.

**Then the observation that shows you thought about it:** *"Twelve of sixteen being 'ordered list of things that render as a section' told me what this CMS actually is. It's not a database — it's a set of editable page sections. So the hard questions were about ordering, singletons and how much presentation belongs in the content layer, not about relations."*

---

### Q3. [Intermediate] 🔥 How do you do singletons in Sanity?

**Strong answer covers:** **you don't — a singleton is a document with a well-known ID, enforced by convention in three places:**

1. `structure.ts` links the sidebar item directly to `documentId("heroContent")` and filters that type out of the generic type list, so there's no "create" button.
2. The query pins the ID: `*[_type == "heroContent" && _id == "heroContent"][0]` — **not** `*[_type == "heroContent"][0]`.
3. `preview.prepare()` returns a static title, since there's only one.

**The bit to volunteer:** *"None of that prevents a second document being created through the API. What makes it safe is the query — pinning `_id` means a stray duplicate is inert rather than randomly winning. If I were hardening it I'd add `__experimental_actions: ['update','publish']` to remove create and delete from the Studio entirely."*

**The general principle:** in a document store, a singleton is a well-known ID that every reader agrees to use. Same pattern as the migration's `DEFAULT_AUTHOR_ID`.

---

### Q4. [Intermediate] 🔥🔥 You have `validation: (r) => r.required()` on a field. Is that field guaranteed to be present?

**No — and this is the question to get right.** `required()` is a **Studio form check**. The API accepts documents without it. Every one of the 434 migrated posts entered through the API and never touched the Studio.

**The evidence in the code:**

```groq
*[_type == "post" && defined(publishedAt) && publishedAt <= now()]
*[_type == "stat" && (context == "home" || !defined(context))]
```

Both `publishedAt` and `context` are `required()`, and both are guarded anyway. The `!defined(context)` clause is a backwards-compatibility shim for documents created before the field existed — `required()` doesn't apply retroactively either.

**The generalisation:** *"CMS validation is a UX affordance, not a constraint. If I need a real guarantee I enforce it in the query with `defined()`, or I run a script over the dataset. It's the same distinction as client-side form validation versus a database `NOT NULL`."*

---

### Q5. [Intermediate] Explain GROQ to someone who knows SQL.

**Strong answer covers:** every query is `*[filter] | order() [slice] { projection }`. `*` is all documents; there are no tables, just a `_type` predicate.

The mappings: `SELECT` → the trailing projection, `WHERE` → the filter, `JOIN` → `->`, `LIMIT` → `[0...20]`, `COUNT(*)` → `count(*[...])`.

**The two differences worth naming:**

- **The projection is a shape, not a list.** `coverImage { asset, alt }` returns a nested object. You describe the JSON you want back.
- **`->` follows a reference and inlines the target, server-side.** `author-> { name, photo }` is a join with no join syntax and no second round trip. It chains: `author->photo.asset->url`.

---

### Q6. [Intermediate] 🔥 How do you filter by category without building the query string dynamically?

```groq
*[_type == "post" && ($category == "all" || category == $category)]
```

**Strong answer covers:** when the caller passes `"all"`, the left side short-circuits and the clause is a no-op. One static query serves both cases.

**Why it matters:** concatenating a filter fragment means the query text varies per request — which kills any query-plan reuse and, more importantly, reintroduces the injection surface that bound parameters exist to remove. **`$param` is a bound parameter, never interpolated into the query text**, exactly like a prepared statement.

**Bonus, if you want to be honest about your own code:** *"There's a live bug next to that one. The same query has `_id != $featuredId` to stop the featured post also appearing in the grid, and the page passes an empty string, so it never excludes anything. The fetches run in a `Promise.all`, so the featured post's ID isn't known yet when the paged query is fired — a parallel-fetch optimisation quietly breaking a data dependency."*

---

### Q7. [Advanced] What's Portable Text and why not just store HTML?

**Strong answer covers:** Portable Text is rich text as **structured JSON** — an array of `block`s, each with `children` spans carrying `marks`, plus `markDefs` for annotations that carry data (links).

Four arguments against an HTML blob, in order of weight:

1. **Renderable anywhere.** React on the web, native components in an app, plain text for a search index. HTML encodes a rendering decision permanently.
2. **Safe by construction.** There is no arbitrary markup to sanitise, because there is no markup.
3. **Queryable and diffable.** GROQ can reach inside blocks; Sanity can merge concurrent edits.
4. **Custom embeds are first-class.** An image inside an article body is a structured node, so it can go through `next/image` with a hotspot-aware CDN URL inside a semantic `<figure>` — not an `<img>` tag parsed out of a string.

**The cost:** nothing renders until you supply a component map. Four buckets — `block` (by style), `list`, `marks` (decorators and annotations), and `types` (non-text nodes).

**The detail that proves you've used it:** *"Links are the fiddly part. A link's `href` isn't on the span — the span carries a `_key` in its `marks` that points at a `markDefs` entry on the parent block. It's a normalisation, so one annotation can span several spans. It's also why my migration dropped every link: mapping bold to `strong` is one line, mapping a link means accumulating `markDefs` across a whole block."*

---

### Q8. [Advanced] 🔥 Your hero splits the headline into three fields. Defend that.

**This is a "can you argue a trade-off" question.** Don't just defend it.

```
headlineStart      "Stories that"
headlineHighlight  "shape"           ← rendered in the brand colour
headlineEnd        "Africa's future"
```

**Against:** the CMS now knows about the design. An editor who wants to highlight a different word has to think in three fields. A rebrand means editing content documents.

**For:** the alternative is one field with Portable Text or markdown so the editor marks the highlight themselves — which is *more* conceptual load for a two-person content team, and a richer authoring surface just gets misused differently. Three labelled fields with `description` examples are unambiguous and impossible to break.

**The verdict to give:** *"For a small team, the three fields are the right trade. Where I'd push back on my own code is the `initiative` type, which stores `bgColor` as a free-text string — that lets a non-designer put any hex value on the homepage. If presentation has to live in the CMS it should be `options: { list: [...] }` with named brand choices. **Constrain the choice, don't remove it.**"*

---

### Q9. [Intermediate] Your types are hand-written. What's wrong with that, and what's the fix?

**Strong answer covers:** they drifted, in the dangerous direction — declaring more than the data has.

- `TeamMember` and `BoardMember` both declare `localPhoto?: string`. No schema defines it.
- `body` is `unknown[]`, forcing `value={post.body as Parameters<typeof PortableText>[0]["value"]}` at the call site.
- **The real one:** the interfaces describe *documents*, but queries return *projections*. `relatedPostsQuery` doesn't select `author`, yet its results are typed `Post[]`, which declares `author` as non-optional. `related[0].author.name` typechecks and throws at runtime.

**The fix is Sanity TypeGen** — it reads the schema *and* every `groq`-tagged query and emits a type per query, so a projection that omits `author` produces a type without `author`. Every query in the project already carries the `groq` tag TypeGen looks for; it got 90% of the way there and stopped.

**The line:** *"Hand-written types against an external system aren't types, they're hopeful comments."*

---

### Q10. [Intermediate] How did you make the Studio usable for non-technical editors?

**Strong answer covers, honestly:** partially. What was done — Structure Builder pins the two singletons at the top and hides them from the generic list; `preview` gives every type a title, subtitle and thumbnail; `description` on fields carries examples.

**Why previews matter more than they look:** with 434 migrated posts, a document list without a `media` and `subtitle` is 434 identical rows and the CMS is unusable. The `"No author"` fallback in the post preview also makes broken data visible at a glance instead of rendering an empty row.

**What wasn't done, and say so:** *"An editor still sees sixteen flat document types with no indication of which page each one feeds. The obvious next step is grouping — nesting `teamMember`, `boardMember`, `ambassador` and `timeline` under one 'About page' folder in Structure Builder. **The Studio's default is a developer's view of the content model; an editor thinks in pages and tasks.** Sixteen alphabetical types is roughly where translating between the two starts being worth the effort."*

## Related
- [[projects/munakalati/learning/03-sanity/README|learning/03-sanity]]
- [[frontend/frameworks/sanity/README|the general Sanity course]] · [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modelling]]
