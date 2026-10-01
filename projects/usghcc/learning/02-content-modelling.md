# 02 — Content modelling

How the site's content is shaped, validated, and kept honest. The decisions
themselves are logged in the app repo's `DECISIONS.md` (D5, D13, D16); this
explains the thinking well enough to redo it elsewhere.

See also: [01-shell.md](01-shell.md) · [03-frontend.md](03-frontend.md) ·
[index.md](index.md)

---

## 1. The problem: JSON you import is a promise, not a fact

```ts
import about from "@/content/pages/about.json";
const page = about as Page;   // ← a lie, potentially
```

TypeScript types are **erased at runtime**. `as Page` compiles regardless of
what the file actually contains. If someone deletes a field, TypeScript is
perfectly happy and the page renders blank in production.

There is a second, subtler problem specific to imported JSON: TypeScript widens
string literals to `string`. So `"type": "hero"` imports as `string`, not as
the literal `"hero"` — which quietly destroys any discriminated union built on
that field.

**The fix is a runtime check at the boundary where content enters the app.**

---

## 2. Zod: one definition, both jobs

```ts
export const seoSchema = z.object({
  title: z.string().min(1),
  description: z.string().min(1).max(160),
});

export type Seo = z.infer<typeof seoSchema>;
```

`z.infer` derives the TypeScript type **from the validator**. Write the shape
once and you cannot have a type that says one thing and a check that enforces
another — the classic failure mode of hand-writing an `interface` next to a
hand-written `validate()`.

The validation runs in the content loader, which runs at build time, so **bad
content fails `next build`** instead of rendering an empty section to a
visitor. That is the whole point: move the failure from production to CI.

### Error messages are part of the design

```
Invalid content in about.json:
  whoWeAre.body — Required
```

versus `invalid content`. The first tells you the file and the field. Worth the
dozen lines it takes:

```ts
function describe(label: string, error: z.ZodError): string {
  const lines = error.issues.map((issue) => {
    const path = issue.path.length > 0 ? issue.path.map(String).join(".") : "(root)";
    return `  ${path} — ${issue.message}`;
  });
  return `Invalid content in ${label}:\n${lines.join("\n")}`;
}
```

### Throw, do not return null

A loader that returns `null` pushes an error case onto every caller, and the
lazy caller renders nothing. Throwing makes the build the thing that fails.

---

## 3. Blocks vs named fields — the real decision

Two ways to model a page.

**A page-builder / block model:**

```ts
sections: z.array(z.discriminatedUnion("type", [heroSchema, richTextSchema]))
```

**Named fields:**

```ts
const aboutPageSchema = z.object({
  seo, hero, whoWeAre, whatWeDo, objectives,
});
```

The block model buys exactly one thing: **an author can assemble a page that
nobody wrote a component for.** That is genuinely valuable for a CMS with
non-technical editors and dozens of pages.

What it costs on a six-page site maintained by one developer:

1. **Every page has the same loose type.** `page.sections[1]` is
   `Hero | RichText`, unnarrowable without a cast. `page.whoWeAre.body` is
   checked at compile time. Types you cannot use are types you do not have.
2. **Presentation leaks into array position.** The first renderer alternated
   section backgrounds with `index % 2`. Insert one block and every surface
   below it flips — a bug that is invisible in a diff and obvious to a
   designer.
3. **The page stops being readable.** A `switch` over section types tells you
   nothing about what the About page *is*. This tells you everything:

```tsx
<Hero {...page.hero} headingLevel="h1" />
<MediaText {...page.whoWeAre} />
<Pillars {...page.whatWeDo} tone="alt" />
<MediaText {...page.objectives} reverse />
```

**The migration argument does not rescue the block model.** A `page` document
with named fields is the normal way to model a fixed page in Sanity too;
page-builder arrays are the *other* option there, not the mature one. If a
page-builder is ever wanted, it can be added for the pages that need it without
dragging every fixed page through the abstraction.

**Revisit when:** someone other than a developer needs to create pages, or the
same block genuinely repeats across pages in author-chosen order.

---

## 4. What does *not* belong in content

From the schema file, written as a rule:

> no colours, no column counts, no image side, no heading levels

The test: **if a field would stop making sense after a redesign, it is not
content.** "Which side is the picture on" is a layout rhythm the component
owns; an author toggling it per block is how a page ends up with three pictures
down one edge.

Heading level is the sharpest example. `<h1>` vs `<h2>` depends on *position in
the document*, not on the block itself — the same component is an `h1` at the
top of a page and an `h2` further down. Storing it in content guarantees a page
with two `h1`s or none, which breaks screen-reader navigation. So it is a prop:

```tsx
<Hero {...page.hero} headingLevel="h1" />
```

---

## 5. Cross-field validation: `.refine()`

The old site's "Why Ghana?" section claimed Ghana invests "$170+ Billion
annually" in infrastructure. That is the African Development Bank's estimate of
**Africa's** annual financing gap. Ghana's entire GDP is roughly $75–85bn, so
the claim exceeded the whole economy by about 2×. A second card cited a "$1+
trillion value chain" — the World Bank's projection for **Africa's** food
market.

This is not a typo class of error, it is a credibility class of error: the
audience is investors and trade attachés who check numbers.

The structural fix — make it impossible to ship a number without saying where
it came from:

```ts
export const sectorSchema = z
  .object({
    title: z.string().min(1),
    figure: z.string().optional(),   // "$1tn by 2030"
    source: z.string().optional(),   // "World Bank, 2023"
  })
  .refine((sector) => !sector.figure || Boolean(sector.source), {
    message: "a figure must name its source — unsourced numbers do not ship",
    path: ["source"],
  });
```

Things worth noticing:

- **`.refine()` runs on the whole object**, which is what lets it express a
  relationship *between* fields. Per-field validators cannot see each other.
- **`path: ["source"]`** attaches the error to the field the author must fix.
  Without it the error lands on the object root and the message is harder to
  act on.
- **`.refine()` returns a `ZodEffects`**, not a `ZodObject` — so `.extend()`,
  `.merge()` and `.pick()` are no longer available on it. Refine **last**, after
  all composition, or keep the plain object around separately.
- **The implication direction matters.** `!figure || source` means "if there is
  a figure, there must be a source". A figure-less card is still valid — the
  current content ships qualitative cards precisely because nobody has verified
  the numbers yet.

**The general lesson:** when a mistake has already been made once and is
expensive, prefer a constraint over a convention. A comment saying "please cite
sources" is a hope. A schema that rejects the document is a guarantee.

This is the same instinct as putting invariants in database constraints rather
than only in application code — a rule enforced in one place is a rule the
system will eventually let you break.

---

## 6. The content boundary

```ts
// src/lib/content.ts — the ONLY module that imports a content file
export const getHomePage = cache(async (): Promise<HomePage> =>
  parseOrThrow("home.json", homePageSchema, homeJson),
);
```

Two deliberate choices:

- **`async` even though reading a local import is not.** Matching the eventual
  shape now means swapping JSON for a Sanity client touches this one file
  instead of every caller.
- **One getter per page**, not `getPage(slug)`. A generic getter can only
  return a union of every page shape; `getHomePage()` returns exactly
  `HomePage`. Generic-looking APIs that throw away type information are a bad
  trade.

**`cache()` is React's request-scoped memoisation.** Next.js calls
`generateMetadata()` and the page component separately, both needing the same
content. Without `cache`, the file parses twice per request.

---

## Outstanding — promote to the general vault

- [ ] Zod as a runtime boundary: `z.infer`, parse-don't-validate, `.refine()`
      for cross-field rules and its `ZodEffects` caveat → `backend/` or a new
      `validation/` folder
- [ ] "Constraint over convention" as a general engineering principle —
      pairs with the database-constraints material
