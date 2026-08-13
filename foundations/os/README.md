# Operating Systems

The layer directly beneath [[foundations/networking/README|networking]], [[languages/01-java/02-jvm-and-concurrency/README|the JVM]], [[devops/01-linux/README|Linux]], and every container you'll ever run. Processes, memory, scheduling, and I/O — the machinery your runtime is standing on.

## Honest status: partially built

This folder is **one written note plus an interview bank**, not yet a full course like [[foundations/networking/README|networking]] or [[architecture/04-distributed-systems/README|distributed systems]]. Flagging that rather than implying otherwise — the vault's convention is to say what's scaffold.

What exists is genuinely useful, and the interview bank covers the questions that actually get asked. The gap is a proper numbered curriculum.

1. [[foundations/os/fundamentals|OS Fundamentals]] — **[Beginner→Intermediate]** — the existing overview note
2. [[foundations/os/interview/README|interview/]] — processes vs threads, virtual memory and page faults, syscall cost, the page cache, scheduling and cgroup throttling, deadlock, blocking vs async I/O, fork/exec, dynamic linking, "everything is a file"

## Where OS material actually lives in this vault right now

Because the folder is thin, a lot of OS knowledge is distributed across the domains that consume it. If you're looking for something specific:

| Topic | Where it's covered |
|---|---|
| **File descriptors, `epoll`, `io_uring`, C10K** | [[foundations/networking/09-sockets-and-the-network-api\|networking/09-sockets]] |
| **Namespaces, cgroups, what a container *is*** | [[devops/interview/01-linux-containers-and-operations\|devops interview Q3]] |
| **Processes, systemd, signals, permissions** | [[devops/01-linux/06-process-management\|devops/01-linux]] |
| **Memory model, GC, cache lines, false sharing** | [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals\|jvm-internals]] |
| **Virtual threads vs OS threads** | [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads\|virtual-threads]] |
| **Storage, boot, SELinux** | [[devops/01-linux/15-rhcsa/README\|the RHCSA track]] |

## If you build this out

The curriculum that would fit the vault's shape, in reading order — a reasonable plan, not a promise:

1. **What an OS is** — the kernel/user split, privilege rings, why the abstraction exists
2. **Processes & threads** — address spaces, `fork`/`exec`, the process lifecycle, zombies
3. **Scheduling** — CFS/EEVDF, priorities, affinity, NUMA, cgroup CPU quota and throttling
4. **Virtual memory** — page tables, the TLB, page faults, mmap, overcommit, the OOM killer
5. **Memory allocation** — the heap, allocators, fragmentation, huge pages
6. **Concurrency primitives** — futexes, atomics, memory barriers (the layer under [[languages/01-java/02-jvm-and-concurrency/02-concurrency\|Java's memory model]])
7. **File systems & I/O** — inodes, the page cache, `fsync` and the durability boundary, journaling
8. **The I/O evolution** — blocking → `epoll` → `io_uring` (already half-covered in [[foundations/networking/09-sockets-and-the-network-api\|sockets]])
9. **Syscalls & the ABI** — the boundary, its cost, and what KPTI did to it
10. **Isolation** — namespaces, cgroups, seccomp, capabilities — i.e. containers from below

**The best way to learn this is not to read it.** *Operating Systems: Three Easy Pieces* (free online) plus writing a toy shell, a toy allocator, and a toy scheduler will teach more than any set of notes — which is exactly the [[PRIMETECHIE|Rank III]] argument.

## Related
- [[foundations/networking/README|Networking]] — the layer above, built on sockets and file descriptors
- [[devops/01-linux/README|Linux]] — the practical, command-line-facing view of the same machine
- [[languages/01-java/02-jvm-and-concurrency/README|JVM & Concurrency]] — these primitives as a managed runtime exposes them
- [[PRIMETECHIE|The Primetechie Path]] — Rank II–III depth material
