# Track 4 — The Breadboard (Touch the Machine)

**[Advanced]** — Weeks, not evenings. £150–250 of parts. Produces a **physical computer** you can put a scope on. The slowest track by a wide margin, and the one nobody who finishes it ever forgets.

## An honest warning before you buy anything

**Do not build 16-bit PRIME-1 on a breadboard.** A 16-bit bus is 16 wires, and every register, every MUX and every memory connection multiplies that. You would be hand-wiring well over a thousand connections, and a single loose one produces a fault that looks like a logic bug.

**Build an 8-bit cut-down: PRIME-1/8.** Same ISA structure, same control table, half the wires. Once it works you will understand exactly what widening it would involve, and you will not want to.

**Realistic expectations:**

| | |
| :--- | :--- |
| Chips | ~30–40 (74HC series) |
| Wires | 400–700 |
| Cost | £150–250 including tools |
| Time | 40–80 hours, spread over weeks |
| Most common outcome | **Abandoned at the register-file stage** |

**The failure mode is not conceptual, it is mechanical.** You will spend more time finding a wire that looks connected and isn't than you will spend thinking about architecture.

**So why do it?** Because after tracks 1–3, PRIME-1 is a diagram and a program. Here it is a board that draws current and gets warm, where you can put a scope probe on the carry line and *watch the ripple* from [[how-computers-work/05-combinational/02-adders|module 20]] as a real propagation delay. Some things only become real when they are physical.

## Prerequisites beyond the other tracks

**Do tracks 3 and 1 first.** Debugging hardware without a known-good reference implementation is miserable. You need to be able to say "on cycle 12 the emulator has R2 = 9, so what does my board have?"

**Tools you will actually need:**

- A **multimeter** (continuity mode is what you will live in)
- A **logic probe** or, far better, a cheap 8-channel **USB logic analyser** (~£15, and it turns a week of guessing into an afternoon)
- Solid-core 22 AWG hookup wire, pre-cut assortment
- Wire strippers and small flush cutters
- A stable **5 V bench supply** or a good USB breakout — not a phone charger

**An oscilloscope is optional.** A logic analyser is more useful for digital work and a tenth of the price.

## The build, scaled down

### PRIME-1/8 changes from the spec

| Aspect | PRIME-1 | PRIME-1/8 |
| :--- | :--- | :--- |
| Word size | 16 bits | **8 bits** |
| Registers | 8 | **4** (R0–R3, R0 = 0) |
| Address space | 4096 words | **16 words** |
| Instruction | 16 bits | **8 bits**: `[op:4][rd:2][ra:2]` |
| Immediates | 6-bit | **4-bit**, in a second byte where needed |

**Keep the control table identical in structure.** The signals are the same; only the widths shrink.

### Recommended chips

| Function | Chip | Notes |
| :--- | :--- | :--- |
| Registers | **74HC273** or **74HC377** | 8-bit D flip-flops; '377 has a clock enable, which saves logic |
| Bus drivers | **74HC245** / **74HC574** | Tri-state so multiple sources can share a bus |
| Adder | **74HC283** | 4-bit; two of them chain for 8-bit |
| Logic ops | **74HC86** (XOR), **74HC08**, **74HC32** | XOR also does the subtract inversion |
| Counter (PC) | **74HC161** | 4-bit synchronous with parallel load — load is your jump |
| Memory | **74HC189** or a small SRAM | 16×4 or 16×8 |
| **Control ROM** | **AT28C16 EEPROM** | **The key part — see below** |
| Clock | **NE555** + a debounced pushbutton | Manual step *and* free-run |
| Display | LEDs + **74HC245** buffers | Put LEDs on every bus |

> [!NOTE]
> **Use an EEPROM for the control unit, not discrete gates.**
>
> Building the control logic from AND/OR gates would take a dozen extra chips and be miserable to change. An EEPROM *is* a lookup table ([[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 19]]) — address it with the opcode, and its stored bytes are your control signals.
>
> **Better still, it makes the control unit editable.** Change an instruction's behaviour by reburning a chip rather than rewiring the board. This is exactly the "move the function from structure into data" idea from module 19, and here it saves you literal hours.
>
> This is also how Ben Eater's 8-bit computer does it, and it is the right call.

### Milestones — each one testable on its own

**The rule: never wire two subsystems before the first one works standing alone.**

1. **Power and clock.** Rails, decoupling caps, a 555 clock, a manual-step button, and one LED. *One evening.* If the LED blinks when you press the button, your foundations are sound.
2. **One register.** A '273 with LEDs on its outputs and switches on its inputs. Clock it, watch it latch. *This is [[how-computers-work/06-memory/01-latches-and-flip-flops|module 23]] in your hands.*
3. **A bus.** Two registers plus tri-state drivers. Move a value from one to the other. **Only one driver enabled at a time, ever** — two drivers fighting is a short ([[how-computers-work/01-electricity/03-circuit-laws|module 3]]) and will get hot.
4. **The ALU.** Two '283s plus XOR gates for subtract. Feed it two registers, display the result.
5. **The program counter.** A '161 counting, with parallel load for jumps.
6. **Instruction memory + the control EEPROM.** Now opcodes produce control signals. **Watch the signal LEDs change as you step through instructions** — this is the moment the machine stops being wires.
7. **Branches.** Zero-detect (an 8-input NOR) into the PC's load logic.
8. **Run the reference program.**

## The control ROM image

Burn this to the AT28C16. **It is generated from the same control table tracks 1 and 2 use**, so your board cannot silently disagree with your simulator.

Save as `control_rom.py` alongside `datapath.py` from track 1, and run `python3 control_rom.py`.

```python
"""Emit the PRIME-1 control table as an EEPROM image.

Imports the SAME control table the simulator and Verilog use, so the
breadboard's control ROM cannot drift from the other three tracks."""
from datapath import CONTROL, SIGNAL_NAMES

MNEMONICS = ["NOP","ADD","SUB","AND","OR","XOR","SHL","SHR",
             "SLT","LDI","LD","ST","BEZ","BNZ","JMP","JAL"]

# Bit assignment within the 16-bit control word. Group signals by which
# chip they drive so one EEPROM output byte feeds one part of the board.
BIT_LAYOUT = [
    ("RegWrite",  0), ("RegBSrc",   1), ("ALUSrc",    2),
    ("ALUOp",     3),                       # 3 bits: 3,4,5
    ("MemRead",   6), ("MemWrite",  7),     # ---- byte boundary ----
    ("MemToReg",  8), ("Branch",    9), ("BranchNot", 10),
    ("Jump",     11), ("Link",     12),
]

def control_word(opcode):
    """Pack one opcode's signals into a 16-bit EEPROM word."""
    values = dict(zip(SIGNAL_NAMES, CONTROL[opcode]))
    word = 0
    for name, bit in BIT_LAYOUT:
        v = values[name]
        if name == "ALUOp":
            word |= (v & 0x7) << bit        # 3-bit field
        else:
            word |= (1 << bit) if v else 0
    return word

def emit_listing():
    lines = [f"  {'op':>4s} {'mnem':>4s}  {'control word':>13s}  {'lo':>4s}"
             f"    {'hi':>4s}   asserted signals"]
    lines.append("  " + "-" * 76)
    for op in sorted(CONTROL):
        w = control_word(op)
        active = [n for n, v in zip(SIGNAL_NAMES, CONTROL[op])
                  if v and n != "ALUOp"]
        alu = dict(zip(SIGNAL_NAMES, CONTROL[op]))["ALUOp"]
        if alu:
            active.append(f"ALUOp={alu}")
        lines.append(f"  {op:04b} {MNEMONICS[op]:>4s}  {w:013b}"
                     f"  {w & 0xFF:#04x}    {(w >> 8) & 0xFF:#04x}"
                     f"   {', '.join(active) or '-'}")
    return "\n".join(lines)

def intel_hex(words):
    """Intel HEX -- what most EEPROM programmers expect."""
    out = []
    data = []
    for w in words:
        data += [w & 0xFF, (w >> 8) & 0xFF]
    for addr in range(0, len(data), 16):
        chunk = data[addr:addr + 16]
        n = len(chunk)
        rec = [n, (addr >> 8) & 0xFF, addr & 0xFF, 0x00] + chunk
        checksum = (-sum(rec)) & 0xFF
        out.append(":" + "".join(f"{b:02X}" for b in rec + [checksum]))
    out.append(":00000001FF")
    return "\n".join(out)

if __name__ == "__main__":
    print("CONTROL ROM -- generated from the same table tracks 1 and 2 use")
    print()
    print(emit_listing())
    print()

    words = [control_word(op) for op in range(16)]
    print("Intel HEX image (burn this to the control EEPROM):")
    print()
    for line in intel_hex(words).splitlines():
        print("  " + line)
    print()

    # Sanity: the packing must round-trip
    for op in range(16):
        w = control_word(op)
        vals = dict(zip(SIGNAL_NAMES, CONTROL[op]))
        assert bool(w & 1) == bool(vals["RegWrite"]), f"RegWrite wrong for {op:04b}"
        assert ((w >> 3) & 0x7) == vals["ALUOp"], f"ALUOp wrong for {op:04b}"
    # ST must assert RegBSrc and MemWrite and nothing else that writes a register
    st = control_word(0b1011)
    assert st & (1 << 1) and st & (1 << 7) and not (st & 1)
    print("control_rom: passed")
```

Expected output:

```
CONTROL ROM -- generated from the same table tracks 1 and 2 use

    op mnem   control word    lo      hi   asserted signals
  ----------------------------------------------------------------------------
  0000  NOP  0000000000000  0x00    0x00   -
  0001  ADD  0000000000001  0x01    0x00   RegWrite
  0010  SUB  0000000001001  0x09    0x00   RegWrite, ALUOp=1
  0011  AND  0000000010001  0x11    0x00   RegWrite, ALUOp=2
  0100   OR  0000000011001  0x19    0x00   RegWrite, ALUOp=3
  0101  XOR  0000000100001  0x21    0x00   RegWrite, ALUOp=4
  0110  SHL  0000000101001  0x29    0x00   RegWrite, ALUOp=5
  0111  SHR  0000000110001  0x31    0x00   RegWrite, ALUOp=6
  1000  SLT  0000000111001  0x39    0x00   RegWrite, ALUOp=7
  1001  LDI  0000000000101  0x05    0x00   RegWrite, ALUSrc
  1010   LD  0000101000101  0x45    0x01   RegWrite, ALUSrc, MemRead, MemToReg
  1011   ST  0000010000110  0x86    0x00   RegBSrc, ALUSrc, MemWrite
  1100  BEZ  0001000000000  0x00    0x02   Branch
  1101  BNZ  0011000000000  0x00    0x06   Branch, BranchNot
  1110  JMP  0100000000000  0x00    0x08   Jump
  1111  JAL  1100000000001  0x01    0x18   RegWrite, Jump, Link

Intel HEX image (burn this to the control EEPROM):

  :100000000000010009001100190021002900310041
  :1000100039000500450186000002000600080118AD
  :00000001FF

control_rom: passed
```

**Note the bit layout is grouped deliberately.** Signals that drive the same part of the board share an EEPROM output byte, so one chip's outputs run to one region rather than criss-crossing the whole build. **Plan this before you wire, not after.**

## The parts that will bite you

These are hardware problems, and none of them look like logic bugs — which is what makes them expensive.

- **Missing decoupling capacitors.** Put a **0.1 µF ceramic across every chip's power pins**, right at the chip. Without them, switching current spikes cause supply droop that violates the noise margins of [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]], and your machine works "usually". *This causes more breadboard failures than anything else.*
- **Floating inputs.** A CMOS input left unconnected is not 0 — it floats, picks up noise, and oscillates. **Tie every unused input to VCC or GND.** This bites hardest on unused gates in a package you are only half using.
- **Bus contention.** Two tri-state drivers enabled at once fight; current is limited only by the chips. They get hot, then they die. Check enable logic before powering on.
- **Breadboard contact resistance.** Cheap breadboards develop intermittent contacts. A circuit that works when you press on it has a mechanical fault, not a design fault.
- **Long unshielded clock lines.** Ringing on a fast edge can double-clock a register. Keep clock runs short and consider a series resistor.
- **Power supply sag.** 40 chips plus LEDs can pull an amp. LEDs on every bus line are wonderful for debugging and a real load — use current limiting and a supply with headroom.
- **Switch bounce.** Your manual step button will produce several edges per press unless debounced. A 74HC14 Schmitt trigger with an RC, or a proper debounce circuit, is mandatory — otherwise the PC jumps 3 or 4 at a time and you will blame your logic.

## How to know it works

1. **Continuity-test every bus line before powering on.** Ten minutes with a multimeter saves hours.
2. **Test each subsystem standing alone** before connecting it to anything.
3. **LEDs on every bus and every control signal.** Being able to *see* the machine's state is the difference between debugging and guessing.
4. **Single-step, always, first.** Free-run only once the reference program completes.
5. **Diff against the emulator.** Step your board one cycle at a time and compare register LEDs with `prime1.py`'s trace. The cycle where they diverge is your bug.

## Where to stop

**Stop at milestone 6** if you are running out of enthusiasm. A board that fetches instructions and shows control signals lighting up already delivers most of the insight, and it is a genuine achievement.

**Stop at milestone 8** if you want the full thing. R1 = 55 on a row of LEDs, on a machine you wired by hand, is the end of this course.

**Do not** try to widen it to 16 bits, add pipelining, or attach real peripherals. Build the small one, understand it, and do the ambitious version on an FPGA in [[build-your-own-shit/17-your-own-cpu/02-verilog|track 2]] where wires are free.

## If you'd rather follow a proven design

**[Ben Eater's 8-bit breadboard computer](https://eater.net/8bit)** is the canonical version of this project — an excellent video series with a parts list, PCB options, and every mistake already made for you. Its architecture differs from PRIME-1/8 (it is bus-oriented with a microcoded control unit) but the concepts map directly.

**There is no shame in following it rather than my scaled spec.** A working machine you understand beats a half-built one of your own design. Build his, then modify the control EEPROM to add an instruction — that single change proves you understand the control unit, which is the real lesson.

## Related

- [[build-your-own-shit/17-your-own-cpu/index|PRIME-1 index and ISA spec]]
- [[build-your-own-shit/17-your-own-cpu/01-digital-simulator|Track 1]] — the control table this ROM is generated from
- [[build-your-own-shit/17-your-own-cpu/03-python-emulator|Track 3]] — the oracle to step against
- [[how-computers-work/03-transistors/04-making-a-chip|module 14]] — what you are doing by hand, done photographically
- [[foundations/hardware/index|hardware/]] — practical electronics, breadboarding and components
