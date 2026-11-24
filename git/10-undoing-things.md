---
id: c0ced81a-24af-418b-afc6-913900de0832
---

# Undoing Things

This is where most confusion happens. There are multiple ways to undo in Git, and choosing the wrong one can make things worse.

## The Undo Decision Tree
<!-- bite: 0fb459e0-5d78-477e-adf3-a6d06143b5c4 -->

```text
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
<!-- bite: 73841b44-a954-4962-ac66-01a08e48db61 -->

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
<!-- bite: fff6ad80-4249-48be-a59d-5d834fed79db -->

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
<!-- bite: ffd72d6b-0891-4c25-b3cd-c5d402f256d8 -->

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
<!-- bite: 3a61359e-dc9b-4682-9b01-3601fca14cf7 -->

If you did `git reset --hard` and lost commits, or if you deleted a branch — the commits aren't gone immediately. Git keeps them in the reflog for 30 days (90 days for unreachable commits with `gc.reflogExpireUnreachable`).

See **The Reflog — Your Safety Net** below.

---

## The Reflog — Your Safety Net
<!-- bite: 7dd4ebcc-4cdc-48e8-8026-fb868c271f5e -->

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
<!-- bite: c1454cef-3db8-4949-8939-ef95ba9b7b92 -->

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

```text
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

## Check your understanding
<!-- bite: 58a2ae78-4f8c-4fd3-80ff-9031773e1f73 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a6b1bac4" -->
   You committed too early and want to undo the last commit, keeping its changes staged so you can recommit them differently. Which command?

   - [x] `git reset --soft HEAD~1`
   - [ ] `git reset --mixed HEAD~1`
   - [ ] `git reset --hard HEAD~1`
   - [ ] `git revert HEAD`

   <details><summary>Answer</summary>

   `--soft`. It moves HEAD back and leaves both the index and your files alone, so everything is still staged. `--mixed` unstages the changes, and `--hard` throws them away.

   </details>

2. <!-- q: mcq id="f93f93c3" -->
   A bad commit was pushed to `main` an hour ago and three teammates have already pulled. How do you undo it?

   - [ ] `git reset --hard HEAD~1`, then force-push
   - [x] `git revert <sha>`, then push
   - [ ] `git commit --amend`
   - [ ] Delete the branch and push it again

   <details><summary>Answer</summary>

   `git revert`. It adds a new commit that undoes the bad one, so no history is rewritten and your teammates' copies stay valid. Resetting and force-pushing would rewrite history they already have.

   </details>

3. <!-- q: gap id="96ed726f" answers="index;working directory|working tree" -->
   `git reset --mixed HEAD~1` moves HEAD back one commit and resets the ___ to match it, but leaves the ___ unchanged, so the changes show as unstaged.

   <details><summary>Answer</summary>

   The index, then the working directory. `--mixed` is the default mode of `git reset`.

   </details>

4. <!-- q: mcq id="628d99d4" -->
   You ran `git reset --hard HEAD~3` and lost three commits you needed. What is the first thing to look at?

   - [ ] `git log`
   - [x] `git reflog`
   - [ ] `git stash list`
   - [ ] Nothing; they are gone for good

   <details><summary>Answer</summary>

   The reflog. It records every move of HEAD, including where it was before the reset. Find that SHA and run `git reset --hard <sha>` or `git branch recovered <sha>`. Unreachable commits stay recoverable for weeks before garbage collection.

   </details>

5. <!-- q: mcq id="74da0d61" -->
   What is the difference between `git stash pop` and `git stash apply`?

   - [ ] `pop` applies all stashes, `apply` only the newest
   - [x] `pop` applies the newest stash and deletes it; `apply` applies it and keeps it
   - [ ] `apply` also stashes untracked files
   - [ ] There is no difference

   <details><summary>Answer</summary>

   `pop` = apply then drop. `apply` keeps the stash in the list, which is handy if you want to apply it to more than one branch.

   </details>

6. <!-- q: open id="6097aced" -->
   Your changes need to wait for two days while you work on something urgent on another branch. Why does the lesson suggest a WIP commit instead of a stash here?

   <details><summary>Answer</summary>

   Stashes are easy to lose track of over days: the list grows, the names are vague, and they live only on this machine. A WIP commit sits on its own branch where you'll find it, and you can push it. When you come back, `git reset HEAD~1` turns it back into uncommitted changes.

   </details>

## Related
<!-- bite: 310dff3d-de2c-47d5-ba99-bc5b575fb2c2 -->
- [[git/git-troubleshooting|Troubleshooting]] — the symptom-first version of this note
- [[git/03-the-three-trees|The Three Trees]] — `reset --soft/--mixed/--hard` maps exactly onto them
- [[git/01-how-git-works|How Git Actually Works]] — why nothing is really gone until `gc` runs
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 6ec3bfca-8150-40d2-8697-2c83914fe5e6 -->

**Level:** Intermediate. **Covers:** Where most Git confusion lives. A decision tree first, then `reset` vs `revert` vs `restore`, the reflog as a safety net, and stashing.
