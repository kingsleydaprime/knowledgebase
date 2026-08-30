# 04 — DevOps (env vars, package management, deploy)

Part of the [[projects/kingsley-iheme/learning/README|kingsley-iheme learning log]]. Siblings: [[projects/kingsley-iheme/learning/01-frontend|01-frontend]] · [[projects/kingsley-iheme/learning/02-sanity|02-sanity]] · [[projects/kingsley-iheme/learning/03-backend-api|03-backend-api]].

General reference: [[devops/09-secret-management/README|devops/secret-management]] · [[devops/01-linux/README|devops/linux]] · [[git/README|git]].

---

## 1. The env-var architecture

Seven variables, and each one's *shape* encodes a decision:

```bash
NEXT_PUBLIC_SANITY_PROJECT_ID=      # public — the browser needs it
NEXT_PUBLIC_SANITY_DATASET=production
NEXT_PUBLIC_SANITY_API_VERSION=2024-01-01
NEXT_PUBLIC_CAL_USERNAME=           # public — goes in an iframe URL
RESEND_API_KEY=                     # SECRET — server only
RESEND_FROM_EMAIL=
NEXT_PUBLIC_SITE_URL=               # public — used in metadata/OG/sitemap
```

### `NEXT_PUBLIC_` is a security boundary, and it is not subtle

In Next.js, `NEXT_PUBLIC_`-prefixed variables are **inlined into the client bundle at build time**. Not read at runtime, not fetched — literally string-substituted into the JavaScript downloaded by every visitor.

Two consequences that people get wrong in opposite directions:

**Never prefix a secret.** `NEXT_PUBLIC_RESEND_API_KEY` would ship your mail-sending credential to anyone who opens DevTools. This project gets it right: `RESEND_API_KEY` has no prefix, is read only inside `src/app/api/contact/route.ts` (a server-only Route Handler), and never crosses to the browser. Verify it yourself on any Next project:

```bash
# after a build — anything findable here is public, by definition
grep -ro "NEXT_PUBLIC_[A-Z_]*" .next/static/ | sort -u
```

**Because it's baked in at build time, changing it requires a rebuild.** Updating `NEXT_PUBLIC_SITE_URL` in the Vercel dashboard does nothing until you redeploy. This surprises people who expect env vars to be runtime config. Server-only vars (`RESEND_API_KEY`) *are* read at runtime and do take effect on restart — so the two kinds behave differently, and knowing which is which is the difference between a five-minute fix and an hour of confusion.

**Is the Sanity project ID being public a problem?** No, and it's worth being able to say why rather than just trusting it. A Sanity project ID identifies a dataset; it isn't a credential. Public datasets are readable by design — that's how the site renders. Access control lives in the dataset's visibility settings and in tokens for *writes*. Publishing the ID exposes exactly what the website already publishes. Same for the Cal.com username, which is literally part of a public booking URL.

The general habit: **for each variable, ask "what can someone do with this?"** — not "does it look secret." An ID that names public data is fine. A token that authorises an action is not.

### The `|| ""` default pattern

```ts
export const projectId = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || "";
export const isSanityConfigured = Boolean(projectId);
export const CAL_USERNAME = process.env.NEXT_PUBLIC_CAL_USERNAME || "";
const RESEND_API_KEY = process.env.RESEND_API_KEY || "";
```

Every optional integration follows the same three-step shape: **default to empty → derive a boolean → branch in the UI.** No integration ever throws for being absent; each renders its own "not connected" state ([[projects/kingsley-iheme/learning/02-sanity|02 §4]], [[projects/kingsley-iheme/learning/03-backend-api|03 §4]]).

The trade-off, stated plainly: this is the **opposite** of fail-fast. A typo'd variable name doesn't crash the build — it silently disables a feature, and you find out when a page renders an empty state in production. For a service where a missing database URL should absolutely halt the deploy, you'd want validation at boot instead (the [[projects/strictenv/learning|strictenv]] approach: parse the environment against a schema, throw loudly on startup). Here, "must render correctly with nothing connected" is an explicit requirement, so soft failure is right — but it's a choice with a cost, not a free win.

One place the default is doing more than degrading:

```ts
// src/lib/site.ts
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || "https://kingsleyiheme.com")
  .replace(/\/$/, "");
```

The `.replace(/\/$/, "")` strips a trailing slash. **Anchored to the end (`$`), so it only strips the last one** — `https://x.com/` → `https://x.com`. Without it, every URL built by concatenation (`${SITE_URL}${path}`) would produce `https://x.com//about`. That double slash is technically a different URL: duplicate content for crawlers, broken canonicals, and a class of bug that only shows up in the sitemap and OG tags where nobody looks. Normalising input at the boundary, once, beats defending against it at ten call sites.

---

## 2. 🐛 The bug: `.env.local.example` is gitignored

Found while writing these notes. The README's own setup instructions can't be followed from a fresh clone.

**README step 1.3:**
> Copy `.env.local.example` to `.env.local` and fill in the project ID it gives you

**The `.gitignore`:**
```
# env files (can opt-in for committing if needed)
.env*
!.env.example
```

**The verification:**

```bash
# which env files does git actually track?
git ls-files | grep -i env
# → .env.example
#   src/sanity/env.ts
#   (.env.local.example is absent)

# ask git WHY a path is ignored — prints the rule and line number
git check-ignore -v .env.example .env.local.example
# → .env.local.example  .gitignore:34:.env*
```

`git check-ignore -v` is the tool for exactly this question. It tells you the file, the line number, and the pattern responsible, instead of leaving you to eyeball a `.gitignore` and guess.

**What happens.** `.env*` matches everything env-shaped. `!.env.example` re-includes **exactly one filename** — negation patterns are not prefixes or globs, they match literally what they say. `.env.local.example` matches the ignore rule, matches no negation, stays ignored, was never committed. Clone the repo and the file the README tells you to copy **does not exist**.

The bug is invisible on the machine where it was written, because the file is sitting right there locally. It only manifests for the next person — which is the whole audience for a setup README.

**Three ways to fix it**, best first:

```gitignore
# 1. Delete the duplicate. .env.example alone is enough — point the README at it.
.env*
!.env.example

# 2. Or negate both explicitly
.env*
!.env.example
!.env.local.example

# 3. Or negate the pattern
.env*
!.env*.example
```

Option 1 is right, because the two files are ~95% identical and disagree on exactly one line — `.env.example` hardcodes `NEXT_PUBLIC_SITE_URL="https://kingsleyiheme.com"` while `.env.local.example` leaves it blank. Two near-identical templates that quietly diverge is a maintenance trap, and the one that's tracked is the one that survives.

Whichever fix, the file must actually be added — `.gitignore` doesn't retroactively track anything:

```bash
git add -f .env.local.example    # -f overrides the ignore rule
```

**Generalisable lessons:**
1. **`!` negations match literal patterns, not prefixes.** `!.env.example` does nothing for `.env.local.example`.
2. **A `.gitignore` rule ordering matters** — a negation must come *after* the rule it's undoing.
3. **The real fix is testing the clone.** `git clone` into `/tmp` and follow your own README start to finish. Every "works on my machine" setup bug is caught by that one exercise, and nothing else catches them, because your working directory is full of files you never committed.

---

## 3. Two more housekeeping findings

### `styled-components` is a dependency and is imported nowhere

```bash
grep -rl "styled-components" src/   # → no matches
```

It's in `package.json` `dependencies` alongside Tailwind v4. Almost certainly a leftover from an early direction that was abandoned when the Tailwind approach won — worth confirming against `git log -p package.json` before removing.

Why bother removing an unused dep:

- **It's a real install.** `styled-components` pulls a stylis/babel-plugin tree; it's not free bytes on disk or seconds in CI.
- **It's a lie about the architecture.** The next person reading `package.json` reasonably concludes this project uses CSS-in-JS, goes looking for a `ThemeProvider`, and finds nothing. Dependencies are documentation.
- **It's supply-chain surface.** Every dependency is a package that can be compromised, and one you're not using is pure risk with zero benefit. Also noise in every `bun audit` and Dependabot alert forever.
- **It would be an actual problem if used.** styled-components is a runtime CSS-in-JS library that needs a Client Component boundary and a registry to work with the App Router — mixing it with Tailwind v4 here would be strictly worse than either alone.

```bash
bun remove styled-components
```

Same audit is worth running periodically — `bunx depcheck` finds unused dependencies and missing ones.

### `ignoreScripts` and `trustedDependencies` contradict each other

```json
"ignoreScripts": ["sharp", "unrs-resolver"],
"trustedDependencies": ["esbuild", "sharp", "unrs-resolver"]
```

**`sharp` and `unrs-resolver` are in both lists**, which read as opposite instructions.

The background: package managers run `postinstall` scripts, and arbitrary code execution on `install` is a well-known supply-chain attack vector. Bun's response is **`trustedDependencies`** — an explicit allowlist of packages permitted to run lifecycle scripts. Everything else is blocked by default. That's a genuinely good security posture and it's why the field exists.

`ignoreScripts` as a top-level `package.json` field is **npm/yarn-flavoured config, not something bun reads there** — bun takes `ignoreScripts` via `bunfig.toml` or the `--ignore-scripts` flag, and there's no `bunfig.toml` here (bun 1.3.14). So the likely reality is that the `ignoreScripts` array is inert and `trustedDependencies` is what's actually in force — consistent with `node_modules/sharp` being present and built.

Worth resolving rather than leaving ambiguous, because a reader can't tell which is authoritative:

```bash
# does sharp's native binary actually exist, i.e. did its script run?
ls node_modules/sharp/build/Release/ 2>/dev/null || echo "no native build"
```

If `sharp` is needed (it's Next's image optimiser in some deployment targets — Vercel provides its own, so a local build often isn't required), keep it trusted and drop it from `ignoreScripts`. If it isn't, drop it from both. **Two config fields expressing opposite intentions is worse than either choice**, because the next person changing image behaviour has no idea which one to edit.

---

## 4. bun

```json
"scripts": { "dev": "next dev", "build": "next build", "start": "next start", "lint": "eslint" }
```

`bun.lock` (JSON, `lockfileVersion: 1` — the newer text format, readable in diffs, unlike the old binary `bun.lockb` which produced unreviewable merge conflicts).

```bash
bun install          # install deps
bun run dev          # run a package.json script
bunx sanity login    # run a package binary without installing (npx equivalent)
bun add <pkg>        # add a dependency
bun remove <pkg>     # remove one
```

`bunx` vs `bun run` is the distinction worth keeping straight: **`bun run <script>` executes a script defined in `package.json`; `bunx <binary>` executes a package's CLI**, fetching it if it isn't installed. The README correctly uses `bunx sanity init` for a one-off setup command.

Note **`next dev` is not aliased to Turbopack here** — in Next 16, per the upgrade guide, **Turbopack is the default bundler**, so no `--turbo` flag is needed any more. Another instance of the [[projects/kingsley-iheme/learning/01-frontend|01 §0]] rule: half the Next tutorials online still tell you to add a flag that's now redundant.

The commitment to be aware of: choosing bun means CI, deploy targets, and every contributor need it. Vercel detects `bun.lock` and uses bun automatically, so this is low-friction here — but "the lockfile chooses your CI runtime" is worth knowing before you're debugging a build that installed with npm and produced a different tree.

---

## 5. Deploy target and what's still missing

Vercel. Next.js's own platform, so ISR, `ImageResponse` OG generation, Route Handlers and image optimisation all work with no configuration. The env vars go in project settings — and per §1, **`NEXT_PUBLIC_` ones need a redeploy to take effect**, which is the number-one Vercel confusion.

**Launch checklist gathered across these four notes:**

| Item | Why | Note |
|---|---|---|
| Fix `.env.local.example` being gitignored | Fresh clone can't follow the README | §2 |
| Verified sending domain in Resend (SPF/DKIM) | `onboarding@resend.dev` is a sandbox sender; real mail lands in spam without DNS | [[projects/kingsley-iheme/learning/03-backend-api\|03 §3]] |
| Rate limiting on `/api/contact` | Nothing stops a scripted flood; honeypot is ~5 lines | [[projects/kingsley-iheme/learning/03-backend-api\|03 §3]] |
| `console.error` in `sanityFetch` and the 502 branch | Both currently discard the error; nothing to read in the logs | [[projects/kingsley-iheme/learning/02-sanity\|02 §4]], [[projects/kingsley-iheme/learning/03-backend-api\|03 §4]] |
| `postType == "native"` in `POST_BY_SLUG_QUERY` | `/blog/<external-slug>` renders a bodiless page instead of 404 | [[projects/kingsley-iheme/learning/02-sanity\|02 §5]] |
| Copy fixes in `cal-sessions.ts` | "Invidiual", duplicated description, 15-min individual session | [[projects/kingsley-iheme/learning/01-frontend\|01 §8]] |
| `NEXT_PUBLIC_SITE_URL` set in Vercel | Otherwise canonicals/OG/sitemap use the hardcoded fallback | §1 |
| `bun remove styled-components` | Unused dependency | §3 |
| Reconcile `ignoreScripts` / `trustedDependencies` | Contradictory config | §3 |

**Two things absent that are worth adding**, both standing habits from [[projects/gees-arise/learning/09-sys-design|gees-arise]]:

**CI.** There's a GitHub remote (`main` and `dev` branches, a merged PR in the log) and no workflow running typecheck and lint on push. That's the cheapest possible safety net:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bunx tsc --noEmit
      - run: bun run lint
```

`--frozen-lockfile` is the important flag: fail if `package.json` and `bun.lock` disagree, rather than silently resolving something different from what runs locally.

**Pre-commit hooks.** No `.husky/`, no `prepare` script. Typecheck and lint are fast enough to run on every commit, and a hook is what makes "I'll remember to run it" unnecessary. Reminder from the standing preferences: hooks dropped directly into `.git/hooks/` are **not version-controlled** and don't survive a clone — which is precisely the problem Husky's tracked `.husky/` directory plus a `prepare` script solves.

**And a `DECISIONS.md`.** `PLAN.md` captured the up-front decisions well (Cal.com over custom booking, Sanity over MDX, catalog-only books), but decisions made *during* the build — the `sanityFetch` fallback contract, the graceful-degradation stance, `from`/`replyTo`, the route-group split — live only in code comments and now in these notes. The learning files teach *you*; a `DECISIONS.md` answers "why is it built this way" for whoever inherits this, without making them re-derive it.

---

## Takeaways

1. **`NEXT_PUBLIC_` inlines at build time.** Never prefix a secret; expect a rebuild when you change one. `grep -ro "NEXT_PUBLIC_[A-Z_]*" .next/static/` shows what actually shipped.
2. **Judge a variable by what it authorises, not by whether it looks secret.** A project ID naming public data is fine; a token that performs actions is not.
3. **`git check-ignore -v <path>`** answers "why is this ignored" with the exact rule and line.
4. **`!` negations are literal.** `!.env.example` does not cover `.env.local.example`.
5. **Clone your own repo into `/tmp` and follow your README.** It is the only reliable way to catch setup bugs, because your working tree hides them.
6. **Normalise URLs once at the boundary** (`.replace(/\/$/, "")`) rather than defending against `//` at every concatenation.
7. **Unused dependencies are documentation debt and supply-chain surface.** `bunx depcheck`, then remove.
8. **`trustedDependencies` is bun's postinstall allowlist** — a real supply-chain control. Don't leave a contradictory `ignoreScripts` next to it.
9. **Graceful degradation is the opposite of fail-fast.** Both are valid; know which one the project requires and why.
10. **CI and pre-commit hooks are the cheap half of quality.** Hooks in `.git/hooks/` don't survive a clone; `.husky/` + `prepare` does.
