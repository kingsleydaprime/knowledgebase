## Navigating the Filesystem

The commands you'll use every single day. Let's go hands-on.

---

### Where am I?

```bash
pwd
```
"Print Working Directory" — tells you exactly where you are.

---

### Moving around

```bash
cd /etc          # go to /etc
cd ~             # go to your home directory
cd ..            # go up one level
cd -             # go back to where you just were
```

---

### Listing files

```bash
ls               # basic list
ls -l            # detailed list (permissions, size, owner, date)
ls -a            # show hidden files (files starting with .)
ls -la           # both combined — you'll use this constantly
```

---

Try this sequence:

```bash
pwd
cd /etc
ls -la
cd ~
pwd
```

Tell me what you see from `ls -la` inside `/etc` — specifically the first column of characters on the left side of each line. 

That's going to lead us straight into **file permissions** — one of the most important Linux concepts.

> Now I tried this:

```sh
ls -la | head -20
total 6372
drwxr-xr-x 173 root                 root                   12288 May  2 19:03 .
drwxr-xr-x  23 root                 root                    4096 Mar 16  2025 ..
-rw-r--r--   1 root                 root                    3444 Jul  5  2023 adduser.conf
-rw-r--r--   1 root                 root                    3028 Sep 11  2024 adduser.conf.update-old
drwxr-xr-x   3 root                 root                    4096 Sep 11  2024 alsa
drwxr-xr-x   2 root                 root                   20480 Apr  5 08:37 alternatives
-rw-r--r--   1 root                 root                     335 Mar 23  2022 anacrontab
drwxr-xr-x   8 root                 root                    4096 Mar 19 23:06 apache2
-rw-r--r--   1 root                 root                     433 Mar 23  2022 apg.conf
drwxr-xr-x   5 root                 root                    4096 Sep 11  2024 apm
drwxr-xr-x   2 root                 root                    4096 Apr 14 13:48 apparmor
drwxr-xr-x  10 root                 root                   12288 Apr 23 10:41 apparmor.d
drwxr-xr-x   4 root                 root                    4096 Sep  8  2025 apport
drwxr-xr-x   8 root                 root                    4096 Mar 16  2025 apt
drwxr-xr-x   2 root                 root                    4096 Apr  4 18:25 ardour8
drwxr-xr-x   3 root                 root                    4096 Jan 29 14:59 avahi
-rw-r--r--   1 root                 root                  536804 Apr  1  2024 avrdude.conf
-rw-r--r--   1 root                 root                    2319 Jan  6  2022 bash.bashrc
-rw-r--r--   1 root                 root                      45 Nov 11  2021 bash_completion
```

Perfect. Let's decode that first column.

Take this line:
```
drwxr-xr-x   3 root root   4096 Sep 11  2024 alsa
```

That `drwxr-xr-x` — break it into parts:

```
d  rwx  r-x  r-x
│   │    │    │
│   │    │    └── others (everyone else) can: read, no write, execute
│   │    └─────── group (root group) can: read, no write, execute
│   └──────────── owner (root user) can: read, write, execute
└──────────────── d = directory (- means regular file)
```

---

### The three permission types

| Symbol | Meaning | On a file | On a directory |
|---|---|---|---|
| `r` | read | open & read it | list its contents |
| `w` | write | modify it | create/delete files inside |
| `x` | execute | run it as a program | enter it with `cd` |

---

### The three permission groups

| Group | Who |
|---|---|
| Owner | The user who owns the file |
| Group | Users in the assigned group |
| Others | Everyone else |

---

So `drwxr-xr-x` means:
- It's a **directory**
- **Owner** (root) can read, write, enter it
- **Group** can read and enter, but not modify
- **Everyone else** can read and enter, but not modify

---

Now look at this line from your output:
```
-rw-r--r--  1 root root  3444 Jul 5 2023 adduser.conf
```

Can you decode it yourself? Tell me what each part means.

> My answer:

File
Owner can read and write but not execute
Group can read, not write and not execute
Others can only read as well

Perfect. You got it completely.

Now the practical side — **changing permissions.**

---

## chmod

Two ways to use it — symbolic and numeric. You need to know both.

### Symbolic (readable)

```bash
chmod u+x file.sh      # give owner execute
chmod g-w file.txt     # remove write from group
chmod o+r file.txt     # give others read
chmod a+x file.sh      # give everyone execute (a = all)
chmod +x  file.sh      # This is the same as chmod a+x file.sh
```

`u` = user/owner, `g` = group, `o` = others, `a` = all

> The system assumes all by default.

---

### Numeric (octal) — you'll see this everywhere

Each permission has a value:
```
r = 4
w = 2
x = 1
```

You add them up for each group:

```
rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-- = 4+0+0 = 4
r-x = 4+0+1 = 5
```

So `chmod 755 file.sh` means:
```
7 = rwx  (owner)
5 = r-x  (group)
5 = r-x  (others)
```

---

### Common ones you'll use constantly

| Command | Meaning |
|---|---|
| `chmod 755 file.sh` | Owner full, everyone else read+execute — typical for scripts |
| `chmod 644 file.txt` | Owner read+write, everyone else read only — typical for config files |
| `chmod 600 file.txt` | Owner only, no one else — typical for SSH keys |
| `chmod 777 file` | Everyone full access — almost always a bad idea |

---

Quick exercise — run these:

```bash
cd ~
touch testfile.txt
ls -la testfile.txt
chmod 755 testfile.txt
ls -la testfile.txt
chmod 600 testfile.txt
ls -la testfile.txt
```

Try and see if you can say what changed in the first column each time.

## chown — changing ownership

```bash
chown username file.txt           # change owner
chown username:groupname file.txt # change owner and group
chown -R username folder/         # recursive — entire folder
```

You'll mostly use this when a file is owned by root but you need your user to own it. Common in server setups.

---

You now understand:
- ✅ File types (`d`, `-`)
- ✅ Permission groups (owner, group, others)
- ✅ Permission types (r, w, x)
- ✅ chmod — symbolic and numeric
- ✅ chown
