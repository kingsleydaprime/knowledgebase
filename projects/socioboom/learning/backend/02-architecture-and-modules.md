# SocioBoom Backend — The Module Pattern, Middleware Chain & Module Tour

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/01-foundations.md` (Express and TypeScript basics this assumes),
`learning/backend/07-feature-case-studies.md` (two modules followed end to end), and
`learning/backend/09-decisions-and-mastery.md` (why the architecture was shaped this way).

This file covers: the controller / service / model / routes / type five-file module pattern used by
every module in `src/api/v1/modules/`, why the layers are separated and what belongs in each, the
Express app and its middleware chain (order matters and why), and a complete tour of all modules in
the codebase — accounts, analytics, api-keys, auth, billing, content-strategy, discovery,
notifications, posts, reviews, teams, and users.

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


