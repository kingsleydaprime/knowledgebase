# Permutation in String

**LeetCode 567** · Sliding Window · concept: [[03-sliding-window|sliding-window]]

## Problem

Return `true` if `s2` contains a **permutation of `s1`** as a contiguous substring.

```
s1 = "ab", s2 = "eidbaooo"  -> true  ("ba")
s1 = "ab", s2 = "eidboaoo"  -> false
```

## Approach — fixed-size window, compare char counts (optimal)

A permutation of `s1` is any substring of length `len(s1)` with the **same character counts**. So slide a window of exactly that width across `s2` and check whether its count vector matches `s1`'s.

```python
from collections import Counter

def checkInclusion(s1, s2):
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window = Counter(s2[:len(s1)])
    if window == need:
        return True
    for r in range(len(s1), len(s2)):
        window[s2[r]] += 1                 # add the new right char
        left = s2[r - len(s1)]
        window[left] -= 1                  # drop the char leaving on the left
        if window[left] == 0:
            del window[left]               # keep Counters comparable
        if window == need:
            return True
    return False
```

**Time O(n), space O(1)** (26-letter counts). This is a **fixed-size** window — unlike the variable windows above, the width never changes; you add one char and remove one each step.

## Optimization to O(1) per step

Comparing two Counters is O(26). To make each step true O(1), track a `matches` counter of how many of the 26 letters currently have equal counts, updating it incrementally as chars enter/leave — the answer is found when `matches == 26`.

## Key insight

**"Contains a permutation / anagram of X" → fixed-width window + character-count equality.** Anagram = equal multiset ([[002-valid-anagram|Valid Anagram]]); sliding a fixed window turns "is there an anagram anywhere" into a rolling count comparison.

## Related
- concept: [[03-sliding-window|sliding-window]]; builds on [[002-valid-anagram|Valid Anagram]]
- prev: [[017-longest-repeating-character-replacement|Longest Repeating Character Replacement]] · next: [[019-minimum-window-substring|Minimum Window Substring]]
