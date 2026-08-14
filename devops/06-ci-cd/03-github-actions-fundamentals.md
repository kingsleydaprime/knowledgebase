# GitHub Actions — Fundamentals

**[Intermediate]** — The object model (workflow → job → step → action), where the files live, how a run actually executes, and the complete top-level YAML syntax including concurrency and permissions.

## GitHub Actions — How It Works

### Core Concepts

**Workflow** — A YAML file in `.github/workflows/`. Defines what to run and when. A repository can have multiple workflows.

**Event (Trigger)** — What causes a workflow to run: a push, a pull request, a schedule, a manual trigger, etc.

**Job** — A set of steps that run on a single runner. Jobs in a workflow run in parallel by default. You can make them sequential with `needs:`.

**Step** — A single task within a job: run a shell command, or use a pre-built action.

**Action** — A reusable unit of work. Can be from the GitHub Marketplace, a public repository, or your own code.

**Runner** — The machine that executes a job. GitHub provides hosted runners (Ubuntu, Windows, macOS) or you can host your own.

**Artifact** — A file or set of files produced by a workflow and uploaded for download or use by other jobs.

### File Location and Structure

```
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml           # CI pipeline — runs on every PR
        ├── deploy.yml       # CD pipeline — runs on merge to main
        ├── release.yml      # Release pipeline — runs on tag push
        └── scheduled.yml    # Scheduled tasks
```

### The Execution Flow

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

## Workflow YAML — Complete Syntax Reference

### Top-Level Structure

```yaml
name: CI Pipeline          # Display name in GitHub UI (optional but helpful)

on:                        # Trigger(s) — see 04-triggers-jobs-and-runners
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

jobs:                      # The actual work — see 04-triggers-jobs-and-runners
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Hello"
```

### Concurrency Control

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

### Permissions

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

## Related
- [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — this same model shown in this vault's own deploy pipeline
- [[devops/06-ci-cd/04-triggers-jobs-and-runners|Triggers, Jobs and Runners]] — the `on:` and `jobs:` keys in full
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD Concepts]] — the vendor-neutral model underneath
- [[devops/06-ci-cd/README|CI/CD module map]]
