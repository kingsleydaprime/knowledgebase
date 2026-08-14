# Undoing Things

**[Intermediate]** — Where most Git confusion lives. A decision tree first, then `reset` vs `revert` vs `restore`, the reflog as a safety net, and stashing.

This is where most confusion happens. There are multiple ways to undo in Git, and choosing the wrong one can make things worse.

## The Undo Decision Tree

```
What do you want to undo?
│
├── Unstage a file (keep changes in working directory)
│   └── git restore --staged file.txt
│
├── Discard working directory changes (unrecoverable without stash)
│   └── git restore file.txt
│   └── git checkout -- file.txt  (older syntax)
│
├── Undo the last commit (keep changes staged)
│   └── git reset --soft HEAD~1
│
├── Undo the last commit (keep changes unstaged)
│   └── git reset --mixed HEAD~1  (default)
│   └── git reset HEAD~1
│
├── Undo the last commit (discard changes entirely)
│   └── git reset --hard HEAD~1  (DANGEROUS)
│
├── Undo a commit that has been pushed (safe — adds a new commit)
│   └── git revert HEAD
│   └── git revert a1b2c3d
│
└── Fix the last commit message or add a file
    └── git commit --amend
```

## git reset — The Three Modes

```bash
# git reset moves HEAD (and the branch) to a different commit
# The difference is what happens to your working directory and index

git reset --soft HEAD~1
# HEAD moves back one commit
# Index: stays as-is (files are staged, ready to recommit)
# Working directory: unchanged
# Use: "I want to redo the last commit differently"

git reset --mixed HEAD~1      # Default mode
# HEAD moves back one commit
# Index: reset to match the new HEAD
# Working directory: unchanged (changes show as unstaged)
# Use: "I want to un-commit and un-stage my last commit's changes"

git reset --hard HEAD~1
# HEAD moves back one commit
# Index: reset to match the new HEAD
# Working directory: reset to match the new HEAD (CHANGES LOST)
# Use: "I want to completely discard my last commit and its changes"
# WARNING: Working directory changes are permanently lost (unless stashed)

# Reset a specific file (doesn't move HEAD)
git reset HEAD file.txt       # Unstage file (index reset to HEAD, working dir unchanged)
git reset a1b2c3d file.txt    # Reset file in index to a specific commit
```

## git revert — Safe Undo for Shared History

`git revert` creates a new commit that undoes the changes of a previous commit. The old commit remains in history — nothing is rewritten. This is the **only safe way to undo commits that have been pushed to a shared branch**.

```bash
git revert HEAD                # Revert last commit
git revert a1b2c3d             # Revert a specific commit
git revert HEAD~3..HEAD        # Revert last 3 commits (one revert commit each)
git revert -n HEAD~3..HEAD     # Stage reverts without committing (then commit once)
git revert --no-edit HEAD      # Don't open editor for message
git revert -m 1 merge-commit   # Revert a merge commit (1 = keep first parent's changes)
```

## Restoring Files

```bash
# Restore file to state at HEAD
git restore file.txt                        # Modern syntax
git checkout -- file.txt                    # Old syntax

# Restore file to state at specific commit
git restore --source HEAD~2 file.txt
git restore --source a1b2c3d file.txt

# Restore file from another branch
git restore --source feature file.txt

# Restore deleted file
git restore deleted-file.txt                # If deletion is unstaged
git restore --staged deleted-file.txt       # If deletion is staged
```

## Recovering Lost Commits

If you did `git reset --hard` and lost commits, or if you deleted a branch — the commits aren't gone immediately. Git keeps them in the reflog for 30 days (90 days for unreachable commits with `gc.reflogExpireUnreachable`).

See **The Reflog — Your Safety Net** below.

---

## The Reflog — Your Safety Net

### What the Reflog Is

The reflog (reference log) records every time HEAD or a branch ref moves — commits, checkouts, resets, rebases, merges. It's local only (not pushed to remotes) and is the single most important tool for recovering from mistakes.

```bash
git reflog                     # Show reflog for HEAD
git reflog show main           # Reflog for main branch
git reflog show --all          # All reflogs
git reflog expire              # Normally runs automatically; cleans old entries

# Reflog output:
# a1b2c3d HEAD@{0}: commit: feat: add login
# b2c3d4e HEAD@{1}: rebase: fast-forward
# c3d4e5f HEAD@{2}: checkout: moving from main to feature
# d4e5f6g HEAD@{3}: reset: moving to HEAD~1
```

### Recovering with Reflog

```bash
# Scenario: you did git reset --hard and lost commits
git reflog                     # Find the SHA of the lost commit
git reset --hard a1b2c3d       # Reset to it
# Or: create a branch at that point
git branch recovered-work a1b2c3d

# Scenario: you deleted a branch
git reflog                     # Find the last commit SHA that was on the branch
git checkout -b recovered-branch a1b2c3d

# Scenario: rebase went wrong
git reflog                     # Find the SHA before the rebase started
git reset --hard HEAD@{5}      # Go back to before the rebase

# Scenario: merge was a mistake
git reflog
git reset --hard ORIG_HEAD     # Git saves the pre-merge position in ORIG_HEAD
```

### Finding a Lost Commit's SHA

```bash
git fsck --lost-found          # Find all unreachable objects
ls .git/lost-found/commit/     # SHA files for each lost commit
git show sha                   # Inspect each one
git cat-file -p sha            # See commit details
```

---

## Stashing

### Basic Stashing

```bash
git stash                      # Stash tracked modifications and staged changes
git stash push -m "message"    # Stash with a description
git stash -u                   # Also stash untracked files
git stash -a                   # Also stash ignored files
git stash list                 # List all stashes
git stash show                 # Show summary of latest stash
git stash show -p              # Show diff of latest stash
git stash show stash@{2}       # Show specific stash

git stash pop                  # Apply latest stash and delete it
git stash apply                # Apply latest stash but keep it
git stash apply stash@{2}      # Apply specific stash
git stash drop                 # Delete latest stash
git stash drop stash@{2}       # Delete specific stash
git stash clear                # Delete all stashes

# Create a branch from a stash
git stash branch feature stash@{1}   # Create branch, apply stash, drop stash
```

### Partial Stashing

```bash
git stash -p                   # Interactively stash specific hunks (like git add -p)
git stash push -- file.txt     # Stash only a specific file
git stash push path/to/dir/    # Stash only a directory
```

### When to Stash vs When to Commit

```
Use stash when:
- You need to switch context quickly and changes aren't ready to commit
- You want to test something on a clean working directory
- You need to pull but have uncommitted changes

Use a WIP commit instead when:
- Changes will be gone for more than a few hours
- You're switching machines
- Stash history gets complicated

WIP commit approach:
git add -A && git commit -m "WIP: [description]"
# Later: git reset HEAD~1 to un-commit
```

---

## Related
- [[git/git-troubleshooting|Troubleshooting]] — the symptom-first version of this note
- [[git/03-the-three-trees|The Three Trees]] — `reset --soft/--mixed/--hard` maps exactly onto them
- [[git/01-how-git-works|How Git Actually Works]] — why nothing is really gone until `gc` runs
- [[git/README|Git course map]]
