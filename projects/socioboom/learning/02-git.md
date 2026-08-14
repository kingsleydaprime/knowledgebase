# SocioBoom — Git

Version control as practised on this project. The general-purpose version of this material is
[[git/README|the git course]] — read that for internals, rebasing, reflog,
recovery, and workflows. This file teaches the parts that came up here, in the context they
came up in, plus what's true only of this project.

See also [[projects/socioboom/learning/01-shell|01-shell]] and
`socioboom/backend/DECISIONS.md`.

Started 2026-08-11 while splitting the media pipeline work into commits.

---

## 1. This Project Has Two Repos

`socioboom/backend` and `socioboom/frontend` are **separate git repositories**. The parent
`socioboom/` folder is not a repo at all.

Consequences that have actually come up:

- `learning/` lived at `socioboom/learning/`, outside both repos. Moving it to the
  knowledgebase was a plain `cp`/`rm` — no `git mv`, no history to preserve, no staged
  deletion to commit.
- A feature spanning both sides is **two branches and two commits**. There's no atomic
  "commit the whole feature." The media work was `feat/media-and-social-publishing` in the
  backend and `feat/media-uploads` in the frontend.
- `git status` only ever reports on the repo you're standing in. Being in
  `socioboom/frontend` tells you nothing about uncommitted backend work.
- Branches drift independently — backend sat on `main` while frontend was on `dev`.

---

## 2. Conventional Commits

```
type(scope): description
```

Types in use: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.

The scope is the area touched — `media`, `publishing`, `posts`, `auth`. Omit it when a
change doesn't belong to one area.

The description says **why**, not what. The diff already shows what changed:

```
✅ fix(facebook): publish to Pages instead of personal profile
❌ fix(facebook): change endpoint URL and add listPages function
```

The second is just the diff in English. The first tells a future reader what was wrong.

Architectural *why* goes in `socioboom/backend/DECISIONS.md`, not commit messages. A commit
message says why this change; DECISIONS.md says why this design.

---

## 3. Splitting Work Into Commits — and When You Can't

The goal is one commit per logical change. The constraint is that **git stages files, not
ideas.** If one file contains two unrelated changes, a clean split needs extra work.

### The case study

**What was attempted:** four backend commits — media pipeline, Facebook fix, Instagram,
TikTok.

**Why it failed:** `worker.ts`, `account.controller.ts`, and `.env.example` each gained code
for *all three platforms*. Splitting by filename cannot separate three changes living in one
file.

**What shipped instead:** three commits that do split cleanly by path — media pipeline,
all three platform publishers, then `DECISIONS.md`.

Three options when this happens:

**a) Coarser commits that split cleanly by file.** What was done here. Less granular, but
honest and quick.

**b) `git add -p`** — interactive staging, hunk by hunk:

```bash
git add -p src/worker.ts
```

Per hunk: `y` stage, `n` skip, `s` split smaller, `e` edit manually, `q` quit, `a` stage all
remaining in this file, `d` skip all remaining. Powerful, and correct when the split
genuinely matters. Slow and error-prone across three files and four commits.

**c) Commit as you go.** The real fix. Had each platform been committed when it was
finished, the split would never have been needed. **Retroactive splitting is a symptom of
batching too much work before the first commit.** `git add -p` is the escape hatch, not the
cure.

### The test that actually matters

Not "is this commit small" but: **does each commit leave the tree in a working state?**

Each of the three backend commits typechecks on its own. That's the property that makes
`git bisect` work, makes a revert safe, and lets a reviewer read one commit without holding
the other two in their head. (Stated as a general rule in
[[git/12-conventions-and-hygiene|Conventions and Hygiene]].)

Checking commit 1 in isolation means asking: with only these files staged, does anything in
the tree reference something that isn't there yet? Here, `main.ts` imports the new media
routes — staged, fine. The *old* `worker.ts` stays in that commit and doesn't reference
media at all — also fine.

---

## 4. Staging Commands Used Here

```bash
git add path/to/file.ts                # one file
git add src/api/v1/modules/media       # a whole directory, recursively
git add -u src/api/v1/shared/services  # stage MODIFICATIONS AND DELETIONS under a path
git add -p src/worker.ts               # interactive, hunk by hunk
```

`-u` (`--update`) is the one to remember for deletions — it caught the `twitter.ts` and
`linkedin.ts` removals without listing them individually. Plain `git add <deleted-file>`
also works. It does **not** add untracked files; that's the difference from `git add -A`.

Paths with shell metacharacters need quoting:

```bash
git add "src/app/(app)/platform/[platform]/page.tsx"
```

Parentheses and brackets are syntax in zsh — unquoted, the shell tries to interpret them
before git ever sees the path. Next.js route groups make this a recurring annoyance in the
frontend repo.

---

## 5. Feature Branches

One branch per feature or fix, prefixed with the Conventional Commits type:

```bash
git checkout -b feat/media-and-social-publishing
git checkout -b fix/rls-policies
```

`-b` creates and switches in one step.

Backend was sitting on `main` when this work started, which is the thing to avoid — branch
*first*, before writing code, so the work has somewhere to live from the beginning.
Frontend was already on `dev`, so branching off that was straightforward.

---

## 6. Read-Only Commands for Orienting

```bash
git branch --show-current    # which branch am I on
git status --short           # compact status
git diff --stat              # per-file insertion/deletion counts, no content
git diff                     # actual unstaged changes
git diff --staged            # what's about to be committed  ← run before every commit
```

`git diff --staged` before `git commit` is the cheapest good habit here. It catches the
debug `console.log`, the commented-out block, the file staged by accident.

`--short` output, worth reading at a glance:

```
 M .env.example        modified, not staged
M  src/worker.ts       modified, staged
MM src/app/main.ts     staged changes AND further unstaged changes
 D old-file.ts         deleted, not staged
?? new-file.ts         untracked
```

Two columns: left is the staging area, right is the working tree.

---

## Related
- [[git/README|Git course]] — the general-purpose version of all of this
- [[projects/socioboom/learning/01-shell|01-shell]] — shell commands on this project
