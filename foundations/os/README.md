# Operating Systems

The layer directly beneath [[foundations/networking/README|networking]], [[languages/01-java/02-jvm-and-concurrency/README|the JVM]], [[devops/01-linux/README|Linux]], and every container you'll ever run. Processes, memory, scheduling, and I/O — the machinery your runtime is standing on.

**~17,000 words across 12 notes**, built August 2026 against the curriculum this README used to propose. `[reference]`.

> **The honest caveat, unchanged:** the best way to learn this is not to read it. *Operating Systems: Three Easy Pieces* (free online) plus writing a toy shell, a toy allocator and a toy scheduler will teach more than any set of notes — including these. They exist so the vocabulary is in place and the cross-domain links work. [[PRIMETECHIE|Reading is not a rank.]]

## Reading order

**Foundations**

1. [[foundations/os/01-what-an-os-is|What an OS Is]] — **[Beginner → Intermediate]** — the kernel/user split enforced by hardware, monolithic vs microkernel, and the abstractions the kernel exposes
2. [[foundations/os/02-processes-and-threads|Processes and Threads]] — **[Beginner → Intermediate]** — what a process consists of, why `fork`/`exec` is split, copy-on-write, zombies, and what a thread shares
3. [[foundations/os/03-scheduling|Scheduling]] — **[Intermediate]** — CFS and EEVDF, context-switch cost, NUMA, and **cgroup CPU throttling** — the reason services are mysteriously slow in Kubernetes

**Memory**

4. [[foundations/os/04-virtual-memory|Virtual Memory]] — **[Intermediate → Advanced]** — page tables, the TLB, page faults, overcommit, the OOM killer, and why `free` showing no free memory is correct
5. [[foundations/os/05-memory-allocation|Memory Allocation]] — **[Intermediate → Advanced]** — what `malloc` really does, why freed memory doesn't return to the OS, and how fragmentation looks like a leak

**Concurrency**

6. [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — **[Advanced]** — atomics, memory barriers, and **futexes** — why an uncontended lock costs 20ns and a contended one costs 100× that

**Storage and I/O**

7. [[foundations/os/07-filesystems-and-storage|Filesystems and Storage]] — **[Intermediate → Advanced]** — inodes, the page cache, journaling, and **`fsync`** — the boundary where "written" starts to mean something
8. [[foundations/os/08-io-models|I/O Models]] — **[Intermediate → Advanced]** — blocking → `epoll` → `io_uring`, and where every runtime you use actually sits

**The boundary**

9. [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls, Interrupts and the ABI]] — **[Advanced]** — one trap mechanism for four things, what Meltdown did to syscall cost, the vDSO, and eBPF
10. [[foundations/os/10-signals-and-ipc|Signals and IPC]] — **[Intermediate → Advanced]** — signal-handler constraints, `signalfd`, pipes, Unix sockets and fd passing, shared memory

**Putting it together**

11. [[foundations/os/11-isolation-and-containers|Isolation and Containers]] — **[Intermediate → Advanced]** — **there is no such thing as a container.** Namespaces, cgroups, capabilities, seccomp, overlayfs
12. [[foundations/os/12-boot-and-init|Boot and Init]] — **[Intermediate]** — firmware to login prompt, initramfs, and what PID 1 owes you

**Also here:**
- [[foundations/os/fundamentals|OS Fundamentals]] — the original overview note. Shorter, and still the gentlest entry point
- [[foundations/os/interview/README|interview/]] — processes vs threads, page faults, syscall cost, the page cache, scheduling, deadlock, blocking vs async I/O, `LD_PRELOAD`, "everything is a file"

## The five things worth carrying

If the rest fades, these keep paying:

1. **An uncontended mutex is ~20ns; a contended one is ~1–10µs.** A futex only enters the kernel on contention. Shorten critical sections, don't avoid locks → [[foundations/os/06-concurrency-primitives|06]]
2. **cgroup CPU quota is a cliff, not a slope.** Exhaust it early in a period and every thread freezes until the next one. Check `nr_throttled` → [[foundations/os/03-scheduling|03]]
3. **`write` returns before anything is durable.** `fsync` is the boundary, it costs milliseconds, and its errors are not retryable → [[foundations/os/07-filesystems-and-storage|07]]
4. **A container is namespaces + cgroups + a pivot_root.** Not a kernel object → [[foundations/os/11-isolation-and-containers|11]]
5. **Read `available`, not `free`.** The page cache using all your RAM is correct → [[foundations/os/04-virtual-memory|04]]

## Where this connects

OS knowledge is load-bearing across the vault, and these notes are deliberately the *deep* version of things covered practically elsewhere:

| Topic | Also covered in |
|---|---|
| **File descriptors, `epoll`, C10K** | [[foundations/networking/09-sockets-and-the-network-api\|networking/09-sockets]] |
| **Namespaces, cgroups from above** | [[devops/02-docker/README\|Docker]] · [[devops/05-orchestration/README\|Orchestration]] |
| **Processes, systemd, signals from the shell** | [[devops/01-linux/06-process-management\|linux/06]] · [[devops/01-linux/07-systemd-and-services\|linux/07]] |
| **The memory model, GC, false sharing** | [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals\|jvm-internals]] |
| **Green threads over OS threads** | [[languages/02-go/06-goroutines-and-channels\|goroutines]] · [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads\|virtual threads]] · [[languages/03-rust/14-async-and-tokio\|tokio]] |
| **Writing an event loop** | [[backend/frameworks/c/01-the-accept-loop-and-event-loops\|C: The Accept Loop]] |
| **Storage, boot, SELinux operationally** | [[devops/01-linux/15-rhcsa/README\|the RHCSA track]] |

## Known gaps

- **No project.** The [[BUILD-PLAN|build-your-own-x]] shell and OS guides are where this becomes knowledge
- **Device drivers** — the kernel's largest and buggiest surface, entirely uncovered
- **Kernel modules** — writing, loading, and why the internal ABI is deliberately unstable
- **Real-time Linux** — PREEMPT_RT, latency guarantees. Relevant to [[robotics/README|robotics]]
- **Kernel networking internals** — the path from NIC to socket, beyond what [[foundations/networking/README|networking]] covers
- **Windows and macOS** — this is Linux-shaped throughout

## Related
- [[foundations/networking/README|Networking]] — the layer above, built on sockets and file descriptors
- [[devops/01-linux/README|Linux]] — the same machine from the command line
- [[foundations/computer-architecture/README|Computer Architecture]] — the layer directly below: the TLB behind virtual memory, cache coherence behind concurrency primitives, and memory models behind atomics
- [[languages/04-c/README|C]] — the language all of this is written in
- [[PRIMETECHIE|The Primetechie Path]] — Rank II–III depth material
