# Maintain Basic Storage

> RHCSA V10

Part of [[README|RHCSA V10]]. Pairs with [[09-maintain-advanced-storage|maintain-advanced-storage]] for LVM. Some of this overlaps with mount/fstab/mkfs basics already in [[devops/01-linux/linux-reference|Linux Reference]] — this note goes deeper on the partitioning side and the RHEL-specific defaults (XFS, GPT-first tooling).

---

## Partition tables: MBR vs. GPT

A partition table is the map at the start of a disk that says where each partition begins and ends — **MBR (Master Boot Record)** is the original, decades-old format; **GPT (GUID Partition Table)** is its modern replacement, built to remove MBR's size and partition-count ceilings.

| | MBR | GPT |
|---|---|---|
| Max disk size | 2 TB | Effectively unlimited (exabytes) |
| Max primary partitions | 4 (or 3 + 1 extended holding logicals) | 128 by default |
| Boot firmware | Legacy BIOS | UEFI (though GPT can work with BIOS too via a boot partition) |
| Redundancy | Single partition table, one point of failure | Partition table duplicated at start AND end of disk |

Modern RHEL installs on UEFI hardware default to **GPT**. Know both because the exam VM's disk layout isn't guaranteed to be one or the other.

---

## Tools: parted, fdisk, gdisk

**`parted` is RHEL's standard, official partition editor** — it handles both MBR and GPT, works interactively or as one-liners for scripting, and is the tool Red Hat's own course material builds around. `fdisk`/`gdisk` (below) are worth recognizing since they're common elsewhere and still ship on RHEL, but default to `parted` unless something specifically calls for the others.

| Tool | Partition table | Style |
|---|---|---|
| `parted` | Both | Interactive session or fully scriptable one-liners — **the RHEL-standard choice** |
| `fdisk` | MBR natively; modern versions also handle GPT | Interactive, single-letter menu |
| `gdisk` | GPT only | Same interactive style as fdisk, GPT-native |

### parted walkthrough

```bash
sudo parted /dev/sdb print          # show the current partition table without changing anything
```
```
Model: QEMU QEMU HARDDISK (scsi)
Disk /dev/sdb: 5369MB
Partition Table: gpt
Number  Start   End     Size    File system  Name  Flags
```

A brand-new disk has no partition table at all yet — write one first with `mklabel` (this **wipes any existing partition table**, so treat it as destructive):
```bash
sudo parted /dev/sdb mklabel gpt      # or 'msdos' for MBR
```

Then create the partition. Interactively:
```bash
sudo parted /dev/sdb
```
```
(parted) mkpart
Partition name? []? userdata
File system type? [ext2]? xfs
Start? 2048s
End? 1000MB
(parted) print                        # verify before quitting
(parted) quit
```
`mkpart` only labels the partition's intended filesystem type in the table — it does **not** actually create a filesystem on it; that's still a separate `mkfs` step below. Sizes accept `s` (sectors), `MB`/`GB` (powers of 10), or `MiB`/`GiB` (powers of 2) — a start sector that's a multiple of 2048 is the safe, aligned default `parted` itself will nudge you toward if you get it wrong.

The same thing as a single scriptable line, for when interactivity isn't wanted:
```bash
sudo parted /dev/sdb mkpart userdata xfs 2048s 1000MB
sudo parted /dev/sdb rm 1                              # delete partition number 1 — same interactive/one-liner duality
sudo udevadm settle                                     # wait for the kernel to register the new device node before using it
```

### fdisk walkthrough

```bash
sudo fdisk /dev/sdb
```
Inside the interactive prompt:
```
Command (m for help): n        # new partition
Partition type: p              # primary
Partition number: 1
First sector: [Enter]          # accept default (next free sector)
Last sector: +10G              # size, relative to first sector
Command (m for help): w        # WRITE changes to disk — nothing is committed until this
```

| Key command inside fdisk | Action |
|---|---|
| `n` | New partition |
| `d` | Delete partition |
| `p` | Print current partition table |
| `t` | Change a partition's type code |
| `w` | Write changes and exit — **the only command that actually commits anything** |
| `q` | Quit without saving |
| `m` | Help menu |

After writing, make sure the kernel actually sees the new table:
```bash
sudo partprobe /dev/sdb        # re-read partition table without rebooting
sudo lsblk                     # confirm the new partition shows up
```

---

## Creating a filesystem

```bash
sudo mkfs.xfs /dev/sdb1        # XFS — the RHEL default since RHEL 7/8
sudo mkfs.ext4 /dev/sdb1       # ext4 — still fully supported, more flexible (can shrink)
```

| | XFS | ext4 |
|---|---|---|
| RHEL default | Yes | No (but still first-class) |
| Can grow (mounted, live) | Yes — `xfs_growfs` | Yes — `resize2fs` |
| Can shrink | **No** — must back up, recreate, restore | Yes — `resize2fs` |
| Typical use | Default choice, especially large filesystems | When shrink capability matters |

That "XFS can never shrink" line is worth remembering outright — it's the single most-tested gotcha around filesystem choice, and it directly shapes how [[09-maintain-advanced-storage|maintain-advanced-storage]] handles resizing.

---

## Mounting

```bash
sudo mount -t xfs /dev/sdb1 /mnt/data      # explicit filesystem type
sudo mount /dev/sdb1 /mnt/data              # type usually auto-detected, fine for one-off mounts
sudo umount /mnt/data                       # by mountpoint...
sudo umount /dev/sdb1                       # ...or by device, either works
```

Device names (`/dev/sdb1`) aren't stable — order can shift across reboots depending on what's attached. Get the UUID and use that instead:

```bash
sudo blkid /dev/sdb1
# /dev/sdb1: UUID="a1b2c3d4-..." TYPE="xfs"
```

### /etc/fstab — mounting automatically at boot

```
# device                                mountpoint   type   options   dump  pass
UUID=a1b2c3d4-...                       /mnt/data    xfs    defaults  0     2
```

| Field | Meaning |
|---|---|
| device | `UUID=...` (preferred) or `/dev/sdX` (fragile) or `LABEL=...` |
| mountpoint | Where it attaches into the tree |
| type | Filesystem type — `xfs`, `ext4`, `swap`, `nfs`, etc. |
| options | `defaults` covers the common case; others: `ro`, `noatime`, `_netdev` (wait for network — critical for [[10-access-network-attached-storage\|access-network-attached-storage]]) |
| dump | Legacy `dump` backup utility flag — `0` = ignore, essentially always 0 today |
| pass | `fsck` order at boot — `1` for root filesystem, `2` for others, `0` to skip checking |

**Always test an fstab edit before rebooting** — a broken fstab entry can drop the machine into emergency mode on next boot (see [[11-control-the-boot-process|control-the-boot-process]]):
```bash
sudo mount -a          # mount everything in fstab that isn't already mounted — errors show up here immediately, not at next reboot
```

---

## Swap

Swap is disk space the kernel uses to hold memory pages that don't fit in RAM right now — slower than RAM by a lot, so it's a pressure release valve, not a substitute for having enough physical memory for your actual workload. Red Hat's own sizing guidance, worth knowing rather than guessing at:

| Total RAM | Recommended swap | Swap if hibernation matters |
|---|---|---|
| ≤ 2 GB | 2× RAM | 3× RAM |
| 2–8 GB | Same as RAM | 2× RAM |
| 8–64 GB | At least 4 GB | 1.5× RAM |
| > 64 GB | At least 4 GB | Hibernation not recommended at this size |

Hibernation is the special case that drives the bigger numbers — hibernating writes the *entire contents of RAM* to swap before powering off, so swap has to be at least as large as RAM for that to even be possible at all.

```bash
sudo mkswap /dev/sdb2          # format a partition as swap space
sudo swapon /dev/sdb2          # activate it now
swapon --show                  # confirm what's currently active as swap
sudo swapoff /dev/sdb2         # deactivate
```

fstab entry to make it persistent:
```
UUID=...    none    swap    swap    0   0
```
Note the mountpoint field is literally `none` — swap doesn't attach anywhere in the directory tree.
