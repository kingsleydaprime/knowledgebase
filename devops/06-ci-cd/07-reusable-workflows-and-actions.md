# Reusable Workflows and Composite Actions

**[Intermediate → Advanced]** — Two ways to stop copy-pasting YAML across repos: called workflows (a whole job, invoked with inputs and secrets) and composite actions (a bundle of steps).

## Why Reusability Matters

Without reusable workflows, teams copy-paste the same CI logic across dozens of repositories. A change to the linting step means updating 20 files. Reusable workflows solve this — define once, call everywhere.

## Reusable Workflows — Called Workflows

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

## Composite Actions

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

## Related
- [[devops/06-ci-cd/04-triggers-jobs-and-runners|Triggers, Jobs and Runners]] — `uses:` at step level vs job level
- [[devops/06-ci-cd/05-contexts-secrets-and-environments|Contexts and Secrets]] — passing secrets across the boundary
- [[devops/06-ci-cd/README|CI/CD module map]]
