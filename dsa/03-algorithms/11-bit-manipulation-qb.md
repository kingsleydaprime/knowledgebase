# Bit Manipulation — Question Bank

Micro-questions over [[11-bit-manipulation|the bit manipulation module]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. The mental model

**1. Give the physical metaphor for an 8-bit integer.**

<details><summary>Answer</summary>

**A row of 8 light switches.** Bit 0 is the least significant, bit 7 the most.

</details>

**2. What operation turns a switch on, off, and flips it?**

<details><summary>Answer</summary>

**On**: OR. **Off**: AND NOT. **Flip**: XOR.

</details>

**3. Name four real applications.**

<details><summary>Answer</summary>

Network subnet masks (`IP & MASK`); Linux file permissions as 3-bit groups (read=4, write=2, execute=1); 32 independent game state flags in one integer; XOR-based stream ciphers and hashes.

</details>

---

## B. The operators

**4. Define AND, OR and XOR by their output rule.**

<details><summary>Answer</summary>

**AND (`&`)**: 1 only if **both** inputs are 1. **OR (`|`)**: 1 if **either** is 1. **XOR (`^`)**: 1 only if the inputs **differ**.

</details>

**5. What does `~x` equal?**

<details><summary>Answer</summary>

It flips every bit, which in two's complement means **$-x - 1$**. In Python `~5 = -6`, not 2.

</details>

**6. What do `<<` and `>>` do arithmetically?**

<details><summary>Answer</summary>

`<< n` **multiplies by $2^n$**; `>> n` **divides by $2^n$ (floor)**, discarding the low bits.

</details>

---

## C. XOR

**7. Give the three properties of XOR.**

<details><summary>Answer</summary>

$x \oplus 0 = x$ (identity); $x \oplus x = 0$ (self-cancelling); **commutative and associative** — order does not matter.

</details>

**8. What is the consequence for an array?**

<details><summary>Answer</summary>

XOR everything together and **every value appearing an even number of times cancels to 0**, leaving only the odd-count survivor.

</details>

**9. Trace `[4,1,2,1,2]`.**

<details><summary>Answer</summary>

$4 \oplus (1\oplus1) \oplus (2\oplus2) = 4 \oplus 0 \oplus 0 = 4$.

</details>

**10. What does that buy over a hash set?**

<details><summary>Answer</summary>

$O(n)$ time at **$O(1)$ space** instead of $O(n)$.

</details>

**11. Swap two integers using only XOR.**

<details><summary>Answer</summary>

```python
a = a ^ b
b = a ^ b   # now b = original a
a = a ^ b   # now a = original b
```

</details>

**12. When does the XOR trick fail?**

<details><summary>Answer</summary>

**When the unique element appears an even number of times**, or when the duplicates appear 3 times rather than 2. Then you need bit-count-mod-3 tricks.

</details>

---

## D. The idioms

**13. Check whether bit $i$ is set.**

<details><summary>Answer</summary>

`(x >> i) & 1`

</details>

**14. Set, clear and toggle bit $i$.**

<details><summary>Answer</summary>

Set: `x | (1 << i)`. Clear: `x & ~(1 << i)`. Toggle: `x ^ (1 << i)`.

</details>

**15. Test even or odd.**

<details><summary>Answer</summary>

`x & 1` — 0 is even, 1 is odd.

</details>

**16. Test whether `x` is a power of two.**

<details><summary>Answer</summary>

`x > 0 and (x & (x - 1)) == 0` — exactly one bit set.

</details>

**17. Clear the lowest set bit, and isolate it.**

<details><summary>Answer</summary>

Clear: `x & (x - 1)`. Isolate: `x & (-x)`.

</details>

---

## E. Brian Kernighan

**18. Why does `x & (x - 1)` clear exactly the lowest set bit?**

<details><summary>Answer</summary>

**Subtracting 1 flips the lowest set bit to 0 and all bits below it to 1.** ANDing with the original then clears that bit and all below it.

</details>

**19. Trace it on 12.**

<details><summary>Answer</summary>

$1100 \,\&\, 1011 = 1000$ (cleared bit 2); $1000 \,\&\, 0111 = 0000$ (cleared bit 3). **Count = 2.**

</details>

**20. What is the cost, and why is it better than the naive loop?**

<details><summary>Answer</summary>

$O(k)$ where $k$ is the number of **set** bits — rather than looping all 32 regardless.

</details>

---

## F. Costs

**21. Give the four complexity rows.**

<details><summary>Answer</summary>

Single bit op: $O(1)$ — a direct hardware instruction. Kernighan count: $O(k)$, $O(1)$ space. XOR single-number: $O(n)$, **$O(1)$ space**. Bitmask DP: $O(2^n \cdot n)$ time, $O(2^n)$ space — for $n \le 20$.

</details>

---

## G. Traps

**22. What is wrong with `x & 1 == 0`?**

<details><summary>Answer</summary>

**Bitwise operators bind looser than `==`**, so it evaluates as `x & (1 == 0)` = `x & False` = 0. Write `(x & 1) == 0`.

</details>

**23. What breaks in Python for 32-bit problems?**

<details><summary>Answer</summary>

**Python integers have unlimited bit width with no natural overflow.** Problems like "Reverse Bits" need explicit `& 0xFFFFFFFF` masking.

</details>

**24. Summarise the module in one sentence.**

<details><summary>Answer</summary>

Treat an integer as a row of switches — XOR cancels pairs, `x & (x-1)` erases the lowest set bit, and every idiom is one hardware instruction.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[11-bit-manipulation|Bit Manipulation]] — the module
- [[07-number-theory-basics-qb|Number Theory Basics — Question Bank]]
- [[12-math-and-geometry-qb|Math & Geometry — Question Bank]]
