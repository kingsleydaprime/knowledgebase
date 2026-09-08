# Parallel Patterns

**[Advanced]** — The handful of primitives every parallel algorithm is built from, and why scan is the surprising one.

## Map

**Apply a function to every element independently.**

$$y_i = f(x_i)$$

**Perfectly parallel, no communication, linear speedup.** The easy case, and it's what element-wise operations in NumPy or PyTorch are.

**The only real concern is memory access order** — read and write contiguously so accesses coalesce. → [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Coalescing]]

## Reduce

**Combine all elements into one with an associative operator** — sum, max, min, product, logical and.

**Serially it's $O(n)$ and inherently sequential. In parallel it's a tree:**

```
 [a][b][c][d][e][f][g][h]
   \ /    \ /    \ /    \ /
   [ab]  [cd]  [ef]  [gh]        log n levels
     \    /      \    /
      [abcd]     [efgh]
         \        /
          [abcdefgh]
```

**$O(\log n)$ depth with $n/2$ processors.**

> **Associativity is what makes this legal.** $(a+b)+c = a+(b+c)$, so the tree can regroup freely.
>
> **Floating-point addition is not associative**, so **a parallel reduction gives a different answer than a serial one** — and a different answer depending on how many threads you use. **This is why ML training isn't bit-reproducible across GPU counts**, and it isn't a bug. → [[foundations/numerical-methods/02-floating-point-and-error|Summation]]

**The GPU implementation, and the standard escalation:**

1. **Each thread loads several elements** and reduces them serially (better than one element per thread — fewer idle threads at the top of the tree)
2. **Tree-reduce in shared memory** within the block, `__syncthreads()` between levels
3. **Warp-level primitives for the last 32** — `__shfl_down_sync` needs no shared memory or barriers at all
4. **One `atomicAdd` per block** to combine, or a second kernel

**Step 3 is the one people miss** and it's a meaningful win — the final warp needs no synchronisation because it's already in lockstep.

## Scan (prefix sum)

**The pattern that looks sequential and isn't.**

$$y_i = x_0 \oplus x_1 \oplus \cdots \oplus x_i$$

```
 input:      [3, 1, 7, 0, 4, 1, 6, 3]
 inclusive:  [3, 4, 11, 11, 15, 16, 22, 25]
 exclusive:  [0, 3, 4, 11, 11, 15, 16, 22]
```

> **Every element depends on all previous ones — so it looks fundamentally sequential.** It isn't. **Scan parallelises in $O(\log n)$ depth**, and that result is one of the more surprising things in parallel algorithms.

**Two algorithms:**

**Hillis–Steele** — $\log n$ steps, each adding an element $2^k$ back. **Simple, $O(n\log n)$ total work** — not work-efficient, but low depth and fine within a warp.

**Blelloch** — an up-sweep (reduce) then a down-sweep. **$O(n)$ work, $2\log n$ depth.** Work-efficient, and what libraries use.

**Why scan matters so much:**

**Stream compaction** — removing elements that fail a predicate. **Scan the 0/1 flags to get output indices**, then scatter. This is *the* way to filter on a GPU, and it's not obvious until you've seen it.

```
 data:   [a, b, c, d, e]
 keep:   [1, 0, 1, 1, 0]
 scan:   [0, 1, 1, 2, 3]   ← output index for each kept element
 result: [a, c, d]
```

**Radix sort** — each pass is a scan over digit counts.

**Sparse matrix operations** — computing row offsets in CSR.

**Allocation** — many threads each needing a variable amount of space: scan the sizes to get offsets.

**Resource allocation, histogram offsets, run-length encoding, quicksort partitioning.**

> **If you find yourself thinking "each thread needs to know how many threads before it did X", the answer is a scan.** It's the pattern that unlocks the most non-obvious GPU algorithms.

## Stencil

**Each output depends on a local neighbourhood.**

$$y_i = f(x_{i-1}, x_i, x_{i+1})$$

**Convolutions, image filters, finite-difference PDE solvers, cellular automata, blur kernels.** → [[foundations/numerical-methods/09-partial-differential-equations|Finite Differences]]

**The optimisation that matters: shared memory tiling.**

**Naive:** each thread reads all its neighbours from global memory. **With a 3×3 stencil, every element is read 9 times.**

**Tiled:** the block cooperatively loads a tile plus a halo into shared memory, then each thread reads from there. **Each element is read from global memory once.**

**A 9× reduction in global traffic**, and for a bandwidth-bound stencil that's close to a 9× speedup.

**The halo is the fiddly part** — a $16\times16$ tile with a radius-1 stencil needs an $18\times18$ load, so the loading pattern doesn't match the compute pattern and some threads load more than one element.

## Gather and scatter

**Gather:** `y[i] = x[idx[i]]` — indirect *read*.

**Scatter:** `y[idx[i]] = x[i]` — indirect *write*.

**Gather is safe.** Scatter has a problem: **if two threads write to the same index, the result is undefined** unless you use atomics.

> **Prefer gather to scatter.** When you have a choice — and you often do, by inverting the index mapping — **gather avoids both the race and the atomic cost.** This is a standard transformation in GPU algorithm design.

**Both break coalescing** because the accesses are irregular. **Sorting the indices first can be a net win** despite the sort cost, because it restores locality.

## Sort

**Radix sort dominates on GPUs.** $O(n)$ for fixed-width keys, and every pass is a scan — so it's built from the primitives above.

**Bitonic sort** is a sorting *network* — a fixed pattern of compare-exchange operations, data-independent, so **no divergence and no dynamic allocation.** $O(n\log^2 n)$ comparisons, worse asymptotically, but the regularity makes it competitive for small arrays and fully in-shared-memory sorts.

**Merge sort** parallelises reasonably; **quicksort is awkward** because the partition sizes are data-dependent and cause load imbalance.

**Use `cub::DeviceRadixSort` or `thrust::sort`.** They're extremely well optimised and you will not beat them.

## Histogram

**Deceptively hard**, because it's a scatter with collisions.

**Naive:** every thread does `atomicAdd(&hist[bin], 1)` on global memory. **Correct, and catastrophically slow when the data is skewed** — all threads hammering one bin serialises completely.

**The standard fix — privatisation:**

1. **Each block builds a private histogram in shared memory** (atomics there are much cheaper)
2. **One atomic per bin per block** to merge into the global histogram

**Often 10× faster**, and it generalises: **privatise the contended resource, then combine.** That's the same principle as per-thread accumulators on a CPU. → [[foundations/computer-architecture/11-multicore-and-memory-models|Sharding]]

**Sub-histograms per warp** help further when bin counts are small enough to fit.

## Matrix multiply

**The pattern that matters most in practice**, because it's the bulk of every neural network.

**Naive: each thread computes one output element** by reading a full row and column. **$O(n^3)$ work with $O(n^3)$ global memory reads** — hopelessly bandwidth-bound.

**Tiled:** load a tile of A and a tile of B into shared memory, compute partial products, advance.

```
 for each tile k:
     load A[i, k-tile] and B[k-tile, j] into shared memory
     __syncthreads()
     accumulate the partial product
     __syncthreads()
```

**Each element is loaded $n/T$ times instead of $n$** — arithmetic intensity rises by the tile size $T$, and that's what moves the kernel from bandwidth-bound to compute-bound. → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|The Roofline Model]]

**Production implementations add:** register-level tiling (each thread computes a small tile, not one element), double buffering to overlap loads with compute, tensor core intrinsics, and per-architecture tuning.

> **This is why hand-written GEMM reaches maybe 30% of cuBLAS.** The gap is real engineering, not magic — and it's why **you call the library.** → [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/04-matrix-multiplication|Matrix Multiplication]]

## Kernel fusion

**Not a pattern so much as the most important optimisation.**

```
 unfused:  y = relu(x)      → write to memory
           z = y * w        → read, write
           out = z + b      → read, write        3 round trips

 fused:    out = relu(x) * w + b                 1 round trip
```

> **Element-wise operations are almost always bandwidth-bound**, so fusing them is nearly free performance. **Three separate kernels each read and write global memory; one fused kernel does it once.**
>
> **This is the main thing `torch.compile`, XLA and Triton do**, and it's why they give large speedups on models with many small operations without changing the maths at all.

**FlashAttention is the celebrated example:** it fuses the attention computation so the $N\times N$ attention matrix **is never written to global memory** — it's tiled through shared memory instead. **Same output, dramatically less memory traffic, and it made long contexts practical.**

## Practical notes

**Use the library primitives.** CUB (device-wide), Thrust (STL-like), and the framework's built-ins. **`cub::DeviceScan`, `cub::DeviceReduce`, `thrust::sort` are excellent.**

**Compose from patterns rather than inventing.** Most parallel algorithms are map/reduce/scan in some arrangement, and recognising which is most of the design.

**Check associativity before parallelising a reduction.** Subtraction and division aren't associative; floating-point addition is only approximately.

**Privatise contended writes.** Per-block, then combine.

**Prefer gather over scatter.**

**Fuse aggressively**, or use a compiler that does.

**Measure arithmetic intensity.** It tells you whether tiling will help or whether you're already compute-bound. → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Roofline]]

---

## Related
- [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|Memory and Data Movement]] — why tiling works
- [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Performance and the Roofline]] — knowing which bound you're against
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — the sequential versions
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel map]]
