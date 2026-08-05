# Jump Game

**LeetCode 55** · Greedy · concept: [[10-greedy-algorithms|greedy]]

## Problem

Each `nums[i]` is the **max** jump length from index `i`. Starting at index 0, can you reach the last index?

```
[2,3,1,1,4]  ->  true
[3,2,1,0,4]  ->  false   (stuck at index 3)
```

## Approach — track the farthest reachable index (optimal)

Sweep left to right, maintaining the **farthest** index reachable so far. If you ever stand on an index beyond that reach, you're stuck. If reach ever covers the last index, success.

```python
def canJump(nums):
    farthest = 0
    for i in range(len(nums)):
        if i > farthest:
            return False           # can't even get to i
        farthest = max(farthest, i + nums[i])
        if farthest >= len(nums) - 1:
            return True
    return True
```

**Time O(n), space O(1).**

## Greedy beats DP here

A DP ("is index i reachable?") is O(n²). The greedy insight: you don't need to know *how* you reach an index, only whether the running maximum reach covers it. Extending `farthest` as you go, and failing the moment `i` outruns it, captures reachability in one pass. (An equivalent backward greedy shrinks a "goal" post toward 0.)

## Key insight

**Reachability with variable steps → track a single farthest-reachable frontier.** Collapsing "all the ways to get here" into one running maximum is the greedy move that turns O(n²) DP into O(n).

## Related
- concept: [[10-greedy-algorithms|greedy]]
- prev: [[122-maximum-subarray|Maximum Subarray]] · next: [[124-jump-game-ii|Jump Game II]]
