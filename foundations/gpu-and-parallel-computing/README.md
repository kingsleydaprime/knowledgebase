# GPU and Parallel Computing

What a GPU actually is, why "thousands of cores" is misleading, and how to make code fast on one. **The hardware layer under 98 notes of machine learning.**

**~12,100 words across 9 notes** (including practice + solutions). Built August 2026. `[reference]`.

> **The one idea:** a CPU hides memory latency with caches and speculation. **A GPU hides it by having so many threads that when one stalls, another is ready.** Everything else — warps, coalescing, occupancy, the roofline — follows from that single architectural choice.

## Why this exists

**`computer-architecture/README` flagged it directly:** *"GPU architecture — a genuine gap given the ML material in this vault."*

**`ai-ml/` is 98 notes and the largest domain here, and nothing explained the hardware underneath it** — what a tensor core is, why BF16 beat FP16, why batch size affects throughput so much, or why `.item()` in a training loop stalls the pipeline.

## Reading order

**01–02 are the concepts. 03–05 are how to write and tune code. 06 is the diagnostic framework. 07 is scaling out.**

1. [[foundations/gpu-and-parallel-computing/01-why-parallelism|Why Parallelism]] — **[Intermediate]** — the end of frequency scaling, **Amdahl vs Gustafson**, Flynn's taxonomy, and which hardware suits which problem
2. [[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]] — **[Intermediate → Advanced]** — SMs, **the warp and divergence**, occupancy, the memory hierarchy, tensor cores, and when a GPU is the wrong answer
3. [[foundations/gpu-and-parallel-computing/03-the-programming-model|The Programming Model]] — **[Intermediate → Advanced]** — kernels, grids and blocks, **why there's no global barrier**, streams, and the framework stack
4. [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]] — **[Advanced]** — map, reduce, **scan** (the surprising one), stencil, histogram, tiled matmul, and kernel fusion
5. [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]] — **[Advanced]** — **coalescing**, shared memory, bank conflicts, and the PCIe transfer that ruins most first ports
6. [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Performance and the Roofline]] — **[Intermediate → Advanced]** — arithmetic intensity, the roofline diagram, honest benchmarking, and the ML-specific bottlenecks
7. [[foundations/gpu-and-parallel-computing/07-distributed-and-multi-gpu|Distributed and Multi-GPU]] — **[Advanced]** — data/tensor/pipeline parallelism, ZeRO and FSDP, ring all-reduce, and inference at scale

## The things worth carrying

1. **A GPU hides latency with parallelism, not caches.** That's the entire design → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|02]]
2. **"16,384 CUDA cores" means ALU lanes.** A better model is ~132 SMs with very wide SIMD → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|02]]
3. **A warp is 32 threads in lockstep.** Divergence *within* a warp serialises; divergence *between* warps is free → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|02]]
4. **There is no global barrier inside a kernel.** Kernel boundaries are the sync points, and that shapes every GPU algorithm → [[foundations/gpu-and-parallel-computing/03-the-programming-model|03]]
5. **Coalescing is the single biggest memory lever** — up to 32× traffic for the same data. Map thread index to the fastest-varying dimension → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|05]]
6. **PCIe is ~100× slower than local GPU memory.** Keep data resident; a fused pipeline beats faster individual kernels → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|05]]
7. **Arithmetic intensity tells you which bound you're against.** Element-wise ops are always bandwidth-bound; matmul's intensity grows with size, which is why GPUs suit deep learning → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|06]]
8. **`nvidia-smi` "utilisation" means "a kernel was running", not "the hardware was used well."** 100% is compatible with 3% of peak FLOPS → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|06]]
9. **Mixed precision is about tensor cores, not just memory** — roughly 15× the FLOPS on an H100 → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|02]]
10. **Scan parallelises in $O(\log n)$** despite looking sequential, and it's what makes stream compaction and radix sort work → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|04]]
11. **Higher occupancy is not the goal.** It's a means of hiding latency → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|02]]
12. **NVLink is ~20× PCIe**, which is why tensor parallelism stays inside a node → [[foundations/gpu-and-parallel-computing/07-distributed-and-multi-gpu|07]]

## Where this connects

| | |
|---|---|
| [[ai-ml/02-ml-engineer/05-deep-learning/README\|deep learning]] | **The reason this exists.** Mixed precision, batch size, throughput |
| [[foundations/computer-architecture/README\|computer architecture]] | The CPU this is contrasted against |
| [[foundations/numerical-methods/04-linear-systems\|numerical methods]] | The linear algebra that actually runs here |
| [[foundations/computer-architecture/11-multicore-and-memory-models\|memory models]] | CPU-side parallel correctness |
| [[architecture/04-distributed-systems/README\|distributed systems]] | Large training runs are distributed systems |
| [[foundations/computer-graphics/README\|computer graphics]] | What GPUs were originally built for |

## The honest note

**`[reference]`, and this one has a specific asymmetry: the concepts are cheap to verify, the tuning is not.**

**You can confirm coalescing, divergence and the roofline on any consumer GPU in an afternoon.** What you can't get from reading is the judgement of when a kernel is *done* — when the remaining 20% isn't worth the complexity.

**What would close the gap:**

1. **Write vector add, then time it.** Compute its arithmetic intensity by hand, predict the runtime from bandwidth alone, and check. **When the prediction is right, the roofline stops being abstract**
2. **Deliberately break coalescing.** Transpose the index calculation and measure. **Watching a 10–30× slowdown from one swapped index is the fastest way to internalise note 05**
3. **Write a reduction three ways** — naive atomics, shared memory tree, warp shuffle. Measure each
4. **Implement tiled matmul**, compare against cuBLAS, and see how far short you fall. **Then read CUTLASS to find out why**
5. **Profile a real training loop** with the PyTorch profiler. **Find the data-loading gaps** — they're almost always there
6. **Try `torch.compile`** on a model and measure. The speedup is mostly fusion, which is note 04
7. **The resources:** the CUDA C++ Programming Guide (dense, authoritative); *Programming Massively Parallel Processors* (Kirk & Hwu) — the standard textbook; **the Triton tutorials**, which are the best modern on-ramp; and the FlashAttention paper, which is a masterclass in memory-aware kernel design

**No GPU?** Colab and Kaggle give free ones, and **most of these experiments run fine on a T4.**

**What's missing:** ~~exercises~~ — **closed by notes 8–9 (Aug 2026)**; ray tracing hardware, graphics pipeline specifics (that's [[foundations/computer-graphics/README|computer graphics]]), FPGA and ASIC design, sparse and irregular workloads in depth, and power/thermal management.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[foundations/gpu-and-parallel-computing/08-practice-exercises|Practice Exercises]] — twelve exercises, with an **honest no-GPU path** — Amdahl, coalescing, the transfer tax, the roofline
- [[foundations/gpu-and-parallel-computing/09-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[ai-ml/README|AI & ML]] — the domain this sits under
- [[foundations/computer-architecture/README|Computer Architecture]] — the CPU side
- [[foundations/numerical-methods/README|Numerical Methods]] — what runs on this hardware
- [[BUILD-PLAN|Build Plan]]
