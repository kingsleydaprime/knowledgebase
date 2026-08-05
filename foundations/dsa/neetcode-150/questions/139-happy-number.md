# Happy Number

**LeetCode 202** · Math & Geometry · concepts: [[04-fast-slow-pointers|fast-slow-pointers]], [[14-math-and-geometry|math-and-geometry]]

## Problem

Repeatedly replace a number with the **sum of the squares of its digits**. It's "happy" if this reaches 1; otherwise it loops forever. Return whether `n` is happy.

```
19 -> 1²+9²=82 -> 68 -> 100 -> 1   ->  true
```

## The insight — it's cycle detection

The transformation `n → sum of digit squares` is a deterministic "next" function, so the sequence is effectively a linked list. It either reaches 1 or enters a **cycle** — exactly [[041-linked-list-cycle|Linked List Cycle]]. Detect the loop with a `seen` set, or with **Floyd's fast/slow** for O(1) space.

```python
def isHappy(n):
    def next_num(x):
        return sum(int(d) ** 2 for d in str(x))

    slow, fast = n, next_num(n)
    while fast != 1 and slow != fast:      # stop at 1 (happy) or a meeting (cycle)
        slow = next_num(slow)
        fast = next_num(next_num(fast))
    return fast == 1
```

**Time O(log n) per step, space O(1)** with Floyd's (O(log n) with a set).

## Why it must terminate

For any starting number, the digit-square-sum sequence is bounded (large numbers shrink toward ≤ 3-digit values), so by pigeonhole it must eventually repeat — either hitting 1 or cycling. That guarantee is what lets cycle detection decide happiness: reach 1 → happy; meet fast=slow first → unhappy.

## Key insight

**A deterministic "next value" sequence that might loop → cycle detection (set or Floyd's).** Recognizing a *numeric* sequence as a linked list — where `next` is an arithmetic function — is the same leap as [[042-find-the-duplicate-number|Find the Duplicate Number]], applied to math.

## Related
- concepts: [[04-fast-slow-pointers|fast-slow-pointers]], [[14-math-and-geometry|math-and-geometry]]
- relative: [[041-linked-list-cycle|Linked List Cycle]]
- prev: [[138-set-matrix-zeroes|Set Matrix Zeroes]] · next: [[140-plus-one|Plus One]]
