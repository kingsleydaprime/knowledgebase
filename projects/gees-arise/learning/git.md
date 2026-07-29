# Git — Gees Arise

You're running every git command yourself for this project on purpose, to build real muscle memory. This file is notes/explanations to go with that — not a replacement for typing the commands. See `learning/shell.md` for non-git CLI commands (npm, npx, mkdir, grep, etc.) run while building this project — including a note on `git mv`/`git rm`, which look like plain file commands but are actually git operations.

---

## Why commit often, in small pieces

A commit is a saved checkpoint of your project you can always come back to. The habit worth building: **one commit per small, complete change** — not one giant commit at the end of the day. Small commits mean:

- If something breaks, `git log` shows you exactly which checkpoint introduced the problem.
- Your commit history reads like a story of how the project was built — genuinely useful when you (or anyone else) needs to understand *why* something is the way it is later.
- It's what real engineering teams expect — reviewers read your commits, not just your final diff.

## The basic loop you'll be repeating

```
git status          # what changed since the last commit?
git diff             # show me the actual line-by-line changes
git add <file>        # stage a specific file (prefer this over `git add .`)
git commit -m "message"   # save the checkpoint
git log --oneline     # see your history so far
```

`git add .` stages *everything* changed, including files you may not have meant to include (stray config, `.env`, editor junk). Naming files explicitly is slower but safer — worth doing until you have a feel for what's in your working tree at any moment.

## Writing a good commit message

Convention worth adopting early: a short summary line (under ~70 chars) describing *why*, not just *what* — the diff already shows what changed.

- Bad: `updated schema`
- Better: `add task_completions to support recurring task history`

## Conventional Commits — the `type(scope): description` format

Adopted 2026-07-27 for this project. The shape:

```
<type>(<optional scope>): <description>
```

- **`type`** — what *kind* of change this is. The common ones:
  - `feat` — a new feature (`feat(circle-engine): add invite-code join flow`)
  - `fix` — a bug fix (`fix(proof-upload): bypass Vercel's serverless body-size limit`)
  - `chore` — maintenance with no feature/fix behavior change (dependency bumps, config tweaks)
  - `docs` — documentation only
  - `refactor` — restructuring code without changing behavior
  - `test` — adding/fixing tests only
- **`scope`** — *optional*, in parentheses — which part of the app the change touches (`proof-upload`, `circle-engine`, `auth`, `rls`, etc.). Skip it entirely (`fix: ...`) if the change doesn't cleanly belong to one area, or is small enough that scope wouldn't add information.
- **`description`** — same "why over what" rule as above, just prefixed now.

**Why this format specifically, beyond just being tidy:** the `type` prefix is machine-readable — tools like `semantic-release` or changelog generators parse it to auto-figure-out version bumps (a `fix` is a patch release, a `feat` is a minor release, anything with a `BREAKING CHANGE:` footer is a major release) and to group commits into changelog sections automatically. Not wired up for this project yet, but writing commits in this shape from the start means adopting that tooling later is free — the history is already structured for it.

**Examples from this project's actual history** (retroactively described in this format — commits were already made before this convention was adopted, so their real messages may differ):
```
feat(auth): add email/password auth flow with route protection
feat(circle-engine): add circle creation and joining via invite code
feat(tasks): add task creation modal and task list on dashboard
feat(proof-upload): add proof upload and audit feed
fix(proof-upload): bypass Vercel's serverless body-size limit by uploading directly to Supabase Storage
```

## Branching — one branch per feature/fix

Adopted 2026-07-27: work happens on a branch, not directly on `main`. The habit:

```
git checkout -b feat/proof-upload   # branch off main before starting new work
# ...make the change, commit as usual on this branch...
git checkout main
git merge feat/proof-upload         # bring the finished feature back into main
```

**Why branch instead of committing straight to `main`:** `main` stays in a state that (mostly) always works — if a feature turns out half-broken or you want to abandon it, you delete the branch and `main` was never touched. It's also what makes pull requests possible later (a PR is just "here's a branch, review it before merging to main") and what lets more than one thing be in progress at once without them interfering.

**Naming convention:** match the branch prefix to the Conventional Commit type it's building toward — `feat/<slug>` for a new feature, `fix/<slug>` for a bug fix (e.g. `feat/proof-upload`, `fix/rls-recursive-policy`). Keeps the branch name, the eventual commit type, and (later) the PR title all telling the same story.

**Once this repo has a GitHub remote:** the flow becomes branch → push the branch → open a Pull Request → merge via GitHub (rather than a local `git merge`) — same underlying idea, just reviewed before merging instead of merged straight away.

**A real gotcha hit doing this for real:** a new branch always forks from whatever's currently checked out, not from some canonical "clean" starting point — so *which* branch you're standing on when you run `git checkout -b` matters. When `docs/update-readme-and-prd` was needed, the working directory was still sitting on `feat/admin-tiebreak-vote` — a separate, not-yet-merged feature branch. Branching off it directly would have silently carried that feature's commits along for the ride, so the new docs branch would have depended on a feature that might still change or get rejected in review. The fix: switch to `dev` (the shared integration branch, already caught up) *first*, then branch from there — so `docs/update-readme-and-prd` contains only `dev`'s already-settled history plus its own new commit, nothing borrowed from an unrelated branch in progress.

## Two remotes, on purpose — mirroring to two GitHub orgs

```bash
git remote -v
```
```
origin     git@github.com:spectroniqltd/gees-arise.git (fetch/push)
secondary  git@github.com:spectroniqlimited/gees-arise.git (fetch/push)
```
A "remote" is just a **name pointing at a URL** — `origin` isn't a keyword, it's the conventional name `git clone`/`gh repo create` picks for the first remote by default. Nothing stops adding a second one under a different name (`git remote add secondary <url>`) pointing at an entirely different repository — here, mirroring the same project to two different GitHub organizations. `git push` (no remote named) pushes to whichever remote the current branch tracks; `git push secondary <branch>` explicitly targets the other one.

`git push -u origin main` — the `-u` (`--set-upstream`) is what makes plain `git push`/`git pull` work afterward *without* spelling out `origin main` every time; it records "this local branch tracks that remote branch" once, the first time you push a new branch.

## `git stash` — temporarily shelving uncommitted work to switch branches cleanly

```bash
git stash        # save uncommitted changes onto a stack, revert the working tree to match the last commit
git stash pop    # reapply the most recent stash AND remove it from the stack
```
Used this to move the README/PRD edits off `feat/admin-tiebreak-vote` (where they happened to be sitting) onto a fresh `docs/update-readme-and-prd` branch forked from `dev` instead: `git stash` set the working tree back to clean, `git checkout dev && git checkout -b docs/update-readme-and-prd` created the right branch from the right starting point, then `git stash pop` brought the uncommitted edits back — now living on top of the correct branch.

**Worth knowing precisely:** `git checkout <branch>` doesn't *always* refuse to switch with uncommitted changes present — it only refuses if those changes would actually conflict with something that differs between the two branches. In this specific case (README.md/PRD.md untouched by the tiebreak-vote commit), a plain `git checkout dev` might well have worked without stashing at all. Stash was still the right call regardless — it makes the intent unambiguous ("these edits belong on a fresh base, full stop") instead of relying on there happening to be no conflict, and it's the technique that's actually *required* the moment there is one.

`git stash pop` vs `git stash apply`: `pop` reapplies the change and deletes it from the stash stack in one step (the common case — you're done with it). `apply` reapplies but *keeps* the stashed copy on the stack too, useful if you want to apply the same stashed changes to more than one branch.

## Pre-commit hooks — making git physically refuse a bad commit

Added 2026-07-27: `npm run typecheck` (a new script — just `tsc --noEmit` under a name that's easier to remember) and lint now run **automatically, every time you run `git commit`** — not something you have to remember to run yourself. If either fails, the commit is refused outright.

**The mechanism:** git has always supported "hooks" — scripts that run automatically at points like "right before a commit is created" (`pre-commit`), living in `.git/hooks/`. The catch: `.git/` itself is never tracked by git (it's the tracking system, not a tracked thing) — so a hook script dropped straight in there is invisible to anyone who clones the repo, and wouldn't even survive re-cloning it yourself onto a new machine.

**Husky solves that** by keeping the actual hook scripts in a normal, tracked `.husky/` directory instead, and re-installing them into `.git/hooks/` automatically via a `"prepare": "husky"` script in `package.json` — `prepare` is an npm lifecycle script that runs automatically after `npm install`, so anyone (including future-you, on a fresh clone) gets the same hooks the moment they install dependencies, with no manual setup step.

```bash
npx husky init          # created .husky/ + added the "prepare" script
```
Then `.husky/pre-commit` was written to run:
```
npx lint-staged
npm run typecheck
```
`lint-staged` (a separate small tool, paired with Husky) runs a linter **only against the files you've actually staged** (`git add`ed), configured in `package.json`'s `"lint-staged"` field:
```json
"lint-staged": { "*.{ts,tsx}": ["eslint --fix"] }
```
Why staged-files-only for lint but not for typecheck: linting a single file in isolation makes sense (style/pattern rules are mostly local), but TypeScript's type errors can come from *how files relate to each other* — checking only the staged files could miss an error a staged change introduced in a file you didn't touch. So typecheck runs against the whole project every time, while lint stays fast by scoping to what changed.

**Why keep this fast:** a slow pre-commit hook is a pre-commit hook people start bypassing with `git commit --no-verify` — which defeats the entire point. Slower checks (the full Playwright/e2e suite) belong in CI, running on push, not on every single local commit.

## Interactive staging (`git add -p`) — splitting one working tree into several honest commits

Normal `git add <file>` stages the *whole* file's current diff. `git add -p <file>` (or `-p` with no path, for everything) walks through the file's changes one **hunk** (a contiguous block of added/removed lines) at a time, asking `y`/`n`/`s` (split further)/`q` per hunk — so a single file that happened to accumulate changes for two unrelated features can still become two clean commits, instead of one commit that's honestly "two things at once."

**When this actually matters:** it's not about tidiness for its own sake — a commit that bundles two unrelated features makes `git log`/`git bisect`/`git revert` all lie to you later. If a bug shows up in the nudges feature next week, `git blame`/`git bisect` should point at *the nudges commit*, not at a commit whose message says "excuses" while secretly also containing half the nudges diff.

**The real constraint:** `-p` splits at hunk boundaries, not arbitrary lines — if two features' edits land inside the very same contiguous block of changed lines, `-p` can't cleanly separate them (there's an `e` option to manually edit a hunk's patch text as a last resort, but it's fiddly). This is itself a signal: if two features are that entangled in one file, they may not have been as separable a change as the two commit messages claim.

## To fill in as we go

- [x] Branching — see above (adopted 2026-07-27)
- [x] Pre-commit hooks (Husky + lint-staged) — see above (adopted 2026-07-27)
- [x] Interactive staging (`git add -p`) — see above (2026-07-27)
- [x] `git push` / connecting to a GitHub remote — see above (2026-07-27; two remotes, `origin` + `secondary`)
- [x] `git stash` / `git stash pop` — see above (2026-07-27)
- [ ] Pull requests — remote exists now, next PR opened is the moment to log this
- [ ] CI (GitHub Actions) — remote exists now, same checks as the local pre-commit hook, running on push/PR instead
- [ ] Undoing things safely (`git restore`, `git reset` — soft vs hard, and why hard is dangerous)
