# DevOps & Shell Mastery — Beginner to Advanced
### Containers (Docker & Podman), database operations, and a deep dive into find / grep / sed / regex — with the exact commands used on Arete

---

## Part 1 — Absolute Beginner

### What "DevOps" means for a solo founder

You are the ops team. Concretely that means owning:
1. **Environments** — your laptop (dev), and Render (prod). Same code, different config.
2. **Configuration** — secrets and URLs live in environment variables, never in code.
3. **Infrastructure** — Postgres and Redis running somewhere (containers locally, managed services in prod).
4. **Releases** — migrations, seeds, builds, in the right order, repeatably.

### Environment variables and .env files

```bash
# backend/.env  (dev — never commit real secrets)
DATABASE_URL=postgresql://arete:arete_dev_secret@localhost:5432/arete_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev_jwt_secret_change_in_production
```

The URL format to memorize: `protocol://user:password@host:port/database`.

Rules:
- `.env` is per-machine; `.env.prod.example` documents what prod needs without containing values.
- The same code reads `process.env.DATABASE_URL` everywhere — *config varies, code doesn't*. This is the single most important deployment principle (see "12-factor app").

---

## Part 2 — Containers

### The concepts, precisely

| Term | What it is | Analogy |
|---|---|---|
| **Image** | A frozen filesystem + start command (`postgres:16-alpine`) | A class |
| **Container** | A running (or stopped) instance of an image | An object |
| **Volume** | Named storage that outlives containers | The hard drive |
| **Network** | Private DNS + routing between containers | The office LAN |
| **Port mapping** | `host:container` — `5432:5432` exposes the container to your laptop | A doorway |
| **Registry** | Where images come from (Docker Hub by default) | npm for machines |

The core promise: a container bundles the app *and* its OS-level dependencies, so "works on my machine" becomes "works on any machine with a container runtime."

### Arete's docker-compose.dev.yml, annotated

```yaml
services:
  postgres:
    image: postgres:16-alpine          # official image, alpine = tiny base OS
    container_name: arete_postgres_dev
    restart: unless-stopped            # auto-restart on crash/reboot, unless you stopped it
    environment:                       # the image reads these on first boot
      POSTGRES_USER: arete
      POSTGRES_PASSWORD: arete_dev_secret
      POSTGRES_DB: arete_dev
    ports:
      - "5432:5432"                    # host:container — lets localhost:5432 reach it
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data   # data survives `down`
    healthcheck:                       # how the runtime knows it's *ready*, not just running
      test: ["CMD-SHELL", "pg_isready -U arete -d arete_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_dev_data:/data]

volumes:                               # named volumes are declared at top level
  postgres_dev_data:
  redis_dev_data:
```

Key insights:
- **Volumes are why `down` is safe.** We took the stack down after seeding; the 281 variants + 210 messages persisted in `postgres_dev_data`. Only `down -v` (or `volume rm`) destroys data.
- **Healthcheck vs running:** `podman ps` showed `Up 8 seconds (starting)` → the process was up but `pg_isready` hadn't passed yet. Migrations run against a "starting" DB fail confusingly; wait for `(healthy)`.
- `version: "3.9"` at the top is obsolete — compose warns and ignores it now.

### Docker vs Podman — what actually differs

| | Docker | Podman |
|---|---|---|
| Architecture | Client → **root daemon** (`dockerd`) | **Daemonless** — each container is a child process |
| Default privileges | Daemon runs as root | **Rootless** — runs as your user |
| Ships with Fedora/RHEL | No | **Yes** (Red Hat project) |
| CLI | `docker ...` | Same verbs: `podman ps`, `podman run`... |
| Compose | `docker compose` built in | Delegates to a compose provider |
| Images | OCI standard — **identical images work in both** |

Because both implement the **OCI spec**, `postgres:16-alpine` is byte-for-byte the same under either. Kubernetes uses neither directly (containerd/CRI-O) — the image is the portable artifact, the runtime is an implementation detail.

**The three Podman gotchas we actually hit on this project:**

```bash
# 1. `docker ps` failed:
#    "failed to connect to the docker API at unix:///var/run/docker.sock"
#    → there IS no docker daemon on Fedora. Use podman.

# 2. `podman compose up -d` failed:
#    "dial unix /run/user/1000/podman/podman.sock: connect: no such file"
#    → compose talks to podman through a user socket that wasn't started:
systemctl --user start podman.socket        # start it now
systemctl --user enable --now podman.socket # start it on every login (permanent fix)

# 3. `podman ps` showed NOTHING — but postgres was clearly serving on :5432.
#    Rootless containers are per-user: containers started as root (sudo) or by
#    another user are invisible to your `podman ps`. Diagnose from the network side:
ss -tlnp | grep -E '5432|6379'   # ss shows listeners regardless of who owns them
sudo podman ps                    # root's containers live in a separate world
```

`systemctl --user` manages services for *your user session* (rootless), as opposed to system-wide `systemctl` — consistent with Podman's whole rootless philosophy.

### The container commands used on Arete (your cheat sheet)

```bash
# bring the dev stack up (detached)
podman compose -f docker-compose.dev.yml up -d
#              ^^ which file            ^^ -d = detached (don't tie up the terminal)

# see what's running (+ health state)
podman ps
podman ps -a                          # -a includes stopped containers
podman ps --format '{{.Names}} {{.Status}}'   # Go-template output: just the columns you want

# logs, shells, inspection
podman logs -f arete_postgres_dev     # -f = follow (live tail)
podman exec -it arete_postgres_dev psql -U arete -d arete_dev   # shell INTO the container
podman inspect arete_postgres_dev     # full JSON: mounts, env, network, health

# tear down (containers + network removed; named VOLUMES KEPT)
podman compose -f docker-compose.dev.yml down
podman compose -f docker-compose.dev.yml down -v   # ⚠ also deletes volumes = data loss

# housekeeping
podman volume ls
podman images
podman system prune                   # remove stopped containers + dangling images
```

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

## Part 4 — Shell Mastery: pipes, and the text toolkit

### The pipeline model — why the shell is powerful

Every command reads **stdin**, writes **stdout**, and errors to **stderr**. `|` connects stdout → stdin. Small tools compose into queries:

```bash
grep -rn "cache.del" src | wc -l        # how many cache-invalidation call sites?
#  produce lines            count them
```

Redirection:
```bash
cmd >  file      # stdout to file (overwrite)
cmd >> file      # append
cmd 2>&1         # merge stderr INTO stdout (so pipes/`tail` see errors too)
cmd 2>/dev/null  # discard errors
cmd1 && cmd2     # run cmd2 only if cmd1 succeeded (exit code 0)
cmd1 || cmd2     # run cmd2 only if cmd1 FAILED
cmd1 ;  cmd2     # run both regardless
```

You saw `2>&1 | tail -5` constantly in my commands — without `2>&1`, error output bypasses the pipe and you'd tail nothing useful when a command fails.

### cat, head, tail, wc, sort, uniq

```bash
cat file.ts                 # print whole file (concatenate)
head -30 file.ts            # first 30 lines
tail -12 file.ts            # last 12 lines
tail -f server.log          # follow live — THE log-watching command
wc -l file.ts               # line count
wc -l *.tsx                 # per-file + total (how I checked quests.tsx was 1173 lines)
sort | uniq -c | sort -rn   # the classic "frequency count" pipeline
```

Heredoc — feeding a multi-line file from the shell (used to write the verify script):

```bash
cat > verify.ts << 'EOF'
import { PrismaClient } from '@prisma/client';
...
EOF
# quoting 'EOF' prevents the shell from expanding $vars inside the block — almost always what you want for code
```

---

## Part 5 — grep, In Depth

`grep PATTERN [files]` prints lines matching a pattern. It's the tool I used most on your codebase.

### The flags that matter (ranked by how often you'll use them)

```bash
grep -r  "pattern" src/     # recursive through a directory
grep -n  "pattern" file     # show line numbers        → clickable file:line
grep -i  "pattern" file     # case-insensitive
grep -l  "pattern" src/     # only FILENAMES that match (not the lines)
grep -v  "pattern"          # INVERT — lines that DON'T match (a filter)
grep -c  "pattern" file     # count matching lines
grep -E  "a|b"              # extended regex (see Part 7)
grep -F  "literal.string"   # fixed string, NO regex — fast, safe for special chars
grep -w  "id"               # whole word only (won't match "pillarId")
grep -A5 "pattern"          # show 5 lines After each match
grep -B2 "pattern"          # 2 lines Before
grep -C3 "pattern"          # 3 lines of Context both sides
grep --include="*.ts" -r    # recursive, but only into matching filenames
```

### Real commands from this project, dissected

```bash
# "Is faithBackground actually USED anywhere in the backend?"
grep -rn "faithBackground\|equipmentAccess" backend/src --include="*.ts" \
  | grep -v node_modules | grep -v ".spec" | head -20
```
- `-rn` → recursive + line numbers.
- `"faithBackground\|equipmentAccess"` → OR. In basic grep, alternation is `\|` (escaped). With `-E` it's a clean `|`.
- `--include="*.ts"` → skip .js builds, .json, etc.
- `| grep -v node_modules | grep -v ".spec"` → chained *negative* filters: drop dependency and test noise. Piping grep into grep -v is the everyday way to subtract.
- `| head -20` → cap the output.
- **The result (only 4 hits, all in onboarding) was the finding**: the fields were collected but never used in quest generation. Absence of matches is evidence too.

```bash
# "Which onboarding screens mention faith?" — filenames only:
grep -rn "faithBackground\|equipmentAccess\|faith" mobile/app --include="*.tsx" -l

# "Show me the seed script config inside package.json, with context":
grep -A5 '"scripts"\|"prisma"' package.json | head -20
#     ^ -A5 prints the 5 lines AFTER each match — perfect for JSON blocks

# "Find the message-array boundaries in seed.ts before surgical deletion":
grep -n "LEGACY_MESSAGES_REMOVED\|Seed complete\|existingMessages\|^main()\|^}" prisma/seed.ts
#        ^ anchors: ^main() = lines STARTING with main(), ^} = closing braces at column 0
#        This gave exact line numbers (335, 388) to feed into sed.

# case-insensitive filename hunting:
ls -la backend | grep -i env         # found .env and .env.prod.example
```

### grep pro-habits

- Start broad (`grep -rl`), then narrow (`grep -n` in the specific file). Cheap reconnaissance before reading files.
- `grep -F` when searching for strings full of dots/brackets (`grep -F "toISOString()"`) — no escaping needed.
- Know that modern alternatives exist: `rg` (ripgrep) is grep -r but faster and skips `.gitignore`d files by default. Same flags mostly.

---

## Part 6 — find, In Depth

`grep` searches *inside* files; `find` searches for *files themselves* — by name, type, size, age — and can run commands on what it finds.

```bash
find <where> <tests> <actions>
```

### Tests (filters)

```bash
find . -name "*.prisma"          # glob match on filename (quote it! see Part 7 on globs)
find . -iname "readme*"          # case-insensitive name
find . -type f                   # files only
find . -type d                   # directories only
find . -path "*node_modules*"    # match against the whole path
find . -size +1M                 # bigger than 1 MB
find . -mtime -1                 # modified in the last 24h
find . -newer schema.prisma      # modified more recently than that file
```

### Combining tests — AND, OR, NOT (and the parentheses trap)

```bash
# AND is implicit:
find backend -type f -name "*.ts"

# OR is -o — this is from the project:
find backend -name "*.prisma" -o -name "schema*" | grep -v node_modules
#            └── matches either pattern ──┘

# ⚠ THE trap: -o binds looser than implicit AND. This:
find . -name "*.ts" -o -name "*.tsx" -type f
# parses as:  (-name "*.ts")  OR  (-name "*.tsx" AND -type f)   ← not what you meant!
# Fix with escaped parens:
find . \( -name "*.ts" -o -name "*.tsx" \) -type f

# NOT:
find src -type f ! -name "*.spec.ts"

# pruning big directories properly (faster than filtering after):
find . -path ./node_modules -prune -o -type f -name "*.ts" -print
#      └── when path matches, don't descend ──┘            └── needed with -prune
```

### Actions

```bash
find . -name "*.tmp.ts" -delete                      # careful: test with -print first!
find src -name "*.ts" -exec wc -l {} +               # {} = the file(s); + batches them into one wc call
find src -name "*.ts" -exec grep -l "TODO" {} \;     # \; = one command per file (slower)
find . -name "*.log" -print0 | xargs -0 rm           # -print0/-0 = NUL separators, safe for spaces in names
```

**Golden habit:** always run the `find` with plain `-print` (default) first, eyeball the list, *then* add `-delete`/`-exec rm`. Find-with-delete typos are how people erase home directories.

---

## Part 7 — Regex from Zero to Advanced

### First: globs are NOT regex

```
glob  (shell, find -name):   *.ts        → * = anything, ? = one char
regex (grep, sed):           .*\.ts$     → . = any ONE char, * = repeat previous, \. = literal dot
```

The shell expands unquoted globs **before** the command runs — that's why it's `find . -name "*.ts"` (quoted, so *find* sees the pattern) and why `ls backend/.env*` errored with "no matches found": zsh tried to expand the glob itself, found nothing, and aborted the whole command. Quoting controls *who* interprets the pattern.

### The regex building blocks

```
LITERALS & ESCAPES
  cat        matches "cat" anywhere in the line
  \.  \$ \*  literal . $ *  (backslash disarms special meaning)

ANY & CLASSES
  .          any single character
  [abc]      one of a, b, c
  [a-z0-9]   ranges
  [^abc]     any char EXCEPT a, b, c     ← ^ inside [] = negation
  \d \w \s   digit / word-char / whitespace (PCRE; in grep use [0-9], [[:alnum:]_], [[:space:]])

ANCHORS
  ^          start of line          ^import   → lines starting with import
  $          end of line            ;$        → lines ending with semicolon
  \b         word boundary          \bid\b    → "id" but not "pillarId"

QUANTIFIERS (apply to the preceding item)
  *          0 or more              ab*c   → ac, abc, abbc
  +          1 or more              ab+c   → abc, abbc (not ac)
  ?          0 or 1                 colou?r → color, colour
  {3}        exactly 3              [0-9]{3}
  {2,5}      between 2 and 5
  {2,}       2 or more

GROUPS & ALTERNATION
  (foo|bar)  either word
  (ab)+      repeat a group
  \1         backreference — whatever group 1 matched
```

### The three regex dialects (why your pattern "doesn't work")

| Dialect | Where | `+ ? {} () |` are special? |
|---|---|---|
| **BRE** (basic) | plain `grep`, plain `sed` | No — must escape: `\+ \? \{ \} \( \) \|` |
| **ERE** (extended) | `grep -E`, `sed -E`, `awk` | **Yes** — clean syntax |
| **PCRE** (Perl) | `grep -P`, JS, Python | Yes, plus `\d \w` lookaheads, lazy `*?` |

This is why the project command used `"faithBackground\|equipmentAccess"` with plain grep — BRE needs the escaped `\|`. The modern habit: **just always use `grep -E` / `sed -E`** and write clean patterns.

### Worked examples, increasing difficulty

```bash
# 1. All TODO or FIXME comments:
grep -rEn "TODO|FIXME" src/

# 2. Find hardcoded hex colors in the mobile app:
grep -rEn "#[0-9A-Fa-f]{6}\b" mobile/app --include="*.tsx"

# 3. Console.logs that aren't in comments (start-of-line whitespace only before them):
grep -rEn "^\s*console\.log" src/

# 4. Every NestJS route decorator with its path:
grep -rEn "@(Get|Post|Patch|Delete)\(" backend/src --include="*.controller.ts"

# 5. UUIDs anywhere:
grep -rEn "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" logs/

# 6. Env var assignments but NOT comments (negated class + anchor):
grep -En "^[^#]*DATABASE_URL" .env*
```

### The password-masking sed from this project — full dissection

When I printed your `.env`, the DB password had to be hidden:

```bash
sed 's/:[^:@\/]*@/:***@/' .env
```

```
s/PATTERN/REPLACEMENT/      sed's substitute command
:                           match a literal colon        postgresql://arete : PASSWORD @ localhost
[^:@\/]*                    then any run of characters that are NOT : @ or /
                            └ negated class — this is the password itself.
                              Why negated? So it can't overrun past the @ or
                              match the :// after "postgresql" (the / excludes that)
@                           up to the literal @
→ replaced with  :***@      colon, three stars, at-sign — structure kept, secret gone
```

Result: `postgresql://arete:***@localhost:5432/arete_dev`. One line, no temp files, no editor. This is what sed is for.

---

## Part 8 — sed & awk (the stream editors)

### sed — substitute, print, delete by line

```bash
# SUBSTITUTE
sed 's/foo/bar/' file          # first occurrence per line
sed 's/foo/bar/g' file         # every occurrence (g = global)
sed 's/foo/bar/gi' file        # + case-insensitive
sed -E 's/(user)_id/\1Id/g'    # ERE + backreference: user_id → userId
sed 's|/old/path|/new/path|g'  # any delimiter works — use | when the pattern has slashes

# IN-PLACE editing (writes the file):
sed -i 's/foo/bar/g' file      # GNU sed (Linux). macOS needs: sed -i '' 's/foo/bar/g'

# PRINT a line range (-n = quiet except explicit prints):
sed -n '325,345p' seed.ts      # ← used on the project to view seed.ts lines 325–345

# DELETE a line range in place:
sed -i '335,388d' seed.ts      # ← used to remove the legacy message block
                               #   (line numbers came from grep -n first!)
```

The two-step surgical pattern from this project is worth naming:
1. `grep -n "landmark" file` → get exact line numbers.
2. `sed -n 'A,Bp'` to **preview** the range, then `sed -i 'A,Bd'` to cut it.
Never delete by line number without previewing the range first.

### awk — columns and quick reports

awk splits each line into fields (`$1`, `$2`... on whitespace by default; `$0` = whole line).

```bash
awk '{print $1}' access.log                   # first column
awk -F: '{print $1}' /etc/passwd              # -F sets the delimiter
awk '$3 > 100 {print $1, $3}' data.txt        # filter rows by a numeric condition
awk '{sum += $2} END {print sum}' file        # sum a column
podman ps | awk 'NR>1 {print $NF}'            # NR>1 skips header, $NF = last field
```

Rule of thumb: **grep finds lines, sed edits lines, awk understands columns.** Reach for them in that order.

---

## Part 9 — Full Worked Pipelines (from this session)

```bash
# 1. Start stack → wait → verify health, as one guarded chain:
systemctl --user start podman.socket && \
podman compose -f docker-compose.dev.yml up -d && \
sleep 8 && podman ps --format '{{.Names}} {{.Status}}'
# `&&` gates each step on the previous one succeeding.

# 2. Apply migrations, show only the outcome (stderr merged so failures are visible):
bunx prisma migrate deploy 2>&1 | tail -6

# 3. Write a throwaway TS script via heredoc, run it, remove it — leave no trace:
cat > verify.tmp.ts << 'EOF'
...script...
EOF
bun verify.tmp.ts; rm verify.tmp.ts
# `;` not `&&` before rm: clean up even if the script failed.

# 4. Count call sites of a pattern to gauge blast radius before refactoring:
grep -rn "cache.del" backend/src --include="*.ts" | wc -l

# 5. Locate → preview → cut (the safe file-surgery ritual):
grep -n "Seed complete\|^}" prisma/seed.ts     # find boundaries
sed -n '335,388p' prisma/seed.ts               # preview exactly what will die
sed -i '335,388d' prisma/seed.ts               # cut

# 6. Prove a rate limit actually fires (never assume security config works):
for i in $(seq 1 7); do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3000/v1/auth/login \
    -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"wrong"}')
  echo "attempt $i: HTTP $code"
done
# curl flags: -s silent · -o /dev/null discard body · -w "%{http_code}" print ONLY the status.
# Expected: 401 ×5 then 429 ×2. If you never see 429, the limiter is configured but not enforced
# (in NestJS: ThrottlerModule without an APP_GUARD binding — a real bug caught this way).
```

---

## Part 10 — Production Notes (Arete specifics) & Study Path

### Release checklist for the current setup (Render + managed Postgres)

```bash
# The Docker image now runs `migrate deploy && db seed` on every boot, so a
# normal deploy is self-contained. The manual commands remain useful for
# out-of-band runs (e.g. seeding before a deploy, or a non-Docker environment):
DATABASE_URL="<render-url>" bunx prisma migrate deploy
DATABASE_URL="<render-url>" bunx prisma db seed
# Mobile: EAS build only if native config changed; OTA update otherwise.
```

Notes to remember:
- All crons are **UTC**; Lagos is UTC+1 (that's why quest-reminder is `0 6 * * *` = 7 AM WAT).
- `docker-compose.prod.yml` and `Dockerfile` exist in backend/ — the prod image builds the Nest app; env comes from Render's dashboard, not a .env file.
- Podman socket must be enabled after reboots unless you ran `systemctl --user enable --now podman.socket`.

### Study path

1. **Week 1:** Pipes, redirection, `grep -rn`, `head/tail/wc`. Do all code exploration in the terminal for a week.
2. **Week 2:** `find` with `-name/-type/-o/-prune/-exec`; write five real queries against this repo.
3. **Weeks 3–4:** Regex — do the worked examples, then [regex101.com](https://regex101.com) with real log lines. Learn BRE vs ERE once, properly.
4. **Month 2:** Containers — rebuild the compose file from memory; break it (wrong port, missing volume) and diagnose via `logs`/`inspect`. Learn volumes by destroying one on purpose (in dev!).
5. **Month 3:** Write a Dockerfile for a Nest app from scratch (multi-stage: build → slim runtime). Understand every line of the existing one.
6. **Advanced:** CI pipelines (GitHub Actions running migrate deploy + tests), monitoring (uptime checks, log aggregation), backup/restore drills for Postgres (`pg_dump`/`pg_restore` — practice the restore, not just the dump).
