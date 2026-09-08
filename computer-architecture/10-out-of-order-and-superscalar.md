# Out-of-Order and Superscalar Execution

**[Advanced]** — Executing several instructions per cycle, in the wrong order, while pretending you didn't.

## Two separate ideas

**Superscalar** — issue **multiple instructions per cycle**. Width, not order.

**Out-of-order** — execute instructions **when their operands are ready**, not in program order.

**They compose.** A modern core is both: 4–8 wide, and reordering across a window of hundreds of instructions.

**The goal is instruction-level parallelism (ILP)** — finding independent work to fill slots that would otherwise stall.

```
 In-order, 1-wide:
   ldr x1,[x2]   ─────wait 200 cycles for DRAM─────  add x3,x1,x4   add x5,x6,x7
                                                     (x5 waits pointlessly)

 Out-of-order:
   ldr x1,[x2]   ─────wait─────  add x3,x1,x4
   add x5,x6,x7  (executes immediately — independent)
```

> **The whole point is hiding latency.** A cache miss costs 200+ cycles; **out-of-order execution finds other work to do during them.** It's the primary reason a modern core outperforms an in-order one on the same clock — sometimes by 3–4×.

## Register renaming

**The enabler**, and the idea worth understanding properly.

```asm
add x1, x2, x3     ; writes x1
str x1, [x4]       ; reads x1     — RAW: a true dependency
add x1, x5, x6     ; writes x1    — WAW: a NAME conflict only
```

**The third instruction is completely independent of the first two.** It just reuses the name `x1`.

**Renaming maps architectural registers onto a much larger physical register file:**

```
 architectural  →  physical
 add x1,...     →  add p37,...
 str x1         →  str p37
 add x1,...     →  add p52,...     ← different physical register, no conflict
```

**WAR and WAW dependencies disappear entirely.** Only true data flow (RAW) constrains execution.

**The numbers:** an ISA exposes 16 (x86-64) or 32 (AArch64) registers. **The hardware has 180–350+ physical registers.** The architectural names are just an interface.

> **This is why "x86 only has 16 registers" matters less than it sounds.** The hardware has plenty; the ISA limit costs you *encoding* flexibility and forces the compiler to spill more often — real, but not the whole story.

## The pipeline

```
 ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐  ┌────────┐  ┌────────┐
 │ FETCH  │→ │ DECODE │→ │ RENAME │→ │ SCHEDULE │→ │EXECUTE │→ │ RETIRE │
 └────────┘  └────────┘  └────────┘  └──────────┘  └────────┘  └────────┘
   in-order    in-order    in-order   OUT OF ORDER   OOO         IN ORDER
```

**The front end is in-order. The back end is out-of-order. Retirement is in-order again.**

**Reservation stations / scheduler** — instructions wait here until their operands are ready, then issue to a free execution unit. **The scheduler window is 100–500+ instructions** on modern cores.

**Reorder Buffer (ROB)** — holds instructions in **program order** from issue to retirement. Results go here, not to architectural state.

> **The ROB is what makes speculation safe.** Instructions execute out of order, but **they commit in order**, and nothing becomes architecturally visible until it retires. On a misprediction or exception, everything after the offending instruction is simply discarded from the ROB — **it never happened.**
>
> **That's the illusion the whole design maintains: massive internal reordering, perfectly sequential observable behaviour.** And it's precisely the illusion Spectre broke, by observing the *microarchitectural* traces of work that "never happened". → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Speculation]]

**Tomasulo's algorithm** (IBM 360/91, 1967) is the origin of all this — renaming plus reservation stations plus a common data bus. **Sixty years old and still the shape of every high-performance core.**

## Execution units

**A modern core has 8–12 ports**, each feeding different units:

| Port type | Handles | Typical count |
|---|---|---|
| Integer ALU | add, sub, logic | 4 |
| Branch | | 2 |
| Load | | 2–3 |
| Store | address + data | 2 |
| Vector/FP | SIMD, floating point | 2–4 |
| Multiply/divide | | 1 each |

**Latency vs throughput**, and the distinction matters:

| Operation | Latency | Throughput |
|---|---|---|
| Integer add | 1 | 4/cycle |
| Integer multiply | 3 | 1/cycle |
| FP add/multiply (FMA) | 4 | 2/cycle |
| **Integer divide** | **20–40** | **not pipelined** |
| L1 load | 4–5 | 2/cycle |

> **Division is the outlier: 20–40 cycles, poorly pipelined.** Which is why compilers replace division by a constant with a multiply-and-shift, and why `x / 8` becomes `x >> 3`. **Avoid division in hot loops** — multiply by a reciprocal, or restructure.
>
> And note the FMA row: **you can do 2 fused multiply-adds per cycle but each has 4-cycle latency.** A dependent chain runs at 1 per 4 cycles; independent ones run 8× faster. **This is exactly why loop unrolling helps** — it creates independent chains.

## What limits ILP

**Real code rarely achieves the peak width.**

**True dependencies.** A serial chain has no parallelism available:

```c
for (i = 0; i < n; i++) sum += a[i];   // every add depends on the last
```

**FP addition latency ~4 cycles means this runs at 1 element per 4 cycles**, regardless of an 8-wide machine.

**The fix — multiple accumulators:**

```c
s0 += a[i]; s1 += a[i+1]; s2 += a[i+2]; s3 += a[i+3];
// four independent chains → ~4× faster
sum = s0 + s1 + s2 + s3;
```

**Note this changes floating-point results** (addition isn't associative), which is why the compiler won't do it without `-ffast-math`. **For integers it will.** → [[foundations/computer-architecture/02-data-representation|Floating point]]

**Branch mispredictions** flush everything speculative.

**Cache misses** — out-of-order hides some, but **a long dependent chain of misses (pointer chasing) can't be hidden**, because you don't know the next address until the current load returns.

**Window size.** If the independent work is 500 instructions away, the scheduler can't see it.

**Memory ordering.** A load can't reorder past a store to the same address; **memory disambiguation predicts this**, and mispredicting costs a flush.

## Hyperthreading (SMT)

**Two logical cores sharing one physical core** — duplicated architectural state (registers, PC), shared everything else (execution units, caches, predictors).

**The idea:** when one thread stalls on a cache miss, the other uses the idle execution units.

**When it helps:** memory-bound workloads with low IPC and poor ILP. **Typical gain 15–30%**, occasionally more.

**When it hurts:**

- **Compute-bound code with good ILP** — both threads compete for the same units, and cache pressure doubles. **Can be a net loss**
- **Cache-sensitive workloads** — halving the effective L1/L2 per thread
- **Latency-critical services** where predictable tail latency matters more than throughput
- **Security** — shared microarchitectural state across threads is a side channel. **Cloud providers no longer co-locate untrusted tenants on sibling threads**, and OpenBSD disables SMT by default → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Spectre]]

**Benchmark it.** Databases and HPC codes frequently disable SMT and gain.

## Writing ILP-friendly code

**What actually helps:**

**Break dependency chains.** Multiple accumulators is the highest-value single technique.

**Unroll loops** — usually the compiler's job, but it exposes independent work and reduces branch overhead.

**Avoid long serial chains.** Restructure reductions as trees.

**Reduce unpredictable branches** — a flush discards everything in flight.

**Improve locality first.** **A cache miss costs more than any ILP gain**, so memory comes before instruction scheduling. → [[foundations/computer-architecture/08-the-memory-hierarchy|Memory Hierarchy]]

**Avoid division and long-latency ops** in inner loops.

**Let the compiler work.** `-O2`/`-O3` schedule far better than hand-reordering, and modern cores reorder anyway.

**Measure IPC:**

```
perf stat ./program     # look at insn per cycle
```

| IPC | Meaning |
|---|---|
| < 0.5 | **badly stalled** — almost certainly memory |
| ~1.0 | mediocre |
| 2–3 | good |
| 4+ | excellent, near peak |

**Then use `perf record` / `perf annotate`** to find where. **Low IPC plus high cache misses means fix your data layout; low IPC plus high branch misses means fix your branches; low IPC with neither suggests a dependency chain.**

---

## Related
- [[foundations/computer-architecture/06-pipelining|Pipelining]] — the simpler model
- [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction]] — what feeds the front end
- [[foundations/computer-architecture/12-performance|Performance]] — the methodology
- [[foundations/computer-architecture/README|Architecture map]]
