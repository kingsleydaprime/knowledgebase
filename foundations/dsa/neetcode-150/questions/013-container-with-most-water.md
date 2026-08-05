# Container With Most Water

**LeetCode 11** · Two Pointers · concept: [[02-two-pointers|two-pointers]]

## Problem

Each element of `height` is a vertical line. Pick two lines that, with the x-axis, hold the **most water**. Area = width × the **shorter** of the two heights.

```
height = [1, 8, 6, 2, 5, 4, 8, 3, 7]  ->  49   (lines at index 1 and 8: min(8,7) × 7)
```

## Approach 1 — brute force (all pairs)

Try every pair, compute `min(h[i], h[j]) * (j - i)`. **O(n²)** — too slow at n = 10⁵.

## Approach 2 — two pointers from the ends (optimal)

Start as **wide as possible** (pointers at both ends) — that's the maximum possible width. Then the only way to *maybe* do better despite losing width is to raise the limiting (shorter) wall, so **move the shorter pointer inward**.

```python
def maxArea(height):
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        area = min(height[l], height[r]) * (r - l)
        best = max(best, area)
        if height[l] < height[r]:
            l += 1                # move the shorter wall — the only hope of improving
        else:
            r -= 1
    return best
```

**Time O(n), space O(1).** One pass inward.

## Why moving the shorter wall is safe (the greedy argument)

The area is capped by the **shorter** wall. If you moved the *taller* wall inward instead, width shrinks and the height cap can't rise (it's still limited by the unchanged shorter wall) — so the area can only stay the same or drop. Every configuration using the shorter wall at its current position is therefore already considered (this one is the widest such), so discarding it loses nothing. Moving the shorter wall is the only move that can raise the height cap. This is a **greedy** choice justified by an exchange argument — the reason a single O(n) pass provably finds the max without checking every pair.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Brute force | O(n²) | O(1) |
| **Two pointers** | **O(n)** | O(1) |

## Key insight

**When the objective is width × min(ends), start widest and shrink toward the taller side.** The insight isn't the two-pointer mechanic — it's *proving* which pointer to move by showing the alternative can't beat what you've already seen. That "the shorter wall bounds you, so advancing it is the only improving move" logic is the transferable idea.

## Related
- concept: [[02-two-pointers|two-pointers]], [[10-greedy-algorithms|greedy]]
- prev: [[012-3sum|3Sum]] · next: [[014-trapping-rain-water|Trapping Rain Water]]
