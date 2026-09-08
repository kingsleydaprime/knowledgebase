# Gas Station

**LeetCode 134** · Greedy · concept: [[10-greedy-algorithms|greedy]]

## Problem

`gas[i]` is fuel at station `i`; `cost[i]` is fuel to reach station `i+1` (circular). Return the starting station to complete the loop, or `-1`.

## Approach — one pass, two observations (optimal)

Two greedy facts collapse this to O(n):

1. **Feasibility**: if `sum(gas) < sum(cost)`, no start works (not enough total fuel) → `-1`.
2. **Where to start**: track a running tank; whenever it drops **below 0**, no station in the stretch just traversed could be the start, so the next station becomes the candidate and the tank resets.

```python
def canCompleteCircuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1                  # impossible overall
    tank = 0
    start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:               # can't reach i+1 from `start`
            start = i + 1          # ...so try starting fresh after i
            tank = 0
    return start
```

**Time O(n), space O(1).**

## Why the failed stretch can be skipped

If you run out of fuel going from `start` to `i+1`, then **no** station between `start` and `i` can be a valid start either — each of those would begin with even less accumulated fuel at the failure point. So you can jump the candidate straight to `i+1` without re-testing the skipped stations. Combined with the total-fuel check guaranteeing a solution exists, one pass suffices.

## Key insight

**Circular "can you make it around" → total-feasibility check + a greedy restart whenever the running tank goes negative.** The non-obvious part is *proving* the skipped stations can't be starts, which is what licenses the single pass.

## Related
- concept: [[10-greedy-algorithms|greedy]]
- prev: [[124-jump-game-ii|Jump Game II]] · next: [[126-hand-of-straights|Hand of Straights]]
