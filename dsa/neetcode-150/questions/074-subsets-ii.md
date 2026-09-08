# Subsets II

**LeetCode 90** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Return all **unique** subsets of an array that **may contain duplicates**.

```
[1,2,2]  ->  [[], [1], [1,2], [1,2,2], [2], [2,2]]
```

## The challenge

[[071-subsets|Subsets]]'s include/exclude blindly would emit `[1,2]` twice (once per duplicate `2`). The fix: **sort**, so duplicates are adjacent, then skip a duplicate when it would start a redundant branch.

## Approach — sort + skip duplicate siblings

```python
def subsetsWithDup(nums):
    nums.sort()                           # duplicates become adjacent
    res = []
    path = []
    def backtrack(start):
        res.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                  # skip duplicate at the SAME tree level
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return res
```

**Time O(n · 2ⁿ), space O(n).**

## Why `i > start`, not `i > 0`

The skip must fire only for duplicates **at the same decision level** (siblings in the recursion tree), not for a duplicate legitimately used deeper in the path. `i > start` means "this isn't the first choice at this level," so a repeated value here would re-create a branch a sibling already made. Using the second `2` as a *continuation* of a path containing the first `2` is fine (that's `[2,2]`); using it to *start* the same subset as the first `2` did is the duplicate to cut.

## Key insight

**Dedupe combinatorial output → sort, then skip a value equal to its previous sibling at the same level (`i > start`).** This exact idiom recurs in Combination Sum II and Permutations II — the one-line guard that keeps duplicate inputs from producing duplicate outputs.

## Related
- concept: [[14-backtracking|backtracking]]
- builds on: [[071-subsets|Subsets]]
- prev: [[073-permutations|Permutations]] · next: [[075-combination-sum-ii|Combination Sum II]]
