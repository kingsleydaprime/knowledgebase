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

## Check your understanding
<!-- bite: a2057f58-13f5-496e-99e2-f9620a931499 -->

Try each one before you open the answer.

1. <!-- q: mcq id="ebdca70f" -->
   `main` hasn't moved since you branched `feature` off it, and `feature` has 3 new commits. What does `git merge feature` on `main` do?

   - [ ] Creates a merge commit with two parents
   - [x] Fast-forwards: moves the `main` pointer up to the tip of `feature`
   - [ ] Squashes the 3 commits into one
   - [ ] Refuses, because the branches have diverged

   <details><summary>Answer</summary>

   A fast-forward. No merge commit is needed, because `main` can simply move forward along `feature`'s commits. Use `--no-ff` if you want a merge commit anyway.

   </details>

2. <!-- q: exact id="23f6858c" answer="2" -->
   `main` and `feature` both have new commits since they split. You merge `feature` into `main` and Git creates a merge commit. How many parents does it have?

   <details><summary>Answer</summary>

   2: the previous tip of `main` and the tip of `feature`. That's how the history records that two lines of work joined.

   </details>

3. <!-- q: mcq id="cd207efa" -->
   When does a three-way merge stop with a conflict?

   - [ ] Whenever both branches changed the same file
   - [x] When both branches changed the same lines since the merge base
   - [ ] Whenever the branches have diverged
   - [ ] When one branch deleted a commit

   <details><summary>Answer</summary>

   Same lines. Git compares each side with the merge base, their common ancestor. Changes in different parts of the same file merge on their own.

   </details>

4. <!-- q: mcq id="07d784d2" -->
   You resolved the conflict markers in `config.yml` by editing the file. What comes next?

   - [ ] `git merge --abort`
   - [x] `git add config.yml`, then `git merge --continue` (or `git commit`)
   - [ ] `git checkout --theirs config.yml`
   - [ ] Nothing; Git notices the markers are gone

   <details><summary>Answer</summary>

   Stage the file to mark it as resolved, then finish the merge. `git merge --abort` would throw the merge away and go back to how things were before it.

   </details>

5. <!-- q: open id="3a351ec2" -->
   What does `git merge --squash feature` do, and when would you use it?

   <details><summary>Answer</summary>

   It applies all of `feature`'s changes to your branch as one uncommitted change, with no merge commit. You then commit it yourself as a single commit. Use it when the feature's history is messy ("wip", "fix typo") and you want one clean commit on `main` without rebasing.

   </details>

## Related
<!-- bite: 0118d34e-651d-4c3b-8bd0-067f377cd617 -->
- [[git/06-rebasing|Rebasing]] — the other way to integrate
- [[git/07-merge-vs-rebase|Merge vs Rebase]] — choosing between them
- [[git/04-branching|Branching]] — what you are merging
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 3ee9792d-77fc-46e3-8b0b-9e83927d9340 -->

**Level:** Intermediate. **Covers:** Fast-forward vs three-way merges, reading and resolving conflict markers, and the merge strategies beyond the default.
