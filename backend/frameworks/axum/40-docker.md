---
id: 7b2aabb4-1bd6-43cf-a128-aaae809631a8
---

# Docker

**A Docker image is a program packed with everything it needs to run, so it runs the same on any machine, and Docker Compose starts a whole system of them, with their networks, storage and secrets, from one file.**

## Before you start
<!-- bite: 728559cf-a51a-4089-9119-78c2519ca909 -->

You should have finished [[backend/frameworks/axum/39-config-secrets-and-health|lesson 39]]: every program reads its settings safely, answers health checks and stops on SIGTERM. You need Docker with Compose (`docker compose version`).

After this lesson you will be able to:

1. Build small, safe images for a Rust workspace, with dependencies cached in their own layer.
2. Build without a database, using sqlx's query cache.
3. Run the whole system with Compose: three programs, Postgres, two Redis servers, NATS, Jaeger, Prometheus and Caddy.
4. Keep the inside of the system unreachable from outside, and secrets out of the environment.

## Where we stopped
<!-- bite: 4443b8f4-0019-478f-9902-cdf930675230 -->

To run Mama Put today you start Postgres, two Redis servers, NATS, Jaeger and Prometheus by hand, then three programs from two folders, each with its own `.env`. It works on one laptop, after an afternoon. A server needs the same thing, every time, in one command.

## Terms used in this lesson
<!-- bite: c3ddb3f9-cd23-49f4-8a9d-5383c0b40e25 -->

1. **Image**: This is a packed program and everything it needs, built once from a `Dockerfile`.
2. **Container**: This is a running image, with its own files, network and process list.
3. **Layer**: This is one step of a Dockerfile, saved. If a step's inputs haven't changed, Docker reuses the saved layer instead of running it again.
4. **Multi-stage build**: This is a Dockerfile with several `FROM`s: early stages build, the last one copies only the finished program into a small image.
5. **Compose file**: This is `compose.yaml`: every container in a system, how they connect, and what they keep.

## Step 1: building without a database
<!-- bite: 4c068212-e39e-41de-a2fa-ae6242e178b9 -->

sqlx checks every query against a real database while compiling (lesson 8). A Docker build has no database. The answer is sqlx's **query cache**: run once with the database, and sqlx saves what it learned about each query into `.sqlx/`; then `SQLX_OFFLINE=true` builds check against those files instead.

```bash
cargo sqlx prepare --workspace
```

writes the API's queries to `.sqlx/` (90 files). Notifications' queries weren't among them: its `sqlx.toml` points it at another database, and the installed `sqlx` command was built without config-file support. The macros themselves write the cache when `SQLX_OFFLINE_DIR` is set during a normal build against the live database:

```bash
SQLX_OFFLINE_DIR=$PWD/notifications/.sqlx cargo check -p notifications --all-targets
```

Then the whole workspace builds with no database at all (`SQLX_OFFLINE=true cargo check --workspace`, tried for real). Both `.sqlx` folders go into git. Change a query and forget to refresh them, and the offline build fails; lesson 41's pipeline checks it on every change.

## Step 2: the Dockerfile
<!-- bite: 3c08704d-2047-4df8-93a4-72f3edcb0e38 -->

```dockerfile
# syntax=docker/dockerfile:1
# One Dockerfile for all three programs: docker build --target api|worker|notifications .

# --- tools: Rust, and cargo-chef, which lets Docker keep the dependencies' build as its own layer
FROM rust:1.96-slim-bookworm AS chef
RUN cargo install cargo-chef --locked --version 0.1.73
WORKDIR /app
# Two compile jobs, as on the laptop: building in Docker shouldn't take the whole machine.
ENV CARGO_BUILD_JOBS=2

# --- a list of the dependencies, from Cargo.toml and Cargo.lock only
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# --- build the dependencies (slow, and cached until Cargo.lock changes), then our code (quick)
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --workspace --recipe-path recipe.json
COPY . .
# No database while building: sqlx checks queries against the cache in .sqlx instead.
ENV SQLX_OFFLINE=true
RUN cargo build --release --workspace --bins

# --- the images that run: distroless has glibc and certificates, and no shell, no package manager,
# nothing an attacker could use. `nonroot` runs as user 65532, never as root.
FROM gcr.io/distroless/cc-debian12:nonroot AS api
COPY --from=builder /app/target/release/mama-put /usr/local/bin/mama-put
EXPOSE 8080 50051 9100
ENTRYPOINT ["/usr/local/bin/mama-put"]

FROM gcr.io/distroless/cc-debian12:nonroot AS worker
COPY --from=builder /app/target/release/worker /usr/local/bin/worker
ENTRYPOINT ["/usr/local/bin/worker"]

FROM gcr.io/distroless/cc-debian12:nonroot AS notifications
COPY --from=builder /app/target/release/notifications /usr/local/bin/notifications
ENTRYPOINT ["/usr/local/bin/notifications"]
```

Read it top to bottom:

1. **`chef`**: Rust, plus **cargo-chef**, which splits "build the dependencies" from "build our code".
2. **`planner`**: `cargo chef prepare` reads `Cargo.toml` and `Cargo.lock` and writes `recipe.json`, a list of the dependencies. It's the same file as long as the dependencies don't change.
3. **`builder`**: `cargo chef cook` builds only the dependencies, from the recipe. That layer is slow (hundreds of crates, in release mode) and Docker keeps it until `Cargo.lock` changes. Then `COPY . .` and `cargo build` build our own code, quickly.
4. **Three final images, one per program**, chosen with `--target`. Each is `gcr.io/distroless/cc-debian12:nonroot`: glibc, certificates, and nothing else. No shell, no package manager, nothing an attacker could use, which is why lesson 39 gave the API a `healthcheck` command of its own.
5. **`nonroot`** runs as user 65532. A program that's broken into isn't root in its container either.
6. **`CARGO_BUILD_JOBS=2`**: as on the laptop, so a build doesn't take the whole machine.

`.dockerignore` keeps what must never reach Docker out of the build:

```text
# Never sent to Docker: build output, secrets, local settings, uploaded files.
target/
keys/
.env
notifications/.env
uploads/
.git/
```

Without it, `COPY . .` would copy `target/` (gigabytes), and `keys/` and `.env` into an image anyone with the image could read.

Build one:

```bash
docker build --target api -t mama-put/api:dev .
```

The first build is long: the dependencies compile from nothing, in release mode, with two jobs. After that, a change to our code rebuilds only the last steps.

## Step 3: the whole system in Compose
<!-- bite: cb2dec35-436d-4e68-a67b-73ab200ea440 -->

`compose.yaml`, in parts. First the shared settings and the stores:

```yaml
# The whole of Mama Put on one machine: docker compose up -d --build
# Two networks: `edge` is what the outside reaches (Caddy, and through it the API); `backend` is
# internal only: nothing outside can reach Postgres, Redis, NATS or the other services.

name: mama-put

x-api-env: &common-env
  NATS_URL: nats://nats:4222
  CACHE_REDIS_URL: redis://redis-cache:6379/0
  LIMITS_REDIS_URL: redis://redis-limits:6379/0
  OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4317
  METRICS_ADDR: 0.0.0.0:9100

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: mama
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      POSTGRES_DB: mamaput
    secrets: [postgres_password]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./deploy/postgres-init.sql:/docker-entrypoint-initdb.d/10-notifications.sql:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "mama", "-d", "mamaput"]
      interval: 5s
    networks: [backend]

  redis-cache:
    image: redis:7-alpine
    command: ["redis-server", "--maxmemory", "64mb", "--maxmemory-policy", "allkeys-lru", "--save", ""]
    networks: [backend]

  redis-limits:
    image: redis:7-alpine
    command: ["redis-server", "--maxmemory", "64mb", "--maxmemory-policy", "noeviction"]
    networks: [backend]

  nats:
    image: nats:2-alpine
    command: ["-js", "-sd", "/data", "-m", "8222"]
    volumes: [natsdata:/data]
    networks: [backend]

  jaeger:
    image: jaegertracing/jaeger:2.11.0
    ports: ["127.0.0.1:16686:16686"]   # its web page, for this machine only
    networks: [backend]

  prometheus:
    image: prom/prometheus:v3.7.3
    command: ["--config.file=/etc/prometheus/prometheus.yml"]
    volumes:
      - ./deploy/prometheus.compose.yml:/etc/prometheus/prometheus.yml:ro
      - ./deploy/alerts.yml:/etc/prometheus/alerts.yml:ro
    ports: ["127.0.0.1:9090:9090"]
    networks: [backend]
```

1. **`x-api-env`** is a YAML anchor: settings several services share, written once and merged in with `<<: *common-env`.
2. **Each service is reached by its name**: `redis://redis-cache:6379`, `nats://nats:4222`. Compose's network has its own name lookup.
3. **Postgres keeps its data in a volume**, `pgdata`, so it survives the container being recreated. Its password comes from a secret file (`POSTGRES_PASSWORD_FILE`), and `deploy/postgres-init.sql` runs once, on a new volume, making notifications' user and database:

```sql
-- Run once, when the Postgres volume is new: the notifications service's own user and database.
-- Change the password, and put the same one in NOTIFICATIONS_DATABASE_URL.
CREATE USER notifications WITH PASSWORD 'change-me';
CREATE DATABASE mamaput_notifications OWNER notifications;
REVOKE CONNECT ON DATABASE mamaput FROM PUBLIC;
GRANT CONNECT ON DATABASE mamaput TO mama;
```

4. **NATS keeps its streams in a volume too** (`-sd /data`), so events waiting for a reader survive a restart.
5. **Jaeger and Prometheus** publish their pages on `127.0.0.1` only: this machine can look, the internet can't.

The API:

```yaml
  api:
    image: ${REGISTRY:-mama-put}/api:${TAG:-dev}   # built here, or pulled by deploy.sh
    build: { context: ., target: api }
    environment:
      <<: *common-env
      DATABASE_URL_FILE: /run/secrets/database_url
      JWT_SECRET_FILE: /run/secrets/jwt_secret
      STAFF_KEY_FILE: /run/secrets/staff_key
      PAYSTACK_SECRET_KEY_FILE: /run/secrets/paystack_secret_key
      PUBLIC_URL: ${PUBLIC_URL:-http://localhost}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-http://localhost}
      AUTH_ISSUER: ${AUTH_ISSUER:-http://localhost:9000}
      AUTH_JWKS_URL: ${AUTH_JWKS_URL:-http://localhost:9000/jwks.json}
      SERVICE_KEYS: notifications=/run/secrets/notifications_public_key
      LISTEN_ADDR: 0.0.0.0:8080
      GRPC_ADDR: 0.0.0.0:50051
      APP_ENV: production
      BEHIND_PROXY: "true"
      SHUTDOWN_DRAIN_SECONDS: "5"
      UPLOAD_DIR: /data/uploads
    secrets: [database_url, jwt_secret, staff_key, paystack_secret_key, notifications_public_key]
    volumes: [uploads:/data/uploads]
    depends_on:
      postgres: { condition: service_healthy }
    # No shell or curl in the image: the program checks itself.
    healthcheck:
      test: ["CMD", "/usr/local/bin/mama-put", "healthcheck"]
      interval: 10s
      start_period: 20s
    stop_grace_period: 20s   # the 5 s drain, then requests in progress
    networks: [edge, backend]
```

1. **Secrets as files**: `JWT_SECRET_FILE: /run/secrets/jwt_secret`, and the `secrets:` list says which files this container may see. Lesson 39's `_FILE` support reads them.
2. **`LISTEN_ADDR: 0.0.0.0:8080`**: every network the container is on, so Caddy can reach it.
3. **`depends_on` with `service_healthy`**: the API waits for Postgres to answer `pg_isready`. The worker and notifications wait for the API's own health check, because the API runs the migrations.
4. **`stop_grace_period: 20s`**: after SIGTERM, 5 seconds of draining, then up to 15 for requests in progress, before Docker kills it.
5. **`image` and `build` together**: `docker compose up --build` builds it here; lesson 41's `deploy.sh` pulls the one CI built, by commit.

The worker still reads plain environment variables, so its settings come from the shell (`${WORKER_DATABASE_URL}`); moving it to `Settings` and `_FILE` is lesson 39's first practice.

And Caddy, in front:

```text
# Caddy: HTTPS with a free certificate for the real domain, and every request passed to the API.
{$SITE_ADDRESS:localhost} {
	encode zstd gzip
	reverse_proxy api:8080 {
		# Ask the API's /readyz; while it says "stopping", send nothing new.
		health_uri /readyz
		health_interval 2s
		# Live streams (kitchen events, MCP) must reach the client at once, not in batches.
		flush_interval -1
	}
}
```

Caddy gets HTTPS certificates by itself for a real domain (`SITE_ADDRESS=api.mamaput.ng`), and checks the API's `/readyz` every 2 seconds, so a draining copy gets nothing new. `flush_interval -1` sends live streams (lesson 20's kitchen events, MCP) to the client at once instead of in batches.

### Two networks

```yaml
networks:
  edge: {}
  backend: { internal: true }
```

`backend` is **internal**: containers on it can reach each other, and nothing else, in or out. Postgres, Redis, NATS, the worker and notifications live only there. The API is on both; Caddy only on `edge`. So the only way in from outside is ports 80 and 443, through Caddy, to the API. The gRPC port, the metrics ports, the databases: none of them are reachable from outside, and that's lesson 34's "on a private network" made real.

Prometheus reads the containers by name, in `deploy/prometheus.compose.yml`:

```yaml
# The same as prometheus.yml, with the containers' names instead of 127.0.0.1.
global:
  scrape_interval: 15s
rule_files: [alerts.yml]
scrape_configs:
  - job_name: api
    static_configs: [{ targets: ["api:9100"] }]
  - job_name: worker
    static_configs: [{ targets: ["worker:9101"] }]
  - job_name: notifications
    static_configs: [{ targets: ["notifications:9102"] }]
```

## Step 4: running it
<!-- bite: 18db2857-d1d4-4db8-af4e-72475a1d3fc4 -->

Make the secrets once (never in git):

```bash
mkdir -p secrets
openssl rand -hex 32 > secrets/jwt_secret
openssl rand -hex 16 > secrets/staff_key
openssl rand -hex 16 > secrets/postgres_password
echo "postgres://mama:$(cat secrets/postgres_password)@postgres:5432/mamaput" > secrets/database_url
echo "sk_test_your_paystack_key" > secrets/paystack_secret_key
```

Then:

```bash
docker compose up -d --build
docker compose ps
```

`ps` should show every service running, and the API `healthy` once its `healthcheck` has passed. `docker compose logs -f api` shows its JSON lines; `docker compose stop api` should show `stopping` with `SIGTERM` and an exit well inside the grace period.

These runs are listed to do: the image build was started on the laptop, and the Compose run, an order paid through it and the `docker stop` timing are on the list of checks still to run.

## The Rust in this lesson
<!-- bite: d0c42278-88e0-44d3-88d2-a9fa35cf2345 -->

1. **`SQLX_OFFLINE=true`** and the `.sqlx` folders: query checks without a database.
2. **`SQLX_OFFLINE_DIR`**: where the query macros write what they learn, during a live build.
3. **Release builds**, `cargo build --release`: optimised, much slower to build, much faster to run.
4. **A workspace's binaries**, `--workspace --bins`: every program from every crate, in one build.

## Your project so far
<!-- bite: 676bb3a1-bfeb-4db7-8d05-0cc01a16dfc6 -->

```text
mama-put/
├── Dockerfile                    ← NEW: cargo-chef, distroless nonroot; targets api, worker, notifications
├── .dockerignore                 ← NEW
├── .sqlx/ · notifications/.sqlx/ ← NEW: the query caches, in git
├── compose.yaml                  ← NEW: the whole system; edge and internal backend networks; secrets
├── secrets/                      ← NEW, not in git: one file per secret
└── deploy/
    ├── postgres-init.sql         ← NEW: notifications' user and database
    ├── prometheus.compose.yml    ← NEW: scrape by container name
    └── Caddyfile                 ← NEW: HTTPS, health checks, streaming
```

## Common mistakes
<!-- bite: 2a30b834-d21c-42c2-9107-7b8323b2fd67 -->

1. **No `.dockerignore`.** `target/` makes every build slow, and `keys/` and `.env` end up in the image.
2. **One `COPY . .` before building dependencies.** Every code change rebuilds every crate. Cook the dependencies first.
3. **A full OS image to run one program.** Distroless, as a non-root user.
4. **Forgetting the query cache.** The offline build fails; refresh `.sqlx` with every query change.
5. **Every container on one network with published ports.** Keep the inside internal; one way in.
6. **Secrets in `environment:`.** `docker inspect` shows them. Secret files.
7. **`depends_on` without a health condition.** "Started" isn't "ready".

## Check your understanding
<!-- bite: 2324adb4-4b47-41a3-8428-8f819c192ef7 -->

1. What does cargo-chef change about rebuilding after a one-line code change?
2. Why can't the API's container use `curl` for its health check, and what does it use instead?
3. Which containers can the internet reach, and how is that enforced?
4. Why do the worker and notifications wait for the API to be healthy, not just Postgres?

<details>
<summary>Answers, after your attempt</summary>

1. The dependencies are built in their own layer, from a recipe that only changes when `Cargo.lock` does, so Docker reuses that layer and only our own code is rebuilt.
2. The distroless image has no shell or curl. It runs `mama-put healthcheck`, which asks the API's own `/readyz` and exits 0 or 1.
3. Only Caddy, on ports 80 and 443. The `backend` network is internal, so nothing on it can be reached from outside, and only Caddy publishes ports to the world.
4. Because the API runs the database migrations when it starts. Until it's healthy, the tables they need may not be there yet.

</details>

## Practice
<!-- bite: 052a6614-4939-43b5-a544-dca009d1c884 -->

1. Build all three images and compare their sizes with `docker images`.
2. Add a `migrate` service that runs the migrations once and exits, and make the API and worker wait for it (`service_completed_successfully`). Why is that better than the API migrating at start, with two API copies?
3. Run two copies of the API (`docker compose up -d --scale api=2`) and watch Caddy share requests between them.

**Done when** `docker compose up -d --build` starts everything, the API reports `healthy`, an order placed through Caddy gets its receipt in notifications' log, and `docker compose stop api` shows a clean SIGTERM stop.

## Before moving on
<!-- bite: acbda501-5e81-4654-a537-032dc2332005 -->

Mama Put now runs anywhere Docker runs, the same way every time, with the inside sealed off and secrets kept as files. The last step is making that happen by itself: every change tested, built and deployed, safely, without anyone typing these commands on a server.

## Related
<!-- bite: e383b77e-83ed-451c-8ef0-5d9b3e377fa6 -->

- [[backend/frameworks/axum/41-ci-and-deployment|Next: CI and Deployment]]
- [[backend/frameworks/net-http/28-production-config-and-docker|The same lesson in net/http]] — a static Go binary on distroless, and the same Compose layout
- [[backend/frameworks/axum/08-data-with-postgres|Data with PostgreSQL]] — the checked queries the cache keeps working

## About this lesson
<!-- bite: 23c1a38f-0889-4b73-8a48-ca1ce61224e6 -->

**Level:** Advanced. Lesson 40 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later, Docker with Compose v2, cargo-chef and distroless images. Covers sqlx's offline query cache for a workspace with two databases, a multi-stage Dockerfile with cached dependencies and three distroless non-root targets, `.dockerignore`, a Compose file for the whole system with health-gated start order, volumes, secret files, an internal backend network, Caddy in front with health checks and streaming, and Prometheus by container name. The offline build was checked on a laptop; the image build, the Compose run and the stop timing are listed to run later.
