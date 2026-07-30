# Arete DevOps — grep, In Depth

Split out from the original single-file `devops-learning.md`. See also
`04-shell-pipes-and-text-toolkit.md` and `07-regex-from-zero-to-advanced.md`.

---

## Part 5 — grep, In Depth

`grep PATTERN [files]` prints lines matching a pattern. It's the tool I used most on your codebase.

### The flags that matter (ranked by how often you'll use them)

```bash
grep -r  "pattern" src/     # recursive through a directory
grep -n  "pattern" file     # show line numbers        → clickable file:line
grep -i  "pattern" file     # case-insensitive
grep -l  "pattern" src/     # only FILENAMES that match (not the lines)
grep -v  "pattern"          # INVERT — lines that DON'T match (a filter)
grep -c  "pattern" file     # count matching lines
grep -E  "a|b"              # extended regex (see Part 7)
grep -F  "literal.string"   # fixed string, NO regex — fast, safe for special chars
grep -w  "id"               # whole word only (won't match "pillarId")
grep -A5 "pattern"          # show 5 lines After each match
grep -B2 "pattern"          # 2 lines Before
grep -C3 "pattern"          # 3 lines of Context both sides
grep --include="*.ts" -r    # recursive, but only into matching filenames
```

### Real commands from this project, dissected

```bash
# "Is faithBackground actually USED anywhere in the backend?"
grep -rn "faithBackground\|equipmentAccess" backend/src --include="*.ts" \
  | grep -v node_modules | grep -v ".spec" | head -20
```
- `-rn` → recursive + line numbers.
- `"faithBackground\|equipmentAccess"` → OR. In basic grep, alternation is `\|` (escaped). With `-E` it's a clean `|`.
- `--include="*.ts"` → skip .js builds, .json, etc.
- `| grep -v node_modules | grep -v ".spec"` → chained *negative* filters: drop dependency and test noise. Piping grep into grep -v is the everyday way to subtract.
- `| head -20` → cap the output.
- **The result (only 4 hits, all in onboarding) was the finding**: the fields were collected but never used in quest generation. Absence of matches is evidence too.

```bash
# "Which onboarding screens mention faith?" — filenames only:
grep -rn "faithBackground\|equipmentAccess\|faith" mobile/app --include="*.tsx" -l

# "Show me the seed script config inside package.json, with context":
grep -A5 '"scripts"\|"prisma"' package.json | head -20
#     ^ -A5 prints the 5 lines AFTER each match — perfect for JSON blocks

# "Find the message-array boundaries in seed.ts before surgical deletion":
grep -n "LEGACY_MESSAGES_REMOVED\|Seed complete\|existingMessages\|^main()\|^}" prisma/seed.ts
#        ^ anchors: ^main() = lines STARTING with main(), ^} = closing braces at column 0
#        This gave exact line numbers (335, 388) to feed into sed.

# case-insensitive filename hunting:
ls -la backend | grep -i env         # found .env and .env.prod.example
```

### grep pro-habits

- Start broad (`grep -rl`), then narrow (`grep -n` in the specific file). Cheap reconnaissance before reading files.
- `grep -F` when searching for strings full of dots/brackets (`grep -F "toISOString()"`) — no escaping needed.
- Know that modern alternatives exist: `rg` (ripgrep) is grep -r but faster and skips `.gitignore`d files by default. Same flags mostly.

---

