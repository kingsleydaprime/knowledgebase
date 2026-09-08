# Missing Number

**LeetCode 268** · Bit Manipulation · concept: [[13-bit-manipulation|bit-manipulation]]

## Problem

An array holds `n` distinct numbers from the range `[0, n]`. Find the one missing.

```
[3,0,1]  ->  2
[0,1]    ->  2
```

## Approach 1 — XOR indices with values (optimal, O(1) space)

XOR every index `0…n` together with every array value. Each present number cancels with its own index; the **missing** number has an index but no matching value, so it survives.

```python
def missingNumber(nums):
    result = len(nums)                     # start with n (the top index, absent as a value)
    for i, num in enumerate(nums):
        result ^= i ^ num                  # cancel matching index/value pairs
    return result
```

**Time O(n), space O(1).**

## Approach 2 — Gauss sum

The sum `0 + 1 + … + n = n(n+1)/2`; subtract the array's actual sum and the difference is the missing number. Equally O(n)/O(1), but can overflow in fixed-width languages (XOR never does).

## Why XOR isolates the gap

Pairing each index with its value, `result` XORs together `0^0 ^ 1^1 ^ …` for every present number — all cancel — plus the missing number's index, which has no value to cancel it. Seeding with `n` covers the top index (which is never an array value when the range is `[0, n]`). It's [[144-single-number|Single Number]]'s cancellation applied to index/value pairs.

## Key insight

**"One missing from a complete range" → XOR indices against values so matched pairs cancel** (or use the arithmetic-series sum). The XOR form avoids overflow and needs no extra space — the cleaner of the two.

## Related
- concept: [[13-bit-manipulation|bit-manipulation]]
- relative: [[144-single-number|Single Number]]
- prev: [[147-reverse-bits|Reverse Bits]] · next: [[149-sum-of-two-integers|Sum of Two Integers]]
