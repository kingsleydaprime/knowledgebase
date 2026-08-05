# Edit Distance

**LeetCode 72** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return the minimum number of operations (insert, delete, replace a character) to turn `word1` into `word2`.

```
"horse" -> "ros"  ->  3   (replace h→r, delete r, delete e)
```

## The recurrence — three edits, one grid

`dp[i][j]` = edits to convert `word1[i:]` into `word2[j:]`. If the current characters **match**, no cost — take the diagonal `dp[i+1][j+1]`. Otherwise it's `1 +` the cheapest of the three operations, each corresponding to a neighbor cell:

- **delete** `word1[i]` → `dp[i+1][j]`
- **insert** `word2[j]` → `dp[i][j+1]`
- **replace** → `dp[i+1][j+1]`

```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][n] = m - i                   # delete the rest of word1
    for j in range(n + 1):
        dp[m][j] = n - j                   # insert the rest of word2
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if word1[i] == word2[j]:
                dp[i][j] = dp[i + 1][j + 1]                # match -> free diagonal
            else:
                dp[i][j] = 1 + min(dp[i+1][j],            # delete
                                   dp[i][j+1],            # insert
                                   dp[i+1][j+1])          # replace
    return dp[0][0]
```

**Time O(m·n), space O(m·n)** (reducible to O(n)).

## Each operation is a direction

The elegance: the three edit operations map exactly to the three neighbor cells — delete (down), insert (right), replace (diagonal). Matching characters cost nothing and slide down the diagonal. The base cases (`dp[i][n]`, `dp[m][j]`) are pure deletions/insertions to reach the empty string.

## Key insight

**Transforming one string into another with per-character operations → the two-string grid, `1 + min` of the three neighbors on a mismatch.** Edit Distance is the "min-cost" member of the [[112-longest-common-subsequence|LCS]] family — the most-tested 2-D DP, and the model for diff/spell-check/alignment.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- family: [[112-longest-common-subsequence|LCS]], [[118-distinct-subsequences|Distinct Subsequences]]
- prev: [[118-distinct-subsequences|Distinct Subsequences]] · next: [[120-burst-balloons|Burst Balloons]]
