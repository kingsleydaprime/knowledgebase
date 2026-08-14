# Investigating History

**[Intermediate]** — Reading the past: `log` and its filters, `show`, `diff`, `blame`, `shortlog`, and `bisect` for finding the commit that broke something by binary search.

## git log

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

```
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

```bash
git shortlog                   # Commits grouped by author
git shortlog -sn               # Summary: count, sorted numerically
git shortlog -sn --no-merges   # Exclude merge commits
git shortlog -sn main..feature # Commits in feature not in main
```


---

## Git Bisect — Finding Bugs with Binary Search

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

## Related
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — good messages are what make `log` searchable at all
- [[git/git-troubleshooting|Troubleshooting]] — when investigation turns into recovery
- [[devops/01-linux/03-file-operations|File Operations (Linux)]] — `grep` and pipes, which most of these commands feed into
- [[git/README|Git course map]]
