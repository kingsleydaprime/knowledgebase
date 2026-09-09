# Module 23: The ALU (One Circuit, Many Operations)

**[Intermediate → Advanced]** — Part VI ends by wrapping the adder, the logic gates and a shifter behind a multiplexer. The result is the computational core of every processor — and the first circuit whose behaviour is chosen by *data*.

## Before you start

- You can build an adder/subtractor and compute the four flags — [[how-computers-work/05-combinational/02-adders|module 21]].
- You can build a multiplexer and know it costs $width$ copies to go word-wide — [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]].
- You know gate delays accumulate along the critical path — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].

**After this lesson you will be able to:**

1. Explain why an ALU computes every operation in parallel and then selects, rather than reconfiguring.
2. Build a barrel shifter and explain why it takes $\log_2 n$ stages rather than $n$.
3. Explain how the opcode field of an instruction connects directly to ALU select lines.
4. Explain why the ALU is usually on the critical path, and what that means for the whole processor.

**Study route:** section 3 is the design principle that surprises people. Section 6 is the connection to Part IX.

---

## 1. Why this exists (real-world motivation)

You can add, subtract, AND, OR, XOR and shift. Each is a separate circuit.

**A processor cannot afford a separate circuit per operation with separate wiring to memory and registers.** It needs *one* block that takes two operands plus a control code and produces whichever result the code names.

That block is the **Arithmetic Logic Unit**, and it is where a processor actually computes. Everything else in a CPU — registers, memory, control, the instruction pipeline — exists to feed the ALU operands and to put its results somewhere useful.

**It is also the first circuit in this course whose behaviour is selected at runtime by other bits.** Up to now every circuit did exactly one thing, fixed by its wiring. An ALU does eight things, and which one is decided by three input bits that arrive with the data. That shift — **from behaviour fixed by structure to behaviour selected by data** — is the seed of the stored-program computer.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **ALU** | Arithmetic Logic Unit — computes arithmetic and bitwise operations |
| **Opcode** | The control bits selecting which operation to perform |
| **Operand** | An input value to the operation |
| **Function select** | The ALU's opcode input, driving its internal MUX |
| **Barrel shifter** | Shifts by any amount in a fixed number of stages |
| **Arithmetic shift** | Right shift preserving the sign bit |
| **Logical shift** | Right shift filling with zeros |
| **SLT** | Set-Less-Than: outputs 1 if $A < B$, used for comparisons |
| **Flags / status register** | Z, N, C, V — the bits describing the result |

---

## 3. The design principle: compute everything, then select

The intuitive design would be a circuit that *reconfigures* itself — rewiring into an adder when told to add, into an AND array when told to AND.

**Real ALUs do the opposite, and it looks wasteful until you count the cost.**

```
              A ──┬──────┬──────┬──────┬─────┐
                  │      │      │      │     │
              B ──┼──┬───┼──┬───┼──┬───┼──┬──┤
                  ▼  ▼   ▼  ▼   ▼  ▼   ▼  ▼  ▼
               ┌─────┐┌─────┐┌─────┐┌─────┐┌──────┐
               │ ADD ││ AND ││ OR  ││ XOR ││SHIFT │   all run EVERY cycle
               └──┬──┘└──┬──┘└──┬──┘└──┬──┘└───┬──┘
                  └──────┴──────┴──────┴───────┘
                                │
                          ┌─────▼─────┐
              opcode ────►│    MUX    │
                          └─────┬─────┘
                                ▼
                             RESULT
```

**Every unit computes on every cycle, regardless of the opcode. The MUX throws away all but one result.**

Why this wins:

1. **There is no such thing as reconfigurable wiring.** Wires are fixed at manufacture. "Reconfiguring" would mean transistors switching connections — which is what the MUX *is*, so you have not avoided anything.
2. **Parallel evaluation costs no extra time.** The units run concurrently, so the delay is the slowest unit plus one MUX — not the sum.
3. **Gates are cheap; time is not.** An AND array for 8 bits is 8 gates. Adding a cycle of latency to every instruction is far more expensive than a few hundred spare transistors.

**The cost is power.** Every unit switches every cycle, so [[how-computers-work/03-transistors/03-cmos|module 13]]'s $\alpha C V^2 f$ is paid for results that get discarded. Modern designs claw some back with **operand isolation** — holding inputs steady on units whose result is not selected, so they do not switch — which is clock gating's cousin, applied inside the ALU.

---

## 4. The barrel shifter

Shifting looks like it should be a loop: shift by one, repeat $n$ times. **That would take $n$ stages of delay** and make shift-by-7 seven times slower than shift-by-1 — unacceptable when every instruction must fit one clock period.

**A barrel shifter does any shift in $\log_2 n$ stages.** Decompose the shift amount in binary: stage $k$ either shifts by $2^k$ or passes through, selected by bit $k$ of the amount.

```
   shift by 5 = binary 101

   stage 0 (shift 1?)  bit0 = 1  ->  shift by 1
   stage 1 (shift 2?)  bit1 = 0  ->  pass through
   stage 2 (shift 4?)  bit2 = 1  ->  shift by 4
                                     total: 5  ✓
```

Each stage is a row of 2-to-1 multiplexers — the module 20 primitive again. **Three stages cover every shift from 0 to 7; five stages cover a 32-bit shifter.**

Shift amount has no effect on delay: shifting by 7 costs exactly what shifting by 1 costs. **This is the same "convert a sequential dependency into a logarithmic tree" move as carry-lookahead in [[how-computers-work/05-combinational/02-adders|module 21]]** — the recurring shape of fast digital design.

---

## 5. Putting it together

An 8-bit ALU with a 3-bit opcode gives eight operations:

| Opcode | Operation | Notes |
| :--- | :--- | :--- |
| `000` | ADD | |
| `001` | SUB | adder with B inverted, carry-in 1 |
| `010` | AND | |
| `011` | OR | |
| `100` | XOR | |
| `101` | SHL | barrel shifter left |
| `110` | SHR | barrel shifter right |
| `111` | SLT | set-less-than — subtract, test sign |

**SLT is worth noticing.** It performs a subtraction and reports only the sign of the result. It exists because comparison is how branches are decided, and reusing the adder is free. **A comparison is a subtraction whose result you discard** — which is why `cmp` on real machines sets flags without storing anything.

The lab verifies all eight operations against Python's semantics over **every one of the 65,536 input pairs — 524,288 checks, zero failures.**

### The flags, one more time

The same result bits mean different things under different interpretations:

| Operation | Result | C | V | Reading |
| :--- | :--- | :-: | :-: | :--- |
| `0xFF + 0x01` | `0x00` | 1 | 0 | Unsigned overflow; signed $(-1)+1 = 0$ is fine |
| `0x7F + 0x01` | `0x80` | 0 | 1 | Signed overflow ($127+1$); unsigned 128 is fine |

**The ALU computes one result and reports both flags. The instruction set decides which matters** — `JC` branches on carry, `JO` on overflow. The hardware refuses to choose an interpretation, which is exactly right: it does not know whether your bits are signed.

---

## 6. Predict before reading on

The ALU's opcode is three bits that select the operation. Those bits have to come from somewhere.

**Where, in a real processor?**

<details><summary>Check your answer</summary>

**From the instruction itself.** A machine instruction is a binary word, and some of its bits are the **opcode field**. Those bits are routed — sometimes almost directly — to the ALU's function-select input.

```
   instruction:  [ opcode ][ reg A ][ reg B ][ dest ]
                     │
                     └──────────────► ALU function select
```

**This is the meeting point the whole course has been heading toward.** [[how-computers-work/index|The index]] described two directions — bottom-up from physics, top-down from source code — converging at the processor. The opcode field *is* that convergence: bits produced by a compiler, arriving as voltages on the select lines of a multiplexer built from transistors.

When you write `a + b` in C, the compiler emits an ADD instruction, whose opcode bits become `000` on those wires, which steers this MUX to pass the adder's output. **Nothing else happens.** The chain from your source code to the electrons is complete, and it is shorter than it looks.

Instruction encoding is Part IX ([[how-computers-work/07-the-bridge|the bridge]] routes you there); you have now built the hardware end of it.
</details>

---

## 7. Worked example — runnable

Save as `alu_lab.py` and run `python3 alu_lab.py`.

```python
"""One circuit, many operations. The computational core of a processor."""
WIDTH = 8
MASK = (1 << WIDTH) - 1

# Opcodes -- these bits come straight from the instruction (module 26 onward)
OPS = {0b000: "ADD", 0b001: "SUB", 0b010: "AND", 0b011: "OR",
       0b100: "XOR", 0b101: "SHL", 0b110: "SHR", 0b111: "SLT"}

def ripple_add(a, b, carry_in=0):
    """Reused from module 21. Returns (sum, carry_out, carry_into_msb)."""
    result, carry, carry_into_msb = 0, carry_in, 0
    for i in range(WIDTH):
        if i == WIDTH - 1:
            carry_into_msb = carry
        x, y = (a >> i) & 1, (b >> i) & 1
        s = x ^ y ^ carry
        carry = (x & y) | (carry & (x ^ y))
        result |= s << i
    return result, carry, carry_into_msb

def barrel_shift(value, amount, right=False):
    """Shift by any amount in log2(WIDTH) MUX stages, not `amount` steps.

    Stage k either shifts by 2^k or passes through, selected by bit k of
    `amount`. Three stages cover every shift from 0 to 7."""
    result = value
    for k in range(3):                       # log2(8) = 3 stages
        if (amount >> k) & 1:
            shift = 1 << k
            result = (result >> shift) if right else ((result << shift) & MASK)
    return result

def alu(a, b, opcode):
    """Compute EVERY operation in parallel, then select one with a MUX.

    This is how real hardware does it: the adder, logic gates and shifter
    all run on every cycle regardless of the opcode. Selecting is cheaper
    than reconfiguring."""
    subtract = (opcode == 0b001) or (opcode == 0b111)     # SUB and SLT both subtract
    b_eff = (~b & MASK) if subtract else b
    sum_result, carry_out, carry_msb = ripple_add(a, b_eff, 1 if subtract else 0)

    results = {
        0b000: sum_result,
        0b001: sum_result,
        0b010: a & b,
        0b011: a | b,
        0b100: a ^ b,
        0b101: barrel_shift(a, b & 0b111, right=False),
        0b110: barrel_shift(a, b & 0b111, right=True),
        0b111: 1 if to_signed(sum_result) < 0 else 0,     # set-less-than
    }
    result = results[opcode]                              # <- the MUX

    arithmetic = opcode in (0b000, 0b001, 0b111)
    return result, {
        "Z": 1 if result == 0 else 0,
        "N": (result >> (WIDTH - 1)) & 1,
        "C": carry_out if arithmetic else 0,
        "V": (carry_out ^ carry_msb) if arithmetic else 0,
    }

def to_signed(value):
    return value - (1 << WIDTH) if value & (1 << (WIDTH - 1)) else value

if __name__ == "__main__":
    print(f"{WIDTH}-bit ALU, {len(OPS)} operations selected by a 3-bit opcode")
    print()
    print(f"  {'opcode':>7s} {'op':>4s}   A     B     ->  result        flags")
    for code, name in OPS.items():
        a, b = 0b10110010, 0b00000011
        r, f = alu(a, b, code)
        flags = " ".join(f"{k}={v}" for k, v in f.items())
        print(f"  {code:03b} {name:>4s}  {a:08b} {b:08b} -> {r:08b} ({r:3d})  {flags}")
    print()

    print("The barrel shifter: any shift in 3 MUX stages, not N steps")
    for amount in range(4):
        print(f"  10110010 << {amount} = {barrel_shift(0b10110010, amount):08b}"
              f"    >> {amount} = {barrel_shift(0b10110010, amount, right=True):08b}")
    print()

    print("verifying every operation against Python semantics:")
    checks = {
        0b000: lambda a, b: (a + b) & MASK,
        0b001: lambda a, b: (a - b) & MASK,
        0b010: lambda a, b: a & b,
        0b011: lambda a, b: a | b,
        0b100: lambda a, b: a ^ b,
        0b101: lambda a, b: (a << (b & 7)) & MASK,
        0b110: lambda a, b: a >> (b & 7),
        0b111: lambda a, b: 1 if to_signed((a - b) & MASK) < 0 else 0,
    }
    failures = 0
    for code, reference in checks.items():
        for a in range(256):
            for b in range(256):
                got, _ = alu(a, b, code)
                if got != reference(a, b):
                    failures += 1
                    if failures == 1:
                        print(f"  first failure: {OPS[code]} a={a} b={b}"
                              f" got {got} want {reference(a,b)}")
    print(f"  {len(checks)} operations x 65,536 input pairs = "
          f"{len(checks)*65536:,} checks, {failures} failures")
    print()

    print("flags in action -- the SAME bits, two interpretations:")
    for a, b, note in [(0xFF, 0x01, "unsigned overflow, signed fine"),
                       (0x7F, 0x01, "signed overflow, unsigned fine"),
                       (0x00, 0x00, "zero result")]:
        r, f = alu(a, b, 0b000)
        print(f"  {a:#04x} + {b:#04x} = {r:#04x}   C={f['C']} V={f['V']}"
              f" Z={f['Z']} N={f['N']}   ({note})")

    assert failures == 0
    assert alu(5, 3, 0b001)[0] == 2
    assert alu(0x0F, 0xF0, 0b011)[0] == 0xFF
    assert alu(3, 5, 0b111)[0] == 1          # 3 < 5 -> 1
    assert alu(5, 3, 0b111)[0] == 0          # 5 < 3 -> 0
    print()
    print("alu_lab: passed")
```

Expected output:

```
8-bit ALU, 8 operations selected by a 3-bit opcode

   opcode   op   A     B     ->  result        flags
  000  ADD  10110010 00000011 -> 10110101 (181)  Z=0 N=1 C=0 V=0
  001  SUB  10110010 00000011 -> 10101111 (175)  Z=0 N=1 C=1 V=0
  010  AND  10110010 00000011 -> 00000010 (  2)  Z=0 N=0 C=0 V=0
  011   OR  10110010 00000011 -> 10110011 (179)  Z=0 N=1 C=0 V=0
  100  XOR  10110010 00000011 -> 10110001 (177)  Z=0 N=1 C=0 V=0
  101  SHL  10110010 00000011 -> 10010000 (144)  Z=0 N=1 C=0 V=0
  110  SHR  10110010 00000011 -> 00010110 ( 22)  Z=0 N=0 C=0 V=0
  111  SLT  10110010 00000011 -> 00000001 (  1)  Z=0 N=0 C=1 V=0

The barrel shifter: any shift in 3 MUX stages, not N steps
  10110010 << 0 = 10110010    >> 0 = 10110010
  10110010 << 1 = 01100100    >> 1 = 01011001
  10110010 << 2 = 11001000    >> 2 = 00101100
  10110010 << 3 = 10010000    >> 3 = 00010110

verifying every operation against Python semantics:
  8 operations x 65,536 input pairs = 524,288 checks, 0 failures

flags in action -- the SAME bits, two interpretations:
  0xff + 0x01 = 0x00   C=1 V=0 Z=1 N=0   (unsigned overflow, signed fine)
  0x7f + 0x01 = 0x80   C=0 V=1 Z=0 N=1   (signed overflow, unsigned fine)
  0x00 + 0x00 = 0x00   C=0 V=0 Z=1 N=0   (zero result)

alu_lab: passed
```

The `results` dictionary is the point: **every entry is computed before the selection happens.** `result = results[opcode]` is the multiplexer, and in hardware all eight values genuinely exist on wires at that moment.

---

## 8. The ALU on the critical path

The ALU is almost always the slowest block in a simple processor, because the adder's carry chain runs through it ([[how-computers-work/05-combinational/02-adders|module 21]]).

Its delay is roughly:

$$t_{ALU} = t_{adder} + t_{MUX}$$

With a 64-bit carry-lookahead adder at 280 ps and a MUX at ~40 ps, that is around 320 ps — implying a ceiling near 3 GHz **before** register overheads, wire delay, or anything else in the path.

**Three consequences that shape real processors:**

1. **Adder design is disproportionately important.** Shaving 50 ps off the carry chain lifts the whole chip's clock.
2. **Complex ALU operations get their own path.** Multiply and divide are far slower than add, so they are given multiple cycles or a separate pipelined unit rather than being allowed to set the clock for everything.
3. **This motivates pipelining.** If the ALU cannot be made faster, split the work across cycles so a *new* operation can start each cycle even though each takes several — throughput without latency reduction. That is [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]].

---

## 9. Common pitfalls and traps

1. **Thinking the ALU reconfigures.** It computes everything and discards most of it. Wires do not move.
2. **Assuming unused units cost nothing.** They cost dynamic power on every cycle, which is why operand isolation exists.
3. **Building an iterative shifter.** Shift-by-one repeated makes delay depend on the shift amount. Use a barrel shifter.
4. **Confusing logical and arithmetic right shift.** Logical fills with 0; arithmetic replicates the sign bit. Using the wrong one silently corrupts negative numbers — the reason C has both `>>` semantics depending on signedness.
5. **Treating flags as belonging to an interpretation.** The ALU sets C and V on every arithmetic operation. Software picks which to test.
6. **Forgetting the MUX is word-wide.** An 8-way MUX on 64-bit results is 64 copies of an 8-to-1 MUX — real area.

---

## 10. Check your understanding

1. **Why is SLT implemented as a subtraction rather than a dedicated comparator?**
   <details><summary>Answer</summary>
   Because the adder already exists and subtraction is free in two's complement (module 21). $A < B$ exactly when $A - B$ is negative, so SLT is a subtract whose sign bit becomes the result and whose difference is discarded.<br>
   A dedicated magnitude comparator would be extra area for something already computed. This is why real ISAs have a <code>cmp</code> instruction that sets flags without writing a result — it is a subtraction you throw away.<br>
   (The careful version must also account for signed overflow: the correct signed test is $N \oplus V$, not $N$ alone, which is why hardware comparison instructions use both flags.)
   </details>

2. **A 32-bit barrel shifter needs how many stages, and how many 2-to-1 MUXes?**
   <details><summary>Answer</summary>
   $\log_2 32 = $ <strong>5 stages</strong>, each 32 MUXes wide → <strong>160 MUXes</strong>.<br>
   Compare with an iterative design: correct, far smaller, but with delay proportional to the shift amount — up to 31 stages for a shift of 31, and variable timing, which is unacceptable when every instruction must complete in a fixed clock period. <strong>Predictable timing is worth the area.</strong>
   </details>

3. **Why does the ALU compute flags on every operation, even bitwise ones where C and V are meaningless?**
   <details><summary>Answer</summary>
   Because the flag logic is combinational and runs regardless — there is no way to "not compute" it without adding gating that costs more than it saves.<br>
   In practice most ISAs define which flags each instruction <em>updates</em>: logical operations typically set Z and N but leave C and V untouched or cleared. The lab reflects this by zeroing C and V for non-arithmetic ops. This is a <strong>specification decision, not a hardware limitation</strong>, and it varies between architectures — one of many reasons porting assembly between ISAs is error-prone.
   </details>

4. **The ALU is the first circuit whose behaviour is chosen by data. Why is that significant?**
   <details><summary>Answer</summary>
   Every previous circuit did exactly one thing, determined by its wiring. To change the behaviour you would rebuild it.<br>
   The ALU's behaviour is chosen by three input bits arriving alongside the data — so <strong>the same silicon performs different operations on different cycles, decided by information rather than structure.</strong><br>
   That is the seed of the stored-program computer: if the operation is selected by bits, those bits can be <em>stored in memory</em> and fetched like any other data. A sequence of such bit patterns is a <strong>program</strong>. It is the same insight as the MUX-as-LUT in [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]] — moving function from structure into data — and it is what Part VIII builds on.
   </details>

---

## 11. Practice — independent task

**Task:** Extend the ALU to 16 bits and add three operations.

- **(a)** Widen the lab to 16 bits. Re-run the verification on 20,000 random pairs per operation plus boundary values (0, 1, 0x7FFF, 0x8000, 0xFFFF).
- **(b)** Add **arithmetic right shift** (SRA), which replicates the sign bit. Verify it against Python's `>>` on negative values, converting appropriately. Show a case where SRA and SHR differ.
- **(c)** Add **rotate left** (ROL), where bits shifted off the top re-enter at the bottom. Implement it with the barrel shifter structure.
- **(d)** Add **SLTU** (unsigned set-less-than). Find inputs where SLT and SLTU disagree, and explain which flag combination each uses.
- **(e)** You now need 11 operations, so the opcode grows to 4 bits. What does that cost — in MUX width, and in instruction encoding bits?
- **(f)** Estimate the ALU's critical path: 16-bit carry-lookahead adder plus a 16-to-1 MUX. Assume 20 ps per gate level and that a 16-to-1 MUX tree is 4 levels deep. What is $f_{max}$?
- **(g)** Which of your 11 operations is slowest? If you removed it from the ALU and gave it a separate multi-cycle unit, what would $f_{max}$ become?

**Done when:** all 11 operations verify, you have found inputs distinguishing SLT from SLTU and SRA from SHR, and you can state $f_{max}$ before and after moving the slowest operation off the critical path.

<details><summary>Hint for (d), only if stuck</summary>
Try $A = 0x0001$, $B = 0xFFFF$. <strong>Unsigned:</strong> $1 < 65535$ → SLTU = 1. <strong>Signed:</strong> $1 < -1$ is false → SLT = 0.<br>
SLTU is decided by the carry flag (borrow), SLT by $N \oplus V$. This is precisely why MIPS and RISC-V provide both instructions, and why mixing signed and unsigned comparisons is such a persistent source of bugs in C.
</details>

---

## 12. Tradeoffs and limits

- **Multiply and divide are not here.** Multiplication is shift-and-add with partial-product trees; division is iterative. Both are far slower than add and are usually separate units.
- **Floating point is a different unit entirely.** An FPU has its own adder, multiplier, normaliser and rounding logic, and its own exception flags.
- **The parallel-compute approach costs power.** Operand isolation and clock gating mitigate it, at the cost of design complexity.
- **Real ALUs are wider and deeper.** SIMD units perform many narrow operations per instruction; the principle is unchanged, the replication is large.

---

## Before moving on

**This is the end of Part VI.** You are ready for Part VII when you can, closed-book:

- [ ] Explain why an ALU computes all operations in parallel and selects with a MUX.
- [ ] Build a barrel shifter and explain the $\log_2 n$ stage count.
- [ ] List the operations of a simple ALU and explain why SLT is a subtraction.
- [ ] Explain why the ALU is usually on the critical path and name three consequences.
- [ ] Explain why behaviour selected by data, rather than structure, is a significant step.

**Recap:** An ALU wraps an adder, logic gates and a barrel shifter behind a multiplexer, computing every operation in parallel and selecting one with the opcode — because wires cannot be rewired and parallel evaluation costs no extra time. The barrel shifter achieves any shift in $\log_2 n$ MUX stages. Flags are computed on every operation, leaving the signed/unsigned interpretation to software. The ALU's carry chain usually sets the critical path, and its opcode input is where an instruction's bits meet the transistors.

**Next:** [[how-computers-work/06-memory/01-latches-and-flip-flops|Module 22 — Latches and Flip-Flops]] begins Part VII and makes the conceptual leap of the whole course: **feedback turns combinational logic into memory.** Every circuit so far forgets everything the instant its inputs change. That is about to stop.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/05-combinational/02-adders|Module 21 — Adders]] — the carry chain inside this block
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — the MUX that selects the operation
- [[foundations/computer-architecture/05-the-datapath|computer-architecture/the datapath]] — where the ALU sits in a processor
- [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]] — the answer to a slow ALU
