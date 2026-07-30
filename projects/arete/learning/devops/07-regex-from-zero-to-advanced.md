# Arete DevOps — Regex from Zero to Advanced

Split out from the original single-file `devops-learning.md`. See also `05-grep-in-depth.md` and
`08-sed-and-awk.md`.

---

## Part 7 — Regex from Zero to Advanced

### First: globs are NOT regex

```
glob  (shell, find -name):   *.ts        → * = anything, ? = one char
regex (grep, sed):           .*\.ts$     → . = any ONE char, * = repeat previous, \. = literal dot
```

The shell expands unquoted globs **before** the command runs — that's why it's `find . -name "*.ts"` (quoted, so *find* sees the pattern) and why `ls backend/.env*` errored with "no matches found": zsh tried to expand the glob itself, found nothing, and aborted the whole command. Quoting controls *who* interprets the pattern.

### The regex building blocks

```
LITERALS & ESCAPES
  cat        matches "cat" anywhere in the line
  \.  \$ \*  literal . $ *  (backslash disarms special meaning)

ANY & CLASSES
  .          any single character
  [abc]      one of a, b, c
  [a-z0-9]   ranges
  [^abc]     any char EXCEPT a, b, c     ← ^ inside [] = negation
  \d \w \s   digit / word-char / whitespace (PCRE; in grep use [0-9], [[:alnum:]_], [[:space:]])

ANCHORS
  ^          start of line          ^import   → lines starting with import
  $          end of line            ;$        → lines ending with semicolon
  \b         word boundary          \bid\b    → "id" but not "pillarId"

QUANTIFIERS (apply to the preceding item)
  *          0 or more              ab*c   → ac, abc, abbc
  +          1 or more              ab+c   → abc, abbc (not ac)
  ?          0 or 1                 colou?r → color, colour
  {3}        exactly 3              [0-9]{3}
  {2,5}      between 2 and 5
  {2,}       2 or more

GROUPS & ALTERNATION
  (foo|bar)  either word
  (ab)+      repeat a group
  \1         backreference — whatever group 1 matched
```

### The three regex dialects (why your pattern "doesn't work")

| Dialect | Where | `+ ? {} () |` are special? |
|---|---|---|
| **BRE** (basic) | plain `grep`, plain `sed` | No — must escape: `\+ \? \{ \} \( \) \|` |
| **ERE** (extended) | `grep -E`, `sed -E`, `awk` | **Yes** — clean syntax |
| **PCRE** (Perl) | `grep -P`, JS, Python | Yes, plus `\d \w` lookaheads, lazy `*?` |

This is why the project command used `"faithBackground\|equipmentAccess"` with plain grep — BRE needs the escaped `\|`. The modern habit: **just always use `grep -E` / `sed -E`** and write clean patterns.

### Worked examples, increasing difficulty

```bash
# 1. All TODO or FIXME comments:
grep -rEn "TODO|FIXME" src/

# 2. Find hardcoded hex colors in the mobile app:
grep -rEn "#[0-9A-Fa-f]{6}\b" mobile/app --include="*.tsx"

# 3. Console.logs that aren't in comments (start-of-line whitespace only before them):
grep -rEn "^\s*console\.log" src/

# 4. Every NestJS route decorator with its path:
grep -rEn "@(Get|Post|Patch|Delete)\(" backend/src --include="*.controller.ts"

# 5. UUIDs anywhere:
grep -rEn "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" logs/

# 6. Env var assignments but NOT comments (negated class + anchor):
grep -En "^[^#]*DATABASE_URL" .env*
```

### The password-masking sed from this project — full dissection

When I printed your `.env`, the DB password had to be hidden:

```bash
sed 's/:[^:@\/]*@/:***@/' .env
```

```
s/PATTERN/REPLACEMENT/      sed's substitute command
:                           match a literal colon        postgresql://arete : PASSWORD @ localhost
[^:@\/]*                    then any run of characters that are NOT : @ or /
                            └ negated class — this is the password itself.
                              Why negated? So it can't overrun past the @ or
                              match the :// after "postgresql" (the / excludes that)
@                           up to the literal @
→ replaced with  :***@      colon, three stars, at-sign — structure kept, secret gone
```

Result: `postgresql://arete:***@localhost:5432/arete_dev`. One line, no temp files, no editor. This is what sed is for.

---

