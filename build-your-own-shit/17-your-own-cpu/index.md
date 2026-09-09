# Build Your Own CPU — PRIME-1

**[Advanced]** — Design an instruction set, build the processor that executes it four different ways, then write the assembler, emulator and compiler that target it. **The only guide here that starts below software.**

Every other guide in this folder builds something *on top of* a computer. This one builds the computer.

> **Why four tracks?** A CPU is the one artefact where the medium changes what you learn. Wiring gates in a simulator teaches you what a datapath *is*; writing Verilog teaches you how hardware is actually described; a Python emulator teaches you what an ISA *means*; a breadboard teaches you that all of it is physical. **They are not alternatives. They are four passes over the same design**, each cheap once you have done the previous one.

## What you're building

**PRIME-1** — a 16-bit processor with 8 registers, 16 instructions, and 64 KB of addressable memory. Small enough to fit on one page, big enough to run real programs.

By the end you will have:

1. An **ISA specification** — the contract between your hardware and your software
2. A **working processor**, built four ways
3. An **assembler** turning `ADD R1, R2, R3` into `0001 001 010 011 000`
4. An **emulator** with a debugger, so you can single-step your own machine
5. A **compiler** for a small language, targeting your own instruction set
6. A program you wrote, in a language you designed, compiled by your compiler, running on your processor

**What you're deliberately not building:** pipelining, caches, interrupts, virtual memory, or an operating system. Those are [[foundations/computer-architecture/index|computer-architecture/]] and [[build-your-own-shit/05-your-own-os|your own OS]]. PRIME-1 is a *correct* processor, not a fast one — and getting a correct one running is the lesson.

## What you need first

**Required — from [[how-computers-work/index|How Computers Work]]:**

| You need | From |
| :--- | :--- |
| Gates from transistors | [[how-computers-work/04-logic/01-gates-from-transistors\|module 15]] |
| Adders and the carry chain | [[how-computers-work/05-combinational/02-adders\|module 20]] |
| Multiplexers and decoders | [[how-computers-work/05-combinational/01-multiplexers-and-decoders\|module 19]] |
| The ALU | [[how-computers-work/05-combinational/04-the-alu\|module 22]] |
| Flip-flops and setup/hold | [[how-computers-work/06-memory/01-latches-and-flip-flops\|module 23]] |
| Register files and the program counter | [[how-computers-work/06-memory/02-registers-and-counters\|module 24]] |

**If you have not done those, do them first.** This guide assumes you can build an ALU and a register file, and spends its time on what happens *above* them.

**Helpful:** any programming language for the emulator and assembler tracks. Python is used in the examples.

**Honest note on what's missing:** the vault has no HDL course. Track 2 teaches enough Verilog inline to build PRIME-1, but it is not a Verilog tutorial — it is a CPU guide that happens to use Verilog.

## The four tracks

| Track | You produce | Time | What it teaches that others don't |
| :--- | :--- | :--- | :--- |
| **[[build-your-own-shit/17-your-own-cpu/01-digital-simulator\|1 — Digital simulator]]** | A clickable circuit | A weekend | **What a datapath physically is.** You see the buses light up and can single-step the clock |
| **[[build-your-own-shit/17-your-own-cpu/02-verilog\|2 — Verilog]]** | Synthesisable HDL | 2–3 evenings | How hardware is really described and verified. Runs on an FPGA if you have one |
| **[[build-your-own-shit/17-your-own-cpu/03-python-emulator\|3 — Python emulator]]** | An emulator + debugger | One evening | **What an ISA means** as a contract, independent of any implementation |
| **[[build-your-own-shit/17-your-own-cpu/04-breadboard\|4 — Breadboard]]** | A physical machine | Weeks | That all of it is voltages on wires. Unforgettable, and slow |

**Suggested order: 3 → 1 → 2 → 4.**

Write the emulator first. It is one evening, it makes the ISA concrete, and — crucially — **it becomes the reference implementation you test the other three against.** When your circuit disagrees with your emulator on instruction 47, you have a test case rather than a mystery.

Then build the circuit to see it, then Verilog to describe it properly, then breadboard it if you want to touch it.

---

## The PRIME-1 specification

**All four tracks implement exactly this.** Keep this page open while you build.

### Machine state

```
   8 registers, 16 bits each:  R0 R1 R2 R3 R4 R5 R6 R7
                               ^^
                               R0 is HARDWIRED TO ZERO -- writes are discarded

   PC          16-bit program counter
   FLAGS       Z (zero), N (negative), C (carry), V (overflow)
   Memory      65,536 words of 16 bits, word-addressed
```

**Why R0 = 0 is worth one register:** it makes `MOV rd, ra` into `ADD rd, ra, R0`, comparison-against-zero free, and `NOP` into `ADD R0, R0, R0`. One hardwired constant removes several instruction formats. RISC-V and MIPS both do this.

### Instruction formats

Every instruction is exactly **16 bits**. Three formats:

```
   R-type   [ op:4 ][ rd:3 ][ ra:3 ][ rb:3 ][ fn:3 ]     register-register
   I-type   [ op:4 ][ rd:3 ][ ra:3 ][   imm:6      ]     immediate / memory
   J-type   [ op:4 ][          addr:12             ]     jumps
```

Fixed width means **the decoder is trivial and the PC always advances by 1.** Variable-length encoding (as on x86) buys code density and costs a much harder decoder — a tradeoff worth understanding, and the wrong one for a first CPU.

### Instruction set

| Op | Mnemonic | Format | Operation |
| :--- | :--- | :--- | :--- |
| `0000` | `NOP` | — | do nothing |
| `0001` | `ADD rd, ra, rb` | R | `rd = ra + rb` |
| `0010` | `SUB rd, ra, rb` | R | `rd = ra - rb` |
| `0011` | `AND rd, ra, rb` | R | `rd = ra & rb` |
| `0100` | `OR  rd, ra, rb` | R | `rd = ra \| rb` |
| `0101` | `XOR rd, ra, rb` | R | `rd = ra ^ rb` |
| `0110` | `SHL rd, ra, rb` | R | `rd = ra << rb` |
| `0111` | `SHR rd, ra, rb` | R | `rd = ra >> rb` |
| `1000` | `SLT rd, ra, rb` | R | `rd = 1 if ra < rb else 0` (signed) |
| `1001` | `LDI rd, imm` | I | `rd = sign_extend(imm)` |
| `1010` | `LD  rd, ra, imm` | I | `rd = mem[ra + imm]` |
| `1011` | `ST  rd, ra, imm` | I | `mem[ra + imm] = rd` |
| `1100` | `BEZ ra, imm` | I | `if ra == 0: PC += imm` (signed, PC-relative) |
| `1101` | `BNZ ra, imm` | I | `if ra != 0: PC += imm` |
| `1110` | `JMP addr` | J | `PC = addr` |
| `1111` | `JAL addr` | J | `R7 = PC + 1; PC = addr` |

**`JAL` writes the return address into R7**, which makes function calls work: call with `JAL`, return with `ADD PC, R7, R0`... except PC is not a register here, so **return is `JR`** — implemented as `JMP` through a register. For simplicity PRIME-1 uses `BEZ R0, R7` as its return idiom, since R0 is always zero so the branch always taken, offset from R7.

> [!NOTE]
> **That last paragraph is deliberately awkward, and you should fix it.**
>
> Designing an ISA means discovering these gaps. PRIME-1 as specified has no clean register-indirect jump, which makes `return` clumsy. **Your first real design decision is how to add one** — spend an opcode on `JR ra`, or repurpose an R-type function code.
>
> [[how-computers-work/08-capstone/02-the-isa|Capstone module 28]] works through this and several other decisions properly. If you are following the course, do that module before building. If you are here for the build, just add `JR` and move on — it is your ISA.

### Execution cycle

```
   FETCH     IR = mem[PC];  PC = PC + 1
      ↓
   DECODE    split IR into op / rd / ra / rb / imm
      ↓
   EXECUTE   ALU computes; or address is calculated
      ↓
   MEMORY    load or store, if this instruction needs it
      ↓
   WRITEBACK result -> register file (unless rd is R0)
```

**PC increments during fetch, before execution.** So a branch offset is relative to the *next* instruction, not the current one. This trips everyone up once; get it right in the emulator and the other tracks inherit it.

### The reference program

Every track must run this. It sums the integers 1 to 10 and halts with the answer in R1.

```asm
        LDI  R1, 0          ; sum = 0
        LDI  R2, 10         ; i = 10
loop:   ADD  R1, R1, R2     ; sum += i
        LDI  R3, 1
        SUB  R2, R2, R3     ; i -= 1
        BNZ  R2, loop       ; repeat while i != 0
halt:   JMP  halt           ; spin forever
```

**Expected result: R1 = 55.** If your build produces 55, your datapath, control logic, ALU, register file, branch logic and memory all work. It is a remarkably thorough test for six lines.

---

## The build order

Whichever track you take, build in this sequence. **Each milestone runs.**

1. **Fetch only.** PC increments, memory is read, IR loads. Run a memory full of `NOP` and watch the PC count. *You now have a machine that goes.*
2. **Decode.** Split the IR into fields and light them up / print them. No execution yet.
3. **ALU ops.** Wire the register file and ALU. Execute `ADD`, `SUB`, `AND`, `OR`, `XOR`. *Your CPU computes.*
4. **Immediates.** Add `LDI`. Now you can get constants into registers without pre-loading memory.
5. **Memory.** Add `LD` and `ST`. *Your CPU has state beyond its registers.*
6. **Branches.** Add `BEZ` and `BNZ`. **This is the milestone that matters** — your machine can now loop, and it is Turing-complete in practice.
7. **Jumps and calls.** `JMP`, `JAL`, and whatever you chose for `JR`.
8. **Run the reference program.** Get 55.

**Do not skip step 1 to "save time".** A machine that fetches and does nothing else is 20 minutes of work and eliminates half the possible bugs in every later step.

## The parts that will bite you

- **Off-by-one on the PC.** Branch offsets are relative to PC-after-increment. Decide once, write it in your spec, and make the emulator authoritative.
- **Sign extension.** A 6-bit immediate of `111111` is $-1$, not 63. Forgetting this makes backward branches jump forward into nothing.
- **R0 writes.** If R0 is not genuinely hardwired, `NOP` (`ADD R0,R0,R0`) silently corrupts it and everything drifts.
- **Read-during-write.** In one cycle, the register file is read *before* the write lands ([[how-computers-work/06-memory/02-registers-and-counters|module 24]]). `ADD R1, R1, R2` must use the old R1.
- **Clock edges in simulators.** A gate loop with no flip-flop will oscillate. If your simulator hangs, you have made a combinational loop.
- **Word vs byte addressing.** PRIME-1 is word-addressed: `mem[5]` is the sixth 16-bit word, not byte 5. Mixing this up corrupts every load.

## How to know it works

**The emulator is your oracle.** Write it first, test it hard, then diff every other track against it:

1. **Per-instruction tests.** For each of the 16 opcodes, set up registers, execute one instruction, assert the result and flags.
2. **The reference program.** R1 = 55.
3. **Differential testing.** Generate random instruction sequences, run them on the emulator and on your circuit, compare register dumps after every cycle. **This finds the bugs staring at waveforms never will.**
4. **Edge cases.** Overflow, negative immediates, branch to self, write to R0, load from address 0.

## Where to stop

**Stop when the reference program prints 55 on at least two tracks.** That is a complete, working computer of your own design.

**Worth continuing to:** the assembler (it makes writing test programs bearable), then a compiler for a tiny language — that is where the two halves of [[how-computers-work/index|How Computers Work]] finally meet.

**Not worth it here:** pipelining, caches or superscalar execution. They are the subject of [[foundations/computer-architecture/index|computer-architecture/]], and bolting them onto a first CPU teaches less than reading about them and building a second one later.

## Related

- [[how-computers-work/index|How Computers Work]] — the course this is the capstone of
- [[build-your-own-shit/04-your-own-language|Your Own Language]] — the compiler that will target PRIME-1
- [[build-your-own-shit/05-your-own-os|Your Own OS]] — what runs on a *real* CPU
- [[foundations/computer-architecture/index|computer-architecture/]] — pipelining, caches, and everything PRIME-1 leaves out
- [[build-your-own-shit/index|Build Your Own Shit index]]
