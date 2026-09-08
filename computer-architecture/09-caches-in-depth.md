# Caches in Depth

**[Advanced]** — Associativity, replacement, write policies, and the pathological cases that make a working program mysteriously slow.

## Anatomy

**A cache splits every address into three fields:**

```
 ┌──────────┬────────┬────────┐
 │   TAG    │  INDEX │ OFFSET │
 └──────────┴────────┴────────┘
```

- **Offset** — which byte within the 64-byte line (6 bits)
- **Index** — which set to look in
- **Tag** — stored with the line, compared to confirm a hit

**Lookup:** use the index to select a set, compare the tag against every line in that set, and on a match return the byte at the offset.

## Associativity

**How many places a given address may live.**

**Direct-mapped (1-way)** — exactly one possible location.

*Fast, simple, no selection logic.* **Two hot addresses mapping to the same index evict each other endlessly** — conflict thrashing, even in a mostly-empty cache.

**Fully associative** — any line anywhere.

*No conflict misses.* **Requires comparing every tag in parallel** — expensive in power and area, so it's only used for tiny structures like TLBs.

**$N$-way set associative** — the compromise, and what everything uses.

```
 8-way set associative:
   set 0: [way0][way1][way2][way3][way4][way5][way6][way7]
   set 1: [    ][    ][    ][    ][    ][    ][    ][    ]
   ...
```

**Typical modern values:** L1 8-way, L2 8–16-way, L3 12–20-way.

> **Diminishing returns are steep.** Going 1-way → 2-way removes most conflict misses; 8-way → 16-way barely helps. **8-way is where the curve flattens**, which is why it's near-universal.

### Conflict misses

**The three kinds of miss (the "three Cs"):**

| Type | Cause | Fix |
|---|---|---|
| **Compulsory** | first ever access | prefetching |
| **Capacity** | working set exceeds cache | smaller working set, blocking |
| **Conflict** | too many lines map to one set | **change the layout** |

**Conflict misses are the surprising ones**, and they produce genuinely baffling behaviour:

```c
#define N 1024                    // power of two — dangerous
double A[N][N];
for (i = 0; i < N; i++)
    sum += A[i][0];               // stride = 8192 bytes
```

**Every access maps to the same set.** With 8-way associativity you hold 8 lines and thrash forever, **while using a tiny fraction of the cache.**

> **The fix is padding: make it `A[N][N+1]`.** The stride is no longer a power of two, accesses spread across sets, and **the program can get several times faster from one character.**
>
> **This is why power-of-two array dimensions are a known performance hazard** in numerical code, and why FFT and matrix libraries pad their strides deliberately. It's also a good demonstration that "the algorithm is the same" doesn't mean "the performance is the same".

## Replacement policies

**When a set is full, which line goes?**

**LRU** — least recently used. **Good, and expensive** to track exactly beyond 4-way (you need an ordering of all ways).

**Pseudo-LRU** — a tree of bits approximating LRU. **What's actually implemented.**

**Random** — surprisingly competitive, and immune to pathological patterns.

**RRIP / adaptive** — modern policies predicting re-reference intervals. **Better on streaming workloads**, where LRU is actively wrong.

> **LRU's known failure: a loop over data slightly larger than the cache.** By the time you return to the first element, it's been evicted — **so you miss on every access despite near-perfect locality.** LRU evicts exactly the line you're about to need.
>
> **Random replacement handles this better**, which is a nice counterexample to "smarter is better".

## Write policies

**Write-through** — write to cache and memory simultaneously. Simple, consistent, **high memory traffic.**

**Write-back** — write only to cache; mark the line **dirty**; write to memory on eviction. **Far less traffic**, and what everything uses. The complication is coherence.

**On a write miss:**

**Write-allocate** — fetch the line, then write. Standard, and it pairs with write-back.

**No-write-allocate** — write straight to memory. Better for streaming writes you'll never read.

**Non-temporal stores** (`_mm_stream_si128`, `movntdq`) bypass the cache entirely. **Use when writing a large buffer you won't read soon** — clearing memory, streaming output. **It avoids polluting the cache with data you don't need**, and avoids the read-for-ownership traffic.

**Write combining buffers** merge multiple small writes to the same line into one memory transaction — important for memory-mapped I/O and framebuffers.

## Cache coherence

**Multiple cores, each with private L1/L2, all caching the same memory.**

**MESI** — the protocol, and the four states:

| State | Meaning |
|---|---|
| **M**odified | I have it, it's dirty, **I'm the only one** |
| **E**xclusive | I have it, it's clean, I'm the only one |
| **S**hared | I have it, clean, **others may too** |
| **I**nvalid | I don't have it |

**MESIF** (Intel) and **MOESI** (AMD) add states to reduce memory traffic by allowing cache-to-cache transfer.

**The rule: a write requires exclusive ownership.** To write a line in state S, a core must **invalidate every other copy** first — a Request For Ownership, broadcast on the interconnect.

**The performance consequences:**

**Reads scale.** Many cores can hold a line in S simultaneously, no traffic.

**Writes to shared data do not scale.** Every write invalidates every other copy. **A counter incremented by all cores serialises on coherence traffic** regardless of how the increment is implemented.

**Cache-to-cache transfer is not free** — 50–200 cycles, sometimes worse than DRAM on multi-socket systems.

## False sharing

**The most common real coherence bug, and it's invisible in the source.**

```c
struct Counters {
    long a;    // thread 1 increments this
    long b;    // thread 2 increments this
};             // both in the SAME 64-byte cache line
```

**The variables are independent. The cache line is not.**

**Every write by thread 1 invalidates thread 2's copy and vice versa** — the line ping-pongs between cores at 50–200 cycles per transfer.

> **This can make a parallel program slower than the single-threaded version**, which is a genuinely confusing failure: the code is correct, the logic is independent, and adding threads makes it worse.

**The fix — pad to a cache line:**

```c
struct Counters {
    alignas(64) long a;
    alignas(64) long b;
};
```

Or in C++: `alignas(std::hardware_destructive_interference_size)`.

**Where it hides:**

- Adjacent elements of an array indexed by thread ID — **`results[thread_id]++` is the canonical case**
- Adjacent fields in a struct written by different threads
- A lock next to the data it protects (though this can also *help*, if the same core takes both)
- **Adjacent nodes in a lock-free queue**

**Find it with `perf c2c`**, which is built specifically to detect it and reports the exact line and offending offsets.

**The opposite — true sharing** — is genuinely shared data, and it can't be padded away. The fix is algorithmic: **per-thread accumulators combined at the end**, which is why sharded counters and thread-local aggregation exist. → [[foundations/os/06-concurrency-primitives|Concurrency Primitives]]

## Inclusive vs exclusive

**Inclusive** — L3 contains everything in L1 and L2. **Simplifies coherence** (snoop only L3 to know whether any core has a line), **wastes capacity** (data duplicated at every level). Intel's traditional design.

**Exclusive** — a line lives at exactly one level. **More effective total capacity**, more complex coherence. AMD's approach.

**Non-inclusive** — neither guaranteed. Most modern Intel designs.

**Why you'd care:** with an inclusive L3, **an L3 eviction forces eviction from every core's L1 and L2.** One core streaming through memory can evict another core's hot data — a real cross-tenant interference problem in cloud environments, and part of why noisy-neighbour effects exist.

## NUMA

**On multi-socket systems, memory is attached to specific sockets.**

```
 ┌─────────┐  interconnect  ┌─────────┐
 │ Socket0 │ ←───────────→  │ Socket1 │
 │  cores  │                │  cores  │
 └────┬────┘                └────┬────┘
      │ local ~80ns              │ local ~80ns
   ┌──▼───┐                   ┌──▼───┐
   │ DRAM │                   │ DRAM │
   └──────┘                   └──────┘
      remote access: ~140ns — nearly 2×
```

**Remote memory is 1.5–2× slower.**

**Practical handling:**

- **First-touch allocation** — Linux allocates a page on the node whose core first *touches* it, not the one that called `malloc`. **So initialise data on the thread that will use it**, which is a non-obvious and important detail for parallel initialisation loops
- **`numactl --cpunodebind=0 --membind=0`** to pin a process
- **`libnuma`** for explicit control
- **Check with `numastat`** — high `numa_miss` means remote traffic

**Modern chiplet designs (AMD's CCX/CCD, Intel's tiles) have NUMA-like effects within a single socket** — cross-chiplet latency exceeds intra-chiplet. **Worth knowing that "one socket" no longer means "uniform".**

## Practical notes

**Know your cache sizes:** `lscpu`, `getconf -a | grep CACHE`, or `/sys/devices/system/cpu/cpu0/cache/`.

**Size working sets to fit.** A block that fits in L2 dramatically outperforms one that doesn't, and the cliff is sharp.

**Avoid power-of-two strides**, or pad to break them.

**Pad shared-but-independent data to 64 bytes.**

**Initialise on the using thread**, on NUMA systems.

**Use non-temporal stores** for large write-only streams.

**Measure with `perf c2c` and `perf stat`** rather than reasoning about it — cache behaviour is genuinely hard to predict from source.

---

## Related
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — the practical rules
- [[foundations/computer-architecture/11-multicore-and-memory-models|Multicore and Memory Models]] — ordering on top of coherence
- [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — what runs on this
- [[foundations/computer-architecture/README|Architecture map]]
