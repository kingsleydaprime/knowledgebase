# What an OS Is

**[Beginner → Intermediate]** — The kernel/user split, why hardware enforces it, and the three jobs an operating system actually does.

**Source:** `[reference]` — built out August 2026 from the plan in [[foundations/os/README|the OS README]]. The overview note [[foundations/os/fundamentals|fundamentals]] covers the same ground more briefly.

## The three jobs

Strip away everything else and an OS does three things:

**1. Abstraction.** Your program says `write(fd, buf, n)`. It doesn't know whether that's an SSD, a network socket, a pipe, or a terminal — and it doesn't know the disk's command protocol, sector size, or interrupt vector. The OS turns wildly different hardware into a few uniform interfaces.

**2. Arbitration.** One CPU, many processes. One block of RAM, many address spaces. The OS decides who gets what, when, and stops any one program from taking everything.

**3. Isolation.** A crashing process must not take down the machine. A malicious process must not read another's memory. This is the job that needs hardware help.

Everything else — filesystems, scheduling, virtual memory, networking — is an implementation of one of those three.

## The kernel/user split

The central structural fact:

```
┌─────────────────────────────────────────┐
│  USER SPACE (ring 3)                    │
│  your program, libc, the shell, nginx   │
│  • cannot touch hardware directly       │
│  • cannot see other processes' memory   │
│  • cannot execute privileged instructions│
└──────────────┬──────────────────────────┘
               │  syscall boundary
┌──────────────▼──────────────────────────┐
│  KERNEL SPACE (ring 0)                  │
│  scheduler, memory manager, drivers, VFS │
│  • full hardware access                 │
│  • sees all physical memory             │
│  • a bug here kills the machine         │
└─────────────────────────────────────────┘
```

**This is enforced by the CPU, not by the OS.** x86 has four privilege levels ("rings"); Linux uses two — ring 0 for the kernel, ring 3 for everything else. ARM calls them exception levels (EL0/EL1). Certain instructions — loading the page table base register, disabling interrupts, doing raw I/O — **fault** if executed in ring 3.

That hardware enforcement is what makes isolation real rather than a convention. Without it, "don't touch other processes' memory" would be a request.

The consequence you feel daily: **anything interesting requires asking the kernel**, and asking costs a privilege transition. → [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls, Interrupts and the ABI]]

## Why a bug in the kernel is different

A segfault in your program kills your program. A null dereference in a kernel driver panics the machine, because there's nothing above it to catch the fault.

This asymmetry drives a lot of design:

- **Drivers are the largest source of kernel bugs** — they're the biggest, least-reviewed part of the code and written by hardware vendors
- **Rust in the kernel** exists specifically to reduce this class of failure
- **Microkernels** move drivers into user space so a driver crash is recoverable

## Monolithic vs microkernel

The oldest architectural argument in the field.

**Monolithic** — the whole kernel is one program in one address space. Filesystems, drivers, network stack, scheduler all call each other directly as functions.

- Fast: a filesystem calling into a block driver is a function call
- Fragile: any bug can corrupt any kernel structure
- Linux, Windows NT (mostly), BSD

**Microkernel** — the kernel does only IPC, scheduling, and memory. Filesystems, drivers, and the network stack are ordinary user-space processes.

- Robust: a crashed driver restarts; it can't corrupt the kernel
- Slower: a filesystem calling a driver is IPC — a context switch, not a function call
- QNX, seL4, MINIX 3, Fuchsia's Zircon

The Tanenbaum–Torvalds debate (1992) argued this out publicly, and the practical answer turned out to be "monolithic won on performance, then borrowed the good ideas":

- **Loadable kernel modules** give monolithic kernels dynamic driver loading
- **FUSE** puts filesystems in user space when robustness matters more than speed
- **DPDK / SPDK / io_uring** move networking and storage back toward user space for performance
- **Hybrid kernels** (macOS's XNU) blend both

Meanwhile microkernels won where correctness is non-negotiable: seL4 is formally verified and used in aviation and defence; QNX runs in cars.

**Where this matters to you:** it explains why a Linux driver bug is a kernel panic, why FUSE filesystems are slower, and why "just do it in user space" is a real performance strategy for I/O. → [[foundations/os/08-io-models|I/O Models]]

## The abstractions the kernel exposes

Almost everything a program does resolves to one of these:

| Abstraction | Really is | Note |
|---|---|---|
| **Process** | an address space + threads + open files | → [[foundations/os/02-processes-and-threads\|02]] |
| **Thread** | a schedulable execution context | shares the address space |
| **File descriptor** | an index into a per-process table | the universal I/O handle |
| **Virtual memory** | a per-process address→page mapping | → [[foundations/os/04-virtual-memory\|04]] |
| **Signal** | asynchronous notification | → [[foundations/os/10-signals-and-ipc\|10]] |
| **Socket** | a file descriptor for a network endpoint | → [[foundations/networking/09-sockets-and-the-network-api\|sockets]] |

### "Everything is a file"

The Unix design decision that keeps paying off: files, directories, devices, pipes, sockets, and kernel state all appear as file descriptors, and all respond to `read`, `write`, `close`.

```bash
cat /proc/self/status        # kernel data, read like a file
echo 1 > /proc/sys/net/ipv4/ip_forward   # kernel configuration, written like a file
cat /dev/urandom | head -c 16            # a device, read like a file
```

The payoff isn't philosophical — it's that **one set of tools works on everything**. Shell redirection, `select`/`epoll`, permissions, and `strace` all operate on file descriptors, so they compose across every kind of object without special cases.

The limits are real too: `ioctl()` exists precisely because some devices need operations that don't fit read/write, and it's the ugly escape hatch the abstraction leaks through.

## `/proc` and `/sys`

Two pseudo-filesystems that are the practical interface to kernel state:

```bash
/proc/<pid>/status      # process state, memory, threads
/proc/<pid>/maps        # the process's address space  → 04-virtual-memory
/proc/<pid>/fd/         # its open file descriptors
/proc/meminfo           # system memory
/proc/cpuinfo
/sys/fs/cgroup/         # cgroup limits  → 11-isolation-and-containers
/sys/block/             # block devices
```

`/proc` is process and kernel information; `/sys` is the device model and tunables. Neither exists on disk — reads are handled by kernel functions at the moment you read them.

**These are your primary debugging tools for anything OS-shaped.** Most of what `top`, `ps`, and `free` report comes from `/proc`.

## Where the boundary actually is

Worth being precise, because it's commonly misunderstood:

- **`printf` is not a syscall.** It's libc, which formats into a buffer and eventually calls `write`
- **`malloc` is not a syscall.** It's an allocator that calls `brk` or `mmap` occasionally → [[foundations/os/05-memory-allocation|05]]
- **Threads are not a libc concept.** `pthread_create` calls `clone` → [[foundations/os/02-processes-and-threads|02]]

The C standard library is a *user-space* layer that batches, caches, and abstracts over syscalls. Confusing the two makes performance reasoning wrong — buffered `printf` in a loop costs almost nothing, unbuffered `write` in a loop costs a syscall each time.

```bash
strace -c ./myprogram        # which syscalls, how many, how long — the ground truth
ltrace ./myprogram           # library calls instead
```

## The honest advice

> **The best way to learn this is not to read about it.** *Operating Systems: Three Easy Pieces* (free online) plus writing a toy shell, a toy allocator, and a toy scheduler teaches more than any set of notes — including these.

These notes exist so the vocabulary is in place and the cross-domain links work. The [[BUILD-PLAN|build-your-own-shit]] guides for a shell and an OS are where this becomes knowledge. [[PRIMETECHIE|Reading is not a rank.]]

---

## Related
- [[foundations/os/fundamentals|OS Fundamentals]] — the original overview note
- [[foundations/os/02-processes-and-threads|Processes and Threads]] — the first real abstraction
- [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls, Interrupts and the ABI]] — crossing the boundary
- [[devops/01-linux/README|Linux]] — the same machine from the command line
- [[foundations/os/README|OS course map]]
