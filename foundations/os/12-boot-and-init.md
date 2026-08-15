# Boot and Init

**[Intermediate]** — Power button to login prompt, and what PID 1 is actually responsible for.

## The chain

```
Power → firmware (UEFI/BIOS) → bootloader (GRUB) → kernel → initramfs → PID 1 (systemd) → services
```

[[foundations/os/fundamentals|The fundamentals note]] covers this at a high level; this one goes into what each stage actually does and where it goes wrong.

## 1. Firmware

The CPU starts executing at a fixed address (`0xFFFFFFF0` on x86) pointing at firmware ROM.

**UEFI** replaced BIOS and works differently in ways that matter:

| | BIOS | UEFI |
|---|---|---|
| Boot code location | 512-byte MBR | `.efi` files on a FAT32 **EFI System Partition** |
| Disk layout | MBR — 4 partitions, 2TB max | GPT — 128 partitions, huge disks |
| Mode | 16-bit real mode | 32/64-bit from the start |
| Verification | none | **Secure Boot** — signature checking |

UEFI can read a filesystem, so the bootloader is an ordinary file (`/boot/efi/EFI/fedora/grubx64.efi`) rather than code crammed into 512 bytes.

**Secure Boot** verifies each stage's signature against keys in firmware. It's why an unsigned kernel module won't load with Secure Boot on, and why third-party drivers need signing or MOK enrolment.

```bash
[ -d /sys/firmware/efi ] && echo UEFI || echo BIOS
efibootmgr -v          # boot entries
mokutil --sb-state     # Secure Boot status
```

## 2. Bootloader

GRUB's job: find the kernel, load it into memory, pass parameters, jump to it.

```bash
/boot/grub2/grub.cfg           # generated — don't edit directly
/etc/default/grub              # edit this, then grub2-mkconfig
cat /proc/cmdline              # what the running kernel was actually given
```

Kernel parameters worth knowing:

```
root=UUID=...              which device holds the root filesystem
ro                         mount it read-only initially
quiet splash               suppress boot messages
single / init=/bin/bash    RECOVERY — boot straight to a shell
systemd.unit=rescue.target
mitigations=off            disable Spectre/Meltdown mitigations (faster, insecure)
```

**`init=/bin/bash` is the recovery tool worth remembering** — it skips systemd entirely and drops you at a root shell with the root filesystem mounted. It's how you fix a broken `/etc/fstab` or a forgotten root password, and it's also why physical access means root access without disk encryption.

## 3. The kernel

Decompresses itself, then:

1. Sets up page tables and switches to protected/long mode
2. Initialises the memory manager, scheduler, and interrupt tables
3. Detects and initialises CPUs — the boot CPU brings up the others
4. Mounts the **initramfs**
5. Starts PID 1

```bash
dmesg | head -50         # the kernel's own log of all this
```

## 4. initramfs

A **compressed cpio archive containing a minimal userspace**, unpacked into a tmpfs and used as a temporary root.

It exists to solve a bootstrapping problem: the kernel needs a driver to read the root filesystem, but the driver lives *on* the root filesystem. The initramfs carries just enough — storage drivers, LVM, RAID, LUKS unlock, filesystem modules — to mount the real root.

```bash
lsinitrd /boot/initramfs-$(uname -r).img | head    # what's inside
dracut -f                                          # rebuild it
```

Then `pivot_root` (the same call [[foundations/os/11-isolation-and-containers|containers]] use) switches to the real root and `exec`s the real init.

**This is a common failure point.** A kernel update that regenerates the initramfs without the right storage driver produces a boot that hangs at "waiting for root device" — the kernel is fine, it just can't see the disk.

## 5. PID 1

The kernel starts exactly one process. Everything else descends from it.

PID 1 has special properties, all of which matter:

- **It cannot be killed** by signals it hasn't handled — the kernel doesn't apply default handlers
- **If it exits, the kernel panics**
- **Orphaned processes are re-parented to it**, and it must reap them

Those last two are why containers have a PID 1 problem: your application becomes PID 1, ignores `SIGTERM` by default, and doesn't reap orphans. → [[foundations/os/02-processes-and-threads|Processes and Threads]]

### systemd

Replaced SysV init and won, controversially. What it actually changed:

**Parallel startup by dependency graph** rather than sequential numbered scripts. Boot time went from ~30s to a few seconds.

**Socket activation** — systemd creates the listening socket and starts the service on first connection, passing the socket via `SCM_RIGHTS`. Services can start in any order because the socket exists before any of them do. → [[foundations/os/10-signals-and-ipc|IPC]]

**cgroup-based supervision.** Every service gets its own cgroup, so systemd knows exactly which processes belong to it — no PID files, no guessing, and `systemctl stop` reliably kills the whole tree. SysV init could never do this.

**Declarative units** instead of shell scripts:

```ini
[Unit]
Description=My API
After=network-online.target
Requires=postgresql.service

[Service]
Type=notify
ExecStart=/usr/local/bin/myapi
Restart=on-failure
RestartSec=5s

# hardening — the same primitives as containers
User=myapi
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
MemoryMax=512M
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

Those hardening directives are worth noticing: `ProtectSystem`, `PrivateTmp`, `MemoryMax` and `CPUQuota` are **namespaces and cgroups** applied to an ordinary service. systemd gives you most of a container's isolation without a container.

```bash
systemctl status myapi
journalctl -u myapi -f
systemd-analyze blame              # what's slow at boot
systemd-analyze critical-chain     # the dependency path that determined boot time
systemctl list-dependencies
```

`Type=notify` requires the service to call `sd_notify(READY=1)` when it's actually ready — better than `Type=simple`, which considers the service started the moment `exec` returns, before it can serve anything.

**Targets** replaced runlevels: `multi-user.target` (3), `graphical.target` (5), `rescue.target` (1).

### The controversy, briefly

The objections were scope creep (systemd absorbed logging, DNS, NTP, network config, containers), tight coupling, and binary journals. The defence is that the old model genuinely couldn't do supervision or dependency-ordered parallel startup properly.

It won because the technical arguments about cgroup supervision and socket activation were correct. Alternatives — OpenRC, runit, s6 — remain in Alpine, Void, and Gentoo.

## Container init

The same problem, smaller:

```dockerfile
ENTRYPOINT ["/app"]                  # app is PID 1 — must handle SIGTERM and reap
```

```bash
docker run --init ...                # inserts tini as PID 1
```

`tini` and `dumb-init` are ~200-line programs that do exactly two things: forward signals to the child, and reap zombies. That's all PID 1 must do.

**If your container's process spawns subprocesses, or ignores `SIGTERM`, use `--init`.** Otherwise you get zombie accumulation and 10-second waits on every `docker stop`.

## Diagnosing a broken boot

```bash
dmesg                              # kernel log
journalctl -b                      # this boot
journalctl -b -1                   # the PREVIOUS boot — for diagnosing a crash
journalctl -p err -b               # errors only
systemd-analyze blame
```

The usual failures:

| Symptom | Usually |
|---|---|
| Hangs at "waiting for root device" | initramfs missing a storage driver |
| Kernel panic — "unable to mount root" | wrong `root=` UUID, or a bad `/etc/fstab` |
| Drops to emergency shell | a filesystem in `/etc/fstab` failed to mount |
| Boots to a black screen | graphics driver — try `nomodeset` |
| Service won't start | `journalctl -u <name>`, then check `After=`/`Requires=` |

**`journalctl -b -1`** is the one people forget — the log from the boot *before* the crash is where the cause usually is.

## The whole picture

```
firmware ──→ bootloader ──→ kernel ──→ initramfs ──→ pivot_root ──→ systemd ──→ services
   │             │             │           │                           │
UEFI/BIOS      GRUB      decompress,   drivers to               parallel start
Secure Boot   /boot      init memory,  mount real root          by dependency,
              cmdline    start PID 1                            cgroup supervision
```

Every stage hands control to the next and disappears. By the time you have a login prompt, the firmware, bootloader and initramfs are all gone from memory.

---

## Related
- [[foundations/os/fundamentals|OS Fundamentals]] — the shorter version of this chain
- [[foundations/os/02-processes-and-threads|Processes and Threads]] — PID 1's duties
- [[foundations/os/11-isolation-and-containers|Isolation and Containers]] — the primitives systemd uses for hardening
- [[devops/01-linux/19-the-boot-process|Linux: The Boot Process]] · [[devops/01-linux/07-systemd-and-services|systemd and Services]]
- [[foundations/os/README|OS course map]]
