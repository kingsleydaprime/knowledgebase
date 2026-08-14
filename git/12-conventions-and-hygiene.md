# Conventions and Hygiene

**[Beginner → Intermediate]** — Conventional Commits, what makes a commit message worth reading, and the commit/branch/repo hygiene that keeps a history usable a year later.

## The Conventional Commits Standard

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

## The Seven Rules of a Great Commit Message

1. **Separate subject from body with a blank line**
2. **Limit the subject line to 72 characters**
3. **Do not end the subject line with a period**
4. **Use the imperative mood** — "Add feature" not "Added feature" or "Adds feature"
5. **Wrap the body at 72 characters**
6. **Use the body to explain what and why, not how** — the diff shows how
7. **Reference issues and PRs in the footer**

## Examples — Good vs Bad

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

---

## Commit Hygiene

**Commit early, commit often** — during development. Then clean up with interactive rebase before sharing. Small commits are easier to review, easier to bisect, and easier to revert.

**Each commit should be atomic** — it should represent one logical change. If you have to use "and" to describe what the commit does, consider splitting it.

**Every commit should leave the code in a working state** — tests pass, app starts, no syntax errors. This makes `git bisect` reliable.

**Never commit directly to main or develop** — always through a branch and PR.

**Never commit secrets** — not even temporarily. If you do, the secret is compromised regardless of whether you delete it later. Rotate the secret immediately, then use `git filter-branch` or BFG Repo Cleaner to scrub the history.

## Branch Hygiene

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

## The .gitignore You Always Need

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

## Force Push Safety

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

## Repository Health

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

## Security Practices

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

## The git config Settings That Actually Matter

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

## Related
- [[git/11-tags-and-versioning|Tags and Versioning]] — what conventional commits let you automate
- [[git/16-hooks-and-signing|Hooks and Signing]] — enforcing these conventions mechanically
- [[git/09-investigating-history|Investigating History]] — the payoff for hygiene, a year later
- [[git/README|Git course map]]
