---
id: ecd2fb67-0326-4396-a889-310de65c0b97
---

# Production Config and Docker

**Getting ready for production means making the system start the same way everywhere, refuse to start when it's set up wrong, tell the platform when it's healthy, and stop without dropping anyone's request. Docker packs each service with exactly what it needs into an image, and Docker Compose starts the whole system, every service and database, with one command.** Up to now Mama Put has run in four terminals with hand-typed `docker run` commands. This lesson makes it something you could hand to a server.

## Before you start
<!-- bite: ac62c8d1-76d9-4679-bdc9-026a240d31cb -->

You should have the observability from [[backend/frameworks/express/27-observability|lesson 27]], and Docker (or Podman) installed. If containers, images and volumes are new to you, read [[devops/03-docker/index|Docker]] first; this lesson uses them rather than teaching them from zero.

After this lesson you will be able to:

1. Load and check every setting at start-up with zod, and refuse to start with a clear list of what's wrong.
2. Add liveness and readiness health checks, and say what each is for.
3. Shut down politely: stop taking new work, finish what's in flight, close connections, exit.
4. Give the app a database user that can't change the schema, and run migrations as their own step.
5. Write a small, safe Dockerfile for a Node service in a monorepo.
6. Run the whole system with Docker Compose, in the right order, with only one port open to the outside.

## Where we stopped
<!-- bite: c22b3d31-36e3-4f84-b8cb-41f4ab43d6db -->

Count how Mama Put starts today:

1. `docker run` for Postgres, two Redis servers, Jaeger, Prometheus, each typed from a lesson.
2. `npm run migrate -w api`.
3. Three terminals: `npm run dev -w api`, `npm run worker -w api`, `npm run dev -w notifications`.
4. Settings in three `.env` files. If `PAYSTACK_SECRET_KEY` is missing, nobody knows until the first customer pays and the webhook check fails, quietly, for every payment.

And when you stop it, Ctrl+C kills each program in the middle of whatever it was doing.

That's a laptop setup. A server needs: one way to start everything, settings checked before the first request, the platform knowing which containers are healthy, and stops that lose nothing.

## The kid version
<!-- bite: 0c78e0b6-c9d8-49ca-bafd-cf592ab9add3 -->

Before Mama opens in the morning, she checks: gas? rice? oil? change for customers? If the gas is out, she doesn't open and *then* discover it when the first customer orders. She checks first, and if something's missing she says exactly what.

At closing time, she doesn't throw the last customers out mid-meal. She turns the sign to "closed" so nobody new comes in, lets the people eating finish, then locks up.

And everything for the stall packs into one cart, the same way every day, so her sister can set up an identical stall across town.

The morning check is config validation. The sign is readiness. Letting people finish is graceful shutdown. The cart is a Docker image.

**Where the picture stops working.** Mama's sister can improvise if one pot is missing. A container can't: it has exactly what the image put in it, nothing more. That's the point. "Works on my machine" stops being a thing, because every machine runs the same cart.

## Terms used in this lesson
<!-- bite: 8d7f9aa4-c23a-4064-940e-aceaaa1a3f22 -->

1. **Configuration**: This is everything that differs between places the app runs (addresses, keys, limits) and so lives outside the code.
2. **Fail fast**: This means stopping at start-up, loudly, when something is wrong, instead of starting and failing later in a confusing way.
3. **Liveness check**: This answers "is this process alive, or stuck?". If it fails, the platform restarts the container.
4. **Readiness check**: This answers "should this process get traffic right now?". If it fails, the platform stops sending it requests, but doesn't restart it.
5. **Graceful shutdown**: This is stopping in order: refuse new work, finish current work, close connections, exit.
6. **Image**: This is a packed, read-only file system with your app and everything it needs. A **container** is a running copy of an image.
7. **Dockerfile**: This is the recipe for building an image.
8. **Docker Compose**: This is a tool that starts several containers together from one file, `compose.yaml`, with their settings, networks and volumes.
9. **Volume**: This is storage that lives outside a container, so data survives when the container is replaced.

## Step 1: config, checked once
<!-- bite: 602802f9-6c15-49bf-8091-a80472cdf7dd -->

Every service reads `process.env` in a dozen places today: `process.env.DATABASE_URL!` here, `process.env.STAFF_KEY ?? ""` there (lesson 8 promised this lesson would fix that). Replace them all with **one** file that reads every setting, checks it, and gives the rest of the code a typed object.

`api/src/config.ts`:

```ts
import { z } from "zod";

const list = z
  .string()
  .transform((value) => value.split(",").map((item) => item.trim()).filter(Boolean));

const Config = z
  .object({
    NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
    PORT: z.coerce.number().int().min(1).max(65535).default(3000),
    GRPC_ADDRESS: z.string().default("0.0.0.0:50051"),
    METRICS_PORT: z.coerce.number().int().default(9464),
    LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),

    DATABASE_URL: z.url(),
    QUEUE_REDIS_URL: z.url(),
    CACHE_REDIS_URL: z.url(),

    PUBLIC_URL: z.url(),
    ALLOWED_ORIGINS: list.pipe(z.array(z.url()).min(1)),
    TRUST_PROXY_HOPS: z.coerce.number().int().min(0).max(3).default(0),

    JWT_SECRET: z.string().min(32, "must be at least 32 characters"),
    PAYSTACK_SECRET_KEY: z.string().regex(/^sk_(test|live)_/, "must be a Paystack secret key"),
    DELIVERY_WEBHOOK_URL: z.url(),
    DELIVERY_WEBHOOK_SECRET: z.string().min(32),
    SERVICE_PUBLIC_KEYS: z.string().transform((text, ctx) => {
      try {
        return z.record(z.string(), z.string()).parse(JSON.parse(text));
      } catch {
        ctx.addIssue({ code: "custom", message: "must be JSON like {\"notifications\": \"-----BEGIN PUBLIC KEY-----...\"}" });
        return z.NEVER;
      }
    }),

    AUTH_ISSUER: z.url(),
    AUTH_JWKS_URL: z.url(),
    MCP_RESOURCE_URL: z.url(),

    PHOTOS_DIR: z.string().default("uploads/photos"),
    SHUTDOWN_GRACE_MS: z.coerce.number().int().default(20_000),
  })
  .superRefine((config, ctx) => {
    if (config.NODE_ENV === "production") {
      if (config.PAYSTACK_SECRET_KEY.startsWith("sk_test_")) {
        ctx.addIssue({ code: "custom", path: ["PAYSTACK_SECRET_KEY"], message: "is a TEST key in production" });
      }
      if (!config.PUBLIC_URL.startsWith("https://")) {
        ctx.addIssue({ code: "custom", path: ["PUBLIC_URL"], message: "must be https in production" });
      }
    }
  });

export type Config = z.infer<typeof Config>;

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const result = Config.safeParse(env);
  if (!result.success) {
    console.error("Mama Put API can't start. These settings are wrong or missing:");
    for (const issue of result.error.issues) {
      console.error(`  ${issue.path.join(".") || "(config)"}: ${issue.message}`);
    }
    process.exit(1);
  }
  return result.data;
}
```

Start the API with `JWT_SECRET` missing and a test Paystack key in production, and it refuses, in plain words:

```text
Mama Put API can't start. These settings are wrong or missing:
  JWT_SECRET: Invalid input: expected string, received undefined
  PAYSTACK_SECRET_KEY: is a TEST key in production
```

Rules worth keeping:

1. **One place reads the environment.** `server.ts` calls `loadConfig()` first thing and passes pieces of `config` down as dependencies. No other file touches `process.env`. Tests build a config object directly.
2. **Coerce what arrives as text.** Environment values are always strings. `z.coerce.number()` turns `"3000"` into `3000`, and fails on `"three thousand"`.
3. **Defaults only for things that are safe to default.** A port, a log level: yes. A secret, a database address: never. A missing secret must stop the app.
4. **Print what's wrong, never the values.** The error lists setting names and problems. Printing `JWT_SECRET=...` into logs would leak the secret this check is protecting.
5. **Check combinations**, with `superRefine`: a test key in production, plain `http` for the public URL. Those are the expensive mistakes.

`QUEUE_REDIS_URL` is lesson 18's `REDIS_URL`, renamed now that there are two Redis servers and a name should say which. `TRUST_PROXY_HOPS` is lesson 14's `app.set("trust proxy", ...)`, now set per environment: 0 on a laptop, 1 behind one proxy in production. `ALLOWED_ORIGINS` is lesson 14's CORS list, which differs between staging and production.

Notifications gets its own `config.ts` with its own settings. Each service checks only what *it* needs.

**Where do the values come from?** On a laptop, `.env` files (never committed; `.env.example` is, with every setting and no real values). In production, from the platform's secret storage, given to the container as environment variables or files. [[devops/06-secret-management/index|Secret Management]] covers the options. The app doesn't care: it reads the environment, checks it, and starts or refuses.

## Step 2: health checks
<!-- bite: eaae2c60-9596-46d5-8ecf-74a5f79dc050 -->

Two questions, two routes. They sound alike and are used very differently.

```ts
// api/src/health.ts
export function createHealthRoutes(deps: { pool: pg.Pool; queueRedis: Redis; isShuttingDown: () => boolean }) {
  const router = express.Router();

  // Is the process alive? Cheap, no dependencies.
  router.get("/live", (_req, res) => res.json({ status: "ok" }));

  // Should we get traffic? Check what we can't work without.
  router.get("/ready", async (_req, res) => {
    if (deps.isShuttingDown()) return res.status(503).json({ status: "shutting-down" });
    const checks = await Promise.allSettled([
      withTimeout(deps.pool.query("SELECT 1"), 1000),
      withTimeout(deps.queueRedis.ping(), 1000),
    ]);
    const ok = checks.every((check) => check.status === "fulfilled");
    res.status(ok ? 200 : 503).json({ status: ok ? "ready" : "not-ready" });
  });

  return router;
}
```

mounted at `/health`, before the rate limits and auth.

1. **Liveness doesn't check the database.** If Postgres is down, restarting the API won't fix Postgres; it'll just restart every API container, over and over, at the worst time. Liveness asks only "is this process able to answer at all?". It fails when the process is truly stuck, and a restart is the right medicine.
2. **Readiness checks what we can't serve without**: Postgres and the queue Redis. Not the **cache** Redis: lesson 19 made the app work without it, so a dead cache must not take the API out of service.
3. **Every check has a short timeout.** A health check that hangs is worse than one that fails.
4. **The answers say little.** `ready` or `not-ready`, no error messages, no versions. These routes are reachable, and they shouldn't tell strangers what you run.
5. **Readiness turns false during shutdown**, which is the first step of the next part.

## Step 3: stopping politely
<!-- bite: f0b911d6-1689-42f7-a585-fc6ae6cb4e3d -->

When a new version is deployed, the platform sends each old container `SIGTERM`, waits a while (the grace period), and then kills it. Use that time well. Lesson 18 did this for the worker; now the API, which has more to close: HTTP connections, SSE streams, the gRPC server, two Redis clients, a database pool.

At the end of `api/src/server.ts`:

```ts
let shuttingDown = false;

async function shutdown(signal: string) {
  if (shuttingDown) return;
  shuttingDown = true;
  logger.info({ signal }, "shutting down");

  // If anything hangs, don't hang forever.
  setTimeout(() => {
    logger.error("shutdown took too long, exiting anyway");
    process.exit(1);
  }, config.SHUTDOWN_GRACE_MS).unref();

  // 1. Readiness is now 503. Give the proxy a moment to notice and stop sending us traffic.
  await sleep(5_000);

  // 2. Stop accepting connections; let in-flight requests finish.
  const httpClosed = new Promise<void>((resolve) => httpServer.close(() => resolve()));
  httpServer.closeIdleConnections();
  kitchenStreams.endAll();            // lesson 20: screens reconnect to a healthy server

  // 3. The gRPC server: finish current calls, refuse new ones.
  const grpcClosed = new Promise<void>((resolve) => grpcServer.tryShutdown(() => resolve()));

  await Promise.all([httpClosed, grpcClosed]);

  // 4. Only now close what requests were using.
  await Promise.allSettled([queueRedis.quit(), cacheRedis.quit(), kitchenEvents.close(), pool.end()]);

  logger.info("bye");
  process.exit(0);
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
```

The order is the whole point:

1. **Say "not ready" first, and wait.** The proxy checks readiness every few seconds. Until it notices, it may still send us requests; if we'd already stopped listening, those requests would fail. Five seconds of saying "don't send me more" while still answering is what makes deploys invisible to customers.
2. **Stop listening, finish what's in flight.** `server.close()` stops new connections and calls back when the current ones end. `closeIdleConnections()` closes kept-alive connections that aren't doing anything, which would otherwise keep `close()` waiting. SSE streams never end by themselves, so we end them.
3. **Close the database and Redis last.** Requests still finishing need them.
4. **A deadline for the whole thing.** `unref()` means the timer itself won't keep the process alive. If something hangs, we exit anyway, before the platform's kill.

The grace period must be longer than this: Docker's default is 10 seconds, which is too short for 5 seconds of waiting plus finishing requests. Compose sets it to 30.

## Step 4: a database user that can't drop tables
<!-- bite: 15a1f57f-df7f-4b4d-913d-2fb101337951 -->

Lesson 14 promised: give each part the least power it needs. So far the app has connected as `postgres`, which can do anything: drop every table, read every database, create users. A bug or an SQL injection with those powers is a disaster.

Two database users instead:

1. **`migrator`** owns the schema. Migrations run as it. It can create and change tables.
2. **`mama_put_app`** is what the running API uses. It can read and write rows, and nothing else: no `CREATE`, no `DROP`, no `ALTER`.

`ops/postgres-init/01-users.sh`, run by the Postgres container the first time it starts with an empty volume:

```bash
#!/bin/bash
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-SQL
  CREATE ROLE migrator      LOGIN PASSWORD '${MIGRATOR_PASSWORD}';
  CREATE ROLE mama_put_app  LOGIN PASSWORD '${APP_DB_PASSWORD}';
  CREATE ROLE notifications LOGIN PASSWORD '${NOTIFICATIONS_DB_PASSWORD}';
  CREATE DATABASE mama_put               OWNER migrator;
  CREATE DATABASE mama_put_notifications OWNER notifications;
  REVOKE ALL ON DATABASE mama_put FROM PUBLIC;
  GRANT CONNECT ON DATABASE mama_put TO mama_put_app;
SQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname mama_put <<-SQL
  GRANT USAGE ON SCHEMA public TO mama_put_app;
  ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mama_put_app;
  ALTER DEFAULT PRIVILEGES FOR ROLE migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO mama_put_app;
SQL
```

`ALTER DEFAULT PRIVILEGES` means "every table `migrator` creates from now on, `mama_put_app` may read and write". So new migrations need no extra grants. The notifications user owns its own database and can't connect to `mama_put` at all (lesson 25's rule, enforced by Postgres).

And migrations become **their own step**, run before the new version starts, as `migrator`. The API never runs migrations at start-up: with three copies starting at once, three would try to migrate together, and the app user couldn't anyway.

## Step 5: the Dockerfile
<!-- bite: f03f0191-3e1b-430b-899a-676595983f9b -->

One image per service. The build runs from the top of the monorepo, because each service needs `proto/`, `contracts/` and the shared lockfile.

`api/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1

# 1. Install production dependencies only.
FROM node:24-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
COPY api/package.json api/
COPY notifications/package.json notifications/
COPY contracts/package.json contracts/
RUN npm ci --omit=dev --workspace api

# 2. The image we run.
FROM node:24-slim
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY proto ./proto
COPY contracts ./contracts
COPY api ./api
WORKDIR /app/api
USER node
EXPOSE 3000 50051 9464
CMD ["node", "--import", "@opentelemetry/auto-instrumentations-node/register", "src/server.ts"]
```

Line by line, the decisions:

1. **`node:24-slim`**: Node 24 runs our TypeScript directly, like 23.6 did, and it's a long-term support release. `slim` leaves out tools we don't need, so the image is smaller and has less to attack. Pin it more exactly (`node:24.11-slim`, or a digest) in real use, so builds don't change under you.
2. **Two stages** ([[devops/03-docker/04-multi-stage-builds|multi-stage builds]]). The first installs dependencies; the second copies only the result. Nothing from the install step (npm's cache, build tools) ends up in the final image.
3. **`package.json` files copied before the code.** Docker caches each step. If only your code changed, the `npm ci` step is reused from the cache, and builds take seconds instead of minutes. Copy the code first, and every code change reinstalls everything.
4. **`npm ci --omit=dev --workspace api`**: install exactly what the lockfile says (`ci`, not `install`), without test tools, for the `api` workspace only. `sharp` gets its Linux build, because this runs in Linux.
5. **No build step.** There's nothing to compile: Node runs the `.ts` files. Type *checking* still matters, but it happens in CI (lesson 29), not here.
6. **`USER node`**: don't run as root. The official Node image has a `node` user for exactly this. If someone breaks into the app, they don't get root inside the container.
7. **`CMD ["node", ...]`**, in brackets (the "exec form"). Node is then the main process and receives `SIGTERM` directly. `CMD npm start` would put npm in between, and npm doesn't reliably pass signals on, so your polite shutdown would never run.
8. **The OpenTelemetry `--import` is in the command**, so tracing is loaded before the app, as lesson 27 required.

And `.dockerignore` at the top, so the build never copies things it shouldn't:

```text
**/node_modules
**/.env
**/.env.*
!**/.env.example
.git
**/uploads
**/*.test.ts
**/test
```

The `.env` lines matter most: without them, `COPY api ./api` would copy your local secrets into the image, and anyone who gets the image gets them.

`notifications/Dockerfile` is the same with `notifications` in place of `api`, `EXPOSE 9465`, and `src/main.ts`. The worker doesn't need its own image: it's the API image with a different command.

## Step 6: the whole system in Compose
<!-- bite: d95ed002-70c1-4f76-a954-e428881bec07 -->

`compose.yaml`, at the top of `mama-put/`:

```yaml
name: mama-put

x-app: &app
  init: true
  restart: unless-stopped
  stop_grace_period: 30s
  env_file: [.env]

services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
      MIGRATOR_PASSWORD: ${MIGRATOR_PASSWORD:?}
      APP_DB_PASSWORD: ${APP_DB_PASSWORD:?}
      NOTIFICATIONS_DB_PASSWORD: ${NOTIFICATIONS_DB_PASSWORD:?}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./ops/postgres-init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10

  queue-redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes", "--maxmemory-policy", "noeviction"]
    volumes: [queuedata:/data]
    healthcheck: { test: ["CMD", "redis-cli", "ping"], interval: 5s }

  cache-redis:
    image: redis:7
    command: ["redis-server", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru", "--save", ""]

  migrate:
    build: { context: ., dockerfile: api/Dockerfile }
    command: ["node", "src/db/migrate.ts"]
    environment:
      DATABASE_URL: postgres://migrator:${MIGRATOR_PASSWORD}@postgres:5432/mama_put
    depends_on:
      postgres: { condition: service_healthy }
    restart: "no"

  api:
    <<: *app
    build: { context: ., dockerfile: api/Dockerfile }
    environment:
      DATABASE_URL: postgres://mama_put_app:${APP_DB_PASSWORD}@postgres:5432/mama_put
      QUEUE_REDIS_URL: redis://queue-redis:6379
      CACHE_REDIS_URL: redis://cache-redis:6379
      OTEL_SERVICE_NAME: api
      OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4318
    ports: ["127.0.0.1:3000:3000"]
    volumes: [photos:/app/api/uploads/photos]
    depends_on:
      migrate: { condition: service_completed_successfully }
      queue-redis: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health/ready').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]
      interval: 10s
      start_period: 20s

  worker:
    <<: *app
    build: { context: ., dockerfile: api/Dockerfile }
    command: ["node", "--import", "@opentelemetry/auto-instrumentations-node/register", "src/worker.ts"]
    environment:
      DATABASE_URL: postgres://mama_put_app:${APP_DB_PASSWORD}@postgres:5432/mama_put
      QUEUE_REDIS_URL: redis://queue-redis:6379
      CACHE_REDIS_URL: redis://cache-redis:6379
      OTEL_SERVICE_NAME: api-worker
      OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4318
    volumes: [photos:/app/api/uploads/photos]
    depends_on:
      migrate: { condition: service_completed_successfully }

  notifications:
    <<: *app
    build: { context: ., dockerfile: notifications/Dockerfile }
    environment:
      DATABASE_URL: postgres://notifications:${NOTIFICATIONS_DB_PASSWORD}@postgres:5432/mama_put_notifications
      QUEUE_REDIS_URL: redis://queue-redis:6379
      API_GRPC_URL: api:50051
      OTEL_SERVICE_NAME: notifications
      OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger:4318
    depends_on:
      queue-redis: { condition: service_healthy }

  jaeger:
    image: jaegertracing/jaeger
    ports: ["127.0.0.1:16686:16686"]

  prometheus:
    image: prom/prometheus
    volumes: ["./ops/prometheus.yml:/etc/prometheus/prometheus.yml:ro"]
    ports: ["127.0.0.1:9090:9090"]

volumes:
  pgdata:
  queuedata:
  photos:
```

What it's doing:

1. **Every service finds the others by name.** Inside Compose's network, `postgres`, `queue-redis` and `api` are host names. Notifications reaches the API's gRPC server at `api:50051`. (`ops/prometheus.yml` now scrapes `api:9464` and `notifications:9465` instead of `host.docker.internal`.)
2. **Only what must be reachable is published**, and only on `127.0.0.1` for now: the API's port 3000, and the dashboards for you. Postgres, both Redis servers, gRPC (50051) and the metrics ports (9464, 9465) aren't published at all; only other containers can reach them. That's lesson 22's "never expose gRPC" and lesson 27's "metrics are internal", done by the network. In lesson 29, a proxy in front takes over port 443 and even 3000 stops being published.
3. **The start-up order is written down.** `migrate` waits for Postgres to be healthy, runs, and exits. `api` and `worker` wait for `migrate` to *finish successfully*. A failed migration means the new version never starts, which is exactly what you want.
4. **Passwords come from `.env`**, which is never committed. `${POSTGRES_PASSWORD:?...}` makes Compose refuse to start if it's missing: the same "fail fast" as `loadConfig`, one level up.
5. **`x-app: &app`** is a block of shared settings, merged into each app service with `<<: *app`: `init: true` (a tiny init process that passes signals on and cleans up), `restart: unless-stopped`, the 30-second grace period, and the shared `.env`.
6. **Volumes** keep data when containers are replaced: the databases, the queue, and the photos.

**About photos.** A Docker volume works on one server. With two servers, each has its own volume, and half the photos go missing. Real deployments put uploads in **object storage** (Amazon S3, Cloudflare R2, or MinIO, which you can run yourself; see [[devops/minio-guide|MinIO]]). The menu photo code from lesson 14 and the worker from lesson 18 would then read and write through an S3 client instead of the file system. One server with a volume is fine for Mama Put today; know that it's the first thing to change when you add a second.

**About TLS between services** (lesson 26): mount the certificate files into the `api` and `notifications` containers as read-only volumes, and point their config at the paths. The private keys are secrets, so they come from the same place as `.env`, never from the image.

## Step 7: running it
<!-- bite: 42732122-eb23-4e91-bd9d-8a2a856834f8 -->

```bash
cp .env.example .env          # then fill in real values
docker compose up -d --build
docker compose ps
```

`ps` should show `postgres`, both Redis servers and the app services as running and (where they have checks) healthy, and `migrate` as exited with code 0.

Useful commands:

```bash
docker compose logs -f api notifications     # follow the JSON logs (pipe through npx pino-pretty to read)
docker compose exec postgres psql -U postgres mama_put
docker compose run --rm migrate               # run migrations again, after adding one
docker compose up -d --build api              # rebuild and replace just the API
docker compose down                           # stop everything (volumes are kept)
```

Now test the shutdown: send some requests in a loop, run `docker compose restart api`, and check that none of them failed. Then test the config check: remove `JWT_SECRET` from `.env`, `docker compose up -d api`, and read `docker compose logs api`.

## The TypeScript in this lesson
<!-- bite: b15a3923-42c3-4717-83b4-e72c0028f218 -->

1. **`z.coerce.number()`**: Converts the input with `Number(...)` before checking it, so the text `"3000"` becomes `3000`.
2. **`.transform((value) => value.split(",")...)`** then **`.pipe(z.array(z.url()).min(1))`**: `transform` changes the value; `pipe` sends the changed value into another schema to check it. Together: "a comma-separated string that must become at least one valid URL".
3. **`ctx.addIssue(...)` and `return z.NEVER`**: Inside a `transform` or `superRefine`, `ctx.addIssue` reports a problem. `z.NEVER` is a value of type `never`, returned after reporting, so TypeScript knows nothing useful comes out.
4. **`.superRefine((config, ctx) => {...})`**: A check that runs after the whole object passes, so it can compare fields with each other.
5. **`z.record(z.string(), z.string())`**: An object with any string keys and string values, like `{ "notifications": "-----BEGIN..." }`.
6. **`env: NodeJS.ProcessEnv = process.env`**: The parameter's type is Node's type for environment variables, and it defaults to the real environment. Tests pass their own object instead.
7. **`issue.path.join(".") || "(config)"`**: Each issue's path is a list like `["PAYSTACK_SECRET_KEY"]`. `||` gives a fallback label when the path is empty.
8. **`Promise.allSettled([...])`**: Like `Promise.all`, but waits for every promise to finish whether it succeeds or fails, and tells you which did which. Right for health checks and shutdown, where one failure shouldn't stop us looking at the others.
9. **`setTimeout(...).unref()`**: `unref()` tells Node this timer alone shouldn't keep the program running. If everything else closes, Node exits without waiting for it.
10. **`new Promise<void>((resolve) => httpServer.close(() => resolve()))`**: Turns a callback into something we can `await`, as in lesson 22.

## Your project so far
<!-- bite: 23eb40ed-915f-4722-988a-66966afacefb -->

```text
mama-put/
├── compose.yaml                         ← NEW: the whole system: databases, Redis ×2, migrate, api, worker,
│                                          notifications, Jaeger, Prometheus
├── .env.example                         ← NEW: every Compose-level setting, no real values
├── .dockerignore                        ← NEW: no node_modules, no .env, no tests in images
├── ops/
│   ├── postgres-init/01-users.sh        ← NEW: migrator, mama_put_app, notifications; databases; grants
│   └── prometheus.yml                   ← scrapes api:9464 and notifications:9465
├── package.json · package-lock.json · proto/ · contracts/
├── api/
│   ├── Dockerfile                       ← NEW: two stages, slim, non-root, exec-form CMD
│   └── src/
│       ├── config.ts                    ← NEW: every setting, checked; fails fast with a clear list
│       ├── health.ts                    ← NEW: /health/live, /health/ready (db + queue redis; not cache)
│       ├── server.ts                    ← loadConfig first; graceful shutdown in order
│       ├── worker.ts                    ← loadConfig; shutdown from lesson 18
│       └── ...                          ← no file reads process.env any more
└── notifications/
    ├── Dockerfile                       ← NEW
    └── src/config.ts · src/health.ts    ← NEW: its own settings and checks
```

## Common mistakes
<!-- bite: b9cdda80-056b-460d-b29b-95b2db91ec66 -->

1. **Reading `process.env` all over the code.** Missing settings fail later, somewhere confusing. One config file, checked at start-up.
2. **Defaults for secrets.** `JWT_SECRET ?? "dev-secret"` ships to production one day. Secrets have no defaults.
3. **Printing config values in errors or logs.** That's how secrets leak. Print names and problems.
4. **Liveness that checks the database.** Postgres goes down, and the platform restarts every app container in a loop.
5. **A dead cache making the app "not ready".** It was built to work without it.
6. **Stopping without waiting.** Requests sent before the proxy noticed fail. Say "not ready", wait, then close.
7. **`CMD npm start`.** Signals don't reach Node, and shutdown never runs.
8. **Running as root in the container**, or copying `.env` into the image.
9. **The app connecting as the database owner.** One injection and the tables can be dropped.
10. **Migrations at app start-up.** Several copies race, and a half-applied migration takes everything down.
11. **Publishing every port.** Databases, Redis, gRPC and metrics belong on the internal network only.

## Check your understanding
<!-- bite: 6e0b743b-8e2e-4d43-a3c9-c82fe2db4257 -->

1. Why does `loadConfig` stop the program instead of logging a warning and carrying on?
2. Postgres goes down for a minute. What should liveness and readiness say, and why?
3. In the shutdown, why do we wait 5 seconds *before* closing the HTTP server?
4. Why is the cache Redis left out of the readiness check?
5. Why copy the `package.json` files into the image before the source code?
6. The API connects as `mama_put_app`. An SQL injection gets through somewhere. What can't the attacker do that they could have done as `postgres`?

<details>
<summary>Answers, after your attempt</summary>

1. Because a wrongly configured app that starts anyway fails later, in confusing ways, often with real customers: payments that never verify, logins that never work. Refusing to start, with a list of exactly what's wrong, turns a mysterious outage into a two-minute fix before anyone is affected.
2. Liveness: still OK, because the process is fine and restarting it won't fix Postgres. Readiness: not ready (503), because without Postgres we can't serve requests, so the proxy should send traffic elsewhere (or show an error page) until it's back.
3. The proxy only checks readiness every few seconds. Until it notices we're "not ready", it may still send us requests. If we stopped listening immediately, those would fail. Waiting while answering lets the proxy move traffic away first.
4. The app works without the cache (lesson 19): reads just go to Postgres. Making the cache required for readiness would let a non-essential piece take the whole API out of service.
5. Docker caches each step. Dependencies change rarely; code changes all the time. With the `package.json` files first, a code-only change reuses the cached `npm ci` step and the build is fast.
6. Create, change or drop tables, create users, or touch other databases such as notifications'. They're limited to reading and writing rows in `mama_put`'s tables, which is still bad, but far smaller and easier to recover from.

</details>

## Practice
<!-- bite: 2b88c54c-21cc-4326-8849-953a8a77d4b1 -->

1. Write `config.ts` for both services, and remove every other use of `process.env`. Add a test that `loadConfig` rejects a test Paystack key in production, without exiting the test runner (make `loadConfig` throw, and let `server.ts` turn that into the exit).
2. Write `health.ts` for notifications: live, and ready when its database and Redis answer.
3. Finish the API's shutdown, including `kitchenStreams.endAll()`, and check it with the restart-under-load test from step 7.
4. Build both images and look at their sizes (`docker images`). Then remove `.dockerignore` and build again, and see what changed (and check whether your `.env` got in).
5. Add a `restore-check` to your notes: back up the database with `docker compose exec postgres pg_dump`, and restore it into a fresh database. A backup you've never restored isn't a backup.

**Done when** `docker compose up -d --build` on a clean machine starts everything in order, with migrations run once by `migrator`; a missing secret stops the API with a clear message; stopping the cache Redis leaves the API ready; stopping Postgres makes it not ready but doesn't restart it; `docker compose restart api` under a stream of requests fails none of them; and from outside the machine, only port 3000 (and nothing else) answers.

## Before moving on
<!-- bite: 5466ba1b-5f35-46ce-8d96-0854920bfd79 -->

Mama Put is now a set of images and one `compose.yaml`. Anyone with Docker can start the whole system, the same way every time, with settings checked, health reported, shutdowns clean, and only one door open.

But it still only runs where *you* type `docker compose up`. Nothing checks that tests pass before something is built. Nothing builds images automatically, keeps old versions to go back to, or puts the new one on a real server with HTTPS. And when a change goes wrong in production, "how do I undo this, right now?" needs an answer you've practised. That's the last lesson: CI and deployment.

## Related
<!-- bite: 0d23dc6f-b5c4-4f10-ac86-365802c44140 -->

- [[backend/frameworks/express/29-ci-and-deployment|Next: CI and Deployment]]
- [[devops/03-docker/index|Docker]] — images, containers, networks and volumes in more depth
- [[devops/06-secret-management/index|Secret Management]] — where `.env` values should really come from
- [[backend/frameworks/express/14-security|Security]] — least power, here applied to the database user

## About this lesson
<!-- bite: 35deaaf6-cf03-4c75-b139-a35424c26de1 -->

**Level:** Advanced. Lesson 28 of [[backend/frameworks/express/index|Express]]. Covers loading every setting once with zod, coercion, safe defaults, cross-field checks with `superRefine`, failing fast without printing values, liveness versus readiness and what each should check, graceful shutdown in order (not ready, wait, stop listening, finish requests, end streams, stop gRPC, close Redis and Postgres, a hard deadline), separate migrator and app database users with default privileges, migrations as their own step, a two-stage Dockerfile for a monorepo with cached dependency installs, a non-root user and exec-form `CMD`, `.dockerignore`, a Compose file with health checks, start-up order, migrations that gate the app, internal-only ports, shared settings, volumes, object storage for photos, and running and testing the whole system.
