# Pipelining

**[Intermediate]** — Overlapping instructions to keep every stage busy, and the three kinds of hazard that stop you.

## The idea

**A five-stage datapath uses one stage at a time and idles the other four.** Pipelining fixes that by starting a new instruction every cycle.

```
       cycle: 1    2    3    4    5    6    7    8
 instr 1:     IF   ID   EX   MEM  WB
 instr 2:          IF   ID   EX   MEM  WB
 instr 3:               IF   ID   EX   MEM  WB
 instr 4:                    IF   ID   EX   MEM  WB
```

**After the pipeline fills, one instruction completes per cycle** — five times the throughput of a sequential machine, with the same hardware.

> **The crucial distinction: pipelining improves *throughput*, not *latency*.** Each individual instruction still takes five cycles from fetch to writeback — arguably slightly longer, because of the pipeline registers. **You complete more per second without making any one faster.**
>
> **It's a laundry analogy that actually works.** One load takes wash + dry + fold regardless. But you can dry load 1 while washing load 2, and the *throughput* multiplies.

**Ideal speedup is the number of stages. Real speedup is less**, because of hazards.

## Structural hazards

**Two instructions need the same hardware in the same cycle.**

**The classic case:** instruction 4's IF and instruction 1's MEM both want memory in cycle 4.

**The fix is separate instruction and data caches** — which is why every CPU has a split L1: **L1i and L1d are separate caches**, and this is the reason. (Unified L2 and L3 are fine, since they're accessed less often.)

**The register file needs two read ports and one write port** so ID can read two operands while WB writes a result. **Some designs write in the first half of the cycle and read in the second**, which resolves it without extra ports.

**Structural hazards are largely designed away** in modern cores — with enough execution units and cache ports, they're rare. Multiply and divide units are the exception; they're not fully pipelined, so back-to-back divides stall.

## Data hazards

**An instruction needs a result that isn't ready.**

```asm
add x1, x2, x3     ; writes x1 in WB (cycle 5)
sub x4, x1, x5     ; needs x1 in ID  (cycle 3)  ← too early
```

**Three kinds**, though only one matters for an in-order pipeline:

| | Name | Real dependency? |
|---|---|---|
| **RAW** | read after write | **Yes** — a true dependency |
| WAR | write after read | No — a naming conflict |
| WAW | write after write | No — a naming conflict |

**RAW is fundamental** — the second instruction genuinely needs the first's result. **WAR and WAW are artefacts of reusing register names**, and [[foundations/computer-architecture/10-out-of-order-and-superscalar|register renaming]] eliminates them entirely.

### Forwarding

**The main fix, and it's elegant.**

The ALU result *exists* at the end of EX — it just hasn't been written to the register file yet. **So route it directly from the EX output to the next instruction's EX input**, bypassing the register file.

```
 add x1,x2,x3:  IF  ID  EX ─┐  MEM  WB
                            │ (forward)
 sub x4,x1,x5:      IF  ID  └→ EX   MEM  WB
```

**No stall.** Forwarding paths (bypass networks) exist between most pipeline stages, and they resolve the large majority of data hazards.

### The load-use hazard

**The one forwarding cannot fix:**

```asm
ldr x1, [x2]       ; value available at end of MEM (cycle 4)
add x3, x1, x4     ; needs it in EX (cycle 4) — not there yet
```

**A load's result isn't ready until MEM completes**, so the dependent instruction must stall one cycle.

**The compiler's job:** schedule an independent instruction into that slot. **This is why instruction scheduling is a real compiler optimisation** — reordering to fill load-use delay slots is measurable. → [[foundations/compilers/07-optimisation|Optimisation]]

**And it's a reason to prefer flat data over pointer chasing:** a linked-list traversal is a chain of dependent loads, each waiting for the previous, and there's nothing to fill the gap. **Latency-bound, not throughput-bound.** → [[foundations/computer-architecture/08-the-memory-hierarchy|Memory Hierarchy]]

## Control hazards

**The expensive one.**

```asm
cmp  x1, x2
b.eq label         ; outcome known in EX (cycle 3)
???                ; but IF needs the next address in cycle 2
```

**You must fetch something before you know whether it's right.**

**The options:**

**Stall** until resolved. Correct and slow — 2–3 cycles per branch, and **branches are 15–25% of instructions**, so this is a large loss.

**Predict** and speculatively execute. **If right, no cost. If wrong, discard the work and restart.**

**Branch delay slots** — MIPS's approach: the instruction after a branch always executes. **An ISA-visible hack** that worked at 5 stages and became actively harmful at 20. **A cautionary tale about exposing microarchitecture in the ISA** — MIPS was stuck with it forever.

**Prediction won**, and it's the subject of the next note. Modern predictors exceed 95% accuracy, which makes speculation overwhelmingly profitable. → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction]]

## The cost of a flush

**When a prediction is wrong, every speculatively-fetched instruction must be discarded.**

$$\text{penalty} \approx \text{pipeline depth to resolution}$$

| Pipeline | Misprediction cost |
|---|---|
| 5-stage classic | ~2–3 cycles |
| Modern (14–20 stages) | **~15–20 cycles** |
| Pentium 4 (31 stages) | **~30+ cycles** |

> **A 20-cycle penalty is roughly 60 lost instruction slots** on a 3-wide machine. **At 95% accuracy with branches every 5 instructions, mispredictions still cost around 15–20% of performance** — which is why branch predictors get an enormous transistor budget.
>
> And it's why **deeper pipelines have diminishing returns.** More stages means a higher clock and a worse misprediction penalty, and past a point the second dominates.

## Deeper pipelines

**The trade, stated:**

**More stages** → shorter critical path → **higher clock frequency.**

**But:** worse misprediction penalty, more pipeline-register overhead per stage, more power, and more forwarding complexity.

**Modern designs sit at 14–20 stages.** The Pentium 4's 31 was a well-documented mistake. → [[foundations/computer-architecture/05-the-datapath|Clocking]]

## What this means for your code

**The practical translation**, which is the point of the note:

**Predictable branches are nearly free.** A loop condition that's taken 999 times then not taken predicts almost perfectly.

**Unpredictable branches are expensive.** A data-dependent branch on random input mispredicts ~50% of the time.

> **The famous demonstration:** summing an array, adding only elements above a threshold. **Sorting the array first makes the loop several times faster** — the identical work, with the identical instruction count. **Sorted data makes the branch predictable.** It's the top-voted Stack Overflow question of all time, and it's this note.

**Branchless code can win** when a branch is unpredictable:

```c
// branchy — mispredicts on random data
if (a > b) max = a; else max = b;

// branchless — conditional move, no prediction needed
max = a > b ? a : b;    // compiler often emits cmov
```

**But only when unpredictable.** `cmov` has a data dependency on both operands, so **for a predictable branch, the branchy version is faster** — speculation lets it run ahead while `cmov` must wait. **Measure; don't assume branchless is better.**

**Loop unrolling** reduces branch count and exposes instruction-level parallelism. **Compilers do it; you rarely should by hand.**

**Sort or partition data** so branches become predictable, if you're branching in a hot loop.

**Use lookup tables or arithmetic** to eliminate a branch entirely, where it's cheap to do so.

**Profile before optimising.** `perf stat` reports `branch-misses` directly:

```
perf stat -e branches,branch-misses ./program
```

**A miss rate above ~5% in a hot loop is worth investigating.** Below that, look elsewhere. → [[foundations/computer-architecture/12-performance|Performance]]

---

## Related
- [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction and Speculation]] — solving the control hazard
- [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]] — hiding the data hazards
- [[foundations/computer-architecture/05-the-datapath|The Datapath]] — the stages being pipelined
- [[foundations/computer-architecture/README|Architecture map]]
