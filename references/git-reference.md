# Git — Comprehensive Advanced Reference

> A deep reference covering Git from internals to advanced workflows.
> Not just what commands to run — but what Git is actually doing and why.
> Covers the object model, branching, merging, rebasing, history rewriting,
> collaboration patterns, hooks, signing, and production best practices.

---

## Table of Contents

1. [How Git Actually Works — The Internals](#1-how-git-actually-works--the-internals)
2. [Configuration](#2-configuration)
3. [Repository Setup and Cloning](#3-repository-setup-and-cloning)
4. [The Three Trees — Working Directory, Index, HEAD](#4-the-three-trees--working-directory-index-head)
5. [Staging and Committing](#5-staging-and-committing)
6. [Branching](#6-branching)
7. [Merging — Deep Reference](#7-merging--deep-reference)
8. [Rebasing — Deep Reference](#8-rebasing--deep-reference)
9. [Merge vs Rebase — When to Use Which](#9-merge-vs-rebase--when-to-use-which)
10. [Remote Repositories](#10-remote-repositories)
11. [History Inspection](#11-history-inspection)
12. [Undoing Things — The Complete Guide](#12-undoing-things--the-complete-guide)
13. [The Reflog — Your Safety Net](#13-the-reflog--your-safety-net)
14. [Stashing](#14-stashing)
15. [Tags](#15-tags)
16. [Git Bisect — Finding Bugs with Binary Search](#16-git-bisect--finding-bugs-with-binary-search)
17. [Submodules](#17-submodules)
18. [Git Worktrees](#18-git-worktrees)
19. [Git Hooks](#19-git-hooks)
20. [Signing Commits and Tags](#20-signing-commits-and-tags)
21. [Advanced Diff and Patch](#21-advanced-diff-and-patch)
22. [Git Workflows — Team Collaboration Patterns](#22-git-workflows--team-collaboration-patterns)
23. [Commit Message Best Practices](#23-commit-message-best-practices)
24. [Branch Naming Conventions](#24-branch-naming-conventions)
25. [Best Practices — The Full Picture](#25-best-practices--the-full-picture)
26. [Troubleshooting and Recovery](#26-troubleshooting-and-recovery)

---

## 1. How Git Actually Works — The Internals

### 1.1 Git is a Content-Addressable Filesystem

Most version control systems track changes (diffs). Git tracks **snapshots** — complete states of every file at every commit. Understanding this explains why Git is so fast and why operations like branching are nearly instantaneous.

Everything Git stores is an **object**, identified by a **SHA-1 hash** of its content. If two files have identical content, they share one object. If a file doesn't change between commits, the new commit just points to the same object — no duplication.

```bash
# See Git's object store
ls .git/objects/

# Inspect any object
git cat-file -t a1b2c3d    # Type: blob, tree, commit, or tag
git cat-file -p a1b2c3d    # Pretty-print the content
```

### 1.2 The Four Object Types

**Blob** — stores the content of a single file. No filename, no metadata. Just bytes.

**Tree** — stores a directory listing: a list of (mode, name, SHA) entries pointing to blobs (files) and other trees (subdirectories).

**Commit** — stores:
- A pointer to a tree (the root of the snapshot)
- A pointer to the parent commit (or multiple parents for merges)
- Author name, email, timestamp
- Committer name, email, timestamp
- The commit message

**Tag** — stores a pointer to another object (usually a commit) with a name, message, and optional signature.

```bash
# See what a commit actually contains
git cat-file -p HEAD
# tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
# parent a1b2c3d4e5f6...
# author Kingsley Ihemelandu <k@example.com> 1746000000 +0000
# committer Kingsley Ihemelandu <k@example.com> 1746000000 +0000
#
# feat: add user authentication

# See what a tree contains
git cat-file -p HEAD^{tree}
# 100644 blob a8c3f... README.md
# 040000 tree 9f7d2... src
# 100755 blob b2e4a... deploy.sh
```

### 1.3 Refs — Human-Readable Names for SHAs

Refs are files in `.git/refs/` that store a SHA. They're just pointers to objects.

```bash
cat .git/refs/heads/main          # The SHA of the latest commit on main
cat .git/refs/remotes/origin/main # What origin/main points to
cat .git/HEAD                     # What's currently checked out

# HEAD is special — it points to the current branch ref (or directly to a SHA in detached HEAD)
cat .git/HEAD
# ref: refs/heads/main   ← on a branch
# or
# a1b2c3d4e5f6...        ← detached HEAD
```

### 1.4 How a Commit Changes the Graph

When you make a commit, Git:
1. Creates blob objects for any changed files
2. Creates tree objects for affected directories
3. Creates a commit object pointing to the root tree and the parent commit
4. Moves the current branch ref to point at the new commit SHA

```
Before commit:
  main → C2 → C1

After commit:
  main → C3 → C2 → C1
  HEAD → main (still tracking main)
```

Branching is just creating a new ref file pointing at a commit. It costs nothing — just 41 bytes.

```bash
# What branch creation actually does
cat .git/refs/heads/main      # a1b2c3d4...
git checkout -b feature       # Creates .git/refs/heads/feature with same SHA
cat .git/refs/heads/feature   # a1b2c3d4... (same SHA, new ref)
```

### 1.5 The .git Directory

```
.git/
├── HEAD              # Current branch or commit
├── config            # Repo-level config
├── description       # Used by GitWeb (not important)
├── index             # The staging area (binary file)
├── COMMIT_EDITMSG    # Last commit message
├── MERGE_HEAD        # Present during a merge conflict
├── REBASE_HEAD       # Present during a rebase
├── hooks/            # Client-side hook scripts
├── info/             # exclude file (like .gitignore but not tracked)
├── logs/             # Reflog — history of where refs have pointed
│   ├── HEAD
│   └── refs/heads/main
├── objects/          # All objects (blobs, trees, commits, tags)
│   ├── pack/         # Packed objects (efficient storage)
│   └── info/
└── refs/             # Branch, tag, and remote refs
    ├── heads/        # Local branches
    ├── remotes/      # Remote tracking branches
    └── tags/         # Tags
```

---

## 2. Configuration

### 2.1 Config Levels

Git has three config levels, each overriding the previous:

```bash
git config --system   # /etc/gitconfig — applies to all users on the machine
git config --global   # ~/.gitconfig — applies to all your repos
git config --local    # .git/config — applies to this repo only
```

### 2.2 Essential Configuration

```bash
# Identity — required for commits
git config --global user.name "Kingsley Ihemelandu"
git config --global user.email "kingsley@example.com"

# Default branch name
git config --global init.defaultBranch main

# Default editor
git config --global core.editor nvim

# Default merge strategy
git config --global pull.rebase false    # merge on pull (explicit)
git config --global pull.rebase true     # rebase on pull
git config --global pull.ff only         # only fast-forward on pull (safest)

# Diff and merge tools
git config --global merge.tool vimdiff
git config --global diff.tool vimdiff

# Colour output
git config --global color.ui auto

# Credential caching
git config --global credential.helper cache               # Cache for 15 minutes
git config --global credential.helper 'cache --timeout=3600'  # 1 hour

# Line ending handling
git config --global core.autocrlf input    # Linux/Mac: convert CRLF to LF on commit
git config --global core.autocrlf true     # Windows: convert LF to CRLF on checkout

# Aliases (covered in section 2.3)
```

### 2.3 Useful Aliases

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.visual "!gitk"
git config --global alias.aliases "config --get-regexp alias"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.pushf "push --force-with-lease"  # Safe force push

# View all config
git config --list
git config --list --show-origin  # Show which file each setting comes from

# View specific setting
git config user.email
git config --global core.editor
```

### 2.4 The ~/.gitconfig File

```ini
[user]
	name = Kingsley Ihemelandu
	email = kingsley@example.com
	signingkey = YOUR_GPG_KEY_ID

[core]
	editor = nvim
	autocrlf = input
	excludesfile = ~/.gitignore_global

[init]
	defaultBranch = main

[pull]
	rebase = false

[push]
	default = current           # Push to same-name branch on remote
	autoSetupRemote = true      # Auto set upstream on first push

[commit]
	gpgsign = true              # Sign all commits

[tag]
	gpgsign = true              # Sign all tags

[rebase]
	autoStash = true            # Auto stash/unstash during rebase
	autoSquash = true           # Auto apply fixup! and squash! commits

[merge]
	conflictstyle = diff3       # Show base in conflict markers (very useful)
	tool = vimdiff

[diff]
	algorithm = histogram       # Better diff algorithm than default myers
	colorMoved = zebra          # Colour moved lines differently from added/removed

[alias]
	st = status
	co = checkout
	br = branch -vv
	ci = commit
	lg = log --oneline --graph --decorate --all
	lgs = log --oneline --graph --decorate
	unstage = reset HEAD --
	last = log -1 HEAD --stat
	amend = commit --amend --no-edit
	pushf = push --force-with-lease
	aliases = config --get-regexp alias
	wip = "!git add -A && git commit -m 'WIP'"
	undo = reset HEAD~1 --mixed
	stash-all = stash save --include-untracked

[color]
	ui = auto

[credential]
	helper = cache --timeout=3600
```

### 2.5 Global .gitignore

```bash
git config --global core.excludesfile ~/.gitignore_global
```

```
# ~/.gitignore_global — ignored in all repos
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
Thumbs.db
*.swp
*.swo
*~
.idea/
.vscode/
*.log
```

---

## 3. Repository Setup and Cloning

```bash
# Initialise
git init                           # Initialise in current directory
git init project-name              # Create directory and initialise
git init --bare repo.git           # Bare repo — no working tree (for servers)

# Clone
git clone url                      # Clone into directory named from URL
git clone url directory-name       # Clone into specific directory
git clone --depth 1 url            # Shallow clone — only latest commit (fast)
git clone --branch feature url     # Clone specific branch
git clone --single-branch url      # Only clone current branch (not all branches)
git clone --recurse-submodules url # Clone with all submodules
git clone --mirror url             # Mirror clone — for backups (bare + all refs)

# Adding remotes
git remote add origin url          # Add remote named origin
git remote add upstream url        # Add upstream (for forks)
git remote -v                      # List remotes with URLs
git remote show origin             # Detailed remote info
git remote rename origin old-name  # Rename remote
git remote remove origin           # Remove remote
git remote set-url origin new-url  # Change remote URL
```

---

## 4. The Three Trees — Working Directory, Index, HEAD

This is the most important conceptual model for understanding Git commands.

### 4.1 The Three Areas

**Working Directory** — The actual files on your disk. What you see in your editor. Untracked changes live here.

**Index (Staging Area)** — A proposed snapshot of your next commit. When you `git add`, you're moving changes from the working directory into the index. The index is a binary file at `.git/index`.

**HEAD** — A pointer to the last commit on your current branch. Represents the current snapshot of the repository.

```
Working Directory  →  git add  →  Index (Staging)  →  git commit  →  HEAD (Repository)

git diff               = Working Directory vs Index
git diff --staged      = Index vs HEAD
git diff HEAD          = Working Directory vs HEAD
```

### 4.2 File States

```bash
git status             # Show state of all files

# States:
# Untracked    — new file Git doesn't know about yet
# Tracked      — file Git knows about; can be:
#   Unmodified — same as HEAD
#   Modified   — changed in working directory but not staged
#   Staged     — in index, ready for next commit
# Ignored      — matched by .gitignore

git status -s          # Short status
# ?? file              — untracked
# A  file              — staged new file
# M  file              — modified and staged
#  M file              — modified but not staged
# MM file              — modified, partially staged
# D  file              — staged deletion
```

---

## 5. Staging and Committing

### 5.1 Staging

```bash
git add file.txt               # Stage specific file
git add directory/             # Stage entire directory
git add .                      # Stage all changes in current directory
git add -A                     # Stage all changes in entire repo
git add -u                     # Stage modifications and deletions (not new files)
git add -p                     # Interactive — stage hunks (chunks) selectively
git add -i                     # Interactive staging menu

# Interactive hunk staging (-p) — extremely useful
# y — stage this hunk
# n — skip this hunk
# s — split into smaller hunks
# e — manually edit the hunk
# q — quit
# a — stage all remaining hunks in this file
# d — skip all remaining hunks in this file
# ? — help

git restore --staged file.txt  # Unstage a file (keep working directory changes)
git restore file.txt           # Discard working directory changes (dangerous — unrecoverable)
```

### 5.2 Committing

```bash
git commit                     # Open editor to write commit message
git commit -m "message"        # Inline commit message
git commit -am "message"       # Stage all tracked changes and commit (skip git add)
git commit --amend             # Amend last commit (opens editor)
git commit --amend --no-edit   # Amend last commit keeping same message
git commit --amend -m "new"    # Amend with new message
git commit --allow-empty -m "trigger CI"  # Commit with no changes (useful for CI)

# Commit with detailed message (title + body)
git commit -m "feat: add user auth

Implements JWT-based authentication with:
- Login endpoint with bcrypt password validation
- Token refresh mechanism
- Role-based middleware guards

Closes #42"
```

### 5.3 .gitignore

```bash
# Patterns
file.txt               # Ignore specific file
*.log                  # Ignore all .log files
/build                 # Ignore build/ in root only (not src/build/)
build/                 # Ignore any directory named build
!important.log         # Un-ignore (negate a pattern)
**/logs                # Ignore logs/ in any subdirectory
doc/*.txt              # Ignore .txt in doc/ but not doc/sub/file.txt
doc/**/*.pdf           # Ignore all .pdf files anywhere under doc/

# Check why a file is ignored
git check-ignore -v filename

# Force-add an ignored file
git add -f ignored-file.txt

# List all ignored files
git ls-files --ignored --exclude-standard

# .gitignore only affects untracked files
# To stop tracking a file already committed:
git rm --cached file.txt           # Remove from index only (keep on disk)
git rm --cached -r directory/      # Recursive
echo "file.txt" >> .gitignore      # Then add to .gitignore
git commit -m "stop tracking file.txt"
```

---

## 6. Branching

### 6.1 Branch Commands

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

### 6.2 Tracking Branches

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

### 6.3 Detached HEAD

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

## 7. Merging — Deep Reference

### 7.1 What Merge Does

Merge takes two branch tips and creates a new commit that has both as parents. The new commit's tree represents the combined state of both branches. Git's merge algorithm finds the common ancestor (merge base) and applies changes from both sides.

```
Before:          After merge:
     A---B---C  feature        A---B---C  feature
    /                         /           \
D---E---F---G  main      D---E---F---G---H  main
                                           ↑
                                     merge commit
                                     (two parents: C and G)
```

### 7.2 Fast-Forward Merge

If the target branch hasn't moved since the feature branch was created, Git can simply move the branch pointer forward — no merge commit needed. The history is linear.

```
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

### 7.3 Three-Way Merge

When both branches have diverged (both have commits since their common ancestor), Git performs a three-way merge:
1. Find the merge base (common ancestor)
2. Compare each branch's changes to the base
3. Apply both sets of changes to the base

If changes touch different parts of the code — automatic merge. If both branches changed the same lines — **merge conflict**.

### 7.4 Resolving Merge Conflicts

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

### 7.5 Merge Strategies

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

## 8. Rebasing — Deep Reference

### 8.1 What Rebase Does

Rebase moves or replays commits from one branch onto another. Instead of a merge commit, it creates new commits with the same changes but different parent commits.

```
Before:          After rebase (feature onto main):
     A---B---C  feature             A'--B'--C'  feature
    /                              /
D---E---F---G  main      D---E---F---G  main
```

A', B', C' are new commits — same changes as A, B, C but with different SHAs because their parent changed. The old A, B, C commits become orphaned.

**The golden rule of rebasing: never rebase commits that have been pushed to a shared remote branch.** Rebasing rewrites history. If others have based work on your old commits, rewriting them creates a nightmare.

### 8.2 Basic Rebase

```bash
git checkout feature
git rebase main                 # Replay feature commits on top of main

# What rebase does step by step:
# 1. Find the common ancestor of feature and main
# 2. Save the diff of each commit since the ancestor
# 3. Reset feature to the same commit as main
# 4. Apply each saved diff as a new commit
```

### 8.3 Interactive Rebase

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

### 8.4 Fixup Commits

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

### 8.5 Rebase onto Another Branch

```bash
# Move a branch to a different base
# Before: feature-b was branched from feature-a (which is unmerged)
# You want to move feature-b to be based on main instead

git rebase --onto main feature-a feature-b
# --onto target  from  branch
# "Replay commits that are on feature-b but not on feature-a, onto main"
```

### 8.6 Handling Rebase Conflicts

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

## 9. Merge vs Rebase — When to Use Which

This is one of the most debated topics in Git. Here's the complete, honest answer.

### 9.1 The Core Tradeoff

**Merge** preserves the true history of what happened. The graph shows branches, parallel development, and where things came together. It's honest — this is what actually occurred. But in large teams with many branches, the graph becomes a tangled web.

**Rebase** creates a clean, linear history. It tells a simplified story: "these changes were developed in sequence." Easier to read with `git log`, easier to use `git bisect`, easier to review. But it rewrites commits — the SHA changes, and you lose the context of when something was actually developed.

Neither is universally correct. The right answer depends on context.

### 9.2 Use Merge When

**Merging a completed feature branch into main/develop:**

```bash
git checkout main
git merge --no-ff feature/user-auth
```

Use `--no-ff` to always create a merge commit even if fast-forward is possible. This preserves the fact that these commits came from a feature branch — you can see the branch in the graph and revert the entire feature by reverting one commit.

**Pulling from a shared remote branch:**

```bash
git pull origin main   # = fetch + merge
```

When multiple people are working on the same branch (e.g. `develop`), merge preserves everyone's contribution as-is.

**When working on a public/shared branch:**

Once commits are pushed and others may have pulled them, never rebase. Merge only. Rebasing would rewrite history that others depend on.

**Merging hotfixes into both main and develop:**

```bash
git checkout main && git merge --no-ff hotfix/critical-fix
git checkout develop && git merge --no-ff hotfix/critical-fix
```

### 9.3 Use Rebase When

**Updating your local feature branch with latest main:**

```bash
git checkout feature/my-feature
git rebase main
```

This is the most common use. You want your feature to be based on the latest main so it merges cleanly. Your commits go on top of main's latest — no merge commit needed, clean linear history.

**Cleaning up your commit history before opening a PR:**

```bash
git rebase -i main
# Squash WIP commits, fix typos in messages, reorder for logical flow
```

Before sharing your work, clean it up. Squash the "fix typo" and "WIP: halfway done" commits. The reviewer should see a clean series of logical commits, not your development stream of consciousness.

**Keeping a long-running feature branch up to date:**

```bash
# Daily or before PR:
git fetch origin
git rebase origin/main
```

Repeatedly merging main into a feature branch creates a noisy history with many merge commits. Rebasing keeps the feature branch clean.

**Splitting a monolithic commit into logical parts:**

```bash
git rebase -i HEAD~1   # Mark the commit as 'edit'
git reset HEAD~1       # Unstage all changes
git add -p             # Selectively stage part 1
git commit -m "part 1"
git add -p             # Stage part 2
git commit -m "part 2"
git rebase --continue
```

### 9.4 Never Rebase When

- The branch has been pushed and others have pulled it — rewriting shared history causes chaos
- You're on `main`, `develop`, or any shared branch — these are sacred; their history is immutable
- You need to preserve the exact authorship and timing of commits (auditing, compliance)
- You don't fully understand what the rebase will do — merge is always safer

### 9.5 The Practical Team Rules

```
Rule 1: Main and develop are immutable — never rebase them.

Rule 2: Feature branches are yours until you open a PR.
        Rebase freely on your own branches.

Rule 3: Once a PR is open and others have reviewed/commented,
        avoid rebasing — it makes review harder.
        If you must, warn the team.

Rule 4: Never push --force to a shared branch.
        Use --force-with-lease if you must force-push your own branch.

Rule 5: When in doubt, merge. It's always recoverable.
        A bad rebase can be recovered with reflog but it's painful.
```

### 9.6 The Decision Flowchart

```
Are you updating your local feature branch with latest from main?
  └─ Yes → rebase (git rebase main)

Are you cleaning up commits before a PR?
  └─ Yes → interactive rebase (git rebase -i main)

Are you merging a completed feature into main/develop?
  └─ Yes → merge with --no-ff (git merge --no-ff feature)

Are these commits already pushed to a remote anyone else has access to?
  └─ Yes → never rebase → merge only

Are you pulling from a shared branch?
  └─ Yes → merge (or configure pull.rebase = false)

Are you working alone on a branch no one else touches?
  └─ Yes → rebase freely
```

---

## 10. Remote Repositories

### 10.1 Fetching and Pulling

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

### 10.2 Pushing

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

### 10.3 Working with Forks

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

## 11. History Inspection

### 11.1 git log

```bash
git log                        # Full log
git log --oneline              # One line per commit
git log --graph                # ASCII branch graph
git log --oneline --graph --decorate --all   # The most useful view
git log -5                     # Last 5 commits
git log --since="2 weeks ago"
git log --until="2024-01-01"
git log --author="Kingsley"
git log --grep="auth"          # Commits with "auth" in message
git log -S "function_name"     # Commits that added/removed this string (pickaxe)
git log -G "regex"             # Commits where diff matches regex
git log --follow file.txt      # Follow file through renames
git log -- file.txt            # Commits touching file.txt
git log main..feature          # Commits in feature not in main
git log feature..main          # Commits in main not in feature
git log main...feature         # Commits in either but not both (symmetric diff)
git log --stat                 # Show files changed per commit
git log --patch                # Show full diff for each commit
git log --format="%H %an %s"   # Custom format
git log --no-merges            # Exclude merge commits
git log --merges               # Show only merge commits
```

**Custom format specifiers:**

```
%H  — commit hash (full)
%h  — commit hash (abbreviated)
%an — author name
%ae — author email
%ad — author date
%ar — author date, relative
%cn — committer name
%s  — subject (first line)
%b  — body
%D  — ref names
```

### 11.2 git show and diff

```bash
git show                       # Show latest commit
git show HEAD                  # Same
git show a1b2c3d               # Show specific commit
git show HEAD~2                # Show commit 2 before HEAD
git show HEAD:file.txt         # Show file contents at HEAD
git show main:src/app.js       # File contents on main branch

# Commit references
HEAD                           # Current commit
HEAD~1 or HEAD~               # One commit back
HEAD~3                         # Three commits back
HEAD^                          # First parent (same as HEAD~1 for regular commits)
HEAD^2                         # Second parent (only for merge commits)
a1b2c3d^                       # Parent of this commit
@{yesterday}                   # Commit at yesterday's time
@{2.weeks.ago}                 # Two weeks ago
main@{1}                       # Previous position of main

git diff                       # Working directory vs index
git diff --staged              # Index vs HEAD (what will be committed)
git diff HEAD                  # Working directory vs HEAD
git diff main feature          # Difference between two branches
git diff a1b2c3d b2c3d4e       # Difference between two commits
git diff HEAD~3                # Working dir vs 3 commits ago
git diff -- file.txt           # Diff only for specific file
git diff --stat                # Summary of changes
git diff --word-diff           # Word-level diff (good for prose)
git diff --ignore-whitespace   # Ignore whitespace changes
```

### 11.3 git blame

```bash
git blame file.txt             # Show who last changed each line
git blame -L 10,20 file.txt    # Only lines 10-20
git blame -w file.txt          # Ignore whitespace changes
git blame -C file.txt          # Detect lines moved from other files
git blame a1b2c3d -- file.txt  # Blame at a specific commit

# Reading blame output:
# SHA    (author    date    line_number) content
# a1b2c3 (Kingsley  2026-01 10)         const app = express();
```

### 11.4 git shortlog

```bash
git shortlog                   # Commits grouped by author
git shortlog -sn               # Summary: count, sorted numerically
git shortlog -sn --no-merges   # Exclude merge commits
git shortlog -sn main..feature # Commits in feature not in main
```

---

## 12. Undoing Things — The Complete Guide

This is where most confusion happens. There are multiple ways to undo in Git, and choosing the wrong one can make things worse.

### 12.1 The Undo Decision Tree

```
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

### 12.2 git reset — The Three Modes

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

### 12.3 git revert — Safe Undo for Shared History

`git revert` creates a new commit that undoes the changes of a previous commit. The old commit remains in history — nothing is rewritten. This is the **only safe way to undo commits that have been pushed to a shared branch**.

```bash
git revert HEAD                # Revert last commit
git revert a1b2c3d             # Revert a specific commit
git revert HEAD~3..HEAD        # Revert last 3 commits (one revert commit each)
git revert -n HEAD~3..HEAD     # Stage reverts without committing (then commit once)
git revert --no-edit HEAD      # Don't open editor for message
git revert -m 1 merge-commit   # Revert a merge commit (1 = keep first parent's changes)
```

### 12.4 Restoring Files

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

### 12.5 Recovering Lost Commits

If you did `git reset --hard` and lost commits, or if you deleted a branch — the commits aren't gone immediately. Git keeps them in the reflog for 30 days (90 days for unreachable commits with `gc.reflogExpireUnreachable`).

See Section 13 — The Reflog.

---

## 13. The Reflog — Your Safety Net

### 13.1 What the Reflog Is

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

### 13.2 Recovering with Reflog

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

### 13.3 Finding a Lost Commit's SHA

```bash
git fsck --lost-found          # Find all unreachable objects
ls .git/lost-found/commit/     # SHA files for each lost commit
git show sha                   # Inspect each one
git cat-file -p sha            # See commit details
```

---

## 14. Stashing

### 14.1 Basic Stashing

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

### 14.2 Partial Stashing

```bash
git stash -p                   # Interactively stash specific hunks (like git add -p)
git stash push -- file.txt     # Stash only a specific file
git stash push path/to/dir/    # Stash only a directory
```

### 14.3 When to Stash vs When to Commit

```
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

## 15. Tags

### 15.1 Lightweight vs Annotated Tags

**Lightweight tag** — just a named pointer to a commit. Like a branch that doesn't move. No metadata.

**Annotated tag** — a full Git object with tagger name, email, date, message, and optionally a GPG signature. Use for releases.

```bash
# Lightweight
git tag v1.0.0                         # Tag current commit
git tag v1.0.0 a1b2c3d                 # Tag a specific commit

# Annotated (use for releases)
git tag -a v1.0.0 -m "Release 1.0.0"  # Annotated tag
git tag -a v1.0.0 a1b2c3d -m "Release 1.0.0"  # Specific commit

# Signed (requires GPG setup — see Section 20)
git tag -s v1.0.0 -m "Release 1.0.0"

# Listing tags
git tag                                # List all tags
git tag -l "v1.*"                      # List matching pattern
git tag -n                             # List with tag messages

# Inspecting
git show v1.0.0                        # Show tag and tagged commit

# Pushing tags
git push origin v1.0.0                 # Push specific tag
git push origin --tags                 # Push all tags
git push origin --follow-tags          # Push only annotated tags

# Deleting tags
git tag -d v1.0.0                      # Delete local tag
git push origin --delete v1.0.0        # Delete remote tag

# Checking out a tag (detached HEAD)
git checkout v1.0.0
git checkout -b hotfix/1.0.1 v1.0.0   # Create branch from tag
```

### 15.2 Semantic Versioning with Tags

```bash
# MAJOR.MINOR.PATCH
# v1.0.0 — initial release
# v1.0.1 — patch (bug fix, backwards compatible)
# v1.1.0 — minor (new feature, backwards compatible)
# v2.0.0 — major (breaking change)

# Pre-release versions
git tag -a v2.0.0-alpha.1 -m "Alpha 1"
git tag -a v2.0.0-rc.1 -m "Release Candidate 1"
```

---

## 16. Git Bisect — Finding Bugs with Binary Search

`git bisect` performs a binary search through commit history to find the commit that introduced a bug. Instead of manually checking commits, you tell Git "good" or "bad" and it narrows down to the culprit in O(log n) steps.

```bash
git bisect start                       # Start bisect session
git bisect bad                         # Current commit has the bug
git bisect good v1.0.0                 # v1.0.0 was working
# Git checks out the midpoint commit

# Test the code, then:
git bisect good                        # This commit is fine
git bisect bad                         # This commit has the bug
# Repeat until Git identifies the first bad commit

git bisect reset                       # End session, return to original HEAD

# Full example:
git bisect start
git bisect bad HEAD                    # Current HEAD is broken
git bisect good HEAD~50                # 50 commits ago it was working
# Git will need ~6 steps (log2(50)) to find the bad commit
```

### 16.1 Automated Bisect

```bash
# If you have a test script that exits 0 (pass) or non-zero (fail):
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run ./test.sh               # Automatically bisects using the script

# The script receives each commit as the working directory
# and should exit 0 if good, 1 if bad, 125 if the commit can't be tested
```

---

## 17. Submodules

### 17.1 What Submodules Are

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

### 17.2 Working with Submodules

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

## 18. Git Worktrees

### 18.1 What Worktrees Are

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

### 18.2 Worktrees vs Cloning Again

| | Worktree | Clone |
|---|---|---|
| Shared git history | Yes | No (separate .git) |
| Disk usage | Minimal | Full copy |
| Can be on same branch | No | Yes |
| Setup time | Instant | Slow (download) |
| Best for | Quick context switches | Independent experiments |

---

## 19. Git Hooks

### 19.1 What Hooks Are

Hooks are scripts that Git runs automatically at specific points in the workflow. They live in `.git/hooks/` as executable files. They're not committed to the repository (`.git/` is excluded) — each developer must set up their own hooks.

To share hooks with a team, store them in a directory like `./hooks/` in the repo and configure Git to use it:

```bash
git config core.hooksPath ./hooks     # Point Git to the shared hooks directory
```

### 19.2 Client-Side Hooks

**pre-commit** — runs before a commit is created. Non-zero exit aborts the commit.

```bash
#!/bin/bash
# .git/hooks/pre-commit (or ./hooks/pre-commit)
set -e

echo "Running pre-commit checks..."

# Run linter
npm run lint || { echo "Linting failed"; exit 1; }

# Run tests
npm test || { echo "Tests failed"; exit 1; }

# Check for console.log statements
if git diff --cached | grep "console.log"; then
  echo "Error: console.log found in staged changes"
  exit 1
fi

echo "Pre-commit checks passed"
```

**prepare-commit-msg** — runs before the commit message editor opens. Can prepend branch name, ticket number, etc.

```bash
#!/bin/bash
# Prepend branch name to commit message
BRANCH_NAME=$(git branch --show-current)
TICKET=$(echo "$BRANCH_NAME" | grep -oE '[A-Z]+-[0-9]+' || true)

if [ -n "$TICKET" ]; then
  MSG_FILE=$1
  CURRENT_MSG=$(cat "$MSG_FILE")
  echo "[$TICKET] $CURRENT_MSG" > "$MSG_FILE"
fi
```

**commit-msg** — receives the commit message file. Validate message format.

```bash
#!/bin/bash
# Enforce conventional commits format
COMMIT_MSG=$(cat "$1")
PATTERN="^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .{1,72}"

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
  echo "Error: Commit message doesn't follow conventional commits format"
  echo "Expected: type(scope): description"
  echo "Types: feat|fix|docs|style|refactor|test|chore|perf|ci|build"
  exit 1
fi
```

**post-commit** — runs after commit completes. Notification, logging, etc.

```bash
#!/bin/bash
# Notify on commit
echo "Committed: $(git log -1 --format='%h %s')"
```

**pre-push** — runs before `git push`. Good for blocking pushes to protected branches.

```bash
#!/bin/bash
# Block direct push to main
REMOTE=$1
URL=$2
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "main" ]; then
  echo "Error: Direct push to main is not allowed"
  echo "Please create a feature branch and open a PR"
  exit 1
fi

# Run full test suite before pushing
npm test || { echo "Tests must pass before pushing"; exit 1; }
```

**pre-rebase** — runs before rebase starts.

```bash
#!/bin/bash
# Prevent rebasing main or develop
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ]; then
  echo "Error: Do not rebase main or develop"
  exit 1
fi
```

### 19.3 Server-Side Hooks

These run on the remote repository (GitHub/GitLab/self-hosted):

**pre-receive** — runs before any refs are updated. Can reject pushes.
**update** — runs once per branch being updated.
**post-receive** — runs after push completes. Good for notifications, deployments.

```bash
#!/bin/bash
# post-receive — trigger deployment
while read oldrev newrev refname; do
  branch="${refname#refs/heads/}"
  if [ "$branch" = "main" ]; then
    echo "Deploying to production..."
    cd /var/www/app && git pull && npm run build && pm2 restart app
  fi
done
```

### 19.4 Husky — Managed Hooks for Node.js Projects

```bash
# Install
npm install --save-dev husky
npx husky init

# Add hooks
echo "npm run lint" > .husky/pre-commit
echo "npm test" > .husky/pre-push

# Make executable
chmod +x .husky/*
```

---

## 20. Signing Commits and Tags

### 20.1 Why Sign

Signing commits with a GPG key proves that a commit was actually made by the person it claims. Without signing, anyone can set any `user.name` and `user.email` and commit as you. GitHub shows "Verified" badges on signed commits.

### 20.2 GPG Setup

```bash
# Generate a GPG key
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, no expiration (or 2 years)

# List keys
gpg --list-secret-keys --keyid-format LONG

# Output:
# /home/username/.gnupg/secring.gpg
# ----------------------------------
# sec   rsa4096/A1B2C3D4E5F6G7H8 2026-01-01 [SC]
#       FULL-KEY-FINGERPRINT-HERE
# uid   Kingsley Ihemelandu <k@example.com>

# Copy your key ID (the part after rsa4096/)
# In this example: A1B2C3D4E5F6G7H8

# Export public key for GitHub
gpg --armor --export A1B2C3D4E5F6G7H8
# Copy this output and add to GitHub → Settings → SSH and GPG keys

# Configure Git to use the key
git config --global user.signingkey A1B2C3D4E5F6G7H8
git config --global commit.gpgsign true   # Sign all commits
git config --global tag.gpgsign true      # Sign all tags

# Tell GPG which terminal to use
export GPG_TTY=$(tty)
# Add to ~/.bashrc to make permanent
```

### 20.3 Signing

```bash
# Sign a commit
git commit -S -m "message"     # -S for signing
# With commit.gpgsign = true, -S is automatic

# Sign a tag
git tag -s v1.0.0 -m "Release 1.0.0"

# Verify signatures
git verify-commit HEAD
git verify-tag v1.0.0
git log --show-signature        # Show signature status in log
```

### 20.4 SSH Signing (Git 2.34+)

```bash
# Use SSH key instead of GPG (simpler)
git config --global gpg.format ssh
git config --global user.signingkey "$(cat ~/.ssh/id_ed25519.pub)"
git config --global commit.gpgsign true

# Verify (requires allowed_signers file)
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
echo "email@example.com $(cat ~/.ssh/id_ed25519.pub)" >> ~/.ssh/allowed_signers
```

---

## 21. Advanced Diff and Patch

### 21.1 Advanced Diff Options

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

### 21.2 Creating and Applying Patches

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

### 21.3 Cherry-Pick

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

## 22. Git Workflows — Team Collaboration Patterns

### 22.1 GitHub Flow (Simple, Recommended for Most Teams)

The simplest branching strategy. Works well for teams that deploy continuously.

```
main ─────────────────────────────────────────→ (always deployable)
        │                │
        └─ feature/a     └─ feature/b
           │                 │
           └─ PR → merge      └─ PR → merge
```

**Rules:**
1. `main` is always deployable
2. Create a branch for every feature/fix
3. Open a PR when ready for review
4. Merge to main after approval
5. Deploy immediately after merge

```bash
# The workflow
git checkout main && git pull
git checkout -b feature/user-auth
# Work, commit, push
git push -u origin feature/user-auth
# Open PR on GitHub
# After approval and CI passing:
# Squash and merge via GitHub UI
# Delete the branch
git checkout main && git pull
git branch -d feature/user-auth
```

### 22.2 Git Flow (Structured, for Versioned Releases)

Git Flow is designed for projects with scheduled releases, not continuous deployment.

```
main ────────────────────────────────────────────────→ (production, tagged)
  │                                              │
  └─ develop ──────────────────────────────→    │
         │                    │                 │
         └─ feature/a         └─ feature/b      │
                  │                 │           │
                  └─ merge develop  └─ merge    │
                            │                   │
                            └─ release/1.0 ─────┘
                                    │         │
                                    │    hotfix/1.0.1
                                    │         │
                              merge main    merge main
                              merge develop merge develop
```

**Branches:**
- `main` — production. Tagged at every release.
- `develop` — integration branch. All features merge here first.
- `feature/*` — branches from develop, merge back to develop
- `release/*` — branches from develop when ready to release; bug fixes only; merges to main and develop
- `hotfix/*` — branches from main for urgent fixes; merges to main and develop

```bash
# Git Flow CLI (install separately)
git flow init
git flow feature start user-auth
git flow feature finish user-auth
git flow release start 1.0.0
git flow release finish 1.0.0
git flow hotfix start 1.0.1
git flow hotfix finish 1.0.1
```

**When to use Git Flow:** Large teams, scheduled releases, multiple versions in production simultaneously. It's heavyweight — most modern teams prefer GitHub Flow.

### 22.3 Trunk-Based Development

The most common at high-performing engineering organisations (Google, Facebook, Stripe). Developers commit directly to `main` (or via very short-lived feature branches), relying on feature flags to hide incomplete work in production.

```
main ────────────────────────────────────────────→
  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
  c1 c2 c3  branch  c6 c7  branch  c10 c11
              │              │
              c4 c5───merge  c8 c9───merge
             (short-lived branches < 1 day)
```

**Rules:**
1. Branches (if any) are short-lived — merged within a day
2. Every commit to main must be releasable
3. Feature flags control what users see
4. CI must be fast and reliable — must pass before merge

### 22.4 Pull Request Best Practices

```
A good PR:
- Has a clear title following conventional commits format
- Has a description explaining WHY (not just what the diff shows)
- References the issue/ticket it closes
- Is small — ideally < 400 lines of diff
- Has tests covering the changes
- Has no unresolved console.logs, TODOs from this PR, or debug code
- Is self-reviewed by the author before requesting review

PR description template:
## What
Brief description of what changed.

## Why
The motivation and context. What problem does this solve?

## How
Any non-obvious implementation details worth explaining.

## Testing
How was this tested? What edge cases were considered?

## Screenshots (if UI changes)

Closes #42
```

---

## 23. Commit Message Best Practices

### 23.1 The Conventional Commits Standard

Conventional Commits is a specification for commit messages that makes them machine-readable (for changelog generation, semantic versioning, CI triggers) and human-readable.

```
<type>(<scope>): <short description>
<blank line>
<body>
<blank line>
<footer>
```

**Types:**

| Type | When to use |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, missing semicolons — no logic change |
| `refactor` | Code restructuring — no feature or fix |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `chore` | Build process, tooling, dependencies |
| `ci` | CI configuration changes |
| `build` | Build system changes |
| `revert` | Reverting a previous commit |

```
feat(auth): add JWT refresh token rotation

Implements automatic refresh token rotation on each use.
The old refresh token is invalidated and a new one issued,
reducing the window for token theft.

- Adds RefreshToken entity with expiry
- Adds POST /auth/refresh endpoint
- Adds rotation logic in AuthService
- Adds cleanup job for expired tokens

BREAKING CHANGE: /auth/login now returns refreshToken in addition to accessToken
Closes #142
```

**Breaking changes** are indicated by `BREAKING CHANGE:` in the footer, or by appending `!` after the type:

```
feat!: change API response format for /users

BREAKING CHANGE: Users endpoint now returns { data: [...] } instead of [...]
```

### 23.2 The Seven Rules of a Great Commit Message

1. **Separate subject from body with a blank line**
2. **Limit the subject line to 72 characters**
3. **Do not end the subject line with a period**
4. **Use the imperative mood** — "Add feature" not "Added feature" or "Adds feature"
5. **Wrap the body at 72 characters**
6. **Use the body to explain what and why, not how** — the diff shows how
7. **Reference issues and PRs in the footer**

### 23.3 Examples — Good vs Bad

```bash
# BAD
git commit -m "fix"
git commit -m "changes"
git commit -m "WIP"
git commit -m "updated stuff"
git commit -m "Fixed the bug where users couldn't log in on certain browsers"
# (too long, no type, past tense)

# GOOD
git commit -m "fix(auth): resolve login failure on Safari 16"
git commit -m "feat(payments): add Paystack webhook handler"
git commit -m "refactor(db): extract query builders into repository pattern"
git commit -m "docs(api): add OpenAPI annotations to user endpoints"
git commit -m "perf(search): add GIN index on users.email column"
git commit -m "test(auth): add integration tests for token refresh flow"
```

---

## 24. Branch Naming Conventions

### 24.1 Standard Patterns

```
<type>/<ticket-id>-<short-description>

feat/PROJ-142-user-authentication
fix/PROJ-89-login-safari-bug
hotfix/critical-payment-failure
release/v1.2.0
chore/update-dependencies
docs/api-documentation
refactor/extract-auth-service
test/add-payment-integration-tests
```

**Rules:**
- All lowercase
- Hyphens, not underscores or spaces
- Short but descriptive (3-5 words)
- Include ticket/issue number when applicable
- Type prefix matches commit type convention

### 24.2 Protected Branch Patterns

Configure in GitHub/GitLab:

```
main        — production, requires PR + review + CI
develop     — integration, requires PR
release/*   — release branches, restricted push
hotfix/*    — hotfix branches, restricted
```

---

## 25. Best Practices — The Full Picture

### 25.1 Commit Hygiene

**Commit early, commit often** — during development. Then clean up with interactive rebase before sharing. Small commits are easier to review, easier to bisect, and easier to revert.

**Each commit should be atomic** — it should represent one logical change. If you have to use "and" to describe what the commit does, consider splitting it.

**Every commit should leave the code in a working state** — tests pass, app starts, no syntax errors. This makes `git bisect` reliable.

**Never commit directly to main or develop** — always through a branch and PR.

**Never commit secrets** — not even temporarily. If you do, the secret is compromised regardless of whether you delete it later. Rotate the secret immediately, then use `git filter-branch` or BFG Repo Cleaner to scrub the history.

### 25.2 Branch Hygiene

```bash
# Delete branches after merging
git branch -d feature/done         # Local
git push origin --delete feature/done  # Remote

# Prune stale remote tracking branches
git fetch --prune
git remote prune origin

# Keep feature branches short-lived — hours to days, not weeks
# Long-lived branches → big PRs → hard reviews → painful merges
```

### 25.3 The .gitignore You Always Need

```bash
# Node.js
node_modules/
dist/
build/
.env
.env.*
!.env.example
*.log
npm-debug.log*
.npm
coverage/
.nyc_output/

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.env
dist/
*.egg-info/
.pytest_cache/

# General
.DS_Store
Thumbs.db
*.swp
*.swo
.idea/
.vscode/
*.log
```

### 25.4 Force Push Safety

```bash
# NEVER:
git push --force origin main       # Can destroy teammates' work

# ALWAYS use instead:
git push --force-with-lease        # Fails if remote has commits you haven't fetched
git push --force-with-lease --force-if-includes  # Even safer (git 2.30+)

# When is force push acceptable:
# - Your own feature branch (no one else has based work on it)
# - After interactive rebase to clean history before PR
# - To fix a botched merge before others pull
```

### 25.5 Repository Health

```bash
# Verify repo integrity
git fsck                           # Check object database

# Optimise the repo
git gc                             # Garbage collect — pack loose objects, prune reflog
git gc --aggressive                # More thorough (slower)
git prune                          # Remove unreachable objects
git repack -ad                     # Repack all objects into one packfile

# Count objects
git count-objects -v

# See repo size
du -sh .git
```

### 25.6 Security Practices

```bash
# Remove accidentally committed secrets
# Step 1: Rotate the secret immediately (assume it's compromised)

# Step 2: Remove from history using BFG (faster) or git filter-branch
# BFG Repo Cleaner (recommended):
java -jar bfg.jar --delete-files id_rsa.pub repo.git
java -jar bfg.jar --replace-text passwords.txt repo.git

# Or using git filter-branch (slower, built-in):
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret.env" \
  --prune-empty --tag-name-filter cat -- --all

# Step 3: Force push all branches and tags
git push origin --force --all
git push origin --force --tags

# Step 4: Tell all contributors to re-clone

# Prevent future secret commits
# Use tools like gitleaks, detect-secrets, or truffleHog as pre-commit hooks
```

### 25.7 The git config Settings That Actually Matter

```bash
# Safer defaults
git config --global pull.ff only              # Refuse to merge on pull (must be explicit)
git config --global push.default current      # Push to same-named remote branch
git config --global rebase.autoStash true     # Auto-stash before rebase
git config --global rebase.autoSquash true    # Auto-apply fixup! commits
git config --global merge.conflictstyle diff3 # Show merge base in conflicts
git config --global diff.algorithm histogram  # Better diff

# Convenience
git config --global fetch.prune true          # Always prune on fetch
git config --global help.autocorrect 20       # Auto-correct mistyped commands (2s delay)
git config --global core.excludesfile ~/.gitignore_global
```

---

## 26. Troubleshooting and Recovery

### "I committed to the wrong branch"

```bash
# Move the commit to the correct branch
git log --oneline -3              # Note the SHA of the commit you want to move
git checkout correct-branch
git cherry-pick SHA               # Apply it to the right branch
git checkout wrong-branch
git reset --hard HEAD~1           # Remove it from the wrong branch
```

### "I accidentally deleted a branch"

```bash
git reflog                        # Find the last commit SHA on the deleted branch
git checkout -b recovered-branch SHA
```

### "I did git reset --hard and lost work"

```bash
git reflog                        # Find the SHA before the reset
git reset --hard SHA              # Go back
# Or create a branch at that point:
git branch recovered SHA
```

### "My rebase went horribly wrong"

```bash
git rebase --abort                # If still in progress
# If already completed:
git reflog                        # Find the pre-rebase position
git reset --hard HEAD@{N}         # N = the position before rebase started
# Or:
git reset --hard ORIG_HEAD        # Git saves pre-operation position here
```

### "I accidentally committed my .env file"

This is one of the most common Git mistakes. The response depends on whether you've pushed yet.

---

**Scenario A — Not pushed yet (local only)**

Easy. The secret hasn't left your machine.

```bash
# Remove .env from the last commit but keep the file on disk
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit --amend --no-edit       # Amend the commit — .env is gone from it
```

If the .env was committed several commits ago (not just the last one):

```bash
git rebase -i HEAD~N               # N = how many commits back the .env appeared
# Mark the offending commit as 'edit'
# When rebase stops there:
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit --amend --no-edit
git rebase --continue
```

---

**Scenario B — Pushed to a private repo, no one else has pulled**

Act fast. The secret is on GitHub's servers but no one has it yet.

```bash
# Step 1 — Rotate/revoke the secret immediately
# Don't wait. Do this first. Assume the worst.

# Step 2 — Remove .env from the entire git history using BFG (recommended)
# Install BFG: https://rtyley.github.io/bfg-repo-cleaner/

# Clone a fresh mirror of your repo
git clone --mirror https://github.com/you/your-repo.git

# Run BFG to delete the file from all history
java -jar bfg.jar --delete-files .env your-repo.git

# Clean up the repo
cd your-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push all branches and tags
git push --force

# Step 3 — Add .env to .gitignore in your working repo
cd your-working-repo
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"
git push

# Step 4 — Re-clone locally (your local clone's history is now stale)
cd ..
rm -rf your-working-repo
git clone https://github.com/you/your-repo.git
```

---

**Scenario C — Pushed to a public repo, or others have pulled**

The secret is compromised. Full stop. No amount of Git history rewriting changes this — GitHub indexes public repos, bots scrape them within seconds, and anyone who pulled has the secret in their local history.

```bash
# Step 1 — Rotate/revoke ALL secrets in the .env file IMMEDIATELY
# API keys, database passwords, JWT secrets — everything. Right now.

# Step 2 — Make the repo private immediately (buys time)
# GitHub → Repo Settings → Danger Zone → Change visibility

# Step 3 — Remove from history (same as Scenario B)
git clone --mirror https://github.com/you/your-repo.git
java -jar bfg.jar --delete-files .env your-repo.git
cd your-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# Step 4 — Contact GitHub support
# https://support.github.com/
# Request they clear cached views of the file
# GitHub's API may still serve the blob even after history rewrite

# Step 5 — Notify anyone who cloned the repo
# They need to re-clone — their local history still has the secret

# Step 6 — Add .env to .gitignore in the cleaned repo
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"
git push

# Step 7 — Audit what used those credentials
# Check logs for any unauthorised access using the compromised keys
```

---

**Using git filter-branch instead of BFG (no Java required, slower)**

```bash
# Remove .env from entire history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
git push origin --force --tags
```

---

**How to prevent this happening again**

```bash
# 1. Add .env to .gitignore before creating the file
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"

# 2. Always have a .env.example committed with placeholder values
cp .env .env.example
# Edit .env.example — replace real values with placeholders
git add .env.example
git commit -m "chore: add .env.example"

# 3. Add a pre-commit hook to catch .env before it's committed
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached --name-only | grep -qE "^\.env$|^\.env\."; then
  echo "ERROR: Attempting to commit a .env file."
  echo "Remove it with: git rm --cached .env"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit

# 4. Use gitleaks for broader secret detection
# Install: https://github.com/gitleaks/gitleaks
gitleaks protect --staged   # Scan staged changes before commit
```

### "Merge conflict I don't understand"

```bash
git log --merge                   # Show commits causing the conflict
git diff --merge                  # Show conflicting changes
git checkout --conflict=diff3 file.txt  # Re-show conflict markers with base
git mergetool                     # Open visual merge tool
git merge --abort                 # Start over if needed
```

### "Detached HEAD panic"

```bash
git log --oneline -5              # See where you are
git switch main                   # Go back to main (commits made in detached HEAD are orphaned)
# If you made commits in detached HEAD that you want to keep:
git branch my-work                # Create branch at current position (do this FIRST)
git switch main
```

### "Slow git status"

```bash
# Common on large repos or slow filesystems
git config core.fsmonitor true              # Enable filesystem monitor (git 2.37+)
git config core.untrackedCache true         # Cache untracked file info
git update-index --really-refresh           # Refresh the index
git gc                                      # Optimise object storage
```

### "Accidentally staged the wrong thing"

```bash
git restore --staged file.txt               # Unstage specific file
git restore --staged .                      # Unstage everything
git reset HEAD file.txt                     # Older syntax for unstaging
```

### "Need to split a commit into two"

```bash
git rebase -i HEAD~1              # Mark the commit as 'edit'
git reset HEAD~1                  # Unstage everything from that commit
git add -p                        # Stage part 1 interactively
git commit -m "part 1"
git add -p                        # Stage part 2
git commit -m "part 2"
git rebase --continue
```

### "I want to see what changed between my branch and main"

```bash
git log --oneline main..HEAD      # Commits on my branch not on main
git diff main...HEAD              # Changes introduced by my branch (three dots)
git diff main                     # All differences between my branch and main
```

### "git push rejected (non-fast-forward)"

```bash
# Someone else pushed while you were working
git fetch origin
git log --oneline HEAD..origin/main  # See what they pushed
git rebase origin/main              # Rebase your work on top of theirs
git push                            # Now it should work
# Or merge:
git merge origin/main && git push
```

---

*Last updated: 2026 — Built from real Git usage across solo and team projects.*
