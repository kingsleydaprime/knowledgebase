# Longest Palindromic Substring

**LeetCode 5** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Return the longest contiguous substring that is a palindrome.

```
"babad"  ->  "bab" (or "aba")
"cbbd"   ->  "bb"
```

## Approach — expand around center (optimal for space)

A palindrome mirrors around a center. There are `2n − 1` centers (each character, and each gap between characters, for even-length palindromes). From each, expand outward while the characters match, tracking the longest.

```python
def longestPalindrome(s):
    res = ""
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return s[l+1:r]                    # the palindrome between the last matching bounds

    for i in range(len(s)):
        odd = expand(i, i)                 # odd-length, center at i
        even = expand(i, i + 1)            # even-length, center between i and i+1
        res = max(res, odd, even, key=len)
    return res
```

**Time O(n²), space O(1).**

## Two center types

Odd-length palindromes have a single-character center (`expand(i, i)`); even-length ones center on a gap (`expand(i, i+1)`). Checking both from every index covers all `2n−1` centers. The DP-table approach (`dp[i][j]` = is `s[i:j+1]` a palindrome) is also O(n²) but O(n²) space; expand-around-center is the same time with O(1) space. (Manacher's algorithm reaches O(n) but is rarely expected.)

## Key insight

**Palindrome problems → expand around each of the 2n−1 centers.** Growing outward from a center is often simpler and more space-efficient than filling a 2-D DP table, and it directly powers [[104-palindromic-substrings|Palindromic Substrings]] (count instead of longest).

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- prev: [[102-house-robber-ii|House Robber II]] · next: [[104-palindromic-substrings|Palindromic Substrings]]
