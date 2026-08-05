# Contains Duplicate

**LeetCode 217** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Given an integer array `nums`, return `true` if any value appears **at least twice**, and `false` if every element is distinct.

```
[1, 2, 3, 1]     -> true   (1 repeats)
[1, 2, 3, 4]     -> false
```

This is the "hello world" of hashing — the whole point is to feel the time-space tradeoff that recurs across the entire Arrays & Hashing set.

## Approach 1 — brute force (all pairs)

Compare every element against every later element.

```python
def containsDuplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
```

**Time O(n²), space O(1).** Correct but quadratic — ~10⁸ comparisons at n = 10⁴, which is already the edge of "too slow" (see the constraint heuristic in [[01-algorithms|algorithms]]).

## Approach 2 — sort, then scan neighbors

Duplicates become adjacent once sorted, so one linear pass finds them.

```python
def containsDuplicate(nums):
    nums.sort()
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1]:
            return True
    return False
```

**Time O(n log n), space O(1)** (ignoring sort's stack). Better, and O(1) space if you're allowed to mutate the input — the trade is that it destroys the original order.

## Approach 3 — hash set (optimal)

Walk once, remembering everything seen. The moment you meet a value already in the set, it's a duplicate.

```python
def containsDuplicate(nums):
    seen = set()
    for n in nums:
        if n in seen:          # O(1) average membership check
            return True
        seen.add(n)            # O(1) average insert
    return False
```

**Time O(n), space O(n).** This is the canonical **trade memory for speed** move: an extra O(n) set buys a single linear pass. `len(set(nums)) != len(nums)` is the same idea in one line.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Brute force | O(n²) | O(1) |
| Sort + scan | O(n log n) | O(1)* |
| **Hash set** | **O(n)** | **O(n)** |

\* if in-place sort is allowed.

## Key insight

"Have I seen this before?" → reach for a hash **set**. It converts a nested-loop search into a single pass. Recognizing that phrasing is the reflex the rest of this category builds on — the same set-membership move powers [[009-longest-consecutive-sequence|Longest Consecutive Sequence]] and the per-unit checks in [[008-valid-sudoku|Valid Sudoku]].

## Related
- concept: [[03-hash-maps|hash-maps]]
- next: [[002-valid-anagram|Valid Anagram]] — from set membership to *count* maps
