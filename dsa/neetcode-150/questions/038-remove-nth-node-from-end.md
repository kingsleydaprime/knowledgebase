# Remove Nth Node From End of List

**LeetCode 19** · Linked List · concept: [[04-fast-slow-pointers|fast-slow-pointers]]

## Problem

Remove the n-th node **from the end** and return the head, in one pass.

```
1->2->3->4->5, n=2   ->   1->2->3->5
```

## The idea — two pointers, n apart

To find the n-th from the end in one pass, advance a `fast` pointer **n steps ahead**, then move `fast` and `slow` together. When `fast` reaches the end, `slow` is exactly at the node *before* the one to remove. A **dummy head** handles the edge case of removing the first node.

```python
def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n):
        fast = fast.next          # open a gap of n
    while fast.next:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next    # skip the target
    return dummy.next
```

**Time O(n), space O(1).**

## Why the gap works

Keeping `fast` exactly `n` ahead of `slow` means when `fast` hits the last node, `slow` sits `n` from the end — one before the target. The **dummy** is essential: without it, deleting the head (`n == length`) has no "previous node" to relink.

## Key insight

**"K-th from the end" in one pass → a fixed-gap two-pointer.** Offsetting one pointer by the desired distance converts "from the end" (which normally needs the length first) into a single forward sweep. The dummy-head pattern neutralizes the head-deletion edge case.

## Related
- concept: [[04-fast-slow-pointers|fast-slow-pointers]], [[04-linked-lists|linked-lists]]
- prev: [[037-reorder-list|Reorder List]] · next: [[039-copy-list-with-random-pointer|Copy List with Random Pointer]]
