# Jump Game II

**LeetCode 45** · Greedy · concept: [[10-greedy-algorithms|greedy]]

## Problem

Same jump rules as [[123-jump-game|Jump Game]], but return the **minimum number of jumps** to reach the last index (a solution is guaranteed).

## Approach — greedy BFS by "jump levels" (optimal)

Think in levels, like [[03-bfs|BFS]]: from the current jump's range `[l, r]`, one more jump reaches the farthest any index in that window allows. Expand level by level, counting jumps, until a level covers the end.

```python
def jump(nums):
    jumps = 0
    l = r = 0                      # current reachable window [l, r]
    while r < len(nums) - 1:
        farthest = max(i + nums[i] for i in range(l, r + 1))
        l = r + 1                  # next window starts past the current one
        r = farthest               # ...and reaches the new farthest
        jumps += 1
    return jumps
```

**Time O(n), space O(1).**

## Why this is BFS in disguise

Each "level" is the set of indices reachable in exactly `k` jumps; the next level is everything reachable from the current window. The minimum jump count is the level at which the end first appears — BFS's shortest-path property, applied greedily without an explicit queue. Taking the farthest reach from the whole current window (not one index) is what makes each jump count optimal.

## Key insight

**Fewest jumps → greedy level-expansion (implicit BFS): from the current reachable window, jump to the farthest it can reach.** It reframes "minimum jumps" as "how many BFS levels to cover the array," giving O(n) instead of an O(n²) DP.

## Related
- concept: [[10-greedy-algorithms|greedy]], [[03-bfs|bfs]]
- builds on: [[123-jump-game|Jump Game]]
- prev: [[123-jump-game|Jump Game]] · next: [[125-gas-station|Gas Station]]
