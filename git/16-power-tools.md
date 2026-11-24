---
id: e4c37a1b-9732-450f-af6f-1b9fd4eab157
---

# Power Tools

Git's power tools are the less common features you reach for in special cases, such as submodules, worktrees and patches. A submodule puts one Git project inside another, and a worktree lets you have two branches open in separate folders at the same time. Most days you will not need them, but they save a lot of trouble when you do.

## What Submodules Are
<!-- bite: 5346b5f8-b6e4-40e2-8390-0d16919a652c -->

A submodule is a Git repository embedded inside another Git repository. The parent repo stores a reference to a specific commit in the submodule — not the submodule's files directly. Useful for including shared libraries, common components, or external dependencies you want to pin to a specific version.

**Submodules are complex.** Only use them when you have a genuine need to include one repo inside another and pin it to a specific commit. Many teams use package managers instead.

```bash
# Adding a submodule
git submodule add https://github.com/org/lib.git path/to/submodule
git submodule add -b main https://github.com/org/lib.git path/to/lib  # Track a branch

# This creates:
# - A directory at path/to/submodule (the submodule repo)
# - A .gitmodules file with the submodule config
# - A commit-like entry in the parent repo's tree

# Cloning a repo with submodules
git clone --recurse-submodules url
# Or for existing clones:
git submodule init
git submodule update
# Combined:
git submodule update --init --recursive
```

## Working with Submodules
<!-- bite: c9d60547-5fc4-4391-a287-2569b71969f2 -->

```bash
# Update all submodules to their recorded commits
git submodule update --recursive

# Update submodules to latest commit on their tracked branch
git submodule update --remote

# Run a command in each submodule
git submodule foreach 'git pull origin main'
git submodule foreach --recursive 'git status'

# Check submodule status
git submodule status

# Change submodule URL
git submodule set-url path/to/sub new-url

# Remove a submodule
git submodule deinit path/to/sub    # Deregister
git rm path/to/sub                  # Remove from index and working tree
rm -rf .git/modules/path/to/sub     # Remove submodule's git data
```

---

## Git Worktrees
<!-- bite: 3498d30d-b996-427c-b1cb-f32ff75aae96 -->

### What Worktrees Are

A worktree is a linked working directory attached to a repository. Instead of cloning the repo again to work on two branches simultaneously, you create a new worktree — same git history, different branch, different directory.

**Use case:** You're deep in a feature and need to make an urgent hotfix on main. Instead of stashing everything and switching branches, create a worktree for the hotfix.

```bash
# Create a worktree for hotfix on main
git worktree add ../hotfix main         # Create ../hotfix directory on main branch
git worktree add ../hotfix -b hotfix/critical  # Create with new branch

# Work in the new worktree (different terminal/directory)
cd ../hotfix
# Make changes, commit, push

# List worktrees
git worktree list

# Remove a worktree
git worktree remove ../hotfix          # Remove linked worktree
git worktree prune                     # Clean up stale worktree info
```

### Worktrees vs Cloning Again

| | Worktree | Clone |
|---|---|---|
| Shared git history | Yes | No (separate .git) |
| Disk usage | Minimal | Full copy |
| Can be on same branch | No | Yes |
| Setup time | Instant | Slow (download) |
| Best for | Quick context switches | Independent experiments |

---

---

## Advanced Diff and Patch
<!-- bite: 95e18ad3-1982-48d6-bf79-f553c6022b5c -->

### Advanced Diff Options

```bash
git diff --word-diff            # Word-level diff (good for documentation)
git diff --word-diff=color      # Coloured word diff
git diff --color-words          # Similar to word-diff=color
git diff --ignore-whitespace    # Ignore all whitespace
git diff -b                     # Ignore whitespace changes
git diff -w                     # Ignore all whitespace
git diff --ignore-blank-lines   # Ignore blank line changes
git diff --diff-filter=M        # Only modified files
git diff --diff-filter=A        # Only added files
git diff --diff-filter=D        # Only deleted files
git diff --diff-filter=R        # Only renamed files
git diff --name-only            # Only filenames, no content
git diff --name-status          # Filenames with status (M, A, D, R)
git diff --stat                 # Summary: files changed, insertions, deletions
git diff --compact-summary      # More compact stat
git diff -U10                   # Show 10 lines of context (default is 3)
```

### Creating and Applying Patches

```bash
# Create a patch file
git diff > my-changes.patch                    # Working directory changes
git diff HEAD~3 > last-3-commits.patch         # Specific commits
git format-patch HEAD~3                        # 3 separate .patch files, one per commit
git format-patch -1 HEAD                      # Just the latest commit
git format-patch main..feature                # All commits in feature not in main
git format-patch main..feature --stdout > feature.patch  # Single file

# Apply patches
git apply my-changes.patch                    # Apply a diff patch
git apply --check my-changes.patch            # Check if patch applies cleanly
git apply --stat my-changes.patch             # Show what would be applied
git am feature.patch                          # Apply a format-patch patch (preserves author)
git am --abort                                # Abort failed am
git am --continue                             # Continue after resolving conflict
```

### Cherry-Pick

Cherry-pick applies the changes from a specific commit onto your current branch. Useful for pulling a specific bug fix from one branch to another without merging everything.

```bash
git cherry-pick a1b2c3d                       # Apply commit a1b2c3d
git cherry-pick a1b2c3d b2c3d4e               # Apply two commits
git cherry-pick a1b2c3d..e5f6g7h              # Apply a range
git cherry-pick -n a1b2c3d                    # Apply without committing (stage only)
git cherry-pick -x a1b2c3d                    # Append "(cherry picked from commit...)" to message
git cherry-pick --edit a1b2c3d                # Edit message before committing
git cherry-pick --abort                       # Abort on conflict
git cherry-pick --continue                    # Continue after resolving conflict
```

---

## Check your understanding
<!-- bite: ae3749f2-e0d6-4991-b40e-453532ebdbf6 -->

Try each one before you open the answer.

1. <!-- q: mcq id="413f4878" -->
   A bug fix landed on `develop` as commit `a1b2c3d`, and you need exactly that fix on `release/2.0` without bringing anything else from `develop`. What do you use?

   - [ ] `git merge develop`
   - [x] `git cherry-pick a1b2c3d`
   - [ ] `git rebase develop`
   - [ ] `git submodule update`

   <details><summary>Answer</summary>

   Cherry-pick. It applies the changes of that one commit as a new commit on your current branch. Add `-x` to record where it came from in the message.

   </details>

2. <!-- q: mcq id="5da0af28" -->
   You are halfway through a feature and need to fix an urgent bug on `main` without stashing anything. Which tool lets you have both branches checked out at once in two folders, sharing one history?

   - [ ] A second `git clone`
   - [x] `git worktree add ../hotfix main`
   - [ ] `git submodule add`
   - [ ] `git stash branch`

   <details><summary>Answer</summary>

   A worktree. It is a second working folder linked to the same repository, so it is instant and uses almost no extra disk. A fresh clone would also work, but it downloads everything again and has a separate history.

   </details>

3. <!-- q: mcq id="801992a5" -->
   What does a parent repository store for a submodule?

   - [ ] A full copy of the submodule's files
   - [x] A pointer to one specific commit in the submodule
   - [ ] The submodule's latest branch, always updated
   - [ ] Nothing; submodules are separate projects

   <details><summary>Answer</summary>

   One pinned commit. The submodule stays where it is until you update it, for example with `git submodule update --remote` and a new commit in the parent.

   </details>

4. <!-- q: exact id="8feee2ec" answer="git submodule update --init --recursive" -->
   You cloned a repository without `--recurse-submodules`, and the submodule folders are empty. What single command fills them in, including submodules inside submodules?

   <details><summary>Answer</summary>

   `git submodule update --init --recursive`.

   </details>

5. <!-- q: mcq id="c61cd466" -->
   You want to send three commits by email so the receiver can apply them with the original authors and messages kept. Which pair of commands?

   - [ ] `git diff > changes.patch` and `git apply`
   - [x] `git format-patch` and `git am`
   - [ ] `git stash` and `git stash pop`
   - [ ] `git cherry-pick` and `git revert`

   <details><summary>Answer</summary>

   `git format-patch` writes each commit as a patch with its author and message, and `git am` applies them as commits. A plain `git diff` patch carries only the changes, with no commit information.

   </details>

## Related
<!-- bite: 98143d97-dec3-473a-b61a-2218b333d0db -->
- [[git/06-rebasing|Rebasing]] — cherry-pick is the same replay machinery, one commit at a time
- [[git/09-investigating-history|Investigating History]] — the diff options here extend `git diff`
- [[git/02-configuration-and-setup|Configuration and Setup]] — `clone --recurse-submodules`
- [[git/index|Git course map]]

## About this lesson
<!-- bite: f11f5f5b-6f73-4ebc-b532-3c50c8d926d9 -->

**Level:** Advanced. **Covers:** Submodules, worktrees, patch files and cherry-pick: the tools you reach for occasionally and want documented when you do.
