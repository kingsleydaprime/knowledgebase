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
