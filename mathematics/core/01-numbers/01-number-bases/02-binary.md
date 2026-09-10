# Binary (Base 2)

**[Beginner]** — Base 2 on its own terms: the vocabulary built on it, the powers worth memorising, and why "kilobyte" has two different meanings.

## Before you start

- You can convert between decimal and any base — [[01-introduction|number bases]].
- You know what a power is — [[foundations/mathematics/06-exponents|exponents]].

**What you will be able to do after this lesson:**

1. Read and write binary numerals fluently for small values.
2. Recite the powers of two up to $2^{16}$ and explain where each shows up.
3. Explain bit, byte, nibble and word, and what each is worth.
4. Explain why 1 KB is sometimes 1000 and sometimes 1024 bytes.

---

## 1. Two digits, and what follows

Binary uses only `0` and `1`. Every place is worth twice the one to its right:

```
   place:   128  64  32  16   8   4   2   1
   power:   2^7 2^6 2^5 2^4 2^3 2^2 2^1 2^0

   1  0  1  1  0  0  1  0   =  128 + 32 + 16 + 2  =  178
```

**Reading small binary by eye is a skill worth acquiring**, and it comes from knowing the powers rather than from calculating.

| $n$ | $2^n$ | Where you meet it |
| ---: | ---: | :--- |
| 1 | 2 | one bit, two states |
| 3 | 8 | bits in a byte |
| 4 | 16 | one hex digit |
| 8 | 256 | values in a byte |
| 10 | 1,024 | a "K" in memory sizes |
| 16 | 65,536 | a 16-bit address space |
| 20 | 1,048,576 | a "M" |
| 32 | 4,294,967,296 | 32-bit address limit — about 4 GB |

**That last row is why 32-bit machines could not use more than 4 GB of RAM.** Not a design choice anyone made; just $2^{32}$.

## 2. The vocabulary

| Term | Size | Note |
| :--- | :--- | :--- |
| **bit** | 1 binary digit | from *binary digit* |
| **nibble** | 4 bits | exactly one hex digit |
| **byte** | 8 bits | 256 possible values; the standard unit of memory |
| **word** | machine-dependent | 16, 32 or 64 bits — whatever the CPU handles naturally |

**A byte holds 256 values** — 0 to 255 unsigned, or −128 to 127 signed ([[foundations/computer-architecture/02-data-representation|two's complement]]).

## 3. The kilobyte problem

$2^{10} = 1024$, which is *almost* 1000. That near-miss caused decades of confusion.

- **Memory** is addressed in powers of two, so 1 KB has always meant **1024** bytes.
- **Storage manufacturers** use SI prefixes: 1 GB means **1,000,000,000** bytes.

**So a "1 TB" drive shows as about 931 GB in an operating system that divides by 1024 three times.** Nobody is lying; two different definitions are in use.

The IEC introduced **kibibyte (KiB) = 1024** and **kilobyte (KB) = 1000** to fix this in 1998. Adoption has been partial at best, so you still have to ask which is meant.

## 4. Practice — independent task

- **(a)** Write out the powers of two from $2^0$ to $2^{16}$ from memory, then check.
- **(b)** Convert these to decimal by eye, without long division: `1111`, `10000`, `10101010`, `11111111`.
- **(c)** A colour is stored as three bytes, one each for red, green and blue. How many distinct colours? Express it as a power of two and in decimal.
- **(d)** An IPv4 address is 32 bits. How many addresses exist? Why did that turn out to be too few, and how many does IPv6's 128 bits give?
- **(e)** A drive is advertised as 2 TB. What will an operating system that divides by 1024 report? Show the arithmetic.

**Done when:** you can convert small binary by sight, and can explain the 2 TB discrepancy in one sentence with the numbers.

<details><summary>Hint for (c) and (d) — open only after an attempt</summary>
Three bytes is 24 bits, so $2^{24} = 16{,}777{,}216$ colours — which is where "16 million colours" and "24-bit colour" both come from, and they are the same claim.<br><br>
IPv4's $2^{32} \approx 4.3$ billion looked limitless in 1981 and ran out because every device wants one. IPv6's $2^{128}$ is about $3.4 \times 10^{38}$ — enough to give every atom on Earth's surface several addresses. <strong>The jump is not 4× — it is squaring, twice.</strong>
</details>

## Before moving on

- [ ] Read small binary numerals by sight using the powers of two.
- [ ] State what a bit, nibble, byte and word are.
- [ ] Explain why a byte holds 256 values.
- [ ] Explain the KB-versus-KiB discrepancy with arithmetic.

**Recap:** Binary uses two digits, with each place worth twice the last. Knowing the powers of two makes small binary readable by sight, and explains several fixed numbers in computing — 256 values per byte, 65,536 for 16 bits, and the 4 GB ceiling of 32-bit addressing. A byte is 8 bits and a nibble is 4, which is exactly one hex digit. Because $2^{10}$ is 1024 rather than 1000, memory and storage use different definitions of "kilo", which is why drives appear smaller than advertised.

**Next:** [[03-decimal|Decimal]] — the base you already use, examined for why it was chosen and why it is not special.

## Related

- [[01-introduction|Number bases]] · [[04-hexadecimal|Hexadecimal]]
- [[foundations/how-computers-work/01-electricity/05-the-digital-abstraction|How Computers Work — the digital abstraction]]
