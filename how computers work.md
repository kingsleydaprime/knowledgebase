# FROM SILICON TO SOFTWARE

## A Bottom-Up Study of Computing Systems

### Course Description

This course provides a first-principles journey through the complete computational stack, beginning with matter, electricity, and semiconductor physics and progressing through transistors, digital logic, memory, processor architecture, machine code, assembly language, compilers, operating systems, and high-level programming languages.

The central objective is to understand **how physical phenomena become computation and how computation eventually becomes software**.

The course follows two directions:

**Bottom-up:**

Physics → Silicon → Semiconductor → Transistor → Logic Gate → Digital Circuit → Memory/Datapath → CPU → ISA → Machine Code

**Top-down:**

Programming Language → Compiler/Interpreter → Intermediate Representation → Assembly → Machine Code → ISA → CPU

The two paths meet at the processor.

---

# COURSE OBJECTIVES

By the end of this course, the student should be able to:

1. Explain what information and computation mean physically.
2. Explain voltage, current, resistance, power, electric fields, and basic circuit behavior.
3. Explain why silicon is useful for electronic computation.
4. Explain semiconductor behavior and energy bands.
5. Explain doping and the formation of P-type and N-type semiconductors.
6. Explain PN junctions and diodes.
7. Explain how a MOSFET works physically.
8. Explain how transistors implement digital switches.
9. Derive logic gates from transistor circuits.
10. Use Boolean algebra and truth tables to analyze digital systems.
11. Design combinational logic circuits.
12. Explain sequential logic and digital memory.
13. Build conceptual registers, counters, and memory systems.
14. Explain binary arithmetic and signed-number representation.
15. Explain how an ALU works.
16. Explain how registers, buses, ALUs, and control logic form a datapath.
17. Explain the fetch-decode-execute cycle.
18. Understand instruction-set architecture.
19. Design a simple instruction set.
20. Explain machine-code encoding.
21. Read and write assembly language.
22. Explain memory hierarchy and caching.
23. Explain pipelining and CPU performance.
24. Explain hazards, forwarding, branch prediction, and out-of-order execution.
25. Explain processes, threads, virtual memory, system calls, and operating-system interaction with hardware.
26. Explain how compilers translate high-level programs into machine code.
27. Explain lexical analysis, parsing, ASTs, semantic analysis, IR, optimization, and code generation.
28. Explain interpreters, bytecode, virtual machines, JIT compilation, and runtime systems.
29. Compare different programming-language execution models.
30. Build a small computer architecture, assembler, and programming language as a capstone project.
31. Trace a program from source code all the way down to physical transistor activity.

---

# PART 0 — PREREQUISITE MATHEMATICS

## Week 1 — Mathematical Foundations

### Topics

- Number systems
- Natural numbers
- Integers
- Rational numbers
- Real numbers
- Sets
- Functions
- Variables
- Equations
- Algebraic manipulation
- Exponents
- Logarithms
- Scientific notation
- Units and dimensional analysis

### Engineering Mathematics

- Ratios
- Proportions
- Graphs
- Slopes
- Rates of change
- Basic differentiation
- Basic integration

### Why This Matters

Mathematics provides the language used to describe electrical systems, signals, semiconductor behavior, and computational algorithms.

---

# PART I — INFORMATION AND COMPUTATION

## Week 2 — What Is Information?

### Topics

- Data vs information
- Representation
- Physical representation of information
- Analog information
- Digital information
- Continuous vs discrete systems
- Signals
- States
- Bits
- Bytes
- Binary states
- Information encoding
- Noise
- Reliability
- Error tolerance

### Key Question

How can a physical object represent an abstract idea such as a number?

---

## Week 3 — Number Representation

### Topics

- Decimal
- Binary
- Octal
- Hexadecimal
- Base conversion
- Binary arithmetic
- Binary addition
- Binary subtraction
- Binary multiplication
- Binary division
- Bit positions
- Most significant bit
- Least significant bit
- Bitwise representation

### Number Systems

- Unsigned integers
- Signed integers
- Sign-magnitude
- One's complement
- Two's complement
- Overflow
- Underflow
- Fixed-point representation
- Floating-point representation

---

# PART II — ELECTRICITY AND ELECTRONICS

## Week 4 — Fundamentals of Electricity

### Topics

- Electric charge
- Electrons
- Protons
- Electric fields
- Electric potential
- Voltage
- Current
- Resistance
- Conductance
- Power
- Energy
- Ground
- Reference potential

### Laws

- Ohm's Law
- Kirchhoff's Current Law
- Kirchhoff's Voltage Law

### Circuit Concepts

- Open circuit
- Closed circuit
- Short circuit
- Series circuits
- Parallel circuits
- Voltage division
- Current division

---

## Week 5 — Electrical Signals

### Topics

- DC
- AC
- Waveforms
- Frequency
- Period
- Amplitude
- Phase
- Rise time
- Fall time
- Pulse signals
- Square waves
- Clock signals
- Signal propagation
- Noise
- Signal integrity

### Digital Electronics

- Logic-high voltage
- Logic-low voltage
- Noise margins
- Propagation delay
- Switching time

---

# PART III — MATTER AND SEMICONDUCTORS

## Week 6 — Atomic Structure

### Topics

- Atoms
- Protons
- Neutrons
- Electrons
- Atomic number
- Atomic mass
- Electron shells
- Valence electrons
- Electron energy levels
- Chemical bonding

### Key Question

Why does the arrangement of electrons determine whether a material conducts electricity?

---

## Week 7 — Silicon and Crystal Structure

### Topics

- Silicon
- Silicon dioxide
- Quartz
- Silicon crystal lattice
- Covalent bonds
- Valence electrons
- Crystal defects
- Pure/intrinsic silicon
- Electronic-grade silicon
- Silicon purification

### Semiconductor Manufacturing Overview

- Raw silicon
- Polysilicon
- Single-crystal silicon
- Czochralski process
- Silicon ingots
- Wafer slicing
- Wafer polishing

---

## Week 8 — Semiconductor Physics

### Topics

- Conductors
- Insulators
- Semiconductors
- Energy bands
- Valence band
- Conduction band
- Band gap
- Electron-hole pairs
- Thermal energy
- Carrier concentration
- Electron mobility
- Hole mobility

### Semiconductor Behavior

- Temperature dependence
- Electrical conductivity
- Carrier movement
- Recombination

---

## Week 9 — Doping

### Topics

- Intrinsic semiconductor
- Extrinsic semiconductor
- Doping
- Donor atoms
- Acceptor atoms
- Phosphorus
- Boron
- N-type semiconductor
- P-type semiconductor
- Majority carriers
- Minority carriers

### Key Question

How do we deliberately alter silicon so that we can control its electrical behavior?

---

## Week 10 — PN Junctions and Diodes

### Topics

- PN junction
- Diffusion
- Carrier concentration
- Depletion region
- Built-in potential
- Electric field
- Forward bias
- Reverse bias
- Breakdown
- Diode characteristics
- Rectification

### Devices

- Basic diode
- Zener diode
- LED
- Photodiode

---

# PART IV — THE TRANSISTOR

## Week 11 — Introduction to Transistors

### Topics

- What is a transistor?
- Transistor as amplifier
- Transistor as switch
- Bipolar junction transistor
- MOSFET
- BJT vs MOSFET
- Source
- Drain
- Gate
- Body
- Oxide layer

---

## Week 12 — MOSFET Physics

### Topics

- NMOS
- PMOS
- Gate voltage
- Electric field
- Channel formation
- Threshold voltage
- Source-drain current
- Enhancement mode
- Depletion concepts
- Cutoff
- Linear/triode region
- Saturation region

### Key Question

How does applying voltage to one terminal allow us to control current between two other terminals?

---

## Week 13 — CMOS

### Topics

- Complementary MOS
- NMOS pull-down network
- PMOS pull-up network
- CMOS inverter
- Static power
- Dynamic power
- Switching
- Leakage
- Transistor sizing

### Practical Concepts

- Propagation delay
- Fan-out
- Fan-in
- Power-delay tradeoffs

---

# PART V — TRANSISTORS TO LOGIC

## Week 14 — Digital Logic

### Topics

- Logic states
- Truth tables
- Boolean variables
- Boolean functions
- NOT
- AND
- OR
- NAND
- NOR
- XOR
- XNOR

### Gate Implementation

- Transistor-level NOT
- Transistor-level NAND
- Transistor-level NOR
- CMOS gate construction

---

## Week 15 — Boolean Algebra

### Topics

- Boolean expressions
- Boolean identities
- Identity law
- Null law
- Idempotent law
- Complement law
- Involution
- Commutative law
- Associative law
- Distributive law
- Absorption law
- De Morgan's laws

### Circuit Simplification

- Algebraic simplification
- Truth-table simplification
- Karnaugh maps
- Sum of products
- Product of sums

---

## Week 16 — Universal Logic

### Topics

- Functional completeness
- NAND as universal gate
- NOR as universal gate
- Building NOT from NAND
- Building AND from NAND
- Building OR from NAND
- Building NOT from NOR
- Building AND from NOR
- Building OR from NOR

### Major Concept

A sufficiently large collection of simple switches can implement arbitrary digital logic.

---

# PART VI — COMBINATIONAL LOGIC

## Week 17 — Basic Digital Building Blocks

### Topics

- Buffers
- Inverters
- Multiplexers
- Demultiplexers
- Encoders
- Decoders
- Priority encoders
- Comparators

### Applications

- Data selection
- Address decoding
- Control selection
- Routing digital information

---

## Week 18 — Binary Arithmetic Circuits

### Topics

- Half adder
- Full adder
- Carry
- Sum
- Ripple-carry adder
- Carry propagation
- Carry-lookahead concept
- Subtraction circuits
- Adder/subtractor circuits

### Arithmetic

- Binary addition
- Two's-complement subtraction
- Overflow detection

---

## Week 19 — ALU

### Topics

- Arithmetic Logic Unit
- Arithmetic operations
- Logical operations
- Addition
- Subtraction
- AND
- OR
- XOR
- NOT
- Shifts
- Comparisons
- Flags

### Flags

- Zero
- Carry
- Sign
- Overflow
- Negative

---

# PART VII — MEMORY AND STATE

## Week 20 — Sequential Logic

### Topics

- Combinational vs sequential logic
- Feedback
- State
- Clock
- Clocked systems
- Latches
- Flip-flops

### Circuits

- SR latch
- D latch
- D flip-flop
- JK flip-flop
- T flip-flop

---

## Week 21 — Registers and Counters

### Topics

- Registers
- Register width
- Parallel registers
- Shift registers
- Serial-in/serial-out
- Serial-in/parallel-out
- Parallel-in/serial-out
- Counters
- Up counters
- Down counters
- Program counters

---

## Week 22 — Memory Technology

### Topics

- Memory cells
- SRAM
- DRAM
- ROM
- PROM
- EPROM
- EEPROM
- Flash memory

### Memory Concepts

- Address
- Data
- Read
- Write
- Word
- Memory width
- Memory capacity
- Address space
- Memory latency

---

# PART VIII — BUILDING A COMPUTER

## Week 23 — Datapaths

### Topics

- Registers
- Register files
- ALU
- Multiplexers
- Buses
- Data movement
- Register-to-register operations
- Memory-to-register operations

### Build

Design a basic datapath:

```text
Registers → ALU → Registers
     ↑                 ↓
     └──── Memory ─────┘
```

---

## Week 24 — Control Logic

### Topics

- Control signals
- Hardwired control
- Microprogrammed control
- Instruction decoding
- Control sequencing
- Clocked control
- State machines
- Finite state machines

---

## Week 25 — CPU Architecture

### Topics

- CPU components
- ALU
- Registers
- Control unit
- Program Counter
- Instruction Register
- Stack Pointer
- Status register
- Datapath
- Control path
- Memory interface

### CPU Operation

Study:

```text
FETCH
 ↓
DECODE
 ↓
EXECUTE
 ↓
MEMORY ACCESS
 ↓
WRITE BACK
```

---

# PART IX — INSTRUCTION SET ARCHITECTURE

## Week 26 — What Is an ISA?

### Topics

- Instruction Set Architecture
- ISA vs microarchitecture
- Machine instructions
- Opcodes
- Operands
- Registers
- Memory operations
- Control-flow instructions

### ISA Examples

- x86
- x86-64
- ARM
- AArch64
- RISC-V
- MIPS

---

## Week 27 — Instruction Encoding

### Topics

- Instruction formats
- Opcode fields
- Register fields
- Immediate values
- Address fields
- Fixed-length instructions
- Variable-length instructions
- Instruction decoding

### Exercise

Design a custom instruction encoding for your own CPU.

---

## Week 28 — Addressing Modes

### Topics

- Immediate addressing
- Register addressing
- Direct addressing
- Indirect addressing
- Base addressing
- Indexed addressing
- PC-relative addressing
- Stack addressing

---

## Week 29 — Assembly Language

### Topics

- Assembly syntax
- Registers
- Instructions
- Labels
- Directives
- Constants
- Memory operands
- Branches
- Functions
- Stack operations

### Programming Exercises

- Arithmetic
- Loops
- Conditionals
- Arrays
- Functions
- Recursion
- Stack manipulation

---

# PART X — MEMORY HIERARCHY

## Week 30 — Why Memory Is Hierarchical

### Topics

- Latency
- Bandwidth
- Capacity
- Cost
- Locality
- Temporal locality
- Spatial locality

### Hierarchy

```text
Registers
↓
L1 Cache
↓
L2 Cache
↓
L3 Cache
↓
RAM
↓
SSD
↓
Storage
```

---

## Week 31 — CPU Caches

### Topics

- Cache lines
- Cache hits
- Cache misses
- Hit rate
- Miss rate
- Cache latency
- Direct-mapped cache
- Set-associative cache
- Fully associative cache
- Replacement policies
- Write-through
- Write-back
- Write allocation

---

## Week 32 — Virtual Memory

### Topics

- Virtual addresses
- Physical addresses
- Address translation
- Pages
- Page frames
- Page tables
- Multi-level page tables
- Translation Lookaside Buffer
- Page faults
- Memory protection

---

# PART XI — MAKING THE CPU FAST

## Week 33 — CPU Performance

### Topics

- Clock frequency
- Clock cycle
- Instruction latency
- Throughput
- CPI
- IPC
- Benchmarking
- Amdahl's Law
- Critical paths
- Performance vs power

---

## Week 34 — Pipelining

### Topics

- Pipeline stages
- Instruction throughput
- Pipeline latency
- Pipeline registers
- Five-stage pipeline

```text
IF
↓
ID
↓
EX
↓
MEM
↓
WB
```

### Hazards

- Structural hazards
- Data hazards
- Control hazards

---

## Week 35 — Pipeline Solutions

### Topics

- Stalling
- Forwarding
- Hazard detection
- Branch prediction
- Branch penalties
- Pipeline flushing
- Speculative execution

---

## Week 36 — Modern CPU Architecture

### Topics

- Superscalar processors
- Multiple execution units
- Instruction-level parallelism
- Out-of-order execution
- Register renaming
- Reservation stations
- Reorder buffers
- Speculative execution
- SIMD
- Vector processing
- Multicore CPUs
- Simultaneous multithreading

---

# PART XII — THE SOFTWARE-HARDWARE INTERFACE

## Week 37 — Machine Code

### Topics

- Binary instructions
- Instruction encoding
- Machine-code execution
- Opcode decoding
- Registers
- Memory operands
- Branch instructions

### Exercise

Take assembly and manually encode it into machine code.

---

## Week 38 — Assembly and Object Files

### Topics

- Assembler
- Source files
- Object files
- Symbols
- Relocations
- Sections
- Text section
- Data section
- BSS
- Symbol tables

---

## Week 39 — Linking and Executables

### Topics

- Linker
- Static linking
- Dynamic linking
- Libraries
- Shared libraries
- Relocation
- Entry points
- Executable formats

### Formats

- ELF
- PE
- Mach-O

---

# PART XIII — OPERATING SYSTEMS

## Week 40 — Operating System Fundamentals

### Topics

- What an operating system does
- Kernel
- User space
- Kernel space
- Hardware abstraction
- Resource management
- Protection
- Processes
- System calls

---

## Week 41 — Processes and Threads

### Topics

- Process
- Process state
- Process Control Block
- Thread
- User threads
- Kernel threads
- Context switching
- Scheduling

### Scheduling

- FCFS
- Round Robin
- Priority scheduling
- Multilevel queues

---

## Week 42 — System Calls

### Topics

- User programs
- System calls
- Privilege levels
- Traps
- Interrupts
- Exceptions
- Kernel entry
- Return to user space

### Examples

Study conceptually:

```text
open()
read()
write()
fork()
exec()
mmap()
```

---

## Week 43 — Interrupts and I/O

### Topics

- Hardware interrupts
- Software interrupts
- Exceptions
- Interrupt controllers
- Device drivers
- Memory-mapped I/O
- Port I/O
- DMA
- Buffers

---

## Week 44 — Memory Management

### Topics

- Stack
- Heap
- Static memory
- Dynamic allocation
- Virtual memory
- Paging
- Memory protection
- Shared memory
- Memory-mapped files

---

# PART XIV — PROGRAMMING LANGUAGES

## Week 45 — What Is a Programming Language?

### Topics

- Syntax
- Semantics
- Grammar
- Tokens
- Expressions
- Statements
- Variables
- Functions
- Types
- Scope
- Lifetime
- Evaluation

---

## Week 46 — Type Systems

### Topics

- Static typing
- Dynamic typing
- Strong vs weak typing
- Type inference
- Primitive types
- Composite types
- Generics
- Polymorphism
- Type checking
- Type safety

### Compare

```text
C
Rust
Java
Python
JavaScript
```

---

# PART XV — COMPILERS

## Week 47 — Compiler Architecture

### Topics

```text
Source Code
 ↓
Lexical Analysis
 ↓
Parsing
 ↓
AST
 ↓
Semantic Analysis
 ↓
Intermediate Representation
 ↓
Optimization
 ↓
Code Generation
 ↓
Assembly
 ↓
Machine Code
```

---

## Week 48 — Lexical Analysis

### Topics

- Characters
- Tokens
- Lexemes
- Keywords
- Identifiers
- Operators
- Literals
- Whitespace
- Comments
- Regular expressions
- Finite automata

### Project

Build a basic lexer.

---

## Week 49 — Parsing

### Topics

- Grammar
- Context-free grammar
- Parse trees
- Abstract Syntax Trees
- Recursive descent parsing
- Operator precedence
- Associativity

### Project

Build a parser for a tiny language.

---

## Week 50 — Semantic Analysis

### Topics

- Type checking
- Symbol tables
- Scope resolution
- Name resolution
- Function validation
- Variable declarations
- Type compatibility
- Semantic errors

---

## Week 51 — Intermediate Representation

### Topics

- Why compilers use IR
- Three-address code
- SSA
- Basic blocks
- Control-flow graphs
- Data-flow concepts

Example:

```text
t1 = b * 2
t2 = a + t1
x = t2
```

---

## Week 52 — Compiler Optimization

### Topics

- Constant folding
- Constant propagation
- Dead-code elimination
- Common-subexpression elimination
- Strength reduction
- Inlining
- Loop optimization
- Register allocation
- Instruction selection

---

## Week 53 — Code Generation

### Topics

- Target architecture
- Instruction selection
- Register allocation
- Calling conventions
- Stack frames
- Function prologues
- Function epilogues
- Assembly generation
- Machine-code generation

---

# PART XVI — INTERPRETERS AND RUNTIMES

## Week 54 — Interpreters

### Topics

- Interpretation
- AST interpreters
- Tree-walk interpreters
- Bytecode interpreters
- Runtime environments
- Environments
- Closures
- Function calls

---

## Week 55 — Virtual Machines

### Topics

- Virtual machines
- Bytecode
- Virtual registers
- Stack machines
- Register machines
- VM instruction sets
- Runtime systems

---

## Week 56 — JIT Compilation

### Topics

- Just-in-time compilation
- Profiling
- Hot code
- Runtime optimization
- Speculative optimization
- Deoptimization
- Inline caching

### Example Architecture

```text
JavaScript
 ↓
Parser
 ↓
AST
 ↓
Bytecode
 ↓
Interpreter
 ↓
Profiler
 ↓
JIT Compiler
 ↓
Machine Code
 ↓
CPU
```

---

# PART XVII — LANGUAGE RUNTIME SYSTEMS

## Week 57 — Memory Management

### Topics

- Manual memory management
- Stack allocation
- Heap allocation
- Allocators
- Garbage collection
- Reference counting
- Mark-and-sweep
- Generational GC
- Ownership
- Borrowing

---

## Week 58 — Function Calls

### Topics

- Calling conventions
- Arguments
- Return values
- Stack frames
- Call stack
- Registers
- Caller-saved registers
- Callee-saved registers
- Function prologue
- Function epilogue
- Recursion

---

# PART XVIII — COMPLETE TRACE

## Week 59 — From Source Code to CPU

Take:

```c
int x = 5 + 3;
```

Trace it through:

```text
Source Code
 ↓
Lexer
 ↓
Parser
 ↓
AST
 ↓
Semantic Analysis
 ↓
IR
 ↓
Optimization
 ↓
Assembly
 ↓
Machine Code
 ↓
Executable
 ↓
Operating System
 ↓
Process
 ↓
Virtual Memory
 ↓
CPU
 ↓
Instruction Decoder
 ↓
Control Signals
 ↓
Registers
 ↓
ALU
 ↓
Logic Gates
 ↓
Transistors
 ↓
Electrical Signals
 ↓
Semiconductor Physics
```

---

# PART XIX — BUILD YOUR OWN COMPUTER

## Week 60 — Design a CPU

### Project: PRIME-1

Design a custom CPU.

### Specifications

Decide:

- Word size
- Number of registers
- Instruction size
- Memory size
- Address width
- ALU operations
- Branch instructions
- Load/store instructions
- Stack architecture
- Calling convention

---

## Week 61 — Design PRIME-1 ISA

Create instructions for:

### Data movement

- LOAD
- STORE
- MOV

### Arithmetic

- ADD
- SUB
- MUL

### Logic

- AND
- OR
- XOR
- NOT

### Control flow

- JMP
- JZ
- JNZ
- CALL
- RET

### System

- HALT
- NOP

Define the exact binary encoding.

---

## Week 62 — Build the CPU

Implement conceptually or using HDL:

- Registers
- Program counter
- Instruction register
- ALU
- Control unit
- Memory
- Bus
- Clock
- Instruction decoder

Possible tools:

- Logisim
- Digital
- Verilog
- SystemVerilog
- VHDL
- FPGA

---

# PART XX — BUILD YOUR OWN SOFTWARE STACK

## Week 63 — Build an Assembler

Create:

```text
PRIME-1 Assembly
       ↓
Assembler
       ↓
PRIME-1 Machine Code
```

Features:

- Labels
- Opcodes
- Registers
- Constants
- Addresses
- Error reporting

---

## Week 64 — Build a Virtual Machine

Before or alongside physical/HDL hardware, create a software emulator:

```text
PRIME-1 Machine Code
        ↓
PRIME-1 Emulator
        ↓
Your computer
```

The emulator should simulate:

- Registers
- Memory
- Program counter
- ALU
- Instructions
- Flags
- CPU cycles

---

## Week 65 — Build a Programming Language

Create a tiny language.

Example:

```text
let x = 5;
let y = 3;

let z = x + y;

print(z);
```

Design:

- Syntax
- Keywords
- Types
- Variables
- Expressions
- Statements
- Functions

---

## Week 66 — Compile Your Language

Build:

```text
Your Language
      ↓
Lexer
      ↓
Parser
      ↓
AST
      ↓
Semantic Analysis
      ↓
IR
      ↓
PRIME-1 Assembly
      ↓
Assembler
      ↓
PRIME-1 Machine Code
      ↓
PRIME-1 CPU
```

---

# PART XXI — FINAL INTEGRATION

## Week 67 — Full System Integration

The final goal is to demonstrate:

```text
                HUMAN
                  ↓
        HIGH-LEVEL PROGRAM
                  ↓
             COMPILER
                  ↓
          INTERMEDIATE CODE
                  ↓
             ASSEMBLY
                  ↓
           MACHINE CODE
                  ↓
                ISA
                  ↓
              CPU
        ┌─────────┴─────────┐
        ↓                   ↓
       ALU              REGISTERS
        ↓                   ↓
    LOGIC GATES        MEMORY SYSTEM
        ↓                   ↓
    TRANSISTORS       MEMORY CELLS
        ↓                   ↓
      SILICON ←→ ELECTRICAL SIGNALS
                  ↓
              PHYSICS
```

### Final Demonstration

Write one simple program in your custom language.

Compile it.

Assemble it.

Load it into your CPU/emulator.

Execute it.

Then trace one instruction manually from:

**source code → compiler → assembly → machine code → instruction decoder → control signals → registers → ALU → logic gates → transistors.**

---

# FINAL PROJECT

## "Build a Computer From First Principles"

The student should produce:

### 1. A CPU architecture document

- Block diagram
- Datapath
- Control unit
- Registers
- ALU
- Memory interface
- Clocking model

### 2. An ISA specification

- Instructions
- Opcodes
- Encodings
- Registers
- Addressing modes
- Memory model

### 3. A CPU implementation

- Logic simulator, HDL, FPGA, or physical implementation

### 4. An assembler

- Assembly parser
- Symbol resolution
- Machine-code generator

### 5. A CPU emulator

- Instruction execution
- Memory simulation
- Registers
- Debugging tools

### 6. A compiler

- Lexer
- Parser
- AST
- Semantic analyzer
- IR
- Code generator

### 7. A tiny programming language

- Syntax
- Semantics
- Types
- Variables
- Functions
- Control flow

### 8. Final technical report

The report must explain the complete stack:

**Physics → Semiconductor → Transistor → CMOS → Logic → Digital Circuits → Memory → ALU → Datapath → Control → CPU → ISA → Machine Code → Assembly → Compiler → Runtime → Operating System → Programming Language.**

---

# MASTER CONCEPT MAP

The entire course can ultimately be remembered as this:

```text
PHYSICS
│
├── Electromagnetism
│
↓
MATTER
│
├── Atoms
├── Electrons
└── Crystal structures
│
↓
SEMICONDUCTORS
│
├── Silicon
├── Doping
├── P-type
└── N-type
│
↓
PN JUNCTIONS
│
↓
TRANSISTORS
│
├── NMOS
├── PMOS
└── CMOS
│
↓
LOGIC GATES
│
├── NOT
├── AND
├── OR
├── NAND
├── NOR
└── XOR
│
↓
DIGITAL CIRCUITS
│
├── Multiplexers
├── Decoders
├── Adders
├── Comparators
└── Shifters
│
├─────────────────┐
↓                 ↓
SEQUENTIAL       COMBINATIONAL
LOGIC             LOGIC
│                 │
├── Latches       └── ALU
├── Flip-flops
├── Registers
└── Counters
│
↓
DATAPATH
│
├── Registers
├── ALU
├── Buses
└── Memory interface
│
↓
CONTROL UNIT
│
↓
CPU
│
├── Program Counter
├── Instruction Register
├── Registers
├── ALU
└── Control Logic
│
↓
ISA
│
↓
MACHINE CODE
│
↓
ASSEMBLY
│
↓
ASSEMBLER
│
↓
OBJECT CODE
│
↓
LINKER
│
↓
EXECUTABLE
│
↓
OPERATING SYSTEM
│
├── Processes
├── Threads
├── Memory
├── System calls
├── Drivers
└── I/O
│
↓
RUNTIME
│
├── Libraries
├── VM
├── Garbage collector
└── JIT
│
↓
COMPILER / INTERPRETER
│
├── Lexer
├── Parser
├── AST
├── Semantic analysis
├── IR
├── Optimization
└── Code generation
│
↓
PROGRAMMING LANGUAGE
│
↓
HUMAN IDEAS
```

# CORE PRINCIPLE OF THE COURSE

At every stage, ask three questions:

### 1. What is physically happening?

For example:

> What are the electrons doing?

### 2. What abstraction have we created?

For example:

> We don't care about individual electrons anymore; we call the resulting behavior a transistor.

### 3. What does the next layer build from it?

For example:

> Transistors become logic gates, which become arithmetic circuits, which become ALUs.

The ultimate goal is not merely to know the hierarchy.

It is to understand **why every layer can exist**.

---

# RECOMMENDED STUDY RULE

Do not move to the next module until you can explain the current one **without looking at your notes**.

For each major concept:

**Understand → Draw → Derive → Build → Explain → Connect.**

If you cannot explain why a NAND gate works from its transistor arrangement, don't simply memorize NAND.

Go back down.

If you cannot explain how an ALU performs addition, go back to the full adder.

If you cannot explain how the CPU executes ADD, go back to the datapath and control unit.

If you cannot explain how the instruction exists physically, go back to logic gates and transistors.

This is a **bottom-up systems-engineering course**, not a vocabulary course.
