# Module: Bit Manipulation (Binary Operations & Space Optimization)

Welcome to the **Bit Manipulation** module. Every integer in a computer is stored as a sequence of binary digits (bits)—zeros and ones. Bit manipulation operates *directly* on those binary digits using special bitwise operators, bypassing the usual arithmetic layer entirely.

Mastering bit manipulation lets you solve problems with **$O(1)$ space** that would otherwise need hash sets or extra arrays, and unlocks powerful tricks for parity checking, power-of-two detection, and encoding subsets.

---

## 1. Real-World Motivation & Physical Metaphors

Think of an 8-bit integer as a **row of 8 light switches**:

```
Decimal 53:  Binary = 0 0 1 1 0 1 0 1
                      ↑             ↑
                   Bit 7         Bit 0
                 (Most              (Least
               Significant)      Significant)
```

- **Turning on switch 2 (OR)**: Sets bit 2 to 1, regardless of its current state.
- **Turning off switch 2 (AND NOT)**: Forces bit 2 to 0.
- **Flipping switch 2 (XOR)**: Toggles bit 2 between 0 and 1.

### Real-World Applications:
1. **Network Subnet Masks**: `IP & MASK` extracts the network address portion using bitwise AND.
2. **Permission Systems (Linux chmod)**: File permissions are stored as 3-bit groups (read=4, write=2, execute=1) operated on with OR, AND, XOR.
3. **Game Engine State Flags**: Storing 32 independent boolean game states in a single 32-bit integer.
4. **Cryptography**: XOR-based stream ciphers and hash functions.

---

## 2. Plain-English Terminology & Concept Table

| Operator | Symbol | Behavior | Example (4-bit) |
| :--- | :--- | :--- | :--- |
| **AND** | `&` | Output 1 only if **both** inputs are 1. | `1100 & 1010 = 1000` |
| **OR** | `\|` | Output 1 if **either** input is 1. | `1100 \| 1010 = 1110` |
| **XOR** | `^` | Output 1 only if inputs **differ**. | `1100 ^ 1010 = 0110` |
| **NOT** | `~` | **Flips** every bit (two's complement: `~x = -x - 1`). | `~0101 = 1010` |
| **Left Shift** | `<<` | Shift bits left, fill 0s on right → **multiplies by $2^n$**. | `0011 << 2 = 1100` |
| **Right Shift** | `>>` | Shift bits right, discard low bits → **divides by $2^n$ (floor)**. | `1100 >> 1 = 0110` |

---

## 3. XOR — The Core Workhorse

XOR has three properties that drive most interview bit tricks:

```
x ^ 0 = x          (XOR with 0 is identity — no change)
x ^ x = 0          (XOR with self cancels to 0)
XOR is commutative & associative  (order doesn't matter)
```

**The Consequence**: XOR the entire array → every value that appears an **even number of times cancels to 0**, leaving only the odd-count survivor:

```python
# Find the single non-duplicate element in O(n) time, O(1) space
def single_number(nums: list) -> int:
    result = 0
    for n in nums:
        result ^= n
    return result

# Example: [4, 1, 2, 1, 2]
# 4 ^ 1 ^ 2 ^ 1 ^ 2 = 4 ^ (1^1) ^ (2^2) = 4 ^ 0 ^ 0 = 4 ✓
```

---

## 4. The Essential Bit Manipulation Idioms

```python
# 1. Check if bit i is set (nonzero = True)
(x >> i) & 1       # Shift i right, then check lowest bit

# 2. Set bit i to 1
x | (1 << i)       # Create mask with only bit i set, OR it in

# 3. Clear bit i to 0
x & ~(1 << i)      # Create mask with bit i cleared, AND it in

# 4. Toggle (flip) bit i
x ^ (1 << i)       # XOR with mask flips only bit i

# 5. Check if x is even or odd
x & 1              # 0 = even, 1 = odd

# 6. Check if x is a power of two (exactly ONE bit set)
x > 0 and (x & (x - 1)) == 0

# 7. Clear the LOWEST set bit (Brian Kernighan's trick)
x & (x - 1)       # Subtracting 1 flips lowest set bit and all below it; AND erases them

# 8. Isolate the LOWEST set bit only
x & (-x)           # All other bits zeroed out
```

---

## 5. Deep Dive: Brian Kernighan's Bit Count

> [!KEY-INSIGHT]
> **`x & (x - 1)` always clears exactly the lowest set bit**.
>
> When you subtract 1 from `x`, the lowest set bit flips to 0 and all bits below it flip to 1. ANDing with the original `x` then clears that bit and all below it in one operation.

```python
def count_set_bits(x: int) -> int:
    """O(number of set bits) — Brian Kernighan's Algorithm."""
    count = 0
    while x:
        x &= (x - 1)  # Clear lowest set bit each iteration
        count += 1
    return count

# Example: x = 12 = 1100₂
# Iteration 1: 1100 & 1011 = 1000  (cleared bit 2)
# Iteration 2: 1000 & 0111 = 0000  (cleared bit 3)
# count = 2 ✓ (12 has two set bits)
```

---

## 6. Time & Space Complexity

| Technique | Time | Space | Benefit |
| :--- | :--- | :--- | :--- |
| **Any single bit operation** | $O(1)$ | $O(1)$ | Direct hardware instruction. |
| **Brian Kernighan bit count** | $O(k)$ where $k$ = set bits | $O(1)$ | Faster than looping all 32 bits. |
| **XOR single-number trick** | $O(n)$ | **$O(1)$** | Eliminates need for hash set. |
| **Bitmask DP (subset enumeration)** | $O(2^n \cdot n)$ | $O(2^n)$ | Encodes all subsets of ≤20 elements in integers. |

---

## 7. Common Pitfalls & Traps

1. **Operator Precedence Trap**: Bitwise operators bind **looser** than `==` and `+`. Always parenthesize:
   - **Wrong**: `x & 1 == 0` (evaluates as `x & (1 == 0)` = `x & False` = 0)
   - **Correct**: `(x & 1) == 0`
2. **Python Arbitrary Precision**: Python integers have unlimited bit width with no natural 32-bit overflow. Problems requiring 32-bit behavior (like "Reverse Bits") need explicit `& 0xFFFFFFFF` masking.
3. **`~x` is `-x - 1` in Two's Complement**: In Python, `~5 = -6`, not `2` (which you might expect in 4-bit arithmetic).
4. **XOR only works for odd-count uniqueness**: If the "unique" element appears 3 times (not just once) among elements appearing 2 times, plain XOR won't isolate it. You need bit-count-mod-3 tricks.

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: Using only XOR (`^`), how would you swap two integer variables `a` and `b` without using a temporary variable?
   - <details><summary>Click for Answer</summary><b>Answer:</b><br><code>a = a ^ b</code><br><code>b = a ^ b</code>  (now b = original a)<br><code>a = a ^ b</code>  (now a = original b)</details>

2. **Question**: Why does `x & (x - 1)` clear exactly the lowest set bit of `x`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Subtracting 1 from <code>x</code> flips the lowest set bit from 1 → 0, and sets all bits below it to 1 (binary borrowing). ANDing with the original <code>x</code> then zeros out that bit and all bits below it (which were already 0 in <code>x</code>).</details>

3. **Question**: How would you check if an integer `x` is a power of two using bit manipulation?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>x > 0 and (x & (x - 1)) == 0</code>. Powers of two have exactly one set bit. <code>x & (x - 1)</code> clears the lowest set bit, so the result is 0 if and only if <code>x</code> had exactly one set bit.</details>

---

## Related Modules
- [[07-number-theory-basics|Number Theory Basics]] — Arithmetic cousin (GCD, primality, modular arithmetic)
- [[01-algorithms|Algorithms & Complexity Analysis]] — Space vs. time tradeoffs
