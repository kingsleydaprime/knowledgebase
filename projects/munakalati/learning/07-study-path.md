# Study Path — What Munakalati Taught, and What to Learn Next

**Closing note for [[projects/munakalati/learning/README|munakalati]].** Written at handover: what this project actually exercised, where it was thin, and the specific next things worth learning from here.

---

## What this project genuinely exercised

**Content modelling as a discipline of its own.** Not database design (no joins, no transactions, no normalisation pressure) and not component design — a third thing: deciding what an *editor* should be able to change, and how much presentation is allowed to live in the content layer. The `headlineStart`/`headlineHighlight`/`headlineEnd` split and the `bgColor` field are both defensible and both debatable, and being able to argue either side is the skill.

**Moving data between two systems that disagree.** The migration is the strongest thing in this project. 434 records, an API whose documentation didn't match its responses, two incompatible rich-text formats, and idempotent bulk writes that had to survive being re-run a dozen times. Most developers do this once and never write down what they learned.

**Server-first rendering at a scale where it matters.** Five client components in a ~10,000-line app. Nearly every page ships zero JavaScript.

**Reading a codebase you're about to leave.** Writing these notes surfaced two dead queries, nine duplicated components, a live pagination bug and three gitignored files — none of which were visible from inside the day-to-day work.

## What it did *not* exercise — the honest gaps

**No tests. None.** No unit tests, no integration tests, no e2e. For a migration in particular this is the sharpest gap: `toPortableText` is a pure function from a Wix node tree to Portable Text, which is the most testable function imaginable, and one that ran destructively across 434 records without a single assertion.

**No CI.** Nothing runs typecheck or lint on push. A broken build reaches production unless someone remembers.

**No auth, no roles, no user data.** Everything is public content. Sanity's Studio login is the only authentication anywhere.

**No relational thinking.** One reference (`post → author`), and the migration pointed all 434 at a single default author. No joins, no cascades, no integrity constraints.

**No observability.** No error tracking, no logging, no analytics. The CMS-fallback pattern means a broken query is invisible *by design*, and there's nothing that would surface it.

## The five things to do next, in order

Ranked by value-per-hour for the skills, not by what the site needs.

### 1. Write tests for the pure transform functions — *highest value, smallest effort*

`toPortableText`, `wixMarks`, `resolveWixUrl`, `findFirstImageUrl` and the `dedup` grouping logic are all pure functions with real inputs sitting in `src/docs.md`. This is the ideal first testing exercise because the fixtures already exist:

```js
test("wix:image:// URIs resolve to the public CDN", () => {
  expect(resolveWixUrl("wix:image://v1/abc~mv2.jpg/photo.jpg#originWidth=1000"))
    .toBe("https://static.wixstatic.com/media/abc~mv2.jpg");
});

test("nested blockquotes flatten to paragraphs, preserving text", () => { /* … */ });

test("null slugs never group together", () => { /* the dedup sentinel */ });
```

`bun test` is built in — no config, no runner to install. **Do this one first.** It's the gap that most changes how the next migration goes.

### 2. Turn on `typedRoutes`

```ts
// next.config.ts
const nextConfig: NextConfig = { typedRoutes: true, /* … */ };
```

One line, and the entire `/resources` 404 cascade becomes a compile error. The best return on effort in this whole list.

### 3. Adopt Sanity TypeGen

```bash
npx sanity typegen generate
```

Deletes `types.ts` as a hand-maintained file, kills the `Parameters<typeof PortableText>[0]["value"]` cast, and turns "this projection doesn't select `author`" into a type error. Every query already carries the `groq` tag TypeGen needs.

### 4. Add Husky + lint-staged + CI

`tsc --noEmit` and `eslint` on pre-commit, the same two on push via GitHub Actions. **The point is the ratchet, not the checks** — the standard has to hold on the weeks when attention doesn't, which is precisely when the commit-message convention here slipped and the broken links landed.

### 5. Replace ISR polling with webhook revalidation

A Sanity webhook → a Next route handler → `revalidateTag()`. Content updates instantly instead of within 60 seconds, and it's the first genuinely *distributed* thing this project would contain: a callback from another service, needing a shared secret, signature verification, and an idempotent handler. Good ground for [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency]] in a setting that isn't a script.

## Where to go for the general versions

| From this project | The course |
|---|---|
| Sanity, GROQ, Portable Text | [[frontend/frameworks/sanity/README|frontend/frameworks/sanity/]] |
| Content modelling as a concept | [[frontend/04-state-and-data/03-content-modeling-and-headless-cms|content modeling and headless CMS]] |
| The migration playbook | [[concepts/04-best-practices/06-data-migrations|concepts/04 — data migrations]] |
| App Router, RSC, ISR | [[frontend/frameworks/next/README|next/]] · [[frontend/02-rendering/README|rendering]] |
| Ops-script conventions | [[devops/01-linux/12-bash-scripting|bash scripting]] |
| Two remotes, merge hygiene | [[git/08-remotes-and-collaboration|remotes and collaboration]] |
| Retries, backoff, idempotency | [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]] |

## The one-sentence version

**This was a content-migration project wearing a website's clothes** — the interesting engineering was almost entirely in getting 434 records out of a system that didn't want to give them up and into one that models them differently, and the frontend was a well-built but conventional Next.js content site on top of it. Tell it that way.

## Related
- [[projects/munakalati/learning/06-bugs-and-postmortems|06 — bugs and postmortems]] — including the standing-issues table
- [[projects/munakalati/interview/README|the interview bank]]
- [[projects/README|all projects and the domains they exercise]]
