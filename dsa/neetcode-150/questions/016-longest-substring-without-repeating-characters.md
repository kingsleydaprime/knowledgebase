# Longest Substring Without Repeating Characters

**LeetCode 3** · Sliding Window · concept: [[03-sliding-window|sliding-window]]

## Problem

Return the length of the longest substring with **no repeated characters**.

```
"abcabcbb" -> 3 ("abc")
"bbbbb"    -> 1 ("b")
"pwwkew"   -> 3 ("wke")
```

## Approach — variable-size window with a set (optimal)

Grow a window on the right; the instant it contains a duplicate, shrink from the left until the duplicate is gone. A set holds the current window's characters.

```python
def lengthOfLongestSubstring(s):
    seen = set()
    l = 0
    best = 0
    for r in range(len(s)):
        while s[r] in seen:        # duplicate -> shrink from the left
            seen.remove(s[l])
            l += 1
        seen.add(s[r])
        best = max(best, r - l + 1)
    return best
```

**Time O(n), space O(min(n, alphabet)).** Each index enters and leaves the window at most once, so despite the nested `while`, total work is O(n).

## Variant — jump the left pointer with a map

Storing `char -> last index` lets `l` jump straight past the previous occurrence instead of stepping one at a time: `l = max(l, last[c] + 1)`. Same O(n), fewer iterations.

## Key insight

**"Longest window satisfying a constraint" → grow right, shrink left when the constraint breaks.** This is *the* variable-size sliding-window template; every problem below is a variation on what "the constraint" and "the window state" are.

## Related
- concept: [[03-sliding-window|sliding-window]]
- prev: [[015-best-time-to-buy-and-sell-stock|Best Time to Buy/Sell Stock]] · next: [[017-longest-repeating-character-replacement|Longest Repeating Character Replacement]]
