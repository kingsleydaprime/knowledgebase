# Branching Strategies

**[Intermediate]** — GitHub Flow, GitFlow, trunk-based development and the forking workflow: what each optimises for, when it fits, and the branch naming convention that goes with them.

## Why Strategy Matters

Without an agreed branching strategy, teams develop inconsistent habits: some people work directly on main, others create branches for every keystroke, PRs sit unreviewed for days, and no one is sure if main is deployable at any given moment. A branching strategy is a social contract — everyone on the team knows the rules without asking.

## GitHub Flow — Simple, Continuous Deployment

The most practical strategy for most teams. One rule: `main` is always deployable.

```
main ─────────────────────────────────────────→ (protected, always deployable)
      │             │              │
      └─ feat/a     └─ fix/b       └─ feat/c
         │               │              │
         ├─ commits       ├─ commit      ├─ commits
         └─ PR → CI → review → squash merge
```

**The workflow:**

```bash
# 1. Always start from latest main
git checkout main && git pull
git checkout -b feature/user-auth

# 2. Work in small, frequent commits
git add -p
git commit -m "feat(auth): add JWT token generation"
git commit -m "feat(auth): add token validation middleware"
git commit -m "test(auth): add unit tests for JWT service"

# 3. Keep branch up to date with main (daily, or before opening PR)
git fetch origin
git rebase origin/main

# 4. Push and open PR
git push -u origin feature/user-auth
# Open PR on GitHub

# 5. After approval and CI green: squash merge via GitHub UI
# This collapses all feature commits into one clean commit on main

# 6. Delete branch
git branch -d feature/user-auth
git push origin --delete feature/user-auth
```

**Merge strategies on GitHub:**

- **Squash and merge** — All feature commits collapse into one commit on main. Clean history. Good for most teams.
- **Rebase and merge** — Feature commits are replayed onto main linearly. Preserves individual commits. Good when commits are already clean.
- **Create a merge commit** — Standard merge, preserves branch in history. Use with `--no-ff` if you want to see branches in git log.

**Best for:** Small to medium teams, continuous deployment, web services, any team that ships multiple times per day.

---

## GitFlow — Structured Release Management

For products with scheduled release cycles — mobile apps, versioned APIs, enterprise software shipped to customers.

**Branch structure:**

```
main ─────────────────────────────────────────────────────→ (tagged releases only)
   │                                                    │
   └─ develop ──────────────────────────────────────→  │
          │                    │                    │   │
          └─ feature/auth      └─ feature/payments  │   │
                   │                 │              │   │
                   └─ merge develop  └─ merge        │   │
                             │                      │   │
                             └─ release/2.0 ─────────┘   │
                                      │               │   │
                                 bugfix only      merge  │
                                                 main+   │
                                                 develop  │
                                                          │
                                                hotfix/2.0.1
                                                     │
                                              merge main+develop
```

**Commands for each branch type:**

```bash
# Feature branch
git checkout develop
git checkout -b feature/payment-integration
# work, commit...
git checkout develop && git merge --no-ff feature/payment-integration
git branch -d feature/payment-integration

# Release branch (when develop is ready to release)
git checkout develop
git checkout -b release/2.0.0
# Only bug fixes here — no new features
git commit -m "fix: resolve edge case in payment flow"
git commit -m "chore(release): bump version to 2.0.0"

# Finish the release
git checkout main && git merge --no-ff release/2.0.0
git tag -a v2.0.0 -m "Release 2.0.0"
git checkout develop && git merge --no-ff release/2.0.0
git branch -d release/2.0.0

# Hotfix (urgent production bug)
git checkout main
git checkout -b hotfix/2.0.1
git commit -m "fix: resolve critical XSS vulnerability"

# Finish the hotfix
git checkout main && git merge --no-ff hotfix/2.0.1
git tag -a v2.0.1 -m "Hotfix 2.0.1"
git checkout develop && git merge --no-ff hotfix/2.0.1
git branch -d hotfix/2.0.1
```

**git-flow CLI (automates all of the above):**

```bash
# Install
brew install git-flow-avh   # macOS
sudo apt install git-flow   # Ubuntu

# Initialise in a repo
git flow init   # accepts all defaults with -d

# Feature
git flow feature start user-auth
git flow feature finish user-auth   # merges to develop, deletes branch

# Release
git flow release start 2.0.0
git flow release finish 2.0.0   # merges to main+develop, tags, deletes

# Hotfix
git flow hotfix start 2.0.1
git flow hotfix finish 2.0.1
```

**Best for:** Mobile apps (App Store review cycles), versioned SDKs/libraries, enterprise software, teams maintaining multiple live versions.

---

## Trunk-Based Development — Maximum Velocity

Developers commit directly to `main` or via branches that live less than one day. No long-running branches. Feature flags control what users see.

```
main ─────────────────────────────────────────────→
  c1 c2 c3       c6 c7       c10 c11 c12
         │            │
         c4 c5─merge  c8 c9─merge
        (< 1 day)    (< 1 day)
```

**Key disciplines:**

```bash
# Never let a branch live more than a day
# If it's going to take longer → use a feature flag

# Commit directly to main for small changes
git checkout main && git pull
# make a small change
git commit -m "fix: correct typo in error message"
git push

# For slightly larger work: short-lived branch
git checkout -b fix/auth-null-pointer
git commit -m "fix(auth): handle null user in middleware"
git push -u origin fix/auth-null-pointer
# Open PR, get fast review (hours, not days), merge same day

# Feature flags in code
if (featureFlags.isEnabled('new-checkout-v2', userId)) {
  return newCheckoutFlow();
}
return legacyCheckout();
```

**What makes trunk-based work:**
- CI runs in < 10 minutes — slow CI blocks everyone
- High test coverage — need confidence that `main` always works
- Feature flags — incomplete features are hidden, not branched
- Small, frequent commits — easier to review, less risk
- On-call culture — whoever breaks main fixes it immediately

**Best for:** Google-scale teams, companies with strong CI/CD infrastructure, teams that ship dozens of times per day. Hard to adopt without existing test coverage and feature flag infrastructure.

---

## Forking Workflow (Open Source)

Used when contributors don't have write access to the main repository.

```
Upstream (org/project)  ← PR from fork
         │
         └─ Fork (contributor/project)
                  │
                  └─ feature branch → PR → upstream
```

```bash
# 1. Fork the repo on GitHub

# 2. Clone your fork
git clone https://github.com/you/project.git
cd project

# 3. Add upstream remote
git remote add upstream https://github.com/org/project.git
git remote -v
# origin   https://github.com/you/project.git (your fork)
# upstream https://github.com/org/project.git (original)

# 4. Always branch from latest upstream
git fetch upstream
git checkout -b feature/my-contribution upstream/main

# 5. Work and commit
git commit -m "feat: add awesome feature"

# 6. Keep up to date with upstream during development
git fetch upstream
git rebase upstream/main

# 7. Push to your fork and open PR to upstream
git push -u origin feature/my-contribution
# Open PR: your fork → upstream repo
```

---

## Choosing a Strategy

```
Small team (1-5 people), continuous deployment?
  → GitHub Flow

Large team, scheduled quarterly releases, multiple versions in production?
  → GitFlow

Elite team, extreme CI/CD, strong test coverage, feature flags?
  → Trunk-based development

Open source, or contributors without write access?
  → Forking workflow

Most teams at most companies?
  → GitHub Flow
```

The honest summary: GitHub Flow is the right default and the other three are answers to specific constraints. Adopt GitFlow because you genuinely ship versioned releases, not because it looks rigorous — its overhead is real and most teams that adopt it end up working around it.

---

## Branch Naming — Complete Convention

```
# Format
<type>/<optional-ticket-id>-<short-description>

# Feature work
feature/user-authentication
feature/PROJ-142-payment-integration
feature/add-dark-mode

# Bug fixes
fix/login-safari-bug
fix/PROJ-89-null-pointer-checkout
bugfix/cart-total-calculation

# Hotfixes (urgent production bugs)
hotfix/critical-xss-vulnerability
hotfix/payment-gateway-timeout

# Release branches (GitFlow)
release/v1.2.0
release/2.0.0-rc1

# Chores, maintenance
chore/update-dependencies
chore/remove-deprecated-api
deps/upgrade-node-20

# Documentation
docs/api-reference
docs/onboarding-guide

# Experiments (disposable, no PR required)
experiment/new-caching-strategy
spike/postgres-migration

# Rules:
# - All lowercase
# - Hyphens, not underscores or spaces
# - Short but descriptive (3-5 words after the type)
# - Include ticket number when possible (links PR to issue tracker)
# - Type matches conventional commit type where applicable
```

---

## Related
- [[git/07-merge-vs-rebase|Merge vs Rebase]] — the per-commit decision inside each strategy
- [[git/14-github-and-ci|GitHub as a Platform]] — branch protection is how a strategy gets enforced
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — trunk-based development assumes a fast, trustworthy pipeline
- [[git/README|Git course map]]
