# SocioBoom Backend — BullMQ, Redis & Reliable Background Work

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/04-auth-and-security.md` (the token refresh the publish worker depends on),
`learning/backend/06-ai-and-agents.md` (the discovery agent that runs as a queued job), and
`learning/backend/08-devops-and-deployment.md` (the war story of the worker that never ran).

This file covers: what a job queue is and why scheduled posting needs one, BullMQ and Redis setup,
the queue/worker split and why the worker is a separate process, delayed jobs for scheduling, why
long AI work belongs in a background job rather than a request handler, and queue reliability — how
retries can double-post to social platforms and the `publishedPlatforms` job-data pattern that
prevents it.

---

## 10. Job Queues with BullMQ and Redis

### Why Not setTimeout?

The naive approach to scheduling a post:

```ts
setTimeout(() => {
  postToSocialMedia(post);
}, delay);
```

This has fatal problems:
- If the server restarts, all pending `setTimeout` calls are lost.
- If you run two server instances, the same post might fire twice.
- Node.js does not guarantee exact timing under load.
- There is no visibility into pending jobs, failed jobs, retries.

### What is a Job Queue?

A job queue is a separate data store (Redis, in this case) that holds jobs persistently. Your server is the **producer** — it adds jobs to the queue. A separate **worker process** is the **consumer** — it pulls jobs off the queue and executes them.

```
Producer (main server)          Queue (Redis)           Consumer (worker process)
  postQueue.add(job, {delay})  →  [job stored]  →  worker processes job at right time
```

Because the jobs are in Redis (not in server memory), they survive server restarts. You can run multiple worker instances — BullMQ uses atomic operations to ensure each job is processed exactly once.

### Redis Connection

```ts
// src/config/queue.ts
import { Queue, Worker, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';

const redisConnection = new IORedis({
  host: 'localhost',
  port: 6379,
  maxRetriesPerRequest: null, // Required for BullMQ workers
});
```

`maxRetriesPerRequest: null` is a BullMQ requirement. It disables ioredis's built-in retry limit so BullMQ can manage retries itself.

### The Three Queues

```ts
export const postQueue      = new Queue('postQueue', { connection: redisConnection });
export const analyticsQueue = new Queue('analyticsQueue', { connection: redisConnection });
export const notificationQueue = new Queue('notificationQueue', { connection: redisConnection });
```

- `postQueue` — fires when a scheduled post's time arrives
- `analyticsQueue` — runs hourly to refresh analytics for published posts
- `notificationQueue` — runs every 5 minutes to check for new notifications

### Adding a Job with Delay

```ts
// src/api/v1/modules/posts/post.service.ts
const delay = scheduledAt.getTime() - Date.now(); // milliseconds until scheduled time

if (delay > 0) {
  await postQueue.add(
    'schedulePost',                                // Job name (for filtering/monitoring)
    { postId: post.id, userId, content, platforms }, // Job data (payload)
    { delay },                                     // Options: delay before processing
  );
}
```

BullMQ stores the job in Redis with a score equal to `now + delay`. The worker process polls Redis using a sorted set operation — jobs with a score in the past are ready to process.

### Adding a Repeating Job

```ts
// src/api/v1/modules/analytics/analytics.service.ts
await analyticsQueue.add(
  'fetchAnalytics',
  { postId, platform },
  { repeat: { every: 3600000 } }, // Repeat every 1 hour (3,600,000 ms)
);

// src/api/v1/modules/notifications/notification.service.ts
await notificationQueue.add(
  'checkNotifications',
  { userId, postId, platform },
  { repeat: { every: 300000 } }, // Repeat every 5 minutes
);
```

BullMQ manages repeating jobs internally — it re-enqueues the job after each execution.

### The Worker Process

The worker runs as a **separate Node.js process** from the main HTTP server. This is important: if a job takes 30 seconds, it does not block the HTTP server.

```ts
// src/worker.ts
import { Worker } from 'bullmq';
import { postQueue, analyticsQueue, notificationQueue } from './config/queue';
import { AnalyticsService } from './api/v1/modules/analytics/analytics.service';
import { NotificationService } from './api/v1/modules/notifications/notification.service';

// Worker for posts: fires when a scheduled post's time arrives
const postWorker = new Worker('postQueue', async (job) => {
  const { postId, userId, content, platforms } = job.data;
  console.log(`Posting to ${platforms} for post ${postId}`);
  // Call platform APIs here (e.g., postToTwitter(accessToken, content))
}, { connection: postQueue.options.connection });

// Worker for analytics: runs hourly
const analyticsWorker = new Worker('analyticsQueue', async (job) => {
  const { postId, platform } = job.data;
  await AnalyticsService.fetchAnalytics(postId, platform);
}, { connection: analyticsQueue.options.connection });

// Worker for notifications: runs every 5 minutes
const notificationWorker = new Worker('notificationQueue', async (job) => {
  const { userId, postId, platform } = job.data;
  await NotificationService.checkNotifications(userId, postId, platform);
}, { connection: notificationQueue.options.connection });

// Event listeners for observability
postWorker.on('completed', (job) => console.log(`Post job ${job.id} completed`));
postWorker.on('failed', (job, err) => console.error(`Post job ${job?.id} failed: ${err.message}`));
analyticsWorker.on('completed', (job) => console.log(`Analytics job ${job.id} completed`));
notificationWorker.on('failed', (job, err) => console.error(`Analytics job ${job?.id} failed: ${err.message}`));
notificationWorker.on('completed', (job) => console.log(`Notification job ${job.id} completed`));
notificationWorker.on('failed', (job, err) => console.error(`Notification job ${job?.id} failed: ${err.message}`));
```

To run the worker separately:

```bash
# In development
ts-node -r tsconfig-paths/register src/worker.ts

# In production (after build)
node dist/worker.js
```

### BullMQ Internal Mechanics

BullMQ uses several Redis data structures:

- **Sorted set** `bull:postQueue:delayed` — jobs with a score = process-at timestamp. The worker polls this set looking for scores <= now.
- **List** `bull:postQueue:wait` — jobs ready to be picked up by a worker (FIFO).
- **Hash** `bull:postQueue:job:123` — the job data, status, attempts, timestamps.
- **Sorted set** `bull:postQueue:completed` — completed jobs (configurable TTL).
- **Sorted set** `bull:postQueue:failed` — failed jobs (kept until manually removed).

The transition `delayed → wait → active → completed/failed` is atomic using Redis Lua scripts, which is why BullMQ can safely run multiple worker instances without double-processing.

---


## 24. Long AI Work Belongs in Background Jobs

An agent run takes 1–3 minutes. Three things break if you run it inside an HTTP request:

1. **Timeouts** — proxies (Railway, nginx, browsers) give up long before 3 minutes.
2. **Retries multiply cost** — a client that retries a timed-out request starts a *second* agent run while the first is still burning tokens.
3. **No progress feedback** — the user stares at a spinner with zero results until everything finishes.

The pattern that fixes all three, using infrastructure the project already had (BullMQ + Redis):

```
POST /discovery/search
  → BillingService.checkAndConsume(userId)     // charge at kickoff, once
  → create session row  { status: 'running' }
  → discoveryQueue.add('discover', { sessionId, userId, ... })
  → return 202 { session }                      // immediately

worker process:
  → userKeys = await ApiKeysService.getForUser(userId)   // BYOK resolved at RUN time
  → runDiscoveryAgent(...)                                // saves pain points AS IT FINDS THEM
  → update session { status: 'completed', summary }
  → NotificationModel.create(...)

GET /discovery/:sessionId    ← client polls this
  → { session, painPoints }  // grows while the agent works
```

Design details that matter:

- **`202 Accepted`**, not `201`, is the correct status for "started but not finished."
- **Incremental saves are the streaming mechanism.** The agent's `save_pain_point` tool writes a DB row the moment a pain point is verified. Polling clients see the list grow — no WebSockets or SSE needed to feel "live."
- **Resolve user API keys inside the worker**, not the controller. Job payloads live in Redis; putting decrypted keys in them would be a second, unencrypted copy of your users' secrets.
- **One combined poll endpoint** (`session` + `painPoints` together). Two endpoints polled every 4 s doubles request volume against your own rate limiter.
- **Failure is a state, not an exception**: catch, set `status: 'failed'` with the reason in `summary`, notify — so the frontend shows "failed," not an eternal spinner. Discovery jobs use `attempts: 1`; retrying an agent run costs real money, so failures surface instead of silently re-running.

The same reasoning in reverse justified keeping web review fetching *synchronous*: it was capped at `maxSteps: 6` on the fast model, which fits inside a normal request. Budget determines architecture.

---


## 26. Queue Reliability: Retries Without Double-Posting

The publish worker originally ran each job once. One network blip → post marked `failed` forever. Adding retries is one config block:

```ts
export const postQueue = new Queue('postQueue', {
  connection: redisConnection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 30_000 },  // 30s, 60s, 120s
    removeOnComplete: 1000,
    removeOnFail: 5000,
  },
});
```

But naïve retries create a worse bug than the one they fix: if a job publishes to Twitter, then fails on LinkedIn, the retry would **tweet again**. Retries demand idempotency. The fix — record progress *in the job itself*:

```ts
const alreadyPublished = new Set(job.data.publishedPlatforms ?? []);

for (const platform of platforms) {
  if (alreadyPublished.has(platform)) continue;      // skip on retry
  // ... publish ...
  alreadyPublished.add(platform);
  await job.updateData({ ...job.data, publishedPlatforms: [...alreadyPublished] });
}

if (failed.length > 0) {
  // last attempt? notify the user; either way, throw so BullMQ retries
  const isLastAttempt = job.attemptsMade + 1 >= (job.opts.attempts ?? 1);
  if (isLastAttempt) { /* create per-platform failure notifications */ }
  throw new Error(`Failed platforms: ...`);
}
```

`job.updateData` persists to Redis, so the retry — even on another worker — sees what already succeeded. Throwing is deliberate: **in BullMQ, throwing is how you request a retry.**

Two related fixes from the same session:

- **Stale-payload race:** jobs used to carry `content` in their payload. Edit a scheduled post → the queued job still publishes the *old* text. Now the payload is just `{ postId, userId }` and the worker re-reads the post from Postgres at publish time. Rule: job payloads should carry *identity*, not *state* — state lives in the database.
- **`content.slice(0, 280)`** truncates mid-word. The replacement cuts at the last word boundary and appends `…`. Tiny fix, very visible to users.

---


