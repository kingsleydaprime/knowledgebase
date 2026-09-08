# OS Interview — Processes, Memory & I/O

From [[foundations/os/fundamentals|OS fundamentals]]. Depth probes — they're checking whether your model bottoms out at the runtime or goes below it.

---

### Q1. [Intermediate] 🔥 Process vs thread, and what does a context switch actually cost?

**Strong answer covers:** a **process** has its own virtual address space, file descriptor table, and permissions. A **thread** shares all of that with its siblings and has only its own stack, registers, and program counter. On Linux both are "tasks" to the scheduler — `clone()` with different flags decides what's shared, which is why the distinction is softer than textbooks imply.

**The cost, which is the real question:**
- **Thread → thread in the same process:** save/restore registers, scheduler bookkeeping. ~1–2 microseconds.
- **Process → process:** the above **plus a page-table switch**, which flushes TLB entries. The direct cost is similar, but the *indirect* cost is much higher — the new process runs with a cold TLB and cold caches, so it's slow for a while afterwards. That indirect cost usually dominates and is invisible in microbenchmarks.

**Why it matters:** at ~1–5 microseconds of real cost, a context switch is an eternity when your latency budget is sub-microsecond. That's the entire argument for **busy-spinning** instead of blocking in low-latency code, for [[languages/01-java/interview/02-jvm-and-concurrency|lock-free data structures]], and for **thread pinning** to keep a thread on one core with its cache warm.

---

### Q2. [Intermediate] 🔥 Explain virtual memory. What happens on a page fault?

**Strong answer covers:** every process sees its own flat address space; the MMU translates virtual → physical via page tables, cached in the **TLB**. This gives isolation (you can't address another process's memory), enables overcommit and sharing (the same physical page for a shared library across processes), and lets the OS relocate pages freely.

**On a page fault**, the address isn't currently mapped. Three cases, and distinguishing them is the answer:
- **Minor fault** — the page is in memory but not mapped in this process's tables (first touch of a lazily-allocated page, or a shared page already resident). Cheap — no I/O.
- **Major fault** — the page must be read from disk (swap, or a memory-mapped file). **Expensive** — a disk round trip, so the process blocks.
- **Invalid** — nothing there → `SIGSEGV`.

**Detail that scores:** **`malloc` doesn't allocate physical memory.** It reserves virtual address space; physical pages are assigned on first *touch*, via minor faults. That's why a process's virtual size (VSZ) can vastly exceed physical (RSS), why overcommit works, and why touching a large buffer once at startup ("pre-faulting") is a real low-latency technique — you pay the faults up front rather than at an unpredictable moment.

**Related:** huge pages reduce TLB pressure for large heaps; the **OOM killer** appears because Linux overcommits and eventually has to renege.

---

### Q3. [Intermediate] 🔥 What is a system call and why is it expensive?

**Strong answer covers:** a controlled transition from user mode to kernel mode — the CPU switches privilege level, the kernel validates arguments (it cannot trust user pointers), does the work, and returns.

**The cost:** the mode switch itself is now fairly cheap (`syscall`/`sysret` instructions), on the order of 100ns. But: it pollutes caches and branch predictors, may cause a reschedule, and — since **Spectre/Meltdown mitigations** (KPTI) — involves page-table switching that made syscalls significantly more expensive again. That's a nice detail to know: a *security* mitigation measurably changed the performance calculus for syscall-heavy workloads.

**Why it matters:** it's why batching syscalls is a real optimisation, and it drives the whole progression in [[foundations/networking/09-sockets-and-the-network-api|the sockets note]] — `select` → `epoll` → **`io_uring`**, where io_uring's headline feature is submitting many operations through a shared ring buffer with *no syscall at all* in the steady state.

---

### Q4. [Intermediate] What's the page cache, and why does `free` show almost no free memory?

**Strong answer covers:** the kernel caches file contents in otherwise-unused RAM. A read that hits the page cache never touches disk; writes go to the cache and are flushed later (which is why `fsync` exists and why "the write returned" ≠ "the data is durable").

**The `free` output:** memory used as page cache shows as "used" but is **reclaimable instantly** under pressure. This is why "Linux is using all my RAM!" is a non-problem — free RAM is wasted RAM. Read the `available` column, not `free`.

**Where it bites:**
- **Databases** often bypass or duplicate it (`O_DIRECT`) because they know their access patterns better than the kernel's LRU.
- **In containers**, page cache counts against the **cgroup memory limit** — so an application that reads lots of files can get OOM-killed by cache it doesn't control. A genuinely confusing production failure and a great thing to know.
- **`fsync` semantics** are the durability boundary; the 2018 "fsync gate" (Postgres discovering that a failed fsync could be reported once and then forgotten) is a good war story.

---

### Q5. [Intermediate] How does the scheduler decide what runs next?

**Strong answer covers:** Linux's **CFS** (Completely Fair Scheduler) tracks each task's **virtual runtime** and always runs the task with the lowest — approximating "everyone gets a fair share," weighted by nice value. In a red-black tree, so selection is O(log n). (Newer kernels use **EEVDF**, which improves latency fairness — worth knowing that CFS is being replaced.)

**Real-time classes** (`SCHED_FIFO`, `SCHED_RR`) sit above and preempt everything normal — used in trading and audio, and dangerous because a spinning RT thread can lock out the kernel.

**What matters for latency work:**
- **CPU affinity / pinning** (`taskset`, `isolcpus`) keeps a thread on one core so its cache stays warm and it isn't migrated.
- **NUMA** — memory attached to another socket is meaningfully slower. Pin memory with the thread.
- **`cgroups` CPU quota** — in Kubernetes, a CPU limit is enforced by **throttling within a 100ms period**, so a bursty application can be throttled while showing low average CPU utilisation. This is one of the most common and most misdiagnosed container performance problems, and naming it is a strong practical signal.

---

### Q6. [Intermediate] 🔥 What is a deadlock and how do you prevent one?

**Strong answer covers Coffman's four necessary conditions** — mutual exclusion, hold-and-wait, no preemption, circular wait. **Break any one and deadlock is impossible.**

**In practice, the one you break is circular wait:** impose a **global lock ordering** — always acquire locks in a consistent order (say, by memory address or ID). Simple, and it eliminates the entire class.

**Alternatives:** `tryLock` with a timeout and backoff (breaks hold-and-wait); take one coarse lock instead of several; or avoid shared mutable state entirely (message passing, immutability).

**Distinguish the neighbours, because they get conflated:**
- **Livelock** — threads are active but making no progress (each politely backing off for the other).
- **Starvation** — a thread never gets the resource because others keep winning.
- **Priority inversion** — a low-priority thread holds a lock a high-priority thread needs, and a medium-priority thread preempts the low one, blocking the high one indefinitely. This is the **Mars Pathfinder** bug; the fix is priority inheritance.

**How you'd diagnose it:** a thread dump — the JVM will explicitly report "Found one Java-level deadlock" with the cycle.

---

### Q7. [Intermediate] Blocking vs non-blocking vs async I/O.

**Strong answer covers:**
- **Blocking** — the thread sleeps until the operation completes. Simple, and costs a thread per concurrent operation.
- **Non-blocking** — the call returns immediately with "would block"; you must poll or use readiness notification (`epoll`). One thread handles many descriptors, but you must not block it.
- **Async (completion-based)** — you submit an operation and are notified when it's *done*, not when it's *ready*. `io_uring` on Linux, IOCP on Windows.

**The distinction people miss — readiness vs completion:** `epoll` tells you *"you can read now without blocking"*; you still do the read yourself. `io_uring` does the read for you and hands you the result. That's why `epoll` never worked properly for **file** I/O — a regular file is always "ready," so readiness notification is meaningless, and reads still block. Completion-based APIs are what finally fixed async file I/O on Linux.

**Bring it up a layer:** the same tension resolves in the language runtime — goroutines and [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|virtual threads]] give you blocking-style *code* on non-blocking *execution*. The programming model and the execution model never had to match.

---

### Q8. [Intermediate] What actually happens when a program starts?

**Strong answer covers:** `fork()` duplicates the current process — with **copy-on-write**, so pages are shared until one side writes, which is what makes fork cheap despite copying an address space. Then `exec()` replaces the process image with a new program.

**Then:** the kernel maps the ELF segments, loads the **dynamic linker**, which resolves shared library dependencies and relocations (lazily by default, via the PLT/GOT — which is why the first call to a library function is slower). Then control passes to `_start` → runtime init → `main`.

**Details worth adding:** the fork/exec split looks redundant but is elegant — between the two calls you're in a child process where you can freely set up redirections, close descriptors, and drop privileges before the new program exists. That's exactly how a shell implements pipes and `>` redirection. `posix_spawn` and `vfork` exist for when you don't need that and want to avoid duplicating a large address space.

---

### Q9. [Advanced] Why is `LD_PRELOAD` interesting, and what does that tell you about dynamic linking?

**Strong answer covers:** `LD_PRELOAD` loads a library *before* all others, so its symbols win resolution. You can transparently replace `malloc`, `open`, or any libc function without recompiling anything.

**Legitimate uses:** profilers and allocators (jemalloc, tcmalloc), `fakeroot`, network shims, debugging tools.

**Security implication:** it's a classic persistence and privilege-escalation technique, which is why it's **ignored for setuid binaries** — otherwise any user could inject code into a root program.

**What it tells you about dynamic linking:** symbol resolution is a **runtime name lookup**, not a compile-time binding. That's the same property that makes shared libraries updatable without relinking, that makes symbol interposition possible, and that causes "wrong library version" dependency hell. Static linking trades all of that away for a bigger, self-contained, more predictable binary — which is exactly why Go defaults to static and why distroless container images work.

---

### Q10. [Intermediate] 🔥 What does "everything is a file" actually buy you?

**Strong answer covers:** files, pipes, sockets, devices, and even kernel state (`/proc`, `/sys`) are all accessed through **file descriptors** with the same small API — `read`, `write`, `close`, `select`/`epoll`.

**What it buys:** composability. `epoll` works on sockets *and* pipes *and* timerfd *and* signalfd, so an event loop can wait on network I/O, timers, and signals in **one** call. Shell redirection and pipes work uniformly across every program ever written. A tool that reads stdin works on a file, a socket, or another program's output without knowing the difference.

**Where the abstraction leaks — and naming this is what separates a good answer:** an fd doesn't tell you message boundaries ([[foundations/networking/09-sockets-and-the-network-api|TCP is a byte stream]]), a successful `write` doesn't mean delivery, regular files are always "ready" so `epoll` is useless on them, and `open()` on a network filesystem can block for minutes in a way a local `open` never does. The uniform interface hides genuinely different failure modes, which is precisely where the hard bugs live.
