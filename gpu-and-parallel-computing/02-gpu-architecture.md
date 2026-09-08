# GPU Architecture

**[Intermediate → Advanced]** — What a GPU actually is, why "thousands of cores" is misleading, and the warp.

## The design trade

**A CPU core is optimised for latency. A GPU is optimised for throughput.** Everything follows from that.

```
 CPU core                          GPU SM
 ┌──────────────────────┐          ┌──────────────────────┐
 │ ┌──┐ huge control    │          │ ┌┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┐    │
 │ │AL│ branch predict  │          │ ├┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┤    │  many small ALUs
 │ │U │ OOO scheduler   │          │ ├┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┤    │
 │ └──┘ reorder buffer  │          │ └┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┘    │
 │ ┌──────────────────┐ │          │ ┌────┐ tiny control  │
 │ │   LARGE CACHE    │ │          │ │cache│              │
 │ └──────────────────┘ │          │ └────┘               │
 └──────────────────────┘          └──────────────────────┘
```

**A CPU spends most of its transistors on making *one* instruction stream fast** — branch prediction, out-of-order execution, speculation, deep caches. → [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]]

**A GPU spends them on arithmetic units** and hides latency a completely different way.

> **The CPU hides memory latency with caches and speculation. The GPU hides it by having so many threads that when one stalls, another is ready.**
>
> **That's the whole architectural idea.** A CPU tries not to wait. A GPU accepts waiting and makes sure there's always other work.

## The hierarchy

**NVIDIA terminology, with AMD/portable equivalents:**

| NVIDIA | AMD / OpenCL | What it is |
|---|---|---|
| **SM** (streaming multiprocessor) | CU (compute unit) | the real "core" — a scheduler plus many ALUs |
| **CUDA core** | stream processor | **an ALU lane, not a core** |
| **Warp** (32 threads) | wavefront (64) | **the actual scheduling unit** |
| Thread block | workgroup | threads that can cooperate |
| Grid | NDRange | all blocks in a launch |

> **"16,384 CUDA cores" is marketing.** Those are ALU lanes, not independent cores. **A better mental model: an H100 has 132 SMs**, each roughly analogous to a CPU core with a very wide vector unit. **132 cores × 128-wide SIMD** is closer to the truth than "16,896 cores".

**A block runs entirely on one SM** and can't migrate. Blocks are distributed across SMs by the hardware scheduler.

## The warp — the thing to understand

> **A warp is 32 threads executing in lockstep, sharing one instruction pointer.**

**They're not independent.** All 32 execute the same instruction each cycle, on different data. **SIMD hardware wearing a threaded programming model** — which is why NVIDIA calls it SIMT.

**Why it matters practically — divergence:**

```cuda
if (threadIdx.x % 2 == 0) {
    do_A();     // 16 threads active, 16 idle
} else {
    do_B();     // the other 16 active, first 16 idle
}
```

> **Both branches execute serially, with the inactive threads masked off.** The warp takes the time of A **plus** B. **Divergence within a warp costs you throughput directly**, and a 32-way divergent branch runs 32× slower than a uniform one.
>
> **Divergence *between* warps is free.** Warp 0 taking the if-branch and warp 1 taking the else-branch costs nothing. **So structure your data so that threads in the same warp take the same path** — sorting by branch condition is a real and effective optimisation.

**Independent thread scheduling** (Volta, 2017) lets threads within a warp make independent progress, which fixed a class of deadlocks in fine-grained synchronisation. **It does not remove the divergence cost** — execution is still serialised.

**Warp-level primitives** are the reward for understanding this: `__shfl_sync`, `__ballot_sync`, `__reduce_add_sync` exchange data between threads in a warp **through registers, with no memory traffic at all.** A warp-level reduction is dramatically faster than one through shared memory.

## Latency hiding and occupancy

**An SM holds many warps resident simultaneously** — up to 64 on recent hardware. **When one stalls on a memory access, the scheduler switches to another in a single cycle.**

**Context switching is free** because every resident warp has its own registers. **There's no state to save** — this is why the register file is enormous (256 KB per SM) and why register usage limits how many warps fit.

**Occupancy** = resident warps / maximum possible.

**What limits it:**

**Registers per thread.** The register file is fixed, so a kernel using 128 registers per thread fits half as many warps as one using 64.

**Shared memory per block.** Same argument.

**Block size.** Too small wastes scheduler slots; too large may not fit.

> **Higher occupancy is not automatically better**, and this is a genuinely common misconception. **Occupancy is a means of hiding latency, not a goal.** A kernel with high instruction-level parallelism and few memory stalls performs well at 25% occupancy; a memory-bound kernel may need 75%+.
>
> **Volkov's well-known result showed kernels running faster at *lower* occupancy** by using more registers per thread for better ILP. **Measure, don't maximise.**

## The memory hierarchy

| Level | Latency | Size | Scope |
|---|---|---|---|
| **Registers** | ~1 cycle | 256 KB/SM | thread |
| **Shared memory / L1** | ~30 cycles | 100–228 KB/SM | **block** |
| L2 | ~200 cycles | 40–50 MB | device |
| **Global (HBM)** | **~400–800 cycles** | 40–192 GB | device |
| Host (over PCIe) | ~10 µs | system RAM | — |

**Two things differ sharply from a CPU:**

**Shared memory is software-managed.** It's a scratchpad you explicitly load and use — **not a cache that works automatically.** Using it well is most of hand-optimised GPU programming. → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]]

**Global memory bandwidth is enormous and latency is terrible.** An H100 has ~3.35 TB/s of HBM3 bandwidth — **roughly 30× a high-end CPU** — but each access takes hundreds of cycles. **Bandwidth is the resource; latency is hidden by parallelism.**

## Tensor cores

**Specialised units doing a small matrix multiply-accumulate in one instruction.**

$$D = A\times B + C \qquad\text{for small tiles, e.g. } 16\times16$$

> **This is where modern ML performance actually comes from.** An H100 delivers ~67 TFLOPS of general FP32 and **~990 TFLOPS of FP16 through tensor cores** — roughly 15×.
>
> **Which is why mixed precision isn't a minor optimisation.** Training in FP16/BF16 with FP32 accumulation isn't about saving memory primarily — **it's about accessing hardware that's an order of magnitude faster.** → [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]]

**Precision formats and why they exist:**

| Format | Bits | Note |
|---|---|---|
| FP32 | 32 | the baseline |
| **TF32** | 19 | FP32 range, FP16-ish precision. **Automatic on Ampere+** |
| **BF16** | 16 | **FP32 exponent range**, fewer mantissa bits |
| FP16 | 16 | needs loss scaling to avoid gradient underflow |
| FP8, FP4 | 8, 4 | inference, and increasingly training |

**BF16 beat FP16 for training** because gradients span an enormous dynamic range. **Keeping FP32's exponent matters more than keeping its mantissa** — an information-theoretic point about where the bits should go. → [[foundations/computer-architecture/02-data-representation|Data Representation]]

**Tensor cores are only used if your shapes cooperate** — dimensions should be multiples of 8 or 16. **A matrix of size 4095 can be substantially slower than 4096**, which is a real and surprising effect worth knowing.

## The GPU vendors

**NVIDIA** — CUDA, and the software ecosystem is the actual moat. cuDNN, cuBLAS, NCCL, and every ML framework's first-class target.

**AMD** — ROCm and HIP (a near-source-compatible CUDA analogue). **MI300X is competitive on hardware**; the software has historically lagged and is improving.

**Apple** — unified memory means **no PCIe transfer at all**, which changes the calculus completely for medium-sized models. Metal Performance Shaders, and MLX.

**Intel** — Arc and Ponte Vecchio, oneAPI/SYCL.

**Google TPU** — a systolic array ASIC, not a GPU. **Excellent for large matmuls, less flexible**, and accessed through XLA/JAX.

**The portable options:** SYCL, OpenCL, Vulkan compute, and **Triton** (write in Python, compile to efficient GPU code) — which has become the standard way to write custom kernels for ML, and is what PyTorch 2's compiler emits.

## When a GPU is the wrong answer

**Being honest about this saves time:**

**Small problems.** Kernel launch is ~5–10 µs. **Below a few thousand elements, the CPU wins outright.**

**Branchy, irregular control flow.** Divergence destroys the model.

**Pointer chasing.** Linked lists, trees, graph traversal with irregular access — **no coalescing, and the memory system is built on the assumption of coalescing.**

**Latency-critical single requests.** GPUs give throughput, not low latency for one item.

**Anything transfer-dominated.** If arithmetic intensity is low, PCIe is your bottleneck and more FLOPS don't help. → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|The Roofline Model]]

> **The realistic expectation: 5–20× over a well-optimised multithreaded CPU implementation** for suitable workloads. **The "100× speedup" papers usually compare against single-threaded unoptimised CPU code** — a comparison that flatters the GPU by roughly the factor you'd get from using the CPU properly.

---

## Related
- [[foundations/gpu-and-parallel-computing/03-the-programming-model|The Programming Model]] — writing code for this
- [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]] — coalescing and shared memory
- [[foundations/computer-architecture/01-what-architecture-is|Computer Architecture]] — the CPU it's contrasted with
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
