# Module 20: Multiplexers and Decoders (Selection and Addressing)

**[Intermediate]** — Part VI begins. You stop building individual gates and start assembling them into blocks. These two are the most important: **selection** and **addressing** are what every memory and every datapath is made of.

## Before you start

- You know NAND is universal and can build any function from gates — [[how-computers-work/04-logic/04-universal-gates|module 18]].
- You can minimise a function and price it in transistors — [[how-computers-work/04-logic/03-karnaugh-maps|module 17]], [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].

**After this lesson you will be able to:**

1. Explain what a decoder does and why it is exactly the mechanism of memory addressing.
2. Build a multiplexer from a decoder, and extend a 1-bit MUX to a word-wide one.
3. Explain why a priority encoder exists and what breaks without one.
4. Explain how a MUX with constant inputs implements *any* function — and why that is what an FPGA is.

**Study route:** section 3 and 4 are the two primitives. Section 6 (MUX as lookup table) is the one with the biggest downstream consequence.

---

## 1. Why this exists (real-world motivation)

Module 18 proved you can build any function from NAND gates. True, and not yet useful — because "any function" as a flat truth table is hopeless at scale. A 32-bit adder has 64 inputs; its truth table has $2^{64}$ rows. You will not be drawing that K-map.

**Real digital systems are built from a small vocabulary of reusable blocks**, and two of them dominate everything that follows:

- **"Which of these many things do I want?"** — a **multiplexer**. Choosing between two ALU results, picking a register to read, selecting a branch target.
- **"Given this number, activate exactly one thing."** — a **decoder**. Every memory access, every instruction decode, every chip-select line.

**These are not conveniences.** A memory is fundamentally a decoder attached to storage cells; a CPU datapath is fundamentally multiplexers routing values between registers and the ALU. Learn these two and Parts VII and VIII become assembly rather than invention.

---

## 2. Terminology

| Term | Plain-English definition | Where you meet it |
| :--- | :--- | :--- |
| **Multiplexer (MUX)** | Selects one of $2^n$ inputs using $n$ select bits | Choosing an ALU operand |
| **Demultiplexer (DEMUX)** | Routes one input to one of $2^n$ outputs | Write-enable steering |
| **Decoder** | $n$ inputs → $2^n$ outputs, exactly one high | Memory addressing |
| **Encoder** | $2^n$ inputs → $n$ outputs, the inverse | Keypad scanning |
| **Priority encoder** | An encoder that resolves simultaneous inputs | Interrupt controllers |
| **One-hot** | A code where exactly one bit is high | Decoder output |
| **Select lines** | The control inputs choosing the path | — |
| **LUT** | Lookup table — a MUX with constants wired to its data inputs | FPGA logic cell |
| **Word-wide** | Operating on all bits of a value at once | 32-bit datapath MUX |

---

## 3. The decoder — addressing

**A decoder takes an $n$-bit number and activates exactly one of $2^n$ output lines.**

```
              ┌──────────┐──── out 0    (high when select = 00)
   select ────┤          │──── out 1    (high when select = 01)
   (2 bits)───┤ DECODER  │──── out 2    (high when select = 10)
              │          │──── out 3    (high when select = 11)
              └──────────┘

   select 10  ->  [0, 0, 1, 0]     exactly one line high: "one-hot"
```

Each output is one AND gate testing a specific combination of the select bits — output 2 is $S_1 \cdot \overline{S_0}$, and so on. **A decoder is just all $2^n$ minterms of the select variables, computed in parallel.**

> [!NOTE]
> **This is precisely how memory addressing works, and it is worth pausing on.**
>
> When a CPU puts address `0x1A4` on the bus, no search occurs. The address bits feed a decoder, and the decoder raises exactly one word line — the one belonging to that location. Every other location stays dormant.
>
> **That is why memory access is $O(1)$** — the "random access" in RAM. It is not that the hardware searches quickly; it is that a decoder activates the right row directly, in one gate delay. The array does not care whether you asked for address 0 or address 4 billion.
>
> This is the hardware fact underneath the constant-time array indexing in [[dsa/04-data-structures/01-arrays|dsa/arrays]]. The $O(1)$ you rely on in software is a decoder.

**The cost:** a decoder needs $2^n$ AND gates. A 32-bit address decoded flat would need $2^{32}$ gates — impossible. Real memories decode **hierarchically**: split the address into row and column parts and decode each separately, so $2^{16} + 2^{16}$ gates replace $2^{32}$. That structure is why memory has rows and columns at all, and it returns in [[how-computers-work/06-memory/03-memory-technology|module 24]].

---

## 4. The multiplexer — selection

**A multiplexer selects one of $2^n$ data inputs and passes it to a single output.**

The construction is a decoder plus a little logic: decode the select bits to one-hot, AND each data line with its own select line, then OR the results. Only the selected line can contribute; every other is ANDed with 0.

$$\text{OUT} = \sum_i (D_i \cdot \text{onehot}_i)$$

```
        D0 ──┐
        D1 ──┤        ┌─────┐
        D2 ──┤  MUX   │     ├──── OUT
        D3 ──┘        └──▲──┘
                         │
                    select (2 bits)
```

### Word-wide multiplexers

The MUX above handles **one bit**. A datapath selects between whole 32-bit values.

**A word-wide MUX is simply 32 copies of the 1-bit MUX, sharing the same select lines.** Bit 0 of each input feeds one MUX, bit 1 feeds another, and so on.

This has a direct cost consequence: **a 32-bit 2-to-1 MUX costs 32× a 1-bit one.** Multiplexers are everywhere in a datapath, and their area adds up fast — which is one reason architectures try to limit how many places a value can come from.

---

## 5. Encoders and priority

An **encoder** is the inverse of a decoder: $2^n$ inputs, and it outputs the binary index of whichever one is high.

**A plain encoder has a serious flaw: it assumes exactly one input is active.** Feed it two and the output is nonsense — typically the bitwise OR of the two indices, which is a third, wrong index.

That assumption fails constantly in practice. Several devices raise interrupts in the same cycle; multiple keys are pressed together.

**A priority encoder fixes it by defining a winner.** When several inputs are active, it reports the highest-priority one, and provides a separate **valid** output distinguishing "input 0 is active" from "nothing is active" — two cases a bare index cannot tell apart.

| Inputs | Index | Valid |
| :--- | ---: | ---: |
| `0000` | — | 0 |
| `1000` | 0 | 1 |
| `0010` | 2 | 1 |
| `1010` | 2 | 1 |
| `1111` | 3 | 1 |

**Interrupt controllers are priority encoders.** When the disk and the timer and the network card all interrupt at once, a priority encoder decides which the CPU services first. You will meet this again as interrupt handling in [[os/09-syscalls-interrupts-and-the-abi|os/syscalls and interrupts]].

---

## 6. A MUX is a lookup table — and that is what an FPGA is

Here is the result with the largest downstream consequence.

**Take a $2^n$-to-1 multiplexer. Wire the function's variables to the select lines. Wire constants — the truth table's output column — to the data inputs.**

The MUX now computes that function. Select bits pick the truth table row; the constant on that row's data pin is the answer.

For XOR, wire `0, 1, 1, 0` to the four data inputs of a 4-to-1 MUX:

| $A$ | $B$ | Selected input | Output |
| :-: | :-: | :-: | :-: |
| 0 | 0 | $D_0 = 0$ | 0 |
| 0 | 1 | $D_1 = 1$ | 1 |
| 1 | 0 | $D_2 = 1$ | 1 |
| 1 | 1 | $D_3 = 0$ | 0 |

The lab verifies this for **all 16 two-input functions**, with zero failures.

> [!NOTE]
> **This is the second universality result in the course, and it is the practical one.**
>
> [[how-computers-work/04-logic/04-universal-gates|Module 18]] showed NAND is universal — you can build anything, but you must *rewire* for each function. A MUX-as-LUT is universal too, and crucially **the wiring never changes.** Only the stored constants do.
>
> **That is exactly what an FPGA is.** An FPGA is a large array of small LUTs — typically 4- or 6-input — plus programmable interconnect. "Programming" it means writing constants into the LUTs and configuring the routing. No silicon is modified; you are filling in truth tables.
>
> It is also the deep reason a general-purpose computer is possible at all: **you can build one fixed circuit whose behaviour is determined by stored data rather than by its structure.** Hold that thought — it is the same idea as a stored program, and it returns in Part VIII.

---

## 7. Predict before reading on

A 3-input LUT can implement any 3-input function. FPGAs commonly use **6-input** LUTs.

**How many bits of configuration does a 6-input LUT need, and how many distinct functions can it implement?**

<details><summary>Check your answer</summary>

A 6-input function has $2^6 = 64$ truth-table rows, so the LUT needs **64 configuration bits** — a 64-to-1 MUX with 64 stored constants.

The number of distinct functions it can implement is the number of ways to fill those bits: $2^{64} \approx 1.8 \times 10^{19}$.

**One small block, wired once, covering eighteen quintillion functions.** And a modern FPGA contains hundreds of thousands of them.

The tradeoff is why 6 and not 16: LUT cost grows as $2^n$, so a 16-input LUT would need 65,536 bits. Six is an empirical sweet spot — big enough to absorb most logic clusters, small enough to stay cheap.
</details>

---

## 8. Worked example — runnable

Save as `mux_lab.py` and run `python3 mux_lab.py`.

```python
"""Selection and addressing: the two operations every datapath is made of."""
from itertools import product

def decoder(select_bits):
    """n select bits -> 2^n outputs, exactly one HIGH. This is ADDRESSING."""
    n = len(select_bits)
    index = 0
    for b in select_bits:
        index = (index << 1) | b
    return [1 if i == index else 0 for i in range(2 ** n)]

def multiplexer(data_inputs, select_bits):
    """2^n data inputs -> 1 output, chosen by the select bits. This is SELECTION."""
    one_hot = decoder(select_bits)
    # AND each data line with its select line, then OR the results
    return sum(d & s for d, s in zip(data_inputs, one_hot))

def mux_word(word_inputs, select_bits, width=8):
    """Select between multi-bit WORDS, not single bits.

    A word MUX is just `width` copies of the 1-bit MUX sharing select lines --
    which is why a 32-bit datapath multiplexer costs 32x a 1-bit one."""
    result = 0
    for bit in range(width):
        slice_of_bit = [(w >> bit) & 1 for w in word_inputs]
        result |= multiplexer(slice_of_bit, select_bits) << bit
    return result

def demultiplexer(data_in, select_bits):
    """1 input -> one of 2^n outputs; the rest are 0. The inverse of a MUX."""
    return [data_in & s for s in decoder(select_bits)]

def priority_encoder(inputs):
    """Return (index of highest-priority active input, valid flag).

    Plain encoders break if two inputs are high at once; a priority encoder
    resolves the tie by always reporting the highest-numbered active line."""
    for i in range(len(inputs) - 1, -1, -1):
        if inputs[i]:
            return i, 1
    return 0, 0          # nothing active -> index meaningless, valid = 0

def mux_as_lookup_table(truth_table):
    """A 2^n-to-1 MUX with constants on its data inputs computes ANY function.

    Wire the truth table's output column to the data inputs and the function's
    variables to the select lines. This is exactly how an FPGA LUT works."""
    def f(*inputs):
        return multiplexer(truth_table, list(inputs))
    return f

if __name__ == "__main__":
    print("DECODER -- n bits in, one-hot out (this is how memory is addressed):")
    for bits in product([0, 1], repeat=2):
        out = decoder(list(bits))
        print(f"  select {''.join(map(str, bits))} -> {out}   (line {out.index(1)} enabled)")
    print()

    print("MULTIPLEXER -- select one of four data lines:")
    data = [1, 0, 1, 1]
    print(f"  data inputs = {data}")
    for bits in product([0, 1], repeat=2):
        out = multiplexer(data, list(bits))
        idx = decoder(list(bits)).index(1)
        print(f"  select {''.join(map(str, bits))} -> {out}   (passing data[{idx}])")
    print()

    print("WORD MUX -- the same circuit, replicated across every bit:")
    words = [9, 8, 7, 6]
    print(f"  word inputs = {words}")
    for bits in product([0, 1], repeat=2):
        idx = decoder(list(bits)).index(1)
        print(f"  select {''.join(map(str, bits))}"
              f" -> {mux_word(words, list(bits))}   (passing word[{idx}])")
    print("  a 32-bit datapath MUX is 32 copies of the 1-bit MUX, shared selects")
    print()

    print("DEMULTIPLEXER -- route one input to one of four outputs:")
    for bits in product([0, 1], repeat=2):
        print(f"  data=1, select {''.join(map(str, bits))}"
              f" -> {demultiplexer(1, list(bits))}")
    print()

    print("PRIORITY ENCODER -- resolves simultaneous requests:")
    for inputs in [[0,0,0,0], [1,0,0,0], [0,0,1,0], [1,0,1,0], [1,1,1,1]]:
        idx, valid = priority_encoder(inputs)
        note = f"index {idx}" if valid else "no request"
        print(f"  inputs {inputs} -> {note}, valid={valid}")
    print()

    # The universality result: a MUX is a lookup table
    print("A MUX with constants on its data inputs computes ANY function.")
    print("Building XOR from a 4-to-1 MUX (truth table 0,1,1,0 on the data pins):")
    xor_lut = mux_as_lookup_table([0, 1, 1, 0])
    for a, b in product([0, 1], repeat=2):
        got, want = xor_lut(a, b), a ^ b
        print(f"  A={a} B={b} -> {got}   (XOR = {want})")
        assert got == want

    print()
    print("verifying MUX-as-LUT for ALL 16 two-input functions:")
    failures = 0
    for f in range(16):
        table = [(f >> i) & 1 for i in range(4)]
        lut = mux_as_lookup_table(table)
        for row, (a, b) in enumerate(product([0, 1], repeat=2)):
            if lut(a, b) != table[row]:
                failures += 1
    print(f"  16 functions x 4 rows checked, {failures} failures")
    print("  -> one MUX + constants = any logic function (this is an FPGA LUT)")

    assert failures == 0
    assert decoder([1, 0]) == [0, 0, 1, 0]
    assert multiplexer([1, 0, 1, 1], [1, 0]) == 1        # 1-bit primitive
    assert mux_word([9, 8, 7, 6], [1, 1]) == 6           # word-wide selection
    assert mux_word([0xAA, 0x55], [1]) == 0x55
    assert priority_encoder([1, 0, 1, 0]) == (2, 1)
    assert priority_encoder([0, 0, 0, 0])[1] == 0
    print()
    print("mux_lab: passed")
```

Expected output:

```
DECODER -- n bits in, one-hot out (this is how memory is addressed):
  select 00 -> [1, 0, 0, 0]   (line 0 enabled)
  select 01 -> [0, 1, 0, 0]   (line 1 enabled)
  select 10 -> [0, 0, 1, 0]   (line 2 enabled)
  select 11 -> [0, 0, 0, 1]   (line 3 enabled)

MULTIPLEXER -- select one of four data lines:
  data inputs = [1, 0, 1, 1]
  select 00 -> 1   (passing data[0])
  select 01 -> 0   (passing data[1])
  select 10 -> 1   (passing data[2])
  select 11 -> 1   (passing data[3])

WORD MUX -- the same circuit, replicated across every bit:
  word inputs = [9, 8, 7, 6]
  select 00 -> 9   (passing word[0])
  select 01 -> 8   (passing word[1])
  select 10 -> 7   (passing word[2])
  select 11 -> 6   (passing word[3])
  a 32-bit datapath MUX is 32 copies of the 1-bit MUX, shared selects

DEMULTIPLEXER -- route one input to one of four outputs:
  data=1, select 00 -> [1, 0, 0, 0]
  data=1, select 01 -> [0, 1, 0, 0]
  data=1, select 10 -> [0, 0, 1, 0]
  data=1, select 11 -> [0, 0, 0, 1]

PRIORITY ENCODER -- resolves simultaneous requests:
  inputs [0, 0, 0, 0] -> no request, valid=0
  inputs [1, 0, 0, 0] -> index 0, valid=1
  inputs [0, 0, 1, 0] -> index 2, valid=1
  inputs [1, 0, 1, 0] -> index 2, valid=1
  inputs [1, 1, 1, 1] -> index 3, valid=1

A MUX with constants on its data inputs computes ANY function.
Building XOR from a 4-to-1 MUX (truth table 0,1,1,0 on the data pins):
  A=0 B=0 -> 0   (XOR = 0)
  A=0 B=1 -> 1   (XOR = 1)
  A=1 B=0 -> 1   (XOR = 1)
  A=1 B=1 -> 0   (XOR = 0)

verifying MUX-as-LUT for ALL 16 two-input functions:
  16 functions x 4 rows checked, 0 failures
  -> one MUX + constants = any logic function (this is an FPGA LUT)

mux_lab: passed
```

Notice that `multiplexer()` is built *from* `decoder()` rather than independently — selection is addressing plus gating. And `mux_word()` is a loop over `multiplexer()`, which is literally what the hardware does: replicate the 1-bit circuit across every bit position.

---

## 9. Common pitfalls and traps

1. **Confusing a decoder with a demultiplexer.** A decoder takes only select bits. A DEMUX also takes a data input and routes it. A DEMUX is a decoder whose outputs are ANDed with the data line.
2. **Using a plain encoder where inputs can collide.** Two simultaneous inputs produce a wrong index, not an error. Use a priority encoder.
3. **Forgetting the valid output.** Without it, "input 0 active" and "nothing active" both read as index 0.
4. **Assuming a word MUX costs the same as a bit MUX.** It costs $width$ times as much, and datapaths are full of them.
5. **Trying to decode a wide address flatly.** $2^{32}$ AND gates is not a design. Decode hierarchically.
6. **Thinking LUT-based logic is free.** A 6-input LUT costs 64 configuration bits plus a 64-to-1 MUX, whether your function needs two inputs or six. FPGAs trade area for flexibility.

---

## 10. Check your understanding

1. **Build an 8-to-1 MUX from 2-to-1 MUXes. How many do you need, and how deep is the tree?**
   <details><summary>Answer</summary>
   <strong>Seven.</strong> Four in the first rank pair up the eight inputs (selected by $S_0$), two in the second rank (selected by $S_1$), one in the third (selected by $S_2$). In general a $2^n$-to-1 MUX needs $2^n - 1$ two-input MUXes.<br>
   The tree is <strong>3 levels deep</strong>, so propagation delay is 3 MUX delays rather than 1. This is the recurring structural tradeoff: a tree of small blocks costs less area than one huge block but adds delay proportional to $\log_2$ of the input count.
   </details>

2. **Why does memory addressing use a decoder rather than comparing the address against each location?**
   <details><summary>Answer</summary>
   Comparing would need one comparator per location and some way to arbitrate — enormous area, and the delay would grow with capacity.<br>
   A decoder computes all $2^n$ minterms in parallel, so exactly one word line rises after a fixed, capacity-independent delay. <strong>That constant delay is what "random access" means</strong> — address 0 and address 4 billion take the same time. It is the hardware basis of $O(1)$ array indexing.
   </details>

3. **A 4-to-1 MUX has select bits $S_1S_0$ and data inputs wired to $A$, $\overline{A}$, 0, 1. What function of $S_1$, $S_0$, $A$ does it compute?**
   <details><summary>Answer</summary>
   It selects: $S_1S_0 = 00 \to A$; $01 \to \overline{A}$; $10 \to 0$; $11 \to 1$.<br>
   This is a small <strong>programmable function unit</strong> — the same circuit computes identity, inversion, constant-zero or constant-one depending on control bits. Feeding a MUX with <em>variables</em> as well as constants is how you build a compact configurable block, and it is exactly the trick an ALU uses in [[how-computers-work/05-combinational/04-the-alu|module 23]] to make one circuit perform many operations.
   </details>

4. **Why is a MUX-based LUT the basis of FPGAs rather than a NAND array?**
   <details><summary>Answer</summary>
   Both are universal, but they differ in <em>what changes</em> between functions. A NAND implementation needs different <strong>wiring</strong> for each function, and wiring cannot be altered after manufacture.<br>
   A LUT keeps the wiring fixed and changes only <strong>stored constants</strong>, which are trivially rewritable from memory cells. That makes the same silicon reconfigurable in the field, in milliseconds, arbitrarily often.<br>
   The deeper point: moving the function from the structure into the data is what makes reconfigurability — and, in Part VIII, stored-program computing — possible at all.
   </details>

---

## 11. Practice — independent task

**Task:** Design the address decoding for a small system with a 16-bit address bus and three devices:

- RAM: 32 KB at addresses `0x0000`–`0x7FFF`
- ROM: 16 KB at `0x8000`–`0xBFFF`
- I/O registers: 256 bytes at `0xFF00`–`0xFFFF`

- **(a)** For each device, work out which address bits must be examined and which are "don't care". Express each chip-select as a Boolean expression of the address bits.
- **(b)** How many gate inputs does each chip-select need? Which device is cheapest to decode, and why?
- **(c)** Addresses `0xC000`–`0xFEFF` are unmapped. What should a read from there return, and what are two reasonable hardware behaviours?
- **(d)** Implement `address_decode(addr)` returning which device is selected (or `None`), and verify that no address ever selects two devices — the hardware equivalent of a bus conflict.
- **(e)** Suppose the I/O block were moved to `0xFF80`–`0xFFFF` (128 bytes). Does decoding get cheaper or more expensive? State the general rule connecting a region's size and alignment to its decoding cost.
- **(f)** Extend `mux_lab.py` with your decoder and add an assertion that every one of the 65,536 addresses selects at most one device.

**Done when:** your exhaustive check passes over all 65,536 addresses, and you can state the rule from (e) in one sentence.

<details><summary>Hint for (e), only if stuck</summary>
A region of size $2^k$ that is <em>aligned</em> to a $2^k$ boundary needs only the top $16-k$ address bits examined — the low $k$ bits are entirely don't-care.<br>
So <strong>larger, power-of-two-sized, properly aligned regions are cheaper to decode.</strong> This is exactly why memory-mapped regions in real systems are always power-of-two sized and aligned, and why an awkward region like "3 KB starting at 0x1234" would need far more gates than its size suggests.
</details>

---

## 12. Tradeoffs and limits

- **Flat decoding does not scale.** Beyond about 10 address bits, hierarchical or two-stage decoding is mandatory. Real DRAM splits addresses into row and column strobes for precisely this reason.
- **MUX delay grows with input count.** A tree of 2-to-1 MUXes has $\log_2 N$ levels; a flat $N$-to-1 has huge fan-in. Both cost delay, differently.
- **LUTs waste area on simple functions.** A 6-input LUT holding a 2-input AND still costs 64 configuration bits. FPGAs are typically 10–20× less area-efficient than an ASIC implementing the same logic, and slower — the price of reconfigurability.
- **These blocks are purely combinational.** Outputs depend only on current inputs; nothing here remembers anything. That limitation is absolute until Part VII.

---

## Before moving on

- [ ] Explain what a decoder does and why it makes memory access constant-time.
- [ ] Build a MUX from a decoder, and explain the cost of going word-wide.
- [ ] Explain why priority encoders exist and what the valid output is for.
- [ ] Explain how a MUX plus constants implements any function, and why that is an FPGA.
- [ ] Explain why hierarchical decoding is necessary for wide addresses.

**Recap:** A decoder turns an $n$-bit number into one-hot activation of $2^n$ lines — the mechanism behind constant-time memory addressing. A multiplexer is a decoder plus gating, selecting one of many inputs; word-wide versions replicate it per bit. Priority encoders resolve simultaneous requests and report validity separately. A MUX with constants on its data inputs computes any function of its select bits, making it a lookup table — universal like NAND, but reconfigurable by changing data rather than wiring, which is what an FPGA is.

**Next:** [[how-computers-work/05-combinational/02-adders|Module 21 — Adders]] builds arithmetic from pure logic. You will find that the carry chain — not the addition itself — is what sets a processor's clock speed.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/04-logic/04-universal-gates|Module 18]] — the other universality result
- [[how-computers-work/06-memory/03-memory-technology|Module 24]] — where hierarchical decoding returns
- [[dsa/04-data-structures/01-arrays|dsa/arrays]] — the O(1) indexing this module explains
- [[os/09-syscalls-interrupts-and-the-abi|os/syscalls and interrupts]] — priority encoders as interrupt controllers
