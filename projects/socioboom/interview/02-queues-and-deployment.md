# SocioBoom — Queues, Reliability & Deployment

From [`../learning/backend/05-queues-and-jobs.md`](../learning/backend/05-queues-and-jobs.md) and
[`08-devops-and-deployment.md`](../learning/backend/08-devops-and-deployment.md).

---

### Q1. [Intermediate] 🔥 Why is there a queue at all? Why not just a cron job or a `setTimeout`?

**Strong answer covers:** scheduled publishing needs **durability** (a restart must not lose a post
scheduled for tomorrow — `setTimeout` dies with the process), **retries with backoff**, **delayed
execution** at a precise time, and **isolation** so a slow platform API doesn't tie up a web
process. BullMQ on Redis gives all four. A cron job could work but you'd hand-roll per-job state,
retry accounting and concurrency.

**The related architectural point:** long AI work belongs in a background job for the same reason —
a request that takes ninety seconds is a request that will be killed by some proxy in between, and
the user's browser shouldn't be the thing holding it open.

---

### Q2. [Advanced] 🔥🔥 You added retries and created a worse bug. Explain.

**The best backend story in this project.**

**Strong answer covers the setup:** retries are one config block —
```ts
defaultJobOptions: {
  attempts: 3,
  backoff: { type: 'exponential', delay: 30_000 },   // 30s, 60s, 120s
}
```

**The bug this creates:** one job publishes to several platforms. If it succeeds on Twitter and fails
on LinkedIn, the retry re-runs the **whole job** — and tweets again. Users get duplicate posts, which
for a social publishing tool is about the worst possible failure.

**The fix — record progress inside the job's own data:**
```ts
const alreadyPublished = new Set(job.data.publishedPlatforms ?? []);
for (const platform of platforms) {
  if (alreadyPublished.has(platform)) continue;      // skip on retry
  // ...publish...
  alreadyPublished.add(platform);
  await job.updateData({ ...job.data, publishedPlatforms: [...alreadyPublished] });
}
```
The job carries its own progress, so a retry **resumes** rather than repeats.

**The sentence to land:** *retries demand idempotency* — adding retries to a non-idempotent operation
converts a visible failure into an invisible duplication, which is strictly worse.

**Follow-up worth pre-empting:** *"Why store it on the job rather than in the database?"* — the job is
the unit being retried, so the progress and the retry are atomic with respect to each other. A
database row would work and needs its own consistency story with the job's lifecycle. And `updateData`
must happen **after** the publish succeeds, not before, or a crash between them loses a post rather
than duplicating one — choosing which direction to fail in is the actual design decision.

---

### Q3. [Advanced] 🔥🔥 Every scheduled post would have silently never published. What was wrong?

**Strong answer covers:** `worker.ts` existed, compiled, and was **completely correct** — and nothing
anywhere started it. No npm script, the Dockerfile `CMD` ran only the API, `fly.toml` declared one
process, and compose had no worker service. There was no error to find, because nothing failed;
the code simply never ran.

**The checklist that fixed it — this generalises to any app with a background process:**

| Layer | Fix |
|---|---|
| `package.json` | `dev:worker` and `start:worker` scripts |
| The worker itself | `import 'dotenv/config'` at the top — a standalone process doesn't inherit the API's dotenv call |
| Compose (dev + prod) | a `worker` service: same image, `command: node dist/worker.js` |
| `fly.toml` | a `[processes]` block with both `app` and `worker` |
| Railway | a second service from the same repo with a custom start command |

**The architectural insight that makes this more than a checklist:** platforms auto-stop idle HTTP
machines (`min_machines_running = 0`). **A scheduler cannot live in a machine that sleeps** — the
9 a.m. post needs something awake at 9 a.m. A worker has no HTTP service, so it stays running.
That's why worker-as-separate-process isn't tidiness; it's what makes scheduled delivery work at all.

---

### Q4. [Advanced] 🔥 Railway reported "1/1 replicas never became healthy" for your worker. Why?

**Strong answer covers:** the platform health-checked the worker at `/health` and got service
unavailable eleven times. Diagnosis: **the worker had no HTTP server at all.** Nothing was broken
except the expectation — a background process legitimately doesn't serve HTTP.

**Two valid fixes, and why one was chosen:** remove the health check (workers don't need one), or add
a liveness endpoint so the platform can genuinely detect a dead worker. The endpoint won, because
"no health check" also means "no way to know it died" — which is exactly the failure mode from Q3.

**The implementation detail worth quoting:** the port is env-gated so a shared local `.env` can't make
the worker collide with the API —
```ts
const healthPort = process.env.WORKER_HEALTH_PORT
  ?? (process.env.NODE_ENV === 'production' ? process.env.PORT : undefined);
if (healthPort) { http.createServer(...).listen(Number(healthPort)); }
```

---

### Q5. [Intermediate] What's in your Docker setup, and why multi-stage?

**Strong answer covers:** a build stage with the full toolchain producing `dist/`, and a runtime stage
containing only the compiled output and production dependencies — smaller image, faster pulls,
smaller attack surface. The project-specific part: **the same image serves both processes**, with the
command deciding whether it's the API or the worker. That's the right factoring, because it
guarantees the two can't drift to different code versions.

**Layer-caching detail:** copy `package.json`/lockfile and install *before* copying source, so a
source change doesn't reinstall every dependency.

---

### Q6. [Intermediate] 🔥 You had 502s in production. How do you debug one?

**Strong answer covers:** a 502 means the proxy couldn't get a valid response from your app — so the
question is always *did the app start, and is it listening where the platform expects?* Check, in
order: did the process boot at all (read the startup logs rather than the health status); is it
binding to the **platform-provided `PORT`** rather than a hard-coded one; is it binding to `0.0.0.0`
rather than `127.0.0.1` (a container listening on localhost is unreachable from outside it); and did
it start and then crash on a missing env var or an unreachable database.

**The generalisable habit:** a 502 is almost never an application-logic bug. It's a
process/port/binding problem, and looking in the route handler wastes an hour.

---

### Q7. [Intermediate] 🔥 And CORS failures in production that worked in dev?

**Strong answer covers:** dev usually runs permissive (or same-origin through a proxy) while
production has an explicit allowlist — so the prod frontend's origin has to actually be in it,
including protocol and any `www`. Two subtleties: **credentialed requests can't use `*`**, they need
the exact origin echoed plus `Access-Control-Allow-Credentials`; and a **preflight** `OPTIONS` must
be answered before auth runs, or the browser sees a CORS failure whose real cause is a 401 (see
[01-backend-architecture.md](01-backend-architecture.md) Q2).

**The diagnostic tell:** if curl works and the browser doesn't, it's CORS. If neither works, it isn't.

---

### Q8. [Intermediate] How does a scheduled post actually flow through the system?

**Strong answer covers:** the user schedules a post → a job is enqueued with a **delay** to the
target time → BullMQ holds it in Redis → the worker (a continuously-running process) picks it up at
the scheduled moment → for each connected platform not already in `publishedPlatforms`, refresh the
token if needed and call the platform API → record success per platform → if any failed, throw so
BullMQ retries with backoff, and on the last attempt notify the user.

**The details that make this a good answer:** the delay is BullMQ's, not a timer in the app;
partial success is recorded, not discarded; and "notify on the final attempt" is different from
"notify on every failure", or a user gets three emails for one transient blip.

---

### Q9. [Advanced] What happens if you run two workers?

**Strong answer covers:** BullMQ is designed for it — a job is delivered to exactly one worker via
Redis, so horizontal scaling is adding processes. The things that then matter: **concurrency per
worker** interacts with platform rate limits (two workers each doing five concurrent publishes is ten
concurrent calls to the same API), token refresh can race if two jobs for the same account refresh
simultaneously, and job-level idempotency (Q2) becomes load-bearing rather than merely prudent.

**The honest note:** the current design would mostly work, and the token-refresh race is the piece
that needs a lock before you'd want it running at scale.

---

### Q10. [Intermediate] What would you add to make this operable at 3am?

**Strong answer covers:** metrics on queue depth and failure rate (a growing queue is the earliest
signal of anything wrong); alerting on the **worker being dead**, which is exactly what the health
endpoint from Q4 enables; a dead-letter view of exhausted jobs so failed posts are visible rather
than lost; structured logs with the post id and platform so one publish attempt is traceable across
retries; and a manual replay path, since "retry this failed post" is the most common operator action.
