# Largest Rectangle in Histogram

**LeetCode 84** · Stack · concept: [[06-monotonic-stack|monotonic-stack]]

## Problem

Given bar `heights` of width 1, find the area of the largest rectangle that fits under the histogram.

```
[2,1,5,6,2,3]  ->  10   (bars of height 5 and 6, width 2)
```

## The idea — each bar's maximal rectangle

For every bar, the widest rectangle *of that bar's height* extends left and right until it hits a **shorter** bar. So the answer is `max(height[i] × width[i])`, where `width[i]` runs between the nearest shorter bars on each side. Finding "nearest shorter bar on each side" is the [[06-monotonic-stack|monotonic stack]] job — done in one pass.

## Approach — monotonic increasing stack (optimal)

Keep a stack of `(start_index, height)` with heights **increasing**. When a bar shorter than the top arrives, the taller bars can't extend past it, so pop them and finalize their rectangles — each popped bar could extend right up to the current index.

```python
def largestRectangleArea(heights):
    stack = []                 # (start_index, height), heights increasing
    best = 0
    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:      # current bar ends the taller ones
            idx, height = stack.pop()
            best = max(best, height * (i - idx))   # width from its start to here
            start = idx                        # current bar extends back to idx
        stack.append((start, h))
    # bars still on the stack extend to the end
    n = len(heights)
    for idx, height in stack:
        best = max(best, height * (n - idx))
    return best
```

**Time O(n), space O(n).**

## The subtle part — extending the start leftward

When a bar `h` pops taller bars, `h` can extend **left** to the start index of the last bar it popped (those taller bars are ≥ `h`, so `h` fits under them). Carrying `start` back through the pops is what lets each bar know how far left it reaches. The trailing loop handles bars that never met a shorter bar (they reach the right end).

## Key insight

**"Largest rectangle / max area bounded by shorter neighbors" → monotonic stack giving nearest-smaller on both sides.** It's the most advanced next-smaller-element application: each bar's rectangle is width (between nearest shorter bars) × height, all computed in a single amortized-O(n) sweep.

## Related
- concept: [[06-monotonic-stack|monotonic-stack]]
- relative: [[025-daily-temperatures|Daily Temperatures]] (same stack mechanic)
- prev: [[026-car-fleet|Car Fleet]] — end of Stack
- next category: Binary Search
