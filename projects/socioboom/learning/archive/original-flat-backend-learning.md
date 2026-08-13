# SocioBoom Backend: A Complete Learning Guide

From absolute beginner to expert — everything needed to understand, replicate, and extend the SocioBoom API.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Foundations: Node.js, Express, TypeScript](#2-foundations-nodejs-express-typescript)
3. [Project Bootstrap](#3-project-bootstrap)
4. [TypeScript Configuration](#4-typescript-configuration)
5. [The Module Pattern](#5-the-module-pattern)
6. [Express App and Middleware Chain](#6-express-app-and-middleware-chain)
7. [Database with Prisma 5](#7-database-with-prisma-5)
8. [Authentication with Passport JWT](#8-authentication-with-passport-jwt)
9. [Security: Helmet, CORS, Rate Limiting](#9-security-helmet-cors-rate-limiting)
10. [Job Queues with BullMQ and Redis](#10-job-queues-with-bullmq-and-redis)
11. [AI Provider Abstraction](#11-ai-provider-abstraction)
12. [All Modules: A Complete Tour](#12-all-modules-a-complete-tour)
13. [Feature Deep-Dive: Review Poster](#13-feature-deep-dive-review-poster)
14. [Feature Deep-Dive: Pain-Point Discovery](#14-feature-deep-dive-pain-point-discovery)
15. [External API Calls with Axios](#15-external-api-calls-with-axios)
16. [OAuth: Reddit App-Only Token Flow](#16-oauth-reddit-app-only-token-flow)
17. [Environment Variables and Secret Management](#17-environment-variables-and-secret-management)
18. [Docker: Dev and Production Stages](#18-docker-dev-and-production-stages)
19. [Architecture Decision Records](#19-architecture-decision-records)
20. [Replicating the Backend From Scratch](#20-replicating-the-backend-from-scratch)
21. [Expert-Level Internals](#21-expert-level-internals)
22. [Single-Shot Prompts vs AI Agents](#22-single-shot-prompts-vs-ai-agents)
23. [Structured Output: Forced Tool Use Instead of Regex](#23-structured-output-forced-tool-use-instead-of-regex)
24. [Long AI Work Belongs in Background Jobs](#24-long-ai-work-belongs-in-background-jobs)
25. [Grounding an Agent: URL Allowlists, Page Fetching, SSRF](#25-grounding-an-agent-url-allowlists-page-fetching-ssrf)
26. [Queue Reliability: Retries Without Double-Posting](#26-queue-reliability-retries-without-double-posting)
27. [Tokens at Rest and OAuth Refresh Across Platforms](#27-tokens-at-rest-and-oauth-refresh-across-platforms)
28. [Verifying Migrations Without Your Dev Database](#28-verifying-migrations-without-your-dev-database)
29. [Deployment War Stories: The Worker That Never Ran, 502s, and CORS](#29-deployment-war-stories-the-worker-that-never-ran-502s-and-cors)

---

## 1. The Big Picture

SocioBoom is a SaaS tool for founders and marketers. It does three things:

1. **Schedule posts** to social media platforms (Twitter, LinkedIn, Facebook, Instagram) at a future time.
2. **Turn customer reviews** (from Google, Yelp, Twitter, Reddit) into polished marketing posts using AI.
3. **Find pain points** on Reddit and Twitter where people complain about problems your product solves, then generate authentic-sounding replies that organically introduce your product.

The backend is a REST API. A "REST API" is a server that listens for HTTP requests (the same protocol your browser uses) and sends back JSON responses. The frontend (a React app) calls this API. The API talks to a PostgreSQL database, a Redis job queue, and several external APIs (Google, Yelp, Twitter, Reddit, Anthropic).

Here is the full request lifecycle for scheduling a post:

```
Frontend
  → POST /api/v1/posts/schedule  (HTTP request with JSON body)
     → Express receives it
     → helmet adds security headers
     → cors validates the origin
     → express.json() parses the JSON body
     → passport.authenticate() checks the JWT token
     → globalLimiter checks rate limit
     → PostController.schedulePost() handles the request
        → PostService.schedulePost() runs business logic
           → PostModel.create() writes to PostgreSQL via Prisma
           → postQueue.add() pushes a delayed job to Redis/BullMQ
        → res.status(201).json(post) sends the saved post back
```

Every feature follows this same path.

---

## 2. Foundations: Node.js, Express, TypeScript

### What is Node.js?

Node.js is a runtime that lets you run JavaScript on a server instead of in a browser. Before Node.js, JavaScript only ran in browsers. Node.js uses V8 (Chrome's JS engine) and wraps it with APIs for talking to the file system, network, OS, etc.

Node.js is **asynchronous by default**. Instead of waiting for one operation to finish before starting another (blocking), Node.js uses an event loop that lets it handle thousands of simultaneous connections without creating a thread for each one.

```js
// Synchronous (blocking) - BAD for a server
const data = fs.readFileSync('file.txt'); // Freezes everything until done
doSomethingWith(data);

// Asynchronous (non-blocking) - GOOD for a server
fs.readFile('file.txt', (err, data) => {
  doSomethingWith(data); // Called when file is ready, nothing else blocked
});

// Modern async/await syntax (what SocioBoom uses)
const data = await fs.promises.readFile('file.txt'); // Pauses only this function
doSomethingWith(data);
```

SocioBoom uses Node.js 22, which is the LTS (Long-Term Support) version as of 2025.

### What is Express?

Express is a minimal web framework for Node.js. Without it, you would need to write raw HTTP server code:

```js
// Without Express - raw Node.js HTTP
const http = require('http');
http.createServer((req, res) => {
  if (req.url === '/posts' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ posts: [] }));
  }
}).listen(3000);
```

With Express, the same thing becomes:

```js
const express = require('express');
const app = express();
app.get('/posts', (req, res) => res.json({ posts: [] }));
app.listen(3000);
```

Express gives you:
- **Routing** — map URLs to handler functions
- **Middleware** — functions that run before your handler (for auth, parsing, logging, etc.)
- **Request/Response objects** — clean APIs for reading requests and writing responses

### What is TypeScript?

TypeScript is JavaScript with types. It compiles to JavaScript. The types exist only during development — they are erased when compiled. They let your editor catch errors before you run the code.

```ts
// JavaScript - no types, no safety
function createPost(userId, content, platforms) {
  // If you pass a string for userId instead of a number, you find out at runtime
}

// TypeScript - types catch mistakes immediately
function createPost(userId: number, content: string, platforms: string[]): Promise<Post> {
  // If you pass a string for userId, TypeScript gives you an error before you even run the code
}
```

SocioBoom uses TypeScript 5 with `"strict": true`, which is the most stringent setting — it enables every safety check.

---

## 3. Project Bootstrap

To replicate the backend from scratch:

```bash
mkdir backend && cd backend
git init
npm init -y

# Install runtime dependencies
pnpm add express dotenv helmet cors express-rate-limit passport passport-jwt \
         @prisma/client bullmq ioredis axios @anthropic-ai/sdk pg compression

# Install development dependencies
pnpm add -D typescript ts-node nodemon prisma \
         @types/express @types/node @types/cors @types/pg @types/passport \
         @types/passport-jwt @types/compression
```

The `package.json` scripts:

```json
{
  "scripts": {
    "dev": "ts-node src/app/main.ts",
    "build": "tsc",
    "start": "node dist/app/main.js"
  }
}
```

- `dev` — runs TypeScript directly using `ts-node` (no compile step needed during development)
- `build` — compiles TypeScript to JavaScript in a `dist/` folder
- `start` — runs the compiled JavaScript (what production uses)

The TypeScript path alias `@/*` → `src/*` requires `tsconfig-paths` to work with `ts-node`:

```bash
pnpm add -D tsconfig-paths
```

Then change the dev script:

```json
"dev": "ts-node -r tsconfig-paths/register src/app/main.ts"
```

---

## 4. TypeScript Configuration

The full `tsconfig.json` for this project. The key settings are:

```jsonc
{
  "compilerOptions": {
    "target": "es2016",        // Compile to ES2016 JavaScript
    "module": "commonjs",      // Use require()/module.exports (Node.js standard)
    "paths": {
      "@/*": ["./src/*"]       // @/config/prisma → src/config/prisma
    },
    "esModuleInterop": true,   // Allows: import express from 'express'
    "strict": true,            // All strict checks on
    "skipLibCheck": true       // Don't type-check node_modules .d.ts files
  }
}
```

**Why `module: "commonjs"`?** Node.js has historically used CommonJS (`require()`/`module.exports`). ES Modules (`import`/`export`) work in Node.js too but require `.mjs` extension or `"type": "module"` in `package.json`. CommonJS is simpler to configure with Prisma, BullMQ, and ts-node, so SocioBoom uses it. TypeScript compiles the ES-style `import/export` syntax you write to CommonJS `require()` calls automatically.

**Why `esModuleInterop`?** Some packages like Express export a function as `module.exports`. Without `esModuleInterop`, you would have to write `import * as express from 'express'`. With it, you can write `import express from 'express'` — the more natural form.

**Why path aliases?** Without aliases, imports look like `../../config/prisma`. That breaks whenever you move a file. With `@/config/prisma`, the import always refers to the same file regardless of where the importing file lives.

**TypeScript Declaration Merging for `req.user`:**

Express's `Request` type does not have a `user` property by default. Passport attaches the authenticated user to `req.user`. To tell TypeScript about this without losing type safety, SocioBoom uses declaration merging in `src/express.d.ts`:

```ts
// src/express.d.ts
import { IUser } from '@/api/v1/modules/users/user.type';

declare global {
  namespace Express {
    interface Request {
      user?: IUser;
    }
  }
}
```

This merges your new property into Express's existing `Request` interface. Now `req.user` is typed everywhere with no cast needed.

---

## 5. The Module Pattern

Every feature in SocioBoom is a module. A module lives in `src/api/v1/modules/<name>/` and contains exactly five files:

| File | Responsibility |
|---|---|
| `<name>.type.ts` | TypeScript types and interfaces for this module |
| `<name>.model.ts` | All database queries (talks to Prisma) |
| `<name>.service.ts` | Business logic (orchestrates models, calls AI, queues jobs) |
| `<name>.controller.ts` | HTTP layer (reads `req`, calls service, writes `res`) |
| `<name>.routes.ts` | URL routing (maps HTTP verbs + paths to controller methods) |

This is called a layered architecture. Each layer only knows about the layer directly below it:

```
routes → controller → service → model → Prisma → PostgreSQL
```

**Why this structure?** Several reasons:
- You can change the database without touching the HTTP layer.
- You can add a second interface (CLI, cron job) that calls the service without duplicating logic.
- Testing is easier — you can test the service in isolation by mocking the model.
- New developers can predict where code lives without reading the whole codebase.

Let's trace the posts module as a complete example.

### `post.type.ts`

```ts
// src/api/v1/modules/posts/post.type.ts
export type { Post } from '@prisma/client';
```

Most types come directly from Prisma because the Prisma client auto-generates TypeScript types from the schema. Re-exporting them here means the rest of the module imports from `./post.type` rather than directly from `@prisma/client` — a single place to change if types ever need augmentation.

### `post.model.ts`

```ts
// src/api/v1/modules/posts/post.model.ts
import prisma from '@/config/prisma';
import { Post } from '@prisma/client';

export class PostModel {
  static async create(
    userId: number,
    content: string,
    platforms: string[],
    scheduledAt: Date,
  ): Promise<Post> {
    return prisma.post.create({
      data: { userId, content, platforms, scheduledAt, status: 'scheduled' },
    });
  }

  static async findByUserId(userId: number): Promise<Post[]> {
    return prisma.post.findMany({ where: { userId } });
  }
}
```

The model contains **only database queries**. No business logic. No HTTP. If you need to add a query to find posts by status, add it here. Nothing else changes.

### `post.service.ts`

```ts
// src/api/v1/modules/posts/post.service.ts
import { postQueue } from '@/config/queue';
import { PostModel } from './post.model';
import { Post } from './post.type';

export class PostService {
  static async schedulePost(
    userId: number,
    content: string,
    platforms: string[],
    scheduledAt: Date,
  ): Promise<Post> {
    // 1. Write to the database
    const post = await PostModel.create(userId, content, platforms, scheduledAt);

    // 2. Calculate delay in milliseconds
    const delay = scheduledAt.getTime() - Date.now();

    // 3. If the scheduled time is in the future, enqueue a delayed job
    if (delay > 0) {
      await postQueue.add(
        'schedulePost',
        { postId: post.id, userId, content, platforms },
        { delay },
      );
    }

    return post;
  }

  static async getUserPosts(userId: number): Promise<Post[]> {
    return PostModel.findByUserId(userId);
  }
}
```

The service contains **business logic**. Here, "schedule a post" is a two-step operation: save to DB first, then enqueue a job. The model does not know this. The controller does not know this. Only the service does.

### `post.controller.ts`

```ts
// src/api/v1/modules/posts/post.controller.ts
import { Request, Response } from 'express';
import { PostService } from './post.service';

export class PostController {
  static async schedulePost(req: Request, res: Response) {
    const { content, platforms, scheduledAt } = req.body as {
      content: string;
      platforms: string[];
      scheduledAt: string;
    };
    const userId = req.user?.id; // Set by Passport JWT middleware
    try {
      const post = await PostService.schedulePost(
        userId!,
        content,
        platforms,
        new Date(scheduledAt), // Convert ISO string from JSON body to Date
      );
      res.status(201).json(post); // 201 Created
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  }

  static async getPosts(req: Request, res: Response) {
    const userId = req.user?.id;
    try {
      const posts = await PostService.getUserPosts(userId!);
      res.json(posts); // 200 OK (default)
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  }
}
```

The controller is the **HTTP translation layer**. It reads values from `req` (body, params, query, user), calls the service, and writes to `res`. It handles the try/catch and maps errors to HTTP status codes.

**Why cast `req.body`?** Express types `req.body` as `any` because it does not know your request shape. The cast `req.body as { content: string; ... }` tells TypeScript what shape to expect. In a production system you would add runtime validation (e.g., with Zod) to ensure the body actually matches before trusting it.

### `post.routes.ts`

```ts
// src/api/v1/modules/posts/post.routes.ts
import { Router } from 'express';
import { PostController } from './post.controller';

const router = Router();

router.post('/schedule', PostController.schedulePost);
router.get('/', PostController.getPosts);

export default router;
```

Routes only map HTTP verbs and paths to controller methods. Nothing else.

### How routes are wired together

In `src/app/main.ts`:

```ts
import postRoutes from '@/api/v1/modules/posts/post.routes';
// ...
const apiV1 = express.Router();
apiV1.use('/posts', postRoutes);
app.use('/api/v1', apiV1);
```

This means:
- `POST /api/v1/posts/schedule` → `PostController.schedulePost`
- `GET /api/v1/posts/` → `PostController.getPosts`

The path is assembled from three parts: `/api/v1` (top-level prefix) + `/posts` (module prefix) + `/schedule` (route suffix).

---

## 6. Express App and Middleware Chain

The entire app setup lives in `src/app/main.ts`. Here is the middleware chain in order:

```ts
import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import passport from 'passport';
import postRoutes from '@/api/v1/modules/posts/post.routes';
// ... other route imports
import '@/config/auth'; // Side-effect import: registers the Passport JWT strategy

dotenv.config(); // Load .env file into process.env

const app = express();

// 1. Security headers (must be first)
app.use(helmet());

// 2. CORS — controls which origins can call this API
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));

// 3. Parse JSON request bodies (limit prevents memory exhaustion attacks)
app.use(express.json({ limit: '10kb' }));

// 4. Initialize Passport (must come after express.json)
app.use(passport.initialize());

// 5. Global rate limiter — 200 requests per 15 minutes per IP
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' },
});

// 6. Stricter AI rate limiter — 15 requests per minute per IP
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 15,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'AI rate limit reached. Please wait a moment.' },
});

app.use(globalLimiter); // Applied globally

// 7. Versioned API router — all routes under /api/v1
const apiV1 = express.Router();

// JWT authentication on ALL /api/v1 routes
apiV1.use(passport.authenticate('jwt', { session: false }));

// Module routes
apiV1.use('/posts', postRoutes);
apiV1.use('/analytics', analyticsRoutes);
apiV1.use('/notifications', notificationRoutes);
apiV1.use('/accounts', accountRoutes);
apiV1.use('/teams', teamRoutes);
apiV1.use('/reviews', reviewRoutes);
apiV1.use('/discovery', discoveryRoutes);

// AI-specific limiter applied to expensive endpoints
apiV1.use('/reviews/generate', aiLimiter);
apiV1.use('/discovery/search', aiLimiter);
apiV1.use('/discovery/generate-response', aiLimiter);

app.use('/api/v1', apiV1);

// 8. Global error handler (must be last, must have 4 parameters)
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// 9. Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

**What is middleware?** A middleware is a function with the signature `(req, res, next) => void`. Express calls middlewares in the order they are registered. Each middleware can:
1. Modify `req` or `res`
2. Call `next()` to pass control to the next middleware
3. Send a response and stop the chain

```
Request → helmet() → cors() → json() → passport() → globalLimiter → [route handler] → Response
```

If any middleware sends a response (like the auth middleware returning 401), later middlewares do not run.

**The error handler is special.** Express recognizes an error handler by its four-parameter signature `(err, req, res, next)`. When any route calls `next(error)`, or when Express itself catches a thrown error, it skips to this handler.

---

## 7. Database with Prisma 5

### What is an ORM?

An ORM (Object-Relational Mapper) lets you talk to a relational database using the programming language's objects instead of raw SQL. Without Prisma:

```js
// Raw SQL
const result = await pool.query('SELECT * FROM posts WHERE user_id = $1', [userId]);
const posts = result.rows;
```

With Prisma:

```ts
// Type-safe ORM
const posts = await prisma.post.findMany({ where: { userId } });
// posts is typed as Post[] — TypeScript knows every field and its type
```

### The Prisma Singleton

```ts
// src/config/prisma.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export default prisma;
```

**Why a singleton?** `PrismaClient` maintains a connection pool to PostgreSQL. Creating a new instance per request would exhaust database connections. One instance shared across the whole app is the correct approach. In Node.js modules are cached after first `require()`, so importing this file always returns the same instance.

### The Schema

The Prisma schema at `prisma/schema.prisma` defines your database structure:

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL") // Read from .env
}

model Post {
  id          Int            @id @default(autoincrement())
  userId      Int            @map("user_id")     // TypeScript: userId, DB column: user_id
  content     String
  platforms   Json                               // Stored as JSON array in the DB
  scheduledAt DateTime       @map("scheduled_at")
  status      String
  createdAt   DateTime       @default(now()) @map("created_at")
  analytics   PostAnalytic[]                     // Relation: one post has many analytics
  notifications Notification[]

  @@map("posts") // The actual table name in PostgreSQL
}

model PostAnalytic {
  id       Int    @id @default(autoincrement())
  postId   Int    @map("post_id")
  platform String
  likes    Int    @default(0)
  shares   Int    @default(0)
  comments Int    @default(0)
  post     Post   @relation(fields: [postId], references: [id])

  @@unique([postId, platform]) // Compound unique index
  @@map("post_analytics")
}
```

The `@@map` directive separates the TypeScript name (`Post`, camelCase fields) from the SQL name (`posts`, snake_case columns). This is a best practice: SQL conventions use snake_case, TypeScript conventions use camelCase.

The `@@unique([postId, platform])` creates a compound unique constraint. A post can only have one analytics row per platform. Prisma names this constraint `postId_platform` automatically, which you use in upsert queries.

### Every Prisma Operation SocioBoom Uses

**Create:**
```ts
const post = await prisma.post.create({
  data: { userId, content, platforms, scheduledAt, status: 'scheduled' },
});
// Returns: the newly created Post object with id, createdAt, etc.
```

**Find many with filter:**
```ts
const posts = await prisma.post.findMany({
  where: { userId },
  orderBy: { createdAt: 'desc' },
});
```

**Find one by unique field:**
```ts
const painPoint = await prisma.painPoint.findUnique({
  where: { id: painPointId },
});
// Returns: PainPoint | null
```

**Update:**
```ts
const updated = await prisma.painPoint.update({
  where: { id: painPointId },
  data: { generatedResponse: response },
});
```

**Upsert (create or update):**
```ts
// If a row with this postId+platform exists, update it. Otherwise create it.
const analytic = await prisma.postAnalytic.upsert({
  where: { postId_platform: { postId, platform } },
  update: { likes, shares, comments },
  create: { postId, platform, likes, shares, comments },
});
```

`postId_platform` is the name Prisma generated for the `@@unique([postId, platform])` constraint. The naming pattern is always `fieldA_fieldB`.

**Relational query (OR filter):**
```ts
const teams = await prisma.team.findMany({
  where: {
    OR: [
      { ownerId: userId },                      // Teams this user owns
      { members: { some: { userId } } },        // Teams this user is a member of
    ],
  },
});
```

**Delete:**
```ts
const deleted = await prisma.user.delete({ where: { id } });
```

### Prisma Migrations

When you change the schema, you create a migration:

```bash
# During development: create and apply a migration
npx prisma migrate dev --name add_review_posts

# In production: apply pending migrations
npx prisma migrate deploy

# After cloning the repo (generate the TypeScript client from the schema)
npx prisma generate
```

A migration is a SQL file that Prisma creates automatically by diffing your schema against the current database state. Migrations are committed to git. This means the database schema is version-controlled alongside your code.

**Why Prisma instead of raw SQL?** Several reasons:
- Type safety: every query result is typed, errors are caught at compile time.
- Auto-generated client: no manual SQL for common operations.
- Migrations: schema changes are tracked, reviewable, and reproducible.
- Relations: join queries written in TypeScript, not SQL string concatenation.
- Switching databases: change `provider = "postgresql"` to `provider = "mysql"` and recompile.

### Legacy Database Pool

`src/config/db.ts` uses the raw `pg` pool (Node.js PostgreSQL driver). This was the original database access before Prisma was added. It is kept for reference and historical accuracy but is not used in any module. All database access goes through `src/config/prisma.ts`.

---

## 8. Authentication with Passport JWT

### What is JWT?

JWT (JSON Web Token) is a string that encodes a payload (like `{ userId: 42 }`) and signs it with a secret key. The server creates the token when the user logs in and sends it to the client. The client includes it in every subsequent request. The server verifies the signature to confirm the token came from itself and was not tampered with.

A JWT looks like: `header.payload.signature` — three base64-encoded segments separated by dots.

### Why JWTs?

JWTs are **stateless**. The server does not need to store session data in a database or Redis — it just checks the signature. This makes horizontal scaling (multiple server instances) trivial.

### Passport JWT Strategy

`src/config/auth.ts` registers the strategy (implementation details TBD in the codebase, but the pattern is):

```ts
// src/config/auth.ts
import passport from 'passport';
import { Strategy as JwtStrategy, ExtractJwt } from 'passport-jwt';
import prisma from '@/config/prisma';

passport.use(
  new JwtStrategy(
    {
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: process.env.JWT_SECRET!,
    },
    async (payload, done) => {
      try {
        const user = await prisma.user.findUnique({ where: { id: payload.sub } });
        if (!user) return done(null, false);
        return done(null, user); // Attaches user to req.user
      } catch (err) {
        return done(err, false);
      }
    },
  ),
);
```

The `ExtractJwt.fromAuthHeaderAsBearerToken()` extractor reads the `Authorization: Bearer <token>` header from each request.

In `main.ts`, this line protects all `/api/v1` routes:

```ts
apiV1.use(passport.authenticate('jwt', { session: false }));
```

`{ session: false }` disables Passport's session middleware (you do not need sessions when using JWTs). If the token is missing or invalid, Passport sends a `401 Unauthorized` response before your controller ever runs.

The `import '@/config/auth'` at the top of `main.ts` is a side-effect import — it runs the file for its side effect (registering the strategy) without importing anything from it.

---

## 9. Security: Helmet, CORS, Rate Limiting

### Helmet

```ts
app.use(helmet());
```

Helmet sets several HTTP response headers that protect against common web vulnerabilities:

| Header | Protection against |
|---|---|
| `X-DNS-Prefetch-Control: off` | DNS prefetch leaking |
| `X-Frame-Options: SAMEORIGIN` | Clickjacking |
| `X-Content-Type-Options: nosniff` | MIME type sniffing |
| `Strict-Transport-Security` | Protocol downgrade attacks |
| `Content-Security-Policy` | XSS, data injection |
| `X-XSS-Protection: 0` | Turns off the buggy browser XSS filter |

Without Helmet, none of these headers are set. Browsers use them as defense layers. Attackers who find other vulnerabilities have fewer avenues to exploit.

### CORS

CORS (Cross-Origin Resource Sharing) is a browser security feature. When JavaScript at `https://app.socioboom.com` tries to call `https://api.socioboom.com`, the browser first asks the API: "do you allow requests from this origin?" The API responds with `Access-Control-Allow-Origin: https://app.socioboom.com`. Only then does the browser allow the request.

```ts
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true, // Allows cookies and Authorization headers
}));
```

CORS protection is enforced by the browser. Server-to-server requests (like from Postman or curl) are not subject to CORS. This is fine — the JWT authentication handles server-level access control.

### Rate Limiting

Rate limiting prevents a single user or IP from overwhelming the server.

```ts
// Global: 200 requests per 15 minutes
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes in milliseconds
  max: 200,
  standardHeaders: true,    // Send RateLimit-* headers (RFC 6585)
  legacyHeaders: false,     // Do not send X-RateLimit-* headers
  message: { error: 'Too many requests, please try again later.' },
});

// AI endpoints: 15 requests per minute
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 15,
  message: { error: 'AI rate limit reached. Please wait a moment.' },
});
```

**Why stricter limits on AI endpoints?** Each AI request calls Anthropic or OpenRouter, which costs money and takes 2–10 seconds. Without a limit, a single user (or attacker who steals a JWT) could run up a huge API bill in seconds. 15 AI requests per minute is generous for real use but stops abuse.

The `windowMs` is a sliding window — each request is tracked with a timestamp. When the window resets, old requests fall off. `express-rate-limit` stores counts in memory by default. For a multi-server deployment, you would use the `redis` store option so all instances share the same counter.

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

## 11. AI Provider Abstraction

### The Problem

You want to call an AI model. But which model? Anthropic's API is different from OpenAI's API. If you hard-code Anthropic calls everywhere, switching to another provider means changing dozens of files.

### The Solution

Create a single function that is the only thing the rest of the codebase calls. Hide which provider is used behind an environment variable.

```ts
// src/api/v1/shared/services/ai.ts
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';

// Read provider at startup (not per request — avoids overhead)
const provider = (process.env.AI_PROVIDER || 'anthropic') as 'anthropic' | 'openrouter';

// Initialize the Anthropic client once
const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// The only export — the single interface the rest of the codebase uses
export async function generateText(systemPrompt: string, userPrompt: string): Promise<string> {
  if (provider === 'openrouter') {
    return generateWithOpenRouter(systemPrompt, userPrompt);
  }
  return generateWithAnthropic(systemPrompt, userPrompt);
}
```

Every service that needs AI calls `generateText(system, user)` and gets back a string. It does not know or care which model ran.

### Anthropic Implementation (Extended Thinking)

```ts
async function generateWithAnthropic(systemPrompt: string, userPrompt: string): Promise<string> {
  const stream = anthropic.messages.stream({
    model: 'claude-opus-4-8',
    max_tokens: 8000,
    thinking: { type: 'adaptive' }, // Adaptive thinking: model decides when to think deeply
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
  });

  // Wait for the full response (streaming resolves to the final message)
  const message = await stream.finalMessage();

  // The response can contain thinking blocks (internal reasoning) and text blocks
  // We only want the text blocks
  for (const block of message.content) {
    if (block.type === 'text') return block.text;
  }
  return '';
}
```

`thinking: { type: 'adaptive' }` tells the model to use extended thinking when the query warrants it. The model produces "thinking" content blocks (its internal reasoning chain) followed by text blocks (the actual answer). The code filters for text blocks only.

`stream.finalMessage()` waits for the complete response even though we're using the streaming API. The reason to use the streaming API anyway: it allows real-time progress reporting and has better timeout handling for long-running responses.

### OpenRouter Implementation

```ts
async function generateWithOpenRouter(systemPrompt: string, userPrompt: string): Promise<string> {
  const model = process.env.OPENROUTER_MODEL || 'anthropic/claude-opus-4-8';

  const { data } = await axios.post(
    'https://openrouter.ai/api/v1/chat/completions',
    {
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
    },
    {
      headers: {
        Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': process.env.APP_URL || 'http://localhost:3000',
        // HTTP-Referer is required by OpenRouter for rate limiting and attribution
      },
    },
  );

  return (data.choices[0]?.message?.content as string) ?? '';
}
```

OpenRouter's API follows the OpenAI ChatCompletion format. The response shape is `{ choices: [{ message: { content: string } }] }`. The optional chaining (`?.`) and nullish coalescing (`?? ''`) handle edge cases where the response is malformed.

### When to Use Which Provider

- **`AI_PROVIDER=anthropic`** (default): Direct Anthropic API with extended thinking. Best for quality. Requires `ANTHROPIC_API_KEY`.
- **`AI_PROVIDER=openrouter`**: Routes through OpenRouter, which aggregates many model providers. Useful for fallback, cost comparison, or accessing models not directly available. Requires `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL`.

Switching providers requires only changing `.env`. Zero code changes.

---

## 12. All Modules: A Complete Tour

Here is every module, what it does, its routes, and its key logic.

### Users Module (`/api/v1/users`)

**What it does:** Manages user accounts (CRUD).

**Key file:** `user.repo.ts` — this module has a repository instead of a model, distinguishing low-level DB access from higher-level operations. (The pattern is the same; the naming varies.)

**Routes:** Not wired into the main router yet (implementation in progress).

**Key Prisma queries:**
```ts
prisma.user.findMany()
prisma.user.findUnique({ where: { id } })
prisma.user.create({ data: { name, email } })
prisma.user.update({ where: { id }, data: { name, email } })
prisma.user.delete({ where: { id } })
```

### Posts Module (`/api/v1/posts`)

**What it does:** Create and retrieve scheduled social media posts.

**Routes:**
- `POST /api/v1/posts/schedule` — create a scheduled post, enqueue delayed BullMQ job
- `GET /api/v1/posts/` — get all posts for the authenticated user

### Analytics Module (`/api/v1/analytics`)

**What it does:** Store and retrieve engagement metrics (likes, shares, comments) per post per platform.

**Routes:**
- `GET /api/v1/analytics/:postId` — get analytics for a specific post

**Key concept — upsert:** Analytics are fetched periodically and the numbers change. Using upsert means the first fetch creates the row; subsequent fetches update it. Without upsert you would need a check-then-create-or-update pattern with a race condition.

**Key concept — repeating jobs:**
```ts
await analyticsQueue.add(
  'fetchAnalytics',
  { postId, platform },
  { repeat: { every: 3600000 } }, // Every 1 hour
);
```

### Notifications Module (`/api/v1/notifications`)

**What it does:** Track engagement events (likes, comments) as notifications for users.

**Routes:**
- `GET /api/v1/notifications/` — get all notifications for the authenticated user

**Key concept:** Notifications are generated by a BullMQ worker that runs every 5 minutes, not by a user-initiated request.

### Accounts Module (`/api/v1/accounts`)

**What it does:** Store OAuth tokens for connected social media accounts (Twitter access token, etc.).

**Routes:**
- `GET /api/v1/accounts/` — list the user's connected accounts

**Key concept:** When a user connects their Twitter account via OAuth, the frontend exchanges the OAuth code for an access token, then calls `POST /api/v1/accounts/connect` (not yet wired) to save the token. The worker later uses this token when posting.

### Teams Module (`/api/v1/teams`)

**What it does:** Create and manage teams. A user can own a team or be a member with a role (admin, editor, viewer).

**Routes:**
- `POST /api/v1/teams/` — create a team (creator is automatically added as admin)
- `GET /api/v1/teams/` — list teams the user owns or belongs to

**Key concept — OR query with relations:**
```ts
prisma.team.findMany({
  where: {
    OR: [
      { ownerId: userId },
      { members: { some: { userId } } }, // "some" = at least one matching member
    ],
  },
});
```

### Reviews Module (`/api/v1/reviews`)

**What it does:** Fetch customer reviews from external platforms and generate AI-powered marketing posts from them.

**Routes:**
- `POST /api/v1/reviews/fetch-google` — fetch reviews from Google Places API
- `POST /api/v1/reviews/fetch-yelp` — fetch reviews from Yelp Fusion API
- `POST /api/v1/reviews/fetch-twitter` — fetch Twitter mentions
- `POST /api/v1/reviews/fetch-reddit` — fetch Reddit posts mentioning the business
- `POST /api/v1/reviews/generate` — (AI-rate-limited) generate social media posts from reviews
- `POST /api/v1/reviews/save` — save a generated post to the database
- `GET /api/v1/reviews/` — list saved review posts for the user

Covered in depth in Section 13.

### Discovery Module (`/api/v1/discovery`)

**What it does:** Find people complaining about problems your product solves and generate authentic replies.

**Routes:**
- `POST /api/v1/discovery/search` — (AI-rate-limited) run the full discovery pipeline
- `POST /api/v1/discovery/generate-response` — (AI-rate-limited) generate a reply for a specific pain point
- `GET /api/v1/discovery/` — list discovery sessions for the user
- `GET /api/v1/discovery/:sessionId/pain-points` — list pain points for a session

Covered in depth in Section 14.

---

## 13. Feature Deep-Dive: Review Poster

The Review Poster feature transforms the problem of writing marketing content into a three-step workflow: fetch → select → generate.

### Step 1: Fetch Reviews from Platforms

**Google Places:**

```ts
static async fetchGoogleReviews(businessName: string): Promise<Review[]> {
  const apiKey = process.env.GOOGLE_PLACES_API_KEY;

  // Step A: Find the place_id for the business name
  const searchRes = await axios.get(
    'https://maps.googleapis.com/maps/api/place/findplacefromtext/json',
    {
      params: {
        input: businessName,
        inputtype: 'textquery',
        fields: 'place_id,name',
        key: apiKey,
      },
    },
  );
  const placeId = searchRes.data.candidates?.[0]?.place_id;
  if (!placeId) return []; // Business not found

  // Step B: Fetch the reviews using the place_id
  const detailRes = await axios.get(
    'https://maps.googleapis.com/maps/api/place/details/json',
    {
      params: {
        place_id: placeId,
        fields: 'reviews,name',
        key: apiKey,
      },
    },
  );

  // Step C: Normalize the response into the Review interface
  const rawReviews = detailRes.data.result?.reviews ?? [];
  return rawReviews.map((r) => ({
    source: 'google' as const,
    businessName: detailRes.data.result?.name ?? businessName,
    reviewerName: r.author_name,
    reviewText: r.text ?? '',
    rating: r.rating,
  }));
}
```

The Google Places API requires two calls: one to find the `place_id` from a text search, and one to fetch details (including reviews) using that `place_id`. The free tier returns up to 5 reviews per business.

**Yelp:**

```ts
static async fetchYelpReviews(businessName: string, location = 'US'): Promise<Review[]> {
  const headers = { Authorization: `Bearer ${process.env.YELP_API_KEY}` };

  // Search for the business
  const searchRes = await axios.get('https://api.yelp.com/v3/businesses/search', {
    headers,
    params: { term: businessName, location, limit: 1 },
  });

  const bizId: string = searchRes.data.businesses?.[0]?.id;
  if (!bizId) return [];

  // Fetch reviews for that specific business
  const reviewsRes = await axios.get(
    `https://api.yelp.com/v3/businesses/${bizId}/reviews`,
    { headers },
  );

  return (reviewsRes.data.reviews ?? []).map((r) => ({
    source: 'yelp' as const,
    businessName: searchRes.data.businesses[0].name,
    reviewerName: r.user?.name,
    reviewText: r.text ?? '',
    rating: r.rating,
  }));
}
```

**Twitter Mentions:**

```ts
static async fetchTwitterMentions(businessName: string): Promise<Review[]> {
  const { data } = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
    params: {
      query: `"${businessName}" -is:retweet lang:en`,
      max_results: 25,
      'tweet.fields': 'author_id,text',
      expansions: 'author_id',    // Include user objects in the response
      'user.fields': 'username',
    },
    headers: { Authorization: `Bearer ${process.env.TWITTER_BEARER_TOKEN}` },
  });

  // Build a lookup from userId → username
  const users: Record<string, string> = {};
  for (const u of data.includes?.users ?? []) users[u.id] = u.username;

  return (data.data ?? []).map((tweet) => ({
    source: 'twitter' as const,
    businessName,
    reviewerName: tweet.author_id ? `@${users[tweet.author_id]}` : undefined,
    reviewText: tweet.text,
  }));
}
```

Twitter's v2 API uses "expansions" — you request `author_id` on tweets and `expansions: 'author_id'` to get user objects included in the same response. Without expansions you would need a second API call per tweet to look up usernames.

### Step 2: AI Post Generation

```ts
static async generatePosts(req: GeneratePostsRequest): Promise<GeneratedPost[]> {
  const { reviews, businessName, tone = 'professional', targetPlatforms = ['twitter', 'instagram', 'linkedin'] } = req;

  // The system prompt defines the AI's persona and constraints
  const system = `You are a social media marketing expert. Convert customer reviews into compelling social media posts.
Tone: ${tone}. Target platforms: ${targetPlatforms.join(', ')}.
Rules: Keep posts concise, highlight the positive, add relevant emojis, include a call-to-action where natural.
If a business name is provided, mention it naturally. Do NOT make up any details not in the review.`;

  const results: GeneratedPost[] = [];

  // Generate one post per review (sequential to avoid rate limits)
  for (const review of reviews) {
    const user = `Business: ${businessName || review.businessName || 'our business'}
Reviewer: ${review.reviewerName ?? 'a customer'}
Rating: ${review.rating ? `${review.rating}/5` : 'not specified'}
Review: "${review.reviewText}"

Write one social media post that celebrates this review and encourages others to try us out. Return only the post text, no labels.`;

    const content = await generateText(system, user);
    results.push({ review, content });
  }

  return results;
}
```

Key prompt engineering decisions:
- The system prompt establishes tone and platform context once, not per review.
- "Return only the post text, no labels" prevents the AI from prefixing with "Here's your post:".
- "Do NOT make up any details" is a grounding constraint to prevent hallucination.
- Sequential `for...of` instead of `Promise.all` avoids hitting rate limits on the AI provider.

### Step 3: Save and Schedule

After the user selects which generated posts they like, they call:
- `POST /api/v1/reviews/save` to persist the selection to the `ReviewPost` table.
- `POST /api/v1/posts/schedule` (the existing post scheduling endpoint) to actually schedule the post for publishing.

The Review Poster reuses the existing post scheduling system — it does not implement its own scheduling logic.

---

## 14. Feature Deep-Dive: Pain-Point Discovery

This is the most algorithmically complex feature. It chains five AI and API calls in a pipeline.

### The Full Pipeline

```
User sends: { appDescription: "SocioBoom schedules social posts", platforms: ["reddit", "twitter"] }

Step 1: AI extracts search keywords
  → ["can't keep up with social media", "automate instagram posting", "social media scheduling tool"]

Step 2: Search Reddit and/or Twitter with those keywords
  → 50 raw posts

Step 3: AI filters for genuine pain points relevant to the product
  → 12 relevant posts

Step 4: Save session and pain points to database
  → { session: {...}, painPoints: [...] }

Step 5 (later, on demand): AI generates an authentic reply for a specific pain point
  → "I totally get this struggle! I used to spend hours on social media. SocioBoom..."
```

### Step 1: Keyword Extraction

```ts
static async extractKeywords(appDescription: string): Promise<string[]> {
  const system = 'You are a market research expert. Extract search keywords from an app description.';

  const user = `App: "${appDescription}"

Return 5-8 short phrases that people complaining about problems this app solves would likely write.
Examples: "I hate manually posting to instagram", "no time to manage social media"
Return ONLY a JSON array of strings, nothing else.`;

  const raw = await generateText(system, user);

  // Extract JSON from the response (handle case where AI adds surrounding text)
  const match = raw.match(/\[[\s\S]*\]/);
  if (!match) return [appDescription]; // Fallback to the description itself
  return JSON.parse(match[0]) as string[];
}
```

The regex `\[[\s\S]*\]` matches everything from the first `[` to the last `]`, including newlines. This handles cases where the AI puts the JSON array on multiple lines or adds surrounding text. It is a defensive parsing pattern.

### Step 2: Multi-Platform Search

```ts
static async runDiscovery(userId: number, req: SearchRequest) {
  const { appDescription, platforms } = req;

  // Create a session record first (tracks this discovery run)
  const session = await DiscoveryModel.createSession(userId, appDescription, platforms);

  // Get keywords from AI
  const keywords = await DiscoveryService.extractKeywords(appDescription);

  // Search each requested platform in parallel... or sequentially here
  const rawPosts: RawPost[] = [];
  if (platforms.includes('reddit')) {
    const posts = await DiscoveryService.searchReddit(keywords);
    rawPosts.push(...posts);
  }
  if (platforms.includes('twitter')) {
    const posts = await DiscoveryService.searchTwitter(keywords);
    rawPosts.push(...posts);
  }

  // AI filters the results
  const filtered = await DiscoveryService.filterPainPoints(rawPosts, appDescription);

  // Save each filtered post as a PainPoint
  const painPoints: PainPoint[] = [];
  for (const post of filtered) {
    const saved = await DiscoveryModel.savePainPoint(session.id, post);
    painPoints.push(saved);
  }

  return { session, painPoints };
}
```

**Reddit search:**
```ts
static async searchReddit(keywords: string[]): Promise<RawPost[]> {
  const token = await DiscoveryService.getRedditToken();
  const query = keywords.join(' OR '); // Reddit search syntax: keyword1 OR keyword2 OR ...

  const { data } = await axios.get('https://oauth.reddit.com/search', {
    params: { q: query, limit: 25, sort: 'relevance', type: 'link' },
    headers: {
      Authorization: `Bearer ${token}`,
      'User-Agent': 'SocioBoom/1.0', // Reddit requires a User-Agent
    },
  });

  return (data.data?.children ?? []).map((child) => ({
    platform: 'reddit' as DiscoveryPlatform,
    subreddit: child.data.subreddit,
    postUrl: child.data.permalink ? `https://reddit.com${child.data.permalink}` : undefined,
    postAuthor: child.data.author,
    postContent: child.data.selftext || child.data.title || '',
  }));
}
```

**Twitter search:**
```ts
static async searchTwitter(keywords: string[]): Promise<RawPost[]> {
  // Wrap each keyword in quotes for exact phrase matching
  const query = keywords.map((k) => `"${k}"`).join(' OR ');

  const { data } = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
    params: {
      query: `${query} -is:retweet lang:en`, // Exclude retweets, English only
      max_results: 25,
      'tweet.fields': 'author_id,text',
      expansions: 'author_id',
      'user.fields': 'username',
    },
    headers: { Authorization: `Bearer ${process.env.TWITTER_BEARER_TOKEN}` },
  });

  const users: Record<string, string> = {};
  for (const u of data.includes?.users ?? []) {
    users[u.id] = u.username;
  }

  return (data.data ?? []).map((tweet) => ({
    platform: 'twitter' as DiscoveryPlatform,
    postUrl: `https://twitter.com/i/web/status/${tweet.id}`,
    postAuthor: tweet.author_id ? users[tweet.author_id] : undefined,
    postContent: tweet.text,
  }));
}
```

### Step 3: AI Filtering

```ts
static async filterPainPoints(posts: RawPost[], appDescription: string): Promise<RawPost[]> {
  if (posts.length === 0) return [];

  const system = 'You are a market research analyst identifying genuine pain points relevant to a product.';

  const user = `Product: "${appDescription}"

Posts to evaluate:
${posts.map((p, i) => `${i}. "${p.postContent.slice(0, 300)}"`).join('\n')}

Return ONLY a JSON array of the indices (0-based) of posts that express a genuine pain point this product could solve. Example: [0, 2, 5]`;

  const raw = await generateText(system, user);

  // Parse the index array from the AI response
  const match = raw.match(/\[[\s\S]*?\]/); // Non-greedy: first complete array
  if (!match) return posts; // If parsing fails, return all posts (fail open)

  const indices = JSON.parse(match[0]) as number[];
  return indices.map((i) => posts[i]).filter(Boolean); // filter(Boolean) removes any undefined
}
```

Sending all posts in one AI call (batch filtering) is far more efficient than filtering each post individually. The AI sees the full context and can make comparative judgments. The `slice(0, 300)` prevents the prompt from becoming too long if posts are very lengthy.

### Step 4: Generate a Reply (On Demand)

```ts
static async generateResponse(
  painPointContent: string,
  appDescription: string,
  platform: DiscoveryPlatform,
): Promise<string> {
  const system = `You are a savvy growth marketer writing authentic ${platform} replies that help people with their problems while naturally mentioning a relevant product.
Rules: Sound human, not like an ad. Lead with empathy and a useful tip. Mention the product organically, not as a pitch. Keep it under 280 characters for Twitter.`;

  const user = `Our product: "${appDescription}"

Their post: "${painPointContent}"

Write a helpful reply that addresses their pain point and naturally introduces our product as a solution. Return only the reply text.`;

  return generateText(system, user);
}
```

The platform-specific instruction (`Keep it under 280 characters for Twitter`) is built into the prompt. The system prompt instructs the AI to sound human, not like an advertisement, which is critical for this to work — blatant ads get downvoted and banned.

---

## 15. External API Calls with Axios

Axios is an HTTP client. SocioBoom uses it for every external API call.

### Basic Pattern

```ts
import axios from 'axios';

// GET with query params and headers
const { data } = await axios.get('https://api.example.com/resource', {
  params: { key: 'value' },           // Appended to URL: ?key=value
  headers: { Authorization: 'Bearer token' },
});

// POST with JSON body
const { data } = await axios.post('https://api.example.com/resource', body, {
  headers: { 'Content-Type': 'application/json' },
});

// POST with form-encoded body (for OAuth token endpoints)
await axios.post(
  'https://www.reddit.com/api/v1/access_token',
  'grant_type=client_credentials',    // String body, not object
  {
    auth: { username: clientId, password: clientSecret }, // Basic auth
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  },
);
```

**Why axios instead of the built-in `fetch`?** In Node.js 22, `fetch` is available natively. Axios provides:
- Automatic JSON serialization/deserialization
- Query parameter serialization (`params` option)
- Basic auth shortcut (`auth` option)
- Consistent error handling (throws on 4xx/5xx status codes)
- Better TypeScript types

### Error Handling for External API Calls

External APIs can fail. When they do, the controller's try/catch catches the error and returns a 500 response:

```ts
static async fetchGoogle(req: Request, res: Response) {
  try {
    const reviews = await ReviewService.fetchGoogleReviews(businessName);
    res.json({ reviews });
  } catch (error) {
    // If the Google API is down, or the key is invalid, or the business is not found:
    res.status(500).json({ error: (error as Error).message });
  }
}
```

For production, you would differentiate error types:
- API key invalid → 500 (server misconfiguration)
- Business not found → 404
- Google API temporarily down → 503 with retry advice

---

## 16. OAuth: Reddit App-Only Token Flow

Reddit requires OAuth even for public read-only data. SocioBoom uses the "app-only" flow (also called "client credentials") which does not require a user to log in — it just authenticates the application itself.

### The Flow

```
SocioBoom server
  → POST https://www.reddit.com/api/v1/access_token
      Authorization: Basic base64(clientId:clientSecret)
      Body: grant_type=client_credentials

Reddit
  → { access_token: "xyz", expires_in: 3600, token_type: "bearer" }

SocioBoom server
  → GET https://oauth.reddit.com/search
      Authorization: Bearer xyz
      User-Agent: SocioBoom/1.0
```

### Token Caching

Making an OAuth token request before every API call wastes time and hits Reddit's rate limits. Instead, SocioBoom caches the token in memory:

```ts
private static redditToken: string | null = null;
private static redditTokenExpiry = 0; // Unix timestamp in ms

private static async getRedditToken(): Promise<string> {
  // If we have a valid cached token, return it immediately
  if (DiscoveryService.redditToken && Date.now() < DiscoveryService.redditTokenExpiry) {
    return DiscoveryService.redditToken;
  }

  // Otherwise, fetch a new token
  const { data } = await axios.post(
    'https://www.reddit.com/api/v1/access_token',
    'grant_type=client_credentials',
    {
      auth: {
        username: process.env.REDDIT_CLIENT_ID!,
        password: process.env.REDDIT_CLIENT_SECRET!,
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'SocioBoom/1.0',
      },
    },
  );

  // Cache the token. The - 60_000 gives a 1-minute buffer before expiry.
  DiscoveryService.redditToken = data.access_token as string;
  DiscoveryService.redditTokenExpiry = Date.now() + (data.expires_in as number) * 1000 - 60_000;

  return DiscoveryService.redditToken;
}
```

`expires_in` is in seconds (typically 3600 = 1 hour). Converting: `expires_in * 1000` = milliseconds. Subtracting `60_000` (1 minute) means the token is considered expired 1 minute before Reddit actually expires it — a safety buffer for clock skew and slow network calls.

**Important:** This cache is in the Node.js process memory. If you run multiple instances of the server, each has its own cached token. This is fine because each token is independently valid. For very high traffic, you could move the cache to Redis to share it across instances, but it is unnecessary here.

Both `ReviewService` and `DiscoveryService` implement this pattern independently. In a larger codebase, you would extract this into a shared `RedditAuthService`.

### Why `'grant_type=client_credentials'` as a String?

Reddit's token endpoint uses `application/x-www-form-urlencoded` encoding, not JSON. This means the body is a URL-encoded key-value string like `key=value&key2=value2`. Axios sends a string body as-is. If you passed an object `{ grant_type: 'client_credentials' }` without the right headers, Axios would serialize it as JSON, and Reddit's server would reject it.

---

## 17. Environment Variables and Secret Management

### The `.env` File

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/socioboom

# Server
PORT=3001
FRONTEND_URL=http://localhost:3000
JWT_SECRET=your-long-random-secret-string

# AI
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-opus-4-8
APP_URL=http://localhost:3001

# Social platforms
GOOGLE_PLACES_API_KEY=...
YELP_API_KEY=...
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

### How `dotenv` Works

```ts
import dotenv from 'dotenv';
dotenv.config(); // Reads .env and adds each variable to process.env
```

`dotenv.config()` must be called before any code reads `process.env`. That is why it is at the top of `main.ts`.

`.env` is in `.gitignore`. It is never committed to version control. Each developer and each deployment environment has its own `.env` file. This ensures:
- Development keys are never in production
- Production secrets are never in git history
- Different developers can use different API keys

### The `!` Non-Null Assertion

```ts
const token = data.access_token as string;
const clientId = process.env.REDDIT_CLIENT_ID!;
```

The `!` tells TypeScript "I know this value cannot be null or undefined at runtime." It suppresses the TypeScript error `Object is possibly 'undefined'`. Use it only when you are genuinely certain — if `REDDIT_CLIENT_ID` is not set, the code will fail at runtime with a confusing error. In production-quality code, you would validate all required environment variables at startup:

```ts
// At startup, fail loudly if required env vars are missing
const required = ['DATABASE_URL', 'JWT_SECRET', 'ANTHROPIC_API_KEY'];
for (const key of required) {
  if (!process.env[key]) throw new Error(`Missing required env var: ${key}`);
}
```

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

## 22. Single-Shot Prompts vs AI Agents

The original Pain-Point Discovery was a **pipeline**: three fixed steps, each a single LLM call.

```
extractKeywords(description)      → 1 LLM call, returns phrases
webSearch(phrases) per platform   → fixed queries, snippets only
generateText(filter prompt)       → 1 LLM call over 5,000 chars of snippets
```

It worked, but every weakness traced back to the same root cause: **the pipeline can't react to what it finds.**

- If the extracted keywords were bad, the whole session was bad — nothing could reformulate.
- It only ever saw search *snippets*, never the actual posts, so "pain points" were often truncated titles.
- If a search returned 2 results, it shipped 2 results instead of trying a different angle.

The rewrite replaced the pipeline with an **agent**: one model in a loop with tools, deciding for itself what to do next.

```
loop (max N steps):
  model looks at everything so far
  → calls search_web / search_reddit / fetch_page / save_pain_point
  → tool results are appended to the conversation
  → repeat until the model stops calling tools (or budget runs out)
```

The core loop (`shared/services/agent.ts`) is ~60 lines per provider. The Anthropic version:

```ts
const messages: Anthropic.MessageParam[] = [{ role: 'user', content: prompt }];

while (steps < maxSteps) {
  steps++;
  const outOfBudget = steps === maxSteps;
  const res = await client.messages.create({
    model, max_tokens: 4000, system, messages,
    tools: anthropicTools,
    // Last turn: force a text wrap-up instead of more tool calls
    ...(outOfBudget ? { tool_choice: { type: 'none' as const } } : {}),
  });
  messages.push({ role: 'assistant', content: res.content });

  const toolUses = res.content.filter((b) => b.type === 'tool_use');
  if (!toolUses.length) return { finalText: lastText, steps, toolCalls };

  const results = [];
  for (const tu of toolUses) {
    results.push({
      type: 'tool_result',
      tool_use_id: tu.id,
      content: await safeExecute(toolMap.get(tu.name), tu.name, tu.input),
    });
  }
  messages.push({ role: 'user', content: results });
}
```

Key mechanics worth memorizing:

1. **Every `tool_use` block must be answered with a `tool_result`** in the next user message, matched by `tool_use_id`. If you drop one, the API rejects the request.
2. **Tool errors go back as text, not exceptions.** `safeExecute` catches everything and returns `"Error: ..."` — the agent reads the error and adapts (retries with different input, tries another tool). An unhandled throw would kill the whole run over one bad URL.
3. **Cap tool-result size** (we truncate at 6,000 chars). A fetched web page can be 500 KB of HTML; without a cap one tool call blows the context window and your budget.
4. **Budget the loop with `maxSteps`, and force a wrap-up on the last step** using `tool_choice: 'none'` so you always get a final summary instead of a half-finished tool call.
5. The OpenRouter version is the same loop with OpenAI-style `tools`/`tool_calls`/`role: "tool"` messages — writing both keeps BYOK users on whichever provider they configured.

**When to use which** (the actual decision framework applied to this codebase):

| Task | Shape | Choice |
|---|---|---|
| Topic → platform posts | one input, one output | single-shot |
| Review → social post | one input, one output | single-shot |
| Pain point → reply | one input, one output | single-shot |
| Find pain points across the web | search → read → judge → refine → repeat | **agent** |
| Find reviews of a business | search → open review pages → extract | **agent (small budget)** |

An agent adds latency and cost per run, so it must buy you something: *iteration* (reformulating failed searches) and *tool access* (reading the actual page). If the task has neither — it's a pure text transformation — an agent is just a slower prompt.

---

## 23. Structured Output: Forced Tool Use Instead of Regex

The old code asked the model for JSON and then went fishing:

```ts
const raw = await generateText(system, userPrompt, aiKeys);
const match = raw.match(/\[[\s\S]*\]/);   // find something array-shaped
if (!match) return [];                    // silently give up
const posts = JSON.parse(match[0]);       // hope it parses
```

Three failure modes, all silent:
- The model wraps the JSON in prose or markdown fences → regex may grab garbage.
- The model apologizes instead of answering → `return []` looks identical to "no results."
- The JSON parses but has the wrong shape → crash later, far from the cause.

The fix on Anthropic is **forced tool use**. You define a tool whose `input_schema` is your output schema, then force the model to "call" it. The model physically cannot reply with prose — the only legal output is arguments matching your schema:

```ts
const message = await client.messages.create({
  model, max_tokens: 4000, system,
  messages: [{ role: 'user', content: userPrompt }],
  tools: [{ name: 'emit_result', description: 'Emit the structured result.', input_schema: schema }],
  tool_choice: { type: 'tool', name: 'emit_result' },   // ← the forcing
});
const block = message.content.find((b) => b.type === 'tool_use');
return block.input as T;   // already parsed, already schema-shaped
```

Gotchas learned the hard way:

1. **The schema root must be `type: "object"`.** If you want an array, wrap it: `{ keywords: string[] }` instead of `string[]`.
2. **Forced `tool_choice` is incompatible with extended thinking** — thinking only allows `auto`/`none`. `generateJSON` therefore doesn't pass `thinking`, while free-text `generateText` does.
3. OpenRouter doesn't support Anthropic's forcing across all models, so the fallback is `response_format: { type: 'json_object' }` plus a *tolerant* parser (strip fences, then find the first `{...}`/`[...]`). Tolerance is the fallback, not the default.

Also fixed in the same pass: `generate.controller` passes `enum: platforms` on the platform field, so the model can't invent `"Twitter/X"` when the frontend expects `"twitter"`. Push every constraint you have into the schema — each one is a class of bug the model can no longer produce.

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

## 25. Grounding an Agent: URL Allowlists, Page Fetching, SSRF

### The hallucinated-URL bug (a real one)

The old validation tried to detect fake URLs with a pattern check:

```ts
const isReal = url && (realUrls.has(url)
  || /reddit\.com\/r\/\w+\/comments\//.test(url)    // ← the hole
  || /twitter\.com|x\.com/.test(url));
```

See the flaw? A model that invents `https://reddit.com/r/startups/comments/abc123/fake_post/` produces a **well-formed** URL — the regex happily passes it. Users would click through to 404s. You cannot validate provenance with a format check.

The fix: **an allowlist of URLs the system actually observed.** Every search result and every successfully fetched page registers its URL in a `Set`:

```ts
export interface ResearchContext {
  seenUrls: Set<string>;   // populated by search_web and fetch_page
  ...
}

// in save_pain_point:
const urlVerified = !!postUrl && ctx.seenUrls.has(postUrl);
// unverified → saved with postUrl: undefined, and the agent is told:
return `Saved, but the URL was dropped — it never appeared in your search results. Do not invent URLs.`;
```

Two properties make this robust: the check is *exact membership*, not pattern matching; and the agent gets **feedback** when it misbehaves, which corrects it mid-run.

### Reading pages properly

Search snippets are ~150 chars. The `fetch_page` tool gets the real content, with a platform-specific trick worth knowing: **append `.json` to any Reddit thread URL** and you get the post *and comments* as clean JSON — no HTML scraping:

```ts
const jsonUrl = `https://www.reddit.com${url.pathname.replace(/\/$/, '')}.json?limit=15`;
// data[0] = the post, data[1] = the comment tree
```

Comments are often better pain points than the post itself ("came here to say I have this exact problem").

For everything else: strip `<script>`/`<style>`, strip tags, decode entities, collapse whitespace. Crude but sufficient for an LLM reader.

### SSRF: the security cost of `fetch_page`

The moment your server fetches URLs an *LLM chose*, you've built a potential Server-Side Request Forgery gadget: a manipulated agent could request `http://localhost:3001/api/...` or a cloud metadata endpoint *from inside your network*. Guard before every fetch:

```ts
const host = url.hostname.toLowerCase();
const isPrivate =
  host === 'localhost' || host.endsWith('.local') || host.endsWith('.internal') ||
  /^127\.|^10\.|^192\.168\.|^169\.254\.|^0\./.test(host) ||
  /^172\.(1[6-9]|2\d|3[01])\./.test(host) ||
  host === '::1' || host.startsWith('fd') || host.startsWith('fe80');
if (isPrivate) throw new Error('URL points to a private address');
```

Plus `timeout` and `maxContentLength` on the request itself — a hanging or 2 GB response shouldn't stall a worker.

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

## 27. Tokens at Rest and OAuth Refresh Across Platforms

### Encrypt at the model boundary

User API keys were AES-256-GCM encrypted, but the OAuth `accessToken`/`refreshToken` in `accounts` — arguably *more* sensitive, they can post as the user — were plaintext. The fix lives entirely in `AccountModel`, so no caller changes:

```ts
// iv:authTag:ciphertext hex triplet produced by config/encryption.ts
const ENCRYPTED_SHAPE = /^[0-9a-f]{32}:[0-9a-f]{32}:[0-9a-f]+$/i;

function open(value: string | null) {
  if (!value || !ENCRYPTED_SHAPE.test(value)) return value;  // legacy plaintext row
  try { return decrypt(value); } catch { return value; }
}
```

Two patterns here: **encrypt/decrypt at a single choke point** (every read/write already went through `AccountModel`, so the change is invisible everywhere else), and **tolerate legacy data** — rows written before encryption still decrypt as themselves and get sealed on their next write. No migration script, no downtime.

### Refresh is different on every platform

| Platform | Mechanism | Catch |
|---|---|---|
| Twitter | standard `refresh_token` grant | rotates the refresh token — store the new one |
| LinkedIn | `refresh_token` grant | only if your app has refresh enabled |
| Facebook | **no refresh token at all** — exchange the current token for a new long-lived one | exchange only works while the token is **still valid** |

Facebook's catch drives the design: you must refresh *proactively, before* expiry. Hence per-platform refresh windows:

```ts
const REFRESH_WINDOW_MS: Record<string, number> = {
  facebook: 7 * 24 * 60 * 60 * 1000,   // a week early — can't refresh after expiry
  twitter: 60_000,
  linkedin: 60_000,
};
```

And when refresh fails and the token is truly dead, **fail loudly**: create a notification telling the user to reconnect. The silent version of this bug is brutal — every scheduled post just quietly fails about 60 days after the user connected LinkedIn, and nobody knows why.

### Closing the analytics loop

The worker used to throw away the API responses after publishing. But those responses contain the platform's post ID — the key you need to *ever* fetch real engagement. Now each publisher returns it (`res.data.data.id` for Twitter, the `x-restli-id` header for LinkedIn, `json.data.name` for Reddit with `api_type: 'json'`), it's stored on `PostAnalytic.externalId`, and an hourly repeatable job pulls real like/share/comment counts:

```ts
engagementQueue.add('refresh', {}, { repeat: { every: 60 * 60 * 1000 } });
// BullMQ dedupes repeatable jobs by their repeat key — safe to run on every boot
```

Lesson: when you call an external API that *creates* something, always persist the returned ID, even if you don't need it yet. It's unrecoverable later.

---

## 28. Verifying Migrations Without Your Dev Database

Situation: schema changed, but no Postgres was running and Docker's daemon was down. Two useful facts:

1. **`prisma generate` needs no database** — it only reads `schema.prisma`. Types compile immediately.
2. **Migration files are just SQL in a timestamped folder.** You can write one by hand and Prisma treats it like its own:

```
prisma/migrations/20260714084700_post_variants_subreddit_analytics_external_id/migration.sql
```
```sql
ALTER TABLE "posts" ADD COLUMN "content_by_platform" JSONB,
ADD COLUMN "subreddit" TEXT;
ALTER TABLE "post_analytics" ADD COLUMN "external_id" TEXT;
```

But hand-written SQL can drift from the schema, so verify before trusting it. A throwaway container is perfect (podman worked when Docker's daemon didn't — same images, daemonless):

```bash
podman run -d --name pg-test -e POSTGRES_USER=... -p 5433:5432 postgres:16-alpine
DATABASE_URL="postgresql://...@localhost:5433/..." npx prisma migrate deploy
DATABASE_URL="..." npx prisma migrate diff \
  --from-schema-datasource prisma/schema.prisma \
  --to-schema-datamodel  prisma/schema.prisma
# → "No difference detected."  ← the migrations exactly produce the schema
podman rm -f pg-test
```

Note the port: **5433**, because another project's Postgres already owned 5432. Verify who's actually listening before you point tools at a port — the migration would otherwise have knocked on a *different project's database* (it failed safely on credentials, but that was luck, not design).

Bonus version lesson: `createManyAndReturn` looked perfect for batch inserts but was Preview-gated in this Prisma version. `prisma.$transaction(items.map(i => prisma.painPoint.create({ data: i })))` batches N inserts into one round-trip transaction and works on every version — boring beats clever when the clever thing is version-gated.

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
