# Build Your Own OS

**[Advanced]** — The longest and hardest thing on this list. Weeks, not a weekend. Also the only one where you write code that runs with nothing underneath it.

## What you're building

A 64-bit kernel that boots on real hardware (or QEMU), prints to the screen, handles interrupts, manages physical and virtual memory, runs multiple processes with preemptive scheduling, and exposes a handful of syscalls.

By the end **it boots from a USB stick on a real machine.** That's the hook, and nothing else on this list compares to watching your own kernel print on hardware you own.

**What you're deliberately not building:** a usable OS. No shell you'd want, no networking, no USB stack, no graphics beyond a framebuffer, no real filesystem driver, no SMP. Linux is ~30 million lines.

**Why this one:** everything else you've built assumed an OS underneath. This is the bottom. It's also the only project here where a mistake means the machine triple-faults and reboots with no error message — which teaches a kind of care nothing else does.

> **Be honest about scope.** This is where people start and stop. **Get to milestone 3 (interrupts) and you've already learned more than most working engineers know about the boot path.** Everything past milestone 6 is a months-long commitment.

## What you need first

| You should know | Where |
|---|---|
| **C**, thoroughly — pointers, memory layout, `volatile`, UB | [[languages/04-c/README\|the C course]] |
| **The boot chain** | [[foundations/os/12-boot-and-init\|os/12]] |
| **Virtual memory and page tables** | [[foundations/os/04-virtual-memory\|os/04]] — **the hardest milestone depends on this** |
| **Processes, context switching** | [[foundations/os/02-processes-and-threads\|os/02]] · [[foundations/os/03-scheduling\|os/03]] |
| **Interrupts, syscalls, the ABI** | [[foundations/os/09-syscalls-interrupts-and-the-abi\|os/09]] |
| **Some x86-64 assembly** | not covered in the vault — see the gaps note in [[foundations/os/README\|os/README]] |

**You'll also need the [OSDev Wiki](https://wiki.osdev.org)**, which is the canonical reference and effectively the specification for this project. [Philipp Oppermann's *Writing an OS in Rust*](https://os.phil-opp.com) is the best modern tutorial in any language.

## Setup before milestone 1

**A cross-compiler.** Your system compiler targets your OS — it assumes libc, a dynamic loader, and a stack that exists. You need a **freestanding** toolchain:

```bash
x86_64-elf-gcc          # a cross-compiler, built or installed
# or with clang, which is natively a cross-compiler:
clang --target=x86_64-elf -ffreestanding -nostdlib -mno-red-zone
```

`-ffreestanding` says "no standard library, no assumptions". `-mno-red-zone` is **mandatory for kernel code** — the [[foundations/os/09-syscalls-interrupts-and-the-abi|red zone]] is 128 bytes below the stack pointer that leaf functions may use, and an interrupt handler will silently corrupt it.

**QEMU**, and use it for everything:

```bash
qemu-system-x86_64 -cdrom myos.iso -serial stdio -d int,cpu_reset -no-reboot
```

`-no-reboot` and `-d int` are the difference between "it reboots instantly and you learn nothing" and "you see the exception that killed it".

## The build order

### 1. Boot and print something

Use a bootloader — **do not write one**. Writing a bootloader teaches you 16-bit real mode, which no longer exists on modern hardware paths and isn't where the interesting material is.

**Limine** is the current best choice: it boots you directly into 64-bit long mode with paging enabled, a memory map, and a framebuffer already set up. GRUB with Multiboot2 is the traditional alternative and leaves you in 32-bit protected mode with more setup to do.

Then write to the framebuffer (or serial):

```c
void kmain(struct limine_framebuffer *fb) {
    // write pixels, or use the serial port for text
    for (;;) __asm__("hlt");
}
```

**Test:** `qemu-system-x86_64 -cdrom myos.iso` shows your output.

**Watch for:** **use the serial port for debugging output from day one.** `-serial stdio` puts your kernel's output in your terminal, where you can pipe it, grep it, and scroll back. Screen output is for demos; serial is for working.

The `hlt` loop at the end matters — without it you fall off the end of `kmain` into garbage.

### 2. The GDT and IDT

Two descriptor tables the CPU requires.

**GDT** (Global Descriptor Table) — memory segments. In 64-bit mode segmentation is mostly vestigial, so you need a minimal flat GDT plus a **TSS** (Task State Segment) that holds the kernel stack pointer used when an interrupt arrives from user mode.

**IDT** (Interrupt Descriptor Table) — 256 entries mapping interrupt vectors to handler addresses. → [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls and Interrupts]]

**Test:** load both without the machine resetting. Then deliberately divide by zero and see your handler run.

**Watch for:** an interrupt handler must be declared with the right calling convention (`__attribute__((interrupt))` in GCC/Clang) or the stack frame is wrong and you triple-fault. **A triple fault is a silent instant reboot** — QEMU's `-d int -no-reboot` is how you see what actually happened.

### 3. Interrupts and a timer

Set up the PIC (or APIC), unmask the timer and keyboard, enable interrupts with `sti`.

**Test:** a timer tick incrementing a counter you print. Keyboard input echoing to the screen.

> **This is the milestone that makes it feel real.** Your code is now being *interrupted by hardware* and resuming correctly. If you stop anywhere, stop here — you'll have learned the boot path, the descriptor tables, and the interrupt mechanism, which is the majority of the conceptual value.

**Watch for:** you must send an **EOI** (end-of-interrupt) to the PIC or you never receive another interrupt of that type — the classic "my timer ticked exactly once" bug. Handlers must be short and must not assume any locks are available.

### 4. Physical memory management

The bootloader gives you a memory map. Track which physical page frames are free.

A **bitmap allocator** is the simplest: one bit per 4KB frame. A free-list of frames is also fine.

**Test:** allocate frames, free them, allocate again, assert you get valid distinct addresses.

**Watch for:** the memory map has holes — reserved regions, ACPI tables, MMIO. **Mark your own kernel's frames as used**, or you'll allocate over yourself, which produces spectacularly confusing corruption.

### 5. Virtual memory and paging

**The hardest milestone**, and the one that separates a toy from a kernel.

Build 4-level page tables, map physical frames to virtual addresses, handle page faults. → [[foundations/os/04-virtual-memory|Virtual Memory]]

**Test:** map a fresh frame to an arbitrary virtual address, write to it, read it back. Unmap it and confirm the access faults.

**Watch for:**

- **You must not unmap the code you're currently executing.** Higher-half mapping (kernel at `0xFFFF800000000000`+) exists so kernel and user mappings coexist
- **Flush the TLB** after changing a mapping (`invlpg`, or reload CR3). Stale translations produce bugs that look like memory corruption → [[foundations/os/04-virtual-memory|TLB]]
- **Every page-table level needs the present and writable bits set correctly.** A missing bit three levels up makes the mapping silently absent
- Identity-map what you need before switching, or the instruction after the switch faults

**A page-fault handler that prints CR2 (the faulting address), the error code, and RIP is the most valuable debugging tool you will build.**

### 6. A heap

`kmalloc`/`kfree` on top of the frame allocator. A bump allocator first, then a free-list or slab allocator. → [[foundations/os/05-memory-allocation|Memory Allocation]]

**Test:** allocate varied sizes, free in mixed order, allocate again. Assert no overlaps.

**Watch for:** you're writing the allocator you've used for free your whole career. Alignment matters, and there's no `valgrind` — a bug here corrupts everything downstream and looks like a bug in whatever ran next.

### 7. User mode

Ring 3, and the first real privilege boundary.

Set up a TSS, a user-mode GDT entry, map a user page, and `iretq` into it.

**Test:** a user program that loops. Then have it execute a privileged instruction and confirm your kernel catches the fault rather than dying.

**Watch for:** the transition requires exactly the right stack layout for `iretq`. Get one field wrong and you triple-fault with no message. **This is the most fiddly single step in the project** — go slowly and dump the stack.

### 8. Syscalls

The `syscall`/`sysret` instructions, configured via MSRs (`LSTAR`, `STAR`, `SFMASK`).

Implement `write`, `exit`, `read`.

**Test:** a user program calling your `write` to print, then `exit`.

**Watch for:** the kernel must **switch to a kernel stack** immediately (the user stack is untrusted), and **validate every pointer a user passes** — a user handing you a kernel address must not be dereferenced. That check is the entire security boundary of an OS, and forgetting it is how real kernel vulnerabilities happen.

### 9. Processes and scheduling

A process structure (page tables, registers, state, kernel stack), a context switch in assembly, and a round-robin scheduler driven by the timer. → [[foundations/os/03-scheduling|Scheduling]]

**Test:** two user processes printing alternately, preempted by the timer.

**Watch for:** the context switch saves and restores registers and swaps CR3. It's ~20 lines of assembly and every line matters. Preemption from an interrupt handler is harder than cooperative yielding — start with `yield()`, then add the timer.

### 10. A filesystem

Simplest useful path: an **initrd** — a tar archive loaded by the bootloader, read-only, parsed in memory. Enough to load user programs.

A real driver (FAT32 is the friendliest) plus a VFS layer is a whole project after that. → [[foundations/os/07-filesystems-and-storage|Filesystems]]

**Test:** load and execute a program from the initrd.

## Per-language toolkit

Fewer options here than anywhere else — you need no runtime, no GC, and direct hardware access.

| | Viability |
|---|---|
| **C** | **The default.** Every tutorial, every wiki page, every example. Needs a cross-compiler and inline assembly |
| **Rust** | **Excellent, and increasingly the recommended path.** `#![no_std]`, `#![no_main]`, and `x86_64`/`bootloader` crates that handle the tedious descriptor-table code. Ownership genuinely helps with page-table safety. [Writing an OS in Rust](https://os.phil-opp.com) is the best tutorial available |
| **Zig** | Very good — cross-compilation and freestanding targets are first-class, and the build system is simpler than any C setup |
| **C++** | Works with `-fno-exceptions -fno-rtti -nostdlib`. You lose most of the standard library; RAII still helps |
| **Assembly** | Required in small doses: the entry stub, context switch, `iretq` sequence |
| **Go / Python / JS** | **No.** They need a runtime that needs an OS |

**Recommendation: Rust if you want to finish, C if you want the traditional experience.** The Rust crates eliminate a lot of error-prone boilerplate, and the type system catches page-table mistakes that would otherwise be silent triple faults.

Supporting tools regardless of language:

```bash
qemu-system-x86_64      # your entire development environment
gdb                     # QEMU's -s -S flags let you attach and single-step your kernel
objdump / readelf       # inspect your kernel binary
xorriso / limine        # build a bootable ISO
```

**QEMU + GDB is the single most valuable setup here:**

```bash
qemu-system-x86_64 -cdrom myos.iso -s -S       # wait for a debugger on :1234
gdb kernel.elf -ex 'target remote :1234'
```

You can breakpoint, single-step, and inspect registers in your own kernel. Without it you're debugging by printing.

## The parts that will bite you

**The triple fault.** A fault while handling a fault while handling a fault → instant reboot, no message. `-d int -no-reboot` in QEMU is the only way to see the cause.

**The red zone.** `-mno-red-zone` in every kernel compilation unit, or interrupts silently corrupt local variables.

**Forgetting the EOI.** Your timer ticks once and stops.

**Stale TLB entries.** Change a mapping without flushing, and you read the old page.

**Alignment.** Page tables must be 4KB-aligned. The stack must be 16-byte aligned at a call. Misalignment produces faults far from the cause.

**Wrong interrupt calling convention.** The handler returns with the wrong stack and everything explodes.

**Unvalidated user pointers.** The single most important security discipline in a kernel.

**Assuming the standard library exists.** No `printf`, no `malloc`, no `memcpy` — you write all of them. Even `memcpy` is needed because the compiler emits calls to it for struct assignment.

**Debugging without tools.** There is no `printf` until you write one, no debugger until you set up GDB, no sanitizers at all. Set up serial output and QEMU+GDB before milestone 2, not after you're stuck.

## How to know it works

```bash
qemu-system-x86_64 -cdrom myos.iso -serial stdio -d int,cpu_reset -no-reboot -m 512M
```

**Then real hardware:**

```bash
sudo dd if=myos.iso of=/dev/sdX bs=4M status=progress && sync
```

Boot an old laptop from it. **QEMU is forgiving in ways real hardware isn't** — real machines have different memory maps, different firmware quirks, and no patience. A kernel that works in QEMU and not on metal usually has a hard-coded assumption about the memory map or the framebuffer.

**Test each milestone destructively:** divide by zero and confirm your handler runs; dereference an unmapped address and confirm the page-fault handler prints something useful; have a user process execute `cli` and confirm it faults instead of succeeding.

**A boot-and-check script** that runs QEMU with a timeout, captures serial output, and greps for expected strings gives you regression testing — genuinely worth building once you're past milestone 3.

## Where to stop

**Stop at milestone 3 (interrupts) for the concepts. Stop at milestone 5 (paging) for real depth. Stop at 9 (processes) and you've built an operating system.**

What each level teaches you:

- **1–3:** how a machine actually boots, what the CPU requires before it will run your code, and how hardware interrupts work
- **4–6:** where memory comes from, what a page table *is*, and why an OS can lie to every process about the address space
- **7–9:** what the privilege boundary costs, what a context switch really does, and why a syscall is expensive

**Real kernels additionally have:** SMP and per-CPU state, dozens of device drivers, a network stack, real filesystems with journaling, a scheduler that's been tuned for two decades, security frameworks, power management, and support for hardware that lies about its own capabilities.

**If you continue:** the most rewarding next steps are a **keyboard-driven shell** running as a user process (it makes the whole thing feel like a computer), then **SMP** (bringing up the other cores is a satisfying, well-defined problem).

This is the natural endpoint of [[build-your-own-x/07-your-own-shell|the shell guide]] — there you called `fork` and `exec`; here you implement them.

---

## Related
- [[foundations/os/README|Operating Systems]] — the whole domain, written to unblock this
- [[foundations/os/04-virtual-memory|Virtual Memory]] — the hardest milestone
- [[foundations/os/09-syscalls-interrupts-and-the-abi|Syscalls, Interrupts and the ABI]] — milestones 2, 3 and 8
- [[languages/04-c/README|C]] — the language most of this is written in
- [[build-your-own-x/README|build-your-own-x]]
