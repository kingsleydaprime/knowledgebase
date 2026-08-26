# Build Your Own Memory Allocator

> **[Intermediate]** · Implement `malloc` and `free`. **A weekend, ~300 lines, and one of the best effort-to-insight ratios here.**

## What you're building

**A drop-in replacement for `malloc`, `free`, `calloc` and `realloc`** that real programs link against and run on.

**And what you're deliberately not:** competing with glibc, being thread-safe from day one, or being fast. **The goal is that "the heap" stops being a word and becomes a data structure you've walked.**

## What you need first

- **C, and pointers you're comfortable with** → [[languages/04-c/README|C]]
- **What the stack and heap actually are** → [[foundations/os/05-memory-allocation|memory allocation]]
- **`sbrk` or `mmap`** — how a process asks the kernel for memory → [[foundations/os/09-syscalls-interrupts-and-the-abi|syscalls]]
- Helpful: [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]]

**C is the natural language** — you need raw pointers and pointer arithmetic. Rust with `unsafe` works and fights you productively.

## The build order

**1. Get memory from the kernel.**
`sbrk(n)` moves the program break and returns the old value; `mmap` is the modern way. Just take a big chunk and hand out pieces.
*Works when:* `my_malloc(100)` returns a pointer you can write 100 bytes to without crashing.

**2. A bump allocator.**
Keep a pointer; move it forward on each allocation. **`free` does nothing.**
*Works when:* a program doing thousands of small allocations runs correctly. **This is a real allocator** — arena allocators in games and compilers are exactly this, and their speed is the point.

**3. Block headers.**
`free(ptr)` receives only a pointer, so the size must be recoverable. Store a header *immediately before* the returned pointer:

```c
struct block {
    size_t size;
    int    free;
    struct block *next;
};
```
Return `(void*)(header + 1)`; on free, step back to find the header.
*Works when:* you can free a block and read its size back correctly.

**4. A free list, and reuse.**
Thread free blocks into a list. On allocation, walk it looking for one big enough — **first-fit** is the simplest.
*Works when:* alloc/free/alloc of the same size **reuses the same address**. That's the moment the allocator becomes real.

**5. Splitting.**
A 1000-byte block satisfying a 16-byte request wastes 984 bytes. Split it and return the remainder to the free list.
*Works when:* memory usage stops growing under a mixed alloc/free workload.

**6. Coalescing.**
Two adjacent free blocks should merge, or you fragment into uselessness. Merge with the next block; merging with the *previous* one needs a **boundary tag** — a footer duplicating the size — so you can find it.
*Works when:* alloc 3 blocks, free all 3, and you can then allocate one block the size of all three combined. **This is the test that matters most.**

**7. Alignment.**
Return pointers aligned to `max_align_t` (16 bytes on x86-64). **Misaligned SIMD access crashes on some platforms and is silently slow on others.**
*Works when:* `(uintptr_t)ptr % 16 == 0` for every allocation.

**8. `calloc` and `realloc`.**
`calloc` must zero — and must **check for overflow** in `n * size`, which is a real CVE class. `realloc` grows in place if the next block is free, otherwise allocates and copies.
*Works when:* `realloc` preserves contents and handles `NULL` and size-0 per the standard.

**9. Run a real program against it.**
```bash
gcc -shared -fPIC -o myalloc.so myalloc.c
LD_PRELOAD=./myalloc.so ls
```
*Works when:* **`ls` runs correctly using your allocator.** Genuinely satisfying, and an unforgiving test.

**10. Optional: size classes and bins.**
Segregate free lists by size to avoid walking a long list for a small request. That's the step toward how real allocators work.

## The parts that will bite you

**Off-by-one on header size.** Every allocation must reserve `sizeof(header)` extra. Get it wrong and you overwrite metadata — producing corruption that surfaces *much* later, somewhere unrelated.

**Alignment.** If your header is 24 bytes, payloads land at 24-byte offsets — misaligned. Round the header up.

**`LD_PRELOAD` bootstrapping.** The dynamic linker may call `malloc` before your allocator initialises. A small static buffer for early allocations is the usual fix, and hitting this is instructive about how processes start → [[foundations/os/12-boot-and-init|boot and init]].

**Freeing a pointer you didn't allocate**, or twice. Real allocators detect some of this; yours will corrupt silently. **A magic number in the header catches it cheaply.**

**Fragmentation is the whole problem.** Without coalescing you'll have plenty of free memory and no block large enough — and watching that happen is the lesson.

## How to know it works

1. **Alloc/free/alloc reuses the address**
2. **Coalescing test:** three adjacent frees allow one large allocation
3. **Alignment holds** for every pointer
4. **A stress test** — thousands of random alloc/free of random sizes, writing a pattern and verifying it later. **This catches overlapping allocations, which is the bug that matters**
5. **`LD_PRELOAD` against real programs** — `ls`, `cat`, then something bigger
6. **Measure fragmentation** — total requested vs total taken from the kernel

## Where to stop

**Stop after `LD_PRELOAD` works and you've measured fragmentation.** Thread safety, per-thread arenas, and the security hardening real allocators do are each large projects that teach much less per hour.

**You will have learned:** what a pointer returned by `malloc` actually points into, why `free` needs no size, why fragmentation is the hard problem, why alignment exists, and why heap corruption surfaces far from its cause — which makes [[foundations/programming-fundamentals/10-errors-and-debugging|debugging]] C a different activity afterwards.

**And it makes [[languages/03-rust/README|Rust's]] ownership model land differently**: you'll have written the bugs it exists to prevent.

## Related
- [[foundations/os/05-memory-allocation|memory allocation]] — the theory
- [[languages/04-c/README|C]] — the language, and undefined behaviour
- [[build-your-own-shit/05-your-own-os|your own OS]] — where you'd write the layer below this
- [[languages/07-csharp/08-memory-gc-and-spans|garbage collection]] — the other approach

*Source: [reference] — build guide, Aug 2026.*
