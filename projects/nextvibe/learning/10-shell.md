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

---

## Editing source files from a heredoc script (2026-08-21)

Most of this session's edits were applied by piping a Python script into
`python3` from the shell, rather than opening an editor:

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("backend/src/modules/social/likes.service.ts")
s = p.read_text()
assert old in s, "pattern not found"   # fail loudly rather than silently no-op
p.write_text(s.replace(old, new, 1))
PY
```

Reading the pieces:

- `python3 -` — the `-` means *read the program from stdin* instead of from a
  file. Same convention as `cat -`, `tar -f -`.
- `<<'PY' ... PY` — a **heredoc**: everything up to the closing `PY` is fed to
  the command's stdin. `PY` is just a chosen delimiter; any word works.
- The **quotes** around `<<'PY'` are the part that matters. Quoted, the body is
  passed through literally. Unquoted (`<<PY`), the shell first expands `$vars`,
  backticks and `\` escapes *inside* the body — which mangles code containing
  `$` or `\`. **Default to the quoted form** unless you specifically want
  interpolation.

Why this over `sed -i`: `sed` works line-by-line, so multi-line replacements are
awkward, and it silently does nothing when the pattern doesn't match. The
`assert old in s` above turns "my edit didn't apply" into an immediate error
instead of a change you believe happened but didn't.

**The failure this actually caused, worth learning from.** One script inserted
an import after "the last line starting with `import `":

```python
last_import = max(i for i, l in enumerate(lines) if l.startswith("import "))
```

In a file ending with a *multi-line* import, that heuristic picked the opening
`import {` line and inserted the new import between the brace and its members —
a syntax error:

```ts
import {
import { resetAuthRefreshState } from "@/app/provider/api/baseQuery";
  Laptop, Music, ...
} from "lucide-react";
```

Line-oriented edits assume line-oriented structure. When the target is nested
syntax, anchor on something unambiguous (here, the closing `} from "lucide-react";`)
— and run the typechecker afterwards, which is exactly what caught it.

## `grep -ril` — locating files by content (2026-08-21)

```bash
grep -ril "postcard" backend/src frontend --include="*.ts" --include="*.tsx"
```

- `-r` recurse into directories
- `-i` case-insensitive
- `-l` print **only the filenames** with a match, not the matching lines —
  turns grep from "show me the matches" into "show me which files to open"
- `--include=GLOB` restrict to matching filenames; repeatable, which is how both
  `.ts` and `.tsx` are covered above

Pair `-l` with a later `grep -n` on the narrowed set: find the files, then find
the lines. `-n` prints line numbers, and `-A N` / `-B N` print N lines after /
before each match, which is usually faster than opening the file:

```bash
grep -n "model Like" -A 20 backend/prisma/schema/social.prisma
```

## `npx tsc --noEmit` — typecheck without building (2026-08-21)

```bash
npx tsc --noEmit          # uses ./tsconfig.json
npx tsc --noEmit -p backend/tsconfig.json    # -p picks a specific project
```

`--noEmit` runs the full typechecker and writes **no output files** — you get
the errors without a build directory. It's the cheapest possible "did I break
anything" check and the natural thing to run after edits.

Reading its output honestly matters: this run reported errors in
`app.controller.spec.ts` (missing `@types/jest`) and `reminders.service.ts`
(missing `csv-parse`) that had nothing to do with the change in flight. Check
whether a reported file is one you actually touched before assuming you caused
it — and equally, don't wave away errors in files you *did* touch. Filtering
generated noise keeps the real signal visible:

```bash
npx tsc --noEmit 2>&1 | grep -v "^\.next/" | head -30
```

## Reading a video with `ffmpeg` / `ffprobe` (2026-08-21)

Used to diagnose a mobile bug from a screen recording that couldn't be
reproduced locally.

```bash
# What am I dealing with? -v error suppresses the banner, leaving just the data.
ffprobe -v error \
  -show_entries format=duration,size \
  -show_entries stream=width,height,r_frame_rate,codec_name \
  -of default=noprint_wrappers=1 clip.mp4

# Frames at 3/sec, numbered, tiled 6x4 into contact sheets
ffmpeg -i clip.mp4 -vf "fps=3,scale=176:-1,\
drawtext=text='%{n}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,\
tile=6x4" sheet_%d.png
```

- `-vf` is the **video filter chain**; commas separate stages and each feeds the
  next. Order matters — scale before tile, or you tile full-size frames.
- `fps=3` *resamples* to 3 frames per second of video. It isn't playback speed;
  it's how many frames get emitted.
- `scale=176:-1` sets width and lets `-1` compute the height to preserve aspect
  ratio. `-2` instead rounds to an even number, which some codecs require.
- `%{n}` inside `drawtext` is the frame counter — a per-frame expression, not a
  shell variable, which is why it's inside single quotes.
- `sheet_%d.png` — `%d` is filled in by ffmpeg per output file, the same
  convention as `frame_%03d.png` (zero-padded to 3 digits so they sort correctly).

Tiling is the part that does the actual work: 24 frames in one image shows the
*pattern* across an interaction, which is what a bug usually is, rather than any
single moment.

Note `-v error` on both commands. ffmpeg's default output is a wall of build
configuration; suppressing it leaves only what was asked for — worth doing
whenever the output is being read rather than watched.

---

## Part N — `git log -L`: following a function through history (2026-08-22)

While diagnosing the word puzzle scoring bug, the first question was "when did
this function last change?" — not "what does it do now".

```bash
git log --oneline -L 628,690:src/modules/games/games.service.ts
```

`-L <start>,<end>:<file>` follows a **range of lines** through history and shows
only the commits that touched it, each with the diff of just that range. Unlike
`git log -- <file>`, which drowns you in every commit that touched a 1800-line
service, this answers a question about one function.

Git tracks the range as edits above it shift it up and down, so the line numbers
you give are the ones in your *current* working tree.

Two variants worth knowing:

```bash
# By regex instead of line numbers — follows the function even as it moves
git log -L :calculateScore:src/modules/games/games.service.ts

# Suppress the diffs, just list the commits
git log --oneline -L 628,690:src/file.ts -s
```

The `:funcname:file` form is usually what you want — it finds the function by
name and doesn't go stale when you edit the file.

**Why this mattered here:** it proved the scoring function hadn't changed since
an old commit, which redirected the whole investigation away from the code that
looked guilty and toward the data. Cheap question, large saving.

---

## Part N+1 — Heredocs, and the nested-delimiter trap that bit me writing this

The read-only DB diagnostic was written to a file, run once, and removed:

```bash
cat > prisma/_tmp-diagnose.ts <<'SCRIPT'
...typescript...
SCRIPT
npx tsx prisma/_tmp-diagnose.ts 2>&1 | tail -70
rm prisma/_tmp-diagnose.ts
```

**`<<'SCRIPT'` with the delimiter quoted.** Unquoted `<<SCRIPT` makes the shell
expand `$variables` and backticks *inside* the heredoc before writing it, which
mangles any script containing `${...}` template literals. Quoting the delimiter
turns off all expansion and writes the text literally. For anything containing
code, always quote it.

**It lives in `prisma/`, not `/tmp`.** The script imports
`../src/generated/prisma/client` and needs `dotenv/config` to find `.env` — both
resolve relative to where the file sits. A script that depends on a project's
module resolution has to run from inside that project.

The `_tmp-` prefix and the `rm` are the discipline part: a diagnostic that
outlives its diagnosis becomes a file nobody dares delete two years later.

### The trap: a heredoc ends at the *first* line equal to its delimiter

Writing this very section failed the first time. The command was:

```bash
cat >> notes.md <<'EOF'
...prose containing an example that itself used <<'EOF' ... EOF ...
EOF
```

The shell doesn't understand nesting. It scans line by line for the first line
that is exactly the delimiter, and the `EOF` **inside my example** ended the
heredoc early. Everything after it stopped being data and became commands — so
the shell cheerfully ran the `npx tsx` and `rm` lines from my own example text,
and the notes file was left truncated mid-sentence.

Three ways out, in rough order of preference:

```bash
# 1. Pick a delimiter the content cannot contain
cat >> notes.md <<'END_OF_NOTE'
... text that mentions EOF freely ...
END_OF_NOTE

# 2. Write the file from a language with real string literals
python3 - <<'PY'
pathlib.Path('notes.md').write_text(...)
PY

# 3. Indent the body and use <<- (only strips TABS, not spaces — awkward)
```

**The general lesson: a heredoc is not a quoting construct that nests.** The
moment the content is itself shell-flavoured, prefer writing the file from
Python/Node, where a string is a genuine value with an unambiguous end.

The failure mode is nastier than a syntax error, too: instead of refusing to
run, the shell silently reinterprets your data as instructions. Anything
destructive sitting in an example (`rm`, `git reset`) would have executed for
real. Check what actually ran after a heredoc misbehaves.

### Piping to `tail` to survive a wall of output

```bash
npx tsx prisma/_tmp-diagnose.ts 2>&1 | tail -70
```

`2>&1` redirects stderr into stdout **before** the pipe, so errors reach `tail`
too — without it a crash prints to the terminal unpiped while `tail` shows
nothing useful. Order matters here: the redirection has to come before the `|`.

---

## Part N+2 — Reading *parts* of a file: `sed -n` as a surgical `cat` (2026-08-28)

`cat` on a 600-line service file is mostly waste. `sed -n` prints only what you
ask for. The `-n` means "don't auto-print every line"; the `p` command then does
all the printing, so you get exactly the selected range.

**By line number:**

```bash
sed -n '235,420p' src/modules/auth/auth.service.ts   # lines 235–420
sed -n '1,140p'  src/modules/auth/auth.controller.ts # the first 140 (= head -140)
sed -n '268,$p'  DECISIONS.md                        # line 268 to end of file
```

**By pattern range** — far more useful, because you usually know the *name* of
the thing you want, not its line number. An address can be a `/regex/`, and
`start,end` works with regexes on either side:

```bash
# print one method, from its signature to the closing brace at its indent level
sed -n '/private async upsertGoogleUser/,/^  }/p' src/modules/auth/auth.service.ts
```

`/^  }/` is doing real work there: anchored to a closing brace at exactly two
spaces of indentation, i.e. the end of a class method, not the end of every
nested `if` inside it. Pattern ranges end at the **first** match after the start,
so the anchor has to be specific or you get three lines instead of forty.

**Several ranges in one call** — separate commands with `;`:

```bash
sed -n '/private sanitizeUser/,/^  }/p;/private async generateTokens/,/^  }/p' file.ts
```

That pulled three unrelated helper methods out of one file in a single command,
which beats three round trips through `grep -n` and line arithmetic.

The pairing to remember: **`grep -n` to find, `sed -n` to read.** `grep` gives
you the line number or the pattern, `sed -n` gives you the surrounding block.

## Part N+3 — `node -e` to check a behaviour instead of arguing about it (2026-08-28)

Writing the mobile OAuth guide, the question came up: does JS's `URL` parser
handle a custom scheme like `nextvibe://auth?code=abc`, or does it treat it as
opaque and lose the query string? There was a code comment in the repo asserting
one answer and a memory of the spec asserting another.

Rather than pick a side:

```bash
node -e "const u=new URL('nextvibe://auth?code=abc123'); console.log(u.host, u.searchParams.get('code'));"
# → auth abc123
```

`node -e` runs a one-liner and exits. `python3 -c` is the same idea; for anything
multi-line, graduate to the `python3 - << 'PY'` heredoc pattern from the earlier
section.

The habit is the point: **a claim about runtime behaviour is cheap to test and
expensive to get wrong in documentation.** Ten seconds settled it — and it also
surfaced the real caveat worth documenting, which is that Node's answer is *not*
React Native's: RN ships a partial `URL` polyfill with no `searchParams`, so the
same line that works here returns `undefined` on a device. Testing the assumption
is what turned a vague worry into a specific warning worth writing down.

---

## Part N+4 — Swapping a dependency, and the pipe that ate the exit code (2026-09-02)

Replacing `expo-server-sdk` with `firebase-admin` on the backend. Three things
worth keeping from it.

### `pnpm remove` / `pnpm add`

```bash
pnpm remove expo-server-sdk        # drops it from package.json, node_modules AND the lockfile
pnpm add firebase-admin            # the reverse
```

`remove` is the one people skip — deleting the import and leaving the package
installed means the lockfile keeps pinning a dependency nothing uses, and it
still gets downloaded on every CI install.

### The trap: `cmd | tail` throws away `cmd`'s exit code

This actually bit me. The install was run as:

```bash
pnpm remove expo-server-sdk && pnpm add firebase-admin 2>&1 | tail -20
```

`pnpm add` **failed** — npm registry timeouts — and the command still reported
**exit code 0**. Nothing looked wrong until `grep firebase package.json` came
back empty.

The reason: **a pipeline's exit status is the exit status of its **last**
command.** `tail` succeeded at tailing the error output, so the pipeline
succeeded. `pnpm`'s failure was invisible to anything checking `$?`.

Three fixes, depending on what you need:

```bash
set -o pipefail                 # pipeline fails if ANY stage fails — the usual answer
cmd | tail -20; echo "${PIPESTATUS[0]}"   # bash: exit code of the first stage
cmd | tail -20; echo "${pipestatus[1]}"   # zsh: same idea, 1-indexed array
```

In a script, `set -euo pipefail` at the top is the standard opening line and this
is exactly the bug it exists to prevent. Interactively, the lesson is simpler:
**after piping a command's output through anything, verify the effect, not the
exit code.** `grep firebase package.json` was the real check.

### Reading the installed types instead of trusting your memory of an API

`firebase-admin` was at v14, newer than anything I could recall reliably. Rather
than write the send call from memory:

```bash
grep -n "sendEachForMulticast" node_modules/firebase-admin/lib/messaging/messaging.d.ts
grep -n "interface BatchResponse" -A 20 node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
grep -rn "registration-token-not-registered" node_modules/firebase-admin/lib/messaging/*.js
```

This caught two things a from-memory version would have got wrong: the
token-based `MulticastMessage` is **deprecated** in v14 in favour of FIDs, and
the exact error-code strings (which are prefixed `messaging/` only at throw time
— visible in `error.js`, not in the constant list).

**`node_modules` is primary source.** It's the exact version you're compiling
against, which is more than the library's own docs site can say — those describe
whatever version is current. `.d.ts` files for the API surface, the `.js` for
the constants and behaviour the types don't capture.

### `pnpm approve-builds`

```
[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: @firebase/util, protobufjs
```

Not an error. pnpm refuses to run packages' `postinstall` scripts by default —
arbitrary code execution on install is a real supply-chain vector. `pnpm
approve-builds` lets you allow specific ones. Only needed if a package genuinely
requires its postinstall (native compilation, downloading a binary); these two
don't for the messaging path, so it was left alone.

---

## Part N+5 — Inspecting config without printing secrets (2026-09-02)

Question: are the `FIREBASE_*` values in `.env` real yet, or still the
placeholders from `.env.example`? The lazy answer is `cat .env`, which dumps a
private key into the terminal (and into scrollback, and into any transcript).
Better to ask a narrower question:

```bash
val=$(grep -E "^FIREBASE_PROJECT_ID=" .env | cut -d= -f2- | tr -d '"')

if [ -z "$val" ]; then echo "EMPTY"
elif echo "$val" | grep -qi "your-\|xxx"; then echo "still a placeholder"
else echo "set (${#val} chars)"; fi
```

Three things worth keeping:

- **`cut -d= -f2-`** — split on `=`, take field 2 **to the end**. The `-` is the
  point: `-f2` alone would truncate at the first `=` inside the value, which
  base64 and PEM data are full of.
- **`${#var}`** — the *length* of a variable. Reports "is it plausibly a real
  key" without revealing the key. Same family as `${var:-default}` and
  `${var#prefix}`.
- **`grep -q`** — quiet: no output, just an exit status for the `if`. The right
  tool whenever you're testing rather than displaying.

**The habit: when you only need a yes/no about a secret, compute the yes/no.**
Printing the value to read it yourself puts it somewhere you didn't intend.

### `command -v` over `which`

```bash
command -v firebase >/dev/null && firebase --version || echo "not installed"
```

`command -v` is a shell builtin and POSIX; `which` is an external binary that
isn't guaranteed present and whose exit status is inconsistent across systems.
`command -v` is the portable check for "is this on PATH". Redirect to
`/dev/null` when you want only the exit status.
