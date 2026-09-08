# Subsets

**LeetCode 78** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Return **all** subsets (the power set) of an array of distinct integers.

```
[1,2,3]  ->  [[], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]
```

## Approach — include/exclude each element (optimal)

The power set is a binary choice per element: **take it or skip it**. Backtracking explores both branches, appending a copy of the current path at each leaf.

```python
def subsets(nums):
    res = []
    path = []
    def backtrack(i):
        if i == len(nums):
            res.append(path[:])           # a completed subset (copy!)
            return
        path.append(nums[i])              # choice 1: include nums[i]
        backtrack(i + 1)
        path.pop()                        # undo
        backtrack(i + 1)                  # choice 2: exclude nums[i]
    backtrack(0)
    return res
```

**Time O(n · 2ⁿ), space O(n)** recursion (output is O(n·2ⁿ)).

## The backtracking skeleton

Every backtracking solution is: **choose → recurse → un-choose**. The `path.append(...)` / `path.pop()` bracket a recursive call so the same list is reused across branches instead of copied. And you must append `path[:]` (a **copy**) to the result — appending `path` itself stores a reference that later mutations corrupt.

## Key insight

**Generate all combinations/subsets → binary include-exclude backtracking.** Subsets is the template the whole category specializes: Combination Sum changes the branching, Subsets II adds duplicate-skipping, but the choose/recurse/undo spine is identical.

## Related
- concept: [[14-backtracking|backtracking]]
- next: [[072-combination-sum|Combination Sum]]
