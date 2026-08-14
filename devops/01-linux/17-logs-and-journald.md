# Logs and journald

**[Intermediate]** — reading the machine's own account of what happened. The first thing you do when something breaks, and the thing nobody teaches you.

## The kid version first

A Linux box keeps a diary. Several diaries, actually, written by different people who don't fully agree on where the diary lives.

Everything the kernel and every service says goes to the **journal** (`journalctl`), a binary database managed by systemd. Some of it *also* gets copied into plain text files under `/var/log/` by an older daemon (rsyslog), because plain text is easy to grep, ship, and rotate. Both are looking at the same events; they're two views, not two sources.

When a service won't start, the answer is almost always already written down. Most people just never learn to read it.

## The one command

```bash
journalctl -u nginx -n 50 --no-pager       # last 50 lines for one unit
journalctl -u nginx -f                      # follow, like tail -f
journalctl -u nginx --since "10 min ago"    # time-bounded
journalctl -p err -b                        # errors only, this boot
journalctl -b -1                            # the PREVIOUS boot — for crashes
journalctl -k                               # kernel messages (dmesg equivalent)
```

If you learn one, learn `journalctl -u <service> -n 50 --no-pager`. It answers "why won't this start" far more often than any amount of staring at config files. `systemctl status` shows you the last ~10 lines for free, which is often enough — [[devops/01-linux/07-systemd-and-services|systemd & services]].

`-b -1` deserves special mention: when a machine hard-crashes or reboots unexpectedly, the interesting logs are in the *previous* boot, and looking at the current one shows you a clean startup and nothing else.

## Where things actually are

| | Ubuntu/Debian | RHEL/Fedora |
|---|---|---|
| Journal | `journalctl` | same |
| Auth/sudo/ssh | `/var/log/auth.log` | `/var/log/secure` |
| General system | `/var/log/syslog` | `/var/log/messages` |
| Package manager | `/var/log/apt/` | `/var/log/dnf.log` |
| Per-service | `/var/log/nginx/`, `/var/log/postgresql/` | same idea |

Note the auth log difference — `auth.log` vs `secure` — because it's the file you want when investigating failed SSH logins, and copying a command from the wrong distro's tutorial silently gives you nothing.

Services that write their own files (nginx, postgres) bypass the journal entirely. If `journalctl -u nginx` is empty but nginx is clearly serving, its access/error logs are in `/var/log/nginx/`.

## The journal is volatile by default on some systems

This catches people out badly: on a default Debian/Ubuntu install the journal may live in `/run/log/journal`, which is **tmpfs — wiped on reboot**. You investigate a crash, reboot to recover, and the evidence is gone.

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
journalctl --disk-usage
```

Do this on any machine you might need to debug after the fact — which is all of them.

## Keeping logs from filling the disk

A full disk from unrotated logs is a genuinely common outage, and a confusing one because the application error ("cannot write") has nothing to do with logging.

```bash
journalctl --vacuum-size=500M        # trim now
journalctl --vacuum-time=30d
```

Persistently, set `SystemMaxUse=500M` in `/etc/systemd/journald.conf`. For plain-text logs, **logrotate** handles it (`/etc/logrotate.d/`) — rotating, compressing, and deleting old files on a schedule. Anything writing its own log file without a logrotate entry is a disk-space incident waiting for a busy week.

```bash
df -h /var                            # the check to run when anything is "mysteriously" broken
du -sh /var/log/* | sort -rh | head
```

## Reading logs well

- **Start at the first error, not the last.** Failures cascade; the final message is usually a symptom of something 40 lines earlier.
- **Note the timestamp and compare it to when the problem started.** A scary-looking error from three days ago is not your outage.
- **Journal timestamps are in local time by default**, but many application logs use UTC. Mixing them up while correlating events across services wastes hours — `journalctl --utc` puts everything in one frame.
- **`-p err` first, then widen.** Cut to errors, then go back for context once you know roughly where to look.

## Key insight

The machine already told you what went wrong. `journalctl -u <service> -n 50` before you change a single config line — and make the journal persistent *before* you need it, because the default on some distros throws away exactly the logs you'll want after a crash.

## Related
- [[devops/01-linux/07-systemd-and-services|systemd & services]] — where these logs come from
- [[devops/01-linux/15-rhcsa/05-analyze-and-store-logs|RHCSA: Analyze & Store Logs]] — the deep version: field filtering, rsyslog rules, logrotate config, journal storage
- [[devops/10-observability/README|Observability]] — what happens when one machine's logs become a hundred machines' logs
- [[devops/01-linux/16-sed-and-awk|sed & awk]] — for the plain-text half
