# Disks and Filesystems

**[Intermediate]** — adding storage to a machine, and the two commands that will save you when a disk fills up.

## The kid version first

A disk is a slab of blocks. Three things have to happen before you can put a file on it:

1. **Partition** — divide the slab into named regions.
2. **Format** — write a filesystem into a region, so it can hold files rather than raw blocks.
3. **Mount** — attach that filesystem to a directory in the tree, because Linux has no drive letters. `/mnt/data` *is* the disk.

Miss any step and nothing works. Do them in the wrong order and you erase something.

## The full-disk emergency

This is the situation you'll actually meet, so it goes first:

```bash
df -h                                  # which filesystem is full
df -i                                  # ...or has run out of INODES (millions of tiny files)
du -sh /var/* | sort -rh | head        # what's eating it, drilling down
```

`df -i` is the one people don't know. A filesystem can be 40% full and still refuse to create a file because it's out of inodes — usually a runaway process writing millions of small files, or a cache directory nobody cleans. The error message ("No space left on device") is identical, and `df -h` shows plenty of room, which is baffling until you know.

The other classic: **a deleted file still held open by a process doesn't free its space.** You delete a 20GB log, `df` doesn't move, and you go looking for a second cause.

```bash
sudo lsof +L1        # open files with no directory entry — the culprits
```

Restart the process holding it and the space returns.

## Adding a disk, start to finish

```bash
lsblk                                  # what disks exist and what's on them
sudo parted /dev/sdb mklabel gpt       # GPT unless you have a reason
sudo parted -a opt /dev/sdb mkpart primary ext4 0% 100%
sudo mkfs.ext4 /dev/sdb1               # or mkfs.xfs
sudo mkdir -p /mnt/data
sudo mount /dev/sdb1 /mnt/data
```

Then make it survive a reboot — **by UUID, never by device name**:

```bash
sudo blkid /dev/sdb1                   # get the UUID
echo 'UUID=a1b2c3d4-... /mnt/data ext4 defaults 0 2' | sudo tee -a /etc/fstab
sudo mount -a                          # TEST IT NOW
```

Device names are not stable — `/dev/sdb` can become `/dev/sdc` after adding hardware or a reboot, and an fstab entry pointing at the wrong disk is how you mount something unexpected over a directory that already had data in it.

**`sudo mount -a` before you reboot is not optional.** A malformed fstab line stops the machine booting into a normal state, and on a remote VPS with no console that is a very bad afternoon. If it's ever happened to you, that's what [[devops/01-linux/19-the-boot-process|rescue mode]] is for.

## ext4 vs xfs vs btrfs

| | Use when |
|---|---|
| **ext4** | Default choice. Mature, predictable, shrinkable |
| **xfs** | Large files and high parallel throughput. RHEL's default. **Cannot be shrunk** |
| **btrfs** | You want snapshots and checksumming built in |
| **zfs** | Same, more mature, licensing-awkward on Linux |

For a server holding an application and its data, ext4 or xfs, and you'll rarely regret either. The one asymmetry worth remembering is that **xfs grows but never shrinks** — if you might need to reclaim space from a volume, that decision is made at format time.

## LVM — the layer that makes disks resizable

Partitioning directly onto a disk is rigid: a partition's neighbours pin it in place, so growing `/var` means moving everything after it. LVM inserts an indirection layer:

```
physical volumes (disks)  →  volume group (a pool)  →  logical volumes (what you format and mount)
```

Now "grow /var" is "take more space from the pool," and the pool can span multiple disks.

```bash
sudo pvcreate /dev/sdc                       # 1. enlist a disk
sudo vgextend data-vg /dev/sdc               # 2. add it to the pool
sudo lvextend -l +100%FREE /dev/data-vg/lv-var   # 3. grow the volume
sudo resize2fs /dev/data-vg/lv-var           # 4. grow the FILESYSTEM on top
```

**Step 4 is the one everyone forgets.** Growing the logical volume gives the filesystem more room to expand into; it does not expand it. `df` will show the old size until you resize the filesystem itself. (`xfs_growfs` for xfs, and note it must be mounted, unlike `resize2fs`.)

If you're provisioning a server you may ever need to expand, put it on LVM from the start. Retrofitting it later means downtime and a backup you'd rather not be relying on.

## Key insight

Three layers — partition, filesystem, mount — and every storage problem is a question of which one you're actually operating on. When a disk fills, check `df -i` and `lsof +L1` before believing `df -h`. When you edit fstab, run `mount -a` before you reboot.

## Related
- [[devops/01-linux/01-file-system|The File System]] — the tree these get attached to
- [[devops/01-linux/15-rhcsa/08-maintain-basic-storage|RHCSA: Basic Storage]] — parted/fdisk walkthroughs, swap, mount options in depth
- [[devops/01-linux/15-rhcsa/09-maintain-advanced-storage|RHCSA: Advanced Storage]] — LVM properly, including shrinking and replacing a failing disk
- [[devops/01-linux/19-the-boot-process|The Boot Process]] — for when a bad fstab entry stops the boot
