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

## 5. Heredocs — writing whole files from the shell

Adding the Chairman's profile meant appending a ~35-line TypeScript object to
`src/lib/content.ts`. Not a job for `sed`. The tool is a **heredoc**:

```bash
cat >> src/lib/content.ts << 'EOF'

export const chairman = {
  name: 'Josiah "Air" Yoshiyahu II',
  ...
};
EOF
```

Three things are happening on that first line, and each matters.

### `>>` vs `>`

- `>` **truncates** the file to zero bytes, then writes. Get this wrong on a file you
  meant to add to and the old contents are gone, with no undo outside git.
- `>>` **appends** — existing contents stay, new text lands at the end.

The habit worth building: type `>>` by default, and reach for `>` only when you have
consciously decided the old file should cease to exist.

### `<< 'EOF'` vs `<< EOF` — quote the delimiter

The delimiter is the word the shell watches for to know the text has ended. Whether
you quote it changes how the **body** is treated:

| Form | Shell expands `$VAR`, backticks, `\` in the body? |
| --- | --- |
| `<< EOF` | **Yes** |
| `<< 'EOF'` | **No** — every character goes through literally |

Writing code, this is not a stylistic preference. TSX is full of `${...}`; unquoted,
the shell would try to expand `${chairman.name}` as a shell variable, find it empty,
and silently write an empty string into the file.

**Rule: if the heredoc body is code or markdown, quote the delimiter.** Leave it
unquoted only when you specifically *want* shell values interpolated into the output.

### The terminator must be alone on its line — and must not appear in the body

No leading spaces (`<<-` strips leading *tabs* only, not spaces), nothing after it.

I hit the sharper version of this while writing these very notes: the note body
contained a worked example that itself ended with `PY` on its own line, while the
outer heredoc was also delimited by `PY`. The shell doesn't know one is "inside" a
code fence — it is scanning line by line for its terminator. It found the inner one,
ended the heredoc early, and tried to execute the remaining prose as commands:

```
(eval):19: unmatched `
```

An error that names a backtick when the real fault is a delimiter collision several
lines earlier. **When a heredoc body contains heredocs, the outer delimiter must be
something that cannot appear in the text** — `__SCRIPT_EOF__` rather than `EOF`. The
sturdier fix, once a script is more than a few lines: write it to a file first and run
that file, so there is only one level of quoting to reason about.

---

## 6. `python3 - << 'EOF'` — when the edit is too smart for `sed`

Inserting a new JSX section into `about/page.tsx` needed two things: rewrite an import
line, and insert ~75 lines *before* one anchor line. `sed` does the first and is
painful at the second.

```bash
python3 - << 'EOF'
from pathlib import Path
p = Path("src/app/about/page.tsx")
s = p.read_text()

old = 'import { divisions, GROUP } from "@/lib/content";'
assert old in s, "import line not found"
s = s.replace(old, 'import { chairman, divisions, GROUP } from "@/lib/content";')

anchor = "      {/* LEADERSHIP */}"
assert anchor in s, "leadership anchor not found"
s = s.replace(anchor, section + anchor, 1)

p.write_text(s)
EOF
```

- **`python3 -`** — the `-` means "read the program from stdin" rather than from a
  file. With a heredoc, that is a throwaway script leaving nothing on disk.
- **`.read_text()` / `.write_text()`** — read the whole file, transform the string,
  write it back. Fine at this scale; stream line-by-line for a huge file.

### The habit that matters: assert before you write

```python
assert anchor in s, "leadership anchor not found"
```

Without it, a mistyped anchor means `.replace()` matches nothing, returns the string
unchanged, and `write_text()` cheerfully writes the **identical** file back. Exit code
0. Success message printed. Nothing changed. You then spend ten minutes wondering why
the browser doesn't show your new section.

`sed` has precisely the same failure mode and no equivalent guard — that is the real
argument for reaching for Python once an edit has any logic in it. Assert that what
you are matching on exists, *then* mutate.

### `.replace(old, new, 1)` — the count argument

The trailing `1` caps it at one replacement. If `{/* LEADERSHIP */}` ever appeared
twice, an uncapped replace would insert the whole section twice. Bound the count when
you mean "the first one" rather than "all of them".

---

## 7. Inspecting images before you write markup for them

Before adding the logos and carousel photos I needed three facts about each file:
dimensions, real content, and — for the logos — the exact background colour.

### Dimensions without opening an editor

```bash
find public -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) \
  -printf '%8s  %p\n' | sort -k2
```

- `\( ... \)` — grouping in `find`. The backslashes are there because bare
  parentheses are shell syntax; `find` needs to receive them literally.
- `-o` is OR. Without the grouping, `-o` would bind loosely and the `-printf` would
  only apply to the last branch — a classic `find` bug.
- `-printf '%8s  %p'` — size in bytes right-aligned to 8 columns, then path. Cheaper
  and more scriptable than `ls -la` per directory.

### The pixel that decides the CSS

```bash
python3 -c "
from PIL import Image
im = Image.open('public/logos/logo-dark.jpg').convert('RGB')
w, h = im.size
print([im.getpixel(p) for p in [(2,2), (w-3,2), (2,h-3), (w-3,h-3)]])
"
```

Both logos came back exactly `(0,0,0)` and `(255,255,255)` at every corner. That single
fact is what made `mix-blend-mode` the correct fix rather than a hopeful one — see
[[02-frontend]] §12. Had they been `(4,2,6)` or a gradient, blending would have left a
visible ghost rectangle and the answer would have been "go get a transparent PNG".

**The habit:** when a CSS technique depends on an exact colour value, measure it. Do not
infer it from how the image looks.

### `python3 -c` vs `python3 -` (heredoc)

`-c` takes the program as a single argument — good for one-liners. The heredoc form from
§6 is better once the script has more than a couple of lines, because you are not
fighting nested quoting inside a shell string. Note the `"` wrapper above means `$` would
still be expanded by the shell — fine here since there is none, but a reason to prefer
the quoted heredoc as soon as the code gets real.

---

## See also

- [[02-frontend]] — the design-token thinking behind this rename, and why some of
  these substitutions needed hand-fixing afterwards.
