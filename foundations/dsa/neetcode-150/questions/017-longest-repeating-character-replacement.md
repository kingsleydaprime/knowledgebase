# Longest Repeating Character Replacement

**LeetCode 424** · Sliding Window · concept: [[03-sliding-window|sliding-window]]

## Problem

Given a string `s` and integer `k`, you may replace up to `k` characters with any letter. Return the length of the longest substring of a **single repeated character** you can achieve.

```
s = "AABABBA", k = 1  ->  4   (replace one B in "AABA"→"AAAA", or "ABBB")
```

## The key formula

A window is **valid** if the characters you'd have to replace fit within `k`:

```
(window length) − (count of the most frequent char in the window) ≤ k
```

That left term is "how many chars aren't the majority" — exactly how many replacements you'd need. Grow the window while valid; shrink when not.

```python
def characterReplacement(s, k):
    count = {}
    l = 0
    max_freq = 0
    best = 0
    for r in range(len(s)):
        count[s[r]] = count.get(s[r], 0) + 1
        max_freq = max(max_freq, count[s[r]])
        while (r - l + 1) - max_freq > k:      # too many replacements needed
            count[s[l]] -= 1
            l += 1
        best = max(best, r - l + 1)
    return best
```

**Time O(n), space O(alphabet).**

## Why `max_freq` never needing a decrease is fine

It looks like a bug that `max_freq` isn't recomputed when the window shrinks. It isn't: the answer `best` only ever grows, and it can only grow when `max_freq` grows. A stale (too-high) `max_freq` might keep the window one size too long, but it never *shrinks* `best` below a previously valid length — so the maximum is still correct. This subtlety is the whole interview point.

## Key insight

**Window validity = "characters to change ≤ budget," i.e. `len − maxFreq ≤ k`.** Reframing "replace k chars" as "the non-majority count must fit in k" is the move; the window mechanics are then the standard grow/shrink template.

## Related
- concept: [[03-sliding-window|sliding-window]]
- prev: [[016-longest-substring-without-repeating-characters|Longest Substring Without Repeating]] · next: [[018-permutation-in-string|Permutation in String]]
