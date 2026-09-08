# Red Hat Certified System Administrator (RHCSA) V10

> Course tracker + notes index. Mirrors the section list from the course platform. Where a topic is already covered by an existing Linux note in this vault, it's linked directly instead of duplicated — RHCSA-specific nuance (RHEL vs. what I already know from Ubuntu/Debian) gets added inline in those notes or as a short addendum here.

Status key: ✅ done · 🔄 in progress · ⬜ not started yet

---

## Sections

1. ✅ Training Material & PDFs — course logistics, not a topic
2. ✅ Introduction to Course — course logistics, not a topic
3. ✅ [[01-getting-started-with-rhel|Getting Started with Red Hat Enterprise Linux]]
4. ✅ [[02-installing-rhel|Installing Red Hat Enterprise Linux]]
5. 🔄 [[03-accessing-the-command-line|Accessing the Command Line]] — *now learning*
6. ✅ Manage files from the Command Line → [[devops/01-linux/02-navigating-file-system|Navigating the Filesystem]], [[devops/01-linux/03-file-operations|File Operations & Text Manipulation]]
7. ✅ [[04-get-help-in-rhel|Get Help in Red Hat Enterprise Linux]]
8. ✅ Create, View & Edit Text Files → [[devops/01-linux/03-file-operations|File Operations & Text Manipulation]]
9. ✅ Manage Local Users & Groups → [[devops/01-linux/04-users-and-groups|Users & Groups]]
10. ✅ Control Access to Files → [[devops/01-linux/02-navigating-file-system|Navigating the Filesystem]] (permissions, chmod, chown)
11. ✅ Monitor & Manage Linux Processes → [[devops/01-linux/06-process-management|Process Management]]
12. ✅ Control Services & Daemons → [[devops/01-linux/07-systemd-and-services|systemd & Services]], [[devops/01-linux/08-writing-a-system-d-service|Writing a systemd Service]]
13. ✅ Configure & Secure SSH → [[devops/01-linux/14-basic-ssh-config|Basic SSH Config]], hardening cross-referenced in [[12-manage-network-security|manage-network-security]]
14. ✅ [[05-analyze-and-store-logs|Analyze & Store Logs]]
15. ✅ Manage Networking → [[devops/01-linux/13-network-fundamentals|Networking Fundamentals]] (concepts + ufw, now with an nmcli/NetworkManager addendum for the RHEL-native side)
16. ✅ Archive and Transfer Files → [[18-archiving-and-transferring-files|Archiving and Transferring Files]] (tar/gzip/bzip2/xz, sftp/scp/rsync)
17. ✅ Install & Update Software → [[devops/01-linux/05-package-management|Package Management]]
18. ✅ Access Linux File Systems → [[devops/01-linux/01-file-system|The Linux Filesystem]] *(directory tree)* + [[08-maintain-basic-storage|Maintain Basic Storage]] *(mounting, fstab, filesystem types)*
19. ✅ Improving Command Line Productivity Using Shell Scripts → [[devops/01-linux/12-bash-scripting|Bash Scripting]] + [[14-text-processing-and-searching|Text Processing & Searching]] (grep/find/wc/sort/cut, exam-drill depth)
20. ✅ [[06-tune-system-performance|Tune System Performance]] — builds on [[devops/01-linux/06-process-management|Process Management]]
21. ✅ Schedule Future Tasks → [[devops/01-linux/11-cron-jobs|Cron Jobs]] + [[17-scheduling-user-and-system-tasks|Scheduling User and System Tasks]] (at, systemd timers, systemd-tmpfiles)
22. ✅ [[07-manage-selinux-security|Manage SELinux Security]]
23. ✅ [[08-maintain-basic-storage|Maintain Basic Storage]]
24. ✅ [[09-maintain-advanced-storage|Maintain Advanced Storage]]
25. ✅ [[10-access-network-attached-storage|Access Network-Attached Storage]]
26. ✅ [[11-control-the-boot-process|Control the Boot Process]]
27. ✅ [[12-manage-network-security|Manage Network Security]]
28. ✅ [[13-running-containers|Running Containers]]
29. ✅ Relevant Resumes — career-prep material, not a technical topic
30. ✅ Interview Content — career-prep material, not a technical topic

1 section still unseen (31 total) — added here once it shows up in the course.

---

## In-depth notes written for this course

RHEL-specific topics with no prior coverage in the vault — written out in full (commands, tables, exam gotchas), not just stubs:

- [[01-getting-started-with-rhel|getting-started-with-rhel]]
- [[02-installing-rhel|installing-rhel]]
- [[03-accessing-the-command-line|accessing-the-command-line]]
- [[04-get-help-in-rhel|get-help-in-rhel]]
- [[05-analyze-and-store-logs|analyze-and-store-logs]]
- [[06-tune-system-performance|tune-system-performance]]
- [[07-manage-selinux-security|manage-selinux-security]] — the biggest conceptual gap vs. the Ubuntu/Debian notes elsewhere in this vault
- [[08-maintain-basic-storage|maintain-basic-storage]]
- [[09-maintain-advanced-storage|maintain-advanced-storage]]
- [[10-access-network-attached-storage|access-network-attached-storage]]
- [[11-control-the-boot-process|control-the-boot-process]] — includes the full lost-root-password recovery walkthrough
- [[12-manage-network-security|manage-network-security]] — firewalld, replacing ufw
- [[13-running-containers|running-containers]] — Podman, replacing Docker
- [[14-text-processing-and-searching|text-processing-and-searching]] — grep/find/wc/sort/cut/uniq, example-dense, the tools used to explore this vault itself
- [[17-scheduling-user-and-system-tasks|scheduling-user-and-system-tasks]] — `at` for one-time jobs, systemd timers + systemd-tmpfiles for system-level scheduling
- [[18-archiving-and-transferring-files|archiving-and-transferring-files]] — tar/compression, sftp/scp/rsync
- [[19-flatpak|flatpak]] — sandboxed application packaging, a genuinely different model from RPM
- [[20-rhel-image-mode|rhel-image-mode]] — bootc, RHEL 10's newest paradigm: the OS itself as an immutable, rollback-able container image

All known gaps from earlier are now closed — [[devops/01-linux/13-network-fundamentals|Networking Fundamentals]] got an nmcli/NetworkManager addendum for the RHEL-native side of interface config.

## Supplementary topics (found reviewing the official course books)

Cross-checked this folder against the actual RH124/RH134 course books (Red Hat System Administration I & II, RHEL 10.0 editions — `4484555-rh124v10.pdf` / `4484556-rh134v10.pdf` at the vault root) and found a handful of genuinely uncovered topics. Four became new standalone notes (above); three were small enough to fold directly into an existing note instead:

- **RHEL Lightspeed** (AI-assisted command-line help, new in RHEL 10) — added to [[04-get-help-in-rhel|get-help-in-rhel]]
- **Shell I/O redirection** (`>`, `>>`, `2>`, pipes, `tee`) — added to [[03-accessing-the-command-line|accessing-the-command-line]]
- **Building container images** (Containerfile, `podman build`) — added to [[13-running-containers|running-containers]], which previously only covered running pre-built images

---

## Practice

[[15-practice-exercises|Practice Exercises]] — self-test tasks, goal-only (no walkthroughs), matching the exam's performance-based format. Do these on an actual VM with the notes closed, not as a reading exercise.

[[16-practice-exercises-solutions|Practice Exercises — Solutions]] — worked, step-by-step answers to every task above. Check here only after attempting the task yourself — that's the entire point of the goal-only format.
