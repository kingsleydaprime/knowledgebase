# Linked List Reversal — Question Bank

Micro-questions over [[05-linked-list-reversal|the linked list reversal pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

---

## A. Why it exists

**1. Give the stack-of-papers analogy for both approaches.**

<details><summary>Answer</summary>

**Building a new stack** by moving papers one at a time is $O(n)$ time and $O(n)$ space. **Rewiring each paper's connection in place** is $O(n)$ time and $O(1)$ space.

</details>

**2. State the pattern.**

<details><summary>Answer</summary>

**Reverse a linked list by rewiring `.next` pointers as you walk through it**, instead of building a new list.

</details>

**3. What is pointer rewiring?**

<details><summary>Answer</summary>

Changing the `.next` references to point to different nodes.

</details>

---

## B. The mechanism

**4. Which three pointers do you keep, and why each?**

<details><summary>Answer</summary>

**`prev`** — the node before the current one, which is where `curr.next` must point. **`curr`** — where you are. **`nxt`** — a temporary hold on `curr.next`, because **you would otherwise lose your only path forward the moment you rewire it**.

</details>

**5. Write the loop.**

<details><summary>Answer</summary>

```python
prev = None
curr = head
while curr:
    nxt = curr.next      # save before overwriting
    curr.next = prev     # reverse the pointer
    prev = curr
    curr = nxt
return prev              # prev is the new head
```

</details>

**6. Why is `prev` initialised to `None`?**

<details><summary>Answer</summary>

**The old head becomes the new tail**, and a tail's `next` must be `None`. It acts as the sentinel.

</details>

**7. Why return `prev` and not `curr`?**

<details><summary>Answer</summary>

When the loop ends, **`curr` is `None` and `prev` is the last node processed** — which is the new head.

</details>

**8. Trace `1→2→3→4→5`.**

<details><summary>Answer</summary>

After step 1: `1 ← 2`, rest untouched, `prev=1, curr=2`. After step 2: `1 ← 2 ← 3`, `prev=2, curr=3`. Finally `None ← 1 ← 2 ← 3 ← 4 ← 5` with `prev = 5`.

</details>

---

## C. Reversing a sublist

**9. Describe the three phases.**

<details><summary>Answer</summary>

1. **Walk to the start of the range**, keeping a reference to the node just before it.
2. **Reverse only within the range**, using the same three-pointer loop.
3. **Stitch the reversed section back** — three pieces (before, reversed middle, after) glued together.

</details>

**10. What is the most common bug here?**

<details><summary>Answer</summary>

**Off-by-one on where the sublist starts and ends.** Draw the before/after picture first.

</details>

**11. What if the sublist starts at position 1?**

<details><summary>Answer</summary>

There is no node before it, so the head itself changes. **A sentinel/dummy node before the head removes the special case entirely** — you reattach to `dummy.next` and return that.

</details>

---

## D. Recursive versus iterative

**12. Write the recursive version.**

<details><summary>Answer</summary>

```python
if not head or not head.next:
    return head
new_head = reverse_list_recursive(head.next)
head.next.next = head
head.next = None
return new_head
```

</details>

**13. What does `head.next.next = head` do?**

<details><summary>Answer</summary>

**Makes the next node point back at the current one** — the reversal itself, done on the way back up the recursion.

</details>

**14. Why `head.next = None` immediately after?**

<details><summary>Answer</summary>

Otherwise the two nodes **point at each other**, creating a two-node cycle.

</details>

**15. Give the trade-offs.**

<details><summary>Answer</summary>

**Iterative**: $O(1)$ space, no recursion overhead, but more complex pointer management. **Recursive**: simpler to understand, but $O(n)$ stack space and **risk of stack overflow on long lists**.

</details>

---

## E. Traps

**16. What is "the one line that makes or breaks this algorithm"?**

<details><summary>Answer</summary>

**`nxt = curr.next` before `curr.next = prev`.** Skipping it **disconnects the rest of the list before you have walked into it.**

</details>

**17. What are the costs?**

<details><summary>Answer</summary>

$O(n)$ time, **$O(1)$ space** — the entire value of doing it in place.

</details>

**18. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Carry three pointers and flip one link per step — save the way forward before you overwrite it, and the old head becomes the new tail.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[05-linked-list-reversal|Linked List Reversal]] — the pattern
- [[dsa/02-data-structures/04-linked-lists-qb|Linked Lists — Question Bank]] — where the pointer-order trap is named
- [[04-fast-slow-pointers-qb|Fast & Slow Pointers — Question Bank]]
