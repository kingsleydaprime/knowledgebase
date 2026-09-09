# Module 28: Design the PRIME-1 CPU (Every Choice Costs Something)

**[Advanced]** — The capstone begins. Before you build anything you must decide what to build — and every decision spends bits from a budget that does not stretch.

## Before you start

- You have completed modules 1–26 and can build every component of a CPU.
- You have read [[how-computers-work/07-the-bridge|module 27]] and at minimum [[foundations/computer-architecture/05-the-datapath|computer-architecture/the datapath]].

**After this lesson you will be able to:**

1. State the decisions an ISA designer must make, and why they are coupled rather than independent.
2. Compute an instruction encoding budget and show which designs do not fit.
3. Justify PRIME-1's word size, register count and instruction width from evidence.
4. Explain why architectural decisions are almost impossible to reverse.

**Study route:** section 3 is the budget that drives everything else. Do the lab before reading section 6 — the numbers make the argument better than prose.

---

## 1. Why this exists (real-world motivation)

You could start wiring. People do, and they produce machines that work and are miserable to program — a 4-bit immediate that cannot hold a loop counter, a register count that makes every function spill to memory, an encoding with no room for the instruction they needed to add.

**The distinguishing feature of architecture decisions is that they are almost impossible to reverse.** Change the word size and every register, bus, ALU and memory interface changes with it. Change the instruction encoding and every program ever assembled for the machine is invalid.

**x86 has carried decisions from 1978 for nearly fifty years.** Its variable-length encoding, its register naming, its segment registers — all preserved because binary compatibility mattered more than elegance. That is not incompetence; it is what architecture means.

**So decide deliberately, write the reasons down, and only then build.**

---

## 2. The decisions

Six, and **they are coupled** — which is what makes this hard:

| Decision | Question | Constrains |
| :--- | :--- | :--- |
| **Word size** | How wide is a value? | Address space, wire count, ALU cost |
| **Register count** | How many, and how are they named? | Encoding bits, register file area |
| **Instruction width** | Fixed or variable? How many bits? | Decoder complexity, code density |
| **Memory model** | Word- or byte-addressed? How is memory reached? | Address space, load/store design |
| **Instruction count** | How many opcodes? | Opcode field width |
| **Addressing modes** | How is an operand's location expressed? | Encoding space, datapath complexity |

**They compete for the same bits.** More registers means fewer bits for immediates. More opcodes means fewer bits for everything else. That is the whole problem.

---

## 3. The encoding budget

**Every instruction has a fixed number of bits, and each field must be paid for.**

For a 16-bit instruction with $R$ registers and $N$ opcodes:

$$\text{opcode} = \lceil\log_2 N\rceil \qquad \text{register field} = \lceil\log_2 R\rceil$$

A three-register instruction (`ADD rd, ra, rb`) needs the opcode plus three register fields. An immediate instruction needs the opcode, two register fields, and whatever is left goes to the immediate.

**Run the numbers for register count, holding the instruction at 16 bits:**

| Registers | Bits/reg | R-type spare | I-type imm | Immediate range | Verdict |
| ---: | ---: | ---: | ---: | ---: | :--- |
| 4 | 2 | 6 | 8 | −128 to 127 | ok |
| **8** | **3** | **3** | **6** | **−32 to 31** | **ok** |
| 16 | 4 | 0 | 4 | −8 to 7 | immediate reaches only 7, need 10 |
| 32 | 5 | −3 | 2 | −2 to 1 | R-type does not fit |

> [!NOTE]
> **Note how that verdict is decided.** Not by taste, and not by an arbitrary "immediates should be at least $n$ bits" rule.
>
> The reference program contains `LDI R2, 10`. **A 4-bit signed immediate spans −8 to 7 and cannot represent 10.** So 16 registers is rejected because it fails a concrete program you have already written.
>
> **Design against a workload, not against intuition.** This is exactly how real ISA decisions are made — you run benchmarks, look at what the instruction mix actually needs, and let the evidence choose. The lab encodes that requirement as a constant so the reasoning is inspectable rather than asserted.

**So 8 registers.** Four would also work and gives roomier immediates, but 8 is the largest count that still leaves a usable immediate — and registers are the scarcest resource when writing real code.

---

## 4. Register count has a second cost

Encoding is not the only pressure. From [[how-computers-work/06-memory/02-registers-and-counters|module 25]], a register file's read ports are multiplexer trees:

| Registers | Storage bits | MUX gates | Total |
| ---: | ---: | ---: | ---: |
| 4 | 64 | 96 | 160 |
| 8 | 128 | 224 | 352 |
| 16 | 256 | 480 | 736 |
| 32 | 512 | 992 | 1504 |

**Cost is dominated by the read MUXes, not the storage** — and doubling the register count slightly more than doubles total area, because each of the two read ports needs a bigger tree.

**Two independent arguments converge on a small register file.** When encoding pressure and area cost point the same way, the decision is easy.

---

## 5. Word size

| Bits | Unsigned max | Signed range | Address space |
| ---: | ---: | ---: | ---: |
| 8 | 255 | −128 to 127 | 256 words |
| **16** | **65,535** | **−32,768 to 32,767** | **65,536 words** |
| 32 | 4,294,967,295 | ±2.1 billion | 4.3 billion words |

**8 bits fails on address space, not on arithmetic.** 256 words holds a toy program *or* its data, not both. You would immediately need bank switching, which is a whole extra mechanism to design and debug.

**32 bits doubles every wire, every register bit, every ALU stage** — for a first machine, that is cost with no lesson attached. It also makes the breadboard track genuinely impossible.

**16 bits is the smallest word that is not immediately painful.** 64 KB is enough for real programs, arithmetic covers a useful range, and the buses stay buildable.

---

## 6. The remaining decisions

### Fixed-width instructions

**Every PRIME-1 instruction is exactly 16 bits.** The alternative — variable-length, as on x86 — buys code density and costs a much harder decoder.

| | Fixed width | Variable width |
| :--- | :--- | :--- |
| Decoder | Trivial — fields are at known positions | Complex — must determine length first |
| PC increment | Always +1 | Depends on the instruction just decoded |
| Code density | Worse — short instructions waste bits | Better |
| Pipelining | Easy — fetch is uniform | Hard — cannot fetch the next until you decode this one |

**Fixed width, for a first machine, is not close.** It is also why RISC architectures chose it: the decoder simplicity pays for itself in pipelining, which is worth far more than the code size.

### Word-addressed memory

`mem[5]` is the sixth **16-bit word**, not byte 5. Byte addressing needs alignment rules, byte-enable signals on the memory interface, and load/store variants for each width. **Word addressing removes all of that**, at the cost of making byte-oriented data (strings) awkward.

**A real design would choose byte addressing.** PRIME-1 chooses simplicity, and it is worth knowing that is a deliberate simplification rather than the normal answer.

### R0 hardwired to zero

**One register spent on a constant, and it pays for itself:**

- `MOV rd, ra` becomes `ADD rd, ra, R0`
- `NOP` becomes `ADD R0, R0, R0`
- Comparison against zero needs no immediate
- Any instruction wanting "no second operand" uses R0

**One hardwired constant removes the need for several instruction formats.** MIPS and RISC-V both do this; ARM notably does not, and pays for it with more encoding formats.

### 16 opcodes

4 opcode bits leaves a 6-bit immediate. 5 bits would give 32 instructions and a 5-bit immediate (−16 to 15) — still viable, but PRIME-1 does not need 32 instructions, and unused opcodes are wasted encoding space.

---

## 7. Predict before reading on

PRIME-1 spends all 16 opcodes. You want to add a register-indirect jump, `JR ra` — the clean way to return from a function.

**Where do the bits come from?**

<details><summary>Check your answer</summary>

**There is no spare opcode, so you must take the bits from somewhere else.** Three real options:

1. **Repurpose the R-type `fn` field.** R-type instructions have 3 spare bits ([[how-computers-work/05-combinational/02-adders|see the budget table]]). Make one opcode a "system" group whose `fn` field selects `JR`, `HLT`, and future additions. **This is what MIPS does** — its `funct` field extends one opcode into 64.
2. **Steal an opcode you use less.** `SHL` and `SHR` could merge into one shift instruction with a direction bit in the spare R-type field, freeing an opcode.
3. **Widen the opcode to 5 bits.** Now every immediate shrinks to 5 bits, and −16 to 15 still holds 10 — so this works, but it costs you range in *every* immediate instruction to gain one new one.

**Option 1 is the right answer**, and it teaches the general lesson: **when you run out of encoding space, add a level of indirection rather than widening the field.** The cost is a slightly more complex decoder; the benefit is room to grow without invalidating existing programs.

That is exactly why real ISAs have "extension" opcodes and escape prefixes, and it is the mechanism by which x86 has absorbed forty years of additions.
</details>

---

## 8. Worked example — runnable

Save as `design_lab.py` and run `python3 design_lab.py`.

```python
"""Every ISA decision spends bits from a fixed budget. This makes the
tension visible instead of leaving it to taste."""
import math

def reg_bits(n_registers):
    return math.ceil(math.log2(n_registers))

def encoding_budget(instr_bits, n_registers, n_opcodes):
    """How the instruction word divides up, for each format."""
    op = math.ceil(math.log2(n_opcodes))
    r  = reg_bits(n_registers)
    return {
        "opcode":     op,
        "reg field":  r,
        "R-type spare": instr_bits - op - 3 * r,   # rd, ra, rb
        "I-type imm":   instr_bits - op - 2 * r,   # rd, ra, immediate
        "J-type addr":  instr_bits - op,
    }

def immediate_range(bits, signed=True):
    if bits <= 0:
        return None
    return (-(1 << (bits - 1)), (1 << (bits - 1)) - 1) if signed \
        else (0, (1 << bits) - 1)

# The reference program does `LDI R2, 10`, so an immediate must at least
# reach 10. That is a concrete requirement, not an arbitrary bit count.
REQUIRED_IMMEDIATE = 10

def viable(budget, required=REQUIRED_IMMEDIATE):
    """Viable if every format fits AND immediates can hold a useful constant."""
    reasons = []
    if budget["R-type spare"] < 0:
        reasons.append("R-type does not fit")
    rng = immediate_range(budget["I-type imm"])
    if rng is None or rng[1] < required:
        got = rng[1] if rng else 0
        reasons.append(f"immediate reaches only {got}, need {required}")
    return (not reasons), reasons

def regfile_cost(n_registers, width, read_ports=2):
    """Rough area: storage bits plus the read MUX tree (module 20)."""
    storage = n_registers * width
    mux_per_port = (n_registers - 1) * width      # 2-to-1 MUXes in a tree
    return storage, read_ports * mux_per_port

if __name__ == "__main__":
    print("DECISION 1 -- how many registers, given a 16-bit instruction?")
    print(f"  {'regs':>5s} {'bits/reg':>9s} {'R spare':>8s} {'I imm':>6s}"
          f" {'imm range':>16s}  verdict")
    for n in (4, 8, 16, 32):
        b = encoding_budget(16, n, 16)
        ok, why = viable(b)
        rng = immediate_range(b["I-type imm"])
        rng_s = f"{rng[0]} to {rng[1]}" if rng else "none"
        print(f"  {n:5d} {b['reg field']:9d} {b['R-type spare']:8d}"
              f" {b['I-type imm']:6d} {rng_s:>16s}  "
              f"{'ok' if ok else '; '.join(why)}")
    print()
    print("  -> 8 registers is the largest that still leaves a usable immediate.")
    print("     16 registers gives only -8..7, which cannot even hold the")
    print("     constant 10 that the reference program needs.")
    print()

    print("DECISION 2 -- register file cost (16-bit words, 2 read ports)")
    print(f"  {'regs':>5s} {'storage bits':>13s} {'MUX gates':>11s} {'total':>8s}")
    for n in (4, 8, 16, 32):
        st, mux = regfile_cost(n, 16)
        print(f"  {n:5d} {st:13d} {mux:11d} {st + mux:8d}")
    print("  -> cost is dominated by the READ MUXes, not the storage.")
    print("     Doubling registers more than doubles the area (module 25).")
    print()

    print("DECISION 3 -- word size, and what it can address")
    print(f"  {'bits':>5s} {'unsigned max':>13s} {'signed range':>22s}"
          f" {'address space':>14s}")
    for w in (8, 16, 32):
        print(f"  {w:5d} {(1<<w)-1:13,d} "
              f"{f'{-(1<<(w-1)):,} to {(1<<(w-1))-1:,}':>22s}"
              f" {f'{1<<w:,} words':>14s}")
    print("  -> 8-bit cannot address enough memory to hold an interesting")
    print("     program AND its data. 32-bit doubles every wire and register.")
    print("     16 bits is the smallest word that is not immediately painful.")
    print()

    print("DECISION 4 -- how many opcodes can you afford?")
    for op_bits in (3, 4, 5):
        b = encoding_budget(16, 8, 1 << op_bits)
        ok, why = viable(b)
        print(f"  {op_bits} opcode bits -> {1<<op_bits:2d} instructions,"
              f" I-type immediate {b['I-type imm']:2d} bits"
              f"   {'ok' if ok else '; '.join(why)}")
    print("  -> 4 bits (16 instructions) is the sweet spot: enough to be")
    print("     useful, cheap enough to leave a 6-bit immediate.")
    print()

    print("THE CHOSEN DESIGN: PRIME-1")
    final = encoding_budget(16, 8, 16)
    for k, v in final.items():
        print(f"  {k:16s} {v:3d} bits")
    ok, _ = viable(final)
    print(f"  viable: {ok}")

    assert viable(encoding_budget(16, 8, 16))[0]
    assert not viable(encoding_budget(16, 32, 16))[0]     # 32 regs does not fit
    assert not viable(encoding_budget(16, 16, 16))[0]     # 16 regs -> 4-bit imm
    assert regfile_cost(16, 16)[1] > 2 * regfile_cost(8, 16)[1]
    print()
    print("design_lab: passed")
```

Expected output:

```
DECISION 1 -- how many registers, given a 16-bit instruction?
   regs  bits/reg  R spare  I imm        imm range  verdict
      4         2        6      8      -128 to 127  ok
      8         3        3      6        -32 to 31  ok
     16         4        0      4          -8 to 7  immediate reaches only 7, need 10
     32         5       -3      2          -2 to 1  R-type does not fit; immediate reaches only 1, need 10

  -> 8 registers is the largest that still leaves a usable immediate.
     16 registers gives only -8..7, which cannot even hold the
     constant 10 that the reference program needs.

DECISION 2 -- register file cost (16-bit words, 2 read ports)
   regs  storage bits   MUX gates    total
      4            64          96      160
      8           128         224      352
     16           256         480      736
     32           512         992     1504
  -> cost is dominated by the READ MUXes, not the storage.
     Doubling registers more than doubles the area (module 25).

DECISION 3 -- word size, and what it can address
   bits  unsigned max           signed range  address space
      8           255            -128 to 127      256 words
     16        65,535      -32,768 to 32,767   65,536 words
     32 4,294,967,295 -2,147,483,648 to 2,147,483,647 4,294,967,296 words
  -> 8-bit cannot address enough memory to hold an interesting
     program AND its data. 32-bit doubles every wire and register.
     16 bits is the smallest word that is not immediately painful.

DECISION 4 -- how many opcodes can you afford?
  3 opcode bits ->  8 instructions, I-type immediate  7 bits   ok
  4 opcode bits -> 16 instructions, I-type immediate  6 bits   ok
  5 opcode bits -> 32 instructions, I-type immediate  5 bits   ok
  -> 4 bits (16 instructions) is the sweet spot: enough to be
     useful, cheap enough to leave a 6-bit immediate.

THE CHOSEN DESIGN: PRIME-1
  opcode             4 bits
  reg field          3 bits
  R-type spare       3 bits
  I-type imm         6 bits
  J-type addr       12 bits
  viable: True

design_lab: passed
```

---

## 9. The resulting specification

| Decision | Choice | Because |
| :--- | :--- | :--- |
| Word size | 16 bits | 8 cannot address enough memory; 32 doubles every wire |
| Registers | 8 (R0–R7) | Largest count leaving a usable 6-bit immediate |
| R0 | Hardwired to 0 | Removes the need for several instruction formats |
| Instruction width | 16 bits, fixed | Trivial decoder, uniform fetch, pipelining-friendly |
| Opcodes | 16 (4 bits) | Enough instructions, leaves a 6-bit immediate |
| Memory | 64K words, word-addressed | No alignment rules, no byte-enable logic |
| Formats | R, I, J | One for each shape of operand |

**Write your version of this table down before building anything.** When you are three hours into debugging and cannot remember whether immediates are signed, this is what you check.

---

## 10. Common pitfalls and traps

1. **Deciding by taste rather than by workload.** "8 registers feels right" is not a reason. "16 registers cannot encode the constant 10" is.
2. **Treating the decisions as independent.** They compete for the same bits. Changing one changes all of them.
3. **Not writing down the reasons.** Six months later you will not remember why immediates are 6 bits, and you will "fix" it.
4. **Optimising for code density on a first machine.** Variable-length encoding is a real technique and the wrong one here.
5. **Spending all your opcodes.** Leave one for the instruction you have not thought of yet — or plan the escape mechanism from section 7.
6. **Forgetting the register file's area cost.** Encoding is not the only pressure against more registers.

---

## 11. Check your understanding

1. **Why is instruction width a harder decision to change later than, say, the number of ALU operations?**
   <details><summary>Answer</summary>
   Adding an ALU operation is an internal change: existing programs still run, and only the control unit and ALU change. It is backward-compatible.<br>
   Changing the instruction width <strong>invalidates every program ever assembled</strong> for the machine, and changes the fetch logic, the PC increment, memory layout and the decoder. It is a new architecture, not a revision. This asymmetry — some decisions are internal, some are part of the contract — is exactly what the ISA/microarchitecture split exists to formalise.
   </details>

2. **PRIME-1 uses word addressing. What specifically becomes awkward?**
   <details><summary>Answer</summary>
   <strong>Anything byte-oriented.</strong> A string packs two characters per word, so reading one character needs a load, a shift and a mask — three instructions where a byte-addressed machine uses one. Struct layouts waste space when fields are smaller than a word.<br>
   The compensation is that <strong>alignment problems disappear entirely</strong>: every access is naturally aligned, no unaligned-access penalty exists, and the memory interface needs no byte-enable signals. For a machine whose purpose is teaching, that is the right trade — and knowing it <em>is</em> a trade is the point.
   </details>

3. **Adding a 5th opcode bit gives 32 instructions. Why not just do that?**
   <details><summary>Answer</summary>
   Because it takes a bit from <em>every</em> I-type immediate, shrinking the range from −32..31 to −16..15. You would pay in every immediate instruction to gain sixteen opcodes you have no use for.<br>
   Encoding space is zero-sum. <strong>The right question is never "can I afford this field?" but "what am I taking it from?"</strong> — and if the answer is "something I use constantly, to gain something I use rarely", the answer is no.
   </details>

4. **Why does x86 still carry decisions made in 1978?**
   <details><summary>Answer</summary>
   Because the ISA is a <strong>contract</strong>, and binary compatibility is the product. Millions of programs exist as machine code; changing the encoding would invalidate all of them.<br>
   So x86 grew by <em>extension</em> — prefixes, escape opcodes, new modes — never by revision. The result is a decoder of extraordinary complexity, which modern chips handle by translating x86 into internal micro-operations. <strong>The architecture is forty years old; the microarchitecture executing it is not</strong>, and that separation is what makes the arrangement survivable. This is the ISA/microarchitecture distinction doing real work.
   </details>

---

## 12. Practice — independent task

**Task:** Design your own variant, and justify it against evidence rather than taste.

- **(a)** Write a short program (10–20 instructions) doing something you care about — a string search, a bubble sort of 8 values, a Fibonacci sequence. Write it in *pseudo-assembly*, before fixing your ISA.
- **(b)** From that program, count: how many distinct constants do you need, and what is the largest? How many simultaneously-live values (that is your minimum register count)? What memory range do you touch?
- **(c)** Using `encoding_budget()`, find every (registers, opcodes) combination that satisfies your program's requirements in a 16-bit instruction. Add your required-immediate value as the `required` parameter.
- **(d)** If nothing fits, you have three options: widen the instruction to 24 or 32 bits, reduce your requirements, or add a second word for large immediates. Cost each one.
- **(e)** Choose, and write the decision table from section 9 with a *reason* in every row that references your program.
- **(f)** Now design one instruction that your program needed and PRIME-1 lacks. Where do its bits come from? Use the section 7 options.
- **(g)** Extend `design_lab.py` with `fits_program(constants, live_values, memory_words, instr_bits)` returning viable configurations, and verify your choice.

**Done when:** every row of your decision table cites evidence from your own program, and you can name one instruction PRIME-1 is missing and say exactly what it would cost to add.

<details><summary>Hint for (b), only if stuck</summary>
"Simultaneously live" means values you need to keep at the same time. Trace your program and, at each line, count the variables that will be read later. The maximum across all lines is your minimum register count — anything beyond that must <strong>spill</strong> to memory, costing a load and a store each time.<br>
This is exactly what a compiler's <strong>register allocator</strong> computes ([[foundations/compilers/07-optimisation|compilers/optimisation]]), and doing it by hand once makes register pressure stop being an abstraction.
</details>

---

## 13. Tradeoffs and limits

- **This is a load-store architecture by omission.** PRIME-1's ALU operations work only on registers; memory is reached only by `LD` and `ST`. That is the RISC convention and it simplifies the datapath enormously — but it is a choice, and CISC machines that compute directly on memory operands exist.
- **No interrupt mechanism is designed here.** Adding one requires saving the PC and flags, a vector table, and a way to disable interrupts — a substantial extension, and the reason [[foundations/os/index|os/]] is a separate course.
- **No consideration of pipelining.** A pipelined implementation would want to avoid instructions with variable latency and might change the encoding to simplify decode. Designing for a single-cycle implementation first is the right order.
- **Real ISA design is workload-driven at enormous scale.** Vendors profile billions of instructions across representative software before adding one. This module's "design against your own program" is the same method, four orders of magnitude smaller.

---

## Before moving on

- [ ] List the six coupled decisions and explain why they compete.
- [ ] Compute an encoding budget and identify which configurations fail.
- [ ] Justify 8 registers and a 16-bit word from evidence, not preference.
- [ ] Explain why fixed-width encoding suits a first machine.
- [ ] Explain why architecture decisions are near-irreversible.

**Recap:** Every ISA decision spends bits from a fixed instruction budget, and the decisions are coupled — more registers means smaller immediates. PRIME-1 is 16-bit with 8 registers because that is the largest register count leaving an immediate able to hold the constants a real program needs, and because register file area grows faster than register count. Fixed-width instructions, word addressing and a hardwired R0 all trade a little generality for a much simpler datapath. Architecture decisions are near-irreversible because the ISA is a contract, which is why x86 still carries 1978.

**Next:** [[how-computers-work/08-capstone/02-the-isa|Module 29 — The PRIME-1 ISA]] turns these decisions into an exact binary encoding and a complete instruction set.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU]] — the four build tracks implementing this design
- [[foundations/computer-architecture/03-instruction-sets|computer-architecture/instruction sets]] — RISC vs CISC in depth
- [[how-computers-work/06-memory/02-registers-and-counters|module 25]] — the register file whose cost drives decision 2
