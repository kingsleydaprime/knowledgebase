# 05 — Migration

**The most distinctive thing [[projects/munakalati/learning/README|munakalati]] taught.** Moving 434 blog posts from Wix to Sanity — extraction from an API you don't control, rich-text conversion between two incompatible tree formats, idempotent bulk writes, and three repair scripts for what the import got wrong.

Almost none of this is Wix- or Sanity-specific. **It's the general skill of moving data between two systems that disagree**, which is one of those tasks that appears once a project and is never taught.

1. [[projects/munakalati/learning/05-migration/01-anatomy-of-a-migration|01 — Anatomy of a Content Migration]] ⭐ — **[Intermediate]** — the five phases, the field mapping table, deliberate punts, **`_id: "wix-" + id` and the 868-post incident**, v1 vs v2 side by side
2. [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|02 — Reading a Third-Party API You Don't Control]] ⭐ — **[Intermediate]** — curl-and-save before you code, **`fetch` doesn't throw on 4xx**, offset vs cursor paging, degrading on 401, undocumented URL schemes, three-source fallback chains
3. [[projects/munakalati/learning/05-migration/03-idempotency-reruns-and-reports|03 — Idempotency, Reruns and Run Reports]] ⭐ — **[Intermediate → Advanced]** — deterministic IDs + upsert, replace vs patch (**whose edits win**), skip-if-done, `--force`/`--retry`, a hand-rolled concurrency limiter read line by line, backoff, reports as retry input
4. [[projects/munakalati/learning/05-migration/04-portable-text-conversion|04 — Converting Rich Text]] — **[Advanced]** — tree to flat array, the recursive flattening strategy and what it costs, **every hyperlink in 434 posts was lost**, cleaning vs. data loss
5. [[projects/munakalati/learning/05-migration/05-repair-scripts|05 — Repair Scripts]] — **[Intermediate]** — the seven-step template, **why `dedup` is the safe name and `dedup:apply` the dangerous one**, null must not form a group, when duplication beats coupling

## The five things to take away

**An ID scheme is a contract with your own future re-runs.** Changing `_id: post.id` to `_id: "wix-" + id` mid-migration turned 434 posts into 868.

**`fetch` resolves on 401.** No status check means error bodies get parsed as data and the script reports success.

**A pagination bug that under-fetches is invisible.** Always reconcile your count against the source's own reported total before transforming anything.

**The default must be safe.** `bun run dedup` previews; `bun run dedup:apply` destroys.

**Phase 5 always exists.** You cannot know how inconsistent the source data is until you've pulled all of it, so plan for repair scripts rather than treating them as evidence of failure.

## Related
- General: [[concepts/04-best-practices/06-data-migrations|concepts/04 — data migrations]]
- [[projects/munakalati/learning/03-sanity/README|03 — Sanity]] — the target system
- [[projects/munakalati/interview/03-migration-and-data-integrity|interview: migration and data integrity]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]]
