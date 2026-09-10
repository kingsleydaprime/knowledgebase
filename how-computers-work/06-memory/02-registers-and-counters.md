# Module 25: Registers and Counters (From One Bit to a Machine That Steps)

**[Intermediate]** — A flip-flop holds one bit. This module scales that to words, builds the register file a CPU reads its operands from, and constructs the **program counter** — the single register that turns a calculator into a computer.

## Before you start

- You know how a flip-flop stores a bit and why it is edge-triggered — [[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]].
- You can build decoders and multiplexers — [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]].
- You can build an adder, so you can build an incrementer — [[how-computers-work/05-combinational/02-adders|module 21]].

**After this lesson you will be able to:**

1. Build a multi-bit register with load enable, and explain why "hold" is implemented as a multiplexer.
2. Build shift registers and explain how serial links become parallel data.
3. Build counters and explain why they wrap.
4. Build a register file from a decoder and multiplexers, and explain how a program counter implements all control flow.

**Study route:** section 6 (register file) is where modules 19 and 23 combine. Section 7 (program counter) is the one that changes what the machine *is*.

---

## 1. Why this exists (real-world motivation)

Module 24 produced a device that stores one bit. Useful, and a long way from a computer.

**Three things are missing:**

1. **Width.** Values are words, not bits. You need to store all 8 or 32 or 64 bits together, updating as a unit.
2. **Addressability.** A CPU has many registers and must read *two specific ones* and write *one specific one*, chosen by bits in the instruction.
3. **Sequence.** Something must decide *which instruction runs next* — and update itself every cycle.

**Each is built from parts you already have.** No new primitive appears in this module: registers are flip-flops in parallel, addressing is the decoder and multiplexer from [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]], and the program counter is a register wired to an incrementer.

**That third item is the important one.** Everything so far computes a value. The program counter makes the machine *go somewhere next*, and that is the difference between a calculator and a computer.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Register** | $n$ flip-flops sharing a clock, storing one word |
| **Load enable** | Control deciding whether a register updates this cycle |
| **Shift register** | A register whose contents move one position per clock |
| **SIPO / PISO** | Serial-in parallel-out / parallel-in serial-out |
| **Counter** | A register that increments itself |
| **Ripple counter** | Asynchronous — each stage clocks the next |
| **Synchronous counter** | All stages share one clock |
| **Register file** | A small addressable array of registers with read and write ports |
| **Port** | One independent read or write path |
| **Program counter (PC)** | The register holding the address of the next instruction |

---

## 3. A register is flip-flops in parallel

An $n$-bit register is $n$ flip-flops sharing a clock line. On each edge, all of them capture simultaneously.

```
        D7 D6 D5 D4 D3 D2 D1 D0
         │  │  │  │  │  │  │  │
        ┌▼┐┌▼┐┌▼┐┌▼┐┌▼┐┌▼┐┌▼┐┌▼┐
        │F││F││F││F││F││F││F││F│    8 flip-flops
        └┬┘└┬┘└┬┘└┬┘└┬┘└┬┘└┬┘└┬┘
   clk ──┴──┴──┴──┴──┴──┴──┴──┘     one shared clock
         │  │  │  │  │  │  │  │
        Q7 Q6 Q5 Q4 Q3 Q2 Q1 Q0
```

### Load enable is a multiplexer

A register usually should **not** update every cycle. But a flip-flop has no "do nothing" input — it captures whatever is on D at every edge.

**The solution is to change what D is connected to.** Put a 2-to-1 MUX in front:

```
   data_in ──►┐
              │ MUX ──► D ──►[ FLIP-FLOP ]──┬──► Q
        ┌────►┘                             │
        │      ▲                            │
        │   load_enable                     │
        └───────────────────────────────────┘
                    feedback
```

- `load_enable = 1` → D gets the new data.
- `load_enable = 0` → **D gets the register's own output.** It reloads itself with what it already had.

**"Holding" is implemented as "writing the same value back".** The flip-flop still captures every single cycle; it just captures its own output. This is worth internalising — there is no idle state in synchronous hardware, only values being continuously recirculated.

---

## 4. Shift registers — the bridge between serial and parallel

Wire each flip-flop's output to the next one's input, and every clock edge moves the whole contents one position.

```
   serial in ──►[F]──►[F]──►[F]──►[F]──► serial out
                 │     │     │     │
                Q0    Q1    Q2    Q3     parallel out
```

Shifting eight bits in one at a time turns a serial stream into a parallel byte:

```
   after bit 0 (1): 00000001
   after bit 3 (1): 00001011
   after bit 7 (0): 10110010   <- one complete byte
```

**There are four configurations**, named by how data enters and leaves:

| Name | In | Out | Used for |
| :--- | :--- | :--- | :--- |
| **SISO** | serial | serial | Delay lines — data emerges $n$ clocks later |
| **SIPO** | serial | parallel | **Receiving**: a wire becomes a word |
| **PISO** | parallel | serial | **Transmitting**: a word becomes a wire |
| **PIPO** | parallel | parallel | Just an ordinary register (module 25's first section) |

**SIPO and PISO are the pair that matter**, and together they are a serial link: PISO at the transmitter shifts a byte out one bit at a time, SIPO at the receiver shifts it back in. That is UART, SPI and every shift-register LED driver you will ever wire.

**This is how essentially every serial interface works** — UART, SPI, I²C, USB, Ethernet. A wire carries one bit at a time; a shift register accumulates them into a word the rest of the system can use. Run it the other way (PISO) to transmit.

It is also how the **barrel shifter** of [[how-computers-work/05-combinational/04-the-alu|module 23]] differs: a shift register shifts *over time*, one position per clock. A barrel shifter shifts *in space*, any distance in one cycle. Same operation, completely different cost and use.

---

## 5. Counters — a register that feeds its own incrementer

```
        ┌──────────────┐
        │   REGISTER   ├──┬──► count
        └──────▲───────┘  │
               │          │
        ┌──────┴───────┐  │
        │  +1 ADDER    │◄─┘
        └──────────────┘
```

That is the entire design. The adder is the one from [[how-computers-work/05-combinational/02-adders|module 21]] with one input tied to the constant 1 — which simplifies to an **incrementer**, cheaper than a full adder because one operand is known.

A 4-bit counter produces `1, 2, ... 15, 0, 1, 2, ...` — **wrapping is not a bug.** With $n$ bits there are only $2^n$ values, so the carry out of the top bit has nowhere to go and is discarded. Counters are inherently modulo-$2^n$.

> [!NOTE]
> **Synchronous versus ripple counters.** A *ripple* counter uses each stage's output as the next stage's clock. It is very cheap and subtly broken: stages change at different times, so during transitions the counter briefly shows wrong values — `0111 → 0110 → 0100 → 0000 → 1000` on its way from 7 to 8.
>
> Any logic reading it during that window sees garbage. A *synchronous* counter clocks all stages together, so all bits change at once. **Use synchronous counters for anything that will be decoded**, and ripple counters only for slow, uncritical things like blinking an LED.

---

## 6. The register file — where modules 19 and 23 meet

A CPU needs many registers, with the instruction naming which to use. `ADD R3, R5` must read R3 and R5 and write the result, all in one cycle.

**Two operations, two module 20 primitives:**

- **Reading is a multiplexer.** The register address selects which register's output reaches the read port. It is combinational — no clock needed, the value is just *there*.
- **Writing is a decoder.** The write address is decoded to one-hot, and each register's load enable is that one-hot bit ANDed with a global write enable. **Exactly one register loads; every other holds.**

```
                        ┌──────────────┐
   write_addr ─────────►│   DECODER    │
   write_enable ───────►│              │
                        └──┬──┬──┬──┬──┘
                           │  │  │  │      one-hot load enables
                        ┌──▼┐┌─▼┐┌─▼┐┌─▼┐
   write_data ─────────►│R0││R1││R2││R3│  ... registers
                        └─┬┘└─┬┘└─┬┘└─┬┘
                          └───┴───┴───┴──┬──────────┐
                                    ┌────▼────┐┌────▼────┐
   read_addr_a ────────────────────►│  MUX A  ││  MUX B  │◄─ read_addr_b
                                    └────┬────┘└────┬────┘
                                     read_a      read_b
```

**A real CPU register file is exactly this**, typically with two read ports and one write port — precisely what a three-operand instruction needs. Extra ports cost real area: a second write port means another decoder and another input to every register's MUX, which is why superscalar processors with many ports have surprisingly large register files.

---

## 7. The program counter — the machine becomes sequential

Everything until now computes values. **The program counter decides what happens next**, and it is the smallest, most consequential register in the machine.

```
        ┌─────────────┐
        │     PC      ├──┬──► instruction address (to memory)
        └──────▲──────┘  │
               │         │
          ┌────┴────┐    │
          │   MUX   │    │
          └─▲─────▲─┘    │
            │     │      │
     +1 ────┘     └──── branch_target
      ▲
      └──────────────────┘
```

Three cases, and they are all of control flow:

| Situation | Next PC | The program construct |
| :--- | :--- | :--- |
| Normal | PC + 1 | sequential execution |
| Branch taken | branch target | `if`, loops, `goto` |
| Stall | PC (unchanged) | waiting on memory |

The lab's trace:

```
   cycle 0    fetch next              -> 0x1
   cycle 1    fetch next              -> 0x2
   cycle 2    branch taken to 0x40    -> 0x40
   cycle 3    fetch next              -> 0x41
   cycle 4    stalled (memory wait)   -> 0x41
   cycle 5    fetch next              -> 0x42
```

> [!NOTE]
> **This is the whole of control flow, and it is smaller than anyone expects.**
>
> Every `if`, every `while`, every function call, every `return`, every exception, every thread switch — all of it, in every program ever written, is **this register being loaded with a different value.**
>
> A conditional branch is: compute a condition in the ALU ([[how-computers-work/05-combinational/04-the-alu|module 23]]), use its flag to drive the MUX select, and the PC either increments or loads the target. A function call additionally saves the old PC so `return` can restore it.
>
> **The machine has no concept of a loop.** It only ever does "PC + 1" or "PC = something else". Loops are what *we* call it when the something-else points backwards.
>
> And note the significance: an incrementer plus a MUX plus a register has turned a combinational calculator into a machine that **executes a sequence**. That is the last structural piece a processor needs.

---

## 8. Predict before reading on

A register file has 2 read ports and 1 write port. An instruction does `ADD R3, R3, R5` — reading R3, and writing R3 in the same cycle.

**What value does the read port see: the old R3 or the new one?**

<details><summary>Check your answer</summary>

**The old one.** Reads are combinational and reflect the registers' *current* outputs. The write only takes effect at the clock edge, at the end of the cycle. So during the cycle, the read port sees the pre-write value — which is exactly what `R3 = R3 + R5` requires.

**This is why edge-triggered flip-flops matter so much** ([[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]). If the register file used transparent latches, the new value could race back around to the read port mid-cycle and be added to itself again. The design would be unreliable and temperature-dependent.

**The subtlety returns in pipelined processors.** There, the write may happen several cycles after the read, so a later instruction can read a stale value — a **read-after-write hazard**, solved by forwarding or stalling. That is [[computer-architecture/06-pipelining|computer-architecture/pipelining]], and the problem originates in exactly this timing question.
</details>

---

## 9. Worked example — runnable

Save as `register_lab.py` and run `python3 register_lab.py`.

```python
"""From one bit to a word, to a register file, to the program counter."""

WIDTH = 8
MASK = (1 << WIDTH) - 1

class Register:
    """WIDTH flip-flops sharing one clock and one load-enable.

    Load enable is NOT a separate kind of flip-flop -- it is a MUX in
    front of the D input, choosing between the new value and the
    register's own output. 'Hold' is implemented as 'reload yourself'."""
    def __init__(self, width=WIDTH):
        self.value = 0
        self.width = width

    def clock_edge(self, data_in, load_enable):
        d = data_in if load_enable else self.value      # <- the MUX
        self.value = d & ((1 << self.width) - 1)
        return self.value

class ShiftRegister:
    """Serial in, parallel out -- and parallel in, serial out."""
    def __init__(self, width=WIDTH):
        self.value = 0
        self.width = width

    def shift_in(self, bit):
        """One bit enters at the LSB, everything moves up, MSB falls off."""
        out_bit = (self.value >> (self.width - 1)) & 1
        self.value = ((self.value << 1) | (bit & 1)) & ((1 << self.width) - 1)
        return out_bit

    def load(self, value):
        self.value = value & ((1 << self.width) - 1)

class Counter:
    """A register wired to its own incrementer. That is the whole design."""
    def __init__(self, width=WIDTH):
        self.reg = Register(width)
        self.width = width

    def clock_edge(self, enable=1, load=0, load_value=0):
        if load:
            nxt = load_value
        elif enable:
            nxt = (self.reg.value + 1) & ((1 << self.width) - 1)
        else:
            nxt = self.reg.value
        return self.reg.clock_edge(nxt, 1)

class RegisterFile:
    """What a CPU actually has: N registers, 2 read ports, 1 write port.

    Reading = a MUX selecting one register (module 20).
    Writing = a DECODER enabling exactly one register (module 20).
    The register file is those two blocks wrapped around an array."""
    def __init__(self, n_registers=8, width=WIDTH):
        self.regs = [Register(width) for _ in range(n_registers)]
        self.n = n_registers

    def read(self, addr_a, addr_b):
        """Two combinational reads -- MUXes, no clock needed."""
        return self.regs[addr_a].value, self.regs[addr_b].value

    def clock_edge(self, write_addr, write_data, write_enable):
        """One synchronous write, steered by a decoder."""
        for i, reg in enumerate(self.regs):
            enable_this = write_enable and (i == write_addr)   # <- the DECODER
            reg.clock_edge(write_data, enable_this)

class ProgramCounter:
    """The register that makes a machine SEQUENTIAL rather than combinational.

    next_pc = MUX(branch_taken, pc + 1, branch_target)"""
    def __init__(self, width=16):
        self.reg = Register(width)
        self.width = width

    def clock_edge(self, branch_taken=0, branch_target=0, stall=0):
        if stall:
            nxt = self.reg.value
        elif branch_taken:
            nxt = branch_target
        else:
            nxt = (self.reg.value + 1) & ((1 << self.width) - 1)
        return self.reg.clock_edge(nxt, 1)

if __name__ == "__main__":
    print("REGISTER -- load enable is a MUX, not a special flip-flop")
    r = Register()
    print(f"  {'edge':>5s} {'data_in':>8s} {'load':>5s} {'-> value':>9s}")
    for data, load in [(0xA5, 1), (0x3C, 0), (0x3C, 1), (0xFF, 0)]:
        v = r.clock_edge(data, load)
        note = "loaded" if load else "held (fed itself back)"
        print(f"  {'^':>5s} {data:#8x} {load:5d} {v:#9x}   {note}")
    print()

    print("SHIFT REGISTER -- serial to parallel conversion")
    sr = ShiftRegister()
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    print(f"  shifting in {bits} one bit per clock:")
    for i, b in enumerate(bits):
        sr.shift_in(b)
        print(f"    after bit {i} ({b}): {sr.value:08b}")
    print(f"  8 serial bits became one parallel byte: {sr.value:#04x}")
    print("  -> this is how a UART, SPI or any serial link receives data")
    print()

    print("COUNTER -- a register wired to its own incrementer")
    c = Counter(width=4)
    seq = []
    for _ in range(18):
        seq.append(c.clock_edge())
    print(f"  counting: {seq}")
    print(f"  wraps at 2^4 = 16 back to 0 -- counters are modular by nature")
    print()

    print("REGISTER FILE -- 8 registers, 2 read ports, 1 write port")
    rf = RegisterFile(n_registers=8)
    rf.clock_edge(write_addr=3, write_data=0x2A, write_enable=1)
    rf.clock_edge(write_addr=5, write_data=0x11, write_enable=1)
    a, b = rf.read(3, 5)
    print(f"  wrote R3=0x2A, R5=0x11")
    print(f"  read ports: R3={a:#04x}, R5={b:#04x}  (both in the same cycle)")
    rf.clock_edge(write_addr=3, write_data=0xFF, write_enable=0)
    print(f"  write with enable=0: R3={rf.read(3,0)[0]:#04x}  (unchanged)")
    print("  -> ADD R3, R5 needs exactly this: two reads and one write per cycle")
    print()

    print("PROGRAM COUNTER -- the seed of control flow")
    pc = ProgramCounter(width=8)
    print(f"  {'cycle':>6s} {'action':>26s} {'-> PC':>7s}")
    actions = [(0, 0, 0, "fetch next"), (0, 0, 0, "fetch next"),
               (1, 0x40, 0, "branch taken to 0x40"), (0, 0, 0, "fetch next"),
               (0, 0, 1, "stalled (memory wait)"), (0, 0, 0, "fetch next")]
    for i, (taken, target, stall, label) in enumerate(actions):
        v = pc.clock_edge(taken, target, stall)
        print(f"  {i:6d} {label:>26s} {v:#7x}")
    print()
    print("  every program that has ever run is this register being updated.")
    print("  sequential execution = PC + 1. a branch = load a different value.")
    print("  that is the ENTIRE mechanism of control flow.")

    assert Register().clock_edge(0xAB, 1) == 0xAB
    r2 = Register(); r2.clock_edge(0xAB, 1)
    assert r2.clock_edge(0x00, 0) == 0xAB          # hold really holds
    c2 = Counter(width=3)
    assert [c2.clock_edge() for _ in range(9)] == [1,2,3,4,5,6,7,0,1]
    rf2 = RegisterFile(4)
    rf2.clock_edge(2, 0x77, 1)
    assert rf2.read(2, 0) == (0x77, 0)
    print()
    print("register_lab: passed")
```

Expected output:

```
REGISTER -- load enable is a MUX, not a special flip-flop
   edge  data_in  load  -> value
      ^     0xa5     1      0xa5   loaded
      ^     0x3c     0      0xa5   held (fed itself back)
      ^     0x3c     1      0x3c   loaded
      ^     0xff     0      0x3c   held (fed itself back)

SHIFT REGISTER -- serial to parallel conversion
  shifting in [1, 0, 1, 1, 0, 0, 1, 0] one bit per clock:
    after bit 0 (1): 00000001
    after bit 1 (0): 00000010
    after bit 2 (1): 00000101
    after bit 3 (1): 00001011
    after bit 4 (0): 00010110
    after bit 5 (0): 00101100
    after bit 6 (1): 01011001
    after bit 7 (0): 10110010
  8 serial bits became one parallel byte: 0xb2
  -> this is how a UART, SPI or any serial link receives data

COUNTER -- a register wired to its own incrementer
  counting: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2]
  wraps at 2^4 = 16 back to 0 -- counters are modular by nature

REGISTER FILE -- 8 registers, 2 read ports, 1 write port
  wrote R3=0x2A, R5=0x11
  read ports: R3=0x2a, R5=0x11  (both in the same cycle)
  write with enable=0: R3=0x2a  (unchanged)
  -> ADD R3, R5 needs exactly this: two reads and one write per cycle

PROGRAM COUNTER -- the seed of control flow
   cycle                     action   -> PC
       0                 fetch next     0x1
       1                 fetch next     0x2
       2       branch taken to 0x40    0x40
       3                 fetch next    0x41
       4      stalled (memory wait)    0x41
       5                 fetch next    0x42

  every program that has ever run is this register being updated.
  sequential execution = PC + 1. a branch = load a different value.
  that is the ENTIRE mechanism of control flow.

register_lab: passed
```

Note that `Register.clock_edge` contains the line `d = data_in if load_enable else self.value` — **that ternary is the multiplexer**, and `self.value` on the right-hand side is the feedback wire. The class never has a "do nothing" branch, because the hardware never does nothing.

---

## 10. Common pitfalls and traps

1. **Thinking a register can idle.** Every flip-flop captures on every edge. Holding is implemented by feeding the output back through a MUX.
2. **Using a ripple counter where the value is decoded.** Its bits change at different times, so intermediate garbage appears. Use synchronous counters.
3. **Forgetting counters wrap.** An 8-bit counter goes 255 → 0. If that matters, detect the wrap explicitly.
4. **Assuming more register-file ports are cheap.** Each read port adds a full MUX; each write port adds a decoder and another MUX input per register.
5. **Expecting a same-cycle write to be visible to a same-cycle read.** It is not — the write lands at the edge.
6. **Treating the PC as special hardware.** It is an ordinary register plus an incrementer and a MUX.

---

## 11. Check your understanding

1. **Why does a register need a MUX for load enable, rather than gating the clock?**
   <details><summary>Answer</summary>
   Gating the clock — ANDing it with an enable — <em>does</em> work and is used, but it is dangerous: the gate adds delay, so the gated clock arrives skewed relative to the main clock, and any glitch on the enable becomes a spurious clock edge that corrupts the register.<br>
   A data MUX keeps the clock pristine and global. <strong>Clock gating is used deliberately for power saving</strong> ([[how-computers-work/03-transistors/03-cmos|module 13]]) but with carefully designed gating cells, not ad-hoc AND gates.
   </details>

2. **A 32-register file with 2 read ports. How many 32-to-1 MUXes and how wide?**
   <details><summary>Answer</summary>
   <strong>Two</strong> 32-to-1 MUXes, each <strong>32 bits wide</strong> — so 64 individual 32-to-1 bit MUXes. From [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]], a 32-to-1 MUX built from 2-to-1s needs 31 of them, so roughly <strong>1,984 two-input MUXes</strong> just for reading.<br>
   This is why register files are a substantial fraction of a core's area and why ISAs do not simply provide hundreds of registers. The read MUX cost grows with register count, and so does the delay ($\log_2 n$ levels).
   </details>

3. **How does a function call work, in terms of the program counter?**
   <details><summary>Answer</summary>
   A call does two things: <strong>save the current PC + 1</strong> (the return address) somewhere — a link register or the stack — and then <strong>load the PC with the function's address</strong>.<br>
   A return loads the PC back from wherever the address was saved. That is all. <strong>The machine has no concept of "function"</strong>; it has "load the PC and remember where you were". Everything else — parameters, stack frames, calling conventions — is agreement between compiler and programmer, layered on top of this one mechanism.
   </details>

4. **Why is the program counter the component that makes a machine a computer?**
   <details><summary>Answer</summary>
   Every other block computes a function of its inputs — give an ALU two numbers and it produces a result, with no notion of "next".<br>
   The PC introduces <strong>sequence</strong>: the machine has a position in an instruction stream, and it advances. Combined with the ability to load the PC conditionally, it gains <strong>choice</strong>. Sequence plus choice plus memory is exactly what makes a system Turing-complete — so the PC is precisely the component that lifts the hardware from evaluating expressions to executing algorithms.
   </details>

---

## 12. Practice — independent task

**Task:** Build the state elements of a tiny CPU.

- **(a)** Implement a 16-register file, 8 bits wide, with 2 read ports and 1 write port. Verify reads are unaffected by a same-cycle write.
- **(b)** Add a hardware convention where register 0 always reads as 0 regardless of what is written (as in MIPS and RISC-V). Implement it and explain why an ISA would waste a register this way.
- **(c)** Build an 8-bit PC with increment, branch and stall.
- **(d)** Implement a **call/return** mechanism: add a link register, a `call(target)` that saves PC+1 and jumps, and a `ret()` that restores. Test nested calls two deep — and explain what breaks at three.
- **(e)** Replace the link register with a **stack pointer** and a small memory array so nesting works to any depth. What did that cost?
- **(f)** Wire it together: write an `execute(instruction)` supporting `ADD rd, ra, rb`, `LOADI rd, imm`, `JMP addr` and `BEQZ ra, addr`. Run a program that counts down from 5 to 0 and halts.
- **(g)** Trace your program cycle by cycle, printing PC, the instruction, and all register values. Confirm the loop executes exactly five times.

**Done when:** your countdown program runs to completion, the cycle trace shows the branch being taken exactly five times, and you can explain why register 0 being hardwired to zero simplifies the instruction set.

<details><summary>Hint for (b), only if stuck</summary>
Make the <em>read</em> path return 0 for address 0, and either ignore writes to it or let them happen harmlessly — the read is what matters.<br>
It is worth a register because it makes many operations free: <code>MOV rd, ra</code> becomes <code>ADD rd, ra, r0</code>; a comparison against zero needs no immediate; <code>NOP</code> becomes <code>ADD r0, r0, r0</code>. <strong>One hardwired constant removes the need for several instruction formats</strong> — a good trade, and you will make exactly this decision yourself in the capstone.
</details>

---

## 13. Tradeoffs and limits

- **Register files are not built from discrete flip-flops in practice.** They use custom SRAM-like cells with dedicated read/write ports — denser and faster than a MUX tree, and the reason register file design is a specialist job.
- **Port count is the dominant cost.** Area grows roughly with (ports)², which is why wide superscalar machines either accept huge register files or split them into clusters.
- **Clock distribution limits register count.** Every flip-flop needs the clock edge at nearly the same instant; skew across a large file eats timing margin.
- **This module ignores reset.** Real registers need a defined power-on state, adding a reset input to every flip-flop and a whole discipline about synchronous versus asynchronous reset.

---

## Before moving on

- [ ] Build a register with load enable and explain why hold is a MUX, not an idle state.
- [ ] Explain how a shift register converts between serial and parallel.
- [ ] Build a counter and explain wrapping, and when a ripple counter is unsafe.
- [ ] Build a register file and identify the decoder and the MUXes.
- [ ] Explain how the PC implements sequential execution, branching and function calls.

**Recap:** A register is $n$ flip-flops on a shared clock, with load enable implemented as a MUX feeding the output back — hardware never idles, it recirculates. Shift registers move contents one place per clock, bridging serial links and parallel words. A counter is a register wired to an incrementer, inherently modulo-$2^n$. A register file is [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]]'s decoder (for writing) and multiplexers (for reading) wrapped around an array of registers. The program counter — a register, an incrementer and a MUX — is the entire mechanism of control flow.

**Next:** [[how-computers-work/06-memory/03-memory-technology|Module 26 — Memory Technology]] closes Part VII. Registers are fast and enormous per bit; storing gigabytes needs a different bargain, and the six-transistor-versus-one-capacitor tradeoff is what produces the memory hierarchy.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/06-memory/01-latches-and-flip-flops|Module 24]] — the flip-flop being replicated here
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — the decoder and MUX inside every register file
- [[computer-architecture/05-the-datapath|computer-architecture/the datapath]] — where the register file and PC sit in a CPU
- [[computer-architecture/06-pipelining|computer-architecture/pipelining]] — read-after-write hazards, which start with this module's timing
