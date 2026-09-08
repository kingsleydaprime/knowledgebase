# Computer Architecture

How you get from logic gates to something that runs a program, and why that machine has the performance characteristics it does. **The layer between [[foundations/os/README|operating systems]] and [[hardware/02-digital-and-analog|digital logic]]** — and the source of every constant the rest of this vault quotes.

**~18,900 words across 14 notes** (including practice + solutions). Built August 2026 to close a gap found by auditing a standard CS syllabus against this vault. `[reference]`.

> **The practical pitch:** Big-O tells you how an algorithm scales. **This domain tells you why one $O(n)$ loop is thirty times slower than another** — and that ratio decides more real performance outcomes than complexity class does.

## Reading order

**02–05 are the foundation. 06–07 and 10 are the performance machinery. 08–09 are memory** — the most practically important part. **11–12 are multicore and method.**

1. [[foundations/computer-architecture/01-what-architecture-is|What Computer Architecture Is]] — **[Beginner → Intermediate]** — the ISA as a contract, RISC vs CISC honestly, and **the latency numbers scaled so you can feel them**
2. [[foundations/computer-architecture/02-data-representation|Data Representation]] — **[Beginner → Intermediate]** — two's complement, IEEE 754, endianness, alignment. **Why $0.1+0.2\neq0.3$ and why struct field order matters**
3. [[foundations/computer-architecture/03-instruction-sets|Instruction Sets]] — **[Intermediate]** — registers, addressing modes, calling conventions, SIMD, and **why variable-length decode is x86's permanent handicap**
4. [[foundations/computer-architecture/04-assembly|Assembly]] — **[Intermediate]** — reading it, which is the skill that matters. The stack, calls, and **what bounds checking actually costs**
5. [[foundations/computer-architecture/05-the-datapath|The Datapath]] — **[Intermediate]** — fetch/decode/execute/memory/writeback, control signals, and **why microcode saved the industry in 2018**
6. [[foundations/computer-architecture/06-pipelining|Pipelining]] — **[Intermediate]** — overlapping instructions, the three hazards, and **why sorting an array makes the same loop several times faster**
7. [[foundations/computer-architecture/07-branch-prediction-and-speculation|Branch Prediction and Speculation]] — **[Intermediate → Advanced]** — TAGE predictors, and **Spectre: how discarded work leaks data**
8. [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — **[Intermediate]** — **the most important note here.** Cache lines, locality, AoS vs SoA, and why linked lists lose to arrays
9. [[foundations/computer-architecture/09-caches-in-depth|Caches in Depth]] — **[Advanced]** — associativity, coherence, **false sharing**, NUMA, and the power-of-two stride trap
10. [[foundations/computer-architecture/10-out-of-order-and-superscalar|Out-of-Order and Superscalar]] — **[Advanced]** — register renaming, the reorder buffer, and **breaking dependency chains with multiple accumulators**
11. [[foundations/computer-architecture/11-multicore-and-memory-models|Multicore and Memory Models]] — **[Advanced]** — acquire/release, and **why your lock-free code works on x86 and breaks on ARM**
12. [[foundations/computer-architecture/12-performance|Performance]] — **[Intermediate → Advanced]** — the method: measure, understand, algorithm, layout, micro-optimise, measure again

## The things worth carrying

1. **DRAM is ~50–75× slower than L1.** Most programs are memory-bound, not compute-bound → [[foundations/computer-architecture/08-the-memory-hierarchy|08]]
2. **Count cache lines touched, not operations.** That's the number that predicts runtime → [[foundations/computer-architecture/08-the-memory-hierarchy|08]]
3. **A linked list and an array have the same $O(n)$ traversal and a 10× difference**, because pointer chasing serialises the loads → [[foundations/computer-architecture/08-the-memory-hierarchy|08]]
4. **False sharing can make a parallel program slower than the serial one** — independent variables, one cache line. `perf c2c` finds it → [[foundations/computer-architecture/09-caches-in-depth|09]]
5. **Predictable branches are nearly free; unpredictable ones cost ~20 cycles.** Sorting the data can beat rewriting the loop → [[foundations/computer-architecture/06-pipelining|06]]
6. **Serial dependency chains waste a wide machine.** Multiple accumulators is the highest-value micro-optimisation → [[foundations/computer-architecture/10-out-of-order-and-superscalar|10]]
7. **x86 is strongly ordered and hides concurrency bugs that ARM exposes.** Test on ARM → [[foundations/computer-architecture/11-multicore-and-memory-models|11]]
8. **`volatile` is not for threading** in C/C++ — no ordering, no atomicity → [[foundations/computer-architecture/11-multicore-and-memory-models|11]]
9. **Never use floats for money or equality**, and float addition isn't associative — so the compiler can't reorder it and parallel reductions aren't reproducible → [[foundations/computer-architecture/02-data-representation|02]]
10. **Amdahl: optimising 10% of runtime caps your gain at 11%.** Profile first, always → [[foundations/computer-architecture/12-performance|12]]
11. **Microarchitectural state is a covert channel.** Spectre broke the assumption that the ISA is a sufficient security abstraction → [[foundations/computer-architecture/07-branch-prediction-and-speculation|07]]

## Where this connects

| | |
|---|---|
| [[foundations/os/README\|operating systems]] | Sits directly on this — virtual memory, scheduling, syscalls |
| [[hardware/02-digital-and-analog\|hardware/]] | The gates and signals below |
| [[foundations/compilers/08-code-generation\|compilers]] | Codegen, register allocation and scheduling target this machine |
| [[languages/04-c/README\|C]] · [[languages/05-cpp/README\|C++]] · [[languages/03-rust/README\|Rust]] | Where you can actually control layout and see the effects |
| [[foundations/dsa/05-algorithms/01-algorithms\|algorithms]] | Big-O's constants live here |
| [[cybersecurity/05-cryptography/README\|cryptography]] | Constant-time code, and why timing is a leak |

## The honest note

**`[reference]`, and this domain is unusually easy to close the gap on** — everything here is measurable on the machine you're reading this on, in minutes, for free.

**That makes the gap less excusable than in [[engineering/README|engineering/]] or [[robotics/README|robotics/]].** No hardware to buy, no lab. Just `perf` and an afternoon.

**What would actually close it:**

1. **Run `perf stat` on something you wrote.** Look at the IPC. **Then find out why it's what it is.** Twenty minutes, and it makes the whole track concrete
2. **Reproduce the sorted-array branch experiment.** Same code, sorted and unsorted input, several-fold difference. **Seeing it yourself is different from reading it**
3. **Write the matrix multiply three ways** — naive, loop-interchanged, blocked. Measure. **The 10× from reordering identical arithmetic is the lesson of note 08 in one experiment**
4. **Demonstrate false sharing.** Two threads incrementing adjacent array elements, then padded to 64 bytes. **Watch it get faster by adding memory**
5. **Read some assembly on Godbolt.** Change optimisation levels and watch code disappear
6. **The books:** Patterson & Hennessy (*Computer Organization and Design*) for the fundamentals; Hennessy & Patterson (*Computer Architecture: A Quantitative Approach*) for depth; **Drepper's *What Every Programmer Should Know About Memory*** — free, and still the best thing written on note 08's material; Agner Fog's optimisation manuals for the microarchitectural detail

**What's missing here:** ~~exercises~~ — **closed by notes 13–14 (Aug 2026)**; ~~GPU architecture~~ (**now covered** — [[foundations/gpu-and-parallel-computing/README|foundations/gpu-and-parallel-computing/]]), I/O and DMA, power and thermal design in depth, chip layout, formal verification of hardware, and anything on FPGAs or accelerator design beyond a mention.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[foundations/computer-architecture/13-practice-exercises|Practice Exercises]] — twelve experiments on your own machine — cache sizes measured from timing alone, and **two classic results that fail to reproduce at `-O2`**
- [[foundations/computer-architecture/14-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[foundations/os/README|Operating Systems]] — the layer above
- [[hardware/README|Hardware & Embedded]] — the layer below
- [[foundations/theory-of-computation/05-turing-machines|Turing Machines]] — the universal machine this implements
- [[BUILD-PLAN|Build Plan]]
