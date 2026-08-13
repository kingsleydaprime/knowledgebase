# SocioBoom Backend — PostgreSQL, Prisma 5 & Migrations

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/02-architecture-and-modules.md` (the model layer that wraps Prisma),
`learning/backend/04-auth-and-security.md` (encrypting tokens before they reach these tables), and
`learning/backend/08-devops-and-deployment.md` (running Postgres in Docker and on Aiven).

This file covers: the Prisma 5 schema and every model in it, the `@map`/`@@map` snake_case
convention, relations and cascade deletes, generating and applying migrations, the migration
workflow in practice, and how to verify a migration is correct without access to your dev
database.

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


