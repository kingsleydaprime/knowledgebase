# Counting Bits

**LeetCode 338** · Bit Manipulation · concepts: [[13-bit-manipulation|bit-manipulation]], [[15-dynamic-programming|dynamic-programming]]

## Problem

For every integer `0 … n`, return the number of set bits. Aim for O(n) total.

```
n = 5  ->  [0,1,1,2,1,2]
```

## Approach — DP off a shifted subproblem (optimal)

Calling [[145-number-of-1-bits|popcount]] on each number is O(n log n). The O(n) trick uses a recurrence: `i` has the same bits as `i >> 1` (drop the lowest bit), **plus one** if `i` is odd (that dropped bit was a 1).

```python
def countBits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)       # bits of i//2, plus the lowest bit of i
    return dp
```

**Time O(n), space O(n).**

## Why the recurrence holds

`i >> 1` is `i` with its lowest bit chopped off, so it has all of `i`'s set bits except possibly that lowest one. `i & 1` recovers whether the chopped bit was set. Since `i >> 1 < i`, `dp[i >> 1]` is already computed — a clean overlapping-subproblem, hence [[15-dynamic-programming|DP]]. (An alternative recurrence, `dp[i] = dp[i & (i-1)] + 1`, uses Kernighan's identity.)

## Key insight

**Bit counts over a range → DP, because a number's popcount relates to a smaller number's (`i>>1` or `i&(i-1)`).** This is a lovely bridge between bit manipulation and dynamic programming — the same result each number's bits build on an already-solved subproblem.

## Related
- concepts: [[13-bit-manipulation|bit-manipulation]], [[15-dynamic-programming|dynamic-programming]]
- builds on: [[145-number-of-1-bits|Number of 1 Bits]]
- prev: [[145-number-of-1-bits|Number of 1 Bits]] · next: [[147-reverse-bits|Reverse Bits]]
