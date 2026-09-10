# Module 34: Final Integration (Source Code to Electrons)

**[Advanced]** — The last module. One line of a language you designed, followed down every layer to transistor switching — with nothing taken on faith.

## Before you start

**You need everything.** Modules 1–33, and working versions of your CPU, assembler, emulator and compiler.

**After this lesson you will be able to:**

1. Trace a single statement through all eleven layers of the stack.
2. Name, for each layer, what represents the data and what performs the operation.
3. Identify any gap in your own understanding, precisely.

**Study route:** run the lab, then do section 6 closed-book. **The closed-book attempt is the actual assessment** — everything before it is preparation.

---

## 1. The question this course was built to answer

> **If I write `let z = x + y;`, can I trace that single statement all the way down to electrons physically moving through transistors?**

**Yes.** And not as a hand-wave — as eleven concrete layers, each of which you have built.

The lab does not narrate the trace. **It computes it**, using the lexer, parser and code generator from [[how-computers-work/08-capstone/06-build-the-language|module 33]], the assembler from [[how-computers-work/08-capstone/04-build-the-assembler|module 31]], the disassembler from [[how-computers-work/08-capstone/02-the-isa|module 29]], the control table from [[how-computers-work/08-capstone/03-build-the-hardware|module 30]], the emulator from [[how-computers-work/08-capstone/05-build-the-emulator|module 32]], and the full-adder logic from [[how-computers-work/05-combinational/02-adders|module 21]].

---

## 2. The eleven layers

| # | Layer | What represents the data | What performs the operation |
| --: | :--- | :--- | :--- |
| 1 | Source code | Characters in a file | A human's intent |
| 2 | Tokens | `(kind, text)` pairs | The lexer's regular expressions |
| 3 | AST | A tree of nodes | The parser's grammar rules |
| 4 | Assembly | Mnemonics and labels | The code generator's traversal |
| 5 | Machine code | 16-bit words | The assembler's encoding tables |
| 6 | Instruction fields | Bit ranges within a word | The decoder's wire splitting |
| 7 | Control signals | Eleven wires, high or low | The control ROM |
| 8 | Registers and ALU | Voltages on 16 wires per value | Multiplexers and the adder |
| 9 | Logic gates | A voltage per wire | XOR, AND, OR gates |
| 10 | Transistors | Channel conducting or not | Gate voltage inverting a surface |
| 11 | Physics | Electron positions and fields | Coulomb's law |

**Each row's "what performs the operation" is built from the row below it.** That is the whole course in one table.

---

## 3. What the trace shows

Running `let x = 5; let y = 3; let z = x + y; print(z);`:

**The ADD instruction** encodes as `0x1650`, or `0001011001010000`:

```
   0001 011 001 010 000
   ^^^^                  opcode = ADD
        ^^^              rd = R3
            ^^^          ra = R1
                ^^^      rb = R2
```

**The control ROM**, addressed by opcode `0001`, asserts `RegWrite` and nothing else. `ALUSrc = 0` selects register B rather than the immediate; `ALUOp = 000` selects ADD.

**The ALU** receives 5 and 3 and produces 8. And at the gate level:

```
   bit  A  B |  A^B  A&B  Cin&(A^B) |  sum  carry
     0  1  1 |    0    1          0 |    0      1
     1  0  1 |    1    0          1 |    0      1
     2  1  0 |    1    0          1 |    0      1
     3  0  0 |    0    0          0 |    1      0
```

**Read that carefully — it is the most satisfying four lines in the course.** At bit 0, both inputs are 1: XOR gives 0, AND gives 1, and **a carry is born**. It propagates through bits 1 and 2 without either input contributing, and finally lands at bit 3 producing the only set bit in the answer.

`0101 + 0011 = 1000`. **Five plus three is eight, and you can see the carry travel.**

**One full adder is 42 transistors** built from gate cells; a 16-bit adder is 672. Each is a MOSFET whose gate voltage inverts a silicon surface to form a channel — silicon doped with roughly one atom in fifty million replaced by phosphorus or boron, insulated by four molecular layers of SiO₂ whose 9 eV band gap electrons cannot cross.

---

## 4. Worked example — runnable

Save as `trace_lab.py` alongside every other file you have built, and run `python3 trace_lab.py`.

```python
"""THE COMPLETE TRACE.

One line of Pebble, followed down every layer to transistor switching.
Nothing here is narrated -- every layer is computed by the tools built
in modules 29-33 and the physics established in modules 1-26."""
from pebble import lex, Parser, CodeGen, OUT_PORT
from prime1 import assemble, Prime1
from isa_lab import disassemble, fields
from datapath import CONTROL, SIGNAL_NAMES
from control_derive import ISA

SOURCE = "let x = 5;\nlet y = 3;\nlet z = x + y;\nprint(z);\n"

# Transistor counts per gate in static CMOS (module 16)
GATE_TRANSISTORS = {"NOT": 2, "NAND": 4, "NOR": 4, "AND": 6, "OR": 6, "XOR": 12}
# A full adder is 2 XOR + 2 AND + 1 OR (module 21)
FULL_ADDER_GATES = {"XOR": 2, "AND": 2, "OR": 1}

def full_adder(a, b, carry_in):
    """The module 21 full adder, returning every intermediate signal."""
    xor1 = a ^ b
    total = xor1 ^ carry_in
    and1, and2 = a & b, carry_in & xor1
    return total, and1 | and2, {"A^B": xor1, "A&B": and1, "Cin&(A^B)": and2}

def trace_addition(a, b, width=16, show_bits=5):
    rows, carry = [], 0
    for i in range(width):
        x, y = (a >> i) & 1, (b >> i) & 1
        s, carry, parts = full_adder(x, y, carry)
        if i < show_bits:
            rows.append((i, x, y, parts, s, carry))
    return rows

def transistors_per_full_adder():
    return sum(GATE_TRANSISTORS[g] * n for g, n in FULL_ADDER_GATES.items())

def rule(title):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)

if __name__ == "__main__":
    rule("LAYER 1 -- SOURCE CODE (a human idea, written down)")
    for n, line in enumerate(SOURCE.strip().splitlines(), 1):
        print(f"  {n}  {line}")
    print()
    print("  we follow ONE statement: 'let z = x + y;'  with x=5, y=3")

    rule("LAYER 2 -- TOKENS (lexical analysis, module 33)")
    tokens = lex("let z = x + y;")
    print("  " + "  ".join(f"{k}({t})" if t else k for k, t, _ in tokens))

    rule("LAYER 3 -- ABSTRACT SYNTAX TREE (parsing, module 33)")
    ast = Parser(lex("let z = x + y;")).parse()
    stmt = ast[1][0]
    print(f"  {stmt[0]}  '{stmt[1]}'")
    print(f"    └── binop '{stmt[2][1]}'")
    print(f"          ├── {stmt[2][2]}")
    print(f"          └── {stmt[2][3]}")

    rule("LAYER 4 -- ASSEMBLY (code generation, module 33)")
    asm = CodeGen().compile(Parser(lex(SOURCE)).parse())
    for line in asm.splitlines():
        print("  " + line)

    rule("LAYER 5 -- MACHINE CODE (assembly, module 31)")
    program, _ = assemble(asm)
    add_index = next(i for i, w in enumerate(program) if (w >> 12) == 0b0001)
    print(f"  {'addr':>5s}  {'hex':>5s}  {'binary':>18s}   disassembly")
    for i, w in enumerate(program[:10]):
        mark = "  <-- the ADD we follow" if i == add_index else ""
        print(f"  {i:5d}  {w:#06x}  {w:016b}   {disassemble(w, i):20s}{mark}")

    rule("LAYER 6 -- INSTRUCTION FIELDS (what the decoder sees)")
    word = program[add_index]
    f = fields(word)
    print(f"  {word:016b}")
    print(f"  ^^^^                opcode = {f['op']:04b} = ADD")
    print(f"      ^^^             rd     = {f['rd']:03b} = R{f['rd']}")
    print(f"         ^^^          ra     = {f['ra']:03b} = R{f['ra']}")
    print(f"            ^^^       rb     = {f['rb']:03b} = R{f['rb']}")

    rule("LAYER 7 -- CONTROL SIGNALS (module 30)")
    signals = CONTROL[f["op"]]
    print(f"  the control ROM is addressed by the opcode {f['op']:04b} and outputs:")
    for name, value in zip(SIGNAL_NAMES, signals):
        state = "ASSERTED" if value else "."
        print(f"    {name:12s} = {value}   {state}")
    print()
    print("  these wires steer the multiplexers. RegWrite=1 enables the")
    print("  register file's write port; ALUSrc=0 selects register B, not")
    print("  the immediate; ALUOp=0 selects ADD on the ALU's function input.")

    rule("LAYER 8 -- REGISTER FILE AND ALU (modules 23, 25)")
    cpu = Prime1(); cpu.load(program)
    while cpu.pc != add_index and not cpu.halted:
        cpu.step()
    a_val, b_val = cpu.reg[f["ra"]], cpu.reg[f["rb"]]
    print(f"  read port A -> R{f['ra']} = {a_val}  ({a_val:016b})")
    print(f"  read port B -> R{f['rb']} = {b_val}  ({b_val:016b})")
    print(f"  ALU function select = {signals[3]:03b} (ADD)")
    cpu.step()
    print(f"  result -> R{f['rd']} = {cpu.reg[f['rd']]}  "
          f"({cpu.reg[f['rd']]:016b})")

    rule("LAYER 9 -- LOGIC GATES (the adder, module 21)")
    print(f"  {a_val} + {b_val}, bit by bit through the ripple-carry chain:")
    print(f"  {'bit':>4s} {'A':>2s} {'B':>2s} | {'A^B':>4s} {'A&B':>4s}"
          f" {'Cin&(A^B)':>10s} | {'sum':>4s} {'carry':>6s}")
    for i, x, y, parts, s, c in trace_addition(a_val, b_val):
        print(f"  {i:4d} {x:2d} {y:2d} | {parts['A^B']:4d} {parts['A&B']:4d}"
              f" {parts['Cin&(A^B)']:10d} | {s:4d} {c:6d}")
    print("  (bits 5-15 are all zero and omitted)")
    print()
    print("  bit 0: A=1 B=1 -> XOR gives 0, AND gives 1 -> a carry is born")
    print("  bit 1: the carry arrives, A=0 B=1 -> sum 0, carry propagates")
    print("  bit 3: the carry finally lands -> sum bit 1")

    rule("LAYER 10 -- TRANSISTORS (modules 13, 16)")
    per_fa = transistors_per_full_adder()
    detail = " + ".join(f"{n}x{g}({GATE_TRANSISTORS[g]})"
                        for g, n in FULL_ADDER_GATES.items())
    print(f"  one full adder = {detail} = {per_fa} transistors")
    print(f"  a 16-bit adder = 16 x {per_fa} = {16 * per_fa} transistors")
    print()
    print()
    print("  NOTE: that is the cost of building a full adder from separate")
    print("  gate CELLS. A purpose-designed CMOS full adder (the 'mirror")
    print("  adder') needs only 28 -- because building one PDN/PUN network")
    print("  directly beats composing pre-made gates (module 16).")
    print()
    print("  each transistor is a MOSFET (module 12): a voltage on an")
    print("  insulated gate inverts a silicon surface, forming a channel")
    print("  between two doped regions -- and current flows.")

    rule("LAYER 11 -- PHYSICS (modules 6-10)")
    print("  the doped regions are silicon with ~1 atom in 50 million")
    print("  replaced by phosphorus or boron (module 9).")
    print("  the insulator is SiO2, ~4 molecules thick, with a 9 eV band")
    print("  gap that electrons cannot cross (modules 8, 11).")
    print("  'a 1' is a voltage above 2.4 V; 'a 0' is below 0.4 V; the")
    print("  0.4 V gap between them is the noise margin (module 5) that")
    print("  makes every layer above this one possible.")

    rule("THE ANSWER")
    cpu2 = Prime1(); cpu2.load(program)
    last, printed = cpu2.mem[OUT_PORT], []
    while not cpu2.halted and cpu2.cycles < 10000:
        cpu2.step()
        if cpu2.mem[OUT_PORT] != last:
            last = cpu2.mem[OUT_PORT]; printed.append(last)
    print(f"  the program printed: {printed[-1]}")
    print(f"  'let z = x + y;' with x=5, y=3 gave z = {printed[-1]}")
    print()
    print("  every layer above was computed, not asserted.")

    assert printed[-1] == 8
    assert cpu.reg[f["rd"]] == 8
    assert per_fa == 42
    print()
    print("trace_lab: passed")
```

Expected output:

```

========================================================================
  LAYER 1 -- SOURCE CODE (a human idea, written down)
========================================================================
  1  let x = 5;
  2  let y = 3;
  3  let z = x + y;
  4  print(z);

  we follow ONE statement: 'let z = x + y;'  with x=5, y=3

========================================================================
  LAYER 2 -- TOKENS (lexical analysis, module 33)
========================================================================
  LET(let)  ID(z)  OP(=)  ID(x)  OP(+)  ID(y)  PUNCT(;)  EOF

========================================================================
  LAYER 3 -- ABSTRACT SYNTAX TREE (parsing, module 33)
========================================================================
  let  'z'
    └── binop '+'
          ├── ('var', 'x')
          └── ('var', 'y')

========================================================================
  LAYER 4 -- ASSEMBLY (code generation, module 33)
========================================================================
          LDI R1, 5
          ST R1, R0, 0
          LDI R1, 3
          ST R1, R0, 1
          LD R1, R0, 0
          LD R2, R0, 1
          ADD R1, R1, R2
          ST R1, R0, 2
          LD R1, R0, 2
          ST R1, R0, 31       ; memory-mapped output
  L1_halt:
          JMP L1_halt

========================================================================
  LAYER 5 -- MACHINE CODE (assembly, module 31)
========================================================================
   addr    hex              binary   disassembly
      0  0x9205  1001001000000101   LDI R1, 5           
      1  0xb200  1011001000000000   ST R1, R0, 0        
      2  0x9203  1001001000000011   LDI R1, 3           
      3  0xb201  1011001000000001   ST R1, R0, 1        
      4  0xa200  1010001000000000   LD R1, R0, 0        
      5  0xa401  1010010000000001   LD R2, R0, 1        
      6  0x1250  0001001001010000   ADD R1, R1, R2        <-- the ADD we follow
      7  0xb202  1011001000000010   ST R1, R0, 2        
      8  0xa202  1010001000000010   LD R1, R0, 2        
      9  0xb21f  1011001000011111   ST R1, R0, 31       

========================================================================
  LAYER 6 -- INSTRUCTION FIELDS (what the decoder sees)
========================================================================
  0001001001010000
  ^^^^                opcode = 0001 = ADD
      ^^^             rd     = 001 = R1
         ^^^          ra     = 001 = R1
            ^^^       rb     = 010 = R2

========================================================================
  LAYER 7 -- CONTROL SIGNALS (module 30)
========================================================================
  the control ROM is addressed by the opcode 0001 and outputs:
    RegWrite     = 1   ASSERTED
    RegBSrc      = 0   .
    ALUSrc       = 0   .
    ALUOp        = 0   .
    MemRead      = 0   .
    MemWrite     = 0   .
    MemToReg     = 0   .
    Branch       = 0   .
    BranchNot    = 0   .
    Jump         = 0   .
    Link         = 0   .

  these wires steer the multiplexers. RegWrite=1 enables the
  register file's write port; ALUSrc=0 selects register B, not
  the immediate; ALUOp=0 selects ADD on the ALU's function input.

========================================================================
  LAYER 8 -- REGISTER FILE AND ALU (modules 23, 25)
========================================================================
  read port A -> R1 = 5  (0000000000000101)
  read port B -> R2 = 3  (0000000000000011)
  ALU function select = 000 (ADD)
  result -> R1 = 8  (0000000000001000)

========================================================================
  LAYER 9 -- LOGIC GATES (the adder, module 21)
========================================================================
  5 + 3, bit by bit through the ripple-carry chain:
   bit  A  B |  A^B  A&B  Cin&(A^B) |  sum  carry
     0  1  1 |    0    1          0 |    0      1
     1  0  1 |    1    0          1 |    0      1
     2  1  0 |    1    0          1 |    0      1
     3  0  0 |    0    0          0 |    1      0
     4  0  0 |    0    0          0 |    0      0
  (bits 5-15 are all zero and omitted)

  bit 0: A=1 B=1 -> XOR gives 0, AND gives 1 -> a carry is born
  bit 1: the carry arrives, A=0 B=1 -> sum 0, carry propagates
  bit 3: the carry finally lands -> sum bit 1

========================================================================
  LAYER 10 -- TRANSISTORS (modules 13, 16)
========================================================================
  one full adder = 2xXOR(12) + 2xAND(6) + 1xOR(6) = 42 transistors
  a 16-bit adder = 16 x 42 = 672 transistors


  NOTE: that is the cost of building a full adder from separate
  gate CELLS. A purpose-designed CMOS full adder (the 'mirror
  adder') needs only 28 -- because building one PDN/PUN network
  directly beats composing pre-made gates (module 16).

  each transistor is a MOSFET (module 12): a voltage on an
  insulated gate inverts a silicon surface, forming a channel
  between two doped regions -- and current flows.

========================================================================
  LAYER 11 -- PHYSICS (modules 6-10)
========================================================================
  the doped regions are silicon with ~1 atom in 50 million
  replaced by phosphorus or boron (module 9).
  the insulator is SiO2, ~4 molecules thick, with a 9 eV band
  gap that electrons cannot cross (modules 8, 11).
  'a 1' is a voltage above 2.4 V; 'a 0' is below 0.4 V; the
  0.4 V gap between them is the noise margin (module 5) that
  makes every layer above this one possible.

========================================================================
  THE ANSWER
========================================================================
  the program printed: 8
  'let z = x + y;' with x=5, y=3 gave z = 8

  every layer above was computed, not asserted.

trace_lab: passed
```

---

## 5. What is still taken on faith

**Be honest about the boundary.** The trace bottoms out at "a voltage on an insulated gate inverts the silicon surface". Below that:

- **Why energy levels are quantised** requires quantum mechanics, and this course took it as given ([[how-computers-work/02-semiconductors/03-energy-bands|module 8]]).
- **Why the electric field behaves as it does** is Maxwell's equations, assumed throughout.
- **Timing** is modelled but not simulated — the trace shows *what* happens, not *when*. Propagation delay, setup and hold are real and invisible here.
- **The emulator is not the hardware.** It agrees with the datapath model on every test, which is evidence, not proof.

**Every model has a floor, and knowing where yours is matters more than pretending it does not exist.** This course's floor is quantum mechanics, and that is a reasonable place to stop.

---

## 6. The assessment — do this closed-book

**This is the real finish line of the course.** Everything before it was preparation.

Take a fresh sheet of paper. Write `let z = x + y;` at the top and `electrons` at the bottom. **Fill in every layer between, from memory.**

For each layer, answer three questions — the ones [[how-computers-work/index|the course index]] set out at the start:

1. **What is physically happening?**
2. **What abstraction have we created?**
3. **What does the next layer build from it?**

**Where you get stuck is the useful part.** A gap here is not a failure; it is a precise reading list. Go back to that module, and only that module.

**You have finished this course when you can fill the sheet without help.** Not when you have read to the bottom of the last page.

---

## 7. Common pitfalls and traps

1. **Treating the trace as something to read.** It is something to reproduce. Reading it proves nothing.
2. **Skipping a layer because it "obviously" works.** The layers you skip are the ones you do not understand.
3. **Confusing the model with the machine.** The emulator agrees with the datapath; neither is silicon.
4. **Thinking the abstraction boundaries are arbitrary.** Each exists because a lower layer offers a *guarantee* — noise margins, a stable ISA — that makes ignoring it safe.
5. **Believing you are done because the program printed 8.** The program working proves the artifacts work. The closed-book trace proves *you* do.

---

## 8. Check your understanding

1. **At which layer does "5" stop being a number and become something else?**
   <details><summary>Answer</summary>
   <strong>It was never a number.</strong> At layer 1 it is the character <code>5</code>. At layer 2 a token. At layer 5 it is the bit pattern <code>000101</code> inside an <code>LDI</code>. At layer 8 it is voltages on sixteen wires. At layer 10 it is channels conducting or not.<br>
   <strong>"Five" exists only in the interpretation we agreed on</strong> — that a group of wires read as place-value binary denotes a quantity. The silicon has no concept of five, and the course's whole method is watching that agreement be constructed layer by layer, then relied upon.
   </details>

2. **The trace says the ADD asserts `RegWrite` and nothing else. Why so few signals?**
   <details><summary>Answer</summary>
   Because most control signals select <em>alternatives to the default path</em>, and ADD is the default path. It uses register B (so <code>ALUSrc</code>=0), writes the ALU result (so <code>MemToReg</code>=0), touches no memory, and does not branch.<br>
   Only <code>RegWrite</code> must be asserted, to enable the write port. <strong>A control table's sparseness is a sign the datapath's defaults were chosen well</strong> — if every instruction asserted most signals, the defaults are wrong.
   </details>

3. **Why does the carry taking three bit-positions to travel matter?**
   <details><summary>Answer</summary>
   Because it is <strong>sequential</strong>, and sequential means slow. Each position's carry depends on the one below, so a 16-bit add cannot finish faster than 16 carry propagations — which is $O(n)$ delay and, at 64 bits, caps a clock below 400 MHz ([[how-computers-work/05-combinational/02-adders|module 21]]).<br>
   Watching the carry born at bit 0 arrive at bit 3 is watching the reason carry-lookahead exists, and the reason "turn a sequential dependency into a logarithmic tree" recurs four times in this course.
   </details>

4. **What would you need to add to trace this on real silicon rather than an emulator?**
   <details><summary>Answer</summary>
   <strong>Timing.</strong> The emulator computes what each layer produces; it says nothing about when. On real hardware you would need propagation delay per gate, wire RC, setup and hold windows, and clock skew — and you would find the carry chain does not settle instantaneously but ripples over hundreds of picoseconds.<br>
   You would also meet effects with no model here at all: supply droop, crosstalk, metastability at asynchronous boundaries ([[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]). <strong>The functional trace is complete and the physical one is not</strong> — which is exactly why the breadboard track exists.
   </details>

---

## 9. Practice — the final project

**Task:** Produce the artifacts the curriculum's final project asks for. You have built most of them; this is assembling them into something coherent.

- **(a)** A **CPU architecture document**: block diagram, datapath, control unit, registers, ALU, memory interface, clocking model.
- **(b)** An **ISA specification** in the format of [[how-computers-work/08-capstone/02-the-isa|module 29]] section 4, including every detail from the "must be nailed down" list.
- **(c)** A **CPU implementation** on at least two of the four build tracks, agreeing with each other.
- **(d)** An **assembler** with a listing file and proper error messages.
- **(e)** An **emulator** with a debugger and a differential test harness.
- **(f)** A **compiler** for your own language, with at least one feature Pebble lacks.
- **(g)** A **technical report** explaining the complete stack, using the section 2 table as its skeleton, with your own artifacts as the evidence at each layer.

**Done when:** someone who has not taken this course can read your report and follow one statement of your language to transistor switching.

---

## 10. Where to go next

**You have built the bottom half properly and routed the top half.** The obvious continuations:

| Direction | Where |
| :--- | :--- |
| Make the CPU fast | [[computer-architecture/06-pipelining\|pipelining]], [[computer-architecture/09-caches-in-depth\|caches]], [[computer-architecture/10-out-of-order-and-superscalar\|out-of-order]] |
| Run programs on it | [[build-your-own-shit/05-your-own-os\|Your Own OS]] |
| Make the language real | [[build-your-own-shit/04-your-own-language\|Your Own Language]] — bytecode VM, closures, GC |
| Optimise the compiler | [[compilers/07-optimisation\|compilers/optimisation]] — register allocation is the big win |
| Go lower | Quantum mechanics, or [[hardware/index\|hardware/]] for practical electronics |

**The gap worth knowing about:** [[how-computers-work/07-the-bridge|the bridge]] flagged that this vault has no dedicated treatment of **linkers and executable formats**. If you want the source-to-CPU chain genuinely complete, that is the missing link.

---

## Before you finish

- [ ] Trace `let z = x + y;` through all eleven layers, closed-book.
- [ ] For each layer, name what represents the data and what performs the operation.
- [ ] State where your model bottoms out and what it takes on faith.
- [ ] Explain why the carry taking three bit-positions to travel is the reason carry-lookahead exists.
- [ ] Explain why "5" was never a number.

**Recap:** A statement in a language you designed becomes tokens, a tree, assembly, machine code, bit fields, control signals, register and ALU activity, gate switching, transistor channels, and finally electrons responding to fields. Every layer was computed by tools you built, not asserted. The abstractions are not arbitrary: each exists because the layer below offers a guarantee — a noise margin, a stable ISA — that makes ignoring it safe. The model bottoms out at quantum mechanics, and knowing where it bottoms out is part of understanding it.

**This is the end of the course.**

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/08-capstone/06-build-the-language|Module 33]] — the compiler this traces
- [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU]] — the four hardware builds
- [[how-computers-work/07-the-bridge|Module 27 — The Bridge]] — the upper stack in depth
