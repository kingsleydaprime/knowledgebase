# Interleaving String

**LeetCode 97** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return whether `s3` is formed by **interleaving** `s1` and `s2` (both used entirely, relative order preserved).

```
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"  ->  true
```

## The recurrence — a 2-D reachability grid

`dp[i][j]` = "can `s3[:i+j]` be formed from `s1[:i]` and `s2[:j]`?" You reach `(i, j)` if either:

- the last char came from `s1`: `dp[i-1][j]` and `s1[i-1] == s3[i+j-1]`, or
- the last char came from `s2`: `dp[i][j-1]` and `s2[j-1] == s3[i+j-1]`.

```python
def isInterleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            if i > 0 and s1[i-1] == s3[i+j-1]:
                dp[i][j] = dp[i][j] or dp[i-1][j]     # took a char from s1
            if j > 0 and s2[j-1] == s3[i+j-1]:
                dp[i][j] = dp[i][j] or dp[i][j-1]     # took a char from s2
    return dp[m][n]
```

**Time O(m·n), space O(m·n)** (reducible to O(n)).

## Why greedy fails

At a position where both `s1` and `s2` offer the needed character, greedy can't know which to take — a wrong pick dead-ends. The 2-D DP explores **both** consumption paths, and `i + j` is exactly how far into `s3` you are, tying the two indices to one position in the output.

## Key insight

**"Can two sequences interleave into a third?" → 2-D reachability DP indexed by how much of each source is consumed** (with `i+j` locating the target position). Whenever a wrong local choice can strand a greedy solution, a 2-D DP that keeps both options alive is the fix.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- family: [[112-longest-common-subsequence|Longest Common Subsequence]] (two-sequence grid)
- prev: [[115-target-sum|Target Sum]] · next: [[117-longest-increasing-path-in-a-matrix|Longest Increasing Path in a Matrix]]
