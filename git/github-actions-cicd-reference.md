# GitHub Actions & CI/CD — Comprehensive Reference Guide

> A deep, practical reference covering GitHub Actions from first principles to production pipelines.
> Covers YAML syntax, triggers, runners, secrets, CI pipelines, CD pipelines,
> deployment strategies, semantic versioning, reusable workflows, and security.

---

## Table of Contents

1. [What CI/CD Is and Why It Matters](#1-what-cicd-is-and-why-it-matters)
2. [GitHub Actions — How It Works](#2-github-actions--how-it-works)
3. [Workflow YAML — Complete Syntax Reference](#3-workflow-yaml--complete-syntax-reference)
4. [Triggers — on:](#4-triggers--on)
5. [Jobs and Steps](#5-jobs-and-steps)
6. [Runners](#6-runners)
7. [Contexts and Expressions](#7-contexts-and-expressions)
8. [Secrets, Variables, and Environments](#8-secrets-variables-and-environments)
9. [Caching](#9-caching)
10. [Artifacts](#10-artifacts)
11. [Matrix Builds](#11-matrix-builds)
12. [Reusable Workflows and Composite Actions](#12-reusable-workflows-and-composite-actions)
13. [CI Pipeline — The Complete Build](#13-ci-pipeline--the-complete-build)
14. [CD Pipeline — Deployment](#14-cd-pipeline--deployment)
15. [Deployment Strategies](#15-deployment-strategies)
16. [Branching Strategies](#16-branching-strategies)
17. [Branch Protection Rules](#17-branch-protection-rules)
18. [Semantic Versioning and Releases](#18-semantic-versioning-and-releases)
19. [Security in CI/CD](#19-security-in-cicd)
20. [Complete Real-World Pipeline Examples](#20-complete-real-world-pipeline-examples)
21. [Troubleshooting and Debugging](#21-troubleshooting-and-debugging)

---

## 1. What CI/CD Is and Why It Matters

### 1.1 The Problem CI/CD Solves

Before CI/CD, software was developed in long branches that diverged from main for weeks or months. Integration happened late — and was painful. Manual deployment was error-prone, inconsistent between environments, and required heroic effort from one person who "knew how to deploy."

**CI (Continuous Integration)** — Every code change is automatically built, tested, and verified before it can be merged. Problems are caught within minutes of being introduced, not days later when someone else's work breaks against yours.

**CD (Continuous Delivery)** — Every change that passes CI is automatically deployable. A human still decides when to deploy.

**CD (Continuous Deployment)** — Every change that passes CI is automatically deployed to production. No human in the loop.

### 1.2 The Core Value

```
Without CI/CD:
Developer commits → PR reviewed → merged → someone manually runs tests →
someone manually builds → someone manually deploys → hope nothing breaks

With CI/CD:
Developer commits → automated tests run → automated build → automated deploy →
system tells you if anything broke → rollback is one click
```

The goal is to make deployment so routine, so boring, and so safe that it stops being a special event.

### 1.3 The CI/CD Pipeline Stages

```
Code Push
    ↓
Lint & Format Check      ← catches style issues immediately (seconds)
    ↓
Unit Tests               ← catches logic bugs (minutes)
    ↓
Integration Tests        ← catches system-level bugs (minutes)
    ↓
Security Scan            ← catches vulnerabilities (minutes)
    ↓
Build Docker Image       ← produces deployable artifact (minutes)
    ↓
Push to Registry         ← image available for deployment
    ↓
Deploy to Staging        ← automated
    ↓
Smoke Tests              ← verify staging is alive
    ↓
Deploy to Production     ← automated or manual gate
    ↓
Post-deploy Health Check ← verify production is alive
```

---

## 2. GitHub Actions — How It Works

### 2.1 Core Concepts

**Workflow** — A YAML file in `.github/workflows/`. Defines what to run and when. A repository can have multiple workflows.

**Event (Trigger)** — What causes a workflow to run: a push, a pull request, a schedule, a manual trigger, etc.

**Job** — A set of steps that run on a single runner. Jobs in a workflow run in parallel by default. You can make them sequential with `needs:`.

**Step** — A single task within a job: run a shell command, or use a pre-built action.

**Action** — A reusable unit of work. Can be from the GitHub Marketplace, a public repository, or your own code.

**Runner** — The machine that executes a job. GitHub provides hosted runners (Ubuntu, Windows, macOS) or you can host your own.

**Artifact** — A file or set of files produced by a workflow and uploaded for download or use by other jobs.

### 2.2 File Location and Structure

```
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml           # CI pipeline — runs on every PR
        ├── deploy.yml       # CD pipeline — runs on merge to main
        ├── release.yml      # Release pipeline — runs on tag push
        └── scheduled.yml    # Scheduled tasks
```

### 2.3 The Execution Flow

```
1. Event occurs (push, PR, schedule, etc.)
2. GitHub finds matching workflows in .github/workflows/
3. For each matching workflow:
   a. Evaluate trigger conditions (branches, paths, etc.)
   b. Spin up runner(s) for each job
   c. Check out the repository
   d. Execute steps in order
   e. Report success or failure
```

---

## 3. Workflow YAML — Complete Syntax Reference

### 3.1 Top-Level Structure

```yaml
name: CI Pipeline          # Display name in GitHub UI (optional but helpful)

on:                        # Trigger(s) — see Section 4
  push:
    branches: [main]

env:                       # Environment variables available to all jobs
  NODE_VERSION: '20'
  REGISTRY: ghcr.io

defaults:                  # Default settings for all run steps
  run:
    shell: bash
    working-directory: ./src

concurrency:               # Prevent duplicate runs
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel older runs for the same branch

permissions:               # Workflow-level permissions (principle of least privilege)
  contents: read
  packages: write
  pull-requests: write

jobs:                      # The actual work — see Section 5
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Hello"
```

### 3.2 Concurrency Control

```yaml
# Cancel in-progress runs when a new commit is pushed to the same branch
# Prevents stacking up CI runs for rapid commits
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# For deployments: don't cancel in-progress deploys, just queue
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false   # Wait for current deploy to finish
```

### 3.3 Permissions

GitHub Actions runs with a token (`GITHUB_TOKEN`) that has permissions to the repository. Declare only what you need:

```yaml
permissions:
  contents: read           # Read repo content (checkout)
  contents: write          # Write to repo (create releases, commit)
  packages: read           # Read GitHub Packages
  packages: write          # Push to GitHub Container Registry
  issues: write            # Comment on issues
  pull-requests: write     # Comment on PRs, set status
  actions: read            # Read workflow runs
  deployments: write       # Create deployment records
  id-token: write          # OIDC token for cloud auth (AWS, GCP)
  security-events: write   # Upload SARIF security results

# Grant minimal permissions at workflow level, override at job level if needed
# Job-level permissions override workflow-level for that job
```

---

## 4. Triggers — on:

### 4.1 Push and Pull Request

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'      # matches release/1.0, release/2.x, etc.
      - '!hotfix/**'      # excludes hotfix branches
    paths:
      - 'src/**'          # only trigger if files in src/ changed
      - 'package.json'
      - '!**.md'          # don't trigger for markdown changes
    tags:
      - 'v*'              # trigger on version tags: v1.0.0, v2.3.1
      - 'v[0-9]+.[0-9]+.[0-9]+'  # more specific semver pattern

  pull_request:
    branches: [main, develop]
    types:
      - opened            # PR created
      - synchronize       # new commit pushed to PR
      - reopened          # PR reopened
      - ready_for_review  # PR marked ready (moved from draft)
    paths-ignore:
      - 'docs/**'
      - '*.md'

  pull_request_target:    # Runs in context of base branch (access to secrets)
    types: [opened, synchronize]
    # Use carefully — PRs from forks run in target repo context
```

### 4.2 Manual Triggers

```yaml
on:
  workflow_dispatch:      # Manual trigger via GitHub UI or API
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production
        default: staging
      version:
        description: 'Version to deploy (leave empty for latest)'
        required: false
        type: string
      dry_run:
        description: 'Run without making changes'
        required: false
        type: boolean
        default: false
      debug:
        description: 'Enable debug logging'
        type: boolean
        default: false
```

```yaml
# Access the inputs in your workflow
jobs:
  deploy:
    steps:
      - run: echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"
      - if: inputs.dry_run == false
        run: ./deploy.sh ${{ inputs.environment }}
```

### 4.3 Scheduled Triggers

```yaml
on:
  schedule:
    - cron: '0 2 * * *'          # every day at 2 AM UTC
    - cron: '0 */6 * * *'        # every 6 hours
    - cron: '0 9 * * 1-5'        # 9 AM UTC Monday-Friday
    - cron: '30 5 1 * *'         # 5:30 AM on the first of every month

# Cron syntax: minute hour day-of-month month day-of-week
# Note: scheduled workflows only run on the default branch
```

### 4.4 Other Triggers

```yaml
on:
  release:
    types: [published, created, released]

  issues:
    types: [opened, labeled]

  issue_comment:
    types: [created]

  workflow_run:           # trigger when another workflow completes
    workflows: ['CI']
    types: [completed]
    branches: [main]

  repository_dispatch:    # trigger via API (external systems)
    types: [deploy, test]
    # curl -X POST https://api.github.com/repos/owner/repo/dispatches \
    #   -H "Authorization: token $TOKEN" \
    #   -d '{"event_type": "deploy"}'

  create:                 # branch or tag created
  delete:                 # branch or tag deleted
  fork:
  watch:
    types: [started]      # someone stars the repo
```

### 4.5 Filtering Events

```yaml
# Only run when specific files change
on:
  push:
    paths:
      - 'src/**/*.ts'
      - 'package*.json'
      - 'Dockerfile'
      - '.github/workflows/ci.yml'  # re-run CI if the CI config changes

# Only run on certain branches
on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
    branches-ignore:
      - 'dependabot/**'  # skip Dependabot PRs
```

---

## 5. Jobs and Steps

### 5.1 Job Structure

```yaml
jobs:
  test:                              # Job ID (used for references)
    name: Run Tests                  # Display name in UI
    runs-on: ubuntu-latest           # Runner — see Section 6
    timeout-minutes: 30              # Kill job if it exceeds this
    continue-on-error: false         # Fail workflow if this job fails

    needs: [lint]                    # Run after lint job completes
    needs: [build, test]             # Run after BOTH build and test

    if: github.ref == 'refs/heads/main'  # Conditional — only run on main

    environment:
      name: staging                  # GitHub environment (for protection rules)
      url: https://staging.example.com

    outputs:                         # Values this job exposes to other jobs
      version: ${{ steps.version.outputs.value }}
      image_tag: ${{ steps.build.outputs.tag }}

    env:                             # Job-level environment variables
      NODE_ENV: test

    steps:
      - name: Step name             # Display name
        id: step_id                 # For referencing outputs: steps.step_id.outputs.x
        uses: actions/checkout@v4   # Use an action
        with:                       # Action inputs
          fetch-depth: 0
```

### 5.2 Steps — run vs uses

```yaml
steps:
  # Shell command
  - name: Install dependencies
    run: npm ci

  # Multi-line shell command
  - name: Build and test
    run: |
      npm run build
      npm test
      echo "Done"

  # With specific shell
  - name: Python script
    shell: python
    run: |
      import json
      print(json.dumps({"status": "ok"}))

  # With working directory
  - name: Build frontend
    working-directory: ./frontend
    run: npm run build

  # Use a marketplace action
  - name: Checkout
    uses: actions/checkout@v4      # Always pin to a version tag

  # Use action with inputs
  - name: Setup Node.js
    uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'

  # Use action from same repo
  - uses: ./.github/actions/my-composite-action
    with:
      input: value

  # Use action from another repo
  - uses: org/repo/.github/actions/my-action@v2

  # Conditional step
  - name: Deploy to production
    if: github.ref == 'refs/heads/main' && success()
    run: ./deploy.sh production

  # Continue even if this step fails
  - name: Optional check
    continue-on-error: true
    run: npm run optional-check

  # Environment variables for a specific step
  - name: Run with env
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      NODE_ENV: production
    run: node migrate.js
```

### 5.3 Step Outputs

```yaml
steps:
  - name: Get version
    id: version
    run: |
      VERSION=$(node -p "require('./package.json').version")
      echo "value=$VERSION" >> $GITHUB_OUTPUT   # set output
      echo "tag=v$VERSION" >> $GITHUB_OUTPUT

  - name: Use the version
    run: echo "Version is ${{ steps.version.outputs.value }}"

  # Job outputs (for passing between jobs)
jobs:
  build:
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=1.2.3" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

### 5.4 Job Dependencies and Fan-Out/Fan-In

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:unit

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:integration

  build:
    needs: [lint, test-unit, test-integration]  # fan-in: wait for all three
    runs-on: ubuntu-latest
    steps:
      - run: docker build .

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh staging

  deploy-production:
    needs: deploy-staging
    environment: production       # requires manual approval
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh production
```

```
lint ──────────┐
               ├──→ build ──→ deploy-staging ──→ deploy-production
test-unit ─────┤
               │
test-integration┘
```

### 5.5 Expressions and Conditions

```yaml
# Job/step condition syntax
if: <expression>

# Common conditions
if: success()                          # previous steps succeeded (default)
if: failure()                          # any previous step failed
if: always()                           # run regardless of previous results
if: cancelled()                        # workflow was cancelled

if: github.event_name == 'push'
if: github.ref == 'refs/heads/main'
if: github.actor != 'dependabot[bot]'
if: contains(github.event.pull_request.labels.*.name, 'deploy')
if: startsWith(github.ref, 'refs/tags/v')

# Combining conditions
if: github.ref == 'refs/heads/main' && success()
if: failure() || cancelled()

# Check if a previous step succeeded/failed specifically
if: steps.tests.outcome == 'success'
if: steps.build.outcome == 'failure'
# outcomes: success, failure, cancelled, skipped
```

---

## 6. Runners

### 6.1 GitHub-Hosted Runners

GitHub provides virtual machines that are fully managed:

```yaml
runs-on: ubuntu-latest       # Latest Ubuntu LTS (recommended for most tasks)
runs-on: ubuntu-22.04        # Specific Ubuntu version (pinned, more stable)
runs-on: ubuntu-20.04
runs-on: windows-latest
runs-on: windows-2022
runs-on: macos-latest
runs-on: macos-13
```

**What's included on ubuntu-latest:**
- Docker and Docker Compose
- Node.js, Python, Java, Go, Ruby, .NET
- Git, curl, wget, jq
- AWS CLI, Azure CLI, GCloud CLI
- Many more — see the full software list in GitHub docs

**Specs:** 2-core CPU, 7GB RAM, 14GB SSD. For larger jobs, GitHub offers paid larger runners.

### 6.2 Self-Hosted Runners

Run Actions on your own infrastructure — useful for:
- Jobs that need more resources than GitHub's 2-core runners
- Jobs that need access to private network resources
- Cost reduction for high-volume pipelines
- Specific hardware (GPU, ARM, etc.)

```yaml
runs-on: self-hosted                    # Any self-hosted runner
runs-on: [self-hosted, linux, x64]      # With labels
runs-on: [self-hosted, production]      # Custom label
```

**Setting up a self-hosted runner:**

```bash
# On your server (Ubuntu)
mkdir actions-runner && cd actions-runner

# Download the runner (get the exact URL from GitHub: Settings → Actions → Runners)
curl -o actions-runner-linux-x64-2.319.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.319.0/actions-runner-linux-x64-2.319.0.tar.gz

tar xzf ./actions-runner-linux-x64-2.319.0.tar.gz

# Configure (token from GitHub Settings → Actions → Runners → New self-hosted runner)
./config.sh --url https://github.com/your-org/your-repo --token YOUR_TOKEN

# Run as a service
sudo ./svc.sh install
sudo ./svc.sh start

# Runner labels help target it in workflows
./config.sh --url ... --token ... --labels production,linux,x64
```

### 6.3 Runner Groups (GitHub Enterprise / Organizations)

```yaml
# Target a specific runner group
jobs:
  deploy:
    runs-on:
      group: production-runners
      labels: [linux, x64]
```

### 6.4 Docker Container Jobs

Run a job inside a Docker container instead of directly on the runner OS:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: node:20-alpine
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
      env:
        NODE_ENV: test
      options: --cpus 2

    services:                          # Sidecar containers (databases, etc.)
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
        env:
          DATABASE_URL: postgresql://postgres:postgres@postgres:5432/testdb
          REDIS_URL: redis://redis:6379
```

---

## 7. Contexts and Expressions

### 7.1 What Contexts Are

Contexts are objects containing information about the workflow run, available as `${{ context.property }}`.

### 7.2 github Context

```yaml
${{ github.event_name }}         # push, pull_request, workflow_dispatch, etc.
${{ github.ref }}                # refs/heads/main, refs/tags/v1.0.0
${{ github.ref_name }}           # main, v1.0.0 (just the branch/tag name)
${{ github.sha }}                # full commit SHA: a1b2c3d4e5f6...
${{ github.actor }}              # username who triggered the workflow
${{ github.repository }}         # owner/repo-name
${{ github.repository_owner }}   # owner
${{ github.run_id }}             # unique ID for this workflow run
${{ github.run_number }}         # sequential run number
${{ github.workflow }}           # workflow name
${{ github.job }}                # current job ID
${{ github.workspace }}          # path to checked-out repo on runner
${{ github.token }}              # GITHUB_TOKEN (same as secrets.GITHUB_TOKEN)

# Pull request specific
${{ github.event.pull_request.number }}
${{ github.event.pull_request.head.sha }}
${{ github.event.pull_request.base.ref }}  # target branch
${{ github.event.pull_request.labels.*.name }}

# Push specific
${{ github.event.before }}       # previous commit SHA
${{ github.event.after }}        # new commit SHA
${{ github.event.commits[0].message }}
```

### 7.3 env Context

```yaml
${{ env.MY_VARIABLE }}          # access environment variables set with env:
```

### 7.4 secrets Context

```yaml
${{ secrets.MY_SECRET }}         # access repository/org secrets
${{ secrets.GITHUB_TOKEN }}      # automatic token provided by GitHub
```

### 7.5 steps Context

```yaml
${{ steps.step_id.outputs.my_output }}   # step output
${{ steps.step_id.outcome }}             # success, failure, cancelled, skipped
${{ steps.step_id.conclusion }}          # final conclusion after continue-on-error
```

### 7.6 needs Context

```yaml
${{ needs.job_id.outputs.my_output }}    # output from a required job
${{ needs.job_id.result }}               # success, failure, cancelled, skipped
```

### 7.7 runner Context

```yaml
${{ runner.os }}                 # Linux, Windows, macOS
${{ runner.arch }}               # X64, ARM64
${{ runner.temp }}               # temp directory path
${{ runner.tool_cache }}         # tool cache path
```

### 7.8 Expression Functions

```yaml
# String functions
${{ contains('hello world', 'hello') }}       # true
${{ startsWith(github.ref, 'refs/tags/') }}   # true for tag pushes
${{ endsWith(github.ref, '/main') }}
${{ format('Hello {0}!', github.actor) }}     # Hello kingsley!
${{ join(matrix.os, ', ') }}                  # ubuntu-latest, windows-latest

# Array/object functions
${{ toJSON(github.event) }}                   # JSON string of the context
${{ fromJSON('{"key": "value"}').key }}       # parse JSON: "value"

# Conditional
${{ github.event_name == 'push' && 'yes' || 'no' }}  # ternary-like

# hashFiles — for cache keys
${{ hashFiles('**/package-lock.json') }}       # hash of all package-lock.json files
${{ hashFiles('Dockerfile', 'package.json') }} # hash of specific files
```

---

## 8. Secrets, Variables, and Environments

### 8.1 Secrets

Secrets are encrypted values stored in GitHub and injected into workflows. They are never printed in logs (GitHub masks them).

**Where to set them:**
- Repository: Settings → Secrets and variables → Actions → Secrets
- Organisation: applies to all repos in the org
- Environment: scoped to a specific deployment environment

```yaml
# Accessing secrets
steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    run: ./deploy.sh

# GITHUB_TOKEN — automatically provided, no setup needed
- name: Push to registry
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: docker push ghcr.io/${{ github.repository }}/app:latest

# Secrets in with: (action inputs)
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_HUB_USERNAME }}
    password: ${{ secrets.DOCKER_HUB_TOKEN }}
```

**Secret naming conventions:**
```
VPS_SSH_KEY           — SSH private key for server access
VPS_HOST              — server hostname/IP
VPS_USER              — SSH username
DOCKER_HUB_USERNAME   — Docker Hub credentials
DOCKER_HUB_TOKEN      — Docker Hub access token (not password)
DATABASE_URL          — database connection string
JWT_SECRET            — application secret
SLACK_WEBHOOK_URL     — notification webhook
AWS_ACCESS_KEY_ID     — AWS credentials
AWS_SECRET_ACCESS_KEY
```

### 8.2 Variables (Non-Secret Configuration)

Variables are like secrets but not encrypted — for non-sensitive configuration values visible in logs.

```yaml
# Set at: Settings → Secrets and variables → Actions → Variables
# Access with: vars context

steps:
  - run: echo "Deploying to ${{ vars.DEPLOY_HOST }}"
  - run: echo "App version prefix: ${{ vars.VERSION_PREFIX }}"
```

### 8.3 Environments

Environments add a layer of protection to deployments — required reviewers, wait timers, and scoped secrets.

**Create at:** Settings → Environments → New environment

```yaml
jobs:
  deploy-staging:
    environment:
      name: staging
      url: https://staging.yourdomain.com   # shown in GitHub UI after deploy

  deploy-production:
    environment:
      name: production
      url: https://yourdomain.com
    # If production environment has required reviewers configured:
    # workflow will pause here until a reviewer approves in the GitHub UI
```

**Environment features:**
- **Required reviewers** — one or more people must approve before the job runs
- **Wait timer** — delay before the job runs (e.g. 5 minutes to catch last-minute issues)
- **Deployment branches** — only certain branches can deploy to this environment
- **Environment secrets** — secrets that are only available in that environment's jobs

### 8.4 Secret Hierarchy and Scoping

```
Organisation secrets → available to all repos in the org
    ↓
Repository secrets → available to all workflows in the repo
    ↓
Environment secrets → only available in jobs targeting that environment
```

If the same secret name exists at multiple levels, the most specific level wins.

---

## 9. Caching

### 9.1 Why Caching Matters

Installing dependencies (`npm install`, `mvn install`, `pip install`) can take 2–5 minutes on every CI run. Caching stores the result of those installations and restores them on subsequent runs. With a warm cache, dependency installation drops to seconds.

### 9.2 actions/cache

```yaml
- name: Cache node modules
  uses: actions/cache@v4
  with:
    path: ~/.npm                               # what to cache
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    # key: if this exact key exists, restore from cache (cache hit)
    # if not found (cache miss), the job runs normally and saves at the end

    restore-keys: |
      ${{ runner.os }}-npm-                   # partial match fallback keys
      ${{ runner.os }}-
    # restore-keys: tried in order if exact key misses
    # allows using a slightly stale cache when lock file changed
```

### 9.3 Language-Specific Cache Examples

**Node.js:**

```yaml
# Option 1: Manual cache
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-node-

- run: npm ci

# Option 2: Built into setup-node (recommended)
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'          # or 'yarn' or 'pnpm'
    # automatically caches ~/.npm and restores before npm ci
```

**Java/Maven:**

```yaml
- uses: actions/setup-java@v4
  with:
    java-version: '21'
    distribution: 'temurin'
    cache: 'maven'        # caches ~/.m2/repository

# Or manually:
- uses: actions/cache@v4
  with:
    path: ~/.m2/repository
    key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
    restore-keys: ${{ runner.os }}-maven-
```

**Python:**

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

# Or manually:
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: ${{ runner.os }}-pip-
```

**Docker layer caching:**

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push with cache
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: myimage:latest
    cache-from: type=gha          # use GitHub Actions cache
    cache-to: type=gha,mode=max   # save all layers to cache
```

### 9.4 Cache Keys Strategy

The cache key must balance:
- **Too specific** (hash of every file) → cache misses on any change
- **Too broad** (just the OS) → stale cache, wrong dependencies

```yaml
# Good cache key strategy:
key: ${{ runner.os }}-${{ matrix.node-version }}-npm-${{ hashFiles('**/package-lock.json') }}
# - Separate cache per OS (different binary paths)
# - Separate cache per Node version (different native module binaries)
# - Invalidate when lock file changes (new/updated dependencies)
# - Fall back to any cache for this OS+version combination
restore-keys: |
  ${{ runner.os }}-${{ matrix.node-version }}-npm-
  ${{ runner.os }}-${{ matrix.node-version }}-
```

---

## 10. Artifacts

### 10.1 What Artifacts Are

Artifacts are files uploaded from a workflow run that persist after the run ends. Uses:
- Pass build output between jobs (build in one job, deploy in another)
- Download test results, coverage reports, built binaries
- Debug failing builds by downloading logs

### 10.2 Uploading and Downloading

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build        # produces ./dist/

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-output          # artifact name
          path: ./dist/               # what to upload
          retention-days: 7           # how long to keep (default 90)
          if-no-files-found: error    # error | warn | ignore

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: build-output
          path: ./dist/               # where to put it

      - run: ls -la ./dist/
      - run: ./deploy.sh
```

### 10.3 Common Artifact Patterns

**Test results:**

```yaml
- name: Run tests
  run: npm test -- --coverage --reporters=json
  continue-on-error: true   # upload results even if tests fail

- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()              # upload even if tests failed
  with:
    name: test-results
    path: |
      coverage/
      test-results.json
```

**Multiple files pattern:**

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: app-bundle
    path: |
      dist/
      Dockerfile
      docker-compose.yml
      !dist/**/*.map        # exclude source maps
```

**Download all artifacts from a run:**

```yaml
- uses: actions/download-artifact@v4
  # No 'name' specified — downloads all artifacts into separate directories
  with:
    path: ./artifacts/

# Results in:
# ./artifacts/build-output/
# ./artifacts/test-results/
```

---

## 11. Matrix Builds

### 11.1 What Matrix Builds Are

Matrix builds run a job multiple times with different configurations in parallel. Essential for testing across multiple Node versions, OSes, or any variable combination.

### 11.2 Basic Matrix

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [18, 20, 22]
        # Creates 9 jobs: 3 OSes × 3 Node versions

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

### 11.3 Matrix with Include and Exclude

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20]
    include:
      # Add an extra combination not in the base matrix
      - os: ubuntu-latest
        node: 22
        experimental: true        # extra variable available as matrix.experimental
    exclude:
      # Remove a specific combination
      - os: windows-latest
        node: 18

  fail-fast: false    # don't cancel all matrix jobs if one fails (default: true)
  max-parallel: 4     # limit concurrent jobs (default: unlimited)
```

### 11.4 Dynamic Matrix from JSON

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          # Build matrix dynamically based on changed files, config, etc.
          echo 'matrix={"service":["api","worker","frontend"]}' >> $GITHUB_OUTPUT

  test:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing ${{ matrix.service }}"
```

---

## 12. Reusable Workflows and Composite Actions

### 12.1 Why Reusability Matters

Without reusable workflows, teams copy-paste the same CI logic across dozens of repositories. A change to the linting step means updating 20 files. Reusable workflows solve this — define once, call everywhere.

### 12.2 Reusable Workflows — Called Workflows

**Define the reusable workflow** (`.github/workflows/reusable-deploy.yml`):

```yaml
name: Reusable Deploy

on:
  workflow_call:                    # this makes it callable by other workflows
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: string
      image_tag:
        required: true
        type: string
      dry_run:
        required: false
        type: boolean
        default: false
    secrets:
      VPS_SSH_KEY:
        required: true
      VPS_HOST:
        required: true
      VPS_USER:
        required: true
    outputs:
      deploy_url:
        description: 'URL of the deployed application'
        value: ${{ jobs.deploy.outputs.url }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - name: Deploy
        id: deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/app
            docker compose pull
            docker compose up -d --remove-orphans
            echo "url=https://${{ inputs.environment }}.example.com" >> $GITHUB_OUTPUT
```

**Call it from another workflow:**

```yaml
name: Deploy Pipeline

on:
  push:
    branches: [main]

jobs:
  ci:
    uses: ./.github/workflows/reusable-ci.yml    # call from same repo

  deploy-staging:
    needs: ci
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
      image_tag: ${{ github.sha }}
    secrets:
      VPS_SSH_KEY: ${{ secrets.STAGING_SSH_KEY }}
      VPS_HOST: ${{ secrets.STAGING_HOST }}
      VPS_USER: ${{ secrets.STAGING_USER }}

  deploy-production:
    needs: deploy-staging
    uses: org/shared-workflows/.github/workflows/deploy.yml@main  # from another repo
    with:
      environment: production
      image_tag: ${{ github.sha }}
    secrets: inherit   # pass all secrets from calling workflow
```

### 12.3 Composite Actions

A composite action bundles multiple steps into a reusable action — lighter than a reusable workflow.

**Define** (`.github/actions/setup-and-install/action.yml`):

```yaml
name: Setup and Install
description: Sets up Node.js and installs dependencies with caching

inputs:
  node-version:
    description: 'Node.js version'
    required: false
    default: '20'
  working-directory:
    description: 'Where to run npm ci'
    required: false
    default: '.'

outputs:
  cache-hit:
    description: 'Whether the npm cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}

    - uses: actions/cache@v4
      id: cache
      with:
        path: ~/.npm
        key: ${{ runner.os }}-node${{ inputs.node-version }}-${{ hashFiles('**/package-lock.json') }}

    - name: Install dependencies
      shell: bash
      working-directory: ${{ inputs.working-directory }}
      run: npm ci
```

**Use it:**

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./.github/actions/setup-and-install
    with:
      node-version: '20'
  - run: npm test
```

---

## 13. CI Pipeline — The Complete Build

### 13.1 What a Good CI Pipeline Does

Every pull request and push should:
1. Fail fast on obvious issues (lint/format in seconds)
2. Run all tests in parallel where possible
3. Build the deployable artifact
4. Scan for security issues
5. Report status back to the PR

### 13.2 Complete Node.js / NestJS CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ─── Fast checks ──────────────────────────────────────────────────────────────
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Check formatting (Prettier)
        run: npm run format:check

      - name: Lint (ESLint)
        run: npm run lint

      - name: Type check
        run: npm run type-check

  # ─── Tests ────────────────────────────────────────────────────────────────────
  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Run unit tests
        run: npm run test:unit -- --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-unit
          path: coverage/
          retention-days: 3

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - run: npm ci

      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/testdb

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
          JWT_SECRET: test-secret-do-not-use-in-production

  # ─── Security ─────────────────────────────────────────────────────────────────
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for known vulnerabilities in dependencies
        run: npm audit --audit-level=high

      - name: Scan for secrets in code
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ─── Build ────────────────────────────────────────────────────────────────────
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [lint, test-unit, test-integration, security]
    permissions:
      contents: read
      packages: write

    outputs:
      image: ${{ steps.meta.outputs.tags }}
      digest: ${{ steps.push.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            GIT_SHA=${{ github.sha }}

      - name: Scan Docker image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: 1

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: trivy-results.sarif

  # ─── PR Summary ───────────────────────────────────────────────────────────────
  pr-comment:
    name: PR Status Comment
    runs-on: ubuntu-latest
    needs: [build]
    if: github.event_name == 'pull_request'
    permissions:
      pull-requests: write
    steps:
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `✅ CI passed! Image built: \`sha-${{ github.sha }}\``
            })
```

### 13.3 Complete Java / Spring Boot CI Pipeline

```yaml
name: Java CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: testdb
        options: >-
          --health-cmd "mysqladmin ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 3306:3306

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: temurin
          cache: maven

      - name: Build with Maven
        run: mvn -B package --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpassword

      - name: Run tests
        run: mvn -B test --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpassword

      - name: Upload test report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: surefire-reports
          path: target/surefire-reports/

      - name: Upload JAR
        uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: target/*.jar
```

---

## 14. CD Pipeline — Deployment

### 14.1 CD Pipeline Structure

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        default: staging

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.yourdomain.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd ~/app
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f

  smoke-test:
    name: Smoke Test
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - name: Wait for service
        run: |
          for i in {1..12}; do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://staging.yourdomain.com/health)
            [ "$STATUS" = "200" ] && echo "Healthy" && exit 0
            echo "Attempt $i: status $STATUS. Waiting..."
            sleep 10
          done
          echo "Service did not become healthy" && exit 1

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: smoke-test
    environment:
      name: production
      url: https://yourdomain.com
    # GitHub will pause here if production env has required reviewers
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd ~/app
            echo "${{ github.sha }}" > .current-sha
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f

  notify:
    name: Notify
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: always()
    steps:
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "${{ needs.deploy-production.result == 'success' && '✅' || '❌' }} Deploy to production: ${{ needs.deploy-production.result }}\nCommit: ${{ github.sha }}\nBy: ${{ github.actor }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 14.2 Rollback Workflow

```yaml
# .github/workflows/rollback.yml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        required: true
      sha:
        description: 'Git SHA to roll back to (leave empty for previous)'
        required: false

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4

      - name: Determine rollback target
        id: target
        run: |
          if [ -n "${{ inputs.sha }}" ]; then
            echo "sha=${{ inputs.sha }}" >> $GITHUB_OUTPUT
          else
            # Get the SHA before the current one
            PREV=$(git log --format="%H" -n 2 | tail -1)
            echo "sha=$PREV" >> $GITHUB_OUTPUT
          fi

      - name: Execute rollback
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets[format('{0}_HOST', inputs.environment)] }}
          username: ${{ secrets[format('{0}_USER', inputs.environment)] }}
          key: ${{ secrets[format('{0}_SSH_KEY', inputs.environment)] }}
          script: |
            cd ~/app
            IMAGE="ghcr.io/${{ github.repository }}:sha-${{ steps.target.outputs.sha }}"
            echo "Rolling back to: $IMAGE"
            docker pull $IMAGE
            IMAGE_TAG=sha-${{ steps.target.outputs.sha }} docker compose up -d
            echo "${{ steps.target.outputs.sha }}" > .current-sha
            echo "Rollback complete"
```

---

## 15. Deployment Strategies

### 15.1 Recreate (Simple)

Stop the old version, start the new one. Causes downtime. Only acceptable for non-production or low-traffic services.

```yaml
script: |
  cd ~/app
  docker compose down
  docker compose pull
  docker compose up -d
```

**Use when:** Development/staging environments, internal tools, services where brief downtime is acceptable.

### 15.2 Rolling Deployment

Replace instances one at a time. The load balancer routes traffic only to healthy instances. No downtime as long as you have multiple instances.

```bash
#!/bin/bash
# rolling-deploy.sh

set -e
SERVICE=$1
IMAGE=$2

echo "Starting rolling deployment of $SERVICE → $IMAGE"

# Scale up with new version alongside old
docker compose pull $SERVICE
docker compose up -d --no-deps --scale $SERVICE=2 --no-recreate $SERVICE

# Wait for new container to be healthy
sleep 15

# Scale back to desired replicas (removes old container)
docker compose up -d --no-deps --scale $SERVICE=1 --no-recreate $SERVICE

echo "Rolling deployment complete"
```

```yaml
# In GitHub Actions
- name: Rolling deploy
  uses: appleboy/ssh-action@v1
  with:
    host: ${{ secrets.VPS_HOST }}
    username: ${{ secrets.VPS_USER }}
    key: ${{ secrets.VPS_SSH_KEY }}
    script: |
      cd ~/app
      docker compose pull app
      # Start second instance alongside first
      docker compose up -d --no-deps --scale app=2 --no-recreate app
      # Wait for health check
      sleep 20
      # Remove the old one
      docker compose up -d --no-deps --scale app=1 --no-recreate app
      docker image prune -f
```

**Use when:** Single server with Traefik/Nginx, services that can run two versions simultaneously.

### 15.3 Blue-Green Deployment

Maintain two complete environments (blue = current, green = new). Switch traffic between them instantly. Instant rollback by switching back.

```yaml
# .github/workflows/blue-green.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Blue-green deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -e
            cd ~/app

            # Determine current and next color
            CURRENT=$(cat .active_color 2>/dev/null || echo "blue")
            NEXT=$([ "$CURRENT" = "blue" ] && echo "green" || echo "blue")

            echo "Current: $CURRENT → Deploying to: $NEXT"

            # Deploy to inactive environment
            IMAGE_TAG=${{ github.sha }} docker compose -f compose.$NEXT.yml up -d

            # Health check the new environment
            sleep 20
            STATUS=$(curl -sf http://localhost:808$([ "$NEXT" = "green" ] && echo 1 || echo 0)/health || echo "fail")
            if [ "$STATUS" != "ok" ]; then
              echo "Health check failed — aborting"
              docker compose -f compose.$NEXT.yml down
              exit 1
            fi

            # Switch traffic (update Traefik label or nginx upstream)
            echo "$NEXT" > .active_color

            # Shut down old environment after grace period
            sleep 10
            docker compose -f compose.$CURRENT.yml down

            echo "Switched traffic to $NEXT"
```

**Use when:** You need instant rollback, or running both versions simultaneously for testing is valuable.

### 15.4 Canary Deployment

Route a small percentage of traffic to the new version, monitor metrics, gradually increase.

```yaml
# Canary using Kubernetes + Argo Rollouts (see DevOps reference)
# For a VPS setup, approximate with weighted Traefik or Nginx upstream:

- name: Canary deploy (10% traffic)
  uses: appleboy/ssh-action@v1
  with:
    script: |
      cd ~/app
      # Start canary alongside stable
      docker compose up -d --no-deps --scale app-canary=1 app-canary
      # Update Traefik to weight: 90% stable, 10% canary
      # Monitor for 10 minutes, then promote or rollback
      sleep 600
      # Check error rate (example with simple log counting)
      ERRORS=$(docker logs app-canary --since 10m 2>&1 | grep ERROR | wc -l)
      TOTAL=$(docker logs app-canary --since 10m 2>&1 | wc -l)
      if [ $ERRORS -gt 10 ]; then
        echo "Too many errors in canary — rolling back"
        docker compose stop app-canary
        exit 1
      fi
      # Promote: make canary the new stable
      docker compose up -d --no-deps app
      docker compose stop app-canary
```

**Use when:** High-traffic production systems where you want to validate before full rollout.

### 15.5 Choosing a Strategy

```
Low traffic, internal tool, brief downtime OK?
  → Recreate

Single server, Docker + Traefik, need zero downtime?
  → Rolling

Multi-server with load balancer, need instant rollback?
  → Blue-Green

High traffic, want gradual confidence before full rollout?
  → Canary
```

---

## 16. Branching Strategies

### 16.1 GitHub Flow

The simplest strategy. Works for teams doing continuous deployment.

```
main ─────────────────────────────────────────→ (always deployable)
      │          │           │
      └─ feat/a  └─ feat/b   └─ fix/c
         │             │          │
         └─ PR → merge  └─ PR      └─ PR → merge
```

**Rules:**
1. `main` is always deployable and protected
2. All work happens in feature branches (`feature/`, `fix/`, `chore/`)
3. Open a PR — CI must pass — at least one review required
4. Merge to main → automatically deploy
5. Delete the branch after merge

**Branch naming:**
```
feature/user-authentication
feature/PROJ-142-payment-integration
fix/login-safari-bug
fix/PROJ-89-null-pointer-on-checkout
hotfix/critical-xss-vulnerability
chore/update-dependencies
docs/api-documentation
refactor/extract-auth-service
```

### 16.2 GitFlow

For teams with scheduled releases and multiple versions in production.

```
main ────────────────────────────────────────────────→ (production, tagged)
  │                                              │
  └─ develop ──────────────────────────────→    │
         │                    │                 │
         └─ feature/auth      └─ feature/pay    │
                  │                 │           │
                  └─ merge develop  └─ merge    │
                            │                   │
                            └─ release/1.2 ─────┘
                                    │         │
                                    │    hotfix/1.2.1
                                    │         │
                              merged to    merged to
                              main+develop main+develop
```

**Branches:**
- `main` — production only. Tagged at every release. Never commit directly here.
- `develop` — integration branch. All features merge here.
- `feature/*` — branches from `develop`, merged back to `develop`
- `release/*` — branches from `develop` when ready to release. Bug fixes only. Merges to `main` and `develop`.
- `hotfix/*` — branches from `main` for urgent production fixes. Merges to `main` and `develop`.

**When to use:** Large teams, scheduled releases, multiple versions in production simultaneously. Heavy overhead — most modern teams prefer GitHub Flow.

### 16.3 Trunk-Based Development

Developers commit directly to `main` (or very short-lived branches < 1 day). Feature flags hide incomplete work in production.

```
main ────────────────────────────────────────────→
  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │
  c1 c2  branch  c5 c6  branch  c9 c10 c11
         │              │
         c3 c4──merge   c7 c8──merge
        (< 1 day)      (< 1 day)
```

**Rules:**
1. Branches (if used) live less than one day
2. Every commit to main must be releasable
3. Feature flags (`if featureFlags.isEnabled('new-feature')`) hide incomplete work
4. CI must be fast (< 10 minutes) — slow CI blocks everyone
5. Every developer commits to main at least once per day

**When to use:** High-performing teams (Google, Stripe), continuous deployment, strong test coverage and feature flag infrastructure.

### 16.4 Choosing a Strategy

```
Small team (1-5 people), continuous deployment?
  → GitHub Flow

Large team, scheduled quarterly releases, multiple versions?
  → GitFlow

Elite team, extreme CI/CD, strong test coverage, feature flags?
  → Trunk-based development

Most teams at most companies?
  → GitHub Flow
```

---

## 17. Branch Protection Rules

### 17.1 What They Are

Branch protection rules prevent direct pushes to important branches and enforce quality gates before merging.

### 17.2 Configuration (GitHub Settings → Branches → Add rule)

**Recommended for `main`:**

```
Branch name pattern: main

☑ Require a pull request before merging
    ☑ Require approvals: 1 (or 2 for larger teams)
    ☑ Dismiss stale pull request approvals when new commits are pushed
    ☑ Require review from Code Owners

☑ Require status checks to pass before merging
    ☑ Require branches to be up to date before merging
    Required status checks: (add your CI job names)
      - CI / Lint & Format
      - CI / Unit Tests
      - CI / Integration Tests
      - CI / Build Docker Image

☑ Require conversation resolution before merging

☑ Require signed commits (if you've set up GPG signing)

☑ Require linear history (enforces squash/rebase merging — no merge commits)

☑ Do not allow bypassing the above settings
    (even admins can't force-push)

☐ Allow force pushes (leave unchecked for main)
☐ Allow deletions (leave unchecked for main)
```

**CODEOWNERS file** (`.github/CODEOWNERS`):

```
# Global owners — required reviewers for any file change
*                           @org/backend-team

# Specific paths
/src/auth/                  @org/security-team
/src/payments/              @org/payments-team @finance-lead
/.github/workflows/         @org/devops-team
/docs/                      @org/docs-team
Dockerfile                  @org/devops-team
```

### 17.3 Rulesets (GitHub Enterprise / newer repos)

GitHub Rulesets are a newer, more powerful alternative to branch protection rules — they can apply to multiple branches at once and have bypass lists:

```yaml
# Via GitHub API or terraform
# Apply to main and release/* branches simultaneously
# Allow DevOps team to bypass for emergency fixes
```

---

## 18. Semantic Versioning and Releases

### 18.1 Semantic Versioning (SemVer)

The version format is `MAJOR.MINOR.PATCH`:

- **MAJOR** — breaking changes. Users must update their code.
- **MINOR** — new features, backwards compatible.
- **PATCH** — bug fixes, backwards compatible.

```
v1.0.0    → Initial release
v1.0.1    → Bug fix (backwards compatible)
v1.1.0    → New feature (backwards compatible)
v2.0.0    → Breaking change (users must update)

Pre-release:
v2.0.0-alpha.1    → Alpha (unstable, internal testing)
v2.0.0-beta.1     → Beta (feature-complete, external testing)
v2.0.0-rc.1       → Release candidate (final testing before release)
```

### 18.2 Automated Version Bumping with Conventional Commits

When commit messages follow the Conventional Commits spec, tools can automatically determine the next version:

```
feat: add payment processing       → MINOR bump (1.0.0 → 1.1.0)
fix: resolve null pointer in login → PATCH bump (1.1.0 → 1.1.1)
feat!: change API response format  → MAJOR bump (1.1.1 → 2.0.0)
  BREAKING CHANGE: ...
docs: update readme                → no version bump
chore: update dependencies         → no version bump
```

### 18.3 Automated Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  packages: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.release.outputs.released }}
      version: ${{ steps.release.outputs.version }}
      tag: ${{ steps.release.outputs.tag }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0            # full history for changelog generation

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      # semantic-release analyses commits, determines version, creates tag,
      # generates changelog, and publishes release
      - name: Create Release
        id: release
        uses: cycjimmy/semantic-release-action@v4
        with:
          extra_plugins: |
            @semantic-release/changelog
            @semantic-release/git
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  docker:
    needs: release
    if: needs.release.outputs.released == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release.outputs.tag }}   # checkout the tagged commit

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ needs.release.outputs.version }}
```

**`.releaserc` (semantic-release configuration):**

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", {
      "changelogFile": "CHANGELOG.md"
    }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

### 18.4 Manual Version Tagging Workflow

```yaml
# .github/workflows/tag-release.yml
name: Tag and Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version (e.g. 1.2.3)'
        required: true
      release_notes:
        description: 'Release notes'
        required: true

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Update package.json version
        run: |
          npm version ${{ inputs.version }} --no-git-tag-version
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add package.json
          git commit -m "chore(release): v${{ inputs.version }} [skip ci]"
          git push

      - name: Create tag and GitHub release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ inputs.version }}
          name: Release v${{ inputs.version }}
          body: ${{ inputs.release_notes }}
          generate_release_notes: true   # auto-generate from commit history
```

---

## 19. Security in CI/CD

### 19.1 Secret Management Best Practices

```yaml
# ✅ Good: use secrets context
- run: ./deploy.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}

# ❌ Bad: hardcoded secret in workflow
- run: API_KEY=mysecret ./deploy.sh

# ❌ Bad: printing secrets (GitHub masks common secrets but not all)
- run: echo "Key is ${{ secrets.API_KEY }}"

# ✅ Mask custom values in logs
- name: Set dynamic secret
  run: |
    TOKEN=$(generate_token.sh)
    echo "::add-mask::$TOKEN"     # mask this value in all future log output
    echo "token=$TOKEN" >> $GITHUB_OUTPUT
```

### 19.2 Principle of Least Privilege

```yaml
# Declare minimal permissions at workflow level
permissions:
  contents: read

# Override with more permissions only where needed
jobs:
  build:
    permissions:
      packages: write      # only this job writes packages
```

### 19.3 Dependency Scanning

```yaml
# Dependabot — automatically open PRs for vulnerable dependencies
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10
    groups:
      devDependencies:
        dependency-type: devDependencies

  - package-ecosystem: docker
    directory: /
    schedule:
      interval: weekly

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly

# npm audit in CI
- name: Check for vulnerabilities
  run: npm audit --audit-level=high
  # Fails if any HIGH or CRITICAL vulnerabilities found
```

### 19.4 OIDC for Cloud Authentication

Instead of storing long-lived cloud credentials as secrets, use OpenID Connect to get short-lived tokens:

```yaml
# No AWS keys stored in GitHub — uses OIDC token instead
permissions:
  id-token: write     # required for OIDC
  contents: read

jobs:
  deploy:
    steps:
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-role
          aws-region: us-east-1
          # No access key or secret key — GitHub gets a temporary token from AWS

      - run: aws s3 ls    # authenticated automatically
```

### 19.5 Preventing Supply Chain Attacks

```yaml
# ✅ Pin actions to a specific commit SHA (most secure)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# ✅ Pin to a version tag (less secure but practical)
- uses: actions/checkout@v4

# ❌ Avoid mutable refs
- uses: actions/checkout@main     # main could be changed by anyone

# ✅ Use dependabot to keep action versions updated
# .github/dependabot.yml includes github-actions ecosystem
```

### 19.6 Hardening Workflows

```yaml
# Restrict what third-party actions can access
permissions:
  contents: read          # most restrictive by default

# Prevent script injection via PR titles/body
- name: Safe use of PR title
  run: echo "PR title:" $TITLE      # ❌ vulnerable to injection if TITLE contains backticks
  env:
    TITLE: ${{ github.event.pull_request.title }}

- name: Safe use of PR title
  run: echo "PR title: $TITLE"      # ✅ passed as env var, not shell-interpolated
  env:
    TITLE: ${{ github.event.pull_request.title }}
```

---

## 20. Complete Real-World Pipeline Examples

### 20.1 Full NestJS + Docker + VPS Pipeline

```yaml
# .github/workflows/main.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  NODE_VERSION: '20'

jobs:
  # ── CI ──────────────────────────────────────────────────────────────────────

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci --prefer-offline
      - run: npm run lint
      - run: npm run format:check

  test:
    name: Test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: --health-cmd pg_isready --health-interval 10s --health-retries 5
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci --prefer-offline
      - run: npm run test:cov
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
          JWT_SECRET: test-secret
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/
          retention-days: 7

  build-image:
    name: Build & Push Image
    runs-on: ubuntu-latest
    needs: [lint, test]
    permissions:
      contents: read
      packages: write
    outputs:
      tag: ${{ steps.meta.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ── CD ──────────────────────────────────────────────────────────────────────

  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build-image
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://yourdomain.com
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        env:
          IMAGE_TAG: ${{ needs.build-image.outputs.tag }}
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          envs: IMAGE_TAG
          script: |
            set -e
            cd ~/app

            # Pull the specific image
            docker pull ghcr.io/${{ github.repository }}:$IMAGE_TAG

            # Zero-downtime rolling deploy
            docker compose pull
            docker compose up -d --no-deps --scale app=2 --no-recreate app
            sleep 20
            docker compose up -d --no-deps --scale app=1 --no-recreate app
            docker image prune -f

            echo "${{ github.sha }}" > .current-sha

      - name: Health check
        run: |
          for i in {1..10}; do
            STATUS=$(curl -sf -o /dev/null -w "%{http_code}" https://yourdomain.com/health)
            [ "$STATUS" = "200" ] && echo "✅ Healthy" && exit 0
            echo "Attempt $i: $STATUS"
            sleep 10
          done
          exit 1

      - name: Notify on failure
        if: failure()
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            # Auto-rollback on health check failure
            cd ~/app
            PREV_SHA=$(cat .current-sha 2>/dev/null || echo "")
            if [ -n "$PREV_SHA" ]; then
              echo "Rolling back to $PREV_SHA"
              docker compose up -d --no-deps app
            fi
```

### 20.2 Full Java / Spring Boot + MySQL + VPS Pipeline

```yaml
name: Java CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  JAVA_VERSION: '21'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpass
          MYSQL_DATABASE: testdb
        options: --health-cmd "mysqladmin ping" --health-interval 10s --health-retries 5
        ports: ['3306:3306']

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: temurin
          cache: maven

      - name: Build and test
        run: mvn -B verify --no-transfer-progress
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb?useSSL=false&allowPublicKeyRetrieval=true
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: testpass
          SPRING_JPA_HIBERNATE_DDL_AUTO: create-drop

      - name: Upload test reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: target/surefire-reports/

  build-image:
    name: Build & Push
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        id: push
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: Deploy
    needs: build-image
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/app
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

---

## 21. Troubleshooting and Debugging

### 21.1 Enable Debug Logging

```yaml
# Add these secrets to enable verbose logging:
# ACTIONS_RUNNER_DEBUG = true   → runner diagnostic info
# ACTIONS_STEP_DEBUG = true     → step debug output (echo commands)

# Or trigger from the API:
# curl -X POST .../workflows/ci.yml/dispatches \
#   -d '{"ref":"main","inputs":{}}'

# Debug in a specific step
- name: Debug info
  run: |
    echo "=== Context ==="
    echo "github.ref = ${{ github.ref }}"
    echo "github.sha = ${{ github.sha }}"
    echo "github.actor = ${{ github.actor }}"
    echo "=== Environment ==="
    env | sort
    echo "=== Files ==="
    ls -la
```

### 21.2 tmate — Interactive SSH Debugging

```yaml
# Drop into an interactive shell on the runner for debugging
- name: Setup tmate session (debug only — remove before merging)
  uses: mxschmitt/action-tmate@v3
  if: failure()          # only open if previous step failed
  timeout-minutes: 30    # auto-close after 30 minutes
```

### 21.3 Common Errors and Fixes

**"Resource not accessible by integration"**
```yaml
# Missing permission declaration
permissions:
  pull-requests: write   # add the required permission
```

**"Error: GITHUB_TOKEN Permissions"** when pushing to registry
```yaml
permissions:
  packages: write    # required for ghcr.io pushes
```

**"Process completed with exit code 1"** — generic failure
```yaml
# Add set -x to see every command being executed
- run: |
    set -x
    npm test
```

**Cache not being restored**
```yaml
# Check the cache key — hashFiles() returns empty string if no files match
- run: echo "Hash = ${{ hashFiles('**/package-lock.json') }}"
# If empty, the glob pattern is wrong
```

**Service container not ready**
```yaml
services:
  postgres:
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5    # increase this if DB is slow to start
# Add a wait step after checkout to give services time
- run: sleep 5
```

**"Input required and not supplied"**
```yaml
# workflow_call input marked required: true but not passed by caller
# Either make it optional or ensure the caller always passes it
```

**"Context access might be invalid"**
```yaml
# Accessing outputs from a job that hasn't run
needs: [job-a]
# job-b.outputs.value requires:
# 1. job-a declares outputs:
# 2. steps in job-a set the output with >> $GITHUB_OUTPUT
# 3. job-b references it as needs.job-a.outputs.value
```

### 21.4 Workflow Monitoring

```bash
# GitHub CLI — view workflow runs
gh run list                           # list recent runs
gh run list --workflow=ci.yml         # filter by workflow
gh run view 12345                     # view a specific run
gh run view 12345 --log               # view logs
gh run view 12345 --log-failed        # only show failed steps

# Re-run a failed workflow
gh run rerun 12345
gh run rerun 12345 --failed           # only re-run failed jobs

# Watch a run in progress
gh run watch 12345

# Cancel a run
gh run cancel 12345
```

### 21.5 Skipping CI

```bash
# Add to commit message to skip CI (useful for docs/config changes)
git commit -m "docs: update readme [skip ci]"
git commit -m "docs: update readme [ci skip]"
# GitHub also respects: [no ci], [skip actions]
```

---

*Last updated: 2026 — Built from real CI/CD pipeline experience across production deployments.*
