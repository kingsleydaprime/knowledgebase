# Maintain Advanced Storage

> RHCSA V10

Part of [[README|RHCSA V10]]. Builds directly on [[08-maintain-basic-storage|maintain-basic-storage]] — LVM sits on top of raw partitions, and RHEL's default install layout is already LVM (see [[02-installing-rhel|installing-rhel]]), so this is the normal state of things, not an advanced edge case.

---

## Why LVM exists

Plain partitions are fixed the moment you create them — growing `/var` when it fills up means backup, repartition, restore. **LVM (Logical Volume Manager)** adds a layer of abstraction between physical disks and the filesystems on top of them, so volumes can be resized, moved, and combined across physical disks *without* touching the filesystem layout underneath, mostly live.

```
Physical Volume (PV)  →  Volume Group (VG)  →  Logical Volume (LV)
   raw disk/partition       pool of storage        the thing you
   initialized for LVM      combining 1+ PVs        actually format
                                                      and mount
```

---

## Building the stack

```bash
sudo pvcreate /dev/sdb /dev/sdc          # initialize one or more disks/partitions as PVs
sudo pvs                                  # list PVs, quick summary
sudo pvdisplay                            # list PVs, full detail

sudo vgcreate data-vg /dev/sdb /dev/sdc   # combine PVs into a volume group — the "pool"
sudo vgs                                  # list VGs
sudo vgdisplay                            # full detail, including free extents

sudo lvcreate -L 20G -n data-lv data-vg   # carve a 20GB logical volume out of the VG
sudo lvcreate -l 100%FREE -n data-lv data-vg   # or take ALL remaining free space instead of a fixed size
sudo lvs                                  # list LVs
sudo lvdisplay                            # full detail
```

LVs show up as devices at `/dev/data-vg/data-lv` (or `/dev/mapper/data--vg-data--lv`) — format and mount them exactly like a regular partition:
```bash
sudo mkfs.xfs /dev/data-vg/data-lv
sudo mount /dev/data-vg/data-lv /mnt/data
```

---

## Growing a volume group

Ran out of space in the VG entirely? Add another PV:
```bash
sudo pvcreate /dev/sdd
sudo vgextend data-vg /dev/sdd
```

---

## Resizing a logical volume — and the filesystem on top of it

Resizing the LV and resizing the filesystem inside it are **two separate steps**. Growing the LV without growing the filesystem just leaves unused space the filesystem doesn't know about.

```bash
sudo lvextend -L +10G /dev/data-vg/data-lv     # grow the LV by 10GB
sudo lvextend -l +100%FREE /dev/data-vg/data-lv # or grow to consume all free space in the VG
```

Then grow the filesystem to match — the command depends on the filesystem type:
```bash
sudo xfs_growfs /mnt/data                       # XFS — note: takes the MOUNTPOINT, not the device, and the fs must be mounted
sudo resize2fs /dev/data-vg/data-lv              # ext4 — takes the DEVICE, works mounted or unmounted
```

A common one-liner combining both steps:
```bash
sudo lvextend -L +10G -r /dev/data-vg/data-lv    # -r = automatically resize the filesystem after growing the LV
```

### Shrinking

**This is where the XFS-can't-shrink limitation from [[08-maintain-basic-storage|maintain-basic-storage]] fully bites.** For an XFS volume that needs to be smaller, there's no in-place shrink — the only path is: back up the data, destroy and recreate the LV at the smaller size, format fresh, restore the data.

ext4 *can* shrink, but order matters and it's the reverse of growing:
```bash
sudo umount /mnt/data
sudo e2fsck -f /dev/data-vg/data-lv              # forced check — required before resize2fs will shrink
sudo resize2fs /dev/data-vg/data-lv 15G           # shrink the FILESYSTEM first
sudo lvreduce -L 15G /dev/data-vg/data-lv         # THEN shrink the LV to match
```
Shrinking the LV before the filesystem risks truncating live filesystem data that's still sitting in the space being removed — this ordering (filesystem first, then LV) is the exam-relevant gotcha to remember.

---

## Cleaning up

```bash
sudo umount /mnt/data
sudo lvremove /dev/data-vg/data-lv
sudo vgremove data-vg
sudo pvremove /dev/sdb /dev/sdc
```
Order matters here too — you can't remove a VG that still has LVs in it, or a PV that's still part of a VG.

---

## Stratis — the newer alternative

RHEL 8+ ships **Stratis**, a volume-managing filesystem that wraps LVM + XFS complexity behind a simpler CLI, aimed at making thin provisioning and snapshots easier without hand-managing PV/VG/LV layers directly.

```bash
sudo systemctl enable --now stratisd
sudo stratis pool create data-pool /dev/sdb
sudo stratis filesystem create data-pool data-fs
```
Mounts at `/stratis/data-pool/data-fs`. Worth knowing it exists and roughly what it's for — LVM is still the primary thing tested and used in practice, but Stratis shows up in newer RHEL objectives as the direction storage management is heading.

---

## Quick reference: which layer am I resizing?

| Symptom | Fix at this layer |
|---|---|
| VG has no free space | `pvcreate` + `vgextend` — add more physical storage |
| VG has free space, LV is small | `lvextend` |
| LV is the right size, filesystem still reports old size | `xfs_growfs` (mounted, XFS) or `resize2fs` (ext4, mounted or not) |
