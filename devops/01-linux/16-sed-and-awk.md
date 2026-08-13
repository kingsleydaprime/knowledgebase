# sed and awk

The two stream processors. `grep` finds lines; `sed` and `awk` *transform* them.

Written 2026-08-11 — `sed` appeared in [[devops/01-linux/linux-reference|linux-reference]]
as lookup material but was never taught in the numbered sequence, and heavy `sed` use
during a documentation migration made the gap obvious.

Assumes [[devops/01-linux/15-rhcsa/14-text-processing-and-searching|text processing]]
(grep, find, regex) and [[devops/01-linux/12-bash-scripting|bash scripting]].

---

## Which tool for which job

| Need | Tool |
|---|---|
| Find lines matching a pattern | `grep` |
| Substitute text, delete lines, extract line ranges | `sed` |
| Work with *columns*, arithmetic, accumulate totals | `awk` |
| Anything needing real data structures | Python |

The honest rule: `sed` for line-oriented edits, `awk` for column-oriented ones, and when
you find yourself writing an `awk` program longer than a few lines, switch to Python.

---

## sed — the stream editor

`sed` reads input line by line, applies commands, and prints the result. It does **not**
modify files unless you tell it to.

### The `-n` flag, and the classic beginner bug

By default `sed` prints every line it reads. The `p` command prints too. So:

```bash
sed '2,4p' file.txt      # ❌ lines 2-4 appear TWICE
sed -n '2,4p' file.txt   # ✅ only lines 2-4
```

`-n` suppresses the automatic printing, leaving `p` as the only source of output. **Almost
every use of `p` wants `-n`.**

### Line ranges — extracting a slice of a file

```bash
sed -n '42p'        file.txt   # just line 42
sed -n '10,20p'     file.txt   # lines 10 through 20
sed -n '100,$p'     file.txt   # line 100 to end of file  ($ = last line)
sed -n '1,/START/p' file.txt   # from line 1 until the first line matching START
```

This is the practical way to carve up a file too large to open. Combined with `grep -n` to
find the boundaries:

```bash
grep -n "^## " big-document.md      # get heading line numbers
sed -n '245,388p' big-document.md   # extract one section
```

That two-step is exactly how a 2,500-line document gets split into chapters. **Watch the
boundaries** — an off-by-one between where one range ends and the next begins silently
drops content. Verify afterwards rather than assuming (see
[[projects/socioboom/learning/01-shell|socioboom/01-shell]] for a worked verification).

### Substitution — the command everyone knows

```bash
sed 's/old/new/'      file.txt   # first occurrence PER LINE
sed 's/old/new/g'     file.txt   # every occurrence (g = global)
sed 's/old/new/2'     file.txt   # only the 2nd occurrence on each line
sed 's/old/new/gi'    file.txt   # global, case-insensitive
```

The delimiter doesn't have to be `/`. When the text contains slashes, switch it — this
avoids a wall of escaping:

```bash
sed 's/\/usr\/local\/bin/\/opt\/bin/g'   # painful
sed 's|/usr/local/bin|/opt/bin|g'        # same thing, readable
```

Any character works after `s`. `|`, `#`, and `,` are common choices.

### Editing files in place

```bash
sed -i        's/old/new/g' file.txt   # GNU: edit in place, no backup
sed -i.bak    's/old/new/g' file.txt   # keep file.txt.bak
sed -i '' -e  's/old/new/g' file.txt   # BSD/macOS: -i REQUIRES an argument
```

**The `-i` portability trap:** GNU sed (Linux) takes an optional suffix attached to the
flag. BSD sed (macOS) *requires* a separate argument. A script using bare `-i` works on
Linux and, on macOS, silently consumes the next argument as the backup suffix. If a script
must run on both, use `perl -pi -e` instead, or test the platform.

Always dry-run first — omit `-i`, check the output, then add it.

### Deleting and selecting lines

```bash
sed '3d'            file.txt   # delete line 3
sed '2,5d'          file.txt   # delete lines 2-5
sed '/^#/d'         file.txt   # delete comment lines
sed '/^$/d'         file.txt   # delete blank lines
sed '/^#/!d'        file.txt   # ! inverts — delete everything EXCEPT comments
sed -n '/BEGIN/,/END/p' f.txt  # print the block between two patterns
```

### Addressing — apply a command only to matching lines

Any command can be prefixed with an address:

```bash
sed '/^server/ s/8080/3000/'  config.txt   # substitute only on lines starting "server"
sed '10,20 s/foo/bar/g'       file.txt     # substitute only within lines 10-20
sed '$ a\Appended last line'  file.txt     # a = append, $ = last line
sed '1 i\Inserted first line' file.txt     # i = insert before
```

### Multiple commands

```bash
sed -e 's/a/b/' -e 's/c/d/' file.txt
sed 's/a/b/; s/c/d/'        file.txt
sed -f script.sed           file.txt   # commands from a file
```

### Capture groups

```bash
echo "John Smith" | sed -E 's/(\w+) (\w+)/\2, \1/'    # → Smith, John
```

`-E` enables extended regex (no backslashes before `(`, `+`, `?`). Without it you need
`\(` and `\)`. **Prefer `-E`** — it matches the regex syntax you already know from
`grep -E` and most programming languages.

`&` in the replacement means "the whole match":

```bash
echo "hello" | sed 's/.*/[&]/'    # → [hello]
```

---

## awk — the column processor

`awk` splits each line into fields and runs a program against them. Where `sed` thinks in
lines, `awk` thinks in **records and fields**.

```bash
awk '{print $1}'        file.txt   # first whitespace-separated field
awk '{print $NF}'       file.txt   # LAST field (NF = number of fields)
awk '{print $1, $3}'    file.txt   # comma inserts a space
awk '{print NR, $0}'    file.txt   # NR = record number, $0 = whole line
```

### Built-in variables

| Variable | Meaning |
|---|---|
| `$0` | The entire line |
| `$1`, `$2`… | Individual fields |
| `NF` | Number of fields on this line |
| `NR` | Current record (line) number |
| `FS` | Input field separator (default: whitespace) |
| `OFS` | Output field separator |

### Changing the separator

```bash
awk -F: '{print $1}' /etc/passwd          # colon-separated → usernames
awk -F, '{print $2}' data.csv             # CSV (naive — breaks on quoted commas)
awk -F'\t' '{print $1}' data.tsv          # tab
```

### Patterns — the real power

The structure is `pattern { action }`. Omit the pattern and it runs on every line; omit
the action and it prints matching lines:

```bash
awk '/error/'                  log.txt   # like grep
awk '$3 > 100'                 data.txt  # rows where field 3 exceeds 100
awk 'NF > 5'                   file.txt  # lines with more than 5 fields
awk 'NR % 2 == 0'              file.txt  # every even line
awk '$1 == "POST" {print $7}'  access.log
```

### BEGIN, END, and accumulation

This is what `sed` fundamentally cannot do — carry state across lines:

```bash
# Sum a column
awk '{sum += $3} END {print sum}' data.txt

# Average
awk '{sum += $1; n++} END {print sum/n}' numbers.txt

# Count occurrences into an associative array
awk '{count[$1]++} END {for (k in count) print k, count[k]}' access.log

# With a header
awk 'BEGIN {print "USER\tSHELL"} -F: {print $1"\t"$7}' /etc/passwd
```

`BEGIN` runs before any input, `END` after all of it.

### Practical one-liners

```bash
# Top 10 IPs hitting a web server
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# Total bytes served (field 10 in combined log format)
awk '{sum += $10} END {print sum/1024/1024 " MB"}' access.log

# Processes using more than 100MB RSS
ps aux | awk '$6 > 100000 {print $11, $6/1024 "MB"}'

# Non-system users (UID >= 1000)
awk -F: '$3 >= 1000 {print $1}' /etc/passwd
```

---

## Combining them

The pipeline idiom: `grep` narrows, `sed` reshapes, `awk` computes.

```bash
grep "ERROR" app.log \
  | sed 's/^\[\([^]]*\)\].*/\1/' \
  | awk '{count[$1]++} END {for (d in count) print d, count[d]}' \
  | sort
```

Read as: find error lines → extract the bracketed timestamp → count per day → sort.

Each stage does one thing. When a stage starts needing conditionals and nested logic, that's
the signal to stop and write a script instead.

---

## Related
- [[devops/01-linux/15-rhcsa/14-text-processing-and-searching|text processing]] — grep, find, sort, uniq, cut
- [[devops/01-linux/12-bash-scripting|bash scripting]] — heredocs, `set -euo pipefail`, functions
- [[devops/01-linux/linux-reference|linux-reference]] — lookup reference

## Seen in the wild
- [[projects/arete/learning/devops/08-sed-and-awk|arete: sed & awk]] — a deeper treatment written against real files
- [[projects/arete/learning/devops/07-regex-from-zero-to-advanced|arete: regex from zero to advanced]] — the regex layer underneath
- [[projects/arete/learning/devops/05-grep-in-depth|grep]] and [[projects/arete/learning/devops/06-find-in-depth|find]] in depth — currently the vault's deepest shell material, and it lives in a project folder
