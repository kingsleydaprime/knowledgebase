# Content Modelling and the Headless CMS

**[[frontend/04-state-and-data/README|04 — State and Data]], note 3.** **[Intermediate]** `[reference]`

**Framework-agnostic.** The Sanity implementation is [[frontend/frameworks/sanity/README|frameworks/sanity]]; a real 16-type model is [[projects/munakalati/learning/03-sanity/02-schema-design|munakalati]].

> **The one idea:** content modelling is a third design discipline, distinct from database design and from component design — and the question it answers is not *"what shape is this data?"* but ***"what should a non-technical person be able to change, and how badly can they break the page doing it?"***

---

## Coupled vs. headless

A traditional CMS (WordPress, Wix, Drupal) owns the content **and** the templates **and** the hosting. A **headless** CMS owns only the content and exposes it over an API; presentation is entirely yours.

|  | Coupled | Headless |
|---|---|---|
| **Presentation** | themes/templates in the CMS | your app, any framework |
| **Multi-channel** | the website is the product | one API, many consumers |
| **Editor experience** | usually "edit the page" | usually "edit the data" |
| **You maintain** | plugins and theme overrides | every template, list and 404 |
| **Time to a basic blog** | an afternoon | a week |

**Choose headless when the presentation is the differentiated part.** If the site is a blog with a standard theme, a coupled CMS is genuinely the better engineering decision, and saying so is a mark of judgement rather than a lack of ambition.

The real cost of headless is not technical. It's that **you now own the editor's experience**, and nobody assigns story points to it.

## What kind of thing is each document type?

Most content models are three shapes, and naming the shape tells you which problems you'll have:

**1. Real content** — many rows, editor-created, related to each other. Posts, authors, products. **The problems are relations and lifecycle**: drafts, scheduling, referential integrity when something is deleted.

**2. Ordered collections** — a hand-curated list rendered as a page section. Testimonials, partners, team members, timeline entries. **The problem is ordering**, and it's underrated.

**3. Singletons** — exactly one document. Hero content, site settings, a footer. **The problem is that most CMSs don't have them**, so you enforce one by convention.

In practice a marketing site is overwhelmingly shape 2. **When most of your types are "an editable page section", the interesting questions are ordering, singletons and presentation coupling — not normalisation.** That realisation saves a lot of time spent designing relations nobody needs.

## Ordering

The naive approach — an integer `order` field — needs three cooperating pieces, and people usually ship two:

1. the field on the document,
2. a sort configuration so the *editor* sees the list in running order,
3. **an explicit sort in the query**, or the site ignores all of it.

Miss the third and you get the classic report: *"I reordered it in the CMS and nothing changed."*

**Its real weakness is ergonomic:** every item defaults to `0`, so an editor's first experience is a list with no order, and reordering means retyping numbers across several documents. The alternatives are **an array of references on a parent document** (drag-to-reorder, order is the array index) or a fractional-index / orderable-list plugin. **Integer `order` is fine for a dozen items and painful at a hundred** — pick knowing which you have.

## Singletons

There is usually no built-in "exactly one". A singleton is **a document with a well-known ID that every reader agrees to use**, and making it stick takes three things:

- the admin UI links directly to that ID (no pointless list-of-one),
- the **query pins the ID** rather than taking the first of all of them,
- the create and delete actions are removed for that type.

**The pinned ID in the query is the load-bearing part.** Take `[0]` of all documents of the type and a stray second one can silently start winning, with no error anywhere. Pin it and a duplicate is inert.

## Validation is a form check, not a constraint

> **In almost every headless CMS, "required" is enforced by the editing UI, not the API.**

Anything written by a script, a migration or a direct API call can violate it — and validation never applies retroactively to documents created before a rule existed. This is the single most common wrong assumption developers bring from relational databases, where `NOT NULL` means *not null*.

Three consequences:

- **Guard in the query** (`defined(x)`), not in your head.
- **Handle missing fields in components**, especially anything bulk-imported.
- **If you need a real guarantee, script it** over the dataset and re-run it.

## The presentation-coupling question

The recurring judgement call: **how much design belongs in the content layer?**

Two real examples from a live model:

```
headlineStart      "Stories that"
headlineHighlight  "shape"           ← rendered in the brand colour
headlineEnd        "Africa's future"
```

```
bgColor      "#FDF4EE"     free-text hex
accentColor  "#E8500A"
```

**Against:** the CMS now knows about the design. Editors think in implementation terms; a rebrand means editing content; a non-designer can put anything on the homepage.

**For, and it's a real argument:** the alternative — one rich-text field so the editor marks the highlight themselves — is *more* conceptual load for a small team, and a richer authoring surface just gets misused differently. Three labelled fields with worked examples in their descriptions are unambiguous and hard to break.

**The rule that resolves it:** **constrain the choice, don't remove it.** The three-field headline is a fair trade. A free-text colour is not — the same control as a named list ("Sunrise", "Deep") keeps editors inside the design system while still giving them the decision. **Where presentation must live in the CMS, it should be an enumeration, not a string.**

## The schema is documentation

The field labels and descriptions are the only instructions most editors will ever read, delivered at the moment they're needed. `description: 'Small label above the headline, e.g. "Africa's Children's Media Ecosystem"'` is worth more than a wiki page nobody opens.

The same goes for **list previews**. Four hundred documents with no thumbnail and no subtitle is an unusable CMS. And give the subtitle an explicit fallback — *"No author"* rather than a blank — so broken data is visible at a glance instead of invisible.

## Generate your types

Hand-maintaining TypeScript interfaces against a CMS schema **guarantees drift**, and the drift is always in the dangerous direction: the types declare more than the data has.

The specific trap: interfaces describe *documents*, but queries return *projections*. Type a projection's result as the full document type and code reading a field that query never selected typechecks fine and throws at runtime.

**Most headless CMSs now ship a type generator that reads the schema and the queries.** Use it. **Hand-written types against an external system aren't types, they're hopeful comments.**

## The fallback pattern

Common enough to name. Sites are usually designed and built *before* the CMS exists — you can't model content that doesn't exist yet, and stakeholders approve a page, not a schema. So each section keeps its original hardcoded content and uses it when the CMS returns nothing:

```
data = cmsResult.length > 0 ? adapt(cmsResult) : FALLBACK
```

The piece that makes it clean is a **view model** — a shape that is neither the CMS type nor raw props — plus one adapter function. Image URLs become plain strings on both paths, so **the markup never learns where the data came from** and there's no branching scattered through it.

**Wins:** frontend and content entry proceed in parallel; every page is always renderable; a fresh clone with no credentials still runs.

> **The risk, and it is serious: if a query breaks — a renamed field, a typo — the fetch returns empty and the page renders the fallback *perfectly, with no error*. You lose the integration and the site looks fine.** That's worse than a crash, because a crash gets fixed the same day.

**Two cheap mitigations:** log server-side whenever a fallback fires, so it reaches your platform logs; and a strict mode in production that throws instead of falling back. And treat the fallbacks as scaffolding with a demolition date — once a section's content is genuinely in the CMS, the hardcoded copy is dead weight pretending to be a safety net.

## Related
- [[frontend/frameworks/sanity/README|frameworks/sanity]] — one implementation, in depth
- [[projects/munakalati/learning/03-sanity/02-schema-design|munakalati — a real 16-type model]]
- [[concepts/04-best-practices/06-data-migrations|data migrations]] — getting content *into* the model
- [[databases/database-design-reference|database design]] — the discipline this is not
