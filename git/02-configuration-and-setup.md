---
id: 1bc19400-b9b5-4fe9-9049-75eb61def0bb
---

# Configuration and Setup

## Config Levels
<!-- bite: f8b0c820-caf8-4f6d-ba5d-31f2c9ab2935 -->

Git has three config levels, each overriding the previous:

```bash
git config --system   # /etc/gitconfig — applies to all users on the machine
git config --global   # ~/.gitconfig — applies to all your repos
git config --local    # .git/config — applies to this repo only
```

## Essential Configuration
<!-- bite: c38bde8e-865a-46b3-a74d-d45c484dc056 -->

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

# Aliases (see "Useful Aliases" below)
```

## Useful Aliases
<!-- bite: 6dbf11bd-346c-4ea3-9889-8f4a322d7902 -->

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

## The ~/.gitconfig File
<!-- bite: c6bb5e66-48da-41c1-8ab5-ebd1edf83a4f -->

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

## Global .gitignore
<!-- bite: ade20a6c-cf1b-4d6a-b356-c2e25bdfbdb5 -->

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

## Repository Setup and Cloning
<!-- bite: b7c21859-03e7-46bf-8670-2fb0b9822779 -->

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

## Related
<!-- bite: 576888d4-3a3c-4ae1-89b3-cc809df75257 -->
- [[git/03-the-three-trees|The Three Trees]] — the next step once a repo exists
- [[git/17-hooks-and-signing|Hooks and Signing]] — what `commit.gpgsign` and `tag.gpgsign` above actually turn on
- [[devops/01-linux/10-environment-variables|Environment Variables]] — how the shell finds your editor and credentials
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 1150fa7e-5487-4a3d-a6a9-dfd9fd006d20 -->

**Level:** Beginner. **Covers:** The three config levels, the `~/.gitconfig` worth copying, a global `.gitignore`, and the full set of `init` / `clone` / `remote` options.
