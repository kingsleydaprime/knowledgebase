# Linux — Comprehensive Reference Guide

> A deep, practical reference covering Linux from first principles to production-level usage.
> Covers the filesystem, shell, users, permissions, processes, networking, storage, scripting, and more.
> Built for someone who uses Linux daily and needs to understand what's actually happening, not just which commands to type.

---

## Table of Contents

1. [How Linux Works — The Mental Model](#1-how-linux-works--the-mental-model)
2. [The Filesystem — Everything is a File](#2-the-filesystem--everything-is-a-file)
3. [Navigation and File Operations](#3-navigation-and-file-operations)
4. [Users, Groups, and Permissions](#4-users-groups-and-permissions)
5. [The Shell — Bash and Beyond](#5-the-shell--bash-and-beyond)
6. [Text Processing — The Linux Superpower](#6-text-processing--the-linux-superpower)
7. [Processes and Job Control](#7-processes-and-job-control)
8. [Package Management](#8-package-management)
9. [Systemd — Services and the Boot Process](#9-systemd--services-and-the-boot-process)
10. [Networking](#10-networking)
11. [Storage — Disks, Partitions, and Filesystems](#11-storage--disks-partitions-and-filesystems)
12. [Archives and Compression](#12-archives-and-compression)
13. [Environment Variables and Shell Configuration](#13-environment-variables-and-shell-configuration)
14. [SSH — Deep Reference](#14-ssh--deep-reference)
15. [Bash Scripting](#15-bash-scripting)
16. [Cron and Task Scheduling](#16-cron-and-task-scheduling)
17. [System Monitoring and Performance](#17-system-monitoring-and-performance)
18. [Logs and Journald](#18-logs-and-journald)
19. [Security and Hardening](#19-security-and-hardening)
20. [File Searching and Indexing](#20-file-searching-and-indexing)
21. [Input, Output, and Redirection](#21-input-output-and-redirection)
22. [Disk Usage and Cleanup](#22-disk-usage-and-cleanup)
23. [Linux for Servers — Production Patterns](#23-linux-for-servers--production-patterns)
24. [Troubleshooting Cheatsheet](#24-troubleshooting-cheatsheet)

---

## 1. How Linux Works — The Mental Model

### 1.1 The Kernel

Linux is technically just the kernel — the core program that runs first when the computer boots and manages everything: CPU scheduling, memory allocation, device drivers, and system calls. What most people call "Linux" is actually GNU/Linux — the Linux kernel plus a collection of tools (the GNU utilities: bash, grep, awk, ls, etc.) that make it usable.

The kernel runs in **kernel space** — it has unrestricted access to all hardware and memory. Everything else — your applications, your shell, your web server — runs in **user space** and must ask the kernel for resources via **system calls** (read, write, open, fork, exec, etc.).

When you run `cat file.txt`, what actually happens:
1. The shell calls `execve()` to start the `cat` process
2. `cat` calls `open()` to ask the kernel to open the file
3. The kernel checks permissions, opens the file, returns a file descriptor
4. `cat` calls `read()` in a loop to ask the kernel for data
5. The kernel reads from disk into a kernel buffer, copies to user space
6. `cat` calls `write()` to write the data to stdout
7. `cat` calls `exit()` when done

Understanding this model explains why Linux behaves the way it does — everything is permissions checks, file descriptors, and process management.

### 1.2 Distributions

The Linux kernel is the same everywhere. What differs between Ubuntu, Debian, Fedora, Arch, and Alpine is:
- The package manager (`apt`, `dnf`, `pacman`, `apk`)
- The default init system (almost all use systemd now)
- The default shell and utilities
- The release cadence and support period
- The philosophy (stability vs bleeding edge)

**For servers:** Ubuntu LTS (Long Term Support), Debian, or RHEL/CentOS Stream. Ubuntu LTS is the most common for VPS and cloud workloads — widely documented, 5-year support window.

**For containers:** Alpine Linux — tiny (5MB base image), musl libc, busybox utilities. Used in almost every production Docker image.

**For development:** Ubuntu, Fedora, or Arch — your preference.

### 1.3 Everything is a File

This is the most important Linux concept. In Linux, almost everything is represented as a file:
- Regular files — text, binaries, images
- Directories — files that contain lists of other files
- Devices — `/dev/sda` is your hard disk, `/dev/null` discards everything written to it, `/dev/random` produces random bytes
- Sockets — network and IPC communication endpoints
- Pipes — connections between processes
- Proc filesystem — `/proc/cpuinfo` is a "file" that the kernel writes on-the-fly when you read it

This means the same tools — `cat`, `echo`, `read`, `write` — work on all of them. It's a profoundly simple and powerful abstraction.

### 1.4 Processes

Every running program is a process. Each process has:
- A **PID** (Process ID) — a unique number
- A **PPID** (Parent PID) — every process except PID 1 was started by another process
- An **owner** (UID) — determines what it can access
- **File descriptors** — open files, sockets, pipes
- **Memory** — stack and heap
- **Environment variables** — inherited from the parent

The init process (PID 1, systemd on modern Linux) is the ancestor of all other processes. Every process is created by `fork()` (copying an existing process) followed by `exec()` (replacing the copy with a new program).

---

## 2. The Filesystem — Everything is a File

### 2.1 The Filesystem Hierarchy Standard (FHS)

Linux has a standardised directory layout. Knowing where things live tells you where to look when something goes wrong.

```
/                    Root — top of the entire filesystem tree
├── bin/             Essential user binaries: ls, cp, cat, bash (symlink to /usr/bin on modern systems)
├── boot/            Bootloader and kernel files
├── dev/             Device files: /dev/sda (disk), /dev/null, /dev/zero, /dev/random
├── etc/             System-wide configuration files — all plain text
├── home/            User home directories: /home/username
├── lib/             Shared libraries needed by /bin and /sbin
├── media/           Mount point for removable media (USB drives, CDs)
├── mnt/             Temporary mount points
├── opt/             Optional third-party software packages
├── proc/            Virtual filesystem — kernel and process information
├── root/            Root user's home directory (not /home/root)
├── run/             Runtime data (PIDs, sockets) — cleared on boot
├── sbin/            System binaries — for root: fdisk, iptables, useradd
├── srv/             Service data — web server files, FTP content
├── sys/             Virtual filesystem — hardware and kernel info
├── tmp/             Temporary files — cleared on boot (or via cron on some systems)
├── usr/             User programs and data (read-only in principle)
│   ├── bin/         Most user commands: git, python, node
│   ├── lib/         Libraries for /usr/bin
│   ├── local/       Locally compiled software — highest priority in PATH
│   └── share/       Architecture-independent data: man pages, icons
└── var/             Variable data — things that change while running
    ├── log/         System and application logs
    ├── lib/         Application state data (Docker stores images here)
    ├── tmp/         Temporary files preserved between reboots
    └── www/         Web server document roots (convention)
```

### 2.2 Key Directories to Know

**`/etc`** — All system configuration lives here. Plain text files — you can read and understand them. Notable:
- `/etc/passwd` — user accounts (not passwords — just account info)
- `/etc/shadow` — hashed passwords (root only)
- `/etc/hosts` — local DNS overrides
- `/etc/hostname` — the machine's hostname
- `/etc/fstab` — filesystems to mount at boot
- `/etc/ssh/sshd_config` — SSH server configuration
- `/etc/crontab` — system-wide cron jobs
- `/etc/environment` — system-wide environment variables
- `/etc/apt/sources.list` — package repositories (Debian/Ubuntu)

**`/proc`** — A virtual filesystem the kernel writes on-the-fly. Reading files here reads live kernel data:
- `/proc/cpuinfo` — CPU details
- `/proc/meminfo` — memory usage
- `/proc/uptime` — seconds since boot
- `/proc/loadavg` — load averages
- `/proc/net/tcp` — open TCP connections
- `/proc/PID/` — directory for each running process

**`/var/log`** — System logs:
- `/var/log/syslog` — general system messages
- `/var/log/auth.log` — authentication events (SSH logins, sudo)
- `/var/log/kern.log` — kernel messages
- `/var/log/apt/` — package install/upgrade history
- `/var/log/nginx/` — Nginx access and error logs

**`/dev`** — Device files:
- `/dev/sda`, `/dev/sdb` — SCSI/SATA disks
- `/dev/nvme0n1` — NVMe SSDs
- `/dev/sda1`, `/dev/sda2` — disk partitions
- `/dev/null` — the black hole — writing discards, reading returns EOF
- `/dev/zero` — returns infinite null bytes
- `/dev/random` / `/dev/urandom` — random data
- `/dev/tty` — current terminal
- `/dev/stdin`, `/dev/stdout`, `/dev/stderr` — standard streams

### 2.3 Absolute vs Relative Paths

**Absolute path** — starts from root `/`. Always works regardless of your current directory:
```bash
/home/username/projects/app/src/main.js
```

**Relative path** — relative to your current directory:
```bash
./src/main.js        # ./ means current directory
../config/app.yml    # ../ means parent directory
~/projects/          # ~ expands to your home directory (/home/username)
```

### 2.4 File Types

```bash
ls -la
```

The first character of the permissions string tells you the file type:

| Character | Type |
|---|---|
| `-` | Regular file |
| `d` | Directory |
| `l` | Symbolic link |
| `c` | Character device |
| `b` | Block device |
| `s` | Socket |
| `p` | Named pipe (FIFO) |

---

## 3. Navigation and File Operations

### 3.1 Navigation

```bash
pwd                          # Print working directory — where am I?
cd /path/to/directory        # Change to absolute path
cd ../                       # Go up one directory
cd ~                         # Go to home directory
cd -                         # Go to previous directory (toggle)
cd                           # No argument — also goes home

ls                           # List files
ls -l                        # Long format — permissions, owner, size, date
ls -la                       # Include hidden files (dotfiles)
ls -lh                       # Human-readable sizes (KB, MB, GB)
ls -lt                       # Sort by modification time, newest first
ls -lS                       # Sort by size, largest first
ls -R                        # Recursive — list all subdirectories
ls /path/to/dir              # List a specific directory
```

### 3.2 File Operations

```bash
# Creating
touch file.txt               # Create empty file or update timestamp
mkdir directory              # Create directory
mkdir -p a/b/c               # Create nested directories (no error if exists)

# Copying
cp file.txt copy.txt         # Copy file
cp -r dir/ copy_dir/         # Copy directory recursively
cp -p file.txt dest/         # Preserve permissions, timestamps, owner
cp -i file.txt dest/         # Prompt before overwriting

# Moving and Renaming
mv file.txt newname.txt      # Rename file
mv file.txt /other/dir/      # Move file
mv -i file.txt dest/         # Prompt before overwriting

# Deleting
rm file.txt                  # Delete file
rm -r directory/             # Delete directory recursively
rm -rf directory/            # Force delete — no prompts (use carefully)
rm -i file.txt               # Prompt before each deletion
rmdir directory/             # Delete empty directory only

# Viewing file contents
cat file.txt                 # Print entire file
cat -n file.txt              # Print with line numbers
less file.txt                # Paginate — scroll with j/k, quit with q
more file.txt                # Simpler pager (less is better)
head file.txt                # First 10 lines
head -n 20 file.txt          # First 20 lines
tail file.txt                # Last 10 lines
tail -n 20 file.txt          # Last 20 lines
tail -f file.txt             # Follow — stream new lines as they're added
tail -f -n 50 file.txt       # Follow, starting from last 50 lines

# File information
file file.txt                # Detect file type (regardless of extension)
stat file.txt                # Full metadata — size, permissions, timestamps, inode
wc file.txt                  # Word, line, character count
wc -l file.txt               # Line count only
wc -c file.txt               # Byte count only
du -sh file.txt              # Disk usage of a file
```

### 3.3 Symbolic and Hard Links

**Symbolic link (symlink)** — A pointer to another file or directory. Like a shortcut. If the target is deleted, the symlink breaks.

```bash
ln -s /path/to/original /path/to/link   # Create a symlink
ln -s /usr/local/bin/node /usr/bin/node # Common use: make a binary available in PATH
ls -la                                   # Symlinks show as: link -> target
readlink -f symlink                      # Resolve symlink to its final target
```

**Hard link** — A second name for the same file (same inode). Deleting either name doesn't delete the data until all names are removed. Can't span filesystems or link directories.

```bash
ln original.txt hardlink.txt   # Create a hard link
```

---

## 4. Users, Groups, and Permissions

### 4.1 Users

Every file and process is owned by a user. Users are identified by a **UID** (User ID) number — the name is just a human-readable alias.

```bash
# User information
whoami                       # Current username
id                           # Current UID, GID, and all groups
id username                  # Info for a specific user
who                          # Who is logged in
w                            # Who is logged in and what they're doing
last                         # Login history
lastlog                      # Last login for all users

# User management
sudo useradd -m username     # Create user with home directory
sudo useradd -m -s /bin/bash -G sudo username  # With bash shell and sudo group
sudo adduser username        # Interactive user creation (friendlier on Debian/Ubuntu)
sudo adduser --gecos "" username  # Skip the extra prompts
sudo userdel username        # Delete user (keep home directory)
sudo userdel -r username     # Delete user and home directory
sudo usermod -aG groupname username   # Add user to a group
sudo usermod -s /bin/bash username    # Change user's shell
sudo passwd username         # Set or change password
sudo passwd -l username      # Lock account (disable login)
sudo passwd -u username      # Unlock account

# Switch users
su - username                # Switch to user (- loads their full environment)
sudo -u username command     # Run a command as another user
sudo -i                      # Interactive root shell via sudo
sudo command                 # Run a single command as root
```

**Important system users:**
- `root` (UID 0) — superuser, unrestricted access to everything
- `www-data` (UID 33) — web server processes (Nginx, Apache)
- `nobody` — processes that need minimal privileges

### 4.2 Groups

Groups allow multiple users to share access to files. Each file has one owner (user) and one group.

```bash
groups                       # List groups current user belongs to
groups username              # List groups for a specific user
cat /etc/group               # All groups on the system

sudo groupadd groupname      # Create a group
sudo groupdel groupname      # Delete a group
sudo gpasswd -a username groupname   # Add user to group
sudo gpasswd -d username groupname   # Remove user from group
newgrp groupname             # Switch active group in current session
```

### 4.3 The Permission Model

Every file has three permission sets:
- **u** (user/owner) — the file's owner
- **g** (group) — members of the file's group
- **o** (other/world) — everyone else

Each set has three bits:
- **r** (read = 4) — view contents
- **w** (write = 2) — modify contents
- **x** (execute = 1) — run as program (files) / enter directory

```bash
ls -la
# Output: -rwxr-xr-- 1 kingsley developers 4096 May 1 10:30 script.sh
#          ││││││││││
#          │└──┤└──┤└── other permissions (r--)
#          │   │   └─── group permissions (r-x)
#          │   └─────── user permissions (rwx)
#          └─────────── file type (-)
```

```bash
# Changing permissions
chmod 755 file               # rwxr-xr-x (numeric)
chmod u+x file               # Add execute for owner (symbolic)
chmod g-w file               # Remove write from group
chmod o=r file               # Set other to read-only exactly
chmod a+x file               # Add execute for all
chmod -R 755 directory/      # Recursive

# Changing ownership
chown username file          # Change owner
chown username:groupname file  # Change owner and group
chown -R username:group dir/ # Recursive
chgrp groupname file         # Change group only
```

### 4.4 Special Permission Bits

Beyond the standard rwx, there are three special bits:

**SUID (Set User ID) — bit 4000** — When set on an executable, it runs as the file's owner, not the person executing it. This is how `passwd` can modify `/etc/shadow` (owned by root) when run by a regular user.

```bash
chmod u+s file               # Set SUID
chmod 4755 file              # Numeric: 4 = SUID + 755
ls -l                        # Shows as 's' in owner execute position: -rwsr-xr-x
```

**SGID (Set Group ID) — bit 2000** — On executables, runs with the file's group. On directories, new files inherit the directory's group instead of the creator's primary group. Useful for shared project directories.

```bash
chmod g+s directory/         # Set SGID on directory
chmod 2755 directory/
ls -l                        # Shows as 's' in group execute position: drwxr-sr-x
```

**Sticky Bit — bit 1000** — On directories, only the file owner (or root) can delete files, even if others have write permission. Used on `/tmp` so users can't delete each other's temp files.

```bash
chmod +t directory/          # Set sticky bit
chmod 1777 /tmp              # Sticky bit + full permissions
ls -l                        # Shows as 't' in other execute position: drwxrwxrwt
```

### 4.5 sudo and the sudoers File

`sudo` allows permitted users to run commands as root (or another user). Configuration is in `/etc/sudoers` — **always edit with `visudo`**, which validates syntax before saving (a syntax error in sudoers locks you out).

```bash
sudo visudo                  # Safe editor for sudoers

# Common sudoers entries:
# username ALL=(ALL:ALL) ALL         — user can run any command as any user
# %sudo    ALL=(ALL:ALL) ALL         — anyone in the sudo group
# username ALL=(ALL) NOPASSWD: ALL   — no password prompt (use carefully)
# username ALL=(ALL) /usr/bin/docker # Only allow running docker
```

```bash
sudo -l                      # List what the current user can sudo
sudo -l -U username          # List what another user can sudo
sudo !!                      # Re-run last command with sudo
```

---

## 5. The Shell — Bash and Beyond

### 5.1 What the Shell Is

The shell is a command interpreter — it reads your input, parses it, and makes system calls to execute it. It's also a programming language. Bash (Bourne Again Shell) is the default on most Linux systems.

When you type a command, bash:
1. Expands aliases
2. Expands variables (`$HOME`, `$PATH`)
3. Performs glob expansion (`*.txt` → list of files)
4. Splits the result into words
5. Looks up the command in PATH
6. Forks a child process and executes the command

### 5.2 Essential Shell Features

**History:**

```bash
history                      # Show command history
history 20                   # Last 20 commands
!!                           # Repeat last command
!n                           # Repeat command number n
!string                      # Repeat last command starting with string
!$                           # Last argument of previous command
!*                           # All arguments of previous command
Ctrl+R                       # Reverse search through history
Ctrl+G                       # Cancel reverse search
```

**Keyboard shortcuts:**

```bash
Ctrl+C                       # Kill current process (SIGINT)
Ctrl+Z                       # Suspend current process (send to background)
Ctrl+D                       # EOF / logout
Ctrl+L                       # Clear screen (same as clear)
Ctrl+A                       # Move cursor to beginning of line
Ctrl+E                       # Move cursor to end of line
Ctrl+W                       # Delete word before cursor
Ctrl+U                       # Delete from cursor to beginning of line
Ctrl+K                       # Delete from cursor to end of line
Alt+F                        # Move forward one word
Alt+B                        # Move backward one word
Tab                          # Autocomplete
Tab Tab                      # Show all completions
```

**Aliases:**

```bash
alias ll='ls -lah'           # Create alias
alias gs='git status'
alias ..='cd ..'
alias ...='cd ../..'
unalias ll                   # Remove alias
alias                        # List all aliases
```

Put aliases in `~/.bashrc` or `~/.bash_aliases` to make them permanent.

### 5.3 Variables

```bash
# Setting variables
NAME="Kingsley"              # No spaces around =
export NAME="Kingsley"       # Export makes it available to child processes

# Using variables
echo $NAME
echo ${NAME}                 # Braces — clearer, required in some contexts
echo "${NAME}daprime"        # Concatenation

# Variable operations
echo ${NAME:-"default"}      # Use default if NAME is unset or empty
echo ${NAME:="default"}      # Set and use default if unset
echo ${NAME:?"error msg"}    # Error and exit if unset
echo ${#NAME}                # Length of NAME
echo ${NAME^^}               # Uppercase
echo ${NAME,,}               # Lowercase
echo ${NAME:0:4}             # Substring: start at 0, length 4
echo ${NAME/old/new}         # Replace first match
echo ${NAME//old/new}        # Replace all matches
```

**Special variables:**

```bash
$0                           # Script name
$1, $2, $3...                # Positional arguments
$@                           # All arguments as separate words
$*                           # All arguments as a single word
$#                           # Number of arguments
$?                           # Exit code of last command (0 = success)
$$                           # PID of current shell
$!                           # PID of last background process
$-                           # Current shell options
```

### 5.4 Command Substitution and Arithmetic

```bash
# Command substitution — use output of a command as a value
DATE=$(date +%Y-%m-%d)
FILES=$(ls *.txt)
echo "Today is $(date)"

# Arithmetic
echo $((5 + 3))              # 8
echo $((10 / 3))             # 3 (integer division)
echo $((10 % 3))             # 1 (modulo)
COUNT=5
((COUNT++))                  # Increment
((COUNT += 10))

# bc for floating point
echo "scale=2; 10/3" | bc    # 3.33
```

### 5.5 Quoting

Understanding quoting prevents many confusing bugs:

```bash
# Double quotes — preserve spaces, allow variable expansion
echo "Hello $NAME"           # Hello Kingsley
echo "Today is $(date)"      # Expands $() too

# Single quotes — everything is literal
echo 'Hello $NAME'           # Hello $NAME (no expansion)
echo 'Today is $(date)'      # Today is $(date)

# Backslash — escape next character
echo "Price: \$50"           # Price: $50
echo "Tab:\there"            # Tab:	here

# Word splitting — why you should quote variables
files="a b c"
ls $files                    # Runs: ls a b c (three args)
ls "$files"                  # Runs: ls "a b c" (one arg)
```

---

## 6. Text Processing — The Linux Superpower

### 6.1 Why This Matters

Linux's philosophy is small tools that do one thing well, connected by pipes. The combination of `grep`, `awk`, `sed`, `sort`, `cut`, `tr`, and pipes creates a text processing environment more powerful than most scripting languages for log analysis, data extraction, and transformation.

### 6.2 grep — Search Text

```bash
grep "pattern" file.txt              # Search for pattern in file
grep -i "pattern" file.txt           # Case-insensitive
grep -n "pattern" file.txt           # Show line numbers
grep -v "pattern" file.txt           # Invert — show lines NOT matching
grep -r "pattern" directory/         # Recursive search
grep -l "pattern" *.txt              # Only show filenames, not matching lines
grep -c "pattern" file.txt           # Count matching lines
grep -A 3 "pattern" file.txt         # 3 lines After each match
grep -B 3 "pattern" file.txt         # 3 lines Before each match
grep -C 3 "pattern" file.txt         # 3 lines Context (before and after)
grep -E "pattern1|pattern2" file.txt # Extended regex (OR)
grep -w "word" file.txt              # Match whole word only
grep -o "pattern" file.txt           # Show only the matching part
grep --color "pattern" file.txt      # Highlight matches

# Useful patterns
grep "^ERROR" app.log                # Lines starting with ERROR
grep "EOF$" file.txt                 # Lines ending with EOF
grep "[0-9]\{3\}" file.txt           # Lines with 3+ consecutive digits
grep -E "\b[0-9]{1,3}(\.[0-9]{1,3}){3}\b" file.txt  # IP addresses
```

### 6.3 sed — Stream Editor

`sed` transforms text — find and replace, delete lines, insert text:

```bash
# Substitution
sed 's/old/new/' file.txt            # Replace first occurrence per line
sed 's/old/new/g' file.txt           # Replace all occurrences (global)
sed 's/old/new/gi' file.txt          # Case-insensitive, global
sed -i 's/old/new/g' file.txt        # Edit file in-place
sed -i.bak 's/old/new/g' file.txt    # In-place with .bak backup

# Delete lines
sed '/pattern/d' file.txt            # Delete lines matching pattern
sed '5d' file.txt                    # Delete line 5
sed '5,10d' file.txt                 # Delete lines 5-10
sed '/^$/d' file.txt                 # Delete blank lines
sed '/^#/d' file.txt                 # Delete comment lines

# Print specific lines
sed -n '5p' file.txt                 # Print only line 5
sed -n '5,10p' file.txt              # Print lines 5-10
sed -n '/pattern/p' file.txt         # Print lines matching pattern

# Insert and append
sed '5i\New line' file.txt           # Insert before line 5
sed '5a\New line' file.txt           # Append after line 5
sed '1i\#!/bin/bash' script.sh       # Add shebang at top

# Practical examples
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed 's/[[:space:]]*$//' file.txt     # Remove trailing whitespace
sed 's/^[[:space:]]*//' file.txt     # Remove leading whitespace
```

### 6.4 awk — Structured Text Processing

`awk` is a full programming language for processing columnar data. Each input line is split into fields by a delimiter.

```bash
# Basic usage
awk '{print $1}' file.txt            # Print first field (space-separated)
awk '{print $1, $3}' file.txt        # Print fields 1 and 3
awk -F: '{print $1}' /etc/passwd     # -F: sets field separator to :
awk '{print NF}' file.txt            # Print number of fields per line
awk '{print NR": "$0}' file.txt      # Print line number and line

# Conditions
awk '$3 > 100' file.txt              # Print lines where field 3 > 100
awk '/pattern/ {print $2}' file.txt  # Print field 2 of matching lines
awk 'NR==5' file.txt                 # Print line 5
awk 'NR>=5 && NR<=10' file.txt       # Print lines 5-10

# Calculations
awk '{sum += $1} END {print sum}' numbers.txt      # Sum column 1
awk '{sum += $1} END {print sum/NR}' numbers.txt   # Average
awk 'END {print NR}' file.txt                      # Count lines

# BEGIN and END blocks
awk 'BEGIN {print "Header"} {print $1} END {print "Footer"}' file.txt

# Practical examples
awk -F: '{print $1": "$3}' /etc/passwd        # Username: UID
awk '{print $NF}' file.txt                    # Last field on each line
awk '!seen[$0]++' file.txt                    # Remove duplicate lines
ps aux | awk '{print $1, $2, $11}' | head -20 # Process list: user, pid, command
df -h | awk 'NR>1 {print $5, $6}'             # Disk usage percentages and mount points
```

### 6.5 sort and uniq

```bash
sort file.txt                        # Sort alphabetically
sort -r file.txt                     # Reverse sort
sort -n file.txt                     # Numeric sort
sort -k2 file.txt                    # Sort by field 2
sort -k2 -n file.txt                 # Sort by field 2 numerically
sort -u file.txt                     # Sort and remove duplicates
sort -t: -k3 -n /etc/passwd          # Sort passwd by UID (field 3, : delimiter)

uniq file.txt                        # Remove consecutive duplicate lines (input must be sorted)
uniq -c file.txt                     # Count occurrences
uniq -d file.txt                     # Show only duplicate lines
uniq -u file.txt                     # Show only unique lines

# Common pattern: count and rank occurrences
sort file.txt | uniq -c | sort -rn   # Most frequent lines first
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head  # Top IPs
```

### 6.6 cut, tr, paste

```bash
# cut — extract columns
cut -d: -f1 /etc/passwd              # Field 1, colon delimiter
cut -d: -f1,3 /etc/passwd            # Fields 1 and 3
cut -c1-10 file.txt                  # Characters 1-10
cut -d, -f2- file.csv                # Field 2 to end (CSV)

# tr — translate or delete characters
echo "Hello" | tr 'a-z' 'A-Z'       # Uppercase
echo "Hello" | tr 'A-Z' 'a-z'       # Lowercase
echo "he llo" | tr -d ' '           # Delete spaces
echo "hello" | tr -s 'l'            # Squeeze repeated chars
cat file.txt | tr '\n' ','          # Replace newlines with commas

# paste — merge lines
paste file1.txt file2.txt            # Merge lines side by side with tab
paste -d, file1.txt file2.txt        # Comma delimiter
paste -s file.txt                    # Merge all lines of one file
```

### 6.7 Pipes and Chaining

```bash
# The pipe | connects stdout of one command to stdin of the next
cat /var/log/auth.log | grep "Failed" | awk '{print $11}' | sort | uniq -c | sort -rn

# Real-world examples
# Find the 10 biggest files in a directory
find /var -type f | xargs du -sh | sort -rh | head -10

# Count errors per hour in a log file
grep "ERROR" app.log | awk '{print $1, substr($2,1,2)}' | sort | uniq -c

# Find all processes using more than 50% CPU
ps aux | awk '$3 > 50 {print $1, $2, $3, $11}'

# Extract all unique email addresses from a file
grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' file.txt | sort -u

# Show disk usage of top 10 directories
du -sh /* 2>/dev/null | sort -rh | head -10
```

### 6.8 xargs

`xargs` builds and executes commands from stdin — it turns lines of input into command arguments:

```bash
# Basic usage
echo "file1 file2 file3" | xargs rm       # Remove those files
find . -name "*.log" | xargs rm           # Delete all .log files
find . -name "*.txt" | xargs grep "error" # Search inside all .txt files

# With placeholder
find . -name "*.jpg" | xargs -I{} cp {} /backup/  # {} is replaced with each line
ls *.txt | xargs -I{} mv {} {}.bak               # Rename all .txt to .txt.bak

# Parallel execution
find . -name "*.jpg" | xargs -P4 -I{} convert {} -resize 800x {}  # 4 parallel processes

# Handle spaces in filenames
find . -name "*.txt" -print0 | xargs -0 grep "pattern"  # -print0 and -0 handle spaces
```

---

## 7. Processes and Job Control

### 7.1 Viewing Processes

```bash
ps                           # Processes for current terminal
ps aux                       # All processes, all users, detailed
ps aux | grep process-name   # Find a specific process
ps -ef                       # Full format listing (alternative style)
ps --forest                  # Tree view showing parent-child relationships
ps -u username               # Processes for a specific user
ps -p PID                    # Info for a specific PID

pgrep process-name           # Find PID(s) by name
pgrep -u username            # Find PIDs owned by user
pgrep -a nginx               # Show PID and full command

top                          # Interactive process viewer (q to quit)
htop                         # Better interactive viewer (install separately)
```

**Reading `ps aux` output:**

```
USER     PID   %CPU  %MEM   VSZ    RSS   TTY  STAT  START  TIME  COMMAND
kingsley 1234  0.5   1.2    45000  12000 pts/0 Sl   10:00  0:01  node server.js
```

- **VSZ** — Virtual memory size (includes shared libs, memory-mapped files)
- **RSS** — Resident Set Size — actual RAM used
- **STAT** — Process state: `S` sleeping, `R` running, `Z` zombie, `T` stopped, `D` uninterruptible sleep

### 7.2 Signals

Signals are messages sent to processes:

```bash
kill PID                     # Send SIGTERM (15) — graceful shutdown request
kill -9 PID                  # Send SIGKILL — immediate force kill
kill -HUP PID                # Send SIGHUP — reload config (many daemons respond to this)
kill -STOP PID               # Pause process
kill -CONT PID               # Resume paused process
killall process-name         # Kill all processes with that name
pkill process-name           # Kill by name (more flexible)
pkill -u username            # Kill all processes by user
pkill -9 -f "python script"  # Kill by full command line match

# Signal numbers you'll use
# SIGTERM (15) — graceful termination — give the process a chance to clean up
# SIGKILL (9) — immediate kill — cannot be caught or ignored
# SIGHUP (1) — hangup — traditionally reloads config
# SIGINT (2) — interrupt — same as Ctrl+C
# SIGSTOP (19) — pause — same as Ctrl+Z
# SIGCONT (18) — continue a stopped process
```

### 7.3 Job Control

```bash
command &                    # Run command in background
jobs                         # List background jobs
fg                           # Bring most recent background job to foreground
fg %2                        # Bring job 2 to foreground
bg                           # Continue stopped job in background
bg %2                        # Continue job 2 in background

Ctrl+Z                       # Suspend current foreground process
Ctrl+C                       # Terminate current foreground process

# nohup — run command that survives terminal close
nohup command &              # Output goes to nohup.out
nohup command > output.log 2>&1 &  # Custom output file

# disown — remove job from shell's job table (survives shell exit)
command &
disown %1                    # Disown job 1
```

### 7.4 Process Priority — nice and renice

Lower priority processes get less CPU time when the system is busy. Nice value ranges from -20 (highest priority) to 19 (lowest).

```bash
nice -n 10 command           # Start command with lower priority (nice=10)
nice -n -5 command           # Higher priority (requires root for negative values)
renice 10 -p PID             # Change priority of running process
renice 10 -u username        # Change priority of all user's processes

# View priorities in top/htop — NI column
top                          # Look at NI column
```

### 7.5 /proc Filesystem for Process Info

```bash
ls /proc/PID/                # Directory for each running process
cat /proc/PID/status         # Process status and memory info
cat /proc/PID/cmdline        # Full command line (null-separated)
cat /proc/PID/environ        # Environment variables
cat /proc/PID/fd/            # Open file descriptors
cat /proc/PID/maps           # Memory map
ls -la /proc/PID/fd/         # See all open files by a process
```

---

## 8. Package Management

### 8.1 apt — Debian/Ubuntu

```bash
# Updating
sudo apt update              # Refresh package index (always do this first)
sudo apt upgrade             # Upgrade all installed packages
sudo apt full-upgrade        # Upgrade + handle changed dependencies
sudo apt dist-upgrade        # Full upgrade + may add/remove packages

# Installing and removing
sudo apt install package-name
sudo apt install -y package-name     # Auto-confirm
sudo apt install package=1.2.3       # Install specific version
sudo apt remove package-name         # Remove package (keep config)
sudo apt purge package-name          # Remove package and config files
sudo apt autoremove                  # Remove unused dependency packages
sudo apt clean                       # Clear cached package files

# Searching and info
apt search keyword                   # Search for packages
apt show package-name                # Package details
apt list --installed                 # List installed packages
apt list --upgradable                # List upgradable packages
dpkg -l                              # List all installed packages (dpkg level)
dpkg -l | grep package-name          # Check if specific package is installed
dpkg -L package-name                 # List files installed by a package
dpkg -S /path/to/file                # Find which package owns a file

# Repositories
cat /etc/apt/sources.list            # Main repository sources
ls /etc/apt/sources.list.d/          # Additional repository files
sudo add-apt-repository ppa:name/ppa # Add a PPA (Ubuntu)
```

### 8.2 Other Package Managers

```bash
# dnf/yum — Fedora/RHEL/CentOS
sudo dnf install package-name
sudo dnf remove package-name
sudo dnf update
sudo dnf search keyword
sudo dnf info package-name

# pacman — Arch Linux
sudo pacman -Syu             # Full system upgrade
sudo pacman -S package-name  # Install
sudo pacman -R package-name  # Remove
sudo pacman -Ss keyword      # Search

# apk — Alpine Linux (used in Docker containers)
apk add package-name
apk del package-name
apk update
apk search keyword
apk info package-name

# snap — universal packages (Ubuntu)
snap install package-name
snap remove package-name
snap list
snap refresh                 # Update all snaps
```

### 8.3 Manual Installation Methods

```bash
# From source
./configure                  # Check dependencies and generate Makefile
make                         # Compile
sudo make install            # Install to /usr/local/

# From .deb file
sudo dpkg -i package.deb     # Install .deb package
sudo apt install -f          # Fix missing dependencies after dpkg install

# From binary/tarball
tar -xzf software.tar.gz
cd software/
sudo cp binary /usr/local/bin/

# pip — Python packages
pip install package --break-system-packages    # System Python (Ubuntu 23+)
pip install package --user                     # Install to ~/.local/bin/
python -m venv venv && source venv/bin/activate  # Virtual environment (preferred)
pip install -r requirements.txt

# npm — Node.js packages
npm install -g package-name  # Global install
npm install package-name     # Local (project) install
```

---

## 9. Systemd — Services and the Boot Process

### 9.1 The Boot Process

Understanding the Linux boot process helps you debug startup failures:

```
1. BIOS/UEFI — Power-on self-test, finds bootloader
2. GRUB — Bootloader, loads kernel and initramfs into memory
3. Kernel — Initialises hardware, mounts root filesystem
4. initramfs — Temporary root filesystem with drivers
5. /sbin/init (PID 1) — systemd on modern Linux
6. systemd — Reads unit files, brings up services in dependency order
7. getty/login — Terminal login prompts
8. Shell
```

### 9.2 systemd Units

Everything systemd manages is a **unit** — a file describing a service, mount point, socket, timer, or device.

**Service unit** (`.service`) — A daemon or one-shot process
**Timer unit** (`.timer`) — Like cron, but systemd-managed
**Socket unit** (`.socket`) — Socket-activated service
**Mount unit** (`.mount`) — Filesystem mount point
**Target unit** (`.target`) — Group of units (like runlevels)

Unit files live in:
- `/lib/systemd/system/` — Package-installed units (don't edit these)
- `/etc/systemd/system/` — Local overrides and custom units (edit these)
- `~/.config/systemd/user/` — User-level units

### 9.3 Service Management

```bash
# Starting, stopping, restarting
sudo systemctl start service-name
sudo systemctl stop service-name
sudo systemctl restart service-name
sudo systemctl reload service-name    # Reload config without full restart
sudo systemctl reload-or-restart service-name  # Reload if possible, else restart

# Enable/disable (start on boot)
sudo systemctl enable service-name    # Enable — start on boot
sudo systemctl disable service-name   # Disable — don't start on boot
sudo systemctl enable --now service-name  # Enable and start immediately

# Status and info
systemctl status service-name         # Status, recent logs, PID
systemctl is-active service-name      # Active or not
systemctl is-enabled service-name     # Enabled or not
systemctl list-units                  # All active units
systemctl list-units --type=service   # All active services
systemctl list-units --failed         # Failed units
systemctl list-unit-files             # All installed unit files and state

# System state
sudo systemctl reboot
sudo systemctl poweroff
sudo systemctl suspend
sudo systemctl hibernate

# Daemon reload — required after editing unit files
sudo systemctl daemon-reload          # Must run after creating/editing unit files
```

### 9.4 Writing a Service Unit

```ini
# /etc/systemd/system/my-app.service

[Unit]
Description=My Application Server           # Human-readable name
After=network.target                        # Start after network is up
After=postgresql.service                    # Start after PostgreSQL
Requires=postgresql.service                 # Fail if PostgreSQL isn't running

[Service]
Type=simple                                 # Process stays in foreground
User=appuser                                # Run as this user
Group=appgroup
WorkingDirectory=/home/appuser/app          # Working directory

# Environment
Environment=NODE_ENV=production
Environment=PORT=3000
EnvironmentFile=/home/appuser/app/.env      # Load env vars from file

# The command to run
ExecStart=/usr/bin/node /home/appuser/app/dist/main.js

# Graceful stop
ExecStop=/bin/kill -SIGTERM $MAINPID
TimeoutStopSec=30                           # Wait up to 30s for graceful stop

# Restart policy
Restart=always                              # Always restart on exit
RestartSec=5                                # Wait 5s before restart
StartLimitInterval=60s                      # Within 60 seconds
StartLimitBurst=3                           # Allow 3 restart attempts

# Output
StandardOutput=journal                      # Logs go to journald
StandardError=journal

[Install]
WantedBy=multi-user.target                  # Start in normal multi-user mode
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now my-app
sudo systemctl status my-app
journalctl -u my-app -f                     # Follow service logs
```

### 9.5 Targets (Runlevels)

```bash
systemctl get-default                       # Show default target
sudo systemctl set-default multi-user.target  # Set default (no GUI)
sudo systemctl set-default graphical.target   # Set default (with GUI)
sudo systemctl isolate rescue.target          # Switch to rescue mode
```

---

## 10. Networking

### 10.1 Network Concepts

**IP Address** — A numerical identifier for a network interface. IPv4: `192.168.1.100`. IPv6: `2001:db8::1`.

**Subnet mask** — Defines which part of the IP is the network and which is the host. `/24` means the first 24 bits are network (`255.255.255.0`). Hosts in the same `/24` can reach each other directly.

**Gateway** — The router that forwards traffic to other networks. Typically `192.168.1.1` on home networks.

**DNS** — Translates hostnames to IP addresses. `/etc/resolv.conf` specifies which DNS servers to use.

**Port** — A number (0–65535) that identifies a specific service on a host. Port 80 = HTTP, 443 = HTTPS, 22 = SSH, 5432 = PostgreSQL, 6379 = Redis.

**Socket** — An IP address + port combination. `192.168.1.100:3000`.

### 10.2 Network Configuration

```bash
# View interfaces and addresses
ip addr                          # All interfaces and IP addresses (modern)
ip addr show eth0                # Specific interface
ifconfig                         # Older alternative (install net-tools)

# View routing table
ip route                         # Show routing table
ip route show default            # Show default gateway

# Interface management
ip link set eth0 up              # Bring interface up
ip link set eth0 down            # Bring interface down
ip addr add 192.168.1.100/24 dev eth0  # Assign IP (temporary — lost on reboot)

# DNS
cat /etc/resolv.conf             # DNS servers in use
cat /etc/hosts                   # Local DNS overrides (hostname → IP)
resolvectl status                # systemd-resolved status (modern Ubuntu)
```

### 10.3 Network Diagnostics

```bash
# Connectivity
ping host                        # Send ICMP echo — basic reachability test
ping -c 4 host                   # Send exactly 4 pings
ping -i 0.2 host                 # Ping every 0.2 seconds (fast)

# DNS lookup
nslookup domain.com              # Basic DNS query
dig domain.com                   # Detailed DNS query
dig domain.com A                 # Query for A records (IPv4)
dig domain.com MX                # Query for mail records
dig @8.8.8.8 domain.com          # Query specific DNS server
host domain.com                  # Simple DNS lookup

# Routing
traceroute domain.com            # Trace route to destination
tracepath domain.com             # Similar, doesn't need root
mtr domain.com                   # Live traceroute with statistics

# Port and connection checking
ss -tlnp                         # Show listening TCP sockets with PID
ss -ulnp                         # Show listening UDP sockets
ss -an                           # All connections
ss -an | grep :80                # Connections on port 80
netstat -tlnp                    # Older alternative (install net-tools)
lsof -i :3000                    # What's using port 3000
lsof -i tcp                      # All TCP connections

# Testing connectivity to a port
nc -zv host 80                   # TCP connection test (netcat)
nc -zv host 80 443               # Test multiple ports
telnet host 80                   # Another port test (older)
curl -v http://host:3000/        # HTTP connection test with details

# Network interface statistics
ip -s link                       # Packet/byte counters per interface
ss -s                            # Socket statistics summary
cat /proc/net/dev                # Detailed interface statistics
```

### 10.4 curl and wget

```bash
# curl — transfer data to/from URLs
curl https://example.com                    # GET request
curl -o file.html https://example.com       # Save to file
curl -O https://example.com/file.tar.gz     # Save with original filename
curl -L https://example.com                 # Follow redirects
curl -I https://example.com                 # Headers only
curl -v https://example.com                 # Verbose — show request and response headers
curl -s https://example.com                 # Silent — no progress bar
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'                     # POST with JSON body
curl -X POST https://api.example.com \
  -H "Authorization: Bearer token" \
  -d @data.json                             # POST from file
curl -u username:password https://example.com  # Basic auth
curl -k https://self-signed.example.com     # Skip SSL verification
curl -w "%{http_code}\n" -o /dev/null -s https://example.com  # Just status code
curl --retry 3 --retry-delay 5 https://example.com  # Retry on failure
curl -x http://proxy:8080 https://example.com  # Through a proxy

# wget — download files
wget https://example.com/file.tar.gz        # Download file
wget -q https://example.com/file.tar.gz     # Quiet
wget -c https://example.com/bigfile.tar.gz  # Continue interrupted download
wget -r -np https://example.com/dir/        # Recursive download
wget --limit-rate=1m https://example.com/file.tar.gz  # Limit bandwidth
```

### 10.5 iptables and Firewall

```bash
# iptables — the underlying Linux firewall (UFW is a frontend for this)
sudo iptables -L                    # List all rules
sudo iptables -L -n -v              # Verbose with packet counts
sudo iptables -L INPUT              # List INPUT chain rules

# The three main chains:
# INPUT — incoming traffic destined for this host
# OUTPUT — outgoing traffic from this host
# FORWARD — traffic passing through (for routers/gateways)

# Rules
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # Allow TCP port 80 in
sudo iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT   # Allow from subnet
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  # Allow established
sudo iptables -P INPUT DROP         # Default deny incoming
sudo iptables -D INPUT 3            # Delete rule number 3

# Save and restore
sudo iptables-save > /etc/iptables/rules.v4   # Save rules
sudo iptables-restore < /etc/iptables/rules.v4  # Restore rules

# UFW is much easier for everyday use (covered in VPS reference)
```

### 10.6 /etc/hosts and DNS

```bash
# /etc/hosts — local DNS overrides, checked before DNS servers
cat /etc/hosts

# Add entries
echo "192.168.1.100 myserver.local" | sudo tee -a /etc/hosts

# Common uses
# Block a domain
echo "0.0.0.0 ads.example.com" | sudo tee -a /etc/hosts
# Point domain to local dev server
echo "127.0.0.1 api.myapp.local" | sudo tee -a /etc/hosts
```

---

## 11. Storage — Disks, Partitions, and Filesystems

### 11.1 Disk Concepts

**Block device** — A device that reads/writes in fixed-size blocks (sectors). Hard drives, SSDs, USB drives.

**Partition** — A logically divided section of a disk. `/dev/sda` is the disk; `/dev/sda1`, `/dev/sda2` are partitions.

**Filesystem** — A structure on a partition that organises files. `ext4` is the most common Linux filesystem. Others: `xfs`, `btrfs`, `ntfs`, `fat32`.

**Mount** — Attaching a filesystem to a directory in the tree. After mounting `/dev/sda1` at `/data`, files on that partition are accessible at `/data/`.

**Inode** — A data structure that stores file metadata (size, owner, timestamps, permissions, data block pointers) — everything except the filename. The directory entry maps filename → inode number.

### 11.2 Disk Management Commands

```bash
# View disks and partitions
lsblk                        # Block devices in a tree view
lsblk -f                     # Include filesystem type and mount point
fdisk -l                     # Detailed partition table (run as root)
parted -l                    # Another partition viewer
blkid                        # Block device UUIDs and filesystem types

# Disk and filesystem usage
df -h                        # Disk usage by filesystem, human-readable
df -i                        # Inode usage (if you run out of inodes, you can't create files)
du -sh /path/                # Disk usage of a directory
du -sh /*                    # Disk usage of top-level directories
du -sh * | sort -rh | head   # Largest directories in current location
ncdu /                       # Interactive disk usage browser

# Mounting and unmounting
sudo mount /dev/sdb1 /mnt/data      # Mount a partition
sudo mount -o ro /dev/sdb1 /mnt/    # Mount read-only
sudo umount /mnt/data               # Unmount
sudo umount -l /mnt/data            # Lazy unmount (when busy)

# /etc/fstab — automatic mounts at boot
# Format: device  mountpoint  fstype  options  dump  pass
cat /etc/fstab
# UUID=abc123 /data ext4 defaults 0 2
# Use UUID not /dev/sdb1 — device names can change, UUIDs don't
```

### 11.3 Creating Filesystems

```bash
# Partition a new disk
sudo fdisk /dev/sdb          # Interactive partitioner
# Commands inside fdisk: n (new), p (primary), w (write)

# Create filesystem
sudo mkfs.ext4 /dev/sdb1     # Create ext4 filesystem
sudo mkfs.xfs /dev/sdb1      # Create XFS filesystem
sudo mkfs.fat -F32 /dev/sdb1 # Create FAT32

# Label the filesystem
sudo e2label /dev/sdb1 my-data  # Label ext4
sudo tune2fs -L my-data /dev/sdb1  # Alternative

# Check and repair filesystem
sudo fsck /dev/sdb1          # Check (unmounted only)
sudo fsck -y /dev/sdb1       # Auto-fix errors
sudo e2fsck -f /dev/sdb1     # Force check ext4
```

### 11.4 LVM — Logical Volume Manager

LVM adds a layer of abstraction between physical disks and filesystems, allowing you to resize volumes, add disks to a volume group, and create snapshots.

```
Physical Disks (/dev/sda, /dev/sdb)
    ↓
Physical Volumes (PV)
    ↓
Volume Group (VG) — pool of storage
    ↓
Logical Volumes (LV) — like virtual partitions
    ↓
Filesystems (ext4, xfs)
```

```bash
# Create LVM
sudo pvcreate /dev/sdb                     # Initialise disk as physical volume
sudo vgcreate my-vg /dev/sdb               # Create volume group
sudo lvcreate -L 20G -n my-lv my-vg        # Create 20GB logical volume
sudo mkfs.ext4 /dev/my-vg/my-lv            # Create filesystem
sudo mount /dev/my-vg/my-lv /data/

# Extend a logical volume
sudo lvextend -L +10G /dev/my-vg/my-lv     # Add 10GB
sudo resize2fs /dev/my-vg/my-lv            # Resize ext4 filesystem to fill it

# View LVM
sudo pvs                                   # Physical volumes
sudo vgs                                   # Volume groups
sudo lvs                                   # Logical volumes
sudo pvdisplay
sudo vgdisplay
sudo lvdisplay
```

---

## 12. Archives and Compression

### 12.1 tar — The Archive Tool

`tar` (Tape Archive) bundles files into a single archive. Compression is separate but usually combined.

```bash
# Create archives
tar -czf archive.tar.gz directory/          # Create gzip-compressed archive
tar -cjf archive.tar.bz2 directory/         # Create bzip2-compressed archive
tar -cJf archive.tar.xz directory/          # Create xz-compressed archive
tar -cf archive.tar directory/              # Create uncompressed archive

# Extract archives
tar -xzf archive.tar.gz                     # Extract gzip archive
tar -xjf archive.tar.bz2                    # Extract bzip2 archive
tar -xJf archive.tar.xz                     # Extract xz archive
tar -xf archive.tar.gz -C /destination/     # Extract to specific directory

# List contents without extracting
tar -tzf archive.tar.gz                     # List contents of gzip archive

# Flags reference
# -c  create
# -x  extract
# -t  list
# -z  gzip compression
# -j  bzip2 compression
# -J  xz compression
# -f  filename (must come last before the filename)
# -v  verbose
# -C  change to directory
# -p  preserve permissions
```

### 12.2 Other Compression Tools

```bash
# gzip / gunzip
gzip file.txt                # Compress to file.txt.gz (removes original)
gzip -k file.txt             # Keep original
gunzip file.txt.gz           # Decompress
gzip -d file.txt.gz          # Same as gunzip
gzip -l file.txt.gz          # List compression ratio

# zip / unzip (cross-platform)
zip archive.zip file1 file2  # Create zip
zip -r archive.zip directory/ # Recursive
unzip archive.zip            # Extract
unzip -l archive.zip         # List contents
unzip archive.zip -d /path/  # Extract to directory

# xz
xz file.txt                  # Compress (best ratio, slowest)
unxz file.txt.xz             # Decompress

# bzip2
bzip2 file.txt
bunzip2 file.txt.bz2

# zstd — modern, fast
zstd file.txt                # Compress
zstd -d file.txt.zst         # Decompress
```

---

## 13. Environment Variables and Shell Configuration

### 13.1 Environment Variables

Environment variables are key-value pairs available to all processes. They configure software behaviour without changing code.

```bash
env                          # List all environment variables
printenv                     # Same
printenv HOME                # Print specific variable
echo $PATH                   # Print PATH

export MY_VAR="value"        # Set and export for child processes
unset MY_VAR                 # Remove variable

# Common environment variables
$HOME                        # Home directory: /home/username
$USER                        # Current username
$SHELL                       # Current shell: /bin/bash
$PATH                        # Colon-separated list of directories searched for commands
$PWD                         # Current working directory
$OLDPWD                      # Previous working directory
$EDITOR                      # Default text editor
$TERM                        # Terminal type
$LANG                        # System locale
$TZ                          # Timezone
$DISPLAY                     # X11 display (GUI)
$HISTSIZE                    # How many commands to keep in history
$PS1                         # Shell prompt format
```

### 13.2 PATH

PATH is the most important environment variable. When you type a command, the shell looks in each directory listed in PATH, in order, until it finds the executable.

```bash
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin

# Add a directory to PATH
export PATH="$HOME/.local/bin:$PATH"   # Prepend — searched first
export PATH="$PATH:/opt/myapp/bin"     # Append — searched last

# Find where a command lives
which node                   # /usr/local/bin/node
which python3                # /usr/bin/python3
type ls                      # ls is aliased to 'ls --color=auto'
whereis git                  # All locations: binary, source, man pages
```

### 13.3 Shell Configuration Files

When bash starts, it reads configuration files in a specific order:

**Login shell** (when you SSH in or use `su -`):
1. `/etc/profile` — system-wide
2. `~/.bash_profile` or `~/.profile` — user-specific login config

**Interactive non-login shell** (opening a new terminal tab):
1. `~/.bashrc` — user-specific interactive config

**The common pattern** — put everything in `~/.bashrc` and source it from `~/.bash_profile`:

```bash
# ~/.bash_profile
if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi
```

```bash
# ~/.bashrc — add customisations here
export PATH="$HOME/.local/bin:$PATH"
export EDITOR=nvim
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups   # No duplicate history entries

# Aliases
alias ll='ls -lah'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias df='df -h'
alias du='du -h'

# Custom prompt
export PS1='\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]\$ '

# Source after editing
source ~/.bashrc    # Or: . ~/.bashrc
```

---

## 14. SSH — Deep Reference

### 14.1 How SSH Works

SSH (Secure Shell) establishes an encrypted tunnel between two machines. When you connect:

1. **TCP handshake** — client connects to port 22
2. **Protocol negotiation** — agree on SSH version and algorithms
3. **Key exchange** — generate a shared session key using Diffie-Hellman (no key ever transmitted)
4. **Server authentication** — server proves identity using its host key (stored in `~/.ssh/known_hosts`)
5. **User authentication** — password or public key
6. **Encrypted session** — all subsequent communication is encrypted with the session key

### 14.2 Key Management

```bash
# Generate keys
ssh-keygen -t ed25519 -C "comment"              # Ed25519 (recommended)
ssh-keygen -t rsa -b 4096 -C "comment"          # RSA 4096 (older, compatible)
ssh-keygen -t ed25519 -f ~/.ssh/custom_key       # Custom filename

# Key files
~/.ssh/id_ed25519                # Private key — never share, chmod 600
~/.ssh/id_ed25519.pub            # Public key — share freely
~/.ssh/authorized_keys           # Public keys allowed to log in (chmod 600)
~/.ssh/known_hosts               # Fingerprints of servers you've connected to

# Copying public key to server
ssh-copy-id user@host                           # Copy default public key
ssh-copy-id -i ~/.ssh/custom.pub user@host      # Copy specific key

# SSH agent — hold decrypted keys in memory
eval $(ssh-agent)                # Start agent
ssh-add                          # Add default key
ssh-add ~/.ssh/custom_key        # Add specific key
ssh-add -l                       # List loaded keys
ssh-add -D                       # Remove all keys from agent
```

### 14.3 ~/.ssh/config

The SSH config file allows you to set per-host options, avoiding long command-line flags:

```
# ~/.ssh/config

# Default settings for all hosts
Host *
  ServerAliveInterval 60        # Send keepalive every 60s
  ServerAliveCountMax 3         # Give up after 3 missed keepalives
  AddKeysToAgent yes            # Auto-add keys to agent
  IdentityFile ~/.ssh/id_ed25519

# Specific host
Host myserver
  HostName 203.0.113.42         # Actual IP or hostname
  User kingsley                 # Username
  Port 2222                     # Custom SSH port
  IdentityFile ~/.ssh/server_key

# Jump host (bastion)
Host internal-server
  HostName 10.0.1.50            # Private IP
  User kingsley
  ProxyJump bastion             # SSH through bastion first

Host bastion
  HostName 203.0.113.10
  User kingsley
```

With this config:
```bash
ssh myserver                    # Instead of: ssh -p 2222 -i ~/.ssh/server_key kingsley@203.0.113.42
ssh internal-server             # Automatically jumps through bastion
```

### 14.4 Port Forwarding and Tunneling

```bash
# Local port forwarding — forward local port to remote destination
ssh -L 8080:localhost:80 user@server     # localhost:8080 → server:80
ssh -L 5432:db-host:5432 user@bastion    # Local 5432 → db-host:5432 through bastion

# Remote port forwarding — forward remote port to local machine
ssh -R 8080:localhost:3000 user@server   # server:8080 → your machine:3000 (expose local to remote)

# Dynamic port forwarding — SOCKS proxy
ssh -D 1080 user@server                  # Creates SOCKS5 proxy on local port 1080
# Configure browser to use SOCKS5 proxy localhost:1080

# Flags
# -N: don't execute remote command (for tunnels)
# -f: go to background
# -C: compress data
ssh -L 5432:db:5432 user@bastion -N -f   # Background database tunnel
```

### 14.5 scp and rsync

```bash
# scp — secure copy (simple)
scp file.txt user@host:/remote/path/      # Upload
scp user@host:/remote/file.txt ./         # Download
scp -r directory/ user@host:/remote/path/ # Upload directory
scp -P 2222 file.txt user@host:/path/     # Custom port

# rsync — efficient sync (preferred for large transfers)
rsync -avz source/ user@host:/destination/         # Upload with compression
rsync -avz user@host:/source/ ./destination/       # Download
rsync -avz --delete source/ user@host:/dest/       # Mirror (delete remote extras)
rsync -avz --exclude='.git' --exclude='node_modules' source/ user@host:/dest/
rsync -avzP source/ user@host:/dest/               # -P: progress + partial (resume)
rsync -n source/ user@host:/dest/                  # Dry run — show what would change
rsync -e "ssh -p 2222" source/ user@host:/dest/    # Custom SSH port
```

---

## 15. Bash Scripting

### 15.1 Script Structure

```bash
#!/bin/bash
# Above: shebang — tells the OS which interpreter to use
# Always make scripts executable: chmod +x script.sh

# Best practice: set options at the top
set -e          # Exit immediately if any command fails
set -u          # Treat unset variables as errors
set -o pipefail # Pipe fails if any command in it fails
# Combined: set -euo pipefail
```

### 15.2 Conditionals

```bash
# if/elif/else
if [ "$var" = "value" ]; then
  echo "matched"
elif [ "$var" = "other" ]; then
  echo "other match"
else
  echo "no match"
fi

# [[ ]] is more powerful than [ ] — prefer it in bash scripts
if [[ "$var" == "value" ]]; then   # == works in [[]]
if [[ "$var" =~ ^[0-9]+$ ]]; then  # Regex matching in [[]]
if [[ -z "$var" ]]; then           # True if var is empty
if [[ -n "$var" ]]; then           # True if var is non-empty

# File tests
if [[ -f "$file" ]]; then    # Regular file exists
if [[ -d "$dir" ]]; then     # Directory exists
if [[ -e "$path" ]]; then    # Path exists (any type)
if [[ -r "$file" ]]; then    # File is readable
if [[ -w "$file" ]]; then    # File is writable
if [[ -x "$file" ]]; then    # File is executable
if [[ -s "$file" ]]; then    # File exists and is non-empty

# Numeric comparisons (use -eq, -lt, etc. in [ ]; use == < > in (( )))
if [ "$n" -eq 5 ]; then      # Equal
if [ "$n" -ne 5 ]; then      # Not equal
if [ "$n" -lt 5 ]; then      # Less than
if [ "$n" -gt 5 ]; then      # Greater than
if (( n > 5 )); then         # Arithmetic context — cleaner for numbers

# Combining conditions
if [[ -f "$file" && -r "$file" ]]; then   # AND
if [[ "$a" = "x" || "$b" = "y" ]]; then  # OR
if [[ ! -f "$file" ]]; then               # NOT
```

### 15.3 Loops

```bash
# for loop
for i in 1 2 3 4 5; do
  echo "Number: $i"
done

for file in *.txt; do
  echo "Processing $file"
done

for i in $(seq 1 10); do
  echo "$i"
done

for ((i=0; i<10; i++)); do   # C-style for loop
  echo "$i"
done

# while loop
while [[ "$count" -lt 10 ]]; do
  echo "Count: $count"
  ((count++))
done

# Read lines from file or command
while IFS= read -r line; do
  echo "Line: $line"
done < file.txt

while IFS= read -r line; do
  echo "$line"
done < <(command_that_outputs_lines)

# until loop — runs until condition is true
until [[ "$result" = "done" ]]; do
  result=$(check_status)
  sleep 5
done

# Loop control
break       # Exit loop
continue    # Skip to next iteration
```

### 15.4 Functions

```bash
# Define
my_function() {
  local var="$1"    # local — scoped to function
  echo "Got: $var"
  return 0          # Return code (0-255); not a return value
}

# Call
my_function "argument"

# Capture return value (use echo + command substitution)
get_value() {
  echo "computed_value"
}
result=$(get_value)

# Error handling with functions
check_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" >&2   # >&2 writes to stderr
    exit 1
  fi
}
```

### 15.5 Error Handling

```bash
# Check command success
if ! command; then
  echo "Command failed" >&2
  exit 1
fi

# Trap — run cleanup on exit or error
cleanup() {
  echo "Cleaning up..."
  rm -f /tmp/tempfile
}
trap cleanup EXIT              # Run on any exit
trap cleanup ERR               # Run on error
trap 'cleanup; exit 1' INT TERM  # Run on Ctrl+C or kill

# Exit with a message
die() {
  echo "ERROR: $1" >&2
  exit "${2:-1}"    # Exit code defaults to 1
}

[[ -f "$config" ]] || die "Config file not found: $config"
```

### 15.6 A Practical Script Template

```bash
#!/bin/bash
# deploy.sh — Example production script

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
APP_DIR="/home/appuser/my-app"
IMAGE="yourdockerhubuser/my-app"
LOG_FILE="/var/log/deploy.log"

# ─── Functions ────────────────────────────────────────────────────────────────
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

die() {
  log "ERROR: $1"
  exit "${2:-1}"
}

check_deps() {
  local deps=("docker" "curl")
  for dep in "${deps[@]}"; do
    command -v "$dep" &>/dev/null || die "Required dependency not found: $dep"
  done
}

health_check() {
  local url="$1"
  local attempts=0
  local max=30

  log "Waiting for service to become healthy..."

  while (( attempts < max )); do
    if curl -sf "$url" &>/dev/null; then
      log "Service is healthy"
      return 0
    fi
    ((attempts++))
    sleep 5
  done

  die "Service failed health check after $((max * 5)) seconds"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
  log "Starting deployment..."

  check_deps

  cd "$APP_DIR" || die "App directory not found: $APP_DIR"

  log "Pulling latest image..."
  docker compose pull

  log "Starting new containers..."
  docker compose up -d --remove-orphans

  health_check "https://app.yourdomain.com/health"

  log "Cleaning up old images..."
  docker image prune -f

  log "Deployment complete."
}

main "$@"
```

---

## 16. Cron and Task Scheduling

### 16.1 Cron Syntax

```
# ┌─── minute (0–59)
# │ ┌─── hour (0–23)
# │ │ ┌─── day of month (1–31)
# │ │ │ ┌─── month (1–12 or Jan-Dec)
# │ │ │ │ ┌─── day of week (0–7; 0 and 7 = Sunday, or Sun-Sat)
# │ │ │ │ │
  * * * * * command to run
```

**Special values:**
- `*` — every value
- `*/5` — every 5 (minutes, hours, etc.)
- `1,5,10` — at 1, 5, and 10
- `1-5` — from 1 to 5 (inclusive)

```bash
# Examples
0 * * * *    command    # Every hour at :00
0 3 * * *    command    # Every day at 3:00 AM
0 3 * * 0    command    # Every Sunday at 3:00 AM
*/15 * * * * command    # Every 15 minutes
0 */6 * * *  command    # Every 6 hours
0 9-17 * * 1-5 command # Every hour 9-17, Monday-Friday
0 0 1 * *    command    # First day of every month at midnight
```

**Special strings:**
```bash
@reboot   command    # Once at startup
@hourly   command    # 0 * * * *
@daily    command    # 0 0 * * *
@weekly   command    # 0 0 * * 0
@monthly  command    # 0 0 1 * *
@yearly   command    # 0 0 1 1 *
```

### 16.2 Managing Cron Jobs

```bash
crontab -e               # Edit your cron jobs
crontab -l               # List your cron jobs
crontab -r               # Remove all your cron jobs
sudo crontab -e -u username  # Edit another user's cron jobs
sudo crontab -l -u username  # List another user's cron jobs

# System cron directories (no crontab syntax — just scripts)
/etc/cron.hourly/        # Scripts run hourly
/etc/cron.daily/         # Scripts run daily
/etc/cron.weekly/        # Scripts run weekly
/etc/cron.monthly/       # Scripts run monthly

# System crontab (can specify user)
/etc/crontab             # System crontab with user column
/etc/cron.d/             # Additional crontab files
```

### 16.3 Cron Best Practices

```bash
# Always use full paths in cron — PATH is minimal in cron's environment
# BAD:
0 3 * * * backup.sh
# GOOD:
0 3 * * * /home/username/scripts/backup.sh

# Redirect output — cron will email output if no redirection
0 3 * * * /home/username/scripts/backup.sh >> /var/log/backup.log 2>&1
# 2>&1 redirects stderr to same place as stdout

# Use flock to prevent overlapping runs
0 * * * * flock -n /tmp/job.lock /home/username/scripts/job.sh
# flock -n: fail immediately if lock is already held (don't wait)

# Test your cron command manually first
/bin/bash /home/username/scripts/backup.sh
```

---

## 17. System Monitoring and Performance

### 17.1 CPU

```bash
top                          # Interactive process viewer
htop                         # Better top (install separately)
nproc                        # Number of CPU cores
lscpu                        # CPU architecture details
cat /proc/cpuinfo            # Raw CPU info

# Load average — in top, uptime, and w
uptime
# 14:00  up 5 days,  load average: 0.52, 0.68, 0.73
#                                  1min  5min  15min
# Load average = average number of runnable + waiting-for-CPU processes
# Load = 1.0 on a 4-core system means 25% utilised
# Load = 4.0 on a 4-core system means 100% utilised
# Load > number of cores = system is overloaded

mpstat                       # Per-CPU statistics (install sysstat)
mpstat -P ALL 1              # All CPUs, 1-second intervals
```

### 17.2 Memory

```bash
free -h                      # RAM and swap usage, human-readable
cat /proc/meminfo            # Detailed memory stats

# Reading free -h output:
#               total   used   free   shared  buff/cache  available
# Mem:           7.7G   2.1G   4.5G    150M       1.1G      5.2G
# Swap:          2.0G   100M   1.9G
#
# "available" is what matters — free + reclaimable buff/cache
# buff/cache is Linux's disk cache — it's used but can be reclaimed

vmstat 1                     # Virtual memory stats, 1-second intervals
```

### 17.3 Disk I/O

```bash
iostat                       # Disk I/O statistics (install sysstat)
iostat -x 1                  # Extended stats, 1-second intervals
iotop                        # Interactive per-process I/O monitor (install iotop)
iotop -o                     # Only show processes actively doing I/O

# Key metrics in iostat -x:
# %util — disk utilisation (close to 100% = disk is saturated)
# await — average wait time per request in milliseconds
# r/s, w/s — read/write operations per second
```

### 17.4 Network

```bash
nload                        # Live bandwidth usage per interface (install nload)
iftop                        # Per-connection bandwidth usage (install iftop)
nethogs                      # Per-process bandwidth usage (install nethogs)
ss -s                        # Socket statistics summary
cat /proc/net/dev            # Cumulative bytes/packets per interface
```

### 17.5 System-Wide Tools

```bash
vmstat 1 10                  # System stats: processes, memory, swap, I/O, CPU (10 samples)
sar -u 1 5                   # CPU usage, 5 samples (sysstat)
sar -r 1 5                   # Memory usage, 5 samples
sar -d 1 5                   # Disk stats, 5 samples

dmesg                        # Kernel ring buffer — hardware events, driver messages
dmesg | tail -20             # Recent kernel messages
dmesg -T                     # With human-readable timestamps
dmesg -w                     # Follow (like tail -f)
dmesg | grep -i error        # Look for hardware errors

# System info
uname -a                     # Kernel version, architecture, hostname
hostname                     # Machine hostname
hostname -I                  # All IP addresses
uptime                       # Time running and load averages
cat /etc/os-release          # OS version info
lsb_release -a               # OS release info (Ubuntu/Debian)
```

### 17.6 strace and ltrace — Debugging at the System Call Level

```bash
strace command               # Trace system calls made by a command
strace -p PID                # Attach to running process
strace -e open,read command  # Trace only specific system calls
strace -o output.txt command # Write trace to file
strace -f command            # Follow forks (trace child processes too)

# Common use: why is this program slow or failing?
strace -p $(pgrep my-app) 2>&1 | grep -E "open|read|write|connect"
```

---

## 18. Logs and Journald

### 18.1 Traditional Log Files

```bash
# Key log files
/var/log/syslog              # General system messages
/var/log/auth.log            # Authentication: SSH logins, sudo, su
/var/log/kern.log            # Kernel messages
/var/log/dmesg               # Boot-time hardware/driver messages
/var/log/apt/history.log     # Package install/remove history
/var/log/dpkg.log            # dpkg activity
/var/log/nginx/access.log    # Nginx request log
/var/log/nginx/error.log     # Nginx error log

tail -f /var/log/syslog      # Follow system log
tail -f /var/log/auth.log    # Watch authentication events live

# Log rotation — logrotate manages log file sizes
cat /etc/logrotate.conf      # Global config
ls /etc/logrotate.d/         # Per-application configs
sudo logrotate -f /etc/logrotate.conf  # Force rotation now
```

### 18.2 journalctl — systemd Journal

On modern Ubuntu, most logs go to the systemd journal (`journalctl`), not just files.

```bash
# Basic usage
journalctl                   # All logs (oldest first, paginated)
journalctl -r                # Reverse — newest first
journalctl -n 50             # Last 50 entries
journalctl -f                # Follow — like tail -f
journalctl -b                # Since last boot
journalctl -b -1             # Previous boot
journalctl --since "1 hour ago"
journalctl --since "2026-01-01 00:00:00" --until "2026-01-02 00:00:00"

# Filtering by unit (service)
journalctl -u nginx          # Nginx logs
journalctl -u nginx -f       # Follow nginx logs
journalctl -u nginx -n 100   # Last 100 nginx entries
journalctl -u nginx -u postgresql  # Multiple services

# Filtering by priority
journalctl -p err            # Errors only
journalctl -p warning        # Warnings and above
# Priority levels: emerg, alert, crit, err, warning, notice, info, debug

# Filtering by PID or executable
journalctl _PID=1234
journalctl _EXE=/usr/bin/sshd

# Output formats
journalctl -o json           # JSON output
journalctl -o json-pretty    # Formatted JSON
journalctl -o short-precise  # Precise timestamps

# Disk usage
journalctl --disk-usage      # How much space the journal uses
sudo journalctl --vacuum-size=500M   # Keep only 500MB of logs
sudo journalctl --vacuum-time=7d     # Keep only last 7 days
```

---

## 19. Security and Hardening

### 19.1 User and Privilege Security

```bash
# Find all SUID/SGID binaries — potential privilege escalation vectors
find / -perm -4000 -type f 2>/dev/null    # SUID files
find / -perm -2000 -type f 2>/dev/null    # SGID files
find / -perm -6000 -type f 2>/dev/null    # SUID + SGID

# Find world-writable files and directories
find / -perm -o+w -type f 2>/dev/null     # World-writable files
find / -perm -o+w -type d 2>/dev/null     # World-writable directories

# Files with no owner (orphaned after user deletion)
find / -nouser 2>/dev/null
find / -nogroup 2>/dev/null

# Check sudoers
sudo -l                      # What can the current user sudo
cat /etc/sudoers             # Full sudoers (read-only without visudo)
```

### 19.2 File Integrity

```bash
# Calculate file checksums
sha256sum file.txt           # SHA-256 hash
sha256sum -c checksums.txt   # Verify against a checksums file
md5sum file.txt              # MD5 (weaker — use sha256 for security)

# AIDE — Advanced Intrusion Detection Environment
sudo aide --init             # Build baseline database
sudo aide --check            # Compare current state to baseline
# Any changed files are reported — detect tampering
```

### 19.3 Open Ports and Services Audit

```bash
# What's listening on the network?
ss -tlnp                     # TCP listening sockets with PID
ss -ulnp                     # UDP listening sockets
ss -tlnp | grep -v "127.0.0.1"  # Only externally accessible

# Close unnecessary services
sudo systemctl stop service-name
sudo systemctl disable service-name

# Scan your own server (from outside)
nmap -sV your-ip             # Port scan with service detection
nmap -A your-ip              # Aggressive scan (OS, services, scripts)
```

### 19.4 auditd — System Audit Logging

`auditd` logs security-relevant system calls and file access events:

```bash
sudo apt install auditd
sudo systemctl enable --now auditd

# Add audit rules
sudo auditctl -w /etc/passwd -p wa -k passwd_changes    # Watch file for writes
sudo auditctl -w /etc/sudoers -p wa -k sudoers_changes
sudo auditctl -a always,exit -F arch=b64 -S execve      # Log all executed commands

# View audit log
sudo ausearch -k passwd_changes   # Events tagged with key
sudo aureport --summary           # Summary report
sudo aureport --auth              # Authentication events
```

### 19.5 AppArmor

AppArmor is a Mandatory Access Control (MAC) system that confines programs to specific files and capabilities. It's enabled by default on Ubuntu.

```bash
sudo apparmor_status                  # Show profiles and their status
sudo aa-status                        # Same

# Profile modes
# enforce — violations are blocked and logged
# complain — violations are logged but not blocked (use for developing profiles)

sudo aa-complain /path/to/binary      # Set to complain mode
sudo aa-enforce /path/to/binary       # Set to enforce mode

sudo aa-logprof                        # Interactively update profile based on log events

# Disable a profile
sudo ln -s /etc/apparmor.d/usr.bin.program /etc/apparmor.d/disable/
sudo apparmor_parser -R /etc/apparmor.d/usr.bin.program
```

---

## 20. File Searching and Indexing

### 20.1 find

`find` is the most powerful file search tool — it searches the filesystem directly:

```bash
# Basic find
find /path -name "filename"          # Find by name
find /path -name "*.log"             # Find by pattern
find /path -iname "readme*"          # Case-insensitive name
find . -type f                       # Files only
find . -type d                       # Directories only
find . -type l                       # Symlinks only

# Find by size
find . -size +100M                   # Larger than 100MB
find . -size -1k                     # Smaller than 1KB
find . -size +10M -size -100M        # Between 10MB and 100MB

# Find by time
find . -mtime -7                     # Modified in last 7 days
find . -mtime +30                    # Modified more than 30 days ago
find . -newer reference.txt          # Modified after reference.txt
find . -atime -1                     # Accessed in last 24 hours

# Find by permissions
find . -perm 644                     # Exact permissions
find . -perm -644                    # At least 644
find . -perm /u+s                    # Has SUID bit

# Find by owner
find . -user username                # Owned by user
find . -group groupname              # Owned by group
find . -nouser                       # No owner

# Execute actions
find . -name "*.tmp" -delete                   # Delete all .tmp files
find . -name "*.sh" -exec chmod +x {} \;       # Make all .sh files executable
find . -type f -exec grep -l "pattern" {} \;   # Find files containing pattern
find . -name "*.log" -exec gzip {} \;          # Compress all log files
find . -name "*.log" | xargs gzip              # Same, using xargs (faster for many files)

# Exclude directories
find . -name "*.js" -not -path "*/node_modules/*"
find . -name "*.py" -not -path "*/.git/*" -not -path "*/venv/*"

# Combine conditions
find . -type f -name "*.txt" -size +1k -mtime -30  # AND (default)
find . -name "*.txt" -o -name "*.md"               # OR
find . -not -name "*.log"                           # NOT
```

### 20.2 locate and updatedb

`locate` uses a pre-built index — much faster than `find` but only as fresh as the last index update:

```bash
locate filename              # Fast search
locate -i filename           # Case-insensitive
locate "*.conf"              # Pattern
locate -c filename           # Count results

sudo updatedb                # Rebuild the index (runs daily via cron)
```

### 20.3 which, type, whereis

```bash
which python3                # Path to the first python3 in PATH
which -a python3             # All pythons in PATH
type ls                      # Is it an alias, builtin, or file?
type -a ls                   # All definitions
whereis git                  # Binary, source, and man page locations
```

---

## 21. Input, Output, and Redirection

### 21.1 The Three Streams

Every process has three standard file descriptors:
- **0 — stdin** — standard input (keyboard by default)
- **1 — stdout** — standard output (terminal by default)
- **2 — stderr** — standard error (terminal by default)

### 21.2 Redirection

```bash
# Redirect stdout
command > file.txt           # Write stdout to file (overwrite)
command >> file.txt          # Append stdout to file
command > /dev/null          # Discard stdout

# Redirect stderr
command 2> error.log         # Write stderr to file
command 2>> error.log        # Append stderr to file
command 2>/dev/null          # Discard stderr

# Redirect both
command > output.log 2>&1    # Both stdout and stderr to same file
command &> output.log        # Shorthand for the above
command >> output.log 2>&1   # Append both

# Redirect stdin
command < input.txt          # Read stdin from file
command <<< "string"         # Here-string — pass string as stdin

# Here-document — multi-line stdin
command << EOF
line 1
line 2
EOF

cat << EOF > config.yml
server:
  host: localhost
  port: 3000
EOF

# Tee — write to file AND stdout simultaneously
command | tee output.log               # Overwrite
command | tee -a output.log            # Append
command | tee file1 file2 | grep error # Write to two files, pipe to grep
```

### 21.3 Process Substitution

```bash
# <() — treat command output as a file
diff <(ls dir1) <(ls dir2)            # Diff two directory listings
grep "error" <(journalctl -u nginx)   # Search journalctl output

# >() — send output to a command as if it's a file
tee >(gzip > output.gz) > output.txt  # Write to both gzip and plain file
```

---

## 22. Disk Usage and Cleanup

### 22.1 Finding What's Using Space

```bash
df -h                        # Filesystem usage overview
du -sh /*                    # Top-level directory sizes
du -sh /var/*                # Inside /var
du -sh * | sort -rh | head -20  # Largest items in current directory
ncdu /                       # Interactive browser (install ncdu)

# Find largest files
find / -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -20
find /var -type f -size +100M 2>/dev/null  # Files larger than 100MB

# Find and remove old log files
find /var/log -name "*.log.gz" -mtime +30 -delete
find /tmp -mtime +7 -delete              # Old temp files
```

### 22.2 Common Space Hogs

```bash
# Journal logs
journalctl --disk-usage
sudo journalctl --vacuum-size=200M

# APT cache
du -sh /var/cache/apt/
sudo apt clean               # Clear downloaded package cache

# Docker (see VPS reference for full Docker cleanup)
docker system df
docker system prune -af

# Core dumps
find / -name "core" -type f 2>/dev/null
find / -name "core.*" -type f 2>/dev/null

# Old kernels (Ubuntu)
dpkg --list 'linux-image-*' | grep '^ii'   # Installed kernels
sudo apt autoremove --purge                 # Remove old kernels

# Thumbnail cache
du -sh ~/.cache/thumbnails/
rm -rf ~/.cache/thumbnails/*

# npm cache
npm cache clean --force
du -sh ~/.npm/
```

---

## 23. Linux for Servers — Production Patterns

### 23.1 Running Services Reliably

```bash
# Always use systemd for long-running processes — not nohup, not screen
# systemd handles restarts, logging, dependency management

# Check if a service died and why
journalctl -u my-app -n 50 --no-pager
systemctl status my-app

# Services that should auto-restart
# In unit file: Restart=always or Restart=on-failure

# Resource limits via systemd (better than ulimit for services)
# In unit file:
# LimitNOFILE=65535     — file descriptors
# LimitNPROC=4096       — max processes
# MemoryLimit=512M      — memory limit
# CPUQuota=50%          — CPU limit
```

### 23.2 Server Hardening Checklist

```bash
# Disable unnecessary services
systemctl list-units --type=service --state=running   # What's running?
sudo systemctl disable --now avahi-daemon   # Zero-conf networking (rarely needed on servers)
sudo systemctl disable --now cups          # Printing (not needed on servers)

# Check for world-writable files in critical directories
find /etc -perm -o+w 2>/dev/null

# Verify SSH hardening
grep -E "^(PasswordAuthentication|PermitRootLogin|UsePAM)" /etc/ssh/sshd_config

# Check open ports
ss -tlnp

# Verify firewall is active
sudo ufw status

# Check scheduled jobs
crontab -l
sudo crontab -l
ls /etc/cron.*

# Review sudo configuration
sudo cat /etc/sudoers
```

### 23.3 Useful One-Liners for Production

```bash
# Watch a file for changes
watch -n 1 'ls -lh /var/log/app.log'

# Monitor multiple log files at once
tail -f /var/log/nginx/access.log /var/log/nginx/error.log

# Count connections by state (SYN_WAIT, ESTABLISHED, etc.)
ss -an | awk '{print $2}' | sort | uniq -c | sort -rn

# Top 10 IPs hitting your server
tail -n 10000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head

# Find processes listening on unexpected ports
ss -tlnp | grep -v -E ":22|:80|:443|:3000"

# Memory usage by process name
ps aux | awk '{print $4, $11}' | sort -rn | head -10

# Disk write speed test
dd if=/dev/zero of=/tmp/test bs=1M count=512 conv=fdatasync 2>&1 | tail -1

# Disk read speed test
dd if=/tmp/test of=/dev/null bs=1M 2>&1 | tail -1

# Network bandwidth test (install iperf3)
# On server: iperf3 -s
# On client: iperf3 -c server-ip

# How long a process has been running
ps -p PID -o etime=

# Watch system calls of a running process (what's it doing right now?)
strace -p PID -e trace=network 2>&1 | head -20

# Show all environment variables of a running process
cat /proc/PID/environ | tr '\0' '\n'

# Quickly check if a port is open on a remote host
timeout 3 bash -c 'cat < /dev/null > /dev/tcp/host/port' && echo "open" || echo "closed"
```

### 23.4 Shell Multiplexers — tmux

`tmux` (terminal multiplexer) lets you run multiple terminal sessions in one window, detach from them (they keep running on the server), and reattach later. Essential for server work.

```bash
tmux                         # Start tmux
tmux new -s session-name     # Start named session
tmux ls                      # List sessions
tmux attach -t session-name  # Attach to session
tmux attach                  # Attach to most recent session
tmux kill-session -t name    # Kill a session

# Key bindings (default prefix is Ctrl+B)
Ctrl+B  c        # New window
Ctrl+B  n        # Next window
Ctrl+B  p        # Previous window
Ctrl+B  0-9      # Switch to window number
Ctrl+B  ,        # Rename window
Ctrl+B  %        # Split pane vertically
Ctrl+B  "        # Split pane horizontally
Ctrl+B  arrows   # Move between panes
Ctrl+B  z        # Zoom/unzoom current pane
Ctrl+B  d        # Detach from session (session keeps running)
Ctrl+B  [        # Enter scroll/copy mode (q to exit)
Ctrl+B  ?        # Help — show all key bindings
```

```bash
# ~/.tmux.conf — customise tmux
# Change prefix from Ctrl+B to Ctrl+A (screen-style)
set-option -g prefix C-a
unbind C-b
bind C-a send-prefix

# Enable mouse
set -g mouse on

# Increase scrollback buffer
set -g history-limit 10000

# Start windows at 1 not 0
set -g base-index 1
```

---

## 24. Troubleshooting Cheatsheet

### "Command not found"

```bash
which command-name           # Is it in PATH?
echo $PATH                   # What's in PATH?
ls /usr/local/bin /usr/bin   # Is it installed?
sudo apt install package-name  # Install it
export PATH="$HOME/.local/bin:$PATH"  # Add directory to PATH
```

### "Permission denied"

```bash
ls -la file                  # Check permissions
whoami                       # Who am I running as?
stat file                    # Full file metadata
sudo command                 # Run as root
chmod +x script.sh           # Add execute permission
chown username file          # Fix ownership
```

### "No space left on device"

```bash
df -h                        # Which filesystem is full?
du -sh /* 2>/dev/null        # What's taking space?
du -sh /var/*                # Check /var
docker system prune -af      # Clean Docker
sudo journalctl --vacuum-size=200M  # Clean journals
sudo apt clean               # Clean package cache
find /tmp -mtime +7 -delete  # Clean old temp files
```

### "Port already in use"

```bash
sudo lsof -i :PORT           # What process is using the port?
sudo ss -tlnp | grep :PORT   # Same
sudo kill -9 PID             # Kill it
```

### "Service won't start"

```bash
sudo systemctl status service-name      # Status and recent logs
journalctl -u service-name -n 50        # More logs
journalctl -u service-name -b           # Since last boot
sudo systemctl cat service-name         # Show unit file
sudo systemd-analyze verify service.service  # Validate unit file
```

### "SSH connection refused"

```bash
nc -zv host 22                    # Is port 22 open?
sudo systemctl status sshd        # Is SSH running?
sudo ufw status                   # Is firewall blocking it?
cat /etc/ssh/sshd_config          # Is the port correct?
sudo journalctl -u sshd           # SSH server logs
```

### "Disk is slow"

```bash
iostat -x 1                  # Is a disk at 100% utilisation?
iotop -o                     # Which process is causing I/O?
sudo dmesg | grep -i error   # Hardware errors?
sudo smartctl -a /dev/sda    # SMART disk health data
```

### "System is slow/high load"

```bash
uptime                       # Load average
top                          # What's using CPU?
htop                         # Better process view
free -h                      # Is memory exhausted?
vmstat 1                     # CPU, memory, I/O all at once
sar -u 1 10                  # CPU usage over time
```

### "Network connectivity problems"

```bash
ping 8.8.8.8                 # Can we reach the internet?
ping $(hostname -I)          # Can we reach ourselves?
ip route                     # Is the default gateway set?
cat /etc/resolv.conf         # DNS configured?
dig google.com               # DNS resolution working?
curl -v https://example.com  # Full HTTP diagnostic
```

### Reading an Error You Don't Understand

```bash
# Copy the error message, then:
# 1. Check the last few lines — the actual error is usually at the bottom
# 2. Check the service log: journalctl -u service-name -n 100
# 3. Check syslog: tail -50 /var/log/syslog
# 4. Search the exact error string — someone else has hit it

# Useful: run the failing command with strace to see system calls
strace command 2>&1 | tail -20
```

---

*Last updated: 2026 — Built from real Linux usage and server experience.*
