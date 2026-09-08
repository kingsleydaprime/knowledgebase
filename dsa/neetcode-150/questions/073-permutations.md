# Permutations

**LeetCode 46** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Return all permutations of an array of distinct integers.

```
[1,2,3]  ->  [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

## Approach — backtracking with a used-set (optimal)

Unlike subsets/combinations (where **order doesn't matter** and you only move forward), permutations care about order, so at each position you may pick **any unused** element. Track which are used.

```python
def permute(nums):
    res = []
    path = []
    used = [False] * len(nums)
    def backtrack():
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue                  # already placed
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()                    # undo
            used[i] = False
    backtrack()
    return res
```

**Time O(n · n!), space O(n).**

## Combinations vs permutations — the structural difference

Combinations pass an **index** and only go forward (order irrelevant, no revisiting). Permutations loop over **all** positions each call, gated by a `used` flag (order matters, every element appears at every position across branches). Spotting which of these two shapes a problem needs is the core backtracking judgment.

## Key insight

**Order matters → loop over all unused elements at each step (`used` set); order doesn't → advance an index.** That single distinction separates the permutation family from the subset/combination family; the choose/recurse/undo spine is otherwise identical.

## Related
- concept: [[14-backtracking|backtracking]]
- contrast: [[071-subsets|Subsets]] (index-based)
- prev: [[072-combination-sum|Combination Sum]] · next: [[074-subsets-ii|Subsets II]]
