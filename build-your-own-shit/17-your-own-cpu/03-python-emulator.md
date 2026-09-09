# Track 3 — The Python Emulator (Build This First)

**[Intermediate]** — One evening. Produces the **reference implementation** every other track is tested against, and makes the ISA concrete before you commit a single wire.

## Why this track goes first

You could start by wiring gates. You would then spend two days debugging a circuit without knowing whether the *specification* was even coherent.

**An emulator answers "what should this machine do?" in a form you can run, test and argue with.** It takes an evening, it catches every ambiguity in the ISA, and — the real payoff — when your circuit disagrees with it on cycle 47, you have a **diffable test case** rather than a staring contest with a waveform.

**This is the same reason the reference program exists.** Build the oracle, then build the thing.

## What you're building

- A **two-pass assembler**: text in, 16-bit machine words out
- An **emulator**: fetch, decode, execute, memory, writeback
- A **debugger**: single-step, register dump, cycle count
- Enough tests that you trust it as the authority

## Milestones

Each one runs.

### 1 — Machine state and a dump

A class holding 8 registers, a PC, flags, and 64K words of memory. A `dump()` printing all of it.

**Test:** construct it, print it, see zeros. *You have something to look at.*

### 2 — Fetch only

`step()` reads `mem[PC]`, increments PC, returns the word. No decoding.

**Test:** load `[0, 0, 0]`, step three times, assert PC is 3. *Your machine goes.*

**Get the PC increment right now.** It happens during fetch, before execution, so branch offsets are relative to PC-*after*-increment. Every track inherits this decision.

### 3 — Decode

Split the instruction into `op`, `rd`, `ra`, `rb`, `imm`, `addr`. Print them.

```python
op   = (instruction >> 12) & 0xF
rd   = (instruction >> 9)  & 0x7
ra   = (instruction >> 6)  & 0x7
rb   = (instruction >> 3)  & 0x7
imm  = sign_extend(instruction & 0x3F, 6)
addr = instruction & 0xFFF
```

**Test:** hand-encode `ADD R1, R2, R3` and assert the fields come back as 1, 2, 3.

### 4 — R-type ALU operations

`ADD`, `SUB`, `AND`, `OR`, `XOR`, `SHL`, `SHR`, `SLT`, plus flags.

**Two traps, both from [[how-computers-work/06-memory/02-registers-and-counters|module 24]] and [[how-computers-work/05-combinational/04-the-alu|module 22]]:**

- **R0 must be hardwired.** Write to it and discard. If `write_reg` stores to R0, then `NOP` (`ADD R0,R0,R0`) silently works but every idiom that relies on R0 being zero breaks later, mysteriously.
- **Read before write.** `ADD R1, R1, R2` must read the *old* R1. Read both operands into locals before writing the result.

**Test:** each opcode individually, with flags.

### 5 — Immediates and sign extension

`LDI`. And **`LDI R1, -1` must give `0xFFFF`, not `0x003F`.**

```python
def sign_extend(value, bits):
    if value & (1 << (bits - 1)):
        return value - (1 << bits)
    return value
```

**Test:** `LDI R1, -1` → `0xFFFF`. This one bug otherwise surfaces as backward branches jumping forward.

### 6 — Memory

`LD rd, ra, imm` and `ST rd, ra, imm`, both with `mem[ra + imm]`.

**PRIME-1 is word-addressed.** `mem[5]` is the sixth 16-bit word, not byte 5.

**Test:** store to an address, load it back, assert equality.

### 7 — Branches

`BEZ` and `BNZ`, PC-relative from PC-after-increment.

**Test:** a two-instruction infinite loop. If it loops, your offsets are right.

### 8 — The assembler

Two passes:

1. **Pass 1** walks the source counting instruction addresses and recording where each label lands.
2. **Pass 2** encodes, resolving label references — and for branches computes `target - (address + 1)`.

**Test:** assemble the reference program, disassemble it by eye against the spec table.

### 9 — Run the reference program

**R1 = 55.**

## The complete implementation

Save as `prime1.py` and run `python3 prime1.py`. Standard library only.

```python
"""PRIME-1 emulator and assembler -- the reference implementation.

Every other build track is tested against this."""

WORD = 16
MASK = (1 << WORD) - 1

OPCODES = {
    "NOP": 0b0000, "ADD": 0b0001, "SUB": 0b0010, "AND": 0b0011,
    "OR":  0b0100, "XOR": 0b0101, "SHL": 0b0110, "SHR": 0b0111,
    "SLT": 0b1000, "LDI": 0b1001, "LD":  0b1010, "ST":  0b1011,
    "BEZ": 0b1100, "BNZ": 0b1101, "JMP": 0b1110, "JAL": 0b1111,
}
R_TYPE = {"ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "SLT"}
I_TYPE = {"LDI", "LD", "ST", "BEZ", "BNZ"}
J_TYPE = {"JMP", "JAL"}

def sign_extend(value, bits):
    """A 6-bit 0b111111 is -1, not 63. Forgetting this breaks backward branches."""
    if value & (1 << (bits - 1)):
        return value - (1 << bits)
    return value

def to_signed(value):
    return value - (1 << WORD) if value & (1 << (WORD - 1)) else value


class Prime1:
    def __init__(self, memory_words=65536):
        self.reg = [0] * 8
        self.pc = 0
        self.mem = [0] * memory_words
        self.flags = {"Z": 0, "N": 0, "C": 0, "V": 0}
        self.halted = False
        self.cycles = 0

    def load(self, program, at=0):
        for i, word in enumerate(program):
            self.mem[at + i] = word & MASK

    def write_reg(self, index, value):
        """R0 is hardwired to zero -- writes are discarded, not stored."""
        if index != 0:
            self.reg[index] = value & MASK

    def set_flags(self, result, carry=0, overflow=0):
        self.flags["Z"] = 1 if (result & MASK) == 0 else 0
        self.flags["N"] = (result >> (WORD - 1)) & 1
        self.flags["C"] = carry
        self.flags["V"] = overflow

    def step(self):
        """One fetch-decode-execute-memory-writeback cycle."""
        instruction = self.mem[self.pc]
        self.pc = (self.pc + 1) & MASK          # PC advances during FETCH
        self.cycles += 1

        op = (instruction >> 12) & 0xF
        rd = (instruction >> 9) & 0x7
        ra = (instruction >> 6) & 0x7
        rb = (instruction >> 3) & 0x7
        imm = sign_extend(instruction & 0x3F, 6)
        addr = instruction & 0xFFF

        a, b = self.reg[ra], self.reg[rb]

        if op == OPCODES["NOP"]:
            pass
        elif op == OPCODES["ADD"]:
            raw = a + b
            self.write_reg(rd, raw)
            self.set_flags(raw, carry=(raw >> WORD) & 1,
                           overflow=self._ovf(a, b, raw))
        elif op == OPCODES["SUB"]:
            raw = a - b
            self.write_reg(rd, raw)
            self.set_flags(raw, carry=1 if a >= b else 0,
                           overflow=self._ovf(a, (~b + 1) & MASK, raw))
        elif op == OPCODES["AND"]:
            self.write_reg(rd, a & b); self.set_flags(a & b)
        elif op == OPCODES["OR"]:
            self.write_reg(rd, a | b); self.set_flags(a | b)
        elif op == OPCODES["XOR"]:
            self.write_reg(rd, a ^ b); self.set_flags(a ^ b)
        elif op == OPCODES["SHL"]:
            r = (a << (b & 0xF)) & MASK
            self.write_reg(rd, r); self.set_flags(r)
        elif op == OPCODES["SHR"]:
            r = a >> (b & 0xF)
            self.write_reg(rd, r); self.set_flags(r)
        elif op == OPCODES["SLT"]:
            r = 1 if to_signed(a) < to_signed(b) else 0
            self.write_reg(rd, r); self.set_flags(r)
        elif op == OPCODES["LDI"]:
            self.write_reg(rd, imm & MASK); self.set_flags(imm)
        elif op == OPCODES["LD"]:
            self.write_reg(rd, self.mem[(a + imm) & MASK])
        elif op == OPCODES["ST"]:
            self.mem[(a + imm) & MASK] = self.reg[rd]
        elif op == OPCODES["BEZ"]:
            if a == 0:
                self.pc = (self.pc + imm) & MASK    # relative to PC-after-increment
        elif op == OPCODES["BNZ"]:
            if a != 0:
                self.pc = (self.pc + imm) & MASK
        elif op == OPCODES["JMP"]:
            if addr == ((self.pc - 1) & 0xFFF):     # jump to self = halt idiom
                self.halted = True
            self.pc = addr
        elif op == OPCODES["JAL"]:
            self.write_reg(7, self.pc)
            self.pc = addr
        return instruction

    @staticmethod
    def _ovf(a, b, raw):
        """Signed overflow: both operands same sign, result differs."""
        sa, sb, sr = (a >> 15) & 1, (b >> 15) & 1, (raw >> 15) & 1
        return 1 if sa == sb and sr != sa else 0

    def run(self, max_cycles=10000):
        while not self.halted and self.cycles < max_cycles:
            self.step()
        return self.halted

    def dump(self):
        regs = "  ".join(f"R{i}={self.reg[i]:5d}" for i in range(8))
        f = "".join(k for k, v in self.flags.items() if v) or "-"
        return f"PC={self.pc:04x}  {regs}  flags={f}"


def assemble(source):
    """Two-pass assembler: pass 1 collects labels, pass 2 emits words."""
    lines = []
    for raw in source.strip().splitlines():
        line = raw.split(";")[0].strip()
        if line:
            lines.append(line)

    # Pass 1 -- label addresses
    labels, address = {}, 0
    for line in lines:
        if ":" in line:
            label, _, rest = line.partition(":")
            labels[label.strip()] = address
            if not rest.strip():
                continue
        address += 1

    # Pass 2 -- encode
    program, address = [], 0
    for line in lines:
        if ":" in line:
            _, _, line = line.partition(":")
            line = line.strip()
            if not line:
                continue
        parts = line.replace(",", " ").split()
        mnemonic, args = parts[0].upper(), parts[1:]
        op = OPCODES[mnemonic]

        def reg(token):
            return int(token.upper().lstrip("R"))

        if mnemonic == "NOP":
            word = 0
        elif mnemonic in R_TYPE:
            word = (op << 12) | (reg(args[0]) << 9) | (reg(args[1]) << 6) \
                   | (reg(args[2]) << 3)
        elif mnemonic == "LDI":
            word = (op << 12) | (reg(args[0]) << 9) | (int(args[1], 0) & 0x3F)
        elif mnemonic in ("LD", "ST"):
            word = (op << 12) | (reg(args[0]) << 9) | (reg(args[1]) << 6) \
                   | (int(args[2], 0) & 0x3F)
        elif mnemonic in ("BEZ", "BNZ"):
            target = labels[args[1]] if args[1] in labels else int(args[1], 0)
            offset = target - (address + 1)          # relative to PC-after-increment
            assert -32 <= offset <= 31, f"branch out of range: {offset}"
            word = (op << 12) | (reg(args[0]) << 6) | (offset & 0x3F)
        elif mnemonic in J_TYPE:
            target = labels[args[0]] if args[0] in labels else int(args[0], 0)
            word = (op << 12) | (target & 0xFFF)
        else:
            raise ValueError(mnemonic)
        program.append(word)
        address += 1
    return program, labels


REFERENCE_PROGRAM = """
        LDI  R1, 0          ; sum = 0
        LDI  R2, 10         ; i = 10
loop:   ADD  R1, R1, R2     ; sum += i
        LDI  R3, 1
        SUB  R2, R2, R3     ; i -= 1
        BNZ  R2, loop       ; repeat while i != 0
halt:   JMP  halt           ; spin forever
"""

if __name__ == "__main__":
    program, labels = assemble(REFERENCE_PROGRAM)
    print("ASSEMBLED the reference program:")
    print(f"  {'addr':>5s} {'word':>7s} {'binary':>20s}")
    for i, word in enumerate(program):
        label = next((k for k, v in labels.items() if v == i), "")
        print(f"  {i:5d} {word:#07x} {word:016b}  {label}")
    print(f"  labels: {labels}")
    print()

    cpu = Prime1()
    cpu.load(program)
    print("EXECUTING (first 12 cycles):")
    for _ in range(12):
        if cpu.halted:
            break
        instruction = cpu.step()
        print(f"  {instruction:016b}  {cpu.dump()}")
    print("  ...")
    cpu.run()
    print()
    print(f"HALTED after {cpu.cycles} cycles")
    print(f"  {cpu.dump()}")
    print(f"  R1 = {cpu.reg[1]}   (expected 55)")

    assert cpu.reg[1] == 55, f"expected 55, got {cpu.reg[1]}"
    assert cpu.halted

    # R0 really is hardwired
    c2 = Prime1(); c2.load(assemble("LDI R0, 42\nhalt: JMP halt")[0]); c2.run()
    assert c2.reg[0] == 0, "R0 must stay zero"

    # Sign extension: a negative immediate
    c3 = Prime1(); c3.load(assemble("LDI R1, -1\nhalt: JMP halt")[0]); c3.run()
    assert c3.reg[1] == 0xFFFF, f"sign extension broken: {c3.reg[1]:#x}"

    # SLT is signed
    c4 = Prime1()
    c4.load(assemble("LDI R1, -1\nLDI R2, 1\nSLT R3, R1, R2\nhalt: JMP halt")[0])
    c4.run()
    assert c4.reg[3] == 1, "signed comparison broken"

    print()
    print("prime1: passed")
```

Expected output:

```
ASSEMBLED the reference program:
   addr    word               binary
      0 0x09200 1001001000000000  
      1 0x0940a 1001010000001010  
      2 0x01250 0001001001010000  loop
      3 0x09601 1001011000000001  
      4 0x02498 0010010010011000  
      5 0x0d0bc 1101000010111100  
      6 0x0e006 1110000000000110  halt
  labels: {'loop': 2, 'halt': 6}

EXECUTING (first 12 cycles):
  1001001000000000  PC=0001  R0=    0  R1=    0  R2=    0  R3=    0  R4=    0  R5=    0  R6=    0  R7=    0  flags=Z
  1001010000001010  PC=0002  R0=    0  R1=    0  R2=   10  R3=    0  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  0001001001010000  PC=0003  R0=    0  R1=   10  R2=   10  R3=    0  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  1001011000000001  PC=0004  R0=    0  R1=   10  R2=   10  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  0010010010011000  PC=0005  R0=    0  R1=   10  R2=    9  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=C
  1101000010111100  PC=0002  R0=    0  R1=   10  R2=    9  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=C
  0001001001010000  PC=0003  R0=    0  R1=   19  R2=    9  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  1001011000000001  PC=0004  R0=    0  R1=   19  R2=    9  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  0010010010011000  PC=0005  R0=    0  R1=   19  R2=    8  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=C
  1101000010111100  PC=0002  R0=    0  R1=   19  R2=    8  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=C
  0001001001010000  PC=0003  R0=    0  R1=   27  R2=    8  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  1001011000000001  PC=0004  R0=    0  R1=   27  R2=    8  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=-
  ...

HALTED after 43 cycles
  PC=0006  R0=    0  R1=   55  R2=    0  R3=    1  R4=    0  R5=    0  R6=    0  R7=    0  flags=ZC
  R1 = 55   (expected 55)

prime1: passed
```

## Reading the trace

The execution trace is the most useful thing this track produces. Follow the loop:

```
0001001001010000  PC=0003  R1=   10  R2=   10   <- ADD R1,R1,R2  (sum += i)
1001011000000001  PC=0004  R1=   10  R3=    1   <- LDI R3,1
0010010010011000  PC=0005  R2=    9        C    <- SUB R2,R2,R3  (i -= 1)
1101000010111100  PC=0002                  C    <- BNZ taken: PC 6 -> 2
```

**Look at the last line.** The BNZ is at address 5; after fetch PC is 6; the encoded offset is `111100` = $-4$; $6 + (-4) = 2$, the loop label. **That is the off-by-one made visible**, and it is why the emulator is worth writing before the hardware.

Note also the `C` flag set by `SUB`: it indicates *no borrow* (i.e. $R2 \geq R3$), which is the unsigned "greater or equal" test from [[how-computers-work/05-combinational/03-multipliers-and-comparators|module 21]].

## The parts that will bite you

- **`JMP` to self as the halt idiom.** PRIME-1 has no `HLT` opcode — the spec spends all 16 codes elsewhere. `JMP halt` where `halt` is its own address spins forever; the emulator detects it and stops. **On real hardware it genuinely spins**, which is what a halt loop is.
- **Flags on non-arithmetic instructions.** Decide whether `AND` sets C and V, and *write it in the spec*. The emulator here clears them. Any track that disagrees will fail differential testing.
- **`assemble()` label handling with an instruction on the same line.** `loop: ADD R1,R1,R2` defines a label *and* emits an instruction. Pass 1 must not double-count the address.
- **Branch range.** A 6-bit signed offset reaches $-32$ to $+31$. The assembler asserts this; without the assert you get silent wraparound.

## Extending it into a debugger

Once it runs, ~30 more lines make it genuinely useful:

- `break(addr)` — a set of addresses; stop when PC hits one
- `watch(reg)` — print whenever a register changes
- `disassemble(word)` — the inverse of the assembler, for reading memory dumps
- `run_until(condition)` — step until a predicate holds

**The disassembler is the highest-value addition**, because it lets you print memory as instructions and check what your assembler actually produced.

## How to know it works

1. **Per-opcode tests** — 16 of them, each asserting result and flags.
2. **The reference program** — R1 = 55 after 43 cycles.
3. **The four assertions in `__main__`** — R0 hardwiring, sign extension, signed `SLT`, and halting.
4. **Round-trip** — assemble, disassemble, compare with the source.

**Then keep it.** This file is the oracle for tracks 1, 2 and 4. When your Verilog produces 54 instead of 55, you run both cycle by cycle and diff the register dumps until they diverge — and that cycle is your bug.

## Where to stop

**Stop when the reference program gives 55 and your tests pass.** Resist adding instructions until another track needs them.

The natural next step is not more features — it is **building the same machine in a different medium** and discovering which parts of your spec were ambiguous.

## Related

- [[build-your-own-shit/17-your-own-cpu/index|PRIME-1 index and ISA spec]]
- [[build-your-own-shit/17-your-own-cpu/01-digital-simulator|Track 1 — Digital simulator]] — build it as a circuit
- [[build-your-own-shit/17-your-own-cpu/02-verilog|Track 2 — Verilog]]
- [[build-your-own-shit/17-your-own-cpu/04-breadboard|Track 4 — Breadboard]]
- [[how-computers-work/06-memory/02-registers-and-counters|module 24]] — the register file and PC this emulates
- [[build-your-own-shit/04-your-own-language|Your Own Language]] — the compiler that will target this ISA
