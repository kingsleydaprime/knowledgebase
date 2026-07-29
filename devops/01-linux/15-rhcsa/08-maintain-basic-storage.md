# Maintain Basic Storage

> RHCSA V10

Part of [[README|RHCSA V10]]. Pairs with [[09-maintain-advanced-storage|maintain-advanced-storage]] for LVM. Some of this overlaps with mount/fstab/mkfs basics already in [[devops/01-linux/linux-reference|Linux Reference]] — this note goes deeper on the partitioning side and the RHEL-specific defaults (XFS, GPT-first tooling).

---

## Partition tables: MBR vs. GPT

| | MBR | GPT |
|---|---|---|
| Max disk size | 2 TB | Effectively unlimited (exabytes) |
| Max primary partitions | 4 (or 3 + 1 extended holding logicals) | 128 by default |
| Boot firmware | Legacy BIOS | UEFI (though GPT can work with BIOS too via a boot partition) |
| Redundancy | Single partition table, one point of failure | Partition table duplicated at start AND end of disk |

Modern RHEL installs on UEFI hardware default to **GPT**. Know both because the exam VM's disk layout isn't guaranteed to be one or the other.

---

## Tools: fdisk, gdisk, parted

| Tool | Partition table | Style |
|---|---|---|
| `fdisk` | MBR natively; modern versions also handle GPT | Interactive, single-letter menu |
| `gdisk` | GPT only | Same interactive style as fdisk, GPT-native |
| `parted` | Both | Can be interactive or fully scriptable in one line |

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

`parted` one-liner equivalent, for when scripting matters more than interactivity:
```bash
sudo parted /dev/sdb mklabel gpt
sudo parted /dev/sdb mkpart primary xfs 0% 10GiB
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
| options | `defaults` covers the common case; others: `ro`, `noatime`, `_netdev` (wait for network — critical for [[10-access-network-attached-storage|access-network-attached-storage]]) |
| dump | Legacy `dump` backup utility flag — `0` = ignore, essentially always 0 today |
| pass | `fsck` order at boot — `1` for root filesystem, `2` for others, `0` to skip checking |

**Always test an fstab edit before rebooting** — a broken fstab entry can drop the machine into emergency mode on next boot (see [[11-control-the-boot-process|control-the-boot-process]]):
```bash
sudo mount -a          # mount everything in fstab that isn't already mounted — errors show up here immediately, not at next reboot
```

---

## Swap

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
