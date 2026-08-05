# Longest Consecutive Sequence

**LeetCode 128** · Arrays & Hashing · concept: [[03-hash-maps|hash-maps]]

## Problem

Given an unsorted array `nums`, return the length of the longest run of **consecutive integers** (order in the array doesn't matter). Required time: **O(n)**.

```
[100, 4, 200, 1, 3, 2]  ->  4   (the run 1,2,3,4)
```

## Approach 1 — sort, then scan

Sorting makes consecutive numbers adjacent; walk and count runs.

```python
def longestConsecutive(nums):
    if not nums:
        return 0
    nums = sorted(set(nums))
    longest = streak = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1] + 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1
    return longest
```

**Time O(n log n), space O(n).** Correct, but the sort violates the O(n) requirement — it's the "good enough" baseline, not the intended answer.

## Approach 2 — hash set, count only from run starts (optimal)

Put everything in a set for O(1) membership. The insight that gets you to O(n): **only start counting a run at its smallest element** — a number `x` is the start of a run iff `x - 1` is **not** in the set. From each start, walk upward (`x+1, x+2, …`) as long as the next number exists.

```python
def longestConsecutive(nums):
    num_set = set(nums)
    longest = 0
    for x in num_set:
        if x - 1 not in num_set:        # x is the START of a run
            length = 1
            while x + length in num_set:  # extend upward
                length += 1
            longest = max(longest, length)
    return longest
```

## Why this is O(n), not O(n²)

The inner `while` looks alarming inside a loop, but the "only start from a run's beginning" guard means **each number is visited by a `while` loop at most once** — a number is only ever walked *over* as part of the single run that starts below it. Across the whole algorithm the inner loop does O(n) total work, so it's O(n) overall despite the nested appearance. Drop the `x - 1 not in num_set` guard and it degrades to O(n²), re-walking the same runs from every element.

## Complexity summary

| Approach | Time | Space |
|---|---|---|
| Sort + scan | O(n log n) | O(n) |
| **Hash set, run-starts** | **O(n)** | O(n) |

## Key insight

A set gives O(1) "does `x±1` exist?" lookups, which lets you **reconstruct sorted-adjacency without sorting**. The decisive move is the **run-start guard**: doing work only at each sequence's left edge is what collapses a seemingly-quadratic scan to linear. This "only act at a boundary" idea — recognizing the unique entry point of a structure — is a recurring way to avoid redundant work.

## Related
- concept: [[03-hash-maps|hash-maps]]
- builds on set membership from [[001-contains-duplicate|Contains Duplicate]]
- prev: [[008-valid-sudoku|Valid Sudoku]] — end of Arrays & Hashing
- next category: [[02-two-pointers|Two Pointers]]
