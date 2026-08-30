# munakalati — Migration and Data Integrity

From [[projects/munakalati/learning/05-migration/README|learning/05-migration]]. **This is the strongest material in the project.** Bulk data migration is something most developers do once, badly, and never reflect on — being able to talk about idempotency, verification and repair as *design* rather than firefighting is genuinely differentiating.

---

### Q1. [Intermediate] 🔥🔥 Walk me through the migration.

**Strong answer covers the five phases**, and the point that they're separate scripts for a reason:

1. **Extract** — paginate the Wix Blog API, fetch each post's full content.
2. **Transform** — map fields; convert Wix's rich-text tree into Portable Text.
3. **Load** — `createOrReplace` into Sanity with a deterministic `_id`; upload images to the asset store.
4. **Verify** — a JSON run report, plus GROQ spot checks in Vision.
5. **Repair** — three separate scripts for the classes of damage phase 4 found.

**Numbers:** 434 posts, 208 skipped as already-done on the final run, 0 failures. 418 of 433 cover images backfilled.

**The framing that makes this a good answer:** *"Phase 5 is the one people don't plan for and always need. It isn't evidence the migration was done badly — **you cannot know how inconsistent the source data is until you've pulled all of it.** Posts whose rich content 401s, images stored under an internal `wix:image://` scheme, slugs percent-encoded for French titles: I found all three at scale, after loading, and fixed them with small targeted scripts rather than re-running the whole import."*

---

### Q2. [Intermediate] 🔥🔥 How did you make it safe to run twice?

**Strong answer covers the pair:** a **deterministic ID derived from the source record** plus an **upsert**.

```js
_id: `wix-${listing.id}`
await sanity.createOrReplace(doc);
```

Same Wix post always produces the same Sanity `_id`; `createOrReplace` overwrites rather than inserting. **Running it N times leaves the same dataset as running it once.**

**Then the nuance that shows depth** — the three write verbs and what choosing between them means:

| | Behaviour | Use when |
|---|---|---|
| `create` | fails if the ID exists | a duplicate run should be an error |
| `createOrReplace` | upsert, **replaces the whole document** | re-importing from a source of truth |
| `patch(id).set({…})` | merges named fields only | fixing one field on existing docs |

*"`createOrReplace` replacing the whole document is the sharp edge. Once editors started fixing categories by hand in the Studio, re-running the migration became destructive — the script's version wins entirely. That's exactly why the repair scripts use `patch().set()` instead: `fix-slugs` changes `slug` and nothing else. **Choosing between replace and patch is choosing whose edits win.**"*

---

### Q3. [Intermediate] 🔥🔥 Tell me about a mistake you made in the migration.

**The 868-post duplication — the crispest lesson in the project.**

The first script wrote `_id: post.id`, the raw Wix UUID. The rewrite wrote `_id: "wix-" + id`. Both had been run. Since `createOrReplace` keys on `_id` and the two generated *different* IDs for the same source post, the second created a full second copy. **434 posts became 868.**

**The fix:** `dedup.js` — group by slug, keep the `wix-` prefixed document, delete the rest.

**The lesson, stated generally:** *"Idempotency is a property of the **pair** — ID scheme and write verb. `createOrReplace` guarantees nothing on its own if the ID changes between runs. Changing the ID format mid-migration is changing a primary key, and the reconciliation is part of that change, not something you discover afterwards."*

**Then the redemption**, because the prefix was right: `_id match "wix-*"` gives provenance (which posts are migrated versus hand-authored — a distinction you can't reconstruct later), and it scopes destructive queries so `backfill-images.js` physically cannot touch a hand-written post. *"It should have been there from commit one. Cheap at the start, expensive to retrofit."*

---

### Q4. [Advanced] 🔥 How do you convert between two rich-text formats?

**Strong answer covers the shape of the problem first:** Wix stores an arbitrarily-nested tree of typed nodes; Portable Text is a **flat array** of blocks. Everything follows from that mismatch.

**The strategy:**

```js
// Recurse into container nodes (BLOCKQUOTE, lists, COLLAPSIBLE, etc.)
if (node.nodes?.length && !["PARAGRAPH", "HEADING"].includes(node.type)) {
  blocks.push(...(await toPortableText(node.nodes)));
}
```

Anything that isn't a paragraph or heading but has children gets recursed into, and the result is spliced flat. A `BLOCKQUOTE > PARAGRAPH > TEXT` becomes a plain paragraph. The exclusion list stops paragraphs being processed twice.

**What it buys:** unknown node types degrade gracefully — Wix could add a `TABLE` tomorrow and the words inside still come through. **Against a format you don't control, preserving the text and losing the wrapper is the right default.**

**What it costs, and say it:** *"Every blockquote in 434 posts is now an ordinary paragraph and every bulleted list is a run of paragraphs. That was a deliberate trade for a blog that's mostly prose — if the source had been documentation full of nested lists and tables, the same choice would have destroyed it."*

**And the loss worth owning:** *"The bigger one is links. I mapped bold, italic and underline and dropped `LINK`, because Portable Text needs a `markDefs` entry on the parent block plus a `_key` reference in the span — more work than pushing a string. **Every hyperlink in 434 posts is now plain text.** It's also the most recoverable loss, since Wix still has the source; a repair script could re-fetch and patch `body`. I'd put that on the handover list rather than let someone find it in a year."*

---

### Q5. [Intermediate] 🔥 How do you make a destructive script safe to run?

**Strong answer covers the template**, but lead with the one that shows judgement:

```json
"dedup":       "bun run src/dedup.js --dry-run",
"dedup:apply": "bun run src/dedup.js"
```

**The short, obvious, easy-to-type name is the safe one.** Destroying data requires typing `:apply`. *"That's five extra characters that exist purely to make you mean it. The default must be safe and the dangerous thing must be the one you go out of your way to ask for."*

Then the rest:

- **Print before/after for every change, in both modes** — so the dry run is a faithful preview and the real run leaves a transcript. **A dry run that takes a different code path is a dry run that lies.**
- **`useCdn: false`** — never decide what to delete from a cache.
- **A query that defines the work set as narrowly as possible.** `backfill-images.js` fetches `*[_type == "post" && _id match "wix-*" && !defined(coverImage)]` — the loop then physically cannot touch anything else. **Safety lives in the query, not in the loop.**
- **A backup first.** `sanity dataset export` → 70MB, taken before the first destructive run.
- **Deterministic choices** — the dedup survivor rule gives the same answer twice, otherwise the dry run means nothing.

---

### Q6. [Advanced] 🔥 There's a subtle bug class in the dedup script's grouping. What is it?

```js
const key = post.slug || `__no-slug__${post._id}`;
```

**Strong answer:** **null must not become a bucket.** Without that sentinel, every post lacking a slug groups under the key `undefined`, becomes one large "duplicate" group, and the script **deletes all but one of them.**

*"Whenever you group records by a nullable field, the null case needs its own unique key. It's a bug class, not a one-off — and in a script whose next action is `delete`, it's the difference between a cleanup and an incident."*

**Bonus if you want to go further:** grouping by *slug* rather than `_id` is itself the right call — two documents with different IDs are different documents to the database, but what makes them duplicates is that they'd serve the same URL. **Group by the thing that defines identity for the user.**

---

### Q7. [Intermediate] 🔥 Why bound concurrency, and how?

**Strong answer covers the why first:** unbounded `Promise.all` over 434 posts opens 434 simultaneous image downloads plus 434 uploads — rate limits, socket exhaustion, or hundreds of image buffers in memory.

The limiter is 25 hand-rolled lines: a counter of in-flight tasks and a FIFO queue, where **`.finally()` decrements and calls `run()` again**, so a completing task pulls the next off the queue.

**Two details that make it correct**, and knowing them is the point:

- **`.finally()` runs on both paths**, so a *failed* task still frees its slot. Get that wrong and one failure permanently reduces your concurrency; get it wrong enough and it deadlocks.
- **`.then(resolve, reject)` rather than `.then(resolve).catch(reject)`** — the two-argument form doesn't catch an error thrown by `resolve`.

**Be honest about the build-vs-buy:** *"Writing my own concurrency primitive deserves more scepticism than it usually gets. It was defensible here — the script runs under `bun` outside the app's dependency graph, and 25 lines is small enough to verify by reading. But `p-limit` is 20 lines of *tested* code, and the failure mode of a subtly broken limiter is a deadlock at post 300 of 434."*

---

### Q8. [Intermediate] How do you know the migration actually worked?

**Strong answer covers:** a structured JSON report written on every run:

```json
{ "total": 434, "skipped": 208, "failedCount": 0, "failed": [] }
```

It does four jobs: **retry input** (`--retry` reads the failed IDs back as the next run's work list), audit trail, verification baseline (compare against `count(*[_type == "post"])` in Vision), and handover document — *"the number in my handover notes came from that file, not from memory."*

**What makes a report useful rather than decorative:** structured JSON so code can read it; `failed` entries carrying `{id, title, error}` so you can retry *and* diagnose; pretty-printed because a human reads it.

**What's missing, and volunteer it:** *"No timestamp and no record of the arguments. Each run overwrites the last, so I can't tell whether that report was the third run or the tenth, or whether it was a `--force` run. One line — a date in the filename — and there's a real trail."*

---

### Q9. [Advanced] 🔥🔥 What would you do differently?

**Have three, ordered by value.**

**1. Test the pure transforms.** *"`toPortableText`, `resolveWixUrl`, `findFirstImageUrl` and the dedup grouping are all pure functions, and I had real fixtures sitting in a file of saved API responses. I ran them destructively across 434 records without a single assertion. `bun test` is built in — there was no setup cost to skip."*

**2. Reconcile the count before transforming.** *"Three lines:*

```js
if (posts.length !== reportedTotal)
  throw new Error(`Fetched ${posts.length} of ${reportedTotal} — refusing to continue`);
```

*My first script assumed cursor pagination against an API that uses offsets, so it fetched one page and reported success. **A bug that under-fetches is invisible** — no error, just less data. That check turns it into a loud failure."*

**3. Decide the ID scheme up front, and write the field mapping down before writing code.** *"The mapping table is where the real decisions are — including the two I punted: Wix category UUIDs, so all 434 posts are `category: "news"` and the blog's category filter is effectively useless, and Wix `memberId`s, so everything points at one default author. Both are recorded in a comment at the line that made the choice, which is the part I'd keep."*

---

### Q10. [Advanced] Three near-identical copies of `resolveWixUrl` exist. Isn't that a DRY violation?

**A trap question — don't just agree.**

**Strong answer:** *"It is duplication, and I think it was the right call. These are throwaway operational scripts with different lifetimes — each runs a handful of times and then never again. Extracting a shared module would couple them: a change made for the backfill could break the main import, and **the main import already ran successfully against real data, so the last thing I want is to touch it.** Duplication is cheaper than coupling when the copies have different lifetimes."*

**Then the limit**, so it doesn't read as a rationalisation: *"The cost is real — a bug found in one copy gets fixed in one copy. The line where it stops being acceptable is roughly the fourth copy, or the first time someone has to edit two of them for the same reason. And it's a judgement I'd make differently for application code, where the copies live forever and change together."*

## Related
- [[projects/munakalati/learning/05-migration/README|learning/05-migration]]
- [[concepts/04-best-practices/06-data-migrations|the general playbook]] · [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]]
