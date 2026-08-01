# Supabase — Sorepoint

Running Supabase locally, the schema/data model, migrations, and TypeGen.
Teaching *why*, newest topics appended as they come up.

For Slice 1 we run Supabase **locally** (Docker/Podman stack via the CLI), no
cloud project yet — see `~/code/spectroniq/sorepoint/DECISIONS.md`.

---

## 1. A container runtime the CLI can reach — rootless Podman

`supabase start` runs the whole local stack (Postgres, PostgREST, GoTrue/Auth,
Storage, Studio, …) as **containers**. The CLI talks to a Docker-compatible API
socket. On this Fedora box, real Docker's socket is root-owned (hence `sudo`),
but **Podman** is also installed and can expose a *rootless* socket — no sudo, no
root-equivalent `docker` group.

### Why rootless Podman over adding yourself to the `docker` group

The classic "just `sudo usermod -aG docker $USER`" works, but the `docker` group
is effectively **root**: any member can `docker run -v /:/host` and own the whole
filesystem. Rootless Podman runs containers as *your* user with no such group, so
a container break-out is contained to your user, not root. Better default for a
machine you care about.

### One-time setup

```bash
# Enable + start the rootless Podman API socket for your user.
#   --user  → your personal systemd instance, not the system one (no sudo)
#   enable  → start automatically on future logins
#   --now   → also start it right now
systemctl --user enable --now podman.socket
```

Then tell Docker-compatible tools where Podman's socket lives, via the standard
`DOCKER_HOST` env var (persisted in `~/.zshrc`):

```bash
export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
```

- `DOCKER_HOST` is the env var *every* Docker-API client reads to find the
  daemon. Pointing it at Podman's socket makes the Supabase CLI talk to Podman
  transparently — it never knows it isn't Docker.
- `$(id -u)` is your numeric user id (1000 here); the rootless socket always
  lives under `/run/user/<uid>/`.

Verify it's reachable:

```bash
podman info --format 'socket: {{.Host.RemoteSocket.Path}}  exists: {{.Host.RemoteSocket.Exists}}'
# socket: /run/user/1000/podman/podman.sock  exists: true
```

> Gotcha: `systemctl --user` services stop when you fully log out of *all*
> sessions, unless you enable lingering: `loginctl enable-linger $USER`. Not
> needed while you stay logged in.

---

## 2. Installing the Supabase CLI as a dev dependency (not global)

Supabase's docs explicitly recommend **not** installing the CLI globally. Instead
add it to the project so the version is pinned in `package.json` and travels with
the repo:

```bash
npm install supabase --save-dev
```

There is then **no global `supabase` command** — run it through the package
runner:

```bash
npx supabase --version   # 2.111.0
```

Why this is the better habit: a globally-installed CLI drifts per-machine and
isn't captured anywhere. As a pinned devDependency, everyone (and every CI run,
and future-you on a new laptop) gets the exact same CLI version from
`npm install`, and upgrades are a reviewable diff in `package.json`.

---

## 3. `supabase init` — scaffolding the project

```bash
npx supabase init --yes
```

Creates:

```
supabase/config.toml    # local stack config (ports, versions, feature toggles)
supabase/.gitignore     # ignores local-only artifacts (e.g. .branches, .temp)
```

`--yes` answers any prompt with the default. Without `-i/--interactive` it does
**not** try to write editor settings, so it's safe to run non-interactively. No
containers are touched by `init` — it only writes files.

---

## 4. Creating a migration file — let the CLI name it

```bash
npx supabase migration new create_core_schema
# → supabase/migrations/20260731211205_create_core_schema.sql
```

Never hand-invent a migration filename. The leading timestamp
(`YYYYMMDDHHMMSS`) is what orders migrations, and the CLI generates it correctly.
You then write your SQL into the empty file it created. (This is the *imperative
migrations* workflow — hand-authored SQL files applied in timestamp order — as
opposed to Supabase's newer *declarative schema* approach where you edit a
desired-state file and let the CLI diff it into a migration.)

---

## 5. Debugging `supabase start` on Fedora — SELinux vs rootless Podman

The first `supabase start` failed. The **log told us exactly what** (read errors
fully before reacting):

```
pgsodium_getkey.sh: /etc/postgresql-custom/pgsodium_root.key: Read-only file system
FATAL:  invalid secret key
... supabase_db_sorepoint: container is not ready
```

Diagnosis, step by step:

1. **The DB container couldn't write a file it expected to own.** Not a Supabase
   bug — something made an in-container path read-only.
2. `getenforce` → **`Enforcing`**. Fedora ships SELinux on.
3. The rule: on SELinux, a bind-mount into a container must be **relabeled**
   (Podman's `:z`/`:Z` mount suffix) or SELinux denies access. The Supabase CLI
   mounts config files **without** those suffixes, so SELinux made them
   read-only → the pgsodium key write failed → Postgres aborted.

**Fix — disable SELinux labeling for Podman containers**, user-scoped, in
`~/.config/containers/containers.conf`:

```ini
[containers]
label = false
```

This is equivalent to running every container with `--security-opt
label=disable`. Trade-off: it drops one mandatory-access-control layer for this
user's containers — but they're still **rootless**, so it's still safer than the
root-equivalent `docker` group.

Two things the config change alone doesn't do — both needed here:

- **Restart the Podman service so it re-reads config.** The container is created
  by the socket-activated `podman.service`, which reads `containers.conf` at
  startup — not from your shell:
  ```bash
  systemctl --user restart podman.socket
  ```
- **Delete the half-initialized volume.** The failed first run left a
  `supabase_db_sorepoint` volume with a partial data dir, so the next start said
  *"PostgreSQL Database directory appears to contain a database; Skipping
  initialization"* and would never regenerate the key. Postgres only runs its
  init (incl. pgsodium key) on an **empty** data dir:
  ```bash
  podman volume rm supabase_db_sorepoint
  ```

Lesson: an infra failure is a *diagnosis* problem, not a retry problem. The log
named the file, `getenforce` named the cause, and the fix followed from the
mechanism — not from trying random flags.

---

## 6. What `supabase start` gives you — and the new key names

On success it prints the local stack's URLs and keys:

```
API_URL     http://127.0.0.1:54321   # PostgREST + Auth + Storage gateway
DB_URL      postgresql://postgres:postgres@127.0.0.1:54322/postgres
STUDIO_URL  http://127.0.0.1:54323   # the dashboard UI
MAILPIT     http://127.0.0.1:54324   # catches outgoing auth emails locally
```

Keys — note Supabase's **new naming** (verified live here):

| New name (use these)       | Legacy equivalent   | Where it may go        |
|----------------------------|---------------------|------------------------|
| `sb_publishable_…`         | `anon` JWT          | browser-safe (public)  |
| `sb_secret_…`              | `service_role` JWT  | **server only** — bypasses RLS |

The publishable key is safe in the browser and is subject to RLS. The secret key
**bypasses RLS entirely**, so it must never reach client code — in Next.js that
means never giving it a `NEXT_PUBLIC_` prefix (any `NEXT_PUBLIC_*` var is bundled
into the browser build).

`npx supabase status` reprints all of this any time.

---

## 7. Migrations apply on start; TypeGen; wiring env

- **Migrations run automatically** during `supabase start` on a fresh DB — the
  log showed `Applying migration …create_core_schema.sql`. To reapply after
  editing a migration, `npx supabase db reset` rebuilds the DB from scratch.
- **Verify, don't assume** (Supabase skill rule #2). We confirmed the result by
  querying catalog tables *inside the container*:
  ```bash
  podman exec -i supabase_db_sorepoint psql -U postgres -At \
    -c "select tablename, rowsecurity from pg_tables where schemaname='public';"
  ```
  `rowsecurity = t` on every table confirmed RLS was enabled.
- **Advisors** (Supabase's built-in security/perf linter) — run before treating
  a schema as done:
  ```bash
  npx supabase db advisors   # → "No issues found"
  ```
  It flags things like RLS-disabled public tables and unindexed foreign keys.
  Ours passed because RLS is on everywhere and every FK has an index.
- **TypeGen** — one generated file the app *and* the worker import, so the types
  can never drift from the schema:
  ```bash
  npx supabase gen types typescript --local --schema public > src/lib/database.types.ts
  ```
  Regenerate this after every migration. `--schema public` keeps Supabase's
  internal `auth`/`storage` types out of it.
- **Env** — `.env.local` (git-ignored) holds the local URL + keys;
  `.env.example` (committed, placeholders) documents what's needed. Because RLS
  is on with **no policies yet**, the anon/publishable key sees nothing, so
  Slice-1 server code reads with `SUPABASE_SECRET_KEY`.

---

## 8. GRANTs vs RLS — two independent gates (a real bug)

The worker's first DB write failed with:

```
42501  permission denied for table scans
hint: GRANT SELECT ON public.scans TO service_role;
```

Surprising, because the SECRET key maps to `service_role`, which **bypasses RLS**.
But RLS wasn't the gate — **table GRANTs** were. They're independent:

- **GRANT** decides whether a role may touch a table *at all* (SELECT/INSERT/…).
- **RLS** decides which *rows* are visible *once* a role can touch the table.

`service_role` bypasses RLS but still needs the GRANT. Why was it missing? Because
**migrations run as the `postgres` role**, and `postgres`'s *default privileges*
in schema `public` grant the API roles only partial rights (DELETE/TRUNCATE/
REFERENCES/TRIGGER — no SELECT/INSERT/UPDATE). Supabase's *full* default grants
are attached to the `supabase_admin` role, so objects created by `postgres` (our
migrations) don't inherit them. Confirmed by inspecting `pg_default_acl`.

Fix — an explicit grant migration (kept separate; the schema migration was already
committed, and migrations are append-only):

```sql
grant select, insert, update, delete on all tables in schema public to service_role;
alter default privileges in schema public
  grant select, insert, update, delete on tables to service_role;   -- future tables too
```

Takeaways: (1) `permission denied` on Supabase is usually a GRANT problem, not an
RLS one; read the error's hint. (2) Once a migration is committed, add a new one
rather than editing it. (3) `alter default privileges` fixes the *next* tables so
you don't rediscover this every migration.

---

## See also

- `shell.md` — `systemctl --user`, env vars, the scaffolding move-aside trick
- `backend.md` — the pipeline worker that hit this bug; source adapters; OSM
- app repo `~/code/spectroniq/sorepoint/DECISIONS.md` — why local-first, worker-not-route
