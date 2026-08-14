# GitHub as a Platform, and Git in CI

**[Intermediate]** — The layer above Git itself: branch protection, CODEOWNERS, rulesets, pull request practice — and how a CI system interacts with your repository once those rules exist.

## Why Branch Protection Matters

Without protection, anyone with write access can push directly to `main`, force-push over history, or delete the branch. Protection rules enforce your team's branching strategy at the GitHub level — they apply even to admins (optionally) and cannot be bypassed by individual developers.

## Recommended Settings for `main`

```
Settings → Branches → Add branch protection rule

Branch name pattern: main

Core protections:
☑ Require a pull request before merging
    Required approvals: 1 (small team) | 2 (larger team)
    ☑ Dismiss stale pull request approvals when new commits are pushed
    ☑ Require review from Code Owners (if CODEOWNERS file exists)
    ☑ Require approval of the most recent reviewable push

☑ Require status checks to pass before merging
    ☑ Require branches to be up to date before merging
    Required status checks: (these are your CI job names)
      - CI / Lint & Format
      - CI / Unit Tests
      - CI / Integration Tests
      - CI / Build Docker Image

☑ Require conversation resolution before merging

Quality controls:
☑ Require linear history
    (enforces squash or rebase merge — no merge commits on main)

☑ Require signed commits
    (GPG or SSH signed — proves identity, not just email header)

Security:
☑ Do not allow bypassing the above settings
    ☑ Include administrators
    (even you cannot force-push to main)

Danger zone:
☐ Allow force pushes     ← leave unchecked
☐ Allow deletions        ← leave unchecked
```

## CODEOWNERS

The `.github/CODEOWNERS` file defines who must review changes to specific files or directories. Reviewers are automatically requested when a PR touches those paths.

```
# .github/CODEOWNERS

# Default: any change requires review from backend-team
*                           @org/backend-team

# Auth and security code requires security team review
/src/auth/                  @org/security-team
/src/middleware/             @org/security-team

# Payment code requires both payments team and a finance lead
/src/payments/              @org/payments-team @finance-lead

# CI/CD changes require devops review
/.github/                   @org/devops-team
/Dockerfile                 @org/devops-team
/docker-compose*.yml        @org/devops-team

# Migrations require DBA or tech lead sign-off
/migrations/                @tech-lead @dba-team

# Documentation managed by docs team
/docs/                      @org/docs-team
/README.md                  @org/docs-team
```

## Setting Merge Strategy

Enforce a specific merge strategy to maintain clean history:

```
Settings → General → Pull Requests

For GitHub Flow (squash history):
  ☐ Allow merge commits    ← disable
  ☐ Allow rebase merging   ← disable
  ☑ Allow squash merging   ← only this
  
  Squash merge commit title: Pull request title
  Squash merge commit message: Pull request body

For feature-branch preservation:
  ☐ Allow merge commits
  ☑ Allow rebase merging   ← clean linear history with individual commits
  ☐ Allow squash merging

Auto-delete head branches:
  ☑ Automatically delete head branches   ← clean up after merge
```

## Rulesets (Newer, More Powerful)

GitHub Rulesets (GA 2023) replace branch protection rules for organisations. They can target multiple branches with a single rule and have bypass lists for specific roles.

```
Settings → Rules → Rulesets → New branch ruleset

Name: Production Branch Protection
Enforcement: Active
Bypass list: Role: Organization admin (emergency bypass)

Target branches:
  Include by pattern: main
  Include by pattern: release/**

Rules:
  ☑ Restrict deletions
  ☑ Require linear history
  ☑ Require signed commits
  ☑ Require a pull request before merging
    Required approvals: 2
    ☑ Dismiss stale reviews on push
  ☑ Require status checks
    Required checks: CI, Security Scan
  ☑ Block force pushes
```

---

---

## Pull Request Best Practices

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

## Git in CI/CD Pipelines

### How CI Systems Interact with Git

CI systems (GitHub Actions, GitLab CI, Jenkins) clone your repository, run jobs, and interact with Git. Understanding how they check out code and what git information is available prevents common pipeline bugs.

### Checkout Depth — Shallow vs Full

By default, `actions/checkout` does a shallow clone (depth=1) — only the latest commit. This is fast but breaks commands that need history:

```yaml
# Shallow clone (default) — fast, but git log only shows one commit
- uses: actions/checkout@v4

# Full clone — needed for changelog generation, git log, version tools
- uses: actions/checkout@v4
  with:
    fetch-depth: 0   # 0 = full history

# Specific depth — for git log last N commits
- uses: actions/checkout@v4
  with:
    fetch-depth: 50

# Why full history matters:
# - semantic-release needs history to determine version bumps
# - git log --oneline to generate changelogs
# - git describe to get the last tag
# - Checking if a file changed since last release
```

### Git Information Available in Pipelines

```yaml
# Common git values available via github context
${{ github.sha }}          # current commit SHA (full)
${{ github.ref }}          # refs/heads/main or refs/tags/v1.0.0
${{ github.ref_name }}     # main or v1.0.0
${{ github.event.before }} # previous commit SHA (on push)

# Deriving values from git in a step
- name: Get git info
  run: |
    # Short SHA (first 7 chars) — common for image tagging
    SHORT_SHA=$(git rev-parse --short HEAD)
    echo "short_sha=$SHORT_SHA" >> $GITHUB_OUTPUT

    # Last tag reachable from HEAD
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    echo "last_tag=$LAST_TAG" >> $GITHUB_OUTPUT

    # Commits since last tag (for build numbers)
    COMMITS_SINCE=$(git rev-list $LAST_TAG..HEAD --count)
    echo "commits_since_tag=$COMMITS_SINCE" >> $GITHUB_OUTPUT

    # Branch name
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "branch=$BRANCH" >> $GITHUB_OUTPUT
```

### Tagging from CI

```yaml
# Create and push a tag from a CI pipeline
- name: Create release tag
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git tag -a "v${{ steps.version.outputs.value }}" \
      -m "Release v${{ steps.version.outputs.value }}"
    git push origin "v${{ steps.version.outputs.value }}"

# Using the official action
- uses: rickstaa/action-create-tag@v1
  with:
    tag: v${{ steps.version.outputs.value }}
    message: Release v${{ steps.version.outputs.value }}
```

### Committing Back to the Repository from CI

```yaml
# Bump version in package.json and commit back
- name: Bump version
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    npm version patch --no-git-tag-version
    git add package.json package-lock.json
    git commit -m "chore(release): bump version [skip ci]"
    git push

# IMPORTANT: [skip ci] prevents an infinite loop where the commit triggers CI again
# GitHub also respects [ci skip], [no ci], [skip actions]
```

### Detecting What Changed

```yaml
# Check if specific files changed — decide whether to run expensive steps
- name: Detect changes
  id: changes
  uses: dorny/paths-filter@v3
  with:
    filters: |
      backend:
        - 'src/**'
        - 'package*.json'
        - 'Dockerfile'
      docs:
        - 'docs/**'
        - '*.md'
      infra:
        - 'terraform/**'
        - '.github/workflows/**'

- name: Run backend tests
  if: steps.changes.outputs.backend == 'true'
  run: npm test

- name: Deploy docs
  if: steps.changes.outputs.docs == 'true'
  run: ./deploy-docs.sh

# Manual change detection with git diff
- name: Check if Dockerfile changed
  id: dockerfile
  run: |
    if git diff --name-only HEAD~1 HEAD | grep -q "Dockerfile"; then
      echo "changed=true" >> $GITHUB_OUTPUT
    else
      echo "changed=false" >> $GITHUB_OUTPUT
    fi

- name: Rebuild image (only if Dockerfile changed)
  if: steps.dockerfile.outputs.changed == 'true'
  run: docker build .
```

### PR Validation — Enforcing Conventions in CI

```yaml
# Validate PR title follows Conventional Commits
- name: Validate PR title
  if: github.event_name == 'pull_request'
  run: |
    TITLE="${{ github.event.pull_request.title }}"
    PATTERN="^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .{1,72}"
    if ! echo "$TITLE" | grep -qE "$PATTERN"; then
      echo "❌ PR title does not follow Conventional Commits format"
      echo "Expected: type(scope): description"
      echo "Examples:"
      echo "  feat(auth): add JWT refresh tokens"
      echo "  fix(payments): handle timeout on Paystack webhook"
      exit 1
    fi
    echo "✅ PR title is valid"

# Check commits on the PR branch
- name: Lint commit messages
  uses: wagoid/commitlint-github-action@v6
  with:
    configFile: commitlint.config.js
```

### Git LFS in CI

Large file storage (LFS) stores large binary files outside the git history:

```bash
# Install LFS locally
git lfs install
git lfs track "*.psd"
git lfs track "*.zip"
git add .gitattributes
git commit -m "chore: configure LFS for design assets"
```

```yaml
# In GitHub Actions — checkout includes LFS files by default
- uses: actions/checkout@v4
  with:
    lfs: true   # explicitly enable LFS (default is false for speed)
```

---

## Related
- [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — GitHub Actions dissected via this vault's own deploy pipeline
- [[git/github-actions-cicd-reference|GitHub Actions reference]] — the full hands-on Actions notes
- [[git/13-branching-strategies|Branching Strategies]] — what the protection rules are protecting
- [[git/11-tags-and-versioning|Tags and Versioning]] — releases cut from CI
- [[git/README|Git course map]]
