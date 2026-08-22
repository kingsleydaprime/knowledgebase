# Shell — kolade-royal

Commands actually used while working on this project, with what each flag does.

---

## 1. Surveying a codebase before you change it

Before the purple/lilac rebrand I needed to know *where* the old colours were used and
*how often*. Two commands did the whole survey.

### Listing every source file

```bash
find src public -type f | sort
```

- `find <dirs>` — walk those directories recursively.
- `-type f` — only regular files (skip directories themselves).
- `| sort` — alphabetical, so the tree reads predictably.

### Counting how often each colour token appears

```bash
grep -roh -E '\b(ink|parchment2|parchment|brassLight|brass|green|rust|stone)\b' src \
  | sort | uniq -c | sort -rn
```

This is the single most useful "survey" idiom in the shell. Piece by piece:

| flag | meaning |
|---|---|
| `-r` | recursive — search every file under `src` |
| `-o` | print **only the matched text**, not the whole line |
| `-h` | suppress filenames (we only want the words) |
| `-E` | extended regex, so `(a\|b)` and `+` work without backslashes |

`\b` is a **word boundary** — a zero-width position between a word character
(`[A-Za-z0-9_]`) and a non-word character. `\bbrass\b` matches `text-brass"` but *not*
`brassLight`, because after `brass` comes `L`, which is still a word character, so no
boundary exists there. This detail is what made the later rename safe.

Then the classic three-stage count:

```
sort          # group identical lines together (uniq only collapses ADJACENT duplicates)
uniq -c       # collapse runs of identical lines, prefixing each with its count
sort -rn      # sort numerically (-n), reversed (-r) → most frequent first
```

Output was:

```
     32 stone
     21 brassLight
     19 ink
     18 parchment
     16 brass
      3 rust
      2 green
```

Immediately useful: `stone` is the workhorse (borders everywhere), `green` and `rust`
are near-decorative, and `parchment2` appears **zero** times — it was defined in the
Tailwind config but never used. Dead config you'd never notice by reading files one at
a time.

### Counting lines to judge scope

```bash
wc -l src/app/*.tsx src/components/*.tsx src/lib/*.ts
```

`wc` = word count; `-l` = lines only. Total came to 603 lines across 9 files — small
enough to rename tokens by hand-checked `sed` rather than needing anything cleverer.

---

## 2. `sed` — stream editing files in place

`sed` reads text line by line and applies editing commands. The one command you'll use
99% of the time is **substitute**:

```
s/pattern/replacement/flags
```

The full rename:

```bash
sed -E -i \
  -e 's/\bbrassLight\b/lilac/g' \
  -e 's/\bbrass\b/lilac/g' \
  -e 's/\bparchment\b/mist/g' \
  -e 's/\bstone\b/heather/g' \
  -e 's/\bgreen\b/plum/g' \
  -e 's/\brust\b/lilacDeep/g' \
  src/app/page.tsx src/components/Nav.tsx   # ...and the rest
```

| flag | meaning |
|---|---|
| `-E` | extended regex (same as in `grep -E`) |
| `-i` | **in place** — rewrite the file instead of printing to stdout |
| `-e` | "here comes an expression" — lets you chain many substitutions in one pass |
| `g` (trailing) | **global** — replace every match on a line, not just the first |

That `g` matters a lot here: a single `className="..."` line can contain
`border-stone/15` *and* `text-stone` — without `g` only the first would change.

### Three things that will bite you with `sed -i`

1. **`-i` is destructive and there is no undo.** If the project isn't in git yet
   (this one wasn't), you have no safety net. GNU sed lets you keep a backup:
   `sed -i.bak 's/x/y/g' file` writes `file.bak` first. Worth doing when you're not
   sure about a pattern.
2. **Order of expressions matters** when one pattern is a prefix of another.
   `brass` is a prefix of `brassLight`, so a naive `s/brass/lilac/g` run first would
   turn `brassLight` into `lilacLight` — a token that doesn't exist, silently producing
   an unstyled element. Two defences: put the longer pattern first, *and* use `\b`
   so the short pattern can't match inside the long one anyway. Belt and braces.
3. **`sed` doesn't understand your language.** It's pure text. If the word `stone` had
   appeared in the site's prose, it would have been rewritten to `heather` in the
   visible copy. Always verify afterwards (next section) rather than trusting the
   substitution.

### Verifying a bulk edit

Two greps: one that should find everything, one that should find nothing.

```bash
grep -rn -E '\b(lilac|mist|heather|plum|lilacDeep)\b' src | wc -l   # → 68 new tokens
grep -rn -E '\b(brass|parchment|stone|green|rust)\b' src || echo "none"
```

`-n` adds line numbers. The `|| echo "none"` idiom leans on grep's **exit code**: grep
exits `1` when it finds nothing, so `||` (run-if-previous-failed) fires and prints
"none". A clean way to make "no results" an explicit, readable answer rather than
silence.

### Reviewing the result grouped by file

```bash
grep -rn -oE '(bg|text|border|divide)-(ink2|ink|plum|violet|lilac|mist|heather)(/[0-9]+)?' src \
  | awk -F: '{print $1": "$3}'
```

`awk -F:` splits each line on `:` into fields `$1, $2, $3…`. Since `grep -n` outputs
`filename:linenumber:match`, this prints `filename: match` — dropping the line numbers
to make a readable per-file inventory of every colour in the codebase. Handy for a
final eyeball that no element ended up with, say, dark text on a dark background.

---

## 3. Checking whether you're even in a git repo

```bash
git -C . rev-parse --is-inside-work-tree
```

- `-C <dir>` — run git as if started in that directory.
- `rev-parse --is-inside-work-tree` — prints `true`, or errors with
  `fatal: not a git repository` and a non-zero exit code.

This is the scriptable way to ask the question (as opposed to `git status`, which
prints a wall of text). It's how I found out this project had a `.gitignore` but had
never actually been `git init`-ed — the `.gitignore` was doing precisely nothing.

---

## 4. Type-checking without building

```bash
npx tsc --noEmit
```

- `npx` — run a binary from `node_modules/.bin` without installing it globally.
- `tsc` — the TypeScript compiler.
- `--noEmit` — type-check only; don't write any `.js` output.

Fast confidence check after a bulk edit, and it costs nothing. Note what it *can't*
catch: `className="bg-lilac"` is just a string to TypeScript. If `lilac` didn't exist
in the Tailwind config, `tsc` would still say OK and the element would silently render
unstyled. Type-checking proves the code compiles, not that the design is right — for
that you need the browser.

---

## See also

- [[02-frontend]] — the design-token thinking behind this rename, and why some of
  these substitutions needed hand-fixing afterwards.
