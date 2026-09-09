# How Computers Work

**A bottom-up study of computing systems, from sand to software.**

Most computing education starts in the middle. You learn a language, then maybe some data structures, and the machine underneath stays a rumour — a thing that "runs" your code by unspecified magic. This course removes the magic by refusing to start in the middle. It begins with electric charge and does not introduce an abstraction until the layer beneath it has been built.

> **The one idea:** every layer of a computer is a **deliberate act of forgetting**. Transistors forget that electrons are individuals and remember only "conducting or not". Logic gates forget voltage and remember only true and false. The ISA forgets which circuit does the adding. Each layer is a lie that is *useful because it is reliable* — and the whole subject is the study of why each lie holds, and what happens at the seams where it doesn't.

## What this course is, and what it borrows

The stack is too large for one folder, and this vault already teaches most of its upper half well. So this course **writes the missing bottom** — the path from electric charge to a working memory cell, which exists nowhere else in the vault — and then **routes you through the existing courses** for the layers they already cover, with the framing that makes each one part of a single climb.

That means the folder here is not the whole course. [[how-computers-work/07-the-bridge|Part VIII–XVIII]] is a reading path, not a rewrite.

## The two directions

**Bottom-up** — what this course builds first:

```
Physics → Silicon → Semiconductor → Transistor → Logic Gate
   → Digital Circuit → Memory/Datapath → CPU → ISA → Machine Code
```

**Top-down** — the descent from human intent:

```
Programming Language → Compiler → IR → Assembly → Machine Code → ISA → CPU
```

**The two paths meet at the processor.** The capstone is the demonstration that they really do meet: you write a program in a language you designed, compile it with a compiler you wrote, and execute it on a CPU you specified.

## Course objectives

By the end you should be able to:

1. Explain what information and computation mean *physically* — what is different about a piece of matter that is storing a 1 versus a 0.
2. Explain semiconductor behaviour well enough to say why silicon, and not copper or glass, sits at the bottom of the stack.
3. Derive a logic gate from a transistor circuit, and a transistor's behaviour from a doped junction.
4. Design combinational and sequential circuits, and explain how feedback creates memory out of components that have none.
5. Trace the fetch–decode–execute cycle through a datapath you can draw from memory.
6. Explain how a compiler turns text into instructions, and how an operating system gets those instructions onto the hardware.
7. **Trace one line of source code all the way down to transistor activity** without skipping a layer.

## Parts 0 and I — where they live (not written here)

The curriculum opens with **Part 0 (mathematics)** and **Part I (information and number representation)**. Neither is written in this folder, because **both are already taught properly elsewhere in the vault** — and duplicating them would create two versions to keep in sync.

| Curriculum topic | Where it is taught |
| :--- | :--- |
| Number bases, binary, decimal, hexadecimal, base conversion | [[foundations/mathematics/core/01-numbers/01-number-bases/01-introduction\|mathematics/number bases]] → [[foundations/mathematics/core/01-numbers/01-number-bases/02-binary\|binary]], [[foundations/mathematics/core/01-numbers/01-number-bases/04-hexadecimal\|hexadecimal]] |
| Exponents, logarithms, scientific notation | [[foundations/mathematics/06-exponents\|mathematics/exponents]], [[foundations/mathematics/07-scientific-notation\|scientific notation]] |
| Sets, functions, algebraic manipulation | [[foundations/mathematics/02-sets\|sets]], [[foundations/mathematics/05-algebraic-manipulation\|algebraic manipulation]] |
| Boolean logic, proof, modular arithmetic | [[foundations/discrete-math/index\|discrete-math/]] |
| Derivatives and integrals *(used only qualitatively here)* | [[foundations/mathematics/calculus/02-calculus-1/06-defining-derivative/01-definition\|calculus/the derivative]] |
| **Signed integers, two's complement, overflow** | [[foundations/computer-architecture/02-data-representation\|computer-architecture/data representation]] |
| **Fixed-point and floating-point, IEEE-754** | [[foundations/computer-architecture/02-data-representation\|computer-architecture/data representation]] |
| Endianness, alignment, text encoding | [[foundations/computer-architecture/02-data-representation\|computer-architecture/data representation]] |
| Information, entropy, encoding, error tolerance | [[foundations/information-theory/index\|information-theory/]] |

**The one you will actually need early:** [[foundations/computer-architecture/02-data-representation|two's complement]]. [[how-computers-work/05-combinational/02-adders|Module 21]] builds a subtractor from it, and [[how-computers-work/05-combinational/04-the-alu|module 23]] uses its overflow rules for the flags. **Read that note before module 21** if the phrase "invert and add one" is not already familiar.

Everything else on this list can be looked up when you meet it.

## Part I — the missing bottom (written here)

These parts exist nowhere else in the vault. This is the actual new material.

### Part II — Electricity and Electronics

The physics you need, and no more. Not an EE degree — the subset that makes transistors comprehensible.

1. [[how-computers-work/01-electricity/01-charge-current-and-voltage|Charge, Current and Voltage]] — **[Beginner]** — what is actually moving, and what "pressure" means for electrons
2. [[how-computers-work/01-electricity/02-resistance-and-ohms-law|Resistance and Ohm's Law]] — **[Beginner]** — the one equation, and power as the thing that limits every chip ever built
3. [[how-computers-work/01-electricity/03-circuit-laws|Circuit Laws — Kirchhoff, Series and Parallel]] — **[Beginner]** — voltage dividers, the mechanism behind every logic level
4. [[how-computers-work/01-electricity/04-signals-and-time|Signals and Time]] — **[Beginner → Intermediate]** — DC, AC, edges, rise time, and why clocks exist
5. [[how-computers-work/01-electricity/05-the-digital-abstraction|The Digital Abstraction]] — **[Intermediate]** — **the most important lesson in Part II**: how noise margins buy the right to stop thinking about voltage

### Part III — Matter and Semiconductors

Why sand. This part answers a question most courses skip entirely.

6. [[how-computers-work/02-semiconductors/01-atoms-and-electrons|Atoms and Electrons]] — **[Beginner]** — valence electrons, and why the periodic table predicts conductivity
7. [[how-computers-work/02-semiconductors/02-silicon-and-crystal|Silicon and the Crystal Lattice]] — **[Beginner]** — covalent bonding, purification, and how a wafer is made
8. [[how-computers-work/02-semiconductors/03-energy-bands|Energy Bands and Conduction]] — **[Intermediate]** — the band gap: one number that sorts all matter into conductor, insulator, semiconductor
9. [[how-computers-work/02-semiconductors/04-doping|Doping — Engineering a Semiconductor]] — **[Intermediate]** — adding one impurity atom in ten million to gain total control
10. [[how-computers-work/02-semiconductors/05-pn-junctions|PN Junctions and Diodes]] — **[Intermediate]** — the depletion region, and the first device that does something *asymmetric*

### Part IV — The Transistor

11. [[how-computers-work/03-transistors/01-what-a-transistor-is|What a Transistor Is]] — **[Intermediate]** — amplifier versus switch, BJT versus MOSFET, and why digital chose the MOSFET
12. [[how-computers-work/03-transistors/02-mosfet-physics|MOSFET Physics]] — **[Intermediate]** — channel formation, threshold voltage, and the three operating regions
13. [[how-computers-work/03-transistors/03-cmos|CMOS — The Pull-Up/Pull-Down Idea]] — **[Intermediate]** — **why your laptop doesn't melt**: complementary networks and near-zero static power
14. [[how-computers-work/03-transistors/04-making-a-chip|Making a Chip]] — **[Intermediate]** — **how transistors are physically built**: photolithography, the self-aligned gate, metal interconnect, and why yield makes big chips expensive

### Part V — Transistors to Logic

15. [[how-computers-work/04-logic/01-gates-from-transistors|Gates from Transistors]] — **[Intermediate]** — build NOT, NAND, NOR from CMOS pairs, and see why NAND is cheaper than AND
16. [[how-computers-work/04-logic/02-boolean-algebra|Boolean Algebra]] — **[Beginner → Intermediate]** — the laws, De Morgan, and algebra as circuit optimisation
17. [[how-computers-work/04-logic/03-karnaugh-maps|Karnaugh Maps and Minimisation]] — **[Intermediate]** — turning a truth table into the cheapest circuit that implements it
18. [[how-computers-work/04-logic/04-universal-gates|Universal Gates]] — **[Intermediate]** — the proof that NAND alone is enough for *any* computation
19. [[how-computers-work/04-logic/05-buffers-and-driving-wires|Buffers, Fan-out and Driving Real Wires]] — **[Intermediate]** — **the electrical layer between logic and physics**: what a buffer is for, tri-state buses, floating inputs, bus contention and decoupling

### Part VI — Combinational Logic

20. [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Multiplexers and Decoders]] — **[Intermediate]** — selection and addressing, the two moves behind every memory system
21. [[how-computers-work/05-combinational/02-adders|Adders — Half, Full and Carry Propagation]] — **[Intermediate]** — **arithmetic from pure logic**, traced bit by bit, and why the carry chain sets your clock speed
22. [[how-computers-work/05-combinational/03-multipliers-and-comparators|Multipliers and Comparators]] — **[Intermediate → Advanced]** — shift-and-add, carry-save trees, and why comparison is a subtraction you throw away
23. [[how-computers-work/05-combinational/04-the-alu|The ALU]] — **[Intermediate → Advanced]** — one circuit, many operations, and the flags that make branching possible

### Part VII — Memory and State

24. [[how-computers-work/06-memory/01-latches-and-flip-flops|Latches and Flip-Flops]] — **[Intermediate → Advanced]** — **the conceptual leap of the whole course**: feedback turns combinational logic into memory
25. [[how-computers-work/06-memory/02-registers-and-counters|Registers and Counters]] — **[Intermediate]** — from one bit to a word, and the program counter that makes a machine *sequential*
26. [[how-computers-work/06-memory/03-memory-technology|Memory Technology — SRAM, DRAM and Flash]] — **[Intermediate]** — six transistors versus one capacitor, and why that tradeoff shapes the memory hierarchy

## Part II — the bridge (routes into existing courses)

27. [[how-computers-work/07-the-bridge|The Bridge — Parts VIII to XVIII]] — the reading path through `computer-architecture/`, `os/`, `compilers/` and `programming-language-theory/`, with the dependency from Parts II–VII named at each step

## Part III — the capstone (written here)

**PRIME-1** — design and build a computer and its software stack. This is where the two directions meet.

The **design** lives here; the **four build tracks** live in [[build-your-own-shit/17-your-own-cpu/index|build-your-own-shit/17-your-own-cpu]] — logic simulator, Verilog, Python emulator and breadboard.

28. [[how-computers-work/08-capstone/01-design-the-cpu|Design the PRIME-1 CPU]] — word size, registers, memory model, and the tradeoffs behind each choice
29. [[how-computers-work/08-capstone/02-the-isa|The PRIME-1 ISA]] — instruction encoding, and why fixed-width beats variable-width for a first machine
30. [[how-computers-work/08-capstone/03-build-the-hardware|Build the Hardware]] — deriving the control unit from the ISA, then building it
31. [[how-computers-work/08-capstone/04-build-the-assembler|Build the Assembler]] — two-pass assembly, labels, symbol resolution
32. [[how-computers-work/08-capstone/05-build-the-emulator|Build the Emulator]] — a software PRIME-1, and differential testing
33. [[how-computers-work/08-capstone/06-build-the-language|Build the Language]] — lexer, parser, AST, codegen to PRIME-1 assembly
34. [[how-computers-work/08-capstone/07-final-integration|Final Integration]] — the full trace, source code to transistor

## Answering your own questions

This course is built to answer a specific list of questions — see [[how-computers-work/some-questions|some-questions]]. Each level of that list maps onto a part here:

| Question level | Answered by |
| :--- | :--- |
| Level 1 — Electricity | Part II (modules 1–5) |
| Level 2 — Semiconductor physics | Part III (modules 6–10) |
| Level 3 — The transistor | Part IV (modules 11–14) |
| Level 4 — Logic | Part V (modules 15–19) |
| Level 5 — From logic to computation | Part VI (modules 20–23) |
| Level 6 — Memory | Part VII (modules 24–26) |
| Level 7 — Build the CPU | The bridge (27) + capstone (28–30) |
| Level 8 — Machine language | The bridge (27) + capstone (29, 31) |
| Level 9 — Assembly → compiler → language | The bridge (27) + capstone (31–34) |

## Prerequisites

**Required:** arithmetic, algebra, and comfort reading a small program. That is genuinely it for Parts II–VII.

**Helpful but introduced as needed:** exponents and logarithms (for orders of magnitude and bit counts); the idea of a derivative (for rates of change in signals — used qualitatively, never solved).

**Where to top up:** [[foundations/mathematics/index|mathematics/]] for the algebra and logarithms. Part 0 of the original curriculum listed calculus; in practice this course uses it only to say "how fast something is changing", and you can read every lesson without having taken a calculus course.

**Not required:** any prior electronics, physics beyond secondary school, or hardware. No lab equipment is needed — every experiment in Parts II–VII is either a pencil-and-paper derivation or a free logic simulator.

## How to study this course

1. **Go in order for Parts II–VII.** This is the one stretch where skipping genuinely breaks things — doping makes no sense without band gaps, and CMOS makes no sense without doping.
2. **Draw everything.** Circuits and truth tables live in the hand, not the eye. Every lesson has something to redraw closed-book.
3. **Obey the descent rule.** If you cannot explain a NAND gate from its transistors, do not move on to adders — go back down. The whole value of a bottom-up course is lost the moment you start memorising a layer instead of deriving it.
4. **Use the bridge as a route, not a summary.** Parts VIII–XVIII send you into full existing courses. Those are weeks of work, not an afternoon.
5. **Build the capstone.** Everything before it is preparation for the moment your own compiler emits your own opcodes onto your own CPU.

## The core principle

At every layer, ask three questions:

**1. What is physically happening?** — What are the electrons doing?

**2. What abstraction have we created?** — We stop tracking individual electrons and call the behaviour "a transistor".

**3. What does the next layer build from it?** — Transistors become gates, gates become adders, adders become ALUs.

The goal is not to memorise the hierarchy. It is to understand **why every layer is allowed to exist** — what property of the layer below makes it safe to stop looking down.

## Master concept map

```text
PHYSICS ── Electromagnetism
   ↓
MATTER ── Atoms, Electrons, Crystal structure
   ↓
SEMICONDUCTORS ── Silicon, Doping, P-type, N-type
   ↓
PN JUNCTIONS
   ↓
TRANSISTORS ── NMOS, PMOS, CMOS
   ↓
LOGIC GATES ── NOT, AND, OR, NAND, NOR, XOR
   ↓
DIGITAL CIRCUITS ── Multiplexers, Decoders, Adders, Comparators, Shifters
   ├──────────────────────┐
   ↓                      ↓
COMBINATIONAL          SEQUENTIAL
   └── ALU                ├── Latches, Flip-flops
                          └── Registers, Counters
   ↓
DATAPATH ── Registers, ALU, Buses, Memory interface
   ↓
CONTROL UNIT
   ↓
CPU ── PC, IR, Registers, ALU, Control logic
   ↓
ISA → MACHINE CODE → ASSEMBLY → ASSEMBLER → OBJECT CODE → LINKER → EXECUTABLE
   ↓
OPERATING SYSTEM ── Processes, Threads, Memory, Syscalls, Drivers, I/O
   ↓
RUNTIME ── Libraries, VM, Garbage collector, JIT
   ↓
COMPILER / INTERPRETER ── Lexer, Parser, AST, Semantics, IR, Optimisation, Codegen
   ↓
PROGRAMMING LANGUAGE
   ↓
HUMAN IDEAS
```

## Related courses

- [[foundations/computer-architecture/index|Computer Architecture]] — where Parts VIII–XII are taught
- [[foundations/os/index|Operating Systems]] — Part XIII
- [[foundations/compilers/index|Compilers]] — Parts XV–XVII
- [[foundations/programming-language-theory/index|Programming Language Theory]] — Part XIV, the formal side
- [[foundations/information-theory/index|Information Theory]] — Part I in its mathematical form
- [[foundations/hardware/index|Hardware]] — the practical, build-things-with-microcontrollers counterpart to Part II
- [[foundations/mathematics/index|Mathematics]] — Part 0 prerequisites
- [[COURSE-STANDARD|Course standard]] — the teaching shape every lesson here follows
