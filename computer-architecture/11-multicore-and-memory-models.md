# Multicore and Memory Models

**[Advanced]** — What other cores actually see when you write to memory, and why your lock-free code works on x86 and breaks on ARM.

## The problem

**Coherence guarantees that all cores eventually agree on the value of each location.** It says nothing about **ordering between different locations.**

```c
// initially x = y = 0

// Thread 1        // Thread 2
x = 1;             y = 1;
r1 = y;            r2 = x;
```

**Can `r1 == 0 && r2 == 0`?**

**Sequential intuition says no** — one of the writes must come first. **On real hardware, yes**, and on x86 too.

**Why:** each core has a **store buffer**. A write goes into it and drains to cache later, while **loads may read past pending stores.** So both cores can read the other's old value.

> **This is not a bug.** Store buffers are essential — without them every write would stall on cache ownership. **The reordering is the price of performance**, and memory models are how it's specified.

## Memory models

**A memory model defines which reorderings are permitted** — the contract between hardware, compiler and programmer.

**Sequential consistency (SC)** — Lamport's definition: the result is as if all operations executed in some global order consistent with each thread's program order.

**Intuitive, and too slow to implement.** No real hardware provides it.

**The actual models:**

| Model | Reorders | Where |
|---|---|---|
| **TSO** (Total Store Order) | **only store→load** | **x86-64**, SPARC |
| **Weak / relaxed** | **almost anything** | **ARM, POWER, RISC-V** |

> **x86 is strongly ordered.** Only store→load reordering is allowed, which means **a lot of naive lock-free code accidentally works on x86.**
>
> **ARM and POWER are weakly ordered.** Loads and stores reorder freely unless barriers say otherwise.
>
> **This is why code that works fine on your x86 laptop breaks on an ARM server or an Apple Silicon Mac.** The bug was always there; x86 was hiding it. **It's one of the most common real portability failures in concurrent code**, and it became far more common once ARM servers and M-series Macs became mainstream.

## The compiler reorders too

**And this catches people who've thought about hardware but not about the compiler.**

```c
while (!flag) { }        // compiler may hoist the load out of the loop
do_work();               // → infinite loop, flag never re-read
```

**The compiler assumes single-threaded semantics** unless told otherwise. It caches values in registers, reorders independent operations, and eliminates "redundant" loads.

**`volatile` is not the fix.** It prevents the compiler caching the value but **provides no ordering guarantees against other memory operations and no atomicity.** In C and C++, `volatile` is for memory-mapped I/O and signal handlers, **not for threads.** (Java's `volatile` is different — it *does* provide ordering.)

**Use atomics.** They constrain the compiler and emit the right hardware barriers.

## Barriers and atomics

**C++11 / C11 / Rust memory orderings**, from weakest:

| Ordering | Guarantee |
|---|---|
| `relaxed` | atomicity only, **no ordering** |
| `consume` | (deprecated in practice, treated as acquire) |
| **`acquire`** | on a load — **nothing after moves before it** |
| **`release`** | on a store — **nothing before moves after it** |
| `acq_rel` | both, for read-modify-write |
| **`seq_cst`** | sequential consistency, **the default** |

**The acquire/release pair is the one to understand:**

```c
// Producer                    // Consumer
data = 42;                     if (flag.load(acquire)) {
flag.store(true, release);         use(data);   // guaranteed to see 42
                               }
```

> **Release says: everything I wrote before this is visible to anyone who acquires this.** It's a one-way barrier, and it's exactly the guarantee a mutex provides — **unlock is a release, lock is an acquire.** Every lock-free structure is built from this pattern.

**`seq_cst` is the default because it's the only model most people can reason about.** It costs a full barrier (`mfence` on x86, `dmb ish` on ARM). **Use it unless you have measured that you need less** — the performance difference is usually small, and the correctness difference is enormous.

**`relaxed` is genuinely useful for counters** where you only need atomicity, not ordering — statistics, reference counts being incremented (though *decrement*-to-zero needs acquire/release).

## Atomic operations

**Compare-and-swap** is the universal primitive:

```c
bool compare_exchange(atomic<T>& obj, T& expected, T desired);
// atomically: if (obj == expected) { obj = desired; return true; }
//             else { expected = obj; return false; }
```

**Every lock-free algorithm is built on CAS**, usually in a retry loop. **Its universality is a theorem** (Herlihy): CAS can implement any concurrent object for any number of threads, which load/store and even fetch-and-add cannot.

**LL/SC (load-linked / store-conditional)** is the ARM and RISC-V equivalent — load with a reservation, store only if untouched since. **Avoids the ABA problem** that CAS has, at the cost of spurious failures.

**Cost:** an uncontended atomic RMW is ~20 cycles; **contended, it's 100s** because of cache-line ping-ponging. → [[foundations/computer-architecture/09-caches-in-depth|Cache Coherence]]

**The ABA problem** — you read A, someone changes it to B and back to A, your CAS succeeds but the world changed underneath. **Real, and the reason lock-free stacks use tagged pointers or hazard pointers.**

## Why lock-free is hard

**The honest assessment**, because it's frequently attempted and rarely done correctly.

**Lock-free code must handle:**

- Memory ordering on every access, correctly, on every target architecture
- The ABA problem
- **Safe memory reclamation** — you can't free a node while another thread might be reading it. **This is the hardest part**, and it needs hazard pointers, epoch-based reclamation, or RCU
- Correctness arguments that are genuinely difficult and not testable by running it

**And the payoff is often negative.** A well-implemented mutex is fast when uncontended (a single atomic op), and modern futex-based locks avoid syscalls entirely in the fast path. **Lock-free helps under high contention or when you need progress guarantees** (real-time, signal handlers, interrupt context) — not as a general performance technique.

> **Use a library.** `folly`, `crossbeam`, `boost::lockfree`, or the concurrent collections in your standard library. **These are written by specialists and verified with model checkers.** Writing your own is a research project that looks like a coding task. → [[foundations/os/06-concurrency-primitives|Concurrency Primitives]]

## Testing concurrent code

**The specific difficulty: ordinary testing does not work.** A race may manifest once in $10^9$ runs, on one architecture, under one scheduler.

**What does work:**

**ThreadSanitizer** (`-fsanitize=thread`) — detects data races at runtime by tracking happens-before. **Slow (5–15×) and extremely effective.** Run your test suite under it.

**Model checkers** — CDSChecker, Loom (Rust), GenMC. **Exhaustively explore every legal interleaving and memory ordering** for a small test. This is how you actually verify a lock-free structure.

**Stress testing on weak hardware.** **Run on ARM.** x86's strong ordering hides bugs that ARM exposes immediately.

**`herd7` / `litmus`** — tools for reasoning about specific memory-model questions formally.

## Scaling

**What limits multicore speedup**, beyond correctness:

**Amdahl's law:**

$$S = \frac{1}{(1-p) + p/n}$$

**With 5% serial work, the maximum speedup is 20×** — no matter how many cores. **The serial fraction dominates**, and finding it matters more than adding threads. → [[foundations/computer-architecture/12-performance|Performance]]

**Contention.** Shared cache lines serialise regardless of your algorithm.

**False sharing.** Independent data on one line. → [[foundations/computer-architecture/09-caches-in-depth|False Sharing]]

**Memory bandwidth.** Cores share a memory controller. **A bandwidth-bound workload does not scale with cores** — this is common and frequently misdiagnosed as a locking problem.

**NUMA.** Remote memory is ~2× slower.

**The patterns that scale:**

- **Shard.** Per-thread state combined at the end. **The single most effective technique** — a per-thread counter summed at the end beats any atomic counter
- **Read-mostly.** Many readers of a shared line cost nothing; RCU and seqlocks exploit this
- **Partition the data**, not just the work — so each thread owns its own cache lines
- **Batch.** Amortise synchronisation over more work
- **Pin threads** to cores for cache and NUMA locality

## Practical notes

**Default to `seq_cst`.** Relax only with measurement and justification.

**Never use `volatile` for threading** in C or C++.

**Test on ARM.** Non-negotiable if you ship cross-platform concurrent code.

**Run ThreadSanitizer** in CI.

**Prefer message passing or immutability** where you can. **A design with no shared mutable state has no memory-model problems** — which is the real argument for channels, actors, and functional data structures.

**Measure scaling.** Plot throughput against thread count. **If it flattens or declines, find out why** before adding more threads — the answer is usually contention, false sharing, or bandwidth.

---

## Related
- [[foundations/computer-architecture/09-caches-in-depth|Caches in Depth]] — coherence, which this sits on top of
- [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — locks, futexes, and what to use instead
- [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]] — the same problem, one scale up
- [[foundations/computer-architecture/README|Architecture map]]
