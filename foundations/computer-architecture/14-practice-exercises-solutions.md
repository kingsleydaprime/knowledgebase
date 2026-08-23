# Practice Exercises — Solutions

> **[Intermediate → Advanced]** · Worked answers to [[foundations/computer-architecture/13-practice-exercises|note 13]].

**Measured on an Intel i7-8650U** (4 cores / 8 threads, L1d 32 KB per core, L2 256 KB per core, L3 8 MB shared), GCC, August 2026. **Your absolute numbers will differ; the ratios and the shape should not.**

Two of these classic experiments **do not reproduce at `-O2`**, and that is recorded here rather than hidden — it's the most useful thing in the file.

---

## Part A — Representation and instructions

### 1. Floating-point edges

`0.1 + 0.2` → `0.30000000000000004`.

The integer boundary is **2⁵³ = 9,007,199,254,740,992**. Beyond it, `float(n) == float(n+1)`, and `(2**53) + 1` as a double gives back 2⁵³.

**Why exactly there:** a double has 52 stored mantissa bits plus one implicit leading bit = 53 bits of precision. Integers up to 2⁵³ are exactly representable; above that the gap between representable values is ≥ 2, so odd numbers vanish.

53 bits ≈ **15–17 significant decimal digits**. This is why JavaScript (all numbers are doubles) cannot represent large 64-bit database IDs, and why APIs return them as strings → [[foundations/computer-architecture/02-data-representation|note 02]].

### 2. Overflow three ways

- **Signed overflow is undefined behaviour.** At `-O0` it usually wraps; at `-O2` the compiler may assume it cannot happen and delete your check. This is a real class of security bug
- **Unsigned overflow is defined** — it wraps modulo 2ⁿ. Guaranteed by the standard
- **Shifting by ≥ the width is UB**, and genuinely varies: x86 masks the shift count to 5 or 6 bits, so `x << 32` on a 32-bit int may return `x`, not 0

`-fsanitize=undefined` reports the signed overflow and the shift at runtime with file and line. **Run it on any C you write** → [[languages/04-c/README|C]].

### 3. What the compiler emits

At `-O0` every variable round-trips to the stack. At `-O1`+ they live in registers. At `-O2` a loop summing 1..100 with a constant bound becomes a single `mov` of `5050` — the loop is gone entirely.

The general lesson, and it is the one that matters for the rest of this file: **the assembly is not your source translated literally.** Anything you measure is measuring the *compiler's* program.

---

## Part B — The memory hierarchy

### 4. Measure your own cache sizes

The plot shows flat plateaus with sharp steps at the working-set boundaries: ~1 ns/access inside L1, ~4 ns in L2, ~15 ns in L3, ~80–100 ns in DRAM.

**The steps land at your cache sizes** — that's the whole exercise. You've derived the hierarchy from timing alone.

Two things that will spoil it if you're not careful: the hardware prefetcher hides latency on sequential access (use a **randomised pointer chase** to defeat it), and the compiler may hoist your loop (make the result feed into something observable).

### 5. Stride

Per-element cost rises from stride 1 to stride 16 and then flattens.

**Why:** a cache line is 64 bytes = 16 four-byte ints. At stride 1 you use all 16 ints per line fetched. At stride 16 you use **one int per line** — 16× the memory traffic for the same element count. Beyond that you're already wasting the whole line, so it can't get worse per element touched.

**This is why [[game-development/02-engines-and-the-game-loop|ECS]] and data-oriented design exist**, and why an array of structs can be 16× slower than a struct of arrays for a scan that touches one field.

### 6. Matrix multiply — and why size changes the answer

Measured:

| | **N = 512** | **N = 1024** |
|---|---|---|
| `ijk` naive | 0.211 s | **5.059 s** |
| `ikj` interchanged | 0.094 s | **1.041 s** |
| blocked (64) | 0.089 s | **0.775 s** |
| **speedup** | 2.4× | **6.5×** |

Same arithmetic. Same result. **6.5× at N=1024.**

`ijk` walks `B` **down a column** — stride *N*×8 bytes, so every access is a new cache line and nearly every one misses. `ikj` walks both `B` and `C` along rows, so each fetched line is fully consumed.

**And the reason the effect is only 2.4× at N=512 is the point of running both:** at N=512, `B` is 512×512×8 = 2 MB and largely fits in the 8 MB L3, so column-walking is punished mildly. At N=1024 it's 8 MB and doesn't. **The penalty appears when the working set exceeds the cache** — which is exactly why benchmarks on small inputs mislead → [[foundations/computer-architecture/09-caches-in-depth|note 09]].

Blocking adds little over `ikj` here because `-O2` already vectorises the inner loop well; on a larger matrix or with a bigger tile the gap widens.

---

## Part C — Speculation and parallelism

### 7. The sorted-array result, and why it vanishes

**This is the important one.** Same source, same data, two optimisation levels:

```
-O0:   unsorted 0.418 s    sorted 0.105 s     ← 4.0× — the classic result
-O2:   unsorted 0.024 s    sorted 0.022 s     ← ~none
```

At `-O0` the `if (data[i] >= 128)` is a real conditional branch. On random data it's unpredictable, so the predictor is right about half the time and each miss costs a pipeline flush of ~15–20 cycles. Sorting makes the branch almost perfectly predictable, and the penalty disappears → [[foundations/computer-architecture/07-branch-prediction-and-speculation|note 07]].

**At `-O2` the branch does not exist.** Grep the assembly:

```bash
gcc -O2 -S -o - bp.c | grep -cE "cmov|pcmpgt|pmaxs|paddd"   # → 3
```

The compiler replaced it with **branchless code** — a conditional move, or SIMD predication that computes both sides and masks. No branch, nothing to mispredict, so sorting buys nothing.

**Three lessons, and they're worth more than the original demonstration:**

1. **You cannot benchmark a microarchitectural effect without checking what the compiler emitted.** Half the blog posts reproducing this experiment are measuring `-O0` code and reporting it as a property of the CPU
2. **Branchless code is the *fix* for unpredictable branches**, and your compiler often applies it for you
3. **The famous Stack Overflow answer is still correct** — it just describes a branch the compiler no longer generates for this shape of code

### 8. Counting mispredictions

On the `-O0` build, `perf stat -e branches,branch-misses`:

- **Unsorted:** miss rate around 25–50% of the data-dependent branch
- **Sorted:** well under 1%

**Read the rate, not the count.** Both versions execute the same number of branches; only the accuracy differs. Multiply the extra misses by ~15–20 cycles and you have the time difference from exercise 7, which is the check that you understand the mechanism rather than just the ratio.

### 9. Faster by adding memory

Unpadded counters in adjacent array slots share one 64-byte line. Two cores writing to that line ping-pong exclusive ownership between their caches on every increment — **false sharing**. Padding each counter to its own line typically gives **3–10×**.

Nothing is logically shared. The variables are independent. **The hardware's unit of coherence is the line, not the variable**, and that mismatch is the entire bug → [[foundations/computer-architecture/11-multicore-and-memory-models|note 11]].

This is why real concurrent structures pad their per-thread state, and why `alignas(64)` appears in high-performance code.

### 10. Breaking sequential consistency

On x86 you **will** see both-zero, at a low rate — typically a handful per million iterations.

x86 is **TSO**: it permits exactly one reordering, a *store* being buffered past a later *load*. Both threads' stores sit in store buffers while both loads read stale memory → both see 0. No other reordering is allowed, which is why x86 feels almost sequentially consistent and why code that's buggy on x86 is *much* buggier on ARM.

`mfence` (or a `seq_cst` atomic) between the store and the load drains the buffer and the count goes to zero.

**If you saw nothing:** your compiler probably reordered or cached the loads in registers. Use `volatile` or relaxed atomics — you're trying to observe the *hardware*, so the compiler must be stopped from "helping".

---

## Part D — Method

### 11. IPC

Typical: **0.5–1.5** for memory-bound work, **2–4** for compute-bound on a wide core (this machine can retire 4/cycle).

**IPC alone is never a verdict.** Low IPC might be stalls, or might be a program doing very little work very efficiently. High IPC might be a program executing far more instructions than it needs to.

**The next counter depends on the direction:** low IPC → `cache-misses`, `LLC-load-misses`, `stalled-cycles-backend`. Suspicious high IPC → `instructions` against a baseline. That branching decision *is* note 12's method.

### 12. Predict, then measure

No answer — the log is the artefact.

**The common wrong predictions:** people guess 10× for exercise 6 (it's 6.5× at N=1024 and 2.4× at N=512), and almost nobody predicts that exercise 7 shows *nothing* at `-O2`.

**Being wrong is the deliverable.** An engineer who predicts and checks develops calibration; one who only measures develops a collection of numbers → [[foundations/systems-engineering/05-trade-studies|trade studies]] makes the same argument about sensitivity analysis.

## Related
- [[foundations/computer-architecture/13-practice-exercises|the exercises]]
- [[foundations/computer-architecture/README|the course]]

*Source: [reference] — measured on an i7-8650U with GCC, August 2026.*
