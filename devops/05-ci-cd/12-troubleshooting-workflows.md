---
id: 21a1b389-f859-44b8-844c-6ce70f8b8fbe
---

# Troubleshooting Workflows

Troubleshooting a workflow is finding out why a GitHub Actions run failed and fixing it. This lesson shows how to get more detailed logs, how to log into a runner while it is running, and the errors you will most often hit with their fixes. It also shows how to skip CI on purpose.

## Enable Debug Logging
<!-- bite: 383372be-4e6a-405c-a8ac-499579327fbf -->

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
<!-- bite: f2cd5309-5b55-4fa0-8f4f-2983d6f5dfcb -->

```yaml
# Drop into an interactive shell on the runner for debugging
- name: Setup tmate session (debug only — remove before merging)
  uses: mxschmitt/action-tmate@v3
  if: failure()          # only open if previous step failed
  timeout-minutes: 30    # auto-close after 30 minutes
```

## Common Errors and Fixes
<!-- bite: 9ea7a18e-f03b-4f79-9db3-eade8c08157e -->

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
<!-- bite: 0ca4d1f6-51d0-4b5a-b33d-06a96179a9d2 -->

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
<!-- bite: 975bd978-ac57-49bf-a6e2-43ebbf77c58c -->

```bash
# Add to commit message to skip CI (useful for docs/config changes)
git commit -m "docs: update readme [skip ci]"
git commit -m "docs: update readme [ci skip]"
# GitHub also respects: [no ci], [skip actions]
```

---

## Related
<!-- bite: b5ef23a1-65b8-4c00-a374-810e7967d747 -->
- [[devops/05-ci-cd/03-github-actions-fundamentals|Fundamentals]] — knowing the execution model is half of debugging it
- [[devops/05-ci-cd/05-contexts-secrets-and-environments|Contexts and Secrets]] — the source of most "why is this empty" bugs
- [[devops/05-ci-cd/index|CI/CD module map]]

## About this lesson
<!-- bite: 3dee5f89-9361-411e-9bcd-752c133b32e9 -->

**Level:** Reference. **Covers:** Debug logging, interactive SSH into a runner with tmate, the errors you will actually hit and their fixes, and how to skip CI deliberately.
