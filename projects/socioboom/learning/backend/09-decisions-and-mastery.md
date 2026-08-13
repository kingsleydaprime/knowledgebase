# SocioBoom Backend — Decision Records, Rebuild Path & Expert Internals

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
every other file in `learning/backend/` — this one is the synthesis layer that assumes them, and
`learning/frontend/08-rebuild-and-reference.md` (the matching frontend rebuild path).

This file covers: the architecture decision records for the backend (what was chosen, what else was
considered, why), a step-by-step path to replicating the entire backend from scratch, and the
expert-level internals — the parts of Node, Express and Prisma worth understanding once the rest is
comfortable.

---

## 19. Architecture Decision Records

This section explains the "why" behind each major decision.

### Why Module Pattern (MVC-like)?

**Alternative:** Flat files — one big `routes.ts` that contains all routes, models, and logic.

**Problem with flat files:** At 10 routes it is manageable. At 50 routes, nobody can find anything. Adding a feature means reading 2,000 lines to find the right place. Testing requires a running HTTP server.

**Module pattern benefits:**
- Predictable file locations — new developer can find `review.service.ts` without searching.
- Separation of concerns — the controller does not know about Redis, the model does not know about HTTP.
- Testability — `PostService.schedulePost` can be unit-tested without Express.
- Scalability — adding a new feature means adding a new folder, not modifying existing files.

### Why Prisma Instead of Raw SQL?

**Alternative:** `pg` pool with raw SQL strings.

**Raw SQL problems:**
- SQL strings have no type safety — typos in column names fail at runtime.
- No autocomplete for table names or fields.
- Manual result mapping — `rows[0].user_id` vs `user.userId`.
- No built-in migration system.

**Prisma benefits:**
- The schema is the single source of truth — change the schema, run migrate, get updated types.
- Every query is type-checked — `prisma.post.findMany({ where: { userId: 'string' } })` is a compile error.
- Relations are first-class — joining tables is Prisma query syntax, not SQL.
- `prisma studio` gives a visual database browser for free.

### Why BullMQ for Scheduling Instead of `setTimeout` or Cron?

**`setTimeout` problems:** Lost on restart. No retry on failure. No visibility. Can't run multiple instances.

**Cron problems:** Runs at wall-clock times, not relative to when a post was created. Requires checking the database every minute to find posts due. Does not scale.

**BullMQ benefits:**
- Jobs persist in Redis — survive restarts.
- Built-in retry with backoff — if posting to Twitter fails, retry 3 times with exponential backoff.
- Exact delay — job fires at `scheduledAt` time, not when a cron next runs.
- Concurrency control — run 5 jobs in parallel, not more.
- Monitoring — BullMQ UI (Bull Board) shows queue status.
- Separate process — a slow job does not block HTTP responses.

### Why Redis for the Queue?

**Alternative:** PostgreSQL-backed queue (PGMQ, pg-boss), or in-memory queue.

**Redis is the right choice because:**
- BullMQ is purpose-built for Redis and uses Redis data structures (sorted sets) optimally.
- Redis is extremely fast for queue operations — pushing a job takes microseconds.
- Redis Pub/Sub can be used for real-time notifications (future feature).
- In-memory queues do not persist. PostgreSQL queues are possible but slower and more complex.

### Why AI Provider Abstraction?

**Alternative:** Call `anthropic.messages.create()` directly in each service.

**Problem:** If you later want to try GPT-4o for a specific task, or OpenRouter for cost reasons, you change 8 files. If Anthropic has an outage, you cannot switch providers without a deploy.

**Abstraction benefits:**
- Change `AI_PROVIDER` in `.env` and redeploy — done.
- Add a third provider (Gemini, Ollama for local inference) by adding one function to `ai.ts`.
- Prompt engineering stays in the services, provider details stay in `ai.ts`.

### Why `express-rate-limit` on AI Routes Specifically?

The AI routes (`/reviews/generate`, `/discovery/search`, `/discovery/generate-response`) each trigger one or more Anthropic API calls. These calls:
- Cost money (billed per token)
- Take 2–15 seconds each
- Can be expensive if called thousands of times

The global 200/15min limit applies to all routes. The AI limiter (15/min) is an additional layer on just the expensive routes. If a user has 200 requests in their global budget, they still cannot use more than 15 AI calls per minute. This protects against:
- Abusive users running automated scripts
- A compromised JWT being used to drain the AI budget

### Why Helmet for Security Headers?

Helmet is a collection of middleware functions, each setting one security-relevant HTTP header. Without Helmet, a browser vulnerability that triggers XSS might allow attacker scripts to run in the victim's browser. Helmet headers tell the browser to:
- Refuse to render the page in an `<iframe>` (prevents clickjacking)
- Not guess content types (prevents MIME confusion attacks)
- Only load resources from trusted origins (CSP)
- Force HTTPS (HSTS)

These are browser-enforced protections. Setting them costs nothing and provides meaningful defense in depth.

### Why TypeScript Path Aliases?

**Without aliases:**
```ts
import prisma from '../../../config/prisma';
import { PostModel } from '../modules/posts/post.model';
```

**With aliases (`@/*` → `src/*`):**
```ts
import prisma from '@/config/prisma';
import { PostModel } from '@/api/v1/modules/posts/post.model';
```

Benefits:
- Moving files does not break imports.
- Imports are readable — you can tell at a glance what `@/config/prisma` is.
- Refactoring is easier — search for `@/config/prisma` instead of `../../../config/prisma`.

### Why Separate Docker Stages for Dev vs Production?

The dev stage runs `ts-node` — it compiles and runs TypeScript in one step, making the development feedback loop fast. But `ts-node` is slow for production (it compiles on every startup) and adds ~50MB of devDependencies.

The production stage pre-compiles with `tsc`, copies only the compiled JavaScript and production dependencies, and produces an image that starts in milliseconds. The security posture is better too — TypeScript source code, development tools, and test infrastructure are not in the production image.

---

## 20. Replicating the Backend From Scratch

Here is the exact sequence to build this from zero.

### 1. Initialize the Project

```bash
mkdir socioboom-backend && cd socioboom-backend
git init
echo "node_modules\ndist\n.env" >> .gitignore

pnpm init
pnpm add express dotenv helmet cors express-rate-limit passport passport-jwt \
         @prisma/client bullmq ioredis axios @anthropic-ai/sdk pg

pnpm add -D typescript ts-node tsconfig-paths nodemon prisma \
         @types/express @types/node @types/cors @types/pg \
         @types/passport @types/passport-jwt
```

### 2. Create `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "es2016",
    "module": "commonjs",
    "paths": { "@/*": ["./src/*"] },
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "outDir": "./dist"
  }
}
```

### 3. Initialize Prisma

```bash
npx prisma init
```

This creates `prisma/schema.prisma` and a `.env` with `DATABASE_URL`. Edit the schema to define your models, then:

```bash
npx prisma migrate dev --name init
npx prisma generate
```

### 4. Create the Directory Structure

```bash
mkdir -p src/app src/config src/api/v1/shared/services src/api/v1/shared/jobs
mkdir -p src/api/v1/modules/{posts,analytics,notifications,accounts,teams,users,reviews,discovery}
```

### 5. Create Config Files

Create `src/config/prisma.ts`, `src/config/queue.ts`, `src/config/auth.ts`, and `src/express.d.ts` as shown in this guide.

### 6. Create Each Module

For each module, create all five files in order: type → model → service → controller → routes.

### 7. Create `src/app/main.ts`

Wire all routes into the Express app with the full middleware chain.

### 8. Create `src/worker.ts`

Set up BullMQ workers for all three queues.

### 9. Add Scripts to `package.json`

```json
{
  "scripts": {
    "dev": "ts-node -r tsconfig-paths/register src/app/main.ts",
    "worker": "ts-node -r tsconfig-paths/register src/worker.ts",
    "build": "tsc",
    "start": "node dist/app/main.js"
  }
}
```

### 10. Create `.env`

Fill in all required environment variables (see Section 17).

### 11. Start Development

```bash
# Terminal 1: Start Redis
docker run -p 6379:6379 redis:alpine

# Terminal 2: Start the API server
pnpm dev

# Terminal 3: Start the worker
pnpm worker
```

---

## 21. Expert-Level Internals

### BullMQ's Delayed Job Implementation

When you call `postQueue.add('schedulePost', data, { delay: 5000 })`, BullMQ:

1. Assigns the job a UUID.
2. Stores the job data in a Redis hash: `bull:postQueue:job:<id>`.
3. Adds the job ID to the sorted set `bull:postQueue:delayed` with score `Date.now() + 5000`.

The worker process polls this sorted set every 1 second (configurable) using:

```
ZRANGEBYSCORE bull:postQueue:delayed 0 <currentTimestamp> LIMIT 0 1
```

When the current timestamp is past the job's score, it atomically moves the job to `bull:postQueue:wait` using a Lua script. The script ensures this operation is atomic — no two workers can claim the same job.

### Why `maxRetriesPerRequest: null`

ioredis by default retries failed Redis commands a limited number of times before throwing. BullMQ workers run long-lived blocking commands (`BLPOP`, blocking pop from a list) to wait for new jobs. If ioredis's retry limit is reached during this blocking wait, it throws an error that crashes the worker. Setting `maxRetriesPerRequest: null` disables this limit, allowing BullMQ to manage its own retry logic for the worker's connection.

### Prisma's Query Engine

When you run `npx prisma generate`, Prisma downloads a query engine binary — a Rust-compiled executable that handles the actual SQL generation and database connection pooling. The TypeScript client you import is a thin wrapper that sends type-safe queries to this binary via inter-process communication. This is why `npx prisma generate` is needed in the Dockerfile — the binary is platform-specific and must be generated for the target OS (Linux Alpine in Docker).

### TypeScript Declaration Merging in Depth

The `express.d.ts` file uses two TypeScript features:
- **Declaration merging:** TypeScript merges multiple declarations with the same name. When you declare `namespace Express { interface Request { user?: IUser } }`, TypeScript merges this with Express's existing `Request` interface.
- **Ambient declarations:** `declare global` makes the declaration globally available without importing it, which is what you want for augmenting third-party types.

This is a standard pattern called "module augmentation" and is the correct TypeScript way to extend third-party types.

### OAuth Token Expiry Buffer Explained

```ts
DiscoveryService.redditTokenExpiry = Date.now() + (data.expires_in as number) * 1000 - 60_000;
```

Why subtract 60 seconds? Imagine this sequence without the buffer:
1. Token expires at T=3600s.
2. At T=3599s, `Date.now() < redditTokenExpiry` is true, so we use the cached token.
3. The network request takes 2 seconds.
4. At T=3601s, Reddit receives the request with an expired token → 401 error.

With a 60-second buffer:
1. Token is considered expired at T=3540s.
2. At T=3539s, we use the cached token.
3. If the request takes up to 59 seconds, it still arrives before Reddit's actual expiry.
4. At T=3540s, we fetch a new token before the real expiry.

This is a standard pattern in OAuth token management. The buffer size depends on your expected worst-case network latency.

### AI Streaming vs Non-Streaming

SocioBoom uses `anthropic.messages.stream()` but immediately calls `stream.finalMessage()`, so it behaves like a non-streaming call. Why use the streaming API at all?

1. **Timeout handling:** The Anthropic SDK's non-streaming `create()` waits for the entire response before returning. For long responses (8,000 tokens with extended thinking), this can take 60+ seconds and may hit HTTP timeout limits. The streaming API receives chunks as they arrive, so the connection stays alive.

2. **Future flexibility:** If you want to stream the AI response to the frontend in real-time (showing the post as it's being written), you already have the streaming infrastructure. You just need to pipe chunks to the response instead of awaiting `finalMessage()`.

3. **Extended thinking compatibility:** The `thinking` parameter only works with the streaming API in some SDK versions.

### Redis Key Naming in BullMQ

BullMQ's Redis keys follow the pattern `bull:<queueName>:<type>:<id>`. In SocioBoom:

- `bull:postQueue:job:1` — job data hash
- `bull:postQueue:delayed` — sorted set of delayed jobs
- `bull:postQueue:wait` — list of jobs ready to process
- `bull:postQueue:active` — sorted set of jobs being processed
- `bull:postQueue:completed` — sorted set of completed jobs
- `bull:postQueue:failed` — sorted set of failed jobs
- `bull:postQueue:repeat:schedulePost:every:...` — repeat job configuration

You can inspect these directly with:

```bash
redis-cli
KEYS bull:postQueue:*
HGETALL bull:postQueue:job:1
ZRANGEBYSCORE bull:postQueue:delayed -inf +inf WITHSCORES
```

### The `as const` Assertion

In the review service:

```ts
return rawReviews.map((r) => ({
  source: 'google' as const,  // Type is 'google', not string
  reviewText: r.text ?? '',
}));
```

Without `as const`, TypeScript infers the type of `'google'` as `string`. But the `Review` interface requires `source: ReviewSource` where `ReviewSource = 'google' | 'yelp' | 'twitter' | 'reddit' | 'manual'`. A `string` does not satisfy `ReviewSource`. `as const` narrows the type to the literal `'google'`, which satisfies the union type.

### Compound `WHERE OR` with Prisma Relations

```ts
prisma.team.findMany({
  where: {
    OR: [
      { ownerId: userId },
      { members: { some: { userId } } },
    ],
  },
});
```

The SQL Prisma generates for this:

```sql
SELECT t.*
FROM "teams" t
WHERE t.owner_id = $1
   OR EXISTS (
     SELECT 1
     FROM "team_members" tm
     WHERE tm.team_id = t.id
       AND tm.user_id = $1
   )
```

`{ members: { some: { userId } } }` is Prisma's way of expressing "at least one related `TeamMember` where `userId` matches." `some` becomes `EXISTS (SELECT 1 FROM ... WHERE ...)`. The equivalent operators are `every` (ALL related records match) and `none` (NO related records match).

---


