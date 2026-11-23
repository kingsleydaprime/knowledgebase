---
id: dbfbb8af-dd1a-45b8-b0cd-acb106c165fd
---

# Pattern: Fast & Slow Pointers

Fast and slow pointers is a technique where two markers move through a list at different speeds, one step and two steps at a time. If the list loops back on itself, the fast one will catch up with the slow one. It is like two runners on a track: if the track is a circle, the faster runner eventually laps the slower one.

## Before you start
<!-- bite: a388a38b-79a8-4066-9f77-fb54ffb9915b -->

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
<!-- bite: 21346b4a-01c7-4937-8ece-93093c124829 -->

Imagine you're walking down a hallway and want to know if there's a loop (a section of hallway that leads back to a previous section). You could keep a mental note of every room you've visited, but that requires O(n) memory. Instead, you could walk at two different speeds: one person walks normally, another person runs twice as fast. If there's a loop, the faster person will eventually catch up to the slower person inside the loop. If there's no loop, the faster person will reach the end of the hallway first.

This is the fast & slow pointers pattern: walk two pointers through a structure at different speeds — one step at a time vs two steps at a time. If there's a cycle, the fast pointer eventually laps the slow one and they meet; if there isn't, the fast pointer simply reaches the end.

Computer scientists call this **Floyd's Tortoise and Hare algorithm**. It's used for cycle detection, random number generation, and solving problems that can be reduced to finding cycles in sequences.

---

## 2. Definitions and terminology
<!-- bite: 6f197572-fdbd-413b-b55f-3d9157c567e9 -->

| Term                     | Plain-English definition                                                     | Example / analogy                                                      |
| ------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Fast & slow pointers** | Walk two indices through a structure at different speeds (1 step vs 2 steps) | Two people walking down a hallway, one normal speed, one twice as fast |
| **Cycle detection**      | Determining whether a sequence of "next" steps repeats/loops                 | Finding if a linked list has a loop                                    |
| **Lapping**              | The fast pointer overtakes the slow pointer inside a cycle                   | The faster runner laps the slower runner on a circular track           |
| **O(1) space**           | Constant extra memory regardless of input size                               | Using two variables instead of a hash set                              |

---

## 3. How it works — step by step
<!-- bite: eb132fdb-f6e2-4443-adc4-29f7f57d014c -->

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

```text
1 -> 3 -> 5 -> 7 -> 9
          ^_________|          (9 points back to 5 — a cycle)

slow moves one node at a time, fast moves two nodes at a time:

slow: 1, 3, 5, 7
fast: 1, 5, 9, 7

After 3 steps, both are at node 7 -> cycle detected!
```

### Why not just use a hash set of visited nodes?

You can — `if node in visited: return True` — and it's simpler to reason about. But it costs O(n) extra space. Fast & slow pointers get the same O(n) time with O(1) space, which is the entire reason this pattern is worth knowing rather than just always reaching for a set.

---

## 4. Implementation — complete runnable example
<!-- bite: 64d04875-ffd8-4372-8845-84780613ef37 -->

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

```text
Test 1 - cycle exists: True
Test 2 - no cycle: False
Test 3 - cycle start: 1
fast_slow_pointers_lab: passed
```

---

## 5. Beyond linked lists
<!-- bite: ad4f7b15-2609-4a4b-99c8-5a29e3b6c67e -->

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
<!-- bite: 41fbe3a1-29df-459a-b183-ab244bb4caec -->

O(n) time, O(1) space — the space savings over the hash-set approach is the whole point of this pattern.

---

## 7. Tradeoffs and limitations
<!-- bite: d26cd317-f8c9-4125-b99f-0a58ea1536aa -->

- **Only detects cycles, doesn't tell you where.** The basic algorithm only tells you _if_ there's a cycle, not where it starts. An extension can find the start, but it's more complex.
- **Requires a well-defined "next" function.** The pattern works on any sequence where you can compute the next element deterministically.
- **Hash set is simpler to reason about.** For small inputs or when memory is not a concern, the hash-set approach may be preferable for its clarity.

---

## Check your understanding
<!-- bite: 4d4096e4-0d42-496d-a9bf-3dadf54d2d74 -->

Try each one before you open the answer.

1. <!-- q: mcq id="a014df3d" -->
   In Floyd's cycle detection (tortoise and hare), how far does each pointer move on every step?

   - [ ] Slow 1 node, fast 3 nodes
   - [x] Slow 1 node, fast 2 nodes
   - [ ] Both 1 node, but fast starts later
   - [ ] Slow 2 nodes, fast 4 nodes

   <details><summary>Answer</summary>

   Slow moves one node and fast moves two. Inside a cycle the gap between them then closes by exactly one node per step.

   </details>

2. <!-- q: mcq id="ae7f4e32" -->
   Fast and slow pointers and a hash set of visited nodes can both detect a cycle in O(n) time. What does the pointer method gain?

   - [ ] It is faster: O(log n) time
   - [x] It uses O(1) extra space instead of O(n)
   - [ ] It works on lists without a next pointer
   - [ ] It also sorts the list

   <details><summary>Answer</summary>

   Space. Two pointer variables are O(1); a set that remembers every visited node is O(n).

   </details>

3. <!-- q: mcq id="1aeef57c" -->
   The loop runs `while fast and fast.next`. If that loop ends without the pointers ever meeting, what does it mean?

   - [x] The list has no cycle: fast reached the end
   - [ ] The cycle is too long to detect
   - [ ] The list has exactly one node
   - [ ] The cycle starts at the head

   <details><summary>Answer</summary>

   No cycle. A list with a loop has no end, so fast could never run out of nodes.

   </details>

4. <!-- q: mcq id="f3f348de" -->
   Slow and fast have met inside a cycle. How do you find the node where the cycle starts?

   - [ ] Return the meeting node
   - [x] Put one pointer back at the head, then move both one step at a time until they meet
   - [ ] Keep moving fast two steps until it reaches the head
   - [ ] Count the cycle length and divide by two

   <details><summary>Answer</summary>

   Reset one pointer to the head and step both by one. Where they meet again is the start of the cycle.

   </details>

5. <!-- q: open id="07458088" -->
   Why are the fast and slow pointers sure to meet once both are inside a cycle, instead of fast jumping over slow forever?

   <details><summary>Answer</summary>

   Each step, fast gains exactly one node on slow, so the gap behind slow shrinks by one every step. A gap that drops by one each time must reach zero, so they land on the same node; fast can't skip over slow because it never closes more than one node at a time.

   </details>

## Check your understanding: worked problems
<!-- bite: 6fa38c60-eeba-40d9-a0b5-d27bdf88017b -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="4533f784" answers="4;5" -->
   Fill in the gaps. A linked list is 1 → 2 → 3 → 4 → 5 → 6, and node 6 points back to node 3. Slow and fast both start at node 1; each step slow moves 1 node and fast moves 2. They first meet after ___ steps, at node ___.

   <details><summary>Answer</summary>

   4 steps, at node 5. Slow goes 2, 3, 4, 5. Fast goes 3, 5, 3, 5. After step 4 both are on 5.

   </details>

2. <!-- q: gap id="76a765e8" answers="40;3" -->
   Fill in the gaps. A list is 10 → 20 → 30 → 40 → 50 → 60 → 70, and node 70 points back to node 40. Slow and fast meet at node 50. Now one pointer goes back to the head and both move one node at a time. They meet at node ___ after ___ steps.

   <details><summary>Answer</summary>

   Node 40, after 3 steps. From the head: 20, 30, 40. From 50: 60, 70, 40. Node 40 is where the cycle starts.

   </details>

3. <!-- q: exact id="76bf0268" answer="10" -->
   For the happy-number check, next(n) is the sum of the squares of n's digits. What is next(next(97))?

   <details><summary>Answer</summary>

   10. next(97) = 81 + 49 = 130, and next(130) = 1 + 9 + 0 = 10.

   </details>

4. <!-- q: exact id="cdf592f7" answer="5" -->
   Find the duplicate number: nums = [2, 5, 1, 4, 3, 5] has length 6 with values from 1 to 5, so one value repeats. Treating each value as a pointer to that index, Floyd's method finds the cycle entrance. What number does it return?

   <details><summary>Answer</summary>

   5. Index 1 and index 5 both hold 5, so two arrows point to index 5, and that shared target is where the cycle begins.

   </details>

## 9. Practice — independent task
<!-- bite: b0ecabf0-623a-4161-bf76-e728cdaa71f6 -->

**Task:** Implement a function `find_happy_number(n)` that returns `True` if `n` is a happy number, `False` otherwise. Use the fast & slow pointer pattern. Test it with the following cases:

- `n = 19` → expected `True` (happy number)
- `n = 2` → expected `False` (enters cycle 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4...)

**Done when:** your function returns the correct results for both test cases.

---

## Practice problems
<!-- bite: 53105def-1318-4046-81b0-f20cabd0271a -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

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
<!-- bite: cfe13bcd-9f11-4e54-947c-95ed6bf5a293 -->

You are done with this pattern when you can, closed-book:

- [ ] Explain why a fast pointer moving two steps must meet a slow one inside a cycle.
- [ ] Find the cycle's start after detection, and justify why resetting one pointer to the head works.
- [ ] Implement cycle detection independently, handling the empty and single-node cases.
- [ ] State why this beats a hash set of visited nodes.

**Recap:** Two pointers traversing at different speeds detect cycles in O(1) space. Inside a loop the fast pointer gains one position per step on the slow one, so it must eventually land on it — the gap closes by exactly one each iteration and cannot be skipped over. Finding the loop's entry then falls out of the distance arithmetic, and the whole thing uses two variables rather than a set of every visited node.

**Next:** [[05-linked-list-reversal|linked-list-reversal]] — the other core linked-list technique — rewiring pointers in place, which the fast/slow midpoint is often the setup for.

## 10. Related
<!-- bite: 6c1904d3-e640-4161-b340-7f71874e70a7 -->

- [[04-linked-lists|linked-lists]] — the original application of this pattern
- [[03-hash-maps|hash maps]] — alternative for cycle detection (O(n) space)
- [[11-dfs-pattern|dfs-pattern]] — another pattern for exploring graphs
- [[01-growth-and-asymptotic-notation|algorithms]] — where the O(1) space framing comes from
- [[04-fast-slow-pointers|fast-slow-pointers]] — this note

---

## 11. Further reading
<!-- bite: 070fd909-fb09-4882-97b5-e87886687919 -->

The pattern appears in many contexts beyond LeetCode:

- **Random number generation:** Floyd's algorithm for generating random numbers with uniform distribution
- **Cryptography:** Cycle detection in hash functions
- **Network protocols:** Detecting loops in routing tables
- **Database systems:** Finding cycles in dependency graphs

The core idea — using two pointers at different speeds to detect cycles efficiently — is a fundamental algorithmic technique that appears whenever you need to detect repetition in a sequence.

## About this lesson
<!-- bite: b6e4f09b-aa99-405b-8d6c-fbec188c3ab0 -->

**Level:** Intermediate. **Covers:** A university-level introduction to the fast & slow pointers pattern: what it is, why it exists, how it works, and how to implement it independently.
