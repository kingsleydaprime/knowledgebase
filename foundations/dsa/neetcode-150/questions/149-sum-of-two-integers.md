# Sum of Two Integers

**LeetCode 371** · Bit Manipulation · concept: [[13-bit-manipulation|bit-manipulation]]

## Problem

Add two integers **without** using `+` or `-`.

```
a = 2, b = 3  ->  5
```

## Approach — XOR for sum, AND-shift for carry (optimal)

Rebuild addition from its hardware primitives. For each bit column: `a ^ b` is the sum **ignoring carries**, and `(a & b) << 1` is the **carry** into the next column. Repeat until there's no carry left.

```python
def getSum(a, b):
    mask = 0xFFFFFFFF                       # 32-bit window (Python ints are unbounded)
    while b & mask:                        # while a carry remains
        a, b = a ^ b, (a & b) << 1         # sum-without-carry, carry
    a &= mask
    # interpret as signed 32-bit
    return a if a <= 0x7FFFFFFF else ~(a ^ mask)
```

**Time O(1)** (≤ 32 carry rounds), **space O(1).**

## Full-adder logic

`a ^ b` sets a bit where exactly one of the inputs has a 1 (sum, no carry); `a & b` finds where **both** are 1 (a carry, which belongs one position higher, hence `<< 1`). Looping propagates carries until they run out — precisely how a hardware ripple-carry adder works. In Python the masking is essential because its ints are arbitrary-precision (no natural 32-bit overflow or sign), so you emulate a fixed-width signed word.

## Key insight

**Addition = XOR (partial sum) + carry (AND, shifted), iterated.** This exposes what `+` actually compiles to, and the same decomposition underlies [[142-multiply-strings|grade-school arithmetic]] and ALU design — the deepest "what is a number operation, really" bit problem.

## Related
- concept: [[13-bit-manipulation|bit-manipulation]]
- prev: [[148-missing-number|Missing Number]] · next: [[150-reverse-integer|Reverse Integer]]
