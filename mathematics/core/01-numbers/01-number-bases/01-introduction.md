# Number Bases

**[Beginner]** — What a numeral actually means, how to convert between any two bases, and why computing uses base 2 and base 16 rather than the base you grew up with.

## Before you start

- You can multiply and divide whole numbers.
- You know what a remainder is.
- Nothing else. This is the first topic in the [[ss1-ss3-course-outline|SS1 curriculum]] and assumes only arithmetic.

**What you will be able to do after this lesson:**

1. Explain what the digits of a numeral mean in terms of place value and powers of the base.
2. Convert a number from any base to decimal, and from decimal to any base.
3. Add two numbers in a base other than ten, using the algorithm you already know.
4. Explain why computing uses binary, and why hexadecimal is used as shorthand for it.

**Study route:** read sections 1–4, run the lab, then attempt the practice before opening the hint.

---

## 1. A number is not a numeral

Start with a distinction that sounds pedantic and is the whole lesson.

**A number is a quantity.** Seven apples is seven apples whether you write it `7`, `VII`, `111`, or scratch seven marks on a wall.

**A numeral is notation** — the marks we make to record a quantity.

**Base is a property of the notation, not of the number.** When you write `1010` in binary and `10` in decimal, you have not written two different numbers. You have written **the same number twice**.

This matters because it is the single most common confusion in the topic. "Converting to binary" does not change a quantity. It re-spells it.

---

## 2. What the digits mean

The numeral `3407` in base ten means:

$$3 \times 10^3 + 4 \times 10^2 + 0 \times 10^1 + 7 \times 10^0$$

**Each position is worth the base raised to that position's index**, counting from zero at the right. That is the entire rule, and it is not special to ten.

The same numeral read in base **eight** would mean:

$$3 \times 8^3 + 4 \times 8^2 + 0 \times 8^1 + 7 \times 8^0 = 1536 + 256 + 0 + 7 = 1799$$

**Same digits, different base, different quantity.** Which is why `10` is ambiguous unless you say what base it is in — and why it is worth writing $1010_2$ or $\text{0b}1010$ when there is any doubt.

**A base $b$ system uses exactly $b$ digit symbols**, from $0$ to $b-1$. Base ten uses 0–9. Base two uses 0 and 1. Base sixteen needs sixteen symbols, so it borrows letters: 0–9 then A–F for ten to fifteen.

> [!NOTE]
> **There is no digit equal to the base.** Base ten has no single symbol for ten — you write `10`, meaning "one group of ten and none left over". Base two has no symbol for two; you write `10`.
>
> This is why `2` is not a valid binary digit, and the lab raises an error if you try. Every "carry" you have ever done is this rule in action: the column filled up, so it rolled over into the next.

---

## 3. Converting to decimal

Read the digits left to right, and at each step **multiply the running total by the base and add the new digit**:

```
   1011 in base 2:
     start          0
     digit 1   0*2 + 1 =  1
     digit 0   1*2 + 0 =  2
     digit 1   2*2 + 1 =  5
     digit 1   5*2 + 1 = 11
```

This is **Horner's method**, and it is better than computing each power separately: no exponentiation, one multiply and one add per digit.

## 4. Converting from decimal

**Divide repeatedly by the base. The remainders are the digits, produced in reverse.**

```
   156 into base 2:
     156 / 2 =  78  remainder 0
      78 / 2 =  39  remainder 0
      39 / 2 =  19  remainder 1
      19 / 2 =   9  remainder 1
       9 / 2 =   4  remainder 1
       4 / 2 =   2  remainder 0
       2 / 2 =   1  remainder 0
       1 / 2 =   0  remainder 1

   read bottom to top:  10011100
```

**Why it works:** dividing by the base strips off the last digit, exactly as dividing by ten strips the units digit in decimal. The remainder *is* that digit.

---

## 5. Arithmetic in any base

**The column-addition algorithm you learned at school was never about ten.** It is: add a column, keep the part below the base, carry the rest.

```
     1011           carry:  1 1 1
   + 0110
   ------
    10001
```

Column by column, right to left: $1+0=1$; $1+1=2$, which is `10` in base two, so write 0 and carry 1; $0+1+1=2$ again, write 0 carry 1; $1+0+1=2$, write 0 carry 1; the final carry becomes a new leading digit.

Check it: $1011_2 = 11$ and $0110_2 = 6$, and $10001_2 = 17$. ✓

---

## 6. Why computing uses base 2

Not because binary is mathematically special. **Because a physical switch has two reliable states.**

A transistor is either conducting or not; a voltage is either above a threshold or below it. Building a component with two clearly distinguishable states is easy and robust; building one with ten would mean ten voltage bands, each with a tenth the tolerance to noise.

**So the base is chosen by the hardware, not the mathematics.** Ternary computers have been built — the Soviet Setun in 1958 — and lost to binary because two states are so much easier to keep reliable.

## 7. Why hexadecimal exists

Binary is correct and unreadable. `11010110101100` is a number you cannot check by eye.

**Hexadecimal is base 16, and $16 = 2^4$ — so one hex digit is exactly four binary digits.** That correspondence is not approximate; it is exact, and it means you can convert digit by digit with no arithmetic at all:

```
   A5  ->  1010 0101
   ^^      ^^^^ ^^^^
   A = 1010,  5 = 0101
```

**That is the entire reason hex is used** for memory addresses, byte values, colour codes (`#FF8800`) and file dumps. It is binary with the digits grouped into readable chunks, not a different idea.

**Octal (base 8) works the same way** with $8 = 2^3$, three bits per digit. It was common when machines had 12-, 24- or 36-bit words; hex won when 8-bit bytes did, since a byte is exactly two hex digits.

---

## 8. Worked example — runnable

**Runnable example:** save as `bases_lab.py` and run `python3 bases_lab.py`. Standard library only. It deliberately avoids Python's `bin()`, `hex()` and `int(x, base)` — the point is to build the conversion, not to call it.

```python
"""Number bases: positional notation, conversion, and arithmetic in any base.

Nothing here uses Python's built-in bin/hex/int(x, base) -- the point is
to build the conversion, not to call it."""

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_decimal(text, base):
    """Positional notation: each digit is worth (digit value) x base^position.

    Read left to right, multiplying the running total by the base -- which
    is Horner's method, and avoids computing powers at all."""
    total = 0
    for ch in text.upper():
        value = DIGITS.index(ch)
        if value >= base:
            raise ValueError(f"digit {ch!r} is not valid in base {base}")
        total = total * base + value
    return total

def from_decimal(n, base):
    """Repeated division. The remainders ARE the digits, produced backwards."""
    if n == 0:
        return "0"
    digits = ""
    while n:
        digits = DIGITS[n % base] + digits
        n //= base
    return digits

def expand(text, base):
    """Show the place-value expansion that defines the number."""
    parts = []
    for i, ch in enumerate(text.upper()):
        power = len(text) - 1 - i
        parts.append(f"{DIGITS.index(ch)}x{base}^{power}")
    return " + ".join(parts)

def add_in_base(a, b, base):
    """Column addition with carry -- the algorithm you learned for base 10,
    which was never actually about ten."""
    a, b = a.upper(), b.upper()
    width = max(len(a), len(b))
    a, b = a.rjust(width, "0"), b.rjust(width, "0")
    out, carry, steps = "", 0, []
    for i in range(width - 1, -1, -1):
        da, db = DIGITS.index(a[i]), DIGITS.index(b[i])
        total = da + db + carry
        digit, new_carry = total % base, total // base
        steps.append((a[i], b[i], carry, DIGITS[digit], new_carry))
        out = DIGITS[digit] + out
        carry = new_carry
    if carry:
        out = DIGITS[carry] + out
    return out, steps

def nibbles(binary):
    """One hex digit is EXACTLY four binary digits, because 16 = 2^4."""
    binary = binary.rjust((len(binary) + 3) // 4 * 4, "0")
    return [binary[i:i+4] for i in range(0, len(binary), 4)]

if __name__ == "__main__":
    print("POSITIONAL NOTATION -- what a numeral actually means")
    for text, base in [("3407", 10), ("1011", 2), ("2A", 16), ("777", 8)]:
        print(f"  {text:>6s} in base {base:2d} = {expand(text, base):32s} = {to_decimal(text, base)}")
    print("  -> the digits are the same symbols; the BASE decides their worth.")
    print()

    print("ONE QUANTITY, MANY NUMERALS")
    print(f"  {'decimal':>8s} {'binary':>12s} {'octal':>7s} {'hex':>5s}")
    for n in (0, 5, 10, 16, 64, 255, 1000):
        print(f"  {n:8d} {from_decimal(n,2):>12s} {from_decimal(n,8):>7s} {from_decimal(n,16):>5s}")
    print("  -> 'ten' and '1010' and 'A' are the same NUMBER written three ways.")
    print("     A number is a quantity. A numeral is notation for it.")
    print()

    print("CONVERSION BY REPEATED DIVISION -- 156 into base 2")
    n, steps = 156, []
    while n:
        steps.append((n, n % 2))
        n //= 2
    for value, rem in steps:
        print(f"  {value:4d} / 2 = {value//2:4d} remainder {rem}")
    print(f"  read the remainders BOTTOM to TOP: {from_decimal(156, 2)}")
    print()

    print("COLUMN ADDITION IN BASE 2 -- the same algorithm, a different base")
    total, steps = add_in_base("1011", "0110", 2)
    print(f"    1011")
    print(f"  + 0110")
    print(f"  ------")
    print(f"    {total}")
    print(f"  {'col':>5s} {'a':>2s} {'b':>2s} {'carry in':>9s} {'digit':>6s} {'carry out':>10s}")
    for i, (da, db, cin, digit, cout) in enumerate(steps):
        print(f"  {i:5d} {da:>2s} {db:>2s} {cin:9d} {digit:>6s} {cout:10d}")
    print(f"  check: {to_decimal('1011',2)} + {to_decimal('0110',2)} = "
          f"{to_decimal(total,2)}")
    print()

    print("WHY HEX EXISTS -- one hex digit is exactly four bits")
    for h in ("A5", "FF", "1C"):
        b = from_decimal(to_decimal(h, 16), 2).rjust(8, "0")
        print(f"  {h} -> {b}  =  {' '.join(nibbles(b))}")
        per_digit = [from_decimal(DIGITS.index(c), 2).rjust(4, "0") for c in h]
        print(f"       each hex digit separately: {' '.join(per_digit)}  <- identical")
    print("  -> because 16 = 2^4, you can convert digit by digit with no")
    print("     arithmetic. That is the entire reason hex is used for memory")
    print("     dumps, colours and byte values instead of decimal.")

    assert to_decimal("1011", 2) == 11
    assert to_decimal("FF", 16) == 255
    assert from_decimal(255, 16) == "FF"
    assert from_decimal(0, 2) == "0"
    for n in range(500):
        for b in (2, 8, 16, 36):
            assert to_decimal(from_decimal(n, b), b) == n, (n, b)
    assert add_in_base("1011", "0110", 2)[0] == "10001"
    assert add_in_base("F", "1", 16)[0] == "10"
    try:
        to_decimal("2", 2); raise SystemExit("expected ValueError")
    except ValueError:
        pass
    print()
    print("bases_lab: passed")
```

Expected output:

```
POSITIONAL NOTATION -- what a numeral actually means
    3407 in base 10 = 3x10^3 + 4x10^2 + 0x10^1 + 7x10^0 = 3407
    1011 in base  2 = 1x2^3 + 0x2^2 + 1x2^1 + 1x2^0    = 11
      2A in base 16 = 2x16^1 + 10x16^0                 = 42
     777 in base  8 = 7x8^2 + 7x8^1 + 7x8^0            = 511
  -> the digits are the same symbols; the BASE decides their worth.

ONE QUANTITY, MANY NUMERALS
   decimal       binary   octal   hex
         0            0       0     0
         5          101       5     5
        10         1010      12     A
        16        10000      20    10
        64      1000000     100    40
       255     11111111     377    FF
      1000   1111101000    1750   3E8
  -> 'ten' and '1010' and 'A' are the same NUMBER written three ways.
     A number is a quantity. A numeral is notation for it.

CONVERSION BY REPEATED DIVISION -- 156 into base 2
   156 / 2 =   78 remainder 0
    78 / 2 =   39 remainder 0
    39 / 2 =   19 remainder 1
    19 / 2 =    9 remainder 1
     9 / 2 =    4 remainder 1
     4 / 2 =    2 remainder 0
     2 / 2 =    1 remainder 0
     1 / 2 =    0 remainder 1
  read the remainders BOTTOM to TOP: 10011100

COLUMN ADDITION IN BASE 2 -- the same algorithm, a different base
    1011
  + 0110
  ------
    10001
    col  a  b  carry in  digit  carry out
      0  1  0         0      1          0
      1  1  1         0      0          1
      2  0  1         1      0          1
      3  1  0         1      0          1
  check: 11 + 6 = 17

WHY HEX EXISTS -- one hex digit is exactly four bits
  A5 -> 10100101  =  1010 0101
       each hex digit separately: 1010 0101  <- identical
  FF -> 11111111  =  1111 1111
       each hex digit separately: 1111 1111  <- identical
  1C -> 00011100  =  0001 1100
       each hex digit separately: 0001 1100  <- identical
  -> because 16 = 2^4, you can convert digit by digit with no
     arithmetic. That is the entire reason hex is used for memory
     dumps, colours and byte values instead of decimal.

bases_lab: passed
```

---

## 9. Common mistakes

1. **Reading a numeral without knowing its base.** `101` is 5 in binary, 65 in octal, 101 in decimal and 257 in hex. Always state the base when it is not obvious.
2. **Using a digit equal to or larger than the base.** There is no `2` in binary and no `8` in octal. If you have written one, you have made an arithmetic slip.
3. **Reading the remainders top to bottom.** Repeated division produces the digits *backwards*. Reading them in the order they appeared reverses the number.
4. **Thinking conversion changes the quantity.** It changes only the notation.
5. **Converting hex to binary via decimal.** Unnecessary — go digit by digit, four bits each. Going through decimal is slower and invites arithmetic errors.

## 10. Practice — independent task

**Task:** Extend the lab to handle **fractional** numbers.

- **(a)** Convert `0.101` from base 2 to decimal by hand. The rule is the same, but the exponents go negative: $1 \times 2^{-1} + 0 \times 2^{-2} + 1 \times 2^{-3}$.
- **(b)** Write `fraction_to_decimal(text, base)` handling a numeral with a point, e.g. `"1011.101"`.
- **(c)** Converting *to* a base is the harder direction: repeatedly **multiply** the fraction by the base and take the integer part as the next digit. Write `decimal_to_fraction(value, base, max_digits)`.
- **(d)** Convert 0.1 (decimal) to binary with 20 digits. **It does not terminate.** Explain why, in terms of the prime factors of 10 and 2.
- **(e)** Which decimal fractions *do* terminate in binary? State the rule and test it on 0.5, 0.25, 0.75, 0.2 and 0.3.
- **(f)** Explain, in one sentence, why `0.1 + 0.2 != 0.3` in almost every programming language.

**Done when:** your two functions round-trip correctly for terminating fractions, and you can explain the non-termination of 0.1 in terms of factors rather than by saying "computers are imprecise".

<details><summary>Hint for (d) and (e) — open only after an attempt</summary>
A fraction terminates in base $b$ exactly when its denominator, in lowest terms, has <strong>no prime factors outside those of $b$</strong>.<br><br>
Base 10 has prime factors 2 and 5, so tenths, halves, quarters and fifths all terminate. Base 2 has only the factor 2, so only fractions whose denominator is a power of two terminate — $\frac{1}{2}$, $\frac{1}{4}$, $\frac{3}{4}$ do; $\frac{1}{10}$ does not, because 10 = 2 × 5 and that 5 has nowhere to go.<br><br>
This is the same reason $\frac{1}{3}$ never terminates in decimal. <strong>Floating point is not "imprecise" — it is exact in base 2</strong>, and 0.1 simply is not representable there, exactly as 1/3 is not representable in a finite decimal.
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Explain the difference between a number and a numeral.
- [ ] Write the place-value expansion of a numeral in any base.
- [ ] Convert both directions between decimal and any base, and say why repeated division works.
- [ ] Add two binary numbers with carries and check the result in decimal.
- [ ] Explain why hex is used, in terms of $16 = 2^4$.

**Recap:** A numeral's digits mean digit × base^position, and that rule is identical in every base — only the base changes. Converting to decimal is a running multiply-and-add; converting from decimal is repeated division, with the remainders read backwards. Column arithmetic works unchanged in any base. Computing uses base 2 because a switch has two reliable states, and hexadecimal because one hex digit is exactly four bits, making it readable shorthand for binary rather than a separate idea.

**Next:** [[02-binary|Binary]] — base 2 on its own terms, and the vocabulary of bits and bytes built on it.

## Related

- [[03-decimal|Decimal]] · [[04-hexadecimal|Hexadecimal]]
- [[foundations/mathematics/06-exponents|exponents]] — the powers this lesson depends on
- [[foundations/how-computers-work/01-electricity/05-the-digital-abstraction|How Computers Work — the digital abstraction]] — why two states, physically
- [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]] — signed numbers and floating point, built on this
