# Module 30: Build the Hardware (Deriving the Control Unit)

**[Advanced]** — You have an ISA. This module shows that the control unit — the block everyone finds mysterious — is a **mechanical consequence** of that ISA, then hands you to the four build tracks.

## Before you start

- You have an exact instruction encoding — [[how-computers-work/08-capstone/02-the-isa|module 29]].
- You can build every datapath component: ALU ([[how-computers-work/05-combinational/04-the-alu|module 23]]), register file and PC ([[how-computers-work/06-memory/02-registers-and-counters|module 25]]), memory ([[how-computers-work/06-memory/03-memory-technology|module 26]]).
- You have read [[foundations/computer-architecture/05-the-datapath|computer-architecture/the datapath]].

**After this lesson you will be able to:**

1. Explain what a control unit is and why it is a lookup table rather than a program.
2. **Derive** control signals from an instruction's semantics, by rule.
3. Explain the difference between hardwired and microprogrammed control.
4. Choose a build track and know what each one will teach you.

**Study route:** section 4 is the derivation — the whole point of this module. The build itself lives in the four tracks; this module makes sure you understand what you are building before you wire it.

---

## 1. Why this exists (real-world motivation)

Every component of a CPU has now been built. Lay them on a table: an ALU, a register file, a program counter, memory, some multiplexers.

**Nothing happens.** They are connected to nothing, and no signal tells the multiplexers what to select or the register file when to write.

**The control unit is what makes them a processor rather than a pile of parts.** It reads the opcode and asserts the signals that steer everything else.

It has a reputation for being the hard part, and it is not. **It is a lookup table** — and this module shows you can derive its contents mechanically from the instruction semantics you already wrote down.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Control unit** | Turns an opcode into control signals |
| **Control signal** | One wire steering one multiplexer, enable or operation select |
| **Hardwired control** | Control implemented as combinational logic or a ROM |
| **Microprogrammed control** | Control implemented as a tiny program in a control store |
| **Datapath** | Everything the control unit steers |
| **Single-cycle** | Every instruction completes in one clock |
| **Control ROM** | A memory holding the control table, addressed by opcode |

---

## 3. The datapath, and what needs steering

```
              ┌─────────┐    ┌──────────┐
        ┌────►│   PC    ├───►│  I-MEM   ├──── instruction
        │     └─────────┘    └──────────┘         │
        │          │                              ▼
        │       ┌──▼──┐                   ┌───────────────┐
        │       │ +1  │                   │ CONTROL UNIT  │
        │       └──┬──┘                   └───────┬───────┘
        │          │                              │ 11 signals
        │     ┌────▼─────┐   ┌──────────────────┐ │
        └─────┤ PC MUX   │◄──┤  REGISTER FILE   │◄┘
              └──────────┘   └───┬──────────┬───┘
                                 │ A        │ B
                                 │      ┌───▼───┐
                                 │      │ALUSrc │◄─ immediate
                                 │      │  MUX  │
                              ┌──▼──────▼──┐
                              │    ALU     │
                              └──────┬─────┘
                                ┌────▼────┐   ┌───────────┐
                                │  D-MEM  ├──►│ MemToReg  ├──► writeback
                                └─────────┘   │    MUX    │
                                              └───────────┘
```

**Four multiplexers and several enables.** Each needs a signal, and the signal depends on which instruction is executing. **That set of signals is the control unit's output.**

---

## 4. Deriving the control signals

Here is the part worth understanding properly.

**Do not try to invent the control table.** Instead, describe each instruction by **what it does**, and the signals fall out by rule.

For each instruction, answer six questions:

| Question | Field |
| :--- | :--- |
| Where does the result go, if anywhere? | `dest` |
| Where does the written value come from? | `src` |
| What is the ALU's second input? | `operand` |
| Does it touch memory, and how? | `mem` |
| Which ALU operation? | `alu` |
| Does it change control flow? | `flow` |

**Then each control signal is one sentence of reasoning:**

| Signal | Rule |
| :--- | :--- |
| `RegWrite` | *Does anything get written to a register?* → `dest is not None` |
| `RegBSrc` | *Does read port B supply store data rather than an ALU operand?* → `mem == "write"` |
| `ALUSrc` | *Is the ALU's second input the immediate?* → `operand == "imm"` |
| `ALUOp` | Copied straight from the semantics |
| `MemRead` | `mem == "read"` |
| `MemWrite` | `mem == "write"` |
| `MemToReg` | *Does the written value come from memory?* → `src == "mem"` |
| `Branch` | *Is this a conditional branch?* |
| `BranchNot` | *Is the condition inverted?* |
| `Jump` | *Is this an unconditional jump?* |
| `Link` | *Is the destination the link register?* → `dest == "R7"` |

**That is the entire control unit.** Eleven one-line rules, applied to sixteen instructions.

The lab implements exactly this and then **checks the derived table against the hand-written one** that the logic simulator, the Verilog and the breadboard EEPROM are all built from. **Sixteen opcodes, zero mismatches.**

> [!NOTE]
> **This is why the control unit is not the hard part.**
>
> It looks intimidating because a control table is a wall of ones and zeros with no obvious structure. But **you never write that wall by hand** — you write down what each instruction means, and the table is generated.
>
> **Change the ISA and the table follows mechanically.** Add `JR` and you add one row of semantics; the signals derive themselves. That is what makes ISA extension tractable, and it is why real designs describe control declaratively and let tools produce the logic.
>
> The corollary matters too: **if you cannot describe an instruction's semantics cleanly, you cannot build its control logic cleanly.** A messy control unit is usually a symptom of a messy ISA.

---

## 5. Hardwired versus microprogrammed

Two ways to implement the table:

**Hardwired** — combinational logic, or a ROM addressed by opcode. Fast (one gate delay), inflexible (changing it means changing hardware). **PRIME-1 uses this**, and in the breadboard track the ROM is literally an EEPROM chip you burn.

**Microprogrammed** — a small memory holding a *sequence* of control words per instruction, stepped through by a microsequencer. Each instruction becomes a tiny program in a lower-level language.

| | Hardwired | Microprogrammed |
| :--- | :--- | :--- |
| Speed | Fast | Slower — one micro-step per cycle |
| Complexity | Simple for simple ISAs | Handles complex multi-step instructions |
| Changeable | No | Yes — rewrite the control store |
| Used by | RISC machines | CISC machines, historically |

**This is a large part of the RISC/CISC story.** x86's complex instructions were microprogrammed because implementing them as flat combinational logic was infeasible. RISC's simple, uniform instructions made hardwired control practical — and hardwired control is faster, which is much of where RISC's performance advantage came from.

**Modern x86 does both:** simple instructions are decoded by hardwired logic, complex ones fall back to a microcode ROM. And microcode being *updatable* is how CPU vendors patch errata — including the Spectre and Meltdown mitigations.

---

## 6. Predict before reading on

PRIME-1 is **single-cycle**: every instruction completes in one clock, so the clock period must accommodate the slowest one.

**Which instruction is slowest, and what does that cost the fast ones?**

<details><summary>Check your answer</summary>

**`LD` is slowest.** Trace its path: register file read → ALU (address calculation) → data memory read → writeback multiplexer → register file write. It is the only instruction touching *both* the ALU and memory before writing back.

**Everything else pays for it.** `ADD` skips the memory access entirely and could finish much sooner, but the clock period is set by `LD`, so `ADD` finishes early and then waits.

**This is the fundamental inefficiency of single-cycle design**, and there are two escapes:

1. **Multi-cycle** — break each instruction into steps and let each take only the cycles it needs. `ADD` takes 4, `LD` takes 5. This needs a state machine in the control unit rather than a flat table.
2. **Pipelining** — keep the single-cycle-per-stage structure but overlap instructions, so a new one starts every cycle even though each takes five. Same clock period as multi-cycle, roughly five times the throughput.

**Pipelining is why real processors are fast**, and it is the subject of [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]]. **Build the single-cycle version first** — it is correct, comprehensible, and the thing pipelining is an optimisation *of*.
</details>

---

## 7. Worked example — runnable

Save as `control_derive.py` next to `datapath.py`, and run `python3 control_derive.py`.

```python
"""Derive the control unit MECHANICALLY from the ISA.

The control table in datapath.py was written by hand. This file shows it
was not invented: given a declarative description of what each instruction
DOES, the control signals follow by rule. Then it checks the two agree."""
from datapath import CONTROL, SIGNAL_NAMES, ALU_ADD, ALU_SUB, ALU_AND, \
                     ALU_OR, ALU_XOR, ALU_SHL, ALU_SHR, ALU_SLT

# ---------------------------------------------------------------------------
# The ISA, described by SEMANTICS rather than by control signals.
# Each entry says what the instruction reads, computes and writes.
#   dest    : None | "rd" | "R7"
#   src     : where the written value comes from -- "alu" | "mem" | "pc+1"
#   operand : the ALU's second input -- "rb" | "imm"
#   alu     : which ALU operation
#   mem     : None | "read" | "write"
#   flow    : None | "branch_if_zero" | "branch_if_nonzero" | "jump"
# ---------------------------------------------------------------------------
ISA = {
    0b0000: dict(name="NOP", dest=None,  src=None,   operand="rb",  alu=ALU_ADD),
    0b0001: dict(name="ADD", dest="rd",  src="alu",  operand="rb",  alu=ALU_ADD),
    0b0010: dict(name="SUB", dest="rd",  src="alu",  operand="rb",  alu=ALU_SUB),
    0b0011: dict(name="AND", dest="rd",  src="alu",  operand="rb",  alu=ALU_AND),
    0b0100: dict(name="OR",  dest="rd",  src="alu",  operand="rb",  alu=ALU_OR),
    0b0101: dict(name="XOR", dest="rd",  src="alu",  operand="rb",  alu=ALU_XOR),
    0b0110: dict(name="SHL", dest="rd",  src="alu",  operand="rb",  alu=ALU_SHL),
    0b0111: dict(name="SHR", dest="rd",  src="alu",  operand="rb",  alu=ALU_SHR),
    0b1000: dict(name="SLT", dest="rd",  src="alu",  operand="rb",  alu=ALU_SLT),
    0b1001: dict(name="LDI", dest="rd",  src="alu",  operand="imm", alu=ALU_ADD),
    0b1010: dict(name="LD",  dest="rd",  src="mem",  operand="imm", alu=ALU_ADD,
                 mem="read"),
    0b1011: dict(name="ST",  dest=None,  src=None,   operand="imm", alu=ALU_ADD,
                 mem="write"),
    0b1100: dict(name="BEZ", dest=None,  src=None,   operand="rb",  alu=ALU_ADD,
                 flow="branch_if_zero"),
    0b1101: dict(name="BNZ", dest=None,  src=None,   operand="rb",  alu=ALU_ADD,
                 flow="branch_if_nonzero"),
    0b1110: dict(name="JMP", dest=None,  src=None,   operand="rb",  alu=ALU_ADD,
                 flow="jump"),
    0b1111: dict(name="JAL", dest="R7",  src="pc+1", operand="rb",  alu=ALU_ADD,
                 flow="jump"),
}

def derive(spec):
    """Turn one instruction's semantics into control signals.

    Each rule below is a single sentence of reasoning -- this is the
    entire content of a control unit."""
    mem  = spec.get("mem")
    flow = spec.get("flow")

    # "Does anything get written to a register?"
    reg_write  = 1 if spec["dest"] else 0
    # "Does read port B supply the STORE DATA rather than an ALU operand?"
    reg_b_src  = 1 if mem == "write" else 0
    # "Is the ALU's second input the immediate?"
    alu_src    = 1 if spec["operand"] == "imm" else 0
    alu_op     = spec["alu"]
    mem_read   = 1 if mem == "read" else 0
    mem_write  = 1 if mem == "write" else 0
    # "Does the written value come from memory rather than the ALU?"
    mem_to_reg = 1 if spec["src"] == "mem" else 0
    branch     = 1 if flow in ("branch_if_zero", "branch_if_nonzero") else 0
    branch_not = 1 if flow == "branch_if_nonzero" else 0
    jump       = 1 if flow == "jump" else 0
    # "Is the destination the link register, holding a return address?"
    link       = 1 if spec["dest"] == "R7" else 0

    return (reg_write, reg_b_src, alu_src, alu_op, mem_read,
            mem_write, mem_to_reg, branch, branch_not, jump, link)

if __name__ == "__main__":
    print("DERIVING the control unit from the ISA semantics")
    print()
    print(f"  {'op':>5s} {'name':>5s} | {'dest':>5s} {'src':>5s} {'operand':>8s}"
          f" {'mem':>6s} {'flow':>18s}")
    print("  " + "-" * 62)
    for op in sorted(ISA):
        s = ISA[op]
        print(f"  {op:04b} {s['name']:>5s} | {str(s['dest']):>5s} {str(s['src']):>5s}"
              f" {s['operand']:>8s} {str(s.get('mem')):>6s} {str(s.get('flow')):>18s}")
    print()

    print("The eleven derivation rules, applied:")
    print(f"  {'op':>5s} {'name':>5s} " + " ".join(f"{n[:4]:>4s}" for n in SIGNAL_NAMES))
    print("  " + "-" * 62)
    for op in sorted(ISA):
        vals = " ".join(f"{v:>4d}" for v in derive(ISA[op]))
        print(f"  {op:04b} {ISA[op]['name']:>5s} {vals}")
    print()

    print("CHECK: does the derived table match the hand-written one in")
    print("datapath.py -- the table the simulator, the Verilog and the")
    print("breadboard EEPROM are all built from?")
    mismatches = 0
    for op in sorted(ISA):
        got, want = derive(ISA[op]), CONTROL[op]
        if got != want:
            mismatches += 1
            for name, g, w in zip(SIGNAL_NAMES, got, want):
                if g != w:
                    print(f"    {ISA[op]['name']}: {name} derived={g} handwritten={w}")
    print(f"  16 opcodes compared, {mismatches} mismatches")
    print()
    print("  -> the control unit is a CONSEQUENCE of the ISA, not a design")
    print("     decision. Change the ISA and the table follows mechanically.")

    assert mismatches == 0
    # a control unit for an instruction that does nothing must assert nothing
    assert derive(ISA[0b0000])[0] == 0
    assert sum(derive(ISA[0b0000])) == 0
    print()
    print("control_derive: passed")
```

Expected output:

```
DERIVING the control unit from the ISA semantics

     op  name |  dest   src  operand    mem               flow
  --------------------------------------------------------------
  0000   NOP |  None  None       rb   None               None
  0001   ADD |    rd   alu       rb   None               None
  0010   SUB |    rd   alu       rb   None               None
  0011   AND |    rd   alu       rb   None               None
  0100    OR |    rd   alu       rb   None               None
  0101   XOR |    rd   alu       rb   None               None
  0110   SHL |    rd   alu       rb   None               None
  0111   SHR |    rd   alu       rb   None               None
  1000   SLT |    rd   alu       rb   None               None
  1001   LDI |    rd   alu      imm   None               None
  1010    LD |    rd   mem      imm   read               None
  1011    ST |  None  None      imm  write               None
  1100   BEZ |  None  None       rb   None     branch_if_zero
  1101   BNZ |  None  None       rb   None  branch_if_nonzero
  1110   JMP |  None  None       rb   None               jump
  1111   JAL |    R7  pc+1       rb   None               jump

The eleven derivation rules, applied:
     op  name RegW RegB ALUS ALUO MemR MemW MemT Bran Bran Jump Link
  --------------------------------------------------------------
  0000   NOP    0    0    0    0    0    0    0    0    0    0    0
  0001   ADD    1    0    0    0    0    0    0    0    0    0    0
  0010   SUB    1    0    0    1    0    0    0    0    0    0    0
  0011   AND    1    0    0    2    0    0    0    0    0    0    0
  0100    OR    1    0    0    3    0    0    0    0    0    0    0
  0101   XOR    1    0    0    4    0    0    0    0    0    0    0
  0110   SHL    1    0    0    5    0    0    0    0    0    0    0
  0111   SHR    1    0    0    6    0    0    0    0    0    0    0
  1000   SLT    1    0    0    7    0    0    0    0    0    0    0
  1001   LDI    1    0    1    0    0    0    0    0    0    0    0
  1010    LD    1    0    1    0    1    0    1    0    0    0    0
  1011    ST    0    1    1    0    0    1    0    0    0    0    0
  1100   BEZ    0    0    0    0    0    0    0    1    0    0    0
  1101   BNZ    0    0    0    0    0    0    0    1    1    0    0
  1110   JMP    0    0    0    0    0    0    0    0    0    1    0
  1111   JAL    1    0    0    0    0    0    0    0    0    1    1

CHECK: does the derived table match the hand-written one in
datapath.py -- the table the simulator, the Verilog and the
breadboard EEPROM are all built from?
  16 opcodes compared, 0 mismatches

  -> the control unit is a CONSEQUENCE of the ISA, not a design
     decision. Change the ISA and the table follows mechanically.

control_derive: passed
```

---

## 8. Now build it — choose a track

The design is complete. **The four build tracks live in [[build-your-own-shit/17-your-own-cpu/index|build-your-own-shit/17-your-own-cpu]]**, because they are builds rather than lessons — and because you will keep them open beside a simulator rather than reading them straight through.

| Track | You produce | Time | What only this track teaches |
| :--- | :--- | :--- | :--- |
| [[build-your-own-shit/17-your-own-cpu/03-python-emulator\|3 — Python emulator]] | Emulator + assembler | One evening | **What the ISA means**, and it becomes your oracle |
| [[build-your-own-shit/17-your-own-cpu/01-digital-simulator\|1 — Digital simulator]] | A clickable circuit | A weekend | **What a datapath physically is** — you watch buses light up |
| [[build-your-own-shit/17-your-own-cpu/02-verilog\|2 — Verilog]] | Synthesisable HDL | 2–3 evenings | How hardware is really described; runs on an FPGA |
| [[build-your-own-shit/17-your-own-cpu/04-breadboard\|4 — Breadboard]] | A physical machine | Weeks | That all of it is voltages on wires |

**Do track 3 first**, whatever else you do. It takes an evening, it makes the ISA concrete, and every other track is debugged by diffing against it.

**All four implement the same control table** — the one this module derived. The breadboard track even generates its EEPROM image from it, so the hardware cannot silently disagree with the simulator.

### The milestone order, whichever track

1. **Fetch only** — PC increments, memory is read. *20 minutes, and it eliminates half the possible bugs.*
2. **Decode** — split the instruction into fields and display them.
3. **R-type ALU ops** — register file plus ALU. *Your CPU computes.*
4. **Immediates** — `LDI` and the ALUSrc multiplexer.
5. **Memory** — `LD`, `ST`, and the `RegBSrc` multiplexer.
6. **Branches** — *the milestone that matters.* Your machine can now loop.
7. **Jumps and calls.**
8. **The reference program** — R1 = 55.

---

## 9. Common pitfalls and traps

1. **Inventing the control table by hand.** Derive it from semantics; hand-written tables have exactly the kind of single-bit error that produces baffling behaviour.
2. **Forgetting `RegBSrc`.** Stores read a different register field than everything else. Nobody predicts this one.
3. **Building a combinational loop.** Every feedback path must pass through a register, or the circuit oscillates ([[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]]).
4. **Skipping milestone 1.** "Fetch only" is trivial and catches clock, memory and PC bugs in isolation.
5. **Free-running the clock too early.** Single-step until the reference program works.
6. **Assuming a control unit must be complex.** It is eleven rules and a lookup.

---

## 10. Check your understanding

1. **Why is the control unit a lookup table rather than logic that "figures out" what to do?**
   <details><summary>Answer</summary>
   Because there is nothing to figure out. The opcode is a fixed-width field with a finite set of values, and each value maps to exactly one set of control signals — a pure function from a small domain.<br>
   <strong>Any pure function from a small domain is best implemented as a lookup</strong>, which is [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]]'s MUX-as-LUT result. A ROM addressed by opcode is both the simplest and the fastest implementation.
   </details>

2. **Adding `JR ra` from module 29's exercise: what changes in the control unit?**
   <details><summary>Answer</summary>
   You add one row of <em>semantics</em> — dest=None, flow="jump_register" — and one new control signal, say <code>JumpReg</code>, selecting the PC's source as read port A rather than the address field.<br>
   The derivation rules then produce the row automatically. <strong>The datapath change is one extra input on the PC multiplexer.</strong> That is the whole cost, and it is small precisely because the control unit is derived rather than hand-maintained.
   </details>

3. **Why did CISC architectures use microprogramming while RISC used hardwired control?**
   <details><summary>Answer</summary>
   CISC instructions are complex and multi-step — a single x86 string instruction can loop over memory. Implementing that as flat combinational logic is impractical, so it becomes a small program in a control store, executed step by step.<br>
   RISC instructions are deliberately simple and uniform, each doing one thing in one pass through the datapath. That fits a flat table, and <strong>hardwired control is faster</strong> because there is no micro-step sequencing.<br>
   Much of RISC's early performance advantage came from exactly this: simpler instructions enabling simpler, faster control. Modern x86 hedges — hardwired for simple instructions, microcode for the rest, which also lets vendors ship errata fixes as microcode updates.
   </details>

4. **The lab derives the table and compares it to the hand-written one. Why bother, if you already have a working table?**
   <details><summary>Answer</summary>
   Two reasons. First, it <strong>proves the hand-written table is right</strong> — a single wrong bit produces behaviour that is hard to attribute, and comparing against an independent derivation catches it.<br>
   Second, and more importantly, it proves the table is <strong>a consequence rather than a choice</strong>. If the two agree, the control unit contains no information not already in the ISA — so extending the ISA cannot require creative control design.<br>
   This is the same discipline as differential testing in the build tracks: two independent routes to the same answer, checked against each other.
   </details>

---

## 11. Practice — independent task

**Task:** Extend the control unit for the instructions you added in module 29.

- **(a)** Add `JR ra` to `ISA` in `control_derive.py` with a new `flow` value. Add a `JumpReg` signal and its derivation rule.
- **(b)** Add `HLT`. What signals does it assert? (Consider: what should the PC do?)
- **(c)** Add `LUI rd, imm`. It needs the ALU to shift the immediate left by 6 — can you do that with existing signals, or do you need a new ALU operation?
- **(d)** Update `CONTROL` in `datapath.py` to match, and confirm the derivation still reports zero mismatches.
- **(e)** Draw the datapath changes: which multiplexers gain inputs, and what feeds them?
- **(f)** Implement `JR` and `HLT` in the emulator, and verify a function call and return works end to end.
- **(g)** Regenerate the breadboard control ROM with `control_rom.py` and confirm the new instructions appear in the Intel HEX output.

**Done when:** the derived and hand-written tables still agree, a nested function call returns correctly in the emulator, and the EEPROM image includes your new instructions.

<details><summary>Hint for (b), only if stuck</summary>
The cleanest `HLT` asserts <strong>nothing at all</strong> except a halt flag, and the PC logic simply stops updating — the machine keeps fetching the same instruction forever, which is exactly what a halt is.<br>
On a physical build you also want it to <strong>stop the clock</strong> or light an LED, otherwise you cannot tell "halted" from "hung". That is a real difference between a simulator and a board, and it is worth adding a halt indicator to the breadboard build.
</details>

---

## 12. Tradeoffs and limits

- **Single-cycle is the simplest correct design and the slowest.** Every instruction pays the cost of the slowest one. Multi-cycle and pipelined designs fix this at the cost of a control state machine.
- **No hazard handling.** With one instruction in flight there are no hazards. Pipelining introduces them all at once — see [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]].
- **No exceptions or interrupts.** The control unit has no path for "abandon this instruction and go somewhere else", which a real machine needs.
- **The derivation assumes one control word per instruction.** Multi-cycle or microprogrammed designs need a *sequence*, which is a state machine rather than a lookup — a genuinely bigger step.

---

## Before moving on

- [ ] Explain what a control unit is and why a lookup table is the right implementation.
- [ ] Derive control signals from an instruction's semantics using the eleven rules.
- [ ] Explain why the control table is a consequence of the ISA rather than a design decision.
- [ ] Distinguish hardwired from microprogrammed control and say which suits which ISA style.
- [ ] Explain why `LD` sets the clock period in a single-cycle design.

**Recap:** The control unit turns an opcode into the signals steering the datapath's multiplexers and enables. It is not invented — describing each instruction by what it writes, where the value comes from, what the ALU operand is, whether memory is touched and whether control flow changes yields every signal by a one-line rule. The derived table matches the hand-written one used by all four build tracks, proving the control unit carries no information not already in the ISA. Hardwired control suits simple uniform instruction sets; microprogramming exists for complex ones.

**Next:** [[how-computers-work/08-capstone/04-build-the-assembler|Module 31 — Build the Assembler]] turns assembly text into the machine code this hardware executes.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU]] — the four build tracks
- [[how-computers-work/08-capstone/02-the-isa|Module 29]] — the ISA this control unit derives from
- [[foundations/computer-architecture/05-the-datapath|computer-architecture/the datapath]]
- [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]] — the answer to single-cycle inefficiency
