# Schema Migrations — Reference Guide

> How migration systems actually work, what schema drift is and how it happens,
> and the recovery procedure when a migration fails against a database you
> cannot reset. Framework-agnostic, with Postgres and Prisma specifics where the
> details matter. Written 2026-09-21 after a production P3009 on nextvibe — see
> [[projects/nextvibe/learning/09-devops|nextvibe devops Part 60]] for that
> incident in full.

---

## 1. A migration system is a ledger plus a pile of files

Every migration tool — Prisma, Rails, Alembic, Flyway, Liquibase, EF Core — is
the same two things:

1. **An ordered directory of SQL files**, named so they sort chronologically
2. **A table inside the database** recording which of them have run

Prisma calls it `_prisma_migrations`, Rails `schema_migrations`, Flyway
`flyway_schema_history`. The names differ; the idea does not.

**This is the whole mental model, and it explains every failure mode.** The tool
does not inspect your schema to decide what to do. It compares the file list to
the ledger and runs the difference. So there are three things that can disagree:

```
   migration files   ←→   the ledger   ←→   the actual schema
```

Any two of them getting out of step is a distinct class of bug:

| Disagreement | Symptom |
|---|---|
| files vs ledger | pending migrations, or "migration not found in history" |
| ledger vs schema | **drift** — the tool's beliefs are fiction |
| files vs schema | the next generated migration is nonsense |

The ledger being a plain table is the most useful fact in this entire document.
When a tool's CLI will not tell you what is wrong, query it directly.

## 2. Schema drift

**Drift is any schema change the ledger does not know about.** The database and
the migration history have diverged, and the tool cannot tell.

How it happens, roughly in order of frequency:

- **`prisma db push` / `db:sync` against a real database.** These mutate schema
  to match a model file and write *nothing* to the ledger. They exist for
  prototyping against a scratch database. Used anywhere with history, they are
  the single biggest source of drift.
- **Manual DDL.** Someone runs `ALTER TABLE` in a console to fix something
  urgent. It works. Nobody writes the migration.
- **Marking migrations applied without running them** (`migrate resolve
  --applied`). Sometimes legitimate — usually a way of postponing a problem.
- **Restoring a backup** from a different schema version.
- **Two branches** generating migrations from the same parent state.

### Why drift is invisible until it is expensive

Nothing breaks when drift appears. The app works — the tables it needs exist.
The failure comes later, when the *next* migration is generated or applied:

- A generated migration diffs your model against **drifted** state, so it
  contains changes you never asked for
- An existing migration fails with "already exists", because the object was
  created by hand

A migration file that bundles unrelated changes — one named "add logs table"
that also alters three other tables — is the diagnostic signature of drift. It
was generated as a diff against a schema nobody had described.

## 3. When a migration fails

### It usually does not half-apply

In Postgres, **DDL is transactional**. `CREATE TABLE`, `ALTER TABLE`,
`CREATE TYPE`, `CREATE INDEX` all participate in transactions, and migration
tools wrap each file in one. So a SQL error normally rolls the whole file back
atomically, leaving nothing behind.

This is a Postgres luxury worth appreciating. **MySQL cannot do this** —
pre-8.0 DDL is not transactional at all, and even with atomic DDL each statement
commits separately. A failed MySQL migration genuinely leaves you halfway, which
is why MySQL shops write smaller migrations.

Exceptions in Postgres: `CREATE INDEX CONCURRENTLY` and `ALTER TYPE … ADD VALUE`
(pre-12) cannot run inside a transaction. Migrations containing them can partly
apply.

### The deciding fact: how many steps applied

```sql
SELECT migration_name, started_at, finished_at, rolled_back_at,
       applied_steps_count, logs
FROM _prisma_migrations
WHERE finished_at IS NULL OR rolled_back_at IS NOT NULL
ORDER BY started_at DESC;
```

`applied_steps_count` decides everything. The error message does not.

### The two recovery verbs

Neither touches your schema. **Both only edit the ledger.** Internalise that and
the choice becomes obvious:

| Verb | Ledger effect | Next `deploy` |
|---|---|---|
| `resolve --rolled-back` | deletes the failure row | **retries** the file |
| `resolve --applied` | writes a success row | **skips** the file forever |

- `applied_steps_count = 0` → nothing landed → **`--rolled-back`**, then fix the
  file so the retry succeeds
- All steps applied (failure was afterwards, e.g. a dropped connection) →
  **`--applied`**
- Partial → make the file idempotent, then **`--rolled-back`**

Choosing `--applied` when nothing ran is the expensive error. The ledger then
claims objects exist that do not, every later migration is built on that
premise, and you discover it when production queries a missing table.

### Never reset

`prisma migrate reset`, `rails db:reset`, `alembic downgrade base` — these drop
data. They are in every tutorial because tutorials run locally. There is no
version of "I'll just reset it" that is correct for a database with users in it.

## 4. Idempotent migrations

If `--rolled-back` means the file re-runs, the file has to tolerate a partially
present schema.

### Postgres native guards

```sql
CREATE TABLE IF NOT EXISTS …
CREATE INDEX IF NOT EXISTS …
ALTER TABLE t ADD COLUMN IF NOT EXISTS …
ALTER TABLE t DROP COLUMN IF EXISTS …
ALTER TABLE t DROP CONSTRAINT IF EXISTS …
DROP TABLE IF EXISTS …
```

### The two that have no guard

`CREATE TYPE` and `ADD CONSTRAINT` accept no `IF NOT EXISTS`. Use a catalog
check:

```sql
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'my_enum') THEN
    CREATE TYPE "my_enum" AS ENUM ('A','B');
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_name') THEN
    ALTER TABLE t ADD CONSTRAINT fk_name FOREIGN KEY …;
  END IF;
END $$;
```

The catalogs worth knowing: `pg_type` (types and enums), `pg_constraint`
(constraints), `pg_class` (tables and indexes), `pg_enum` (enum values), and
`information_schema.columns` / `.tables` for the portable spellings.

Prefer `information_schema` when you want a missing table to fall through
quietly — querying the table itself errors, querying the catalog just returns
no rows.

Some statements are **already idempotent** and need no wrapper:
`ALTER COLUMN … DROP NOT NULL`, `ALTER COLUMN … SET DEFAULT`. Knowing which
saves you from reflexively wrapping everything.

### ⚠️ The trap inside the fix

**`IF NOT EXISTS` matches on name, not shape.**
`CREATE TABLE IF NOT EXISTS users` skips a table called `users` whatever columns
it has. If the drifted object differs from what the migration describes, the
skip is silent and the divergence becomes permanent — you have swapped a loud
failure for a quiet lie.

So before deploying an idempotent rewrite, verify **shape**:

```sql
-- enum values, in order (order matters for enums)
SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder)
FROM pg_type t JOIN pg_enum e ON e.enumtypid = t.oid
WHERE t.typname = 'my_enum' GROUP BY t.typname;

-- cheap first pass on tables
SELECT table_name, count(*) FROM information_schema.columns
WHERE table_schema = 'public' GROUP BY table_name;

-- and the real comparison when the count matches but you want certainty
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema='public' AND table_name='users' ORDER BY ordinal_position;
```

## 5. Renames are the most dangerous change you can make

No schema differ can detect a rename. It sees a field that disappeared and a
field that appeared, and emits:

```sql
ALTER TABLE t DROP COLUMN "old_name", ADD COLUMN "new_name" TEXT;
```

Which is correct on its own terms and **destroys every value in the column**.
Prisma at least prints a warning block into the file; not all tools do.

**Always read a generated migration before applying it, and grep it for
`DROP`.** A rename in a model file is the single most common route to silent
data loss in an ORM-driven codebase.

The hand-written version:

```sql
ALTER TABLE t RENAME COLUMN "old_name" TO "new_name";
```

### Expand/contract, for renames that cannot take downtime

A rename is instant in Postgres but breaks any running code expecting the old
name. With more than one app instance, you cannot deploy schema and code
simultaneously. So split it across releases:

1. **Expand** — add the new column; write to both; read from old
2. **Backfill** — copy existing values
3. **Switch** — read from new; keep writing both
4. **Contract** — stop writing old; drop it in a later release

Four deploys instead of one. The point is that every intermediate state works
with both the old and new code, so nothing breaks mid-rollout. The same shape
applies to splitting a column, changing a type, or moving data between tables.

## 6. Prevention

### A shadow database

The highest-value safeguard, and the most commonly skipped. A shadow database is
a throwaway database the tool builds **from migration history alone**, then
diffs your model against. Prisma's `SHADOW_DATABASE_URL`; Rails does it via
`schema.rb` comparison.

Its real job is detecting drift: if history-built schema ≠ actual schema, the
tool can tell you *before* generating a migration against fiction.

Without one, every generated migration is a diff against whatever the real
database has become.

### Rules that prevent most of this

- **Never `db push` at a database with migration history.** Prototyping only.
- **Never apply DDL by hand** to an environment that has a ledger. If you must
  in an emergency, write the matching migration and `resolve --applied` it the
  same day, with a note.
- **One logical change per migration.** A file touching five unrelated tables is
  evidence you generated it from drift rather than from an intention.
- **Read every generated migration.** Grep for `DROP`.
- **Deploy scripts should be `migrate deploy` and nothing else.** A deploy
  script carrying a growing list of hardcoded `resolve --applied` calls — with
  `|| true` to swallow failures — is a standing instruction to lie to the
  ledger. Each use widens the gap it exists to hide.

### The forward-only question

Most teams write `down` migrations and never run them. In production you fix
forward: a bad migration gets a new migration reverting it, so the ledger stays
append-only and the history stays honest. Down migrations are genuinely useful
locally, for iterating. Do not mistake having them for having a rollback plan —
a rollback plan is a backup and a tested restore.

## 7. Operational notes

### Connection strings are not portable between tools

Loading `.env` is a convention each framework implements, **not a shell
feature**. Your ORM reads it; `psql`, `curl` and `mysql` do not. A CLI failing
with "cannot connect to local socket" usually means "you gave me no URL", not
"the server is down".

```bash
set -a; . ./.env; set +a
# or extract one variable, tolerating either quote style:
U="$(grep '^DATABASE_URL=' .env | cut -d'=' -f2- | tr -d "\"'")"
```

`cut -d'=' -f2-` keeps everything after the *first* `=`, so query parameters
like `?sslmode=require` survive.

**ORMs invent their own connection-string vocabulary.** Prisma accepts
`sslmode=no-verify`, which libpq rejects outright — libpq allows only
`disable | allow | prefer | require | verify-ca | verify-full`. The equivalent
of `no-verify` is `require`: both encrypt, neither validates the certificate
chain. Note that this means an active MITM is possible; `verify-full` plus the
provider's CA certificate is the strict option.

### Reading long text out of psql

```bash
psql "$URL" -At -c "SELECT logs FROM _prisma_migrations WHERE …"
```

`-A` disables column alignment, `-t` drops headers. Without these, a multi-line
error is padded into an unreadable table.

### Migrating on container start does not scale

An entrypoint that runs `migrate deploy` before `exec`ing the app is fine at one
replica. At two or more, they race for the migration lock — most tools handle it
via advisory locks, but you get slow starts and confusing logs. Past a single
instance, migrations belong in a separate deploy step or a job that runs once.

---

## Related

- [[databases/12-operating-a-database|12 — Operating a Database]]
- [[databases/08-transactions-and-acid|08 — Transactions & ACID]] — why Postgres DDL rolls back
- [[databases/database-design-reference|Database Design Reference]]
- [[projects/nextvibe/learning/09-devops|nextvibe — DevOps]] Part 56 and Part 60
