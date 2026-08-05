# Minimum Window Substring

**LeetCode 76** · Sliding Window · concept: [[03-sliding-window|sliding-window]]

## Problem

Given strings `s` and `t`, return the **shortest** substring of `s` containing every character of `t` (with multiplicity). Empty string if none exists.

```
s = "ADOBECODEBANC", t = "ABC"  ->  "BANC"
```

## Approach — expand to satisfy, contract to minimize (optimal)

The hardest sliding-window template: grow the right edge until the window is **valid** (contains all of `t`), then shrink the left edge as far as possible while *staying* valid, recording the smallest valid window seen.

```python
from collections import Counter

def minWindow(s, t):
    if not t or not s:
        return ""
    need = Counter(t)
    missing = len(t)                       # total chars still needed (with multiplicity)
    l = 0
    best = (float("inf"), 0, 0)            # (length, start, end)

    for r, ch in enumerate(s):
        if need[ch] > 0:                   # this char helps satisfy t
            missing -= 1
        need[ch] -= 1                      # may go negative for surplus chars

        while missing == 0:                # window is valid -> try to shrink
            if r - l + 1 < best[0]:
                best = (r - l + 1, l, r)
            need[s[l]] += 1
            if need[s[l]] > 0:             # removing s[l] breaks validity
                missing += 1
            l += 1

    return "" if best[0] == float("inf") else s[best[1] : best[2] + 1]
```

**Time O(|s| + |t|), space O(|t|).**

## The two-phase rhythm

- **Expand (`for r`)**: always advance right, folding each char into `need`. `missing` counts required chars not yet covered.
- **Contract (`while missing == 0`)**: while valid, record the window and pull the left edge in; validity breaks precisely when you remove a char the window actually needed (`need[s[l]] > 0` *after* incrementing).

Letting `need` go **negative** for surplus characters is the trick that makes contraction correct — you only lose validity when a genuinely-needed char's count would drop below required.

## Key insight

**"Smallest window containing a target set" → expand-to-valid, then contract-to-minimal.** The `missing`/`need` bookkeeping (with negatives for surplus) generalizes to any "cover all requirements with the tightest window" problem — the canonical hard sliding window.

## Related
- concept: [[03-sliding-window|sliding-window]]
- prev: [[018-permutation-in-string|Permutation in String]] · next: [[020-sliding-window-maximum|Sliding Window Maximum]]
