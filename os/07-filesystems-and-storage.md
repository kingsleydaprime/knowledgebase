# Filesystems and Storage

**[Intermediate → Advanced]** — Inodes, the page cache, and `fsync` — the boundary where "written" starts to mean something.

## The layers

```
your code:  write(fd, buf, n)
                │
      ┌─────────▼─────────┐
      │  VFS              │  the uniform interface — ext4, xfs, btrfs, nfs, tmpfs
      ├───────────────────┤
      │  PAGE CACHE       │  writes land HERE and return. Not durable yet.
      ├───────────────────┤
      │  FILESYSTEM       │  inodes, extents, journal
      ├───────────────────┤
      │  BLOCK LAYER      │  I/O scheduler, request merging
      ├───────────────────┤
      │  DEVICE DRIVER    │  NVMe, SCSI, virtio
      ├───────────────────┤
      │  DEVICE           │  and its own volatile write cache
      └───────────────────┘
```

**Every layer buffers.** That's what makes I/O fast and what makes durability subtle.

## The VFS

The Virtual File System is the abstraction that makes `read`/`write` work identically on ext4, NFS, a tmpfs, a USB stick, and `/proc`. Each filesystem implements a set of operations; the VFS dispatches to them.

It's the same design as [[languages/02-go/04-methods-and-interfaces|an interface]] — one small contract, many implementations — and it's why `cat` doesn't need to know what it's reading from.

## Inodes

A file's metadata lives in an **inode**, and the filename does not:

```
inode: size, permissions, uid/gid, timestamps, link count,
       and POINTERS to the data blocks
```

**The name lives in the directory**, which is just a file mapping names → inode numbers. That decoupling explains several things that otherwise look strange:

**Hard links** are two names for one inode. Both are equally "the file"; deleting one just decrements the link count.

```bash
ln file.txt other.txt          # same inode, link count 2
ls -li                          # the first column IS the inode number
stat file.txt
```

**Deleting an open file works.** `unlink` removes the directory entry and decrements the link count. The inode and its blocks survive while any process holds it open — which is why:

```bash
rm huge.log          # df shows no space freed...
lsof | grep huge.log # ...because a process still has it open
```

That's the answer to "I deleted the logs and the disk is still full": restart the process holding the descriptor, or truncate it in place (`> file.log`).

**Renames within a filesystem are atomic and free** — just update the directory entry. That's why the write-to-temp-then-rename pattern is the standard atomic-update idiom:

```c
write(tmpfd, data, n);
fsync(tmpfd);                     // durable BEFORE the rename
close(tmpfd);
rename("file.tmp", "file");       // atomic swap
fsync(dirfd);                     // make the RENAME durable too
```

**Both fsyncs are required.** Skip the first and you can end up with a renamed file full of zeros; skip the second and the rename itself may be lost. This is the single most-botched durability pattern in application code.

**Running out of inodes** is possible with disk space remaining — millions of tiny files exhaust a fixed inode table on ext4:

```bash
df -i        # inode usage — check this when df says there's space but writes fail
```

## The page cache, and why `write` is a lie

```c
write(fd, buf, n);        // returns almost immediately — data is in the PAGE CACHE
                          // it may be nowhere near the disk
```

`write` copies into kernel memory and returns. The data becomes durable when the kernel flushes it — within ~30 seconds by default, or on demand.

**If the machine loses power now, the data is gone**, and `write` already told you it succeeded.

```bash
cat /proc/sys/vm/dirty_ratio               # % of RAM that can be dirty before writers BLOCK
cat /proc/sys/vm/dirty_background_ratio    # % at which background flushing starts
cat /proc/sys/vm/dirty_expire_centisecs    # age at which a page must be written
grep -E 'Dirty|Writeback' /proc/meminfo
```

Hitting `dirty_ratio` makes every writer block until flushing catches up — a common cause of a system that suddenly stalls under heavy write load.

Reads use the same cache: a second read of the same file is a memory copy. → [[foundations/os/04-virtual-memory|Virtual Memory]]

## `fsync` and the durability boundary

```c
fsync(fd);         // flush this file's data AND metadata; returns when the device says done
fdatasync(fd);     // data + only metadata needed to read it back (skips mtime) — faster
sync();            // everything, system-wide
```

**`fsync` is the boundary.** Before it, "written" means "in RAM". After it returns successfully, the data survives power loss.

It costs **~100µs–10ms** depending on the device, which is why databases fight so hard to minimise it — group commit, write-ahead logs, and batching all exist to amortise `fsync` across many transactions.

Three things that go wrong:

**The device lies.** Consumer drives with volatile write caches sometimes acknowledge a flush before the data is on stable media. Enterprise drives have power-loss protection; consumer ones often don't.

```bash
hdparm -W /dev/sda            # is the write cache on?
```

**`fsync` errors are not retryable** — the "fsyncgate" problem. On Linux, a failed writeback marks the error and **clears it on the first `fsync` that reports it**. A second `fsync` returns success even though the data was lost. Postgres had to change to panic-on-fsync-failure because there is no safe recovery. If your code ignores `fsync`'s return value, fix that; if it retries on failure, that's worse.

**Directory entries need their own fsync.** Creating a file and fsyncing it doesn't guarantee the *name* survives — the directory is a separate object.

→ [[architecture/04-distributed-systems/README|Distributed systems]] durability arguments all bottom out here.

## Journaling

A crash mid-write can leave the filesystem inconsistent — an inode marked allocated with no directory entry, or a directory entry pointing at a freed inode.

A **journal** makes metadata updates atomic: write the intent to a log, then perform the operation, then mark it done. After a crash, replay or discard incomplete entries. Recovery is seconds instead of a full `fsck` over the whole disk.

```bash
mount -o data=ordered   # DEFAULT: metadata journalled, data written BEFORE its metadata
mount -o data=journal   # data journalled too — safest, ~2× write amplification
mount -o data=writeback # metadata only, no ordering — fastest, can expose stale blocks
```

**`data=ordered` is the sensible default** and the reason ext4 doesn't usually expose garbage after a crash: the data hits the disk before the metadata that points at it.

Copy-on-write filesystems (btrfs, ZFS) take a different route — never overwrite in place, so the old version is intact until the new one is complete. That gives atomic snapshots and checksums for free, at the cost of fragmentation and higher write amplification.

## The filesystems

| | Character |
|---|---|
| **ext4** | the Linux default. Mature, fast, extents, journalled. Boring in the best sense |
| **XFS** | excellent for large files and high parallelism; RHEL's default. Can't shrink |
| **btrfs** | CoW, snapshots, checksums, built-in RAID. Feature-rich; RAID5/6 still not recommended |
| **ZFS** | CoW with checksums, integrated volume management. Excellent; licensing keeps it out of the kernel tree |
| **tmpfs** | RAM-backed. `/dev/shm`, `/run`. Fast, volatile |
| **overlayfs** | union mount — **the basis of container images** → [[devops/02-docker/README\|Docker]] |
| **NFS / CIFS** | network filesystems. The abstraction leaks: latency, partial failure, locking |

**overlayfs is worth understanding** if you use containers. A container's filesystem is read-only image layers plus a writable upper layer; writing to a file in a lower layer **copies the whole file up first** (copy-up). That's why writing to a large file inside a container can be surprisingly slow the first time, and why write-heavy workloads should use a volume rather than the container filesystem.

## The block layer

```bash
cat /sys/block/nvme0n1/queue/scheduler      # [none] mq-deadline kyber bfq
```

**`none` is correct for NVMe.** The device has deep parallel queues and reorders internally; an OS-level scheduler just adds latency. `mq-deadline` or `bfq` still matter for spinning disks.

```bash
iostat -x 1                # %util, await, r/s, w/s — the first thing to look at
iotop                      # per-process I/O
biolatency                 # bcc/eBPF — latency histogram
cat /proc/pressure/io      # PSI — how much time is LOST waiting on I/O
```

`await` (average request latency) and PSI are the two numbers that tell you whether storage is your problem. `%util` is misleading on NVMe — a device can be 100% "utilised" with plenty of headroom, because it services many requests concurrently.

## Direct I/O

```c
int fd = open(path, O_DIRECT | O_RDWR);    // bypass the page cache entirely
```

Reads and writes go straight to the device. Buffers must be aligned to the block size, and the length must be a multiple of it.

**Only correct when you're managing your own cache** — which is exactly what a database does. Postgres deliberately uses the page cache; Oracle and MySQL/InnoDB mostly use `O_DIRECT` with their own buffer pool, because a database knows its access patterns better than the kernel does.

For everything else, `O_DIRECT` makes things slower. It's not a "fast mode".

```c
posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL);   // hint: read ahead aggressively
posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);     // drop these pages from the cache
```

`FADV_DONTNEED` after streaming a huge file is polite — it stops a one-off backup from evicting everyone else's hot cache.

## Zero-copy

The normal path for serving a file copies it twice: disk → page cache → user buffer → socket buffer.

```c
sendfile(out_fd, in_fd, NULL, count);              // kernel-to-kernel, no user-space copy
splice(fd_in, NULL, fd_out, NULL, len, 0);         // via a pipe, more general
```

`sendfile` is how nginx and Kafka serve static content fast — the data never enters user space, saving two copies and the associated cache pressure. It's a real, measurable win for file-serving workloads, and irrelevant if you're transforming the data anyway.

---

## Related
- [[foundations/os/08-io-models|I/O Models]] — blocking, epoll, io_uring
- [[foundations/os/04-virtual-memory|Virtual Memory]] — the page cache from the memory side
- [[devops/01-linux/18-disks-and-filesystems|Linux: Disks and Filesystems]] — the operational view
- [[databases/database-design-reference|Database Design]] — why durability costs what it does
- [[foundations/os/README|OS course map]]
