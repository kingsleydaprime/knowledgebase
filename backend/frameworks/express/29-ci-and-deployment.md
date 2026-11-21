---
id: e3e4447c-7148-48ce-adba-9c9d25ff9faf
---

# CI and Deployment

**Continuous integration (CI) means every change is automatically checked (type-checked, tested, built) before it can join the main code. Continuous deployment (CD) means every change that passes is automatically put on the real servers, the same careful way every time, with a quick way back if it goes wrong.** Together they turn "deploying" from a nervous evening of typed commands into something that happens several times a day without anyone holding their breath.

## Before you start
<!-- bite: aad9fc69-492f-46d3-863c-6f869d031bd4 -->

You should have the whole system running with Docker Compose from [[backend/frameworks/express/28-production-config-and-docker|lesson 28]].

You'll need the code on GitHub, and for the deployment part, a small Linux server (a VPS) with Docker installed and a domain name pointing at it. [[devops/04-vps/vps-setup|VPS Setup]] covers getting one ready. If you don't have one yet, do the CI half now; it's useful on its own.

After this lesson you will be able to:

1. Write a GitHub Actions pipeline that type-checks, tests (with real Postgres and Redis), and checks the API docs and contracts on every pull request.
2. Build and publish Docker images, tagged so every version can be found again.
3. Deploy to a server with HTTPS in front, run migrations safely, and check the new version is healthy.
4. Change the database without downtime, with expand and contract.
5. Roll back quickly, and keep dependencies up to date without drama.

## Where we stopped
<!-- bite: 4f7bdfa3-8639-4b48-8511-1b1ac57dc212 -->

Deploying Mama Put today would mean: run the tests on your laptop (if you remember), build images, copy them to the server somehow, SSH in, run the migration, restart the containers, and hope. Every step is a chance to forget something, and when it breaks at 9 p.m., nobody remembers exactly what was done.

And look at the promises earlier lessons left for this one:

1. Lesson 1: Node runs TypeScript **without checking the types**, so something must.
2. Lesson 11: "CI fails if the committed `openapi/v2.json` doesn't match the code."
3. Lesson 14: "a bot opens a pull request when an update is available."
4. Lesson 22: `.proto` changes checked for breaking changes.
5. Lesson 25: both services' tests on every change, the payoff of the monorepo.

## The kid version
<!-- bite: 454d4fbb-1cea-4cb9-ac05-077fd576641c -->

Before any new dish goes on Mama's menu, her sister tastes it. Every time, even if Mama has made it a hundred times. If it's too salty, it doesn't go on the menu, however sure Mama was.

When it passes, the new dish goes on the board. But Mama keeps yesterday's recipe card. If customers hate the new jollof, she can cook yesterday's tomorrow, without having to remember it.

The sister tasting is CI. Putting it on the board is deployment. Yesterday's recipe card is a rollback.

**Where the picture stops working.** Going back to yesterday's jollof is easy because nothing about the kitchen changed. In software, if the new version changed the *database*, going back to old code may not fit the new tables. So database changes need their own careful steps, which is half of this lesson.

## Terms used in CI and deployment
<!-- bite: 55b077b0-b44f-4548-9579-fe1612831dab -->

1. **Pipeline** (or **workflow**): This is the list of automatic steps that run on every change.
2. **Job** and **step**: A job is a group of steps that run on one machine; jobs can run in parallel or wait for each other.
3. **Runner**: This is the machine that runs a job. GitHub provides them.
4. **Artifact**: This is something a pipeline produces and keeps, like a Docker image.
5. **Container registry**: This is a store for Docker images, like GitHub Container Registry (`ghcr.io`).
6. **Image tag**: This is a name for one version of an image. We tag with the git commit id, so every image points to exactly one version of the code.
7. **Reverse proxy**: This is the server in front of the app that takes HTTPS connections from the internet and passes requests on. We'll use Caddy, which gets HTTPS certificates by itself.
8. **Rollback**: This is going back to the previous working version.
9. **Expand and contract**: This is a way of changing the database in steps, so the old and new versions of the code both work at every moment.

## Step 1: the CI pipeline
<!-- bite: 1895b3d5-8c6b-420f-80a8-c51d240edcfe -->

GitHub Actions reads workflows from `.github/workflows/`. If GitHub Actions is new to you, [[devops/05-ci-cd/03-github-actions-fundamentals|GitHub Actions Fundamentals]] explains the parts first.

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: ci
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-retries 10
      queue-redis:
        image: redis:7
        ports: ["6379:6379"]
      cache-redis:
        image: redis:7
        ports: ["6380:6379"]

    env:
      NODE_ENV: test

    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-node@v5
        with:
          node-version: 24
          cache: npm

      - run: npm ci

      - name: Type-check both services
        run: |
          npx tsc --noEmit -p api
          npx tsc --noEmit -p notifications

      - name: Fast tests
        run: |
          npm test -w api
          npm test -w notifications

      - name: Integration tests
        env:
          DATABASE_URL: postgres://postgres:ci@localhost:5432/mama_put_test
          QUEUE_REDIS_URL: redis://localhost:6379/1
          CACHE_REDIS_URL: redis://localhost:6380
        run: |
          psql postgres://postgres:ci@localhost:5432/postgres -c "CREATE DATABASE mama_put_test"
          npm run test:integration -w api

      - name: OpenAPI docs match the code
        run: |
          npm run openapi -w api
          git diff --exit-code -- api/openapi

      - name: Known vulnerabilities
        run: npm audit --omit=dev --audit-level=high
```

What each part is for:

1. **`on: pull_request` and `push` to `main`**: every pull request is checked before it's merged, and `main` is checked again after.
2. **`permissions: contents: read`**: this workflow may only *read* the repository. Give every workflow the least it needs; a compromised step can then do little.
3. **`concurrency` with `cancel-in-progress`**: push twice to a branch quickly, and the first run is cancelled. No point testing code that's already been replaced.
4. **`services`**: GitHub starts Postgres and both Redis servers as containers next to the job, on `localhost`, exactly as lesson 16's integration tests expect. The same tests, the same real databases, on every change.
5. **`npm ci`** installs exactly what's in the lockfile, so CI tests the same versions production will run.
6. **Type-checking.** Node runs our `.ts` files by *removing* the types, without checking them (lesson 1). A wrong type would sail through to production and fail at runtime. `tsc --noEmit` checks every file and writes nothing. This step is the reason running TypeScript directly is safe.
7. **Both services' tests.** A change to `contracts/events.ts` runs the API's tests *and* notifications' tests, so a change that breaks the other side fails here, not in production. That's the monorepo paying off.
8. **The OpenAPI check**, lesson 11's promise. The docs are generated from the code; if someone changed a schema and didn't regenerate and commit `openapi/*.json`, `git diff --exit-code` finds a difference and fails. Reviewers always see the real API change in the pull request.
9. **`npm audit`** fails on known high-severity holes in production dependencies.

Two more checks worth adding as the project grows:

1. **Breaking `.proto` changes** (lesson 22): `buf breaking` compares the `.proto` files against `main` and fails on removed fields, changed numbers or types. The `bufbuild/buf-action` GitHub Action runs it.
2. **A lint step** (ESLint), so style arguments happen once, in a config file, not in every review.

**Protect `main`.** In the repository's settings, add a rule: pull requests into `main` need this workflow to pass. Now nothing untested can reach `main`, whoever is in a hurry.

## Step 2: building and publishing images
<!-- bite: 158b097c-7cf7-438a-a2f4-6d538cf76289 -->

When `main` passes, build each service's image and push it to the registry. Add a second job to the same workflow:

```yaml
  images:
    needs: check
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    strategy:
      matrix:
        service: [api, notifications]
    steps:
      - uses: actions/checkout@v5
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: ${{ matrix.service }}/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.service }}
          cache-to: type=gha,mode=max,scope=${{ matrix.service }}
```

1. **`needs: check`**: images are only built from code that passed every check.
2. **`packages: write`**, only on this job: it can push images; the check job still can't.
3. **`matrix`**: the same steps run twice, once per service, in parallel.
4. **The tag is the commit id** (`github.sha`). Every image says exactly which code it holds. Never deploy `latest`: "latest" changes under you, and you can't roll back to "the previous latest".
5. **`cache-from` and `cache-to`**: Docker's layer cache is kept between runs, so lesson 28's careful ordering (dependencies before code) pays off in CI too.
6. **`GITHUB_TOKEN`** is created by GitHub for each run, valid only for that run. No long-lived password to store or leak.

## Step 3: the server
<!-- bite: 89b9827d-8e60-438f-ba4e-0bc88570ec31 -->

On the VPS, the system runs from the same `compose.yaml`, with a second file, `compose.prod.yaml`, that changes only what's different in production:

```yaml
services:
  migrate:
    image: ghcr.io/you/mama-put/api:${IMAGE_TAG:?}
    build: !reset null
  api:
    image: ghcr.io/you/mama-put/api:${IMAGE_TAG:?}
    build: !reset null
    ports: !reset []
    environment:
      TRUST_PROXY_HOPS: "1"
  worker:
    image: ghcr.io/you/mama-put/api:${IMAGE_TAG:?}
    build: !reset null
  notifications:
    image: ghcr.io/you/mama-put/notifications:${IMAGE_TAG:?}
    build: !reset null

  caddy:
    image: caddy:2
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./ops/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
    depends_on: [api]

volumes:
  caddy_data:
```

1. **`image: ...:${IMAGE_TAG}` and `build: !reset null`**: in production, don't build; pull the exact image CI built. `IMAGE_TAG` must be set, or Compose refuses.
2. **`ports: !reset []` on the API**: port 3000 isn't published at all any more. The only doors to the internet are Caddy's 80 and 443.
3. **`TRUST_PROXY_HOPS: 1`**: there's exactly one proxy in front now, so lesson 14's `trust proxy` is 1, and rate limits see real customer addresses.

`ops/Caddyfile`:

```text
api.mamaput.example {
	reverse_proxy api:3000 {
		health_uri /health/ready
		health_interval 5s
	}
	encode zstd gzip
}
```

That's all Caddy needs. It gets a free HTTPS certificate for `api.mamaput.example` by itself, renews it by itself, redirects HTTP to HTTPS, and sends requests to the API. It checks `/health/ready` every 5 seconds, which is the readiness check lesson 28 built, doing its job. (`encode` compresses responses; Caddy knows not to buffer the SSE stream from lesson 20.)

On the server, once:

1. Make a `deploy` user, and a folder `/srv/mama-put` with `compose.yaml`, `compose.prod.yaml`, `ops/`, and the production `.env` (written there by hand or from your secret manager, **never** from git).
2. Log Docker in to `ghcr.io` with a token that can only *read* packages.
3. Open only ports 22 (SSH), 80 and 443 in the firewall.

Paystack's webhook URL becomes `https://api.mamaput.example/webhooks/paystack`, with the **live** key in production's `.env` (lesson 28's config check makes sure it's not the test one).

## Step 4: deploying from CI
<!-- bite: 3821b157-d595-4183-85b4-72696e4924c1 -->

A third job deploys what the second built:

```yaml
  deploy:
    needs: images
    runs-on: ubuntu-latest
    environment: production
    concurrency: production
    steps:
      - name: Set up SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          echo "${{ secrets.DEPLOY_KNOWN_HOSTS }}" > ~/.ssh/known_hosts

      - name: Deploy
        run: ssh deploy@${{ vars.DEPLOY_HOST }} "cd /srv/mama-put && ./deploy.sh ${{ github.sha }}"
```

1. **`environment: production`**: GitHub environments can require a person's approval before the job runs, and hold their own secrets. The SSH key lives there, available only to this job, only after approval if you want it.
2. **`concurrency: production`**: two deploys never run at once.
3. **`known_hosts`**: the server's identity is checked, so the key is only ever sent to the real server.

The steps themselves live in a script on the server, `deploy.sh`, so you can run exactly the same thing by hand in an emergency:

```bash
#!/bin/bash
set -euo pipefail
NEW_TAG="$1"
COMPOSE="docker compose -f compose.yaml -f compose.prod.yaml"
OLD_TAG="$(cat .current-tag 2>/dev/null || true)"

export IMAGE_TAG="$NEW_TAG"
$COMPOSE pull migrate api worker notifications
$COMPOSE up -d --remove-orphans     # migrate runs first; api and worker wait for it to succeed

# Is the new version really serving?
for i in $(seq 1 30); do
  if curl -fsS https://api.mamaput.example/health/ready > /dev/null; then
    echo "$NEW_TAG" > .current-tag
    echo "deployed $NEW_TAG"
    exit 0
  fi
  sleep 2
done

echo "new version not ready after 60 s, rolling back to $OLD_TAG"
if [ -n "$OLD_TAG" ]; then
  export IMAGE_TAG="$OLD_TAG"
  $COMPOSE up -d api worker notifications
fi
exit 1
```

In words: pull the new images; start them (Compose runs `migrate` first, and lesson 28's `depends_on` means a failed migration stops the new version from starting at all); check the public health URL for a minute; if it's healthy, remember this tag; if not, put the previous tag back and fail the job, so you hear about it.

**An honest limit.** On one server, `up -d` replaces the API container, and for a few seconds while the new one starts, Caddy has nothing healthy to send requests to. Lesson 28's polite shutdown means no request is *dropped*, but some will wait or get an error in that window. For Mama Put at 3 p.m., that's acceptable. For true zero-downtime, run two copies of the API and replace them one at a time (a "rolling" deploy), which Caddy can balance between; or move to a platform that does this for you (most container platforms and Kubernetes do). The pipeline doesn't change: build, tag, migrate, roll out, check, roll back.

## Step 5: changing the database without breaking anything
<!-- bite: 925501e8-d67b-49ac-bbab-49c1fb01b481 -->

Look at the deploy again. For a short while, the **old** code is still running while the migration has already changed the database. And if we roll back, the **old** code runs against the **new** database. So every migration must work with both the version before it and the version after.

Most migrations already do: adding a table, adding a column with a default or that can be empty, adding an index. They're invisible to old code.

The dangerous ones rename, remove or change. Say Mama wants `dishes.name` to become `dishes.title`. Doing it in one migration (`ALTER TABLE dishes RENAME COLUMN name TO title`) breaks the old code the moment the migration runs, and breaks a rollback completely.

**Expand and contract** does it in three deploys:

1. **Expand.** A migration adds `title`, copies `name` into it, and the new code writes **both** columns and reads `title`. Old code still works: it only knows `name`, which is still there and still kept up to date.
2. **Move over.** Once every running copy is the new code (and you're sure you won't roll back past it), the next version stops writing `name`.
3. **Contract.** A later migration drops `name`. Nothing reads or writes it by then.

It's lesson 10's rule ("add, don't change; then retire the old thing") applied to the database. It's slower, and it means you never have to choose between "keep the site up" and "change the schema".

**Rolling back data.** Code is easy to roll back: run the previous image. Data isn't: if a migration deleted a column, rolling back the code doesn't bring the column back. That's why the rule is **roll forward**: migrations are written so they never need undoing (expand and contract), and if something's wrong, the fix is a new migration, not a "down" migration run in a panic. And take a backup before any migration that removes anything (lesson 28's `pg_dump`, scheduled nightly at least, and tested by restoring).

## Step 6: rolling back
<!-- bite: c96b453a-2b61-48d4-93a9-4ae9fdf5a4f4 -->

When the new version is live and something's wrong (the health check passed, but checkout is failing):

```bash
ssh deploy@api.mamaput.example
cd /srv/mama-put
cat .current-tag              # the bad one
./deploy.sh <previous-sha>    # the good one
```

Because every image is tagged with its commit id and kept in the registry, "the previous version" is one command away, and it's the same command as a normal deploy. Practise it once on a quiet day, so on a bad day it's boring. (Keep a list of recent good tags: `git log --oneline main` shows them, and the registry has every one.)

Two habits make rollbacks rare and small:

1. **Deploy small changes, often.** A deploy with one change has one thing that can be wrong. A deploy with a month of changes has a hundred.
2. **Feature flags** for risky features: ship the code switched off, then switch it on in config (lesson 28) for staff first, then everyone. Switching it off again is faster than any deploy.

Watch lesson 27's graphs for a few minutes after every deploy: error rate, p95, and `payments_settled_total`. The alerts are there for the things you miss.

## Step 7: keeping dependencies fresh
<!-- bite: 50fe2db6-ea1f-49a8-9f81-c3b2252b1001 -->

Lesson 14's promise. `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule: { interval: weekly }
    groups:
      minor-and-patch:
        update-types: ["minor", "patch"]

  - package-ecosystem: docker
    directories: ["/api", "/notifications"]
    schedule: { interval: weekly }

  - package-ecosystem: github-actions
    directory: "/"
    schedule: { interval: weekly }
```

Every week, Dependabot opens pull requests for newer versions: npm packages (small updates grouped into one pull request, so you're not buried), the Node base image in both Dockerfiles, and the Actions in the workflow. Each pull request runs the full CI pipeline, so you can see whether the update breaks anything before you merge it. Security fixes come straight away, not weekly.

A dependency kept up to date a little every week is easy. One left for two years is a project of its own.

## Step 8: keeping the pipeline itself safe
<!-- bite: 6dee6d24-3b1b-483c-9a29-107546ccb78c -->

The pipeline can deploy to production, so it's worth protecting like production ([[devops/05-ci-cd/10-pipeline-security|Pipeline Security]] goes deeper):

1. **Least permissions per job**, as above: read-only by default, `packages: write` only where images are pushed.
2. **Secrets only where needed**: the SSH key in the `production` environment, not in the whole repository.
3. **Pull requests from forks get no secrets.** GitHub's `pull_request` trigger already does this. Never change it to `pull_request_target` for a workflow that runs the pull request's code: that gives strangers' code your secrets.
4. **Pin third-party Actions.** A tag like `@v6` can be moved by its owner; a full commit hash can't. Dependabot will keep hashes up to date for you.
5. **Never print secrets.** GitHub hides known secrets in logs, but `echo $SECRET | base64` slips past. Don't echo them at all.

## The TypeScript in this lesson
<!-- bite: b32c3f8b-a926-4248-8f5e-22ef209fb2bc -->

No new TypeScript this time, and that's worth saying out loud: the type-checking step is how TypeScript stays useful when Node runs it without checking.

1. **`tsc --noEmit -p api`**: runs the TypeScript compiler with `api/tsconfig.json`, checking every file and writing nothing. It's the only place types are actually checked, so it must be in CI and must pass.
2. **Why it catches what tests miss**: a test only checks the paths it runs. `tsc` checks every line, including the error branch nobody tested. Lesson 7's `Record<ErrorKind, number>`, lesson 13's policy table and lesson 22's gRPC status map all rely on `tsc` refusing to pass when a kind or action is missing.
3. **Your editor runs the same checks** as you type, using the same `tsconfig.json`. CI is the version nobody can skip.

## Your project so far
<!-- bite: c6427e21-6e81-41d0-8696-e2f2bab6c3a3 -->

```text
mama-put/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                   ← NEW: check (types, tests on real Postgres/Redis, OpenAPI, audit)
│   │                                  → images (both services, tagged by commit) → deploy (approval, SSH)
│   └── dependabot.yml               ← NEW: npm, Docker base images, Actions, weekly
├── compose.yaml                     ← from lesson 28: builds locally
├── compose.prod.yaml                ← NEW: pulls ${IMAGE_TAG} images, no published API port, Caddy on 80/443
├── deploy.sh                        ← NEW: pull, up (migrate first), health check, roll back on failure
├── ops/
│   ├── Caddyfile                    ← NEW: HTTPS, reverse proxy with readiness checks, compression
│   ├── postgres-init/ · prometheus.yml · alerts.yml
├── .env.example · .dockerignore · package.json · package-lock.json
├── proto/ · contracts/
├── api/                             ← Dockerfile, src/, migrations/, openapi/, tests: 29 lessons of Mama Put
└── notifications/                   ← Dockerfile, src/, migrations/, tests
```

## Common mistakes
<!-- bite: e814e2c3-2d7a-4d6a-9a41-d25ad15190ae -->

1. **No type-check in CI.** Node runs wrongly typed code happily, until it fails in production.
2. **Tests against fakes only in CI.** The races and SQL bugs only show on real Postgres. Run the integration tests too.
3. **Deploying `latest`.** You can't tell what's running, or go back to what was.
4. **Migrations that break the running version.** Renames and drops in one step. Expand, then contract.
5. **Counting on "down" migrations.** Roll forward; take backups; test restores.
6. **Deploys nobody can run by hand.** Put the steps in a script on the server; CI just calls it.
7. **No health check after deploying.** "It started" isn't "it works". Check readiness from outside, and roll back automatically if it fails.
8. **Secrets everywhere.** Whole-repository secrets, `echo`ed in logs, available to pull requests from forks.
9. **Updating dependencies once a year.** Small and weekly, through CI, or never at all, and then all at once in a crisis.
10. **Never practising a rollback.** The first time shouldn't be at 9 p.m. on a Friday.

## Check your understanding
<!-- bite: 9600406b-cb56-4863-a905-bb894d0f9427 -->

1. Why does CI need `tsc --noEmit` when the tests already pass?
2. What does `git diff --exit-code -- api/openapi` catch?
3. Why are images tagged with the commit id instead of `latest`?
4. During a deploy, which versions of the code run against the new database schema, and what does that mean for migrations?
5. How would you rename `dishes.name` to `dishes.title` without breaking anything?
6. The new version passes its health check, but checkout starts failing. What do you do, and why is it quick?

<details>
<summary>Answers, after your attempt</summary>

1. Node removes types without checking them, and tests only check the paths they run. `tsc` checks every line, so type errors in untested branches, or a missing case in a `Record<ErrorKind, ...>` map, fail CI instead of failing in production.
2. The API docs being out of date. The step regenerates `openapi/*.json` from the code; if the committed files differ, someone changed the API without updating its docs, and the pull request fails until they do.
3. So every image points to exactly one version of the code, you always know what's running, and "go back to the previous version" means "deploy the previous tag", which still exists. `latest` changes meaning every build.
4. Both the old version (still running until it's replaced, or brought back by a rollback) and the new one. So every migration must work for both: add things freely; rename, change or remove only in steps.
5. Expand: add `title`, copy `name` into it, and deploy code that writes both and reads `title`. Once nothing old is running, stop writing `name`. Contract: a later migration drops `name`.
6. Roll back: run `deploy.sh` with the previous commit's tag. It's quick because the old image is still in the registry, tagged by commit, and the deploy script is the same one used every day. Then find and fix the bug with a new change, through CI as usual.

</details>

## Practice
<!-- bite: f7fbcc9a-0d2a-4d65-bdbf-d97f32b513fe -->

1. Push the repository to GitHub, add `ci.yml`, and open a pull request that breaks a type on purpose. Watch it fail. Then one that changes a schema without regenerating the docs. Watch that fail too.
2. Protect `main` so pull requests need CI to pass.
3. Add the `images` job and check both images appear in your GitHub packages, tagged with the commit.
4. If you have a server: set up Caddy, `compose.prod.yaml` and `deploy.sh`, add the `deploy` job with an approval, and deploy. Then deploy a version whose `/health/ready` always fails, and watch it roll back by itself.
5. Do a full expand-and-contract rename of a column across three pull requests.
6. Add `dependabot.yml`, and merge the first update it opens after CI passes.

**Done when** every pull request is type-checked and tested against real Postgres and Redis before it can be merged; every merge to `main` produces two images tagged with its commit; a deploy runs migrations first, checks health from outside, and rolls itself back if the check fails; you've rolled back by hand once, on purpose; and `https://api.mamaput.example/v2/menu` answers over HTTPS with nothing else on the server reachable from the internet except SSH.

## The end of the road, and the start of the next
<!-- bite: 26c9a1c6-7131-4d5a-9ca9-429f7a6816bb -->

Look at where Mama Put API started, in lesson 1: one file, one route, "Mama Put is open!".

It's now a production system. A REST API with one response shape, validation, problem details, pagination, filtering, search, sorting, field selection, two versions side by side, and OpenAPI docs. Accounts with hashed passwords, rotating refresh tokens and a written permission policy. Security headers, CORS, rate limits and safe uploads. Idempotent orders that can't happen twice, and a last plate that goes to exactly one customer. Payments through Paystack, verified webhooks in and signed webhooks out. Background jobs, a cache that stays honest, a live kitchen screen. GraphQL for the phone app, gRPC between services, and an MCP server that lets AI assistants order safely for real people. A second service listening to events through an outbox, calling back with deadlines, retries, circuit breakers and its own identity. Logs, metrics and traces across all of it. Containers, health checks, polite shutdowns, and a pipeline that tests, builds, deploys and rolls back by itself.

None of the ideas in those 29 lessons belong to Express. Validation at the door, rules in services, one error shape, conditional updates for races, idempotency keys, the outbox, deadlines, readiness: they're the same in every framework and every language. Express was just the place we built them first. The other framework subjects build the **same** Mama Put API, in their own style, so you can see which parts are the framework and which parts are simply good backend engineering.

## Related
<!-- bite: 62494c5a-0304-4764-a5da-c0a6d90c3119 -->

- [[backend/frameworks/express/index|Express]] — all 29 lessons
- [[devops/05-ci-cd/index|CI/CD]] — pipelines in much more depth
- [[devops/04-vps/vps-setup|VPS Setup]] — preparing the server
- [[backend/frameworks/index|All frameworks]] — the same system, built in other frameworks

## About this lesson
<!-- bite: 72a43c3d-b59b-43f9-b7a5-524559d611da -->

**Level:** Advanced. Lesson 29 of [[backend/frameworks/express/index|Express]], and the last. Covers a GitHub Actions pipeline with least permissions and cancelled duplicate runs, real Postgres and Redis service containers for integration tests, type-checking with `tsc --noEmit` because Node strips types without checking them, testing both services on every change, checking generated OpenAPI docs and known vulnerabilities, building and pushing both images to GitHub Container Registry tagged by commit with layer caching, a production Compose override that pulls exact images and puts Caddy in front for automatic HTTPS and readiness checks, deploying through a GitHub environment with approval and a script on the server, migrations first and a public health check with automatic rollback, the limits of single-server deploys, expand-and-contract migrations, rolling forward, backups, rolling back by tag, small deploys and feature flags, Dependabot for npm, base images and Actions, and keeping the pipeline itself secure.
