# Reverse Linked List

**LeetCode 206** · Linked List · concept: [[05-linked-list-reversal|linked-list-reversal]]

## Problem

Reverse a singly linked list; return the new head.

```
1 -> 2 -> 3 -> 4 -> 5   becomes   5 -> 4 -> 3 -> 2 -> 1
```

## Approach 1 — iterative pointer flip (optimal)

Walk the list carrying three references: `prev`, `curr`, and a saved `next`. Point each node back at its predecessor, then advance.

```python
def reverseList(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next      # save the rest before we clobber it
        curr.next = prev     # flip this node's pointer backward
        prev = curr          # advance prev
        curr = nxt           # advance curr
    return prev              # prev is the new head
```

**Time O(n), space O(1).**

## Approach 2 — recursive

Reverse the tail, then make the next node point back at the current one. **O(n) time, O(n) stack space** — elegant but uses the call stack.

```python
def reverseList(head):
    if not head or not head.next:
        return head
    new_head = reverseList(head.next)
    head.next.next = head    # the node ahead now points back at me
    head.next = None
    return new_head
```

## The one bug everyone hits

Forgetting to **save `curr.next` before overwriting it** — once you set `curr.next = prev`, the original next is lost and the list is severed. The `nxt` temp is mandatory.

## Key insight

**Reversal = re-point each `next` backward while walking, holding prev/curr/next.** This three-pointer dance is the atom of nearly every hard linked-list problem (Reorder List, Reverse-in-k-Group) — internalize it cold.

## Related
- concept: [[05-linked-list-reversal|linked-list-reversal]], [[04-linked-lists|linked-lists]]
- next: [[036-merge-two-sorted-lists|Merge Two Sorted Lists]]
