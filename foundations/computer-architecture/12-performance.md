# Performance

**[Intermediate → Advanced]** — Turning everything in this track into a method for actually making code faster.

## The method

**In order, and the order matters more than any individual technique:**

```
1. MEASURE      profile — find where the time goes
2. UNDERSTAND   why is it slow? which resource is saturated?
3. ALGORITHM    better complexity beats every micro-optimisation
4. DATA LAYOUT  cache behaviour usually dominates
5. MICRO-OPT    branches, ILP, SIMD
6. MEASURE      confirm it worked
```

> **Steps 1 and 6 are where people fail.** Optimising without measuring means optimising the wrong thing, and **not re-measuring means shipping a "faster" version that isn't.**
>
> **Programmer intuition about performance is unreliable**, including experienced programmers, including yours. The profiler is not optional.

## Amdahl's law

$$S = \frac{1}{(1-p) + p/s}$$

**Speeding up a fraction $p$ of the program by $s$ gives overall speedup $S$.**

| Fraction optimised | Made infinitely fast | Overall speedup |
|---|---|---|
| 10% | ∞ | **1.11×** |
| 50% | ∞ | 2× |
| 90% | ∞ | 10× |
| 90% | 2× | 1.8× |

> **Optimising something that takes 10% of runtime caps your gain at 11%, even if you make it free.** This is the argument for profiling first, stated arithmetically.

**Its multicore form:** with 5% inherently serial work, **maximum speedup is 20× regardless of core count.**

**Gustafson's counter-argument** is worth knowing: in practice you often scale the *problem* to the machine rather than fixing problem size. **More cores let you solve bigger problems in the same time**, even if they don't solve the same problem faster.

## Finding the bottleneck

**Which resource is saturated?** The answer determines everything you do next.

```
perf stat ./program
```

**Read the IPC first:**

| IPC | Diagnosis |
|---|---|
| **< 0.5** | badly stalled — almost certainly **memory** |
| ~1.0 | mediocre; check branches and dependencies |
| 2–3 | healthy |
| 4+ | near peak; only algorithmic gains left |

**Then the specific counters:**

```
perf stat -e cycles,instructions,\
             cache-misses,LLC-load-misses,\
             branch-misses,dTLB-load-misses ./program
```

| Symptom | Likely cause | Fix |
|---|---|---|
| High LLC misses | **memory-bound** | data layout, blocking, smaller types |
| High branch misses | unpredictable branches | sort data, branchless, restructure |
| High dTLB misses | large working set | huge pages |
| Low IPC, few misses | **dependency chains** | multiple accumulators, unroll |
| High IPC, still slow | **algorithm** | better complexity |

**Then locate it:**

```
perf record -g ./program && perf report
perf annotate            # per-instruction, with sample counts
```

> **`perf annotate` frequently surprises.** The hot instruction is often a load you never thought about, not the arithmetic you assumed. **Attribution can skew by a few instructions** due to sampling — look at the surrounding block, not one line.

## The tools

| Tool | For |
|---|---|
| **`perf`** | Linux profiling. **The default. Learn this one** |
| **Flame graphs** | visualising `perf record` output |
| `valgrind --tool=callgrind` | exact call counts, ~50× slowdown |
| `cachegrind` | simulated cache behaviour, deterministic |
| **`perf c2c`** | **false sharing specifically** |
| Intel VTune / AMD uProf | vendor tools, deeper counters |
| `heaptrack`, `massif` | allocation profiling |
| `strace` / `bpftrace` | syscalls, kernel time |

**Sampling vs instrumentation:**

**Sampling** (perf) — interrupt periodically, record the stack. **Low overhead (~1%), statistical, safe in production.**

**Instrumentation** (callgrind) — count everything exactly. **Precise, enormously slow, and it perturbs what it measures.**

**Use sampling by default.**

## Benchmarking honestly

**The part that's easy to get wrong**, and a wrong benchmark is worse than none.

**The compiler will delete your benchmark:**

```c
for (i = 0; i < N; i++) expensive_function(x);   // result unused → removed entirely
```

**Use `black_box` (Rust), `benchmark::DoNotOptimize` (Google Benchmark), or consume the result.**

**Warm up.** The first iterations pay for cold caches, page faults, JIT compilation, and branch predictor training. **Discard them.**

**Report distributions, not means.** Run many iterations; report median and p99. **A single number hides bimodality**, and the tail is often what users experience.

**Control the environment.** Disable turbo and frequency scaling (`cpupower frequency-set -g performance`), pin to a core (`taskset`), and close other work. **Frequency scaling alone can produce 30% run-to-run variation.**

**Measure the right thing.** A microbenchmark with everything in L1 tells you nothing about production behaviour with a cold cache and a large working set. **Microbenchmarks routinely predict the wrong winner** for exactly this reason.

**Use a framework:** Google Benchmark (C++), Criterion (Rust), JMH (Java). **They handle warmup, statistics, and optimiser defeat properly** — all things that are easy to get subtly wrong by hand.

## The techniques, ordered by payoff

**1. Better algorithm.** $O(n^2) \to O(n\log n)$ beats every micro-optimisation, and no amount of cache tuning saves a quadratic algorithm at scale. → [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]]

**2. Do less work.** Cache results, avoid recomputation, exit early, batch operations, **eliminate the work entirely.** The fastest code is the code that doesn't run.

**3. Better data layout.** **Usually the largest win after algorithm.** Contiguous over pointer-linked, SoA where appropriate, hot/cold splitting, smaller types. → [[foundations/computer-architecture/08-the-memory-hierarchy|Memory Hierarchy]]

**4. Reduce allocation.** Arena and pool allocators, reuse buffers, stack over heap, reserve capacity upfront. **Allocation is often a surprising fraction of runtime**, and it fragments your cache. → [[foundations/os/05-memory-allocation|Memory Allocation]]

**5. Parallelise** — after the single-threaded version is good. **Parallelising bad code just uses more cores badly.** → [[foundations/computer-architecture/11-multicore-and-memory-models|Multicore]]

**6. Compiler flags.** `-O2`, `-march=native`, LTO, PGO. **PGO is underused and gives 5–20%** on branch-heavy code for essentially no effort — it lets the compiler lay out code according to actual behaviour.

**7. SIMD** — for data-parallel inner loops. Check auto-vectorisation first. → [[foundations/computer-architecture/03-instruction-sets|SIMD]]

**8. Micro-optimisation** — branchless code, multiple accumulators, unrolling. **Last, and only where the profiler points.**

## Latency vs throughput

**Different goals, different techniques**, and conflating them causes bad decisions.

**Throughput** — work per second. Batch, pipeline, parallelise, amortise. **Buffering helps.**

**Latency** — time for one operation. **Buffering hurts.** Minimise queuing, avoid GC pauses, pre-warm caches.

**Tail latency** is usually what matters for services. **p99 and p999, not the mean.**

> **Tail latency amplifies in distributed systems.** A request fanning out to 100 servers waits for the slowest — **so the p99 of one service becomes the median of the aggregate.** This is why "the average is fine" is not an adequate answer. → [[architecture/01-system-design-fundamentals/README|System Design]]
>
> **Sources of tail latency:** GC pauses, cache misses on cold data, lock contention, page faults, network retransmits, and background work like compaction. **Techniques:** hedged requests, tail-tolerant design, and reducing variance rather than the mean.

## When to stop

**The honest part.**

**Set a target first.** "Fast enough" needs a definition, or you optimise forever.

**Diminishing returns are real.** The first fix might give 10×; the fifth gives 3%.

**Optimised code costs you.** It's harder to read, harder to change, and more likely to be wrong. **Every micro-optimisation is a maintenance liability**, and you should be able to justify each one with a measurement.

**Correctness first, always.** A fast wrong answer is worthless, and `-ffast-math` in particular changes results.

> **Knuth's line is usually misquoted.** The full version: *"We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. **Yet we should not pass up our opportunities in that critical 3%.**"*
>
> **The point isn't "don't optimise" — it's "find the 3% first."** That's what profiling is for.

## A worked example

**A realistic sequence, to show the method:**

```
Starting point:                          10.0 s
1. perf → 80% in one function
2. That function is O(n²) → O(n log n):   2.0 s   (5×)
3. perf → IPC 0.4, high LLC misses
4. AoS → SoA, better locality:            0.8 s   (2.5×)
5. perf → IPC 1.8, high branch-misses
6. Sort input so branches predict:        0.5 s   (1.6×)
7. Auto-vectorisation with -march=native: 0.3 s   (1.7×)
8. Parallelise across 8 cores:            0.06 s  (5×)
                                          ────────
                                          160× total
```

**Every step was chosen by measurement**, and every step's speedup came from a different bottleneck. **Doing them in a different order would have wasted most of the effort** — parallelising the $O(n^2)$ version first would have bought 8× instead of 160×.

---

## Related
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — where most of the wins are
- [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]] — reading IPC
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — the step that beats everything else
- [[foundations/computer-architecture/README|Architecture map]]
