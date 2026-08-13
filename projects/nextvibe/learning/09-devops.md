# NextVibe — DevOps, Deployment & Infrastructure

Split out from the original flat `learning.md` (moved to `learning/archive/`). See also
`learning/00-sys-design.md`, `learning/backend/01-core.md`, `learning/backend/03-modules.md`,
`learning/backend/02-auth.md`, `learning/backend/05-realtime.md`, and `learning/backend/04-games-ai.md`
for the rest of the backend material, and `learning/frontend/*.md` for the frontend side.

This file covers: deploying to Render (build pipelines, `package.json` mistakes that break CI),
local development environment problems (the inotify `ENOSPC` error), reading server startup logs
for problems, robust process error handling (signals, graceful shutdown), MinIO/object-storage
configuration and the Cloudflare R2 migration path, how presigned URL signatures work, the
dev/prod environment-variable split that always catches people out, and a production
out-of-memory incident from AI generation on a memory-constrained Render instance.

---

## Part 24 — Deploying to Production: CI/CD, Build Pipelines, and the Mistakes That Break Them

Deploying is the step where your working local code becomes a running server that real users hit. It fails in ways that are invisible locally, for reasons that feel baffling until you understand the concepts. This part explains those concepts using the actual production failure this project experienced.

---

### What Happens When You Deploy to Render (or Any Cloud Host)

When you push to your repo and Render picks it up, it:

1. Clones your repository onto a fresh machine — a machine that has nothing installed except the OS, Node, and the tools Render provides
2. Runs your **Build Command** — the commands that turn your TypeScript source into runnable JavaScript
3. Runs your **Start Command** — the command that starts the server

The key insight: **the build machine is a blank slate.** It does not have your local `node_modules`. It does not inherit your local environment. Every tool your build process needs must be installed from scratch.

---

### What `--frozen-lockfile` Means and Why It Exists

When you run `pnpm install` locally, pnpm reads `package.json`, resolves versions, downloads packages, and writes a snapshot of every resolved version to `pnpm-lock.yaml`. This lockfile is the exact recipe for the installation.

`--frozen-lockfile` tells pnpm: "Do not update the lockfile. If the lockfile and `package.json` are out of sync, fail immediately."

**Why does CI/CD use `--frozen-lockfile`?**

Without it, if a developer forgot to commit an updated lockfile, the CI machine would silently re-resolve packages — potentially installing different versions than what was tested locally. A bug could exist only in production because production got a slightly different package. `--frozen-lockfile` makes "lockfile matches package.json" a hard requirement. The build fails loud and early rather than silently installing the wrong thing.

**The rule:** always commit your lockfile. Always. Every `package.json` change must be followed by `pnpm install` and a commit of the updated `pnpm-lock.yaml`.

---

### Bug #1: `pnpm` in `dependencies` → Worker Exits With Code 1

The project had this in `package.json`:

```json
"dependencies": {
  ...
  "pnpm": "^11.1.2",
  ...
}
```

This caused the build to crash immediately with `Worker pnpm#1 exited with code 1`.

**Why?**

`pnpm` is a package manager — a CLI tool that manages packages. It is not a library your app imports. When you put it in `dependencies`, the running pnpm process tries to install... pnpm itself. The pnpm package has its own postinstall lifecycle scripts that try to register itself as a package manager, which conflicts with the already-running pnpm process. The worker crashes.

**The correct approach:** package managers, build tools, and CLI utilities that you don't `import` in your code do not belong in `dependencies`. They belong in one of:

| Where | What it means |
|---|---|
| `devDependencies` | Used during development/build, not at runtime |
| `engines` field | Declares the minimum version required, doesn't install anything |
| `packageManager` field | Declares the exact package manager used (Node.js Corepack feature) |

For this project, pnpm was removed from `dependencies` entirely. The correct way to declare "this project uses pnpm 11" is:

```json
"engines": {
  "node": ">=20.0.0",
  "pnpm": ">=11.0.0"
}
```

Or with Corepack:

```json
"packageManager": "pnpm@11.1.2"
```

Neither of these installs pnpm — they're just documentation constraints. pnpm is already installed globally on the build machine.

**Lesson:** `dependencies` are packages your app imports at runtime. `devDependencies` are packages used during development and build. Never put a CLI tool, package manager, or build tool in `dependencies` unless your app literally `import`s it.

---

### Bug #2: `nest: not found` → `NODE_ENV=production` Skipping DevDependencies

Even if the install succeeded, the build would then fail with:

```
sh: 1: nest: not found
```

`nest` is the NestJS CLI. It's what runs `nest build` to compile TypeScript. It's in `devDependencies`:

```json
"devDependencies": {
  "@nestjs/cli": "^11.0.0",
  ...
}
```

**Why wasn't it installed?**

Render (like most cloud hosts) sets `NODE_ENV=production` during the build. When `NODE_ENV=production`, pnpm's default behaviour is to skip `devDependencies` — because on a production server, you don't want dev tools like test runners, type checkers, and linters installed. It saves disk space and install time.

The problem: **your build tools live in devDependencies, but the build runs in production mode.**

This is a genuine tension in Node.js tooling. There are two ways to resolve it:

**Option A: Add `--prod=false` to the install command (used here)**

```
pnpm install --frozen-lockfile --prod=false
```

`--prod=false` explicitly tells pnpm "ignore `NODE_ENV`, install devDependencies too." This ensures `@nestjs/cli`, `typescript`, `ts-node`, `prisma` (the CLI, not `@prisma/client`) and all other build tools are available during the build step.

**Option B: Move build tools to `dependencies`**

Some teams move `@nestjs/cli` and `typescript` to regular `dependencies`. This works but is semantically wrong — these tools are not used by the running server, they're only used to compile it. Mixing them into `dependencies` bloats your production node_modules.

Option A is cleaner. The full Render build command for this project:

```
pnpm install --frozen-lockfile --prod=false; pnpm run db:deploy; pnpm dlx prisma generate; pnpm run build
```

---

### Understanding the Full Build Command

Let's break down each step:

```
pnpm install --frozen-lockfile --prod=false
```
Install all dependencies (including dev). Fail if lockfile is out of sync.

```
pnpm run db:deploy
```
Runs `prisma migrate deploy` — applies any pending database migrations. The `db:deploy` script in this project first uses `prisma migrate resolve --applied` to mark some historical migrations as already-applied (because they were manually applied and Prisma's migration history doesn't know about them), then runs `deploy` to apply anything new. This ensures the database schema matches the code before the code starts.

```
pnpm dlx prisma generate
```
Generates the Prisma Client TypeScript types from the schema. The generated client lives in `src/generated/prisma`. Without this step, `@prisma/client` has no types and the app can't compile. Note: `pnpm dlx` runs a command from a remote package without installing it globally — it's like `npx` for pnpm.

```
pnpm run build
```
Runs `nest build`, which uses the NestJS CLI to invoke the TypeScript compiler (tsc) and output JavaScript to `dist/`. This is the compiled server that will actually run.

---

### Why `@prisma/client` Is Listed in `dependencies` But Still Needs `prisma generate`

`@prisma/client` in `dependencies` installs the runtime client library — the JavaScript code that connects to Postgres and runs queries. But the actual TypeScript types and the generated client code are specific to your schema. They live in `src/generated/prisma` and are produced by `prisma generate`.

Without running `prisma generate`, your code can import `@prisma/client` but will get no type information and no client tailored to your schema. This is why `prisma generate` must always run as part of the build, not just when you change the schema.

The `prisma` CLI package (which runs `generate`) is in `devDependencies`. It's needed at build time, not at runtime. The `@prisma/client` package (runtime) is in `dependencies`. Two different packages, two different purposes.

---

### The `postbuild` Script: Copying Generated Files

```json
"postbuild": "pnpm run copy:prisma"
```

`copy:prisma` does:
```bash
mkdir -p dist/src/generated && cp -r src/generated/prisma dist/src/generated/
```

NestJS compiles TypeScript to `dist/`. But the Prisma-generated files in `src/generated/` are already JavaScript (generated by Prisma, not by you). `tsc` doesn't necessarily copy them into `dist/`. The `postbuild` step manually copies the generated client into the `dist/` folder so the compiled server can find it at runtime.

**The `post` prefix:** in npm/pnpm scripts, any script prefixed with `post` automatically runs after the matching script. `postbuild` runs after `build`. `pretest` would run before `test`. This is a built-in convention, not a custom feature.

---

### How to Debug a Failed Production Build

When a build fails in CI/CD, here is the process:

1. **Read the exact error message.** "Worker pnpm#1 exited with code 1" means a pnpm child process crashed. "nest: not found" means a binary isn't in PATH. "Could not resolve @prisma/client" means Prisma wasn't generated.

2. **Map the error to the step that caused it.** Build commands run sequentially. If step 1 fails, step 2 never runs. In this case, the `pnpm install` worker crash meant prisma and nest also failed — not because they had their own problems, but because the install never completed.

3. **Check `package.json` and `pnpm-lock.yaml` for inconsistencies.** Is a package in the wrong section? Is the lockfile behind? Does `package.json` have something that doesn't belong?

4. **Check whether `NODE_ENV` affects the build.** If your build host sets `NODE_ENV=production`, know that this changes install behaviour.

5. **Reproduce locally with the same flags.** Run `NODE_ENV=production pnpm install --frozen-lockfile` locally. If it fails the same way, you've reproduced it and can iterate faster than pushing and waiting for CI.

6. **Work top to bottom.** Fix the first error, see what happens next. Don't try to fix all errors at once — they may be cascading from a single root cause.

---

### Summary: What to Never Do in `package.json`

| Mistake | Why It Breaks |
|---|---|
| Put a package manager (`pnpm`, `npm`, `yarn`) in `dependencies` | Postinstall lifecycle conflicts; package managers manage other packages, not themselves |
| Put build-only tools in `dependencies` | Bloats production node_modules with unused tools |
| Forget to commit `pnpm-lock.yaml` after changes | `--frozen-lockfile` fails; CI installs different versions than local |
| Use `pnpm install --frozen-lockfile` without `--prod=false` on a host that sets `NODE_ENV=production` | devDependencies (including CLI tools) are skipped; build fails |

---

## Part 25 — Development Environment Problems and How to Solve Them

These are errors that happen on your local machine during development, not in production. They feel catastrophic the first time you see them. Once you understand what they mean, they take less than a minute to fix.

---

### `ENOSPC: System limit for number of file watchers reached`

**The full error:**

```
Error: ENOSPC: System limit for number of file watchers reached,
watch '/home/.../src/generated/prisma/wasm-edge-light-loader.mjs'
    at FSWatcher.<computed> (node:internal/fs/watchers:247:19)
    ...
  errno: -28,
  code: 'ENOSPC',
```

**What you were doing when it appeared:** Running `pnpm run start:dev` — the NestJS watch mode compiler. Everything compiled fine (`Found 0 errors. Watching for file changes.`), then the process crashed.

**Why `ENOSPC` is misleading:** `ENOSPC` stands for "No Space on Device." Your first instinct is to check disk space. That's wrong. This error has nothing to do with disk space. It's about a Linux kernel resource called **inotify**.

**What inotify is:**

Linux uses a kernel subsystem called `inotify` to implement file watching. When a program wants to know when a file changes, it asks the kernel to "watch" that file. The kernel maintains a list of all active watches across all processes on the machine.

By default, Linux caps this list at **65,536 watches total** across all processes. When the cap is hit, the error code is `ENOSPC` — because the kernel reports "no space" in the watch table, even though your disk is fine.

**Why this project hits the limit:**

The NestJS watch mode compiler (via `chokidar`) registers an inotify watch on every file it monitors. This project has a `src/generated/prisma/` directory containing many generated files from Prisma. Combined with the rest of `src/`, `node_modules/.pnpm/`, and any other projects or editors you have open on the same machine (VS Code alone consumes thousands of watches), the total exceeds 65,536.

**How to check the current limit:**

```bash
cat /proc/sys/fs/inotify/max_user_watches
# outputs: 65536
```

**The fix — increase the limit permanently:**

```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

`/etc/sysctl.conf` is the kernel parameter configuration file. Changes here survive reboots. `sysctl -p` reloads the file immediately without rebooting. After this, the limit is 524,288 — eight times the default, more than enough for any development machine.

**For an immediate fix without rebooting (does not survive reboot):**

```bash
sudo sysctl fs.inotify.max_user_watches=524288
```

**Why 524,288?** It is the standard recommended value in the documentation for VS Code, Webpack, Jest, and other watch-heavy tools. It's high enough that you will never hit the ceiling in normal development, while still being a finite cap that prevents a runaway process from consuming unlimited kernel resources.

**After applying the fix:** Restart `pnpm run start:dev`. The error will not appear again.

**Key lesson:** `ENOSPC` in Node.js file watcher errors does not mean disk space. It means a kernel resource table is full. Always check the full error message — `code: 'ENOSPC'` combined with `syscall: 'watch'` is the giveaway that it's inotify, not disk.

---

## Part 31 — Reading Server Startup Logs to Detect Problems Before They Bite

### What the Startup Logs Tell You

Every time NestJS starts, `RouterExplorer` prints every registered route:

```
[RouterExplorer] Mapped {/v1/admin/coupons, POST} route
[RouterExplorer] Mapped {/v1/admin/coupons, POST} route   ← same route twice
```

Two lines for the same route is a red flag. It means two controllers are registered at the same path. As covered in `learning/backend/01-core.md` (Part 27 — Duplicate Controller Routes), NestJS silently uses the first one and ignores the second. This log is your only warning — there is no error at runtime.

### Subtle Path Param Naming Differences

```
[RouterExplorer] Mapped {/v1/events/:id/rsvp, POST} route
[RouterExplorer] Mapped {/v1/events/:eventId/rsvp, POST} route
```

These look different (`:id` vs `:eventId`) so NestJS registers both. But they match the same incoming URLs — `/v1/events/abc/rsvp` matches both. The first one registered wins every request. The second controller's handler is dead code. You won't see an error. You'll see the wrong service being called.

**How to catch it:** After adding a new controller or route, scan the startup logs for:
- Identical path+method pairs (exact duplicates)
- Paths that differ only in param name (`:id` vs `:eventId`) — structurally identical

```bash
# Quick check: count routes, look for duplicates
grep "RouterExplorer.*Mapped" logs.txt | sort | uniq -d
```

### What Else to Watch in Startup Logs

| Log message | What it means |
|---|---|
| `[NestFactory] Starting Nest application...` | Bootstrap started |
| `[InstanceLoader] XModule dependencies initialized` | Module DI wired |
| `[RoutesResolver] XController {/v1/path}` | Controller scope registered |
| `[RouterExplorer] Mapped {/v1/path, METHOD}` | Individual route registered |
| `[NestApplication] Nest application successfully started` | Ready to serve |

If the app hangs between `InstanceLoader` and `RoutesResolver`, a provider constructor is likely blocking (synchronous DB call, infinite loop, missing env var causing a crash). If it hangs after all routes are mapped, the `listen()` call is failing (port in use, permission denied for ports < 1024).

### Reading a 403 from Logs Alongside Prior Events

Production logs tell a story. One example from this codebase:

```
09:26:01  POST /v1/users/A/follow      201   ← user 1 follows user A
09:26:31  POST /v1/users/B/follow      201   ← user 1 follows user B
09:43:50  POST /v1/auth/oauth/google   200   ← user 2 logs in
09:45:19  POST /v1/conversations       403   ← user 2 tries to DM someone
09:46:16  POST /v1/users/X/follow      201   ← user 2 starts following people
09:47:44  POST /v1/users/Y/follow      201
```

The 403 on `/conversations` isn't an auth problem — the user just logged in successfully. It's a **mutual follow** problem. User 2 is trying to DM someone they're not mutually following yet. The follow actions *after* the 403 confirm they're trying to fix it. You can read the sequence of events and understand intent from timestamps alone.

This skill — reading log timelines to understand what a user was doing — is one of the most valuable debugging tools you have in production.

---

## Part 33 — Robust Process Error Handling

### Why the Basic Pattern Is Insufficient

The basic pattern most tutorials show:

```javascript
process
  .on('uncaughtException', (err) => console.error(err))
  .on('unhandledRejection', (err) => console.error(err))
```

has two critical problems:
1. It logs the error but **doesn't exit**. The process continues running in an undefined state after an uncaught exception. The Node.js documentation explicitly says the process should be considered unsafe after `uncaughtException` — memory may be corrupted, async state may be inconsistent.
2. It handles only two events. There are several others that matter in production.

### The Full Set of Process Events That Matter

| Signal / Event | Who sends it | What to do |
|---|---|---|
| `uncaughtException` | Node.js runtime | Log, exit 1 |
| `unhandledRejection` | Node.js runtime | Log, exit 1 |
| `SIGTERM` | Docker, Kubernetes, `kill <pid>` | Graceful shutdown, exit 0 |
| `SIGINT` | Ctrl+C in terminal | Graceful shutdown, exit 0 |
| `SIGHUP` | Terminal closed (Unix) | Graceful shutdown, exit 0 |
| `SIGUSR2` | nodemon (restart) | Cleanup, re-raise signal |
| `warning` | Node.js runtime | Log only, do not exit |

### The Force-Exit Timeout — The Part Everyone Misses

When you call `server.close()` or `app.close()`, you stop accepting **new** connections. But existing connections are allowed to finish. If a long-running request never finishes (e.g., a client that opened a connection and went silent), the server close never completes — the process hangs.

In Docker/Kubernetes, this means the container stays alive until Kubernetes gives up and sends SIGKILL (the nuclear option with no cleanup at all). You want to control this yourself:

```javascript
const timer = setTimeout(() => {
  console.error('Graceful shutdown timed out — forcing exit');
  process.exit(1);
}, 10_000);  // 10 seconds

timer.unref();  // ← this is critical
```

**Why `.unref()`?** A timer with a reference keeps the Node.js event loop alive. If everything else (server, connections) has closed, you want the process to exit naturally — not stay alive waiting for a timeout that should only fire if something went wrong. `.unref()` tells the event loop "don't count this timer as a reason to stay alive." The timer still fires if the process hasn't exited, but it doesn't prevent natural exit.

### SIGUSR2 and nodemon

`nodemon` sends `SIGUSR2` to restart your process during development. If you don't handle it, nodemon still works — but you miss the opportunity to cleanly close DB connections and release resources before the restart. The correct pattern is to clean up and then **re-raise** the signal so nodemon knows the process acknowledged it:

```javascript
process.once('SIGUSR2', async () => {
  await app.close();  // or server.close()
  process.kill(process.pid, 'SIGUSR2');  // re-raise, nodemon proceeds
});
```

Note `process.once` — not `process.on`. nodemon only sends this once. Using `once` avoids accumulating handlers across multiple restarts.

### Plain Node.js Implementation

```javascript
// error-handler.js
function registerProcessErrorHandlers(server) {
  function shutdown(signal, code = 0) {
    console.log(`[${signal}] Shutting down gracefully...`);

    const timer = setTimeout(() => {
      console.error('[shutdown] Timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    server.close((err) => {
      if (err) {
        console.error('[shutdown] Error closing server:', err);
        process.exit(1);
      }
      process.exit(code);
    });
  }

  process.on('uncaughtException', (err) => {
    console.error(`[uncaughtException] ${err.message}\n${err.stack}`);
    process.exit(1);  // always exit — process state is undefined after this
  });

  process.on('unhandledRejection', (reason) => {
    const msg = reason instanceof Error ? reason.stack : String(reason);
    console.error(`[unhandledRejection] ${msg}`);
    process.exit(1);
  });

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));
  process.on('SIGHUP',  () => shutdown('SIGHUP'));

  process.once('SIGUSR2', () => {
    console.log('[SIGUSR2] nodemon restart — closing server');
    server.close(() => process.kill(process.pid, 'SIGUSR2'));
  });

  process.on('warning', (w) => {
    console.warn(`[warning:${w.name}] ${w.message}`);
  });
}

const server = app.listen(3000);
registerProcessErrorHandlers(server);
```

### Express.js — Adding the 4-Argument Error Handler

Express has its own error-handling middleware convention on top of process-level handlers. The key rule: **error middleware must have exactly four parameters**. Express detects error handlers by parameter count — if your function only has 3 parameters, Express treats it as regular middleware.

```javascript
// Must come AFTER all routes and regular middleware
function globalErrorHandler(err, req, res, next) {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  console.error(`[error] ${req.method} ${req.url} — ${status}: ${message}`);

  res.status(status).json({
    success: false,
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message,
      // only expose stack trace in development
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
    },
  });
}

// 404 handler — for routes that don't match anything
function notFoundHandler(req, res) {
  res.status(404).json({
    success: false,
    error: { code: 'NOT_FOUND', message: `Cannot ${req.method} ${req.path}` },
  });
}

app.use(yourRoutes);
app.use(notFoundHandler);    // after routes, before error handler
app.use(globalErrorHandler); // last middleware registered
```

Triggering the error handler from a route:

```javascript
// Express 4 — pass errors to next()
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await db.findUser(req.params.id);
    if (!user) {
      const err = new Error('User not found');
      err.status = 404;
      return next(err);
    }
    res.json(user);
  } catch (err) {
    next(err);
  }
});

// Express 5 / with express-async-errors patch — throw directly
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  if (!user) throw Object.assign(new Error('User not found'), { status: 404 });
  res.json(user);
});
```

### NestJS Implementation

```typescript
// src/common/process-error-handler.ts
import { INestApplication, Logger } from '@nestjs/common';

const logger = new Logger('Process');

export function registerProcessErrorHandlers(app: INestApplication) {
  async function shutdown(signal: string, code = 0) {
    logger.log(`${signal} received — closing application`);

    const timer = setTimeout(() => {
      logger.error('Graceful shutdown timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    await app.close(); // triggers OnApplicationShutdown hooks on all providers
    process.exit(code);
  }

  process.on('uncaughtException', (err: Error) => {
    logger.error(`Uncaught Exception: ${err.message}`, err.stack);
    process.exit(1);
  });

  process.on('unhandledRejection', (reason: unknown) => {
    const message = reason instanceof Error ? reason.stack : String(reason);
    logger.error(`Unhandled Rejection: ${message}`);
    process.exit(1);
  });

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));
  process.on('SIGHUP',  () => shutdown('SIGHUP'));

  process.once('SIGUSR2', async () => {
    logger.log('SIGUSR2 received (nodemon restart)');
    await app.close();
    process.kill(process.pid, 'SIGUSR2');
  });

  process.on('warning', (warning: Error) => {
    logger.warn(`[${warning.name}] ${warning.message}`);
  });
}
```

**Why `app.close()` matters in NestJS:** It calls `OnApplicationShutdown` lifecycle hooks on every provider. This is how you cleanly close database connections, flush message queues, and drain in-flight requests. Without it, those connections leak — Postgres connection pools don't get released, Redis clients stay open, and your next deploy may hit connection limits.

### The Five Rules to Remember

1. **Always exit after `uncaughtException`** — Node.js documentation says the process is in an undefined state. Trying to serve more requests after this is gambling.
2. **Always exit after `unhandledRejection`** — future Node.js versions exit automatically; handle it yourself now.
3. **Always set a force-exit timeout on shutdown signals** — `server.close()` waits for connections to drain; if one hangs, so does your process.
4. **Always call `.unref()` on that timeout** — without it, the timer itself keeps the event loop alive even after everything has closed.
5. **Re-raise `SIGUSR2` after cleanup** — don't exit on it; nodemon needs the re-raised signal to know it can restart.

(See also `learning/backend/01-core.md` for `OnModuleInit` / `OnApplicationShutdown` NestJS lifecycle hooks — `app.enableShutdownHooks()` is required for `SIGTERM`/`SIGINT` to actually trigger these hooks.)

---

## Part 34 — MinIO Configuration: Two URLs, Two Different Jobs

### The Core Confusion

MinIO storage involves two URLs that serve completely different purposes, and mixing them up is one of the most common bugs when deploying:

| Variable | What it is | Who uses it |
|---|---|---|
| `MINIO_ENDPOINT` | The address NestJS uses to talk to MinIO | Your NestJS server (server-to-server) |
| `CDN_BASE_URL` / `MINIO_EXTERNAL_URL` | The address clients use to access stored files | Browsers, mobile apps |

These two can be — and often *are* — different addresses for the same MinIO instance.

### Why They Can Differ

Imagine MinIO running inside a Docker network. Other containers can reach it at `minio:9000` (the internal Docker DNS name). But browsers outside the network need to use `https://files.yourdomain.com`. So:

- `MINIO_ENDPOINT=minio:9000` — NestJS connects here (internal)
- `CDN_BASE_URL=https://files.yourdomain.com/nextvibe` — clients use this (external)

In this codebase, MinIO runs on Railway at `minio-production-5cff.up.railway.app`. NestJS connects to it there, and clients also access files from the same domain. So both values should point to the same Railway domain. The bug was that `CDN_BASE_URL` was left as `http://localhost:9000/nextvibe` — the local dev value — even after MinIO moved to Railway.

### How the Code Resolves the Public Base URL

```typescript
this.publicBaseUrl =
  this.configService.get('MINIO_EXTERNAL_URL') ??   // explicit override wins
  this.configService.get('CDN_BASE_URL') ??          // fallback
  `${protocol}://${host}:${port}/${bucket}`;         // auto-constructed from MINIO_ENDPOINT
```

Priority: `MINIO_EXTERNAL_URL` → `CDN_BASE_URL` → constructed from `MINIO_ENDPOINT`. If you set `CDN_BASE_URL` wrong, you'll get wrong public URLs in every API response. If you set neither, it auto-constructs from `MINIO_ENDPOINT` — which works if your MinIO endpoint is already public-facing.

### The Classic Bug This Produces

```
// .env (production — wrong)
MINIO_ENDPOINT=minio-production-5cff.up.railway.app   ✅ correct
CDN_BASE_URL=http://localhost:9000/nextvibe            ❌ dev leftover

// Result:
uploadUrl = https://minio-production-5cff.up.railway.app/nextvibe/events/file.jpg?X-Amz-...  ✅
fileUrl   = http://localhost:9000/nextvibe/events/file.jpg                                     ❌

// uploadUrl works (browser can upload there)
// fileUrl goes into the database
// Every image/video reference in every API response points to localhost:9000
// No images or videos load in production
```

The `uploadUrl` is generated by the MinIO client (which uses `MINIO_ENDPOINT` — correct). The `fileUrl` is built using `publicBaseUrl` (which uses `CDN_BASE_URL` — wrong). That's why the upload worked but the stored URLs were broken.

### Fix

```
CDN_BASE_URL=https://minio-production-5cff.up.railway.app/nextvibe
```

### Also: MinIO Needs to Know Its Own External URL

MinIO itself has a configuration variable called `MINIO_SERVER_URL`. This tells MinIO what its own public address is — it affects things like presigned URL generation when MinIO is behind a reverse proxy. If MinIO generates presigned URLs using its internal address, and a browser tries to use those URLs, it won't be able to reach MinIO.

On Railway, MinIO's `MINIO_SERVER_URL` should be set to `https://minio-production-5cff.up.railway.app`. This is separate from anything in your NestJS `.env` — it's a MinIO server environment variable.

### Cloudflare R2 as the Migration Path

The root cause of slow uploads on this project is Railway-hosted MinIO: Railway throttles bandwidth and containers cold-start. Cloudflare R2 is the recommended migration target.

R2 is 100% S3-compatible — same API, same SDK, same request format. Migrating requires **only environment variable changes**, no code changes:

```bash
# MinIO on Railway (current)
MINIO_ENDPOINT=minio-production-5cff.up.railway.app
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=your-secret
MINIO_BUCKET_NAME=nextvibe
MINIO_USE_SSL=true
MINIO_PORT=443
CDN_BASE_URL=https://minio-production-5cff.up.railway.app/nextvibe

# Cloudflare R2 (same code, different env vars)
MINIO_ENDPOINT=<account-id>.r2.cloudflarestorage.com
MINIO_ACCESS_KEY=your-r2-access-key-id
MINIO_SECRET_KEY=your-r2-secret-access-key
MINIO_BUCKET_NAME=nextvibe
MINIO_USE_SSL=true
MINIO_PORT=443
CDN_BASE_URL=https://pub-<hash>.r2.dev
```

The `StorageService` (AWS SDK v3 S3 client) and `UploadService` (`minio` npm package) both read from env vars and both are S3-compatible clients — they work with R2 without modification.

**Why R2 is better than Railway-hosted MinIO:**
- $0 egress fees — data transfer out of R2 is free (Railway charges bandwidth per GB)
- No cold starts — R2 is Cloudflare's edge network, always warm
- Better global performance — files served from Cloudflare's CDN edge nodes
- No self-managed instance — Cloudflare handles availability, scaling, backups

**Short-term fix without migrating:** Use `browser-image-compression` on the client side before the XHR upload. A 5 MB photo compresses to ~200–400 KB, making uploads 10–15× faster regardless of the storage backend. This is complementary to R2, not a replacement. (See `learning/frontend/05-uploads-errors.md` for the full client-side compression implementation.)

---

## Part 35 — Presigned URLs: How the Signature Actually Works

### What a Presigned URL Is

A presigned URL is a regular HTTPS URL with an authentication signature embedded in its query parameters. It allows someone (like a browser) to perform a specific S3/MinIO operation *without* having the MinIO credentials. The credentials stay on your server; only the signature goes to the client.

An example presigned PUT URL:

```
https://minio-production-5cff.up.railway.app/nextvibe/events/file.jpg
  ?X-Amz-Algorithm=AWS4-HMAC-SHA256
  &X-Amz-Credential=minioadmin%2F20260522%2Fus-east-1%2Fs3%2Faws4_request
  &X-Amz-Date=20260522T102959Z
  &X-Amz-Expires=900
  &X-Amz-SignedHeaders=host
  &X-Amz-Signature=7270ad47...
```

Breaking this down:
- `X-Amz-Algorithm` — signing algorithm used (HMAC-SHA256)
- `X-Amz-Credential` — who signed it + date + region + service
- `X-Amz-Date` — when the signature was created (ISO 8601)
- `X-Amz-Expires` — how long the URL is valid in seconds (900 = 15 minutes)
- `X-Amz-SignedHeaders` — which request headers are covered by the signature
- `X-Amz-Signature` — the actual cryptographic signature

### What the Signature Covers

The signature is an HMAC-SHA256 hash over:
- The HTTP method (`PUT`)
- The bucket and object key (`/nextvibe/events/file.jpg`)
- The expiry time
- The credentials used

This means:
- You **cannot** change the file path — the signature will be invalid
- You **cannot** use the URL after it expires — MinIO checks the date + expiry
- You **cannot** use it for a different HTTP method (a PUT URL won't work for GET)
- You **can** use it from any IP address — there is no IP binding by default

### The Expiry Window

In this codebase, URLs expire in 15 minutes (`15 * 60 = 900` seconds). This means the frontend must start the upload within 15 minutes of requesting the presigned URL. For large files with slow connections, you may need to increase this. For very sensitive data, keep it short.

### Content-Type Constraint

When generating a presigned URL, you can optionally lock it to a specific Content-Type. If you do, MinIO will reject any PUT that doesn't send exactly that Content-Type header.

In this codebase, `presignedPutObject` is called without a Content-Type — so MinIO accepts any file type. This is flexible but means you can't enforce "only images" at the storage layer. If you want that, you'd need to pass the Content-Type when generating:

```typescript
// Locked to a specific content type (more secure)
const uploadUrl = await this.minioClient.presignedPutObject(
  this.bucketName,
  storageKey,
  expiresSeconds,
  { 'Content-Type': contentType },  // MinIO enforces this
);
```

### Browser CORS: The Hidden Requirement

When a browser sends a `PUT` request to a different domain (like uploading to MinIO from your app at `app.mynextvibe.com`), the browser first sends a **preflight `OPTIONS` request** to check if MinIO allows cross-origin uploads.

MinIO must respond to that `OPTIONS` with the right CORS headers:

```
Access-Control-Allow-Origin: https://app.mynextvibe.com
Access-Control-Allow-Methods: PUT
Access-Control-Allow-Headers: Content-Type
```

If MinIO doesn't have CORS configured, the preflight fails, and the actual `PUT` never happens. The browser shows a CORS error. **This is the most common reason presigned URL uploads work in testing (Postman, curl) but fail in the browser** — because Postman doesn't do CORS preflight.

### Configuring CORS on MinIO

In MinIO, CORS is configured via the MinIO admin console or the `mc` CLI:

```bash
# Using MinIO client (mc)
mc alias set myminio https://minio-production-5cff.up.railway.app minioadmin minioadmin
mc admin config set myminio/ api cors_allow_origin="https://app.mynextvibe.com"
```

Or via MinIO's web console (browser UI at your MinIO domain) → Administrator → Configuration → API → CORS.

For development, you can allow all origins (`*`), but in production, restrict to your actual frontend domain.

(See also `learning/backend/01-core.md` Part 32 for the full backend-side migration from multipart uploads to this presigned-URL flow, and `learning/frontend/05-uploads-errors.md` for the frontend upload implementation.)

---

## Part 38 — Environment Variables: The Dev/Prod Split That Always Catches You

### The Pattern of the Bug

The most common production bug isn't a code bug — it's an env var that was set up for local development and never updated for production. The pattern:

1. During development, you run MinIO locally at `localhost:9000`
2. You set `CDN_BASE_URL=http://localhost:9000/nextvibe` in your `.env`
3. You deploy — MinIO moves to Railway, NestJS moves to Railway
4. You update `MINIO_ENDPOINT=minio-production-5cff.up.railway.app`
5. You forget to update `CDN_BASE_URL`
6. NestJS connects to MinIO correctly (MINIO_ENDPOINT is right)
7. Every file URL stored in the database is `http://localhost:9000/...`
8. No images load in production

The fix is one line. The debugging takes an hour because the upload *succeeds* — the data just isn't right.

### The Rule: Separate Concerns in Your `.env`

Every URL in your `.env` that a **browser or mobile app** will use must point to a public address. Every URL that only your **server** uses can be an internal address. When you deploy, go through every variable and ask: "who uses this URL?"

| Variable | User | Must be public? |
|---|---|---|
| `MINIO_ENDPOINT` | NestJS server | No — can be internal |
| `CDN_BASE_URL` | Browser (image URLs) | **Yes** |
| `DATABASE_URL` | NestJS server | No |
| `WEB_APP_URL` | Used in emails/QR codes sent to users | **Yes** |
| `REDIS_HOST` | NestJS server | No |

### The `.env.example` Contract

`.env.example` is a contract for anyone setting up the project. Every value in it should be a safe placeholder that makes it obvious what the format should be — not a working local value that someone might use as-is in production.

```bash
# Bad — someone copies this to .env, deploys, and it silently uses localhost
CDN_BASE_URL=http://localhost:9000/nextvibe

# Good — obviously a placeholder, no one will use it as-is
CDN_BASE_URL=https://your-minio-host/nextvibe
```

This is why the `.env.example` in this codebase was updated to the generic placeholder form, not the Railway-specific URL — `.env.example` should work for *any* deployment, not be tied to one specific infrastructure.

---

## Part 55 — AI Generation Memory: OOM on Render 512MB

### The Root Cause

`AiGeneratorService` called the OpenRouter API (Gemini 2.5 Flash) with:

```typescript
max_tokens: 60000,
```

The model generates up to 60,000 tokens. Holding a partially-streamed or fully-buffered response of that size in Node.js memory consumes approximately 240MB per AI request (token buffers, JSON parse buffers, intermediate strings). The Render instance has 512MB total — leaving ~270MB for the rest of the application (Prisma connections, cached queries, active sessions). A single AI request combined with normal traffic pushed the process over the limit. Render killed it with an OOM signal.

### The Fix: Per-Game-Type Token Caps

```typescript
const maxTokens = dto.gameType === 'WORD_PUZZLE' ? 8000 : 4000;
```

Reasoning:
- **WORD_PUZZLE** needs more tokens because it returns a full 10×10 grid (100 single-character cells) plus hidden word metadata. A single round with 2 words is ~300 tokens of grid + metadata.
- **TRIVIA, THIS_OR_THAT, TWO_TRUTHS_ONE_LIE** have compact question shapes. 4,000 tokens is more than enough for 10 questions per round with multiple rounds.

Memory impact at 4,000 tokens: approximately 16MB per request. At 8,000 tokens: approximately 32MB. Both are manageable on a 512MB instance.

### Recommended Additional Step

Add `--max-old-space-size=400` to the Node.js start command on Render:

```
node --max-old-space-size=400 dist/main.js
```

Without this, Node.js will use as much heap memory as the OS allows until the OS kills it. With this flag, Node.js triggers garbage collection more aggressively when approaching 400MB — keeping the process alive instead of getting OOM-killed.

(See `learning/backend/04-games-ai.md` for the AI generation service itself — the OpenRouter integration and the anonymous game play system that also lives in the games module — and for the related dead-code cleanup that was done alongside this fix.)

---

## Part 56 — Does Your Docker Image Actually Apply Migrations?

Worth asking of any deployed app, and the answer is often no. It was no here, for four
independent reasons — each of which would block it on its own. The method of checking matters
more than this particular verdict, so here's the order to check in:

**1. Does anything invoke a migration?** Look at `CMD`/`ENTRYPOINT` in the Dockerfile and at
`command:`/`entrypoint:` in the compose file:

```dockerfile
CMD ["bun", "dist/src/main.js"]
```

That starts the app and nothing else. A `db:deploy` script existed in `package.json`, but
**a script nothing calls is not a deployment step**. Grep for who calls it:

```bash
grep -rn "migrate deploy\|db:deploy\|entrypoint\|ENTRYPOINT" Dockerfile docker-compose*.yml package.json
```

The only `entrypoint:` in the compose file belonged to a MinIO bucket-provisioner container —
easy to skim past and assume the app had one too.

**2. Is the CLI even in the runtime image?** `prisma` is usually a **devDependency**, and
production images install with `--production` / `--omit=dev`, which excludes it. So
`prisma migrate deploy` isn't available inside the container at all.

**3. Are the CLI's config files copied in?** The Dockerfile copied `package.json`, lockfiles,
`dist/`, and `prisma/` — but not `prisma.config.ts`.

**4. Can the CLI even connect?** This is the one that's easy to miss:

```prisma
datasource db {
  provider = "postgresql"
}
```

No `url`. It lives in `prisma.config.ts` instead. So even a container *with* the CLI installed
couldn't reach the database without that file. (See Part 37 in
`learning/backend/06-money-ledger-and-payouts.md` — the same missing `url` breaks standalone
scripts in a different way.)

### `migrate deploy` vs `migrate dev` — never confuse these

| Command | What it does | Safe in prod? |
|---|---|---|
| `prisma migrate dev` | Creates migrations, **can reset the database**, reruns seeds | **No. Never.** |
| `prisma migrate deploy` | Applies pending migrations only. Never resets, never drops | Yes |
| `prisma migrate diff` | Prints SQL, changes nothing | Yes (read-only) |

`migrate dev` is the one in every tutorial because tutorials run locally. Pointing it at a
production `DATABASE_URL` can drop the database to resolve drift. Only ever run `deploy`
against something you care about.

### If you do want migrations in the container

The usual pattern is an entrypoint script that migrates then execs the app:

```sh
#!/bin/sh
set -e
npx prisma migrate deploy
exec bun dist/src/main.js
```

...plus copying `prisma.config.ts` in and making the CLI available at runtime.

**But know the trade-off:** migrating on container start doesn't scale past one replica. Prisma
takes an advisory lock so nothing corrupts, but every replica blocks on boot behind whichever
one is doing the work, and a slow migration becomes a slow rollout. The cleaner pattern at
scale is a **separate release step** that runs once before new containers roll out (Render's
"pre-deploy command", Heroku's release phase, a Kubernetes Job). Single-instance and
pre-launch, entrypoint-on-start is a reasonable trade.

---

## Part 57 — `environment:` Silently Overrides `env_file:` in Compose

This one is worth internalising because it fails quietly and looks correct.

```yaml
app:
  env_file:
    - .env                                                        # your real config
  environment:
    DATABASE_URL: postgresql://postgres:password@postgres:5432/nextvibe   # wins
```

In Docker Compose, **`environment:` takes precedence over `env_file:`**. So despite `.env`
being loaded with the real (Aiven) connection string, this service talks to the throwaway
Postgres container defined in the same file, with the password literally `password`.

A file named `docker-compose.prod.yml` doing this isn't a production stack at all — it's a
self-contained local stack that happens to be named "prod". Nothing errors; the app boots
fine and connects to an empty database.

**How to check what a container actually got**, rather than what you think it got:

```bash
docker compose -f docker-compose.prod.yml config          # renders the FINAL merged config
docker compose exec app printenv DATABASE_URL             # what the running container sees
```

`docker compose config` is the useful one — it resolves all the layering, variable
substitution, and overrides, and prints what Compose will really use. Run it before debugging
"why is my app talking to the wrong database."

**The general lesson:** when two mechanisms can set the same value, find out which wins
*before* you rely on either. Precedence rules are the source of a whole class of bug where
everything looks configured correctly and behaves otherwise.

---

## Part 58 — Is It a Code Bug, or Are You Looking at a Stale Deploy?

A live page misbehaved and the backend logs looked like this:

```
GET /v1/events/earnings                     404
GET /v1/events/earnings/attendees           404
GET /v1/organizer-payments/publish-preview/earnings  400
GET /v1/vibe-tags?eventId=earnings          200
```

The obvious reading is "the backend is broken." The correct reading is the opposite: the
backend is answering perfectly. There is genuinely no event whose id is `"earnings"`.

**The request path told us which code was running.** A newly added Next.js page lived at
`/dashboard/earnings`, but the *deployed* frontend was built before that page existed. With no
static route to match, the URL fell through to the dynamic `app/dashboard/[eventId]/` route,
which rendered with `eventId = "earnings"` and dutifully asked the API for an event by that
name.

So the deployed frontend was stale, and nothing in the backend needed changing at all.

### The diagnostic habit

**When production behaves differently from local, verify what is deployed before debugging the
code.** Local passing while production fails is far more often a deployment-state difference
than a logic bug, and hours get lost editing correct code.

Concretely, the tell was that the *absent* requests mattered as much as the present ones: the
new page would have called `/v1/earnings/balance`, and nothing in the logs did. **Ask what
should be in the logs and isn't** — a missing request is evidence, not silence.

### Probing a deployed API with status codes

You can check whether a route exists on a deployed service without credentials, because a
globally-guarded API distinguishes the two cases for you:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://your-api.example.com/v1/payout-accounts/supported
```

| Response | Meaning |
|---|---|
| `404` | Route does not exist — **the deploy has not picked up your code** |
| `401` | Route exists, auth required — **deployed correctly** |

Always run a **control** alongside it, so you know the two codes actually discriminate on that
service rather than everything returning the same thing:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://your-api.example.com/v1/definitely-not-a-route
# expect 404
```

If the control returns 404 and your real routes return 401, the deploy is confirmed live. That
is a complete verification with no login, no Postman, and no dashboard access. (See
`learning/10-shell.md` Part 6 for what those curl flags do.)

---

## Part 59 — `NEXT_PUBLIC_*` Is Baked In at Build Time

The single most common "I changed the env var and nothing happened" in Next.js.

Variables prefixed `NEXT_PUBLIC_` are **inlined into the JavaScript bundle during the build**.
They are not read from the environment at runtime. So:

- Changing `NEXT_PUBLIC_API_URL` in your host's dashboard and **restarting** the service does
  nothing. The old value is already compiled into the shipped JS.
- You must trigger a **rebuild** for a new value to take effect.
- Locally, the same rule applies to `next dev`: edit `.env` and you must restart the dev
  server. An edit mid-session is silently ignored.

The corollary worth remembering: **anything in a `NEXT_PUBLIC_` variable is public.** It ships
inside JavaScript that any visitor can read. Never put a secret behind that prefix — it is a
declaration that the value is safe to expose, not a way to pass configuration.

### And when `.env` is gitignored

If `.env*` is in `.gitignore` (it should be), the deployed app does **not** get its values from
your repo — they come from the host's dashboard. Two separate sources of truth that drift
silently, because nothing errors when they disagree; the app just points at the wrong backend.

When a deployed frontend can't reach its API, check the host's env config before the code. And
confirm in the browser's Network tab which host the requests actually go to — that is the only
answer that isn't a guess.
