# 04 — Shell

*MyPaddie, Day 1 (2026-10-05).* See also: [[devops/01-linux/index|linux]]

## Diagnosing a "hung" install on a slow network

`bun install` sat on "Resolving dependencies" for 15 minutes. Instead of retrying
blindly, measure:

```bash
curl -s -o /dev/null -w "%{http_code} %{size_download}B %{time_total}s\n" \
  https://registry.npmjs.org/is-number
```

- `-s` silent, `-o /dev/null` throw the body away
- `-w` print a format string after the request — `%{http_code}`, `%{size_download}`,
  `%{time_total}`, `%{speed_download}` are the useful ones

Result: a 36 KB file took 2.2 s (~16 KB/s). Next.js's package metadata is several
MB → minutes per package. Not a bug — a slow pipe.

```bash
timeout 30 curl … || echo TIMEOUT
```
`timeout N cmd` kills `cmd` after N seconds. Exit code **124** means "timeout
killed it" — handy for telling a hang apart from a real failure.

## Installing from the cache

```bash
bun install --help | grep -iE 'offline|cache'
bun install --prefer-offline   # use cached metadata, only fetch what's missing
bun install --offline          # never touch the network
```

The cache (`~/.bun/install/cache`) already had `next@16.3.8` from other projects.
`--prefer-offline` finished in 32 ms. Lesson: `--help | grep` the tool for the
flag before reaching for workarounds.

## Exit codes through pipes: zsh vs bash

```bash
some-cmd | tail -5; echo $?   # $? is tail's exit code, not some-cmd's!
```

To get the first command's status: bash has `${PIPESTATUS[0]}`, **zsh** has
`${pipestatus[1]}` (lowercase, 1-indexed). Your shell is zsh, so `PIPESTATUS`
printed nothing. Simplest portable fix: don't pipe — redirect to a file, check
`$?`, then read the file:

```bash
cmd > out.log 2>&1; echo "exit=$?"; tail out.log
```

## `pkill -f` can kill itself

```bash
pkill -f 'bun install'; bun install --prefer-offline
```

`-f` matches the *full command line* — and the shell running this line contains
the text `bun install`, so `pkill` killed its own shell (exit 144 = 128 + signal
16). Match more precisely, or kill by PID from `ps`.

## Supabase CLI as a dev dependency

```bash
bun add -d supabase      # pinned per project, in the lockfile
bunx supabase --version
bunx supabase init
bunx supabase migration new core_schema   # creates supabase/migrations/<timestamp>_core_schema.sql
bunx supabase db start                    # only Postgres — not the whole stack
bunx supabase test db                     # run pgTAP tests in supabase/tests
```

`migration new` generates the timestamped filename — never hand-invent it.
`db start` instead of `start` pulls one image instead of ~10, which matters on
16 KB/s.

## Podman pretending to be Docker

`docker info` reports "Server Version: 5.8.7 … rootless" — that's Podman. The
Supabase CLI speaks the Docker API, and `DOCKER_HOST` points it at Podman's socket:

```bash
echo $DOCKER_HOST   # unix:///run/user/1000/podman/podman.sock
```

## When the CLI is the slow part: go under it

`supabase db start` had Postgres **up and healthy**, then sat on "Initialising
schema…" downloading yet another image. Read the logs before waiting longer:

```bash
podman ps --format '{{.Names}} {{.Image}} {{.Status}}'   # is the DB actually up?
podman logs --tail 8 supabase_db_mypaddie                # "ready to accept connections"
```

Two tricks got around it:

1. **Pin the image you already have.** The CLI reads the Postgres version from
   `supabase/.temp/postgres-version` (normally written by `supabase link`):
   ```bash
   printf '17.6.1.156' > supabase/.temp/postgres-version
   ```
2. **Skip the CLI and run the image directly:**
   ```bash
   podman run -d --name mypaddie_db -e POSTGRES_PASSWORD=postgres \
     -p 127.0.0.1:54322:5432 public.ecr.aws/supabase/postgres:17.6.1.156
   podman exec -i mypaddie_db psql -U postgres -v ON_ERROR_STOP=1 --single-transaction \
     < supabase/migrations/20261005133805_core_schema.sql
   ```
   - `-p 127.0.0.1:54322:5432` publish on localhost only, not on every network interface
   - `podman exec -i` keeps stdin open so `< file.sql` reaches `psql` inside the container
   - `-v ON_ERROR_STOP=1` stop at the first error (default: keep going!)
   - `--single-transaction` all-or-nothing: a failed migration leaves no half-built schema

Killing the CLI mid-start made it **remove its container** (it cleans up after
itself) — so kill a tool and you may lose what it built.

## pkill -f, again

Same trap as above, hit a second time the same day: `pkill -f '…supabase db start'`
inside a command that also *contained* that text killed its own shell. The safe
version finds PIDs first, and the `!/awk/` stops awk matching itself:

```bash
for p in $(ps -eo pid,cmd | awk '/supabase db start/ && !/awk/ {print $1}'); do kill $p; done
```

## Day 2 odds and ends

- `bun add --exact pkg@^2` does **not** pin — a range wins over `--exact`. Read the
  installed version (`node -p "require('./node_modules/pkg/package.json').version"`)
  and write it into package.json yourself.
- Read a library's real API from its types, not memory:
  `grep -n "registerTool" node_modules/@modelcontextprotocol/server/dist/*.d.mts`
- `supabase gen types typescript --db-url postgresql://…` generates types from
  any running Postgres — no linked project needed.
- In zsh, `?` in an unquoted URL is a glob: `curl http://x/login?next=/a` fails
  with "no matches found". Quote URLs: `curl 'http://x/login?next=/a'`.
- Smoke-testing a server you start in the background: wait until it answers
  (`for i in $(seq 1 30); do curl -s -o /dev/null URL && break; sleep 1; done`),
  probe it, then kill it by PID.

## zsh eats `--include=*.ts` before grep sees it (2026-10-07)

```sh
grep -rn "goal_completion" src --include=*.ts
# zsh: no matches found: --include=*.ts
```

zsh tries to expand every unquoted `*` as a filename glob — even inside a
flag. Bash quietly passes an unmatched glob through as literal text; zsh
(with the default `NOMATCH` option) refuses to run the command at all. Quote
the pattern so grep gets it untouched:

```sh
grep -rn "goal_completion" src --include='*.ts' --include='*.tsx'
```

## Types from the local database, not the hosted one

`bun run db:types` uses `--linked`, i.e. the hosted project — which only has
the migrations you've pushed. While a migration is still local:

```sh
supabase db reset --local                      # apply every migration from scratch
supabase gen types typescript --local --schema public > /tmp/types.ts
diff src/shared/supabase/database.types.ts /tmp/types.ts   # look before overwriting
```

Generating to a temp file and diffing first shows exactly what the new
migration added (here: two columns and one function) and catches surprises
before they land in the real file.

## Scripted edits that fail loudly

```sh
python3 - <<'PY'
p = 'src/features/items/items.actions.ts'
s = open(p).read()
old = 'const optionalText = z.string().trim()...'
assert old in s, old          # no match → crash, not a silent no-op
s = s.replace(old, 'new text')
open(p, 'w').write(s)
PY
```

`python3 -` reads the program from stdin; `<<'PY'` (quoted delimiter) stops
the shell expanding `$` and backticks inside it. The `assert` is the point:
`sed` with a pattern that doesn't match exits 0 and changes nothing, which
looks exactly like success.

## Re-creating a SQL function from its latest version (2026-10-08)

Each rule change to a big SQL function (`collect_nudges`, ~150 lines) is a new
migration that re-creates the whole thing. The safe routine, as one command:

```sh
SRC=$(grep -ln "create or replace function private.collect_nudges" supabase/migrations/*.sql | sort | tail -1)
{
  echo "-- why this change"
  awk '/create or replace function private.collect_nudges/,/^\$\$;/' "$SRC" \
    | sed "s/^           or (t.any_time_day = t.today and t.local_time >= time '15:00'))$/           or (t.any_time_day = t.today and t.local_time >= t.any_time_from))/"
  echo "revoke all on function private.collect_nudges(timestamptz) from public;"
} > supabase/migrations/20261105090000_any_time_nudge_setting.sql

diff <(awk '/…/,/^\$\$;/' "$SRC") <(awk '/…/,/^\$\$;/' supabase/migrations/20261105090000_any_time_nudge_setting.sql)
```

- **`sort | tail -1`**: migrations are named by timestamp, so sorting the
  filenames puts the newest last. That's the *latest* definition. Copying an
  older one silently loses later changes (this nearly dropped a column once).
- **`awk '/start/,/end/'`** prints from the line matching `start` through the
  next line matching `end`. `^\$\$;` is a line that is exactly `$$;`, the end
  of a Postgres function body.
- **`sed` with the whole old line, `^…$` anchored**, so it can only change that
  exact line. If the pattern doesn't match, nothing changes, and the `diff` step
  is what catches that.
- **`{ …; } > file`** groups several commands into one output: header, function,
  `revoke`.
- **`diff <(cmd1) <(cmd2)`**: *process substitution*. Each `<(…)` becomes a
  temporary file holding that command's output, so you can diff two command
  outputs without writing files. The only differences should be your change.

### The gotcha: a range re-opens when the start pattern matches again

```sh
awk '/function private.pause_for_events/,/^\$\$;/' file.sql
```

That migration also had `revoke all on function private.pause_for_events(...)`
*after* the function. The revoke line matched the start pattern too, so `awk`
opened a **second** range there and printed until the next `$$;`, the end of a
*different* function. A `grep -l "function private.send_nudges"` hunting for the
definition was fooled the same way by a `revoke … send_nudges()` line.
**Anchor the pattern to the definition**:

```sh
awk '/^create (or replace )?function private.pause_for_events/,/^\$\$;/' file.sql
grep -ln "^create or replace function private.send_nudges" supabase/migrations/*.sql
```

## Querying the local database from the CLI

```sh
bunx supabase db query --local "select conname from pg_constraint where conrelid = 'public.bills'::regclass and contype = 'c'"
bunx supabase migration up --local     # apply new migrations to the running local DB
bunx supabase test db                  # run every pgTAP file
```

`db query` (CLI v2.79+) prints JSON, so pipe it to `grep conname` for a quick
look. It found the auto-generated name `bills_every_check`, which a migration
needed in order to drop and re-add the constraint. Never guess generated
constraint names.

## Proving a test catches the bug: make it fail on purpose

A new test for a fix passed, but would it have failed *without* the fix?
Temporarily load the old function, run the tests, and put the fix back:

```sh
F=supabase/migrations/20261111090000_pause_marker_survives_holds.sql
OLD=$(sed -n '/^create or replace function private.pause_for_events/,/^\$\$;/p' "$F" \
      | sed "s/p_now - interval '1 millisecond' from starting/p_now from starting/")
bunx supabase db query --local "$OLD"        # the old behaviour
bunx supabase test db | grep -E "Failed test|Result"   # → the two new tests fail ✓
bunx supabase db query --local "$(sed -n '/^create or replace function private.pause_for_events/,/^\$\$;/p' "$F")"
bunx supabase test db | grep Result          # → PASS
```

- `sed -n '…p'` prints only the matching block (same range idea as `awk`).
- `"$(…)"` passes the whole multi-line function as one argument. The quotes
  matter: unquoted, the shell would split it on spaces.
- This is the "red before green" step from testing ([[03-testing]]): a test
  you've never seen fail might be testing nothing.
