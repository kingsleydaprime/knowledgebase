# Idempotency, Reruns and Run Reports

**Split from:** the munakalati migration domain. **See also:** [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|01 — anatomy]] · [[projects/munakalati/learning/05-migration/05-repair-scripts|05 — repair scripts]]
**General version:** [[concepts/04-best-practices/06-data-migrations|data migrations]] · [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]]

---

## The assumption to start from

**A migration script will be run many times.** Not once. It will fail two thirds of the way through on a malformed record; you'll fix the transform and run it again; the API will rate-limit you; you'll add a field and want to re-import just that; you'll run it against staging and then against production.

Everything in this note follows from designing for that from the first line, rather than writing a one-shot script and then discovering it isn't one.

## Idempotency: deterministic IDs + `createOrReplace`

```js
_id: `wix-${listing.id}`
// ...
await sanity.createOrReplace(doc);
```

Two halves of one property:

- **The ID is derived from the source record**, so the same Wix post always produces the same Sanity `_id`. Nothing random, no timestamp, no auto-increment.
- **`createOrReplace` is an upsert.** Create it if absent, overwrite it whole if present.

Together: **running the script N times leaves exactly the same dataset as running it once.** That is idempotency, and in a migration it is the difference between "run it again" and "run it again and then spend an afternoon writing a dedup script".

The three write verbs and when each is right:

| | Behaviour | Use when |
|---|---|---|
| `create` | Fails if the ID exists | You want a duplicate run to be an error |
| `createOrReplace` | Upsert, **replaces the whole document** | Re-importing from a source of truth — the migration |
| `patch(id).set({...})` | Merges specified fields only | Fixing one field on existing docs — the repair scripts |

**`createOrReplace` replacing the *whole* document is the sharp edge.** If an editor manually fixed a post's `category` in the Studio and you re-run the migration, that edit is gone — the script's version wins entirely. That's correct while the source is authoritative and dangerous the moment humans start editing. In this project the transition happened: once the team began fixing categories by hand, re-running `migration.js` became a destructive act.

**That's exactly why the repair scripts use `patch().set()` instead** — `fix-slugs.js` changes `slug` and nothing else, `backfill-images.js` changes `coverImage` and nothing else. Surgical writes leave human edits intact. **Choosing between replace and patch is choosing whose version wins.**

## Skip-if-done: making the expensive part cheap to retry

```js
const doneIds = new Set(
  await sanity.fetch(`*[_type == "post" && defined(coverImage)]._id`)
);
const forceMode = process.argv.includes("--force");
if (doneIds.size && !forceMode)
  console.log(`⏭   ${doneIds.size} post(s) already have a cover image and will be skipped (--force to override)\n`);

for (const listing of listings) {
  const sanityId = `wix-${listing.id}`;
  if (!forceMode && doneIds.has(sanityId)) { skipped++; continue; }
  // ...fetch, transform, upload
}
```

Three things worth extracting:

**One query, not N.** The whole set of already-done IDs is fetched once up front into a `Set`. The alternative — checking existence per post inside the loop — is 434 extra round trips. `Set` lookup is O(1); `Array.includes` in a loop would quietly be O(n²). At 434 that's survivable, at 50,000 it isn't.

**The `._id` at the end of the GROQ is a terse projection** — it returns a flat array of strings, `["wix-abc", "wix-def"]`, rather than objects. Exactly the shape `new Set(...)` wants.

**The skip predicate is `defined(coverImage)`, not "document exists".** That's a deliberate and slightly subtle choice: the expensive part of this migration is downloading and re-uploading images, and a post with a cover image is one where that work completed. A post that exists but has no cover is either genuinely image-less or *failed partway*, and gets retried. The skip condition tracks **the expensive side effect, not the record's existence.**

The cost of that cleverness: 208 of 434 posts were skipped on the final run — and some of them are posts that legitimately have no image on Wix, so they'll be re-attempted on every future run forever. A `migratedAt` timestamp field would separate "done" from "done and produced an image" properly. Fine at this scale; the right fix at a larger one.

**`--force` is the escape hatch**, and it should always exist. When the transform changes — a Portable Text fix, a new field — you need to re-run over everything, skip logic be damned.

## `--retry`: re-running only the failures

```js
if (retryMode) {
  if (!fs.existsSync("migration-report.json"))
    throw new Error("No migration-report.json found — run without --retry first");

  const report = JSON.parse(fs.readFileSync("migration-report.json", "utf8"));
  if (!report.failed?.length) {
    console.log("✅  No failures in migration-report.json — nothing to retry.");
    return;
  }
  // Build minimal listing objects from the report so we can re-fetch by ID
  listings = report.failed.map((f) => ({ id: f.id, title: f.title, slug: f.id }));
  console.log(`🔁  Retrying ${listings.length} failed post(s)…\n`);
}
```

**The report is not just a log — it's an input.** The failed IDs from the last run become the work list for the next. That closes the loop: run, inspect failures, fix the code, `--retry`, repeat until `failed` is empty. Much better than re-scanning 434 posts to find the 6 that broke.

The guard clauses are good practice: a missing report throws a message that tells you what to do, and an empty `failed` array exits cleanly rather than doing nothing mysteriously.

**There is one real bug in it.** The synthesised listing is `{ id, title, slug: f.id }` — but `buildDoc` reads the cover image from `listing.media`, `listing.heroImage`, and `listing.excerpt`, none of which exist on this stub. It also writes `slug: { current: decodeURIComponent(listing.slug) }`, so a retried post gets **its Wix UUID as its slug**. The full fetch supplies the body and some metadata, so a retry isn't useless — but it produces a subtly worse document than a normal run, with a URL nobody would want.

The fix is to re-fetch the listing entry rather than fake it, or to store the whole listing object in the report instead of just `{id, title, error}`. **The general lesson: if a retry path constructs a partial version of the normal input, the retried records are second-class in ways nobody will notice until much later.** Retry with the same data the happy path uses.

## Concurrency: bounded, and hand-rolled

```js
function makeLimiter(concurrency) {
  let active = 0;
  const queue = [];
  function run() {
    while (active < concurrency && queue.length) {
      active++;
      const { fn, resolve, reject } = queue.shift();
      fn().then(resolve, reject).finally(() => { active--; run(); });
    }
  }
  return (fn) => new Promise((resolve, reject) => { queue.push({ fn, resolve, reject }); run(); });
}

const limit = makeLimiter(5);
```

Twenty-five lines replacing the `p-limit` dependency that v1 used. Read it as a state machine: a counter of in-flight tasks and a FIFO queue. `run()` starts tasks while there's headroom; **`.finally()` decrements and calls `run()` again**, so the completion of one task is what pulls the next off the queue. Calling `run()` on every enqueue handles the case where there's headroom already.

The subtleties that make it correct:

- **`.then(resolve, reject)` rather than `.then(resolve).catch(reject)`** — the two-argument form doesn't catch an error thrown *by* `resolve`, keeping rejection semantics clean.
- **`.finally()` runs on both paths**, so a failed task still frees its slot. Get this wrong and one failure permanently reduces your concurrency; get it wrong enough and the queue deadlocks.
- The returned function wraps each task in a promise the caller can await, so `limit(fn)` is a drop-in for `fn()`.

**Why bound concurrency at all** — the reason it's marked *"VERY IMPORTANT for stability"* in v1: unbounded, `Promise.all` over 434 posts opens 434 simultaneous image downloads plus 434 uploads. You will hit rate limits, exhaust sockets, or blow up memory holding hundreds of image buffers. **5 is a reasonable default** — enough parallelism to matter, low enough to be polite to an API you don't own.

**Is hand-rolling it right?** For a script that must run under `bun` outside the app's dependency graph, avoiding a dependency is defensible, and the implementation is genuinely correct. Against: `p-limit` is 20 lines of *tested* code, and the failure mode of a subtly broken limiter (a deadlock at post 300 of 434) is expensive to debug. The honest answer is that it was worth it here because it *works* and it's small enough to verify by reading — but "I'll write my own concurrency primitive" is a decision that deserves more scepticism than it usually gets.

## Retry with backoff

```js
let retries = 3;
while (retries > 0) {
  try {
    // fetch, upload
    return ref;
  } catch (err) {
    retries--;
    if (retries === 0) {
      console.warn(`  ⚠ Image skipped (${url.slice(0, 60)}…): ${err.message}`);
      return null;   // degrade, don't throw
    }
    await new Promise((r) => setTimeout(r, 1500));
  }
}
```

Three attempts, 1.5s apart, then **give up and return `null` rather than throwing** — a post with no cover image still migrates. The choice of what a failure *means* is the design: an image is optional, so it degrades; the post fetch is essential, so it throws and lands in `failed`.

`await new Promise(r => setTimeout(r, ms))` is the standard sleep idiom in JS — there's no built-in `sleep`, and this is what everyone means by one.

**What's missing:** the delay is fixed, not exponential (1.5s, 1.5s), and there's no jitter. Proper backoff doubles (1s, 2s, 4s) with a random offset so that N clients retrying after an outage don't synchronise into a thundering herd. For a single-operator script hitting a big CDN it doesn't matter; **for anything running in production against a rate-limited API it very much does** → [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]].

Also missing: it retries *everything*. A 404 is not going to succeed on the third attempt — retrying only 5xx and 429 would be strictly better and no harder to write.

## Reports: the artifact that makes a run auditable

```js
fs.writeFileSync(
  "migration-report.json",
  JSON.stringify({ total: listings.length, skipped, failedCount: failed.length, failed }, null, 2),
);
```

```json
{ "total": 434, "skipped": 208, "failedCount": 0, "failed": [] }
```

Small, and it does four jobs: it's the **retry input** (above), the **audit trail** (434 posts, we know), the **verification baseline** (compare against `count(*[_type == "post"])` in Vision), and **the handover document** — the number in the notes came from here, not from anyone's memory.

Three things that make a report useful rather than decorative:

- **Structured JSON, not log lines.** It gets read by code.
- **`failed` carries `{ id, title, error }`** — enough to retry *and* enough to diagnose without re-running.
- **`null, 2` pretty-printing** — a human reads this file in an editor. Costs nothing.

What would make it better: a **timestamp and the arguments the run was invoked with**. Right now each run overwrites the last, so there's no history — you can't tell whether `{total: 434, skipped: 208}` was the third run or the tenth, or whether it was a `--force` run. `migration-report-2026-06-25T14-01.json` would cost one line and give a real trail.

## The checklist this all adds up to

Before running any bulk import against real data:

1. **Deterministic IDs** derived from the source. Never random.
2. **Upsert, not insert** — decide replace-vs-patch by asking whose edits should win.
3. **A skip condition** tracking the expensive side effect, and a **`--force`** to ignore it.
4. **`--dry-run` on anything destructive** → [[projects/munakalati/learning/05-migration/05-repair-scripts|note 05]].
5. **Bounded concurrency.** Never unbounded `Promise.all` over a large list.
6. **Retries with backoff on transient failures**, and a decision per failure type about degrade-vs-fail.
7. **A structured report**, written even on success, that the retry path can read back.
8. **A backup taken before the first destructive run** — here, `sanity dataset export` → 70MB `sanity-export.tar.gz`.

## Related
- [[concepts/04-best-practices/06-data-migrations|the general playbook]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]] · [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]
- [[projects/direct-debit-sandbox-java/learning/05-async-scheduling-retry|direct-debit — the same problem in Java]]
