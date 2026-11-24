---
id: 20d3afaf-1772-439c-9d48-c2c88ef320c8
---

# Conventions and Hygiene

Git conventions are agreed ways of writing commit messages, naming branches and keeping a project's history tidy. They make the history easy to read, for people and for tools. A clear commit message is like a clear label on a box in a store room: anyone can find what they need later.

## The Conventional Commits Standard
<!-- bite: 1ba3e167-e11a-42ee-9ae4-0b73f20ca4ca -->

Conventional Commits is a specification for commit messages that makes them machine-readable (for changelog generation, semantic versioning, CI triggers) and human-readable.

```text
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

```text
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

```text
feat!: change API response format for /users

BREAKING CHANGE: Users endpoint now returns { data: [...] } instead of [...]
```

## The Seven Rules of a Great Commit Message
<!-- bite: 600bb35b-7905-4d0c-ae69-eccd933e7d9d -->

1. **Separate subject from body with a blank line**
2. **Limit the subject line to 72 characters**
3. **Do not end the subject line with a period**
4. **Use the imperative mood** — "Add feature" not "Added feature" or "Adds feature"
5. **Wrap the body at 72 characters**
6. **Use the body to explain what and why, not how** — the diff shows how
7. **Reference issues and PRs in the footer**

## Examples — Good vs Bad
<!-- bite: f17958e6-f729-4077-a9f9-f5ffb7e9da17 -->

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
<!-- bite: b8bff462-e602-409a-8d8f-b6cfeb6c1409 -->

**Commit early, commit often** — during development. Then clean up with interactive rebase before sharing. Small commits are easier to review, easier to bisect, and easier to revert.

**Each commit should be atomic** — it should represent one logical change. If you have to use "and" to describe what the commit does, consider splitting it.

**Every commit should leave the code in a working state** — tests pass, app starts, no syntax errors. This makes `git bisect` reliable.

**Never commit directly to main or develop** — always through a branch and PR.

**Never commit secrets** — not even temporarily. If you do, the secret is compromised regardless of whether you delete it later. Rotate the secret immediately, then use `git filter-branch` or BFG Repo Cleaner to scrub the history.

## Branch Hygiene
<!-- bite: 64d1877c-90bc-4707-975d-e780a1d2b16d -->

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
<!-- bite: a9e38641-9391-4f61-9140-7f6d9b30c4e3 -->

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
<!-- bite: 0f8ccfa7-cb16-4b50-bd47-d041a723fe84 -->

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
<!-- bite: df1f683d-bc1d-4d82-8526-4f14881c88bf -->

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
<!-- bite: 18b937a9-80cf-4181-9727-74a7eae3a42b -->

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
<!-- bite: d110f5e3-55b6-442f-bf4c-e7e5ca0898d1 -->

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

## Check your understanding
<!-- bite: c19f4cb0-74f2-4afa-9a9e-33a9ce7aea50 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c54e1640" -->
   Which commit message follows Conventional Commits and the seven rules?

   - [ ] `Fixed the bug where users couldn't log in on Safari.`
   - [x] `fix(auth): resolve login failure on Safari 16`
   - [ ] `updated stuff`
   - [ ] `fix(auth): Resolved login failure on Safari 16.`

   <details><summary>Answer</summary>

   `fix(auth): resolve login failure on Safari 16`. It has a type and scope, uses the imperative mood ("resolve", not "resolved"), is short and has no full stop at the end.

   </details>

2. <!-- q: exact id="3861f017" answer="perf" -->
   You added a database index that makes search three times faster, with no change in behaviour. Which Conventional Commits type fits best?

   <details><summary>Answer</summary>

   `perf`, a performance improvement. For example `perf(search): add index on users.email`.

   </details>

3. <!-- q: exact id="46a3ad03" answer="72" -->
   What is the maximum length the lesson gives for a commit subject line, in characters?

   <details><summary>Answer</summary>

   72. The body is also wrapped at 72 characters.

   </details>

4. <!-- q: mcq id="0a64c117" -->
   You pushed a commit containing a live API key, and five minutes later pushed another commit deleting it. What must you do first?

   - [ ] Nothing; the key is deleted now
   - [ ] Run BFG to clean the history, then you're safe
   - [x] Rotate the key at once, because it is compromised either way
   - [ ] Make the repository private

   <details><summary>Answer</summary>

   Rotate it. The key is still in the history and may already have been copied. Cleaning the history with BFG and force-pushing comes after, and a pre-commit scanner such as gitleaks helps stop it happening again.

   </details>

5. <!-- q: open id="92621303" -->
   Why should every commit leave the code working, with tests passing and the app starting?

   <details><summary>Answer</summary>

   So `git bisect` works. Bisect checks out commits in the middle of the history and asks whether the bug is there. If some commits don't build or fail for unrelated reasons, you can't tell good from bad and the search breaks down. Working commits are also safe to revert or deploy on their own.

   </details>

6. <!-- q: mcq id="382516b4" -->
   Why keep feature branches short-lived, hours to days rather than weeks?

   - [ ] Git slows down with old branches
   - [x] Long branches turn into big pull requests, hard reviews and painful merges
   - [ ] GitHub deletes branches after a week
   - [ ] Short branches don't need commit messages

   <details><summary>Answer</summary>

   The longer a branch lives, the more `main` moves away from it, so the pull request grows, reviewers struggle and conflicts pile up.

   </details>

## Related
<!-- bite: d49720dc-4ced-4091-a376-7de309993881 -->
- [[git/11-tags-and-versioning|Tags and Versioning]] — what conventional commits let you automate
- [[git/17-hooks-and-signing|Hooks and Signing]] — enforcing these conventions mechanically
- [[git/09-investigating-history|Investigating History]] — the payoff for hygiene, a year later
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 76fc933e-f994-4658-a222-8d454fa03ca0 -->

**Level:** Beginner → Intermediate. **Covers:** Conventional Commits, what makes a commit message worth reading, and the commit/branch/repo hygiene that keeps a history usable a year later.
