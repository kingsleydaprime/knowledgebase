# Triggers, Jobs and Runners

**[Intermediate]** — What starts a workflow (`on:` in full), how jobs and steps are structured, `run` vs `uses`, step outputs, job dependencies and fan-out/fan-in — and the machines all of it executes on.

## Triggers — on:

### Push and Pull Request

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

### Manual Triggers

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

### Scheduled Triggers

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

### Other Triggers

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

### Filtering Events

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

## Jobs and Steps

### Job Structure

```yaml
jobs:
  test:                              # Job ID (used for references)
    name: Run Tests                  # Display name in UI
    runs-on: ubuntu-latest           # Runner — see "Runners" below
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

### Steps — run vs uses

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

### Step Outputs

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

### Job Dependencies and Fan-Out/Fan-In

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

### Expressions and Conditions

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

## Runners

### GitHub-Hosted Runners

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

### Self-Hosted Runners

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

### Runner Groups (GitHub Enterprise / Organizations)

```yaml
# Target a specific runner group
jobs:
  deploy:
    runs-on:
      group: production-runners
      labels: [linux, x64]
```

### Docker Container Jobs

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

## Related
- [[devops/06-ci-cd/03-github-actions-fundamentals|Fundamentals]] — the YAML skeleton these keys sit in
- [[devops/06-ci-cd/05-contexts-secrets-and-environments|Contexts and Secrets]] — the expressions used in `if:` conditions here
- [[devops/02-docker/README|Docker]] — container jobs and service containers run on the same primitives
- [[devops/06-ci-cd/README|CI/CD module map]]
