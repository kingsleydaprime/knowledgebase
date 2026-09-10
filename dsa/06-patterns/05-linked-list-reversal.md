# Pattern: Linked List In-place Reversal

**[Intermediate]** — A university-level introduction to the linked list reversal pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand linked lists. See [[04-linked-lists|linked lists]] if needed.
- You should know what recursion is. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define the linked list reversal pattern and explain why it achieves O(1) extra space instead of O(n).
2. Implement in-place reversal of a whole linked list.
3. Apply the pattern to reverse only a sublist of a linked list.
4. Explain the trade-offs between recursive and iterative implementations.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you have a physical stack of papers and you want to reverse their order. You could create a new stack by taking papers one by one from the top of the original stack and placing them on the new stack. That's O(n) time and O(n) space.

But you could also reverse the order in place by walking through the original stack and rewiring each paper's connection to the next paper. That's O(n) time and O(1) space.

This is the linked list reversal pattern: reverse a linked list (or a section of one) by rewiring `.next` pointers as you walk through it, instead of building a new list — O(1) extra space instead of O(n).

---

## 2. Definitions and terminology

| Term                  | Plain-English definition                                                                 | Example / analogy                                                        |
| --------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **In-place reversal** | Reverse the order of elements without allocating new storage for the elements themselves | Reversing a deck of cards by flipping each card's connection to the next |
| **Pointer rewiring**  | Changing the `.next` references to point to different nodes                              | Changing a linked list's pointers to reverse the order                   |
| **Sentinel**          | A temporary placeholder used to simplify edge cases                                      | Using `None` as the initial previous pointer                             |
| **Backtracking**      | Undoing a choice before trying the next option                                           | Reversing a sublist and restoring the original connections               |

---

## 3. How it works — step by step

### Reversing a whole linked list

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

**Concrete example:**

```
Before:  1 -> 2 -> 3 -> 4 -> 5 -> None

step 1:  1 <- 2    3 -> 4 -> 5 -> None      prev=1 curr=2
step 2:  1 <- 2 <- 3    4 -> 5 -> None      prev=2 curr=3
...
After:  None <- 1 <- 2 <- 3 <- 4 <- 5      prev=5 (new head)
```

### Reversing only a sublist

Same mechanism, but you first walk to the start of the range, keep a reference to the node just before it (to reattach afterward), reverse only within the range, then stitch the reversed section back into the rest of the list — three pieces (before, reversed-middle, after) glued back together.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `linked_list_reversal_lab.py` and run `python3 linked_list_reversal_lab.py`. It uses only Python's standard library and creates no external files.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_list(head):
    """Reverse a whole linked list in-place."""
    prev = None
    curr = head
    while curr:
        nxt = curr.next        # save before overwriting
        curr.next = prev       # reverse the pointer
        prev = curr            # advance prev
        curr = nxt             # advance curr
    return prev                 # prev is the new head


def reverse_sublist(head, m, n):
    """Reverse nodes from position m to n (1-indexed)."""
    if not head or m == n:
        return head

    dummy = ListNode(0, head)   # dummy node to simplify edge cases
    prev = dummy

    # Walk to the node before position m
    for _ in range(m - 1):
        prev = prev.next

    # Reverse the sublist
    curr = prev.next
    for _ in range(n - m):
        nxt = curr.next
        curr.next = nxt.next
        nxt.next = prev.next
        prev.next = nxt

    return dummy.next


def print_list(head):
    """Print the linked list values."""
    values = []
    curr = head
    while curr:
        values.append(str(curr.val))
        curr = curr.next
    print(" -> ".join(values) if values else "empty")


if __name__ == "__main__":
    # Test case 1: reverse whole list
    head1 = ListNode(1)
    head1.next = ListNode(2)
    head1.next.next = ListNode(3)
    head1.next.next.next = ListNode(4)
    head1.next.next.next.next = ListNode(5)

    reversed1 = reverse_list(head1)
    print("Test 1 - reverse whole list:")
    print_list(reversed1)
    assert [node.val for node in [reversed1, reversed1.next, reversed1.next.next, reversed1.next.next.next, reversed1.next.next.next.next]] == [5, 4, 3, 2, 1], "List not reversed correctly"

    # Test case 2: reverse sublist
    head2 = ListNode(1)
    head2.next = ListNode(2)
    head2.next.next = ListNode(3)
    head2.next.next.next = ListNode(4)
    head2.next.next.next.next = ListNode(5)

    reversed2 = reverse_sublist(head2, 2, 4)
    print("Test 2 - reverse sublist 2-4:")
    print_list(reversed2)
    assert [node.val for node in [reversed2, reversed2.next, reversed2.next.next, reversed2.next.next.next, reversed2.next.next.next.next]] == [1, 4, 3, 2, 5], "Sublist not reversed correctly"

    # Test case 3: edge case - single node
    head3 = ListNode(1)
    reversed3 = reverse_sublist(head3, 1, 1)
    print("Test 3 - single node:")
    print_list(reversed3)
    assert reversed3.val == 1, "Single node list should remain unchanged"

    print("linked_list_reversal_lab: passed")
```

Expected output:

```
Test 1 - reverse whole list:
5 -> 4 -> 3 -> 2 -> 1
Test 2 - reverse sublist 2-4:
1 -> 4 -> 3 -> 2 -> 5
Test 3 - single node:
1
linked_list_reversal_lab: passed
```

---

## 5. Recursive vs. Iterative

### Iterative (shown above)

- **Pros:** O(1) space, no recursion stack overhead
- **Cons:** More complex pointer management

### Recursive

```python
def reverse_list_recursive(head):
    if not head or not head.next:
        return head

    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

- **Pros:** Simpler to understand
- **Cons:** O(n) space due to recursion stack, risk of stack overflow for long lists

---

## 6. Complexity

O(n) time, O(1) space — the entire value of doing it in place rather than building a new list (which would still be O(n) time but O(n) extra space).

---

## 7. Tradeoffs and limitations

- **Saving `curr.next` before overwriting is crucial.** Skipping it disconnects the rest of the list before you've walked into it.
- **Off-by-one on where the sublist reversal starts/ends is the most common bug.** Draw the before/after picture first, same advice as in [[04-linked-lists|linked-lists]].
- **Recursive version risks stack overflow.** For very long lists, the iterative version is safer.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given a linked list `1 -> 2 -> 3 -> 4 -> 5`, trace through the iterative reversal algorithm step by step.
2. **Question:** Why is saving `curr.next` before overwriting `curr.next = prev` the one line that makes or breaks this algorithm?
3. **Question:** What happens if you try to reverse a sublist that starts at position 1? How do you handle the edge case?

### Answers — after your attempt

1. `prev=None curr=1`
   `nxt=2 curr.next=None prev=1 curr=2`
   `nxt=3 curr.next=1 prev=2 curr=3`
   `nxt=4 curr.next=2 prev=3 curr=4`
   `nxt=5 curr.next=3 prev=4 curr=5`
   `nxt=None curr.next=4 prev=5 curr=None`
   Return `prev=5` as new head.
2. Saving `curr.next` before overwriting `curr.next = prev` is crucial because `curr.next` is your only path forward in the list. If you overwrite it before saving, you lose access to the rest of the list before you've walked into it.
3. If the sublist starts at position 1, the node before position 1 is the dummy node. You need to handle this edge case by using a dummy node or checking if `m == 1` and adjusting your pointer management accordingly.

---

## 9. Practice — independent task

**Task:** Implement a function `reverse_k_nodes(head, k)` that reverses the first `k` nodes of a linked list, leaving the rest unchanged. Use the linked list reversal pattern. Test it with the following cases:

- `head = [1, 2, 3, 4, 5], k = 3` → expected `[3, 2, 1, 4, 5]`
- `head = [1, 2, 3, 4, 5], k = 1` → expected `[1, 2, 3, 4, 5]` (no change)

**Done when:** your function returns the correct linked list for both test cases.

---

## Practice problems

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[035-reverse-linked-list|Reverse Linked List]] (LeetCode #206) — the three-pointer flip everything else here builds on.
2. [[045-reverse-nodes-in-k-group|Reverse Nodes in k-Group]] (LeetCode #25) — the same flip applied blockwise; the tail reconnection is the hard part.
3. [[037-reorder-list|Reorder List]] (LeetCode #143) — reverse the second half, then interleave.
4. [[040-add-two-numbers|Add Two Numbers]] (LeetCode #2) — not reversal, but the same dummy-head-and-walk discipline.
5. [[039-copy-list-with-random-pointer|Copy List with Random Pointer]] (LeetCode #138) — pointer rewiring of a different kind; good practice at not losing a reference.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since partial and pairwise reversals are where the pointer bookkeeping actually bites:

6. Reverse Linked List II (#92) — reverse only positions $m..n$; the boundary handling *is* the problem.
7. Swap Nodes in Pairs (#24) — $k$-group with $k=2$ — do this before #25.
8. Palindrome Linked List (#234) — reverse half the list in place.
9. Rotate List (#61) — find the tail, close the ring, cut it.
10. Odd Even Linked List (#328) — splice into two lists, then rejoin.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Draw the three-pointer dance (`prev`, `curr`, `next`) for one iteration.
- [ ] Explain why you must save `next` *before* rewiring, and what happens if you don't.
- [ ] Reverse a sublist between two positions independently.
- [ ] State the space complexity and why the recursive version is worse on long lists.

**Recap:** In-place reversal walks the list rewiring each node's `next` to point backwards, holding three pointers so the forward link is saved before it is destroyed. It is O(n) time and O(1) space. The recursive formulation is elegant and costs O(n) stack, which is a real hazard on long lists.

**Next:** [[06-monotonic-stack|monotonic-stack]] — a different way of remembering what you have already seen — a stack that discards elements it can prove will never be the answer.

## 10. Related

- [[04-linked-lists|linked-lists]] — the underlying data structure
- [[04-fast-slow-pointers|fast-slow-pointers]] — used in some reversal algorithms
- [[01-algorithms|algorithms]] — where the O(1) space framing comes from
- [[05-linked-list-reversal|linked-list-reversal]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Reversing substrings in text editors:** In-place reversal of character sequences
- **Undo operations in software:** Reverting changes by reversing pointer operations
- **Memory management:** Reversing linked lists of free blocks in memory allocators
- **Data structure transformations:** Converting between different list representations

The core idea — rewiring pointers to reverse order without allocating new storage — is a fundamental algorithmic technique that appears whenever you need to reverse a sequence in place.
