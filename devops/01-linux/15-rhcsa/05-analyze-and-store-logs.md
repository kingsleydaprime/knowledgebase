# Analyze & Store Logs

> RHCSA V10

Part of [[README|RHCSA V10]]. **These aren't two independent, parallel loggers** — `systemd-journald` is the actual collection point for everything (kernel messages, early boot output, every daemon's stdout/stderr, and syslog events), and `rsyslog` sits *downstream* of it, reading from the journal (via its `imjournal` module) to sort messages into the traditional text files under `/var/log/`. journald's own copy is structured/binary and — by default — **not persistent across reboots**; rsyslog's text files in `/var/log/` are what actually survives long-term, which is exactly why "make the journal persistent" (below) is worth doing rather than relying on rsyslog's copy alone.

---

## journald / journalctl

Every unit systemd manages sends its output to the journal — this is *the* log source on a modern RHEL box, including for services with no separate log file of their own.

```bash
journalctl                        # entire journal, oldest first
journalctl -e                     # jump to the end (newest entries) — like tail
journalctl -f                     # follow live, like tail -f
journalctl -r                     # reverse order, newest first
```

### Filtering — this is where journalctl earns its keep

```bash
journalctl -u sshd                 # only this systemd unit's logs
```
```
Jul 30 08:14:02 host sshd[1842]: Server listening on 0.0.0.0 port 22.
Jul 30 08:41:17 host sshd[2093]: Accepted publickey for kingsley from 10.0.0.5 port 51422 ssh2
Jul 30 09:02:44 host sshd[2211]: Failed password for invalid user admin from 203.0.113.9 port 39102 ssh2
```
Each line is exactly what it would've looked like in `/var/log/secure` — `journalctl -u <unit>` is the modern, no-separate-log-file-needed replacement for "grep the right log file for this service's name."
```bash
journalctl -u sshd -f              # follow just this unit live
journalctl -b                      # only since the current boot
journalctl -b -1                   # the PREVIOUS boot — critical for "why did it crash last night"
journalctl --list-boots            # see all boots the journal has recorded, with their offsets
journalctl --since "2026-07-23 09:00" --until "2026-07-23 10:00"
journalctl --since yesterday
journalctl -k                      # kernel messages only (like dmesg, but persistent across reboots if journal is persistent)
journalctl -p err                  # priority filter — err and everything more severe
journalctl -p warning..err         # priority range
journalctl -o json-pretty          # structured output — useful for scripting/piping to jq
journalctl -o verbose               # every indexed field for each entry, not just the summary line — see below
```

### Filtering by field — more precise than `-u` when you need it

Every journal entry carries structured fields, not just a text message — `journalctl -o verbose` reveals them (`_PID`, `_UID`, `_COMM`, `_EXE`, `_SYSTEMD_UNIT`, and more; the full list is in `systemd.journal-fields(7)`). You can filter directly on any of them, and combine several at once (combining fields is an implicit AND):

```bash
journalctl _PID=1                            # everything logged by PID 1 specifically (systemd itself)
journalctl _UID=81                            # everything logged by a specific UID
journalctl _SYSTEMD_UNIT=sshd.service _PID=2188   # narrow to one unit AND one specific process instance of it
```
This is the tool for "which specific process instance logged this," in a way `-u <unit>` alone can't answer once a unit has restarted several times with different PIDs.

Priority levels, from most to least severe (numeric values you'll see in `-p` output or scripting):

| # | Name |
|---|---|
| 0 | emerg |
| 1 | alert |
| 2 | crit |
| 3 | err |
| 4 | warning |
| 5 | notice |
| 6 | info |
| 7 | debug |

### Persistent vs. volatile journal storage

By default on a lot of installs, the journal only lives in `/run/log/journal` — **RAM-backed, wiped on every reboot**. For a real server you almost always want it to survive reboots:

```bash
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
```

Or set it explicitly in `/etc/systemd/journald.conf`:
```ini
[Journal]
Storage=persistent
```

This exact task — "make the journal persistent" — is a classic RHCSA-style exam item because it's a one-liner if you know it and a total guess if you don't.

### Managing journal size

```bash
journalctl --disk-usage            # how much space the journal is currently using
journalctl --vacuum-size=500M      # shrink journal down to this size, deleting oldest entries
journalctl --vacuum-time=2weeks    # delete anything older than 2 weeks
```

---

## rsyslog — the text-file layer

Still installed alongside journald on RHEL and responsible for the traditional `/var/log/*` text files a lot of tools and admins still expect.

```bash
/etc/rsyslog.conf              # main config
/etc/rsyslog.d/*.conf          # drop-in configs, same pattern as sudoers.d/logrotate.d
```

Rules follow a `facility.priority   destination` format:
```
mail.*                          /var/log/maillog
*.info;mail.none;cron.none      /var/log/messages
authpriv.*                      /var/log/secure
cron.*                          /var/log/cron
```

Common log files this produces on RHEL:

| File | Contents |
|---|---|
| `/var/log/messages` | General system messages — the default catch-all |
| `/var/log/secure` | Authentication and authorization events — `sudo`, SSH logins, `su` |
| `/var/log/cron` | Cron job execution log |
| `/var/log/maillog` | Mail subsystem |
| `/var/log/boot.log` | Boot-time service startup messages |

```bash
systemctl restart rsyslog      # apply config changes
```

---

## logrotate — keeping logs from eating the disk

Runs daily via a systemd timer (`logrotate.timer`), rotating/compressing/deleting old log files per rules.

```bash
/etc/logrotate.conf            # global defaults
/etc/logrotate.d/*             # per-service overrides — most packages drop one of these in on install
```

Example drop-in:
```
/var/log/myapp/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    size 50M
}
```

| Directive | Meaning |
|---|---|
| `weekly` / `daily` / `monthly` | Rotation frequency |
| `rotate N` | Keep N old rotated copies before deleting the oldest |
| `compress` | Gzip rotated files |
| `missingok` | Don't error if the log file doesn't exist |
| `notifempty` | Skip rotation if the log is empty |
| `size 50M` | Rotate once the file crosses this size, regardless of schedule |

```bash
logrotate -f /etc/logrotate.conf     # force a rotation run right now — useful for testing a rule without waiting for the timer
logrotate -d /etc/logrotate.conf     # dry run, shows what WOULD happen
```

---

## A note on timestamps

Logs are only as useful as their timestamps are accurate. Worth a quick sanity check with `timedatectl` and, if **NTP (Network Time Protocol)** sync via `chronyd` is off, logs across a fleet of machines can drift out of correlation with each other — a real problem when you're trying to line up an error across a web server and a database server, where "which happened first" is the entire question you're trying to answer.

```bash
timedatectl                    # current time, timezone, whether NTP sync is active
chronyc sources                # what time servers chronyd is actually syncing against
```
