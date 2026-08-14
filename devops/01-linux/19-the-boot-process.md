# The Boot Process

**[Intermediate]** — what happens between power-on and a login prompt, and how to get in when that sequence breaks. The note you want *before* you need it.

## The kid version first

Booting is a relay race where each runner is bigger than the last and knows only how to find the next one.

```
firmware (UEFI/BIOS)   finds a bootloader on disk
   └── GRUB            finds and loads a kernel + initramfs
        └── kernel     mounts the real root filesystem
             └── systemd (PID 1)  starts everything else, in dependency order
```

Every boot failure is one runner failing to hand off. Knowing which handoff broke tells you which tool fixes it — and the symptom tells you the runner:

| Symptom | Failed handoff | Where you fix it |
|---|---|---|
| No bootable device / firmware screen | firmware → bootloader | Firmware settings, disk order, reinstall GRUB |
| GRUB menu, then nothing | GRUB → kernel | Kernel parameters, wrong/removed kernel |
| Kernel panic, "cannot mount root" | kernel → root fs | Broken initramfs, wrong root UUID |
| Boots to emergency shell | systemd → services | Almost always **fstab** |
| Boots but a service is dead | systemd unit failure | `journalctl -u <unit>` |

That last-but-one row is the one you'll actually hit. See [[devops/01-linux/18-disks-and-filesystems|disks & filesystems]] — a mistyped fstab line is the single most common self-inflicted boot failure.

## GRUB — the part you can edit at boot

Hold **Shift** (BIOS) or **Esc** (UEFI) during startup to get the menu. Press **`e`** on an entry to edit its boot parameters for this boot only — nothing is written to disk, so a reboot undoes any mistake.

Two parameters worth knowing on the `linux` line:

- **`systemd.unit=rescue.target`** — single-user mode: root filesystem mounted, minimal services, root shell. For fixing a broken config.
- **`systemd.unit=emergency.target`** — even more minimal: root mounted read-only, almost nothing started. For when rescue itself won't come up (e.g. fstab is so broken that mounting fails).

Then **Ctrl-X** to boot with the edit.

In emergency mode the root filesystem is read-only, so your first move before editing anything is:

```bash
mount -o remount,rw /
```

Forgetting that produces a baffling "cannot write file" in an editor when you're already stressed.

Permanent changes go in `/etc/default/grub`, followed by regenerating the config — and the command differs by distro, which is exactly the sort of thing that bites when you follow the wrong tutorial:

```bash
sudo update-grub                                     # Debian/Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg          # RHEL/Fedora
```

## Fixing a broken fstab from rescue mode

The most common real repair:

```bash
mount -o remount,rw /
nano /etc/fstab            # comment out the offending line
mount -a                   # verify — no errors means it will boot
reboot
```

Adding `nofail` to non-essential mounts in fstab prevents this class of failure entirely — the boot continues instead of dropping to a shell when that device is missing. On a cloud VM with attached volumes, `nofail` is close to mandatory, because a volume that fails to attach otherwise takes the whole machine down.

## systemd targets — what "runlevel" became

A target is a named set of units to reach.

```bash
systemctl get-default
sudo systemctl set-default multi-user.target   # boot to console, no GUI — right for a server
sudo systemctl isolate rescue.target           # switch now, without rebooting
```

| Target | Roughly |
|---|---|
| `graphical.target` | Full desktop |
| `multi-user.target` | Networked, console only — the server default |
| `rescue.target` | Single user, minimal services |
| `emergency.target` | Root shell, root mounted read-only |

Setting a server to `multi-user.target` is free performance and a smaller attack surface if a GUI got installed by accident.

## Diagnosing a slow boot

```bash
systemd-analyze                  # total time, split firmware/loader/kernel/userspace
systemd-analyze blame            # slowest units, descending
systemd-analyze critical-chain   # the dependency path that actually gated the boot
```

`blame` is the famous one but `critical-chain` is the useful one: a unit can take 30 seconds and delay nothing if the boot wasn't waiting on it. Chase the chain, not the list.

The usual culprits are a network-wait unit hanging on an interface that will never come up, and a mount waiting on a device that isn't there — both are the same shape of problem, and `nofail` or disabling the wait fixes both.

## Key insight

Firmware → GRUB → kernel → systemd, each finding the next. Identify which handoff failed from the symptom and you know which tool to reach for. Learn to press `e` at the GRUB menu on a machine that *isn't* broken — it's a bad time to learn the keystroke when it is.

## Related
- [[devops/01-linux/15-rhcsa/11-control-the-boot-process|RHCSA: Control the Boot Process]] — the deep version, including resetting a lost root password step by step
- [[devops/01-linux/18-disks-and-filesystems|Disks and Filesystems]] — the fstab entries that cause most boot failures
- [[devops/01-linux/07-systemd-and-services|systemd & services]] — what PID 1 does after the boot completes
- [[devops/01-linux/17-logs-and-journald|Logs and journald]] — `journalctl -b -1` to read the boot that failed
