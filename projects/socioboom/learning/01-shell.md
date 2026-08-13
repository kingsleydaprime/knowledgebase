# SocioBoom — Shell & Command Line

Commands actually used on this project, with what each flag does — taught in the context
where they came up rather than as an abstract reference.

The general-purpose versions of this material also live in the main vault:
[[devops/01-linux/README|devops/01-linux]] for fundamentals,
[[devops/01-linux/12-bash-scripting|12-bash-scripting]] for scripting,
[[devops/01-linux/16-sed-and-awk|16-sed-and-awk]] for stream editing, and
[[devops/01-linux/15-rhcsa/14-text-processing-and-searching|rhcsa/14-text-processing]] for
grep/find/regex. Read those for depth; read this for how it played out here.

See also [[projects/socioboom/learning/02-git|02-git]] and
[[projects/socioboom/learning/backend/08-devops-and-deployment|backend/08-devops]].

Started 2026-08-11 during the learning-file reorganization and the media pipeline work.

---

## 1. Exploring an Unfamiliar Codebase

```bash
find src prisma -type f | sort
```

`find` walks directories recursively. `-type f` restricts to regular files (excluding
directories, symlinks, sockets). Piping to `sort` gives stable alphabetical output — `find`
returns filesystem order otherwise, which is effectively random and makes two runs
impossible to diff.

```bash
grep -n "^## " backend-learning.md
```

- `-n` prefixes each match with its line number
- `^` anchors to line start

This lists only Markdown H2 headings with line numbers — a table of contents for a file too
big to read. It's what produced the line ranges used for splitting the learning files.

### Proving dead code is actually dead

Three service files existed — `facebook.ts`, `twitter.ts`, `linkedin.ts` — and looked like
the platform publishers. They weren't; the real ones were inline in `worker.ts`.

```bash
grep -rn "postToFacebook\|postToTwitter\|postToLinkedIn" src/
```

- `-r` recurses through directories
- `\|` is alternation in **basic** regex; with `-E` (extended) you'd write plain `|`

Matches appeared **only in the definitions**, never at a call site. That turned "these look
unused" into "these are provably unused," which is what made deleting them safe rather than
a guess.

Worth generalizing: before deleting anything, grep its exported names across the whole
source tree. Only hits are the definitions → it's dead.

---

## 2. Extracting Line Ranges with `sed`

```bash
sed -n '41,241p' source.md >> dest.md
```

`sed` is a stream editor. Two parts matter:

- `-n` suppresses the default "print every line" behavior
- `'41,241p'` selects lines 41–241 and `p` prints them

Without `-n`, the selected lines print **twice** — once from the default behavior, once
from `p`. That's the classic `sed` beginner bug.

`>>` appends; `>` truncates the file first. Getting these backwards silently destroys work.

### The reusable extraction function

```bash
emit() {
  local dest="$1"; shift
  for r in "$@"; do
    sed -n "${r}p" "$SRC" >> "$dest"
    printf '\n' >> "$dest"
  done
}

emit "$OUT/04-auth.md" '700,816' '1603,1734' '2396,2446'
```

- `local` scopes the variable to the function instead of leaking globally
- `"$1"` is the first argument; `shift` discards it so `"$@"` is everything after
- `"$@"` **quoted** preserves each argument as a separate word — unquoted `$*` mashes them
  into one string and breaks on any argument containing a space

This handles non-contiguous ranges, which mattered because thematically related sections
weren't adjacent in the original file.

Note the double quotes in `"${r}p"` — the variable must expand, so single quotes would be
wrong there, even though single quotes are correct for a literal range like `'41,241p'`.

---

## 3. Heredocs, and Why the Quoting Matters

```bash
cat > "$OUT/01-foundations.md" <<'EOF'
# Title with `backticks` and $variables
EOF
```

`<<'EOF'` with the delimiter **quoted** treats the body as literal text. `<<EOF` unquoted
performs expansion — `$VAR` substitutes and backticks execute as command substitution.

Since these headers contained backticks around filenames, the unquoted form would have
tried to *run* `learning/archive/` as a command. Quote the delimiter unless you specifically
want interpolation.

Same idea for embedding another language:

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("src/features/posts/components/PostPreview.tsx")
s = p.read_text()
s = s.replace('media: string[]', 'media: MediaItem[]')
p.write_text(s)
PY
```

The `-` tells Python to read the program from stdin. This is the right tool when a
replacement is too structural for `sed` — multi-line matches, or exact strings full of
regex metacharacters. Several frontend edits needed this because JSX is dense with `{`,
`$`, and backticks, and `str.replace` is literal so none of it needs escaping.

---

## 4. Script Safety

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `-e` exit immediately if any command fails
- `-u` error on referencing an unset variable (catches typos in variable names)
- `-o pipefail` a pipeline fails if **any** stage fails, not just the last one

Without `pipefail`, `false | true` succeeds. Without `-e`, a failing `sed` mid-script keeps
going and produces a half-written file that looks fine. Both matter a lot in a script whose
job is to carve up 4,800 lines of documentation.

`#!/usr/bin/env bash` rather than `#!/bin/bash` finds bash via `PATH`, which matters on
systems where it isn't at `/bin/bash`.

---

## 5. Verifying a Migration Instead of Trusting It

Moving 4,808 lines across 17 files is exactly the kind of operation where something silently
vanishes. Rather than eyeballing it:

```bash
grep -o '^## [0-9]\+\. .*' "$SRC" | while read -r h; do
  n=$(grep -Fxh "$h" "$KB"/backend/*.md | wc -l)
  [ "$n" -eq 1 ] || echo "PROBLEM ($n copies): $h"
done
```

- `grep -o` prints **only the matching part**, not the whole line — so each heading becomes
  a search term
- `while read -r h` reads one line at a time into `$h`; `-r` stops backslashes being
  interpreted as escapes
- `$(...)` is command substitution — captures output as a value
- `grep -Fxh`:
  - `-F` fixed string, not a regex (headings contain `.`, which would otherwise be a
    wildcard)
  - `-x` match the **whole line** exactly, so "## 1. Foo" can't match "## 1. Foo Extended"
  - `-h` suppress filename prefixes, so `wc -l` counts *matches*, not files
- `[ "$n" -eq 1 ] || echo ...` runs the echo only when the test fails

**This caught a real bug.** Section 15 landed in **zero** files — one range ended at 1541
and that section started at 1542. A silent one-section hole in a 2,557-line migration,
found in seconds. Eyeballing would never have caught it.

Then before deleting the originals:

```bash
diff -q "$SRC/backend-learning.md" "$KB/archive/original-flat-backend-learning.md"
```

`-q` reports only *whether* files differ, not how. Proving the archives were byte-identical
turned an irreversible `rm` into a safe one.

**The habit worth keeping:** when a bulk operation is too large to verify by reading, write
the check as code. It takes a minute and converts "probably fine" into "verified."

---

## 6. Small Things

```bash
rmdir "$SRC"          # only removes an EMPTY directory
rm -r "$SRC"          # removes everything inside, no questions
```

`rmdir` failing is *useful information* — it means files you didn't account for are still
in there. Reach for it first; `rm -r` can't tell you that.

```bash
wc -l file            # count lines
grep -c "" file       # also counts lines, including a final unterminated one
grep -vn "^$" file    # print with line numbers, skipping blanks
```

`-v` inverts the match and `^$` matches an empty line — together they strip blanks. Useful
for reading a heavily-spaced config file (like `.env.example`) without scrolling.

**Working directory persists between commands** in a single shell session. After
`cd backend`, a second `cd backend` fails with "no such directory" because you're already
there. This caused a real error during this session. Either use absolute paths or track
where you are.

---

## 7. Project Commands

```bash
# Backend
npx tsc --noEmit          # typecheck without emitting output — the main gate here
npx prisma generate       # regenerate the client after a schema change
npx prisma validate       # check schema syntax without touching the database
npx prisma migrate dev    # apply migrations (needs the DB running)
pnpm dev                  # API server
pnpm dev:worker           # BullMQ worker — separate process, must run for publishing

# Frontend
npx tsc --noEmit
pnpm dev
```

`npx next lint` **no longer exists** — removed in Next 16. It's `npx eslint` now, though
this project's ESLint config currently crashes on load with "Converting circular structure
to JSON," so `tsc --noEmit` is the only working check until that's fixed.

---

## Related
- [[devops/01-linux/README|Linux course]] — the general-purpose version of this material
- [[projects/socioboom/learning/02-git|02-git]] — git on this project
