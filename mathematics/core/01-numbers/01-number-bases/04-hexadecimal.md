# Hexadecimal (Base 16)

**[Beginner]** — The base nobody counts in and everybody reads. Chosen for one mathematical reason, and used everywhere that reason applies.

## Before you start

- You can convert between bases — [[01-introduction|number bases]].
- You know what a bit and a byte are — [[02-binary|binary]].

**What you will be able to do after this lesson:**

1. Read and write hex fluently, including the letter digits.
2. Convert between hex and binary by sight, with no arithmetic.
3. Explain why hex is used for memory dumps, colours and byte values.
4. Recognise hex in the wild and know what it is describing.

---

## 1. Sixteen digits

Base 16 needs sixteen symbols. The first ten are the familiar digits; the rest borrow letters:

| Hex | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
| :-- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Dec | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |

**A–F are digits, not letters that happen to be there.** `A` means the quantity ten, exactly as `7` means seven.

Hex is usually written with a marker so it is not mistaken for decimal: `0xFF`, `#FF`, `$FF` or `FFh` depending on the convention.

## 2. The one reason hex exists

$$16 = 2^4$$

**So one hex digit is exactly four binary digits — always, with no remainder and no carrying between them.**

```
   1010 0101         binary
   ^^^^ ^^^^
     A    5          hex
```

You convert **digit by digit**, in either direction, with no arithmetic:

| Hex | Binary | | Hex | Binary |
| :-: | :----- | - | :-: | :----- |
| 0 | 0000 | | 8 | 1000 |
| 1 | 0001 | | 9 | 1001 |
| 2 | 0010 | | A | 1010 |
| 3 | 0011 | | B | 1011 |
| 4 | 0100 | | C | 1100 |
| 5 | 0101 | | D | 1101 |
| 6 | 0110 | | E | 1110 |
| 7 | 0111 | | F | 1111 |

**Learn those sixteen rows and hex becomes free.** It is the only memorisation this topic asks for, and it pays off permanently.

> [!NOTE]
> **Compare with decimal, which has no such relationship.** $10$ is not a power of 2, so converting binary to decimal requires actual arithmetic and mixes all the bits together. Changing one bit can change every decimal digit.
>
> In hex, changing one bit changes **exactly one hex digit**. That locality is why memory dumps, colour codes and bit masks are all written in hex — you can see which bits moved.

## 3. A byte is two hex digits

A byte is 8 bits, and $8 = 2 \times 4$, so **every byte is exactly two hex digits** — from `00` to `FF`, covering all 256 values.

That correspondence is why hex is everywhere bytes are:

- **Memory addresses** — `0x7FFE4C2A1B30`
- **Colours** — `#FF8800` is red `FF`, green `88`, blue `00`
- **MAC addresses** — `00:1B:44:11:3A:B7`
- **Byte values in a hex dump** — two characters per byte, so columns line up
- **Bit masks** — `0xFF00` obviously means "the top byte", which `65280` does not
- **Unicode code points** — `U+1F600`
- **Hashes** — a SHA-256 digest is 64 hex characters, that is 32 bytes

## 4. Reading hex in the wild

```
   #FF8800     colour: full red, two-thirds green, no blue -> orange
   0x0F        the low four bits set
   0xFF00      the high byte of a 16-bit value
   0x80000000  the top bit of a 32-bit value -- the sign bit
   0xDEADBEEF  a deliberately recognisable marker value
```

**That last one is a real convention.** Programmers fill unused memory with distinctive hex patterns — `0xDEADBEEF`, `0xCAFEBABE`, `0xBAADF00D` — because spotting one in a debugger immediately tells you that you are reading uninitialised or freed memory rather than real data.

## 5. Practice — independent task

- **(a)** Convert by sight, no arithmetic: `0x3F`, `0xC0`, `0xA7`, `0xFFFF` to binary.
- **(b)** Convert to hex by sight: `1101 0110`, `0000 1111`, `1111 0000 1010 0101`.
- **(c)** What colour is `#00FF00`? What is `#808080`? What does `#FFFFFF` mean, and why?
- **(d)** A 32-bit value is `0x80000000`. Which single bit is set? What does that bit mean in a signed integer ([[foundations/computer-architecture/02-data-representation|two's complement]])?
- **(e)** Write `mask(bits)` returning the hex mask that selects the low `n` bits — `mask(4)` should give `0xF`, `mask(8)` gives `0xFF`, `mask(12)` gives `0xFFF`. Explain the pattern.
- **(f)** Given `0xAB` and the mask `0x0F`, what does a bitwise AND produce? What does that operation extract, and why is it a common idiom?

**Done when:** you can convert both directions by sight without writing anything down, and can explain what masking with `0x0F` extracts.

<details><summary>Hint for (e) and (f) — open only after an attempt</summary>
The mask for the low $n$ bits is $2^n - 1$, which in hex is a run of <code>F</code>s (plus one partial digit when $n$ is not a multiple of 4). That is <code>(1 &lt;&lt; n) - 1</code> in most languages.<br><br>
<code>0xAB &amp; 0x0F</code> keeps only the bits where the mask has 1s, giving <code>0x0B</code> — <strong>the low nibble</strong>. Since one hex digit <em>is</em> a nibble, masking with <code>0x0F</code> extracts the last hex digit. That is why bit manipulation is written in hex: the mask visually shows which digits survive.
</details>

## Before moving on

- [ ] Recite the sixteen hex digits and their values.
- [ ] Convert hex to binary and back by sight.
- [ ] Explain why $16 = 2^4$ is the entire reason hex is used.
- [ ] Explain why a byte is exactly two hex digits.
- [ ] Read a colour code and a bit mask and say what each describes.

**Recap:** Hexadecimal uses sixteen digits, 0–9 then A–F. It exists because $16 = 2^4$, so one hex digit is exactly four bits and conversion is digit-by-digit with no arithmetic — and a byte, being 8 bits, is exactly two hex digits. That locality means changing one bit changes exactly one hex digit, which is why memory dumps, colours, masks and addresses are all written in hex rather than decimal.

**Next:** [[foundations/mathematics/01-numbers|Number systems]] — from *how* numbers are written to *what kinds* of number exist.

## Related

- [[01-introduction|Number bases]] · [[02-binary|Binary]] · [[03-decimal|Decimal]]
- [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]] — where these bytes get meaning
- [[foundations/how-computers-work/index|How Computers Work]] — the course this unblocks
