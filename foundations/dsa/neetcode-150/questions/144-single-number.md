# Single Number

**LeetCode 136** · Bit Manipulation · concept: [[13-bit-manipulation|bit-manipulation]]

## Problem

Every element appears **twice** except one. Find that single element — in O(n) time and **O(1) space**.

```
[4,1,2,1,2]  ->  4
```

## Approach — XOR everything (optimal)

XOR has three magic properties: `x ^ x = 0`, `x ^ 0 = x`, and it's commutative/associative. So XOR-ing the whole array cancels every value that appears an **even** number of times, leaving only the lone element.

```python
def singleNumber(nums):
    result = 0
    for n in nums:
        result ^= n            # duplicates cancel to 0; the unique one survives
    return result
```

**Time O(n), space O(1).**

## Why the pairs vanish

Because XOR is order-independent, the array effectively regroups as `(a^a) ^ (b^b) ^ … ^ unique`. Each duplicate pair XORs to 0, and `0 ^ unique = unique`. A hash set also works but costs O(n) space — XOR is the O(1)-space win that makes this a bit-manipulation classic.

## Key insight

**"Find the element with odd multiplicity" → XOR the whole collection; even-count values self-cancel.** This XOR-sum trick reappears in [[148-missing-number|Missing Number]] and any "find the unpaired value" problem — the single most useful bit identity.

## Related
- concept: [[13-bit-manipulation|bit-manipulation]]
- relative: [[148-missing-number|Missing Number]]
- next: [[145-number-of-1-bits|Number of 1 Bits]]
