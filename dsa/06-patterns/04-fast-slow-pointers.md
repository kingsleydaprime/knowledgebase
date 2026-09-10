# Pattern: Fast & Slow Pointers

**[Intermediate]** — A university-level introduction to the fast & slow pointers pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand linked lists. See [[04-linked-lists|linked lists]] if needed.
- You should know what a hash map is. See [[03-hash-maps|hash maps]] for the alternative approach.

**What you will be able to do after this lesson:**

1. Define the fast & slow pointers pattern and explain why it detects cycles in O(1) space.
2. Implement cycle detection in a linked list using fast & slow pointers.
3. Apply the pattern to related problems like happy numbers and finding the duplicate number in an array.
4. Explain why the hash-map alternative exists but is less space-efficient.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're walking down a hallway and want to know if there's a loop (a section of hallway that leads back to a previous section). You could keep a mental note of every room you've visited, but that requires O(n) memory. Instead, you could walk at two different speeds: one person walks normally, another person runs twice as fast. If there's a loop, the faster person will eventually catch up to the slower person inside the loop. If there's no loop, the faster person will reach the end of the hallway first.

This is the fast & slow pointers pattern: walk two pointers through a structure at different speeds — one step at a time vs two steps at a time. If there's a cycle, the fast pointer eventually laps the slow one and they meet; if there isn't, the fast pointer simply reaches the end.

Computer scientists call this **Floyd's Tortoise and Hare algorithm**. It's used for cycle detection, random number generation, and solving problems that can be reduced to finding cycles in sequences.

---

## 2. Definitions and terminology

| Term                     | Plain-English definition                                                     | Example / analogy                                                      |
| ------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Fast & slow pointers** | Walk two indices through a structure at different speeds (1 step vs 2 steps) | Two people walking down a hallway, one normal speed, one twice as fast |
| **Cycle detection**      | Determining whether a sequence of "next" steps repeats/loops                 | Finding if a linked list has a loop                                    |
| **Lapping**              | The fast pointer overtakes the slow pointer inside a cycle                   | The faster runner laps the slower runner on a circular track           |
| **O(1) space**           | Constant extra memory regardless of input size                               | Using two variables instead of a hash set                              |

---

## 3. How it works — step by step

### Cycle detection in a linked list

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # one step
        fast = fast.next.next     # two steps
        if slow == fast:
            return True
    return False
```

**Why they meet:** once both pointers are inside the cycle, the _gap_ between them shrinks by exactly one node every step (fast closes distance faster than the cycle can lengthen the gap), so the gap must eventually hit zero, meaning they occupy the same node.

**Concrete example:**

```
1 -> 3 -> 5 -> 7 -> 9
          ^_________|          (9 points back to 5 — a cycle)

slow moves one node at a time, fast moves two nodes at a time:

slow: 1, 3, 5, 7, 9, 5, 7, 9, ...
fast: 1, 3, 5, 7, 9, 5, 7, 9, ...

After 3 steps, both are at node 5 -> cycle detected!
```

### Why not just use a hash set of visited nodes?

You can — `if node in visited: return True` — and it's simpler to reason about. But it costs O(n) extra space. Fast & slow pointers get the same O(n) time with O(1) space, which is the entire reason this pattern is worth knowing rather than just always reaching for a set.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `fast_slow_pointers_lab.py` and run `python3 fast_slow_pointers_lab.py`. It uses only Python's standard library and creates no external files.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def has_cycle(head):
    """Return True if the linked list contains a cycle."""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # one step
        fast = fast.next.next     # two steps
        if slow == fast:
            return True
    return False


def find_cycle_start(head):
    """Return the node where the cycle begins, or None if no cycle."""
    slow = fast = head
    # First, detect if there's a cycle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # no cycle

    # Find the start of the cycle
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow  # node where cycle begins


if __name__ == "__main__":
    # Test case 1: cycle exists
    node1 = ListNode(1)
    node2 = ListNode(2)
    node3 = ListNode(3)
    node1.next = node2
    node2.next = node3
    node3.next = node1  # cycle back to node1

    result1 = has_cycle(node1)
    print(f"Test 1 - cycle exists: {result1}")
    assert result1 == True, f"Expected True, got {result1}"

    # Test case 2: no cycle
    node4 = ListNode(4)
    node5 = ListNode(5)
    node4.next = node5

    result2 = has_cycle(node4)
    print(f"Test 2 - no cycle: {result2}")
    assert result2 == False, f"Expected False, got {result2}"

    # Test case 3: find cycle start
    result3 = find_cycle_start(node1)
    print(f"Test 3 - cycle start: {result3.val if result3 else None}")
    assert result3 is not None and result3.val == 1, f"Expected cycle start at node 1, got {result3.val if result3 else None}"

    print("fast_slow_pointers_lab: passed")
```

Expected output:

```
Test 1 - cycle exists: True
Test 2 - no cycle: False
Test 3 - cycle start: 1
fast_slow_pointers_lab: passed
```

---

## 5. Beyond linked lists

The same idea detects cycles in _any_ sequence generated by repeatedly applying a function to a value:

### Happy Number

A happy number eventually reaches 1 when you repeatedly replace it with the sum of the squares of its digits. Some numbers enter a cycle that never reaches 1.

```python
def is_happy(n):
    def get_next(num):
        total = 0
        while num:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total

    slow = fast = n
    while True:
        slow = get_next(slow)
        fast = get_next(get_next(fast))
        if slow == fast:
            break

    return slow == 1
```

### Find the Duplicate Number

Given an array `nums` of length `n+1` with values in `[1, n]`, there must be a duplicate. Treat array values as implicit `next` pointers:

```python
def find_duplicate(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    # Find the entrance to the cycle
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
```

---

## 6. Complexity

O(n) time, O(1) space — the space savings over the hash-set approach is the whole point of this pattern.

---

## 7. Tradeoffs and limitations

- **Only detects cycles, doesn't tell you where.** The basic algorithm only tells you _if_ there's a cycle, not where it starts. An extension can find the start, but it's more complex.
- **Requires a well-defined "next" function.** The pattern works on any sequence where you can compute the next element deterministically.
- **Hash set is simpler to reason about.** For small inputs or when memory is not a concern, the hash-set approach may be preferable for its clarity.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given a linked list with a cycle, trace through the fast & slow pointer algorithm step by step.
2. **Question:** Why does the algorithm guarantee that the fast pointer will eventually catch up to the slow pointer if there's a cycle?
3. **Question:** How would you modify the algorithm to find the start of the cycle?

### Answers — after your attempt

1. `slow: 1, 3, 5, 7, 9, 5, 7, 9, ...`
   `fast: 1, 3, 5, 7, 9, 5, 7, 9, ...`
   After 3 steps, both are at node 5 -> cycle detected!
2. Once both pointers are inside the cycle, the _gap_ between them shrinks by exactly one node every step (fast closes distance faster than the cycle can lengthen the gap), so the gap must eventually hit zero, meaning they occupy the same node.
3. After detecting a cycle (when `slow == fast`), reset one pointer to the head and move both pointers one step at a time until they meet again. The meeting point is the start of the cycle.

---

## 9. Practice — independent task

**Task:** Implement a function `find_happy_number(n)` that returns `True` if `n` is a happy number, `False` otherwise. Use the fast & slow pointer pattern. Test it with the following cases:

- `n = 19` → expected `True` (happy number)
- `n = 2` → expected `False` (enters cycle 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4...)

**Done when:** your function returns the correct results for both test cases.

---

## Practice problems

**In the [[foundations/dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[041-linked-list-cycle|Linked List Cycle]] (LeetCode #141) — Floyd's algorithm in its original setting.
2. [[042-find-the-duplicate-number|Find the Duplicate Number]] (LeetCode #287) — the same algorithm on an *array*, treating values as pointers — the surprise of the set.
3. [[037-reorder-list|Reorder List]] (LeetCode #143) — find the middle with fast/slow, then reverse and interleave.
4. [[038-remove-nth-node-from-end|Remove Nth Node From End]] (LeetCode #19) — two pointers held $n$ apart, one pass.
5. [[139-happy-number|Happy Number]] (LeetCode #202) — cycle detection with no list at all, just repeated digit-squaring.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since the 150 uses Floyd's algorithm but never asks you to find the cycle's *start*:

6. Linked List Cycle II (#142) — finding where the cycle *starts* — the half of Floyd's algorithm #141 does not need.
7. Middle of the Linked List (#876) — fast/slow with nothing else attached.
8. Palindrome Linked List (#234) — middle, reverse, compare: three sub-patterns in one.
9. Circular Array Loop (#457) — cycle detection with direction constraints.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain why a fast pointer moving two steps must meet a slow one inside a cycle.
- [ ] Find the cycle's start after detection, and justify why resetting one pointer to the head works.
- [ ] Implement cycle detection independently, handling the empty and single-node cases.
- [ ] State why this beats a hash set of visited nodes.

**Recap:** Two pointers traversing at different speeds detect cycles in O(1) space. Inside a loop the fast pointer gains one position per step on the slow one, so it must eventually land on it — the gap closes by exactly one each iteration and cannot be skipped over. Finding the loop's entry then falls out of the distance arithmetic, and the whole thing uses two variables rather than a set of every visited node.

**Next:** [[05-linked-list-reversal|linked-list-reversal]] — the other core linked-list technique — rewiring pointers in place, which the fast/slow midpoint is often the setup for.

## 10. Related

- [[04-linked-lists|linked-lists]] — the original application of this pattern
- [[03-hash-maps|hash maps]] — alternative for cycle detection (O(n) space)
- [[11-dfs-pattern|dfs-pattern]] — another pattern for exploring graphs
- [[01-algorithms|algorithms]] — where the O(1) space framing comes from
- [[04-fast-slow-pointers|fast-slow-pointers]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Random number generation:** Floyd's algorithm for generating random numbers with uniform distribution
- **Cryptography:** Cycle detection in hash functions
- **Network protocols:** Detecting loops in routing tables
- **Database systems:** Finding cycles in dependency graphs

The core idea — using two pointers at different speeds to detect cycles efficiently — is a fundamental algorithmic technique that appears whenever you need to detect repetition in a sequence.
