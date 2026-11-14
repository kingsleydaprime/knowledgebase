# How Computers Work

## What this course is about

**A computer is a machine made of billions of tiny electrical switches. This course shows how switching electricity on and off adds up to apps, games and websites.**

When you write `print("hello")`, something physical happens inside the machine: electricity flows through some wires and not others. Most programming courses never explain how one leads to the other, so the machine stays a mystery that "just runs" your code.

This course starts at the very bottom, with electricity, and builds upwards one layer at a time:
- **electricity** flows through materials like silicon;
- silicon is made into **transistors**, tiny switches that electricity can turn on and off;
- switches are wired into **logic gates**, which make simple yes/no decisions;
- gates are combined into circuits that can **add numbers** and **remember** them;
- those circuits are combined into a **processor (CPU)**, which follows instructions;
- instructions come from **programs**, written in languages that a **compiler** translates.

You never use a layer until you've seen how it's built from the one below. At the end, you design your own simple computer and write a small programming language that runs on it.

## What you'll be able to do

By the end you will be able to:
- explain what electricity, voltage and current are, and why computers use only "on" and "off";
- explain why computer chips are made of silicon;
- explain how a transistor works as a switch, and how switches make logic gates;
- build an adding circuit and a memory circuit out of gates, on paper or in a free simulator;
- explain how a processor runs instructions one after another;
- follow one line of code all the way down to switches turning on and off.

## Before you start

**You need:** basic arithmetic, basic algebra, and comfort reading a short program. That's all. No electronics, no physics beyond secondary school, and no equipment: every exercise is done on paper or in a free logic simulator.

**One topic to read early:** how computers store negative numbers, called two's complement. It's taught in [[computer-architecture/02-data-representation|Data Representation]]. Read it before module 21. Other maths topics (binary, hexadecimal, logarithms) are linked from the lessons when you need them; see [[mathematics/index|Mathematics]].

## Where to start

The course has three stages. **Go in order through Stage 1**: each module depends on the one before. If something doesn't make sense, go back a module rather than pushing on.

### Stage 1: From electricity to memory (written here)

**Electricity**

1. [[how-computers-work/01-electricity/01-charge-current-and-voltage|Charge, Current and Voltage]]: what's actually moving in a wire, and what voltage means.
2. [[how-computers-work/01-electricity/02-resistance-and-ohms-law|Resistance and Ohm's Law]]: the one equation you need, and why heat limits every chip.
3. [[how-computers-work/01-electricity/03-circuit-laws|Circuit Laws: Kirchhoff, Series and Parallel]]: how voltage and current split around a circuit.
4. [[how-computers-work/01-electricity/04-signals-and-time|Signals and Time]]: signals that change over time, and why computers need a clock.
5. [[how-computers-work/01-electricity/05-the-digital-abstraction|The Digital Abstraction]]: the most important module in this stage. How messy voltages become a clean "0" or "1".

**Why chips are made of silicon**

6. [[how-computers-work/02-semiconductors/01-atoms-and-electrons|Atoms and Electrons]]: why some materials carry electricity and others don't.
7. [[how-computers-work/02-semiconductors/02-silicon-and-crystal|Silicon and the Crystal Lattice]]: what silicon is like inside, and how it's purified.
8. [[how-computers-work/02-semiconductors/03-energy-bands|Energy Bands and Conduction]]: the one property that decides whether a material conducts.
9. [[how-computers-work/02-semiconductors/04-doping|Doping: Engineering a Semiconductor]]: adding a tiny amount of another element to control how silicon conducts.
10. [[how-computers-work/02-semiconductors/05-pn-junctions|PN Junctions and Diodes]]: joining two kinds of silicon to make a one-way gate for electricity.

**The transistor**

11. [[how-computers-work/03-transistors/01-what-a-transistor-is|What a Transistor Is]]: the switch at the heart of every computer.
12. [[how-computers-work/03-transistors/02-mosfet-physics|MOSFET Physics]]: how the kind of transistor used in chips switches on and off.
13. [[how-computers-work/03-transistors/03-cmos|CMOS: The Pull-Up/Pull-Down Idea]]: pairing transistors so a chip uses almost no power when idle. Why your laptop doesn't melt.
14. [[how-computers-work/03-transistors/04-making-a-chip|Making a Chip]]: how billions of transistors are printed onto a chip, and why big chips are expensive.

**From switches to logic**

15. [[how-computers-work/04-logic/01-gates-from-transistors|Gates from Transistors]]: building NOT, NAND and NOR gates out of transistors.
16. [[how-computers-work/04-logic/02-boolean-algebra|Boolean Algebra]]: the maths of true and false, used to simplify circuits.
17. [[how-computers-work/04-logic/03-karnaugh-maps|Karnaugh Maps and Minimisation]]: a visual method for finding the smallest circuit that does a job.
18. [[how-computers-work/04-logic/04-universal-gates|Universal Gates]]: why one kind of gate (NAND) is enough to build anything.
19. [[how-computers-work/04-logic/05-buffers-and-driving-wires|Buffers, Fan-out and Driving Real Wires]]: what goes wrong when real gates drive real wires, and how to fix it.

**Circuits that calculate**

20. [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Multiplexers and Decoders]]: circuits that choose between inputs and pick out one location, the basis of memory.
21. [[how-computers-work/05-combinational/02-adders|Adders: Half, Full and Carry Propagation]]: adding numbers using nothing but logic gates.
22. [[how-computers-work/05-combinational/03-multipliers-and-comparators|Multipliers and Comparators]]: multiplying, and checking which number is bigger.
23. [[how-computers-work/05-combinational/04-the-alu|The ALU]]: one circuit that does all the arithmetic and logic, the calculator inside the processor.

**Circuits that remember**

24. [[how-computers-work/06-memory/01-latches-and-flip-flops|Latches and Flip-Flops]]: the big leap of the course. Feeding a circuit's output back into itself makes it remember.
25. [[how-computers-work/06-memory/02-registers-and-counters|Registers and Counters]]: storing whole numbers, and counting, which lets a processor step through a program.
26. [[how-computers-work/06-memory/03-memory-technology|Memory Technology: SRAM, DRAM and Flash]]: the different kinds of memory chips, and why computers use several.

### Stage 2: From the processor to programs (a route through other courses)

27. [[how-computers-work/07-the-bridge|The Bridge]]: a reading path through the courses that already teach the upper layers: [[computer-architecture/index|Computer Architecture]] (how a processor is organised), [[os/index|Operating Systems]], and [[compilers/index|Compilers]]. Each step says which earlier module it builds on. This stage is weeks of work, not an afternoon.

### Stage 3: Build your own computer (the final project)

Design a simple computer called **PRIME-1**, then write its software. This is where the bottom-up and top-down halves meet: a program in a language you made, compiled by a compiler you wrote, running on a processor you designed. The design is here; the hands-on building is in [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU]], in a simulator, in Verilog, in Python or on a breadboard.

28. [[how-computers-work/08-capstone/01-design-the-cpu|Design the PRIME-1 CPU]]: deciding how big numbers are, how many registers, and how memory works.
29. [[how-computers-work/08-capstone/02-the-isa|The PRIME-1 ISA]]: the set of instructions the processor understands, and how each is written in binary.
30. [[how-computers-work/08-capstone/03-build-the-hardware|Build the Hardware]]: building the part that reads each instruction and makes it happen.
31. [[how-computers-work/08-capstone/04-build-the-assembler|Build the Assembler]]: a program that turns readable instructions into binary.
32. [[how-computers-work/08-capstone/05-build-the-emulator|Build the Emulator]]: a software version of PRIME-1, to test against.
33. [[how-computers-work/08-capstone/06-build-the-language|Build the Language]]: a small programming language that compiles to PRIME-1.
34. [[how-computers-work/08-capstone/07-final-integration|Final Integration]]: following one line of your code all the way down to the switches.

## How to study it

1. **Go in order through Stage 1.** Doping makes no sense without energy bands, and gates make no sense without transistors.
2. **Draw everything.** Redraw each circuit and table without looking. It sticks in the hand, not the eye.
3. **Don't move on until you can explain the layer below.** If you can't explain a NAND gate from its transistors, don't start adders.
4. **At every layer, ask three questions:** What is physically happening? What simpler idea have we created by ignoring the details? What does the next layer build from it?

## The whole climb on one page

```text
Electricity
  → Silicon (semiconductors)
  → Transistors (tiny switches)
  → Logic gates (yes/no decisions)
  → Adders and the ALU (calculating)    and    Flip-flops and registers (remembering)
  → The processor (CPU)
  → Machine code and assembly
  → Operating system
  → Compiler
  → Programming language
  → Your ideas
```

## Related

- [[how-computers-work/some-questions|Some questions]]: the list of questions this course was built to answer, each matched to the module that answers it.
- [[computer-architecture/index|Computer Architecture]]: the next layer up from Stage 1.
- [[hardware/index|Hardware]]: the hands-on counterpart, building real things with microcontrollers.
- [[information-theory/index|Information Theory]]: what "information" means mathematically.
- [[COURSE-STANDARD|Course standard]]: the lesson shape every module here follows.

---

## About this course

- **What's written here and what isn't:** Stage 1 (modules 1–26) and the capstone design (28–34) are written in this folder, because they weren't taught anywhere else in the vault. Number systems and maths are linked to the [[mathematics/index|Mathematics]] course instead of being repeated, and the upper layers go through the existing courses in Stage 2.
- **The original curriculum's part names** (Part 0 maths, Part I information, Parts II–VII the hardware, Parts VIII–XVIII the upper layers) still appear inside some modules. Stage 1 here is Parts II–VII.
