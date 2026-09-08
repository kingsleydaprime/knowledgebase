# Memory and Data Movement

**[Advanced]** — Coalescing, shared memory, bank conflicts, and the PCIe transfer that ruins most first GPU ports.

## The central fact

> **GPUs have enormous bandwidth and terrible latency. Almost every GPU performance problem is a memory problem.**

**An H100:** ~990 TFLOPS (FP16 tensor) against ~3.35 TB/s of HBM3.

$$\frac{990\times10^{12}\text{ FLOP/s}}{3.35\times10^{12}\text{ byte/s}} \approx 295 \text{ FLOP per byte}$$

**To keep the arithmetic units busy you need ~300 floating-point operations for every byte you load.** Most code does nothing close.

**Which means most kernels are bandwidth-bound**, and optimising arithmetic in a bandwidth-bound kernel achieves nothing. → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|The Roofline Model]]

## Coalescing

**The single most important GPU memory concept.**

**The memory system serves a warp's 32 accesses in *transactions* of 32, 64 or 128 bytes.**

**Coalesced — consecutive threads read consecutive addresses:**

```
 thread:   0    1    2    3   ...  31
 address: 0x00 0x04 0x08 0x0C ... 0x7C
          └────────── one 128-byte transaction ──────────┘
```

**Uncoalesced — strided or scattered:**

```
 thread:   0      1      2     ...
 address: 0x00   0x80   0x100  ...
          └─ 32 separate transactions ─┘
```

> **Up to 32× more memory traffic for the same data.** The hardware fetches a full transaction regardless, so a strided access wastes most of every one.
>
> **This single effect explains most of the gap between a naive kernel and a good one.**

**The practical rule: thread index should map to the *fastest-varying* dimension.**

```cuda
// ✓ coalesced — consecutive threads → consecutive columns
int col = blockIdx.x * blockDim.x + threadIdx.x;
value = matrix[row * width + col];

// ✗ strided — consecutive threads jump by `width`
int row = blockIdx.x * blockDim.x + threadIdx.x;
value = matrix[row * width + col];
```

**Which is why row-major vs column-major matters so much more on a GPU than a CPU** — a CPU's cache and prefetcher tolerate stride; a GPU's memory system doesn't.

**And it's why Structure-of-Arrays beats Array-of-Structures on GPUs, almost always:**

```
 AoS: [x0 y0 z0][x1 y1 z1][x2 y2 z2]   reading all x = stride 3 ✗
 SoA: [x0 x1 x2][y0 y1 y2][z0 z1 z2]   reading all x = contiguous ✓
```

→ [[foundations/computer-architecture/08-the-memory-hierarchy|AoS vs SoA]]

**Alignment matters too** — a 128-byte transaction starting mid-boundary spans two transactions. `cudaMalloc` returns 256-byte-aligned memory; `cudaMallocPitch` pads 2D allocations so each row starts aligned.

## Shared memory

**A software-managed scratchpad per SM.** ~100–228 KB, roughly L1 latency, **and you control it explicitly.**

**The pattern it enables — load once, use many times:**

```cuda
__shared__ float tile[TILE][TILE];

tile[ty][tx] = global_data[...];   // cooperative load
__syncthreads();                    // everyone has written
// now every thread can read any element cheaply
```

**This is what makes tiled matrix multiply and stencil computations fast.** → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]]

### Bank conflicts

**Shared memory is divided into 32 banks, 4 bytes wide, interleaved.**

**Different banks → all 32 accesses in one cycle. Same bank, different addresses → serialised.**

```
 address:  0    1    2   ...  31   32   33
 bank:     0    1    2   ...  31    0    1     (address % 32)
```

**The classic conflict — a column of a 32-wide array:**

```cuda
__shared__ float tile[32][32];
x = tile[threadIdx.x][0];    // all threads hit bank 0 → 32× slower
```

**The standard fix is padding:**

```cuda
__shared__ float tile[32][33];   // ← one extra column
```

> **Adding a column shifts each row by one bank, so a column access spreads across all 32.** **One character, up to 32× on that access** — and it's the classic GPU micro-optimisation.
>
> **Broadcast is free:** all threads reading the *same* address is a single broadcast, not a conflict. Only *different* addresses in the *same* bank serialise.

## The transfer problem

**The mistake that makes first GPU ports slower than the CPU version.**

| Path | Bandwidth |
|---|---|
| GPU ↔ its own HBM | **~3,000 GB/s** |
| **PCIe 4.0 x16** | **~25 GB/s** |
| PCIe 5.0 x16 | ~50 GB/s |
| **NVLink** (GPU↔GPU) | 600–900 GB/s |
| **Unified memory (Apple, Grace-Hopper)** | **no transfer at all** |

> **PCIe is ~100× slower than local GPU memory.** A kernel taking 50 µs, fed by 200 µs of transfer, is a net loss.
>
> **The rule: keep data resident on the device.** Transfer once, run many kernels, transfer results back. **A pipeline of ten fused GPU operations with no host round trips beats five faster kernels that each return to the CPU.**

**Practical techniques:**

**Pinned (page-locked) host memory** — `cudaMallocHost`. **Required for true async transfer**, and roughly 2× faster than pageable. Pageable memory forces a staged copy through a driver buffer, synchronously.

**Overlap with streams** — copy chunk $n+1$ while computing on chunk $n$. **Can nearly double throughput** on transfer-heavy work. → [[foundations/gpu-and-parallel-computing/03-the-programming-model|Streams]]

**Unified memory** (`cudaMallocManaged`) — one pointer, the driver migrates pages on demand. **Convenient, and it can thrash** if the access pattern ping-pongs. Use `cudaMemPrefetchAsync` to hint.

**Apple Silicon and Grace-Hopper have genuinely unified memory** — the CPU and GPU share physical RAM. **No transfer step exists**, which changes the design calculus entirely and is a real advantage for medium-sized models.

## Memory types

| Type | Scope | Notes |
|---|---|---|
| **Registers** | thread | fastest; spills to local memory if you use too many |
| **Shared** | block | scratchpad; watch bank conflicts |
| **Global** | device | the big one; **coalesce** |
| **Constant** | device, read-only | 64 KB, **broadcast-optimised** — great for parameters all threads read |
| **Texture** | device, read-only | cached for **2D spatial locality**, free interpolation |
| **Local** | thread | **misleadingly named — it's global memory.** Register spills land here |

**"Local memory" is the trap.** It sounds fast and is global memory with a thread-private view. **Register spilling silently moves your hot variables to DRAM** — check with `-Xptxas -v` and reduce register pressure if the compiler reports spills.

**Texture memory is underused outside graphics.** For read-only data with 2D locality — image processing, stencils on 2D grids — the texture cache is optimised for exactly that access pattern, and `__ldg()` / `const __restrict__` gets you the read-only path without the texture API.

## Diagnosing

**Nsight Compute tells you directly:**

**Memory throughput vs peak** — are you near the bandwidth limit?

**Global load/store efficiency** — **the coalescing metric.** Below ~50% means you're wasting most of every transaction, and fixing the access pattern is the highest-value change available.

**Shared memory bank conflicts** — the count per request.

**Achieved occupancy** — is there enough parallelism to hide latency?

**Register spills** — reported by `-Xptxas -v` at compile time.

**The decision tree:**

```
Low memory throughput + low efficiency  → fix COALESCING
High throughput, near peak              → bandwidth-bound; reduce traffic
                                          (tiling, fusion, smaller types)
Low throughput, low occupancy           → not enough parallelism
Low throughput, high occupancy          → latency-bound; check dependencies
Compute-bound near peak FLOPS           → you're done
```

## Practical notes

**Coalesce first.** It's usually the biggest single win and often a one-line index change.

**Use SoA layout** for GPU data.

**Tile into shared memory** whenever data is reused within a block.

**Pad shared arrays** to avoid bank conflicts — the `[32][33]` trick.

**Minimise host↔device transfer** above all else. Keep data resident.

**Use pinned memory and streams** when transfers are unavoidable.

**Prefer smaller types where precision allows.** FP16/BF16 halves your bandwidth requirement, **which for a bandwidth-bound kernel is a straight 2× speedup** — independently of tensor cores.

**Fuse kernels.** Every avoided round trip to global memory is bandwidth saved. → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Kernel Fusion]]

**Check for register spills** before blaming the algorithm.

---

## Related
- [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Performance and the Roofline]] — which bound you're against
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — the CPU analogue
- [[foundations/gpu-and-parallel-computing/04-parallel-patterns|Parallel Patterns]] — tiling and fusion
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
