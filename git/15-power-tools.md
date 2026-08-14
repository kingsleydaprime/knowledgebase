# Power Tools

**[Advanced]** — Submodules, worktrees, patch files and cherry-pick: the tools you reach for occasionally and want documented when you do.

## What Submodules Are

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

## Related
- [[git/06-rebasing|Rebasing]] — cherry-pick is the same replay machinery, one commit at a time
- [[git/09-investigating-history|Investigating History]] — the diff options here extend `git diff`
- [[git/02-configuration-and-setup|Configuration and Setup]] — `clone --recurse-submodules`
- [[git/README|Git course map]]
