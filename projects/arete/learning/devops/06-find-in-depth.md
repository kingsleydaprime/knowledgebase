# Arete DevOps — find, In Depth

Split out from the original single-file `devops-learning.md`. See also `05-grep-in-depth.md`.

---

## Part 6 — find, In Depth

`grep` searches *inside* files; `find` searches for *files themselves* — by name, type, size, age — and can run commands on what it finds.

```bash
find <where> <tests> <actions>
```

### Tests (filters)

```bash
find . -name "*.prisma"          # glob match on filename (quote it! see Part 7 on globs)
find . -iname "readme*"          # case-insensitive name
find . -type f                   # files only
find . -type d                   # directories only
find . -path "*node_modules*"    # match against the whole path
find . -size +1M                 # bigger than 1 MB
find . -mtime -1                 # modified in the last 24h
find . -newer schema.prisma      # modified more recently than that file
```

### Combining tests — AND, OR, NOT (and the parentheses trap)

```bash
# AND is implicit:
find backend -type f -name "*.ts"

# OR is -o — this is from the project:
find backend -name "*.prisma" -o -name "schema*" | grep -v node_modules
#            └── matches either pattern ──┘

# ⚠ THE trap: -o binds looser than implicit AND. This:
find . -name "*.ts" -o -name "*.tsx" -type f
# parses as:  (-name "*.ts")  OR  (-name "*.tsx" AND -type f)   ← not what you meant!
# Fix with escaped parens:
find . \( -name "*.ts" -o -name "*.tsx" \) -type f

# NOT:
find src -type f ! -name "*.spec.ts"

# pruning big directories properly (faster than filtering after):
find . -path ./node_modules -prune -o -type f -name "*.ts" -print
#      └── when path matches, don't descend ──┘            └── needed with -prune
```

### Actions

```bash
find . -name "*.tmp.ts" -delete                      # careful: test with -print first!
find src -name "*.ts" -exec wc -l {} +               # {} = the file(s); + batches them into one wc call
find src -name "*.ts" -exec grep -l "TODO" {} \;     # \; = one command per file (slower)
find . -name "*.log" -print0 | xargs -0 rm           # -print0/-0 = NUL separators, safe for spaces in names
```

**Golden habit:** always run the `find` with plain `-print` (default) first, eyeball the list, *then* add `-delete`/`-exec rm`. Find-with-delete typos are how people erase home directories.

---

