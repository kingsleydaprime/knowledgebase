# Why Parallelism

**[Intermediate]** — The free lunch ended, what Amdahl actually limits, and the taxonomy that tells you which kind of parallel you need.

**Source:** `[reference]` — see [[foundations/gpu-and-parallel-computing/README|the domain note]].

## The end of free performance

**Until ~2005, single-thread performance doubled every couple of years.** Dennard scaling meant smaller transistors switched faster at the same power density, so clocks rose and your code got faster while you slept.

**Then power density hit a wall.**

$$P \approx CV^2f + \text{leakage}$$

**Power scales with frequency and with the square of voltage** — and higher clocks need higher voltage to switch reliably. **Around 4 GHz, a chip can no longer dissipate the heat.** → [[foundations/computer-architecture/01-what-architecture-is|Where performance comes from]]

**Moore's Law continued** — transistor counts kept rising. **They went into cores, caches, and specialised units instead of frequency.**

> **So performance is now something you have to *ask for*.** A single-threaded program on a 64-core machine uses 1.5% of it. **Parallelism stopped being an optimisation and became the only remaining source of speedup.**

## Amdahl's law

$$S = \frac{1}{(1-p) + p/N}$$

**$p$ is the parallelisable fraction; $N$ the number of processors.**

| Serial fraction | Max speedup, $N\to\infty$ |
|---|---|
| 0% | ∞ |
| 1% | **100×** |
| 5% | **20×** |
| 10% | 10× |
| 50% | 2× |

> **5% serial work caps you at 20×, however many cores you buy.** That's the number worth carrying — **the serial fraction, not the core count, is what limits you**, and finding it matters more than adding hardware.

**And the serial fraction includes things people forget:** startup, I/O, synchronisation, the final reduction, and any section holding a global lock.

**Gustafson's counter-argument** is the honest complement: **in practice you scale the problem to the machine.** Nobody buys a supercomputer to solve last year's problem faster — they solve a bigger one. **If the parallel work grows with $N$ while the serial part stays fixed, speedup scales linearly.**

**Both are right, about different questions.** Amdahl: *"how much faster is this fixed job?"* Gustafson: *"how much more can I do in the same time?"*

**The practical reading:** strong scaling (fixed problem, more cores) hits Amdahl's wall. **Weak scaling (problem grows with cores) is what large systems are actually designed for**, and it's why "does it scale?" needs the question clarified before it can be answered.

## Flynn's taxonomy

**Four categories, and knowing which you're in tells you which tool applies.**

| | Single instruction | Multiple instruction |
|---|---|---|
| **Single data** | **SISD** — classic scalar CPU | MISD — rare |
| **Multiple data** | **SIMD** — vector units, GPUs | **MIMD** — multicore, clusters |

**SIMD** — one instruction, many data elements. **AVX, NEON, and the heart of a GPU.** Requires the same operation on everything, which is exactly what array maths is. → [[foundations/computer-architecture/03-instruction-sets|SIMD]]

**MIMD** — independent instruction streams. **Threads on a multicore CPU, processes across a cluster.** Flexible, and much higher overhead per unit of work.

**SIMT** — "single instruction, multiple threads" — is NVIDIA's term for the GPU model, and it sits between the two: **it looks like MIMD to the programmer and executes like SIMD in hardware.** That gap is where most GPU performance surprises come from. → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]]

## Kinds of parallelism

**Data parallelism** — the same operation on many elements.

```
for i in range(N):   y[i] = f(x[i])      # every i independent
```

**The easiest kind, and it's what GPUs exist for.** Image processing, matrix maths, neural network layers, particle simulation.

**Task parallelism** — different operations concurrently. A pipeline stage per core, a thread pool of heterogeneous jobs. **Harder to balance**, since tasks differ in cost.

**Pipeline parallelism** — stages operating on different items simultaneously, like an assembly line. **Throughput improves; latency for one item doesn't.** Used in CPU instruction pipelines, video encoding, and pipelined model parallelism in ML training.

**Embarrassingly parallel** — no communication between workers at all. Monte Carlo runs, hyperparameter sweeps, batch image processing, rendering separate frames. **If your problem is this, stop reading and just run it $N$ times.**

## The costs

**Parallelism is never free**, and the overheads are where the promised speedup disappears.

**Synchronisation.** Locks, barriers, atomics. **A barrier costs the slowest thread's time** — everyone waits for the straggler.

**Communication.** Moving data between cores, sockets, or machines.

| Transfer | Rough latency |
|---|---|
| Same core (L1) | ~1 ns |
| Cross-core (L3) | ~20 ns |
| Cross-socket (NUMA) | ~100 ns |
| **CPU → GPU (PCIe)** | **~10 µs + transfer** |
| Node → node (InfiniBand) | ~1–2 µs |
| Node → node (Ethernet) | ~50 µs |

> **The CPU↔GPU line is the one that catches people.** Moving data across PCIe costs microseconds and limited bandwidth. **A GPU kernel that takes 50 µs and needs 200 µs of transfer is a net loss** — and this is the single most common reason a first GPU port is *slower* than the CPU version. → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]]

**Load imbalance.** If one worker gets twice the work, you've halved your efficiency. **Dynamic scheduling and work stealing** address it at some overhead.

**Contention.** Shared cache lines, memory bandwidth, a hot lock. **[[foundations/computer-architecture/09-caches-in-depth|False sharing]] can make a parallel program slower than the serial one** — independent variables on the same cache line, ping-ponging between cores.

**Correctness.** Race conditions, deadlocks, and memory-ordering bugs that appear once in $10^9$ runs on one architecture. → [[foundations/computer-architecture/11-multicore-and-memory-models|Memory Models]]

## Which hardware

**The decision that matters before any code is written.**

| | Good at | Bad at |
|---|---|---|
| **Multicore CPU** | branching, irregular control flow, low latency, large memory | massive data parallelism |
| **GPU** | **regular data parallelism, huge throughput** | branching, small problems, latency-critical work |
| **FPGA** | fixed pipelines, ultra-low latency, custom precision | development time, flexibility |
| **ASIC/TPU** | one workload, maximum efficiency | anything else |
| **Cluster** | problems exceeding one machine | fine-grained communication |

> **The rough rule: a GPU wins when you have thousands of independent identical operations and enough arithmetic per byte moved.** Below that, PCIe transfer and kernel launch overhead eat the gain.
>
> **A CPU with good SIMD and multithreading is often within 2–5× of a GPU** on realistic workloads, and it's far easier to program. **Measure before porting.**

## Scaling in practice

**Strong scaling** — fixed problem, more workers. **Measure with speedup: $T_1/T_N$.** Efficiency is $S/N$, and it decays as communication grows relative to work.

**Weak scaling** — problem grows with workers. **Measure whether time-per-worker stays flat.**

**Report which one you measured.** A paper claiming "linear scaling to 1000 nodes" without saying which is not saying much.

**The practical procedure:**

1. **Profile the serial version first.** Parallelising unoptimised code just wastes more cores → [[foundations/computer-architecture/12-performance|Performance]]
2. **Find the parallelisable fraction.** Amdahl tells you the ceiling before you start
3. **Start with the coarsest granularity that works.** Fine-grained parallelism has proportionally more overhead
4. **Measure at 1, 2, 4, 8, … workers.** **Plot it.** Where the curve bends is where your bottleneck is
5. **When it flattens, find out why** — contention, bandwidth, imbalance, or the serial fraction

## Practical notes

**Try the easy things first.** A better algorithm, better data layout, or SIMD often beats parallelising. **$O(n^2) \to O(n\log n)$ beats 64 cores.**

**Use a library or a framework.** OpenMP for shared-memory loops (often one `#pragma`), TBB, Rayon (Rust), `multiprocessing`/`joblib` (Python), MPI for clusters. **Hand-rolled thread pools are a common source of subtle bugs.**

**Beware Python's GIL.** Threads don't give CPU parallelism in CPython — use `multiprocessing`, or a library releasing the GIL (NumPy, PyTorch do). **Free-threaded CPython (3.13+, PEP 703) is changing this**, gradually.

**Prefer immutability and message passing** where you can. **A design with no shared mutable state has no data races** — which is the real argument for channels, actors and functional structures. → [[languages/02-go/07-concurrency-patterns|Go concurrency patterns]]

**Test on more cores than you develop on**, and under ThreadSanitizer.

**Watch memory bandwidth.** Many "parallel" workloads are bandwidth-bound and stop scaling at 4–8 cores regardless of how many you have. **This is frequently misdiagnosed as a locking problem.**

---

## Related
- [[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]] — what a GPU actually is
- [[foundations/computer-architecture/11-multicore-and-memory-models|Multicore and Memory Models]] — the correctness side
- [[foundations/computer-architecture/12-performance|Performance]] — profile before parallelising
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
