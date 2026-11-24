---
id: 7f8bb123-c851-4949-a99a-4f940264160d
---

# GitHub as a Platform, and Git in CI

GitHub is a website that hosts Git projects and adds team features such as pull requests, reviews and rules about who can change what. CI (continuous integration) means having tests and checks run automatically every time someone pushes code. Together they stop broken code from slipping into the main version unnoticed.

## Why Branch Protection Matters
<!-- bite: 09b1e644-cf34-417c-bfab-87b1ebca1706 -->

Without protection, anyone with write access can push directly to `main`, force-push over history, or delete the branch. Protection rules enforce your team's branching strategy at the GitHub level — they apply even to admins (optionally) and cannot be bypassed by individual developers.

## Recommended Settings for `main`
<!-- bite: 26d116ee-9da1-4368-be90-6a22d7ba432d -->

```text
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
<!-- bite: 7c08fe6d-3213-4cc4-a777-08b2f393f132 -->

The `.github/CODEOWNERS` file defines who must review changes to specific files or directories. Reviewers are automatically requested when a PR touches those paths.

```text
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
/index.md                  @org/docs-team
```

## Setting Merge Strategy
<!-- bite: bceb6682-3dcf-4362-94e6-ce57416ea3a4 -->

Enforce a specific merge strategy to maintain clean history:

```text
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
<!-- bite: a2cbae3f-6b22-46b0-bee2-ec4489a79be5 -->

GitHub Rulesets (GA 2023) replace branch protection rules for organisations. They can target multiple branches with a single rule and have bypass lists for specific roles.

```text
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
<!-- bite: d6f5b9d2-4fbf-4f25-b69c-e52e96ea53d3 -->

```text
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
<!-- bite: 0b02af29-9c14-4d40-91f8-ef84509db5ed -->

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

## Check your understanding
<!-- bite: 64118f9e-7fd1-48cc-a578-fbb9d08071f3 -->

Try each one before you open the answer.

1. <!-- q: mcq id="61c8d8a8" -->
   Your release job uses `actions/checkout@v4` with no options, and `git describe --tags` fails to find any tag. Why?

   - [ ] Tags can't be read inside CI
   - [x] The default checkout is a shallow clone of one commit, so the history and tags aren't there
   - [ ] `git describe` only works on Windows runners
   - [ ] The job needs admin rights

   <details><summary>Answer</summary>

   The default is `fetch-depth: 1`. Set `fetch-depth: 0` to get the full history, which version and changelog tools need.

   </details>

2. <!-- q: exact id="4540282f" answer="[skip ci]" accept="[ci skip]|[no ci]|[skip actions]" -->
   A CI job bumps the version and pushes a commit back to the repository. What do you put in that commit's message so it doesn't start CI again and loop forever?

   <details><summary>Answer</summary>

   `[skip ci]`. GitHub also accepts `[ci skip]`, `[no ci]` and `[skip actions]`.

   </details>

3. <!-- q: mcq id="3488574c" -->
   The `.github/CODEOWNERS` file contains `/src/payments/  @org/payments-team`. What happens when a pull request changes `src/payments/refund.ts`?

   - [ ] The pull request is blocked forever
   - [x] The payments team is automatically requested as reviewers
   - [ ] Only the payments team can open pull requests
   - [ ] The file is ignored by CI

   <details><summary>Answer</summary>

   The payments team is asked to review. With "Require review from Code Owners" turned on, their approval is also needed before merging.

   </details>

4. <!-- q: mcq id="3fcd521f" -->
   Which branch protection setting forces every change to `main` to arrive by squash or rebase, with no merge commits?

   - [ ] Require signed commits
   - [x] Require linear history
   - [ ] Require conversation resolution
   - [ ] Dismiss stale approvals

   <details><summary>Answer</summary>

   Require linear history. A merge commit would add a second line to the graph, so it is refused.

   </details>

5. <!-- q: open id="d3babc29" -->
   Why turn on "Dismiss stale pull request approvals when new commits are pushed"?

   <details><summary>Answer</summary>

   Without it, someone could get an approval and then push new, unreviewed commits, and the old approval would still let them merge. Dismissing stale approvals means the approval always covers the code that actually gets merged.

   </details>

6. <!-- q: exact id="d9675b45" answer="400" -->
   According to the lesson, a good pull request should ideally be smaller than how many lines of diff?

   <details><summary>Answer</summary>

   400. Small pull requests get reviewed properly; huge ones get skimmed.

   </details>

## Related
<!-- bite: 27687957-74ac-4fcb-9563-b13e3362cdaf -->
- [[devops/05-ci-cd/02-ci-cd-tools|CI/CD Tools]] — GitHub Actions dissected via this vault's own deploy pipeline
- [[git/15-the-github-cli|The GitHub CLI]] — every rule on this page, driven from the terminal
- [[devops/05-ci-cd/index|DevOps → CI/CD]] — GitHub Actions itself, in depth, across 10 notes
- [[git/13-branching-strategies|Branching Strategies]] — what the protection rules are protecting
- [[git/11-tags-and-versioning|Tags and Versioning]] — releases cut from CI
- [[git/index|Git course map]]

## About this lesson
<!-- bite: d5d21ad1-0acb-42df-965f-1db675b4564d -->

**Level:** Intermediate. **Covers:** The layer above Git itself: branch protection, CODEOWNERS, rulesets, pull request practice — and how a CI system interacts with your repository once those rules exist.
