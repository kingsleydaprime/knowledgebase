# Git — Munakalati

**Domain:** git, as it showed up in [[projects/munakalati/learning/README|munakalati]] — a client project with **two remotes**, a second contributor, and a `.gitignore` that quietly excluded the most important scripts in the repo.
**General version:** [[git/README|the git course]] — this file is only the project-specific parts.

45 commits, two authors (43 / 2), one branch.

---

## Two remotes on one repository

```console
$ git remote -v
origin     git@github.com:Readopia/munaworld.git       (fetch)
origin     git@github.com:Readopia/munaworld.git       (push)
secondary  git@github.com:kingsleydaprime/munakalati.git (fetch)
secondary  git@github.com:kingsleydaprime/munakalati.git (push)
```

**`origin` is the client's org; `secondary` is a personal mirror.** A remote is nothing more than a named URL — a repository can have any number, and `origin` is a convention, not a special name.

The commands, since this is the bit that isn't in the general course:

```bash
git remote add secondary git@github.com:kingsleydaprime/munakalati.git   # add one
git remote -v                                                            # list, with URLs
git push secondary main                                                  # push to a specific remote
git push                                                                 # → wherever the branch tracks (origin)
git remote show origin                                                   # what's tracking what
```

**The thing to understand: `git push` with no arguments does not push to every remote.** It pushes the current branch to its *upstream*, which here is `origin/main` (`git branch -a` shows `remotes/origin/HEAD -> origin/main`). `secondary` only receives what you explicitly send it, so **the mirror silently drifts behind unless you remember to push twice.**

Why have the mirror at all is a legitimate question, and the honest answer for a contract project is portfolio and continuity access — if org membership goes away at the end of the engagement, so does the history. Fine as a motivation, and it comes with two things worth being deliberate about:

- **Keep it in sync or don't rely on it.** A three-months-stale mirror is worse than none, because you'll believe you have a copy.
- **Anything the client would consider private is now in two places.** Here that's fine (no secrets are tracked — see below), but it's the question to ask before adding a personal remote to client work.

If you genuinely want both on every push:

```bash
git remote set-url --add --push origin git@github.com:Readopia/munaworld.git
git remote set-url --add --push origin git@github.com:kingsleydaprime/munakalati.git
```

That gives `origin` two push URLs, so one `git push` reaches both. Fetch still comes from the first.

## Merge commits from a second contributor

```console
$ git log --merges --oneline
ddbd4ec Merge branch 'main' of github.com:Readopia/munaworld Merge content from other pages.
7c24347 Merge branch 'main' of https://github.com/Readopia/munaworld
```

Both are **`git pull` merges** — the auto-generated commit you get when your local `main` and `origin/main` have both moved and git reconciles them. Joseph Awe contributed two commits of page content; those two merges are where they joined.

Two things to take from them:

**The default message is noise.** `"Merge branch 'main' of github.com:Readopia/munaworld"` says nothing a reader needs. `ddbd4ec` has *"Merge content from other pages."* appended, which is the right instinct — but jammed onto the same line rather than in the body, so `git log --oneline` shows a run-on. **A merge commit is a real commit; its message should say what came in.**

**These are "sync merges", the kind `--rebase` exists to prevent.** Nothing was being merged in the sense of integrating a feature — two people committed to `main` and git had to reconcile. On a two-person project with one branch, that's every pull. `git pull --rebase` replays your local commits on top of theirs and keeps history linear:

```bash
git pull --rebase                      # this time
git config pull.rebase true            # this repo, from now on
git config --global pull.rebase true   # everywhere
```

The general merge-vs-rebase argument is in [[git/07-merge-vs-rebase|the course]]. The narrow point for this repo: **a merge commit should record a decision to integrate something, not the accident of two people pushing on the same afternoon.**

## The commit-message drift

28 of 45 commits follow Conventional Commits; 17 don't. The recent end of the log is the non-conforming end:

```
3442c85 Fix redirect errors from home page.
ec37af7 Create not-found.tsx.
42f3e19 Remove Resources section from MVP — hide pages and nav links
f2b69dc Improve queries for handling url slugs of foreign languages
bcd087b Feat: Add date formatting for better text display        ← capital F, near-miss
```

Against the earlier, consistent stretch:

```
4745727 feat: implement About Us page with team member profiles and CMS integration
e2394f4 feat: add Wix blog migration script and implement pagination for blog posts
81515a2 feat: add hero content schema and queries, update Hero component…
```

**The drift is towards the end of the project**, which is the normal direction — conventions hold while things are calm and lapse under deadline. Worth naming honestly rather than as a nitpick: a convention that only survives easy weeks isn't providing the thing it was adopted for. `42f3e19` should have been `chore(resources): hide Resources section from MVP`, `3442c85` should have been `fix(links): correct hrefs orphaned by the Resources removal` — and that second one, written properly, would have made the connection between the two commits visible in the log.

The mechanical fix, given a Node project that already has `package.json`, is a **`commit-msg` hook running `commitlint`** — same Husky setup as the pre-commit typecheck. A hook enforces on the bad weeks too, which is the entire point.

Two other patterns in the log:

- **`Refactor code structure for improved readability and maintainability`, twice, verbatim.** Says nothing. If a commit message could be attached to any commit in any repo, it isn't a message.
- **`Initial commit` → `Revert "Initial commit"` → `Initial commit recommitted`.** Three commits at the start of history that exist because of a mistake. Harmless — but this is exactly the window where `git reset` and a clean re-commit are free, before anyone has pulled.

## The real finding: `.gitignore` excludes the migration scripts

The last three lines of `.gitignore`:

```gitignore
api.md
docs.md
migration.js
migration-report.json
backfill-images.js
backfill-report.json
sanity-export.tar.gz
```

**A pattern with no slash matches at every level of the tree.** `migration.js` does not mean "`migration.js` in the repo root" — it means *any file named `migration.js`, anywhere*. So:

```console
$ git check-ignore -v src/migration.js src/backfill-images.js src/docs.md
.gitignore:51:migration.js       src/migration.js
.gitignore:53:backfill-images.js src/backfill-images.js
.gitignore:50:docs.md            src/docs.md
```

**Three files that are not in the repository:**

| File | Status | What it is |
|---|---|---|
| `src/migration.js` | **ignored** | The 414-line Wix→Sanity migration. `bun run migrate` points at it |
| `src/backfill-images.js` | **ignored** | The 229-line cover-image backfill. `bun run backfill-images` points at it |
| `src/docs.md` | **ignored** | The saved Wix API responses — the only record of the source data's shape |
| `src/dedup.js` | tracked | |
| `src/fix-slugs.js` | tracked | |
| `src/wix-blog-migrate.js` | tracked | the superseded v1 |

**So a fresh clone gets a `package.json` with `"migrate": "bun run src/migration.js"` pointing at a file that doesn't exist**, while the *obsolete* first attempt at the same job is committed and present. For a project being handed over, that's the highest-severity item in this whole set of notes — the work is real, it's on one laptop, and nothing in the repo hints that it's missing.

**How it happened is ordinary and worth recognising**, because it's a trap rather than carelessness: the reports (`migration-report.json`, `backfill-report.json`) and the 70MB `sanity-export.tar.gz` genuinely *should* be ignored — they're generated output and a huge binary. The script names were added to the same block at the same time, plausibly to keep an early scratch version out of the repo, and then the scripts became real and nobody revisited the list.

Two habits that catch it:

```bash
git status --ignored --short | grep '^!!' | grep -v node_modules   # what am I ignoring?
git check-ignore -v <path>                                          # why is this file ignored?
```

`git check-ignore -v` is the one to remember — it prints **the file and line of the rule that matched**, which turns "why won't git add this" from a guessing game into a one-liner. And the general rule: **ignore patterns should be anchored unless you truly mean "anywhere"** — `/migration.js` (leading slash) matches only the root, which is almost certainly what was intended.

The fix, when someone picks this up:

```bash
# 1. anchor or delete the three script/doc patterns in .gitignore
# 2. then force-add the files, since they're still matched until the rule changes
git add -f src/migration.js src/backfill-images.js src/docs.md
git commit -m "fix(repo): commit migration scripts excluded by unanchored gitignore patterns"
```

## What the repo does get right

**No secrets are tracked.** `.env*` and `.env.*` are ignored with an `!.env.example` exception, and `git ls-files | grep -E '\.env|tar\.gz'` returns nothing. Both `.env` and `.env.migration` hold a live `SANITY_API_TOKEN` and a `WIX_API_KEY`, and neither has ever been committed. That's the failure that actually hurts, and it didn't happen.

**The 70MB dataset export is ignored.** `sanity-export.tar.gz` in git history would bloat every clone forever, and `git rm` doesn't undo it — the blob stays in history and needs `filter-repo` to remove. Ignored from the start is the only easy time.

**`42f3e19` is a well-formed commit.** A pure `git mv` rename (five files, `0` insertions, `0` deletions on four of them — git detected the rename rather than recording delete+add), plus the two-line nav change that made it coherent, plus a body explaining the reversal:

```
Remove Resources section from MVP — hide pages and nav links

The resources folder is renamed to _resources (excluded from routing)
and the nav link is removed from both desktop and mobile menus. Easy to
restore when the section is ready.
```

**One change, one commit, and the body says how to undo it.** That's the standard the rest of the log should have been held to.

## Related
- [[git/08-remotes-and-collaboration|remotes and collaboration]] · [[git/07-merge-vs-rebase|merge vs rebase]] · [[git/12-conventions-and-hygiene|conventions and hygiene]] · [[git/17-hooks-and-signing|hooks]]
- [[projects/munakalati/learning/05-migration/05-repair-scripts|migration/05]] — the scripts that aren't committed
- [[projects/gees-arise/learning/01-git|gees-arise — git]]
