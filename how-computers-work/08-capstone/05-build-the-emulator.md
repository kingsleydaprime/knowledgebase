# Module 32: Build the Emulator (Your Oracle)

**[Intermediate → Advanced]** — A software PRIME-1. Its real value is not that it runs your programs, but that it is the **reference implementation** every other build is tested against.

## Before you start

- You have an ISA and an assembler — modules [[how-computers-work/08-capstone/02-the-isa|29]] and [[how-computers-work/08-capstone/04-build-the-assembler|31]].
- You can write a disassembler — module 29's lab.

**After this lesson you will be able to:**

1. Build a debugger with breakpoints, watches and disassembly.
2. Explain differential testing and why it beats staring at waveforms.
3. Implement test-case shrinking, and explain why a minimal failure is worth more than a failing one.
4. Explain what an emulator can and cannot tell you about your hardware.

**Study route:** section 4 is the technique that will actually find your hardware bugs.

---

## 1. Why this exists (real-world motivation)

The emulator is the easiest track to build — one evening — and the most valuable thing you will produce, for a reason that has nothing to do with running programs.

**When your circuit gives 54 instead of 55, what do you do?**

Without a reference, you stare at a schematic and guess. With one, you run the same program on both, compare state cycle by cycle, and find the exact cycle where they diverge. **That cycle contains your bug.**

**An emulator turns debugging from an art into a search.** That is why [[build-your-own-shit/17-your-own-cpu/index|the build guide]] insists you write it first, before wiring anything.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Emulator** | Software that behaves like the hardware, instruction for instruction |
| **Oracle** | A trusted reference the thing under test is compared against |
| **Differential testing** | Running the same input through two implementations and diffing |
| **Shrinking** | Reducing a failing test case to the smallest still-failing one |
| **Breakpoint** | Stop execution when the PC reaches an address |
| **Watch** | Report whenever a register or address changes |
| **Cycle-accurate** | Matching the hardware's timing, not just its results |

---

## 3. The debugger

**Forty lines turn an emulator into something you can investigate.** Three features carry almost all the value:

**Disassembly** — print each executed instruction as text, not hex. Requires module 29's address-aware disassembler.

**Watches** — report when a chosen register changes:

```
  0002  1250  ADD R1, R1, R2           R1: 0 -> 10
  0004  2498  SUB R2, R2, R3           R2: 10 -> 9
  0005  d0bc  BNZ R2, 2
```

**Breakpoints** — run freely until the PC reaches an address, then stop and let you look.

**Read that trace and the loop is visible**: R1 accumulating, R2 counting down, and `BNZ R2, 2` sending control back to address 2. That is your machine executing your program, in a form you can read.

---

## 4. Differential testing — the technique that matters

Hand-written tests check the cases you thought of. **Differential testing checks cases you did not.**

```
   random program ──┬──► emulator  ──► final register state ─┐
                    │                                        ├──► compare
                    └──► datapath  ──► final register state ─┘
```

The lab generates **300 random straight-line programs**, runs each on both the emulator and the datapath model, and compares final register state and cycle count. **Zero mismatches.**

**Straight-line only, deliberately.** Random jumps produce programs that loop forever or run off the end. Restricting to ALU and immediate instructions keeps every program bounded and every comparison meaningful. Branches are tested separately with structured programs.

> [!NOTE]
> **This is how you will actually debug your circuit.** When the Verilog or the breadboard disagrees with the emulator, you do not reason about it — you generate programs until one fails, then shrink it.
>
> It is also standard industrial practice. CPU verification teams run **billions** of randomly generated instruction sequences against a reference model, because the state space is far too large to test by hand. **You are doing a small version of exactly the real thing.**

---

## 5. Shrinking — turning a failure into a bug report

A random failing program is twelve unrelated instructions. That is a puzzle, not a diagnosis.

**Shrinking removes lines while the failure persists**, leaving the smallest program that still breaks:

```python
for i in range(len(lines) - 1):
    trial = lines[:i] + lines[i+1:]
    if still_fails(trial):
        lines = trial          # keep the shorter version, repeat
```

A twelve-instruction failure typically shrinks to two or three. **That is a bug report** — you can read it, reason about it, and fix it.

This is the core idea behind property-based testing tools like QuickCheck and Hypothesis, and it is worth having implemented once by hand.

---

## 6. Predict before reading on

Your emulator gives 55. Your Verilog gives 55. Your breadboard gives 55.

**Does that prove all three are correct?**

<details><summary>Check your answer</summary>

**No.** It proves they agree on *one program*.

Three specific gaps:

1. **Agreement is not correctness.** If you made the same conceptual error in all three — say, misreading your own spec on the branch reference point — they will agree with each other and disagree with the specification. **Differential testing finds discrepancies, not misconceptions.** The defence is the round-trip and specification tests of [[how-computers-work/08-capstone/02-the-isa|module 29]], which check against the *contract* rather than against another implementation.

2. **One program exercises a fraction of the state space.** The reference program never executes `AND`, `SLT`, `LD`, `ST` or `JAL`. Random testing is what covers those.

3. **The emulator is not cycle-accurate to real hardware.** It counts instructions, not gate delays. It cannot tell you that your critical path is too long, that you have a setup-time violation, or that a signal glitches. **Timing bugs are invisible to an emulator** — that is what simulation waveforms and static timing analysis are for.

**An emulator verifies *logic*, not *timing*.** Both matter, and they need different tools.
</details>

---

## 7. Worked example — runnable

Save as `emulator_lab.py` next to `prime1.py`, `datapath.py` and `isa_lab.py`, and run `python3 emulator_lab.py`.

```python
"""The emulator as ORACLE: a debugger, and differential testing against
the datapath model. This is how you find bugs in hardware you built."""
import random
from prime1 import Prime1, assemble, OPCODES, REFERENCE_PROGRAM
from datapath import Datapath
from isa_lab import disassemble

# ---------------------------------------------------------------- DEBUGGER
class Debugger:
    """~40 lines that turn an emulator into something you can investigate."""
    def __init__(self, cpu):
        self.cpu = cpu
        self.breakpoints = set()
        self.watches = []
        self.log = []

    def breakpoint(self, addr):  self.breakpoints.add(addr)
    def watch(self, reg):        self.watches.append(reg)

    def step(self):
        pc_before = self.cpu.pc
        before = list(self.cpu.reg)
        word = self.cpu.mem[pc_before]
        self.cpu.step()
        changed = [f"R{i}: {before[i]} -> {self.cpu.reg[i]}"
                   for i in self.watches if before[i] != self.cpu.reg[i]]
        self.log.append((pc_before, word, changed))
        return pc_before, word, changed

    def run_until_breakpoint(self, max_cycles=10000):
        while not self.cpu.halted and self.cpu.cycles < max_cycles:
            self.step()
            if self.cpu.pc in self.breakpoints:
                return self.cpu.pc
        return None

    def trace(self, limit=None):
        out = []
        for pc, word, changed in (self.log[:limit] if limit else self.log):
            note = ("   " + ", ".join(changed)) if changed else ""
            out.append(f"  {pc:04x}  {word:04x}  {disassemble(word, pc):22s}{note}")
        return out

# ----------------------------------------------------- DIFFERENTIAL TESTING
ALU_OPS = ["ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "SLT"]

def random_program(rng, length=12):
    """Straight-line code only -- no jumps, so execution is bounded and
    both implementations must agree cycle for cycle."""
    lines = []
    for _ in range(length):
        if rng.random() < 0.35:
            lines.append(f"LDI R{rng.randint(1,7)}, {rng.randint(-32,31)}")
        else:
            op = rng.choice(ALU_OPS)
            lines.append(f"{op} R{rng.randint(1,7)}, "
                         f"R{rng.randint(0,7)}, R{rng.randint(0,7)}")
    lines.append("halt: JMP halt")
    return "\n".join(lines)

def differential_test(n_programs=300, seed=1):
    """Run identical programs on both implementations, compare final state."""
    rng = random.Random(seed)
    mismatches = []
    for i in range(n_programs):
        src = random_program(rng)
        program, _ = assemble(src)
        a = Prime1();   a.load(program);   a.run()
        b = Datapath(); b.load(program);   b.run()
        if a.reg[:8] != b.reg[:8] or a.cycles != b.cycles:
            mismatches.append((i, src, a.reg[:8], b.reg[:8]))
    return mismatches

def shrink(src):
    """Given a failing program, remove lines while it still fails.

    A 200-line failure is unreadable; a 3-line failure is a bug report."""
    lines = src.strip().splitlines()
    changed = True
    while changed:
        changed = False
        for i in range(len(lines) - 1):          # never drop the halt
            trial = lines[:i] + lines[i+1:]
            try:
                program, _ = assemble("\n".join(trial))
                a = Prime1();   a.load(program);   a.run()
                b = Datapath(); b.load(program);   b.run()
                if a.reg[:8] != b.reg[:8]:
                    lines, changed = trial, True
                    break
            except Exception:
                continue
    return "\n".join(lines)

if __name__ == "__main__":
    print("THE DEBUGGER -- stepping the reference program")
    program, labels = assemble(REFERENCE_PROGRAM)
    cpu = Prime1(); cpu.load(program)
    dbg = Debugger(cpu)
    dbg.watch(1); dbg.watch(2)
    dbg.breakpoint(labels["loop"])

    hit = dbg.run_until_breakpoint()
    print(f"  ran until breakpoint at 'loop' (address {hit})")
    print(f"  {'addr':>6s}  {'word':>4s}  {'disassembly':22s}   watched changes")
    for line in dbg.trace():
        print(line)
    print()
    for _ in range(6):
        dbg.step()
    print("  ...six more steps, watching R1 and R2:")
    for line in dbg.trace()[-6:]:
        print(line)
    cpu.run()
    print(f"  final: R1 = {cpu.reg[1]} after {cpu.cycles} cycles")
    print()

    print("DIFFERENTIAL TESTING -- emulator vs datapath model")
    print("  300 random straight-line programs, 12 instructions each,")
    print("  run on both implementations, final register state compared.")
    mismatches = differential_test()
    print(f"  mismatches: {len(mismatches)}")
    if mismatches:
        i, src, ra, rb = mismatches[0]
        print(f"  first failure (program {i}), shrunk to a minimal case:")
        for line in shrink(src).splitlines():
            print("      " + line)
        print(f"      emulator: {ra}")
        print(f"      datapath: {rb}")
    else:
        print("  -> the two implementations agree on every program.")
        print("     When your CIRCUIT disagrees, this is the harness that")
        print("     finds the smallest program showing the bug.")
    print()

    print("WHY SHRINKING MATTERS")
    print("  a random failing program is 12 unrelated instructions.")
    print("  shrink() removes lines while the failure persists, leaving")
    print("  the smallest program that still breaks -- which is a bug")
    print("  report rather than a puzzle.")

    assert cpu.reg[1] == 55
    assert len(mismatches) == 0
    assert len(dbg.log) > 0
    print()
    print("emulator_lab: passed")
```

Expected output:

```
THE DEBUGGER -- stepping the reference program
  ran until breakpoint at 'loop' (address 2)
    addr  word  disassembly              watched changes
  0000  9200  LDI R1, 0             
  0001  940a  LDI R2, 10               R2: 0 -> 10

  ...six more steps, watching R1 and R2:
  0002  1250  ADD R1, R1, R2           R1: 0 -> 10
  0003  9601  LDI R3, 1             
  0004  2498  SUB R2, R2, R3           R2: 10 -> 9
  0005  d0bc  BNZ R2, 2             
  0002  1250  ADD R1, R1, R2           R1: 10 -> 19
  0003  9601  LDI R3, 1             
  final: R1 = 55 after 43 cycles

DIFFERENTIAL TESTING -- emulator vs datapath model
  300 random straight-line programs, 12 instructions each,
  run on both implementations, final register state compared.
  mismatches: 0
  -> the two implementations agree on every program.
     When your CIRCUIT disagrees, this is the harness that
     finds the smallest program showing the bug.

WHY SHRINKING MATTERS
  a random failing program is 12 unrelated instructions.
  shrink() removes lines while the failure persists, leaving
  the smallest program that still breaks -- which is a bug
  report rather than a puzzle.

emulator_lab: passed
```

---

## 8. Common pitfalls and traps

1. **Building the emulator after the hardware.** It is your oracle; build it first or debug blind.
2. **Generating random programs with jumps.** They loop forever. Restrict to straight-line code, and test control flow separately.
3. **Comparing only the final state.** Comparing cycle by cycle tells you *where* the divergence starts, which is far more useful.
4. **Not shrinking failures.** A twelve-instruction failure is a puzzle; a two-instruction one is a fix.
5. **Trusting agreement as correctness.** Two implementations sharing a misconception agree perfectly.
6. **Expecting the emulator to catch timing bugs.** It cannot. It has no notion of gate delay.

---

## 9. Check your understanding

1. **Why compare cycle counts as well as register state?**
   <details><summary>Answer</summary>
   Because a difference in cycle count reveals a control-flow divergence that final state might hide. Two implementations could reach the same registers by different routes — one taking a branch the other did not, then converging.<br>
   Cycle count is a cheap, sensitive proxy for "did these execute the same instructions". If states match but counts differ, something took a different path and you have found a real bug that state comparison alone would have missed.
   </details>

2. **Your emulator and circuit agree for 10,000 random programs, then the circuit fails on real code. What kind of bug is likely?**
   <details><summary>Answer</summary>
   Almost certainly something the random generator never produced. Straight-line random tests exercise the ALU thoroughly and <strong>never test branches, memory or interactions between them</strong>.<br>
   Likely candidates: a branch offset edge case, a load immediately following a store to the same address, or a `JAL` whose link register write collides with something. <strong>The fix is to extend the generator</strong> — add structured control flow, add memory operations, add sequences designed to create dependencies. Coverage of the generator is the real limit on what random testing finds.
   </details>

3. **How would you make the emulator cycle-accurate, and is it worth it?**
   <details><summary>Answer</summary>
   You would model the datapath stage by stage rather than instruction by instruction, tracking when each value becomes available and adding delay for memory access, and eventually pipeline registers and stalls.<br>
   <strong>For a single-cycle machine it is not worth it</strong> — every instruction takes one cycle by definition, so instruction count <em>is</em> cycle count. It becomes essential once you pipeline, because then performance depends on hazards and stalls, and an instruction-count model would be badly wrong. Real projects keep both: a fast functional model for correctness, a slow cycle-accurate one for performance.
   </details>

4. **Why is an emulator more useful than a simulator waveform for finding logic bugs?**
   <details><summary>Answer</summary>
   A waveform shows you <em>everything</em> at every instant — hundreds of signals, most irrelevant. Finding a bug means knowing what to look at and when.<br>
   An emulator gives you a <strong>known-correct answer to compare against</strong>, which converts the problem from "inspect everything" to "find the first cycle where these two disagree". You then open the waveform <em>at that cycle</em>, already knowing which value is wrong.<br>
   <strong>The waveform is for diagnosis; the emulator is for localisation.</strong> You need both, in that order.
   </details>

---

## 10. Practice — independent task

**Task:** Extend the test harness until it would genuinely catch a hardware bug.

- **(a)** Extend `random_program()` to emit `LD` and `ST` with safe addresses, and confirm both implementations still agree.
- **(b)** Add structured control flow: generate a random loop with a bounded counter, so branches are exercised without risking non-termination.
- **(c)** Change the comparison from final-state to **per-cycle**: run both one step at a time and report the first cycle where any register differs.
- **(d)** Deliberately break the datapath — invert one bit in the `CONTROL` table — and confirm your harness finds it and shrinks to a minimal case. **A test suite that has never caught a bug is untested.**
- **(e)** Measure coverage: which of the 16 opcodes did 300 random programs execute? Adjust the generator until all 16 are covered.
- **(f)** Add a `--trace` mode dumping every cycle's PC, instruction and registers in a diffable format, so you can `diff` two implementations' logs directly.
- **(g)** Write the `JAL`/return sequence from module 29's exercise and verify it in the debugger, watching R7.

**Done when:** your harness catches the deliberate bug from (d), shrinks it to under four instructions, and reports full opcode coverage.

<details><summary>Hint for (d), only if stuck</summary>
Flip <code>RegWrite</code> to 0 for <code>ADD</code>, or <code>ALUSrc</code> to 1 for a register-register operation. Then run the harness.<br>
<strong>If it does not catch the bug, that is the more interesting result</strong> — it means your generator never produces a program where that signal matters. Work out why, and fix the generator. This is exactly how coverage-guided fuzzing works, and doing it once by hand makes the idea concrete.
</details>

---

## 11. Tradeoffs and limits

- **Functional, not timing-accurate.** No gate delays, no setup/hold, no glitches. Timing bugs need simulation and static analysis.
- **No I/O beyond memory-mapped output.** Real emulators model peripherals, interrupts and DMA.
- **Random testing has diminishing returns.** After a point, extra random programs explore the same paths. Coverage-guided generation is the answer, and it is what industrial verification uses.
- **Agreement is not correctness.** Both implementations can share a misconception. Specification-level tests are the complement.

---

## Before moving on

- [ ] Build a debugger with breakpoints, watches and disassembly.
- [ ] Explain differential testing and why it finds bugs hand-written tests miss.
- [ ] Implement shrinking and explain why a minimal failure is worth more.
- [ ] State three things an emulator cannot tell you about your hardware.

**Recap:** The emulator's value is as an oracle. A debugger with disassembly, watches and breakpoints makes execution readable; differential testing against a second implementation finds discrepancies no hand-written test would; and shrinking reduces a random failure to a minimal case you can actually reason about. Agreement between implementations is not proof of correctness — shared misconceptions survive it — and an emulator verifies logic while saying nothing about timing.

**Next:** [[how-computers-work/08-capstone/06-build-the-language|Module 33 — Build the Language]] is where the course's two directions meet: a compiler for a language you designed, emitting instructions for a CPU you designed.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[build-your-own-shit/17-your-own-cpu/03-python-emulator|Track 3]] — the emulator implementation
- [[how-computers-work/08-capstone/03-build-the-hardware|Module 30]] — the datapath model this is diffed against
- [[how-computers-work/08-capstone/02-the-isa|Module 29]] — the disassembler the debugger uses
