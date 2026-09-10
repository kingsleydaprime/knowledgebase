# Module 22: Multipliers and Comparators (Beyond Addition)

**[Intermediate → Advanced]** — Addition was the easy one. Multiplication is where the "just add more gates" answer stops working, and comparison turns out to be a subtraction you throw away.

## Before you start

- You can build a ripple-carry and a carry-lookahead adder, and trace a multi-bit addition — [[how-computers-work/05-combinational/02-adders|module 21]].
- You know a barrel shifter shifts by any amount in $\log_2 n$ stages — [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]].
- You know gate delays accumulate along the critical path — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].

**After this lesson you will be able to:**

1. Explain why binary multiplication needs no times table, and trace it by hand.
2. Build a multiplier from partial products and adders, and say why it costs so much more than an adder.
3. Explain carry-save addition and why it breaks the carry-chain bottleneck.
4. Build equality and magnitude comparators, and explain why comparison reuses the adder.

**Study route:** section 3 is the hand trace — do it on paper. Section 5 (carry-save) is the clever idea that makes fast multipliers possible.

---

## 1. Why this exists (real-world motivation)

[[how-computers-work/05-combinational/02-adders|Module 21]] built an adder and showed it scales to any width by repetition. **Multiplication does not scale that way.**

Two 8-bit numbers multiply to a 16-bit result. Two 64-bit numbers multiply to 128 bits. The output is twice the input width, and — worse — every input bit can influence every output bit. There is no "one full adder per position" decomposition that just repeats.

**Yet multiplication is everywhere**: array indexing computes `base + index × size`; graphics is matrix arithmetic; neural networks are multiply-accumulate in enormous quantity; even a hash function is mostly multiplies.

And **comparison** is quietly just as fundamental. Every `if`, every loop condition, every branch depends on comparing two values. A processor that cannot compare cannot make a decision.

**This module builds both, and finds they are closer to the adder than they look.**

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Partial product** | One row of long multiplication: A shifted, or zero |
| **Array multiplier** | Partial products summed by a grid of adders |
| **Carry-save adder (CSA)** | Adds three numbers into two, with no carry propagation |
| **3:2 compressor** | Another name for a CSA — three inputs, two outputs |
| **Wallace / Dadda tree** | A tree of CSAs reducing many partial products quickly |
| **Equality comparator** | Tests $A = B$ |
| **Magnitude comparator** | Tests $A > B$, $A = B$, $A < B$ |
| **Multiply-accumulate (MAC)** | $a \times b + c$ as a single operation |

---

## 3. Binary multiplication needs no times table

Long multiplication in decimal requires memorising a table: $7 \times 8 = 56$. **Binary requires nothing**, and this is the key simplification.

A binary digit is 0 or 1. So each partial product is either **A shifted left**, or **nothing at all**. There is no table because there are only two cases.

Take $13 \times 11$ in 4 bits:

```
      1101   (13)
    x 1011   (11)
    --------
    00001101   <- B bit 0 = 1:  A << 0
    00011010   <- B bit 1 = 1:  A << 1
    00000000   <- B bit 2 = 0:  contribute nothing
    01101000   <- B bit 3 = 1:  A << 3
    --------
    10001111   (143)   = 13 x 11  ✓
```

**Look at what each row required.** Testing one bit of B (a wire), shifting A (just wiring — a shift by a constant amount is *free* in hardware, it is which wire connects where), and then either passing it through or zeroing it (one AND gate per bit).

$$\text{partial product}_i = A \cdot B_i \quad\text{shifted left by } i$$

Since $B_i$ is a single bit, "multiply A by $B_i$" is **an AND gate on each bit of A.**

> [!NOTE]
> **This is the answer to "how does hardware multiply?"** — it does not. It **shifts and adds**, and shifting is free because it is only a wiring offset.
>
> A multiplier is: a grid of AND gates producing the partial products, and a pile of adders summing them. **No new kind of component appears** — it is the same NAND-derived gates from [[how-computers-work/04-logic/04-universal-gates|module 18]], arranged differently.
>
> The expense is not complexity. It is **quantity**: an 8×8 multiplier needs 64 AND gates and roughly 56 full adders. A 64×64 multiplier needs 4096 AND gates and about 4000 full adders — which is why a multiplier occupies far more area than an adder, and why early processors omitted it entirely and multiplied in software.

---

## 4. The array multiplier, and why it is slow

The obvious construction sums the partial products with ordinary adders, one row at a time. Each addition must wait for the previous, and each addition is itself a ripple-carry that must propagate.

**The result is a critical path roughly proportional to $2n$ adder stages:**

| Width | Array multiplier | Plain adder |
| ---: | ---: | ---: |
| 8 | 560 ps | 160 ps |
| 16 | 1200 ps | 200 ps |
| 32 | 2480 ps | 240 ps |
| 64 | 5040 ps | 280 ps |

**At 64 bits, a naive multiplier is 18× slower than an adder.** At 5 ns it would cap the clock below 200 MHz.

This is why multiplication is never allowed to share the adder's timing budget. **Multipliers get their own pipeline stages** — typically 3 to 5 cycles of latency, pipelined so a new multiply can start every cycle even though each takes several to finish.

---

## 5. Carry-save addition — the trick that fixes it

The bottleneck is the same villain as in module 21: **the carry chain**. Every partial-product addition pays a full carry propagation, and there are $n$ of them.

**The insight: when adding many numbers, do not propagate carries until the very end.**

A **carry-save adder** takes *three* numbers and produces *two* whose sum equals the original three:

$$\text{sum} = X \oplus Y \oplus Z \qquad\qquad \text{carry} = \big((X{\cdot}Y) + (Y{\cdot}Z) + (X{\cdot}Z)\big) \ll 1$$

**Every bit position computes independently.** No bit waits for its neighbour. **The delay is one full-adder delay regardless of width** — a 64-bit CSA is exactly as fast as a 4-bit one.

```
   Ordinary addition of 3 numbers:
     X + Y  -> carry propagates the full width   (slow)
     result + Z -> carry propagates again        (slow)

   Carry-save:
     X, Y, Z -> sum, carry     ONE gate delay, any width
     ...reduce more numbers the same way...
     finally: sum + carry      ONE real carry propagation, at the end
```

**A Wallace tree** applies this repeatedly: $n$ partial products are compressed 3-into-2 at each level, reducing the count by a factor of 1.5 per level, until only two remain. Those two go into a single fast carry-lookahead adder.

Since each level costs one full-adder delay and the count falls geometrically, the depth is $O(\log n)$:

| Width | Array | Wallace tree | Speedup |
| ---: | ---: | ---: | ---: |
| 8 | 560 ps | 400 ps | 1.4× |
| 16 | 1200 ps | 440 ps | 2.7× |
| 32 | 2480 ps | 520 ps | 4.8× |
| 64 | 5040 ps | 600 ps | **8.4×** |

> [!NOTE]
> **This is the same move as carry-lookahead, applied one level up.**
>
> Module 21 converted the sequential carry chain within *one* addition into a logarithmic tree. Carry-save converts the sequential chain of *many additions* into a logarithmic tree.
>
> **The pattern — "find the sequential dependency, pay area to make it a tree" — has now appeared three times**: carry-lookahead, the barrel shifter, and Wallace trees. It is the single most reusable idea in digital design, and it is the same idea as parallel prefix / scan algorithms in software.

---

## 6. Comparators

### Equality — cheap

$A = B$ exactly when every bit pair matches. **XNOR** outputs 1 when two bits are equal, so:

$$A = B \iff \prod_{i} \overline{(A_i \oplus B_i)}$$

That is $n$ XNOR gates feeding one $n$-input AND. **For 8 bits: 8 XNORs and 7 two-input ANDs.** Cheap, and the delay is $\log n$ if the AND is a tree.

### Magnitude — reuse the adder

$A > B$ is harder, but you already have the machinery. **Scan from the most significant bit down; the first position where the bits differ decides the answer.** If $A_i = 1$ and $B_i = 0$ there, then $A > B$.

That is a ripple from the MSB — and a ripple is exactly what we have been avoiding. **So real hardware does not build a dedicated magnitude comparator.** It computes $A - B$ in the existing adder and reads the flags:

| Test | Unsigned | Signed |
| :--- | :--- | :--- |
| $A = B$ | Z | Z |
| $A \neq B$ | $\overline{Z}$ | $\overline{Z}$ |
| $A < B$ | $\overline{C}$ (borrow) | $N \oplus V$ |
| $A \geq B$ | C | $\overline{N \oplus V}$ |

**A comparison is a subtraction whose difference you discard.** This is why `cmp` exists as an instruction that sets flags without writing a result, and why [[how-computers-work/05-combinational/04-the-alu|module 23]]'s SLT is implemented as a subtract.

**And it explains the signed/unsigned trap.** The same subtraction serves both, but which flags you read differs — $\overline{C}$ for unsigned, $N \oplus V$ for signed. Read the wrong pair and comparisons silently go wrong for half the input range. That is the hardware root of a whole family of C bugs.

---

## 7. Predict before reading on

An 8-bit multiplier needs 64 AND gates and about 56 full adders.

**How does that scale to 32 bits, and what does it imply about where multipliers appear?**

<details><summary>Check your answer</summary>

Partial products scale as $n^2$: a 32×32 multiplier needs **1024 AND gates** and roughly **992 full adders** — about **6000 gates**, versus roughly 200 for a 32-bit adder. **Thirty times the area.**

**Implications, all of which show up in real hardware:**

1. **Early CPUs had no multiplier.** The 6502 and original ARM multiplied in software with shift-and-add loops — slow, but free in area.
2. **Multipliers are shared and pipelined**, not replicated. A core typically has one or two, not one per execution slot.
3. **GPUs and AI accelerators are mostly multipliers.** Their workload is multiply-accumulate, so they spend area on many small multipliers rather than one wide one — and reduced-precision formats (bf16, int8) are popular precisely because area scales as $n^2$. Halving the width quarters the multiplier.

**That $n^2$ is why low-precision AI arithmetic took off**: going from 32-bit to 8-bit multipliers is a 16× area saving, so you fit 16× as many.
</details>

---

## 8. Worked example — runnable

Save as `multiply_lab.py` and run `python3 multiply_lab.py`.

```python
"""Multiplication and comparison: the other two arithmetic blocks."""
import math

GATE_DELAY_PS = 20
WIDTH = 8
MASK = (1 << WIDTH) - 1

def partial_products(a, b, width=WIDTH):
    """Long multiplication in binary: each 1-bit of B shifts A left.

    Because a binary digit is only 0 or 1, there is no multiplication
    table -- each partial product is either A shifted, or nothing."""
    rows = []
    for i in range(width):
        rows.append((a << i) if (b >> i) & 1 else 0)
    return rows

def shift_and_add_multiply(a, b, width=WIDTH):
    """Sum the partial products. This IS binary multiplication."""
    return sum(partial_products(a, b, width))

def trace_multiply(a, b, width=4):
    """Show long multiplication the way you would do it on paper."""
    print(f"    {a:0{width}b}  ({a})")
    print(f"  x {b:0{width}b}  ({b})")
    print("  " + "-" * (width + 8))
    for i in range(width):
        bit = (b >> i) & 1
        row = (a << i) if bit else 0
        note = f"A << {i}" if bit else "zero (B bit is 0)"
        print(f"    {row:0{2*width}b}   <- B bit {i} = {bit}: {note}")
    total = shift_and_add_multiply(a, b, width)
    print("  " + "-" * (width + 8))
    print(f"    {total:0{2*width}b}  ({total})   = {a} x {b}")
    return total

def carry_save_add(x, y, z):
    """Add THREE numbers producing two, with no carry propagation.

    This is the trick behind fast multipliers: a full adder used as a
    3:2 compressor. Every bit position works independently, so the
    delay is ONE gate level regardless of width."""
    partial_sum = x ^ y ^ z                       # bitwise, no carries
    carry = ((x & y) | (y & z) | (x & z)) << 1    # carries shifted left
    return partial_sum, carry

def array_multiplier_delay_ps(width):
    """Critical path of a simple array multiplier: roughly 2n adder stages."""
    return (2 * width - 2) * 2 * GATE_DELAY_PS

def wallace_delay_ps(width):
    """Wallace tree: log_1.5(n) compression levels, then one fast adder."""
    levels = math.ceil(math.log(width, 1.5))
    return (levels * 2 + 8) * GATE_DELAY_PS

def equality_comparator(a, b, width=WIDTH):
    """A == B: XNOR each bit pair, AND the results. n XNOR + (n-1) AND."""
    for i in range(width):
        if (((a >> i) & 1) ^ ((b >> i) & 1)):     # XOR = 1 means bits differ
            return 0
    return 1

def magnitude_comparator(a, b, width=WIDTH):
    """A > B, unsigned: scan from the MSB, first difference decides.

    Returns (greater, equal, less)."""
    for i in range(width - 1, -1, -1):
        bit_a, bit_b = (a >> i) & 1, (b >> i) & 1
        if bit_a and not bit_b:
            return 1, 0, 0
        if bit_b and not bit_a:
            return 0, 0, 1
    return 0, 1, 0

if __name__ == "__main__":
    print("MULTIPLICATION is shift-and-add -- long multiplication in binary:")
    trace_multiply(13, 11, 4)
    print()
    print("  in decimal you need a times table; in binary you do NOT,")
    print("  because each digit is 0 or 1 -- so every partial product is")
    print("  just A shifted, or nothing at all. That is why multiplication")
    print("  in hardware is only adders and wires.")
    print()

    print("verifying the 8x8 multiplier against Python:")
    failures = sum(1 for a in range(256) for b in range(256)
                   if shift_and_add_multiply(a, b) != a * b)
    print(f"  all 65,536 input pairs checked, {failures} failures")
    assert failures == 0
    print()

    print("CARRY-SAVE ADDITION -- add 3 numbers in ONE gate delay:")
    for x, y, z in [(0b1011, 0b0110, 0b1101), (255, 255, 255)]:
        s, c = carry_save_add(x, y, z)
        print(f"  {x} + {y} + {z} = {x+y+z}")
        print(f"    -> partial sum {s} + carry {c} = {s + c}  (no carry chain used)")
        assert s + c == x + y + z
    print("  the carry chain is paid ONCE at the very end, not per addition")
    print()

    print("WHY MULTIPLICATION IS SLOWER THAN ADDITION:")
    print(f"  {'width':>6s} {'array mult':>12s} {'Wallace tree':>14s} {'adder':>10s}")
    for w in (8, 16, 32, 64):
        print(f"  {w:6d} {array_multiplier_delay_ps(w):10d} ps"
              f" {wallace_delay_ps(w):12d} ps {(2+2*math.ceil(math.log2(w)))*GATE_DELAY_PS:8d} ps")
    print("  -> multipliers get their own pipeline stages; they cannot")
    print("     share the adder's clock budget")
    print()

    print("COMPARATORS:")
    print(f"  {'A':>4s} {'B':>4s}  {'A==B':>5s} {'A>B':>4s} {'A=B':>4s} {'A<B':>4s}")
    for a, b in [(200, 200), (200, 100), (100, 200), (0, 0), (255, 254)]:
        eq = equality_comparator(a, b)
        g, e, l = magnitude_comparator(a, b)
        print(f"  {a:4d} {b:4d}  {eq:5d} {g:4d} {e:4d} {l:4d}")

    fails = sum(1 for a in range(256) for b in range(256)
                if (equality_comparator(a, b) != (1 if a == b else 0)
                    or magnitude_comparator(a, b)[0] != (1 if a > b else 0)))
    print(f"  exhaustive check over 65,536 pairs: {fails} failures")
    assert fails == 0
    print()
    print(f"  equality costs {WIDTH} XNOR + {WIDTH-1} AND gates")
    print(f"  magnitude is a subtraction you throw away (module 23's SLT)")

    print()
    print("multiply_lab: passed")
```

Expected output:

```
MULTIPLICATION is shift-and-add -- long multiplication in binary:
    1101  (13)
  x 1011  (11)
  ------------
    00001101   <- B bit 0 = 1: A << 0
    00011010   <- B bit 1 = 1: A << 1
    00000000   <- B bit 2 = 0: zero (B bit is 0)
    01101000   <- B bit 3 = 1: A << 3
  ------------
    10001111  (143)   = 13 x 11

  in decimal you need a times table; in binary you do NOT,
  because each digit is 0 or 1 -- so every partial product is
  just A shifted, or nothing at all. That is why multiplication
  in hardware is only adders and wires.

verifying the 8x8 multiplier against Python:
  all 65,536 input pairs checked, 0 failures

CARRY-SAVE ADDITION -- add 3 numbers in ONE gate delay:
  11 + 6 + 13 = 30
    -> partial sum 0 + carry 30 = 30  (no carry chain used)
  255 + 255 + 255 = 765
    -> partial sum 255 + carry 510 = 765  (no carry chain used)
  the carry chain is paid ONCE at the very end, not per addition

WHY MULTIPLICATION IS SLOWER THAN ADDITION:
   width   array mult   Wallace tree      adder
       8        560 ps          400 ps      160 ps
      16       1200 ps          440 ps      200 ps
      32       2480 ps          520 ps      240 ps
      64       5040 ps          600 ps      280 ps
  -> multipliers get their own pipeline stages; they cannot
     share the adder's clock budget

COMPARATORS:
     A    B   A==B  A>B  A=B  A<B
   200  200      1    0    1    0
   200  100      0    1    0    0
   100  200      0    0    0    1
     0    0      1    0    1    0
   255  254      0    1    0    0
  exhaustive check over 65,536 pairs: 0 failures

  equality costs 8 XNOR + 7 AND gates
  magnitude is a subtraction you throw away (module 23's SLT)

multiply_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Thinking hardware multiplies like a lookup table.** It shifts and adds. A 64-bit times table would have $2^{128}$ entries.
2. **Forgetting the result is double-width.** $n \times n$ bits gives $2n$ bits. Truncating silently is a classic overflow bug.
3. **Assuming shifting costs gates.** A shift by a *constant* is free — it is just which wire goes where. Only *variable* shifts need a barrel shifter.
4. **Treating multiply as one-cycle.** It is typically 3–5 pipelined cycles. Code that assumes multiply is as cheap as add mis-predicts performance.
5. **Building a dedicated magnitude comparator.** Subtract in the existing adder and read the flags.
6. **Reading the wrong flags for signed comparison.** Unsigned uses C; signed uses $N \oplus V$. Mixing them is a real and common bug.

---

## 10. Check your understanding

1. **Why is multiplying by 8 far cheaper than multiplying by 7?**
   <details><summary>Answer</summary>
   $\times 8$ is a left shift by 3 — <strong>free in hardware</strong>, just wiring, and one instruction in software.<br>
   $\times 7$ has three 1-bits in binary (111), so it needs three partial products summed. A compiler will often rewrite it as $(x \ll 3) - x$ — one shift and one subtract — which is why strength reduction is a standard optimisation ([[compilers/07-optimisation|compilers/optimisation]]). <strong>The cost of a constant multiply depends on the bit pattern of the constant.</strong>
   </details>

2. **A carry-save adder "adds three numbers in one gate delay". Where did the carry propagation go?**
   <details><summary>Answer</summary>
   It was <em>deferred</em>, not eliminated. The CSA produces two numbers whose sum is the true total; the carries are still there, sitting in the second number, shifted one place left.<br>
   The saving comes from <strong>paying the propagation once</strong> at the end of the whole tree, rather than once per addition. Reducing 32 partial products with ordinary adders costs 31 carry propagations; with a Wallace tree it costs about 8 CSA levels plus <strong>one</strong> propagation.
   </details>

3. **Why do AI accelerators use 8-bit or 16-bit multipliers rather than 32-bit?**
   <details><summary>Answer</summary>
   Multiplier area scales as $n^2$. An 8-bit multiplier is <strong>16× smaller</strong> than a 32-bit one, so the same silicon holds 16× as many — and neural network inference is dominated by multiply-accumulate throughput, not precision.<br>
   Training and inference tolerate low precision surprisingly well, so trading numerical range for 16× more arithmetic units is overwhelmingly worth it. That $n^2$ in the area equation is the direct cause of the bf16/int8/fp8 trend.
   </details>

4. **Why does a processor provide both `SLT` and `SLTU` rather than one comparison?**
   <details><summary>Answer</summary>
   The subtraction is identical; only the <em>interpretation</em> differs. Unsigned less-than is read from the carry/borrow flag; signed less-than is $N \oplus V$.<br>
   Hardware cannot know whether your bits represent signed or unsigned values — [[how-computers-work/05-combinational/02-adders|module 21]] established that the ALU computes one result and reports both C and V. So the <em>instruction</em> must specify which interpretation applies, which is why the ISA has two comparison instructions and why C's implicit signed/unsigned conversions cause so many bugs.
   </details>

---

## 11. Practice — independent task

**Task:** Build and analyse a 4×4 multiplier, then extend the analysis.

- **(a)** By hand, multiply `1011` × `1101` using the partial-product method. Show all four rows and the sum. Verify against decimal.
- **(b)** Count the AND gates and full adders a 4×4 array multiplier needs. Generalise to $n \times n$.
- **(c)** Implement `array_multiply(a, b, width)` that sums partial products with your ripple-carry adder from module 21, and verify it exhaustively for 4×4 (256 pairs).
- **(d)** Implement a Wallace-tree reduction using `carry_save_add()`. For 4 partial products, how many CSA levels are needed? Verify it gives the same results as (c).
- **(e)** Compute the critical path of both designs at 20 ps per gate. What is the speedup?
- **(f)** Implement `multiply_by_constant(x, k)` that generates a minimal shift-and-add sequence for a *constant* multiplier. Test with $k = 7, 8, 10, 100$. Which needs the fewest operations, and why?
- **(g)** Signed multiplication: what breaks if you feed your unsigned multiplier two's-complement negatives? Try $(-3) \times 5$ in 4-bit two's complement and explain the wrong answer. Look up Booth's algorithm and state in one sentence what it fixes.

**Done when:** both multipliers agree on all 256 inputs, you can state the $n \times n$ gate count, and you can explain why $(-3) \times 5$ fails in a naive unsigned multiplier.

<details><summary>Hint for (g), only if stuck</summary>
In 4-bit two's complement, $-3$ is `1101`. An unsigned multiplier reads that as <strong>13</strong>, so it computes $13 \times 5 = 65$, not $-15$.<br>
The problem is the sign bit: in two's complement the MSB has weight $-2^{n-1}$, not $+2^{n-1}$, so its partial product must be <em>subtracted</em> rather than added. Booth's algorithm handles this (and reduces the number of partial products for runs of 1s) by recoding the multiplier into signed digits.
</details>

---

## 12. Tradeoffs and limits

- **Division is genuinely harder.** It has no simple parallel form; restoring and non-restoring division are iterative, and SRT division (the one Intel got wrong in the 1994 Pentium FDIV bug) uses a lookup table to guess quotient digits. Division typically takes 20–40 cycles and is often not pipelined.
- **Floating-point multiply is different again.** Multiply the mantissas, add the exponents, normalise, round. The integer multiplier is only one part.
- **Delay models here are first-order.** Real Wallace trees have irregular wiring that costs layout area and routing delay; Dadda trees reduce adder count slightly at the cost of a wider final adder.
- **Booth recoding is standard in practice.** It halves the number of partial products for signed multiplication and handles sign correctly, so real multipliers use it rather than the naive array shown here.

---

## Before moving on

- [ ] Trace a binary multiplication by hand and explain why no times table is needed.
- [ ] Count the gates in an $n \times n$ multiplier and explain the $n^2$ scaling.
- [ ] Explain carry-save addition and why its delay is width-independent.
- [ ] Build equality and magnitude comparators, and explain why real hardware subtracts instead.
- [ ] State which flags implement signed and unsigned comparison.

**Recap:** Binary multiplication is shift-and-add: each partial product is A ANDed with one bit of B and shifted, so no multiplication table is needed and shifting by a constant is free wiring. Summing the partial products naively gives $O(n)$ delay and $O(n^2)$ area; carry-save addition defers all carry propagation, letting a Wallace tree reduce the partial products in $O(\log n)$ with a single real carry chain at the end. Equality comparison is XNOR plus AND; magnitude comparison is a subtraction whose difference is discarded, read from C for unsigned and $N \oplus V$ for signed.

**Next:** [[how-computers-work/05-combinational/04-the-alu|Module 23 — The ALU]] wraps the adder, the logic gates and a shifter behind a multiplexer, producing the single block a processor computes with.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/05-combinational/02-adders|Module 21 — Adders]] — the carry chain this module works around
- [[how-computers-work/05-combinational/04-the-alu|Module 23 — The ALU]] — where comparison becomes SLT
- [[compilers/07-optimisation|compilers/optimisation]] — strength reduction, replacing multiplies with shifts
