# Min Stack

**LeetCode 155** · Stack · concept: [[07-stacks-and-queues|stacks-and-queues]]

## Problem

Design a stack supporting `push`, `pop`, `top`, and `getMin` — all in **O(1)**.

## The challenge

`getMin` in O(1) is the catch: scanning for the min is O(n), and a single `min` variable breaks on `pop` (once you pop the current minimum, what's the new one?). You need the min **at every stack depth**.

## Approach — pair each element with the min-so-far (optimal)

Keep a parallel stack where each entry is the minimum of everything at or below it. On `push`, store `min(new value, current min)`. Then `pop` naturally restores the previous minimum for free.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.mins = []                       # mins[i] = min of stack[0..i]

    def push(self, val):
        self.stack.append(val)
        self.mins.append(min(val, self.mins[-1] if self.mins else val))

    def pop(self):
        self.stack.pop()
        self.mins.pop()

    def top(self):
        return self.stack[-1]

    def getMin(self):
        return self.mins[-1]                 # O(1)
```

**All operations O(1) time; O(n) space.**

## Why the parallel min-stack works

The minimum is a property of a *prefix* of the stack. By storing, at each level, the min of everything up to that level, popping automatically exposes the min of the shorter stack — no recomputation. (A space optimization stores mins only when they change, or encodes deltas, but the paired-stack version is the clearest.)

## Key insight

**To make an aggregate (min/max) O(1) under push/pop, store the running aggregate alongside each element.** The stack's LIFO discipline means level `i`'s aggregate is always valid when level `i` is on top — a reusable "augment the stack with precomputed state" technique.

## Related
- concept: [[07-stacks-and-queues|stacks-and-queues]]
- prev: [[021-valid-parentheses|Valid Parentheses]] · next: [[023-evaluate-reverse-polish-notation|Evaluate Reverse Polish Notation]]
