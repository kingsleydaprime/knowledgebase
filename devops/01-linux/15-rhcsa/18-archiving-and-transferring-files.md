# Archiving and Transferring Files

> RHCSA V10 — added after reviewing the official RH134 course book (Red Hat System Administration II, RHEL 10.0), which gives this its own two chapters not previously covered in this folder in any depth (the RHCSA README only pointed to a brief `tar`/`scp` mention in [[devops/01-linux/linux-reference|Linux Reference]]).

Part of [[README|RHCSA V10]]. Two related but distinct problems: **archiving** bundles many files into one (for backup, or to move a whole tree at once), **transferring** moves files between machines securely over SSH.

---

## tar — bundling files into one archive

An archive is one file that contains many — the same idea as a `.zip`, but the Linux-native tool is `tar` ("tape archive," from its original purpose). `tar` needs exactly one **action** flag plus almost always `-f` to name the archive file:

| Action | Meaning |
|---|---|
| `-c` | **c**reate an archive |
| `-t` | lis**t** an archive's contents, without extracting |
| `-x` | e**x**tract an archive |

```bash
tar -cf backup.tar file1.log file2.log      # create
tar -tf backup.tar                           # list contents (no extraction)
tar -xf backup.tar                           # extract, into the current directory
```

By default `tar` strips the leading `/` from absolute paths before storing them (`tar: Removing leading '/' from member names` is expected output, not an error) — this is deliberate: an archive of relative paths can be extracted anywhere without silently overwriting files at their original absolute location.

### Compression

`tar` doesn't compress by itself — it hands off to a separate compressor, selected by flag (and conventionally reflected in the filename extension):

| Flag | Algorithm | Extension | Tradeoff |
|---|---|---|---|
| `-z` | gzip | `.tar.gz` | Fastest, most universally available, weakest compression of the three |
| `-j` | bzip2 | `.tar.bz2` | Slower than gzip, better ratio, less universally available |
| `-J` | xz | `.tar.xz` | Slowest, best compression ratio |
| `-a` | auto-detect | (any) | Picks the algorithm from the filename extension you give it |

```bash
tar -czf backup.tar.gz /etc          # create + gzip in one step
tar -tf backup.tar.gz                 # listing works the same regardless of compression — tar reads the type from the archive header
tar -xf backup.tar.gz                 # extraction also auto-detects — no need to specify -z/-j/-J to extract
```

A permissions gotcha worth knowing: extracting as a regular user makes *you* the owner of the extracted files, while extracting as root preserves the original owner/group from the archive. Extended attributes (ACLs, SELinux contexts) are **not** preserved by default either — that needs `--acls` and `--selinux` explicitly added to the create/extract command.

---

## Transferring files over SSH

Three tools, same underlying secure channel (SSH), different shape:

| Tool | Shape | When |
|---|---|---|
| `sftp` | Interactive session (or one-shot) | Browsing a remote filesystem, uploading/downloading a handful of files |
| `scp` | One command, one transfer | Quick single-file/directory copy, scriptable |
| `rsync` | One command, but **only copies what changed** | Repeated syncs of the same tree — much faster on the second run |

### sftp — interactive, browsable

```bash
sftp remoteuser@remotehost
```
```
sftp> ls              # list remote directory (same commands as local shell: cd, mkdir, pwd)
sftp> lpwd             # the "l" prefix means "local" — lpwd, lcd, lls all act on YOUR machine instead
sftp> put localfile    # upload
sftp> get remotefile   # download
sftp> get -r remotedir # -r for a whole directory tree
sftp> exit
```
One-shot download without opening an interactive session (no equivalent one-liner for `put`, only `get`):
```bash
sftp remoteuser@remotehost:/path/to/file
```

### scp — one-line copy

```bash
scp localfile remoteuser@remotehost:/remote/path        # upload
scp remoteuser@remotehost:/remote/file localdir/          # download
scp -r localdir remoteuser@remotehost:/remote/path       # -r for directories
```
**RHEL 10 change worth knowing:** `scp` now uses the SFTP protocol underneath by default, rather than legacy SCP (which had a known code-injection vulnerability, CVE-2020-15778). `-O` forces the old legacy protocol if you specifically need it; an admin can disable legacy SCP entirely by creating `/etc/ssh/disable_scp`, in which case `-O` stops working too (SFTP-based transfer still does).

### rsync — only transfers what changed

```bash
rsync -av /var/log/ remoteuser@remotehost:/backup/log/
```
`-a` (archive mode) is really shorthand for several flags at once — recursive, preserve symlinks/permissions/timestamps/ownership — the "just do the sensible complete thing" default. `-v` adds progress detail. Run it again against the same destination and only the files that actually changed get sent — this is the entire reason to reach for `rsync` over `scp` for anything you'll repeat (a nightly backup, a deploy step), since a second run of `scp -r` re-copies everything from scratch every time.

```bash
rsync -avn /var/log/ remoteuser@remotehost:/backup/log/   # -n = dry run: shows what WOULD transfer, changes nothing
```
Always worth a dry run first against a destination you can't easily undo.

**The trailing-slash gotcha** — this is the single most common `rsync` mistake:
```bash
rsync -av /var/log  /backup     # NO trailing slash on source → creates /backup/log/...
rsync -av /var/log/ /backup     # trailing slash on source → copies CONTENTS directly into /backup/...
```
A source directory *with* a trailing slash means "the contents of this directory"; *without* the slash means "this directory itself." Bash tab-completion adds the trailing slash automatically, which is exactly why this mistake usually happens when typing the path out by hand instead.

---

## Which tool for which job

| Need | Tool |
|---|---|
| Bundle a directory tree into one file (backup, move as a unit) | `tar` |
| Shrink that bundle | `tar -z` (fast) / `-j` (smaller, slower) / `-J` (smallest, slowest) |
| Browse a remote filesystem interactively, grab a few files | `sftp` |
| One-off scripted copy, don't care about re-runs | `scp` |
| Repeated sync of the same tree — only send what changed | `rsync` |
