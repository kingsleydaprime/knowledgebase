# Longest Common Subsequence

**LeetCode 1143** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return the length of the longest subsequence common to two strings (characters in order, not necessarily contiguous).

```
"abcde", "ace"  ->  3   ("ace")
```

## The recurrence — compare two sequences

`dp[i][j]` = LCS of `a[i:]` and `b[j:]`. If the characters **match**, extend the diagonal: `1 + dp[i+1][j+1]`. If not, take the better of dropping one character from either string: `max(dp[i+1][j], dp[i][j+1])`.

```python
def longestCommonSubsequence(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]        # match -> diagonal + 1
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])  # skip a char in a or b
    return dp[0][0]
```

**Time O(m·n), space O(m·n)** (reducible to O(min(m,n)) with two rows).

## The two-sequence grid

The state is a **pair of indices**, one into each string — a grid where `dp[i][j]` reads from three neighbors (diagonal on match, or right/down on mismatch). This is the archetype: Edit Distance, Distinct Subsequences, and Interleaving String are all this grid with different cell rules.

## Key insight

**Comparing two sequences → a 2-D DP indexed by a position in each, match extends the diagonal, mismatch takes the best of dropping one side.** LCS is the template of the whole two-string DP family — learn its grid and the others are variations.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- family: [[119-edit-distance|Edit Distance]], [[118-distinct-subsequences|Distinct Subsequences]]
- prev: [[111-unique-paths|Unique Paths]] · next: [[113-best-time-to-buy-and-sell-stock-with-cooldown|Buy/Sell Stock with Cooldown]]
