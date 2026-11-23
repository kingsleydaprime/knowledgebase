---
id: f98b2184-bcd1-42c2-a711-0ff7f85eb04d
---

# Pattern: Linked List In-place Reversal

Linked list reversal is flipping the order of a linked list by turning each link around, without making a new list. A linked list is a chain of items where each item points to the next. It is like a queue of people where each person turns to face the person who was behind them.

## Before you start
<!-- bite: 51a5fdbc-4d0d-4ac2-9852-5adfcbddb0bd -->

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
<!-- bite: 50f9eb12-d1bc-4c73-876f-33b9e454ca08 -->

Imagine you have a physical stack of papers and you want to reverse their order. You could create a new stack by taking papers one by one from the top of the original stack and placing them on the new stack. That's O(n) time and O(n) space.

But you could also reverse the order in place by walking through the original stack and rewiring each paper's connection to the next paper. That's O(n) time and O(1) space.

This is the linked list reversal pattern: reverse a linked list (or a section of one) by rewiring `.next` pointers as you walk through it, instead of building a new list — O(1) extra space instead of O(n).

---

## 2. Definitions and terminology
<!-- bite: ebfa99fd-62a1-4ec0-a7cc-d869a519e0e4 -->

| Term                  | Plain-English definition                                                                 | Example / analogy                                                        |
| --------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **In-place reversal** | Reverse the order of elements without allocating new storage for the elements themselves | Reversing a deck of cards by flipping each card's connection to the next |
| **Pointer rewiring**  | Changing the `.next` references to point to different nodes                              | Changing a linked list's pointers to reverse the order                   |
| **Sentinel**          | A temporary placeholder used to simplify edge cases                                      | Using `None` as the initial previous pointer                             |
| **Backtracking**      | Undoing a choice before trying the next option                                           | Reversing a sublist and restoring the original connections               |

---

## 3. How it works — step by step
<!-- bite: 2f793bf9-0fb2-4c11-af2f-9bb301553748 -->

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

```text
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
<!-- bite: 209c050a-de8b-42ac-86db-b4660c53b9cd -->

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

```text
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
<!-- bite: 2a9f1bf3-a062-44dc-86cf-24dacb76cbf6 -->

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
<!-- bite: b183fae6-cfb1-47c0-b6e6-277004a2c427 -->

O(n) time, O(1) space — the entire value of doing it in place rather than building a new list (which would still be O(n) time but O(n) extra space).

---

## 7. Tradeoffs and limitations
<!-- bite: 97a1fa50-c7ff-43d9-a42e-9bd1c9a6bc8b -->

- **Saving `curr.next` before overwriting is crucial.** Skipping it disconnects the rest of the list before you've walked into it.
- **Off-by-one on where the sublist reversal starts/ends is the most common bug.** Draw the before/after picture first, same advice as in [[04-linked-lists|linked-lists]].
- **Recursive version risks stack overflow.** For very long lists, the iterative version is safer.

---

## Check your understanding
<!-- bite: a0caa5b7-7b0b-429b-b17d-706bc1a4566f -->

Try each one before you open the answer.

1. <!-- q: mcq id="8a0ab44c" -->
   In the iterative reversal loop, which line has to run before `curr.next = prev`?

   - [x] nxt = curr.next
   - [ ] prev = curr
   - [ ] curr = nxt
   - [ ] return prev

   <details><summary>Answer</summary>

   Save curr.next first. Once curr.next is overwritten it is your only path to the rest of the list, and it's gone.

   </details>

2. <!-- q: mcq id="163ae3dc" -->
   When the iterative reversal loop finishes, curr is None. Which pointer is the new head of the list?

   - [ ] curr
   - [x] prev
   - [ ] the old head
   - [ ] nxt

   <details><summary>Answer</summary>

   prev. It points at the last node handled, which was the old tail and is now the first node.

   </details>

3. <!-- q: gap id="553db379" answers="O(1)|1|constant;O(n)|n" -->
   Fill in the gaps. Reversing a list of n nodes, the iterative version uses ___ extra space and the recursive version uses ___ extra space.

   <details><summary>Answer</summary>

   O(1) and O(n). The recursive version keeps one call on the stack for every node, which is also why it can overflow on long lists.

   </details>

4. <!-- q: mcq id="5746fe34" -->
   reverse_sublist puts a dummy node in front of the head before walking. Which case does that dummy make easy?

   - [ ] A list with an even number of nodes
   - [x] A sublist that starts at position 1, so it has no real node before it
   - [ ] A sublist that ends at the tail
   - [ ] An empty sublist

   <details><summary>Answer</summary>

   Starting at position 1. The reversed piece must be joined onto "the node before it", and the dummy gives the head such a node.

   </details>

5. <!-- q: open id="38e34eb5" -->
   Why does in-place reversal need only O(1) extra space, while building a reversed copy needs O(n)?

   <details><summary>Answer</summary>

   In place, you only turn each existing next pointer around, using three pointer variables (prev, curr, nxt) whatever the list length. A copy makes a new node for every element, so the extra memory grows with n.

   </details>

## Check your understanding: worked problems
<!-- bite: b2e775fb-c2e3-4309-8234-6ed4155f3a82 -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="c9a67a4b" answers="3;9" -->
   Fill in the gaps. Iterative reversal of 7 → 3 → 9 → 2 starts with prev = None and curr = 7. After two passes of the loop, prev is node ___ and curr is node ___.

   <details><summary>Answer</summary>

   prev = 3, curr = 9. Pass 1 points 7 at None and moves to prev = 7, curr = 3. Pass 2 points 3 at 7 and moves to prev = 3, curr = 9.

   </details>

2. <!-- q: gap id="b7fd689a" answers="10;50;40;30;20;60" -->
   Fill in the gaps. Reverse positions 2 to 5 (counting from 1) of 10 → 20 → 30 → 40 → 50 → 60. The list becomes ___ → ___ → ___ → ___ → ___ → ___.

   <details><summary>Answer</summary>

   10 → 50 → 40 → 30 → 20 → 60. Only nodes 2 to 5 (20, 30, 40, 50) are flipped; 10 and 60 stay where they are.

   </details>

3. <!-- q: gap id="931b7edb" answers="c;b;a;d;e" -->
   Fill in the gaps. Reverse positions 1 to 3 of a → b → c → d → e. The list becomes ___ → ___ → ___ → ___ → ___.

   <details><summary>Answer</summary>

   c → b → a → d → e. The head itself changes, which is why the dummy node before the head is needed.

   </details>

4. <!-- q: gap id="40959758" answers="8;4" -->
   Fill in the gaps. reverse_list runs its loop once per node. reverse_sublist(head, m, n) runs its inner loop n − m times. On an 8-node list, reverse_list runs ___ times, and reverse_sublist(head, 3, 7) runs ___ times.

   <details><summary>Answer</summary>

   8 and 4. Reversing 5 nodes (positions 3 to 7) needs 7 − 3 = 4 moves, since each move lifts one node to the front of the piece.

   </details>

## 9. Practice — independent task
<!-- bite: 077765e1-ea9b-4a59-bed5-0f5f66412932 -->

**Task:** Implement a function `reverse_k_nodes(head, k)` that reverses the first `k` nodes of a linked list, leaving the rest unchanged. Use the linked list reversal pattern. Test it with the following cases:

- `head = [1, 2, 3, 4, 5], k = 3` → expected `[3, 2, 1, 4, 5]`
- `head = [1, 2, 3, 4, 5], k = 1` → expected `[1, 2, 3, 4, 5]` (no change)

**Done when:** your function returns the correct linked list for both test cases.

---

## Practice problems
<!-- bite: 335949f3-334f-45d4-9723-954209aa1b51 -->

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
<!-- bite: 37032d9a-f12d-48d7-944e-84f300039eca -->

You are done with this pattern when you can, closed-book:

- [ ] Draw the three-pointer dance (`prev`, `curr`, `next`) for one iteration.
- [ ] Explain why you must save `next` *before* rewiring, and what happens if you don't.
- [ ] Reverse a sublist between two positions independently.
- [ ] State the space complexity and why the recursive version is worse on long lists.

**Recap:** In-place reversal walks the list rewiring each node's `next` to point backwards, holding three pointers so the forward link is saved before it is destroyed. It is O(n) time and O(1) space. The recursive formulation is elegant and costs O(n) stack, which is a real hazard on long lists.

**Next:** [[06-monotonic-stack|monotonic-stack]] — a different way of remembering what you have already seen — a stack that discards elements it can prove will never be the answer.

## 10. Related
<!-- bite: 16c3cca1-ed26-4424-86ad-357203bbefa9 -->

- [[04-linked-lists|linked-lists]] — the underlying data structure
- [[04-fast-slow-pointers|fast-slow-pointers]] — used in some reversal algorithms
- [[01-growth-and-asymptotic-notation|algorithms]] — where the O(1) space framing comes from
- [[05-linked-list-reversal|linked-list-reversal]] — this note

---

## 11. Further reading
<!-- bite: a858cfa5-fcc1-4cd1-b942-cfd374b20f2a -->

The pattern appears in many contexts beyond LeetCode:

- **Reversing substrings in text editors:** In-place reversal of character sequences
- **Undo operations in software:** Reverting changes by reversing pointer operations
- **Memory management:** Reversing linked lists of free blocks in memory allocators
- **Data structure transformations:** Converting between different list representations

The core idea — rewiring pointers to reverse order without allocating new storage — is a fundamental algorithmic technique that appears whenever you need to reverse a sequence in place.

## About this lesson
<!-- bite: 1475dc0c-9608-41a9-a580-1112184c364c -->

**Level:** Intermediate. **Covers:** A university-level introduction to the linked list reversal pattern: what it is, why it exists, how it works, and how to implement it independently.
