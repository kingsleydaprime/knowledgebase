# Arete — DevOps, Databases & the Shell

From [`../learning/devops/`](../learning/devops/) — containers, Prisma operations, and a deep dive
into grep / find / sed / awk / regex.

Shell questions come up more than people expect, especially for backend roles — usually as
*"how would you find X in a large codebase"* or *"walk me through debugging this on a server."*

---

### Q1. [Intermediate] 🔥 Explain the three Prisma migrate commands and where each belongs.

**Strong answer covers:**
- **`migrate dev`** — development only. Diffs your schema, generates a migration, applies it, and
  regenerates the client. It requires a **shadow database** (it creates and drops one to compute the
  diff safely), and it will happily reset your database if history has drifted.
- **`migrate deploy`** — production. Applies pending migrations in order and nothing else. No
  generation, no shadow DB, no destructive reset.
- **`db push`** — prototyping only. Force-syncs the schema with no migration file, so there's no
  history and no path to production.

**The rule:** `dev` writes history, `deploy` replays it, `push` skips it. Running `migrate dev`
against production is the mistake this distinction exists to prevent.

---

### Q2. [Advanced] 🔥 You needed a migration but had no database to run against. What did you do?

**Strong answer covers `prisma migrate diff` — the trick worth knowing:**

```bash
cp prisma/schema.prisma /tmp/schema-old.prisma     # snapshot BEFORE editing
# ...edit schema.prisma...
bunx prisma migrate diff \
  --from-schema-datamodel /tmp/schema-old.prisma \
  --to-schema-datamodel   prisma/schema.prisma \
  --script                                          # emit SQL to stdout
```

Paste the output into `prisma/migrations/<YYYYMMDDHHMMSS>_<name>/migration.sql` and `migrate deploy`
treats the hand-placed folder exactly like a generated one.

**Why it's a good answer:** `migrate diff` compares any two schema states — schema files, live
databases, or migration histories — so it's also how you generate a migration *against production's
actual state*, or verify that your history produces the schema you think it does. The folder-name
format matters: the timestamp prefix is the ordering mechanism.

---

### Q3. [Advanced] 🔥🔥 A production data bug, and you can't get a SQL shell. How do you investigate?

**Strong answer covers:** go through the app's own ORM with a throwaway script using the same
`DATABASE_URL` the backend uses —

```bash
cat > debug.tmp.ts << 'EOF'
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
prisma.user.findMany({ take: 5, orderBy: { createdAt: 'desc' } })
  .then(console.log).finally(() => prisma.$disconnect());
EOF
bun debug.tmp.ts; rm debug.tmp.ts
```

**Then tell the story that makes it concrete:** this is how the seed race was diagnosed in *three
queries* — users existed ✓, tasks existed ✓, user-pillars empty ✗. Root cause isolated without ever
opening a SQL shell.

**The transferable point:** the connection your app already has is a debugging tool. Not being able
to `psql` is an inconvenience, not a blocker — and quoted heredoc (`<< 'EOF'`) matters here, because
unquoted would let the shell expand `$` inside the script.

---

### Q4. [Intermediate] Docker vs Podman — what actually differs?

**Strong answer covers:** Podman is daemonless and rootless by default — containers run as your user
with no privileged background service, which removes the "member of the docker group is effectively
root" problem. The CLI is deliberately Docker-compatible, so commands translate directly. The
practical friction: rootless means low ports need extra configuration, volume permissions are mapped
through user namespaces (so file ownership inside and outside the container differs), and on SELinux
systems mounts need the right label — which is where most "Docker command doesn't work under Podman"
reports actually come from.

---

### Q5. [Beginner] Walk me through your dev compose file. What's in it and why?

**Strong answer covers:** Postgres and Redis as services with pinned image versions, named volumes so
data survives a container restart, ports published to localhost only, and environment variables for
credentials that match the app's `DATABASE_URL`. The reason it's in version control: a new machine
gets a working dependency stack with one command, and nobody is running a subtly different Postgres
version than production.

---

### Q6. [Intermediate] 🔥 Explain the pipeline model. Why is the shell powerful?

**Strong answer covers:** each tool does one thing and reads/writes text streams, so `|` composes
them into a program you didn't have to write. `grep` filters lines, `sort`/`uniq -c` counts,
`awk` extracts columns, `sed` transforms. The power isn't any individual tool — it's that a
one-off question ("which endpoints appear most in this log?") becomes a one-line composition rather
than a script.

**The classic to have ready:** `... | sort | uniq -c | sort -rn | head` — count occurrences, ranked.
`uniq` only collapses *adjacent* duplicates, which is why the first `sort` is mandatory and why
forgetting it produces a wrong answer that looks plausible.

---

### Q7. [Intermediate] 🔥 Which grep flags do you actually use, and what does each solve?

**Strong answer covers, roughly in order of use:**
- `-r` recursive, `-n` line numbers (so the output is clickable/actionable)
- `-i` case-insensitive
- `-l` list matching files only — the right flag when you want "where does this live", not context
- `-v` invert — "lines that *don't* match", underrated for filtering noise out of logs
- `-E` extended regex, so you get `+`, `?`, `|` and groups without backslash-escaping everything
- `-w` whole word — the flag that stops `id` matching `videoId` and `hidden`
- `-A`/`-B`/`-C` context lines, essential when reading logs
- `--include='*.ts'` to scope by file type instead of piping through another filter

**The pro habit:** start broad and narrow down, and use `-l` first to see *where* before you look at
*what*.

---

### Q8. [Intermediate] 🔥 `find` — tests, actions, and the parentheses trap.

**Strong answer covers:** `find <path> <tests> <actions>`. Tests: `-name`/`-iname`, `-type f|d`,
`-mtime`, `-size`, `-path`. Actions: `-print`, `-delete`, `-exec cmd {} \;` (once per file) versus
`-exec cmd {} +` (batched — far faster, and the one to prefer).

**The trap:** combining tests. `-a` (AND) is implicit, `-o` is OR, and **OR binds loosely**, so
`find . -name '*.ts' -o -name '*.tsx' -print` prints only the `.tsx` matches — the `-print` binds to
the second test only. You need `find . \( -name '*.ts' -o -name '*.tsx' \) -print`, with the
parentheses escaped from the shell. The failure is silent and produces plausible-looking output,
which is what makes it worth knowing.

**Safety habit:** never write `-delete` first. Run it with `-print`, read the list, then change the
action.

---

### Q9. [Advanced] 🔥 Globs are not regex. Explain the difference and the three dialects.

**Strong answer covers:**
- **Globs** are shell filename patterns: `*` means "any characters", `?` means "one character".
  In **regex**, `*` means "zero or more of the previous item" and `.` means "any character" — so
  the glob `*.ts` is the regex `.*\.ts`. Confusing them is why patterns "don't work."
- **Three regex dialects:** BRE (basic — `grep`, `sed` by default, where `+`, `?`, `|`, `()` need
  backslashes), ERE (extended — `grep -E`, `sed -E`, where they don't), and PCRE (`grep -P`, most
  programming languages, adding lookarounds, lazy quantifiers, `\d`/`\w` shorthand).

**Why this matters practically:** the same pattern silently means different things in different
tools, so "my regex works in my editor but not in grep" is almost always a dialect problem, not a
logic problem.

---

### Q10. [Advanced] 🔥🔥 Dissect this: `sed 's/:[^:@\/]*@/:***@/' .env`

**This is the best shell question in the project — it's real, it's short, and every part has a
reason.**

**Strong answer covers, piece by piece:**
- `s/PATTERN/REPLACEMENT/` — sed's substitute command.
- `:` — a literal colon. In `postgresql://arete:PASSWORD@localhost`, that's the colon before the
  password.
- `[^:@\/]*` — a **negated character class**: any run of characters that are *not* `:`, `@` or `/`.
  This is the password itself. Negated rather than `.*` for two reasons: `.*` is greedy and would
  overrun past the `@`, and excluding `/` stops it matching back across the `://` after
  `postgresql`.
- `@` — the literal at-sign that terminates the password.
- Replacement `:***@` — keeps the structure, removes the secret.

**Result:** `postgresql://arete:***@localhost:5432/arete_dev`. One line, no temp files, no editor.

**The lesson to state:** a negated character class is usually the right tool where people reach for
non-greedy matching — it can't overrun the delimiter by construction, and BRE (which `sed` uses by
default) has no lazy quantifier anyway.

---

### Q11. [Intermediate] When do you reach for `awk` instead of `grep` or `sed`?

**Strong answer covers:** when the data is **columnar** and you need a specific field or an
aggregate. `awk '{print $2}'` extracts a column; `awk '$3 > 100'` filters on a field's value;
`awk '{sum += $2} END {print sum}'` totals one. `grep` filters lines, `sed` transforms text, `awk`
understands records and fields — that's the division. The moment you're counting `cut -d' ' -f`
positions and piping through three more tools, awk was the answer.

---

### Q12. [Intermediate] What's your release checklist for this stack?

**Strong answer covers:** migrations applied with `migrate deploy` (never `dev`) as a separate,
verifiable step before the new code starts serving; environment variables checked on the target,
because a missing one is the most common deploy failure; seed/content deployment run idempotently;
health check after boot; and the log read on first boot rather than assumed — a process that starts
and then fails to connect to Redis looks identical to a healthy one from the outside.

**The Arete-specific one worth naming:** cron schedulers are upserted on boot, so a deploy
re-registers them — which is safe *because* it's an upsert, and would silently double every
scheduled job if it weren't.

---

### Q13. [Beginner] How do you handle `.env` files and secrets in a solo-founder setup?

**Strong answer covers:** `.env` is gitignored, a committed `.env.example` documents the required
keys with dummy values, and production values live in the platform's secret store (Render's
environment settings here) rather than in a file. And when you *do* need to show an env file — in a
screenshot, a log, or a support conversation — mask it (Q10). Naming the masking habit as part of
secret handling, rather than as a shell trick, is the better answer.
