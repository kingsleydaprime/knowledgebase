# Decode Ways

**LeetCode 91** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

`A`–`Z` map to `1`–`26`. Count how many ways a digit string can be decoded.

```
"12"   ->  2   ("AB" = 1,2  or  "L" = 12)
"226"  ->  3   (2 2 6, 22 6, 2 26)
```

## The recurrence — take one digit or two

At position `i`, the number of decodings is: ways from `i+1` if `s[i]` is a valid single digit (`1`–`9`), **plus** ways from `i+2` if `s[i:i+2]` is a valid pair (`10`–`26`).

```python
def numDecodings(s):
    n = len(s)
    # dp[i] = ways to decode s[i:]; dp[n] = 1 (empty string)
    two_ahead, one_ahead = 0, 1            # dp[i+2], dp[i+1]
    for i in range(n - 1, -1, -1):
        cur = 0
        if s[i] != "0":                    # single digit 1-9
            cur += one_ahead
        if i + 1 < n and (s[i] == "1" or (s[i] == "2" and s[i+1] <= "6")):
            cur += two_ahead               # valid pair 10-26
        two_ahead, one_ahead = one_ahead, cur
    return one_ahead
```

**Time O(n), space O(1).**

## The `0` and `>26` traps

- A leading `"0"` decodes to nothing (`0` and `27`+ have no letter), so `s[i] == "0"` contributes 0 single-digit ways.
- A pair is valid only if it's `10`–`26`: first digit `1` (any second), or `2` with second ≤ `6`.

These validity checks are where the bugs live; the recurrence itself is Fibonacci-shaped (each state sums the next one or two).

## Key insight

**"Number of ways to segment a sequence" → DP summing over valid next-chunk sizes.** Here chunks are 1 or 2 digits gated by validity — the same "one-or-two step" shape as [[099-climbing-stairs|Climbing Stairs]], but with feasibility conditions on each step.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- prev: [[104-palindromic-substrings|Palindromic Substrings]] · next: [[106-coin-change|Coin Change]]
