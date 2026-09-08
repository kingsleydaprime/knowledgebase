# Regular Expression Matching

**LeetCode 10** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Implement regex matching for `.` (any single char) and `*` (zero or more of the **preceding** element), matching the **entire** string.

```
s = "aab", p = "c*a*b"  ->  true
s = "mississippi", p = "mis*is*p*."  ->  false
```

## The recurrence — the `*` is the hard case

`dp[i][j]` = does `s[i:]` match `p[j:]`? A single char/`.` matches when `p[j]` equals `s[i]` (or is `.`) and the rest matches. The `*` (which pairs with `p[j-1]`) branches two ways:

- **zero occurrences** — skip `p[j]` and `p[j+1]`: `dp[i][j+2]`
- **one+ occurrence** — if `p[j]` matches `s[i]`, consume `s[i]` and stay on the pattern: `dp[i+1][j]`

```python
def isMatch(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[m][n] = True                        # empty string matches empty pattern
    for i in range(m, -1, -1):
        for j in range(n - 1, -1, -1):
            first = i < m and p[j] in (s[i], ".")
            if j + 1 < n and p[j + 1] == "*":
                dp[i][j] = dp[i][j + 2] or (first and dp[i + 1][j])   # zero, or one+
            else:
                dp[i][j] = first and dp[i + 1][j + 1]                 # single match
    return dp[0][0]
```

**Time O(m·n), space O(m·n).**

## The two branches of `*`

`x*` means "zero or more x." **Zero**: ignore both `x` and `*`, jump the pattern by 2. **One or more**: if `x` matches the current character, consume that character but keep the `x*` in play (it might match again). Every regex-DP bug lives in getting these two branches — and the "match current char" guard — right.

## Key insight

**Wildcard/regex matching → 2-D DP where `*` splits into "use zero of the preceding" vs. "use one and stay."** It's the most intricate two-string DP (Wildcard Matching, LC 44, is a simpler cousin) — the payoff of mastering the family's grid before tackling the `*` branching.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- family: [[112-longest-common-subsequence|LCS]], [[119-edit-distance|Edit Distance]]
- prev: [[120-burst-balloons|Burst Balloons]] — end of 2-D DP
- next category: Greedy
