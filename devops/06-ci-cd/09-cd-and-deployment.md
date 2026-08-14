# CD, Deployment Strategies and Releases

**[Intermediate → Advanced]** — The deploy half: pipeline structure and rollback, the four rollout strategies in depth (recreate, rolling, blue-green, canary) with the tradeoffs that pick between them, and cutting releases automatically from CI.

## CD Pipeline — Deployment

### CD Pipeline Structure

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

### Rollback Workflow

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

## Deployment Strategies

### Recreate (Simple)

Stop the old version, start the new one. Causes downtime. Only acceptable for non-production or low-traffic services.

```yaml
script: |
  cd ~/app
  docker compose down
  docker compose pull
  docker compose up -d
```

**Use when:** Development/staging environments, internal tools, services where brief downtime is acceptable.

### Rolling Deployment

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

### Blue-Green Deployment

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

### Canary Deployment

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

### Choosing a Strategy

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

## Releasing from CI

### Automated Release Workflow

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

### Manual Version Tagging Workflow

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

## Related
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — the build this deploys
- [[devops/05-orchestration/README|Orchestration]] — rolling and canary rollouts as Kubernetes primitives
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — the pull-based alternative to deploying from CI
- [[git/11-tags-and-versioning|Tags and Versioning]] — the SemVer contract these releases follow
- [[devops/10-observability/README|Observability]] — what tells you a canary is failing
- [[devops/06-ci-cd/README|CI/CD module map]]
