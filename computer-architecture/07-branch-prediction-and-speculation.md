# Branch Prediction and Speculation

**[Intermediate → Advanced]** — Guessing what happens next, executing it before you know, and the security disaster that followed.

## Why predict

**Branches are 15–25% of instructions.** With a 15–20 cycle misprediction penalty, stalling on every branch would cost most of your performance.

**So the CPU guesses, and executes speculatively.** Right guesses cost nothing; wrong ones discard the work.

$$\text{cost} = \text{miss rate} \times \text{penalty}$$

**At 95% accuracy and a 20-cycle penalty, that's 1 cycle per branch on average.** At 99%, it's 0.2. **The difference between a good and a great predictor is large**, which is why they get an enormous transistor budget — some designs spend more area on prediction than on the ALUs.

## How predictors evolved

**1-bit** — remember the last outcome for this branch. Simple, and it **mispredicts twice per loop**: once on the final iteration, once on re-entry.

**2-bit saturating counter** — the classic:

```
 strongly    weakly     weakly     strongly
   NOT   ←──   NOT   ←──  TAKEN  ←── TAKEN
   TAKEN  ──→ TAKEN  ──→         ──→
```

**Requires two wrong guesses to flip.** A loop taken 999 times then not-taken only mispredicts once — the counter stays "strongly taken" through the single exit. **~85–90% accuracy** for a tiny amount of state.

**Two-level / correlating** — branch outcomes are correlated:

```c
if (x > 0) { ... }
...
if (x > 10) { ... }   // if the first was false, this is too
```

**Index a table by the branch address *and* the recent global history** (a shift register of the last $n$ outcomes). **Captures correlation between branches**, reaching ~93–95%.

**Tournament / hybrid** — run a local predictor and a global one, plus a **meta-predictor** choosing which to trust per branch. Some branches are locally patterned, others globally correlated.

**TAGE** — the modern standard. Multiple tables indexed by **different history lengths**, tagged so the longest matching history wins. **Captures both short and very long correlations**, and reaches **98–99%** on typical code. Every current high-performance CPU uses a TAGE derivative.

**Perceptron predictors** — a simple neural network over the history bits. Used in AMD's designs, often alongside TAGE.

> **These are genuinely sophisticated machine learning systems running in silicon at multi-GHz**, trained online, with a few kilobytes of state. It's one of the more remarkable pieces of engineering in a modern chip.

## Beyond direction

**Predicting *whether* a branch is taken isn't enough.**

**Branch Target Buffer (BTB)** — caches the *target address*, so you can fetch it before decoding the branch. **A BTB miss costs cycles even on a correctly-predicted branch.**

**Indirect branch prediction** — for `call rax`, virtual dispatch, and jump tables, the target varies. **Harder**, and it's why virtual calls in a hot polymorphic loop cost more than the load suggests. **ITTAGE** handles this in modern cores.

**Return Address Stack (RAS)** — a small hardware stack pushed on `call` and popped on `ret`. **Returns are near-perfectly predicted**, which is why function calls are cheap. Typically 16–32 entries; **deeper recursion overflows it and returns start mispredicting.**

## Speculation

**Prediction only pays if you act on it.**

**The CPU executes down the predicted path before knowing it's correct**, then either commits or discards.

**What makes it safe:** results go to a **reorder buffer**, not to architectural state. **Nothing becomes visible until the instruction retires**, and instructions retire in order. If a prediction was wrong, everything after it is discarded before it ever became real. → [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]]

**Other speculation:**

- **Memory disambiguation** — guess a load doesn't alias an earlier pending store, and execute it early
- **Value prediction** — guess a load's result (research, rarely shipped)
- **Prefetching** — speculatively fetch memory you'll probably need → [[foundations/computer-architecture/09-caches-in-depth|Caches]]

## Spectre and Meltdown

**The 2018 discovery that speculation leaks data**, and the most consequential microarchitecture story of the last decade.

> **The core insight: discarded speculative work leaves traces in the cache.**
>
> Architectural state is rolled back perfectly. **Microarchitectural state is not** — and cache contents are measurable through timing.

**Spectre v1 (bounds check bypass):**

```c
if (index < array1_size) {          // train this to predict TAKEN
    y = array2[array1[index] * 4096];  // then pass an out-of-bounds index
}
```

1. **Train** the predictor with in-bounds values so it predicts "taken"
2. **Pass an out-of-bounds index.** The bounds check must load `array1_size` from memory — slow — so the CPU **speculates past it**
3. Speculatively, `array1[index]` reads **out-of-bounds memory**, and `array2[secret * 4096]` **loads a cache line whose address depends on the secret**
4. The check resolves, the work is discarded, **the architectural state is clean**
5. **But one line of `array2` is now cached.** Time accesses to each candidate line; the fast one reveals the secret byte

**No instruction executed illegally. The rollback was perfect. The data leaked anyway.**

**Spectre v2 (branch target injection)** — poison the indirect branch predictor so a victim speculatively jumps to a gadget of your choosing.

**Meltdown** — on affected Intel chips, the permission check on a kernel-memory load happened *late*, so speculative execution read kernel memory before faulting. **Simpler and more devastating**, and it allowed reading all of kernel memory from userspace.

### The mitigations, and their cost

| Mitigation | Cost |
|---|---|
| **KPTI** (separate kernel page tables) | **5–30%** on syscall-heavy workloads |
| **Retpoline** (replace indirect branches) | a few % |
| **IBRS/IBPB** (flush predictor state) | varies, sometimes large |
| **`lfence`** after bounds checks | large where applied |
| **Microcode updates** | shipped to existing CPUs |

> **These were among the largest across-the-board performance regressions in computing history** — some database and I/O workloads lost 30%. **And they were shipped in weeks**, which was only possible because microcode is updatable. → [[foundations/computer-architecture/05-the-datapath|Microcode]]

**Meltdown was fixed in hardware** in subsequent designs. **Spectre largely was not** — it's inherent to speculation, and mitigating it fully would mean giving up most of the performance speculation provides.

**The lesson that generalised:**

**Microarchitectural state is a covert channel.** A whole family followed — MDS/RIDL/Fallout, LVI, Retbleed, Downfall, Inception. **Any shared microarchitectural resource can leak across a security boundary.**

**And it broke a foundational assumption:** that the ISA is a sufficient security abstraction. **Timing was never part of the contract, and it turned out to carry information.**

**Practical consequences that persist:** cloud providers no longer co-locate untrusted tenants on sibling hyperthreads; browsers reduced timer resolution and added site isolation; **and constant-time cryptography became non-negotiable** — any secret-dependent branch or memory access is a leak. → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic Best Practices]]

## Writing predictable code

**What you can actually do:**

**Make branches predictable.** Sorting or partitioning data so a hot branch goes one way is often a large win. → [[foundations/computer-architecture/06-pipelining|The sorted-array example]]

**Hoist invariant branches out of loops.** A condition that doesn't change shouldn't be tested every iteration — and the compiler will often do this (loop unswitching) if it can prove invariance.

**Use `[[likely]]` / `[[unlikely]]`** (C++20) or `__builtin_expect` for genuinely skewed branches — error paths especially. **It affects code layout**, keeping the hot path contiguous in the instruction cache, which is often the bigger win.

**Consider branchless** for unpredictable branches — `cmov`, bit tricks, table lookups. **Only when unpredictable**, since `cmov` serialises on both inputs.

**Reduce indirect calls in hot loops.** Devirtualisation, or sorting objects by type so the indirect target is stable. **A megamorphic call site mispredicts constantly.**

**Watch deep recursion** — it overflows the return address stack.

**Measure:**

```
perf stat -e branches,branch-misses,cycles,instructions ./prog
```

**Above ~5% miss rate in a hot path is worth attention.** And check `instructions per cycle` — below ~1.0 suggests you're stalling on something, whether branches or memory.

---

## Related
- [[foundations/computer-architecture/06-pipelining|Pipelining]] — why the penalty exists
- [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]] — what makes speculation safe
- [[foundations/computer-architecture/09-caches-in-depth|Caches in Depth]] — the side channel
- [[foundations/computer-architecture/README|Architecture map]]
