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

---

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
