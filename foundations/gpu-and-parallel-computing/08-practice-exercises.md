# Practice Exercises

> **[Advanced]** · Twelve exercises. **Most need a GPU — and there's an honest path for you if you don't have one.**

**The hardware problem, stated plainly:** this is the one domain in the vault where the exercises genuinely need hardware you may not own. Three routes:

| Route | Cost | Good for |
|---|---|---|
| **Google Colab** — free T4 | £0 | **Everything here.** The recommended route |
| Kaggle notebooks | £0 | 30 h/week of T4/P100 |
| A cloud instance | ~£0.50/h | Exercises 10–12 |
| **CPU only** | £0 | Exercises 1, 2, 11 and the *reasoning* in all of them |

**Exercises marked 🖥️ work without a GPU.** The roofline and Amdahl reasoning is hardware-independent and is arguably the most transferable part of the course.

Solutions in [[foundations/gpu-and-parallel-computing/09-practice-exercises-solutions|note 09]].

---

## Part A — Parallelism, before any GPU (note 01)

**1. 🖥️ Measure Amdahl's law on your own code.**
Take something with a genuinely serial section (reading a file, then processing it in parallel). Measure with 1, 2, 4, 8 threads or processes.
**Done when:** your speedup curve flattens, and you can estimate the serial fraction $s$ from the plateau via $1/s$ → [[foundations/gpu-and-parallel-computing/01-why-parallelism|note 01]].

**2. 🖥️ Find the point where parallelism loses.**
Parallelise a trivial operation (squaring a number) across a process pool, for arrays of $10^2$ to $10^7$ elements. Time against the serial version.
**Done when:** you have the **crossover size** below which parallel is *slower*, and can name the three costs that dominate below it.

---

## Part B — The programming model (notes 02–03)

**3. Write your first kernel.**
Vector addition in CUDA (or Triton, or Numba `@cuda.jit`, or a compute shader). Verify against NumPy.
**Done when:** it's correct **and** you can explain what `blockIdx.x * blockDim.x + threadIdx.x` computes and why it's the standard idiom.

**4. Get the launch configuration wrong.**
Run your kernel with block sizes of 1, 32, 128, 256, 1024. Time each.
**Done when:** block size 1 is catastrophically slow, you know why 32 matters specifically, and you can state your GPU's warp size → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|note 02]].

**5. Cause an out-of-bounds thread.**
Launch more threads than array elements without a bounds check. Observe. Then add `if (i < n)`.
**Done when:** you understand why the guard is in essentially every CUDA kernel ever written.

---

## Part C — Memory, the real subject (note 05)

**6. Measure the transfer tax.**
Time: host→device copy, kernel, device→host copy, separately, for a vector add on $10^8$ floats.
**Done when:** you can state what fraction of total time was *compute*. **It will be small, and that is the single most important number in this course** → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|note 05]].

**7. Break coalescing.**
Write a kernel where consecutive threads read consecutive elements, then one where they read with a stride of 32. Time both.
**Done when:** you have the ratio, and can relate it to the number of memory transactions each pattern generates.

**8. Use shared memory.**
Implement tiled matrix multiplication using shared memory, and compare against the naive version.
**Done when:** you can state the arithmetic intensity of each (FLOPs per byte loaded) and why tiling improves it → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|note 06]].

**9. Demonstrate warp divergence.**
A kernel where threads branch on `threadIdx.x % 2` versus one branching on `threadIdx.x / 32`. Same work, same branch count.
**Done when:** the second is substantially faster, and you can explain it in terms of what a warp executes.

---

## Part D — Roofline and scale (notes 06–07)

**10. 🖥️ Build a roofline for your hardware.**
Look up (or measure) peak FLOP/s and peak memory bandwidth. Plot the roofline. Place vector-add, matrix-multiply and a reduction on it by computing their arithmetic intensity.
**Done when:** you can say which are memory-bound and which compute-bound **before running them**, and your measurements agree → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|note 06]].

**11. 🖥️ Predict, then measure.**
Before exercise 6 and exercise 7, write down your predicted ratios.
**Done when:** you have predictions and measurements side by side. **Most people badly underestimate the transfer tax.**

**12. Profile a real kernel.**
Run Nsight Compute (or `nvprof`) on your tiled matmul. Find achieved occupancy, memory throughput, and the limiting factor it reports.
**Done when:** the profiler's verdict matches your roofline prediction — or you can explain the discrepancy.

## Related
- [[foundations/gpu-and-parallel-computing/09-practice-exercises-solutions|Solutions]]
- [[foundations/gpu-and-parallel-computing/README|the course]]
- [[foundations/computer-architecture/13-practice-exercises|architecture exercises]] — the same method on the CPU

*Source: [reference] — built from this course's own gap-closing list.*
