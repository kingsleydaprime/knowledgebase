---
id: a6c85929-128a-48ae-be4f-62de6404a892
---

# Merging

Merging is joining the work from one branch into another, so both sets of changes end up together. Usually Git does this by itself. When two people changed the same lines, Git asks you to choose, and that is called a merge conflict.

## What Merge Does
<!-- bite: f45c4e7c-3a1a-4475-a784-97189654154e -->

Merge takes two branch tips and creates a new commit that has both as parents. The new commit's tree represents the combined state of both branches. Git's merge algorithm finds the common ancestor (merge base) and applies changes from both sides.

```text
Before:          After merge:
     A---B---C  feature        A---B---C  feature
    /                         /           \
D---E---F---G  main      D---E---F---G---H  main
                                           ↑
                                     merge commit
                                     (two parents: C and G)
```

## Fast-Forward Merge
<!-- bite: 633ac79b-7177-417b-9f5a-6b6603c841d1 -->

If the target branch hasn't moved since the feature branch was created, Git can simply move the branch pointer forward — no merge commit needed. The history is linear.

```text
Before:          After ff merge:
     A---B---C  feature        
    /                         
D---E  main      D---E---A---B---C  main (feature)
```

```bash
git checkout main
git merge feature                     # Fast-forward if possible
git merge --ff-only feature           # Fail if fast-forward isn't possible
git merge --no-ff feature             # Always create a merge commit
git merge --no-ff -m "merge message" feature  # Custom merge commit message
```

## Three-Way Merge
<!-- bite: 5153a9d6-2f40-4881-907a-ece75ae3500b -->

When both branches have diverged (both have commits since their common ancestor), Git performs a three-way merge:
1. Find the merge base (common ancestor)
2. Compare each branch's changes to the base
3. Apply both sets of changes to the base

If changes touch different parts of the code — automatic merge. If both branches changed the same lines — **merge conflict**.

## Resolving Merge Conflicts
<!-- bite: 66c194e7-28d6-4e0a-b5fe-c14e6b0b5c2b -->

```bash
git merge feature               # Conflict!
git status                      # Shows conflicting files

# Conflict markers in the file:
<<<<<<< HEAD
    current branch content
=======
    incoming branch content
>>>>>>> feature

# With diff3 style (set merge.conflictstyle = diff3 in config):
<<<<<<< HEAD
    current branch content
||||||| base
    original content (the merge base)
=======
    incoming branch content
>>>>>>> feature
# Seeing the base is extremely helpful for understanding what changed

# Resolution options:
git checkout --ours file.txt    # Take our version entirely
git checkout --theirs file.txt  # Take their version entirely
# Or manually edit the file to the correct state

# After resolving:
git add file.txt                # Mark as resolved
git merge --continue            # Continue merge
# Or:
git commit                      # Complete the merge

# Abort a merge
git merge --abort               # Return to pre-merge state
```

## Merge Strategies
<!-- bite: 6a2200fe-7580-439d-b51b-accbbc898b5a -->

```bash
# Default — recursive (for two branches)
git merge feature

# Ours — always take our version (useful for "overwrite with our version")
git merge -s ours feature

# Subtree — like recursive but remaps the tree
git merge -s subtree --squash feature

# Octopus — merge more than two branches at once
git merge feature1 feature2 feature3

# Squash merge — apply all feature commits as a single unstaged change
git merge --squash feature
git commit -m "feat: implement feature X"
# Use when you want a clean single commit but don't want to rebase
```


---

## Related
<!-- bite: 0118d34e-651d-4c3b-8bd0-067f377cd617 -->
- [[git/06-rebasing|Rebasing]] — the other way to integrate
- [[git/07-merge-vs-rebase|Merge vs Rebase]] — choosing between them
- [[git/04-branching|Branching]] — what you are merging
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 3ee9792d-77fc-46e3-8b0b-9e83927d9340 -->

**Level:** Intermediate. **Covers:** Fast-forward vs three-way merges, reading and resolving conflict markers, and the merge strategies beyond the default.
