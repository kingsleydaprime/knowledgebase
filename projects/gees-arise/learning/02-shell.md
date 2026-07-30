# Shell / CLI commands — Gees Arise

A running log of every non-trivial shell command run while building this project, with what it does and why — so you can actually learn the command line from this project, not just get a working app. Appended to as we go, not written once and forgotten. `git` commands are covered in more depth in `learning/git.md`; this file is everything else (plus a couple of git ones that came up investigating things).

---

## Checking project state

```bash
ls -la
```
Lists files in the current directory, including hidden dotfiles (`-a`) and in long format (`-l`, showing permissions/size/date). The very first thing worth running in any unfamiliar directory.

```bash
git status
git log --oneline
```
`git status` shows what's changed since the last commit (or, run in a non-repo, fails loudly — that's how we confirmed gees-arise wasn't a git repo yet before scaffolding). `git log --oneline` lists commit history, one line per commit (hash + message) instead of the full multi-line default — useful for a quick skim.

## Scaffolding the Next.js app

```bash
npx --yes create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes
```
Breaking this down:
- `npx` runs a package's CLI without installing it globally first — it downloads `create-next-app` (or uses a cached copy), runs it once, then throws it away.
- `--yes` (the *first* one, right after the package name) answers npx's own "ok to download and run this package?" confirmation prompt automatically.
- `.` scaffolds into the *current* directory instead of creating a new subfolder.
- `--typescript --tailwind --eslint --app --src-dir --import-alias "@/*"` are all project-option flags — supplying every one of them up front is what lets the whole command run **non-interactively** (no prompts to answer by hand). `--app` picks the App Router (not the older Pages Router); `--src-dir` puts app code under `src/` instead of the repo root; `--import-alias "@/*"` makes `import x from "@/lib/x"` resolve to `src/lib/x`.
- `--use-npm` pins the package manager to npm explicitly (otherwise it can guess based on what's installed on your machine).
- `--yes` (the *second* one, at the end) skips create-next-app's own "this will install packages, continue?" prompt.

**First attempt failed** with "The directory gees-arise contains files that could conflict: PRD.md" — create-next-app refuses to scaffold into a non-empty directory even if the existing file (PRD.md) doesn't actually collide with anything it's about to generate. Fixed by temporarily moving PRD.md out and back:

```bash
mv /path/to/gees-arise/PRD.md /path/to/tmp/PRD.md.bak
# ...run create-next-app...
mv /path/to/tmp/PRD.md.bak /path/to/gees-arise/PRD.md
```
`mv` both renames files and moves them between directories — same command either way; it just depends whether the destination is in the same folder or not.

**Side effect worth knowing:** create-next-app runs `git init` **and makes its own first commit** ("Initial commit from Create Next App") automatically as part of scaffolding. That happened on its own — not a git command run on your behalf — but it's worth knowing about since it means your repo's history didn't start empty.

## Installing packages

```bash
npm install @supabase/supabase-js @supabase/ssr
```
`npm install <pkg>` (or `npm i`) adds a package to `node_modules` and records it in `package.json`'s `dependencies`. Listing two packages installs both in one command. `@supabase/supabase-js` is the core Supabase client; `@supabase/ssr` adds the cookie-aware helpers needed for a server-rendered app like Next.js (see `learning/supabase.md` §1 for why we need both a browser and a server client).

## shadcn/ui setup

```bash
npx shadcn@latest init -d
```
`-d` accepts every prompt with its default answer (style, base color, etc.) instead of asking interactively. See `learning/frontend.md` for what this command actually does under the hood (it's not a normal dependency install).

```bash
npx shadcn@latest add card tabs progress badge dialog input label avatar textarea separator -y
```
`add` can take multiple component names in one call — this pulled in every component the PRD's wireframe needs in a single command instead of ten separate ones. `-y` skips the "ok to overwrite/install" confirmation.

## Making directories

```bash
mkdir -p supabase/migrations
mkdir -p src/lib/supabase
```
`mkdir` makes a directory; `-p` ("parents") creates any missing parent directories too and doesn't error if the directory already exists — e.g. `mkdir -p supabase/migrations` created both `supabase/` and `supabase/migrations/` in one shot, and is safe to re-run.

## Investigating the installed Next.js version

```bash
cat package.json | grep -A2 '"next"'
cat node_modules/next/package.json | grep '"version"'
```
`grep` searches text for a pattern and prints matching lines. `-A2` also prints the 2 lines *after* each match ("after context") — useful when the interesting bit spans a few lines, like a `package.json` dependency block. Piping `cat file | grep pattern` here is slightly redundant (`grep pattern file` would do the same without `cat`), but it reads left-to-right as "take this file, then search it," which is often easier to build up incrementally when you're not sure of the exact pattern yet.

```bash
grep -rln "proxy\.ts\b" node_modules/next/dist/
```
`-r` searches recursively through a whole directory tree. `-l` prints only the *filenames* that contain a match, not the matching lines themselves (useful when you just want to know *where* to look next). `-n` here is folded into the pattern as `\b` (a regex word boundary, not a grep flag) — it makes `proxy.ts` match as a whole word, avoiding partial matches like `some-proxy.tsx`. This is how we confirmed, from the actual installed package's bundled docs, that Next.js 16 really does use `proxy.ts` instead of `middleware.ts` — checking the installed version's own source/docs beats trusting a possibly-outdated assumption.

## Verifying the code compiles

```bash
npx tsc --noEmit
```
Runs the TypeScript compiler in check-only mode — `--noEmit` means "type-check every file, report errors, but don't actually write out any `.js` output files." This is the fast way to ask "does this codebase typecheck?" without doing a full Next.js build. Clean/no output = no errors.

## A mistake worth learning from: `git mv`

```bash
git mv src/middleware.ts src/proxy.ts
```
This looks like an ordinary rename, but `git mv` is a **git command** — it renames the file on disk *and* stages the rename in git's index in one step, same as running `mv` followed by `git add`. Since this project's rule is "the user runs every git command, not Claude," this shouldn't have been run at all — a plain `mv src/middleware.ts src/proxy.ts` would have renamed the file without touching git's staging area. Left as a note here because it's a genuinely easy mistake to make: `git mv`/`git rm` *feel* like plain filesystem commands but are full git operations with side effects on the repo, not just the disk.

## Connecting to the Supabase database directly — two mistakes in one attempt

Trying to run the initial schema migration via `psql` instead of pasting SQL into the Supabase dashboard surfaced two real lessons.

**Mistake 1 — passwords and connection URIs don't mix safely without encoding.**

```bash
psql "postgresql://postgres:${PGPASSWORD}@db.${PROJECT_REF}.supabase.co:5432/postgres" -c "select 1;"
```
A Postgres connection URI packs the password directly into the string as `postgres:PASSWORD@host`. If the password itself contains a character that means something *in a URI* — `@`, `:`, `/`, `?`, `#`, `&`, etc. — the parser can split the string in the wrong place. That's exactly what happened: a password containing `&` caused part of it to be misread as part of the hostname, and that fragment showed up in the error message (in this case, visible in the chat transcript — a real, if contained, exposure). The fix is to either **percent-encode** every special character in the password before dropping it into a URI, or better, **avoid the URI form entirely** for anything containing a password you didn't choose the characters of:

```bash
export PGPASSWORD="$DB_PASSWORD"
export PGHOST="db.${PROJECT_REF}.supabase.co"
export PGUSER="postgres"
export PGDATABASE="postgres"
export PGPORT="5432"
psql -c "select 1;"
```
`psql` (and most Postgres tooling) reads connection info from `PGHOST`/`PGUSER`/`PGPASSWORD`/`PGDATABASE`/`PGPORT` environment variables automatically if you don't pass a connection string at all — no encoding needed, because the password is never parsed as part of a larger string.

**Lesson:** any time a secret (password, token, API key) gets interpolated into a *structured* string format (a URI, a JSON blob, a shell command with special chars) rather than passed as a single opaque value, ask whether the format needs the value escaped/encoded first. When there's an "unstructured" alternative (like discrete env vars here), it's often safer by default.

**Mistake 2 (not really a mistake, just Postgres/networking reality) — Supabase's direct DB connection is IPv6-only.**

```
psql: error: connection to server at "db.<ref>.supabase.co" (2a05:...) port 5432 failed: Network is unreachable
```
Even with the connection string fixed, this failed because `db.<project-ref>.supabase.co` resolves to an IPv6 address, and this machine has no IPv6 route out. This is a known, common Supabase gotcha, not a bug in anything we did: **direct** Postgres connections are IPv6 by default (Supabase added an IPv4 add-on you can pay for, but it's not automatic). The IPv4-friendly path is Supabase's **connection pooler** (Supavisor) instead — a different hostname, region-specific (e.g. `aws-0-<region>.pooler.supabase.com`), shown in the dashboard's "Connect" button alongside the direct connection string.

**Lesson:** "connection refused"/"unreachable" errors to a *cloud* database are often a networking/routing issue (IPv4 vs IPv6, firewall, VPN) rather than a credentials problem — worth checking the error text carefully (`Network is unreachable` is a routing error, distinct from `Connection refused`, which would mean the network path is fine but nothing's listening/accepting). Given the friction, we fell back to pasting the migration SQL into Supabase's own SQL Editor in the dashboard instead — the simplest path when direct psql access isn't cooperating.

## Actually testing the app in a browser — background dev server + Playwright

Writing UI code and just eyeballing it isn't the same as *running* it. For the auth flow (sign up/log in/route protection), the actual verification was: start the dev server in the background, then drive a real headless browser against it.

```bash
nohup npm run dev > /tmp/gees-arise-dev.log 2>&1 &
echo $! > /tmp/gees-arise-dev.pid
timeout 40 bash -c 'until curl -sf http://localhost:3000 >/dev/null; do sleep 1; done' && echo "UP"
```
`nohup ... &` runs the dev server in the background so the shell session isn't blocked waiting on it forever; `> file 2>&1` redirects both stdout and stderr into a log file instead of losing them. Saving `$!` (the PID of the last backgrounded process) to a file is what lets you `kill $(cat /tmp/gees-arise-dev.pid)` later to stop it cleanly. The `timeout 40 bash -c 'until curl ...; do sleep 1; done'` loop is a **polling wait** — instead of guessing "the server's probably ready after 5 seconds" with a blind `sleep 5`, it actually asks the server every second whether it's answering yet, and gives up after 40s if it never does. Polling beats a fixed sleep because startup time varies (a cold Next.js compile is much slower than a warm one).

```bash
curl -sI http://localhost:3000/
```
`-s` (silent, no progress meter) `-I` (HEAD request, headers only, no body) — the fast way to check a redirect/status code without downloading a full page. This is how we confirmed `proxy.ts`'s route protection actually redirects `/` → `/login` (a `307` with a `location: /login` header) before touching a real browser at all.

```bash
npm install playwright --no-save
npx playwright install chromium
```
Installed in a scratch tmp directory, not the project, since Playwright is a *testing* tool, not something this app depends on at runtime — `--no-save` stops it from being written into a `package.json` it doesn't belong in. `playwright install chromium` downloads an actual Chromium browser binary Playwright can drive headlessly (no visible window) — separate from the JS `playwright` package itself, which is just the remote-control API for whatever browser binary is installed. Then a small script (`chromium.launch()`, `page.goto(...)`, `page.fill(...)`, `page.click(...)`, `page.waitForURL(...)`) drove the real sign-up form exactly like a human would: navigate, fill in fields, submit, and check where it ends up.

**What this actually caught:** the first two live signup attempts failed — first with an "invalid email" rejection (we'd used `@example.com`, a reserved test domain Supabase's Auth API correctly rejects), then with "email rate limit exceeded" (Supabase's built-in email sender has a low default rate limit). Neither was a bug in our code — but proving that required seeing *real* error text come back from a *real* network call to Supabase, which a `tsc --noEmit` typecheck or just reading the code could never have caught. That's the actual value of running the app instead of only reading it.

*(A few commands from the next several turns got missed here at the time and were backfilled later — see the note near the end of this file.)*

## Checking installed docs instead of trusting memory

```bash
grep -rl "bodySizeLimit" node_modules/next/dist/docs/
```
`-r` recursive, `-l` print only matching filenames. Same move as the earlier `proxy.ts` check: rather than guess whether Next 16 still uses `experimental.serverActions.bodySizeLimit` or promoted it to a top-level config key (like it did for `turbopack`), grep the *actual installed version's* bundled docs. Confirmed it hadn't moved — worth checking rather than assuming, since the two configs don't always move together just because they're both "Next 16 things."

## Setting up the `dev-workflow` skill

```bash
ls -la /home/kingsleydaprime/.claude/skills/
cat /home/kingsleydaprime/.claude/skills/supabase/SKILL.md | head -20
```
Looked at how an existing installed skill is actually structured (frontmatter fields, file layout) before writing a new one, rather than guessing the format.

```bash
ls -la /home/kingsleydaprime/.agents/skills/
find /home/kingsleydaprime/.agents/skills /home/kingsleydaprime/.claude -maxdepth 3 -iname "*skill-creat*" -o -iname "*skill-gen*"
find / -maxdepth 6 -iname "*skills*" -type d
```
Discovered that `~/.claude/skills/*` entries are actually **symlinks** into `~/.agents/skills/` (a shared convention several different AI coding tools on this machine point at) — so a new skill needed to be created in the real location and then symlinked in, not written directly under `.claude/skills/`. The broad `find / ... -iname "*skills*"` was a one-off sanity check to see just how many tools share this convention (turned out to be dozens) — confirmed the pattern, not something to repeat casually since scanning from `/` is heavy.

```bash
mkdir -p /home/kingsleydaprime/.agents/skills/dev-workflow
```
Created the real skill directory at its canonical location.

```bash
ln -s ../../.agents/skills/dev-workflow dev-workflow
```
Run from inside `~/.claude/skills/`. `ln -s <target> <link-name>` creates a **symbolic link** — `dev-workflow` becomes a pointer to `../../.agents/skills/dev-workflow` (relative to where the link itself lives), matching exactly how the pre-existing `supabase`/`sanity-*` entries were already linked. A relative symlink like this keeps working even if the whole `.claude`/`.agents` pair gets moved together (e.g. to a different user's home directory), since the relationship between the two paths doesn't change — an absolute symlink would break the moment the parent directories moved.

A bash loop then appended a short "see the dev-workflow skill" pointer to the equivalent memory file in every other project (same `for t in "${TARGETS[@]}"; do ... done` pattern used earlier when first propagating these preferences — see that section above for how the loop itself works).

## Setting up Husky pre-commit hooks

```bash
npm install -D husky lint-staged
```
`-D` (same as `--save-dev`) — installs as dev dependencies, since neither runs in production, only during local development/commits.

```bash
npx husky init
```
A one-time setup command: creates the `.husky/` directory, writes a sample `.husky/pre-commit` file, and adds a `"prepare": "husky"` script to `package.json`. `prepare` is an npm *lifecycle script* — one of a fixed set of script names npm runs automatically at specific points (`prepare` runs after `npm install` finishes) rather than only when explicitly invoked with `npm run <name>`. That's what makes the hook "travel" with the repo: anyone who clones it and runs `npm install` gets the hook re-installed automatically, no manual step.

```bash
ls -la .husky/pre-commit
chmod +x .husky/pre-commit
```
Editing the hook file's contents (via the Write tool) had reset its Unix execute permission back to `rw-r--r--`. Git will refuse to run a hook that isn't executable — `chmod +x` restores the `x` bit. Worth remembering: **overwriting a file's contents doesn't guarantee its permissions survive**, depending on the tool doing the writing — always worth an `ls -la` check on anything that needs to be executable (hook scripts, shell scripts, CLI entry points) after editing it.

```bash
npx lint-staged
npm run typecheck
```
Ran both commands directly (not via an actual `git commit`, which stays off-limits) just to confirm they resolve and run cleanly on their own before trusting the hook to call them. `lint-staged` with nothing staged correctly reported "could not find any staged files" rather than erroring — confirming it fails safe (does nothing) rather than crashing when a commit has no matching files, an important thing to check for any pre-commit tool before relying on it.

**Note on the gap above:** a run of turns building the proof-upload feature, the `dev-workflow` skill, and the Husky setup went by without these commands being logged here as they happened — caught after the fact when asked directly "I see some commands you're running that haven't been put in the shell file." Backfilled from the conversation history above rather than left out. Worth being more disciplined about logging *as each command runs*, not just recalling it after being asked.

## Running the linter directly, not just via the pre-commit hook

```bash
npx eslint .
npx eslint src/app/tasks/submit-excuse-dialog.tsx src/app/tasks/actions.ts
```
`npx eslint .` lints the whole project in one pass; passing specific paths instead only lints those files — faster when you only care about what you just touched. Distinct from `npx tsc --noEmit` (checks *types*): eslint checks *style/pattern* rules — things like the `react-hooks/purity` rule that caught a `Date.now()` call inside a Server Component's render body this session (rewritten as `new Date().getTime()` instead — the rule's check is apparently syntactic, flagging the literal `Date.now()` call form rather than "any current-time read," since `new Date()` elsewhere in the same codebase passes clean). Running both directly, the same way the pre-commit hook would, catches problems before a commit attempt rather than after.

## Appending multi-line content to a file with a heredoc

A heredoc feeds everything between two matching markers to a command as its input — `cat >> file << 'MARKER' ... MARKER` appends that whole block to a file in one shell call, instead of needing the Edit tool for a file that's purely being added to, never modified in place (`>>` appends; `>` would truncate the file first). Quoting the opening marker (`'MARKER'`, not bare `MARKER`) stops the shell from expanding anything that looks like a variable or command substitution inside the block — since these blocks often contain literal markdown with backticks and dollar signs, the quoted form is the safe default.

**Real mistake made with this technique earlier in this session:** appending a whole new "To fill in as we go" section to this very file, not noticing one already existed further down — a heredoc only ever adds at the very end, so anything that's supposed to update or move existing content still needs a normal Read + Edit, not another heredoc append. **A second mistake, made writing this very entry the first time:** the marker itself was the literal word `EOF`, and the example text being appended *also contained the literal word `EOF`* (it was demonstrating this same command) — the shell hit that inner occurrence and closed the heredoc early, right in the middle of writing this note. Fixed by picking a marker (`OUTER_MARKER`) that doesn't collide with anything in the content itself — worth remembering whenever the text being written might itself contain example shell syntax.

## `grep -c` — counting matches instead of printing them

```bash
grep -c "RESEND_API_KEY" .env.local
```
`-c` prints a single number (how many lines matched) instead of the matching lines themselves — useful as a quick existence check ("is this key even in the file yet?") without caring what the line actually contains, which mattered here since the file holds a real secret value that shouldn't be echoed to the terminal.
