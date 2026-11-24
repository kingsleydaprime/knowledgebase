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

## Check your understanding
<!-- bite: c3a08931-9799-4be1-9600-cab2a63401fc -->

Try each one before you open the answer.

1. <!-- q: mcq id="52a58351" -->
   What is the difference between `git fetch` and `git pull`?

   - [ ] There is none
   - [x] `fetch` downloads remote changes without touching your branch; `pull` fetches and then merges or rebases them in
   - [ ] `fetch` uploads; `pull` downloads
   - [ ] `pull` only works on `main`

   <details><summary>Answer</summary>

   `pull` is `fetch` plus integrating. Fetching first lets you look at what's new (`git log HEAD..origin/main`) before deciding to merge it.

   </details>

2. <!-- q: mcq id="238d41cd" -->
   You run `git pull --ff-only` and your branch has diverged from the remote. What happens?

   - [ ] Git makes a merge commit
   - [ ] Git rebases your commits
   - [x] Git refuses, and your branch is left unchanged
   - [ ] Git deletes your local commits

   <details><summary>Answer</summary>

   It refuses. `--ff-only` only moves your branch forward when that needs no merge. That's why it's the safest pull: it never creates a merge or rewrites anything without you deciding.

   </details>

3. <!-- q: exact id="840b8d15" answer="git push origin --delete old-feature" accept="git push origin :old-feature" -->
   What command deletes the branch `old-feature` from the remote `origin`?

   <details><summary>Answer</summary>

   `git push origin --delete old-feature`. The older form is `git push origin :old-feature`.

   </details>

4. <!-- q: gap id="072afd99" answers="origin;upstream" -->
   In the fork workflow, the remote pointing at your own fork is usually called ___, and the remote pointing at the original project is usually called ___.

   <details><summary>Answer</summary>

   `origin` for your fork, `upstream` for the original. You fetch from `upstream` to stay up to date and push to `origin`, then open a pull request.

   </details>

5. <!-- q: open id="036fa9c3" -->
   A teammate pushed two commits to your shared branch while you were rewriting it. Explain what `git push --force` and `git push --force-with-lease` would each do.

   <details><summary>Answer</summary>

   `--force` replaces the remote branch with yours, so your teammate's two commits disappear from it. `--force-with-lease` first checks that the remote is still where you last fetched it. Because it moved, the push fails, and you can fetch, include their work, and try again.

   </details>

## Related
<!-- bite: bbe1d025-52ab-4cce-9941-99339a3f1f24 -->
- [[git/13-branching-strategies|Branching Strategies]] — the forking workflow in full
- [[git/14-github-and-ci|GitHub as a Platform]] — the rules a remote enforces on push
- [[git/04-branching|Branching]] — tracking branches
- [[git/index|Git course map]]

## About this lesson
<!-- bite: f88a41b8-be5d-4cc1-9462-1b97b98efead -->

**Level:** Beginner → Intermediate. **Covers:** `fetch` vs `pull`, pushing safely (including why `--force-with-lease` exists), and the fork + upstream workflow.
