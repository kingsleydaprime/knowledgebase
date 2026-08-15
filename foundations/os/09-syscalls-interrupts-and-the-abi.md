# Syscalls, Interrupts and the ABI

**[Advanced]** — Crossing the privilege boundary, what it costs, and the one mechanism that handles system calls, hardware interrupts, page faults and division by zero.

## One mechanism, four names

The CPU has a single way to transfer control to the kernel: a **trap into an interrupt handler**. Everything that enters the kernel uses it:

| Event | Source | Synchronous? |
|---|---|---|
| **System call** | your program, deliberately | yes |
| **Exception / fault** | your program, accidentally (page fault, divide by zero) | yes |
| **Hardware interrupt** | a device (NIC, disk, timer) | **no** |
| **Inter-processor interrupt** | another CPU core | no |

The CPU consults the **IDT** (Interrupt Descriptor Table) — a table of handler addresses set up at boot — switches to ring 0 and to the kernel stack, and jumps.

That "switch to the kernel stack" matters: the kernel can't trust the user stack pointer, so every task has a separate kernel stack (~16KB) that the trap mechanism switches to automatically.

## Making a system call

```c
write(fd, buf, n);        // libc wrapper
```

What actually happens on x86-64:

```asm
mov rax, 1          ; syscall number (1 = write)
mov rdi, fd         ; arg 1
mov rsi, buf        ; arg 2
mov rdx, n          ; arg 3
syscall             ; TRAP — switch to ring 0, jump to the handler
                    ; return value in rax; negative = -errno
```

The **calling convention is fixed by the ABI**: number in `rax`, arguments in `rdi, rsi, rdx, r10, r8, r9` (note `r10`, not `rcx` — the `syscall` instruction clobbers `rcx`). Maximum six arguments; anything larger goes by pointer to a struct.

`syscall`/`sysret` replaced the old `int 0x80` software interrupt because they're substantially faster — no IDT lookup, just a jump to a preconfigured address in an MSR.

```bash
strace ./prog                    # every syscall, arguments, return value
strace -c ./prog                 # counts and time — the ground truth for I/O behaviour
cat /usr/include/asm/unistd_64.h # the numbers
```

**Syscall numbers are a permanent ABI commitment.** Linux never changes or reuses them, which is why a binary from 2005 still runs. New functionality gets a new number (`openat` alongside `open`, `epoll_pwait2` alongside `epoll_wait`).

## What it costs

| | Cost |
|---|---|
| Function call | ~1–2ns |
| Syscall (pre-2018) | ~50–100ns |
| **Syscall (post-Spectre/Meltdown)** | **~200–1000ns** |
| Context switch | ~1–3µs |

The direct cost is privilege transition and register saving. The indirect cost is worse: the kernel's working set displaces yours in L1/L2, so your code resumes with a cold cache.

**The mitigations made this several times worse.** [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Meltdown]] forced **KPTI** (Kernel Page Table Isolation) — the kernel's pages are no longer mapped into the user address space, so every syscall now switches page tables, flushing TLB entries. Spectre mitigations added `retpoline` and IBPB on top.

The measured effect was **5–30% throughput loss on syscall-heavy workloads**, which is why 2018 was a bad year for database operators.

```bash
cat /sys/devices/system/cpu/vulnerabilities/*     # what's mitigated on this machine
mitigations=off                                    # kernel cmdline — faster, and don't
```

**This cost is why batching matters** and why `io_uring` exists: one syscall submitting fifty operations beats fifty syscalls. It's also why buffered `printf` beats unbuffered `write` in a loop by orders of magnitude.

## vDSO — the syscalls that aren't

Some calls are read-only and extremely frequent. Trapping for them is pure waste:

```c
clock_gettime(CLOCK_MONOTONIC, &ts);    // ~25ns — NO syscall
gettimeofday(&tv, NULL);
getcpu(...);
time(NULL);
```

The **vDSO** (virtual dynamic shared object) is a small shared library the kernel maps into every process. It contains real code plus a page of kernel-maintained data (the current time, updated by the timer interrupt). `clock_gettime` reads that page directly in user space.

```bash
cat /proc/self/maps | grep vdso
LD_SHOW_AUXV=1 /bin/true | grep VDSO
```

**This is why timing code is cheap.** A benchmark calling `clock_gettime` a million times isn't making a million syscalls. It also explains why `strace` shows no `clock_gettime` — there's nothing to trace.

## Interrupts

A device raises a signal; the CPU stops what it's doing and jumps to a handler.

```bash
cat /proc/interrupts       # per-CPU counts per IRQ — where they're landing
```

**Top half / bottom half.** An interrupt handler runs with interrupts disabled on that core, so it must be extremely short. Linux splits the work:

- **Top half** (the hard IRQ): acknowledge the device, copy the minimum, schedule the rest. Microseconds
- **Bottom half** (softirq / tasklet / workqueue): the real processing, with interrupts enabled and preemption possible

This is why `ksoftirqd` appears in `top` under heavy network load — the bottom half of packet processing.

### Interrupt storms and NAPI

At 10Gb/s a NIC can raise millions of interrupts per second, and the machine spends all its time in interrupt context — **livelock**: 100% CPU, zero throughput.

**NAPI** is the fix: on the first packet, disable that queue's interrupts and switch to **polling** while traffic is heavy, re-enabling interrupts when it goes idle. Interrupts for low load, polling for high load, automatically.

```bash
ethtool -c eth0            # interrupt coalescing settings
ethtool -l eth0            # queue count
cat /proc/irq/<n>/smp_affinity     # which CPU handles this IRQ
```

**IRQ affinity matters at high packet rates**: pinning a NIC queue's interrupt to the same core as the thread processing it keeps the data in that core's cache. `irqbalance` does this automatically and is sometimes worth disabling in favour of manual pinning. → [[foundations/networking/15-network-performance|Network Performance]]

## Faults and exceptions

Synchronous traps caused by the instruction being executed:

| Fault | Cause | Result |
|---|---|---|
| **Page fault** | address not currently mapped | usually **fixed transparently** → [[foundations/os/04-virtual-memory\|VM]] |
| **General protection** | privileged instruction in ring 3 | `SIGSEGV` |
| **Divide by zero** | | `SIGFPE` |
| **Invalid opcode** | | `SIGILL` |
| **Double fault** | a fault while handling a fault | kernel panic |

**Page faults are the interesting case** because most are not errors — they're the mechanism that makes demand paging, copy-on-write, and `mmap` work. The kernel fixes the mapping and re-executes the faulting instruction, and your program never knows.

A `SIGSEGV` is just a page fault the kernel decided was illegitimate.

## The ABI

The **Application Binary Interface** is the contract between compiled code and everything else: how arguments are passed, how the stack is laid out, how structs are padded, how names are mangled.

The System V AMD64 ABI (Linux, macOS, BSD) says: integer arguments in `rdi, rsi, rdx, rcx, r8, r9`, floats in `xmm0-7`, return in `rax`, and a **128-byte red zone** below the stack pointer that leaf functions may use without adjusting `rsp`.

Windows uses a different convention (`rcx, rdx, r8, r9`, 32-byte shadow space), which is one reason cross-platform binaries aren't a thing.

**Why this matters to you:**

**FFI depends on it.** [[languages/03-rust/15-unsafe-and-ffi|Rust calling C]], Go's cgo, Python's ctypes and the JNI all work because everyone agrees on the C ABI. It's the lingua franca.

**`extern "C"` disables C++ name mangling**, so the symbol is findable. → [[languages/05-cpp/01-why-cpp-and-what-it-added|C++]]

**Struct layout is part of the contract.** Padding and alignment must match on both sides, which is why `#[repr(C)]` exists in Rust. → [[languages/04-c/08-structs-unions-and-layout|C: Struct Layout]]

**Linux's userspace ABI is famously stable.** "We do not break userspace" is the kernel's hardest rule — syscall numbers and semantics are permanent. The *internal* kernel ABI is explicitly unstable, which is why out-of-tree modules break on every kernel upgrade and why vendors want their drivers upstreamed.

## Seeing the boundary

```bash
strace -c ./prog                              # which syscalls, how many, how long
strace -f -e trace=openat ./prog              # follow forks, filter
ltrace ./prog                                 # library calls instead
perf trace ./prog                             # lower overhead than strace
perf stat -e 'syscalls:sys_enter_*' ./prog
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'
```

**`strace -c` is the first thing to run on any I/O-shaped performance problem.** A program making 50,000 `write` calls where 50 would do is instantly visible, and it's a common finding.

Be aware `strace` uses `ptrace` and stops the process on **every** syscall — it can slow a program 10–100×. `perf trace` and bpftrace are far cheaper for production.

## eBPF

The modern way to observe (and extend) the kernel: run verified, sandboxed bytecode at kernel hook points without writing a module.

```bash
bpftrace -e 'kprobe:do_sys_openat2 { printf("%s %s\n", comm, str(arg1)); }'
```

Attach to syscalls, kernel functions, tracepoints, or network paths. The verifier proves termination and memory safety before loading, so a bad program is rejected rather than panicking the machine.

This is what `bcc`, `bpftrace`, Cilium, Falco and most modern observability tooling are built on — and it's arguably the most significant Linux addition of the last decade, because it made the kernel programmable without the risk that made kernel modules terrifying.

---

## Related
- [[foundations/os/01-what-an-os-is|What an OS Is]] — the privilege boundary being crossed
- [[foundations/os/08-io-models|I/O Models]] — why batching syscalls matters
- [[foundations/os/10-signals-and-ipc|Signals and IPC]] — the kernel interrupting *you*
- [[languages/03-rust/15-unsafe-and-ffi|Rust: FFI]] — the ABI in use
- [[foundations/os/README|OS course map]]
