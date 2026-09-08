# Virtual Memory

**[Intermediate → Advanced]** — The abstraction that makes isolation possible, why `free` shows almost no free memory, and what the OOM killer is actually deciding.

## The lie every process is told

Every process believes it has the entire address space to itself, starting at zero, contiguous, all its own. On 64-bit Linux that's 128TB of user space per process on a machine with 16GB of RAM.

The MMU (memory management unit) translates **virtual addresses** to **physical addresses** on every single memory access, using per-process page tables.

What this buys:

- **Isolation** — process A's address `0x1000` and process B's map to different physical pages. Neither can name the other's memory
- **No relocation problem** — every program can be compiled to load at the same address
- **Overcommit** — allocate more than you have, as long as you don't touch it all
- **Sharing** — one physical copy of libc mapped into every process
- **Swap** — a page can live on disk, faulted back on access

## Page tables

Memory is divided into **pages**, 4KB by default. A virtual address splits into indices into a multi-level table plus an offset:

```
64-bit virtual address (4-level paging, 48 bits used):
┌────────┬────────┬────────┬────────┬────────────┐
│ PML4   │ PDPT   │ PD     │ PT     │ offset     │
│ 9 bits │ 9 bits │ 9 bits │ 9 bits │ 12 bits    │
└────────┴────────┴────────┴────────┴────────────┘
     │        │        │        │         └→ byte within the 4KB page
     └────────┴────────┴────────┴→ four memory accesses to find the physical page
```

**A translation costs up to four memory reads** — which would make every access five times slower. Hence the TLB.

Page tables are sparse: only levels covering mapped regions exist, so an address space with three small mappings costs a few kilobytes of tables rather than gigabytes.

5-level paging exists for machines needing more than 128TB.

## The TLB

The **Translation Lookaside Buffer** caches recent virtual→physical translations. A hit costs ~1 cycle; a miss costs the full page walk.

Typically a few thousand entries. At 4KB per entry, that covers only a few megabytes — so a program with a large working set and scattered access misses constantly.

**Two consequences that matter:**

**Context switches flush it** (or did, before PCID/ASID tagging), which is a large part of a context switch's real cost. → [[foundations/os/03-scheduling|Scheduling]]

**Huge pages exist to reduce pressure.** A 2MB page covers 512× the memory per TLB entry:

```bash
cat /sys/kernel/mm/transparent_hugepage/enabled     # THP: always / madvise / never
```

**Transparent huge pages are a mixed blessing.** They help large sequential workloads and cause latency spikes elsewhere — `khugepaged` compacting memory to form 2MB blocks can stall a process for milliseconds. **Most databases (Redis, MongoDB, Postgres) recommend disabling THP** and using explicit hugepages instead. If you see unexplained multi-millisecond pauses, check THP first.

## Page faults

The CPU raises a fault when a virtual address isn't currently mapped to a physical page. **This is normal and constant**, not an error.

**Minor fault** — the page is in memory but not in this process's page table. Map it and continue. Microseconds.

- First touch of a `malloc`'d page
- Copy-on-write after `fork`
- A shared library already in the page cache

**Major fault** — the data isn't in RAM. Read it from disk. **Milliseconds on spinning disks, ~100µs on NVMe** — thousands of times slower.

- Reading a file page not in the page cache
- Faulting a page back from swap

```bash
ps -o min_flt,maj_flt -p <pid>
/usr/bin/time -v ./prog           # both counts
perf stat -e page-faults,minor-faults,major-faults ./prog
```

**High major-fault rates mean you're thrashing** — the working set exceeds RAM and you're paging constantly. The machine appears busy while accomplishing almost nothing, and load average climbs. It's one of the clearest "add RAM or reduce footprint" signals.

**Invalid access** — the address isn't mapped at all. The kernel sends `SIGSEGV`. That's a segfault: not a hardware failure, just a page fault the kernel decided was illegitimate.

## Demand paging and overcommit

```c
void *p = malloc(1024 * 1024 * 1024);    // 1GB — succeeds instantly
                                          // NO physical memory allocated yet
p[0] = 1;                                 // page fault → ONE 4KB page allocated
```

**Allocation reserves address space; physical pages arrive on first touch.** That's demand paging, and it's why `malloc` of a gigabyte is instant.

```bash
cat /proc/sys/vm/overcommit_memory
# 0 = heuristic (default)  1 = always allow  2 = strict accounting
```

Overcommit is what makes `fork` viable for large processes and what lets a JVM reserve a huge heap it never fills. It also means **a successful `malloc` is not a promise** — the failure surfaces later, when you touch the memory and there's none left.

That's when the OOM killer runs.

## The OOM killer

When the kernel cannot free a page and cannot fail an allocation, it picks a process to kill.

```bash
cat /proc/<pid>/oom_score          # computed; higher = more likely victim
echo -1000 > /proc/<pid>/oom_score_adj    # -1000 = never kill (needs privilege)
dmesg | grep -i "killed process"          # the evidence, after the fact
```

The score is roughly proportional to memory used, so **the biggest process usually dies — which is often your database, not the leaking process that caused it.**

In containers this is sharper:

```bash
/sys/fs/cgroup/memory.max          # hard limit — exceeding it OOM-kills within the cgroup
/sys/fs/cgroup/memory.high         # soft limit — throttles and reclaims aggressively instead
/sys/fs/cgroup/memory.current
/sys/fs/cgroup/memory.events       # oom_kill count
```

**A container hitting `memory.max` gets killed with exit code 137** (128 + SIGKILL). That's the `OOMKilled` status in Kubernetes, and the most common cause of mysterious pod restarts.

`memory.high` is the underused one — it applies reclaim pressure and slows the cgroup rather than killing it, which is usually what you want for a service with a lumpy allocation profile.

Runtimes need telling about the limit, same as with CPU:

```bash
GOMEMLIMIT=450MiB              # Go — a soft limit; the GC works harder as you approach
-XX:MaxRAMPercentage=75.0      # JVM
```

Without these, the runtime sizes its heap from the *host's* memory and gets killed before its GC ever feels pressure. → [[languages/02-go/13-performance-and-runtime|Go: the runtime]]

## The page cache — why `free` shows no free memory

```bash
$ free -h
              total        used        free      shared  buff/cache   available
Mem:           16Gi       4.0Gi       200Mi       100Mi        12Gi        11Gi
```

**`free` being near zero is correct and healthy.** The kernel uses all spare RAM to cache file contents — the **page cache**. Unused RAM is wasted RAM.

**Read `available`, not `free`.** `available` estimates what you could allocate, counting reclaimable cache. Cache is evicted instantly under pressure.

Every file read goes through the page cache: a second read of the same file is a memory copy, not disk I/O. It's the single biggest reason filesystem performance is tolerable.

```bash
sync && echo 3 > /proc/sys/vm/drop_caches    # drop it — for benchmarking ONLY
vmtouch -v /path/to/file                      # what's actually cached
```

## `mmap`

Map a file (or anonymous memory) directly into the address space:

```c
void *addr = mmap(NULL, len, PROT_READ, MAP_PRIVATE, fd, 0);
// now read the file by dereferencing pointers — no read() syscall
```

| Flag | Meaning |
|---|---|
| `MAP_PRIVATE` | copy-on-write; writes don't hit the file |
| `MAP_SHARED` | writes go to the file, visible to other mappers |
| `MAP_ANONYMOUS` | not backed by a file — this is how `malloc` gets large blocks |
| `MAP_POPULATE` | fault it all in now, avoiding later stalls |

**When `mmap` beats `read`:** random access over a large file, sharing between processes, and avoiding a copy (`read` copies page cache → your buffer; `mmap` maps the same pages).

**When it doesn't:** sequential streaming (`read` with readahead is competitive and simpler), small files (setup cost dominates), and any case where **you can't handle a `SIGBUS`** — if the file is truncated under you, touching a mapped page past the new end raises `SIGBUS`, not an error return.

`mmap` is how shared libraries load, how databases access data files, and how [[foundations/os/05-memory-allocation|allocators]] get memory from the kernel.

## Copy-on-write

Both processes' page tables point at the same physical pages, marked read-only. A write faults; the kernel copies that page and makes it writable for the writer.

Used for: `fork`, `MAP_PRIVATE` file mappings, and the zero page (all reads of untouched anonymous memory hit one shared zero-filled page until written).

**The practical consequence:** a forked child's memory usage grows as it writes. Redis's background save forks, and if the parent is taking heavy writes, the child's copy-on-write pages can approach a full copy of the dataset — the classic "Redis used 2× memory during a save" surprise.

## Swap

Move a page to disk, free the physical frame, mark the PTE not-present. Access faults it back.

```bash
swapon --show
cat /proc/sys/vm/swappiness       # 0-100; how eagerly to swap anonymous pages vs drop cache
```

**Swap is not "extra RAM".** Faulting from disk is thousands of times slower than RAM, so a system actively swapping its working set is unusable — you'll see load average climb while throughput collapses.

Its real value is evicting genuinely cold pages (a daemon that ran at startup and never runs again) to free RAM for the page cache.

**`swapaccount` and containers:** cgroup v2's `memory.swap.max` controls swap per cgroup. Kubernetes historically required swap disabled entirely, because a throttled-but-swapping pod makes scheduling decisions meaningless.

## Reading a process's memory

```bash
cat /proc/<pid>/maps         # every mapping: address range, perms, backing file
cat /proc/<pid>/smaps_rollup # aggregated: RSS, PSS, swap, shared vs private
pmap -x <pid>
```

The three numbers, and the difference matters:

- **VSZ / virtual** — address space reserved. Nearly meaningless; includes untouched allocations
- **RSS** — resident set size, physical pages currently mapped in. **Double-counts shared pages** across processes
- **PSS** — proportional set size: shared pages divided by the number of sharers. **The honest number** for "how much is this process actually costing"

Summing RSS across processes vastly overstates memory use, because every process counts the full size of shared libc. Sum PSS instead.

---

## Related
- [[foundations/os/05-memory-allocation|Memory Allocation]] — what `malloc` does with this
- [[foundations/os/07-filesystems-and-storage|Filesystems and Storage]] — the page cache from the other side
- [[foundations/os/11-isolation-and-containers|Isolation and Containers]] — cgroup memory limits
- [[languages/04-c/07-memory-management|C: Memory Management]] — the same picture from user space
- [[foundations/os/README|OS course map]]
