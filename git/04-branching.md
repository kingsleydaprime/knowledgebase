# Branching

**[Beginner]** — Creating, listing, switching and deleting branches; tracking branches and what `ahead`/`behind` mean; and how to get out of a detached HEAD.

## Branch Commands

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

## Related
- [[git/05-merging|Merging]] — bringing a branch back
- [[git/13-branching-strategies|Branching Strategies]] — the team patterns these commands serve
- [[git/08-remotes-and-collaboration|Remotes and Collaboration]] — where tracking branches point
- [[git/README|Git course map]]
