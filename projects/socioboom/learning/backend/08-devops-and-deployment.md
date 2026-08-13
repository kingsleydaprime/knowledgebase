# SocioBoom Backend — Docker, Deployment & Production War Stories

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/04-auth-and-security.md` (secret management in deployed environments),
`learning/backend/05-queues-and-jobs.md` (the worker process that deployment has to keep alive), and
`learning/backend/03-database-prisma.md` (running migrations against a hosted database).

This file covers: the multi-stage Dockerfile and the dev/production compose files, and the
production war stories — the worker that silently never ran, intermittent 502s, and the CORS
misconfiguration — each with the actual symptom, the actual diagnosis, and the fix.

---

## 18. Docker: Dev and Production Stages

The `Dockerfile` uses multi-stage builds — a feature that lets you have different stages in one file, each building on or copying from previous stages.

```dockerfile
# Stage 1: base — install dependencies and generate Prisma client
FROM node:22-alpine AS base
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile    # Exact versions from lockfile
COPY . .
RUN npx prisma generate               # Generate TypeScript client from schema

# Stage 2: dev — extends base, runs ts-node directly
FROM base AS dev
ENV NODE_ENV=development
CMD ["pnpm", "dev"]                   # ts-node src/app/main.ts

# Stage 3: builder — compile TypeScript to JavaScript
FROM base AS builder
RUN pnpm build                        # tsc → dist/

# Stage 4: production — lean image with only runtime files
FROM node:22-alpine AS production
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod  # Only production dependencies (no TypeScript, nodemon, etc.)
COPY --from=builder /app/dist ./dist       # Compiled JavaScript
COPY --from=builder /app/prisma ./prisma   # Schema for migrations
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma  # Generated Prisma client
ENV NODE_ENV=production
EXPOSE 3001
CMD ["node", "dist/app/main.js"]           # Run compiled JavaScript
```

**Why multi-stage?** The production image is much smaller than the dev image because:
- It does not contain TypeScript, ts-node, nodemon (dev-only tools)
- It does not contain TypeScript source files
- It does not contain test files or documentation

A smaller image starts faster, uses less memory, and has a smaller attack surface.

**Why `--frozen-lockfile`?** This flag makes pnpm fail if the lockfile is out of date with `package.json`. In CI/CD, this ensures the exact same dependency versions are installed every time — reproducible builds.

**Why `node:22-alpine`?** Alpine Linux is a minimal Linux distribution. The Alpine-based Node.js image is about 100MB vs 800MB for the full Debian-based image. For a production server, smaller is better.

---


## 29. Deployment War Stories: The Worker That Never Ran, 502s, and CORS

### The worker that never ran

`worker.ts` existed, compiled, and was completely correct — and **nothing anywhere started it**. No npm script, Dockerfile `CMD` ran only the API, fly.toml had one process, compose had no worker service. Every scheduled post would have silently never published.

The checklist that fixed it (memorize this — it applies to any app with a background process):

| Layer | Fix |
|---|---|
| package.json | `"dev:worker": "nodemon --exec 'ts-node ... src/worker.ts'"`, `"start:worker": "node dist/worker.js"` |
| worker itself | `import 'dotenv/config'` at the top — standalone processes don't inherit the API's dotenv call |
| compose (dev + prod) | a `worker` service: same image, `command: node dist/worker.js` |
| fly.toml | `[processes]` block with `app` and `worker` entries |
| Railway | second service from the same repo, custom start command `node dist/worker.js` |

The subtle architecture point: platforms auto-stop idle HTTP machines (`min_machines_running = 0`). A *scheduler* cannot live in a machine that sleeps — the 9 a.m. post needs something awake at 9 a.m. Workers, having no HTTP service, are kept running continuously. That's why worker-as-separate-process isn't just tidiness; it's what makes scheduled delivery actually work.

### Health checks on a background worker

Railway health-checked the worker at `/health` → `service unavailable` × 11 → "1/1 replicas never became healthy!" Diagnosis: **the worker had no HTTP server at all.** Nothing was broken except the expectation.

Two valid fixes: remove the health check path (workers don't need one), or add a liveness endpoint so the platform can genuinely tell you the worker died. We chose the endpoint, with an env-gated bind so it can't collide with the API's port from a shared `.env` in local dev:

```ts
const healthPort = process.env.WORKER_HEALTH_PORT
  ?? (process.env.NODE_ENV === 'production' ? process.env.PORT : undefined);
if (healthPort) {
  http.createServer((_req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'worker' }));
  }).listen(Number(healthPort));
}
```

### Anatomy of a 502

`OPTIONS /api/v1/auth/signup → 502` after **31 seconds**. The duration is the diagnostic: ~30 s is an edge proxy timing out trying to *connect*. The request never reached Express — so it's not CORS, not the route, not auth. It's "nobody is listening where the proxy is knocking."

The cause was a three-way port disagreement:

```
main.ts:      app.listen(process.env.PORT || 5000)   ← code default
Dockerfile:   EXPOSE 3001                             ← what Railway detected as target
Railway env:  (no PORT variable set)                  ← so the app bound 5000
```

Proxy targets 3001, app listens on 5000 → 502. Fix: make them agree (default changed to 3001, `PORT=3001` set explicitly, domain target port checked). Rule: **the port in your logs' "listening on" line must equal the port your platform's domain targets.** Check both, every deploy.

### CORS is configuration, not just middleware

The `cors` package was installed and active the whole time — the browser error ("No 'Access-Control-Allow-Origin' header") happened because the middleware was configured to allow only `FRONTEND_URL`, which was unset in production and defaulted to `localhost:3000`. The Vercel origin didn't match, so the header was simply never sent.

Reading the two errors apart:
- **CORS error, fast** → server responded, origin not allowed → fix the allowlist/env var.
- **`net::ERR_FAILED` / 502, slow** → server never responded → fix ports/process, CORS is irrelevant.

The upgraded config accepts a comma-separated allowlist (production + previews + local):

```ts
const allowedOrigins = (process.env.FRONTEND_URL || "http://localhost:3000")
  .split(",").map((o) => o.trim().replace(/\/$/, "")).filter(Boolean);

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) return callback(null, true);
    return callback(new Error(`Origin ${origin} not allowed by CORS`));
  },
  credentials: true,
}));
```

Details that bite: origins must match **exactly** (no trailing slash — hence the `replace(/\/$/, "")`), and `!origin` allows non-browser clients (curl, server-to-server, health checks) that send no Origin header.

---

*This guide covers the entire SocioBoom backend. Use it as both a learning resource and a reference manual. The patterns here — module structure, Prisma queries, BullMQ jobs, AI abstraction, agent loops, Reddit OAuth — repeat throughout the codebase. Master one module and the rest follow the same logic.*

