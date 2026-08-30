# Repair Scripts — Fixing Data After It's Landed

**Split from:** the munakalati migration domain. **See also:** [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|03 — idempotency]] · [[projects/munakalati/learning/06-bugs-and-postmortems|06 — postmortems]]

Three scripts, ~90 lines each, each fixing one class of damage the main import left behind. **They share one template, and that template is the reusable thing.**

---

## The template

Every one of `dedup.js`, `fix-slugs.js` and `backfill-images.js` has the same seven-step skeleton:

```js
// 1. Header comment: what's broken, why, and how to run it
// Remove duplicate Sanity posts created by the old wix-blog-migrate.js script.
// The old script used _id: <wixId> (raw UUID). The current migration.js uses _id: wix-<wixId>.
// Running both left every post duplicated under two different IDs.
// Run: bun run src/dedup.js [--dry-run]

// 2. Config from env, asserted up front
const PROJECT_ID = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID;
const SANITY_TOKEN = process.env.SANITY_API_TOKEN;
if (!PROJECT_ID || !SANITY_TOKEN)
  throw new Error("Missing NEXT_PUBLIC_SANITY_PROJECT_ID or SANITY_API_TOKEN");

// 3. A write client with useCdn: false
const sanity = createClient({ projectId, dataset, apiVersion, token, useCdn: false });

async function run() {
  const dryRun = process.argv.includes("--dry-run");     // 4. dry-run flag

  const docs = await sanity.fetch(`*[...]{ ... }`);      // 5. find the damaged set
  const toFix = docs.filter(/* the predicate */);

  if (toFix.length === 0) {                              // 6. exit early, say so
    console.log("✅  No encoded slugs found — nothing to do.");
    return;
  }

  for (const doc of toFix) {
    console.log(`  Before: ...\n  After:  ...`);         // 7. print the change first
    if (!dryRun) await sanity.patch(doc._id).set({ ... }).commit();
  }
}

run().catch((err) => { console.error("💥 Fatal:", err.message); process.exit(1); });
```

**That header comment is doing more work than it looks.** Six months later, `dedup.js` is a mystery — *why* were there duplicates? The comment answers it in three lines, at the only place someone will definitely look. A repair script is by nature a response to a specific incident; **without the incident written down, the script is unreadable and undeletable** — nobody can tell whether it's still needed.

## `--dry-run` is the non-negotiable part

```js
const dryRun = process.argv.includes("--dry-run");
```

```json
"scripts": {
  "dedup": "bun run src/dedup.js --dry-run",
  "dedup:apply": "bun run src/dedup.js",
  "fix-slugs": "bun run src/fix-slugs.js --dry-run",
  "fix-slugs:apply": "bun run src/fix-slugs.js"
}
```

**Look at which way round the npm scripts are.** The short, obvious, easy-to-type name — `bun run dedup` — is the *safe* one. Destroying data requires typing `:apply`, five extra characters that exist purely to make you mean it.

That's a deliberate ergonomic decision and it's the right one. **The default must be safe; the dangerous thing must be the one you go out of your way to ask for.** Compare the alternative, where `bun run dedup` deletes 434 documents and `bun run dedup:dry` previews — same functionality, one accidental tab-completion away from disaster.

`process.argv.includes("--dry-run")` is about as simple as flag parsing gets. No `yargs`, no `commander`. For a script with one or two boolean flags, that's correct — a dependency for this would be silly. It doesn't scale (no `-n` short form, no `--help`, no validation, and a typo like `--dryrun` silently means "apply"), and that last one is the real risk. A `--dry-run`-by-default script with an explicit `--apply` flag would be safer still, because a typo then fails *safe*.

**Print the change before making it**, in both modes:

```js
console.log(`  ${post._id}`);
console.log(`    Before: ${post.slug}`);
console.log(`    After:  ${decoded}\n`);

if (!dryRun) await sanity.patch(post._id).set({ slug: { _type: "slug", current: decoded } }).commit();
```

Same output whichever mode you're in, so the dry run is a faithful preview and the real run leaves a transcript. **The dry run must exercise every line except the write** — a dry run that takes a different code path is a dry run that lies to you.

## `dedup.js` — group, choose a survivor, delete the rest

The interesting part is the choice of survivor:

```js
// Group by slug; fall back to _id if slug is missing
const bySlug = new Map();
for (const post of posts) {
  const key = post.slug || `__no-slug__${post._id}`;
  if (!bySlug.has(key)) bySlug.set(key, []);
  bySlug.get(key).push(post);
}

for (const [slug, group] of bySlug) {
  if (group.length < 2) continue;

  // Prefer the wix- prefixed ID (from the current migration.js)
  const keeper = group.find((p) => p._id.startsWith("wix-")) ?? group[0];
  const dupes = group.filter((p) => p._id !== keeper._id);
  // ...
}
```

**Group by the thing that defines identity for the *user*, not for the database.** Two documents with different `_id`s are different documents as far as Sanity is concerned; what makes them duplicates is that they'd serve the same URL. The slug is the real key.

**`|| \`__no-slug__${post._id}\`` is the detail that stops a catastrophe.** Without it, every post lacking a slug groups under the key `undefined`, becomes one big "duplicate" group, and the script deletes all but one of them. The sentinel makes each slugless document unique to itself, so it can never be grouped with anything. **Whenever you group records by a nullable field, null must not become a bucket** — this is a bug class, not a one-off.

**`?? group[0]`** is the fallback survivor if no `wix-` prefixed document exists. Combined with the `| order(_createdAt asc)` on the fetch, that means "keep the oldest" — a defensible tiebreak, and importantly a *deterministic* one. A non-deterministic survivor choice makes a dry run meaningless, because the apply run might pick differently.

Deletion is one at a time in a loop, logging each ID. Slower than Sanity's transaction API, and right: you get a per-document record of what went, and an error partway through leaves a comprehensible half-finished state.

## `fix-slugs.js` — the smallest possible script

```js
const toFix = posts.filter((p) => {
  try {
    return decodeURIComponent(p.slug) !== p.slug;
  } catch {
    return false;
  }
});
```

The entire detection logic: **if decoding changes it, it was encoded.**

**The `try/catch` matters.** `decodeURIComponent` throws `URIError` on a malformed sequence — a lone `%` , or `%zz`. One bad slug in 434 would crash the whole script partway through, leaving the dataset half-fixed. Catching and returning `false` means "can't decode it, leave it alone", which is the right conservative behaviour for a repair tool.

**The bug it fixes** — the full story is in [[projects/munakalati/learning/06-bugs-and-postmortems|06]] — is that Wix stores slugs for non-English titles percent-encoded (`l%C3%A9ducation-des-enfants`), so the URL bar showed `%C3%A9` instead of `é` and, worse, Next.js's decoded route param never matched the stored value. Note that `migration.js` now calls `decodeURIComponent(listing.slug)` at build time, so **this script is the retroactive fix for documents imported before that line existed.** The permanent fix and the repair are two different changes; both were needed.

## `backfill-images.js` — the read-first pattern

```js
const missing = await sanity.fetch(
  `*[_type == "post" && _id match "wix-*" && !defined(coverImage)]{ _id, title }`
);
```

**One query defines the entire work set**, and it's tightly scoped:

- `_type == "post"` — only posts
- `_id match "wix-*"` — **only migrated ones.** A hand-authored post deliberately published without a cover is not this script's business. This is where the ID prefix from [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|note 01]] pays for itself.
- `!defined(coverImage)` — only the broken ones
- `{ _id, title }` — only the fields needed; no bodies, no images

**Reading exactly the damaged set, and nothing else, is the safety property.** The loop then physically cannot touch a document outside it. Contrast with a script that fetches all posts and decides inside the loop — one wrong condition and it's rewriting everything.

The script duplicates `fetchWixPost`, `resolveWixUrl`, `findFirstImageUrl`, `uploadImage`, `makeLimiter` and the three-source cover fallback from `migration.js`, near-verbatim. Roughly 100 duplicated lines with a comment admitting it: *"Try three sources in order (mirrors migration.js buildDoc logic)"*.

**Is that acceptable?** Genuinely, mostly yes, and it's worth being clear why rather than reflexively calling it a DRY violation. These are throwaway operational scripts, each meant to run a handful of times and then never again. Extracting a shared `wix-client.js` would couple them: a change made for the backfill could break the main import, and the main import already ran successfully against real data — you do not want to touch it. **Duplication is cheaper than coupling when the copies have different lifetimes.**

The cost is real though: `resolveWixUrl` exists twice, so a bug found in one is fixed in one. The line where it stops being acceptable is roughly the fourth copy, or the first time someone edits both.

## Where these scripts fall down as a handover artifact

Two structural problems, both discovered by reading `.gitignore`:

**`migration.js` and `backfill-images.js` are gitignored.** Lines 51 and 53 of `.gitignore` list `migration.js` and `backfill-images.js` with no path, so they match at any depth — including `src/`. `dedup.js`, `fix-slugs.js` and `wix-blog-migrate.js` *are* committed; the two most important scripts are not, and neither is `src/docs.md`. A fresh clone gets a `package.json` with `"migrate": "bun run src/migration.js"` pointing at a file that isn't there. Full detail in [[projects/munakalati/learning/01-git|01 — git]].

**They read `.env`, but the migration needs `.env.migration`.** Both files exist, with different variables commented out — `.env` has the local Sanity project active, `.env.migration` has production active. Nothing in the scripts selects between them; it's `bun`'s automatic `.env` loading plus manual editing of which lines are commented. That's a foot-gun: the difference between pointing a `dedup:apply` at your local dataset and at production is which lines happen to be commented out right now. An explicit `--dataset` argument, or `dotenv -e .env.migration --`, would make the target a visible part of the command.

## The generalisable checklist

For any script that modifies production data:

1. **Header comment** — what broke, why, how to run it.
2. **Assert config at the top**, before any work.
3. **`useCdn: false`** — never decide what to delete from a cache.
4. **A query that defines the work set as narrowly as possible.** Safety lives here.
5. **`--dry-run`, and make it the default in whatever wraps the script.**
6. **Print before/after for every change**, in both modes.
7. **Exit early and say "nothing to do"** when the set is empty.
8. **Deterministic choices** — a survivor rule that gives the same answer twice.
9. **Nulls must not form a group.**
10. **A backup first.** `sanity dataset export` — 70MB well spent.

## Related
- [[concepts/04-best-practices/06-data-migrations|the general playbook]]
- [[devops/01-linux/12-bash-scripting|bash scripting]] — the dry-run/apply flag convention
- [[projects/munakalati/learning/02-shell|02 — shell]]
