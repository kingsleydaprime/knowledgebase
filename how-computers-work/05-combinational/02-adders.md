# Module 21: Adders (Arithmetic from Pure Logic)

**[Intermediate]** — Numbers have never appeared in this course. Only voltages, then bits, then Boolean functions. This module makes a circuit that *adds* — and the carry chain it produces turns out to be what limits a processor's clock speed.

## Before you start

- You can build any function from gates, and know XOR is the expensive one — [[how-computers-work/04-logic/01-gates-from-transistors|module 15]], [[how-computers-work/04-logic/04-universal-gates|module 18]].
- You know that gate delays accumulate along a path and the critical path sets $f_{max}$ — [[how-computers-work/01-electricity/04-signals-and-time|module 4]].
- You have met two's complement, or are willing to take $-B = \overline{B} + 1$ on trust for one section.

**After this lesson you will be able to:**

1. Derive the half adder and full adder from truth tables, and chain them into a ripple-carry adder.
2. Explain why the carry chain makes ripple-carry delay $O(n)$ and why that caps clock frequency.
3. Explain generate/propagate and how carry-lookahead reduces delay to $O(\log n)$.
4. Build one circuit that both adds and subtracts, and compute the four ALU status flags.

**Study route:** section 5 is the point of the module. Section 6 is the fix, and section 7 explains why subtraction is free.

---

## 1. Why this exists (real-world motivation)

Everything so far has been Boolean: true and false, on and off. **Nothing has been a number.**

Yet a processor's headline job is arithmetic. So a bridge is needed — a circuit whose Boolean behaviour, when you *interpret* its bits as a binary number, happens to compute a sum.

**That interpretation is the whole trick.** The circuit does not know it is adding. It computes XOR and AND. It is only because we agree to read its inputs and outputs as place-value binary that the XOR-and-AND pattern *is* addition.

**This is the same abstraction move as [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]**, one level higher. There, a voltage became a bit by agreement. Here, a group of bits becomes a number by agreement — and a pile of gates becomes arithmetic.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Half adder** | Adds two bits; produces sum and carry. No carry input |
| **Full adder** | Adds three bits (two operands plus a carry-in) |
| **Carry-in / carry-out** | The carry entering / leaving a bit position |
| **Ripple-carry adder** | Full adders chained, each waiting for the previous carry |
| **Critical path** | The slowest route through a circuit — sets the clock |
| **Generate** ($G$) | This position makes a carry regardless of the incoming one: $A \cdot B$ |
| **Propagate** ($P$) | This position passes an incoming carry along: $A \oplus B$ |
| **Carry-lookahead** | Computing all carries in parallel from $G$ and $P$ |
| **Two's complement** | Signed representation where $-B = \overline{B} + 1$ |
| **Flags** | Status bits: zero, negative, carry, overflow |

---

## 3. The half adder

Add two single bits. There are four cases, and the answer needs two output bits:

| $A$ | $B$ | Carry | Sum |
| :-: | :-: | :-: | :-: |
| 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 |
| 1 | 1 | **1** | **0** |

Read the columns as Boolean functions:

- **Sum is 1 when exactly one input is 1** → that is **XOR**.
- **Carry is 1 only when both are 1** → that is **AND**.

$$\text{Sum} = A \oplus B \qquad\qquad \text{Carry} = A \cdot B$$

**Binary addition is XOR, with AND for the carry.** No arithmetic was designed — the truth table was read off, and the standard gates happened to match.

---

## 4. The full adder

A half adder cannot be chained, because it has nowhere to accept a carry *in*. Adding multi-bit numbers requires three inputs per position.

The elegant construction uses two half adders: add $A$ and $B$, then add the carry-in to that partial sum. A carry from either stage produces a carry out.

$$\text{Sum} = A \oplus B \oplus C_{in} \qquad\qquad C_{out} = (A \cdot B) + (C_{in} \cdot (A \oplus B))$$

```
    A ──┐
        HALF ADDER ──┬── sum1 ──┐
    B ──┘            │          HALF ADDER ── SUM
                   carry1       │
                     │   Cin ───┘  └── carry2
                     │              │
                     └──── OR ──────┘
                            │
                          C_out
```

**Now they chain.** Wire each stage's carry-out to the next stage's carry-in and you have an $n$-bit adder. The lab verifies an 8-bit version against Python's arithmetic on **all 65,536 input pairs**, with zero failures.

---

### Chaining them: an 8-bit addition, traced by hand

This is the step that turns "XOR and AND handle 1+1" into "this adds real numbers". **Wire one full adder to each bit position, and connect each carry-out to the next stage's carry-in.** That is the entire construction.

Take $107 + 58$:

```
   A = 01101011  (107)
   B = 00111010  (58)
```

Work from bit 0 (rightmost) upward. At each position the full adder sees three bits — $A_i$, $B_i$, and the carry from below — and produces a sum bit and a carry for the position above:

| Pos | $A_i$ | $B_i$ | $C_{in}$ | $A \oplus B$ | Sum $= (A{\oplus}B){\oplus}C_{in}$ | $A \cdot B$ | $C_{in}(A{\oplus}B)$ | $C_{out}$ |
| --: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 0 | 1 | 0 | 0 | 1 | **1** | 0 | 0 | 0 |
| 1 | 1 | 1 | 0 | 0 | **0** | 1 | 0 | **1** |
| 2 | 0 | 0 | 1 | 0 | **1** | 0 | 0 | 0 |
| 3 | 1 | 1 | 0 | 0 | **0** | 1 | 0 | **1** |
| 4 | 0 | 1 | 1 | 1 | **0** | 0 | 1 | **1** |
| 5 | 1 | 1 | 1 | 0 | **1** | 1 | 0 | **1** |
| 6 | 1 | 0 | 1 | 1 | **0** | 0 | 1 | **1** |
| 7 | 0 | 0 | 1 | 0 | **1** | 0 | 0 | 0 |

Reading the sum column from bit 7 down to bit 0: `10100101` = **165**. And $107 + 58 = 165$. ✓

**Follow one interesting row.** At position 4, $A_4 = 0$ and $B_4 = 1$, so on their own they would give sum 1 and no carry. But a carry arrived from position 3, so the sum becomes $1 \oplus 1 = 0$ and a carry is generated by the $C_{in}(A \oplus B)$ term. **The carry that was born at position 1 has now influenced positions 2, 3, 4, 5, 6 and 7** — that single chain of dependency is the entire subject of section 5.

### Scaling to 16, 32 and 64 bits

**Nothing changes except the number of rows.**

```
   4-bit adder:    4 full adders  in a chain
   8-bit adder:    8 full adders  in a chain
  32-bit adder:   32 full adders  in a chain
  64-bit adder:   64 full adders  in a chain
```

Each full adder is the same six-gate circuit. There is no new idea at 32 bits, no special wide-adder component — just more copies of the identical block, carry-out to carry-in, all the way up.

**Two things do change, and both matter:**

1. **Area grows linearly.** A 64-bit adder is 64 full adders, roughly 400 gates. Fine.
2. **Delay grows linearly too** — and that is the problem, because the carry must physically travel the whole chain before the top bit is correct. This is what section 5 quantifies and section 6 fixes.

> [!NOTE]
> **This is the answer to "how does electricity do maths?"** — and it is worth stating plainly.
>
> It does not. **A full adder is six gates obeying physics.** Each gate is transistors switching, which is electrons responding to fields. Nothing in the circuit knows what "107" is.
>
> The arithmetic exists because *we* agreed to read the eight wires as place-value binary. Under that agreement, the pattern of XORs and ANDs that the physics produces is exactly the pattern that addition requires. **The circuit computes a Boolean function; addition is our interpretation of it** — and the interpretation holds for 8 bits, 64 bits, or 4096, because the place-value agreement scales and the wiring just repeats.
>
> This is the same move as [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]], where a voltage became a bit by agreement. Meaning is never in the silicon; it is in the convention, and the silicon is built to honour it.


## 5. The carry chain — the real subject of this module

Here is the problem, and it is the reason this module matters beyond arithmetic.

**Bit 0's carry cannot be computed until bit 0's inputs are known — fine. But bit 1 must wait for bit 0's carry. Bit 2 must wait for bit 1's. And so on.**

```
   A7 B7    A6 B6    A5 B5         A1 B1    A0 B0
    │  │     │  │     │  │          │  │     │  │
   ┌▼──▼┐   ┌▼──▼┐   ┌▼──▼┐        ┌▼──▼┐   ┌▼──▼┐
   │ FA │◄──│ FA │◄──│ FA │◄─ ... ─│ FA │◄──│ FA │◄── 0
   └─┬──┘   └─┬──┘   └─┬──┘        └─┬──┘   └─┬──┘
     S7       S6       S5            S1       S0

     ◄──────── carry ripples this way, one stage at a time ────────
```

**The carry ripples.** Each full adder adds about 2 gate delays to the carry path, so an $n$-bit ripple-carry adder has delay proportional to $n$.

At 20 ps per gate:

| Width | Ripple delay | Max clock |
| ---: | ---: | ---: |
| 8 | 320 ps | 3.12 GHz |
| 16 | 640 ps | 1.56 GHz |
| 32 | 1280 ps | 0.78 GHz |
| 64 | 2560 ps | 0.39 GHz |

**A 64-bit ripple-carry adder caps the clock at under 400 MHz.**

That is a devastating number. Recall [[how-computers-work/01-electricity/04-signals-and-time|module 4]]: the clock period must exceed the critical path. **If the adder is on the critical path — and in a CPU it almost always is — then the carry chain alone limits the entire processor.**

**The bottleneck is not the addition.** Each bit's sum is two XORs, and all of them could be computed simultaneously. **The bottleneck is purely the sequential dependency of the carry** — every position waiting to hear from its neighbour.

---

## 6. Carry-lookahead — computing carries in parallel

The fix comes from asking a sharper question: *must* a carry ripple, or can it be predicted?

Look at what each bit position can do with a carry:

- **Generate:** if $A_i = 1$ and $B_i = 1$, this position produces a carry **whatever comes in**. $G_i = A_i \cdot B_i$.
- **Propagate:** if exactly one of $A_i, B_i$ is 1, this position passes an incoming carry through. $P_i = A_i \oplus B_i$.

So the carry out of position $i$ is:

$$C_{i+1} = G_i + P_i \cdot C_i$$

**Expand it and the recursion unrolls into a flat expression:**

$$C_2 = G_1 + P_1 G_0 + P_1 P_0 C_0$$
$$C_3 = G_2 + P_2 G_1 + P_2 P_1 G_0 + P_2 P_1 P_0 C_0$$

**Every carry is now a direct function of the inputs**, with no dependence on other carries. All $G_i$ and $P_i$ compute in parallel in one gate delay; the carries follow in a tree of depth $\log n$.

| Width | Ripple | Lookahead | Speedup |
| ---: | ---: | ---: | ---: |
| 8 | 320 ps | 160 ps | 2.0× |
| 16 | 640 ps | 200 ps | 3.2× |
| 32 | 1280 ps | 240 ps | 5.3× |
| 64 | 2560 ps | 280 ps | **9.1×** |

**At 64 bits, lookahead turns a 390 MHz limit into 3.6 GHz.**

> [!NOTE]
> **The cost is area, and it grows fast.** Those expanded expressions need wide AND and OR gates, and the widths grow with the number of bits looked ahead — running straight into the fan-in limits of [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].
>
> Real adders therefore use **hierarchical lookahead**: 4-bit lookahead blocks, themselves combined by a second level of lookahead. Modern designs use refinements like Kogge–Stone and Brent–Kung, which are different points on the same area-versus-depth tradeoff.
>
> **This is the recurring shape of digital design:** a sequential dependency is the enemy, and you pay area to convert it into a parallel tree. You will see exactly this pattern again in pipelining ([[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]]) and in parallel prefix algorithms.

---

## 7. Subtraction is free

**You do not need a subtractor.** In two's complement, $-B = \overline{B} + 1$, so:

$$A - B = A + \overline{B} + 1$$

You already have an adder. Invert each bit of $B$, and set the carry-in to 1 to supply the $+1$.

**Both operations, one circuit:** put an XOR gate on each bit of $B$ with a control line `SUB`, and feed `SUB` to the carry-in as well.

- `SUB = 0`: XOR passes $B$ unchanged, carry-in 0 → **addition**.
- `SUB = 1`: XOR inverts $B$, carry-in 1 → **subtraction**.

**Two extra XOR gates and one wire buy you subtraction.** This is the single strongest practical argument for two's complement over sign-magnitude, and it is why essentially every machine uses it.

### The flags

An ALU also reports status bits about the result:

| Flag | Meaning | How it is computed |
| :--- | :--- | :--- |
| **Z** (zero) | Result is zero | NOR of all result bits |
| **N** (negative) | Result's sign bit is set | The MSB |
| **C** (carry) | Unsigned overflow | Carry out of the MSB |
| **V** (overflow) | **Signed** overflow | $C_{out} \oplus C_{into\ MSB}$ |

**C and V are different, and confusing them is a classic bug.** Carry means the result exceeded the *unsigned* range. Overflow means it exceeded the *signed* range.

The lab shows `200 - 100 = 100` with `C=1, V=1`: correct as unsigned arithmetic, but as *signed* 8-bit values that is $(-56) - 100 = -156$, which does not fit in $[-128, 127]$ — so V flags it. **The circuit computes one result; which flag matters depends on how the software chooses to interpret the bits.**

---

## 8. Predict before reading on

Adding two 8-bit signed numbers: $100 + 28$.

**What is stored, and which flags are set?**

<details><summary>Check your answer</summary>

$100 + 28 = 128$. In 8 bits, 128 is stored as `10000000`.

Interpreted as **signed**, `10000000` is **−128**.

So the machine computes $100 + 28 = -128$. Flags: **V = 1** (signed overflow — the true result 128 exceeds the maximum 127), **N = 1** (sign bit set), **C = 0** (no unsigned overflow; 128 fits fine in 8 unsigned bits).

**Two positive numbers added to give a negative result** — the classic signature of signed overflow, and exactly what V exists to detect. This is the hardware behind the `INT_MIN` and overflow bugs described in [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]], and why signed overflow is undefined behaviour in C: the compiler is entitled to assume V never gets set.
</details>

---

## 9. Worked example — runnable

Save as `adder_lab.py` and run `python3 adder_lab.py`.

```python
"""Arithmetic built from logic gates -- and why the carry chain sets clock speed."""

GATE_DELAY_PS = 20        # per-gate propagation delay (module 4)

def half_adder(a, b):
    """Two bits in, sum and carry out. Sum is XOR, carry is AND."""
    return a ^ b, a & b

def full_adder(a, b, carry_in):
    """Three bits in. Built from two half adders plus an OR."""
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, carry_in)
    return s2, c1 | c2

def trace_addition(a, b, width=8):
    """Print every full adder's inputs and outputs, position by position.

    This is the whole of multi-bit addition: one full adder per bit, with
    each carry-out wired to the next stage's carry-in. Nothing else."""
    print(f"    A = {a:0{width}b} ({a})")
    print(f"    B = {b:0{width}b} ({b})")
    print(f"    {'pos':>3s} {'A':>2s} {'B':>2s} {'Cin':>4s} | "
          f"{'A^B':>4s} {'^Cin':>5s} = {'Sum':>3s} | {'A&B':>4s} {'Cin&(A^B)':>10s}"
          f" = {'Cout':>4s}")
    carry, bits = 0, []
    for i in range(width):
        x, y = (a >> i) & 1, (b >> i) & 1
        xor1 = x ^ y
        s_bit = xor1 ^ carry
        and1, and2 = x & y, carry & xor1
        cout = and1 | and2
        print(f"    {i:3d} {x:2d} {y:2d} {carry:4d} | {xor1:4d} {s_bit:5d} = {s_bit:3d}"
              f" | {and1:4d} {and2:10d} = {cout:4d}")
        bits.append(s_bit)
        carry = cout
    total = sum(b << i for i, b in enumerate(bits))
    print(f"    result = {total:0{width}b} ({total}), carry out = {carry}")
    return total, carry

def ripple_carry_add(a, b, width=8, carry_in=0):
    """Chain full adders, each waiting for the previous carry. Returns
    (sum, carry_out, carry_into_msb) -- the last is needed for overflow."""
    result, carry = 0, carry_in
    carry_into_msb = 0
    for i in range(width):
        if i == width - 1:
            carry_into_msb = carry
        bit_a, bit_b = (a >> i) & 1, (b >> i) & 1
        s, carry = full_adder(bit_a, bit_b, carry)
        result |= s << i
    return result, carry, carry_into_msb

def add_or_subtract(a, b, subtract, width=8):
    """One circuit for both: invert B and set carry-in when subtracting.
    This is two's complement -- A - B == A + (~B) + 1."""
    b_effective = (~b & ((1 << width) - 1)) if subtract else b
    return ripple_carry_add(a, b_effective, width, carry_in=1 if subtract else 0)

def flags(a, b, result, carry_out, carry_into_msb, width=8):
    """The status bits every ALU produces."""
    sign_bit = (result >> (width - 1)) & 1
    return {
        "zero":     1 if result == 0 else 0,
        "negative": sign_bit,
        "carry":    carry_out,                       # unsigned overflow
        "overflow": carry_out ^ carry_into_msb,      # signed overflow
    }

def ripple_delay_ps(width):
    """Carry must ripple through every stage: 2 gate delays each."""
    return width * 2 * GATE_DELAY_PS

def lookahead_delay_ps(width):
    """Carry-lookahead computes carries as a tree: O(log n) depth."""
    import math
    levels = math.ceil(math.log2(width))
    return (2 + 2 * levels) * GATE_DELAY_PS

def max_clock_ghz(delay_ps):
    return 1e12 / delay_ps / 1e9

if __name__ == "__main__":
    print("HALF ADDER -- sum = A XOR B, carry = A AND B:")
    for a in (0, 1):
        for b in (0, 1):
            s, c = half_adder(a, b)
            print(f"  {a} + {b} = {c}{s}  (carry={c}, sum={s})")
    print()

    print("FULL ADDER -- adds a carry-in, so adders can be chained:")
    for a in (0, 1):
        for b in (0, 1):
            for cin in (0, 1):
                s, c = full_adder(a, b, cin)
                print(f"  {a} + {b} + {cin} = {c}{s}", end="   ")
        print()
    print()

    print("TRACING an 8-bit addition -- one full adder per bit position:")
    trace_addition(107, 58, 8)
    print("    the ONLY thing that changes at 16, 32 or 64 bits is how many rows")
    print()

    print("verifying the 8-bit ripple-carry adder against Python arithmetic:")
    failures = 0
    for a in range(256):
        for b in range(256):
            got, carry, _ = ripple_carry_add(a, b, 8)
            want = (a + b) & 0xFF
            if got != want or carry != ((a + b) >> 8):
                failures += 1
    print(f"  all 65,536 input pairs checked, {failures} failures")
    assert failures == 0
    print()

    print("SUBTRACTION -- same circuit, B inverted and carry-in = 1:")
    for a, b in [(10, 3), (3, 10), (100, 100), (200, 100)]:
        result, carry, cmsb = add_or_subtract(a, b, subtract=True)
        f = flags(a, b, result, carry, cmsb)
        signed = result - 256 if result > 127 else result
        print(f"  {a:3d} - {b:3d} = {result:3d} (as signed: {signed:4d})"
              f"  flags: Z={f['zero']} N={f['negative']}"
              f" C={f['carry']} V={f['overflow']}")
    print()

    print("SIGNED OVERFLOW -- when the result won't fit in 8 bits:")
    for a, b, label in [(100, 27, "100+27 = 127, fits"),
                        (100, 28, "100+28 = 128, OVERFLOWS"),
                        (127, 1,  "127+1        OVERFLOWS")]:
        result, carry, cmsb = ripple_carry_add(a, b, 8)
        f = flags(a, b, result, carry, cmsb)
        signed = result - 256 if result > 127 else result
        print(f"  {label:26s} -> stored {result:3d} = signed {signed:4d}"
              f"  V={f['overflow']}")
    print()

    print("THE CARRY CHAIN IS THE BOTTLENECK:")
    print(f"  {'width':>6s} {'ripple':>10s} {'lookahead':>12s} {'ripple f_max':>14s}"
          f" {'lookahead f_max':>17s}")
    for width in (8, 16, 32, 64):
        r, l = ripple_delay_ps(width), lookahead_delay_ps(width)
        print(f"  {width:6d} {r:8d} ps {l:10d} ps"
              f" {max_clock_ghz(r):12.2f} GHz {max_clock_ghz(l):15.2f} GHz")
    print()
    print(f"  at 64 bits, lookahead is"
          f" {ripple_delay_ps(64)/lookahead_delay_ps(64):.1f}x faster")
    print("  -> ripple carry is O(n) delay; lookahead is O(log n)")

    assert ripple_delay_ps(64) > lookahead_delay_ps(64)
    assert flags(0, 0, 0, 0, 0)["zero"] == 1
    print()
    print("adder_lab: passed")
```

Expected output:

```
HALF ADDER -- sum = A XOR B, carry = A AND B:
  0 + 0 = 00  (carry=0, sum=0)
  0 + 1 = 01  (carry=0, sum=1)
  1 + 0 = 01  (carry=0, sum=1)
  1 + 1 = 10  (carry=1, sum=0)

FULL ADDER -- adds a carry-in, so adders can be chained:
  0 + 0 + 0 = 00     0 + 0 + 1 = 01     0 + 1 + 0 = 01     0 + 1 + 1 = 10   
  1 + 0 + 0 = 01     1 + 0 + 1 = 10     1 + 1 + 0 = 10     1 + 1 + 1 = 11   

TRACING an 8-bit addition -- one full adder per bit position:
    A = 01101011 (107)
    B = 00111010 (58)
    pos  A  B  Cin |  A^B  ^Cin = Sum |  A&B  Cin&(A^B) = Cout
      0  1  0    0 |    1     1 =   1 |    0          0 =    0
      1  1  1    0 |    0     0 =   0 |    1          0 =    1
      2  0  0    1 |    0     1 =   1 |    0          0 =    0
      3  1  1    0 |    0     0 =   0 |    1          0 =    1
      4  0  1    1 |    1     0 =   0 |    0          1 =    1
      5  1  1    1 |    0     1 =   1 |    1          0 =    1
      6  1  0    1 |    1     0 =   0 |    0          1 =    1
      7  0  0    1 |    0     1 =   1 |    0          0 =    0
    result = 10100101 (165), carry out = 0
    the ONLY thing that changes at 16, 32 or 64 bits is how many rows

verifying the 8-bit ripple-carry adder against Python arithmetic:
  all 65,536 input pairs checked, 0 failures

SUBTRACTION -- same circuit, B inverted and carry-in = 1:
   10 -   3 =   7 (as signed:    7)  flags: Z=0 N=0 C=1 V=0
    3 -  10 = 249 (as signed:   -7)  flags: Z=0 N=1 C=0 V=0
  100 - 100 =   0 (as signed:    0)  flags: Z=1 N=0 C=1 V=0
  200 - 100 = 100 (as signed:  100)  flags: Z=0 N=0 C=1 V=1

SIGNED OVERFLOW -- when the result won't fit in 8 bits:
  100+27 = 127, fits         -> stored 127 = signed  127  V=0
  100+28 = 128, OVERFLOWS    -> stored 128 = signed -128  V=1
  127+1        OVERFLOWS     -> stored 128 = signed -128  V=1

THE CARRY CHAIN IS THE BOTTLENECK:
   width     ripple    lookahead   ripple f_max   lookahead f_max
       8      320 ps        160 ps         3.12 GHz            6.25 GHz
      16      640 ps        200 ps         1.56 GHz            5.00 GHz
      32     1280 ps        240 ps         0.78 GHz            4.17 GHz
      64     2560 ps        280 ps         0.39 GHz            3.57 GHz

  at 64 bits, lookahead is 9.1x faster
  -> ripple carry is O(n) delay; lookahead is O(log n)

adder_lab: passed
```

Note `full_adder` calls `half_adder` twice — the hierarchy is real, not decorative. And `add_or_subtract` inverts B and sets carry-in from the *same* control signal, which is the two-XOR trick in code.

---

## 10. Common pitfalls and traps

1. **Confusing carry with overflow.** C is unsigned overflow, V is signed. They are computed differently and frequently disagree.
2. **Thinking the adder knows about signs.** It does not. The identical circuit and identical bits serve both interpretations; only the flags differ.
3. **Assuming ripple-carry is fine because addition is "simple".** The additions are simple and parallel; the *carry dependency* is what costs $O(n)$.
4. **Forgetting the carry-in when subtracting.** $\overline{B}$ alone gives ones' complement, off by one. The $+1$ comes from the carry-in.
5. **Expecting carry-lookahead to be free.** It costs area, and fan-in limits force hierarchical structures.
6. **Overlooking XOR's cost.** Each full adder uses two XORs, and XOR is the most expensive common gate (module 15). A 64-bit adder contains 128 of them.

---

## 11. Check your understanding

1. **Why can all the sum bits be computed in parallel, while the carries cannot?**
   <details><summary>Answer</summary>
   $\text{Sum}_i = A_i \oplus B_i \oplus C_i$ depends on that position's own inputs plus <em>its</em> carry-in. If the carries were known, every sum would compute simultaneously in two XOR delays.<br>
   But $C_{i+1}$ depends on $C_i$, which depends on $C_{i-1}$ — a genuine sequential chain. <strong>The carries are the only sequential part of addition</strong>, which is why every fast-adder technique targets the carry and none targets the sum.
   </details>

2. **Show that a full adder's carry-out can be written $G + P \cdot C_{in}$, and explain why $P$ uses XOR rather than OR.**
   <details><summary>Answer</summary>
   $C_{out} = AB + C_{in}(A \oplus B) = G + P \cdot C_{in}$ with $G = AB$, $P = A \oplus B$.<br>
   Using OR for $P$ would also give a correct <em>adder</em>, since when $A = B = 1$ the $G$ term already forces a carry, making the $P$ term redundant there. XOR is preferred because $P = A \oplus B$ is <strong>the sum bit that must be computed anyway</strong>, so it is shared rather than built twice — and because it makes $G$ and $P$ mutually exclusive, which simplifies the lookahead algebra.
   </details>

3. **A CPU has a 64-bit ripple-carry ALU on its critical path. Marketing wants 4 GHz. What must change?**
   <details><summary>Answer</summary>
   4 GHz means a 250 ps period. A 64-bit ripple-carry adder needs 2560 ps — <strong>ten times too slow</strong>. No amount of process improvement closes a 10× gap.<br>
   The fix is architectural: replace ripple-carry with carry-lookahead (280 ps, from the table) or a parallel-prefix adder. Alternatively, <em>pipeline</em> the adder across several cycles — which raises throughput without reducing latency, and introduces the hazards handled in [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]].<br>
   This is a concrete instance of module 4's lesson: clock speed is deduced from the critical path, so making a chip faster means finding and shortening that path.
   </details>

4. **Why is two's complement, rather than sign-magnitude, essentially universal?**
   <details><summary>Answer</summary>
   Because subtraction becomes addition. $A - B = A + \overline{B} + 1$, so <strong>one adder plus a row of XORs handles both operations</strong> — no separate subtractor, no special-casing of signs.<br>
   Sign-magnitude requires comparing magnitudes, deciding which to subtract from which, and fixing up the result sign. It also has two representations of zero ($+0$ and $-0$), which breaks equality comparison.<br>
   Two's complement has one zero and reuses the adder unchanged. The cost is an asymmetric range — $-128$ has no positive counterpart in 8 bits — which is the source of the `abs(INT_MIN)` bug in [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]].
   </details>

---

## 12. Practice — independent task

**Task:** Extend the lab into a 16-bit adder and analyse its timing.

- **(a)** Verify your 16-bit ripple-carry adder against Python arithmetic on 10,000 random pairs plus all boundary cases (0, 1, 0xFFFF, 0x8000, 0x7FFF).
- **(b)** Compute the ripple-carry delay and $f_{max}$ at 20 ps per gate.
- **(c)** Implement `generate_propagate(a, b, width)` returning the $G$ and $P$ bit vectors, then implement 4-bit carry-lookahead blocks and verify the carries match the ripple-carry version.
- **(d)** Build a 16-bit adder from four 4-bit lookahead blocks chained by ripple, then from four blocks with a second-level lookahead. Compute the delay of each.
- **(e)** Tabulate all three designs — pure ripple, block-ripple, two-level lookahead — with delay, $f_{max}$, and an approximate gate count. Which would you choose for a 3 GHz processor?
- **(f)** Add signed and unsigned overflow detection and verify: find an input pair where C is set but V is not, and another where V is set but C is not.

**Done when:** all three adders agree on every test input, and you can justify a design choice against a 3 GHz target with delay *and* area numbers.

<details><summary>Hint for (f), only if stuck</summary>
<strong>C set, V clear:</strong> add two large <em>unsigned</em> values whose signed interpretations are negative, e.g. `0xFFFF + 0x0001`. Unsigned this overflows; signed it is $(-1) + 1 = 0$, perfectly valid.<br>
<strong>V set, C clear:</strong> add two large positive signed values, e.g. `0x7FFF + 0x0001`. Signed this overflows into negative; unsigned it is just 32768, well within range.<br>
The two flags genuinely answer different questions, which is why hardware provides both and leaves the choice to the instruction.
</details>

---

## 13. Tradeoffs and limits

- **Delay models here are first-order.** Real gate delay depends on fan-out, wire load and input slew. SPICE or static timing analysis gives real numbers; this model gets the scaling right.
- **Lookahead area grows quickly.** Full lookahead across 64 bits is impractical; hierarchical schemes trade a little depth for far less area.
- **Other adder families exist.** Carry-select computes both possible results and picks one when the carry arrives; carry-skip bypasses blocks that merely propagate. All target the same enemy.
- **Multiplication is a different problem.** It is repeated shift-and-add, and fast multipliers use Wallace or Dadda trees to sum partial products. Division is harder still and is usually iterative rather than combinational.

---

## Before moving on

- [ ] Derive the half adder from its truth table and identify XOR and AND.
- [ ] Build a full adder from two half adders and explain why chaining needs a carry-in.
- [ ] Explain why ripple-carry delay is $O(n)$ and compute $f_{max}$ for a given width.
- [ ] Define generate and propagate, and explain how lookahead reaches $O(\log n)$.
- [ ] Build an add/subtract unit with two XORs and a control line.
- [ ] Distinguish the carry and overflow flags and give an input where they differ.

**Recap:** A half adder is XOR for sum and AND for carry; a full adder chains by accepting a carry-in. Ripple-carry adders are correct but their carry dependency gives $O(n)$ delay — a 64-bit one caps the clock below 400 MHz. Carry-lookahead expresses each carry directly from generate and propagate signals, reducing depth to $O(\log n)$ and giving a 9× speedup at 64 bits, at the cost of area. Two's complement makes subtraction free: invert B, set carry-in, and the same adder does both.

**Next:** [[how-computers-work/05-combinational/04-the-alu|Module 23 — The ALU]] wraps the adder together with logic operations and a shifter behind a multiplexer, producing one circuit that performs many operations — the computational core of every processor.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/01-electricity/04-signals-and-time|Module 4]] — critical path and clock frequency
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — the MUX that selects the ALU's operation
- [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]] — two's complement and real overflow bugs
- [[foundations/computer-architecture/06-pipelining|computer-architecture/pipelining]] — the other answer to a long critical path
