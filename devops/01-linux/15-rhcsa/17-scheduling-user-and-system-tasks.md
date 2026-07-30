# Scheduling User and System Tasks

> RHCSA V10 — added after reviewing the official RH134 course book (Red Hat System Administration II, RHEL 10.0), which covers this as its own two-chapter topic not previously in this folder.

Part of [[README|RHCSA V10]]. Recurring jobs (`cron`) already have a general note at [[devops/01-linux/11-cron-jobs|cron-jobs]] — this note covers what that one doesn't: **one-time** deferred jobs (`at`), and the RHEL-10-specific shift toward **systemd timers** for system-level scheduling, plus **systemd-tmpfiles** for managing temporary files.

---

## `at` — run something once, in the future

Cron is for *recurring* jobs. For a job that should run exactly once — "reset this firewall change in 10 minutes if I don't cancel it," "run this backup at 2am tonight" — `at` is the right tool, and it's installed and enabled by default via the `atd` daemon.

```bash
at now +5min < myscript.sh      # reads commands from a file via input redirection
at 21:00                          # interactive: type commands, then Ctrl+D on an empty line to finish
at teatime tomorrow                # at understands natural time specs: teatime = 16:00, midnight, noon, "+4 days", etc.
```

If you give a time with no date, `at` runs today if that time hasn't passed yet, or tomorrow if it has — worth testing with `atq` right after scheduling so you're not surprised which day it picked.

```bash
atq                    # list YOUR pending jobs (root sees everyone's)
at -c 5                # show the exact commands/environment stored in job number 5
atrm 5                 # cancel job number 5
```

```
$ atq
28   Mon May 19 05:13:00 2025 a student
```
Reading that line: `28` is the job number, then the scheduled date/time, then the **queue letter** (`a`–`z`, `A`–`Z` — later letters run at higher priority; you rarely need to think about this beyond the default `a`), then the owning user.

---

## systemd timers — replacing cron for system-level scheduling

Starting with RHEL 10, `systemd` timer units are the RHEL-idiomatic way most **system** scheduled tasks are defined, rather than a system-wide crontab entry — `cron` still exists and still works (and is still the right tool for a personal recurring job, per [[devops/01-linux/11-cron-jobs|cron-jobs]]), but built-in RHEL scheduling (log rotation, temp-file cleanup, package cache refresh) now runs through timer units.

A timer unit is a `.timer` file that triggers another unit (almost always a same-named `.service`) on a schedule:

```bash
systemctl list-units -t timer            # active/pending timers right now
systemctl list-unit-files -t timer        # every installed timer unit + whether it's enabled
systemctl status logrotate.timer          # when it last fired, when it fires next
systemctl enable --now logrotate.timer    # enable at boot AND start now, same two-step pattern as any other unit
```

```
$ systemctl status logrotate.timer
● logrotate.timer - Daily rotation of log files
     Active: active (waiting) since Wed ...
    Trigger: Fri 2025-05-30 00:48:43 UTC; 24h left
   Triggers: ● logrotate.service
```
"Trigger" is when it next fires; "Triggers:" (plural) is which service unit it fires when it does.

A timer unit's schedule lives in its `[Timer]` section:

```ini
[Unit]
Description=Run system activity accounting tool every 10 minutes

[Timer]
OnCalendar=*:00/10        # calendar-based: every 10 minutes, on the clock

[Install]
WantedBy=sysstat.service
```

| Directive | Meaning |
|---|---|
| `OnCalendar=` | Absolute/calendar schedule — `*:00/10` (every 10 min), `2025-07-* 12:35` (a specific date+time pattern), etc. |
| `OnBootSec=` | Relative to boot — `OnBootSec=15min` fires 15 minutes after startup |
| `OnUnitActiveSec=` | Relative to the *last time this same unit ran* — `OnUnitActiveSec=1d` fires 24h after the previous run, not on a fixed clock time |

**Never edit a unit file under `/usr/lib/systemd/system/` directly** — a package update overwrites it silently. Copy it to `/etc/systemd/system/` first (which takes precedence), edit the copy, then:
```bash
systemctl daemon-reload              # required after any unit file change, or systemd won't see it
systemctl enable --now <name>.timer
```

---

## systemd-tmpfiles — keeping temporary files from accumulating forever

Lots of services and scripts assume certain directories under `/tmp` or `/run` already exist, and without cleanup, `/tmp` fills up with stale data over a long-running system's lifetime. `systemd-tmpfiles` handles both problems — creating expected temp locations at boot, and periodically purging old files — driven by config files rather than ad-hoc cleanup scripts.

```bash
systemctl status systemd-tmpfiles-clean.timer     # the timer that drives periodic cleanup (daily, 15min after boot by default)
systemd-tmpfiles --clean /etc/tmpfiles.d/tmp.conf  # run a clean pass against one config file right now, for testing
systemd-tmpfiles --create /etc/tmpfiles.d/myapp.conf   # create what a config file specifies, right now
```

Config file syntax (`man tmpfiles.d`): `Type Path Mode UID GID Age Argument`

```
d /run/myapp     0755 root root -     # create the dir if missing; never auto-purged (no age given)
D /home/student  0700 student student 1d   # create if missing; purge ALL contents older than 1 day
q /tmp           1777 root root 5d    # like 'd', but specifically for the shared /tmp convention
L /run/link      -    root root -     /etc/fstab   # create a symlink instead of a directory
```
`d` vs `D`: lowercase only creates the directory if missing and leaves existing contents alone; uppercase actively removes contents older than the given age. Getting this distinction backwards is the easy mistake — `D` on a directory you didn't mean to prune can quietly delete real data.

**Three config locations, in override order** — same precedence pattern as systemd units generally:

| Location | Purpose |
|---|---|
| `/usr/lib/tmpfiles.d/*.conf` | Shipped by RPM packages — **never edit directly**, a package update overwrites it |
| `/run/tmpfiles.d/*.conf` | Volatile, daemon-managed at runtime |
| `/etc/tmpfiles.d/*.conf` | **Admin overrides go here** — same filename as a shipped config takes precedence over it |

---

## Which tool for which job

| Need | Tool |
|---|---|
| Run something once, at a specific future time, as yourself | `at` |
| Recurring job, personal (yours specifically) | `cron` via `crontab -e` — see [[devops/01-linux/11-cron-jobs|cron-jobs]] |
| Recurring **system-level** task, RHEL-idiomatic | a `.timer` unit |
| Make sure a directory/symlink exists at boot, or gets pruned over time | `systemd-tmpfiles` |
