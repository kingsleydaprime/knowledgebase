# Reverse Bits

**LeetCode 190** · Bit Manipulation · concept: [[13-bit-manipulation|bit-manipulation]]

## Problem

Reverse the bits of a 32-bit unsigned integer.

```
0000...00101  (43261 in a 32-bit word)  ->  its bit-reversed value
```

## Approach — shift out one end, shift into the other (optimal)

Build the result bit by bit: extract the **lowest** bit of the input and push it onto the **top** of the result. Over 32 iterations, the input drains from the right while the result fills from the left — a mirror.

```python
def reverseBits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)   # make room, drop in n's lowest bit
        n >>= 1                             # advance to n's next bit
    return result
```

**Time O(32) = O(1), space O(1).**

## The mirror mechanic

Each step: `result << 1` opens a new low slot, `| (n & 1)` fills it with the input's current lowest bit, and `n >>= 1` moves on. Because `result` shifts left (bit 0 of input → bit 31 of output on the last of 32 steps), the bit order is reversed. Fixed 32-iteration count makes it O(1). (A divide-and-conquer mask-swap does it in O(log 32) steps.)

## Key insight

**Bit-order reversal → pop the lowest bit of the source and push it as the highest bit of the destination, repeated for the word width.** The "shift out one side, shift in the other" pattern is the same shape as reversing a number's decimal digits ([[150-reverse-integer|Reverse Integer]]) or a linked list.

## Related
- concept: [[13-bit-manipulation|bit-manipulation]]
- relative: [[150-reverse-integer|Reverse Integer]]
- prev: [[146-counting-bits|Counting Bits]] · next: [[148-missing-number|Missing Number]]
