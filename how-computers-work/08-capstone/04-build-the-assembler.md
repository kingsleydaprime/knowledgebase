# Module 31: Build the Assembler (Text Becomes Machine Code)

**[Intermediate → Advanced]** — The first piece of software in the capstone, and the one that makes everything after it bearable. Nobody hand-encodes instructions twice.

## Before you start

- You have an exact instruction encoding — [[how-computers-work/08-capstone/02-the-isa|module 29]].
- You can write a disassembler — module 29's lab.
- Any programming language. Python is used here.

**After this lesson you will be able to:**

1. Explain why an assembler needs **two** passes, with a concrete failing example.
2. Implement symbol resolution and PC-relative offset calculation.
3. Produce a listing file, and explain why it is the most useful debugging artifact you will build.
4. Report errors that identify what is wrong rather than raising a traceback.

**Study route:** section 3 is the two-pass argument. Section 5 is what separates a usable tool from a script.

---

## 1. Why this exists (real-world motivation)

You have hand-encoded instructions. `ADD R3, R1, R2` became `0x1650` by looking up an opcode, shifting register numbers into position, and OR-ing them together.

**Do that for a fifty-instruction program and you will make a mistake.** Worse, you will make it silently — a wrong bit produces a valid but different instruction, and the machine executes it without complaint.

**Then you insert an instruction near the top, and every branch offset below it is wrong.**

That last problem is the real motivation. An assembler is not just a lookup table for opcodes; **it is the thing that makes your program editable**, because it recomputes every address-dependent value each time you assemble.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Assembler** | Translates assembly text into machine code |
| **Mnemonic** | The human name for an opcode (`ADD`) |
| **Label** | A name for an address |
| **Symbol table** | The map from label names to addresses |
| **Forward reference** | Using a label before it is defined |
| **Two-pass** | Collect labels first, encode second |
| **Listing** | Output showing address, machine word and source together |
| **Directive** | An instruction to the assembler, not the CPU (`.word`, `.org`) |

---

## 3. Why two passes are unavoidable

Consider this, which is the shape of every `if` ever compiled:

```asm
        LDI  R1, 0
        BNZ  R1, done      ; 'done' is defined LATER
        LDI  R1, 99
done:   JMP  done
```

**A single-pass assembler fails here.** When it reaches the `BNZ` it has not yet seen `done`, so it cannot compute the offset. The lab demonstrates exactly this — one pass reports `'done' not yet defined` on a program that is completely valid.

**And you cannot simply forbid forward references.** Every forward branch — every `if`, every `while` exit, every function call to something defined below — is one. Forbidding them would make the assembler useless.

**So: two passes.**

```
   PASS 1   walk the source, count addresses, record where each label
            lands. Emit nothing.
            -> symbol table: {'done': 3}

   PASS 2   walk again and encode. Every label is now known, so
            offsets can be computed.
```

> [!NOTE]
> **This is the same problem compilers and linkers face, at three different scales.**
>
> - An **assembler** resolves labels within one file.
> - A **linker** resolves symbols *between* files — you call `printf` without knowing where it will land, and the linker patches the address once everything is placed. That is **relocation**, and it is why object files carry relocation entries.
> - A **dynamic loader** resolves them at *run time*, when a shared library is mapped at an address nobody knew at compile time.
>
> **All three are the same two-phase pattern:** collect what is defined, then patch what refers to it. Understanding it once here makes [[foundations/compilers/08-code-generation|compilers/code generation]] and the linking material much less mysterious.

---

## 4. The offset calculation, precisely

The single most error-prone line in an assembler:

$$\text{offset} = \text{target} - (\text{address of branch} + 1)$$

**The `+1` is because the PC increments during fetch** ([[how-computers-work/06-memory/02-registers-and-counters|module 25]]), so a branch is relative to the *next* instruction.

Get it wrong and every branch is off by one — loops run one iteration short, or jump into the middle of the instruction before their target.

**And check the range.** A 6-bit signed offset reaches −32 to +31. Beyond that, the assembler must *say so*, not silently wrap:

```
BNZ out of range  ->  range error: branch out of range: 40
```

A silently wrapped offset produces a program that jumps somewhere arbitrary. **This is exactly the class of bug that takes a day to find**, and one `assert` prevents it.

---

## 5. The listing file

**Emit one, early.** A listing shows address, machine word, binary, label and source on one line:

```
  addr  word            binary  label      source
  0000  9200  1001001000000000             LDI  R1, 0
  0001  d041  1101000001000001             BNZ  R1, done
  0002  9223  1001001000100011             LDI  R1, 99
  0003  e003  1110000000000011  done:      JMP  done
```

**This is the most useful debugging artifact in the whole project.** When your CPU executes `0xd041` and does something unexpected, the listing tells you instantly which source line produced it and what the assembler thought it meant.

It is also how you verify the assembler itself: read the binary column against the encoding table from [[how-computers-work/08-capstone/02-the-isa|module 29]] and check by eye.

---

## 6. Error reporting

An assembler that raises a Python traceback tells the user nothing. **Three failure modes deserve three distinct messages:**

| Failure | Message |
| :--- | :--- |
| Branch too far | `range error: branch out of range: 40` |
| Unknown instruction | `unknown mnemonic: 'FROB'` |
| Wrong operand count | `malformed operand: list index out of range` |

**Add line numbers and the source text**, and you have a tool someone else could use. This is not polish — it is the difference between a script and a program, and you will be that user within an hour.

---

## 7. Predict before reading on

Your assembler works. You add one instruction near the top of a working program, reassemble, and now it crashes.

**What went wrong, and whose fault is it?**

<details><summary>Check your answer</summary>

**Nothing went wrong, and it is nobody's fault — if the assembler is correct.** Inserting an instruction shifts every later address by one, so every label moves and every offset is recomputed. That is precisely what the second pass is for, and a correct assembler handles it invisibly.

**If it *does* crash, the likely causes are:**

1. **A branch that was just within range is now out of range.** Adding an instruction between a branch and its target lengthens the offset. The assembler should report this clearly rather than wrapping.
2. **Hardcoded addresses in the source.** If you wrote `JMP 7` instead of `JMP loop`, the numeric address is now wrong. **This is why you use labels for everything** — a numeric address is a hardcoded assumption about layout.
3. **Data mixed into the instruction stream** without a directive to mark it, so the assembler tried to decode it.

**The general lesson:** anything position-dependent must be *computed*, never written down. That is true of assembly labels, of linker relocation, and of position-independent code in shared libraries.
</details>

---

## 8. Worked example — runnable

Save as `assembler_lab.py` next to `prime1.py`, and run `python3 assembler_lab.py`.

**The full two-pass assembler is in [[build-your-own-shit/17-your-own-cpu/03-python-emulator|track 3]]** — this lab demonstrates *why* it is built that way, and what it owes its user.

```python
"""Why an assembler needs two passes, and what good errors look like."""
from prime1 import assemble, OPCODES

FORWARD_REFERENCE = """
        LDI  R1, 0
        BNZ  R1, done      ; 'done' is defined LATER -- a forward reference
        LDI  R1, 99
done:   JMP  done
"""

def one_pass(source):
    """A single-pass assembler. It fails on forward references, because
    when it reaches the branch it has not yet seen the label."""
    labels, program, address, errors = {}, [], 0, []
    for raw in source.strip().splitlines():
        line = raw.split(";")[0].strip()
        if not line:
            continue
        if ":" in line:
            name, _, rest = line.partition(":")
            labels[name.strip()] = address
            line = rest.strip()
            if not line:
                continue
        parts = line.replace(",", " ").split()
        mnemonic, args = parts[0].upper(), parts[1:]
        if mnemonic in ("BNZ", "BEZ", "JMP", "JAL"):
            target = args[-1]
            if not target.lstrip("-").isdigit() and target not in labels:
                errors.append(f"line {address}: '{target}' not yet defined")
        program.append(mnemonic)
        address += 1
    return program, errors

def listing(source):
    """A LISTING file: address, machine word, and the source that made it.
    This is the single most useful debugging artifact an assembler emits."""
    program, labels = assemble(source)
    lines, address = [], 0
    out = []
    for raw in source.strip().splitlines():
        text = raw.split(";")[0].strip()
        if not text:
            continue
        label = next((k for k, v in labels.items() if v == address), "")
        word = program[address]
        shown = raw.strip()
        if label and shown.startswith(label + ":"):
            shown = shown[len(label) + 1:].strip()
        out.append(f"  {address:04x}  {word:04x}  {word:016b}  "
                   f"{(label + ':') if label else '':10s} {shown}")
        address += 1
    return out

def assemble_checked(source):
    """Assemble, but report errors with context instead of raising."""
    try:
        return assemble(source), None
    except AssertionError as e:
        return None, f"range error: {e}"
    except KeyError as e:
        return None, f"unknown mnemonic: {e}"
    except (IndexError, ValueError) as e:
        return None, f"malformed operand: {e}"

if __name__ == "__main__":
    print("WHY TWO PASSES -- the forward reference problem")
    print()
    for line in FORWARD_REFERENCE.strip().splitlines():
        print("  " + line)
    print()
    _, errors = one_pass(FORWARD_REFERENCE)
    print(f"  a ONE-pass assembler reports {len(errors)} error(s):")
    for e in errors:
        print(f"    {e}")
    print("  ...but the program is perfectly valid. The label is simply")
    print("  defined further down, and forward branches are how every")
    print("  'if' and 'while' in every language is compiled.")
    print()
    program, labels = assemble(FORWARD_REFERENCE)
    print(f"  a TWO-pass assembler handles it: labels = {labels}")
    print()
    print("  PASS 1  walk the source, count addresses, record where each")
    print("          label lands. Emit nothing.")
    print("  PASS 2  walk again and encode, now that every label is known.")
    print()

    print("THE LISTING FILE -- address, machine code, and the source line")
    print(f"  {'addr':>6s}  {'word':>4s}  {'binary':>16s}  {'label':10s} source")
    for line in listing(FORWARD_REFERENCE):
        print(line)
    print()

    print("ERROR REPORTING -- what an assembler owes its user")
    bad_programs = [
        ("BNZ out of range",  "        LDI R1, 0\n        BNZ R1, far\n" +
                              "        NOP\n" * 40 + "far:    JMP far"),
        ("unknown mnemonic",  "        FROB R1, R2, R3\nhalt: JMP halt"),
        ("missing operand",   "        ADD R1\nhalt: JMP halt"),
    ]
    for name, src in bad_programs:
        _, err = assemble_checked(src)
        print(f"  {name:20s} -> {err}")
    print()
    print("  each of these is a REAL failure mode. An assembler that raises")
    print("  a bare traceback makes them all look identical.")

    assert len(one_pass(FORWARD_REFERENCE)[1]) == 1
    assert assemble(FORWARD_REFERENCE)[1]["done"] == 3
    assert assemble_checked("FROB R1, R2, R3")[1] is not None
    long_branch = ("LDI R1, 0\nBNZ R1, far\n" + "NOP\n" * 40 + "far: JMP far")
    assert assemble_checked(long_branch)[1] is not None, "range error not caught"
    print()
    print("assembler_lab: passed")
```

Expected output:

```
WHY TWO PASSES -- the forward reference problem

  LDI  R1, 0
          BNZ  R1, done      ; 'done' is defined LATER -- a forward reference
          LDI  R1, 99
  done:   JMP  done

  a ONE-pass assembler reports 1 error(s):
    line 1: 'done' not yet defined
  ...but the program is perfectly valid. The label is simply
  defined further down, and forward branches are how every
  'if' and 'while' in every language is compiled.

  a TWO-pass assembler handles it: labels = {'done': 3}

  PASS 1  walk the source, count addresses, record where each
          label lands. Emit nothing.
  PASS 2  walk again and encode, now that every label is known.

THE LISTING FILE -- address, machine code, and the source line
    addr  word            binary  label      source
  0000  9200  1001001000000000             LDI  R1, 0
  0001  d041  1101000001000001             BNZ  R1, done      ; 'done' is defined LATER -- a forward reference
  0002  9223  1001001000100011             LDI  R1, 99
  0003  e003  1110000000000011  done:      JMP  done

ERROR REPORTING -- what an assembler owes its user
  BNZ out of range     -> range error: branch out of range: 40
  unknown mnemonic     -> unknown mnemonic: 'FROB'
  missing operand      -> malformed operand: list index out of range

  each of these is a REAL failure mode. An assembler that raises
  a bare traceback makes them all look identical.

assembler_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Writing a one-pass assembler.** It cannot handle forward references, which are most branches.
2. **Getting the `+1` wrong.** Offsets are relative to PC-after-increment. Decide once, and make the emulator authoritative.
3. **Not checking offset range.** A silently wrapped branch jumps somewhere arbitrary and is very hard to trace.
4. **Counting label-only lines as instructions.** `loop:` on its own line occupies no address; `loop: ADD ...` occupies one.
5. **Hardcoding addresses in source.** Use labels for everything so insertion is safe.
6. **Skipping the listing file.** It is an hour of work and saves days.

---

## 10. Check your understanding

1. **Could you avoid two passes by back-patching instead?**
   <details><summary>Answer</summary>
   Yes, and it is a real technique. Emit instructions in one pass; when you hit an unresolved label, emit a placeholder and record its location in a <strong>fixup list</strong>. When the label is later defined, go back and patch every recorded location.<br>
   This is one pass over the <em>source</em> but still two visits to the affected instructions — the work is identical, just reorganised. It is what many compilers do internally, because they are generating code in memory anyway. <strong>Two-pass is simpler to get right; back-patching is faster when the source is large.</strong>
   </details>

2. **Why does the assembler compute branch offsets rather than the programmer writing them?**
   <details><summary>Answer</summary>
   Because an offset is a fact about <em>layout</em>, not about intent. The programmer means "go to the top of the loop"; the offset that achieves it changes whenever anything between the branch and the target changes.<br>
   Writing offsets by hand means every edit risks silently breaking every branch nearby. <strong>Labels express intent; offsets express layout; the assembler translates between them.</strong> This is the same separation that lets a linker relocate code.
   </details>

3. **What is a directive, and why isn't `.word 42` an instruction?**
   <details><summary>Answer</summary>
   A directive instructs the <em>assembler</em>, not the CPU. <code>.word 42</code> says "place the value 42 here" — it emits data into the output, but no instruction is being described.<br>
   Others: <code>.org</code> sets the assembly address, <code>.equ</code> defines a constant, <code>.ascii</code> emits text. They are essential because a program is not only code: it has initialised data, lookup tables and constants, and they must land in memory somewhere. <strong>PRIME-1's assembler has no directives, which is why the Pebble compiler in [[how-computers-work/08-capstone/06-build-the-language|module 33]] must generate <code>LDI</code> instructions to create every constant</strong> instead of just placing them in memory.
   </details>

4. **How does an assembler differ from a compiler?**
   <details><summary>Answer</summary>
   An assembler is <strong>one-to-one</strong>: each source line becomes exactly one instruction, and the mapping is mechanical. There is no choice about how to translate <code>ADD R1, R2, R3</code>.<br>
   A compiler is <strong>one-to-many and makes decisions</strong>: <code>x = a + b</code> could become many different instruction sequences depending on where <code>a</code>, <code>b</code> and <code>x</code> live, which registers are free, and what the optimiser decides. <strong>Choosing among valid translations is the compiler's whole job</strong>, and it is why module 33 is the harder build.
   </details>

---

## 11. Practice — independent task

**Task:** Turn the track 3 assembler into a tool you would be willing to use.

- **(a)** Add a listing file output, matching section 5's format.
- **(b)** Add line numbers to every error message, and print the offending source line with a caret under the problem.
- **(c)** Add the `.word` directive so you can place data in memory. Verify with a program that loads a constant from a `.word` and prints it.
- **(d)** Add `.equ NAME value` for named constants, and use it to give `OUT_PORT` a name instead of the bare number 31.
- **(e)** Add a `--disassemble` mode using module 29's disassembler, so the tool round-trips its own output.
- **(f)** Detect and report **duplicate labels**, which currently silently overwrite in the symbol table.
- **(g)** Detect **unreachable code** — instructions after an unconditional `JMP` with no label pointing at them — and emit a warning, not an error.

**Done when:** your assembler produces a listing, reports all three error classes with line numbers, and correctly assembles a program that uses `.word` and `.equ`.

<details><summary>Hint for (f), only if stuck</summary>
In pass 1, before recording a label, check whether it is already in the symbol table. If it is, that is an error — two different addresses cannot share a name, and whichever wins, some branch will silently go to the wrong place.<br>
Real assemblers distinguish <strong>local labels</strong> (often written <code>1:</code>, <code>2:</code>, and referenced as <code>1f</code> for "next 1 forward") precisely so that repeated names inside macros do not collide. That is worth knowing exists, though it is beyond what PRIME-1 needs.
</details>

---

## 12. Tradeoffs and limits

- **No macros.** Real assemblers support macro expansion, which is a small textual language of its own and a common source of confusion when it goes wrong.
- **No object file output.** This assembler emits a flat image starting at address 0. A real one emits relocatable objects with symbol and relocation tables for a linker to combine — the gap flagged in [[how-computers-work/07-the-bridge|the bridge]].
- **No expression evaluation.** `LDI R1, 4*8+2` is rejected. Real assemblers evaluate constant expressions at assembly time.
- **One section only.** Real programs separate `.text`, `.data` and `.bss`; PRIME-1 puts everything in one address space with no distinction.

---

## Before moving on

- [ ] Explain the forward reference problem and why it forces two passes.
- [ ] Compute a PC-relative offset correctly, including the `+1`.
- [ ] Explain why offset range must be checked rather than wrapped.
- [ ] Produce a listing file and say why it is worth the effort.
- [ ] Explain the parallel between assembler symbols, linker relocation and dynamic loading.

**Recap:** An assembler translates mnemonics to machine code and — more importantly — computes every address-dependent value so the program stays editable. Forward references make two passes unavoidable: pass 1 builds the symbol table, pass 2 encodes. Branch offsets are relative to PC-after-increment and must be range-checked rather than silently wrapped. A listing file and specific error messages are what separate a usable tool from a script, and the collect-then-patch pattern reappears at larger scale in linkers and dynamic loaders.

**Next:** [[how-computers-work/08-capstone/05-build-the-emulator|Module 32 — Build the Emulator]] gives you a software PRIME-1 and, crucially, the oracle you test your hardware against.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[build-your-own-shit/17-your-own-cpu/03-python-emulator|Track 3]] — the full assembler implementation
- [[how-computers-work/08-capstone/02-the-isa|Module 29]] — the encoding being generated
- [[foundations/compilers/08-code-generation|compilers/code generation]] — where assembly output and object files are covered
