# Merge Two Sorted Lists

**LeetCode 21** · Linked List · concept: [[04-linked-lists|linked-lists]]

## Problem

Merge two sorted linked lists into one sorted list; return its head.

```
1->2->4 , 1->3->4   ->   1->1->2->3->4->4
```

## Approach — two pointers + dummy head (optimal)

Walk both lists, always appending the smaller current node to the output. A **dummy head** node removes the "is the result empty yet?" special case — you always have a `tail` to append to.

```python
def mergeTwoLists(l1, l2):
    dummy = ListNode()
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 or l2        # attach whatever remains (one list is now empty)
    return dummy.next           # skip the dummy
```

**Time O(m + n), space O(1)** — it splices existing nodes, allocating nothing but the dummy.

## Why the dummy head matters

Without it, you'd branch on whether the result list is empty every iteration to initialize the head. The dummy gives you a stable node to build off of; `dummy.next` is the real head at the end. This idiom recurs in almost every list-construction problem.

## Key insight

**Merging sorted sequences → advance the pointer at the smaller head.** It's the merge step of [[04-sorting|merge sort]], on linked nodes instead of arrays — and the building block of [[044-merge-k-sorted-lists|Merge K Sorted Lists]]. The dummy-head trick is the reusable technique.

## Related
- concept: [[04-linked-lists|linked-lists]]; merge step of [[04-sorting|sorting]]
- prev: [[035-reverse-linked-list|Reverse Linked List]] · next: [[037-reorder-list|Reorder List]]
