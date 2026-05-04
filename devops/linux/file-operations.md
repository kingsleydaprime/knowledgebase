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
