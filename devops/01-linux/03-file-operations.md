## File Operations & Text Manipulation

This is where the terminal becomes genuinely powerful. On a server there's no GUI — everything is reading, searching, and editing files through the terminal.

---

### Reading files

```bash
cat file.txt          # print entire file
less file.txt         # scroll through file (q to quit)
head file.txt         # first 10 lines
tail file.txt         # last 10 lines
tail -f file.txt      # last 10 lines + follow live updates
```

`tail -f` is critical for DevOps — it's how you watch logs in real time.

---

### Try it on a real log file:

```bash
cat /var/log/syslog | head -20
```

---

### Creating & editing files

```bash
touch file.txt              # create empty file
nano file.txt               # simple terminal editor
vim file.txt                # powerful but steep learning curve
echo "hello" > file.txt     # write to file (overwrites)
echo "hello" >> file.txt    # append to file
```

---

### The `>` and `>>` operators

```bash
echo "line 1" > test.txt     # creates file with "line 1"
echo "line 2" >> test.txt    # adds "line 2" on new line
cat test.txt                 # shows both lines
```

---

Try that sequence and tell me what you see. Then we'll get into `grep`, `find`, and pipes which is where it gets really interesting.

## grep — searching inside files

```bash
grep "word" file.txt              # search for word in file
grep -i "word" file.txt           # case insensitive
grep -r "word" /path/             # search recursively in directory
grep -n "word" file.txt           # show line numbers
grep -v "word" file.txt           # show lines that DON'T match
grep -l "word" /path/             # show only filenames that match
grep -c "word" file.txt           # count matching lines
```

---

Try these on real system files:

```bash
grep "kijuchihe" /etc/passwd
grep -n "Port" /etc/ssh/sshd_config
grep -r "error" /var/log/syslog | head -20
```

---

## Pipes `|`

You've already used pipes. The concept is simple:

**Take the output of one command and feed it as input to the next.**

```bash
cat /etc/passwd | grep "kijuchihe"
ps aux | grep "zen" | grep -v grep
ls /etc | grep "ssh"
```

You can chain as many as you want:
```bash
cat /var/log/syslog | grep "error" | grep -v "apparmor" | head -20
```

---

## find — searching for files

```bash
find /path -name "filename"           # find by name
find /path -name "*.txt"              # find by extension
find /path -type f                    # files only
find /path -type d                    # directories only
find /path -size +100M                # files larger than 100MB
find /path -mtime -7                  # modified in last 7 days
find /path -user kijuchihe            # owned by user
```

---

Run these:

```bash
find /home -name "*.txt"
find / -name "sshd_config" 2>/dev/null
find /var/log -size +1M
```

The `2>/dev/null` on the second one suppresses permission error messages. Tell me what you get.

## Searching a codebase

`grep -r` and `find` as shown above will work — and then drown you in `node_modules/`, `.git/`, and build output. Four flags turn them from "technically recursive" into something you'd actually use on a project:

```bash
grep -rn "pattern" .                          # recursive + line numbers — the default pair
grep -rn "pattern" . --include="*.md"         # only search files matching this glob
grep -rn "pattern" . --exclude-dir=node_modules --exclude-dir=.git
grep -rn "pattern" . --include="*.js" --exclude-dir=dist   # flags stack
```

`--include` takes a **glob**, not a directory, and it's repeatable. `--exclude-dir` is what saves you: a single unfiltered `grep -r` in a JavaScript project spends most of its time inside `node_modules/`.

For `find`, the matching pair is `-path` (matches the whole path, not just the filename) and `-not`:

```bash
find . -name "*.md"                     # matches the FILENAME only
find . -path "*/docs/*.md"              # matches the whole PATH — note the leading */
find . -ipath "*git*"                   # -i prefix = case-insensitive (works on -name too)
find . -name "*.md" -not -path "./node_modules/*"   # exclude a subtree
find . -type f -not -path "./.git/*" -not -path "./node_modules/*"
```

The `-not -path` exclusions must match how the path is *printed* — since `find .` prints `./a/b.md`, the pattern needs the leading `./`. Getting that wrong is the usual reason an exclusion silently does nothing.

### Counting instead of reading

Sometimes you don't want the matches, you want the shape of the data:

```bash
grep -c "pattern" file.md          # matches in ONE file
grep -rc "pattern" *.md            # per-file counts — one "file:count" line each
grep -rl "pattern" . --include="*.md" | wc -l   # how many files match, total
wc -l *.md                         # line counts per file + a total
```

`grep -c` per file is a fast structural audit. In a linked note vault, counting the wikilink marker per file finds orphaned notes — anything reporting `0` links to nothing:

```bash
grep -c "\[\[" git/*.md            # 0 means the note is a dead end
wc -l devops/06-ci-cd/*.md         # is this module thin or fat?
```

### A note on quoting

Always quote the pattern and the glob. Unquoted, the **shell** expands `*` before the command ever sees it:

```bash
grep -rn "pattern" . --include=*.md    # zsh: "no matches found" if no .md in the CWD
grep -rn "pattern" . --include="*.md"  # correct — grep receives the glob itself
```

Bash and zsh differ here — bash silently passes the unmatched pattern through, zsh errors out. Quoting works in both, so just always quote.

## Redirection

You've seen `>` and `>>`. Let's formalize it.

In Linux every process has three standard streams:

| Stream | Number | Meaning |
|---|---|---|
| `stdin` | 0 | input — what goes into a command |
| `stdout` | 1 | output — normal results |
| `stderr` | 2 | errors — error messages |

```bash
command > file.txt        # redirect stdout to file (overwrite)
command >> file.txt       # redirect stdout to file (append)
command 2> error.txt      # redirect stderr to file
command 2>/dev/null       # discard errors entirely
command > file.txt 2>&1   # redirect both stdout and stderr to file
command < file.txt        # feed file as stdin to command
```

---

The `2>/dev/null` you saw earlier in the `find` command now makes sense — `2` is stderr, `/dev/null` is the black hole. Errors go in, nothing comes out.

---

Try these:

```bash
# stdout to file
echo "hello world" > output.txt
cat output.txt

# stderr to null
ls /root 2>/dev/null

# both stdout and stderr to file
ls /root /home > both.txt 2>&1
cat both.txt

# feed file as input
wc -l < /etc/passwd
```

`wc -l` counts lines. Here it counts how many users are in passwd.

Note:
**sed** — Stream EDitor

**awk** — Aho, Weinberger, and Kernighan

Awk is named after its three creators — Alfred **A**ho, Peter **W**einberger, and Brian **K**ernighan. Kernighan is the same guy from K&R C (The C Programming Language book). No deeper meaning — just their initials.

Ready for shell scripting?
