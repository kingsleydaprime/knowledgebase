---
id: 8e5b9014-f436-4015-952d-9c36a9c1f840
---

# CI and Deployment

**Continuous integration (CI) means every change is checked automatically, by building it and running every test, before it can join the main code; continuous deployment means a change that passes is built into images and put on the server by the same pipeline, safely, with no one typing commands on the server.**

## Before you start
<!-- bite: c9038d01-f078-488e-98ac-af0c23804402 -->

You should have finished [[backend/frameworks/axum/40-docker|lesson 40]]: the whole system runs with `docker compose up`. You'll need a GitHub repository for the project, and a Linux server you can reach over SSH, with Docker installed.

After this lesson you will be able to:

1. Write a GitHub Actions pipeline that checks formatting, Clippy, the query cache and every test, against real Postgres and NATS.
2. Build and publish one image per program, with layer caching.
3. Deploy by commit, with an SSH key that can do one thing only.
4. Roll out with no downtime, and roll back.
5. Change the database without breaking the copies still running the old code.

## Where we stopped
<!-- bite: 15f6d56e-d7e3-4395-a37f-7e742b3ea486 -->

Everything works on the laptop, when the right person remembers the right commands in the right order. A forgotten `cargo sqlx prepare`, a test nobody ran, an image built from uncommitted changes: each one is a broken deploy. The pipeline makes the right order the only order.

## Terms used in this lesson
<!-- bite: 459691ed-ca1f-4f4c-a777-df1c9283bf6d -->

1. **Pipeline**: This is the list of jobs that run on every push: check, test, build, deploy.
2. **Job**: This is one part of a pipeline, run on a fresh machine (a **runner**). Jobs can depend on each other.
3. **Artifact**: This is something a job produces for later: here, an image in a registry, tagged with the commit.
4. **Rolling deploy**: This is starting the new copies, waiting until they're healthy, and only then stopping the old ones, so something is always answering.
5. **Expand and contract**: This is changing a database in two steps (add the new, then later remove the old), so old and new code can run at the same time.

## Step 1: the pipeline
<!-- bite: 006065e1-9fc2-43ce-be6d-34f10111d8c7 -->

`.github/workflows/ci.yml` has four jobs:

```text
check ─┐
       ├─► images (api, worker, notifications) ─► deploy
test ──┘
```

`check` and `test` run on every push and pull request; `images` and `deploy` only on `main`, after both pass.

### check

```yaml
  check:
    runs-on: ubuntu-latest
    env:
      SQLX_OFFLINE: "true"
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { components: "clippy, rustfmt" }
      - uses: Swatinem/rust-cache@v2
      - run: cargo fmt --all --check
      - run: cargo clippy --workspace --all-targets -- -D warnings
      - name: The query cache matches the queries
        run: cargo install sqlx-cli --no-default-features --features postgres,sqlx-toml --locked && cargo sqlx prepare --workspace --check
```

1. **`Swatinem/rust-cache`** keeps `target/` and Cargo's downloads between runs, keyed by `Cargo.lock`. Without it, every run compiles every crate from nothing.
2. **`cargo fmt --check`** fails if any file isn't formatted, so formatting is never discussed in review.
3. **Clippy with `-D warnings`**: a warning fails the build. Clippy found real things in lessons 23 to 37 (a closure that could be a function, a lock held across an await in a test).
4. **`cargo sqlx prepare --workspace --check`**: fails if `.sqlx` doesn't match the queries, the mistake from lesson 40 that would break the image build. This `sqlx` is built with `sqlx-toml`, so notifications' config file is understood.

### test

```yaml
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_USER: mama, POSTGRES_PASSWORD: ci, POSTGRES_DB: mamaput }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    env:
      DATABASE_URL: postgres://mama:ci@localhost:5432/mamaput
      NOTIFICATIONS_DATABASE_URL: postgres://notifications:ci@localhost:5432/mamaput_notifications
      NATS_URL: nats://localhost:4222
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      # Service containers can't take arguments, and NATS needs -js: start it by hand.
      - run: docker run -d -p 4222:4222 nats:2-alpine -js
      - name: The notifications database and user
        run: |
          PGPASSWORD=ci psql -h localhost -U mama -d mamaput -c "CREATE USER notifications CREATEDB PASSWORD 'ci'" \
            -c "CREATE DATABASE mamaput_notifications OWNER notifications"
      - run: cargo install sqlx-cli --no-default-features --features postgres --locked
      - run: sqlx migrate run && (cd notifications && DATABASE_URL=$NOTIFICATIONS_DATABASE_URL sqlx migrate run)
      - run: cargo test --workspace
```

1. **Service containers**: GitHub starts Postgres and Redis beside the job, reachable on `localhost`.
2. **NATS by hand.** Service containers can't be given arguments, and NATS needs `-js`, so it's a plain `docker run`.
3. **Notifications' database and user**, made the way lesson 40's init script makes them.
4. **Migrations, then `cargo test --workspace`**: the same tests as the laptop, against real Postgres and NATS. The NATS tests that skip without `NATS_URL` (microservice part 2) run here.

## Step 2: images, by commit
<!-- bite: 0ad656e6-237f-4770-8064-f9fc76a5161d -->

```yaml
  images:
    needs: [check, test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    strategy:
      matrix: { target: [api, worker, notifications] }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - uses: docker/build-push-action@v6
        with:
          target: ${{ matrix.target }}
          push: true
          tags: ghcr.io/${{ github.repository }}/${{ matrix.target }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.target }}
          cache-to: type=gha,mode=max,scope=${{ matrix.target }}
```

1. **A matrix**: the same job three times, once per `--target`, in parallel.
2. **Tagged with the commit** (`github.sha`), never only `latest`. Then "what's running?" has an exact answer, and going back means naming an older commit.
3. **`cache-from` / `cache-to: type=gha`** keeps Docker's layers in GitHub's cache, so cargo-chef's dependency layer (lesson 40) is built once and reused until `Cargo.lock` changes.
4. **The GitHub registry** (`ghcr.io`), with the job's own token, which may only write packages.

## Step 3: deploying, with a key that can do one thing
<!-- bite: c8ec92f4-517d-4b92-b884-e34b4a71fbdf -->

```yaml
  deploy:
    needs: [images]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy this commit
        run: |
          mkdir -p ~/.ssh && echo "${{ secrets.DEPLOY_KEY }}" > ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519
          echo "${{ secrets.DEPLOY_HOST_KEY }}" >> ~/.ssh/known_hosts
          ssh deploy@${{ secrets.DEPLOY_HOST }} "${{ github.sha }}"
```

The pipeline holds an SSH key for the server. If that key could run any command, anyone who could change the workflow could do anything on the server. So on the server, the key's line in `~/.ssh/authorized_keys` names the one thing it may run:

```text
command="/srv/mama-put/deploy/deploy.sh",no-pty,no-port-forwarding,no-agent-forwarding ssh-ed25519 AAAA… ci-deploy
```

Whatever the pipeline asks for, SSH runs `deploy.sh`, and the commit it asked for arrives in `SSH_ORIGINAL_COMMAND`. `deploy/deploy.sh`:

```bash
#!/usr/bin/env bash
# Runs on the server, as the `deploy` user. Its SSH key may run only this script (command= in
# authorized_keys), and the commit to deploy arrives as SSH_ORIGINAL_COMMAND.
set -euo pipefail
sha="${SSH_ORIGINAL_COMMAND:?which commit?}"
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || { echo "not a commit: $sha" >&2; exit 1; }
cd /srv/mama-put
export TAG="$sha"
docker compose pull api worker notifications
# New API copies first, beside the old ones; only when they're healthy do the old ones go.
docker compose up -d --no-deps --scale api=2 --no-recreate --wait api
docker compose up -d --no-deps --wait api worker notifications
echo "$sha" > deployed-commit
```

1. **The commit is checked**: exactly 40 hex characters, or nothing happens. It goes into `TAG`, which `compose.yaml`'s `image:` lines use.
2. **`docker compose pull`** fetches the three images CI built. Nothing is built on the server.
3. **The API rolls**: `--scale api=2 --no-recreate --wait` starts a new copy beside the old one and waits until it's healthy (lesson 39's `healthcheck`); then the second `up` replaces the rest. Caddy only sends traffic to copies whose `/readyz` says yes, and the old copy drains before stopping. Something is answering the whole time.
4. **`deployed-commit`** records what's running.
5. **`environment: production`** in the workflow lets GitHub require a person's approval before this job runs, if you want one.

**Rolling back** is deploying an older commit: run the `deploy` job again for it, or on the server `ssh deploy@server <older-sha>` with the same key. The images are still in the registry, tagged by commit.

## Step 4: changing the database safely
<!-- bite: 9769d1cc-6bf1-4d92-8545-36937dd5d58e -->

During a rolling deploy, old and new copies of the API run **at the same time**, against one database. So a migration must work for both. The rule is **expand, then contract**:

1. **Expand**: add the new thing, and keep the old. Add a column as nullable; write to both old and new; read the new if it's there. Deploy.
2. **Move the data**, with a job (lesson 18), in batches.
3. **Contract**: once no running code reads the old thing, remove it, in a later deploy.

Renaming `users.name` to `users.full_name` is three deploys, not one. Never `DROP` or `RENAME` something the previous release still reads. Microservice part 2's `payments.receipt_sent_at`, which nothing reads any more, is exactly a column waiting for its contract step.

**Who runs migrations?** Today the API runs them when it starts (lesson 8). With two copies starting at once, both try; sqlx takes a lock, so one waits, but a long migration then holds up every new copy. Lesson 40's practice 2, a one-off `migrate` service the others wait for, is the better shape for production, and the pipeline's deploy runs it first.

## Step 5: what to check before calling it done
<!-- bite: 14fa0086-2580-47dd-8a4d-3e9d8cb7d2f0 -->

Lessons 39 to 41 were written without running every check, to save time, and these are on the list to run together:

1. `cargo test --workspace` and Clippy with the lesson 39 code.
2. The three images building, `docker compose up`, an order paid through Caddy reaching notifications, and `docker compose stop api` stopping cleanly within its grace period.
3. The workflow on a real push, and `deploy.sh` on a real server.

## The Rust in this lesson
<!-- bite: 2714a0cb-aefa-47d1-b532-a0e55a7ed775 -->

1. **`cargo fmt --all --check`**: formatting checked, not changed.
2. **`cargo clippy --workspace --all-targets -- -D warnings`**: every crate, tests included, with warnings as errors.
3. **`cargo sqlx prepare --workspace --check`**: the query cache compared with the queries.
4. **`cargo install … --locked`**: a tool installed with the exact versions in its own lock file, so CI gets the same build every time.

## Your project so far
<!-- bite: 05d311c5-e69e-4df4-b5fe-936cba9df2e8 -->

```text
mama-put/
├── .github/workflows/ci.yml      ← NEW: check, test, images (matrix), deploy
├── compose.yaml                  ← image names tagged ${TAG}
└── deploy/
    └── deploy.sh                 ← NEW: runs on the server; the deploy key may run only this
```

And the whole project, after 41 lessons: an Axum API with REST (two versions), GraphQL, gRPC and an MCP server; payments and webhooks; background jobs; caching; live updates; a notifications service fed by an outbox and NATS; service tokens, deadlines and a circuit breaker; logs, traces and metrics; three small images; and a pipeline that tests, builds and deploys every change.

## Common mistakes
<!-- bite: 6579e214-7247-463b-960e-c9e3e4837a83 -->

1. **No cache in CI.** Every run compiles everything; Rust makes that very slow.
2. **Tests that need services CI doesn't start.** Start them in the job, or skip clearly when they're missing.
3. **Images tagged only `latest`.** Nobody knows what's running, and there's nothing to roll back to.
4. **Building on the server.** Slow, and not what was tested. Build once in CI, pull by commit.
5. **A deploy key that can run anything.** `command=` in `authorized_keys`.
6. **Stopping the old copies before the new ones are healthy.** Downtime, and nothing to fall back to.
7. **A migration the previous release can't live with.** Expand, then contract.

## Check your understanding
<!-- bite: 6b7c0495-2339-4a1e-870c-84e5d2bf43f2 -->

1. Why do `check` and `test` run on every pull request, but `images` and `deploy` only on `main`?
2. Why tag images with the commit?
3. What stops a stolen deploy key from deleting everything on the server?
4. Describe the rolling deploy in `deploy.sh`. When is the old API stopped?
5. Why can't one deploy rename a column?

<details>
<summary>Answers, after your attempt</summary>

1. Every change should be checked before it joins `main`; only changes that are on `main`, and have passed, should become images and reach the server.
2. So exactly one image belongs to each commit: "what's running?" has an answer, and rolling back means deploying an earlier commit's images, which are still there.
3. The `command=` option in `authorized_keys`: whatever the key's user asks for, SSH runs only `deploy.sh`, which accepts only a commit id.
4. A new API copy starts beside the old one, and Compose waits until its health check passes; only then are the remaining copies replaced. The old copy drains (its `/readyz` says 503) and stops after its requests finish.
5. During the deploy, old copies still run the old code, which reads the old name. Rename it and they fail. Add the new column, move the data, and remove the old one in a later deploy.

</details>

## Practice
<!-- bite: 5709ddc7-096f-4c6d-9b3c-9895b82ed588 -->

1. Push the project to GitHub and make the `check` and `test` jobs pass.
2. Add a `migrate` step to `deploy.sh`, run before the API rolls.
3. Plan the contract step for `payments.receipt_sent_at`: what has to be true before the migration that drops it can run?

**Done when** a push to a branch runs `check` and `test`, a merge to `main` builds three images tagged with the commit and deploys them with no downtime, and deploying an earlier commit rolls back.

## Before moving on
<!-- bite: a9a0c630-2eed-4442-aff4-25dc14a9224b -->

That's the whole of Mama Put in Axum, from "Mama Put is open!" in lesson 1 to a system that tests, builds and deploys itself. Okay!!!!! The same system, the same lessons, are in [[backend/frameworks/net-http/index|net/http]] and [[backend/frameworks/express/index|Express]]: reading one alongside this is the fastest way to see what's Rust, and what's just good backend engineering.

## Related
<!-- bite: 474988a8-a178-46ae-967e-199ebcd41539 -->

- [[backend/frameworks/axum/index|Axum]] — the whole subject
- [[backend/frameworks/net-http/29-ci-and-deployment|The same lesson in net/http]] — the same pipeline, for a Go module
- [[backend/frameworks/axum/40-docker|Docker]] — the images this pipeline builds

## About this lesson
<!-- bite: fbdb2116-ac63-4172-b7d6-5e23c75f8506 -->

**Level:** Advanced. Lesson 41 of the [[backend/frameworks/axum/index|Axum]] subject, and the last. Written for GitHub Actions, Docker with Compose v2 and a Linux server. Covers a pipeline that checks formatting, Clippy and the query cache, runs every test against real Postgres, Redis and NATS, builds one image per program by commit with layer caching, and deploys over SSH with a single-command key; rolling deploys with health checks and rollback by commit; and expand-and-contract migrations. Written without running the pipeline or the deploy; those checks are listed to run later.
