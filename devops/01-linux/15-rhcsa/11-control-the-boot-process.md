# Control the Boot Process

> RHCSA V10

Part of [[README|RHCSA V10]]. This is where "reset a lost root password" lives — one of the most classic RHCSA exam tasks, walked through in full below.

---

## The boot sequence

```
Firmware (BIOS/UEFI)  →  Bootloader (GRUB2)  →  Kernel + initramfs  →  systemd (PID 1)  →  target
```

| Stage | What happens |
|---|---|
| Firmware | POST, finds a boot device |
| GRUB2 | Loads the selected kernel + initramfs into memory, hands off control |
| Kernel + initramfs | Kernel initializes hardware; initramfs is a minimal temporary root filesystem holding just enough drivers/tools to find and mount the *real* root filesystem |
| systemd (PID 1) | Once real root is mounted, systemd takes over as the first real process and brings the system up to a target |

---

## GRUB2

```bash
/etc/default/grub              # human-edited settings — kernel command line defaults, timeout, etc.
/boot/grub2/grub.cfg            # the ACTUAL file GRUB reads at boot — generated, never edit by hand
```

After changing `/etc/default/grub`, regenerate the real config:
```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg          # BIOS systems
sudo grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg  # UEFI systems
```

### Editing boot parameters at the GRUB menu, temporarily

At the GRUB menu (hold a key during boot, or it shows automatically if `GRUB_TIMEOUT` isn't 0):
- Press **`e`** on the highlighted entry to edit it for this boot only
- Find the `linux` line, append kernel parameters at the end
- **Ctrl+X** (or F10) to boot with the change — nothing here is saved permanently, exactly what you want when troubleshooting without wanting the change to persist

---

## systemd targets — the modern replacement for runlevels

Old SysV init used numbered **runlevels**; systemd uses named **targets** that map onto them for compatibility:

| Runlevel (legacy) | systemd target | Meaning |
|---|---|---|
| 0 | `poweroff.target` | Shut down |
| 1 | `rescue.target` | Single-user, minimal, root-only |
| 3 | `multi-user.target` | Full multi-user, network, no GUI — normal server state |
| 5 | `graphical.target` | Multi-user + GUI |
| 6 | `reboot.target` | Reboot |

```bash
systemctl get-default                 # what target boots by default
sudo systemctl set-default multi-user.target   # change the default persistently
systemctl isolate rescue.target        # switch to a DIFFERENT target RIGHT NOW, without rebooting
```

`systemctl set-default` on a server you accidentally installed with a GUI (`graphical.target`) but don't want running one is a realistic, exam-style task in its own right.

---

## Rescue mode vs. emergency mode

Both are ways in when something's broken enough that a normal boot won't get you a working shell.

| | `rescue.target` | `emergency.target` |
|---|---|---|
| Filesystems | Local filesystems mounted, read-write | Only root filesystem, and **read-only** |
| Services | Most base system services started | Bare minimum — barely more than a shell |
| Root password | Required | Required |
| Use case | Fix something that needs other services running (e.g. fix a package) | Root filesystem itself is too broken to trust write access to yet |

Reach either from the GRUB menu by appending to the kernel line (press `e`, edit, Ctrl+X):
```
systemd.unit=rescue.target
systemd.unit=emergency.target
```

---

## Resetting a lost root password — the full walkthrough

If you don't even have the root password to *get into* rescue/emergency mode, you need to intercept boot **before** systemd asks for any password at all — using `rd.break`, which drops you into the initramfs shell, before the real root filesystem is even mounted read-write.

1. At the GRUB menu, press `e` on the boot entry.
2. Find the line starting with `linux` (or `linux16`), append `rd.break` at the end.
3. Ctrl+X to boot with that.
4. You land in the initramfs shell with root mounted read-only at `/sysroot`:
   ```bash
   mount -o remount,rw /sysroot        # make it writable
   chroot /sysroot                      # pivot into the real root filesystem
   passwd root                          # set the new password
   touch /.autorelabel                  # force a FULL SELinux relabel on next boot — required, see below
   exit                                  # leave the chroot
   exit                                  # leave the initramfs shell, resumes normal boot
   ```
5. System reboots normally with the new root password.

### Why `/.autorelabel` matters

Any file created or modified while inside that `rd.break` shell doesn't get a proper SELinux context — the SELinux userspace tools that would normally do that aren't running yet at that boot stage. Skip `touch /.autorelabel` and the system boots with a mislabeled `/etc/shadow` (among other things), which SELinux (if enforcing) will then block access to — you'll have "fixed" the password but broken login entirely. This step is what ties [[07-manage-selinux-security|manage-selinux-security]] directly into boot troubleshooting, and it's the detail most people forget under exam time pressure.

The relabel adds real time to the next boot (it walks the entire filesystem) — expected, not a sign anything's wrong.
