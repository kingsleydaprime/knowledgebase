# Installing Red Hat Enterprise Linux

> RHCSA V10

Part of [[README|RHCSA V10]]. Builds on [[01-getting-started-with-rhel|getting-started-with-rhel]].

---

## Getting the installer

The RHEL installer is **Anaconda** (same installer Fedora uses — not related to the Python distribution of the same name). You get the ISO through a free Red Hat Developer Subscription at developers.redhat.com, download the "Binary DVD" ISO for your architecture, and boot from it (USB, or a virtual CD-ROM in a VM).

Boot menu options:
- **Install Red Hat Enterprise Linux** — the real thing
- **Test this media & install** — checksums the ISO first (worth doing once, skip it after)
- **Troubleshooting** → rescue an existing installation, or boot in basic graphics mode if the GUI installer won't render

---

## Anaconda's hub-and-spoke layout

Anaconda shows one **Installation Summary** hub screen with spokes (sub-screens) branching off it. You can visit spokes in any order; a spoke with a warning icon blocks you from starting the install until it's resolved.

| Spoke | What you set |
|---|---|
| Keyboard | Layout |
| Language Support | Locale |
| Time & Date | Timezone, NTP |
| Installation Source | Local media vs. network location |
| Software Selection | Base environment — see below |
| **Installation Destination** | Disk(s), partitioning — see below |
| KDUMP | Kernel crash dump reservation (leave default unless low on RAM) |
| Network & Host Name | Hostname, interface activation |
| Root Password | Root account, or lock it and rely on sudo-only admin (common hardened setup) |
| User Creation | First regular user, optionally "Make this user administrator" (adds to `wheel` group → sudo) |

The `wheel` group is worth understanding, not just memorizing: on RHEL, membership in `wheel` is what `/etc/sudoers` grants blanket sudo access to (`%wheel ALL=(ALL) ALL`, usually already uncommented by default). Checking "Make this user administrator" during install is just a checkbox for "add this user to the `wheel` group" — nothing more mysterious than that.

---

## Installation Destination — the one that matters most for the exam

Two paths:

**Automatic partitioning** — Anaconda picks layout for you. On RHEL, the default is:
```
/boot        — xfs, separate partition, not under LVM (bootloader must read it directly)
/boot/efi    — on UEFI systems, the EFI System Partition (vfat)
/            — xfs, inside an LVM logical volume
swap         — inside an LVM logical volume
```
Notice: **LVM by default**. This is different from a lot of Debian/Ubuntu default installs, which often skip LVM. In short, "inside an LVM logical volume" means `/` and swap aren't sitting directly on a fixed-size partition — there's a flexible pool of storage underneath them that can be grown (and, with caveats, shrunk) later without wiping and repartitioning the disk. That flexibility is exactly why "Maintain Advanced Storage" (resizing volumes live) is even possible — see [[09-maintain-advanced-storage|maintain-advanced-storage]] for the full mechanics.

**Custom partitioning** — you define the layout yourself: mount points, sizes, filesystem types (`xfs` is the RHEL default filesystem — see [[08-maintain-basic-storage|maintain-basic-storage]] for why), and whether each goes on a plain partition, LVM, or (newer) Stratis.

---

## Software selection — base environments

Pick a base environment, then optionally add-on groups on top:

| Base environment | What it is |
|---|---|
| Server with GUI | Full server + desktop environment (GNOME) — heaviest |
| Server | Text-mode server, no GUI — what most production RHEL boxes run |
| Minimal Install | Bare minimum to boot and be managed remotely — smallest attack surface, add packages later with `dnf` |
| Workstation | Desktop-focused install |
| Custom Operating System | Nothing pre-selected — full manual control |

For exam practice, **Minimal Install** is the realistic choice — it forces you to know `dnf install` for anything you need afterward instead of leaning on a GUI that won't be there.

---

## After installation: registration

The very first `dnf` command on a freshly installed, unregistered RHEL system will fail — there are no repos configured yet. Register against Red Hat's CDN (or a local Satellite/mirror in a real enterprise):

```bash
subscription-manager register --username <user> --password <pass>
subscription-manager attach --auto
dnf repolist                          # confirm repos are now populated
```

---

## Kickstart — unattended installs

Every RHEL install generates `/root/anaconda-ks.cfg` — a **Kickstart file** that records exactly what you just chose. It doubles as a template: hand that file (or a hand-written one) to a new installer boot via a boot option, and the entire install runs unattended, no clicking through spokes.

```bash
# Boot option to point at a kickstart file (on a boot server, USB, or NFS)
inst.ks=http://server/ks.cfg
```

Key directives inside a kickstart file:

```kickstart
lang en_US.UTF-8
keyboard us
timezone America/New_York
rootpw --iscrypted $6$...              # pre-hashed password
network --bootproto=dhcp --hostname=host1
autopart --type=lvm                    # or a manual `part`/`logvol` layout
firewall --enabled --service=ssh
selinux --enforcing

%packages
@^minimal-environment
vim
%end
```

This isn't RHCSA-exam-tested directly (that's more of an automation/RHCE-adjacent skill), but it's worth knowing it exists — it's *why* enterprises can provision hundreds of identical RHEL boxes without a human clicking through Anaconda each time.
