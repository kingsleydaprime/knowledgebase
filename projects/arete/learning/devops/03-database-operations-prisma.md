# Arete DevOps — Database Operations (Prisma)

Split out from the original single-file `devops-learning.md`. See also
`02-containers-docker-podman.md`.

---

## Part 3 — Database Operations (Prisma)

### The three migrate commands and where each belongs

```bash
bunx prisma migrate dev --name add_task_variants
# DEV ONLY. Diffs schema.prisma against the DB, writes a new SQL file into
# prisma/migrations/<timestamp>_add_task_variants/, applies it, regenerates the client.

bunx prisma migrate deploy
# PROD (and CI). Applies pending migration files IN ORDER. Generates nothing,
# asks nothing, destroys nothing. This is the only migrate command prod should ever see.

bunx prisma generate
# Regenerates the typed client from schema.prisma. Run after every schema change/pull.
```

### Trick used on this project: generating migration SQL with no database

`migrate dev` needs a live shadow database. To create the task-variants migration offline:

```bash
cp prisma/schema.prisma /tmp/schema-old.prisma      # snapshot BEFORE editing
# ...edit schema.prisma (add TaskVariant, variantId)...
bunx prisma migrate diff \
  --from-schema-datamodel /tmp/schema-old.prisma \
  --to-schema-datamodel   prisma/schema.prisma \
  --script                                          # emit SQL to stdout
# paste into prisma/migrations/20260714090000_add_task_variants/migration.sql
```

`migrate diff` compares two schema states (files, live DBs, or migration histories) and prints the SQL to get from A to B. `migrate deploy` then treats your hand-placed folder like any generated one. Folder name format matters: `<YYYYMMDDHHMMSS>_<name>`.

### Seeding

```bash
bunx prisma db seed        # runs the command in package.json → "prisma": { "seed": "ts-node prisma/seed.ts" }
```

Arete's seed is **idempotent** (safe to run on every deploy): upserts keyed on slugs for tasks/variants/pillars, wipe-and-recreate for messages only when the library grew. Prod release order is always:

```bash
bunx prisma migrate deploy   # 1. schema first
bunx prisma db seed          # 2. then content
# 3. then (or simultaneously) the new app code
```

**This order is now automated in the Dockerfile** so no human can forget it:

```dockerfile
COPY --from=builder /app/tsconfig.json ./    # ts-node (which runs seed.ts) needs it at runtime
CMD ["sh", "-c", "npx prisma migrate deploy && npx prisma db seed && node dist/src/main"]
```

Because the seed is idempotent, boot-time seeding doubles as **content deployment**: edit `task-variants.ts` or `daily-messages.ts`, deploy, and the new content is live — no manual step, no CMS.

### Incident write-up: the seed race (why that order is law)

Real incident from launch week: a fresh dev database was brought up, and a user **registered 77 seconds before the seed ran**. Onboarding queried the pillars table, got an empty array, "successfully" created zero user-pillars, and marked onboarding complete. Result: an account permanently stuck with no quests — schema was fine, *content* was missing.

Ops lessons:
1. **Migrate → seed → open the doors.** A database that has tables but no reference data is not ready for traffic.
2. Baking the sequence into the container's boot command turns a runbook rule into a guarantee.
3. The app-level companions (fail loudly if reference data is missing; self-heal broken accounts) live in the backend notes — defense in depth means the ops fix AND the code fix.

### Debugging a DB you can't psql into

When `podman exec ... psql` isn't available (container owned by another user, or no psql on host), go through the app's own ORM — a throwaway script uses the same `DATABASE_URL` the backend uses:

```bash
cat > debug.tmp.ts << 'EOF'
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
prisma.user.findMany({ take: 5, orderBy: { createdAt: 'desc' } })
  .then(console.log).finally(() => prisma.$disconnect());
EOF
bun debug.tmp.ts; rm debug.tmp.ts
```

This is how the seed-race incident was diagnosed in three queries: users existed ✓, tasks existed ✓, user-pillars empty ✗ — root cause isolated without ever opening a SQL shell.

---

