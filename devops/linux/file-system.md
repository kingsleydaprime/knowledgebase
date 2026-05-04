# The Linux Filesystem

First thing to understand — in Linux, **everything is a file.** Devices, processes, sockets, hardware — all represented as files somewhere.

And it all starts from one place: **`/`** (called "root").

No `C:\` or `D:\` like Windows. One tree, everything hangs off `/`.

---

Open your terminal and run:

```bash
ls /
```

You'll see the top-level directories. Here's what the important ones mean:

| Directory | Description | Common contents & what they are |
|---|---|---|
| `/bin` | Commands everyone uses daily | `ls` (list files), `cp` (copy), `mv` (move), `cat` (read file), `bash` (the shell itself), `chmod` (change permissions) |
| `/boot` | Everything needed to start the OS before the kernel fully loads | `grub/` (bootloader config), `vmlinuz` (the compressed kernel file), `initrd.img` (temporary filesystem used during boot) |
| `/dev` | Hardware represented as files — remember, everything is a file in Linux | `sda` (your main hard disk), `tty` (terminal devices), `null` (a black hole — anything written here disappears), `zero` (infinite stream of zeros), `random` (generates random bytes) |
| `/etc` | The system's control room — all configuration lives here | `passwd` (user accounts list), `hosts` (local DNS — maps names to IPs), `fstab` (what drives to mount on boot), `ssh/` (SSH server config), `nginx/` (nginx web server config), `cron.d/` (scheduled tasks) |
| `/home` | Each user on the system gets their own personal folder here | `/home/kingsley/` contains your `Desktop/`, `Downloads/`, `.bashrc` (your shell config), `.ssh/` (your SSH keys) |
| `/lib` | Shared code that programs in `/bin` and `/sbin` depend on to run | `*.so` files — think of these like `.dll` files on Windows, shared libraries multiple programs use simultaneously |
| `/media` | When you plug in a USB or external drive, Linux auto-mounts it here | `/media/kingsley/USB_DRIVE/` — your files on that drive appear here |
| `/mnt` | A manual mount point — you decide what goes here | If you manually mount a second hard drive or network share, you'd put it here |
| `/opt` | Third-party software that doesn't follow standard Linux structure installs here | `/opt/google/` (Google Chrome), `/opt/lampp/` (XAMPP), basically any software that bundles everything into one folder |
| `/proc` | A fake filesystem — nothing here is on disk, it's live data the kernel generates on the fly | `cpuinfo` (your CPU details), `meminfo` (RAM usage), `uptime` (how long system has been running), `1/` (folder with everything about PID 1 — open files, memory maps, etc) |
| `/root` | The home directory for the root (admin) user — separate from `/home` for security | Same structure as a normal home folder but only accessible by root |
| `/run` | Fresh runtime data generated after every boot — wiped and recreated each startup | `systemd/` (systemd runtime state), `lock/` (lock files so two processes don't do the same thing), `user/` (per-user runtime data) |
| `/sbin` | System administration commands — mostly for the root user | `fdisk` (partition disks), `fsck` (check/repair filesystem), `iptables` (firewall rules), `reboot` (restart system) |
| `/srv` | Data that services on this machine serve to the outside world | `/srv/http/` (files your web server serves), `/srv/ftp/` (files your FTP server serves) |
| `/sys` | Like `/proc` but focused specifically on hardware and kernel subsystems | `block/` (block devices like disks), `bus/` (hardware buses like USB, PCI), `class/` (device categories), `devices/` (every device the kernel knows about) |
| `/tmp` | Scratch space — anything here gets wiped on reboot | Session files, build artifacts, anything a program needs temporarily |
| `/usr` | The bulk of installed software and their supporting files | `bin/` (non-essential user commands), `lib/` (their libraries), `local/` (stuff you compile/install manually), `share/` (documentation, icons, shared data) |
| `/var` | Data that constantly changes as the system runs | `log/` (system and app logs), `cache/` (cached app data), `mail/` (mail spool), `www/` (web server files on some distros), `lib/` (persistent app state data) |
| `/swapfile` | Overflow space — when RAM is full, the kernel moves less-used memory here temporarily | A single file, not a directory |
| `/snap` | Ubuntu's snap package system stores self-contained app bundles here | `/snap/firefox/` (Firefox as a snap), `/snap/core/` (snap runtime itself) |
| `/lost+found` | If your filesystem crashes and the OS recovers broken file fragments, they end up here | Filesystem debris — you'd only look here after a crash |
---

### Interesting commands to run

```sh
ls /etc | head -20
ls /var
ls /proc | head -20

# view the content of cpu info
cat /proc/cpuinfo | head -30
cat /proc/meminfo | head -10
# You're literally reading live kernel data as a file.
```
