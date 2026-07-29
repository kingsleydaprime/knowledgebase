# Get Help in Red Hat Enterprise Linux

> RHCSA V10

Part of [[README|RHCSA V10]]. This matters more than it looks on the exam — you get zero internet access during RHCSA, so `man` and `--help` are the *only* references you have.

---

## man — the primary reference

```bash
man ls              # manual page for the ls command
man -k partition     # keyword search across all man pages (same as apropos)
apropos partition    # identical to man -k
whatis ls            # one-line summary of what a command is
```

### Man page sections

Man pages are organized into numbered sections. The same *name* can exist in multiple sections meaning different things — `passwd` is both a command and a file format:

| Section | Covers |
|---|---|
| 1 | User commands |
| 2 | System calls (kernel functions) |
| 3 | Library calls (C library functions) |
| 4 | Special files (usually in `/dev`) |
| 5 | File formats and conventions |
| 6 | Games |
| 7 | Miscellaneous (protocols, conventions, overviews) |
| 8 | System administration commands (mostly root-only) |

```bash
man passwd            # section 1 by default — the passwd COMMAND
man 5 passwd           # explicitly section 5 — the /etc/passwd FILE FORMAT
man -a passwd          # walk through every section that has an entry
```

Knowing to reach for `man 5 fstab` instead of `man fstab` (which doesn't exist — fstab isn't a command) is a real exam-relevant skill.

### Navigating inside a man page

Man pages open in a pager (`less` under the hood):

| Key | Action |
|---|---|
| `Space` / `f` | Page down |
| `b` | Page up |
| `/term` | Search forward for `term` |
| `n` | Next search match |
| `N` | Previous search match |
| `g` | Jump to top |
| `G` | Jump to bottom |
| `q` | Quit |

### Man page structure

Every man page follows roughly the same skeleton — knowing the skeleton means you can skim straight to what you need instead of reading top to bottom:

```
NAME          — one-line description
SYNOPSIS      — exact command syntax, [optional] vs required args
DESCRIPTION   — full explanation
OPTIONS       — every flag, explained
EXAMPLES      — sample invocations (not every page has this)
FILES         — related config/data files
SEE ALSO      — related man pages
```

---

## --help — faster, shallower

Almost every command supports `command --help` (or `-h`) for a quick flag summary printed straight to the terminal — no pager, no full explanation. Good for "what was that flag called again" when you already know the command.

```bash
tar --help
systemctl --help
```

---

## info — GNU's deeper alternative

Some GNU tools ship more detailed **Texinfo** documentation than their man page, browsable as a menu-driven hypertext document:

```bash
info coreutils
```

| Key | Action |
|---|---|
| `Space` | Next page |
| `Enter` | Follow a menu link under the cursor |
| `u` | Up one menu level |
| `q` | Quit |

In practice `man` covers the vast majority of what you need day to day; `info` is worth knowing exists for the handful of tools (like `coreutils`, `bash` itself) that document themselves more thoroughly there.

---

## Local package documentation

```bash
ls /usr/share/doc/<package-name>/     # READMEs, changelogs, example configs shipped with a package
rpm -qd httpd                          # list documentation files owned by a specific package
rpm -ql httpd                          # list ALL files owned by a package (not just docs)
```

---

## Red Hat's own documentation (outside the exam)

Not usable *during* the offline exam, but the real-world answer once you're on the job:

- **access.redhat.com/documentation** — official product docs per RHEL version
- **Red Hat Customer Portal** — Knowledgebase articles, especially for weird specific error messages
- **Red Hat Bugzilla** — tracked bugs, useful when something looks like a known issue rather than a config mistake
