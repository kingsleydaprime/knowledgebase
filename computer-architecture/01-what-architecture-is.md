# What Computer Architecture Is

**[Beginner → Intermediate]** — The ISA as a contract, the layers between your code and the electrons, and why the constants matter.

**Source:** `[reference]` — see [[foundations/computer-architecture/README|the domain note]].

## The gap this fills

**Above:** [[foundations/os/README|operating systems]] assume a CPU that executes instructions and a memory that stores things.

**Below:** [[hardware/02-digital-and-analog|digital logic]] gives you gates and flip-flops.

**Between them is architecture** — how you get from NAND gates to something that runs a program, and why that machine has the performance characteristics it does.

> **The practical reason to care:** every performance note in this vault quotes constants — "cache miss", "branch misprediction", "false sharing", "memory barrier". **This domain is where those constants come from.** Big-O tells you how an algorithm scales; architecture tells you why one $O(n)$ loop is thirty times slower than another. → [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]]

## The layers

```
    application            what you write
  ─────────────────
    language / runtime     compilers, JIT, GC
  ─────────────────
    operating system       processes, virtual memory
  ─────────────────
 ▶  ISA                    THE CONTRACT
  ─────────────────
 ▶  microarchitecture      how this chip implements it
  ─────────────────
    logic / gates
  ─────────────────
    transistors / physics
```

**Each layer is an abstraction over the one below, and the two marked layers are what this domain is about.**

## The ISA is a contract

> **The Instruction Set Architecture is everything software is allowed to depend on: instructions, registers, addressing modes, the memory model, and how exceptions behave.**
>
> **The microarchitecture is how a particular chip implements that contract.**

**x86-64 is an ISA.** Intel's Golden Cove and AMD's Zen 4 are microarchitectures implementing it. **The same binary runs on both** — that's the contract holding — while the chips differ completely inside: different pipeline depths, cache sizes, execution units, branch predictors.

**This separation is the central idea in the domain**, and it's what makes forty years of binary compatibility possible. A 2024 CPU runs code compiled in 1995.

**Where it leaks — and it does leak:**

**Performance is not in the contract.** Same instructions, wildly different speed. **This is the leak you'll actually hit**, and most of this track is about it.

**Timing side channels.** Spectre and Meltdown exploited *microarchitectural* state (caches, speculation) to leak data the *architectural* contract said was inaccessible. **The abstraction was violated by the implementation**, and it took a decade to notice. → [[foundations/computer-architecture/07-branch-prediction-and-speculation|Speculation]]

**Memory ordering.** What other cores observe depends on the model, and it differs sharply between x86 and ARM. **This is a real portability trap.** → [[foundations/computer-architecture/11-multicore-and-memory-models|Memory Models]]

## The major ISAs

| ISA | Style | Where |
|---|---|---|
| **x86-64** | CISC, variable-length | desktops, servers |
| **ARM (AArch64)** | RISC, fixed 32-bit | phones, Apple Silicon, AWS Graviton |
| **RISC-V** | RISC, **open standard** | embedded, research, growing |
| **POWER, SPARC** | RISC | legacy enterprise |

**RISC vs CISC**, and the honest version:

**CISC** — many complex instructions, variable length, memory operands. Designed when memory was scarce and compilers were poor, so instruction density mattered.

**RISC** — few simple instructions, fixed length, load/store only. Easier to pipeline and decode.

> **The debate is largely over, and both sides won something.** Modern x86 chips **decode CISC instructions into RISC-like micro-ops** internally and execute those. **The ISA is a compatibility skin over a RISC core.**
>
> **What remains real** is decode cost. x86's variable-length instructions (1–15 bytes) make parallel decoding genuinely hard — you can't find instruction boundaries without decoding. ARM's fixed 32-bit instructions decode trivially in parallel. **That's a real and permanent advantage**, and it's part of why Apple Silicon can decode 8 instructions per cycle where x86 struggles past 4–6.

**RISC-V matters because it's free.** No licence, no royalties, extensible. Already dominant in academic work and moving into embedded and accelerators.

## Where performance comes from

**The historical shift that shapes everything below:**

```
 performance
     │              ╱‾‾‾‾‾  multicore era
     │            ╱        (parallelism)
     │      ╱‾‾‾‾
     │    ╱   ← ~2005: clock speeds stall
     │  ╱
     │╱  frequency scaling era
     └──────────────────→ time
```

**Until about 2005, performance came free.** Dennard scaling meant smaller transistors ran faster at the same power, and clock speeds doubled regularly. **Your code got faster if you waited.**

**Then power density hit a wall.** Clocks stalled around 3–4 GHz. **Moore's Law kept delivering transistors; they went into cores, caches and speculation instead of frequency.**

**The consequences you live with:**

- **Free lunch over.** Single-threaded performance improves slowly now. **To go faster, go parallel** → [[foundations/os/02-processes-and-threads|Threads]]
- **Memory is the bottleneck**, not compute. CPUs got much faster than DRAM, so most programs wait on memory → [[foundations/computer-architecture/08-the-memory-hierarchy|Memory Hierarchy]]
- **Dark silicon** — you can't power all the transistors at once, so chips include specialised units used intermittently
- **Specialisation** — GPUs, TPUs, video encoders, crypto units. **When general-purpose scaling stops, build specific hardware**

## The numbers that matter

**Latency, in units you can feel.** Scale a cycle to one second:

| Operation | Cycles | Scaled |
|---|---|---|
| L1 cache hit | ~4 | **4 seconds** |
| L2 hit | ~12 | 12 seconds |
| L3 hit | ~40 | 40 seconds |
| **Main memory** | **~200–300** | **~4 minutes** |
| Branch mispredict | ~15–20 | 20 seconds |
| **NVMe SSD read** | ~150,000 | **~2 days** |
| **Network round trip (same DC)** | ~1,500,000 | **~3 weeks** |

> **Memory is 50× slower than L1.** That single ratio explains cache-friendly data structures, why an array of structs beats a struct of pointers, why linked lists underperform their Big-O, and why "just add an index" sometimes makes a database slower.

**Throughput vs latency** is the other distinction. A modern core issues 4–6 instructions per cycle **if they're independent.** A dependency chain runs at the latency of each step. **Same instruction count, several times the runtime** — which is why loop unrolling and instruction-level parallelism matter. → [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order Execution]]

## The abstractions that leak

**A preview of the rest of the track**, because each of these is a place where "the CPU executes my instructions in order" stops being true:

**Memory looks flat. It isn't.** Caches make access cost vary by 50×, and it's invisible in your source.

**Instructions look sequential. They aren't.** Out-of-order execution reorders aggressively, constrained only by dependencies.

**Branches look free. They aren't.** A misprediction costs 15–20 cycles of discarded work.

**Memory writes look immediate. They aren't.** Store buffers and cache coherence mean other cores see your writes later, possibly reordered.

**Your program looks alone. It isn't.** Other processes share caches, TLBs and predictors — the basis of side-channel attacks.

> **Every one of these leaks is a performance or correctness surprise waiting**, and the reason to learn architecture is to recognise them when the profiler says something absurd.

## Reading this track

**02–05 are the foundation** — data representation, instruction sets, assembly, and how a CPU actually executes one instruction.

**06–07 and 10 are the performance machinery** — pipelining, branch prediction, out-of-order execution.

**08–09 are memory**, which is where most real performance problems live. **If you read only two notes, read those.**

**11–12 are multicore and how to actually make code fast.**

**Prerequisites:** some [[hardware/02-digital-and-analog|digital logic]] helps but isn't required. Familiarity with C-level programming — pointers, memory layout — makes it much more concrete. → [[languages/04-c/README|C]]

---

## Related
- [[foundations/computer-architecture/02-data-representation|Data Representation]] — how numbers are actually stored
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — the most practically important part
- [[hardware/README|Hardware & Embedded]] — the layer below
- [[foundations/computer-architecture/README|Architecture map]]
