# The Programming Model

**[Intermediate → Advanced]** — Kernels, grids and blocks. Writing code that runs on thousands of threads.

## The shape of a GPU program

```
1. Allocate device memory
2. Copy input   host → device
3. Launch kernel  (thousands of threads)
4. Copy output  device → host
5. Free
```

**Steps 2 and 4 are frequently the bottleneck**, which is the first thing to design around. → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]]

## Kernels

**A kernel is a function that runs once per thread.**

```cuda
__global__ void add(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];      // the bounds check matters
}

// launch: 256 threads per block, enough blocks to cover n
add<<<(n + 255) / 256, 256>>>(a, b, c, n);
```

**The whole model is in those five lines:**

**You write what *one* thread does**, not a loop. The loop is implicit in the launch.

**`blockIdx * blockDim + threadIdx`** is the universal index calculation. Every GPU kernel starts with some version of it.

**The bounds check is mandatory.** You launch a whole number of blocks, so **the last block usually has threads past the end of the data.** Omitting the check is an out-of-bounds write — and one of the most common GPU bugs.

**The hierarchy:**

```
 GRID
 ├── BLOCK (0,0)  ├── BLOCK (1,0)  ├── BLOCK (2,0)
 │   ├── warp 0   │                │
 │   ├── warp 1   │   threads here can:
 │   └── ...      │   - share shared memory
 │                │   - __syncthreads()
 │                │
 Blocks CANNOT synchronise with each other
```

> **The critical constraint: there is no global barrier within a kernel.** Blocks may run in any order, concurrently or sequentially, and **you cannot make block 5 wait for block 3.**
>
> **If you need a global barrier, end the kernel and launch another.** Kernel boundaries *are* the global sync points, and this shapes GPU algorithm design more than anything else — it's why multi-pass reductions exist. (Cooperative groups offer grid-wide sync with restrictions, but the rule holds for ordinary kernels.)

**Choosing block size:** **256 is a good default.** Must be a multiple of 32 (the warp size) or you waste lanes. Larger blocks share more shared memory; smaller blocks schedule more flexibly. **Use the occupancy calculator rather than guessing**, and then measure.

## Synchronisation

**`__syncthreads()`** — a barrier for all threads in a block.

```cuda
shared_data[threadIdx.x] = input[i];
__syncthreads();                       // everyone has written
float left = shared_data[threadIdx.x - 1];
```

> **Every thread in the block must reach it.** Calling `__syncthreads()` inside divergent control flow where some threads don't participate is **undefined behaviour** — and in practice a hang.
>
> ```cuda
> if (threadIdx.x < 10) { __syncthreads(); }   // ✗ deadlock
> ```

**Atomics** — `atomicAdd`, `atomicCAS`, etc. Work across the whole device.

**Cheap on modern hardware for shared memory, expensive when many threads hit the same global address** — they serialise. **The standard fix is a two-stage reduction:** reduce within each block using shared memory, then one atomic per block instead of one per thread.

**`atomicAdd` on floats is non-deterministic** — the summation order varies between runs, and floating-point addition isn't associative. **So your results won't be bit-reproducible.** Usually fine; occasionally a real problem for debugging or regulatory reproducibility. → [[foundations/numerical-methods/02-floating-point-and-error|Non-associativity]]

## Streams and asynchrony

**By default, kernel launches are asynchronous** — the CPU returns immediately and the GPU queues the work.

> **This makes naive timing wrong:**
> ```cuda
> start_timer();
> kernel<<<...>>>();
> stop_timer();          // measures the launch, not the kernel
> ```
> **You must `cudaDeviceSynchronize()` before stopping the clock**, or use CUDA events. **Beginner benchmarks reporting microsecond kernel times are almost always this bug.**

**Streams** are independent queues. Work in different streams can overlap:

```
 Stream 1:  [copy H→D]  [kernel]  [copy D→H]
 Stream 2:              [copy H→D]  [kernel]  [copy D→H]
 Stream 3:                          [copy H→D]  [kernel]
```

**Overlapping transfer with computation can nearly double throughput** on transfer-heavy workloads — while one chunk computes, the next transfers.

**Requires pinned (page-locked) host memory** for async copies. `cudaMallocHost`. **Pageable memory forces a synchronous staged copy**, silently.

**CUDA graphs** capture a sequence of operations and replay it with a single launch. **Cuts launch overhead substantially for workloads with many small kernels** — which describes inference on small models, and it's why frameworks adopted them.

## The frameworks

**Most people should never write a raw kernel.** The layers, from highest:

**PyTorch / JAX / TensorFlow** — write array operations, get GPU execution. **`torch.compile` and JAX's `jit` fuse operations automatically**, which removes most of the reason to hand-write kernels.

**CuPy** — a NumPy-compatible API on the GPU. **Often a near drop-in replacement**, which makes it the cheapest thing to try.

**Numba** — `@cuda.jit` compiles Python to CUDA. Good for custom kernels without leaving Python.

**Triton** — write in a Python-like DSL, get near-hand-tuned performance. **Handles memory coalescing and shared memory for you.** This is what PyTorch 2's inductor backend emits, and **it's now the standard way to write custom ML kernels** — FlashAttention has a well-known Triton implementation.

**CUDA C++ / HIP** — full control, and what you drop to when you genuinely need it.

**Portable:** SYCL, OpenCL, Vulkan compute, WebGPU.

> **The realistic recommendation: use the framework, profile, and only write a kernel when the profiler shows a specific fusion or memory pattern the compiler missed.** That's a real situation — it's why FlashAttention exists — but it's not the common one.

## The library layer

**Never write these yourself:**

| Library | For |
|---|---|
| **cuBLAS** | dense linear algebra. **Hand-tuned per architecture** |
| cuDNN | convolutions, pooling, normalisation |
| **CUTLASS** | templated GEMM you can compose into |
| Thrust | STL-like algorithms — sort, scan, reduce |
| cuSPARSE / cuSOLVER | sparse and dense solvers |
| **NCCL** | **multi-GPU collectives** — all-reduce, broadcast |
| cuRAND | random numbers |

**A hand-written matrix multiply typically reaches 10–30% of cuBLAS.** Closing that gap means tiling, double buffering, tensor core intrinsics, and per-architecture tuning. → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]]

**NCCL matters for distributed training** — it implements ring and tree all-reduce over NVLink and InfiniBand, and it's what makes multi-GPU gradient synchronisation efficient. → [[foundations/gpu-and-parallel-computing/07-distributed-and-multi-gpu|Distributed and Multi-GPU]]

## Debugging

**Harder than CPU debugging, and the tooling is decent if you use it.**

**`compute-sanitizer`** (formerly `cuda-memcheck`) — **the equivalent of Valgrind.** Catches out-of-bounds access, race conditions on shared memory, and misaligned access. **Run it; it finds real bugs.**

**Check every API return code.** Errors are asynchronous and surface later at an unrelated call:

```cuda
#define CHECK(x) do { cudaError_t e = (x); \
  if (e != cudaSuccess) { fprintf(stderr, "%s:%d %s\n", \
    __FILE__, __LINE__, cudaGetErrorString(e)); exit(1);} } while(0)
```

**Without this, a bug in kernel A appears as a failure in an unrelated `cudaMemcpy` three calls later.**

**`printf` works inside kernels** — buffered, flushed at synchronisation. Crude and effective for small cases.

**`cuda-gdb`** and Nsight for real debugging; **Nsight Compute** for kernel-level profiling and **Nsight Systems** for the timeline view.

**The common bugs:**

**Missing bounds check** — the last block runs off the end.

**Race on shared memory** — a missing `__syncthreads()`. **Works most of the time**, which is the worst kind of bug.

**Divergent `__syncthreads()`** — hangs.

**Forgetting to copy results back**, and reading stale host memory.

**Silent kernel launch failure** — too many registers, too much shared memory. **Check the return code.**

**Integer overflow in the index** — `blockIdx.x * blockDim.x` overflows `int` for very large launches. Use `size_t`.

## Practical notes

**Start with a working CPU version** and validate the GPU output against it numerically. **Expect small floating-point differences** from different summation orders — compare with a tolerance, not equality.

**Profile before optimising.** Nsight Compute reports achieved occupancy, memory throughput, and whether you're compute- or bandwidth-bound. **That last number determines everything you do next.** → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|The Roofline Model]]

**Minimise transfers before optimising kernels.** Keep data resident on the device across operations. **A fused pipeline that never returns to host memory beats faster individual kernels.**

**Use `float` unless you need `double`.** Consumer GPUs have FP64 at 1/32 or 1/64 of FP32 throughput — **a 4090 is dramatically slower in double precision.** Datacentre cards (A100, H100) are 1/2, which is why they cost what they do for scientific work.

**Watch for implicit synchronisation.** `cudaMalloc`, `cudaFree` and default-stream operations synchronise, silently destroying overlap. **Allocate once, reuse buffers, use a memory pool.**

---

## Related
- [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]] — the algorithms to build with
- [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]] — where the performance is
- [[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]] — the hardware this maps to
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
