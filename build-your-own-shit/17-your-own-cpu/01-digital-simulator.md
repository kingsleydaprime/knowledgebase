# Track 1 — The Digital Simulator (See the Datapath)

**[Advanced]** — A weekend. Produces a **clickable circuit** where you single-step the clock and watch buses light up. The track that makes "datapath" stop being a word and start being a thing.

## Why this track

Track 3's emulator tells you what PRIME-1 *does*. It tells you nothing about what a processor *is*.

**Here you place an ALU, a register file and a program counter on a canvas and wire them together.** Then you click the clock once and watch a value leave the register file, cross the ALU, and land back in a register. The abstraction collapses into a picture.

**The thing you will actually learn is the control unit** — the table that turns an opcode into the twelve signals steering everything else. In the emulator that logic hides inside `if op == ...`. In a circuit there *is* no `if`; there is a ROM, and its contents are the CPU's entire personality.

## The tool

**[Digital](https://github.com/hneemann/Digital)** — free, offline, Java, actively maintained. Built for exactly this: it has a register file, RAM, ROM and ALU components, a clock you can single-step, and it shows values on every wire as you go.

**Logisim Evolution** works equally well if you already know it. The build below is described in component terms, not menu clicks, so it transfers.

**Why not draw it on paper?** Because a circuit that has never run is almost certainly wrong, and you will not find out which part.

## What you're building

```
                   ┌─────────────────────────────────────────┐
                   │                                         │
              ┌────▼────┐    ┌──────────┐                    │
        ┌────►│   PC    ├───►│  I-MEM   ├──┬─── instruction   │
        │     └─────────┘    │  (ROM)   │  │                  │
        │          │         └──────────┘  │                  │
        │       ┌──▼──┐                    │                  │
        │       │ +1  │                    ▼                  │
        │       └──┬──┘         ┌────────────────────┐        │
        │          │            │   CONTROL UNIT     │        │
        │          │            │  (opcode -> 12     │        │
        │          │            │   control signals) │        │
        │          │            └─────────┬──────────┘        │
        │          │                      │ control           │
        │     ┌────▼─────┐                ▼                   │
        │     │  BRANCH  │◄──── ┌──────────────────┐          │
        └─────┤   MUX    │      │  REGISTER FILE   │          │
              └──────────┘      │  8 x 16-bit      │          │
                                │  2 read, 1 write │          │
                                └───┬──────────┬───┘          │
                                    │ A        │ B            │
                                    │      ┌───▼───┐          │
                                    │      │ALUSrc │◄─ imm    │
                                    │      │  MUX  │          │
                                    │      └───┬───┘          │
                                 ┌──▼──────────▼──┐           │
                                 │      ALU       │           │
                                 └────────┬───────┘           │
                                          │ result            │
                                    ┌─────▼─────┐             │
                                    │   D-MEM   │             │
                                    │   (RAM)   │             │
                                    └─────┬─────┘             │
                                    ┌─────▼─────┐             │
                                    │ MemToReg  │             │
                                    │    MUX    ├─────────────┘
                                    └───────────┘   writeback
```

Six blocks and four multiplexers. **That is a processor.**

## The control unit — the part that matters

Everything above except the control unit is a component you already understand from [[how-computers-work/index|How Computers Work]]. The control unit is new, and it is the whole intellectual content of this track.

**It is a ROM.** Address it with the 4-bit opcode; it outputs the control signals for that instruction. Twelve outputs, sixteen entries.

Here is the complete table. **Type this into a ROM component and your CPU knows how to be a CPU:**

```
    op name RegW RegB ALUS ALUO MemR MemW MemT Bran Bran Jump Link
  ----------------------------------------------------------------
  0000  NOP    0    0    0    0    0    0    0    0    0    0    0
  0001  ADD    1    0    0    0    0    0    0    0    0    0    0
  0010  SUB    1    0    0    1    0    0    0    0    0    0    0
  0011  AND    1    0    0    2    0    0    0    0    0    0    0
  0100   OR    1    0    0    3    0    0    0    0    0    0    0
  0101  XOR    1    0    0    4    0    0    0    0    0    0    0
  0110  SHL    1    0    0    5    0    0    0    0    0    0    0
  0111  SHR    1    0    0    6    0    0    0    0    0    0    0
  1000  SLT    1    0    0    7    0    0    0    0    0    0    0
  1001  LDI    1    0    1    0    0    0    0    0    0    0    0
  1010   LD    1    0    1    0    1    0    1    0    0    0    0
  1011   ST    0    1    1    0    0    1    0    0    0    0    0
  1100  BEZ    0    0    0    0    0    0    0    1    0    0    0
  1101  BNZ    0    0    0    0    0    0    0    1    1    0    0
  1110  JMP    0    0    0    0    0    0    0    0    0    1    0
  1111  JAL    1    0    0    0    0    0    0    0    0    1    1
```

### What each signal does

| Signal | Meaning |
| :--- | :--- |
| **RegWrite** | Write the result back to the register file |
| **RegBSrc** | Read port B address: 0 = `rb` field, 1 = `rd` field (**stores need this**) |
| **ALUSrc** | ALU's second operand: 0 = register B, 1 = the immediate |
| **ALUOp** | Which operation ([[how-computers-work/05-combinational/04-the-alu\|module 22]]'s function select) |
| **MemRead** | Read data memory at the ALU result |
| **MemWrite** | Write register B into data memory at the ALU result |
| **MemToReg** | Writeback source: 0 = ALU result, 1 = memory data |
| **Branch** | This is a conditional branch |
| **BranchNot** | Invert the condition (0 = branch if zero, 1 = branch if not zero) |
| **Jump** | Unconditional jump to the 12-bit address field |
| **Link** | Write PC+1 into R7 (for `JAL`) |

> [!NOTE]
> **`RegBSrc` is the signal nobody predicts, and it is worth understanding before you wire anything.**
>
> Every R-type instruction reads `ra` and `rb`. But `ST rd, ra, imm` needs to read **`ra`** (the address base) and **`rd`** (the data being stored) — a different field than every other instruction uses.
>
> So read port B needs a multiplexer on its *address* input. This is not in the ISA spec; it is a consequence of the encoding, and it only becomes visible when you try to build the thing.
>
> **This is the single best argument for building a CPU rather than reading about one.** The spec looked complete. It wasn't.

## Milestones

Follow the master guide's build order. Each one runs in the simulator.

### 1 — Fetch only

Place a **register** (PC, 16-bit), an **adder** with one input tied to constant 1, and a **ROM** (instruction memory). Wire PC → ROM address, PC → adder → back to PC input. Add a **clock**.

Fill the ROM with zeros. **Single-step the clock and watch the PC count: 0, 1, 2, 3.**

*You have a machine that goes.* Do not skip this — it eliminates half the possible bugs in every later step.

### 2 — Decode

Add **splitters** breaking the 16-bit instruction into `op[15:12]`, `rd[11:9]`, `ra[8:6]`, `rb[5:3]`, `imm[5:0]`, `addr[11:0]`.

Attach **LED/probe outputs** to each field. Put one real instruction in the ROM and check the fields light up correctly.

**Digital shows values on hover** — use it constantly.

### 3 — Register file and ALU

Place the **register file** (8 × 16-bit, two read ports, one write port) and the **ALU**. Wire `ra` → read address A, `rb` → read address B, `rd` → write address.

Add the control ROM with just the R-type rows filled in.

**Test:** hand-load the ROM with `LDI` replaced by pre-initialised registers, then execute `ADD R1, R2, R3`. Watch the value appear in R1.

**Hardwire R0 to zero.** In Digital, either use a register file component that supports it, or AND the write-enable with `(rd != 0)`.

### 4 — The ALUSrc multiplexer and immediates

Add a **sign-extender** (6 → 16 bits) and a 2-to-1 MUX selecting between register B and the immediate. Fill in the `LDI` control row.

**Test:** `LDI R1, 5` puts 5 in R1. Then `LDI R1, -1` must put `0xFFFF` in R1 — if it puts `0x003F`, your sign extender is wrong.

### 5 — Memory

Add **RAM** for data memory, plus the `MemToReg` MUX and the `RegBSrc` MUX. Fill in `LD` and `ST`.

**Test:** `ST` a value, `LD` it back into a different register.

### 6 — Branches

Add a **zero-detector** on read port A (a 16-input NOR), the branch condition logic (`Branch AND (zero XOR BranchNot)`), and the branch MUX selecting between `PC+1` and `PC+1+imm`.

**Test:** a two-instruction infinite loop. **If it loops, your offsets are right.**

### 7 — Jumps

Add the jump MUX and the `Link` path writing `PC+1` into R7.

### 8 — Run the reference program

Load the assembled reference program into the instruction ROM and run. **R1 = 55.**

## The reference model

Before wiring anything, run this. It is the same datapath **structured exactly like the circuit** — every decision made by a control signal, with no `if` on the opcode anywhere in the execution path.

**Read `Datapath.cycle()` alongside the block diagram.** Each commented section is one column of the picture, and each control signal is one wire.

Save as `datapath.py` next to `prime1.py` from track 3, and run `python3 datapath.py`.

```python
"""PRIME-1 as a DATAPATH plus a CONTROL UNIT.

The datapath below contains NO if/elif on the opcode. Every decision is
made by a control signal read from a table. That table is the control
unit -- and it is exactly what you wire in a logic simulator."""

MASK = 0xFFFF

# ALU function codes (the ALU's own select lines -- module 22)
ALU_ADD, ALU_SUB, ALU_AND, ALU_OR, ALU_XOR, ALU_SHL, ALU_SHR, ALU_SLT = range(8)

# One row per opcode. THIS TABLE IS THE CONTROL UNIT.
#            RegWrite RegBSrc ALUSrc ALUOp   MemRd MemWr MemToReg Branch BrNot Jump Link
CONTROL = {
    0b0000: (0,       0,      0,     ALU_ADD, 0,   0,    0,       0,     0,    0,   0),  # NOP
    0b0001: (1,       0,      0,     ALU_ADD, 0,   0,    0,       0,     0,    0,   0),  # ADD
    0b0010: (1,       0,      0,     ALU_SUB, 0,   0,    0,       0,     0,    0,   0),  # SUB
    0b0011: (1,       0,      0,     ALU_AND, 0,   0,    0,       0,     0,    0,   0),  # AND
    0b0100: (1,       0,      0,     ALU_OR,  0,   0,    0,       0,     0,    0,   0),  # OR
    0b0101: (1,       0,      0,     ALU_XOR, 0,   0,    0,       0,     0,    0,   0),  # XOR
    0b0110: (1,       0,      0,     ALU_SHL, 0,   0,    0,       0,     0,    0,   0),  # SHL
    0b0111: (1,       0,      0,     ALU_SHR, 0,   0,    0,       0,     0,    0,   0),  # SHR
    0b1000: (1,       0,      0,     ALU_SLT, 0,   0,    0,       0,     0,    0,   0),  # SLT
    0b1001: (1,       0,      1,     ALU_ADD, 0,   0,    0,       0,     0,    0,   0),  # LDI
    0b1010: (1,       0,      1,     ALU_ADD, 1,   0,    1,       0,     0,    0,   0),  # LD
    0b1011: (0,       1,      1,     ALU_ADD, 0,   1,    0,       0,     0,    0,   0),  # ST
    0b1100: (0,       0,      0,     ALU_ADD, 0,   0,    0,       1,     0,    0,   0),  # BEZ
    0b1101: (0,       0,      0,     ALU_ADD, 0,   0,    0,       1,     1,    0,   0),  # BNZ
    0b1110: (0,       0,      0,     ALU_ADD, 0,   0,    0,       0,     0,    1,   0),  # JMP
    0b1111: (1,       0,      0,     ALU_ADD, 0,   0,    0,       0,     0,    1,   1),  # JAL
}
SIGNAL_NAMES = ["RegWrite", "RegBSrc", "ALUSrc", "ALUOp", "MemRead",
                "MemWrite", "MemToReg", "Branch", "BranchNot", "Jump", "Link"]

def sign_extend(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def to_signed(v):
    return v - (1 << 16) if v & 0x8000 else v

def alu(a, b, op):
    """The module 22 ALU: computes everything, a MUX selects one."""
    results = {
        ALU_ADD: (a + b) & MASK,
        ALU_SUB: (a - b) & MASK,
        ALU_AND: a & b,
        ALU_OR:  a | b,
        ALU_XOR: a ^ b,
        ALU_SHL: (a << (b & 0xF)) & MASK,
        ALU_SHR: a >> (b & 0xF),
        ALU_SLT: 1 if to_signed(a) < to_signed(b) else 0,
    }
    return results[op]


class Datapath:
    def __init__(self):
        self.reg = [0] * 8
        self.pc = 0
        self.imem = [0] * 4096
        self.dmem = [0] * 4096
        self.halted = False
        self.cycles = 0

    def load(self, program):
        for i, w in enumerate(program):
            self.imem[i] = w & MASK

    def cycle(self, trace=False):
        """One clock cycle. Note: no branching on opcode anywhere below."""
        # --- FETCH -------------------------------------------------------
        ir = self.imem[self.pc]
        pc_plus_1 = (self.pc + 1) & MASK

        # --- DECODE ------------------------------------------------------
        op   = (ir >> 12) & 0xF
        rd   = (ir >> 9)  & 0x7
        ra   = (ir >> 6)  & 0x7
        rb   = (ir >> 3)  & 0x7
        imm  = sign_extend(ir & 0x3F, 6) & MASK
        addr = ir & 0xFFF
        (reg_write, reg_b_src, alu_src, alu_op, mem_read,
         mem_write, mem_to_reg, branch, branch_not, jump, link) = CONTROL[op]

        # --- REGISTER READ ------------------------------------------------
        # read port B selects rb normally, rd for stores (the data to write)
        rb_addr = rd if reg_b_src else rb
        a = self.reg[ra]
        b = self.reg[rb_addr]
        a_is_zero = 1 if a == 0 else 0          # dedicated zero-detect for branches

        # --- EXECUTE -------------------------------------------------------
        operand_b = imm if alu_src else b        # <- the ALUSrc MUX
        result = alu(a, operand_b, alu_op)

        # --- MEMORY ---------------------------------------------------------
        mem_data = self.dmem[result & 0xFFF] if mem_read else 0
        if mem_write:
            self.dmem[result & 0xFFF] = b        # b is reg[rd] because RegBSrc=1

        # --- WRITEBACK --------------------------------------------------------
        write_value = mem_data if mem_to_reg else result
        write_dest = rd
        if link:                                 # JAL writes the return address to R7
            write_value, write_dest = pc_plus_1, 7
        if reg_write and write_dest != 0:        # R0 is hardwired
            self.reg[write_dest] = write_value & MASK

        # --- PC UPDATE ---------------------------------------------------------
        take_branch = branch and (a_is_zero ^ branch_not)
        if jump:
            next_pc = addr
            if addr == self.pc:                  # jump-to-self = halt idiom
                self.halted = True
        elif take_branch:
            next_pc = (pc_plus_1 + imm) & MASK
        else:
            next_pc = pc_plus_1

        if trace:
            active = [n for n, v in zip(SIGNAL_NAMES, CONTROL[op]) if v and n != "ALUOp"]
            print(f"  PC={self.pc:04x} IR={ir:016b} | {', '.join(active) or 'none':38s}"
                  f"| R1={self.reg[1]:3d} R2={self.reg[2]:3d} -> PC={next_pc:04x}")

        self.pc = next_pc
        self.cycles += 1

    def run(self, max_cycles=10000, trace_first=0):
        while not self.halted and self.cycles < max_cycles:
            self.cycle(trace=self.cycles < trace_first)


if __name__ == "__main__":
    print("THE CONTROL UNIT -- opcode in, control signals out.")
    print("This table IS the circuit you wire. Nothing else decides anything.\n")
    names = ["NOP","ADD","SUB","AND","OR","XOR","SHL","SHR",
             "SLT","LDI","LD","ST","BEZ","BNZ","JMP","JAL"]
    hdr = f"  {'op':>4s} {'name':>4s} " + " ".join(f"{n[:4]:>4s}" for n in SIGNAL_NAMES)
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for op in sorted(CONTROL):
        vals = " ".join(f"{v:>4d}" for v in CONTROL[op])
        print(f"  {op:04b} {names[op]:>4s} {vals}")
    print()

    # Assemble with the verified track-3 assembler -- no hand-encoding
    from prime1 import assemble, Prime1, REFERENCE_PROGRAM
    program, _ = assemble(REFERENCE_PROGRAM)

    dp = Datapath()
    dp.load(program)
    print("EXECUTING -- watch which control signals are asserted each cycle:")
    dp.run(trace_first=8)
    print("  ...")
    print()
    print(f"HALTED after {dp.cycles} cycles")
    print(f"  R1 = {dp.reg[1]}  (expected 55)")

    assert dp.reg[1] == 55, f"expected 55, got {dp.reg[1]}"
    assert dp.reg[0] == 0

    # DIFFERENTIAL TEST: the datapath must agree with the track-3 emulator
    print()
    print("DIFFERENTIAL TEST against the track-3 emulator:")
    ref = Prime1(); ref.load(program); ref.run()
    print(f"  emulator: R1={ref.reg[1]}, {ref.cycles} cycles")
    print(f"  datapath: R1={dp.reg[1]}, {dp.cycles} cycles")
    assert ref.reg[:8] == dp.reg[:8], f"registers differ: {ref.reg} vs {dp.reg}"
    assert ref.cycles == dp.cycles, "cycle counts differ"
    print("  registers and cycle counts match exactly")

    # LD/ST exercise the RegBSrc mux and the memory path
    mem_test = """
            LDI  R1, 25
            LDI  R2, 8
            ST   R1, R2, 0
            LD   R3, R2, 0
    halt:   JMP  halt
    """
    prog2, _ = assemble(mem_test)
    dp2 = Datapath(); dp2.load(prog2); dp2.run()
    ref2 = Prime1(); ref2.load(prog2); ref2.run()
    print()
    print(f"  LD/ST: stored 25 at address 8, read back {dp2.reg[3]}")
    assert dp2.dmem[8] == 25 and dp2.reg[3] == 25
    assert ref2.reg[3] == dp2.reg[3], "load/store disagrees with emulator"

    print()
    print("datapath: passed")
```

Expected output:

```
THE CONTROL UNIT -- opcode in, control signals out.
This table IS the circuit you wire. Nothing else decides anything.

    op name RegW RegB ALUS ALUO MemR MemW MemT Bran Bran Jump Link
  ----------------------------------------------------------------
  0000  NOP    0    0    0    0    0    0    0    0    0    0    0
  0001  ADD    1    0    0    0    0    0    0    0    0    0    0
  0010  SUB    1    0    0    1    0    0    0    0    0    0    0
  0011  AND    1    0    0    2    0    0    0    0    0    0    0
  0100   OR    1    0    0    3    0    0    0    0    0    0    0
  0101  XOR    1    0    0    4    0    0    0    0    0    0    0
  0110  SHL    1    0    0    5    0    0    0    0    0    0    0
  0111  SHR    1    0    0    6    0    0    0    0    0    0    0
  1000  SLT    1    0    0    7    0    0    0    0    0    0    0
  1001  LDI    1    0    1    0    0    0    0    0    0    0    0
  1010   LD    1    0    1    0    1    0    1    0    0    0    0
  1011   ST    0    1    1    0    0    1    0    0    0    0    0
  1100  BEZ    0    0    0    0    0    0    0    1    0    0    0
  1101  BNZ    0    0    0    0    0    0    0    1    1    0    0
  1110  JMP    0    0    0    0    0    0    0    0    0    1    0
  1111  JAL    1    0    0    0    0    0    0    0    0    1    1

EXECUTING -- watch which control signals are asserted each cycle:
  PC=0000 IR=1001001000000000 | RegWrite, ALUSrc                      | R1=  0 R2=  0 -> PC=0001
  PC=0001 IR=1001010000001010 | RegWrite, ALUSrc                      | R1=  0 R2= 10 -> PC=0002
  PC=0002 IR=0001001001010000 | RegWrite                              | R1= 10 R2= 10 -> PC=0003
  PC=0003 IR=1001011000000001 | RegWrite, ALUSrc                      | R1= 10 R2= 10 -> PC=0004
  PC=0004 IR=0010010010011000 | RegWrite                              | R1= 10 R2=  9 -> PC=0005
  PC=0005 IR=1101000010111100 | Branch, BranchNot                     | R1= 10 R2=  9 -> PC=0002
  PC=0002 IR=0001001001010000 | RegWrite                              | R1= 19 R2=  9 -> PC=0003
  PC=0003 IR=1001011000000001 | RegWrite, ALUSrc                      | R1= 19 R2=  9 -> PC=0004
  ...

HALTED after 43 cycles
  R1 = 55  (expected 55)

DIFFERENTIAL TEST against the track-3 emulator:
  emulator: R1=55, 43 cycles
  datapath: R1=55, 43 cycles
  registers and cycle counts match exactly

  LD/ST: stored 25 at address 8, read back 25

datapath: passed
```

**Note what the trace shows.** Each cycle prints only the control signals that are *asserted*. `LDI` asserts `RegWrite, ALUSrc`. `ADD` asserts only `RegWrite`. `BNZ` asserts `Branch, BranchNot` and writes nothing. **Those signal names are the wires you are about to solder**, and the circuit is correct when it asserts the same ones.

The differential test at the end is the technique the master guide insists on: the datapath and the track-3 emulator must agree on **every register and the cycle count**. When your circuit disagrees, run both and find the first cycle where they diverge.

## The parts that will bite you

- **Combinational loops.** If you accidentally wire an output back to an input with no register in the path, the simulator will oscillate or refuse to settle. Every loop must pass through the PC register or the register file. This is [[how-computers-work/06-memory/01-latches-and-flip-flops|module 23]]'s feedback, and here it is a bug rather than a feature.
- **Forgetting `RegBSrc`.** Stores will write the wrong value and you will chase it for an hour.
- **Register file write timing.** Digital's register file writes on the clock edge. If your read appears to see the new value in the same cycle, you have wired it as a latch, not a flip-flop ([[how-computers-work/06-memory/02-registers-and-counters|module 24]]).
- **Sign extension on the wrong width.** Extend from bit 5, not bit 15.
- **ROM vs RAM for instructions.** Use a ROM for instruction memory — it cannot be accidentally overwritten by a stray store while you are debugging.
- **Clock speed.** Run it single-stepped first. Only switch to a free-running clock once the reference program works.

## How to know it works

1. **Per-milestone**, as above — each one is separately testable.
2. **The reference program gives 55.**
3. **Differential test.** Digital can export a signal trace; dump the register file each cycle and compare against `datapath.py`'s output.
4. **The control ROM matches the table** — re-read it entry by entry. A single wrong bit produces bafflingly specific misbehaviour.

## Where to stop

**Stop when the reference program produces 55 and you have single-stepped through the loop at least once**, watching the branch fire.

**Worth adding if you enjoyed it:** seven-segment display output on a memory-mapped address, so your CPU can print. That is 20 minutes and makes it feel like a real machine.

**Not worth adding here:** pipelining. It changes every timing assumption in the design and is better attempted as a second CPU.

## Related

- [[build-your-own-shit/17-your-own-cpu/index|PRIME-1 index and ISA spec]]
- [[build-your-own-shit/17-your-own-cpu/03-python-emulator|Track 3 — Python emulator]] — build this first; it is your oracle
- [[build-your-own-shit/17-your-own-cpu/02-verilog|Track 2 — Verilog]] — the same design, described rather than drawn
- [[build-your-own-shit/17-your-own-cpu/04-breadboard|Track 4 — Breadboard]]
- [[how-computers-work/05-combinational/04-the-alu|module 22]] — the ALU you are placing
- [[how-computers-work/06-memory/02-registers-and-counters|module 24]] — the register file and PC
