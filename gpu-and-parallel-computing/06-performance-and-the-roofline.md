# Performance and the Roofline

**[Intermediate → Advanced]** — Arithmetic intensity, the one diagram that tells you what to optimise, and how to benchmark a GPU honestly.

## Arithmetic intensity

$$I = \frac{\text{FLOPs performed}}{\text{bytes moved from memory}}$$

**The single number that determines whether you're limited by compute or by bandwidth.**

**Worked examples, and the spread is the point:**

| Operation | FLOPs | Bytes | Intensity |
|---|---|---|---|
| Vector add ($c = a+b$) | $n$ | $12n$ | **0.083** |
| SAXPY ($y = ax+y$) | $2n$ | $12n$ | 0.17 |
| Dot product | $2n$ | $8n$ | 0.25 |
| **Matrix–vector** | $2n^2$ | $\sim4n^2$ | **0.5** |
| **Matrix–matrix** ($n^3$) | $2n^3$ | $\sim12n^2$ | **$\propto n$ — grows!** |

> **Element-wise operations have intensity below 1.** They are **always** bandwidth-bound, on every machine, and no amount of arithmetic optimisation helps. **The only lever is moving fewer bytes** — fuse them, or use smaller types.
>
> **Matrix multiply is the outlier: intensity grows with size.** $O(n^3)$ work against $O(n^2)$ data. **That's exactly why GEMM can saturate a GPU and why deep learning maps so well onto this hardware** — the workload is mostly large matmuls.

## The roofline model

**Plot achievable performance against arithmetic intensity, log–log:**

```
 GFLOP/s
   │                    ┌──────────────  peak compute
   │                  ╱
   │                ╱        ← compute-bound region
   │              ╱
   │            ╱  ← slope = memory bandwidth
   │          ╱
   │        ╱      ← memory-bound region
   │      ╱
   └────────────────────────────────► arithmetic intensity
          ↑
      ridge point = peak FLOPS / bandwidth
```

$$\text{attainable} = \min(\text{peak FLOPS},\ I \times \text{bandwidth})$$

**The ridge point is where the two limits cross.** For an H100 in FP16: $990/3.35 \approx 295$ FLOP/byte.

> **Everything with intensity below the ridge is memory-bound, however much compute you have.** Buying a faster GPU with the same bandwidth does nothing for those kernels.
>
> **The roofline turns "why is this slow" into two concrete questions:** *which side of the ridge am I on*, and *how close to the roof*?

**How to use it:**

**Compute your kernel's intensity** — count FLOPs and bytes, or read them from Nsight Compute.

**Plot your achieved performance.**

| Position | What to do |
|---|---|
| Below the roof, memory-bound | **fuse, tile, use smaller types, fix coalescing** |
| Below the roof, compute-bound | use tensor cores, reduce instruction count, fix divergence |
| **On the roof** | **you're done — the algorithm is the only remaining lever** |

**The "ceilings" refinement** adds sub-rooflines for not using tensor cores, not vectorising, or poor coalescing — **so the gap between your point and the top roof decomposes into named causes.**

## Benchmarking honestly

**GPU benchmarking has its own specific traps**, and most reported numbers hit at least one.

**Synchronise before timing.** Kernel launches are asynchronous.

```cuda
cudaDeviceSynchronize();  start = now();
kernel<<<...>>>();
cudaDeviceSynchronize();  end = now();     // ✓
```

**Without the second sync you time the launch, not the work.** Microsecond kernel times in a beginner benchmark are almost always this. **Or use CUDA events**, which time on the device and are more accurate.

**Warm up.** The first launch pays JIT compilation, context creation and allocation. **Discard several iterations.**

**Watch clock throttling.** GPUs boost then throttle under sustained load. **A short benchmark measures boost clocks you won't sustain.** Lock clocks with `nvidia-smi -lgc` for reproducibility, or run long enough to reach steady state.

**Include the transfer if it's part of the real workload.** A kernel benchmark excluding PCIe is measuring something you can't actually get.

**Compare against a *good* CPU baseline.** Multithreaded, SIMD-enabled, `-O3`, using the right library.

> **This is where most "100× speedup" claims come from — a tuned GPU implementation against single-threaded unoptimised CPU code.** **Realistic figures against a well-optimised CPU baseline are 5–20×**, and saying so is more useful than the marketing number.

**Report the distribution**, not one run. Median and p99 — GPU timings have real variance from scheduling and thermal effects.

## The tooling

**Nsight Compute** — per-kernel analysis. **Occupancy, memory throughput, coalescing efficiency, warp stall reasons, roofline placement.** The tool to reach for when one kernel is slow.

**Nsight Systems** — the timeline. **Shows kernel execution, transfers, CPU activity and gaps.** The tool for "where is the time actually going" across a whole application, and it's how you find that you're transfer-bound or launch-bound rather than compute-bound.

**`nvidia-smi`** — utilisation, memory, power, temperature, clocks.

> **A warning about "GPU utilisation" in `nvidia-smi`: it reports the fraction of time *at least one kernel was running*, not how well you're using the hardware.** **100% utilisation is entirely compatible with using 3% of the FLOPS.** It's a coarse "is anything running" signal, not an efficiency metric — and it misleads a lot of people.

**PyTorch profiler / `torch.profiler`** — operator-level attribution for ML workloads, with a trace viewer. **Start here for model work** rather than dropping to Nsight.

## Common bottlenecks in ML

**Since that's the biggest consumer of GPUs in this vault:**

**Data loading.** The GPU idles while the CPU decodes JPEGs. **Extremely common.** More workers, prefetch, a faster format (WebDataset, FFCV), or GPU decoding (DALI). **Check GPU utilisation over time — sawtooth means you're input-bound.**

**Small batch size.** Underutilises the hardware and makes launch overhead significant. **Larger batches (with a scaled learning rate) usually improve throughput substantially.**

**Unfused element-wise chains.** Bandwidth-bound, and `torch.compile` fixes most of them for free. → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Kernel Fusion]]

**Not using tensor cores.** FP32 without TF32, or shapes not multiples of 8/16. **A dimension of 4095 instead of 4096 can cost you a large fraction of peak.** → [[foundations/gpu-and-parallel-computing/02-gpu-architecture|Tensor Cores]]

**Host↔device sync in the training loop.** Any `.item()`, `.cpu()`, or `print(loss)` **forces a synchronisation and stalls the pipeline.** Accumulate on device and log every N steps.

**Memory-bound attention** — solved by FlashAttention, which fuses the computation so the $N\times N$ matrix never reaches global memory.

**Gradient synchronisation** in multi-GPU training. → [[foundations/gpu-and-parallel-computing/07-distributed-and-multi-gpu|Distributed and Multi-GPU]]

## The optimisation order

**Same discipline as [[foundations/computer-architecture/12-performance|CPU performance]], different specifics:**

```
1. PROFILE               Nsight Systems for the timeline
2. Is the GPU even busy? → fix data loading / launch overhead first
3. Which bound?          → roofline: memory or compute
4. If memory-bound:      coalescing → fusion → tiling → smaller types
5. If compute-bound:     tensor cores → divergence → instruction mix
6. Only then:            micro-optimise the kernel
7. RE-PROFILE
```

**Step 2 is the one people skip.** **A GPU sitting idle 60% of the time because of data loading cannot be fixed by optimising kernels**, and it's a very common situation.

## Practical notes

**Measure before porting to GPU at all.** Compute the arithmetic intensity by hand. **If it's below 1 and the data doesn't already live on the device, the transfer will dominate.**

**Keep data resident.** The single biggest structural win.

**Use the libraries** — cuBLAS, cuDNN, and `torch.compile`. They implement the optimisations above better than hand-written code.

**Try mixed precision early.** BF16 usually costs no accuracy and buys both bandwidth and tensor cores. → [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]]

**Batch aggressively.** GPUs are throughput machines; small work starves them.

**Watch memory capacity, not just bandwidth.** Running out of VRAM forces smaller batches or gradient checkpointing, both of which cost throughput.

**Don't chase occupancy as a goal.** It's a means of hiding latency, and high-ILP kernels do fine at 25%.

---

## Related
- [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]] — the memory-bound fixes
- [[foundations/computer-architecture/12-performance|Performance]] — the CPU-side methodology
- [[foundations/gpu-and-parallel-computing/07-distributed-and-multi-gpu|Distributed and Multi-GPU]] — when one GPU isn't enough
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
