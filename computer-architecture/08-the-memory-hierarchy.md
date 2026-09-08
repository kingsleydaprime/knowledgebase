# The Memory Hierarchy

**[Intermediate]** — Why memory is the bottleneck, and the single most important thing to understand about performance.

## The wall

**CPUs got much faster than memory, for decades.**

```
 relative
 speed
    │      CPU  ╱‾‾‾‾‾‾‾‾
    │         ╱
    │       ╱      ← the gap
    │     ╱
    │   ╱  ______________
    │  ╱‾‾   DRAM
    └────────────────────→ time
```

**The result is a ratio worth internalising:**

| Level | Latency | Size | Scaled to 1 cycle = 1 second |
|---|---|---|---|
| **Register** | 0 cycles | ~1 KB | instant |
| **L1** | ~4 cycles | 32–64 KB | **4 seconds** |
| **L2** | ~12 cycles | 256 KB–2 MB | 12 seconds |
| **L3** | ~40 cycles | 8–64 MB (shared) | 40 seconds |
| **DRAM** | **~200–300 cycles** | GB | **~4 minutes** |
| **NVMe SSD** | ~150,000 cycles | TB | **~2 days** |
| **Network (same DC)** | ~1.5M cycles | — | **~3 weeks** |

> **DRAM is ~50–75× slower than L1.** That single ratio explains more real-world performance behaviour than any other number in computing.
>
> **Most programs are memory-bound, not compute-bound.** The CPU is waiting, not calculating — which is why "reduce instruction count" is usually the wrong optimisation and "improve locality" is usually the right one.

## Why a hierarchy works

**Locality**, and it's an empirical property of real programs rather than a law:

**Temporal locality** — data used now is likely to be used again soon. *Loop counters, hot variables, a frequently-called function.*

**Spatial locality** — data near what you just used is likely to be used soon. *Sequential array traversal, struct fields, instructions.*

**Caches exploit both.** Temporal via retention, spatial via **fetching a whole line**.

## Cache lines

> **Memory moves in fixed-size blocks — 64 bytes on essentially every modern CPU. This is the fundamental unit, and almost everything practical follows from it.**

**Reading one byte fetches 64.** So:

**Sequential access is nearly free after the first byte.** Reading 64 sequential bytes costs one miss, not 64.

**Random access pays full price every time.** Every access is a new line.

**Small data structures fit in one line.** A 64-byte struct is one fetch; a 72-byte struct is two.

**Alignment matters.** A struct straddling a line boundary costs two fetches. → [[foundations/computer-architecture/02-data-representation|Alignment]]

**The demonstration everyone should run once:**

```c
// Fast — 8 misses per 64 elements (sequential)
for (i = 0; i < N; i++) sum += a[i];

// Slow — potentially 1 miss per access
for (i = 0; i < N; i += 16) sum += a[i];
```

**The second does 1/16th the work and can be no faster**, because both touch the same number of cache lines.

## Data structure consequences

**This is where the note pays for itself.**

**Array of Structs vs Struct of Arrays:**

```c
struct Particle { float x, y, z, vx, vy, vz; };   // 24 bytes
Particle particles[N];                             // AoS

struct Particles { float x[N], y[N], z[N], vx[N], vy[N], vz[N]; };  // SoA
```

**If you only need `x`:** AoS fetches 24 bytes per particle to use 4 — **83% of the bandwidth wasted.** SoA fetches only `x`, and vectorises cleanly.

**If you need all fields together:** AoS wins, because one line has everything.

**Choose based on your access pattern**, and this is why data-oriented design exists in game engines and HPC.

**Linked lists vs arrays:**

| | Traversal |
|---|---|
| **Array** | sequential, prefetcher-friendly, ~1 miss per 16 ints |
| **Linked list** | **pointer chase** — each node is a potential miss, and each load depends on the previous |

> **A linked list has the same $O(n)$ traversal as an array and can be 10× slower.** The loads are *serially dependent* — you can't fetch node $n+1$ until node $n$ arrives — so there's no memory-level parallelism and the prefetcher can't help.
>
> **This is the clearest case where Big-O misleads.** `std::vector` beats `std::list` for almost everything, including insertion in the middle at moderate sizes, because memmove is sequential and pointer chasing isn't. → [[foundations/dsa/04-data-structures/04-linked-lists|Linked Lists]]

**Hash maps** — open addressing (linear probing) is usually faster than chaining, because probes stay in the same cache line. **The pointer chasing in chained buckets is the cost.** → [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]]

**Trees** — B-trees beat binary trees on real hardware even in memory, because a node sized to a cache line does many comparisons per fetch. **A binary tree does one comparison per cache miss**; a B-tree with 16-way fanout does four levels' worth. This is why database indexes are B-trees and why `absl::btree_map` exists.

## Matrix multiply, the canonical example

```c
// Naive — B is accessed by column, striding through memory
for (i) for (j) for (k) C[i][j] += A[i][k] * B[k][j];

// Loop interchange — all three access sequentially
for (i) for (k) for (j) C[i][j] += A[i][k] * B[k][j];
```

**Identical arithmetic. The second can be several times faster**, purely from access pattern.

**Blocking (tiling)** goes further — process sub-blocks that fit in cache, so each block is loaded once and reused $B$ times:

```c
for (ii = 0; ii < N; ii += B)
  for (jj = 0; jj < N; jj += B)
    for (kk = 0; kk < N; kk += B)
      /* multiply the B×B block */
```

**This is why tuned BLAS beats naive code by 10–50×** — not better asymptotics, just cache-aware ordering. → [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/04-matrix-multiplication|Matrix Multiplication]]

## Prefetching

**Hardware prefetchers detect access patterns and fetch ahead.**

**They handle well:** sequential forward, sequential backward, and constant strides.

**They cannot handle:** pointer chasing, random access, indirect indexing (`a[b[i]]`), and irregular patterns.

**Software prefetch** — `__builtin_prefetch(ptr)` — issues a hint. **Rarely helps** and often hurts: get the distance wrong and you evict useful data or arrive too late. **Measure before and after**, and be sceptical.

> **The reliable way to benefit from prefetching is to make your access pattern predictable**, not to insert hints. Sort your indices, flatten your structures, traverse in memory order.

## Virtual memory and the TLB

**Every memory access requires translating a virtual address to a physical one**, via page tables. **A page walk is several memory accesses**, so it's cached in the **TLB**.

**A TLB miss costs 10–100+ cycles**, and it's a separate cost from a cache miss.

**TLB reach** — entries × page size — is often only a few MB with 4 KB pages. **Working sets larger than that thrash the TLB even if the data is in L3.**

**Huge pages (2 MB / 1 GB)** multiply the reach by 512×. **Significant for databases, JVM heaps, and large in-memory workloads**, and often worth enabling explicitly. → [[foundations/os/04-virtual-memory|Virtual Memory]]

## Measuring

**Don't guess. `perf` tells you directly:**

```
perf stat -e cache-references,cache-misses,\
             L1-dcache-load-misses,LLC-load-misses,\
             dTLB-load-misses,cycles,instructions ./program
```

**What the numbers mean:**

- **IPC below ~1.0** — you're stalling. Above 2 is healthy
- **High LLC misses** — going to DRAM. **The expensive one**
- **High dTLB misses** — consider huge pages
- **`perf c2c`** — finds false sharing specifically

**`perf record` + `perf annotate`** shows which instruction is stalling, and it's frequently a load you didn't think about.

**`valgrind --tool=cachegrind`** simulates the hierarchy — slow, deterministic, and good for comparing two implementations without measurement noise.

## The rules

**In rough order of impact:**

**1. Sequential beats random.** Almost always, by a lot.

**2. Compact beats sparse.** Smaller data means more fits in cache. `uint16_t` instead of `int` can double your effective cache.

**3. Contiguous beats pointer-linked.** Arrays over lists, indices over pointers, arenas over scattered allocation. → [[foundations/os/05-memory-allocation|Memory Allocation]]

**4. Split hot from cold.** Keep frequently-accessed fields together; move rarely-used ones out. **A hot 16-byte struct beats a hot-and-cold 200-byte one.**

**5. Block your loops** for anything reusing data.

**6. Reorder struct fields** largest-first to eliminate padding.

**7. Align to cache lines** for anything written by multiple threads. → [[foundations/computer-architecture/11-multicore-and-memory-models|False Sharing]]

**8. Reduce indirection.** Each pointer hop is a potential miss.

> **The mental shift:** stop counting operations and start counting **cache lines touched**. That's the number that predicts runtime for most real code, and it's a completely different optimisation target from instruction count.

---

## Related
- [[foundations/computer-architecture/09-caches-in-depth|Caches in Depth]] — how they actually work
- [[foundations/os/04-virtual-memory|Virtual Memory]] — the TLB and page tables
- [[foundations/computer-architecture/12-performance|Performance]] — the full methodology
- [[foundations/computer-architecture/README|Architecture map]]
