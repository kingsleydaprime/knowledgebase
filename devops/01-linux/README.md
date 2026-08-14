# Linux

A map of the Linux notes in this folder, in reading order — the day-to-day OS fundamentals every other devops topic (Docker, cloud, VPS deployment, and the RHCSA cert track) assumes as background. No reading order existed here before this pass; this one is newly authored, not pulled from a prior doc, so treat it as a reasonable default rather than gospel.

## Reading order

1. [[01-file-system|file-system]] — **[Beginner]** — "everything is a file," the directory tree, how Linux represents devices/processes/sockets
2. [[02-navigating-file-system|navigating-file-system]] — **[Beginner]** — the commands you'll use every single day, hands-on
3. [[03-file-operations|file-operations]] — **[Beginner]** — creating, editing, and manipulating files/text from the terminal
4. [[04-users-and-groups|users-and-groups]] — **[Beginner]** — Linux as a multi-user system from day one, and how permissions/ownership follow from that
5. [[05-package-management|package-management]] — **[Beginner]** — installing software via a package manager instead of a downloaded installer
6. [[06-process-management|process-management]] — **[Intermediate]** — every running program is a process; inspecting and controlling them
7. [[07-systemd-and-services|systemd-and-services]] — **[Intermediate]** — how background programs (nginx, postgres, ssh) are managed as services
8. [[08-writing-a-system-d-service|writing-a-system-d-service]] — **[Intermediate]** — writing your own service unit file (companion note to the one above)
9. [[09-symbolic-links|symbolic-links]] — **[Beginner]** — pointers to another file/directory, and how they differ from a hard link
10. [[10-environment-variables|environment-variables]] — **[Beginner]** — variables available system-wide to any process
11. [[11-cron-jobs|cron-jobs]] — **[Intermediate]** — scheduling commands to run automatically
12. [[12-bash-scripting|bash-scripting]] — **[Intermediate]** — automating the commands above into reusable scripts, plus `set -euo pipefail` and heredocs
13. [[17-logs-and-journald|logs-and-journald]] — **[Intermediate]** — reading the machine's own account of what happened: `journalctl`, where each distro keeps its log files, making the journal survive a reboot, and stopping logs filling the disk
14. [[16-sed-and-awk|sed-and-awk]] — **[Intermediate]** — transforming text rather than just finding it: line-range extraction, substitution, and column/aggregate processing
15. [[18-disks-and-filesystems|disks-and-filesystems]] — **[Intermediate]** — partition → format → mount, `fstab` by UUID, the full-disk emergency (`df -i`, `lsof +L1`), and LVM for storage you can grow
16. [[19-the-boot-process|the-boot-process]] — **[Intermediate]** — firmware → GRUB → kernel → systemd, which handoff each symptom points at, and getting into rescue mode when a bad `fstab` line stops the boot
17. [[13-network-fundamentals|network-fundamentals]] — **[Intermediate]** — the networking concepts you need before SSH makes sense
18. [[14-basic-ssh-config|basic-ssh-config]] — **[Intermediate]** — remotely controlling another machine over an encrypted session — how you'll access every server/cloud instance you ever deploy to
19. [[20-firewalls-and-hardening|firewalls-and-hardening]] — **[Intermediate]** — `ss -tulpn` before any rule, ufw and firewalld, keys-only SSH, AppArmor vs SELinux, and the ten-minute baseline for any public box

> **On the numbering:** file numbers ran out of order once `15-` was taken by the RHCSA folder, and notes 16–20 were appended as they were written. **The list above is the reading order**; the filename prefixes are just unique IDs. Renaming them would break wikilinks across the vault for no reader benefit.

## Next layer — RHCSA certification track

[[devops/01-linux/15-rhcsa/README|15-rhcsa/]] — a structured cert-prep course built on top of everything above, going deeper on RHEL specifics (SELinux contexts, firewalld zones and rich rules, Podman, Stratis, image mode).

Notes 17–20 above were added (Aug 2026) because several genuinely distro-neutral topics — logs, storage, boot, firewalls — existed *only* inside that cert track, so anyone reading this folder start-to-finish never met them. The RHCSA notes remain the deep versions and each new note hands off to its sibling; what's here is the Ubuntu/Debian-first core everyone needs regardless of distro.

## Also in this folder (not part of the numbered sequence)

- [[linux-reference|linux-reference]] — a comprehensive standalone reference guide, meant for lookup rather than linear reading
- [[redis-fixing|redis-fixing]] — an incident note from a real debugging session, not a course topic
- `sysinfo.sh` — a script, not a note

## Related
- [[devops/README|devops curriculum map]]
