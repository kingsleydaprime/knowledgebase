# Add Two Numbers

**LeetCode 2** · Linked List · concept: [[04-linked-lists|linked-lists]]

## Problem

Two numbers are stored as linked lists with digits in **reverse** order (ones digit first). Add them and return the sum as a linked list.

```
(2->4->3) + (5->6->4)  =  342 + 465 = 807  ->  7->0->8
```

## Approach — digit-by-digit with carry (optimal)

The reverse order is a gift: the list heads are the ones digits, so you add left to right exactly like grade-school addition, propagating a **carry**. Loop while either list has digits or a carry remains.

```python
def addTwoNumbers(l1, l2):
    dummy = ListNode()
    tail = dummy
    carry = 0
    while l1 or l2 or carry:
        total = carry
        if l1: total += l1.val; l1 = l1.next
        if l2: total += l2.val; l2 = l2.next
        carry, digit = divmod(total, 10)     # carry = total//10, digit = total%10
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next
```

**Time O(max(m, n)), space O(max(m, n))** for the result.

## The three things the loop condition handles

`while l1 or l2 or carry` covers all cases at once: **unequal lengths** (one list runs out first), and a **final carry** (`5->5` + `5->5` = `0->1->1`, needing a new node). Forgetting the trailing `carry` is the classic bug.

## Key insight

**Reverse-order digits let you add from the head with a running carry** — the same full-adder idea as [[13-bit-manipulation|Sum of Two Integers]], base 10 instead of base 2. `divmod(total, 10)` splits each column into carry and digit in one step.

## Related
- concept: [[04-linked-lists|linked-lists]]
- prev: [[039-copy-list-with-random-pointer|Copy List with Random Pointer]] · next: [[041-linked-list-cycle|Linked List Cycle]]
