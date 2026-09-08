# Combination Sum

**LeetCode 39** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Given distinct `candidates` and a `target`, return all unique combinations summing to `target`. Each candidate may be reused **unlimited** times.

```
candidates = [2,3,6,7], target = 7  ->  [[2,2,3], [7]]
```

## Approach — backtracking, recurse on the same index for reuse

At each step choose to (a) use the current candidate again — recurse on the **same** index `i` — or (b) move past it to index `i+1`. Allowing "same index" is what permits reuse; only ever moving forward (never back) prevents permutation-duplicates like `[2,3,2]`.

```python
def combinationSum(candidates, target):
    res = []
    path = []
    def backtrack(i, remaining):
        if remaining == 0:
            res.append(path[:])
            return
        if remaining < 0 or i == len(candidates):
            return                        # overshot or out of candidates
        path.append(candidates[i])        # use candidates[i] (again)
        backtrack(i, remaining - candidates[i])   # same i -> reuse allowed
        path.pop()                        # undo
        backtrack(i + 1, remaining)       # skip candidates[i] entirely
    backtrack(0, target)
    return res
```

**Time O(2^target) worst case, space O(target/min)** recursion depth.

## Reuse vs. order via the index

Recursing on the **same** `i` reuses an element; recursing on `i+1` moves on and never returns to it. Because you only advance, each combination is generated in a single nondecreasing-index order — so `[2,2,3]` appears once, not also as `[2,3,2]`. The index parameter encodes both "reuse allowed" and "no permutation dupes."

## Key insight

**"Combinations to a target, elements reusable" → recurse on the same index to reuse, advance to move on.** The `remaining < 0` prune cuts dead branches early. Contrast [[075-combination-sum-ii|Combination Sum II]] (each element once + duplicate skipping).

## Related
- concept: [[14-backtracking|backtracking]]
- prev: [[071-subsets|Subsets]] · next: [[073-permutations|Permutations]]
