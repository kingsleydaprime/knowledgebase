# Operating Systems

## What an operating system is

**An operating system is the main program that runs a computer and shares it out between all the other programs.**

Windows, macOS, Linux, Android and iOS are operating systems. When you open several apps at once, something has to decide which one gets the processor right now, give each one its own memory so they can't read or wreck each other's, and let them all use the same disk, screen and network without clashing. That's the operating system's job. Apps never touch the hardware directly: they ask the operating system, and it does the work for them.

The core part of the operating system, the part in charge of all this, is called the **kernel**.

## What you'll be able to do

By the end you will be able to:
- explain what happens when you start a program, and the difference between a process and a thread;
- explain how the computer runs many programs "at once" on a few processor cores;
- explain how each program gets its own private memory, and what happens when memory runs out;
- understand why saved data isn't truly safe until the operating system says so;
- explain how a program waits for many network connections at the same time;
- explain what a container (like Docker) really is underneath.

## Where to start

**New to this?** Start with [[os/fundamentals|OS Fundamentals]], a shorter overview that covers the whole subject gently. Then read the numbered notes in order.

### How the operating system is organised

1. [[os/01-what-an-os-is|What an OS Is]]: the kernel, why apps aren't allowed to touch the hardware directly, and how the hardware enforces that.
2. [[os/02-processes-and-threads|Processes and Threads]]: what a running program is made of, how a new one is started, and how threads let one program do several things at once.
3. [[os/03-scheduling|Scheduling]]: how the operating system decides which program runs next, and why apps can run mysteriously slowly in cloud setups that limit CPU time.

### Memory

4. [[os/04-virtual-memory|Virtual Memory]]: how every program gets its own private memory, what happens when memory runs out, and why "no free memory" is usually fine.
5. [[os/05-memory-allocation|Memory Allocation]]: how a program asks for memory and gives it back, and why memory use can keep growing even without a bug.

### Doing several things at once

6. [[os/06-concurrency-primitives|Concurrency Primitives]]: locks and the other tools that stop threads from corrupting shared data, and what they cost.

### Files and input/output

7. [[os/07-filesystems-and-storage|Filesystems and Storage]]: how files are stored, and the exact moment saved data is truly safe on disk.
8. [[os/08-io-models|I/O Models]]: the different ways a program waits for data from disks and networks, and how servers handle thousands of connections.

### Where programs meet the operating system

9. [[os/09-syscalls-interrupts-and-the-abi|Syscalls, Interrupts and the ABI]]: how a program asks the kernel to do something, and how hardware gets the kernel's attention.
10. [[os/10-signals-and-ipc|Signals and IPC]]: how the operating system interrupts a program (for example on Ctrl+C), and how programs send data to each other.

### Putting it together

11. [[os/11-isolation-and-containers|Isolation and Containers]]: what a container really is. There's no single "container" thing in the kernel, just several features combined.
12. [[os/12-boot-and-init|Boot and Init]]: everything that happens from pressing the power button to the login screen.

## Practice

Notes alone won't make this stick. The best way to learn operating systems is to build small versions of their parts:
- **Read** [*Operating Systems: Three Easy Pieces*](https://pages.cs.wisc.edu/~remzi/OSTEP/), free online and very readable.
- **Build** a tiny shell (the program that runs your terminal commands), a tiny memory allocator and a tiny scheduler. See [[build-your-own-shit/index|Build Your Own]].
- **Prepare for interviews** with [[os/interview/index|OS interview prep]]: processes versus threads, memory, scheduling, files and more.

## Key ideas to remember

1. **Saving a file doesn't make it safe straight away.** The data sits in memory until the operating system writes it to disk. Programs that must not lose data ask for that explicitly (`fsync`). → [[os/07-filesystems-and-storage|07]]
2. **"No free memory" on Linux is usually healthy.** Spare memory is used to speed up the disk, and it's handed back the moment a program needs it. Look at "available", not "free". → [[os/04-virtual-memory|04]]
3. **A lock costs almost nothing when nobody else wants it,** and a lot when threads fight over it. Hold locks briefly rather than avoiding them. → [[os/06-concurrency-primitives|06]]
4. **A cloud CPU limit is a hard stop, not a slowdown.** Use up your share early and every thread freezes until the next time slot. → [[os/03-scheduling|03]]
5. **A container is just a normal program with limits around what it can see and use.** → [[os/11-isolation-and-containers|11]]

## Related

- [[devops/01-linux/index|Linux]]: the same machine, from the command line.
- [[networking/index|Networking]]: built on top of the operating system's connections.
- [[computer-architecture/index|Computer Architecture]]: the hardware underneath.
- [[languages/04-c/index|C]]: the language operating systems are written in.
- [[devops/02-docker/index|Docker]]: containers from the user's side.

---

## About this course

- **Size:** 12 notes, about 17,000 words, plus an overview note and interview prep. Written in August 2026.
- **Linux throughout:** the details are Linux's. Windows and macOS work on the same ideas but differ in detail.
- **Not covered yet:** device drivers, kernel modules, real-time Linux, and how network data travels from the network card to a program inside the kernel.
