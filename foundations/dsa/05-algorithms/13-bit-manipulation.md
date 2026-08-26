# Bit Manipulation

Bit manipulation operates on the individual binary digits of an integer directly, using the bitwise operators. It shows up in interviews as a category of its own because a handful of tricks turn problems that look like they need extra space or a full pass into O(1)-space, single-expression solutions — and because the underlying representation ([[foundations/programming-fundamentals/15-how-types-actually-work|how integers are stored as bits]]) is fair game to test.

## The operators

| Op | Name | Effect | Example (4-bit) |
|---|---|---|---|
| `&` | AND | 1 only where **both** bits are 1 | `1100 & 1010 = 1000` |
| `\|` | OR | 1 where **either** bit is 1 | `1100 \| 1010 = 1110` |
| `^` | XOR | 1 where bits **differ** | `1100 ^ 1010 = 0110` |
| `~` | NOT | flips every bit | `~1100 = ...0011` (with sign) |
| `<<` | left shift | shift left, fill 0 → **×2ⁿ** | `0011 << 1 = 0110` |
| `>>` | right shift | shift right → **÷2ⁿ** (floor) | `0110 >> 1 = 0011` |

## The properties that make tricks work

**XOR is the workhorse.** Three identities do most of the heavy lifting:

- `x ^ 0 = x` (XOR with 0 is identity)
- `x ^ x = 0` (a value XORed with itself cancels)
- XOR is commutative and associative (order doesn't matter)

Together these mean: **XOR the whole list and every value that appears an even number of times cancels to 0, leaving only the odd-one-out.** That's *Single Number* in one line. It's also how you find a missing/duplicate number without a hash set, and how you swap two variables without a temp (`a ^= b; b ^= a; a ^= b`).

## The essential idioms

```python
# Test / set / clear / toggle bit i
x & (1 << i)          # is bit i set?  (nonzero if yes)
x | (1 << i)          # set bit i to 1
x & ~(1 << i)         # clear bit i to 0
x ^ (1 << i)          # toggle bit i

# The two most-tested tricks
x & (x - 1)           # clears the LOWEST set bit  -> loop this to COUNT set bits
x & (-x)              # isolates the LOWEST set bit (all else 0)

# Handy checks
x & 1                 # parity: 1 if odd, 0 if even
x > 0 and (x & (x - 1)) == 0   # is x a power of two? (exactly one set bit)
```

**`x & (x - 1)` deserves special attention.** Subtracting 1 flips the lowest set bit to 0 and sets all bits below it to 1; ANDing with the original therefore *erases exactly the lowest set bit*. Looping `x &= x - 1` and counting iterations counts set bits in O(number-of-set-bits) instead of O(bit-width) — **Brian Kernighan's algorithm**, the *Number of 1 Bits* answer.

## Counting bits for a whole range — DP on bits

*Counting Bits* (bit counts for `0..n`) reveals a neat recurrence bridging bit manipulation and [[foundations/dsa/06-patterns/15-dynamic-programming|DP]]: `count[i] = count[i >> 1] + (i & 1)` — a number has the set-bits of itself-shifted-right, plus one more if it's odd. O(n) instead of O(n log n).

## Addition without `+` — full-adder logic

*Sum of Two Integers* forbids `+`/`-`, forcing you to rebuild addition from bits: `a ^ b` is the sum **without carries**, `(a & b) << 1` is the **carry**; loop until there's no carry left. This is literally how hardware adds, and the classic "do you understand what `+` compiles to" question. (In Python it needs masking to a fixed width because ints are arbitrary-precision — a real gotcha there.)

## Complexity

Most bit tricks are **O(1) time and O(1) space** (fixed 32/64-bit width), or O(bit-width) = O(1) for a fixed integer size. The value they add is usually **space**: replacing a hash set or a second array with a single accumulator (XOR sum, a bitmask). Bitmasks also encode a subset of ≤ ~20 elements in one integer — the enabling trick for subset/DP-over-subsets problems (bitmask DP).

## Canonical problems (NeetCode Bit Manipulation)

- **Single Number** — XOR the whole array; pairs cancel, the unique element remains. O(1) space.
- **Number of 1 Bits** — Brian Kernighan's `x &= x - 1` loop.
- **Counting Bits** — the `count[i] = count[i >> 1] + (i & 1)` DP recurrence.
- **Reverse Bits** — shift bits out of one end and into the other, 32 times.
- **Missing Number** — XOR all indices `0..n` with all values; everything present cancels, leaving the missing one (also solvable by Gauss sum).
- **Sum of Two Integers** — XOR (sum) + AND-shift (carry) loop, no `+`.
- **Reverse Integer** — digit reversal with 32-bit overflow checking (more arithmetic than bitwise, grouped here).

## Gotchas

- **Operator precedence**: `&`, `|`, `^` bind *looser* than `==` and `+` in most languages — parenthesize (`(x & 1) == 0`, not `x & 1 == 0`).
- **Signed shifts and `~`**: `~x == -x - 1` in two's complement; right-shifting negatives is implementation/language-defined (arithmetic vs logical). Know your language.
- **Python ints are arbitrary-precision** — there's no natural 32-bit overflow, so problems assuming fixed width (Sum of Two Integers, Reverse Bits) need explicit `& 0xFFFFFFFF` masking and manual sign handling.
- **XOR only isolates a value that's unique by odd count** — if the "unique" element can appear a different number of times, plain XOR won't find it (those need bit-count-mod-k tricks).
- **Don't reach for bit tricks first** — they're O(1)-space wins on specific structure, not a general tool; a hash map is clearer when space isn't the constraint.

## Related
- [[foundations/programming-fundamentals/15-how-types-actually-work|Data types]] — two's complement, how integers are bits
- [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic programming]] — Counting Bits recurrence; bitmask DP
- [[07-number-theory-basics|Number theory]] — the arithmetic cousin (GCD, primality, modular math)
