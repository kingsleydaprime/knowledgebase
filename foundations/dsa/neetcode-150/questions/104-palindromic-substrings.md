# Palindromic Substrings

**LeetCode 647** · 1-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Count how many substrings are palindromes (different positions count separately).

```
"aaa"  ->  6   ("a"×3, "aa"×2, "aaa"×1)
```

## Approach — expand around center, count each expansion (optimal)

Identical machinery to [[103-longest-palindromic-substring|Longest Palindromic Substring]], but instead of tracking the longest, **count every** successful expansion — each one is a distinct palindromic substring.

```python
def countSubstrings(s):
    count = 0
    def expand(l, r):
        nonlocal count
        while l >= 0 and r < len(s) and s[l] == s[r]:
            count += 1                     # each valid expansion is one palindrome
            l -= 1
            r += 1

    for i in range(len(s)):
        expand(i, i)                       # odd-length centers
        expand(i, i + 1)                   # even-length centers
    return count
```

**Time O(n²), space O(1).**

## Same skeleton, different accumulator

Longest-palindrome and count-palindromes are the *same* center-expansion traversal — one keeps the best, the other increments a counter. Every step where `s[l] == s[r]` succeeds is exactly one more palindromic substring, so counting is a `+= 1` inside the expand loop.

## Key insight

**Count vs. optimize is usually just a different accumulator over the same traversal.** Once you have the center-expansion structure, "how many palindromes" and "longest palindrome" differ by one line — recognizing this saves re-deriving the approach.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- builds on: [[103-longest-palindromic-substring|Longest Palindromic Substring]]
- prev: [[103-longest-palindromic-substring|Longest Palindromic Substring]] · next: [[105-decode-ways|Decode Ways]]
