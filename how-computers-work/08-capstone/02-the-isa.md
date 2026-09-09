# Module 29: The PRIME-1 ISA (The Contract)

**[Advanced]** — Module 28 made the design decisions. This module turns them into an exact binary encoding — the contract that every piece of hardware and every program must agree on.

## Before you start

- You have made the design decisions and can justify them — [[how-computers-work/08-capstone/01-design-the-cpu|module 28]].
- You can read a bit field and understand sign extension — [[how-computers-work/05-combinational/02-adders|module 21]].
- You have read [[foundations/computer-architecture/03-instruction-sets|computer-architecture/instruction sets]].

**After this lesson you will be able to:**

1. Specify an instruction encoding precisely enough to build hardware from it.
2. Explain the addressing modes PRIME-1 supports and the ones it deliberately omits.
3. Write a disassembler, and explain why it must know an instruction's address.
4. Prove an ISA is unambiguous by round-tripping every encodable instruction.

**Study route:** section 4 is the specification you will keep open while building. Section 6 is the verification technique, and it found a real bug in this very spec.

---

## 1. Why this exists (real-world motivation)

**An ISA is a contract, and it is the only one in the whole system that both sides must honour exactly.**

Hardware promises: *give me these bits and I will do this.* Software promises: *I will only send you bits that mean something.* Neither side needs to know anything else about the other — which is why the same binary runs on an Intel and an AMD chip whose internal designs share almost nothing.

**The contract must be exact.** "The immediate field is six bits" is not enough. Signed or unsigned? Sign-extended to what width? Relative to which address? Every ambiguity becomes a bug that appears only in the case nobody tested.

This module writes the contract down, and then **proves it is unambiguous** rather than asserting it.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Encoding** | The bit layout of an instruction |
| **Field** | A named group of bits within an instruction |
| **Opcode** | The field selecting which instruction this is |
| **Immediate** | A constant carried inside the instruction itself |
| **Addressing mode** | How an operand's location is expressed |
| **PC-relative** | An address given as an offset from the program counter |
| **Disassembler** | Machine code back to assembly text — the assembler's inverse |
| **Round-trip** | assemble(disassemble(x)) == x, the ambiguity test |
| **Load-store architecture** | ALU works only on registers; memory reached only by load/store |

---

## 3. The three formats

Every PRIME-1 instruction is exactly **16 bits**, in one of three shapes:

```
   R-type   [op:4][rd:3][ra:3][rb:3][fn:3]     register-register
   I-type   [op:4][rd:3][ra:3][   imm:6   ]     immediate and memory
   J-type   [op:4][        addr:12        ]     jumps
```

**All three total exactly 16 bits**, which is the constraint module 28's budget was solving.

**The `fn` field on R-type is currently unused** — three spare bits. That is deliberate: it is the escape hatch from [[how-computers-work/08-capstone/01-design-the-cpu|module 28]]'s section 7, where you add `JR` and `HLT` without disturbing anything else.

---

## 4. The instruction set

| Opcode | Mnemonic | Format | Operation |
| :--- | :--- | :--- | :--- |
| `0000` | `NOP` | — | do nothing |
| `0001` | `ADD rd, ra, rb` | R | `rd = ra + rb` |
| `0010` | `SUB rd, ra, rb` | R | `rd = ra - rb` |
| `0011` | `AND rd, ra, rb` | R | `rd = ra & rb` |
| `0100` | `OR rd, ra, rb` | R | `rd = ra \| rb` |
| `0101` | `XOR rd, ra, rb` | R | `rd = ra ^ rb` |
| `0110` | `SHL rd, ra, rb` | R | `rd = ra << rb` |
| `0111` | `SHR rd, ra, rb` | R | `rd = ra >> rb` |
| `1000` | `SLT rd, ra, rb` | R | `rd = 1 if ra < rb else 0` (**signed**) |
| `1001` | `LDI rd, imm` | I | `rd = sign_extend(imm)` |
| `1010` | `LD rd, ra, imm` | I | `rd = mem[ra + imm]` |
| `1011` | `ST rd, ra, imm` | I | `mem[ra + imm] = rd` |
| `1100` | `BEZ ra, imm` | I | `if ra == 0: PC += imm` |
| `1101` | `BNZ ra, imm` | I | `if ra != 0: PC += imm` |
| `1110` | `JMP addr` | J | `PC = addr` |
| `1111` | `JAL addr` | J | `R7 = PC + 1; PC = addr` |

### The details that must be nailed down

**These are the ambiguities that become bugs:**

1. **Immediates are signed**, in two's complement, sign-extended from bit 5 to 16 bits. `LDI R1, -1` gives `0xFFFF`, not `0x003F`.
2. **Branch offsets are relative to PC-after-increment.** The PC increments during fetch, so `BNZ` at address 5 with offset −4 goes to address 2, not 1.
3. **Memory is word-addressed.** `mem[5]` is the sixth 16-bit word.
4. **R0 is hardwired to zero.** Writes are discarded, not stored.
5. **`SLT` is signed.** An unsigned variant would need its own opcode.
6. **Flags are set by arithmetic only.** Logical operations leave C and V untouched.

**Write these down in your own spec.** Every one is a decision, and every one has a wrong answer that half-works.

---

## 5. Addressing modes

PRIME-1 supports four, and the omissions matter as much as the inclusions:

| Mode | Example | How the operand is found |
| :--- | :--- | :--- |
| **Register** | `ADD R1, R2, R3` | In a register |
| **Immediate** | `LDI R1, 5` | Inside the instruction |
| **Base + displacement** | `LD R1, R2, 4` | `mem[R2 + 4]` |
| **PC-relative** | `BNZ R1, loop` | `PC + offset` |

**Deliberately omitted:**

- **Direct addressing** (`LD R1, 0x1234`) — a 16-bit address does not fit alongside an opcode and a register in 16 bits. Use `LDI` then base+0.
- **Register-indirect with auto-increment** — convenient for array loops, but it means an instruction writes *two* registers, which complicates the register file's write port.
- **Indexed** (`mem[ra + rb]`) — would need a third register field on an I-type, which does not fit.

> [!NOTE]
> **Base + displacement is the one that earns its keep.** It gives you struct field access (`mem[base + field_offset]`), stack frame access (`mem[SP + local_offset]`), and array access with a constant index — all from one mode.
>
> **This is why almost every real ISA has it**, and why the compiler in [[how-computers-work/08-capstone/06-build-the-language|module 33]] will lean on it for every variable access.

---

## 6. Proving the contract is unambiguous

Here is the technique, and it is the reason this module has a lab.

**An ISA is ambiguous if either:**

- two different instructions can produce the same bits, or
- one instruction has no unique textual form.

**The test: for every encodable word, disassemble it, reassemble the result, and require identical bits.**

$$\text{assemble}(\text{disassemble}(w)) = w \quad \text{for all valid } w$$

The lab runs this over **6,267 encodings** — every register combination for every R-type, every immediate for `LDI`, every branch offset, and the J-type address boundaries. **Zero mismatches.**

> [!NOTE]
> **This test found a real bug in this spec, and it is worth knowing what it was.**
>
> The first version failed immediately. The assembler treated `BNZ R4, -3` as a **target address** and computed the offset itself. The disassembler emitted the raw **offset**. Round-tripping therefore computed an offset of an offset, and diverged.
>
> **The encoding was never ambiguous — the assembly *syntax* was.** Two tools disagreed about what the text meant, and nothing in the spec settled it.
>
> **The fix taught something real:** `disassemble()` now takes the instruction's **address**, because a branch immediate is PC-relative — the same 16 bits mean different targets at different addresses.
>
> That is why real disassemblers take a base address, why `objdump` shows addresses in its left column, and ultimately **why relocation exists**: position-dependent encodings must be adjusted when code moves. A round-trip test on a toy ISA surfaced the same issue that shapes real executable formats.

---

## 7. Predict before reading on

`JAL` writes the return address to R7 and jumps. To return, you need to jump to *the address in a register* — and PRIME-1 has no such instruction.

**Using only the 16 instructions above, how do you return from a function?**

<details><summary>Check your answer</summary>

**You cannot, cleanly.** This is the gap [[build-your-own-shit/17-your-own-cpu/index|the build guide]] flags and [[how-computers-work/08-capstone/01-design-the-cpu|module 28]] told you to fix.

**The ugly workaround:** store R7 into memory, then use self-modifying code — write a `JMP` instruction with the right address into the instruction stream and jump to it. This works, it is genuinely how some early machines did it, and it is horrible: it breaks with caches, it breaks with read-only code, and it is unanalysable.

**The right fix, from module 28's section 7:** use the R-type `fn` field. Make one opcode a system group where `fn` selects the operation:

```
   fn = 000  ->  JR ra      (PC = ra)
   fn = 001  ->  HLT
   fn = 010  ->  reserved
```

**One opcode now holds eight instructions**, and you have spent nothing you were using. This is exactly what MIPS does with its `funct` field.

**Do this before building.** A CPU without a working `return` cannot run a compiled language, which makes [[how-computers-work/08-capstone/06-build-the-language|module 33]] impossible.
</details>

---

## 8. Worked example — runnable

The disassembler is the highest-value tool you will write for this project: it lets you read memory dumps as instructions and check what your assembler actually produced.

Save as `isa_lab.py` next to `prime1.py`, and run `python3 isa_lab.py`.

```python
"""The PRIME-1 ISA: encoding, decoding, and a round-trip proof.

An ISA is a CONTRACT. This file is that contract made executable --
if assemble(disassemble(w)) != w for any valid w, the spec is ambiguous."""
from prime1 import OPCODES, R_TYPE, I_TYPE, J_TYPE, assemble, sign_extend

MNEMONIC = {v: k for k, v in OPCODES.items()}

FORMAT = {}
for name, op in OPCODES.items():
    FORMAT[op] = ("R" if name in R_TYPE else
                  "J" if name in J_TYPE else
                  "I" if name in I_TYPE else "-")

def fields(word):
    """Split a 16-bit instruction into every field, regardless of format."""
    return {
        "op":   (word >> 12) & 0xF,
        "rd":   (word >> 9)  & 0x7,
        "ra":   (word >> 6)  & 0x7,
        "rb":   (word >> 3)  & 0x7,
        "fn":   word & 0x7,
        "imm":  sign_extend(word & 0x3F, 6),
        "addr": word & 0xFFF,
    }

def disassemble(word, address=0):
    """Machine code back to assembly text. The inverse of the assembler.

    NOTE the `address` parameter. Branch immediates are PC-relative, so
    the same 16 bits mean different targets at different addresses. A
    disassembler that does not know where an instruction lives cannot
    print its branch target -- which is also why relocation exists."""
    f = fields(word)
    op = f["op"]
    name = MNEMONIC.get(op, "???")
    fmt = FORMAT.get(op, "-")
    if name == "NOP":
        return "NOP"
    if fmt == "R":
        return f"{name} R{f['rd']}, R{f['ra']}, R{f['rb']}"
    if fmt == "J":
        return f"{name} {f['addr']}"
    if name == "LDI":
        return f"{name} R{f['rd']}, {f['imm']}"
    if name in ("LD", "ST"):
        return f"{name} R{f['rd']}, R{f['ra']}, {f['imm']}"
    if name in ("BEZ", "BNZ"):
        target = address + 1 + f["imm"]        # relative to PC-after-increment
        return f"{name} R{f['ra']}, {target}"
    return f"{name} ?"

def encode_one(text):
    """Assemble a single instruction (no labels)."""
    program, _ = assemble(text)
    return program[0]

def field_layout(fmt):
    """Which bits belong to which field, for the encoding diagram."""
    return {
        "R": [("op", 15, 12), ("rd", 11, 9), ("ra", 8, 6), ("rb", 5, 3), ("fn", 2, 0)],
        "I": [("op", 15, 12), ("rd", 11, 9), ("ra", 8, 6), ("imm", 5, 0)],
        "J": [("op", 15, 12), ("addr", 11, 0)],
    }[fmt]

if __name__ == "__main__":
    print("INSTRUCTION FORMATS -- every instruction is exactly 16 bits")
    for fmt in ("R", "I", "J"):
        parts = " ".join(f"[{n}:{hi-lo+1}]" for n, hi, lo in field_layout(fmt))
        total = sum(hi - lo + 1 for _, hi, lo in field_layout(fmt))
        print(f"  {fmt}-type  {parts:44s} = {total} bits")
    print()

    print("THE INSTRUCTION SET")
    print(f"  {'op':>5s} {'mnemonic':>9s} {'fmt':>4s}  operation")
    ops = {
        "NOP": "do nothing", "ADD": "rd = ra + rb", "SUB": "rd = ra - rb",
        "AND": "rd = ra & rb", "OR": "rd = ra | rb", "XOR": "rd = ra ^ rb",
        "SHL": "rd = ra << rb", "SHR": "rd = ra >> rb",
        "SLT": "rd = 1 if ra < rb else 0  (signed)",
        "LDI": "rd = sign_extend(imm)", "LD": "rd = mem[ra + imm]",
        "ST":  "mem[ra + imm] = rd", "BEZ": "if ra == 0: PC += imm",
        "BNZ": "if ra != 0: PC += imm", "JMP": "PC = addr",
        "JAL": "R7 = PC + 1; PC = addr",
    }
    for name, op in sorted(OPCODES.items(), key=lambda kv: kv[1]):
        print(f"  {op:04b} {name:>9s} {FORMAT[op]:>4s}  {ops[name]}")
    print()

    print("ENCODING one instruction of each format, field by field")
    samples = ["ADD R3, R1, R2", "LDI R5, -7", "LD R2, R1, 4", "BNZ R4, 0", "JMP 100"]
    for text in samples:
        w = encode_one(text)
        f = fields(w)
        fmt = FORMAT[f["op"]]
        chunks = []
        for nm, hi, lo in field_layout(fmt):
            width = hi - lo + 1
            val = (w >> lo) & ((1 << width) - 1)
            chunks.append(f"{val:0{width}b}")
        print(f"  {text:16s} -> {w:#06x}  {' '.join(chunks)}   ({fmt}-type)")
    print()

    print("ROUND-TRIP PROOF -- disassemble every encodable instruction,")
    print("reassemble it, and require an identical word.")
    tested = failures = 0
    for name, op in OPCODES.items():
        fmt = FORMAT[op]
        if name == "NOP":
            cases = [0x0000]
        elif fmt == "R":
            cases = [(op << 12) | (rd << 9) | (ra << 6) | (rb << 3)
                     for rd in range(8) for ra in range(8) for rb in range(8)]
        elif name == "LDI":
            cases = [(op << 12) | (rd << 9) | (imm & 0x3F)
                     for rd in range(8) for imm in range(-32, 32)]
        elif name in ("LD", "ST"):
            cases = [(op << 12) | (rd << 9) | (ra << 6) | (imm & 0x3F)
                     for rd in range(8) for ra in range(8) for imm in (-32, -1, 0, 1, 31)]
        elif name in ("BEZ", "BNZ"):
            cases = [(op << 12) | (ra << 6) | (imm & 0x3F)
                     for ra in range(8) for imm in range(-31, 32)]
        else:                                     # J-type
            cases = [(op << 12) | addr for addr in (0, 1, 100, 2047, 4095)]
        for word in cases:
            text = disassemble(word)
            back = encode_one(text)
            tested += 1
            if back != word:
                failures += 1
                if failures <= 3:
                    print(f"    MISMATCH {word:#06x} -> '{text}' -> {back:#06x}")
    print(f"  {tested:,} encodings tested, {failures} mismatches")
    print()
    print("  a round-trip failure would mean two different instructions share")
    print("  an encoding, or one instruction has no unique text form --")
    print("  i.e. the ISA is AMBIGUOUS. Zero failures means the contract holds.")

    assert failures == 0
    assert disassemble(encode_one("ADD R3, R1, R2")) == "ADD R3, R1, R2"
    # the same bits mean different targets at different addresses:
    w = encode_one("BNZ R1, 0")
    assert disassemble(w, 0) != disassemble(w, 10)
    assert disassemble(0x0000) == "NOP"
    print()
    print("isa_lab: passed")
```

Expected output:

```
INSTRUCTION FORMATS -- every instruction is exactly 16 bits
  R-type  [op:4] [rd:3] [ra:3] [rb:3] [fn:3]           = 16 bits
  I-type  [op:4] [rd:3] [ra:3] [imm:6]                 = 16 bits
  J-type  [op:4] [addr:12]                             = 16 bits

THE INSTRUCTION SET
     op  mnemonic  fmt  operation
  0000       NOP    -  do nothing
  0001       ADD    R  rd = ra + rb
  0010       SUB    R  rd = ra - rb
  0011       AND    R  rd = ra & rb
  0100        OR    R  rd = ra | rb
  0101       XOR    R  rd = ra ^ rb
  0110       SHL    R  rd = ra << rb
  0111       SHR    R  rd = ra >> rb
  1000       SLT    R  rd = 1 if ra < rb else 0  (signed)
  1001       LDI    I  rd = sign_extend(imm)
  1010        LD    I  rd = mem[ra + imm]
  1011        ST    I  mem[ra + imm] = rd
  1100       BEZ    I  if ra == 0: PC += imm
  1101       BNZ    I  if ra != 0: PC += imm
  1110       JMP    J  PC = addr
  1111       JAL    J  R7 = PC + 1; PC = addr

ENCODING one instruction of each format, field by field
  ADD R3, R1, R2   -> 0x1650  0001 011 001 010 000   (R-type)
  LDI R5, -7       -> 0x9a39  1001 101 000 111001   (I-type)
  LD R2, R1, 4     -> 0xa444  1010 010 001 000100   (I-type)
  BNZ R4, 0        -> 0xd13f  1101 000 100 111111   (I-type)
  JMP 100          -> 0xe064  1110 000001100100   (J-type)

ROUND-TRIP PROOF -- disassemble every encodable instruction,
reassemble it, and require an identical word.
  6,267 encodings tested, 0 mismatches

  a round-trip failure would mean two different instructions share
  an encoding, or one instruction has no unique text form --
  i.e. the ISA is AMBIGUOUS. Zero failures means the contract holds.

isa_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Leaving the immediate's signedness unstated.** Signed or unsigned changes the meaning of half the encodings.
2. **Not fixing the branch reference point.** Before or after the PC increment? Pick one, write it down, make the emulator authoritative.
3. **A disassembler that ignores addresses.** It cannot print branch targets correctly, and it will disagree with your assembler.
4. **Spending every opcode.** Leave the `fn` escape hatch, or you cannot add anything later.
5. **Assuming your spec is unambiguous because you wrote it.** Round-trip it. The bug in section 6 survived writing, reading, and being used by three working implementations.
6. **Forgetting that flags are part of the contract.** Which instructions set which flags is as much a specification as the operation itself.

---

## 10. Check your understanding

1. **Why does a disassembler need to know an instruction's address, when an assembler apparently does not?**
   <details><summary>Answer</summary>
   The assembler <em>does</em> know — it tracks the address as it emits instructions, which is how it converts a label into a PC-relative offset.<br>
   A disassembler is handed raw bytes with no context. A branch immediate of −4 is meaningless without knowing where the instruction sits; at address 5 it means "go to 2", at address 100 it means "go to 97". <strong>Position-dependent encodings require position information to interpret.</strong> This is the same fact that makes relocation necessary when a linker moves code, and why `objdump` prints an address column.
   </details>

2. **PRIME-1 has no direct addressing. What does `LD R1, 0x1234` become?**
   <details><summary>Answer</summary>
   Two instructions: get the address into a register, then load with a zero displacement.<br>
   But `LDI` only carries a 6-bit immediate (−32..31), so `0x1234` does not fit either. You need to <strong>construct</strong> the constant — load the high part, shift left, OR in the low part — which takes several instructions.<br>
   <strong>This is a real cost of a small instruction word</strong>, and real RISC ISAs face it too: MIPS has <code>lui</code> (load upper immediate) precisely for this, and RISC-V has <code>lui</code>/<code>addi</code> pairs. Adding a <code>LUI</code>-style instruction to PRIME-1 would be a sound use of a spare <code>fn</code> code.
   </details>

3. **Why is `SLT` in the ISA when `SUB` already sets the N flag?**
   <details><summary>Answer</summary>
   Because a flag is not a value. <code>SUB</code> sets N, which a branch can test — but you cannot <em>store</em> N in a register or do arithmetic on it.<br>
   <code>SLT</code> produces a 0 or 1 <strong>in a register</strong>, which is what you need to implement <code>x = (a &lt; b)</code> in a language, or to combine several comparisons with AND/OR. This is why RISC-V has <code>slt</code> despite having branches: comparison-as-value and comparison-as-branch are different needs.<br>
   (Note also the correct signed test from [[how-computers-work/05-combinational/03-multipliers-and-comparators|module 22]] is $N \oplus V$, not $N$ alone — another reason to have a dedicated instruction that gets it right.)
   </details>

4. **What breaks if two instructions accidentally share an encoding?**
   <details><summary>Answer</summary>
   The decoder cannot tell them apart, so one of them becomes unreachable — the hardware will always pick whichever the control logic matches first. Programs using the shadowed instruction silently do the wrong thing.<br>
   Worse, the failure is <strong>invisible in testing</strong> unless you happen to exercise that instruction, and it cannot be fixed later without breaking every program already assembled. <strong>This is precisely what the round-trip test prevents</strong>, and it costs one function to write.
   </details>

---

## 11. Practice — independent task

**Task:** Extend the PRIME-1 ISA and prove your extension is sound.

- **(a)** Add `JR ra` (jump to the address in a register) using the R-type `fn` field. Choose an opcode to host the system group, define the encoding, and say what `fn` values you reserve.
- **(b)** Add `HLT` in the same group. Explain why a real halt instruction is better than the `JMP self` idiom.
- **(c)** Add `LUI rd, imm` (load upper immediate: `rd = imm << 6`) so large constants can be built in two instructions. Show how to construct `0x1234`.
- **(d)** Update `disassemble()` for all three, and extend the round-trip test to cover them. **It must still report zero mismatches.**
- **(e)** Write the call/return sequence: a `CALL` to a function, the function body, and a `RET` using your `JR`. Test it in the emulator with a function that doubles its argument.
- **(f)** Nested calls break with a single link register. Show the failure concretely (call A, which calls B, then return), then fix it with a stack: designate R6 as a stack pointer and write `PUSH`/`POP` sequences using `ST`/`LD`.
- **(g)** Document your extended ISA as a table in the format of section 4, including every detail from the "must be nailed down" list.

**Done when:** the round-trip test passes on your extended ISA, and a two-deep nested call returns correctly in the emulator.

<details><summary>Hint for (f), only if stuck</summary>
With one link register: <code>JAL A</code> puts the return address in R7. Inside A, <code>JAL B</code> <strong>overwrites R7</strong> with A's internal address. When B returns to A, A's own return address is gone — it returns to itself, and loops forever.<br>
The fix: at the top of any function that calls another, <strong>push R7 onto a stack</strong> (<code>SUB R6,R6,one</code> then <code>ST R7,R6,0</code>), and pop it before returning. That is the <strong>function prologue and epilogue</strong>, and you have just derived why calling conventions exist — see [[foundations/os/09-syscalls-interrupts-and-the-abi|os/syscalls and the ABI]].
</details>

---

## 12. Tradeoffs and limits

- **No interrupt support.** A real ISA needs a way to save the PC and flags on an external event, a vector table, and a return-from-interrupt instruction. That is a substantial extension and the reason [[foundations/os/index|os/]] is its own course.
- **No privilege levels.** Every instruction is available to every program, so there is no kernel/user split and no memory protection.
- **No multiply or divide.** Both are large ([[how-computers-work/05-combinational/03-multipliers-and-comparators|module 22]]) and better added as a separate unit once the base machine works.
- **Fixed 16-bit instructions waste space on simple operations.** `NOP` uses 16 bits to do nothing. Variable-length encoding would fix that and complicate everything else.

---

## Before moving on

- [ ] State the three instruction formats and show all three total 16 bits.
- [ ] List the six details that must be nailed down, and why each is a bug if left vague.
- [ ] Name PRIME-1's four addressing modes and one it omits, with the reason.
- [ ] Explain why a disassembler needs an address, and connect it to relocation.
- [ ] Explain the round-trip test and what a failure would mean.

**Recap:** An ISA is the exact contract between hardware and software. PRIME-1 uses three 16-bit formats — R, I and J — with 16 opcodes and three spare `fn` bits reserved for extension. The details that turn a sketch into a specification are signedness, the branch reference point, addressing granularity, R0's behaviour and flag rules. Ambiguity is proved absent by round-tripping every encodable instruction through a disassembler and back — a test that found a real inconsistency between this spec's assembler and disassembler, and whose fix explains why disassemblers take addresses and why relocation exists.

**Next:** [[how-computers-work/08-capstone/03-build-the-hardware|Module 30 — Build the Hardware]] derives the control unit from this table and points you at the four build tracks.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/08-capstone/01-design-the-cpu|Module 28]] — the decisions this encodes
- [[build-your-own-shit/17-your-own-cpu/index|Build Your Own CPU]] — the four implementations of this contract
- [[foundations/computer-architecture/03-instruction-sets|computer-architecture/instruction sets]] — RISC vs CISC, real ISAs
