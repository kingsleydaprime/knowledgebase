# Converting a Foreign Rich-Text Format into Portable Text

**Split from:** the munakalati migration domain. **See also:** [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|sanity/04 — the format itself]] · [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|02 — the Wix API]]

**This is the hardest part of any CMS migration** and the one that decides whether the imported content is genuinely usable or just technically present.

---

## Two trees, and the mapping between them

Wix stores rich text as its **Document Model** — a tree of typed nodes:

```json
{ "type": "PARAGRAPH",
  "nodes": [
    { "type": "TEXT", "textData": { "text": "Hello ", "decorations": [] } },
    { "type": "TEXT", "textData": { "text": "world", "decorations": [{ "type": "BOLD" }] } }
  ] }
```

Sanity stores it as **Portable Text** — a flat array of blocks, each with spans:

```json
{ "_type": "block", "_key": "a1b2c3d4", "style": "normal", "markDefs": [],
  "children": [
    { "_type": "span", "_key": "e5f6", "text": "Hello ", "marks": [] },
    { "_type": "span", "_key": "g7h8", "text": "world", "marks": ["strong"] }
  ] }
```

Similar enough to lull you, different in three ways that matter:

| | Wix Document Model | Portable Text |
|---|---|---|
| **Structure** | arbitrarily nested tree | **flat array** of block-level items |
| **Text** | `TEXT` node with `textData.text` | `span` with `text` |
| **Formatting** | `decorations: [{type: "BOLD"}]` | `marks: ["strong"]` |
| **Identity** | none needed | **`_key` required on every node** |

**"Tree → flat array" is the central problem.** A blockquote containing a paragraph containing bold text is three levels deep in Wix; in Portable Text it's one block with a `style` and some spans. Anything nested must be either flattened or dropped, and *deciding which* is the actual work.

## The converter, and the recursion that makes it work

```js
async function toPortableText(nodes = []) {
  const blocks = [];

  for (const node of nodes) {
    if (node.type === "TEXT") continue;              // leaves handled by their parent

    if (node.type === "PARAGRAPH") {
      const children = (node.nodes || [])
        .filter((n) => n.type === "TEXT")
        .map((n) => ({
          _type: "span",
          _key: key(),
          text: n.textData?.text ?? n.text ?? "",
          marks: wixMarks(n.textData?.decorations),
        }));

      if (children.some((c) => c.text.trim())) {
        blocks.push({ _type: "block", _key: key(), style: "normal", markDefs: [], children });
      }
    }

    if (node.type === "HEADING") {
      const level = node.headingData?.level ?? 2;
      const style = level <= 2 ? "h2" : level === 3 ? "h3" : "h4";
      // ...same span mapping...
      blocks.push({ _type: "block", _key: key(), style, markDefs: [], children });
    }

    if (node.type === "IMAGE") {
      const imageUrl = node.image?.src?.url || node.image?.url;
      if (imageUrl) {
        const ref = await uploadImage(imageUrl);
        if (ref) blocks.push({ ...ref, _key: key(), alt: node.image?.altText || "" });
      }
    }

    // Recurse into container nodes (BLOCKQUOTE, lists, COLLAPSIBLE, etc.)
    if (node.nodes?.length && !["PARAGRAPH", "HEADING"].includes(node.type)) {
      blocks.push(...(await toPortableText(node.nodes)));
    }
  }

  return blocks;
}
```

**The last clause is the flattening strategy, and it's the cleverest line in the migration.** Anything that isn't a paragraph or a heading but *has* children gets recursed into, and whatever comes back is spliced into the same flat output array. A `BLOCKQUOTE > PARAGRAPH > TEXT` yields a plain paragraph block. A three-level nested list yields a series of paragraphs.

The `!["PARAGRAPH", "HEADING"].includes(node.type)` exclusion is what stops double-processing: those two types consume their own `TEXT` children directly, so recursing into them as well would emit every paragraph twice.

**What this strategy buys and what it costs:**

- **Buys:** unknown node types degrade gracefully. Wix can add a `COLLAPSIBLE_LIST` or a `TABLE` tomorrow and the text inside it still comes through as paragraphs rather than vanishing. For a migration against a format you don't control, that is the right default — **preserve the words, lose the wrapper**.
- **Costs:** every blockquote in 434 posts is now an ordinary paragraph. Every bulleted list is a run of paragraphs with no bullets. The information is there; the semantics are gone, and no future script can recover them because the distinction wasn't recorded.

**This is a genuine judgement call, not an oversight**, and the right way to think about it is: how much of the corpus is affected, and how visible is the loss? For a blog that's mostly prose, flattening a handful of quotes is a fair trade for shipping. If the source had been documentation full of nested lists and tables, the same choice would have destroyed it.

The tell that it *was* a choice rather than an accident: the frontend defines a `blockquote` renderer and `bullet`/`number` list renderers in `portableTextComponents`. **The rendering side supports what the migration doesn't produce** — the styling was ready for content that never arrives, which is itself a small useful signal when reading this code later.

## Decorations → marks

```js
function wixMarks(decorations = []) {
  const marks = [];
  for (const d of decorations) {
    if (d.type === "BOLD") marks.push("strong");
    else if (d.type === "ITALIC") marks.push("em");
    else if (d.type === "UNDERLINE") marks.push("underline");
  }
  return marks;
}
```

Three mapped, everything else silently dropped. **The notable omission is `LINK`.** Wix carries links as a decoration with a `linkData`; Portable Text needs a `markDefs` entry on the block plus a `_key` reference in the span's `marks` — the indirection described in [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|sanity/04]]. It's more work than pushing a string, and it wasn't done.

**Consequence: every hyperlink in 434 migrated posts is now plain text.** The words survive; the destinations are gone. That's the largest single piece of data loss in this migration, and it's worth stating plainly rather than filing under "minor". Any internal cross-links between posts, any citations, any calls to action — all inert.

It's also the most *recoverable* loss, because Wix still has the source: a repair script in the style of `fix-slugs.js` could re-fetch each post, walk for link decorations, and patch `body`. Whether that's worth doing is a content decision, but the option should be on the table in the handover rather than discovered later.

Sketch of what the mapping would need:

```js
// per block, collect link decorations into markDefs and reference them by _key
const markDefs = [];
const marks = [];
for (const d of decorations) {
  if (d.type === "LINK") {
    const _key = key();
    markDefs.push({ _key, _type: "link", href: d.linkData?.link?.url });
    marks.push(_key);                    // the span references the definition
  } else if (d.type === "BOLD") marks.push("strong");
  // ...
}
```

Note that `markDefs` is per-*block*, not per-span, so it has to be accumulated across all a block's spans and attached to the parent — which is exactly why the current code hardcodes `markDefs: []` and moves on.

## Empty-block filtering

```js
if (children.some((c) => c.text.trim())) {
  blocks.push({ ... });
}
```

Only emit a block if at least one span has non-whitespace text. Rich text editors accumulate empty paragraphs — someone pressing Enter twice, a trailing blank line, a spacer. Import them faithfully and every article renders with random gaps, because `mb-6` on an empty `<p>` is still `mb-6`.

**`.some()` rather than checking the joined string** is the right shape: it short-circuits on the first non-empty span.

Note the asymmetry — `PARAGRAPH` has this guard, `HEADING` doesn't. An empty heading would be emitted. Almost certainly harmless (empty headings are rare), and almost certainly an oversight rather than a decision.

**Cleaning during migration is right, and worth defending:** an empty paragraph carries no information, and every downstream consumer would have to filter it forever. But the line is fine — filter *noise*, never filter *content you don't currently render*. Dropping empty blocks is cleaning; dropping links because the renderer is easier without them would have been data loss disguised as cleaning.

## The async recursion nobody notices

`toPortableText` is `async` and `await`s `uploadImage` inline for every `IMAGE` node — inside a `for...of` loop, inside a recursive call.

**`for...of` with `await` is sequential**, which here is *correct*: it preserves the order of blocks in the article. `Promise.all` over the nodes would upload images in parallel and then need to reassemble them in order.

And the sequential-looking upload isn't actually a bottleneck, because `uploadImage` immediately hands off to `limit(...)` — the bounded queue from [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|note 03]] — so five uploads still run concurrently *across* posts even though each post's blocks are built in order. **Ordering at the block level, parallelism at the transport level.** That separation is worth noticing; it's easy to get one at the cost of the other.

The `imageCache` (`Map` from resolved URL to asset ref) means a logo repeated in fifty posts is downloaded and uploaded once. It's per-process, so it resets between runs — Sanity's own asset deduplication catches the rest.

## The general shape of a rich-text converter

Migrating *any* rich text into *any* other rich text, the same five questions come up:

1. **What are the block-level types on each side, and how do they correspond?** (paragraph, heading levels, quote, list, code)
2. **What are the inline annotations, and do any carry data?** (bold/italic are flags; links and footnotes carry payloads and are always the fiddly ones)
3. **How do embeds work?** (images, video, custom widgets — usually a custom node type on both sides)
4. **What do you do with nesting the target can't express?** Flatten, drop, or approximate — **decide deliberately and write it down.**
5. **What identity does the target require?** (`_key`s here; some formats need stable IDs for anchors)

And one meta-rule: **convert a handful of representative posts first and read the output as rendered HTML before running the batch.** The most expensive version of this task is discovering after importing 434 posts that every list became a wall of text — which is, in fact, roughly what happened.

## Related
- [[projects/munakalati/learning/03-sanity/04-images-and-portable-text|sanity/04 — rendering the result]]
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — postmortems]]
- [[concepts/04-best-practices/06-data-migrations|the general playbook]]
