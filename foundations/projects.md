# Foundations — Projects — Projects

*The vault's largest section by far (~312,000 words) and its most theoretical. **These are the cheapest reps here** — most are a single script, an afternoon, and a concept that stops being abstract.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## Graphics & GPU — the most visible reps

- 🟢 ⭐ **[Ray Tracing in One Weekend](https://raytracing.github.io)** — genuinely a weekend, no API, no build system, and you finish with a real rendered image. **The single best entry point in graphics.**
- 🟢 **Break coalescing deliberately** — write a CUDA kernel, transpose the index calculation, measure. **A 10–30× slowdown from one swapped index** makes [[foundations/gpu-and-parallel-computing/05-memory-and-data-movement|note 05]] permanent.
- 🟡 **Write a software rasteriser** — edge functions, z-buffer, perspective-correct interpolation. No GPU. **Then deliberately skip the perspective correction and watch textures warp like a PlayStation 1** → [[foundations/computer-graphics/03-rasterisation|03]].
- 🟡 **Reduce your render resolution.** If the frame rate doesn't change, you're CPU-bound. **A ten-second test that saves days** → [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|06]].
- 🟡 ⭐ **Matrix multiply on a GPU three ways** — naive, tiled with shared memory, then cuBLAS. Measure each. **Seeing how far short hand-written code falls is the lesson** → [[foundations/gpu-and-parallel-computing/04-parallel-patterns|04]].
- 🔴 **Profile a real training loop** with `torch.profiler` and find the data-loading gaps. **They're almost always there**, and the GPU is idle while you optimise kernels → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|06]].

**If you do one:** Ray Tracing in One Weekend. It's the rare project that's short, self-contained, and produces something you want to show people.


## Numerical methods & information theory

- 🟢 ⭐ **Plot the finite-difference error U-curve** — compute $f'(x)$ at $h$ from $10^{-1}$ to $10^{-16}$, plot the error. **The V shape is the whole of [[foundations/numerical-methods/01-why-numerical-methods|note 01]] in one picture**, and it takes five minutes.
- 🟢 **Break the quadratic formula** — solve $x^2 + 10^8x + 1 = 0$ naively and with the stable form. **Watch half your digits vanish** → [[foundations/numerical-methods/02-floating-point-and-error|02]].
- 🟢 **Measure the entropy of a real file**, then compare against what `gzip` and `zstd` achieve. **The gap is the redundancy your model isn't capturing** → [[foundations/information-theory/01-what-information-is|01]].
- 🟡 **Reproduce Runge's phenomenon** — interpolate $1/(1+25x^2)$ at 5, 10, 20 equally-spaced points. **More points makes it worse.** Then use Chebyshev nodes and watch it converge → [[foundations/numerical-methods/06-interpolation-and-approximation|06]].
- 🟡 **Hit a stiffness wall** — integrate a stiff ODE with `RK45` and with `BDF`. **Compare step counts; it's usually orders of magnitude** → [[foundations/numerical-methods/08-ordinary-differential-equations|08]].
- 🟡 **Fit forward vs reverse KL to a bimodal distribution.** One covers both modes, one picks a single mode. **Twenty lines, and [[foundations/information-theory/04-cross-entropy-and-kl-divergence|note 04]]'s central point becomes visual.**
- 🔴 **Do a convergence study on anything** — halve the step, confirm the error falls at the promised rate. **The single most useful habit in numerical work.**

**If you do one:** the finite-difference U-curve. Five minutes, and it permanently changes how you think about "just use a smaller step."


## CS theory — the cheapest reps in this vault

- 🟢 **Run `perf stat` on something you wrote** — look at the IPC, then work out *why* it's that number. Twenty minutes, and it turns [[foundations/computer-architecture/12-performance|the whole performance note]] from reading into a method you've used.
- 🟢 **Reproduce the sorted-array branch experiment** — the same loop over sorted vs shuffled data, several-fold difference, identical instruction count. **Seeing it yourself is different from reading it** → [[foundations/computer-architecture/06-pipelining|pipelining]].
- 🟢 **Demonstrate false sharing** — two threads incrementing adjacent array elements, then padded to 64 bytes. **Watch a parallel program get faster by adding memory** → [[foundations/computer-architecture/09-caches-in-depth|caches]].
- 🟡 ⭐ **Matrix multiply, three ways** — naive, loop-interchanged, blocked. Measure each. **A 10× spread from reordering identical arithmetic** is the single best demonstration of [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]].
- 🟡 **Prove three things on paper** — $\{a^nb^n\}$ isn't regular, the halting problem is undecidable, one NP-completeness reduction. **Reading a proof and producing one are different skills** → [[foundations/discrete-math/03-proof-techniques|proof techniques]].
- 🟡 ⭐ **Build a regex engine** — Thompson's construction → subset construction → simulate the DFA. A few hundred lines, and it makes [[foundations/theory-of-computation/02-finite-automata|the regex/NFA/DFA equivalence]] concrete. **This is the missing ninth guide in [[build-your-own-shit/README|build-your-own-shit]].**
- 🔴 **Write a SAT solver** — DPLL is short; adding clause learning makes it genuinely useful. The best way to understand why [[foundations/theory-of-computation/07-complexity-classes|NP-completeness]] is survivable in practice.
- 🔴 **Lean's Natural Number Game, then a real proof in Lean** — a proof assistant will not let you skip a step, which is exactly the discipline reading proofs doesn't build.

**If you do one:** the matrix-multiply trio. It takes an hour, produces a number you can't argue with, and permanently changes how you think about data layout.


## Python & data tools

- 🟢 **pandas cleaning gauntlet** — take a deliberately messy CSV and clean it end-to-end ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]): missing data, dtypes, duplicates, inconsistent categories — no loops, all vectorized.
- 🟢 **NumPy, no loops** — reimplement a handful of numeric routines (normalization, moving average, a distance matrix, one-hot encoding) as pure vectorized [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — the "if you're looping you're doing it wrong" drill.
- 🟢 **10 questions, one dataset** — answer ten analytical questions about a dataset using only `groupby`/`value_counts`/boolean selection ([[ai-ml/00-foundations/04-python-and-data-tools/03-pandas|pandas]]) and [[ai-ml/00-foundations/04-python-and-data-tools/04-visualization-basics|seaborn]].


## Systems — where the build guides live

The deepest foundations reps are all written up as full guides in [[build-your-own-shit/README|build-your-own-shit/]]:

| | Guide | Makes concrete |
|---|---|---|
| 🟠 | [[build-your-own-shit/07-your-own-shell\|Shell]] | [[foundations/os/README\|OS]] — `fork`/`exec`, fds, pipes |
| 🟠 | [[build-your-own-shit/08-your-own-container\|Container]] | [[foundations/os/11-isolation-and-containers\|namespaces and cgroups]] |
| 🟠 | [[build-your-own-shit/01-http-server\|HTTP server]] | [[foundations/networking/README\|networking]] |
| 🔴 | [[build-your-own-shit/09-your-own-regex-engine\|Regex engine]] | [[foundations/theory-of-computation/README\|automata]] — **theory to code, one evening** |
| 🔴 | [[build-your-own-shit/04-your-own-language\|Language]] | [[foundations/compilers/README\|compilers]] — the deepest single lesson |
| 🔴 | [[build-your-own-shit/11-your-own-memory-allocator\|Memory allocator]] | [[foundations/os/05-memory-allocation\|memory]] |
| 🔴 | [[build-your-own-shit/05-your-own-os\|Operating system]] | all of [[foundations/os/README\|OS]] — weeks, not a weekend |

## Practice exercises already written

Several foundations courses ship exercises with solutions. **Do these before inventing your own:** [[foundations/discrete-math/09-practice-exercises|discrete maths]] · [[foundations/theory-of-computation/09-practice-exercises|theory of computation]] · [[foundations/computer-architecture/13-practice-exercises|computer architecture]] · [[foundations/numerical-methods/11-practice-exercises|numerical methods]] · [[foundations/information-theory/08-practice-exercises|information theory]] · [[foundations/gpu-and-parallel-computing/08-practice-exercises|GPU & parallel]] · [[foundations/computer-graphics/10-practice-exercises|graphics]] · [[foundations/programming-language-theory/08-practice-exercises|PL theory]] · [[foundations/programming-fundamentals/16-practice-exercises|programming fundamentals]]


## If you only do one

**The regex engine.** One evening, ~200 lines, and it converts the most abstract folder in the vault ([[foundations/theory-of-computation/README|theory of computation]]) into running code — plus yours beats Python's `re` on adversarial input, which is a genuinely satisfying result.


## Related
- [[foundations/README|the foundations index]] — all fifteen courses

- [[foundations/dsa/README|DSA]] · [[foundations/os/README|OS]] · [[foundations/compilers/README|compilers]] · [[foundations/networking/README|networking]]
- [[build-your-own-shit/README|build-your-own-shit]] — the systems reps
- [[project-ideas|Project Ideas]] — the vault-wide index
