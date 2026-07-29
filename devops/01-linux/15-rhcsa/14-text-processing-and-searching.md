# Text Processing & Searching — grep, find, wc, and friends

> RHCSA V10

Part of [[README|RHCSA V10]] — the depth-and-examples layer behind "Improving Command Line Productivity Using Shell Scripts" and "Manage files from the Command Line." The base syntax for these tools already exists in [[devops/01-linux/linux-reference|Linux Reference]] (§6 text processing, §20.1 find) and [[devops/01-linux/03-file-operations|File Operations & Text Manipulation]] — this note is the exam-drill version: more examples, more combining-tools-into-pipelines, because that's exactly the shape RHCSA tasks take ("find every file matching X, then do Y to it").

These are also, not coincidentally, the exact commands I lean on constantly while working in this repo — `grep` to locate a section across files, `wc -l` to size up a file before reading it, `find` to locate something by name or type. Muscle memory here pays off far beyond the exam.

---

## cat, tac, nl — reading files with more control

```bash
cat file.txt              # print entire file
cat -n file.txt            # print with line numbers — useful for "edit line 47" type tasks
cat -A file.txt             # show non-printing characters ($ for end of line, ^I for tab) — catches hidden whitespace bugs
tac file.txt                # cat backwards, last line first
nl file.txt                  # like cat -n but with more numbering control (nl -ba to number blank lines too)
cat file1.txt file2.txt > combined.txt      # concatenate multiple files into one
cat file1.txt file2.txt | wc -l              # combined line count without creating an intermediate file
```

---

## wc — counting

```bash
wc -l file.txt          # lines
wc -w file.txt           # words
wc -c file.txt           # bytes
wc -m file.txt           # characters (differs from -c with multi-byte/unicode content)
wc -L file.txt           # length of the longest line
wc file.txt              # all four of lines/words/bytes/filename at once, in that order
```

Where `wc` earns its keep is piped onto the output of something else, as a counting step in a bigger pipeline:

```bash
cat /etc/passwd | wc -l               # how many user accounts exist total
grep -c "nologin" /etc/passwd          # how many accounts CAN'T log in interactively — grep -c is a shortcut for `grep | wc -l`
ls /etc/systemd/system/*.service | wc -l    # how many custom service unit files exist
find /home -type f | wc -l              # how many regular files exist under /home, recursively
ps aux | wc -l                          # rough process count (off by one for the header line — grep -c avoids that)
```

`grep -c` vs `grep | wc -l`: they're usually equivalent, but `grep -c` counts *matching lines*, while `wc -l` after a `grep` with multiple matches per line (rare, but `-o` output mode produces one match per output line, changing the count) can diverge. Default to `grep -c` when just counting matching lines — it's one process instead of two.

---

## grep — the single most-used command on the exam

```bash
grep "pattern" file.txt              # basic search
grep -i "pattern" file.txt            # case-insensitive
grep -v "pattern" file.txt            # INVERT — show lines that DON'T match (extremely common: "everything except comments")
grep -n "pattern" file.txt            # show line numbers
grep -c "pattern" file.txt            # count matching lines instead of printing them
grep -r "pattern" /path/               # recursive through a directory tree
grep -l "pattern" /path/*.conf        # print only FILENAMES that contain a match (not the matching lines)
grep -L "pattern" /path/*.conf        # inverse of -l — filenames that DON'T contain a match
grep -A3 "pattern" file.txt            # show 3 lines of context AFTER each match
grep -B3 "pattern" file.txt            # 3 lines BEFORE each match
grep -C3 "pattern" file.txt            # 3 lines of context on BOTH sides
grep -w "pattern" file.txt             # match whole word only — "cat" won't match inside "category"
grep -x "pattern" file.txt             # match the WHOLE LINE exactly, not just a substring anywhere in it
```

### Regex flavors: BRE vs. ERE

Plain `grep` uses **Basic Regular Expressions (BRE)**, where some metacharacters need escaping. `grep -E` (equivalent to the older `egrep`) uses **Extended Regular Expressions (ERE)**, which is the more intuitive/modern syntax most people already know from other languages.

```bash
grep 'user\+' file.txt         # BRE: + needs a backslash to mean "one or more"
grep -E 'user+' file.txt        # ERE: + works unescaped

grep 'foo\|bar' file.txt        # BRE: alternation needs escaping
grep -E 'foo|bar' file.txt       # ERE: unescaped

grep -E '^(root|kingsley):' /etc/passwd     # alternation + anchor combined — lines starting with either username
```

| Metacharacter | Meaning | BRE | ERE (`grep -E`) |
|---|---|---|---|
| `.` | any single character | works unescaped | works unescaped |
| `*` | zero or more of the previous | works unescaped | works unescaped |
| `+` | one or more of the previous | `\+` | `+` |
| `?` | zero or one of the previous | `\?` | `?` |
| `\|` | alternation (OR) | `\|` | `\|` |
| `()` | grouping | `\(...\)` | `(...)` |
| `^` | start of line | works unescaped | works unescaped |
| `$` | end of line | works unescaped | works unescaped |
| `[...]` | character class | works unescaped | works unescaped |

Default to `grep -E` unless there's a specific reason not to — it removes an entire category of "why isn't my regex matching" mistakes caused by forgetting a backslash.

### Character classes and anchors — the regex you actually need for the exam

```bash
grep '^root' /etc/passwd                # lines STARTING with "root"
grep 'bash$' /etc/passwd                 # lines ENDING with "bash" — finds every user with bash as their shell
grep -E '^[0-9]' file.txt                 # lines starting with a digit
grep -E '[A-Z]' file.txt                  # lines containing at least one uppercase letter
grep -E '^[^#]' /etc/fstab                 # lines that DON'T start with # — the classic "strip comments" pattern
grep -E '^\s*$' file.txt -v                # -v + blank-line pattern = strip blank lines too
grep -E '^[^#]' /etc/fstab | grep -v '^\s*$'   # combined: real, non-comment, non-blank config lines only
```

### Practical exam-style pipelines

```bash
# Every account with an interactive shell (not a service account)
grep -E '/(bash|zsh|sh)$' /etc/passwd

# Every UID in the "human user" range (typically 1000+)
awk -F: '$3 >= 1000 {print $1, $3}' /etc/passwd

# Count failed SSH login attempts today
grep "Failed password" /var/log/secure | wc -l

# Find the line number of a specific setting in a config file, to jump straight to it in an editor
grep -n "^Port" /etc/ssh/sshd_config

# Confirm a kernel parameter took effect after a boot-time edit (see control-the-boot-process.md)
grep -o 'rd.break' /proc/cmdline

# Every currently-mounted filesystem of type xfs
grep xfs /proc/mounts
```

---

## find — locating files by any criteria

```bash
find /path -name "filename"           # exact name match
find /path -iname "filename"           # case-insensitive name match
find /path -name "*.conf"              # by extension/glob pattern
find /path -type f                     # regular files only
find /path -type d                     # directories only
find /path -type l                     # symlinks only — see devops/linux/symbolic-links
find /path -user kingsley               # owned by a specific user
find /path -group developers            # owned by a specific group
find /path -perm 644                    # exact permission match
find /path -perm -644                   # AT LEAST these permissions (others may be set too)
find /path -size +100M                  # larger than 100MB
find /path -size -1k                    # smaller than 1KB
find /path -mtime -7                    # modified within the last 7 days
find /path -mtime +30                   # modified MORE than 30 days ago
find /path -empty                       # empty files or directories
find /path -maxdepth 1                  # don't recurse past the top level — treat like `ls`, not a full tree walk
```

### Combining conditions

```bash
find /var/log -name "*.log" -size +10M                  # AND is implicit between conditions
find /home -type f \( -name "*.tmp" -o -name "*.bak" \)  # OR needs explicit grouping and -o
find / -type f -not -path "/proc/*" -name "core"          # exclude a path from the search entirely
```

### Acting on results — the actual reason find matters on the exam

```bash
find /tmp -name "*.tmp" -delete                    # delete every match directly — no confirmation, be sure of the pattern first
find /home -name "*.log" -exec rm {} \;              # -exec runs a command once PER match, {} is replaced with the filename
find /home -name "*.log" -exec rm {} +                # same idea but batches matches into fewer command invocations — faster on huge result sets
find /var/log -name "*.log" -mtime +30 -exec gzip {} \;   # compress every log older than 30 days
find / -perm -4000 -type f 2>/dev/null                # find every SUID binary on the system — a real security-audit task
find /etc -name "*.conf" | xargs grep -l "listen"      # pipe results into xargs to feed them to another command in bulk
```

`-exec ... \;` vs `-exec ... +`: the `\;` form runs the command separately for every single match (slow, but safe if the command can only take one argument at a time); the `+` form batches as many matches as possible into fewer invocations (faster, but the command must accept multiple arguments — `rm` does, some commands don't).

### find + xargs — the classic combo

```bash
find /home -name "*.txt" | xargs grep -l "password"     # search inside every .txt file found for a string
find /var/log -name "*.log" -mtime +90 | xargs rm -v     # bulk-delete with verbose output, one command instead of a loop
find . -name "*.sh" -print0 | xargs -0 chmod +x           # -print0 / -0 pairing: NUL-separated instead of newline-separated, so filenames with spaces don't break the pipeline
```

That `-print0` / `xargs -0` pairing is worth remembering specifically — a plain `find | xargs` pipeline silently breaks on any filename containing a space, and that's exactly the kind of edge case an exam scenario file is likely to contain on purpose.

---

## sort, uniq, cut — shaping output

```bash
sort file.txt                    # alphabetical
sort -n file.txt                  # numeric (alphabetical sort puts "10" before "9" — -n fixes that)
sort -r file.txt                  # reverse
sort -k2 file.txt                 # sort by the 2nd whitespace-delimited field
sort -t: -k3 -n /etc/passwd        # sort /etc/passwd by UID (field 3, colon-delimited, numeric)
sort -u file.txt                  # sort AND deduplicate in one step

uniq file.txt                     # remove ADJACENT duplicate lines — almost always used after sort first
sort file.txt | uniq              # the real, reliable way to dedupe (uniq alone only catches ADJACENT dupes)
sort file.txt | uniq -c            # count occurrences of each unique line
sort file.txt | uniq -c | sort -rn # the classic "top N most frequent lines" pipeline

cut -d: -f1 /etc/passwd            # colon-delimited, field 1 — extract just usernames
cut -d: -f1,3 /etc/passwd          # multiple fields
cut -c1-10 file.txt                 # by CHARACTER position instead of a delimiter
```

### A complete worked pipeline

"Which 5 IPs hit this server the most, based on the access log?"
```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -5
```
Read left to right: pull the first field (the IP) out of every line → sort so identical IPs are adjacent → count consecutive duplicates → sort those counts numerically, descending → take the top 5. This exact shape — extract, sort, count, sort again, limit — is the backbone of a huge fraction of real text-processing tasks, on the exam and off it.

---

## Quick reference: which tool for which job

| I need to... | Reach for |
|---|---|
| Find lines matching a pattern | `grep` |
| Find files matching a name/type/size/date | `find` |
| Count lines/words/files | `wc -l`, or `grep -c`, or `find \| wc -l` |
| Extract a specific column from delimited text | `cut` or `awk '{print $N}'` |
| Remove duplicate lines | `sort \| uniq` |
| Run a command against many found files at once | `find ... -exec` or `find ... \| xargs` |
| Do all of the above chained together | a pipe (`\|`) — see [[devops/01-linux/linux-reference|Linux Reference]] §6 for pipe fundamentals |
