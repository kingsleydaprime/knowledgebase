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
12. [[12-bash-scripting|bash-scripting]] — **[Intermediate]** — automating the commands above into reusable scripts
13. [[13-network-fundamentals|network-fundamentals]] — **[Intermediate]** — the networking concepts you need before SSH makes sense
14. [[14-basic-ssh-config|basic-ssh-config]] — **[Intermediate]** — remotely controlling another machine over an encrypted session — how you'll access every server/cloud instance you ever deploy to

## Next layer — RHCSA certification track

[[devops/01-linux/15-rhcsa/README|15-rhcsa/]] — a structured cert-prep course built on top of everything above, with RHEL-specific nuance (SELinux, firewalld, Podman) layered on top of the Ubuntu/Debian-flavored fundamentals in this folder.

## Also in this folder (not part of the numbered sequence)

- [[linux-reference|linux-reference]] — a comprehensive standalone reference guide, meant for lookup rather than linear reading
- [[redis-fixing|redis-fixing]] — an incident note from a real debugging session, not a course topic
- `sysinfo.sh` — a script, not a note

## Related
- [[devops/README|devops curriculum map]]
