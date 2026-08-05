# Reverse Nodes in k-Group

**LeetCode 25** · Linked List · concept: [[05-linked-list-reversal|linked-list-reversal]]

## Problem

Reverse the list in groups of `k`. A trailing group of fewer than `k` nodes is left as-is.

```
1->2->3->4->5, k=2  ->  2->1->4->3->5
1->2->3->4->5, k=3  ->  3->2->1->4->5
```

## Approach — reverse each block, stitch the boundaries (optimal)

The hardest standard linked-list problem: repeatedly (1) check that `k` nodes remain, (2) reverse exactly that block, (3) reconnect it to the reversed part before and the untouched part after. A `group_prev` pointer tracks the node just before the current block.

```python
def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # find the k-th node from group_prev
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next          # fewer than k left -> done

        group_next = kth.next              # first node of the next group
        # reverse the block [group_prev.next .. kth]
        prev, curr = group_next, group_prev.next
        while curr != group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        # reconnect: group_prev -> kth(new head), old head -> group_next
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp                   # old head is the tail of this block = next group_prev
```

**Time O(n), space O(1).**

## The two hard parts

1. **Look before you leap** — walk `k` nodes *first* to confirm a full group exists; if not, stop (the partial tail stays).
2. **Boundary stitching** — after reversing a block, `group_prev` must point to the block's new head (`kth`), and the block's old head becomes the next `group_prev`. Getting these re-links right is the whole difficulty.

## Key insight

**Segment-wise reversal = (reverse a bounded block) + (careful boundary relinking), repeated.** It's [[035-reverse-linked-list|Reverse Linked List]] applied to fixed windows, where the pointer bookkeeping between groups — not the reversal — is what makes it hard.

## Related
- concept: [[05-linked-list-reversal|linked-list-reversal]]
- builds on: [[035-reverse-linked-list|Reverse Linked List]]
- prev: [[044-merge-k-sorted-lists|Merge K Sorted Lists]] — end of Linked List
- next category: Trees
