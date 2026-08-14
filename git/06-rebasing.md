# Rebasing

**[Intermediate → Advanced]** — What replaying commits actually does to their SHAs, interactive rebase as a history-editing tool, `fixup!` commits, and `--onto`.

## What Rebase Does

Rebase moves or replays commits from one branch onto another. Instead of a merge commit, it creates new commits with the same changes but different parent commits.

```
Before:          After rebase (feature onto main):
     A---B---C  feature             A'--B'--C'  feature
    /                              /
D---E---F---G  main      D---E---F---G  main
```

A', B', C' are new commits — same changes as A, B, C but with different SHAs because their parent changed. The old A, B, C commits become orphaned.

**The golden rule of rebasing: never rebase commits that have been pushed to a shared remote branch.** Rebasing rewrites history. If others have based work on your old commits, rewriting them creates a nightmare.

## Basic Rebase

```bash
git checkout feature
git rebase main                 # Replay feature commits on top of main

# What rebase does step by step:
# 1. Find the common ancestor of feature and main
# 2. Save the diff of each commit since the ancestor
# 3. Reset feature to the same commit as main
# 4. Apply each saved diff as a new commit
```

## Interactive Rebase

Interactive rebase (`-i`) is one of Git's most powerful features. It lets you rewrite the history of a series of commits before sharing them: reorder, edit, squash, drop, or split commits.

```bash
git rebase -i HEAD~5            # Interactively rebase last 5 commits
git rebase -i main              # Interactively rebase everything since branching from main
git rebase -i a1b2c3d           # Interactively rebase since a specific commit
```

The editor opens with a list of commits (oldest first) and commands:

```
pick a1b2c3d feat: add login endpoint
pick b2c3d4e fix: correct typo in login
pick c3d4e5f feat: add logout endpoint
pick d4e5f6g test: add auth tests
pick e5f6g7h docs: update auth docs

# Commands:
# p, pick   = use commit as-is
# r, reword = use commit, but edit the commit message
# e, edit   = use commit, but stop for amending
# s, squash = meld into previous commit (keeps both messages)
# f, fixup  = like squash but discard this commit's message
# d, drop   = remove commit entirely
# x, exec   = run shell command
# b, break  = stop here (continue rebase later with git rebase --continue)
# l, label  = label current HEAD with a name
# t, reset  = reset HEAD to a label
# m, merge  = create a merge commit
```

**Common interactive rebase operations:**

```bash
# Squash the typo fix into the feature commit:
pick a1b2c3d feat: add login endpoint
fixup b2c3d4e fix: correct typo in login   # ← change pick to fixup
pick c3d4e5f feat: add logout endpoint

# Reorder commits:
pick c3d4e5f feat: add logout endpoint     # ← moved up
pick a1b2c3d feat: add login endpoint
pick d4e5f6g test: add auth tests

# Drop a commit:
drop e5f6g7h docs: update auth docs        # ← this commit disappears

# Edit a commit (stop and amend it):
edit a1b2c3d feat: add login endpoint      # ← git stops here
# Then: make changes, git add, git commit --amend, git rebase --continue
```

## Fixup Commits

`fixup!` and `squash!` are special commit message prefixes that work with `git rebase --autosquash`:

```bash
# Make a normal commit
git commit -m "feat: add payment processing"

# Later, realise you have a small fix for that commit
git add fix.js
git commit -m "fixup! feat: add payment processing"
# The message must match exactly (or be a prefix of) the target commit

# When you rebase with --autosquash, Git automatically
# moves the fixup! commit next to its target and marks it as fixup
git rebase -i --autosquash main

# With autoSquash = true in config (recommended), --autosquash is always on
```

## Rebase onto Another Branch

```bash
# Move a branch to a different base
# Before: feature-b was branched from feature-a (which is unmerged)
# You want to move feature-b to be based on main instead

git rebase --onto main feature-a feature-b
# --onto target  from  branch
# "Replay commits that are on feature-b but not on feature-a, onto main"
```

## Handling Rebase Conflicts

```bash
git rebase main                 # Conflict on commit B

# The conflict is in a single commit — resolve it, then:
git add resolved-file.txt
git rebase --continue           # Apply next commit

# Skip a commit entirely (use with care)
git rebase --skip

# Abort and return to pre-rebase state
git rebase --abort
```


---

## Related
- [[git/07-merge-vs-rebase|Merge vs Rebase]] — the rules for when this is safe
- [[git/01-how-git-works|How Git Actually Works]] — why rewriting produces new SHAs
- [[git/10-undoing-things|Undoing Things]] — the reflog is how you survive a bad rebase
- [[git/README|Git course map]]
