---
id: c149bf6a-6b3d-4a33-99bc-796752c0b7d0
---

# CI and Deployment

**Continuous integration (CI) means every change is checked automatically (formatted, vetted, tested, scanned) the moment it's pushed, so a broken change is caught before it reaches anyone. Continuous deployment means that once a change passes, it's packaged and put live automatically, the same careful way every time, with a quick way back if it goes wrong.** Together they turn "deploying" from a nervous evening into something that happens several times a day without anyone holding their breath.

## Before you start
<!-- bite: f30359d4-2564-4c51-9b2f-bb5e44d5d846 -->

You should have finished [[backend/frameworks/net-http/28-production-config-and-docker|lesson 28]], with the whole system running under Docker Compose on your laptop, and the code in a GitHub repository. This lesson needs a **server** to deploy to: any Linux machine you can reach over SSH with a public IP address, like a small virtual private server from any hosting company (1–2 GB of memory is enough for Mama Put), and a domain name whose DNS you can change.

After this lesson you will be able to:

1. Write a GitHub Actions pipeline that checks formatting, generated code, vet, staticcheck, vulnerabilities, protobuf contracts, and unit and integration tests.
2. Build every program's image and publish it to GitHub's container registry, tagged with the commit.
3. Prepare a server safely: a deploy user, SSH keys only, a firewall, Docker, secrets and backups.
4. Deploy from CI over SSH with a key that can do one thing, replacing the API without a moment where none is running.
5. Change the database schema without breaking the running version, and roll back to the last good version in one command.
6. Keep dependencies fresh, and keep the pipeline itself from becoming the weak point.

## What to install
<!-- bite: c3c399f5-239c-4456-a7e6-2bde9d8f6975 -->

One more Go tool, for deeper checks than `go vet`:

```bash
go get -tool honnef.co/go/tools/cmd/staticcheck@latest
```

**staticcheck** finds bugs and dead code that `go vet` doesn't look for: values computed and never used, deprecated functions still called, conditions that are always true. It's the most widely used extra Go checker. It joins lesson 14's `govulncheck` and lesson 22's `buf` in `go.mod`'s `tool` list, so CI runs exactly the versions you do.

On the server (step 3) you'll install Docker Engine from Docker's own instructions for your Linux distribution, which includes the Compose plugin. Nothing else.

## Where we stopped
<!-- bite: d0eadd4d-7e10-422d-9105-3796f7c62954 -->

Today, getting a change live looks like this: run the tests (if you remember), build the images on your laptop, copy them to the server somehow, SSH in, run the migrations by hand (if you remember), restart everything, and hope. If the new version is broken, try to remember what the last version was.

Every one of those steps is a chance to make a mistake, and the steps you forget are the ones that hurt. A laptop with an uncommitted change builds an image nobody can rebuild. A migration run after the new code starts breaks the new code. A restart of both API copies at once drops every order placed in those seconds.

The fix isn't being more careful. It's making the careful way the only way: written down once, run by a machine, every time.

## The kid version
<!-- bite: 47fe7883-3191-4307-8651-4ced4150849b -->

Mama Put's food now comes from a central kitchen and goes out to three stalls. Before any new recipe reaches a stall, the head cook tastes it, checks the salt, checks the price on the card matches the price in the book. Every time, the same checks, whoever made the recipe. That's CI.

When a recipe passes, the van takes it to each stall. The driver doesn't empty the old pot until the new one is hot and ready, so there's always something to serve. That's deploying without downtime.

And if customers say the new stew is too salty, the old recipe is still in the book, and tomorrow's van brings it back. That's rolling back.

**Where the picture stops working.** A recipe can be un-made; a database change often can't. If the new recipe needed a new kind of pot, and the stall threw the old pots away, the old recipe can't come back. Step 5 is about never throwing the old pots away too soon.

## Terms used in this lesson
<!-- bite: ae268207-30e0-45df-9814-81969e4956f4 -->

1. **Pipeline**: This is the list of automatic steps that run on every push: checks, tests, builds, deploy.
2. **Workflow**: This is GitHub Actions' word for a pipeline, written as a YAML file in `.github/workflows/`.
3. **Job**: This is one part of a workflow that runs on its own fresh machine (a **runner**). Jobs can wait for other jobs with `needs`.
4. **Container registry**: This is a place to store and download images, like GitHub's `ghcr.io`.
5. **Artifact**: This is something a pipeline produces and keeps: here, the images.
6. **Zero-downtime deploy**: This means replacing a running version with a new one without any moment where nobody is answering.
7. **Rolling update**: This is replacing copies of a service a few at a time, so some are always running.
8. **Rollback**: This is putting the previous version back when the new one is bad.
9. **Expand and contract**: This is changing a database schema in two separate steps (add the new thing; later, remove the old thing), so both the old and the new version of the code work in between.
10. **Environment**: This is GitHub's name for a deploy target, like `production`, which can have its own secrets and require a person's approval.

## Step 1: the CI pipeline
<!-- bite: 6dd85fea-de5b-40e4-aa7f-e5b5f299b655 -->

`.github/workflows/ci.yml`, the checks part:

```yaml
name: ci

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
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # buf breaking compares with main
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Formatted
        run: test -z "$(gofmt -l .)" || (gofmt -l . && exit 1)
      - name: Generated code is up to date
        run: make generate && git diff --exit-code
      - name: Vet
        run: go vet ./...
      - name: Staticcheck
        run: go tool staticcheck ./...
      - name: Known vulnerabilities
        run: go tool govulncheck ./...
      - name: Protobuf lint and breaking changes
        run: |
          go tool buf lint
          go tool buf breaking --against '.git#branch=origin/main'
      - name: Unit tests
        run: make test
```

From the top:

1. **`on: pull_request` and `push` to `main`**: run on every pull request, and on every change that lands on `main`.
2. **`permissions: contents: read`**: by default, a workflow's token can do a lot to your repository. This one can only read it. Jobs that need more ask for more, by name (step 2).
3. **`concurrency` with `cancel-in-progress`**: push twice in a minute, and the first run is cancelled. Nobody needs the result of a commit that's already been replaced.
4. **`actions/setup-go` with `go-version-file: go.mod`**: CI uses the Go version written in `go.mod`, the same as your laptop. It also caches downloaded modules and build results between runs, so a run takes a minute or two, not ten.

And the checks, each one a promise made in an earlier lesson:

1. **Formatted**: `gofmt -l` lists files that aren't formatted. Go has one format, and CI keeps it that way (lesson 1).
2. **Generated code is up to date**: lesson 11's OpenAPI types, lesson 21's GraphQL, lesson 22's protobuf. `make generate` writes them all again; if `git diff` then finds a change, someone edited a spec or schema and forgot to regenerate, or edited generated code by hand.
3. **`go vet`**: the checks the Go team ships, including lesson 22's "you forgot `cancel()`".
4. **staticcheck**: deeper checks (above).
5. **govulncheck** (lesson 14): known vulnerabilities, and only ones in code we actually call, so it rarely cries wolf.
6. **buf lint and buf breaking** (lesson 22): the `.proto` files follow the rules, and nothing in them would break a service built from `main`'s version. `fetch-depth: 0` downloads the whole history, so `origin/main` exists to compare with.
7. **`make test`** (lesson 16): `go test -race -shuffle=on ./...`. This includes lesson 25's import boundary test, lesson 13's every-action-has-a-rule test and lesson 26's every-method-has-a-rule test, so the architecture is checked on every push along with the behaviour.

### Integration tests, with real dependencies

```yaml
  integration:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres" --health-interval 2s --health-retries 20
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    env:
      TEST_DATABASE_URL: postgres://postgres:test@localhost:5432/mamaput_test?sslmode=disable
      TEST_REDIS_URL: redis://localhost:6379/0
      NATS_URL: nats://localhost:4222
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - name: Start NATS with JetStream
        run: docker run -d --name nats -p 4222:4222 nats:2-alpine -js
      - name: Create the test database
        run: PGPASSWORD=test psql -h localhost -U postgres -c 'CREATE DATABASE mamaput_test'
      - name: Integration tests
        run: make test-integration
```

1. **`services`** start containers beside the job, and the `options` health check makes the job wait until Postgres is ready. Lesson 16's `dbtest` finds them through `TEST_DATABASE_URL` (and its "name must end in `_test`" guard is satisfied).
2. **NATS is started by hand**, with `docker run`, because a GitHub `services` container can't be given command-line arguments, and NATS needs `-js` to switch JetStream on. A small wrinkle, and the kind of thing you only learn by trying.
3. **`check` and `integration` run at the same time**, on separate machines. The pipeline takes as long as the slower one, not both added together.

This workflow passes **actionlint**, a checker for GitHub Actions files (`go run github.com/rhysd/actionlint/cmd/actionlint@latest`). It catches typos in `${{ }}` expressions and mistakes in `run:` scripts before you push and wait.

Finally, in the repository's settings on GitHub, make `main` a **protected branch** that needs `check` and `integration` to pass before a pull request can be merged. Now a red pipeline can't reach `main` at all.

## Step 2: building and publishing images
<!-- bite: f707d131-7d27-4694-adfd-6e19d81db06f -->

Once a push to `main` passes, build each program's image and publish it:

```yaml
  publish:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: [check, integration]
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write
    strategy:
      matrix:
        cmd: [api, worker, notifications, migrate]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          build-args: |
            CMD=${{ matrix.cmd }}
            VERSION=${{ github.sha }}
          tags: ghcr.io/${{ github.repository_owner }}/mamaput-${{ matrix.cmd }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.cmd }}
          cache-to: type=gha,mode=max,scope=${{ matrix.cmd }}
```

1. **`if` and `needs`**: only for pushes to `main`, and only after both test jobs passed. Pull requests are tested but never published.
2. **`permissions: packages: write`**: this job alone may publish packages. If a bad dependency ever ran code in the `check` job, it couldn't push a poisoned image.
3. **`matrix`**: the same steps four times, once for each program, in parallel. `${{ matrix.cmd }}` becomes `api`, `worker`, `notifications`, `migrate`: lesson 28's `Dockerfile` builds whichever it's told.
4. **`GITHUB_TOKEN`** is made by GitHub for each run and expires when it ends. No password of yours is stored anywhere.
5. **The tag is the commit**, `ghcr.io/you/mamaput-api:3f9c2a1...`. Never `latest`. A commit tag says exactly what code is in the image, it never changes, and every version you've ever published stays available, which is what makes rollback (step 6) possible.
6. **`VERSION=${{ github.sha }}`** goes into lesson 28's `-ldflags`, so the program itself knows its commit, and every log line and trace says it (lesson 27).
7. **`cache-from` and `cache-to: type=gha`** keep Docker's build cache in GitHub's cache between runs, one per program, so lesson 28's "download modules once" layer is reused.

## Step 3: the server
<!-- bite: dd62510f-cf8e-4308-bf10-09ce0b3889b7 -->

A fresh Ubuntu server, prepared once. As `root`, or with `sudo`:

```bash
# A user for deploying, who can run Docker but nothing else as root.
adduser --disabled-password --gecos "" deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh

# SSH: keys only, no root logins.
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/; s/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl reload ssh

# Firewall: SSH, HTTP and HTTPS. Nothing else from outside.
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Docker Engine and the Compose plugin: follow docs.docker.com/engine/install/ubuntu, then
usermod -aG docker deploy
```

1. **A `deploy` user** in the `docker` group runs everything. (Being in the `docker` group is close to being root, since Docker can do anything on the machine; that's why only the deploy key can log in as this user, and only to run one script, below.)
2. **No passwords over SSH**, and no logging in as `root`. Passwords can be guessed; keys can't.
3. **The firewall** allows exactly what Caddy needs (80 and 443) and SSH. Lesson 28's Compose file already publishes nothing else, except Prometheus and Jaeger on `127.0.0.1`; the firewall is the second lock.

Then, as `deploy`, the project itself:

```bash
git clone https://github.com/you/mama-put.git /srv/mama-put    # needs a read-only deploy key if the repo is private
cd /srv/mama-put
./deploy/make-secrets.sh                                        # lesson 28: random passwords and keys, once
echo "sk_live_..." > secrets/paystack_secret_key                # the real ones, typed in here, never in git
echo "IMAGE_PREFIX=ghcr.io/you/mamaput" > .env                  # Compose reads .env for ${IMAGE_PREFIX}
echo "$GHCR_READ_TOKEN" | docker login ghcr.io -u you --password-stdin   # only if the images are private
```

The server keeps **its own secrets**, made on the server, and they never leave it. CI never sees the Paystack key or the database passwords: it only tells the server which version to run. A leaked CI secret can trigger a deploy; it can't read customers' data.

**DNS**: point `api.mamaput.ng`'s A record at the server's IP address. The first time Caddy starts and gets a request for that name, it fetches a certificate from Let's Encrypt by itself.

**Backups.** Before the first real order, set up nightly backups, because a server's disk is one bad day from gone:

```bash
# /etc/cron.d/mamaput-backup  (runs as deploy at 03:15 every night)
15 3 * * * deploy cd /srv/mama-put && docker compose exec -T postgres pg_dump -U postgres -Fc mamaput > /srv/backups/mamaput-$(date +\%F).dump && find /srv/backups -name '*.dump' -mtime +14 -delete
```

Then copy `/srv/backups` off the server every night (to your hosting company's object storage, say), because a backup on the same disk dies with it. And once, on a quiet afternoon, **restore** a backup into a fresh database and check the orders are there. A backup nobody has ever restored is a hope, not a backup.

## Step 4: deploying from CI
<!-- bite: 0d08f75f-f986-4c1d-91fa-7e9d67aa78fb -->

### One key, one command

CI logs in to the server over SSH as `deploy`, with a key made just for it:

```bash
ssh-keygen -t ed25519 -N "" -C "ci-deploy" -f ci-deploy
```

On the server, the public half goes in `/home/deploy/.ssh/authorized_keys`, with two words in front of it that change everything:

```text
command="/srv/mama-put/deploy/deploy.sh",restrict ssh-ed25519 AAAAC3Nza... ci-deploy
```

1. **`command="..."`**: whatever this key asks to run, the server runs `deploy.sh` instead. The command the key *asked* for is passed to the script as `$SSH_ORIGINAL_COMMAND`, and that's how CI says which version.
2. **`restrict`**: no terminal, no port forwarding, no anything else.

So the key in GitHub's secrets can do exactly one thing: deploy a version of Mama Put. Even if it leaked, nobody could use it to get a shell.

In GitHub, the private half goes in a secret, `DEPLOY_SSH_KEY`, on an **environment** called `production`. In the environment's settings, add yourself as a **required reviewer**: then every deploy waits for a person to click "approve". (Remove that when you trust the pipeline. Some teams never do.) Also store `DEPLOY_KNOWN_HOSTS`, the server's own key, from `ssh-keyscan your.server.ip`, so CI can be sure it's talking to your server and not an impostor.

### The deploy job

```yaml
  deploy:
    needs: [publish]
    runs-on: ubuntu-24.04
    environment: production
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    steps:
      - name: Deploy over SSH
        env:
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          KNOWN_HOSTS: ${{ secrets.DEPLOY_KNOWN_HOSTS }}
          HOST: ${{ vars.DEPLOY_HOST }}
        run: |
          install -m 700 -d ~/.ssh
          echo "$SSH_KEY" > ~/.ssh/deploy && chmod 600 ~/.ssh/deploy
          echo "$KNOWN_HOSTS" > ~/.ssh/known_hosts
          ssh -i ~/.ssh/deploy "deploy@$HOST" "${{ github.sha }}"
```

1. **`environment: production`** gives the job that environment's secrets, and its approval rule.
2. **`concurrency` without cancelling**: two deploys never run at once, and a deploy that has started is never cut off half-way. The next one waits its turn.
3. **Secrets go through `env`**, not straight into the script. GitHub hides them in the logs either way, but passing them as environment variables means a strange character in a secret can't change what the shell command does.
4. **The only thing sent is the commit**, as the "command" the key asks for.

### The script on the server

`deploy/deploy.sh`, committed with everything else:

```bash
#!/usr/bin/env bash
# deploy.sh COMMIT: run that version of Mama Put. Called by CI's key, or by hand for a rollback.
set -euo pipefail
cd /srv/mama-put

version=${SSH_ORIGINAL_COMMAND:-${1:-}}
if [[ ! $version =~ ^[0-9a-f]{40}$ ]]; then
  echo "usage: deploy.sh <full commit sha>" >&2
  exit 2
fi

exec 9>/tmp/mamaput-deploy.lock
flock -n 9 || { echo "another deploy is running" >&2; exit 1; }

echo "deploying $version"
git fetch --quiet origin
git checkout --quiet --detach "$version"       # compose.yaml and deploy/ as they were in this version
export VERSION=$version

docker compose pull --quiet api worker notifications migrate
docker compose run --rm migrate                 # the schema first; old code must still work with it (step 5)
./deploy/rollout.sh api                         # new API copies up and healthy before the old ones go
docker compose up -d --no-deps --wait worker notifications
docker compose up -d --wait                     # anything else whose settings changed (Caddy, Prometheus)

curl -fsS --max-time 5 https://api.mamaput.ng/ >/dev/null   # can the world reach it?
echo "$(date -Is) $version" >> /srv/mama-put-deploys.log
echo "deployed $version"
```

Read it as a checklist that can't be skipped:

1. **Check the input.** `$SSH_ORIGINAL_COMMAND` came over the network. Only a 40-character commit hash gets past the pattern, so nothing else can be smuggled in.
2. **One deploy at a time on the server too**, with `flock`: a lock file that a second copy of the script can't take.
3. **The configuration of that version.** `git checkout` the same commit, so the `compose.yaml`, Caddyfile and alert rules match the code being deployed.
4. **Pull before changing anything**, so a missing image (a typo, a failed publish) stops the deploy before it starts.
5. **Migrations first**, as a one-off container (lesson 28). If a migration fails, `set -e` stops the script, and the old version keeps running, untouched.
6. **The API, without downtime** (below).
7. **The worker and notifications**, replaced the ordinary way. They don't answer customers; lesson 28's polite stop and lesson 25's acks mean nothing in flight is lost, and the stream holds anything that arrives in the few seconds between.
8. **A smoke test**: one real request from outside, through DNS and Caddy and HTTPS. If it fails, the script exits with an error, CI shows red, and you look.
9. **A log of deploys**, which is the list of good versions to roll back to.

### Replacing the API with nothing dropped

`docker compose up -d` on its own would recreate both API copies more or less together, and for a few seconds there'd be nothing to answer. `deploy/rollout.sh` starts the new copies **beside** the old ones, waits until they're healthy, and only then stops the old ones:

```bash
#!/usr/bin/env bash
# rollout.sh SERVICE: replace every container of SERVICE with the new image, without a moment with none running.
set -euo pipefail
service=$1
old=$(docker compose ps -q "$service")

if [[ -z $old ]]; then # first deploy: nothing to replace
  docker compose up -d --no-deps --wait "$service"
  exit 0
fi
count=$(echo "$old" | wc -l)

echo "starting $count new $service containers beside the $count old ones"
if ! docker compose up -d --no-deps --no-recreate --scale "$service=$((count * 2))" --wait --wait-timeout 120 "$service"; then
  echo "the new containers never became healthy: removing them, keeping the old ones" >&2
  for id in $(docker compose ps -q "$service"); do
    grep -q "$id" <<<"$old" || docker rm -f "$id" >/dev/null
  done
  exit 1
fi

sleep 5 # Caddy asks DNS for the API's addresses every 2 seconds (lesson 28): let it find the new ones
echo "new ones are healthy; stopping the old ones politely"
docker stop --time 30 $old >/dev/null
docker rm $old >/dev/null
echo "done: $(docker compose ps -q "$service" | wc -l) $service containers on the new version"
```

1. **`--scale api=4 --no-recreate`**: with `VERSION` set to the new commit, Compose makes two *more* containers from the new image and leaves the two old ones exactly as they are.
2. **`--wait`** waits for the new containers' health checks (lesson 28's `/app healthcheck`) to pass, up to two minutes.
3. **If they never get healthy**, the new ones are removed and the old ones keep serving. A broken build can't take the site down; the deploy fails and you see it in CI.
4. **`sleep 5`** gives Caddy time to see the new addresses (lesson 28's `refresh 2s`) before the old ones disappear.
5. **`docker stop --time 30`** sends `SIGTERM` and waits up to 30 seconds: lesson 28's polite stop runs in full. Its drain delay and Caddy's `lb_try_duration` mean requests in flight finish, and new ones go to the new copies.

I tested this with two versions of a small image built like lesson 28's, checking twice a second how many healthy copies were running. The count never went below two: `2 2 4 2 2 2 2 2`. Two old, four for a moment, two new. And running `docker compose up -d --wait` afterwards, with the same version, left the new copies alone, which is why `deploy.sh` can finish with a plain `up` for everything else.

(There's a Docker plugin, `docker rollout`, that does the same as this script with more care for corner cases. Writing it out shows exactly what a zero-downtime deploy is: never stop the old until the new is ready.)

## Step 5: changing the database without breaking anything
<!-- bite: b530f423-c259-4f3b-ab6a-9ed6d7975e85 -->

Look at the order in `deploy.sh` again: migrations run **first**, while the old version is still serving. And during the rollout, old and new API copies serve at the same time. So for a while, **the old code runs against the new schema**. And if you roll back (step 6), the old code runs against the new schema again, because migrations aren't undone.

So every migration must be safe for the code **before** it. That rules out a whole kind of change done in one step. Renaming `dishes.name` to `dishes.title`, done as one migration, breaks every old copy the moment it runs: they all still say `SELECT name`.

Instead, **expand, then contract**, over several deploys:

1. **Expand** (deploy 1): add the new column, `title`, and copy `name` into it. The code writes **both** and still reads `name`. Old code doesn't know `title` exists, and doesn't care.
2. **Switch** (deploy 2): the code reads `title` (and still writes both, in case of a rollback to deploy 1).
3. **Contract** (deploy 3, days later, when nobody will roll back past deploy 2): stop writing `name`, and a migration drops it.

It's lesson 10's API versioning ("add, don't change; remove only when nobody uses it"), for the database. Lesson 10 promised this step: its `005_prices_in_kobo.sql` renamed `price_naira` to `price_kobo` in one go, which was only safe because Mama Put wasn't live yet and the app could be stopped. Done live, it would be three deploys: add `price_kobo` and fill it, write both and read the new one, then drop `price_naira`. Lesson 12's migration was the safe kind already: it added `customer_id` as a nullable column, so old inserts that didn't know about it kept working.

Two more habits, for tables with many rows:

1. **`CREATE INDEX CONCURRENTLY`** for new indexes on big tables, so writes aren't blocked while it builds. It can't run inside a transaction, so lesson 8's runner needs a way to mark such a migration (a comment on its first line, `-- no-transaction`, is a common choice).
2. **A `lock_timeout`** at the top of migrations: `SET lock_timeout = '5s'`. If a migration has to wait for a lock (a long query is holding the table), it fails after 5 seconds instead of queueing behind it while every new query queues behind *it*, freezing the site. A failed migration is retried at a quieter time; a frozen site isn't.

## Step 6: rolling back
<!-- bite: 552c7fc1-5166-495a-871c-681b160a49e7 -->

The new version is out, and the error rate climbs (lesson 27's `ManyServerErrors` fires). Don't debug in production. **Go back first, then find out why.**

Rolling back is a deploy of the previous version:

```bash
ssh you@your.server
tail -n 5 /srv/mama-put-deploys.log            # the last versions that went out
/srv/mama-put/deploy/deploy.sh 9b1e4c7...      # the one before the bad one
```

The same script, the same checks, the same zero-downtime rollout. It works because:

1. **Every version's images are still in the registry**, tagged by commit (step 2). Nothing to rebuild.
2. **The old code works with the new schema**, because of step 5. The migration doesn't need undoing.
3. **The configuration comes back too**: `git checkout` of the old commit brings back its `compose.yaml` and Caddyfile.

What a rollback **can't** undo: data. If the bad version wrote wrong prices into orders, going back stops it writing more, but the rows it wrote are still wrong. That's a data fix, with a careful script, a test on a copy first, and a backup taken just before.

Then, calmly: find the commit in `git log`, look at its trace and logs in lesson 27's tools (every line says its `version`), write the failing test from what happened, fix, and push. The pipeline takes it from there.

## Step 7: keeping dependencies fresh
<!-- bite: bbccf4e7-5845-4c87-8761-3f8729cf84d8 -->

Old dependencies collect known holes. `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: gomod
    directory: /
    schedule: { interval: weekly }
    groups:
      all-go: { patterns: ["*"] }
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
```

Every week, GitHub's Dependabot opens pull requests updating Go modules (grouped into one pull request, so it's one review, not thirty), the actions in the workflow, and the images in the `Dockerfile`. Each one runs the whole pipeline, so an update that breaks a test never gets merged.

And because new vulnerabilities are found in old code, run `govulncheck` on a schedule too, not just when you push: add `schedule: [{ cron: "0 6 * * 1" }]` to a small workflow that runs only that step, every Monday morning. A hole found in a library you haven't touched for months still shows up.

## Step 8: keeping the pipeline itself safe
<!-- bite: 29705e18-f1d7-4700-95b9-6218a7820f84 -->

The pipeline can deploy to production, so it's worth attacking. A few habits keep it from being the weak point:

1. **Least permissions, per job.** `contents: read` at the top; `packages: write` only for `publish`; the deploy key only in the `production` environment.
2. **Pin actions to a commit.** `actions/checkout@v4` follows whatever its owners tag as `v4`. If an action you use is ever taken over, the next run uses the attacker's code with your permissions. Writing `actions/checkout@<full commit sha> # v4` pins it exactly. Dependabot (step 7) still updates pinned actions for you. The examples here use `@v4` so they're easy to read; pin them in your repository.
3. **Never `pull_request_target` with the pull request's code.** Plain `pull_request` runs a stranger's pull request with no secrets and a read-only token, which is safe. `pull_request_target` runs with your secrets, and checking out the pull request's code under it hands your secrets to whoever wrote it.
4. **Secrets stay on the server.** CI holds one secret that matters, the deploy key, and it can only run `deploy.sh`.
5. **Approvals for production**, at least until you trust the pipeline.
6. **Everything in git.** The workflow, the Dockerfile, the Compose file and the scripts are reviewed like code, because they are code.

## The Go in this lesson
<!-- bite: e2a7fad0-6673-47f7-bb7f-b1028af77132 -->

1. **`go-version-file: go.mod`**: CI uses the exact Go version the module says, the same as everyone's laptop.
2. **`go tool staticcheck ./...`**, `go tool govulncheck ./...`, `go tool buf`: Tools pinned in `go.mod`, run without installing anything.
3. **`gofmt -l .`**: Lists files that aren't formatted; an empty list means all is well.
4. **`go test -race -shuffle=on ./...`**: Every test, with the race detector, in a random order each run, so tests that secretly depend on each other's order are found.
5. **`-tags integration`** and **`-p 1`** (lesson 16): The tests that need real dependencies, one package at a time.
6. **`-ldflags "-X main.version=$SHA"`**: The commit baked into the binary, reported in every log line and trace.
7. **One `Dockerfile` for many `cmd/` programs**: `--build-arg CMD=...` and a CI matrix build them all from one module.

## Your project so far
<!-- bite: 0a17ff5f-07ff-4b0a-a8b2-e3a14aadb2c2 -->

```text
mama-put/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 ← NEW: check, integration, publish (4 images), deploy
│   │   └── vulncheck.yml          ← NEW: govulncheck every Monday
│   └── dependabot.yml             ← NEW: Go modules, actions and images, weekly
├── go.mod                         ← tool honnef.co/go/tools/cmd/staticcheck
├── deploy/
│   ├── deploy.sh                  ← NEW: check the commit, lock, checkout, pull, migrate, rollout, smoke test, log
│   ├── rollout.sh                 ← NEW: new copies beside the old, healthy first, old ones stopped politely
│   └── ...                        ← lesson 28's Caddyfile, postgres-init.sh, make-secrets.sh, env files, Prometheus
├── Dockerfile · compose.yaml      ← lesson 28
├── cmd/ · internal/ · proto/ · migrations/   ← the whole system, lessons 1–28
└── Makefile                       ← generate, test, test-integration, proto-check
```

And on the server, outside git: `/srv/mama-put` (a checkout of the deployed commit), `secrets/`, `.env` with `IMAGE_PREFIX`, `/srv/mama-put-deploys.log`, `/srv/backups`, and the restricted deploy key in `authorized_keys`.

## Common mistakes
<!-- bite: aa1c0644-dcbb-4b8f-abd2-a1433eaceda3 -->

1. **Tests that only run on your laptop.** If CI doesn't run them, they'll stop being run. Everything in the pipeline, and a protected `main`.
2. **Forgetting the generated code check.** The spec says one thing, the code another. `make generate && git diff --exit-code`.
3. **Images tagged `latest`.** Nobody knows what's running, and there's nothing to roll back to. Tag with the commit.
4. **Building images on a laptop.** Unrepeatable, and whatever was uncommitted goes live. Build in CI, from the commit.
5. **Production secrets in CI.** Every workflow change could leak them. Keep them on the server.
6. **A deploy key that can open a shell.** `command="...",restrict`.
7. **Migrations after the new code starts**, or migrations the old code can't live with. Migrate first, expand and contract.
8. **Restarting every copy at once.** Start the new ones, wait for healthy, then stop the old.
9. **No smoke test.** Everything "succeeded", and the site is down. One real request from outside.
10. **Debugging in production during an incident.** Roll back first; understand after.
11. **Backups never restored.** Restore one, on purpose, before you need to.
12. **Actions pinned to a moving tag, and `pull_request_target` with untrusted code.** The pipeline becomes the way in.

## Check your understanding
<!-- bite: 53d3da03-3084-48d3-bbec-16cff4742e62 -->

1. Name four checks in the `check` job, and for each, the earlier lesson whose promise it keeps.
2. Why is NATS started with `docker run` in the integration job, when Postgres and Redis are `services`?
3. Why are images tagged with the commit and not `latest`, and what does that make possible?
4. The deploy key leaks. What can someone do with it, and what stops them doing more?
5. Walk through `rollout.sh` replacing two API copies. When are there four, and what happens if the new ones never get healthy?
6. You need to rename `orders.quantity` to `orders.plates`. Why can't it be one migration, and what are the steps?
7. A deploy has made the error rate jump. What do you do first, and why does that work without undoing the migration it ran?

<details>
<summary>Answers, after your attempt</summary>

1. Any four of: `gofmt` (lesson 1's one format); generated code up to date (lessons 11, 21 and 22's generators); `go vet` (lesson 22's `cancel` and others); `govulncheck` (lesson 14); `buf lint` and `buf breaking` (lesson 22's contract rules); `make test`, which includes lesson 25's boundary test and lessons 13 and 26's completeness tests, all with the race detector (lesson 2).
2. GitHub's `services` containers can't be given command-line arguments, and NATS needs `-js` to turn on JetStream, which lesson 25's code depends on. `docker run` in a step can pass the flag.
3. A commit tag says exactly which code is in the image, never changes, and leaves every version published. That makes deploys repeatable, logs and traces traceable to code, and rollback a matter of deploying an older tag that's still in the registry.
4. Run `deploy.sh` with some commit, which means deploying a version of Mama Put that exists in the repository and the registry. The `command=` and `restrict` options in `authorized_keys` mean the key can't open a shell, forward ports or run anything else, and the script refuses anything that isn't a 40-character commit hash. The real secrets stay on the server, out of reach.
5. It records the two old containers' IDs, then scales to four with `--no-recreate`, so two new ones start from the new image beside the old two; that's when there are four. `--wait` waits for the new ones to be healthy, then after 5 seconds (for Caddy to see them) the old two are stopped politely and removed. If the new ones never get healthy, the script removes them and exits with an error, and the old two never stopped serving.
6. During a deploy, and after any rollback, old code runs against the new schema. Old code says `quantity`, so a rename would break it the moment the migration ran. Instead: add `plates`, copy `quantity` into it, and make the code write both (deploy 1); make the code read `plates` (deploy 2); later, when nobody will roll back past deploy 2, stop writing `quantity` and drop it (deploy 3).
7. Roll back first: run `deploy.sh` with the previous good commit from the deploys log. It works because the old images are still in the registry, and because every migration is written to be safe for the code before it, so the old version runs happily on the new schema. Then find out why, write the failing test, fix and push.

</details>

## Practice
<!-- bite: b9bc209e-2a24-4056-8ee2-313120efd103 -->

1. Add `ci.yml` to your repository, open a pull request with a badly formatted file, and watch `check` fail. Then protect `main` so it can't be merged.
2. Run actionlint on the workflow before pushing it, and fix anything it finds.
3. Prepare a server as in step 3, point a domain (or a free subdomain) at it, and do a first deploy by hand with `deploy.sh <commit>`.
4. Make the restricted deploy key, add it and the `production` environment to GitHub, and let a push to `main` deploy by itself.
5. Run `curl` in a loop against the live API (`while true; do curl -s -o /dev/null -w '%{http_code}\n' https://api.mamaput.ng/; sleep 0.2; done`) during a deploy, and check every line says `200`.
6. Do a rollback on purpose: deploy, then deploy the previous commit, and check the version in the logs changes back.
7. Restore last night's backup into a scratch database on your laptop (`pg_restore -d mamaput_restore mamaput-YYYY-MM-DD.dump`) and count the orders.
8. Do a rename with expand and contract over three deploys, and roll back once in the middle to prove it holds.

**Done when** a pull request can't be merged unless every check passes; a push to `main` publishes four images tagged with its commit and, after your approval, deploys them; a `curl` loop sees no failures during a deploy; rolling back to the previous commit is one command and drops nothing; the deploy key can't open a shell; and you've restored a backup at least once.

## The end of the road, and the start of the next
<!-- bite: 1368b933-ea95-45c5-820d-b53dbc8fddba -->

Okay!!!!! Look at where Mama Put API started: in lesson 1, a few lines of Go answering "Mama Put is open!".

Now it's a production system:

1. A menu, orders and customer accounts in PostgreSQL, with rules in the services, the last plate going to exactly one customer, and roles that decide who can do what.
2. A well-designed REST API with one response shape, pagination, filtering and sorting, two versions side by side, and OpenAPI docs generated into Go types.
3. Payments through Paystack that can't be counted twice, webhooks in and out, idempotency so retries are harmless, background jobs, a fail-open Redis cache, and a kitchen screen that updates live.
4. The same services behind GraphQL for the phone app, gRPC for our own services, and MCP for AI assistants that act for a customer and can never spend their money on a guess.
5. A second service for notifications, fed by an outbox and NATS, calling back with deadlines, retries, circuit breakers and signed service tokens.
6. Logs, metrics and traces across every service, typed config, health checks, polite shutdown, 10 MB images, the whole system in one Compose file, and a pipeline that tests, publishes, deploys without dropping an order, and rolls back in one command.

Almost all of it on Go's standard library, with small, focused packages only where the standard library really has nothing. That's the Go way, and you've now seen how far it goes.

What next? The same Mama Put API is built in [[backend/frameworks/chi/index|Chi]], a router that sits on top of everything you know here, and in [[backend/frameworks/gin/index|Gin]], a full framework that does more for you and asks you to do things its way. Building the same system again in each is the quickest way to see what a framework actually gives you, and what it costs.

## Related
<!-- bite: 11a75083-4a81-49da-8b2f-a3a0ca8b846f -->

- [[backend/frameworks/net-http/index|net/http: all the lessons]]
- [[backend/frameworks/express/29-ci-and-deployment|The same lesson in Express]] — the same pipeline for a Node monorepo
- [[backend/frameworks/net-http/16-testing|Testing]] — the tests the pipeline runs
- [[backend/frameworks/net-http/28-production-config-and-docker|Production Config and Docker]] — the images and Compose file being deployed
- [[backend/frameworks/chi/index|Chi]] — the same app with a router on top

## About this lesson
<!-- bite: 35b4b562-39d2-4afa-b450-098152461500 -->

**Level:** Advanced. Lesson 29, the last, of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, GitHub Actions and the GitHub container registry, Docker Engine with Compose v2 or later, and an Ubuntu server. Covers a CI workflow with formatting, generated-code, vet, staticcheck, govulncheck and buf checks, unit and integration tests with service containers and a hand-started NATS, actionlint, protected branches, publishing images per program with a matrix, commit tags and build caches, least-privilege job permissions, preparing a server with a deploy user, keys-only SSH, a firewall, server-held secrets and tested backups, a restricted deploy key with `command=` and `restrict`, production environments with approval and serialized deploys, a deploy script that checks its input, locks, migrates first, rolls the API out with no downtime and smoke-tests, a rolling update with Compose's `--scale --no-recreate --wait`, expand-and-contract migrations with concurrent indexes and lock timeouts, rollback by commit, Dependabot and scheduled vulnerability checks, and keeping the pipeline itself safe.
