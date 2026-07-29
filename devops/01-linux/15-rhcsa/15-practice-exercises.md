# RHCSA Practice Exercises

> RHCSA V10

Part of [[README|RHCSA V10]]. Goal-only tasks, no walkthroughs — this mirrors the actual exam format: you're told the end state you need, not the commands to get there. Each task has a **Verify** line so you can confirm you actually got there, not just that you think you did.

## How to use this

- Run these on a **real VM** (RHEL, Rocky, or Alma — identical for this purpose), not a container, not the exam VM.
- Close the notes before attempting a task. Open them only after — to check yourself, or after a genuine stuck point, not mid-attempt.
- Time yourself. The real exam gives you ~2.5 hours for the full task list — if a single task like these is taking you 20+ minutes, that's the signal to go re-read the relevant note, not to keep guessing.
- Snapshot the VM before starting (or reinstall between sessions) — several tasks below deliberately break things, and you don't want leftover damage confusing a later exercise.
- Reboot after any task that claims persistence ("survives a reboot") — the exam grades the machine cold, after your session ends. A fix that only works until the next reboot is not a passing fix.

---

## Users, Groups & Permissions

1. Create a group `devteam`. Create a user `alice` whose primary group is `devteam`, secondary group `wheel`, shell `/bin/bash`, and whose account expires in 90 days from today.
   **Verify:** `id alice`, `chage -l alice`

2. Create a user `bob` who can authenticate via SSH key only — no usable password login at all.
   **Verify:** `sudo passwd -S bob` shows locked; attempt an SSH login with a password and confirm it's rejected while key-based auth still works.

3. A shared directory `/srv/teamdocs` needs: group ownership `devteam`, any file created inside it inherits that group automatically (regardless of the creating user's primary group), and any user in `devteam` can delete only their *own* files, not each other's.
   **Verify:** log in as two different `devteam` members, have each create a file, confirm group ownership on both, then confirm neither can delete the other's file.

4. `carol` should be able to run `systemctl restart httpd` and nothing else as root, without a password prompt.
   **Verify:** as `carol`, run `sudo systemctl restart httpd` (should work, no prompt) then `sudo systemctl restart sshd` (should be refused).

---

## Storage

5. A second disk was just attached to the VM. Partition it, format it XFS, and mount it persistently at `/data` — must survive a reboot.
   **Verify:** `reboot`, then `df -h /data` and `mount | grep /data`

6. Build an LVM stack from a raw disk: a volume group `appvg`, a 2GB logical volume `applv` inside it, formatted ext4, mounted at `/app`.
   **Verify:** `lsblk`, `lvs`, `df -h /app`

7. `/app` from the previous task is now full. Grow it by 1GB without unmounting it or losing data.
   **Verify:** `df -h /app` shows the new size, and a file written before the resize still exists and is intact.

8. Create a 512MB swap file (not a partition) and activate it persistently.
   **Verify:** `swapon --show`, reboot, `swapon --show` again.

9. Given an NFS export `nfs-server:/exports/shared`, mount it at `/mnt/shared` on demand (not at boot) — nothing should mount until something actually accesses that path, and it should unmount itself again after being idle.
   **Verify:** `mount | grep shared` shows nothing right after boot; `ls /mnt/shared` triggers a mount; wait past the idle timeout and confirm it's gone from `mount` again without you touching it.

---

## Processes, Services & Boot

10. A runaway process is consuming CPU. Find it by name, lower its scheduling priority without killing it, and confirm the change.
    **Verify:** `ps -eo pid,ni,comm | grep <name>` shows the new niceness.

11. Write a systemd unit for a custom script at `/usr/local/bin/heartbeat.sh` that starts on boot, restarts automatically if it crashes, and runs as a dedicated non-root user.
    **Verify:** `systemctl status heartbeat`, then `kill` the process manually and confirm systemd restarts it on its own.

12. The system currently boots to a graphical desktop. Change it to boot to a text-only multi-user prompt by default, without uninstalling the desktop environment.
    **Verify:** `systemctl get-default`, then reboot and confirm no GUI comes up.

13. Simulate a lost root password (set one, then "forget" it) and recover access without reinstalling the system.
    **Verify:** successful root login afterward with a password you just set, and confirm the system isn't stuck denying access to files due to a skipped SELinux step.

14. A custom `.mount` unit or fstab entry you write is deliberately broken (bad UUID, bad options — your choice). Reboot and get the system back to a normal login prompt, then fix the entry properly.
    **Verify:** clean reboot afterward with no manual intervention needed.

---

## Networking & Firewall & SSH

15. Configure a static IP, gateway, and DNS server on one interface using the RHEL-native tool — must survive a reboot.
    **Verify:** reboot, then `ip addr show <iface>` and `cat /etc/resolv.conf`.

16. A web server is listening on port 8080. Open it in the firewall persistently, confirm it's reachable from another machine, then confirm the rule is still active after `firewall-cmd --reload` on its own (not just after your `--add-port` command).
    **Verify:** `firewall-cmd --list-ports` before and after a manual `--reload`, plus an actual connection test with `curl` or `nc` from another host.

17. Move sshd to a non-default port. It must actually be reachable on the new port from another machine — not just "sshd says it's listening."
    **Verify:** `ss -tlnp | grep sshd` on the server, then a real SSH connection attempt from a different machine on the new port. If it fails, check all three layers this touches (there are three).

18. Restrict SSH so `root` cannot log in directly at all, but a regular user can still log in and `sudo` to root.
    **Verify:** attempt a direct `ssh root@host` (should fail) then `ssh regularuser@host` followed by `sudo -i` (should succeed).

---

## SELinux

19. Move your web server's document root from the default location to `/web`. Get it serving files again — DAC permissions are already correct, something else is blocking it.
    **Verify:** `curl localhost` returns your content, `ls -Z /web` shows the correct context, and `ausearch -m avc -ts recent` shows no new denials after the fix.

20. Put SELinux in permissive mode temporarily, reproduce a denial, then go back to enforcing — but figure out what the fix *would have needed to be* using the log from while it was permissive.
    **Verify:** `ausearch -m avc -ts recent` (or `sealert`) shows the denial that occurred while permissive; you can state the exact `semanage`/`setsebool` command that would have prevented it.

21. A service needs to make an outbound network connection that its SELinux policy blocks by default. Allow it, persistently, without disabling SELinux and without writing a custom policy module.
    **Verify:** `getsebool <name>` shows `on`, reboot, `getsebool <name>` still shows `on`.

---

## Logging & Performance

22. Make the systemd journal persistent across reboots on a system where it currently isn't.
    **Verify:** note a specific log line, reboot, confirm `journalctl -b -1` still shows it.

23. Find every "Failed password" SSH attempt from the last 24 hours and report the count and the distinct source IPs involved, using only journal/log tools — no writing anything to a file first.
    **Verify:** your one-line pipeline output vs. manually eyeballing the log.

24. Apply a system tuning profile appropriate for a database server doing constant heavy I/O, and confirm it actually took effect (not just that you ran the command).
    **Verify:** `tuned-adm active` after a reboot.

---

## Software & Containers

25. Install a package, then find every file it put on the filesystem — not by guessing, by asking the package manager directly.
    **Verify:** cross-check one or two of the listed files actually exist at those paths.

26. Roll back a package to a specific earlier version already available in the local package cache, without a full `dnf history undo` of unrelated transactions.
    **Verify:** the installed version matches the one you targeted.

27. Run a container from an image, publish a port, and make it start automatically on boot **as a non-root user**, surviving that user logging out.
    **Verify:** reboot the VM with no active login session for that user, then confirm the container is running and reachable.

---

## Text Processing (closed-book — this category is the real test of [[14-text-processing-and-searching|text-processing-and-searching]])

28. From `/etc/passwd`, list only accounts with UID ≥ 1000, sorted by UID, showing just username and UID.

29. Count how many `.log` files exist anywhere under `/var/log`, recursively, in one command.

30. Given a directory of mixed files, find every file larger than 50MB that hasn't been modified in over 30 days, and list their sizes and paths without deleting anything yet.

31. From an access log, produce the 5 most frequently occurring source IPs, most frequent first, in a single pipeline.

32. Strip a config file down to only its real, active settings — no comment lines, no blank lines — without modifying the original file.

---

## A full mixed drill (closest thing to the real exam)

33. Set a 45-minute timer. On a fresh VM snapshot: create a user with a group and sudo scoped to one specific command, partition and mount a second disk persistently at `/opt/data`, open a custom application port in the firewall persistently, and make an SELinux boolean change survive a reboot. Reboot once at the end and confirm all four are still true in one pass — don't check them one at a time as you go.

This last one is deliberately the format that matters most: multiple unrelated tasks, a hard time limit, and a single reboot at the end to catch anything that only "worked" temporarily.
