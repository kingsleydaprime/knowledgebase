# Reading a Third-Party API You Don't Control

**Split from:** the munakalati migration domain. **See also:** [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|01 — anatomy]] · [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|03 — idempotency]]

The Wix Blog API is the specific subject, but almost nothing here is Wix-specific. **This is the note about the general skill: extracting data from an API whose documentation is incomplete, whose shapes vary per record, and which you cannot change.**

---

## Step zero: capture the real responses

`src/docs.md` is a file of copy-pasted `curl` commands and their actual JSON responses — list posts, query posts, get one post, and a full post object.

```bash
curl 'https://www.wixapis.com/blog/v3/posts?featured=false&categoryIds=a68da372-...' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: <AUTH>'
```

**Doing this before writing the script is the highest-leverage twenty minutes of a migration.** Reasons, in order of how often they bite:

1. **Documented shapes and real shapes differ.** The docs show `coverMedia.image`; the live responses for this site carry `media.wixMedia.image` and sometimes `heroImage`. You only find that by looking.
2. **A saved response is a fixture.** You can write and reason about the transform against real JSON without hitting the network.
3. **The API can go away.** Once the Wix site is decommissioned, `docs.md` is the only remaining record of what the source data looked like — which matters for anyone auditing the migration later.

**One caveat on this file as it stands:** `src/docs.md` is *gitignored* (see [[projects/munakalati/learning/01-git|01 — git]]), so it exists only on one machine. For a handover artifact, that's the wrong place for it.

The habit to keep: **`curl` the endpoint by hand first, save the output, then write code.** Not "read the docs, write the client, debug against production."

## Pagination: read the response, not the tutorial

```js
// migration.js — the version that works
async function fetchAllPosts() {
  const posts = [];
  const pageSize = 100;
  let offset = 0;
  let total = Infinity;

  while (offset < total) {
    const url = new URL(WIX_BASE);
    url.searchParams.set("paging.limit", String(pageSize));
    url.searchParams.set("paging.offset", String(offset));

    const res = await fetch(url.toString(), { headers: { /* auth */ } });
    if (!res.ok) throw new Error(`List posts failed (${res.status}): ${await res.text()}`);

    const data = await res.json();
    const page = data.posts || [];
    posts.push(...page);

    total = data.metaData?.total ?? page.length;
    offset += data.metaData?.count ?? page.length;

    if (page.length === 0) break;
  }
  return posts;
}
```

There's a comment above it in the source that is the whole lesson:

```js
// The Wix list endpoint uses metaData.count / metaData.offset / metaData.total
// — NOT cursor-based pagination.
```

**The first attempt assumed cursors** (`data.meta?.nextCursor`) because that's the modern convention and what most examples show. Wix uses classic offset paging, and it advertises it in `metaData` — visible in the saved response in `docs.md`. The failure mode was silent: `undefined` cursor ends the `do...while` after one page, no error raised. **A pagination bug that under-fetches looks exactly like a small dataset.**

Four defensive details in the working version, each covering a specific way this goes wrong:

- **`total = Infinity` initially** — the loop must run at least once to learn the real total.
- **`?? page.length` on both reads** — if `metaData` is missing entirely, degrade to "advance by what we got" rather than dividing by `undefined` and looping forever.
- **`if (page.length === 0) break`** — a hard stop independent of the arithmetic. **Every paging loop needs an escape hatch that doesn't depend on the server's own counters being correct**, or a bad `total` becomes an infinite loop hammering someone's API.
- **`new URL()` + `searchParams.set()`** rather than string concatenation — correct encoding for free, and readable.

## `if (!res.ok)` — `fetch` does not throw on HTTP errors

```js
const res = await fetch(url);
if (!res.ok) {
  const body = await res.text();
  throw new Error(`Fetch post ${id} failed (${res.status}): ${body}`);
}
```

**`fetch` rejects only on network failure.** A 401, a 404, a 500 all resolve normally with `res.ok === false`. Skip the check — as v1 did — and `await res.json()` parses the *error* body into `{ message: "..." }`, `data.posts` is `undefined`, `|| []` swallows it, and the script cheerfully reports migrating zero posts.

**Including `await res.text()` in the message is the part people leave out and then regret.** `Wix 401` tells you nothing; `Wix 401: {"message":"RICH_CONTENT fieldset requires elevated permissions"}` tells you exactly what to do next — and in this project it's literally what led to the fallback below. Read the whole error, not the status code → the same habit as [[projects/gees-arise/learning/README|gees-arise]]'s Vercel body-limit and Supabase rate-limit debugging.

## Degrading instead of failing: the 401 fallback

Some posts (drafts, members-only) reject the `RICH_CONTENT` fieldset with a 401 while their metadata is perfectly readable. The fix is a two-iteration loop over the *options*:

```js
async function fetchPost(id) {
  for (const fieldset of ["RICH_CONTENT", null]) {
    const url = new URL(`${WIX_BASE}/${id}`);
    if (fieldset) url.searchParams.set("fieldsets", fieldset);

    const res = await fetch(url.toString(), { headers: { /* auth */ } });

    if (res.status === 401 && fieldset) {
      process.stdout.write(" [retrying without RICH_CONTENT]");
      continue;                       // try the next, less demanding option
    }
    if (!res.ok) throw new Error(`Fetch post ${id} failed (${res.status}): ${await res.text()}`);

    return (await res.json()).post;
  }
}
```

**`for (const x of [best, fallback])` is a neat idiom for "try progressively cheaper options"** — it reads better than nested try/catch and extends to three options by adding an array element.

Note the precision of the guard: `res.status === 401 && fieldset`. Only a 401, and only when there's still a fallback left. A 401 on the *second* pass (no fieldset) means the credentials are genuinely wrong, falls through to the `!res.ok` throw, and fails loudly. **A retry that can mask a real auth failure is worse than no retry** — this one can't.

The product decision embedded here is worth naming: **a post with metadata and no body is better than no post at all.** The title, date, slug and cover image migrate; the body is empty and can be filled in later. Partial success beats an all-or-nothing failure when the alternative is losing the record entirely — but only because it's *visible*: the console prints the retry, so the operator knows it happened.

## Undocumented URL schemes: `wix:image://`

The single most Wix-specific thing in the migration, and a perfect example of the class of problem:

```js
// Wix often returns internal URIs like wix:image://v1/{fileId}/{filename}
// instead of a public https:// URL. Convert them before fetching.
function resolveWixUrl(raw) {
  if (!raw) return null;
  if (raw.startsWith("wix:image://v1/")) {
    const fileId = raw.slice("wix:image://v1/".length).split("/")[0].split("#")[0];
    return `https://static.wixstatic.com/media/${fileId}`;
  }
  return raw;
}
```

An image URL in the content nodes may be `wix:image://v1/abc123~mv2.jpg/photo.jpg#originWidth=1000&originHeight=714`. That is **not a URL any HTTP client can fetch** — it's an internal reference in a custom scheme. Passing it to `fetch` throws, and in v1 that's exactly what happened: the retry loop burned three attempts and logged `❌ Image failed`.

The parse is a small chain worth reading carefully: `.slice(prefix.length)` drops the scheme, `.split("/")[0]` takes the file ID and discards the filename, `.split("#")[0]` strips the `#originWidth=...` fragment (needed because a file ID with no trailing filename still carries the fragment). Then the public CDN pattern is reconstructed.

**How you find something like this:** not in the docs. `backfill-images.js` has a `--debug` flag that exists for exactly this purpose:

```js
if (debugMode) {
  const post = await fetchWixPost(wixId);
  console.log("Raw `media` field from Wix API:");
  console.log(JSON.stringify(post?.media, null, 2));
  console.log("\nAll top-level keys on the post object:");
  console.log(Object.keys(post ?? {}).join(", "));
  return;
}
```

**Fetch one record, dump its actual shape, exit.** `Object.keys()` on the response is the move — it shows you fields the documentation never mentioned, which is how `heroImage` and `media.wixMedia` were found. Building this into the script rather than doing it ad hoc in a REPL means it's still there the next time the shape surprises you.

## Shape variance: three sources for one field

The cover image is the clearest case of "the same logical field lives in different places depending on the record":

```js
// 1. media.wixMedia.image — an explicit cover set in the Wix editor
const imgL = listing.media?.wixMedia?.image;
const imgF = full?.media?.wixMedia?.image;
let coverRaw =
  imgL?.url || (imgL?.id ? `https://static.wixstatic.com/media/${imgL.id}` : null) ||
  imgF?.url || (imgF?.id ? `https://static.wixstatic.com/media/${imgF.id}` : null);

// 2. heroImage — the mobile hero, often set when no explicit cover exists
if (!coverRaw) {
  const hero = listing.heroImage || full?.heroImage;
  coverRaw = hero?.url || (hero?.id ? `https://static.wixstatic.com/media/${hero.id}` : null);
}

// 3. the first IMAGE node anywhere in the body
if (!coverRaw) {
  coverRaw = findFirstImageUrl(full?.content?.nodes || full?.richContent?.nodes || []);
}
```

Three sources, **each checked two ways** (`?.url`, else reconstruct from `?.id`), across **two objects** (the listing entry and the full fetch, which do not carry identical data), with **two possible names** for the body array (`content` vs `richContent`). That is roughly twelve access paths for one field.

It looks like over-engineering and it isn't: **the fallback chain is the empirical record of what the data actually contained.** Each `if (!coverRaw)` was added because a batch of posts came back with no image and someone went and looked. 418 of 433 posts ended up with a cover image; without the chain that number would have been a fraction of it.

The generalisable technique is **`?.` plus `||` chains for progressive fallback**, and — more importantly — *ordering the fallbacks by quality*. The explicit editor-set cover is the best answer, the mobile hero is a decent one, the first body image is a guess. Try them in that order, not in whatever order you discovered them.

`findFirstImageUrl` is the small recursive walk, and it's the right shape for a tree you didn't design:

```js
function findFirstImageUrl(nodes = []) {
  for (const node of nodes) {
    if (node.type === "IMAGE") return node.image?.src?.url || node.image?.url || null;
    if (node.nodes?.length) {
      const found = findFirstImageUrl(node.nodes);
      if (found) return found;
    }
  }
  return null;
}
```

Depth-first, returns on the first hit, `= []` default so a missing `nodes` is a no-op rather than a crash. Note **`node.image?.src?.url || node.image?.url`** — even within one node type, the shape varies. That's Wix's document model having evolved over time, and it's what you should expect from any long-lived content system.

## Related
- [[projects/munakalati/learning/05-migration/04-portable-text-conversion|04 — turning those nodes into Portable Text]]
- [[projects/munakalati/learning/02-shell|02 — shell]] — the `curl` habit
- [[backend/README|backend]] · [[foundations/networking/README|networking]] — HTTP status semantics
