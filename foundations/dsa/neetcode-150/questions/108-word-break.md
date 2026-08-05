# Word Break

**LeetCode 139** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Given a string `s` and a dictionary `wordDict`, return whether `s` can be segmented into a space-separated sequence of dictionary words.

```
s = "leetcode", wordDict = ["leet","code"]  ->  true
s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]  ->  false
```

## The recurrence

`dp[i]` = "can `s[i:]` be fully segmented?" It's true if some dictionary word matches a prefix `s[i:j]` **and** the remainder `dp[j]` is also segmentable. `dp[n] = True` (empty string).

## Approach — bottom-up (optimal)

```python
def wordBreak(s, wordDict):
    words = set(wordDict)                  # O(1) membership
    n = len(s)
    dp = [False] * (n + 1)
    dp[n] = True                           # empty suffix is trivially segmentable
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if s[i:j] in words and dp[j]:
                dp[i] = True
                break                      # one valid split suffices
    return dp[0]
```

**Time O(n² · L) (substring checks), space O(n).**

## Why DP, not greedy

Greedily matching the longest prefix can strand you (`"catsandog"`: taking `"cats"` blocks a valid path that needs `"cat"`). DP tries **all** split points, and `dp[j]` reuses the already-computed answer for the remainder — the overlapping-subproblem win. `dp[i] = (exists a word prefix) AND (rest is segmentable)`.

## Key insight

**"Can this sequence be split into valid pieces?" → DP where `dp[i]` depends on a valid first piece + `dp[past that piece]`.** A boolean segmentation DP; the same shape underlies sentence/expression parsing and [[077-palindrome-partitioning|palindrome partitioning]]'s feasibility.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- prev: [[107-maximum-product-subarray|Maximum Product Subarray]] · next: [[109-longest-increasing-subsequence|Longest Increasing Subsequence]]
