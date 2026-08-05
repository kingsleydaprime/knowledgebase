# Linked List Cycle

**LeetCode 141** · Linked List · concept: [[04-fast-slow-pointers|fast-slow-pointers]]

## Problem

Return `true` if a linked list contains a cycle.

## Approach 1 — hash set of visited nodes

Walk the list, storing each node; if you revisit one, there's a cycle. **O(n) time, O(n) space.**

## Approach 2 — Floyd's tortoise and hare (optimal)

Two pointers, `slow` (1 step) and `fast` (2 steps). If there's a cycle, `fast` laps `slow` and they **meet**; if `fast` reaches null, the list ends and there's no cycle.

```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

**Time O(n), space O(1).**

## Why they must meet inside a cycle

Once both pointers are in the loop, each step closes the gap between them by exactly one (fast gains 1 per tick). A gap that shrinks by 1 each step, in a finite cycle, reaches 0 — they can't jump past each other. So a cycle guarantees a meeting; no cycle means `fast` hits null first.

## Finding the cycle's start (follow-up)

After they meet, move one pointer back to the head and advance both **one step at a time**; they meet again at the cycle's entrance (a distance argument on loop length). This is the exact trick behind [[042-find-the-duplicate-number|Find the Duplicate Number]].

## Key insight

**Cycle detection in O(1) space → Floyd's fast/slow pointers.** Different speeds guarantee a collision inside any loop. This generalizes to any "sequence that eventually repeats" — including numeric sequences (Happy Number) and array-as-function problems.

## Related
- concept: [[04-fast-slow-pointers|fast-slow-pointers]]
- prev: [[040-add-two-numbers|Add Two Numbers]] · next: [[042-find-the-duplicate-number|Find the Duplicate Number]]
