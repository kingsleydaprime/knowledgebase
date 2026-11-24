---
id: 350327ef-e32d-4446-9980-820c4207b70f
---

# Investigating History

Investigating history is using Git's saved record to find out what changed, when, who changed it and why. Git can show you the full list of commits, the exact lines each one changed, and even help you find which commit brought in a bug. It is like checking your bank statement line by line to see where the money went.

## git log
<!-- bite: 44bcd223-4403-4d93-bcc1-ea43797c280d -->

```bash
git log                        # Full log
git log --oneline              # One line per commit
git log --graph                # ASCII branch graph
git log --oneline --graph --decorate --all   # The most useful view
git log -5                     # Last 5 commits
git log --since="2 weeks ago"
git log --until="2024-01-01"
git log --author="Kingsley"
git log --grep="auth"          # Commits with "auth" in message
git log -S "function_name"     # Commits that added/removed this string (pickaxe)
git log -G "regex"             # Commits where diff matches regex
git log --follow file.txt      # Follow file through renames
git log -- file.txt            # Commits touching file.txt
git log main..feature          # Commits in feature not in main
git log feature..main          # Commits in main not in feature
git log main...feature         # Commits in either but not both (symmetric diff)
git log --stat                 # Show files changed per commit
git log --patch                # Show full diff for each commit
git log --format="%H %an %s"   # Custom format
git log --no-merges            # Exclude merge commits
git log --merges               # Show only merge commits
```

**Custom format specifiers:**

```text
%H  — commit hash (full)
%h  — commit hash (abbreviated)
%an — author name
%ae — author email
%ad — author date
%ar — author date, relative
%cn — committer name
%s  — subject (first line)
%b  — body
%D  — ref names
```

## git show and diff
<!-- bite: dd23f69f-6900-43e5-a327-09875dd52b62 -->

```bash
git show                       # Show latest commit
git show HEAD                  # Same
git show a1b2c3d               # Show specific commit
git show HEAD~2                # Show commit 2 before HEAD
git show HEAD:file.txt         # Show file contents at HEAD
git show main:src/app.js       # File contents on main branch

# Commit references
HEAD                           # Current commit
HEAD~1 or HEAD~               # One commit back
HEAD~3                         # Three commits back
HEAD^                          # First parent (same as HEAD~1 for regular commits)
HEAD^2                         # Second parent (only for merge commits)
a1b2c3d^                       # Parent of this commit
@{yesterday}                   # Commit at yesterday's time
@{2.weeks.ago}                 # Two weeks ago
main@{1}                       # Previous position of main

git diff                       # Working directory vs index
git diff --staged              # Index vs HEAD (what will be committed)
git diff HEAD                  # Working directory vs HEAD
git diff main feature          # Difference between two branches
git diff a1b2c3d b2c3d4e       # Difference between two commits
git diff HEAD~3                # Working dir vs 3 commits ago
git diff -- file.txt           # Diff only for specific file
git diff --stat                # Summary of changes
git diff --word-diff           # Word-level diff (good for prose)
git diff --ignore-whitespace   # Ignore whitespace changes
```

## git blame
<!-- bite: 2477ef83-5f42-476a-b920-881ae53aac40 -->

```bash
git blame file.txt             # Show who last changed each line
git blame -L 10,20 file.txt    # Only lines 10-20
git blame -w file.txt          # Ignore whitespace changes
git blame -C file.txt          # Detect lines moved from other files
git blame a1b2c3d -- file.txt  # Blame at a specific commit

# Reading blame output:
# SHA    (author    date    line_number) content
# a1b2c3 (Kingsley  2026-01 10)         const app = express();
```

## git shortlog
<!-- bite: d22294b4-6172-4563-b7b6-148fcb0d24b4 -->

```bash
git shortlog                   # Commits grouped by author
git shortlog -sn               # Summary: count, sorted numerically
git shortlog -sn --no-merges   # Exclude merge commits
git shortlog -sn main..feature # Commits in feature not in main
```


---

## Git Bisect — Finding Bugs with Binary Search
<!-- bite: 5cf07e87-2c1e-4d29-9c05-5a80fffa4163 -->

`git bisect` performs a binary search through commit history to find the commit that introduced a bug. Instead of manually checking commits, you tell Git "good" or "bad" and it narrows down to the culprit in O(log n) steps.

```bash
git bisect start                       # Start bisect session
git bisect bad                         # Current commit has the bug
git bisect good v1.0.0                 # v1.0.0 was working
# Git checks out the midpoint commit

# Test the code, then:
git bisect good                        # This commit is fine
git bisect bad                         # This commit has the bug
# Repeat until Git identifies the first bad commit

git bisect reset                       # End session, return to original HEAD

# Full example:
git bisect start
git bisect bad HEAD                    # Current HEAD is broken
git bisect good HEAD~50                # 50 commits ago it was working
# Git will need ~6 steps (log2(50)) to find the bad commit
```

### Automated Bisect

```bash
# If you have a test script that exits 0 (pass) or non-zero (fail):
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run ./test.sh               # Automatically bisects using the script

# The script receives each commit as the working directory
# and should exit 0 if good, 1 if bad, 125 if the commit can't be tested
```

---

## Check your understanding
<!-- bite: ee4237ad-2836-4c82-96bd-ee349987ab15 -->

Try each one before you open the answer.

1. <!-- q: exact id="ac31e650" answer="7" -->
   You start `git bisect` with the current commit bad and a commit 100 commits back good. About how many good/bad tests does Git need, at most, to find the first bad commit?

   <details><summary>Answer</summary>

   About 7, because 2⁷ = 128 is the first power of 2 at or above 100. Each test halves the range that's left, so it takes log₂(100) ≈ 6.6 steps, rounded up.

   </details>

2. <!-- q: mcq id="2df0d4b9" -->
   What does `git log main..feature` list?

   - [x] Commits on `feature` that aren't on `main`
   - [ ] Commits on `main` that aren't on `feature`
   - [ ] Every commit on both branches
   - [ ] Commits on either branch but not both

   <details><summary>Answer</summary>

   Commits reachable from `feature` but not from `main`: what the feature adds. `feature..main` is the other way round, and three dots (`main...feature`) gives commits on either but not both.

   </details>

3. <!-- q: exact id="8794e3bc" answer="git log -S" accept="git log -S calculateDiscount" -->
   A function called `calculateDiscount` vanished from the code and you want the commit that removed it. Which `git log` option searches for commits that added or removed a given string? Give the command and the option.

   <details><summary>Answer</summary>

   `git log -S "calculateDiscount"`, the pickaxe. It lists commits whose changes added or removed that exact string. `-G` does the same with a regular expression.

   </details>

4. <!-- q: mcq id="4a75146a" -->
   You want to see who last changed lines 40 to 55 of `server.js`. Which command?

   - [ ] `git log -5 server.js`
   - [x] `git blame -L 40,55 server.js`
   - [ ] `git show server.js`
   - [ ] `git shortlog server.js`

   <details><summary>Answer</summary>

   `git blame -L 40,55 server.js` shows the commit, author and date that last touched each of those lines.

   </details>

5. <!-- q: mcq id="6fd5e007" -->
   `HEAD` is a merge commit. Which reference names its second parent, the tip of the branch that was merged in?

   - [ ] `HEAD~2`
   - [x] `HEAD^2`
   - [ ] `HEAD~1`
   - [ ] `HEAD@{2}`

   <details><summary>Answer</summary>

   `HEAD^2`. `^` picks a parent, so `^2` is the second parent. `HEAD~2` goes back two generations along first parents, and `HEAD@{2}` is where HEAD pointed two moves ago, from the reflog.

   </details>

6. <!-- q: open id="161f6546" -->
   You have a script `test.sh` that exits 0 when the bug is absent and 1 when it is present. How does `git bisect run` save you work?

   <details><summary>Answer</summary>

   After `git bisect start`, `git bisect bad` and `git bisect good <commit>`, run `git bisect run ./test.sh`. Git checks out each midpoint, runs the script, and reads its exit code as good (0) or bad (1–127, except 125, which means "can't test this one, skip it"). It repeats until it names the first bad commit, with no manual testing. Finish with `git bisect reset`.

   </details>

## Related
<!-- bite: a06523a0-fcc1-45ad-bc79-fd461814e793 -->
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — good messages are what make `log` searchable at all
- [[git/git-troubleshooting|Troubleshooting]] — when investigation turns into recovery
- [[devops/01-linux/03-file-operations|File Operations (Linux)]] — `grep` and pipes, which most of these commands feed into
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 92573c1e-3c77-4108-a825-1103c4647993 -->

**Level:** Intermediate. **Covers:** Reading the past: `log` and its filters, `show`, `diff`, `blame`, `shortlog`, and `bisect` for finding the commit that broke something by binary search.
