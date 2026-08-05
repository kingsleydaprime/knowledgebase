# Koko Eating Bananas

**LeetCode 875** · Binary Search · concept: [[09-modified-binary-search|modified-binary-search]]

## Problem

Koko eats bananas from `piles` at speed `k` per hour (one pile at a time; a partial pile still uses a full hour). Given `h` hours, return the **minimum** integer speed `k` that finishes all piles in time.

```
piles = [3,6,7,11], h = 8  ->  4
```

## The insight — binary search on the answer

`k` isn't found in the array — it's a value in the range `[1, max(piles)]`. The key property is **monotonicity**: if speed `k` works, every speed `> k` also works; if `k` is too slow, everything slower is too. That yes/no boundary is binary-searchable. Search for the smallest `k` whose total hours ≤ `h`.

```python
import math

def minEatingSpeed(piles, h):
    def hours_at(k):
        return sum(math.ceil(p / k) for p in piles)   # ceil: partial pile = full hour

    l, r = 1, max(piles)
    while l < r:
        k = l + (r - l) // 2
        if hours_at(k) <= h:
            r = k              # k works -> maybe a slower speed also works; keep k
        else:
            l = k + 1          # too slow -> need faster
    return l                   # smallest feasible speed
```

**Time O(n · log(max pile)), space O(1).** Each feasibility check is O(n); the search does O(log(max)) checks.

## "Binary search on the answer" — the pattern

When you can't binary-search the *input* but can (1) define a candidate answer range and (2) write an O(n) **feasibility test** that's monotonic in the candidate, binary-search the *answer space*. The array isn't sorted — the **answers** are (feasible above a threshold, infeasible below). This is one of the highest-leverage patterns in the set; it also solves Capacity to Ship Packages, Split Array Largest Sum, and Swim in Rising Water.

## Key insight

**"Minimize/maximize a value subject to a monotonic feasibility check" → binary search the answer.** The two ingredients are a bounded range and a monotone predicate; the search then finds the boundary between "works" and "doesn't."

## Related
- concept: [[09-modified-binary-search|modified-binary-search]]
- prev: [[029-search-a-2d-matrix|Search a 2D Matrix]] · next: [[031-find-minimum-in-rotated-sorted-array|Find Minimum in Rotated Sorted Array]]
