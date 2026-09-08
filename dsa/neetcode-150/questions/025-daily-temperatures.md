# Daily Temperatures

**LeetCode 739** · Stack · concept: [[06-monotonic-stack|monotonic-stack]]

## Problem

For each day, how many days until a **warmer** temperature? `0` if none comes.

```
[73,74,75,71,69,72,76,73]  ->  [1,1,4,2,1,1,0,0]
```

## Approach 1 — brute force

For each day, scan forward to the next warmer day. **O(n²)** — too slow.

## Approach 2 — monotonic stack (optimal)

Keep a stack of **indices of days still waiting for a warmer day**, with temperatures **decreasing** down the stack. Each new day resolves every waiting day it's warmer than.

```python
def dailyTemperatures(temps):
    res = [0] * len(temps)
    stack = []                               # indices, temps decreasing
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:   # today is warmer than waiting days
            j = stack.pop()
            res[j] = i - j                       # distance to the warmer day
        stack.append(i)
    return res
```

**Time O(n), space O(n).** Each index is pushed and popped once → amortized O(1) each.

## Why it's O(n) despite the nested `while`

An index enters the stack exactly once and leaves exactly once. The inner `while` does total work bounded by n pops across the whole run — the hallmark amortized argument of the [[06-monotonic-stack|monotonic stack]].

## Key insight

**"Next greater/smaller element" → monotonic stack of unresolved indices.** The stack holds items still waiting for their answer; a new element resolves all the pending items it dominates. This is the single most reusable stack pattern — Car Fleet, Largest Rectangle, and Trapping Rain Water are all variations.

## Related
- concept: [[06-monotonic-stack|monotonic-stack]]
- prev: [[024-generate-parentheses|Generate Parentheses]] · next: [[026-car-fleet|Car Fleet]]
