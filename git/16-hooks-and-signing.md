# Hooks and Signing

**[Advanced]** — Automating checks at commit and push time (client-side, server-side, and via Husky), and proving commits are yours with GPG or SSH signatures.

## What Hooks Are

Hooks are scripts that Git runs automatically at specific points in the workflow. They live in `.git/hooks/` as executable files. They're not committed to the repository (`.git/` is excluded) — each developer must set up their own hooks.

To share hooks with a team, store them in a directory like `./hooks/` in the repo and configure Git to use it:

```bash
git config core.hooksPath ./hooks     # Point Git to the shared hooks directory
```

## Client-Side Hooks

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

## Server-Side Hooks

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

## Husky — Managed Hooks for Node.js Projects

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

## Signing Commits and Tags

### Why Sign

Signing commits with a GPG key proves that a commit was actually made by the person it claims. Without signing, anyone can set any `user.name` and `user.email` and commit as you. GitHub shows "Verified" badges on signed commits.

### GPG Setup

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

### Signing

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

### SSH Signing (Git 2.34+)

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

## Related
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — the rules a pre-commit hook enforces
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|Digital Signatures and PKI]] — what a GPG signature actually proves
- [[devops/01-linux/12-bash-scripting|Bash Scripting]] — hooks are just executable scripts
- [[git/14-github-and-ci|Git in CI]] — server-side enforcement when hooks are not enough
- [[git/README|Git course map]]
