## Shell Scripting

A shell script is just a file containing commands you'd normally type in the terminal — automated and reusable.

---

### Your first script

```bash
touch hello.sh
nano hello.sh
```

Type this inside:

```bash
#!/bin/bash

echo "Hello, Kingsley"
echo "Today is: $(date)"
echo "You are logged in as: $(whoami)"
echo "Current directory: $(pwd)"
```

Save and exit nano (`Ctrl+X` → `Y` → `Enter`), then:

```bash
chmod +x hello.sh
./hello.sh
```

---

### The shebang `#!/bin/bash`

That first line tells the OS which interpreter to use to run the script. Without it, the OS doesn't know what to do with the file.

| Shebang | Meaning |
|---|---|
| `#!/bin/bash` | run with bash |
| `#!/usr/bin/env python3` | run with python3 |
| `#!/usr/bin/env node` | run with node |

---

### `$()` — command substitution

```bash
echo "Today is: $(date)"
```

`$()` runs a command and inserts its output inline. So `$(date)` gets replaced with the actual date output.

---

```bash
> touch hello.sh
> chmod +x hello.sh
> nano hello.sh
> hello.sh
zsh: command not found: hello.sh
> ./hello.sh
Hello, Kingsley
Today is: Mon 04 May 2026 20:18:27 GMT
You are logged in as: kijuchihe
Current directory: /home/kijuchihe

```

Perfect. Everything worked.

One thing to note — you ran `hello.sh` without `./` first and got "command not found". That's intentional Linux behavior.

When you type a command, the shell only looks in directories listed in your `PATH` environment variable. Your current directory is not in `PATH` by default — for security reasons. So you must explicitly say "run this from here" with `./`.

---

Check your PATH:
```bash
echo $PATH
```

You'll see a list of directories separated by `:`. Those are the only places the shell looks for commands automatically.

---

Now let's make the script actually do something useful. Variables, conditionals, loops — ready?


## Variables

```bash
#!/bin/bash

name="Kingsley"
age=21
greeting="Hello, $name. You are $age years old."

echo $greeting
echo "Name is: $name"
echo "In 10 years you'll be: $((age + 10))"
```

Rules:
- No spaces around `=`
- Access variable with `$`
- Math goes inside `$(())`

---

## Conditionals

```bash
#!/bin/bash

age=21

if [ $age -ge 18 ]; then
    echo "You are an adult"
elif [ $age -ge 13 ]; then
    echo "You are a teenager"
else
    echo "You are a child"
fi
```

### Comparison operators

| Operator | Meaning |
|---|---|
| `-eq` | equal to |
| `-ne` | not equal |
| `-gt` | greater than |
| `-lt` | less than |
| `-ge` | greater than or equal |
| `-le` | less than or equal |
| `=` | string equal |
| `!=` | string not equal |

---

## Loops

```bash
#!/bin/bash

# for loop
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# while loop
count=1
while [ $count -le 5 ]; do
    echo "Count: $count"
    count=$((count + 1))
done
```

```txt
Is there another way to write arrays in bash or are we getting there?
```

We're getting there — but since you asked:

```bash
# define array
names=("Kingsley" "Feyi" "Alice")

# access by index
echo ${names[0]}       # Kingsley
echo ${names[1]}       # Feyi

# all elements
echo ${names[@]}

# length of array
echo ${#names[@]}

# loop through array
for name in "${names[@]}"; do
    echo "Name: $name"
done
```

Key things:
- Arrays use `()` with spaces between elements
- Access elements with `${array[index]}`
- `@` means all elements
- `#` before gives you the length
- Bash arrays are zero-indexed

Perfect. Everything working correctly.

---

## Functions

```bash
#!/bin/bash

# define a function
greet() {
    local name=$1       # $1 = first argument passed in
    local age=$2        # $2 = second argument
    echo "Hello $name, you are $age years old"
}

# call it
greet "Kingsley" 21
greet "Feyi" 20


# function with return value
add() {
    local result=$(($1 + $2))
    echo $result        # in bash you "return" values by echoing them
}

sum=$(add 10 20)        # capture the output
echo "Sum is: $sum"
```

Key things:
- `$1`, `$2`, `$3` — arguments passed to the function
- `local` — keeps variable scoped inside the function only
- Bash functions don't return values like other languages — you echo the result and capture it with `$()`

---

## User Input

```bash
#!/bin/bash

read -p "Enter your name: " name
read -p "Enter your age: " age

echo "Hello $name, you are $age years old"

if [ $age -ge 18 ]; then
    echo "You are an adult"
else
    echo "You are a minor"
fi
```

```txt
It works. So quick one. What if a function can take multiple parameters?
What is the -p flag for?
```

**Multiple parameters** — `$1`, `$2`, `$3`... goes as far as you need. There's also `$@` which means all arguments at once:

```bash
sum_all() {
    local total=0
    for num in "$@"; do
        total=$((total + num))
    done
    echo $total
}

result=$(sum_all 1 2 3 4 5)
echo "Total: $result"
```

`$@` captures everything passed in, no matter how many.

---

**`-p` flag on `read`** — "prompt". It lets you display a message before waiting for input, on the same line.

Without `-p`:
```bash
echo "Enter your name: "
read name
```

With `-p`:
```bash
read -p "Enter your name: " name
```

Same result, cleaner syntax.

Other useful `read` flags:

| Flag | Meaning |
|---|---|
| `-p` | prompt message |
| `-s` | silent — hides input (for passwords) |
| `-t 10` | timeout after 10 seconds |
| `-n 1` | read only 1 character |

## Script Arguments

Just like functions take arguments, scripts themselves can take arguments from the command line.

```bash
#!/bin/bash

echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "All arguments: $@"
echo "Number of arguments: $#"
```

Run it as:
```bash
./script.sh Kingsley 21 Accra
```

---

## Special variables

| Variable | Meaning |
|---|---|
| `$0` | script name |
| `$1`-`$9` | arguments |
| `$@` | all arguments |
| `$#` | number of arguments |
| `$?` | exit code of last command |
| `$$` | PID of current script |
| `$USER` | current user |
| `$HOME` | home directory |
| `$PWD` | current directory |

---

## Exit codes

Every command returns an exit code when it finishes:
- `0` = success
- anything else = failure

```bash
ls /etc
echo $?        # prints 0 — success

ls /fakepath
echo $?        # prints 2 — failed
```

This is how scripts know if something worked:

```bash
#!/bin/bash

if ! mkdir /tmp/testdir; then
    echo "Failed to create directory"
    exit 1
fi

echo "Directory created successfully"
```

---

## Free

The free command shows you your RAM usage — how much memory your system has, how much is being used, and how much is available.

It reads directly from `/proc/meminfo` under the hood.

```bash
cat /proc/meminfo | head -20
```

Run that — you'll see the raw data that `free` reads and formats into a clean table.

```bash
free -h      # human readable (MB, GB)
free -m      # in megabytes
free -g      # in gigabytes
free -s 5    # update every 5 seconds
```

Output columns:

| Column | Meaning |
|---|---|
| `total` | total RAM |
| `used` | currently used |
| `free` | completely unused |
| `shared` | used by tmpfs/shared memory |
| `buff/cache` | kernel using for buffers and cache |
| `available` | what's actually available for new processes |

The important one is `available` not `free` — Linux intentionally uses spare RAM for caching to speed things up. That cache gets released instantly when a process needs it. So `free` being low doesn't mean you're out of memory.

Also `df` while we're at it:

```bash
df -h        # disk usage, human readable
df -h /      # just root partition
df -i        # inode usage instead of space
```

| Column | Meaning |
|---|---|
| `Filesystem` | the device/partition |
| `Size` | total size |
| `Used` | space used |
| `Avail` | space available |
| `Use%` | percentage used |
| `Mounted on` | where it's mounted |

## Colors

```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
```

These are **ANSI escape codes** — special character sequences that terminals interpret as color/formatting instructions rather than printing them literally.

The format is:
```
\033[  style ; color  m
```

| Part | Meaning |
|---|---|
| `\033` | escape character (tells terminal what follows is a code) |
| `[` | start of code |
| `0` or `1` | 0 = normal, 1 = bold |
| `;` | separator |
| `31-37` | color code |
| `m` | end of code |
| `\033[0m` | reset — back to normal color |

### Color codes

| Code | Color |
|---|---|
| `31` | Red |
| `32` | Green |
| `33` | Yellow |
| `34` | Blue |
| `35` | Magenta |
| `36` | Cyan |
| `37` | White |

### Usage
You must use `echo -e` for colors to render — the `-e` flag tells echo to interpret escape sequences:

```bash
echo -e "\033[0;32m Hello \033[0m"   # prints Hello in green
echo -e "${GREEN}Hello${NC}"          # same thing using variables
```

Without `-e` it prints the raw codes as text.


> Check for [sysinfo.sh](./sysinfo.sh)

This was the output of mine

```zsh
> ./sysinfo.sh
================================
       SYSTEM INFORMATION
================================
Basic Info:
Hostname:    kingsley-pc
User:        kijuchihe
Date:        Tue 05 May 2026 08:07:54 GMT
Uptime:      up 52 minutes
CPU:
Model:       Intel(R) Core(TM) i7-4500U CPU @ 1.80GHz
Cores:       4
Load avg:    2.00 2.05 1.94
Memory:
Used: 4.2Gi / Total: 15Gi (Free: 8.7Gi)
Disk:
Used: 190G / Total: 916G (22% used)
Top 5 Processes (CPU):
USER       PID    %CPU   COMMAND
kijuchi+   8076   50.0   ps
kijuchi+   3594   26.4   /opt/zen/zen
kijuchi+   3801   14.8   /opt/zen/zen
kijuchi+   2662   11.4   /usr/bin/gnome-shell
kijuchi+   3496   8.8    /proc/self/exe
Network Interfaces:
lo 127.0.0.1/8
eno1
wlo1 192.168.2.103/24
virbr0 192.168.122.1/24
================================
```

Beautiful. Script worked perfectly.

A few things your system just told you:

**CPU:** i7-4500U — older processor but solid. Load average of ~2.0 on 4 cores means you're at 50% load consistently.

**Memory:** 4.2GB used out of 15GB — much better than yesterday. Zen is behaving.

**Disk:** 190GB used out of 916GB — you have plenty of space.

**Zen is still your heaviest process** — 26% and 14% CPU on two separate processes.

**Network interfaces:**
- `lo` — loopback (127.0.0.1 — your machine talking to itself)
- `eno1` — ethernet (no IP, not connected)
- `wlo1` — WiFi (192.168.2.103 — this is your actual IP on the network)
- `virbr0` — virtual bridge for your VMs (from libvirt you have installed)

---

This is the kind of thing that runs on servers every few minutes and pipes output to a monitoring system.

---

## Script safety — `set -euo pipefail`

Every non-trivial script should start with this. Without it, bash's defaults are dangerous:
a failing command doesn't stop the script, a typo'd variable silently becomes an empty
string, and a broken pipeline reports success.

```bash
#!/usr/bin/env bash
set -euo pipefail
```

| Flag | Long form | What it does |
|---|---|---|
| `-e` | `set -o errexit` | Exit immediately if any command exits non-zero |
| `-u` | `set -o nounset` | Error on referencing an unset variable |
| `-o pipefail` | — | A pipeline fails if **any** stage fails, not just the last |

### Why each one matters

**Without `-e`**, the script keeps going after a failure:

```bash
cd /nonexistent      # fails, prints an error
rm -rf ./*           # RUNS ANYWAY — in whatever directory you were already in
```

That is a genuinely catastrophic pattern and it's bash's default behavior.

**Without `-u`**, a typo becomes silence:

```bash
BACKUP_DIR=/srv/backups
rm -rf "$BACKUP_DIRR/"    # typo → expands to "/" → deletes everything it can reach
```

With `-u`, that's an immediate error instead.

**Without `pipefail`**, only the last command's status counts:

```bash
grep "pattern" missing-file.txt | wc -l
echo $?    # 0 — "success", because wc succeeded, even though grep failed
```

### `#!/usr/bin/env bash` vs `#!/bin/bash`

`env` looks bash up via `PATH`. On systems where bash isn't at `/bin/bash` (notably NixOS,
and macOS where `/bin/bash` is an ancient 3.x), the `env` form finds the right one.

### Escaping `-e` when you expect a failure

Sometimes a non-zero exit is the answer you want:

```bash
set -e
if grep -q "pattern" file.txt; then ...     # fine — grep in a condition doesn't trigger -e
fi

count=$(grep -c "pattern" file.txt || true) # `|| true` swallows the failure deliberately
```

---

## Heredocs — multi-line text into a command

A heredoc feeds a block of literal text to a command's stdin.

```bash
cat > config.yml <<'EOF'
server:
  host: localhost
  port: 3000
EOF
```

The delimiter (`EOF` by convention, but any word works) marks the end. Everything between
goes to the command.

### The quoting rule — this is the part that bites

| Form | Behavior |
|---|---|
| `<<'EOF'` | **Literal.** No expansion of anything. |
| `<<EOF` | **Expanded.** `$VAR` substitutes, backticks execute, `\` escapes. |

```bash
NAME="world"

cat <<EOF
Hello $NAME          # → Hello world
Today is $(date)     # → runs date
EOF

cat <<'EOF'
Hello $NAME          # → Hello $NAME     (literal)
Today is $(date)     # → Today is $(date)
EOF
```

**Default to the quoted form.** Writing a config file, a script, or documentation
containing `$` or backticks with an unquoted heredoc will corrupt it — and worse, backticks
will *execute* whatever is inside them.

### The delimiter must not appear in the body

**The shell ends a heredoc at the first line that is exactly the delimiter** — it has no idea
that line is inside a fenced code block, a comment, or a nested example. So a heredoc that
*documents* heredocs will terminate itself early:

```bash
cat > notes.md <<'EOF'
Writing a file looks like this:

    cat > x.txt <<'EOF'
    hello
    EOF          # ← this line ends the OUTER heredoc

...and everything after here is handed to the shell as commands.
EOF
```

The failure is loud but confusing: the file is written truncated, and the remaining prose is
executed. Prose makes terrible shell — expect `command not found`, or a glob error like
`no matches found: *word*` from a line of markdown containing `*emphasis*`.

**Two habits:**

- **Pick a delimiter that cannot occur in the body.** `MDDOC`, `PYSRC`, `SQLBLOCK` — anything
  but `EOF` when the content might itself contain `EOF`.
- **When a heredoc-heavy command errors, check the tail of what it wrote** (`tail -5 file`).
  The truncation point names the line that closed it.

### `<<-` strips leading tabs

Lets you indent a heredoc inside a function or loop without the indentation ending up in
the output. Note: **tabs only**, not spaces.

```bash
deploy() {
	cat <<-'EOF'
	Starting deploy...
	EOF
}
```

### Embedding another language

The `-` argument tells most interpreters to read the program from stdin:

```bash
python3 - <<'PY'
import json, pathlib
data = json.loads(pathlib.Path("package.json").read_text())
print(data["version"])
PY
```

Useful when a text transformation is too structural for `sed` — Python's `str.replace` is
literal, so strings full of regex metacharacters need no escaping.

### Nested heredocs need different delimiters

A heredoc ends at **the first line equal to its delimiter** — it doesn't understand nesting.
So a script that writes *another* heredoc using the same word terminates early, and the shell
tries to execute the remainder as commands:

```bash
python3 - <<'PY'          # outer
s = """
cat <<'PY'                # inner — SAME word
hello
PY                        # <- ends the OUTER heredoc here. Everything after is shell input
"""
PY
```

The symptom is a baffling `unmatched \`` or `command not found` pointing at a line that looks
fine. **Use distinct delimiters whenever one heredoc contains another** — `PY` inside `OUTEREOF`,
or feed the script via `python3 /dev/stdin <<'OUTEREOF'`.

### Herestrings — a single line

```bash
grep "pattern" <<< "$SOME_VARIABLE"
```

`<<<` passes one string as stdin. Cleaner than `echo "$VAR" | grep`.

---

## One-off scripts across a whole repo

Three techniques that come up whenever you're processing or auditing a directory tree rather
than running a program. Added Aug 2026, from distilling three course transcripts into this
vault — the work that produced [[foundations/programming-fundamentals/README|programming fundamentals]]
and [[devops/00-the-physical-layer/README|the physical layer]].

### `fold` — make a one-line file readable by line-based tools

Machine-generated files — video transcripts, minified JSON, some exports — are frequently
**one enormous line**. Every line-based tool is useless on them: `head -50` prints the whole
file, `sed -n '1,100p'` prints the whole file, `grep -n` reports "line 1" for everything.

```bash
wc -lwc transcript.md
#       0  124714  651107     ← zero newlines, 124k words, 651 KB
```

`fold` inserts line breaks at a fixed width:

```bash
fold -s -w 200 transcript.md > wrapped.txt
```

- `-w 200` — wrap at 200 characters
- `-s` — **break at spaces**, not mid-word. Almost always what you want for prose

Now every line-based tool works, and you can read a huge file in controlled chunks:

```bash
wc -l wrapped.txt          # 3299
sed -n '1,140p' wrapped.txt      # first chunk
sed -n '141,280p' wrapped.txt    # next chunk
```

**Why chunk at all rather than `cat`:** anything with an output limit — a pager, a log, a tool
window — truncates a 650 KB dump. Fixed line ranges give you a cursor you can advance
deliberately, and `grep -n` on the wrapped file gives you real line numbers to jump to.

The reverse (`fmt`, or `tr -d '\n'`) puts it back if you need the original shape.

### Guard a scripted rewrite with an assertion

When rewriting files programmatically, the dangerous failure is not a crash — it's a
**silent no-op**. `str.replace` on a string that isn't there returns the original, and the
script writes the file back unchanged and exits 0. You believe the edit landed. It didn't.

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("README.md")
s = p.read_text()

old = "the exact text I expect to find"
assert old in s, "anchor not found — file changed since I last looked"   # ← the guard

s = s.replace(old, "the replacement")
p.write_text(s)
PY
```

**The `assert` converts a silent wrong result into a loud failure**, which is the same instinct
as ECC memory and checksums: you cannot fix what you were never told about. Cheap, one line,
and it catches the case where a file drifted between when you read it and when you edited it.

`sed -i` has the identical hazard with no equivalent guard — it exits 0 whether or not the
pattern matched. If the edit matters, check afterwards:

```bash
sed -i 's/old/new/' file.md
grep -c "new" file.md          # verify it actually landed
```

### A verification pass over the whole tree

The useful habit after any bulk edit: **write a throwaway script that checks the invariant you
care about.** It takes two minutes and finds what reading cannot.

For a wiki-linked vault, the invariant is "every `[[link]]` points at a file that exists":

```bash
python3 - <<'PY'
import re, pathlib
root = pathlib.Path(".")

SKIP = ("quartz", "node_modules", "sources")
notes = [p for p in root.rglob("*.md") if p.parts[0] not in SKIP]

# Obsidian resolves BOTH forms, so both count as valid:
#   full path   [[devops/01-linux/12-bash-scripting]]
#   short form  [[12-bash-scripting]]        <- resolved by filename alone
valid = {str(p.with_suffix("")) for p in notes} | {p.stem for p in notes}

bad = []
for p in notes:
    text = re.sub(r"```.*?```", "", p.read_text(), flags=re.S)   # ignore code blocks
    for m in re.finditer(r"\[\[([^\]\|\\]+)", text):
        target = m.group(1).strip()
        if target not in valid:
            bad.append((str(p), target))

print(f"{len(bad)} broken")
for f, t in bad:
    print(" ", f, "->", t)
PY
```

**Accepting both link forms is the part that matters**, and getting it wrong is instructive.
The strict version — full paths only — reports **2,032 "broken" links in this vault**, every
one of them fine, because the vault uses short-form links throughout. A checker with a
false-positive rate like that gets ignored within a day, which makes it *worse* than no
checker: it turns a real signal into noise you've trained yourself to skip. Same failure mode
as a noisy alert → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

Tune it until a clean run means something, then trust it.

Three things worth stealing from the shape regardless of what you're checking:

- **Build the set of valid things first, then test against it.** One pass to collect, one to
  check — far faster and clearer than re-scanning for every reference
- **Strip what shouldn't be scanned** before matching. Here it's fenced code blocks, which
  otherwise report a Python list literal `[[1, 2, 3]]` as a broken link
- **Print what failed, not just how many.** A count tells you there's a problem; the list is
  the fix

Same pattern, other invariants worth checking after a bulk edit:

```bash
# unclosed code fences — an odd number of ``` in a file
# (find, not **/*.md — globstar is on by default in zsh but NOT in bash)
find . -name "*.md" -not -path "./quartz/*" | while read -r f; do
  n=$(grep -c '^```' "$f")
  [ $((n % 2)) -ne 0 ] && echo "UNCLOSED: $f ($n)"
done

# reconcile a claimed count against reality before publishing it
find . -name "*.md" -not -path "./quartz/*" | wc -l
cat foundations/programming-fundamentals/*.md | wc -w
```

**That last one is the point of the whole section.** Any number written into a README — note
counts, word counts, "12 notes" — is a claim that rots. Deriving it from the filesystem takes
one command and stops the document lying.

## Flags for scripts that touch production data

A one-off script that reads an API is harmless. A one-off script that **deletes, patches or
overwrites real records** is a different object, and it earns a small, fixed set of conventions.

### `--dry-run`, and which name is the safe one

Parsing is as simple as it looks, and for one or two booleans that is correct — no `getopts`,
no dependency:

```bash
DRY_RUN=false
[[ " $* " == *" --dry-run "* ]] && DRY_RUN=true
```

```js
const dryRun = process.argv.includes("--dry-run");   // the same thing in a node/bun script
```

**The important decision isn't the parsing — it's which invocation is short.** Wire the wrappers
so the obvious, tab-completable name is the *preview*:

```json
"cleanup":       "bun run scripts/cleanup.js --dry-run",
"cleanup:apply": "bun run scripts/cleanup.js"
```

> **The default must be safe, and the destructive path must be the one you go out of your way to
> ask for.** The reverse — `cleanup` deletes, `cleanup:dry` previews — is the same functionality
> one accidental tab-completion away from an incident.

The residual risk with `includes("--dry-run")` is that a typo (`--dryrun`) silently means *apply*.
Where the stakes justify it, invert the flag: **dry-run unconditionally, require an explicit
`--apply`.** Then a typo fails safe.

### Print the change before making it — in both modes

```js
console.log(`  ${id}\n    Before: ${before}\n    After:  ${after}`);
if (!dryRun) await write(id, after);
```

Identical output either way, so the preview is faithful and the real run leaves a transcript.
**A dry run that takes a different code path is a dry run that lies to you.**

### The rest of the set

| Flag | Job |
|---|---|
| `--dry-run` | preview; the default |
| `--force` | ignore the "already done" skip, for when the transform itself changed |
| `--retry` | re-run only what failed last time, read back from the run report |
| `--debug` | fetch **one** record, dump its actual shape, exit — before you trust the docs |
| `--limit N` | process the first N, to sanity-check on real data at low cost |

`--debug` is the underrated one. Building "show me what this API really returns" into the script
means it's still there the next time the shape surprises you, instead of being retyped into a REPL.

### Structure

1. **A header comment: what this fixes, why it exists, and how to run it.** A repair script is a
   response to a specific incident; without the incident written down it is unreadable *and*
   undeletable, because nobody can tell whether it is still needed.
2. **Assert config at the top** — fail on a missing env var before doing any work, not halfway
   through.
3. **A query/filter that defines the work set as narrowly as possible.** *Safety lives in the
   selection, not in the loop* — a loop cannot damage what was never fetched.
4. **Exit early and say so** when there's nothing to do.
5. **Deterministic choices.** If the script picks a survivor among duplicates, the rule must give
   the same answer twice, or the dry run told you nothing.
6. **Write a structured report**, even on success.

### The `.env` foot-gun

Runtimes that auto-load `.env` (bun, and node with `--env-file`) make it invisible **which
environment a destructive script is about to hit** — it's decided by which lines happen to be
commented out in a file you aren't looking at. Name the target in the command:

```bash
bun --env-file=.env.migration run scripts/cleanup.js --dry-run
dotenv -e .env.staging -- node scripts/cleanup.js
```

**Anything that decides between staging and production should be visible in your shell history.**

## Related
- [[devops/01-linux/16-sed-and-awk|sed and awk]] — when the transformation is line-shaped
- [[devops/01-linux/03-file-operations|file operations]] — `find`, `grep -r`, and the search flags
- [[git/09-investigating-history|investigating history]] — the git equivalent of a verification pass
- [[concepts/04-best-practices/06-data-migrations|data migrations]] — where the dry-run/apply conventions above come from
- [[projects/munakalati/learning/02-shell|munakalati — shell]] — these techniques against a real codebase
