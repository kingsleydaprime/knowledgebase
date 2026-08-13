# SocioBoom Backend — Foundations: Node, Express, TypeScript, Bootstrap

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/02-architecture-and-modules.md` (the module pattern these foundations build into),
`learning/backend/03-database-prisma.md` (the data layer), and
`learning/backend/09-decisions-and-mastery.md` (the from-scratch rebuild that re-walks this ground
with the whole system in view).

This file covers: the big-picture view of what the SocioBoom backend actually does, Node.js and the
event loop, what Express is and why it was chosen, TypeScript fundamentals as they apply to a
server, the initial project bootstrap, and the `tsconfig.json` settings that matter (strict mode,
path aliases, and the `tsc-alias` build step that makes them work at runtime).

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


