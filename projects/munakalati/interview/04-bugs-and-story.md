# munakalati — Bugs, Trade-offs and Project Story

The behavioural half, from [[projects/munakalati/learning/06-bugs-and-postmortems|learning/06]]. **This project's bugs are unusually good interview material because five of the six were silent** — no exception, no failing build, just wrong output that looked right.

---

### Q1. [Advanced] 🔥🔥 Tell me about the hardest bug you debugged.

**The slug encoding saga. Tell it properly — it has a real chain, two wrong-ish fixes, and a general principle.**

**Symptom:** blog posts with French titles 404'd. The URL read `/blog/l%C3%A9ducation-des-enfants` instead of `/blog/léducation-des-enfants`, and the post was visibly in Sanity.

**The chain:**

1. Wix stores the slug for a non-ASCII title **already percent-encoded**, so `slug.current` in Sanity contained the encoded string as literal text.
2. The browser requests the encoded URL — correct; non-ASCII bytes must be encoded on the wire.
3. **Next.js decodes the route param**, handing the page `"léducation-des-enfants"`.
4. Sanity holds `"l%C3%A9ducation-des-enfants"`. No match. 404.

**The insight to lead with:** *"Two layers were each doing the right thing individually and disagreeing about what the value **is**. Next decodes because decoded is what application code wants. Wix encoded because URL-safe is what a URL wants. Neither is wrong — nobody owned the seam."*

**Fix attempt 1** — query for the decoded form, fall back to `encodeURIComponent(slug)`. It worked, and it was wrong: it **enshrined the bad data**. The Studio still showed `%C3%A9`, an editor copying the slug got a double-encoded URL, and every future consumer would have to know the quirk. *"Every read path pays forever for a write path that was wrong once."*

**Fix attempt 2** — three coordinated changes: `decodeURIComponent` in the migration so new imports are clean; `fix-slugs.js` to repair the existing 434; and normalise on read *towards decoded*.

**The detail that makes this a strong answer:** *"The direction matters, and it isn't arbitrary. `decodeURIComponent` is **idempotent** for already-decoded strings — decoding `"hello"` gives `"hello"`. `encodeURIComponent` is not: `%C3%A9` becomes `%25C3%25A9`. So normalising towards decoded is safe whichever form arrives, and normalising towards encoded would have been a trap. **Normalise at the boundary, in the idempotent direction.**"*

**And the safety detail:** the decode is wrapped in `try/catch`, because `decodeURIComponent("%zz")` throws `URIError` — uncaught in a Server Component that's a 500 on a malformed URL, trivially triggerable by anyone typing a stray `%`. The catch turns it into a normal 404.

---

### Q2. [Advanced] 🔥🔥 Tell me about a bug that produced no error at all.

**Two good ones — pick by what the interviewer seems to want.**

**The pagination bug (data-flavoured).** The first migration script assumed cursor pagination: `cursor = data.meta?.nextCursor`. The Wix endpoint uses **offset** paging and returns `metaData.count/offset/total` — no cursor. `undefined` ended the loop after one iteration. The script fetched one page of 434 posts and **reported success.**

*"That's the whole class: a bug that under-fetches is invisible. No exception, no warning, a clean report — just less data than there should be. Truncated pagination, a `LIMIT` left in from development, a filter that's too narrow, an API silently capping page size. The only defence is reconciliation: assert your count against the source's own reported total before you transform anything."*

**Then the sharp observation:** *"`?.` isn't free. Optional chaining on a field I **assumed** existed turned what would have been a `TypeError` pointing straight at the problem into `undefined` flowing quietly onward. It's the right tool for genuinely optional fields and a silencer on fields you believe are mandatory."*

**The `fetch` bug (platform-flavoured).** The same script never checked `res.ok`:

```js
const res = await fetch(url, { headers });
const data = await res.json();              // parses the *error* body happily
posts = posts.concat(data.posts || []);     // undefined → [] → silence
```

**`fetch` rejects only on network failure.** A 401 resolves normally. *"And the fix wasn't just adding the status check — it was putting `await res.text()` **in the error message**. `Wix 401` is a dead end; `Wix 401: {"message":"RICH_CONTENT fieldset requires elevated permissions"}` is a fix. That message is what told me some posts need elevated permissions for their body but not their metadata, which led directly to the fallback that let all 434 import with metadata even when the body was forbidden."*

---

### Q3. [Intermediate] 🔥 You shipped a change that broke six links. What happened?

**Own it cleanly, then generalise.**

Renaming `resources/` to `_resources/` un-routed the section. Six `<Link href="/resources/...">` elsewhere became 404s. The commit updated the Navbar — the obvious place — and stopped.

**The interesting half:** the follow-up commit also fixed `/donate` → `/engage/donate` and `/engage#partner` → `/engage/partner`, **broken by an earlier restructure and unnoticed for weeks.**

*"That's the real lesson. A broken internal link produces no error anywhere — no build failure, no console warning, no exception. It fails only in a human's browser, only if that human clicks it. **`href` is an untyped string and it's the largest unchecked surface in a Next.js app.**"*

**Three fixes, in order of value:**

1. `typedRoutes: true` in `next.config.ts` — generates a union of valid routes, so an invalid `href` is a **compile error**. One line.
2. `grep -rn 'href="/resources' src` before and after a rename.
3. A link checker in CI for what typing can't catch — external links, hrefs built by concatenation.

**And the good judgement to point out:** the fixes weren't mechanical. "Media Library" went to `/blog`, "Publications" to `/our-work/magazine` — *"each redirected to the closest surviving thing the user actually wanted, not all to the homepage."*

---

### Q4. [Advanced] 🔥 What's the pattern across your bugs on this project?

**This is the question that separates a good candidate from a good engineer. Have the answer ready.**

> *"Five of six were silent. A decoded/encoded mismatch showed up as a 404 that looked like missing content. A renamed route showed up as a link that just didn't work. A changed ID scheme showed up as duplicates that looked like a content problem. A missing cursor field showed up as a smaller dataset that looked like a smaller dataset. An unchecked status code showed up as an empty import that reported success.*
>
> *That isn't coincidence — it's what bugs in content and data-pipeline code **are**. There's no crash because nothing is technically wrong; the code did what it said. And the defences are correspondingly unglamorous and cheap: check the status code, reconcile the count, type the routes, assert before you write, log when a fallback fires.*
>
> ***Not one of those bugs needed a debugger. All of them needed something to have been asserted earlier.***"

---

### Q5. [Intermediate] 🔥 Defend a technical decision someone might criticise.

**Best option: the CMS fallback pattern.** Every section keeps hardcoded content and uses it when Sanity returns nothing.

**The criticism:** content in two places, only one obviously authoritative. Nothing flags divergence when an editor updates a testimonial in the Studio and the JSX still has the old one.

**The defence:** *"The site was designed and built before the CMS existed, and the client would populate content later — which is the normal ordering, because you can't model content that doesn't exist yet and stakeholders approve a page, not a schema. The fallback decoupled frontend work from content entry so neither blocked the other, made every page always renderable, and meant a fresh clone with no credentials still renders the whole site."*

**The concession, which is what makes it credible:** *"And the failure mode is genuinely bad. If a query breaks, the page renders the fallback perfectly with no error — you lose the CMS integration and everything looks fine. **The safety net hides the fall.** A `console.warn` when the fallback fires would have cost one line and converted a silent failure into a visible one. That's the change I'd make."*

---

### Q6. [Intermediate] Tell me about dead code you left behind.

**Answer honestly; the reflection is the point.**

Nine components exist twice — `home/Hero.tsx` and `home/cms/Hero.tsx`, and so on. The originals are hardcoded, the `cms/` ones fetch from Sanity, and the homepage imports the `cms/` ones. **The originals are dead.**

*"Keeping the old one alongside the new is a sensible way to do a risky conversion — you can diff them, and you revert by changing an import. The problem is that nothing in `home/Hero.tsx` says 'superseded'. Someone opens it, edits the headline, and nothing happens on the site. That's a genuinely confusing half-hour I've now handed to whoever comes next."*

**The generalisation:** *"**A scaffold needs a demolition date.** 'Keep it around during the migration' is right; 'during' has to end. If you can't delete it the day the switch flips, the deletion goes in the tracker alongside the migration itself."*

---

### Q7. [Intermediate] 🔥 What's in your repo that shouldn't be, or isn't and should be?

**A strong, specific answer that shows you audit your own work.**

*"Three files aren't in the repository at all: `src/migration.js`, `src/backfill-images.js` and `src/docs.md` — the 414-line migration, the image backfill, and my saved Wix API responses. They're gitignored."*

**Why:** `.gitignore` lists `migration.js` and `backfill-images.js` with no leading slash. **A pattern with no slash matches at every level of the tree**, so it caught `src/migration.js` too. The run reports and the 70MB dataset export genuinely should be ignored; the script names got added to the same block and nobody revisited it.

*"So a fresh clone gets `package.json` with `\"migrate\": \"bun run src/migration.js\"` pointing at a file that doesn't exist — while the **obsolete** first attempt at the same job is committed and present."*

**The tool that found it:** `git check-ignore -v src/migration.js` prints the file, line number and text of the rule that matched. *"It turns 'why won't git add this' from a guessing game into a one-liner, and I'd now run `git status --ignored` on any repo I inherit."*

**What the repo got right, for balance:** no secrets tracked — `.env*` is ignored, both env files hold a live Sanity token and Wix API key, and neither has ever been committed. And the 70MB export was ignored from the start, which is the only easy time; once a blob is in history, `git rm` doesn't remove it.

---

### Q8. [Beginner] 🔥 What was the hardest non-technical part?

**Good honest answers, pick one:**

**Scoping for an MVP.** *"The Resources section was four finished pages, and the call was to launch without it. Rather than delete or branch it, I renamed the folder with a leading underscore so Next excludes it from routing — the code stays in `main`, compiles, and restoring it is a rename plus two nav links. The commit message says exactly that. **A reversible change is worth much more when the reversal is written down.**"*

**Deciding what not to migrate.** *"Wix categories are UUIDs into a separate collection and Wix authors are member IDs the API key may not even reach. Mapping either would have meant a second extract and a decision table. I punted both — every post landed as `category: "news"` with one default author — and wrote the reason in a comment on the line that made the choice. The cost is real: the blog's category filter is effectively useless until someone does it by hand. **A migration where every field maps cleanly is one you didn't look at hard enough** — the skill is deciding explicitly what you're dropping and recording why."*

---

### Q9. [Intermediate] Talk about working with the other contributor.

**Strong answer covers:** 45 commits, two authors, one branch, two remotes (the client's org plus a personal mirror). Two merge commits, both from `git pull` reconciling parallel work on `main`.

**What you'd change**, which is the substance:

*"Those merges are 'sync merges' — nothing was being integrated in the sense of a feature landing; two people had committed to `main` and git had to reconcile. `git pull --rebase` (or `git config pull.rebase true`) keeps that history linear. **A merge commit should record a decision to integrate something, not the accident of two people pushing the same afternoon.**"*

*"And my commit messages drifted. 28 of 45 follow Conventional Commits, and the non-conforming ones are all at the recent end — the convention held while things were calm and lapsed under deadline. That's the normal direction, and it's also the argument for a `commit-msg` hook running commitlint: a hook enforces on the bad weeks, which is the only weeks it matters."*

---

### Q10. [Advanced] 🔥 If you had another two weeks, what would you do?

**Ordered, with reasons — not a wish list.**

1. **Tests for the pure transform functions.** *"`toPortableText`, `resolveWixUrl`, `findFirstImageUrl`, the dedup grouping — all pure, and the fixtures already exist in my saved API responses. This is the gap that most changes how the next migration goes."*
2. **`typedRoutes: true`.** One line; the entire `/resources` 404 class becomes a compile error.
3. **Sanity TypeGen.** Deletes the hand-written types, kills the `Parameters<typeof PortableText>[0]["value"]` cast, and turns "this projection doesn't select `author`" into a type error.
4. **Husky + lint-staged + CI.** *"`tsc --noEmit` and eslint on pre-commit and on push. **The point is the ratchet, not the checks** — the standard has to hold on the weeks when attention doesn't, which is exactly when the commit convention slipped and the broken links landed."*
5. **Webhook revalidation instead of 60-second ISR.** Instant publishing, and the first genuinely distributed piece in the project — a callback from another service, a shared secret, signature verification, an idempotent handler.

**Then the one-sentence close:** *"And I'd fix the featured post appearing twice on page one of the blog, which is a one-line bug I found while writing my handover notes and haven't shipped."*

---

### Q11. [Beginner] Why should we care about a marketing site?

**Reframe, don't apologise.**

> *"You shouldn't, particularly — the site is conventional and well-built and that's all. **What's worth talking about is that it was a content-migration project wearing a website's clothes.** 434 records out of a system that didn't want to give them up, an API whose docs didn't match its responses, two rich-text formats that disagree about nesting, and an import that had to survive being re-run a dozen times against production data with no way to undo it except a 70MB tarball I'd taken beforehand. That's the part I'd want to be asked about."*

## Related
- [[projects/munakalati/learning/06-bugs-and-postmortems|learning/06 — the full postmortems]]
- [[projects/munakalati/learning/07-study-path|learning/07 — study path]]
- [[projects/gees-arise/interview/04-bugs-and-story|gees-arise — the other bugs-and-story bank]]
