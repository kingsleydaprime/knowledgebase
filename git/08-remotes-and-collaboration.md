---
id: 8cb6c959-1721-410f-b903-fab71084a958
---

# Remotes and Collaboration

A remote is a copy of your Git project kept somewhere else, usually on a site like GitHub, so other people can share it. You push your work up to it and pull other people's work down from it. It works a bit like a shared Google Drive folder, except every change is tracked and nothing is overwritten by accident.

## Fetching and Pulling
<!-- bite: cd446072-c148-439d-bea2-20516119bafa -->

```bash
# Fetch — download remote changes but don't integrate
git fetch                      # Fetch from all remotes
git fetch origin               # Fetch from origin
git fetch origin main          # Fetch specific branch
git fetch --all                # Fetch all remotes
git fetch --prune              # Also delete local refs to deleted remote branches

# Pull — fetch + integrate (merge or rebase depending on config)
git pull                       # Pull current branch from its upstream
git pull origin main           # Pull specific remote/branch
git pull --rebase              # Pull with rebase instead of merge
git pull --ff-only             # Only pull if fast-forward (safe — refuses if diverged)
git pull --no-ff               # Always create merge commit on pull

# The safest pull workflow:
git fetch origin               # Download without integrating
git log HEAD..origin/main      # See what's new
git merge origin/main          # Integrate when ready
```

## Pushing
<!-- bite: 7ea9e6e8-ec58-407b-8eb9-02ba8815206a -->

```bash
git push                       # Push current branch to its upstream
git push origin main           # Push to specific remote/branch
git push -u origin feature     # Push and set upstream tracking
git push --all                 # Push all branches
git push --tags                # Push all tags
git push origin :branch        # Delete remote branch (old syntax)
git push origin --delete branch  # Delete remote branch (modern)

# Force push (use with extreme caution)
git push --force               # DANGEROUS — overwrites remote history
git push --force-with-lease    # Safer — fails if remote has commits you haven't fetched
# Always use --force-with-lease over --force when you must force-push

# Push a specific local branch to a differently named remote branch
git push origin local-branch:remote-branch
```

## Working with Forks
<!-- bite: 8dbf0da9-bad6-41bc-8c54-78cba4abec3a -->

```bash
# Fork workflow
git clone https://github.com/you/repo.git   # Clone your fork
git remote add upstream https://github.com/original/repo.git  # Add upstream

# Keep fork updated
git fetch upstream
git checkout main
git merge upstream/main        # Or: git rebase upstream/main
git push origin main           # Push to your fork

# Open a PR: push your feature branch to your fork, then PR on GitHub
git push -u origin feature/my-feature
```


---

## Related
<!-- bite: bbe1d025-52ab-4cce-9941-99339a3f1f24 -->
- [[git/13-branching-strategies|Branching Strategies]] — the forking workflow in full
- [[git/14-github-and-ci|GitHub as a Platform]] — the rules a remote enforces on push
- [[git/04-branching|Branching]] — tracking branches
- [[git/index|Git course map]]

## About this lesson
<!-- bite: f88a41b8-be5d-4cc1-9462-1b97b98efead -->

**Level:** Beginner → Intermediate. **Covers:** `fetch` vs `pull`, pushing safely (including why `--force-with-lease` exists), and the fork + upstream workflow.
