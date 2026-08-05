# Distinct Subsequences

**LeetCode 115** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Count how many **distinct subsequences** of `s` equal `t`.

```
s = "rabbbit", t = "rabbit"  ->  3
```

## The recurrence

`dp[i][j]` = number of ways `t[j:]` appears as a subsequence of `s[i:]`. When characters match, you may either **use** `s[i]` to match `t[j]` (advance both) **or skip** `s[i]` (advance only `s`); when they don't match, you can only skip `s[i]`.

```python
def numDistinct(s, t):
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][n] = 1                       # matched all of t -> one way (empty target)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            dp[i][j] = dp[i + 1][j]        # skip s[i]
            if s[i] == t[j]:
                dp[i][j] += dp[i + 1][j + 1]   # also use s[i] to match t[j]
    return dp[0][0]
```

**Time O(m·n), space O(m·n)** (reducible to O(n)).

## The "use it or skip it" on a match

The subtlety versus [[112-longest-common-subsequence|LCS]]: on a match you **sum both choices** (use `s[i]` *and* skip it are distinct ways), because you're **counting** subsequences, not measuring length. The base case `dp[i][n] = 1` means "fully matched `t`" — one valid subsequence, regardless of leftover `s`.

## Key insight

**Counting subsequence matches → two-string grid where a match *adds* (use + skip) and a mismatch *carries* (skip only).** It's LCS's grid with summation instead of max — the recurring theme that the whole two-string DP family shares a skeleton, differing only in the cell operation.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- family: [[112-longest-common-subsequence|LCS]], [[119-edit-distance|Edit Distance]]
- prev: [[117-longest-increasing-path-in-a-matrix|Longest Increasing Path in a Matrix]] · next: [[119-edit-distance|Edit Distance]]
