# Securing the Pipeline

**[Intermediate → Advanced]** — Your CI system holds production credentials and runs arbitrary third-party code. Secret handling, least privilege, dependency scanning, OIDC instead of long-lived keys, and supply-chain hardening.

## Secret Management Best Practices

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

## Principle of Least Privilege

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

## Dependency Scanning

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

## OIDC for Cloud Authentication

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

## Preventing Supply Chain Attacks

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

## Hardening Workflows

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

## Related
- [[devops/09-secret-management/README|Secret Management]] — where secrets should live
- [[cybersecurity/README|Cybersecurity]] — supply-chain attacks in their wider context
- [[devops/06-ci-cd/05-contexts-secrets-and-environments|Contexts and Secrets]] — the mechanics being hardened here
- [[devops/06-ci-cd/README|CI/CD module map]]
