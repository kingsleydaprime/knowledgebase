---
id: 8226c5db-bc7b-4a1d-9cfa-c5aa7c4df9c1
---

# Module: Level-Order Traversal (Breadth-First)

Level-order traversal is visiting the items of a tree one level at a time: the top first, then everything one step down, then the next level, and so on. It is also called breadth-first traversal. Think of a school assembly where the head teacher greets the front row first, then the second row, then the third.

## Before you start
<!-- bite: f901e47c-a2bd-4c4c-aeb3-2675e46dc94d -->

- You know the depth-first orders — [[01-depth-first-traversals|depth-first traversals]].
- You know what a queue does — [[../../05-stacks-and-queues|stacks and queues]].

**After this lesson you will be able to:**

1. Perform a level-order traversal by hand, and implement it with a queue.
2. Produce output **grouped by level**, not just a flat sequence.
3. Say when level-order is the right choice and when depth-first is.
4. Explain why this traversal uses a queue where the others use a stack.

**Study route:** read the mechanism, then the grouped-by-level variant, then the comparison at the end.

---

## 5. Breadth-First Traversal (Level-Order Traversal)
<!-- bite: fad6d8ce-2df9-47fd-863c-ee891b7ecfc6 -->

Unlike DFS traversals, **Level-Order Traversal** visits nodes level by level from top to bottom, left to right.

Because recursion uses a LIFO call stack, Level-Order cannot be written recursively. It uses an explicit **Queue (FIFO)** data structure:

```python
from collections import deque

def level_order(root: TreeNode) -> list:
    """Level-order traversal using an explicit Queue."""
    if root is None:
        return []
    
    result = []
    queue = deque([root])  # Initialize FIFO Queue with root
    
    while queue:
        current = queue.popleft()  # Remove next node from queue
        result.append(current.val)
        
        # Enqueue left child if it exists
        if current.left:
            queue.append(current.left)
            
        # Enqueue right child if it exists
        if current.right:
            queue.append(current.right)
            
    return result

# Visited Order: [1, 2, 3, 4, 5]
```

---

## 6. Time & Space Complexity Summary
<!-- bite: aff37a2e-26db-4f7d-956d-27770ac5f78a -->

| Traversal Type | Time Complexity | Space Complexity (Auxiliary Stack/Queue) |
| :--- | :--- | :--- |
| **Preorder (DFS)** | $O(n)$ | $O(h)$ call stack space ($h = \text{height of tree}$). |
| **Inorder (DFS)** | $O(n)$ | $O(h)$ call stack space ($O(\log n)$ balanced, $O(n)$ degenerate). |
| **Postorder (DFS)** | $O(n)$ | $O(h)$ call stack space. |
| **Level-Order (BFS)** | $O(n)$ | $O(w)$ queue space ($w = \text{max width of tree}$, up to $N/2$ leaves). |

---

## 7. Common Pitfalls & Traps
<!-- bite: ddec6155-a4fe-4d2b-8155-2ebd8cc8e0df -->

1. **Stack Overflow on Deep Trees**: Recursive DFS uses the CPU call stack. For a degenerate tree of height $10,000$, recursive traversal causes a `RecursionError` / Stack Overflow. Use an explicit iterative stack for deep trees.
2. **Queue vs Stack Trap in BFS**: Level-order requires a **FIFO Queue** (`popleft()`). Accidental use of a LIFO Stack (`pop()`) turns BFS into a bizarre right-to-left DFS traversal!
3. **Inorder Fallacy**: Inorder traversal only produces sorted output on **Binary Search Trees (BSTs)**. On arbitrary binary trees, it does not guarantee sorted order.

## Check your understanding
<!-- bite: 16520cef-32c4-4995-9142-b8e682b1a9fd -->

Try each one before you open the answer.

1. <!-- q: mcq id="a9f7804e" -->
   Which structure does a level-order traversal use to hold the nodes waiting to be visited?

   - [x] A queue (first in, first out)
   - [ ] A stack (last in, first out)
   - [ ] A hash map
   - [ ] A heap

   <details><summary>Answer</summary>

   A queue. Children join the back, so everything at one depth comes out before anything at the next depth. A stack would always dive into the newest node, which is depth-first.

   </details>

2. <!-- q: gap id="a3fd08a5" answers="1;2;3;4;5;6;7" -->
   Fill in the gaps. A perfect binary tree has root 1. 1's children are 2 (left) and 3 (right). 2's children are 4 and 5. 3's children are 6 and 7. The level-order traversal is ___, ___, ___, ___, ___, ___, ___.

   <details><summary>Answer</summary>

   1, 2, 3, 4, 5, 6, 7. Level 0 is 1, level 1 is 2 then 3, level 2 is 4, 5, 6, 7, each read left to right.

   </details>

3. <!-- q: mcq id="3d706b8a" -->
   A tree has n nodes, height h and widest level w. How much extra space does level-order traversal need?

   - [ ] O(h)
   - [x] O(w)
   - [ ] O(1)
   - [ ] O(log n) always

   <details><summary>Answer</summary>

   O(w). The queue holds about one level at a time. For a perfect tree the bottom level has about n/2 nodes, so the queue can grow to O(n), while depth-first needs only O(h).

   </details>

4. <!-- q: mcq id="022b6fab" -->
   A level-order traversal accidentally uses `pop()` (take from the end) instead of `popleft()` on its list of waiting nodes. What happens?

   - [ ] It still gives level order
   - [x] It becomes a depth-first traversal, so nodes no longer come out level by level
   - [ ] It crashes on the first call
   - [ ] It visits every node twice

   <details><summary>Answer</summary>

   Taking from the end makes the list a stack, so the traversal dives down the most recently added branch: a depth-first order, usually right-to-left.

   </details>

5. <!-- q: open id="8f4f30a5" -->
   How do you change a level-order traversal so its output is grouped by level, like [[1], [2, 3], [4, 5]], instead of one flat list?

   <details><summary>Answer</summary>

   At the start of each round, read the queue's current length. That many nodes are exactly the current level, so pop just that many into one group, adding their children to the back as you go. Then start a new group for the next round.

   </details>

---

## Check your understanding: worked problems
<!-- bite: 6319654f-2bc9-4754-8476-ce687beebd2d -->

Work each one out on paper first, then type your answer.

1. <!-- q: exact id="b5c9caba" answer="1, 2, 3, 4, 5, 6, 7, 8, 9" accept="123456789|1 2 3 4 5 6 7 8 9" -->
   A binary tree has root 1. 1's children are 2 (left) and 3 (right). 2 has only a left child, 4. 3's children are 5 (left) and 6 (right). 5's children are 7 (left) and 8 (right). 6 has only a right child, 9. List the level-order traversal, separated by commas.

   <details><summary>Answer</summary>

   1, 2, 3, 4, 5, 6, 7, 8, 9. Level 0: 1. Level 1: 2, 3. Level 2: 4, 5, 6. Level 3: 7, 8, 9.

   </details>

2. <!-- q: exact id="db3eab06" answer="3" -->
   A binary tree has root 1. 1's children are 2 (left) and 3 (right). 2 has only a left child, 4. 3's children are 5 (left) and 6 (right). 5's children are 7 (left) and 8 (right). 6 has only a right child, 9. A level-order traversal pops one node from the front of the queue, then adds its children to the back. What is the largest number of nodes the queue ever holds after a pop and its pushes?

   <details><summary>Answer</summary>

   3. For example, after visiting 3 the queue holds 4, 5, 6, and after visiting 5 it holds 6, 7, 8. It never holds more than the widest level, which here is 3.

   </details>

3. <!-- q: exact id="22d5b358" answer="1, 3, 6, 9, 5, 8, 7, 2, 4" accept="136958724|1 3 6 9 5 8 7 2 4" -->
   A binary tree has root 1. 1's children are 2 (left) and 3 (right). 2 has only a left child, 4. 3's children are 5 (left) and 6 (right). 5's children are 7 (left) and 8 (right). 6 has only a right child, 9. Someone writes level order with a stack by mistake: start with [1]; repeatedly take the LAST item, visit it, then append its left child and then its right child. List the visit order, separated by commas.

   <details><summary>Answer</summary>

   1, 3, 6, 9, 5, 8, 7, 2, 4. The right child is appended last, so it is taken next; the traversal dives down the right side first. That is a right-to-left depth-first order, not level order.

   </details>

## Before moving on
<!-- bite: 683e2d65-57f3-4774-a13d-dd301bfb280c -->

You can implement level-order traversal, group its output by level, and say when to prefer it.

**Recap:** level-order visits every node at one depth before moving deeper, using a **queue** rather than a stack; it costs $O(n)$ time and $O(w)$ space where $w$ is the widest level — which for a perfect tree is about $n/2$, so it can use far more memory than a depth-first traversal on the same tree; it is the right choice when the answer depends on depth, such as finding the shallowest node satisfying something, or printing a tree level by level.

## Related
<!-- bite: f0ff2066-58e4-438f-829b-ccee22e39a3b -->

- [[index|the traversal folder]]
- [[01-depth-first-traversals|Depth-First Traversals]] — the other three orders
- [[02-breadth-first-search|Breadth-First Search]] — the same idea on a general graph

## About this lesson
<!-- bite: 48f97da9-e80e-46a6-ac73-04f8332191b0 -->

**Level:** Intermediate. **Covers:** visiting a tree one depth at a time, and the queue that makes it work.
