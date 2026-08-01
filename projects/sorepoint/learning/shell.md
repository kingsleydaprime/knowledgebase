# Shell — Sorepoint

Command-line techniques used on this project, with the *why*. Newest topics added
as they come up.

---

## Checking whether a product/package name is taken

When naming Sorepoint we needed to know if candidate names were free. Two cheap
checks from the terminal, no browser needed for the first one.

### 1. Is the npm package name free? — `npm view`

```bash
npm view sorepoint name
```

`npm view <pkg> <field>` (aliases: `npm info`, `npm show`) asks the npm registry
for a package's metadata **without installing anything**. Ask for one field
(`name`, `version`, `description`) to keep output tiny.

- If the package **exists**, it prints that field.
- If it **doesn't exist**, npm exits with an error containing the phrase
  `is not in this registry` (a 404).

So we can turn that into a FREE/TAKEN flag by grepping for the error text:

```bash
npm view sorepoint name 2>&1 | grep -q 'is not in' && echo FREE || echo TAKEN
```

Piece by piece:
- `2>&1` — redirect **stderr into stdout** so the pipe sees the error text too
  (npm prints errors to stderr; without this, `grep` would never see them).
- `grep -q 'is not in'` — `-q` = *quiet*: print nothing, just exit `0` if the
  pattern is found (name is free) or `1` if not (name exists).
- `A && B || C` — shell short-circuit: run `B` if `A` succeeded, else `C`. Here:
  found the "not in registry" error → `echo FREE`, otherwise → `echo TAKEN`.
  (Careful with this idiom in general: if `B` itself fails, `C` still runs. Fine
  here because `echo` never fails.)

### 2. Check a whole list at once — a `for` loop

```bash
for n in sorepoint triagely firstfix onepitch weakspot; do
  printf "%-12s " "$n"
  npm view "$n" name 2>&1 | grep -q 'is not in' && echo FREE || echo TAKEN
done
```

- `for n in a b c; do … done` — loop over a literal list, `$n` is each item.
- `printf "%-12s " "$n"` — print the name **left-justified in a 12-char column**
  (`-` = left-justify, `12` = width, `s` = string) so the FREE/TAKEN column lines
  up in a neat table. `printf` is better than `echo` here because it doesn't add a
  newline, letting the loop body finish the line.

### 3. npm-free is necessary but NOT sufficient

A free npm name only means *no npm package*. A name can still be owned by a real
company (trademark, .com, existing SaaS). So we paired every npm check with a web
search — that's how `kerbside` (npm-free) was ruled out: there's already a
"Kerbside" booking-software product. Registry check = cheap first filter; web
search = the real clearance.

---

## Scaffolding into a non-empty repo — moving files aside with `mv`

`create-next-app` refuses to run in a directory that already contains
non-standard files: it only tolerates a small allow-list (`.git`, `.gitignore`,
`LICENSE`, a few IDE/config files). Our repo already had `file.md` and `docs/`,
so the generator would have bailed with *"the directory contains files that
could conflict."*

Rather than scaffold into a throwaway subfolder and merge hidden files back by
hand, the cleaner move is: **park the conflicting files, scaffold in place, put
them back.**

```bash
mv file.md docs "$SCRATCH"/
```

- `mv a b c dest/` — `mv` takes **many sources and one final destination**. When
  the last argument is a directory, every preceding argument is moved *into* it.
  So this moves both `file.md` and the `docs/` folder into `$SCRATCH`.
- Order matters: the **last** path is always the destination. `mv a b` renames
  `a`→`b`; `mv a b dir/` moves both into `dir/`. The trailing `/` is a habit that
  makes intent obvious and makes `mv` error loudly if `dir` isn't actually a
  directory (safer than silently renaming).

### Why plain `mv`, not `git mv`

`git mv` looks like a file operation but is really a **git** operation — it
stages the rename in the index. For temporary plumbing like this (move out, move
back, net-zero change) we deliberately use plain `mv` so git's index is never
touched. Afterward `git status` just shows the files as working-tree deletions:

```bash
git status --short
#  D docs/PLAN.md
#  D docs/SPEC.md
#  D file.md
```

The leading space + `D` means **deleted in the working tree but not staged** —
git's first column is the *staged* (index) status, the second is the
*working-tree* status. Since we move the files right back before anything is
committed, this reverses to a clean tree with no history churn.
