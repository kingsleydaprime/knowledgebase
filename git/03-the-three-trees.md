# The Three Trees — Working Directory, Index, HEAD

**[Beginner]** — The most important mental model in Git, and the staging, committing and `.gitignore` mechanics that sit on top of it.

This is the most important conceptual model for understanding Git commands.

## The Three Areas

**Working Directory** — The actual files on your disk. What you see in your editor. Untracked changes live here.

**Index (Staging Area)** — A proposed snapshot of your next commit. When you `git add`, you're moving changes from the working directory into the index. The index is a binary file at `.git/index`.

**HEAD** — A pointer to the last commit on your current branch. Represents the current snapshot of the repository.

```
Working Directory  →  git add  →  Index (Staging)  →  git commit  →  HEAD (Repository)

git diff               = Working Directory vs Index
git diff --staged      = Index vs HEAD
git diff HEAD          = Working Directory vs HEAD
```

## File States

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

## Related
- [[git/01-how-git-works|How Git Actually Works]] — what the index is a binary file *of*
- [[git/10-undoing-things|Undoing Things]] — `reset` is defined entirely in terms of these three trees
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — what to put in the message you just learned to write
- [[git/README|Git course map]]
