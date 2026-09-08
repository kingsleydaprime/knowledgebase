# Combination Sum II

**LeetCode 40** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Given `candidates` (which **may contain duplicates**) and a `target`, return all unique combinations summing to `target`. Each number is used **at most once**.

```
candidates = [10,1,2,7,6,1,5], target = 8  ->  [[1,1,6],[1,2,5],[1,7],[2,6]]
```

## Approach — sort + advance index + skip duplicate siblings

Combines two ideas already seen: use each element **once** by recursing on `i+1` (not `i`, as in [[072-combination-sum|Combination Sum]]), and avoid duplicate combinations by sorting and skipping equal siblings (as in [[074-subsets-ii|Subsets II]]).

```python
def combinationSum2(candidates, target):
    candidates.sort()
    res = []
    path = []
    def backtrack(start, remaining):
        if remaining == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue                          # skip duplicate at this level
            if candidates[i] > remaining:
                break                             # sorted -> all later are too big
            path.append(candidates[i])
            backtrack(i + 1, remaining - candidates[i])   # i+1 -> each used once
            path.pop()
    backtrack(0, target)
    return res
```

**Time O(2ⁿ) worst case, space O(n).**

## The two mechanics working together

- **`i + 1`** in the recursive call → each element consumed at most once (vs. Combination Sum's reuse via same `i`).
- **`i > start` skip** → no duplicate combinations from equal input values.
- **`break` on `candidates[i] > remaining`** → sorting lets you abandon the rest of the loop early.

## Key insight

**"Each element once + duplicate inputs" = advance the index (`i+1`) *and* skip equal siblings (`i > start`), after sorting.** It's the synthesis of the two prior backtracking refinements; recognizing which combination of guards a problem needs is the skill.

## Related
- concept: [[14-backtracking|backtracking]]
- combines: [[072-combination-sum|Combination Sum]] + [[074-subsets-ii|Subsets II]]
- prev: [[074-subsets-ii|Subsets II]] · next: [[076-word-search|Word Search]]
