# Memory Allocation

**[Intermediate → Advanced]** — What `malloc` actually does, why freed memory doesn't return to the OS, and how fragmentation looks like a leak.

## Two layers

```
your code:   malloc(64)
                 │
      ┌──────────▼──────────┐
      │  ALLOCATOR (libc)   │   user space — manages a pool, splits and merges blocks
      │  glibc / jemalloc   │   fast path: no syscall at all
      └──────────┬──────────┘
                 │  occasionally, in large chunks
      ┌──────────▼──────────┐
      │  KERNEL             │   brk / mmap — hands over whole pages
      └─────────────────────┘
```

**`malloc` is not a syscall.** It's user-space code managing a pool it obtained from the kernel earlier. A typical `malloc` involves no kernel interaction at all — that's why it costs tens of nanoseconds rather than a microsecond.

The kernel deals only in **pages** (4KB). The allocator's job is turning that into arbitrary-sized blocks with acceptable speed and waste.

## Getting memory from the kernel

```c
void *brk(void *addr);          // move the heap boundary — the old way
void *sbrk(intptr_t incr);
void *mmap(...MAP_ANONYMOUS...); // map fresh pages anywhere — the modern way
```

glibc uses both: `brk` to grow the main heap for small allocations, and `mmap` directly for large ones (over `M_MMAP_THRESHOLD`, 128KB by default).

That threshold has a visible consequence:

```c
void *p = malloc(200 * 1024);   // > threshold → its own mmap
free(p);                         // munmap'd — returned to the OS IMMEDIATELY

void *q = malloc(100);           // from the heap
free(q);                         // stays in the allocator's free list — NOT returned
```

**Small frees don't return memory to the OS.** They return it to the allocator, which keeps it for the next `malloc`. RSS doesn't drop.

This is correct behaviour — asking the kernel for memory is expensive, so keeping a pool is the point — and it's the source of endless "my program has a leak" confusion. `malloc_trim(0)` forces a return where the layout permits it.

## How an allocator works

The core problem: satisfy variable-sized requests from a pool, quickly, without wasting too much.

**Free lists.** Each free block carries a header (size, flags) and is linked into a list. `malloc` searches for a suitable block; `free` puts it back and **coalesces** with adjacent free blocks to fight fragmentation.

**Size classes / bins.** Searching one list is O(n), so allocators bin blocks by size — glibc has fastbins, tcache, smallbins, largebins, and unsorted. A request goes to the right bin and takes the first entry, which is O(1).

**Thread caches.** A global lock on every `malloc` destroys multithreaded performance. Modern allocators give each thread a private cache:

- **glibc**: `tcache` (per-thread, small sizes) plus multiple **arenas** — separate heaps that threads are assigned to
- **jemalloc / tcmalloc**: per-thread caches over per-CPU or per-arena structures

The trade is memory for speed. Per-thread caches mean the same total allocation is spread across more pools, so RSS is higher.

**A glibc detail worth knowing:** the number of arenas defaults to 8× the core count. On a 64-core machine that's 512 arenas, each potentially holding a 64MB heap — which is why a threaded C program can show surprising RSS. `MALLOC_ARENA_MAX=2` caps it, and is a standard container tuning.

## Fragmentation

**External** — enough total free memory, no single block big enough:

```
[used 1KB][free 2KB][used 1KB][free 2KB][used 1KB]
5KB free, but a 3KB request fails
```

**Internal** — the allocator rounds up. Request 100 bytes, get a 112-byte block plus a 16-byte header. Waste inside the allocation.

Fragmentation is **why RSS climbs in a long-running process that has no leak.** Every allocation is freed correctly, and the heap can't be shrunk because a live object sits near the top. It's the classic "we restart the service nightly" cause, and it's genuinely hard to fix in-place.

Mitigations: allocators with better placement (jemalloc is meaningfully better here), size-segregated pools, or arenas that free everything at once.

```bash
MALLOC_ARENA_MAX=2 ./prog          # fewer glibc arenas
LD_PRELOAD=/usr/lib/libjemalloc.so ./prog     # swap allocator without recompiling
```

That `LD_PRELOAD` swap is worth knowing — it's a one-line experiment that sometimes cuts RSS substantially, and it works because `malloc` is a dynamically-linked symbol. → [[foundations/os/12-boot-and-init|dynamic linking]]

## Which allocator

| | Character |
|---|---|
| **glibc malloc** (ptmalloc2) | the default. Fine; fragments more; many arenas |
| **jemalloc** | lower fragmentation, excellent multithreaded, great introspection. FreeBSD's default, Rust's old default |
| **tcmalloc** | Google's; very fast small allocations, good profiling |
| **mimalloc** | Microsoft's; small, fast, often the best on benchmarks now |
| **musl malloc** | tiny, simple, **noticeably slower under thread contention** |

That last one matters in practice: **Alpine-based containers use musl**, and a threaded, allocation-heavy service can be measurably slower there than on glibc. It's a real and frequently-missed cause of "the same binary is slower in this image".

## Allocation strategies that avoid the problem

The fastest allocation is the one you don't make.

**Arena / bump allocator** — allocate by advancing a pointer; free everything at once:

```c
void *arena_alloc(Arena *a, size_t n) {
    n = (n + 15) & ~(size_t)15;                  // align
    if (a->used + n > a->cap) return NULL;
    void *p = a->base + a->used;
    a->used += n;
    return p;
}
```

Allocation is a pointer bump. There's no individual `free`, so **no fragmentation, no use-after-free, no double-free, no leaks** — you reset the arena. Ideal where lifetimes are naturally grouped: per request, per frame, per compilation unit. Compilers, game engines and web servers all use them.

**Pool allocator** — fixed-size blocks on a free list. O(1), zero fragmentation for that size class.

**Slab allocator** — the kernel's own approach: caches of pre-initialised objects of one type. `cat /proc/slabinfo`.

**Object pooling** — reuse instead of reallocating. `sync.Pool` in Go, `ObjectPool` in Java.

**Stack allocation** — free, automatic, and bounded. Prefer it when the size is known and modest. → [[languages/04-c/07-memory-management|C: Memory Management]]

## Managed runtimes

A garbage collector changes the allocation profile entirely:

**Bump allocation in a nursery.** Allocating in a generational GC is a pointer increment — *faster* than `malloc`. The cost moves to collection.

**Compaction.** A moving collector relocates live objects to eliminate fragmentation. That's something `malloc` fundamentally cannot do, because C pointers are raw addresses that would become invalid.

So the trade isn't "GC is slower" — it's:

| | Manual | GC |
|---|---|---|
| Allocation | ~20–50ns | ~1–5ns (bump) |
| Deallocation | explicit, immediate | deferred, batched |
| Fragmentation | permanent | fixed by compaction |
| Pauses | none | some (sub-ms in Go/ZGC) |
| Memory overhead | low | 2–5× headroom typical |

→ [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]] · [[languages/02-go/13-performance-and-runtime|Go's GC]]

## Huge pages for allocation

```c
madvise(addr, len, MADV_HUGEPAGE);
mmap(..., MAP_HUGETLB, ...);          // explicit, from a preallocated pool
```

2MB pages reduce TLB pressure for large working sets — worth real percentages for databases and JVMs with big heaps. Explicit hugepages (`vm.nr_hugepages`) are predictable; transparent hugepages can stall you at allocation time while `khugepaged` compacts. → [[foundations/os/04-virtual-memory|Virtual Memory]]

## Debugging

```bash
valgrind --leak-check=full --show-leak-kinds=all ./prog
gcc -fsanitize=address ./prog                    # faster; also catches overflow, UAF
heaptrack ./prog && heaptrack_gui heaptrack.*    # allocation profiler — where and how much
MALLOC_CHECK_=3 ./prog                            # glibc's own consistency checks
jemalloc: MALLOC_CONF=prof:true,prof_prefix:jeprof ./prog
```

**`heaptrack` is the underused one.** Valgrind and ASan tell you about *bugs*; heaptrack tells you where your memory is *going*, which is the question when RSS is high and nothing is leaking.

For "is this a leak or fragmentation?": a leak grows without bound and the allocations are live; fragmentation plateaus at a higher-than-expected level with everything correctly freed. `malloc_stats()` or jemalloc's `stats.allocated` vs `stats.mapped` distinguishes them — a large gap between allocated and mapped is fragmentation.

---

## Related
- [[foundations/os/04-virtual-memory|Virtual Memory]] — where the pages come from
- [[languages/04-c/07-memory-management|C: Memory Management]] — the user-space view, and arenas
- [[languages/02-go/13-performance-and-runtime|Go: Performance]] — escape analysis and the GC
- [[foundations/os/README|OS course map]]
