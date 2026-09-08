# Number of 1 Bits

**LeetCode 191** · Bit Manipulation · concept: [[13-bit-manipulation|bit-manipulation]]

## Problem

Count the set bits (1s) in the binary representation of an integer (the "Hamming weight").

```
11  (1011)  ->  3
128 (10000000)  ->  1
```

## Approach 1 — check each bit

Shift and mask 32 times: `count += (n >> i) & 1`. Simple, O(number of bits) = O(32).

## Approach 2 — Brian Kernighan's trick (optimal)

`n & (n - 1)` clears the **lowest set bit**. Loop it, counting iterations — you loop exactly once per set bit, not once per bit position.

```python
def hammingWeight(n):
    count = 0
    while n:
        n &= n - 1             # drop the lowest set bit
        count += 1
    return count
```

**Time O(number of set bits), space O(1).**

## Why `n & (n - 1)` clears the lowest 1

Subtracting 1 flips the lowest set bit to 0 and turns all bits below it to 1; ANDing with the original then zeroes exactly that lowest set bit (and leaves the higher bits untouched). So each iteration removes one 1, and the loop runs `popcount(n)` times — faster than scanning all 32 positions when bits are sparse.

## Key insight

**`n & (n - 1)` removes the lowest set bit** — the foundational bit idiom. Kernighan's algorithm counts 1s in O(set bits); the same "peel the lowest bit" move detects powers of two (`n & (n-1) == 0`) and drives the DP in [[146-counting-bits|Counting Bits]].

## Related
- concept: [[13-bit-manipulation|bit-manipulation]]
- prev: [[144-single-number|Single Number]] · next: [[146-counting-bits|Counting Bits]]
