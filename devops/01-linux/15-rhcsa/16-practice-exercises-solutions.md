# RHCSA Practice Exercises — Solutions

> Worked, step-by-step answers to every task in [[15-practice-exercises|practice-exercises]]. Attempt each one closed-book first — the entire point of the goal-only format is training yourself to derive the command from the *end state required*, the way the actual exam grades you. Commands below assume RHEL/Rocky/Alma; adjust device names (`/dev/sdb`, interface names) to match your VM.

---

## Users, Groups & Permissions

**1. `alice`: primary group devteam, secondary wheel, 90-day expiry**
```
groupadd devteam
useradd -g devteam -G wheel -s /bin/bash -e $(date -d "+90 days" +%Y-%m-%d) alice
passwd alice
```
`-e` sets **account** expiration (a hard date), which is what `chage -l` reports as "Account expires" — don't confuse this with `-M` (password max age), which is a different field entirely.

**2. `bob`: SSH key only, no usable password**
```
useradd bob
mkdir -p /home/bob/.ssh && chmod 700 /home/bob/.ssh
# place bob's public key in /home/bob/.ssh/authorized_keys
chmod 600 /home/bob/.ssh/authorized_keys
chown -R bob:bob /home/bob/.ssh
passwd -l bob
```
`passwd -l` prepends `!` to the password hash, invalidating password auth entirely while leaving key-based auth (which never consults that field) untouched. `passwd -S bob` reports `L` for locked.

**3. `/srv/teamdocs`: group-inherit + own-file-only delete**
```
mkdir -p /srv/teamdocs
chgrp devteam /srv/teamdocs
chmod 3770 /srv/teamdocs
```
`3770` = setgid (`2000`, new files inherit the directory's group regardless of the creator's primary group) + sticky bit (`1000`, restricts deletion inside the directory to the file's owner, the directory's owner, or root) + `770` (rwx for owner/group, nothing for others). `ls -ld` should show `drwxrws-t`.

**4. `carol`: passwordless sudo scoped to one command**
```
visudo -f /etc/sudoers.d/carol
```
```
carol ALL=(root) NOPASSWD: /usr/bin/systemctl restart httpd
```
Use the full binary path (`/usr/bin/systemctl`, confirm with `which systemctl`) — sudoers matches the exact command line, so anything else (including `systemctl restart sshd`) is refused by default.

---

## Storage

**5. Second disk → XFS → persistent `/data`**
```
parted /dev/sdb --script mklabel gpt mkpart primary 0% 100%
mkfs.xfs /dev/sdb1
mkdir -p /data
blkid /dev/sdb1
```
Add to `/etc/fstab` (UUID, not the device name — device names can shift across reboots):
```
UUID=<uuid-from-blkid>  /data  xfs  defaults  0 0
```
```
mount -a
```

**6. LVM stack: `appvg` → `applv` (2GB, ext4) → `/app`**
```
pvcreate /dev/sdc
vgcreate appvg /dev/sdc
lvcreate -L 2G -n applv appvg
mkfs.ext4 /dev/appvg/applv
mkdir -p /app
```
`/etc/fstab`: `/dev/appvg/applv  /app  ext4  defaults  0 0`, then `mount -a`.

**7. Grow `/app` by 1GB, online**
```
lvextend -L +1G /dev/appvg/applv
resize2fs /dev/appvg/applv
```
`resize2fs` grows an already-mounted ext4 filesystem live — no unmount needed. (If this were XFS instead, the equivalent is `xfs_growfs /app`, which also works mounted — XFS actually *requires* being mounted to grow.)

**8. 512MB swap file, persistent**
```
dd if=/dev/zero of=/swapfile bs=1M count=512
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```
`/etc/fstab`: `/swapfile  none  swap  sw  0 0`. The `chmod 600` before `mkswap` matters — a world-readable swap file is a real information-disclosure risk (swap can contain anything that was in memory, including secrets).

**9. On-demand NFS mount via autofs**
```
dnf install -y autofs
```
`/etc/auto.master.d/shared.autofs`:
```
/mnt  /etc/auto.shared
```
`/etc/auto.shared`:
```
shared  -fstype=nfs  nfs-server:/exports/shared
```
```
systemctl enable --now autofs
```
Nothing mounts until something touches `/mnt/shared` (autofs intercepts the access and mounts on demand), and it unmounts again after the idle timeout (`--timeout=`, default 300s, settable per-map or in `/etc/autofs.conf`) — this is exactly what a static `/etc/fstab` entry can't do.

---

## Processes, Services & Boot

**10. Renice a runaway process without killing it**
```
ps -eo pid,ni,comm | grep <name>
renice -n 10 -p <pid>
```
Positive value = *lower* priority (nicer to other processes), not higher — a common mix-up.

**11. systemd unit: boot start, auto-restart, dedicated user**
```
useradd -r -s /sbin/nologin heartbeat
```
`/etc/systemd/system/heartbeat.service`:
```ini
[Unit]
Description=Heartbeat script

[Service]
ExecStart=/usr/local/bin/heartbeat.sh
Restart=always
User=heartbeat

[Install]
WantedBy=multi-user.target
```
```
systemctl daemon-reload
systemctl enable --now heartbeat
```
Kill the PID (`kill <pid>`) and `systemctl status heartbeat` should show it restarted with a fresh PID and an incremented restart count.

**12. Default to text-only boot, GUI still installed**
```
systemctl set-default multi-user.target
```
This only changes the **default target systemd boots into** — the graphical environment and its packages are untouched, and you can still `systemctl isolate graphical.target` manually any time. `systemctl get-default` confirms the change.

**13. Recover a "lost" root password**
At the GRUB menu, highlight the boot entry, press `e`, find the line starting with `linux` (or `linux16`), append `rd.break` at the end, then `Ctrl+X` to boot into the rescue shell:
```
mount -o remount,rw /sysroot
chroot /sysroot
passwd root
touch /.autorelabel
exit
exit
```
`/.autorelabel` is the step people forget — the rescue environment doesn't run with SELinux fully active, so the password file gets rewritten with the wrong (or missing) security context. Without forcing a full relabel on the next real boot, SELinux denies logins against the mismatched context even though the password itself is correct.

**14. Recover from a broken fstab/mount unit**
A bad `/etc/fstab` entry (or `.mount` unit) drops the boot into **emergency mode** automatically, prompting for the root password. If it doesn't (some broken unit configurations boot further before failing), force it by appending `systemd.unit=emergency.target` at the GRUB kernel line.
```
mount -o remount,rw /
vi /etc/fstab   # fix or comment out the bad line
systemctl daemon-reload
reboot
```

---

## Networking & Firewall & SSH

**15. Static IP/gateway/DNS via the RHEL-native tool**
```
nmcli con show
nmcli con mod "<connection-name>" ipv4.method manual \
  ipv4.addresses 192.168.1.50/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns 8.8.8.8
nmcli con up "<connection-name>"
```
`nmcli` writes to a persistent connection profile (unlike `ip addr add`, which is runtime-only) — this is the RHEL-native equivalent of what `netplan`/`/etc/network/interfaces` do elsewhere.

**16. Firewall: persistent port + confirm it survives a manual reload**
```
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --reload
```
Without `--permanent`, a rule lives only in the runtime configuration and disappears on the next `--reload` (or reboot) — this task specifically catches that mistake, since it asks you to reload *and then* check the rule is still there.

**17. Move sshd to a non-default port — the three layers**
```
# /etc/ssh/sshd_config
Port 2222
```
```
semanage port -a -t ssh_port_t -p tcp 2222
firewall-cmd --add-port=2222/tcp --permanent
firewall-cmd --reload
systemctl restart sshd
```
The three layers, in the order people usually forget them: (1) `sshd_config` itself, (2) **SELinux's port type** — `sshd` is only allowed to bind ports labeled `ssh_port_t`, so a new port needs to be added to that label via `semanage port`, and (3) **firewalld**. Missing any one of the three leaves it "listening" locally (`ss -tlnp` looks fine) but unreachable or refused.

**18. No direct root SSH, regular user + sudo still works**
```
# /etc/ssh/sshd_config
PermitRootLogin no
```
```
systemctl restart sshd
```
Confirm the regular user is in `wheel` (or another sudo-enabled group) so `sudo -i` still reaches root after logging in as themselves.

---

## SELinux

**19. Web doc root moved to `/web` — fix the context, not the permissions**
```
mkdir /web && cp -r /var/www/html/* /web/
# edit /etc/httpd/conf/httpd.conf: DocumentRoot "/web", and update the matching <Directory "/web"> block
semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"
restorecon -Rv /web
systemctl restart httpd
```
`semanage fcontext` writes the *rule* (persists across relabels); `restorecon` actually *applies* it to the existing files. Skipping `restorecon` is the classic mistake — the rule exists but the files on disk still carry the old (or default, unlabeled) context, so httpd is still denied.

**20. Permissive → reproduce → enforcing → identify the real fix**
```
setenforce 0
# reproduce the failing action here
ausearch -m avc -ts recent
setenforce 1
```
Read the `ausearch` (or `sealert -a /var/log/audit/audit.log`) output for the specific `scontext`/`tcontext`/`tclass` denied, and either state the exact boolean (`getsebool -a | grep <keyword>`) or the `semanage fcontext`/`restorecon` pair that would have prevented it — the deliverable here is the *diagnosis*, since permissive mode logs what would have been denied without actually blocking it.

**21. Persistent SELinux boolean for outbound connections**
```
getsebool -a | grep network_connect
setsebool -P httpd_can_network_connect on
```
The `-P` flag is what makes it persistent (writes to policy on disk); a bare `setsebool` without `-P` reverts on reboot — exactly what the verify step in the exercise is checking for.

---

## Logging & Performance

**22. Persistent systemd journal**
```
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
```
By default (`Storage=auto` in `journald.conf`), the journal only persists if `/var/log/journal` already exists — creating it is the entire fix; you don't need to touch `journald.conf` unless it's been explicitly set to `volatile`.

**23. Failed SSH logins in the last 24h — journal only, one pipeline**
```
journalctl -u sshd --since "-24 hours" | grep "Failed password" | wc -l
journalctl -u sshd --since "-24 hours" | grep "Failed password" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | sort -u
```
`--since "-24 hours"` filters at the journal level (fast, no full-log scan); `grep -oE` with an IP-shaped pattern plus `sort -u` gets the distinct source list in the same pass style.

**24. Tuned profile for heavy database I/O**
```
tuned-adm list
tuned-adm profile throughput-performance
```
`throughput-performance` is RHEL's recommended profile for sustained high I/O workloads like databases (as opposed to `latency-performance`, which trades some throughput for lower response-time variance). `tuned-adm active` after a reboot confirms it stuck — tuned profiles are persistent by default once set.

---

## Software & Containers

**25. Installed package's files, via the package manager**
```
dnf install -y httpd
rpm -ql httpd
```
`rpm -ql` (query, list files) is authoritative — it's reading the package's own manifest, not guessing from a filesystem scan.

**26. Downgrade to a specific cached version**
```
dnf list --showduplicates httpd
dnf downgrade httpd-<version>
```
Targeting an exact `package-version` with `dnf downgrade` only touches that package, unlike `dnf history undo <id>`, which reverts an entire transaction (potentially including unrelated packages installed in the same batch).

**27. Rootless container, boot-persistent, survives logout**
```
podman run -d --name myapp -p 8080:80 <image>
podman generate systemd --new --files --name myapp
mkdir -p ~/.config/systemd/user
mv container-myapp.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now container-myapp.service
loginctl enable-linger <username>
```
`loginctl enable-linger` is the piece this task is actually testing: a user's systemd `--user` instance normally dies the moment their last session ends, taking any user-level services with it. Linger keeps that user's systemd instance (and anything enabled under it) running headless, independent of any logged-in session — which is what makes "survives that user logging out" possible at all.

---

## Text Processing (closed-book)

**28. UID ≥ 1000, sorted by UID, username + UID**
```
awk -F: '$3>=1000 {print $1, $3}' /etc/passwd | sort -k2 -n
```

**29. Count of `.log` files under `/var/log`, recursive**
```
find /var/log -type f -name "*.log" | wc -l
```

**30. Files >50MB, unmodified 30+ days, size + path, no deletion**
```
find /path -type f -size +50M -mtime +30 -exec ls -lh {} \;
```

**31. Top 5 source IPs from an access log**
```
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -5
```

**32. Strip a config to active settings only, original untouched**
```
grep -vE '^\s*#|^\s*$' original.conf > active.conf
```
Redirecting to a *new* file (`active.conf`) rather than editing in place is what keeps the original untouched, as required.

---

## Full Mixed Drill

Task 33 is exercises 4, 5, 16, and 21 combined under a single 45-minute timer with one reboot at the end — there's no new technique here, just the discipline of doing all four without checking each one immediately:

1. **User + scoped sudo** — combine solution 1 (user/group creation) with solution 4's `/etc/sudoers.d/` drop-in.
2. **Persistent partition at `/opt/data`** — solution 5, substituting the mount point.
3. **Firewall port, persistent** — solution 16.
4. **SELinux boolean, persistent** — solution 21.

Do all four, `reboot` exactly once, then verify all four in a single pass afterward (`id`, `sudo -l`, `df -h /opt/data`, `firewall-cmd --list-ports`, `getsebool <name>`) — checking one at a time as you go is exactly the habit this drill is designed to break, since the real exam only grades the machine cold at the end.
