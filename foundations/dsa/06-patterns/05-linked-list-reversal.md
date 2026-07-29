# Pattern: Linked List In-place Reversal

Reverse a [[04-linked-lists|linked list]] (or a section of one) by rewiring `.next` pointers as you walk through it, instead of building a new reversed list — O(1) extra space instead of O(n).

## When to use it

Any problem that asks you to reverse a whole list or a sub-range of one (`reverse nodes from position m to n`), or that secretly needs a reversal as a step (e.g. checking if a list is a palindrome by reversing the second half).

## How it works

Keep three pointers: the node before the current one (`prev`), the current node, and a temporary hold on `.next` before you overwrite it (you'd otherwise lose your only path forward the moment you rewire `current.next`).

```python
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next        # save before overwriting
        curr.next = prev       # reverse the pointer
        prev = curr            # advance prev
        curr = nxt             # advance curr
    return prev                 # prev is the new head
```

```
Before:  1 -> 2 -> 3 -> 4 -> 5 -> None

step 1:  1 <- 2    3 -> 4 -> 5 -> None      prev=1 curr=2
step 2:  1 <- 2 <- 3    4 -> 5 -> None      prev=2 curr=3
...
After:   None <- 1 <- 2 <- 3 <- 4 <- 5      prev=5 (new head)
```

## Reversing only a sublist

Same mechanism, but you first walk to the start of the range, keep a reference to the node just before it (to reattach afterward), reverse only within the range, then stitch the reversed section back into the rest of the list — three pieces (before, reversed-middle, after) glued back together.

## Complexity

O(n) time, O(1) space — the entire value of doing it in place rather than building a new list (which would still be O(n) time but O(n) extra space).

## Gotchas

- Saving `curr.next` **before** overwriting `curr.next = prev` is the one line that makes or breaks this — skip it and you disconnect the rest of the list before you've walked into it.
- Off-by-one on where the sublist reversal starts/ends is the most common bug in the `m, n` sublist variant — draw the before/after picture first, same advice as in [[04-linked-lists|linked-lists]].

## Practice problems
1. Reverse Linked List (LeetCode #206)
2. Reverse Linked List II (LeetCode #92) — reverse only a sublist
3. Swap Nodes in Pairs (LeetCode #24) — reversal in fixed-size chunks

## Related
- [[04-linked-lists|linked-lists]]
- [[04-fast-slow-pointers|fast-slow-pointers]]
