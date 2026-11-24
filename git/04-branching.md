---
id: 97a54d0f-e435-467d-bdf0-ed674a82217c
---

# Branching

A branch in Git is a separate line of work inside the same project, so you can try a change without touching the main version. When the change is ready, you bring it back in. It is like writing a draft essay on a copy of your notes, so the clean copy stays safe until you are happy with the draft.

## Branch Commands
<!-- bite: e8597352-2978-4bc9-a01c-830ddd3da1c5 -->

```bash
git branch                     # List local branches
git branch -r                  # List remote tracking branches
git branch -a                  # List all branches (local + remote)
git branch -v                  # Branches with last commit message
git branch -vv                 # Branches with upstream tracking info
git branch feature             # Create branch (stay on current branch)
git branch -d feature          # Delete merged branch
git branch -D feature          # Force delete (even if unmerged)
git branch -m old-name new-name  # Rename branch
git branch -m new-name         # Rename current branch
git branch --merged            # Branches merged into current
git branch --no-merged         # Branches not yet merged

# Switching branches
git checkout branch-name       # Switch to branch
git checkout -b branch-name    # Create and switch
git checkout -b feature origin/feature  # Create tracking an existing remote branch
git switch branch-name         # Modern syntax (git 2.23+)
git switch -c branch-name      # Modern: create and switch
git switch -                   # Switch to previous branch

# Create branch from specific point
git checkout -b feature main          # Branch from main
git checkout -b feature v1.2.0        # Branch from tag
git checkout -b feature a1b2c3d       # Branch from commit SHA
```

## Tracking Branches
<!-- bite: 71af2e5d-4315-485f-88da-fa2b485b22f3 -->

A tracking branch is a local branch that has a relationship with a remote branch. It knows where to push and pull by default.

```bash
# Set upstream for an existing branch
git branch --set-upstream-to=origin/main main
git branch -u origin/feature feature

# Push and set upstream in one command
git push -u origin feature      # -u sets the upstream

# See tracking info
git branch -vv
# * main    a1b2c3d [origin/main] feat: add auth
#   feature b2c3d4e [origin/feature: ahead 2] feat: user profile

# ahead N  — you have N commits not pushed
# behind N — remote has N commits not pulled
# ahead 2, behind 1 — diverged (need to merge or rebase)
```

## Detached HEAD
<!-- bite: 6c8b4f41-9763-4494-920b-911524378a78 -->

Detached HEAD means HEAD points directly to a commit SHA, not to a branch. Any commits you make won't belong to any branch and can be garbage-collected.

```bash
git checkout a1b2c3d            # Detach HEAD at this commit
git checkout v1.2.0             # Detach HEAD at a tag
git log --oneline HEAD~5..HEAD  # Look around without detaching

# If you made commits in detached HEAD and want to keep them:
git branch new-branch           # Create branch at current position
# Or:
git checkout -b new-branch      # Create and switch
```


---

## Check your understanding
<!-- bite: 0ec0a2fc-74ff-43fe-9364-78c846967aa5 -->

Try each one before you open the answer.

1. <!-- q: exact id="bb772af9" answer="git switch -c login-page" accept="git checkout -b login-page" -->
   What single command creates a branch called `login-page` and switches to it, using the modern syntax?

   <details><summary>Answer</summary>

   `git switch -c login-page`. The older form is `git checkout -b login-page`.

   </details>

2. <!-- q: mcq id="ded0af1e" -->
   `git branch -vv` shows `feature b2c3d4e [origin/feature: ahead 3, behind 1]`. What does this mean?

   - [ ] You have 3 unpushed commits and the remote has no new ones
   - [x] You have 3 commits the remote doesn't, and the remote has 1 you don't, so the branches have diverged
   - [ ] The remote is 3 commits ahead of you
   - [ ] There are 3 merge conflicts

   <details><summary>Answer</summary>

   Diverged. Ahead 3 means three local commits not pushed; behind 1 means one remote commit not pulled. You need to merge or rebase before you can push normally.

   </details>

3. <!-- q: mcq id="7f63532f" -->
   You try `git branch -d experiment` and Git refuses, saying the branch isn't fully merged. What does `git branch -D experiment` do differently?

   - [ ] It merges the branch first, then deletes it
   - [x] It deletes the branch anyway, even though its commits aren't merged anywhere
   - [ ] It deletes the remote branch too
   - [ ] It only renames the branch

   <details><summary>Answer</summary>

   `-D` force-deletes. The unmerged commits then belong to no branch. They can still be found in the reflog for a while, but make sure you don't need them.

   </details>

4. <!-- q: open id="a5c4dd2a" -->
   You checked out an old commit with `git checkout a1b2c3d`, made two commits, and want to keep them. Why are they at risk, and what do you do?

   <details><summary>Answer</summary>

   This is detached HEAD: HEAD points straight at a commit, not at a branch, so the new commits belong to no branch. Switch away and nothing points at them, and Git can eventually garbage-collect them. Run `git branch keep-this` (or `git switch -c keep-this`) while you're still there, so a branch points at them.

   </details>

5. <!-- q: exact id="b0737168" answer="git push -u origin search" accept="git push --set-upstream origin search" -->
   You created a local branch called `search`. What command pushes it to `origin` and sets it as the upstream, so later plain `git push` and `git pull` know where to go?

   <details><summary>Answer</summary>

   `git push -u origin search`. The `-u` sets the upstream (tracking) relationship.

   </details>

## Related
<!-- bite: 0d3ad197-2135-45e0-b10b-a463ce2cedaa -->
- [[git/05-merging|Merging]] — bringing a branch back
- [[git/13-branching-strategies|Branching Strategies]] — the team patterns these commands serve
- [[git/08-remotes-and-collaboration|Remotes and Collaboration]] — where tracking branches point
- [[git/index|Git course map]]

## About this lesson
<!-- bite: df9a04c9-5fa2-436d-baeb-bec77ca24f82 -->

**Level:** Beginner. **Covers:** Creating, listing, switching and deleting branches; tracking branches and what `ahead`/`behind` mean; and how to get out of a detached HEAD.
