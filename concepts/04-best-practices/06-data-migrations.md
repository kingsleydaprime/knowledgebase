# Data Migrations

**[[concepts/04-best-practices/README|04 — Best Practices]], note 6.** **[Intermediate → Advanced]** `[reference]`

Moving records from one system into another that models them differently. **A task most developers do once, under time pressure, without a playbook** — and then never write down what they learned.

**Worked example:** [[projects/munakalati/learning/05-migration/README|munakalati — 434 blog posts, Wix → Sanity]], where every claim here has a scar attached.

---

## The five phases

They have genuinely different failure modes and different rerun semantics, which is why merging them produces something you can't safely re-run.

| Phase | The question | Typical failure |
|---|---|---|
| **1. Extract** | Can I get **all** the source data out? | silently getting only some of it |
| **2. Transform** | What does a source record *become*? | losing information you didn't decide to lose |
| **3. Load** | Can I write it **idempotently**? | duplicates; overwriting human edits |
| **4. Verify** | Did it land, and is it right? | skipped entirely |
| **5. Repair** | Fix what phase 4 found, without re-running everything | not planned for |

> **Phase 5 always happens.** It is not evidence the migration was done badly. **You cannot know how inconsistent the source data is until you have pulled all of it** — so plan for small, targeted repair scripts rather than treating them as failure.

## Before any code: the mapping table

Source field → target field → **what to do when it doesn't fit**. Writing this out is the actual design work, and it forces the decisions that otherwise get made accidentally at 1am.

> **A migration where every field maps cleanly is one you didn't look at hard enough.**

Decide explicitly what you are **dropping**, and **write the reason at the line that drops it**:

```js
category: "news",   // source categories are UUIDs into another collection — mapping punted, fix in the CMS
```

That comment is what the person asking "why is everything categorised as news?" will find. A punt recorded is a decision; a punt unrecorded is a bug someone else inherits.

## Phase 1 — Extract

**`curl` the endpoint and save the response before you write a client.** Twenty minutes, and it pays three ways: documented shapes and real shapes differ; the saved response becomes your test fixture; and when the source system is decommissioned, that file is the only surviving record of what the data looked like.

**Know your HTTP client's error semantics.** JavaScript's `fetch` **resolves** on 401/404/500 and rejects only on network failure. `axios` rejects by default. Python's `requests` needs `raise_for_status()`. Get this wrong and an error body gets parsed as data:

```js
const res = await fetch(url);
if (!res.ok) throw new Error(`Failed (${res.status}): ${await res.text()}`);
```

**Put the response body in the message.** `401` is a dead end; `401: {"message":"RICH_CONTENT requires elevated permissions"}` tells you what to build next.

**Read the pagination scheme from the actual response, not from convention.** Cursor paging is fashionable; plenty of APIs still use offsets. Assuming the wrong one usually fails *silently* — a missing `nextCursor` field is `undefined`, the loop exits after one page, and the script reports success.

Every paging loop needs a stop condition that doesn't trust the server's counters:

```js
if (page.length === 0) break;
```

**Degrade rather than fail where you can.** Some records may reject the richest fieldset while their metadata reads fine. A record with metadata and no body beats no record — *provided it's visible*:

```js
for (const fieldset of ["RICH_CONTENT", null]) { … if (res.status === 401 && fieldset) continue; … }
```

Note the precision: only that status, and only while a fallback remains. **A retry that can mask a genuine auth failure is worse than no retry.**

## Phase 2 — Transform

**Expect the same logical field in different places on different records.** Build fallback chains, and **order them by quality** — the explicitly-set value first, the approximation last:

```js
let cover = explicit?.url ?? hero?.url ?? firstImageInBody(nodes) ?? null;
```

A chain like that looks like over-engineering and usually isn't: **each link is the empirical record of a batch of records that had nothing in the previous slot.**

**Rich text is the hard part**, and the questions are always the same five:

1. What are the block-level types on each side, and how do they correspond?
2. What are the inline annotations — and do any carry data? *(bold is a flag; **links and footnotes carry payloads and are always the fiddly ones**)*
3. How do embeds work?
4. **What do you do with nesting the target can't express?** Flatten, drop, or approximate — decide deliberately and write it down.
5. What identity does the target require? (stable keys, anchors)

**Convert a handful of representative records and read the rendered output before running the batch.** The expensive version of this task is discovering after importing 434 posts that every list became a wall of text.

**Cleaning vs. data loss — the line:** dropping empty paragraphs is *cleaning* (they carry no information, and every downstream consumer would filter them forever). Dropping links because the renderer is easier without them is *data loss wearing cleaning's clothes*. Both feel identical while you're writing the code at 1am.

## Phase 3 — Load

### Idempotency is a property of a *pair*

**A deterministic ID derived from the source record, plus an upsert.**

```js
_id: `src-${sourceRecord.id}`
await client.createOrReplace(doc);
```

Either alone guarantees nothing: an upsert on a random ID still duplicates, and a deterministic ID with `create` still errors on the second run.

> **An ID scheme is a contract with your own future re-runs.** Changing it mid-migration is changing a primary key. In the worked example it turned 434 records into 868, and the reconciliation cost a whole extra script.

**Prefix the ID with its provenance** (`wix-`, `legacy-`). Three payoffs, all cheap at the start and expensive to retrofit:

- **provenance** — `_id match "src-*"` tells you which records were migrated versus authored natively, a distinction you cannot reconstruct later;
- **safe scoping** for destructive queries, so a repair script physically cannot touch a hand-authored record;
- **collision avoidance** between two ID keyspaces.

### Replace vs. patch — whose edits win

| Verb | Behaviour | Use when |
|---|---|---|
| `create` | fails if the ID exists | a duplicate run should be an error |
| `createOrReplace` | upsert, **replaces the whole record** | re-importing from a source of truth |
| `patch(id).set({…})` | merges named fields only | fixing one field on existing records |

**Replace is correct while the source is authoritative and destructive the moment humans start editing.** Once an editor fixes something by hand, re-running a replace-based import silently discards their work. That's precisely why repair scripts should patch.

### Make reruns cheap

- **A skip condition that tracks the expensive side effect**, not merely "the record exists". If the costly part is downloading and re-uploading images, skip on *"has an image"*.
- Fetch the done-set in **one query into a `Set`**, not one existence check per record.
- **`--force`** to ignore the skip, for when the transform changes.
- **`--retry`** to re-run only the previous failures.

> **If a retry path constructs a *partial* version of the normal input, retried records are second-class in ways nobody notices for months.** Re-fetch the real source record; don't synthesise a stub from your error log.

### Bounded concurrency, always

Never unbounded `Promise.all` over a large list — rate limits, socket exhaustion, hundreds of buffers in memory. **A limit of about 5 is a sane default** for a third-party API you don't own.

Whether you hand-roll the limiter or take the dependency, the correctness details are the same: **a failed task must free its slot** (`.finally`, not `.then`), or one failure permanently reduces concurrency and enough of them deadlock the queue.

### Retry with backoff, and decide what failure *means*

Three attempts with a delay, then **degrade or fail — per failure type, deliberately.** In the worked example an image failure returns `null` (the record still migrates) while a record fetch failure throws (it lands in the failed list). Prefer exponential backoff with jitter over a fixed delay, and **only retry 5xx and 429** — a 404 will not succeed on the third attempt.

## Phase 4 — Verify

**Reconcile the count before you transform anything.** Three lines, and it converts the most common invisible failure into a loud one:

```js
if (fetched.length !== reportedTotal)
  throw new Error(`Fetched ${fetched.length} of ${reportedTotal} — refusing to continue`);
```

**Write a structured report on every run**, not just on failure:

```json
{ "total": 434, "skipped": 208, "failedCount": 0, "failed": [{ "id": "…", "title": "…", "error": "…" }] }
```

It does four jobs: **retry input**, audit trail, verification baseline, and handover document. Include enough per failure to *both* retry and diagnose. **Timestamp the filename** — a report that overwrites itself can't tell you whether it describes the third run or the tenth.

Beyond counts, spot-check: the longest record, the shortest, one with non-ASCII characters, one with no image, the oldest.

## Phase 5 — Repair

Small scripts, one class of damage each. The template that keeps them safe:

1. **A header comment: what broke, why, and how to run it.** Without the incident recorded, the script is unreadable *and* undeletable — nobody can tell whether it's still needed.
2. **Assert config up front**, before any work.
3. **Read live, never from a cache** — deciding what to delete from a stale snapshot is how you delete the wrong thing.
4. **A query that defines the work set as narrowly as possible.** *Safety lives in the query, not in the loop.*
5. **`--dry-run`, and make it the default in whatever wraps the script.**
6. **Print before/after for every change, in both modes.** A dry run that takes a different code path is a dry run that lies.
7. **Exit early and say "nothing to do"** when the set is empty.
8. **Deterministic choices** — a survivor rule that gives the same answer twice, or the dry run means nothing.

> **The default must be safe.** Wire the scripts so `run cleanup` previews and `run cleanup:apply` destroys. Five extra characters that exist purely to make you mean it.

**And one bug class worth memorising: when grouping records by a nullable field, null must not become a bucket.** Give each null its own sentinel key (`__none__${id}`), or every record missing that field groups together as "duplicates" — and the next line is usually `delete`.

## The pre-flight checklist

1. **Take a backup.** A full export before the first destructive run. Cheap; the only alternative to it is hope.
2. **Deterministic, prefixed IDs.** Decided before run one.
3. **Upsert, not insert** — and choose replace-vs-patch by asking whose edits should win.
4. **A skip condition on the expensive step, and `--force`.**
5. **`--dry-run` on anything destructive**, defaulted on.
6. **Bounded concurrency.**
7. **Retries with backoff; a per-failure-type decision to degrade or fail.**
8. **Count reconciliation before transforming.**
9. **A structured, timestamped report the retry path can read back.**
10. **Test the pure transform functions.** They're the most testable code you will write all year, and the fixtures are the API responses you already saved in phase 1.

## Related
- [[projects/munakalati/learning/05-migration/README|munakalati — the worked example]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]] · [[architecture/03-architectural-patterns/02-resilience-patterns|resilience patterns]]
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data and integration patterns]]
- [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modelling]] — designing the target
- [[devops/01-linux/12-bash-scripting|bash scripting]] — the flag conventions
