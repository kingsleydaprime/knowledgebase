# Reorder List

**LeetCode 143** · Linked List · concepts: [[04-fast-slow-pointers|fast-slow-pointers]], [[05-linked-list-reversal|reversal]]

## Problem

Reorder `L0→L1→…→Ln` in place to `L0→Ln→L1→Ln-1→L2→…` — no value changes, just pointer surgery.

```
1->2->3->4     ->   1->4->2->3
1->2->3->4->5  ->   1->5->2->4->3
```

## Approach — three classic sub-routines composed

This problem is famous for being three easier problems stacked:

1. **Find the middle** with [[04-fast-slow-pointers|fast/slow pointers]] (slow moves 1, fast moves 2; slow lands at the middle).
2. **Reverse the second half** ([[035-reverse-linked-list|Reverse Linked List]]).
3. **Merge the two halves** alternately.

```python
def reorderList(head):
    # 1. middle: slow ends at the start of the second half
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 2. reverse the second half
    second = slow.next
    slow.next = None                 # split the list
    prev = None
    while second:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt
    # prev is now the head of the reversed second half

    # 3. merge first half and reversed second half alternately
    first, second = head, prev
    while second:
        f_next, s_next = first.next, second.next
        first.next = second
        second.next = f_next
        first, second = f_next, s_next
```

**Time O(n), space O(1).**

## Key insight

**Hard list problems decompose into {find middle, reverse, merge}.** Recognizing that a scary transformation is really a *composition* of the three fundamental list operations is the meta-skill — none of the three steps is hard alone.

## Related
- concepts: [[04-fast-slow-pointers|fast-slow-pointers]], [[05-linked-list-reversal|reversal]]
- prev: [[036-merge-two-sorted-lists|Merge Two Sorted Lists]] · next: [[038-remove-nth-node-from-end|Remove Nth Node From End]]
