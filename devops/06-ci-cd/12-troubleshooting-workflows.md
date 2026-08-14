# Troubleshooting Workflows

**[Reference]** — Debug logging, interactive SSH into a runner with tmate, the errors you will actually hit and their fixes, and how to skip CI deliberately.

## Enable Debug Logging

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

## tmate — Interactive SSH Debugging

```yaml
# Drop into an interactive shell on the runner for debugging
- name: Setup tmate session (debug only — remove before merging)
  uses: mxschmitt/action-tmate@v3
  if: failure()          # only open if previous step failed
  timeout-minutes: 30    # auto-close after 30 minutes
```

## Common Errors and Fixes

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

## Workflow Monitoring

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

## Skipping CI

```bash
# Add to commit message to skip CI (useful for docs/config changes)
git commit -m "docs: update readme [skip ci]"
git commit -m "docs: update readme [ci skip]"
# GitHub also respects: [no ci], [skip actions]
```

---

## Related
- [[devops/06-ci-cd/03-github-actions-fundamentals|Fundamentals]] — knowing the execution model is half of debugging it
- [[devops/06-ci-cd/05-contexts-secrets-and-environments|Contexts and Secrets]] — the source of most "why is this empty" bugs
- [[devops/06-ci-cd/README|CI/CD module map]]
