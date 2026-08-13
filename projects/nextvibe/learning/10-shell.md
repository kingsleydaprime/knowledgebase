# NextVibe — Shell & Command Line

New file (2026-08-12), started while investigating the payout/ledger work. See also
`learning/09-devops.md` (deployment, env vars, server logs) and
`learning/backend/06-money-ledger-and-payouts.md` (the Prisma CLI commands used to generate
migration SQL safely).

This file covers: searching a codebase with `grep` and the zsh glob gotcha that silently
breaks it, `find` with pruning, sizing up an unfamiliar codebase quickly, loading `.env`
into a shell session, how ordinary commands leak credentials, and using `curl` status codes to
check what a deployed server is actually running.

---

## Part 1 — `grep -r` for Codebase Investigation

The workhorse for "does this code actually do what the schema claims":

```bash
grep -rni "withdrawal" --include='*.ts' . | grep -v "modules/withdrawals"
```

Flag by flag:

| Flag | Meaning |
|---|---|
| `-r` | recursive — walk directories |
| `-n` | print line numbers (so you can jump straight to it) |
| `-i` | case-insensitive |
| `--include='*.ts'` | only search files matching this pattern |

Piping to `grep -v <pattern>` **excludes** matches — here, "show me every mention of
withdrawal *outside* its own module." That single command is what proved the withdrawal
system was dead code: the only hit was one import line in `app.module.ts`, meaning nothing in
the entire codebase ever approved or paid a withdrawal.

### The zsh gotcha that will bite you

This fails in zsh:

```bash
grep -rn "withdrawal" --include=*.ts .
# zsh: no matches found: --include=*.ts
```

**Why:** zsh expands globs *before* the command runs. It tries to expand `*.ts` against the
current directory, finds no `.ts` files there, and — unlike bash, which would pass the
pattern through unchanged — zsh treats "no matches" as a hard error and refuses to run the
command at all.

**Fix:** quote it, so the shell passes the literal string to grep and lets *grep* do the
matching:

```bash
grep -rn "withdrawal" --include='*.ts' .
```

The general rule: **any glob meant for the program rather than the shell must be quoted.**
Same applies to `find -name '*.ts'`.

### Searching for several things at once

Alternation with `\|` (basic regex) finds any of a set of terms — useful for "does this
concept exist anywhere under any of its likely names":

```bash
grep -rni "platformFee\|commission\|serviceFee\|netAmount" --include='*.ts' .
```

Empty output here was the actual finding: no platform-fee logic existed anywhere.

**Beware `echo "(exit: $?)"` after a pipeline** — `$?` reports the exit status of the *last*
command in the pipe, not the grep you cared about. To test whether grep matched, check its
status directly, or just look at whether output appeared.

---

## Part 2 — `find` with Pruning

```bash
find . -path ./node_modules -prune -o -name "*.prisma" -print
```

Reads as: "for the path `./node_modules`, prune it (don't descend); *otherwise* (`-o`), if the
name matches `*.prisma`, print it."

`-prune` is what makes `find` fast in a JS project. Without it, `find` walks every one of the
tens of thousands of files under `node_modules`. The `-print` at the end is **required** here
— once you use `-o`, the implicit "print everything" behaviour goes away, and without it the
command silently outputs nothing.

---

## Part 3 — Sizing Up an Unfamiliar Codebase

```bash
wc -l *.prisma | sort -n
```

`wc -l` counts lines; `sort -n` sorts numerically (not lexically — without `-n`, "100" sorts
before "20"). Run over a schema directory it immediately shows where the complexity lives:

```
   21 withdrawals.prisma
   79 billing.prisma
  136 tickets.prisma
  237 enums.prisma
 1296 total
```

A 21-line file for the entire payout system next to a 136-line ticketing file is a strong
signal about which one was actually finished.

Related, for structure rather than size:

```bash
ls */ -d          # list only directories
ls -R modules/payments   # recurse one subtree
```

---

## Part 4 — Loading `.env` Into Your Shell

Some CLI tools need env vars present in the shell, not just loaded by the app:

```bash
set -a && source .env; set +a
```

- `set -a` — **auto-export**: every variable assigned from now on is exported to child
  processes automatically.
- `source .env` — run the file in the *current* shell (so the assignments stick). `./` would
  run it in a subshell and the variables would vanish when it exited.
- `set +a` — turn auto-export back off, so you don't accidentally export everything else you
  define later.

Without `set -a`, `source .env` defines the variables as shell-local only, and the command you
run next won't see them.

**Caution:** this puts secrets into your shell environment for the rest of the session, where
any process you launch can read them. Prefer letting the tool load `.env` itself when it can.

---

## Part 5 — Credentials Leaking Through Ordinary Commands

Running `npx prisma validate` printed this:

```
DEBUG: DATABASE_URL = postgres://avnadmin:AVNS_KfQ...@pg-....aivencloud.com:18220/defaultdb
```

The cause was a leftover line in `prisma.config.ts`:

```typescript
console.log('DEBUG: DATABASE_URL =', process.env.DATABASE_URL); // ← Add this temporary line
```

Two lessons:

1. **A `console.log` of a connection string leaks the password to every log that captures
   stdout** — your terminal scrollback, CI build logs, deployment logs. CI logs in particular
   are often readable by more people than the database itself.
2. **A comment saying "temporary" is not a mechanism.** If you add a debug line that prints a
   secret, delete it in the same session. Grep for it before committing:

   ```bash
   grep -rn "console.log.*process.env" --include='*.ts' .
   ```

Once a credential has been printed, rotating it is the only real fix — you cannot un-print it
from logs you don't control.

---

## Part 6 — `curl` for Checking What a Server Actually Returns

Often you don't want a response *body* — you want to know whether an endpoint exists, or is up,
or how slow it is. This prints only the status code:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/v1/some/route
```

| Flag | Meaning |
|---|---|
| `-s` | silent — suppress the progress meter, which otherwise pollutes output |
| `-o /dev/null` | throw the response body away |
| `-w "..."` | **write-out**: print this template after the request completes |
| `--max-time 60` | give up after 60s (essential against cold-starting free-tier hosts) |

`-w` understands a set of variables, and the useful ones beyond `%{http_code}` are:

```bash
curl -s -o /dev/null -w "%{http_code} in %{time_total}s\n" "$URL"
curl -s -o /dev/null -w "connect %{time_connect}s  ttfb %{time_starttransfer}s\n" "$URL"
```

`%{time_starttransfer}` (time to first byte) is the one that separates "the server is slow" from
"the network is slow" — a high TTFB with a fast connect means the server is thinking.

### Looping over several endpoints

Checking a whole set at once, formatted so it's readable:

```bash
B=https://api.example.com
for p in /v1/earnings/balance /v1/payouts /v1/admin/payouts; do
  printf "%-34s -> HTTP %s\n" "$p" "$(curl -s -o /dev/null -w '%{http_code}' "$B$p" --max-time 60)"
done
```

Two things worth stealing from that snippet:

- **`printf` with `%-34s`** left-aligns in a 34-character column, so the output lines up into a
  readable table instead of ragged text. `echo` can't do this.
- **`$(...)` command substitution inside the printf argument** runs curl and drops its output
  straight into the string.

Watch the quoting: `-w '%{http_code}'` uses **single** quotes so the shell doesn't try to expand
`{http_code}` as a variable before curl sees it.

### Always run a control

When using status codes to infer something, verify the codes actually discriminate. Hit a route
you *know* doesn't exist and confirm it returns something different:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$B/v1/definitely-not-a-route"   # expect 404
```

Without this you can't tell "404 means not deployed" from "this server returns 404 for
everything." A test with no control isn't evidence. (Applied to verifying deployments in
`learning/09-devops.md` Part 58.)
