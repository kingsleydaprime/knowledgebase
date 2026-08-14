# Contexts, Secrets and Environments

**[Intermediate]** — The context objects available inside an expression (`github`, `env`, `secrets`, `steps`, `needs`, `runner`), the expression functions, and how secrets, variables and environments are scoped.

## Contexts and Expressions

### What Contexts Are

Contexts are objects containing information about the workflow run, available as `${{ context.property }}`.

### github Context

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

### env Context

```yaml
${{ env.MY_VARIABLE }}          # access environment variables set with env:
```

### secrets Context

```yaml
${{ secrets.MY_SECRET }}         # access repository/org secrets
${{ secrets.GITHUB_TOKEN }}      # automatic token provided by GitHub
```

### steps Context

```yaml
${{ steps.step_id.outputs.my_output }}   # step output
${{ steps.step_id.outcome }}             # success, failure, cancelled, skipped
${{ steps.step_id.conclusion }}          # final conclusion after continue-on-error
```

### needs Context

```yaml
${{ needs.job_id.outputs.my_output }}    # output from a required job
${{ needs.job_id.result }}               # success, failure, cancelled, skipped
```

### runner Context

```yaml
${{ runner.os }}                 # Linux, Windows, macOS
${{ runner.arch }}               # X64, ARM64
${{ runner.temp }}               # temp directory path
${{ runner.tool_cache }}         # tool cache path
```

### Expression Functions

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

## Secrets, Variables, and Environments

### Secrets

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

### Variables (Non-Secret Configuration)

Variables are like secrets but not encrypted — for non-sensitive configuration values visible in logs.

```yaml
# Set at: Settings → Secrets and variables → Actions → Variables
# Access with: vars context

steps:
  - run: echo "Deploying to ${{ vars.DEPLOY_HOST }}"
  - run: echo "App version prefix: ${{ vars.VERSION_PREFIX }}"
```

### Environments

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

### Secret Hierarchy and Scoping

```
Organisation secrets → available to all repos in the org
    ↓
Repository secrets → available to all workflows in the repo
    ↓
Environment secrets → only available in jobs targeting that environment
```

If the same secret name exists at multiple levels, the most specific level wins.

---

## Related
- [[devops/09-secret-management/README|Secret Management]] — the broader problem this is one instance of
- [[devops/06-ci-cd/10-pipeline-security|Securing the Pipeline]] — why least privilege on these tokens matters
- [[devops/06-ci-cd/04-triggers-jobs-and-runners|Triggers, Jobs and Runners]] — where these contexts get evaluated
- [[devops/06-ci-cd/README|CI/CD module map]]
