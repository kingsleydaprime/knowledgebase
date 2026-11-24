---
id: 615f55c0-1fb4-4ee7-96c5-9dccb734209f
---

# The Three Trees — Working Directory, Index, HEAD

This is the most important conceptual model for understanding Git commands.

## The Three Areas
<!-- bite: e669044f-8f34-4588-b1d4-ec00553bac13 -->

**Working Directory** — The actual files on your disk. What you see in your editor. Untracked changes live here.

**Index (Staging Area)** — A proposed snapshot of your next commit. When you `git add`, you're moving changes from the working directory into the index. The index is a binary file at `.git/index`.

**HEAD** — A pointer to the last commit on your current branch. Represents the current snapshot of the repository.

```text
Working Directory  →  git add  →  Index (Staging)  →  git commit  →  HEAD (Repository)

git diff               = Working Directory vs Index
git diff --staged      = Index vs HEAD
git diff HEAD          = Working Directory vs HEAD
```

## File States
<!-- bite: 708bba4d-497f-4b4f-a5a5-140764d4bc20 -->

```bash
git status             # Show state of all files

# States:
# Untracked    — new file Git doesn't know about yet
# Tracked      — file Git knows about; can be:
#   Unmodified — same as HEAD
#   Modified   — changed in working directory but not staged
#   Staged     — in index, ready for next commit
# Ignored      — matched by .gitignore

git status -s          # Short status
# ?? file              — untracked
# A  file              — staged new file
# M  file              — modified and staged
#  M file              — modified but not staged
# MM file              — modified, partially staged
# D  file              — staged deletion
```

---

## Staging and Committing
<!-- bite: d89b8c24-7b21-4fde-a72b-48bdb1e877c5 -->

### Staging

```bash
git add file.txt               # Stage specific file
git add directory/             # Stage entire directory
git add .                      # Stage all changes in current directory
git add -A                     # Stage all changes in entire repo
git add -u                     # Stage modifications and deletions (not new files)
git add -p                     # Interactive — stage hunks (chunks) selectively
git add -i                     # Interactive staging menu

# Interactive hunk staging (-p) — extremely useful
# y — stage this hunk
# n — skip this hunk
# s — split into smaller hunks
# e — manually edit the hunk
# q — quit
# a — stage all remaining hunks in this file
# d — skip all remaining hunks in this file
# ? — help

git restore --staged file.txt  # Unstage a file (keep working directory changes)
git restore file.txt           # Discard working directory changes (dangerous — unrecoverable)
```

### Committing

```bash
git commit                     # Open editor to write commit message
git commit -m "message"        # Inline commit message
git commit -am "message"       # Stage all tracked changes and commit (skip git add)
git commit --amend             # Amend last commit (opens editor)
git commit --amend --no-edit   # Amend last commit keeping same message
git commit --amend -m "new"    # Amend with new message
git commit --allow-empty -m "trigger CI"  # Commit with no changes (useful for CI)

# Commit with detailed message (title + body)
git commit -m "feat: add user auth

Implements JWT-based authentication with:
- Login endpoint with bcrypt password validation
- Token refresh mechanism
- Role-based middleware guards

Closes #42"
```

### .gitignore

```bash
# Patterns
file.txt               # Ignore specific file
*.log                  # Ignore all .log files
/build                 # Ignore build/ in root only (not src/build/)
build/                 # Ignore any directory named build
!important.log         # Un-ignore (negate a pattern)
**/logs                # Ignore logs/ in any subdirectory
doc/*.txt              # Ignore .txt in doc/ but not doc/sub/file.txt
doc/**/*.pdf           # Ignore all .pdf files anywhere under doc/

# Check why a file is ignored
git check-ignore -v filename

# Force-add an ignored file
git add -f ignored-file.txt

# List all ignored files
git ls-files --ignored --exclude-standard

# .gitignore only affects untracked files
# To stop tracking a file already committed:
git rm --cached file.txt           # Remove from index only (keep on disk)
git rm --cached -r directory/      # Recursive
echo "file.txt" >> .gitignore      # Then add to .gitignore
git commit -m "stop tracking file.txt"
```


---

## Check your understanding
<!-- bite: 7f3b1dad-0cae-4f8d-931c-c04f7eeae565 -->

Try each one before you open the answer.

1. <!-- q: gap id="9477f3d3" answers="working directory|working tree;index|staging area" -->
   `git add` moves changes from the ___ into the ___, and `git commit` turns the index into a new commit at HEAD.

   <details><summary>Answer</summary>

   From the working directory into the index (the staging area). The index is your proposed next snapshot.

   </details>

2. <!-- q: mcq id="66d38127" -->
   You staged `app.js` and then edited it again. Which command shows only the changes you have staged?

   - [ ] `git diff`
   - [x] `git diff --staged`
   - [ ] `git diff HEAD`
   - [ ] `git status -s`

   <details><summary>Answer</summary>

   `git diff --staged` compares the index with HEAD. Plain `git diff` shows working directory against index, which here is the newer, unstaged edit. `git diff HEAD` shows both together.

   </details>

3. <!-- q: mcq id="968e2855" -->
   `git status -s` prints `MM app.js`. What does that mean?

   - [ ] The file was merged twice
   - [x] Some changes are staged and there are more unstaged changes on top
   - [ ] The file is untracked
   - [ ] The file was deleted and re-added

   <details><summary>Answer</summary>

   Modified and partially staged. The first column is the index, the second the working directory. `M ` would be fully staged, ` M` not staged at all.

   </details>

4. <!-- q: mcq id="f68406bd" -->
   A file called `.env` was committed a month ago. You add `.env` to `.gitignore`, but Git still shows changes to it. Why?

   - [ ] `.gitignore` only works after a restart
   - [x] `.gitignore` only affects untracked files, and `.env` is already tracked
   - [ ] The pattern needs to be `/.env`
   - [ ] Hidden files can't be ignored

   <details><summary>Answer</summary>

   `.gitignore` never applies to files Git already tracks. Run `git rm --cached .env` to stop tracking it (it stays on disk), then commit. If it held secrets, they are still in the history, so rotate them.

   </details>

5. <!-- q: exact id="30011dd8" answer="git add -p" accept="git add --patch" -->
   You changed two unrelated things in one file and want to commit them separately. What command lets you stage the file hunk by hunk?

   <details><summary>Answer</summary>

   `git add -p`. It shows each hunk and asks: `y` to stage, `n` to skip, `s` to split it smaller.

   </details>

6. <!-- q: mcq id="17a9f06d" -->
   Which of these destroys work that can't be recovered from Git?

   - [ ] `git restore --staged notes.md`
   - [x] `git restore notes.md` on a file with unstaged edits
   - [ ] `git rm --cached notes.md`
   - [ ] `git commit --amend --no-edit`

   <details><summary>Answer</summary>

   `git restore notes.md` throws away the unstaged edits in the working directory. They were never committed or staged, so Git has no copy. `--staged` only unstages, `rm --cached` keeps the file on disk, and an amended commit can still be found in the reflog.

   </details>

## Related
<!-- bite: 78255e00-f2ae-4064-a094-8078eed9c7fb -->
- [[git/01-how-git-works|How Git Actually Works]] — what the index is a binary file *of*
- [[git/10-undoing-things|Undoing Things]] — `reset` is defined entirely in terms of these three trees
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — what to put in the message you just learned to write
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 38136c11-11c3-40ac-82a8-33c92cd3644d -->

**Level:** Beginner. **Covers:** The most important mental model in Git, and the staging, committing and `.gitignore` mechanics that sit on top of it.
