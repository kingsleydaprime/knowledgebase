# Practice Exercises — Solutions

> **[Advanced]** · Worked answers to [[foundations/gpu-and-parallel-computing/08-practice-exercises|note 08]].

**An honest caveat this file must carry:** the GPU figures below are **representative values from vendor documentation and published benchmarks, not measurements I made.** This vault has no GPU. The CPU-side exercises (1, 2) and the roofline reasoning (10, 11) *are* verifiable here and stated as such. **Where a number is borrowed rather than measured, it says so** — and that distinction is exactly the honesty this vault's `[reference]` marker exists for.

---

## Part A — Parallelism

### 1. Amdahl's law

Speedup with $n$ workers, serial fraction $s$:
$$S(n) = \frac{1}{s + \frac{1-s}{n}} \qquad\text{and}\qquad \lim_{n\to\infty} S(n) = \frac{1}{s}$$

**Read $s$ off your own plateau.** If speedup tops out near 5× no matter how many cores you add, then $s \approx 0.2$ — 20% of the work is irreducibly serial.

**The uncomfortable consequence:** at $s = 0.1$, the ceiling is 10× **on infinite hardware**. Adding cores past that buys nothing.

**Which is why the first question about any parallelisation is "what fraction is actually parallel?"** — not "how many cores can I get?" Gustafson's law is the optimistic counterpart: if the *problem* grows with the machine, the serial fraction shrinks. Both are true; they answer different questions → [[foundations/gpu-and-parallel-computing/01-why-parallelism|note 01]].

### 2. Where parallelism loses

There is always a crossover, typically somewhere in $10^4$–$10^6$ elements for trivial work in Python.

**The three costs below it:**
1. **Startup** — process creation is ~10s of ms; thread creation ~µs
2. **Serialisation** — arguments and results are pickled and copied between processes → [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]
3. **Coordination** — scheduling, synchronisation, result collection

**The rule: work per task must dwarf the overhead per task.** Parallelising something cheap is reliably slower than doing it serially — and this is the same reasoning that decides whether to offload to a GPU at all.

---

## Part B — The programming model

### 3. Your first kernel

```cuda
__global__ void vadd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}
```

`blockIdx.x * blockDim.x + threadIdx.x` computes a **globally unique index** for this thread: which block am I in, times how big a block is, plus my position within it.

**It's the standard idiom because the model is deliberately two-level** — blocks are scheduled independently onto SMs (which gives scalability across GPU sizes), and threads within a block can cooperate via shared memory. The flat index reconstructs a 1-D view over that 2-D hierarchy → [[foundations/gpu-and-parallel-computing/03-the-programming-model|note 03]].

### 4. Launch configuration

Representative shape (from vendor guidance):

| Block size | Outcome |
|---|---|
| 1 | **Catastrophic** — 1/32 of the hardware used |
| 32 | Correct minimum; one full warp |
| 128–256 | **Usually optimal** |
| 1024 | Often fine; may reduce occupancy by exhausting registers |

**Block size 1 wastes 31/32 of every warp.** A warp is 32 threads executing in lockstep — the hardware's actual scheduling unit. A block of 1 thread still occupies a whole warp slot, so you use 3% of the machine.

**Always make block size a multiple of 32.** Above that, the trade is occupancy against per-thread resources; 128 or 256 is the standard starting point → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|note 02]].

### 5. Out-of-bounds thread

Grid sizes are computed as `ceil(n / blockSize)`, which almost always launches **more threads than elements**. Without `if (i < n)`, the surplus threads write past the end — corrupting memory or triggering an illegal-access error.

**That guard is in essentially every CUDA kernel ever written**, and its absence is the first thing to check when a kernel produces garbage.

---

## Part C — Memory

### 6. The transfer tax

Representative for $10^8$ floats (400 MB per array) over PCIe 4.0 (~25 GB/s effective) with a modern discrete GPU:

| Stage | Time | Share |
|---|---|---|
| Host → device (2 arrays, 800 MB) | ~32 ms | ~48% |
| Kernel (vector add) | **~1 ms** | **~1.5%** |
| Device → host (400 MB) | ~16 ms | ~24% |

**Roughly 1–3% of the time is computation.** The rest is moving data across PCIe.

**This is the most important number in the course.** Vector addition does 1 FLOP per 12 bytes moved — hopeless arithmetic intensity. **The GPU is not the bottleneck; the bus is.**

**The consequences shape all real GPU code:** keep data resident on the device across many kernels, fuse operations to avoid round trips, overlap transfer with compute using streams, and **do not offload an operation whose data movement costs more than the computation saves.** It's also why unified memory, NVLink and on-package memory exist → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|note 05]].

### 7. Coalescing

Representative: **stride-32 access is roughly 10–30× slower** than consecutive access.

**Why:** memory is served in transactions (typically 32-byte sectors / 128-byte lines). When 32 consecutive threads read 32 consecutive floats, that's ~128 bytes — **one or a few transactions serving the whole warp.** With a stride of 32, each thread touches a different line, so the warp needs **32 separate transactions** and 31/32 of every fetched line is discarded.

**Same instruction count. Same FLOPs. 32× the memory traffic.**

**This is the GPU version of exercise 5 in [[foundations/computer-architecture/13-practice-exercises|the architecture exercises]]** — cache-line utilisation — and it is why data layout (struct-of-arrays over array-of-structs) dominates GPU performance work.

### 8. Shared memory tiling

**Arithmetic intensity** = FLOPs ÷ bytes loaded from global memory.

- **Naive matmul:** each thread loads $2N$ values for $2N$ FLOPs ⇒ intensity ≈ 0.25 FLOP/byte for floats. **Deeply memory-bound**
- **Tiled with a $T\times T$ tile:** each element loaded into shared memory is reused $T$ times ⇒ intensity rises by a factor of ~$T$. At $T=32$, ~8 FLOP/byte — **compute-bound territory**

Typical speedup **5–10×**, from reuse alone. The arithmetic is identical.

**Shared memory is a programmer-managed cache**, and tiling is the canonical use: stage a tile cooperatively, `__syncthreads()`, compute from it, move on → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|note 06]].

### 9. Warp divergence

- **`threadIdx.x % 2`** — alternating threads take different branches, so **every warp diverges.** The hardware executes both paths serially with half the lanes masked off. ~2× cost
- **`threadIdx.x / 32`** — the branch is *uniform within each warp*, so no warp diverges. Different warps take different paths, which is free

**Same branches, same total work, different cost — because the branch granularity matched the warp.**

**This is SIMT's defining constraint:** a warp has one program counter. Divergence within a warp serialises; divergence across warps is free. **Structure your data so threads in a warp agree.**

---

## Part D — Roofline and scale

### 10. Build a roofline

$$\text{Attainable FLOP/s} = \min(\text{peak FLOP/s},\ \text{peak bandwidth} \times \text{arithmetic intensity})$$

Plotted log-log, that's a diagonal (bandwidth-limited) meeting a horizontal ceiling (compute-limited). **The ridge point** — peak FLOP/s ÷ peak bandwidth — is the intensity you must exceed to be compute-bound. On modern GPUs it's roughly **10–100 FLOP/byte**, and it has been *rising*: compute has outpaced bandwidth for decades.

| Kernel | Intensity | Verdict |
|---|---|---|
| Vector add | ~0.08 | **Memory-bound**, hopelessly |
| Reduction | ~0.25 | Memory-bound |
| Naive matmul | ~0.25 | Memory-bound |
| **Tiled matmul ($T$=32)** | ~8 | Approaching compute-bound |
| Dense matmul, well-tuned | 10–100 | **Compute-bound** |

**You can classify a kernel before writing it**, by counting FLOPs and bytes on paper. **That prediction is the whole value of the roofline** — it tells you whether to optimise arithmetic (pointless if memory-bound) or data movement.

**It's also why matrix multiplication is the operation GPUs are marketed on:** it's one of the few common kernels with high enough intensity to reach peak. And it's why transformer inference is memory-bound at batch size 1 and compute-bound at large batch → [[ai-ml/README|AI & ML]].

### 11. Predict, then measure

No answer — the log is the artefact.

**The systematic error is underestimating the transfer tax.** People predict "the copy is maybe 20% of the time" and it's 90%+. **Being wrong here is more instructive than being right**, and it's the same calibration habit as [[foundations/computer-architecture/13-practice-exercises|architecture exercise 12]].

### 12. Profile a real kernel

Nsight Compute reports **achieved occupancy** (active warps vs maximum), **memory throughput** as a percentage of peak, and a **limiter** — memory-bound, compute-bound, or latency-bound.

**Two things worth knowing:**

**High occupancy is not the goal.** It's a means of hiding memory latency. A kernel at 25% occupancy that saturates bandwidth is *finished* — raising occupancy would do nothing. Chasing occupancy as a metric is a common waste.

**If the profiler disagrees with your roofline**, the usual causes are uncoalesced access (so effective bandwidth is far below peak), shared-memory bank conflicts, or register spilling to local memory. **The discrepancy is the finding** — it means one of your assumptions about the memory pattern was wrong.

## Related
- [[foundations/gpu-and-parallel-computing/08-practice-exercises|the exercises]]
- [[foundations/gpu-and-parallel-computing/README|the course]]

*Source: [reference] — **GPU figures are representative values from vendor documentation, not measured here** (this vault has no GPU). The Amdahl and roofline reasoning is hardware-independent.*
